# -*- coding: utf-8 -*-
"""Lotul 12, comanda 12.1, pachetul `emit` — emiterea facturii, ciorna ei, facturile recurente, livrarea intracomunitară din Operațiuni.

  * 495 — ciorna facturii pe server: începută într-un browser, se regăsește în altul („alt calculator”), iar ciorna veche rămasă în
    browser (de dinainte de reparație) urcă pe server la prima deschidere;
  * 488 — lista de articole de stoc a liniei are căutare (denumire sau cod de bare, fără diacritice);
  * 470 — „nota …” din detaliul facturii deschide Registrul jurnal PE nota facturii (evidențiată, adusă pe ecran), nu la începutul lunii;
  * 462 — șablonul facturii recurente trece prin verificările facturii obișnuite, la salvare;
  * C84 — din Operațiuni, „Livrare intracomunitară” › Bunuri trimite la „Emite factură”, unde livrarea de bunuri pe o firmă cu stocul
    cantitativ-valoric se emite cu articolul din stoc, iar marfa se descarcă.

DATE DE PORNIRE fără ecran (declarate, regula lui 429): firmele sunt NOI (`conftest.firma_noua`), pregătite pe rutele ecranelor
(`e2e_bloc_a.pregateste_firma`); intrările în stoc pe drumul „Mișcări, fișe de magazie” (`stocuri_cv_api.intrare`, ca `e2e_bloc_c.firma_cv`);
facturile de pornire ale lui 470 pe ruta formularului (`e2e_bloc_a.emite_api`). VIES e serviciu extern: răspunsul lui e servit de probă
(`page.route`). Clientul român: DANTE INTERNATIONAL SA, CUI 14399840 — cifra de control verificată cu algoritmul din CLAUDE.md.

Temei: CF art.294 alin.(2) lit.a) (livrarea intracomunitară scutită, „către o persoană impozabilă [...] care îi comunică furnizorului un
cod valabil de înregistrare în scopuri de TVA, atribuit de autoritățile fiscale din alt stat membru”); CF art.319 alin.(20) lit.a) („numărul
de ordine, în baza uneia sau a mai multor serii”) și lit.f) („denumirea/numele și adresa beneficiarului”); Legea 31/1990 art.74 alin.(1)
și (3) (forma juridică și capitalul social pe factură). 495, 488, 470: N/A — reguli de produs (CLAUDE.md §9)."""
import contextlib
import json
from decimal import Decimal

import pytest

from conftest import _ecran, firma_noua, sql
from e2e_bloc_a import AZI, PRODUS, _card, emite_api, pregateste_firma, scoate_forma_si_capitalul

ecran_cont = contextlib.contextmanager(_ecran)
PATRON = "patron@prisma-cont.test"
CUI_DANTE = "14399840"


@pytest.fixture()
def firma_emit(patron):
    for f in firma_noua():
        pregateste_firma(patron, f)
        try:
            yield f
        finally:
            sql("DELETE FROM public.ciorne_formular WHERE tenant_id = %s", (f["tenant_id"],))


def _intrari(firma, articole):
    """Intrările în stoc (denumire, cantitate, preț) pe drumul „Mișcări, fișe de magazie”."""
    from core import db, stocuri_cv_api
    with db.get_conn(firma["schema"]) as c:
        for den, cant, pret in articole:
            r = stocuri_cv_api.intrare(c, firma["schema"], {"denumire": den, "um": "buc", "data": AZI.isoformat(), "cantitate": cant,
                                                            "pret_unitar": pret, "document": "Inventar initial proba lot 12"})
            assert "eroare" not in r, r
        c.commit()


def _emiterea(e, firma):
    e.firma(firma["nume"])
    _card(e, "facturi", "#fac-emite")
    e.pg.click("#fac-emite")
    e.pg.wait_for_selector("#em-l0-descriere", timeout=25000)
    e.pg.wait_for_timeout(400)


def _uid(email):
    return sql("SELECT id FROM public.users WHERE email = %s", (email,))[0][0]


