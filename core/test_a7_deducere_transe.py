# -*- coding: utf-8 -*-
"""[A7, 17.09.2026] Deducerea personală: tranșele de 50 lei se rotunjesc ÎN SUS (ceil), nu în jos.

Constatarea A7: `salarizare.py` folosea `floor((brut-sm)/50)`. Art. 77 alin.(4) CF: tranșa
„sm+1 … sm+50" e PRIMA treaptă de reducere (deducerea scade cu 0,5 p.p. la fiecare 50 lei sau
fracție). Cu floor, un brut de sm+1 primea încă deducerea integrală (20%) în loc de 19,50%. Greșit
pe 49 din fiecare 50 de valori. PICĂ pe codul de dinainte (865,00 la sm+1), TRECE după (843,38).

sm(08/2026) = 4.325 (HG 146/2026). Deducerea de bază pentru 0 persoane pornește de la 20%.
"""
import datetime

from core import salarizare

_LA = datetime.date(2026, 8, 1)


def _baza(brut):
    return float(salarizare.deducere_personala(brut, persoane=0, la_data=_LA)["baza"])


def test_sm_plus_1_e_prima_treapta_19_50():
    # 4326 = sm+1: prima treaptă -> 19,50% x 4325 = 843,375 -> 843,38 (NU 20% = 865,00)
    assert _baza(4326) == 843.38, "deducere(sm+1)=%r (așteptat 843,38 = 19,50%%)" % _baza(4326)


def test_sm_plus_50_tot_prima_treapta():
    # 4375 = sm+50: tot prima treaptă -> 19,50%
    assert _baza(4375) == 843.38, "deducere(sm+50)=%r (așteptat 843,38 = 19,50%%)" % _baza(4375)


def test_sm_plus_51_a_doua_treapta_19_00():
    # 4376 = sm+51: a doua treaptă -> 19,00% x 4325 = 821,75
    assert _baza(4376) == 821.75, "deducere(sm+51)=%r (așteptat 821,75 = 19,00%%)" % _baza(4376)


def test_sm_exact_deducere_integrala():
    # la sm exact (4325), fără reducere de treaptă -> 20% x 4325 = 865,00
    assert _baza(4325) == 865.00, "deducere(sm)=%r (așteptat 865,00 = 20%%)" % _baza(4325)
