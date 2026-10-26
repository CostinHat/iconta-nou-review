# -*- coding: utf-8 -*-
"""Lotul 13, comanda 13.1 (verbatim în DECIZII „Comanda 13.1”), zona admin — Panou Admin și paginile publice:

  * 642 / „Înregistrează cabinetul tău” pe două coloane (decizia Costin: „confirmat”): câmpurile pe două coloane, fereastra întreagă în
    ecran la 1280×720, „Creează cont” în vedere (decizia Costin: „642: e2e-ul e dovada potrivită pentru înregistrarea unui cabinet.”);
  * 645 suspendarea: motivul obligatoriu din lista fixă + nota internă; motivul la logare, fără linie de contact; emailul către
    administratorul cabinetului; jurnalul (cine, când, motivul, reactivarea);
  * 644 a bara superadminului se recitește după suspendare (fără reîncărcare); 644 b „utilizatori”, nu „angajați”;
  * 646 a–e anunțurile: destinatari expliciți („Toate cabinetele”), confirmarea cu numărul, propunerile monitorului cu datele actului,
    lista trimiterilor (citit / retragere), data în fereastra anunțului, invitația cu „Copiază” și retragere;
  * 643 Sănătate server: cifre în format românesc, pragul de alertă lângă cifre și pe grafice, scara verticală;
  * 649 Analytics: vizitele dintr-o sesiune iConta deschisă nu se numără; zilele în forma aplicației;
  * 578 pagina publică „Funcționalități”: fără funcțiile găsite stricate, fără funcțiile platformei, fără dubluri;
  * 608 mesajele de autentificare încep cu literă mare.

Pe aplicația din index, pe baza de TEST; emailurile în cutia de test (`ICONTA_EMAIL_CUTIE`), nimic nu pleacă."""
import contextlib
import glob
import json
import os
import re
import sys
import time

import pytest

from conftest import BAZA, Ecran, _ecran, sql

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_bloc_a import _scoate_cont   # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.common import cate   # noqa: E402

SUPERADMIN = "admin@prisma-cont.test"
LAPTOP = {"width": 1280, "height": 720}


@pytest.fixture()
def superadmin(browser, request):
    """[lotul 13, plasa 1: ERROR la 644 / 646 a-c] testele care restrâng lista cabinetelor (`_numai_cabinetul`) lasă rutele active la
    închidere: o cerere `/admin/activitate/cabinete` încă în zbor („Route.fetch: Request context disposed”) arunca eroarea în testul
    următor. Rutele se scot (fără să aștepte cererea) înaintea închiderii contextului."""
    g = _ecran(browser, request, SUPERADMIN)
    e = next(g)
    try:
        yield e
    finally:
        with contextlib.suppress(Exception):
            e.pg.unroute_all(behavior="ignoreErrors")
        with contextlib.suppress(StopIteration):
            next(g)


def _emailurile(catre, inainte):
    cutie = os.environ["ICONTA_EMAIL_CUTIE"]
    out = []
    for cale in sorted(set(glob.glob(os.path.join(cutie, "*.json"))) - inainte):
        e = json.load(open(cale, encoding="utf-8"))
        if e.get("catre") == catre:
            out.append(e)
    return out


def _cutia():
    return set(glob.glob(os.path.join(os.environ["ICONTA_EMAIL_CUTIE"], "*.json")))


def _panou(e, cheie):
    e.pg.goto(BAZA + "/", wait_until="domcontentloaded")
    e.pg.wait_for_selector(".cab-grila", timeout=30000)
    e.pg.click("button.cab-card:has([data-cheie='%s'])" % cheie)


def _numai_cabinetul(pg, cab_id):
    """Răspunsul real al `/admin/activitate/cabinete`, cu numai cabinetul probei (lista bazei de test e lungă și se schimbă)."""
    def h(route):
        r = route.fetch()
        d = r.json()
        d["cabinete"] = [c for c in d["cabinete"] if c["id"] == cab_id]
        route.fulfill(response=r, body=json.dumps(d), content_type="application/json")
    pg.route("**/admin/activitate/cabinete", h)


