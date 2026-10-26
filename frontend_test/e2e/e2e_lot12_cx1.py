# -*- coding: utf-8 -*-
"""Lotul 12, pachetul `cx1` — testele de capăt la capăt care lipseau pentru deficiențele găsite de Code în facturi, bancă, casă, portal și
D394, plus generatoarele fișierelor pentru dovezile pe firmele de test (`frontend_test/dovada/dovezi_lot12_cx1.json`, pasul „incarca”).

  C112 Istoricul facturilor: încasările în lei față de totalul în lei (factura în valută încasată parțial nu e „încasată”).
  C113 Cashflow-ul din portalul clientului: factura în valută intră cu totalul ei în lei.
  C114 Chitanța pozată: facturile primite plătite deja prin bancă nu mai sunt oferite „Ce plătește chitanța?”.
  C115 Borderoul de achiziție: linia poartă UM-ul articolului nou ales pe ecran ȘI al articolului ales din nomenclator, nu „buc”.
  C120 XML-ul e-Factura între alte două firme: refuzat la import ȘI la validare (dacă a ajuns în lista „de validat”).
  C124 „Verifică acum în SPV”: motivul aplicației nu e scris „ANAF a răspuns: …”.
  C125 Răspunsul importului de extras păstrează sensul liniei (încasare / plată).
  C135 Nota de casă a facturii, scrisă cu numărul lipit: Registrul jurnal o arată cu seria separat.
  C144 Potrivirea din Bancă / Casă oferă numai documentele cu încasare (fără proforme).
  C145 Pragul Intrastat numără numai documentele fiscale (fără proforme).
  C152 Mesajele D394 (factura din bon fără Z, chitanța fără cotă, încasarea fără chitanță): data ZZ.LL.AAAA, felul operațiunii în cuvinte.

Pașii contabilului pe aplicația din index, pe baza de TEST, pe firme NOI (`firma_e2e` / `firma_noua`), pregătite pe rutele ecranelor
(`e2e_bloc_a.pregateste_firma`). Facturile se emit pe ruta formularului (`POST facturi/emite`); cea în EUR cu cursul introdus de mână
(5 lei, consemnat cu autorul — `facturi_api.emite_factura`), ca totalul în lei să fie cunoscut. Plățile prin bancă: extrasul încărcat pe
ecranul Bancă -> „Alege facturile” -> „Contează selectate”. Clientul DANTE INTERNATIONAL SA, CUI 14399840; codul de TVA german DE136695976
— cifrele de control verificate (`e2e_lot12_firme1.py`). Fișierul e-Factura de probă: `ghid_incoming/lot12_fisiere_proba` (F1, DANTE
DNT-RT-1020), cu cumpărătorul F1 Comert Stoc SRL — pentru firma nouă a testului e „între alte două firme”.

DATE DE PORNIRE scrise direct, declarate la fiecare scriere: nota de casă cu numărul facturii lipit (cum o scria `casa_api.leaga` înainte
de 443 / C135), factura între alte două firme ajunsă în lista de validat înainte de C120, chitanța anulată (starea încasării fără chitanță
de dinainte de 456 (a), pe care Casa de acum n-o mai produce).

Temei: N/A — afișarea și potrivirea documentelor (CLAUDE.md §9); pragul Intrastat și temeiul lui stau în `core/intrastat.py` (testul nu
atinge valoarea pragului); data în forma pentru om: DESIGN_SYSTEM cap.4.

Aserțiunile sunt pe structură (câmpurile răspunsurilor, `data-*`, cifrele citite de pe ecran, rândurile din bază) sau pe textul produs de
funcția-sursă din cod (`efactura_import.alta_firma`, `jurnal_api.fara_serie_lipita`, `spv_conector.MESAJ_CITIRE_NECONECTAT`,
`casa_api.ETICHETE_CATEGORIE`, `pdf_util.data_ro`) — nu pe șiruri scrise aici. MUTAȚIILE: `mut_lot12_cx1.json`, câte una pe test."""
import contextlib
import datetime as _dt
import hashlib
import io
import json
import re
import time
from decimal import Decimal

import pytest

from conftest import BAZA, _ecran, ai_pregateste, alege_perioada, alege_tipul, firma_noua, sql
from e2e_bloc_a import AZI, CLIENT, _api, _card, _ok, _profil as _profil_bloc_a, emite_api, pregateste_firma
from e2e_bloc_b import _deschide_rand, _nota_jn

ecran_cont = contextlib.contextmanager(_ecran)
PROBA_XML = "/home/costin/ghid_incoming/lot12_fisiere_proba/F1_efactura_DANTE_DNT-RT-1020.xml"
DANTE = "14399840"
DE_CLIENT = "DE136695976"
#: imaginea minimă (JPEG 1×1) a chitanței pozate — `_common.tip_imagine` citește octeții, nu numele (aceeași ca `e2e_bloc_a`, 9)
JPEG = bytes.fromhex("ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c"
                     "1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432ffc0000b080001000101011100ffc4001f0000010501010101"
                     "010100000000000000000102030405060708090a0bffda0008010100003f00d2cf20ffd9")
_SUMA = re.compile(r"\d{1,3}(?:\.\d{3})*,\d{2}")


def _tag():
    return int(time.time() * 1000) % 1000000


def _sume(text):
    """Sumele scrise de ecran (`bani`: 1.234,56), ca numere."""
    return {Decimal(x.replace(".", "").replace(",", ".")) for x in _SUMA.findall(text or "")}


def _t(pg, sel):
    return " ".join(pg.inner_text(sel).split())


