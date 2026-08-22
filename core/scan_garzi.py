# -*- coding: utf-8 -*-
"""I1 — instrumentul pentru interdictiile 18 (garda isi ia dovada din proza) si 19 (garda raporteaza
favorabil pe zero randuri), plus cele patru axe cerute.

REGULA 6 din PLAN_INVESTIGATII: masuratoarea NU citeste proza. Tot ce se decide aici se decide pe
ARBORE SINTACTIC (ast) sau pe EXECUTIA tiparului pe corpus. Nicio clasificare pe potrivire de text
in comentarii.

Patru sub-instrumente:
  A. `tipare_moarte`  - fiecare tipar regex dintr-o garda, EXECUTAT pe tot corpusul. Zero potriviri
     pe TOT repo-ul => tiparul nu poate potrivi nimic nicaieri, deci nici pe subiectul lui.
  B. `fara_existenta`  - functii de test in care NICIO asertiune nu stabileste existenta: toate sunt
     de forma „nu s-a intamplat nimic rau". O astfel de garda trece pe o lume goala.
  C. `citeste_proza`   - garda deschide un fisier SURSA (.py/.js) si cauta in text fara sa scoata
     comentariile/docstringurile (fara ast.parse / tokenize / scan_ancore).
  D. `axe_git`         - pentru fiecare fisier-garda: comisa INAINTE de fix (singura, fara fisier de
     productie in acelasi commit) sau ODATA cu fixul.

Se ruleaza cu `--calibrare <rev>` ca sa masoare o revizie din istoric, nu HEAD.
"""
import ast
import io
import os
import re
import subprocess
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT_CORPUS = (".py", ".js", ".html", ".css", ".sql", ".md", ".xsd", ".json", ".csv", ".txt")
SARI_DIR = {"venv", ".git", "__pycache__", "node_modules", ".pytest_cache", "frontend_test"}

FUNCTII_RE = {"compile", "search", "match", "fullmatch", "findall", "finditer", "sub", "subn", "split"}
# Uneltele care SCOT proza inainte de cautare. Prezenta lor = garda nu citeste proza.
# Doar unelte care SCOT proza. `tokenize` si `ast.parse` NU sunt aici, desi par: tokenizarea
# COLECTEAZA string-urile (docstringul e un token de string), iar `ast.parse` lasa docstringurile
# ca noduri Constant. Exact asa a picat `test_schema_coloane`: tokeniza literalii SQL dintr-un .py
# si lua DOCSTRINGURILE drept SQL. Prima forma a instrumentului le scutea pe amandoua si nu gasea
# cazul de calibrare - o lista de scutiri prea larga orbeste la fel de bine ca un tipar mort.
UNELTE_FARA_PROZA = ("scan_ancore", "fara_proza", "domenii_docstring", "ast.get_docstring")


def fisiere_garda(rad):
    out = []
    for r, d, f in os.walk(rad):
        d[:] = [x for x in d if x not in SARI_DIR]
        for n in f:
            if not n.endswith(".py"):
                continue
            if n.startswith("test_") or n.startswith("scan_") or n.startswith("verificator"):
                out.append(os.path.join(r, n))
    return sorted(out)


def corpus(rad):
    """Tot ce se poate citi in repo, ca text. Un tipar care nu potriveste NICAIERI aici nu poate
    potrivi pe subiectul lui - implicatia merge intr-o singura directie, si e cea sigura."""
    buc = []
    for r, d, f in os.walk(rad):
        d[:] = [x for x in d if x not in SARI_DIR]
        for n in f:
            if n.endswith(EXT_CORPUS):
                try:
                    buc.append(io.open(os.path.join(r, n), encoding="utf-8", errors="replace").read())
                except OSError:
                    pass
    return buc


# ---------------------------------------------------------------- A. tipare moarte
def _tipare_din(arb):
    """(linie, tipar) pentru fiecare SIR LITERAL dat unei functii `re`. Sirurile construite
    (f-string, %, concatenare cu variabila) NU se pot extrage - se numara separat."""
    gasite, dinamice = [], 0
    for nod in ast.walk(arb):
        if not isinstance(nod, ast.Call):
            continue
        f = nod.func
        nume = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
        modul = getattr(getattr(f, "value", None), "id", "")
        if nume not in FUNCTII_RE or modul not in ("re", ""):
            continue
        if modul == "" and nume not in ("compile",):
            continue
        if not nod.args:
            continue
        a = nod.args[0]
        if isinstance(a, ast.Constant) and isinstance(a.value, str):
            gasite.append((nod.lineno, a.value, _flaguri(nod)))
        else:
            dinamice += 1
    return gasite, dinamice


