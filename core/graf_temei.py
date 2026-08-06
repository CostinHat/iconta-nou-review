# -*- coding: utf-8 -*-
"""core/graf_temei.py - GRAFUL DE DEPENDENTE fiscale, EXTRAS DIN COD (Modelul de temei 01.08, pct.3).

Scop: cand o lege modifica o valoare, sa ai lista EXACTA a locurilor de actualizat - fara sa iei
aplicatia la mana. Acopera modificarea PRIN EFECT: se schimba salariul minim, nimic nu citeaza HG-ul
nou, dar salariul minim intra in deducere, facilitate, plafon 12 sm, suprataxare part-time, prag tineri.
Intrebarea nu e "cine citeaza actul", ci "cine FOLOSESTE valoarea".

Mecanism: analizor AST care gaseste apelurile cota("x") in corpul fiecarei functii + inchidere
tranzitiva pe apelurile intre functii. Interogare pe graf, NU lista intretinuta manual (o lista de mana
devine stale la prima refactorizare - tiparul pentru care s-a despartit ISTORIC.md si s-a sters DE_FACUT).
Dependenta sta pe FUNCTIE, nu pe intrarea din COTE.

LIMITE DECLARATE:
- o valoare HARDCODATA care ocoleste cota() nu apare in graf -> gardul de literale fiscale (GRI, azi 0)
  e CONDITIA ca graful sa fie complet.
- rezolvare pe NUME de functie (nu pe modul): doua functii cu acelasi nume in module diferite se
  confunda - fals-pozitiv posibil in inchiderea tranzitiva. Acceptat: graful supra-raporteaza (mai
  degraba un loc in plus de verificat decat unul lipsa).
- o lege care creeaza obligatie NOUA (IMCA, e-Transport) nu e acoperita - nimic nu poate cita un act
  inexistent; e produs, nu intretinere.

  python3 -m core.graf_temei salariu_minim   # ce depinde de salariul minim
"""
import ast
import pathlib

_RAD = pathlib.Path(__file__).resolve().parent.parent


def _cote_directe(node):
    """Cheile COTE cerute DIRECT in corpul functiei: cota("x") / c.cota("x") / common.cota("x")."""
    keys = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            fn = n.func
            nume = getattr(fn, "attr", None) or getattr(fn, "id", None)
            if nume == "cota" and n.args:
                a0 = n.args[0]
                if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
                    keys.add(a0.value)
            elif nume == "salariu_minim_luna":
                # [#12] accesor period-aware al salariului minim (art.77 alin.3) = dependenta DIRECTA
                keys.add("salariu_minim")
    return keys


def _apeleaza(node, cunoscute):
    """Functiile din codebase apelate in corpul functiei (pt inchiderea tranzitiva)."""
    called = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            fn = n.func
            nume = getattr(fn, "attr", None) or getattr(fn, "id", None)
            if nume in cunoscute:
                called.add(nume)
    return called


def construieste_graf(radacina=None):
    """{functie: {fisier, cote (chei COTE directe), apeleaza (functii)}} pt toate functiile din core/*.py.

    Trateaza TIPARUL DE VERSIONARE (dispecer pe la_data + registru _VARIANTE_*): un dispecer care apeleaza
    varianta INDIRECT (fn = alege_varianta(_VARIANTE_X, ...); fn(...)) e legat de variantele din registru,
    ca inchiderea tranzitiva sa nu se rupa (dispecerul depinde de ce depind variantele lui)."""
    rad = pathlib.Path(radacina) if radacina else _RAD
    functii = {}
    trees = {}
    for f in sorted(rad.glob("core/*.py")):
        if f.name.startswith("test_"):
            continue
        try:
            tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        trees[f.name] = tree
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functii[node.name] = (f.name, node)
    cunoscute = set(functii)
    # registre de variante la nivel de modul: (fisier, nume_var) -> {functii referite in valoare}
    modvar = {}
    for fname, tree in trees.items():
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                refs = {n.id for n in ast.walk(node.value) if isinstance(n, ast.Name) and n.id in cunoscute}
                if refs:
                    for tgt in node.targets:
                        if isinstance(tgt, ast.Name):
                            modvar[(fname, tgt.id)] = refs
    graf = {}
    for nume, (fisier, node) in functii.items():
        apel = _apeleaza(node, cunoscute)
        for n in ast.walk(node):   # dispecer -> variante, prin registrul _VARIANTE_* referit in corp
            if isinstance(n, ast.Name) and (fisier, n.id) in modvar:
                apel |= modvar[(fisier, n.id)]
        graf[nume] = {"fisier": fisier, "cote": _cote_directe(node), "apeleaza": apel - {nume}}
    return graf


def depinde_de(cheie_cota, radacina=None):
    """Functiile care depind de o cheie COTE - DIRECT (cota("cheie") in corp) sau TRANSITIV (apeleaza o
    functie care depinde). Intoarce {nume_functie: "direct" | "prin <functie>"}."""
    graf = construieste_graf(radacina)
    rez = {n: "direct" for n, d in graf.items() if cheie_cota in d["cote"]}
    schimbat = True
    while schimbat:
        schimbat = False
        for n, d in graf.items():
            if n in rez:
                continue
            for apelat in d["apeleaza"]:
                if apelat in rez:
                    rez[n] = "prin %s" % apelat
                    schimbat = True
                    break
    return rez


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print('uz: python3 -m core.graf_temei <cheie_cota>   (ex: salariu_minim, tva_standard, cas)')
        sys.exit(2)
    cheie = sys.argv[1]
    dep = depinde_de(cheie)
    if not dep:
        print("Nicio functie nu depinde de %r (verifica cheia sau daca valoarea e ocolita prin literal)." % cheie)
        sys.exit(0)
    graf = construieste_graf()
    print("%d functii depind de %r:" % (len(dep), cheie))
    for nume in sorted(dep, key=lambda n: (dep[n] != "direct", n)):
        print("  %-32s %-12s [%s]" % (nume, dep[nume], graf.get(nume, {}).get("fisier", "?")))
