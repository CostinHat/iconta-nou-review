# -*- coding: utf-8 -*-
"""Care gărzi asertează pe TEXT în loc de STRUCTURĂ — pe ASERȚIUNE, nu pe fișier.

Regula, dată de Costin 24.08.2026: *o gardă asertează pe structură, nu pe text.* Nu „cheia apare
undeva în răspuns", ci „câmpul are valoarea asta".

DE CE PE ASERȚIUNE ȘI PE FIȘIER, nu global (Costin, 24.08): un plafon global pe **fișiere** nu
constrânge nimic înăuntru — un fișier nou cu 40 de aserțiuni pe text ar urca numărul cu **unu**.
Clichetul e deci un **dicționar fișier → număr**, iar un fișier nou pornește de la **zero**.

CELE TREI SUB-CATEGORII, numărate separat, după CE STĂ ÎN DREAPTA lui `in`:

  1. **sursa** — dreapta vine dintr-o citire de fișier (`open(...).read()`, `read_text()`). Gardul
     caută un șir în codul pe care îl păzește, deci nu poate deosebi *„e implementat"* de
     *„e descris"*.
  2. **randare** — dreapta e HTML sau textul unui răspuns HTTP (`.text`, `.content`). Un `<div>`
     dintr-un comentariu HTML trece la fel de bine ca unul randat.
  3. **reprezentare** — dreapta e `str(...)`, `repr(...)` sau `json.dumps(...)` peste o structură.
     **Cea mai insidioasă**: *arată ca apartenență la o cheie și e sub-șir pe reprezentare.*
     `"total" in str(d)` trece și când `d = {"subtotal_vechi": 1}`.

Și două stări care NU sunt în clasă, dar se numără ca să se vadă ce nu se vede:
  - **container** — dreapta e dovedit un set/listă/dict/tuplu (literal, comprehensiune, sau o funcție
    locală care întoarce așa ceva). Aici `in` **chiar e** apartenență. E forma corectă.
  - **nedeterminat** — nu s-a putut rezolva ce e în dreapta. NU se raportează ca trecut: absența unei
    verificări nu e o verificare.

MODUL DE EȘEC AL CONTAINERULUI, declarat. Un `in` pe container e sigur doar cât timp dreapta rămâne
container. `"nr_curent" in chei` se transformă tăcut în sub-șir dacă `chei` devine vreodată un `str`
— și **arată identic**. De aceea forma recomandată nu e `in`, ci operatorul de mulțime:
`chei >= {"nr_curent"}` **crapă** pe un șir, în loc să treacă. Scanul nu poate cere asta, dar o
numește aici, iar gărzile reparate o folosesc.
"""
import ast
import io
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CLASA = ("sursa", "randare", "reprezentare")

_CITIRE = ("read", "read_text", "open")
_REPREZENTARE = ("str", "repr", "dumps")
_RANDARE_ATTR = ("text", "content", "body")
_RANDARE_NUME = ("html", "pagina", "ecran", "randat", "dom", "markup", "page")


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


def _nume_apel(nod):
    f = nod.func
    return getattr(f, "attr", None) or getattr(f, "id", None)


