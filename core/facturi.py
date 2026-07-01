"""
core/facturi.py — contare facturi + TVA + storno. Calcul PUR, fără DB.
Construit de la zero din OMFP 1802/2014 + Cod fiscal (TVA, taxare inversă art. 331).

Conturi:
  emisă:   4111 Clienți ; 4427 TVA colectată ; venituri 701/703/704/707
  primită: 401 Furnizori ; 4426 TVA deductibilă ; 301/302/371/6xx
  taxare inversă: 4426 = 4427 (autocolectare la beneficiar)
"""
from __future__ import annotations
from decimal import Decimal

from core import common as c
from core.common import _dec, _q

REGULI = "2026.1"
MODUL = "facturi"

VENIT = {            # tip -> cont de venit (factură emisă)
    "marfa": "707",
    "produse": "701",
    "servicii": "704",
    "prestari": "704",
    "reziduale": "703",
}
ACHIZITIE = {        # tip -> cont (factură primită)
    "marfa": "371",
    "materii_prime": "301",
    "materiale": "302",
    "obiecte_inventar": "303",
    "imobilizare": "213",
}


def _nota(debit, credit, suma, temei=None):
    n = {"debit": debit, "credit": credit, "suma": _q(suma),
         "modul": MODUL, "reguli": REGULI}
    if temei:
        n["temei"] = temei
    return n


# ============================================================
#  TVA pe cotă (cu dată de valabilitate)
# ============================================================
def calcul_tva(baza, cota=None, la_data=None):
    """
    Întoarce {tva, cota, temei}. Dacă `cota` lipsește, ia cota standard din common
    valabilă la `la_data` (prinde 19 vs 21 după perioadă).
    """
    if cota is None:
        cota, temei = c.cota("tva_standard", la_data)
    else:
        cota, temei = _dec(cota), "cotă specificată (redusă/scutită)"
    return {"tva": _q(_dec(baza) * cota), "cota": cota, "temei": temei}


# ============================================================
#  FACTURĂ EMISĂ (vânzare)
# ============================================================
def factura_emisa(baza, tip="marfa", cota=None, la_data=None, cont_venit=None):
    """4111 = venit (bază) ; 4111 = 4427 (TVA)."""
    cont = cont_venit or VENIT[tip]
    t = calcul_tva(baza, cota, la_data)
    note = [_nota("4111", cont, baza)]
    if t["tva"]:
        note.append(_nota("4111", "4427", t["tva"], temei=t["temei"]))
    return note


# ============================================================
#  FACTURĂ PRIMITĂ (achiziție)
# ============================================================
def factura_primita(baza, tip="marfa", cota=None, la_data=None, cont=None):
    """cont = 401 (bază) ; 4426 = 401 (TVA)."""
    c_ach = cont or ACHIZITIE[tip]
    t = calcul_tva(baza, cota, la_data)
    note = [_nota(c_ach, "401", baza)]
    if t["tva"]:
        note.append(_nota("4426", "401", t["tva"], temei=t["temei"]))
    return note


# ============================================================
#  TAXARE INVERSĂ (art. 331 Cod fiscal)
# ============================================================
def taxare_inversa(baza, tip="marfa", cota=None, la_data=None, cont=None):
    """
    La beneficiar: cont = 401 (bază, fără TVA pe 401) ; 4426 = 4427 (autocolectare).
    Nu se plătește TVA efectiv către furnizor.
    """
    c_ach = cont or ACHIZITIE[tip]
    t = calcul_tva(baza, cota, la_data)
    note = [_nota(c_ach, "401", baza)]
    if t["tva"]:
        note.append(_nota("4426", "4427", t["tva"],
                          temei="Cod fiscal art. 331 — taxare inversă"))
    return note


# ============================================================
#  STORNO (corecție în roșu — sume negative)
# ============================================================
def storno(note):
    """Întoarce aceleași note cu sume negative (corecție în același exercițiu, pct. 330)."""
    return [{**n, "suma": _q(-_dec(n["suma"])), "storno": True} for n in note]
