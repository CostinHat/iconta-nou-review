# -*- coding: utf-8 -*-
"""Lotul 4 (comanda Costin 15.10.2026, verbatim în DECIZII „Lotul 4”): înregistrarea liberă cu confirmarea emailului, comutatorul din
Panou Admin, anunțul la cabinet nou și „Activitate cabinete”; 256 — după o publicare, pagina principală și ecranele se încarcă în
versiunea nouă fără Ctrl+F5. Pe aplicația din index, pe baza de TEST; emailurile aplicației de probă stau în cutia de test
(`ICONTA_EMAIL_CUTIE`), de unde proba ia linkul de confirmare — linkul pe care altfel numai destinatarul îl vede.
253 (decizia Costin 15.10.2026 seara, DECIZII „Poarta o dată pe lot” pct.4a: „253: o leagă testele din e2e_inregistrare_libera.py”) =
înregistrarea liberă a lotului 4: testele fluxului și ale comutatorului poartă numărul. 257 = Cloudflare Turnstile pe formular: widgetul
REAL, cu cheile de test ale Cloudflare (`scripts/e2e_poarta.py`), și siteverify real pe server."""
import glob
import json
import os
import re
import secrets

import pytest

from conftest import BAZA, LAT, INALT, Ecran, _ecran, sql
from e2e_invitatii import _client_nou, mod_inregistrare

EMAIL = "e2e.inregistrare@exemplu.ro"
CABINET = "E2E Probă Cabinet Liber"
PAROLA = secrets.token_urlsafe(12) + "!Aa1"   # generată la rulare (garda secretelor din git)
SUPERADMIN = "admin@prisma-cont.test"
RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _curata():
    def tabele(col):
        return [r[0] for r in sql("SELECT c.table_name FROM information_schema.columns c JOIN information_schema.tables t "
                                  "ON t.table_schema = c.table_schema AND t.table_name = c.table_name AND t.table_type = 'BASE TABLE' "
                                  "WHERE c.table_schema = 'public' AND c.column_name = %s AND c.table_name NOT IN ('users', "
                                  "'accounting_firms')", (col,))]
    uids = [r[0] for r in sql("SELECT id FROM public.users WHERE email = %s", (EMAIL,))]
    fids = [r[0] for r in sql("SELECT id FROM public.accounting_firms WHERE nume = %s", (CABINET,))]
    sql("DELETE FROM public.inregistrari_in_asteptare WHERE email = %s", (EMAIL,))
    sql("DELETE FROM public.acord_termeni WHERE email = %s", (EMAIL,))
    sql("DELETE FROM public.cereri_ritm WHERE cheie IN ('inregistrare_ip', 'inregistrare_email', 'confirmare_ip')")
    if uids:
        for t in tabele("user_id"):
            sql('DELETE FROM public."%s" WHERE user_id = ANY(%%s)' % t, (uids,))
        sql("DELETE FROM public.users WHERE id = ANY(%s)", (uids,))
    if fids:
        for t in tabele("accounting_firm_id"):
            sql('DELETE FROM public."%s" WHERE accounting_firm_id = ANY(%%s)' % t, (fids,))
        sql("DELETE FROM public.accounting_firms WHERE id = ANY(%s)", (fids,))


@pytest.fixture()
def superadmin(browser, request):
    yield from _ecran(browser, request, SUPERADMIN)


@pytest.fixture()
def curat():
    era = sql("SELECT valoare FROM public.setari_platforma WHERE cheie = 'inregistrare'")
    _curata()
    yield
    _curata()
    mod_inregistrare(era[0][0] if era else "invitatie")


def _scrisori(catre):
    out = []
    for f in sorted(glob.glob(os.path.join(os.environ["ICONTA_EMAIL_CUTIE"], "*.json"))):
        m = json.load(open(f, encoding="utf-8"))
        if m["catre"] == catre:
            out.append(m)
    return out


def _comuta(superadmin, mod):
    """Superadminul: Panou Admin -> „Înregistrare” -> modul -> „Salvează”."""
    pg = superadmin.pg
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila", timeout=30000)
    pg.click("button.cab-card:has([data-cheie='inregistrare'])")
    pg.wait_for_selector("#ins-moduri", timeout=10000)
    pg.check("input[name='ins-mod'][value='%s']" % mod)
    pg.click("#ins-salveaza")
    pg.wait_for_selector("#ins-msg.msg-ok", timeout=10000)
    assert sql("SELECT valoare FROM public.setari_platforma WHERE cheie = 'inregistrare'") == [(mod,)]


