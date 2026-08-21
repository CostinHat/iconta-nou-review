# -*- coding: utf-8 -*-
"""Reconciliere bancară — matching linii extras pe facturi deschise.

Motor pur: nu atinge DB. Primește linii de extras (din banca_parser.parse_extras,
îmbogățite cu cui via banca.extrage_cui) și facturi deschise ca liste de dict.

Factură deschisă: {"id", "tert_cui", "directie" ('emisa'/'primita'),
                   "data_emitere" (date/str sortabil), "sold" (Decimal/float)}
Linie extras:     {"suma" (>0), "tip" ('incasare'/'plata'), "cui" (str|None),
                   "descriere", "data"}

Rezultat per linie: {"status": 'verde'|'galben'|'rosu',
                     "alocari": [{"factura_id", "suma"}],
                     "motiv": str}
verde  = match exact (o factură sau combinație cu sumă identică)
galben = alocare parțială / FIFO (necesită confirmare atentă)
rosu   = fără CUI sau fără facturi deschise ale partenerului
"""
from core import afirmatii as _af  # [P8] absenta spune UNDE s-a cautat
from decimal import Decimal
from itertools import combinations

TOLERANTA = Decimal("0.01")
MAX_COMBO = 4  # max facturi într-o combinație exactă


def _d(v):
    return v if isinstance(v, Decimal) else Decimal(str(v))


def _norm_cui(cui):
    if not cui:
        return None
    return str(cui).upper().replace("RO", "").strip() or None


def facturi_partener(facturi_deschise, cui, tip):
    """Facturile deschise ale partenerului cu CUI dat, pe direcția potrivită tipului.
    incasare -> emise; plata -> primite. Sortate crescător după data_emitere (FIFO)."""
    cui = _norm_cui(cui)
    if not cui:
        return []
    directie = "emisa" if tip == "incasare" else "primita"
    rez = [f for f in facturi_deschise
           if _norm_cui(f.get("tert_cui")) == cui
           and f.get("directie") == directie
           and _d(f.get("sold", 0)) > TOLERANTA]
    return sorted(rez, key=lambda f: (str(f.get("data_emitere") or ""), f["id"]))


def _match_exact_una(suma, facturi):
    for f in facturi:
        if abs(_d(f["sold"]) - suma) <= TOLERANTA:
            return f
    return None


def _match_combo(suma, facturi):
    """Combinație de 2..MAX_COMBO facturi cu sumă exactă. Preferă seturile mai mici,
    apoi facturile mai vechi (facturi e deja FIFO)."""
    if len(facturi) > 12:  # limită anti-exploziv; peste, doar FIFO
        facturi = facturi[:12]
    for n in range(2, min(MAX_COMBO, len(facturi)) + 1):
        for combo in combinations(facturi, n):
            if abs(sum(_d(f["sold"]) for f in combo) - suma) <= TOLERANTA:
                return list(combo)
    return None


def _alocare_fifo(suma, facturi):
    """Alocă suma FIFO pe facturi; ultima poate fi parțială. Întoarce (alocari, rest)."""
    alocari, rest = [], suma
    for f in facturi:
        if rest <= TOLERANTA:
            break
        sold = _d(f["sold"])
        parte = min(sold, rest)
        alocari.append({"factura_id": f["id"], "suma": parte})
        rest -= parte
    return alocari, rest


def potriveste_linie(linie, facturi_deschise):
    """Matching pentru o linie de extras. Vezi docstring modul pentru contract."""
    suma = _d(linie.get("suma", 0)).copy_abs()
    cui = _norm_cui(linie.get("cui"))
    if not cui:
        return dict(_af.afirmatie(
            "absenta_observatie", "reconciliere extras",
            "fără CUI în descriere",
            surse_consultate="descrierea liniei de extras (câmpul din care se extrage CUI-ul)"),
            status="rosu", alocari=[])

    facturi = facturi_partener(facturi_deschise, cui, linie.get("tip"))
    if not facturi:
        return dict(_af.afirmatie(
            "absenta_observatie", "reconciliere extras",
            f"niciun document deschis pentru CUI {cui}",
            surse_consultate=f"documentele DESCHISE ale partenerului cu CUI {cui} "
                             f"(cele stinse nu se caută)"),
            status="rosu", alocari=[])

    f = _match_exact_una(suma, facturi)
    if f:
        return {"status": "verde",
                "alocari": [{"factura_id": f["id"], "suma": suma}],
                "motiv": "match exact pe o factura"}

    combo = _match_combo(suma, facturi)
    if combo:
        return {"status": "verde",
                "alocari": [{"factura_id": f["id"], "suma": _d(f["sold"])} for f in combo],
                "motiv": f"match exact pe {len(combo)} facturi"}

    alocari, rest = _alocare_fifo(suma, facturi)
    if rest > TOLERANTA:
        return {"status": "galben", "alocari": alocari,
                "motiv": f"suma depășește soldul total; rest nealocat {rest}"}
    return {"status": "galben", "alocari": alocari,
            "motiv": "alocare partiala FIFO"}


def potriveste_extras(linii, facturi_deschise):
    """Matching pentru toate liniile. Soldurile se consumă secvențial:
    o factură alocată integral la linia N nu mai e disponibilă la linia N+1."""
    solduri = {f["id"]: _d(f["sold"]) for f in facturi_deschise}
    rezultate = []
    for linie in linii:
        disponibile = [dict(f, sold=solduri[f["id"]])
                       for f in facturi_deschise if solduri[f["id"]] > TOLERANTA]
        rez = potriveste_linie(linie, disponibile)
        for a in rez["alocari"]:
            solduri[a["factura_id"]] -= _d(a["suma"])
        rezultate.append(rez)
    return rezultate
