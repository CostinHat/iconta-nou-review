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
