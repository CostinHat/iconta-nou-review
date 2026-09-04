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
    return {"pret": p.quantize(B), "compensatie": c, "total": (p + c).quantize(B)}

def achizitie_de_la_agricultor(valoare, in_registru, procent=8):
    """Achizitie de la agricultor cu regim special. Compensatia e deductibila
    (alin. 17) doar daca agricultorul e in Registrul ANAF la data livrarii."""
    if not in_registru:
        raise ValueError("agricultor neinscris in Registrul agricultorilor la data "
                         "livrarii - compensatia NU este deductibila (art. 315^1 al. 17, norme)")
    return compensatie(valoare, procent)
