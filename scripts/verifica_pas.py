# -*- coding: utf-8 -*-
"""scripts/verifica_pas.py — verificatorul pe pas al jurnalului de verificare (comanda 16.1, pct.3). Face un pas pe serverul de lucru (8019), ia JSON-ul ecranului
(cererea GET a ecranului) și captura paginii, compară JSON-ul cu așteptarea pasului și scrie rândul în docs/dovezi/<lot>/jurnal_verificare.csv. VERDICTUL îl scrie această
comparație (trece / pică), nu executorul; `neexecutat` = pasul n-a putut rula (server căzut, captură imposibilă). Un rând fără captură existentă, cu mtime în intervalul
declarat (inceput–sfarsit), se refuză (control încrucișat în scripts/jurnal_verificator.sh).
  verifica_pas.py --lot 16.1-C3 --pas P1 --actiune "<text>" --json-url /public/config --pasi docs/dovezi/16_1_C3/pasi.json --asertiune P1 [--pagina /] [--baza http://127.0.0.1:8019] [--csv cale]
Oracolul (16.1-C3, pct.1): așteptarea vine din pasi.json, nu din linia de comandă. Fiecare asertiune are „operator” și „valoare” (copiate literal din pasi_<lot>.txt al arhitectului: acolo sunt
singurele coloane comparate, „descriere” nu) și „cheie” (a lui Code): cheia JSON a ecranului (cu puncte pentru cuib) sau o sursă `text:<url>` (corpul răspunsului) / `dom:<selector css>`
(elementele paginii: nr_randuri = câte sunt, activ = primul e activ, interval_px = înălțimile lor, text = textul lor). Compararea e `compara_asertiune(operator, valoare, observat)`, fără altă interpretare.
Operatori: egal / contine / nr_randuri / lipseste / interval_px / activ / text_contine (definiți în antetul pasi_<lot>.txt)."""
import argparse
import csv
import datetime
import decimal
import json
import os
import re
import subprocess
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jurnal_lot as JL  # noqa: E402

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMPURI = ["lot", "commit", "verificator", "inceput", "sfarsit", "pas", "actiune", "verdict", "captura", "motiv"]


OPERATORI = ("egal", "contine", "nr_randuri", "lipseste", "interval_px", "activ", "text_contine")


def _text(x):
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, (list, tuple)):
        return ",".join(_text(i) for i in x)
    return "" if x is None else str(x)


def compara_asertiune(operator, valoare, observat):
    """Singura comparație a oracolului: operator + valoare (literale din fișierul arhitectului) față de ce s-a citit prin cheie. -> (verdict, motiv)."""
    val = str(valoare)
    if operator == "egal":
        o = _text(observat)
        try:   # numere: cu punct și 2 zecimale, comparate ca valori exacte (1210.00 = 1210.0), nu ca text
            if re.fullmatch(r"-?\d+\.\d{2}", val) and re.fullmatch(r"-?\d+(\.\d+)?", o):
                return ("trece", "") if decimal.Decimal(o) == decimal.Decimal(val) else ("pica", "găsit %s, așteptat %s" % (o, val))
        except decimal.InvalidOperation:
            pass
        return ("trece", "") if o == val else ("pica", "găsit %r, așteptat %r" % (o, val))
    if operator == "contine" or operator == "text_contine":
        return ("trece", "") if val in _text(observat) else ("pica", "%r nu apare în %r" % (val, _text(observat)[:200]))
    if operator == "lipseste":
        return ("trece", "") if val not in _text(observat) else ("pica", "%r apare în %r" % (val, _text(observat)[:200]))
    if operator == "nr_randuri":
        n = len(observat) if isinstance(observat, (list, tuple, dict)) else (0 if observat in (None, "") else None)
        if n is None:
            return "pica", "nu e o listă: %r" % (observat,)
        return ("trece", "") if n == int(val) else ("pica", "găsit %d, așteptat %s" % (n, val))
    if operator == "interval_px":
        lo, hi = [float(x) for x in val.split("-")]
        valori = observat if isinstance(observat, (list, tuple)) else [observat]
        try:
            rele = [v for v in valori if not lo <= float(v) <= hi]
        except (TypeError, ValueError):
            return "pica", "nu e număr: %r" % (observat,)
        return ("trece", "") if valori and not rele else ("pica", "în afara %s: %r" % (val, rele or "nicio valoare"))
    if operator == "activ":
        if not isinstance(observat, bool):
            return "pica", "nu e true/false: %r" % (observat,)
        return ("trece", "") if _text(observat) == val else ("pica", "găsit %s, așteptat %s" % (_text(observat), val))
    return "pica", "operator necunoscut: %r" % operator


