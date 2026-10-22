# -*- coding: utf-8 -*-
"""Lotul 11, comanda Costin 11.1 (verbatim în DECIZII „Comanda 11.1”), subagentul T: 428 (PRIORITAR) — TVA la încasare pe PAȘII REALI ai
contabilului — și C76 (PRIORITAR) — lipsa de la inventar ajunge în D300.

DE CE UN TEST NOU LA 428. Retestul lui Costin pe producție (21.10.2026, F6 Migrare Test SRL): „firma în TVA la încasare emite factura pe
4427, fără mențiunea obligatorie, iar Configurare emitere nu arată sistemul”. Pe producție, perioada scrisă în Date firmă la 17:46 era „de la
01.11.2026” (opțiunea exercitată în octombrie se aplică de la prima zi a perioadei fiscale următoare, CF art.282 alin.(3^1) lit.a), iar
factura F6 nr. 1 era din 21.10.2026 — deci, corect, pe regulile generale (CF art.282 alin.(7) lit.a): 4427, fără mențiune. Niciun ecran
nu spunea asta: „Configurare emitere” arăta sistemul numai dacă se aplica AZI, formularul nu spunea nimic. Testele lotului 10 (verzi în
plasă) scriau perioada direct în bază, de la începutul lunii curente, și emiteau pe API — n-au trecut niciodată prin Date firmă -> Emite
factură (formularul) -> Configurare emitere, deci nici prin cazul „factura de azi, sistemul de luna viitoare”.

Aici, totul pe ecran: perioada din Date firmă, factura din formularul „Emite factură”, încasarea din Casă, validarea notelor pe ruta
butonului „Validează”, declarațiile din Declarații (XML-ul de la pasul 2). Datele de PORNIRE scrise pe rutele ecranelor, nu în bază:
Date firmă + vectorul fiscal + produsul din nomenclator (`pregateste_firma` / `_profil_fara_numerotare`). Nimic nu se inserează direct.
Clientul: CUI 18547290 — cifra de control verificată cu algoritmul din CLAUDE.md."""
import base64
import datetime as _dt
import io
import re

import pytest

from conftest import firma_noua, perioada_incheiata, sql
from e2e_bloc_a import AZI, PRODUS, _api, _card, _deschide_emiterea, _ok, _profil, pregateste_firma

LUNA = perioada_incheiata("lunar")          # D300 / D394 se generează numai pe o perioadă încheiată (383)
ZI = LUNA.inceput.replace(day=10)           # data facturii și a încasării, în luna încheiată
CLIENT = {"#em-cui": "18547290", "#em-nume": "Client Incasare Lot11 SRL", "#em-adresa": "Str. Probei 1", "#em-oras": "Sector 1"}


@pytest.fixture()
def firma_t():
    for f in firma_noua():
        yield f


def _pdf_text(e, cale):
    import pypdf
    b64 = e.pg.evaluate("""async (c) => { const t = sessionStorage.getItem('iconta_token');
        const x = await fetch(c, {headers: {Authorization: 'Bearer ' + t}}); const b = new Uint8Array(await x.arrayBuffer());
        let s = ''; b.forEach((v) => { s += String.fromCharCode(v); }); return btoa(s); }""", cale)
    return "".join(p.extract_text() for p in pypdf.PdfReader(io.BytesIO(base64.b64decode(b64))).pages)


def _note_factura(schema, fid):
    return sql('SELECT l.cont_debit, l.cont_credit, l.suma::text FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l '
               "ON l.inregistrare_id = i.id WHERE i.factura_id = %%s ORDER BY i.id, l.id" % (schema, schema), (fid,))


