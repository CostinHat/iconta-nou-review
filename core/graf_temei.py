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
import re

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


def _apeleaza(node, fisier, chei, pe_nume, alias, importate):
    """Cheile CALIFICATE ale functiilor apelate in corpul functiei (pt inchiderea tranzitiva).

    Vezi blocul R17 de la finalul fisierului: rezolvarea nu mai e pe nume simplu."""
    called = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            called |= _rezolva(n, fisier, chei, pe_nume, alias, importate)
    return called


_CACHE = {}


def construieste_graf(radacina=None):
    """MEMOIZAT pe radacina. Graful se reconstruieste identic la fiecare apel, iar dupa R17 e cu 54%
    mai mare (2180 noduri fata de 1412) - `cote_cluster` il cerea o data per cluster per functie de
    test, deci suita a trecut de bugetul portii. Cheia e radacina; obiectul se intoarce PARTAJAT,
    fiindca toti consumatorii doar citesc din el."""
    _k = str(radacina)
    if _k not in _CACHE:
        _CACHE[_k] = _construieste_graf(radacina)
    return _CACHE[_k]


def _construieste_graf(radacina=None):
    """{functie: {fisier, cote (chei COTE directe), apeleaza (functii)}} pt toate functiile din core/*.py.

    Trateaza TIPARUL DE VERSIONARE (dispecer pe la_data + registru _VARIANTE_*): un dispecer care apeleaza
    varianta INDIRECT (fn = alege_varianta(_VARIANTE_X, ...); fn(...)) e legat de variantele din registru,
    ca inchiderea tranzitiva sa nu se rupa (dispecerul depinde de ce depind variantele lui)."""
    rad = pathlib.Path(radacina) if radacina else _RAD
    functii = {}
    trees = {}
    surse = {}
    for f in sorted(rad.glob("core/*.py")):
        if f.name.startswith("test_"):
            continue
        try:
            src = f.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src)
        except SyntaxError:
            continue
        trees[f.name] = tree
        surse[f.name] = src
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # R17: cheie CALIFICATA. `setdefault` NU se foloseste: o coliziune ramasa chiar si cu
                # (fisier, nume) trebuie sa se vada, nu sa fie inghitita tacit.
                functii[cheie(f.name, node.name)] = (f.name, node)
    cunoscute = set(functii)
    _pe_nume = {}
    for _k in cunoscute:
        _pe_nume.setdefault(nume_scurt(_k), []).append(_k)
    _imp = {fn: _importuri(s) for fn, s in surse.items()}
    # registre de variante la nivel de modul: (fisier, nume_var) -> {functii referite in valoare}
    modvar = {}
    for fname, tree in trees.items():
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                refs = {cheie(fname, n.id) for n in ast.walk(node.value)
                        if isinstance(n, ast.Name) and cheie(fname, n.id) in cunoscute}
                if refs:
                    for tgt in node.targets:
                        if isinstance(tgt, ast.Name):
                            modvar[(fname, tgt.id)] = refs
    graf = {}
    for k, (fisier, node) in functii.items():
        al, imp = _imp.get(fisier, ({}, {}))
        apel = _apeleaza(node, fisier, cunoscute, _pe_nume, al, imp)
        for n in ast.walk(node):   # dispecer -> variante, prin registrul _VARIANTE_* referit in corp
            if isinstance(n, ast.Name) and (fisier, n.id) in modvar:
                apel |= modvar[(fisier, n.id)]
        graf[k] = {"fisier": fisier, "cote": _cote_directe(node), "apeleaza": apel - {k}}
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


# =================================================================================================
#  R17 (23.08.2026) — CHEIA CALIFICATA + REZOLVAREA APELURILOR PRIN IMPORTURI
#
#  Pana azi, `functii[node.name]` era un dictionar PLAT peste tot core/*.py: doua fisiere cu acelasi
#  nume de functie deveneau UNUL, iar castigatorul era decis de ordinea alfabetica. Masurat atunci:
#  761 din 2.173 de definitii (35%) disparute, `genereaza` in 53 de fisiere pastrat doar din
#  declaratii_api.py, iar 86 din cele 88 de muchii ale hartii nepazite de vreun test.
#
#  Cheia e acum "fisier.py::nume". Masurat: (fisier, nume) lasa O SINGURA coliziune in tot core/
#  (`common.py::__init__`, doua clase imbricate), deci cheia e suficienta - dar coliziunea aia ramane
#  reala si e numarata, nu ascunsa.
#
#  A doua jumatate, si cea care conteaza mai mult: un apel `salarizare.calcul_salariu(...)` isi arunca
#  modulul si se potrivea pe nume. Acum se rezolva IN ORDINEA ASTA:
#     1. apel cu atribut `alias.N(...)` -> modulul dupa care sta aliasul, din importurile fisierului;
#     2. apel simplu `N(...)`          -> definitia din ACELASI fisier, daca exista;
#     3. apel simplu `N(...)`          -> `from core.M import N` in fisierul apelant;
#     4. nerezolvat                    -> TOATE candidatii cu acel nume.
#
#  Pasul 4 e o SUPRA-aproximare deliberata. Vechea forma alegea unul singur si tacea; asta le ia pe
#  toate, deci greseste in directia ZGOMOTOASA - o muchie in plus aprinde un test, una lipsa nu.
#  Reziduul se numara: `statistici_rezolvare()`.
# =================================================================================================

