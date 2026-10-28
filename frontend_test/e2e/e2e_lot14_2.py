# -*- coding: utf-8 -*-
"""Lotul 14, comanda Costin 14.2 (verbatim în DECIZII „Comanda 14.2”) — probe de capăt la capăt, în browser, pe ecranele reale:

  * 715  — cererile de pornire ale ecranelor (drepturi, semafor, coada…) nu sunt „acțiuni”: nici în Fișa cabinetului, nici în alerta de acces anormal;
  * 712  — „Țara partenerului” urmează codul fiscal al clientului: nepotrivirea se spune chiar la alegerea țării, iar emiterea se oprește cu motiv;
  * 527.1 — la preluare, soldul de pe 117 (rezultat reportat) fără analitic se pune pe analiticul ales (1171 / 1172 / 1174), cu întrebare pe ecran;
  * 559.1 — Portal, „Cifrele firmei”: cifra mare e contabilitatea (4111 / 401), facturile deschise sunt detaliul, fără explicații pentru contabil;
  * 708  — formularul de autentificare are atributele standard (username / current-password), formularele care nu sunt de autentificare nu le au.

(595.1 — D398 gri — e probat în `e2e_lot13_oss.py::test_def_595_oss_se_alege_in_date_firma`; 714 — TVA la încasare pe achiziții — în
`core/test_lot14_2_714_tva_incasare_achizitii.py`, pe schemă sintetică, fiindcă refuzul stă pe ruta Operațiunilor.)

Firmele sunt NOI (`firma_noua`), cabinetul probei 715 e sintetic. Mutațiile: `mut_lot14_2.json`."""
import contextlib
import datetime as _dt
import re
import sys
import os
import time

import pytest

from conftest import BAZA, Ecran, _ecran, firma_noua, sql

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_bloc_a import _api, _deschide_emiterea, _ok, pregateste_firma   # noqa: E402
from e2e_bloc_e import _nota   # noqa: E402
from e2e_lot12_start import _scoate_contul   # noqa: E402
from e2e_lot13_admin import SUPERADMIN, _numai_cabinetul, _panou, cabinet_645   # noqa: E402,F401 — cabinet_645 e fixtură

AZI = _dt.date.today()
_F = ".fereastra:last-of-type "
ecran_cont = contextlib.contextmanager(_ecran)


# ── 715 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_715_cererile_automate_ale_ecranelor_nu_sunt_actiuni(browser, request, cabinet_645):
    """715. Pașii: un cabinet nou deschide aplicația (ecranul de pornire face singur zeci de cereri: drepturi, semafor, coada, termene…) -> în
    jurnal cererile există, (regula „automat” se aplică la citire) -> alerta de acces anormal, cu pragul coborât la o singură acțiune, NU numește cabinetul pentru
    ele -> superadminul: Panou Admin › Activitate › Fișa cabinetului: niciun grup „drepturi” / „semafor” din cererile automate. Înainte: Fișa
    număra „GET /eu/drepturi (29)”, iar alerta pleca pe 394 de „acțiuni”. MUTAȚIA: `este_automata` întoarce mereu False -> ROȘU."""
    from conftest import _db
    from core import alerta_acces
    cab = cabinet_645
    with ecran_cont(browser, request, cab["email"]) as c:
        c.pg.goto(BAZA + "/", wait_until="domcontentloaded")
        c.pg.wait_for_selector(".cab-grila", timeout=30000)
        c.pg.wait_for_timeout(1500)
        c.captura("ecranul_de_pornire")
    from core import audit_automat
    automate = sql("SELECT count(*) FROM public.audit_log WHERE user_id = %s AND actiune = ANY(%s)", (cab["uid"], list(audit_automat.EXACTE)))[0][0]
    toate = sql("SELECT count(*) FROM public.audit_log WHERE user_id = %s", (cab["uid"],))[0][0]
    assert automate >= 1 and toate >= automate, (automate, toate)
    with _db().get_conn() as conn:
        semnalati = {u["user_id"]: u for u in alerta_acces.detecteaza(conn, 10, 8, 1)}   # pragul: o singură acțiune
    assert cab["uid"] not in semnalati or semnalati[cab["uid"]]["actiuni"] <= toate - automate, semnalati.get(cab["uid"])
    with ecran_cont(browser, request, SUPERADMIN) as sa:
        pg = sa.pg
        _numai_cabinetul(pg, cab["id"])
        _panou(sa, "activitate")
        rand = pg.locator(".pf-frand[data-cabinet='%d']" % cab["id"])
        rand.wait_for(timeout=60000)
        rand.locator("[data-fisa]").click()
        pg.wait_for_selector("#ac-detaliu", timeout=30000)
        pg.wait_for_timeout(500)
        text = " ".join(pg.inner_text(".fereastra:last-of-type").split())
        sa.captura("fisa_cabinetului")
        assert "drepturi" not in text.lower() and "semafor" not in text.lower(), text
        grupe = pg.eval_on_selector_all(_F + "[data-grup]", "els => els.map(e => e.innerText)")
        assert not [g for g in grupe if re.search(r"drepturi|semafor|patru|coada|termene", g, re.I)], grupe


