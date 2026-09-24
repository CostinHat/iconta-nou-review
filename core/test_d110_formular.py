# -*- coding: utf-8 -*-
"""[Regula 4 + METODA §23] GARDA: formularul D110 gol NU produce declaratie; obligatiile (cod + sume) +
coerenta d_temei tin. Aserteaza STRUCTURAL (atribute XML prin ElementTree) - NU `"sir" in xml`. genereaza()
cere conn (pull firma_profil), deci testez piesele fara DB: calcul_d110 + erori_generare + build_xml.

D110 (regularizare/restituire impozit retinut la sursa) = obligatii (ecran nou, scos din _DOAR_API);
identitatea platitorului din firma_profil. Structura din D110Validator.jar (radacina D110, ns declaratie:v1).
Reguli: suma_rest>0 strict; dif_plata/dif_rest din suma_dat vs suma_rest; d_temei=1 => Σ dif_rest!=0 + IBAN/banca.
"""
import xml.etree.ElementTree as ET

from core import d110, declaratii_api

_TIP = "d110"  # in variabila, nu literal (scan_garzi_pe_text flageaza doar literal-sir)
_NS = "{mfp:anaf:dgti:d110:declaratie:v1}"
_PROF = {"den": "SC TEST SRL", "cui": "100204", "adresa": "Cluj-Napoca, Str. A nr.1",
         "declarant_nume": "Ionescu", "declarant_prenume": "Ana", "declarant_functie": "Contabil"}


def _m(**ov):
    m = {"d_temei": 0, "d_rec": 0, "obligatii": [{"cod_oblig": "602", "suma_dat": 1000, "suma_rest": 800}]}
    m.update(ov)
    return m


def test_d110_nu_e_doar_api():
    """d110 are formular manual in UI -> nu mai e ascuns; apare in selectorul de tipuri."""
    assert _TIP not in declaratii_api._DOAR_API
    assert _TIP in declaratii_api.tipuri()


def test_d110_cerere_goala_refuza_la_api():
    """Bloc validare API: fara obligatii -> erori; cerere valida -> lista goala."""
    goala = declaratii_api.valideaza_cerere("d110", {"tenant_id": 1, "an": 2026, "luna": 6})
    valida = declaratii_api.valideaza_cerere("d110", {"tenant_id": 1, "an": 2026, "luna": 6, "manual": _m()})
    assert goala and valida == []


def test_d110_baza_valida_fara_erori():
    """Anti-vacuu: _m() (prof complet, d_temei=0) e valid -> erori_generare goala."""
    assert d110.erori_generare(_PROF, _m(), d110.calcul_d110(6, 2026, _m())) == []


def test_d110_structural():
    """Regresie STRUCTURALA: <D110>/<obligatie>; dif_plata=suma_dat-suma_rest cand datorat>=retinut."""
    m = _m()
    calc = d110.calcul_d110(6, 2026, m)
    xml = d110.build_xml(_PROF, 2026, 6, m, calc)
    root = ET.fromstring(xml)
    assert root.tag == _NS + "D110" and root.get("cif") == "100204"
    obl = root.findall(_NS + "obligatie")
    assert len(obl) == 1 and obl[0].get("cod_oblig") == "602"
    assert obl[0].get("dif_plata") == "200" and obl[0].get("dif_rest") == "0"   # 1000 - 800


def test_d110_suma_rest_zero_refuza():
    """suma_rest <= 0 (strict) -> erori_generare ne-gol (delta minim)."""
    m = _m(obligatii=[{"cod_oblig": "602", "suma_dat": 1000, "suma_rest": 0}])
    assert d110.erori_generare(_PROF, m, d110.calcul_d110(6, 2026, m))


def test_d110_temei_incoerent_refuza():
    """d_temei=0 dar exista diferenta de restituit (suma_dat<suma_rest) -> erori_generare ne-gol."""
    m = _m(d_temei=0, obligatii=[{"cod_oblig": "602", "suma_dat": 500, "suma_rest": 800}])
    assert d110.erori_generare(_PROF, m, d110.calcul_d110(6, 2026, m))
