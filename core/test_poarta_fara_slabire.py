# -*- coding: utf-8 -*-
"""GARD — „Nu ai voie să slăbești, să ocolești sau să ștergi un test ca să treacă poarta” (comanda Costin 11.2, forma a doua, regula 3d,
verbatim în DECIZII „Comanda 11.2, forma a doua”).

Verbatim: *„Lotul se duce până la capăt fără oprire. Dacă poarta pică, repari codul și o rulezi din nou, până trece. Nu ai voie să
slăbești, să ocolești sau să ștergi un test ca să treacă poarta. Te oprești doar dacă reparația ar cere schimbarea unui comportament deja
decis sau o operație care nu se poate anula.”*

DE CE MECANIC: regula 3d scoate limita de două rulări pe lot — poarta se reia până la verde. Fără gardă, cea mai scurtă cale spre verde
devine slăbirea testului roșu (pe 31.07 poarta „pytest && git commit” a fost ocolită prin subset; CLAUDE.md, CICLUL DE NECONFORMITATE).

CE COMPARĂ: fiecare test care exista la INTRAREA LOTULUI (`git merge-base HEAD main` — ce e publicat) față de arborele de acum, numai pe
fișierele de test schimbate de atunci (`git diff --name-status`):
  (1) testul există încă (în același fișier sau, mutat, oriunde în arbore — cu același nume);
  (2) n-a pierdut aserțiuni: numărul de `assert` + `pytest.raises` / `pytest.fail` / `pytest.warns` din corp nu scade;
  (3) n-a primit `skip` / `skipif` / `xfail` / `pytest.skip()` / `pytest.xfail()` / `pytest.importorskip()` pe care nu-l avea;
  (4) nicio ocolire a colectării: `collect_ignore`, `pytest_collection_modifyitems`, `pytest_ignore_collect`, `--deselect`, `--ignore`,
      `-k ` în conftest-uri / configurarea pytest / `scripts/githooks/poarta-suita` nu cresc față de intrare.
EXCEPȚIA: o intrare în `MOTIVATE` de mai jos, `"<fișier>::<test>": "<motiv>"` — de ex. testul unei rute scoase prin decizia lui Costin,
cu decizia numită. Motivul stă AICI, într-un singur loc, vizibil în diff; o excepție fără abatere (stale) pică și ea.

LIMITĂ DECLARATĂ: (a) numărarea e statică — un `assert` mutat într-o funcție ajutătoare se vede ca aserțiune scoasă (fals pozitiv, se
motivează), iar o aserțiune înlocuită cu una mai slabă (`==` -> `in`, o toleranță mărită) nu se vede; (b) cazurile scoase dintr-un
`parametrize` nu se numără; (c) un test redenumit apare ca șters (se motivează cu numele nou). COLLECTED-ul real (rulat) rămâne în
raportul porții (CLAUDE.md §2.2 sect.2).
"""
import ast
import io
import os
import re
import subprocess

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RE_TEST = re.compile(r"(^|/)(test_[^/]*|e2e_[^/]*|conftest)\.py$")
CONFIG = ("pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini", "scripts/githooks/poarta-suita")
_RE_OCOLIRE = re.compile(r"collect_ignore|pytest_collection_modifyitems|pytest_ignore_collect|--deselect|--ignore\b|(?<![\w-])-k ")
_SLABIRI = {"skip", "skipif", "xfail", "importorskip"}
_ASERTIUNI = {"raises", "fail", "warns"}
#: [regula 3d] excepțiile motivate: {"<fișier>::<test>": "<motiv, cu decizia / deficiența numită>"}
MOTIVATE = {
    "core/test_lot14_2_595_1_d398_gri.py::test_d398_gri_cu_motiv_cand_oss_e_nu":
        "schimbare decisă de Costin (comanda 14.3, D2): la răspunsul OSS „Nu” D398 nu mai e gri, ci dispare din lista tipurilor; regula o păzește "
        "core/test_lot14_3_d2_oss.py::test_starea_oss_din_vector (și e2e `e2e_lot13_oss.py::test_def_595_oss_se_alege_in_date_firma`, pasul „Nu”)",
    "core/test_lot14_2_595_1_d398_gri.py::test_d398_gri_si_cand_oss_nu_e_declarat_dar_nu_cand_e_da":
        "schimbare decisă de Costin (comanda 14.3, D2): nedeclarat nu mai e gri și tăcut, ci „de lămurit” (activ, cu trimitere la Date firmă): "
        "core/test_lot14_3_d2_oss.py::test_starea_oss_din_vector și e2e `e2e_lot14_2.py::test_def_595_1_d398_de_lamurit_cat_firma_nu_a_raspuns_la_oss`",
    "core/test_lot14_2_595_1_d398_gri.py::test_d398_gri_si_fara_cod_romanesc_ca_inainte":
        "mutat, nu scos (comanda 14.3, D2): regula veche (fără cod de TVA românesc D398 rămâne gri) e păzită de "
        "core/test_lot14_3_d2_oss.py::test_d398_nu_mai_e_gri_pe_raspunsul_oss (ultima aserțiune), alături de noua regulă OSS",
    "frontend_test/e2e/e2e_lot14_2.py::test_def_595_1_d398_e_inactiva_cat_firma_nu_a_raspuns_da_la_oss":
        "redenumit și schimbat prin decizia lui Costin (comanda 14.3, D2): D398 fără răspuns OSS nu mai e inactivă, ci „de lămurit” (activă): "
        "frontend_test/e2e/e2e_lot14_2.py::test_def_595_1_d398_de_lamurit_cat_firma_nu_a_raspuns_la_oss",
}


