# -*- coding: utf-8 -*-
"""core/test_cont_din_corp_normalizat.py — un cont luat din CORPUL CERERII trece prin strip().

DE UNDE VINE (masurat 26.08.2026, pe AST): tiparul
    str(corp.get("cont_x") or "<implicit>")
arata ca o garda si e o MASCA. `or` transforma None si "" in implicit, dar lasa "   " sa treaca
VERBATIM in `inregistrari_linii`. Consecinta, probata pe schema efemera:
  - `NOT NULL` nu-l opreste (spatiile nu sunt NULL);
  - un `CHECK (cont <> '')` nu l-ar fi oprit (spatiile nu sunt sirul gol);
  - si pana la reparatia din aceeasi zi NICIUNA din cele doua verificari de echilibru nu-l vedea,
    fiindca `if l.get("cont_debit")` e ADEVARAT pe "   ".
Clasa avea 19 situri (main.py, core/inventariere.py, core/stocuri_cv_api.py), toate reparate cu
tiparul deja corect din acelasi cod: `(str(corp.get("x") or "").strip() or "<implicit>")`.

ASERTEAZA PE STRUCTURA, nu pe text (clichet 50): se cauta in AST daca nodul care citeste contul
are un stramos `.strip()` care il CONTINE — nu daca sirul ".strip()" apare pe aceeasi linie.

MODURILE DE ESEC ALE GARDULUI, scrise INAINTE (interdictia 76):
  H1 corpul cererii sub alt nume decat corp/date/body/payload -> NEVAZUT. Domeniul e declarat.
  H2 normalizarea intr-o functie chemata (`_cont(corp, "x")`) -> ar aparea ca neacoperit, adica
     FALS POZITIV, nu fals negativ. Directia sigura.
  H3 cheie care nu incepe cu "cont" (ex. "debit") -> NEVAZUT; masurat: nu exista azi.
  H4 fisiere de test -> excluse deliberat (fixturile au voie sa construiasca date rupte).
"""
import ast
import io
import os

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPURI = {"corp", "date", "body", "payload"}

# Situri care au voie sa NU fie normalizate, fiecare cu motivul. Gol = nimic tolerat.
PIN = {}


def _fisiere():
    out = [os.path.join(RAD, "main.py")]
    cd = os.path.join(RAD, "core")
    for f in sorted(os.listdir(cd)):
        if f.endswith(".py") and not f.startswith("test_") and not f.startswith("scan_"):
            out.append(os.path.join(cd, f))
    return out


def _e_cont(cheie):
    """Cheia numeste un CONT contabil, nu orice incepe cu «cont».

    Calibrare negativa gasita de gard pe el insusi, la prima rulare: `corp.get("continut")` --
    continutul unui mesaj -- trecea drept cont si producea un fals pozitiv. Prefixul brut "cont"
    e prea larg; forma reala e `cont` exact, sau `cont_<ceva>`."""
    return bool(cheie) and (cheie == "cont" or cheie.startswith("cont_"))


def _parinti(arb):
    p = {}
    for n in ast.walk(arb):
        for c in ast.iter_child_nodes(n):
            p[c] = n
    return p


def _sub_strip(nod, par):
    """Are nodul un STRAMOS `.strip()` care il contine? Structural, nu textual."""
    cur = nod
    while cur in par:
        cur = par[cur]
        if isinstance(cur, ast.Call) and isinstance(cur.func, ast.Attribute) and cur.func.attr == "strip":
            return True
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            return False
    return False


def _citiri_de_cont():
    """[(fisier:linie, expresie, normalizat)] pentru fiecare citire de cont din corpul cererii."""
    gasite = []
    for cale in _fisiere():
        rel = os.path.relpath(cale, RAD)
        try:
            arb = ast.parse(io.open(cale, encoding="utf-8").read())
        except SyntaxError:
            continue
        par = _parinti(arb)
        for n in ast.walk(arb):
            cheie = baza = None
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get"
                    and n.args and isinstance(n.args[0], ast.Constant)
                    and isinstance(n.args[0].value, str)):
                cheie, baza = n.args[0].value, n.func.value
            elif (isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant)
                  and isinstance(n.slice.value, str)):
                cheie, baza = n.slice.value, n.value
            if not _e_cont(cheie):
                continue
            if not (isinstance(baza, ast.Name) and baza.id in CORPURI):
                continue
            gasite.append(("%s:%d" % (rel, n.lineno), ast.unparse(n), _sub_strip(n, par)))
    return gasite


@pytest.fixture(scope="module")
def citiri():
    g = _citiri_de_cont()
    # ANTI-VACUU: un gard care nu gaseste nimic raporteaza verde despre o lume pe care n-o vede.
    assert len(g) >= 15, (
        "sonda a gasit doar %d citiri de cont din corpul cererii — clasa masurata pe 26.08.2026 "
        "avea 19 situri reparate plus cele deja corecte. Sub prag inseamna ca sonda s-a rupt "
        "(redenumire de variabila, alt tipar), nu ca s-a curatat codul." % len(g))
    return g


def test_orice_cont_din_corpul_cererii_trece_prin_strip(citiri):
    rele = [(u, e) for (u, e, ok) in citiri if not ok and u not in PIN]
    assert not rele, (
        "%d citire(i) de cont din corpul cererii NU trec prin strip() — un cont format din spatii "
        "ajunge verbatim in evidenta, iar acolo nu-l opreste nici NOT NULL, nici un CHECK pe sirul "
        "gol:\n%s" % (len(rele), "\n".join("  %s   ->  %s" % (u, e[:110]) for u, e in rele)))


def test_sonda_chiar_vede_un_sit_nenormalizat():
    """CALIBRARE POZITIVA pe propriul mod de esec: daca sonda n-ar deosebi normalizat de
    nenormalizat, testul de mai sus ar fi verde pe orice cod."""
    arb = ast.parse('x = str(corp.get("cont_venit") or "707")\n'
                    'y = (str(corp.get("cont_stoc") or "").strip() or "371")\n')
    par = _parinti(arb)
    stari = {}
    for n in ast.walk(arb):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get"
                and n.args and isinstance(n.args[0], ast.Constant)):
            stari[n.args[0].value] = _sub_strip(n, par)
    assert stari == {"cont_venit": False, "cont_stoc": True}, stari


def test_pinul_e_gol_sau_motivat():
    """Un sit tolerat fara motiv scris ar face din clichet o lista de ignorat."""
    for unde, motiv in PIN.items():
        assert isinstance(motiv, str) and len(motiv) > 40, \
            "%s e in PIN fara motiv scris" % unde
