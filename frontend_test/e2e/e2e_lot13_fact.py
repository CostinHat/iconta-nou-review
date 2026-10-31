# -*- coding: utf-8 -*-
"""Lotul 13, comanda 13.1 (Costin 25.10.2026), zona `fact` — facturile emise și primite, chitanța, seria, VIES-ul la emitere, partenerii,
e-Transport, șablonul facturii recurente, borderoul.

  * 545 — aceeași factură TI-1 (taxare inversă, același furnizor) a doua oară: refuzată, cu prima numită;
  * 546 — factura primită cu taxare inversă: totalul de plată e baza, TVA-ul separat (CF art.331 alin.(3));
  * 547 — factura primită introdusă greșit, cu nota încă ciornă: „Șterge factura”; fără „Trimite pe email” la factura primită;
  * 542 — seria nouă pornește de la 1 (nu de la contorul vechi);
  * 543 — seria chitanțelor se cere pe loc, ca seria facturii;
  * C199 — livrarea intracomunitară: codul invalid în VIES refuză scutirea; VIES indisponibil = avertisment și reîncercare (550);
  * 634 — factura primită în valută: echivalentul în lei înainte de validare; după validare, contul și nota, cu butonul spre ea;
  * 632 / 640 — Clienți / Furnizori: numărul facturilor rămâne după salvare, clientul străin fără județ, adăugare / căutare / ștergere,
    localitatea o singură dată pentru clientul care e și furnizor, persoana fizică fără localitate semnalată;
  * 534 / 535 — e-Transport completat din factură; toate câmpurile lipsă deodată;
  * 680 — șablonul facturii recurente cu aceleași întrebări ca „Emite factură” (scadența, perioada, modul, SPV), „Emite factura lunii”;
  * 603 / 604 — borderoul: titlul notei cu diacritice, butonul lângă NIR (nu în „TVA regimuri speciale”);
  * 611 / 613 / 615 — retestele: refuzul achiziției de la persoana fizică numește ce lipsește; mesajul „articolul n-are cota TVA” dispare la
    alegerea cotei; după stornare nimic „Se stornează…”, factura „stornată” fără reîmprospătare.

DATE DE PORNIRE fără ecran (declarate, regula lui 429): firmele sunt NOI (`conftest.firma_noua`), pregătite pe rutele ecranelor
(`e2e_bloc_a.pregateste_firma`); starea de dinainte de reparație (contorul vechi al lui 542, seria chitanțelor lipsă a lui 543) se pune cu
SQL, numit în fiecare test. VIES e servit de plasă (`<ICONTA_ANAF_SIMULAT>/vies.json`). Clientul român: DANTE INTERNATIONAL SA, CUI 14399840
— cifra de control verificată cu algoritmul din CLAUDE.md.

Temei: CF art.331 alin.(3) (546); CF art.294 alin.(2) lit.a) (C199: „un cod valabil de înregistrare în scopuri de TVA”); CF art.319
alin.(20) lit.a) (542: „numărul de ordine, în baza uneia sau a mai multor serii”); OMFP 2634/2015 anexa 1 pct.24 (543: seria chitanței
„stabilit(ă) de entitate”); OMFP 2634/2015 anexa 1 pct.58 lit.c (545 / 547). Restul: N/A — reguli de produs (CLAUDE.md §9)."""
import json
import os
from decimal import Decimal

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import AZI, ARTICOL, CLIENT, PRODUS, _api, _card, _deschide_emiterea, _deschide_factura, _ok, articol_in_stoc, emite_api, \
    pregateste_firma

CUI_DANTE = "14399840"
COD_INVALID, COD_INDISPONIBIL = "DE999999990", "IE6388047V"


@pytest.fixture(scope="module")
def firma_fact_noua():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_fact(patron, firma_fact_noua):
    pregateste_firma(patron, firma_fact_noua)
    return firma_fact_noua


def _lei(x):
    s = "{:,.2f}".format(float(x))
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _vies(cod, raspuns):
    """Răspunsul VIES de pe server (plasa: `<ICONTA_ANAF_SIMULAT>/vies.json`) pentru `cod`."""
    d = os.environ.get("ICONTA_ANAF_SIMULAT")
    assert d, "plasa rulează cu VIES simulat (ICONTA_ANAF_SIMULAT)"
    os.makedirs(d, exist_ok=True)
    cale = os.path.join(d, "vies.json")
    v = json.load(open(cale, encoding="utf-8")) if os.path.exists(cale) else {}
    v[cod] = raspuns
    json.dump(v, open(cale, "w", encoding="utf-8"), ensure_ascii=False)


def _fisa(patron, firma, fel, corp):
    """Fișa unui client / furnizor pe ruta ecranului Clienți / Furnizori (`POST /clienti`, `POST /furnizori`); una cu același CUI deja
    în nomenclator (409, salvată de un test de dinainte) rămâne cum e."""
    r = _api(patron, "POST", "/tenants/%d/%s" % (firma["tenant_id"], fel), corp)
    assert r["status"] in (200, 409), r
    return r["json"]


def _ti_operatiuni(patron, firma, numar="TI-1", valoare="30000"):
    """Operațiuni speciale -> „Taxare inversă internă (art. 331)” -> furnizorul DANTE, factura `numar`, deșeuri, 30.000, 371, 21%,
    (plătitorul se verifică la ANAF din CUI, nu se mai întreabă) -> „Generează nota”; întoarce textul zonei de rezultat."""
    patron.firma(firma["nume"])
    _card(patron, "operatiuni", "[data-op]")
    pg = patron.pg
    pg.locator("button[data-op]", has_text="Taxare inversă internă").first.click()
    pg.wait_for_selector("#op-trimite", timeout=10000)
    pg.fill("#op-data", AZI.isoformat())
    pg.fill("#op-furnizor_nume", "DANTE INTERNATIONAL SA")
    pg.fill("#op-furnizor_cui", CUI_DANTE)
    pg.fill("#op-numar", numar)
    pg.select_option("#op-categorie", "deseuri")
    pg.fill("#op-valoare", valoare)
    pg.fill("#op-cont_destinatie", "371")
    pg.fill("#op-cota", "21")
    pg.click("#op-trimite")
    pg.wait_for_function("() => (document.querySelector('#op-mesaj') || {innerText: ''}).innerText.trim().length > 0", timeout=30000)
    pg.wait_for_timeout(400)
    return pg.inner_text("#op-mesaj")