def citeste_cheia(raspuns, cheie):
    """Valoarea de la cheia JSON (cu puncte pentru cuib); -> (găsit, valoare)."""
    cur = raspuns
    for p in cheie.split("."):
        if not isinstance(cur, dict) or p not in cur:
            return False, None
        cur = cur[p]
    return True, cur


def observa(cheie, raspuns, baza, pagina):
    """Ce citește oracolul prin cheie: cheia JSON a ecranului, `text:<url>` (corpul răspunsului) sau `dom:<selector>` (elementele paginii). -> (găsit, observat)."""
    if cheie.startswith("text:"):
        return True, urllib.request.urlopen(baza + cheie[5:], timeout=20).read().decode("utf-8", "replace")
    if cheie.startswith("dom:"):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            pag = b.new_page(viewport={"width": 1366, "height": 768})
            pag.goto(baza + pagina, wait_until="load", timeout=30000)
            el = pag.query_selector_all(cheie[4:])
            rez = {"n": len(el), "activ": el[0].is_enabled() if el else None, "px": [e.bounding_box()["height"] for e in el if e.bounding_box()],
                   "text": " ".join(e.inner_text() for e in el)}
            b.close()
        return True, rez
    return citeste_cheia(raspuns, cheie)


def compara(asertiune, observat):
    """Aserțiunea din pasi.json ({operator, valoare, cheie}) față de ce s-a citit. -> (verdict, motiv)."""
    if isinstance(observat, dict) and set(observat) == {"n", "activ", "px", "text"}:   # sursa dom: operatorul alege ce se compară
        op = asertiune["operator"]
        observat = {"nr_randuri": [None] * observat["n"], "activ": observat["activ"], "interval_px": observat["px"]}.get(op, observat["text"])
    return compara_asertiune(asertiune["operator"], asertiune["valoare"], observat)


def incarca_asertiune(cale, id_):
    for a in json.load(open(cale, encoding="utf-8"))["asertiuni"]:
        if a["id"] == id_:
            return a
    raise SystemExit("asertiunea %s nu e în %s" % (id_, cale))


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
    ap.add_argument("--pasi", required=True, help="docs/dovezi/<lot>/pasi.json")
    ap.add_argument("--asertiune", required=True, help="id-ul asertiunii din pasi.json")
    ap.add_argument("--pagina", default="/")
    ap.add_argument("--baza", default="http://127.0.0.1:8019")
    ap.add_argument("--csv", default=None)
    ap.add_argument("--verificator", default="scripts/verifica_pas.py v1")
    o = ap.parse_args(a)
    lotf = JL.L.lot_fisier(o.lot)
    csv_ = o.csv or os.path.join(RAD, "docs", "dovezi", lotf, "jurnal_verificare.csv")
    cap = os.path.join(os.path.dirname(csv_), "capturi", "%s_%s.png" % (lotf, o.pas))
    os.makedirs(os.path.dirname(cap), exist_ok=True)
    t0 = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    verdict, motiv = "neexecutat", ""
    try:
        a = incarca_asertiune(o.pasi, o.asertiune)
        raspuns = json.load(urllib.request.urlopen(o.baza + o.json_url, timeout=20))
        gasit, obs = observa(a["cheie"], raspuns, o.baza, o.pagina)
        verdict, motiv = compara(a, obs) if gasit else ("pica", "cheia %s lipsește din ecran" % a["cheie"])
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
