# -*- coding: utf-8 -*-
"""scripts/poarta_selectie.py — ce rulează poarta implicită (comanda 15.G, 30.10.2026), derivat mecanic; nu primește fișiere în argv.

Tipărește JSON: {"pytest": [fișiere core/test_*.py], "e2e": [fișiere e2e_*.py], "motive": {fișier: de ce}, "incerte": [...]}.
  1. testele fișierelor atinse de la ultima publicare (`main`): `poarta_scurta.selectie`, nivelul `direct`; nesiguranța derivării NU
     extinde la suita întreagă (se listează în `incerte`) — suita întreagă e doar poarta de noapte;
  2. scenariile deficiențelor: core/test_lot*scenariu* și, pentru plasa e2e, NUMAI fișierele din ~/ghid_incoming/scenarii_<comanda>.txt
     (<comanda> = variabila POARTA_COMANDA; fără ea sau fără fișier, nimic) + e2e-urile fluxurilor atinse de la `main` (scripts/poarta_harta.txt);
  3. nucleul fiscal și de calcul: declarații (d###), TVA, solduri, stocuri, salarii, balanță.
Ce e pe lista de sărit (`poarta_sare`) nu apare. „Testele picate la ultima rulare" sunt `pytest --lf` / fișierul de cazute al plasei (poarta_lot.sh)."""
import glob
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import perimetru as P  # noqa: E402
import poarta_scurta as S  # noqa: E402
import poarta_sare  # noqa: E402

RAD = P.RAD
NUCLEU = re.compile(r"^test_(d\d{3}|.*(tva|sold|stoc|salar|declarat|balanta))")
BAZA_PUBLICAT = "main"


#: peste atâtea fișiere e2e aduse de hartă, (b) se înlocuiește cu cele numite sub FLUXURI în scenarii_<comanda>.txt (comanda 15.1, 31.10.2026)
LIMITA_FLUXURI = 20


def _rel(cale):
    return os.path.relpath(cale, RAD)


def _harta():
    """[(cale sau prefix, [fișiere e2e])] din scripts/poarta_harta.txt."""
    out = []
    for ln in open(os.path.join(RAD, "scripts", "poarta_harta.txt"), encoding="utf-8"):
        if "=>" in ln and not ln.startswith("#"):
            k, v = ln.split("=>", 1)
            out.append((k.strip(), v.split()))
    return out


def _ultima_rulare():
    """Commitul ultimei rulări ROȘII a porții pe zona curentă (scripts/poarta_ultima.txt), dacă există și e strămoș al lui HEAD; altfel None."""
    cale = os.path.join(RAD, "scripts", "poarta_ultima.txt")
    try:
        sha = open(cale, encoding="utf-8").read().strip()
    except OSError:
        return None
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        return None
    ok = subprocess.run(["git", "merge-base", "--is-ancestor", sha, "HEAD"], cwd=RAD, capture_output=True).returncode == 0
    return sha if ok else None


def selecteaza():
    motive = {}

    def pune(f, de_ce):
        motive.setdefault(f, []).append(de_ce)

    flux_harta = {}   # (b) e2e-urile fluxurilor atinse, după hartă: fișier -> fișierele atinse care l-au adus
    flux_numite = []  # e2e-urile din scenarii_<comanda>.txt sub titlul FLUXURI

    baza = subprocess.run(["git", "merge-base", "HEAD", BAZA_PUBLICAT], cwd=RAD, capture_output=True, text=True).stdout.strip()
    # [15.1, 31.10.2026] prima rulare a unei zone: „atinse” = față de `main`; reluare după roșu: numai ce s-a schimbat de la ultima rulare a porții
    # (commitul ei, reținut de poarta_lot.sh în scripts/poarta_ultima.txt cât timp zona e roșie) — plus cele picate (--lf / fișierul de căzute),
    # scenariile și verificatorul, care rămân mereu
    ultima = _ultima_rulare()
    if ultima:
        baza = ultima
    incerte = []
    if baza:
        P.BAZA = baza
        atinse = P.atinse_din_git()
        teste, incerte, _e2e, _front, _nev = S.selectie(atinse, "direct")
        for t in teste:
            pune(t, "atins de la ultima publicare")
        # [15.1-E2] JS / CSS atins: testele de browser ale ecranelor (pytest care încarcă `/static/`) — derivarea din importuri nu le vede, iar cadrul
        # ferestrei din 15.1-E2 a rupt 21 dintre ele fără ca poarta să le fi rulat (CLAUDE.md §5: „JS/CSS atins: e2e-ul ecranelor atinse”)
        if any(a.startswith("static/") for a in atinse):
            for f in sorted(glob.glob(os.path.join(RAD, "core", "test_*.py"))):
                try:
                    if re.search(r"playwright|chromium", open(f, encoding="utf-8").read()):
                        pune(_rel(f), "browser: JS/CSS atins")
                except OSError:
                    pass
        harta = _harta()
        for a in atinse:
            for cheie, fisiere in harta:
                if a == cheie or (cheie.endswith("/") and a.startswith(cheie)):
                    for e in fisiere:
                        flux_harta.setdefault("frontend_test/e2e/" + e, []).append(a)
    for f in sorted(glob.glob(os.path.join(RAD, "core", "test_lot*scenariu*.py"))):
        pune(_rel(f), "scenariu")
    comanda = os.environ.get("POARTA_COMANDA", "").strip()
    cale = os.path.join(os.environ.get("GHID_INCOMING", os.path.expanduser("~/ghid_incoming")), "scenarii_%s.txt" % comanda)
    if comanda and os.path.isfile(cale):
        in_fluxuri = False
        for ln in open(cale, encoding="utf-8"):
            ln = ln.strip()
            if ln.lstrip("# ").upper() == "FLUXURI":   # titlul care desparte scenariile de e2e-urile ecranelor numite (regula 15.1, CLAUDE.md §5)
                in_fluxuri = True
            elif ln and not ln.startswith("#"):
                if in_fluxuri:
                    flux_numite.append("frontend_test/e2e/" + os.path.basename(ln))
                else:
                    pune("frontend_test/e2e/" + os.path.basename(ln), "scenariu al comenzii " + comanda)
    # (b): peste LIMITA_FLUXURI fișiere, harta se înlocuiește cu fluxurile numite; lista completă a hărții se păstrează pentru raport (D)
    inlocuit = len(flux_harta) > LIMITA_FLUXURI
    if inlocuit:
        for f in flux_numite[:LIMITA_FLUXURI]:
            pune(f, "flux numit în scenarii (harta a adus peste %d)" % LIMITA_FLUXURI)
    else:
        for f, de_la in flux_harta.items():
            pune(f, "flux atins: " + de_la[0])
    for f in sorted(glob.glob(os.path.join(RAD, "core", "test_*.py"))):
        if NUCLEU.match(os.path.basename(f)):
            pune(_rel(f), "nucleu fiscal / calcul")
    ramase = {f: m for f, m in motive.items() if os.path.isfile(os.path.join(RAD, f)) and not poarta_sare.sare_fisier(os.path.join(RAD, f))}
    return {"pytest": sorted(f for f in ramase if f.startswith("core/") and os.path.basename(f).startswith("test_")),
            "e2e": sorted(os.path.basename(f) for f in ramase if f.startswith("frontend_test/e2e/")),
            "motive": ramase, "incerte": list(incerte), "baza": baza,
            "flux_harta": sorted(os.path.basename(f) for f in flux_harta), "flux_inlocuit": inlocuit}