def _ti_api(patron, firma, numar="TI-7"):
    r = _ok(_api(patron, "POST", "/tenants/%d/achizitie-taxare-inversa" % firma["tenant_id"], {
        "data": AZI.isoformat(), "furnizor_nume": "DANTE INTERNATIONAL SA", "furnizor_cui": CUI_DANTE, "numar": numar,
        "categorie": "deseuri", "valoare": 30000, "cont_destinatie": "371", "cota": 21}), "taxare inversă")
    return r["factura_id"]


# ================================================================ 545 / 546 / 547 — factura primită
def test_def_545_a_doua_factura_ti_1_de_la_acelasi_furnizor_e_refuzata(patron, firma_fact):
    """545. Pașii: Operațiuni -> Taxare inversă internă: TI-1 de la DANTE, 30.000 -> nota generată; aceeași factură a doua oară -> refuzul
    „Factura TI-1 de la DANTE INTERNATIONAL SA e deja înregistrată…”, iar în bază rămâne o singură factură TI-1 și o singură notă."""
    s = firma_fact["schema"]
    _ti_operatiuni(patron, firma_fact)
    txt = _ti_operatiuni(patron, firma_fact)
    patron.captura("a_doua_oara")
    assert "TI-1" in txt and "e deja înregistrată" in txt, txt
    assert sql('SELECT count(*) FROM "%s".facturi WHERE numar = %%s' % s, ("TI-1",))[0][0] == 1
    assert sql('SELECT count(*) FROM "%s".inregistrari i JOIN "%s".facturi f ON f.id = i.factura_id WHERE f.numar = %%s' % (s, s),
               ("TI-1",))[0][0] == 1


def test_def_546_factura_cu_taxare_inversa_arata_totalul_de_plata_fara_tva(patron, firma_fact):
    """546. Pașii: factura primită cu taxare inversă (30.000, cota 21) -> Istoric facturi -> detaliul: „TVA taxare inversă … nu se plătește
    furnizorului” 6.300,00 separat, „Total de plată” 30.000,00 (nu 36.300); starea de plată pe 30.000."""
    fid = _ti_api(patron, firma_fact, "TI-546")
    _deschide_factura(patron, firma_fact, fid)
    pg = patron.pg
    pg.wait_for_selector("#fd-total-de-plata", timeout=20000)
    patron.captura()
    assert _lei(30000) in pg.inner_text("#fd-total-de-plata"), pg.inner_text("#fd-total-de-plata")
    assert _lei(6300) in pg.inner_text("#fd-tva-ti") and "nu se plătește furnizorului" in pg.inner_text("#fd-tva-ti")
    assert _lei(36300) not in pg.inner_text(".fd-totaluri")


def test_def_547_factura_primita_cu_nota_ciorna_se_sterge(patron, firma_fact):
    """547. Pașii: factura primită TI-547 (nota ei e încă ciornă) -> detaliul: fără „Trimite pe email”, cu „Șterge factura” -> confirmare
    -> „… și notele ei ciornă au fost șterse”; în bază nici factura, nici nota ei."""
    s = firma_fact["schema"]
    fid = _ti_api(patron, firma_fact, "TI-547")
    _deschide_factura(patron, firma_fact, fid)
    pg = patron.pg
    # [15.1, 547.1 — înlocuiește 675 pentru acțiunile fără sens] „Trimite pe email” nu se afișează pe o factură primită
    assert pg.locator("#fd-email").count() == 0, "„Trimite pe email” nu are rost la o factură primită"
    assert pg.is_enabled("#fd-sterge") and pg.get_attribute("#fd-sterge", "aria-disabled") is None
    pg.click("#fd-sterge")
    pg.locator("#ca-ok", has_text="Șterge factura").click()
    pg.wait_for_selector("#fd-sters-rez", timeout=20000)
    patron.captura()
    assert "au fost șterse" in pg.inner_text("#fd-sters-rez")
    assert sql('SELECT count(*) FROM "%s".facturi WHERE id = %%s' % s, (fid,))[0][0] == 0
    assert sql('SELECT count(*) FROM "%s".inregistrari WHERE factura_id = %%s' % s, (fid,))[0][0] == 0


# ================================================================ 542 / 543 — seria facturii, seria chitanței
def _completeaza_factura(pg):
    for sel, val in CLIENT.items():
        pg.fill(sel, val)
    pg.dispatch_event("#em-nume", "input")
    pg.fill("#em-oras", "Sector 2")
    pg.select_option("#em-judet", "B")
    pg.fill("#em-l0-descriere", PRODUS)
    pg.dispatch_event("#em-l0-descriere", "input")
    pg.wait_for_timeout(1200)                                            # cota din nomenclator
    pg.fill("#em-l0-cantitate", "1")
    pg.dispatch_event("#em-l0-cantitate", "input")
    pg.fill("#em-l0-pret_unitar", "100")
    pg.dispatch_event("#em-l0-pret_unitar", "input")
    if pg.input_value("#em-l0-cota") != "21":
        pg.select_option("#em-l0-cota", "21")
    if not pg.input_value("#em-l0-um"):   # [lotul 13, regula UM] UM-ul nu mai vine „buc” din oficiu: ce nu propune nomenclatorul scrie omul
        pg.fill("#em-l0-um", "ora")