# ================================================================ 495 — ciorna facturii pe server
def test_def_495_factura_inceputa_se_regaseste_pe_alt_calculator(patron, browser, request, firma_emit):
    """495. Factură: ciorna facturii e salvată doar în browser; pe alt calculator nu se regăsește.
    Pașii: contabilul-șef începe o factură (clientul DANTE, linia „Servicii de consultanță…” 2 × 150) și nu o emite -> pe ALT calculator
    (alt browser, fără nimic în stocarea lui), același cont, aceeași firmă -> „Emite factură”: anunțul „Factura începută … a fost
    păstrată”, clientul și linia cum le-a lăsat, totalul 363,00 (300 + 21%). „Renunță la factură” -> ciorna dispare și de pe server."""
    pg = patron.pg
    tid = firma_emit["tenant_id"]
    _emiterea(patron, firma_emit)
    with pg.expect_response(lambda r: "/ciorne-formular/factura" in r.url and r.request.method == "PUT", timeout=15000):
        pg.fill("#em-cui", CUI_DANTE)
        pg.fill("#em-nume", "DANTE INTERNATIONAL SA")
        pg.dispatch_event("#em-nume", "input")
        pg.fill("#em-l0-descriere", PRODUS)
        pg.dispatch_event("#em-l0-descriere", "input")
        pg.fill("#em-l0-cantitate", "2")
        pg.dispatch_event("#em-l0-cantitate", "input")
        pg.fill("#em-l0-pret_unitar", "150")
        pg.dispatch_event("#em-l0-pret_unitar", "input")
    pg.wait_for_timeout(1500)    # ultima tastă: trimisă după pauza ciornei
    patron.captura("calculatorul_1")
    assert sql("SELECT count(*) FROM public.ciorne_formular WHERE user_id = %s AND tenant_id = %s AND formular = 'factura'", (_uid(PATRON), tid))[0][0] == 1
    with ecran_cont(browser, request, PATRON) as alt:                     # „alt calculator”: alt browser, stocarea lui goală
        _emiterea(alt, firma_emit)
        p2 = alt.pg
        assert p2.evaluate("() => Object.keys(localStorage).filter(k => k.startsWith('iconta_ciorna_factura')).length") == 0
        assert "a fost păstrată" in p2.inner_text("#em-ciorna"), p2.inner_text("#em-ciorna")
        assert p2.input_value("#em-cui") == CUI_DANTE and p2.input_value("#em-nume") == "DANTE INTERNATIONAL SA"
        assert (p2.input_value("#em-l0-descriere"), p2.input_value("#em-l0-cantitate"), p2.input_value("#em-l0-pret_unitar")) == \
            (PRODUS, "2", "150")
        p2.wait_for_function("() => (document.querySelector('#em-total') || {innerText: ''}).innerText.includes('363,00')", timeout=10000)
        assert "300,00" in p2.inner_text("#em-total")                    # baza 2 × 150; TVA 63,00 (21%)
        alt.captura("calculatorul_2")
        p2.click("#em-renunta")
        p2.locator("button", has_text="Da, renunț la factură").click()
        p2.wait_for_function("() => !(document.querySelector('#em-ciorna') || {innerText: ''}).innerText.includes('a fost păstrată')",
                             timeout=10000)
        p2.wait_for_timeout(800)
    assert sql("SELECT count(*) FROM public.ciorne_formular WHERE tenant_id = %s AND formular = 'factura'", (tid,))[0][0] == 0


