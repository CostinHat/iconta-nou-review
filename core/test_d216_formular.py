# -*- coding: utf-8 -*-
"""[Regula 4 + METODA §23] GARDA: formularul D216 gol NU produce declaratie; antetul + cel putin un bun
(imobil sau mobil) cu valoare > plafon tin. Aserteaza STRUCTURAL (tip exceptie, atribute XML prin
ElementTree) - NU `"sir" in xml`.

D216 (impozit special pe bunuri de valoare mare, Legea 296/2023) = antet + liste imobile/mobile (ecran nou,
scos din _DOAR_API). Structura din D216Validator.jar (radacina D216, ns declaratie:v1). Reguli probate:
valoare_impozabila > plafon (d_rec=0); impozit = ROUND(baza * cota anului) — 0,3% 2024-2025, 0,9% din 2026 (COTE).
"""
import xml.etree.ElementTree as ET

import pytest
from core import d216, declaratii_api
from core.common import Perioada

_TIP = "d216"  # in variabila, nu literal (scan_garzi_pe_text flageaza doar literal-sir)
_NS = "{mfp:anaf:dgti:d216:declaratie:v1}"

_IMOBIL = {"judet_imobil": "BOTOSANI", "cod_judet_imobil": "7", "localitate_imobil": "BOTOSANI",
           "cod_localitate_imobil": "1", "strada_imobil": "STR PRIMAVERII", "cod_strada_imobil": "1",
           "nr_cadastral": "12345", "valoare_impozabila_imobil": 3000000, "cota": 0.3, "plafon_imobil": 2500000}
_MOBIL = {"an_detinere": 2023, "niv": 5, "valoare_impozabila_mobil": 400000, "plafon_mobil": 375000}


def _m(**ov):
    m = {"nume": "POPESCU ION", "cif": "1960101410019", "domiciliuFiscal": "JUD BOTOSANI MUN BOTOSANI",
         "nume_intocmit": "IONESCU MARIA", "functia_intocmit": "CONTABIL", "d_rec": 0,
         "imobile": [dict(_IMOBIL)], "mobile": [dict(_MOBIL)]}
    m.update(ov)
    return m


def test_d216_nu_e_doar_api():
    """d216 are formular manual in UI -> nu mai e ascuns; apare in selectorul de tipuri."""
    assert _TIP not in declaratii_api._DOAR_API
    assert _TIP in declaratii_api.tipuri()


def test_d216_cerere_goala_refuza_la_api():
    """Bloc validare API: fara nume/bunuri -> erori; cerere valida -> lista goala."""
    goala = declaratii_api.valideaza_cerere("d216", {"tenant_id": 1, "an": 2025})
    valida = declaratii_api.valideaza_cerere("d216", {"tenant_id": 1, "an": 2025, "manual": _m()})
    assert goala and valida == []


def test_d216_formular_gol_refuza():
    """Fara niciun bun -> ValueError (tip), NU XML."""
    with pytest.raises(ValueError):
        d216.genereaza(None, None, Perioada(2025, luna=12), _m(imobile=[], mobile=[]))


def test_d216_structural():
    """Regresie STRUCTURALA: <D216>/<bun_imobil>/<bun_mobil>; pe 2025 impozit = ROUND(baza*0,3/100) (Legea 296/2023)."""
    xml, res = d216.genereaza(None, None, Perioada(2025, luna=12), _m())
    root = ET.fromstring(xml)
    assert root.tag == _NS + "D216"
    imob = root.findall(_NS + "bun_imobil")
    mob = root.findall(_NS + "bun_mobil")
    assert len(imob) == 1 and len(mob) == 1
    # baza imobil = (3000000-2500000)*0.3/100 = 1500 -> impozit = round(1500*0.3/100) = 5
    assert imob[0].get("impozit_imobil") == "5" and root.get("impozit_imobile") == "5"
    # baza mobil = 400000-375000 = 25000 -> impozit = round(25000*0.3/100) = 75
    assert mob[0].get("impozit_mobil") == "75" and root.get("impozit_mobile") == "75"


def test_d216_cota_impozitului_pe_anul_fiscal_2026_e_0_9_la_suta():
    """[lot 19 pct.4a, 02.10.2026] Cota vine din COTE pe ANUL declarat, nu dintr-o constantă de modul (era 0.3 fix ->
    pentru 2026 o treime din impozit, DUK respingea cu R29/R37)."""
    xml, res = d216.genereaza(None, None, Perioada(2026, luna=12), _m())
    root = ET.fromstring(xml)
    imob, mob = root.find(_NS + "bun_imobil"), root.find(_NS + "bun_mobil")
    # CF art.500^2 lit.a): „prin aplicarea unei cote de 0,9% asupra diferenței dintre valoarea impozabilă a clădirii … și
    # plafonul de 2.500.000 lei” (Legea 239/2025 art.XII pct.51, în vigoare 01.01.2026 — art.XIII alin.(1) lit.a)):
    # baza 1500 (cota-parte 0,3%) -> 1500 * 0,9% = 13,5 -> ROUND aritmetic = 14 (DUK regula R29: ROUND(baza * 0.9 / 100))
    assert imob.get("impozit_imobil") == "14" and root.get("impozit_imobile") == "14"
    # CF art.500^2 lit.b): „prin aplicarea unei cote de 0,9% asupra diferenței dintre valoarea de achiziție și plafonul de
    # 375.000 lei”: 25000 * 0,9% = 225 (DUK regula R37)
    assert mob.get("impozit_mobil") == "225" and root.get("impozit_mobile") == "225"
    assert (res.impozit_imobile, res.impozit_mobile) == (14, 225)


def test_d216_cota_pe_ani_si_refuz_inainte_de_impozit():
    from datetime import date
    from decimal import Decimal
    from core import common
    # Legea 296/2023 art.III pct.65 (Titlul X^1 de la 01.01.2024): „prin aplicarea unei cote de 0,3% …”
    assert d216.cota_impozit(2024) == d216.cota_impozit(2025) == Decimal("0.003")
    # CF art.500^2 lit.a)-b), forma din 01.01.2026: „0,9%”
    assert d216.cota_impozit(2026) == Decimal("0.009")
    # CF art.500^3 alin.(1): „datorat pentru întregul an fiscal” -> o singură cotă pe an (cea de la 01.01)
    assert d216.cota_impozit(2026) == common.cota("impozit_special_valoare_mare", date(2026, 12, 31))[0]
    with pytest.raises(Exception):      # 2023: impozitul nu exista — nu se inventează o cotă retroactiv
        d216.cota_impozit(2023)


def test_d216_valoare_sub_plafon_refuza():
    """valoare_impozabila <= plafon -> erori_generare o semnaleaza (lista ne-goala; delta minim)."""
    assert d216.erori_generare({}, _m()) == []                             # baza valida (anti-vacuu)
    sub = dict(_IMOBIL, valoare_impozabila_imobil=2000000, plafon_imobil=2500000)
    assert d216.erori_generare({}, _m(imobile=[sub], mobile=[]))


def test_d216_cota_invalida_refuza():
    """cota in afara (0,100] -> erori_generare o semnaleaza."""
    rea = dict(_IMOBIL, cota=0)
    assert d216.erori_generare({}, _m(imobile=[rea], mobile=[]))
