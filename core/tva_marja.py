# -*- coding: utf-8 -*-
"""Regim special marja (art. 312 CF, norme pct. 86) - motor PUR.
Marja = pret vanzare - pret cumparare; TVA = marja x cota/(100+cota) (suta marita);
marja negativa -> TVA 0 (se reporteaza in jurnalul special). Pe factura NU se
inscrie TVA distinct; mentiune "regimul marjei - bunuri second-hand"."""
from decimal import Decimal, ROUND_HALF_UP

def vanzare_marja(pret_vanzare, pret_cumparare, cota=21):
    pv = Decimal(str(pret_vanzare))
    pc = Decimal(str(pret_cumparare))
    c = Decimal(str(cota))
    if pv <= 0 or pc < 0:
        raise ValueError("preturi invalide")
    marja = pv - pc
    if marja <= 0:
        return {"marja_bruta": marja.quantize(Decimal("0.01")), "tva": Decimal("0.00"),
                "marja_neta": marja.quantize(Decimal("0.01")),
                "nota": "marja negativa/zero - fara TVA, se reporteaza in jurnalul special"}
    tva = (marja * c / (100 + c)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {"marja_bruta": marja.quantize(Decimal("0.01")), "tva": tva,
            "marja_neta": (marja - tva).quantize(Decimal("0.01")), "nota": None}
