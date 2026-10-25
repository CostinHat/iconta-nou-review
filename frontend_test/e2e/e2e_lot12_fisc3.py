# -*- coding: utf-8 -*-
"""Lotul 12, pachetul fisc3 (comanda 12.3 pct.3, pct.7, pct.10): testele de capăt la capăt pentru C156, C157, C163 și C84.

  · C156 — prestarea intracomunitară de servicii a neplătitorului ÎNREGISTRAT art.317 (forma firmei de test F3): „fără TVA român, mențiunea
    «taxare inversă», codul RO art. 317 pe factură, P în D390”. Ecranul (detaliul facturii) și PDF-ul: „Cod TVA (art.317): RO…”, „Taxare
    inversă”, fără „Scutit de TVA … art. 310” (CF art.318 alin.(1), alin.(4) lit.b pct.2; CF art.319 alin.(20) lit.d și lit.m).
  · C157 — neplătitorul NEînregistrat art.317: aceeași prestare se emite, cu avertismentul emiterii (CF art.317 alin.(1) lit.b).
  · C163 — serviciul primit de la prestatorul din UE (factura primită, fără operațiunea din ecranul D301) face luna D301 datorată în
    Control fiscal, iar D301 numește factura neintrodusă (CF art.307 alin.(2), art.324 alin.(1) lit.d).
  · C84 — livrarea intracomunitară de bunuri fără dovada transportului se emite cu avertisment, nu se refuză (CF art.294 alin.(3);
    HG 1/2016 pct.65).

Pașii pe aplicația din index, pe baza de TEST, pe firme NOI de test (`firma_noua`), pregătite pe drumul ecranelor (`pregateste_firma` +
Date firmă + Vector fiscal, `e2e_lot12_cx3._neplatitor_art317`). Facturile se datează în luna încheiată (`conftest.perioada_incheiata`).
VIES e servit de plasă (codul DE811907980 al probelor R187 / C78 / C110 / C154). `sql` doar citește."""
import pytest

from conftest import alege_perioada, alege_tipul, firma_noua, perioada_incheiata, sql

COD_CLIENT_IC = "DE811907980"
LUNA = perioada_incheiata("lunar")
ZI = LUNA.inceput.replace(day=12)
_F = ".fereastra:last-of-type "


@pytest.fixture()
def firma_fisc3():
    for f in firma_noua():
        yield f


def _cui_digits(f):
    return "".join(ch for ch in sql('SELECT cui FROM "%s".firma_profil' % f["schema"])[0][0] if ch.isdigit())


def _neinregistrat_art317(patron, f):
    """Neplătitorul cu operațiuni intracomunitare, NEînregistrat art.317 (vectorul fiscal, ruta ecranului „Vector fiscal”)."""
    from e2e_bloc_a import _api, _ok
    from e2e_lot12_cx3 import _neplatitor_art317
    _neplatitor_art317(patron, f)
    _ok(_api(patron, "POST", "/tenants/%d/vector" % f["tenant_id"], {"regim_fiscal": "micro", "platitor_tva": False, "tip_decont": None,
                                                                     "operatiuni_ic": True, "inreg_art317": False,
                                                                     "tva_data_inceput": None}), "vector fiscal (neînregistrat art.317)")


def _pdf(patron, fid):
    from e2e_bloc_a import _pdf_ok, _pdf_text
    pg = patron.pg
    with pg.expect_response(lambda r: r.url.endswith("/facturi/%s/pdf" % fid), timeout=30000) as rr:
        pg.click("#fd-pdf")
    return _pdf_text(_pdf_ok(patron, rr))[0]


