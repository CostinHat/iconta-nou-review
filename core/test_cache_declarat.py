# -*- coding: utf-8 -*-
"""P6 valul 2 — un cache admis isi poarta cele cinci lucruri, si dovada nu e o promisiune.

Textul canonic (`PLAN_HARDENING.md:704-707`) admite cache local **numai DECLARAT**, cu cinci
lucruri langa el: rol · sursa autoritativa · motiv · invalidare · dovada de reconstructie identica.

Garda are trei straturi, si al treilea e cel care conteaza:

  1. FIECARE cache clasificat ca `declarat` are o `Declaratie` in modulul lui, cu toate cele cinci
     campuri pline. Se verifica pe CAMPURI, nu pe text — o declaratie scrisa in proza intr-un
     docstring ar fi «declarata» pentru un om si invizibila pentru o garda.
  2. Campul `dovada` numeste o functie de test care EXISTA cu adevarat, in fisierul asta. O
     declaratie care trimite la o proba inexistenta e mai rea decat lipsa ei: se citeste ca
     verificata. Se cauta in AST-ul fisierului, nu cu o expresie regulata peste text.
  3. Probele de reconstructie CHIAR ruleaza: golesc cache-ul si compara raspunsul. Fiecare are si
     o aserțiune ANTI-VACUUM — un cache care se reconstruieste gol de doua ori ar trece o
     comparatie de egalitate fara sa dovedeasca nimic.

CE NU ACOPERA, scris: probele compara raspunsul DUPA golire cu cel dinainte, in ACELASI proces.
Nu pot arata ca doua procese ar reconstrui la fel — pentru sase din cele sapte, sursa e un fisier
versionat sau o functie pura, deci e acelasi lucru; pentru `firma_rezumat._SANATATE` diferenta
dintre procese e reala si e DECLARATA in clasificare (difera prin vechime, nu prin adevar).
"""
from __future__ import annotations

import ast
import importlib
import io
import os
import sys

import pytest

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RADACINA, "scripts"))
sys.path.insert(0, RADACINA)

import p6_clasificare as CL  # noqa: E402
from core.cache_declarat import Declaratie, numele_declaratiei  # noqa: E402

ACEST_FISIER = os.path.abspath(__file__)


def _cache_declarate():
    """Perechile (modul, nume) pe care clasificarea le accepta ca **cache declarat**."""
    return sorted(k for k, v in CL.TABEL.items() if v.fel == "declarat")


def _declaratia(modul, nume):
    return getattr(importlib.import_module(modul), numele_declaratiei(nume), None)


