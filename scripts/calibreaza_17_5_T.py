# -*- coding: utf-8 -*-
"""scripts/calibreaza_17_5_T.py — probele pe cazuri reale ale lotului de unelte 17.5-T: T.5 (depășirea de prag sub încărcare străină, G2), T.6 (proba de mediu înaintea plasei), T.8 (proba de contract la
începutul porții). Nu e rulare a porții: iese cu 1 la orice abatere (repari cauza în perimetrul lotului și reiei).
Ia lacătul pe iconta_test și 8019 (scripts/lacat_test.py) și pornește numai dacă 8019 e liber; la sfârșit 8019 e liber din nou și baza e restaurată.
Rezultatul: docs/dovezi/17_5_T/calibrare_17_5_T.txt (un rând pe caz) și calibrare_jurnal.log (jurnalul cazurilor, separat de jurnalul comun al lotului).
  T.5 (ii)  pe o COPIE a jurnalului real (JL.durate poate scrie în jurnal: nu se cheamă pe original) și pe logurile reale incarcare_poarta_17_5_O / O2 / O3.log din ~/ghid_incoming: fazele poarta_plasa ale loturilor
            17.5-O2, 17.5-O3 și 17.5-O (două), cu un prag artificial sub durata măsurată = toate STOP (logurile reale sunt în formatul vechi: nu există dovadă de încărcare străină susținută);
            veghe_incarcare.sh conține formatul citit de parser; (iii) numărătoarea stamp-urilor și a rândurilor «strain» în formatul vechi.
  T.6 (ii)  clonă temporară, nucleu cu un singur test verde pe P, e2e_poarta.py fals: trei încercări cu proba căzută = trei linii INFRA, stare[complete] gol, stare[oprit] «infra ×3: proba de mediu …», ieșirea 3;
            apoi o probă căzută o dată și verde la a doua încercare = o linie INFRA, rularea continuă, stare[infra] gol; poarta_verdicte.log și lot_stare_17_5_T.json din depozitul principal neatinse.
  T.6 (iii) o singură dată, pe P: proba din docs/dovezi/17_5_T/proba_mediu.txt există, numește un test care trece singur de trei ori și rulează verde pe mediul real, cu durata.
  T.8 (c)   pe clonă temporară cu poarta reală: pasi.txt cu textul oracolului, rândul pasului a) pe alt commit, captura lipsă = REFUZ proba_contract înainte de prima treaptă, fără stare; dovezi corecte și lot
            «unelte» fără pasi.txt = poarta pornește (fișier-martor prezent)."""
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import argumente_script  # noqa: E402
import infra_g2 as IG  # noqa: E402
import jurnal_lot as JL  # noqa: E402
import lacat_test as LT  # noqa: E402
import poarta_lib as L  # noqa: E402
import publica_lot as PL  # noqa: E402
import verificator_design as VD  # noqa: E402

LOT = "17.5-T"
DOVEZI = os.path.join(RAD, "docs", "dovezi", "17_5_T")
DEP = os.path.expanduser("~/calibrare_17_5_T_dep")
PRINCIPAL = os.path.expanduser("~/iconta_nou")
GHID = os.path.expanduser("~/ghid_incoming")
REZ = []


def caz(nume, ok, detalii=""):
    REZ.append((nume, bool(ok), detalii))
    print("%s %s%s" % ("OK     " if ok else "ABATERE", nume, (" — " + detalii) if detalii else ""))


def sha256(cale):
    return hashlib.sha256(open(cale, "rb").read()).hexdigest() if os.path.exists(cale) else "absent"


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def git(cwd, *a):
    return sh(["git", *a], cwd=cwd).stdout.strip()


def comun(rad):
    return git(rad, "rev-parse", "--path-format=absolute", "--git-common-dir")


# ── T.5 (ii), (iii): cazurile reale ──────────────────────────────────────────────────────────────────────────────
CAZURI_G2 = [("17.5-O2", "incarcare_poarta_17_5_O2.log", "2026-11-11T15:04:11", "2026-11-11T15:36:25"),
             ("17.5-O3", "incarcare_poarta_17_5_O3.log", "2026-11-11T16:36:45", "2026-11-11T17:08:57"),
             ("17.5-O", "incarcare_poarta_17_5_O.log", "2026-11-11T12:19:40", "2026-11-11T12:51:54"),
             ("17.5-O", "incarcare_poarta_17_5_O.log", "2026-11-11T13:14:39", "2026-11-11T13:46:58")]


