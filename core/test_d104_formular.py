# -*- coding: utf-8 -*-
"""[Regula 4 + METODA §23] GARDA: formularul D104 gol NU produce declaratie; declarantul + asocierea +
profit/pierdere + asociatii tin. Aserteaza STRUCTURAL (atribute XML prin ElementTree) - NU `"sir" in xml`.
genereaza() cere conn (pull firma_profil), deci testez piesele fara DB: erori_generare + build_xml.

D104 (distribuire venituri/cheltuieli intre asociati, asociere f.PJ) = declarant + asociere + asociati (ecran
nou, scos din _DOAR_API). Structura din D104Validator.jar (radacina declaratie104, ns declaratie:v1).
Reguli: luna ∈ {3,6,9,12}; per SB 0<cota<=100, cif1 unic; totaluri agregate; declarant din manual sau firma_profil.
"""
import xml.etree.ElementTree as ET

from core import d104, declaratii_api

_TIP = "d104"  # in variabila, nu literal (scan_garzi_pe_text flageaza doar literal-sir)
_NS = "{mfp:anaf:dgti:d104:declaratie:v1}"


def _cnp(b):
    w = (2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9)
    c = sum(int(b[i]) * w[i] for i in range(12)) % 11
    return b + str(1 if c == 10 else c)


def _m(**ov):
    m = {
        "declarant_nume": "POPESCU", "declarant_prenume": "ION", "declarant_functie": "Asociat desemnat",
        "asociere": {"cui": "100204", "den": "ASOCIEREA EXEMPLU", "adresa": "Cluj-Napoca, Str. A nr.1"},
        "profit_pierd": 6000, "d_rec": 0,
        "asociati": [{"den": "POPESCU ION", "cif": _cnp("196022915094"), "cota": 60, "venit": 6000, "chelt": 2000, "imp_datorat": 900},
                     {"den": "IONESCU ANA", "cif": _cnp("290030112233"), "cota": 40, "venit": 4000, "chelt": 1000, "imp_datorat": 600}],
    }
    m.update(ov)
    return m


def test_d104_nu_e_doar_api():
    """d104 are formular manual in UI -> nu mai e ascuns; apare in selectorul de tipuri."""
    assert _TIP not in declaratii_api._DOAR_API
    assert _TIP in declaratii_api.tipuri()


def test_d104_cerere_goala_refuza_la_api():
    """Bloc validare API: fara asociati/profit -> erori; cerere valida -> lista goala."""
    goala = declaratii_api.valideaza_cerere("d104", {"tenant_id": 1, "an": 2025, "trim": 1})
    valida = declaratii_api.valideaza_cerere("d104", {"tenant_id": 1, "an": 2025, "trim": 1, "manual": _m()})
    assert goala and valida == []


def test_d104_baza_valida_fara_erori():
    """Anti-vacuu: _m() (declarant in manual) e valid la trim I -> erori_generare goala."""
    assert d104.erori_generare({}, 3, _m()) == []


def test_d104_structural():
    """Regresie STRUCTURALA: <declaratie104>/<SB>; luna=3, Tven agregat, 2 SB cu cif1 corect."""
    calc = d104.calcul_d104(3, _m())
    xml = d104.build_xml({}, 2025, 3, _m(), calc)
    root = ET.fromstring(xml)
    assert root.tag == _NS + "declaratie104"
    assert root.get("luna") == "3" and int(root.get("Tven")) == 10000
    sb = root.findall(_NS + "SB")
    assert len(sb) == 2
    assert {s.get("cif1") for s in sb} == {_cnp("196022915094"), _cnp("290030112233")}
    assert root.get("nume_declar") == "POPESCU"   # declarant din manual (fallback)


def test_d104_cota_peste_100_refuza():
    """cota > 100 -> erori_generare ne-gol (delta minim)."""
    a = [{"den": "X", "cif": _cnp("196022915094"), "cota": 150, "venit": 6000, "chelt": 2000, "imp_datorat": 900}]
    assert d104.erori_generare({}, 3, _m(asociati=a))


def test_d104_cif_duplicat_refuza():
    """cif1 duplicat intre asociati -> erori_generare ne-gol."""
    cf = _cnp("196022915094")
    a = [{"den": "X", "cif": cf, "cota": 60, "venit": 6000, "chelt": 2000, "imp_datorat": 900},
         {"den": "Y", "cif": cf, "cota": 40, "venit": 4000, "chelt": 1000, "imp_datorat": 600}]
    assert d104.erori_generare({}, 3, _m(asociati=a))
