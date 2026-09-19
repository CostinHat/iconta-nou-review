# -*- coding: utf-8 -*-
"""INVENTARUL A CE E PROBAT ȘI CUM — derivat din cod, ca auditorul să REPRODUCĂ, nu să creadă.

Rulează în rădăcina depozitului:  ./venv/bin/python audit/deriva_cifrele.py

Nu scrie nimic în depozit. Tipărește, pe secțiuni:
  A. CLICHETELE — fiecare constantă de plafon/criteriu din suită, valoarea ei scrisă, valoarea
     RECALCULATĂ acum de instrumentul care o produce, și verdictul (coincid / NU coincid).
  B. GĂRZILE — numărul de fișiere de probă și de funcții de test, pe categorii.
  C. PROBELE DE LANȚ — fișierele din `frontend_test/`, care NU sunt culese de pytest.
  D. INSTRUMENTELE de derivare, cu ce răspund.

*O cifră pe care auditorul n-o poate recalcula nu e o măsurătoare, e o amintire.*
"""
from __future__ import annotations

import ast
import io
import os
import re
import subprocess
import sys

RAD = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(RAD) == "audit":
    RAD = os.path.dirname(RAD)
if RAD not in sys.path:
    sys.path.insert(0, RAD)


def _linie(ch="-", n=100):
    print(ch * n)


# ── A. CLICHETELE ────────────────────────────────────────────────────────────────────────────
#: (constanta, fisierul care o poarta, cum se RECALCULEAZA acum). A treia coloană e ce face
#: inventarul verificabil: fără ea, cifra din cod ar fi o afirmație despre sine însăși.
CLICHETE = [
    ("PLAFON_SUBSET_FISCAL", "core/test_rute_probate.py",
     "len(scripts.scan_scrieri_declaratii.subsetul()[0])",
     "rute care scriu în tabele de declarație, fără probă în suită. CRITERIU (egalitate), nu plafon."),
    ("PLAFON_IN_SUITA", "core/test_rute_probate.py",
     "len(scripts.scan_rute_fara_proba.nenumite(doar_suita=True))",
     "rute care scriu, fără nicio probă pe care s-o ruleze poarta."),
    ("PLAFON_NICAIERI", "core/test_rute_probate.py",
     "len(scripts.scan_rute_fara_proba.nenumite())",
     "rute care scriu, nenumite în niciun fișier de probă din depozit."),
    ("PLAFON_NECORELATE", "core/test_coduri_validator.py",
     "len(scripts.scan_coduri_validator.confrunta()[0])",
     "coduri `DUK regula` citate care nu apar în validatorul declarației lor. CRITERIU."),
]


def _recalc(cheie):
    """Recalcularea, ca APEL, nu ca șir evaluat: un `eval` pe text ar putea eșua tăcut și ar
    raporta „EROARE" acolo unde de fapt n-am scris bine expresia."""
    from scripts import scan_scrieri_declaratii as _sd
    from scripts import scan_rute_fara_proba as _sr
    from scripts import scan_coduri_validator as _sc
    return {
        "PLAFON_SUBSET_FISCAL": lambda: len(_sd.subsetul()[0]),
        "PLAFON_IN_SUITA": lambda: len(_sr.nenumite(doar_suita=True)),
        "PLAFON_NICAIERI": lambda: len(_sr.nenumite()),
        "PLAFON_NECORELATE": lambda: len(_sc.confrunta()[0]),
    }[cheie]()


