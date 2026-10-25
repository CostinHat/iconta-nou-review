# -*- coding: utf-8 -*-
"""Lotul 12, comanda 12.2 (Costin 24.10.2026, verbatim în DECIZII „Comanda 12.2”), pachetul `fact2` — factura de furnizor, mesajele de
după emitere, livrarea intracomunitară din Operațiuni, refuzul și verificarea CUI din „Emite factură”:

  * C73.1 (grav, pct.6) — aceeași factură de furnizor (furnizor + număr) se oprește pe toate căile: a doua „Achiziție necorporală” cu
    LIC-73 de la 14399840 se refuză, cu factura existentă numită;
  * 443.1 (pct.2) — mesajul după emitere / stornare spune seria și numărul ca în Istoric („E2EA nr. 1”), nu lipite („E2EA1”);
  * C78.1 (pct.7) — Operațiuni › „Livrare/prestare intracomunitară”: rezultatul VIES (valid / invalid, numele firmei) se vede sub câmp
    înainte de „Generează nota”; confirmarea arată nota o singură dată;
  * 304 (redeschisă) — după „Emite” refuzat pentru clientul român cu „livrare intracomunitară”, tastarea altui CUI scoate tot refuzul:
    erorile, caseta „NU s-a salvat.” și fereastra refuzului („țara clientului: RO”);
  * C166 — răspunsul negativ al verificării CUI („CUI negăsit la ANAF”, cod invalid în VIES) rămâne în ciorna formularului.

DATE DE PORNIRE fără ecran (declarate, regula lui 429): firmele sunt NOI (`conftest.firma_noua`), pregătite pe rutele ecranelor
(`e2e_bloc_a.pregateste_firma`); stocul lui 304 ca în `e2e_bloc_c.firma_cv`; VIES e serviciu extern: răspunsul lui e servit de plasă
(`<ICONTA_ANAF_SIMULAT>/vies.json`, ca în `e2e_lot11_x`) sau de probă (`page.route`); ANAF la „Verifică” (C166), de probă. CUI-urile
14399840 (DANTE INTERNATIONAL SA) și 18547290: cifra de control verificată cu algoritmul din CLAUDE.md
(`core/test_lot12_fact2_c73_dublura.py::test_cuiurile_de_proba_au_cifra_de_control_buna`).

Temei: OMFP 2634/2015 anexa 1 pct.58 lit.c („fiecare dată înregistrată în contabilitate trebuie să se regăsească în conținutul unui
document”) — C73.1; CF art.319 alin.(20) lit.a („numărul de ordine, în baza uneia sau a mai multor serii”) — 443.1; CF art.278 alin.(2)
(locul prestării către o persoană impozabilă e locul unde ea își are sediul) — C78.1. 304, C166: N/A — reguli de produs (CLAUDE.md §9)."""
import json
import os

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import AZI, PRODUS, SERIE, _deschide_emiterea, _deschide_factura, pregateste_firma
from e2e_bloc_c import firma_cv  # noqa: F401 — fixture (304: articol de stoc)

CUI_DANTE = "14399840"
CLIENT = {"#em-cui": "18547290", "#em-nume": "Client Fact2 Lot12 SRL", "#em-adresa": "Str. Probei 2", "#em-oras": "Sector 1"}
COD_VIES_VALID, COD_VIES_INVALID = "DE811907980", "DE999999990"


@pytest.fixture()
def firma_f2(patron):
    for f in firma_noua():
        pregateste_firma(patron, f)
        try:
            yield f
        finally:
            sql("DELETE FROM public.ciorne_formular WHERE tenant_id = %s", (f["tenant_id"],))


def _vies_simulat(coduri):
    """Răspunsurile VIES servite de plasă (aceeași formă ca `e2e_lot11_x`), pentru verificarea de pe ecran și pentru nota livrării."""
    d = os.environ.get("ICONTA_ANAF_SIMULAT")
    if not d:
        return
    os.makedirs(d, exist_ok=True)
    cale = os.path.join(d, "vies.json")
    vies = json.load(open(cale, encoding="utf-8")) if os.path.exists(cale) else {}
    vies.update(coduri)
    with open(cale, "w", encoding="utf-8") as f:
        json.dump(vies, f, ensure_ascii=False)


def _operatiune(patron, firma, cheie):
    patron.firma(firma["nume"])
    pg = patron.pg
    pg.click("#fa-operatiuni")
    pg.wait_for_selector("[data-op]", timeout=20000)
    pg.locator("button[data-op='%s']" % cheie).click()
    pg.wait_for_selector("#op-trimite", timeout=10000)
    return pg


