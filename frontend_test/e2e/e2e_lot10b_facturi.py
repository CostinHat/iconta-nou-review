# -*- coding: utf-8 -*-
"""Lotul 10, comanda 10.2 (Costin 21.10.2026, verbatim în DECIZII „Comanda 10.2”), punctele de la factură:

- 7d (415): „la factură, mesajul roșu «Articolul n-are cota TVA» rămâne după ce cota a fost aleasă pe linie.”
- 7e (417): „pe ecranul de detaliu al facturii de stornare nu apare trimiterea la factura inițială (pe PDF apare).”
- 7f (419, partea facturii): „după stornare butonul rămâne «Se stornează…»; factura stornată rămâne «neîncasată» până la reîmprospătare.”
- 7g: „Factură în valută: cursul BNR și TVA-ul în lei nu se văd înainte de emitere.”

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ de test (`firma_noua`, pregătită pe rutele ecranelor —
`e2e_bloc_a.pregateste_firma`). Clientul DANTE INTERNATIONAL SA, CUI 14399840 — cifra de control verificată cu algoritmul din CLAUDE.md.
Factura în valută e datată 04.09.2026: cursul BNR EUR din acea zi e în cache-ul bazei de test, deci ecranul nu cere BNR-ului nimic."""
import datetime as _dt
from decimal import ROUND_HALF_UP, Decimal

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import AZI, ARTICOL, CLIENT, PRODUS, _api, _deschide_emiterea, _deschide_factura, _ok, articol_in_stoc, emite_api

ZI_VALUTA = _dt.date(2026, 9, 4)
ZI_CURS = _dt.date(2026, 9, 3)     # cursul comunicat în ziua anterioară facturii (CF art.290 alin.(2) + HG 1/2016 pct.35 alin.(1))


@pytest.fixture(scope="module")
def firma_fac_noua():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_fac(patron, firma_fac_noua):
    """Firma nouă, cu Date firmă, vectorul fiscal, seria și nomenclatorul (pregătirea e idempotentă: o valoare neschimbată nu scrie)."""
    from e2e_bloc_a import pregateste_firma
    pregateste_firma(patron, firma_fac_noua)
    return firma_fac_noua


def _lei(x):
    """Suma cum o scrie ecranul (`bani`): 1.234,56."""
    s = "{:,.2f}".format(float(x))
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _numar_pe_hartie(numar, serie="E2EA"):
    """„E2EA5” -> „E2EA nr. 5” (`facturi.mentiune_storno`)."""
    return "%s nr. %s" % (serie, numar[len(serie):]) if numar.startswith(serie) else "nr. %s" % numar


# ── 7d (415) ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_415_mesajul_articolului_fara_cota_dispare_cand_aleg_cota_pe_linie(patron, firma_fac):
    """415. Pașii: un articol cu stoc care nu e în nomenclatorul de produse („Marfa 415 fara cota”) -> Emite factură -> linia: alege
    articolul -> sub linie, mesajul roșu „Articolul „…” n-are cota TVA în nomenclator…, sau alege cota pe linie.” -> aleg 21% din lista
    cotei de pe linie -> mesajul dispare; cota rămâne 21%."""
    tid = firma_fac["tenant_id"]
    _ok(_api(patron, "POST", "/tenants/%d/stocuri/intrare" % tid, {"denumire": "Marfa 415 fara cota", "um": "buc", "data": AZI.isoformat(),
                                                                   "cantitate": 5, "pret_unitar": 10, "document": "NIR 415"}), "intrare")
    _deschide_emiterea(patron, firma_fac["nume"])
    pg = patron.pg
    pg.wait_for_selector("#em-l0-articol", timeout=20000)
    pg.select_option("#em-l0-articol", label=pg.eval_on_selector("#em-l0-articol",
                     "(s) => [...s.options].find((o) => o.textContent.startsWith('Marfa 415 fara cota')).textContent"))
    pg.wait_for_selector("#em-l0-cota-mesaj .caseta-atentie", timeout=15000)
    t = pg.inner_text("#em-l0-cota-mesaj")
    patron.captura("mesajul")
    assert "Articolul „Marfa 415 fara cota” n-are cota TVA în nomenclator" in t and "alege cota pe linie" in t, t
    pg.select_option("#em-l0-cota", "21")
    pg.wait_for_function("() => !document.querySelector('#em-l0-cota-mesaj').textContent.trim()", timeout=5000)
    patron.captura("cota_aleasa")
    assert pg.input_value("#em-l0-cota") == "21"
    assert not pg.query_selector("#em-l0-cota-mesaj .caseta-atentie")


