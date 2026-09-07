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

**A DOUA FORMA A PERIMETRULUI (regula 5, Costin 03.09.2026)**: *„o tura care nu atinge niciun
fisier executabil (.py, .js) ruleaza doar garzile de registre si documente, nu suita completa. Se
stabileste din ce s-a modificat fata de HEAD, nu prin judecata."*

Pana azi, orice `.md` atins facea instrumentul sa REFUZE sa scurteze — corect, fiindca graful de
import nu vede cine citeste un registru. Dar cand se ating **NUMAI** documente, perimetrul chiar se
poate inchide: sunt garzile care **citesc fisiere**, iar alea se pot deriva la fel de mecanic —
`perimetru_documente()`, care cauta in AST-ul fiecarui test numele documentelor urmarite de git,
direct sau printr-un modul importat. *Nu e o lista scrisa de mana: o gardă noua peste un registru
nou intra singura.*

**CE NU INLOCUIESTE.** Poarta completa ramane obligatorie inainte de publicare si inainte de
`/clear`. Instrumentul asta e pentru bucla scurta din timpul turei.

Folosire:
    ./venv/bin/python scripts/perimetru.py                  # din git diff
    ./venv/bin/python scripts/perimetru.py core/d100.py     # explicit
    ./venv/bin/python scripts/perimetru.py --pytest         # doar argumentele pentru pytest
"""
import ast
import functools
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


@functools.lru_cache(maxsize=1)
def graf_invers():
    """{modul: {fisiere care il importa}} — construit peste tot repo-ul, o singura data.

    [07.09.2026]  face propozitia de mai sus ADEVARATA. Pana azi graful se reconstruia la
    fiecare apel: docstringul promitea „o singura data", codul facea de fiecare data. Garda portii
    scurte, care il cheama de opt ori, dura 107 s din asta."""
    inv = {}
    for cale in _fisiere_py():
        for m in importurile(cale):
            inv.setdefault(m, set()).add(cale)
    return inv


def atinse_din_git():
    """**CE S-A MODIFICAT FATA DE HEAD** — exact `git diff --name-only HEAD`, nimic altceva.

    **[03.09.2026] Forma dinainte adauga si fisierele NETRACKED, si asta facea regula 5 inaplicabila
    pe arborele asta.** Masurat: `git status` arata permanent **299** de fisiere neurmarite — **217
    `.png`** (capturi de proba; `METODA_VERIFICARE.md` §27 le tine deliberat afara din repo), **58
    `.py`** (din care **55** probe din `frontend_test/`, plus 3 ale lui `ruff` din `venv/`), 10 `.md`
    si 6 `.csv` de lucru. Instrumentul le socotea „cod atins", deci **refuza sa scurteze la fiecare
    tura**, oricat de mica.

    **De ce forma noua e corecta, nu doar comoda.** *„Modificat fata de HEAD"* e chiar comanda:
    `git diff HEAD` acopera fisierele urmarite care s-au schimbat **si** adaugirile puse in index —
    adica exact ce va intra in commit. Un fisier neurmarit si nestagiat **nu face parte din ce se
    publica**: pytest nu-l culege (probele se numesc `proba_*`, nu `test_*`), iar daca cineva scrie
    un test nou, el apare aici **de indata ce il stagiaza**. *Riscul pe care il acopera vechea forma
    — un test nou nevazut — dispare la `git add`, adica inainte de orice commit.*

    **Ce NU se face:** nu se ocoleste refuzul instrumentului dandu-i argumente pe linia de comanda.
    Costin, 03.09: *„nu-l suprascrie cu judecata ta — o exceptie luata o data face regula o
    formalitate."* Daca instrumentul spune ca nu poate scurta, se ruleaza tot."""
    try:
        r = subprocess.run(["git", "diff", "--name-only", "HEAD"], cwd=RAD,
                           capture_output=True, text=True, timeout=60)
    except Exception:
        return []
    if r.returncode != 0:
        return []
    out = {x.strip() for x in r.stdout.splitlines() if x.strip()}
    return sorted(x for x in out if x.split("/", 1)[0] not in SARITE)


def netracked():
    """Fisierele neurmarite si nestagiate — NU intra in perimetru, dar se RAPORTEAZA.

    Tacerea despre ele ar fi la fel de rea ca socotirea lor: cine citeste iesirea trebuie sa stie
    ca exista o mulțime de fisiere pe care instrumentul nu le-a privit, si cat de mare e."""
    try:
        r = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=RAD,
                           capture_output=True, text=True, timeout=60)
    except Exception:
        return []
    if r.returncode != 0:
        return []
    return sorted(x.strip() for x in r.stdout.splitlines()
                  if x.strip() and x.split("/", 1)[0] not in SARITE)


#: Ce inseamna „fisier executabil" — cele doua feluri de cod care se EXECUTA in aplicatie.
#: Costin le-a numit explicit; nu se deduc si nu se largesc tacit.
EXT_EXECUTABILE = (".py", ".js")


#: Fisierele de PROVENIENTA ale corpusului — registre si ele, dar nu `.md` si nu in radacina.
#: Sunt numite explicit fiindca sunt singurele doua care ies din criteriul structural de mai jos.
REGISTRE_IN_PLUS = ("anaf_surse/INDEX.json", "anaf_surse/PROVENIENTA.json")


