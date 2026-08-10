# -*- coding: utf-8 -*-
"""Gardian J1/T7 (TURA 4): DEDUCEREA (suma_ded) in D710 - inchidere gol RECONCILIERE.

GOLUL (dovedit): suma_ded_i/_c era LISTATA in docstring ca input acceptat dar NICIODATA
citita de calcul_d710 - ObligatieRect emitea suma_plata=suma_dat indiferent. O rectificare
cu deducere (contabilul corecteaza o deducere) producea o declaratie DUK-VALIDA dar ARITMETIC
GRESITA: deducerea disparea tacit, suma_plata ramanea = suma_dat. Nimeni nu prindea eroarea.

REZOLVARE per sursa (Zona 710, poz.11a + Modele de completare) + dovedit pe DUK (09.08.2026):
  - cod 121 (micro, model 9#): suma_ded E parte din model -> IMPLEMENTATA. suma_plata =
    Maximum(suma_dat - suma_ded, 0); suma_ded_I/_C emise; totalPlata_A include suma_ded
    (DUK regula R11b). suma_rest nu se completeaza.
  - cod 103 (profit, model 8#): suma_ded "nu se completeaza" (DUK regula R14-21); modelul
    foloseste suma_redu, nu suma_ded -> o suma_ded furnizata e BLOCATA cu ValueError, ca sa nu
    se emita niciodata o declaratie respinsa/gresita.

Fiecare test apara o afirmatie dovedita pe validatorul oficial DUK - vezi core/d710.py.
"""
import re
import pytest
from core.d710 import calcul_d710 as _c, build_xml
from core.common import Perioada
import core.duk as duk

_DUK = duk.poate_valida("d710")


def _prof():
    return {"cui": "456789123", "nume": "TEST RECTIFICATIVA SRL",
            "adresa": "Str. Test nr.1 Bucuresti Sector 1"}


def _gen(obl, luna=3):
    res = _c(_prof(), Perioada(2025, luna=luna), {}, {"obligatii": obl})
    return res, build_xml(res)


def _linie_obl(xml):
    return [l for l in xml.split("\n") if "<obligatie" in l][0]


# ---- MUTATIE: suma_ded nu mai e abandonata tacit (cod 121, model 9#) ----

def test_mutatie_suma_ded_aplicata_nu_abandonata_tacit():
    """MUTATIE J1/T7. cod 121 cu suma_ded>0.
    BEFORE (bug): suma_ded ignorata -> suma_plata=suma_dat, niciun atribut suma_ded (declaratie
    aritmetic gresita, DUK-valida). AFTER: suma_plata = suma_dat - suma_ded pe fiecare latura,
    suma_ded_I/_C emise. Un test care ar trece pe codul vechi (suma_plata==suma_dat) pica acum."""
    res, xml = _gen([{"cod_oblig": "121", "suma_dat_i": 1000, "suma_dat_c": 1000,
                      "cota": "1", "suma_ded_i": 200, "suma_ded_c": 300}])
    o = res.obligatii[0]
    # deducerea NU mai e abandonata: plata = dat - ded (nu mai = dat)
    assert o.suma_ded_i == 200 and o.suma_ded_c == 300
    assert o.suma_plata_i == 800 and o.suma_plata_c == 700
    assert o.suma_plata_i != o.suma_dat_i and o.suma_plata_c != o.suma_dat_c
    lin = _linie_obl(xml)
    assert 'suma_ded_I="200"' in lin and 'suma_ded_C="300"' in lin
    assert 'suma_plata_I="800"' in lin and 'suma_plata_C="700"' in lin


def test_totalPlata_A_include_suma_ded_R11b():
    """DUK regula R11b (Zona 710 poz.11a): totalPlata_A = Σ latura (suma_dat + suma_ded + suma_plata).
    Cu ded: (1000+200+800)+(1000+300+700)=4000. Fara suma_ded in suma de control, DUK respinge R11b."""
    res, xml = _gen([{"cod_oblig": "121", "suma_dat_i": 1000, "suma_dat_c": 1000,
                      "cota": "1", "suma_ded_i": 200, "suma_ded_c": 300}])
    assert res.total_plata_a == 4000
    emis = int(re.search(r'totalPlata_A="(\d+)"', xml).group(1))
    assert emis == res.total_plata_a == 4000


def test_deducere_pe_o_singura_latura():
    """Deducere doar pe latura corectata (ded_i=0, ded_c=300): plata_i=dat_i, plata_c=dat_c-ded_c.
    Perechea suma_ded_I/_C se emite impreuna (0 pe latura fara deducere, acceptat de DUK)."""
    res, xml = _gen([{"cod_oblig": "121", "suma_dat_i": 1000, "suma_dat_c": 1000,
                      "cota": "1", "suma_ded_c": 300}])
    o = res.obligatii[0]
    assert o.suma_plata_i == 1000 and o.suma_plata_c == 700
    lin = _linie_obl(xml)
    assert 'suma_ded_I="0"' in lin and 'suma_ded_C="300"' in lin
    assert res.total_plata_a == (1000 + 0 + 1000) + (1000 + 300 + 700) == 4000


# ---- BASELINE (fara deducere) NESCHIMBAT ----