def t5():
    copie = os.path.join(tempfile.mkdtemp(prefix="calibrare_17_5_T_j_", dir="/tmp"), "jurnal.log")
    shutil.copy(os.path.join(PRINCIPAL, ".lot_jurnal.log"), copie)
    for lot, log, inceput, sfarsit in CAZURI_G2:
        durate = [d for d in JL.durate(lot, cale=copie) if d[0] == "poarta_plasa" and d[2][:19] == inceput]      # copia jurnalului, nu originalul
        if not durate:
            caz("T.5 ii: %s: faza poarta_plasa de la %s în copia jurnalului real" % (lot, inceput), False, "lipsește")
            continue
        _, id_, i0, i1, rez, sec = durate[0]
        text = open(os.path.join(GHID, log), encoding="utf-8", errors="replace").read() if os.path.exists(os.path.join(GHID, log)) else None
        prag = sec - 1                                                                                                  # prag artificial sub durata măsurată
        d = IG.decide("poarta_plasa", sec, prag, i0, i1, text)
        stop, _ = PL.depasiri_praguri(durate, ["max poarta_plasa %d" % prag], {}, {}, {})
        caz("T.5 ii: %s poarta_plasa %s–%s (%ds > prag artificial %ds), log %s = STOP (nu infra)" % (lot, inceput[11:], sfarsit[11:], sec, prag, log),
            d["decizie"] == "stop" and len(stop) == 1 and stop[0] == "pragul „poarta_plasa” depășit: %ds > %ds" % (sec, prag),
            "decizia %s (%s); depasiri_praguri: %s" % (d["decizie"], d["motiv"], stop[0] if stop else "fără STOP"))
    veghe = open(os.path.join(GHID, "veghe_incarcare.sh"), encoding="utf-8").read()
    caz("T.5 ii: ~/ghid_incoming/veghe_incarcare.sh conține formatul citit de parser (ps cu cputimes, stamp «date '+%F %H:%M:%S'», rândul «strain: pid %s cputimes %s»)",
        "ps -eo pid,pcpu,cputimes" in veghe and "date '+%F %H:%M:%S'" in veghe and "strain: pid %s cputimes %s" in veghe)
    for lot, log in (("17.5-O", "incarcare_poarta_17_5_O.log"), ("17.5-O2", "incarcare_poarta_17_5_O2.log"), ("17.5-O3", "incarcare_poarta_17_5_O3.log")):
        text = open(os.path.join(GHID, log), encoding="utf-8", errors="replace").read()
        stampuri = sum(1 for ln in text.splitlines() if "faza=" in ln and not ln.startswith(" "))
        strain = sum(1 for ln in text.splitlines() if ln.startswith("   strain:"))
        vechi_st, vechi_str = IG.format_vechi(text)
        caz("T.5 iii: %s în formatul vechi: %d din %d stamp-uri și %d din %d rânduri «strain» (fără dată în stamp / fără cputimes); stamp-uri în formatul cerut: %d" % (
            log, vechi_st, stampuri, vechi_str, strain, len(IG.citeste_log(text))), vechi_st == stampuri and vechi_str == strain and not IG.citeste_log(text))


# ── clona temporară (modelul cazului (e) din calibreaza_17_5_U.py) ───────────────────────────────────────────────
def pregateste_clona(p_commit, lotf="17_5_T", unelte=True):
    shutil.rmtree(DEP, ignore_errors=True)
    sh(["git", "clone", "--local", "-q", RAD, DEP], check=True)
    with open(os.path.join(DEP, ".git", "info", "exclude"), "a") as f:
        f.write("/venv\n/import_fiscalos\n")
    os.symlink(os.path.join(PRINCIPAL, "venv"), os.path.join(DEP, "venv"))
    os.symlink(os.path.join(PRINCIPAL, "import_fiscalos"), os.path.join(DEP, "import_fiscalos"))
    sh(["git", "checkout", "-q", "-b", "lucru/calibrare-17-5-t", p_commit], cwd=DEP, check=True)
    sh(["git", "branch", "-f", "main", p_commit], cwd=DEP, check=True)