def test_def_504_um_gol_la_emitere_se_refuza_langa_camp(patron, firma_fact):
    """504 (clasa — decizia sesiunii principale 26.10.2026 pe întrebarea UM: „UM gol NU devine «buc» pe ascuns — se refuză, lângă câmp, cu
    o propoziție («Alege unitatea de măsură a liniei.»)”). Pașii: Emite factură -> linia nouă: UM-ul e gol (nu „buc”) -> DANTE, produsul din
    nomenclator, 1 × 100, 21% -> UM-ul șters de om -> „Emite”: refuzul lângă UM-ul liniei, cu propoziția regulii, nicio factură scrisă ->
    „ora” -> „Emite”: factura emisă, linia în „ora”.
    MUTAȚIA (`mut_lot13_fact.json`): refuzul UM-ului scos din ruta emiterii -> factura pleacă fără UM -> ROȘU."""
    s = firma_fact["schema"]
    _deschide_emiterea(patron, firma_fact["nume"])
    pg = patron.pg
    assert pg.input_value("#em-l0-um") == "", "linia nouă vine cu UM pus din oficiu"
    _completeaza_factura(pg)
    pg.fill("#em-l0-um", "")
    n0 = sql('SELECT count(*) FROM "%s".facturi' % s)[0][0]
    pg.click("#em-emite")
    pg.wait_for_selector("#em-l0-um[aria-invalid='true']", timeout=30000)
    patron.captura("um_refuzat")
    assert pg.inner_text(".msg-eroare[data-camp='em-l0-um']").strip() == "Alege unitatea de măsură a liniei."
    assert sql('SELECT count(*) FROM "%s".facturi' % s)[0][0] == n0
    pg.fill("#em-l0-um", "ora")
    pg.click("#em-emite")
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=30000)
    patron.captura("emisa")
    assert sql('SELECT l.um FROM "%s".factura_linii l JOIN "%s".facturi f ON f.id = l.factura_id ORDER BY f.id DESC LIMIT 1' % (s, s)) == [("ora",)]


def test_def_542_seria_noua_porneste_de_la_1_nu_de_la_contorul_vechi(patron, firma_fact):
    """542. DATE DE PORNIRE (SQL, starea de pe F2 din 22.10.2026): o factură „1” emisă fără serie, contorul la 2, seria ștearsă.
    Pașii: Emite factură -> DANTE, 1 × 100 -> „Emite”: seria se cere pe loc -> „F2T” (numărul primei facturi: gol) -> „Stabilește seria și
    emite”: factura „F2T nr. 1”, nu „F2T nr. 2”."""
    s = firma_fact["schema"]
    from core import nomenclator_status_factura as _nsf   # starea implicită a facturii emise, din nomenclator
    sql('INSERT INTO "%s".facturi (numar, data_emitere, total, tva, directie, status, tip, tert_nume, tert_cui) VALUES '
        "('1', %%s, 121, 21, %%s, %%s, 'factura', 'DANTE INTERNATIONAL SA', %%s)" % s, (AZI, "emisa", _nsf.IMPLICITA, CUI_DANTE))  # date-de-pornire: starea de pe F2 din 22.10.2026 (o factură „1” emisă fără serie, contorul la 2), pe care ecranul nu o mai produce
    sql('UPDATE "%s".firma_profil SET serie_factura = NULL, urmator_numar_factura = 2 WHERE id = 1' % s)  # date-de-pornire: starea de pe F2 din 22.10.2026 (o factură „1” emisă fără serie, contorul la 2), pe care ecranul nu o mai produce
    try:
        _deschide_emiterea(patron, firma_fact["nume"])
        pg = patron.pg
        _completeaza_factura(pg)
        pg.click("#em-emite")
        pg.wait_for_selector("#em-serie-noua", timeout=20000)
        pg.fill("#em-serie-noua", "F2T")
        patron.captura("seria_pe_loc")
        pg.click("#em-serie-si-emite")
        pg.wait_for_selector("#em-rezultat.em-bun", timeout=30000)
        patron.captura("emisa")
        assert "F2T nr. 1" in pg.inner_text("#em-rezultat"), pg.inner_text("#em-rezultat")
        assert sql('SELECT numar FROM "%s".facturi WHERE serie = %%s' % s, ("F2T",)) == [("F2T1",)]
    finally:
        sql('UPDATE "%s".firma_profil SET serie_factura = %%s WHERE id = 1' % s, ("E2EA",))  # date-de-pornire: seria firmei pusă la loc după probă (Date firmă nu șterge / nu dă înapoi seria)


def test_def_543_seria_chitantelor_se_cere_pe_loc(patron, firma_fact):
    """543. DATE DE PORNIRE (SQL): firma fără seria chitanțelor. Pașii: factura emisă -> detaliul -> „Emite chitanță” -> „Emite”: sub
    formular, seria se cere pe loc (fără „Deschide Date firmă”) -> „CHE” -> „Stabilește seria și emite chitanța”: „Chitanța CHE nr. 1 a fost
    emisă”; seria e în Date firmă."""
    s = firma_fact["schema"]
    f = emite_api(patron, firma_fact)
    sql('UPDATE "%s".firma_profil SET serie_chitanta = NULL WHERE id = 1' % s)  # date-de-pornire: firma fără seria chitanțelor — Date firmă refuză ștergerea seriei, odată stabilită
    try:
        _deschide_factura(patron, firma_fact, f["factura_id"])
        pg = patron.pg
        pg.click("#fd-chitanta")
        pg.wait_for_selector("#fd-chit-ok", timeout=10000)
        pg.click("#fd-chit-ok")
        pg.wait_for_selector("#ser-chit-serie", timeout=20000)
        assert not pg.query_selector("#ser-chit-box button[data-ecran-destinatie]:not([hidden])")
        pg.fill("#ser-chit-serie", "CHE")
        patron.captura("seria_pe_loc")
        pg.click("#ser-chit-ok")
        pg.wait_for_function("() => document.body.innerText.includes('Chitanța CHE nr. 1 a fost emisă')", timeout=30000)
        patron.captura("emisa")
        assert sql('SELECT serie_chitanta FROM "%s".firma_profil' % s) == [("CHE",)]
    finally:
        sql('UPDATE "%s".firma_profil SET serie_chitanta = %%s WHERE id = 1' % s, ("E2ECH",))  # date-de-pornire: seria de pornire a firmei, pusă la loc după probă


