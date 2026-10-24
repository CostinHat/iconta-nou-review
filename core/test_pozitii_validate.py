# -*- coding: utf-8 -*-
"""GARD — fiecare poziție validată la testare are un test automat în poartă (comanda Costin 11.2 pct.4, verbatim în DECIZII
„Comanda 11.2”): „Regulă permanentă, scrisă în DECIZII: fiecare poziție validată la testare are un test automat în poartă, iar poarta nu
trece dacă vreunul pică. Aplic-o acum pe pozițiile validate: din planul de testare F004, F006, F008, F017, F019, F025, F028, F072, F073,
F078, F080, F081, F087, F134, F183; din retestul lotului 10: 383, 386, 401, 404, 415, 417, 419, 421, 423, 427, 430–432, 433, 434, 435,
436, 438, 7h, pct. 9.”

Registrul canonic e `POZITII_VALIDATE.csv` (rădăcina depozitului): `pozitie,sursa,ce_s_a_validat,test,fel` — `test` = nodeid-uri pytest
exacte (`cale::funcție`), separate de „ ; ”; `fel` ∈ {e2e, pytest}. O poziție nouă validată la testare = un rând nou aici, în același
commit cu testul ei.

CE VERIFICĂ (fiecare punct pică poarta):
  (a) fiecare rând are cel puțin un test, iar fiecare nodeid există: fișierul există și are funcția, la nivelul modulului, cu numele
      `test…` (prefixul pe care îl colectează pytest);
  (b) unde rulează: `fel=e2e` -> fișierul e `frontend_test/e2e/e2e_*.py`. Plasa porții îl colectează: `scripts/githooks/poarta-suita`
      cheamă `"$PY" scripts/e2e_poarta.py <iesire>` FĂRĂ `--doar` și respinge la orice cod nenul (`exit 1`); `scripts/e2e_poarta.py`
      rulează `pytest -q -p no:cacheprovider -o python_files=e2e_*.py --rootdir frontend_test/e2e frontend_test/e2e` (fără `--doar`,
      ținta e tot directorul), fără `-k` / `-m` / `--deselect` / `--ignore`, și întoarce codul lui pytest; în `frontend_test/e2e/` nu e
      niciun fișier de configurare pytest și niciun cârlig care ignoră / deselectează. `fel=pytest` -> fișierul e `core/test_*.py`, pe
      care îl colectează suita porții: `"$PY" -m pytest -q -n "$NW" --dist loadfile` din rădăcină, fără căi, fără `-k` / `-m`, fără
      `pytest.ini` / `tox.ini` / `setup.cfg` / `[tool.pytest]`, iar `conftest.py` și `core/conftest.py` nu ignoră / deselectează nimic;
  (c) un test listat nu e oprit: niciun decorator `skip` / `skipif` / `xfail`, niciun `pytestmark` cu ele, niciun `pytest.skip` /
      `pytest.xfail` / `pytest.importorskip` în corpul lui, la nivelul modulului sau în fixturile lui (cele din modul, din `conftest.py`-urile
      care i se aplică și din modulele vecine din care le importă), urmărite din fixtură în fixtură;
  (d) pozițiile cerute de Costin în 11.2 pct.4 sunt TOATE în registru (lista fixă `POZITII_CERUTE`, ca nimeni să nu le poată scoate);
  (e) un rând al unui număr din `DEFICIENTE.md` numește TOATE testele de capăt la capăt din coloana „test” a registrului deficiențelor, iar
      numărul e „rezolvată” (o poziție validată nu poate sta pe un număr redeschis fără ca registrul să o spună);
  (f) fiecare `test_pozitie_*` din `frontend_test/e2e/e2e_pozitii_validate.py` are mutația lui în `mut_pozitii_validate.json` (cu ancora
      prezentă o dată în fișierul numit), și e numit de un rând al registrului;
  (g) [comanda Costin 12.1 pct.7, verbatim: „Pentru fiecare poziție de pilot deja validată (F019, F026, F028, F073, F080, F081, F087, F134,
      F183, F252, F254) adaugă test automat în poartă, dacă nu există.”] fiecare din aceste poziții e în registru (lista fixă
      `POZITII_PILOT_VALIDATE`) și rândul ei numește un test propriu `test_pozitie_<f>_…` din `e2e_pozitii_validate.py` — fluxul principal
      al funcționalității, nu doar teste de deficiențe vecine.

LIMITĂ DECLARATĂ: garda dovedește că testul RULEAZĂ în poartă și NU e oprit; dacă testul reface exact ce a verificat Costin pe ecran se
judecă la scrierea lui (docstringul numește pașii) și se probează prin mutație (`--mutatie=`), nu de aici. Un test care se oprește singur
fără `pytest.skip` (un `return` timpuriu) nu se vede.
"""
import ast
import csv
import io
import json
import os
import re
import shlex
import tomllib

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRU = "POZITII_VALIDATE.csv"
COLOANE = ["pozitie", "sursa", "ce_s_a_validat", "test", "fel"]
FELURI = {"e2e": re.compile(r"^frontend_test/e2e/e2e_[^/]+\.py$"), "pytest": re.compile(r"^core/test_[^/]+\.py$")}
CONFTEST = {"e2e": ("frontend_test/e2e/conftest.py",), "pytest": ("conftest.py", "core/conftest.py")}
#: comanda Costin 11.2 pct.4, verbatim mai sus — „430–432” = 430, 431, 432
POZITII_CERUTE = ("F004", "F006", "F008", "F017", "F019", "F025", "F028", "F072", "F073", "F078", "F080", "F081", "F087", "F134", "F183",
                  "383", "386", "401", "404", "415", "417", "419", "421", "423", "427", "430", "431", "432", "433", "434", "435", "436",
                  "438", "7h", "pct.9")
