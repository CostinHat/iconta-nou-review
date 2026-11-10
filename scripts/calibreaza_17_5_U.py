# -*- coding: utf-8 -*-
"""scripts/calibreaza_17_5_U.py — probele pe cazuri reale ale lotului de unelte 17.5-U (U.1 cazurile a–d, U.2 cazul (e), U.3 pe loturile 17.5-D / 17.5-E / L, U.4 sha256 înainte și după,
U.7 criteriile (a)–(c)). Nu e rulare a porții: iese cu 1 la orice abatere (repari cauza în perimetrul lotului și reiei, cel mult de două ori).
Ia lacătul pe iconta_test și 8019 (scripts/lacat_test.py) și pornește numai dacă 8019 e liber (`ss -ltn | grep :8019` gol, `lacat_test.py stare` = liber); la sfârșit 8019 e liber din nou și baza e restaurată.
Rezultatul: docs/dovezi/17_5_U/calibrare_17_5_U.txt (un rând pe caz) și calibrare_jurnal.log (jurnalul cazurilor, separat de jurnalul comun al lotului).

Uz:
  calibreaza_17_5_U.py [--lot-anterior=<lot>]     L = lotul anterior pentru Q10 (implicit 17.5-E2 dacă ~/ghid_incoming/oprite/OPRIT_17.5-E2.txt spune «publicat», altfel 17.5-D)"""
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import argumente_script  # noqa: E402
import lacat_test as LT  # noqa: E402
import verificator_design as VD  # noqa: E402

LOT = "17.5-U"
DOVEZI = os.path.join(RAD, "docs", "dovezi", "17_5_U")
ALT = "/tmp/calibrare_17_5_U_alt"
SCRIPT_FALS = "/tmp/calibrare_17_5_U_script"
DEP = os.path.expanduser("~/calibrare_17_5_U_dep")
PRINCIPAL = os.path.expanduser("~/iconta_nou")
REZ = []
SERVER_FALS = ("import socket, sys, time\ns = socket.socket()\ns.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)\ns.bind(('127.0.0.1', int(sys.argv[1])))\ns.listen(1)\ntime.sleep(600)\n")


def caz(nume, ok, detalii=""):
    REZ.append((nume, bool(ok), detalii))
    print("%s %s%s" % ("OK     " if ok else "ABATERE", nume, (" — " + detalii) if detalii else ""))


def sha256(cale):
    return hashlib.sha256(open(cale, "rb").read()).hexdigest() if os.path.exists(cale) else "absent"


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def git(cwd, *a):
    return sh(["git", *a], cwd=cwd).stdout.strip()


def port_liber():
    return not VD.port_ocupat(8019)


def server_fals(director):
    """Server fals pe 8019 (un script al cărui nume conține «uvicorn»), pornit din `director` într-o sesiune proprie."""
    os.makedirs(director, exist_ok=True)
    os.makedirs(SCRIPT_FALS, exist_ok=True)
    script = os.path.join(SCRIPT_FALS, "uvicorn_fals.py")
    open(script, "w").write(SERVER_FALS)
    p = subprocess.Popen([sys.executable, script, "8019"], cwd=director, start_new_session=True)
    for _ in range(50):
        if VD.port_ocupat(8019):
            break
        time.sleep(0.1)
    return p


def opreste_fals(p):
    if p.poll() is None:
        p.kill()
    p.wait()


def restaureaza():
    sh(["sh", "scripts/baza_test.sh", "restaureaza"], cwd=RAD)


def worktree_temporar(cale_martor):
    """Un worktree temporar cu baza_test.sh gol și un e2e fals care scrie fișierul-martor; venv-ul worktree-ului lotului."""
    wt = tempfile.mkdtemp(prefix="calibrare_17_5_U_wt_", dir="/tmp")
    os.makedirs(os.path.join(wt, "scripts", "bin"))
    open(os.path.join(wt, "scripts", "baza_test.sh"), "w").write("#!/bin/sh\nexit 0\n")
    open(os.path.join(wt, "scripts", "e2e_poarta.py"), "w").write("open(%r, 'w').write('rulat')\n" % cale_martor)
    os.symlink(os.path.join(RAD, "venv"), os.path.join(wt, "venv"))
    return wt