def test_def_495_ciorna_veche_din_browser_urca_pe_server(patron, browser, request, firma_emit):
    """495, documentul VECHI: o ciornă rămasă în browser de dinainte de reparație (forma ei, în stocarea browserului) urcă pe server la
    prima deschidere a formularului și se reface; copia din browser se șterge după ce serverul a primit-o; apoi se regăsește și pe alt
    calculator."""
    pg = patron.pg
    tid, uid = firma_emit["tenant_id"], _uid(PATRON)
    veche = {"v": 1, "salvat_la": "2026-10-20T09:15:00.000Z", "moneda": "RON", "scadentaScrisa": False, "pleacaMarfa": None,
             "semnMarfa": None, "stareCui": None, "campuri": {"em-cui": CUI_DANTE, "em-nume": "Client Ciorna Veche SRL"},
             "linii": [{"descriere": PRODUS, "cantitate": 3, "um": "ora", "pret_unitar": 100, "cota_tva": 21, "cota_propusa": 21,
                        "articol_id": None, "categorie_tva": None}]}
    patron.firma(firma_emit["nume"])
    pg.evaluate("([k, v]) => localStorage.setItem(k, v)", ["iconta_ciorna_factura:%d:%d" % (uid, tid), json.dumps(veche)])
    _card(patron, "facturi", "#fac-emite")
    with pg.expect_response(lambda r: "/ciorne-formular/factura" in r.url and r.request.method == "PUT", timeout=15000):
        pg.click("#fac-emite")
    pg.wait_for_selector("#em-l0-descriere", timeout=25000)
    assert "a fost păstrată" in pg.inner_text("#em-ciorna") and "20.10.2026" in pg.inner_text("#em-ciorna"), pg.inner_text("#em-ciorna")
    assert pg.input_value("#em-nume") == "Client Ciorna Veche SRL" and pg.input_value("#em-l0-cantitate") == "3"
    patron.captura("vechi_refacuta")
    pg.wait_for_timeout(500)
    assert pg.evaluate("(k) => localStorage.getItem(k)", "iconta_ciorna_factura:%d:%d" % (uid, tid)) is None
    pe_server = sql("SELECT continut FROM public.ciorne_formular WHERE user_id = %s AND tenant_id = %s AND formular = 'factura'", (uid, tid))
    assert pe_server and pe_server[0][0]["campuri"]["em-nume"] == "Client Ciorna Veche SRL", pe_server
    with ecran_cont(browser, request, PATRON) as alt:
        _emiterea(alt, firma_emit)
        assert alt.pg.input_value("#em-nume") == "Client Ciorna Veche SRL"
        alt.captura("vechi_alt_calculator")


# ================================================================ 488 — căutarea în lista de articole
def test_def_488_articolul_din_stoc_se_cauta_in_lista(patron, firma_emit):
    """488. Factură: lista de articole fără căutare, greu de folosit la sute de articole.
    Pașii: firma cu 40 de articole în stoc -> Emite factură -> pe linie, în „Caută articolul în stoc”, scrie „surub” (fără diacritice):
    lista arată numai „Șurub M8 zincat” (plus „— fără articol —”); îl alege -> denumirea și UM-ul vin din articol. Scrie „xyz”: lista spune
    „Nimic din listă nu conține «xyz»”, iar articolul ales rămâne ales."""
    _intrari(firma_emit, [("Marfa diversa %02d" % i, 5, 10) for i in range(1, 40)] + [("Șurub M8 zincat", 100, 0.5)])
    _emiterea(patron, firma_emit)
    pg = patron.pg
    toate = pg.locator("#em-l0-articol option").count()
    assert toate == 41, toate                                              # 40 de articole + „— fără articol (serviciu) —”
    pg.fill("#em-l0-cauta-articol", "surub")
    pg.dispatch_event("#em-l0-cauta-articol", "input")
    optiuni = pg.eval_on_selector_all("#em-l0-articol option", "els => els.map(e => e.textContent.trim())")
    assert optiuni == ["— fără articol (serviciu) —", "Șurub M8 zincat · stoc 100 buc"], optiuni
    patron.captura("cautare")
    pg.select_option("#em-l0-articol", label="Șurub M8 zincat · stoc 100 buc")
    pg.wait_for_function("() => document.querySelector('#em-l0-descriere').value === 'Șurub M8 zincat'", timeout=5000)
    assert pg.input_value("#em-l0-um") == "buc"
    pg.fill("#em-l0-cauta-articol", "xyz")
    pg.dispatch_event("#em-l0-cauta-articol", "input")
    optiuni = pg.eval_on_selector_all("#em-l0-articol option", "els => els.map(e => e.textContent.trim())")
    assert "Nimic din listă nu conține „xyz”" in optiuni, optiuni
    assert pg.locator("#em-l0-articol option:checked").inner_text().startswith("Șurub M8 zincat")
    patron.captura("nimic_gasit")
    pg.click("#em-renunta")
    pg.locator("button", has_text="Da, renunț la factură").click()