#: comanda Costin 12.1 pct.7, verbatim în docstring (g): pozițiile pilot validate, fiecare cu testul ei `test_pozitie_<f>_…`
POZITII_PILOT_VALIDATE = ("F019", "F026", "F028", "F073", "F080", "F081", "F087", "F134", "F183", "F252", "F254")
_OPRIRI = {"skip", "skipif", "xfail"}
_APELURI_OPRIRE = {"skip", "xfail", "importorskip"}
_FISIER_POZITII = "frontend_test/e2e/e2e_pozitii_validate.py"
_MUTATII = "frontend_test/e2e/mut_pozitii_validate.json"


def _citeste(cale, surse=None):
    """Textul fișierului `cale` (relativ la depozit), sau None. `surse` = {cale: text} — fișiere sintetice (autoprobele gărzii)."""
    if surse is not None and cale in surse:
        return surse[cale]
    p = os.path.join(_RAD, cale)
    return io.open(p, encoding="utf-8").read() if os.path.isfile(p) else None


def randuri(text=None):
    """[{pozitie, sursa, ce_s_a_validat, test, fel}] — rândurile registrului."""
    text = text if text is not None else _citeste(REGISTRU)
    assert text is not None, "%s lipsește" % REGISTRU
    r = list(csv.DictReader(io.StringIO(text)))
    cap = next(csv.reader(io.StringIO(text)))
    assert cap == COLOANE, "antetul registrului: %s (cerut: %s)" % (cap, COLOANE)
    return r


def nodeid_uri(rand):
    return [t.strip() for t in (rand.get("test") or "").split(" ; ") if t.strip()]


# ── analiza unui fișier de teste ───────────────────────────────────────────────────────────────────────────────────────────────
def _nume_din(expr):
    """Numele (Name / Attribute) dintr-o expresie — `pytest.mark.skip(...)` -> {pytest, mark, skip}."""
    return {n.id for n in ast.walk(expr) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(expr) if isinstance(n, ast.Attribute)}


def _din_pytest(arbore):
    """Numele importate direct din pytest (`from pytest import skip`)."""
    return {a.asname or a.name for n in ast.walk(arbore) if isinstance(n, ast.ImportFrom) and n.module == "pytest" for a in n.names}


def _apeluri_oprire(nod, din_pytest):
    out = []
    for n in ast.walk(nod):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        if isinstance(f, ast.Attribute) and f.attr in _APELURI_OPRIRE and isinstance(f.value, ast.Name) and f.value.id == "pytest":
            out.append("pytest.%s (linia %d)" % (f.attr, n.lineno))
        elif isinstance(f, ast.Name) and f.id in _APELURI_OPRIRE and f.id in din_pytest:
            out.append("%s (linia %d)" % (f.id, n.lineno))
    return out


def _e_fixtura(fn):
    return any(_nume_din(d) >= {"fixture"} for d in fn.decorator_list)


