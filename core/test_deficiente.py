# -*- coding: utf-8 -*-
"""GARD — registrul deficiențelor (`DEFICIENTE.md`) și plasa lui (comanda Costin 09.10.2026, pct.6–9 și 13, verbatim în DECIZII).

  · numerotarea e continuă (1..ultimul, fără goluri sau dubluri) și N1–N18 sunt toate acolo: „orice deficiență nouă primește
    următorul număr din DEFICIENTE.md”; deficiențele găsite de Code au prefixul C, continuu de la C1 (decizia Costin 10.10.2026: „De
    acum, defectele găsite de tine primesc prefixul C, iar numerele simple rămân ale mele”);
  · starea e din mulțimea închisă; `parțial` / `nerezolvată` / `nu se aplică` spun ce lipsește (motivul);
  · `rezolvată` are commitul (existent în git) ȘI testul de capăt la capăt numit, care există ca funcție `test_def_<nr>_…` într-un
    `frontend_test/e2e/e2e_*.py`: „Un număr fără test nu e «rezolvată», e «neverificat»”;
  · invers, fiecare `test_def_<nr>_…` din plasă e al unui număr din registru (un test fără deficiență e o probă fără întrebare);
  · poarta rulează plasa (`scripts/e2e_poarta.py` în `scripts/githooks/poarta-suita`): „orice publicare la care pică o verificare a
    plasei nu se face”.
"""
import ast
import csv
import glob
import io
import json
import os
import re
import subprocess
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# [17.10.2026, decizia Costin pct.3 — „Marchează 268 în DEFICIENTE ca amânată, cu motivul”] + `amânată`: amânare DECISĂ de Costin, cu motiv
# [15.1-E7, pct.5] + `reparat, fără dovadă pe ecran`: reparat în cod, fără un test e2e pe ecran numit în harta porții; devine `rezolvată` numai când primește scenariul
# (plasa pilot din E6 sau lotul care o retestează); termen: lotul E8, apoi revine pe `nerezolvată`
STARE_FARA_DOVADA = "reparat, fără dovadă pe ecran"
STARI = {"rezolvată", "parțial", "nerezolvată", "nu se aplică", "neverificat", "amânată", STARE_FARA_DOVADA}
STARI_N = {"reală", "nu e reală", "neverificat"}
#: [CLAUDE.md §2.3 pct.10] rândul rezolvat în commitul care îl conține
AUTO_COMMIT = "commitul care conține această intrare"
CU_MOTIV = {"parțial", "nerezolvată", "nu se aplică", "reală", "amânată"}
NR_N = 18


def randuri(text=None):
    """[{nr, text, stare, commit, lipsa, test}] — rândurile numerotate ale tabelului."""
    text = text if text is not None else io.open(os.path.join(_RAD, "DEFICIENTE.md"), encoding="utf-8").read()
    out = []
    for ln in text.splitlines():
        # [lotul 12, comanda 12.2] „409.1”, „C73.1”: subnumărul lui Costin pentru o reapariție după retest (rândul de bază rămâne)
        m = re.match(r"^\| (\d+(?:\.\d)?|N\d+|C\d+(?:\.\d)?) \|(.*)\|\s*$", ln)
        if not m:
            continue
        cel = [c.strip() for c in m.group(2).split("|")]
        assert len(cel) == 5, "rândul %s nu are cele 6 coloane: %r" % (m.group(1), ln[:120])
        out.append(dict(zip(("text", "stare", "commit", "lipsa", "test"), cel), nr=m.group(1)))
    return out


def plasa_e2e():
    """{nr: [cale::funcție]} — testele `test_def_<nr>_…` din plasă și testele `test_pilot_…` ale căror numere sunt declarate în `DEFICIENTE_PROBATE`."""
    out = {}
    for f in sorted(glob.glob(os.path.join(_RAD, "frontend_test", "e2e", "e2e_*.py"))):
        for n in ast.walk(ast.parse(io.open(f, encoding="utf-8").read())):
            if isinstance(n, ast.FunctionDef):
                # subnumărul („test_def_409_1_…” -> „409.1”) e o singură cifră după număr: „test_def_439_426_…” rămâne al lui 439
                m = re.match(r"^test_def_((?:\d+|n\d+|c\d+)(?:_\d(?=_))?)_", n.name)
                if m:
                    out.setdefault(m.group(1).upper().replace("_", "."), []).append("%s::%s" % (os.path.relpath(f, _RAD), n.name))
        # [16.2-B] testul unei poziții pilot (`test_pilot_<poziție>`) declară numerele pe care le dovedește: `DEFICIENTE_PROBATE = ("278.1", …)` la nivel de modul
        arbore = ast.parse(io.open(f, encoding="utf-8").read())
        for n in arbore.body:
            if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "DEFICIENTE_PROBATE" for t in n.targets):
                for nr in ast.literal_eval(n.value):
                    out.setdefault(str(nr).upper(), []).extend("%s::%s" % (os.path.relpath(f, _RAD), x.name) for x in arbore.body
                                                               if isinstance(x, ast.FunctionDef) and x.name.startswith("test_pilot_"))
    return out