# ── cabinetul sintetic al probei (cabinetul + administratorul lui, pe drumul aplicației) ──────────────────────────────────────
@pytest.fixture()
def cabinet_645():
    from conftest import _db
    from core import auth_api
    db = _db()
    email, parola = "e2e.645.%d@prisma-cont.test" % (int(time.time() * 1000) % 100000000), "Parola-E2E-645-%d" % int(time.time())
    with db.get_conn() as c:
        r = auth_api.inregistreaza_cabinet(c, email, parola, "E2E Cabinet Suspendare 645", nume="Probă", prenume="Ana")
        assert r.get("ok"), r
        with c.cursor() as cur:
            cur.execute("UPDATE public.users SET parola_schimbata = true, bun_venit_vazut_la = now() WHERE id = %s", (r["user_id"],))
        c.commit()
    try:
        yield {"id": r["firm_id"], "uid": r["user_id"], "email": email, "parola": parola}
    finally:
        sql("DELETE FROM public.anunturi_cabinet WHERE cabinet_id = %s", (r["firm_id"],))
        for (uid,) in sql("SELECT id FROM public.users WHERE accounting_firm_id = %s", (r["firm_id"],)):
            _scoate_cont(uid)
        sql("DELETE FROM public.suspendari_cabinet WHERE cabinet_id = %s", (r["firm_id"],))
        with contextlib.suppress(Exception):
            sql("DELETE FROM public.accounting_firms WHERE id = %s", (r["firm_id"],))


def _logare_cu_parola(browser, request, email, parola):
    """Pagina publică -> „Acces” -> „Intră în cont” -> cabinet -> emailul și parola -> „Autentificare”. Întoarce textul refuzului."""
    ctx = browser.new_context(viewport={"width": 1700, "height": 1000})
    e = Ecran(ctx.new_page(), request.node.name)
    try:
        pg = e.pg
        pg.goto(BAZA + "/", wait_until="domcontentloaded")
        pg.wait_for_selector("#pagina-acces-btn", timeout=20000)
        pg.click("#pagina-acces-btn")
        pg.click("#acces-intra")
        pg.click("#lg-cabinet")
        pg.fill("#login-email", email)
        pg.fill("#login-parola", parola)
        pg.click("#login-buton")
        pg.wait_for_selector("#login-eroare:not([hidden])", timeout=20000)
        pg.wait_for_timeout(300)
        e.captura("logare")
        return " ".join(pg.inner_text("#login-eroare").split()), e
    finally:
        ctx.close()


