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


def _refuz(pg):
    pg.wait_for_selector(_F + "#dec-refuz", timeout=120000)
    return _txt(pg, "#dec-refuz")


def _raspunde_in_date_firma(pg, valoare):
    """Din refuz -> butonul „Date firmă” (trimiterea între ferestre) -> câmpul „Înregistrată în regimul special OSS” -> Salvează."""
    pg.click(_F + "[data-ecran-destinatie='date_firma']")
    pg.wait_for_selector("#df-inregistrat_oss", timeout=30000)
    pg.select_option("#df-inregistrat_oss", valoare)
    pg.evaluate("() => { const m = document.querySelector('#df-msg'); if (m) m.innerHTML = ''; }")
    pg.click("#df-salveaza")
    pg.wait_for_function("() => (document.querySelector('#df-msg') || {innerText: ''}).innerText.includes('alvat')", timeout=30000)


def test_def_595_oss_se_alege_in_date_firma(patron, firma_oss):
    """595 + 595.1 + D2 (14.3). Pașii: firmă neplătitoare înregistrată art.317, fără răspuns la OSS -> Declarații: D398 activă, marcată „de lămurit —
    răspunde în Date firmă …” -> formularul NU întreabă OSS -> completează livrarea -> „Generează D398”: refuz „nu ai răspuns … Date firmă” cu butonul
    „Date firmă” -> câmpul „Înregistrată în regimul special OSS” (fără răspuns precompletat) -> „Nu” -> Salvează -> D398 NU mai apare în lista
    tipurilor -> Date firmă: „Da” -> Salvează -> D398 din nou: se generează. MUTAȚII: refuzul scos din generare -> ROȘU; câmpul scos din Date
    firmă -> ROȘU; D398 ascuns la „Nu” scos -> ROȘU."""
    from e2e_lot12_cx3 import _neplatitor_art317
    schema = firma_oss["schema"]
    _neplatitor_art317(patron, firma_oss)   # date-de-pornire: Date firmă + vector fiscal, pe rutele ecranelor
    assert sql('SELECT inregistrat_oss FROM "%s".firma_profil' % schema) == [(None,)]   # nedeclarat: firma n-a răspuns încă
    p = perioada_incheiata("trimestrial")

    # 0) [D2, 14.3] fără răspuns, D398 NU e gri și tăcut: apare activă, marcată „de lămurit — răspunde în Date firmă …”
    from e2e_lot13_decl import _card, _optiune
    patron.firma(firma_oss["nume"])
    _card(patron, "declaratii", _F + "#dec-tip")
    o = _optiune(patron.pg, "d398")
    patron.captura("d398_de_lamurit")
    assert not o["dez"] and "de lămurit" in o["text"] and "Date firmă" in o["text"], o

    # 1) formularul nu întreabă; fără răspuns în Date firmă generarea se oprește și trimite acolo
    pg = _continua_formular(patron, firma_oss, "d398", p.an, trim=p.trim)
    assert pg.locator(_F + "#d398-oss").count() == 0 and "regimul special OSS" not in _txt(pg, "#dec-d398-form")
    _completeaza_si_genereaza(pg, _refuz)
    refuz = _txt(pg, "#dec-refuz")
    patron.captura("refuz_nedeclarat")
    assert "nu ai răspuns" in refuz and "Date firmă" in refuz and "CF art.315 alin.(3)" in refuz, refuz
    assert pg.locator(_F + "[data-ecran-destinatie='date_firma']").count() == 1

    # 2) Date firmă: câmpul e „— alege —” (nimic precompletat), „Nu” -> Salvează
    pg.click(_F + "[data-ecran-destinatie='date_firma']")
    pg.wait_for_selector("#df-inregistrat_oss", timeout=30000)
    assert pg.input_value("#df-inregistrat_oss") == ""
    patron.captura("date_firma_nedeclarat")
    pg.select_option("#df-inregistrat_oss", "0")
    pg.click("#df-salveaza")
    pg.wait_for_function("() => (document.querySelector('#df-msg') || {innerText: ''}).innerText.includes('alvat')", timeout=30000)
    assert sql('SELECT inregistrat_oss FROM "%s".firma_profil' % schema) == [(False,)]

    # 3) „Nu”: D398 NU mai apare deloc în lista tipurilor (nu e a firmei) [D2, 14.3]
    patron.firma(firma_oss["nume"])
    _card(patron, "declaratii", _F + "#dec-tip")
    patron.pg.wait_for_selector(_F + "#dec-tip", timeout=20000)
    patron.captura("d398_dispare_la_nu")
    assert patron.pg.locator(_F + "#dec-tip option[value='d398']").count() == 0, "D398 se oferă deși firma a răspuns „Nu”"

    # 4) „Da”: D398 se generează
    patron.firma(firma_oss["nume"])
    patron.pg.click("#fa-datefirma")
    patron.pg.wait_for_selector("#df-inregistrat_oss", timeout=30000)
    pg = patron.pg
    pg.select_option("#df-inregistrat_oss", "1")
    pg.evaluate("() => { const m = document.querySelector('#df-msg'); if (m) m.innerHTML = ''; }")
    pg.click("#df-salveaza")
    pg.wait_for_function("() => (document.querySelector('#df-msg') || {innerText: ''}).innerText.includes('alvat')", timeout=30000)
    assert sql('SELECT inregistrat_oss FROM "%s".firma_profil' % schema) == [(True,)]
    pg = _continua_formular(patron, firma_oss, "d398", p.an, trim=p.trim)
    _completeaza_si_genereaza(pg, _asteapta_rezultat)
    patron.captura("generat_da")
    assert pg.locator(_F + "#dec-refuz").count() == 0 and "nu ai răspuns" not in _txt(pg)
