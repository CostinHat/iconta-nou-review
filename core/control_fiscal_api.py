"""
core/control_fiscal_api.py — semafor de conformare fiscala per firma (cross-portfolio).

Pentru fiecare firma:
  1. citeste vectorul fiscal (firma_profil: regim_fiscal, platitor_tva, tip_decont, operatiuni_ic)
     + are_salariati (din tabelul salariati)
  2. deriva ce declaratii sunt DATORATE pe perioadele trecute (scadentar in cod)
  3. compara cu public.declaratii_depuse
  4. intoarce semafor (verde/galben/rosu) + lista lipsuri

Scadentar 2026 (verificat ANAF):
  - termen standard ziua 25 a lunii urmatoare perioadei (daca e weekend -> prima zi lucratoare)
  - D300 TVA: lunar SAU trimestrial (dupa tip_decont)
  - D112: lunar daca are salariati
  - D100: trimestrial daca micro
  - D101: anual (25 martie an+1) daca profit
  - D390: lunar daca operatiuni intracomunitare
"""
from __future__ import annotations
import datetime

PRAG_URMARIT_ZILE = 7   # termen in <= 7 zile, nedepus -> galben


def _zi_lucratoare(d):
    """Daca d cade sambata/duminica, muta la luni."""
    while d.weekday() >= 5:   # 5=sam, 6=dum
        d += datetime.timedelta(days=1)
    return d


def _termen(an, luna):
    """Termenul de depunere = 25 a lunii urmatoare perioadei (an,luna), mutat in zi lucratoare."""
    luna_t = luna + 1
    an_t = an
    if luna_t > 12:
        luna_t = 1
        an_t += 1
    return _zi_lucratoare(datetime.date(an_t, luna_t, 25))


def _trimestre_pana_la(an, azi):
    """Lista (an, luna_finala_trimestru) cu termen <= azi+fereastra, pentru anul curent."""
    out = []
    for tri, luna_fin in enumerate([3, 6, 9, 12], start=1):
        out.append((an, luna_fin))
    return out


def declaratii_datorate(vector, are_salariati, azi=None):
    """
    Intoarce lista de {tip, an, luna, termen, perioada_txt} datorate pana acum (termen trecut
    sau in fereastra de urmarire). vector = dict cu regim_fiscal, platitor_tva, tip_decont, operatiuni_ic.
    """
    azi = azi or datetime.date.today()
    an = azi.year
    out = []
    limita = azi + datetime.timedelta(days=PRAG_URMARIT_ZILE)

    platitor_tva = bool(vector.get("platitor_tva"))
    decont = (vector.get("tip_decont") or "lunar").lower()
    regim = (vector.get("regim_fiscal") or "micro").lower()
    ic = bool(vector.get("operatiuni_ic"))

    def adauga(tip, a, luna_perioada, perioada_txt):
        term = _termen(a, luna_perioada)
        if term <= limita:   # datorata daca termenul a trecut sau e in fereastra
            out.append({"tip": tip, "an": a, "luna": luna_perioada,
                        "termen": term.isoformat(), "perioada": perioada_txt})

    luni_nume = ["", "ian", "feb", "mar", "apr", "mai", "iun", "iul", "aug", "sep", "oct", "noi", "dec"]

    # D300 TVA
    if platitor_tva:
        if decont == "trimestrial":
            for tri, luna_fin in enumerate([3, 6, 9, 12], start=1):
                adauga("D300", an, luna_fin, f"T{tri}")
        else:
            for luna in range(1, 13):
                adauga("D300", an, luna, luni_nume[luna])

    # D112 salariati (lunar)
    if are_salariati:
        for luna in range(1, 13):
            adauga("D112", an, luna, luni_nume[luna])

    # D100 micro (trimestrial)
    if regim == "micro":
        for tri, luna_fin in enumerate([3, 6, 9, 12], start=1):
            adauga("D100", an, luna_fin, f"T{tri}")

    # D101 profit (anual, termen 25 martie an+1 -> pentru anul precedent)
    if regim == "profit":
        # D101 pentru anul precedent, termen 25 martie an curent
        term = _zi_lucratoare(datetime.date(an, 3, 25))
        if term <= limita:
            out.append({"tip": "D101", "an": an - 1, "luna": 12,
                        "termen": term.isoformat(), "perioada": f"anual {an-1}"})

    # D390 operatiuni intracomunitare (lunar)
    if ic:
        for luna in range(1, 13):
            adauga("D390", an, luna, luni_nume[luna])

    return out


def evalueaza_firma(conn_schema, conn_public, tenant_id, schema, azi=None):
    """
    Intoarce {stare, datorate, depuse, lipsa, urmarit} pentru o firma.
    stare: 'verde' / 'galben' / 'rosu'.
    conn_schema: conexiune cu search_path pe schema firmei (firma_profil, salariati)
    conn_public: conexiune pe public (declaratii_depuse)
    """
    azi = azi or datetime.date.today()

    # vector + salariati
    with conn_schema.cursor() as cur:
        cur.execute("SELECT regim_fiscal, platitor_tva, tip_decont, operatiuni_ic FROM firma_profil LIMIT 1")
        row = cur.fetchone()
        vector = {}
        if row:
            vector = {"regim_fiscal": row[0], "platitor_tva": row[1],
                      "tip_decont": row[2], "operatiuni_ic": row[3]}
        cur.execute("SELECT to_regclass('salariati')")
        are_sal = False
        if cur.fetchone()[0]:
            cur.execute("SELECT count(*) FROM salariati WHERE activ=true")
            are_sal = cur.fetchone()[0] > 0

    if not vector:
        return {"stare": "gri", "datorate": 0, "depuse": 0, "lipsa": [], "urmarit": [],
                "mesaj": "vector fiscal necompletat"}

    datorate = declaratii_datorate(vector, are_sal, azi)

    # depuse din public
    with conn_public.cursor() as cur:
        cur.execute("SELECT tip, an, luna FROM public.declaratii_depuse WHERE tenant_id=%s", (tenant_id,))
        depuse = {(t, a, l) for (t, a, l) in cur.fetchall()}

    lipsa, urmarit = [], []
    for d in datorate:
        cheie = (d["tip"], d["an"], d["luna"])
        if cheie in depuse:
            continue
        term = datetime.date.fromisoformat(d["termen"])
        if term < azi:
            lipsa.append(d)            # termen trecut, nedepus -> restanta
        else:
            urmarit.append(d)          # in fereastra, nedepus -> de urmarit

    if lipsa:
        stare = "rosu"
    elif urmarit:
        stare = "galben"
    else:
        stare = "verde"

    return {"stare": stare, "datorate": len(datorate), "depuse": len(depuse),
            "lipsa": lipsa, "urmarit": urmarit}
