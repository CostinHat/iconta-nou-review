# -*- coding: utf-8 -*-
"""SCANNER de constante fiscale NESURSATE din codul de PRODUCTIE (20.08.2026).

DE CE EXISTA. Inventarul de pe 31.07 a masurat TESTE care asertaza o constanta: 114, din care 29 cu
temei si 85 fara. Era orb prin constructie la constantele care traiesc DOAR in productie - `25` din
`_ZIUA.get(tip, 25)` (scadente.py) nu apare in niciun test; testele asertaza date deja calculate.
Deci dimensiunea clasei era necunoscuta, iar sursarea unei bucati insemna munca pe un fragment
dintr-un intreg nemasurat.

CE DISTINGE o constanta fiscala de un numar oarecare. NU felul in care e FOLOSITA - prima incercare a
cautat aritmetica + comparatii: a gasit 127, aproape integral zgomot de format (len(cnp)==13, % 11,
1<=zi<=31, calculul Pastelui) si a RATAT tinta cunoscuta, fiindca un default la .get() nu e nici
aritmetica nici comparatie. Ci felul in care LOCUIESTE:
    H1  constanta la nivel de modul (inclusiv in dict/tuple/set literal)
    H2  default la lookup: x.get(k, N) / getattr(o, a, N)
    H3  default de parametru de functie
    H4  Decimal("N") literal
    H5  atribuit/comparat cu un nume fiscal (prag, plafon, cota, salariu, venit, termen...)

CLASIFICAREA vine de la STRAMOSUL SINTACTIC, nu de la ramura care a gasit literalul - a doua incercare
a picat exact aici: `Decimal("4050")` avea `Temei(...)` pe acelasi rand si a ajuns totusi in "nesursat".
    A  SURSAT      un stramos poarta `Temei(...)`  -> cazul BUN, se exclude
    B  NOMENCLATOR cod/pondere/lungime din XSD sau algoritm (_CNP_W, _JUD, TIPURI_OP, LIMITE_TEXT).
                   Are si el sursa, dar ALTA (XSD/validator) si alta cadenta de revizuire.
    C  NESURSAT    TINTA
    D  precizie    Decimal("0.01") de cuantizare, chr(), stari interne. Numarata, nu aruncata tacut.

ZGOMOTUL si CITARILE se exclud dupa forma, INAINTE de culegere: operanzii lui len(), divizorii de
modulo, componentele de data, si argumentele lui `Temei(...)`/`date(...)` - care sunt citari, nu valori.

LIMITA, scrisa fiindca tacerea unui scan se citeste ca absenta: granita B/C e euristica pe NUME (NOM).
Un nomenclator botezat neinspirat ajunge in C - fals pozitiv, il vezi. O valoare fiscala botezata
`_TIP_...` ar ajunge in B - fals negativ, NU o vezi. De-aia gardul care foloseste scannerul poarta o
calibrare in TREI directii, nu una: o singura tinta lasa scanul sa treaca pe gol in celelalte.
"""

import ast
import json
import os
import re
from collections import Counter

RAD = "/home/costin/iconta_nou/core"
STRUCT = {0, 1, -1, 2, 100}
FIS = re.compile(r"^(d\d{3}[a-z_]*|salarizare|scadente|stat_plata_api|salariati_api|cote\w*|"
                 r"tva_\w+|bilant\w*|impozit\w*|contributii\w*|control_fiscal\w*|common)\.py$")
NF = re.compile(r"prag|plafon|cota|cote|salariu|salar|venit|impozit|contrib|cas\b|cass\b|cam\b|"
                r"deduc|scutir|termen|scadent|zi_dep|micro|profit|dividend|tichet|norma|baza|minim|maxim", re.I)
NOM = re.compile(r"_W$|_WEIGHT|_KEY$|CNP|CUI|JUD|SIRUTA|TIPURI|TIP_|_TIP|FORMA|LIMITE_TEXT|LIMITE|"
                 r"TAXCODE|COD_|CODURI|_REL_|_PER_|CAEN|VALUT|TARA|_MAP$|SCHEMA|XSD|NOMENCL|SARB|"
                 r"HEADER|_STR_|_OPT$|PERIODIC|_CAT_|CATEG", re.I)


