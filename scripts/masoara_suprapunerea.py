# -*- coding: utf-8 -*-
"""MĂSURĂTOARE (01.09.2026): cât se suprapun listele pe care le urmez.

NU ARE GARDĂ ȘI NU ARE CLICHET, deliberat: e o cifră de decizie, luată o dată, nu o populație de
păzit. Stă în repo doar ca cifra să se poată **recalcula** — o cifră care nu se poate recalcula e o
amintire, nu o măsurătoare.

LIMITĂ DECLARATĂ: șapte din cele nouă fișiere de checklist (`LOT_1..7_VERIFICARI.md`, **250** din
cele 500 de secțiuni) sunt **netracked**. Cifra lui `E` se poate reproduce pe stația asta, nu dintr-un
clone curat.

Nu restructurează nimic. Potrivire pe OBIECT — ce fișier, ce declarație, ce articol, ce rută, ce
ecran —, nu pe titlu. Obiectele se extrag din CORPUL fiecărei intrări, nu din rândul-rezumat.
"""
import io
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # radacina repo, nu scripts/
os.chdir(RAD)
sys.path.insert(0, RAD)


def citeste(c):
    return io.open(c, encoding="utf-8", errors="replace").read()


# ── extragerea obiectelor ──────────────────────────────────────────────────────────────────────
TIPARE = [
    ("fisier", re.compile(r"\b(?:core|scripts|anaf_surse|frontend_test|static)/[\w./-]+\.\w{1,5}\b")),
    ("fisier", re.compile(r"\bmain\.py\b")),
    ("declaratie", re.compile(r"\b[Dd](\d{3})(?:_[a-z0-9_]+)?\b")),
    ("articol", re.compile(r"\bart(?:icolul)?\.?\s*([0-9]{1,3}(?:\^\d)?|[IVXLC]{1,6})\b")),
    ("ruta", re.compile(r"/tenants/\{[\w_]+\}/[\w/{}-]+")),
    ("ecran", re.compile(r"#fa-[\w-]+")),
]


def obiecte(text):
    out = set()
    for tip, tipar in TIPARE:
        for m in tipar.finditer(text or ""):
            v = m.group(0) if tip in ("fisier", "ruta", "ecran") else m.group(1)
            if tip == "declaratie":
                v = "D" + v
            if tip == "articol":
                v = "art." + v
            out.add((tip, v))
    return out


# ── sursele ────────────────────────────────────────────────────────────────────────────────────
def blocuri(cale, tipar_titlu):
    """[(cod, corp)] — fiecare secțiune care începe cu tiparul dat, până la următoarea."""
    d = citeste(cale)
    poz = [(m.start(), m.group(1)) for m in tipar_titlu.finditer(d)]
    out = []
    for i, (a, cod) in enumerate(poz):
        b = poz[i + 1][0] if i + 1 < len(poz) else len(d)
        out.append((cod, d[a:b]))
    return out


RESTANTE = blocuri("CONFORMITATE.md", re.compile(r"(?m)^### (R\d+) — "))
INTERDICTII = blocuri("CONFORMITATE.md", re.compile(r"(?m)^## (\d+) — "))


def stare(corp):
    m = re.search(r"\*\*stare\*\*:\s*([A-ZĂÎÂȘȚ]+)", corp)
    return m.group(1) if m else "?"


from scripts import scan_ramas as SR  # noqa: E402

randuri = SR.tot()
corp_restanta = dict(RESTANTE)
corp_interdictie = dict(INTERDICTII)

LISTE = {}

# A. cele 114 rânduri, cu corpul rezolvat acolo unde există
a = {}
for r in randuri:
    cod = r.get("cod") or ""
    txt = (r.get("ce") or "") + " " + (r.get("sursa") or "")
    if cod.startswith("R") and cod in corp_restanta:
        txt += " " + corp_restanta[cod]
    elif cod.startswith("#") and cod[1:] in corp_interdictie:
        txt += " " + corp_interdictie[cod[1:]]
    a["%s %s" % (r.get("fel"), cod)] = txt
LISTE["A. scan_ramas (114)"] = a

# B. restanțe DESCHISE
LISTE["B. restanțe DESCHISE"] = {c: t for c, t in RESTANTE if stare(t) == "DESCHISĂ"}

# C. interdicții NEÎNCEPUTE
LISTE["C. interdicții NEÎNCEPUTE"] = {"#" + c: t for c, t in INTERDICTII if stare(t) == "NEÎNCEPUTĂ"}

# D. PLAN_INVESTIGATII, pe secțiuni
LISTE["D. PLAN_INVESTIGATII"] = dict(
    blocuri("PLAN_INVESTIGATII.md", re.compile(r"(?m)^#{1,3} (.+)$")))