# ── 7f (419) și 7e (417) ──────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_419_dupa_stornare_factura_e_stornata_fara_reimprospatare(patron, firma_fac):
    """419. Pașii: factură cu un articol din stoc, emisă cu „Pleacă marfa acum: Da” -> detaliul -> „Stornează” -> „Da” (marfa se întoarce)
    -> „Confirm stornarea”: confirmarea „Storno creat: …” rămâne pe ecran, iar FĂRĂ reîmprospătare: nicăieri „Se stornează…”, factura e
    „stornată” (nu „neîncasată”), iar „Stornează” și „Emite chitanță” nu mai sunt oferite."""
    aid = articol_in_stoc(patron, firma_fac, cantitate=22, pret=10)
    f = emite_api(patron, firma_fac, linii=[{"descriere": ARTICOL, "cantitate": 1, "um": "buc", "pret_unitar": 20.0, "cota_tva": 21,
                                              "cota_propusa": 21, "articol_id": aid}], pleaca_marfa=True)
    _deschide_factura(patron, firma_fac, f["factura_id"])
    pg = patron.pg
    assert "neîncasată" in pg.inner_text(".fd-antet-sus")
    pg.click("#fd-storno")
    pg.wait_for_selector("#fd-storno-retur", timeout=10000)
    pg.select_option("#fd-storno-retur", "true")
    pg.click("#fd-storno-ok")
    pg.wait_for_function("() => (document.querySelector('#fd-storno-rez') || {}).textContent && "
                         "document.querySelector('#fd-storno-rez').textContent.includes('Storno creat')", timeout=30000)
    patron.captura()
    sus = " ".join(pg.inner_text(".fd-antet-sus").split())
    assert "Se stornează" not in pg.inner_text("body"), sus
    assert "stornată" in sus and "neîncasată" not in sus, sus
    # [lotul 13, 675 — DS cap.1 v2.104] „Stornează” și „Emite chitanță” stau la locul lor, inactive, cu motivul (nu mai dispar)
    assert pg.get_attribute("#fd-storno", "aria-disabled") == "true" and "stornată integral" in pg.get_attribute("#fd-storno", "title"), sus
    assert pg.get_attribute("#fd-chitanta", "aria-disabled") == "true" and not pg.query_selector("#fd-storno-ok"), sus
    assert "Marfa a revenit în stoc: %s × 1 buc" % ARTICOL in pg.inner_text("#fd-storno-rez") and pg.is_visible("#fd-spre-istoric")


def test_def_417_detaliul_stornarii_trimite_la_factura_initiala(patron, firma_fac):
    """417. Pașii: factură emisă -> „Stornează” -> „Confirm stornarea” -> „Înapoi la Istoric facturi” -> rândul stornării -> detaliul ei
    arată, sub client, „Stornare factura <serie> nr. <n> din <dată>” (ca pe PDF) -> clic: se deschide factura inițială."""
    f = emite_api(patron, firma_fac)
    _deschide_factura(patron, firma_fac, f["factura_id"])
    pg = patron.pg
    assert not pg.query_selector("#fd-vezi-stornata")   # factura inițială n-are trimitere
    pg.click("#fd-storno")
    pg.wait_for_selector("#fd-storno-ok", timeout=10000)
    if pg.query_selector("#fd-storno-retur"):
        pg.select_option("#fd-storno-retur", "false")
    with pg.expect_response(lambda r: r.request.method == "POST" and r.url.endswith("/facturi/%d/storno" % f["factura_id"]),
                            timeout=30000) as rr:
        pg.click("#fd-storno-ok")
    st = rr.value.json()
    pg.wait_for_selector("#fd-spre-istoric", timeout=30000)
    pg.click("#fd-spre-istoric")
    pg.wait_for_selector(".fac-frand-btn[data-id='%s']" % st["factura_id"], timeout=20000)
    pg.click(".fac-frand-btn[data-id='%s']" % st["factura_id"])
    pg.wait_for_selector("#fd-vezi-stornata", timeout=25000)
    t = pg.inner_text("#fd-vezi-stornata")
    patron.captura("stornarea")
    # CF art.330 alin.(1) lit.b): „se înscriu numărul și data facturii corectate”
    assert t == "Stornare factura %s din %s" % (_numar_pe_hartie(f["numar"]), AZI.strftime("%d.%m.%Y")), t   # AZI-dat-de-test (emite_api)
    pg.click("#fd-vezi-stornata")
    # [lotul 11, deficiența 443, comanda Costin 11.1 pct.19: „seria și numărul se afișează separat peste tot (F6 nr. 1, nu F61)”] titlul
    # detaliului facturii inițiale e „Factură E2EA nr. 5” (`numarCuSerie`), nu „Factură E2EA5”
    from core.pdf_util import serie_nr
    serie = sql('SELECT serie FROM "%s".facturi WHERE id = %%s' % firma_fac["schema"], (f["factura_id"],))[0][0]
    pg.wait_for_function("(x) => [...document.querySelectorAll('.fd-antet h2')].some((h) => h.textContent.trim() === x)",
                         arg="Factură %s" % serie_nr(serie, f["numar"]), timeout=25000)
    patron.captura("initiala")


