# -*- coding: utf-8 -*-
"""scripts/matrice_text_taiat.py — matricea de text tăiat (comanda 17.2-B): fiecare intrare din core/catalog_ecrane.json, deschisă la 603x590, 1366x768 și 2133x1111 prin
scripts/verificator_design.py `ecran` cu detectorul scripts/text_taiat_masuri.js (a doua cale de măsurare, `masuri_alt`). Rulează cu ./venv/bin/python.
  calibreaza [--iesire D] [--eticheta T]   calibrarea detectorului în ambele direcții, pe 8019; scrie calibrare.txt în D (implicit docs/dovezi/17_2_B/)
  matrice    [--iesire D] [--eticheta T]   315 deschideri; scrie în D baza_text_taiat.csv, baza_text_taiat.json, rezumat.txt (prima linie = eticheta, implicit «baza»);
                                           refuză cu 1, fără nicio deschidere, dacă calibrare.txt din D nu se încheie cu «abateri: 0 sha=<HEAD>»
  un-ecran <nume> <rez> <director>         intern: un ecran într-un subproces cu timeout
Capturile PNG și JSON-urile per ecran: ~/matrice_text_taiat_capturi (în afara depozitului). Regulile comune cu matricea 16.7 (lacăt, 8019, restaurări): calibreaza_16_7.ruleaza_pe_server."""
import argparse
import csv
import json
import os
import signal
import subprocess
import sys
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
DOVEZI = os.path.join(RAD, "docs", "dovezi", "17_2_B")
CAPTURI = os.path.expanduser("~/matrice_text_taiat_capturi")
JS = os.path.join(RAD, "scripts", "text_taiat_masuri.js")
REZOLUTII = ("603x590", "1366x768", "2133x1111")
TIMEOUT = 240
RANDURI_ASTEPTATE = 105 * len(REZOLUTII)
TAIETURI_PE_ECRAN = 50
TIPURI = ("lat", "inalt", "iesit")
STARE_TIMEOUT = "timeout"
NEDESCHIS_FARA_FEREASTRA = "nicio fereastră de lucru deschisă"
ECRANE_CALIBRARE = ("De validat", "Declarații lucrate", "Declarații F1 pasul 1")
ATRIBUT_PROBA = "data-proba-17-2-b"

# injecțiile calibrării (corp JS cu `F` = ultima fereastră, învelit de calibreaza_16_7.deschide)
_LA_INCEPUT = "F.querySelector('.fereastra-corp').insertAdjacentHTML('afterbegin', %s);"
INJECTIE_RAU = _LA_INCEPUT % json.dumps(
    '<div %(a)s="lat" style="display:block;width:40px;overflow:hidden;white-space:nowrap">Text de probă foarte lung pentru tăiere pe lățime</div>'
    '<div %(a)s="inalt" style="display:block;height:12px;overflow:hidden;line-height:20px">Text de probă<br>pe două rânduri</div>'
    '<div style="position:relative;overflow:hidden;width:100px;height:30px"><button %(a)s="iesit" style="position:absolute;left:150px;white-space:nowrap">Buton de probă</button></div>'
    % {"a": ATRIBUT_PROBA}, ensure_ascii=False)
_BUN = 'style="display:block;position:fixed;left:0;top:0"'
INJECTIE_BUN = _LA_INCEPUT % json.dumps(
    '<div %(a)s="bun" %(s)s>Text de probă foarte lung pentru tăiere pe lățime</div>'
    '<div %(a)s="bun" %(s)s>Text de probă<br>pe două rânduri</div>'
    '<div %(a)s="bun" %(s)s><button %(a)s="bun">Buton de probă</button></div>' % {"a": ATRIBUT_PROBA, "s": _BUN}, ensure_ascii=False)
#: tip -> începutul textului elementului probă cu valoarea de atribut respectivă
TEXT_PROBA = {"lat": "Text de probă foarte", "inalt": "Text de probă pe", "iesit": "Buton de probă"}


def git(*a):
    return subprocess.run(["git", *a], cwd=RAD, capture_output=True, text=True, check=True).stdout


