# -*- coding: utf-8 -*-
"""GARD — registrul deficiențelor (`DEFICIENTE.md`) și plasa lui (comanda Costin 09.10.2026, pct.6–9 și 13, verbatim în DECIZII).

  · numerotarea e continuă (1..ultimul, fără goluri sau dubluri) și N1–N18 sunt toate acolo: „orice deficiență nouă primește
    următorul număr din DEFICIENTE.md”;
  · starea e din mulțimea închisă; `parțial` / `nerezolvată` / `nu se aplică` spun ce lipsește (motivul);
  · `rezolvată` are commitul (existent în git) ȘI testul de capăt la capăt numit, care există ca funcție `test_def_<nr>_…` într-un
    `frontend_test/e2e/e2e_*.py`: „Un număr fără test nu e «rezolvată», e «neverificat»”;
  · invers, fiecare `test_def_<nr>_…` din plasă e al unui număr din registru (un test fără deficiență e o probă fără întrebare);
  · poarta rulează plasa (`scripts/e2e_poarta.py` în `scripts/githooks/poarta-suita`): „orice publicare la care pică o verificare a
    plasei nu se face”.
"""
import ast
import glob
import io
import os
import re
import subprocess

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STARI = {"rezolvată", "parțial", "nerezolvată", "nu se aplică", "neverificat"}
STARI_N = {"reală", "nu e reală", "neverificat"}
CU_MOTIV = {"parțial", "nerezolvată", "nu se aplică", "reală"}
NR_N = 18


def randuri(text=None):
    """[{nr, text, stare, commit, lipsa, test}] — rândurile numerotate ale tabelului."""
    text = text if text is not None else io.open(os.path.join(_RAD, "DEFICIENTE.md"), encoding="utf-8").read()
    out = []
    for ln in text.splitlines():
        m = re.match(r"^\| (\d+|N\d+) \|(.*)\|\s*$", ln)
        if not m:
            continue
        cel = [c.strip() for c in m.group(2).split("|")]
        assert len(cel) == 5, "rândul %s nu are cele 6 coloane: %r" % (m.group(1), ln[:120])
        out.append(dict(zip(("text", "stare", "commit", "lipsa", "test"), cel), nr=m.group(1)))
    return out


def plasa_e2e():
    """{nr: [cale::funcție]} — testele `test_def_<nr>_…` din plasă."""
    out = {}
    for f in sorted(glob.glob(os.path.join(_RAD, "frontend_test", "e2e", "e2e_*.py"))):
        for n in ast.walk(ast.parse(io.open(f, encoding="utf-8").read())):
            if isinstance(n, ast.FunctionDef):
                m = re.match(r"^test_def_(\d+|n\d+)_", n.name)
                if m:
                    out.setdefault(m.group(1).upper(), []).append("%s::%s" % (os.path.relpath(f, _RAD), n.name))
    return out


def test_numerotarea_e_continua_si_completa():
    """MUTAȚIE: un rând șters / un număr dublat -> pică."""
    nr = [r["nr"] for r in randuri()]
    num = [int(x) for x in nr if x.isdigit()]
    assert num == list(range(1, max(num) + 1)), "numerotarea 1..%d are goluri sau dubluri" % max(num)
    assert max(num) >= 188, "anti-vacuu: registrul trebuie să aibă cel puțin 1–188"
    assert [x for x in nr if x.startswith("N")] == ["N%d" % i for i in range(1, NR_N + 1)]


def test_starea_e_din_multimea_inchisa_si_cu_motiv():
    rele = []
    for r in randuri():
        permise = STARI_N if r["nr"].startswith("N") else STARI
        if r["stare"] not in permise:
            rele.append("%s: stare %r" % (r["nr"], r["stare"]))
        elif r["stare"] in CU_MOTIV and not r["lipsa"]:
            rele.append("%s: %s fără „ce lipsește / motiv”" % (r["nr"], r["stare"]))
    assert not rele, "\n".join(rele)


def test_rezolvata_are_commit_si_test_de_capat_la_capat():
    """MUTAȚIE: o stare „rezolvată” fără test (sau cu un test inexistent) -> pică."""
    teste = plasa_e2e()
    rele = []
    for r in randuri():
        if r["stare"] != "rezolvată":
            continue
        numite = re.findall(r"`([^`]+::test_def_[^`]+)`", r["test"])
        if not numite:
            rele.append("%s: rezolvată fără test de capăt la capăt" % r["nr"])
        for t in numite:
            if t not in teste.get(r["nr"], []):
                rele.append("%s: testul %s nu există în plasă" % (r["nr"], t))
        c = re.findall(r"`([0-9a-f]{7,40})`", r["commit"])
        if not c:
            rele.append("%s: rezolvată fără commit" % r["nr"])
        for sha in c:
            if subprocess.run(["git", "cat-file", "-e", sha + "^{commit}"], cwd=_RAD, capture_output=True).returncode:
                rele.append("%s: commitul %s nu există" % (r["nr"], sha))
    assert not rele, "\n".join(rele)


def test_fiecare_test_al_plasei_e_al_unei_deficiente_din_registru():
    stari = {r["nr"]: r["stare"] for r in randuri()}
    rele = ["%s (%s)" % (t, nr) for nr, ts in plasa_e2e().items() for t in ts if nr not in stari]
    assert not rele, "teste test_def_<nr> fără număr în DEFICIENTE.md: %s" % rele
    assert plasa_e2e(), "anti-vacuu: plasa n-are niciun test de capăt la capăt"


def test_poarta_ruleaza_plasa():
    """MUTAȚIE: pasul plasei scos din poartă -> pică."""
    t = io.open(os.path.join(_RAD, "scripts", "githooks", "poarta-suita"), encoding="utf-8").read()
    assert re.search(r'^"\$PY" scripts/e2e_poarta\.py ', t, re.M), "poarta nu mai rulează plasa de capăt la capăt"
    i = t.index('"$PY" scripts/e2e_poarta.py ')
    assert re.search(r"^\s*exit 1$", t[i:i + 900], re.M), "un eșec al plasei trebuie să respingă commitul"