def _emite(patron, firma, pret, cantitate=1, moneda="RON", curs=None, tip="factura", tert=None, zi=None, bon=None, descriere=None):
    """Un document emis pe ruta formularului (`POST facturi/emite`), cu payload-ul ecranului. `curs` = cursul introdus de mână (cu data
    lui = data facturii); `bon` = (numărul, data) bonului fiscal pe baza căruia se emite factura; `tert` = câmpurile clientului."""
    zi = zi or AZI
    corp = {"linii": [{"descriere": descriere or "Servicii E2E CX1", "cantitate": cantitate, "um": "buc", "pret_unitar": pret,
                       "cota_tva": 21, "cota_propusa": 21, "articol_id": None}],
            "tert_nume": CLIENT["#em-nume"], "tert_cui": CLIENT["#em-cui"], "tert_adresa": CLIENT["#em-adresa"], "moneda": moneda,
            "tert_tara": "RO", "tip_operatiune": "normal", "bon_fiscal_nr": None, "bon_fiscal_data": None,
            "data_emitere": zi.isoformat(), "data_scadenta": (zi + _dt.timedelta(days=30)).isoformat() if tip == "factura" else None,
            "tip": tip}
    if curs is not None:
        corp.update(curs_manual=curs, data_curs_manual=zi.isoformat())
    if bon:
        corp.update(bon_fiscal_nr=bon[0], bon_fiscal_data=bon[1].isoformat())
    corp.update(tert or {})
    return _ok(_api(patron, "POST", "/tenants/%d/facturi/emite" % firma["tenant_id"], corp), "emitere %s" % tip)


# ── Bancă ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _banca(e, firma):
    e.firma(firma["nume"])
    _card(e, "banca", "#bk-fisier")


def _incarca_extras(pg, csv_text, eticheta):
    """Extrasul CSV încărcat pe ecranul Bancă; întoarce răspunsul importului (cel primit de ecran)."""
    pg.evaluate("() => { const m = document.querySelector('#bk-mesaj'); if (m) m.innerHTML = ''; }")
    with pg.expect_response(lambda r: "/banca/reconciliere/import" in r.url and r.request.method == "POST", timeout=60000) as rr:
        pg.set_input_files("#bk-fisier", {"name": "extras_e2e_%s_%d.csv" % (eticheta, time.time()), "mimeType": "text/csv",
                                          "buffer": csv_text.encode("utf-8")})
    pg.wait_for_function("() => { const t = document.querySelector('#bk-mesaj').innerText; return t && !t.includes('Se cite'); }",
                         timeout=30000)
    return rr.value.json()


def _alege_facturile(pg, text_linie):
    """„Alege facturile” pe rândul liniei `text_linie`; întoarce rândul. [lotul 13, 673] Lista facturilor deschise e în fereastra ei."""
    rand = pg.locator("#bk-lista tbody.tn-nota", has_text=text_linie).first
    rand.wait_for(timeout=20000)
    rand.locator("[data-alege]").click()
    pg.wait_for_selector(".fereastra:last-of-type #bk-pk-ok", timeout=20000)
    return rand


def _fid_oferite(pg, zona, atribut):
    return {int(x) for x in pg.eval_on_selector_all("%s [%s]" % (zona, atribut), "(els, a) => els.map((e) => e.getAttribute(a))", atribut)}


def _conteaza_pe_factura(pg, text_linie, fid):
    """Linia `text_linie` -> „Alege facturile” -> factura `fid` bifată -> „Contează selectate”: nota se creează."""
    _alege_facturile(pg, text_linie)
    pg.check(".fereastra:last-of-type input[data-fid='%d']" % fid)
    pg.click(".fereastra:last-of-type #bk-pk-ok")
    # [lotul 13, 673] fereastra alegerii se închide; confirmarea contării e în zona de mesaj a Băncii
    pg.wait_for_function("() => !document.querySelector('#bk-pk-ok') && "
                         "((document.querySelector('#bk-mesaj') || {}).innerText || '').length > 0", timeout=30000)


def _istoric_detaliu(e, firma, fid):
    """Facturi -> „Istoric facturi” (luna de azi) -> rândul documentului `fid` (cu „Vezi și facturile mai vechi” cât trebuie) -> detaliul."""
    e.firma(firma["nume"])
    _card(e, "facturi", "#fac-istoric")
    pg = e.pg
    pg.click("#fac-istoric")
    pg.wait_for_selector("#fac-prev", timeout=25000)
    sel = ".fac-frand-btn[data-id='%d']" % fid
    for _ in range(10):
        pg.wait_for_function("() => !document.body.innerText.includes('Se încarcă')", timeout=25000)
        if pg.locator(sel).count() or not pg.locator("#fac-mai-multe:not([aria-disabled='true'])").count():   # [lotul 13, 675] inactiv = toate afișate
            break
        pg.click("#fac-mai-multe")
    pg.click(sel)
    pg.wait_for_selector(".fd-td-um", timeout=25000)


# ── C112 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c112_istoricul_compara_incasarile_in_lei_cu_totalul_in_lei(patron, firma_e2e):
    """C112. Pașii: factura emisă în EUR, 100,00 + TVA 21% = 121,00 EUR, cursul 5 (total în evidență 605,00 lei) -> Bancă: încasarea de
    300,00 lei -> „Alege facturile” -> factura -> „Contează selectate” -> Facturi -> „Istoric facturi”: rândul facturii spune „încasată
    parțial: 300,00 din 605,00 lei” (înainte: „încasată” — 300 lei comparați cu 121 EUR).
    MUTAȚIA: `facturi_api._cu_stare_incasare` ia totalul din `antet_lei` (totalul în valută pe listă) -> „încasată” -> ROȘU."""
    pregateste_firma(patron, firma_e2e)
    f = _emite(patron, firma_e2e, 100, moneda="EUR", curs=5, descriere="Servicii E2E C112")
    fid = f["factura_id"]
    ((total, total_lei),) = sql('SELECT total, total_lei FROM "%s".facturi WHERE id = %%s' % firma_e2e["schema"], (fid,))
    assert (total, total_lei) == (Decimal("121.00"), Decimal("605.00")), (total, total_lei)   # premisa: valuta ≠ lei
    zi = AZI.strftime("%d.%m.%Y")
    _banca(patron, firma_e2e)
    pg = patron.pg
    _incarca_extras(pg, "Data;Detalii;Suma\n%s;Incasare E2E C112 DANTE;300,00\n" % zi, "c112")
    _conteaza_pe_factura(pg, "Incasare E2E C112", fid)
    assert sql('SELECT count(*) FROM "%s".inregistrari WHERE factura_id = %%s AND sursa = \'banca\'' % firma_e2e["schema"], (fid,)) == [(1,)]
    patron.firma(firma_e2e["nume"])
    _card(patron, "facturi", "#fac-istoric")
    with pg.expect_response(lambda r: "/facturi?an=" in r.url and r.request.method == "GET", timeout=30000) as rr:
        pg.click("#fac-istoric")
    rand = pg.locator(".fac-frand-btn[data-id='%d']" % fid)
    rand.wait_for(timeout=25000)
    sub = " ".join(rand.locator(".pf-frand-sub").inner_text().split())
    patron.captura("istoric_partial")
    (st,) = [x["stare_incasare"] for x in rr.value.json()["facturi"] if x["id"] == fid]
    assert (st["stare"], Decimal(st["incasat"]), Decimal(st["total"])) == ("partial", Decimal("300.00"), Decimal("605.00")), st
    assert {Decimal("300.00"), Decimal("605.00")} <= _sume(sub), sub   # încasat din total, amândouă în lei, pe rândul facturii


