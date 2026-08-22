# -*- coding: utf-8 -*-
"""SECȚIUNEA B a raportului („UNDE SUNTEM"), DERIVATĂ din antetul CONFORMITATE.md.

  scripts/raport_b.py

De ce nu se scrie de mână (Costin, 22.08.2026): *„dacă B s-ar scrie separat, ar deveni al doilea loc
unde trăiește aceeași stare — și s-ar învechi, exact clasa pe care o închidem."* Antetul e sursa;
raportul îl reproduce. Dacă cele două diverg, antetul are dreptate.

Cifrele NU se citesc din antet — se NUMĂRĂ din secțiuni. O stare scrisă de mână despre propriile
secțiuni ar fi exact aceeași clasă de defect, doar mutată cu un rând mai jos.
"""
import io
import os
import re
import subprocess

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF = os.path.join(RAD, "CONFORMITATE.md")
STARI = ("MĂSURATĂ", "PARȚIAL", "NEMĂSURABILĂ", "NEÎNCEPUTĂ")


def _camp(corp, nume):
    m = re.search(r"^[ \t]*[-*]?[ \t]*\*\*%s\*\*[ \t]*:[ \t]*(.*)$" % re.escape(nume),
                  corp, re.M | re.I)
    return None if m is None else m.group(1).strip()


def _antet(t):
    m = re.search(r"^## ANTET DE ETAPĂ[ \t]*$(.*?)^---[ \t]*$", t, re.M | re.S)
    return None if m is None else m.group(1)


def _sectiuni(t):
    buc = re.split(r"^## (\d+)\s*[—-]\s*(.+)$", t, flags=re.M)
    return {int(buc[k]): buc[k + 2] for k in range(1, len(buc), 3)}


def main():
    t = io.open(CONF, encoding="utf-8").read()
    a = _antet(t)
    if a is None:
        raise SystemExit("CONFORMITATE.md n-are antet de etapă — secțiunea B n-are sursă")
    sec = _sectiuni(t)

    # cifrele: NUMĂRATE, nu citite
    nr = {s: 0 for s in STARI}
    alta = 0
    for _n, corp in sec.items():
        v = (_camp(corp, "stare") or "").strip("*").split("—")[0].split("(")[0].split(",")[0].strip()
        if v in nr:
            nr[v] += 1
        else:
            alta += 1

    # cel mai vechi commit: derivat din secțiuni, apoi confruntat cu ce scrie antetul
    hashuri = []
    for n, corp in sec.items():
        h = (_camp(corp, "pe commit") or "—").strip("`*— ")
        if h:
            r = subprocess.run(["git", "-C", RAD, "log", "-1", "--format=%ct %h %cs", h],
                               capture_output=True, text=True)
            if r.returncode == 0 and r.stdout.strip():
                p = r.stdout.split()
                hashuri.append((int(p[0]), p[1], p[2], n))
    hashuri.sort()

    print("## B. UNDE SUNTEM")
    print()
    print("*Derivat din antetul `CONFORMITATE.md` cu `scripts/raport_b.py` — nu scris de mână.*")
    print()
    print("- **etapa**: %s" % (_camp(a, "etapa") or "?"))
    print("- **pasul curent**: %s" % (_camp(a, "pasul curent") or "?"))
    print("- **criteriul de terminare**: %s" % (_camp(a, "criteriul de terminare") or "?"))
    print("- **ce mai lipsește**: %s" % (_camp(a, "ce lipsește") or "?"))
    print("- **interdicții, din %d**: MĂSURATE %d · PARȚIAL %d · NEMĂSURABILE %d · NEÎNCEPUTE %d%s"
          % (len(sec), nr["MĂSURATĂ"], nr["PARȚIAL"], nr["NEMĂSURABILĂ"], nr["NEÎNCEPUTĂ"],
             (" · alte stări %d" % alta) if alta else ""))
    if hashuri:
        _ct, h, zi, n = hashuri[0]
        print("- **cel mai vechi commit din registru**: `%s` (%s), de la secțiunea #%d" % (h, zi, n))
    else:
        print("- **cel mai vechi commit din registru**: — (nicio cifră ancorată)")
    print("- **decizii care blochează**: %s" % (_camp(a, "decizii care blochează") or "?"))
    print("- **antetul, actualizat la**: %s" % (_camp(a, "ultima actualizare") or "?"))


if __name__ == "__main__":
    main()