def _regimul_din_date_firma(e, firma, de_la):
    """Date firmă -> Vector fiscal -> „Aplică sistemul TVA la încasare”: Da, „de la” -> Salvează (ca omul: după ce butonul e activ)."""
    pg = e.pg
    e.firma(firma["nume"])
    _card(e, "datefirma", "#df-salveaza")
    pg.select_option("#vf-tva_incasare", "da")
    pg.fill("#vf-tva_incasare_de_la", de_la.isoformat())
    pg.wait_for_selector("#df-salveaza:not([disabled])", timeout=30000)
    pg.evaluate("() => { const m = document.querySelector('#df-msg'); if (m) m.innerHTML = ''; }")
    pg.click("#df-salveaza")
    # mesajul de salvare: „Datele firmei au fost salvate.” sau, cu un câmp obligatoriu lipsă, „Salvat. Lipsește …” (`date_firma._mesajSalvat`)
    pg.wait_for_function("() => /salvat/i.test((document.querySelector('#df-msg') || {innerText: ''}).innerText)", timeout=30000)
    e.captura("regimul_din_date_firma")
    # aplicația a scris perioada (drumul ecranului: `POST tva-incasare` -> `regim_tva_incasare.salveaza`)
    assert sql('SELECT de_la::text, pana_la, sursa FROM "%s".tva_incasare_perioade' % firma["schema"]) == [(de_la.isoformat(), None, "manual")]


def _completeaza_factura(pg, data, pret="1000"):
    pg.fill("#em-data", data.isoformat())
    pg.dispatch_event("#em-data", "change")
    for sel, v in CLIENT.items():
        pg.fill(sel, v)
    pg.select_option("#em-judet", "B")
    pg.fill("#em-l0-descriere", PRODUS)
    pg.wait_for_function("() => document.querySelector('#em-l0-pret_unitar').value !== ''", timeout=20000)
    pg.fill("#em-l0-cantitate", "1")
    pg.fill("#em-l0-pret_unitar", pret)
    pg.wait_for_function("() => document.querySelector('#em-l0-cota').value === '21'", timeout=20000)


def _emite_din_formular(e, firma):
    pg = e.pg
    peste = sql('SELECT COALESCE(max(id), 0) FROM "%s".facturi' % firma["schema"])[0][0]
    pg.click("#em-emite")
    pg.wait_for_selector("#em-rezultat.em-emisa", timeout=60000)
    fid = sql('SELECT id FROM "%s".facturi WHERE id > %%s AND directie = \'emisa\' ORDER BY id' % firma["schema"], (peste,))
    assert len(fid) == 1, fid
    return fid[0][0], " ".join(pg.inner_text("#em-rezultat").split())


def _valideaza(e, firma, ids):
    """„Validează” pe fiecare notă (ruta butonului din Registrul jurnal)."""
    for nid in ids:
        _ok(_api(e, "POST", "/tenants/%d/jurnal/%d/valideaza" % (firma["tenant_id"], nid), {}), "validarea notei %s" % nid)


def _xml_declaratiei(e, firma, tip):
    """Declarații -> tipul -> luna încheiată -> „Continuă” -> pasul 2: XML-ul arătat de ecran."""
    from e2e_bloc_d import _genereaza
    _genereaza(e, firma, tip, LUNA.an, LUNA.luna)
    pg = e.pg
    e.captura("pas2_" + tip)
    assert not pg.locator(".fereastra:last-of-type .dec-eroare").count(), e.fereastra()[:3000]
    return pg.eval_on_selector(".fereastra:last-of-type details.dec-xml pre.dec-xml-pre", "el => el.textContent")


def _atr(xml, nume):
    m = re.search(r'\b%s="([^"]*)"' % nume, xml)
    return m.group(1) if m else None


