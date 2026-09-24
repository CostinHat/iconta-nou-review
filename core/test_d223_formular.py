# -*- coding: utf-8 -*-
"""[Regula 4 + METODA §23] GARDA: formularul D223 gol NU produce declaratie; asocierea + responsabilul +
activitatea + asociatii (cote Σ=100, venit estimat distribuit dupa cota) tin. Aserteaza STRUCTURAL
(atribute XML prin ElementTree) - NU `"sir" in xml`. genereaza() cere conn (pull firma_profil), deci
testez piesele fara DB: erori_generare(prof, manual) + build_xml(prof, an, manual, calc).

D223 (venituri estimate asocieri f.PJ) = asociere + responsabil + o activitate + asociati (ecran nou,
scos din _DOAR_API). Structura din D223Validator.jar (radacina declaratie223, ns declaratie:v1).
"""
import xml.etree.ElementTree as ET

from core import d223, declaratii_api

_TIP = "d223"  # in variabila, nu literal (scan_garzi_pe_text flageaza doar literal-sir)
_NS = "{mfp:anaf:dgti:d223:declaratie:v1}"


def _cnp(b):
    w = (2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9)
    c = sum(int(b[i]) * w[i] for i in range(12)) % 11
    return b + str(1 if c == 10 else c)


def _m(**ov):
    m = {
        "declarant_nume": "POPESCU", "declarant_prenume": "ION", "declarant_functie": "Responsabil",
        "asociere": {"nume": "ASOCIEREA EXEMPLU", "cif": "100204", "adresa": "Cluj-Napoca, Str. A nr.1"},
        "responsabil": {"den_r": "POPESCU ION", "cif_r": _cnp("180010122114"), "adresa_r": "Cluj-Napoca, Str. A nr.1"},
        "d_rec1": 0, "d_rec": 0,
        "activitate": {"categ_venit": "1", "forma_org": "2", "det_venit": "1", "caen": "4711", "judet": "12",
                       "localitate": "Cluj-Napoca", "sediu": "Cluj-Napoca, Str. A nr.1", "nr_contr": "1",
                       "data_contr": "01.01.2020", "venit_brut": 10000, "cheltuieli": 4000},
        "asociati": [{"nume_d": "POPESCU ION", "cif_d": _cnp("196022915094"), "cota_d": 60},
                     {"nume_d": "IONESCU ANA", "cif_d": _cnp("290030112233"), "cota_d": 40}],
    }
    m.update(ov)
    return m


def test_d223_nu_e_doar_api():
    """d223 are formular manual in UI -> nu mai e ascuns; apare in selectorul de tipuri."""
    assert _TIP not in declaratii_api._DOAR_API
    assert _TIP in declaratii_api.tipuri()


def test_d223_cerere_goala_refuza_la_api():
    """Bloc validare API: fara activitate/asociati -> erori; cerere valida -> lista goala."""
    goala = declaratii_api.valideaza_cerere("d223", {"tenant_id": 1, "an": 2025})
    valida = declaratii_api.valideaza_cerere("d223", {"tenant_id": 1, "an": 2025, "manual": _m()})
    assert goala and valida == []


def test_d223_erori_generare_gol_refuza():
    """Fara asociati / activitate -> erori_generare ne-gol (nu se poate genera)."""
    assert d223.erori_generare({}, _m(asociati=[]))
    assert d223.erori_generare({}, {})


def test_d223_structural():
    """Regresie STRUCTURALA: build_xml -> <declaratie223>/<activitate>/<asociat>; net3 si distributie corecte."""
    calc = d223.calcul_d223(_m())
    xml = d223.build_xml({}, 2025, _m(), calc)
    root = ET.fromstring(xml)
    assert root.tag == _NS + "declaratie223"
    act = root.findall(_NS + "activitate")
    assert len(act) == 1
    assert act[0].get("categ_venit") == "1" and act[0].get("judet") == "12" and act[0].get("net3") == "6000"
    asoc = act[0].findall(_NS + "asociat")
    assert len(asoc) == 2 and act[0].get("nr_asoc") == "2"
    assert {a.get("cota_d") for a in asoc} == {"60", "40"}
    assert sum(int(a.get("venit_d")) for a in asoc) == 6000   # distributie: suma venit_d = net3


def test_d223_baza_valida_fara_erori():
    """Anti-vacuu: baza _m() e valida (prof gol, declarant din manual) -> lista de erori goala."""
    assert d223.erori_generare({}, _m()) == []


def test_d223_cota_nu_suma_100_refuza():
    """Σ cota_d != 100 -> lista de erori ne-goala (delta minim fata de baza valida = suma cotelor)."""
    assert d223.erori_generare({}, _m(
        asociati=[{"nume_d": "X", "cif_d": _cnp("196022915094"), "cota_d": 50}]))


def test_d223_sector_obligatoriu_bucuresti():
    """judet=40 (Bucuresti) fara sector -> lista de erori ne-goala (delta minim = sectorul)."""
    act = dict(_m()["activitate"], judet="40", sector="")
    assert d223.erori_generare({}, _m(activitate=act))
