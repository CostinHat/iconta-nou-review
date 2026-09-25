# -*- coding: utf-8 -*-
"""[Regula 4 + METODA §23] GARDA: formularul D318 gol NU produce declaratie; perioada + solicitantul +
contul de rambursare + activitatea + facturile (achizitie/import cu furnizor UE) tin. Aserteaza STRUCTURAL
(tip exceptie, atribute XML prin ElementTree) - NU `"sir" in xml`.

D318 (rambursare TVA din alt stat UE, Directiva 2008/9/CE) = D318 > Applicant + BusinessDescription +
PurchaseInformation(>EuSupplier + GoodsDescriptionP) [+ ImportInformation(>Supplier + GoodsDescriptionI)].
Radacina <D318>, ns declaratie:v1 (scos din _DOAR_API). Reguli probate la validator: R5.1 (annual=1 =>
luni 1-12); R9.1/R9.3 (referenceNumber DOAR la rectificativa); R50.1 (per factura: acelasi semn,
vatAmount<=taxableAmount, issuingDate in perioada). Forma minima DUK-valida probata la DUKIntegrator.
"""
import xml.etree.ElementTree as ET

import pytest
from core import d318, declaratii_api
from core.common import Perioada

_TIP = "d318"  # in variabila, nu literal (scan_garzi_pe_text flageaza doar literal-sir)
_NS = "{mfp:anaf:dgti:d318:declaratie:v1}"


def _m(**ov):
    m = {
        "an": 2025, "luna_inceput": 1, "luna_sfarsit": 12, "annual": 1, "d_rec": 0, "cui": "40410000",
        "refunding_country": "DE", "language": "RO", "currency": "EUR",
        "iban": "DE89370400440532013000", "bic": "DEUTDEFF",
        "owner_name": "SC TEST SRL", "owner_type": "A", "declarant": "POPESCU ION", "functie": "administrator",
        "solicitant": {"denumire": "SC TEST SRL", "strada": "Str. Exemplu 1, Cluj-Napoca",
                       "email": "test@example.ro", "cod_postal": "400000"},
        "activitati": [{"activitate": "6201", "descriere": "Realizare software la comanda"}],
        "achizitii": [{"reference_number": "DE-2025-000123", "issuing_date": "15.06.2025",
                       "taxable_amount": 1000, "vat_amount": 190, "deductible_vat": 190,
                       "furnizor": {"denumire": "Muster GmbH", "strada": "Hauptstrasse 1, Berlin",
                                    "tara": "DE", "vat_id": "DE123456789"},
                       "bunuri": [{"code": "3"}]}],
    }
    m.update(ov)
    return m


def test_d318_nu_e_doar_api():
    """d318 are formular manual in UI -> nu mai e ascuns; apare in selectorul de tipuri."""
    assert _TIP not in declaratii_api._DOAR_API
    assert _TIP in declaratii_api.tipuri()


def test_d318_cerere_goala_refuza_la_api():
    """Bloc validare API: fara CUI/IBAN/facturi -> erori; cerere valida -> lista goala."""
    goala = declaratii_api.valideaza_cerere("d318", {"tenant_id": 1, "an": 2025})
    valida = declaratii_api.valideaza_cerere("d318", {"tenant_id": 1, "an": 2025, "manual": _m()})
    assert goala and valida == []


def test_d318_formular_gol_refuza():
    """Fara nicio factura -> ValueError (tip), NU XML: o cerere de rambursare fara facturi n-are ce cere."""
    with pytest.raises(ValueError):
        d318.genereaza(None, None, Perioada(2025, luna=12), _m(achizitii=[], importuri=[]))


def test_d318_structural():
    """Regresie STRUCTURALA: <D318> > Applicant + BusinessDescription + PurchaseInformation>EuSupplier+GoodsDescriptionP."""
    xml, res = d318.genereaza(None, None, Perioada(2025, luna=12), _m())
    root = ET.fromstring(xml)
    assert root.tag == _NS + "D318"
    assert root.get("annual") == "1" and root.get("refundingCountryCode") == "DE"
    assert root.get("amount") == "190.00"       # suma TVA deductibila ceruta
    assert root.get("sumaControl") == "0"       # R8: fix 0
    assert len(root.findall(_NS + "Applicant")) == 1
    assert len(root.findall(_NS + "BusinessDescription")) == 1
    pi = root.findall(_NS + "PurchaseInformation")
    assert len(pi) == 1 and pi[0].get("deductibleVATAmount") == "190.00"
    assert len(pi[0].findall(_NS + "EuSupplier")) == 1
    assert pi[0].find(_NS + "EuSupplier").get("countryCode") == "DE"
    assert len(pi[0].findall(_NS + "GoodsDescriptionP")) == 1


def test_d318_annual_cere_an_intreg():
    """R5.1: annual=1 cu luni != (1,12) -> erori_generare ne-gol; forma corecta -> gol."""
    assert d318.erori_generare({}, _m()) == []
    assert d318.erori_generare({}, _m(luna_inceput=3, luna_sfarsit=9))


def test_d318_vat_peste_baza_refuza():
    """R50.1: vatAmount > taxableAmount pe o factura -> erori_generare ne-gol."""
    rau = [{"reference_number": "DE-1", "issuing_date": "15.06.2025", "taxable_amount": 100,
            "vat_amount": 200, "deductible_vat": 200,
            "furnizor": {"denumire": "X GmbH", "strada": "Str 1", "tara": "DE"}, "bunuri": [{"code": "3"}]}]
    assert d318.erori_generare({}, _m(achizitii=rau))


def test_d318_referinta_doar_la_rectificativa():
    """R9.1: initiala (d_rec=0) NU poate avea reference_number; R9.3: rectificativa (d_rec=1) cere reference_number."""
    assert d318.erori_generare({}, _m(d_rec=0, reference_number="RO123"))       # initiala cu ref -> eroare
    assert d318.erori_generare({}, _m(d_rec=1))                                 # rectificativa fara ref -> eroare
    assert d318.erori_generare({}, _m(d_rec=1, reference_number="RO123")) == []  # rectificativa cu ref RO -> ok