def scan(f, src):
    L = src.splitlines()
    try:
        arb = ast.parse(src)
    except SyntaxError:
        return []
    par = {}
    for n in ast.walk(arb):
        for c in ast.iter_child_nodes(n):
            par[id(c)] = n
    # cache: subarborele lui X contine un Temei?
    tem = {}

    def are_temei(n):
        if id(n) in tem:
            return tem[id(n)]
        r = any(isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == "Temei"
                or isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and x.func.attr == "Temei"
                or isinstance(x, ast.Name) and x.id in ("Temei", "_Tm")
                for x in ast.walk(n))
        tem[id(n)] = r
        return r

    ex, brut = set(), []

    def lit(n):
        return (isinstance(n, ast.Constant) and isinstance(n.value, (int, float))
                and not isinstance(n.value, bool) and n.value not in STRUCT)

    def txt(n):
        ln = getattr(n, "lineno", 0)
        return ln, (L[ln - 1].strip()[:100] if 0 < ln <= len(L) else "")

    # ── pasul 1: exclude zgomotul de format, si CITARILE ──
    for n in ast.walk(arb):
        if isinstance(n, ast.Call):
            fn = n.func
            if isinstance(fn, ast.Name) and fn.id == "len":
                ex.update(id(p) for p in ast.walk(n))
            if isinstance(fn, ast.Name) and fn.id in ("Temei", "_Tm", "date", "datetime"):
                ex.update(id(p) for p in ast.walk(n))          # argumentele citarii nu sunt valori
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod) and lit(n.right):
            ex.add(id(n.right))
        if isinstance(n, ast.Compare):
            nm = ast.unparse(n.left)[:30].strip()
            if re.fullmatch(r"_?(d|zi|mo|luna|y|an|yy|aa|mm|dd)\d?", nm):
                ex.update(id(c) for c in n.comparators if lit(c))

    # ── pasul 2: culege, cu casa si contextul ──
    def cul(n, casa, ctx):
        if lit(n) and id(n) not in ex:
            brut.append((n, casa, ctx))

    niv = {}

    def marc(n, d):
        niv[id(n)] = d
        for c in ast.iter_child_nodes(n):
            marc(c, d + (1 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) else 0))
    marc(arb, 0)

    for n in ast.walk(arb):
        if isinstance(n, ast.Call):
            fn = n.func
            if isinstance(fn, ast.Attribute) and fn.attr == "get" and len(n.args) == 2:
                cul(n.args[1], "H2", "default la %s.get()" % ast.unparse(fn.value)[:34])
            elif isinstance(fn, ast.Name) and fn.id == "getattr" and len(n.args) == 3:
                cul(n.args[2], "H2", "default la getattr()")
            elif isinstance(fn, ast.Name) and fn.id == "Decimal" and n.args:
                a = n.args[0]
                if isinstance(a, ast.Constant) and re.fullmatch(r"-?\d+(\.\d+)?", str(a.value)) \
                   and float(a.value) not in {0, 1, 2, 100} and id(a) not in ex:
                    brut.append((a, "H4", "Decimal literal"))
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in n.args.defaults + [x for x in n.args.kw_defaults if x]:
                cul(d, "H3", "default de parametru in %s()" % n.name)
        elif isinstance(n, ast.Assign):
            tg = ", ".join(ast.unparse(t) for t in n.targets)[:44]
            if niv.get(id(n), 1) == 0:
                for p in ast.walk(n.value):
                    cul(p, "H1", "constanta de modul `%s`" % tg)
            elif NF.search(tg):
                for p in ast.walk(n.value):
                    cul(p, "H5", "atribuit lui `%s`" % tg)
        elif isinstance(n, ast.Compare):
            nm = ast.unparse(n.left)[:30].strip()
            if NF.search(nm) and not re.fullmatch(r"_?(d|zi|mo|luna|y|an|yy|aa|mm|dd)\d?", nm):
                for c in n.comparators:
                    cul(c, "H5", "comparat cu `%s`" % nm)

    # ── pasul 3: CLASIFICA uniform, urcand pe parinti ──
    out = []
    for n, casa, ctx in brut:
        cls, a = "C", n
        while id(a) in par:
            a = par[id(a)]
            if isinstance(a, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef)):
                break
            if are_temei(a):
                cls = "A"
                break
        if cls == "C" and NOM.search(ctx):
            cls = "B"
        ln, t = txt(n)
        val = str(n.value)
        out.append({"f": f, "l": ln, "v": val, "casa": casa, "cls": cls, "ctx": ctx[:44], "txt": t})
    return out



# ── clasa D: precizie/format rezidual. Separata DUPA clasificare, ca sa ramana numarabila. ──
def _este_precizie(h):
    t, v = h["txt"], h["v"]
    if v in ("0.01", "0.001", "0.005", "0.5") and (
            "quantize" in t or re.search(r"^_?[A-Z0-9_]{1,6}\s*=\s*Decimal", t)):
        return True
    if "chr(" in t:
        return True
    return bool(re.search(r"_RANG_STARE|_ORDINE|_PRIORIT", h["ctx"]))


def inventar(rad=RAD):
    """Toti literalii clasificati din modulele fiscale. Fara efecte in afara de citit."""
    hits = []
    for f in sorted(os.listdir(rad)):
        if not f.endswith(".py") or f.startswith("test_") or not FIS.match(f):
            continue
        with open(os.path.join(rad, f), encoding="utf-8", errors="replace") as fh:
            hits += scan(f, fh.read())
    vaz, U = set(), []
    for h in hits:
        k = (h["f"], h["l"], h["v"])
        if k in vaz:
            continue
        vaz.add(k)
        if h["cls"] == "C" and _este_precizie(h):
            h["cls"] = "D"
        U.append(h)
    return U


def nesursate(rad=RAD):
    """Doar clasa C - constantele fiscale fara temei atasat."""
    return [h for h in inventar(rad) if h["cls"] == "C"]


if __name__ == "__main__":
    from collections import Counter
    U = inventar()
    for c in "ABCD":
        print("%s %4d" % (c, sum(1 for h in U if h["cls"] == c)))
    print("")
    print("BASELINE = {")
    for f, n in sorted(Counter(h["f"] for h in nesursate()).items()):
        print('    "%s": %d,' % (f, n))
    print("}")
