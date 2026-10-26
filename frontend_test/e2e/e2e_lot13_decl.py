# -*- coding: utf-8 -*-
"""Lotul 13, comanda Costin 13.1 (`~/ghid_incoming/comanda_13_1.txt`), subagentul DECL — declarațiile: 651, 659, 656, 657, 652, 653, 654,
658, 650, 635, 595, 594, 636, 637, 638, 538, 591, 592, 539, 540, 660 și C19 (D112). Pașii contabilului pe aplicația din index, pe baza de
TEST, pe firme NOI (`firma_noua`).

DATE DE PORNIRE fără ecran (declarate, `# date-de-pornire` pe linie): Date firmă și vectorul fiscal pe rutele ecranelor (`pregateste_firma`,
`_profil` din `e2e_lot12_decl`, `_neplatitor_art317` din `e2e_lot12_cx3`); achiziția intracomunitară pe ruta formularului din Operațiuni
(`POST achizitie-ic`); salariatul pe ruta salariaților (`_firma_cu_salariat`); depunerea la ANAF a unei declarații = rândul ei din
`public.declaratii_depuse` (o depunere nu se poate produce din plasă). CUI-ul furnizorului irlandez IE6388047V e cel din proba lui Costin
(F3, achiziția IE-100); CNP-ul salariatului are cifra de control calculată (`e2e_bloc_b._cnp`).

Temeiurile (citate pe linia aserțiunii; textul întreg în `core/verificare_bun_simt.py`, `core/declaratii_api.py`): CF art.224 alin.(4)
lit.b (dividendele nerezidenților: 10% în 2025, OUG 156/2024 art.LXIV pct.15); CF art.324 alin.(10) (D311); CF art.315 alin.(3)-(4) (D398);
HG 1/2016 pct.73 alin.(13) și (15) lit.c (D318); CF art.324 alin.(1) (D301); CF art.325 alin.(2) (D390); CF art.122 / 130 / 107 / 125 / 151
(formularele înlocuite de Declarația unică); OPANAF 605/2026 anexa nr.2 pct.2.4 (rectificativa D112)."""
import datetime as _dt
import re

import pytest

from conftest import alege_perioada, alege_tipul, firma_noua, perioada_incheiata, sql
from e2e_bloc_a import _api, _card, _ok, pregateste_firma

_F = ".fereastra:last-of-type "
AN_D207 = 2025          # anul încheiat pe care cota dividendelor nerezidenților e verificată la sursă (10%)
AZI = _dt.date.today()
LUNA = perioada_incheiata("lunar")
COD_IE = "IE6388047V"


@pytest.fixture()
def firma_l13():
    for f in firma_noua():
        yield f


def _platitor(patron, f, regim="profit"):
    from e2e_lot12_decl import _profil
    _profil(patron, f, regim=regim)


def _neplatitor(patron, f, art317=True):
    if art317:
        from e2e_lot12_cx3 import _neplatitor_art317
        _neplatitor_art317(patron, f)
        return
    pregateste_firma(patron, f, platitor=False)


def _pas1(patron, f, tip, an, luna=None, trim=None):
    """Firma -> Declarații -> tipul (din „Alte declarații”, dacă trebuie) -> perioada (pasul 1)."""
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "declaratii", _F + "#dec-tip")
    alege_tipul(pg, tip, zona=_F)
    alege_perioada(pg, an, luna, trim, zona=_F)
    return pg


def _continua_formular(patron, f, tip, an, luna=None, trim=None):
    """Pasul 1 -> „Continuă →”: la o declarație cu formular, pasul 2 arată formularul (fără nicio cerere la server)."""
    pg = _pas1(patron, f, tip, an, luna, trim)
    pg.click(_F + "#dec-continua")
    pg.wait_for_selector(_F + "#dec-%s-form details" % tip, timeout=60000)
    return pg


def _txt(pg, sel=""):
    loc = pg.locator(_F + sel) if sel else pg.locator(".fereastra").last
    return " ".join(loc.inner_text().split()) if loc.count() else ""


def _asteapta_rezultat(pg):
    pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); return f && f.innerText.includes("
                         "'Pasul 2 din 3') && !!f.querySelector('.dec-ok, .dec-avert, #dec-refuz, #dec-rect-depusa'); }", timeout=120000)


# ── D207: beneficiarul nerezident ──────────────────────────────────────────────────────────────────────────────────────────────────
def _beneficiar_d207(pg, baza, imp, tip="01", stat_cauta="germ", stat="DE"):
    z = _F
    pg.select_option(z + "#d207-tip", tip)
    pg.fill(z + "#d207-den", "KUNDE GMBH")
    pg.fill(z + "#d207-stat-cauta", stat_cauta)
    pg.select_option(z + "#d207-stat", stat)
    pg.fill(z + "#d207-cifs", "DE811907980")
    pg.select_option(z + "#d207-act", "1")
    pg.fill(z + "#d207-baza", str(baza))
    pg.fill(z + "#d207-imp", str(imp))


