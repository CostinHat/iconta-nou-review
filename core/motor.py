"""
core/motor.py — motor contabil: carte mare + rezultat + închidere lună/an. Calcul PUR.
Construit de la zero din OMFP 1802/2014 (pct. 421-423, funcțiunea conturilor 121/129/117).

Conturi:
  121 Profit sau pierdere   129 Repartizarea profitului
  117/1171 Rezultatul reportat   1061 Rezerve legale
  clasa 6 = cheltuieli   clasa 7 = venituri
"""
from __future__ import annotations
from decimal import Decimal

from core import common as c
from core.common import _dec, _q, agrega_conturi

REGULI = "2026.1"
MODUL = "motor"
TEMEI_INCHIDERE = "OMFP 1802/2014 pct. 422 (funcțiunea conturilor 121/129/117)"


def _nota(debit, credit, suma, temei=None):
    n = {"debit": debit, "credit": credit, "suma": _q(suma),
         "modul": MODUL, "reguli": REGULI}
    if temei:
        n["temei"] = temei
    return n


# ============================================================
#  CARTE MARE
# ============================================================
def carte_mare(note, solduri_initiale=None):
    """Rulaje debitoare/creditoare + sold pe fiecare cont (delegă la common)."""
    return agrega_conturi(note, solduri_initiale)


# ============================================================
#  REZULTAT (venituri − cheltuieli)
# ============================================================
def rezultat(note):
    ag = agrega_conturi(note)
    ven = chel = Decimal(0)
    for ct, v in ag.items():
        if ct.startswith("7"):
            ven += v["credit"] - v["debit"]      # venit = sold creditor
        elif ct.startswith("6"):
            chel += v["debit"] - v["credit"]      # cheltuială = sold debitor
    rez = ven - chel
    return {"venituri": _q(ven), "cheltuieli": _q(chel),
            "rezultat": _q(rez), "tip": "profit" if rez >= 0 else "pierdere"}


# ============================================================
#  ÎNCHIDERE LUNĂ — descărcare clasa 6 și 7 în 121
# ============================================================
def inchidere_luna(note):
    """7xx = 121 (venituri) ; 121 = 6xx (cheltuieli). Note cu urmă."""
    ag = agrega_conturi(note)
    inchidere = []
    for ct in sorted(ag):
        v = ag[ct]
        if ct.startswith("7"):
            venit = v["credit"] - v["debit"]
            if venit != 0:
                inchidere.append(_nota(ct, "121", venit, temei=TEMEI_INCHIDERE))
        elif ct.startswith("6"):
            chelt = v["debit"] - v["credit"]
            if chelt != 0:
                inchidere.append(_nota("121", ct, chelt, temei=TEMEI_INCHIDERE))
    return inchidere


# ============================================================
#  REZERVĂ LEGALĂ (31.12) — 5% din profit, plafon 20% capital
# ============================================================
def _rezerva_legala_2018(profit, capital_social, rezerva_existenta=0):
    """129 = 1061 cu 5% din profit, dar cumulat ≤ 20% din capitalul social."""
    p = _dec(profit)
    if p <= 0:
        return {"suma": _q(0), "nota": None}
    cota = p * Decimal("0.05")
    plafon = _dec(capital_social) * Decimal("0.20") - _dec(rezerva_existenta)
    suma = min(cota, plafon)
    if suma <= 0:
        return {"suma": _q(0), "nota": None}
    return {"suma": _q(suma),
            "nota": _nota("129", "1061", suma,
                          temei="OMFP 1802/2014 pct. 421; Legea 31/1990 art. 183")}


_VARIANTE_REZERVA_LEGALA = [
    ("2018-01-01", _rezerva_legala_2018,
     c.Temei("Legea", 31, 1990, art="183", data_in="2018-01-01", nivel_sursa="REDARE",
             de_cine="Code/Costin", verificat_la="2026-07-31", lant_acte="OMFP 1802/2014 pct.421")),
]


def rezerva_legala(profit, capital_social, rezerva_existenta=0, la_data=None):
    """Rezerva legala (5% profit, cumulat <= 20% capital), DISPECER pe la_data.
    TEMEI: Legea 31/1990 art.183 (rezerva legala 5% profit / plafon 20% capital social); OMFP 1802/2014
    pct.421 (nota 129=1061). nivel_sursa: REDARE. Versionata in timp: o schimbare de procent/plafon ->
    varianta datata noua, nu 'if data' in corp."""
    from datetime import date as _dt
    fn, _ = c.alege_varianta(_VARIANTE_REZERVA_LEGALA, la_data or _dt.today())
    return fn(profit, capital_social, rezerva_existenta)


# ============================================================
#  ÎNCHIDERE AN (la începutul anului următor)
# ============================================================
def inchidere_an(rezultat_val):
    """profit: 121 = 1171 ; pierdere: 1171 = 121."""
    r = _dec(rezultat_val)
    if r >= 0:
        return _nota("121", "1171", r, temei=TEMEI_INCHIDERE)
    return _nota("1171", "121", -r, temei=TEMEI_INCHIDERE)


def inchidere_129(suma):
    """La începutul anului următor: 121 = 129 (închidere repartizare profit)."""
    return _nota("121", "129", suma, temei=TEMEI_INCHIDERE)
