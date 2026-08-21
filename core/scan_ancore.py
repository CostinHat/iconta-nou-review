# -*- coding: utf-8 -*-
"""SCANNER de ANCORE: un gard care caută un șir într-un fișier sursă îl găsește în COD, sau doar în
PROZĂ? (21.08.2026)

DE CE. Clasa a apărut de TREI ori într-o zi: gardul TEMA D s-a aprins pe propria explicație; `lit.`
din scanul de constante s-a aprins pe cuvântul „po-LIT-e)"; iar `test_randerul_chiar_o_afiseaza` a
rămas VERDE după ce titlul secțiunii a fost șters din randare, fiindcă îl găsea în comentariul de
deasupra. De fiecare dată gardul citea proză și credea că citește cod.

Un gard a cărui ancoră trăiește doar într-un comentariu e mai rău decât niciunul: raportează verde
despre o lume pe care n-o vede, și rezistă exact la mutația care ar trebui să-l facă roșu.

CE FACE. Găsește aserțiunile de forma `"ANCORĂ" in <sursă citită>` din teste, rezolvă fișierul citit
(`inspect.getsource(X)` sau `open(<cale>).read()`), scoate comentariile și docstringurile, și verifică
dacă ancora mai există. Dacă nu — gardul e ancorat în proză.

CE NU POATE SPUNE. Nu rezolvă orice formă de citire (căi construite dinamic, fișiere alese la rulare).
Alea sunt raportate ca „nerezolvate", NU ca trecute — absența unei verificări nu e o verificare.
"""
import ast
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fara_proza(text, cale):
    """Sursa fără comentarii și fără docstringuri. Pentru .js: comentarii // și /* */."""
    if cale.endswith(".js"):
        text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
        return re.sub(r"(^|[^:])//[^\n]*", r"\1", text)
    try:
        arb = ast.parse(text)
    except SyntaxError:
        return text
    doc = set()
    for n in ast.walk(arb):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            c = getattr(n, "body", None)
            if c and isinstance(c[0], ast.Expr) and isinstance(c[0].value, ast.Constant) \
               and isinstance(c[0].value.value, str):
                doc.add((c[0].lineno, c[0].end_lineno))
    linii = text.splitlines()
    afara = []
    for i, l in enumerate(linii, 1):
        if any(a <= i <= b for a, b in doc):
            continue
        afara.append(re.sub(r"#.*$", "", l))
    return "\n".join(afara)


def _cale_din_apel(nod):
    """Calea citită de `open(...)` — acceptă os.path.join cu bucăți literale."""
    buc = [a.value for a in ast.walk(nod)
           if isinstance(a, ast.Constant) and isinstance(a.value, str)]
    buc = [b for b in buc if b not in ("utf-8", "r", "replace", "strict")]
    if not buc:
        return None
    cale = os.path.join(*buc) if len(buc) > 1 else buc[0]
    return cale if cale.endswith((".py", ".js", ".json", ".md")) else None


def _tinta_functiei(fn):
    """(fel, referință) pentru sursa citită de funcție.

    O funcție care citește MAI MULTE fișiere nu poate fi verificată: nu știm care aserțiune se referă
    la care sursă, iar a presupune primul fișier produce acuzații false — s-a întâmplat la calibrare
    (`test_backend_contract_erori_campuri_wired` citește api.js ȘI main.py, iar ancora din main.py a
    fost raportată „absentă" pentru că era căutată în api.js). Se raportează AMBIGUU, nu greșit."""
    tinte = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "getsource":
            if n.args:
                tinte.append(("modul", ast.unparse(n.args[0])))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "open":
            c = _cale_din_apel(n)
            if c:
                tinte.append(("cale", c))
    unice = list(dict.fromkeys(tinte))
    if len(unice) == 1:
        return unice[0]
    return ("ambiguu", len(unice)) if unice else (None, None)


def inventar():
    """[(fisier_test, functie, ancora, stare)] cu stare ∈ cod | PROZA | nerezolvat."""
    out = []
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if not (f.startswith("test_") and f.endswith(".py")):
            continue
        p = os.path.join(RAD, "core", f)
        try:
            arb = ast.parse(io.open(p, encoding="utf-8").read())
        except SyntaxError:
            continue
        for fn in ast.walk(arb):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            fel, ref = _tinta_functiei(fn)
            if not fel:
                continue
            ancore = [n.left.value for n in ast.walk(fn)
                      if isinstance(n, ast.Compare) and any(isinstance(o, ast.In) for o in n.ops)
                      and isinstance(n.left, ast.Constant) and isinstance(n.left.value, str)
                      and len(n.left.value) > 3]
            if not ancore:
                continue
            if fel == "ambiguu":
                for a in ancore:
                    out.append((f, fn.name, a, "ambiguu"))
                continue
            text, cale = _sursa_tinta(fel, ref)
            for a in ancore:
                if text is None:
                    out.append((f, fn.name, a, "nerezolvat"))
                elif a in fara_proza(text, cale):
                    out.append((f, fn.name, a, "cod"))
                elif a in text:
                    out.append((f, fn.name, a, "PROZA"))
                else:
                    out.append((f, fn.name, a, "absent"))
    return out


def _sursa_tinta(fel, ref):
    if fel == "cale":
        p = ref if os.path.isabs(ref) else os.path.join(RAD, ref)
        if os.path.exists(p):
            return io.open(p, encoding="utf-8", errors="replace").read(), p
        # calea e relativă la altceva — o căutăm după numele fișierului
        nume = os.path.basename(ref)
        for rad, dirs, fis in os.walk(RAD):
            if any(x in rad for x in ("venv", ".git", "_arhiva", "node_modules")):
                continue
            if nume in fis:
                q = os.path.join(rad, nume)
                return io.open(q, encoding="utf-8", errors="replace").read(), q
        return None, ref
    # modul: rezolvăm prin import
    nume = ref.split(".")[-1]
    for sub in ("core", "frontend_test", ""):
        q = os.path.join(RAD, sub, "%s.py" % nume) if sub else os.path.join(RAD, "%s.py" % nume)
        if os.path.exists(q):
            return io.open(q, encoding="utf-8", errors="replace").read(), q
    return None, ref


if __name__ == "__main__":
    from collections import Counter
    inv = inventar()
    c = Counter(s for _f, _fn, _a, s in inv)
    print("ancore: %d | %s" % (len(inv), dict(c)))
    for f, fn, a, s in inv:
        if s in ("PROZA", "absent"):
            print("  [%s] %s::%s  -> %r" % (s, f, fn, a[:70]))