def test_def_651_d207_formularul_gol_fara_eroare_rosie(patron, firma_l13):
    """651 (clasa 89). Pașii: Declarații -> D207, 2025 -> „Continuă”: pasul 2 arată formularul și o notă neutră („Completează formularul de
    mai jos, apoi apasă „Generează D207””), fără niciun refuz roșu („D207 nu are ce genera” era starea normală a unei firme fără plăți către
    nerezidenți, afișată ca eroare). MUTAȚIA: pasul 2 cere serverul și la formularul gol -> refuzul roșu -> ROȘU."""
    _platitor(patron, firma_l13)
    pg = _continua_formular(patron, firma_l13, "d207", AN_D207)
    patron.captura("d207_formular")
    assert "Completează formularul de mai jos, apoi apasă „Generează D207”" in _txt(pg, "#dec-completeaza"), patron.fereastra()[:1500]
    assert pg.locator(_F + ".dec-eroare, " + _F + "#dec-refuz, " + _F + ".msg-eroare").count() == 0, patron.fereastra()[:1500]
    assert "nu are ce genera" not in patron.fereastra()
    assert pg.inner_text(_F + "#d207-regen").strip() == "Generează D207"


def test_def_659_d311_la_deschidere_fara_erori(patron, firma_l13):
    """659 (clasele 651, 285). Pașii: firmă neplătitoare -> Declarații -> D311, luna trecută -> „Continuă”: formularul, fără paragraful roșu
    cu trei erori de sub zona vizibilă (data anulării, motivul, sumele) — erorile apar numai la „Generează D311”, lângă câmpuri.
    MUTAȚIA: aceeași ca la 651 -> ROȘU."""
    _neplatitor(patron, firma_l13, art317=False)
    pg = _continua_formular(patron, firma_l13, "d311", LUNA.an, LUNA.luna)
    patron.captura("d311_formular")
    assert pg.locator(_F + "#dec-completeaza").count() == 1 and pg.locator(_F + ".dec-eroare, " + _F + "#dec-refuz").count() == 0
    pg.click(_F + "#d311-regen")
    pg.wait_for_selector(_F + ".msg-eroare[data-camp='d311-data']", timeout=20000)
    assert pg.locator(_F + ".dec-eroare, " + _F + "#dec-refuz").count() == 0   # lângă câmpuri, nu un paragraf sub formular


def test_def_656_d207_impozitul_peste_baza_e_oprit_la_adaugare(patron, firma_l13):
    """656. Pașii: D207, 2025 -> beneficiar: dividende, KUNDE GMBH, Germania, cod fiscal străin, Codul fiscal, bază 1 leu, impozit 160 lei ->
    „+ adaugă beneficiarul”: refuzul stă lângă „Impozit reținut” („Impozitul (160,00 lei) e mai mare decât baza (1,00 lei) …”), beneficiarul
    nu intră în listă. CF art.224 alin.(4): impozitul se calculează „prin aplicarea următoarelor cote asupra veniturilor brute”.
    MUTAȚIA: verificarea din ecran scoasă -> beneficiarul intră -> ROȘU."""
    _platitor(patron, firma_l13)
    pg = _continua_formular(patron, firma_l13, "d207", AN_D207)
    _beneficiar_d207(pg, 1, 160)
    pg.click(_F + "#d207-add")
    pg.wait_for_selector(_F + ".msg-eroare[data-camp='d207-imp']", timeout=20000)
    patron.captura("d207_160_pe_1")
    assert "Impozitul (160,00 lei) e mai mare decât baza (1,00 lei)" in _txt(pg, ".msg-eroare[data-camp='d207-imp']")
    assert pg.locator(_F + ".dec-d207-del").count() == 0


def test_def_656_d207_cota_dividendelor_verificata_inaintea_validatorului(patron, firma_l13):
    """656 (cota). Pașii: D207, 2025 -> dividende plătite unui nerezident, Codul fiscal, bază 10.000, impozit 1.600 (16%) -> „+ adaugă” ->
    „Generează D207”: nu se generează — „la dividende plătite în 2025, Codul fiscal cere impozit de 10% din bază (CF art.224 alin.(4) lit.b):
    1.000 lei, nu 1.600 lei” (OUG 156/2024 art.LXIV pct.15); fără caseta verde a validatorului. MUTAȚIA: cota din 2025 pusă 16% ->
    D207 trece -> ROȘU."""
    _platitor(patron, firma_l13)
    pg = _continua_formular(patron, firma_l13, "d207", AN_D207)
    _beneficiar_d207(pg, 10000, 1600)
    pg.click(_F + "#d207-add")
    pg.wait_for_selector(_F + ".dec-d207-del", timeout=20000)
    pg.click(_F + "#d207-regen")
    _asteapta_rezultat(pg)
    patron.captura("d207_cota_dividende")
    refuz = _txt(pg, "#dec-refuz")
    assert "verificarea cifrelor" in refuz and "Codul fiscal cere impozit de 10% din bază" in refuz and "1.000 lei, nu 1.600 lei" in refuz, refuz
    assert pg.locator(_F + ".dec-ok").count() == 0


def _d207_validata(patron, f):
    _platitor(patron, f)
    pg = _continua_formular(patron, f, "d207", AN_D207)
    _beneficiar_d207(pg, 10000, 1000)   # CF art.224 alin.(4) lit.b, 2025: 10%
    pg.click(_F + "#d207-add")
    pg.wait_for_selector(_F + ".dec-d207-del", timeout=20000)
    pg.click(_F + "#d207-regen")
    _asteapta_rezultat(pg)
    assert "Validat cu DUKIntegrator" in _txt(pg, ".dec-ok"), patron.fereastra()[:3000]   # DUK D207 — judecătorul structurii
    return pg


