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

BAZA DIFF-ULUI SI POARTA COMPUSA (23.10.2026, CLAUDE.md §5: „Verdictul pentru commitul reparat se compune din rularea completă
anterioară plus rerularea țintită.”; DECIZII 23.10.2026 „Comanda 12.1”). Doua optiuni care numesc un COMMIT, nu fisiere — regula [1]
ramane: lista atinselor vine tot din `git diff`, argumentul alege numai commitul de la care se citeste (`perimetru.BAZA`):
  * `--fata-de=<X>`: rularea tintita a tot ce s-a schimbat de la X incoace (implicit X = HEAD, bucla din tura);
  * `--compus=<X>`: poarta COMPUSA a lui HEAD din rularea completa rosie a lui X (`compus`, mai jos), chemata de
    `scripts/poarta_lot.sh --compus`. Tot aici traieste si formatul inregistrarii unei rulari (`scrie_rulare_din_argv`, chemata de
    `scripts/githooks/poarta-suita`): un singur scriitor si un singur cititor.
"""
import json
import os
import re
import subprocess
import sys
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))

import perimetru as P  # noqa: E402

#: „incert -> ruleaza tot”: suita intreaga, fara selectie, pe procesele portii (`scripts/githooks/poarta-suita`: -n 3, loadfile)
SUITA_INTREAGA = ["./venv/bin/python", "-m", "pytest", "-q", "-n", "3", "--dist", "loadfile"]
FRONT = (".js", ".css", ".html")
#: motivul pus de `e2e_din_plasa` cand plasa e atinsa INTEGRAL (conftest-ul ei / `scripts/e2e_poarta.py`): compusul il refuza
PLASA_INTREAGA = "plasa (conftest / e2e_poarta.py) atinsă"


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
        return {e: [PLASA_INTREAGA] for e in toate}
    out = {e: ["atins"] for e in plasa if e in toate}
    module = {os.path.basename(e)[:-3] for e in out}
    for e in toate:
        if e in out:
            continue
        imp = set(re.findall(r"^from (e2e_\w+) import", open(os.path.join(RAD, e), encoding="utf-8").read(), re.M)) & module
        if imp:
            out[e] = ["importă %s" % ", ".join(sorted(imp))]
    return out


def selectie(atinse, nivel):
    """`(teste, incerte, e2e, front, nevazute)` — ce rulează pentru fișierele atinse, pe cele trei clase (`imparte`): testele pytest,
    motivele de nesiguranță ale derivării Python, `{fișier e2e: [motive]}`, fișierele de front atinse și fișierele din „restul” pe care
    nu le numește niciun test (le vede numai poarta completă). Una singură, pentru rularea țintită (`main`) și pentru compus."""
    python, front, restul = imparte(atinse)
    teste, incerte = P.nivel(nivel, python) if python else ([], [])
    nevazute = []
    if restul:
        teste = sorted(set(teste) | set(P.perimetru_documente()) | set(teste_care_numesc(restul)))
        nevazute = [a for a in restul if not teste_care_numesc([a]) and not (a.endswith(".md") and "/" not in a)]
    e2e = e2e_din_plasa(atinse)
    if front:
        teste = sorted(set(teste) | set(teste_statice()) | set(teste_care_numesc(front)))
        for f, ids in e2e_atinse(front).items():
            e2e.setdefault(f, []).append("id-uri: " + ", ".join(ids[:6]) + (" …" if len(ids) > 6 else ""))
    return teste, list(incerte), e2e, front, nevazute


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


# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#  INREGISTRAREA RULARII SI POARTA COMPUSA (23.10.2026, CLAUDE.md §5; DECIZII 23.10.2026 „Comanda 12.1”)
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# Verbatim: „Un test care a trecut deja pe exact același commit nu se mai rulează a doua oară. Dacă poarta pică: se repară cauza, apoi
# se rulează testele căzute și tot ce depinde de reparație. Poarta completă se reia numai dacă reparația a atins piese folosite în mai
# multe locuri sau dacă perimetrul ei nu e sigur. Verdictul pentru commitul reparat se compune din rularea completă anterioară plus
# rerularea țintită.” și „Durata fiecărei părți a porții se măsoară și se raportează.”
#
# INREGISTRAREA. `poarta-suita` (rularea completa) scrie, prin `scrie_rulare_din_argv`, `<git-common-dir>/poarta_rulari/<sha>.json`:
# per parte rc, durata, nodurile cazute (`FAILED` / `ERROR` din pytest si din plasa) si `cazute_complete` — lista are atatea randuri cate
# cazute numara rezumatul lui pytest (o lista trunchiata, sau o parte cazuta fara rezumat, nu se poate compune).
#
# COMPUSUL (`compus(X)`, chemat de `scripts/poarta_lot.sh --compus`, pe arborele curat al lui HEAD): X = commitul rularii complete ROSII.
# Ruleaza nodurile cazute in X + perimetrul reparatiei (`git diff X`, nivelul `integrare` — inchiderea completa, prin `main`, plus
# rutele), e2e-ul cazut in X + e2e-ul derivat al reparatiei (`scripts/e2e_poarta.py --doar=…`, din INDEX), probele de prospetime,
# verificatorul si cifrele F1–F5; restul suitei a trecut in X si reparatia nu-l atinge. REFUZA (cod 2, fara verdict: „ruleaza poarta
# completa”) cand compunerea nu e sigura: rularea lui X lipseste / nu e completa / are arborele schimbat / are cazute nenumarabile; X nu
# e stramos al lui HEAD; diff gol; orice motiv `incerte` al derivarii; un fisier din „restul” pe care nu-l numeste niciun test; plasa
# atinsa integral; perimetrul gol; o piesa folosita in multe locuri (perimetrul >= jumatate din fisierele de test, pragul din
# `core/test_poarta_scurta.py::test_perimetrul_nu_e_toata_suita`); un nod cazut al carui fisier nu mai exista.
#: subdirectorul din `<git-common-dir>` cu inregistrarile rularilor porții
DIR_RULARI = "poarta_rulari"
#: partile ale caror cazute sunt noduri pytest, rerulate pe nume de compus
PARTI_CU_NODURI = ("proaspat", "pytest", "plasa")
PARTI = PARTI_CU_NODURI + ("verificator", "cifre", "arbore")
#: nivelul derivarii in compus: inchiderea COMPLETA (prin `main`) plus rutele — nu treapta de minute a buclei
NIVEL_COMPUS = "integrare"
PY = "./venv/bin/python"
_RE_CAZUT = re.compile(r"^(FAILED|ERROR) (\S+?(?:\[.*?\])?)(?: - |$)")
_RE_REZUMAT = re.compile(r"\b\d+ (?:passed|failed|errors?|skipped|xfailed|xpassed|deselected)\b")


def cazute_din_text(text):
    """`(noduri, randuri)` — nodurile `FAILED` / `ERROR` din rezumatul scurt al lui pytest, fără dubluri, și câte rânduri au fost."""
    noduri, randuri = [], 0
    for ln in text.splitlines():
        m = _RE_CAZUT.match(ln)
        if m:
            randuri += 1
            if m.group(2) not in noduri:
                noduri.append(m.group(2))
    return noduri, randuri


def numar_cazute(text):
    """`failed + errors` din ULTIMUL rând-rezumat al lui pytest; `None` dacă rezumatul lipsește."""
    for ln in reversed(text.splitlines()):
        if _RE_REZUMAT.search(ln):
            return sum(int(n) for n in re.findall(r"(\d+) (?:failed|errors?)\b", ln))
    return None


def parte(rc, durata, loguri=()):
    """O parte a rulării, din primul log existent și nevid: rc, durata, nodurile căzute, dacă lista e completă, ultimul rând."""
    text = ""
    for cale in loguri:
        try:
            text = open(cale, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if text.strip():
            break
    noduri, randuri = cazute_din_text(text)
    rezumat = next((x for x in reversed(text.splitlines()) if x.strip()), "")
    return {"rc": rc, "durata_s": durata, "cazute": noduri, "rezumat": rezumat[-300:],
            "cazute_complete": rc == 0 or (randuri > 0 and numar_cazute(text) == randuri)}


def _git(*a):
    return subprocess.run(["git"] + list(a), cwd=RAD, capture_output=True, text=True)


def _commit(rev):
    r = _git("rev-parse", "--verify", "--quiet", rev + "^{commit}")
    return r.stdout.strip() if r.returncode == 0 else None


def cale_rulare(sha):
    comun = _git("rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()
    return os.path.join(comun, DIR_RULARI, "%s.json" % sha)


def scrie_rulare(cale, inregistrare):
    os.makedirs(os.path.dirname(cale), exist_ok=True)
    with open(cale + ".tmp", "w", encoding="utf-8") as f:
        json.dump(inregistrare, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(cale + ".tmp", cale)
    print("[poarta] rularea -> %s" % cale)


def scrie_rulare_din_argv(argv):
    """Chemată de `poarta-suita`: `<cale.json> <sha> <ramura> <data> <parte>|<rc>|<durata>[|<log>…] …` (un singur scriitor al formatului)."""
    cale, sha, ramura, data = argv[:4]
    parti = {}
    for spec in argv[4:]:
        nume, rc, durata, *loguri = spec.split("|")
        parti[nume] = parte(int(rc or 1), int(durata or 0), loguri)
    scrie_rulare(cale, {"sha": sha, "ramura": ramura, "data": data, "tip": "completa", "parti": parti,
                        "verde": not any(p["rc"] for p in parti.values())})
    return 0


def plan_compus(x, rulare):
    """`(pytest, e2e, motive, atinse, front)` pentru compusul de la X; `motive` nevid -> compusul se REFUZĂ."""
    motive = []
    if not rulare:
        return [], [], ["rularea completă a lui %s n-are înregistrare (%s)" % (x[:12], cale_rulare(x))], [], []
    if rulare.get("tip") != "completa" or rulare.get("sha") != x:
        motive.append("înregistrarea lui %s nu e a unei rulări complete pe acest commit" % x[:12])
    parti = rulare.get("parti") or {}
    motive += ["partea %s lipsește din rularea lui %s" % (n, x[:12]) for n in PARTI if n not in parti]
    if (parti.get("arbore") or {}).get("rc"):
        motive.append("arborele s-a schimbat cât a rulat poarta completă — rularea nu e despre %s" % x[:12])
    for n in PARTI_CU_NODURI:
        p = parti.get(n) or {}
        if p.get("rc") and not p.get("cazute_complete"):
            motive.append("%s a căzut în %s (exit %s), dar lista testelor căzute nu e completă (%d noduri; „%s”)"
                          % (n, x[:12], p.get("rc"), len(p.get("cazute") or ()), p.get("rezumat", "")))
    head = _commit("HEAD")
    if x == head or _git("merge-base", "--is-ancestor", x, "HEAD").returncode != 0:
        motive.append("%s nu e strămoș al lui HEAD — reparația nu pornește din rularea lui" % x[:12])
    if _git("status", "--porcelain", "--untracked-files=normal").stdout.strip():
        motive.append("arborele nu e curat — compusul judecă commitul HEAD")
    P.BAZA = x
    atinse = P.atinse_din_git()
    if not atinse:
        motive.append("reparația nu schimbă niciun fișier față de %s — aceeași rulare ar trece un test instabil pe noroc" % x[:12])
    teste, incerte, e2e, front, nevazute = selectie(atinse, NIVEL_COMPUS) if atinse else ([], [], {}, [], [])
    motive += incerte
    motive += ["%s — niciun test nu-l numește: îl vede numai poarta completă" % a for a in nevazute]
    if any(PLASA_INTREAGA in m for ms in e2e.values() for m in ms):
        motive.append("plasa atinsă integral (conftest-ul plasei / scripts/e2e_poarta.py) — e2e-ul reparației e toată plasa")
    if atinse and not (teste or e2e or front):
        motive.append("perimetru gol, deși s-au atins fișiere")
    toate = _teste()
    if teste and len(teste) * 2 >= len(toate):
        motive.append("piesă folosită în multe locuri: perimetrul reparației are %d din %d fișiere de test" % (len(teste), len(toate)))
    cazute_py = list(dict.fromkeys(nd for n in ("proaspat", "pytest") for nd in (parti.get(n) or {}).get("cazute") or ()))
    cazute_e2e = list(dict.fromkeys((parti.get("plasa") or {}).get("cazute") or ()))
    motive += ["%s a căzut în %s, iar fișierul lui nu mai există" % (nd, x[:12]) for nd in cazute_py
               if not os.path.isfile(os.path.join(RAD, nd.split("::")[0]))]
    motive += ["%s (plasa) a căzut în %s, iar fișierul lui nu mai există" % (nd, x[:12]) for nd in cazute_e2e
               if not os.path.isfile(os.path.join(RAD, "frontend_test", "e2e", nd.split("::")[0]))]
    pytest_sel = list(teste) + [nd for nd in cazute_py if nd.split("::")[0] not in teste]
    e2e_fis = sorted(os.path.basename(f) for f in e2e)
    e2e_sel = e2e_fis + [nd for nd in cazute_e2e if nd.split("::")[0] not in e2e_fis]
    return pytest_sel, e2e_sel, motive, atinse, front


def _parte_rulata(nume, cmd, jurnale):
    """Rulează o parte a compusului cu ieșirea în `<jurnale>/compus_<nume>.log`; `(rc, durata, log)`."""
    log = os.path.join(jurnale, "compus_%s.log" % nume)
    print("[compus] %s: %s" % (nume, " ".join(cmd) if len(cmd) < 12 else " ".join(cmd[:11]) + " … (%d argumente)" % len(cmd)))
    t0 = time.time()
    with open(log, "w", encoding="utf-8") as f:
        rc = subprocess.run(cmd, cwd=RAD, stdout=f, stderr=subprocess.STDOUT).returncode
    durata = int(time.time() - t0)
    text = open(log, encoding="utf-8", errors="replace").read()
    if nume == "verificator":      # verdictul verificatorului e rândul TOTAL, nu exit-ul
        rc = 0 if [x for x in text.splitlines() if x.startswith("TOTAL: ")][-1:] == ["TOTAL: 0 candidate"] else 1
    print("[compus] %s: exit %d, %d s — %s" % (nume, rc, durata, next((x for x in reversed(text.splitlines()) if x.strip()), "")))
    return rc, durata, log


def compus(x):
    """Poarta COMPUSĂ pentru HEAD, din rularea completă roșie a lui X. 0 = verde, 1 = roșu, 2 = refuz (rulează poarta completă),
    4 = eroare a instrumentului (fără verdict)."""
    try:
        try:
            rulare = json.load(open(cale_rulare(x), encoding="utf-8"))
        except (OSError, ValueError):
            rulare = None
        pytest_sel, e2e_sel, motive, atinse, front = plan_compus(x, rulare)
        print("COMPUS din rularea completă a lui %s — ATINSE de reparație (%d): %s" % (x[:12], len(atinse), ", ".join(atinse)))
        if motive:
            print("REFUZ: compusul nu e sigur — rulează poarta COMPLETĂ (sh scripts/poarta_lot.sh). Motive:")
            for m in motive:
                print("   - " + m)
            return 2
        jurnale = os.environ.get("POARTA_JURNALE", "/tmp")
        parti = {}
        t0 = time.time()
        if os.path.isdir(os.path.join(RAD, "core")):
            rc, d, log = _parte_rulata("proaspat", [PY, "-m", "pytest", "-q", "-k", "proaspat", "core/"], jurnale)
            parti["proaspat"] = parte(rc, d, [log])
        if pytest_sel:
            rc, d, log = _parte_rulata("pytest", SUITA_INTREAGA + pytest_sel, jurnale)
            parti["pytest"] = parte(rc, d, [log])
        rc, d, log = _parte_rulata("verificator", [PY, "verificator_conformitate.py"], jurnale)
        parti["verificator"] = parte(rc, d, [log])
        rc, d, log = _parte_rulata("cifre", [PY, "scripts/cifre_referinta.py", "--productie", "--verifica"], jurnale)
        parti["cifre"] = parte(rc, d, [log])
        if e2e_sel:            # din INDEX (fără `--arbore`): exact ce se publică; după pytest, nu peste el (aceeași bază de test)
            rc, d, log = _parte_rulata("plasa", [PY, "scripts/e2e_poarta.py"] + ["--doar=" + e for e in e2e_sel], jurnale)
            parti["plasa"] = parte(rc, d, [log])
        verde = not any(p["rc"] for p in parti.values())
        durate = " · ".join("%s %ds" % (n, p["durata_s"]) for n, p in parti.items()) + " · compus %ds" % int(time.time() - t0)
        print("[compus] DURATE: %s" % durate)
        rosii = [n for n, p in parti.items() if p["rc"]]
        with open(os.path.join(RAD, ".poarta_jurnal.log"), "a", encoding="utf-8") as f:
            f.write("    DURATE: %s %s compus din %s%s · %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%S%z"), "VERDE" if verde else "ROSU",
                                                               x[:12], " · " + " ".join(rosii) if rosii else "", durate))
        head = _commit("HEAD")
        scrie_rulare(cale_rulare(head), {"sha": head, "tip": "compus", "compus_din": x, "parti": parti, "verde": verde,
                                         "data": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "atinse": atinse,
                                         "plan": {"pytest": pytest_sel, "e2e": e2e_sel}})
        if front:
            print("OBLIGATIA EXECUTORULUI: uneltele vizuale pe ecranele atinse (front atins: %s)." % ", ".join(front))
        print("[compus] %s" % ("VERDE" if verde else "ROSU — părți roșii: " + ", ".join(rosii)))
        return 0 if verde else 1
    except Exception:  # noqa: BLE001 — o eroare a instrumentului nu e un verdict
        import traceback
        traceback.print_exc()
        print("[compus] EROARE a instrumentului — niciun verdict scris; rulează poarta completă.")
        return 4


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

    # [23.10.2026] baza diff-ului: un COMMIT, nu fisiere — `--fata-de=<X>` (ce s-a atins de la X incoace) si `--compus=<X>` (poarta
    # compusa, CLAUDE.md §5). Tot `git diff`; argumentul alege numai commitul de la care se citeste.
    baze = [a.split("=", 1)[1] for a in argv if a.startswith(("--fata-de=", "--compus="))]
    if len(baze) > 1 or (baze and not _commit(baze[0])):
        print("REFUZ: --fata-de / --compus cer UN commit existent (ai dat: %s)." % ", ".join(baze))
        return 3
    if any(a.startswith("--compus=") for a in argv):
        return compus(_commit(baze[0]))
    if baze:
        P.BAZA = _commit(baze[0])

    atinse = P.atinse_din_git()
    nt = P.netracked()
    if not atinse:
        print("ATINSE: niciunul — arborele e curat fata de %s. Nimic de rulat." % P.BAZA)
        if nt:
            print("(%d fisiere neurmarite si nestagiate, NEPRIVITE de instrument)" % len(nt))
        return 0

    print("ATINSE (%d):" % len(atinse))
    for a in atinse:
        print("   ", a)
    if nt:
        print("(plus %d fisiere neurmarite si nestagiate, care NU intra in perimetru)" % len(nt))

    teste, incerte, e2e, front, nevazute = selectie(atinse, nivel)
    for a in nevazute:
        print("(niciun test nu numeste %s: il vede numai poarta lotului)" % a)
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
