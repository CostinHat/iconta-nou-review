# -*- coding: utf-8 -*-
"""Decontari asociati (455/456/457/463) - motor PUR.
Surse: Legea 31/1990 art. 67 (dividende trimestriale), OMFP 3067/2018
(cont 463, pct. 423^1-423^2 OMFP 1802), impozit dividende 16% pentru
distribuiri incepand cu 01.01.2026 (Legea 141/2025; 10% anterior).
- dividende ANUALE: 1171=457 brut; impozit 457=446; plata net 457=5121;
- dividende INTERIMARE: 463=456 brut; impozit 456=446; plata net 456=5121;
  regularizare dupa aprobarea situatiilor anuale: 1171=457 + 457=463;
  exces (interimar > anual): restituire de la asociat 5121=456;
- imprumut DE LA asociat (4551): primire 5121=4551; restituire 4551=5121;
  dobanda 666=4551 + impozit 10% pe venitul din dobanda PF retinut 4551=446."""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date

B = Decimal("0.01")
COTA_2026 = Decimal("16")
COTA_VECHE = Decimal("10")

def cota_dividend(la_data=None):
    ref = la_data or date.today()
    return COTA_2026 if ref >= date(2026, 1, 1) else COTA_VECHE

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def _imp(brut, cota):
    return (_d(brut) * cota / 100).quantize(B, rounding=ROUND_HALF_UP)

def nota_dividend(brut, la_data=None, interimar=False, cu_plata=True):
    """Repartizare + impozit + (optional) plata. Anual: 1171/457; interimar: 463/456."""
    b = _d(brut)
    if b <= 0:
        raise ValueError("brut invalid")
    cota = cota_dividend(la_data)
    imp = _imp(b, cota)
    net = b - imp
    if interimar:
        linii = [("463", "456", b), ("456", "446", imp)]
        if cu_plata:
            linii.append(("456", "5121", net))
    else:
        linii = [("1171", "457", b), ("457", "446", imp)]
        if cu_plata:
            linii.append(("457", "5121", net))
    return {"linii": linii, "impozit": imp, "net": net, "cota": str(cota)}

def nota_regularizare_interimar(total_interimar, dividend_anual_aprobat):
    """Dupa aprobarea situatiilor anuale: 1171=457 anual + compensare 457=463;
    daca interimar > anual, excesul se restituie: restituire 5121=456."""
    ti, da = _d(total_interimar), _d(dividend_anual_aprobat)
    if ti <= 0 or da < 0:
        raise ValueError("valori invalide")
    linii = [("1171", "457", da)] if da > 0 else []
    compensat = min(ti, da)
    if compensat > 0:
        linii.append(("457", "463", compensat))
    exces = ti - da
    if exces > 0:
        linii.append(("5121", "456", exces))  # restituire de la asociat (60 zile)
    return {"linii": linii, "compensat": compensat,
            "exces_de_restituit": exces if exces > 0 else Decimal("0.00")}

def nota_imprumut_asociat(suma, operatie="primire", dobanda=0,
                          impozit_dobanda_pct=10):
    """4551: primire 5121=4551; restituire 4551=5121 (+ dobanda 666=4551,
    impozit retinut 4551=446)."""
    s = _d(suma)
    if s < 0 or (s == 0 and not dobanda):
        raise ValueError("suma invalida")
    if operatie == "primire":
        return {"linii": [("5121", "4551", s)]}
    if operatie == "restituire":
        linii = []
        if s > 0:
            linii.append(("4551", "5121", s))
        d = _d(dobanda)
        if d > 0:
            imp = _imp(d, Decimal(str(impozit_dobanda_pct)))
            linii.append(("666", "4551", d))
            if imp > 0:
                linii.append(("4551", "446", imp))
            linii.append(("4551", "5121", d - imp))
        return {"linii": linii}
    raise ValueError("operatie: primire|restituire")
