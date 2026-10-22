# -*- coding: utf-8 -*-
"""Lotul 11, comanda 11.1 (Costin 21.10.2026, verbatim în DECIZII „Comanda 11.1”) — subagentul P2: deficiența 444 pe celelalte drumuri care
verifică partenerul la ANAF („când numele de la ANAF diferă de fișa partenerului, se spune și se propune actualizarea”): NIR-ul
(„Verifică” lângă CUI-ul furnizorului) și casa („Verifică” lângă CUI-ul partenerului). Ecranul fișelor e în e2e_lot11_p.py.

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ (`firma_noua`, Date firmă pe drumul ecranului —
`e2e_bloc_e._completeaza`). DATE DE PORNIRE: fișa partenerului cu numele vechi, pe ruta ecranului Furnizori / Clienți (POST); răspunsul
ANAF e servit de plasă pe server (`anaf_api.CHEIE_SIMULAT`, `<dir>/anaf.json`), deci comparația fișă–ANAF rulează în aplicație.
CUI-urile 14399840 / 2864518 au cifra de control verificată (algoritmul din CLAUDE.md). Mutațiile: frontend_test/e2e/mut_lot11_p2.json."""
import json
import os

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import _card
from e2e_bloc_d import PATRON, _api

ANAF = {"14399840": {"denumire": "DANTE INTERNATIONAL SA", "platitor_tva": True, "inactiv": False},
        "2864518": {"denumire": "ALTEX ROMANIA SRL", "platitor_tva": True, "inactiv": False}}


@pytest.fixture(scope="module")
def firma_p2():
    from e2e_bloc_e import _completeaza
    for f in firma_noua():
        yield _completeaza(f, "cantitativ_valoric")


def _anaf():
    """Răspunsurile ANAF ale plasei (`anaf_api._raspuns_simulat`): {cui: rezultat}."""
    d = os.environ["ICONTA_ANAF_SIMULAT"]
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "anaf.json"), "w", encoding="utf-8") as f:
        json.dump(ANAF, f, ensure_ascii=False)


def _fisa(firma, fel, nume, cui):
    """Fișa partenerului cu numele vechi, pe ruta ecranului (Furnizori / Clienți -> rând nou -> Salvează)."""
    st, r = _api(PATRON, "POST", "/tenants/%d/%s" % (firma["tenant_id"], fel), {"nume": nume, "cui": cui})
    assert st == 200, (st, r)
    return sql('SELECT id FROM "%s".%s WHERE cui = %%s' % (firma["schema"], fel), (cui.replace("RO", ""),))[0][0]


def _verifica(pg, buton, stare):
    with pg.expect_response(lambda r: "/verifica-cui/" in r.url, timeout=30000):
        pg.click(buton)
    pg.wait_for_function("s => !(document.querySelector(s) || {innerText: 'la ANAF…'}).innerText.includes('la ANAF…')", arg=stare,
                         timeout=15000)


def test_def_444_nir_propune_actualizarea_fisei_furnizorului(patron, firma_p2):
    """444 (NIR). Pașii: fișa furnizorului „DANTE SRL” (CUI 14399840) -> Stocuri -> „+ NIR nou” -> CUI 14399840 -> „Verifică”: furnizorul
    din ANAF în formular și „Numele de la ANAF diferă: «DANTE INTERNATIONAL SA» (în fișă: «DANTE SRL»).” cu „Actualizează fișa cu numele de
    la ANAF” -> clic -> „DANTE SRL: numele din fișă e acum «DANTE INTERNATIONAL SA»”, fișa are numele de la ANAF -> „Verifică” din nou:
    nicio propunere."""
    _anaf()
    fz = _fisa(firma_p2, "furnizori", "DANTE SRL", "RO14399840")
    patron.firma(firma_p2["nume"])
    pg = patron.pg
    _card(patron, "stocuri", "#sn-toggle")
    pg.click("#sn-toggle")
    pg.wait_for_selector("#sn-numar", state="visible", timeout=10000)
    pg.fill("#sn-cui", "14399840")
    _verifica(pg, "#sn-verifica", "#sn-cui-stare")
    buton = "#sn-anaf-aplica-furnizori-%d" % fz
    pg.wait_for_selector(buton, timeout=15000)
    st = pg.inner_text("#sn-cui-stare")
    assert "Numele de la ANAF diferă: „DANTE INTERNATIONAL SA” (în fișă: „DANTE SRL”)." in st, st
    assert pg.input_value("#sn-furn") == "DANTE INTERNATIONAL SA"
    patron.captura("nir_diferit")
    pg.click(buton)
    pg.wait_for_function("() => (document.querySelector('#sn-cui-stare') || {innerText: ''}).innerText.includes('numele din fișă e acum')",
                         timeout=30000)
    assert sql('SELECT nume, cui FROM "%s".furnizori WHERE id = %%s' % firma_p2["schema"], (fz,)) == [("DANTE INTERNATIONAL SA", "14399840")]
    patron.captura("nir_actualizat")
    _verifica(pg, "#sn-verifica", "#sn-cui-stare")
    assert pg.query_selector("[id^='sn-anaf-aplica-']") is None and "diferă" not in pg.inner_text("#sn-cui-stare")


def test_def_444_casa_propune_actualizarea_fisei_clientului(patron, firma_p2):
    """444 (casă). Pașii: fișa clientului „ALTEX SRL” (CUI 2864518) -> Casa -> dispoziție nouă, „Încasare de la client”, CUI 2864518 ->
    „Verifică”: partenerul din ANAF în formular și „Numele de la ANAF diferă: «ALTEX ROMANIA SRL» (în fișă: «ALTEX SRL»).” cu „Actualizează
    fișa cu numele de la ANAF” -> clic -> „ALTEX SRL: numele din fișă e acum «ALTEX ROMANIA SRL»”, fișa are numele de la ANAF."""
    _anaf()
    cl = _fisa(firma_p2, "clienti", "ALTEX SRL", "2864518")
    patron.firma(firma_p2["nume"])
    pg = patron.pg
    _card(patron, "casa", "#c-toggle")
    pg.click("#c-toggle")
    pg.wait_for_selector("#c-cui", state="visible", timeout=10000)
    pg.select_option("#c-cat", "incasare_client")
    pg.fill("#c-cui", "2864518")
    _verifica(pg, "#c-cui-verif", "#c-cui-stare")
    buton = "#c-anaf-aplica-clienti-%d" % cl
    pg.wait_for_selector(buton, timeout=15000)
    st = pg.inner_text("#c-cui-stare")
    assert "Numele de la ANAF diferă: „ALTEX ROMANIA SRL” (în fișă: „ALTEX SRL”)." in st, st
    assert pg.input_value("#c-part") == "ALTEX ROMANIA SRL"
    patron.captura("casa_diferit")
    pg.click(buton)
    pg.wait_for_function("() => (document.querySelector('#c-cui-stare') || {innerText: ''}).innerText.includes('numele din fișă e acum')",
                         timeout=30000)
    assert sql('SELECT nume FROM "%s".clienti WHERE id = %%s' % firma_p2["schema"], (cl,)) == [("ALTEX ROMANIA SRL",)]
    patron.captura("casa_actualizat")
