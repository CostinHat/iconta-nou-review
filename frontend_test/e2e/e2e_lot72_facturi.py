# -*- coding: utf-8 -*-
"""Lotul 7, comanda 7.2 (Costin 17.10.2026, verbatim în DECIZII „Comanda 7.2”): facturarea și datele firmei — 303, 304, 305, 306, 307,
308, 318 — pe aplicația din index, pe baza de TEST, pe firma nouă a fișierului (`firma_e2e`; la 304, cu stoc cantitativ-valoric)."""
import datetime as _dt
import json

from conftest import sql
from e2e_bloc_a import AZI, PRODUS, _api, _card, _deschide_emiterea, _ok, pregateste_firma
from e2e_bloc_c import firma_cv  # noqa: F401 — fixture (304: articol de stoc)

IE = {"tert_nume": "Client Irlanda E2E Ltd", "tert_cui": "IE9999999ZZ", "tert_adresa": "1 Grand Canal Square", "tert_oras": "Dublin",
      "tert_tara": "IE"}


def _emite_ie(e, firma, data_emitere=None):
    """Factura de servicii către clientul din Irlanda (0%, prestare cu locul în afara României), pe ruta formularului; `data_emitere`
    implicit azi — [lotul 10, 383] pentru o declarație, în perioada încheiată pe care se generează (`conftest.perioada_incheiata`)."""
    zi = data_emitere or AZI
    corp = dict(IE, linii=[{"descriere": PRODUS, "cantitate": 1, "um": "buc", "pret_unitar": 1000.0, "cota_tva": 0, "cota_propusa": 0,
                            "articol_id": None, "categorie_tva": "serviciu_extern"}],
                moneda="RON", tip_operatiune="normal", bon_fiscal_nr=None, bon_fiscal_data=None, data_emitere=zi.isoformat(),
                data_scadenta=(zi + _dt.timedelta(days=30)).isoformat(), tip="factura")
    return _ok(_api(e, "POST", "/tenants/%d/facturi/emite" % firma["tenant_id"], corp), "factura IE")


def test_def_303_verifica_cui_spune_ca_asteapta_si_ce_s_a_intamplat(patron, firma_e2e):
    """303. „Verifică” CUI nu arăta nimic cât aștepta ANAF; părea stricat.
    Pașii: Emite factură -> CUI -> „Verifică” cu ANAF lent: butonul spune „Se verifică…” și e blocat cât așteaptă; ANAF nu răspunde (502
    cu refuzul serverului) -> sub câmp: „ANAF nu răspunde acum la verificarea CUI …”, nu „verificarea a eșuat”; butonul revine."""
    from core import anaf_api
    pregateste_firma(patron, firma_e2e)
    _deschide_emiterea(patron, firma_e2e["nume"])
    pg = patron.pg
    pg.route("**/verifica-cui/**", lambda r: (pg.wait_for_timeout(2500), r.fulfill(
        status=502, content_type="application/json", body=json.dumps({"detail": anaf_api.MESAJ_ANAF_NU_RASPUNDE}))))
    pg.fill("#em-cui", "14399840")
    pg.click("#em-verifica")
    pg.wait_for_function("() => document.querySelector('#em-verifica').textContent === 'Se verifică…'", timeout=5000)
    assert pg.eval_on_selector("#em-verifica", "b => b.disabled") is True
    patron.captura("se_verifica")
    pg.wait_for_function("() => document.querySelector('#em-verifica').textContent === 'Verifică'", timeout=20000)
    stare = pg.inner_text("#em-cui-stare")
    patron.captura("anaf_nu_raspunde")
    assert stare == anaf_api.MESAJ_ANAF_NU_RASPUNDE and "a eșuat" not in stare, stare
    assert pg.eval_on_selector("#em-verifica", "b => b.disabled") is False
    pg.unroute("**/verifica-cui/**")
    # 502-ul de mai sus l-a dat testul (ANAF simulat căzut), nu aplicația: nu e o cădere de raportat de fixture
    patron.cereri_rele[:] = [x for x in patron.cereri_rele if "/verifica-cui/" not in x[1]]