# ── 645 + 644 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_645_suspendarea_cere_motivul_iar_logarea_il_arata_fara_contact(browser, request, superadmin, cabinet_645):
    """645. Pașii superadminului: Panou Admin -> Activitate cabinete -> rândul cabinetului -> „Suspendă” -> fereastra „Suspendă
    cabinetul”: „Suspendă accesul” fără motiv -> „Alege motivul suspendării.” (nimic scris) -> „Neplată” + nota internă -> confirmarea
    -> lista spune că e suspendat, cu motivul, și că emailul a plecat la administrator. Emailul (cutia de test): motivul, fără nota
    internă. Logarea administratorului cabinetului cu parola: „Cabinetul este suspendat. Motivul: neplată.” — fără „contact”/„furnizor”,
    fără nota internă. Fișa cabinetului: jurnalul (motivul, nota internă, „încă suspendat”); „Reactivează” -> jurnalul are reactivarea.
    ROȘU înainte: suspendarea fără motiv, la logare „Cabinetul este suspendat. Contactați furnizorul.”"""
    pg = superadmin.pg
    cab = cabinet_645
    _numai_cabinetul(pg, cab["id"])
    _panou(superadmin, "activitate")
    rand = pg.locator(".pf-frand[data-cabinet='%d']" % cab["id"])
    rand.wait_for(timeout=60000)
    rand.locator("[data-toggle]").click()
    pg.wait_for_selector("#sus-trimite", timeout=20000)
    pg.click("#sus-trimite")
    pg.wait_for_function("() => (document.querySelector('#sus-msg') || {}).innerText.includes('Alege motivul suspendării.')", timeout=10000)
    assert sql("SELECT activ FROM public.accounting_firms WHERE id = %s", (cab["id"],)) == [(True,)]
    pg.click("#sus-motiv [data-motiv='neplata']")
    assert pg.get_attribute("#sus-motiv [data-motiv='neplata']", "aria-pressed") == "true"
    pg.fill("#sus-nota", "Notă internă 645: restanță din septembrie")
    superadmin.captura("fereastra_suspendarii")
    inainte = _cutia()
    pg.click("#sus-trimite")
    pg.wait_for_selector("#caseta-atentie-activa #ca-ok", timeout=10000)
    assert "neplată" in pg.inner_text("#caseta-atentie-activa")
    pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("() => /e suspendat/.test((document.querySelector('#ac-mesaj') || {}).innerText || '')", timeout=30000)
    msg = " ".join(pg.inner_text("#ac-mesaj").split())
    superadmin.captura("lista_dupa_suspendare")
    assert "(motivul: neplată)" in msg and "Emailul cu motivul a plecat la 1 administrator" in msg, msg
    assert sql("SELECT motiv, nota_interna, reactivat_la FROM public.suspendari_cabinet WHERE cabinet_id = %s", (cab["id"],)) == \
        [("neplata", "Notă internă 645: restanță din septembrie", None)]
    em = []
    for _ in range(20):
        em = _emailurile(cab["email"], inainte)
        if em:
            break
        time.sleep(0.5)
    assert len(em) == 1 and "Motivul: <b>neplată</b>" in em[0]["html"] and "restanță" not in em[0]["html"], em
    text, _e = _logare_cu_parola(browser, request, cab["email"], cab["parola"])
    assert text == "Cabinetul este suspendat. Motivul: neplată.", text
    assert not re.search(r"contact|furnizor|restanță", text, re.I), text
    # fișa cabinetului: jurnalul suspendărilor
    rand.locator("[data-fisa]").click()
    pg.wait_for_selector("#ac-suspendari", timeout=30000)
    j = " ".join(pg.inner_text("#ac-suspendari").split())
    superadmin.captura("jurnal")
    assert "neplată" in j and "Notă internă 645" in j and "încă suspendat" in j, j
    pg.click(".fereastra .nav-inapoi")
    rand = pg.locator(".pf-frand[data-cabinet='%d']" % cab["id"])
    rand.wait_for(timeout=30000)
    rand.locator("[data-toggle]").click()
    pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("() => /activ din nou/.test((document.querySelector('#ac-mesaj') || {}).innerText || '')", timeout=30000)
    assert sql("SELECT reactivat_la IS NOT NULL FROM public.suspendari_cabinet WHERE cabinet_id = %s", (cab["id"],)) == [(True,)]


def test_def_644_bara_superadminului_se_reciteste_dupa_suspendare_si_numara_utilizatori(superadmin, cabinet_645):
    """644. Pașii: Panou Admin -> Activitate cabinete (lista: numai cabinetul probei) — bara de sus: „1 cabinet activ … 1 utilizator”,
    rândul: „1 utilizator” (nu „angajat”) -> „Suspendă” cu motiv -> bara de sus, FĂRĂ reîncărcare: „0 cabinete active”. ROȘU înainte:
    bara rămânea „… cabinete active” până la reîncărcare; eticheta era „angajați”."""
    pg = superadmin.pg
    cab = cabinet_645
    _numai_cabinetul(pg, cab["id"])
    _panou(superadmin, "activitate")
    rand = pg.locator(".pf-frand[data-cabinet='%d']" % cab["id"])
    rand.wait_for(timeout=60000)
    pg.wait_for_function("() => /cabinet/.test((document.querySelector('[data-sumar-admin]') || {}).textContent || '')", timeout=30000)
    bara = pg.inner_text("[data-sumar-admin]")
    sub = rand.locator(".pf-frand-sub").first.inner_text()
    assert cate(1, "cabinet activ", "cabinete active") in bara and cate(1, "utilizator", "utilizatori") in bara, bara
    assert cate(1, "utilizator", "utilizatori") in sub and "angajat" not in sub and "angajat" not in bara, (sub, bara)
    superadmin.captura("inainte")
    rand.locator("[data-toggle]").click()
    pg.wait_for_selector("#sus-trimite", timeout=20000)
    pg.click("#sus-motiv [data-motiv='cerere_cabinet']")
    pg.click("#sus-trimite")
    pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("(t) => (document.querySelector('[data-sumar-admin]') || {}).textContent.includes(t)",
                         arg=cate(0, "cabinet activ", "cabinete active"), timeout=30000)
    superadmin.captura("dupa")


# ── 646 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
MESAJ_646 = "Anunț de probă E2E 646 — mentenanță programată"


