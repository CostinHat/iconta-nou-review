# -*- coding: utf-8 -*-
"""CE NU S-A VERIFICAT — derivat din registre și din cod, scris ca atare, fără atenuare.

Rulează:  ./venv/bin/python audit/deriva_neverificatul.py

Nu scrie nimic. Tipărește:
  A. RESTANȚELE DESCHISE, cu felul, contorul și condiția de deblocare.
  B. INTERDICȚIILE care nu sunt MĂSURATE.
  C. `xfail(strict=True)` — datoria verificabilă mecanic, cu motivul fiecăreia.
  D. ORBIREA DECLARATĂ a instrumentelor — ce spun ele însele că NU văd.
  E. RUTELE fără probă în suită.
  F. CHECKLISTUL DE BROWSER — ce acoperă și ce nu.

*Regula acestui fișier: nimic nu se atenuează. Dacă o cifră e mare, se scrie mare.*
"""
from __future__ import annotations

import ast
import io
import os
import re
import sys

RAD = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(RAD) == "audit":
    RAD = os.path.dirname(RAD)
if RAD not in sys.path:
    sys.path.insert(0, RAD)


def _linie(ch="-", n=100):
    print(ch * n)


def _cit(p):
    return io.open(os.path.join(RAD, p), encoding="utf-8").read()


# ── A. RESTANȚELE ────────────────────────────────────────────────────────────────────────────
def sectiunea_A():
    from core import test_conformitate as _tc
    print("A. RESTANȚE DESCHISE — fiecare cu felul ei și cu CE O ÎNCHIDE")
    _linie()
    rest = _tc._restante()
    deschise = []
    for cod, (titlu, corp) in sorted(rest.items(), key=lambda x: int(x[0][1:])):
        stare = (_tc._camp(corp, "stare") or "").strip("* ")
        if not stare.startswith("DESCHIS"):
            continue
        deschise.append((cod, titlu, _tc._camp(corp, "felul"), _tc._camp(corp, "cine deblochează"),
                         _tc._camp(corp, "condiția de deblocare")))
    for cod, titlu, fel, cine, cond in deschise:
        print("  %-6s [%s / %s] %s" % (cod, (fel or "?").strip("* "), (cine or "?").strip("* "),
                                       titlu[:86]))
        if cond:
            print("         închide când: %s" % cond[:150])
    _linie()
    print("  TOTAL RESTANȚE DESCHISE: %d" % len(deschise))
    print()


# ── B. INTERDICȚIILE ─────────────────────────────────────────────────────────────────────────
def sectiunea_B():
    from core import test_conformitate as _tc
    print("B. INTERDICȚIILE din PLAN_ARHITECTURA care NU sunt MĂSURATE")
    _linie()
    plan = _tc._interdictii_din_plan()
    sect = _tc._sectiuni_interdictii() if hasattr(_tc, "_sectiuni_interdictii") else None
    t = _cit("CONFORMITATE.md")
    pe_stare = {}
    for nr in sorted(plan):
        m = re.search(r"^### (?:Interdic[țt]ia )?%d\b.*?$" % nr, t, re.M)
        stare = "NEÎNCEPUTĂ"
        if m:
            bloc = t[m.end():m.end() + 4000]
            ms = re.search(r"^[ \t]*[-*]?[ \t]*\*\*stare\*\*[ \t]*:[ \t]*(.*)$", bloc, re.M)
            if ms:
                stare = ms.group(1).strip().strip("*").split("(")[0].strip()
        pe_stare.setdefault(stare, []).append(nr)
    for stare in sorted(pe_stare):
        nre = pe_stare[stare]
        marcaj = "" if stare == "MĂSURATĂ" else "   <-- NEMĂSURATĂ"
        print("  %-16s %3d : %s%s" % (stare, len(nre),
                                      ", ".join(str(x) for x in nre[:24]) +
                                      (" …" if len(nre) > 24 else ""), marcaj))
    nem = sum(len(v) for k, v in pe_stare.items() if k != "MĂSURATĂ")
    _linie()
    print("  INTERDICȚII CARE NU SUNT MĂSURATE: %d din %d" % (nem, len(plan)))
    print("  (starea se citește din CONFORMITATE.md; `raport_b.py` dă același total)")
    print()