def test_def_657_dupa_stergerea_beneficiarului_validarea_se_anuleaza(patron, firma_l13):
    """657. Pașii: D207, 2025 -> un beneficiar (10.000 / 1.000) -> „Generează D207”: „Validat … fără erori”, „Trimite în coadă →” activ ->
    „șterge” beneficiarul (0 beneficiari): caseta verde și rezultatul dispar, „Trimite în coadă →” e inactiv, iar lângă el: „Ai modificat
    declarația după ce a fost generată și validată, deci rezultatul nu mai e valabil. Apasă „Regenerează D207” …”.
    MUTAȚIA: modificarea nu se mai socotește -> caseta verde și butonul rămân -> ROȘU."""
    pg = _d207_validata(patron, firma_l13)
    assert pg.is_enabled(_F + "#dec-trimite")
    pg.click(_F + ".dec-d207-del")
    pg.wait_for_function("() => ((document.querySelector('.fereastra:last-of-type #dec-invalidat') || {}).innerText || '').trim() !== ''",
                         timeout=20000)
    patron.captura("d207_dupa_stergere")
    assert pg.locator(_F + "#dec-rezultat").is_hidden() and not pg.locator(_F + ".dec-ok").is_visible()
    assert pg.is_disabled(_F + "#dec-trimite")
    assert "rezultatul nu mai e valabil. Apasă „Regenerează D207”" in _txt(pg, "#dec-invalidat")


def test_def_658_d207_fara_harta_de_componente(patron, firma_l13):
    """658 (clasa 163). Pașii: D207 generată și validată: pe ecran nu mai apare „Cifra acestui tip de declarație nu se poate desface — nu e
    trecut în harta de componente” și nici altă notă despre componente (declarația e chiar formularul de deasupra).
    MUTAȚIA: D207 scoasă din `DIN_FORMULAR` -> nota despre rânduri -> ROȘU."""
    pg = _d207_validata(patron, firma_l13)
    t = patron.fereastra()
    patron.captura("d207_fara_componente")
    assert "harta de componente" not in t and "nu se pot arăta aici" not in t and "nu se poate desface" not in t, t[:3000]


def test_def_652_beneficiarul_completat_se_adauga_la_generare(patron, firma_l13):
    """652. Pașii: D207, 2025 -> beneficiarul completat (10.000 / 1.000), FĂRĂ „+ adaugă” -> „Generează D207”: beneficiarul intră în
    declarație (cererea poartă un beneficiar), nicio eroare pe „Nume” (completat corect), nicio casetă dublă.
    MUTAȚIA: adăugarea la generare scoasă -> „Adaugă cel puțin un beneficiar” și nicio cerere -> ROȘU."""
    _platitor(patron, firma_l13)
    pg = _continua_formular(patron, firma_l13, "d207", AN_D207)
    _beneficiar_d207(pg, 10000, 1000)
    with pg.expect_request(lambda r: r.method == "POST" and r.url.endswith("/declaratii/d207/valideaza"), timeout=30000) as rq:
        pg.click(_F + "#d207-regen")
    benef = rq.value.post_data_json["manual"]["beneficiari"]
    _asteapta_rezultat(pg)
    patron.captura("d207_adaugat_la_generare")
    assert [(b["den"], b["stat"], str(b["baza"]), str(b["imp"])) for b in benef] == [("KUNDE GMBH", "DE", "10000", "1000")], benef
    assert pg.locator(_F + ".msg-eroare[data-camp='d207-den']").count() == 0 and pg.locator(_F + ".refuz-salvare").count() == 0


def test_def_653_statul_de_rezidenta_lista_cu_cautare(patron, firma_l13):
    """653 (clasele 85, 259). Pașii: D207, 2025 -> „Stat de rezidență”: se scrie „germ” în căutare -> lista păstrează Germania (DE), nu
    Franța; codurile fiscale spun de la început „completează măcar unul”. MUTAȚIA: căutarea scoasă -> Franța rămâne -> ROȘU."""
    _platitor(patron, firma_l13)
    pg = _continua_formular(patron, firma_l13, "d207", AN_D207)
    assert "Cod de identificare fiscală * — completează măcar unul" in _txt(pg, "#dec-d207-form")   # înainte de orice eroare
    pg.fill(_F + "#d207-stat-cauta", "germ")
    pg.dispatch_event(_F + "#d207-stat-cauta", "input")
    optiuni = pg.eval_on_selector_all(_F + "#d207-stat option", "os => os.filter(o => o.value).map(o => o.textContent)")
    patron.captura("d207_stat_cautat")
    assert "Germania (DE)" in optiuni and not [o for o in optiuni if "(FR)" in o], optiuni


