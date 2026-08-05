"""
core/d112_reconciliere.py — A DOUA CALE D112 (gard de continut, 05.08.2026, pas 3/6).

Acelasi TIPAR ca D300/D394, dar D112 e cel mai EXPUS la tautologie: totalurile
generatorului vin din salarizare.calcul_salariu (facilitate/deducere/CM/plafon/
part-time). Deci calea 2 recalculeaza CONTRIBUTIILE din brut, cu formula minima si
cotele din REGISTRUL DE LEGE (common.cota), FARA sa atinga calcul_salariu / salarizare /
d112.pull — nici direct, nici tranzitiv (probat pe AST, inclusiv lantul de import).

CE RECONCILIAZA — DOAR CAZUL SIMPLU (scris ca atare, NU "D112 acoperit"):
  CAS = brut x cota_cas si CASS = brut x cota_cass, PER ANGAJAT, doar pentru angajatii
  fara nicio structura care schimba formula:
    - brut contractual STRICT peste salariul minim (facilitatea OUG 89/2025 se declanseaza
      EXACT la brut == salariu minim -> peste minim, facilitate = 0, baza contributie = brut);
    - fara concediu medical in luna (CM schimba baza/procentele);
    - norma intreaga (part-time -> suprataxare);
    - ne-scutit (scutit_contrib_minim);
    - fara tichete (masa/vacanta/cultural/cresa - schimba baza CASS/impozit);
    - angajat LUNA INTREAGA (fara proratare de angajare/incetare la mijloc de luna).
  Un angajat care incalca ORICARE conditie -> NEACOPERIT (sarit, nu alarma falsa).

CE RAMANE IN AFARA (LIMITA DECLARATA, GARZI cat.4 - gardul NU acopera):
  - FACILITATE la minim PRORATATA (schimbare de salariu in luna sau luna partiala) - facilitatea la minim
    TOATA luna, full-time E ACOPERITA de la 05.08 (sub-caz 1a). SCUTIRI, PLAFOANE, PART-TIME suprataxare;
  - CONCEDII MEDICALE (CM): baze si procente proprii (OUG 158/2005);
  - IMPOZIT (necesita deducerea personala degresiva art.77 - calcul complex, exclus din acest gard);
  - CAM (contributia asiguratorie de munca, agregat de angajator);
  - TICHETE (baza CASS/impozit modificata).
  Impozitul si CAM raman pe seama gardului structural DUK + golden-ele existente; aici NU se
  reconciliaza pe a doua cale. Extindere = pas separat.

NON-TAUTOLOGIE (probata pe AST + lant tranzitiv - test_d112_reconciliere): modulul NU importa
si NU foloseste calcul_salariu / salarizare / d112 / salariu_istoric. Isi trage singur brutul
(SQL propriu, mirror pe salariu_la) si detecteaza singur cazul simplu (SQL propriu pe salariati/
concedii_medicale/beneficii_lunare). Cotele vin din common.cota (registrul de lege period-aware),
NU dintr-un intermediar al generatorului.

DIVERGENTA = HARD-BLOCK (ReconciliereD112) care numeste angajatul si AMBELE valori; NU repara
tacit (tipar DECIZII 05.08).

LIMITE suplimentare: input partajat gresit (ambele cai citesc acelasi brut gresit) = §8.
"""

import calendar as _cal
from datetime import date as _date
from decimal import Decimal, ROUND_HALF_UP


class ReconciliereD112(ValueError):
    """Cele doua cai nu se reconciliaza pe contributiile cazului simplu, SAU un angajat emis are
    date corupte (brut lipsa / sub minimul legal). Poarta angajatul si ambele valori."""