# ── C. xfail ─────────────────────────────────────────────────────────────────────────────────
def sectiunea_C():
    print("C. `xfail(strict=True)` — datoria verificabilă mecanic, cu MOTIVUL fiecăreia")
    _linie()
    n = 0
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if not f.startswith("test_"):
            continue
        try:
            src = io.open(os.path.join(RAD, "core", f), encoding="utf-8").read()
            arb = ast.parse(src)
        except SyntaxError:
            continue
        for nod in ast.walk(arb):
            if not isinstance(nod, ast.FunctionDef):
                continue
            for dec in nod.decorator_list:
                if not (isinstance(dec, ast.Call) and "xfail" in ast.dump(dec.func)):
                    continue
                strict = any(k.arg == "strict" and getattr(k.value, "value", None) is True
                             for k in dec.keywords)
                motiv = next((k.value.value for k in dec.keywords
                              if k.arg == "reason" and isinstance(k.value, ast.Constant)), "")
                if strict:
                    n += 1
                    print("  %s::%s" % (f, nod.name))
                    print("      %s" % (motiv or "(FĂRĂ MOTIV SCRIS — asta e în sine un defect)")[:200])
    _linie()
    print("  TOTAL xfail(strict): %d" % n)
    print()


# ── D. ORBIREA DECLARATĂ ─────────────────────────────────────────────────────────────────────
def sectiunea_D():
    print("D. ORBIREA DECLARATĂ a instrumentelor — ce spun ELE ÎNSELE că nu văd")
    _linie()
    tipare = ("NU vede", "nu vede", "NU acopera", "NU acoperă", "punct orb", "LIMITA DECLARATA",
              "LIMITĂ DECLARATĂ", "Ce NU face, declarat", "CE NU VEDE", "Unde e oarbă",
              "orbește", "nu poate spune")
    gasite = 0
    for d in ("scripts", "core"):
        for f in sorted(os.listdir(os.path.join(RAD, d))):
            if not f.endswith(".py"):
                continue
            try:
                arb = ast.parse(io.open(os.path.join(RAD, d, f), encoding="utf-8").read())
            except SyntaxError:
                continue
            doc = ast.get_docstring(arb) or ""
            for ln in doc.split("\n"):
                if any(x in ln for x in tipare):
                    gasite += 1
                    print("  %s/%s" % (d, f))
                    print("      %s" % ln.strip()[:150])
                    break
    _linie()
    print("  INSTRUMENTE CU ORBIRE DECLARATĂ ÎN PROPRIUL DOCSTRING: %d" % gasite)
    print("  *Fiecare e o zonă despre care instrumentul spune singur că NU poate afirma nimic.*")
    print()


# ── E. RUTELE ────────────────────────────────────────────────────────────────────────────────
def sectiunea_E():
    from scripts import scan_rute_fara_proba as _sr
    from scripts import scan_scrieri_declaratii as _sd
    print("E. RUTELE CARE SCRIU ȘI N-AU PROBĂ")
    _linie()
    suita = _sr.nenumite(doar_suita=True)
    nicaieri = _sr.nenumite()
    sub, _fara = _sd.subsetul()
    print("  fără probă pe care s-o ruleze POARTA : %d" % len(suita))
    print("  fără probă NICĂIERI în depozit       : %d" % len(nicaieri))
    print("  din ele, care ating TABELE DE DECLARAȚIE: %d" % len(sub))
    print()
    print("  Cele %d fără probă în suită, pe nume:" % len(suita))
    for cale, metoda, fn in suita:
        print("      %-6s %s" % (metoda, cale))
    print()


# ── F. CHECKLISTUL DE BROWSER ────────────────────────────────────────────────────────────────
def sectiunea_F():
    print("F. CHECKLISTUL DE BROWSER — ce e și ce NU acoperă")
    _linie()
    fisiere = ["TRASEE_VERIFICARI.md", "T36_VERIFICARI.md"] + sorted(
        x for x in os.listdir(RAD) if re.match(r"LOT_\d+_VERIFICARI\.md$", x))
    total = 0
    for f in fisiere:
        p = os.path.join(RAD, f)
        if not os.path.exists(p):
            continue
        n = len(re.findall(r"(?m)^#{2,3} ", io.open(p, encoding="utf-8").read()))
        total += n
        print("  %-28s %4d secțiuni" % (f, n))
    _linie()
    print("  TOTAL: %d secțiuni de checklist de browser." % total)
    print()
    print("  CE NU ACOPERĂ, măsurat (GARZI.md, 01.09.2026):")
    print("    · 90% din ce atinge checklistul NU apare în backlog (228 din 252 de obiecte);")
    print("    · 89% din ce atinge backlogul n-are NICIO verificare de browser (200 din 224).")
    print("    · niciunul dintre fișierele astea nu e rulat de poartă — sunt liste scrise, nu probe.")
    print()


if __name__ == "__main__":
    for f in (sectiunea_A, sectiunea_B, sectiunea_C, sectiunea_D, sectiunea_E, sectiunea_F):
        try:
            f()
        except Exception as e:  # noqa: BLE001
            print("  !! %s a eșuat: %s: %s" % (f.__name__, type(e).__name__, str(e)[:120]))
            print("     *Eșecul se tipărește, nu se ascunde: o secțiune lipsă ar arăta ca una goală.*")
            print()