# ── C113 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def firma_portal():
    for f in firma_noua():
        yield f


def _scoate_contul(email):
    from e2e_lot12_start import _scoate_contul as scoate
    scoate(email)


def test_def_c113_cashflow_portalului_ia_totalul_facturii_in_lei(patron, firma_portal, browser, request):
    """C113. Pașii: contabilul emite factura în EUR (121,00 EUR, cursul 5 -> 605,00 lei, scadentă peste 30 de zile) și îi validează nota
    (4111 = 605,00) -> dă acces clientului la portal -> clientul: „Cifrele firmei” -> „Previziune bani (8 săptămâni)”: în săptămâna
    scadenței intră +605 lei (înainte: +121 — totalul în EUR luat ca lei, deși soldul din balanță e în lei).
    MUTAȚIA: `repo_facturi.de_incasat` ia `total` (în valută) drept rest în lei (funcția `pentru_cashflow`, scoasă în lotul 13, a fost înlocuită de
    `repo_portal.facturi_deschise_validate`) -> +121 -> ROȘU."""
    pregateste_firma(patron, firma_portal)
    s, tid = firma_portal["schema"], firma_portal["tenant_id"]
    f = _emite(patron, firma_portal, 100, moneda="EUR", curs=5, descriere="Servicii E2E C113")
    ((nid,),) = sql('SELECT id FROM "%s".inregistrari WHERE factura_id = %%s AND sursa = \'facturi\'' % s, (f["factura_id"],))
    _ok(_api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (tid, nid), {}), "validarea notei facturii")   # „Validează” din Registrul jurnal
    email = "e2e.l12.c113.%d@exemplu.ro" % (int(time.time() * 1000) % 100000000)
    _scoate_contul(email)
    try:
        _ok(_api(patron, "POST", "/tenants/%d/client-acces" % tid, {"email": email, "nume": "Client Probă C113"}), "acces client")
        # contul de test a trecut de „Bun venit” (ca `cont_asistent(bun_venit_vazut=True)`): fereastra lui, deschisă de aplicație la prima
        # intrare, ar acoperi cardurile portalului — proba e previziunea, nu primirea
        sql("UPDATE public.users SET bun_venit_vazut_la = now() WHERE email = %s", (email,))
        with ecran_cont(browser, request, email) as c:
            cp = c.pg
            cp.goto(BAZA + "/", wait_until="domcontentloaded")
            card = cp.locator("button.cab-card", has_text="Cifrele firmei").first
            card.wait_for(timeout=30000)
            with cp.expect_response(lambda r: "/portal/cashflow" in r.url, timeout=30000) as rr:
                card.click()
            cp.wait_for_selector("#cf-zona .pf-frand", timeout=30000)
            randuri = cp.eval_on_selector_all("#cf-zona .pf-frand", "els => els.map((e) => e.innerText)")
            c.captura("previziune")
            raspuns = rr.value.json()   # citit cât contextul clientului e deschis (la ieșirea din `with` se închide)
        incasari = [Decimal(str(w["incasari"])) for w in raspuns["saptamani"]]
        assert sum(incasari) == Decimal("605") and Decimal("605") in incasari, incasari   # factura întreagă, în lei, o dată
        pe_ecran = [Decimal(m.replace(".", "").replace(",", ".")) for r in randuri for m in re.findall(r"\+([\d.]+(?:,\d+)?) lei", r)]
        assert pe_ecran == [Decimal("605")], randuri
    finally:
        _scoate_contul(email)


# ── C114 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _primita_manual(patron, firma, numar, pret):
    _ok(_api(patron, "POST", "/tenants/%d/facturi-primite/manual" % firma["tenant_id"],
             {"tert_tara": "RO", "tert_cui": DANTE, "tert_nume": "DANTE INTERNATIONAL SA", "serie": "DNT", "numar": numar,
              "data_emitere": AZI.isoformat(), "moneda": "RON", "cont": "628",
              "linii": [{"descriere": "Servicii curierat", "cantitate": "1", "um": "buc", "pret_unitar": str(pret), "cota_tva": "21"}]}),
        "factura primită %s" % numar)
    return sql('SELECT id FROM "%s".facturi WHERE numar = %%s AND directie = \'primita\'' % firma["schema"], (numar,))[0][0]


