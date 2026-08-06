# -*- coding: utf-8 -*-
"""Productie in curs si produse finite - motor PUR (OMFP 1802/2014, metoda
inventarului permanent, cost standard cu diferente pe 348).
- obtinere produse finite: 345 = 711 la cost standard;
- diferente de pret la obtinere (cost efectiv vs standard): nefavorabile
  (efectiv > standard) 348 = 711; favorabile 711 = 348 (sau 348 in rosu);
- productie in curs: constatare la sfarsit de luna 331 = 711;
  reluare la inceputul lunii urmatoare 711 = 331;
- vanzare: 4111 = 701 + 4427 (separat) si descarcarea gestiunii 711 = 345
  la cost standard + repartizarea diferentelor: coeficient 348 aplicat la
  iesiri -> 711 = 348 (nefavorabile) / 348 = 711 (favorabile)."""
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def nota_obtinere(cost_standard, cost_efectiv=None):
    """345=711 la standard + diferente pe 348."""
    cs = _d(cost_standard)
    if cs <= 0:
        raise ValueError("Costul standard trebuie să fie un număr pozitiv.")
    linii = [("345", "711", cs)]
    dif = None
    if cost_efectiv is not None:
        ce = _d(cost_efectiv)
        if ce <= 0:
            raise ValueError("cost efectiv invalid")
        d = ce - cs
        if d > 0:
            linii.append(("348", "711", d))
            dif = {"sens": "nefavorabila", "suma": d}
        elif d < 0:
            linii.append(("711", "348", -d))
            dif = {"sens": "favorabila", "suma": -d}
    return {"linii": linii, "diferenta": dif}

def nota_productie_in_curs(suma, moment="constatare"):
    """constatare (sfarsit luna): 331=711; reluare (inceput luna): 711=331."""
    s = _d(suma)
    if s <= 0:
        raise ValueError("Suma trebuie să fie un număr pozitiv.")
    if moment == "constatare":
        return {"linii": [("331", "711", s)]}
    if moment == "reluare":
        return {"linii": [("711", "331", s)]}
    raise ValueError("moment: constatare|reluare")

def coeficient_348(sold_initial_348, rulaj_348, sold_initial_345, intrari_345):
    """K = (Si348 + Rulaj348) / (Si345 + Intrari345). Semnul lui 348 se
    pastreaza (debitor=nefavorabil pozitiv, creditor=favorabil negativ)."""
    numarator = _d(sold_initial_348) + _d(rulaj_348)
    numitor = _d(sold_initial_345) + _d(intrari_345)
    if numitor <= 0:
        raise ValueError("baza 345 invalida")
    return (numarator / numitor).quantize(Decimal("0.000001"))

def nota_vanzare(pret_vanzare, cost_standard_iesit, cota_tva=21, coef_348=None):
    """4111 = 701 + 4427; descarcare 711=345 standard + diferente aferente."""
    pv, cs = _d(pret_vanzare), _d(cost_standard_iesit)
    if pv <= 0 or cs <= 0:
        raise ValueError("Una sau mai multe valori sunt invalide. Verifică sumele și cantitățile introduse.")
    tva = (pv * Decimal(str(cota_tva)) / 100).quantize(B, rounding=ROUND_HALF_UP)
    linii = [("4111", "701", pv)]
    if tva > 0:
        linii.append(("4111", "4427", tva))
    linii.append(("711", "345", cs))
    dif = None
    if coef_348:
        d = (cs * Decimal(str(coef_348))).quantize(B, rounding=ROUND_HALF_UP)
        if d > 0:
            linii.append(("711", "348", d))
            dif = {"sens": "nefavorabila", "suma": d}
        elif d < 0:
            linii.append(("348", "711", -d))
            dif = {"sens": "favorabila", "suma": -d}
    return {"linii": linii, "tva": tva, "diferenta_repartizata": dif}