_IMPORT_MOD = re.compile(r"^\s*from\s+core\s+import\s+(.+)$", re.M)
_IMPORT_MOD2 = re.compile(r"^\s*import\s+core\.(\w+)\s+as\s+(\w+)\s*$", re.M)
_IMPORT_FN = re.compile(r"^\s*from\s+core\.(\w+)\s+import\s+(.+)$", re.M)

_NEREZOLVATE = {}


def cheie(fisier, nume):
    return "%s::%s" % (fisier, nume)


def nume_scurt(k):
    return k.split("::", 1)[1] if "::" in k else k


def fisier_din(k):
    return k.split("::", 1)[0] if "::" in k else ""


def _importuri(src):
    """(alias -> fisier_modul, nume_importat -> fisier_modul) pentru importurile din `core`."""
    alias, nume = {}, {}
    for m in _IMPORT_MOD.finditer(src):
        for buc in m.group(1).split(","):
            buc = buc.strip().rstrip("\\").strip()
            if not buc:
                continue
            p = buc.split(" as ")
            mod = p[0].strip()
            al = p[-1].strip() if len(p) > 1 else mod
            if re.match(r"^\w+$", mod) and re.match(r"^\w+$", al):
                alias[al] = mod + ".py"
    for m in _IMPORT_MOD2.finditer(src):
        alias[m.group(2)] = m.group(1) + ".py"
    for m in _IMPORT_FN.finditer(src):
        mod = m.group(1) + ".py"
        for buc in m.group(2).split(","):
            buc = buc.strip().rstrip("\\").strip().strip("()")
            if not buc:
                continue
            p = buc.split(" as ")
            orig = p[0].strip()
            al = p[-1].strip() if len(p) > 1 else orig
            if re.match(r"^\w+$", orig) and re.match(r"^\w+$", al):
                nume[al] = (mod, orig)
    return alias, nume


def _rezolva(call, fisier, chei, pe_nume, alias, importate):
    """Cheile calificate catre care poate duce un apel. set() daca nu duce nicaieri cunoscut."""
    fn = call.func
    at = getattr(fn, "attr", None)
    if at is not None:
        baza = getattr(getattr(fn, "value", None), "id", None)
        mod = alias.get(baza)
        if mod and cheie(mod, at) in chei:
            return {cheie(mod, at)}
        if baza is None or mod is None:
            n = at
        else:
            return set()
    else:
        n = getattr(fn, "id", None)
    if n is None:
        return set()
    if cheie(fisier, n) in chei:
        return {cheie(fisier, n)}
    imp = importate.get(n)
    if imp and cheie(imp[0], imp[1]) in chei:
        return {cheie(imp[0], imp[1])}
    cand = pe_nume.get(n)
    if not cand:
        return set()
    if len(cand) > 1:
        _NEREZOLVATE[n] = len(cand)
    return set(cand)


def statistici_rezolvare():
    """{nume: cati candidati} pentru apelurile ramase NEREZOLVATE (supra-aproximate la pasul 4)."""
    return dict(_NEREZOLVATE)


def apeluri_din(relpath, func, radacina=None):
    """Cheile calificate ale functiilor-sursa apelate de functia `func` din fisierul `relpath`.

    Aceeasi rezolvare ca in graf: un test care cheama `salarizare.calcul_salariu` ajunge la
    `salarizare.py::calcul_salariu`, nu la orice functie din core/ care se cheama la fel."""
    rad = pathlib.Path(radacina) if radacina else _RAD
    graf = construieste_graf(radacina)
    chei = set(graf)
    pe_nume = {}
    for k in chei:
        pe_nume.setdefault(nume_scurt(k), []).append(k)
    try:
        src = (rad / relpath).read_text(encoding="utf-8")
        tree = ast.parse(src)
    except (OSError, SyntaxError):
        return set()
    alias, importate = _importuri(src)
    fisier = pathlib.Path(relpath).name
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func:
            out = set()
            for c in ast.walk(node):
                if isinstance(c, ast.Call):
                    out |= _rezolva(c, fisier, chei, pe_nume, alias, importate)
            return out
    return set()
