# -*- coding: utf-8 -*-
"""GARD [C6, 25.08.2026]: un nomenclator se ia din NORMĂ; validatorul e constrângere, nu sursă.

Perechea gardului: `test_nomenclatoare_ancorate.py` cere ca fiecare nomenclator să fie PROBAT pe
validatorul instalat (nivel 3, constrângerea). Gardul ăsta cere ca el să fie și ANCORAT pe normă
(nivel 1–2, sursa), și ca diferența dintre cele două să fie CONSEMNATĂ, nu tăcută.

Fără el, ancorarea-pe-validator din 04.08 rămâne singura regulă, iar ea nu poate detecta cazul în
care arbitrul e mai îngust decât legea: îl copiază și trece verde.

Ce asertează, pe structură (METODA §23) - obiectele din `core/nomenclatoare.py`, nu textul
comentariilor:
  1. ce enumeră norma == ce e în cod (când norma închide lista);
  2. citatul din normă se REZOLVĂ în fișierul din corpus, la text - nu doar fișierul există;
  3. când norma e deschisă, sau când arbitrul diferă de normă, dezacordul e scris;
  4. codul trece prin arbitru (valorile din cod ⊆ ce acceptă validatorul);
  5. clichet pe câte nomenclatoare probate n-au încă ancoră de normă.
"""
import ast
import importlib
import pathlib
import re
import unicodedata

import pytest

from core import nomenclatoare as N
from core import test_nomenclatoare_ancorate as VAL

RAD = pathlib.Path(__file__).resolve().parent.parent

# Cate nomenclatoare probate pe validator n-au inca sursa normativa. Scade, nu creste. Fiecare
# coborare cere citirea normei la sursa - deci se face pe rand, nu prin copiere.
_CLICHET_FARA_NORMA = 6