def test_def_654_refuzul_vechi_dispare_la_urmatoarea_actiune(patron, firma_l13):
    """654. Pașii: firmă micro -> D710, trimestrul trecut -> „Generează D710” fără obligații: „D710 cere cel puțin o obligație corectată.”
    -> se alege codul obligației (121): refuzul vechi dispare (nu mai e despre ce e pe ecran). MUTAȚIA: refuzul nu mai iese -> ROȘU."""
    _platitor(patron, firma_l13, regim="micro")
    p = perioada_incheiata("trimestrial")
    pg = _continua_formular(patron, firma_l13, "d710", p.an, trim=p.trim)
    pg.click(_F + "#d710-regen")
    pg.wait_for_selector(_F + "#dec-refuz", timeout=60000)
    assert "cel puțin o obligație corectată" in _txt(pg, "#dec-refuz")
    pg.select_option(_F + "#d710-cod", "121")
    pg.wait_for_selector(_F + "#dec-refuz", state="detached", timeout=10000)
    patron.captura("d710_refuz_disparut")
    assert "cel puțin o obligație corectată" not in patron.fereastra()


# ── regimul de TVA: D311, D318, D398 ───────────────────────────────────────────────────────────────────────────────────────────────
def _optiune(pg, tip):
    """Opțiunea tipului în lista Declarațiilor („Alte declarații” deschisă, dacă e pliată): {dez, titlu, text}."""
    if pg.locator(_F + "#dec-alte").count() and pg.get_attribute(_F + "#dec-alte", "aria-expanded") != "true":
        pg.click(_F + "#dec-alte")
    loc = pg.locator(_F + "#dec-tip option[value='%s']" % tip)
    loc.wait_for(state="attached", timeout=10000)
    return loc.evaluate("o => ({dez: o.disabled, titlu: o.title, text: o.textContent})")


def test_def_650_d311_nu_se_datoreaza_la_platitor(patron, firma_l13):
    """650. Pașii: firmă plătitoare de TVA -> Declarații -> „Alte declarații”: D311 e inactivă, cu motivul „D311 nu se datorează — firma e
    înregistrată în scopuri de TVA, iar D311 o depune numai firma căreia i s-a anulat codul de TVA (CF art.324 alin.(10)).” (înainte:
    „D311 · lunar”, ca datorată). MUTAȚIA: regula scoasă -> D311 activă -> ROȘU."""
    _platitor(patron, firma_l13)
    pg = patron.pg
    patron.firma(firma_l13["nume"])
    _card(patron, "declaratii", _F + "#dec-tip")
    o = _optiune(pg, "d311")
    patron.captura("d311_platitor")
    assert o["dez"] and "D311 nu se datorează — firma e înregistrată în scopuri de TVA" in o["titlu"] and "CF art.324 alin.(10)" in o["titlu"], o


def test_def_635_d318_inactiva_la_neplatitor(patron, firma_l13):
    """635. Pașii: firmă neînregistrată în scopuri de TVA -> Declarații -> „Alte declarații”: D318 e inactivă, cu motivul (HG 1/2016 pct.73
    alin.(15) lit.c: ANAF nu înaintează cererea firmei care aplică scutirea întreprinderilor mici). MUTAȚIA: regula scoasă -> ROȘU."""
    _neplatitor(patron, firma_l13, art317=False)
    pg = patron.pg
    patron.firma(firma_l13["nume"])
    _card(patron, "declaratii", _F + "#dec-tip")
    o = _optiune(pg, "d318")
    patron.captura("d318_neplatitor")
    assert o["dez"] and "D318 nu se depune" in o["titlu"] and "HG 1/2016 pct.73 alin.(15) lit.c" in o["titlu"], o


def test_def_594_d398_texte_si_date_din_date_firma(patron, firma_l13):
    """594. Pașii: firmă neplătitoare înregistrată art.317 -> D398, trimestrul trecut -> „Continuă”: denumirea și codul de TVA vin din Date
    firmă (RO + CUI), fără refuz roșu înainte de orice acțiune, fără numele interne („msest”, „msid”, „e_int”, „harta de componente”) și
    fără „perioada se ia din selectorul de sus”. MUTAȚIA: denumirea nu mai vine din Date firmă -> ROȘU."""
    _neplatitor(patron, firma_l13)
    p = perioada_incheiata("trimestrial")
    pg = _continua_formular(patron, firma_l13, "d398", p.an, trim=p.trim)
    patron.captura("d398_formular")
    cui = sql("SELECT cui FROM public.tenants WHERE id = %s", (firma_l13["tenant_id"],))[0][0]
    assert pg.input_value(_F + "#d398-name") == firma_l13["nume"] and pg.input_value(_F + "#d398-vat") == "RO" + re.sub(r"\D", "", cui)
    t = patron.fereastra()
    for intern in ("msest", "msid", "e_int", "harta de componente", "selectorul de sus"):
        assert intern not in t, (intern, t[:2000])
    assert pg.locator(_F + ".dec-eroare, " + _F + "#dec-refuz").count() == 0


