# -*- coding: utf-8 -*-
"""Lotul 13, comanda Costin 13.1, deficiența 595 — înregistrarea în regimul special OSS se întreabă în DATE FIRMĂ, nu în formularul D398
(decizia Costin 26.10.2026, verbatim în DECIZII: „6 da” la propunerea „595 — înregistrarea OSS se întreabă în Date firmă, nu în formularul
D398”). Pașii contabilului pe aplicația din index, pe baza de TEST, pe firmă NOUĂ (`firma_noua`).

DATE DE PORNIRE fără ecran (declarate, `# date-de-pornire` pe linie): Date firmă și vectorul fiscal ale neplătitorului înregistrat art.317
pe rutele ecranelor (`_neplatitor_art317` din `e2e_lot12_cx3`). Răspunsul OSS se dă pe ecran (Date firmă), nu pe rută.

Temei: CF art.315 alin.(3): „În cazul în care România este statul membru de înregistrare, persoana impozabilă respectivă trebuie să depună
în format electronic o declarație de începere a activității sale supuse regimului special la organul fiscal competent.”
Mutațiile: frontend_test/e2e/mut_lot13_oss.json."""
import pytest

from conftest import firma_noua, perioada_incheiata, sql
from e2e_lot13_decl import _F, _asteapta_rezultat, _continua_formular, _txt


@pytest.fixture()
def firma_oss():
    for f in firma_noua():
        yield f


def _completeaza_si_genereaza(pg, asteapta):
    pg.select_option(_F + "#d398-moes", "1")
    pg.wait_for_selector(_F + "#d398-eint", timeout=20000)
    pg.select_option(_F + "#d398-eint", "false")
    pg.fill(_F + "#d398-stat", "DE")
    pg.select_option(_F + "#d398-sup", "1")
    pg.select_option(_F + "#d398-trade", "1")
    pg.select_option(_F + "#d398-vrt", "1")
    pg.fill(_F + "#d398-rate", "19")
    pg.fill(_F + "#d398-baza", "1000")
    pg.click(_F + "#d398-add")
    pg.wait_for_selector(_F + ".dec-d398-del", timeout=20000)
    pg.click(_F + "#d398-regen")
    asteapta(pg)


def _optiune_d398(patron, f):
    """Declarații -> opțiunea D398 din lista tipurilor („Alte declarații” deschisă): {dez, titlu}."""
    from e2e_lot13_decl import _card, _optiune
    patron.firma(f["nume"])
    _card(patron, "declaratii", _F + "#dec-tip")
    return _optiune(patron.pg, "d398")


def _oss_in_date_firma(patron, f, valoare):
    """Firma -> „Date firmă” -> „Înregistrată în regimul special OSS” -> Salvează (pe ecran, ca contabilul)."""
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-datefirma")
    pg.wait_for_selector("#df-inregistrat_oss", timeout=30000)
    pg.select_option("#df-inregistrat_oss", valoare)
    pg.evaluate("() => { const m = document.querySelector('#df-msg'); if (m) m.innerHTML = ''; }")
    pg.click("#df-salveaza")
    pg.wait_for_function("() => (document.querySelector('#df-msg') || {innerText: ''}).innerText.includes('alvat')", timeout=30000)


def test_def_595_oss_se_alege_in_date_firma(patron, firma_oss):
    """595 + 595.1 (14.2). Pașii: firmă neplătitoare înregistrată art.317, fără răspuns la OSS -> Declarații: D398 e inactivă, cu motivul „nu ai
    răspuns în Date firmă” (ca D318) -> Date firmă: câmpul „Înregistrată în regimul special OSS” e „— alege —” (nimic precompletat) -> „Nu” ->
    Salvează -> D398 inactivă, cu motivul legii (CF art.315 alin.(3)) -> „Da” -> Salvează -> D398 activă: se deschide și se generează. La
    generare, refuzul rămâne apărarea de rezervă (`core/test_lot14_2_595_1_d398_gri.py`). MUTAȚII: câmpul scos din Date firmă -> ROȘU; D398 gri
    scos din `neaplicabile_regim` -> ROȘU."""
    from e2e_lot12_cx3 import _neplatitor_art317
    schema = firma_oss["schema"]
    _neplatitor_art317(patron, firma_oss)   # date-de-pornire: Date firmă + vector fiscal, pe rutele ecranelor
    assert sql('SELECT inregistrat_oss FROM "%s".firma_profil' % schema) == [(None,)]   # nedeclarat: firma n-a răspuns încă
    p = perioada_incheiata("trimestrial")

    # 1) fără răspuns: D398 inactivă, cu motiv (ca D318); formularul nu se poate deschide
    o = _optiune_d398(patron, firma_oss)
    patron.captura("d398_gri_nedeclarat")
    assert o["dez"] and "nu ai răspuns" in o["titlu"] and "Date firmă" in o["titlu"] and "CF art.315 alin.(3)" in o["titlu"], o

    # 2) Date firmă: câmpul e „— alege —” (nimic precompletat), „Nu” -> Salvează
    patron.firma(firma_oss["nume"])
    patron.pg.click("#fa-datefirma")
    patron.pg.wait_for_selector("#df-inregistrat_oss", timeout=30000)
    assert patron.pg.input_value("#df-inregistrat_oss") == ""
    patron.captura("date_firma_nedeclarat")
    _oss_in_date_firma(patron, firma_oss, "0")
    assert sql('SELECT inregistrat_oss FROM "%s".firma_profil' % schema) == [(False,)]

    # 3) „Nu”: D398 inactivă, cu motivul legii
    o = _optiune_d398(patron, firma_oss)
    patron.captura("d398_gri_nu")
    assert o["dez"] and "CF art.315 alin.(3)" in o["titlu"] and "nu e înregistrată" in o["titlu"], o

    # 4) „Da”: D398 activă, se generează
    _oss_in_date_firma(patron, firma_oss, "1")
    assert sql('SELECT inregistrat_oss FROM "%s".firma_profil' % schema) == [(True,)]
    pg = _continua_formular(patron, firma_oss, "d398", p.an, trim=p.trim)
    assert pg.locator(_F + "#d398-oss").count() == 0 and "regimul special OSS" not in _txt(pg, "#dec-d398-form")
    _completeaza_si_genereaza(pg, _asteapta_rezultat)
    patron.captura("generat_da")
    assert pg.locator(_F + "#dec-refuz").count() == 0 and "nu ai răspuns" not in _txt(pg)
