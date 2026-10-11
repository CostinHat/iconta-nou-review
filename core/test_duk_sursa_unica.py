# -*- coding: utf-8 -*-
"""GARD — validatorul DUK se rulează numai prin `core/duk.py` (deficiența 222, comanda Costin 10.10.2026: „mesajul de confirmare apare
ca o casetă brută «ok»”). Bilanțul (S1005/S1003) rula `DUKIntegrator.jar` separat și trimitea conținutul fișierului DUK — „ok” la
un fișier valid — ca „erori”; ecranul îl punea într-o casetă sub „Validare fără erori”. `duk.valideaza` normalizează „ok”, tratează
rularea eșuată ca gri și păstrează un singur loc de schimbat la o versiune nouă a pachetului ANAF.

Gardul: niciun modul din aplicație (în afară de `core/duk.py`) nu pornește un proces cu `DUKIntegrator.jar` — pe AST: apelurile
`subprocess.*` / `Popen` cu un argument constant care numește jar-ul. Ecranul (nicio casetă „ok” sub verdict) e în plasă:
`e2e_comanda_1010.py::test_def_222_…`."""
import ast
import glob
import os

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PROCES = {"run", "Popen", "check_output", "check_call", "call"}


def _rulari_duk(cale):
    for n in ast.walk(ast.parse(open(cale, encoding="utf-8").read())):
        if isinstance(n, ast.Call) and getattr(n.func, "attr", getattr(n.func, "id", None)) in _PROCES:
            consts = {c.value for a in n.args for c in ast.walk(a) if isinstance(c, ast.Constant) and isinstance(c.value, str)}
            if {c for c in consts if c.endswith("DUKIntegrator.jar")}:
                yield n.lineno


def test_validatorul_se_ruleaza_numai_prin_core_duk():
    """MUTAȚIE: rularea directă `subprocess.run(["java", "-jar", "DUKIntegrator.jar", …])` pusă înapoi în `s1005_valideaza` -> pică."""
    fisiere = [f for f in glob.glob(os.path.join(_RAD, "core", "*.py")) + [os.path.join(_RAD, "main.py")]
               if not os.path.basename(f).startswith("test_")]
    assert len(fisiere) > 100, len(fisiere)                                  # anti-vacuu: aplicația e acolo
    gasite = ["%s:%d" % (os.path.relpath(f, _RAD), ln) for f in fisiere if not f.endswith(os.path.join("core", "duk.py"))
              for ln in _rulari_duk(f)]
    assert gasite == [], gasite
    assert list(_rulari_duk(os.path.join(_RAD, "core", "duk.py"))), "anti-vacuu: scanul recunoaște rularea din core/duk.py"
