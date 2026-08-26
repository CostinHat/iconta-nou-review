# -*- coding: utf-8 -*-
"""GARD [R61, 26.08.2026]: raportul Z nu se poate înregistra de două ori, iar niciuna din cele
două rute nu scrie într-o lună închisă.

De unde vine. Costin a întrebat, la lotul 6, *ce deosebește `horeca/raport-z` de
`horeca/import-amef`*. Deosebirile sunt reale (fișier parsat vs. tastat · ciornă vs. validată),
iar rolul e explicat în cod. Dar **cele două asimetrii care contează mergeau invers decât rolul**:
ruta cu rol scria `validata` direct **fără verificare de duplicat**, iar ruta fără rol era singura
**fără poarta de perioadă închisă**. Un al doilea apel dubla venitul zilei, direct în evidență.

Decizia lui (varianta a): a doua notă se **refuză 409**. Un duplicat nu e o corecție, e o greșeală
de operare. Iar cheia nu e data — e **NUI + numărul raportului**: o firmă cu două case de marcat
are două rapoarte Z legitime în aceeași zi.

CE FACE IMPOSIBIL: o rută de raport Z care scrie în `inregistrari` **înainte** de a fi întrebat
dacă raportul există deja · una care scrie fără poarta de perioadă · o verificare de unicitate
care se uită într-o singură sursă (tastate DA, importate NU — adică jumătate de poartă).

CUM ASERTEAZĂ, fiindcă e chiar întrebarea pe care o pune clichetul 50: **numai pe noduri de AST**
— apeluri, linii, și mulțimea `_SURSE_Z` citită ca literal. Nicăieri, nici măcar la recunoașterea
scrierii, nu se caută un șir într-un text: ordinea se măsoară față de primul `…execute(…)`, care e
un nod, nu o interogare citită ca proză.

CE NU FACE, declarat: nu probează pe date că baza refuză — e o gardă pe structura rutei, nu o
probă funcțională. Nu spune nici că totalurile sunt corecte; spune că nota nu se poate dubla.
"""
import ast
import io
import os

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RUTE = ("horeca_raport_z", "horeca_import_amef")
_GARZI = ("_cere_z_unic", "_cere_luna_deschisa")

# felurile în care lipsa poate arăta — mulțime închisă, ca asertarea să fie pe ele, nu pe frază
ABSENT, DUPA_SCRIERE, FARA_RUTA, FARA_EXECUTIE = (
    "absent", "dupa_scriere", "fara_ruta", "fara_executie")