def test_def_c114_chitanta_pozata_nu_ofera_factura_platita_prin_banca(patron, firma_e2e):
    """C114. Pașii: două facturi primite de la DANTE (121,00 și 242,00 lei, introduse de mână) -> Bancă: plata de 121,00 lei -> „Alege
    facturile” -> prima -> „Contează selectate” -> „Bonuri și chitanțe” -> „Adaugă document”: chitanța DANTE de 121,00 lei (citită de
    model) -> deschisă: „Ce plătește chitanța?” oferă numai factura de 242,00 lei, nu și pe cea plătită prin bancă (o a doua plată).
    MUTAȚIA: `repo_facturi.candidate_pentru_bon` înapoi pe „neplătită = fără `platita_la`” -> prima e oferită -> ROȘU."""
    pregateste_firma(patron, firma_e2e)
    t = _tag()
    platita = _primita_manual(patron, firma_e2e, "C114A%d" % t, 100)
    neplatita = _primita_manual(patron, firma_e2e, "C114B%d" % t, 200)
    _banca(patron, firma_e2e)
    pg = patron.pg
    _incarca_extras(pg, "Data;Detalii;Suma\n%s;Plata E2E C114 DANTE;-121,00\n" % AZI.strftime("%d.%m.%Y"), "c114")
    _conteaza_pe_factura(pg, "Plata E2E C114", platita)
    ai_pregateste(json.dumps({"tip": "chitanta", "comerciant": "DANTE INTERNATIONAL SA", "cui": DANTE, "data": AZI.isoformat(),
                              "total": 121.0, "numar_document": "CH%d" % t, "mentiuni": "contravaloare factura", "articole": [], "tva": [],
                              "bon_complet": True, "orientare": 0}))
    patron.firma(firma_e2e["nume"])
    _card(patron, "bonuri", "#bc-adauga")
    with pg.expect_response(lambda r: "/confirma" in r.url and "/portal/bon/" in r.url, timeout=60000):
        pg.set_input_files("#bc-fisier", {"name": "chitanta_c114.jpg", "mimeType": "image/jpeg", "buffer": JPEG})
    pg.locator("[data-doc]", has_text="DANTE").first.wait_for(timeout=30000)
    pg.locator("[data-doc]", has_text="DANTE").first.click()
    pg.wait_for_selector("input[name='d-fact']", timeout=30000)
    pg.wait_for_function("() => document.querySelectorAll(\"input[name='d-fact']\").length > 1", timeout=30000)
    oferite = {x for x in pg.eval_on_selector_all("input[name='d-fact']", "els => els.map((e) => e.value)") if x}
    patron.captura("ce_plateste_chitanta")
    assert str(neplatita) in oferite, oferite             # factura cu ceva de plătit
    assert str(platita) not in oferite, oferite           # plătită prin bancă: nu se mai oferă


# ── C115 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _borderou(patron, firma, nume, articol_id=None, articol_nou=None, um=None, cantitate="100", valoare="150"):
    """Stocuri -> „Borderou de achiziție” -> vânzătorul persoană fizică, valoarea, contul 371, articolul (din listă sau nou, cu UM-ul
    ales), cantitatea, categoria -> „Generează nota”. Întoarce răspunsul generării."""
    patron.firma(firma["nume"])
    _card(patron, "stocuri", "#s-borderou")
    pg = patron.pg
    pg.click("#s-borderou")
    pg.wait_for_selector("#op-furnizor_nume", timeout=20000)
    pg.fill("#op-data", AZI.isoformat())
    pg.fill("#op-furnizor_nume", nume)
    pg.fill("#op-furnizor_adresa", "Str. Mare 2, Cluj-Napoca")
    pg.fill("#op-furnizor_act", "CJ 123456")
    pg.fill("#op-valoare", valoare)
    pg.fill("#op-cont_cheltuiala", "371")
    if articol_nou:
        pg.select_option("#op-articol", "__nou__")
        pg.fill("#op-articol_den", articol_nou)
        pg.fill("#op-um", um)
    else:
        pg.select_option("#op-articol", str(articol_id))
    pg.fill("#op-cantitate", cantitate)
    pg.select_option("#op-categorie", "1001")
    with pg.expect_response(lambda r: "/achizitie-neinregistrat" in r.url and r.request.method == "POST", timeout=30000) as rr:
        pg.click("#op-trimite")
    pg.wait_for_selector("#op-mesaj .caseta-ok", timeout=20000)
    assert rr.value.status == 200, rr.value.text()
    return rr.value.json()


def test_def_c115_borderoul_scrie_um_ul_articolului(patron, firma_e2e):
    """C115 (ambele drumuri). Pașii: (a) Stocuri -> „Borderou de achiziție” -> „Articol nou…” „Floarea-soarelui E2E C115”, UM „t” ->
    „Generează nota”; (b) articolul „Porumb E2E C115” (în nomenclator în „kg”) ALES din listă -> „Generează nota” -> Facturi -> „Istoric
    facturi” -> fiecare borderou: linia are UM-ul „t”, respectiv „kg”, iar articolul intră în stoc în UM-ul lui (înainte: „buc” pe linie).
    MUTAȚIA: `uc_tenants` (borderoul) cu `um_stoc = "buc"` -> amândouă liniile „buc” -> ROȘU."""
    pregateste_firma(patron, firma_e2e)
    s, t = firma_e2e["schema"], _tag()
    porumb = "Porumb E2E C115 %d" % t
    aid = _ok(_api(patron, "POST", "/tenants/%d/stocuri/intrare" % firma_e2e["tenant_id"],
                   {"denumire": porumb, "um": "kg", "data": AZI.isoformat(), "cantitate": 10, "pret_unitar": 1, "cont_stoc": "371"}),
              "articolul din nomenclator (Mișcări › intrare)")["articol_id"]
    nou = _borderou(patron, firma_e2e, "Vasile Pop C115", articol_nou="Floarea-soarelui E2E C115 %d" % t, um="t")
    ales = _borderou(patron, firma_e2e, "Maria Pop C115", articol_id=aid)
    for r, um in ((nou, "t"), (ales, "kg")):
        assert sql('SELECT um FROM "%s".factura_linii WHERE factura_id = %%s' % s, (r["factura_id"],)) == [(um,)], (r, um)
        assert sql('SELECT a.um FROM "%s".miscari_stoc m JOIN "%s".articole a ON a.id = m.articol_id WHERE m.factura_id = %%s'
                   % (s, s), (r["factura_id"],)) == [(um,)], (r, um)
        _istoric_detaliu(patron, firma_e2e, r["factura_id"])
        patron.captura("borderou_um_%s" % um)
        assert patron.pg.eval_on_selector_all(".fd-td-um", "els => els.map((e) => e.innerText.trim())") == [um]


# ── C120 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _xml_altei_firme(tag):
    """Fișierul de probă real (DANTE -> F1 Comert Stoc SRL), cu numărul `tag`: pentru firma nouă a testului, o factură între alte două firme."""
    return io.open(PROBA_XML, encoding="utf-8").read().replace("DNT-RT-1020", tag).encode("utf-8")


def _refuz_asteptat(firma, xml):
    """Refuzul pe care îl dă aplicația pentru factura între alte două firme: sursa unică, `efactura_import.alta_firma`."""
    from core import efactura_import as efi
    cif = "".join(c for c in sql('SELECT cui FROM "%s".firma_profil WHERE id = 1' % firma["schema"])[0][0] if c.isdigit())
    msg = efi.alta_firma(efi.parseaza_xml(xml, cif), cif)
    assert msg, "premisa: fișierul de probă nu e între alte două firme pentru firma testului"
    return msg


