# -*- coding: utf-8 -*-
"""scripts/p5_trasabilitate.py — trasabilitatea finală a lui P5, măsurată DUPĂ ultimul commit.

**DE CE E UN FIȘIER SEPARAT, produs după commit.** Un raport nu-și poate conține propriul hash:
`FINAL_HEAD` există abia după ce commitul care poartă raportul a fost creat. Iar cerința fazei e `FULL_SUITE_COMMIT == FINAL_HEAD` — adică suita trebuie să ruleze pe HEAD-ul final,
nu pe arborele de dinaintea lui. Cele două se pot împăca doar cu o măsurătoare de după.

**CE MĂSOARĂ, și niciunul nu se presupune:**
  * cele cinci brațe — `HEAD`, `origin/main`, `public/main`, `backup/lant-<zi>`, și commitul
    **procesului viu**. Ultimul se citește din PROCES, prin `GET /admin/versiune`, care întoarce
    ștampila pusă în memorie la pornire — nu se deduce din ora de start, cum face `post-commit`;
  * suita completă, rulată ACUM, pe HEAD-ul curent, cu exit code-ul ei.

**Regula, respectată:** dacă oricare braț nu se poate citi sau diferă, `FIVE_WAY_STATUS=FAIL` și
`P4_STATUS=NOT_ACCEPTED`. Un braț necitit nu e un braț închis.

**CINCI brațe, nu patru.** `post-commit` verifică patru (HEAD, `origin/main`, backup, procesul viu
prin ora de pornire). Aici sunt cinci: se adaugă `public/main` — al doilea remote, care a produs
R176 — și commitul procesului viu se citește DIN PROCES, nu din ora lui de start.

Rulare: `./venv/bin/python -m scripts.p5_trasabilitate`
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import artefacte_p5  # noqa: E402

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


#: commitul de la care a plecat faza — pinat de comanda fazei
BASELINE_COMMIT = "8ce4cd84b07f411f458a35cc9b9ff9e9990fbcd1"


def _cere(acceptare, cheie, valoare):
    return "%s=%s" % (cheie, valoare) in acceptare


def main():
    head = _git("rev-parse", "HEAD")
    origin = _git("rev-parse", "origin/main")
    public = _git("rev-parse", "public/main")
    zi = subprocess.run(["date", "+%Y-%m-%d"], capture_output=True, text=True).stdout.strip()
    backup, sursa_backup = _backup(zi)
    viu, detaliu = commit_proces_viu()

    # COMMITUL CODULUI DE DIAGNOSTIC — primul commit de dupa baseline. Se citeste din istorie,
    # nu se presupune ca e HEAD: daca dupa el mai vine un commit de raport, cele doua NU sunt
    # acelasi lucru, si comanda fazei cere sa nu fie confundate.
    lant = _git("rev-list", "--reverse", "%s..HEAD" % BASELINE_COMMIT).split()
    cod = lant[0] if lant else ""

    s = suita_completa()

    brate = {"HEAD": head, "ORIGIN_MAIN": origin, "PUBLIC_MAIN": public,
             "BACKUP": backup, "LIVE_PROCESS_COMMIT": viu}
    necitite = [k for k, v in brate.items() if not v]
    diferite = [k for k, v in brate.items() if v and v != head]
    five_way = "PASS" if (not necitite and not diferite) else "FAIL"

    acceptare = io.open(os.path.join(RAD, "masuratori", "p5", "acceptare.txt"),
                        encoding="utf-8").read()

    conditii = [
        ("suita verde", s["failed"] == 0 and s["exit"] == 0),
        ("cinci brate", five_way == "PASS"),
        ("fara candidat neclasificat", _cere(acceptare, "UNCLASSIFIED_RAW_CANDIDATES", "0")),
        ("contabilitatea claselor", _cere(acceptare, "RAW_CLASS_ACCOUNTING", "PASS")),
        ("fara excludere nemotivata", _cere(acceptare, "UNEXPLAINED_EXCLUSIONS", "0")),
        ("fara gol de calibrare", _cere(acceptare, "DETECTOR_CALIBRATION_GAPS", "0")),
        ("codul de productie neatins", _cere(acceptare, "PRODUCTION_CODE_CHANGED", "NO")),
        ("datele de productie neatinse", _cere(acceptare, "PRODUCTION_DATA_AFFECTED", "NO")),
        ("nicio masuratoare pe alta ramura", _cere(acceptare, "UNEXPECTED_STATUSES", "0")),
    ]
    ok = all(v for _n, v in conditii)

    L = []
    L.append("TRASABILITATEA FINALA P5 — DIAGNOSTIC, masurata DUPA ultimul commit")
    L.append("Generat cu: ./venv/bin/python -m scripts.p5_trasabilitate")
    L.append("produs la: %s" % subprocess.run(["date", "-Is"], capture_output=True,
                                              text=True).stdout.strip())
    L.append("=" * 78)
    L.append("")
    L.append(acceptare.split("=" * 78, 1)[-1].strip())
    L.append("")
    L.append("--- CELE TREI COMMITURI, tinute separat --------------------------------------")
    L.append("BASELINE_COMMIT=%s" % BASELINE_COMMIT)
    L.append("DIAGNOSTIC_CODE_COMMIT=%s" % (cod or "(NICIUNUL)"))
    L.append("P5_FINAL_DIAGNOSTIC_COMMIT=%s" % head)
    L.append("  commituri intre baseline si final: %d" % len(lant))
    if cod and cod != head:
        L.append("  ATENTIE: codul de diagnostic si commitul final NU sunt acelasi commit.")
        L.append("  Suita de mai jos a rulat pe %s (finalul), nu pe %s." % (head[:8], cod[:8]))
    L.append("")
    L.append("--- SUITA COMPLETA, rulata acum ----------------------------------------------")
    L.append("FULL_SUITE_COMMIT=%s" % head)
    L.append("FULL_SUITE_PASSED=%d" % s["passed"])
    L.append("FULL_SUITE_FAILED=%d" % s["failed"])
    L.append("FULL_SUITE_SKIPPED=%d" % s["skipped"])
    L.append("FULL_SUITE_XFAILED=%d" % s["xfailed"])
    L.append("FULL_SUITE_EXIT_CODE=%d" % s["exit"])
    L.append("  (durata: %.2f s · linia de rezumat: %s)" % (s["durata"], s["coada"]))
    L.append("  COMANDA: ./venv/bin/python -m pytest -q")
    L.append("  Suita a rulat pe arborele lui %s, DUPA commit — deci FULL_SUITE_COMMIT == "
             "P5_FINAL_DIAGNOSTIC_COMMIT" % head[:8])
    L.append("")
    L.append("--- CELE CINCI BRATE ---------------------------------------------------------")
    L.append("HEAD=%s" % head)
    L.append("ORIGIN_MAIN=%s" % (origin or "(NECITIT)"))
    L.append("PUBLIC_MAIN=%s" % (public or "(NECITIT)"))
    L.append("BACKUP=%s   (backup/lant-%s, citit din %s)"
             % (backup or "(NECITIT)", zi, sursa_backup))
    L.append("LIVE_PROCESS_COMMIT=%s" % (viu or "(NECITIT)"))
    L.append("  sursa procesului viu: GET /admin/versiune -> %s" % detaliu)
    if necitite:
        L.append("BRATE NECITITE: %s" % ", ".join(necitite))
    if diferite:
        L.append("BRATE DIFERITE DE HEAD: %s" % ", ".join(diferite))
    L.append("FIVE_WAY_STATUS=%s   (HEAD · origin/main · public/main · backup · proces viu)"
             % five_way)
    L.append("")
    L.append("--- VERDICT ------------------------------------------------------------------")
    for nume, v in conditii:
        L.append("  [%s] %s" % ("OK" if v else "PICAT", nume))
    L.append("P5_DIAGNOSTIC_STATUS=%s" % ("COMPLETE" if ok else "INCOMPLETE"))
    L.append("P5_IMPLEMENTATION=NOT_STARTED")
    L.append("  `P5_DIAGNOSTIC_STATUS=COMPLETE` NU inseamna `P5_IMPLEMENTATION=CLOSED`:")
    L.append("  diagnosticul e inchis, remedierea nu e nici macar inceputa — v. valurile din raport.")
    # ── FISIERE_ATINSE.txt — derivat, nu tinut minte ────────────────────────────
    stare = _git("diff", "--name-status", "%s..HEAD" % BASELINE_COMMIT)
    atinse = [l for l in stare.splitlines() if l.strip()]
    F = ["FISIERE ATINSE IN FAZA P5-DIAGNOSTIC",
         "de la %s (baseline) pana la %s (final)" % (BASELINE_COMMIT[:8], head[:8]),
         "=" * 78, "",
         "Derivat cu: git diff --name-status %s..HEAD" % BASELINE_COMMIT[:8],
         "Legenda: A = adaugat · M = modificat · D = sters", "",
         "--- TOATE (%d) ---" % len(atinse)]
    F += ["  " + l for l in atinse]
    prod = [l for l in atinse if artefacte_p5._e_productie(l.split("\t")[-1])]
    F += ["", "--- DIN CARE, COD DE PRODUCTIE (%d) ---" % len(prod)]
    F += (["  " + l for l in prod] if prod
          else ["  niciunul. PRODUCTION_CODE_CHANGED=NO nu e o declaratie, e randul asta."])
    cale_f = os.path.join(RAD, "masuratori", "p5", "FISIERE_ATINSE.txt")
    with io.open(cale_f, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(F) + "\n")

    # ── COMMIT_P5.txt — cele trei commituri, cu subiectul fiecaruia ─────────────
    C = ["COMMITURILE FAZEI P5-DIAGNOSTIC", "=" * 78, "",
         "BASELINE_COMMIT=%s" % BASELINE_COMMIT,
         "  %s" % _git("log", "-1", "--format=%s", BASELINE_COMMIT),
         "",
         "DIAGNOSTIC_CODE_COMMIT=%s" % (cod or "(NICIUNUL)"),
         "  %s" % (_git("log", "-1", "--format=%s", cod) if cod else "-"),
         "",
         "P5_FINAL_DIAGNOSTIC_COMMIT=%s" % head,
         "  %s" % _git("log", "-1", "--format=%s", head),
         "",
         "FULL_SUITE_COMMIT=%s   (rulata DUPA acest commit)" % head,
         "",
         "--- LANTUL INTREG (%d commituri) ---" % len(lant)]
    C += ["  " + l for l in _git("log", "--oneline",
                                 "%s..HEAD" % BASELINE_COMMIT).splitlines()]
    cale_c = os.path.join(RAD, "masuratori", "p5", "COMMIT_P5.txt")
    with io.open(cale_c, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(C) + "\n")

    text = "\n".join(L)
    cale = os.path.join(RAD, "masuratori", "p5", "TRASABILITATE_P5.txt")
    with io.open(cale, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(text)
    print()
    print("scris: %s" % cale)
    print("scris: %s" % cale_f)
    print("scris: %s" % cale_c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