def test_numerotarea_e_continua_si_completa():
    """MUTAȚIE: un rând șters / un număr dublat -> pică."""
    nr = [r["nr"] for r in randuri()]
    num = [int(x) for x in nr if x.isdigit()]
    assert num == list(range(1, max(num) + 1)), "numerotarea 1..%d are goluri sau dubluri" % max(num)
    assert max(num) >= 188, "anti-vacuu: registrul trebuie să aibă cel puțin 1–188"
    assert [x for x in nr if x.startswith("N")] == ["N%d" % i for i in range(1, NR_N + 1)]
    c = [x for x in nr if x.startswith("C") and "." not in x]
    sub = [x for x in nr if "." in x]
    assert not [x for x in sub if x.split(".")[0] not in nr], "subnumăr fără rândul de bază: %s" % sub
    assert c == ["C%d" % i for i in range(1, len(c) + 1)], "numerotarea C are goluri, dubluri sau e în altă ordine: %s" % c
    assert len(c) >= 7, "anti-vacuu: C1–C7 (fostele 220–226 ale lui Code) trebuie să fie acolo"


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
        numite = re.findall(r"`([^`]+::test_(?:def|pilot)_[^`]+)`", r["test"])
        if not numite:
            rele.append("%s: rezolvată fără test de capăt la capăt" % r["nr"])
        for t in numite:
            if t not in teste.get(r["nr"], []):
                rele.append("%s: testul %s nu există în plasă" % (r["nr"], t))
        c = re.findall(r"`([0-9a-f]{7,40})`", r["commit"])
        if not c and r["commit"].strip() == AUTO_COMMIT:
            continue   # CLAUDE.md §2.3 pct.10: registrul nu poate purta SHA-ul commitului care îl conține
        if not c:
            rele.append("%s: rezolvată fără commit" % r["nr"])
        for sha in c:
            if subprocess.run(["git", "cat-file", "-e", sha + "^{commit}"], cwd=_RAD, capture_output=True).returncode:
                rele.append("%s: commitul %s nu există" % (r["nr"], sha))
    assert not rele, "\n".join(rele)


def plasa_publicarii():
    """Fișierele e2e pe care le rulează plasa de publicare: tot ce numește harta porții (`scripts/poarta_harta.txt`) plus plasa fixă pilot (15.1-E7, pct.5)."""
    import glob as _g
    out = set()
    for ln in io.open(os.path.join(_RAD, "scripts", "poarta_harta.txt"), encoding="utf-8"):
        if "=>" in ln and not ln.startswith("#"):
            out.update(ln.split("=>", 1)[1].split())
    out.update(os.path.basename(f) for f in _g.glob(os.path.join(_RAD, "frontend_test", "e2e", "e2e_pilot*.py")))
    out.add("e2e_pozitii_validate.py")
    return out


def test_rezolvata_are_testul_e2e_in_harta_portii():
    """[15.1-E7, pct.5] „rezolvată” = numele unui test e2e pe ecran, existent ÎN HARTA porții (plasa de publicare îl rulează, deci e verde la ultima rulare): un test pytest
    pe funcție nu e dovadă pentru un număr văzut pe ecran. MUTAȚIE: un test numit care nu e în hartă (sau un `rezolvată` fără test) -> pică."""
    in_harta = plasa_publicarii()
    rele = []
    for r in randuri():
        if r["stare"] != "rezolvată":
            continue
        for t in re.findall(r"`([^`]+::test_(?:def|pilot)_[^`]+)`", r["test"]):
            if os.path.basename(t.split("::")[0]) not in in_harta:
                rele.append("%s: testul %s nu e în harta porții (scripts/poarta_harta.txt)" % (r["nr"], t))
    assert not rele, "\n".join(rele)


def test_fiecare_test_al_plasei_e_al_unei_deficiente_din_registru():
    stari = {r["nr"]: r["stare"] for r in randuri()}
    rele = ["%s (%s)" % (t, nr) for nr, ts in plasa_e2e().items() for t in ts if nr not in stari]
    assert not rele, "teste test_def_<nr> fără număr în DEFICIENTE.md: %s" % rele
    assert plasa_e2e(), "anti-vacuu: plasa n-are niciun test de capăt la capăt"


