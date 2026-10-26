# -*- coding: utf-8 -*-
"""GARD — deficiența 258 (comanda Costin 15.10.2026, verbatim: „mesajul pentru asistent spune «Nota #24», iar pe card nota e «Nr. crt.
5»; numărul intern nu se afișează nicăieri.”). CLASA: orice text pe care îl citește omul și care numește o înregistrare (notă, factură,
operațiune, salariat, cerere, firmă) prin id-ul ei intern, cu „#”, în loc de ce vede pe ecran (nota: „nr. crt. 5 din 12.03.2026”,
`core/eticheta_nota.py`; factura: seria, numărul și data; omul și firma: numele).

CE CAUTĂ, pe structură (AST pentru Python, tipar ancorat pentru JS), nu pe o listă de mesaje:
  - Python (`core/**/*.py` fără teste, `main.py`): un literal de text în care „#” stă la început de cuvânt și e urmat de un loc de
    completat — `#%s`, `#%d`, `#%(x)s`, `#%` (RAISE din plpgsql, în migrări), `#{}` (`.format`) sau `#` urmat de o valoare într-un
    f-string;
  - JS (`static/**/*.js`, `static/*.html`, fără `vendor/`): `#${…}` sau un text terminat în „#” lipit cu `+` de o valoare.
CE NU E CLASA, exclus STRUCTURAL (nu după mesaj):
  - un selector CSS: argumentul unei funcții de selecție (`querySelector`, `querySelectorAll`, `closest`, `matches`, `getElementById`,
    `gv`) — `"#" + id` acolo e id-ul unui element HTML, nu al unei înregistrări;
  - „#” lipit de un cuvânt sau de o valoare (`%s#%s`, `/#${…}`, `}#${…}`): fragmentul unei adrese, nu o etichetă;
  - numărul de ORDINE dintr-o listă a declarației (`for i, x in enumerate(...)`: „polița #3”) — e poziția pe care omul o vede în
    lista lui, nu un id;
  - textul pentru TERMINAL (`print`, jurnalul aplicației `log.*` / `logger.*`) și domeniul unei afirmații (`unde=`, `core/afirmatii.py`:
    nu se afișează — ecranul arată motivul; verificat: `static/js` nu citește `unde` din afirmații);
  - `EXCEPTII` (numite, cu motiv): textele pentru echipa iConta, unde id-ul e chiar ce cere ruta de execuție manuală.
CLICHETUL E LA ZERO: orice apariție nouă pică, cu fișierul, rândul și textul.
MUTAȚIE: `"Nota #%s e la validare"` pus înapoi în `core/coada_api.py` -> ROȘU (proba în raportul lotului)."""
import ast
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: (fișier, funcție) -> motivul pentru care id-ul intern e chiar textul potrivit
EXCEPTII = {
    ("core/gdpr_cerere.py", "corp_anunt"): "emailul către echipa iConta: execuția manuală se cere pe ruta "
                                            "`/gdpr/sterge-cabinet/<id>/executa`, deci id-urile cabinetului și ale cererii sunt instrucțiunea",
}

#: „#” la început de cuvânt, urmat de un loc de completat (printf, plpgsql `%`, `.format`)
_PY = re.compile(r"(?:^|(?<=[\s(\[„\"'«:,]))#(?:%|\{\})")
_SELECTORI = ("querySelector", "querySelectorAll", "closest", "matches", "getElementById", "gv",
              # [lotul 13] `api.cereAlegerile(root, [selectori])` — al doilea argument e o listă de selectori CSS
              "cereAlegerile")
_JS = re.compile(r"(?:^|(?<=[\s(\[„\"'`>«:,]))#(?:\$\{|[\"'`]\s*\+)")
_LOG = ("debug", "info", "warning", "error", "exception", "critical")


def _fisiere_py():
    out = [os.path.join(RAD, "main.py")]
    for d, _dirs, fis in os.walk(os.path.join(RAD, "core")):
        out += [os.path.join(d, f) for f in fis if f.endswith(".py") and not f.startswith("test_")]
    return sorted(out)


def _fisiere_js():
    out = []
    for d, dirs, fis in os.walk(os.path.join(RAD, "static")):
        dirs[:] = [x for x in dirs if x != "vendor"]
        out += [os.path.join(d, f) for f in fis if f.endswith(".js") and not f.endswith(".min.js")]
    out += [os.path.join(RAD, "static", f) for f in os.listdir(os.path.join(RAD, "static")) if f.endswith(".html")]
    return sorted(out)


def _parinti(t):
    p = {}
    for n in ast.walk(t):
        for c in ast.iter_child_nodes(n):
            p[c] = n
    return p


def _contoare_enumerate(fn):
    """Numele legate ca număr de ordine: primul element din `for i, x in enumerate(...)`."""
    out = set()
    for n in ast.walk(fn):
        if isinstance(n, (ast.For, ast.comprehension)) and isinstance(n.iter, ast.Call) and getattr(n.iter.func, "id", None) == "enumerate" \
                and isinstance(n.target, ast.Tuple) and isinstance(n.target.elts[0], ast.Name):
            out.add(n.target.elts[0].id)
    return out


def _argument_la_diez(s, dreapta):
    """Expresia care completează locul de după „#” într-un `"…" % dreapta` (sau None dacă nu se poate citi)."""
    m = _PY.search(s)
    k = len(re.findall(r"%(?:\(\w+\))?[-#0 +]*\d*(?:\.\d+)?[sdifr]", s[:m.start()]))
    if isinstance(dreapta, ast.Tuple):
        return dreapta.elts[k] if k < len(dreapta.elts) else None
    return dreapta if k == 0 else None