def test_baseline_fara_deducere_neschimbat():
    """Cazul dominant (fara deducere): suma_plata = suma_dat, NICIUN atribut suma_ded emis,
    totalPlata_A = 2*(dat_i+dat_c) = 500 - identic cu comportamentul anterior extinderii."""
    res, xml = _gen([{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150, "cota": "1"}])
    o = res.obligatii[0]
    assert o.suma_plata_i == o.suma_dat_i == 100
    assert o.suma_plata_c == o.suma_dat_c == 150
    assert "suma_ded" not in xml
    assert res.total_plata_a == 500


# ---- BLOCAJ (b): coduri al caror model NU prevede deducere ----

def test_cod_103_cu_deducere_blocat():
    """cod 103 (profit, model 8#): suma_ded 'nu se completeaza' (DUK regula R14-21). O suma_ded
    furnizata pe 103 e BLOCATA cu ValueError PRE-DUK - nu se emite o declaratie respinsa, nu se
    pierde deducerea tacit."""
    with pytest.raises(ValueError):
        _gen([{"cod_oblig": "103", "suma_dat_i": 1000, "suma_dat_c": 1000,
               "suma_ded_i": 200, "suma_ded_c": 300}], luna=6)
    # doar latura initiala completata -> tot blocat
    with pytest.raises(ValueError):
        _gen([{"cod_oblig": "103", "suma_dat_i": 1000, "suma_dat_c": 1000,
               "suma_ded_i": 200}], luna=6)
    # 103 FARA deducere ramane valid (model 8#: suma_plata = suma_dat)
    res, xml = _gen([{"cod_oblig": "103", "suma_dat_i": 1000, "suma_dat_c": 1000}], luna=6)
    assert "suma_ded" not in xml
    assert res.obligatii[0].suma_plata_c == 1000


def test_cod_121_deducere_peste_datorat_blocat():
    """cod 121 (model 9#): suma_rest = 0 (micro nu restituie excedentul). O deducere care depaseste
    suma_dat pe o latura ar clampa plata la 0 si ar pierde tacit excedentul -> BLOCATA cu ValueError."""
    with pytest.raises(ValueError):
        _gen([{"cod_oblig": "121", "suma_dat_i": 800, "suma_dat_c": 800, "cota": "1",
               "suma_ded_i": 1000, "suma_ded_c": 100}])
    with pytest.raises(ValueError):
        _gen([{"cod_oblig": "121", "suma_dat_i": 800, "suma_dat_c": 800, "cota": "1",
               "suma_ded_c": 900}])
    # deducere egala cu datoratul (plata=0) e permisa (nu depaseste)
    res, _ = _gen([{"cod_oblig": "121", "suma_dat_i": 800, "suma_dat_c": 800, "cota": "1",
                    "suma_ded_i": 800, "suma_ded_c": 800}])
    assert res.obligatii[0].suma_plata_i == 0 and res.obligatii[0].suma_plata_c == 0


def test_suma_ded_nenumerica_sau_negativa_mesaj_clar():
    """suma_ded nenumerica / negativa -> ValueError clar (camp + valoare), ca la suma_dat (nu stacktrace)."""
    with pytest.raises(ValueError):
        _gen([{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150, "cota": "1", "suma_ded_c": "abc"}])
    with pytest.raises(ValueError):
        _gen([{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150, "cota": "1", "suma_ded_c": -5}])


# ---- DUK (judecatorul final ANAF) - gated ----

@pytest.mark.skipif(not _DUK, reason="validatorul D710 nu e instalat in pachetul DUK")
def test_duk_deducere_121_valida_before_after():
    """AFTER (deducere aplicata corect) = DUK-valid. BEFORE (suma_ded abandonat, suma_plata=suma_dat
    peste o declaratie cu deducere reala) = tot DUK-valid DAR aritmetic gresit - exact golul: DUK nu
    poate prinde eroarea aritmetica, garda din motor trebuie sa o previna."""
    res, xml = _gen([{"cod_oblig": "121", "suma_dat_i": 1000, "suma_dat_c": 1000,
                      "cota": "1", "suma_ded_i": 200, "suma_ded_c": 300}])
    r = duk.valideaza(xml, "d710", an=2026, luna=8, timeout=110)
    assert r["stare"] == "valid", "DUK a gasit erori pe deducerea corecta: %s" % r["erori"]

    # reconstruim declaratia BUGGY (suma_plata=suma_dat, fara suma_ded) si aratam ca DUK o accepta:
    # DUK regula R11b se satisface pt ca e o declaratie fara deducere consistenta cu ea insasi -
    # deducerea reala a contabilului (200/300) e pur si simplu absenta. Aritmetic gresita, DUK-oarba.
    buggy = re.sub(r'\s*suma_ded_I="\d+" suma_ded_C="\d+"', '', xml)
    buggy = buggy.replace('suma_plata_I="800"', 'suma_plata_I="1000"').replace('suma_plata_C="700"', 'suma_plata_C="1000"')
    buggy = re.sub(r'totalPlata_A="\d+"', 'totalPlata_A="4000"', buggy)
    rb = duk.valideaza(buggy, "d710", an=2026, luna=8, timeout=110)
    assert rb["stare"] == "valid", "declaratia buggy (deducere abandonata) chiar e DUK-valida (gol confirmat)"


@pytest.mark.skipif(not _DUK, reason="validatorul D710 nu e instalat in pachetul DUK")
def test_duk_baseline_fara_deducere_valid():
    _, xml = _gen([{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150, "cota": "1"}])
    assert duk.valideaza(xml, "d710", an=2026, luna=8, timeout=110)["stare"] == "valid"
