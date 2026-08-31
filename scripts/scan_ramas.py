# -*- coding: utf-8 -*-
"""scripts/scan_ramas.py — CE A RAMAS DE FACUT, derivat din fisiere, cu sursa pe fiecare rand.

Cerut de Costin, 31.08.2026: *«Deriva din fisiere lista a ce a ramas de facut, cu sursa pe fiecare
rand si cu dimensiune probata. Unde doua liste numesc acelasi lucru diferit, e constatare.
Masuratoare, nu constructie.»*

DE UNDE CITESTE — sase surse, fiecare cu propriul format, niciuna copiata aici:

  1. `CONFORMITATE.md` · restantele R<n>, dupa campul `stare`         -> RESTANTA
  2. `CONFORMITATE.md` · lista 3, prin `scan_lista3`                  -> ARTEFACT
  3. `CONFORMITATE.md` · interdictiile 1-77, dupa `stare`             -> INTERDICTIE
  4. `INSTRUMENTE_ROADMAP.md` · cele 11 instrumente                   -> INSTRUMENT
  5. clichetele vii (refuzuri, garzi pe text, ancore)                 -> CLICHET
  6. `GARZI.md` · constatarile marcate GRI sau DESCHIS                -> CONSTATARE

CE INSEAMNA «DIMENSIUNE PROBATA»: pentru fiecare rand, o cifra care se poate RECALCULA acum, nu una
citita din proza. Unde nu exista, se scrie `?` — un randul fara dimensiune e o sarcina despre care nu
se stie cat e de mare, si asta e o informatie, nu o lipsa de raportare.

CELE TREI MODURI DE ESEC, scrise inainte de prima rulare:
  1. **Citeste STAREA scrisa, nu adevarul.** Un rand care zice REZOLVATA fara sa fie nu se vede de
     aici. Instrumentul spune ce spun fisierele despre ele insele.
  2. **Nu vede ce nu e intr-o lista.** O sarcina care traieste doar intr-un mesaj sau intr-un
     comentariu de cod nu apare. Deci lista e un plafon INFERIOR.
  3. **Potrivirea intre liste e pe CUVINTE-CHEIE.** Doua liste care numesc acelasi lucru cu vocabular
     complet diferit nu se pot potrivi mecanic — exact clasa pe care o cauta. Deci divergentele
     gasite sunt un plafon INFERIOR, iar cele negasite nu inseamna ca nu exista.
"""
import io
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)   # rulat direct, nu ca modul
CONF = os.path.join(RAD, "CONFORMITATE.md")
ROADMAP = os.path.join(RAD, "INSTRUMENTE_ROADMAP.md")
GARZI = os.path.join(RAD, "GARZI.md")

#: Felurile de rand. Nomenclator INCHIS.
FELURI = ("RESTANTA", "ARTEFACT", "INTERDICTIE", "INSTRUMENT", "CLICHET", "CONSTATARE")


def _citeste(cale):
    return io.open(cale, encoding="utf-8", errors="replace").read() if os.path.exists(cale) else ""


def restante():
    """R<n> cu `stare` DESCHISA, din CONFORMITATE."""
    t = _citeste(CONF)
    out = []
    for m in re.finditer(r"^### (R\d+) — (.+?)$", t, re.M):
        cod, titlu = m.group(1), m.group(2).strip()
        capat = t.find("\n### ", m.end())
        corp = t[m.end():capat if capat > 0 else m.end() + 4000]
        st = re.search(r"- \*\*stare\*\*: \*{0,2}(\w+)", corp)
        stare = (st.group(1) if st else "?").upper()
        if stare.startswith("REZOLVAT"):
            continue
        c = re.search(r"\(contor (\d+)\)", corp) or re.search(r"- \*\*reluări\*\*: (\d+)", corp)
        out.append({"fel": "RESTANTA", "cod": cod, "ce": titlu,
                    "sursa": "CONFORMITATE.md · ### %s" % cod,
                    "dimensiune": c.group(1) if c else "?"})
    return out


