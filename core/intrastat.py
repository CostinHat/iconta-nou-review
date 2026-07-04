# -*- coding: utf-8 -*-
"""Intrastat - verificator praguri (Ordinul INS 1604/2025, MO 1022/05.11.2025).
Praguri 2026: 1.000.000 lei expedieri si 1.000.000 lei introduceri (separat pe
flux). Obligatia de declarare incepe cu LUNA in care valoarea CUMULATA de la
inceputul anului depaseste pragul, separat pe flux. Declaratia se depune lunar
la INS (intrastat.ro) cu coduri NC8 - aici doar monitorizam pragurile."""
from decimal import Decimal

PRAG_2026 = Decimal("1000000")
PRAG_ATENTIE = Decimal("0.80")  # avertizare la 80%

PREFIXE_UE = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "GR", "ES",
              "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL",
              "PL", "PT", "SE", "SI", "SK", "XI"}

def e_partener_ue(cui):
    """CUI cu prefix de stat membru UE (nu RO) -> operatiune intracomunitara."""
    c = (cui or "").strip().upper().replace(" ", "")
    return c[:2] in PREFIXE_UE

def analiza_flux(valori_lunare, prag=PRAG_2026):
    """valori_lunare: {luna(int): suma}. Returneaza cumulat, status
    (sub_prag|atentie|depasit), luna_depasirii, procent."""
    cumulat = Decimal("0")
    luna_dep = None
    for luna in sorted(valori_lunare):
        cumulat += Decimal(str(valori_lunare[luna] or 0))
        if luna_dep is None and cumulat > prag:
            luna_dep = luna
    procent = (cumulat / prag * 100).quantize(Decimal("0.1")) if prag else Decimal("0")
    if luna_dep:
        status = "depasit"
    elif cumulat >= prag * PRAG_ATENTIE:
        status = "atentie"
    else:
        status = "sub_prag"
    return {"cumulat": cumulat, "status": status, "luna_depasirii": luna_dep,
            "procent": procent, "prag": prag}
