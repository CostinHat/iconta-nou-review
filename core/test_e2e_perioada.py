# -*- coding: utf-8 -*-
"""GARD — perioada declarației în plasa e2e (10.10.2026). `e2e_bloc_d._genereaza` completa numai „Lună”: după C2 (D406 trimestrial la
neplătitor) firma nouă a testului 136 a arătat „Trimestru”, iar testul a generat în tăcere trimestrul implicit al ecranului (T4/2026)
în locul lunii cerute (09/2026) — plasa a picat pe o cerere pe care n-o făcuse. Clasa: un helper care sare peste selectorul afișat
generează altă perioadă decât cea cerută. Trei helperi (blocurile c, d, e) și două alegeri directe aveau aceeași formă.

Acum perioada se alege într-un singur loc, `frontend_test/e2e/conftest.alege_perioada`, care urmează selectorul afișat și pică dacă
lipsește. Gardul: (1) niciun fișier al plasei nu mai completează `#dec-an` / `#dec-luna` / `#dec-trim` pe lângă el; (2) helperul
alege luna, trimestrul lunii, și pică fără selector."""
import ast
import glob
import importlib.util
import os
import re
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_E2E = os.path.join(_RAD, "frontend_test", "e2e")
_SELECTOR = re.compile(r"#dec-(luna|trim|an)\b")
_ACTIUNI = {"select_option", "fill", "dispatch_event"}


def _apeluri(cale):
    """(numele apelat, primul argument constant sau None) pentru fiecare apel din fișier — pe AST, nu pe text."""
    for n in ast.walk(ast.parse(open(cale, encoding="utf-8").read())):
        if isinstance(n, ast.Call):
            nume = n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", None)
            arg = n.args[0] if n.args else None
            consts = [c.value for c in ast.walk(arg) if isinstance(c, ast.Constant) and isinstance(c.value, str)] if arg else []
            yield nume, consts, n.lineno


def test_perioada_se_alege_numai_prin_helper():
    """MUTAȚIE: `pg.select_option("#dec-luna", "7")` înapoi în e2e_bloc_e -> pică."""
    fisiere = sorted(glob.glob(os.path.join(_E2E, "e2e_*.py")))
    assert len(fisiere) >= 8, fisiere                                    # anti-vacuu: plasa e acolo (9 la 10.10.2026)
    directe, prin_helper = [], 0
    for f in fisiere:
        for nume, consts, linie in _apeluri(f):
            if nume in _ACTIUNI and any(_SELECTOR.search(c) for c in consts):
                directe.append("%s:%d" % (os.path.basename(f), linie))
            prin_helper += nume == "alege_perioada"
    assert directe == [], directe
    assert prin_helper >= 4, prin_helper                                 # anti-vacuu: helperul e folosit


class _Pg:
    def __init__(self, selectoare):
        self.sel, self.ales = set(selectoare), {}

    def locator(self, s):
        return type("L", (), {"count": lambda _s: int(s in self.sel)})()

    def fill(self, s, v):
        self.ales[s] = v

    def select_option(self, s, v):
        self.ales[s] = v

    def dispatch_event(self, s, e):
        pass


