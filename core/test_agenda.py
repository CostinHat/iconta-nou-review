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


def _ast_functie(src, nume):
    """ast.dump al functiei `nume` cu docstring-ul scos. Comentariile nu-s in AST (ignorate automat);
    formatarea e ignorata de ast.dump. None daca src nu se parseaza; '<ABSENT>' daca functia nu exista
    (redenumita/stearsa -> tratat ca schimbat)."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == nume:
            b = node.body
            if b and isinstance(b[0], ast.Expr) and isinstance(getattr(b[0], "value", None), ast.Constant) \
               and isinstance(b[0].value.value, str):
                node.body = b[1:]
            return ast.dump(node)
    return "<ABSENT>"


def _functie_schimbata(relpath, func, data_verif):
    """(schimbat: bool, nota_fallback: str|None). Compara AST-ul functiei `func` (fara docstring) intre
    commitul de la data_verif (ultimul <= data) si HEAD. Fallback VIZIBIL daca o versiune nu se parseaza."""
    iso = data_verif.isoformat()
    oc = subprocess.run(["git", "-C", str(_RAD), "log", "--until=%s 23:59:59" % iso, "-1", "--format=%H",
                         "--", relpath], capture_output=True, text=True).stdout.strip()
    if not oc:
        return True, None
    old = subprocess.run(["git", "-C", str(_RAD), "show", "%s:%s" % (oc, relpath)],
                         capture_output=True, text=True).stdout
    new = subprocess.run(["git", "-C", str(_RAD), "show", "HEAD:%s" % relpath],
                         capture_output=True, text=True).stdout
    ao, an = _ast_functie(old, func), _ast_functie(new, func)
    if ao is None or an is None:
        return True, "versiunea nu se parseaza; fallback pe fisier pentru %s::%s" % (relpath, func)
    return (ao != an), None


def test_fiecare_modul_A_are_fisier_de_test():
    a = agenda.stare_sesiune_a()
    assert a is not None, "Inventarul sesiunii A lipseste din TESTE.md"
    lipsa = []
    for rand in a["rows"]:
        if not rand["fisiere"]:
            lipsa.append(rand["modul"] + " (niciun fisier numit)")
            continue
        for f in rand["fisiere"]:
            if not (_RAD / "core" / f).exists():
                lipsa.append("%s -> %s (inexistent)" % (rand["modul"], f))
    assert not lipsa, "module A fara fisier de test in repo (contopeste sau adauga fisierul): %s" % lipsa


def test_verificarile_A_nu_sunt_in_urma_codului():
    """Un cluster √ DD.MM e STALE daca FUNCTIA lui de test s-a schimbat substantial dupa acea data
    (nivel de FUNCTIE, nu de fisier - 30.07: verificarea unui cluster nou NU mai reseteaza clusterele
    co-locate in acelasi fisier). Docstring/comentariu/format NU reseteaza (varianta c la nivel de
    functie). Co-locatie (clustere ce impart o functie de test): se reseteaza IMPREUNA, mesajul o spune.
    Ruleaza pe starea COMISA (git HEAD): commit INTAI, apoi poarta."""
    import collections
    a = agenda.stare_sesiune_a()
    assert a is not None
    azi = datetime.date.today()
    folos = collections.defaultdict(list)   # (relpath, functie) -> [(cluster, data_verif)]
    for rand in a["rows"]:
        if not rand["verificat"] or "." not in rand["verificat"]:
            continue
        if not rand["fisiere"] or not rand.get("functie"):
            continue
        zi, luna = rand["verificat"].split(".")[:2]
        dv = datetime.date(azi.year, int(luna), int(zi))
        relpath = "core/" + rand["fisiere"][0]
        for fn in rand["functie"]:
            folos[(relpath, fn)].append((rand["cluster"], dv))
    stale = []
    for (relpath, fn), cl in sorted(folos.items()):
        dv = min(d for _, d in cl)   # cea mai veche data (conservator)
        schimbat, nota = _functie_schimbata(relpath, fn, dv)
        nume = [c for c, _ in cl]
        if nota:
            stale.append("%s::%s: %s (clustere: %s)" % (relpath, fn, nota, ", ".join(nume)))
        elif schimbat:
            co = "  [CO-LOCATIE - clustere resetate impreuna]" if len(nume) > 1 else ""
            stale.append("functia de test %s::%s s-a schimbat substantial -> reverifica la sursa: %s%s"
                         % (relpath, fn, ", ".join(nume), co))
    assert not stale, "AGENDA STALE (functie de test in urma docului):\n" + "\n".join(stale)


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


def test_garda_functie_distinge_functia_clusterului():
    """Mutatie pe garda de FUNCTIE, ambele sensuri (Costin, 30.07):
    - schimbare in ASSERT-ul functiei clusterului -> AST difera (reseteaza);
    - schimbare in ALTA functie din acelasi fisier -> functia clusterului NEatinsa (NU reseteaza) -
      cazul care dovedeste upgrade-ul de la fisier la functie;
    - schimbare DOAR de docstring in functia clusterului -> NU reseteaza (varianta c la nivel functie);
    - functie absenta -> tratata ca schimbata."""
    vechi = ('def test_cluster():\n    "doc"\n    assert calc(2) == 4\n\n'
             'def test_alta():\n    assert alt(1) == 1\n')
    assert_schimbat = ('def test_cluster():\n    "doc"\n    assert calc(2) == 5\n\n'
                       'def test_alta():\n    assert alt(1) == 1\n')
    alta_schimbata = ('def test_cluster():\n    "doc"\n    assert calc(2) == 4\n\n'
                      'def test_alta():\n    assert alt(1) == 999\n')
    doar_docstring = ('def test_cluster():\n    "doc NOU, reformulat"\n    assert calc(2) == 4  # comentariu\n\n'
                      'def test_alta():\n    assert alt(1) == 1\n')
    assert _ast_functie(vechi, "test_cluster") != _ast_functie(assert_schimbat, "test_cluster"), \
        "schimbarea de assert NU reseteaza"
    assert _ast_functie(vechi, "test_cluster") == _ast_functie(alta_schimbata, "test_cluster"), \
        "schimbarea in ALTA functie reseteaza clusterul (upgrade-ul fisier->functie nu tine)"
    assert _ast_functie(vechi, "test_cluster") == _ast_functie(doar_docstring, "test_cluster"), \
        "schimbarea de docstring reseteaza (varianta c cazuta la nivel de functie)"
    assert _ast_functie("def x():\n    pass\n", "test_cluster") == "<ABSENT>", "functia absenta nedetectata"


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
    fals = ("- ACOPERIT: `core/exista_ac.py` — foo\n"
            "  test_exista_ac.py bar\n"
            "- LIPSA: **Y** — core/planificat_lipsa.py\n")
    toks = _fisiere_din_garzi_acoperit(fals)
    assert "core/exista_ac.py" in toks and "test_exista_ac.py" in toks, "nu extrage fisierele din ACOPERIT"
    assert "core/planificat_lipsa.py" not in toks, "scaneaza gresit fisiere din LIPSA (pot lipsi legitim)"
    assert _h2_duplicate(["## A", "## B", "## A"]) == ["## A"], "nu prinde titlul duplicat"
    assert _h2_duplicate(["## A", "## B"]) == [], "fals-pozitiv pe titluri unice"



def test_fiecare_fisier_test_are_cel_putin_un_test():
    """GARZI cat.9 (onestitatea testelor): un fisier test_*.py (exclus venv) cu 0 functii 'def test_'
    pare acoperire care NU exista - pytest nu-l colecteaza, dar numele sugereaza suita. Un script
    functional nu trebuie sa poarte prefixul test_. Prinde scripturile deghizate; verde cand nu exista."""
    goale = []
    for f in sorted(_RAD.rglob("test_*.py")):
        if "venv" in f.parts:
            continue
        src = f.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"^\s*(async\s+)?def test_", src, re.MULTILINE):
            goale.append(str(f.relative_to(_RAD)))
    assert not goale, ("fisiere test_*.py cu 0 functii 'def test_' (redenumeste-le fara prefixul test_ "
                       "- sunt scripturi, nu suita): %s" % goale)
