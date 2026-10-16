# -*- coding: utf-8 -*-
"""Alerta de load (comanda Costin 15.10.2026 noaptea, „Lotul 5 — comanda 3” pct.6b, verbatim în DECIZII): „Alerta de load pleacă doar
dacă media pe 15 minute depășește un prag calculat pe numărul de procesoare și rămâne așa; nu pleacă în timpul rulărilor tale de teste.”
Pe decizia pură `core.alerta_load.de_alertat` (istoricul buclei de sănătate, un rând la 5 minute) + legătura ei în `main.py`.
MUTAȚII: pragul `0.7 × procesoare` -> pică testul pragului; condiția „rămâne așa” scoasă (un singur rând ajunge) -> pică testul vârfului;
rândurile cu teste ignorate -> pică testele rulărilor; vechea regulă pe `load1` pusă înapoi în `main.py` -> pică testul legăturii."""
import datetime
import os

from core import alerta_load as al

T0 = datetime.datetime(2026, 10, 15, 20, 0)
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _ist(valori, teste=()):
    """Un rând la 5 minute, ultimul la T0; `teste` = indicii rândurilor cu o rulare de teste."""
    n = len(valori)
    return [(T0 - datetime.timedelta(minutes=5 * (n - 1 - i)), v, i in teste) for i, v in enumerate(valori)]


def test_pragul_e_numarul_de_procesoare():
    assert (al.prag(2), al.prag(8), al.prag(None)) == (2.0, 8.0, 1.0)
    assert al.de_alertat(_ist([1.9] * 7), 2, T0)[0] is False          # sub 2 procesoare ocupate: nimic (vechiul prag era 1,4)
    assert al.de_alertat(_ist([2.0] * 7), 2, T0)[0] is True


def test_un_varf_nu_e_o_alerta_trebuie_sa_ramana():
    assert al.de_alertat(_ist([0.5] * 6 + [3.5]), 2, T0)[0] is False
    assert al.de_alertat(_ist([0.5, 0.5, 0.5, 0.5, 3.0, 3.1, 3.2]), 2, T0)[0] is True    # 15 minute la rând peste prag
    assert al.de_alertat(_ist([3.0, 3.1]), 2, T0) == (False, "istoric prea scurt (2 rânduri în 15 minute)")


def test_nu_pleaca_in_timpul_unei_rulari_de_teste():
    alerta, motiv = al.de_alertat(_ist([3.0] * 7, teste={6}), 2, T0)
    assert (alerta, motiv) == (False, "rulare de teste în ultimele 30 de minute")


def test_nu_pleaca_nici_imediat_dupa_rulare_media_o_mai_contine():
    assert al.de_alertat(_ist([3.0] * 7, teste={2}), 2, T0)[0] is False      # rularea s-a terminat acum 20 de minute
    assert al.de_alertat(_ist([3.0] * 8, teste={0}), 2, T0)[0] is True       # acum 35 de minute: în afara ferestrei


def test_main_alerteaza_load_numai_prin_decizia_din_istoric():
    src = open(os.path.join(RAD, "main.py"), encoding="utf-8").read()
    corp = src[src.index("def _verifica_si_alerta"):src.index("def _ciclu_sanatate")]
    assert corp.count("_alerta_load.de_alertat(") == 1 and corp.count('m["load1"]') == 0, "alerta de load ocolește decizia"
