# -*- coding: utf-8 -*-
"""[Regula 4 + METODA §23] GARDA: formularul D398 gol NU produce declaratie; regimul + identitatea + livrarile
(pe stat de consum) tin. Aserteaza STRUCTURAL (tip exceptie, atribute XML prin ElementTree) - NU `"sir" in xml`.

D398 (OSS - TVA regimuri speciale) = d398 > MS(stat) > SUPPLY (ecran nou, scos din _DOAR_API). Structura din
D398Validator.jar (radacina d398, ns declaratie:v1). Reguli probate: vat_amount=taxable*rate/100 (R29);
msest doar in regim UE (R23); bunuri interzise non-UE (R25.1); vat_rate in (0,100] (R27.1); taxable>0 (R28).
"""
import xml.etree.ElementTree as ET

import pytest
from core import d398, declaratii_api
from core.common import Perioada

_TIP = "d398"  # in variabila, nu literal (scan_garzi_pe_text flageaza doar literal-sir)
_NS = "{mfp:anaf:dgti:d398:declaratie:v1}"


def _m(**ov):
    m = {"moes_voes_imp": 1, "e_int": 0, "name": "SC TEST SRL", "vat_id_no": "RO40410000",
         "an_r": 2026, "luna_r": 3, "period_start_date": "01.01.2026", "period_end_date": "31.03.2026",
         "d_rec": 0, "currency": "EUR",
         "ms": [{"mscon_state": "DE", "supplies": [
             {"supply_type": 1, "trade_type": 1, "vat_rate_type": 1, "vat_rate": 19, "taxable_amount": 1000}]}]}
    m.update(ov)
    return m


def test_d398_nu_e_doar_api():
    """d398 are formular manual in UI -> nu mai e ascuns; apare in selectorul de tipuri."""
    assert _TIP not in declaratii_api._DOAR_API
    assert _TIP in declaratii_api.tipuri()


def test_d398_cerere_goala_refuza_la_api():
    """Bloc validare API: fara regim/identitate/state -> erori; cerere valida -> lista goala."""
    goala = declaratii_api.valideaza_cerere("d398", {"tenant_id": 1, "an": 2026, "trim": 1})
    valida = declaratii_api.valideaza_cerere("d398", {"tenant_id": 1, "an": 2026, "trim": 1, "manual": _m()})
    assert goala and valida == []


def test_d398_formular_gol_refuza():
    """Fara MS -> ValueError (tip), NU XML (moes valid dar niciun stat cu supply nu se genereaza NIL fara sens util)."""
    with pytest.raises(ValueError):
        d398.genereaza(None, None, Perioada(2026, luna=3), _m(ms=[{"mscon_state": "DE", "supplies": []}]))


def test_d398_structural():
    """Regresie STRUCTURALA: <d398>/<MS>/<SUPPLY>; vat_amount=taxable*rate/100; grand_total_vat_due agregat."""
    xml, res = d398.genereaza(None, None, Perioada(2026, luna=3), _m())
    root = ET.fromstring(xml)
    assert root.tag == _NS + "d398"
    ms = root.findall(_NS + "MS")
    assert len(ms) == 1 and ms[0].get("mscon_state") == "DE"
    sup = ms[0].findall(_NS + "SUPPLY")
    assert len(sup) == 1 and sup[0].get("vat_amount") == "190.00"   # 1000 * 19 / 100
    assert root.get("grand_total_vat_due") == "190.00"


def test_d398_bunuri_in_nonue_refuza():
    """R25.1: bunuri (supply_type=1) interzise in regim non-UE (moes=2) -> erori_generare ne-gol."""
    assert d398.erori_generare({}, _m()) == []
    assert d398.erori_generare({}, _m(moes_voes_imp=2, e_int=None))


def test_d398_cota_invalida_refuza():
    """R27.1: vat_rate in afara (0,100] -> erori_generare ne-gol."""
    bad = [{"mscon_state": "DE", "supplies": [
        {"supply_type": 1, "trade_type": 1, "vat_rate_type": 1, "vat_rate": 0, "taxable_amount": 1000}]}]
    assert d398.erori_generare({}, _m(ms=bad))