def _pagina(browser, request, eticheta):
    ctx = browser.new_context(viewport={"width": LAT, "height": INALT})
    return ctx, Ecran(ctx.new_page(), "%s_%s" % (request.node.name, eticheta))


def _login(vp, email, parola):
    vp.goto(BAZA + "/", wait_until="domcontentloaded")
    vp.wait_for_selector("#pagina-acces-btn", timeout=20000)
    vp.click("#pagina-acces-btn")
    vp.click("#acces-intra")
    vp.click("#lg-cabinet")
    vp.fill("#login-email", email)
    vp.fill("#login-parola", parola)
    vp.click("#login-buton")


def _asteapta_turnstile(vp):
    """Widgetul Cloudflare a dat tokenul (câmpul ascuns `cf-turnstile-response` din caseta lui), iar verificarea a rulat într-un frame de
    pe challenges.cloudflare.com (iframe-ul stă într-un shadow DOM închis, deci se caută printre frame-urile paginii, nu cu CSS)."""
    vp.wait_for_function("() => ((document.querySelector('#reg-robot input[name=\"cf-turnstile-response\"]') || {}).value || '')"
                         ".length > 0", timeout=30000)
    assert [f.url for f in vp.frames if f.url.startswith("https://challenges.cloudflare.com/")], [f.url for f in vp.frames]


def test_def_253_inregistrarea_libera_contul_apare_numai_dupa_clicul_pe_linkul_din_email(superadmin, browser, request, curat):
    from core import inregistrare_libera as il
    _comuta(superadmin, "libera")
    superadmin.captura("comutator")
    ctx, viz = _pagina(browser, request, "vizitator")
    try:
        vp = viz.pg
        _client_nou(vp, BAZA + "/")
        vp.wait_for_selector("#reg-email", timeout=10000)
        assert vp.get_attribute("#reg-email", "readonly") is None          # emailul se scrie (nu vine dintr-o invitație)
        vp.fill("#reg-cabinet", CABINET)
        vp.fill("#reg-nume-admin", "Ionescu Maria")
        vp.fill("#reg-email", EMAIL)
        vp.fill("#reg-parola", PAROLA)
        vp.fill("#reg-parola2", PAROLA)
        vp.check("#reg-termeni")
        _asteapta_turnstile(vp)                                             # [257] verificarea anti-roboți a trecut
        viz.captura("formular")
        vp.click("#reg-buton")
        vp.wait_for_selector("#reg-verifica", timeout=20000)
        assert EMAIL in vp.inner_text("#reg-verifica")
        viz.captura("verifica_emailul")
        assert sql("SELECT count(*) FROM public.users WHERE email = %s", (EMAIL,)) == [(0,)]          # niciun cont încă
        assert sql("SELECT count(*) FROM public.accounting_firms WHERE nume = %s", (CABINET,)) == [(0,)]
        _login(vp, EMAIL, PAROLA)                                           # până la confirmare nu se poate loga
        vp.wait_for_selector("#login-eroare:not([hidden])", timeout=10000)
        assert vp.inner_text("#login-eroare") == il.MESAJ_NECONFIRMAT
        viz.captura("login_inainte")
        (scrisoare,) = _scrisori(EMAIL)
        tok = re.search(r"#confirmare=([\w-]+)", scrisoare["html"]).group(1)
        vp.goto("about:blank")                                              # linkul din email = o încărcare nouă a paginii
        vp.goto(BAZA + "/#confirmare=" + tok, wait_until="domcontentloaded")
        vp.wait_for_selector("#conf-rezultat.caseta-info", timeout=20000)
        assert CABINET in vp.inner_text("#conf-rezultat")
        assert "#confirmare=" not in vp.url
        viz.captura("confirmat")
        vp.click("#conf-intra")
        assert vp.input_value("#login-email") == EMAIL
        vp.fill("#login-parola", PAROLA)
        vp.click("#login-buton")
        vp.wait_for_selector(".cab-grila", timeout=30000)
        viz.captura("in_cont")
        assert sql("SELECT activ FROM public.users WHERE email = %s", (EMAIL,)) == [(True,)]
        vp.evaluate("sessionStorage.clear(); localStorage.clear()")         # al doilea clic pe același link, fără sesiune
        vp.goto("about:blank")
        vp.goto(BAZA + "/#confirmare=" + tok, wait_until="domcontentloaded")
        vp.wait_for_selector("#conf-rezultat.caseta-atentie", timeout=20000)
        assert vp.inner_text("#conf-rezultat").startswith("Linkul a fost folosit deja")
        assert not viz.erori and not viz.cereri_rele
    finally:
        ctx.close()
    (dest,) = sql("SELECT email FROM public.users WHERE rol='superadmin' AND activ=true ORDER BY id LIMIT 1")[0]   # ca aplicația
    anunt = [m for m in _scrisori(dest) if m["subiect"] == "[iConta.eu] Cabinet nou: %s" % CABINET]
    assert len(anunt) == 1 and EMAIL in anunt[0]["html"]
    pg = superadmin.pg                                                      # „Activitate cabinete”: cabinetul, cu data și calea
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila", timeout=30000)
    pg.click("button.cab-card:has([data-cheie='activitate'])")
    rand = pg.locator(".pf-frand", has_text=CABINET)
    rand.wait_for(timeout=60000)                                            # interogarea ia ~5 s pe baza de test
    assert "(înregistrare liberă)" in rand.inner_text()
    superadmin.captura("activitate")


