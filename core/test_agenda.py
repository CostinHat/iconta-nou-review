# -*- coding: utf-8 -*-
"""Garda anti-stale a agendei: pica daca TESTE.md a ramas in urma codului. Diferenta fata de DE_FACUT.md
(care a murit necitit): agenda e scrisa de mana DAR pazita mecanic - docul in urma codului pica suita."""
import os
import re
import ast
import subprocess
import datetime
import pathlib

from core import agenda

_RAD = pathlib.Path(__file__).resolve().parent.parent


def _git_at(cale):
    """Timestamp Unix al ultimului commit care a atins `cale` (NU mtime - se schimba la checkout)."""
    r = subprocess.run(["git", "-C", str(_RAD), "log", "-1", "--format=%at", "--", str(cale)],
                       capture_output=True, text=True)
    t = r.stdout.strip()
    return int(t) if t else None


def _ast_fara_docstring(src):
    """ast.dump al sursei cu docstring-urile scoase (module/functii/clase). Comentariile NU sunt in
    AST (ignorate automat); formatarea e ignorata de ast.dump (structural, fara linii/coloane)."""
    tree = ast.parse(src)

    def strip(node):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            b = node.body
            if b and isinstance(b[0], ast.Expr) and isinstance(getattr(b[0], "value", None), ast.Constant) \
               and isinstance(b[0].value.value, str):
                node.body = b[1:]
        for ch in ast.iter_child_nodes(node):
            strip(ch)

    strip(tree)
    return ast.dump(tree)


def _cod_substantial_diferit(old_src, new_src):
    """True daca s-a schimbat un assert / o valoare / o conditie / o formula (AST difera, fara
    docstring). False la schimbare DOAR de comentariu, docstring, formatare sau format de citare."""
    return _ast_fara_docstring(old_src) != _ast_fara_docstring(new_src)


def _schimbare_substantiala(relpath, data_verif):
    """(substantial: bool, nota_fallback: str|None). Compara continutul fisierului la data verificarii
    (ultimul commit <= data) cu HEAD, pe AST fara docstring. Fallback VIZIBIL pe comparatia de data
    daca o versiune istorica nu se parseaza - nota apare in mesajul gardii, nu tacut."""
    iso = data_verif.isoformat()
    old_commit = subprocess.run(
        ["git", "-C", str(_RAD), "log", "--until=%s 23:59:59" % iso, "-1", "--format=%H", "--", relpath],
        capture_output=True, text=True).stdout.strip()
    if not old_commit:
        return True, None  # nicio versiune la/inainte de data verificarii -> conservator: stale
    old_src = subprocess.run(["git", "-C", str(_RAD), "show", "%s:%s" % (old_commit, relpath)],
                             capture_output=True, text=True).stdout
    new_src = subprocess.run(["git", "-C", str(_RAD), "show", "HEAD:%s" % relpath],
                             capture_output=True, text=True).stdout
    try:
        return _cod_substantial_diferit(old_src, new_src), None
    except SyntaxError:
        return True, "versiunea de la %s nu se parseaza; cad pe comparatia de data pentru %s" % (iso, relpath)


def test_fiecare_modul_A_are_fisier_de_test():
    a = agenda.stare_sesiune_a()
    assert a is not None, "Inventarul sesiunii A lipseste din TESTE.md"
    lipsa = []
    for rand in a[2]:
        if not rand["fisiere"]:
            lipsa.append(rand["modul"] + " (niciun fisier numit)")
            continue
        for f in rand["fisiere"]:
            if not (_RAD / "core" / f).exists():
                lipsa.append("%s -> %s (inexistent)" % (rand["modul"], f))
    assert not lipsa, "module A fara fisier de test in repo (contopeste sau adauga fisierul): %s" % lipsa