def test_def_646_a_c_anuntul_cere_destinatari_confirma_numarul_si_se_retrage(superadmin, cabinet_645):
    """646 a + c. Pașii: Anunțuri -> „Mesaj” fără destinatari -> „Alege destinatarii…” (nimic trimis) -> „Destinatari” -> „Toate
    cabinetele” -> „Mesaj” -> „Trimite” -> confirmarea spune la câte cabinete pleacă (= cabinetele active) -> „Renunță” (nimic trimis) ->
    „Destinatari”: numai cabinetul probei -> „Trimite” -> „Anunțuri trimise”: rândul, „0 din 1” citit -> „Retrage” -> „retras”; cabinetul
    nu-l mai primește. ROȘU înainte: „Nimic bifat = anunțul merge la toți”; fără listă și fără retragere."""
    pg = superadmin.pg
    cab = cabinet_645
    pg.evaluate("() => { delete window._anStare; }")
    _panou(superadmin, "anunturi")
    pg.wait_for_selector("#an-op-msg", timeout=20000)
    pg.click("#an-op-msg")
    pg.fill("#an-mesaj", MESAJ_646)
    pg.click("#an-trimite")
    pg.wait_for_function("() => (document.querySelector('#an-msg') || {}).innerText.includes('Alege destinatarii')", timeout=10000)
    assert sql("SELECT count(*) FROM public.anunturi_cabinet WHERE mesaj = %s", (MESAJ_646,)) == [(0,)]
    superadmin.captura("fara_destinatari")
    pg.click(".fereastra .nav-inapoi")
    pg.click("#an-op-cab")
    pg.check("#an-toate")
    active = sql("SELECT count(*) FROM public.accounting_firms WHERE activ")[0][0]
    pg.click(".fereastra .nav-inapoi")
    pg.click("#an-op-msg")
    pg.fill("#an-mesaj", MESAJ_646)
    pg.click("#an-trimite")
    pg.wait_for_selector("#caseta-atentie-activa", timeout=10000)
    conf = " ".join(pg.inner_text("#caseta-atentie-activa").split())
    superadmin.captura("confirmarea_toate")
    assert ("Anunțul pleacă la %s (toate cabinetele active)" % cate(active, "cabinet", "cabinete")) in conf, conf
    pg.click("#caseta-atentie-activa #ca-nu")
    assert sql("SELECT count(*) FROM public.anunturi_cabinet WHERE mesaj = %s", (MESAJ_646,)) == [(0,)]
    pg.click(".fereastra .nav-inapoi")
    pg.click("#an-op-cab")
    pg.uncheck("#an-toate")
    pg.fill("#sel-cauta", "E2E Cabinet Suspendare 645")
    pg.check(".sel-bifa[value='%d']" % cab["id"])
    pg.click(".fereastra .nav-inapoi")
    pg.click("#an-op-msg")
    pg.fill("#an-mesaj", MESAJ_646)
    pg.click("#an-trimite")
    pg.wait_for_selector("#caseta-atentie-activa #ca-ok", timeout=10000)
    assert "Anunțul pleacă la 1 cabinet." in " ".join(pg.inner_text("#caseta-atentie-activa").split())
    pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("() => (document.querySelector('#an-msg') || {}).innerText.includes('Trimis către 1 cabinet')", timeout=20000)
    assert sql("SELECT count(*) FROM public.anunturi_cabinet WHERE mesaj = %s", (MESAJ_646,)) == [(1,)]
    pg.click(".fereastra .nav-inapoi")
    pg.click("#an-op-trimise")
    rand = pg.locator("#an-trimise tr", has_text=MESAJ_646)
    rand.wait_for(timeout=20000)
    assert "0 din 1" in rand.inner_text() and "activ" in rand.inner_text()
    superadmin.captura("trimise")
    rand.locator("[data-retrage]").click()
    pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("(m) => [...document.querySelectorAll('#an-trimise tr')].some((r) => r.innerText.includes(m) && "
                         "r.innerText.includes('retras'))", arg=MESAJ_646, timeout=20000)
    superadmin.captura("retras")
    assert sql("SELECT count(*) FROM public.anunturi_cabinet WHERE mesaj = %s AND retras_la IS NOT NULL", (MESAJ_646,)) == [(1,)]
    from core import repo_admin
    from conftest import _db
    with _db().get_conn() as c, c.cursor() as cur:
        assert repo_admin.anunturi_pentru_cabinet(cur, cab["id"]) == []


