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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jurnal_lot as JL  # noqa: E402
import poarta_lib as L  # noqa: E402

RAD = L.RAD


def _versiune_pytest(wt):
    r = subprocess.run(["./venv/bin/python", "-m", "pytest", "--version"], cwd=wt, capture_output=True, text=True)
    return (r.stdout + r.stderr).strip() or "?"


def main():
    IESIRE = os.path.join(RAD, "docs", "dovezi", L.lot_fisier(JL.lot_curent()), "baza.json")   # 16.1-C3: fiecare lot își are baza lui
    baza = subprocess.run(["git", "merge-base", "HEAD", "main"], cwd=RAD, capture_output=True, text=True).stdout.strip()
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
        if L.hash_fisier(os.path.join(wt, L.MANIFEST)) != L.hash_fisier(os.path.join(RAD, L.MANIFEST)):
            print("[baza] REFUZ: manifestul din repo diferă de al commitului de bază.")
            return 1
        if subprocess.run(["./venv/bin/python", "scripts/genereaza_manifest_plasa.py", "--verifica", L.MANIFEST], cwd=wt, capture_output=True).returncode:
            print("[baza] REFUZ: manifestul nu se potrivește cu fișierele bazei.")
            return 1
        trepte, teste = L.ruleaza_trepte(wt, J, procese=os.environ.get("POARTA_PROCESE", "3"))
        cache = {}
        for t in teste:
            f, k = L.cheie_asertiuni(t["nume"])
            t["asertiuni"] = 1 if t["treapta"] == "verificator" else cache.setdefault(f, L.asertiuni(wt, f)).get(k, 0)
        snap = json.load(open(os.path.join(RAD, "docs", "dovezi", "16_0", "snapshot.json")))
        dump = os.path.expanduser("~/backups_test/iconta_test.dump")
        antet = {"commit_baza": baza, "manifest_sha256": L.hash_fisier(os.path.join(RAD, L.MANIFEST)), "snapshot_id": snap["id"],
                 "snapshot_arhiva_sha256": L.hash_fisier(dump), "snapshot_arhiva_la_fel_cu_cea_din_16_0": L.hash_fisier(dump) == snap["arhiva_sha256"],
                 "data": datetime.datetime.now().isoformat(timespec="seconds"), "trepte_s": trepte,
                 "mediu": {"python": platform.python_version(), "sistem": platform.platform(), "gazda": platform.node(),
                           "pytest": _versiune_pytest(wt),
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