def _primite(patron, firma):
    patron.firma(firma["nume"])
    _card(patron, "facturi", "#fac-primite")
    patron.pg.click("#fac-primite")
    patron.pg.wait_for_selector("#fp-manual", timeout=25000)


def test_def_c120_xml_intre_alte_doua_firme_e_refuzat_la_import(patron, firma_e2e):
    """C120 (importul). Pașii: Facturi -> „Facturi primite (SPV)” -> „Importă XML UBL” cu factura DANTE -> F1 Comert Stoc SRL (alt CUI decât
    al firmei): mesajul spune că factura nu e a firmei (emitentul, cumpărătorul, CUI-ul firmei), nimic nu intră în lista de validat.
    MUTAȚIA: `spv_receive.importa_xml_manual` fără `alta_firma` -> factura intră în listă -> ROȘU."""
    pregateste_firma(patron, firma_e2e)
    s = firma_e2e["schema"]
    tag, nume = "E2EC120A-%d" % _tag(), "c120_import_%d.xml" % _tag()
    xml = _xml_altei_firme(tag)
    asteptat = _refuz_asteptat(firma_e2e, xml)
    inainte = sql('SELECT count(*) FROM "%s".efactura_primite' % s)[0][0]
    _primite(patron, firma_e2e)
    pg = patron.pg
    with pg.expect_response(lambda r: "/facturi-primite/import-xml" in r.url, timeout=40000) as rr:
        pg.set_input_files("#fp-xml", {"name": nume, "mimeType": "text/xml", "buffer": xml})
    pg.wait_for_function("(m) => (document.querySelector('#fp-mesaj') || {innerText: ''}).innerText.includes(m)", arg=asteptat[:60],
                         timeout=40000)
    patron.captura("refuzat_la_import")
    r = rr.value.json()
    assert (r["importate"], r["erori"]) == (0, ["%s: %s" % (nume, asteptat)]), r
    assert asteptat in " ".join(pg.inner_text("#fp-mesaj").split()), pg.inner_text("#fp-mesaj")
    assert sql('SELECT count(*) FROM "%s".efactura_primite' % s)[0][0] == inainte
    assert pg.locator(".fac-primita-btn", has_text=tag).count() == 0


def test_def_c120_xml_intre_alte_doua_firme_ajuns_in_lista_nu_se_valideaza(patron, firma_e2e):
    """C120 (validarea). Pașii: în lista „de validat” e o factură DANTE -> F1 Comert Stoc SRL intrată înainte de reparație (date de
    pornire) -> Facturi primite -> deschisă -> contul 628 -> „Validează” -> „Validează”: refuzul spune că factura nu e a firmei; nicio
    factură, nicio notă scrisă, factura rămâne nevalidată.
    MUTAȚIA: `uc_tenants.factura_primita_valideaza` fără refuzul `alta_firma` -> factura se validează (cheltuială și TVA de dedus) -> ROȘU."""
    pregateste_firma(patron, firma_e2e)
    s = firma_e2e["schema"]
    tag = "E2EC120V-%d" % _tag()
    xml = _xml_altei_firme(tag)
    asteptat = _refuz_asteptat(firma_e2e, xml)
    cif = "".join(c for c in sql('SELECT cui FROM "%s".firma_profil WHERE id = 1' % s)[0][0] if c.isdigit())
    txt = xml.decode("utf-8")
    sha = hashlib.sha256(xml).hexdigest()
    # date-de-pornire: factura între alte două firme intrată în lista de validat înainte de C120 (importul / SPV-ul de atunci n-o refuza)
    pid = sql('INSERT INTO "%s".efactura_primite (id_mesaj_anaf, cif_emitent, cif_beneficiar, tip, xml_brut, xml_sha256, status) '
              "VALUES (%%s, %%s, %%s, 'MANUAL', %%s, %%s, 'ciorna') RETURNING id" % s, ("e2e-c120-" + sha[:40], DANTE, cif, txt, sha))[0][0]
    _primite(patron, firma_e2e)
    pg = patron.pg
    pg.click(".fac-primita-btn[data-id='%d']" % pid)
    pg.wait_for_selector("#pr-cont", timeout=20000)
    pg.fill("#pr-cont", "628")
    with pg.expect_response(lambda r: "/facturi-primite/%d/valideaza" % pid in r.url, timeout=40000) as rr:
        pg.click("#pr-valideaza")
        pg.click("#ca-ok")
    pg.wait_for_function("(m) => [...document.querySelectorAll('.fereastra')].pop().innerText.includes(m)", arg=asteptat[:60], timeout=30000)
    patron.captura("refuzat_la_validare")
    assert rr.value.status == 422, (rr.value.status, rr.value.text())
    assert asteptat in " ".join(patron.fereastra().split())
    assert sql('SELECT status, factura_id FROM "%s".efactura_primite WHERE id = %%s' % s, (pid,)) == [("ciorna", None)]
    assert sql('SELECT count(*) FROM "%s".facturi WHERE numar = %%s' % s, (tag,)) == [(0,)]


# ── C124 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c124_verifica_acum_in_spv_nu_pune_motivul_aplicatiei_pe_seama_anaf(patron, firma_e2e):
    """C124. Pașii (cabinetul de test nu e conectat la SPV): Facturi -> „Facturi primite (SPV)” -> „Verifică acum în SPV”: mesajul e
    motivul aplicației, „Cabinetul nu e conectat la SPV.” — fără „ANAF a răspuns: „…”” în față (ANAF nici n-a fost întrebat).
    MUTAȚIA: `facturi_ecran.js` scrie mereu „ANAF a răspuns: „…”.” -> ROȘU."""
    from core import spv_conector as sc
    if sql("SELECT count(*) FROM public.spv_token WHERE accounting_firm_id = %s AND activ", (firma_e2e["cabinet_id"],))[0][0]:
        pytest.fail("cabinetul de test are o conexiune SPV activă: proba „motivul aplicației” n-ar avea subiect")
    pregateste_firma(patron, firma_e2e)
    _primite(patron, firma_e2e)
    pg = patron.pg
    with pg.expect_response(lambda r: "/spv/verifica-acum" in r.url, timeout=60000) as rr:
        pg.click("#fp-verifica")
    pg.wait_for_function("() => { const m = document.querySelector('#fp-mesaj'); return m && m.innerText && !m.innerText.includes('Se citește'); }",
                         timeout=30000)
    patron.captura("motivul_aplicatiei")
    c = rr.value.json()["citire"]
    assert (c["eroare"], c["de_la_anaf"]) == (sc.MESAJ_CITIRE_NECONECTAT, False), c
    assert " ".join(pg.inner_text("#fp-mesaj").split()) == sc.MESAJ_CITIRE_NECONECTAT