def _git(*a):
    return subprocess.run(("git",) + a, cwd=_RAD, capture_output=True, text=True)


def baza_lotului():
    """SHA-ul de intrare al lotului: ce e publicat (`main`) și strămoș al lui HEAD."""
    p = _git("merge-base", "HEAD", "main")
    assert p.returncode == 0, "intrarea lotului (merge-base HEAD main) nu se poate afla: %s" % p.stderr.strip()
    return p.stdout.strip()


def _pytest_attr(n):
    """`pytest.X` / `pytest.mark.X` -> X (altfel None)."""
    if isinstance(n, ast.Call):
        n = n.func
    if isinstance(n, ast.Attribute):
        v = n.value
        if isinstance(v, ast.Name) and v.id == "pytest":
            return n.attr
        if isinstance(v, ast.Attribute) and v.attr == "mark" and isinstance(v.value, ast.Name) and v.value.id == "pytest":
            return n.attr
    return None


def functii_test(src):
    """PURĂ. {nume: {"aserturi": n, "slabiri": n}} — testele unui fișier (funcții `test_*` și metodele claselor `Test*`)."""
    out = {}
    try:
        t = ast.parse(src)
    except SyntaxError:
        return None

    def ia(fn, pref=""):
        aserturi = slabiri = 0
        for d in fn.decorator_list:
            if _pytest_attr(d) in _SLABIRI:
                slabiri += 1
        for n in (x for st in fn.body for x in ast.walk(st)):   # numai corpul: decoratorii s-au numărat mai sus
            if isinstance(n, ast.Assert):
                aserturi += 1
            elif isinstance(n, ast.Call):
                a = _pytest_attr(n)
                if a in _ASERTIUNI:
                    aserturi += 1
                elif a in _SLABIRI:
                    slabiri += 1
        out[pref + fn.name] = {"aserturi": aserturi, "slabiri": slabiri}

    modul_slab = 0
    for n in t.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test_"):
            ia(n)
        elif isinstance(n, ast.ClassDef) and n.name.startswith("Test"):
            for m in n.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name.startswith("test_"):
                    ia(m, n.name + ".")
        elif isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "pytestmark" for x in n.targets):
            modul_slab += sum(1 for x in ast.walk(n.value) if _pytest_attr(x) in _SLABIRI)
        elif isinstance(n, ast.Expr) and _pytest_attr(n.value) in _SLABIRI:
            modul_slab += 1   # pytest.skip(..., allow_module_level=True) / importorskip la nivel de modul
    if modul_slab:
        for v in out.values():
            v["slabiri"] += modul_slab
    return out