def comite_clona(mesaj):
    sh(["git", "add", "-A"], cwd=DEP, check=True)
    sh(["git", "-c", "user.email=calibrare@iconta", "-c", "user.name=calibrare", "commit", "-q", "--no-verify", "-m", mesaj], cwd=DEP, check=True)


FALS_E2E = """import os, sys
D = %(d)r
doar = [a for a in sys.argv[1:] if a.startswith("--doar=")]
proba = len(doar) == 1 and "::" in doar[0]
if proba:
    mod = open(os.path.join(D, "mod")).read().strip()
    n = int(open(os.path.join(D, "n")).read()) if os.path.exists(os.path.join(D, "n")) else 0
    open(os.path.join(D, "n"), "w").write(str(n + 1))
    if mod == "cade" or (mod == "o_data" and n < 2):
        sys.exit(3)
    sys.exit(0)
open(os.path.join(D, "martor"), "w").write("rulat")
"""


def t6_clona(p_commit):
    pregateste_clona(p_commit)
    baza = json.load(open(os.path.join(DEP, "docs", "dovezi", "17_5_T", "baza.json"), encoding="utf-8"))
    pe_fisier = {}
    for t in baza["teste"]:
        pe_fisier.setdefault(t["nume"].split("::")[0], []).append(t)
    candidat = next((f for f, ts in sorted(pe_fisier.items(), key=lambda kv: len(kv[1])) if f.startswith("core/test_") and os.path.exists(os.path.join(DEP, f)) and len(ts) >= 2
                     and all(t["rezultat"] == "trece" for t in ts) and f not in set(git(DEP, "diff", "--name-only", baza["antet"]["commit_baza"], p_commit).splitlines())), None)
    if not candidat:
        caz("T.6 ii: fișier de test pentru nucleul clonei", False, "nu s-a găsit în baza.json")
        return
    director = tempfile.mkdtemp(prefix="calibrare_17_5_T_e2e_", dir="/tmp")
    open(os.path.join(DEP, "scripts", "poarta_nucleu.txt"), "w").write(candidat + "\n")
    open(os.path.join(DEP, "scripts", "e2e_poarta.py"), "w").write(FALS_E2E % {"d": director})
    open(os.path.join(DEP, "scripts", "baza_test.sh"), "w").write("#!/bin/sh\nexit 0\n")
    open(os.path.join(DEP, "verificator_conformitate.py"), "w").write("print('TOTAL: 0')\n")
    baza["antet"]["commit_baza"] = p_commit
    baza["antet"]["manifest_sha256"] = sha256(os.path.join(DEP, "scripts", "plasa_16_2.manifest"))
    json.dump(baza, open(os.path.join(DEP, "docs", "dovezi", "17_5_T", "baza.json"), "w"), indent=1, ensure_ascii=False)
    comite_clona("calibrare 17.5-T: nucleu cu un fișier, e2e fals cu proba controlată, verificator fals, baza = P")
    murdar = git(DEP, "status", "--porcelain", "--untracked-files=normal")
    caz("T.6 ii: arborele clonei e curat înainte de poartă", murdar == "", murdar[:200])
    if murdar:
        return
    f_verdicte, f_stare = os.path.join(comun(PRINCIPAL), "poarta_verdicte.log"), os.path.join(comun(PRINCIPAL), "lot_stare_17_5_T.json")
    inainte = (sha256(f_verdicte), sha256(f_stare))
    sha_dep = git(DEP, "rev-parse", "HEAD")

    def ruleaza(mod, sufix):
        for f in ("n", "martor"):
            if os.path.exists(os.path.join(director, f)):
                os.remove(os.path.join(director, f))
        open(os.path.join(director, "mod"), "w").write(mod)
        for f in (os.path.join(comun(DEP), "lot_stare_17_5_T.json"), os.path.join(comun(DEP), "poarta_verdicte.log")):
            if os.path.exists(f):
                os.remove(f)
        env = dict(os.environ, LOT=LOT, LACAT_TEST_PID=str(os.getpid()), POARTA_PLASA_FIX="scripts/plasa_16_2.manifest", POARTA_JURNALE=tempfile.mkdtemp(prefix="calibrare_17_5_T_J_", dir="/tmp"),
                   POARTA_LOG_INCARCARE="/nu/exista")
        env.pop("LOT_JURNAL", None)
        r = subprocess.run(["sh", "scripts/poarta_lot.sh"], cwd=DEP, env=env, capture_output=True, text=True, timeout=3 * 3600)
        open(os.path.join(DOVEZI, "calibrare_%s_poarta.out" % sufix), "w", encoding="utf-8").write(r.stdout + r.stderr)
        verd = [ln for ln in open(os.path.join(comun(DEP), "poarta_verdicte.log"), encoding="utf-8")] if os.path.exists(os.path.join(comun(DEP), "poarta_verdicte.log")) else []
        stare = json.load(open(os.path.join(comun(DEP), "lot_stare_17_5_T.json"))) if os.path.exists(os.path.join(comun(DEP), "lot_stare_17_5_T.json")) else {}
        return r, verd, stare

    r, verd, stare = ruleaza("cade", "a_proba_cazuta")
    infra = [ln for ln in verd if ln.startswith("INFRA ")]
    caz("T.6 ii (a): proba căzută de trei ori = trei linii INFRA <sha>, nicio linie VERDE / ROSU, plasa nu a pornit (fișier-martor absent), ieșirea 3",
        len(infra) == 3 and len(verd) == 3 and all(ln.split()[1] == sha_dep for ln in infra) and not os.path.exists(os.path.join(director, "martor")) and r.returncode == 3,
        "%d linii, %d INFRA, ieșire %d" % (len(verd), len(infra), r.returncode))
    caz("T.6 ii (a): stare[complete] gol, stare[oprit] = «infra ×3: proba de mediu …», trei intrări în stare[infra]",
        stare.get("complete") == [] and str(stare.get("oprit", "")).startswith("infra ×3: proba de mediu ") and len(stare.get("infra", [])) == 3, json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in stare.items()}, ensure_ascii=False)[:300])
    caz("T.6 ii (a): fiecare dintre cele trei încercări pornește din mediu refăcut și rulează proba de două ori (prima rulare + reluarea unică din 17.5-U): contorul probei = 6", open(os.path.join(director, "n")).read() == "6")
    r, verd, stare = ruleaza("o_data", "b_proba_o_data")
    infra = [ln for ln in verd if ln.startswith("INFRA ")]
    caz("T.6 ii (b): proba căzută la prima încercare (cu reluarea ei unică) și verde la a doua = o linie INFRA, apoi rularea continuă (plasa a pornit: fișier-martor prezent)", len(infra) == 1 and os.path.exists(os.path.join(director, "martor")),
        "%d linii INFRA, martor %s, ieșire %d" % (len(infra), os.path.exists(os.path.join(director, "martor")), r.returncode))
    caz("T.6 ii (b): stare[infra] gol după rularea reală, stare[complete] cu o rulare", stare.get("infra") == [] and len(stare.get("complete", [])) == 1, json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in stare.items()}, ensure_ascii=False)[:300])
    caz("T.6 ii: poarta_verdicte.log și lot_stare_17_5_T.json din depozitul principal neatinse (sha256 înainte = după; absent = absent)", (sha256(f_verdicte), sha256(f_stare)) == inainte, "%s | %s" % inainte)
    shutil.rmtree(director, ignore_errors=True)


