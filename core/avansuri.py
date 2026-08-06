# -*- coding: utf-8 -*-
"""Avansuri furnizori/clienti (409/419) si regularizare - motor PUR.
OMFP 1802/2014 + art. 282 al. 2 lit. b CF (TVA exigibila la incasarea avansului).
- avans PLATIT furnizor (factura de avans): % = 401: 409x + 4426; plata 401=5121;
  409x dupa destinatie: 4091 stocuri, 4092 servicii, 4093 imobilizari corporale,
  4094 imobilizari necorporale;
- regularizare la factura finala: inversare avans (401 = 409x, 401 = 4426) +
  inregistrarea facturii finale intregi separat;
- avans INCASAT de la client (factura de avans): 4111 = % (419 + 4427);
  incasare 5121=4111; regularizare: inversare (419 = 4111, 4427 = 4111)."""
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")
CONT_AVANS = {"stocuri": "4091", "servicii": "4092",
              "imobilizari": "4093", "imobilizari_necorporale": "4094"}

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def _tva(baza, cota):
    return (_d(baza) * Decimal(str(cota)) / 100).quantize(B, rounding=ROUND_HALF_UP)

def nota_avans_platit(suma_fara_tva, cota=21, destinatie="stocuri"):
    """Factura de avans primita de la furnizor: 409x + 4426 = 401."""
    s = _d(suma_fara_tva)
    if s <= 0:
        raise ValueError("Suma trebuie să fie un număr pozitiv.")
    if destinatie not in CONT_AVANS:
        raise ValueError("destinatie: " + "|".join(CONT_AVANS))
    tva = _tva(s, cota)
    linii = [(CONT_AVANS[destinatie], "401", s)]
    if tva > 0:
        linii.append(("4426", "401", tva))
    return {"linii": linii, "tva": tva, "cont_avans": CONT_AVANS[destinatie]}

def nota_regularizare_avans_platit(suma_fara_tva, cota=21, destinatie="stocuri"):
    """La factura finala: inversarea avansului (401 = 409x, 401 = 4426).
    Factura finala se inregistreaza separat, intreaga."""
    s = _d(suma_fara_tva)
    if s <= 0:
        raise ValueError("Suma trebuie să fie un număr pozitiv.")
    if destinatie not in CONT_AVANS:
        raise ValueError("destinatie: " + "|".join(CONT_AVANS))
    tva = _tva(s, cota)
    linii = [("401", CONT_AVANS[destinatie], s)]
    if tva > 0:
        linii.append(("401", "4426", tva))
    return {"linii": linii, "tva": tva}

def nota_avans_incasat(suma_fara_tva, cota=21):
    """Factura de avans emisa catre client: 4111 = % (419 + 4427)."""
    s = _d(suma_fara_tva)
    if s <= 0:
        raise ValueError("Suma trebuie să fie un număr pozitiv.")
    tva = _tva(s, cota)
    linii = [("4111", "419", s)]
    if tva > 0:
        linii.append(("4111", "4427", tva))
    return {"linii": linii, "tva": tva}

def nota_regularizare_avans_incasat(suma_fara_tva, cota=21):
    """La factura finala: inversarea avansului (419 = 4111, 4427 = 4111)."""
    s = _d(suma_fara_tva)
    if s <= 0:
        raise ValueError("Suma trebuie să fie un număr pozitiv.")
    tva = _tva(s, cota)
    linii = [("419", "4111", s)]
    if tva > 0:
        linii.append(("4427", "4111", tva))
    return {"linii": linii, "tva": tva}
