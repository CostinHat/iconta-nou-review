# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1 (verbatim în DECIZII „Comanda 12.1”), pachetul `notif` — grupa 4 (asistenți, notificări, administrare,
emailuri) și numerele 598 / 600 din chat.

  * 598 — eșecul WhatsApp: „WhatsApp nu e disponibil … notificările îți vin în continuare pe email”, fără „verifică numărul”, fără coduri
    Meta. Meta e SIMULAT pe server (`whatsapp.CHEIE_SIMULAT`, `<ICONTA_WHATSAPP_SIMULAT>/whatsapp.json`): nicio cerere la Meta;
  * 600 — întoarcerea din ANAF: fiecare eșec are textul lui pe pagina de retur (`static/spv_callback.html`, motivul din
    `spv_rute.rezultat_callback`); când ANAF nu trimite deloc înapoi („sesiune invalidă” / pagina de ieșire), fila iConta.eu spune la
    întoarcere ce face contabilul. Nicio cerere nu pleacă la ANAF: `logincert.anaf.ro` e oprit în browser, iar schimbul codului nu se
    atinge (motivele probate aici se hotărăsc înaintea lui);
  * 487 — invitația unui asistent fără nicio firmă e refuzată, pe lista firmelor, și nu scrie niciun cont;
  * 492 — bara realizărilor asistentului („… lucrări pregătite luna aceasta”) se recitește după ce pregătește o notă, fără reîncărcare;
  * C101 — Panou Admin → Cabinete și bara superadminului numără la „facturi emise” / „declarații depuse” numai cererile reușite.