# ── C156 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c156_prestarea_ic_a_neplatitorului_art317_poarta_taxare_inversa_si_codul_ro(patron, firma_fisc3):
    """C156. Pașii: firmă neplătitoare de TVA, înregistrată art.317 -> Facturi -> Emite factură -> client DE811907980 (VIES valid), linia
    „Servicii de consultanta IT …”, 500 lei, 0% -> „Emite factură” -> „Istoric facturi” -> factura nouă: sub antet „Codul de TVA al firmei pe
    această factură (art.317): RO<CUI>” și „… Taxare inversă — prestare de servicii cu locul în alt stat membru …”, linia cu categoria
    prestării cu locul în afara României -> „PDF”: „Cod TVA (art.317): RO<CUI>”, „Taxare inversă”, fără „Scutit de TVA … art. 310”.
    Înainte: „CIF: <CUI>” și „Scutit de TVA — regim special de scutire … art. 310” (categoria O).
    MUTAȚIA (`mut_lot12_fisc3.json`): categoria prestării art.317 oprită în `categorii_tva.verifica_linii` -> linia O -> ROȘU."""
    from core import categorii_tva, factura_pdf
    from e2e_bloc_a import _card
    from e2e_bloc_e import _la_luna   # factura e pe luna încheiată: istoricul pornește pe luna de azi
    from e2e_lot12_cx3 import _neplatitor_art317
    from e2e_lot12_cx5 import _emite_prestarea_ic
    f = firma_fisc3
    s = f["schema"]
    _neplatitor_art317(patron, f)
    fid = _emite_prestarea_ic(patron, f)
    patron.captura("emisa")
    assert sql('SELECT categorie_tva, cota_tva::text FROM "%s".factura_linii WHERE factura_id = %%s' % s, (fid,)) == [
        (categorii_tva.PRESTARE_IC_317, "0.00")]
    cui = _cui_digits(f)
    ((data_f,),) = sql('SELECT data_emitere FROM "%s".facturi WHERE id = %%s' % s, (fid,))
    patron.firma(f["nume"])
    _card(patron, "facturi", "#fac-istoric")
    patron.pg.click("#fac-istoric")
    _la_luna(patron, "#fac-prev", data_f.year, data_f.month)
    patron.pg.click(".fac-frand-btn[data-id='%s']" % fid)
    patron.pg.wait_for_selector("#fd-pdf", timeout=25000)
    pg = patron.pg
    antet = [" ".join(t.split()) for t in pg.locator(".fd-antet-linie").all_inner_texts()]
    patron.captura("detaliul")
    # CF art.318 alin.(1): codul atribuit conform art.317 „are prefixul RO”; alin.(4) lit.b pct.2: se comunică „beneficiarului, persoană
    # impozabilă din alt stat membru, către care prestează servicii pentru care acesta este obligat la plata taxei”
    # CF art.319 alin.(20) lit.m: „în cazul în care clientul este persoana obligată la plata TVA, mențiunea «taxare inversă»” — ultimele
    # rânduri ale antetului sunt mențiunile facturii (`f.mentiuni`), întregi: codul art.317, apoi „taxare inversă”; fără scutirea art.310
    mentiune = factura_pdf.mentiuni_categorii([{"categorie_tva": categorii_tva.PRESTARE_IC_317}], "DE")[0]
    assert antet[-2:] == ["Codul de TVA al firmei pe această factură (art.317): RO" + cui, mentiune], antet
    assert antet.count(factura_pdf.MENTIUNE_NEPLATITOR) == 0, antet
    assert categorii_tva.CATEGORII[categorii_tva.PRESTARE_IC_317]["eticheta"] in pg.locator(".fd-categorie").first.inner_text()
    text = _pdf(patron, fid)
    # antetul PDF-ului (rândul întreg al firmei: codul art.317, apoi Registrul Comerțului din Date firmă) și mențiunea întreagă, o dată
    assert (text.count("Cod TVA (art.317): RO%s · J40/1234/2015" % cui), text.count(mentiune),
            text.count(" ".join(factura_pdf.MENTIUNE_NEPLATITOR.split()))) == (1, 1, 0), text[:800]