# E. checklistul de browser
e = {}
# Cheia poarta un INDICE, nu doar titlul trunchiat. Prima forma folosea `cod[:40]`, iar titlurile
# care incepeau la fel se suprascriau: 446 sectiuni numarate din 500 reale, 54 pierdute TACUT.
for f in ["TRASEE_VERIFICARI.md", "T36_VERIFICARI.md"] + sorted(
        x for x in os.listdir(".") if re.match(r"LOT_\d+_VERIFICARI\.md$", x)):
    if os.path.exists(f):
        for i, (cod, corp) in enumerate(blocuri(f, re.compile(r"(?m)^#{2,3} (.+)$"))):
            e["%s#%d %s" % (f, i, cod[:40])] = corp
LISTE["E. checklist de browser"] = e

# ── 1. CONȚINEREA: B și C sunt subseturi ale lui A? ────────────────────────────────────────────
print("=" * 94)
print("1. CONȚINEREA LISTELOR — sunt liste diferite, sau aceeași listă numărată de mai multe ori?")
print("=" * 94)
coduri_A = {k.split()[-1] for k in LISTE["A. scan_ramas (114)"]}
for nume in ("B. restanțe DESCHISE", "C. interdicții NEÎNCEPUTE"):
    coduri = set(LISTE[nume])
    inA = coduri & coduri_A
    print("  %-28s %3d intrări · %3d și în A (%d%%) · %d doar în ea"
          % (nume, len(coduri), len(inA), round(100 * len(inA) / max(len(coduri), 1)),
             len(coduri - inA)))
print("  %-28s %3d intrări" % ("A. scan_ramas", len(LISTE["A. scan_ramas (114)"])))
print("  %-28s %3d secțiuni" % ("D. PLAN_INVESTIGATII", len(LISTE["D. PLAN_INVESTIGATII"])))
print("  %-28s %3d secțiuni" % ("E. checklist de browser", len(LISTE["E. checklist de browser"])))

# ── 2. SUPRAPUNEREA PE OBIECT ──────────────────────────────────────────────────────────────────
ob_lista = defaultdict(set)      # obiect -> {liste}
ob_intrari = defaultdict(set)    # obiect -> {lista::intrare}
for nume, intrari in LISTE.items():
    for cod, corp in intrari.items():
        for o in obiecte(corp):
            ob_lista[o].add(nume)
            ob_intrari[o].add("%s::%s" % (nume[:1], cod))

print()
print("=" * 94)
print("2. SUPRAPUNEREA PE OBIECT — în câte liste apare același fișier / declarație / articol")
print("=" * 94)
c = Counter(len(v) for v in ob_lista.values())
print("  obiecte distincte: %d" % len(ob_lista))
for k in sorted(c, reverse=True):
    print("     în %d liste: %4d obiecte" % (k, c[k]))

print()
print("  OBIECTELE ATINSE DE CELE MAI MULTE LISTE (top 22):")
print("  %-46s %5s %6s  %s" % ("OBIECT", "liste", "intrări", "care liste"))
for o, liste in sorted(ob_lista.items(), key=lambda kv: (-len(kv[1]), -len(ob_intrari[kv[0]])))[:22]:
    print("  %-46s %5d %6d  %s"
          % ("%s %s" % (o[0][:4], o[1][:40]), len(liste), len(ob_intrari[o]),
             " ".join(sorted(x[0] for x in liste))))

# ── 3. ISTORICUL: ce s-a atins de mai multe ori ────────────────────────────────────────────────
print()
print("=" * 94)
print("3. ISTORICUL — fișiere pe care le-am atins de cele mai multe ori (git, ultimele 30 de zile)")
print("=" * 94)
fisiere = sorted({v for (t, v) in ob_lista if t == "fisier"})
atins = []
for f in fisiere:
    if not os.path.exists(f):
        continue
    n = subprocess.run(["git", "log", "--since=30 days ago", "--oneline", "--", f],
                       stdout=subprocess.PIPE).stdout.decode().count("\n")
    atins.append((n, f, len(ob_lista[("fisier", f)]), len(ob_intrari[("fisier", f)])))
atins.sort(reverse=True)
print("  %-52s %8s %6s %8s" % ("FIȘIER", "commituri", "liste", "intrări"))
for n, f, nl, ni in atins[:20]:
    print("  %-52s %8d %6d %8d" % (f[:52], n, nl, ni))
print("\n  fișiere numite de liste dar NEATINSE în 30 de zile: %d din %d"
      % (sum(1 for n, *_ in atins if n == 0), len(atins)))