def u1_ab():
    import poarta_lib as L
    martor = os.path.join(tempfile.mkdtemp(prefix="calibrare_17_5_U_m_", dir="/tmp"), "martor")
    # a. server fals pornit din afara worktree-ului și a directoarelor temporare ale uneltelor
    wt = worktree_temporar(martor)
    p = server_fals(ALT)
    try:
        _, teste = L.ruleaza_trepte(wt, tempfile.mkdtemp(dir="/tmp"), LOT, pytest_ids=[], e2e_fisiere=["e2e_x.py"], verificator=False)
        ses = [t for t in teste if t["nume"] == "plasa_e2e::sesiune"]
        caz("U.1 a: server fals din %s pe 8019 + ruleaza_trepte = refuz cu numele procesului, fișierul-martor absent, serverul viu" % ALT,
            len(ses) == 1 and ("ocupat de pid %d" % p.pid) in ses[0]["mesaj"] and "uvicorn" in ses[0]["mesaj"] and not os.path.exists(martor) and p.poll() is None, ses[0]["mesaj"] if ses else "fără sesiune")
    finally:
        opreste_fals(p)
    # b. același server din /tmp/verificator_design
    p = server_fals(VD.TEMP)
    try:
        _, teste = L.ruleaza_trepte(wt, tempfile.mkdtemp(dir="/tmp"), LOT, pytest_ids=[], e2e_fisiere=["e2e_x.py"], verificator=False)
        jurnal = [ln for ln in open(os.environ["LOT_JURNAL"], encoding="utf-8") if "\telibereaza_8019\t" in ln and ("pid %d" % p.pid) in ln]
        caz("U.1 b: același server din %s = oprit, logat (faza elibereaza_8019, patru valori), fișierul-martor apare, portul liber" % VD.TEMP,
            port_liber() and os.path.exists(martor) and p.wait(timeout=30) is not None and bool(jurnal), (jurnal[0].strip() if jurnal else "fără rând în jurnal")[:300])
    finally:
        opreste_fals(p)
        shutil.rmtree(wt, ignore_errors=True)
        shutil.rmtree(VD.TEMP, ignore_errors=True)
    # c. serverul real al worktree-ului, cu stare.json ștearsă (cazul 17.5-E)
    r = sh(["sh", "scripts/porneste_8019.sh"], cwd=RAD)
    pornit = VD.port_ocupat(8019)
    stare = VD.STARE
    sters = False
    if os.path.exists(stare):
        os.remove(stare)
        sters = not os.path.exists(stare)
    proprietar = VD.proprietari_port(8019)[0] if pornit else {}
    r2 = sh([os.path.join(RAD, "venv", "bin", "python"), "scripts/verificator_design.py", "opreste"], cwd=RAD)
    caz("U.1 c: porneste_8019.sh (server real %s), stare.json ștearsă, verificator_design.py opreste îl oprește" % (("pid %s" % proprietar.get("pid")) if proprietar else "nepornit"),
        r.returncode == 0 and pornit and sters is True and r2.returncode == 0 and port_liber(), "pornit=%s stare.json ștearsă=%s; opreste: ieșire %d: %s" % (pornit, sters, r2.returncode, r2.stdout.strip()[-160:]))
    restaureaza()
    # d. server fals pe 8019 + porneste_8019.sh = ieșire 1 cu numele procesului
    p = server_fals(ALT)
    try:
        r = sh(["sh", "scripts/porneste_8019.sh"], cwd=RAD)
        caz("U.1 d: server fals pe 8019 + porneste_8019.sh = ieșire 1 cu numele procesului", r.returncode == 1 and ("pid %d" % p.pid) in r.stderr + r.stdout and "uvicorn_fals.py" in r.stderr + r.stdout and p.poll() is None,
            (r.stdout + r.stderr).strip()[-300:])
    finally:
        opreste_fals(p)
    caz("U.1: 8019 liber după cazurile a–d", port_liber() and not sh("ss -ltn | grep :8019", shell=True).stdout)


