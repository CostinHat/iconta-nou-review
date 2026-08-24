# -*- coding: utf-8 -*-
"""INSTRUMENT — module cu funcții publice și ZERO importatori în afara testelor.

  core/scan_module_nelegate.py

Cerut de Costin 24.08.2026: *„câte alte module de verificare există și nu sunt apelate? E măsurabil
mecanic — un modul cu funcții publice și zero apelanți în afara testelor. E chiar tiparul «nu s-a
stricat, n-a fost niciodată legat»."*

**Măsoară prin AST, nu prin grep, și diferența e chiar rezultatul.** `grep salarii_contare` găsește o
potrivire în `core/salarizare.py:296` — dar e un **comentariu**. Proza descrie o legătură care nu
există. Un scan pe text ar fi raportat modulul ca legat.

MODURILE DE EȘEC, scrise ÎNAINTE de prima măsurătoare (interdicția 76 — calibrare pe propriul mod de
eșec, nu pe cazul fericit):

  E1. **import dinamic prin șir** (`importlib.import_module`, `__import__`) — invizibil pentru AST.
      Se raportează separat, ca perimetru necunoscut, nu se înghite.
  E2. **punct de intrare** (cron / CLI / systemd) — n-are importatori PRIN CONSTRUCȚIE, dar e viu.
      Detectat prin `if __name__ == "__main__"`. **Sub-detectează:** un script fără gardă `__main__`,
      care execută la nivel de modul, cade greșit în lista „nelegate" (instanța: `verificator_conformitate.py`).
  E3. **încărcat de altceva decât un import Python** — ASGI/uvicorn, hook de shell, rută prin șir.
      Instanța cunoscută: `main.py`, pe care uvicorn îl încarcă fără ca cineva să-l importe.
  E4. **modul importat, dar cu funcții publice pe care nu le cheamă nimeni** — NEACOPERIT. Sonda e la
      nivel de MODUL, nu de funcție. Un modul importat pentru o funcție, cu alte trei moarte, trece.
  E5. module fără funcții publice, și `__init__.py` — n-au ce lega, se sar.
"""
import ast
import io
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZONE = ("core", "scripts", "frontend_test", "date_test", ".")
SARITE = ("__pycache__", "venv", ".git", "node_modules", "_arhiva_patchuri", ".lant_tmp")


def _fisiere(rad):
    vazut = set()
    for z in ZONE:
        baza = os.path.join(rad, z)
        if not os.path.isdir(baza):
            continue
        for r, d, fs in os.walk(baza):
            d[:] = [x for x in d if x not in SARITE]
            for f in sorted(fs):
                if f.endswith(".py"):
                    c = os.path.abspath(os.path.join(r, f))
                    if c not in vazut:
                        vazut.add(c)
                        yield c


def e_test(cale):
    b = os.path.basename(cale)
    return b.startswith("test_") or b.endswith("_test.py") or "conftest" in b


def _publice(arb):
    """Funcții/clase publice la NIVEL DE MODUL. Cele imbricate nu sunt suprafață publică."""
    return [n.name for n in arb.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and not n.name.startswith("_")]


def _importate(arb):
    """Numele importate, ORIUNDE în fișier — inclusiv lazy, din corpul unei funcții (regula aici)."""
    out = set()
    for n in ast.walk(arb):
        if isinstance(n, ast.Import):
            for a in n.names:
                out.add(a.name)
                out.add(a.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom):
            if n.module:
                out.add(n.module)
                out.add(n.module.split(".")[0])
            for a in n.names:
                out.add(a.name)
    return out


def _dinamic(arb):
    for n in ast.walk(arb):
        if isinstance(n, ast.Call):
            nume = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
            if nume in ("import_module", "__import__", "load_module", "spec_from_file_location"):
                return True
    return False


def masoara(rad=None):
    """-> {nelegate, doar_test, intrari, dinamice, importatori}. Sursă unică; gardul importă de aici."""
    rad = rad or RAD
    mod, imp_ne_test, imp_test, dinamice = {}, {}, {}, []

    fisiere = list(_fisiere(rad))
    for cale in fisiere:
        try:
            src = io.open(cale, encoding="utf-8").read()
            arb = ast.parse(src, filename=cale)
        except (SyntaxError, UnicodeDecodeError):
            continue
        b = os.path.basename(cale)[:-3]
        if b != "__init__" and not e_test(cale):
            mod[b] = (cale, _publice(arb), "__main__" in src and "if __name__" in src)
        if _dinamic(arb):
            dinamice.append(os.path.relpath(cale, rad))
        for nume in _importate(arb):
            tinta = imp_test if e_test(cale) else imp_ne_test
            tinta.setdefault(nume.split(".")[-1], set()).add(os.path.relpath(cale, rad))

    nelegate, doar_test, intrari = [], [], []
    for nume, (cale, publice, e_intrare) in sorted(mod.items()):
        if not publice:
            continue                                                    # E5
        alti = {f for f in imp_ne_test.get(nume, set())
                if os.path.abspath(os.path.join(rad, f)) != cale}
        if alti:
            continue
        rel = os.path.relpath(cale, rad).replace("\\", "/")
        rand = (rel, len(publice), len(imp_test.get(nume, set())))
        if e_intrare:
            intrari.append(rand)                                        # E2
        elif imp_test.get(nume):
            doar_test.append(rand)
        else:
            nelegate.append(rand)

    return {"nelegate": nelegate, "doar_test": doar_test, "intrari": intrari,
            "dinamice": dinamice, "importatori": imp_ne_test, "fisiere": len(fisiere)}


def doar_core(rez):
    """Cele care contează pentru clasa lui R33: module de PRODUCȚIE din `core/`, ținute verzi de teste
    și chemate de nimeni. Restul listelor sunt unelte, probe și puncte de intrare."""
    return sorted(r for r in rez["doar_test"] + rez["nelegate"] if r[0].startswith("core/"))


if __name__ == "__main__":
    r = masoara()
    print("fisiere .py: %d" % r["fisiere"])
    for cheie in ("doar_test", "nelegate", "intrari"):
        print("\n== %s (%d) ==" % (cheie, len(r[cheie])))
        for rel, np, nt in r[cheie]:
            print("   %-46s publice=%-3d teste=%d" % (rel, np, nt))
    print("\n== CORE, clasa R33 (%d) ==" % len(doar_core(r)))
    for rel, np, nt in doar_core(r):
        print("   %-46s publice=%-3d teste=%d" % (rel, np, nt))