#: fișierele a căror atingere înseamnă „toate ecranele” (R11): plafonul întreg de teste de browser și fluxuri
TOATE_ECRANELE = ("static/stil.css", "static/js/navigator.js", "static/js/api.js", "static/js/cadru.js")
#: plafonul testelor de browser din core/ și al fluxurilor e2e luate împreună (R11)
PLAFON_LISTA = 20


def lista(fisiere):
    """[R11, 15.1-E4] Ce va rula poarta pentru fișierele pe care lotul le va atinge, înainte de primul commit: testele de browser din core/ ȘI fluxurile
    e2e (harta + FLUXURI din scenarii_<comanda>.txt), cel mult PLAFON_LISTA fișiere. O atingere a lui stil.css / navigator.js / api.js / cadru.js
    înseamnă „toate ecranele”: plafonul întreg. Un fișier static/ fără nicio intrare în hartă e zonă neacoperită: `neacoperite` nu e gol,
    iar harta se extinde întâi (scripts/poarta_harta.txt), abia apoi începe lotul."""
    fisiere = [f.replace(os.sep, "/") for f in fisiere]
    harta = _harta()
    toate = any(f in TOATE_ECRANELE for f in fisiere)
    din_harta, neacoperite = [], []
    for f in fisiere:
        gasit = [e for cheie, es in harta if f == cheie or (cheie.endswith("/") and f.startswith(cheie)) for e in es]
        for e in gasit:
            if e not in din_harta:
                din_harta.append(e)
        if f.startswith("static/") and not gasit:
            neacoperite.append(f)
    comanda = os.environ.get("POARTA_COMANDA", "").strip()
    cale = os.path.join(os.environ.get("GHID_INCOMING", os.path.expanduser("~/ghid_incoming")), "scenarii_%s.txt" % comanda)
    numite, in_fluxuri = [], False
    if comanda and os.path.isfile(cale):
        for ln in open(cale, encoding="utf-8"):
            ln = ln.strip()
            if ln.lstrip("# ").upper() == "FLUXURI":
                in_fluxuri = True
            elif ln and not ln.startswith("#") and in_fluxuri:
                numite.append(os.path.basename(ln))
    browser = []
    if any(f.startswith("static/") for f in fisiere):
        for f in sorted(glob.glob(os.path.join(RAD, "core", "test_*.py"))):
            try:
                if re.search(r"playwright|chromium", open(f, encoding="utf-8").read()):
                    browser.append(_rel(f))
            except OSError:
                pass
    # ordinea: fluxurile numite, apoi 6 teste de browser (ele păzesc cadrul, nu un singur flux), apoi harta, apoi restul testelor de browser
    candidate = ["frontend_test/e2e/" + e for e in numite] + browser[:6] + ["frontend_test/e2e/" + e for e in din_harta] + browser[6:]
    unice = []
    for c in candidate:
        if c not in unice and os.path.isfile(os.path.join(RAD, c)) and not poarta_sare.sare_fisier(os.path.join(RAD, c)):
            unice.append(c)
    return {"fisiere": fisiere, "toate_ecranele": toate, "plafon": PLAFON_LISTA, "candidate": len(unice), "lista": unice[:PLAFON_LISTA],
            "taiate": unice[PLAFON_LISTA:], "neacoperite": neacoperite}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--lista":
        rez = lista(sys.argv[2:] or list(P.atinse_din_git()))
        print(json.dumps(rez, ensure_ascii=False, indent=1))
        sys.exit(1 if rez["neacoperite"] else 0)
    print(json.dumps(selecteaza(), ensure_ascii=False, indent=1))