def ocoliri(text):
    """PURĂ. Câte mecanisme de ocolire a colectării apar în text."""
    return len(_RE_OCOLIRE.findall(text))


def abateri(vechi, nou, oriunde, ocoliri_vechi, ocoliri_noi, motivate):
    """PURĂ. vechi / nou: {fișier: {test: {...}}} (fișierele de test schimbate); oriunde: {test: [(fișier, {...})]} (tot arborele);
    ocoliri_*: {fișier: n}. -> [abateri nemotivate], [excepții stale]."""
    rele, folosite = [], set()
    for f, tv in sorted(vechi.items()):
        tn = nou.get(f) or {}
        for nume, v in sorted(tv.items()):
            cheie = "%s::%s" % (f, nume)
            acum = tn.get(nume)
            if acum is None:
                alt = [x for x in oriunde.get(nume, []) if x[0] != f]
                acum = alt[0][1] if len(alt) == 1 else None
            ce = []
            if acum is None:
                ce.append("testul a fost șters")
            else:
                if acum["aserturi"] < v["aserturi"]:
                    ce.append("aserțiuni %d -> %d" % (v["aserturi"], acum["aserturi"]))
                if acum["slabiri"] > v["slabiri"]:
                    ce.append("skip / xfail nou (%d -> %d)" % (v["slabiri"], acum["slabiri"]))
            if not ce:
                continue
            if cheie in motivate:
                folosite.add(cheie)
                continue
            rele.append("%s: %s — regula 3d: nu se slăbește, nu se ocolește, nu se șterge un test ca să treacă poarta; dacă e o "
                        "schimbare decisă, motivul intră în MOTIVATE din core/test_poarta_fara_slabire.py" % (cheie, "; ".join(ce)))
    for f in sorted(set(ocoliri_vechi) | set(ocoliri_noi)):
        if ocoliri_noi.get(f, 0) > ocoliri_vechi.get(f, 0):
            cheie = "%s::<colectare>" % f
            if cheie in motivate:
                folosite.add(cheie)
            else:
                rele.append("%s: ocolire a colectării nouă (collect_ignore / deselect / ignore / -k: %d -> %d)"
                            % (f, ocoliri_vechi.get(f, 0), ocoliri_noi[f]))
    return rele, sorted(set(motivate) - folosite)


def masoara():
    baza = baza_lotului()
    dif = _git("diff", "--name-status", "--no-renames", baza).stdout.splitlines()
    schimbate = sorted({ln.split("\t")[-1] for ln in dif if ln.strip()})
    vechi, nou, ov, on = {}, {}, {}, {}
    for f in schimbate:
        # numai fișierele pe care le măsoară garda: un fișier binar schimbat (o imagine din `static/`) nu e text și nu e test
        if not (_RE_TEST.search(f) or f in CONFIG or f.endswith("conftest.py")):
            continue
        p = _git("show", "%s:%s" % (baza, f))
        text_v = p.stdout if p.returncode == 0 else None
        cale = os.path.join(_RAD, f)
        text_n = io.open(cale, encoding="utf-8").read() if os.path.isfile(cale) else None
        if _RE_TEST.search(f) and text_v is not None:
            tv = functii_test(text_v)
            if tv:
                vechi[f] = tv
                nou[f] = (functii_test(text_n) or {}) if text_n is not None else {}
        if f in CONFIG or f.endswith("conftest.py"):
            ov[f] = ocoliri(text_v or "")
            on[f] = ocoliri(text_n or "")
    oriunde = {}
    fis = _git("ls-files", "--cached", "--others", "--exclude-standard").stdout.splitlines()
    for f in fis:
        if _RE_TEST.search(f) and os.path.isfile(os.path.join(_RAD, f)):
            for nume, v in (functii_test(io.open(os.path.join(_RAD, f), encoding="utf-8").read()) or {}).items():
                oriunde.setdefault(nume, []).append((f, v))
    return baza, vechi, nou, oriunde, ov, on


