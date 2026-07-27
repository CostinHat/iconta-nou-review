# -*- coding: utf-8 -*-
"""Garda: verificarea de profil nu e decorativa — daca exista, blocheaza generarea.

DE CE (27.07.2026): `d300.valideaza(res)` verifica banca/cont/CAEN/CUI de luni de zile si
NU era chemata niciodata din `genereaza()`. XML-ul iesea cu banca="" si cont="", iar ANAF il
respingea: "atribut prezent dar vid nepermis". Contabilul primea eroarea criptica a
validatorului in loc de "completeaza IBAN-ul". 2 din 3 firme reale erau in situatia asta.
d301 la fel. In schimb d100/d101/d205/d710 chemau `erori_generare(prof)` si blocau corect.

Un gard scris care nu e POARTA nu apara nimic - clasa de defect vanata toata ziua.
"""
import ast
import pathlib
import pytest

GENERATOARE = ("d100", "d101", "d205", "d300", "d301", "d710")


def _cheama(mod, nume_fn):
    src = (pathlib.Path(__file__).resolve().parent / ("%s.py" % mod)).read_text(encoding="utf-8")
    t = ast.parse(src)
    for n in ast.walk(t):
        if isinstance(n, ast.FunctionDef) and n.name == "genereaza":
            for sub in ast.walk(n):
                if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) \
                   and sub.func.id == nume_fn:
                    return True
    return False


def _defineste(mod, nume_fn):
    src = (pathlib.Path(__file__).resolve().parent / ("%s.py" % mod)).read_text(encoding="utf-8")
    return any(isinstance(n, ast.FunctionDef) and n.name == nume_fn
               for n in ast.parse(src).body)


@pytest.mark.parametrize("mod", GENERATOARE)
def test_erori_generare_e_chemata_din_genereaza(mod):
    """Daca un generator DEFINESTE erori_generare, genereaza() trebuie s-o CHEME."""
    if not _defineste(mod, "erori_generare"):
        pytest.skip("%s nu defineste erori_generare" % mod)
    assert _cheama(mod, "erori_generare"), (
        "%s defineste erori_generare dar genereaza() n-o cheama - verificarea e decorativa, "
        "iar XML-ul incomplet ajunge la ANAF" % mod)


@pytest.mark.parametrize("mod", ("d300", "d301"))
def test_profil_incomplet_opreste_generarea(mod):
    """Fara banca/cont, generarea trebuie sa se opreasca cu mesaj CITIBIL."""
    import importlib
    m = importlib.import_module("core.%s" % mod)
    prof = {"cui": "14399840", "nume": "PROBA SRL", "caen": "6202", "banca": "", "iban": ""}
    e = m.erori_generare(prof)
    assert e, "%s: profil fara banca/cont trebuie sa dea erori" % mod
    text = " ".join(e).lower()
    assert "banc" in text and ("cont" in text or "iban" in text)


@pytest.mark.parametrize("mod", ("d300", "d301"))
def test_profil_complet_trece(mod):
    import importlib
    m = importlib.import_module("core.%s" % mod)
    prof = {"cui": "14399840", "nume": "PROBA SRL", "caen": "6202",
            "banca": "ING Bank", "iban": "RO63INGB0000999910907330"}
    assert m.erori_generare(prof) == [], "%s: profil complet nu trebuie sa dea erori" % mod


def test_valideaza_nu_repeta_verificarile():
    """valideaza() cheama erori_generare, nu-si scrie propria copie (o singura sursa)."""
    for mod in ("d300", "d301"):
        src = (pathlib.Path(__file__).resolve().parent / ("%s.py" % mod)).read_text(encoding="utf-8")
        i = src.index("def valideaza(res):")
        j = src.find("\ndef ", i + 1)
        corp = src[i:j if j > 0 else len(src)]
        assert "erori_generare(prof)" in corp, "%s: valideaza nu foloseste sursa unica" % mod
        assert corp.count("LIPSĂ bancă") == 0, "%s: valideaza inca repeta verificarea bancii" % mod
