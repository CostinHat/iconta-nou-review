# -*- coding: utf-8 -*-
"""Lotul 15, comanda 15.1, zona A — scenariile 720 și 721 (Operațiuni speciale › Chirii / comodat / refacturări), în browser, pe ecranul real.

  * 720 — felul e grup de alegere pe un rând, fără „— alege —” ca buton; imediat după alegerea felului „chirie plătită”, la o firmă cu TVA la
          încasare, refuzul 714 apare ca card-rezumat cu drum spre Facturi primite, iar „Generează nota” e inactiv cu motiv; „Verifică” pe CUI aduce
          denumirea și stabilește tipul (câmpul „Proprietar” nu se mai cere); cota TVA e grup de alegere din cotele legale la data documentului;
          câmpurile sunt pe grupuri (Document / Furnizor / Client / Sume), aceeași înălțime (44 px), nimic tăiat la 1920 × 1080 și 1366 × 768.
  * 721 — formularul început se păstrează pe server: „înapoi” duce la Operațiuni speciale, la revenire câmpurile sunt cum au fost lăsate; „Renunță” îl golește.
Firma e NOUĂ (`firma_noua`), cu TVA la încasare din prima zi a lunii."""
import datetime as _dt

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import pregateste_firma

AZI = _dt.date.today()
REZOLUTII = ((1920, 1080), (1366, 768))


@pytest.fixture()
def firma_tvai(patron):
    for f in firma_noua():
        pregateste_firma(patron, f, regim_fiscal="profit")
        sql('INSERT INTO "%s".tva_incasare_perioade (de_la) VALUES (%%s)' % f["schema"], (AZI.replace(day=1).isoformat(),))   # date-de-pornire: perioada TVA la încasare a firmei
        yield f


def _formular_chirie(patron, f):
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-operatiuni")
    pg.wait_for_selector("button[data-op='chirie']", state="attached", timeout=25000)
    pg.evaluate("""() => { const b = document.querySelector("button[data-op='chirie']"); const g = b.closest('.op-grup[hidden]');
        if (g) document.querySelector('.rap-tab[data-grup="' + g.dataset.frecventa + '"]').click(); }""")
    pg.click("button[data-op='chirie']")
    pg.wait_for_selector("#op-trimite", timeout=20000)
    pg.wait_for_timeout(1500)


def _alege(pg, camp, valoare):
    sel = "#op-%s" % camp
    pg.wait_for_function("([s, v]) => [...document.querySelector(s).options].some((o) => o.value === String(v))", arg=[sel, str(valoare)], timeout=20000)
    pg.select_option(sel, str(valoare))
    pg.dispatch_event(sel, "change")


def _taiat(pg):
    return pg.evaluate("""() => [...document.querySelectorAll('.fereastra:last-of-type .camp-input, .fereastra:last-of-type .camp-eticheta')]
        .filter((e) => e.offsetParent && e.scrollWidth > e.clientWidth + 1).map((e) => e.id || e.textContent.trim())""")