def _functii_modul(arbore):
    return {n.name: n for n in arbore.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _fixturi_vizibile(cale, arbore, fel, surse):
    """{nume: (cale, FunctionDef, din_pytest)} — fixturile pe care testul din `cale` le poate cere: ale modulului, ale conftest-urilor
    care i se aplică și cele importate din modulele vecine (`from e2e_bloc_d import firma_sal`)."""
    out = {}
    dir_ = os.path.dirname(cale)

    def adauga(c, arb, nume=None):
        dp = _din_pytest(arb)
        for n, fn in _functii_modul(arb).items():
            if _e_fixtura(fn) and (nume is None or n in nume):
                out.setdefault(n, (c, fn, dp))

    adauga(cale, arbore)
    for n in arbore.body:
        if isinstance(n, ast.ImportFrom) and n.module and not n.level and "." not in n.module:
            vecin = "%s/%s.py" % (dir_, n.module) if dir_ else "%s.py" % n.module
            t = _citeste(vecin, surse)
            if t is not None:
                adauga(vecin, ast.parse(t), {a.asname or a.name for a in n.names})
    for c in CONFTEST[fel]:
        t = _citeste(c, surse)
        if t is not None:
            adauga(c, ast.parse(t))
    return out


def probleme_test(poz, nodeid, fel, surse=None):
    """Ce împiedică testul `nodeid` să ruleze în poartă (listă goală = rulează)."""
    if fel not in FELURI:
        return ["%s: felul %r nu e din %s" % (poz, fel, sorted(FELURI))]
    if nodeid.count("::") != 1 or "[" in nodeid:
        return ["%s: %r nu e un nodeid de funcție (`cale::funcție`)" % (poz, nodeid)]
    cale, nume = nodeid.split("::")
    if not FELURI[fel].match(cale):
        return ["%s: %s are fel=%s, dar fișierul nu e în locul pe care îl rulează poarta pentru felul ăsta (%s)"
                % (poz, nodeid, fel, FELURI[fel].pattern)]
    text = _citeste(cale, surse)
    if text is None:
        return ["%s: fișierul %s nu există" % (poz, cale)]
    arbore = ast.parse(text)
    fn = _functii_modul(arbore).get(nume)
    if fn is None or not nume.startswith("test"):
        return ["%s: %s nu există (nicio funcție `%s` la nivelul modulului)" % (poz, nodeid, nume)]
    rele = []
    dp = _din_pytest(arbore)
    for d in fn.decorator_list:
        if _nume_din(d) & _OPRIRI:
            rele.append("%s: %s are decoratorul %s" % (poz, nodeid, ast.unparse(d)))
    for n in arbore.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "pytestmark" for t in n.targets) \
                and _nume_din(n.value) & _OPRIRI:
            rele.append("%s: %s — modulul are `pytestmark = %s`" % (poz, nodeid, ast.unparse(n.value)))
        if isinstance(n, (ast.Expr, ast.If, ast.Try)):
            for a in _apeluri_oprire(n, dp):
                rele.append("%s: %s — modulul se oprește la nivelul lui: %s" % (poz, nodeid, a))
    for a in _apeluri_oprire(fn, dp):
        rele.append("%s: %s se oprește singur: %s" % (poz, nodeid, a))
    fixturi = _fixturi_vizibile(cale, arbore, fel, surse)
    de_vazut, vazute = [a.arg for a in fn.args.args], set()
    while de_vazut:
        f = de_vazut.pop()
        if f in vazute or f not in fixturi:
            continue
        vazute.add(f)
        c, ffn, fdp = fixturi[f]
        for d in ffn.decorator_list:
            if _nume_din(d) & _OPRIRI:
                rele.append("%s: %s — fixtura %s (%s) are decoratorul %s" % (poz, nodeid, f, c, ast.unparse(d)))
        for a in _apeluri_oprire(ffn, fdp):
            rele.append("%s: %s — fixtura %s (%s) oprește testul: %s" % (poz, nodeid, f, c, a))
        de_vazut += [a.arg for a in ffn.args.args]
    return rele


_DEFICIENTE = {}


