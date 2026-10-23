# -*- coding: utf-8 -*-
"""Lotul 11, subagentul V (comanda Costin 11.1, verbatim în DECIZII „Comanda 11.1”): 429 și deciziile din 10.3 (verbatim în DECIZII
„Comanda 10.3”) pe drumul real al contabilului.

- 429: „reevaluarea în valută e neschimbată pe producție (formular manual, fără propunere, fără curs BNR, nimic la închiderea lunii)” —
  un singur formular (Operațiuni nu-l mai are; butonul din Închidere lună e mereu acolo), ajustarea manuală în el, marcată.
- decizia 10.3: „Reevaluarea valutei se face pe soldul în valută al partenerului, inclusiv plățile nelegate”.

Pașii pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ a fișierului (pregătită pe rutele ecranelor). Datele de pornire se fac
pe rutele aplicației, cum le face ecranul: factura EUR pe ruta formularului de emitere (`POST facturi/emite`, fără curs: îl alege
serverul), validarea contării pe ruta „Validează” din Registrul jurnal, încasarea nealocată și creditul pe ruta notei din Registrul
jurnal (`POST jurnal`) — nicio inserare directă în bază. Clientul DANTE INTERNATIONAL SA, CUI 14399840 (cifra de control verificată cu
algoritmul din CLAUDE.md). Cursurile EUR din 25.08.2026 (5,2534) și 31.08.2026 (5,2586) sunt în cache-ul bazei de test."""
import datetime as _dt
import urllib.parse

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import AZI, CLIENT, PRODUS, _api, _ok

ZI = _dt.date(2026, 8, 26)


@pytest.fixture(scope="module")
def firma_v_noua():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_v(patron, firma_v_noua):
    from e2e_bloc_a import pregateste_firma
    pregateste_firma(patron, firma_v_noua)
    return firma_v_noua


def _factura_eur(patron, f):
    """Factura EUR din 26.08.2026 (2 × 150 EUR + 21% = 363,00 EUR), pe ruta formularului de emitere, cu contarea validată."""
    s = f["schema"]
    gasit = sql('SELECT id FROM "%s".facturi WHERE moneda = \'EUR\' AND data_emitere = %%s' % s, (ZI,))
    if gasit:
        return gasit[0][0]
    corp = {"linii": [{"descriere": PRODUS, "cantitate": 2, "um": "ora", "pret_unitar": 150.0, "cota_tva": 21, "cota_propusa": 21,
                       "articol_id": None}], "tert_nume": CLIENT["#em-nume"], "tert_cui": CLIENT["#em-cui"],
            "tert_adresa": CLIENT["#em-adresa"], "moneda": "EUR", "tert_tara": "RO", "tip_operatiune": "normal", "bon_fiscal_nr": None,
            "bon_fiscal_data": None, "data_emitere": ZI.isoformat(), "data_scadenta": (ZI + _dt.timedelta(days=30)).isoformat(),
            "tip": "factura"}
    fid = _ok(_api(patron, "POST", "/tenants/%d/facturi/emite" % f["tenant_id"], corp), "emitere")["factura_id"]
    for (nid,) in sql('SELECT id FROM "%s".inregistrari WHERE factura_id = %%s AND status = \'ciorna\'' % s, (fid,)):
        _ok(_api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (f["tenant_id"], nid), {}), "validarea contării")
    return fid


def _nota(patron, f, data, linie, doc):
    nid = _ok(_api(patron, "POST", "/tenants/%d/jurnal" % f["tenant_id"], {"data": data, "descriere": doc, "document_ref": doc,
                                                                            "linii": [linie]}), "nota")["id"]
    _ok(_api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (f["tenant_id"], nid), {}), "validarea notei")
    return nid


def _reevaluare_august(patron, f):
    """Închidere lună -> 08/2026 -> „Reevaluare valută” (tabelul propunerii)."""
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-inchidere")
    pg.wait_for_selector(".fereastra:last-of-type #il-prev", timeout=30000)
    for _ in range((AZI.year * 12 + AZI.month) - (2026 * 12 + 8)):
        pg.click(".fereastra:last-of-type #il-prev")
    pg.wait_for_function("() => document.querySelector('.fereastra:last-of-type .pf-intro').innerText.includes('08/2026')", timeout=60000)
    pg.wait_for_selector(".fereastra:last-of-type #il-reevaluare", timeout=60000)
    pg.click(".fereastra:last-of-type #il-reevaluare")
    pg.wait_for_selector(".fereastra:last-of-type #rv-tabel", timeout=60000)
    return pg