def u2_e(p_commit):
    """Cazul (e): cleiul relansării din scripts/poarta_rulare.py, pe un depozit temporar (clona lui ~/iconta_nou, cu P adus din worktree)."""
    import poarta_clasifica as C
    shutil.rmtree(DEP, ignore_errors=True)
    sh(["git", "clone", "--local", "-q", PRINCIPAL, DEP], check=True)
    # exclude-ul din ~/iconta_nou nu se copiază printr-un git clone; .gitignore are numai «venv/», fără import_fiscalos
    with open(os.path.join(DEP, ".git", "info", "exclude"), "a") as f:
        f.write("/venv\n/import_fiscalos\n")
    os.symlink(os.path.join(PRINCIPAL, "venv"), os.path.join(DEP, "venv"))
    os.symlink(os.path.join(PRINCIPAL, "import_fiscalos"), os.path.join(DEP, "import_fiscalos"))
    sh(["git", "fetch", "-q", RAD, p_commit], cwd=DEP, check=True)
    sh(["git", "checkout", "-q", "-b", "lucru/calibrare-17-5-u", p_commit], cwd=DEP, check=True)       # ramura curentă se creează înainte de a muta main
    sh(["git", "branch", "-f", "main", p_commit], cwd=DEP, check=True)
    baza = json.load(open(os.path.join(DEP, "docs", "dovezi", "17_5_U", "baza.json"), encoding="utf-8"))
    diff_lot = set(git(DEP, "diff", "--name-only", baza["antet"]["commit_baza"], p_commit).splitlines())
    inv_e = C._inventar_e()
    pe_fisier = {}
    for t in baza["teste"]:
        f = t["nume"].split("::")[0]
        pe_fisier.setdefault(f, []).append(t)
    candidat = None
    for f, ts in sorted(pe_fisier.items(), key=lambda kv: len(kv[1])):
        if f.startswith("core/test_") and f not in diff_lot and os.path.exists(os.path.join(DEP, f)) and all(t["rezultat"] == "trece" for t in ts) and len(ts) >= 2 \
                and not any((os.path.basename(f), t["nume"].split("::")[-1]) in inv_e for t in ts):
            candidat = f
            break
    if not candidat:
        caz("U.2 e: fișier de test pentru nucleul clonei", False, "nu s-a găsit în baza.json")
        return
    open(os.path.join(DEP, "scripts", "poarta_nucleu.txt"), "w").write(candidat + "\n")
    open(os.path.join(DEP, "scripts", "e2e_poarta.py"), "w").write("import sys\nsys.exit(3)\n")
    open(os.path.join(DEP, "verificator_conformitate.py"), "w").write("print('TOTAL: 0')\n")
    baza["antet"]["commit_baza"] = p_commit
    baza["antet"]["manifest_sha256"] = sha256(os.path.join(DEP, "scripts", "plasa_16_2.manifest"))
    json.dump(baza, open(os.path.join(DEP, "docs", "dovezi", "17_5_U", "baza.json"), "w"), indent=1, ensure_ascii=False)
    sh(["git", "add", "scripts/poarta_nucleu.txt", "scripts/e2e_poarta.py", "verificator_conformitate.py", "docs/dovezi/17_5_U/baza.json"], cwd=DEP, check=True)
    sh(["git", "-c", "user.email=calibrare@iconta", "-c", "user.name=calibrare", "commit", "-q", "--no-verify", "-m", "calibrare 17.5-U: nucleu cu un fișier, e2e fals cu cod 3, verificator fals, baza = P"], cwd=DEP, check=True)
    murdar = git(DEP, "status", "--porcelain", "--untracked-files=normal")
    caz("U.2 e: arborele clonei e curat înainte de poartă", murdar == "", murdar[:200])
    if murdar:
        return
    comun_pr = git(PRINCIPAL, "rev-parse", "--path-format=absolute", "--git-common-dir")
    f_verdicte, f_stare = os.path.join(comun_pr, "poarta_verdicte.log"), os.path.join(comun_pr, "lot_stare_17_5_U.json")
    inainte = (sha256(f_verdicte), sha256(f_stare))
    env = dict(os.environ, LOT=LOT, LACAT_TEST_PID=str(os.getpid()), POARTA_PLASA_FIX="scripts/plasa_16_2.manifest", POARTA_JURNALE=tempfile.mkdtemp(prefix="calibrare_17_5_U_J_", dir="/tmp"))
    env.pop("LOT_JURNAL", None)
    r = subprocess.run(["sh", "scripts/poarta_lot.sh"], cwd=DEP, env=env, capture_output=True, text=True, timeout=3 * 3600)
    open(os.path.join(DOVEZI, "calibrare_e_poarta.out"), "w", encoding="utf-8").write(r.stdout + r.stderr)
    comun = git(DEP, "rev-parse", "--path-format=absolute", "--git-common-dir")
    verdicte = [ln for ln in open(os.path.join(comun, "poarta_verdicte.log"), encoding="utf-8") if "lot=17.5-U" in ln] if os.path.exists(os.path.join(comun, "poarta_verdicte.log")) else []
    stare = json.load(open(os.path.join(comun, "lot_stare_17_5_U.json"))) if os.path.exists(os.path.join(comun, "lot_stare_17_5_U.json")) else {}
    infra = [ln for ln in verdicte if ln.startswith("INFRA ")]
    sha_dep = git(DEP, "rev-parse", "HEAD")
    sumar = [ln for ln in r.stdout.splitlines() if re.match(r"\[poarta\] INFRA [0-9a-f]{40} ", ln)]
    zero = all(re.search(r"%s 0\b" % k, sumar[-1]) for k in ("baza_mutata", "nou_regresie", "invalid", "asertiuni_scazute")) if sumar else False
    regresii_ok = all(re.search(r"\(a dispărut din rulare\)$", ln.strip()) for ln in r.stdout.splitlines() if ln.strip().startswith("regresie:"))
    caz("U.2 e: trei linii INFRA <sha> și nicio linie VERDE / ROSU în poarta_verdicte.log al clonei", len(infra) == 3 and len(verdicte) == 3 and all(ln.split()[1] == sha_dep for ln in infra), "%d linii, %d INFRA" % (len(verdicte), len(infra)))
    caz("U.2 e: stare[infra] cu 3 intrări (aceeași sha), stare[complete] și stare[regresii] goale, stare[oprit] = «infra ×3: …»",
        len(stare.get("infra", [])) == 3 and len({e["sha"] for e in stare["infra"]}) == 1 and stare.get("complete") == [] and stare.get("regresii") == [] and str(stare.get("oprit", "")).startswith("infra ×3:"),
        json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in stare.items()}, ensure_ascii=False)[:300])
    caz("U.2 e: lot_picate_17_5_U.json absent, scripts/poarta_ultima.txt absent în clonă, ieșirea 3",
        not os.path.exists(os.path.join(comun, "lot_picate_17_5_U.json")) and not os.path.exists(os.path.join(DEP, "scripts", "poarta_ultima.txt")) and r.returncode == 3, "ieșire %d" % r.returncode)
    caz("U.2 e: nu e cazul mixt (infra numai ::sesiune, regresii numai «a dispărut din rulare», celelalte clase 0)", zero and regresii_ok and sumar != [], sumar[-1][:300] if sumar else "fără linie [poarta] INFRA")
    caz("U.2 e: poarta_verdicte.log și lot_stare_17_5_U.json din depozitul principal neatinse (sha256 înainte = după; absent = absent)", (sha256(f_verdicte), sha256(f_stare)) == inainte, "%s | %s" % inainte)
    shutil.copy(os.path.join(comun, "poarta_verdicte.log"), os.path.join(DOVEZI, "calibrare_e_poarta_verdicte.log")) if os.path.exists(os.path.join(comun, "poarta_verdicte.log")) else None
    restaureaza()


