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
  - FACILITATI (constructii/IT/agricol, salariu minim), SCUTIRI, PLAFOANE, PART-TIME suprataxare;
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
    """Cele doua cai nu se reconciliaza pe contributiile cazului simplu. Poarta ambele valori."""


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
    return Decimal(str(cas)), Decimal(str(cass)), Decimal(str(sm))


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


def reconciliaza(conn, schema, an, luna, salariati_generator):
    """Recalcul independent al CAS/CASS pe cazul simplu, confruntat cu valorile generatorului.
    NU ridica. {"divergente":[...], "reconciliati":[ids], "sarite":[ids]}."""
    import psycopg2.extras as _E
    la_data = _date(an, luna, 1)
    luna_inc = _date(an, luna, 1)
    luna_sf = _date(an, luna, _cal.monthrange(an, luna)[1])
    cota_cas, cota_cass, sm = _cote(la_data)
    gen = {s.get("id"): s for s in (salariati_generator or [])}
    divergente, reconciliati, sarite = [], [], []
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
            # --- detectare CAZ SIMPLU (orice incalcare -> NEACOPERIT) ---
            if r["part_time"] or r["scutit_contrib_minim"]:
                sarite.append(sid); continue
            if float(r["tichet_masa_valoare"] or 0) > 0:
                sarite.append(sid); continue
            if sid in cm_ids or sid in ben_ids:
                sarite.append(sid); continue
            da, di = r["data_angajare"], r["data_incetare"]
            if (da and da > luna_inc) or (di and di < luna_sf):
                sarite.append(sid); continue   # luna nu e intreaga -> proratare -> afara
            brut = _brut_la(cur, schema, sid, luna_sf)
            if brut is None or brut <= sm:
                sarite.append(sid); continue   # brut == sm -> facilitate; sub minim -> afara
            g = gen.get(sid)
            if g is None:
                sarite.append(sid); continue   # generatorul nu l-a emis (ex. incetat) - nu confruntam
            # --- recalcul independent (baza contributie = brut, facilitate 0 la caz simplu) ---
            exp = {"cas": _q(brut * cota_cas), "cass": _q(brut * cota_cass)}
            reconciliati.append(sid)
            for camp in ("cas", "cass"):
                got = int(g.get(camp) or 0)
                if got != exp[camp]:
                    divergente.append({"salariat": sid, "camp": camp,
                                       "generator": got, "cale2": exp[camp], "diferenta": got - exp[camp]})
    return {"divergente": divergente, "reconciliati": reconciliati, "sarite": sarite}


def verifica_reconciliere(conn, schema, an, luna, salariati_generator):
    """POARTA (hard-block): ridica ReconciliereD112 daca CAS/CASS ale cazului simplu diverg.
    Numeste angajatul si AMBELE valori. NU repara tacit (tipar DECIZII 05.08)."""
    rap = reconciliaza(conn, schema, an, luna, salariati_generator)
    if rap["divergente"]:
        linii = "; ".join(
            "salariat %s %s: generator=%d vs cale2=%d (dif %d)" %
            (d["salariat"], d["camp"], d["generator"], d["cale2"], d["diferenta"])
            for d in rap["divergente"])
        raise ReconciliereD112(
            "D112 A DOUA CALE (caz simplu): CAS/CASS ale generatorului NU se reconciliaza cu "
            "recalculul independent din brut x cota. Divergente: %s. Declaratia NU se genereaza "
            "- gardul nu alege singur cine are dreptate; verifica agregarea si datele." % linii)
    return rap
