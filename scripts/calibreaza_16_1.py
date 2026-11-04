# -*- coding: utf-8 -*-
"""scripts/calibreaza_16_1.py — calibrarea pe ambele direcții a porții și a contractului de publicare (comanda 16.1, pct.1h și 4; jurnalul, pct.2). Rulează pe o COPIE
(git clone local) a commitului curent, cu jurnal, HOME și depozit temporare — nu atinge depozitul lotului. Scrie docs/dovezi/16_1/calibrare.txt: un rând pe caz,
„ATINS” (comportamentul cerut) sau „RATAT”; ieșire 1 dacă un caz e ratat. Datele sunt sintetice (se spune pe rând), codul judecat e cel din scripts/."""
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time

AICI = os.path.dirname(os.path.abspath(__file__))
RAD = os.path.dirname(AICI)
REZ = []


def caz(nume, ok, detaliu=""):
    REZ.append((nume, ok, detaliu))
    print("%s  %s  %s" % ("ATINS" if ok else "RATAT", nume, detaliu))


def sh(cmd, cwd, env=None, intrare=None):
    return subprocess.run(cmd, cwd=cwd, env=env, input=intrare, capture_output=True, text=True, shell=isinstance(cmd, str))


def depozit(tmp):
    d = os.path.join(tmp, "dep")
    sh(["git", "init", "-q", "-b", "main", d], tmp)
    for k, v in (("user.email", "c@c"), ("user.name", "c"), ("core.hooksPath", os.path.join(RAD, "scripts", "githooks"))):
        sh(["git", "config", k, v], d)
    return d


def commit(d, nume, text, mesaj="x"):
    os.makedirs(os.path.dirname(os.path.join(d, nume)), exist_ok=True)
    open(os.path.join(d, nume), "w").write(text)
    sh(["git", "add", nume], d)
    sh(["git", "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", mesaj], d)
    return sh(["git", "rev-parse", "HEAD"], d).stdout.strip()


def clasificare():
    sys.path.insert(0, AICI)
    import poarta_clasifica as C
    sh_ = lambda n, r, **k: dict(nume=n, rezultat=r, infra=k.get("infra", False), asertiuni=k.get("a", 1))   # noqa: E731
    inv = {("e2e_x.py", "test_numerotat"): "R999"}
    baza = [sh_("core/test_a.py::test_verde", "trece"), sh_("frontend_test/e2e/e2e_x.py::test_numerotat", "pica"), sh_("core/test_b.py::test_rosu_nenumerotat", "pica")]
    cand = [sh_("core/test_a.py::test_verde", "pica"), sh_("frontend_test/e2e/e2e_x.py::test_numerotat", "pica"), sh_("core/test_b.py::test_rosu_nenumerotat", "pica")]
    r = C.clasifica(cand, baza, set(), RAD, True, inv)
    caz("1h/1a verde pe bază și roșu pe candidat = regresie de lot", r["regresie"] == ["core/test_a.py::test_verde"], "regresii=%s" % r["regresie"])
    caz("1h un test roșu pe main și numerotat în inventar = restanță, nu regresie", len(r["restanta"]) == 1 and "R999" in r["restanta"][0] and "frontend_test/e2e/e2e_x.py::test_numerotat" not in r["regresie"], str(r["restanta"]))
    caz("1h un test roșu pe main și nenumerotat = oprire (baza s-a mișcat)", r["baza_mutata"] == ["core/test_b.py::test_rosu_nenumerotat"] and not C.este_curat(r), str(r["baza_mutata"]))
    r = C.clasifica(baza[:1] + [sh_("core/test_nou.py::test_nou", "trece")], baza[:1], set(), RAD, True, inv)
    caz("1a test absent din bază, fișierul lui în afara diff-ului = test invalid", any("test_nou" in x for x in r["invalid"]), str(r["invalid"]))
    r = C.clasifica(baza[:1] + [sh_("core/test_nou.py::test_nou", "pica")], baza[:1], {"core/test_nou.py"}, RAD, True, inv)
    caz("1a test nou cu fișierul în diff, roșu = regresie de lot", r["nou_regresie"] == ["core/test_nou.py::test_nou"], str(r["nou_regresie"]))
    r = C.clasifica([sh_("core/test_a.py::test_verde", "pica", infra=True)], baza[:1], set(), RAD, False, inv)
    caz("1a eroare de infrastructură = clasă proprie (nu regresie)", r["infra"] == ["core/test_a.py::test_verde"] and not r["regresie"], str(r["infra"]))


