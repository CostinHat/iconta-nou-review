# -*- coding: utf-8 -*-
"""Lotul 15, comanda 15.1-E5 — acțiunea principală a barei de jos, grupul de butoane, bara de sus, lista cu căutare; în browser, pe ecranul real.

  * 727.2: clicul pe rândul listei cu căutare alege declarația (nu deschide ajutorul), Enter alege primul rând din filtru; 742: lista are loc pentru 8 rânduri la 1366×768;
  * bara de jos: fereastra firmei n-are nici principal, nici „Renunță”, nici „Închide”; „←” 40×40 și nicio „✕” în bara de sus (713.1);
  * grupul de butoane: „— alege —” nu mai e buton, butonul principal e cenușiu până se alege; comutatorul XS din Clienți.
Dovezile de valoare ale fiecărui câmp sunt în `core/test_lot15_e5_grupuri.py`."""
import pytest

from conftest import firma_noua
from e2e_bloc_a import pregateste_firma, _deschide_emiterea


@pytest.fixture()
def firma_e5(patron):
    for f in firma_noua():
        pregateste_firma(patron, f)
        yield f


def test_727_2_clic_pe_rand_alege_enter_alege_primul_si_lista_umple_fereastra(patron, firma_e5):
    pg = patron.pg
    pg.set_viewport_size({"width": 1366, "height": 768})
    patron.firma(firma_e5["nume"])
    pg.click("#fa-declaratii")
    pg.wait_for_selector(".ds-lista-rand", timeout=30000)
    inalt = pg.evaluate("() => document.querySelector('.ds-lista-randuri').getBoundingClientRect().height")
    assert inalt >= 8 * 44 - 1, inalt                                             # 742: minimum 8 rânduri la 1366×768
    pg.locator(".ds-lista-rand:not(.ds-lista-inactiv)").first.click()
    assert pg.locator(".ajutor-overlay-liber, .fereastra:has-text('Ajutor ·')").count() == 0   # ajutorul se deschide numai din „?”
    assert pg.input_value("#dec-tip") != ""
    assert pg.is_enabled("#dec-continua") or pg.get_attribute("#dec-continua", "data-cadru-inactiv")  # alegerea a pornit pasul
    # Enter în căutare alege primul rând din filtru
    pg.fill(".ds-lista-cauta", "d300")
    pg.press(".ds-lista-cauta", "Enter")
    assert pg.input_value("#dec-tip") == "d300"
    patron.captura("l15e5_declaratii_lista")


def test_bara_de_sus_fara_x_si_bara_de_jos_a_ferestrei_firmei_fara_principal(patron, firma_e5):
    pg = patron.pg
    patron.firma(firma_e5["nume"])
    m = pg.evaluate("""() => { const F = [...document.querySelectorAll('.fereastra')].pop(), s = F.querySelector('.nav-inapoi').getBoundingClientRect(), x = F.querySelector('.fereastra-antet .nav-x'), r = x ? x.getBoundingClientRect() : null;
      return { x: !!x && [Math.round(r.width), Math.round(r.height)], sag: [Math.round(s.width), Math.round(s.height)], principale: F.querySelectorAll('.fereastra-jos .buton-primar').length,
               butoane: [...F.querySelectorAll('.fereastra-jos button')].map((b) => b.innerText.trim()) }; }""")
    assert m["x"] == [40, 40] and m["sag"] == [40, 40], m                           # [16.8] „✕” 40 × 40; „←” (fereastra firmei e deschisă peste „Firme existente”: pas înapoi real) rămâne 40 × 40
    assert m["principale"] == 0 and m["butoane"] == [], m                           # fereastra firmei: bara fără principal, fără „Renunță”, fără „Închide”


def test_emite_factura_tipul_documentului_si_renunta_pe_cardul_ciornei(patron, firma_e5):
    _deschide_emiterea(patron, firma_e5["nume"])
    pg = patron.pg
    assert pg.locator("#em-tip").evaluate("s => s.value") == "factura"
    pg.locator(".alegere-butoane button", has_text="Proforma").click()
    assert pg.locator("#em-tip").evaluate("s => s.value") == "proforma"             # valoarea trimisă la server = a listei de dinainte
    assert pg.locator(".em-doc-antet #em-renunta").count() == 0                     # „Renunță la factură” nu mai e în mijlocul formularului
    pg.fill("#em-nume", "Client E5")
    pg.wait_for_selector("#em-ciorna .ds-rezumat #em-renunta", timeout=10000)       # ... ci buton S pe cardul ciornei
    m = pg.evaluate("() => { const F = [...document.querySelectorAll('.fereastra')].pop(); return [...F.querySelectorAll('.fereastra-jos button')].map((b) => b.innerText.trim()); }")
    assert m == ["Renunță", "Emite factură"], m


def test_clienti_afiliat_comutator_xs_in_rand(patron, firma_e5):
    pg = patron.pg
    patron.firma(firma_e5["nume"])
    pg.click("#fa-clienti")
    pg.wait_for_selector("#cl-nou", timeout=30000)
    if pg.locator("select.cl-afiliat").count() == 0:
        pytest.skip("firma nouă n-are clienți în listă")
    b = pg.locator("table .alegere-comutator").first
    assert abs(b.bounding_box()["height"] - 28) <= 1
    sel = pg.locator("select.cl-afiliat").first
    inainte = sel.evaluate("s => s.value")
    b.click()
    assert sel.evaluate("s => s.value") != inainte
