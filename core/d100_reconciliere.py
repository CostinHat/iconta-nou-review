# -*- coding: utf-8 -*-
"""
core/d100_reconciliere.py — A DOUA CALE D100 (gard de continut, pas 4/4 lant reconciliere).

DE CE EXISTA: DUK valideaza STRUCTURA D100, nu SEMANTICA. O declaratie cu suma_dat
GRESITA dar structural valida (obligatie prezenta, cod_bugetar corect, nr_evid 23c,
cota=1 la micro) trece azi la DUKIntegrator. Golden dintr-o declaratie ANAF completata
cu cifre nu se poate (anaf_surse/ nu are nicio declaratie completata - vezi memoria
"anaf-surse-fara-exemple-completate"). Deci gardul de continut = recalcul INDEPENDENT al
obligatiei din SURSA (registrul contabil), confruntat cu generatorul.

GAPUL DIN CATALOG PE CARE-L INCHIDE (CATALOG_INVALIDITATE.md "### D100" #31, aggregation-loss):
suma_dat iese gresita pentru ca agregarea veniturilor din pull-ul generatorului difera de
sursa reala (fereastra gresita, filtru status/cont gresit, rand scapat din SUM, obligatie
dublata/lipsa) -> azi XML emis + DUK-valid, NIMENI nu prinde. Calea 2 il face divergenta.

CE RECONCILIAZA (sursa -> declaratie):
  Baza impozabila D100 = veniturile CONTABILIZATE pe cont 70x, note status='validata', in
  fereastra trimestrului (perioada.interval()). Obligatia = baza x cota (micro 121 -> 1%,
  profit 103 -> 16%). Calea 2 isi trage SINGURA din inregistrari_linii suma pe 70x (SQL
  PROPRIU), o inmulteste cu cota din REGISTRU (core.common.cota, NU literal inline) si
  confrunta suma_dat rezultata cu res.obligatii[cod_oblig].suma_dat al generatorului.

CE PRINDE: venit scapat din agregarea pull a generatorului (fereastra/status/cont gresit,
           drop de rand din SUM), obligatie lipsa sau dublata, suma_dat != baza x cota -
           orice face suma_dat a generatorului sa difere de recalculul independent din 70x.

CE NU PRINDE (LIMITE DECLARATE, GARZI cat.4 "Iesire catre autoritati"):
  1. COTA (rata impozit) e INTRARE PARTAJATA: ambele cai o iau din acelasi registru COTE
     (sau din acelasi `manual={'cota':...}`). O cota gresita in registru/manual NU produce
     divergenta (nu se compara cu ea insasi) - raspunderea sursei, nu a acestui gard.
  2. MIS-BOOKING la sursa (blind spot PARTAJAT): venit inregistrat pe cont != 70x, sau nota
     status != 'validata', sau necontabilizat -> ambele cai il rateaza IDENTIC. Gardul prinde
     o AGREGARE gresita a generatorului fata de aceleasi randuri sursa, NU o postare gresita a
     contabilului (input partajat gresit = raspunderea contabilului, CLAUDE.md §8).
  3. REGIMURI in afara micro(121)/profit(103): generatorul nu emite obligatie pentru ele ->
     NEACOPERIT explicit (return acoperit=False, nu alarma falsa).
  4. Obligatii ALTE decat impozitul pe venit/profit din 70x (accize, alte impozite adaugate
     manual) - in afara scopului; calea 2 recalculeaza doar impozitul pe baza 70x.
  5. Ajustari pe baza impozabila anuala (chelt. nedeductibile la profit, scutiri la micro)
     apartin D101 (anual), NU D100 (plata pe venit brut trimestrial) - in afara scopului.

NON-TAUTOLOGIE (probata prin cod - vezi test_d100_reconciliere.test_non_tautologie_*):
acest modul NU importa `core.d100` si NU foloseste `calcul_d100`, `pull` sau `_i` din
generator. SQL propriu pe inregistrari_linii + cota din core.common + Decimal. Cele doua
cai NU impart codul de agregare, deci un bug in pull-ul generatorului (venit scapat,
fereastra gresita, filtru gresit) apare ca divergenta, nu ca acord tautologic.

PRECONDITIE: conn e pozitionat pe schema tenantului (acelasi contract ca `d100.pull`, care
nu seteaza search_path - conn vine din db.get_conn(tenant)).
"""

from decimal import Decimal, ROUND_HALF_UP

from core.common import cota as _cota, cheie_manual as _cheie_manual

# Nomenclator regim -> (cod_oblig XML, nume cota in registrul COTE). RE-DECLARAT aici (NU
# importat din d100) ca sa nu existe cod comun cu calea 1: micro=poz.5 cod_oblig 121 (impozit
# pe veniturile microintreprinderilor), profit=poz.2 cod_oblig 103 (impozit pe profit PJ).
_REGIM_OBLIG = {
    "micro":  ("121", "impozit_micro"),
    "profit": ("103", "impozit_profit"),
}