# ── 428 — pe drumul contabilului: Date firmă -> Emite factură -> Casă -> Validează -> D300 / D394 ─────────────────────────────────────────
def test_def_428_tva_la_incasare_pe_pasii_contabilului(patron, firma_t):
    """428 (PRIORITAR). Pașii: Date firmă -> „Aplică sistemul TVA la încasare”: Da, de la <prima zi a lunii încheiate> -> Salvează ->
    Facturi -> „Emite factură”: data în luna încheiată; caseta de lângă dată spune „firma aplică sistemul TVA la încasare … 4428 …”; client
    român, 1 × 1.000 lei, 21% -> „Emite factură”: mesajul spune „TVA la încasare: TVA-ul e pe 4428”; nota facturii 4111 = 4428 210,00; PDF-ul
    poartă „TVA la încasare” (CF art.319 alin.(20) lit.p) -> Casă -> încasare de la client 605 lei, factura bifată -> nota: 5311 = 4111 605
    și 4428 = 4427 105 (CF art.282 alin.(8)) -> „Validează” pe note -> Declarații -> D300 pe luna încheiată: rândul 9 bază 500, TVA 105
    (partea încasată, nu 1.000 / 210 — CF art.282 alin.(3)) -> D394: sistemTVA="1", tvaCol21="105"."""
    s, tid = firma_t["schema"], firma_t["tenant_id"]
    pregateste_firma(patron, firma_t, platitor=True, regim_fiscal="profit")
    _regimul_din_date_firma(patron, firma_t, LUNA.inceput)
    pg = patron.pg
    _deschide_emiterea(patron, firma_t["nume"])
    _completeaza_factura(pg, ZI)
    pg.wait_for_function("() => { const z = document.querySelector('#em-tva-incasare'); return z && !z.hidden && "
                         "z.innerText.includes('firma aplică sistemul TVA la încasare') && z.innerText.includes('4428'); }", timeout=20000)
    patron.captura("formular_in_sistem")
    fid, rez = _emite_din_formular(patron, firma_t)
    patron.captura("emisa")
    assert "TVA la încasare: TVA-ul e pe 4428" in rez, rez
    # CF art.282 alin.(3): TVA-ul facturii emise în sistem e neexigibil până la încasare -> 4428
    note = _note_factura(s, fid)
    assert ("4111", "4428", "210.00") in note and not [n for n in note if n[1] == "4427"], note
    # CF art.319 alin.(20) lit.p): „în cazul în care exigibilitatea TVA intervine la data încasării [...], mențiunea «TVA la încasare»”
    assert "TVA la încasare" in _pdf_text(patron, "/tenants/%d/facturi/%d/pdf" % (tid, fid))
    # Casă -> încasarea parțială, legată de factură
    patron.firma(firma_t["nume"])
    pg.click("#fa-casa")
    pg.wait_for_selector("#c-toggle", timeout=20000)
    pg.click("#c-toggle")
    pg.fill("#c-data", ZI.isoformat())
    pg.select_option("#c-cat", "incasare_client")
    pg.fill("#c-suma", "605")
    pg.fill("#c-cui", CLIENT["#em-cui"])
    pg.dispatch_event("#c-campuri", "change")
    pg.wait_for_selector("#c-facturi [data-cf='%d']" % fid, timeout=20000)
    pg.check("#c-facturi [data-cf='%d']" % fid)
    pg.click("#c-adauga")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('605,00')", timeout=20000)
    patron.captura("incasarea")
    # CF art.282 alin.(8): „fiecare încasare totală sau parțială se consideră că include și taxa aferentă” — din 605, 105 devine exigibil
    note = _note_factura(s, fid)
    assert ("5311", "4111", "605.00") in note and ("4428", "4427", "105.00") in note, note
    _valideaza(patron, firma_t, [r[0] for r in sql('SELECT id FROM "%s".inregistrari WHERE factura_id = %%s ORDER BY id' % s, (fid,))])
    xml = _xml_declaratiei(patron, firma_t, "d300")
    # CF art.282 alin.(3): exigibilă e numai partea încasată în perioadă — rândul 9 (21%): bază 500, TVA 105
    assert (_atr(xml, "R9_1"), _atr(xml, "R9_2")) == ("500", "105"), xml[:3000]
    xml394 = _xml_declaratiei(patron, firma_t, "d394")
    # OPANAF 2194/2025 (D394) pct.5.1: „TVA colectată aferentă facturilor încasate în perioada de raportare”, la sistemTVA = 1
    assert (_atr(xml394, "sistemTVA"), _atr(xml394, "tvaCol21")) == ("1", "105"), xml394[:3000]


