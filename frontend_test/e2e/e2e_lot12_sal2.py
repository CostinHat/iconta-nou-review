# -*- coding: utf-8 -*-
"""Lotul 12, comanda 12.2 — pachetul sal2: C102.1 (propunerea zilelor de concediu medical și avertismentul peste interval), 629 (treapta
deducerii personale în luna cu concediu medical), C165 (starea notei de salarii citită din notă). Pașii contabilului pe aplicația din
index, pe baza de TEST: Salariați -> statul lunii trecute -> „Concediu” -> „+ Certificat nou”; „Compoziția netului”; Declarații -> D112;
„Contabilizează statul”.

Date de pornire: fiecare test își face firma sintetică și salariatul pe ruta salariaților (`e2e_lot11_s9._firma_cu_salariat`). Nota de
salarii (C165) se scrie și se validează pe rutele aplicației, ca patron (validator: nota nu intră în coada de validare). Nicio inserare
directă în bază. CNP-urile au cifra de control calculată (`e2e_bloc_b._cnp`)."""
import datetime

import pytest

from conftest import _scoate_firmele_e2e, sql
from e2e_bloc_d import LUNA_TRECUTA, PATRON, _api
from e2e_bloc_d import _stat as _stat_luna
from e2e_lot13_sal_ajutor import alege
from e2e_lot11_s9 import (_F, _concedii, _compozitie, _d112_xml, _firma_cu_salariat, _propunerea_zilelor, _randuri_compozitie, _singurul,
                          _un)


def _zile_lucratoare(de, pana):
    st, r = _api(PATRON, "GET", "/util/zile-lucratoare?start=%s&end=%s" % (de.isoformat(), pana.isoformat()))
    assert st == 200, (st, r)
    return int(r["zile"])


def _formular_nou(patron, firma):
    pg = patron.pg
    _stat_luna(patron, firma, luni_inapoi=1)
    _concedii(patron)   # [lotul 13] fereastra salariatului -> „Concediu medical”
    pg.wait_for_selector(_F + "#cm-nou", timeout=20000)
    pg.click(_F + "#cm-nou")
    pg.wait_for_selector(_F + "#cm-calc", timeout=20000)
    return pg


def _o_saptamana():
    """Luni–duminică din luna trecută (prima săptămână întreagă): 7 zile calendaristice."""
    d = LUNA_TRECUTA
    while d.weekday() != 0:
        d += datetime.timedelta(days=1)
    return d, d + datetime.timedelta(days=6)


# ── C102.1 — propunerea zilelor și avertismentul ────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def firma_c102():
    f = _firma_cu_salariat("S2Z")
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def test_def_c102_1_propunerea_revine_cand_campul_e_gol(patron, firma_c102):
    """C102.1. Pașii: „+ Certificat nou” -> „Început” luni, „Sfârșit” vineri -> „Zile lucrătoare CM” propune zilele intervalului -> contabilul
    scrie 3, apoi golește câmpul -> „Sfârșit” duminică -> propunerea revine (zilele intervalului); scrie 4 -> „Sfârșit” vineri -> câmpul
    rămâne 4 (cifra omului). Înainte (lotul 11): după orice tastă în câmp, chiar golit, propunerea nu mai venea, „la orice interval”."""
    de, pana = _o_saptamana()
    vineri = de + datetime.timedelta(days=4)
    z_vineri, z_duminica = _zile_lucratoare(de, vineri), _zile_lucratoare(de, pana)
    assert z_vineri == z_duminica and z_vineri >= 1, (z_vineri, z_duminica)
    pg = _formular_nou(patron, firma_c102)
    pg.fill(_F + "#cm-inceput", de.isoformat())
    pg.fill(_F + "#cm-sfarsit", vineri.isoformat())
    _propunerea_zilelor(pg, z_vineri)
    pg.fill(_F + "#cm-zile", "3")
    pg.fill(_F + "#cm-zile", "")
    pg.fill(_F + "#cm-sfarsit", pana.isoformat())
    _propunerea_zilelor(pg, z_duminica)      # câmpul gol primește din nou propunerea
    patron.captura("propunerea_revine")
    pg.fill(_F + "#cm-zile", "4")
    pg.fill(_F + "#cm-sfarsit", vineri.isoformat())
    pg.wait_for_timeout(1500)               # răspunsul serverului pentru noul interval a sosit
    assert pg.input_value(_F + "#cm-zile") == "4", pg.input_value(_F + "#cm-zile")
    pg.click(_F + "#cm-renunta")