def _q(x):
    """Rotunjire fiscala ARITMETICA la intreg (ROUND_HALF_UP). Autonoma fata de calea 1 (nu common._q)."""
    return int(Decimal(x).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _cote(la_data):
    """Cotele CAS/CASS + salariul minim din REGISTRUL DE LEGE (common.cota, period-aware).
    common e modulul de baza - NU importa salarizare/d112 (verificat pe lantul tranzitiv in test)."""
    from core import common as _c
    cas, _ = _c.cota("cas", la_data)
    cass, _ = _c.cota("cass", la_data)
    sm, _ = _c.cota("salariu_minim", la_data)
    fac, _ = _c.cota("facilitate_salariu_minim", la_data)
    plaf, _ = _c.cota("plafon_facilitate_salariu_minim", la_data)
    return (Decimal(str(cas)), Decimal(str(cass)), Decimal(str(sm)),
            Decimal(str(fac)), Decimal(str(plaf)))


def _brut_la(cur, schema, sid, data):
    """Brut contractual valabil la `data` — SQL PROPRIU (mirror pe salariu_istoric.salariu_la,
    fara a importa modulul). Fallback la salariati.salariu_brut, ca generatorul."""
    cur.execute("SELECT salariu_brut FROM %s.salariu_istoric WHERE salariat_id=%%s AND valabil_din<=%%s "
                "ORDER BY valabil_din DESC LIMIT 1" % schema, (sid, data))
    r = cur.fetchone()
    if r and r["salariu_brut"] is not None:
        return Decimal(str(r["salariu_brut"]))
    cur.execute("SELECT salariu_brut FROM %s.salariati WHERE id=%%s" % schema, (sid,))
    r = cur.fetchone()
    return Decimal(str(r["salariu_brut"])) if (r and r["salariu_brut"] is not None) else None


def _stabil_la_minim(cur, schema, sid, luna_inc, luna_sf):
    """True daca salariul NU s-a schimbat IN cursul lunii (nicio intrare salariu_istoric cu valabil_din
    strict dupa prima zi si pana la ultima). Fara schimbare + la minim -> facilitate_prorata = 1.0."""
    cur.execute("SELECT COUNT(*) AS n FROM %s.salariu_istoric WHERE salariat_id=%%s "
                "AND valabil_din > %%s AND valabil_din <= %%s" % schema, (sid, luna_inc, luna_sf))
    return int((cur.fetchone() or {"n": 0})["n"] or 0) == 0


def reconciliaza(conn, schema, an, luna, salariati_generator):
    """Recalcul independent al CAS/CASS pe cazul simplu, confruntat cu valorile generatorului.
    NU ridica. Intoarce:
      divergente   - CAS/CASS ale cazului simplu care nu se leaga (bug de contributie);
      suspecte     - angajat EMIS de generator cu DATE CORUPTE (brut lipsa / sub minimul legal):
                     skip-SUSPECT, semnalat (nu tacut) - "null base = eroare pana la proba contrarie";
      reconciliati - ids confruntati (cazul simplu);
      sarite       - skip-LEGITIM din complexitate fiscala (facilitate/CM/part-time/scutire/tichete/
                     luna partiala / generatorul nu l-a emis) - tacut, e in afara scopului gardului.
    Distinctia sarit-legitim vs sarit-suspect (cerinta Costin 05.08): un angajat NU trebuie sa cada
    tacut in 'afara' fiindca datele lui sunt stricate - acolo gardul TREBUIE sa vorbeasca."""
    import psycopg2.extras as _E
    la_data = _date(an, luna, 1)
    luna_inc = _date(an, luna, 1)
    luna_sf = _date(an, luna, _cal.monthrange(an, luna)[1])
    cota_cas, cota_cass, sm, fac_val, plafon_fac = _cote(la_data)
    gen = {s.get("id"): s for s in (salariati_generator or [])}
    divergente, suspecte, reconciliati, sarite = [], [], [], []
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT id, salariu_brut, part_time, scutit_contrib_minim, tichet_masa_valoare, "
                    "data_angajare, data_incetare FROM %s.salariati "
                    "WHERE (data_incetare IS NULL OR data_incetare >= %%s) ORDER BY id" % schema, (luna_inc,))
        rows = cur.fetchall()
        cur.execute("SELECT DISTINCT salariat_id FROM %s.concedii_medicale WHERE an=%%s AND luna=%%s"
                    % schema, (an, luna))
        cm_ids = {r["salariat_id"] for r in cur.fetchall()}
        ben_ids = set()
        try:
            cur.execute("SELECT DISTINCT salariat_id FROM %s.beneficii_lunare WHERE an=%%s AND luna=%%s"
                        % schema, (an, luna))
            ben_ids = {r["salariat_id"] for r in cur.fetchall()}
        except Exception:
            ben_ids = set()   # tabela optionala; absenta ei nu e o eroare

        for r in rows:
            sid = r["id"]
            g = gen.get(sid)
            if g is None:
                sarite.append(sid); continue   # generatorul nu l-a emis (ex. incetat) - skip LEGITIM
            brut = _brut_la(cur, schema, sid, luna_sf)
            # --- SKIP-SUSPECT: date corupte pe un angajat EMIS (semnalat, nu tacut) ---
            if brut is None:
                suspecte.append({"salariat": sid, "motiv": "brut LIPSA (salariu_istoric si "
                                 "salariati.salariu_brut ambele goale) - generatorul emite contributii pe 0"})
                continue
            # --- SKIP-LEGITIM: complexitate fiscala (in afara scopului gardului, tacut) ---
            if r["part_time"] or r["scutit_contrib_minim"]:
                sarite.append(sid); continue
            if float(r["tichet_masa_valoare"] or 0) > 0:
                sarite.append(sid); continue
            if sid in cm_ids or sid in ben_ids:
                sarite.append(sid); continue
            da, di = r["data_angajare"], r["data_incetare"]
            if (da and da > luna_inc) or (di and di < luna_sf):
                sarite.append(sid); continue   # luna nu e intreaga -> proratare -> afara
            if brut == sm:
                # SUB-CAZ 1a (extindere acoperire 05.08): FACILITATE la salariul minim, TOATA luna, full-time.
                # Deja filtrat mai sus: full-month, fara CM/tichete/part-time/scutire. Cerem in plus salariu STABIL
                # la minim toata luna (fara schimbare in luna) -> zile_la_minim = zile_lucratoare ->
                # facilitate_prorata = 1.0 -> facilitate = facilitate_val (OUG 89/2025 art.III, verificat la sursa).
                # baza_contrib = sm - facilitate, aplicat la CAS SI CASS (ca in salarizare.py:79-82).
                if not _stabil_la_minim(cur, schema, sid, luna_inc, luna_sf):
                    sarite.append(sid); continue   # schimbare in luna -> facilitate proratata (sub-caz ulterior) NEACOPERIT
                baza = (sm - fac_val) if sm <= plafon_fac else sm   # vbt > plafon -> facilitate 0
                exp = {"cas": _q(baza * cota_cas), "cass": _q(baza * cota_cass)}
                reconciliati.append(sid)
                for camp in ("cas", "cass"):
                    got = _q(g.get(camp) or 0)  # rotunjire la intreg ca _d112int (valoarea EMISA la ANAF), nu trunchiere
                    if got != exp[camp]:
                        divergente.append({"salariat": sid, "camp": camp,
                                           "generator": got, "cale2": exp[camp], "diferenta": got - exp[camp]})
                continue
            # --- SKIP-SUSPECT: sub minimul legal pentru angajat full-time luna intreaga ---
            if brut < sm:
                suspecte.append({"salariat": sid, "motiv": "brut %s SUB salariul minim %s pentru angajat "
                                 "full-time luna intreaga (sub pragul legal) - date probabil corupte"
                                 % (_q(brut), _q(sm))})
                continue
            # --- CAZ SIMPLU: recalcul independent (baza contributie = brut, facilitate 0) ---
            exp = {"cas": _q(brut * cota_cas), "cass": _q(brut * cota_cass)}
            reconciliati.append(sid)
            for camp in ("cas", "cass"):
                got = _q(g.get(camp) or 0)  # rotunjire la intreg ca _d112int (valoarea EMISA la ANAF), nu trunchiere
                if got != exp[camp]:
                    divergente.append({"salariat": sid, "camp": camp,
                                       "generator": got, "cale2": exp[camp], "diferenta": got - exp[camp]})
    return {"divergente": divergente, "suspecte": suspecte,
            "reconciliati": reconciliati, "sarite": sarite}