def test_def_646_b_propunerea_monitorului_arata_datele_actului(superadmin):
    """646 b. O propunere a monitorului fiscal (alertă nevăzută) -> Anunțuri: „Publicat: 15.01.2099 · intră în vigoare: 01.02.2099”;
    alta fără date în sursă: „nu apare în sursă”. ROȘU înainte: fără date."""
    # Drumul aplicației: monitorul fiscal (cronul) citește actul din Portalul legislativ — de neatins din plasă —, îl dă analizei AI și
    # scrie propunerile cu `monitor_fiscal.salveaza`. Plasa pornește de la ieșirea analizei (forma ei, cu datele actului sau fără ele)
    # și trece prin același `salveaza`: data publicării și data intrării în vigoare se citesc / se derivă exact ca pe producție.
    from core import monitor_fiscal
    from conftest import _db
    analiza = [{"titlu": "E2E 646 b act cu date", "rezumat": "r", "directie": "catre_anaf", "declaratii_atinse": ["D300"],
                "data_vigoare": "2099-02-01", "data_publicarii": "2099-01-15"},
               {"titlu": "E2E 646 b act fara date", "rezumat": "r", "directie": "necunoscut", "declaratii_atinse": []}]
    with _db().get_conn() as conn:
        noi = monitor_fiscal.salveaza(conn, "portal_alerta", analiza, "https://legislatie.just.ro/Public/DetaliiDocument/0")
    assert [x["titlu"] for x in noi] == ["E2E 646 b act cu date", "E2E 646 b act fara date"], noi
    ids = dict(sql("SELECT titlu, id FROM public.alerte_fiscale WHERE sursa = 'portal_alerta' AND titlu LIKE %s", ("E2E 646 b act %",)))
    a1, a2 = ids["E2E 646 b act cu date"], ids["E2E 646 b act fara date"]
    try:
        pg = superadmin.pg
        _panou(superadmin, "anunturi")
        pg.wait_for_selector("[data-alerta='%d'] .an-date-act" % a1, timeout=30000)
        t1 = " ".join(pg.inner_text("[data-alerta='%d'] .an-date-act" % a1).split())
        t2 = " ".join(pg.inner_text("[data-alerta='%d'] .an-date-act" % a2).split())
        pg.locator("[data-alerta='%d']" % a1).scroll_into_view_if_needed()
        superadmin.captura()
        assert t1 == "Publicat: 15.01.2099 · intră în vigoare: 01.02.2099", t1
        assert t2 == "Publicat: nu apare în sursă · intră în vigoare: nu apare în sursă", t2
    finally:
        sql("DELETE FROM public.alerte_fiscale WHERE id IN (%s, %s)", (a1, a2))


def test_def_646_d_fereastra_anuntului_arata_data(browser, request, cabinet_645):
    """646 d. Un anunț pentru cabinet -> administratorul cabinetului intră: fereastra „Mesaj de la iConta.eu” spune „Trimis pe <azi>”.
    ROȘU înainte: fereastra nu arăta data."""
    import datetime as _dt
    cab = cabinet_645
    sql("UPDATE public.users SET telefon = '+40700000000', notificari_salvate_la = now() WHERE id = %s", (cab["uid"],))
    # date-de-pornire: trimiterea pe ecran e probată de 646 a + c
    sql("INSERT INTO public.anunturi_cabinet (cabinet_id, mesaj) VALUES (%s, %s)", (cab["id"], MESAJ_646 + " d"))
    with contextlib.contextmanager(_ecran)(browser, request, cab["email"]) as e:
        e.pg.goto(BAZA + "/", wait_until="domcontentloaded")
        e.pg.wait_for_selector(".anunt-data", timeout=30000)
        t = e.pg.inner_text(".anunt-data")
        e.captura()
        assert t.strip() == "Trimis pe %s" % _dt.date.today().strftime("%d.%m.%Y"), t
        e.pg.click(".anunt-ok")


