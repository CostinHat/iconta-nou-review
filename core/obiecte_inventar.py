# -*- coding: utf-8 -*-
"""Obiecte de inventar (303) - motor PUR (OMFP 1802/2014).
Prag mijloc fix: 5.000 lei din 25.02.2026 (OUG 8/2026 art. 28(2)b; anterior
2.500 lei HG 276/2013). MF existente la 31.12.2025 cu valoare 2.500-5.000 se
amortizeaza pe durata ramasa (art. 45(21^3)) - NU se reclasifica.
Sub prag sau durata <1 an -> obiect de inventar:
- achizitie: 303 + 4426 = 401;
- dare in folosinta: 603 = 303 (integral pe cheltuiala) + evidenta
  extracontabila D8035 pana la scoaterea din uz (C8035)."""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date

B = Decimal("0.01")
PRAG_NOU = Decimal("5000")   # OUG 8/2026, de la 25.02.2026
PRAG_VECHI = Decimal("2500")
DATA_PRAG_NOU = date(2026, 2, 25)

def prag_mf(la_data=None):
    ref = la_data or date.today()
    return PRAG_NOU if ref >= DATA_PRAG_NOU else PRAG_VECHI

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def e_obiect_inventar(valoare, la_data=None, durata_sub_1_an=False):
    """Sub pragul MF sau durata <1 an -> obiect de inventar."""
    return durata_sub_1_an or _d(valoare) < prag_mf(la_data)

def nota_achizitie(valoare, cota_tva=None):
    if cota_tva is None:
        raise ValueError("Cota de TVA nu s-a dat. Nu se folosește o valoare implicită: o cotă scrisă în cod se rupe tăcut de lege la prima schimbare, iar o operațiune veche are altă cotă decât una de azi. Declară cota operațiunii.")
    v = _d(valoare)
    if v <= 0:
        raise ValueError("Valoarea introdusă e invalidă (trebuie un număr pozitiv).")
    tva = (v * Decimal(str(cota_tva)) / 100).quantize(B, rounding=ROUND_HALF_UP)
    linii = [("303", "401", v)]
    if tva > 0:
        linii.append(("4426", "401", tva))
    return {"linii": linii, "tva": tva}

def nota_dare_folosinta(valoare):
    """603=303 + D8035 extracontabil (contrapartida tehnica 891)."""
    v = _d(valoare)
    if v <= 0:
        raise ValueError("Valoarea introdusă e invalidă (trebuie un număr pozitiv).")
    return {"linii": [("603", "303", v), ("8035", "891", v)]}

def nota_scoatere_uz(valoare):
    """C8035 la casare/scoatere din uz (proces-verbal)."""
    v = _d(valoare)
    if v <= 0:
        raise ValueError("Valoarea introdusă e invalidă (trebuie un număr pozitiv).")
    return {"linii": [("891", "8035", v)]}
