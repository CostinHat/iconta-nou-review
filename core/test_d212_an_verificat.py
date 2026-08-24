# -*- coding: utf-8 -*-
"""Fișa D212 se produce pe anul CERUT, pe plafoanele verificate ale anului — nu pe unul înghețat.

  core/test_d212_an_verificat.py

R31 + clasa R33, reparate împreună pe 24.08.2026. Ce era: `rip_api.fisa_d212` refuza orice an ≠ 2025
și folosea constanta `PLAFOANE_VENIT_2025`. Pe o instalare din august 2026, butonul «Fișa D212» nu
putea produce decât fișa anului trecut, pentru orice PFA — iar `PLAFOANE_VENIT_2026`, **verificat la
sursă pe 03.08.2026**, nu era chemat de nimeni.

CE PĂZEȘTE: că anul pleacă de la ecran, plafoanele se derivă din el, iar refuzul rămâne legat de
DOVADĂ (anii verificați la sursă), nu de o cifră scrisă o dată.

CE NU PĂZEȘTE, declarat: că plafoanele unui an din `ANI_VERIFICATI` sunt CHIAR cele din lege — aia e
verificarea 3 din Partea 0, o citire. Aici se păzește doar că lista nu se lărgește tăcut și că
motorul e chemat pe anul cerut.
"""
import ast
import io
import os

from core import d212_engine as _e
from core import rip_api as _r

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sursa(rel):
    cale = os.path.join(RAD, rel)
    assert os.path.exists(cale), "fisier inexistent: %s" % rel
    t = io.open(cale, encoding="utf-8").read()
    assert len(t) > 1000, "fisier suspect de scurt: %s — anti-vacuu" % rel
    return t


# ── comportament, nu sursă ────────────────────────────────────────────────────
def test_un_an_neverificat_se_refuza_si_refuzul_numeste_anii():
    """Se cheama FUNCTIA REALA. Refuzul cade inaintea oricarui acces la baza, deci conn=None ajunge."""
    r = _r.fisa_d212(None, "schema_inexistenta", 2027)
    assert isinstance(r, dict) and r.get("eroare"), "2027 nu mai e refuzat — plafoane neverificate"
    for an in _e.ANI_VERIFICATI:
        assert str(an) in r["eroare"], "refuzul nu numeste anii verificati (%s)" % r["eroare"]


def test_un_an_verificat_NU_se_refuza():
    """Direcția INVERSĂ, adăugată după ce RED-proof-ul a arătat că lipsea.

    Mutația `if an not in ANI_VERIFICATI:` -> `if an != 2025:` lăsa gardul VERDE: refuzul pe 2027
    trece și pe forma veche, fiindcă 2027 ≠ 2025. Deci o regresie la exact bugul reparat (fișa poate
    produce numai anul trecut) ar fi intrat nevăzută.

    Se dovedește prin faptul că execuția AJUNGE la baza de date: cu `conn=None`, un an care trece de
    poartă ridică `AttributeError` la `conn.cursor()`. Un an refuzat s-ar întoarce cu dicționarul de
    eroare, fără să atingă baza. Deci excepția e SEMNALUL că poarta a fost trecută, nu un eșec."""
    for an in _e.ANI_VERIFICATI:
        try:
            r = _r.fisa_d212(None, "schema_inexistenta", an)
        except AttributeError:
            continue
        assert False, (
            "anul %d e verificat la sursa, dar poarta il REFUZA: %r — fisa nu poate produce decat "
            "un an fix, exact defectul reparat pe 24.08.2026" % (an, r))


def test_anii_verificati_sunt_cei_cu_plafoane_la_sursa():
    assert _e.ANI_VERIFICATI == (2025, 2026), (
        "lista anilor verificati s-a schimbat — un an intra DUPA ce plafoanele lui sunt verificate la "
        "sursa si scrise in `d212_engine`, nu inainte")
    assert 2027 not in _e.ANI_VERIFICATI


