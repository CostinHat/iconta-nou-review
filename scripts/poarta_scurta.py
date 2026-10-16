# -*- coding: utf-8 -*-
"""scripts/poarta_scurta.py — RULEAZA poarta scurta din PLAN_LUCRU regula 4.

CE ERA SI CE LIPSEA. Derivarea perimetrului exista deja, intreaga, in `scripts/perimetru.py`:
inchiderea tranzitiva pe „cine importa", plus lista `incerte` care spune cand NU se poate inchide.
Ce lipsea era un lansator — ceva care sa ia perimetrul si sa-l RULEZE, cu refuzul respectat. Asta e.
Nu rescrie derivarea: o IMPORTA. *A doua definitie a aceluiasi lucru e inceputul unei divergente
tacute* (PLAN_LUCRU, regula 5).

TREI LUCRURI PE CARE LE FACE IMPOSIBILE, si sunt chiar motivul formei:

1. **NU primeste fisiere.** `perimetru.py` accepta cai in argv — util cand PROBEZI derivarea, dar
   fatal intr-un lansator: ar insemna ca cel care a scris modificarea alege ce se ruleaza. Regula o
   interzice pe litere: *„nu-l suprascrie cu judecata ta — o exceptie luata o data face regula o
   formalitate."* Aici lista atinselor vine NUMAI din `git diff`, si nu exista argument care s-o
   schimbe.
2. **NU poate trece drept poarta.** Cand perimetrul e verde, iesirea spune raspicat ce N-A rulat.
   Un verde care nu-si declara marginile e chiar felul de verde impotriva caruia e scrisa casa asta.
3. **NU ghiceste.** Daca derivarea intoarce fie si un singur motiv de nesiguranta (sau perimetrul iese
   gol), RULEAZA TOT: suita intreaga (`SUITA_INTREAGA`, pe procesele portii), nu poarta. *Un perimetru
   ghicit e mai rau decat o rulare lunga.* [15.10.2026, comanda Costin, verbatim in DECIZII „Poarta o dată
   pe lot”: „după fiecare comandă, doar rularea țintită de azi (poarta_scurta.py / perimetru.py, cu
   «incert → rulează tot»), pe numărul de procese de acum”.] Pana pe 15.10 iesea cu 2 si cerea poarta.

TREI CLASE DE FISIERE ATINSE (15.10.2026 seara, decizia Costin, verbatim in DECIZII „Lotul 5 — rularea țintită pe JS/CSS”: „Când o
comandă atinge JS/CSS, rularea țintită nu devine suita întreagă: rulezi e2e-ul ecranelor atinse, uneltele vizuale și verificatorul [...]
Suita întreagă rămâne doar pentru poarta de lot și pentru cazurile cu adevărat incerte din Python.”) — `imparte()`:
  * PYTHON (`.py`): perimetrul derivat (`perimetru.nivel`); NUMAI nesiguranta lui (conftest, main.py, verificatorul) -> suita intreaga.
  * FRONT (`static/**.js|.css|.html`): verificatorul (rulat aici); e2e-ul ecranelor atinse — DERIVAT: id-urile DOM ale fisierului JS
    (`id="…"`, `getElementById("…")`, `querySelector("#…")`) cautate ca `#id` in `frontend_test/e2e/e2e_*.py` (`e2e_atinse`), rulat cu
    `scripts/e2e_poarta.py --arbore --doar=…`; garzile statice care citesc `static/` (`teste_statice`) — doua din cele cinci picaturi
    ale rularii din 15.10 erau de felul asta (`?v=`, ancorele). Uneltele vizuale raman obligatia executorului (CLAUDE.md §2.3 pct.11):
    cer aplicatia vie si un browser pe ecranele atinse; lansatorul le NUMESTE la final, nu le ruleaza.
  * RESTUL (registre, hook-uri, configuratie, artefacte): garzile de registru (`perimetru.perimetru_documente`) + testele care NUMESC
    fisierul (`teste_care_numesc`). Un fisier pe care nu-l numeste niciun test se spune, nu porneste suita.

CE NU RULEAZA, scris ca sa nu se creada altceva: cifrele F1–F5 si plasa e2e INTREAGA. Poarta completa ruleaza O DATA PE LOT, la
inchiderea lui (`scripts/poarta_lot.sh`), inaintea publicarii.
"""
import os
import subprocess
import sys
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))

import perimetru as P  # noqa: E402

#: „incert -> ruleaza tot”: suita intreaga, fara selectie, pe procesele portii (`scripts/githooks/poarta-suita`: -n 3, loadfile)
SUITA_INTREAGA = ["./venv/bin/python", "-m", "pytest", "-q", "-n", "3", "--dist", "loadfile"]
FRONT = (".js", ".css", ".html")


def imparte(atinse):
    """`(python, front, restul)` — pe extensie și loc, nu prin judecată."""
    front = [a for a in atinse if a.startswith("static/") and a.endswith(FRONT)]
    python = [a for a in atinse if a.endswith(".py")]
    return python, front, [a for a in atinse if a not in front and a not in python]


def _teste():
    return [c for c in P._fisiere_py() if os.path.basename(c).startswith("test_")]


