# -*- coding: utf-8 -*-
"""Retetar HoReCa - motor PUR.
Reteta = lista (articol, cantitate/portie). Vanzare N portii -> consum ingrediente la CMP.
Food cost % = cost ingrediente la CMP / pret vanzare (fara TVA)."""
from decimal import Decimal, ROUND_HALF_UP

def _d(x):
    return Decimal(str(x or 0))

def consum_pe_portii(linii, portii):
    """linii: [{articol_id, cantitate, cmp}]; intoarce consum per ingredient la CMP.
    ValueError daca portii <= 0."""
    p = _d(portii)
    if p <= 0:
        raise ValueError("numar de portii invalid")
    rez = []
    total = Decimal("0")
    for l in linii:
        cant = (_d(l["cantitate"]) * p).quantize(Decimal("0.001"))
        val = (cant * _d(l.get("cmp"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total += val
        rez.append({"articol_id": l["articol_id"], "cantitate": cant, "valoare": val})
    return {"linii": rez, "cost_total": total.quantize(Decimal("0.01"))}

def food_cost(linii, pret_vanzare_fara_tva):
    """Food cost % pe O portie, la CMP curent. None daca pretul e 0."""
    cost = sum((_d(l["cantitate"]) * _d(l.get("cmp")) for l in linii), Decimal("0"))
    pret = _d(pret_vanzare_fara_tva)
    if pret <= 0:
        return {"cost_portie": cost.quantize(Decimal("0.01")), "food_cost_pct": None}
    pct = (cost / pret * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return {"cost_portie": cost.quantize(Decimal("0.01")), "food_cost_pct": pct}
