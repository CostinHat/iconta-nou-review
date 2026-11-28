"""[17.5-U2 pct.6, F6] Proba limitelor 501 / 502 rămase pentru 17.5-F6b, pe copia 8019 (iconta_test restaurată), pe arborele candidatului
(C1 8d876246 sau C2): pentru fiecare subcaz, gestul contabilului, ecranul și TEXTUL VIZIBIL complet (inner_text al ferestrei, detaliile
deschise), valorile afișate și refuzurile, cu captură. Proba ÎNREGISTREAZĂ (martori JSON + PNG în CAPTURI/f6b_limite); nu judecă: judecata
(„indicat explicit ca necalculat / nesuportat” sau nu) se face pe martori, în raport. Datele de probă se pun numai pe copie (API-ul aplicației
sau SQL pe iconta_test), iar baza se restaurează după rulare (rulare_8019.sh --restaureaza)."""
import importlib.util as _iu
import json
import sys
from pathlib import Path

import pytest

RAD_E2E = Path(__file__).resolve().parents[4] / "frontend_test" / "e2e"
sys.path.insert(0, str(RAD_E2E))
# conftest-ul plasei, încărcat sub nume propriu (rădăcina are alt conftest.py), ca în docs/dovezi/17_5_Q10/e2e_probe_q10.py
_spec = _iu.spec_from_file_location("conftest_e2e_f6b", RAD_E2E / "conftest.py")
CE = _iu.module_from_spec(_spec)
_spec.loader.exec_module(CE)


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        yield b
        b.close()

TOP = ".fereastra-overlay:not(.fundal) "
CONT = "dovada.71507@sesiuneab.test"
F1, F2 = "F1 Comert Stoc SRL", "F2 Profit Amortizare SRL"
DATA = "2026-11-03"


def _pagina(browser, w=1366, h=768):
    BAZA, sesiune = CE.BAZA, CE.sesiune
    from core.ceas_proba import MOMENT_REF
    from e2e_ferestre_17_5_Q5 import origine_proba
    origine_proba(BAZA)
    ctx = browser.new_context(viewport={"width": w, "height": h}, accept_downloads=True)
    ctx.clock.set_fixed_time(MOMENT_REF)
    ctx.add_init_script(sesiune(CONT))
    pg = ctx.new_page()
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    return ctx, pg


def _dir():
    d = Path(CE.CAPTURI) / "f6b_limite"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _poza(pg, nume, loc=None):
    if loc is not None:
        loc.scroll_into_view_if_needed()
    pg.screenshot(path=str(_dir() / ("%s.png" % nume)))