def reluare(tmp):
    sys.path.insert(0, AICI)
    import poarta_rulare as PR
    d = depozit(os.path.join(tmp))
    baza = commit(d, "a.txt", "a\n")
    commit(d, "scripts/lot.py", "x = 1\n", "lot")
    commit(d, "core/test_t.py", "def test_t():\n    assert 1\n    assert 2\n", "test")
    rosu = sh(["git", "rev-parse", "HEAD"], d).stdout.strip()
    bt = [{"nume": "core/test_t.py::test_t", "rezultat": "trece", "asertiuni": 2}]
    picate = ["core/test_t.py::test_t"]
    commit(d, "scripts/lot.py", "x = 2\n", "reparatie")
    caz("1h reluare curată (fișier deja în diff-ul lotului) = trece", PR.motiv_refuz_reluare(d, baza, rosu, picate, {}, bt) is None)
    commit(d, "scripts/nou.py", "y = 1\n", "fisier nou")
    m = PR.motiv_refuz_reluare(d, baza, rosu, picate, {}, bt)
    caz("1h reluare cu un fișier nou în diff = refuz, cu numele lui", bool(m) and "scripts/nou.py" in m, str(m))
    m = PR.motiv_refuz_reluare(d, baza, rosu, picate, {"scripts/nou.py": "motiv scris de arhitect"}, bt)
    caz("1c același fișier în exceptii_<lot>.txt (rând cu motiv) = permis", m is None, str(m))
    commit(d, "core/test_t.py", "def test_t():\n    assert 1\n", "aserțiune scoasă")
    m = PR.motiv_refuz_reluare(d, baza, rosu, picate, {"scripts/nou.py": "motiv"}, bt)
    caz("1h aserțiuni scăzute într-un test picat = refuz", bool(m) and "aserțiuni" in m, str(m))


def hook_uri(tmp):
    d = depozit(os.path.join(tmp, "h"))
    primul = commit(d, "f.txt", "1\n")
    sh(["git", "checkout", "-q", "-b", "lot"], d)
    sha = commit(d, "f.txt", "2\n")
    sh(["git", "checkout", "-q", "main"], d)
    comun = os.path.join(d, ".git")
    r = sh(["git", "merge", "--ff-only", "lot"], d)
    caz("4 încercare de mutare a lui main fără verdict = refuzată de hook", r.returncode != 0 and sh(["git", "rev-parse", "HEAD"], d).stdout.strip() == primul, r.stderr.strip().splitlines()[1][:90] if r.stderr.strip() else "")
    open(os.path.join(comun, "poarta_verdicte.log"), "w").write("VERDE %s lot 2026 manifest=x completa lot=16.1\n" % sha)
    r = sh(["git", "merge", "--ff-only", "lot"], d)
    caz("4 numai VERDE (fără PASS) = refuzată de hook", r.returncode != 0 and sh(["git", "rev-parse", "HEAD"], d).stdout.strip() == primul)
    open(os.path.join(comun, "publica_verdicte.log"), "w").write("PASS %s 16.1 x\n" % sha)
    r = sh(["git", "merge", "--ff-only", "lot"], d)
    caz("4 VERDE + PASS = hook-ul lasă main să se mute", r.returncode == 0 and sh(["git", "rev-parse", "HEAD"], d).stdout.strip() == sha, r.stderr.strip()[:80])
    # pre-push: depozit la distanță gol
    bare = os.path.join(tmp, "dist.git")
    sh(["git", "init", "-q", "--bare", bare], tmp)
    sh(["git", "remote", "add", "origin", bare], d)
    os.remove(os.path.join(comun, "publica_verdicte.log"))
    r = sh(["git", "push", "origin", "lot:main"], d)
    caz("4 push pe main fără PASS = refuzat de pre-push", r.returncode != 0 and "REFUZAT" in r.stderr, r.stderr.strip().splitlines()[0][:90] if r.stderr.strip() else "")
    open(os.path.join(comun, "publica_verdicte.log"), "w").write("PASS %s 16.1 x\n" % sha)
    r = sh(["git", "push", "origin", "lot:main"], d)
    caz("4 push pe main cu VERDE + PASS = trece", r.returncode == 0, r.stderr.strip()[-80:])
    r = sh(["git", "push", "origin", "lot:backup/x"], d)
    caz("4 push pe altă ramură (backup/…) nu e păzit", r.returncode == 0)


