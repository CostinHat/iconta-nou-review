# -*- coding: utf-8 -*-
"""Gard T6 (CATALOG_INVALIDITATE.md, D100 #12): denumirea/adresa firmei care depaseste limita
oficiala C(n) e trunchiata TACIT de text_anaf -> pierdere de date silentioasa. App-ul trebuie sa
emita un avertisment NON-blocant (res.avertismente) care numeste campul.

FAIL pe HEAD 8b74ccb: build_xml trunchiaza prin _t(...) fara sa semnaleze -> res.avertismente ramane gol.
PASS dupa reparatie: build_xml adauga avertismentul cand valoarea reala depaseste limita."""
from core import d100
from core.common import LIMITE_TEXT_ANAF as _LIM

_LIM_DEN = _LIM["d100"]["den"]        # 200
_LIM_ADR = _LIM["d100"]["adresa"]     # 1000


def _res(nume, adresa):
    # profil COMPLET (cu declarant) ca res.avertismente sa contina DOAR eventualul avert de trunchiere,
    # nu si avertismentul de declarant lipsa (thread 3, 17.08.2026) - testul e despre trunchiere.
    prof = {"cui": "301111003", "nume": nume, "adresa": adresa,
            "declarant_nume": "POPESCU", "declarant_functie": "ADMINISTRATOR"}
    # o obligatie micro simpla ca build_xml sa aiba ce emite
    return d100.calcul_d100(prof, 2026, 12, [{"cod_oblig": "121", "suma_dat": 100, "cota": "1"}])


def test_den_si_adresa_normale_fara_avertisment():
    res = _res("ALFA MICRO SRL", "Str. Test 1 Bucuresti")
    d100.build_xml(res)
    assert res.avertismente == [], res.avertismente


def test_denumire_prea_lunga_avertizeaza_si_numeste_campul():
    nume = "A" * (_LIM_DEN + 5)
    res = _res(nume, "Str. Test 1")
    xml = d100.build_xml(res)
    assert any("denumirea firmei" in a and "trunchiata" in a for a in res.avertismente), res.avertismente
    # avertismentul e NON-blocant: XML se genereaza, dar den din XML e taiat la limita
    assert ('den="%s"' % ("A" * _LIM_DEN)) in xml
    assert ("A" * (_LIM_DEN + 1)) not in xml


def test_adresa_prea_lunga_avertizeaza_si_numeste_campul():
    adresa = "B" * (_LIM_ADR + 3)
    res = _res("ALFA MICRO SRL", adresa)
    d100.build_xml(res)
    assert any("adresa domiciliului fiscal" in a and "trunchiata" in a for a in res.avertismente), res.avertismente


def test_avertismentul_da_limita_reala():
    res = _res("A" * (_LIM_DEN + 1), "adr")
    d100.build_xml(res)
    e = [a for a in res.avertismente if "denumirea firmei" in a][0]
    assert str(_LIM_DEN) in e         # numeste limita oficiala (200), nu una inventata