def u3(anterior):
    cazuri = [("17.5-D", 0), ("17.5-E", 3)] + ([(anterior, 0)] if anterior not in ("17.5-D", "17.5-E") else [])
    for lot, asteptat in cazuri:
        r = sh(["sh", "scripts/asteapta_poarta.sh", lot, "5"], cwd=RAD)
        caz("U.3: scripts/asteapta_poarta.sh %s iese cu %d pe starea reală" % (lot, asteptat), r.returncode == asteptat, "ieșire %d: %s" % (r.returncode, r.stdout.strip()))


def u4():
    man = os.path.join(RAD, "scripts", "plasa_16_2.manifest")
    copie = tempfile.mkdtemp(prefix="calibrare_17_5_U_m_", dir="/tmp") + "/m.manifest"
    shutil.copy(man, copie)
    py = os.path.join(RAD, "venv", "bin", "python")
    gen = os.path.join(RAD, "scripts", "genereaza_manifest_plasa.py")
    h0 = sha256(copie)
    cazuri = [(["--help"], 0), (["-h"], 0), ([], 2), ([copie], 2), (["--x"], 2), (["--scrie", "--verifica", copie], 2), (["--verifica", copie], 0)]
    for argv, cod in cazuri:
        r = sh([py, gen, *argv], cwd="/tmp")
        caz("U.4: genereaza_manifest_plasa.py %s = ieșire %d, sha256 %s…" % (" ".join(a if a != copie else "<copie>" for a in argv) or "(fără argument)", cod, h0[:12]), r.returncode == cod and sha256(copie) == h0,
            "ieșire %d, sha256 după %s…" % (r.returncode, sha256(copie)[:12]))
    open(copie, "a").write("frontend_test/e2e/e2e_inventat_u4.py\tabc\t3\tpython -m pytest -q x\n")
    h1 = sha256(copie)
    r = sh([py, gen, "--scrie", copie], cwd="/tmp")
    caz("U.4: --scrie pe o copie cu un rând inventat = ieșire 1 cu rândul numit, copia neschimbată", r.returncode == 1 and "e2e_inventat_u4.py" in r.stdout and sha256(copie) == h1, "ieșire %d" % r.returncode)