def _functii(sursa):
    return {n.name: n for n in ast.walk(ast.parse(sursa))
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _linia_primului_apel(fn, nume):
    linii = [n.lineno for n in ast.walk(fn)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == nume]
    return min(linii) if linii else None


def _linia_primei_executii(fn):
    """Linia primului `…execute(…)` din corp, sau None.

    Ancora e un **nod de AST** — un apel al cărui `func` e un atribut numit `execute` — nu un șir
    căutat în SQL. Prima formă a gardului citea textul interogării (*INSERT INTO … inregistrari*),
    ceea ce însemna că singura parte structurală lipsea exact acolo unde clichetul 50 o cere. Pe
    rutele astea cele două coincid: primul `execute` din corp **este** INSERT-ul.

    Afirmația e și mai tare așa: gărzile trebuie să fie înaintea **oricărei** interogări a rutei,
    nu doar înaintea scrierii. Consecința, declarată: dacă vreodată o rută pune un SELECT propriu
    înaintea gărzilor, testul cade — și e corect să cadă, fiindcă atunci poarta n-ar mai fi prima."""
    linii = [n.lineno for n in ast.walk(fn)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "execute"]
    return min(linii) if linii else None


def _lipsuri(sursa):
    """[(ruta, garda, felul)] — structuri, nu propoziții. Gardul asertează pe ele."""
    fns = _functii(sursa)
    rele = []
    for nume in _RUTE:
        fn = fns.get(nume)
        if fn is None:
            rele.append((nume, None, FARA_RUTA))
            continue
        scriere = _linia_primei_executii(fn)
        if scriere is None:
            rele.append((nume, None, FARA_EXECUTIE))
            continue
        for garda in _GARZI:
            apel = _linia_primului_apel(fn, garda)
            if apel is None:
                rele.append((nume, garda, ABSENT))
            elif apel > scriere:
                rele.append((nume, garda, DUPA_SCRIERE))
    return rele


@pytest.fixture(scope="module")
def sursa():
    return io.open(os.path.join(_RAD, "main.py"), encoding="utf-8").read()


def test_ambele_rute_verifica_unicitatea_si_perioada_INAINTE_de_a_scrie(sursa):
    rele = _lipsuri(sursa)
    assert not rele, (
        "raportul Z se poate înregistra de două ori, sau într-o lună închisă:" + chr(10)
        + chr(10).join("  %s · %s · %s" % r for r in rele))


def test_unicitatea_se_cauta_in_AMANDOUA_sursele(sursa):
    """Cheia e aceeași la ruta tastată și la import. O verificare care s-ar uita într-o singură
    sursă ar lăsa un raport deja importat să fie tastat a doua oară — jumătate de poartă, care
    arată exact ca o poartă întreagă.

    Asertează pe MULȚIMEA `_SURSE_Z`, citită ca literal din AST, nu pe SQL-ul în care e folosită:
    tocmai ca să nu depindă de cum e scris interogarea."""
    arb = ast.parse(sursa)
    valori = None
    for n in ast.walk(arb):
        if isinstance(n, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "_SURSE_Z" for t in n.targets):
            valori = ast.literal_eval(n.value)
    assert valori is not None, "`_SURSE_Z` a dispărut din main.py — gardul n-are ce compara"
    assert set(valori) == {"horeca_z", "amef"}, (
        "mulțimea surselor de raport Z s-a schimbat: %s. O sursă scoasă de aici înseamnă că o "
        "notă din ea se poate dubla." % sorted(valori))


_FARA_GARDA = chr(10).join([
    "def horeca_import_amef(tenant_id, fisier, ctx=None):",
    "    with db.get_conn() as conn:",
    "        with conn.cursor() as cur:",
    "            cur.execute('INSERT INTO x.inregistrari (data, numar) VALUES (1,2)')",
    "",
    "def horeca_raport_z(tenant_id, rz, ctx=None):",
    "    with db.get_conn() as conn:",
    "        _cere_luna_deschisa(conn, 'x', rz.data)",
    "        with conn.cursor() as cur:",
    "            cur.execute('INSERT INTO x.inregistrari (data, numar) VALUES (1,2)')",
    "            _cere_z_unic(cur, 'x', 'Z-1-2')",
])


def test_CALIBRARE_gardul_prinde_lipsa_apelului_SI_ordinea_gresita():
    """Calibrare negativă pe propriul mod de eșec (interdicția 76), în ambele forme pe care le
    poate lua greșeala: apelul **absent** (prima rută) și apelul prezent, dar **după** scriere
    (a doua). A doua e forma insidioasă — codul conține numele gărzii, deci un gard care ar
    căuta numele în text ar fi trecut verde."""
    assert set(_lipsuri(_FARA_GARDA)) == {
        ("horeca_import_amef", "_cere_z_unic", ABSENT),
        ("horeca_import_amef", "_cere_luna_deschisa", ABSENT),
        ("horeca_raport_z", "_cere_z_unic", DUPA_SCRIERE),
    }, _lipsuri(_FARA_GARDA)


def test_ANTI_VACUU_rutele_chiar_se_gasesc(sursa):
    """Fără asta, o redenumire ar face gardul să treacă pe o mulțime goală."""
    lipsa = set(_RUTE) - set(_functii(sursa))
    assert not lipsa, "rute negăsite în main.py: %s — gardul s-ar uita în gol" % lipsa