def test_def_429_un_singur_formular_operatiunile_nu_il_mai_au_iar_inchiderea_il_deschide_mereu(patron, firma_v):
    """Pașii: Operațiuni speciale -> nu mai există „Reevaluare lunară solduri valută” (formularul manual fără propunere și fără curs) ->
    Închidere lună, luna în curs (fără blocaj de reevaluare) -> butonul „Reevaluare valută” e acolo -> ecranul spune că luna e în curs."""
    f = firma_v
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-operatiuni")
    pg.wait_for_selector("[data-op]", timeout=20000)
    assert pg.locator("button[data-op='reeval_valuta']").count() == 0
    assert "Reevaluare lunară solduri valută" not in pg.inner_text(".fereastra:last-of-type")
    patron.captura("operatiuni")
    patron.firma(f["nume"])
    pg.click("#fa-inchidere")
    pg.wait_for_selector(".fereastra:last-of-type #il-reevaluare", timeout=60000)
    assert "buton-secundar" in pg.get_attribute(".fereastra:last-of-type #il-reevaluare", "class")   # fără blocaj: secundar, dar acolo
    pg.click(".fereastra:last-of-type #il-reevaluare")
    pg.wait_for_selector(".fereastra:last-of-type #rv-luna-in-curs", timeout=60000)
    assert pg.is_disabled(".fereastra:last-of-type #rv-genereaza")   # nota se generează după sfârșitul lunii
    patron.captura("luna_in_curs")


def test_def_429_plata_nelegata_scade_soldul_partenerului(patron, firma_v):
    """Decizia 10.3. Pașii: factura EUR 363,00 (1.906,98 lei) contată -> încasare din extras NEALOCATĂ facturii, 500,00 lei, cu
    partenerul pe rând (5124 = 4111) -> Închidere lună 08/2026 -> „Reevaluare valută”: rândul partenerului scade plata nelegată —
    267,82 EUR, 1.406,98 lei, „estimat din plățile în lei”, plata arătată sub sold —, cursul BNR 5,2586 din 31.08.2026, diferența 1,38 pe 765."""
    f = firma_v
    _factura_eur(patron, f)
    if not sql('SELECT 1 FROM "%s".inregistrari WHERE document_ref = \'Extras EUR 429\'' % f["schema"]):
        _nota(patron, f, "2026-08-28", {"debit": "5124", "credit": "4111", "suma": 500, "partener_cui": "14399840",
                                        "partener_nume": "DANTE INTERNATIONAL SA"}, "Extras EUR 429")
    pg = _reevaluare_august(patron, f)
    tr = pg.locator(".fereastra:last-of-type #rv-tabel tr:has-text('DANTE INTERNATIONAL SA')")
    rand = " ".join(tr.inner_text().split())
    # soldul estimat din plăți e EDITABIL (`editabile: ["sold_valuta"]` când partenerul are plăți): stă în câmpul rândului, nu în text —
    # `inner_text` nu citește valoarea unui <input>, deci se citește câmpul
    sold = tr.locator("input[data-camp='sold_valuta']")
    assert sold.count() == 1, rand
    patron.captura("plata_nelegata")
    # OMFP 1802/2014 pct.322 alin.(1): plata stinge creanța la cursul din evidență: 500 / (1.906,98 / 363) = 95,18 EUR -> 267,82 EUR;
    assert sold.input_value() == "267.82", sold.input_value()
    # pct.325 alin.(1): 267,82 x 5,2586 = 1.408,36; 1.408,36 - 1.406,98 = 1,38 -> 765
    for x in ("1.406,98", "estimat din plățile în lei", "plăți nelegate de factură", "500,00 lei din 28.08.2026", "5,2586",
              "1,38", "765"):
        assert x in rand, (x, rand)