# ================================================================ 470 — „nota …” deschide nota facturii
def _factura_din_istoric(e, firma, factura_id):
    """Facturi -> Istoric facturi -> rândul facturii. Lista lunii arată ultimele 10 facturi; o factură mai veche se aduce cu
    „Vezi și facturile mai vechi din această lună” (`facturi_ecran.istoricFacturi`, câte 10 în plus), ca la contabil."""
    pg = e.pg
    e.firma(firma["nume"])
    _card(e, "facturi", "#fac-istoric")
    pg.click("#fac-istoric")
    rand = ".fac-frand-btn[data-id='%s']" % factura_id
    pg.wait_for_selector(".fac-frand-btn", timeout=25000)
    while not pg.locator(rand).count():
        assert pg.locator("#fac-mai-multe").count(), "factura %s nu e în Istoric facturi" % factura_id
        pg.click("#fac-mai-multe")
        pg.wait_for_function("(n) => document.querySelectorAll('.fac-frand-btn').length > n",
                             arg=pg.locator(".fac-frand-btn").count(), timeout=25000)
    pg.click(rand)
    pg.wait_for_selector("#fd-pdf", timeout=25000)


def test_def_470_nota_din_factura_se_deschide_pe_nota_ei(patron, firma_emit):
    """470. Factură: linkul „nota din…” deschide Registrul jurnal de la început, nu nota facturii.
    Pașii: luna are 25 de facturi emise (25 de note) -> Istoric facturi -> prima și ultima factură -> „nota …”: Registrul jurnal se
    deschide cu rândul notei FACTURII evidențiat și adus pe ecran (nu primul rând al lunii)."""
    facturi = [emite_api(patron, firma_emit) for _ in range(25)]
    s = firma_emit["schema"]
    for f in (facturi[0], facturi[-1]):
        nid = sql('SELECT id FROM "%s".inregistrari WHERE factura_id = %%s AND sursa = \'facturi\' ORDER BY id LIMIT 1' % s,
                  (f["factura_id"],))[0][0]
        _factura_din_istoric(patron, firma_emit, f["factura_id"])   # prima factură e a 25-a din listă: „Vezi și … mai vechi”
        pg = patron.pg
        pg.click("#fd-vezi-nota")
        rand = ".fereastra:last-of-type tbody.tn-nota[data-nota-id='%d']" % nid   # [lotul 12, 617] rândul notei în tabelul de note
        pg.wait_for_selector(rand, timeout=20000)
        pg.wait_for_timeout(600)
        assert "val-evidentiat" in (pg.get_attribute(rand, "class") or ""), "nota facturii nu e evidențiată"
        # rândul notei (`tr.tn-rand`) pe ecran; detaliul, deschis sub el, poate trece de marginea ferestrei
        pe_ecran = pg.eval_on_selector(rand + " tr.tn-rand", "el => { const r = el.getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight; }")
        assert pe_ecran, "rândul notei facturii nu e pe ecran"
        assert pg.locator(".fereastra:last-of-type .val-evidentiat").count() == 1
        patron.captura("factura_%d" % f["factura_id"])


# ================================================================ 462 — șablonul trece prin verificările facturii
def _sablon_nou(e, firma, cui, nume):
    pg = e.pg
    e.firma(firma["nume"])
    _card(e, "facturi", "#fac-recurente")
    pg.click("#fac-recurente")
    pg.wait_for_selector("#fr-add", timeout=20000)
    pg.click("#fr-add")
    pg.wait_for_selector("#fr-l0-descriere", timeout=20000)
    pg.fill("#fr-cui", cui)
    pg.fill("#fr-nume", nume)
    pg.fill("#fr-l0-descriere", PRODUS)
    pg.dispatch_event("#fr-l0-descriere", "input")
    pg.wait_for_function("() => (document.querySelector('#fr-l0-cota') || {textContent: ''}).textContent.includes('21')", timeout=10000)
    pg.fill("#fr-l0-cantitate", "1")
    pg.dispatch_event("#fr-l0-cantitate", "input")
    pg.fill("#fr-l0-pret_unitar", "100")
    pg.dispatch_event("#fr-l0-pret_unitar", "input")
    pg.fill("#fr-zi", "5")


