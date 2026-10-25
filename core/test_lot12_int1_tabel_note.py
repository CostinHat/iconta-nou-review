# -*- coding: utf-8 -*-
"""[lotul 12, comanda Costin 12.2, integrarea I1 — trei defecte ale tabelului comun de note (617 / 622) găsite la integrare]

  1. „De validat”: „Validează” pe o notă fără document pune întrebarea în detaliul rândului (`locInDetaliu`), care îl deschidea DIRECT
     (`det.hidden = false`), ocolind deschiderea tabelului: liniile notei rămâneau pe „Se încarcă liniile notei…” la nesfârșit, iar la
     redesenare detaliul se închidea (cheia nu intra în `deschise`). Acum deschiderea trece prin același drum ca clicul pe rând.
  2. Detaliul notei din coadă scria „Rulaj: rulaj 121,00 lei” (cuvânt dublat): acum „rulaj 121,00 lei”, o dată.
  3. „De validat” deschis din notificare marca rândul (`val-evidentiat`) fără să-i deschidă detaliul, pe când Registrul jurnal (`evidentiaza`)
     îl deschide — situații identice, soluții identice (CLAUDE.md §9): acum și aici rândul are detaliul deschis, cu liniile.

Ecranul REAL (`validat.js`, `tabel_note.js`, `navigator.js`, `stil.css`), în Chromium, cu rutele simulate (harness-ul
`core/test_lot12_ui2_ecrane.py`). MUTAȚII: `locInDetaliu` înapoi pe `det.hidden = false` -> pică 1; „Rulaj: ${rulajNota(n)}” pus la loc ->
pică 2; deschiderea din `_arataEvidentiat` scoasă -> pică 3. Temei: N/A — reguli de interfață (DS cap.9 „Tabelul de note”; CLAUDE.md §9)."""
from core.test_lot12_ui2_ecrane import _CORP, _coada_proba, _deschide_validat, _pagina, _rute_validat, browser  # noqa: F401

_DETALIU = """(k) => { const c = (%s)(), tb = c.querySelector(`#val-note tbody[data-coada-ids='${k}']`), det = tb.querySelector('.tn-detaliu');
  return {deschis: !det.hidden, se_incarca: !!det.querySelector('.tn-linii-loc'), linii: det.querySelectorAll('table.tn-linii tbody tr').length,
          sub: [...det.querySelectorAll('.pf-frand-sub')].map((p) => p.textContent.trim()), evid: tb.classList.contains('val-evidentiat'),
          caseta: !!document.querySelector('#caseta-atentie-activa')}; }""" % _CORP


def test_validarea_notei_fara_document_deschide_detaliul_cu_liniile_si_il_tine_deschis(browser):  # noqa: F811
    stare = {"coada": _coada_proba()}
    pg, erori = _pagina(browser, _rute_validat(stare))
    try:
        _deschide_validat(pg)
        pg.evaluate("() => document.querySelector(\"#val-note tbody[data-coada-ids='502'] .val-aproba\").click()")
        pg.wait_for_selector("#caseta-atentie-activa", timeout=5000)
        pg.wait_for_timeout(400)
        la_intrebare = pg.evaluate(_DETALIU, "502")
        # o redesenare a cozii (validarea altei note, pe loc): detaliul notei 502 rămâne deschis
        pg.evaluate("() => document.querySelector(\"#val-note tbody[data-coada-ids='501'] .val-aproba\").click()")
        pg.wait_for_function("() => !document.querySelector(\"#val-note tbody[data-coada-ids='501']\")", timeout=5000)
        pg.wait_for_timeout(400)
        dupa = pg.evaluate(_DETALIU, "502")
    finally:
        pg.close()
    assert not erori, erori
    assert (la_intrebare["caseta"], la_intrebare["deschis"], la_intrebare["se_incarca"], la_intrebare["linii"]) == (True, True, False, 2), la_intrebare
    assert (dupa["deschis"], dupa["se_incarca"], dupa["linii"]) == (True, False, 2), dupa


def test_rulajul_din_detaliu_se_scrie_o_singura_data(browser):  # noqa: F811
    pg, erori = _pagina(browser, _rute_validat({"coada": _coada_proba()}))
    try:
        _deschide_validat(pg)
        pg.click("#val-note tbody[data-coada-ids='501'] .tn-deschide")
        pg.wait_for_timeout(300)
        d = pg.evaluate(_DETALIU, "501")
    finally:
        pg.close()
    assert not erori, erori
    assert d["sub"][-1] == "rulaj 121,00 lei", d["sub"]   # era „Rulaj: rulaj 121,00 lei”


def test_din_notificare_randul_are_detaliul_deschis_ca_in_registrul_jurnal(browser):  # noqa: F811
    pg, erori = _pagina(browser, _rute_validat({"coada": _coada_proba()}))
    try:
        pg.evaluate("""async () => { const v = await import('/static/js/ecrane/validat.js');
          window._nav.deschide('De validat', (c, n) => v.randeazaValidat(c, n, {titlu: 'De validat', evidentiaza: 501}), {nivel: 'cabinet'}); }""")
        pg.wait_for_selector("#val-note tbody.val-evidentiat", timeout=15000)
        pg.wait_for_timeout(400)
        d = pg.evaluate(_DETALIU, "501")
    finally:
        pg.close()
    assert not erori, erori
    assert (d["evid"], d["deschis"], d["se_incarca"], d["linii"]) == (True, True, False, 2), d