# ================================================================ C73.1 — dublura facturii de furnizor
def _necorporala(patron, firma, numar):
    """Operațiuni -> „Achiziție necorporală” -> licența LIC de la DANTE (1.000 lei + 21%) -> „Generează nota”."""
    pg = _operatiune(patron, firma, "necorporala")
    pg.fill("#op-data", AZI.isoformat())
    pg.fill("#op-denumire", "Licență program contabilitate")
    pg.fill("#op-valoare", "1000")
    pg.select_option("#op-tip", "licenta")
    pg.fill("#op-dnf_luni", "12")
    pg.fill("#op-furnizor_nume", "DANTE INTERNATIONAL SA")
    pg.fill("#op-furnizor_cui", CUI_DANTE)
    pg.fill("#op-numar", numar)
    pg.fill("#op-cota", "21")
    pg.click("#op-trimite")
    return pg


def _note_205(firma):
    return sql('SELECT count(*) FROM "%s".inregistrari_linii WHERE cont_debit = \'205\'' % firma["schema"])[0][0]


def test_def_c73_1_a_doua_achizitie_necorporala_cu_aceeasi_factura_se_refuza(patron, firma_f2):
    """C73.1. Pașii lui Costin: Operațiuni -> „Achiziție necorporală”, licența cu factura LIC-73 de la 14399840 (1.000 + 210) -> „Generează
    nota”: nota 205 = 404 / 4426 = 404 -> aceeași factură a doua oară (scrisă „LIC 73”): refuzul spune că factura LIC-73 de la DANTE e deja
    înregistrată (data, totalul 1.210,00 lei); nicio a doua notă 205, nicio a doua factură.
    MUTAȚIA: core/facturi_api.py, refuzul din `creeaza_factura` scos -> a doua notă 205 -> ROȘU."""
    pg = _necorporala(patron, firma_f2, "LIC-73")
    pg.wait_for_selector("#op-mesaj .caseta-ok", timeout=30000)
    assert _note_205(firma_f2) == 1
    pg = _necorporala(patron, firma_f2, "LIC 73")
    pg.wait_for_function("() => (document.querySelector('#op-mesaj') || {innerText: ''}).innerText.includes('e deja înregistrată')",
                         timeout=30000)
    patron.captura("a_doua_refuzata")
    t = " ".join(pg.inner_text("#op-mesaj").split())
    assert "Factura LIC-73 de la DANTE INTERNATIONAL SA e deja înregistrată: factura LIC-73 din %s, 1.210,00 lei." % AZI.strftime(
        "%d.%m.%Y") in t, t   # AZI-dat-de-test (data facturii scrisă de test în #op-data)
    # OMFP 2634/2015 pct.58 lit.c: un document, o înregistrare — imobilizarea și TVA-ul de dedus nu se dublează
    assert _note_205(firma_f2) == 1
    assert sql('SELECT count(*) FROM "%s".facturi WHERE directie = \'primita\'' % firma_f2["schema"])[0][0] == 1


# ================================================================ 443.1 — seria și numărul în mesajele de după emitere
def _completeaza(pg):
    for sel, v in CLIENT.items():
        pg.fill(sel, v)
    pg.select_option("#em-judet", "B")
    pg.fill("#em-l0-descriere", PRODUS)
    pg.wait_for_function("() => document.querySelector('#em-l0-pret_unitar').value !== ''", timeout=20000)
    pg.fill("#em-l0-cantitate", "1")
    pg.fill("#em-l0-pret_unitar", "500")
    pg.wait_for_function("() => document.querySelector('#em-l0-cota').value === '21'", timeout=20000)