def test_def_462_sablonul_trece_prin_verificarile_facturii_obisnuite(patron, firma_emit):
    """462. Facturi recurente: șablonul ocolește verificările facturii obișnuite.
    Pașii: firma fără forma juridică în Date firmă (factura obișnuită se refuză: Legea 31/1990 art.74 alin.(1), (3)) -> Facturi ->
    Facturi recurente -> „+ Șablon nou” (DANTE, „Servicii de consultanță…” 1 × 100, ziua 5) -> „Salvează șablonul”: refuzul facturii
    obișnuite pe ecran („Factura lunară ar fi refuzată la emitere: … forma juridică …”), niciun șablon salvat. Codul unui client din alt
    stat („DE123456789”): refuzul stă lângă „CUI beneficiar”. Cu Date firmă completate, același șablon se salvează — și nu lasă nicio
    factură emisă în urma probei."""
    s = firma_emit["schema"]
    scoate_forma_si_capitalul(patron, firma_emit)
    _sablon_nou(patron, firma_emit, CUI_DANTE, "DANTE INTERNATIONAL SA")
    pg = patron.pg
    pg.click("#fr-salveaza")
    pg.wait_for_function("() => (document.querySelector('#fr-rezultat') || {innerText: ''}).innerText.includes('forma juridic')", timeout=20000)
    txt = pg.inner_text("#fr-rezultat")
    assert "Factura lunară ar fi refuzată la emitere" in txt and "Legea 31/1990" in txt, txt
    patron.captura("fara_forma")
    assert sql('SELECT count(*) FROM "%s".facturi_recurente' % s)[0][0] == 0
    pregateste_firma(patron, firma_emit)                                   # Date firmă completate la loc (forma SRL, capitalul)
    _sablon_nou(patron, firma_emit, "DE123456789", "Kunde GmbH")
    pg.click("#fr-salveaza")
    pg.wait_for_selector("#fr-cui[aria-invalid='true']", timeout=20000)
    assert "client din alt stat" in patron.fereastra(), patron.fereastra()
    patron.captura("client_strain")
    assert sql('SELECT count(*) FROM "%s".facturi_recurente' % s)[0][0] == 0
    _sablon_nou(patron, firma_emit, CUI_DANTE, "DANTE INTERNATIONAL SA")
    pg.click("#fr-salveaza")
    pg.wait_for_selector("#fr-add", timeout=20000)                       # salvat: înapoi la lista șabloanelor
    pg.locator(".pf-frand", has_text="DANTE INTERNATIONAL SA").wait_for(timeout=10000)
    patron.captura("salvat")
    assert sql('SELECT tert_nume, zi_emitere FROM "%s".facturi_recurente' % s) == [("DANTE INTERNATIONAL SA", 5)]
    assert sql('SELECT count(*) FROM "%s".facturi' % s)[0][0] == 0         # proba emiterii nu lasă nicio factură
    assert sql('SELECT count(*) FROM "%s".inregistrari' % s)[0][0] == 0


# ================================================================ C84 — livrarea intracomunitară de bunuri, din „Emite factură”
def _vies(pg):
    pg.route("**/verifica-vies**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(
        {"valid": True, "tara": "DE", "nume": "Kunde Handels GmbH", "adresa": "Hauptstrasse 1\n10115 Berlin"})))


