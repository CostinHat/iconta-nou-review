# -*- coding: utf-8 -*-
"""Leasing financiar si operational - motor PUR (OMFP 1802/2014 pct. 212-217).
FINANCIAR (locatar): primire 2133=167 (avans+rate capital+reziduala, curs la
data finantarii, pct. 321) + dobanda totala extracontabil DEBIT 8051 (pct. 215);
rata: %=404 (167 capital + 666 dobanda + 628 comision) + 4426, concomitent
CREDIT 8051 cu dobanda facturata; reziduala: 167=404 (inchide 167);
reevaluare lunara sold 167 la BNR (665/765). Amortizare normala la locatar.
OPERATIONAL: rata = chirie 612=401 + 4426; bunul ramane la locator."""
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def nota_primire_financiar(valoare_capital, dobanda_totala, cont_imobilizare="2133"):
    """Primire bun: 2133=167 capital total + D8051 dobanda totala (extracontabil)."""
    vc, dt = _d(valoare_capital), _d(dobanda_totala)
    if vc <= 0 or dt < 0:
        raise ValueError("valori invalide")
    linii = [(cont_imobilizare, "167", vc)]
    if dt > 0:
        linii.append(("8051", "891", dt))  # debit extracontabil prin 891
    return {"linii": linii, "capital": vc, "dobanda_totala": dt}

def nota_rata_financiar(capital, dobanda=0, comision=0, cota_tva=21,
                        tva_pe=("dobanda", "comision")):
    """Rata: %=404: 167 capital + 666 dobanda + 628 comision + 4426.
    TVA pe intreaga factura (capital+dobanda+comision) - practica curenta a
    finantatorilor RO. Concomitent C8051 cu dobanda facturata."""
    c, d, co = _d(capital), _d(dobanda), _d(comision)
    if c < 0 or d < 0 or co < 0 or (c + d + co) <= 0:
        raise ValueError("valori invalide")
    baza = c + d + co
    tva = (baza * Decimal(str(cota_tva)) / 100).quantize(B, rounding=ROUND_HALF_UP)
    linii = []
    if c > 0:
        linii.append(("167", "404", c))
    if d > 0:
        linii.append(("666", "404", d))
    if co > 0:
        linii.append(("628", "404", co))
    linii.append(("4426", "404", tva))
    if d > 0:
        linii.append(("891", "8051", d))  # credit extracontabil
    return {"linii": linii, "baza": baza, "tva": tva}

def nota_reziduala(valoare_reziduala, cota_tva=21):
    """Valoarea reziduala la finalul contractului: 167=404 + TVA (inchide 167)."""
    vr = _d(valoare_reziduala)
    if vr <= 0:
        raise ValueError("valoare invalida")
    tva = (vr * Decimal(str(cota_tva)) / 100).quantize(B, rounding=ROUND_HALF_UP)
    return {"linii": [("167", "404", vr), ("4426", "404", tva)], "tva": tva}

def nota_rata_operational(chirie, cota_tva=21, cont_cheltuiala="612"):
    """Leasing operational: rata = chirie 612=401 + 4426."""
    ch = _d(chirie)
    if ch <= 0:
        raise ValueError("valoare invalida")
    tva = (ch * Decimal(str(cota_tva)) / 100).quantize(B, rounding=ROUND_HALF_UP)
    return {"linii": [(cont_cheltuiala, "401", ch), ("4426", "401", tva)], "tva": tva}
