# -*- coding: utf-8 -*-
"""[lotul 13, zona firme2] Deficiența 655 în Compensări (clasa „suma cu punct de mii citită ca zecimal”).

Comanda Costin 13.1, verbatim: „655: Sume, tot UI | «1.000» scris în format românesc a fost înregistrat «bază 1,00 lei»: punctul de mii
citit ca zecimal, fără avertisment. De verificat în toată aplicația cum se citesc sumele cu punct de mii.”

Ecranul Compensări trimite suma în forma canonică a câmpului numeric comun („1210.50”, mecanismul zonei DS, `api.campNumericRo`); serverul
(`compensari_api._suma`) primește numai lei și bani cu cel mult două zecimale (punct sau virgulă). CE FACE IMPOSIBIL: o sumă scrisă cu punct
de mii („1.210”) citită tăcut 1,21 lei (`Decimal("1.210") == 1,21` trecea de verificarea zecimalelor); ecranul care citește din nou textul
cu un parsator local (`.replace(",", ".")`, garda `SUMA_CITITA_BRUT` a verificatorului).
TEMEI: N/A — citirea unui număr (CLAUDE.md §9).
"""
import os
from decimal import Decimal

import pytest

from core import compensari_api as ca

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.parametrize("text, suma", [("1210", Decimal("1210")), ("1210.50", Decimal("1210.50")), ("1210,5", Decimal("1210.5")),
                                        (" 605.00 ", Decimal("605.00"))])
def test_suma_canonica_se_citeste(text, suma):
    assert ca._suma(text) == suma


@pytest.mark.parametrize("text", ["1.210", "1.210,50", "1,210.50", "12.345", "abc", "0", "-5", "1.2345"])
def test_suma_cu_punct_de_mii_sau_gresita_se_refuza_numit(text):
    with pytest.raises(ca.RefuzCompensare):
        ca._suma(text)


def test_ecranul_compensarilor_nu_mai_citeste_suma_cu_un_parsator_local():
    js = open(os.path.join(RAD, "static", "js", "ecrane", "compensari_ecran.js"), encoding="utf-8").read()
    assert '.replace(",", ".")' not in js, "Compensări citește din nou suma cu un parsator local („1.210” -> 1,21)"
