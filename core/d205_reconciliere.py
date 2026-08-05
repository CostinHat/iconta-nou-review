"""
core/d205_reconciliere.py — A DOUA CALE D205 (gard de continut, 05.08.2026, pas 6/6).

D205 = impozit pe dividende retinut la sursa, per beneficiar. Generatorul deriva fiecare
beneficiar din: total dividende distribuite (Σ cont 457, note validate) x cota asociatului x cota
impozitului pe dividende (period-aware, common.cota("impozit_dividend")).

DE CE NU CROSS-CHECK D205<->D100 (cerinta Costin - "verifica pe AST ca nu e capcana paritatii"):
D100 declara ACELASI impozit pe dividende, derivat din ACEEASI distributie (cont 457). O
confruntare D205<->D100 ar citi aceeasi sursa de doua ori = same-source trap, exact ca paritatea
D300/D394 (tautologica prin propriul docstring). Deci calea 2 = RECALCUL PROPRIU al bazei si
impozitului per beneficiar din 457 + cota asociat + cota lege, confruntat cu res.beneficiari -
non-tautologic pe AGREGARE/FORMULA (SQL propriu + formula proprie), nu pe sursa.

CE PRINDE: beneficiar scapat din declaratie, baza/impozit gresit (cota asociat aplicata gresit,
cota impozitului gresita, rotunjire), dublare.
CE NU (LIMITA, GARZI cat.4):
  - Beneficiari MANUALI (manual["beneficiari"], introdusi de contabil) -> NEACOPERIT (§8).
  - Input partajat gresit (aceeasi postare 457 gresita citita de ambele cai) - §8.

NON-TAUTOLOGIE (AST): NU importa/foloseste d205.calcul_d205 / d205.pull. Cotele: common.cota
(registrul de lege). Divergenta = HARD-BLOCK care numeste beneficiarul si AMBELE valori.
"""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP


class ReconciliereD205(ValueError):
    """Baza/impozitul pe dividende ale generatorului nu se leaga de recalculul independent."""


def _q(x):
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _dividende_independent(conn, an):
    """Total dividende (Σ cont debit 457, note VALIDATE, anul) + asociatii cu cota>0 - SQL PROPRIU."""
    inc, sf = date(an, 1, 1).isoformat(), date(an + 1, 1, 1).isoformat()
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(l.suma),0) FROM inregistrari_linii l "
                    "JOIN inregistrari i ON i.id = l.inregistrare_id "
                    "WHERE i.status='validata' AND l.cont_debit LIKE '457%%' "
                    "AND i.data >= %s AND i.data < %s", (inc, sf))
        total_div = _q(cur.fetchone()[0] or 0)
        cur.execute("SELECT nume, cnp, cota FROM asociati WHERE cota > 0 ORDER BY nume")
        asoc = cur.fetchall()
    return total_div, asoc


def reconciliaza(conn, schema, perioada, res, manual=None):
    """NU ridica. {"acoperit":bool, "motiv":str|None, "divergente":[...]}."""
    manual = manual or {}
    if manual.get("beneficiari"):
        return {"acoperit": False, "divergente": [],
                "motiv": "beneficiari introdusi manual de contabil (§8) - recalculul din 457 nu se aplica."}
    an = perioada.an
    from core import common as _c   # registrul de lege (cota impozit dividende period-aware)
    cota_div = Decimal(str(_c.cota("impozit_dividend", date(an, 12, 31))[0]))
    total_div, asoc = _dividende_independent(conn, an)
    gen = {str(b.cif): b for b in res.beneficiari}
    divergente = []
    for nume, cnp, cota in asoc:
        parte = _q(Decimal(total_div) * Decimal(str(cota)) / Decimal(100))
        if parte <= 0:
            continue
        imp = _q(Decimal(parte) * cota_div)
        b = gen.get(str(cnp or ""))
        if b is None:
            divergente.append({"beneficiar": cnp or nume, "camp": "beneficiar LIPSA din declaratie",
                               "generator": 0, "cale2_baza": parte, "cale2_imp": imp})
            continue
        if int(b.baza1) != parte:
            divergente.append({"beneficiar": cnp or nume, "camp": "baza",
                               "generator": int(b.baza1), "cale2": parte, "diferenta": int(b.baza1) - parte})
        if int(b.imp1) != imp:
            divergente.append({"beneficiar": cnp or nume, "camp": "impozit",
                               "generator": int(b.imp1), "cale2": imp, "diferenta": int(b.imp1) - imp})
    return {"acoperit": True, "motiv": None, "divergente": divergente}


def verifica_reconciliere(conn, schema, perioada, res, manual=None):
    """POARTA (hard-block): ridica ReconciliereD205 daca baza/impozitul pe dividende nu se leaga de
    recalculul independent. Numeste beneficiarul si AMBELE valori. NU repara tacit."""
    rap = reconciliaza(conn, schema, perioada, res, manual)
    if rap["divergente"]:
        det = []
        for d in rap["divergente"]:
            if d["camp"].startswith("beneficiar LIPSA"):
                det.append("beneficiar %s: %s (cale2 baza=%d imp=%d)"
                           % (d["beneficiar"], d["camp"], d["cale2_baza"], d["cale2_imp"]))
            else:
                det.append("beneficiar %s %s: generator=%d vs cale2=%d (dif %d)"
                           % (d["beneficiar"], d["camp"], d["generator"], d["cale2"], d["diferenta"]))
        raise ReconciliereD205(
            "D205 A DOUA CALE: baza/impozitul pe dividende ale generatorului NU se leaga de recalculul "
            "independent din contul 457. Divergente: %s. Declaratia NU se genereaza - gardul nu alege "
            "singur cine are dreptate; verifica agregarea si datele." % "; ".join(det))
    return rap
