# -*- coding: utf-8 -*-
"""
core/echilibru_perioada.py — C3 (integritate in TIMP): partida dubla la nivel de PERIOADA/tenant + orfani.

A DOUA CALE pentru ce DUK NU verifica: DUK accepta un GL (SAF-T / registru) STRUCTURAL valid dar cu Sigma debit !=
Sigma credit (descoperit la tura 10: TotalDebit 0 vs TotalCredit 15000 trecea DUK). verificatoare.verifica_balanta
verifica egalitatea pe un obiect balanta construit, dar NIMENI n-o rula pe ledger-ul REAL al unei perioade. Aici:
- echilibru_perioada(linii): Sigma(suma pe cont_debit) == Sigma(suma pe cont_credit) - o linie cu o parte lipsa
  (debit SAU credit gol) rupe egalitatea = eroare de integritate (retroactiv / import stricat / editare in luna).
- orfani(linii, id_uri): linii care trimit la o inregistrare inexistenta.
PUR (primeste linii), deci testabil fara DB; un reader DB subtire (echilibru_perioada_db) il aplica pe perioada.
LIMITA declarata: nu e snapshot+hash (regenerare-diff a declaratiei depuse) - aia e alta felie C3 (state_plata
snapshot DECIS in GARZI INVENTAR A). Aici doar invariantul contabil Sigma debit=Sigma credit + orfani.
"""
from decimal import Decimal


def _d(x):
    if isinstance(x, Decimal):
        return x
    return Decimal(str(x or 0))


def echilibru_perioada(linii):
    """PUR. linii = [{cont_debit, cont_credit, suma}, ...]. Intoarce (sigma_debit, sigma_credit, echilibrat: bool).
    O partida dubla corecta: fiecare linie are AMBELE conturi si aceeasi suma pe debit si credit -> egale. Daca o
    linie are o parte lipsa (cont gol), suma ei intra doar pe o parte -> Sigma-le difera = DEZECHILIBRU."""
    sd = sum((_d(l.get("suma")) for l in linii if l.get("cont_debit")), Decimal(0))
    sc = sum((_d(l.get("suma")) for l in linii if l.get("cont_credit")), Decimal(0))
    return sd, sc, sd == sc


def orfani(linii, id_uri_inregistrari):
    """PUR. Linii al caror inregistrare_id NU e in setul de inregistrari existente (referinta rupta)."""
    valide = set(id_uri_inregistrari or ())
    return [l for l in linii if l.get("inregistrare_id") not in valide]


def echilibru_perioada_db(conn, schema, an, luna, doar_validate=True):
    """Reader DB subtire: aplica echilibru_perioada + orfani pe liniile perioadei (note validate). Intoarce dict cu
    starea. NU ridica - semnaleaza (jobul consuma rezultatul; hard-block la nevoie de apelant)."""
    inceput = "%04d-%02d-01" % (an, luna)
    sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
    filtru = "AND i.status = 'validata'" if doar_validate else ""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT l.inregistrare_id, l.cont_debit, l.cont_credit, l.suma "
            "FROM %s.inregistrari_linii l JOIN %s.inregistrari i ON i.id = l.inregistrare_id "
            "WHERE i.data >= %%s AND i.data < %%s %s" % (schema, schema, filtru),
            (inceput, sfarsit))
        linii = [{"inregistrare_id": r[0], "cont_debit": r[1], "cont_credit": r[2], "suma": r[3]} for r in cur.fetchall()]
        cur.execute("SELECT id FROM %s.inregistrari" % schema)
        id_uri = {r[0] for r in cur.fetchall()}
    sd, sc, echilibrat = echilibru_perioada(linii)
    orf = orfani(linii, id_uri)
    return {"an": an, "luna": luna, "sigma_debit": sd, "sigma_credit": sc,
            "echilibrat": echilibrat, "diferenta": sd - sc, "orfani": len(orf)}