# ── C157 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c157_prestarea_ic_fara_inregistrare_art317_primeste_avertisment_nu_refuz(patron, firma_fisc3):
    """C157. Pașii: firmă neplătitoare de TVA, NEînregistrată art.317 -> Emite factură -> client DE811907980, serviciu 500 lei, 0% ->
    „Emite factură”: factura se emite („✓ Factura … emisă”), iar sub confirmare avertismentul: firma nu e înregistrată art.317, Codul fiscal
    cere înregistrarea înainte de prestare (art.317 alin.(1) lit.b), ce să facă (Date firmă). Factura: categoria O, „CIF”.
    Înainte: nimic — prestarea se emitea fără niciun semn.
    MUTAȚIA (`mut_lot12_fisc3.json`): `avertismente_emitere` întoarce mereu [] -> fără avertisment -> ROȘU."""
    from core import categorii_tva
    from e2e_lot12_cx5 import _emite_prestarea_ic
    f = firma_fisc3
    s = f["schema"]
    _neinregistrat_art317(patron, f)
    fid = _emite_prestarea_ic(patron, f)
    pg = patron.pg
    av = pg.locator("#em-rezultat .em-avertisment-emitere")
    av.first.wait_for(timeout=10000)
    patron.captura("avertismentul")
    t = " ".join(av.first.inner_text().split())
    # CF art.317 alin.(1) lit.b — înregistrarea neplătitorului care „prestează servicii care au locul în alt stat membru, pentru care
    # beneficiarul serviciului este persoana obligată la plata taxei [...], înainte de prestarea serviciului”; decizia Costin 12.3 pct.3:
    # „avertisment la emitere, nu refuz”
    assert t == categorii_tva.AVERTISMENT_FARA_ART317, t
    assert pg.locator("#em-rezultat.em-emisa").count() == 1, "factura s-a emis (nu e un refuz)"
    assert sql('SELECT categorie_tva FROM "%s".factura_linii WHERE factura_id = %%s' % s, (fid,)) == [(categorii_tva.NEPLATITOR["cod"],)]


# ── C163 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c163_serviciul_primit_din_ue_face_d301_datorat_si_e_numit_la_generare(patron, firma_fisc3):
    """C163. Pașii (datele, pe rutele ecranelor): firmă neplătitoare, înregistrată art.317 -> Operațiuni › „Achiziție intracomunitară” ›
    Servicii, 300 lei, furnizor DE811907980, factura „AIS-E2E-1”, în luna încheiată -> ecranul D301 › operațiunea se șterge (factura primită
    rămâne). Pe ecran: Control fiscal -> detaliul firmei: D301 pe luna facturii (rândul `d301-<an>-<luna>`) -> Declarații -> D301, luna ->
    „Continuă”: refuzul numește factura („… (fact. AIS-E2E-1, 300 lei) …”, tipul 5).
    Înainte: niciun rând D301 (faptul pe facturi scotea serviciile), iar D301 spunea „nicio operațiune cu exigibilitate în perioadă”.
    MUTAȚIA (`mut_lot12_fisc3.json`): `cu_servicii=True` scos din `control_incrucisat.d301_luni_facturi_ic` -> rândul D301 lipsește -> ROȘU."""
    from e2e_bloc_a import _api, _ok
    from e2e_bloc_c import _deschide
    from e2e_bloc_f import _detaliu_fiscal
    from e2e_lot12_cx3 import _neplatitor_art317
    f = firma_fisc3
    tid = f["tenant_id"]
    _neplatitor_art317(patron, f)
    _ok(_api(patron, "POST", "/tenants/%d/achizitie-ic" % tid, {
        "data": ZI.isoformat(), "valoare": 300, "cota": 21, "cod_tva_furnizor": COD_CLIENT_IC, "numar": "AIS-E2E-1",
        "furnizor_nume": "LIEFERANT E2E GMBH", "tip": "servicii", "cont_destinatie": "628", "descriere": "Servicii software"}),
        "achiziția intracomunitară de servicii")
    ops = _ok(_api(patron, "GET", "/tenants/%d/d301-operatiuni?an=%d&luna=%d" % (tid, LUNA.an, LUNA.luna)), "operațiunile D301")
    for op in ops["operatiuni"]:
        _ok(_api(patron, "DELETE", "/tenants/%d/d301-operatiuni/%d?an=%d&luna=%d" % (tid, op["id"], LUNA.an, LUNA.luna)), "ștergerea")
    pg = patron.pg
    _detaliu_fiscal(patron, f["nume"])
    patron.captura("control_fiscal", intreaga=True)
    rand = _F + ".cf-decl-item[data-cheie='d301-%d-%d']" % (LUNA.an, LUNA.luna)
    # CF art.307 alin.(2): „Taxa este datorată de orice persoană impozabilă [...] care este beneficiar al serviciilor care au locul
    # prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe
    # teritoriul României”; CF art.324 alin.(1) lit.d: decontul special se depune „pentru operațiunile și de către persoanele obligate la
    # plata taxei, conform art. 307 alin. (2)-(4) și (6)”
    assert pg.locator(rand).count() == 1, "D301 %02d/%d lipsește din Control fiscal" % (LUNA.luna, LUNA.an)
    _deschide(patron, f["nume"], "declaratii", "#dec-tip")
    alege_tipul(pg, "d301")
    pg.wait_for_selector("#dec-an", timeout=10000)
    alege_perioada(pg, LUNA.an, LUNA.luna)
    pg.click("#dec-continua")
    pg.wait_for_function("() => document.body.innerText.includes('fact. AIS-E2E-1')", timeout=90000)
    patron.captura("d301_numeste_factura")
    corp = " ".join(pg.inner_text("body").split())
    refuz = ("D301 pe zero, dar în perioadă există achiziții intracomunitare (bunuri sau servicii) înregistrate ca facturi și neintroduse "
             "în operațiunile D301 (1): LIEFERANT E2E GMBH (fact. AIS-E2E-1, 300,00 lei). Introdu-le în ecranul D301 înainte de generare "
             "(serviciile la tipul 5): obligația D301 se naște din achiziția intracomunitară.")
    assert corp.count(refuz) == 1, corp[-800:]


