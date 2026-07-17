"""
core/control_fiscal_api.py — semafor de conformare fiscala per firma (cross-portfolio).

Pentru fiecare firma:
  1. citeste vectorul fiscal (firma_profil: regim_fiscal, platitor_tva, tip_decont, operatiuni_ic)
     + are_salariati (din tabelul salariati)
  2. deriva ce declaratii sunt DATORATE pe perioadele trecute (scadentar in cod)
  3. compara cu public.declaratii_depuse
  4. intoarce semafor (verde/galben/gri/rosu) + lista lipsuri + lista neclar

Principiu (v2, dupa 5 patch-uri): semaforul NU inventeaza un raspuns plauzibil cand
nu stie. Un atribut de vector necompletat -> declaratia care depinde de el iese GRI
cu cauza declarata, NU un default tacut. "Nu stiu" e o stare vizibila, nu verde.

Scadentar: sursa UNICA e core/scadente.py (F081, verificat la calendarul oficial ANAF
2026) — 25 ale lunii urmatoare pentru D100/D112/D300/D390, 25 martie an urmator pentru
D101, mutat la prima zi lucratoare cu SARBATORILE legale (Paste mobil inclus). Nu se
mai reimplementeaza aici (D1: weekend-only ignora sarbatorile -> fals rosu; D4: ziua 25
hardcodata cu D101 lipit pe langa).
"""
from __future__ import annotations
import datetime

from core import scadente  # sursa unica de scadente + zile lucratoare (fara import circular)

PRAG_URMARIT_ZILE = 7   # termen in <= 7 zile, nedepus -> galben

# nume scurt de perioada pentru afisare
_LUNI_NUME = ["", "ian", "feb", "mar", "apr", "mai", "iun", "iul", "aug", "sep", "oct", "noi", "dec"]


def _termen(an, luna=None, tip="d300"):
    """Termenul de depunere al declaratiei `tip` pentru perioada (an, luna), delegat la
    core/scadente.py (25/martie per tip + prima zi lucratoare cu sarbatori legale).
    Semnatura pastreaza forma (an, luna) folosita de termene_api._termen."""
    return scadente.scadenta_data(tip, an, luna=luna)