_NUME_FLAG = {"S": re.S, "DOTALL": re.S, "I": re.I, "IGNORECASE": re.I, "M": re.M,
              "MULTILINE": re.M, "X": re.X, "VERBOSE": re.X, "A": re.A, "ASCII": re.A}


def _flaguri(nod):
    r"""Flagurile CU CARE GARDA compileaza tiparul. Prima forma a instrumentului compila totul cu
    `re.M` si raporta MOARTE tipare care foloseau `re.S` - fals pozitiv pe o clasa intreaga
    (`.*?\n\}` peste un corp de functie JS). Se citesc din arbore, nu se presupun."""
    f = 0
    arg = None
    if len(nod.args) >= 3:
        arg = nod.args[2]
    elif len(nod.args) >= 2 and not isinstance(nod.args[1], ast.Constant):
        arg = nod.args[1] if getattr(nod.func, "attr", "") == "compile" else None
    for k in nod.keywords or []:
        if k.arg == "flags":
            arg = k.value
    if len(nod.args) >= 2 and getattr(nod.func, "attr", "") == "compile":
        arg = nod.args[1]
    if arg is not None:
        for x in ast.walk(arg):
            if isinstance(x, ast.Attribute) and x.attr in _NUME_FLAG:
                f |= _NUME_FLAG[x.attr]
    return f


def tipare_moarte(rad, garzi, corp):
    """MORT se afirma DOAR pentru tiparele al caror subiect e sursa din repo. Pentru cele care cauta
    intr-un artefact produs la rulare (XML generat, raspuns, PDF randat), corpusul nu spune nimic -
    si atunci instrumentul TACE. Vezi `subiecte()`."""
    from core import scan_garzi_subiect as rA
    morti, dinamice, total, rulare = [], 0, 0, 0
    for cale in garzi:
        try:
            arb = ast.parse(io.open(cale, encoding="utf-8").read())
        except SyntaxError:
            continue
        tip, din = _tipare_din(arb)
        sub = rA.subiecte(arb)
        dinamice += din
        for ln, sir, fl in tip:
            total += 1
            fel = sub.get(("inline", ln), "NECUNOSCUT")
            try:
                # `| re.M` e GENEROS deliberat: flaguri in plus pot doar sa CREASCA potrivirile, deci
                # un tipar ramas fara nicio potrivire e mort si sub flagurile reale. Directia sigura.
                rx = re.compile(sir, fl | re.M)
            except re.error:
                continue
            if any(rx.search(t) for t in corp):
                continue
            if fel != "SURSA":
                rulare += 1
                continue
            morti.append((os.path.relpath(cale, rad), ln, sir))
    return morti, total, dinamice, rulare


# ---------------------------------------------------------------- B. fara existenta
def _valoare_concreta(nod):
    """Un literal care nu poate fi produs de o multime goala: sir nevid, numar nenul, True,
    tuplu/lista de literali."""
    if isinstance(nod, ast.Constant):
        v = nod.value
        if v is True:
            return True
        if isinstance(v, str) and v.strip():
            return True
        if isinstance(v, (int, float)) and v != 0 and v is not False:
            return True
        return False
    if isinstance(nod, (ast.Tuple, ast.List)) and nod.elts:
        return any(_valoare_concreta(e) for e in nod.elts)
    return False