# ── 712 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_712():
    for f in firma_noua():
        yield f


def test_def_712_tara_urmeaza_codul_fiscal_al_clientului(patron, firma_712):
    """712. Pașii: Emite factură -> client cu codul „RO14399840” (DANTE INTERNATIONAL): țara se pune România -> o schimb cu mâna în Irlanda:
    chiar atunci apare motivul („nu se potrivește cu codul fiscal … care e al țării RO”); „Emite factură” cu țara Irlanda: refuz cu același
    motiv, nicio factură nouă. Înapoi la România -> motivul dispare. Înainte: țara se putea schimba fără niciun semnal, cu localitatea
    „Sector 2 Mun. București” păstrată. MUTAȚIA: verificarea scoasă din `facturi_api.emite_factura` -> factura se emite cu țara Irlanda -> ROȘU."""
    f = firma_712
    pregateste_firma(patron, f)
    s = f["schema"]
    inainte = sql('SELECT count(*) FROM "%s".facturi' % s)[0][0]
    _deschide_emiterea(patron, f["nume"])
    pg = patron.pg
    pg.fill("#em-cui", "RO14399840")
    pg.dispatch_event("#em-cui", "change")
    pg.wait_for_function("() => document.querySelector('#em-tara').value === 'RO'", timeout=10000)
    pg.fill("#em-nume", "DANTE INTERNATIONAL SA")
    pg.select_option("#em-tara", "IE")
    pg.wait_for_function("() => document.querySelector('#em-cui-stare').innerText.includes('nu se potrivește')", timeout=10000)
    motiv = " ".join(pg.inner_text("#em-cui-stare").split())
    patron.captura("tara_nepotrivita")
    assert "RO14399840" in motiv and "care e al țării RO" in motiv and "Alege țara RO" in motiv, motiv
    pg.fill("#em-adresa", "Str. Proba 1")
    pg.fill("#em-oras", "Sector 2 Mun. București")
    pg.fill("#em-data", AZI.isoformat())
    pg.fill("#em-l0-descriere", "Servicii de consultanta")
    pg.wait_for_selector("#em-l0-cota", timeout=20000)
    pg.select_option("#em-l0-cota", "21")   # fără cotă emiterea se oprește oricum; cu ea, numai refuzul țării o oprește
    pg.fill("#em-l0-cantitate", "1")
    pg.fill("#em-l0-pret_unitar", "100")
    pg.fill("#em-l0-um", "ora")
    pg.wait_for_function("() => !document.querySelector('#em-emite').disabled", timeout=20000)
    pg.click("#em-emite")
    pg.wait_for_function("() => document.body.innerText.includes('nu se potrivește cu codul fiscal')", timeout=60000)
    patron.captura("emitere_refuzata")
    assert sql('SELECT count(*) FROM "%s".facturi' % s)[0][0] == inainte, "factura s-a emis cu țara nepotrivită"
    pg.select_option("#em-tara", "RO")
    pg.wait_for_function("() => !document.querySelector('#em-cui-stare').innerText.includes('nu se potrivește')", timeout=10000)


# ── 527.1 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
BALANTA_117 = (
    "Balanţă de verificare analitică;;;;;;;;\n"
    "SC Firmă Probă SRL;;;;;;;;\n"
    "Perioada: 01.01.2026 - 30.09.2026;;;;;;;;\n"
    "Simbol cont;Denumirea contului;Solduri iniţiale an;;Total sume;;Solduri finale;;\n"
    ";;Debit;Credit;Debit;Credit;Debit;Credit\n"
    "117;Rezultatul reportat;0;14000;0;14000;0;14000\n"
    "5121;Conturi la bănci;14000;0;14000;0;14000;0\n"
    "TOTAL GENERAL;;14000;14000;14000;14000;14000;14000\n"
)


@pytest.fixture()
def firma_527():
    for f in firma_noua():
        yield f