# ── C125 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c125_raspunsul_importului_pastreaza_sensul_liniei(patron, firma_e2e):
    """C125. Pașii: Bancă -> extrasul cu o încasare (+125,00) și o plată (−12,50): răspunsul importului (cel primit de ecran) spune, pe
    fiecare linie, „incasare” / „plata” — nu „reconciliere extras” (cheia afirmației potrivirii scria peste sensul liniei).
    MUTAȚIA: `reconciliere_api.importa_extras` pune afirmația potrivirii DUPĂ câmpurile liniei -> „tip” = „reconciliere extras” -> ROȘU."""
    pregateste_firma(patron, firma_e2e)
    t = _tag()
    zi = AZI.strftime("%d.%m.%Y")
    inc, pla = "Incasare E2E C125 %d" % t, "Plata E2E C125 %d" % t
    _banca(patron, firma_e2e)
    r = _incarca_extras(patron.pg, "Data;Detalii;Suma\n%s;%s;125,00\n%s;%s;-12,50\n" % (zi, inc, zi, pla), "c125")
    patron.pg.locator("#bk-lista tbody.tn-nota", has_text=pla).first.wait_for(timeout=20000)
    patron.captura("import")
    assert {x["descriere"]: (x["tip"], Decimal(x["suma"])) for x in r["linii"]} == {inc: ("incasare", Decimal("125.00")),
                                                                                    pla: ("plata", Decimal("12.50"))}, r["linii"]


# ── C135 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c135_nota_de_casa_a_facturii_arata_seria_separat(patron, firma_e2e):
    """C135. Pașii: factura emisă (363,00 lei) -> Casă -> „+ Dispoziție nouă”: încasare de la client, 363,00, DANTE, factura bifată ->
    „Adaugă”. Nota ei poartă descrierea scrisă cum o scria Casa înainte de 443 („… factura E2EA<n> din … — DANTE …”, numărul lipit: date
    de pornire) -> Registru jurnal: rândul notei spune „factura E2EA nr. <n> din …” (aceeași formă ca la scriere, `pdf_util.serie_nr`).
    MUTAȚIA: `jurnal_api.SCRISE_DE_APLICATIE` fără notele de casă -> rândul rămâne cu numărul lipit -> ROȘU."""
    from core import casa_api, jurnal_api
    from core.pdf_util import data_ro
    pregateste_firma(patron, firma_e2e)
    s = firma_e2e["schema"]
    f = emite_api(patron, firma_e2e)
    fid = f["factura_id"]
    ((serie, numar, data_f, total),) = sql('SELECT serie, numar, data_emitere, total FROM "%s".facturi WHERE id = %%s' % s, (fid,))
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "casa", "#c-toggle")
    pg.click("#c-toggle")
    pg.fill("#c-data", AZI.isoformat())
    pg.select_option("#c-cat", "incasare_client")
    pg.fill("#c-suma", str(total))
    pg.fill("#c-cui", DANTE)
    pg.dispatch_event("#c-campuri", "change")
    pg.wait_for_selector("#c-facturi [data-cf='%d']" % fid, timeout=20000)
    pg.check("#c-facturi [data-cf='%d']" % fid)
    pg.wait_for_timeout(800)
    pg.click("#c-adauga")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('a fost emisă')", timeout=30000)
    ((nid, stare, partener),) = sql('SELECT i.id, i.status, o.partener FROM "%s".casa_operatiuni o JOIN "%s".inregistrari i '
                                    "ON i.id = o.inregistrare_id WHERE i.factura_id = %%s AND i.sursa = 'casa'" % (s, s), (fid,))
    assert stare == "ciorna", stare   # premisa: nota de casă e ciornă (cea validată nu se poate rescrie)
    vechi = casa_api.descriere_nota({"categorie": "incasare_client", "stinge": "factura %s din %s" % (numar, data_ro(data_f)),
                                     "partener": partener})   # formula lui `casa_api.leaga` de dinainte: `f["numar"]`, numărul lipit
    asteptat = jurnal_api.fara_serie_lipita(vechi, serie, numar)
    assert asteptat != vechi, (vechi, asteptat)   # premisa: textul vechi are numărul lipit
    # date-de-pornire: descrierea notei de casă scrisă de codul de dinainte de 443 / C135 (numărul facturii lipit de serie)
    sql('UPDATE "%s".inregistrari SET descriere = %%s WHERE id = %%s' % s, (vechi, nid))
    patron.firma(firma_e2e["nume"])
    _card(patron, "jurnal", "#j-nota-noua")
    # [lotul 12, 617] rândul notei în tabelul de note: descrierea pe rând (celula „Explicație”), liniile și documentul în detaliu —
    # deschis, ca textul citit să cuprindă tot ce cuprindea rândul vechi (antetul și liniile notei)
    rand = _deschide_rand(patron, _nota_jn(patron, nid))
    rand.scroll_into_view_if_needed()
    text = " ".join(rand.inner_text().split())
    patron.captura("nota_casa_serie_separat")
    assert asteptat in text, (asteptat, text)
    assert vechi not in text, text