def teste_care_numesc(cai):
    """Testele care numesc fișierul (calea sau numele lui, ca literal-șir — nu în comentariu)."""
    nume = {x for c in cai for x in (c, os.path.basename(c)) if len(os.path.basename(c)) > 4}
    return sorted(t for t in _teste() if P._siruri(t) & nume)


def teste_statice():
    """Gărzile care citesc sursele UI: testul numește el însuși `static` / `static/…` / `stil.css` (ex. `os.path.join(RAD, "static",
    "js")`), sau importă o UNEALTĂ care le numește — din `scripts/` ori din rădăcină (`versioneaza_assets.py`), un singur nivel, ca
    `perimetru.perimetru_documente`; `main.py` și `conftest.py` nu sunt unelte (ar trage suita întreagă)."""
    def ui(cale):
        return any(s == "static" or s.startswith("static/") or s == "stil.css" for s in P._siruri(cale))
    unelte = {}
    for c in P._fisiere_py():
        m = P._module_din_cale(c)
        if m and (c.startswith("scripts/") or ("/" not in c and c not in ("main.py", "conftest.py"))) and ui(c):
            unelte[m] = c
    return sorted(t for t in _teste() if ui(t) or any(m in unelte for m in P.importurile(t)))


def e2e_atinse(front):
    """`{fișier e2e: [id-uri]}` — testele de capăt la capăt care folosesc id-urile DOM ale fișierelor JS atinse."""
    import glob
    import re
    ids = set()
    for f in front:
        if not f.endswith(".js") or not os.path.isfile(os.path.join(RAD, f)):
            continue
        src = open(os.path.join(RAD, f), encoding="utf-8").read()
        ids |= set(re.findall(r'\bid="([A-Za-z][\w-]{2,})"', src))
        ids |= set(re.findall(r'getElementById\(\s*["\']([\w-]{3,})', src))
        ids |= set(re.findall(r'querySelector(?:All)?\(\s*["\']#([\w-]{3,})', src))
    out = {}
    for e in sorted(glob.glob(os.path.join(RAD, "frontend_test", "e2e", "e2e_*.py"))):
        text = open(e, encoding="utf-8").read()
        gasite = sorted(i for i in ids if re.search(r"#%s\b" % re.escape(i), text))
        if gasite:
            out[os.path.relpath(e, RAD)] = gasite
    return out


def e2e_din_plasa(atinse):
    """`{fișier e2e: [motive]}` — plasa atinsă DIRECT: un fișier e2e schimbat (sau nou) rulează el însuși, și odată cu el fișierele e2e
    care îl importă (ajutoarele comune: `from e2e_bloc_d import …`); `conftest.py`-ul plasei sau `scripts/e2e_poarta.py` schimbate ->
    plasa întreagă (incert pentru plasă). [lotul 5, comanda 3] Înainte, e2e-ul se alegea numai după id-urile DOM ale JS-ului atins:
    `e2e_lot5_id.py`, nou, și `e2e_ciorne_proprii.py`, schimbat, n-au rulat deloc."""
    import glob
    import re
    toate = sorted(os.path.relpath(e, RAD) for e in glob.glob(os.path.join(RAD, "frontend_test", "e2e", "e2e_*.py")))
    plasa = [a for a in atinse if a.startswith("frontend_test/e2e/") and a.endswith(".py")]
    if "scripts/e2e_poarta.py" in atinse or any(a not in toate for a in plasa):
        return {e: ["plasa (conftest / e2e_poarta.py) atinsă"] for e in toate}
    out = {e: ["atins"] for e in plasa if e in toate}
    module = {os.path.basename(e)[:-3] for e in out}
    for e in toate:
        if e in out:
            continue
        imp = set(re.findall(r"^from (e2e_\w+) import", open(os.path.join(RAD, e), encoding="utf-8").read(), re.M)) & module
        if imp:
            out[e] = ["importă %s" % ", ".join(sorted(imp))]
    return out


def _ruleaza_tot(motiv):
    print()
    print("PERIMETRUL NU SE POATE INCHIDE (%s) — se ruleaza SUITA INTREAGA:" % motiv)
    print("  " + " ".join(SUITA_INTREAGA))
    print("(«un perimetru ghicit e mai rau decat o rulare lunga» — PLAN_LUCRU, regula 4)")
    t0 = time.time()
    r = subprocess.run(SUITA_INTREAGA, cwd=RAD)
    print("suita intreaga: %.0f s, exit %d. CE N-A RULAT: verificatorul, cifrele F1–F5, plasa e2e (poarta lotului)."
          % (time.time() - t0, r.returncode))
    return r.returncode