# ── starea unei deschideri ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def stare_deschidere(js):
    """-> (stare, motiv). `js` = dicționarul ecranului | None (JSON lipsă) | STARE_TIMEOUT. «timeout» = subprocesul oprit la TIMEOUT; «nedeschis» = JSON lipsă, eroare_deschidere
    nenul sau nicio fereastră de lucru (motiv mereu scris); «ok» = orice altceva."""
    if js == STARE_TIMEOUT:
        return "timeout", "oprit după %d s" % TIMEOUT
    if js is None:
        return "nedeschis", "JSON lipsă"
    if js.get("eroare_deschidere"):
        return "nedeschis", js["eroare_deschidere"]
    if any(NEDESCHIS_FARA_FEREASTRA in m for r in js.get("pica", {}).values() for m in r):
        return "nedeschis", NEDESCHIS_FARA_FEREASTRA
    if "masuri_alt" not in js:
        return "nedeschis", "detectorul n-a întors rezultat"
    return "ok", ""


def rand_ecran(nume, rez, js):
    """-> dicționarul unui rând al matricei: ecran, rezolutie, stare, motiv, numar, lat/inalt/iesit (None cât timp nu există măsurătoare), taiate."""
    stare, motiv = stare_deschidere(js)
    alt = js.get("masuri_alt") if isinstance(js, dict) else None
    r = {"ecran": nume, "rezolutie": rez, "stare": stare, "motiv": motiv, "numar": None, "lat": None, "inalt": None, "iesit": None, "taiate": []}
    if alt is not None:
        r["taiate"] = alt["taiate"]
        r["numar"] = len(alt["taiate"])
        for t in TIPURI:
            r[t] = sum(1 for x in alt["taiate"] if x["tip"] == t)
    return r


def _n(v):
    return v or 0


# ── scrierea rezultatelor ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def rezumat(randuri, eticheta, durata):
    """Textul rezumat.txt: eticheta pe prima linie, totaluri pe rezoluție, ecranele cu stare ≠ ok (cu motiv), primele 10 ecrane după numărul de tăieturi."""
    linii = [eticheta, "ecrane: %d, deschideri: %d, durata: %d s" % (len({r["ecran"] for r in randuri}), len(randuri), durata)]
    for rez in REZOLUTII:
        pe = [r for r in randuri if r["rezolutie"] == rez]
        stari = {s: sum(1 for r in pe if r["stare"] == s) for s in ("ok", "nedeschis", "timeout")}
        linii.append("%s: deschideri=%d ok=%d nedeschis=%d timeout=%d | tăieturi=%d (lat=%d inalt=%d iesit=%d) | ecrane cu cel puțin o tăietură=%d" % (
            rez, len(pe), stari["ok"], stari["nedeschis"], stari["timeout"], sum(_n(r["numar"]) for r in pe), *(sum(_n(r[t]) for r in pe) for t in TIPURI),
            sum(1 for r in pe if _n(r["numar"]) > 0)))
    cu = {r["ecran"] for r in randuri if _n(r["numar"]) > 0}
    linii.append("ecrane cu cel puțin o tăietură la oricare rezoluție: %d" % len(cu))
    linii.append("")
    linii.append("ecrane cu stare diferită de ok (%d deschideri):" % sum(1 for r in randuri if r["stare"] != "ok"))
    for r in randuri:
        if r["stare"] != "ok":
            linii.append("  %s | %s | %s | %s" % (r["ecran"], r["rezolutie"], r["stare"], r["motiv"]))
    linii.append("")
    linii.append("primele 10 ecrane după numărul de tăieturi (suma pe cele 3 rezoluții):")
    suma = {}
    for r in randuri:
        suma.setdefault(r["ecran"], {})[r["rezolutie"]] = _n(r["numar"])
    for nume, pe in sorted(suma.items(), key=lambda kv: (-sum(kv[1].values()), kv[0]))[:10]:
        linii.append("  %s | %d | %s" % (nume, sum(pe.values()), " ".join("%s=%d" % (rez, pe.get(rez, 0)) for rez in REZOLUTII)))
    return "\n".join(linii) + "\n"


