# -*- coding: utf-8 -*-
"""Teste calendar sarbatori + zile lucratoare (OUG 158/2005 art.10, Legea 220/2016).

Bug reparat 17.07.2026: proratarea CM folosea weekday<5 (ignora sarbatorile legale) in
4 locuri (stat_plata x2, main.py, d112) + tabele hardcodate _D112_NZL (a doua sursa de
adevar). Sursa unica acum: scadente.zile_lucratoare_luna, cu Pastele ORTODOX calculat
(Meeus), nu hardcodat. Oracolul de mai jos = fostele tabele _D112_NZL (erau corecte).
"""
import pytest
from datetime import date
from core.scadente import paste_ortodox, sarbatori_legale, zile_lucratoare_luna, e_zi_lucratoare

# Fostele tabele hardcodate _D112_NZL (oracol de regresie - erau corecte, verificate ANAF)
NZL_2026 = {1: 18, 2: 20, 3: 22, 4: 20, 5: 20, 6: 21, 7: 23, 8: 21, 9: 22, 10: 22, 11: 20, 12: 21}
NZL_2025 = {1: 18, 2: 20, 3: 21, 4: 20, 5: 21, 6: 20, 7: 23, 8: 20, 9: 22, 10: 23, 11: 20, 12: 20}


def test_paste_ortodox():
    assert (paste_ortodox(2025).month, paste_ortodox(2025).day) == (4, 20)
    assert (paste_ortodox(2026).month, paste_ortodox(2026).day) == (4, 12)
    assert (paste_ortodox(2027).month, paste_ortodox(2027).day) == (5, 2)


def test_zile_lucratoare_luna_match_oracol_2026():
    for m in range(1, 13):
        assert zile_lucratoare_luna(2026, m) == NZL_2026[m], m


def test_zile_lucratoare_luna_match_oracol_2025():
    for m in range(1, 13):
        assert zile_lucratoare_luna(2025, m) == NZL_2025[m], m


def test_vinerea_mare_e_sarbatoare():
    # Vinerea Mare (Paste-2) trebuie sa fie sarbatoare - lipsea din calendarul vechi 2026
    assert (4, 10) in sarbatori_legale(2026)      # 10.04.2026
    assert not e_zi_lucratoare(date(2026, 4, 10))
    assert (4, 30) in sarbatori_legale(2027)      # 30.04.2027 (Paste 02.05)


def test_rusalii_si_paste():
    s = sarbatori_legale(2026)
    assert (4, 12) in s and (4, 13) in s          # Paste duminica + luni
    assert (5, 31) in s and (6, 1) in s           # Rusalii 2026


def test_garda_an_neacoperit_esueaza_zgomotos():
    # cazul 2025 (lipsea) nu trebuie sa mai treaca TACUT - trebuie eroare vizibila
    with pytest.raises(ValueError):
        sarbatori_legale(2023)
    with pytest.raises(ValueError):
        zile_lucratoare_luna(2100, 1)


def test_proratare_cm_luna_cu_sarbatoare():
    # Regresie fiscala: aprilie 2026 are 2 sarbatori pe zi lucratoare (10 + 13 apr).
    # Vechi (weekday<5): 22 zile. Corect (fara sarbatori): 20 zile.
    import calendar
    vechi = sum(1 for z in range(1, 31) if date(2026, 4, z).weekday() < 5)
    assert vechi == 22                            # ce dadea codul buggy
    assert zile_lucratoare_luna(2026, 4) == 20    # ce da acum, corect
    # proratare brut 5000, CM 5 zile: se schimba salariul platit
    brut, cm = 5000, 5
    vechi_brut = brut * (vechi - cm) / vechi          # 5000*17/22 = 3863.64
    nou_brut = brut * (zile_lucratoare_luna(2026, 4) - cm) / zile_lucratoare_luna(2026, 4)  # 5000*15/20 = 3750
    assert round(vechi_brut, 2) == 3863.64
    assert round(nou_brut, 2) == 3750.0           # diferenta reala: 113.64 lei/luna