def test_def_304_refuzul_clientului_vechi_dispare_si_vine_inaintea_intrebarii(patron, firma_cv):
    """304. Refuzul calculat pentru clientul vechi (livrare intracomunitară, „țara clientului: RO”) rămânea după schimbarea clientului;
    refuzul venea abia după „Pleacă marfa acum?”; mesajul de jos acoperea „Emite factură”.
    Pașii (firmă cu stoc): Emite factură -> client RO, articolul din stoc pe linie, cota 0%, „livrare intracomunitară” -> „Emite”: refuzul
    vine ÎNAINTE de întrebare („țara clientului: RO”), fără „Pleacă marfa acum?”; „Emite factură” rămâne vizibil, deasupra mesajului nu e
    nimic peste el; schimbat clientul pe unul din Irlanda -> refuzul dispare."""
    pregateste_firma(patron, firma_cv)
    _deschide_emiterea(patron, firma_cv["nume"])
    pg = patron.pg
    pg.fill("#em-cui", "14399840")
    pg.fill("#em-nume", "DANTE INTERNATIONAL SA")
    pg.select_option("#em-l0-articol", label=pg.locator("#em-l0-articol option", has_text=firma_cv["marfa"]).first.inner_text())
    pg.fill("#em-l0-cantitate", "1")
    pg.fill("#em-l0-pret_unitar", "10")
    pg.select_option("#em-l0-cota", "0")
    pg.wait_for_selector("#em-l0-categorie", state="visible", timeout=10000)
    pg.select_option("#em-l0-categorie", "livrare_ic")
    pg.click("#em-emite")
    pg.wait_for_function("() => [...document.querySelectorAll('.msg-eroare')].some((m) => m.innerText.includes('țara clientului: RO'))",
                         timeout=30000)
    assert "Pleacă marfa acum?" not in pg.inner_text("#em-rezultat"), "refuzul vine înaintea întrebării"
    bara = pg.evaluate("""() => { const b = document.querySelector('#em-emite').getBoundingClientRect(); const x = b.left + b.width / 2,
        y = b.top + b.height / 2; const e = document.elementFromPoint(x, y); return e && (e.id === 'em-emite' || !!e.closest('#em-emite')); }""")
    assert bara, "„Emite factură” e acoperit"
    patron.captura("refuz_inainte_de_intrebare")
    pg.fill("#em-cui", "IE9999999ZZ")
    pg.dispatch_event("#em-cui", "change")
    pg.wait_for_function("() => ![...document.querySelectorAll('.msg-eroare')].some((m) => m.innerText.includes('țara clientului: RO'))",
                         timeout=10000)
    patron.captura("refuz_curatat")


def test_def_305_nota_cotei_si_localitatea_din_vies(patron, firma_e2e):
    """305. Textul „cota TVA e propusă automat pe baza denumirii” apărea și la articolele din stoc; localitatea clientului străin rămânea
    goală deși VIES dă adresa.
    Pașii: Emite factură: nota de sub „Produse și servicii” spune că la articolul din stoc cota vine din articol; CUI irlandez -> „Verifică”
    (VIES răspunde cu adresa pe două rânduri) -> țara devine Irlanda, iar „Localitatea clientului” se completează din adresă."""
    pregateste_firma(patron, firma_e2e)
    _deschide_emiterea(patron, firma_e2e["nume"])
    pg = patron.pg
    nota = pg.inner_text(".em-sectiune .camp-eticheta .tip-micut")
    assert "la un articol din stoc, cota TVA vine din articol" in nota, nota
    pg.route("**/verifica-vies**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(
        {"valid": True, "nume": "CLIENT IRLANDA E2E LTD", "adresa": "1 GRAND CANAL SQUARE\nDUBLIN 2", "tara": "IE"})))
    pg.fill("#em-cui", "IE9999999ZZ")
    pg.click("#em-verifica")
    pg.wait_for_function("() => document.querySelector('#em-oras') && document.querySelector('#em-oras').value !== ''", timeout=15000)
    patron.captura("localitatea_din_vies")
    assert (pg.input_value("#em-tara"), pg.input_value("#em-oras")) == ("IE", "DUBLIN 2"), (pg.input_value("#em-tara"),
                                                                                          pg.input_value("#em-oras"))
    pg.unroute("**/verifica-vies**")


def test_def_306_factura_ue_categoria_codul_de_tva_si_tara(patron, firma_e2e):
    """306. Detaliul facturii arăta doar „0%”, fără categoria TVA; pe PDF clientul UE avea „CUI:” în loc de „Cod TVA:” și adresa fără țară.
    Pașii: factura către clientul din Irlanda (serviciu, 0%, „prestare cu locul în afara României”) -> detaliul: sub 0% categoria; clientul
    cu „Cod TVA IE…” și adresa cu „Irlanda”; PDF-ul: „Cod TVA: IE…” și „Irlanda”."""
    from e2e_bloc_a import _deschide_factura, _octeti
    pregateste_firma(patron, firma_e2e)
    f = _emite_ie(patron, firma_e2e)
    _deschide_factura(patron, firma_e2e, f["factura_id"])
    txt = patron.fereastra()
    patron.captura("detaliu")
    assert "Prestare de servicii cu locul în afara României" in txt, txt[:1500]
    assert "Cod TVA IE9999999ZZ" in txt and "Dublin, Irlanda" in txt, txt[:1500]
    pdf = _octeti(patron, "/tenants/%d/facturi/%d/pdf" % (firma_e2e["tenant_id"], f["factura_id"]))
    import io
    from pypdf import PdfReader
    text = " ".join(p.extract_text() for p in PdfReader(io.BytesIO(pdf)).pages)
    assert "Cod TVA: IE9999999ZZ" in text and "Irlanda" in text and "CUI: IE" not in text, text[:800]


