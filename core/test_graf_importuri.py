# -*- coding: utf-8 -*-
"""GARD — importurile din `core` se citesc din arborele de sintaxă, nu cu regex pe un rând (02.10.2026).

Clasa: `graf_temei._importuri` citea `from core.X import …` cu un regex pe UN rând. `from core.d394 import (` urmat de
nume pe rândurile următoare nu era văzut, apelul `build_xml(...)` din test_d394 rămânea nerezolvat și cădea pe
rezolvarea pe NUME — la toate cele 49 de `build_xml` din core/. Când cota D216 a trecut prin `cota()` (lot 19), trei
bife D394 (`tipuri operatiune (pct.215)`, `rezumat1 campuri complete`, `totalPlata_A (R17)`) au părut „pe o bază
schimbată” — fals: nu depind de D216. Același cititor pe un rând era în `scripts/scan_axa_garzi.py` (modulele
importate de o gardă), iar `test_golden_xsd` căuta importul ca subșir. 26 de fișiere au importuri în paranteze.

CE FACE IMPOSIBIL: (1) un import în paranteze nevăzut de graf (testele de comportament de mai jos); (2) un al doilea
cititor de importuri `core` făcut cu regex — orice șir din core/ sau scripts/ care descrie `from\\s+core` /
`import\\s+core` ca expresie regulată oprește poarta (cititorul unic: `graf_temei.importuri_core`).
LIMITĂ: nu vede un cititor scris altfel decât cu `\\s` (ex. `" import "` + split); restul e disciplină de review.
"""
import ast
import glob
import os

from core import graf_temei as gt

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_importul_in_paranteze_pe_mai_multe_randuri_e_vazut():
    src = ("from core.d394 import (\n    COTE,\n    calcul_d394, build_xml as bx,\n)\n"
           "from core import (\n    duk,\n    d216 as _d,\n)\nimport core.d300 as t\n"
           "def f():\n    from core.common import cota\n")
    alias, nume = gt.importuri_core(src)
    assert alias == {"duk": "duk.py", "_d": "d216.py", "t": "d300.py"}
    assert nume == {"COTE": ("d394.py", "COTE"), "calcul_d394": ("d394.py", "calcul_d394"),
                    "bx": ("d394.py", "build_xml"), "cota": ("common.py", "cota")}


def test_testul_d394_ajunge_la_build_xml_din_d394_nu_la_toate():
    # instanța care a deschis clasa: înainte, apelul se rezolva la 49 de build_xml (inclusiv d216.py::build_xml)
    apeluri = gt.apeluri_din("core/test_d394.py", "test_totalPlata_A_R17_sursa_unica_si_probat_pe_validator")
    assert {a for a in apeluri if a.endswith("::build_xml")} == {"d394.py::build_xml"}


#: un regex care citește importuri `core` — scris ca șir sursă (raw), deci cu backslash literal
_TIPARE_REGEX = ("from\\s+core", "import\\s+core", "core\\s+import")


def _regex_de_import(cale):
    try:
        arb = ast.parse(open(cale, encoding="utf-8").read())
    except (SyntaxError, UnicodeDecodeError):
        return []
    return [n.lineno for n in ast.walk(arb)
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and any(t in n.value for t in _TIPARE_REGEX)]


def test_niciun_alt_cititor_de_importuri_core_cu_regex():
    fisiere = glob.glob(os.path.join(_RAD, "core", "*.py")) + glob.glob(os.path.join(_RAD, "scripts", "*.py"))
    gasite = {os.path.relpath(f, _RAD): l for f in fisiere
              if os.path.basename(f) != "test_graf_importuri.py" and (l := _regex_de_import(f))}
    assert gasite == {}, "importurile core se citesc cu graf_temei.importuri_core (AST), nu cu regex: %s" % gasite