def test_def_595_d398_fara_inregistrare_oss_nu_se_genereaza(patron, firma_l13):
    """595. Pașii: firmă neplătitoare înregistrată art.317 -> D398 -> „Firma e înregistrată în regimul special OSS …?” „Nu” -> „Generează
    D398”: nu pleacă nicio cerere; lângă întrebare: „Firma nu e înregistrată în regimul special OSS, deci nu depune D398 (CF art.315
    alin.(3)).” MUTAȚIA: verificarea scoasă din ecran -> ROȘU."""
    _neplatitor(patron, firma_l13)
    p = perioada_incheiata("trimestrial")
    pg = _continua_formular(patron, firma_l13, "d398", p.an, trim=p.trim)
    cereri = []
    pg.on("request", lambda r: cereri.append(r.url) if r.url.endswith("/declaratii/d398/valideaza") else None)
    pg.select_option(_F + "#d398-oss", "false")
    pg.dispatch_event(_F + "#d398-oss", "change")
    pg.click(_F + "#d398-regen")
    pg.wait_for_selector(_F + ".msg-eroare[data-camp='d398-oss']", timeout=20000)
    patron.captura("d398_fara_oss")
    assert "Firma nu e înregistrată în regimul special OSS, deci nu depune D398 (CF art.315 alin.(3))." in \
        _txt(pg, ".msg-eroare[data-camp='d398-oss']")
    pg.wait_for_timeout(800)
    assert cereri == []


def _d318_pas2(patron, f, an=None):
    _platitor(patron, f)
    return _continua_formular(patron, f, "d318", an or AZI.year)


def test_def_636_d318_precompletat_din_date_firma(patron, firma_l13):
    """636. Pașii: firmă plătitoare -> D318 -> „Continuă”: CUI-ul, denumirea, adresa, IBAN-ul, titularul contului, declarantul și funcția lui,
    codul CAEN vin din Date firmă; moneda se alege din lista monedelor BNR (clasa 631), nu se scrie. MUTAȚIA: precompletarea CUI scoasă ->
    ROȘU."""
    pg = _d318_pas2(patron, firma_l13)
    patron.captura("d318_precompletat")
    cui = sql("SELECT cui FROM public.tenants WHERE id = %s", (firma_l13["tenant_id"],))[0][0]
    assert pg.input_value(_F + "#d318-cui") == re.sub(r"^RO", "", cui) and pg.input_value(_F + "#d318-soldenumire") == firma_l13["nume"]
    assert pg.input_value(_F + "#d318-iban") == "RO59BTRLRONCRT0C69TEST01" and pg.input_value(_F + "#d318-declarant") == "ION POPESCU"
    assert pg.input_value(_F + "#d318-functie") == "ADMINISTRATOR" and pg.input_value(_F + "#d318-nace") == "4711"
    monede = pg.eval_on_selector_all(_F + "#d318-cur option", "os => os.map(o => o.value)")
    assert pg.evaluate("() => document.querySelector('.fereastra:last-of-type #d318-cur').tagName") == "SELECT" and {"EUR", "HUF"} <= set(monede)


def _d318_completat(pg, cu_factura=True, luni=(7, 9), tva=27000):
    z = _F
    pg.fill(z + "#d318-an", str(AZI.year if AZI.month > luni[1] else AZI.year - 1))
    pg.dispatch_event(z + "#d318-an", "change")
    pg.uncheck(z + "#d318-annual")
    pg.wait_for_selector(z + "#d318-li", timeout=10000)
    pg.fill(z + "#d318-li", str(luni[0])); pg.dispatch_event(z + "#d318-li", "change")
    pg.fill(z + "#d318-ls", str(luni[1])); pg.dispatch_event(z + "#d318-ls", "change")
    pg.select_option(z + "#d318-tara", "HU")
    pg.select_option(z + "#d318-ownt", "A")
    pg.select_option(z + "#d318-cur", "HUF")
    pg.fill(z + "#d318-bic", "BTRLRO22")
    pg.fill(z + "#d318-solemail", "firma@proba.test")
    for sel in ("#d318-bic", "#d318-solemail", "#d318-tara", "#d318-ownt", "#d318-cur"):
        pg.dispatch_event(z + sel, "change")
    if cu_factura:
        an = pg.input_value(z + "#d318-an")
        pg.select_option(z + "#d318-fel", "achizitie")
        pg.fill(z + "#d318-fnr", "HU-77")
        pg.fill(z + "#d318-fdata", "15.%02d.%s" % (luni[0] + 1, an))
        pg.fill(z + "#d318-fbaza", "100000")
        pg.fill(z + "#d318-ftva", str(tva))
        pg.fill(z + "#d318-fded", str(tva))
        pg.fill(z + "#d318-ffz", "BUDAPEST KFT")
        pg.fill(z + "#d318-ffzstr", "Andrassy ut 1, Budapest")
        pg.select_option(z + "#d318-ffztara", "HU")
        pg.fill(z + "#d318-fcod", "1")
        pg.click(z + "#d318-add")
        pg.wait_for_selector(z + ".dec-d318-del", timeout=20000)