def test_def_443_1_mesajul_dupa_emitere_si_stornare_spune_seria_si_numarul(patron, firma_f2):
    """443.1. Pașii: Emite factură (seria E2EA) -> client, 1 × 500 lei -> „Emite factură”: mesajul spune „Factura E2EA nr. <n> emisă”, nu
    „E2EA<n>” -> detaliul facturii -> „Stornează” -> „Confirm stornarea”: „Storno creat: E2EA nr. <m>”, ca în Istoric.
    MUTAȚIA: static/js/ecrane/emitere_ecran.js, mesajul înapoi pe `r.numar` -> „Factura E2EA1 emisă” -> ROȘU."""
    from core.pdf_util import serie_nr
    pg = patron.pg
    _deschide_emiterea(patron, firma_f2["nume"])
    _completeaza(pg)
    pg.click("#em-emite")
    pg.wait_for_selector("#em-rezultat.em-emisa", timeout=60000)
    fid, serie, numar = sql('SELECT id, serie, numar FROM "%s".facturi ORDER BY id DESC LIMIT 1' % firma_f2["schema"])[0]
    assert serie == SERIE and numar.startswith(SERIE), (serie, numar)
    rez = " ".join(pg.inner_text("#em-rezultat").split())
    patron.captura("emisa")
    # CF art.319 alin.(20) lit.a: seria și numărul de ordine — afișate separat, ca în Istoric
    assert rez.startswith("✓ Factura %s emisă" % serie_nr(serie, numar)) and numar not in rez, rez
    _deschide_factura(patron, firma_f2, fid)
    pg.click("#fd-storno")
    pg.wait_for_selector("#fd-storno-ok", timeout=10000)
    pg.click("#fd-storno-ok")
    pg.wait_for_function("() => ((document.querySelector('#fd-storno-rez') || {}).textContent || '').includes('Storno creat')", timeout=30000)
    s_serie, s_numar = sql('SELECT serie, numar FROM "%s".facturi WHERE storno_din_id = %%s' % firma_f2["schema"], (fid,))[0]
    t = " ".join(pg.inner_text("#fd-storno-rez").split())
    patron.captura("stornata")
    assert t.startswith("✓ Storno creat: %s" % serie_nr(s_serie, s_numar)) and s_numar not in t, t


# ================================================================ C78.1 — VIES înainte de generare, nota o singură dată
def test_def_c78_1_vies_se_vede_inainte_de_generare_iar_nota_o_singura_data(patron, firma_f2):
    """C78.1. Pașii: Operațiuni -> „Livrare/prestare intracomunitară (VIES live)” -> codul unui client invalid în VIES, ieșire din câmp:
    sub câmp „Cod TVA invalid în VIES …” -> codul DE811907980: „valid în VIES · DE · KUNDE E2E GMBH” — înainte de „Generează nota” ->
    Servicii, 1.000 lei, cont 704 -> „Generează nota”: confirmarea arată nota 4111 = 704 · 1.000,00 lei O SINGURĂ dată și clientul din VIES.
    MUTAȚIA: static/js/ecrane/operatiuni_ecran.js, linia de stare VIES scoasă -> nimic sub câmp -> ROȘU."""
    from e2e_bloc_a import _api, _ok, _profil
    p = _profil(firma_f2)
    p["metoda_stoc"] = "global_valoric"
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % firma_f2["tenant_id"], p), "Date firmă (stoc global-valoric)")
    _vies_simulat({COD_VIES_VALID: {"valid": True, "nume": "KUNDE E2E GMBH", "adresa": "Berlin", "eroare": None},
                   COD_VIES_INVALID: {"valid": False, "nume": "", "adresa": "", "eroare": None}})
    pg = _operatiune(patron, firma_f2, "vanzare_ic")
    pg.fill("#op-cod_tva_client", COD_VIES_INVALID)
    pg.dispatch_event("#op-cod_tva_client", "change")
    pg.wait_for_function("() => document.querySelector('#op-cod_tva_client-vies').innerText.startsWith('Cod TVA invalid în VIES')",
                         timeout=30000)
    patron.captura("vies_invalid")
    pg.fill("#op-cod_tva_client", COD_VIES_VALID)
    assert pg.inner_text("#op-cod_tva_client-vies") == ""   # răspunsul codului vechi pleacă la tastare
    pg.dispatch_event("#op-cod_tva_client", "change")
    pg.wait_for_function("() => document.querySelector('#op-cod_tva_client-vies').innerText.startsWith('valid în VIES')", timeout=30000)
    assert pg.inner_text("#op-cod_tva_client-vies") == "valid în VIES · DE · KUNDE E2E GMBH"
    patron.captura("vies_valid_inainte_de_generare")
    pg.fill("#op-data", AZI.isoformat())
    pg.fill("#op-valoare", "1000")
    pg.select_option("#op-tip", "servicii")
    pg.fill("#op-cont_venit", "704")
    pg.fill("#op-descriere", "Servicii Fact2 C78")
    pg.click("#op-trimite")
    pg.wait_for_selector("#op-mesaj .caseta-ok", timeout=30000)
    patron.captura("confirmarea")
    t = " ".join(pg.inner_text("#op-mesaj .caseta-ok").split())
    # CF art.278 alin.(2): prestarea către persoana impozabilă din alt stat membru — nota 4111 = 704, fără TVA
    assert t.count("4111 = 704") == 1, t
    assert "Client: KUNDE E2E GMBH, cod %s valid în VIES." % COD_VIES_VALID in t, t