# ── C84 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c84_livrarea_ic_fara_dovada_transportului_se_emite_cu_avertisment(patron, firma_fisc3):
    """C84 (decizia Costin 12.3 pct.7). Pașii: firmă plătitoare de TVA -> Emite factură -> CUI DE811907980 -> Verifică (VIES: valid, DE) ->
    linia „Marfa revanzare IC E2E”, 2 × 100,00, cota 0%, categoria „livrare intracomunitară” -> „Emite factură” -> caseta „Ai dovada
    transportului bunurilor în alt stat membru? …” -> „Nu încă, emite factura”: factura se emite (200,00, TVA 0,00, scutirea rămâne), iar
    sub confirmare avertismentul spune ce lipsește (dovada transportului) și ce se întâmplă cu scutirea (art.294 alin.(3); HG 1/2016
    pct.65). Înainte: fără întrebare, fără avertisment (iar vechea verificare din Operațiuni refuza).
    MUTAȚIA (`mut_lot12_fisc3.json`): întrebarea oprită (`if intreaba_dovada and _lic and dovada_transport is None:` -> `if False:`) ->
    caseta nu apare -> ROȘU; avertismentul oprit -> ROȘU."""
    from core import intracomunitar as ic
    from e2e_bloc_a import _api, _deschide_emiterea, _ok, _profil, pregateste_firma
    from e2e_lot12_emit import _vies
    f = firma_fisc3
    s = f["schema"]
    pregateste_firma(patron, f)
    p = _profil(f)
    p["metoda_stoc"] = "global_valoric"   # marfa fără articol de stoc (la cantitativ-valoric linia de bunuri cere articolul)
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"], p), "Date firmă (stoc global-valoric)")
    pg = patron.pg
    _vies(pg)
    _deschide_emiterea(patron, f["nume"])
    pg.fill("#em-cui", COD_CLIENT_IC)
    pg.dispatch_event("#em-cui", "change")
    pg.click("#em-verifica")
    pg.wait_for_function("() => (document.querySelector('#em-cui-stare') || {innerText: ''}).innerText.includes('valid în VIES')", timeout=20000)
    pg.fill("#em-nume", "KUNDE E2E GMBH")
    pg.fill("#em-adresa", "Unter den Linden 1")
    pg.fill("#em-oras", "Berlin")
    pg.fill("#em-data", ZI.isoformat())
    pg.fill("#em-l0-descriere", "Marfa revanzare IC E2E")
    pg.wait_for_timeout(1200)                                              # propunerea cotei pentru denumire
    pg.fill("#em-l0-cantitate", "2")
    pg.dispatch_event("#em-l0-cantitate", "input")
    pg.fill("#em-l0-pret_unitar", "100")
    pg.dispatch_event("#em-l0-pret_unitar", "input")
    pg.select_option("#em-l0-cota", "0")
    pg.wait_for_selector("#em-l0-categorie", state="visible", timeout=5000)
    pg.select_option("#em-l0-categorie", "livrare_ic")
    inainte = {r[0] for r in sql('SELECT id FROM "%s".facturi' % s)}
    pg.click("#em-emite")
    pg.wait_for_selector("#em-dovada-nu", timeout=30000)
    patron.captura("intrebarea")
    assert " ".join(pg.inner_text("#em-rezultat .caseta-poarta .cp-mesaj").split()) == (
        ic.INTREBARE_DOVADA_TRANSPORT + " Dacă nu o ai încă, factura se emite și îți spune ce lipsește.")
    assert {r[0] for r in sql('SELECT id FROM "%s".facturi' % s)} == inainte, "întrebarea nu scrie nimic"
    pg.click("#em-dovada-nu")
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=30000)
    av = pg.locator("#em-rezultat .em-avertisment-emitere")
    av.first.wait_for(timeout=10000)
    patron.captura("emisa_cu_avertisment")
    t = " ".join(av.first.inner_text().split())
    # decizia Costin 12.3 pct.7: „avertisment la emitere, nu refuz”; CF art.294 alin.(3): „Prin ordin al ministrului finanțelor publice se
    # stabilesc, acolo unde este cazul, documentele necesare pentru a justifica scutirea de taxă”; HG 1/2016 pct.65: scutirile „sunt
    # aplicate în măsura în care persoanele impozabile pot justifica scutirea cu documentele prevăzute”
    assert t == ic.AVERTISMENT_LIC_FARA_DOVADA, t
    noi = [r[0] for r in sql('SELECT id FROM "%s".facturi ORDER BY id' % s) if r[0] not in inainte]
    assert len(noi) == 1, noi
    assert sql('SELECT total::text, tva::text FROM "%s".facturi WHERE id = %%s' % s, (noi[0],)) == [("200.00", "0.00")]
    assert sql('SELECT categorie_tva FROM "%s".factura_linii WHERE factura_id = %%s' % s, (noi[0],)) == [("livrare_ic",)]


