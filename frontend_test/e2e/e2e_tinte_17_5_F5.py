"""[17.5-F5] Testele țintite e2e ale pozițiilor lotului, în afara plasei fixe (rulate la pct. 19, pe candidat, pe copia 8019):
AC202 (un singur semn pe titlu, fereastra de ajutor cu o secțiune pe ID, ✕ și Esc), 502 (fereastra «Consultanță fiscală» pe firma cu
impozit pe profit), 501 (refuzul documentului lângă câmpul lipsă, fără notă creată) și „▾ detalii” (o singură comutare la fiecare clic).
Contul nativ de probă, ceasul fixat la MOMENT_REF; capturile în CAPTURI/17_5_F5_tinte."""
import re
from pathlib import Path

import pytest

TOP = ".fereastra-overlay:not(.fundal) "
CONT = "dovada.71507@sesiuneab.test"
F1, F2 = "F1 Comert Stoc SRL", "F2 Profit Amortizare SRL"
REZ = ((1366, 768), (603, 590))
NIVEL = """() => { const o = [...document.querySelectorAll('.fereastra-overlay:not(.fundal)')]; const t = o[o.length - 1];
  return t ? {nivel: t.dataset.nivel, active: o.length, antet: (t.querySelector('.fereastra-antet, header') || {textContent: ''}).textContent.replace(/\\s+/g, ' ').trim()} : null; }"""


def _pagina(browser, w, h):
    from conftest import BAZA, sesiune
    from core.ceas_proba import MOMENT_REF
    from e2e_ferestre_17_5_Q5 import origine_proba
    origine_proba(BAZA)
    ctx = browser.new_context(viewport={"width": w, "height": h}, accept_downloads=True)
    ctx.clock.set_fixed_time(MOMENT_REF)
    ctx.add_init_script(sesiune(CONT))
    pg = ctx.new_page()
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    return ctx, pg


def _poza(pg, nume):
    from conftest import CAPTURI
    d = Path(CAPTURI) / "17_5_F5_tinte"
    d.mkdir(parents=True, exist_ok=True)
    pg.screenshot(path=str(d / ("%s.png" % nume)))


@pytest.mark.parametrize("w,h", REZ)
def test_ac202_banca_un_semn_o_fereastra_cu_sectiunile_in_ordine_x_si_esc(browser, w, h):
    from e2e_ferestre_17_5_Q5 import firma
    ctx, pg = _pagina(browser, w, h)
    try:
        firma(pg, F1, "#fa-banca")
        titlu = pg.locator(TOP + "#bk-rezumat h2.pf-titlu")
        titlu.wait_for(state="visible")
        semne = titlu.locator("[data-ajutor]")
        assert semne.count() == 1
        s = semne.first
        assert s.get_attribute("title") == "Ajutor: Bancă" and s.get_attribute("aria-label") == "Ajutor: Bancă"
        assert s.get_attribute("data-ajutor") == "F012,F011,F073"
        box = s.bounding_box()
        assert box["width"] >= 24 and box["height"] >= 24
        n0 = pg.evaluate(NIVEL)
        for inchide in ("x", "esc"):
            s.click()
            pg.wait_for_function("(n) => { const o = [...document.querySelectorAll('.fereastra-overlay:not(.fundal)')]; "
                                 "return o.length && o[o.length - 1].dataset.nivel === String(n); }", arg=int(n0["nivel"]) + 1)
            stare = pg.evaluate(NIVEL)
            assert stare["active"] == 1 and "Ajutor" in stare["antet"] and "Bancă" in stare["antet"]
            sec = pg.locator(TOP + "[data-ajutor-sectiune]")
            assert [sec.nth(i).get_attribute("data-ajutor-sectiune") for i in range(sec.count())] == ["F012", "F011", "F073"]
            assert pg.locator(TOP + "[data-ajutor-incomplet]").count() == 0
            assert pg.locator(TOP + "[data-ajutor-sectiune='F012'] [data-ajutor-sectiune-titlu]").inner_text().strip() == "Citirea extrasului bancar"
            _poza(pg, "ajutor_banca_%s_%dx%d" % (inchide, w, h))
            if inchide == "x":
                pg.locator(TOP + "button.nav-x").last.click()
            else:
                pg.keyboard.press("Escape")
            pg.wait_for_function("(n) => { const o = [...document.querySelectorAll('.fereastra-overlay:not(.fundal)')]; "
                                 "return o.length && o[o.length - 1].dataset.nivel === String(n); }", arg=int(n0["nivel"]))
            assert pg.evaluate(NIVEL)["antet"] == n0["antet"]
    finally:
        ctx.close()


@pytest.mark.parametrize("card, sel, ids, zona", [
    ("#fa-produse", "h2.pf-titlu", "F023,F070", "Produse și servicii"),
    ("#fa-stocuri", "h2.pf-titlu", "F089,F088", "Stocuri"),
    ("#fa-etransport", "h2.pf-titlu", "F044,F121", "e-Transport"),
])
def test_ac202_titlurile_cu_mai_multe_functii_au_un_semn(browser, card, sel, ids, zona):
    from e2e_ferestre_17_5_Q5 import firma
    for w, h in REZ:
        ctx, pg = _pagina(browser, w, h)
        try:
            firma(pg, F1, card)
            t = pg.locator(TOP + sel).filter(has=pg.locator("[data-ajutor]")).first   # titlul desenat (după încărcarea datelor), cu semnul lui
            t.wait_for(state="visible", timeout=30000)
            assert pg.locator(TOP + sel).count() == 1, (card, w)
            semne = t.locator("[data-ajutor]")
            assert semne.count() == 1, (card, w)
            assert semne.first.get_attribute("data-ajutor") == ids and semne.first.get_attribute("aria-label") == "Ajutor: " + zona
            _poza(pg, "semn_%s_%dx%d" % (card[1:], w, h))
        finally:
            ctx.close()