def test_def_646_e_invitatia_se_copiaza_si_se_retrage(browser, request):
    """646 e. Pașii: Invitații cabinete -> emailul -> „Trimite invitația” -> lângă link „Copiază” -> „Linkul e copiat.” (clipboard = link)
    -> lista: „valabilă”, „Retrage” -> confirmare -> „retrasă”; linkul spune „Invitația a fost retrasă.” ROȘU înainte: fără „Copiază”,
    fără retragere."""
    email = "e2e.646e.%d@prisma-cont.test" % (int(time.time() * 1000) % 100000000)
    ctx = browser.new_context(viewport={"width": 1700, "height": 1000})
    ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=BAZA)
    from conftest import sesiune
    ctx.add_init_script(sesiune(SUPERADMIN))
    e = Ecran(ctx.new_page(), request.node.name)
    try:
        pg = e.pg
        _panou(e, "invitatii")
        pg.wait_for_selector("#inv-email", timeout=20000)
        pg.fill("#inv-email", email)
        pg.click("#inv-trimite")
        pg.wait_for_selector("#inv-copiaza", timeout=30000)
        link = pg.input_value("#inv-link")
        pg.click("#inv-copiaza")
        pg.wait_for_function("() => (document.querySelector('#inv-copiat') || {}).innerText.includes('copiat')", timeout=10000)
        assert pg.evaluate("() => navigator.clipboard.readText()") == link
        rand = pg.locator("#inv-tabel tr", has_text=email)
        rand.wait_for(timeout=20000)
        assert "valabilă" in rand.inner_text()
        e.captura("copiat")
        rand.locator("[data-retrage-inv]").click()
        pg.click("#caseta-atentie-activa #ca-ok")
        pg.wait_for_function("(m) => [...document.querySelectorAll('#inv-tabel tr')].some((r) => r.innerText.includes(m) && "
                             "r.innerText.includes('retrasă'))", arg=email, timeout=20000)
        e.captura("retrasa")
        tok = link.split("#invitatie=", 1)[1]
        r = pg.evaluate("async (t) => (await fetch('/public/invitatie/' + encodeURIComponent(t))).json()", tok)
        assert r["valida"] is False and r["refuz"]["cod"] == "RETRASA", r
        assert not e.erori and not e.cereri_rele, (e.erori, e.cereri_rele)
    finally:
        ctx.close()
        sql("DELETE FROM public.invitatii_cabinet WHERE email = %s", (email,))


#: o cifră cu punct ZECIMAL („1.53369140625”, „32.9”); punctul de mii al formatului românesc („7.812,3”, „3.651 MB” — grup de exact trei
#: cifre) nu e una [lotul 13, plasa 1: „3.651 MB liber” era citit ca zecimală]
ZECIMALA_CU_PUNCT = re.compile(r"\b\d+\.(?!\d{3}\b)\d+\b(?![.,]\d)")


# ── 643 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_643_sanatatea_arata_cifre_romanesti_pragul_si_scara(superadmin):
    """643. Pașii: Panou Admin -> Sănătate server: cifrele cu virgulă (încărcarea cu două zecimale), „pragul de alertă” lângă încărcare,
    RAM și disc; graficul încărcării (media pe 15 minute) are scara verticală (3 valori) și linia punctată a pragului. ROȘU înainte:
    „1.53369140625”, „32.9”, fără prag, fără scară."""
    # date-de-pornire: istoricul buclei de sănătate (un rând la 5 minute în producție; plasa nu așteaptă 15 minute)
    sql("INSERT INTO public.metrici_sanatate (ram_procent, disc_procent, load1, load15, conexiuni_db, erori_noi, creat_la, teste) VALUES "
        "(32.9, 41.25, 1.53369140625, 0.734, 7, 0, now() - interval '10 minutes', true), "
        "(33.1, 41.25, 0.8, 0.9, 8, 0, now() - interval '5 minutes', true)")
    try:
        pg = superadmin.pg
        _panou(superadmin, "sanatate")
        pg.wait_for_selector("#san-server", timeout=30000)
        srv = " ".join(pg.inner_text("#san-server").split())
        superadmin.captura()
        assert srv.count("pragul de alertă") == 3, srv
        assert not ZECIMALA_CU_PUNCT.search(srv), srv                                     # nicio cifră cu punct zecimal („1.234,5” e o mie)
        assert re.search(r"\d,\d\d\b", srv) or "—" in srv, srv
        g = pg.locator("[data-grafic='load15']")
        assert g.locator(".san-prag").count() == 1 and g.locator(".san-scara span").count() == 3
        assert not ZECIMALA_CU_PUNCT.search(g.inner_text()), g.inner_text()
    finally:
        sql("DELETE FROM public.metrici_sanatate WHERE teste AND load1 = 1.53369140625")


