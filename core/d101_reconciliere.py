"""
core/d101_reconciliere.py — A DOUA CALE D101 (gard de continut, 05.08.2026, pas 5/6).

ACOPERA PROFITUL CONTABIL, NU pe cel IMPOZABIL (scris ca atare, NU "D101 acoperit").

De ce doar contabil: in D101, doar baza CONTABILA (P1 venituri exploatare, P2 cheltuieli
exploatare, P4 venituri financiare, P5 cheltuieli financiare) vine din contabilitate (pull pe
inregistrari_linii, clasele 7/6). Ajustarile FISCALE (P6 deduceri, P7, P8 nedeductibile,
pierderi reportate...) sunt INTRARI MANUALE ale contabilului (default 0) - datele lui, §8 - iar
profitul impozabil P9 = FORMULA oficiala pe ele, deja pazita de golden-ul lantului de formule
(test_golden_lant_formule_oficiale). Deci calea 2 recalculeaza INDEPENDENT P1/P2/P4/P5 din
balanta si le confrunta cu generatorul; NU verifica P9 (impozabilul).

CE PRINDE: o agregare gresita a veniturilor/cheltuielilor (clasa 7/6) care intra in D101 - drop
de cont, clasa gresita (exploatare vs financiar), semn. Baza pe care se cladeste tot restul.
CE NU (LIMITA, GARZI cat.4):
  - Ajustarile fiscale (P6/P7/P8/...) si profitul IMPOZABIL P9 - intrari manuale (§8) + golden.
  - P1/P2/P4/P5 suprascrise prin `manual` de contabil -> NEACOPERIT (sarite).
  - Input partajat gresit (aceeasi postare gresita citita de ambele cai) - §8.

NON-TAUTOLOGIE (AST): NU importa/foloseste d101.calcul_d101 / d101.pull. SQL propriu pe
inregistrari_linii (aceeasi sursa, agregare INDEPENDENTA de pull). Divergenta = HARD-BLOCK care
numeste randul si AMBELE valori; NU repara tacit (tipar DECIZII 05.08).
"""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP


class ReconciliereD101(ValueError):
    """Baza contabila (venituri/cheltuieli) a generatorului nu se leaga de recalculul din balanta."""


def _q(x):
    return int(Decimal(x).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _baza_contabila_independenta(conn, an):
    """P1/P2/P4/P5 din inregistrari_linii (note VALIDATE, anul), SQL PROPRIU. Split exploatare/
    financiar dupa clasa de cont (76/66 = financiar), ca planul RO. Independent de d101.pull."""
    inc, sf = date(an, 1, 1).isoformat(), date(an + 1, 1, 1).isoformat()
    q = ("SELECT "
         "COALESCE(SUM(CASE WHEN l.cont_credit LIKE '76%%' THEN l.suma ELSE 0 END),0) AS ven_fin, "
         "COALESCE(SUM(CASE WHEN l.cont_credit LIKE '7%%' AND l.cont_credit NOT LIKE '76%%' THEN l.suma ELSE 0 END),0) AS ven_expl, "
         "COALESCE(SUM(CASE WHEN l.cont_debit LIKE '66%%' THEN l.suma ELSE 0 END),0) AS chelt_fin, "
         "COALESCE(SUM(CASE WHEN l.cont_debit LIKE '6%%' AND l.cont_debit NOT LIKE '66%%' THEN l.suma ELSE 0 END),0) AS chelt_expl "
         "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
         "WHERE i.status='validata' AND i.data >= %s AND i.data < %s")
    with conn.cursor() as cur:
        cur.execute(q, (inc, sf))
        ven_fin, ven_expl, chelt_fin, chelt_expl = cur.fetchone()
    return {"P1": _q(ven_expl or 0), "P2": _q(chelt_expl or 0),
            "P4": _q(ven_fin or 0), "P5": _q(chelt_fin or 0)}


_ETICHETA = {"P1": "venituri exploatare", "P2": "cheltuieli exploatare",
             "P4": "venituri financiare", "P5": "cheltuieli financiare"}


def reconciliaza(conn, schema, perioada, res, manual=None):
    """NU ridica. {"divergente":[...], "sarite":[P suprascrise manual]}."""
    manual = manual or {}
    exp = _baza_contabila_independenta(conn, perioada.an)
    divergente, sarite = [], []
    for p in ("P1", "P2", "P4", "P5"):
        if p in manual:
            sarite.append(p); continue   # contabil a suprascris baza -> in afara scopului
        gen = int(res.P.get(p, 0) or 0)
        if gen != exp[p]:
            divergente.append({"rand": p, "eticheta": _ETICHETA[p],
                               "generator": gen, "cale2": exp[p], "diferenta": gen - exp[p]})
    return {"divergente": divergente, "sarite": sarite}


def verifica_reconciliere(conn, schema, perioada, res, manual=None):
    """POARTA (hard-block): ridica ReconciliereD101 daca baza CONTABILA a generatorului nu se leaga
    de recalculul din balanta. Numeste randul si AMBELE valori. NU repara tacit."""
    rap = reconciliaza(conn, schema, perioada, res, manual)
    if rap["divergente"]:
        linii = "; ".join("%s (%s): generator=%d vs cale2=%d (dif %d)" %
                          (d["rand"], d["eticheta"], d["generator"], d["cale2"], d["diferenta"])
                          for d in rap["divergente"])
        raise ReconciliereD101(
            "D101 A DOUA CALE (profit CONTABIL, nu impozabil): veniturile/cheltuielile din balanta "
            "NU se leaga de recalculul independent. Divergente: %s. Declaratia NU se genereaza - "
            "gardul nu alege singur cine are dreptate; verifica agregarea si notele." % linii)
    return rap