# ── 428 — cazul de pe producție: sistemul de luna viitoare, factura de azi, „Configurare emitere” ─────────────────────────────────────────
def test_def_428_configurare_emitere_arata_sistemul_si_factura_dinainte_de_intrare(patron, firma_t):
    """428, cazul F6 de pe producție (21.10.2026). Pașii: Date firmă -> „Aplică sistemul TVA la încasare”: Da, de la <prima zi a lunii
    viitoare> (opțiunea exercitată luna asta, CF art.282 alin.(3^1) lit.a) -> Salvează -> Facturi -> „Emite factură” (numerotarea
    neconfigurată): „Configurare emitere” arată „TVA la încasare de la 01.LL.AAAA — azi nu se aplică” -> „Nu, încep acum”, seria ->
    formularul: caseta de lângă dată spune „abia de la 01.LL.AAAA … regulile generale … 4427 … art. 282 alin. (7) lit. a)” -> factura de azi
    1.000 + 21% -> mesajul nu spune „TVA la încasare”; nota 4111 = 4427 210,00 (nimic pe 4428); PDF-ul fără mențiune."""
    s, tid = firma_t["schema"], firma_t["tenant_id"]
    luna_viitoare = (AZI.replace(day=28) + _dt.timedelta(days=4)).replace(day=1)
    # pornirea, pe rutele ecranelor: Date firmă, vectorul (plătitor lunar), produsul — fără numerotare (ca F6: „Configurare emitere” apare)
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % tid, _profil(firma_t)), "Date firmă")
    _ok(_api(patron, "POST", "/tenants/%d/vector" % tid, {"regim_fiscal": "profit", "platitor_tva": True, "tip_decont": "lunar",
                                                         "operatiuni_ic": False, "inreg_art317": False, "tva_data_inceput": "2026-01-01"}),
        "vector fiscal")
    _ok(_api(patron, "POST", "/tenants/%d/produse" % tid, {"denumire": PRODUS, "um": "ora", "pret_unitar": 150.0, "cota_tva": 21,
                                                          "confirmat": True}), "produs")
    _regimul_din_date_firma(patron, firma_t, luna_viitoare)
    pg = patron.pg
    patron.firma(firma_t["nume"])
    _card(patron, "facturi", "#fac-emite")
    pg.click("#fac-emite")
    pg.wait_for_selector("#em-config-regim", timeout=25000)
    patron.captura("configurare_emitere")
    regim = " ".join(pg.inner_text("#em-config-regim").split())
    assert "TVA la încasare de la %s" % luna_viitoare.strftime("%d.%m.%Y") in regim and "azi nu se aplică" in regim, regim
    pg.click("#em-nu")
    pg.fill("#em-serie2", "T428-")
    pg.click("#em-salveaza-config2")
    pg.wait_for_selector("#em-cui", timeout=25000)
    _completeaza_factura(pg, AZI)
    pg.wait_for_function("() => { const z = document.querySelector('#em-tva-incasare'); return z && !z.hidden && "
                         "z.innerText.includes('abia de la'); }", timeout=20000)
    caseta = " ".join(pg.inner_text("#em-tva-incasare").split())
    patron.captura("formular_inainte_de_intrare")
    # CF art.282 alin.(7) lit.a): factura emisă înainte de intrarea în sistem rămâne pe regulile generale
    assert ("abia de la %s" % luna_viitoare.strftime("%d.%m.%Y")) in caseta and "4427" in caseta and "alin. (7) lit. a)" in caseta, caseta
    fid, rez = _emite_din_formular(patron, firma_t)
    patron.captura("emisa")
    assert "TVA la încasare" not in rez, rez
    note = _note_factura(s, fid)
    assert ("4111", "4427", "210.00") in note and not [n for n in note if "4428" in n[:2]], note
    assert "TVA la încasare" not in _pdf_text(patron, "/tenants/%d/facturi/%d/pdf" % (tid, fid))