def test_def_c102_1_zile_peste_interval_avertisment_si_confirmare(patron, firma_c102):
    """C102.1. Pașii: „+ Certificat nou” -> luni–duminică din luna trecută (5 zile lucrătoare) -> „Zile lucrătoare CM” = 10 -> lângă câmp:
    „… sunt 5 zile lucrătoare (fără weekend și sărbători legale), iar aici scrie 10 zile. Verifică cifra de pe certificat.” -> restul
    certificatului -> „Calculează și salvează”: întrebarea „Ai scris 10 zile lucrătoare … Salvezi certificatul cu 10 zile?”, nimic salvat
    -> „Corectez zilele”: tot nimic -> „Calculează și salvează” -> „Salvează cu 10 zile”: certificatul e în listă, cu 10 zile. Înainte:
    10 zile pe 5 lucrătoare se salvau fără niciun cuvânt."""
    de, pana = _o_saptamana()
    zi = _zile_lucratoare(de, pana)
    assert zi == 5, zi   # premisa: săptămâna întreagă fără sărbătoare legală
    pg = _formular_nou(patron, firma_c102)
    pg.fill(_F + "#cm-serie", "AB")
    pg.fill(_F + "#cm-numar", "1021")
    pg.select_option(_F + "#cm-cod", "01")
    pg.fill(_F + "#cm-acord", de.isoformat())
    pg.fill(_F + "#cm-inceput", de.isoformat())
    pg.fill(_F + "#cm-sfarsit", pana.isoformat())
    _propunerea_zilelor(pg, zi)
    pg.fill(_F + "#cm-zile", "10")
    pg.wait_for_function("() => (document.querySelector(%r) || {}).textContent.includes('iar aici scrie 10 zile')" % (_F + "#cm-zile-avert"),
                         timeout=10000)
    av = pg.inner_text(_F + "#cm-zile-avert")
    assert "sunt 5 zile lucrătoare (fără weekend și sărbători legale), iar aici scrie 10 zile. Verifică cifra de pe certificat." in av, av
    for sel in ("#cm-continuare", "#cm-spital", "#cm-program-national"):
        alege(patron, sel.lstrip("#"), "false")   # [lotul 13, 676] Da / Nu = butoane
    pg.fill(_F + "#cm-ven6", "30000")
    pg.fill(_F + "#cm-zile6", "125")
    patron.captura("avertisment_zile")
    pg.click(_F + "#cm-calc")
    pg.wait_for_selector("#caseta-atentie-activa", timeout=20000)
    intrebare = pg.inner_text("#caseta-atentie-activa")
    patron.captura("intrebarea_la_salvare")
    assert "Ai scris 10 zile lucrătoare de concediu medical" in intrebare and "sunt 5 zile lucrătoare" in intrebare, intrebare
    assert "Salvezi certificatul cu 10 zile?" in intrebare, intrebare
    schema = firma_c102["schema"]
    assert sql('SELECT count(*) FROM "%s".concedii_medicale' % schema) == [(0,)]
    pg.click("#caseta-atentie-activa #ca-nu")
    assert sql('SELECT count(*) FROM "%s".concedii_medicale' % schema) == [(0,)]
    pg.click(_F + "#cm-calc")
    pg.wait_for_selector("#caseta-atentie-activa #ca-ok", timeout=20000)
    assert pg.inner_text("#caseta-atentie-activa #ca-ok") == "Salvează cu 10 zile"
    pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_selector(_F + "#cm-rezultat .panou", timeout=30000)
    lista = pg.inner_text(_F + ".pf-lista")
    patron.captura("certificat_salvat_cu_10_zile")
    assert "10 zile" in lista, lista
    assert sql('SELECT zile FROM "%s".concedii_medicale' % schema) == [(10,)]