def scrie_rezultate(randuri, iesire, eticheta, durata):
    """Scrie baza_text_taiat.csv (antet: ecran, rezoluție, număr, lat, inalt, iesit, stare, motiv), baza_text_taiat.json (cel mult TAIETURI_PE_ECRAN intrări per ecran și
    rezoluție; numărul complet rămâne în CSV) și rezumat.txt în `iesire`. -> 0, sau 1 dacă numărul de rânduri ≠ RANDURI_ASTEPTATE (fișierele se scriu oricum)."""
    os.makedirs(iesire, exist_ok=True)
    with open(os.path.join(iesire, "baza_text_taiat.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ecran", "rezoluție", "număr", "lat", "inalt", "iesit", "stare", "motiv"])
        for r in randuri:
            w.writerow([r["ecran"], r["rezolutie"], *("" if r[k] is None else r[k] for k in ("numar", "lat", "inalt", "iesit")), r["stare"], r["motiv"]])
    scurt = [{**{k: r[k] for k in ("ecran", "rezolutie", "stare", "motiv", "numar")}, "taiate": r["taiate"][:TAIETURI_PE_ECRAN]} for r in randuri]
    json.dump(scurt, open(os.path.join(iesire, "baza_text_taiat.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(iesire, "rezumat.txt"), "w", encoding="utf-8").write(rezumat(randuri, eticheta, durata))
    if len(randuri) != RANDURI_ASTEPTATE:
        print("[matrice_text_taiat] REFUZ: %d rânduri față de %d" % (len(randuri), RANDURI_ASTEPTATE), file=sys.stderr)
        return 1
    return 0


# ── deschiderea unui ecran ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def un_ecran(nume, rez, director):
    import verificator_design as VD
    return VD.ecran(nume, rez, director, masuri_alt=JS, director_png=CAPTURI)


def deschide(nume, rez, json_dir=None):
    """Deschide o intrare la o rezoluție într-un subproces cu timeout; JSON-ul vechi se șterge întâi. -> js | None | STARE_TIMEOUT."""
    import verificator_design as VD
    json_dir = json_dir or os.path.join(CAPTURI, "json")
    os.makedirs(json_dir, exist_ok=True)
    cale = os.path.join(json_dir, "%s_%s.json" % (VD.slug(nume), rez))
    if os.path.exists(cale):
        os.remove(cale)
    cmd = [sys.executable, os.path.join(RAD, "scripts", "matrice_text_taiat.py"), "un-ecran", nume, rez, json_dir]
    p = subprocess.Popen(cmd, cwd=RAD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        p.wait(timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        p.wait()
        return STARE_TIMEOUT
    if not os.path.exists(cale):
        return None
    try:
        return json.load(open(cale, encoding="utf-8"))
    except ValueError:
        return None


def matrice(iesire, eticheta):
    import verificator_design as VD
    t0 = time.time()
    randuri = []
    intrari = VD.registru()
    for e in intrari:
        for rez in REZOLUTII:
            randuri.append(rand_ecran(e["nume"], rez, deschide(e["nume"], rez)))
            r = randuri[-1]
            print("[matrice_text_taiat] %d/%d %s %s: %s, tăieturi=%s" % (len(randuri), len(intrari) * len(REZOLUTII), r["ecran"], rez, r["stare"], r["numar"]), flush=True)
    return scrie_rezultate(randuri, iesire, eticheta, round(time.time() - t0))


# ── calibrarea ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _cu_proba(js):
    return [t for t in js["masuri_alt"]["taiate"] if t["proba"]]


def _fara_proba(js):
    return sum(1 for t in js["masuri_alt"]["taiate"] if not t["proba"])


def compara_pozitiv(js):
    """Cu injecția rea: exact trei intrări cu proba=true, câte una lat, inalt, iesit, fiecare pe elementul cu valoarea de atribut respectivă (recunoscut după text).
    -> (ok, obținut)."""
    p = _cu_proba(js)
    tipuri = sorted(t["tip"] for t in p)
    potrivite = all(t["text"].startswith(TEXT_PROBA[t["tip"]]) for t in p if t["tip"] in TEXT_PROBA)
    return tipuri == sorted(TIPURI) and potrivite, "proba=true: %s%s" % (", ".join("%s(%s)" % (t["tip"], t["text"]) for t in p) or "nicio intrare", "" if potrivite else " — text nepotrivit")


def compara_negativ(js_bun, fara_proba_baza):
    """Cu injecția bună: zero intrări cu proba=true și același număr de intrări fără probă ca la măsurătoarea fără injecție. -> (ok, obținut)."""
    p, f = _cu_proba(js_bun), _fara_proba(js_bun)
    return not p and f == fara_proba_baza, "proba=true: %d, fără probă: %d (fără injecție: %d)" % (len(p), f, fara_proba_baza)


def calibrare(iesire):
    import calibreaza_16_7 as C
    os.makedirs(iesire, exist_ok=True)
    os.makedirs(os.path.join(CAPTURI, "calibrare"), exist_ok=True)
    C.CAPTURI = os.path.join(CAPTURI, "calibrare")
    import verificator_design as VD
    nume_registru = {e["nume"] for e in VD.registru()}
    lipsa = [n for n in ECRANE_CALIBRARE if n not in nume_registru]
    if lipsa:
        print("[matrice_text_taiat] REFUZ: ecrane de calibrare lipsă din registru: %s" % lipsa, file=sys.stderr)
        return 1
    sha = git("rev-parse", "HEAD").strip()
    linii, abateri = ["calibrare detector text tăiat, 3 ecrane × %d rezoluții, sha=%s" % (len(REZOLUTII), sha)], 0
    for nume in ECRANE_CALIBRARE:
        for rez in REZOLUTII:
            js_rau = C.deschide(nume, rez, INJECTIE_RAU, JS)
            js_fara = C.deschide(nume, rez, None, JS)
            js_bun = C.deschide(nume, rez, INJECTIE_BUN, JS)
            for caz, js in (("pozitiv", js_rau), ("fără injecție", js_fara), ("negativ", js_bun)):
                if js is None or js.get("eroare_deschidere") or "masuri_alt" not in js:
                    abateri += 1
                    linii.append("%s | %s | %s | RATAT | ecranul nu s-a deschis" % (caz, nume, rez))
                    print(linii[-1], flush=True)
                    break
            else:
                for caz, (ok, obtinut) in (("pozitiv", compara_pozitiv(js_rau)), ("negativ", compara_negativ(js_bun, _fara_proba(js_fara)))):
                    abateri += not ok
                    linii.append("%s | %s | %s | %s | %s" % (caz, nume, rez, "ATINS" if ok else "RATAT", obtinut))
                    print(linii[-1], flush=True)
    linii.append("abateri: %d sha=%s" % (abateri, sha))
    open(os.path.join(iesire, "calibrare.txt"), "w", encoding="utf-8").write("\n".join(linii) + "\n")
    return 1 if abateri else 0


def calibrare_la_zi(iesire):
    """-> motivul refuzului sau None: calibrare.txt din `iesire` trebuie să existe și să se încheie cu «abateri: 0 sha=<HEAD curent>»."""
    cale = os.path.join(iesire, "calibrare.txt")
    if not os.path.exists(cale):
        return "lipsește %s" % cale
    ultima = (open(cale, encoding="utf-8").read().strip().splitlines() or [""])[-1]
    asteptata = "abateri: 0 sha=%s" % git("rev-parse", "HEAD").strip()
    return None if ultima == asteptata else "ultima linie din calibrare.txt e %r, nu %r" % (ultima, asteptata)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mod", choices=("calibreaza", "matrice", "un-ecran"))
    ap.add_argument("ecran", nargs="?")
    ap.add_argument("rez", nargs="?")
    ap.add_argument("director", nargs="?")
    ap.add_argument("--iesire", default=DOVEZI)
    ap.add_argument("--eticheta", default="baza")
    a = ap.parse_args(argv)
    if a.mod == "un-ecran":
        return un_ecran(a.ecran, a.rez, a.director)
    import calibreaza_16_7 as C
    if a.mod == "calibreaza":
        return C.ruleaza_pe_server("matrice_text_taiat.py", lambda: calibrare(a.iesire))
    motiv = calibrare_la_zi(a.iesire)
    if motiv:
        print("[matrice_text_taiat] REFUZ: calibrarea nu e la zi: %s" % motiv, file=sys.stderr)
        return 1
    return C.ruleaza_pe_server("matrice_text_taiat.py", lambda: matrice(a.iesire, a.eticheta))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