# ── C144 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c144_banca_si_casa_nu_ofera_proforma(patron, firma_e2e):
    """C144. Pașii: către DANTE, o factură (2 × 100 + TVA = 242,00) și o proformă (121,00) -> Bancă: încasarea de 121,00 lei -> „Alege
    facturile”: e oferită factura, nu și proforma -> Casă -> „+ Dispoziție nouă”: încasare de la client, DANTE: „Factura încasată” oferă
    factura, nu și proforma (proforma nu se încasează — se încasează factura).
    MUTAȚIA: `reconciliere_api.facturi_deschise` fără filtrul documentelor cu încasare -> proforma e oferită -> ROȘU."""
    pregateste_firma(patron, firma_e2e)
    t = _tag()
    fact = _emite(patron, firma_e2e, 100, cantitate=2, descriere="Servicii E2E C144 factura")["factura_id"]
    prof = _emite(patron, firma_e2e, 100, tip="proforma", descriere="Servicii E2E C144 proforma")["factura_id"]
    _banca(patron, firma_e2e)
    pg = patron.pg
    _incarca_extras(pg, "Data;Detalii;Suma\n%s;Incasare E2E C144 %d DANTE;121,00\n" % (AZI.strftime("%d.%m.%Y"), t), "c144")
    _alege_facturile(pg, "Incasare E2E C144 %d" % t)
    banca = _fid_oferite(pg, ".fereastra:last-of-type #bk-pk-tabel", "data-fid")
    patron.captura("banca_fara_proforma")
    pg.click(".fereastra:last-of-type #bk-pk-nu")
    assert fact in banca and prof not in banca, (fact, prof, banca)
    patron.firma(firma_e2e["nume"])
    _card(patron, "casa", "#c-toggle")
    pg.click("#c-toggle")
    pg.fill("#c-data", AZI.isoformat())
    pg.select_option("#c-cat", "incasare_client")
    pg.fill("#c-suma", "121")
    pg.fill("#c-cui", DANTE)
    pg.dispatch_event("#c-campuri", "change")
    pg.wait_for_selector("#c-facturi [data-cf='%d']" % fact, timeout=20000)
    casa = _fid_oferite(pg, "#c-facturi", "data-cf")
    patron.captura("casa_fara_proforma")
    assert fact in casa and prof not in casa, (fact, prof, casa)


# ── C145 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def firma_ue():
    for f in firma_noua():
        yield f


def test_def_c145_pragul_intrastat_numara_numai_facturile(patron, firma_ue):
    """C145. Pașii: firma emite azi către un client din Germania (DE136695976) o factură de 1.000,00 lei + TVA și o proformă de 7.000,00
    lei + TVA -> Verificări: rândul Intrastat spune „Expedieri: 1000… lei” (numai factura; înainte: 8.000 — proforma număra la prag).
    MUTAȚIA: `repo_facturi.emise_pe_luni_pentru_intrastat` fără filtrul documentelor fiscale -> 8.000 -> ROȘU."""
    pregateste_firma(patron, firma_ue)
    de = {"tert_nume": "KUNDE HANDELS GMBH", "tert_cui": DE_CLIENT, "tert_adresa": "Hauptstrasse 1", "tert_tara": "DE", "tert_oras": "Berlin"}
    _emite(patron, firma_ue, 1000, tert=de, descriere="Servicii E2E C145 factura")
    _emite(patron, firma_ue, 7000, tip="proforma", tert=de, descriere="Servicii E2E C145 proforma")
    patron.firma(firma_ue["nume"])
    pg = patron.pg
    with pg.expect_response(lambda r: "/intrastat-praguri" in r.url, timeout=60000) as rr:
        _card(patron, "verificari", "#vf-prev")
    rand = pg.locator(".pf-frand", has_text="Intrastat").first
    rand.wait_for(timeout=30000)
    sub = " ".join(rand.locator(".pf-frand-sub").inner_text().split())
    patron.captura("intrastat")
    exped = rr.value.json()["expedieri"]
    assert Decimal(exped["cumulat"]) == Decimal("1000"), exped
    (pe_ecran,) = re.findall(r"Expedieri: ([\d.]+) lei", sub)
    assert Decimal(pe_ecran) == Decimal("1000"), sub


# ── C152 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def firma_d394():
    for f in firma_noua():
        yield f


def _profil_d394(patron, firma, exceptata):
    """Date firmă complete pentru D394 (localitate, telefon, declarant), plătitor de TVA lunar; exceptată sau nu de la casa de marcat."""
    pregateste_firma(patron, firma, platitor=True, regim_fiscal="profit")
    p = _profil_bloc_a(firma, amef=exceptata)
    if exceptata:   # exceptarea cere și activitatea (OUG 28/1999 art.2, `activitati_amef.ACTIVITATI`): „a”, ca `e2e_bloc_c.py`
        p["activitate_amef"] = "a"
    p.update({"adresa": "Str. Probei 9", "oras": "Cluj-Napoca", "judet": "CJ", "telefon": "0264111222",
              "declarant_nume": "POPESCU", "declarant_prenume": "ION", "declarant_functie": "ADMINISTRATOR"})
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % firma["tenant_id"], p), "Date firmă")


