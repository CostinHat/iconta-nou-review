# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.2 (verbatim în `~/ghid_incoming/comanda_12_2.txt`), pachetul `cx7` — testele de capăt la capăt care lipseau
pentru deficiențele găsite de Code în 12.2 și deja reparate în cod (DEFICIENTE.md C176–C186):

  C176 Registrul de evidență fiscală: „Șterge” la o ajustare fiscală nu făcea nimic -> acum întreabă și șterge.
  C179 Datele aduse de la ANAF pentru un CUI rămâneau după schimbarea CUI-ului: NIR, casă, Emite factură, factura primită introdusă de
       mână, înregistrarea cabinetului din invitație.
  C180 După o acțiune pe rând, fereastra trecea prin „Se încarcă…” și sărea sus (Centre de cost, „Dezactivează” pe al 41-lea centru).
  C181 Seria lipită de număr („Factura F1A3”) în facturile candidate ale chitanței pozate și în fișa partenerului.
  C182 „De validat”: „Validează” pe o notă fără document deschidea detaliul fără liniile notei, iar la redesenare detaliul se închidea.
  C183 „De validat”: detaliul notei scria „Rulaj: rulaj 100,00 lei”.
  C184 „De validat” deschis din notificare marca rândul fără să-i deschidă detaliul.
  C185 Registrul jurnal: confirmarea salvării spunea „(ciornă)” și când nota asistentei plecase la validare în cabinet.
  C186 Emite factură: refuzul cu erori numai pe câmpuri apărea și în caseta „NU s-a salvat.”, și în fereastra „Am înțeles”.

C177 (contorul situației stocului comun ferestrelor) NU are test aici: defectul cere două ferestre Stocuri vii deodată, cu o cerere a
primeia încă în zbor; navigatorul ține în pagină numai fereastra de sus, iar Stocuri se deschide numai din fereastra firmei
(`firme.js`, `#fa-stocuri`) — contabilul nu ajunge prin clicuri la două ferestre Stocuri vii. Îl apără testul din Chromium
`core/test_lot12_ui2_ecrane.py::test_628_doua_ferestre_stocuri_nu_isi_anuleaza_lista`.

Pașii contabilului pe aplicația din index, pe baza de TEST, pe firma nouă a fișierului (`firma_e2e`). DATE DE PORNIRE: toate pe drumul
aplicației — ajustarea fiscală, centrele de cost, factura primită și factura emisă pe rutele ecranelor (`POST ajustari-fiscale`,
`POST centre-cost`, `POST facturi-primite/manual`, `POST facturi/emite`); notele asistentei din ecranul ei (`e2e_bloc_b._nota_prin_ecran`);
chitanța pozată citită de modelul simulat al plasei (`ai_pregateste`); răspunsul ANAF pentru 14399840 (DANTE INTERNATIONAL SA) e cel din
baza simulatorului (`frontend_test/e2e/anaf_baza.json`, răspunsul real capturat); CUI-ul 14399840 are cifra de control verificată
(`e2e_lot12_fact2`). Nicio scriere SQL; `sql()` numai citește.

Aserțiunile compară mesaje întregi, celule de tabel, valori de câmp și starea elementelor (deschis / ascuns / prezent), nu sub-șiruri.
MUTAȚIILE: `frontend_test/e2e/mut_lot12_cx7.json`, câte una (sau una pe drum, la C179) pe test.

