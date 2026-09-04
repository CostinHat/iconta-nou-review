# -*- coding: utf-8 -*-
"""Bacsis HoReCa - motor PUR (Legea 376/2022 + art. 115 CF).
CAEN 5610 Restaurante / 5630 Baruri: bacsisul (0-15% sau suma fixa, ales de
client pe nota de plata) se evidentiaza DISTINCT pe bonul fiscal.
Fiscal: NU intra in baza TVA, NU se datoreaza CAS/CASS, NU se recalifica
salarial; impozit pe venit 10% (venit din alte surse) retinut la sursa la
distribuire, plata pana pe 25 a lunii urmatoare (D100), informativ D205.
Monografie (Bența): incasare 461 = 462 (bacsis de distribuit salariatilor);
5121/5311 = 461; impozit 462 = 446; plata net 462 = 5121/5311."""
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")
COTA_IMPOZIT = Decimal("10")

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def nota_incasare(bacsis, sursa="card"):
    """La bonul fiscal: 461=462 + incasare 5121 (card) / 5311 (numerar) = 461."""
    b = _d(bacsis)
    if b <= 0:
        # [R147] „bacsis invalid" nu spunea nici care câmp, nici ce e greșit cu el.
        raise ValueError("Bacșișul încasat trebuie să fie o sumă mai mare decât zero. "
                         "Dacă nu s-a încasat bacșiș, operațiunea nu se înregistrează.")
    cont = "5121" if sursa == "card" else "5311"
    return {"linii": [("461", "462", b), (cont, "461", b)]}

def nota_distribuire(bacsis_brut, sursa="banca"):
    """Retinere impozit 10% (462=446) + plata net catre salariati (462=5121/5311)."""
    b = _d(bacsis_brut)
    if b <= 0:
        # [R147] Aici e bacșișul BRUT, din care se reține impozitul — alt înțeles decât la
        # încasare, deci alt mesaj.
        raise ValueError("Bacșișul brut de distribuit trebuie să fie o sumă mai mare decât "
                         "zero: din el se reține impozitul înainte de plata către salariați.")
    imp = (b * COTA_IMPOZIT / 100).quantize(B, rounding=ROUND_HALF_UP)
    net = b - imp
    cont = "5121" if sursa == "banca" else "5311"
    return {"linii": [("462", "446", imp), ("462", cont, net)],
            "impozit": imp, "net": net}