def main(argv):
    # [1] niciun argument de fisier. Explicit, cu motivul, nu prin ignorare tacuta.
    fisiere = [a for a in argv if not a.startswith("-")]
    if fisiere:
        print("REFUZ: poarta scurta nu primeste fisiere pe linia de comanda.")
        print("  Perimetrul se DERIVA din `git diff`, nu se alege. Ai dat: %s" % " ".join(fisiere))
        print("  (PLAN_LUCRU regula 5: «o excepție luată o dată face regula o formalitate».)")
        print("  Ca sa PROBEZI derivarea pe un fisier anume: scripts/perimetru.py <cale>")
        return 3

    # [P0 07.09.2026] NIVELUL cerut. Implicit: `subsistem` — treapta de minute, cea mai des
    # folosita in bucla de lucru. `--nivel complet` nu e acceptat aici: N4 e suita intreaga, si se
    # ruleaza cu `pytest` fara lista, nu prin instrumentul de perimetru.
    nivel = "subsistem"
    for a in argv:
        if a.startswith("--nivel="):
            nivel = a.split("=", 1)[1]
    if nivel not in P.NIVELURI:
        print("REFUZ: nivel necunoscut %r. Cunoscute: %s" % (nivel, ", ".join(P.NIVELURI)))
        return 3
    if nivel == "complet":
        print("N4 (complet) NU se ruleaza de aici — e suita intreaga:")
        print("  ./venv/bin/python -m pytest -q")
        return 3

    atinse = P.atinse_din_git()
    nt = P.netracked()
    if not atinse:
        print("ATINSE: niciunul — arborele e curat fata de HEAD. Nimic de rulat.")
        if nt:
            print("(%d fisiere neurmarite si nestagiate, NEPRIVITE de instrument)" % len(nt))
        return 0

    print("ATINSE (%d):" % len(atinse))
    for a in atinse:
        print("   ", a)
    if nt:
        print("(plus %d fisiere neurmarite si nestagiate, care NU intra in perimetru)" % len(nt))

    python, front, restul = imparte(atinse)
    teste, incerte = P.nivel(nivel, python) if python else ([], [])
    if restul:
        teste = sorted(set(teste) | set(P.perimetru_documente()) | set(teste_care_numesc(restul)))
        for a in restul:
            if not teste_care_numesc([a]) and not (a.endswith(".md") and "/" not in a):
                print("(niciun test nu numeste %s: il vede numai poarta lotului)" % a)
    e2e = e2e_din_plasa(atinse)
    if front:
        teste = sorted(set(teste) | set(teste_statice()) | set(teste_care_numesc(front)))
        for f, ids in e2e_atinse(front).items():
            e2e.setdefault(f, []).append("id-uri: " + ", ".join(ids[:6]) + (" …" if len(ids) > 6 else ""))
    cod = 0

    # [3] nesiguranta din PYTHON -> suita intreaga, cu motivele scrise
    if incerte:
        print()
        print("Motive de nesiguranta:")
        for m in incerte:
            print("   - ", m, sep="")
        cod = _ruleaza_tot("%d motive" % len(incerte))
    elif not teste and not front:
        # «nimic de rulat» nu e un raspuns despre ce s-a schimbat
        cod = _ruleaza_tot("perimetru gol, desi s-au atins fisiere")
    elif teste:
        print()
        print("NIVEL %s — %d fisiere de test." % (nivel.upper(), len(teste)))
        t0 = time.time()
        r = subprocess.run(["./venv/bin/python", "-m", "pytest", "-q", "--no-header"] + teste, cwd=RAD)
        print("nivel %s: %.0f s pe %d fisiere de test" % (nivel, time.time() - t0, len(teste)))
        cod = r.returncode

    if front:
        print()
        print("FRONT ATINS (%d): verificatorul + e2e-ul ecranelor atinse." % len(front))
        r = subprocess.run(["./venv/bin/python", "verificator_conformitate.py"], cwd=RAD, capture_output=True, text=True)
        total = [x for x in r.stdout.splitlines() if x.startswith("TOTAL: ")]
        print("verificator: %s" % (total[-1] if total else "fara linia TOTAL (exit %d)" % r.returncode))
        if total != ["TOTAL: 0 candidate"]:
            cod = cod or 1
    if e2e:
        print()
        print("E2E (%d fisiere): ecranele atinse + plasa atinsa direct." % len(e2e))
    for f, motive in sorted(e2e.items()):
        print("e2e %s (%s)" % (f, "; ".join(motive)))
        r = subprocess.run(["./venv/bin/python", "scripts/e2e_poarta.py", "--arbore", "--doar=" + os.path.basename(f)], cwd=RAD)
        cod = cod or r.returncode
    if front:
        if not e2e:
            print("(niciun e2e nu foloseste id-urile fisierelor atinse)")
        print("OBLIGATIA EXECUTORULUI (CLAUDE.md §2.3 pct.11): `versioneaza_assets.py --scrie`, apoi uneltele vizuale pe ecranele atinse")
        print("  + artefactele (acoperire_vizuala, text_ecran, proba_pagina_principala, proba_decl50) refacute — le cere poarta lotului.")
    print()
    urm = {"direct": "subsistem", "subsistem": "integrare", "integrare": "complet"}.get(nivel)
    if urm and teste and not incerte:
        print("CE N-A RULAT: tot ce e peste nivelul asta. Urmatoarea treapta: --nivel=%s" % urm)
    print("Poarta COMPLETA: o data pe lot, la inchiderea lui (scripts/poarta_lot.sh), inaintea publicarii.")
    return cod


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