# ── 629 — treapta deducerii pe salariu + indemnizația CM ─────────────────────────────────────────────────────────────────────
@pytest.fixture
def firma_629():
    f = _firma_cu_salariat("S2D", salariu_brut=7000)
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def test_def_629_treapta_deducerii_cu_indemnizatia_cm(patron, firma_629):
    """629. Pașii: salariat cu 7.000 lei -> statul lunii trecute -> „Concediu” -> „+ Certificat nou”: cod 01, 1–10 ale lunii trecute, media
    240 lei/zi -> „Calculează și salvează” -> statul, „Compoziția netului”: deducerea personală = treapta lui „Salariu brut” + „din
    indemnizația CM brută” -> Declarații -> D112: „fără erori”, E3_121 = aceeași deducere, „Total venit brut” (E3_8) = salariul realizat +
    indemnizația (B4_7). Înainte (Costin, F5 Ionescu 10/2026): treapta pe salariul lucrat (4.815,34) fără indemnizația de 262 lei.
    Temeiul: CF art.76 alin.(1) („inclusiv indemnizațiile pentru incapacitate temporară de muncă”), CF art.77 alin.(3)-(4) („venituri
    brute lunare din salarii”), HG 1/2016 Titlul IV pct.13 alin.(1); OPANAF 605/2026 anexa 2, E.3 rândul 8 „Total venit brut”."""
    from decimal import Decimal
    from core import salarizare
    from e2e_lot12_ctrl_d112 import _certificat_01
    _certificat_01(patron, firma_629, 10, "6291")
    _stat_luna(patron, firma_629, luni_inapoi=1)
    comp = _randuri_compozitie(_compozitie(patron))
    patron.captura("compozitia_netului")
    brut, cm = comp["Salariu pe zile lucrate"], comp["Indemnizație concediu medical"]   # [lotul 13, 677] coloana „Venituri”
    ded = comp["în calculul impozitului, scade baza (nu se reține): deducere personală"]
    # CF art.77 alin.(4): treapta pe „venituri brute lunare din salarii” = salariul + indemnizația impozabilă (CF art.76 alin.(1))
    asteptat = salarizare.deducere_personala(brut + cm, la_data=LUNA_TRECUTA)["total"]
    assert asteptat != salarizare.deducere_personala(brut, la_data=LUNA_TRECUTA)["total"], (brut, cm)   # premisa: cazul mută treapta
    assert ded == asteptat, (ded, asteptat, comp)
    a = _singurul(_d112_xml(patron, firma_629))
    e3, b4 = _un(a, "asiguratE3"), _un(a, "asiguratB4")
    assert Decimal(e3["E3_121"]) == asteptat, (e3, asteptat)
    assert int(e3["E3_8"]) == int(b4["B4_7"]), (e3, b4)   # OPANAF 605/2026 anexa 2, E.3 rândul 8: venitul brut REALIZAT


# ── C165 — „Contabilizează statul”: starea notei din notă ────────────────────────────────────────────────────────────────────
@pytest.fixture
def firma_c165():
    f = _firma_cu_salariat("S2N")
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def test_def_c165_nota_validata_direct_nu_e_aratata_ciorna(patron, firma_c165):
    """C165. Pașii: statul lunii trecute -> nota de salarii scrisă și validată (patronul are drept de validare: nota nu trece prin coadă)
    -> Salariați -> statul lunii trecute -> „Contabilizează statul”: „Nota … e validată.”, fără „ciornă”. Înainte (F1, nota 6, 09/2026):
    „Nota există deja în jurnal (…, ciornă).” — starea venea numai din coada de validare."""
    tid = firma_c165["tenant_id"]
    q = "?an=%d&luna=%d" % (LUNA_TRECUTA.year, LUNA_TRECUTA.month)
    st, r = _api(PATRON, "POST", "/tenants/%d/salarii-contare%s" % (tid, q), {})
    assert st == 200 and r.get("nota_id"), (st, r)
    nota = r["nota_id"]
    st, v = _api(PATRON, "POST", "/tenants/%d/jurnal/%d/valideaza" % (tid, nota))
    assert st == 200, (st, v)
    assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % firma_c165["schema"], (nota,)) == [("validata",)]
    assert sql("SELECT count(*) FROM public.declaratii_coada WHERE tenant_id = %s AND fel = 'nota'", (tid,)) == [(0,)]   # premisa
    pg = patron.pg
    _stat_luna(patron, firma_c165, luni_inapoi=1)
    pg.click(_F + "#sp-contare")
    pg.wait_for_function("() => { const z = document.querySelector(%r); return z && !z.innerText.includes('Se calculează') "
                         "&& z.innerText.trim() !== ''; }" % (_F + "#sp-contare-zona"), timeout=30000)
    zona = pg.inner_text(_F + "#sp-contare-zona")
    patron.captura("nota_validata")
    assert "e validată." in zona, zona
    assert "ciornă" not in zona and "Nota există deja în jurnal" not in zona, zona
    assert pg.locator(_F + "#sp-contare-scrie").count() == 0, zona