# ================================================================ C199 / 550 — VIES la emitere
def _livrare_ic(patron, firma, cod):
    _deschide_emiterea(patron, firma["nume"])
    pg = patron.pg
    pg.fill("#em-cui", cod)
    pg.dispatch_event("#em-cui", "change")
    pg.fill("#em-nume", "Client UE E2E")
    pg.fill("#em-adresa", "1 Main Street")
    pg.fill("#em-oras", "Dublin" if cod.startswith("IE") else "Berlin")
    pg.fill("#em-l0-descriere", "Servicii de consultanță UE E2E")
    pg.dispatch_event("#em-l0-descriere", "input")
    pg.wait_for_timeout(1200)
    if not pg.input_value("#em-l0-um"):  # [lotul 13, regula UM] UM-ul nu mai vine „buc” din oficiu: ce nu propune nomenclatorul scrie omul
        pg.fill("#em-l0-um", "ora")
    pg.fill("#em-l0-cantitate", "1")
    pg.dispatch_event("#em-l0-cantitate", "input")
    pg.fill("#em-l0-pret_unitar", "1000")
    pg.dispatch_event("#em-l0-pret_unitar", "input")
    pg.select_option("#em-l0-cota", "0")
    pg.wait_for_selector("#em-l0-categorie", state="visible", timeout=5000)
    pg.select_option("#em-l0-categorie", "livrare_ic")
    pg.click("#em-emite")
    if pg.wait_for_selector("#em-dovada-da, #em-rezultat .msg-eroare, #em-cui[aria-invalid='true'], #em-rezultat.em-bun",
                            timeout=30000) and pg.query_selector("#em-dovada-da"):
        pg.click("#em-dovada-da")
    pg.wait_for_timeout(800)


def test_def_c199_cod_invalid_in_vies_refuza_scutirea(patron, firma_fact):
    """C199. Pașii: Emite factură -> client DE999999990 (VIES: invalid) -> linia 0%, „livrare intracomunitară” -> Emite: refuzul lângă CUI
    („e invalid în VIES … Factura se emite cu TVA românesc”), nicio factură scrisă."""
    s = firma_fact["schema"]
    _vies(COD_INVALID, {"valid": False, "stare": "invalid", "nume": "", "adresa": "", "eroare": "INVALID"})
    n0 = sql('SELECT count(*) FROM "%s".facturi' % s)[0][0]
    _livrare_ic(patron, firma_fact, COD_INVALID)
    pg = patron.pg
    pg.wait_for_function("() => document.body.innerText.includes('e invalid în VIES')", timeout=20000)
    patron.captura()
    assert "TVA românesc" in patron.fereastra()
    assert sql('SELECT count(*) FROM "%s".facturi' % s)[0][0] == n0


def test_def_c199_vies_indisponibil_emite_cu_avertisment_si_reincercare(patron, firma_fact):
    """C199 / 550. Pașii: client IE6388047V, VIES: „serviciu indisponibil” -> factura se emite (scutită), cu avertismentul „VIES nu a
    răspuns acum…” și butonul „Reîncearcă verificarea în VIES”; VIES revine valid -> „Codul … e valid în VIES … scutirea se păstrează”."""
    _vies(COD_INDISPONIBIL, {"valid": False, "stare": "indisponibil", "nume": "", "adresa": "", "eroare": "MS_UNAVAILABLE"})
    _livrare_ic(patron, firma_fact, COD_INDISPONIBIL)
    pg = patron.pg
    pg.wait_for_selector("#em-vies-reincearca", timeout=30000)
    assert "VIES nu a răspuns acum pentru codul %s" % COD_INDISPONIBIL in pg.inner_text("#em-rezultat")
    patron.captura("avertisment")
    _vies(COD_INDISPONIBIL, {"valid": True, "stare": "valid", "nume": "GOOGLE IRELAND LIMITED", "adresa": "Dublin", "eroare": None})
    pg.click("#em-vies-reincearca")
    pg.wait_for_function("() => (document.querySelector('#em-vies-rez') || {innerText: ''}).innerText.includes('valid în VIES')",
                         timeout=20000)
    patron.captura("reincercarea")


# ================================================================ 634 — factura primită: valuta, mesajul validării
def fisier_xml_634_eur(firma=None):
    """Factura e-Factura de probă (DANTE -> F1) în EUR, cu numărul PROBA-634 (generatorul dovezii, pe F1). Cu `firma`, cumpărătorul e
    firma de test (CUI și nume): importul refuză factura altei firme („Factura … nu e a firmei”, efactura_import)."""
    from e2e_lot12_cx1 import PROBA_XML
    import io
    t = io.open(PROBA_XML, encoding="utf-8").read().replace("DNT-RT-1020", "PROBA-634")
    if firma:
        cifre = "".join(c for c in sql('SELECT cui FROM "%s".firma_profil WHERE id = 1' % firma["schema"])[0][0] if c.isdigit())
        t = t.replace("RO401002001", "RO" + cifre).replace(">401002001<", ">%s<" % cifre).replace("F1 Comert Stoc SRL", firma["nume"])
    return t.replace(">RON<", ">EUR<").replace('currencyID="RON"', 'currencyID="EUR"').encode("utf-8")