# ── C189 (cererea pachetului fe3, comanda 12.3 pct.9) ────────────────────────────────────────────────────────────────────────────────
def test_def_c189_propunerea_cotei_sosita_dupa_alegere_nu_inlocuieste_cota_aleasa(patron, firma_fisc3):
    """C189. Pașii: firmă plătitoare -> Emite factură -> denumirea liniei „Servicii de consultanță contabilă E2E” (în nomenclator cu 21%) ->
    înainte să sosească propunerea cotei, contabilul alege 11% -> propunerea (21%) sosește: cota liniei rămâne 11%, iar 21% stă doar ca
    propunere în titlul listei („Cota TVA — propusă: 21%”, pentru jurnalul „propus → ales”). Înainte: propunerea înlocuia cota aleasă.
    MUTAȚIA (`mut_lot12_fisc3.json`): ramura `if (l.cotaAleasa) {…}` scoasă din `emitere_ecran.js` -> cota devine 21 -> ROȘU."""
    from e2e_bloc_a import PRODUS, _deschide_emiterea, pregateste_firma
    f = firma_fisc3
    pregateste_firma(patron, f)
    pg = patron.pg
    tinute = []
    pg.route("**/produse/potriveste", lambda r: tinute.append(r))   # răspunsul propunerii ținut până după alegerea omului
    _deschide_emiterea(patron, f["nume"])
    pg.fill("#em-l0-descriere", PRODUS)
    pg.wait_for_function("() => document.querySelector('#em-l0-cota').value === ''", timeout=10000)
    for _ in range(40):
        if tinute:
            break
        pg.wait_for_timeout(250)
    assert tinute, "cererea propunerii cotei n-a plecat"
    pg.select_option("#em-l0-cota", "11")
    tinute[0].continue_()
    pg.wait_for_function("() => (document.querySelector('#em-l0-cota').title || '') === 'Cota TVA — propusă: 21%'", timeout=15000)
    patron.captura("cota_aleasa_ramane")
    assert pg.input_value("#em-l0-cota") == "11", pg.input_value("#em-l0-cota")
    pg.unroute("**/produse/potriveste")
