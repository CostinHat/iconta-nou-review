# -*- coding: utf-8 -*-
"""scripts/scan_ghid_suprapuneri.py — ghidurile publice care răspund la ACEEAȘI întrebare (comanda Costin 13.10.2026, pct.2a, verbatim
în DECIZII): „grupează ghidurile care răspund la aceeași întrebare … Raportează numărul de grupuri, numărul de pagini implicate și 10
exemple. Nu modifici nimic la grupuri.” Unealta NUMAI MĂSOARĂ: nu atinge niciun ghid.

METODA (deterministă, reproductibilă): titlul ghidului e întrebarea. Două titluri răspund la aceeași întrebare când, după normalizare
(litere mici, fără diacritice, fără cuvinte de legătură, fără terminația flexiunii), diferă NUMAI prin cuvinte de formulare (`FORMULARE`:
„cum se calculează / contabilizează / înregistrează”, „ce trebuie”, anul 2025–2027 …) și au cel puțin 2 cuvinte de conținut comune.
Grupul se formează prin LEGĂTURĂ COMPLETĂ: un ghid intră într-un grup numai dacă e echivalent cu FIECARE membru — fără lanțuri (A~B,
B~C ⇏ A~C), care uneau zeci de titluri diferite.

LIMITA DECLARATĂ: e o măsură LEXICALĂ — prinde reformulările aceleiași întrebări, NU sinonimele („fișa de magazie” / „evidența stocului”)
și nici întrebările echivalente formulate cu alt vocabular; cifra e deci un PLAFON INFERIOR. Precizia a fost verificată de mână pe un
eșantion (raportul lotului).

Uz: python scripts/scan_ghid_suprapuneri.py            -> cifrele + 10 exemple
    python scripts/scan_ghid_suprapuneri.py --csv      -> scrie `ghid_suprapuneri.csv` (grup, slug, titlu), lista pentru aprobare
"""
import collections
import csv
import glob
import os
import re
import sys
import unicodedata

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TINTA = os.path.join(RAD, "ghid_suprapuneri.csv")
LEGATURA = set("""a al ale alt alte am ar are as asa au ca care cei cel cele cu cum da daca de despre din dintr dintre doar e
este fi fie fost i ii il in intr intre iar la le li lui ma mai mi ne ni o ori pe pentru prin sa sau se si sunt te tu un una unei unui
va vs ghid ul""".split())   # „ce / când / cine / unde / cât” schimbă întrebarea: rămân
#: terminațiile flexiunii (articol, plural, genitiv) — tăiate o dată, ca „adaosul” = „adaos”, dar „concediere” ≠ „concediu”
_SUFIXE = ("urilor", "ilor", "elor", "ului", "lor", "ul", "ea", "ei", "le", "ii", "a", "e", "i")
#: cuvinte care schimbă FORMULAREA, nu întrebarea
_FORMULARE = """calculeaza calculez calculezi calcul calculul contabilizeaza contabilizare contabilizarea contabilitatea contabilitate
contabil inregistreaza inregistrez inregistrare inregistrarea procedura procedeaza trebuie depun depune aplica aplic pasi pas exemplu
explicat regula regulile modul face fac facem facut gestioneaza gestionez gestionare trateaza tratez tratezi tratam tratarea tratament
caz situatie practica intrebare raspuns 2025 2026 2027 an anul firma firme firmei societate complet obligatii obligatoriu cum"""


def _radacina(w):
    for s in _SUFIXE:
        if w.endswith(s) and len(w) - len(s) >= 4:
            return w[:-len(s)]
    return w


def _fara_diacritice(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def cuvinte(titlu):
    """Cuvintele de conținut ale titlului. O literă mare singură („codul A”) și un număr („2 ore”) sunt conținut, nu legătură."""
    t = _fara_diacritice(titlu)
    out = set()
    for w in re.findall(r"[A-Za-z0-9]+", t):
        if re.fullmatch(r"[A-Z]|\d+", w):
            out.add("#" + w)
        elif w.lower() not in LEGATURA and len(w) > 1:
            out.add(_radacina(w.lower()))
    return frozenset(out)


FORMULARE = frozenset(_radacina(w) for w in _FORMULARE.split())


def ghiduri(director=None):
    out = []
    for cale in sorted(glob.glob(os.path.join(director or os.path.join(RAD, "ghid"), "*.md"))):
        t = open(cale, encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
        if not m:
            continue
        titlu = next((ln.split(":", 1)[1].strip().strip('"') for ln in m.group(1).splitlines() if ln.startswith("title:")), "")
        out.append((os.path.basename(cale)[:-3], titlu))
    return out


def grupuri(lista):
    T = [cuvinte(t) for _s, t in lista]

    def acelasi(i, j):
        return len(T[i] & T[j]) >= 2 and not ((T[i] ^ T[j]) - FORMULARE)

    idx = collections.defaultdict(list)
    for i, ts in enumerate(T):
        for w in ts:
            idx[w].append(i)
    perechi = []
    for i, ts in enumerate(T):
        cand = collections.Counter(j for w in ts for j in idx[w] if j > i)
        perechi += [(k, i, j) for j, k in cand.items() if k >= 2 and acelasi(i, j)]
    perechi.sort(key=lambda x: (-x[0], x[1], x[2]))
    al, membri = {}, {}
    for _k, i, j in perechi:
        gi, gj = al.get(i), al.get(j)
        if gi is None and gj is None:
            n = len(membri)
            membri[n] = [i, j]
            al[i] = al[j] = n
        elif gi is not None and gj is None and all(acelasi(j, m) for m in membri[gi]):
            membri[gi].append(j)
            al[j] = gi
        elif gj is not None and gi is None and all(acelasi(i, m) for m in membri[gj]):
            membri[gj].append(i)
            al[i] = gj
    return sorted(([lista[i] for i in sorted(v)] for v in membri.values()), key=lambda g: (-len(g), g[0][1]))


if __name__ == "__main__":
    sys.path.insert(0, RAD)
    import argumente_script  # noqa: F401
    argv = argumente_script.citeste(sys.argv[1:], __doc__, flaguri=("--csv",), prefix="[suprapuneri]")
    lista = ghiduri()
    gr = grupuri(lista)
    print("ghiduri publicate: %d · grupuri: %d · pagini în grupuri: %d · cel mai mare grup: %d"
          % (len(lista), len(gr), sum(len(g) for g in gr), max(len(g) for g in gr)))
    for g in gr[:10]:
        print("—", " | ".join(t for _s, t in g))
    if "--csv" in argv:
        with open(TINTA, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["grup", "slug", "titlu"])
            for n, g in enumerate(gr, 1):
                for s, t in g:
                    w.writerow([n, s, t])
        print("scris %s" % TINTA)
