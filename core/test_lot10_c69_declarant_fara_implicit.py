# -*- coding: utf-8 -*-
"""[C69, lotul 10 — clasa „valoare inventată pe documentul ANAF în loc de blocaj”, restul găsit de N / N2] GARDA pe generatoare.

Cele opt declarații cu declarant (D100, D101, D112, D205, D300, D301, D390, D394) blochează lipsa lui prin `firma_profil_api.erori_declarant`
înaintea lui `build_xml` (R101). Fallback-urile `or "ADMINISTRATOR"` / `or "-"` din `build_xml` erau cod mort — dar un apelant direct al lui
`build_xml` (teste, probe, un drum nou) ar fi primit un XML cu declarant inventat. S-au scos, împreună cu avertismentele „se trece implicit
"ADMINISTRATOR"”, care nu se mai puteau declanșa. D112 punea „-” la prenumele asiguratului; structura ANAF (anaf_surse/d112_struct_anaf.txt:3167:
„prenume Prenume C(75) DA  ERR : daca cnp is not null : prenume”) îl cere -> blocaj numit.
MUTAȚII: `or "ADMINISTRATOR"` repus în `d100.build_xml` -> primul test pică; blocajul prenumelui scos din `d112.genereaza` -> al doilea pică.
"""
import io
import os
import re

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATOARE = ("d100", "d101", "d112", "d205", "d300", "d301", "d390", "d394", "d101g", "d710")


def test_niciun_generator_nu_inventeaza_declarantul():
    rele = {}
    for g in GENERATOARE:
        s = io.open(os.path.join(_RAD, "core", g + ".py"), encoding="utf-8").read()
        gasite = re.findall(r'declarant_\w+"\)\s*or\s*(?:\w+\s*or\s*)?"(?:ADMINISTRATOR|-)"', s) + re.findall(r'se trece implicit', s)
        if gasite:
            rele[g] = gasite
    assert rele == {}, rele


def test_scanul_recunoaste_forma_veche():
    """Anti-vacuu: forma scoasă e exact cea pe care o caută gardul."""
    assert re.findall(r'declarant_\w+"\)\s*or\s*(?:\w+\s*or\s*)?"(?:ADMINISTRATOR|-)"',
                      '_t(prof.get("declarant_nume") or den_f or "ADMINISTRATOR", 1)') == ['declarant_nume") or den_f or "ADMINISTRATOR"']


def test_d112_refuza_salariatul_fara_prenume(monkeypatch):
    from core import d112
    from core.common import Perioada
    prof = {"cui": "14399840", "nume": "F SRL", "caen": "4711", "declarant_nume": "POP", "declarant_prenume": "ION",
            "declarant_functie": "ADMINISTRATOR"}
    sal = [{"id": 1, "nume": "IONESCU", "prenume": None, "cnp": "1800101410013"}]
    monkeypatch.setattr(d112, "pull", lambda conn, schema, perioada: (prof, sal))
    with pytest.raises(ValueError) as e:
        d112.genereaza(None, "x", Perioada(2026, luna=9))
    # structura D112: „prenume Prenume C(75) DA  ERR : daca cnp is not null : prenume”
    assert re.findall(r"^D112 nu se poate genera: (.+?) fără (\w+) în fișa salariatului", str(e.value)) == [("un salariat e", "prenume")], str(e.value)
    # salariatul numit (și numai el), lista de la finalul refuzului — CNP 1800101410013 cu cifra de control verificată
    assert str(e.value).rsplit("Stat de plată: ", 1)[1] == "IONESCU (CNP 1800101410013).", str(e.value)