def artefacte():
    """Randurile DESCHISE din lista 3, prin instrumentul ei."""
    from scripts import scan_lista3
    return [{"fel": "ARTEFACT", "cod": "L3", "ce": r["artefact"],
             "sursa": "CONFORMITATE.md · lista 3 (scan_lista3)",
             "dimensiune": "1 rand"}
            for r in scan_lista3.randuri() if r["verdict"] == "DESCHIS"]


def interdictii():
    """Interdictiile care NU sunt MASURATE."""
    t = _citeste(CONF)
    out = []
    for m in re.finditer(r"^## (\d+) — (.+?)$", t, re.M):
        nr, titlu = int(m.group(1)), m.group(2).strip()
        capat = t.find("\n## ", m.end())
        corp = t[m.end():capat if capat > 0 else m.end() + 3000]
        st = re.search(r"- \*\*stare\*\*: \*{0,2}([A-ZĂÂÎȘȚ]+)", corp)
        stare = st.group(1) if st else "?"
        if stare == "MĂSURATĂ":
            continue
        cif = re.search(r"- \*\*cifra\*\*: \*{0,2}(\d+)", corp)
        out.append({"fel": "INTERDICTIE", "cod": "#%d" % nr, "ce": titlu,
                    "sursa": "CONFORMITATE.md · ## %d (%s)" % (nr, stare),
                    "dimensiune": cif.group(1) if cif else "?"})
    return out


#: Starile pe care roadmapul le foloseste. Nomenclator INCHIS — o a patra ar trece tacut drept
#: «neconstruit» sau drept «gata», si niciuna n-ar fi masuratoare.
STARI_INSTRUMENT = ("CONSTRUIT", "PROPUS", "PARȚIAL", "ACOPERIT")


def instrumente():
    """Cele din roadmap care nu sunt CONSTRUITE sau ACOPERITE.

    Roadmapul le tine ca LISTA — `- **#N titlu** — PROPUS: ...` —, nu ca tabel. Prima forma a
    functiei cauta un tabel si intorcea ZERO: o ORBIRE care se citea ca «nu mai e nimic de facut».
    Prinsa fiindca cifra contrazicea ce stiam, si am verificat FORMATUL in loc sa cred cifra.
    """
    t = _citeste(ROADMAP)
    out = []
    for m in re.finditer(r"^- \*\*#(\d+) (.+?)\*\*\s*—\s*(\w+)", t, re.M):
        nr, titlu, stare = m.group(1), m.group(2), m.group(3).upper()
        if stare in ("CONSTRUIT", "ACOPERIT"):
            continue
        out.append({"fel": "INSTRUMENT", "cod": "#%s" % nr,
                    "ce": "%s (%s)" % (re.sub(r"[*`]", "", titlu), stare),
                    "sursa": "INSTRUMENTE_ROADMAP.md · lista", "dimensiune": "?"})
    return out


def clichete():
    """Clichetele vii, cu cifra RECALCULATA acum — singurele randuri cu dimensiune sigura."""
    out = []
    try:
        from scripts import scan_refuzuri
        inv = scan_refuzuri.inventar()
        out.append({"fel": "CLICHET", "cod": "77", "ce": "refuzuri fără temei în module care citează legea",
                    "sursa": "scripts/scan_refuzuri.datorie()",
                    "dimensiune": str(sum(scan_refuzuri.datorie(inv).values()))})
        out.append({"fel": "CLICHET", "cod": "77u", "ce": "UMBRA: refuzuri în module care nu citează legea (nedeplafonat)",
                    "sursa": "scripts/scan_refuzuri.umbra()",
                    "dimensiune": str(sum(scan_refuzuri.umbra(inv).values()))})
    except Exception as e:
        out.append({"fel": "CLICHET", "cod": "77", "ce": "refuzuri", "sursa": "scan_refuzuri",
                    "dimensiune": "EROARE: %s" % str(e)[:40]})
    try:
        from core import scan_garzi_pe_text
        out.append({"fel": "CLICHET", "cod": "50", "ce": "aserțiuni ancorate pe text, nu pe structură",
                    "sursa": "core/scan_garzi_pe_text.pe_fel()",
                    "dimensiune": str(scan_garzi_pe_text.pe_fel()["apare_oricum"])})
    except Exception:
        pass
    try:
        from scripts import scan_ancore_rute
        v = scan_ancore_rute.verdicte()
        out.append({"fel": "CLICHET", "cod": "R80", "ce": "rute despre care detectorul de apelanți nu poate afirma nimic",
                    "sursa": "scripts/scan_ancore_rute.verdicte()",
                    "dimensiune": str(sum(1 for x in v.values() if x == "GRI"))})
    except Exception:
        pass
    return out