def test_def_527_1_preluarea_pune_rezultatul_reportat_pe_analiticul_ales(patron, firma_527):
    """527.1. Pașii: Import date › Solduri inițiale, balanța cu 117 „Rezultatul reportat” 14.000 lei fără analitic -> ecranul întreabă „Rezultatul
    reportat se preia pe” (nimic ales) -> „Salvează soldurile” fără alegere: refuz lângă câmp, nimic scris -> 1171 -> salvat: în evidență
    soldul stă pe 1171, nu pe 117. MUTAȚIA: `cere_analitic_117` întoarce False -> soldul rămâne pe 117 -> ROȘU."""
    from e2e_import_saga import ANTET_PROBA, _incarca, _pas
    from e2e_lot12_migr import confirma_firma_fisierului
    from core.test_import_saga import _cp1250
    f = firma_527
    pg = patron.pg
    _pas(patron, f, "Solduri ini")
    _incarca(patron, "balanta_117.csv", _cp1250(BALANTA_117), "#mig-salveaza-sold")
    pg.wait_for_selector("#mig-analitic-117", timeout=10000)
    assert pg.input_value("#mig-analitic-117") == "", "analiticul apare ales fără ca omul să-l fi ales"
    optiuni = pg.eval_on_selector_all("#mig-analitic-117 option", "os => os.map(o => o.value).filter(Boolean)")
    assert optiuni == ["1171", "1172", "1174"], optiuni
    patron.captura("intrebare_analitic")
    pg.fill("#mig-data-bal", "2026-09-30")
    pg.click("#mig-salveaza-sold")
    confirma_firma_fisierului(pg, ANTET_PROBA)
    pg.wait_for_selector('.msg-eroare[data-camp="mig-analitic-117"]', timeout=20000)
    assert "alege pe ce analitic se preia" in pg.inner_text('.msg-eroare[data-camp="mig-analitic-117"]')
    assert sql('SELECT count(*) FROM "%s".solduri_initiale' % f["schema"])[0][0] == 0
    patron.captura("fara_alegere")
    pg.select_option("#mig-analitic-117", "1171")
    pg.click("#mig-salveaza-sold")
    confirma_firma_fisierului(pg, ANTET_PROBA)   # [599] întrebarea firmei fișierului se pune la fiecare salvare
    pg.wait_for_function("() => document.body.innerText.includes('Rezultatul reportat s-a preluat pe 1171.')", timeout=30000)
    patron.captura("salvat_pe_1171")
    assert sql('SELECT cont, sold_creditor FROM "%s".solduri_initiale WHERE sold_creditor > 0' % f["schema"]) == [("1171", 14000)]


# ── 559.1 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_559_1():
    for f in firma_noua():
        yield f


def test_def_559_1_cifra_mare_e_ce_arata_contabilitatea(patron, firma_559_1, browser, request):
    """559.1 (decizie Costin 14.2). Pașii: firma cu 4111 = 4.468,24 lei și 401 = 3.000,00 lei din note validate, fără nicio factură deschisă -> clientul:
    „Cifrele firmei”: „De încasat de la clienți” 4.468,24 lei, „De plătit către furnizori” 3.000,00 lei (înainte: „0 lei” la furnizori) — fără
    explicațiile contabilului („sold preluat nedefalcat”, „fără factură în evidență”). MUTAȚIA: cifra mare pusă înapoi pe facturile deschise -> ROȘU."""
    from e2e_lot13_portal_p1 import _card, _client
    f = firma_559_1
    pregateste_firma(patron, f)
    d = AZI.isoformat()
    _nota(f, d, [{"debit": "4111", "credit": "707", "suma": "4468.24", "partener_nume": "Client Probă SRL"}], descriere="Vânzare E2E 559.1", valideaza=True)
    _nota(f, d, [{"debit": "607", "credit": "401", "suma": "3000.00", "partener_nume": "Furnizor Probă SRL"}], descriere="Achiziție E2E 559.1", valideaza=True)
    email = _client(patron, f, "5591")
    try:
        with ecran_cont(browser, request, email) as c:
            cp = c.pg
            cp.goto(BAZA + "/", wait_until="domcontentloaded")
            _card(cp, "Cifrele firmei")
            cp.wait_for_selector("#cf-de-incasat", timeout=30000)
            inc = " ".join(cp.inner_text("#cf-de-incasat").split())
            pla = " ".join(cp.inner_text("#cf-de-platit").split())
            c.captura("cifrele_firmei")
            assert "4.468,24 lei" in inc and "3.000,00 lei" in pla, (inc, pla)
            for t in (inc, pla):
                assert "nedefalcat" not in t and "fără factură" not in t and "balanța" not in t and "avans" not in t, t
    finally:
        _scoate_contul(email)