def _martor(nume, date):
    (_dir() / ("%s.json" % nume)).write_text(json.dumps(date, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def _text_fereastra(pg):
    return pg.evaluate("""() => { const o = [...document.querySelectorAll('.fereastra-overlay:not(.fundal)')]; const t = o[o.length - 1];
      return t ? t.innerText : null; }""")


def _api(pg, metoda, url, corp=None):
    return pg.evaluate("""async ([m, u, c]) => { const t = sessionStorage.getItem('iconta_token') || localStorage.getItem('iconta_token');
      const h = {'Content-Type': 'application/json'}; if (t) h.Authorization = 'Bearer ' + t;
      const r = await fetch(u, {method: m, headers: h, body: c === null ? undefined : JSON.stringify(c)});
      let j = null; try { j = await r.json(); } catch (e) { j = null; } return {status: r.status, corp: j}; }""", [metoda, url, corp])


def _tid(nume):
    sql = CE.sql
    return sql("SELECT id, schema_name FROM public.tenants WHERE nume = %s", (nume,))[0]


def _cnp(baza12):
    k = "279146358279"
    s = sum(int(a) * int(b) for a, b in zip(baza12, k)) % 11
    return baza12 + ("1" if s == 10 else str(s))


def _consultanta(pg, firma, data=DATA):
    from e2e_ferestre_17_5_Q5 import firma as deschide
    deschide(pg, firma, "#fa-consultanta")
    pg.wait_for_selector(TOP + "[data-masura='M5']", timeout=60000)
    if data and pg.input_value(TOP + "#cs-data") != data:
        pg.fill(TOP + "#cs-data", data)
        pg.dispatch_event(TOP + "#cs-data", "change")
        y, m, d = data.split("-")
        pg.wait_for_function("(t) => (document.querySelector('.fereastra-overlay:not(.fundal) #cs-data-afisata') || {}).textContent === t",
                             arg="%s.%s.%s" % (d, m, y), timeout=60000)
        pg.wait_for_selector(TOP + "[data-masura='M5']", timeout=60000)
    for b in pg.locator(TOP + ".cs-det-btn").all():
        b.click()
    return pg.evaluate("""() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) [data-masura]')].map((m) => ({cod: m.dataset.masura,
      text: m.innerText}))""")


def _masuri_capturi(pg, eticheta):
    for cod in ("M1", "M2", "M4", "M5"):
        _poza(pg, "%s_%s" % (eticheta, cod), pg.locator(TOP + "[data-masura='%s']" % cod))


# ── 502: M1, M2, M4, M5 pe F1 și F2, cu detaliile deschise ─────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("firma", [F1, F2])
def test_a_502_masurile_cu_detaliile(browser, firma):
    ctx, pg = _pagina(browser)
    try:
        tid, schema = _tid(firma)
        masuri = _consultanta(pg, firma)
        et = "502_%s" % firma.split()[0]
        _masuri_capturi(pg, et)
        _martor(et, {"firma": firma, "data": DATA, "masuri": masuri, "fereastra": _text_fereastra(pg),
                     "asociati": _api(pg, "GET", "/tenants/%s/asociati" % tid), "api": _api(pg, "GET", "/tenants/%s/consultanta-fiscala?data=%s" % (tid, DATA))})
    finally:
        ctx.close()


def test_b_502_m1_firma_cu_doi_asociati_persoane_fizice(browser):
    """M1 «toți asociații»: F1 cu doi asociați persoane fizice (al doilea adăugat pe copie prin API-ul ecranului Date firmă, cotele 60 / 40)."""
    ctx, pg = _pagina(browser)
    try:
        tid, schema = _tid(F1)
        _consultanta(pg, F1)   # sesiunea pe firmă
        inainte = _api(pg, "GET", "/tenants/%s/asociati" % tid)
        rand = (inainte["corp"] or {}).get("randuri") or (inainte["corp"] or {}).get("asociati") or []
        # [corecția 1 la F6] F1 nu are asociați pe copie: fără un prim asociat, cotele ar însuma 40% (refuz); se pun doi asociați PF, 60 / 40
        primul = [{"nume": r.get("nume"), "cnp": r.get("cnp"), "cota": 60} for r in rand[:1]] or [{"nume": "Popescu Ion Proba", "cnp": _cnp("180010142001"), "cota": 60}]
        randuri = primul + [{"nume": "Ionescu Maria Proba", "cnp": _cnp("280010142001"), "cota": 40}]
        scris = _api(pg, "POST", "/tenants/%s/asociati" % tid, {"randuri": randuri})
        masuri = _consultanta(pg, F1)
        _masuri_capturi(pg, "502_F1_doi_asociati")
        _martor("502_F1_doi_asociati", {"inainte": inainte, "trimis": randuri, "scris": scris, "dupa": _api(pg, "GET", "/tenants/%s/asociati" % tid),
                                        "masuri": masuri, "fereastra": _text_fereastra(pg), "api": _api(pg, "GET", "/tenants/%s/consultanta-fiscala?data=%s" % (tid, DATA)),
                                        "cabinet": _api(pg, "GET", "/cabinet/consultanta")})
    finally:
        ctx.close()


# ── 501: formularul hotărârii (operațiuni → asociați → dividend) ───────────────────────────────────────────────────────────────────────────
def _formular_dividend(pg, firma, valori):
    from e2e_ferestre_17_5_Q5 import firma as deschide
    deschide(pg, firma, "#fa-operatiuni")
    pg.locator(TOP + 'button[data-op="asociati"]').click()
    pg.locator(TOP + "#op-operatie").select_option("dividend")
    for camp, val in (("data", "2026-03-15"), ("brut", "10000"), ("numar_hotarare", "1"), ("data_hotarare", "2026-03-15")):
        pg.locator(TOP + "#op-" + camp).fill(val)
        pg.locator(TOP + "#op-" + camp).dispatch_event("change")
    pg.locator(TOP + "#op-interimar").select_option("0")
    pg.locator(TOP + "#op-div-tabel").wait_for(state="visible", timeout=30000)
    for camp, val in valori:
        el = pg.locator(TOP + "#op-" + camp)
        if el.evaluate("(e) => e.tagName") == "SELECT":
            el.select_option(val)
        else:
            el.fill(val)
        el.dispatch_event("change")
    return pg.evaluate("""() => { const t = document.querySelector('.fereastra-overlay:not(.fundal) #op-div-tabel'); return t ? t.innerText : null; }""")


def _descarca(pg, eticheta):
    mesaj = pg.locator(TOP + "#op-hotarare-mesaj")
    rez = {"descarcare": None}
    try:
        with pg.expect_download(timeout=20000) as d:
            pg.locator(TOP + "#op-descarca-pdf").click()
        cale = _dir() / ("%s.pdf" % eticheta)
        d.value.save_as(str(cale))
        rez["descarcare"] = str(cale)
    except Exception as e:  # noqa: BLE001 — refuzul documentului nu descarcă nimic: se înregistrează mesajul
        rez["exceptie"] = type(e).__name__
    pg.wait_for_timeout(1500)
    rez["mesaj"] = mesaj.inner_text() if mesaj.count() else None
    _poza(pg, eticheta, mesaj if mesaj.count() else None)
    rez["fereastra"] = _text_fereastra(pg)
    return rez


COMPLET = (("aprobare_anuala", "da"), ("an_situatii", "2025"), ("termen_plata", "2026-04-15"), ("modalitate_plata", "virament"),
           ("loc_adunare", "sediul societății"), ("prezenta", "toti"), ("vot", "unanimitate"))


def test_c_501_vot_fara_unanimitate(browser):
    ctx, pg = _pagina(browser)
    try:
        tabel = _formular_dividend(pg, F2, [x for x in COMPLET if x[0] != "vot"])
        optiuni = pg.locator(TOP + "#op-vot option").all_inner_texts()
        optiuni_prezenta = pg.locator(TOP + "#op-prezenta option").all_inner_texts()
        rez = _descarca(pg, "501_vot")
        _martor("501_vot", dict(rez, tabel=tabel, optiuni_vot=optiuni, optiuni_prezenta=optiuni_prezenta))
    finally:
        ctx.close()


def test_d_501_t5_rezerva_legala_si_pierderea_reportata(browser):
    """T5: formularul complet pe F2 (distribuire anuală din 117): propunerea afișată, documentul sau refuzul; soldurile 1061 / 117 / 129 ale copiei."""
    sql = CE.sql
    ctx, pg = _pagina(browser)
    try:
        tid, schema = _tid(F2)
        tabel = _formular_dividend(pg, F2, COMPLET)
        _poza(pg, "501_T5_propunere", pg.locator(TOP + "#op-div-tabel"))
        rez = _descarca(pg, "501_T5")
        conturi = {}
        for cont in ("1061", "117", "1171", "129", "121"):
            try:
                conturi[cont] = sql('SELECT coalesce(sum(CASE WHEN cont_debit LIKE %%s THEN suma END),0), coalesce(sum(CASE WHEN cont_credit LIKE %%s THEN suma END),0) '
                                    'FROM "%s".inregistrari_linii WHERE cont_debit LIKE %%s OR cont_credit LIKE %%s' % schema, (cont + "%",) * 4)[0]
            except Exception as e:  # noqa: BLE001
                conturi[cont] = "eroare: %s" % e
        _martor("501_T5", dict(rez, tabel=tabel, conturi=conturi))
    finally:
        ctx.close()


def test_e_501_acordarea_imprumutului(browser):
    """Acordarea unui împrumut către asociat (alin. (2³)): operația absentă — opțiunile «Împrumut asociat» și textul vizibil al ferestrei."""
    from e2e_ferestre_17_5_Q5 import firma as deschide
    ctx, pg = _pagina(browser)
    try:
        deschide(pg, F2, "#fa-operatiuni")
        pg.locator(TOP + 'button[data-op="asociati"]').click()
        operatii = pg.locator(TOP + "#op-operatie option").all_inner_texts()
        pg.locator(TOP + "#op-operatie").select_option("imprumut")
        pg.wait_for_timeout(800)
        sens = pg.locator(TOP + "#op-fel option").all_inner_texts()
        _poza(pg, "501_imprumut", pg.locator(TOP + "#op-fel"))
        toate = pg.evaluate("() => document.body.innerText")
        _martor("501_imprumut", {"operatii": operatii, "sens": sens, "fereastra": _text_fereastra(pg),
                                 "acord_in_pagina": [ln for ln in toate.splitlines() if "acord" in ln.lower()]})
    finally:
        ctx.close()


def test_f_501_beneficiar_persoana_juridica(browser):
    """Beneficiarul PJ: al doilea asociat al lui F2 primește pe copie un CUI (SQL pe iconta_test); formularul complet, propunerea și documentul / refuzul."""
    sql = CE.sql
    ctx, pg = _pagina(browser)
    try:
        tid, schema = _tid(F2)
        inainte = sql('SELECT id, nume, cnp, cota FROM "%s".asociati ORDER BY id' % schema)
        sql('UPDATE "%s".asociati SET cnp = %%s, nume = %%s WHERE id = (SELECT max(id) FROM "%s".asociati)' % (schema, schema), ("14399840", "Proba Holding SRL"))
        dupa = sql('SELECT id, nume, cnp, cota FROM "%s".asociati ORDER BY id' % schema)
        tabel = _formular_dividend(pg, F2, COMPLET)
        _poza(pg, "501_PJ_propunere", pg.locator(TOP + "#op-div-tabel"))
        rez = _descarca(pg, "501_PJ")
        _martor("501_PJ", dict(rez, tabel=tabel, asociati_inainte=inainte, asociati_dupa=dupa))
    finally:
        ctx.close()


# ── 502: M4 cu cursul de închidere prezent (întreprinderile legate) și M5 cu un activ eligibil (lista specială, second-hand, nepus în funcțiune) ──
def test_g_502_m4_intreprinderi_legate_cu_cursul_prezent(browser):
    """M4 pe F1 (micro): cursul BNR EUR din 31.12.2025 pus pe copie (public.curs_bnr_zilnic), ca M4 să ajungă la marja până la plafon."""
    sql = CE.sql
    ctx, pg = _pagina(browser)
    try:
        inainte = sql("SELECT data, moneda, curs FROM public.curs_bnr_zilnic WHERE moneda = 'EUR' AND data = '2025-12-31'")
        if not inainte:
            sql("INSERT INTO public.curs_bnr_zilnic (data, moneda, curs) VALUES ('2025-12-31', 'EUR', 5.0975)")
        tid, schema = _tid(F1)
        masuri = _consultanta(pg, F1)
        _poza(pg, "502_F1_M4_cu_curs", pg.locator(TOP + "[data-masura='M4']"))
        tot = _api(pg, "GET", "/cabinet/consultanta")
        _martor("502_F1_M4_cu_curs", {"curs_inainte": inainte, "masuri": masuri, "api": _api(pg, "GET", "/tenants/%s/consultanta-fiscala?data=%s" % (tid, DATA)),
                                      "cabinet": tot})
    finally:
        ctx.close()


def test_h_502_m5_activ_eligibil_pe_firma_cu_profit(browser):
    """M5 pe F2 (impozit pe profit): un mijloc fix cu codul 2.1.x pus în funcțiune în 2026 (SQL pe copie; starea lui — nou, second-hand, folosit — nu e
    un câmp al aplicației), apoi fereastra, cardul cabinetului și totalul lui."""
    sql = CE.sql
    ctx, pg = _pagina(browser)
    try:
        tid, schema = _tid(F2)
        col = [r[0] for r in sql("SELECT column_name FROM information_schema.columns WHERE table_schema = %s AND table_name = 'mijloace_fixe' ORDER BY ordinal_position", (schema,))]
        try:
            sql('INSERT INTO "%s".mijloace_fixe (cod, denumire, cod_catalog, cont_imobilizare, valoare, data_pif) VALUES (%%s, %%s, %%s, %%s, %%s, %%s)' % schema,
                ("PROBA-M5", "Strung CNC (proba M5, second-hand)", "2.1.1.1", "2131", 50000, "2026-05-15"))
            scris = "ok"
        except Exception as e:  # noqa: BLE001
            scris = "eroare: %s" % e
        masuri = _consultanta(pg, F2)
        _poza(pg, "502_F2_M5_activ", pg.locator(TOP + "[data-masura='M5']"))
        _martor("502_F2_M5_activ", {"coloane": col, "scris": scris, "masuri": masuri,
                                    "api": _api(pg, "GET", "/tenants/%s/consultanta-fiscala?data=%s" % (tid, DATA)), "cabinet": _api(pg, "GET", "/cabinet/consultanta")})
    finally:
        ctx.close()