def test_def_634_factura_in_valuta_arata_leii_si_dupa_validare_nota(patron, firma_fact):
    """634. Pașii: Facturi primite din SPV -> „Importă XML UBL” (PROBA-634, în EUR) -> factura: TVA și total cu moneda („EUR”), cursul BNR
    și „TVA în lei” / „Total în lei” înainte de validare -> contul 371 -> „Validează”: mesajul spune contul și nota („Nota ciornă … 371 =
    401 …”), cu „Vezi nota în Registrul jurnal”, nu „Cheltuiala creată”."""
    patron.firma(firma_fact["nume"])
    _card(patron, "facturi", "#fac-primite")
    pg = patron.pg
    pg.click("#fac-primite")
    pg.wait_for_selector("#fp-xml", state="attached", timeout=20000)
    pg.set_input_files("#fp-xml", files=[{"name": "PROBA-634.xml", "mimeType": "application/xml", "buffer": fisier_xml_634_eur(firma_fact)}])
    pg.wait_for_selector(".fac-primita-btn", timeout=30000)
    pg.locator(".fac-primita-btn", has_text="PROBA-634").first.click()
    pg.wait_for_selector("#pr-tva-lei", timeout=30000)
    assert "EUR" in pg.input_value("#pr-total") and "," in pg.input_value("#pr-total")
    assert "lei" in pg.inner_text("#pr-tva-lei") and "lei" in pg.inner_text("#pr-total-lei")
    patron.captura("inainte_de_validare")
    pg.fill("#pr-cont", "371")
    for sel in ("#pr-furnizor-incasare", "#pr-platitor"):
        if pg.query_selector(sel + ":not([readonly])") and pg.eval_on_selector(sel, "e => e.tagName") == "SELECT":
            pg.select_option(sel, "false" if sel == "#pr-furnizor-incasare" else "true")
    pg.click("#pr-valideaza")
    pg.locator("#ca-ok", has_text="Validează").click()
    pg.wait_for_function("() => (document.querySelector('#pr-zona') || {innerText: ''}).innerText.includes('Validată')", timeout=30000)
    if pg.query_selector("#nir-alta-livrare, [data-nir-alta]"):
        pg.click("#nir-alta-livrare, [data-nir-alta]")
    txt = pg.inner_text("#pr-zona")
    patron.captura("validata")
    assert "Cheltuiala creată" not in txt and "contul 371" in txt and "371 = 401" in txt, txt
    assert pg.is_visible("#pr-vezi-nota")


# ================================================================ 632 / 640 — Clienți și Furnizori
def test_def_632_fisa_clientului_pastreaza_facturile_si_clientul_strain_n_are_judet(patron, firma_fact):
    """632. Pașii: două facturi către DANTE -> Clienți: rândul DANTE (fără fișă) arată 2 la „Facturi emise” -> localitatea, „Salvează”:
    după salvare rândul (acum cu fișă) arată tot 2, nu gol; un client din Irlanda (IE9999999ZZ) n-are listă de județe („— partener din
    alt stat”)."""
    emite_api(patron, firma_fact)
    emite_api(patron, firma_fact)
    _fisa(patron, firma_fact, "clienti", {"nume": "Client Irlanda E2E Ltd", "cui": "IE9999999ZZ", "afiliat": False})
    patron.firma(firma_fact["nume"])
    pg = patron.pg
    _card(patron, "clienti", "#cl-nou")
    rand = "#cl-tabel tr[data-cheie='p%s']" % CUI_DANTE
    pg.wait_for_selector(rand, timeout=20000)
    n = pg.inner_text(rand + " td.fd-td-num").strip()
    pg.fill(rand + " input[id^='cl-oras-']", "Sector 2")
    pg.click(rand + " button.cl-salveaza")
    pg.wait_for_function("() => (document.querySelector('#cl-mesaj') || {innerText: ''}).innerText.includes('DANTE')", timeout=20000)
    # numele stă în valoarea câmpului (nu în textul rândului): rândul se găsește după CUI, care e text
    rand2 = pg.locator("#cl-tabel tbody tr", has_text=CUI_DANTE).first
    assert rand2.locator("td.fd-td-num").inner_text().strip() == n and int(n) >= 2, (n, rand2.inner_text())
    strain = pg.locator("#cl-tabel tbody tr", has_text="IE9999999ZZ").first
    assert "partener din alt stat" in strain.inner_text() and strain.locator("select[id^='cl-judet-']").count() == 0
    patron.captura()