def _teste_deficienta(nr):
    """Testele de capăt la capăt numite în `DEFICIENTE.md` pentru numărul `nr` și starea lui, sau None (nu e un număr al registrului)."""
    if not _DEFICIENTE:
        from core.test_deficiente import randuri as randuri_def
        _DEFICIENTE.update({r["nr"]: (r["stare"], re.findall(r"`([^`]+::test_def_[^`]+)`", r["test"])) for r in randuri_def()})
    return _DEFICIENTE.get(nr)


def probleme(text_csv=None, surse=None, cerute=POZITII_CERUTE, cu_deficiente=True, pilot=POZITII_PILOT_VALIDATE):
    """Toate abaterile registrului (listă goală = registrul e în regulă)."""
    rele, vazute, proprii = [], set(), {}
    for r in randuri(text_csv):
        poz = (r.get("pozitie") or "").strip()
        if not poz:
            rele.append("un rând fără poziție: %r" % r)
            continue
        if poz in vazute:
            rele.append("%s: poziția apare de două ori" % poz)
        vazute.add(poz)
        ts = nodeid_uri(r)
        proprii[poz] = [t for t in ts if t.startswith("%s::test_pozitie_%s_" % (_FISIER_POZITII, poz.lower()))]
        if not ts:
            rele.append("%s: niciun test" % poz)
        for t in ts:
            rele += probleme_test(poz, t, (r.get("fel") or "").strip(), surse)
        if cu_deficiente and re.fullmatch(r"\d+|C\d+", poz):
            d = _teste_deficienta(poz)
            if d is None:
                rele.append("%s: numărul nu e în DEFICIENTE.md" % poz)
            else:
                stare, numite = d
                if stare != "rezolvată":
                    rele.append("%s: poziție validată, dar în DEFICIENTE.md e „%s”" % (poz, stare))
                lipsa = [t for t in numite if t not in ts]
                if lipsa:
                    rele.append("%s: testele din DEFICIENTE.md lipsesc din rând: %s" % (poz, lipsa))
    lipsa = [p for p in cerute if p not in vazute]
    if lipsa:
        rele.append("pozițiile cerute de Costin (11.2 pct.4) lipsesc din registru: %s" % lipsa)
    fara = [p for p in pilot if not proprii.get(p)]
    if fara:
        rele.append("pozițiile pilot validate (12.1 pct.7) fără testul lor `test_pozitie_<f>_…` în %s: %s" % (_FISIER_POZITII, fara))
    return rele


# ── garda ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_fiecare_pozitie_validata_are_un_test_care_ruleaza_in_poarta():
    """(a)–(e). MUTAȚII: un nodeid inexistent / un test listat marcat skip / o poziție cerută scoasă din registru -> ROȘU."""
    rele = probleme()
    assert not rele, "\n".join(rele)
    assert len(randuri()) >= len(POZITII_CERUTE), "anti-vacuu: registrul are mai puține rânduri decât pozițiile cerute"


def probleme_plasa(surse=None):
    """(b) e2e: ce face ca plasa porții să nu ruleze toate `frontend_test/e2e/e2e_*.py` (listă goală = le rulează)."""
    rele = []
    poarta = _citeste("scripts/githooks/poarta-suita", surse) or ""
    linii = [ln for ln in poarta.splitlines() if re.match(r'^"\$PY" scripts/e2e_poarta\.py ', ln)]
    if len(linii) != 1:
        return ["poarta nu rulează plasa de capăt la capăt (o singură dată): %s" % linii]
    # pe ARGUMENTE (tokenizate ca în shell), nu pe sub-șir: un `--doar` dintr-un comentariu de pe rând nu e un argument
    optiuni = {t.split("=", 1)[0] for t in shlex.split(linii[0], comments=True)}
    if optiuni & {"--doar", "--mutatie"}:
        rele.append("poarta rulează numai o parte din plasă: %s" % linii[0])
    i = poarta.index(linii[0])
    if not re.search(r"^\s*exit 1$", poarta[i:i + 900], re.M):
        rele.append("un eșec al plasei nu mai respinge poarta (`exit 1` după `scripts/e2e_poarta.py`)")
    e2e = _citeste("scripts/e2e_poarta.py", surse) or ""
    m = re.search(r'subprocess\.run\(\[py, "-m", "pytest",(.*?)\]\s*\+\s*tinte', e2e, re.S)
    if not m:
        return rele + ["rularea pytest a plasei nu mai are forma cunoscută (`[py, \"-m\", \"pytest\", …] + tinte`)"]
    argumente = m.group(1)
    if '"python_files=e2e_*.py"' not in argumente:
        rele.append("plasa nu mai colectează `e2e_*.py`: %s" % argumente.strip())
    for interzis in ('"-k"', '"-m"', "--deselect", "--ignore", '"-x"', "--maxfail"):
        if interzis in argumente:
            rele.append("plasa rulează pytest cu %s: %s" % (interzis, argumente.strip()))
    if "tinte = [os.path.join(dir_e2e, d) for d in doar] or [dir_e2e]" not in e2e:
        rele.append("fără `--doar`, ținta plasei nu mai e tot directorul `frontend_test/e2e`")
    if not re.search(r"^\s*return r\.returncode$", e2e, re.M):
        rele.append("plasa nu mai întoarce codul lui pytest")
    for f in ("pytest.ini", "tox.ini", "setup.cfg", "pyproject.toml"):
        if _citeste("frontend_test/e2e/" + f, surse) is not None:
            rele.append("configurare pytest în plasă: frontend_test/e2e/%s" % f)
    return rele + _ignorari(CONFTEST["e2e"], surse)