def _d394(patron, firma, an, luna):
    """Firma -> Declarații -> D394 -> perioada -> „Continuă →” -> pasul 2 (rezultatul sau refuzul); întoarce textul ferestrei."""
    pg = patron.pg
    patron.firma(firma["nume"])
    _card(patron, "declaratii", "#dec-tip")
    alege_tipul(pg, "d394", zona=".fereastra:last-of-type ")
    alege_perioada(pg, an, luna, zona=".fereastra:last-of-type ")
    pg.click(".fereastra:last-of-type #dec-continua")
    pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); return f && (f.innerText.includes("
                         "'Pasul 2 din 3') && (!!f.querySelector('.dec-ok, .dec-avert, .dec-eroare, .caseta-eroare, #dec-trimite, "
                         "details.dec-xml'))); }", timeout=120000)
    return " ".join(patron.fereastra().split())


def _avans_in_casa(patron, firma, zi, suma):
    """Casă -> „+ Dispoziție nouă”: încasare de la client, DANTE, fără factură -> „Adaugă”: chitanța avansului (456 (a)). (id, număr, dată)."""
    patron.firma(firma["nume"])
    pg = patron.pg
    _card(patron, "casa", "#c-toggle")
    pg.click("#c-toggle")
    pg.fill("#c-data", zi.isoformat())
    pg.select_option("#c-cat", "incasare_client")
    pg.fill("#c-suma", str(suma))
    pg.fill("#c-cui", DANTE)
    pg.dispatch_event("#c-campuri", "change")
    pg.wait_for_timeout(800)
    pg.click("#c-adauga")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('a fost emisă')", timeout=30000)
    ((cid, numar, data),) = sql('SELECT id, numar, data FROM "%s".chitante WHERE factura_id IS NULL AND suma = %%s' % firma["schema"], (suma,))
    return cid, numar, data


def test_def_c152_d394_factura_din_bon_fara_z_numeste_data_zz_ll_aaaa(patron, firma_d394):
    """C152 (Z incomplet). Pașii: factura emisă pe 12.05.2026 pe baza bonului fiscal nr. 152 din aceeași zi, fără raport Z în mai ->
    Declarații -> D394, 05/2026 -> Continuă: refuzul numește factura „<număr> din 12.05.2026” (nu „2026-05-12”).
    MUTAȚIA: `d394.genereaza` scrie data Z-ului / facturii din bon cum e în bază -> „din 2026-05-12” -> ROȘU."""
    from core.pdf_util import data_ro
    _profil_d394(patron, firma_d394, exceptata=False)
    zi = _dt.date(2026, 5, 12)
    f = _emite(patron, firma_d394, 100, zi=zi, bon=("152", zi), descriere="Servicii E2E C152 din bon")
    text = _d394(patron, firma_d394, 2026, 5)
    patron.captura("z_incomplet")
    assert patron.pg.locator(".fereastra:last-of-type .dec-eroare").count(), text
    assert "%s din %s" % (f["numar"], data_ro(zi)) in text, text
    assert zi.isoformat() not in text, text


def test_def_c152_d394_chitanta_fara_cota_numeste_data_zz_ll_aaaa(patron, firma_d394):
    """C152 (Î2 neclasificat). Pașii: firma exceptată de la casa de marcat -> Casă: avansul de 152,00 lei de la DANTE (chitanța emisă
    automat, fără cotă) pe 10.06.2026 -> Declarații -> D394, 06/2026 -> Continuă: refuzul numește chitanța „<număr> din 10.06.2026”.
    MUTAȚIA: `d394.genereaza` scrie data chitanței cum e în bază -> „din 2026-06-10” -> ROȘU."""
    from core.pdf_util import data_ro
    _profil_d394(patron, firma_d394, exceptata=True)
    _cid, numar, data = _avans_in_casa(patron, firma_d394, _dt.date(2026, 6, 10), Decimal("152.00"))
    text = _d394(patron, firma_d394, 2026, 6)
    patron.captura("i2_neclasificat")
    assert patron.pg.locator(".fereastra:last-of-type .dec-eroare").count(), text
    assert "%s din %s" % (numar, data_ro(data)) in text, text
    assert data.isoformat() not in text, text


def test_def_c152_d394_incasarea_fara_chitanta_numeste_felul_in_cuvinte(patron, firma_d394):
    """C152 (încasare fără chitanță). Pașii: firma exceptată -> Casă: avansul de 153,00 lei de la DANTE pe 10.07.2026, a cărui chitanță e
    anulată (starea încasării fără chitanță — date de pornire) -> Declarații -> D394, 07/2026 -> Continuă: avertismentul spune „Încasare din
    registrul de casă fără chitanță și fără factură: 10.07.2026, 153.00 lei …” și felul operațiunii în cuvinte („încasare de la client”),
    nu codul intern („incasare_client”).
    MUTAȚIA: `d394.calcul_d394` scrie categoria cum e în bază -> „(incasare_client)” -> ROȘU."""
    from core import casa_api
    from core.pdf_util import data_ro
    _profil_d394(patron, firma_d394, exceptata=True)
    cid, _numar, data = _avans_in_casa(patron, firma_d394, _dt.date(2026, 7, 10), Decimal("153.00"))
    # date-de-pornire: încasarea de la client fără chitanță (cum o salva Casa înainte de 456 (a)); Casa de acum emite chitanța singură
    sql('UPDATE "%s".chitante SET anulata = true WHERE id = %%s' % firma_d394["schema"], (cid,))
    text = _d394(patron, firma_d394, 2026, 7)
    patron.captura("incasare_fara_chitanta")
    felul = casa_api.ETICHETE_CATEGORIE["incasare_client"].lower()
    assert "fără chitanță și fără factură: %s, %s lei" % (data_ro(data), Decimal("153.00")) in text, text
    assert "(%s)" % felul in text, text
    assert "incasare_client" not in text, text


# ── generatoarele fișierelor pentru dovezile pe firmele de test (`frontend_test/dovada/dovezi_lot12_cx1.json`, pasul „incarca”) ───────
def fisier_csv_c150(zi_iso):
    """Extrasul CSV al dovezii C150: două comisioane din aceeași zi, sume mici, evident de probă."""
    zi = _dt.date.fromisoformat(zi_iso).strftime("%d.%m.%Y")
    return ("Data;Detalii;Suma\n%s;Proba C150 Comision administrare cont;-0,15\n%s;Proba C150 Comision mentenanta card;-0,07\n"
            % (zi, zi)).encode("utf-8")


def fisier_mt940_c121(zi_iso):
    """Extrasul MT940 al dovezii C121: contul RO66BACX0000001234567890, nu al firmei (încasare mică, de probă)."""
    zi = _dt.date.fromisoformat(zi_iso)
    d = zi.strftime("%y%m%d")
    return (":20:PROBAC121\n:25:RO66BACX0000001234567890\n:28C:00010/001\n:60F:C%sRON1000,00\n:61:%s%sC1,21NTRFNONREF\n"
            ":86:Proba C121 incasare\n:62F:C%sRON1001,21\n" % (d, d, zi.strftime("%m%d"), d)).encode("utf-8")


def fisier_xml_c104():
    """Fișierul e-Factura de probă (DANTE -> F1, 20 H87 / 50 MTR / 12,5 KGM / 1 C62), cu numărul PROBA-C104 (nu se lovește de DNT-RT-1020)."""
    return io.open(PROBA_XML, encoding="utf-8").read().replace("DNT-RT-1020", "PROBA-C104").encode("utf-8")


def fisier_xml_c120():
    """Același fișier, cu numărul PROBA-C120: încărcat la o ALTĂ firmă decât F1 e o factură între alte două firme."""
    return io.open(PROBA_XML, encoding="utf-8").read().replace("DNT-RT-1020", "PROBA-C120").encode("utf-8")