def _plat(s):
    """Text comparabil: fără diacritice, fără cratime de rând, spații colapsate, minuscule.

    Corpusul e text extras din pdf: aceeași literă apare și ca `ţ` (t-sedilă, vechi) și ca `ț`
    (t-virgulă), iar rândurile sunt rupte la lățime fixă. O comparație pe octeți ar pica pe forma
    literei, nu pe conținut - adică ar fi zgomot, nu gardă."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().lower()


def _valori_din_cod(modul, nume):
    m = importlib.import_module("core." + modul)
    return frozenset(getattr(m, nume))


def _ancore():
    return sorted(N.ANCORE_NORMA.items())


def test_ancorele_acopera_cele_patru_masurate():
    """Anti-vacuu: gardul compară ceva. Dacă registrul se golește, testele de mai jos trec vid."""
    assert len(N.ANCORE_NORMA) >= 4, "registrul de ancore s-a golit - gardul de dedesubt nu mai compară nimic"
    for (modul, nume), _a in _ancore():
        assert _valori_din_cod(modul, nume), "%s.%s e gol în cod" % (modul, nume)


@pytest.mark.parametrize("cheie", [k for k in sorted(N.ANCORE_NORMA)])
def test_ce_enumera_norma_e_ce_e_in_cod(cheie):
    """Când norma ÎNCHIDE lista, codul nu poate avea altceva. Un cod în plus = o valoare pe care
    norma n-o prevede; unul în minus = o operațiune legală care nu se poate declara."""
    a = N.ANCORE_NORMA[cheie]
    if a.enumerare is None:
        pytest.skip("norma nu închide lista (deschis=True) - se verifică prin dezacord, nu prin egalitate")
    in_cod = _valori_din_cod(*cheie)
    assert a.enumerare == in_cod, (
        "%s.%s diferă de ce enumeră norma %s:%s  în plus în cod: %s%s  lipsă din cod: %s"
        % (cheie[0], cheie[1], a.norma, chr(10), sorted(in_cod - a.enumerare), chr(10),
           sorted(a.enumerare - in_cod)))


@pytest.mark.parametrize("cheie", [k for k in sorted(N.ANCORE_NORMA)])
def test_citatul_din_norma_se_rezolva_in_corpus(cheie):
    """O citare care nu se poate deschide nu e o sursă, e o amintire. Aici se citește FIȘIERUL și se
    caută fraza - exact verificarea 3 din PLAN_ARHITECTURA („actul chiar conține ce îi atribui")."""
    a = N.ANCORE_NORMA[cheie]
    t = a.norma
    assert t.url, "%s.%s: norma n-are url spre corpus" % cheie
    assert t.text_citat, "%s.%s: norma n-are text_citat (proba verificării)" % cheie
    assert t.nivel_sursa == "MO", (
        "%s.%s: sursa unui nomenclator trebuie să fie de nivel MO, nu %r" % (cheie[0], cheie[1], t.nivel_sursa))
    p = RAD / t.url
    assert p.exists(), "%s.%s: %s nu există în corpus" % (cheie[0], cheie[1], t.url)
    corp = _plat(p.read_text(encoding="utf-8", errors="replace"))
    assert len(corp) > 500, "%s: fișier de corpus gol sau ilizibil" % t.url
    assert _plat(t.text_citat) in corp, (
        "%s.%s: citatul NU se găsește în %s:%s  %r" % (cheie[0], cheie[1], t.url, chr(10), t.text_citat))


@pytest.mark.parametrize("cheie", [k for k in sorted(N.ANCORE_NORMA)])
def test_dezacordul_cu_arbitrul_e_scris_nu_tacut(cheie):
    """Regula lui Costin, mecanizată: dacă norma e deschisă (arbitrul închide în locul ei) sau dacă
    arbitrul acceptă altceva decât enumeră norma, ALEGEREA nu se face tăcut - se consemnează."""
    a = N.ANCORE_NORMA[cheie]
    c = a.constrangere
    assert c and c.instrument and c.proba, "%s.%s: constrângerea arbitrului nu e declarată" % cheie
    trebuie = a.deschis or (a.enumerare is not None and a.enumerare != c.valori)
    if not trebuie:
        return
    d = a.dezacord
    assert d is not None, (
        "%s.%s: norma e deschisă sau diferă de arbitru, deci închiderea e o DECIZIE - scrie dezacordul"
        % cheie)
    # Legătura cu arbitrul se asertează prin IDENTITATE, nu căutând numele lui în proză: un nume
    # într-un text apare și când dezacordul e copiat de la alt nomenclator (METODA §23).
    assert d.cine is c, "%s.%s: dezacordul e legat de altă constrângere decât a lui" % cheie
    assert len(d.ce) > 60, "%s.%s: dezacordul nu spune în ce constă" % cheie
    assert len(d.consecinta) > 60, (
        "%s.%s: dezacordul nu spune CE NU SE POATE FACE din cauza lui - partea care contează" % cheie)


@pytest.mark.parametrize("cheie", [k for k in sorted(N.ANCORE_NORMA)])
def test_codul_trece_prin_arbitru(cheie):
    """Sursa e norma, dar depunerea trece prin validator: ce e în cod trebuie să fie acceptat de el.
    O valoare din cod pe care arbitrul o respinge = declarație respinsă la depunere."""
    a = N.ANCORE_NORMA[cheie]
    in_cod = _valori_din_cod(*cheie)
    respinse = sorted(in_cod - a.constrangere.valori)
    assert not respinse, (
        "%s.%s conține valori pe care %s le respinge: %s" % (cheie[0], cheie[1], a.constrangere.instrument, respinse))


def test_clichet_nomenclatoare_fara_ancora_de_norma():
    """Câte nomenclatoare probate pe validator n-au încă sursă normativă. Scade, nu crește.

    Nu e un xfail deghizat: cele rămase SUNT ancorate pe arbitru (deci depunerea merge), dar nimeni
    n-a citit norma pentru ele. Clichetul spune cifra în loc s-o lase în proză."""
    fara = sorted(k for k in VAL.ANCORE if k not in N.ANCORE_NORMA)
    assert len(fara) <= _CLICHET_FARA_NORMA, (
        "au apărut nomenclatoare fără ancoră de normă (clichet %d, acum %d): %s"
        % (_CLICHET_FARA_NORMA, len(fara), fara))
    assert len(fara) == _CLICHET_FARA_NORMA, (
        "clichetul e depășit - coboară-l la %d" % len(fara))


def test_calibrare_citat_inventat_PICA():
    """Direcția 1 de eșec (METODA §22): gardul trebuie să respingă o citare care nu e în corpus.
    Fără proba asta, `text_citat` ar putea fi orice - iar gardul ar certifica o sursă inexistentă."""
    p = RAD / "anaf_surse/opanaf_705_2020_d390.txt"
    corp = _plat(p.read_text(encoding="utf-8", errors="replace"))
    assert _plat("nomenclatorul de tipuri se stabileşte prin decizie a validatorului") not in corp


def test_calibrare_deschis_fara_dezacord_PICA():
    """Direcția 2: gardul trebuie să respingă o normă deschisă închisă tăcut. Se construiește o
    ancoră falsă în memorie și se cere ca regula să o refuze - nu se atinge registrul real."""
    real = N.ANCORE_NORMA[("d301", "VALUTE")]
    falsa = N.Ancora(norma=real.norma, enumerare=None, deschis=True,
                     constrangere=real.constrangere, dezacord=None)
    trebuie = falsa.deschis or (falsa.enumerare is not None and falsa.enumerare != falsa.constrangere.valori)
    assert trebuie and falsa.dezacord is None, "calibrarea nu mai construiește cazul pe care gardul trebuie să-l prindă"
    # și a doua direcție: un dezacord legat de ALT arbitru trebuie să pice pe identitate
    strain = N.Dezacord(N.ANCORE_NORMA[("d390", "TIPURI")].constrangere, "x" * 70, "y" * 70)
    assert strain.cine is not real.constrangere


def test_enumerarea_nu_e_copiata_din_constrangere():
    """Modul de eșec PROPRIU al instrumentului ăstuia (interdicția 76): dacă `enumerare` s-ar
    completa copiind `constrangere.valori`, gardul ar trece verde afirmând că norma spune ce spune
    validatorul - exact inversarea pe care o repară. Nu se poate proba din date (valorile COINCID
    legitim la d390/d394), deci se probează pe SURSĂ: fiecare `enumerare` scrisă are, în fișierul
    registrului, un citat propriu din normă în vecinătatea ei."""
    src = (RAD / "core" / "nomenclatoare.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    cu_enumerare = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Ancora":
            kw = {k.arg: k.value for k in node.keywords}
            e = kw.get("enumerare")
            if e is not None and not (isinstance(e, ast.Constant) and e.value is None):
                cu_enumerare.append(node)
    assert cu_enumerare, "nicio ancoră cu enumerare - testul ar trece vid"
    for node in cu_enumerare:
        kw = {k.arg: k.value for k in node.keywords}
        norma = kw.get("norma")
        assert isinstance(norma, ast.Call), "ancoră cu enumerare fără Temei propriu"
        tc = next((k.value for k in norma.keywords if k.arg == "text_citat"), None)
        assert isinstance(tc, ast.Constant) and len(tc.value) > 20, (
            "o enumerare fără citat verbatim propriu e o copiere, nu o citire")