# ── C76 — lipsa neimputabilă de la inventar ajunge în D300 (rd.34) ─────────────────────────────────────────────────────────────────────────
def test_def_c76_lipsa_la_inventar_ajunge_in_d300(patron, firma_t):
    """C76 (PRIORITAR; comanda 11.1 pct.3: „lipsa de la inventar trebuie să ajungă în D300”). Pașii: marfă în stoc (10 buc × 20 lei,
    intrată la începutul lunii încheiate) -> Stocuri -> „Mișcări, fișe…” -> Inventar la data <ziua 20 a lunii încheiate>: faptic 0 ->
    „neimputabilă” -> „Salvează inventarul”: nota 607 = 371 200,00 și 635 = 4427 42,00 (HG 1/2016 titlul VII pct.78 alin.(6) lit.a) ->
    „Validează” pe notele lunii -> Declarații -> D300 pe luna încheiată: rândul 34 (XML R31_2) = -42 (OPANAF 174/2026 rd.34, ajustarea
    negativă a taxei deductibile „cu semnul plus sau minus”), iar pasul 2 spune din ce notă vine. Înainte: D300 ieșea identic cu cel de
    dinainte de inventar (recalculul pornea numai din facturi).
    Pornirea: articolul intră pe ruta ecranului „Mișcări” (`POST stocuri/intrare`), cu data din luna încheiată."""
    from e2e_bloc_a import ARTICOL
    s, tid = firma_t["schema"], firma_t["tenant_id"]
    pregateste_firma(patron, firma_t, platitor=True, regim_fiscal="profit")
    aid = _ok(_api(patron, "POST", "/tenants/%d/stocuri/intrare" % tid, {"denumire": ARTICOL, "um": "buc", "data": LUNA.inceput.isoformat(),
                                                                       "cantitate": 10, "pret_unitar": 20, "document": "NIR C76 1"}),
              "intrare")["articol_id"]
    patron.firma(firma_t["nume"])
    _card(patron, "stocuri", "#cv-toggle")
    pg = patron.pg
    pg.click("#cv-toggle")
    pg.wait_for_selector("#cv-inv", timeout=20000)
    pg.fill("#cv-data", LUNA.inceput.replace(day=20).isoformat())
    pg.click("#cv-inv")
    pg.fill("#cvi-a%d-faptic" % aid, "0")
    pg.wait_for_selector("#cvi-a%d-lipsa" % aid, state="visible", timeout=5000)
    pg.select_option("#cvi-a%d-lipsa" % aid, "neimputabila")
    pg.click("#cvi-salveaza")
    pg.wait_for_function("() => document.body.innerText.includes('Inventarul din')", timeout=30000)
    patron.captura("inventar")
    linii = sql('SELECT l.cont_debit, l.cont_credit, l.suma::text FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l '
                "ON l.inregistrare_id = i.id WHERE i.data = %%s ORDER BY l.id" % (s, s), (LUNA.inceput.replace(day=20),))
    # HG 1/2016 titlul VII pct.78 alin.(6) lit.a): ajustarea negativă a TVA-ului dedus pentru bunurile lipsă (21% din 200,00)
    assert ("635", "4427", "42.00") in linii, linii
    _valideaza(patron, firma_t, [r[0] for r in sql('SELECT id FROM "%s".inregistrari WHERE status <> \'validata\' AND data >= %%s '
                                                   'AND data <= %%s ORDER BY id' % s, (LUNA.inceput, LUNA.sfarsit))])
    xml = _xml_declaratiei(patron, firma_t, "d300")
    # OPANAF 174/2026 rd.34 (XML R31): „diferenţele de taxă [...] rezultate ca urmare a ajustării taxei deductibile, cu semnul plus sau minus”
    assert _atr(xml, "R31_2") == "-42", xml[:3000]
    pas2 = " ".join(patron.fereastra().split())
    assert "Rândul 34 (ajustări de taxă) cuprinde -42 lei" in pas2 and "635 = 4427 42,00" in pas2, pas2[:3000]
