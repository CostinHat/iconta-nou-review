# -*- coding: utf-8 -*-
"""scripts/argumente_script.py — argumentele unui script de lucru, citite ÎNAINTE de orice efect (decizia Costin 12.10.2026, verbatim în
DECIZII: „--help la e2e_poarta.py: repară-l în acest lot.”). Clasa: un script cu argumente citite de mână ignora un flag necunoscut și
pornea lucrul — `e2e_poarta.py --help` pornea plasa întreagă (o rulare oprită a lăsat firma sintetică în baza de test),
`publica_static.py --help` publica staticul, `cifre_referinta.py -h` scria `-h.json` / `-h.md` în directorul curent.

`citeste(argv, doc, flaguri, cu_valoare, pozitionale)` -> lista argumentelor, sau iese: `-h` / `--help` tipărește uzul (`doc`) cu cod
0; un argument necunoscut, un flag cu valoare gol sau prea multe poziționale -> motivul + uzul, cod 2. Nimic nu pornește în ambele cazuri.
"""
import sys


def motiv(argv, flaguri=(), cu_valoare=(), pozitionale=0):
    """Motivul refuzului, sau None dacă argumentele sunt cele cunoscute."""
    necunoscute = [a for a in argv if a.startswith("-") and a not in flaguri and not a.startswith(tuple(cu_valoare))]
    if necunoscute:
        return "argument necunoscut: %s" % ", ".join(necunoscute)
    goale = [a for a in argv if cu_valoare and a.startswith(tuple(cu_valoare)) and not a.split("=", 1)[1]]
    if goale:
        return "argument fără valoare: %s" % ", ".join(goale)
    if len([a for a in argv if not a.startswith("-")]) > pozitionale:
        return "cel mult %d argument%s fără „--”" % (pozitionale, "" if pozitionale == 1 else "e") if pozitionale else "niciun argument fără „--”"
    return None


def citeste(argv, doc, flaguri=(), cu_valoare=(), pozitionale=0, prefix="[script]"):
    if any(a in ("-h", "--help") for a in argv):
        print(doc)
        sys.exit(0)
    m = motiv(argv, flaguri, cu_valoare, pozitionale)
    if m:
        uz = doc[doc.index("Uz:"):].rstrip() if "Uz:" in doc else doc
        print("%s %s — nimic nu pornește.\n%s" % (prefix, m, uz), file=sys.stderr)
        sys.exit(2)
    return list(argv)