# ── 649 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_649_vizitele_dintr_o_sesiune_interna_nu_se_numara(browser, request, superadmin):
    """649. Pașii: superadminul deschide Panou Admin -> browserul ține momentul sesiunii (`localStorage`, nimic trimis serverului);
    Analytics: zilele în forma aplicației (ZZ.LL.AAAA), nu ISO, și nota despre vizitele noastre. Pagina publică, într-un browser cu acel
    moment (o sesiune iConta deschisă): nicio cerere `/api/eveniment-public`; într-un browser fără el: vizita pleacă. ROȘU înainte:
    vizita dintr-o sesiune deschisă se număra; „2026-10-24”."""
    pg = superadmin.pg
    _panou(superadmin, "analytics")
    pg.wait_for_selector("#an-intern", timeout=30000)
    zile = pg.inner_text("#an-intern")
    corp = pg.evaluate("() => [...document.querySelectorAll('.fereastra .pf-titlu')].find((h) => h.innerText === 'Pe zi')?.nextElementSibling?.innerText || ''")
    marcaj = pg.evaluate("() => localStorage.getItem('iconta_sesiune_interna')")
    superadmin.captura("analytics")
    assert "nu se numără" in zile.replace("Nu se numără", "nu se numără"), zile
    assert not re.search(r"\b20\d\d-\d\d-\d\d\b", corp), corp
    assert marcaj and int(marcaj) > 0, marcaj                                       # Panou Admin a marcat sesiunea în browser

    def vizite(cu_marcaj):
        ctx = browser.new_context(viewport={"width": 1700, "height": 1000})
        if cu_marcaj:   # același browser în care e deschisă sesiunea (contextul superadminului are sesiunea pusă la fiecare pagină)
            ctx.add_init_script("localStorage.setItem('iconta_sesiune_interna', %s);" % json.dumps(marcaj))
        try:
            p2 = ctx.new_page()
            trimise = []
            p2.on("request", lambda r: trimise.append(r.url) if "/api/eveniment-public" in r.url else None)
            p2.goto(BAZA + "/", wait_until="domcontentloaded")
            p2.wait_for_selector("#pagina-acces-btn", timeout=20000)
            p2.wait_for_timeout(1500)
            return trimise
        finally:
            ctx.close()
    assert vizite(True) == []
    assert len(vizite(False)) >= 1                                                 # anti-vacuu: fără sesiune, vizita pleacă


# ── 578 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
NU_PUBLICE = ("Sinteza zilnică pe email", "Triaj AI al sesizărilor", "Analiza AI a tiparelor de respingere", "Suspendare cabinet",
              "Înregistrarea cabinetului din aplicație", "API pentru portal (numai citire)", "API public pentru integrări",
              "Notificări pe evenimente", "Notificările pe tipuri (ce primești pe WhatsApp / email)",
              "Export GDPR complet cabinet (portabilitate)")


def test_def_578_pagina_functionalitati_fara_functii_stricate_de_platforma_si_dubluri(browser, request):
    """578. Pașii vizitatorului: pagina publică -> „Funcționalități și prețuri” -> fiecare grupă: nicio funcție găsită stricată (sinteza
    zilnică, triajul AI, analiza AI a tiparelor), nicio funcție a administratorului platformei (suspendarea, înregistrarea cabinetelor),
    o singură intrare pentru API, notificări și exportul datelor. ROȘU înainte: toate erau listate."""
    ctx = browser.new_context(viewport={"width": 1700, "height": 1000})
    e = Ecran(ctx.new_page(), request.node.name)
    try:
        pg = e.pg
        pg.goto(BAZA + "/", wait_until="domcontentloaded")
        pg.wait_for_selector("#pagina-functionalitati-btn", timeout=20000)
        pg.click("#pagina-functionalitati-btn")
        pg.wait_for_selector(".func-grila .func-card[data-i]", timeout=10000)
        functii = []
        for i in range(pg.locator(".func-grila .func-card[data-i]").count()):
            pg.locator(".func-grila .func-card[data-i]").nth(i).click()
            pg.wait_for_selector(".func-lista", timeout=10000)
            functii += pg.eval_on_selector_all(".func-lista li", "els => els.map((x) => x.innerText.trim())")
            pg.locator(".func-overlay").last.locator(".nav-x").click()
            pg.wait_for_timeout(200)
        e.captura()
        assert len(functii) > 100, len(functii)                                            # anti-vacuu
        assert not [f for f in functii if f in NU_PUBLICE], [f for f in functii if f in NU_PUBLICE]
        assert sum(1 for f in functii if re.search(r"\bAPI\b", f)) == 1, [f for f in functii if "API" in f]
        assert "Chei API publice per cabinet" in functii and "Notificări în aplicație și pe email" in functii
        assert "Exportul datelor cabinetului, din aplicație" in functii
    finally:
        ctx.close()


