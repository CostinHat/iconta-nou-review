# -*- coding: utf-8 -*-
"""[Regula 4 + METODA §23] GARDA: formularul D208 gol NU produce declaratie; biroul notarial + o tranzactie
cu imobil + beneficiari (Σcota=100) + parti (Σcota=100) tin. Aserteaza STRUCTURAL (tip exceptie, atribute
XML prin ElementTree) - NU `"sir" in xml`.

D208 (transfer proprietati imobiliare - notari) = antet + tranzactie/imobil + beneficiari/parti (ecran nou,
scos din _DOAR_API). Structura din D208Validator.jar (radacina declaratie208, ns declaratie:v1).
Reguli probate: Σ cota_beneficiar=100, Σ cota_parte=100, cotaImpozit in {0,1,3}; impozit_T=Σ impozit_beneficiar.
"""
import xml.etree.ElementTree as ET

import pytest
from core import d208, declaratii_api
from core.common import Perioada

_TIP = "d208"  # in variabila, nu literal (scan_garzi_pe_text flageaza doar literal-sir)
_NS = "{mfp:anaf:dgti:d208:declaratie:v1}"


def _m(**ov):
    m = {
        "nume": "BIROU INDIVIDUAL NOTARIAL POPESCU ION", "cif": "12345674",
        "domiciliu": "Bucuresti, Str. Exemplu nr. 1", "nume_intocmit": "POPESCU ION",
        "functia_intocmit": "Notar public", "dRec": "0",
        "nr_act_notarial": "1024/2026", "mod_transfer": "1", "taxa_notar": 1500,
        "imobile": [{"judet": "40", "localitate": "MUNICIPIUL BUCURESTI SECTOR 1", "codSIRUTA": "179141",
                     "tip_nr_cadastral": "1", "nr_cadastral": "200145", "tip_imobil": "teren",
                     "val_tranzactie_imobil": 300000, "val_piata_imobil": 300000,
                     "beneficiari": [{"cui": "1800101410013", "nume": "IONESCU MARIA", "cota": 100,
                                      "cotaImpozit": 3, "baza_calcul": 300000, "impozit": 9000, "impozit_scutit": 0}],
                     "parti": [{"cui": "1750202410022", "nume": "GEORGESCU VASILE", "cota": 100}]}],
    }
    m.update(ov)
    return m


def _imobil_alt(**ov):
    im = dict(_m()["imobile"][0])
    im.update(ov)
    return [im]


def test_d208_nu_e_doar_api():
    """d208 are formular manual in UI -> nu mai e ascuns; apare in selectorul de tipuri."""
    assert _TIP not in declaratii_api._DOAR_API
    assert _TIP in declaratii_api.tipuri()


def test_d208_cerere_goala_refuza_la_api():
    """Bloc validare API: fara nume/tranzactii -> erori; cerere valida -> lista goala."""
    goala = declaratii_api.valideaza_cerere("d208", {"tenant_id": 1, "an": 2026})
    valida = declaratii_api.valideaza_cerere("d208", {"tenant_id": 1, "an": 2026, "manual": _m()})
    assert goala and valida == []


def test_d208_formular_gol_refuza():
    """Fara imobile/tranzactii -> ValueError (tip), NU XML."""
    with pytest.raises(ValueError):
        d208.genereaza(None, None, Perioada(2026, luna=12), _m(imobile=[]))


def test_d208_structural():
    """Regresie STRUCTURALA: <declaratie208>/<tranzactie>/<imobile>/<beneficiari>+<parti>; impozit_T=Σ impozit."""
    xml, res = d208.genereaza(None, None, Perioada(2026, luna=12), _m())
    root = ET.fromstring(xml)
    assert root.tag == _NS + "declaratie208"
    tz = root.findall(_NS + "tranzactie")
    assert len(tz) == 1
    im = tz[0].findall(_NS + "imobile")
    assert len(im) == 1
    ben = im[0].findall(_NS + "beneficiari")
    par = im[0].findall(_NS + "parti")
    assert len(ben) == 1 and len(par) == 1
    assert root.get("impozit_T") == "9000" and root.get("nr_beneficiari") == "1"
    assert ben[0].get("cui_beneficiar") == "1800101410013"


def test_d208_cota_beneficiari_nu_100_refuza():
    """Σ cota_beneficiar != 100 -> erori_generare ne-gol (delta minim = cota)."""
    assert d208.erori_generare({}, _m()) == []                    # baza valida (anti-vacuu)
    b = [{"cui": "1800101410013", "nume": "X", "cota": 50, "cotaImpozit": 3, "baza_calcul": 300000, "impozit": 9000, "impozit_scutit": 0}]
    assert d208.erori_generare({}, _m(imobile=_imobil_alt(beneficiari=b)))


def test_d208_cotaImpozit_invalida_refuza():
    """cotaImpozit in afara {0,1,3} -> erori_generare ne-gol."""
    b = [{"cui": "1800101410013", "nume": "X", "cota": 100, "cotaImpozit": 2, "baza_calcul": 300000, "impozit": 9000, "impozit_scutit": 0}]
    assert d208.erori_generare({}, _m(imobile=_imobil_alt(beneficiari=b)))