def test_def_637_d318_refuzul_numeste_numai_ce_lipseste(patron, firma_l13):
    """637. Pașii: D318 completată (perioada, CUI, IBAN, banca, moneda — cele din Date firmă venite completate), fără nicio factură ->
    „Generează D318”: lângă buton numai „Adaugă cel puțin o factură.”; nicio eroare pe perioadă, CUI sau IBAN (înainte: refuzul le cerea
    pe toate). MUTAȚIA: verificarea listei de facturi scoasă -> refuzul serverului -> ROȘU."""
    pg = _d318_pas2(patron, firma_l13)
    _d318_completat(pg, cu_factura=False)
    pg.click(_F + "#d318-regen")
    pg.wait_for_selector(_F + ".dec-regen-msg", timeout=20000)
    patron.captura("d318_fara_factura")
    assert _txt(pg, ".dec-regen-msg") == "Adaugă cel puțin o factură."
    assert pg.locator(_F + ".msg-eroare[data-camp]").count() == 0 and pg.locator(_F + "#dec-refuz").count() == 0


def test_def_638_d318_sub_pragul_minim_se_opreste(patron, firma_l13):
    """638. Pașii: D318 pe iulie–septembrie, o factură HUF cu TVA deductibil 27.000 HUF (~70 euro) -> „Generează D318”: nu se generează —
    „… sub pragul minim de 400 euro: HG 1/2016 pct.73 alin.(13) …”; titlul spune anul ales (nu „anul 2025” cu cererea pe alt an), fără
    „harta de componente”. MUTAȚIA: pragul de 400 euro pus 1 euro -> D318 trece -> ROȘU."""
    pg = _d318_pas2(patron, firma_l13)
    _d318_completat(pg)
    an = pg.input_value(_F + "#d318-an")
    pg.click(_F + "#d318-regen")
    _asteapta_rezultat(pg)
    patron.captura("d318_sub_prag")
    refuz = _txt(pg, "#dec-refuz")
    assert "sub pragul minim de 400 euro" in refuz and "HG 1/2016 pct.73 alin.(13)" in refuz, refuz   # pct.73 alin.(13)
    assert "harta de componente" not in patron.fereastra()
    assert pg.locator(_F + ".dec-ok").count() == 0 and an in refuz


# ── datorate din operațiile înregistrate: D301 / D390 la neplătitorul art.317 ─────────────────────────────────────────────────────
def _aic(patron, f, data, numar):
    # date-de-pornire: achiziția intracomunitară pe ruta formularului din Operațiuni (`POST achizitie-ic`, ca e2e_lot12_fisc3)
    _ok(_api(patron, "POST", "/tenants/%d/achizitie-ic" % f["tenant_id"], {
        "data": data.isoformat(), "valoare": 10000, "cota": 21, "cod_tva_furnizor": COD_IE, "numar": numar,
        "furnizor_nume": "FURNIZOR TEST UE", "tip": "bunuri", "cont_destinatie": "371", "descriere": "Marfa UE"}), "achiziția IC")


def _datorate(patron, f):
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "declaratii", _F + "#dec-tip")
    pg.wait_for_timeout(800)
    return [" ".join(t.split()) for t in pg.eval_on_selector_all(
        _F + "#dec-tip optgroup[label^='Datorate de firmă'] option", "os => os.map(o => o.textContent)")]


def test_def_538_d301_din_achizitia_intracomunitara_e_datorata(patron, firma_l13):
    """538. Pașii: firmă neplătitoare înregistrată art.317 -> achiziție intracomunitară azi (IE6388047V) -> Declarații: în „Datorate de
    firmă” apare D301 pe luna achiziției, cu termenul „25 a lunii următoare” (CF art.324 alin.(1): „până la data de 25 inclusiv a lunii
    următoare celei în care ia naștere exigibilitatea”), nu numai D100 / D390 / D406. MUTAȚIA: operațiile scoase din calcul -> ROȘU."""
    from core import scadente
    _neplatitor(patron, firma_l13)
    _aic(patron, firma_l13, AZI, "IE-L13-1")
    opt = _datorate(patron, firma_l13)
    patron.captura("datorate_d301")
    termen = scadente.scadenta_data("d301", AZI.year, luna=AZI.month)
    asteptat = "D301 · %02d/%d · termen de depunere %s" % (AZI.month, AZI.year, termen.strftime("%d.%m.%Y"))
    assert asteptat in opt, opt


def test_def_591_d301_depusa_nu_mai_e_datorata(patron, firma_l13):
    """591. Pașii: ca la 538, apoi D301 pe luna achiziției e depusă la ANAF -> Declarații: D301 nu mai e în „Datorate de firmă”.
    MUTAȚIA: depunerile nu mai scot obligația -> ROȘU."""
    _neplatitor(patron, firma_l13)
    _aic(patron, firma_l13, AZI, "IE-L13-2")
    assert [o for o in _datorate(patron, firma_l13) if o.startswith("D301 · %02d/%d" % (AZI.month, AZI.year))]
    # date-de-pornire: depunerea la ANAF a D301 pe luna achiziției (perioadă a firmei de probă, scoasă cu firma)
    sql("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, sursa, data_depunere, nr_depunere) "
        "VALUES (%s, %s, %s, 'd301', 'extern', now(), 1)", (firma_l13["tenant_id"], AZI.year, AZI.month))
    try:
        opt = _datorate(patron, firma_l13)
        patron.captura("datorate_d301_depusa")
        assert not [o for o in opt if o.startswith("D301 · %02d/%d" % (AZI.month, AZI.year))], opt
    finally:
        sql("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s AND tip = 'd301'", (firma_l13["tenant_id"],))