def jurnal(tmp):
    env = dict(os.environ, LOT_JURNAL=os.path.join(tmp, "jurnal.log"), LOT="16.1")
    p = subprocess.Popen(["sh", os.path.join(AICI, "cronometru.sh"), "16.1", "proba_omorata", "--", "sleep", "300"], cwd=RAD, env=env, start_new_session=True)
    time.sleep(3)
    os.killpg(p.pid, signal.SIGKILL)
    p.wait()
    sh([sys.executable, os.path.join(AICI, "jurnal_lot.py"), "rezumat", "16.1"], RAD, env)
    r = sh([sys.executable, os.path.join(AICI, "jurnal_lot.py"), "rezumat", "16.1"], RAD, env)
    caz("2 un proces omorât în timpul rulării apare în jurnal ca „intrerupt” (cronometru.sh)", "proba_omorata" in r.stdout and "intrerupt" in r.stdout, r.stdout.strip()[:120])
    # pytest omorât: pluginul din conftest.py (copie curată a depozitului, fără bază de test: conftest-ul real cere mediul de test, deci fișierul de probă e în afara lui)
    t = os.path.join(tmp, "probapl")
    os.makedirs(t)
    open(os.path.join(t, "test_p.py"), "w").write("import time\n\ndef test_lung():\n    time.sleep(300)\n")
    env2 = dict(env, PYTHONPATH=AICI, LOT="16.1")
    p = subprocess.Popen([sys.executable, "-m", "pytest", "-q", "-p", "lot_plugin_pytest", "-p", "no:cacheprovider", "test_p.py"], cwd=t, env=env2, start_new_session=True)
    time.sleep(6)
    os.killpg(p.pid, signal.SIGKILL)
    p.wait()
    r = sh([sys.executable, os.path.join(AICI, "jurnal_lot.py"), "rezumat", "16.1"], RAD, env)
    caz("2 o sesiune pytest omorâtă (pluginul din conftest) apare în jurnal ca „intrerupt”", any(ln.startswith("pytest") and "intrerupt" in ln for ln in r.stdout.splitlines()), r.stdout.strip().splitlines()[-1][:120])
    # sesiune încheiată normal: rând cu început și sfârșit
    env3 = dict(env, LOT_JURNAL=os.path.join(tmp, "jurnal2.log"))
    open(os.path.join(t, "test_p.py"), "w").write("def test_ok():\n    assert True\n")
    sh([sys.executable, "-m", "pytest", "-q", "-p", "lot_plugin_pytest", "-p", "no:cacheprovider", "test_p.py"], t, dict(env3, PYTHONPATH=AICI))
    rows = [ln.split("\t") for ln in open(os.path.join(tmp, "jurnal2.log"))]
    caz("2 sesiune pytest încheiată: două rânduri (început, sfârșit „verde”) cu lot, fază, ora ISO, sha", len(rows) == 2 and rows[0][2] == "inceput" and rows[1][2] == "sfarsit" and rows[1][5] == "verde", "%d rânduri" % len(rows))