@pytest.fixture
def alege():
    """conftest-ul plasei, încărcat sub alt nume (`conftest` e deja cel din core/)."""
    sys.path.insert(0, _E2E)                                             # importul lui `curatenie`
    try:
        spec = importlib.util.spec_from_file_location("e2e_conftest_perioada", os.path.join(_E2E, "conftest.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        yield m.alege_perioada
    finally:
        sys.path.remove(_E2E)


def test_helperul_urmeaza_selectorul_afisat_si_pica_fara_el(alege):
    """MUTAȚIE: ramura `#dec-trim` scoasă din `alege_perioada` -> trimestrul nu se mai alege -> pică."""
    lunar = _Pg({"#dec-luna"})
    alege(lunar, 2026, 9)
    assert lunar.ales == {"#dec-an": "2026", "#dec-luna": "9"}, lunar.ales
    trim = _Pg({"#dec-trim"})
    alege(trim, 2026, 9)
    assert trim.ales == {"#dec-an": "2026", "#dec-trim": "3"}, trim.ales        # 09 -> T3, nu trimestrul implicit al ecranului
    explicit = _Pg({"#dec-trim"})
    alege(explicit, 2026, trim=4)
    assert explicit.ales["#dec-trim"] == "4"
    with pytest.raises(AssertionError, match="fără selector"):
        alege(_Pg(set()), 2026, 9)
    anual = _Pg(set())
    alege(anual, 2025)                                                        # anuală: numai anul
    assert anual.ales == {"#dec-an": "2025"}


_FRONT = os.path.join(_RAD, "frontend_test")
_TIP = re.compile(r"#dec-tip\b")


def _alegeri_directe_ale_tipului(cale):
    """`select_option("…#dec-tip", <valoare>)` pe AST: alegerea pe VALOARE (fără `label=` / `index=`, care aleg rândul afișat)."""
    for n in ast.walk(ast.parse(open(cale, encoding="utf-8").read())):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "select_option" and n.args:
            consts = [c.value for c in ast.walk(n.args[0]) if isinstance(c, ast.Constant) and isinstance(c.value, str)]
            if any(_TIP.search(c) for c in consts) and len(n.args) > 1:
                yield n.lineno


def test_tipul_declaratiei_se_alege_numai_prin_helper():
    """[deficiența 301, comanda Costin 17.10.2026 7.2] „Alte declarații” e pliată: un tip nedatorat nu e în listă până la clic. Alegerea
    directă a așteptat o opțiune care nu era acolo (scanul de text, 17.10.2026: 5 ecrane „neatinse”). Tipul se alege numai prin
    `frontend_test/declaratie_tip.alege_tipul`, în plasă, în uneltele vizuale și în sonde.
    MUTAȚIE: `pg.select_option("#dec-tip", tip)` înapoi în `e2e_bloc_e._declaratie` -> pică."""
    fisiere = [f for f in sorted(glob.glob(os.path.join(_FRONT, "**", "*.py"), recursive=True))
               if os.path.basename(f) != "declaratie_tip.py"]
    assert len(fisiere) >= 50, len(fisiere)                               # anti-vacuu: plasa, uneltele și sondele
    directe = ["%s:%d" % (os.path.relpath(f, _RAD), ln) for f in fisiere for ln in _alegeri_directe_ale_tipului(f)]
    assert directe == [], directe
    folosiri = sum(open(f, encoding="utf-8").read().count("alege_tipul(") for f in fisiere)
    assert folosiri >= 10, folosiri                                       # anti-vacuu: helperul e folosit


class _PgTip:
    def __init__(self, datorate, alte):
        self.dat, self.alte, self.deschis, self.ales = set(datorate), set(alte), False, None

    def _vizibile(self):
        return self.dat | (self.alte if self.deschis else set())

    def locator(self, s):
        m = re.search(r"value='([^']+)'", s)
        n = int(m.group(1) in self._vizibile()) if m else int(s.endswith("#dec-alte"))
        return type("L", (), {"count": lambda _s: n})()

    def get_attribute(self, s, a):
        return "true" if self.deschis else "false"

    def click(self, s):
        self.deschis = not self.deschis

    def wait_for_selector(self, s, **k):
        pass

    def select_option(self, s, v):
        self.ales = v


def test_helperul_deschide_alte_declaratii_numai_cand_trebuie():
    """MUTAȚIE: clicul pe „Alte declarații” scos din `alege_tipul` -> D390 nedatorat nu se mai alege -> pică."""
    sys.path.insert(0, _FRONT)
    try:
        from declaratie_tip import alege_tipul
    finally:
        sys.path.remove(_FRONT)
    pg = _PgTip({"d300"}, {"d390"})
    alege_tipul(pg, "d300")
    assert (pg.ales, pg.deschis) == ("d300", False)                       # datorată: lista rămâne pliată
    alege_tipul(pg, "d390")
    assert (pg.ales, pg.deschis) == ("d390", True)
    with pytest.raises(AssertionError, match="nici în „Alte declarații”"):
        alege_tipul(_PgTip({"d300"}, set()), "d200")
