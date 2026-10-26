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
from core.common import nomenclator_cerut

B = Decimal("0.01")
#: [lotul 13, deficiența 513] „Lipsesc tipurile 1515 (pensii și obligații similare) și 1517 (terminarea contractului de muncă).” —
#: OMFP 1802/2014, planul de conturi, grupa 151 „Provizioane”: 1511 litigii, 1512 garanții acordate clienților, 1513 dezafectare
#: imobilizări corporale și alte acțiuni similare legate de acestea, 1514 restructurare, 1515 pensii și obligații similare, 1516
#: impozite, 1517 terminarea contractului de muncă, 1518 alte provizioane.
PROVIZIOANE = {"litigii": "1511", "garantii": "1512", "dezafectare": "1513",
               "restructurare": "1514", "pensii": "1515", "impozite": "1516", "terminare_cm": "1517", "altele": "1518"}
#: [lotul 13, deficiența 514] conturile de ajustare a stocurilor (grupa 39), din care se alege — nu se scriu
CONTURI_AJUSTARE_STOC = ("391", "392", "393", "394", "395", "396", "397", "398")

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
        raise ValueError("Suma trebuie să fie un număr pozitiv.")
    if actiune == "constituire":
        return {"linii": [("6814", "491", s)]}
    if actiune == "reluare":
        return {"linii": [("491", "7814", s)]}
    raise ValueError(nomenclator_cerut("actiune", "constituire|reluare"))

def nota_provizion(suma, tip="garantii", actiune="constituire"):
    """6812=151x / 151x=7812. Deductibil fiscal doar tip=garantii."""
    s = _d(suma)
    if s <= 0:
        raise ValueError("Suma trebuie să fie un număr pozitiv.")
    if tip not in PROVIZIOANE:
        raise ValueError(nomenclator_cerut("tip", PROVIZIOANE))
    cont = PROVIZIOANE[tip]
    deductibil = (tip == "garantii")
    if actiune == "constituire":
        return {"linii": [("6812", cont, s)], "deductibil": deductibil}
    if actiune == "reluare":
        return {"linii": [(cont, "7812", s)], "deductibil": deductibil}
    raise ValueError(nomenclator_cerut("actiune", "constituire|reluare"))

def nota_ajustare_stoc(suma, cont_ajustare="397", actiune="constituire"):
    """6814=39x / 39x=7814 - nedeductibil fiscal (nu figureaza in art. 26)."""
    s = _d(suma)
    if s <= 0:
        raise ValueError("Suma trebuie să fie un număr pozitiv.")
    if str(cont_ajustare) not in CONTURI_AJUSTARE_STOC:   # [lotul 13, 515] refuzul pe limba contabilului
        raise ValueError("Alege contul de ajustare a stocurilor din grupa 39 (391–398): ajustarea se înregistrează pe contul stocului "
                         "depreciat (de exemplu 397 pentru mărfuri).")
    if actiune == "constituire":
        return {"linii": [("6814", str(cont_ajustare), s)], "deductibil": False}
    if actiune == "reluare":
        return {"linii": [(str(cont_ajustare), "7814", s)], "deductibil": False}
    raise ValueError(nomenclator_cerut("actiune", "constituire|reluare"))


def parti_fiscale(suma, procent_deductibil):
    """[lotul 13, deficiența 512] (deductibil, nedeductibil) dintr-o constituire: „10.000 la 300 de zile = 3.000 deductibil, 7.000
    nedeductibil”. Decimal, ROUND_HALF_UP."""
    s = _d(suma)
    ded = (s * Decimal(str(procent_deductibil)) / 100).quantize(B, rounding=ROUND_HALF_UP)
    return ded, s - ded
