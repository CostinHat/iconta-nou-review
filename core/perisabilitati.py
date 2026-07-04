# -*- coding: utf-8 -*-
"""Perisabilitati si scazaminte - motor PUR (HG 831/2004 + art. 25 CF + art. 304 CF).
- limita maxima deductibila = coeficientul grupei (anexe 1-3 HG 831/2004)
  aplicat la PRETUL DE INREGISTRARE al produselor INTRATE;
- conditii: verificare faptica (inventariere/receptie/predare gestiune),
  aproba administratorul, proces-verbal; NU sunt perisabilitati: consum
  tehnologic, neglijenta, sustrageri, forta majora;
- IN limita: 607/60x = 3xx deductibil, FARA ajustare TVA;
- PESTE limita: 607 nedeductibil + AJUSTARE TVA dedusa (635 = 4426) pe
  partea de depasire (art. 304 CF); exceptie fara ajustare: degradare
  calitativa dovedita + dovada distrugerii."""
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def calcul(valoare_intrari, procent_limita, pierdere_constatata,
           cota_tva=21, cont_stoc="371", degradare_dovedita_distrusa=False):
    """Returneaza limita, partea deductibila/nedeductibila, liniile notei."""
    vi, pl, pc = _d(valoare_intrari), Decimal(str(procent_limita)), _d(pierdere_constatata)
    if vi <= 0 or pl < 0 or pc <= 0:
        raise ValueError("valori invalide")
    limita = (vi * pl / 100).quantize(B, rounding=ROUND_HALF_UP)
    deductibil = min(pc, limita)
    nedeductibil = pc - deductibil
    linii = []
    if deductibil > 0:
        linii.append(("607", cont_stoc, deductibil))
    if nedeductibil > 0:
        linii.append(("607", cont_stoc, nedeductibil))  # analitic nedeductibil
    ajustare_tva = Decimal("0.00")
    if nedeductibil > 0 and not degradare_dovedita_distrusa:
        ajustare_tva = (nedeductibil * Decimal(str(cota_tva)) / 100)\
            .quantize(B, rounding=ROUND_HALF_UP)
        if ajustare_tva > 0:
            linii.append(("635", "4426", ajustare_tva))
    return {"limita": limita, "deductibil": deductibil,
            "nedeductibil": nedeductibil, "ajustare_tva": ajustare_tva,
            "linii": linii}