def test_poarta_ruleaza_plasa(tmp_path):
    """Plasa e în poartă și un eșec al ei face poarta ROȘIE. [23.10.2026, CLAUDE.md §5; DECIZII 23.10.2026 „Comanda 12.1”] Poarta nu
    se mai oprește la prima parte roșie: codul plasei se ține (`RC_PLASA=$?`, rândul imediat următor), plasa roșie intră în părțile roșii
    și poarta iese 1 la final (`exit 1` după plasă). Funcțional, pe `poarta-suita` adevărată cu uneltele imitate
    (`core/test_poarta_lot.DepozitPoarta`): numai plasa roșie -> exit 1, iar înregistrarea rulării o arată, cu nodul căzut.
    MUTAȚII: pasul plasei scos din poartă -> pică; `[ "$RC_PLASA" -ne 0 ] && rosu …` scos -> poarta verde pe plasa roșie -> pică."""
    t = io.open(os.path.join(_RAD, "scripts", "githooks", "poarta-suita"), encoding="utf-8").read()
    assert re.search(r'^"\$PY" scripts/e2e_poarta\.py ', t, re.M), "poarta nu mai rulează plasa de capăt la capăt"
    i = t.index('"$PY" scripts/e2e_poarta.py ')
    assert t[i:].splitlines()[1].strip() == "RC_PLASA=$?", "codul plasei nu mai e ținut imediat după rularea ei"
    assert re.search(r"^\s*exit 1$", t[i:i + 900], re.M), "un eșec al plasei trebuie să respingă poarta"
    from core.test_poarta_lot import DepozitPoarta
    dp = DepozitPoarta(tmp_path)
    cod, iesire = dp.suita(plasa="e2e_x.py::test_e")
    assert cod == 1 and iesire.count("[poarta] ROSU: plasa e2e") == 1, iesire
    parti = dp.rulare(dp.git("rev-parse", "HEAD"))["parti"]
    assert {n for n, p in parti.items() if p["rc"]} == {"plasa"} and parti["plasa"]["cazute"] == ["e2e_x.py::test_e"], parti


# ===================================================================================================================================
# [Comanda Costin 11.2 pct.3, verbatim în DECIZII „Comanda 11.2”] „nimic nu e «rezolvat» fără dovadă pe ecran pe firmele de test, inclusiv
# pe documentele create înainte de reparație. Orice reparație acoperă și datele existente.”
#
# DE CE: la retestul lotului 10, cinci „rezolvat” erau false (439 / 425, 409, 452, 429, 451): testul de capăt la capăt trecea pe o firmă
# e2e nouă, cu datele fabricate de test, iar pe firmele de test ale cabinetului (F1–F6) — cu documentele scrise înainte de reparație —
# ecranul arăta încă defectul. Garda de mai sus cere testul e2e; asta cere, pe lângă el, DOVADA PE FIRMELE DE TEST și ce s-a făcut cu
# DATELE EXISTENTE, în coloana „ce lipsește / motiv”:
#
#   dovadă firme de test: `dovezi/lot11/439_f1_balanta.png`, `dovezi/lot11/439_f1_vechi_balanta_preluata.png`; date existente: migrare
#   `core/migrare_x.py` | script `scripts/x.py` | cod `core/x.py` (<ce face cu ele>) | neafectate, pentru că <motiv>
#
#   · fiecare captură: `dovezi/lot<N>/<nr>_..._f<k>_....png` — numărul rândului la început, firma de test (`f1`…`f6`, …) în nume; captura
#     e în manifestul `dovezi/lot<N>/AMPRENTE.json` (în index), cu amprenta sha256 a fișierului de pe disc când fișierul e acolo. Imaginea
#     NU intră în index: `core/test_fara_probe_imagine.py` (decizia Costin 03.09.2026, „nu se salvează și nu devin bază de comparație”);
#     ea călătorește în ZIP-ul lotului, iar amprenta o leagă de rândul din registru (suita a doua a lotului 11 le-a găsit în index — garda
#     imaginilor a picat; DECIZII „Lotul 11: suita a doua”);
#   · când datele existente NU sunt „neafectate”, cel puțin o captură are `vechi` în nume: ecranul pe un document creat ÎNAINTE de reparație;
#   · fișierul numit la migrare / script / cod există.
#
# CRITERIUL (nu se poate ocoli prin neatingerea rândului): se cere dovada oricărui rând `rezolvată` care (a) nu exista în registru la
# pornirea lotului 11 (`REF_LOT11`), SAU (b) are starea / „ce lipsește” / testul schimbate de atunci (orice rând redeclarat rezolvat în
# lotul 11 sau după), SAU (c) e un număr lucrat în comenzile 11.1 / 11.2 (`ATINSE_LOT11`), chiar dacă rândul a rămas cu textul lotului 10.
# Rândurile rezolvate înainte de lotul 11 și neatinse de atunci rămân pe regula veche (registrul nu poate dovedi trecutul).
REF_LOT11 = "381c82df"
#: primul număr al lotului 15 (retesturile din 25.10.2026 încoace): dovada lui e e2e-ul din harta porții, nu capturile lotului 11
NUMAR_LOT15 = 712
#: [Comanda 11.1 pct.1–25 și 11.2 pct.2] numerele lucrate în lotul 11 (cele cu textul lotului 10 care trebuie redovedite: 425 / 426 după
#: 439, 428, 429, 409, 436 afișarea, C68–C74 „dă dovada pe aplicație”, 420, 424; restul sunt noi, dar intră și pe criteriul (a))
ATINSE_LOT11 = frozenset(
    ["409", "420", "422", "424", "425", "426", "428", "429", "436", "247", "248"]
    + [str(n) for n in range(439, 453)]
    + ["C%d" % n for n in range(68, 77)])