def test_niciun_test_slabit_ocolit_sau_sters_fata_de_intrarea_lotului():
    """Regula 3d. MUTAȚIE: un `assert` scos / un `@pytest.mark.skip` adăugat / un test șters într-un fișier de test existent -> pică."""
    baza, vechi, nou, oriunde, ov, on = masoara()
    rele, stale = abateri(vechi, nou, oriunde, ov, on, MOTIVATE)
    assert not rele, "față de intrarea lotului %s:\n%s" % (baza[:8], "\n".join(rele))
    assert not stale, "excepții MOTIVATE fără abatere (scoate-le): %s" % stale


def test_garda_slabirii_nu_e_vida():
    """Anti-vacuu: pică pe fragmente sintetice rele, trece pe unul bun; excepția motivată acoperă, cea stale e semnalată."""
    bun = ("import pytest\n\ndef test_a():\n    assert 1\n    with pytest.raises(ValueError):\n        int('x')\n\n"
           "class TestB:\n    def test_c(self):\n        assert 2\n")
    tv = functii_test(bun)
    assert tv == {"test_a": {"aserturi": 2, "slabiri": 0}, "TestB.test_c": {"aserturi": 1, "slabiri": 0}}, tv
    v = {"core/test_x.py": tv}

    def ab(src, mot=None, oriunde=None, ov=None, on=None):
        return abateri(v, {"core/test_x.py": functii_test(src)}, oriunde or {}, ov or {}, on or {}, mot or {})

    assert ab(bun) == ([], [])
    assert ab(bun + "\ndef test_nou():\n    pytest.skip('x')\n") == ([], []), "un test NOU nu e slăbirea unui test existent"
    rele = {
        "assert scos": bun.replace("    assert 1\n", "    pass\n"),
        "raises scos": bun.replace("    with pytest.raises(ValueError):\n        int('x')\n", ""),
        "skip decorator": bun.replace("def test_a", "@pytest.mark.skip(reason='x')\ndef test_a"),
        "skipif decorator": bun.replace("def test_a", "@pytest.mark.skipif(True, reason='x')\ndef test_a"),
        "xfail decorator": bun.replace("def test_a", "@pytest.mark.xfail\ndef test_a"),
        "pytest.skip în corp": bun.replace("    assert 1\n", "    pytest.skip('x')\n    assert 1\n"),
        "pytestmark pe modul": bun.replace("import pytest\n", "import pytest\npytestmark = pytest.mark.skip\n"),
        "skip la nivel de modul": bun.replace("import pytest\n", "import pytest\npytest.skip('x', allow_module_level=True)\n"),
        "test șters": bun.replace("class TestB:\n    def test_c(self):\n        assert 2\n", ""),
    }
    for ce, src in rele.items():
        assert ab(src)[0], "garda trece pe o slăbire: %s" % ce
    sters = rele["test șters"]
    assert ab(sters, oriunde={"TestB.test_c": [("core/test_y.py", {"aserturi": 1, "slabiri": 0})]}) == ([], []), "testul mutat"
    assert ab(sters, mot={"core/test_x.py::TestB.test_c": "ruta scoasă prin decizia X"}) == ([], [])
    assert ab(bun, mot={"core/test_x.py::test_a": "motiv"})[1] == ["core/test_x.py::test_a"], "excepția stale"
    assert ocoliri('addopts = -q --deselect core/test_x.py::test_a\n') == 1
    assert ocoliri("collect_ignore = ['x']\ndef pytest_collection_modifyitems(items): pass\n") == 2
    assert ocoliri('"$PY" -m pytest -q -k "not lent"\n') == 1 and ocoliri("pytest -q -n 3 --dist loadfile\n") == 0
    assert ab(bun, ov={"conftest.py": 0}, on={"conftest.py": 1})[0], "ocolirea colectării trecută"
