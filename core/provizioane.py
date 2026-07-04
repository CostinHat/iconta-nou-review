# -*- coding: utf-8 -*-
"""Provizioane si ajustari de valoare - motor PUR.
OMFP 1802/2014 sect. 4.10 + art. 26 Cod fiscal:
- ajustari creante clienti: constituire 6814=491, reluare 491=7814;
  deductibilitate art. 26: lit. c) 30% daca >270 zile de la scadenta,
  negarantata, neafiliata; lit. j) 100% daca faliment declarat (PJ, hotarare)
  sau insolventa PF; altfel 0%;
- provizioane (151x): constituire 6812=151x, reluare 151x=7812;
  deductibil DOAR 1512 garantii de buna executie (art. 26(1)b), restul
  (1511 litigii, 1513 dezafectare, 1514 restructurare, 1518 altele) nedeductibile;
- ajustari stocuri: 6814=39x, reluare 39x=7814 - nedeductibile fiscal."""
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")
PROVIZIOANE = {"litigii": "1511", "garantii": "1512", "dezafectare": "1513",
               "restructurare": "1514", "impozite": "1516", "altele": "1518"}

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def deductibilitate_creanta(zile_depasire_scadenta, garantata, afiliata,
                            faliment_declarat=False):
    """Procent deductibil (art. 26 lit. c/j) + temeiul."""
    if garantata:
        return 0, "creanta garantata de alta persoana - nedeductibil (art. 26)"
    if afiliata:
        return 0, "creanta la persoana afiliata - nedeductibil (art. 26)"
    if faliment_declarat:
        return 100, "faliment declarat prin hotarare / insolventa PF - 100% (art. 26(1)j)"
    if zile_depasire_scadenta > 270:
        return 30, "neincasata >270 zile de la scadenta - 30% (art. 26(1)c)"
    return 0, "sub 270 zile de la scadenta - nedeductibil inca (art. 26(1)c)"

def nota_ajustare_creanta(suma, actiune="constituire"):
    """6814=491 / 491=7814."""
    s = _d(suma)
    if s <= 0:
        raise ValueError("suma invalida")
    if actiune == "constituire":
        return {"linii": [("6814", "491", s)]}
    if actiune == "reluare":
        return {"linii": [("491", "7814", s)]}
    raise ValueError("actiune: constituire|reluare")

def nota_provizion(suma, tip="garantii", actiune="constituire"):
    """6812=151x / 151x=7812. Deductibil fiscal doar tip=garantii."""
    s = _d(suma)
    if s <= 0:
        raise ValueError("suma invalida")
    if tip not in PROVIZIOANE:
        raise ValueError("tip: " + "|".join(PROVIZIOANE))
    cont = PROVIZIOANE[tip]
    deductibil = (tip == "garantii")
    if actiune == "constituire":
        return {"linii": [("6812", cont, s)], "deductibil": deductibil}
    if actiune == "reluare":
        return {"linii": [(cont, "7812", s)], "deductibil": deductibil}
    raise ValueError("actiune: constituire|reluare")

def nota_ajustare_stoc(suma, cont_ajustare="397", actiune="constituire"):
    """6814=39x / 39x=7814 - nedeductibil fiscal (nu figureaza in art. 26)."""
    s = _d(suma)
    if s <= 0:
        raise ValueError("suma invalida")
    if not str(cont_ajustare).startswith("39"):
        raise ValueError("cont ajustare stocuri = grupa 39x")
    if actiune == "constituire":
        return {"linii": [("6814", str(cont_ajustare), s)], "deductibil": False}
    if actiune == "reluare":
        return {"linii": [(str(cont_ajustare), "7814", s)], "deductibil": False}
    raise ValueError("actiune: constituire|reluare")
