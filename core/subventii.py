# -*- coding: utf-8 -*-
"""Subventii (445/741/4751/7584) - motor PUR (OMFP 1802/2014 pct. 392-402).
- subventii de EXPLOATARE (inclusiv fonduri UE pt. cheltuieli curente):
  dreptul de incasare 445 = 741 (analitic 7411-7419 dupa natura);
  incasare 5121 = 445; se recunosc pe perioada cheltuielilor compensate;
- subventii pentru INVESTITII (inclusiv fonduri UE pt. active):
  dreptul 445 = 4751; incasare 5121 = 445; reluare la venituri PE MASURA
  AMORTIZARII activului finantat: 4751 = 7584 (proportional cu partea
  subventionata); la cedarea activului, soldul ramas se reia integral;
- restituire subventie: exploatare 741/658 = 5121 (dupa caz),
  investitii 4751 = 5121 pentru partea nerestituita inca la venituri."""
from decimal import Decimal, ROUND_HALF_UP
from core.common import nomenclator_cerut

B = Decimal("0.01")

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def nota_subventie_exploatare(suma, moment="drept", cont_venit="741"):
    """drept: 445=741; incasare: 5121=445."""
    s = _d(suma)
    if s <= 0:
        raise ValueError("Suma trebuie să fie un număr pozitiv.")
    if moment == "drept":
        return {"linii": [("445", str(cont_venit), s)]}
    if moment == "incasare":
        return {"linii": [("5121", "445", s)]}
    raise ValueError(nomenclator_cerut("moment", "drept|incasare"))

def nota_subventie_investitii(suma, moment="drept"):
    """drept: 445=4751; incasare: 5121=445."""
    s = _d(suma)
    if s <= 0:
        raise ValueError("Suma trebuie să fie un număr pozitiv.")
    if moment == "drept":
        return {"linii": [("445", "4751", s)]}
    if moment == "incasare":
        return {"linii": [("5121", "445", s)]}
    raise ValueError(nomenclator_cerut("moment", "drept|incasare"))

def reluare_lunara_investitii(valoare_activ, subventie, amortizare_lunara):
    """4751 = 7584 proportional: amortizare x (subventie / valoare activ)."""
    va, sb, am = _d(valoare_activ), _d(subventie), _d(amortizare_lunara)
    if va <= 0 or sb <= 0 or am <= 0 or sb > va:
        raise ValueError("valori invalide (subventia nu poate depasi valoarea)")
    cota = (am * sb / va).quantize(B, rounding=ROUND_HALF_UP)
    return {"linii": [("4751", "7584", cota)], "reluare": cota,
            "procent_subventionat": str((sb / va * 100).quantize(Decimal("0.01")))}
