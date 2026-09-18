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
import tokenize

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
                if f.startswith("scan_") or f.startswith("verificator"):
                    continue     # instrumentele NUMESC rute ca să le măsoare, nu ca să le probeze
                if doar_suita and not f.startswith("test_"):
                    continue
                # [D5, 18.09.2026] Un fișier de PROBĂ e `test_*.py` sau orice din `frontend_test/`.
                # Modulele de IMPLEMENTARE (`core/*.py`, `scripts/*.py` ne-test) NU sunt probe — altfel
                # chiar modulul care DEFINEȘTE ruta o „numește" prin propria definiție, iar `NICAIERI`
                # ieșea artificial de mic (3 în loc de realul de zeci). „Nicăieri" înseamnă „în niciun
                # fișier care PROBEAZĂ", nu „în niciun fișier".
                if not (f.startswith("test_") or loc == "frontend_test"):
                    continue
                yield os.path.join(dirpath, f)


_CACHE = {}


def _fara_comentarii(text):
    """[D3, 18.09.2026] Textul fără COMENTARII, ca un nume de rută scris într-un comentariu să nu
    „probeze" ruta. Șirurile rămân (probele lovesc calea prin literal: `cl.post(\"/x/5\")`). Pe fișier
    invalid sintactic, se întoarce textul brut (mai bine zgomot decât o excepție care oprește scanul)."""
    try:
        bucati = []
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                continue
            bucati.append(tok.string)
        return "\n".join(bucati)
    except Exception:
        return text


def _sursele(doar_suita):
    if doar_suita not in _CACHE:
        _CACHE[doar_suita] = [_fara_comentarii(io.open(c, encoding="utf-8", errors="ignore").read())
                              for c in _fisiere_de_proba(doar_suita)]
    return _CACHE[doar_suita]


def _tipar_cale(cale):
    """`/portal/bon/{bon_id}/confirma` → regex care prinde și `/portal/bon/5/confirma`."""
    # [D10, 18.09.2026] Un segment `{id}` se potrivește cu un segment concret (`5`) SAU cu un format
    # `%d`/`%s` — stilul dominant al probelor e `\"/tenants/%d/...\" % tid`, pe care `[^/\"'%]+` îl rata
    # (excludea `%`), iar ruta ieșea fals „nenumită".
    bucati = [re.escape(b) if not (b.startswith("{") and b.endswith("}")) else r"(?:[^/\"'%]+|%[sd])"
              for b in cale.split("/")]
    # ANCORAT la capăt. Fără asta, `/tenants/{id}/produse` se potrivea și într-o probă care cheamă
    # `/tenants/5/produse/7` — adică o rută era declarată „numită" de proba ALTEIA, iar cifra ieșea
    # mult mai mică decât cea a auditului. Capătul admis: ghilimea, `?`, `%` (format), spațiu, `)`.
    return re.compile("/".join(bucati) + r"""(?=["'?%\s)]|$)""")


def nenumite(doar_suita=False, surse=None):
    """[(cale, metoda, functie)] — rute care scriu și pe care nicio probă nu le numește."""
    # `surse` (univers fabricat pentru calibrare/gardă) trece prin ACELAȘI filtru de comentarii ca
    # sursele reale — altfel un comentariu fabricat ar „numi" o rută, iar garda D4 ar minți.
    texte = ([_fara_comentarii(t) for t in surse] if surse is not None else _sursele(doar_suita))
    out = []
    for cale, metoda, nume in rute():
        tipar = _tipar_cale(cale)
        # [D3, 18.09.2026] numele se caută pe GRANIȚĂ DE CUVÂNT, nu ca subșir: `nota_avans` nu mai e
        # „numit" de `nota_avans_platit`, iar `set` nu de `pontaj_set`. Împreună cu `_fara_comentarii`
        # (numele dintr-un comentariu nu mai probează), asta oprește cele 20 de rute „numite" fals.
        tipar_nume = re.compile(r"\b%s\b" % re.escape(nume)) if nume else None
        gasit = False
        for t in texte:
            if (tipar_nume and tipar_nume.search(t)) or tipar.search(t):
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