def _stabileste_existenta(test):
    """O asertiune care cere ca CEVA SA FIE. Opusul lui «nu s-a intamplat nimic rau»."""
    for nod in ast.walk(test):
        if not isinstance(nod, ast.Assert):
            continue
        t = nod.test
        if isinstance(t, ast.UnaryOp) and isinstance(t.op, ast.Not):
            continue                                   # `assert not X` - negativa
        if isinstance(t, ast.Compare):
            st = t.ops[0]
            dr = t.comparators[0]
            if isinstance(st, (ast.Gt, ast.GtE)):
                return True                            # len(x) > 0, dar si `ded_tanar > ded_matur`:
                #  o inegalitate stricta cere o relatie NENULA, deci nu poate fi adevarata pe gol
            if isinstance(st, (ast.In, ast.IsNot)):
                return True                            # x in y / x is not None
            # O asertiune care FIXEAZA o valoare concreta nu poate fi adevarata pe o lume goala:
            # `== 'valid'`, `== 200.0`, `is True`, `== (1000, 210)`. Prima forma accepta doar
            # intregi pozitivi si raporta fals ~o treime din esantion - clasa a fost numita uitandu-ma
            # la 29 de rezultate, nu la cod.
            if isinstance(st, (ast.Eq, ast.Is)) and any(_valoare_concreta(x) for x in (t.left, dr)):
                return True
            continue                                   # restul comparatiilor: negative
        if isinstance(t, ast.Call):
            n = t.func.attr if isinstance(t.func, ast.Attribute) else getattr(t.func, "id", "")
            if n == "all":
                continue                               # `assert all(...)` - vid pe lista goala
            return True                                # any(...), o functie care trebuie sa fie True
        if isinstance(t, (ast.Name, ast.Attribute, ast.Subscript)):
            return True                                # `assert x` - x trebuie sa fie nevid
        if isinstance(t, ast.BoolOp):
            return True
    # Indexarea unei multimi CULESE e tot un control de existenta: `randuri[0]` crapa pe gol, deci
    # testul NU poate trece pe o lume goala. Instrumentul o rata si raporta fals.
    for nod in ast.walk(test):
        if isinstance(nod, ast.Subscript) and isinstance(nod.value, ast.Name) \
                and isinstance(nod.slice, ast.Constant) and isinstance(nod.slice.value, int):
            return True
    return False


def fara_existenta(rad, garzi):
    """Vezi rB.py: se numara DOAR testele care isi culeg subiectul (fisiere plimbate, randuri
    interogate), fiindca doar acolo multimea poate fi goala. Testele unitare pe intrare construita
    n-au risc de vid si au fost scoase - erau majoritatea celor 753 din prima forma."""
    from core import scan_garzi_culegere as rB
    rele, total, culeg, cu_control = [], 0, 0, 0
    for cale in garzi:
        try:
            arb = ast.parse(io.open(cale, encoding="utf-8").read())
        except SyntaxError:
            continue
        ajut = rB.ajutoare_modul(arb)
        are_control = rB.control_pozitiv(arb, _stabileste_existenta)
        for nod in ast.walk(arb):
            if not isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not nod.name.startswith("test_"):
                continue
            if not any(isinstance(x, ast.Assert) for x in ast.walk(nod)):
                continue
            total += 1
            if not rB.culege(nod, ajut):
                continue
            culeg += 1
            if _stabileste_existenta(nod):
                continue
            # NU se mai SCUTESTE testul fiindca modulul are un control pozitiv. Scaparea aia a
            # INGHITIT cazul de calibrare (`test_verificarea_nu_scrie_nimic`, reconstruit): modulul
            # era plin de teste bune si unul singur numara pe o luna FARA nicio contradictie. Un
            # frate care dovedeste ca fisierul se citeste nu dovedeste ca ACEST test are ce vedea.
            # Controlul de modul ramane raportat, ca atenuare - nu ca exceptie.
            if are_control:
                cu_control += 1
            rele.append((os.path.relpath(cale, rad), nod.lineno, nod.name, are_control))
    return rele, total, culeg, cu_control


# ---------------------------------------------------------------- C. citeste proza
def _citeste_sursa(arb):
    """True daca fisierul deschide un .py/.js si ii citeste textul."""
    for nod in ast.walk(arb):
        if isinstance(nod, ast.Call):
            f = nod.func
            n = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            if n in ("read_text",):
                return True
            if n == "read" and isinstance(f, ast.Attribute) and isinstance(f.value, ast.Call):
                g = f.value.func
                gn = g.attr if isinstance(g, ast.Attribute) else getattr(g, "id", "")
                if gn == "open":
                    return True
    return False


_MARCAJE_COMENTARIU = ("//", "#", '"""', "/*", "'''")


def _isi_scoate_singur_proza(arb):
    """Modulul isi taie singur comentariile? `test_proprietate_coaja` are `_fara_comentarii()` si
    instrumentul il raporta FALS. Se decide pe ARBORE - un `re.sub`/`split`/`startswith` peste un
    marcaj de comentariu - nu dupa numele functiei, care s-ar putea chema oricum."""
    for nod in ast.walk(arb):
        if not isinstance(nod, ast.Call):
            continue
        f = nod.func
        n = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
        if n not in ("sub", "subn", "split", "startswith", "partition", "find", "index"):
            continue
        for a in list(nod.args) + ([f.value] if isinstance(f, ast.Attribute) else []):
            if isinstance(a, ast.Constant) and isinstance(a.value, str) \
                    and any(m in a.value for m in _MARCAJE_COMENTARIU):
                return True
    return False