def test_def_253_comutatorul_pe_numai_prin_invitatie_inchide_formularul(superadmin, browser, request, curat):
    from core import setari_platforma
    _comuta(superadmin, "invitatie")
    ctx, viz = _pagina(browser, request, "vizitator")
    try:
        vp = viz.pg
        _client_nou(vp, BAZA + "/")
        vp.wait_for_selector("#fi-mesaj", timeout=10000)
        assert vp.inner_text("#fi-mesaj") == setari_platforma.MESAJ_NUMAI_INVITATIE
        assert vp.query_selector("#reg-email") is None
        viz.captura()
    finally:
        ctx.close()


def test_def_257_formularul_liber_trece_prin_cloudflare_turnstile(superadmin, browser, request, curat):
    """257. „Înregistrează cabinetul tău” arată verificarea Cloudflare Turnstile; fără bifa ei, „Creează cont” spune ce lipsește și nu
    trimite nimic; cu ea, cererea trece (siteverify real, pe server). Un robot care trimite cererea direct, fără token, e refuzat cu
    motivul și nu lasă nimic în urmă."""
    from core import inregistrare_libera as il
    _comuta(superadmin, "libera")
    scrisori = len(_scrisori(EMAIL))                                        # cutia de test e a întregii rulări
    ctx, viz = _pagina(browser, request, "vizitator")
    try:
        vp = viz.pg
        _client_nou(vp, BAZA + "/")
        vp.wait_for_selector("#reg-email", timeout=10000)
        vp.fill("#reg-cabinet", CABINET)
        vp.fill("#reg-email", EMAIL)
        vp.fill("#reg-parola", PAROLA)
        vp.fill("#reg-parola2", PAROLA)
        vp.check("#reg-termeni")
        vp.evaluate("document.querySelector('#reg-robot').remove()")       # widgetul n-a apucat să dea tokenul
        vp.click("#reg-buton")
        vp.wait_for_selector("#reg-eroare:not([hidden])", timeout=10000)
        assert vp.inner_text("#reg-eroare").startswith("Așteaptă bifa verde din caseta de verificare anti-roboți")
        viz.captura("fara_bifa")
        r = vp.request.post(BAZA + "/auth/register", data={"email": EMAIL, "parola": PAROLA, "nume_cabinet": CABINET,
                                                            "accept_termeni": True})
        assert r.status == 400 and r.json().get("detail") == il.MESAJ_ANTIROBOT, (r.status, r.text())
        assert sql("SELECT count(*) FROM public.inregistrari_in_asteptare WHERE email = %s", (EMAIL,)) == [(0,)]
        assert len(_scrisori(EMAIL)) == scrisori
        _client_nou(vp, BAZA + "/")                                         # formularul din nou, cu widgetul
        vp.wait_for_selector("#reg-email", timeout=10000)
        _asteapta_turnstile(vp)
        viz.captura("bifa")
        vp.fill("#reg-cabinet", CABINET)
        vp.fill("#reg-email", EMAIL)
        vp.fill("#reg-parola", PAROLA)
        vp.fill("#reg-parola2", PAROLA)
        vp.check("#reg-termeni")
        vp.click("#reg-buton")
        vp.wait_for_selector("#reg-verifica", timeout=20000)
        assert len(_scrisori(EMAIL)) == scrisori + 1
        assert not viz.erori and not viz.cereri_rele
    finally:
        ctx.close()


