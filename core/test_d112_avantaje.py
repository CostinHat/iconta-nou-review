# -*- coding: utf-8 -*-
"""Sectiunea 8.3 avantaje D112 (C4): bilete de valoare defalcate pe tip (E3_10/72/74/75 + E3_60).
Campania "implementarile ramase", punctul 2. Structura oficiala D112 (d112_struct_anaf.txt:6293-6332)."""
import re
from core import d112

_PROF = {"cui": "RO14399840", "nume": "TEST SRL", "caen": "6201", "judet": "B",
         "declarant_nume": "POP", "declarant_prenume": "ION", "declarant_functie": "ADMIN"}


def _sal(**kw):
    base = {"brut": 3000, "cas": 750, "cass": 300, "impozit": 195, "cass_tichete": 0,
            "impozit_tichete": 0, "tichete_nominal": 0, "e83_masa": 0, "e83_vacanta": 0,
            "e83_cultural": 0, "e83_cresa": 0, "ore_zi": 8, "cm": [], "zile_cm": 0,
            "cnp": "1900101410011", "nume": "POPESCU", "prenume": "ION", "data_angajare": "2020-01-15"}
    base.update(kw)
    return base


def test_sectiunea_83_avantaje_defalcata_pe_tip():
    """Sectiunea 8.3: E3_60 = suma bilete, cu componente E3_10 masa / E3_72 cresa / E3_74 cultural / E3_75
    vacanta. Emisa DOAR cand exista avantaje; salariatii fara bilete raman neschimbati (fara E3_60)."""
    sal = _sal(impozit=240, cass_tichete=20, impozit_tichete=45, tichete_nominal=200,
               e83_masa=200, e83_cultural=150, e83_cresa=100)
    xml, _ = d112._d112_genereaza(_PROF, [sal], 2026, 6)
    e3 = re.search(r'<asiguratE3[^>]*/>', xml).group(0)
    # E3_60 = 200 (masa) + 100 (cresa) + 150 (cultural) = 450
    assert 'E3_60="450"' in e3, e3
    assert 'E3_10="200"' in e3 and 'E3_72="100"' in e3 and 'E3_74="150"' in e3, e3
    assert 'E3_75=' not in e3   # vacanta 0 -> componenta omisa
    # E3_60 >= suma componentelor emise (structura oficiala)
    comp = sum(int(v) for v in re.findall(r'E3_(?:10|72|73|74|75)="(\d+)"', e3))
    assert int(re.search(r'E3_60="(\d+)"', e3).group(1)) >= comp

    # fara bilete -> nicio sectiune 8.3 (salariat neschimbat)
    xml0, _ = d112._d112_genereaza(_PROF, [_sal()], 2026, 6)
    assert "E3_60" not in xml0


def test_sectiunea_83_valida_pe_duk():
    """Proba DUK: D112 cu sectiunea 8.3 (masa+cultural+cresa) e VALID pe validatorul instalat. E3_8 nu se
    atinge (ar rupe DUK regula S111 E1_1=Suma(E3_8) - probat: scenariul E3_8+=nominal e respins)."""
    import pytest
    from core import duk
    if not duk.poate_valida("d112"):
        pytest.skip("DUK d112 indisponibil")
    sal = _sal(impozit=240, cass_tichete=20, impozit_tichete=45, tichete_nominal=200,
               e83_masa=200, e83_cultural=150, e83_cresa=100)
    xml, _ = d112._d112_genereaza(_PROF, [sal], 2026, 6)
    r = duk.valideaza(xml, "d112", an=2026)
    assert r["stare"] == "valid", "DUK a respins D112 cu 8.3: %s" % r["erori"]