# ================================================================ 304 — refuzul clientului vechi dispare la tastarea altui client
def test_def_304_refuzul_clientului_roman_dispare_la_tastarea_altui_cui(patron, firma_cv):  # noqa: F811 — fixtura importată
    """304 (redeschisă, 24.10.2026). Pașii lui Costin: Emite factură -> client român (DANTE), articolul din stoc, 0%, „livrare
    intracomunitară” -> „Emite”: refuzul „țara clientului: RO” -> se TASTEAZĂ alt CUI (IE9999999ZZ), fără a ieși din câmp: nu mai rămâne pe
    ecran nicio urmă a refuzului — nici eroarea liniei, nici caseta „NU s-a salvat.”, nici fereastra refuzului („Am înțeles”).
    MUTAȚIA: static/js/ecrane/emitere_ecran.js, curățarea la tastarea CUI-ului scoasă -> caseta rămâne -> ROȘU."""
    pregateste_firma(patron, firma_cv)
    _deschide_emiterea(patron, firma_cv["nume"])
    pg = patron.pg
    pg.fill("#em-cui", CUI_DANTE)
    pg.fill("#em-nume", "DANTE INTERNATIONAL SA")
    pg.select_option("#em-l0-articol", label=pg.locator("#em-l0-articol option", has_text=firma_cv["marfa"]).first.inner_text())
    pg.fill("#em-l0-cantitate", "1")
    pg.fill("#em-l0-pret_unitar", "10")
    pg.select_option("#em-l0-cota", "0")
    pg.wait_for_selector("#em-l0-categorie", state="visible", timeout=10000)
    pg.select_option("#em-l0-categorie", "livrare_ic")
    pg.click("#em-emite")
    urme = """() => [...document.querySelectorAll('.msg-eroare, .refuz-salvare, #refuz-nevazut')]
        .filter((m) => m.getClientRects().length > 0 && m.innerText.includes('țara clientului: RO')).length"""
    pg.wait_for_function(urme + " > 0", timeout=30000)
    pg.wait_for_timeout(1200)   # și fereastra refuzului, dacă vine (api.js o pune după 0,7 s)
    patron.captura("refuzul")
    pg.fill("#em-cui", "IE9999999ZZ")   # tastare, fără ieșire din câmp (fără „change”)
    pg.wait_for_timeout(300)
    patron.captura("dupa_tastarea_altui_cui")
    assert pg.evaluate(urme) == 0, pg.inner_text(".fereastra:last-of-type")
    assert pg.locator(".fereastra:last-of-type .refuz-salvare").count() == 0


# ================================================================ C166 — răspunsul negativ al verificării rămâne în ciornă
def test_def_c166_raspunsul_negativ_al_verificarii_cui_ramane_la_revenire(patron, firma_f2):
    """C166. Pașii: Emite factură -> CUI 18547290 -> „Verifică”: ANAF răspunde „CUI negăsit” -> fereastra se închide imediat -> „Emite
    factură” din nou: factura începută e păstrată, iar sub CUI scrie tot „CUI negăsit la ANAF”. La fel codul invalid în VIES.
    MUTAȚIA: static/js/ecrane/emitere_ecran.js, salvarea în ciornă a lui „CUI negăsit” scoasă -> la revenire nu mai scrie nimic -> ROȘU."""
    pg = patron.pg
    pg.route("**/verifica-cui/**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps({"gasit": False})))
    pg.route("**/verifica-vies**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(
        {"valid": False, "nume": "", "adresa": "", "tara": "IE", "eroare": None})))
    try:
        for cod, raspuns in (("18547290", "CUI negăsit la ANAF"),
                             ("IE9999999ZZ", "cod TVA invalid în VIES — scutirea intracomunitară nu se aplică")):
            _deschide_emiterea(patron, firma_f2["nume"])
            pg.fill("#em-cui", cod)
            pg.click("#em-verifica")
            pg.wait_for_function("(t) => document.querySelector('#em-cui-stare').innerText === t", arg=raspuns, timeout=20000)
            pg.click(".fereastra:last-of-type .nav-x")                     # pleacă imediat după răspuns
            pg.wait_for_selector("#em-cui", state="detached", timeout=10000)
            _deschide_emiterea(patron, firma_f2["nume"])
            pg.wait_for_function("() => (document.querySelector('#em-ciorna') || {innerText: ''}).innerText.includes('a fost păstrată')",
                                 timeout=15000)
            patron.captura("revenire_" + cod)
            assert pg.input_value("#em-cui") == cod
            assert pg.inner_text("#em-cui-stare") == raspuns, pg.inner_text("#em-cui-stare")
            pg.click("#em-renunta")
            pg.locator("button", has_text="Da, renunț la factură").click()
            pg.wait_for_timeout(800)
            pg.click(".fereastra:last-of-type .nav-x")
    finally:
        pg.unroute("**/verifica-cui/**")
        pg.unroute("**/verifica-vies**")
