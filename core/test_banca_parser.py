# -*- coding: utf-8 -*-
"""Test parser extras bancar CSV: delimitator robust (fara csv.Sniffer),
antet cu coloana Suma unica (cu semn), fallback fara antet, mesaj format asteptat.
Constatarea #4 (plimbare M2 14.08.2026)."""
import pytest
from core import banca_parser
from core.banca_parser import parse_extras, FORMAT_ASTEPTAT

# (a) antet + virgula-delimitator + zecimale-virgula + coloana Suma unica.
# Exact cazul care facea csv.Sniffer sa arunce "Could not determine delimiter".
CSV_A = b"""Data,Explicatie,Suma
01.08.2026,Plata factura ENGIE,100,50
02.08.2026,Incasare client DANTE,1234,56
"""

# (b) fara antet, ';', zecimale-virgula, ultima coloana = suma cu semn.
CSV_B = b"""01.08.2026;Plata factura ENGIE;-100,50
02.08.2026;Incasare client DANTE;250,00
03.08.2026;Comision banca;-9,90
"""

# (c) antet cu o singura coloana Suma cu semn (+/-), delimitator ';'.
CSV_C = b"""Data;Detalii;Suma
02.08.2026;Incasare DANTE;+250,00
03.08.2026;Plata ENGIE;-99,90
"""

# bonus: antet clasic Debit + Credit separate, delimitator ';', zecimale-virgula.
CSV_DC = b"""Data;Descriere;Debit;Credit
01.08.2026;Plata furnizor;100,50;
02.08.2026;Incasare client;;250,00
"""


def test_a_virgula_delimitator_si_zecimala():
    tz = parse_extras(CSV_A, "extras.csv")
    assert len(tz) == 2
    assert tz[0]["suma"] == 100.50
    assert tz[1]["suma"] == 1234.56
    assert "ENGIE" in tz[0]["detalii"]


def test_b_fara_antet_punct_virgula():
    tz = parse_extras(CSV_B, "extras.csv")
    assert len(tz) == 3
    assert tz[0]["suma"] == -100.50
    assert tz[1]["suma"] == 250.00
    assert tz[2]["suma"] == -9.90


def test_c_coloana_suma_cu_semn():
    tz = parse_extras(CSV_C, "extras.csv")
    assert len(tz) == 2
    assert tz[0]["suma"] == 250.00
    assert tz[1]["suma"] == -99.90


def test_dc_debit_credit_separate():
    tz = parse_extras(CSV_DC, "extras.csv")
    assert len(tz) == 2
    assert tz[0]["suma"] == -100.50   # debit -> negativ
    assert tz[1]["suma"] == 250.00    # credit -> pozitiv


def test_delimitator_detectat():
    assert banca_parser._detecteaza_delimitator("a,b,c\n1,2,3") == ","
    assert banca_parser._detecteaza_delimitator("a;b;c\n1;2;3") == ";"
    assert banca_parser._detecteaza_delimitator("a\tb\tc\n1\t2\t3") == "\t"
    # ; + zecimale-virgula -> prefera ;
    assert banca_parser._detecteaza_delimitator("01.08.2026;x;100,50") == ";"


def test_mesaj_format_la_zero_tranzactii():
    with pytest.raises(ValueError) as ei:
        parse_extras(b"gunoi fara nicio data sau suma\nalt rand\n", "x.csv")
    assert FORMAT_ASTEPTAT in str(ei.value)
    assert "Debit+Credit" in str(ei.value)
