# -*- coding: utf-8 -*-
"""Lotul 8, comanda 8.1 (Costin 18.10.2026, verbatim în DECIZII „Comanda 8.1”): deficiențele din retestul lotului 7 pe producție —
321–340 — pe aplicația din index, pe baza de TEST, pe firma nouă a fișierului (`firma_e2e`) sau pe un cabinet nou (`cabinet_nou`).
Garda de clasă a lui 325 („nimic nu se deschide fără clicul omului”) stă în `conftest.GARDA_DESCHIDERI`, pe FIECARE ecran al plasei;
aici e numai proba ei pe cazul găsit (`#dec-tip`)."""
import contextlib
import datetime as _dt
import json
import time

import pytest

from conftest import BAZA, _ecran, ai_pregateste, sql, zile_de_acum
from e2e_bloc_a import AZI, CLIENT, PRODUS, _api, _card, _deschide_emiterea, _deschide_factura, _ok, cont_asistent, emite_api, \
    pregateste_firma
from e2e_lot72_cont import cabinet_nou, deschide_setari_panou  # noqa: F401 — fixture (321, 322)
from e2e_lot72_declaratii import _curata, _deschide_coada, _in_coada, _nota_facturii, _peste, _valideaza_notele


def _valideaza_luna(e, firma):
    """Notele ciornă ale lunii, validate (firma e comună fișierului: facturile testelor de dinainte lasă note nevalidate, iar poarta TVA
    refuză D300 cât TVA-ul lor lipsește din balanță — 10.10.2026, deficiențele 120 + 210)."""
    for (nid,) in sql('SELECT id FROM "%s".inregistrari WHERE status = \'ciorna\' AND date_trunc(\'month\', data) = date_trunc(\'month\', '
                      'CURRENT_DATE)' % firma["schema"]):
        _api(e, "POST", "/tenants/%d/jurnal/%d/valideaza" % (firma["tenant_id"], nid), {})


def _factura_fara_tva(e, firma):
    """O factură de servicii către clientul din Irlanda (0%, art.278 alin.(2)): nota ei, NEvalidată, nu schimbă TVA-ul lunii — D300 intră
    în coadă și numește nota (ca F1A6 din retestul lui Costin)."""
    from e2e_lot72_facturi import _emite_ie
    return _emite_ie(e, firma)


@contextlib.contextmanager
def _cont(browser, request, email):
    gen = _ecran(browser, request, email)
    e = next(gen)
    try:
        yield e
    finally:
        with contextlib.suppress(StopIteration):
            next(gen)


# ── 321 / 322 — pagina principală, „Primii pași” ───────────────────────────────────────────────────────────────────────────────
def test_def_321_rotita_deruleaza_pagina_principala_sub_cardurile_primii_pasi(browser, request, cabinet_nou):
    """321 (grav). Cardurile „Primii pași” blocau lucrul: rotița nu derula pagina, „De depus” / „Firme” se ajungeau doar cu Tab.
    Pașii: administratorul unui cabinet nou, pe un ecran de laptop (1280×720): pagina principală cu cele trei carduri; rotița pe carduri
    -> pagina coboară (desktopul derulează), iar cardurile „De depus” și „Firme” ajung în ecran."""
    with _cont(browser, request, cabinet_nou["email"]) as e:
        pg = e.pg
        pg.set_viewport_size({"width": 1280, "height": 720})
        e.acasa()
        pg.wait_for_selector("#inceput-carduri .inceput-card", timeout=30000)
        inalt = pg.evaluate("() => [document.querySelector('.desktop').scrollHeight, innerHeight]")
        assert inalt[0] > inalt[1], "cazul nu se reproduce: conținutul încape în ecran %s" % inalt
        firme = "button.cab-card:has([data-cheie='firme'])"
        assert pg.evaluate("(s) => document.querySelector(s).getBoundingClientRect().top", firme) > 720, "„Firme” e deja în ecran"
        e.captura("inainte")
        bb = pg.locator("#inceput-carduri .inceput-card").first.bounding_box()
        pg.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + 40)
        for _ in range(8):
            pg.mouse.wheel(0, 400)
            pg.wait_for_timeout(150)
        sus = pg.evaluate("() => document.querySelector('.desktop').scrollTop")
        e.captura("dupa_rotita")
        assert sus > 0, "rotița n-a derulat pagina"
        pg.wait_for_function("(s) => { const r = document.querySelector(s).getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight; }",
                             arg=firme, timeout=5000)


def test_def_322_lucrez_singur_nu_se_mai_arata_pe_pasul_facut(browser, request, cabinet_nou):
    """322. „Lucrez singur” pe un pas deja bifat nu făcea nimic.
    Pașii: administratorul cabinetului nou -> pasul 3 („Adaugă echipa”): „Lucrez singur” -> pasul e verde, iar „Lucrez singur” nu mai e pe
    card („Deschide Asistenți” rămâne)."""
    card = "#inceput-carduri .inceput-card[data-card='echipa']"
    with _cont(browser, request, cabinet_nou["email"]) as e:
        pg = e.pg
        e.acasa()
        pg.wait_for_selector(card + " [data-inceput='lucrez_singur']", timeout=30000)
        pg.click(card + " [data-inceput='lucrez_singur']")
        pg.wait_for_function("(s) => document.querySelector(s).classList.contains('inceput-facut')", arg=card, timeout=20000)
        e.captura("facut")
        assert pg.locator(card + " [data-inceput='lucrez_singur']").count() == 0, "„Lucrez singur” încă pe pasul făcut"
        assert pg.locator(card + " [data-inceput='asistenti']").count() == 1, "butonul spre Asistenți a dispărut"


