# -*- coding: utf-8 -*-
"""Ce rută SCRIE fără ca vreo probă s-o numească.

DE CE. Auditul (R1) a numărat 59 de rute pe care nicio probă nu le numește, din care **21 scriu**.
Nuanța pe care a scris-o tot el, ca să nu fie citit mai rău decât e: rutele *sunt* acoperite
structural — sweep-urile generice le trec pe toate, deci nimeni nu poate adăuga o rută fără gardă
sau fără model de corp. Ce lipsește e **comportamentul**: ce se schimbă în lume când ruta se apasă.

CUM MĂSOARĂ. Rutele se iau din `main.app.routes`, nu dintr-o listă scrisă — o rută nouă intră
singură. O rută e „numită" dacă un fișier de probă conține **numele funcției** ei sau un șir care se
potrivește cu **calea** ei (`{id}` → orice segment). Ambele, fiindcă probele se scriu în ambele
feluri: unele cheamă `main.<functie>`, altele lovesc `TestClient`-ul pe cale.

UNDE E OARBĂ, scris ca să nu fie citită mai larg:
  * „numită" ≠ „probată pe comportament". O probă care doar cere ruta și se uită la codul HTTP
    numără la fel ca una care verifică ce s-a schimbat. Instrumentul spune **cine n-are nimic**, nu
    cine are destul.
  * `frontend_test/` intră în căutare, deși pytest nu culege fișierele de acolo. E deliberat: o rută
    probată acolo nu e „nenumită", e probată în afara porții — iar cifra asta n-are voie să spună
    altceva decât spune. Cine vrea numai suita, citește `doar_suita=True`.
"""
from __future__ import annotations

import io
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)   # rulat si direct, nu doar importat din suita
SCRIU = ("POST", "PUT", "PATCH", "DELETE")
LOCURI_PROBE = ("core", "frontend_test", "scripts")


def rute(doar_scrieri=True):
    """[(cale, metoda, nume_functie)] din aplicația vie."""
    import main
    out = []
    for r in main.app.routes:
        cale = getattr(r, "path", "")
        nume = getattr(getattr(r, "endpoint", None), "__name__", "")
        for m in sorted(getattr(r, "methods", set()) or set()):
            if m in ("HEAD", "OPTIONS"):
                continue
            if doar_scrieri and m not in SCRIU:
                continue
            out.append((cale, m, nume))
    return sorted(set(out))


def _fisiere_de_proba(doar_suita=False):
    for loc in LOCURI_PROBE:
        d = os.path.join(RAD, loc)
        if not os.path.isdir(d):
            continue
        for dirpath, dirnames, files in os.walk(d):
            dirnames[:] = [x for x in dirnames if x not in ("__pycache__", "venv")]
            for f in files:
                if not f.endswith(".py"):
                    continue
                if doar_suita and not f.startswith("test_"):
                    continue
                if f.startswith("scan_") or f.startswith("verificator"):
                    continue     # instrumentele NUMESC rute ca să le măsoare, nu ca să le probeze
                yield os.path.join(dirpath, f)


_CACHE = {}


def _sursele(doar_suita):
    if doar_suita not in _CACHE:
        _CACHE[doar_suita] = [io.open(c, encoding="utf-8", errors="ignore").read()
                              for c in _fisiere_de_proba(doar_suita)]
    return _CACHE[doar_suita]


def _tipar_cale(cale):
    """`/portal/bon/{bon_id}/confirma` → regex care prinde și `/portal/bon/5/confirma`."""
    bucati = [re.escape(b) if not (b.startswith("{") and b.endswith("}")) else r"[^/\"'%]+"
              for b in cale.split("/")]
    # ANCORAT la capăt. Fără asta, `/tenants/{id}/produse` se potrivea și într-o probă care cheamă
    # `/tenants/5/produse/7` — adică o rută era declarată „numită" de proba ALTEIA, iar cifra ieșea
    # mult mai mică decât cea a auditului. Capătul admis: ghilimea, `?`, `%` (format), spațiu, `)`.
    return re.compile("/".join(bucati) + r"""(?=["'?%\s)]|$)""")


def nenumite(doar_suita=False, surse=None):
    """[(cale, metoda, functie)] — rute care scriu și pe care nicio probă nu le numește."""
    texte = surse if surse is not None else _sursele(doar_suita)
    out = []
    for cale, metoda, nume in rute():
        tipar = _tipar_cale(cale)
        gasit = False
        for t in texte:
            if (nume and nume in t) or tipar.search(t):
                gasit = True
                break
        if not gasit:
            out.append((cale, metoda, nume))
    return out


if __name__ == "__main__":
    tot = rute()
    n_toate = nenumite()
    n_suita = nenumite(doar_suita=True)
    print("rute care scriu: %d" % len(tot))
    print("nenumite nicăieri (core+frontend_test+scripts): %d" % len(n_toate))
    print("nenumite ÎN SUITĂ (doar core/test_*.py): %d" % len(n_suita))
    for cale, metoda, nume in n_suita:
        semn = " " if (cale, metoda, nume) in n_toate else "*"   # * = probată în afara suitei
        print("  %s %-6s %-45s %s" % (semn, metoda, cale, nume))