def _clasifica_valoare(v, functii, adancime=0):
    """Ce fel de lucru e expresia `v`? Recursiv o singură dată prin funcțiile locale."""
    if isinstance(v, (ast.Set, ast.List, ast.Dict, ast.Tuple,
                      ast.SetComp, ast.ListComp, ast.DictComp)):
        return "container"
    if isinstance(v, ast.Call):
        n = _nume_apel(v)
        if n in _REPREZENTARE:
            return "reprezentare"
        if n in _CITIRE:
            return "sursa"
        if n in ("set", "list", "dict", "tuple", "keys", "values", "loads"):
            return "container"
        if n == "join" and v.args:
            # `"".join(<comprehensiune>)` — decide elementul, nu containerul: rezultatul e un ȘIR.
            a = v.args[0]
            if isinstance(a, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
                c = _clasifica_valoare(a.elt, functii, adancime + 1)
                return c if c in ("sursa", "randare") else "reprezentare"
            return "reprezentare"
        if n in functii and adancime < 3:
            return _clasifica_functie(functii[n], functii, adancime + 1)
        return "nedeterminat"
    if isinstance(v, ast.BoolOp):          # `x or ""`, `a and b`
        for val in v.values:
            c = _clasifica_valoare(val, functii, adancime + 1)
            if c != "nedeterminat":
                return c
        return "nedeterminat"
    if isinstance(v, ast.Subscript):       # `d["k"]`, `lista[0]`
        return _clasifica_valoare(v.value, functii, adancime + 1)
    if isinstance(v, ast.BinOp):           # `a + b`, `"%s" % x`
        return _clasifica_valoare(v.left, functii, adancime + 1)
    if isinstance(v, ast.Attribute):
        if v.attr in _RANDARE_ATTR:
            return "randare"
        return "nedeterminat"
    if isinstance(v, ast.Name):
        if any(x in v.id.lower() for x in _RANDARE_NUME):
            return "randare"
        return "nedeterminat"
    if isinstance(v, ast.JoinedStr) or (isinstance(v, ast.Constant) and isinstance(v.value, str)):
        return "reprezentare"
    return "nedeterminat"


def _clasifica_functie(fn, functii, adancime=0):
    """Ce întoarce o funcție locală? Prima ieșire clasificabilă decide."""
    for n in ast.walk(fn):
        if isinstance(n, ast.Return) and n.value is not None:
            c = _clasifica_valoare(n.value, functii, adancime)
            if c != "nedeterminat":
                return c
    return "nedeterminat"


def _atribuiri(fn):
    """nume -> ultima expresie atribuită, în funcția asta."""
    out = {}
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    out[t.id] = n.value
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.value:
            out[n.target.id] = n.value
        elif isinstance(n, ast.For) and isinstance(n.target, ast.Name):
            out.setdefault(n.target.id, n.iter)
    return out


def _dreapta(cmp_nod, local, functii):
    c = cmp_nod.comparators[0]
    if isinstance(c, ast.Name) and c.id in local:
        return _clasifica_valoare(local[c.id], functii)
    return _clasifica_valoare(c, functii)


def aserțiuni(radacini=None):
    """[{fisier, linia, ancora, categorie}] pentru fiecare `"șir" in X` dintr-un fișier-gardă."""
    if radacini is None:
        radacini = [os.path.join(RAD, "core"), os.path.join(RAD, "frontend_test")]
    out = []
    for cale in _fisiere(radacini):
        try:
            arb = ast.parse(io.open(cale, encoding="utf-8").read())
        except SyntaxError:
            continue
        try:
            rel = os.path.relpath(cale, RAD)
        except ValueError:
            rel = cale
        functii = {n.name: n for n in ast.walk(arb) if isinstance(n, ast.FunctionDef)}
        gazde = [n for n in ast.walk(arb) if isinstance(n, ast.FunctionDef)] or [arb]
        for fn in gazde:
            local = _atribuiri(fn)
            for n in ast.walk(fn):
                if not (isinstance(n, ast.Compare)
                        and any(isinstance(o, ast.In) for o in n.ops)
                        and isinstance(n.left, ast.Constant)
                        and isinstance(n.left.value, str)
                        and len(n.left.value) > 3):
                    continue
                out.append({"fisier": rel, "linia": n.lineno,
                            "ancora": n.left.value[:60],
                            "categorie": _dreapta(n, local, functii)})
    return out


def pe_fisier(radacini=None, categorii=CLASA):
    """{fisier: cate aserțiuni din categoriile cerute}."""
    d = {}
    for a in aserțiuni(radacini):
        if a["categorie"] in categorii:
            d[a["fisier"]] = d.get(a["fisier"], 0) + 1
    return d


def pe_categorie(radacini=None):
    d = {}
    for a in aserțiuni(radacini):
        d[a["categorie"]] = d.get(a["categorie"], 0) + 1
    return d