def test_def_429_ajustarea_manuala_e_in_acelasi_formular_marcata(patron, firma_v):
    """Pașii: credit bancar în EUR (5121 = 1621, 4.970,00 lei; contul nu e propus: n-are factură, nu e disponibilitate) -> „Reevaluare
    valută” -> „Adaugă un cont” -> 1621, EUR, 1.000 -> rândul apare în tabel „adăugat de tine”, cu soldul în lei din evidență (4.970,00),
    cursul BNR 5,2586 și diferența 288,60 pe 665; un cont de avansuri (409) e refuzat lângă câmp, cu temeiul."""
    f = firma_v
    if not sql('SELECT 1 FROM "%s".inregistrari WHERE document_ref = \'Contract credit 429\'' % f["schema"]):
        _nota(patron, f, "2026-08-03", {"debit": "5121", "credit": "1621", "suma": 4970}, "Contract credit 429")
    pg = _reevaluare_august(patron, f)
    pg.click(".fereastra:last-of-type #rv-m-adauga")
    pg.wait_for_selector(".fereastra:last-of-type #rv-m0-cont", timeout=10000)
    pg.fill(".fereastra:last-of-type #rv-m0-cont", "1621")
    pg.dispatch_event(".fereastra:last-of-type #rv-m0-cont", "change")
    pg.wait_for_selector(".fereastra:last-of-type #rv-m0-moneda", timeout=30000)
    pg.fill(".fereastra:last-of-type #rv-m0-moneda", "EUR")
    pg.dispatch_event(".fereastra:last-of-type #rv-m0-moneda", "change")
    pg.wait_for_selector(".fereastra:last-of-type #rv-m0-sold_valuta", timeout=30000)
    pg.fill(".fereastra:last-of-type #rv-m0-sold_valuta", "1000")
    pg.dispatch_event(".fereastra:last-of-type #rv-m0-sold_valuta", "change")
    pg.wait_for_function("() => (document.querySelector(\".fereastra:last-of-type #rv-tabel tr[data-cheie='m1621']\") || {innerText: ''})"
                         ".innerText.includes('288,60')", timeout=60000)
    rand = " ".join(pg.inner_text(".fereastra:last-of-type #rv-tabel tr[data-cheie='m1621']").split())
    patron.captura("ajustare_manuala")
    # OMFP 1802/2014 pct.325 alin.(1): datoria de 1.000 EUR la 5,2586 = 5.258,60 lei; în evidență 4.970,00 -> +288,60 -> 665
    for x in ("adăugat de tine", "1621", "4.970,00", "5,2586", "288,60", "665"):
        assert x in rand, (x, rand)
    pg.click(".fereastra:last-of-type #rv-m-adauga")
    pg.wait_for_selector(".fereastra:last-of-type #rv-m1-cont", timeout=10000)
    pg.fill(".fereastra:last-of-type #rv-m1-cont", "409")
    pg.dispatch_event(".fereastra:last-of-type #rv-m1-cont", "change")
    # OMFP 1802/2014 pct.316 alin.(2): avansurile „nu mai fac obiectul evaluării în funcție de cursul valutar, la finele lunii”
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #rv-mesaj') || {innerText: ''}).innerText"
                         ".includes('pct.316 alin.(2)')", timeout=60000)
    assert pg.get_attribute(".fereastra:last-of-type #rv-m1-cont", "aria-invalid") == "true"
    patron.captura("avans_refuzat")


def test_def_c103_raspunsul_vechi_nu_acopera_ajustarea_scrisa(patron, firma_v):
    """C103 (găsită de Code la rularea țintită de după poarta 2 a lotului 11: testul ajustării manuale a picat o dată, la întâmplare).
    Pașii: credit bancar în EUR (5121 = 1621, 4.970,00 lei) -> Închidere lună 08/2026 -> „Reevaluare valută” -> „Adaugă un cont” ->
    1621, apoi EUR, apoi 1.000: ecranul recalculează propunerea pe server la fiecare câmp, deci pleacă trei cereri; răspunsul celei cu
    soldul sosește PRIMUL, apoi cele vechi (numai contul; contul și moneda) -> rândul rămâne cu diferența 288,60 pe 665 și fără eroare
    lângă câmpurile completate. Înainte: răspunsul vechi, sosit ultimul, se punea pe ecran peste cel nou (propunerea fără sold, sau
    refuzul „lipsește moneda” lângă o monedă scrisă). Răspunsurile se țin pe loc (`page.route`) și se eliberează în ordinea care producea
    defectul."""
    f = firma_v
    if not sql('SELECT 1 FROM "%s".inregistrari WHERE document_ref = \'Contract credit 429\'' % f["schema"]):
        _nota(patron, f, "2026-08-03", {"debit": "5121", "credit": "1621", "suma": 4970}, "Contract credit 429")
    pg = _reevaluare_august(patron, f)
    F = ".fereastra:last-of-type "
    pg.click(F + "#rv-m-adauga")
    pg.wait_for_selector(F + "#rv-m0-cont", timeout=10000)
    tinute = []
    propunerea = lambda url: "/reevaluare-valuta?" in url   # noqa: E731 — propunerea, nu nota (`/reevaluare-valuta/nota`)
    eliberate = set()

    def tine(route):
        tinute.append(route)

    pg.route(propunerea, tine)

    def scrie(camp, valoare):
        n = len(tinute)
        pg.fill(F + "#rv-m0-" + camp, valoare)
        pg.dispatch_event(F + "#rv-m0-" + camp, "change")
        for _ in range(100):
            if len(tinute) > n:
                return
            pg.wait_for_timeout(100)
        raise AssertionError("ecranul n-a recalculat după %s (%d cereri)" % (camp, len(tinute)))

    def elibereaza(route):
        if id(route.request) in eliberate:
            return
        eliberate.add(id(route.request))
        with pg.expect_response(lambda r: r.request == route.request):
            route.continue_()
        pg.wait_for_timeout(400)        # handlerul ecranului rulează după răspuns

    scrie("cont", "1621")
    scrie("moneda", "EUR")
    scrie("sold_valuta", "1000")
    pg.wait_for_timeout(800)            # și `change`-ul nativ al câmpului părăsit pornește o cerere: toate sunt acum ținute
    ultima = tinute[-1]
    assert "1000" in urllib.parse.unquote(ultima.request.url), ultima.request.url
    rand = lambda: " ".join(pg.inner_text(F + "#rv-tabel tr[data-cheie='m1621']").split())   # noqa: E731
    elibereaza(ultima)                  # răspunsul cererii cu soldul sosește PRIMUL
    pg.wait_for_selector(F + "#rv-tabel tr[data-cheie='m1621']", timeout=10000)
    assert "288,60" in rand(), rand()
    for route in reversed(tinute[:-1]):   # apoi cele vechi, cea mai veche ultima (numai contul)
        elibereaza(route)
    patron.captura("raspunsuri_vechi_ultimele")
    pg.unroute(propunerea)
    assert pg.locator(F + "#rv-tabel tr[data-cheie='m1621']").count() == 1, "răspunsul vechi a scos rândul ajustării de pe ecran"
    # OMFP 1802/2014 pct.325 alin.(1): 1.000 EUR la 5,2586 = 5.258,60 lei; în evidență 4.970,00 -> +288,60 -> 665
    for x in ("288,60", "665"):
        assert x in rand(), "răspunsul vechi, sosit ultimul, a înlocuit propunerea cu soldul scris: %r lipsește din %r" % (x, rand())
    for camp in ("cont", "moneda", "sold_valuta"):
        assert pg.get_attribute(F + "#rv-m0-" + camp, "aria-invalid") != "true", \
            "refuzul unei cereri vechi a marcat câmpul %s, deja completat" % camp
    assert pg.input_value(F + "#rv-m0-sold_valuta") == "1000"


