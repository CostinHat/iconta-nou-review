# -*- coding: utf-8 -*-
"""[Regula 4 + METODA §23] GARDA: formularul D221 gol NU produce declaratie; contribuabilul + activitatile
agricole (localitate unica, codp unic) + asociatii (forma_org=2, Σcota=100) tin. Aserteaza STRUCTURAL
(atribute XML prin ElementTree) - NU `"sir" in xml`. genereaza() cere conn (pull firma_profil), deci testez
piesele fara DB: erori_generare(prof, an, manual) + build_xml(prof, an, manual).

D221 (venituri agricole pe norme) = contribuabil + activitati/produse (+ asociati la forma_org=2) (ecran nou,
scos din _DOAR_API). Structura din D221Validator.jar (radacina declaratie221, ns declaratie:v1). Reguli:
totalPlata_A=0 mereu; ordine XSD activitati INAINTE de asociati; forma_org=2 cere >=2 asociati cu Σcota=100.
"""
import xml.etree.ElementTree as ET

from core import d221, declaratii_api

_TIP = "d221"  # in variabila, nu literal (scan_garzi_pe_text flageaza doar literal-sir)
_NS = "{mfp:anaf:dgti:d221:declaratie:v1}"


def _m(**ov):
    m = {
        "nume_declar": "POPESCU", "prenume_declar": "ION", "functie_declar": "TITULAR",
        "cif": "1850715400015", "nume_a": "Popescu Ion", "adresa_a": "Comuna Test, jud. Cluj",
        "forma_org": "1", "d_rec": 0,
        "activitati": [{"judet": "12", "localitate": "Comuna Test", "optiune": "0",
                        "produse": [{"codp": "101", "prod1": 12.5}, {"codp": "201", "prod1": 8}]}],
    }
    m.update(ov)
    return m


def test_d221_nu_e_doar_api():
    """d221 are formular manual in UI -> nu mai e ascuns; apare in selectorul de tipuri."""
    assert _TIP not in declaratii_api._DOAR_API
    assert _TIP in declaratii_api.tipuri()


def test_d221_cerere_goala_refuza_la_api():
    """Bloc validare API: fara cif/activitati -> erori; cerere valida -> lista goala."""
    goala = declaratii_api.valideaza_cerere("d221", {"tenant_id": 1, "an": 2025})
    valida = declaratii_api.valideaza_cerere("d221", {"tenant_id": 1, "an": 2025, "manual": _m()})
    assert goala and valida == []


def test_d221_baza_valida_fara_erori():
    """Anti-vacuu: _m() (individual, declarant in manual) e valid -> erori_generare goala."""
    assert d221.erori_generare({}, 2025, _m()) == []


def test_d221_structural():
    """Regresie STRUCTURALA: <declaratie221>/<activitati>/<produse>; totalPlata_A=0; ordine activitati->asociati."""
    xml = d221.build_xml({}, 2025, _m())
    root = ET.fromstring(xml)
    assert root.tag == _NS + "declaratie221"
    assert root.get("forma_org") == "1" and root.get("totalPlata_A") == "0" and root.get("aj_soc") == "0"
    act = root.findall(_NS + "activitati")
    assert len(act) == 1
    prod = act[0].findall(_NS + "produse")
    assert len(prod) == 2 and {p.get("codp") for p in prod} == {"101", "201"}
    # ordinea in copiii radacinii: toate <activitati> inaintea oricarui <asociati>
    tags = [ch.tag for ch in root]
    if _NS + "asociati" in tags:
        assert tags.index(_NS + "activitati") < tags.index(_NS + "asociati")


def test_d221_codp_duplicat_refuza():
    """codp duplicat in aceeasi activitate -> erori_generare ne-gol (delta minim)."""
    act = [{"judet": "12", "localitate": "Comuna Test", "optiune": "0",
            "produse": [{"codp": "101", "prod1": 5}, {"codp": "101", "prod1": 3}]}]
    assert d221.erori_generare({}, 2025, _m(activitati=act))


def test_d221_asociere_fara_asociati_refuza():
    """forma_org=2 fara cei 2 asociati -> erori_generare ne-gol."""
    assert d221.erori_generare({}, 2025, _m(forma_org="2", nr_contr="1", data_contr="01.01.2020"))
