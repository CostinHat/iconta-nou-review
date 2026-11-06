#!/usr/bin/env python3
"""verifica_liste_exceptii.py — comanda 16.8-B, pct.4: cele două liste ale ferestrelor fără acțiune principală trebuie să spună același lucru.

    verifica_liste_exceptii.py [--cadru <fișier>] [--verificator <fișier>]

Listele: `static/js/cadru.js::FARA_ACTIUNE_PRINCIPALA` (expresie regulată pe titlul ferestrei) și `scripts/verificator_design.py::EXCEPTII_B` (dicționar pe numele
ecranului din registru, cu sufixul firmei). Numai biblioteca standard; nu pornește browser și nu citește baza. Rulat de scripts/inainte_de_commit.sh la fiecare commit.
Ieșire 0 = VERDE (o linie cu numerele), 1 = câte o linie „REFUZ: <motiv>” pe motiv. Constantele de mai jos sunt ale arhitectului."""
import argparse
import ast
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARCAJE = ("· CUI ",)
DOAR_PY = {"Supervizor": "stare", "Declarații lucrate": "stare", "Activitate": "meniu", "Setări cont": "meniu", "Migrare cabinet": "meniu",
           "Ghiduri": "meniu", "Panou Admin — Anunțuri": "meniu"}
INTERZISE = ("Tipare de erori", "Panou Admin — Sănătate server")
CONDITIE_MENIU = "FARA_ACTIUNE_PRINCIPALA.test(titlu) || _esteMeniu("
_INCEPUT = "export const FARA_ACTIUNE_PRINCIPALA = "


def _normal(nume):
    return re.sub(r" F\d+$", "", nume)


def extrage_cadru(text):
    """-> (titluri, marcaje) din FARA_ACTIUNE_PRINCIPALA; ValueError cu motivul când forma nu e cea așteptată."""
    for nr, ln in enumerate(text.splitlines(), 1):
        if not ln.startswith(_INCEPUT):
            continue
        rest = ln[len(_INCEPUT):]
        sfarsit = rest.find("/;")
        m = re.match(r"^/\^\(([^()]*)\)\$\|(.+)$", rest[:sfarsit]) if sfarsit >= 0 else None
        if not m:
            raise ValueError("forma lui FARA_ACTIUNE_PRINCIPALA (cadru.js, linia %d) nu e recunoscută; se așteaptă /^(titlu|…)$|marcaj/" % nr)
        return m.group(1).split("|"), m.group(2).split("|")
    raise ValueError("FARA_ACTIUNE_PRINCIPALA nu e în cadru.js (se așteaptă o linie care începe cu «%s»)" % _INCEPUT)


def extrage_verificator(text):
    """-> dicționarul EXCEPTII_B (ast, fără import: modulul importă playwright); ValueError când lipsește."""
    for nod in ast.parse(text).body:
        if isinstance(nod, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "EXCEPTII_B" for t in nod.targets):
            return ast.literal_eval(nod.value)
    raise ValueError("EXCEPTII_B nu e în verificator_design.py")


def verifica(text_cadru, text_verificator):
    """-> lista motivelor de refuz (goală = VERDE)."""
    try:
        titluri, marcaje = extrage_cadru(text_cadru)
        exceptii = extrage_verificator(text_verificator)
    except ValueError as e:
        return [str(e)]
    motive = []
    normale = {}
    for nume, cat in exceptii.items():
        if cat not in ("stare", "meniu"):
            motive.append("EXCEPTII_B[%s] = %s, se așteaptă „stare” sau „meniu”" % (nume, cat))
        normale[_normal(nume)] = cat
    for t in titluri:
        if t not in normale:
            motive.append("titlul „%s” din cadru.js nu are intrare în EXCEPTII_B" % t)
    for n, cat in normale.items():
        if n in titluri:
            if n in DOAR_PY:
                motive.append("„%s” e titlu în cadru.js și e încă în DOAR_PY; scoate-l din DOAR_PY (decizia arhitectului)" % n)
        elif n not in DOAR_PY:
            motive.append("„%s” din EXCEPTII_B nu are titlu în cadru.js și nu e în DOAR_PY" % n)
        elif DOAR_PY[n] != cat:
            motive.append("„%s” are categoria „%s” în EXCEPTII_B și „%s” în DOAR_PY" % (n, cat, DOAR_PY[n]))
    for n in DOAR_PY:
        if n not in normale:
            motive.append("„%s” e în DOAR_PY, dar nu și în EXCEPTII_B" % n)
    if sorted(marcaje) != sorted(MARCAJE):
        motive.append("marcajele din cadru.js (%s) diferă de MARCAJE (%s)" % (", ".join(marcaje), ", ".join(MARCAJE)))
    if CONDITIE_MENIU not in text_cadru:
        motive.append("cadru.js nu mai combină FARA_ACTIUNE_PRINCIPALA cu _esteMeniu; cele cinci „meniu” din DOAR_PY nu mai au acoperire")
    for n in INTERZISE:
        if n in normale or n in titluri:
            motive.append("„%s” are acțiune principală: se repară în produs, nu se exceptează (17.3)" % n)
    return motive


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cadru", default=os.path.join(RAD, "static", "js", "cadru.js"))
    ap.add_argument("--verificator", default=os.path.join(RAD, "scripts", "verificator_design.py"))
    a = ap.parse_args(argv)
    tc, tv = open(a.cadru, encoding="utf-8").read(), open(a.verificator, encoding="utf-8").read()
    motive = verifica(tc, tv)
    if motive:
        for m in motive:
            print("[liste exceptii] REFUZ: " + m)
        return 1
    titluri, _ = extrage_cadru(tc)
    exceptii = extrage_verificator(tv)
    print("[liste exceptii] VERDE: %d titluri în cadru.js, %d intrări în EXCEPTII_B, %d numai în EXCEPTII_B (DOAR_PY)" % (len(titluri), len(exceptii), len(DOAR_PY)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