def test_def_640_partenerul_se_adauga_se_cauta_si_se_sterge(patron, firma_fact):
    """640. Pașii: Furnizori -> „+ Furnizor nou” (fereastră nouă) -> CUI 14399840 -> „Verifică la ANAF”: denumirea și localitatea aduse ->
    „Salvează fișa” -> lista îl are; căutarea „dante” lasă numai rândul lui; un furnizor fără documente („Furnizor de sters E2E”) -> „Șterge”
    -> dispare; Clienți: DANTE (fișă de client) are localitatea scrisă la furnizor (aceeași firmă); o persoană fizică fără localitate e
    semnalată („D394 o cere”)."""
    s = firma_fact["schema"]
    _fisa(patron, firma_fact, "furnizori", {"nume": "Furnizor de sters E2E"})
    _fisa(patron, firma_fact, "clienti", {"nume": "DANTE INTERNATIONAL SA", "cui": CUI_DANTE, "afiliat": False})
    _fisa(patron, firma_fact, "clienti", {"nume": "Vasile Test E2E", "afiliat": False})
    patron.firma(firma_fact["nume"])
    pg = patron.pg
    _card(patron, "furnizori", "#fz-nou")
    pg.click("#fz-nou")
    pg.wait_for_selector("#fzn-cui", timeout=10000)
    pg.fill("#fzn-cui", CUI_DANTE)
    pg.click("#fzn-anaf")
    pg.wait_for_function("() => document.querySelector('#fzn-nume').value.trim() !== ''", timeout=20000)
    if not pg.input_value("#fzn-oras"):
        pg.fill("#fzn-oras", "Sector 2")
    patron.captura("fisa_noua")
    pg.click("#fzn-salveaza")
    pg.wait_for_selector("#fz-tabel", timeout=20000)
    pg.fill("#fz-cauta", "dante")
    pg.wait_for_timeout(300)
    vizibile = pg.eval_on_selector_all("#fz-tabel tbody tr", "rs => rs.filter(r => !r.hidden).map(r => r.innerText)")
    assert len(vizibile) == 1 and CUI_DANTE in vizibile[0], vizibile   # numele e valoarea câmpului; CUI-ul e textul rândului
    pg.fill("#fz-cauta", "")
    pg.dispatch_event("#fz-cauta", "input")
    rand = pg.locator("#fz-tabel tbody tr:has(input[value='Furnizor de sters E2E'])").first
    rand.locator("details.fz-actiuni > summary").click()                  # [lotul 13, DS cap.9 v2.83] acțiunile rândului, în meniul „Acțiuni”
    rand.locator("button[id^='fz-sterge-']").click()
    pg.locator("#ca-ok", has_text="Șterge fișa").click()
    # lista se redesenează după ștergere (zona mesajului lipsește o clipă): predicatul nu citește un nod absent
    pg.wait_for_function("() => (document.querySelector('#fz-mesaj') || {innerText: ''}).innerText.includes('a fost ștearsă')", timeout=20000)
    assert sql('SELECT count(*) FROM "%s".furnizori WHERE nume = %%s' % s, ("Furnizor de sters E2E",))[0][0] == 0
    oras_fz = sql('SELECT oras FROM "%s".furnizori WHERE cui = %%s' % s, (CUI_DANTE,))[0][0]
    assert sql('SELECT oras FROM "%s".clienti WHERE cui = %%s' % s, (CUI_DANTE,))[0][0] == oras_fz, "o singură localitate pentru DANTE"
    patron.firma(firma_fact["nume"])
    _card(patron, "clienti", "#cl-tabel")
    assert "D394 o cere" in pg.locator("#cl-tabel tbody tr:has(input[value='Vasile Test E2E'])").first.inner_text()
    patron.captura("clienti")


# ================================================================ 534 / 535 — e-Transport
def test_def_534_notificarea_se_completeaza_din_factura(patron, firma_fact):
    """534. Pașii: factură emisă către DANTE -> e-Transport -> „Din factură” (fereastră nouă) -> factura -> formularul: bunul (denumirea,
    cantitatea, valoarea fără TVA), partenerul (RO, 14399840, DANTE), locul de pornire din adresa firmei, tipul „30”; UM-ul și țara nu mai
    vin „H87” / „RO” din oficiu pe formularul gol."""
    f = emite_api(patron, firma_fact)
    patron.firma(firma_fact["nume"])
    pg = patron.pg
    _card(patron, "etransport", "#et-din-factura")
    assert pg.input_value("#b0-um") == "" and pg.input_value("#p-cod_tara") == ""
    pg.click("#et-din-factura")
    pg.wait_for_selector(".et-doc[data-id='%s']" % f["factura_id"], timeout=20000)
    pg.click(".et-doc[data-id='%s']" % f["factura_id"])
    pg.wait_for_function("() => document.querySelector('#b0-denumire') && document.querySelector('#b0-denumire').value !== ''",
                         timeout=20000)
    patron.captura()
    # câmpul numeric românesc (655) arată „300,00”; valoarea lui (`.value`, forma canonică) e cea citită aici
    assert (pg.input_value("#b0-denumire"), Decimal(pg.eval_on_selector("#b0-valoare_fara_tva", "e => e.value"))) == (PRODUS, Decimal("300.00"))
    assert (pg.input_value("#p-cod_tara"), pg.input_value("#p-cod"), pg.input_value("#et-tip")) == ("RO", CUI_DANTE, "30")
    assert pg.input_value("#s-localitate") == "București" and pg.input_value("#s-judet") == "B"
    assert "De completat" in pg.inner_text("#et-din-rez")


def test_def_535_trimiterea_cu_formularul_gol_arata_toate_campurile_lipsa(patron, firma_fact):
    """535. Pașii: e-Transport, formularul gol -> „Trimite UIT în SPV”: listele (tipul, scopul, județele) ȘI câmpurile text (denumirea,
    cantitatea, vehiculul, transportatorul, localitățile) sunt marcate deodată; nimic trimis."""
    patron.firma(firma_fact["nume"])
    pg = patron.pg
    _card(patron, "etransport", "#et-trimite")
    pg.click("#et-trimite")
    pg.wait_for_selector("#b0-denumire[aria-invalid='true']", timeout=20000)
    patron.captura()
    for camp in ("et-tip", "b0-cod_scop", "b0-denumire", "b0-cantitate", "t-nr_vehicul", "t-cod_org", "s-localitate", "f-strada"):
        assert pg.get_attribute("#" + camp, "aria-invalid") == "true", camp


