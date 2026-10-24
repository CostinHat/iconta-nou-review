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
import glob
import io
import json
import os
import re
import subprocess
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# [17.10.2026, decizia Costin pct.3 — „Marchează 268 în DEFICIENTE ca amânată, cu motivul”] + `amânată`: amânare DECISĂ de Costin, cu motiv
STARI = {"rezolvată", "parțial", "nerezolvată", "nu se aplică", "neverificat", "amânată"}
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
        m = re.match(r"^\| (\d+|N\d+|C\d+) \|(.*)\|\s*$", ln)
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
                m = re.match(r"^test_def_(\d+|n\d+|c\d+)_", n.name)
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
    c = [x for x in nr if x.startswith("C")]
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
        numite = re.findall(r"`([^`]+::test_def_[^`]+)`", r["test"])
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
#: [Comanda 11.1 pct.1–25 și 11.2 pct.2] numerele lucrate în lotul 11 (cele cu textul lotului 10 care trebuie redovedite: 425 / 426 după
#: 439, 428, 429, 409, 436 afișarea, C68–C74 „dă dovada pe aplicație”, 420, 424; restul sunt noi, dar intră și pe criteriul (a))
ATINSE_LOT11 = frozenset(
    ["409", "420", "422", "424", "425", "426", "428", "429", "436", "247", "248"]
    + [str(n) for n in range(439, 453)]
    + ["C%d" % n for n in range(68, 77)])
DOVADA = "dovadă firme de test:"
DATE_EXISTENTE = "date existente:"
_RE_CAPTURA = r"^dovezi/lot\d+/%s_(?:[a-z0-9]+_)*?f\d+(?:_[a-z0-9]+)*\.png$"
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
    v = vechi.get(r["nr"])
    if v is None or r["nr"] in ATINSE_LOT11:
        return True
    return any(r[k] != v[k] for k in ("stare", "lipsa", "test"))


def lipsuri_dovada(r, exista=_captura_amprentata):
    """PURĂ (cu `exista` injectat). Ce lipsește din dovada rândului rezolvat — [] dacă e completă."""
    nr, t = r["nr"], r["lipsa"]
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
            if not re.match(_RE_CAPTURA % re.escape(nr.lower()), c):
                rele.append("%s: captura %s nu are forma `dovezi/lot<N>/%s_..._f<k>_....png` (numărul rândului, apoi firma de test)"
                            % (nr, c, nr.lower()))
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
           "core/migrare_x.py"}.__contains__
    bun = dict(nr="439", stare="rezolvată", test="`x::test_def_439_a`", lipsa=(
        "văzut: … dovadă firme de test: `dovezi/lot11/439_f1_balanta.png`, `dovezi/lot11/439_f1_vechi_balanta.png`; "
        "date existente: migrare `core/migrare_x.py` (balanțele preluate refăcute)"))
    assert lipsuri_dovada(bun, are) == []
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