# ── 323 / 324 / 329 — „De depus” ─────────────────────────────────────────────────────────────────────────────────────────────
def _proba_323_329(patron, firma_e2e):
    """323. Declarația depășită stătea la „Generate, nevalidate”, cu „n-a trecut prin validatorul oficial”; „depășită” lipsea din fereastră.
    329. Avertismentul vechi („F1A6 nevalidată”) rămânea după validare; „Deschide nota nota”.
    Pașii: o factură cu nota NEvalidată -> D300 în coadă: cardul numește nota, butonul „Deschide nota din …” (o dată „nota”); nota se
    validează -> cardul stă la „Depășite — de generat din nou”, eticheta „depășită — de generat din nou”, fără „n-a trecut prin validatorul
    oficial” și fără avertismentul notei (validată); „Vezi declarația” -> fereastra începe cu „Depășită — Declarația e depășită: …”."""
    pregateste_firma(patron, firma_e2e)
    peste = _peste()
    pg = patron.pg
    try:
        _valideaza_luna(patron, firma_e2e)
        f = _factura_fara_tva(patron, firma_e2e)
        r = _in_coada(patron, firma_e2e)
        assert r["status"] == 200, r
        rand = _deschide_coada(patron, r["json"]["coada_id"])
        pg.wait_for_selector(rand + " .coada-note-refuz button", timeout=20000)
        buton = pg.inner_text(rand + " .coada-note-refuz button")
        patron.captura("nota_numita")
        assert buton.startswith("Deschide nota din ") and "nota nota" not in buton, buton   # [329]
        _valideaza_notele(patron, firma_e2e, f["factura_id"])
        rand = _deschide_coada(patron, r["json"]["coada_id"])
        txt = pg.inner_text(rand)
        patron.captura("depasita")
        assert pg.locator("#val-depasite " + rand).count() == 1, "declarația depășită nu e în grupul ei"           # [323]
        assert pg.text_content("#val-depasite .cf-grup-titlu").startswith("Depășite — de generat din nou")   # textul, nu majusculele CSS
        assert pg.locator("#val-nevalidate " + rand).count() == 0, "declarația depășită stă și la „Generate, nevalidate”"
        assert "depășită — de generat din nou" in txt and "Declarația e depășită" in txt, txt
        assert "n-a trecut prin validatorul oficial" not in txt and "validatorul a găsit erori" not in txt, txt
        assert "nevalidat" not in txt.split("Declarația e depășită")[1].split("Vezi declarația")[0], txt                # [329]
        pg.click(rand + " .val-vezi")
        pg.wait_for_selector(".fereastra:last-of-type .val-depasita", timeout=60000)
        fer = patron.fereastra()
        patron.captura("fereastra")
        assert "Depășită — Declarația e depășită" in fer, fer[:800]
    finally:
        _curata(firma_e2e, peste)



def test_def_323_depasita_are_grupul_ei_si_fereastra_o_numeste(patron, firma_e2e):
    """323 — pașii în `_proba_323_329` (același scenariu: depășita apare după validarea notei numite)."""
    _proba_323_329(patron, firma_e2e)


def test_def_329_avertismentul_vechi_dispare_dupa_validare_si_nota_o_singura_data(patron, firma_e2e):
    """329 — pașii în `_proba_323_329`."""
    _proba_323_329(patron, firma_e2e)

def test_def_324_declaratia_veche_fara_cerere_merge_in_declaratii_nu_e_refuzata(patron, firma_e2e):
    """324. „Generează din nou” era oferit, apoi refuzat cu trimitere în Declarații (declarațiile intrate în coadă înainte de 17.10.2026
    n-au cererea păstrată).
    Pașii: o declarație din coadă fără cererea păstrată (cum sunt cele de dinainte de lotul 7) -> cardul nu oferă „Generează din nou”, ci
    „Generează din Declarații”; clicul deschide Declarații cu firma, D300 și luna declarației alese."""
    pregateste_firma(patron, firma_e2e)
    peste = _peste()
    pg = patron.pg
    try:
        emite_api(patron, firma_e2e)
        _valideaza_luna(patron, firma_e2e)
        cid = _ok(_in_coada(patron, firma_e2e), "în coadă")["coada_id"]
        sql("UPDATE public.declaratii_coada SET payload = payload - '_cerere' - '_surse' WHERE id = %s", (cid,))   # ca înainte de 17.10
        rand = _deschide_coada(patron, cid)
        assert pg.locator(rand + " [data-act='regenereaza']").count() == 0, "„Generează din nou” oferit, deși serverul îl refuză"
        patron.captura("din_declaratii")
        pg.click(rand + " [data-act='din_declaratii']")
        pg.wait_for_selector(".fereastra:last-of-type #dec-tip", timeout=30000)
        pg.wait_for_function("() => document.querySelector('.fereastra:last-of-type #dec-tip').value === 'd300'", timeout=20000)
        alese = pg.evaluate("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); return [(f.querySelector('#dec-firma') || {}).value, "
                            "(f.querySelector('#dec-luna') || {}).value]; }")
        patron.captura("declaratii")
        assert alese == [str(firma_e2e["tenant_id"]), str(AZI.month)], alese   # AZI-dat-de-test: luna declarației pusă în coadă de `_in_coada`
    finally:
        _curata(firma_e2e, peste)