# ================================================================ 680 — șablonul facturii recurente
def test_def_680_sablonul_are_intrebarile_emiterii_iar_ciorna_se_emite_din_lista(patron, firma_fact):
    """680. Pașii: Facturi recurente -> „+ Șablon nou”: clientul DANTE ales din listă (căutare), seria firmei afișată, cota aleasă pe linie,
    ziua 1, scadența 15 zile, valabil de la 01.01.2026 „până îl opresc”, „Ciornă pregătită — o emit eu” (SPV-ul nu se mai întreabă) ->
    salvat: rândul spune „ciornă pregătită — o emiți tu · scadența la 15 zile · valabil 01.01.2026 – până la oprire” și are „Emite
    factura lunii” -> apăsat: factura emisă, scadentă la 15 zile. Fără modul ales: refuzul lângă alegere."""
    s = firma_fact["schema"]
    emite_api(patron, firma_fact)                                          # DANTE e client al firmei (lista clienților)
    patron.firma(firma_fact["nume"])
    pg = patron.pg
    _card(patron, "facturi", "#fac-recurente")
    pg.click("#fac-recurente")
    pg.wait_for_selector("#fr-add", timeout=20000)
    pg.click("#fr-add")
    pg.wait_for_selector("#fr-client", timeout=20000)
    assert "E2EA" in pg.inner_text("#fr-serie")
    pg.fill("#fr-client-cauta", "dante")
    pg.dispatch_event("#fr-client-cauta", "input")
    pg.select_option("#fr-client", label=pg.locator("#fr-client option", has_text="DANTE").first.inner_text())
    assert pg.input_value("#fr-cui") == CUI_DANTE and pg.input_value("#fr-nume") == "DANTE INTERNATIONAL SA"
    pg.fill("#fr-l0-descriere", PRODUS)
    pg.dispatch_event("#fr-l0-descriere", "input")
    pg.wait_for_timeout(900)
    pg.select_option("#fr-l0-cota", "21")
    pg.fill("#fr-l0-cantitate", "1")
    pg.dispatch_event("#fr-l0-cantitate", "input")
    pg.fill("#fr-l0-pret_unitar", "100")
    pg.dispatch_event("#fr-l0-pret_unitar", "input")
    if not pg.input_value("#fr-l0-um"):   # [lotul 13, regula UM] linia șablonului poartă UM-ul: ce nu propune nomenclatorul scrie omul
        pg.fill("#fr-l0-um", "ora")
        pg.dispatch_event("#fr-l0-um", "input")
    pg.fill("#fr-zi", "1")
    pg.fill("#fr-scadenta", "15")
    pg.fill("#fr-inceput", "2026-01-01")
    pg.click("#fr-pana button[data-val='oprire']")
    pg.click("#fr-salveaza")
    pg.wait_for_selector("#fr-mod[aria-invalid='true'], .msg-eroare[data-camp='fr-mod']", timeout=20000)
    patron.captura("fara_mod")
    pg.click("#fr-mod button[data-val='ciorna']")
    assert not pg.is_visible("#fr-spv-camp")
    patron.captura("sablon")
    pg.click("#fr-salveaza")
    pg.wait_for_selector("#fr-add", timeout=30000)
    rand = pg.locator(".pf-frand", has_text="DANTE INTERNATIONAL SA").first
    rand.wait_for(timeout=10000)
    sub = " ".join(rand.inner_text().split())
    assert "ciornă pregătită — o emiți tu" in sub and "scadența la 15 zile" in sub and "până la oprire" in sub, sub
    assert sql('SELECT mod_emitere, scadenta_zile, trimite_spv FROM "%s".facturi_recurente' % s) == [("ciorna", 15, False)]
    rand.locator("button.fr-emite").click()
    pg.wait_for_function("() => [...document.querySelectorAll('.fr-rez')].some((z) => z.innerText.includes('a fost emisă din șablon'))",
                         timeout=30000)
    patron.captura("emisa")
    zi = sql('SELECT data_emitere, data_scadenta FROM "%s".facturi ORDER BY id DESC LIMIT 1' % s)[0]
    assert (zi[1] - zi[0]).days == 15, zi


# ================================================================ 603 / 604 — borderoul
def test_def_604_borderoul_sta_langa_nir_nu_in_tva_regimuri_speciale(patron, firma_fact):
    """604. Pașii: Operațiuni speciale -> „TVA regimuri speciale”: niciun „Achiziție de la neînregistrat … D394 op. N”; Stocuri: butonul
    „Borderou de achiziție” lângă NIR -> deschide formularul borderoului."""
    patron.firma(firma_fact["nume"])
    pg = patron.pg
    _card(patron, "operatiuni", "[data-op]")
    toate = " ".join(pg.eval_on_selector_all("button[data-op]", "bs => bs.map(b => b.innerText)"))
    assert "neînregistrat" not in toate and "op. N" not in toate, toate
    patron.firma(firma_fact["nume"])                                     # fereastra Operațiunilor acoperă cardurile firmei
    _card(patron, "stocuri", "#s-borderou")
    assert "Borderou" in pg.inner_text("#s-borderou")
    pg.click("#s-borderou")
    pg.wait_for_selector("#op-furnizor_nume", timeout=20000)
    patron.captura()


def test_def_603_nota_borderoului_are_titlul_cu_diacritice_si_sursa_lui(patron, firma_fact):
    """603. Pașii: Stocuri -> Borderou de achiziție (Ion Vanzator E2E, 120 lei, pe cheltuială) -> Registru jurnal: nota se numește
    „Achiziție de la neînregistrat - Ion Vanzator E2E” (cu diacritice), în bază și în Registrul jurnal."""
    s = firma_fact["schema"]
    patron.firma(firma_fact["nume"])
    pg = patron.pg
    _card(patron, "stocuri", "#s-borderou")
    pg.click("#s-borderou")
    pg.wait_for_selector("#op-furnizor_nume", timeout=20000)
    pg.fill("#op-data", AZI.isoformat())
    pg.fill("#op-furnizor_nume", "Ion Vanzator E2E")
    pg.fill("#op-furnizor_adresa", "Str. Livezii 3, Buzău")
    pg.fill("#op-furnizor_act", "BZ 123456")
    pg.fill("#op-valoare", "120")
    pg.fill("#op-cont_cheltuiala", "628")
    pg.select_option("#op-categorie", "alte_bunuri")
    pg.click("#op-trimite")
    pg.wait_for_selector("#op-mesaj .caseta-ok", timeout=30000)
    titlu = sql('SELECT i.descriere FROM "%s".inregistrari i JOIN "%s".facturi f ON f.id = i.factura_id WHERE f.tip = %%s '
                "ORDER BY i.id DESC LIMIT 1" % (s, s), ("borderou",))[0][0]
    assert titlu == "Achiziție de la neînregistrat - Ion Vanzator E2E", titlu
    patron.firma(firma_fact["nume"])
    _card(patron, "jurnal", "#j-nota-noua")
    pg.wait_for_timeout(800)
    t = pg.locator("[data-nota-id]", has_text="Ion Vanzator E2E").first.inner_text()
    patron.captura()
    assert "Achiziție de la neînregistrat" in t and "Achizitie de la neinregistrat" not in t, t


