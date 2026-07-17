# -*- coding: utf-8 -*-
"""Teste F135 pontaj — grila lunara (pura). Informativ, foloseste calendarul corectat."""
from datetime import date
from core.pontaj import grila_pura


def _zi(g, nr):
    return next(z for z in g["zile"] if z["zi_nr"] == nr)


def test_weekend_si_sarbatoare_nelucratoare():
    # aprilie 2026: 10 apr (Vinerea Mare) + 13 apr (Paste) = nelucratoare
    g = grila_pura(2026, 4, None, {})
    assert _zi(g, 10)["stare"] == "nelucratoare"   # sarbatoare pe zi de lucru (vineri)
    assert _zi(g, 13)["stare"] == "nelucratoare"   # sarbatoare (luni)
    assert _zi(g, 4)["stare"] == "nelucratoare"    # sambata

def test_prezent_implicit_pe_zi_lucratoare():
    g = grila_pura(2026, 4, None, {})
    assert _zi(g, 7)["stare"] == "prezent"         # marti lucratoare, fara exceptie

def test_exceptie_afisata():
    g = grila_pura(2026, 4, None, {date(2026, 4, 7): "concediu_odihna"})
    assert _zi(g, 7)["stare"] == "concediu_odihna"

def test_inainte_de_angajare():
    # angajat pe 15 apr 2026: zilele 1-14 = inainte_angajare (chiar lucratoare)
    g = grila_pura(2026, 4, date(2026, 4, 15), {})
    assert _zi(g, 7)["stare"] == "inainte_angajare"
    assert _zi(g, 15)["stare"] == "prezent"        # ziua angajarii, lucratoare (miercuri)

def test_rezumat_numara_corect():
    g = grila_pura(2026, 4, None, {date(2026, 4, 7): "absent_nemotivat",
                                   date(2026, 4, 8): "concediu_odihna"})
    # aprilie 2026: 20 zile lucratoare (fara sarbatori); 2 exceptii -> 18 prezent
    assert g["rezumat"]["prezent"] == 18
    assert g["rezumat"]["absent_nemotivat"] == 1
    assert g["rezumat"]["concediu_odihna"] == 1