class ReconciliereD100(ValueError):
    """Obligatia generatorului nu se reconciliaza cu recalculul din sursa (70x). Poarta AMBELE valori."""


def _q(x):
    """Rotunjire fiscala ARITMETICA la intreg (ROUND_HALF_UP), ca in CLAUDE.md 'Rotunjire fiscala'.
    NU se importa `_i` din d100 - calea 2 e autonoma inclusiv pe rotunjire."""
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _venituri_independent(conn, perioada):
    """SUM(l.suma) pe cont_credit 70x, note VALIDATE, in fereastra perioada.interval().
    SQL PROPRIU - aceeasi sursa ca d100.pull, dar agregare INDEPENDENTA (nu se cheama pull)."""
    inc, sf = perioada.interval()
    q = ("SELECT COALESCE(SUM(l.suma),0) FROM inregistrari_linii l "
         "JOIN inregistrari i ON i.id = l.inregistrare_id "
         "WHERE i.status='validata' AND l.cont_credit LIKE '70%%' "
         "AND i.data >= %s AND i.data < %s")
    with conn.cursor() as cur:
        cur.execute(q, (inc.isoformat(), sf.isoformat()))
        return Decimal(str(cur.fetchone()[0] or 0))


def _cota_procent(regim, nume_cota, an, luna, manual):
    """Cota ca PROCENT (1/16), la fel ca in generator: `manual['cota']` daca dat (contabilul o
    poate suprascrie), altfel din REGISTRU (cota()[0]*100). NU literal inline (interdictie
    verificator default_fiscal_tacit). manual e INTRARE PARTAJATA - vezi LIMITA 1."""
    m = _cheie_manual(manual, "cota")
    if m.get("cota") is not None:
        return Decimal(str(m["cota"]))
    from datetime import date as _date
    return _cota(nume_cota, _date(an, luna, 1))[0] * Decimal(100)


def reconciliaza(conn, perioada, res, manual=None):
    """Recalculeaza independent obligatia si o confrunta cu res. NU ridica - intoarce raportul.
    {"acoperit": bool, "motiv": str|None, "divergente": [...]}"""
    if conn is None:
        return {"acoperit": False, "motiv": "fără conexiune DB (recompute independent indisponibil)", "divergente": []}
    regim = (res.prof.get("regim_fiscal") or "").lower()
    if regim not in _REGIM_OBLIG:
        return {"acoperit": False, "motiv":
                "regim '%s' în afara micro(121)/profit(103) - generatorul nu emite obligație D100 "
                "pentru el (limita 3)." % regim, "divergente": []}

    cod_oblig, nume_cota = _REGIM_OBLIG[regim]
    venituri = _venituri_independent(conn, perioada)
    procent = _cota_procent(regim, nume_cota, res.an, res.luna, manual)
    suma_cale2 = _q(venituri * procent / Decimal(100))

    # suma_dat a generatorului pentru ACEST cod_oblig (0 daca obligatia lipseste din res -
    # atunci un venit nenul la sursa = obligatie SCAPATA = divergenta, nu tacere).
    gen = 0
    for o in res.obligatii or []:
        if str(o.cod_oblig) == cod_oblig:
            gen += int(o.suma_dat)

    divergente = []
    if gen != suma_cale2:
        divergente.append({
            "cod_oblig": cod_oblig,
            "eticheta": "impozit %s (cod %s), baza 70x=%d x cota=%s%%" % (
                regim, cod_oblig, _q(venituri), procent),
            "generator": gen, "cale2": suma_cale2, "diferenta": gen - suma_cale2})
    return {"acoperit": True, "motiv": None, "divergente": divergente}


def verifica_reconciliere(conn, perioada, res, manual=None):
    """POARTA (hard-block): ridica ReconciliereD100 daca obligatia generatorului nu se leaga de
    recalculul independent din sursa (70x). Numeste AMBELE valori. NU repara tacit nici una din
    cai (tipar DECIZII 05.08). Intoarce raportul cand e curat/neacoperit."""
    rap = reconciliaza(conn, perioada, res, manual)
    if rap["divergente"]:
        linii = "; ".join(
            "cod %s (%s): generator=%d vs cale2=%d (dif %d)" %
            (d["cod_oblig"], d["eticheta"], d["generator"], d["cale2"], d["diferenta"])
            for d in rap["divergente"])
        raise ReconciliereD100(
            "D100 A DOUA CALE: obligatia generatorului NU se reconciliaza cu recalculul independent "
            "al bazei din sursa (venituri cont 70x, note validate). Divergente: %s. Declaratia NU se "
            "genereaza - gardul nu alege singur cine are dreptate; verifica agregarea si notele." % linii)
    return rap