# ================================================================ 611 / 613 / 615 — retestele
def test_def_611_refuzul_achizitiei_de_la_persoana_fizica_numeste_ce_lipseste(patron, firma_fact):
    """611 (rămas de la 402). Unde se vede: Stocuri -> „Borderou de achiziție” -> vânzătorul, 120 lei pe 371, fără articol și cantitate ->
    „Generează”: lista „NU s-a salvat” numește câmpurile — „Articolul (din nomenclator)” și „Cantitatea” — cu ce lipsește, nu doar
    „articolul” / „cantitatea”."""
    patron.firma(firma_fact["nume"])
    pg = patron.pg
    _card(patron, "stocuri", "#s-borderou")
    pg.click("#s-borderou")
    pg.wait_for_selector("#op-furnizor_nume", timeout=20000)
    pg.fill("#op-data", AZI.isoformat())
    pg.fill("#op-furnizor_nume", "Maria Ionescu E2E")
    pg.fill("#op-furnizor_adresa", "Str. Livezii 2, Buzău")
    pg.fill("#op-furnizor_act", "BZ 654321")
    pg.fill("#op-valoare", "120")
    pg.fill("#op-cont_cheltuiala", "371")
    pg.select_option("#op-categorie", "alte_bunuri")
    pg.click("#op-trimite")
    pg.wait_for_selector(".refuz-salvare", timeout=10000)
    patron.captura()
    lista = pg.eval_on_selector_all(".refuz-salvare .refuz-salvare-lista > li", "lis => lis.map(li => li.innerText.trim())")
    assert any(x.startswith("Articolul (din nomenclator)") for x in lista) and any(x.startswith("Cantitatea") for x in lista), lista
    assert all(len(x.split()) > 2 for x in lista), lista                    # fiecare rând spune și ce lipsește, nu doar numele câmpului


def test_def_613_mesajul_articolului_fara_cota_dispare_cand_aleg_cota(patron, firma_fact):
    """613 (rămas de la 415). Unde se vede: firmă cu stoc cantitativ-valoric -> Emite factură -> linia: articolul de stoc „Marfa 613 fara
    cota” (fără produs în nomenclator) -> sub linie, caseta roșie „Articolul „…” n-are cota TVA în nomenclator…” -> cota 21% aleasă pe linie
    -> caseta dispare."""
    _ok(_api(patron, "POST", "/tenants/%d/stocuri/intrare" % firma_fact["tenant_id"], {
        "denumire": "Marfa 613 fara cota", "um": "buc", "data": AZI.isoformat(), "cantitate": 5, "pret_unitar": 10, "document": "NIR 613"}),
        "intrare")
    _deschide_emiterea(patron, firma_fact["nume"])
    pg = patron.pg
    pg.wait_for_selector("#em-l0-articol", timeout=20000)
    pg.select_option("#em-l0-articol", label=pg.eval_on_selector("#em-l0-articol",
                     "(s) => [...s.options].find((o) => o.textContent.startsWith('Marfa 613 fara cota')).textContent"))
    pg.wait_for_selector("#em-l0-cota-mesaj .caseta-atentie", timeout=15000)
    assert "n-are cota TVA în nomenclator" in pg.inner_text("#em-l0-cota-mesaj")
    patron.captura("mesajul")
    pg.select_option("#em-l0-cota", "21")
    pg.wait_for_function("() => !document.querySelector('#em-l0-cota-mesaj').textContent.trim()", timeout=5000)
    patron.captura("cota_aleasa")


def test_def_615_dupa_stornare_factura_e_stornata_fara_reimprospatare(patron, firma_fact):
    """615 (rămas de la 419). Pașii: factură cu articolul din stoc, „Pleacă marfa: Da” -> Stornează -> „marfa se întoarce: Da” -> Confirm:
    „Storno creat” rămâne; fără reîmprospătare: nicăieri „Se stornează…”, factura „stornată” (nu „neîncasată”), fără „Stornează” și „Emite
    chitanță”."""
    from e2e_bloc_a import _deschide_factura as _df
    aid = articol_in_stoc(patron, firma_fact, cantitate=22, pret=10)
    f = emite_api(patron, firma_fact, linii=[{"descriere": ARTICOL, "cantitate": 1, "um": "buc", "pret_unitar": 20.0, "cota_tva": 21,
                                              "cota_propusa": 21, "articol_id": aid}], pleaca_marfa=True)
    _df(patron, firma_fact, f["factura_id"])
    pg = patron.pg
    pg.click("#fd-storno")
    pg.wait_for_selector("#fd-storno-retur", timeout=10000)
    pg.select_option("#fd-storno-retur", "true")
    pg.click("#fd-storno-ok")
    pg.wait_for_function("() => (document.querySelector('#fd-storno-rez') || {}).textContent && "
                         "document.querySelector('#fd-storno-rez').textContent.includes('Storno creat')", timeout=30000)
    patron.captura()
    sus = " ".join(pg.inner_text(".fd-antet-sus").split())
    assert "Se stornează" not in pg.inner_text("body") and "stornată" in sus and "neîncasată" not in sus, sus
    assert pg.get_attribute("#fd-storno", "aria-disabled") == "true" and pg.get_attribute("#fd-chitanta", "aria-disabled") == "true"   # [675]
