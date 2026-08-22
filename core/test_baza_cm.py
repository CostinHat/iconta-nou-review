# -*- coding: utf-8 -*-
"""GARDĂ: baza de calcul a indemnizației CM vine din statele EMISE, nu din recalcul. (22.08.2026)

DECIS DE COSTIN: **emis**. Motivul e același cu al fluturașului — ce s-a plătit efectiv e un FAPT, iar
media legală (OUG 158/2005 art.10 al.4) se face pe ce a primit omul, nu pe ce ar rezulta din calculul
de azi. Dacă între timp s-a schimbat o cotă sau salariul minim, recalculul dă alte venituri decât cele
de pe fluturașii deja dați — și indemnizația ar fi calculată pe o realitate care n-a existat.

CE ERA ÎNAINTE: `POST /calcul-cm` chema `stat_plata()` pe fiecare din cele 6 luni anterioare, adică
RECALCULA. Comentariul de acolo apăra o reparație anterioară (baza nu se mai citea din `state_plata`,
fiindcă tabelul era populat ca efect secundar al unui GET). Reparația aia era corectă atunci — tabelul
era un cache de navigare. Acum `state_plata` e un REGISTRU DE DOCUMENTE EMISE, deci sursa s-a schimbat
sub argument.

REGULA, în trei părți:
  1. o lună EMISĂ intră în bază cu cifrele EMISE, nu cu recalculul;
  2. o lună NEEMISĂ intră cu recalculul — dar se NUMĂRĂ separat și se spune, ca să nu se amestece
     tăcut două feluri de cifre;
  3. dacă nicio lună nu e emisă, comportamentul e cel de azi (recalcul integral) — nimic nu se rupe
     pentru firmele care încă nu emit.
"""
import pytest

from core import db

try:
    from core import baza_cm
except Exception:      # pragma: no cover — pe HEAD modulul nu există; garda trebuie să fie ROȘIE
    baza_cm = None

_LIPSA = pytest.mark.skipif(baza_cm is None, reason="core/baza_cm nu există")


def test_modulul_exista():
    """Roșu pe HEAD."""
    assert baza_cm is not None, (
        "core/baza_cm.py lipsește — baza indemnizației se calculează încă din recalcul, deci poate "
        "contrazice fluturașii deja dați")


# ---------------------------------------------------------------- motorul (pur)

@_LIPSA
def test_luna_emisa_intra_cu_cifrele_EMISE():
    """Miezul deciziei: ce s-a plătit e un fapt."""
    emise = {(2026, 5): {"brut": 5000.0, "cm_zile": 0}}
    recalc = {(2026, 5): {"brut": 6000.0, "cm_zile": 0}}
    r = baza_cm.aduna([(2026, 5)], emise, recalc, zile_lucratoare=lambda a, l: 21)
    assert r["venituri"] == 5000.0, "a luat recalculul peste exemplarul emis"
    assert r["luni_emise"] == 1 and r["luni_recalculate"] == 0


@_LIPSA
def test_luna_neemisa_intra_cu_recalculul_dar_se_NUMARA():
    """Două feluri de cifre în aceeași medie e o realitate, nu un defect — dar trebuie SPUS."""
    r = baza_cm.aduna([(2026, 5)], {}, {(2026, 5): {"brut": 6000.0, "cm_zile": 0}},
                      zile_lucratoare=lambda a, l: 21)
    assert r["venituri"] == 6000.0
    assert r["luni_emise"] == 0 and r["luni_recalculate"] == 1


@_LIPSA
def test_amestecul_se_declara():
    """Contabilul trebuie să poată ști pe ce s-a făcut media, nu doar cât e."""
    emise = {(2026, 4): {"brut": 5000.0, "cm_zile": 0}}
    recalc = {(2026, 4): {"brut": 9999.0, "cm_zile": 0}, (2026, 5): {"brut": 6000.0, "cm_zile": 0}}
    r = baza_cm.aduna([(2026, 4), (2026, 5)], emise, recalc, zile_lucratoare=lambda a, l: 21)
    assert r["venituri"] == 11000.0
    assert r["luni_emise"] == 1 and r["luni_recalculate"] == 1
    assert r["temei"], "baza nu spune pe ce se sprijină"
    assert "emis" in r["temei"].lower()


@_LIPSA
def test_zilele_de_CM_se_scad_din_zilele_lucratoare():
    """Regula veche, păstrată: art.10 al.4 numără zilele LUCRATE, nu calendaristice."""
    r = baza_cm.aduna([(2026, 5)], {(2026, 5): {"brut": 5000.0, "cm_zile": 5}}, {},
                      zile_lucratoare=lambda a, l: 21)
    assert r["zile"] == 16


@_LIPSA
def test_luna_fara_nicio_sursa_nu_se_inventeaza():
    """Nici emisă, nici recalculabilă — se sare, și se numără ca lipsă."""
    r = baza_cm.aduna([(2026, 5), (2026, 6)], {}, {(2026, 6): {"brut": 6000.0, "cm_zile": 0}},
                      zile_lucratoare=lambda a, l: 21)
    assert r["luni_lipsa"] == 1 and r["nr_luni"] == 1


@_LIPSA
def test_o_luna_cu_zero_zile_lucrate_nu_intra():
    """Regula veche: o lună integral în CM n-are zile lucrate, deci nu intră în medie."""
    r = baza_cm.aduna([(2026, 5)], {(2026, 5): {"brut": 5000.0, "cm_zile": 21}}, {},
                      zile_lucratoare=lambda a, l: 21)
    assert r["nr_luni"] == 0 and r["zile"] == 0


# ---------------------------------------------------------------- ruta

@_LIPSA
def test_ruta_cere_emisele():
    """DOC↔COD: ruta trebuie să treacă prin motor, nu să recalculeze pe lângă el."""
    import inspect

    import main
    sursa = inspect.getsource(main.calcul_cm_endpoint)
    assert "baza_cm" in sursa, (
        "ruta /calcul-cm nu folosește `core.baza_cm` — baza se face în continuare din recalcul")
    # Prima formă asertea DOAR că numele apare — un gard pe NUME, nu pe comportament. RED-proof-ul a
    # arătat-o: mutația care ocolea motorul trecea, fiindcă numele rămânea în sursă. Ce se interzice
    # de fapt e OCOLIREA: ruta să cheme singură recalculul lunar.
    from core import scan_ancore
    cod = scan_ancore.fara_proza(sursa, "main.py")
    assert "stat_plata(" not in cod, (
        "ruta /calcul-cm cheamă DIRECT `stat_plata()` — asta e ocolirea: recalculează lunile pe lângă "
        "`baza_cm`, care ar fi luat cifrele EMISE")
    assert "_bcm.aduna(" in cod, (
        "ruta nu mai adună prin motor — dacă suma se face altundeva, actualizează gardul")


@_LIPSA
def test_vechea_afirmatie_nu_mai_e_scrisa():
    """Comentariul din rută apăra recalculul ca fiind CORECT. Sursa s-a schimbat sub argument:
    `state_plata` nu mai e un cache de navigare, e registrul documentelor emise. Un comentariu care
    apără decizia veche e o afirmație falsă lăsată în cod."""
    import inspect

    import main
    sursa = inspect.getsource(main.calcul_cm_endpoint)
    assert "Baza se CALCULEAZA pe cele 6 luni anterioare, nu se citeste din state_plata" not in sursa, (
        "comentariul vechi încă apără recalculul — actualizează-l, altfel cine citește află altceva "
        "decât face codul")