def test_def_307_factura_catre_client_nestabilit_fara_termen_spv(patron, firma_e2e):
    """307. Termenul de 5 zile în SPV apărea și la factura către clientul nestabilit în România (Irlanda): fără obligație (OUG 120/2021
    art.10 alin.(1) și (1^1)), fără termen.
    Pașii: factura către clientul din Irlanda (serviciu, 0%) -> detaliul: „netrimisă în SPV · nu e obligatorie”, fără termen."""
    from e2e_bloc_a import _deschide_factura
    pregateste_firma(patron, firma_e2e)
    f = _emite_ie(patron, firma_e2e)
    _deschide_factura(patron, firma_e2e, f["factura_id"])
    txt = patron.fereastra()
    patron.captura("spv_neobligatorie")
    assert "netrimisă în SPV · nu e obligatorie" in txt and "termen" not in txt.split("netrimisă în SPV")[1][:80], txt[:1500]
    d = _ok(_api(patron, "GET", "/tenants/%d/facturi/%d" % (firma_e2e["tenant_id"], f["factura_id"]), None), "detaliu")
    assert d["stare_spv"]["obligatorie"] is False and d["stare_spv"]["termen"] is None, d["stare_spv"]


def test_def_308_ajutorul_importului_ubl_spune_ce_face(patron, firma_e2e):
    """308. Ajutorul spunea că importul UBL creează mereu o „cheltuială” (la firma cu stoc, marfa intră pe 371 / NIR), „Import e-Factura”
    în loc de „Importă XML UBL” și „patru-ochi” în loc de „validarea în doi”.
    Pașii: Facturi primite din SPV -> „?”: ajutorul spune „Importă XML UBL”, că importul nu scrie nicio notă, că la marfă contul e 371 cu
    NIR-ul și „validarea în doi”; fără „patru-ochi” și fără „creează cheltuiala”."""
    pregateste_firma(patron, firma_e2e)
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "facturi", "#fac-primite")
    pg.click("#fac-primite")
    pg.wait_for_selector("h2.pf-titlu [data-ajutor='F043']", timeout=20000)
    buton = pg.inner_text("label[data-actiune='POST /tenants/{tenant_id}/facturi-primite/import-xml']")
    pg.click("h2.pf-titlu [data-ajutor='F043']")
    pg.wait_for_selector(".fereastra:last-of-type .aj-continut", timeout=20000)
    text = pg.inner_text(".fereastra:last-of-type .aj-continut")
    patron.captura("ajutor_ubl")
    assert buton.strip().startswith("Importă XML UBL"), buton
    assert "Importă XML UBL" in text and "nu scrie nicio notă" in text and "371" in text and "NIR" in text, text[:600]
    assert "validarea în doi" in text and "patru-ochi" not in text and "creează cheltuiala" not in text, text[:600]


def test_def_318_cui_blocat_arata_blocat(patron, firma_e2e):
    """318. Date firmă: câmpul CUI blocat arăta ca unul editabil (alb, chenar albastru la clic).
    Pașii: Date firmă -> CUI: fundalul e al paginii (nu alb), iar la clic chenarul rămâne gri, fără umbra albastră."""
    from e2e_bloc_a import _card
    pregateste_firma(patron, firma_e2e)
    patron.firma(firma_e2e["nume"])
    _card(patron, "datefirma", "#df-cui")
    pg = patron.pg
    pg.click("#df-cui")
    st = pg.eval_on_selector("#df-cui", """e => { const s = getComputedStyle(e); const r = getComputedStyle(document.documentElement);
        return {bg: s.backgroundColor, border: s.borderTopColor, umbra: s.boxShadow}; }""")
    alb = pg.evaluate("() => { const d = document.createElement('div'); d.style.color = getComputedStyle(document.documentElement)"
                      ".getPropertyValue('--alb'); document.body.appendChild(d); const c = getComputedStyle(d).color; d.remove(); return c; }")
    patron.captura("cui_blocat")
    assert st["bg"] != alb and st["bg"] not in ("rgb(255, 255, 255)",), st
    assert st["umbra"] in ("none", ""), st
