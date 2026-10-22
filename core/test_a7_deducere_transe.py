# -*- coding: utf-8 -*-
"""[A7, 17.09.2026] Deducerea personală: tranșele de 50 lei se rotunjesc ÎN SUS (ceil), nu în jos.

Constatarea A7: `salarizare.py` folosea `floor((brut-sm)/50)`. Art. 77 alin.(4) CF: tranșa
„sm+1 … sm+50" e PRIMA treaptă de reducere (deducerea scade cu 0,5 p.p. la fiecare 50 lei sau
fracție). Cu floor, un brut de sm+1 primea încă deducerea integrală (20%) în loc de 19,50%. Greșit
pe 49 din fiecare 50 de valori. PICĂ pe codul de dinainte (865,00 la sm+1), TRECE după (843,38).
[lotul 11, 453] Suma se rotunjește acum la leu (aritmetic, structura D112: câmp calculat cu parametri = întreg prin rotunjire
matematică): 843,375 -> 843; 821,75 -> 822. Treapta rămâne ce verifică testele de mai jos (843 ≠ 865).

sm(08/2026) = 4.325 (HG 146/2026). Deducerea de bază pentru 0 persoane pornește de la 20%.
"""
import datetime

from core import salarizare

_LA = datetime.date(2026, 8, 1)


def _baza(brut):
    return float(salarizare.deducere_personala(brut, persoane=0, la_data=_LA)["baza"])


def test_sm_plus_1_e_prima_treapta_19_50():
    # 4326 = sm+1: prima treaptă -> 19,50% x 4325 = 843,375 -> 843 la leu (NU 20% = 865)
    assert _baza(4326) == 843.0, "deducere(sm+1)=%r (așteptat 843 = 19,50%%, rotunjit la leu)" % _baza(4326)


def test_sm_plus_50_tot_prima_treapta():
    # 4375 = sm+50: tot prima treaptă -> 19,50%
    assert _baza(4375) == 843.0, "deducere(sm+50)=%r (așteptat 843 = 19,50%%, rotunjit la leu)" % _baza(4375)


def test_sm_plus_51_a_doua_treapta_19_00():
    # 4376 = sm+51: a doua treaptă -> 19,00% x 4325 = 821,75 -> 822 la leu
    assert _baza(4376) == 822.0, "deducere(sm+51)=%r (așteptat 822 = 19,00%%, rotunjit la leu)" % _baza(4376)


def test_sm_exact_deducere_integrala():
    # la sm exact (4325), fără reducere de treaptă -> 20% x 4325 = 865,00
    assert _baza(4325) == 865.00, "deducere(sm)=%r (așteptat 865,00 = 20%%)" % _baza(4325)


def test_453_suma_deducerii_se_rotunjeste_la_leu():
    """[deficiența 453, comanda Costin 11.3: „verifică la sursă rotunjirea deducerii personale (fluturașul arată 562,25) și aplic-o în
    calcul, fluturaș și D112”; PIVOT față de 205, care conchisese „nu se rotunjește” citind numai CF art.77]
    Brut 5.000 lei în 10/2026 (salariul minim 4.325 lei), fără persoane în întreținere: 5.000 = salariul minim + 675 lei, treapta
    „salariul minim + 651 lei … + 700 lei” = 13,00% -> 13% × 4.325 = 562,25 lei -> 562 lei. MUTAȚIE: fără rotunjire -> 562,25, pică."""
    import datetime as _d
    from decimal import Decimal as _D
    from core import salarizare as _s
    r = _s.deducere_personala(5000, la_data=_d.date(2026, 10, 1))
    # CF art.77 alin.(4): procentul din tabel („salariul minim + 651 lei / salariul minim + 700 lei … 13,00%”) — legea nu spune cum se
    # rotunjește suma; structura D112 (anaf_surse/d112_struct_anaf.txt, antet): „Campurile calculate cu ajutorul parametrilor vor avea
    # valori intregi, pozitive obtinute prin rotunjire matematica” -> 562,25 -> 562 (aritmetic: partea zecimală 0,25 < 0,5)
    assert r["baza"] == _D("562.00") and r["total"] == _D("562.00"), r
    # aritmetic, nu în jos: 778,50 (18,00% × 4.325, brut 4.500) -> 779 (partea zecimală 0,50 >= 0,5 -> +1)
    assert _s.deducere_personala(4500, la_data=_d.date(2026, 10, 1))["baza"] == _D("779.00")
    # suplimentara tinerilor (CF art.77 alin.(10) lit.a: 15% × 4.325 = 648,75) -> 649, componentă rotunjită separat (E3_1221)
    r = _s.deducere_personala(4325, sub_26=True, la_data=_d.date(2026, 10, 1))
    assert (r["baza"], r["tineri"], r["total"]) == (_D("865.00"), _D("649.00"), _D("1514.00")), r