@pytest.mark.parametrize("w,h", REZ)
def test_502_fereastra_consultanta_pe_firma_cu_impozit_pe_profit(browser, w, h):
    from e2e_ferestre_17_5_Q5 import firma
    ctx, pg = _pagina(browser, w, h)
    try:
        firma(pg, F2, "#fa-consultanta")
        pg.locator(TOP + "[data-masura]").first.wait_for(state="visible", timeout=60000)
        rand = pg.locator(TOP + "[data-masura]")
        assert [rand.nth(i).get_attribute("data-masura") for i in range(rand.count())] == ["M1", "M2", "M3", "M4", "M5"]
        stare = {rand.nth(i).get_attribute("data-masura"): rand.nth(i).locator("[data-masura-stare]").inner_text().strip() for i in range(5)}
        assert stare["M4"] == "Nu se aplică" and stare["M2"] == "Nu se aplică", stare   # F2: impozit pe profit, fără salariați
        assert all(v in ("Se aplică", "Nu se aplică", "Lipsesc date", "Lipsesc date — temei neverificat") for v in stare.values())
        for i in range(5):
            if stare["M%d" % (i + 1)] != "Se aplică":
                assert rand.nth(i).locator("[data-masura-motiv]").inner_text().strip()
        assert pg.locator(TOP + ".cs-fraza").inner_text().strip() == "Aplicația semnalează și calculează; decizia și consilierea clientului aparțin contabilului."
        b = rand.nth(0).locator(".cs-det-btn")
        if b.count():
            b.click()
            assert rand.nth(0).locator(".cs-detalii").is_visible() and b.get_attribute("aria-expanded") == "true"
        _poza(pg, "consultanta_f2_%dx%d" % (w, h))
    finally:
        ctx.close()


def test_501_refuzul_documentului_sta_langa_formular_si_nu_creeaza_note(browser):
    from conftest import sql
    from e2e_ferestre_17_5_Q5 import firma
    s2 = sql("SELECT schema_name FROM public.tenants WHERE nume = %s", (F2,))[0][0]
    assert re.fullmatch(r"tenant_[0-9]+", s2)
    note = lambda: sql('SELECT count(*) FROM "%s".inregistrari' % s2)[0][0]  # noqa: E731
    ctx, pg = _pagina(browser, 1366, 768)
    try:
        firma(pg, F2, "#fa-operatiuni")
        pg.locator(TOP + 'button[data-op="asociati"]').click()
        pg.locator(TOP + "#op-operatie").select_option("dividend")
        for camp, val in (("data", "2026-03-15"), ("brut", "10000"), ("numar_hotarare", "1"), ("data_hotarare", "2026-03-15")):
            pg.locator(TOP + "#op-" + camp).fill(val)
            pg.locator(TOP + "#op-" + camp).dispatch_event("change")
        pg.locator(TOP + "#op-interimar").select_option("0")
        pg.locator(TOP + "#op-div-tabel").wait_for(state="visible", timeout=30000)
        assert pg.locator(TOP + "#op-exemplare").input_value() == "3", "exemplarele sugerate: doi asociați plus unu"
        inainte = note()
        pg.locator(TOP + "#op-descarca-pdf").click()
        msg = pg.locator(TOP + "#op-hotarare-mesaj")
        msg.wait_for(state="visible", timeout=30000)
        pg.wait_for_function("() => (document.querySelector('.fereastra-overlay:not(.fundal) #op-hotarare-mesaj') || {}).textContent.trim().length > 0")
        assert "Alege dacă hotărârea aprobă" in msg.inner_text(), msg.inner_text()
        assert note() == inainte
        _poza(pg, "refuz_501")
    finally:
        ctx.close()


def test_detalii_o_singura_comutare_la_fiecare_clic_in_control_fiscal(browser):
    from e2e_ferestre_17_5_Q5 import firma
    ctx, pg = _pagina(browser, 603, 590)
    try:
        firma(pg, F1, "#fa-control")
        pg.locator(TOP + "#cf-luna-comparata").wait_for(state="attached", timeout=60000)
        b = pg.locator(TOP + ".ds-rezumat-cutie .ds-rezumat-plie:not(.ds-rezumat-plie-auto), " + TOP + ".ds-semnal-cutie .ds-semnal-plie").first
        b.wait_for(state="visible", timeout=30000)
        assert b.get_attribute("aria-expanded") in (None, "false")
        b.click()
        assert b.get_attribute("aria-expanded") == "true" and b.inner_text().strip() == "▴ detalii"
        b.click()
        assert b.get_attribute("aria-expanded") == "false" and b.inner_text().strip() == "▾ detalii"
    finally:
        ctx.close()