def u7():
    intrare = os.path.join(RAD, "docs", "dovezi", "17_5_D", "teste_atinse_baza.txt")
    iesire = os.path.join(DOVEZI, "inventar_rosii_baza.txt")
    r = sh([os.path.join(RAD, "venv", "bin", "python"), "scripts/inventar_rosii_baza.py", intrare], cwd=RAD)
    randuri = [ln.split(" | ") for ln in open(iesire, encoding="utf-8").read().splitlines()] if os.path.exists(iesire) else []
    sha = re.search(r"main ([0-9a-f]{40})", open(intrare, encoding="utf-8").readline()).group(1)
    caz("U.7: pe teste_atinse_baza.txt scrie exact 32 de rânduri (ieșire 0)", r.returncode == 0 and len(randuri) == 32, "%d rânduri" % len(randuri))
    pe_cauza = {}
    for rd in randuri:
        pe_cauza[rd[2]] = pe_cauza.get(rd[2], 0) + 1
    caz("U.7 (a): test_def_602_563 și test_def_618 au cauza «data de azi» sau «luna curentă»", all(any(rd[1].startswith(n) and rd[2] in ("data de azi", "luna curentă") for rd in randuri) for n in ("test_def_602_563", "test_def_618")), json.dumps(pe_cauza, ensure_ascii=False))
    caz("U.7 (b): zero «necunoscută» pe cele 32", pe_cauza.get("necunoscută", 0) == 0)
    rele = []
    for fis, test, cauza, loc in randuri:
        if cauza in ("ceas înghețat", "luna curentă", "data de azi"):
            cale, nr = loc.rsplit(":", 1)
            linie = sh(["git", "show", "%s:%s" % (sha, cale)], cwd=RAD).stdout.splitlines()[int(nr) - 1]
            if not any(j in linie for j in ("date.today", "datetime.now", "datetime.datetime.now", "new Date", "Date.now", "DATA_REF", "MOMENT_REF")):
                rele.append("%s:%s -> %r" % (test, loc, linie[:80]))
    caz("U.7 (c): linia citată la «ceas înghețat» / «luna curentă» / «data de azi» conține un token de ceas", not rele, "; ".join(rele)[:300])


def main(argv):
    a = argumente_script.citeste(argv, __doc__, cu_valoare=("--lot-anterior=",), prefix="[calibreaza_17_5_U]")
    anterior = next((x.split("=", 1)[1] for x in a if x.startswith("--lot-anterior=")), None)
    if anterior is None:
        f = os.path.expanduser("~/ghid_incoming/oprite/OPRIT_17.5-E2.txt")
        anterior = "17.5-E2" if os.path.exists(f) and open(f, encoding="utf-8").read().startswith("OPRIT — gata: 17.5-E2 publicat") else "17.5-D"
    if git(RAD, "status", "--porcelain", "--untracked-files=no", "--", "scripts", "core"):
        print("[calibreaza_17_5_U] REFUZ: scripts/ sau core/ au modificări necomise (P = ultimul commit de cod).", file=sys.stderr)
        return 1
    if LT.ia(os.getpid(), "calibreaza_17_5_U"):
        return 1
    os.environ["LACAT_TEST_PID"] = str(os.getpid())
    if not port_liber():
        print("[calibreaza_17_5_U] REFUZ: 8019 e ocupat: %s" % "; ".join(VD._descrie(p) for p in VD.proprietari_port(8019)), file=sys.stderr)
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
        u1_ab()
        u2_e(p_commit)
        u3(anterior)
        u4()
        u7()
    finally:
        if VD.port_ocupat(8019):
            VD.opreste()
        shutil.rmtree(DEP, ignore_errors=True)
        restaureaza()
    caz("8019 liber la sfârșit (ss -ltn | grep :8019 gol)", port_liber() and not sh("ss -ltn | grep :8019", shell=True).stdout)
    with open(os.path.join(DOVEZI, "calibrare_17_5_U.txt"), "w", encoding="utf-8") as f:
        f.write("calibrare 17.5-U pe P=%s, lot anterior L=%s\n" % (p_commit, anterior))
        for nume, ok, det in REZ:
            f.write("%s %s%s\n" % ("OK     " if ok else "ABATERE", nume, (" — " + det) if det else ""))
    abateri = [n for n, ok, _ in REZ if not ok]
    print("\n%d cazuri, %d abateri" % (len(REZ), len(abateri)))
    return 1 if abateri else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