def test_def_592_d390_numai_pe_lunile_cu_operatiuni(patron, firma_l13):
    """592. Pașii: firmă neplătitoare înregistrată art.317, achiziție intracomunitară numai luna trecută -> Declarații: în „Datorate de
    firmă” D390 apare numai pe luna achiziției, niciodată pe luna în curs sau pe cele următoare, fără operațiuni (CF art.325 alin.(2): „pentru
    fiecare lună calendaristică în care ia naștere exigibilitatea”). MUTAȚIA: toate lunile anului socotite cu operațiuni -> ROȘU."""
    _neplatitor(patron, firma_l13)
    _aic(patron, firma_l13, LUNA.inceput.replace(day=12), "IE-L13-3")
    opt = _datorate(patron, firma_l13)
    patron.captura("datorate_d390")
    d390 = [o for o in opt if o.startswith("D390 · ")]
    assert all(o.startswith("D390 · %02d/%d " % (LUNA.luna, LUNA.an)) for o in d390), d390
    assert not [o for o in d390 if o.startswith("D390 · %02d/%d" % (AZI.month, AZI.year))], d390


def test_def_539_d301_furnizorul_fara_prefix_dublat(patron, firma_l13):
    """539. Pașii: firmă neplătitoare înregistrată art.317 -> achiziția intracomunitară de la IE6388047V (codul întreg, cum cere exemplul
    din formular), luna trecută -> Declarații -> D301, luna trecută -> „Continuă”: rândul operațiunii spune „furnizor IE6388047V …”, nu
    „IEIE6388047V”; codul e ținut o singură dată, fără prefix. MUTAȚIA: normalizarea scoasă -> „IEIE…” -> ROȘU."""
    _neplatitor(patron, firma_l13)
    _aic(patron, firma_l13, LUNA.inceput.replace(day=12), "IE-L13-4")
    pg = _pas1(patron, firma_l13, "d301", LUNA.an, LUNA.luna)
    pg.click(_F + "#dec-continua")
    pg.wait_for_selector(_F + "#dec-d301-op .dec-man-rand", timeout=90000)
    patron.captura("d301_furnizor")
    rand = _txt(pg, "#dec-d301-op .dec-man-rand")
    assert "furnizor IE6388047V" in rand and "IEIE" not in rand, rand
    cod = sql('SELECT partener_cod FROM "%s".d301_operatiuni' % firma_l13["schema"])
    assert cod == [("6388047V",)], cod


# ── navigarea: săgeata din pasul 2 ──────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_540_sageata_din_pasul_2_intoarce_la_pasul_1_cu_firma(patron, asistent, firma_l13):
    """540. Pașii (Ana, asistenta cu firma alocată): pagina cabinetului -> cardul „Declarații” -> firma -> D406, luna trecută -> „Continuă”
    (pasul 2) -> săgeata ←: pasul 1, cu firma, tipul și perioada alese (nu pagina principală, cu firma pierdută). MUTAȚIA: pasul 2 desenat
    pe loc, fără pas pe traseu -> săgeata închide Declarațiile -> ROȘU."""
    _platitor(patron, firma_l13)
    uid = sql("SELECT id FROM public.users WHERE email = 'asistent@prisma-cont.test'")[0][0]
    # date-de-pornire: firma alocată asistentei (ca la „Asistenți” -> firmele lui)
    sql("INSERT INTO public.user_tenants (user_id, tenant_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (uid, firma_l13["tenant_id"]))
    try:
        pg = asistent.pg
        asistent.acasa()
        pg.click("button.cab-card:has([data-cheie='declaratii'])")
        pg.wait_for_selector(_F + "#dec-firma", timeout=30000)
        pg.select_option(_F + "#dec-firma", str(firma_l13["tenant_id"]))
        pg.wait_for_selector(_F + "#dec-tip option[value='d406'], " + _F + "#dec-alte", state="attached", timeout=20000)
        alege_tipul(pg, "d406", zona=_F)
        alege_perioada(pg, LUNA.an, LUNA.luna, zona=_F)
        pg.click(_F + "#dec-continua")
        _asteapta_rezultat(pg)
        pg.click(_F + ".nav-inapoi")
        pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); return f && f.innerText.includes("
                             "'Pasul 1 din 3'); }", timeout=30000)
        asistent.captura("inapoi_pasul_1")
        assert pg.input_value(_F + "#dec-firma") == str(firma_l13["tenant_id"]) and pg.input_value(_F + "#dec-tip") == "d406"
    finally:
        sql("DELETE FROM public.user_tenants WHERE user_id = %s AND tenant_id = %s", (uid, firma_l13["tenant_id"]))


# ── 660: formularele înlocuite de Declarația unică ─────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def pfa_l13():
    for f in firma_noua("pfa"):
        yield f