def test_def_c84_livrarea_ic_de_bunuri_se_face_din_emite_factura_si_descarca_stocul(patron, firma_emit):
    """C84 (decizia Costin b). Pașii, pe o firmă cu stocul cantitativ-valoric (ca F1): articolul „Marfa IC E2E” are 20 buc la 4,00 lei ->
    Operațiuni speciale -> „Livrare/prestare intracomunitară” -> Tip: Bunuri: caseta „Livrarea intracomunitară de bunuri se face din
    «Emite factură» …”, fără „Generează nota” -> „Deschide «Emite factură»” -> CUI „DE123456789” -> Verifică (VIES: valid, DE) -> articolul
    din stoc, 2 buc × 100,00, cota 0%, categoria „livrare intracomunitară” -> Emite -> „Da, pleacă marfa”: factura 200,00, TVA 0,00
    (CF art.294 alin.(2) lit.a), linia cu categoria livrării intracomunitare, ieșirea din stoc 2 buc / 8,00 lei (2 × CMP 4,00), stoc rămas 18.
    Tip: Servicii: formularul operațiunii rămâne, cu „Generează nota” și contul 704."""
    s = firma_emit["schema"]
    _intrari(firma_emit, [("Marfa IC E2E", 20, 4)])
    pg = patron.pg
    _vies(pg)
    patron.firma(firma_emit["nume"])
    _card(patron, "operatiuni", "[data-op]")
    pg.locator("button[data-op]", has_text="Livrare/prestare intracomunitară").first.click()
    pg.wait_for_selector("#op-tip", timeout=10000)
    pg.select_option("#op-tip", "servicii")
    pg.dispatch_event("#op-tip", "change")
    # [lotul 13, 504] contul pornește gol (contul uzual 704 e în explicația câmpului)
    assert pg.is_visible("#op-trimite") and pg.input_value("#op-cont_venit") == "" and not pg.is_visible("#op-spre-emitere")
    pg.select_option("#op-tip", "bunuri")
    pg.dispatch_event("#op-tip", "change")
    assert pg.is_visible("#op-spre-emitere") and not pg.is_visible("#op-trimite")
    assert "Livrarea intracomunitară de bunuri se face din «Emite factură»" in pg.inner_text("#op-spre-emitere")
    patron.captura("operatiuni_bunuri")
    pg.click("#op-spre-emitere-buton")
    pg.wait_for_selector(".fereastra:last-of-type #em-l0-articol", timeout=25000)
    pg.fill("#em-cui", "DE123456789")
    pg.dispatch_event("#em-cui", "change")
    pg.click("#em-verifica")
    pg.wait_for_function("() => (document.querySelector('#em-cui-stare') || {innerText: ''}).innerText.includes('valid în VIES')", timeout=10000)
    assert pg.input_value("#em-tara") == "DE"
    pg.fill("#em-oras", "Berlin")
    pg.fill("#em-l0-cauta-articol", "marfa ic")
    pg.dispatch_event("#em-l0-cauta-articol", "input")
    pg.select_option("#em-l0-articol", label=pg.locator("#em-l0-articol option", has_text="Marfa IC E2E").first.inner_text())
    pg.wait_for_function("() => document.querySelector('#em-l0-descriere').value === 'Marfa IC E2E'", timeout=5000)
    pg.wait_for_timeout(1200)                                              # propunerea cotei pentru denumire
    pg.fill("#em-l0-cantitate", "2")
    pg.dispatch_event("#em-l0-cantitate", "input")
    pg.fill("#em-l0-pret_unitar", "100")
    pg.dispatch_event("#em-l0-pret_unitar", "input")
    pg.select_option("#em-l0-cota", "0")
    pg.wait_for_selector("#em-l0-categorie", state="visible", timeout=5000)
    pg.select_option("#em-l0-categorie", "livrare_ic")
    patron.captura("emitere_completata")
    pg.click("#em-emite")
    pg.wait_for_selector("#em-poarta-da", timeout=20000)
    pg.click("#em-poarta-da")
    # [lotul 12, C84, decizia Costin 12.3 pct.7] după „Pleacă marfa acum?”, întrebarea dovezii transportului (livrarea intracomunitară)
    pg.wait_for_selector("#em-dovada-da", timeout=20000)
    pg.click("#em-dovada-da")
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=30000)
    rez = pg.inner_text("#em-rezultat")
    assert "total 200,00" in rez and "1 articol descărcat din gestiune" in rez, rez
    assert pg.locator("#em-rezultat .em-avertisment-emitere").count() == 0, "cu dovada transportului: niciun avertisment"
    patron.captura("emisa")
    fid, total, tva, tara = sql('SELECT id, total::text, tva::text, tert_tara FROM "%s".facturi ORDER BY id DESC LIMIT 1' % s)[0]
    assert (total, tva, tara) == ("200.00", "0.00", "DE"), (total, tva, tara)
    assert sql('SELECT categorie_tva, cantitate::text FROM "%s".factura_linii WHERE factura_id = %%s' % s, (fid,)) == [("livrare_ic", "2.000")]
    assert sql('SELECT tip, cantitate::text, valoare::text FROM "%s".miscari_stoc WHERE factura_id = %%s' % s, (fid,)) == \
        [("iesire", "2.000", "8.00")]
    from core import db, stocuri_cv_api
    with db.get_conn(s) as c:
        art = [a for a in stocuri_cv_api.articole(c, s) if a["denumire"] == "Marfa IC E2E"][0]
        c.rollback()
    assert Decimal(art["stoc"]) == Decimal("18"), art