# ── 708 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_708_formularul_de_autentificare_are_atributele_standard(browser, request):
    """708 (a). Pașii: pagina publică -> Acces -> Intră în cont -> cabinet: emailul are `autocomplete="username"`, parola `current-password`, în
    același formular (managerul de parole îl recunoaște și îl completează); înregistrarea cabinetului nu le are (parolă nouă: `new-password`).
    MUTAȚIA: `autocomplete="current-password"` scos din formular -> ROȘU."""
    ctx = browser.new_context(viewport={"width": 1700, "height": 1000})
    e = Ecran(ctx.new_page(), request.node.name)
    try:
        pg = e.pg
        pg.goto(BAZA + "/", wait_until="domcontentloaded")
        pg.wait_for_selector("#pagina-acces-btn", timeout=20000)
        pg.click("#pagina-acces-btn")
        pg.click("#acces-intra")
        pg.click("#lg-cabinet")
        pg.wait_for_selector("#login-form #login-email", timeout=10000)
        e.captura("autentificare")
        assert pg.get_attribute("#login-form #login-email", "autocomplete") == "username"
        assert pg.get_attribute("#login-form #login-parola", "autocomplete") == "current-password"
        assert pg.locator("#login-form input").count() == 2
    finally:
        ctx.close()


def test_def_708_formularul_de_invitatie_nu_e_citit_ca_autentificare(patron, firma_559_1):
    """708 (b). Pașii: firma -> Acces client -> „Invită client nou”: câmpurile email și nume nu au atribute de autentificare și cer managerului de
    parole să le ignore (`data-bwignore`) — înainte, Bitwarden propunea „Actualizează autentificarea existentă” pe emailul invitat.
    MUTAȚIA: `data-bwignore` scos din `ac-email` -> ROȘU."""
    pg = patron.pg
    patron.firma(firma_559_1["nume"])
    pg.click("#fa-acces")
    pg.wait_for_selector(_F + "#ac-btn-invita", timeout=20000)
    pg.click(_F + "#ac-btn-invita")
    pg.wait_for_selector("#ac-email", timeout=10000)
    patron.captura("invitatie_client")
    for camp in ("#ac-email", "#ac-nume"):
        assert pg.get_attribute(camp, "data-bwignore") == "true", camp
        assert pg.get_attribute(camp, "autocomplete") == "off", camp
    assert pg.locator(_F + "[autocomplete='username'], " + _F + "[autocomplete='current-password']").count() == 0


# ── 714 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_714(patron):
    for f in firma_noua():
        pregateste_firma(patron, f, regim_fiscal="profit")
        # date-de-pornire (declarate): firma aplică TVA la încasare din prima zi a lunii curente (aplicația scrie perioada prin Date firmă; aici,
        # direct în schemă, ca `e2e_lot10_tva_incasare.py`)
        sql('INSERT INTO "%s".tva_incasare_perioade (de_la) VALUES (%%s)' % f["schema"], (AZI.replace(day=1).isoformat(),))
        yield f


def test_def_714_achizitia_fara_factura_nu_deduce_tva_pe_loc_la_firma_cu_tva_la_incasare(patron, firma_714):
    """714. Pașii: firma cu TVA la încasare -> Operațiuni › Chirii / comodat / refacturări › Refacturare utilități: factura furnizorului
    (1.000 + 210 TVA) -> „Generează nota”: refuz — factura furnizorului se înregistrează în Facturi primite, unde TVA-ul stă pe 4428 și se
    deduce la plată (CF art.297 alin.(3)); nicio notă scrisă. Înainte: nota punea 4426 = 401 210, deducere imediată.
    MUTAȚIA: `refuz_nota_tva_la_primire` întoarce mereu None -> nota 4426 = 401 se scrie -> ROȘU."""
    from e2e_lot13_ops import D, _completeaza, _genereaza, _op, _ultima
    f = firma_714
    pg = _op(patron, f, "chirie")
    _completeaza(pg, [("data", D), ("fel", "refacturare"), ("furnizor_cui", "31654471"), ("furnizor_nume", "Utilitati Proba SA"),
                      ("client_cui", "18765430"), ("client_nume", "Chirias Proba SRL"), ("numar", "UT-1"), ("total_factura", "1000"),
                      ("parte_refacturata", "400"), ("cota", "21")])
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("refuz_tva_la_incasare")
    assert "Facturi primite" in m and "art. 297 alin. (3)" in m and "4428" in m, m
    assert _ultima(f) == ultima, "nota s-a scris cu TVA-ul dedus pe loc"
    assert sql('SELECT count(*) FROM "%s".inregistrari_linii WHERE cont_debit = %%s' % f["schema"], ("4426",))[0][0] == 0


def fisier_117():
    """Balanța cu 117 fără analitic, pentru dovada pe firmele de test (`frontend_test/dovada/dovezi_lot14_2.json`, pasul `incarca`): aceeași sursă."""
    from core.test_import_saga import _cp1250
    return _cp1250(BALANTA_117)