def test_def_660_formularele_inlocuite_nu_se_ofera_nici_la_pfa(patron, pfa_l13):
    """660. Pașii: PFA -> Declarații -> „Alte declarații”: D200, D201, D220, D221, D223, D600 nu se oferă (Declarația unică D212 le-a
    înlocuit: CF art.122 alin.(1), art.130 alin.(4), art.107 alin.(2), art.125 alin.(4), art.151 alin.(1); art.120 abrogat de OUG 128/2024);
    D212 rămâne. MUTAȚIA: D600 pusă înapoi în dispecer -> ROȘU."""
    pregateste_firma(patron, pfa_l13, forma=False, regim_fiscal=None)
    pg = patron.pg
    patron.firma(pfa_l13["nume"])
    _card(patron, "declaratii", _F + "#dec-tip")
    if pg.locator(_F + "#dec-alte").count() and pg.get_attribute(_F + "#dec-alte", "aria-expanded") != "true":
        pg.click(_F + "#dec-alte")
    pg.wait_for_selector(_F + "#dec-tip option[value='d212']", state="attached", timeout=20000)
    tipuri = pg.eval_on_selector_all(_F + "#dec-tip option", "os => os.map(o => o.value)")
    patron.captura("pfa_fara_formulare_inlocuite")
    assert not {"d200", "d201", "d220", "d221", "d223", "d600"} & set(tipuri), tipuri


# ── C19: rectificativa D112 numai la cerere, după diferențe ──────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_c19_d112():
    from conftest import _scoate_firmele_e2e
    from e2e_lot11_s9 import _firma_cu_salariat
    f = _firma_cu_salariat("L13C19")
    try:
        yield f
    finally:
        sql("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s AND tip = 'd112'", (f["tenant_id"],))
        _scoate_firmele_e2e(f["tenant_id"])


def test_def_c19_rectificativa_d112_numai_la_cerere_dupa_diferente(patron, firma_c19_d112):
    """C19 (decizia Costin: „diferențele dinaintea rectificativei se extind la D112 acum”). Pașii: firmă cu un salariat -> D112 pe luna
    trecută (validată de DUK) -> declarația depusă la ANAF purta altă sumă la prima obligație -> Declarații -> D112, luna trecută ->
    „Continuă”: „D112 pe LL/AAAA e deja depusă … O rectificativă se completează integral … (OPANAF 605/2026 anexa nr.2 pct.2.4)”, tabelul
    diferențelor (Obligații de plată — obligația cu codul ei — A_datorat: depus → nou), nimic generat, nimic în coadă -> „Generează
    declarația rectificativă →”: „Rectificativă la …”, validată de DUK. MUTAȚIA: poarta scoasă pentru D112 -> se generează direct -> ROȘU."""
    from e2e_bloc_d import LUNA_TRECUTA
    from e2e_lot11_s9 import _d112_xml
    f = firma_c19_d112
    pg = patron.pg
    _d112_xml(patron, f)   # pasul 2 al D112 inițiale, „fără erori” la DUKIntegrator
    xml0 = pg.locator(_F + "details.dec-xml:has(summary:text('Vezi XML-ul generat')) pre.dec-xml-pre").text_content()
    m = re.search(r'A_codOblig="(\d+)"[^>]*A_datorat="(\d+)"', xml0)
    assert m, xml0[:1500]
    cod, suma = m.group(1), int(m.group(2))
    depus = xml0.replace(m.group(0), m.group(0)[:-len('"%d"' % suma)] + '"%d"' % (suma + 7), 1)
    # date-de-pornire: D112 depusă la ANAF cu prima obligație mai mare cu 7 lei (o depunere nu se poate produce din plasă)
    sql("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, sursa, data_depunere, nr_depunere) "
        "VALUES (%s, %s, %s, 'd112', %s, 'extern', now(), 1)", (f["tenant_id"], LUNA_TRECUTA.year, LUNA_TRECUTA.month, depus))
    coada0 = sql("SELECT count(*) FROM public.declaratii_coada WHERE tenant_id = %s AND tip = 'd112'", (f["tenant_id"],))[0][0]
    pg2 = _pas1(patron, f, "d112", LUNA_TRECUTA.year, LUNA_TRECUTA.month)
    pg2.click(_F + "#dec-continua")
    _asteapta_rezultat(pg2)
    patron.captura("c19_d112_diferente")
    caseta = _txt(pg2, "#dec-rect-depusa")
    assert "D112 pe %02d/%d e deja depusă" % (LUNA_TRECUTA.month, LUNA_TRECUTA.year) in caseta and "OPANAF 605/2026 anexa nr.2 pct.2.4" in caseta
    randuri = pg2.eval_on_selector_all(_F + "#dec-rect-diferente tbody tr",
                                       "trs => trs.map(t => [...t.cells].map(c => c.innerText.replace(/\\s+/g, ' ').trim()))")
    assert ["Obligații de plată (secțiunea A)", "obligația cu codul %s" % cod, "A_datorat", str(suma + 7), str(suma)] in randuri, randuri
    assert pg2.locator(_F + "#dec-trimite").count() == 0
    assert sql("SELECT count(*) FROM public.declaratii_coada WHERE tenant_id = %s AND tip = 'd112'", (f["tenant_id"],))[0][0] == coada0
    pg2.click(_F + "#dec-rect-genereaza")
    pg2.wait_for_selector(_F + "#dec-rectificativa", timeout=120000)
    patron.captura("c19_d112_rectificativa")
    assert _txt(pg2, "#dec-rectificativa").startswith("Rectificativă la declarația depusă în afara iConta.eu")
    assert "Validat cu DUKIntegrator" in _txt(pg2, ".dec-ok"), patron.fereastra()[:3000]
