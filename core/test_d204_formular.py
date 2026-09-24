# -*- coding: utf-8 -*-
"""[Regula 4 + METODA §23] GARDA: formularul D204 gol NU produce declaratie; asocierea + reprezentantul +
activitatea + asociatii (cote Σ=100, venit repartizat = net) tin. Aserteaza STRUCTURAL (tip exceptie,
atribute XML prin ElementTree) - NU `"sir" in xml`.

D204 (asociere fara personalitate juridica) = asociere + reprezentant + o activitate + lista asociati
(ecran nou, scos din _DOAR_API). Structura din D204Validator.jar (radacina d204, ns declaratie:v3).
Reguli probate pe DUK: judet cod NUMERIC; nr_contr+data_contr obligatorii; Σ cota_d=100; Σ venit_d=net3.
"""
import xml.etree.ElementTree as ET

import pytest
from core import d204, declaratii_api
from core.common import Perioada

_TIP = "d204"  # in variabila, nu literal (scan_garzi_pe_text flageaza doar literal-sir)
_NS = "{mfp:anaf:dgti:d204:declaratie:v3}"


def _cnp(b):
    w = (2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9)
    c = sum(int(b[i]) * w[i] for i in range(12)) % 11
    return b + str(1 if c == 10 else c)


_CIF_ASO = "100204"  # CUI valid (cifra de control)


def _m(**ov):
    m = {
        "asociere": {"den": "ASOCIEREA EXEMPLU", "cif": _CIF_ASO, "adresa": "Str. Test 1, Cluj-Napoca"},
        "reprezentant": {"nume": "POPESCU ION", "cif": _cnp("180010122114"), "adresa": "Str. Test 2, Cluj-Napoca"},
        "activitate": {"categ_venit": 1, "det_ven_net": 1, "caen": "6201", "forma_org": 1, "judet": "12",
                       "sediu": "Str. Test 1, Cluj-Napoca", "nr_contr": "1", "data_contr": "01.01.2020",
                       "venit3": 10000, "chelt3": 4000},
        "asociati": [{"cif": _cnp("196022915094"), "nume": "POPESCU ION", "cota": 60, "venit": 3600, "pierd": 0},
                     {"cif": _cnp("290030112233"), "nume": "IONESCU ANA", "cota": 40, "venit": 2400, "pierd": 0}],
    }
    m.update(ov)
    return m


def test_d204_nu_e_doar_api():
    """d204 are formular manual in UI -> nu mai e ascuns; apare in selectorul de tipuri."""
    assert _TIP not in declaratii_api._DOAR_API
    assert _TIP in declaratii_api.tipuri()


def test_d204_cerere_goala_refuza_la_api():
    """Bloc validare API: fara asociere/activitate -> erori; cerere valida -> lista goala."""
    goala = declaratii_api.valideaza_cerere("d204", {"tenant_id": 1, "an": 2025})
    valida = declaratii_api.valideaza_cerere("d204", {"tenant_id": 1, "an": 2025, "manual": _m()})
    assert goala and valida == []


def test_d204_formular_gol_refuza():
    """Fara asociati -> ValueError (tip), NU XML."""
    with pytest.raises(ValueError):
        d204.genereaza(None, None, Perioada(2025, luna=12), _m(asociati=[]))


def test_d204_genereaza_structural():
    """Regresie STRUCTURALA: intrare reala -> <d204>/<activitate>/<asociat>; judet numeric, net3=venit3-chelt3."""
    xml, res = d204.genereaza(None, None, Perioada(2025, luna=12), _m())
    root = ET.fromstring(xml)
    assert root.tag == _NS + "d204"
    act = root.findall(_NS + "activitate")
    assert len(act) == 1
    assert act[0].get("judet") == "12" and act[0].get("net3") == "6000"  # 10000 - 4000
    asoc = act[0].findall(_NS + "asociat")
    assert len(asoc) == 2 and act[0].get("nr_asoc") == "2"
    assert {a.get("cota_d") for a in asoc} == {"60", "40"}


def test_d204_cota_nu_suma_100_refuza():
    """Σ cota_d != 100 -> refuz (nu XML gresit)."""
    with pytest.raises(ValueError):
        d204.genereaza(None, None, Perioada(2025, luna=12),
                       _m(asociati=[{"cif": _cnp("196022915094"), "nume": "X", "cota": 50, "venit": 6000, "pierd": 0}]))


def test_d204_venit_repartizat_neegal_refuza():
    """Σ venit_d != net3 -> refuz."""
    with pytest.raises(ValueError):
        d204.genereaza(None, None, Perioada(2025, luna=12),
                       _m(asociati=[{"cif": _cnp("196022915094"), "nume": "X", "cota": 100, "venit": 5000, "pierd": 0}]))


def test_d204_contract_si_judet_numeric_obligatorii():
    """Garda onesta = ce cere DUK: fara contract -> refuz; judet nenumeric -> refuz."""
    with pytest.raises(ValueError):
        d204.genereaza(None, None, Perioada(2025, luna=12),
                       _m(activitate=dict(_m()["activitate"], nr_contr="", data_contr="")))
    with pytest.raises(ValueError):
        d204.genereaza(None, None, Perioada(2025, luna=12),
                       _m(activitate=dict(_m()["activitate"], judet="Cluj")))
