# -*- coding: utf-8 -*-
"""Lotul 15, comanda 15.1-E5, pct.2 — grupul de butoane în locul listelor derulante: valoarea trimisă la server nu se schimbă. Mecanismele REALE (cadru.js,
api.js, stil.css) în Chromium, pe pagina-ham a lotului 12. Pe fiecare câmp reprezentativ: valoarea implicită, valoarea după fiecare buton, câmpul obligatoriu cu „— alege —”.
Dovada pe câmpurile aplicației (op-fel, em-tip, cl-afiliat, nir-l0-cota_tva …) stă în `e2e_lot15_e5.py` și în verificator, rândul h."""
import pytest

from core.test_lot12_ui2_derulare import _pagina
from core.test_lot12_ui2_ecrane import browser  # noqa: F401 — fixture


@pytest.fixture()
def pg(browser):  # noqa: F811
    p, erori = _pagina(browser, {})
    yield p
    p.close()
    assert not erori, erori


_PAGINA = """() => new Promise((rez) => {
  window._nav.deschide('Decont', (c) => {
    c.innerHTML = `<form class="ds-formular" onsubmit="return false"><label class="camp"><span class="camp-eticheta">Fel</span><select id="fel" class="camp-input">
        <option value="avans" selected>Avans</option><option value="decont">Decont</option><option value="altul">Altul</option></select></label>
      <label class="camp"><span class="camp-eticheta">Cota</span><select id="cota" class="camp-input">
        <option value="">— alege —</option><option value="21">21%</option><option value="11">11%</option></select></label>
      <label class="camp"><span class="camp-eticheta">Unică</span><select id="unica" class="camp-input"><option value="x">Singura</option></select></label>
      <table><tbody><tr><td><select id="afil" class="camp-input"><option value="da">Da</option><option value="nu" selected>Nu</option></select></td></tr></tbody></table>
      <label class="camp"><span class="camp-eticheta">Gol</span><select id="gol" class="camp-input"></select></label>
      <p><button class="buton-primar" id="salv">Salvează</button></p></form>`;
  }, { lat: 'lucru' });
  setTimeout(() => rez(true), 400);
})"""


def test_grup_de_butoane_pastreaza_valoarea_implicita_si_o_schimba_ca_lista(pg):
    """MUTAȚIE: `alegereButoane` scos din `_listeDerulante` -> nu există grup -> pică."""
    pg.evaluate(_PAGINA)
    F = ".fereastra:last-of-type "
    assert pg.eval_on_selector("#fel", "s => s.value") == "avans"                          # lista pleca cu prima variantă: grupul pornește cu ea apăsată
    assert pg.locator(F + ".alegere-butoane button[aria-checked=true]").first.inner_text() == "Avans"
    for text, valoare in (("Decont", "decont"), ("Altul", "altul"), ("Avans", "avans")):
        pg.locator(F + ".alegere-butoane", has=pg.locator("button", has_text="Decont")).locator("button", has_text=text).click()
        assert pg.eval_on_selector("#fel", "s => s.value") == valoare                       # aceeași valoare ca înainte (cea a listei)
    h = pg.eval_on_selector(F + ".alegere-butoane button", "b => Math.round(b.getBoundingClientRect().height)")
    assert h == 44, h                                                                       # butoane M


def test_lista_cu_alege_devine_grup_fara_buton_apasat_si_camp_obligatoriu(pg):
    pg.evaluate(_PAGINA)
    assert pg.eval_on_selector("#cota", "s => s.value") == ""                              # nimic ales
    grup = pg.locator(".alegere-butoane", has=pg.locator("button", has_text="21%"))
    assert grup.locator("button[aria-checked=true]").count() == 0
    assert [b for b in grup.locator("button").all_inner_texts()] == ["21%", "11%"]         # niciun buton „— alege —”
    assert "*" in pg.eval_on_selector("#cota", "s => s.closest('label').textContent")      # câmp obligatoriu
    stare = pg.eval_on_selector(".fereastra-jos .buton-primar", "b => ({ inactiv: !!b.dataset.cadruInactiv, motiv: document.querySelector('.fereastra-jos .fj-text')?.textContent || '' })")
    assert stare["inactiv"] and "Cota" in stare["motiv"], stare                             # butonul principal cenușiu, cu „Completează: …”
    grup.locator("button", has_text="11%").click()
    assert pg.eval_on_selector("#cota", "s => s.value") == "11"
    pg.wait_for_timeout(200)
    assert pg.eval_on_selector(".fereastra-jos .buton-primar", "b => !b.dataset.cadruInactiv")


def test_o_singura_varianta_e_text_in_rand_de_tabel_doua_variante_comutator_xs_lista_goala_ascunsa(pg):
    pg.evaluate(_PAGINA)
    assert pg.locator(".alegere-text", has_text="Singura").count() == 1                    # o singură variantă = text, fără control
    comut = pg.locator("table .alegere-comutator")
    assert comut.count() == 1 and comut.inner_text() == "Nu"
    assert comut.evaluate("b => Math.round(b.getBoundingClientRect().height)") == 28       # comutator XS
    comut.click()
    assert pg.eval_on_selector("#afil", "s => s.value") == "da" and comut.inner_text() == "Da"
    assert pg.eval_on_selector("#gol", "s => s.classList.contains('alegere-sursa')")      # lista goală nu rămâne pe ecran
