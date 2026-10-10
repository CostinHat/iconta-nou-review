# -*- coding: utf-8 -*-
"""GARDA instrumentului de inventar al registrului unic de parametri fiscali (`core/scan_registru.py`).

Comanda Costin 08.10.2026 (registrul unic, pct.2): „Inventarul se numără, nu se estimează.” Instrumentul e măsurătoarea pe care se
sprijină migrarea și gardul interdicției 1 — deci el însuși se calibrează pe modurile lui de eșec:
  * literalul din chiar declarația lui `COTE` nu e „în afara registrului”;
  * un apel `ancoreaza` întins pe mai multe rânduri sau chemat printr-un alias (`ancoreaza as _anc`, d212) e „ancorat”, nu „sursat”;
  * clasele E / C ale `scan_constante` ajung „proza” / „nesursat”, iar nomenclatorul și precizia nu se numără.
"""
from core import scan_registru as sr


def test_CALIBRARE_felul_fiecarui_rand():
    """MUTAȚIE: intervalul lui COTE ignorat în `fel` -> literalul registrului numărat „sursat_in_modul” -> pică."""
    interval = (100, 200)
    assert sr.fel({"cls": "A", "f": "common.py", "l": 150}, interval) == "registru"
    assert sr.fel({"cls": "A", "f": "common.py", "l": 250}, interval) == "sursat_in_modul"
    assert sr.fel({"cls": "E", "f": "x.py", "l": 1}, interval) == "proza"
    assert sr.fel({"cls": "C", "f": "x.py", "l": 1}, interval) == "nesursat"
    assert sr.fel({"cls": "B", "f": "x.py", "l": 1}, interval) is None
    assert sr.fel({"cls": "D", "f": "x.py", "l": 1}, interval) is None


def test_CALIBRARE_ancoreaza_prin_alias_si_pe_mai_multe_randuri():
    """d212 cheamă `ancoreaza as _anc`, cu literalul pe alt rând decât numele. MUTAȚIE: aliasul ignorat -> d212 fără ancorate -> pică."""
    assert sr._apeluri_ancoreaza("d212.py"), "apelurile prin alias nu se văd"
    assert any(b > a for a, b in sr._apeluri_ancoreaza("casa.py")), "apelurile pe mai multe rânduri nu se văd ca interval"


def test_ANTI_VACUU_registrul_si_fiecare_fel_se_vad():
    r = sr.inventar()
    assert r["registru"]["chei"] > 10 and r["registru"]["intrari"] >= r["registru"]["chei"]
    assert all(r["total"][f] > 0 for f in ("ancorat", "proza", "nesursat")), r["total"]