def probleme_suita(surse=None):
    """(b) pytest: ce face ca suita porții să nu ruleze toate `core/test_*.py` (listă goală = le rulează)."""
    rele = []
    poarta = _citeste("scripts/githooks/poarta-suita", surse) or ""
    linii = [ln for ln in poarta.splitlines() if re.match(r'^"\$PY" -m pytest -q -n "\$NW" --dist loadfile', ln)]
    if len(linii) != 1:
        return ["poarta nu mai rulează suita întreagă în forma cunoscută: %s" % linii]
    rest = linii[0].split("--dist loadfile", 1)[1]
    if not re.match(r"^\s*>", rest):
        rele.append("suita porții primește argumente în plus (o cale, -k, -m): %r" % rest)
    for f in ("pytest.ini", "tox.ini", "setup.cfg"):
        if _citeste(f, surse) is not None:
            rele.append("configurare pytest în rădăcină: %s" % f)
    # pe TABELĂ (TOML parsat), nu pe sub-șir: `[tool.pytest.ini_options]` e cheia `tool.pytest`
    if tomllib.loads(_citeste("pyproject.toml", surse) or "").get("tool", {}).get("pytest") is not None:
        rele.append("pyproject.toml configurează pytest")
    return rele + _ignorari(CONFTEST["pytest"], surse)


def _ignorari(conftesturi, surse):
    rele = []
    for c in conftesturi:
        t = _citeste(c, surse) or ""
        for cuv in ("collect_ignore", "pytest_ignore_collect", "pytest_collection_modifyitems", "pytest_deselected"):
            if cuv in t:
                rele.append("%s ignoră / deselectează teste (%s)" % (c, cuv))
    return rele


def test_plasa_portii_colecteaza_toate_fisierele_e2e():
    """(b) e2e. MUTAȚII (autoproba de mai jos): `--doar=` pus în poartă / `-k` în rularea plasei / exitul plasei scos -> ROȘU."""
    rele = probleme_plasa()
    assert not rele, "\n".join(rele)


def test_suita_portii_colecteaza_testele_din_core():
    """(b) pytest. MUTAȚII (autoproba de mai jos): o cale / `-k` pe rularea suitei / un `collect_ignore` în conftest -> ROȘU."""
    rele = probleme_suita()
    assert not rele, "\n".join(rele)


def test_fiecare_test_al_pozitiilor_are_mutatia_lui_si_randul_lui():
    """(f). MUTAȚIE: o mutație scoasă din `mut_pozitii_validate.json` / un `test_pozitie_*` nou fără rând în registru -> ROȘU."""
    arbore = ast.parse(_citeste(_FISIER_POZITII))
    proprii = sorted(n for n in _functii_modul(arbore) if n.startswith("test_pozitie_"))
    assert proprii, "anti-vacuu: niciun test_pozitie_* în %s" % _FISIER_POZITII
    muts = json.loads(_citeste(_MUTATII))
    cu_mutatie = {m["test"].split("::", 1)[1] for m in muts}
    assert not [t for t in proprii if t not in cu_mutatie], "teste fără mutație: %s" % [t for t in proprii if t not in cu_mutatie]
    for m in muts:
        t = _citeste(m["fisier"])
        assert t is not None and t.count(m["ancora"]) == 1, "ancora mutației lui %s nu e unică în %s" % (m["test"], m["fisier"])
        assert m["inlocuire"] != m["ancora"], m["test"]
    numite = {x for r in randuri() for x in nodeid_uri(r)}
    fara_rand = [t for t in proprii if "%s::%s" % (_FISIER_POZITII, t) not in numite]
    assert not fara_rand, "teste ale pozițiilor fără rând în %s: %s" % (REGISTRU, fara_rand)