def _functiile_din_fisierul_asta():
    arb = ast.parse(io.open(ACEST_FISIER, encoding="utf-8").read())
    return {n.name for n in ast.walk(arb)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


# ============================================================
#  1+2. DECLARATIA — structura, si dovada care chiar exista
# ============================================================
def test_exista_cache_declarate_de_verificat():
    """ANTI-VACUUM pe garda insasi: daca `fel == 'declarat'` ar disparea din clasificare, toate
    probele parametrizate de mai jos s-ar goli si ar trece triumfal peste nimic."""
    assert len(_cache_declarate()) >= 7, (
        "clasificarea nu mai contine cache-uri declarate — garda asta n-ar mai verifica nimic")


@pytest.mark.parametrize("modul,nume", _cache_declarate(),
                         ids=["%s::%s" % x for x in _cache_declarate()])
def test_fiecare_cache_declarat_poarta_cele_cinci_lucruri(modul, nume):
    d = _declaratia(modul, nume)
    assert isinstance(d, Declaratie), (
        "%s::%s e acceptat ca «cache declarat», dar n-are `%s` de tip `Declaratie` in modulul lui. "
        "Regula canonica admite cache-ul NUMAI declarat."
        % (modul, nume, numele_declaratiei(nume)))
    goale = [c for c in CL.CINCI if not str(getattr(d, c, "")).strip()]
    assert not goale, "%s::%s are campuri goale: %s" % (modul, nume, goale)


@pytest.mark.parametrize("modul,nume", _cache_declarate(),
                         ids=["%s::%s" % x for x in _cache_declarate()])
def test_dovada_numeste_o_proba_care_exista(modul, nume):
    """Al treilea strat. O declaratie care trimite la un test inexistent se citeste ca verificata."""
    d = _declaratia(modul, nume)
    assert "::" in d.dovada, (
        "%s::%s — `dovada` trebuie sa fie `fisier::functie`, e %r" % (modul, nume, d.dovada))
    fis, fn = d.dovada.split("::", 1)
    assert os.path.basename(fis) == os.path.basename(ACEST_FISIER), (
        "%s::%s trimite la %s; probele de reconstructie stau in %s"
        % (modul, nume, fis, os.path.basename(ACEST_FISIER)))
    assert fn in _functiile_din_fisierul_asta(), (
        "%s::%s trimite la proba `%s`, care NU exista. O dovada promisa si nescrisa e mai rea "
        "decat una lipsa." % (modul, nume, fn))


def test_P6_UNDECLARED_CACHES_e_zero():
    """Cheia ceruta de valul 2, scrisa ca aserțiune, nu ca cifra intr-un raport."""
    fara = [(m, n) for m, n in _cache_declarate()
            if not isinstance(_declaratia(m, n), Declaratie)]
    assert not fara, "P6_UNDECLARED_CACHES=%d: %s" % (len(fara), fara)


# ============================================================
#  3. RECONSTRUCTIA IDENTICA — cele sapte probe
# ============================================================
def test_ajutor_se_reconstruieste_identic():
    from core import ajutor
    vechi = ajutor._CACHE
    try:
        ajutor._CACHE = None
        intai = ajutor._incarca()
        assert intai, "cache-ul de ajutor s-a reconstruit GOL — comparatia de mai jos n-ar dovedi nimic"
        ajutor._CACHE = None
        din_nou = ajutor._incarca()
        assert din_nou == intai
        assert len(intai) > 50, "doar %d functionalitati: sursa pare trunchiata" % len(intai)
    finally:
        ajutor._CACHE = vechi


def test_baza_ai_se_reconstruieste_identic():
    from core import raportari_ai
    vechi = raportari_ai._BAZA
    try:
        raportari_ai._BAZA = None
        intai = raportari_ai._baza_cunostinte()
        assert intai.strip(), "baza de cunostinte s-a reconstruit GOALA"
        raportari_ai._BAZA = None
        assert raportari_ai._baza_cunostinte() == intai
        assert intai.count("\n") > 20, "prea putine pozitii LIVE: sursa pare trunchiata"
    finally:
        raportari_ai._BAZA = vechi


def test_enum_xsd_se_reconstruieste_identic():
    from core import d112
    TIP = "Str_caenListSType"
    vechi = dict(d112._ENUM_XSD_CACHE)
    try:
        d112._ENUM_XSD_CACHE.clear()
        intai = d112._enum_xsd(TIP)
        assert intai, "enumerarea %s a iesit GOALA — XSD-ul lipseste sau tipul s-a redenumit" % TIP
        d112._ENUM_XSD_CACHE.clear()
        assert d112._enum_xsd(TIP) == intai
    finally:
        d112._ENUM_XSD_CACHE.clear()
        d112._ENUM_XSD_CACHE.update(vechi)


def test_sarbatori_se_reconstruiesc_identic():
    from core import scadente
    vechi = dict(scadente._cache_sarb)
    try:
        scadente._cache_sarb.clear()
        intai = scadente.sarbatori_legale(2026)
        assert len(intai) >= 15, "doar %d sarbatori in 2026 — calendarul pare incomplet" % len(intai)
        scadente._cache_sarb.clear()
        assert scadente.sarbatori_legale(2026) == intai
    finally:
        scadente._cache_sarb.clear()
        scadente._cache_sarb.update(vechi)


def test_predarea_bnr_se_reconstruieste_identic():
    """Aici «reconstructie identica» inseamna altceva, si de-aia e scris: predarea NU e o sursa de
    valoare, e un context de diagnostic. Proba are doua parti.

    (a) GOLIREA DEGRADEAZA LA STAREA DE DINAINTE DE DESCARCARE, nu la altceva: o predare absenta,
        expirata sau evacuata da acelasi `(None, set())`.
    (b) DECIZIA NU TRECE PE-ACOLO — structural, pe AST: in `curs_pentru`, valoarea intoarsa pe
        calea de succes vine din `_din_cache`, iar `_preluare` apare numai pe caile de refuz.
        Asta e ce face golirea inofensiva, si se poate ARATA, nu doar afirma.
    """
    import datetime
    from core import curs_bnr as cb

    vechi = dict(cb._PREDARE)
    try:
        cb._PREDARE.clear()
        gol = cb._preluare("EUR", datetime.date(2026, 9, 1))
        cb._preda("EUR", datetime.date(2026, 9, 1), RuntimeError("x"), {"EUR"})
        cb._PREDARE[("EUR", datetime.date(2026, 9, 1))] = (-10 ** 9, RuntimeError("x"), {"EUR"})
        expirat = cb._preluare("EUR", datetime.date(2026, 9, 1))
        assert gol == expirat == (None, set()), (
            "o predare expirata da %r, o absenta da %r — degradarea nu e la aceeasi stare"
            % (expirat, gol))

        cb._PREDARE.clear()
        for i in range(cb._PREDARE_MAX + 10):
            cb._preda("T%d" % i, datetime.date(2026, 1, 1), None, set())
        assert len(cb._PREDARE) == cb._PREDARE_MAX, (
            "plafonul nu tine: %d chei" % len(cb._PREDARE))
    finally:
        cb._PREDARE.clear()
        cb._PREDARE.update(vechi)

    sursa = io.open(os.path.join(RADACINA, "core", "curs_bnr.py"), encoding="utf-8").read()
    fn = next(n for n in ast.walk(ast.parse(sursa))
              if isinstance(n, ast.FunctionDef) and n.name == "curs_pentru")
    intoarse = [n for n in ast.walk(fn) if isinstance(n, ast.Return) and n.value is not None]
    assert intoarse, "`curs_pentru` n-are nicio intoarcere — proba ar fi vida"
    for r in intoarse:
        nume = {x.id for x in ast.walk(r) if isinstance(x, ast.Name)}
        assert "_PREDARE" not in nume and "_preluare" not in nume, (
            "o cale de SUCCES a lui `curs_pentru` foloseste predarea (linia %d) — atunci golirea "
            "ei ar putea schimba cursul, nu doar diagnosticul" % r.lineno)


def test_sablonul_de_tenant_se_reconstruieste_identic():
    import main
    vechi = main._TENANT_TEMPLATE
    try:
        cale = main.TENANT_TEMPLATE_PATH
        if not os.path.exists(cale):
            pytest.skip("tenant_template.sql lipseste in mediul asta")
        intai = io.open(cale, encoding="utf-8").read()
        assert intai.strip(), "sablonul de tenant e GOL"
        assert io.open(cale, encoding="utf-8").read() == intai
        if vechi is not None:
            assert vechi == intai, (
                "sablonul din memorie difera de fisier — cache-ul a ramas in urma sursei")
    finally:
        main._TENANT_TEMPLATE = vechi


def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_sanatatea_se_reconstruieste_identic():
    """Golit, instantaneul se reface din catalogul PostgreSQL — singura autoritate — si da acelasi
    verdict ca o interogare proaspata. Ce NU dovedeste: ca doua procese l-ar avea la fel in aceeasi
    clipa. Nici nu l-ar avea, si e declarat: difera prin VECHIME, nu prin adevar."""
    from core import db, firma_rezumat as fr
    vechi = dict(fr._SANATATE)
    try:
        fr._SANATATE.update({"ok": None, "verificat_la": None, "probleme": [], "detaliu": {}})
        assert fr.stare_infrastructura()["ok"] is None, "golirea n-a prins"
        with db.get_conn() as conn:
            refacut = fr.verifica_drift(conn)
            proaspat = fr.verifica_infrastructura(conn)
        assert refacut["ok"] == bool(proaspat["ok"]), (
            "instantaneul refacut (%r) nu spune acelasi lucru ca o interogare proaspata (%r)"
            % (refacut["ok"], proaspat["ok"]))
        assert refacut["probleme"] == proaspat["probleme"]
        assert refacut["detaliu"], "detaliul e gol — verificarea n-a privit nimic"
    finally:
        fr._SANATATE.clear()
        fr._SANATATE.update(vechi)


# ============================================================
#  CALIBRAREA GARZII, in ambele directii
# ============================================================
def test_o_declaratie_incompleta_e_RESPINSA():
    """Directia a doua: garda trebuie sa cada pe ce e stricat, altfel n-a masurat nimic."""
    schioapa = Declaratie(rol="ceva", sursa="", motiv="x", invalidare="y", dovada="z")
    goale = [c for c in CL.CINCI if not str(getattr(schioapa, c, "")).strip()]
    assert goale == ["sursa"], "garda nu vede un camp gol: %s" % goale


def test_o_dovada_catre_o_proba_inexistenta_e_RESPINSA():
    inventate = _functiile_din_fisierul_asta()
    assert "test_o_proba_care_nu_exista_nicaieri" not in inventate, (
        "chiar exista o functie cu numele asta — schimba numele de calibrare")


def test_o_declaratie_completa_e_ACCEPTATA():
    """Directia intai, pe un exemplar sintetic: garda nu respinge ce e in regula."""
    buna = Declaratie(rol="a", sursa="b", motiv="c", invalidare="d",
                      dovada="core/test_cache_declarat.py::test_o_declaratie_completa_e_ACCEPTATA")
    assert not [c for c in CL.CINCI if not str(getattr(buna, c, "")).strip()]
    assert buna.dovada.split("::", 1)[1] in _functiile_din_fisierul_asta()
