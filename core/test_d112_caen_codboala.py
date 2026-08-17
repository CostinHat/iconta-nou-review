# -*- coding: utf-8 -*-
"""[catalog D112 2.1/2.3] caen out-of-enum + cod boala out-of-enum refuzate PRE-DUK.

GAP inchis: caen '9999' (tip XSD Str_caenListSType, enumerare inchisa) si cod boala '99' (D_9 tip
Str_codBoalaSType, coduri 01-15) plecau TACIT -> XSD reject. Acum d112 refuza cu motivul exact,
numind valoarea + tipul XSD. Enumerarile se extrag din anaf_surse/d112_06082026.xsd (autoritatea).

MUTATIE (HEAD 8b74ccb): emitea caen="9999" / D_9="99" fara ValueError -> pytest.raises pica pe HEAD.
Dupa gard -> ValueError ridicat -> PASS.
"""
import re
import pytest
from core import d112


def _prof(**kw):
    p = {"cui": "301111003", "nume": "TEST SRL", "caen": "6202", "judet": "bucuresti"}
    p.update(kw)
    return p


def _sal_cm(**cm):
    cert = {"cod": "01", "zile_ang": 3, "zile_fnuass": 2, "brut_ang": 714,
            "brut_fnuass": 476, "baza": 5000, "serie": "AA", "numar": "111",
            "da": "01.08.2026", "di": "01.08.2026", "ds": "05.08.2026",
            "loc_prescriere": 1, "diagnostic": "999"}
    cert.update(cm)
    return {"id": 1, "nume": "TEST", "prenume": "X", "cnp": "1850315400125",
            "data_angajare": "2026-01-15", "brut": 5000, "brut_lucrat": 3810,
            "ore_zi": 8, "judet_casa": "bucuresti", "cas": 0, "cass": 0, "impozit": 0,
            "facilitate": 0, "deducere": 0, "zile_cm": 5, "cm": [cert]}


def test_baseline_caen_codboala_valide_emit():
    xml, _ = d112._d112_genereaza(_prof(caen="6202"), [_sal_cm(cod="01")], 2026, 8)
    assert 'caen="6202"' in xml
    assert re.search(r'D_9="0?1"', xml), xml


def test_caen_9999_out_of_enum_blocheaza():
    with pytest.raises(ValueError) as ei:
        d112._d112_genereaza(_prof(caen="9999"), [_sal_cm()], 2026, 8)
    msg = str(ei.value)
    assert "CAEN" in msg and "9999" in msg, msg
    assert "Str_caenListSType" in msg, msg


def test_cod_boala_99_out_of_enum_blocheaza():
    with pytest.raises(ValueError) as ei:
        d112._d112_genereaza(_prof(), [_sal_cm(cod="99")], 2026, 8)
    msg = str(ei.value)
    assert "cod boală" in msg and "99" in msg, msg
    assert "Str_codBoalaSType" in msg, msg
    assert "1850315400125" in msg, "trebuie să numeasca salariatul: %s" % msg


def test_enum_xsd_se_incarca_din_sursa():
    """Enumerarile provin din XSD-ul real, nu dintr-un tabel hardcodat (a doua sursa de adevar)."""
    caene = d112._enum_xsd("Str_caenListSType")
    codb = d112._enum_xsd("Str_codBoalaSType")
    assert "6202" in caene and "9999" not in caene
    assert codb == {"%02d" % i for i in range(1, 16)}, sorted(codb)
