# -*- coding: utf-8 -*-
"""scripts/verifica_pas.py — verificatorul pe pas al jurnalului de verificare (comanda 16.1, pct.3). Face un pas pe serverul de lucru (8019), ia JSON-ul ecranului
(cererea GET a ecranului) și captura paginii, compară JSON-ul cu așteptarea pasului și scrie rândul în docs/dovezi/<lot>/jurnal_verificare.csv. VERDICTUL îl scrie această
comparație (trece / pică), nu executorul; `neexecutat` = pasul n-a putut rula (server căzut, captură imposibilă). Un rând fără captură existentă, cu mtime în intervalul
declarat (inceput–sfarsit), se refuză (control încrucișat în scripts/jurnal_verificator.sh).
  verifica_pas.py --lot 16.1 --pas P1 --actiune "<text>" --json-url /public/config --asteptare '{"cheie": valoare}' [--pagina /] [--baza http://127.0.0.1:8019] [--csv cale]
Așteptarea: obiect JSON; fiecare cheie (cu puncte pentru cuib) trebuie să existe în răspuns cu exact valoarea dată."""
import argparse
import csv
import datetime
import json
import os
import subprocess
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jurnal_lot as JL  # noqa: E402

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMPURI = ["lot", "commit", "verificator", "inceput", "sfarsit", "pas", "actiune", "verdict", "captura", "motiv"]


def compara(raspuns, asteptare):
    """-> (verdict, motiv)."""
    for cheie, val in asteptare.items():
        cur = raspuns
        for p in cheie.split("."):
            if not isinstance(cur, dict) or p not in cur:
                return "pica", "cheia %s lipsește din JSON-ul ecranului" % cheie
            cur = cur[p]
        if cur != val:
            return "pica", "%s: găsit %r, așteptat %r" % (cheie, cur, val)
    return "trece", ""


def captura(url, cale):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pag = b.new_page(viewport={"width": 1366, "height": 768})
        pag.goto(url, wait_until="load", timeout=30000)
        pag.screenshot(path=cale)
        b.close()


def main(a):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lot", required=True)
    ap.add_argument("--pas", required=True)
    ap.add_argument("--actiune", required=True)
    ap.add_argument("--json-url", required=True)
    ap.add_argument("--asteptare", required=True)
    ap.add_argument("--pagina", default="/")
    ap.add_argument("--baza", default="http://127.0.0.1:8019")
    ap.add_argument("--csv", default=None)
    ap.add_argument("--verificator", default="scripts/verifica_pas.py v1")
    o = ap.parse_args(a)
    lotf = o.lot.replace(".", "_")
    csv_ = o.csv or os.path.join(RAD, "docs", "dovezi", lotf, "jurnal_verificare.csv")
    cap = os.path.join(os.path.dirname(csv_), "capturi", "%s_%s.png" % (lotf, o.pas))
    os.makedirs(os.path.dirname(cap), exist_ok=True)
    t0 = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    verdict, motiv = "neexecutat", ""
    try:
        raspuns = json.load(urllib.request.urlopen(o.baza + o.json_url, timeout=20))
        verdict, motiv = compara(raspuns, json.loads(o.asteptare))
        captura(o.baza + o.pagina, cap)
    except Exception as e:   # serverul căzut sau captura imposibilă: pasul nu s-a executat, nu „a trecut”  # invariant-intern-ok: verificator pe pas
        verdict, motiv = "neexecutat", "%s: %s" % (type(e).__name__, e)
    t1 = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    nou = not os.path.exists(csv_)
    with open(csv_, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        if nou:
            w.writerow(CAMPURI)
        w.writerow([o.lot, subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAD, capture_output=True, text=True).stdout.strip(), o.verificator, t0, t1, o.pas, o.actiune,
                    verdict, os.path.relpath(cap, RAD) if os.path.exists(cap) else cap, motiv])
    print("[verifica_pas] %s %s: %s %s" % (o.lot, o.pas, verdict, motiv))
    return 0 if verdict == "trece" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
