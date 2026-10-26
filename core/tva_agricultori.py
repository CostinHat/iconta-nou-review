# -*- coding: utf-8 -*-
"""Regim special agricultori (art. 315^1 CF) - motor PUR.
- alin. 2: procent compensare forfetara 8% (din 2019, neschimbat de Legea 141/2025);
- compensatia = procent x pret/tarif EXCLUSIV taxa (alin. 1 lit. h);
- agricultorul nu colecteaza TVA, nu deduce (alin. 4);
- cumparatorul PJ deduce compensatia ca TVA (alin. 17) DOAR daca agricultorul
  figureaza in Registrul agricultorilor la data livrarii (norme);
- evidenta separata achizitii la cumparator (alin. 5)."""
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")

def compensatie(pret_fara_taxa, procent=8):
    """Compensatia forfetara = procent x pret exclusiv taxa."""
    p = Decimal(str(pret_fara_taxa))
    pr = Decimal(str(procent))
    if p <= 0 or pr < 0:
        raise ValueError("Prețul achiziției și procentul de compensare trebuie să fie numere "
                         "pozitive — o achiziție consemnează o operațiune efectuată.")
    c = (p * pr / 100).quantize(B, rounding=ROUND_HALF_UP)
    return {"pret": p.quantize(B, rounding=ROUND_HALF_UP), "compensatie": c, "total": (p + c).quantize(B, rounding=ROUND_HALF_UP)}

def achizitie_de_la_agricultor(valoare, in_registru, procent=8):
    """Achizitie de la agricultor cu regim special. Compensatia se plateste si se deduce
    (alin. 17) doar daca agricultorul e in Registrul ANAF la data livrarii.
    [lotul 13, deficiența 549] „Cu agricultorul neînscris în registru, aplicația refuză toată achiziția; cumpărarea e legală, doar compensația
    nu se deduce. Corect: 301 = 401 10.000 fără 4426, cu mențiunea că nu se aplică compensația.” -> neînscris: compensația 0 + mențiunea."""
    if not in_registru:
        p = Decimal(str(valoare))
        if p <= 0:
            raise ValueError("Prețul achiziției trebuie să fie un număr pozitiv — o achiziție consemnează o operațiune efectuată.")
        p = p.quantize(B, rounding=ROUND_HALF_UP)
        return {"pret": p, "compensatie": Decimal("0.00"), "total": p,
                "mentiune": "agricultor neînscris în Registrul agricultorilor la data livrării: fără compensație (art. 315^1 alin.(17))"}
    return compensatie(valoare, procent)