# ── 608 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_608_mesajele_de_autentificare_incep_cu_majuscula(browser, request):
    """608. Pașii: „Intră în cont” cu o parolă greșită -> „Email sau parolă greșite.”; linkul de logare nevalid (`#magic=…`) -> un mesaj
    care începe cu literă mare și spune ce e de făcut. ROȘU înainte: „email sau parolă greșite”, „link invalid”."""
    text, _e = _logare_cu_parola(browser, request, "nu.exista.608@prisma-cont.test", "parola-gresita-608")
    assert text == "Email sau parolă greșite.", text
    ctx = browser.new_context(viewport={"width": 1700, "height": 1000})
    e = Ecran(ctx.new_page(), request.node.name)
    try:
        e.pg.goto(BAZA + "/", wait_until="domcontentloaded")
        r = e.pg.evaluate("async () => { const x = await fetch('/public/magic-login', {method: 'POST', headers: {'Content-Type': "
                          "'application/json'}, body: JSON.stringify({token: 'ml_inexistent608'})}); return [x.status, await x.json()]; }")
    finally:
        ctx.close()
    det = r[1].get("detail")
    det = det if isinstance(det, str) else json.dumps(det, ensure_ascii=False)
    # [integrare 560 + 608] un token inexistent: textul lui 560 („nu e valid”), cu literă mare și cu ce e de făcut
    assert r[0] == 401 and det.startswith("Linkul de logare nu e valid. Cere unul nou"), r


# ── 642 / „Înregistrează cabinetul tău” pe două coloane ─────────────────────────────────────────────────────────────────────────
def test_def_642_inregistrarea_pe_doua_coloane_incape_in_ecran(browser, request):
    """642 + „Înregistrează cabinetul tău pe două coloane” (decizia Costin: „confirmat”). Pașii, la 1280×720: linkul invitației ->
    „Continuă” -> formularul: CUI și denumirea pe același rând, emailul și telefonul pe același rând (două coloane); fereastra nu
    derulează, „Creează cont” e în ecran. ROȘU înainte (o coloană): 967 px de formular într-o fereastră de 672."""
    from conftest import _db
    from core import invitatii as inv
    email = "e2e.642col.%d@prisma-cont.test" % (int(time.time() * 1000) % 100000000)
    with _db().get_conn() as c, c.cursor() as cur:
        tok = inv.creeaza(cur, email, None)
        c.commit()
    ctx = browser.new_context(viewport=LAPTOP)
    e = Ecran(ctx.new_page(), request.node.name)
    try:
        pg = e.pg
        pg.goto(BAZA + "/#invitatie=" + tok, wait_until="domcontentloaded")
        pg.wait_for_selector("#pr-continua", timeout=20000)
        pg.click("#pr-continua")
        pg.wait_for_selector("#reg-buton", timeout=10000)
        pg.wait_for_timeout(400)
        e.captura()
        o = pg.evaluate("""() => { const t = (s) => document.querySelector(s).closest('label').getBoundingClientRect();
          const md = document.querySelector('#acces-modal'); const b = document.querySelector('#reg-buton').getBoundingClientRect();
          return {cui: t('#reg-cui').top, den: t('#reg-cabinet').top, email: t('#reg-email').top, tel: t('#reg-telefon').top,
                  cui_x: t('#reg-cui').left, den_x: t('#reg-cabinet').left, deruleaza: md.scrollHeight > md.clientHeight + 1,
                  buton: b.top >= 0 && b.bottom <= innerHeight}; }""")
        assert abs(o["cui"] - o["den"]) < 2 and o["den_x"] > o["cui_x"] + 100, o            # două coloane
        assert abs(o["email"] - o["tel"]) < 2, o
        assert not o["deruleaza"] and o["buton"], o
        assert not e.erori and not e.cereri_rele, (e.erori, e.cereri_rele)
    finally:
        ctx.close()
        sql("DELETE FROM public.invitatii_cabinet WHERE email = %s", (email,))
