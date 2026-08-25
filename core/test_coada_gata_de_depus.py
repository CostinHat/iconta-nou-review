# -*- coding: utf-8 -*-
"""GARD [R41 partea II]: «gata de depus» are O SINGURĂ definiție, iar lista o poartă.

Defectul reparat la R41 a fost că ecranul își alegea singur populația listei „De depus",
iar serverul avea altă regulă. Reparația nu e „am schimbat eticheta" — e că **nu mai
există două condiții**: `_poarta_verdict` (care refuză depunerea) și `lista_coada` (care
alimentează ecranul) cheamă amândouă `gata_de_depus`.

Testul ăsta ține exact asta, **pe structură, nu pe text** (METODA §23): se citește AST-ul
lui `coada_api` și se verifică cine cheamă ce. O a doua condiție scrisă inline în poartă
ar trece orice grep, dar pică aici.

Ce NU ține: că ecranul o folosește corect. Aia e o proprietate de randare, probată
comportamental cu `frontend_test/proba_r41_coada.py` (Playwright, desktop + mobil).
"""
import ast
import os

import pytest

from core import coada_api

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_RAD, "core", "coada_api.py")


def _fn(nume):
    arb = ast.parse(open(_SRC, encoding="utf-8").read())
    for n in ast.walk(arb):
        if isinstance(n, ast.FunctionDef) and n.name == nume:
            return n
    raise AssertionError("funcția `%s` a dispărut din core/coada_api.py" % nume)


def _cheama(fn, nume):
    return any(isinstance(n, ast.Call)
               and (getattr(n.func, "id", None) or getattr(n.func, "attr", None)) == nume
               for n in ast.walk(fn))


# ---------- cele patru stări, ca date ----------
AMP = coada_api.amprenta_xml("<x/>")
CAZURI = [
    ("lipsă",            (None, None, None, None, None, "<x/>"),        "lipsa", False),
    ("stătut",           ("valid", None, "alta-amprenta", None, "v1", "<x/>"), "statut", False),
    ("proaspăt, valid",  ("valid", None, AMP, None, "v1", "<x/>"),      "proaspat", True),
    ("proaspăt, erori",  ("erori", "E1", AMP, None, "v1", "<x/>"),      "proaspat", False),
]


@pytest.mark.parametrize("nume,rand,stare,gata", CAZURI, ids=[c[0] for c in CAZURI])
def test_cele_patru_stari(nume, rand, stare, gata):
    st = coada_api.verdict_din_rand(*rand)
    assert st["stare"] == stare, "%s: starea calculată e %r" % (nume, st["stare"])
    assert coada_api.gata_de_depus(st) is gata, (
        "%s: `gata_de_depus` a răspuns %r" % (nume, coada_api.gata_de_depus(st)))


def test_statutul_nu_e_favorabil():
    """P6: necunoscutul domină favorabilul. Un verdict `valid` pe ALT conținut nu ține locul
    unuia proaspăt — altfel o regenerare tăcută ar păstra un verde care nu mai e despre nimic."""
    st = coada_api.verdict_din_rand("valid", None, "amprenta-veche", None, "v1", "<altceva/>")
    assert st["stare"] == "statut"
    assert coada_api.gata_de_depus(st) is False
    assert st.get("motiv"), "starea stătută trebuie să spună DE CE"
    assert st.get("actiune"), "starea stătută trebuie să spună PE UNDE se iese"


def test_poarta_si_lista_folosesc_ACEEASI_functie():
    """Inima gardului, pe STRUCTURĂ: ambele o cheamă pe `gata_de_depus`. O condiție rescrisă
    inline în poartă (`st["stare"] == "proaspat" and ...`) ar arăta identic la citire și ar
    putea diverge tăcut de ce vede omul pe ecran."""
    assert _cheama(_fn("_poarta_verdict"), "gata_de_depus"), (
        "`_poarta_verdict` nu mai cheamă `gata_de_depus` — dacă are condiția proprie, poarta "
        "și ecranul pot ajunge să spună lucruri diferite despre aceeași declarație")
    assert _cheama(_fn("lista_coada"), "gata_de_depus"), (
        "`lista_coada` nu mai cheamă `gata_de_depus` — ecranul își recalculează populația")
    assert _cheama(_fn("lista_coada"), "verdict_din_rand"), (
        "`lista_coada` nu mai calculează starea verdictului — ecranul rămâne fără ce afișa")


def test_lista_NU_scoate_xml_ul_din_baza():
    """XML-ul e citit ca să se calculeze amprenta, dar nu are ce căuta în răspuns: lista se
    cere la fiecare randare, iar un XML de declarație e de ordinul zecilor de kiloocteți.

    Asertat pe NODUL de apel `…pop("_xml")`, nu pe sursa ca text (METODA §23). Prima formă a
    testului ăstuia căuta un șir în `ast.unparse` — exact clasa pe care fișierul o predică,
    și a fost prinsă de `test_garzi_pe_text` în chiar commitul ei."""
    fn = _fn("lista_coada")
    popuri = [n for n in ast.walk(fn)
              if isinstance(n, ast.Call)
              and getattr(n.func, "attr", None) == "pop"
              and n.args and isinstance(n.args[0], ast.Constant)]
    chei = sorted(c.args[0].value for c in popuri)
    # egalitate pe valorile extrase, nu `"sir" in ceva`: forma din urma e chiar ce numara
    # `test_garzi_pe_text`, si l-ar face sa creasca dintr-un test care asertează pe AST
    assert any(k == "_xml" for k in chei), (
        "XML-ul nu mai e SCOS din dicționarul întors (`pop` pe chei: %s) — ajunge la ecran "
        "degeaba, la fiecare randare a cozii" % chei)


def test_calibrare_negativa_functia_chiar_discrimineaza():
    """Direcția «raportează favorabil pe orice»: dacă `gata_de_depus` ar întoarce mereu True,
    testele de mai sus ar trece la fel de bine pe un instrument rupt. Aici se verifică chiar
    că răspunde DIFERIT pe cele patru cazuri — altfel n-ar separa nimic."""
    raspunsuri = {coada_api.gata_de_depus(coada_api.verdict_din_rand(*rand))
                  for _, rand, _, _ in CAZURI}
    assert raspunsuri == {True, False}, (
        "`gata_de_depus` dă același răspuns pe toate cele patru stări (%r) — nu discriminează"
        % raspunsuri)