def test_verificarile_A_nu_sunt_in_urma_codului():
    """Un modul marcat √ DD.MM e STALE daca fisierul lui s-a schimbat SUBSTANTIAL (assert/valoare/
    conditie/formula) dupa acea data -> reverifica. Schimbarile DOAR de comentariu/docstring/format/
    citare NU reseteaza bifa (varianta c, 30.07.2026). Ruleaza pe starea COMISA (git HEAD): commit
    INTAI, apoi poarta - altfel vede versiunea veche si da verde fals."""
    a = agenda.stare_sesiune_a()
    assert a is not None
    azi = datetime.date.today()
    stale = []
    for rand in a[2]:
        if not rand["verificat"] or "." not in rand["verificat"]:
            continue
        zi, luna = rand["verificat"].split(".")[:2]
        data_verif = datetime.date(azi.year, int(luna), int(zi))
        for f in rand["fisiere"]:
            relpath = "core/" + f
            at = _git_at(_RAD / "core" / f)
            if at is None:
                continue
            data_fisier = datetime.datetime.fromtimestamp(at, datetime.timezone.utc).date()
            if data_fisier <= data_verif:
                continue
            subst, nota = _schimbare_substantiala(relpath, data_verif)
            if nota:
                stale.append("%s: %s -> %s" % (rand["modul"], f, nota))
            elif subst:
                stale.append("%s: %s schimbat SUBSTANTIAL dupa %s (assert/valoare/conditie/formula) "
                             "-> reverifica la sursa si actualizeaza randul in TESTE.md"
                             % (rand["modul"], f, data_verif.isoformat()))
            # altfel: doar comentariu/docstring/formatare/citare -> NU e stale, se pastreaza bifa
    assert not stale, "AGENDA STALE (cod substantial in urma docului):\n" + "\n".join(stale)


def test_fiecare_xfail_apare_in_raport():
    d = agenda.datorii_deschise()
    assert d, "nicio datorie xfail citita din test_datorie.py"
    rap = agenda.raport(tehnic=False)
    lipsa = [n for n, _ in d if n not in rap]
    assert not lipsa, "datorii care nu apar in raportul agendei: %s" % lipsa


def test_agenda_ruleaza_fara_eroare():
    rap = agenda.raport(tehnic=False)
    assert "AGENDA iConta" in rap and "URMATORUL PAS" in rap and "DESCHIS ACUM" in rap


def test_stare_tehnica_numara_toata_suita():
    """STARE TEHNICA trebuie sa numere suita de la RADACINA (core/ + radacina), nu un subset.
    Bug 30.07.2026: agenda rula `pytest core/` (colecta doar un subset), dar suita reala e cea
    de la radacina -> STARE TEHNICA afisa un numar mai mic decat realitatea. Compara SCOPE-ul
    colectat (--collect-only), nu ruleaza suita de doua ori. (Fara literal cu numar+passed in
    text, ca traceback-ul la esec sa nu otraveasca regexul din stare_tehnica.)"""
    py = str(_RAD / "venv" / "bin" / "python3")
    if not os.path.exists(py):
        py = "python3"

    def _colectate(scope):
        # UN singur -q: dublu -q schimba formatul --collect-only si dispare 'N tests collected'
        args = ["--collect-only", "-q"] + [x for x in scope if x != "-q"]
        r = subprocess.run([py, "-m", "pytest"] + args,
                           cwd=str(_RAD), capture_output=True, text=True, timeout=120)
        m = re.search(r"(\d+) tests? collected", r.stdout)
        return int(m.group(1)) if m else None

    n_agenda = _colectate(agenda.PYTEST_ARGS)   # scope-ul REAL folosit de stare_tehnica
    n_radacina = _colectate([])                 # radacina, fara niciun filtru
    assert n_agenda is not None and n_radacina is not None, \
        "nu s-a putut parsa 'N tests collected' din pytest --collect-only"
    assert n_agenda == n_radacina, \
        "STARE TEHNICA numara %d, radacina are %d -> agenda ar afisa un numar fals" % (n_agenda, n_radacina)


