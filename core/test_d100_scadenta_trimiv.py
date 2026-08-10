# -*- coding: utf-8 -*-
"""Gard scadenta trim IV D100 (sursa: anaf_surse/d100_struct_anaf.txt + validator DUK R15.1).

- cod 121 (micro), trim IV (luna=12): scadenta = 25.06.an+1 (validatorul v9 respinge 25.01.an+1
  cu R15.1 scadenta ar fi trebuit sa fie 25.06.AAAA pt cod obligatie=121 - dovedit pe date populate).
- cod 103 (impozit profit), luna de sfarsit an fiscal (calendaristic=12): 25.LS = 25.12.an
  (struct linia 258-260 + 25LS linia 3286).
- trim I/II/III: 25 a lunii urmatoare (neschimbat).
nr_evid EMBEDA scadenta (poz.12-17 = ZZLLAA) - trebuie sa reflecte aceeasi data.
"""
from core import d100

PROF = {"cui": "302222000", "nume": "X SRL", "adresa": "Str. Test 1"}


def _scad(cod, luna, cota=""):
    o = {"cod_oblig": cod, "suma_dat": 30}
    if cota:
        o["cota"] = cota
    res = d100.calcul_d100(PROF, 2026, luna, [o])
    return res.obligatii[0]


def test_micro_121_trim_IV_scadenta_25_06_an_urmator():
    ob = _scad("121", 12, cota="1")
    assert ob.scadenta == "25.06.2027", ob.scadenta
    # nr_evid poz.12-17 (ZZLLAA) = 250627
    assert ob.nr_evid[11:17] == "250627", ob.nr_evid


def test_profit_103_trim_IV_scadenta_25_LS():
    ob = _scad("103", 12)
    assert ob.scadenta == "25.12.2026", ob.scadenta
    assert ob.nr_evid[11:17] == "251226", ob.nr_evid


def test_trim_III_neschimbat():
    assert _scad("121", 9, cota="1").scadenta == "25.10.2026"
    assert _scad("103", 9).scadenta == "25.10.2026"