def test_def_c103_campul_in_care_scrie_omul_ramane_cand_soseste_raspunsul(patron, firma_v):
    """C103, a doua fațetă. Pașii: „Reevaluare valută” -> „Adaugă un cont” -> 1621 (ecranul recalculează; răspunsul întârzie) -> contabilul
    trece la „Moneda” și scrie EUR -> sosește răspunsul pentru cont: formularul se re-desenează, iar „Moneda” rămâne EUR, cu focusul în
    ea. Înainte: re-desenarea punea câmpul la loc gol — ce tastase și nu confirmase încă dispărea (testul ajustării manuale a picat așa)."""
    f = firma_v
    if not sql('SELECT 1 FROM "%s".inregistrari WHERE document_ref = \'Contract credit 429\'' % f["schema"]):
        _nota(patron, f, "2026-08-03", {"debit": "5121", "credit": "1621", "suma": 4970}, "Contract credit 429")
    pg = _reevaluare_august(patron, f)
    F = ".fereastra:last-of-type "
    pg.click(F + "#rv-m-adauga")
    pg.wait_for_selector(F + "#rv-m0-cont", timeout=10000)
    tinute = []
    propunerea = lambda url: "/reevaluare-valuta?" in url   # noqa: E731
    cerute = []
    pg.on("request", lambda rq: cerute.append(rq.url) if propunerea(rq.url) else None)
    pg.route(propunerea, lambda route: tinute.append(route))
    pg.fill(F + "#rv-m0-cont", "1621")
    pg.dispatch_event(F + "#rv-m0-cont", "change")
    pg.fill(F + "#rv-m0-moneda", "EUR")          # cererea pentru cont e încă în zbor; „change” pe monedă n-a plecat
    for _ in range(50):
        if tinute:
            break
        pg.wait_for_timeout(100)
    assert tinute, "ecranul n-a recalculat după cont"
    pg.wait_for_timeout(500)
    for route in list(tinute):
        with pg.expect_response(lambda r, rq=route.request: r.request == rq):
            route.continue_()
    pg.wait_for_timeout(500)
    pg.unroute(propunerea)
    patron.captura("moneda_pastrata")
    assert pg.input_value(F + "#rv-m0-moneda") == "EUR", "re-desenarea a golit câmpul în care scria contabilul: %r" % \
        pg.input_value(F + "#rv-m0-moneda")
    assert pg.evaluate("() => document.activeElement && document.activeElement.id") == "rv-m0-moneda"
    # cel târziu la părăsirea câmpului, moneda ajunge în model ca orice editare: propunerea se recalculează cu ea
    pg.focus(F + "#rv-m0-sold_valuta")
    for _ in range(50):
        if any("EUR" in urllib.parse.unquote(u) for u in cerute):
            break
        pg.wait_for_timeout(100)
    assert any("EUR" in urllib.parse.unquote(u) for u in cerute), "moneda păstrată n-a ajuns în propunere: %s" % cerute