Temei: CF art.319 alin.(20) lit.a — „numărul de ordine, în baza uneia sau a mai multor serii, care identifică factura în mod unic” (C181:
seria și numărul sunt două elemente ale facturii; text citit în `anaf_surse/cod_fiscal_227_2015_consolidat.html`). Restul: N/A — reguli de
interfață (CLAUDE.md §9: „Nimic precompletat sau afișat care poate induce în eroare contabilul”; DS cap.9 „După o acțiune pe un rând”,
„Tabelul de note”; DS cap.5 întrebarea de confirmare; DS cap.6 un mesaj, o singură dată)."""
import json

import pytest
import time as _t

from conftest import BAZA, Ecran, ai_pregateste, firma_noua, sql
from e2e_bloc_a import AZI, _api, _card, _deschide_emiterea, _ok, emite_api, pregateste_firma
from e2e_bloc_b import _card_nota, _coada_nota, _de_validat, _nota_prin_ecran, ana, ana_cont  # noqa: F401 — fixture (ana, ana_cont)
from e2e_bloc_c import pregateste_cv   # C186: firma cu articolul de stoc
from e2e_lot12_cx1 import JPEG
from e2e_lot12_form2 import invitatie_642  # noqa: F401 — fixtură (C179, înregistrarea din invitație)

LUNA = (AZI.year, AZI.month)
DANTE, DANTE_NUME = "14399840", "DANTE INTERNATIONAL SA"
CUI_ALTUL = "1439984"            # CUI-ul tastat greșit (o cifră scoasă): ANAF n-a adus nimic pentru el
_CORP = "() => [...document.querySelectorAll('.fereastra-corp')].pop()"


def _tag():
    return int(_t.time() * 1000) % 1000000


def _val(pg, sel):
    return pg.input_value(sel)


# ── C176 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c176_stergerea_ajustarii_fiscale_intreaba_si_sterge(patron, firma_e2e):
    """C176. Pașii: o ajustare fiscală pe anul în curs (amenzi, T1, 100 lei) -> Registrul de evidență fiscală, anul în curs -> „Șterge” pe
    rândul ei: întrebarea „Ștergi ajustarea? D100 și D101 se calculează din nou fără ea.”, cu „Da, șterge ajustarea” / „Păstrează” ->
    „Da, șterge ajustarea”: rândul dispare, iar ajustarea nu mai e în listă. ROȘU înainte: clicul nu arăta nimic și nu ștergea nimic.
    MUTAȚIA: forma veche (`await confirmaCaseta("Ștergi…", {…})`, textul în locul zonei) -> întrebarea nu apare -> ROȘU."""
    tid, an = firma_e2e["tenant_id"], AZI.year
    d = _ok(_api(patron, "GET", "/tenants/%d/ajustari-fiscale?an=%d" % (tid, an)), "ajustări")
    anuale = set(d.get("anuale") or [])
    rand = next(r["rand"] for r in d["randuri"] if r["rand"] not in anuale)
    desc = "Ajustare E2E C176 %d" % _tag()
    _ok(_api(patron, "POST", "/tenants/%d/ajustari-fiscale" % tid,
             {"an": an, "rand": rand, "trim": 1, "suma": "100.00", "descriere": desc, "document": "PV E2E C176"}), "ajustarea")
    aid = next(a["id"] for a in _ok(_api(patron, "GET", "/tenants/%d/ajustari-fiscale?an=%d" % (tid, an)), "ajustări")["ajustari"]
               if a["descriere"] == desc)
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    _card(patron, "regfiscal", "#rf-var")
    pg.fill("#rf-an", str(an))
    pg.dispatch_event("#rf-an", "change")
    pg.wait_for_selector("[data-aj-sterge='%d']" % aid, timeout=30000)
    pg.click("[data-aj-sterge='%d']" % aid)
    pg.wait_for_selector("#caseta-atentie-activa .caseta-intrebare #ca-ok", timeout=10000)
    intrebare = " ".join(pg.inner_text("#caseta-atentie-activa .ca-mesaj").split())
    butoane = [pg.inner_text("#caseta-atentie-activa #ca-ok").strip(), pg.inner_text("#caseta-atentie-activa #ca-nu").strip()]
    patron.captura("intrebarea")
    assert intrebare == "Ștergi ajustarea? D100 și D101 se calculează din nou fără ea.", intrebare
    assert butoane == ["Da, șterge ajustarea", "Păstrează"], butoane
    pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_selector("[data-aj-sterge='%d']" % aid, state="detached", timeout=30000)
    patron.captura("dupa_stergere")
    ramase = [a["id"] for a in _ok(_api(patron, "GET", "/tenants/%d/ajustari-fiscale?an=%d" % (tid, an)), "ajustări")["ajustari"]]
    assert aid not in ramase, ramase


# ── C179 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c179_nir_denumirea_furnizorului_de_la_anaf_dispare_la_alt_cui(patron, firma_e2e):
    """C179 (NIR). Pașii: Stocuri -> „+ NIR nou” -> CUI 14399840 -> „Verifică”: furnizorul = DANTE INTERNATIONAL SA, sub CUI „DANTE
    INTERNATIONAL SA · plătitor TVA” -> CUI-ul schimbat (1439984): furnizorul și linia de sub CUI se golesc -> 14399840 din nou, „Verifică”,
    furnizorul corectat de om -> alt CUI: ce a scris omul rămâne. Nimic nu se salvează.
    MUTAȚIA: `legaDateAnaf` legat de alt câmp decât `#sn-cui` -> denumirea DANTE rămâne lângă CUI-ul nou -> ROȘU."""
    pregateste_firma(patron, firma_e2e)
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    _card(patron, "stocuri", "#sn-toggle")
    pg.click("#sn-toggle")
    pg.wait_for_selector("#sn-cui", state="visible", timeout=10000)
    pg.fill("#sn-cui", DANTE)
    pg.click("#sn-verifica")
    pg.wait_for_function("(d) => document.querySelector('#sn-furn').value === d", arg=DANTE_NUME, timeout=30000)
    stare = " ".join(pg.inner_text("#sn-cui-stare").split())
    patron.captura("denumirea_de_la_anaf")
    pg.fill("#sn-cui", CUI_ALTUL)
    dupa = (_val(pg, "#sn-furn"), pg.inner_text("#sn-cui-stare").strip())
    patron.captura("cui_schimbat")
    pg.fill("#sn-cui", DANTE)
    pg.click("#sn-verifica")
    pg.wait_for_function("(d) => document.querySelector('#sn-furn').value === d", arg=DANTE_NUME, timeout=30000)
    pg.fill("#sn-furn", DANTE_NUME + " — punct de lucru")
    pg.fill("#sn-cui", "18547290")
    om = _val(pg, "#sn-furn")
    assert stare.startswith(DANTE_NUME + " · plătitor TVA"), stare
    assert dupa == ("", ""), dupa                                   # datele CUI-ului vechi nu rămân lângă CUI-ul nou
    assert om == DANTE_NUME + " — punct de lucru", om               # F188: ce a scris omul rămâne


def test_def_c179_casa_partenerul_de_la_anaf_dispare_la_alt_cui(patron, firma_e2e):
    """C179 (casă). Pașii: Casă -> „+ Dispoziție nouă” -> CUI 14399840 -> „Verifică”: partenerul = DANTE INTERNATIONAL SA, sub CUI
    „plătitor TVA” -> CUI-ul schimbat (1439984): partenerul și linia de sub CUI se golesc. Nimic nu se salvează.
    MUTAȚIA: `legaDateAnaf` legat de alt câmp decât `#c-cui` -> partenerul DANTE rămâne -> ROȘU."""
    pregateste_firma(patron, firma_e2e)
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    _card(patron, "casa", "#c-toggle")
    pg.click("#c-toggle")
    pg.wait_for_selector("#c-cui", state="visible", timeout=10000)
    pg.fill("#c-cui", DANTE)
    pg.click("#c-cui-verif")
    pg.wait_for_function("(d) => document.querySelector('#c-part').value === d", arg=DANTE_NUME, timeout=30000)
    stare = pg.inner_text("#c-cui-stare .em-cui-info").strip()
    patron.captura("partenerul_de_la_anaf")
    pg.fill("#c-cui", CUI_ALTUL)
    dupa = (_val(pg, "#c-part"), pg.inner_text("#c-cui-stare").strip())
    patron.captura("cui_schimbat")
    assert stare == "plătitor TVA", stare
    assert dupa == ("", ""), dupa


def test_def_c179_emiterea_datele_clientului_de_la_anaf_dispar_la_alt_cui(patron, firma_e2e):
    """C179 (Emite factură). Pașii: Emite factură -> CUI 14399840 -> „Verifică”: denumirea, adresa, localitatea și județul clientului de la
    ANAF -> CUI-ul schimbat (1439984), tastat: toate patru se golesc, iar linia de sub CUI la fel. Factura nu se emite.
    MUTAȚIA: `legaDateAnaf` legat de alt câmp decât `#em-cui` -> denumirea DANTE rămâne -> ROȘU."""
    pregateste_firma(patron, firma_e2e)
    pg = patron.pg
    _deschide_emiterea(patron, firma_e2e["nume"])
    campuri = ("#em-nume", "#em-adresa", "#em-oras", "#em-judet")
    pg.fill("#em-cui", DANTE)
    pg.click("#em-verifica")
    pg.wait_for_function("(d) => document.querySelector('#em-nume').value === d", arg=DANTE_NUME, timeout=30000)
    dupa_verifica = [_val(pg, s) for s in campuri]
    patron.captura("clientul_de_la_anaf")
    pg.fill("#em-cui", CUI_ALTUL)
    dupa_schimbare = [_val(pg, s) for s in campuri]
    stare_dupa = pg.inner_text("#em-cui-stare").strip()
    patron.captura("cui_schimbat")
    assert dupa_verifica[0] == DANTE_NUME and all(dupa_verifica), dupa_verifica   # ANAF a completat toate patru
    assert dupa_schimbare == ["", "", "", ""], dupa_schimbare
    assert stare_dupa == "", stare_dupa


def test_def_c179_factura_primita_furnizorul_de_la_anaf_dispare_la_alt_cui(patron, firma_e2e):
    """C179 (factura primită introdusă de mână). Pașii: Facturi -> „Facturi primite” -> „Introdu factura de mână” -> CUI 14399840 ->
    „Verifică la ANAF”: furnizorul = DANTE INTERNATIONAL SA, sub CUI „DANTE INTERNATIONAL SA · plătitor TVA” -> CUI-ul schimbat (1439984):
    furnizorul și linia de sub CUI se golesc. Nimic nu se validează.
    MUTAȚIA: `legaDateAnaf` legat de alt câmp decât `#pm-cui` -> furnizorul DANTE rămâne -> ROȘU."""
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    _card(patron, "facturi", "#fac-primite")
    pg.click("#fac-primite")
    pg.wait_for_selector("#fp-manual", timeout=25000)
    pg.click("#fp-manual")
    pg.wait_for_selector("#pm-cui", timeout=20000)
    pg.fill("#pm-cui", DANTE)
    pg.click("#pm-verifica")
    pg.wait_for_function("(d) => document.querySelector('#pm-furnizor').value === d", arg=DANTE_NUME, timeout=30000)
    stare = " ".join(pg.inner_text("#pm-cui-stare").split())
    patron.captura("furnizorul_de_la_anaf")
    pg.fill("#pm-cui", CUI_ALTUL)
    dupa = (_val(pg, "#pm-furnizor"), pg.inner_text("#pm-cui-stare").strip())
    patron.captura("cui_schimbat")
    assert stare.startswith(DANTE_NUME + " · plătitor TVA"), stare
    assert dupa == ("", ""), dupa


def test_def_c179_inregistrarea_denumirea_cabinetului_dispare_la_alt_cui(browser, request, invitatie_642):  # noqa: F811
    """C179 (înregistrarea din invitație). Pașii vizitatorului: linkul invitației -> „Continuă” -> CUI 14399840 -> „Verifică la ANAF”:
    denumirea cabinetului = DANTE INTERNATIONAL SA, sub CUI „Găsit: DANTE INTERNATIONAL SA…” -> CUI-ul schimbat (1439984): denumirea și
    linia de sub CUI se golesc. Niciun cont nu se creează (fixtura o verifică).
    MUTAȚIA: `legaDateAnaf` legat de alt câmp decât `#reg-cui` -> denumirea DANTE rămâne -> ROȘU."""
    _email, tok = invitatie_642
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    e = Ecran(ctx.new_page(), request.node.name)
    try:
        vp = e.pg
        vp.goto(BAZA + "/#invitatie=" + tok, wait_until="domcontentloaded")
        vp.wait_for_selector("#pr-continua", timeout=20000)
        vp.click("#pr-continua")
        vp.wait_for_selector("#reg-cui", timeout=10000)
        vp.fill("#reg-cui", DANTE)
        vp.click("#reg-cui-verifica")
        vp.wait_for_function("(d) => document.querySelector('#reg-cabinet').value === d", arg=DANTE_NUME, timeout=30000)
        info = " ".join(vp.inner_text("#reg-cui-info").split())
        e.captura("denumirea_de_la_anaf")
        vp.fill("#reg-cui", CUI_ALTUL)
        dupa = (vp.input_value("#reg-cabinet"), vp.inner_text("#reg-cui-info").strip())
        e.captura("cui_schimbat")
        assert info.startswith("Găsit: " + DANTE_NUME), info
        assert dupa == ("", ""), dupa
        assert not e.erori and not e.cereri_rele, (e.erori, e.cereri_rele)
    finally:
        ctx.close()


# ── C180 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c180_dupa_dezactivarea_unui_centru_fereastra_ramane_unde_era(patron, firma_e2e):
    """C180. Pașii: 60 de centre de cost -> Centre de cost: fereastra derulată la al 41-lea centru -> „Dezactivează” pe rândul lui: lista
    trece prin „Se încarcă…” și revine cu fereastra unde era (± 60 px: titlul pus de navigator cât se încarcă), iar rândul spune „Reactivează”. ROȘU înainte: fereastra ajungea sus
    (derularea 0). MUTAȚIA: navigatorul nu mai pune derularea la loc -> fereastra sus -> ROȘU."""
    tid = firma_e2e["tenant_id"]
    tag = _tag()
    for i in range(60):
        _ok(_api(patron, "POST", "/tenants/%d/centre-cost" % tid, {"nume": "Centru E2E C180 %d-%02d" % (tag, i)}), "centrul %d" % i)
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    _card(patron, "centrecost", "[data-toggle]")
    pg.wait_for_timeout(400)
    cid = pg.evaluate("() => [...(%s)().querySelectorAll('[data-toggle]')][40].dataset.toggle" % _CORP)
    sel = "[data-toggle='%s']" % cid
    inainte = pg.evaluate("""(s) => { const c = (%s)(), r = c.querySelector(s);
      c.scrollTop += r.getBoundingClientRect().top - c.getBoundingClientRect().top - c.clientHeight / 2; return c.scrollTop; }""" % _CORP, sel)
    assert inainte > 300, inainte                                   # premisa: fereastra chiar e derulată departe de sus
    pg.click(sel)
    pg.wait_for_function("(s) => { const b = document.querySelector(s); return !!b && b.textContent.trim() === 'Reactivează'; }",
                         arg=sel, timeout=30000)
    pg.wait_for_timeout(300)
    dupa = pg.evaluate("() => (%s)().scrollTop" % _CORP)
    patron.captura("dupa_dezactivare")
    assert abs(dupa - inainte) <= 60, (inainte, dupa)               # „fereastra sare sus” -> rămâne pe loc
    centre = _ok(_api(patron, "GET", "/tenants/%d/centre-cost" % tid), "centrele")["centre"]
    assert [c["activ"] for c in centre if str(c["id"]) == cid] == [False], cid


# ── C181 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c181_facturile_candidate_ale_chitantei_au_seria_separat(patron, firma_e2e):
    """C181 (Casă / bonuri). Pașii: factura primită de la DANTE, seria F1A, numărul <n>, 100 lei + 21% (introdusă de mână) -> „Bonuri și
    chitanțe” -> „Adaugă document”: chitanța DANTE de 121,00 lei (citită de model) -> deschisă: în „Ce plătește chitanța?” factura e
    „Factura F1A nr. <n> · DANTE INTERNATIONAL SA · …”, nu „Factura F1A<n>”.
    CF art.319 alin.(20) lit.a: seria și numărul de ordine, două elemente ale facturii.
    MUTAȚIA: `uc_tenants.bon_facturi_candidate` înapoi pe lipirea `serie + numar` -> „Factura F1A<n>” -> ROȘU."""
    pregateste_firma(patron, firma_e2e)
    tid, s, n = firma_e2e["tenant_id"], firma_e2e["schema"], str(_tag())
    _ok(_api(patron, "POST", "/tenants/%d/facturi-primite/manual" % tid,
             {"tert_tara": "RO", "tert_cui": DANTE, "tert_nume": DANTE_NUME, "serie": "F1A", "numar": n, "data_emitere": AZI.isoformat(),
              "moneda": "RON", "cont": "628",
              "linii": [{"descriere": "Servicii curierat", "cantitate": "1", "um": "buc", "pret_unitar": "100", "cota_tva": "21"}]}),
        "factura primită F1A")
    (fid, serie), = sql('SELECT id, serie FROM "%s".facturi WHERE directie = \'primita\' AND numar IN (%%s, %%s)' % s, (n, "F1A" + n))
    assert serie == "F1A", serie                                    # premisa: seria scrisă de contabil e păstrată separat
    ai_pregateste(json.dumps({"tip": "chitanta", "comerciant": DANTE_NUME, "cui": DANTE, "data": AZI.isoformat(), "total": 121.0,
                              "numar_document": "CH%s" % n, "mentiuni": "contravaloare factura", "articole": [], "tva": [],
                              "bon_complet": True, "orientare": 0}))
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    _card(patron, "bonuri", "#bc-adauga")
    with pg.expect_response(lambda r: "/confirma" in r.url and "/portal/bon/" in r.url, timeout=60000):
        pg.set_input_files("#bc-fisier", {"name": "chitanta_c181.jpg", "mimeType": "image/jpeg", "buffer": JPEG})
    pg.locator("[data-doc]", has_text="DANTE").first.wait_for(timeout=30000)
    pg.locator("[data-doc]", has_text="DANTE").first.click()
    pg.wait_for_selector("input[name='d-fact'][value='%d']" % fid, timeout=30000)
    eticheta = pg.eval_on_selector("input[name='d-fact'][value='%d']" % fid, "(e) => e.closest('label').querySelector('span').innerText")
    patron.captura("ce_plateste_chitanta")
    assert [x.strip() for x in eticheta.split(" · ")[:2]] == ["Factura F1A nr. %s" % n, DANTE_NUME], eticheta


def test_def_c181_fisa_partenerului_arata_seria_separat(patron, firma_e2e):
    """C181 (fișa partenerului). Pașii: o factură emisă către DANTE -> Rapoarte comerciale -> „Fișă client/furnizor”: DANTE INTERNATIONAL
    SA -> rândul facturii are în coloana „Număr” seria și numărul separat („<serie> nr. <n>”), nu lipite („<serie><n>”), ca în Istoric.
    CF art.319 alin.(20) lit.a. MUTAȚIA: `serie` scos din răspunsul `rapoarte_comerciale_api.fisa_partener` -> ecranul arată numărul
    lipit -> ROȘU."""
    pregateste_firma(patron, firma_e2e)
    fid = emite_api(patron, firma_e2e)["factura_id"]
    serie, numar = sql('SELECT serie, numar FROM "%s".facturi WHERE id = %%s' % firma_e2e["schema"], (fid,))[0]
    assert serie, (serie, numar)                                    # premisa: factura are serie (numerotarea firmei)
    asteptat = "%s nr. %s" % (serie, numar[len(serie):] if numar.startswith(serie) else numar)
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    _card(patron, "rapoarte", "#r-fisa-sel")
    pg.select_option("#r-fisa-sel", DANTE)
    pg.wait_for_selector("#r-fisa table.fd-tabel tbody tr", timeout=30000)
    numere = pg.eval_on_selector_all("#r-fisa table.fd-tabel tbody tr", "(rr) => rr.map((r) => r.cells[1].textContent.trim())")
    patron.captura("fisa_partenerului")
    assert asteptat in numere, (asteptat, numere)
    assert numar not in numere, numere                              # numărul cum e păstrat („E2EA3”) nu mai apare singur


# ── C182 / C183 / C184 / C185 — „De validat” și Registrul jurnal ───────────────────────────────────────────────────────────────────
_DETALIU = """(d) => { const tb = [...document.querySelectorAll('#val-note tbody.tn-nota')].find((t) => t.innerText.includes(d));
  if (!tb) return null; const det = tb.querySelector('.tn-detaliu'), cas = document.querySelector('#caseta-atentie-activa');
  return {deschis: !det.hidden, se_incarca: !!det.querySelector('.tn-linii-loc'),
          linii: [...det.querySelectorAll('table.tn-linii tbody tr')].map((r) => [...r.cells].map((c) => c.textContent.trim())),
          sub: [...det.querySelectorAll('.pf-frand-sub')].map((p) => p.textContent.trim()),
          intrebare: cas ? cas.querySelector('.ca-mesaj').textContent.trim() : null, intrebare_in_detaliu: !!cas && det.contains(cas),
          evid: tb.classList.contains('val-evidentiat')}; }"""
_LINII_INCARCATE = """(d) => { const tb = [...document.querySelectorAll('#val-note tbody.tn-nota')].find((t) => t.innerText.includes(d));
  const det = tb && tb.querySelector('.tn-detaliu'); return !!det && !det.hidden && !det.querySelector('.tn-linii-loc')
    && det.querySelectorAll('table.tn-linii tbody tr').length > 0; }"""
LINIA_ANEI = ["612", "401", "100,00"]   # nota scrisă de `_nota_prin_ecran`: 612 = 401 · 100 (liniile din `GET /coada/{id}/continut`)
INTREBAREA_FARA_DOC = ("Nota nu are document justificativ, iar o notă nu se validează fără documentul din care provine (Registrul-jurnal, "
                       "col.3: felul, numărul și data). Respinge-o cu motivul, ca cel care a pregătit-o să scrie referința.")


def test_def_c185_confirmarea_salvarii_spune_ca_nota_a_plecat_la_validare(ana, patron, firma_e2e):
    """C185. Pașii: Ana (numai „Poate pregăti”) -> Registru jurnal -> „+ Notă nouă” -> 612 = 401, 100 lei -> „Salvează”: sus, „Ai salvat
    nota din <azi> („<descriere>”) (trimisă la validare în cabinet).”, iar nota e în coada cabinetului; nu „(ciornă)”.
    MUTAȚIA: confirmarea înapoi pe „(ciornă)” scris de mână -> ROȘU."""
    pregateste_firma(patron, firma_e2e)
    desc = "E2E C185 servicii %d" % _tag()
    nid = _nota_prin_ecran(ana, firma_e2e, desc, AZI.isoformat(), luna=LUNA)
    pg = ana.pg
    pg.wait_for_function("() => ((document.querySelector('#j-mesaj') || {}).textContent || '').startsWith('Ai salvat')", timeout=20000)
    mesaj = " ".join(pg.inner_text("#j-mesaj").split())
    ana.captura("confirmarea_salvarii")
    assert mesaj == "Ai salvat nota din %s („%s”) (trimisă la validare în cabinet)." % (AZI.strftime("%d.%m.%Y"), desc), mesaj  # AZI-dat-de-test
    assert _coada_nota(firma_e2e, nid)[1] == "la_senior"


def test_def_c182_validarea_notei_fara_document_arata_liniile_si_le_tine_la_redesenare(ana, patron, firma_e2e):
    """C182. Pașii: Ana scrie o notă FĂRĂ document și una cu document -> contabilul-șef: „De validat” -> „Validează” pe nota fără document:
    întrebarea stă în detaliul rândului, iar detaliul arată liniile notei (612 = 401 · 100,00), nu „Se încarcă liniile notei…” -> „Validează”
    pe cealaltă notă: lista se redesenează pe loc, iar detaliul notei fără document rămâne deschis, cu liniile ei.
    MUTAȚIA: `locInDetaliu` deschide detaliul direct (`det.hidden = false`), ocolind tabelul -> liniile nu se încarcă -> ROȘU."""
    pregateste_firma(patron, firma_e2e)
    tag = _tag()
    fara = "E2E C182 fără document %d" % tag
    cu = "E2E C182 cu document %d" % tag
    _nota_prin_ecran(ana, firma_e2e, fara, AZI.isoformat(), luna=LUNA, doc="")
    nid_cu = _nota_prin_ecran(ana, firma_e2e, cu, AZI.isoformat(), luna=LUNA)
    pg = patron.pg
    _de_validat(patron)
    rand = _card_nota(patron, firma_e2e, fara).first
    rand.wait_for(timeout=20000)
    inchis = pg.evaluate(_DETALIU, fara)["deschis"]
    rand.locator(".tn-rand .val-aproba").click()
    pg.wait_for_selector("#caseta-atentie-activa", timeout=10000)
    pg.wait_for_function(_LINII_INCARCATE, arg=fara, timeout=20000)
    la_intrebare = pg.evaluate(_DETALIU, fara)
    patron.captura("intrebarea_cu_liniile")
    _card_nota(patron, firma_e2e, cu).first.locator(".tn-rand .val-aproba").click()
    if pg.query_selector("#caseta-atentie-activa #ca-ok") and not pg.evaluate(_DETALIU, fara)["intrebare_in_detaliu"]:
        pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("() => ((document.querySelector('#val-confirmare') || {}).textContent || '').startsWith('Ai validat')", timeout=30000)
    pg.wait_for_timeout(500)
    dupa = pg.evaluate(_DETALIU, fara)
    patron.captura("dupa_redesenare")
    assert inchis is False
    assert (la_intrebare["intrebare"], la_intrebare["intrebare_in_detaliu"]) == (INTREBAREA_FARA_DOC, True), la_intrebare
    assert (la_intrebare["deschis"], la_intrebare["se_incarca"], la_intrebare["linii"]) == (True, False, [LINIA_ANEI]), la_intrebare
    assert (dupa["deschis"], dupa["se_incarca"], dupa["linii"]) == (True, False, [LINIA_ANEI]), dupa
    assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % firma_e2e["schema"], (nid_cu,)) == [("validata",)]


def test_def_c183_detaliul_notei_de_validat_scrie_rulajul_o_data(ana, patron, firma_e2e):
    """C183. Pașii: Ana scrie o notă (612 = 401 · 100 lei) -> contabilul-șef: „De validat” -> clic pe rândul notei: ultimul rând al
    detaliului e „rulaj 100,00 lei”, iar niciun rând nu mai scrie „Rulaj: rulaj …”.
    MUTAȚIA: „Rulaj: ${rulajNota(n)}” pus la loc în `validat.randNotaCoada` -> ROȘU."""
    pregateste_firma(patron, firma_e2e)
    desc = "E2E C183 servicii %d" % _tag()
    _nota_prin_ecran(ana, firma_e2e, desc, AZI.isoformat(), luna=LUNA)
    pg = patron.pg
    _de_validat(patron)
    rand = _card_nota(patron, firma_e2e, desc).first
    rand.wait_for(timeout=20000)
    rand.locator(".tn-deschide").click()
    pg.wait_for_function(_LINII_INCARCATE, arg=desc, timeout=20000)
    d = pg.evaluate(_DETALIU, desc)
    patron.captura("detaliul_notei")
    assert d["sub"][-1] == "rulaj 100,00 lei", d["sub"]
    assert [x for x in d["sub"] if x.startswith("Rulaj")] == [], d["sub"]


def test_def_c184_de_validat_din_notificare_deschide_detaliul_notei(ana, patron, firma_e2e):
    """C184. Pașii: Ana scrie o notă -> contabilul-șef: clopoțel -> clic pe „Notă pregătită, de validat” -> „De validat”: rândul notei e
    marcat ȘI are detaliul deschis, cu liniile ei (612 = 401 · 100,00) — ca Registrul jurnal deschis dintr-o notificare.
    MUTAȚIA: deschiderea detaliului scoasă din `_arataEvidentiat` (validat.js) -> rândul marcat, detaliul închis -> ROȘU."""
    pregateste_firma(patron, firma_e2e)
    desc = "E2E C184 servicii %d" % _tag()
    _nota_prin_ecran(ana, firma_e2e, desc, AZI.isoformat(), luna=LUNA)
    pg = patron.pg
    patron.acasa()
    pg.click("#nav-clopot")
    pg.wait_for_selector(".clopot-item, .clopot-gol", timeout=20000)
    pg.locator(".clopot-item", has_text=desc).first.click()
    pg.wait_for_selector("#val-note tbody.tn-nota.val-evidentiat", timeout=20000)
    pg.wait_for_function(_LINII_INCARCATE, arg=desc, timeout=20000)
    d = pg.evaluate(_DETALIU, desc)
    patron.captura("din_notificare")
    assert (d["evid"], d["deschis"], d["se_incarca"], d["linii"]) == (True, True, False, [LINIA_ANEI]), d


# ── C186 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_cv():
    """[C186] o firmă nouă, pregătită ca în `e2e_bloc_c`: `firma_e2e` a modulului are deja facturi emise de testele de mai sus, iar
    numerotarea nu se mai poate porni de la 1 (refuzul corect al lui `seteaza_numerotare`)."""
    for f in firma_noua():
        yield pregateste_cv(f)


def test_def_c186_refuzul_numai_pe_campuri_nu_mai_vine_si_in_fereastra(patron, firma_cv):
    """C186. Pașii: Emite factură -> client român (DANTE), articolul din stoc, 0%, „livrare intracomunitară” -> „Emite”: refuzul are o
    singură eroare, pe câmpul categoriei liniei („…(țara clientului: RO).”), și caseta „NU s-a salvat.” lângă buton; după 1,5 s (plasa
    „refuz nevăzut” pune fereastra la 0,7 s) fereastra „Am înțeles” NU apare. ROȘU înainte: refuzul apărea și în fereastră.
    MUTAȚIA: `api._refuzNevazut` nu mai socotește arătate erorile de câmp -> fereastra apare -> ROȘU."""
    pregateste_firma(patron, firma_cv)
    _deschide_emiterea(patron, firma_cv["nume"])
    pg = patron.pg
    pg.fill("#em-cui", DANTE)
    pg.fill("#em-nume", DANTE_NUME)
    pg.select_option("#em-l0-articol", label=pg.locator("#em-l0-articol option", has_text=firma_cv["marfa"]).first.inner_text())
    pg.fill("#em-l0-cantitate", "1")
    pg.fill("#em-l0-pret_unitar", "10")
    pg.select_option("#em-l0-cota", "0")
    pg.wait_for_selector("#em-l0-categorie", state="visible", timeout=10000)
    pg.select_option("#em-l0-categorie", "livrare_ic")
    pg.click("#em-emite")
    pg.wait_for_selector(".msg-eroare[data-camp]", state="visible", timeout=30000)
    pg.wait_for_timeout(1500)
    m = pg.evaluate("""() => { const vaz = (x) => x.getClientRects().length > 0;
      return {campuri: [...document.querySelectorAll('.msg-eroare[data-camp]')].filter((x) => vaz(x) && !x.closest('.refuz-salvare') && x.textContent.trim())
                .map((x) => x.textContent.trim()),
              nu_s_a_salvat: [...document.querySelectorAll('.refuz-salvare')].filter(vaz).length,
              fereastra: !!document.querySelector('#refuz-nevazut')}; }""")
    patron.captura("refuzul_o_data")
    assert m["campuri"] == ["Livrarea intracomunitară scutită cere un client dintr-un alt stat membru UE (țara clientului: RO)."], m
    assert m["nu_s_a_salvat"] == 1, m
    assert m["fereastra"] is False, m                               # „apărea și în fereastra «Am înțeles»”
