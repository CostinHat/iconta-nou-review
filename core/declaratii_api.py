"""
core/declaratii_api.py — dispatch pentru cele 9 declarații. O singură rută în
main.py cheamă aici; diferențele de semnătură genereaza() stau în ADAPTOARE,
izolate, ca ruta să fie uniformă.

Periodicitate (din realitatea declarațiilor, nu forțată uniform):
  lunar      : d112, d300, d301, d390, d394, d406
  trimestrial: d100
  anual      : d101, d205

Parametri speciali (în body, opționali):
  manual     : d300, d390, d394  (rânduri TVA introduse de contabil)
  cota       : d100
  date_extra, ca_an_precedent_eur : d101

CALCUL+DB stau în module (au pull+genereaza). Aici doar: validare cerere (pură)
+ alegere adaptor. Se dovedește pe server: apelul real genereaza pe schema tenant.
"""
from __future__ import annotations

from core import (d100, d101, d112, d205, d300, d301, d390, d394, d406)

REGULI = "2026.1"
MODUL = "declaratii_api"


# ============================================================
#  ADAPTOARE — un loc unde se absoarbe diferența de semnătură.
#  Fiecare primește (conn, schema, body) și cheamă genereaza corect.
# ============================================================
def _d100(conn, schema, b):
    return d100.genereaza(conn, schema, b["an"], b["trim"], b.get("cota"))

def _d101(conn, schema, b):
    # d101.genereaza() a fost rescris 16.07.2026 pe structura oficiala D101
    # individual (nu D101G grup) - semnatura noua: (conn, schema, an, manual=None).
    # manual = suprascrieri optionale (venituri_totale, cheltuieli_totale etc.)
    manual = dict(b.get("date_extra") or {})
    if b.get("ca_an_precedent_eur"):
        manual.setdefault("ca_an_precedent_eur", b["ca_an_precedent_eur"])
    return d101.genereaza(conn, schema, b["an"], manual or None)

def _d112(conn, schema, b):
    return d112.genereaza(conn, schema, b["an"], b["luna"])

def _d205(conn, schema, b):
    return d205.genereaza(conn, schema, b["an"])

def _d300(conn, schema, b):
    return d300.genereaza(conn, schema, b["an"], b["luna"], b.get("manual"))

def _d301(conn, schema, b):
    return d301.genereaza(conn, schema, b["an"], b["luna"])

def _d390(conn, schema, b):
    return d390.genereaza(conn, schema, b["an"], b["luna"], b.get("manual"))

def _d394(conn, schema, b):
    return d394.genereaza(conn, schema, b["an"], b["luna"], b.get("manual"))

def _d406(conn, schema, b):
    return d406.genereaza(conn, schema, b["an"], b["luna"])


# tip -> (periodicitate, adaptor). Adăugarea unei declarații = o linie aici.
DECLARATII = {
    "d100": ("trimestrial", _d100),
    "d101": ("anual",       _d101),
    "d112": ("lunar",       _d112),
    "d205": ("anual",       _d205),
    "d300": ("lunar",       _d300),
    "d301": ("lunar",       _d301),
    "d390": ("lunar",       _d390),
    "d394": ("lunar",       _d394),
    "d406": ("lunar",       _d406),
}


def tipuri():
    """Lista tipurilor suportate (pentru frontend / validare)."""
    return sorted(DECLARATII.keys())


def periodicitate(tip):
    """'lunar'|'trimestrial'|'anual' sau None dacă tip necunoscut."""
    rec = DECLARATII.get(tip)
    return rec[0] if rec else None


# ============================================================
#  VALIDARE CERERE — PURĂ (testabilă fără DB)
# ============================================================
def valideaza_cerere(tip, body):
    """
    Verifică tip + parametrii ceruți de periodicitate. Întoarce listă erori
    (gol = ok). Nu atinge DB.
    """
    erori = []
    per = periodicitate(tip)
    if per is None:
        return ["tip declarație necunoscut: %r (suportate: %s)"
                % (tip, ", ".join(tipuri()))]

    an = body.get("an")
    if not isinstance(an, int) or an < 2020 or an > 2100:
        erori.append("an invalid: %r (aștept întreg 2020-2100)" % (an,))

    if per == "lunar":
        luna = body.get("luna")
        if not isinstance(luna, int) or luna < 1 or luna > 12:
            erori.append("luna invalidă: %r (aștept 1-12)" % (luna,))
    elif per == "trimestrial":
        trim = body.get("trim")
        if not isinstance(trim, int) or trim < 1 or trim > 4:
            erori.append("trimestru invalid: %r (aștept 1-4)" % (trim,))
    # 'anual' nu cere nimic în plus față de an

    return erori


# ============================================================
#  DISPATCH — alege adaptorul, cheamă genereaza. Parte DB (pe server).
# ============================================================
def genereaza(conn, schema, tip, body):
    """
    Validează cererea, apoi cheamă adaptorul potrivit.
    Întoarce (xml, rezultat) de la modul.
    Ridică ValueError cu erorile dacă cererea e invalidă.
    """
    erori = valideaza_cerere(tip, body)
    if erori:
        raise ValueError("; ".join(erori))
    _per, adaptor = DECLARATII[tip]
    return adaptor(conn, schema, body)
