# -*- coding: utf-8 -*-
"""Care gărzi asertează pe TEXT în loc de STRUCTURĂ.

Regula, dată de Costin 24.08.2026: *o gardă asertează pe structură, nu pe text.* Nu „cheia apare
undeva în răspuns", ci „câmpul are valoarea asta". Un JSON se parsează și se verifică pe câmpuri; un
XML, pe elemente; o randare, pe arbore; codul, pe AST. Unde nu se poate, se declară de ce lângă gardă.

CE E ÎN CLASĂ, structural (toate trei deodată):
  1. fișierul numește o sursă `.py`/`.js` (literal de șir cu extensia),
  2. o deschide (`open`/`read_text`/`walk`/`glob`),
  3. și asertează `"șir" in ceva` — chiar semnalul folosit de `scan_ancore`,
iar NU o curăță de proză înainte (`fara_proza`, `domenii_docstring`, `ast.parse`).

DE CE CONTEAZĂ: un `"cheie" in text` nu păzește lucrul, păzește **proza de lângă lucru**. Nu poate
deosebi „e implementat" de „e descris" — trei instanțe într-o singură zi, 24.08, toate în gărzi
scrise de mine, prinse abia de RED-proof.

CIFRA, ȘI DE CE NU E 13. Interdicția 18 spunea **14** (una exclusă prin natura ei -> 13), măsurat
ad-hoc pe 22.08 pe 369 de fișiere-gardă. Măsurătoarea aia **nu e reproductibilă**: n-a rămas niciun
instrument în urma ei, iar azi sunt 397 de fișiere. Reconstruită pe domeniul de mai sus, clasa e
**51**, nu 13 — deci cifra veche era un **plafon inferior** al unui domeniu mai îngust, nu un
inventar. Clichetul se pune pe 51, fiindcă doar el se poate recalcula mâine.

CELE DOUĂ DIRECȚII DE EȘEC (METODA §22 — un instrument care greșește în ambele n-are niciun plafon):
  - **ratează**: o gardă care citește sursa printr-un helper propriu, fără literal cu extensie în
    fișier, nu intră în domeniu; la fel una care caută cu `re.search` în loc de `in`;
  - **revendică**: un fișier care doar *pomenește* `"ceva.js"` într-un docstring și, separat, are un
    `in` pe altceva, e numărat pe nedrept.
Amândouă au calibrare construită în `core/test_garzi_pe_text.py`. Până când nu erau amândouă acolo,
cifra n-avea voie să fie scrisă nicăieri.
"""
import ast
import io
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Semnale că fișierul SCOATE proza înainte de a asertă — adică se uită la structură, nu la text.
CURATA = ("fara_proza", "domenii_docstring", "parse", "walk", "get_docstring")


def _fisiere(radacini):
    out = []
    for baza in radacini:
        for rad, _d, fis in os.walk(baza):
            if "__pycache__" in rad:
                continue
            for f in fis:
                if f.startswith("test_") and f.endswith(".py"):
                    out.append(os.path.join(rad, f))
    return sorted(out)


def numeste_sursa(arbore):
    """Există un literal de șir care se termină în `.py` sau `.js`?"""
    for n in ast.walk(arbore):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            if n.value.endswith(".py") or n.value.endswith(".js"):
                return True
    return False


def o_deschide(arbore):
    for n in ast.walk(arbore):
        if isinstance(n, ast.Call):
            nume = getattr(n.func, "attr", None) or getattr(n.func, "id", None)
            if nume in ("open", "read_text", "read", "walk", "glob", "rglob", "iglob"):
                return True
    return False


def aserteaza_pe_text(arbore):
    """`"șir" in ceva`, cu șirul destul de lung cât să fie o ancoră, nu un caracter."""
    for n in ast.walk(arbore):
        if (isinstance(n, ast.Compare) and any(isinstance(o, ast.In) for o in n.ops)
                and isinstance(n.left, ast.Constant) and isinstance(n.left.value, str)
                and len(n.left.value) > 3):
            return True
    return False


def curata_proza(arbore):
    for n in ast.walk(arbore):
        if isinstance(n, ast.Call):
            nume = getattr(n.func, "attr", None) or getattr(n.func, "id", None)
            if nume in CURATA:
                return True
    return False


def inventar(radacini=None):
    """[(cale_relativă, stare)] cu stare ∈ `text_brut` | `structura`.

    Fișierele care nu ating deloc o sursă, sau n-o caută cu `in`, NU apar — nu sunt în clasă și nu
    se numără nici ca trecute (absența unei verificări nu e o verificare)."""
    if radacini is None:
        radacini = [os.path.join(RAD, "core"), os.path.join(RAD, "frontend_test")]
    out = []
    for cale in _fisiere(radacini):
        try:
            arb = ast.parse(io.open(cale, encoding="utf-8").read())
        except SyntaxError:
            continue
        if not (numeste_sursa(arb) and o_deschide(arb) and aserteaza_pe_text(arb)):
            continue
        stare = "structura" if curata_proza(arb) else "text_brut"
        try:
            rel = os.path.relpath(cale, RAD)
        except ValueError:
            rel = cale
        out.append((rel, stare))
    return out


def pe_text(radacini=None):
    return [c for c, s in inventar(radacini) if s == "text_brut"]