def _exclus_py(nod, par, rel):
    """De ce un literal cu „#<loc>” nu e textul unei înregistrări pentru om (sau None dacă e)."""
    p, copil, fn = nod, nod, None
    while p in par:
        copil, p = p, par[p]
        if isinstance(p, ast.keyword) and p.arg == "unde":
            return "domeniul afirmației"
        if isinstance(p, ast.Call):
            f = p.func
            if getattr(f, "id", None) == "print" or (isinstance(f, ast.Attribute) and f.attr in _LOG
                                                    and "log" in ast.unparse(f.value).lower()):
                return "terminal / jurnalul aplicației"
        if isinstance(p, ast.BinOp) and isinstance(p.op, ast.Mod) and copil is p.left and isinstance(nod, ast.Constant):
            arg = _argument_la_diez(nod.value, p.right)
            fn_ = p
            while fn_ in par and not isinstance(fn_, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_ = par[fn_]
            if isinstance(arg, ast.Name) and isinstance(fn_, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                    and arg.id in _contoare_enumerate(fn_):
                return "număr de ordine din listă"
        if isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef)) and fn is None:
            fn = p.name
    if (rel, fn) in EXCEPTII:
        return "excepție numită"
    return None


def aparitii_py():
    rele = []
    for cale in _fisiere_py():
        rel = os.path.relpath(cale, RAD)
        t = ast.parse(open(cale, encoding="utf-8").read())
        par = _parinti(t)
        for n in ast.walk(t):
            text = None
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and _PY.search(n.value) and not (
                    n in par and isinstance(par[n], ast.Expr)):                                # un docstring nu se afișează
                text = n.value
            elif isinstance(n, ast.JoinedStr):                                                 # f"… #{x}"
                for a, b in zip(n.values, n.values[1:]):
                    if isinstance(a, ast.Constant) and isinstance(b, ast.FormattedValue) and re.search(r"(?:^|[\s(„\"'])#$", a.value):
                        text = a.value + "{…}"
            if text is not None and not _exclus_py(n, par, rel):
                rele.append((rel, n.lineno, text.strip()[:110]))
    return ["%s:%d  %s" % r for r in sorted(rele)]


def aparitii_js():
    rele = []
    for cale in _fisiere_js():
        rel = os.path.relpath(cale, RAD)
        for i, linie in enumerate(open(cale, encoding="utf-8"), 1):
            if linie.lstrip().startswith("//"):
                continue
            for m in _JS.finditer(linie):
                inainte = linie[:m.start()].rstrip("`\"' ")
                # selector CSS: „#” stă între parantezele unei funcții de selecție, ca prim argument sau mai încolo (o listă de selectori)
                if re.search(r"\b(?:%s)\([^()]*$" % "|".join(_SELECTORI), inainte):
                    continue
                rele.append("%s:%d  %s" % (rel, i, linie.strip()[:130]))
    return rele


def test_niciun_text_pentru_om_nu_numeste_o_inregistrare_prin_id_intern():
    rele = aparitii_py() + aparitii_js()
    assert rele == [], ("%d texte arată id-ul intern cu „#” (deficiența 258) — numește înregistrarea cum o vede omul: nota prin "
                        "`core/eticheta_nota.py` („nr. crt. N din ZZ.LL.AAAA”), factura prin serie, număr și dată, omul și firma prin nume:\n  %s"
                        % (len(rele), "\n  ".join(rele)))


def test_scanerul_vede_clasa_si_lasa_exceptiile_structurale(tmp_path, monkeypatch):
    """Scanerul nu e orb: pe un modul sintetic vede fiecare formă a clasei și lasă în pace fiecare excludere."""
    import core.test_id_intern_afisat as g
    (tmp_path / "core").mkdir()
    (tmp_path / "static").mkdir()
    (tmp_path / "main.py").write_text("", encoding="utf-8")
    (tmp_path / "core" / "m.py").write_text(
        'A = "Nota #%s e la validare" % 5\n'
        'B = "Factura #%(id)s" % {"id": 1}\n'
        'C = f"ciorna #{7}"\n'
        "D = \"RAISE EXCEPTION 'Nota #% e validată', OLD.id\"\n"
        'E = "firma #{}".format(3)\n'
        'def f(polite, log):\n'
        '    for i, p in enumerate(polite, 1):\n'
        '        x = "polita #%d: " % i\n'
        '    print("  #%s" % 9)\n'
        '    log.warning("nota #%s", 3)\n'
        '    g(unde="nota #%s" % 4)\n'
        '    return "%s#%s" % ("url", "ancora")\n', encoding="utf-8")
    (tmp_path / "static" / "e.js").write_text(
        'const a = `Nota #${n.id}`;\n'
        'const b = "Cerere (#" + r.id + ")";\n'
        'const c = corp.querySelector("#" + id);\n'
        'const d = scope.querySelector(`#${prefix}-cor`);\n'
        'window.open(`/#${q}`);\n'
        'if (cereAlegerile(corp, [`#${P}-afiliat`])) lipsa = true;\n'
        'arata(`Cerere #${r.id}`, document.querySelector("#x"));\n', encoding="utf-8")
    monkeypatch.setattr(g, "RAD", str(tmp_path))
    assert [r.split("  ")[0] for r in g.aparitii_py()] == ["core/m.py:%d" % i for i in (1, 2, 3, 4, 5)]
    assert [r.split("  ")[0] for r in g.aparitii_js()] == ["static/e.js:1", "static/e.js:2", "static/e.js:7"]