def citeste_proza(rad, garzi):
    rele = []
    for cale in garzi:
        sursa = io.open(cale, encoding="utf-8").read()
        try:
            arb = ast.parse(sursa)
        except SyntaxError:
            continue
        if not _citeste_sursa(arb):
            continue
        # Tinta e SURSA (nu .md/.json)? Se decide pe literalele de extensie din fisier.
        exts = {c.value for c in ast.walk(arb)
                if isinstance(c, ast.Constant) and isinstance(c.value, str)
                and c.value in (".py", ".js", "*.py", "*.js", "**/*.py", "**/*.js")}
        if not exts:
            continue
        if any(u in sursa for u in UNELTE_FARA_PROZA):
            continue
        if _isi_scoate_singur_proza(arb):
            continue
        rele.append((os.path.relpath(cale, rad), sorted(exts)))
    return rele


# ---------------------------------------------------------------- D. axe git
def axe_git(rad, garzi):
    """Pentru fiecare garda: commitul ei de INTRODUCERE a atins si fisiere de PRODUCTIE?
    Da => scrisa ODATA CU fixul. Nu => scrisa SINGURA (inainte, sau pe cod existent)."""
    out = {"cu_fixul": [], "singura": [], "necunoscut": []}
    for cale in garzi:
        rel = os.path.relpath(cale, rad)
        try:
            h = subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "--", rel],
                               cwd=rad, capture_output=True, text=True, timeout=60).stdout.split()
        except subprocess.TimeoutExpired:
            out["necunoscut"].append(rel)
            continue
        if not h:
            out["necunoscut"].append(rel)
            continue
        com = h[0]
        fis = subprocess.run(["git", "show", "--name-only", "--format=", com],
                             cwd=rad, capture_output=True, text=True).stdout.split()
        prod = [x for x in fis if x.endswith((".py", ".js"))
                and not os.path.basename(x).startswith(("test_", "scan_", "verificator"))]
        (out["cu_fixul"] if prod else out["singura"]).append(rel)
    return out


def main():
    rad = RAD
    if "--rad" in sys.argv:
        rad = sys.argv[sys.argv.index("--rad") + 1]
    doar = sys.argv[sys.argv.index("--doar") + 1] if "--doar" in sys.argv else "abcd"

    garzi = fisiere_garda(os.path.join(rad, "core")) + \
        [os.path.join(rad, x) for x in os.listdir(rad) if x.startswith("verificator") and x.endswith(".py")]
    print("GARZI SCANATE: %d fisiere" % len(garzi))

    if "a" in doar:
        corp = corpus(rad)
        morti, total, din, rul = tipare_moarte(rad, garzi, corp)
        print("\n=== A. TIPARE MOARTE (zero potriviri pe corpus, SUBIECT=SURSA) === %d din %d "
              "(+%d construite dinamic, neextractibile; %d cu zero potriviri dar SUBIECT=RULARE, "
              "despre care corpusul nu poate spune nimic)" % (len(morti), total, din, rul))
        for f, ln, s in morti:
            print("  %s:%d  %r" % (f, ln, s))

    if "b" in doar:
        rele, total, culeg, ctrl = fara_existenta(rad, garzi)
        print("\n=== B. VID POSIBIL (culege + nicio existenta + niciun control pozitiv in modul) "
              "=== %d din %d care CULEG, din %d teste cu asertiuni "
              "(%d dintre ele au un control pozitiv in MODUL - atenuare, nu exceptie)"
              % (len(rele), culeg, total, ctrl))
        for f, ln, n, ctr in rele[:400]:
            print("  %s:%d  %s%s" % (f, ln, n, "   [control in modul]" if ctr else ""))

    if "c" in doar:
        rele = citeste_proza(rad, garzi)
        print("\n=== C. GARZI CARE CITESC SURSA FARA SA SCOATA PROZA === %d" % len(rele))
        for f, e in rele:
            print("  %s  %s" % (f, e))

    if "d" in doar:
        o = axe_git(rad, garzi)
        print("\n=== D. SCRISA ODATA CU FIXUL / SINGURA ===")
        print("  odata cu fixul: %d" % len(o["cu_fixul"]))
        print("  singura:        %d" % len(o["singura"]))
        print("  necunoscut:     %d" % len(o["necunoscut"]))


if __name__ == "__main__":
    main()
