# -*- coding: utf-8 -*-
"""scripts/poarta_baza.py — `sh scripts/poarta_lot.sh --baza` (comanda 16.1, pct.1a).
Rulează poarta COMPLETĂ (verificator, pytest nucleu, plasa e2e din manifest; fără oprire la prima treaptă roșie) pe un worktree curat al commitului de
bază (merge-base cu `main`), pe baza de test restaurată înainte de pytest și înainte de plasa e2e, și scrie docs/dovezi/16_1/baza.json:
pe fiecare test nume stabil, rezultat, durată, număr de aserțiuni; în antet sha-ul bazei, hash-ul manifestului, id-ul snapshotului, mediul.
Manifestul e cel din repo (scripts/plasa_16_2.manifest); un manifest diferit de al bazei = refuz."""
import datetime
import json
import os
import platform
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poarta_lib as L  # noqa: E402

RAD = L.RAD
MANIFEST = "scripts/plasa_16_2.manifest"
NUCLEU = "scripts/poarta_nucleu.txt"
IESIRE = os.path.join(RAD, "docs", "dovezi", "16_1", "baza.json")


def sh(cmd, cwd, env=None, log=None):
    t0 = time.time()
    with open(log or os.devnull, "w") as f:
        r = subprocess.run(cmd, cwd=cwd, env=env, stdout=f, stderr=subprocess.STDOUT, shell=isinstance(cmd, str))
    return r.returncode, round(time.time() - t0, 1)


def main():
    git = lambda *a, cwd=RAD: subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True).stdout.strip()   # noqa: E731
    baza = git("merge-base", "HEAD", "main")
    if not baza:
        print("[baza] REFUZ: nu există merge-base cu main.")
        return 1
    J = os.environ.get("POARTA_JURNALE", "/tmp")
    wt = os.path.join(J, "baza_wt_" + baza[:8])
    subprocess.run(["git", "worktree", "remove", "--force", wt], cwd=RAD, capture_output=True)
    if subprocess.run(["git", "worktree", "add", "--detach", wt, baza], cwd=RAD, capture_output=True, text=True).returncode:
        print("[baza] REFUZ: worktree-ul curat al bazei nu s-a putut crea.")
        return 1
    for nume in ("venv", "import_fiscalos"):
        os.symlink(os.path.join(os.path.expanduser("~/iconta_nou"), nume), os.path.join(wt, nume))
    try:
        if L.hash_fisier(os.path.join(wt, MANIFEST)) != L.hash_fisier(os.path.join(RAD, MANIFEST)):
            print("[baza] REFUZ: manifestul din repo diferă de al commitului de bază.")
            return 1
        py = "./venv/bin/python"
        env = dict(os.environ, POARTA_SARE="1")
        capturi = os.path.join(J, "baza_capturi")
        r, _ = sh([py, "scripts/genereaza_manifest_plasa.py", "--verifica", MANIFEST], wt, env, os.path.join(J, "baza_manifest.log"))
        if r:
            print("[baza] REFUZ: manifestul nu se potrivește cu fișierele bazei (vezi baza_manifest.log).")
            return 1
        trepte, teste = {}, []
        # 1. verificatorul de design (un singur „test”: TOTAL: 0)
        _, d = sh([py, "verificator_conformitate.py"], wt, env, os.path.join(J, "baza_verificator.log"))
        tot = [ln for ln in open(os.path.join(J, "baza_verificator.log"), errors="replace") if "TOTAL" in ln.upper()]
        trece = bool(tot) and "TOTAL: 0" in tot[-1]
        trepte["verificator"] = d
        teste.append({"nume": "verificator::TOTAL", "rezultat": "trece" if trece else "pica", "durata": d, "asertiuni": 1, "mesaj": "" if trece else (tot[-1].strip() if tot else "fără TOTAL")})
        # 2. pytest: nucleul
        sh(["sh", "scripts/baza_test.sh", "restaureaza"], wt, env, os.path.join(J, "baza_restaurare1.log"))
        fisiere = [ln.strip() for ln in open(os.path.join(wt, NUCLEU), encoding="utf-8") if ln.strip() and not ln.startswith("#")]
        jx = os.path.join(J, "baza_pytest.xml")
        _, d = sh([py, "-m", "pytest", "-q", "-n", os.environ.get("POARTA_PROCESE", "3"), "--dist", "loadfile", "--junitxml=" + jx] + fisiere, wt, env, os.path.join(J, "baza_pytest.log"))
        trepte["pytest"] = d
        teste += [dict(t, treapta="pytest") for t in L.citeste_junit(jx, wt)]
        # 3. plasa e2e din manifest
        sh(["sh", "scripts/baza_test.sh", "restaureaza"], wt, env, os.path.join(J, "baza_restaurare2.log"))
        e2e = [ln.split("\t")[0] for ln in open(os.path.join(wt, MANIFEST), encoding="utf-8") if ln.strip() and not ln.startswith("#")]
        jx = os.path.join(J, "baza_e2e.xml")
        env2 = dict(env, PYTEST_ADDOPTS="--junitxml=" + jx)
        _, d = sh([py, "scripts/e2e_poarta.py"] + ["--doar=" + os.path.basename(f) for f in e2e] + [capturi], wt, env2, os.path.join(J, "baza_e2e.log"))
        trepte["plasa_e2e"] = d
        teste += [dict(t, treapta="plasa_e2e") for t in L.citeste_junit(jx, wt)]
        # aserțiuni statice și antet
        cache = {}
        for t in teste:
            if "treapta" not in t:
                t["treapta"] = "verificator"
                continue
            f, k = L.cheie_asertiuni(t["nume"])
            t["asertiuni"] = cache.setdefault(f, L.asertiuni(wt, f)).get(k, 0)
        snap = json.load(open(os.path.join(RAD, "docs", "dovezi", "16_0", "snapshot.json")))
        dump = os.path.expanduser("~/backups_test/iconta_test.dump")
        antet = {"commit_baza": baza, "manifest_sha256": L.hash_fisier(os.path.join(RAD, MANIFEST)), "snapshot_id": snap["id"],
                 "snapshot_arhiva_sha256": L.hash_fisier(dump), "snapshot_arhiva_la_fel_cu_cea_din_16_0": L.hash_fisier(dump) == snap["arhiva_sha256"],
                 "data": datetime.datetime.now().isoformat(timespec="seconds"), "trepte_s": trepte,
                 "mediu": {"python": platform.python_version(), "sistem": platform.platform(), "gazda": platform.node(),
                           "pytest": subprocess.run([py, "-m", "pytest", "--version"], cwd=wt, capture_output=True, text=True).stderr.strip() or "?",
                           "ICONTA_MEDIU": "test", "data_inghetata": "core/ceas_proba.py::DATA_REF"},
                 "total": len(teste), "picate": sum(t["rezultat"] == "pica" for t in teste)}
        os.makedirs(os.path.dirname(IESIRE), exist_ok=True)
        json.dump({"antet": antet, "teste": teste}, open(IESIRE, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("[baza] %d teste, %d picate; trepte %s; scris %s" % (antet["total"], antet["picate"], trepte, os.path.relpath(IESIRE, RAD)))
        return 0
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", wt], cwd=RAD, capture_output=True)


if __name__ == "__main__":
    sys.exit(main())