def declaratii_datorate(vector, are_salariati, azi=None):
    """
    Intoarce {"datorate": [...], "neclar": [...]}.
      - datorate: declaratiile cu termen trecut sau in fereastra de urmarire (fapt cunoscut).
      - neclar:   declaratiile pe care NU le pot stabili fiindca lipseste un atribut din vector
                  (fiecare cu {tip, cauza}). Se afiseaza GRI, cu buton catre Vectorul fiscal.
    vector = dict cu regim_fiscal, platitor_tva, tip_decont, operatiuni_ic (oricare poate fi None).
    """
    azi = azi or datetime.date.today()
    an = azi.year
    limita = azi + datetime.timedelta(days=PRAG_URMARIT_ZILE)
    datorate, neclar = [], []

    # D2: perioadele candidate pornesc de la decembrie / T4 al anului precedent (termen 25 ian
    # an curent), altfel decembrie an-1 e invizibil PERMANENT (in an-1 termenul e viitor, in an
    # bucla nu-l acopera). Filtrul term<=limita taie singur ce e in viitor.
    per_luni = [(an - 1, 12)] + [(an, m) for m in range(1, 13)]
    per_trim = [(an - 1, 4, 12)] + [(an, tri, lf) for tri, lf in enumerate([3, 6, 9, 12], start=1)]

    def adauga(tip, a, luna_perioada, perioada_txt, tip_scad):
        term = _termen(a, luna_perioada, tip=tip_scad)
        if term <= limita:
            datorate.append({"tip": tip, "an": a, "luna": luna_perioada,
                             "termen": term.isoformat(), "perioada": perioada_txt})

    def gri(tip, cauza):
        neclar.append({"tip": tip, "cauza": cauza})

    platitor_tva = vector.get("platitor_tva")
    tip_decont = vector.get("tip_decont")
    regim_fiscal = vector.get("regim_fiscal")
    operatiuni_ic = vector.get("operatiuni_ic")

    # D300 TVA — depinde de platitor_tva (DACA datoreaza) + tip_decont (PERIODICITATEA)
    if platitor_tva is None:
        gri("D300", "Platitor de TVA necompletat in vectorul fiscal - nu pot sti daca datorezi D300.")
    elif platitor_tva:
        decont = (tip_decont or "").strip().lower()
        if decont == "trimestrial":
            for a, tri, lf in per_trim:
                adauga("D300", a, lf, f"T{tri}", "d300")
        elif decont == "lunar":
            for a, m in per_luni:
                adauga("D300", a, m, _LUNI_NUME[m], "d300")
        else:
            gri("D300", "Tip decont TVA necompletat - nu pot sti periodicitatea D300 (lunar/trimestrial).")
    # platitor_tva == False -> nu se datoreaza D300 (cunoscut)

    # D112 salariati (lunar) — are_salariati e fapt din DB, mereu cunoscut
    if are_salariati:
        for a, m in per_luni:
            adauga("D112", a, m, _LUNI_NUME[m], "d112")

    # D100 (micro, trimestrial) / D101 (profit, anual) — depind de regim_fiscal
    if regim_fiscal is None:
        cauza_r = "Regim fiscal necompletat - nu pot sti daca datorezi D100 (micro) sau D101 (profit)."
        gri("D100", cauza_r)
        gri("D101", cauza_r)
    else:
        regim = regim_fiscal.strip().lower()
        if regim == "micro":
            for a, tri, lf in per_trim:
                adauga("D100", a, lf, f"T{tri}", "d100")
        elif regim == "profit":
            # D101 pentru anul precedent, termen 25 martie an curent
            term = _termen(an - 1, tip="d101")
            if term <= limita:
                datorate.append({"tip": "D101", "an": an - 1, "luna": 12,
                                 "termen": term.isoformat(), "perioada": f"anual {an-1}"})

    # D390 operatiuni intracomunitare (lunar)
    if operatiuni_ic is None:
        gri("D390", "Operatiuni intracomunitare necompletat - nu pot sti daca datorezi D390.")
    elif operatiuni_ic:
        for a, m in per_luni:
            adauga("D390", a, m, _LUNI_NUME[m], "d390")

    return {"datorate": datorate, "neclar": neclar}


def _verdict(datorate, neclar, depuse, azi):
    """Pur: din datorate + neclar + set-ul depuse -> (stare, lipsa, urmarit).
    Prioritate: rosu (restanta cunoscuta) > galben (termen apropiat cunoscut) >
    gri (nu pot sti - atribut vector lipsa) > verde. Gri nu poate fi ascuns ca verde."""
    lipsa, urmarit = [], []
    for d in datorate:
        if (d["tip"], d["an"], d["luna"]) in depuse:
            continue
        term = datetime.date.fromisoformat(d["termen"])
        if term < azi:
            lipsa.append(d)          # termen trecut, nedepus -> restanta
        else:
            urmarit.append(d)        # in fereastra, nedepus -> de urmarit
    if lipsa:
        stare = "rosu"
    elif urmarit:
        stare = "galben"
    elif neclar:
        stare = "gri"
    else:
        stare = "verde"
    return stare, lipsa, urmarit


def evalueaza_firma(conn_schema, conn_public, tenant_id, schema, azi=None):
    """
    Intoarce {stare, datorate, depuse, lipsa, urmarit, neclar} pentru o firma.
    stare: 'verde' / 'galben' / 'gri' / 'rosu'.
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
                "neclar": [], "mesaj": "vector fiscal necompletat"}

    rez = declaratii_datorate(vector, are_sal, azi)
    datorate, neclar = rez["datorate"], rez["neclar"]

    # depuse din public
    with conn_public.cursor() as cur:
        cur.execute("SELECT tip, an, luna FROM public.declaratii_depuse WHERE tenant_id=%s", (tenant_id,))
        depuse = {(t, a, l) for (t, a, l) in cur.fetchall()}

    stare, lipsa, urmarit = _verdict(datorate, neclar, depuse, azi)

    return {"stare": stare, "datorate": len(datorate), "depuse": len(depuse),
            "lipsa": lipsa, "urmarit": urmarit, "neclar": neclar}