# ── 7g ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_valuta_cursul_bnr_si_tva_in_lei_se_vad_inainte_de_emitere(patron, firma_fac):
    """7g. Pașii: Emite factură -> data 04.09.2026 -> clientul -> linia (serviciu, 2 × 150, 21%) -> Monedă EUR: sub monedă, ÎNAINTE de
    emitere, „Curs BNR EUR <curs> din 04.09.2026”, „TVA în lei” și „Total în lei” -> „Emite factură” -> factura emisă are exact cursul,
    TVA-ul și totalul în lei arătate înainte."""
    s = firma_fac["schema"]
    # [lotul 11] HG 1/2016 pct.35 alin.(1): „cursul de schimb comunicat de respectiva bancă în ziua anterioară” — 03.09.2026
    curs = Decimal(str(sql("SELECT curs FROM public.curs_bnr_zilnic WHERE moneda = 'EUR' AND data = %s", (ZI_CURS,))[0][0]))
    _deschide_emiterea(patron, firma_fac["nume"])
    pg = patron.pg
    assert pg.is_hidden("#em-valuta")   # la RON nu e nimic de convertit
    pg.fill("#em-data", ZI_VALUTA.isoformat())
    pg.dispatch_event("#em-data", "change")
    for sel, v in CLIENT.items():
        pg.fill(sel, v)
    pg.fill("#em-l0-descriere", PRODUS)
    pg.wait_for_function("() => document.querySelector('#em-l0-cota').value === '21'", timeout=20000)
    pg.fill("#em-l0-pret_unitar", "150")
    pg.fill("#em-l0-cantitate", "2")
    pg.select_option("#em-moneda", "EUR")
    # 2 × 150 = 300 EUR; TVA 21% = 63,00 EUR; total 363,00 EUR — în lei la cursul zilei, rotunjit aritmetic (CF art.319 alin.(20) lit.j)
    tva_lei, total_lei = (_lei((Decimal(x) * curs).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) for x in ("63.00", "363.00"))
    pg.wait_for_function("(x) => (document.querySelector('#em-valuta-tva') || {innerText: ''}).innerText.includes(x)", arg=tva_lei,
                         timeout=20000)
    t = " ".join(pg.inner_text("#em-valuta").split())
    patron.captura("inainte_de_emitere")
    curs_txt = ("%.4f" % curs).replace(".", ",")
    assert "Curs BNR EUR %s din 03.09.2026" % curs_txt in t, t
    assert "TVA în lei %s lei" % tva_lei in t and "Total în lei %s lei" % total_lei in t, t
    with pg.expect_response(lambda r: r.url.endswith("/facturi/emite"), timeout=60000) as rr:
        pg.click("#em-emite")
    fid = rr.value.json()["factura_id"]
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=20000)
    patron.captura("emisa")
    r = sql('SELECT curs_bnr, data_curs::text, tva_lei, total_lei FROM "%s".facturi WHERE id = %%s' % s, (fid,))[0]
    assert r[1] == ZI_CURS.isoformat() and Decimal(str(r[0])) == curs, r
    assert (_lei(r[2]), _lei(r[3])) == (tva_lei, total_lei), r   # ce s-a arătat înainte = ce s-a scris pe factură


