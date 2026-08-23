# -*- coding: utf-8 -*-
"""FAZA 4, pasul 5: mutatia care probeaza garda e REPRODUCTIBILA azi?

O garda se dovedeste printr-un RED-proof: strici codul, garda se aprinde. Intrebarea planului e daca
mutatia aia se mai poate face AZI - adica daca dovada mai exista, sau a ramas o afirmatie din trecut.

Nu se pot rula 2.563 de mutatii. Dar exista o forma in care mutatia e reproductibila PRIN CONSTRUCTIE:
garda are un TOVARAS in suita - un al doilea test care construieste intrarea stricata si arata ca
mecanismul o prinde. Aia nu e o afirmatie despre trecut, e o mutatie care ruleaza la fiecare poarta.

SE MASOARA PE DOUA DEFINITII, si se CONFRUNTA (lectia zilei: o singura definitie e o opinie):
  (a) CONVENTIE  - tovarasul se numeste `..._prinde_...` / `..._prind_...` / `..._detecteaza_...`
  (b) STRUCTURAL - un test din acelasi fisier care cheama ACELASI ajutor ca garda, dar pe o intrare
      construita LOCAL (literal/fixtura in corpul lui), nu pe corpusul real.

DOMENIU: core/test_*.py SI test_*.py din radacina - cele 44 de fisiere pe care masuratorile de azi
le-au ratat pana la intrebarea 2 a lui Costin.

SONDA DE CITIRE.
"""
import ast
import collections
import pathlib
import re

RAD = pathlib.Path("/home/costin/iconta_nou")
CONV = re.compile(r"_(prinde|prind|detecteaza|detecteaza|semnaleaza|respinge)_", re.I)


def fisiere():
    return sorted(RAD.glob("core/test_*.py")) + sorted(RAD.glob("test_*.py"))


def teste(arb):
    return [n for n in ast.walk(arb)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test_")]


def apeluri(fn):
    """Numele functiilor chemate in corpul testului."""
    out = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            nume = getattr(n.func, "attr", None) or getattr(n.func, "id", None)
            if nume:
                out.add(nume)
    return out


def are_intrare_locala(fn):
    """Testul isi CONSTRUIESTE intrarea: un literal de sir/dict/lista atribuit in corp, sau un
    argument literal dat unui apel. Opusul: citeste corpusul real."""
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign) and isinstance(n.value, (ast.Constant, ast.Dict, ast.List)):
            if isinstance(n.value, ast.Constant) and not isinstance(n.value.value, str):
                continue
            return True
        if isinstance(n, ast.Call):
            for a in list(n.args) + [k.value for k in n.keywords]:
                if isinstance(a, ast.Constant) and isinstance(a.value, str) and len(a.value) > 20:
                    return True
    return False


def main():
    per_fisier = {}
    tot = 0
    for p in fisiere():
        try:
            arb = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, OSError):
            continue
        t = teste(arb)
        tot += len(t)
        per_fisier[p.name] = t

    print("=" * 100)
    print("DOMENIU: %d fisiere, %d garzi (include cele 44 din radacina)" % (len(per_fisier), tot))
    print("=" * 100)

    # (a) conventie
    conv = {f: [x for x in t if CONV.search(x.name)] for f, t in per_fisier.items()}
    n_conv = sum(len(v) for v in conv.values())
    fis_conv = [f for f, v in conv.items() if v]

    # (b) structural: test care cheama un ajutor chemat si de alt test din acelasi fisier,
    #     dar isi construieste intrarea local
    n_struct = 0
    struct_fis = set()
    exemple = []
    for f, t in per_fisier.items():
        ap = {x.name: apeluri(x) for x in t}
        for x in t:
            if not are_intrare_locala(x):
                continue
            comune = set()
            for y in t:
                if y is x:
                    continue
                comune |= (ap[x.name] & ap[y.name])
            comune = {c for c in comune if not c.startswith(("assert", "len", "str", "int", "print",
                                                            "sorted", "set", "list", "dict", "open"))}
            if comune:
                n_struct += 1
                struct_fis.add(f)
                if len(exemple) < 8:
                    exemple.append((f, x.name, sorted(comune)[:2]))

    print()
    print("(a) DUPA CONVENTIE DE NUME (`_prinde_`, `_detecteaza_`, `_respinge_`)")
    print("    garzi-tovaras: %d, in %d fisiere  (%.1f%% din garzi)"
          % (n_conv, len(fis_conv), 100.0 * n_conv / max(tot, 1)))
    print()
    print("(b) STRUCTURAL (intrare construita local + ajutor comun cu alt test din fisier)")
    print("    garzi-tovaras: %d, in %d fisiere  (%.1f%%)"
          % (n_struct, len(struct_fis), 100.0 * n_struct / max(tot, 1)))
    print()
    print("CONFRUNTAREA: conventia gaseste %d, structura %d. Raport %.1fx."
          % (n_conv, n_struct, (n_struct / n_conv) if n_conv else 0))
    print("    Conventia e STRICTA - cere ca cineva sa fi numit testul asa.")
    print("    Structura e LARGA - prinde si tovarasii nenumiti, dar si teste unitare obisnuite")
    print("    care se intampla sa imparta un ajutor. Adevarul e intre, si NU se poate strange")
    print("    fara sa citesti - deci cifra care se raporteaza e cea STRICTA, cu limita scrisa.")

    print()
    print("CALIBRARE pe cazuri cunoscute (tovarasi reali, numiti):")
    for f, nume in (("test_agenda.py", "test_secventa_prinde_inversiune"),
                    ("test_agenda.py", "test_fisiere_coloana_completa_prinde_gol"),
                    ("test_agenda.py", "test_garzi_si_duplicat_prind_defectul")):
        gasit = any(x.name == nume for x in conv.get(f, []))
        print("    %-52s %s" % (nume, "gasit" if gasit else "RATAT"))

    print()
    print("FISIERELE CU CEI MAI MULTI TOVARASI (conventie):")
    c = collections.Counter({f: len(v) for f, v in conv.items() if v})
    for f, k in c.most_common(8):
        print("    %-46s %d" % (f, k))

    print()
    print("GARZI FARA NICIUN TOVARAS IN FISIER: %d fisiere din %d"
          % (len([f for f, v in conv.items() if not v]), len(per_fisier)))


main()