# ── 256 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
STATIC = os.path.join(os.path.dirname(RAD), "iconta_publicat", "static")   # ce servește aplicația de probă (`main._alege_static`)
TEXT_VECHI = "Vizite landing, deschideri modal, click-uri, ghiduri"


@pytest.fixture()
def publicare_simulata():
    """O „publicare” în directorul servit: `admin.js` cu alt text pe cardul Analytics + amprenta nouă în `.publicat.json`. La sfârșit,
    fișierele revin exact."""
    if not os.path.isfile(os.path.join(STATIC, ".publicat.json")):
        pytest.skip("numai pe aplicația de probă a plasei (statica publicată lângă arborele exportat)")
    admin, amprenta = os.path.join(STATIC, "js", "ecrane", "admin.js"), os.path.join(STATIC, ".publicat.json")
    vechi = {p: open(p, encoding="utf-8").read() for p in (admin, amprenta)}
    assert TEXT_VECHI in vechi[admin]

    def publica(eticheta):
        open(admin, "w", encoding="utf-8").write(vechi[admin].replace(TEXT_VECHI, "Versiunea nouă (%s)" % eticheta))
        a = json.loads(vechi[amprenta])
        a["commit"] = "e2e256" + eticheta
        open(amprenta, "w", encoding="utf-8").write(json.dumps(a))
        return "Versiunea nouă (%s)" % eticheta
    try:
        yield publica
    finally:
        for p, t in vechi.items():
            open(p, "w", encoding="utf-8").write(t)


def _card_analytics(pg):
    return pg.inner_text("button.cab-card [data-cheie='analytics']")


def test_def_256_pagina_principala_si_ecranele_se_incarca_in_versiunea_noua(superadmin, publicare_simulata):
    """256. Superadminul are aplicația deschisă; se publică o versiune nouă. (1) Pe pagina principală: aplicația se reîncarcă singură
    (fără formular început) și cardul arată textul nou, cu „Aplicația s-a actualizat la versiunea nouă.” (2) Cu un ecran deschis:
    anunțul „Versiune nouă” apare în bara superadminului și rămâne acolo; la întoarcerea pe pagina principală, versiunea nouă."""
    pg = superadmin.pg
    r = pg.goto(BAZA + "/", wait_until="domcontentloaded")
    assert r.headers.get("cache-control") == "no-cache"                    # pagina se revalidează la fiecare încărcare
    pg.wait_for_selector(".cab-grila", timeout=30000)
    assert _card_analytics(pg) == TEXT_VECHI
    nou = publicare_simulata("a")
    pg.evaluate("document.dispatchEvent(new Event('visibilitychange'))")    # revenirea în filă: momentul în care se verifică
    pg.wait_for_function("(t) => (document.querySelector(\"button.cab-card [data-cheie='analytics']\") || {}).innerText === t",
                         arg=nou, timeout=20000)
    pg.wait_for_selector("#versiune-actualizata", timeout=10000)
    superadmin.captura("acasa_actualizata")
    pg.click("button.cab-card:has([data-cheie='invitatii'])")              # un ecran deschis: nimic nu se reîncarcă singur
    pg.wait_for_selector("#inv-email", timeout=20000)
    nou2 = publicare_simulata("b")
    pg.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
    pg.wait_for_selector(".subbara button.versiune-noua", timeout=20000)
    # centralizatorul superadminului (pe baza de test interogarea ia ~5 s pe 1,47 mil. de rânduri de audit) își scrie textul DUPĂ
    # anunț: până la 256 rescria toată bara și anunțul dispărea
    pg.wait_for_selector(".subbara .subbara-admin-sumar", timeout=90000)
    assert pg.locator(".subbara button.versiune-noua").count() == 1, "anunțul „Versiune nouă” a fost șters din bara superadminului"
    assert pg.locator("#inv-email").count() == 1                            # ecranul deschis n-a fost reîncărcat
    superadmin.captura("ecran_deschis_anunt")
    pg.click(".fereastra-antet .nav-x")                                      # închide ecranul: înapoi pe pagina principală
    pg.wait_for_function("(t) => (document.querySelector(\"button.cab-card [data-cheie='analytics']\") || {}).innerText === t",
                         arg=nou2, timeout=20000)
    superadmin.captura("acasa_dupa_ecran")