# ── 325 — nimic nu se deschide singur ────────────────────────────────────────────────────────────────────────────────────────
def test_def_325_lista_tip_declaratie_nu_se_deschide_singura(patron, firma_e2e):
    """325 (clasă). Lista „Tip declarație” s-a deschis singură (focusul pus din cod pe listă, după „Arată alte declarații”).
    Pașii: Declarații -> „Arată alte declarații”: grupa „Alte declarații” apare, focusul rămâne pe buton, iar lista NU primește focus din
    cod; garda din plasă (`GARDA_DESCHIDERI`, pe orice ecran) nu notează nimic."""
    from e2e_bloc_c import _deschide
    pregateste_firma(patron, firma_e2e)
    pg = patron.pg
    _deschide(patron, firma_e2e["nume"], "declaratii", "#dec-tip")
    if not pg.locator("#dec-alte").count():
        pytest.skip("firma n-are declarații datorate: butonul „Arată alte declarații” nu apare")
    pg.click("#dec-alte")
    pg.wait_for_function("() => [...document.querySelectorAll('#dec-tip optgroup')].some((g) => g.label === 'Alte declarații')", timeout=10000)
    activ = pg.evaluate("() => document.activeElement && document.activeElement.id")
    patron.captura("alte_deschise")
    assert activ == "dec-alte", "focusul a plecat pe %r" % activ
    assert not [x for x in patron.deschideri_singure if "dec-tip" in x], patron.deschideri_singure


#: [325] cele trei deschideri, provocate dintr-un script de inițializare (fără gestul omului: `page.evaluate` al Playwright rulează CU gest,
#: deci fereastra n-ar fi fost „înaintea primului gest”); numai pe adresa cu `?z325`, ca restul navigărilor contextului să rămână curate
PROVOACA_325 = r"""
if (location.search.includes("z325")) document.addEventListener("DOMContentLoaded", () => {
  const s = document.createElement("select"); s.id = "z325"; document.body.append(s); s.focus();
  try { s.showPicker(); } catch (e) { /* fără gest, browserul îl refuză — garda l-a notat înainte */ }
  const d = document.createElement("div"); d.setAttribute("role", "dialog"); d.setAttribute("aria-label", "z325-fereastra");
  document.body.append(d);
});
"""


def test_def_325_garda_noteaza_focusul_showpicker_si_fereastra_din_cod(patron):
    """325 (garda). Garda din plasă (`GARDA_DESCHIDERI`) notează toate cele trei deschideri fără clicul omului: focusul pus din cod pe o
    listă, `showPicker` și o fereastră (`role="dialog"`) apărută înaintea primului gest. Pașii: un document nou (niciun gest), în care
    codul pune focus și `showPicker` pe o listă și adaugă o fereastră -> cele trei note, exact. Notele probei se scot, ca aserțiunea
    finală a ecranului să judece restul."""
    pg = patron.pg
    pg.context.add_init_script(PROVOACA_325)
    pg.goto(BAZA + "/?z325=1", wait_until="domcontentloaded")
    asteptate = {"focus din cod pe lista select#z325", "showPicker pe select#z325", "fereastră deschisă fără clic: z325-fereastra"}
    for _ in range(50):
        if asteptate <= set(patron.deschideri_singure):
            break
        pg.wait_for_timeout(100)
    proba = [x for x in patron.deschideri_singure if x in asteptate]
    patron.deschideri_singure[:] = [x for x in patron.deschideri_singure if x not in asteptate]
    assert sorted(proba) == sorted(asteptate), proba


# ── 326 / 327 / 330 — Emite factură ──────────────────────────────────────────────────────────────────────────────────────────
VIES_IE = {"valid": True, "nume": "GOOGLE IRELAND LIMITED E2E", "adresa": "GORDON HOUSE\nBARROW STREET\nDUBLIN 4", "tara": "IE"}
SERV_AI = json.dumps({"cota": 21, "categorie": "standard", "tip": "servicii", "justificare": "CF art.291 alin.(1)", "incredere": "mare"})


