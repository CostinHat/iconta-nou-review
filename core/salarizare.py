"""
core/salarizare.py — calcul salariu brut→net + deduceri + monografie. Calcul PUR, fără DB.
Construit de la zero din Codul fiscal (art. 77, 78, 138, 156, 220^1) + OUG 156/2024.
Cotele (CAS/CASS/impozit/CAM, salariu minim, facilitate) vin din common cu DATĂ de valabilitate.

Conturi salarii (OMFP 1802):
  641 = 421 (brut) ; 421 = 4315 (CAS) ; 421 = 4316 (CASS) ; 421 = 444 (impozit)
  646 = 436 (CAM angajator) ; 421 = 5121 (plata net)
"""
from __future__ import annotations
from decimal import Decimal
from math import floor

from core import common as c
from core.common import _dec, _q

REGULI = "2026.1"
MODUL = "salarizare"

# deduceri (Cod fiscal art. 77)
PCT_DEDUCERE_BAZA = Decimal("0.20")        # 0 persoane în întreținere
PCT_PER_PERSOANA = Decimal("0.05")          # +5% per persoană (max 4)
PCT_TINERI = Decimal("0.15")                # +15% × salariu minim, tineri <26
DEDUCERE_COPIL_SCOALA = Decimal("100")      # +100 lei/copil la școală
PRAG_VENIT_DEDUCERE = Decimal("2000")       # plafon = salariu_minim + 2000


def _nota(debit, credit, suma, temei=None):
    n = {"debit": debit, "credit": credit, "suma": _q(suma),
         "modul": MODUL, "reguli": REGULI}
    if temei:
        n["temei"] = temei
    return n


# ============================================================
#  DEDUCERE PERSONALĂ (art. 77)
# ============================================================
def deducere_personala(brut, persoane=0, sub_26=False, copii_scoala=0,
                       functie_baza=True, la_data=None):
    """Întoarce {baza, tineri, copii, total} — sume scăzute din baza impozitului."""
    if not functie_baza:
        return {"baza": _q(0), "tineri": _q(0), "copii": _q(0), "total": _q(0)}
    sm, _ = c.cota("salariu_minim", la_data)
    b = _dec(brut)
    plafon = sm + PRAG_VENIT_DEDUCERE

    # — de bază —
    if b > plafon:
        ded_baza = Decimal(0)
    else:
        pct = PCT_DEDUCERE_BAZA + PCT_PER_PERSOANA * min(persoane, 4)
        if b > sm:
            trepte = floor((b - sm) / 50)
            pct = max(Decimal(0), pct - Decimal("0.005") * trepte)
        ded_baza = pct * sm

    # — suplimentar tineri <26 (brut între 2000 și plafon) —
    tineri = PCT_TINERI * sm if (sub_26 and PRAG_VENIT_DEDUCERE < b <= plafon) else Decimal(0)
    # — suplimentar copii la școală (indiferent de venit) —
    copii = DEDUCERE_COPIL_SCOALA * _dec(copii_scoala)

    total = ded_baza + tineri + copii
    return {"baza": _q(ded_baza), "tineri": _q(tineri),
            "copii": _q(copii), "total": _q(total)}


# ============================================================
#  CALCUL SALARIU BRUT → NET
# ============================================================
def calcul_salariu(brut, persoane=0, sub_26=False, copii_scoala=0,
                   functie_baza=True, la_data=None):
    """Întoarce breakdown complet: facilitate, CAS, CASS, deducere, impozit, net, CAM, cost."""
    b = _dec(brut)
    sm, temei_sm = c.cota("salariu_minim", la_data)
    cota_cas, _ = c.cota("cas", la_data)
    cota_cass, _ = c.cota("cass", la_data)
    cota_imp, _ = c.cota("impozit_venit", la_data)
    cota_cam, _ = c.cota("cam", la_data)
    facilitate_val, _ = c.cota("facilitate_salariu_minim", la_data)

    # facilitate (sumă netaxabilă) doar la salariul minim
    facilitate = facilitate_val if b <= sm else Decimal(0)
    baza_contrib = b - facilitate

    cas = baza_contrib * cota_cas
    cass = baza_contrib * cota_cass

    ded = deducere_personala(b, persoane, sub_26, copii_scoala, functie_baza, la_data)

    baza_imp = baza_contrib - cas - cass - _dec(ded["total"])
    if baza_imp < 0:
        baza_imp = Decimal(0)
    impozit = baza_imp * cota_imp
    net = b - cas - cass - impozit

    cam = b * cota_cam

    return {
        "brut": _q(b),
        "facilitate": _q(facilitate),
        "cas": _q(cas),
        "cass": _q(cass),
        "deducere": ded,
        "baza_impozabila": _q(baza_imp),
        "impozit": _q(impozit),
        "net": _q(net),
        "cam": _q(cam),
        "cost_angajator": _q(b + cam),
    }


# ============================================================
#  MONOGRAFIE SALARII — note cu urmă
# ============================================================
def monografie_salariu(calc):
    """Generează notele din rezultatul calcul_salariu."""
    return [
        _nota("641", "421", calc["brut"]),       # cheltuială salarii brute
        _nota("421", "4315", calc["cas"]),        # CAS reținut
        _nota("421", "4316", calc["cass"]),       # CASS reținut
        _nota("421", "444", calc["impozit"]),     # impozit pe venit
        _nota("646", "436", calc["cam"]),         # CAM angajator
    ]


def monografie_plata(net, cont_trezorerie="5121"):
    """421 = 5121/5311 (plata salariului net)."""
    return _nota("421", cont_trezorerie, net)