@pytest.mark.parametrize("lat,inalt", REZOLUTII)
def test_def_720_formular_pe_piese(patron, firma_tvai, lat, inalt):
    pg = patron.pg
    pg.set_viewport_size({"width": lat, "height": inalt})
    _formular_chirie(patron, firma_tvai)
    # felul: un singur rând de butoane, fără „— alege —” ca buton, nimic ales la început
    butoane = pg.locator(".alegere-butoane:has(+ #op-fel) > button")
    assert butoane.count() == 4, butoane.all_inner_texts()
    assert not any("alege" in t.lower() for t in butoane.all_inner_texts())
    ys = {round(b.bounding_box()["y"]) for b in butoane.all()}
    assert len(ys) == 1, "felul nu stă pe un rând: %s" % ys
    assert pg.eval_on_selector("#op-fel", "e => e.value") == ""
    # câmpurile pe grupuri, cu titlu
    titluri = pg.locator(".ds-grup:not([hidden]) .ds-grup-titlu").all_inner_texts()
    assert "DOCUMENT" in [t.upper() for t in titluri], titluri
    # felul „chirie plătită” la o firmă cu TVA la încasare: refuzul 714 imediat, cu drum spre Facturi primite; butonul notei inactiv, cu motiv
    _alege(pg, "fel", "chirie_platita")
    pg.wait_for_selector("#op-refuz-fel .ds-rezumat-eroare", timeout=15000)
    assert "Facturi primite" in pg.inner_text("#op-refuz-fel")
    assert pg.locator("#op-refuz-fel .ds-rezumat-actiune").inner_text().strip() == "Deschide Facturi primite"
    assert pg.get_attribute("#op-trimite", "aria-disabled") == "true"
    assert pg.get_attribute("#op-trimite", "data-motiv-inactiv")
    assert pg.inner_text("#op-motiv-inactiv").strip()
    # „Verifică”: denumirea și tipul se stabilesc, „Proprietar” nu se mai cere separat
    pg.fill("#op-furnizor_cui", "14399840")
    pg.click("#op-furnizor_cui-verifica")
    pg.wait_for_function("() => document.querySelector('#op-furnizor_nume').value.length > 3", timeout=20000)
    assert pg.eval_on_selector("#op-proprietar", "e => e.closest('.camp').classList.contains('camp-dedus')")
    assert not pg.is_visible("#op-proprietar")
    # cota: grup de alegere din cotele legale la data documentului, nu câmp de scris
    assert pg.eval_on_selector("#op-cota", "e => e.tagName") == "SELECT"
    cote = pg.locator(".alegere-butoane:has(+ #op-cota) > button").all_inner_texts()
    assert "21%" in cote and "11%" in cote, cote
    # aceeași înălțime pe câmpurile de pe același rând și nimic tăiat
    inaltimi = pg.evaluate("() => [...document.querySelectorAll('.ds-grup .camp-input')].filter((e) => e.offsetParent && e.tagName === 'INPUT').map((e) => Math.round(e.getBoundingClientRect().height))")
    assert inaltimi and set(inaltimi) == {44}, inaltimi
    assert _taiat(pg) == [], _taiat(pg)
    assert pg.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth + 1")
    cuvant = pg.evaluate("""() => { const b = document.querySelector('#op-furnizor_cui-verifica').getBoundingClientRect(), d = document.querySelector('#op-furnizor_nume').getBoundingClientRect();
        return b.right <= d.left || b.bottom <= d.top; }""")
    assert cuvant, "„Verifică” acoperă denumirea: %s" % pg.evaluate("""() => ['#op-furnizor_cui', '#op-furnizor_cui-verifica', '#op-furnizor_nume'].map((q) => { const r = document.querySelector(q).getBoundingClientRect(); return [q, Math.round(r.left), Math.round(r.right), Math.round(r.top)]; })""")
    derulare = pg.evaluate("() => [...document.querySelectorAll('.fereastra-corp')].filter((e) => e.offsetParent && e.scrollHeight > e.clientHeight + 1).map((e) => e.scrollHeight - e.clientHeight)")
    assert derulare == [], "formularul se derulează: %s" % derulare
    patron.captura("l15_720_%d" % lat)


def test_def_721_ciorna_pe_server(patron, firma_tvai):
    pg = patron.pg
    _formular_chirie(patron, firma_tvai)
    _alege(pg, "fel", "chirie_incasata")
    pg.fill("#op-chirie", "1000")
    pg.dispatch_event("#op-chirie", "change")
    pg.wait_for_timeout(2500)   # pauza de tastare: ciorna pleacă la server
    pg.locator(".nav-inapoi").last.click()
    pg.wait_for_selector("button[data-op='chirie']", state="attached", timeout=20000)   # „înapoi” duce la Operațiuni speciale
    assert pg.locator("#fa-operatiuni").count() == 0
    pg.evaluate("""() => { const b = document.querySelector("button[data-op='chirie']"); const g = b.closest('.op-grup[hidden]');
        if (g) document.querySelector('.rap-tab[data-grup="' + g.dataset.frecventa + '"]').click(); }""")
    pg.click("button[data-op='chirie']")
    pg.wait_for_selector("#op-trimite", timeout=20000)
    pg.wait_for_function("() => document.querySelector('#op-fel').value === 'chirie_incasata'", timeout=15000)
    assert pg.input_value("#op-chirie") not in ("", None)
    # F5: ciorna e pe server, deci formularul redeschis are aceleași valori
    pg.reload(wait_until="domcontentloaded")
    pg.wait_for_timeout(3000)
    _formular_chirie(patron, firma_tvai)
    pg.wait_for_function("() => document.querySelector('#op-fel').value === 'chirie_incasata'", timeout=15000)
    # „Renunță” golește ciorna
    pg.click("#op-renunta")
    pg.wait_for_function("() => !!document.querySelector(\"button[data-op='chirie']\")", timeout=20000)
    pg.wait_for_timeout(1500)
    _formular_chirie(patron, firma_tvai)
    assert pg.eval_on_selector("#op-fel", "e => e.value") == ""
