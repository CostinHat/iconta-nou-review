# -*- coding: utf-8 -*-
"""[T1] CNP salariat + CUI firma pre-validate PRE-DUK (checksum offline, core.identitate).

GAP inchis (catalog D112 3.1-3.4): cnpAsig cu lungime/format/leading-zero/alpha gresit (XSD
CnpSType pattern) sau cifra de control gresita (DUK) plecau TACIT la ANAF; la fel CUI firma
prezent-dar-invalid. Acum d112 refuza la radacina cu ValueError care NUMESTE salariatul (nume+CNP)
si motivul exact, inainte de emitere.

MUTATIE (probata pe HEAD 8b74ccb): _d112_genereaza emitea XML fara ValueError (silent emit) ->
pytest.raises pica pe HEAD. Dupa gard -> ValueError ridicat cu motivul exact -> PASS.
"""
import re
import pytest
from core import d112


def _prof(**kw):
    p = {"cui": "14399840", "nume": "TEST SRL", "caen": "6202", "judet": "B",
         "declarant_nume": "POP", "declarant_prenume": "ION", "declarant_functie": "ADMIN"}
    p.update(kw)
    return p


def _sal(**kw):
    base = {"brut": 3000, "cas": 750, "cass": 300, "impozit": 195, "cass_tichete": 0,
            "impozit_tichete": 0, "tichete_nominal": 0, "e83_masa": 0, "e83_vacanta": 0,
            "e83_cultural": 0, "e83_cresa": 0, "ore_zi": 8, "cm": [], "zile_cm": 0,
            "cnp": "1900101410011", "nume": "POPESCU", "prenume": "ION",
            "data_angajare": "2020-01-15"}
    base.update(kw)
    return base


def test_baseline_cnp_cui_valide_emit():
    """Control pozitiv: CNP + CUI valide -> se emite, cnpAsig poarta CNP-ul (gardul nu supra-blocheaza)."""
    xml, _ = d112._d112_genereaza(_prof(), [_sal()], 2026, 6)
    assert 'cnpAsig="1900101410011"' in xml
    assert 'cif="14399840"' in xml


@pytest.mark.parametrize("cnp,cheie", [
    ("12345", "format"),                 # 3.1 lungime (XSD CnpSType pattern)
    ("19001014X0011", "format"),         # 3.2 alpha (non-numeric)
    ("0900101410011", "prima cifra"),    # 3.3 leading-zero (prima cifra 1-9)
    ("1900101410012", "cifra de control"),  # 3.4 checksum (DUK)
])
def test_cnp_angajat_invalid_blocheaza_cu_motiv(cnp, cheie):
    with pytest.raises(ValueError) as ei:
        d112._d112_genereaza(_prof(), [_sal(cnp=cnp)], 2026, 6)
    msg = str(ei.value)
    assert "POPESCU" in msg, "ValueError trebuie sa NUMEASCA salariatul: %s" % msg
    assert cnp in msg, "ValueError trebuie sa contina CNP-ul gresit: %s" % msg
    assert cheie in msg, "ValueError trebuie sa dea motivul exact (%s): %s" % (cheie, msg)


def test_cui_firma_checksum_invalid_blocheaza():
    with pytest.raises(ValueError) as ei:
        d112._d112_genereaza(_prof(cui="14399841"), [_sal()], 2026, 6)  # ultima cifra alterata
    msg = str(ei.value)
    assert "CUI firm" in msg and "14399841" in msg, msg
    assert "cifra de control" in msg, msg


def test_mai_multi_salariati_numeste_pe_cel_gresit():
    """Cu doi salariati, ValueError il numeste pe cel cu CNP invalid, nu pe cel corect."""
    s_ok = _sal(nume="CORECT", cnp="1900101410011")
    s_rau = _sal(nume="GRESIT", cnp="1900101410012")
    with pytest.raises(ValueError) as ei:
        d112._d112_genereaza(_prof(), [s_ok, s_rau], 2026, 6)
    assert "GRESIT" in str(ei.value), str(ei.value)
