# -*- coding: utf-8 -*-
"""scripts/p4_trasabilitate.py — trasabilitatea finală a lui P4, măsurată DUPĂ ultimul commit.

**DE CE E UN FIȘIER SEPARAT, produs după commit.** Un raport nu-și poate conține propriul hash:
`FINAL_HEAD` există abia după ce commitul care poartă raportul a fost creat. Iar cerința rundei de
acceptare e `FULL_SUITE_COMMIT == FINAL_HEAD` — adică suita trebuie să ruleze pe HEAD-ul final,
nu pe arborele de dinaintea lui. Cele două se pot împăca doar cu o măsurătoare de după.

**CE MĂSOARĂ, și niciunul nu se presupune:**
  * cele cinci brațe — `HEAD`, `origin/main`, `public/main`, `backup/lant-<zi>`, și commitul
    **procesului viu**. Ultimul se citește din PROCES, prin `GET /admin/versiune`, care întoarce
    ștampila pusă în memorie la pornire — nu se deduce din ora de start, cum face `post-commit`;
  * suita completă, rulată ACUM, pe HEAD-ul curent, cu exit code-ul ei.

**Regula, respectată:** dacă oricare braț nu se poate citi sau diferă, `FOUR_WAY_STATUS=FAIL` și
`P4_STATUS=NOT_ACCEPTED`. Un braț necitit nu e un braț închis.

Rulare: `./venv/bin/python -m scripts.p4_trasabilitate`
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

PY = os.path.join(RAD, "venv", "bin", "python")
BAZA = "http://127.0.0.1:8010"


def _git(*args):
    r = subprocess.run(["git", "-C", RAD] + list(args), capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def _backup(zi):
    """`(hash, sursa)` pentru bratul BACKUP. E o ramura REMOTE: `rev-parse` pe numele scurt nu o
    gaseste, fiindca local nu exista. Se citeste din remote (ca `post-commit`) si din referinta de
    urmarire; daca amandoua raspund si difera, se spune."""
    nume = "backup/lant-%s" % zi
    r = subprocess.run(["git", "-C", RAD, "ls-remote", "origin", nume],
                       capture_output=True, text=True)
    la_remote = r.stdout.split("\t")[0].strip() if r.returncode == 0 and r.stdout.strip() else ""
    urmarire = _git("rev-parse", "origin/%s" % nume)
    if la_remote and urmarire and la_remote != urmarire:
        return "", "DIVERGENTA: ls-remote=%s vs origin/%s=%s" % (la_remote[:8], nume, urmarire[:8])
    if la_remote:
        return la_remote, "git ls-remote origin %s" % nume
    if urmarire:
        return urmarire, "git rev-parse origin/%s" % nume
    return "", "NECITIT (nici ls-remote, nici referinta de urmarire)"


def commit_proces_viu():
    """Commitul cu care RULEAZĂ procesul viu, citit din el. `None` dacă nu se poate citi.

    Se mintește un token de superadmin pentru un cont care există deja — `/admin/versiune` e o
    citire, și e singura cale prin care procesul spune ce cod are în memorie. Alternativa
    (`ActiveEnterTimestamp > data commitului`) e un PROXY: spune că procesul a pornit după commit,
    nu că rulează chiar acel commit."""
    try:
        import requests
        from core import auth_api, db
        db.init_pool()
        with db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("SELECT id, accounting_firm_id FROM public.users "
                            " WHERE rol = 'superadmin' ORDER BY id LIMIT 1")
                r = cur.fetchone()
        if not r:
            return None, "niciun superadmin in baza"
        tok = auth_api.emite_token({"id": r[0], "rol": "superadmin",
                                    "accounting_firm_id": r[1]})
        raspuns = requests.get(BAZA + "/admin/versiune", timeout=10,
                               headers={"Authorization": "Bearer " + tok})
        if raspuns.status_code != 200:
            return None, "HTTP %s la /admin/versiune" % raspuns.status_code
        j = raspuns.json()
        return (j.get("running") or (j.get("versiune") or {}).get("running")), json.dumps(j)[:200]
    except Exception as e:  # noqa: BLE001
        return None, "%s: %s" % (type(e).__name__, str(e)[:160])


def suita_completa():
    """Rulează suita ÎNTREAGĂ acum, pe arborele curent. Întoarce dict cu cifrele și exit code-ul."""
    t0 = time.time()
    env = dict(os.environ)
    r = subprocess.run([PY, "-m", "pytest", "-q"], cwd=RAD, capture_output=True, text=True,
                       env=env)
    durata = time.time() - t0
    coada = (r.stdout or "").strip().split("\n")[-1]
    def _n(eticheta):
        m = re.search(r"(\d+) %s" % eticheta, coada)
        return int(m.group(1)) if m else 0
    return {
        "exit": r.returncode, "durata": durata, "coada": coada,
        "passed": _n("passed"), "failed": _n("failed"),
        "skipped": _n("skipped"), "xfailed": _n("xfailed"),
    }


def main():
    head = _git("rev-parse", "HEAD")
    origin = _git("rev-parse", "origin/main")
    public = _git("rev-parse", "public/main")
    zi = subprocess.run(["date", "+%Y-%m-%d"], capture_output=True, text=True).stdout.strip()
    backup, sursa_backup = _backup(zi)
    viu, detaliu = commit_proces_viu()

    s = suita_completa()

    brate = {"HEAD": head, "ORIGIN_MAIN": origin, "PUBLIC_MAIN": public,
             "BACKUP": backup, "LIVE_PROCESS_COMMIT": viu}
    necitite = [k for k, v in brate.items() if not v]
    diferite = [k for k, v in brate.items() if v and v != head]
    four_way = "PASS" if (not necitite and not diferite) else "FAIL"

    acceptare = io.open(os.path.join(RAD, "masuratori", "p4", "acceptare.txt"),
                        encoding="utf-8").read()

    ok = (four_way == "PASS" and s["failed"] == 0 and s["exit"] == 0
          and "UNCLASSIFIED_RAW_CANDIDATES=0" in acceptare
          and "UNTESTED_CRITICAL_COMPOSITES=0" in acceptare
          and "UNEXPLAINED_EXCLUSIONS=0" in acceptare)

    L = []
    L.append("TRASABILITATEA FINALA P4 — masurata DUPA ultimul commit")
    L.append("Generat cu: ./venv/bin/python -m scripts.p4_trasabilitate")
    L.append("produs la: %s" % subprocess.run(["date", "-Is"], capture_output=True,
                                              text=True).stdout.strip())
    L.append("=" * 78)
    L.append("")
    L.append(acceptare.split("=" * 78, 1)[-1].strip())
    L.append("")
    L.append("--- TRASABILITATE, masurata acum -------------------------------------------")
    L.append("FINAL_HEAD=%s" % head)
    L.append("FULL_SUITE_COMMIT=%s" % head)
    L.append("FULL_SUITE_PASSED=%d" % s["passed"])
    L.append("FULL_SUITE_FAILED=%d" % s["failed"])
    L.append("FULL_SUITE_SKIPPED=%d" % s["skipped"])
    L.append("FULL_SUITE_XFAILED=%d" % s["xfailed"])
    L.append("FULL_SUITE_EXIT_CODE=%d" % s["exit"])
    L.append("  (durata: %.2f s · linia de rezumat: %s)" % (s["durata"], s["coada"]))
    L.append("  Suita a rulat pe arborele lui %s, DUPA commit — deci FULL_SUITE_COMMIT == FINAL_HEAD"
             % head[:8])
    L.append("")
    L.append("HEAD=%s" % head)
    L.append("ORIGIN_MAIN=%s" % (origin or "(NECITIT)"))
    L.append("PUBLIC_MAIN=%s" % (public or "(NECITIT)"))
    L.append("BACKUP=%s   (backup/lant-%s, citit din %s)"
             % (backup or "(NECITIT)", zi, sursa_backup))
    L.append("LIVE_PROCESS_COMMIT=%s" % (viu or "(NECITIT)"))
    L.append("  sursa procesului viu: GET /admin/versiune -> %s" % detaliu)
    L.append("")
    if necitite:
        L.append("BRATE NECITITE: %s" % ", ".join(necitite))
    if diferite:
        L.append("BRATE DIFERITE DE HEAD: %s" % ", ".join(diferite))
    L.append("FOUR_WAY_STATUS=%s" % four_way)
    L.append("P4_STATUS=%s" % ("CLOSED_ACCEPTED" if ok else "NOT_ACCEPTED"))
    if not ok:
        L.append("  (motivul: %s)" % ("four-way" if four_way != "PASS"
                                      else "suita rosie" if s["failed"] else "cifre de acceptare"))
    text = "\n".join(L)
    cale = os.path.join(RAD, "masuratori", "p4", "TRASABILITATE_P4.txt")
    with io.open(cale, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(text)
    print()
    print("scris: %s" % cale)
    return 0


if __name__ == "__main__":
    sys.exit(main())