DOVADA = "dovadă firme de test:"
DATE_EXISTENTE = "date existente:"
# [lotul 13, cerut de sesiunea principală] contextul capturii: firma de test (`f<k>`, FISCALOS `fiscalos_f9054`) SAU, cuvânt întreg, `admin`
# (ecran al Panoului Admin, fără firmă) / `public` (pagina publică, fără sesiune) — `administrator`, `publicat` nu trec
_RE_CAPTURA = r"^dovezi/lot\d+/%s_(?:[a-z0-9]+_)*?(?:f\d+|admin|public)(?:_[a-z0-9]+)*\.png$"
#: Numerele a căror dovadă e e2e-ul, prin decizia SCRISĂ a lui Costin sau a arhitectului — mulțime ÎNCHISĂ (calibrarea pică dacă alt număr o folosește):
#: „rezolvată” fără captură, cu testul e2e cerut în continuare (`test_rezolvata_are_commit_si_test_de_capat_la_capat`).
DOVADA_PRIN_E2E = {
    "642": "decizia Costin 13.1 pct.4.7: „642: e2e-ul e dovada potrivită pentru înregistrarea unui cabinet.”",
    "278.1": "decizia arhitectului 05.11, regula Costin 04.11",
}
#: dintre ele, cele a căror dovadă e un test pilot + pașii oracolului (16.4 pct.1); restul cer un `test_def_…`
DOVADA_PRIN_PILOT = frozenset({"278.1"})
_FORME_DATE = ("migrare", "script", "cod", "neafectate, pentru că")


def _in_index(cale):
    return not subprocess.run(["git", "ls-files", "--error-unmatch", cale], cwd=_RAD, capture_output=True).returncode


def _exista_in_index(cale):
    return os.path.isfile(os.path.join(_RAD, cale)) and _in_index(cale)


def _manifest(director):
    """{captură: sha256} din `<director>/AMPRENTE.json`, dacă manifestul e în index; altfel {}."""
    m = "%s/AMPRENTE.json" % director
    if not _exista_in_index(m):
        return {}
    return json.load(io.open(os.path.join(_RAD, m), encoding="utf-8"))