def _documente_urmarite():
    """REGISTRELE: fisierele `.md` din **radacina** repo-ului, plus cele doua JSON-uri de provenienta.

    **DE CE ASA DE INGUST — masurat, si prima forma era gresita cu un ordin de marime.** Prima
    definitie era „orice fisier urmarit de git care nu e executabil": includea sabloane
    (`tenant_template.sql`) si actele din `anaf_surse/`, pe care le numeste orice test fiscal intr-un
    temei. Perimetrul iesea **137 de fisiere / 1.314 teste / 976 s (16 min)** — fata de 22 de minute
    ale portii complete, adica o scurtare de un sfert, pentru un instrument care promitea altceva.
    Cu registrele propriu-zise: **25 de fisiere / 253 teste / 396 s (6 min 36 s)**.

    *Deosebirea nu e de prag, e de INTELES: un test care CITEAZA un act din corpus intr-un temei nu
    e o garda de registru. Un test care deschide `CONFORMITATE.md` e.* Criteriul e structural —
    `.md` in radacina —, nu o lista scrisa de mana: un registru nou intra singur.
    """
    out = set(REGISTRE_IN_PLUS)
    try:
        r = subprocess.run(["git", "ls-files"], cwd=RAD, capture_output=True, text=True, timeout=60)
    except Exception:
        return set()
    for cale in r.stdout.splitlines():
        cale = cale.strip()
        if cale.endswith(".md") and "/" not in cale:
            out.add(cale)
    return out | {os.path.basename(x) for x in out}


def _siruri(cale):
    """Literalii de tip sir dintr-un fisier .py, cititi cu `ast`. Un nume de document aparut intr-un
    COMENTARIU nu conteaza — de-aia nu se cauta cu expresii regulate."""
    import warnings
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            arbore = ast.parse(io.open(os.path.join(RAD, cale), encoding="utf-8").read())
    except (SyntaxError, UnicodeDecodeError, OSError):
        return set()
    return {n.value for n in ast.walk(arbore) if isinstance(n, ast.Constant)
            and isinstance(n.value, str)}


def perimetru_documente():
    """Garzile care CITESC documente — derivate, nu enumerate.

    Un test intra daca **el insusi** numeste un document urmarit de git, sau daca importa un
    **scaner din `scripts/`** care il numeste. A doua parte conteaza: garzile de registru trec des
    printr-un scaner (`scan_ramas` citeste `GARZI.md`, `scan_trasee` citeste `TRASEE.md`), iar
    testul lor nu pomeneste niciodata numele fisierului.

    **DE CE UN SINGUR NIVEL, si numai prin `scripts/` — masurat, nu ales.** Prima forma propaga
    tranzitiv prin tot graful de import si intorcea **357 din 578** de teste: aproape orice test
    importa, la cateva niveluri, un modul care numeste un fisier (`tenant_template.sql`, un act din
    `anaf_surse/`). Un perimetru care ia trei sferturi din suita nu deriva nimic, doar imbraca
    „ruleaza tot" in alt nume. Cu un nivel prin scanere: **137**, si cele doua care se adauga fata
    de forma directa sunt exact cele asteptate — `test_lista3` si `test_ramas`, amandoua garzi de
    registru care deleaga scanerului.

    **Ce NU acopera, declarat:** o garda care ar construi numele documentului din bucati
    (`"CONFORM" + "ITATE.md"`), sau una care ajunge la registru prin doua module de `core/`. N-am
    intalnit niciuna; daca apare, perimetrul o rateaza in tacere — de-aia forma asta se foloseste
    DOAR cand nu s-a atins niciun executabil, unde alternativa (poarta completa) e la o comanda."""
    documente = _documente_urmarite()
    if not documente:
        return []
    fisiere = sorted(_fisiere_py())
    direct = {c: bool(_siruri(c) & documente) for c in fisiere}
    cale_din_modul = {}
    for c in fisiere:
        m = _module_din_cale(c)
        if m:
            cale_din_modul[m] = c

    def citeste_documente(cale):
        if direct.get(cale):
            return True
        for m in importurile(cale):
            c2 = cale_din_modul.get(m)
            if c2 and c2.startswith("scripts/") and direct.get(c2):
                return True
        return False

    return sorted(c for c in fisiere
                  if os.path.basename(c).startswith("test_") and citeste_documente(c))


def executabile_atinse(atinse):
    """Care dintre fisierele atinse sunt EXECUTABILE. Se stabileste din extensie, nu prin judecata."""
    return sorted(a for a in atinse if a.endswith(EXT_EXECUTABILE))


def perimetru(atinse):
    """`(teste, incerte)`.

    `teste` = fisierele de test din inchiderea tranzitiva a celor care importa modulele atinse,
    PLUS testele atinse ele insele. `incerte` = motivele pentru care derivarea NU poate inchide
    perimetrul; daca lista nu e goala, raspunsul corect e **poarta completa**."""
    # [regula 5] Daca NU s-a atins niciun executabil, perimetrul e cel al garzilor de documente —
    # si se poate inchide, spre deosebire de cazul mixt, unde un `.md` atins alaturi de cod lasa
    # deschisa intrebarea „ce cod mai depinde de el".
    if atinse and not executabile_atinse(atinse):
        teste = perimetru_documente()
        if teste:
            return teste, []
        return [], ["nu s-a atins niciun executabil, dar derivarea garzilor de documente n-a "
                    "intors nimic — se ruleaza tot"]

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
    if not atinse:
        print("ATINSE: niciunul — arborele e curat fata de HEAD. Nimic de rulat.")
        _nt = netracked()
        if _nt:
            print("(%d fisiere neurmarite si nestagiate, NEPRIVITE de instrument — v. `netracked()`)"
                  % len(_nt))
        return 0
    print("ATINSE (%d):" % len(atinse))
    for a in atinse:
        print("   ", a)
    _nt = netracked()
    if _nt:
        print("(plus %d fisiere neurmarite si nestagiate, care NU intra in perimetru)" % len(_nt))
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