Pe aplicația din index, pe baza de TEST."""
import json
import os
import re
import sys
import time

import pytest

from conftest import BAZA, _ecran, sql

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_bloc_b import _cont_asistent, _firma_gata, _jurnal, _scoate_cont   # noqa: E402
from e2e_lot72_cont import deschide_setari_panou   # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.common import cate   # noqa: E402

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATRON = "patron@prisma-cont.test"
SUPERADMIN = "admin@prisma-cont.test"
TEHNIC = re.compile(r"HTTP|\b\d{3}\b|133010|Meta |Exception|Error|state|token|OAuth", re.I)


@pytest.fixture()
def superadmin(browser, request):
    yield from _ecran(browser, request, SUPERADMIN)


# ── 598: WhatsApp refuzat de Meta ───────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def meta_refuza():
    """Meta simulat: orice cerere WhatsApp e refuzată cu „Account not registered” (133010), ca pe 22.10.2026."""
    d = os.environ.get("ICONTA_WHATSAPP_SIMULAT")
    assert d, ("plasa nu are simulatorul WhatsApp: `scripts/e2e_poarta.py` trebuie să pună ICONTA_WHATSAPP_SIMULAT (lotul 12, 598) — "
               "fără el testul n-ar proba nimic")
    os.makedirs(d, exist_ok=True)
    cale = os.path.join(d, "whatsapp.json")
    json.dump({"http": 400, "error": {"message": "Account not registered", "type": "OAuthException", "code": 133010}},
              open(cale, "w", encoding="utf-8"))
    uid = sql("SELECT id FROM public.users WHERE email = %s", (PATRON,))[0][0]
    sql("UPDATE public.users SET canal_notificari = 'email', telefon = '+40700000000', telefon_confirmat_la = NULL, acord_whatsapp_la = NULL "
        "WHERE id = %s", (uid,))
    sql("DELETE FROM public.telefon_coduri WHERE user_id = %s", (uid,))
    try:
        yield uid
    finally:
        if os.path.exists(cale):
            os.remove(cale)
        sql("DELETE FROM public.telefon_coduri WHERE user_id = %s", (uid,))
        sql("UPDATE public.users SET canal_notificari = 'email', telefon_confirmat_la = NULL, acord_whatsapp_la = NULL WHERE id = %s", (uid,))


def test_def_598_whatsapp_cazut_spune_ca_notificarile_vin_pe_email(patron, meta_refuza):
    """598. Pașii: Setări cont -> Notificări (numărul salvat, neconfirmat; Meta refuză: contul iConta.eu nu e înregistrat) -> bifa de acord
    -> „Trimite codul pe WhatsApp”: „WhatsApp nu e disponibil acum, deci codul de confirmare nu a plecat. Notificările îți vin în
    continuare pe email; …” — fără „verifică numărul”, fără „HTTP 400”, „133010”, „Meta”; canalul rămâne email."""
    from core.uc_cont_notificari import MESAJ_WA_ESUAT
    pg = patron.pg
    deschide_setari_panou(patron, "Notificări", "#not-telefon")
    pg.wait_for_selector("#not-cere-cod", state="visible", timeout=20000)
    pg.check("#not-acord")
    pg.click("#not-cere-cod")
    pg.wait_for_function("() => /WhatsApp/.test((document.querySelector('#not-msg') || {}).innerText || '')", timeout=30000)
    patron.captura("whatsapp_cazut")
    m = pg.inner_text("#not-msg").strip()
    assert m == MESAJ_WA_ESUAT, m
    assert "pe email" in m and "număr" not in m.lower() and not TEHNIC.search(m), m
    assert "msg-eroare" in (pg.get_attribute("#not-msg", "class") or "")
    assert sql("SELECT canal_notificari FROM public.users WHERE id = %s", (meta_refuza,))[0][0] == "email"


# ── 600: întoarcerea din ANAF ───────────────────────────────────────────────────────────────────────────────────────────────────
def _mesaje_retur():
    src = open(os.path.join(RAD, "static", "spv_callback.html"), encoding="utf-8").read()
    bloc = re.search(r"const MESAJE = \{(.*?)\n    \};", src, re.S).group(1)
    return dict(re.findall(r'^\s+(\w+): "([^"]+)",$', bloc, re.M))


def _intoarcere(e, params):
    from urllib.parse import urlencode
    e.pg.goto(BAZA + "/anaf/oauth/callback?" + urlencode(params), wait_until="domcontentloaded")
    e.pg.wait_for_function("() => (document.querySelector('#spv-cb-mesaj') || {}).dataset && "
                           "document.querySelector('#spv-cb-mesaj').dataset.motiv", timeout=20000)
    return e.pg.get_attribute("#spv-cb-mesaj", "data-motiv"), e.pg.inner_text("#spv-cb-mesaj").strip()


def test_def_600_orice_esec_la_anaf_se_intoarce_in_iconta_cu_mesaj_clar(patron):
    """600. Pașii (întoarcerea din ANAF pe adresa de retur a aplicației, cum o face ANAF după autorizare):
    ANAF întoarce eroare (autorizarea n-a fost dată) / nu trimite codul / întoarcerea vine după mai mult de 10 minute / întoarcerea nu e a
    unei cereri plecate din iConta.eu -> pagina „Conectare SPV” a aplicației spune, pe înțelesul contabilului, că SPV nu s-a conectat și
    ce face („Apasă din nou «Conectează SPV»…”), cu butonul „Deschide iConta.eu” — fără „state”, „token”, coduri HTTP; adresa paginii
    poartă numai motivul, niciun text de excepție."""
    from core import spv_conector
    mesaje = _mesaje_retur()
    cab = sql("SELECT accounting_firm_id FROM public.users WHERE email = %s", (PATRON,))[0][0]
    expirat = spv_conector.genereaza_state(spv_conector.principal_firm(cab), acum=int(time.time()) - spv_conector.STATE_DURATA_SEC - 60)
    cazuri = [({"error": "access_denied", "error_description": "HTTP 500 java.lang.NullPointerException"}, "anulata"),
              ({"state": spv_conector.genereaza_state(spv_conector.principal_firm(cab))}, "fara_cod"),
              ({"code": "COD-E2E", "state": expirat}, "expirata"),
              ({"code": "COD-E2E", "state": "nu-e-de-la-iconta"}, "nelegata")]
    for params, motiv in cazuri:
        gasit, text = _intoarcere(patron, params)
        patron.captura(motiv)
        assert gasit == motiv and text == mesaje[motiv], (params, gasit, text)
        assert "nu s-a conectat" in text and "„Conectează SPV”" in text and not TEHNIC.search(text), text
        assert patron.pg.url.endswith("/static/spv_callback.html?motiv=" + motiv), patron.pg.url
        assert patron.pg.locator("a.buton-primar[href='/']").inner_text().strip() == "Deschide iConta.eu"


def test_def_600_fila_iconta_afla_la_intoarcere_ca_anaf_nu_a_trimis_autorizarea(patron):
    """600 (ANAF nu trimite înapoi deloc: „sesiune invalidă”, apoi pagina de ieșire ANAF). Pașii: Setări cont -> Conectare SPV ->
    „Conectează SPV” (se deschide fila ANAF; aici oprită în browser, nicio cerere nu pleacă la ANAF) -> fila ANAF se închide -> înapoi în
    fila iConta.eu: „Conectarea la SPV nu s-a încheiat: ANAF nu a trimis încă înapoi autorizarea. Dacă fila ANAF a rămas pe o eroare (de
    exemplu „sesiune invalidă”) sau pe pagina de ieșire ANAF, închide-o și apasă din nou „Conectează SPV”. …”"""
    pg = patron.pg
    deschide_setari_panou(patron, "Conectare SPV", "#spv-stare")
    if sql("SELECT count(*) FROM public.spv_token WHERE accounting_firm_id = (SELECT accounting_firm_id FROM public.users WHERE email = %s) "
           "AND activ", (PATRON,))[0][0]:
        pytest.fail("cabinetul de test are o conexiune SPV activă: proba „nu s-a conectat nimic” n-ar avea subiect")
    pg.wait_for_selector("#spv-conecteaza", timeout=20000)
    # de aici, nicio cerere în afara aplicației de probă: adresa de autorizare (ANAF) se oprește în browser
    oprite = []
    pg.context.route(lambda u: not u.startswith(BAZA), lambda r: (oprite.append(r.request.url), r.abort()))
    with pg.context.expect_page(timeout=20000) as fila:
        pg.click("#spv-conecteaza")
    fila.value.close()
    assert oprite, "fila de autorizare n-a cerut nimic: proba n-a ajuns la pasul ANAF"      # cererea spre ANAF, oprită în browser
    pg.bring_to_front()
    pg.evaluate("() => { document.dispatchEvent(new Event('visibilitychange')); window.dispatchEvent(new Event('focus')); }")
    pg.wait_for_function("() => /nu s-a încheiat/.test((document.querySelector('#spv-stare') || {}).innerText || '')", timeout=20000)
    patron.captura("intoarcere_fara_autorizare")
    t = pg.inner_text("#spv-stare").strip()
    assert t.startswith("Conectarea la SPV nu s-a încheiat: ANAF nu a trimis încă înapoi autorizarea.") and "sesiune invalidă" in t \
        and "„Conectează SPV”" in t, t


# ── 487: asistent fără firme ────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_487_asistentul_nu_se_invita_fara_nicio_firma(patron):
    """487. Pașii: Asistenți -> „Adaugă asistent” -> emailul, numele -> nicio firmă bifată -> „Trimite invitația”: sub lista firmelor
    „Bifează cel puțin o firmă pe care o lucrează colegul …”, niciun cont creat; firma bifată -> „Trimite invitația” -> „Invitație trimisă
    pe <email>.”"""
    from core.uc_asistenti import MESAJ_ASISTENT_FARA_FIRME
    pg = patron.pg
    email = "e2e-487-%d@prisma-cont.test" % (int(time.time() * 1000) % 1000000000)
    try:
        patron.acasa()
        pg.click("button.cab-card:has([data-cheie='asistenti'])")
        pg.wait_for_selector("#asi-adauga", timeout=20000)
        pg.click("#asi-adauga")
        pg.wait_for_selector(".asi-firma-noua", timeout=20000)
        pg.fill("#asi-email", email)
        pg.fill("#asi-nume", "Asistent 487")
        assert pg.locator(".asi-firma-noua:checked").count() == 0
        pg.click("#asi-trimite")
        pg.wait_for_selector("#asi-firme-noi ~ .msg-eroare, #asi-firme-noi + .msg-eroare", timeout=20000)
        patron.captura("fara_firme")
        sub = pg.locator("#asi-firme-noi + .msg-eroare").inner_text().strip()
        assert sub == MESAJ_ASISTENT_FARA_FIRME, sub
        assert pg.get_attribute("#asi-firme-noi", "aria-invalid") == "true"
        assert sql("SELECT count(*) FROM public.users WHERE email = %s", (email,))[0][0] == 0, "contul s-a creat fără firme"
        pg.locator(".asi-firma-noua").first.check()
        pg.click("#asi-trimite")
        pg.wait_for_selector("#asi-confirmare", timeout=30000)
        assert pg.inner_text("#asi-confirmare").strip() == "Invitație trimisă pe %s." % email
        assert sql("SELECT count(*) FROM public.user_tenants ut JOIN public.users u ON u.id = ut.user_id WHERE u.email = %s",
                   (email,))[0][0] == 1
    finally:
        for (uid,) in sql("SELECT id FROM public.users WHERE email = %s", (email,)):
            sql("DELETE FROM public.user_tenants WHERE user_id = %s", (uid,))
            _scoate_cont(uid)


# ── 492: bara realizărilor asistentului ─────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def ana492(browser, request, firma_e2e):
    _firma_gata(firma_e2e)
    c = _cont_asistent(firma_e2e, "ana492")
    try:
        yield from _ecran(browser, request, c["email"])
    finally:
        _scoate_cont(c["id"])


def _bara3(pg):
    return pg.evaluate("() => (document.querySelector('.bara3') || {}).innerText || ''")


def test_def_492_contorul_pregatite_se_actualizeaza_fara_reincarcare(ana492, firma_e2e):
    """492. Pașii: asistentul nou (nimic pregătit luna aceasta) -> bara de sus: „0 lucrări pregătite luna aceasta” -> Registrul jurnal ->
    „+ Notă nouă” -> Salvează (nota pleacă la validare) -> fără reîncărcare, bara: „1 lucrare pregătită luna aceasta”."""
    import datetime as _dt
    pg = ana492.pg
    azi = _dt.date.today()
    _jurnal(ana492, firma_e2e, (azi.year, azi.month))   # deschiderea firmei pornește din „Acasă” (o încărcare a paginii) — înainte de marcaj
    pg.wait_for_function("() => /pregăti/.test((document.querySelector('.bara3') || {}).innerText || '')", timeout=20000)
    assert re.search(r"\b0\s+lucrări pregătite luna aceasta", _bara3(pg)), _bara3(pg)
    pg.evaluate("() => { window.__fara_reincarcare_492 = true; }")   # de aici, o reîncărcare a paginii l-ar șterge
    desc = "E2E 492 %d" % (int(time.time()) % 100000)
    pg.click("#j-nota-noua")
    pg.wait_for_selector("#je-desc", timeout=10000)
    pg.fill("#je-data", azi.isoformat())
    pg.fill("#je-desc", desc)
    pg.fill("#je-doc", "Contract E2E nr 1 din 01.10.2026")
    pg.fill("#je-linii .je-deb", "612")
    pg.fill("#je-linii .je-cre", "401")
    pg.fill("#je-linii .je-pnume", "Furnizor E2E SRL")   # [381] nota pe 401 cere partenerul la introducere
    pg.fill("#je-linii .je-sum", "100")
    pg.click("#je-salveaza")
    pg.wait_for_selector(".pf-frand:has-text('%s')" % desc, timeout=20000)
    pg.wait_for_function("() => /\\b1\\s+lucrare pregătită luna aceasta/.test((document.querySelector('.bara3') || {}).innerText || '')",
                         timeout=20000)
    ana492.captura("pregatita")
    assert pg.evaluate("() => window.__fara_reincarcare_492 === true"), "pagina s-a reîncărcat"
    assert re.search(r"\b1\s+lucrare pregătită luna aceasta", _bara3(pg)), _bara3(pg)


# ── C101: contoarele din Panou Admin ────────────────────────────────────────────────────────────────────────────────────────────
CABINET_C101 = "E2E C101 Cabinet Probă"
EMAIL_C101 = "e2e.c101.contabil@exemplu.ro"


def _curata_c101():
    uids = [r[0] for r in sql("SELECT id FROM public.users WHERE email = %s", (EMAIL_C101,))]
    if uids:
        sql("DELETE FROM public.audit_log WHERE user_id = ANY(%s)", (uids,))
        sql("DELETE FROM public.users WHERE id = ANY(%s)", (uids,))
    sql("DELETE FROM public.accounting_firms WHERE nume = %s", (CABINET_C101,))


@pytest.fixture()
def cabinet_c101():
    """Cabinetul sintetic: în jurnalul de audit (rândurile pe care le scrie middleware-ul, cu statusul răspunsului) 2 emiteri reușite și 3
    refuzate (422), 1 depunere reușită și 1 refuzată (409), 1 recomandare reușită și 1 refuzată (422)."""
    _curata_c101()
    try:
        # date-de-pornire: cabinetul sintetic al probei, separat de cabinetul de test comun, ca Panou Admin să-i numere numai rândurile de mai jos
        (cab,) = sql("INSERT INTO public.accounting_firms (nume) VALUES (%s) RETURNING id", (CABINET_C101,))[0]
        (uid,) = sql("INSERT INTO public.users (email, password_hash, rol, activ, accounting_firm_id) VALUES (%s, 'x', 'admin_firma', true, %s) "
                     "RETURNING id", (EMAIL_C101, cab))[0]
        for act, st in (("POST /tenants/1/facturi/emite", 200), ("POST /tenants/1/facturi/emite", 200),
                        ("POST /tenants/1/facturi/emite", 422), ("POST /tenants/1/facturi/emite", 422), ("POST /tenants/1/facturi/emite", 422),
                        ("POST /coada/1/depune", 200), ("POST /coada/2/depune", 409), ("POST /recomanda", 200), ("POST /recomanda", 422)):
            # date-de-pornire: rândurile de audit cum le scrie middleware-ul; depunerile (SPV) și refuzurile lor nu se pot produce în plasă
            sql("INSERT INTO public.audit_log (actiune, user_id, detalii) VALUES (%s, %s, %s)", (act, uid, json.dumps({"status": st})))
        yield cab
    finally:
        _curata_c101()


def test_def_c101_panou_admin_nu_numara_refuzurile_ca_facturi_emise(superadmin, cabinet_c101):
    """C101. Pașii: superadminul -> Panou Admin -> Cabinete: rândul cabinetului cu 2 emiteri reușite și 3 refuzate spune „2 facturi
    emise” (era 5), „1 declarație depusă” (era 2), „1 recomandare” (era 2); bara de sus a superadminului (suma pe cabinete; aici numai
    cabinetul probei, restul listei filtrat din răspuns) — la fel; fișa cabinetului — la fel."""
    pg = superadmin.pg

    def numai_c101(route):
        r = route.fetch()
        d = r.json()
        d["cabinete"] = [c for c in d["cabinete"] if c["id"] == cabinet_c101]
        route.fulfill(response=r, body=json.dumps(d), content_type="application/json")
    pg.route("**/admin/activitate/cabinete", numai_c101)
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila", timeout=30000)
    pg.click("button.cab-card:has([data-cheie='activitate'])")
    rand = pg.locator(".pf-frand", has_text=CABINET_C101)
    rand.wait_for(timeout=60000)
    sub = rand.locator(".pf-frand-sub").inner_text()
    superadmin.captura("cabinete")
    for asteptat in (cate(2, "factură emisă", "facturi emise"), cate(1, "declarație depusă", "declarații depuse"),
                     cate(1, "recomandare", "recomandări")):
        assert asteptat in sub, (asteptat, sub)
    pg.wait_for_function("() => /cabinet/.test((document.querySelector('[data-sumar-admin]') || {}).textContent || '')", timeout=30000)
    bara = pg.inner_text("[data-sumar-admin]")
    assert cate(2, "factură emisă", "facturi emise") in bara and cate(1, "declarație depusă", "declarații depuse") in bara, bara
    rand.locator(".pf-frand-text").click()
    pg.wait_for_selector("#ac-detaliu .panou", timeout=30000)
    fisa = pg.inner_text("#ac-detaliu .panou .pf-frand-sub")
    superadmin.captura("fisa")
    assert cate(2, "factură emisă", "facturi emise") in fisa, fisa