def test_plafoanele_se_deriva_din_an_si_2026_difera_de_2025():
    """Daca cele doua ar coincide, legarea n-ar dovedi nimic: ar putea chema orice an."""
    p25, p26 = _e.plafoane_an(2025), _e.plafoane_an(2026)
    assert p25.cass_prag_max_sm == 60, "2025: CASS pe 60 sm"
    assert p26.cass_prag_max_sm == 72, "2026: Legea 239/2025 art.XII pct.19 urca CASS la 72 sm"
    assert p25.cass_prag_max_sm != p26.cass_prag_max_sm


def test_reperul_anului_2026_e_salariul_de_la_1_ianuarie_nu_cel_de_azi():
    """Faptul care face FALSA afirmatia «4.050 e o valoare expirata».

    Reperul D212 e salariul minim la 1 ianuarie al anului de VENIT — fix pe an. Majorarea la 4.325
    (HG 146/2026, de la 1 iulie) NU-l atinge. Deci 4.050 e corect si pentru venituri 2026, iar un gard
    care ar cere «reperul = salariul minim de azi» ar strica o valoare corecta."""
    assert _e.plafoane_an(2026).salariu_minim == 4050
    assert _e.plafoane_an(2025).salariu_minim == 4050


# ── legătura: motorul e chemat, constanta îngheţată nu mai e ──────────────────
def _identificatori(rel):
    """Numele pe care le vede INTERPRETORUL, nu cele care apar in text.

    Prima forma a aserțiunii de mai jos era `"PLAFOANE_VENIT_2025" not in sursa` si a picat pe
    propriul docstring — numele apare in explicatia lasata in `fisa_d212` despre ce era inainte. Un
    nume CITAT in proza nu e o FOLOSIRE; exact distinctia care a produs R33. Deci se citeste prin AST.
    """
    arb = ast.parse(_sursa(rel))
    nume = set()
    for n in ast.walk(arb):
        if isinstance(n, ast.Name):
            nume.add(n.id)
        elif isinstance(n, ast.Attribute):
            nume.add(n.attr)
        elif isinstance(n, ast.ImportFrom):
            nume.update(a.name for a in n.names)
    return nume


def test_api_ul_nu_mai_foloseste_o_constanta_de_an_inghetata():
    nume = _identificatori("core/rip_api.py")
    assert "PLAFOANE_VENIT_2025" not in nume, (
        "rip_api a revenit la constanta de an inghetata — fisa nu mai urmeaza anul cerut")
    assert "plafoane_an" in nume, "rip_api nu mai deriva plafoanele din anul cerut"


def test_calibrarea_pe_AST_chiar_deosebeste_proza_de_folosire():
    """Calibrare pe modul de esec al aserțiunii de mai sus: daca `_identificatori` ar cadea inapoi pe
    text, ar gasi numele din docstring si testul precedent ar fi imposibil de trecut."""
    sursa = _sursa("core/rip_api.py")
    assert "PLAFOANE_VENIT_2025" in sursa, (
        "premisa calibrarii a dispărut: numele nu mai e nici in proza, deci aserțiunea pe AST nu mai "
        "dovedeste nimic — muta calibrarea sau scoate-o")
    assert "PLAFOANE_VENIT_2025" not in _identificatori("core/rip_api.py")


def test_payloadul_poarta_anul_si_reperul():
    """P3: ecranul randeaza, nu stie. Daca cheile dispar, eticheta redevine literal in JS."""
    t = _sursa("core/rip_api.py")
    assert 'r["an"] = an' in t, "payloadul nu mai poarta anul"
    assert 'r["salariu_minim"] = p.salariu_minim' in t, "payloadul nu mai poarta reperul anului"


# ── ecranul ───────────────────────────────────────────────────────────────────
def test_ecranul_cere_anul_din_stare_si_nu_scrie_reperul():
    t = _sursa("static/js/ecrane/rip_ecran.js")
    assert "/rip/d212/${an}" in t, "ecranul nu mai cere anul din stare"
    assert "/rip/d212/2025" not in t, "anul a redevenit literal in cerere"
    assert "4.050" not in t, "reperul a redevenit literal in eticheta"
    assert "${d.an}" in t and "${bani(d.salariu_minim)}" in t, (
        "eticheta nu mai citeste anul si reperul din payload")
