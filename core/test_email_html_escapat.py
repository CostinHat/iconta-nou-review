# -*- coding: utf-8 -*-
"""[C39, 15.10.2026] În HTML-ul emailurilor construite în Python, orice valoare pusă în text e ESCAPATĂ (`common.esc`) — altfel un nume de
firmă, un mesaj al cabinetului sau o adresă scrisă de om devin markup în emailul destinatarului (găsit: mesajul cabinetului către client
și corpul personalizat al facturii trimise pe email intrau brute; numele firmei în patru emailuri).

PE AST, în funcțiile care construiesc emailuri (cheamă `trimite_email_html*` / `_trimite_brevo`, sau au numele unui constructor de corp:
`_html`, `_email_corp`, `_mesaj_*_html`): fiecare interpolare (`%`, `+`, f-string) într-un literal cu etichete HTML trebuie să fie:
  · o constantă;
  · un apel de escapare (numele funcției conține `esc`), eventual urmat de o metodă (`esc(x).replace("\\n", "<br>")`);
  · o valoare CONSTRUITĂ DE COD, recunoscută după nume: un link / URL, o culoare / un stil, o constantă de valabilitate, sau o variabilă
    care ține HTML deja escapat — convenția: numele se termină în `_html` (ex. `corp_html`, `_pm_html`).
LIMITĂ declarată: o variabilă numită `*_html` e crezută pe cuvânt (convenția e garanția); o valoare escapată departe, într-o altă funcție,
trebuie să-și poarte și ea sufixul.
MUTAȚIE: `_esc_html(...)` scos din emailul pachetului lunar (`uc_pachete.py`) -> pică."""
import ast
import glob
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TAG = re.compile(r"<(p|b|a|div|li|ul|br|span|td|tr|table|h\d|strong|i|hr)\b", re.I)
_SIGUR_NUME = re.compile(r"(^|_)(link|url|culoare|cul|li|stil)$|_html$|^html$|VALABILITATE|_ORE$|_ZILE$|_APP_URL$")
_CONVERSII = re.compile(r"%[-#0 +]*\d*(?:\.\d+)?([sdifr%])")
_TRIMITE = re.compile(r"^(trimite_email_html\w*|_trimite_brevo)$")
_CONSTRUCTOR = re.compile(r"^_(html|email_corp|mesaj_\w+_html)$")


def _nume(n):
    return n.id if isinstance(n, ast.Name) else n.attr if isinstance(n, ast.Attribute) else ""


def sigur(n):
    if isinstance(n, ast.Constant):
        return True
    if isinstance(n, ast.Call):
        if "esc" in _nume(n.func).lower():
            return True
        return isinstance(n.func, ast.Attribute) and sigur(n.func.value)          # esc(x).replace(...)
    if isinstance(n, (ast.Name, ast.Attribute)):
        return bool(_SIGUR_NUME.search(_nume(n)))
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod):          # `rand % (eticheta, esc(x))`: argumentele decid
        return all(sigur(a) for a in (n.right.elts if isinstance(n.right, ast.Tuple) else [n.right]))
    if isinstance(n, ast.BinOp):
        return sigur(n.left) and sigur(n.right)
    if isinstance(n, ast.IfExp):
        return sigur(n.body) and sigur(n.orelse)
    if isinstance(n, ast.JoinedStr):
        return all(sigur(v.value) for v in n.values if isinstance(v, ast.FormattedValue))
    return False


def _html(n):
    if isinstance(n, ast.Constant) and isinstance(n.value, str):
        return bool(_TAG.search(n.value))
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
        return _html(n.left) or _html(n.right)
    if isinstance(n, ast.JoinedStr):
        return any(isinstance(v, ast.Constant) and _TAG.search(v.value) for v in n.values)
    return False


def _termeni(n):
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
        return _termeni(n.left) + _termeni(n.right)
    return [n]


def _functii_email():
    fis = sorted(set(glob.glob(os.path.join(RAD, "core", "*.py")) + [os.path.join(RAD, "main.py")])
                 - set(glob.glob(os.path.join(RAD, "core", "test_*.py"))))
    for f in fis:
        src = open(f, encoding="utf-8").read()
        if "trimite_email_html" not in src and "_trimite_brevo" not in src and "def _html" not in src:
            continue
        arb = ast.parse(src)
        for fn in ast.walk(arb):
            if isinstance(fn, ast.FunctionDef):
                trimite = any(isinstance(c, ast.Call) and _TRIMITE.match(_nume(c.func)) for c in ast.walk(fn))
                if _CONSTRUCTOR.match(fn.name) or trimite:
                    yield os.path.relpath(f, RAD), fn


def neescapate():
    out = set()
    for f, fn in _functii_email():
        for n in ast.walk(fn):
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod) and _html(n.left):
                args = n.right.elts if isinstance(n.right, ast.Tuple) else [n.right]
                tipuri = [c for c in _CONVERSII.findall(n.left.value) if c != "%"] if isinstance(n.left, ast.Constant) else []
                # un argument pus pe `%d` / `%02d` / `%f` e un număr — nu poate purta markup
                rele = [a for i, a in enumerate(args) if not sigur(a) and not (i < len(tipuri) and tipuri[i] in "dif")]
            elif isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add) and _html(n):
                rele = [a for a in _termeni(n) if not (_html(a) or sigur(a))]
            elif isinstance(n, ast.JoinedStr) and _html(n):
                rele = [v.value for v in n.values if isinstance(v, ast.FormattedValue) and not sigur(v.value)]
            else:
                continue
            for a in rele:
                out.add((f, a.lineno, fn.name, ast.unparse(a)[:60]))
    return sorted(out)


def test_valorile_din_html_ul_emailurilor_sunt_escapate():
    rele = neescapate()
    assert rele == [], "valoare neescapată în HTML-ul unui email:\n" + "\n".join("  %s:%d %s  %s" % r for r in rele)


def test_CALIBRARE_garda_vede_emailurile():
    """Anti-vacuu: garda chiar vede constructorii de emailuri cunoscuți."""
    vazute = {(f, fn.name) for f, fn in _functii_email()}
    for cunoscut in (("core/uc_pachete.py", "pachet_poveste_set"), ("core/sinteza_zilnica.py", "_html"),
                     ("core/uc_comun.py", "_mesaj_promo_html"), ("core/uc_tenants.py", "factura_email")):
        assert any(f == cunoscut[0] and (cunoscut[1] in n) for f, n in vazute), (cunoscut, sorted(vazute)[:20])