def test_def_419_clasa_chitanta_integrala_arata_incasata_fara_reimprospatare(patron, firma_fac):
    """Clasa lui 419 („factura stornată rămâne «neîncasată» până la reîmprospătare”), aceeași pe chitanță. Pașii: factură emisă, neîncasată
    -> detaliul -> „Emite chitanță” -> „Emite” pe suma întreagă: confirmarea „Chitanța … a fost emisă …” rămâne pe ecran, iar FĂRĂ
    reîmprospătare factura e „încasată”, „Emite chitanță” nu mai e oferit, chitanța apare cu PDF-ul ei."""
    f = emite_api(patron, firma_fac)
    _deschide_factura(patron, firma_fac, f["factura_id"])
    pg = patron.pg
    assert "neîncasată" in pg.eval_on_selector_all(".fd-stare", "els => els.map(e => e.innerText.trim())")
    pg.click("#fd-chitanta")
    pg.wait_for_selector("#fd-chit-ok", timeout=10000)
    pg.click("#fd-chit-ok")
    pg.wait_for_function("() => (document.querySelector('#fd-act-rez') || {innerText: ''}).innerText.includes('a fost emisă')", timeout=30000)
    stari = pg.eval_on_selector_all(".fd-stare", "els => els.map(e => e.innerText.trim())")
    patron.captura()
    assert "încasată" in stari and "neîncasată" not in stari, stari
    assert pg.get_attribute("#fd-chitanta", "aria-disabled") == "true" and pg.query_selector("[data-chpdf]"), stari   # [lotul 13, 675] inactiv, cu motivul


# ── C74 — o factură stornată integral (sau o stornare) nu se mai stornează ──────────────────────────────────────────────────
def test_def_c74_factura_stornata_nu_se_mai_storneaza(patron, firma_fac):
    """C74 (găsită de Code la 419, comanda 10.2). Până acum serverul accepta a doua stornare a unei facturi stornate integral și chiar
    stornarea unei stornări (CF art.330 alin.(1) lit.b): stornarea anulează valorile facturii corectate — nu mai rămâne nimic de stornat).
    Pașii: factură emisă -> stornată -> detaliul ei nu mai oferă „Stornează”; a doua cerere de stornare (alt tab, alt utilizator) e
    refuzată cu motivul, iar stornarea stornării la fel; niciun document nou scris.
    MUTAȚIA: refuzul facturii deja stornate scos din `facturi_api.storneaza` -> ROȘU (a doua stornare acceptată)."""
    s, tid = firma_fac["schema"], firma_fac["tenant_id"]
    f = emite_api(patron, firma_fac)
    st = _ok(_api(patron, "POST", "/tenants/%d/facturi/%d/storno" % (tid, f["factura_id"]), {}), "prima stornare")
    inainte = sql('SELECT count(*) FROM "%s".facturi' % s)[0][0]
    a_doua = _api(patron, "POST", "/tenants/%d/facturi/%d/storno" % (tid, f["factura_id"]), {})
    assert a_doua["status"] in (400, 409, 422), a_doua
    assert "deja stornată integral" in str(a_doua["json"]), a_doua
    a_stornarii = _api(patron, "POST", "/tenants/%d/facturi/%d/storno" % (tid, st["factura_id"]), {})
    assert a_stornarii["status"] in (400, 409, 422) and "ea însăși o stornare" in str(a_stornarii["json"]), a_stornarii
    assert sql('SELECT count(*) FROM "%s".facturi' % s)[0][0] == inainte      # nimic scris, niciun număr rezervat
    _deschide_factura(patron, firma_fac, f["factura_id"])
    patron.captura()
    # [lotul 13, 675] „Stornează” stă la locul lui, inactiv, cu motivul (nu mai dispare)
    assert patron.pg.get_attribute("#fd-storno", "aria-disabled") == "true", "factura stornată integral nu mai oferă „Stornează”"
    assert "stornată integral" in patron.pg.get_attribute("#fd-storno", "title")