def test_def_326_client_ue_valid_vies_linie_de_serviciu_propune_art278_alin2(patron, firma_e2e):
    """326. Pentru client UE valid în VIES și linie de serviciu, cota propusă era 21%; trebuie propusă categoria art.278 alin.(2).
    331 (UM). Linia de serviciu primea UM „buc”.
    Pașii: Emite factură -> o linie de servicii (nomenclator, 21%) -> CUI irlandez, „Verifică”: VIES valid -> linia trece pe 0%, categoria
    „Prestare de servicii cu locul în afara României”; o a doua linie de servicii scrisă acum (în afara nomenclatorului) -> direct 0% cu
    aceeași categorie și UM „serv.”; altă țară (RO) -> propunerea se retrage (21%)."""
    pregateste_firma(patron, firma_e2e)
    _deschide_emiterea(patron, firma_e2e["nume"])
    pg = patron.pg
    ai_pregateste(*([SERV_AI] * 6))
    pg.fill("#em-l0-descriere", PRODUS)
    pg.wait_for_function("() => document.querySelector('#em-l0-cota').value === '21'", timeout=20000)
    pg.route("**/verifica-vies**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(VIES_IE)))
    try:
        pg.fill("#em-cui", "IE6388047V")
        pg.click("#em-verifica")
        pg.wait_for_function("() => document.querySelector('#em-l0-cota').value === '0'", timeout=15000)
        assert pg.input_value("#em-l0-categorie") == "serviciu_extern"
        pg.click("#em-add-linie")
        pg.fill("#em-l1-descriere", "Servicii de audit E2E 326")
        pg.wait_for_function("() => document.querySelector('#em-l1-cota').value === '0'", timeout=20000)
        patron.captura("art278_alin2")
        assert (pg.input_value("#em-l1-categorie"), pg.input_value("#em-l1-um")) == ("serviciu_extern", "serv."), (
            pg.input_value("#em-l1-categorie"), pg.input_value("#em-l1-um"))
        pg.select_option("#em-tara", "RO")
        pg.wait_for_function("() => document.querySelector('#em-l1-cota').value === '21'", timeout=10000)
        assert pg.is_hidden("#em-l1-categorie"), "categoria rămâne după ce clientul nu mai e din UE"
    finally:
        pg.unroute("**/verifica-vies**")


def test_def_327_dupa_emitere_butonul_mesajul_si_caseta_spv(patron, firma_e2e):
    """327. După emitere butonul rămânea „Se emite...”; „a fost trimisă către contabil” când emite chiar contabilul; caseta SPV cu derulare
    proprie (285).
    Pașii: contabilul completează și emite o factură -> butonul „Emisă ✓” (inactiv), mesajul fără „trimisă către contabil”; caseta SPV
    (firma neconectată) se citește întreagă, fără derulare proprie."""
    from e2e_bloc_a import _completeaza_factura
    pregateste_firma(patron, firma_e2e)
    _deschide_emiterea(patron, firma_e2e["nume"])
    pg = patron.pg
    _completeaza_factura(pg, cantitate="1")
    pg.wait_for_function("() => !document.querySelector('#em-emite').disabled", timeout=20000)
    pg.click("#em-emite")
    pg.wait_for_function("() => document.querySelector('#em-rezultat').innerText.includes('emisă')", timeout=60000)
    pg.wait_for_timeout(1500)   # starea SPV se citește după emitere
    if not pg.locator("#em-emite").count():
        pytest.skip("formularul s-a închis singur (firma conectată la SPV): caseta SPV nu apare")
    patron.captura("emisa")
    assert (pg.inner_text("#em-emite"), pg.is_disabled("#em-emite")) == ("Emisă ✓", True)
    assert "trimisă către contabil" not in pg.inner_text("#em-rezultat")
    z = pg.evaluate("() => { const r = document.querySelector('#em-rezultat'); return [r.scrollHeight, r.clientHeight, getComputedStyle(r).overflowY]; }")
    assert z[0] <= z[1] + 1 and z[2] == "visible", "mesajul de după emitere are derulare proprie: %s" % z


def test_def_330_confirmarea_renuntarii_nu_are_doua_renunta(patron, firma_e2e):
    """330. Confirmarea renunțării avea „Renunță la factură” și „Renunță” alăturate.
    Pașii: Emite factură -> „Renunță la factură” -> confirmarea: „Da, renunț la factură” / „Continui factura”; „Continui factura” închide
    confirmarea și formularul rămâne."""
    pregateste_firma(patron, firma_e2e)
    _deschide_emiterea(patron, firma_e2e["nume"])
    pg = patron.pg
    pg.fill("#em-nume", "Client E2E 330")
    pg.click("#em-renunta")
    pg.wait_for_selector("#caseta-atentie-activa #ca-ok", timeout=10000)
    patron.captura("confirmarea")
    assert (pg.inner_text("#ca-ok"), pg.inner_text("#ca-nu")) == ("Da, renunț la factură", "Continui factura")
    pg.click("#ca-nu")
    assert pg.locator("#caseta-atentie-activa").count() == 0 and pg.input_value("#em-nume") == "Client E2E 330"


# ── 331 — texte și aranjare ──────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_331_tabelul_nu_rupe_cuvintele_scurte_iar_adresa_nu_repeta_localitatea(patron, firma_e2e):
    """331. Cuvinte rupte în tabele („Can t”, „servici u”); „DUBLIN 4, DUBLIN 4” în detaliu și PDF.
    Pașii: factura către clientul din Irlanda, adresa din VIES pe rânduri, cu localitatea „DUBLIN 4” și pe rândul ei -> detaliul la 1100 px:
    antetul și celulele scurte ale liniilor pe un singur rând; adresa clientului cu „DUBLIN 4” o dată; PDF-ul la fel."""
    from e2e_bloc_a import _octeti
    pregateste_firma(patron, firma_e2e)
    corp = {"linii": [{"descriere": "Servicii de consultanță contabilă E2E serviciu", "cantitate": 1, "um": "serv.", "pret_unitar": 500.0,
                       "cota_tva": 0, "cota_propusa": 0, "articol_id": None, "categorie_tva": "serviciu_extern"}],
            "tert_nume": VIES_IE["nume"], "tert_cui": "IE6388047V", "tert_adresa": VIES_IE["adresa"], "tert_oras": "DUBLIN 4", "tert_tara": "IE",
            "moneda": "RON", "tip_operatiune": "normal", "bon_fiscal_nr": None, "bon_fiscal_data": None, "data_emitere": AZI.isoformat(),
            "data_scadenta": (AZI + _dt.timedelta(days=30)).isoformat(), "tip": "factura"}
    f = _ok(_api(patron, "POST", "/tenants/%d/facturi/emite" % firma_e2e["tenant_id"], corp), "factura IE")
    pg = patron.pg
    pg.set_viewport_size({"width": 1100, "height": 900})
    _deschide_factura(patron, firma_e2e, f["factura_id"])
    rupte = pg.evaluate("""() => [...[...document.querySelectorAll('.fereastra')].pop().querySelectorAll('.fd-tabel th, .fd-tabel td')]
        .filter((c) => c.innerText.trim() && c.innerText.trim().length <= 12 && !c.innerText.includes(' ')).filter((c) => {
          const r = document.createRange(); r.selectNodeContents(c);
          return new Set([...r.getClientRects()].map((x) => Math.round(x.top))).size > 1; }).map((c) => c.innerText)""")
    txt = patron.fereastra()
    patron.captura("detaliu_1100")
    assert not rupte, "cuvinte scurte rupte pe două rânduri: %s" % rupte
    assert txt.count("DUBLIN 4") == 1, txt[:1500]
    import io
    from pypdf import PdfReader
    pdf = _octeti(patron, "/tenants/%d/facturi/%d/pdf" % (firma_e2e["tenant_id"], f["factura_id"]))
    text = " ".join(p.extract_text() for p in PdfReader(io.BytesIO(pdf)).pages)
    assert text.count("DUBLIN 4") == 1, text[:800]


def test_def_331_banca_descrierea_scurtata_la_cuvant_fara_separator_ramas(patron, firma_e2e):
    """331. „octombrie - ·” la Bancă: descrierea tăiată la 90 de caractere, în mijlocul cuvântului, lipită de „ · motiv”.
    Pașii: o linie de extras cu descrierea lungă care se oprește în „… octombrie - ” și un motiv -> Bancă: rândul ei se termină la un cuvânt
    întreg, cu „…”, fără „ - ·”."""
    s = firma_e2e["schema"]
    desc = "Incasare contravaloare servicii prestate conform contract cadru nr 12 din data de 3 octombrie - " + "x" * 40
    lid = sql('INSERT INTO "%s".extras_linii (data, descriere, suma, tip, status, alocari) VALUES (%%s, %%s, 242, \'incasare\', \'nou\', %%s) '
              'RETURNING id' % s,
              (AZI.isoformat(), desc, json.dumps({"motiv": "nicio factură deschisă cu suma asta"})))[0][0]
    try:
        patron.firma(firma_e2e["nume"])
        _card(patron, "banca", "#bk-fisier")
        pg = patron.pg
        pg.wait_for_function("(d) => document.querySelector('#bk-lista').innerText.includes(d)", arg="Incasare contravaloare", timeout=20000)
        rand = pg.evaluate("() => [...document.querySelectorAll('#bk-lista .pf-frand-sub')].map((x) => x.innerText).find((t) => t.startsWith('Incasare contravaloare'))")
        patron.captura("descrierea")
        assert " - ·" not in rand and "- …" not in rand and "… · nicio factură" in rand, rand
    finally:
        sql('DELETE FROM "%s".extras_linii WHERE id = %%s' % s, (lid,))


def test_def_331_conectare_spv_titlul_o_data_si_banda_cu_spatii(patron, firma_e2e):
    """331. „Conectare SPV” dublat; spații lipsă în banda de sus.
    Pașii: Setări cont -> Conectare SPV: titlul o singură dată; banda de sus: „În lucru: <firmă>” cu spațiu, iar mesajul cu butoane al
    benzii (`.subbara-edu`) are distanță între text și butoane."""
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    sub = pg.evaluate("() => document.querySelector('.subbara').textContent")
    assert "În lucru: " in sub, sub
    deschide_setari_panou(patron, "Conectare SPV", "#spv-stare")
    pg.wait_for_timeout(800)
    titluri = pg.evaluate("() => [...[...document.querySelectorAll('.fereastra')].pop().querySelectorAll('h2')].map((h) => h.textContent.trim())")
    patron.captura("conectare_spv")
    assert titluri.count("Conectare SPV") == 1, titluri
    gap = pg.evaluate("""() => { const s = document.createElement('span'); s.className = 'subbara-edu';
        s.innerHTML = 'nu depune ce a pregătit singur. <button class="btn-link">Activează</button> · <button class="btn-link">Nu acum</button>';
        document.querySelector('.subbara').appendChild(s); const b = s.querySelector('button').getBoundingClientRect();
        const r = document.createRange(); r.selectNodeContents(s.firstChild); const t = r.getBoundingClientRect(); s.remove(); return b.left - t.right; }""")
    assert gap >= 3, "fără spațiu între text și buton în bandă: %s px" % gap


# ── 332 / 333 — Casă, Amortizare ─────────────────────────────────────────────────────────────────────────────────────────────
def test_def_332_dispozitia_noua_porneste_cu_data_de_azi(patron, firma_e2e):
    """332 (clasa 68). Data dispoziției noi venea goală.
    Pașii: Casă -> „+ Dispoziție nouă” -> data e azi (o schimbă omul dacă faptul e din altă zi)."""
    pregateste_firma(patron, firma_e2e)
    patron.firma(firma_e2e["nume"])
    _card(patron, "casa", "#c-toggle")
    pg = patron.pg
    pg.click("#c-toggle")
    pg.wait_for_selector("#c-data", state="visible", timeout=10000)
    patron.captura("data_azi")
    assert pg.input_value("#c-data") in [d.isoformat() for d in zile_de_acum(AZI)], pg.input_value("#c-data")


def test_def_333_amortizarea_lunii_in_curs_nu_e_ceruta_si_nu_e_oferita(patron, firma_e2e):
    """333. Pentru luna în curs, „Ce oprește închiderea” cerea generarea amortizării, iar butonul o refuza (și la Ana în Registru jurnal).
    Pașii: un mijloc fix pus în funcțiune acum trei luni -> Închidere lună, luna curentă: motivul e „luna nu s-a încheiat”, fără
    „amortizarea lunii nu e înregistrată”; Registru jurnal, luna curentă: „Generează amortizarea” inactiv, cu motivul."""
    from e2e_bloc_e import _card as _card_e, _mf
    f = firma_e2e
    m = AZI.year * 12 + AZI.month - 1 - 3
    mid = _mf(f, "MF333", "3000", 30, _dt.date(m // 12, m % 12 + 1, 10).isoformat())
    pg = patron.pg
    try:
        _card_e(patron, f, "inchidere", "#il-prev")
        pg.wait_for_selector(".fereastra:last-of-type #il-controale", timeout=60000)
        pg.wait_for_function("() => document.querySelector('.fereastra:last-of-type #il-controale').innerText.includes('nu s-a încheiat')",
                             timeout=60000)
        zona = pg.inner_text(".fereastra:last-of-type #il-controale")
        patron.captura("inchidere")
        assert "amortizarea lunii nu e înregistrată" not in zona and "nu s-a încheiat" in zona, zona
        _card_e(patron, f, "jurnal", "#j-amort")
        patron.captura("jurnal")
        assert pg.is_disabled("#j-amort") and "după ce luna se încheie" in pg.inner_text("#j-amort-motiv")
    finally:
        sql('DELETE FROM "%s".mijloace_fixe WHERE id = %%s' % f["schema"], (mid,))


# ── 328 — Registru jurnal ────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_328_nota_din_factura_nu_se_sterge_iar_mesajul_spune_ciorna(patron, firma_e2e):
    """328. Nota din factură apărea „Ciornă” în Registru jurnal, iar mesajul D300 spunea „la validare”; „Șterge” oferit pe nota derivată.
    Pașii: o factură emisă, nota ei ciornă (nevalidată) -> D300 în coadă: avertismentul spune „nota ei e ciornă, nevalidată”, nu „la
    validare”; Registru jurnal: pe nota facturii nu e „Șterge”; ștergerea cerută direct e refuzată, cu drumul prin factură."""
    pregateste_firma(patron, firma_e2e)
    peste = _peste()
    pg = patron.pg
    try:
        _valideaza_luna(patron, firma_e2e)
        f = _factura_fara_tva(patron, firma_e2e)
        nid = _nota_facturii(firma_e2e, f["factura_id"])[0]
        r = _ok(_in_coada(patron, firma_e2e), "în coadă")
        rand = _deschide_coada(patron, r["coada_id"])
        av = pg.inner_text(rand)
        assert "nota ei e ciornă, nevalidată" in av and "nota ei e la validare" not in av, av
        patron.firma(firma_e2e["nume"])
        _card(patron, "jurnal", "#j-nota-noua")
        pg.wait_for_selector("[data-nota-id='%d']" % nid, timeout=20000)
        patron.captura("jurnal")
        assert pg.locator("[data-nota-id='%d'] [data-del]" % nid).count() == 0, "„Șterge” oferit pe nota facturii"
        d = _api(patron, "DELETE", "/tenants/%d/jurnal/%d" % (firma_e2e["tenant_id"], nid))
        assert d["status"] >= 400 and "se corectează numai de acolo" in json.dumps(d["json"], ensure_ascii=False), d
    finally:
        _curata(firma_e2e, peste)


# ── 334 / 335 / 336 / 338 — roluri și notificări ────────────────────────────────────────────────────────────────────────────
def test_def_334_asistentul_nu_primeste_butonul_spre_conectare_spv(browser, request, patron, firma_e2e):
    """334. Asistentul vedea „Deschide Conectare SPV” (conectarea e a administratorului cabinetului).
    Pașii: aceeași firmă, cabinetul neconectat la SPV -> fereastra firmei: administratorul are „Deschide Conectare SPV”; asistentul nu-l
    are, i se spune „Conectarea SPV o face administratorul cabinetului …”."""
    pregateste_firma(patron, firma_e2e)
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    pg.wait_for_selector("#firma-spv", timeout=20000)
    pg.wait_for_timeout(1500)
    if not pg.locator("#firma-spv [data-ecran-destinatie='conectare_spv']").count():
        pytest.skip("starea SPV a firmei nu trimite la Conectare SPV (cabinetul de test e conectat): cazul nu se reproduce")
    assert pg.locator("#firma-spv button[data-ecran-destinatie='conectare_spv']").count() == 1, "administratorul și-a pierdut butonul"
    with cont_asistent(firme=(firma_e2e["tenant_id"],)) as a, _cont(browser, request, a["email"]) as e:
        e.firma(firma_e2e["nume"])
        e.pg.wait_for_selector("#firma-spv [data-ecran-destinatie='conectare_spv']", timeout=20000)
        e.captura("asistent")
        assert e.pg.locator("#firma-spv button[data-ecran-destinatie='conectare_spv']").count() == 0, "asistentul primește butonul"
        assert "Conectarea SPV o face administratorul cabinetului" in e.pg.inner_text("#firma-spv")


def _proba_335_336(patron):
    """335. „Trimite codul pe WhatsApp” era oferit înainte de lotul 8. 336. Cu acordul WhatsApp dat și numărul neconfirmat, mesajul spunea
    doar „vin pe email”, fără motiv.
    Pașii (aplicația de probă n-are tokenul WhatsApp, ca producția până la lotul 8): Setări cont -> Notificări -> numărul salvat, acordul dat
    (simulat) -> fără „Trimite codul pe WhatsApp”, WhatsApp inactiv cu motivul; „Salvează” -> „Notificările vin pe email. Trimiterea pe
    WhatsApp nu e încă activă …”."""
    from core.uc_cont_notificari import MOTIV_WA_INACTIV
    from e2e_lot7 import EMAIL, _deschide_notificari, _reseteaza
    _reseteaza()
    try:
        sql("UPDATE public.users SET telefon = '+40759638499', acord_whatsapp_la = now() WHERE email = %s", (EMAIL,))
        pg = _deschide_notificari(patron)
        assert pg.is_hidden("#not-cere-cod") and pg.is_hidden("#not-confirmare"), "[335] codul pe WhatsApp oferit"
        assert pg.inner_text("#not-motiv-canal") == MOTIV_WA_INACTIV
        pg.click("#not-salveaza-canal")
        pg.wait_for_function("() => document.querySelector('#not-msg').innerText.includes('email')", timeout=20000)
        patron.captura("motiv")
        assert pg.inner_text("#not-msg").startswith("Notificările vin pe email. " + MOTIV_WA_INACTIV), pg.inner_text("#not-msg")   # [336]
    finally:
        _reseteaza()



def test_def_335_codul_pe_whatsapp_nu_se_ofera_inainte_de_lotul_8(patron):
    """335 — pașii în `_proba_335_336`."""
    _proba_335_336(patron)


def test_def_336_mesajul_vin_pe_email_spune_de_ce(patron):
    """336 — pașii în `_proba_335_336`."""
    _proba_335_336(patron)

def test_def_338_acelasi_telefon_la_doi_utilizatori_are_avertisment(patron):
    """338. Același telefon salvat la doi utilizatori, fără avertisment.
    Pașii: alt cont are deja numărul 0759 638 499 -> contabilul îl salvează și el în Notificări -> caseta „Același număr e salvat și la alt
    cont din iConta.eu …”; fără celălalt cont, caseta nu apare."""
    from core.uc_cont_notificari import AVERTISMENT_TELEFON_DUBLU
    from e2e_lot7 import _deschide_notificari, _reseteaza
    _reseteaza()
    alt = sql("SELECT id FROM public.users WHERE email = 'asistent@prisma-cont.test'")[0][0]
    era = sql("SELECT telefon FROM public.users WHERE id = %s", (alt,))[0][0]
    try:
        pg = _deschide_notificari(patron)
        pg.fill("#not-telefon", "0759 638 499")
        pg.click("#not-salveaza-telefon")
        pg.wait_for_function("() => document.querySelector('#not-stare-telefon').innerText.includes('+40759638499')", timeout=20000)
        assert pg.is_hidden("#not-avert-telefon"), "avertisment fără alt cont cu același număr"
        sql("UPDATE public.users SET telefon = '+40759638499' WHERE id = %s", (alt,))
        pg = _deschide_notificari(patron)
        pg.wait_for_selector("#not-avert-telefon", state="visible", timeout=20000)
        patron.captura("avertisment")
        assert pg.inner_text("#not-avert-telefon") == AVERTISMENT_TELEFON_DUBLU
    finally:
        sql("UPDATE public.users SET telefon = %s WHERE id = %s", (era, alt))
        _reseteaza()


# ── 339 / 340 — cine primește ce ─────────────────────────────────────────────────────────────────────────────────────────────
def test_def_339_fara_validarea_in_doi_declaratia_proprie_nu_anunta_validatorii(patron, firma_e2e):
    """339. Ana a primit „un element nou de validat” când B a pus propria D300 în „De depus” (validarea în doi a declarațiilor oprită).
    Pașii: validarea în doi oprită -> administratorul pune D300 în coadă -> niciun validator nu primește „de validat” pentru ea; cu
    validarea în doi pornită (doi validatori), aceeași acțiune îi anunță."""
    pregateste_firma(patron, firma_e2e)
    cab = sql("SELECT accounting_firm_id FROM public.tenants WHERE id = %s", (firma_e2e["tenant_id"],))[0][0]
    era = sql("SELECT patru_ochi_activ FROM public.accounting_firms WHERE id = %s", (cab,))[0][0]
    peste = _peste()
    try:
        sql("UPDATE public.accounting_firms SET patru_ochi_activ = false WHERE id = %s", (cab,))
        emite_api(patron, firma_e2e)
        _valideaza_luna(patron, firma_e2e)
        cid = _ok(_in_coada(patron, firma_e2e), "în coadă")["coada_id"]
        n = sql("SELECT count(*) FROM public.notificari WHERE tip = 'de_validat' AND link LIKE %s", ("%%%d%%" % cid,))[0][0]
        assert n == 0, "%d notificări „de validat” cu validarea în doi oprită" % n
    finally:
        sql("UPDATE public.accounting_firms SET patru_ochi_activ = %s WHERE id = %s", (era, cab))
        _curata(firma_e2e, peste)


def test_def_340_superadminul_vede_numai_tipurile_lui_bifate(browser, request):
    """340. „Sesizare nouă” și „cerere de import” veneau nebifate la superadmin; superadminul vedea tipuri care nu-l privesc.
    Pașii: superadminul -> Notificări: numai alertele legislative, sesizările și cererile de import, toate bifate din oficiu."""
    with _cont(browser, request, "admin@prisma-cont.test") as e:
        pg = e.pg
        e.acasa()
        pg.click("button.cab-card:has([data-cheie='notificari_cont'])")
        pg.wait_for_selector(".fereastra:last-of-type #not-tipuri [data-tip]", timeout=20000)
        tipuri = pg.eval_on_selector_all(".fereastra:last-of-type #not-tipuri [data-tip]", "cs => cs.map((c) => [c.dataset.tip, c.checked])")
        e.captura("tipuri")
        assert dict(tipuri) == {"alerta_legislativa": True, "sesizare": True, "cerere_import": True}, tipuri


# ── 337 — Pachete lunare ─────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_337_ecranul_pachetului_spune_depasita_ca_fereastra_povestii(patron, firma_e2e):
    """337. Ecranul pachetului arăta povestea „aprobată ✓”, fereastra ei „depășită”. (Cifrele „numai luna”: probate pe balanța F1 și pe
    Postgres — `core/test_288_povestea_lunii.py::test_337_*`.)
    Pașii: povestea lunii aprobată pe cifrele de acum -> o factură nouă, cu nota validată -> Pachete lunare, luna: ecranul spune „aprobată,
    dar depășită …”, ca fereastra poveștii."""
    from e2e_bloc_a import _pachet
    from e2e_lot72_contab import _valideaza
    pregateste_firma(patron, firma_e2e)
    tid = firma_e2e["tenant_id"]
    rz = _ok(_api(patron, "GET", "/pachete/%d/rezumat?an=%d&luna=%d" % (tid, AZI.year, AZI.month), None), "rezumat")
    text = "În %s firma a avut venituri de %s lei și cheltuieli de %s lei." % (
        rz["luna_nume"], ("%.2f" % rz["venituri"]).replace(".", ","), ("%.2f" % rz["cheltuieli"]).replace(".", ","))
    _ok(_api(patron, "POST", "/pachete/%d/poveste/aproba?an=%d&luna=%d" % (tid, AZI.year, AZI.month), {"text": text}), "aprobarea")
    f = emite_api(patron, firma_e2e)
    for nid in _nota_facturii(firma_e2e, f["factura_id"]):
        _valideaza(patron, firma_e2e, nid)
    _pachet(patron, firma_e2e, AZI.year, AZI.month)
    stare = patron.pg.inner_text("#pac-deschide-stare")
    patron.captura("ecranul_pachetului")
    assert stare.startswith("Povestea e aprobată, dar depășită") and "✓" not in stare, stare


# ── C50 / C51 — găsite de Code în lot ──────────────────────────────────────────────────────────────────────────────────────────
def test_def_c50_coada_se_listeaza_cand_perioada_are_o_nota_nevalidata(patron, firma_e2e):
    """C50. `GET /coada` dădea 500 când perioada unei declarații din coadă avea o notă nevalidată: `coada_api.note_nevalidate` citea două
    `COALESCE` fără alias, iar pe cursorul dict cheile se suprascriau (tuplul ieșea mai scurt -> IndexError). Pașii: o factură cu nota
    NEvalidată -> D300 în coadă -> lista cozii răspunde 200, iar declarația își numește nota."""
    pregateste_firma(patron, firma_e2e)
    peste = _peste()
    try:
        _valideaza_luna(patron, firma_e2e)
        _factura_fara_tva(patron, firma_e2e)
        r = _in_coada(patron, firma_e2e)
        assert r["status"] == 200, r
        lista = _api(patron, "GET", "/coada", None)
        assert lista["status"] == 200, lista
        coada = lista["json"].get("coada", lista["json"]) if isinstance(lista["json"], dict) else lista["json"]
        el = [c for c in coada if c.get("id") == r["json"]["coada_id"]]
        assert len(el) == 1 and len(el[0]["surse_note"]) >= 1, el
    finally:
        _curata(firma_e2e, peste)


def test_def_c51_previzualizarea_programata_nu_citeste_casa_cat_se_reincarca(patron, firma_e2e):
    """C51. Sub încărcare, cronometrul previzualizării din Casă (250 ms după ultima tastare) pornea după „Adaugă”, cât Casa se reîncărca:
    `deseneaza()` pune întâi „Se încarcă...” în corp și abia după registrul lunii redesenează formularul, iar `opPropusa` citea `#c-data`
    inexistent — „Cannot read properties of null (reading 'value')”, prins intermitent de plasă în `e2e_bloc_a::test_def_8` (stiva:
    `opPropusa` <- cronometrul). Pașii, cu ceasul paginii oprit (cronometrele nu pornesc singure): dispoziția de încasare completată ->
    „Adaugă”, cu registrul lunii ținut pe loc (Casa rămâne la „Se încarcă...”) -> ceasul merge mai departe și cronometrul pornește ->
    registrul se întoarce: dispoziția apare, nicio eroare JavaScript."""
    pregateste_firma(patron, firma_e2e)
    pg = patron.pg

    def asteapta(js, ce):
        for _ in range(300):
            if pg.evaluate(js):
                return
            time.sleep(0.1)
        raise AssertionError("n-a apărut: %s" % ce)

    patron.firma(firma_e2e["nume"])
    _card(patron, "casa", "#c-toggle")
    pg.click("#c-toggle")
    pg.clock.install()
    pg.fill("#c-data", AZI.isoformat())
    pg.select_option("#c-cat", "incasare_client")
    pg.fill("#c-suma", "517.00")
    pg.fill("#c-part", "Client C51 E2E SRL")
    pg.fill("#c-doc", "DI E2E C51")
    tinute = []
    e_registrul = lambda url: "/casa/registru" in url   # noqa: E731 — aceeași potrivire la route și la unroute
    pg.route(e_registrul, lambda route: tinute.append(route))
    pg.click("#c-adauga")
    for _ in range(300):   # Playwright (sincron) livrează rutele numai cât e chemat: bucla cheamă pagina, nu doar doarme
        if tinute:
            break
        pg.evaluate("() => 0")
        time.sleep(0.1)
    assert tinute, "Casa nu s-a reîncărcat după „Adaugă” — dispoziția n-a fost salvată?"
    assert pg.evaluate("() => !document.querySelector('#c-data')"), "formularul e încă în pagină — proba n-ar prinde reîncărcarea"
    pg.clock.run_for(2000)
    time.sleep(0.5)
    for route in tinute:
        route.continue_()
    pg.unroute(e_registrul)
    asteapta("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('517,00')", "dispoziția în registru")
    patron.captura("dupa_reincarcare")
    assert not patron.erori, patron.erori