def test_garda_substantial_distinge_docstring_de_assert():
    """Mutatie pe garda insasi (varianta c), doua cazuri: schimbarea de docstring/comentariu NU
    reseteaza bifa (fara fals-pozitiv); schimbarea de assert O reseteaza (prinde). Fara al doilea,
    garda ar putea fi permisiva la tot si tot ar trece."""
    baza = '''def f():
    "doc vechi"
    assert calc(2) == 4  # temei X
'''
    doar_docstring = '''def f():
    "doc NOU, alta formulare"
    assert calc(2) == 4  # alt comentariu, alta formatare
'''
    assert_schimbat = '''def f():
    "doc vechi"
    assert calc(2) == 5  # temei X
'''
    assert _cod_substantial_diferit(baza, doar_docstring) is False, \
        "fals-pozitiv: schimbarea de docstring/comentariu reseteaza bifa"
    assert _cod_substantial_diferit(baza, assert_schimbat) is True, \
        "ratare: schimbarea de assert NU reseteaza bifa"


def _fisiere_din_garzi_acoperit(text):
    """Fisierele numite in bullet-urile ACOPERIT din GARZI (bulletul + continuarile lui indentate).
    NU si cele din LIPSA/PARTIAL - acolo un fisier poate lipsi legitim (e chiar gardul care lipseste)."""
    fisiere = []
    inside = False
    for line in text.splitlines():
        s = line.lstrip()
        if s.startswith("- "):
            inside = s.startswith("- ACOPERIT") or (s.startswith("- **") and "ACOPERIT" in s)
        elif s.startswith("#"):
            inside = False
        if inside:
            fisiere += re.findall(r"core/[\w/]+\.py", line)
            fisiere += re.findall(r"\btest_\w+\.py", line)
    return fisiere


def test_garzi_acoperit_are_fisierele_numite():
    """Un gard marcat ACOPERIT trebuie sa aiba fisierul pe care il numeste - altfel registrul minte
    in sens invers (spune acoperit ce nu exista). Simetric cu Inventarul A."""
    g = (_RAD / "GARZI.md").read_text(encoding="utf-8")
    lipsa = []
    for tok in _fisiere_din_garzi_acoperit(g):
        ok = (_RAD / tok).exists() if tok.startswith("core/") else \
            ((_RAD / "core" / tok).exists() or (_RAD / tok).exists())
        if not ok:
            lipsa.append(tok)
    assert not lipsa, "GARZI ACOPERIT numeste fisiere inexistente: %s" % sorted(set(lipsa))


def _titluri_h2(text):
    return [ln.strip() for ln in text.splitlines() if ln.startswith("## ")]


def _h2_duplicate(titluri):
    return sorted({t for t in titluri if titluri.count(t) > 1})


def test_teste_md_fara_titluri_duplicate():
    """Doua sectiuni cu acelasi titlu = drift: agenda citeste PRIMA, a doua ramane stale invizibil.
    Exact bug-ul din 30.07 (doua '## Starea sesiunii B')."""
    dubluri = _h2_duplicate(_titluri_h2((_RAD / "TESTE.md").read_text(encoding="utf-8")))
    assert not dubluri, "titluri ## duplicate in TESTE.md (agenda citeste doar primul): %s" % dubluri


def test_garzi_si_duplicat_prind_defectul():
    """Mutatie pe cele doua garzi noi: fabricam defectul, garda il prinde; pe curat, tace."""
    # fisier-exista: tokenii din ACOPERIT sunt extrasi, cei din LIPSA sunt ignorati
    fals = ("- ACOPERIT: `core/exista_ac.py` — foo\n"
            "  test_exista_ac.py bar\n"
            "- LIPSA: **Y** — core/planificat_lipsa.py\n")
    toks = _fisiere_din_garzi_acoperit(fals)
    assert "core/exista_ac.py" in toks and "test_exista_ac.py" in toks, "nu extrage fisierele din ACOPERIT"
    assert "core/planificat_lipsa.py" not in toks, "scaneaza gresit fisiere din LIPSA (pot lipsi legitim)"
    # anti-duplicat: prinde dublura, tace pe unic
    assert _h2_duplicate(["## A", "## B", "## A"]) == ["## A"], "nu prinde titlul duplicat"
    assert _h2_duplicate(["## A", "## B"]) == [], "fals-pozitiv pe titluri unice"
