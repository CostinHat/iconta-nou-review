# -*- coding: utf-8 -*-
"""GARD PESTE GĂRZI — o gardă asertează pe STRUCTURĂ, nu pe text.

Regula, dată de Costin 24.08.2026. Motivul, cu instanțele — trei într-o singură zi, toate de forma
„caut un șir în ceva", toate în gărzi scrise de mine în tura asta:

  1. două aserțiuni din `test_registru_jurnal_14_1_1` găseau `nr_curent` și `note_fara_document` în
     **docstringul rutei, scris de mine** — gardul trecea verde fără ca ruta să producă ceva;
  2. curățarea de docstring, la prima formă, ștergea și **SQL-ul din același f-string**, iar gardul
     acuza fals că numerotarea dispăruse — deci greșea în **ambele** direcții (METODA §22);
  3. a treia a fost **auto-referențială**: gardul citea documentația lucrului pe care îl păzea.

CE FACE IMPOSIBIL: ca numărul gărzilor care asertează pe text să **crească**. Cele existente nu se
repară azi — sunt 50 și ar fi o tură întreagă. Dar o gardă nouă pe șir e o **regresie**, nu un
compromis, iar clichetul o oprește la poartă.

CE NU VERIFICĂ, declarat: dacă o gardă din cele 51 e *corectă* pe fondul ei. Clichetul numără forma,
nu adevărul. Și nu vede o gardă care caută cu `re.search` în loc de `in`, nici una care primește
sursa printr-un helper fără literal cu extensie — vezi cele două direcții de eșec din antetul
scanului. De aceea cifra e **plafon inferior**, și se scrie ca atare.
"""
import io
import os

import pytest

from core import scan_garzi_pe_text as _s

# MĂSURAT 24.08.2026, nu estimat: din 397 de fișiere-gardă, 78 ating o sursă `.py`/`.js` și o caută
# cu `in`; **27 o curăță de proză** înainte, **50 nu** (era 51; gardul jurnalului a fost reparat chiar în tura asta). Clichet: nu poate CREȘTE.
#
# DE CE NU 13: interdicția 18 spunea 14 (una exclusă prin natura ei), măsurat ad-hoc pe 22.08 pe 369
# de fișiere. Măsurătoarea aia n-a lăsat niciun instrument în urmă, deci nu se poate recalcula. 51 e
# aceeași clasă, măsurată pe un domeniu declarat și reproductibil — nu o creștere a defectelor.
CLICHET_PE_TEXT = 50


@pytest.fixture(scope="module")
def inv():
    return _s.inventar()


def test_numarul_garzilor_pe_text_nu_creste(inv):
    """Miezul. Clichet pe FORMĂ: cele 51 rămân, dar a 52-a nu intră."""
    pe_text = [c for c, s in inv if s == "text_brut"]
    assert len(pe_text) <= CLICHET_PE_TEXT, (
        "gărzi care asertează pe text brut: %d > %d. O gardă nouă care caută un șir într-un fișier "
        "sursă păzește proza de lângă lucru, nu lucrul. Asertează pe structură — câmp de JSON, "
        "element de XML, nod de AST — sau scrie lângă gardă de ce nu se poate.\n%s"
        % (len(pe_text), CLICHET_PE_TEXT, "\n".join("  " + c for c in sorted(pe_text))))


def test_clichetul_nu_ramane_umflat(inv):
    """Dacă cineva repară gărzi, clichetul coboară — altfel numărul devine loc gol în care încap
    regresii tăcute. Aceeași disciplină ca la clichetul de constante nesursate."""
    pe_text = [c for c, s in inv if s == "text_brut"]
    assert len(pe_text) >= CLICHET_PE_TEXT - 2, (
        "au fost reparate gărzi (%d < %d): coboară CLICHET_PE_TEXT, altfel rămâne loc de regresie"
        % (len(pe_text), CLICHET_PE_TEXT))


def test_anti_vacuu_domeniul_chiar_se_vede(inv):
    """Un scan cu domeniul greșit raportează verde despre o lume pe care n-o vede."""
    assert len(inv) >= 60, "scanul vede doar %d fișiere în clasă — domeniul s-a rupt" % len(inv)
    assert any(s == "structura" for _c, s in inv), (
        "niciun fișier nu apare ca `structura` — detectorul de curățare s-a rupt și ar acuza tot")


# ── calibrare, AMBELE direcții (METODA §22) ──────────────────────────────────
def _scrie(tmp_path, nume, cod):
    d = tmp_path / "core"
    d.mkdir(exist_ok=True)
    p = d / nume
    io.open(str(p), "w", encoding="utf-8").write(cod)
    return str(tmp_path)


def test_CALIBRARE_POZITIVA_o_garda_pe_text_e_prinsa(tmp_path):
    """Direcția „ratează": un caz construit pe care instrumentul TREBUIE să-l vadă."""
    rad = _scrie(tmp_path, "test_fals.py", (
        "import io\n"
        "def test_x():\n"
        "    t = io.open('static/js/ecrane/cabinet.js').read()\n"
        "    assert 'pct-verde' in t\n"))
    assert _s.pe_text([os.path.join(rad, "core")]), (
        "instrumentul RATEAZĂ o gardă care citește un .js și caută un șir în el — exact clasa")


def test_CALIBRARE_NEGATIVA_o_garda_pe_AST_nu_e_acuzata(tmp_path):
    """Direcția „revendică": un caz construit pe care instrumentul NU are voie să-l vadă.

    Fără testul ăsta, clichetul ar putea fi trecut mutând codul, nu reparându-l."""
    rad = _scrie(tmp_path, "test_bun.py", (
        "import ast, io\n"
        "def test_x():\n"
        "    a = ast.parse(io.open('core/d212_engine.py').read())\n"
        "    nume = {n.id for n in ast.walk(a) if isinstance(n, ast.Name)}\n"
        "    assert 'ANI_VERIFICATI' in nume\n"))
    assert not _s.pe_text([os.path.join(rad, "core")]), (
        "instrumentul ACUZĂ o gardă care parsează AST-ul — ar cere reparație unde nu e defect")


def test_CALIBRARE_NEGATIVA_o_garda_pe_JSON_nu_intra_in_clasa(tmp_path):
    """A doua direcție de revendicare: fișierele care nu ating deloc o sursă `.py`/`.js` n-au ce
    căuta în clasă, oricâte `in` ar avea."""
    rad = _scrie(tmp_path, "test_json.py", (
        "import io, json\n"
        "def test_x():\n"
        "    d = json.loads(io.open('anaf_surse/INDEX.json').read())\n"
        "    assert 'fisiere' in d\n"))
    assert not _s.pe_text([os.path.join(rad, "core")]), (
        "un gard pe JSON e numărat ca gard pe sursă — domeniul instrumentului e greșit")