# ── T.8 (c): proba de contract, pe clonă cu poarta reală ──────────────────────────────────────────────────────────
LOT_P, LOTF_P = "99.9-Z", "99_9_Z"


def t8(p_commit):
    pregateste_clona(p_commit)
    martor = os.path.join(DEP, "martor_plasa")
    for f, c in (("scripts/baza_test.sh", "#!/bin/sh\nexit 0\n"), ("verificator_conformitate.py", "print('TOTAL: 0')\n"), ("scripts/poarta_nucleu.txt", ""),
                 ("scripts/e2e_poarta.py", "import sys\nif not any('::' in a for a in sys.argv):\n    open(%r, 'w').write('rulat')\n" % martor)):
        open(os.path.join(DEP, f), "w").write(c)
    comite_clona("calibrare 17.5-T (T.8): treptele false")
    f_verdicte, f_stare = os.path.join(comun(PRINCIPAL), "poarta_verdicte.log"), os.path.join(comun(PRINCIPAL), "lot_stare_17_5_T.json")
    inainte = (sha256(f_verdicte), sha256(f_stare))
    baza = git(DEP, "merge-base", "HEAD", "main")
    d = os.path.join(DEP, "docs", "dovezi", LOTF_P)
    os.makedirs(os.path.join(d, "capturi"), exist_ok=True)
    man = sha256(os.path.join(DEP, "scripts", "plasa_16_2.manifest"))
    json.dump({"antet": {"commit_baza": baza, "manifest_sha256": man}, "teste": []}, open(os.path.join(d, "baza.json"), "w"))
    cap = os.path.relpath(os.path.join(d, "capturi", "a.png"), DEP)
    text_oracol = "a.1 | 1 | ecran | dom:#x | egal | 5 | descriere\nb.1 | 2 | ecran | dom:#y | egal | 6 | descriere\n"
    cazuri = [("pasi.txt cu textul oracolului în loc de id-uri", "produs", text_oracol, [("a.1", baza, True)], True, True),
              ("rândul pasului a) pe alt commit decât baza", "produs", "a.1\nb.1\n", [("a.1", "0" * 40, True)], True, True),
              ("captura rândului lipsește", "produs", "a.1\nb.1\n", [("a.1", baza, True)], False, True),
              ("dovezi corecte", "produs", "a.1\nb.1\n", [("a.1", baza, True)], True, False),
              ("lot «unelte» fără pasi.txt", "unelte", None, [], True, False)]
    for nume, tip, pasi, randuri, captura, refuz in cazuri:
        for f in (martor, os.path.join(d, "capturi", "a.png"), os.path.join(d, "pasi.txt"), os.path.join(comun(DEP), "lot_stare_%s.json" % LOTF_P)):
            if os.path.exists(f):
                os.remove(f)
        open(os.path.join(DEP, "scripts", "praguri_%s.txt" % LOTF_P), "w").write("%s\nrunde_verificator_max: 1\n" % tip)
        if captura:
            open(os.path.join(d, "capturi", "a.png"), "wb").write(b"\x89PNG")
        if pasi is not None:
            open(os.path.join(d, "pasi.txt"), "w", encoding="utf-8").write(pasi)
        import csv
        with open(os.path.join(d, "jurnal_verificare.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["lot", "parcurgere", "pas", "commit", "verificator", "captura", "verdict"])
            for pas, commit, _ in randuri:
                w.writerow([LOT_P, "inainte", pas, commit, "code", cap, "trece"])
        comite_clona("calibrare T.8: " + nume)
        env = dict(os.environ, LOT=LOT_P, LACAT_TEST_PID=str(os.getpid()), POARTA_PLASA_FIX="scripts/plasa_16_2.manifest", POARTA_JURNALE=tempfile.mkdtemp(prefix="calibrare_17_5_T_J_", dir="/tmp"),
                   LOT_JURNAL=os.path.join(tempfile.mkdtemp(prefix="calibrare_17_5_T_L_", dir="/tmp"), "jurnal.log"))
        r = subprocess.run([os.path.join(DEP, "venv", "bin", "python"), "scripts/poarta_rulare.py"], cwd=DEP, env=env, capture_output=True, text=True, timeout=3600)
        stare_f = os.path.join(comun(DEP), "lot_stare_%s.json" % LOTF_P)
        if refuz:
            caz("T.8 c: %s = REFUZ: proba_contract, ieșirea 1, martorul absent, fără stare" % nume,
                r.returncode == 1 and "[poarta] REFUZ: proba_contract:" in r.stdout and not os.path.exists(martor) and not os.path.exists(stare_f) and "INFRA" not in r.stdout,
                (r.stdout.strip().splitlines() or ["-"])[0][:200])
        else:
            caz("T.8 c: %s = poarta pornește (fără REFUZ, martorul prezent)" % nume, "REFUZ" not in r.stdout and os.path.exists(martor), (r.stdout.strip().splitlines() or ["-"])[0][:200])
    caz("T.8 c: poarta_verdicte.log și lot_stare_17_5_T.json din depozitul principal neatinse (sha256 înainte = după)", (sha256(f_verdicte), sha256(f_stare)) == inainte, "%s | %s" % inainte)


# ── T.6 (iii): proba reală ───────────────────────────────────────────────────────────────────────────────────────
def t6_real():
    cale = os.path.join(RAD, L.PROBA_MEDIU)
    nume, motiv = L.proba_mediu_nume(RAD)
    caz("T.6 iii: %s există și numește un test din plasa fixă" % L.PROBA_MEDIU, nume is not None and nume.split("::")[0] in [os.path.basename(x) for x in L.fisiere_manifest(RAD)], motiv or nume)
    if nume is None:
        return
    text = open(cale, encoding="utf-8").read()
    durate = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", text.split("\n", 1)[1])] if "\n" in text else []
    caz("T.6 iii: trei rulări singure ale testului, fiecare ≥ 1 s, scrise în fișier", len(durate) == 3 and all(x >= 1 for x in durate), "durate %s" % durate)
    sh(["sh", "scripts/baza_test.sh", "restaureaza"], cwd=RAD)
    j = tempfile.mkdtemp(prefix="calibrare_17_5_T_proba_", dir="/tmp")
    env = dict(os.environ, POARTA_SARE="1")
    ok, tip, mesaj, dur, n = L.ruleaza_proba_mediu(RAD, j, env)
    caz("T.6 iii: proba %s rulează verde pe mediul real, durata %.1f s (niciun proces străin nu se oprește)" % (n, dur), ok, "%s %s" % (tip, mesaj))
    caz("T.6 iii: durata probei adaugă %.1f s la poarta_plasa (maximul de referință din scripts/praguri_17_5_T.txt: 2409 s)" % dur, True)


def main(argv):
    argumente_script.citeste(argv, __doc__, prefix="[calibreaza_17_5_T]")
    if git(RAD, "status", "--porcelain", "--untracked-files=no", "--", "scripts", "core"):
        print("[calibreaza_17_5_T] REFUZ: scripts/ sau core/ au modificări necomise (P = ultimul commit de cod).", file=sys.stderr)
        return 1
    if LT.ia(os.getpid(), "calibreaza_17_5_T"):
        return 1
    os.environ["LACAT_TEST_PID"] = str(os.getpid())
    if VD.port_ocupat(8019):
        print("[calibreaza_17_5_T] REFUZ: 8019 e ocupat: %s" % "; ".join(VD._descrie(p) for p in VD.proprietari_port(8019)), file=sys.stderr)
        return 1
    os.makedirs(DOVEZI, exist_ok=True)
    os.environ["LOT"] = LOT
    os.environ["LOT_JURNAL"] = os.path.join(DOVEZI, "calibrare_jurnal.log")
    open(os.environ["LOT_JURNAL"], "w").close()

    def iesire(semnal, _cadru):
        raise SystemExit(128 + semnal)
    for s in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(s, iesire)
    p_commit = git(RAD, "rev-parse", "HEAD")
    try:
        t5()
        t6_clona(p_commit)
        t8(p_commit)
        t6_real()
    finally:
        if VD.port_ocupat(8019):
            VD.opreste()
        shutil.rmtree(DEP, ignore_errors=True)
        sh(["sh", "scripts/baza_test.sh", "restaureaza"], cwd=RAD)
    caz("8019 liber la sfârșit (ss -ltn | grep :8019 gol)", not VD.port_ocupat(8019) and not sh("ss -ltn | grep :8019", shell=True).stdout)
    with open(os.path.join(DOVEZI, "calibrare_17_5_T.txt"), "w", encoding="utf-8") as f:
        f.write("calibrare 17.5-T pe P=%s\n" % p_commit)
        for nume, ok, det in REZ:
            f.write("%s %s%s\n" % ("OK     " if ok else "ABATERE", nume, (" — " + det) if det else ""))
    abateri = [n for n, ok, _ in REZ if not ok]
    print("\n%d cazuri, %d abateri" % (len(REZ), len(abateri)))
    return 1 if abateri else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
