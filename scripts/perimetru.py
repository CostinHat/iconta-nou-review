# -*- coding: utf-8 -*-
"""scripts/perimetru.py — PERIMETRUL PORTII SCURTE, derivat din cod.

**Regula pe care o executa** (`PLAN_LUCRU.md`, regula 4 de conducere a lucrului, Costin 02.09.2026):

  > *„Poarta scurta: se ruleaza constructia atinsa si tot ce depinde de ea, derivat din dependentele
  > reale din cod, nu ales de la caz la caz. … Daca derivarea nu poate stabili cu certitudine
  > perimetrul, se ruleaza tot si se spune de ce — un perimetru ghicit e mai rau decat o poarta
  > lunga."*

**CE FACE.** Din fisierele ATINSE (implicit: `git diff --name-only HEAD` + netracked), calculeaza
**inchiderea tranzitiva a celor care le importa** — graful de import inversat, citit cu `ast`, nu cu
expresii regulate —, apoi intoarce fisierele de test din inchidere. Nimic nu e ales de mana.

**CE NU FACE, si de-aia are `--motiv-incert`.** Nu vede legaturile care nu trec prin `import`:
  * importuri dinamice (`__import__`, `importlib`) si nume construite la rulare;
  * gardele care citesc **fisiere** (registre, sabloane, artefacte JSON) fara sa importe modulul;
  * gardele care citesc **baza**, sau care parcurg TOT arborele (scanere de conformitate).
Cand atinge ceva din clasele astea, instrumentul **refuza sa scurteze** si spune de ce. Refuzul e
raspunsul corect: alternativa la nesiguranta e *tot*, nu *mai putin*.

**CE NU INLOCUIESTE.** Poarta completa ramane obligatorie inainte de publicare si inainte de
`/clear`. Instrumentul asta e pentru bucla scurta din timpul turei.

Folosire:
    ./venv/bin/python scripts/perimetru.py                  # din git diff
    ./venv/bin/python scripts/perimetru.py core/d100.py     # explicit
    ./venv/bin/python scripts/perimetru.py --pytest         # doar argumentele pentru pytest
"""
import ast
import io
import os
import subprocess
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Directoare sarite in varianta de REZERVA (`os.walk`), cand git nu raspunde.
#: Calea normala nu le foloseste: populatia vine din `git ls-files`, deci ce e ignorat de git
#: (`.lant_tmp/`, artefacte) e in afara grafului **prin constructie**, nu printr-o lista de mana.
SARITE = {".git", "venv", "__pycache__", "node_modules", "anaf_surse"}

#: Fisiere ATINSE care NU pot fi legate de teste prin graful de import — orice atingere a lor
#: cere poarta completa. Nu e o lista de excludere, e lista claselor pe care derivarea NU le vede.
#: Fiecare intrare poarta MOTIVUL, fiindcă un „de ce" pierdut devine peste o luna o exceptie fara temei.
NEDERIVABILE = {
    "conftest.py": "conftest schimba rularea intregii suite",
    "verificator_conformitate.py": "verificatorul parcurge TOT arborele, nu importa ce verifica",
    "main.py": "rutele sunt citite de scanere care nu importa main (inventarul de trasee, ancorele de rute)",
}

#: Sufixe de fisier atins pentru care graful de import nu spune nimic: registre, sabloane,
#: artefacte. Multe garzi le citesc ca FISIERE.
EXT_NEDERIVABILE = (".md", ".json", ".sql", ".txt", ".css", ".js", ".html", ".yml", ".yaml")


def _module_din_cale(cale):
    """`core/d100.py` -> `core.d100`. Cale relativa la radacina repo-ului."""
    c = cale.replace("\\", "/")
    if not c.endswith(".py"):
        return None
    return c[:-3].replace("/", ".")


def _fisiere_py():
    """Populatia grafului = fisierele .py **urmarite de git**, plus cele netracked care nu sunt
    ignorate. De-aia nu `os.walk`: un director de lucru ignorat (`.lant_tmp/`) contine copii vechi
    ale unor teste, iar ele ar intra in perimetru ca si cum ar fi cod viu."""
    fisiere = []
    for cmd in (["git", "ls-files", "*.py"],
                ["git", "ls-files", "--others", "--exclude-standard", "*.py"]):
        try:
            r = subprocess.run(cmd, cwd=RAD, capture_output=True, text=True, timeout=60)
            if r.returncode == 0:
                fisiere += [x.strip() for x in r.stdout.splitlines() if x.strip()]
        except Exception:
            fisiere = []
            break
    if fisiere:
        for f in sorted(set(fisiere)):
            yield f
        return
    # REZERVA, daca git nu raspunde: se parcurge arborele si se SPUNE, ca nimeni sa nu ia
    # rezultatul drept derivat din aceeasi populatie.
    sys.stderr.write("[perimetru] git n-a raspuns — populatia vine din os.walk, "
                     "deci poate include fisiere ignorate\n")
    for dirpath, dirnames, filenames in os.walk(RAD):
        dirnames[:] = [d for d in dirnames if d not in SARITE]
        for f in filenames:
            if f.endswith(".py"):
                yield os.path.relpath(os.path.join(dirpath, f), RAD).replace("\\", "/")


