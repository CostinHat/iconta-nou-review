# -*- coding: utf-8 -*-
"""FAZA 4, axa D despicata: „odata cu fixul" ascunde DOUA lucruri, iar „singura" ascunde alte doua.

`scan_garzi.axe_git` da 329 „cu fixul" / 49 „singura", si isi declara singur limita in docstring:
„singura (INAINTE, SAU pe cod existent)". Planul intreaba altceva: *daca majoritatea garzilor sunt
scrise DUPA fix si totusi prind regresii reale, regula „garda inainte de reparatie" e mai slaba decat
credem*. Deci trebuie stiut cate sunt DUPA, nu cate sunt „odata cu".

CE SE POATE DESPICA, mecanic:
  - „odata cu fixul" -> commitul de introducere REPARA ceva (mesaj cu vocabular de reparatie) sau
    ADUCE ceva nou. O garda scrisa impreuna cu reparatia NU incalca regula; una scrisa impreuna cu o
    functionalitate noua nici atat.
  - „singura" -> exista o REPARATIE a unui modul pe care garda il importa, comisa INAINTEA ei, in
    fereastra declarata de mai jos? Daca da, garda a venit DUPA o reparatie a subiectului ei.

CE NU SE POATE, si o declar: nu exista in date legatura „garda X pazeste fixul Y". Vocabularul de
reparatie e un proxy pe mesajul de commit, iar fereastra e o alegere. Cifrele de mai jos sunt
INDICII cu definitie scrisa, nu masuratori ale intrebarii exacte.

SONDA DE CITIRE.
"""
import collections
import datetime
import os
import re
import subprocess
import sys

sys.path.insert(0, "/home/costin/iconta_nou")
RAD = "/home/costin/iconta_nou"
FEREASTRA_ZILE = 14   # ALEGERE declarata: „la scurt timp dupa" = doua saptamani

REPARATIE = re.compile(r"\b(repar|reparat|fix|corect|neconformitate|bug|gresit|greșit)", re.I)


def git(*a):
    return subprocess.run(["git", "-C", RAD] + list(a), capture_output=True, text=True).stdout


def introducere(rel):
    """(hash, data, mesaj) al commitului care a ADAUGAT fisierul."""
    out = git("log", "--diff-filter=A", "--format=%H|%ad|%s", "--date=short", "--", rel).split("\n")
    out = [x for x in out if x.strip()]
    if not out:
        return None
    h, d, s = out[0].split("|", 2)
    return h, datetime.date(*map(int, d.split("-"))), s


def module_importate(cale):
    try:
        src = open(cale, encoding="utf-8", errors="replace").read()
    except OSError:
        return set()
    m = set(re.findall(r"^\s*from\s+core\s+import\s+([\w, ]+)", src, re.M))
    out = set()
    for buc in m:
        for x in buc.split(","):
            x = x.strip().split(" as ")[0].strip()
            if re.match(r"^\w+$", x):
                out.add(x)
    out |= set(re.findall(r"^\s*from\s+core\.(\w+)\s+import", src, re.M))
    return out


def reparatii_modul(modul, inainte_de):
    """Commituri pe core/<modul>.py cu vocabular de reparatie, anterioare datei date."""
    out = []
    for linie in git("log", "--format=%H|%ad|%s", "--date=short",
                     "--", "core/%s.py" % modul).split("\n"):
        if not linie.strip():
            continue
        h, d, s = linie.split("|", 2)
        dd = datetime.date(*map(int, d.split("-")))
        if dd < inainte_de and REPARATIE.search(s):
            out.append((h, dd, s))
    return out


def main():
    from core import scan_garzi as sg
    garzi = sg.fisiere_garda(os.path.join(RAD, "core"))
    axe = sg.axe_git(RAD, garzi)
    print("=" * 100)
    print("PORNIND DE LA CIFRA EXISTENTA: cu fixul %d · singura %d · necunoscut %d"
          % (len(axe["cu_fixul"]), len(axe["singura"]), len(axe["necunoscut"])))
    print("=" * 100)

    print("\n1. «ODATA CU FIXUL» — commitul de introducere REPARA sau ADUCE?")
    rep, nou = [], []
    for rel in axe["cu_fixul"]:
        info = introducere(rel)
        if not info:
            continue
        (rep if REPARATIE.search(info[2]) else nou).append((rel, info[2]))
    print("   commit de REPARATIE : %d" % len(rep))
    print("   commit de ADUCERE   : %d" % len(nou))
    print("   -> garda scrisa impreuna cu reparatia NU incalca regula; nici cea scrisa cu o")
    print("      functionalitate noua. Deci cele %d nu sunt «dupa fix»." % (len(rep) + len(nou)))

    print("\n2. «SINGURA» — a venit DUPA o reparatie a modulului pe care il pazeste?")
    dupa, curate, fara_modul = [], [], []
    for rel in axe["singura"]:
        info = introducere(rel)
        if not info:
            continue
        _h, data, _s = info
        mods = module_importate(os.path.join(RAD, rel))
        if not mods:
            fara_modul.append(rel)
            continue
        lovite = []
        for m in mods:
            for h, dd, s in reparatii_modul(m, data):
                if (data - dd).days <= FEREASTRA_ZILE:
                    lovite.append((m, dd, s))
        if lovite:
            dupa.append((rel, lovite))
        else:
            curate.append(rel)
    print("   DUPA o reparatie a subiectului (in %d zile): %d" % (FEREASTRA_ZILE, len(dupa)))
    print("   fara reparatie recenta a subiectului       : %d" % len(curate))
    print("   fara modul core identificabil              : %d" % len(fara_modul))
    for rel, lov in dupa[:10]:
        m, dd, s = lov[0]
        print("      %-46s dupa %s (%s) %s" % (os.path.basename(rel), m, dd, s[:44]))

    print("\n3. CE INSEAMNA, citit cu grija")
    total = len(axe["cu_fixul"]) + len(axe["singura"])
    print("   garzi cu subiect stabilit: %d" % total)
    print("   candidate la «scrisa DUPA fix»: %d (%.1f%%)" % (len(dupa), 100.0 * len(dupa) / max(total, 1)))
    print("   restul de %d nu sunt «dupa fix»: ori repara odata cu garda, ori aduc ceva nou," % (total - len(dupa)))
    print("   ori pazesc cod existent fara reparatie recenta a subiectului.")


main()