def publicare(tmp):
    """Pe o copie a depozitului curent: fișier lipsă = refuz; praguri modificate după pornire = STOP; completă și coerentă = PASS (date sintetice)."""
    cl = os.path.join(tmp, "clona")
    sh(["git", "clone", "-q", "--no-hardlinks", RAD, cl], tmp)
    sh(["git", "checkout", "-q", "-b", "lucru/lot16-1"], cl)
    os.symlink(os.path.join(os.path.expanduser("~/iconta_nou"), "venv"), os.path.join(cl, "venv"))
    acasa = os.path.join(tmp, "acasa")
    os.makedirs(acasa)
    jur = os.path.join(tmp, "j.log")
    env = dict(os.environ, HOME=acasa, LOT_JURNAL=jur, LOT="16.1", PYTHONPATH=os.path.join(cl, "scripts"))
    py = os.path.join(cl, "venv", "bin", "python")
    sha = sh(["git", "rev-parse", "HEAD"], cl).stdout.strip()
    sh(["git", "update-ref", "refs/heads/main", "origin/main"], cl)
    comun = os.path.join(cl, ".git")
    # starea sintetică a unei rulări complete curate pe HEAD
    open(os.path.join(comun, "poarta_verdicte.log"), "w").write("VERDE %s lucru/lot16-1 x manifest=m completa lot=16.1\n" % sha)
    json.dump({"complete": [{"sha": sha, "curat": True}], "reluari": [], "regresii": [], "oprit": None}, open(os.path.join(comun, "lot_stare_16_1.json"), "w"))
    json.dump({"sha": sha, "picate": [], "clase": {}}, open(os.path.join(comun, "lot_picate_16_1.json"), "w"))
    # baza sintetică pentru commitul de bază declarat
    baza = sh(["git", "merge-base", "HEAD", "main"], cl).stdout.strip()
    os.makedirs(os.path.join(cl, "docs", "dovezi", "16_1"), exist_ok=True)
    mh = subprocess.run(["sha256sum", os.path.join(cl, "scripts", "plasa_16_2.manifest")], capture_output=True, text=True).stdout.split()[0]
    json.dump({"antet": {"commit_baza": baza, "manifest_sha256": mh}, "teste": []}, open(os.path.join(cl, "docs", "dovezi", "16_1", "baza.json"), "w"))
    os.makedirs(os.path.join(acasa, "backup_16_1"))
    open(os.path.join(acasa, "backup_16_1", "CLAUDE.md"), "w").write("x")

    def jurnalul_complet():
        for f in ("pornire", "hook", "verificator", "poarta_verificator", "poarta_pytest", "poarta_plasa"):
            i = sh([py, "scripts/jurnal_lot.py", "inceput", "16.1", f], cl, env).stdout.strip() if f != "pornire" else None
            if f == "pornire":
                sh([py, "scripts/jurnal_lot.py", "pornire", "16.1"], cl, env)
            else:
                sh([py, "scripts/jurnal_lot.py", "sfarsit", "16.1", f, i, "verde"], cl, env)
        sh([py, "scripts/jurnal_lot.py", "inceput", "16.1", "publicare"], cl, env)

    def ruleaza():
        return sh([py, "scripts/publica_lot.py"], cl, env)
    # (1) praguri lipsă la pornire
    os.rename(os.path.join(cl, "scripts", "praguri_16_1.txt"), os.path.join(cl, "scripts", "praguri_16_1.txt.ascuns"))
    sh([py, "scripts/jurnal_lot.py", "pornire", "16.1"], cl, env)
    r = ruleaza()
    caz("4 praguri lipsă la pornire = „OPRIT — gata: 16.1 nepublicat, lipsă praguri”", "nepublicat, lipsă praguri" in r.stdout and r.returncode == 1, r.stdout.strip().splitlines()[-1][:100])
    os.rename(os.path.join(cl, "scripts", "praguri_16_1.txt.ascuns"), os.path.join(cl, "scripts", "praguri_16_1.txt"))
    os.remove(jur)
    jurnalul_complet()
    r = ruleaza()
    caz("4 raport lipsă (fișier lipsă) = refuz", r.returncode == 1 and "lipsește raportul" in r.stdout, [x for x in r.stdout.splitlines() if "raportul" in x][:1].__str__()[:100])
    open(os.path.join(acasa, "lot_16_1_raport.md"), "w").write("# raport sintetic de calibrare\n")
    r = ruleaza()
    caz("4 completă și coerentă (poartă VERDE pe HEAD, faze în jurnal, bază, ZIP cu sha și lista diff-ului, backup, perimetru „unelte”) = PASS", r.returncode == 0 and "PASS" in r.stdout, r.stdout.strip().splitlines()[-1][:100])
    # praguri modificate după pornire
    open(os.path.join(cl, "scripts", "praguri_16_1.txt"), "a").write("max poarta_pytest 1\n")
    r = ruleaza()
    caz("4 praguri modificate după pornire = STOP", r.returncode == 1 and "pragurile s-au modificat" in r.stdout, [x for x in r.stdout.splitlines() if "praguri" in x][:1].__str__()[:100])
    sh(["git", "checkout", "-q", "scripts/praguri_16_1.txt"], cl)
    # un lot fără marcajul „unelte” care atinge poarta_lot.sh
    open(os.path.join(cl, "scripts", "praguri_16_1.txt"), "w").write("fără praguri numerice\n")
    os.remove(jur)
    jurnalul_complet()
    r = ruleaza()
    caz("4 lot fără marcajul „unelte” care atinge scripts/poarta_lot.sh = STOP", r.returncode == 1 and "scripts/poarta_lot.sh" in r.stdout, [x for x in r.stdout.splitlines() if "unelte" in x][:1].__str__()[:110])


def main():
    tmp = tempfile.mkdtemp(prefix="calibrare_16_1_")
    try:
        clasificare()
        reluare(tmp)
        hook_uri(os.path.join(tmp))
        jurnal(tmp)
        publicare(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    iesire = os.path.join(RAD, "docs", "dovezi", "16_1", "calibrare.txt")
    os.makedirs(os.path.dirname(iesire), exist_ok=True)
    open(iesire, "w", encoding="utf-8").write("\n".join("%s  %s  %s" % ("ATINS" if ok else "RATAT", n, d) for n, ok, d in REZ) + "\n")
    return 0 if all(ok for _, ok, _ in REZ) else 1


if __name__ == "__main__":
    sys.exit(main())