def constatari():
    """Constatarile din GARZI care se declara GRI sau DESCHIS."""
    t = _citeste(GARZI)
    out = []
    for m in re.finditer(r"^## (\d{2}\.\d{2}\.\d{4}) — (.+?)$", t, re.M):
        titlu = m.group(2).strip()
        gol = re.sub(r"[*`]", "", titlu)
        if "GRI" in gol or "DESCHIS" in gol.upper():
            out.append({"fel": "CONSTATARE", "cod": m.group(1), "ce": gol[:90],
                        "sursa": "GARZI.md · %s" % m.group(1), "dimensiune": "?"})
    return out


def tot():
    return restante() + artefacte() + interdictii() + instrumente() + clichete() + constatari()


#: Perechi de cuvinte care numesc ACELASI lucru in liste diferite. Se scriu ca DATE, ca sa se poata
#: proba — si ca sa se vada cat de putin acopera potrivirea mecanica (modul de esec 3).
SINONIME = (("refuz", "blocaj"), ("temei", "sursa"), ("artefact", "document"),
            ("gard", "clichet"), ("restanta", "restanță"))


def divergente(randuri=None):
    """Randuri din liste DIFERITE care numesc, probabil, acelasi lucru cu alt cuvant."""
    r = tot() if randuri is None else randuri
    out = []
    for i, a in enumerate(r):
        for b in r[i + 1:]:
            if a["fel"] == b["fel"]:
                continue
            ta, tb = a["ce"].lower(), b["ce"].lower()
            for x, y in SINONIME:
                if (x in ta and y in tb) or (y in ta and x in tb):
                    cuv_a = set(re.findall(r"\w{5,}", ta))
                    cuv_b = set(re.findall(r"\w{5,}", tb))
                    if len(cuv_a & cuv_b) >= 2:
                        out.append((a, b, "%s/%s" % (x, y)))
    return out


def _main():
    r = tot()
    print("CE A RAMAS DE FACUT — derivat din fisiere, %d randuri\n" % len(r))
    print("%-12s %-6s %-11s %s" % ("fel", "cod", "dimensiune", "ce · sursa"))
    print("-" * 100)
    for fel in FELURI:
        for x in [y for y in r if y["fel"] == fel]:
            print("%-12s %-6s %-11s %s" % (fel, x["cod"], x["dimensiune"], x["ce"][:56]))
            print("%-31s   sursa: %s" % ("", x["sursa"]))
    print("\nPE FEL: %s" % {f: sum(1 for x in r if x["fel"] == f) for f in FELURI})
    d = divergente(r)
    print("\nDIVERGENTE DE NUME intre liste: %d" % len(d))
    for a, b, per in d:
        print("   [%s] %s :: %s\n        vs [%s] %s :: %s" % (a["fel"], per, a["ce"][:52],
                                                              b["fel"], per, b["ce"][:52]))
    print("\n[anti-vacuu] surse citite: CONFORMITATE=%s ROADMAP=%s GARZI=%s"
          % (os.path.exists(CONF), os.path.exists(ROADMAP), os.path.exists(GARZI)))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