def sectiunea_A():
    print("A. CLICHETELE — valoarea scrisă față de valoarea RECALCULATĂ ACUM")
    _linie()
    rele = 0
    for const, fisier, expr, ce in CLICHETE:
        t = io.open(os.path.join(RAD, fisier), encoding="utf-8").read()
        m = re.search(r"^%s\s*=\s*(\d+)" % re.escape(const), t, re.M)
        scris = int(m.group(1)) if m else None
        try:
            acum = _recalc(const)
        except Exception as e:  # noqa: BLE001
            acum = "EROARE: %s" % str(e)[:60]
        ok = (scris == acum)
        rele += 0 if ok else 1
        print("  %-24s scris=%-6s acum=%-6s  %s" % (const, scris, acum, "OK" if ok else "!! DIVERG"))
        print("      %s" % ce)
        print("      recalculează: %s" % expr)
        # [D6, 18.09.2026] ANTI-VACUUM pt NECORELATE: `acum=0` poate însemna „toate citările se
        # corelează" SAU „niciun jar validator instalat, deci nu s-a putut confrunta nimic". Fără
        # nota asta, un 0 vid s-ar citi ca un 0 curat — exact defectul pe care instrumentul îl caută.
        if const == "PLAFON_NECORELATE" and acum == 0:
            try:
                from scripts import scan_coduri_validator as _sc
                _nec, _fara, _disc = _sc.confrunta()
                if _fara and not _disc:
                    print("      !! VID: NECORELATE=0 fiindcă %d citări au mers în `fara_validator` "
                          "(niciun jar instalat), NU fiindcă se corelează. Cifra nu e o măsurătoare "
                          "cât timp DUKIntegrator lipsește din pachet." % len(_fara))
            except Exception as _e:  # noqa: BLE001
                print("      (anti-vacuum indisponibil: %s)" % str(_e)[:50])
    _linie()
    print("  clichete care NU coincid: %d" % rele)
    print()


# ── B. GĂRZILE ───────────────────────────────────────────────────────────────────────────────
def sectiunea_B():
    print("B. GĂRZILE — fișiere de probă și funcții de test, numărate din cod")
    _linie()
    fisiere = sorted(f for f in os.listdir(os.path.join(RAD, "core")) if f.startswith("test_"))
    total_f = 0
    for f in fisiere:
        try:
            arb = ast.parse(io.open(os.path.join(RAD, "core", f), encoding="utf-8").read())
        except SyntaxError:
            continue
        total_f += sum(1 for n in ast.walk(arb)
                       if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"))
    print("  fișiere de probă în `core/`      : %d" % len(fisiere))
    print("  funcții `test_*` în ele          : %d" % total_f)
    print("  (numărul COLECTAT de pytest poate diferi: parametrizările produc mai multe cazuri)")
    print()


# ── C. PROBELE DE LANȚ ───────────────────────────────────────────────────────────────────────
def sectiunea_C():
    print("C. PROBELE DE LANȚ — `frontend_test/`, care NU sunt culese de pytest")
    _linie()
    d = os.path.join(RAD, "frontend_test")
    probe = sorted(f for f in os.listdir(d) if f.startswith("proba_") and f.endswith(".py"))
    for p in probe:
        prima = ""
        for ln in io.open(os.path.join(d, p), encoding="utf-8"):
            ln = ln.strip().strip('"')
            if ln and not ln.startswith("#"):
                prima = ln[:88]
                break
        print("  %-42s %s" % (p, prima))
    print()
    print("  TOTAL: %d probe de lanț." % len(probe))
    print("  ATENȚIE, și e limita lor: `frontend_test/` NU e cules de pytest, deci NICIUNA nu rulează")
    print("  la poartă. Ele se rulează de mână, pe o instanță vie. Ce e păzit la fiecare commit e")
    print("  numai ce stă în `core/test_*.py`.")
    print()


# ── D. INSTRUMENTELE ─────────────────────────────────────────────────────────────────────────
def sectiunea_D():
    print("D. INSTRUMENTELE de derivare — ce răspunde fiecare")
    _linie()
    d = os.path.join(RAD, "scripts")
    for f in sorted(os.listdir(d)):
        if not (f.startswith("scan_") or f in ("raport_b.py", "perimetru.py", "poarta_scurta.py")):
            continue
        prima = ""
        try:
            arb = ast.parse(io.open(os.path.join(d, f), encoding="utf-8").read())
            doc = ast.get_docstring(arb) or ""
            prima = doc.strip().split("\n")[0][:92]
        except Exception:  # noqa: BLE001
            pass
        print("  %-34s %s" % (f, prima))
    print()


def sectiunea_git():
    print("COMMITUL PE CARE S-A DERIVAT TOT CE E MAI SUS")
    _linie()
    for cmd in (["git", "rev-parse", "HEAD"], ["git", "log", "-1", "--format=%ci %s"],
                ["git", "status", "--porcelain"]):
        r = subprocess.run(cmd, cwd=RAD, capture_output=True, text=True)
        out = (r.stdout or "").strip()
        print("  %-24s %s" % (" ".join(cmd[1:3]), out if out else "(arbore curat)"))
    print()


if __name__ == "__main__":
    sectiunea_git()
    sectiunea_A()
    sectiunea_B()
    sectiunea_C()
    sectiunea_D()