def verifica_reconciliere(conn, schema, an, luna, salariati_generator):
    """POARTA (hard-block): ridica ReconciliereD112 daca (a) CAS/CASS ale cazului simplu diverg, SAU
    (b) un angajat emis are DATE CORUPTE (brut lipsa / sub minim) - skip-suspect, semnalat nu tacut.
    Numeste angajatul si AMBELE valori. NU repara tacit (tipar DECIZII 05.08)."""
    rap = reconciliaza(conn, schema, an, luna, salariati_generator)
    parti = []
    if rap["divergente"]:
        parti.append("DIVERGENTE (caz simplu): " + "; ".join(
            "salariat %s %s: generator=%d vs cale2=%d (dif %d)" %
            (d["salariat"], d["camp"], d["generator"], d["cale2"], d["diferenta"])
            for d in rap["divergente"]))
    if rap["suspecte"]:
        parti.append("SUSPECTE (date corupte, nu caz fiscal legitim): " + "; ".join(
            "salariat %s: %s" % (s["salariat"], s["motiv"]) for s in rap["suspecte"]))
    if parti:
        raise ReconciliereD112(
            "D112 A DOUA CALE: %s. Declaratia NU se genereaza - gardul nu alege singur cine are "
            "dreptate si nu tace pe date corupte; verifica agregarea si datele." % " | ".join(parti))
    return rap
