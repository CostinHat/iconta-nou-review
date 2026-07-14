# -*- coding: utf-8 -*-
"""Test gardian parser MT940 (SWIFT Statement Message).
Format standard :61: (tranzactie) + :86: (detalii). Verificat contra spec SWIFT.
"""
from core.banca_parser import parse_extras

MT940 = b''':20:EXTRAS001
:25:RO49AAAA1B31007593840000
:60F:C260701RON1000,00
:61:2607010701C1210,00NTRFNONREF
:86:Incasare factura DANTE INTERNATIONAL SRL
:61:2607020702D605,50NTRFNONREF
:86:Plata furnizor ENGIE ROMANIA
:61:2607030703C250,00NTRFNONREF
:86:Comision administrare cont
:62F:C260731RON1854,50
'''


def test_mt940_detectat_si_parsat():
    tz = parse_extras(MT940, "extras.sta")
    assert len(tz) == 3


def test_mt940_semne_corecte():
    tz = parse_extras(MT940, "extras.sta")
    assert tz[0]["suma"] == 1210.0    # C = incasare
    assert tz[1]["suma"] == -605.5    # D = plata
    assert tz[2]["suma"] == 250.0


def test_mt940_data_convertita():
    tz = parse_extras(MT940, "extras.sta")
    assert tz[0]["data"] == "01.07.2026"


def test_mt940_detalii_din_86():
    tz = parse_extras(MT940, "extras.sta")
    assert "DANTE INTERNATIONAL" in tz[0]["detalii"]