# ── autoprobele gărzii (mutațiile ei, permanente) ────────────────────────────────────────────────────────────────────────────────
_CSV_PROBA = "pozitie,sursa,ce_s_a_validat,test,fel\nF999,proba,proba,%s,%s\n"


def test_garda_prinde_un_nodeid_inexistent():
    s = {"frontend_test/e2e/e2e_proba_garda.py": "def test_altceva():\n    pass\n"}
    # lista EXACTĂ a abaterilor (nu „un mesaj care conține…”): o listă goală sau un mesaj străin pică
    rele = probleme(_CSV_PROBA % ("frontend_test/e2e/e2e_proba_garda.py::test_ce_nu_exista", "e2e"), s, cerute=(), pilot=())
    assert rele == ["F999: frontend_test/e2e/e2e_proba_garda.py::test_ce_nu_exista nu există "
                    "(nicio funcție `test_ce_nu_exista` la nivelul modulului)"], rele
    rele = probleme(_CSV_PROBA % ("frontend_test/e2e/e2e_lipsa_garda.py::test_x", "e2e"), s, cerute=(), pilot=())
    assert rele == ["F999: fișierul frontend_test/e2e/e2e_lipsa_garda.py nu există"], rele
    rele = probleme(_CSV_PROBA % ("frontend_test/altundeva/e2e_proba_garda.py::test_altceva", "e2e"), s, cerute=(), pilot=())
    assert rele == ["F999: frontend_test/altundeva/e2e_proba_garda.py::test_altceva are fel=e2e, dar fișierul nu e în locul pe care "
                    "îl rulează poarta pentru felul ăsta (%s)" % FELURI["e2e"].pattern], rele
    assert probleme(_CSV_PROBA % ("frontend_test/e2e/e2e_proba_garda.py::test_altceva", "e2e"), s, cerute=(), pilot=()) == []


def test_garda_prinde_testul_oprit():
    cale = "frontend_test/e2e/e2e_proba_garda.py"
    cazuri = {
        "decorator": "import pytest\n\n\n@pytest.mark.skip(reason='x')\ndef test_t():\n    pass\n",
        "skipif": "import pytest\n\n\n@pytest.mark.skipif(True, reason='x')\ndef test_t():\n    pass\n",
        "xfail": "import pytest\n\n\n@pytest.mark.xfail(strict=True)\ndef test_t():\n    pass\n",
        "pytestmark": "import pytest\npytestmark = pytest.mark.skip\n\n\ndef test_t():\n    pass\n",
        "in corp": "import pytest\n\n\ndef test_t():\n    pytest.skip('x')\n",
        "modul": "import pytest\npytest.skip('x', allow_module_level=True)\n\n\ndef test_t():\n    pass\n",
        "fixtura": "import pytest\n\n\n@pytest.fixture\ndef f():\n    pytest.xfail('x')\n\n\ndef test_t(f):\n    pass\n",
        "fixtura din fixtura": ("import pytest\n\n\n@pytest.fixture\ndef g():\n    pytest.skip('x')\n\n\n@pytest.fixture\ndef f(g):\n"
                                "    return g\n\n\ndef test_t(f):\n    pass\n"),
    }
    for caz, text in cazuri.items():
        rele = probleme(_CSV_PROBA % (cale + "::test_t", "e2e"), {cale: text}, cerute=(), pilot=())
        assert rele, "garda n-a prins testul oprit (%s)" % caz
    s = {cale: "from vecin_garda import f\n\n\ndef test_t(f):\n    pass\n",
         "frontend_test/e2e/vecin_garda.py": "import pytest\n\n\n@pytest.fixture\ndef f():\n    pytest.skip('x')\n"}
    assert probleme(_CSV_PROBA % (cale + "::test_t", "e2e"), s, cerute=(), pilot=()), "garda n-a prins fixtura importată care oprește testul"