def _sha256(cale):
    import hashlib
    with open(os.path.join(_RAD, cale), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _captura_amprentata(cale):
    """Captura e în manifestul lotului ei, iar fișierul de pe disc (când e acolo) are amprenta din manifest."""
    amp = _manifest(os.path.dirname(cale)).get(cale)
    return amp is not None and (not os.path.isfile(os.path.join(_RAD, cale)) or _sha256(cale) == amp)


def randuri_la_pornirea_lotului_11():
    """{nr: rând} — registrul din commitul `REF_LOT11` (pornirea ramurii lotului 11)."""
    p = subprocess.run(["git", "show", REF_LOT11 + ":DEFICIENTE.md"], cwd=_RAD, capture_output=True, text=True)
    assert p.returncode == 0, "commitul de referință %s (pornirea lotului 11) nu se poate citi: %s" % (REF_LOT11, p.stderr.strip())
    return {r["nr"]: r for r in randuri(p.stdout)}


def cere_dovada(r, vechi):
    """PURĂ. Rândul `r` (stare rezolvată) cere dovada pe firmele de test? `vechi` = rândurile de la pornirea lotului 11."""
    if r["stare"] != "rezolvată" or r["nr"].startswith("N"):
        return False
    # [15.1-E7, pct.5] numerele lotului 15 (712 și următoarele) sunt „rezolvate” numai cu testul e2e pe ecran din harta porții (`test_rezolvata_are_testul_e2e_in_harta_portii`),
    # nu cu capturi pe firmele de test: regula 11.2 rămâne pentru numerele mai vechi
    if re.match(r"^(\d+)", r["nr"]) and int(re.match(r"^(\d+)", r["nr"]).group(1)) >= NUMAR_LOT15:
        return False
    v = vechi.get(r["nr"])
    if v is None or r["nr"] in ATINSE_LOT11:
        return True
    return any(r[k] != v[k] for k in ("stare", "lipsa", "test"))


#: [16.4 pct.1] formatul fix al coloanei „ce lipsește” pentru dovada unui test pilot: fișierul CSV al oracolului și pașii, enumerați (fără intervale)
_RE_DOVADA_PILOT = re.compile(r"dovada e2e: (docs/dovezi/[\w.-]+/jurnal_verificare\.csv); pasi: ([a-z]\.\d+(?:, [a-z]\.\d+)*)")


def _randuri_csv(cale):
    """Rândurile CSV-ului oracolului `cale`, dacă e în index; altfel None."""
    if not _exista_in_index(cale):
        return None
    with io.open(os.path.join(_RAD, cale), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def lipsuri_dovada_pilot(r, plasa, publicare, rows=None, in_index=_exista_in_index):
    """PURĂ (cu plasa e2e, plasa de publicare, rândurile CSV și `in_index` injectate). [16.4 pct.1] Dovada unui număr din DOVADA_PRIN_PILOT:
    (a) coloana testului numește numai `test_pilot_…`, fiecare în `plasa[nr]` și într-un fișier din `publicare`; (b) „ce lipsește” are exact formatul
    `dovada e2e: <csv>; pasi: a.1, a.2`, iar pentru fiecare pas CSV-ul are, pe același commit, un rând code / dupa / trece și un rând haiku / haiku_1 / trece
    cu verificator_independent începând cu „corespunde”, ambele cu captura în index. -> ce lipsește ([] dacă e completă)."""
    nr = r["nr"]
    numite = re.findall(r"`([^`]+)`", r.get("test") or "")
    rele = []
    if not numite:
        rele.append("%s: dovada prin test pilot cere testul numit în coloana testului" % nr)
    for t in numite:
        if "::test_pilot_" not in t:
            rele.append("%s: testul %s nu e `test_pilot_…` (dovada prin test pilot nu amestecă alte teste)" % (nr, t))
        elif t not in plasa.get(nr, []):
            rele.append("%s: testul %s nu există în plasa e2e a numărului" % (nr, t))
        elif os.path.basename(t.split("::")[0]) not in publicare:
            rele.append("%s: testul %s nu e în plasa de publicare" % (nr, t))
    m = _RE_DOVADA_PILOT.fullmatch((r.get("lipsa") or "").strip())
    if not m:
        rele.append("%s: „ce lipsește” nu are formatul exact `dovada e2e: docs/dovezi/<lot>/jurnal_verificare.csv; pasi: a.1, a.2, …` (pașii enumerați, fără intervale)" % nr)
        return rele
    cale, pasi = m.group(1), m.group(2).split(", ")
    rr = rows if rows is not None else _randuri_csv(cale)
    if rr is None:
        return rele + ["%s: %s nu e în index" % (nr, cale)]
    for pas in pasi:
        def bun(verificator, parcurgere):
            return {x["commit"] for x in rr if x["pas"] == pas and x["verificator"] == verificator and x["parcurgere"] == parcurgere and x["verdict"] == "trece"
                    and (verificator != "haiku" or (x.get("verificator_independent") or "").startswith("corespunde")) and in_index(x["captura"])}
        code, haiku = bun("code", "dupa"), bun("haiku", "haiku_1")
        if not code:
            rele.append("%s: pasul %s nu are rând code / dupa / trece cu captura în index în %s" % (nr, pas, cale))
        elif not haiku:
            rele.append("%s: pasul %s nu are rând haiku / haiku_1 / trece cu verificator_independent «corespunde» și captura în index în %s" % (nr, pas, cale))
        elif not code & haiku:
            rele.append("%s: pasul %s: rândurile code / dupa și haiku / haiku_1 nu sunt pe același commit în %s" % (nr, pas, cale))
    return rele


def lipsuri_dovada(r, exista=_captura_amprentata, plasa=None, publicare=None, rows=None, in_index=_exista_in_index):
    """PURĂ (cu `exista`, plasa e2e, plasa de publicare, rândurile CSV și `in_index` injectate). Ce lipsește din dovada rândului rezolvat — [] dacă e completă."""
    nr, t = r["nr"], r["lipsa"]
    if nr in DOVADA_PRIN_PILOT:   # [16.4 pct.1] dovada prin test pilot și pașii oracolului
        return lipsuri_dovada_pilot(r, plasa_e2e() if plasa is None else plasa, plasa_publicarii() if publicare is None else publicare, rows, in_index)
    if nr in DOVADA_PRIN_E2E:   # dovada e e2e-ul (decizia scrisă din DOVADA_PRIN_E2E); testul de capăt la capăt rămâne cerut
        return [] if re.search(r"`[^`]+::test_def_[^`]+`", r.get("test") or "") else [
            "%s: dovada prin e2e (%s) cere testul de capăt la capăt numit în coloana testului" % (nr, DOVADA_PRIN_E2E[nr])]
    rele = []
    i, j = t.find(DOVADA), t.find(DATE_EXISTENTE)
    if i < 0:
        rele.append("%s: rezolvată fără „%s `dovezi/lot<N>/%s_..._f<k>_....png`” (comanda 11.2 pct.3: dovada pe ecran pe firmele de test)"
                    % (nr, DOVADA, nr.lower()))
    else:
        seg = t[i + len(DOVADA):j if j > i else len(t)]
        capturi = re.findall(r"`([^`]+)`", seg)
        if not capturi:
            rele.append("%s: „%s” nu numește nicio captură (între `…`)" % (nr, DOVADA))
        for c in capturi:
            # [lotul 12] subnumărul (409.1, C73.1) se scrie în numele capturii cu punct sau cu „_” (`443_1_f1_…`, `409.1_f1_…`)
            if not re.match(_RE_CAPTURA % re.escape(nr.lower()).replace(r"\.", "[._]"), c):
                rele.append("%s: captura %s nu are forma `dovezi/lot<N>/%s_..._f<k>_....png` (numărul rândului, apoi firma de test — sau "
                            "`admin` / `public`, ecranele fără firmă)" % (nr, c, nr.lower()))
            elif not exista(c):
                rele.append("%s: captura %s nu e în `%s/AMPRENTE.json` sau amprenta ei diferă (regenerare: python "
                            "scripts/dovada_firme_test.py --amprente=%s > %s/AMPRENTE.json)" % (nr, c, *[os.path.dirname(c)] * 3))
    if 0 <= j < i:
        rele.append("%s: „%s” trebuie să stea DUPĂ „%s” (formatul: dovada, apoi datele existente)" % (nr, DATE_EXISTENTE, DOVADA))
        return rele
    if j < 0:
        rele.append("%s: rezolvată fără „%s <migrare `core/migrare_x.py` | script `scripts/x.py` | cod `core/x.py` | neafectate, pentru că "
                    "…>” (comanda 11.2 pct.3: orice reparație acoperă și datele existente)" % (nr, DATE_EXISTENTE))
        return rele
    de = t[j + len(DATE_EXISTENTE):].strip()
    forma = next((f for f in _FORME_DATE if de.startswith(f)), None)
    if forma is None:
        rele.append("%s: „%s” trebuie să înceapă cu una din %s, nu cu %r" % (nr, DATE_EXISTENTE, " / ".join(_FORME_DATE), de[:40]))
    elif forma == "neafectate, pentru că":
        if len(de[len(forma):].strip(" .;")) < 15:
            rele.append("%s: „date existente: neafectate, pentru că …” fără motiv (cel puțin o propoziție)" % nr)
    else:
        m = re.match(r"%s `([^`]+)`" % forma, de)
        if not m:
            rele.append("%s: „date existente: %s” fără fișierul numit între `…`" % (nr, forma))
        elif not os.path.isfile(os.path.join(_RAD, m.group(1))) and not exista(m.group(1)):
            rele.append("%s: „date existente: %s `%s`” — fișierul nu există" % (nr, forma, m.group(1)))
        # pe CUVINTELE numelui capturii (`<nr>_f<k>_vechi_….png`, despărțite de `/ _ .`), nu pe sub-șir: `reevaluare_vechime.png` nu e veche
        if i >= 0 and not any({"vechi"} & set(re.split(r"[/_.]", c)) for c in re.findall(r"`([^`]+)`", t[i:j if j > i else len(t)])):
            rele.append("%s: datele existente au fost atinse (%s), dar nicio captură nu arată un document creat înainte de reparație "
                        "(`vechi` în numele capturii)" % (nr, forma))
    return rele


def test_rezolvata_din_lotul_11_are_dovada_pe_firmele_de_test_si_datele_existente():
    """Comanda 11.2 pct.3. MUTAȚIE: un rând `rezolvată` nou / atins în lotul 11 fără „dovadă firme de test” sau „date existente” -> pică."""
    vechi = randuri_la_pornirea_lotului_11()
    cer = [r for r in randuri() if cere_dovada(r, vechi)]
    # anti-vacuu: la 22.10.2026, 14 rânduri rezolvate ale lotului 11 cer dovada (409, 420, …, C74); un criteriu rupt care nu mai prinde
    # niciunul ar lăsa garda verde pe gol
    assert len(cer) >= 10, [r["nr"] for r in cer]
    rele = [x for r in cer for x in lipsuri_dovada(r)]
    assert not rele, "\n".join(rele)


def test_garda_dovezii_nu_e_vida():
    """Anti-vacuu: garda pică pe un rând sintetic rău și trece pe unul bun; criteriul prinde rândul nou, rândul atins și lista lotului 11."""
    are = {"dovezi/lot11/439_f1_balanta.png", "dovezi/lot11/439_f1_vechi_balanta.png", "dovezi/lot11/439_f1_vechime_balanta.png",
           "dovezi/lot11/439_admin_balanta.png", "dovezi/lot11/439_public_balanta.png", "dovezi/lot11/439_administrator_x.png",
           "core/migrare_x.py"}.__contains__
    bun = dict(nr="439", stare="rezolvată", test="`x::test_def_439_a`", lipsa=(
        "văzut: … dovadă firme de test: `dovezi/lot11/439_f1_balanta.png`, `dovezi/lot11/439_f1_vechi_balanta.png`; "
        "date existente: migrare `core/migrare_x.py` (balanțele preluate refăcute)"))
    assert lipsuri_dovada(bun, are) == []
    # [lotul 13] contextul `admin` / `public` (ecrane fără firmă), cuvânt întreg — `administrator` nu e contextul admin
    _ne = "; date existente: neafectate, pentru că ecranul nu citește documente scrise înainte"
    assert lipsuri_dovada(dict(bun, lipsa="dovadă firme de test: `dovezi/lot11/439_admin_balanta.png`" + _ne), are) == []
    assert lipsuri_dovada(dict(bun, lipsa="dovadă firme de test: `dovezi/lot11/439_public_balanta.png`" + _ne), are) == []
    assert lipsuri_dovada(dict(bun, lipsa="dovadă firme de test: `dovezi/lot11/439_administrator_x.png`" + _ne), are), \
        "`administrator` a trecut drept contextul `admin`"
    # [lotul 13] excepția dovezii prin e2e e ÎNCHISĂ: numai numerele din DOVADA_PRIN_E2E, și numai cu testul e2e numit
    assert set(DOVADA_PRIN_E2E) == {"642", "278.1"}, "alt număr folosește excepția dovezii prin e2e fără decizia scrisă: %s" % sorted(DOVADA_PRIN_E2E)
    fara_captura = dict(bun, lipsa="lotul 12, reparat; dovada pe firmele de test nu se aplică",
                        test="`frontend_test/e2e/e2e_lot12_form2.py::test_def_642_x`")
    assert lipsuri_dovada(dict(fara_captura, nr="642"), are) == []
    assert lipsuri_dovada(dict(fara_captura, nr="642", test=""), are), "excepția 642 fără testul e2e numit"
    assert lipsuri_dovada(dict(fara_captura, nr="643"), are), "excepția dovezii prin e2e s-a întins la alt număr"
    assert lipsuri_dovada(dict(bun, lipsa="date existente: neafectate, pentru că balanța se citește din fișier la import; "
                                         "dovadă firme de test: `dovezi/lot11/439_f1_balanta.png`"), are), "ordinea: întâi dovada, apoi datele"
    rele = {
        "fără nimic": "văzut: ecranul arată totul corect",
        "fără date existente": "dovadă firme de test: `dovezi/lot11/439_f1_balanta.png`",
        "captură inexistentă": "dovadă firme de test: `dovezi/lot11/439_f1_alta.png`; date existente: neafectate, pentru că nu există documente",
        "captură fără firmă": "dovadă firme de test: `dovezi/lot11/439_balanta.png`; date existente: neafectate, pentru că nu există documente",
        "captură altui număr": "dovadă firme de test: `dovezi/lot11/438_f1_x.png`; date existente: neafectate, pentru că nu există documente",
        "neafectate fără motiv": "dovadă firme de test: `dovezi/lot11/439_f1_balanta.png`; date existente: neafectate, pentru că",
        "formă necunoscută": "dovadă firme de test: `dovezi/lot11/439_f1_balanta.png`; date existente: le-am lăsat",
        "migrare inexistentă": "dovadă firme de test: `dovezi/lot11/439_f1_vechi_balanta.png`; date existente: migrare `core/migrare_y.py`",
        "migrare fără captură veche": "dovadă firme de test: `dovezi/lot11/439_f1_balanta.png`; date existente: migrare `core/migrare_x.py`",
        "«vechi» numai ca sub-șir": ("dovadă firme de test: `dovezi/lot11/439_f1_vechime_balanta.png`; date existente: migrare "
                                     "`core/migrare_x.py`"),
    }
    for ce, lipsa in rele.items():
        assert lipsuri_dovada(dict(bun, lipsa=lipsa), are), "garda trece pe un rând rău: %s" % ce
    vechi = {"420": dict(bun, nr="420"), "300": dict(bun, nr="300")}
    assert cere_dovada(dict(bun, nr="460"), vechi), "rândul nou (inexistent la pornirea lotului 11) trebuie să ceară dovada"
    assert cere_dovada(dict(bun, nr="420"), vechi), "numărul lucrat în lotul 11 trebuie să ceară dovada chiar neschimbat"
    assert not cere_dovada(dict(bun, nr="300"), vechi), "rândul vechi, neatins, rămâne pe regula de dinainte"
    assert cere_dovada(dict(bun, nr="300", lipsa="altceva"), vechi), "rândul vechi redeclarat (motiv schimbat) trebuie să ceară dovada"
    assert not cere_dovada(dict(bun, nr="460", stare="parțial"), vechi)


def test_dovada_prin_test_pilot_a_lui_278_1_se_calibreaza_in_ambele_directii():
    """[16.4 pct.1] 278.1 e scutit de captura regulii 11.2 numai cu test pilot + pașii oracolului citați; orice alt număr < 712 rămâne pe regula veche.
    Calibrare (i)–(vii) pe plasa, plasa de publicare, rândurile CSV și indexul injectate. MUTAȚIE: condiția (a) sau (b) scoasă -> pică."""
    T = "frontend_test/e2e/e2e_pilot_f017.py::test_pilot_F017"
    plasa, publicare = {"278.1": [T], "300": [T]}, {"e2e_pilot_f017.py"}
    pasi = ["c.1", "d.1"]
    cit = "dovada e2e: docs/dovezi/16_2_C/jurnal_verificare.csv; pasi: c.1, d.1"

    def rand(pas, verificator, parcurgere, verdict="trece", ind="", commit="a" * 40):
        return dict(commit=commit, pas=pas, verificator=verificator, parcurgere=parcurgere, verdict=verdict, verificator_independent=ind, captura="c/%s_%s.png" % (pas, verificator))
    csv_bun = [x for p in pasi for x in (rand(p, "code", "dupa"), rand(p, "haiku", "haiku_1", ind="corespunde: ok"), rand(p, "code", "inainte", "pica"))]
    r = dict(nr="278.1", stare="rezolvată", test="`%s`" % T, lipsa=cit)

    def lipsuri(rd=r, rows=csv_bun, pl=plasa, pub=publicare, in_index=lambda c: True):
        return lipsuri_dovada(rd, plasa=pl, publicare=pub, rows=rows, in_index=in_index)
    assert lipsuri() == [], "(i) 278.1 cu test pilot și pașii în CSV trebuie să treacă"
    # (ii) alt număr < 712, cu test pilot, fără captură: refuzat ca până acum (regula capturilor)
    assert lipsuri(dict(r, nr="300")), "(ii) alt număr < 712 a scăpat de regula capturilor"
    assert not cere_dovada(dict(r, nr="900"), {}), "numerele ≥ 712 rămân pe e2e-ul din hartă"
    # (iii) test_def_ amestecat cu test_pilot_
    amestec = dict(r, test="`%s`, `frontend_test/e2e/e2e_x.py::test_def_278_1_x`" % T)
    assert any("test_def_278_1_x" in x for x in lipsuri(amestec, pl={"278.1": [T, "frontend_test/e2e/e2e_x.py::test_def_278_1_x"]}))
    # (iv) pas inexistent sau doar pe «inainte» (pică)
    assert any("c.9" in x for x in lipsuri(dict(r, lipsa=cit.replace("d.1", "c.9"))))
    assert any("d.1" in x for x in lipsuri(rows=[x for x in csv_bun if not (x["pas"] == "d.1" and x["parcurgere"] != "inainte")]))
    # (v) test numit, dar absent din plasa de publicare
    assert any("e2e_pilot_f017" in x for x in lipsuri(pub={"altul.py"}))
    # (vi) Haiku «nu corespunde» / «nejudecabil» pe un pas citat; captură în afara indexului; rânduri pe commituri diferite
    for ind in ("nu corespunde: x", "nejudecabil din captură"):
        rau = [dict(x, verificator_independent=ind) if (x["pas"] == "c.1" and x["verificator"] == "haiku") else x for x in csv_bun]
        assert any("c.1" in x for x in lipsuri(rows=rau)), "(vi) haiku %r a trecut" % ind
    assert any("c.1" in x for x in lipsuri(in_index=lambda c: False))
    separat = [dict(x, commit="b" * 40) if x["verificator"] == "haiku" else x for x in csv_bun]
    assert any("același commit" in x for x in lipsuri(rows=separat))
    # (vii) fără citarea din «ce lipsește», cu pași în interval sau cu text în plus
    for lipsa in ("văzut pe ecran", cit.replace("c.1, d.1", "c.1-d.1"), cit + " (verificat)", ""):
        assert lipsuri(dict(r, lipsa=lipsa)), "(vii) formatul %r a trecut" % lipsa
    assert set(DOVADA_PRIN_PILOT) <= set(DOVADA_PRIN_E2E)


def test_manifestul_capturilor_descrie_discul():
    """Manifestul `dovezi/lot<N>/AMPRENTE.json` e generat (`scripts/dovada_firme_test.py --amprente=DIR`), nu scris de mână: când capturile
    sunt pe disc, manifestul e identic cu amprentele lor. Pe un arbore fără imagini (alt worktree; ele stau în ZIP-ul lotului) rămâne
    verificarea din garda de mai sus, pe numele citate. MUTAȚIE: o captură rescrisă după manifest -> pică."""
    sys.path.insert(0, os.path.join(_RAD, "scripts"))
    import dovada_firme_test as dft
    manifeste = sorted(glob.glob(os.path.join(_RAD, "dovezi", "lot*", "AMPRENTE.json")))
    assert manifeste, "niciun manifest de capturi în dovezi/lot*/ — capturile lotului 11 sunt citate în DEFICIENTE"
    for m in manifeste:
        director = os.path.relpath(os.path.dirname(m), _RAD)
        assert _in_index(os.path.relpath(m, _RAD)), "%s nu e în index (git add)" % m
        pe_disc = dft.amprente_capturi(director)
        if pe_disc:
            assert json.load(io.open(m, encoding="utf-8")) == pe_disc, (
                "%s nu mai descrie capturile de pe disc — regenerează: python scripts/dovada_firme_test.py --amprente=%s > %s"
                % (os.path.relpath(m, _RAD), director, os.path.relpath(m, _RAD)))