def importurile(cale):
    """Modulele importate de un fisier, citite cu `ast`. Un import scris in text (comentariu,
    docstring, sir) NU intra — de-aia nu se foloseste o expresie regulata."""
    import warnings
    try:
        with warnings.catch_warnings():
            # `ast.parse` reemite SyntaxWarning pentru literale ca "\(" din expresii regulate.
            # Nu e treaba instrumentului asta sa le raporteze — `ruff` o face, in poarta.
            warnings.simplefilter("ignore", SyntaxWarning)
            arbore = ast.parse(io.open(os.path.join(RAD, cale), encoding="utf-8").read())
    except (SyntaxError, UnicodeDecodeError, OSError):
        return set()
    out = set()
    for nod in ast.walk(arbore):
        if isinstance(nod, ast.Import):
            for a in nod.names:
                out.add(a.name)
        elif isinstance(nod, ast.ImportFrom):
            if nod.level:            # import relativ — nu apare in repo, dar nu se ghiceste
                continue
            if nod.module:
                out.add(nod.module)
                for a in nod.names:
                    out.add(nod.module + "." + a.name)
    return out


def graf_invers():
    """{modul: {fisiere care il importa}} — construit peste tot repo-ul, o singura data."""
    inv = {}
    for cale in _fisiere_py():
        for m in importurile(cale):
            inv.setdefault(m, set()).add(cale)
    return inv


def atinse_din_git():
    """Fisierele schimbate fata de HEAD, plus cele netracked. Ce spune git, nu ce-mi amintesc eu."""
    out = set()
    for cmd in (["git", "diff", "--name-only", "HEAD"],
                ["git", "ls-files", "--others", "--exclude-standard"]):
        try:
            r = subprocess.run(cmd, cwd=RAD, capture_output=True, text=True, timeout=60)
        except Exception:
            continue
        out.update(x.strip() for x in r.stdout.splitlines() if x.strip())
    # `venv/` apare la `--others` (nu e in .gitignore) si ar umple lista de ATINSE cu mii de
    # fisiere ale dependentelor. Nu e o alegere de perimetru: e granita repo-ului. Se DECLARA,
    # ca nimeni sa nu creada ca instrumentul a sarit ceva scris de noi.
    return sorted(x for x in out if x.split("/", 1)[0] not in SARITE)


def perimetru(atinse):
    """`(teste, incerte)`.

    `teste` = fisierele de test din inchiderea tranzitiva a celor care importa modulele atinse,
    PLUS testele atinse ele insele. `incerte` = motivele pentru care derivarea NU poate inchide
    perimetrul; daca lista nu e goala, raspunsul corect e **poarta completa**."""
    inv = graf_invers()
    incerte = []
    seminte = set()
    for a in atinse:
        baza = os.path.basename(a)
        if baza in NEDERIVABILE:
            incerte.append("%s — %s" % (a, NEDERIVABILE[baza]))
            continue
        if a.endswith(EXT_NEDERIVABILE):
            incerte.append("%s — fisier ne-Python: garzile care il citesc nu-l importa, "
                           "deci graful de import nu le vede" % a)
            continue
        m = _module_din_cale(a)
        if m is None:
            incerte.append("%s — nu e modul Python si nu e in clasele cunoscute" % a)
            continue
        seminte.add(m)

    # inchidere tranzitiva pe „cine importa"
    vazute = set(seminte)
    fisiere = set()
    coada = list(seminte)
    while coada:
        m = coada.pop()
        for cale in inv.get(m, ()):
            fisiere.add(cale)
            m2 = _module_din_cale(cale)
            if m2 and m2 not in vazute:
                vazute.add(m2)
                coada.append(m2)
    # fisierele atinse care sunt ele insele teste intra direct
    for a in atinse:
        if os.path.basename(a).startswith("test_") and a.endswith(".py"):
            fisiere.add(a)
    teste = sorted(f for f in fisiere if os.path.basename(f).startswith("test_"))
    return teste, incerte


def main(argv):
    doar_pytest = "--pytest" in argv
    argv = [a for a in argv if not a.startswith("--")]
    atinse = argv or atinse_din_git()
    teste, incerte = perimetru(atinse)
    if doar_pytest:
        print(" ".join(teste) if not incerte else "")
        return 0 if not incerte else 2
    print("ATINSE (%d):" % len(atinse))
    for a in atinse:
        print("   ", a)
    if incerte:
        print("\nPERIMETRUL NU SE POATE INCHIDE — se ruleaza POARTA COMPLETA. Motive:")
        for m in incerte:
            print("   -", m)
        print("\n(«un perimetru ghicit e mai rau decat o poarta lunga» — PLAN_LUCRU, regula 4)")
        return 2
    print("\nPERIMETRU DERIVAT — %d fisiere de test:" % len(teste))
    for t in teste:
        print("   ", t)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