def test_garda_prinde_pozitia_ceruta_scoasa_din_registru():
    text = _citeste(REGISTRU)
    fara = "\n".join(ln for ln in text.splitlines() if not ln.startswith("F004,")) + "\n"
    rele = probleme(fara)
    # rândul EXACT al pozițiilor lipsă, cu lista lor: numai F004 (o listă goală sau altă poziție pică)
    assert [r for r in rele if r.startswith("pozițiile cerute de Costin")] == [
        "pozițiile cerute de Costin (11.2 pct.4) lipsesc din registru: ['F004']"], rele
    rand = text.splitlines()[1]
    dublat = text + rand + "\n"
    assert probleme(dublat).count("%s: poziția apare de două ori" % rand.split(",", 1)[0]) == 1, "garda n-a prins poziția dublată"


def test_garda_prinde_testul_de_deficienta_lipsa_din_rand():
    text = _citeste(REGISTRU)
    rand = next(ln for ln in text.splitlines() if ln.startswith("383,"))
    scurtat = rand.replace(" ; frontend_test/e2e/e2e_lot10b_declaratii.py::test_def_383_d300_pe_luna_in_curs_se_refuza_la_generare", "")
    assert scurtat != rand, "rândul 383 nu mai are forma presupusă de autoprobă"
    rele = probleme(text.replace(rand, scurtat), cerute=(), pilot=())
    assert any(r.startswith("383: testele din DEFICIENTE.md lipsesc din rând") for r in rele), rele


def test_garda_prinde_plasa_sau_suita_care_nu_ruleaza_tot():
    poarta, e2e = _citeste("scripts/githooks/poarta-suita"), _citeste("scripts/e2e_poarta.py")
    rp = '"$PY" scripts/e2e_poarta.py '
    assert probleme_plasa({"scripts/githooks/poarta-suita": poarta.replace(rp, rp + "--doar=e2e_bloc_a.py ", 1)}), "--doar în poartă"
    assert probleme_plasa({"scripts/e2e_poarta.py": e2e.replace('"-o", "python_files=e2e_*.py"', '"-k", "bloc", "-o", "python_files=e2e_*.py"', 1)}), \
        "-k în rularea plasei"
    assert probleme_plasa({"scripts/e2e_poarta.py": e2e.replace("        return r.returncode\n", "        return 0\n", 1)}), "codul plasei pierdut"
    assert probleme_plasa({"frontend_test/e2e/conftest.py": _citeste("frontend_test/e2e/conftest.py") + "\ncollect_ignore = ['e2e_x.py']\n"}), \
        "collect_ignore în conftest-ul plasei"
    rs = '"$PY" -m pytest -q -n "$NW" --dist loadfile'
    assert probleme_suita({"scripts/githooks/poarta-suita": poarta.replace(rs, rs + " -k proaspat", 1)}), "-k pe suită"
    assert probleme_suita({"pytest.ini": "[pytest]\ntestpaths = frontend_test\n"}), "pytest.ini în rădăcină"


def test_garda_prinde_pozitia_pilot_fara_testul_ei():
    """(g). MUTAȚIE permanentă: rândul F026 fără `test_pozitie_f026_…` (numai cu un test vecin) / rândul scos -> ROȘU, cu lista exactă."""
    text = _citeste(REGISTRU)
    rand = next(ln for ln in text.splitlines() if ln.startswith("F026,"))
    vecin = rand.replace("e2e_pozitii_validate.py::test_pozitie_f026_", "e2e_pozitii_validate.py::test_pozitie_f028_")
    assert vecin != rand, "rândul F026 nu mai are forma presupusă de autoprobă"
    rele = [r for r in probleme(text.replace(rand, vecin), cu_deficiente=False) if r.startswith("pozițiile pilot validate")]
    assert rele == ["pozițiile pilot validate (12.1 pct.7) fără testul lor `test_pozitie_<f>_…` în %s: ['F026']" % _FISIER_POZITII], rele
    fara = "\n".join(ln for ln in text.splitlines() if not ln.startswith("F254,")) + "\n"
    rele = [r for r in probleme(fara, cu_deficiente=False) if r.startswith("pozițiile pilot validate")]
    assert rele == ["pozițiile pilot validate (12.1 pct.7) fără testul lor `test_pozitie_<f>_…` în %s: ['F254']" % _FISIER_POZITII], rele

