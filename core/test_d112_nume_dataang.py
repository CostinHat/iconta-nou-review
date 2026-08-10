# -*- coding: utf-8 -*-
"""[catalog D112 1.8/1.9] numeAsig gol + data_angajare NULL refuzate PRE-DUK.

GAP inchis: numeAsig emis gol -> DUK "vid nepermis"; dataAng lipsa (data_angajare NULL) -> XSD.
Ambele plecau TACIT. Acum d112 refuza la radacina numind salariatul (CNP) + campul.

MUTATIE (HEAD 8b74ccb): _d112_genereaza emitea numeAsig="" / dataAng="" fara ValueError ->
pytest.raises pica pe HEAD. Dupa gard -> ValueError ridicat -> PASS.
"""
import pytest
from core import d112


def _prof():
    return {"cui": "14399840", "nume": "TEST SRL", "caen": "6202", "judet": "B",
            "declarant_nume": "POP", "declarant_prenume": "ION", "declarant_functie": "ADMIN"}


def _sal(**kw):
    base = {"brut": 3000, "cas": 750, "cass": 300, "impozit": 195, "ore_zi": 8,
            "cm": [], "zile_cm": 0, "cnp": "1900101410011", "nume": "POPESCU",
            "prenume": "ION", "data_angajare": "2020-01-15"}
    base.update(kw)
    return base


def test_baseline_emite():
    xml, _ = d112._d112_genereaza(_prof(), [_sal()], 2026, 6)
    assert 'numeAsig="POPESCU"' in xml and 'dataAng="15.01.2020"' in xml


@pytest.mark.parametrize("nume", ["", "   ", None])
def test_numeasig_gol_blocheaza(nume):
    with pytest.raises(ValueError) as ei:
        d112._d112_genereaza(_prof(), [_sal(nume=nume)], 2026, 6)
    msg = str(ei.value)
    assert "numeAsig" in msg, msg
    assert "1900101410011" in msg, "trebuie sa numeasca salariatul prin CNP: %s" % msg


@pytest.mark.parametrize("da", ["", None])
def test_data_angajare_null_blocheaza(da):
    with pytest.raises(ValueError) as ei:
        d112._d112_genereaza(_prof(), [_sal(data_angajare=da)], 2026, 6)
    msg = str(ei.value)
    assert "data_angajare" in msg or "dataAng" in msg, msg
    assert "POPESCU" in msg and "1900101410011" in msg, msg
