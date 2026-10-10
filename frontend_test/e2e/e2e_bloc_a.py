# -*- coding: utf-8 -*-
"""Blocul A (DEFICIENTE.md 1–33) — deficiențele 04.10–05.10 probate în browser, pe aplicația pornită de `scripts/e2e_poarta.py`.

Conturile cu drepturi anume (asistent doar cu „Poate pregăti”, asistent fără bife, asistent fără firme, un cabinet separat) se creează
pe drumul aplicației (`repo_utilizatori.creeaza_cont_asistent`, `auth_api.inregistreaza_cabinet`) și se scot în același test — contul
comun `asistent` are „Poate pregăti” + „Poate valida”, deci nu e cazul din deficiențe. Datele scrise stau pe firma sintetică a rulării
(`firma_e2e`): profilul, numerotarea, nomenclatorul și stocul se pun prin rutele aplicației (din pagină, cu sesiunea contului).
Firma comună „Panificatie Salarii Speciale” (tenant_001) se folosește NUMAI la citire (Salariați).
"""
import base64
import contextlib
import datetime as _dt
import io
import re
import time

from conftest import ai_pregateste, ai_prompturi, _db, _ecran, sql, cui_cu_control, PREFIX_FIRMA

ecran_cont = contextlib.contextmanager(_ecran)
AZI = _dt.date.today()
T_PANIFICATIE = 4784          # tenant_001, „Panificatie Salarii Speciale SRL” — are salariați; doar citire
T_COMERT = 4838               # tenant_003, „Comert Micro TVA SRL” — doar citire (lista de firme)
SERIE = "E2EA"
PRODUS = "Servicii de consultanță contabilă E2E"   # „Servicii” clasifică linia pe 704 fără AI (plasa rulează cu AI simulat)
ARTICOL = "Marfa E2E Bloc A"
CLIENT = {"#em-cui": "14399840", "#em-nume": "DANTE INTERNATIONAL SA", "#em-adresa": "Șos. Virtuții 148, București"}


# ── conturi și cabinet de probă ─────────────────────────────────────────────────────────────────────────────────────────────
def _email(eticheta):
    return "e2e-bloc-a-%s-%d@prisma-cont.test" % (eticheta, int(time.time() * 1000000) % 1000000000)


@contextlib.contextmanager
def cont_asistent(pregati=True, valida=False, depune=False, firme=(), bun_venit_vazut=True, cabinet=1968, eticheta="asist"):
    """Un asistent al cabinetului, creat pe drumul aplicației (`creeaza_cont_asistent`), cu bifele cerute și firmele alocate
    (`leaga_contul_de_firma`); scos la final. `parola` e cea cu care se poate reautentifica."""
    from core import nucleu, repo_utilizatori
    db = _db()
    email, parola = _email(eticheta), "Parola-E2E-%d" % int(time.time())
    with db.get_conn() as c, c.cursor() as cur:
        uid = repo_utilizatori.creeaza_cont_asistent(cur, email, nucleu.hash_parola(parola), "Asistent E2E", cabinet, pregati, valida)[0]
        cur.execute("UPDATE public.users SET prenume = 'Ana', poate_depune = %s, parola_schimbata = true, "
                    "bun_venit_vazut_la = CASE WHEN %s THEN now() END WHERE id = %s", (bool(depune), bool(bun_venit_vazut), uid))
        for t in firme:
            repo_utilizatori.leaga_contul_de_firma(cur, uid, t)
        c.commit()
    try:
        yield {"id": uid, "email": email, "parola": parola}
    finally:
        _scoate_cont(uid)


def _scoate_cont(uid):
    try:
        sql("DELETE FROM public.users WHERE id = %s", (uid,))
    except Exception:  # noqa: BLE001 — un rând care îl numește (coada de declarații): contul rămâne, dezactivat
        sql("UPDATE public.users SET activ = false WHERE id = %s", (uid,))


@contextlib.contextmanager
def cabinet_separat(valida_admin=True):
    """Un cabinet NOU, pe drumul aplicației (`auth_api.inregistreaza_cabinet`: cabinetul + administratorul lui) — ca un contor al
    cabinetului să nu depindă de conturile pe care alte rulări le pun în cabinetul de test. Scos la final."""
    from core import auth_api
    db = _db()
    email = _email("admin")
    with db.get_conn() as c:
        r = auth_api.inregistreaza_cabinet(c, email, "Parola-E2E-%d" % time.time(), "Cabinet E2E Bloc A", nume="Admin", prenume="E2E")
        assert r.get("ok"), r
        with c.cursor() as cur:
            cur.execute("UPDATE public.users SET bun_venit_vazut_la = now(), parola_schimbata = true, poate_valida = %s WHERE id = %s",
                        (bool(valida_admin), r["user_id"]))
        c.commit()
    try:
        yield {"firm_id": r["firm_id"], "user_id": r["user_id"], "email": email}
    finally:
        for (uid,) in sql("SELECT id FROM public.users WHERE accounting_firm_id = %s", (r["firm_id"],)):
            _scoate_cont(uid)
        with contextlib.suppress(Exception):
            sql("DELETE FROM public.accounting_firms WHERE id = %s", (r["firm_id"],))


def aloca(uid, tenant_id):
    from core import repo_utilizatori
    db = _db()
    with db.get_conn() as c, c.cursor() as cur:
        repo_utilizatori.leaga_contul_de_firma(cur, uid, tenant_id)
        c.commit()


# ── utilitare de ecran ───────────────────────────────────────────────────────────────────────────────────────────────────────
def e_baza():
    from conftest import BAZA
    return BAZA + "/"


def _vizibile(pg, sel):
    return pg.eval_on_selector_all(sel, "els => els.filter(e => e.offsetParent !== null).length")


def _asteapta(cond, secunde=10):
    t0 = time.time()
    while time.time() - t0 < secunde:
        if cond():
            return
        time.sleep(0.2)
    assert cond(), "condiția n-a devenit adevărată în %ds" % secunde


def _api(e, metoda, cale, corp=None):
    """O cerere la aplicație din pagina contului (aceeași sesiune ca ecranul) — pentru pregătirea datelor pe drumul aplicației."""
    if not e.pg.url.startswith(e_baza()):
        e.acasa()
    return e.pg.evaluate("""async ([m, c, b]) => {
        const t = sessionStorage.getItem('iconta_token');
        const o = {method: m, headers: {Authorization: 'Bearer ' + t}};
        if (b !== null) { o.headers['Content-Type'] = 'application/json'; o.body = JSON.stringify(b); }
        const x = await fetch(c, o); let j = null; try { j = await x.json(); } catch (_) {}
        return {status: x.status, json: j};
    }""", [metoda, cale, corp])


def _ok(r, ce):
    assert r["status"] == 200, "%s: %s %s" % (ce, r["status"], r["json"])
    return r["json"]


def _deschide_firme(e):
    pg = e.pg
    e.acasa()
    pg.click("button.cab-card:has([data-cheie='firme'])")
    pg.wait_for_timeout(400)
    if pg.query_selector("#opt-existente"):
        pg.click("#opt-existente")
    pg.wait_for_selector("#firme-lista button.firme-rand, #firme-lista .firme-gol", timeout=20000)
    pg.wait_for_timeout(300)


def _card(e, cheie, asteapta):
    e.pg.click("#fa-" + cheie)
    e.pg.wait_for_selector(asteapta, timeout=25000)


def _deschide_emiterea(e, nume):
    e.firma(nume)
    _card(e, "facturi", "#fac-emite")
    e.pg.click("#fac-emite")
    e.pg.wait_for_selector("#em-cui", timeout=25000)
    e.pg.wait_for_timeout(500)


def _octeti(e, cale):
    """Octeții unui document cerut de ecran (aceeași cale, aceeași sesiune) — fereastra „blob:” deschisă de buton nu se poate citi."""
    b64 = e.pg.evaluate("""async (c) => {
        const t = sessionStorage.getItem('iconta_token');
        const x = await fetch(c, {headers: {Authorization: 'Bearer ' + t}});
        const b = new Uint8Array(await x.arrayBuffer()); let s = ''; for (const k of b) s += String.fromCharCode(k); return btoa(s);
    }""", cale)
    return base64.b64decode(b64)


def _pdf_ok(e, rr):
    """Răspunsul cererii făcute de buton e 200 + PDF, iar documentul de la aceeași cale începe cu %PDF-."""
    r = rr.value
    assert r.status == 200 and "application/pdf" in (r.headers.get("content-type") or ""), (r.status, r.headers)
    octeti = _octeti(e, "/" + r.url.split("//", 1)[1].split("/", 1)[1])
    assert octeti[:5] == b"%PDF-", octeti[:120]
    return octeti


def _pdf_text(octeti):
    from pypdf import PdfReader
    rd = PdfReader(io.BytesIO(octeti))
    return re.sub(r"\s+", " ", "\n".join(p.extract_text() for p in rd.pages)), (rd.metadata or {}).get("/Title")


# ── pregătirea firmei sintetice, pe rutele aplicației ───────────────────────────────────────────────────────────────────────
def _profil(firma, forma=True, platitor=True, caen="4711", amef=False):
    cui = sql("SELECT cui FROM public.tenants WHERE id = %s", (firma["tenant_id"],))[0][0]
    p = {"nume": firma["nume"], "cui": cui, "reg_com": "J40/1234/2015", "caen": caen, "adresa": "Str. Proba 1",
         "oras": "București", "judet": "B", "cod_postal": "010101", "banca": "Banca Proba", "iban": "RO49AAAA1B31007593840000",
         "telefon": "0712345678", "email": "", "patron_nume": "Ion Popescu", "declarant_nume": "Popescu",
         "declarant_prenume": "Ion", "declarant_functie": "Administrator", "cont_venit_implicit": "704",
         "metoda_stoc": "cantitativ_valoric", "serie_chitanta": "E2ECH",
         "activitate_exceptata_amef": "1" if amef else "0", "activitate_amef": None}
    if forma:
        p.update({"forma_juridica": "SRL", "capital_subscris": "200", "capital_varsat": None})
    return p


def pregateste_firma(e, firma, forma=True, platitor=True, caen="4711"):
    """Date firmă + vectorul fiscal + numerotarea facturilor + produsul din nomenclator, prin rutele pe care le cheamă ecranele
    (`POST firma-profil/date`, `POST vector`, `PUT facturi/numerotare`, `POST produse`). Idempotent: o valoare neschimbată nu scrie."""
    tid = firma["tenant_id"]
    _ok(_api(e, "POST", "/tenants/%d/firma-profil/date" % tid, _profil(firma, forma, platitor, caen)), "Date firmă")
    _ok(_api(e, "POST", "/tenants/%d/vector" % tid, {"regim_fiscal": "micro", "platitor_tva": platitor,
                                                     "tip_decont": "lunar" if platitor else None, "operatiuni_ic": False,
                                                     "inreg_art317": False, "tva_data_inceput": "2026-01-01" if platitor else None}),
        "vector fiscal")
    num = _ok(_api(e, "GET", "/tenants/%d/facturi/numerotare?data=%s" % (tid, AZI.isoformat())), "numerotare")
    if not num.get("serie"):
        _ok(_api(e, "PUT", "/tenants/%d/facturi/numerotare" % tid, {"serie": SERIE, "numar_start": 1}), "seria")
    for den, um, pret in ((PRODUS, "ora", 150.0), (ARTICOL, "buc", 20.0)):   # cota din nomenclator, fără apel AI la potrivire
        _ok(_api(e, "POST", "/tenants/%d/produse" % tid, {"denumire": den, "um": um, "pret_unitar": pret, "cota_tva": 21,
                                                         "confirmat": True}), "produs")


def scoate_forma_si_capitalul(e, firma):
    p = _profil(firma, forma=False)
    p.update({"forma_juridica": None, "capital_subscris": None, "capital_varsat": None})
    _ok(_api(e, "POST", "/tenants/%d/firma-profil/date" % firma["tenant_id"], p), "forma scoasă")


def articol_in_stoc(e, firma, cantitate=10, pret=12.5):
    """Un articol cu stoc (intrarea din „Mișcări, fișe de magazie”, ruta `stocuri/intrare`); întoarce id-ul lui."""
    tid = firma["tenant_id"]
    arts = _ok(_api(e, "GET", "/tenants/%d/stocuri/articole" % tid), "articole")["articole"]
    for a in arts:
        if a["denumire"] == ARTICOL:
            return a["id"]
    r = _ok(_api(e, "POST", "/tenants/%d/stocuri/intrare" % tid, {"denumire": ARTICOL, "um": "buc", "data": AZI.isoformat(),
                                                                  "cantitate": cantitate, "pret_unitar": pret,
                                                                  "document": "NIR E2E 1"}), "intrare stoc")
    return r["articol_id"]


def emite_api(e, firma, linii=None, pleaca_marfa=None, scadenta=True):
    """O factură emisă pe ruta formularului (`POST facturi/emite`), cu payload-ul pe care îl trimite ecranul."""
    corp = {"linii": linii or [{"descriere": PRODUS, "cantitate": 2, "um": "ora", "pret_unitar": 150.0, "cota_tva": 21,
                                "cota_propusa": 21, "articol_id": None}],
            "tert_nume": CLIENT["#em-nume"], "tert_cui": CLIENT["#em-cui"], "tert_adresa": CLIENT["#em-adresa"], "moneda": "RON",
            "tert_tara": "RO", "tip_operatiune": "normal", "bon_fiscal_nr": None, "bon_fiscal_data": None,
            "data_emitere": AZI.isoformat(), "data_scadenta": (AZI + _dt.timedelta(days=30)).isoformat() if scadenta else None,
            "tip": "factura"}
    if pleaca_marfa is not None:
        corp["pleaca_marfa"] = pleaca_marfa
    return _ok(_api(e, "POST", "/tenants/%d/facturi/emite" % firma["tenant_id"], corp), "emitere")


def _deschide_factura(e, firma, factura_id):
    e.firma(firma["nume"])
    _card(e, "facturi", "#fac-istoric")
    e.pg.click("#fac-istoric")
    e.pg.wait_for_selector(".fac-frand-btn[data-id='%s']" % factura_id, timeout=25000)
    e.pg.click(".fac-frand-btn[data-id='%s']" % factura_id)
    e.pg.wait_for_selector("#fd-pdf", timeout=25000)


def _pachet(e, firma, an, luna):
    """Pachete lunare -> firma -> luna -> „Continuă” -> „Scrie/Deschide povestea”: fereastra poveștii."""
    pg = e.pg
    e.acasa()
    pg.click("button.cab-card:has([data-cheie='pachete'])")
    pg.wait_for_selector("#pac-firma", timeout=20000)
    pg.select_option("#pac-firma", str(firma["tenant_id"]))
    pg.fill("#pac-an", str(an))
    pg.dispatch_event("#pac-an", "change")
    pg.select_option("#pac-luna", str(luna))
    pg.click("#pac-continua")
    pg.wait_for_selector("#pac-deschide", timeout=25000)


def _deschide_povestea(e):
    e.pg.click("#pac-deschide")
    e.pg.wait_for_selector(".pacm #pacm-text", timeout=15000)
    e.pg.wait_for_timeout(300)


# ── 04.10 — drepturile asistentului ─────────────────────────────────────────────────────────────────────────────────────────
def test_def_1_asistentul_afla_de_ce_nu_poate_adauga_firma(browser, request):
    """1. Firme: asistentul junior apasă „Adaugă firma” și nu se întâmplă nimic, fără niciun mesaj.
    Pașii contabilului: asistentul cu „Poate pregăti” (o firmă alocată) deschide Firme. Nu i se mai oferă un buton care nu face nimic:
    „+ Adaugă firmă” nu apare, iar ecranul spune de ce (adăugarea o face doar administratorul cabinetului)."""
    with cont_asistent(firme=(T_COMERT,)) as a, ecran_cont(browser, request, a["email"]) as e:
        _deschide_firme(e)
        pg = e.pg
        assert _vizibile(pg, "#firme-adauga") == 0, "asistentului i se oferă „+ Adaugă firmă”"
        pg.wait_for_selector(".fereastra-corp .drept-motiv", timeout=10000)
        motiv = pg.inner_text(".fereastra-corp .drept-motiv")
        e.captura()
        assert "doar administratorul cabinetului" in motiv, motiv


def test_def_2_asistentul_nu_vede_actiunile_de_administrator_pe_firme(browser, request):
    """2. Firme: asistentului i se afișează „+ Adaugă firmă”, „Import în masă” și „Scoate”, acțiuni de administrator.
    Pașii contabilului: asistentul cu „Poate pregăti” deschide Firme: vede firma alocată, dar niciuna din cele trei acțiuni."""
    with cont_asistent(firme=(T_COMERT,)) as a, ecran_cont(browser, request, a["email"]) as e:
        _deschide_firme(e)
        pg = e.pg
        assert "Comert Micro TVA" in pg.inner_text("#firme-lista")
        e.captura()
        vazute = {s: _vizibile(pg, s) for s in ("#firme-adauga", "#firme-import-masa", ".firme-rand-scoate")}
        assert vazute == {"#firme-adauga": 0, "#firme-import-masa": 0, ".firme-rand-scoate": 0}, vazute
        assert "Butonul Scoate" not in e.fereastra()


def test_def_3_email_client_al_unui_cont_cu_alt_rol_e_refuzat_pe_camp(patron):
    """3. Firme: „Email client” acceptă fără avertisment emailul unui cont existent cu alt rol.
    Pașii contabilului: administratorul deschide Firme -> „+ Adaugă firmă”, tastează un CUI, denumirea, tipul, iar la „Email client”
    adresa asistentului cabinetului (cont cu alt rol). La „Adaugă firma” refuzul apare pe câmp, firma NU se creează."""
    pg = patron.pg
    cui = cui_cu_control(98000000 + int(time.time()) % 999999)
    nume = "%s Email Rol %s SRL" % (PREFIX_FIRMA, cui)
    try:
        _deschide_firme(patron)
        pg.click("#firme-adauga")
        pg.wait_for_selector("#fn-cui", timeout=10000)
        pg.fill("#fn-cui", cui)
        pg.wait_for_function("() => !document.querySelector('#fn-salveaza').disabled", timeout=30000)
        pg.fill("#fn-nume", nume)
        pg.select_option("#fn-tip", "srl")
        pg.fill("#fn-email", "asistent@prisma-cont.test")
        pg.click("#fn-salveaza")
        pg.wait_for_function("() => (document.querySelector('#fn-msg') || {}).textContent", timeout=20000)
        patron.captura()
        pe_camp = pg.eval_on_selector_all(".msg-eroare[data-camp='fn-email']", "els => els.map(e => e.textContent)")
        assert pe_camp and "aparține deja unui cont cu alt rol" in pe_camp[0], pe_camp
        assert pg.get_attribute("#fn-email", "aria-invalid") == "true"
        assert "Firma nu s-a creat" in pg.inner_text("#fn-msg")
        assert sql("SELECT count(*) FROM public.tenants WHERE cui = %s", (cui,)) == [(0,)], "firma s-a creat"
    finally:
        from conftest import _scoate_firmele_e2e
        for (tid,) in sql("SELECT id FROM public.tenants WHERE cui = %s AND nume LIKE %s", (cui, PREFIX_FIRMA + "%")):
            _scoate_firmele_e2e(tid)


def test_def_4_bun_venit_se_inchide_din_x_si_cu_esc(browser, request):
    """4. Bun venit: fereastra se închide doar de la butonul de jos; lipsesc X și Esc.
    Pașii contabilului: la prima intrare apare „Bun venit”, cu X în antet; Esc o închide; la o nouă primă intrare, X o închide.
    Închiderea o marchează văzută (nu reapare). [retestul Costin 09.10: testul vechi trecea pe defect — proba doar „Bun venit”]
    Aceeași prezentare, deschisă din semnul „?” al barei („Prezentarea aplicației”), se închide și ea cu Esc."""
    with cont_asistent(firme=(T_COMERT,), bun_venit_vazut=False) as a:
        with ecran_cont(browser, request, a["email"]) as e:
            pg = e.pg
            pg.goto(e_baza(), wait_until="domcontentloaded")
            pg.wait_for_selector(".bun-venit-overlay .ans-continut", timeout=30000)
            assert pg.is_visible(".bun-venit-antet button.nav-x[aria-label='Închide']"), "fără X în antet"
            e.captura("deschis")
            pg.keyboard.press("Escape")
            pg.wait_for_selector(".bun-venit-overlay", state="detached", timeout=10000)
            e.captura("dupa_esc")
        _asteapta(lambda: sql("SELECT bun_venit_vazut_la IS NOT NULL FROM public.users WHERE id = %s", (a["id"],)) == [(True,)])
        sql("UPDATE public.users SET bun_venit_vazut_la = NULL WHERE id = %s", (a["id"],))
        with ecran_cont(browser, request, a["email"]) as e:
            pg = e.pg
            pg.goto(e_baza(), wait_until="domcontentloaded")
            pg.wait_for_selector(".bun-venit-antet .nav-x", timeout=30000)
            pg.click(".bun-venit-antet .nav-x")
            pg.wait_for_selector(".bun-venit-overlay", state="detached", timeout=10000)
            e.captura("dupa_x")
            # [retestul Costin 09.10] aceeași prezentare, deschisă din semnul „?” al barei („Prezentarea aplicației”): Esc o închide
            pg.click("#nav-ghid")
            pg.wait_for_selector(".fereastra .ans-continut", timeout=20000)
            e.captura("prezentarea_deschisa")
            pg.keyboard.press("Escape")
            pg.wait_for_selector(".fereastra .ans-continut", state="detached", timeout=10000)
            e.captura("prezentarea_dupa_esc")


def test_def_5_ghidul_e_pe_rol_iar_asistentul_fara_firme_primeste_mesaj(browser, request, patron):
    """5. Bun venit: ghidul e același pentru toate rolurile; asistentul fără firme nu primește un mesaj potrivit.
    Pașii contabilului: (a) asistentul fără firme alocate intră prima oară: „Nu ai firme asociate…”, fără fir de pași; (b) asistentul
    cu firme și „Poate pregăti”: firul începe de la datele firmei (fără pasul „Firme”, al administratorului); (c) administratorul,
    din semnul „?” al barei: firul începe cu „Firme”."""
    with cont_asistent(firme=(), bun_venit_vazut=False, eticheta="farafirme") as a, ecran_cont(browser, request, a["email"]) as e:
        e.pg.goto(e_baza(), wait_until="domcontentloaded")
        e.pg.wait_for_selector(".bun-venit-overlay .ans-continut", timeout=30000)
        txt = e.pg.inner_text(".bun-venit-overlay")
        e.captura("fara_firme")
        assert "Nu ai firme asociate" in txt, txt[:300]
        assert e.pg.query_selector(".bun-venit-overlay .ans-fir") is None, "asistentul fără firme primește firul de pași"
    with cont_asistent(firme=(T_COMERT,), bun_venit_vazut=False) as a, ecran_cont(browser, request, a["email"]) as e:
        e.pg.goto(e_baza(), wait_until="domcontentloaded")
        e.pg.wait_for_selector(".bun-venit-overlay .ans-pas-titlu", timeout=30000)
        pasi_asist = e.pg.eval_on_selector_all(".bun-venit-overlay .ans-pas-titlu", "els => els.map(e => e.textContent.trim())")
        e.captura("asistent")
    patron.acasa()
    patron.pg.click("#nav-ghid")
    patron.pg.wait_for_selector(".fereastra-corp .ans-pas-titlu", timeout=20000)
    pasi_admin = patron.pg.eval_on_selector_all(".fereastra-corp .ans-pas-titlu", "els => els.map(e => e.textContent.trim())")
    patron.captura("admin")
    assert pasi_admin[0] == "Firme", pasi_admin
    assert "Firme" not in pasi_asist and "Vector fiscal" in pasi_asist, pasi_asist
    # [retestul Costin 09.10] „Ana vede în catalog funcții de administrator”: catalogul „Ce cuprinde aplicația” al asistentului nu
    # are funcțiile administratorului de cabinet, nici pe ale platformei; administratorul cabinetului le are pe ale lui
    ADMIN_CABINET = {"Chei API publice per cabinet", "Contabilii și asistenții cabinetului", "Exportul datelor cabinetului, din aplicație"}
    PLATFORMA = {"Suspendare cabinet", "Alerte sănătate server"}
    with cont_asistent(firme=(T_COMERT,)) as a, ecran_cont(browser, request, a["email"]) as e:
        e.acasa()
        e.pg.click("#nav-ghid")
        e.pg.wait_for_selector(".fereastra .ans-grupa-lista li", timeout=20000)
        cat_asist = set(e.pg.eval_on_selector_all(".fereastra .ans-grupa-lista li",
                                                  "els => els.filter(x => x.offsetParent !== null).map(x => x.childNodes[0].textContent.trim())"))
        e.captura("catalog_asistent")
    cat_admin = set(patron.pg.eval_on_selector_all(".fereastra .ans-grupa-lista li",
                                                   "els => els.filter(x => x.offsetParent !== null).map(x => x.childNodes[0].textContent.trim())"))
    assert len(cat_asist) > 50 and "Generare contracte" in cat_asist, "anti-vacuu: catalogul asistentului n-a fost citit"
    assert not (ADMIN_CABINET | PLATFORMA) & cat_asist, sorted((ADMIN_CABINET | PLATFORMA) & cat_asist)
    assert ADMIN_CABINET <= cat_admin and not PLATFORMA & cat_admin, (sorted(ADMIN_CABINET - cat_admin), sorted(PLATFORMA & cat_admin))


def test_def_6_contorul_asistenti_nu_numara_administratorul(browser, request):
    """6. Asistenți: contorul îl numără pe administrator printre asistenți.
    Pașii contabilului: într-un cabinet cu un administrator și un singur asistent, administratorul deschide Asistenți: contorul spune
    „1 administrator · 1 asistent (1 activ)”, nu „2 asistenți”."""
    with cabinet_separat() as cab, cont_asistent(cabinet=cab["firm_id"], eticheta="cab"), \
            ecran_cont(browser, request, cab["email"]) as e:
        e.acasa()
        e.pg.click("button.cab-card:has([data-cheie='asistenti'])")
        e.pg.wait_for_selector(".asi-sumar", timeout=20000)
        sumar = e.pg.inner_text(".asi-sumar")
        e.captura()
        assert sumar.strip() == "1 administrator · 1 asistent (1 activ)", sumar


def test_def_7_bun_venit_fara_termenul_de_48_de_ore(browser, request):
    """7. Bun venit: textul „se rezolvă în maximum 48 de ore” e un angajament public nedecis.
    Pașii contabilului: la prima intrare citește „Bun venit”: fraza despre cardul „Raportează” (fost „Suport”, deficiența 202) rămâne,
    fără niciun termen de rezolvare."""
    with cont_asistent(firme=(T_COMERT,), bun_venit_vazut=False) as a, ecran_cont(browser, request, a["email"]) as e:
        e.pg.goto(e_baza(), wait_until="domcontentloaded")
        e.pg.wait_for_selector(".bun-venit-overlay .ans-continut", timeout=30000)
        txt = e.pg.inner_text(".bun-venit-overlay")
        e.captura()
        fraza = [p for p in txt.split("\n") if "cardul „Raportează”" in p]   # [deficiența 202] cardul se numește „Raportează”
        assert fraza, txt[:400]
        assert "48 de ore" not in txt and not re.search(r"\b\d+\s+(?:de\s+)?(?:ore|zile)\b", fraza[0]), fraza


def test_def_8_asistentul_cu_poate_pregati_face_munca_zilnica(browser, request, patron, firma_e2e):
    """8. Drepturi: asistentul era refuzat de server la circa 50 de operații zilnice.
    Pașii contabilului: asistentul cu „Poate pregăti” (firma alocată) face munca curentă: o dispoziție în Casă și o notă contabilă
    nouă în Registrul jurnal — ambele trec (ciorne), fără refuz. Lista acțiunilor pe care serverul i le refuză nu cuprinde nicio
    operație curentă (factură, chitanță, casă, notă, import extras, stoc, NIR, pontaj, export SAGA, e-Transport)."""
    pregateste_firma(patron, firma_e2e)
    with cont_asistent(firme=(firma_e2e["tenant_id"],)) as a, ecran_cont(browser, request, a["email"]) as e:
        pg = e.pg
        e.acasa()
        refuzate = set(_ok(_api(e, "GET", "/eu/drepturi"), "drepturi")["interzise"])
        zilnice = {"POST /tenants/{tenant_id}/facturi/emite", "POST /tenants/{tenant_id}/chitante",
                   "POST /tenants/{tenant_id}/casa/operatiuni", "POST /tenants/{tenant_id}/jurnal",
                   "POST /tenants/{tenant_id}/banca/reconciliere/import", "POST /tenants/{tenant_id}/stocuri/intrare",
                   "POST /tenants/{tenant_id}/stocuri/nir", "POST /tenants/{tenant_id}/pontaj/confirma",
                   "POST /tenants/{tenant_id}/facturi/export-saga"}
        assert not (zilnice & refuzate), sorted(zilnice & refuzate)
        e.firma(firma_e2e["nume"])
        _card(e, "casa", "#c-toggle")
        pg.click("#c-toggle")
        pg.fill("#c-data", AZI.isoformat())
        pg.select_option("#c-cat", "incasare_client")
        pg.fill("#c-suma", "321.00")
        pg.fill("#c-part", "Client Asistent E2E SRL")
        pg.fill("#c-doc", "DI E2E 8")
        pg.click("#c-adauga")
        pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('321,00')", timeout=20000)
        e.captura("casa")
        pg.click(".nav-sageata.nav-inapoi")
        _card(e, "jurnal", "#j-nota-noua")
        pg.click("#j-nota-noua")
        pg.wait_for_selector("#je-salveaza", timeout=10000)
        pg.fill("#je-data", AZI.isoformat())
        pg.fill("#je-desc", "Notă asistent E2E 8")
        pg.fill("#je-doc", "Proces-verbal E2E 8")
        pg.fill(".je-deb", "6022")
        pg.fill(".je-cre", "5311")
        pg.fill(".je-sum", "45.00")
        pg.click("#je-salveaza")
        pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('Notă asistent E2E 8')",
                             timeout=20000)
        e.captura("jurnal")
    s = firma_e2e["schema"]
    assert sql('SELECT count(*) FROM "%s".casa_operatiuni WHERE document = %%s' % s, ("DI E2E 8",)) == [(1,)]
    assert sql('SELECT status FROM "%s".inregistrari WHERE descriere = %%s' % s, ("Notă asistent E2E 8",)) == [("ciorna",)]


def test_def_9_asistentul_vede_pdf_chitanta_si_fluturasul(browser, request, patron, firma_e2e):
    """9. Drepturi: asistentul putea emite chitanțe și certifica bonuri, dar nu vedea PDF-ul chitanței, poza bonului și fluturașul.
    Pașii contabilului: asistentul cu „Poate pregăti” deschide o factură emisă -> „Emite chitanță” -> „PDF chitanță”: PDF-ul se
    deschide; în Salariați (firmă cu salariați alocată) apasă „Fluturaș”: PDF-ul vine; fotografia unui bon al firmei (din directorul de
    bonuri al plasei, separat de producție — `ICONTA_BON_DIR`, comanda 09.10 pct.7) vine și ea, ca imagine."""
    pregateste_firma(patron, firma_e2e)
    f = emite_api(patron, firma_e2e)
    with cont_asistent(firme=(firma_e2e["tenant_id"], T_PANIFICATIE)) as a, ecran_cont(browser, request, a["email"]) as e:
        pg = e.pg
        _deschide_factura(e, firma_e2e, f["factura_id"])
        pg.click("#fd-chitanta")
        pg.wait_for_selector("#fd-chit-ok", timeout=10000)
        pg.click("#fd-chit-ok")
        pg.wait_for_selector("[data-chpdf]", timeout=20000)
        with pg.expect_response(lambda r: "/chitante/" in r.url and r.url.endswith("/pdf"), timeout=30000) as rr:
            pg.click("[data-chpdf]")
        _pdf_ok(e, rr)
        e.captura("chitanta")
        e.firma("Panificatie Salarii Speciale")
        _card(e, "salariati", "[data-flut]")
        with pg.expect_response(lambda r: "/fluturas/" in r.url, timeout=30000) as rr:
            pg.click("[data-flut] >> nth=0")
        _pdf_ok(e, rr)
        e.captura("fluturas")
        # [retestul 09.10, pct.7: directorul separat al bonurilor] fotografia bonului, pe drumul ecranului (`pozaUrl`: cererea imaginii)
        import os as _os
        bid = sql('INSERT INTO "%s".bonuri (comerciant, data, total, nr_imagini, tip) VALUES (\'Magazin Probă E2E\', CURRENT_DATE, 12.10, 1, '
                  "'bon') RETURNING id" % firma_e2e["schema"])[0][0]
        d = _os.path.join(_os.environ["ICONTA_BON_DIR"], firma_e2e["schema"], str(bid))
        _os.makedirs(d, exist_ok=True)
        jpeg = bytes.fromhex("ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c"
                             "1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432ffc0000b080001000101011100ffc4001f0000010501010101"
                             "010100000000000000000102030405060708090a0bffda0008010100003f00d2cf20ffd9")
        open(_os.path.join(d, "img_1.jpg"), "wb").write(jpeg)
        st, tip, n = pg.evaluate("""async (u) => { const t = sessionStorage.getItem('iconta_token');
          const x = await fetch(u, {headers: {'Authorization': 'Bearer ' + t}}); const b = await x.arrayBuffer();
          return [x.status, x.headers.get('content-type'), b.byteLength]; }""", "/tenants/%d/bonuri/%d/imagine/1" % (firma_e2e["tenant_id"], bid))
        assert st == 200 and (tip or "").startswith("image/") and n == len(jpeg), (st, tip, n)


def test_def_10_schimbarea_regimului_de_tva_e_jurnalizata(browser, request, patron, firma_e2e):
    """10. Drepturi: schimbarea regimului de TVA nu era jurnalizată (cine, când, vechi → nou).
    Pașii contabilului: asistentul cu „Poate pregăti” deschide Date firmă la o firmă neplătitoare, alege „Înregistrată în scopuri
    de TVA: Da” cu periodicitatea lunară și salvează. În „Istoricul modificărilor” apare rândul: azi, Ana (asistentul),
    „Plătitor de TVA”, nu -> da."""
    pregateste_firma(patron, firma_e2e, platitor=False)
    with cont_asistent(firme=(firma_e2e["tenant_id"],)) as a, ecran_cont(browser, request, a["email"]) as e:
        pg = e.pg
        e.firma(firma_e2e["nume"])
        _card(e, "datefirma", "#df-salveaza")
        pg.select_option("#vf-platitor_tva", "da")
        pg.select_option("#vf-tip_decont", "lunar")
        if pg.is_visible("#vf-tva_data_inceput"):
            pg.fill("#vf-tva_data_inceput", "2026-01-01")
        pg.click("#df-salveaza")
        pg.wait_for_selector("#df-jurnal", timeout=20000)
        pg.wait_for_function("() => ((document.querySelector('#df-msg') || {}).textContent || '').includes('salvate')", timeout=20000)
        randuri = pg.eval_on_selector_all("#df-jurnal tbody tr", "trs => trs.map(t => [...t.cells].map(c => c.innerText.trim()))")
        pg.locator("#df-jurnal").scroll_into_view_if_needed()
        e.captura()
        tva = [r for r in randuri if r[2] == "Plătitor de TVA"]
        assert tva, randuri
        assert tva[0][1] == "Ana Asistent E2E" and tva[0][3:] == ["nu", "da"], tva[0]
        assert tva[0][0].startswith(AZI.strftime("%d.%m.%Y")), tva[0]


def test_def_11_reges_trimiterea_la_poate_depune_credentialele_la_administrator(browser, request):
    """11. Drepturi: REGES — trimiterea la „Poate depune”, credențialele doar la administrator.
    Pașii contabilului: în Salariați (firmă cu salariați), asistentul DOAR cu „Poate pregăti” nu vede nici „REGES” pe salariați, nici
    „Răspunsuri REGES”, nici „Chei REGES”; asistentul cu „Poate depune” vede „REGES” și „Răspunsuri REGES”, dar nu „Chei REGES”."""
    def numara(a):
        with ecran_cont(browser, request, a["email"]) as e:
            e.firma("Panificatie Salarii Speciale")
            _card(e, "salariati", "[data-flut]")
            r = {s: _vizibile(e.pg, s) for s in ("[data-reges]", "#sp-reges-poll", "#sp-reges-cfg")}
            # [retestul Costin 09.10] textul nu trimite la un buton pe care contul nu-l are („Chei REGES” e al administratorului)
            r["text_chei"] = "Chei REGES" in e.fereastra()
            e.captura("depune" if a.get("depune") else "pregatire")
            return r
    with cont_asistent(firme=(T_PANIFICATIE,)) as a:
        doar_pregatire = numara(a)
    with cont_asistent(firme=(T_PANIFICATIE,), depune=True, eticheta="depune") as a:
        a["depune"] = True
        cu_depunere = numara(a)
    assert doar_pregatire == {"[data-reges]": 0, "#sp-reges-poll": 0, "#sp-reges-cfg": 0, "text_chei": False}, doar_pregatire
    assert cu_depunere["[data-reges]"] > 0 and cu_depunere["#sp-reges-poll"] == 1 and cu_depunere["#sp-reges-cfg"] == 0, cu_depunere
    assert cu_depunere["text_chei"] is False, "asistentului i se spune să configureze „Chei REGES”, buton pe care nu-l are"


# ── 05.10 — Povestea lunii, Asistenți, meniu, Pachete ──────────────────────────────────────────────────────────────────────
def test_def_13_aproba_si_trimite_cer_poate_valida(browser, request, firma_e2e):
    """13. Povestea lunii: „Aprobă” și „Trimite” erau la „Poate pregăti”.
    Pașii contabilului: asistentul DOAR cu „Poate pregăti” deschide Pachete lunare -> firma -> povestea: poate scrie și salva ciorna,
    dar „Aprobă” și „Trimite” nu i se arată (cer „Poate valida”), iar motivul e scris în fereastră."""
    with cont_asistent(firme=(firma_e2e["tenant_id"],)) as a, ecran_cont(browser, request, a["email"]) as e:
        _pachet(e, firma_e2e, AZI.year, AZI.month)
        _deschide_povestea(e)
        pg = e.pg
        r = {s: _vizibile(pg, s) for s in ("#pacm-salveaza", "#pacm-gen", "#pacm-aproba", "#pacm-trimite")}
        motiv = pg.inner_text(".pacm .drept-motiv")
        e.captura()
        assert r == {"#pacm-salveaza": 1, "#pacm-gen": 1, "#pacm-aproba": 0, "#pacm-trimite": 0}, r
        assert "«Poate valida»" in motiv, motiv


def test_def_14_fara_drept_povestea_explica_de_ce_lipsesc_butoanele(browser, request, firma_e2e):
    """14. Povestea lunii: fără drept, fereastra apărea fără butoane și fără explicație.
    Pașii contabilului: asistentul FĂRĂ nicio bifă (firma alocată) deschide povestea lunii: nu vede acțiunile, dar fereastra spune de
    ce — cer drepturile «Poate pregăti» și «Poate valida», pe care le acordă administratorul din Asistenți."""
    with cont_asistent(pregati=False, firme=(firma_e2e["tenant_id"],), eticheta="farabife") as a, \
            ecran_cont(browser, request, a["email"]) as e:
        _pachet(e, firma_e2e, AZI.year, AZI.month)
        _deschide_povestea(e)
        pg = e.pg
        acte = {s: _vizibile(pg, s) for s in ("#pacm-salveaza", "#pacm-gen", "#pacm-aproba", "#pacm-trimite")}
        assert acte == {"#pacm-salveaza": 0, "#pacm-gen": 0, "#pacm-aproba": 0, "#pacm-trimite": 0}, acte
        assert _vizibile(pg, ".pacm .drept-motiv") == 1
        motiv = pg.inner_text(".pacm .drept-motiv")
        e.captura()
        assert "«Poate pregăti»" in motiv and "«Poate valida»" in motiv and "Asistenți" in motiv, motiv


def test_def_142_cd_cere_poate_valida(browser, request, patron, firma_e2e):
    """142. Mijloace fixe: C&D schimbabil de asistentul junior.
    [partea rămasă, registrul: „nu există un cont numai cu «Poate pregăti» pe care să se arate că butonul C&D e ascuns sau refuzat”]
    Pașii: un mijloc fix în registrul firmei -> asistentul NUMAI cu „Poate pregăti”, cu firma alocată, deschide Mijloace fixe ->
    „Acțiuni”: „C&D: nu” nu i se oferă (decizia Costin 08.10 W4: „schimbă regimul fiscal al activului și cere «Poate valida»”), iar
    cererea directă pe aceeași rută e refuzată și bifa rămâne „nu”. Contabilul-șef, pe același activ, are butonul."""
    from decimal import Decimal
    from core import db, repo_mijloace_fixe
    with db.get_conn(firma_e2e["schema"]) as c:
        with c.cursor() as cur:
            mid = repo_mijloace_fixe.adauga_cu_reevaluare(cur, firma_e2e["schema"], "MF142", "Utilaj de probă MF142", "2131", "2813",
                                                          Decimal("3000"), Decimal(0), 36, "2026-05-10", "liniara")[0]
        c.commit()
    sel = "button[data-cd='%s']" % mid

    def deschide(e):
        e.firma(firma_e2e["nume"])
        e.pg.click("#fa-mijloace")
        e.pg.wait_for_selector(sel, state="attached", timeout=20000)
        e.pg.evaluate("(s) => document.querySelector(s).closest('details').open = true", sel)

    with cont_asistent(firme=(firma_e2e["tenant_id"],), eticheta="junior142") as a, ecran_cont(browser, request, a["email"]) as e:
        deschide(e)
        st = e.pg.evaluate("""(s) => { const b = document.querySelector(s);
          return {vizibil: b.offsetParent !== null, refuzat: b.classList.contains('drept-refuzat')}; }""", sel)
        e.captura("asistent")
        assert st == {"vizibil": False, "refuzat": True}, st
        cod = e.pg.evaluate("""async ([u]) => { const t = sessionStorage.getItem('iconta_token');
          const x = await fetch(u, {method: 'PUT', headers: {'Authorization': 'Bearer ' + t, 'Content-Type': 'application/json'},
            body: JSON.stringify({destinatie_cd: 'da'})}); return x.status; }""",
                            ["/tenants/%d/mijloace-fixe/%d/destinatie-cd" % (firma_e2e["tenant_id"], mid)])
        assert cod == 403, cod
    assert sql('SELECT destinatie_cd FROM "%s".mijloace_fixe WHERE id = %%s' % firma_e2e["schema"], (mid,)) == [(False,)]
    deschide(patron)
    assert patron.pg.locator(sel).is_visible()


def test_def_15_administratorul_apare_cu_toate_drepturile(browser, request):
    """15. Asistenți: administratorul apărea cu „Poate valida” nebifat.
    Pașii contabilului: într-un cabinet al cărui administrator are în bază „Poate valida” nebifat (cazul din producție), acesta deschide
    Asistenți: rândul lui arată toate cele trei drepturi active; la „Editează”: „are toate drepturile… Nu se bifează”."""
    with cabinet_separat(valida_admin=False) as cab, ecran_cont(browser, request, cab["email"]) as e:
        e.acasa()
        e.pg.click("button.cab-card:has([data-cheie='asistenti'])")
        e.pg.wait_for_selector("#asi-lista .asi-perm", timeout=20000)
        pastile = e.pg.eval_on_selector_all("#asi-lista .val-card .asi-perm", "els => els.map(e => [e.className, e.textContent.trim()])")
        e.captura()
        assert len(pastile) == 3 and all("asi-perm-on" in c for c, _t in pastile), pastile
        assert any("valida" in t for _c, t in pastile), pastile


def test_def_16_raporteaza_are_iconita(browser, request):
    """16. Meniu: „Raportează” nu avea iconiță.
    Pașii contabilului: asistentul își vede meniul: „Raportează” are o iconiță desenată (în arbore și pe card), ca restul."""
    with cont_asistent(firme=(T_COMERT,)) as a, ecran_cont(browser, request, a["email"]) as e:
        e.acasa()
        forme = e.pg.eval_on_selector_all(".asi-nod[data-nod='raport'] svg, button.cab-card:has([data-cheie='raport']) svg",
                                          "els => els.map(s => s.querySelectorAll('path,circle,rect,line,polyline,polygon').length)")
        e.pg.locator(".asi-nod[data-nod='raport']").scroll_into_view_if_needed()
        e.captura()
        assert len(forme) == 2 and all(n > 0 for n in forme), forme


def test_def_17_pachete_alegerea_firmei_o_singura_data(patron):
    """17. Pachete lunare: alegerea firmei apărea de două ori.
    Pașii contabilului: deschide Pachete lunare: firma se alege dintr-un singur control (lista), fără o a doua căsuță de căutare."""
    patron.acasa()
    patron.pg.click("button.cab-card:has([data-cheie='pachete'])")
    patron.pg.wait_for_selector("#pac-firma", timeout=20000)
    controale = patron.pg.eval_on_selector_all(".dec-form > label.camp input, .dec-form > label.camp select, "
                                               ".dec-form input[placeholder*='firm' i]", "els => els.map(e => e.id)")
    patron.captura()
    assert controale == ["pac-firma"], controale


def test_def_18_povestea_goala_email_cu_cifre_si_trimite_inactiv(patron, firma_e2e):
    """18. Pachete lunare: „Vezi ca email” cu povestea goală arăta o casetă goală; „Trimite” rămânea activ.
    Pașii contabilului: deschide povestea unei luni fără poveste: „Trimite” e inactiv și motivul se vede („povestea e goală”);
    „Vezi ca email” arată emailul cu cifrele pachetului (Venituri, Cheltuieli, Rezultat…) și spune că povestea nu e scrisă."""
    _pachet(patron, firma_e2e, 2099, 1)
    _deschide_povestea(patron)
    pg = patron.pg
    assert pg.is_disabled("#pacm-trimite")
    assert "povestea e goală" in pg.inner_text("#pacm-motiv-trimite")
    pg.click("#pacm-vezi")
    pg.wait_for_function("() => document.querySelector('#pacm-preview').innerText.includes('Cheltuieli')", timeout=20000)
    txt = pg.inner_text("#pacm-preview")
    patron.captura()
    for t in ("Venituri", "Cheltuieli", "Rezultat înainte de impozit", "Declarații depuse", "Povestea lunii nu e scrisă încă."):
        assert t in txt, (t, txt[:500])


def test_def_31_povestea_fara_marcaje_in_caseta_si_in_email(patron, firma_e2e):
    """31. Povestea lunii: marcajele „**” apăreau ca atare în casetă și în email.
    Pașii contabilului: scrie în poveste un text cu marcaje („**Veniturile** … # Titlu … *bine*”), apasă „Vezi ca email”: emailul
    le arată fără marcaje; „Salvează ciornă”, apoi redeschide: caseta are textul fără marcaje."""
    _pachet(patron, firma_e2e, 2099, 2)
    _deschide_povestea(patron)
    pg = patron.pg
    pg.fill("#pacm-text", "# Titlu lunii\n**Veniturile** lunii au fost *bine* urmărite. __Rezultatul__ e în pachet.")
    pg.click("#pacm-vezi")
    pg.wait_for_function("() => document.querySelector('#pacm-preview').innerText.includes('Veniturile')", timeout=20000)
    mail = pg.inner_text("#pacm-preview")
    patron.captura("email")
    assert "**" not in mail and "__" not in mail and "# Titlu" not in mail and "*bine*" not in mail, mail
    assert "Veniturile lunii au fost bine urmărite" in mail, mail
    pg.click("#pacm-vezi")
    pg.click("#pacm-salveaza")
    pg.wait_for_function("() => document.querySelector('#pacm-stare').innerText.includes('Ciornă salvată')", timeout=20000)
    _pachet(patron, firma_e2e, 2099, 2)   # pagina reîncărcată: caseta arată ce s-a salvat pe server
    _deschide_povestea(patron)
    text = pg.input_value("#pacm-text")
    patron.captura("caseta")
    assert "**" not in text and "__" not in text and not text.startswith("#") and "*bine*" not in text, text


def _luna_32(patron, firma_e2e):
    """Luna cu venituri 1.000 lei (4111=704) și nota impozitului 160 lei (691=441), validate; o singură dată pe firmă."""
    s = firma_e2e["schema"]
    pregateste_firma(patron, firma_e2e)
    luna = _dt.date(2026, 7, 15)
    for desc, d, c, suma in (("Venit E2E 32", "4111", "704", "1000.00"), ("Impozit E2E 32", "691", "441", "160.00")):
        if not sql('SELECT 1 FROM "%s".inregistrari WHERE descriere = %%s' % s, (desc,)):
            r = _ok(_api(patron, "POST", "/tenants/%d/jurnal" % firma_e2e["tenant_id"],
                         {"descriere": desc, "data": luna.isoformat(), "document_ref": "PV E2E 32",
                          "linii": [{"debit": d, "credit": c, "suma": suma}]}), "nota " + desc)
            _ok(_api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (firma_e2e["tenant_id"], r["id"])), "validare " + desc)
    return luna


FAPT_32 = ("Veniturile lunii au fost de 1.000,00 lei, cheltuielile de 0,00 lei, iar rezultatul înainte de impozit este de "
           "1.000,00 lei (profit).")


def _genereaza_povestea(patron):
    pg = patron.pg
    pg.click("#pacm-gen")
    pg.wait_for_function("() => document.querySelector('#pacm-gen').textContent.includes('Generează cu AI') "
                         "&& document.querySelector('#pacm-text').value.trim() !== ''", timeout=30000)
    return pg.input_value("#pacm-text"), pg.inner_text("#pacm-abateri")


def test_def_32_rezultat_inainte_de_impozit_pe_pachet_si_in_email(patron, firma_e2e):
    """32. Povestea lunii: rezultatul înainte de impozit numit „profit”, cu laudă nesusținută.
    Pașii contabilului: într-o lună cu venituri 1.000 lei (4111=704) și nota impozitului 160 lei (691=441), pachetul arată
    „Rezultat înainte de impozit 1.000,00 lei (profit)”, cheltuielile 0,00 (impozitul nu e cheltuială a rezultatului dinainte de
    impozit), iar emailul folosește aceeași etichetă.
    [retestul Costin 09.10, cuvânt cu cuvânt] „povestea lunii păstrează laude nesusținute de cifre.” Pașii: modelul (simulat în
    plasă) scrie de ambele dăți „o lună excelentă, cu o creștere remarcabilă” -> „Generează cu AI”: în editor ajunge numai
    propoziția cu cifrele; ecranul spune ce a scos; promptul nu mai cere „ton cald” și interzice calificarea.
    [testul vechi trecea pe defect: nu genera povestea deloc — verifica numai eticheta rezultatului]"""
    luna = _luna_32(patron, firma_e2e)
    _pachet(patron, firma_e2e, luna.year, luna.month)
    pg = patron.pg
    rez = pg.eval_on_selector_all(".pac-rezumat .pac-rez-rand", "els => els.map(e => e.innerText.replace(/\\s+/g, ' ').trim())")
    patron.captura("pachet")
    assert "Venituri 1.000,00 lei" in rez and "Cheltuieli 0,00 lei" in rez, rez
    assert "Rezultat înainte de impozit 1.000,00 lei (profit)" in rez, rez
    _deschide_povestea(patron)
    lauda = "Iulie a fost o lună excelentă pentru firmă, cu o creștere remarcabilă a activității."
    ai_pregateste(lauda + " " + FAPT_32, "Felicitări pentru rezultat! " + FAPT_32)
    text, mesaj = _genereaza_povestea(patron)
    patron.captura("poveste_generata")
    assert text == FAPT_32, text
    assert "Din textul generat s-a scos o propoziție" in mesaj and "Felicitări pentru rezultat!" in mesaj, mesaj
    pr = ai_prompturi()
    assert len(pr) == 2 and "laudă nesusținută de cifre: excelentă" in pr[1]["prompt"], [x["prompt"][-400:] for x in pr]
    assert "Ton cald" not in pr[0]["prompt"] and "NU lauda" in pr[0]["prompt"], pr[0]["prompt"][:600]
    pg.click("#pacm-vezi")
    pg.wait_for_function("() => document.querySelector('#pacm-preview').innerText.includes('Cheltuieli')", timeout=20000)
    mail = re.sub(r"\s+", " ", pg.inner_text("#pacm-preview"))
    patron.captura("email")
    assert "Rezultat înainte de impozit 1.000,00 lei (profit)" in mail, mail[:600]


def test_def_12_parafraza_de_incasare_e_prinsa_si_numita(patron, firma_e2e):
    """12. Povestea lunii: AI confundă venituri, încasări și câștig.
    [partea rămasă, registrul: „Parafraza «tot ce a intrat ca venit s-a transformat în rezultat» … trece nevăzută — framing de
    încasare, neprins de abateri. În plus nu există test e2e determinist”] Pașii: modelul (simulat în plasă) scrie de ambele dăți
    „Tot ce a intrat ca venit s-a transformat în rezultat.” -> „Generează cu AI”: a doua cerere către model numește abaterea, iar
    editorul o arată („termen: a intrat”) înainte de aprobare."""
    luna = _luna_32(patron, firma_e2e)
    _pachet(patron, firma_e2e, luna.year, luna.month)
    _deschide_povestea(patron)
    parafraza = "Tot ce a intrat ca venit s-a transformat în rezultat."
    ai_pregateste(FAPT_32 + " " + parafraza, FAPT_32 + " " + parafraza)
    text, mesaj = _genereaza_povestea(patron)
    patron.captura("poveste_generata")
    assert "textul generat se abate de la pachet" in mesaj and "termen: a intrat" in mesaj, mesaj
    pr = ai_prompturi()
    assert len(pr) == 2 and "termen: a intrat" in pr[1]["prompt"], [x["prompt"][-300:] for x in pr]


def _prezentarea(e):
    e.acasa()
    e.pg.click("#nav-ghid")
    e.pg.wait_for_selector(".fereastra .ans-grupe .ans-grupa", timeout=30000)
    e.pg.wait_for_timeout(400)


def test_def_198_salutul_de_la_intrare_are_diacritice(patron):
    """198. Desktopul contabilului-șef: mesajul „Buna, Dobrescu!” e fără diacritice.
    Pașii: contabilul-șef are notificări necitite -> intră în aplicație: caseta de bun-venit spune „Bună, <prenume>!” (prenumele, ca
    salutul desktopului), iar rândul notificărilor are diacritice („declarații depuse”, „notificări”)."""
    pg = patron.pg
    uid, prenume = sql("SELECT id, coalesce(prenume, '') FROM public.users WHERE email = 'patron@prisma-cont.test'")[0]
    nid = sql("INSERT INTO public.notificari (user_id, tip, text, citit, creat_la) VALUES (%s, 'depusa', 'Probă 198', false, now()) "
              "RETURNING id", (uid,))[0][0]
    try:
        patron.acasa()   # context nou de browser: caseta apare o dată pe sesiune
        pg.wait_for_selector(".sumar-toast", timeout=15000)
        cap = pg.inner_text(".sumar-toast-cap")
        corp = pg.inner_text(".sumar-toast-corp")
        patron.captura("salut")
    finally:
        sql("DELETE FROM public.notificari WHERE id = %s", (nid,))
    assert cap.startswith("Bună, ") and cap.endswith("!"), cap
    if prenume:
        assert cap == "Bună, %s!" % prenume, (cap, prenume)
    assert "declaratie" not in corp and "notificari" not in corp, corp


def test_def_191_versiunea_noua_se_poate_apasa_cu_o_fereastra_deschisa(patron):
    """191. Bara de stare: butonul „Versiune nouă” nu se poate apăsa cât e deschisă o fereastră — stratul ferestrei îl acoperă.
    Pașii: pagina principală -> se deschide o fereastră (Firme) -> se publică o versiune nouă (amprenta publicării se schimbă) -> la
    revenirea în filă apare „Versiune nouă · reîncarcă”: butonul e deasupra stratului ferestrei (el primește apăsarea în punctul lui)."""
    import json as _json
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='firme'])")
    pg.wait_for_selector(".fereastra-overlay", timeout=20000)
    pg.route("**/static/.publicat.json*", lambda r: r.fulfill(status=200, content_type="application/json",
                                                              body=_json.dumps({"la": "proba-191-versiune-noua"})))
    pg.evaluate("() => document.dispatchEvent(new Event('visibilitychange'))")
    pg.wait_for_selector(".versiune-noua", timeout=20000)
    sus = pg.evaluate("""() => { const b = document.querySelector('.versiune-noua'); const r = b.getBoundingClientRect();
      const e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return {ok: !!e && b.contains(e), e: e && e.className}; }""")
    patron.captura("versiune")
    pg.unroute("**/static/.publicat.json*")
    assert sus["ok"], sus


def _coada(e):
    e.acasa()
    e.pg.click("button.cab-card:has([data-cheie='validat'])")
    e.pg.wait_for_selector(".fereastra:last-of-type .cf-grup-titlu", timeout=60000)
    e.pg.wait_for_timeout(800)


def test_def_193_cardurile_cozii_au_latimea_ferestrei(patron):
    """193. Coadă: cardurile „De depus” (D300) sunt înghesuite pe o coloană îngustă.
    Pașii: ecran de 1700 × 1000 -> cardul „De depus” / „De validat” -> în fiecare card de declarație textul (declarația, firma,
    termenul, „Vezi declarația…”) are cel puțin 300 px — nu e strivit de butoane într-o coloană îngustă —, iar butoanele stau în
    card (niciunul nu iese peste marginea lui); la fel pe telefon (390 px)."""
    pg = patron.pg
    masoara = """() => { const f = [...document.querySelectorAll('.fereastra')].pop();
      return [...f.querySelectorAll('.val-card')].map(v => { const r = v.getBoundingClientRect(); const t = v.firstElementChild.getBoundingClientRect();
        const iese = [...v.querySelectorAll('button')].filter(b => { const x = b.getBoundingClientRect(); return x.right > r.right + 1 || x.left < r.left - 1; }).length;
        return {card: Math.round(r.width), text: Math.round(t.width), iese, t: v.innerText.slice(0, 40)}; }); }"""
    for lat, inalt in ((1700, 1000), (390, 844)):
        pg.set_viewport_size({"width": lat, "height": inalt})
        _coada(patron)
        m = pg.evaluate(masoara)
        patron.captura("coada_%d" % lat)
        assert m, "anti-vacuu: nicio declarație în coadă"
        rele = [x for x in m if x["text"] < min(300, x["card"] - 30) or x["iese"]]
        assert not rele, (lat, rele)
        # perioada declarației în forma DS v2.85 cap.4 („T4/2026”, „08/2026”), nu „trim. IV 2026” (văzut pe captura testului)
        decl = [x for x in m if re.match(r"\s*D\d{3}\b", x["t"])]   # cardurile de DECLARAȚIE (notele din coadă n-au perioadă)
        assert decl, "anti-vacuu: niciun card de declarație în coadă: %s" % m
        assert not [x for x in decl if "trim." in x["t"]] and all(re.search(r"T[1-4]/20\d\d|\d\d/20\d\d|\b20\d\d\b", x["t"]) for x in decl), decl
    pg.set_viewport_size({"width": 1700, "height": 1000})


def test_def_217_coada_nu_se_contrazice_despre_validarea_in_doi(browser, request, patron, firma_e2e):
    """217. Coada: textul „validarea în doi nu e pornită” contrazice notele de validat de pe același ecran.
    Pașii: asistentul scrie o notă pe firma alocată (intră la validare) -> contabilul-șef (validarea în doi a declarațiilor nepornită)
    deschide coada: „Note de validat (N)” sus, iar textul spune că notele asistenților se validează și că validarea în doi privește
    declarațiile — nu „validarea în doi nu e pornită” fără ce anume."""
    pregateste_firma(patron, firma_e2e)
    with cont_asistent(firme=(firma_e2e["tenant_id"],)) as a, ecran_cont(browser, request, a["email"]) as e:   # „Poate pregăti”, fără validare
        e.acasa()
        nota = _ok(_api(e, "POST", "/tenants/%d/jurnal" % firma_e2e["tenant_id"],
                        {"data": AZI.isoformat(), "descriere": "Nota D217", "document_ref": "D217",
                         "linii": [{"debit": "5311", "credit": "4111", "suma": 17}]}), "nota asistentului")
    try:
        _coada(patron)
        f = patron.fereastra()
        patron.captura("coada")
    finally:
        sql('DELETE FROM "%s".inregistrari WHERE id = %%s' % firma_e2e["schema"], (nota["id"],))
    assert "note de validat (" in f.lower(), f[:800]   # titlul grupului e cu majuscule din CSS
    assert "validarea în doi nu e pornită" not in f and "Notele de mai sus le-au pregătit asistenții" in f, f[:800]


def test_def_200_prezentarea_fara_goluri_intre_grupe(patron):
    """200. Prezentarea aplicației: coloane inegale, goluri mari.
    Pașii: ecran de 1700 × 1000 -> „?” din bara de sus -> „Ce cuprinde aplicația”: sub fiecare grupă urmează, la cel mult 30 px,
    grupa de dedesubt (sau capătul secțiunii) — fără goluri mari sub grupele scurte, iar coloanele se termină la cel mult 60 px
    una de alta."""
    pg = patron.pg
    pg.set_viewport_size({"width": 1700, "height": 1000})
    _prezentarea(patron)
    m = pg.evaluate("""() => { const z = document.querySelector('.fereastra .ans-grupe'); const zr = z.getBoundingClientRect();
      const bx = [...z.querySelectorAll('.ans-grupa')].flatMap(g => [...g.getClientRects()]).map(r => ({l: r.left, r: r.right, t: r.top, b: r.bottom}));
      const goluri = bx.map(g => { const jos = bx.filter(o => o !== g && o.t >= g.b - 1 && o.l < g.r - 1 && o.r > g.l + 1).map(o => o.t);
        return Math.round((jos.length ? Math.min(...jos) : zr.bottom) - g.b); });
      const col = {}; bx.forEach(g => { const k = Math.round(g.l); col[k] = Math.max(col[k] || 0, g.b); });
      const fund = Object.values(col);
      return {gol_max: Math.max(...goluri), coloane: fund.length, diferenta: Math.round(Math.max(...fund) - Math.min(...fund))}; }""")
    pg.eval_on_selector(".fereastra .ans-grupe", "e => e.scrollIntoView({block: 'start'})")
    patron.captura("prezentarea")
    assert m["gol_max"] <= 30 and m["diferenta"] <= 60, m


def test_def_201_prezentarea_vorbeste_limba_contabilului(patron):
    """201. Prezentarea aplicației: limbaj de programator (pull->push, F163v2, „Dispatch”, v9) și titluri fără diacritice („Facturare
    si e-Factura”).
    Pașii: „?” din bara de sus -> „Ce cuprinde aplicația”: titlurile grupelor au diacritice („Facturare și e-Factura”, „Stocuri, bancă
    și casă”, „Cabinet și portal client”), iar niciun nume nu are „->”, coduri F…, versiuni „v9”, jargon englezesc."""
    from core import ansamblu
    pg = patron.pg
    _prezentarea(patron)
    titluri = pg.eval_on_selector_all(".fereastra .ans-grupa-titlu", "els => els.map(e => e.childNodes[0].textContent.trim())")
    nume = pg.eval_on_selector_all(".fereastra .ans-grupa-lista li", "els => els.map(e => e.childNodes[0].textContent.trim())")
    patron.captura("catalog")
    assert "Facturare și e-Factura" in titluri and "Stocuri, bancă și casă" in titluri and "Cabinet și portal client" in titluri, titluri
    assert len(nume) > 100, len(nume)
    rele = [(x, ansamblu.limbaj_tehnic(x)) for x in titluri + nume if ansamblu.limbaj_tehnic(x)]
    assert not rele, rele


def test_def_202_prezentarea_trimite_la_cardul_care_exista(patron, asistent):
    """202. Prezentarea aplicației trimite la „cardul Suport”; cardul se numește „Raportează”.
    Pașii: contabilul-șef și asistentul -> „?” -> prezentarea trimite la cardul „Raportează”, iar pe pagina principală a fiecăruia
    există un card cu exact acest nume."""
    for e in (patron, asistent):
        _prezentarea(e)
        text = e.pg.inner_text(".fereastra .ans-continut")
        assert "cardul „Raportează”" in text and "cardul Suport" not in text, text[:400]
        e.acasa()
        carduri = e.pg.eval_on_selector_all(".cab-card-titlu, .asi-nod-titlu, .asi-nod", "els => els.map(x => x.innerText.trim())")
        e.captura("desktop")
        assert any(c.split("\n")[0] == "Raportează" for c in carduri), carduri


#: [deficiența 203] ordinea cardurilor cabinetului după lucrul zilnic: întâi ce cere acțiune azi (de validat, restanțe, scadențe), apoi
#: lucrul pe firme și ziua, apoi lunarul, apoi echipa și contul, la urmă sesizările
ORDINE_CABINET = ["validat", "control", "termene", "firme", "brief", "activitate", "pachete", "supervizor", "capacitate",
                  "consolidare", "asistenti", "setari", "raport"]


def test_def_203_cardurile_cabinetului_ordine_raporteaza_si_cifre(patron):
    """203. Pagina principală: la cabinet lipsește cardul „Raportează”; cardurile trebuie ordonate după lucrul zilnic, iar cifrele lor =
    ecranele din spate.
    Pașii: contabilul-șef -> pagina principală: există cardul „Raportează”; cardurile sunt în ordinea lucrului zilnic (de validat,
    control fiscal, termene, firme …, la urmă Raportează) -> cifra cardului Firme = firmele active din ecranul Firme; contoarele
    cardului Control fiscal = contoarele ecranului Control fiscal; „N note de validat” = „Note de validat (N)” din fereastra cozii."""
    import re as _r
    pg = patron.pg
    patron.acasa()
    pg.wait_for_function("() => !document.querySelector('.cab-grila').innerText.includes('se încarcă')", timeout=60000)
    pg.wait_for_timeout(1500)
    card = pg.evaluate("""() => [...document.querySelectorAll('.cab-grila button.cab-card')].map(b => ({
        cheie: (b.querySelector('[data-cheie]') || {}).dataset ? b.querySelector('[data-cheie]').dataset.cheie : null,
        titlu: (b.querySelector('.cab-card-titlu') || {}).innerText, sinteza: (b.querySelector('.cab-card-sinteza') || {}).innerText}))""")
    patron.captura("desktop")
    chei = [c["cheie"] for c in card]
    assert [k for k in chei if k in ORDINE_CABINET] == [k for k in ORDINE_CABINET if k in chei], chei
    raport = [c for c in card if c["cheie"] == "raport"]
    assert raport and raport[0]["titlu"].strip() == "Raportează", raport
    sint = {c["cheie"]: c["sinteza"] for c in card}
    firme_card = int(_r.search(r"(\d+) firm", sint["firme"]).group(1))
    pg.click("button.cab-card:has([data-cheie='firme'])")
    pg.wait_for_timeout(600)
    if pg.query_selector("#opt-existente"):
        pg.click("#opt-existente")
    pg.wait_for_selector("#firme-lista .firme-rand-linie", timeout=30000)
    pg.wait_for_timeout(800)
    firme_ecran = pg.locator("#firme-lista .firme-rand-linie").count()
    assert firme_card == firme_ecran, (sint["firme"], firme_ecran)
    patron.acasa()
    pg.wait_for_function("() => !document.querySelector('[data-cheie=control]').innerText.includes('se încarcă')", timeout=120000)
    ctrl_card = pg.inner_text("[data-cheie=control]")
    pg.click("button.cab-card:has([data-cheie='control'])")
    pg.wait_for_selector(".cf-sumar .cf-pastila", timeout=120000)
    pastile = pg.eval_on_selector_all(".fereastra:last-of-type .cf-sumar .cf-pastila", "els => els.map(e => e.innerText.trim())")
    # fiecare contor nenul de pe ecran are pe card aceeași cifră, pe rândul cu aceeași etichetă (ultimele două cuvinte)
    randuri_card = [x.strip() for x in ctrl_card.split("\n") if x.strip()]
    for p in pastile:
        n, et = _r.match(r"(\d+)\s+(.*)", p).groups()
        if int(n) == 0:
            continue
        coada = " ".join(et.split()[-2:])
        pe_card = [x for x in randuri_card if x.endswith(coada)]
        assert pe_card and pe_card[0].split()[0] == n, (p, randuri_card)
    patron.acasa()
    pg.wait_for_function("() => /\\d/.test(document.querySelector('[data-cheie=validat]').innerText)", timeout=60000)
    val_card = pg.inner_text("[data-cheie=validat]")
    pg.click("button.cab-card:has([data-cheie='validat'])")
    pg.wait_for_selector(".fereastra:last-of-type .cf-grup-titlu", timeout=60000)
    pg.wait_for_timeout(800)
    titluri = pg.eval_on_selector_all(".fereastra:last-of-type .cf-grup-titlu", "els => els.map(e => e.textContent.trim())")
    patron.captura("coada")
    for eticheta_card, grup in ((r"(\d+) note? de validat", "Note de validat"), (r"(\d+) declarații? de validat", "De validat"),
                                (r"(\d+) declarații? de depus", "De depus")):
        m = _r.search(eticheta_card, val_card)
        if m:
            g = [t for t in titluri if t.startswith(grup + " (")]
            assert g and g[0] == "%s (%s)" % (grup, m.group(1)), (val_card, titluri)


def test_def_207_ecranele_generale_pornesc_pe_firma_in_lucru(patron, asistent, firma_e2e):
    """207. Pachete lunare: câmpul „Firmă” nu vine cu firma în lucru.
    Pașii: deschide firma (bara de jos: „În lucru: <firma>”) -> ecranul principal -> Pachete lunare: câmpul „Firmă” e firma în lucru,
    iar „Continuă” e activ -> asistentul (al cărui ecran principal are și Declarații, ecran general de același fel): deschide firma
    -> Declarații: câmpul „Firmă” e firma în lucru."""
    from core import asistenti_api, db
    with db.get_conn() as c:
        r = asistenti_api.atribuie_firma(c, firma_e2e["cabinet_id"], sql("SELECT id FROM public.users WHERE email = "
                                                                          "'asistent@prisma-cont.test'")[0][0], firma_e2e["tenant_id"])
        c.commit()
    assert r.get("ok"), r
    pg = patron.pg
    pregateste_firma(patron, firma_e2e)
    patron.firma(firma_e2e["nume"])
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='pachete'])")
    pg.wait_for_selector("#pac-firma", timeout=20000)
    alese = pg.evaluate("() => [document.querySelector('#pac-firma').value, document.querySelector('#pac-continua').disabled]")
    patron.captura("pachete")
    assert alese == [str(firma_e2e["tenant_id"]), False], alese
    asistent.firma(firma_e2e["nume"])
    asistent.acasa()
    asistent.pg.click(".asi-nod[data-nod='declaratii']")
    asistent.pg.wait_for_selector("#dec-firma", timeout=20000)
    dec = asistent.pg.input_value("#dec-firma")
    asistent.captura("declaratii")
    assert dec == str(firma_e2e["tenant_id"]), dec


def test_def_208_fereastra_povestii_e_de_lucru_nu_de_mesaj(patron, firma_e2e):
    """208. Povestea lunii: fereastra și caseta de text prea mici.
    Pașii: ecran de 1700 × 1000 -> Pachete lunare -> firma -> luna -> „Scrie povestea”: fereastra ține cât un document (cel puțin
    900 px lățime și 70% din înălțimea ecranului), iar caseta de text ocupă cea mai mare parte din ea (cel puțin 55% din înălțimea
    ecranului) — și când povestea e goală; pe telefon (390 px) fereastra încape în ecran."""
    pg = patron.pg
    pg.set_viewport_size({"width": 1700, "height": 1000})
    luna = _luna_32(patron, firma_e2e)
    _pachet(patron, firma_e2e, luna.year, luna.month)
    _deschide_povestea(patron)
    m = pg.evaluate("""() => { const f = document.querySelector('.pacm').getBoundingClientRect(),
        t = document.querySelector('#pacm-text').getBoundingClientRect();
        return {fer_l: Math.round(f.width), fer_h: Math.round(f.height), text_h: Math.round(t.height), vh: innerHeight}; }""")
    patron.captura("desktop")
    assert m["fer_l"] >= 900 and m["fer_h"] >= 0.7 * m["vh"] and m["text_h"] >= 0.55 * m["vh"], m
    pg.set_viewport_size({"width": 390, "height": 844})
    pg.wait_for_timeout(200)
    t = pg.evaluate("() => { const f = document.querySelector('.pacm').getBoundingClientRect(); return [f.left, f.right, f.top, f.bottom, innerWidth, innerHeight]; }")
    patron.captura("telefon")
    pg.set_viewport_size({"width": 1700, "height": 1000})
    assert t[0] >= 0 and t[1] <= t[4] and t[2] >= 0 and t[3] <= t[5], t


def test_def_209_povestea_nu_vorbeste_despre_declaratii(patron, firma_e2e):
    """209. Povestea lunii: spune doar ce reiese din cifre și nimic despre declarații.
    Pașii: luna are o declarație depusă (D300, marcată depusă) -> modelul (simulat în plasă) scrie de ambele dăți „Firma a depus
    decontul de TVA (D300) la termen.” -> „Generează cu AI”: în editor ajunge numai propoziția cu cifrele; promptul nu primește
    declarațiile depuse; tabelul pachetului le arată în continuare."""
    luna = _luna_32(patron, firma_e2e)
    sql("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, sursa) VALUES (%s, %s, %s, 'd300', 'iconta') "
        "ON CONFLICT DO NOTHING", (firma_e2e["tenant_id"], luna.year, luna.month))
    try:
        _pachet(patron, firma_e2e, luna.year, luna.month)
        rez = patron.pg.eval_on_selector_all(".pac-rezumat .pac-rez-rand", "els => els.map(e => e.innerText.replace(/\\s+/g, ' ').trim())")
        _deschide_povestea(patron)
        despre = "Firma a depus decontul de TVA (D300) la termen."
        ai_pregateste(FAPT_32 + " " + despre, despre + " " + FAPT_32)
        text, mesaj = _genereaza_povestea(patron)
        patron.captura("poveste_generata")
    finally:
        sql("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s AND tip = 'd300'", (firma_e2e["tenant_id"],))
    assert any("D300" in r for r in rez), rez
    assert text == FAPT_32, text
    assert despre in mesaj, mesaj
    pr = ai_prompturi()
    assert pr and "D300" not in pr[0]["prompt"], pr[0]["prompt"][:900]   # a doua cerere citează propoziția de corectat, nu date


def test_def_33_povestea_nu_afirma_ce_era_de_depus(patron, firma_e2e):
    """33. Povestea lunii: clientului i se comunicau restanțele (decizia A: rămân alertă la cabinet).
    [retestul Costin 09.10, cuvânt cu cuvânt] „povestea scrie fals «în septembrie nu a fost nicio declarație de depus».” Cauza:
    promptul spunea „Declarații depuse la ANAF: nicio declarație”, iar modelul o citea „nimic de depus”. Pașii: luna fără nicio
    declarație depusă -> modelul (simulat) scrie de ambele dăți „în iulie nu a fost nicio declarație de depus” -> „Generează cu AI”:
    propoziția nu ajunge în editor, iar promptul nu mai poartă rândul „nicio declarație”."""
    luna = _luna_32(patron, firma_e2e)
    _pachet(patron, firma_e2e, luna.year, luna.month)
    _deschide_povestea(patron)
    fals = "În iulie nu a fost nicio declarație de depus."
    ai_pregateste(FAPT_32 + "\n\n" + fals, fals + " " + FAPT_32)
    text, mesaj = _genereaza_povestea(patron)
    patron.captura("poveste_generata")
    assert text == FAPT_32 and "declarați" not in text.lower(), text
    assert fals in mesaj, mesaj
    pr = ai_prompturi()
    assert pr and all("nicio declaratie" not in x["prompt"].lower() for x in pr), [x["prompt"][:700] for x in pr]
    assert "Nu scrie nimic despre declaratii" in pr[0]["prompt"], pr[0]["prompt"][:900]


# ── 05.10 — factura F1 ──────────────────────────────────────────────────────────────────────────────────────────────────────
def _completeaza_factura(pg, cantitate="2"):
    for sel, v in CLIENT.items():
        pg.fill(sel, v)
    pg.fill("#em-l0-descriere", PRODUS)
    pg.wait_for_function("() => document.querySelector('#em-l0-pret_unitar').value !== ''", timeout=20000)
    pg.fill("#em-l0-cantitate", cantitate)


def _campuri_factura(pg):
    return pg.evaluate("""() => Object.fromEntries(['em-cui', 'em-nume', 'em-adresa', 'em-l0-descriere', 'em-l0-cantitate',
        'em-l0-pret_unitar', 'em-l0-um'].map(i => [i, (document.getElementById(i) || {}).value]))""")


def test_def_19_factura_nu_se_pierde_la_date_firma_si_la_expirarea_sesiunii(browser, request, patron, firma_e2e):
    """19. Factură: muncă pierdută de două ori (expirarea sesiunii; după Date firmă).
    Pașii contabilului: asistentul completează o factură (client + linie); firma n-are forma juridică, deci apasă butonul spre Date
    firmă, completează forma și capitalul, salvează și revine („Înapoi”): factura e cum a lăsat-o. Apoi sesiunea expiră; la următoarea
    acțiune (schimbă denumirea liniei) i se cere parola PESTE factură; după parolă continuă, iar câmpurile sunt intacte."""
    pregateste_firma(patron, firma_e2e)
    scoate_forma_si_capitalul(patron, firma_e2e)
    with cont_asistent(firme=(firma_e2e["tenant_id"],)) as a, ecran_cont(browser, request, a["email"]) as e:
        pg = e.pg
        _deschide_emiterea(e, firma_e2e["nume"])
        _completeaza_factura(pg)
        inainte = _campuri_factura(pg)
        pg.click("#em-date-firma-sus")
        pg.wait_for_selector("#df-forma_juridica", timeout=20000)
        pg.select_option("#df-forma_juridica", "SRL")
        pg.fill("#df-capital_subscris", "200")
        pg.click("#df-salveaza")
        pg.wait_for_function("() => ((document.querySelector('#df-msg') || {}).textContent || '').includes('salvate')", timeout=20000)
        pg.click(".nav-sageata.nav-inapoi")
        pg.wait_for_selector("#em-cui", timeout=20000)
        pg.wait_for_function("() => !document.querySelector('#em-emite').disabled", timeout=20000)
        dupa_date_firma = _campuri_factura(pg)
        e.captura("dupa_date_firma")
        assert dupa_date_firma == inainte, (inainte, dupa_date_firma)
        # sesiunea expiră (ca după 24 de ore): tokenul emis înainte de `sesiuni_valide_de` e refuzat de server
        time.sleep(1.1)
        sql("UPDATE public.users SET sesiuni_valide_de = date_trunc('second', now()) WHERE id = %s", (a["id"],))
        time.sleep(1.1)
        pg.fill("#em-l0-cantitate", "3")
        pg.fill("#em-l0-descriere", PRODUS + " ")
        pg.wait_for_selector("#reaut-parola", timeout=20000)
        e.captura("parola_peste_factura")
        assert pg.input_value("#em-nume") == CLIENT["#em-nume"], "factura a dispărut sub fereastra de parolă"
        pg.fill("#reaut-parola", a["parola"])
        pg.click("#reaut-continua")
        pg.wait_for_selector("#reaut-parola", state="detached", timeout=20000)
        pg.wait_for_function("() => document.querySelector('#em-l0-cota').value === '21'", timeout=20000)
        dupa = _campuri_factura(pg)
        e.captura("dupa_parola")
        assert dict(inainte, **{"em-l0-cantitate": "3", "em-l0-descriere": PRODUS + " "}) == dupa, (inainte, dupa)


def test_def_20_forma_juridica_si_capitalul_se_cer_la_deschidere(browser, request, patron, firma_e2e):
    """20. Factură: forma juridică și capitalul se verificau abia la final; forma juridică nu se precompleta din ANAF.
    Pașii contabilului: la o firmă fără formă juridică, deschide „Emite factură”: ÎNAINTE de a scrie ceva, nota spune ce lipsește din
    Date firmă și „Emite factură” e inactiv cu motivul; butonul spre Date firmă deschide ecranul cu forma juridică deja propusă
    (aici din denumirea „… SRL”, ANAF neavând firma sintetică), de verificat și salvat."""
    pregateste_firma(patron, firma_e2e)
    scoate_forma_si_capitalul(patron, firma_e2e)
    with cont_asistent(firme=(firma_e2e["tenant_id"],)) as a, ecran_cont(browser, request, a["email"]) as e:
        pg = e.pg
        _deschide_emiterea(e, firma_e2e["nume"])
        pg.wait_for_selector("#em-pregatire .ca-mesaj", timeout=20000)
        nota = pg.inner_text("#em-pregatire .ca-mesaj")
        assert "forma juridică" in nota, nota
        assert pg.is_disabled("#em-emite") and "forma juridică" in (pg.get_attribute("#em-emite", "title") or "")
        e.captura("la_deschidere")
        pg.click("#em-date-firma-sus")
        pg.wait_for_selector("#df-forma_juridica", timeout=20000)
        assert pg.input_value("#df-forma_juridica") == "SRL"
        propusa = pg.inner_text("#df-forma-propusa")
        e.captura("date_firma")
        assert "Propusă din" in propusa and "SRL" in propusa, propusa


def test_def_21_cota_tva_de_pe_linie_se_corecteaza_si_se_consemneaza(browser, request, patron, firma_e2e):
    """21. Factură: cota TVA de pe linie nu se putea corecta.
    Pașii contabilului: pe linia facturii cota propusă e 21%; contabilul o schimbă în 11% din lista cotelor permise și emite: linia
    e emisă cu 11%, iar schimbarea e consemnată (propus 21 -> ales 11, de cine)."""
    pregateste_firma(patron, firma_e2e)
    with cont_asistent(firme=(firma_e2e["tenant_id"],)) as a, ecran_cont(browser, request, a["email"]) as e:
        pg = e.pg
        _deschide_emiterea(e, firma_e2e["nume"])
        _completeaza_factura(pg)
        pg.wait_for_function("() => document.querySelector('#em-l0-cota').value === '21'", timeout=20000)
        optiuni = pg.eval_on_selector_all("#em-l0-cota option", "els => els.map(e => e.value).filter(Boolean)")
        assert "11" in optiuni and "21" in optiuni, optiuni
        pg.select_option("#em-l0-cota", "11")
        e.captura("cota_aleasa")
        with pg.expect_response(lambda r: r.url.endswith("/facturi/emite"), timeout=60000) as rr:
            pg.click("#em-emite")
        fid = rr.value.json()["factura_id"]
        pg.wait_for_selector("#em-rezultat.em-bun", timeout=20000)
        e.captura("emisa")
    s = firma_e2e["schema"]
    assert sql('SELECT cota_tva::int FROM "%s".factura_linii WHERE factura_id = %%s' % s, (fid,)) == [(11,)]
    assert sql('SELECT cota_propusa::int, cota_aleasa::int, user_id FROM "%s".factura_cota_jurnal WHERE factura_id = %%s' % s,
               (fid,)) == [(21, 11, a["id"])]


def test_def_22_formularul_arata_data_scadenta_si_seria(patron, firma_e2e):
    """22. Factură: formularul nu arăta data emiterii, scadența și seria.
    Pașii contabilului: deschide „Emite factură”: vede data emiterii (azi), scadența propusă (azi + termenul legal) și seria cu
    următorul număr; poate schimba data și scadența."""
    pregateste_firma(patron, firma_e2e)
    _deschide_emiterea(patron, firma_e2e["nume"])
    pg = patron.pg
    assert pg.input_value("#em-data") == AZI.isoformat()
    scad = pg.input_value("#em-scadenta")
    serie = pg.inner_text("#em-serie-nr")
    patron.captura()
    assert scad and _dt.date.fromisoformat(scad) > AZI, scad
    assert serie.startswith(SERIE + " · următorul număr:"), serie
    pg.fill("#em-data", "2026-10-01")
    pg.dispatch_event("#em-data", "change")
    pg.wait_for_function("() => document.querySelector('#em-scadenta').value.startsWith('2026-10-31')", timeout=10000)


def test_def_23_pdf_factura_cod_tva_serie_data_scadenta_titlu(browser, request, patron, firma_e2e):
    """23. PDF factură: CUI fără RO, fără serie, data ca „Emisă”, fără scadență, fișier „(anonymous)” (CF art. 319 alin. 20).
    Pașii contabilului: deschide factura emisă -> „PDF factură”: pe PDF codul firmei plătitoare e „Cod TVA: RO…”, numărul e
    „Seria E2EA nr. …”, „Data emiterii: …”, „Data scadenței: …”, iar documentul are titlul „Factura E2EA nr. …”."""
    pregateste_firma(patron, firma_e2e)
    f = emite_api(patron, firma_e2e)
    cui = sql("SELECT cui FROM public.tenants WHERE id = %s", (firma_e2e["tenant_id"],))[0][0]
    _deschide_factura(patron, firma_e2e, f["factura_id"])
    pg = patron.pg
    with pg.expect_response(lambda r: r.url.endswith("/facturi/%s/pdf" % f["factura_id"]), timeout=30000) as rr:
        pg.click("#fd-pdf")
    text, titlu = _pdf_text(_pdf_ok(patron, rr))
    patron.captura()
    nr = str(f["numar"])[len(SERIE):]
    assert "Cod TVA: RO%s" % re.sub(r"\D", "", cui) in text, text[:600]
    assert "Seria %s nr. %s" % (SERIE, nr) in text, text[:600]
    assert "Data emiterii: %s" % AZI.strftime("%d.%m.%Y") in text and "Emisă -" not in text, text[:600]
    assert "Data scadenței: %s" % (AZI + _dt.timedelta(days=30)).strftime("%d.%m.%Y") in text, text[:600]
    assert titlu == "Factura %s nr. %s" % (SERIE, nr), titlu


def test_def_24_notele_automate_poarta_documentul_iar_validarea_fara_document_cere_confirmare(patron, firma_e2e):
    """24. Note automate: notele de stoc (607=371) și comision (627=5121) fără document justificativ; validarea trecea fără avertisment.
    Pașii contabilului: emite o factură cu marfă din stoc („pleacă marfa”), importă un extras cu un comision și îl contează: în
    Registrul jurnal nota 607=371 are documentul „Factură …”, nota 627=5121 „Extras bancar …”; o notă scrisă fără document e marcată
    pe rând, iar „Validează” pe ea cere confirmare („nu are document justificativ. Validezi totuși?”)."""
    pregateste_firma(patron, firma_e2e)
    tid, s = firma_e2e["tenant_id"], firma_e2e["schema"]
    art = articol_in_stoc(patron, firma_e2e)
    f = emite_api(patron, firma_e2e, linii=[{"descriere": ARTICOL, "cantitate": 1, "um": "buc", "pret_unitar": 20.0, "cota_tva": 21,
                                              "cota_propusa": 21, "articol_id": art}], pleaca_marfa=True)
    extras = "Data;Detalii;Suma\n%s;Comision administrare cont E2E 24;-7,50\n" % AZI.strftime("%d.%m.%Y")
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "banca", "#bk-fisier")
    pg.set_input_files("#bk-fisier", {"name": "extras_e2e_24_%d.csv" % time.time(), "mimeType": "text/csv",
                                      "buffer": extras.encode("utf-8")})
    pg.wait_for_selector("[data-cont]", timeout=30000)
    pg.locator(".pf-frand", has_text="Comision administrare cont E2E 24").locator("[data-cont]").click()
    pg.wait_for_function("() => document.querySelector('#bk-mesaj').innerText.includes('627=5121')", timeout=20000)
    nota_manuala = _ok(_api(patron, "POST", "/tenants/%d/jurnal" % tid, {"descriere": "Notă fără document E2E 24", "data":
                                                                         AZI.isoformat(), "linii": [{"debit": "6022", "credit": "5311",
                                                                                                     "suma": "11.00"}]}), "nota")["id"]
    pg.click(".nav-sageata.nav-inapoi")
    _card(patron, "jurnal", "#j-nota-noua")
    pg.wait_for_timeout(500)
    stoc = sql('SELECT i.id FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l ON l.inregistrare_id = i.id '
               "WHERE l.cont_debit = '607' AND l.cont_credit = '371' AND i.data = %%s ORDER BY i.id DESC LIMIT 1" % (s, s), (AZI,))
    comision = sql('SELECT i.id FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l ON l.inregistrare_id = i.id '
                   "WHERE l.cont_debit = '627' AND l.cont_credit = '5121' AND i.descriere LIKE %%s" % (s, s), ("%E2E 24%",))
    assert stoc and comision, (stoc, comision)

    def rand(nid):
        return pg.inner_text("[data-nota-id='%s']" % nid)
    r_stoc, r_com, r_man = rand(stoc[0][0]), rand(comision[0][0]), rand(nota_manuala)
    patron.captura("jurnal", intreaga=True)
    assert "Document justificativ: Factură %s din %s" % (f["numar"], AZI.strftime("%d.%m.%Y")) in r_stoc, r_stoc
    assert "Notă fără document justificativ" not in r_stoc and "Notă fără document justificativ" not in r_com, (r_stoc, r_com)
    assert "Document justificativ: Extras bancar" in r_com, r_com
    assert "Notă fără document justificativ" in r_man, r_man
    pg.click("[data-nota-id='%s'] [data-val]" % nota_manuala)
    pg.wait_for_selector("#caseta-atentie-activa #ca-ok", timeout=10000)
    caseta = pg.inner_text("#caseta-atentie-activa")
    patron.captura("confirmare")
    assert "nu are document justificativ. Validezi totuși?" in caseta and "Validează fără document" in caseta, caseta
    assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % s, (nota_manuala,)) == [("ciorna",)]


def test_def_25_factura_spune_nota_propusa_si_duce_la_nota(patron, firma_e2e):
    """25. Factură: detaliul scria „contabilizată” cât nota era ciornă; din factură nu se ajungea la notă.
    Pașii contabilului: deschide o factură abia emisă (nota de contare e ciornă): starea e „notă propusă, de validat”, nu
    „contabilizată”; butonul „nota #N” deschide Registrul jurnal pe luna notei, cu nota pe ecran."""
    pregateste_firma(patron, firma_e2e)
    f = emite_api(patron, firma_e2e)
    _deschide_factura(patron, firma_e2e, f["factura_id"])
    pg = patron.pg
    stari = pg.eval_on_selector_all(".fd-antet .fd-stare", "els => els.map(e => e.textContent.trim())")
    patron.captura("detaliu")
    assert "notă propusă, de validat" in stari and "contabilizată" not in stari, stari
    nota = pg.inner_text("#fd-vezi-nota")
    nid = int(re.search(r"#(\d+)", nota).group(1))
    assert sql('SELECT factura_id, status FROM "%s".inregistrari WHERE id = %%s' % firma_e2e["schema"], (nid,)) == \
        [(f["factura_id"], "ciorna")]
    pg.click("#fd-vezi-nota")
    pg.wait_for_selector(".fereastra:last-of-type [data-nota-id='%d']" % nid, timeout=20000)
    assert "Registru jurnal" in patron.fereastra()
    patron.captura("nota")


def test_def_26_banca_spune_exact_ce_a_importat_si_ce_nota_a_creat(patron, firma_e2e):
    """26. Bancă: mesaje false („2 linii potrivite”, „0 înregistrări”).
    Pașii contabilului: importă un extras cu 2 linii fără facturi de potrivit: mesajul spune „2 linii importate: 0 potrivite pe
    facturi, 2 fără potrivire”; contează comisionul pe nota propusă: „Notă 627=5121 creată (ciornă #N)”, iar nota există."""
    pregateste_firma(patron, firma_e2e)
    zi = AZI.strftime("%d.%m.%Y")
    extras = "Data;Detalii;Suma\n%s;Comision administrare cont E2E 26;-12,50\n%s;Incasare client necunoscut E2E 26;500,00\n" % (zi, zi)
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "banca", "#bk-fisier")
    pg.set_input_files("#bk-fisier", {"name": "extras_e2e_26_%d.csv" % time.time(), "mimeType": "text/csv",
                                      "buffer": extras.encode("utf-8")})
    pg.wait_for_function("() => document.querySelector('#bk-mesaj').innerText.includes('importate')", timeout=30000)
    mesaj = pg.inner_text("#bk-mesaj")
    patron.captura("import")
    assert "2 linii importate: 0 potrivite pe facturi, 2 fără potrivire" in mesaj, mesaj
    pg.locator(".pf-frand", has_text="Comision administrare cont E2E 26").locator("[data-cont]").click()
    pg.wait_for_function("() => document.querySelector('#bk-mesaj').innerText.includes('creat')", timeout=20000)
    mesaj = pg.inner_text("#bk-mesaj")
    pg.locator(".pf-frand", has_text="Comision administrare cont E2E 26").get_by_text("Contat ✓").wait_for(timeout=20000)
    patron.captura("contare")
    m = re.search(r"Notă 627=5121 creată \(ciornă #(\d+)\)", mesaj)
    assert m, mesaj
    assert sql('SELECT l.cont_debit, l.cont_credit, l.suma::text FROM "%s".inregistrari_linii l WHERE l.inregistrare_id = %%s'
               % firma_e2e["schema"], (int(m.group(1)),)) == [("627", "5121", "12.50")]


def test_def_27_linia_facturii_cu_um_pret_din_nomenclator_si_fara_articol_semnalat(patron, firma_e2e):
    """27. Factură/stoc: cantități cu zecimale în exces și fără unitate; prețul nu se prelua; „fără articol” nesemnalat.
    Pașii contabilului: pe o firmă cu stoc, deschide „Emite factură”: articolul din listă arată „stoc 10 buc” (nu „10.000”); scrie
    denumirea unui produs din nomenclator: prețul (150) și UM (ora) se completează; linia lui, fără articol de stoc, spune că marfa
    nu se descarcă din gestiune; alegând articolul de stoc, UM devine „buc” și semnul dispare."""
    pregateste_firma(patron, firma_e2e)
    articol_in_stoc(patron, firma_e2e)
    _deschide_emiterea(patron, firma_e2e["nume"])
    pg = patron.pg
    optiuni = pg.eval_on_selector_all("#em-l0-articol option", "els => els.map(e => e.textContent.trim())")
    marfa = [o for o in optiuni if o.startswith(ARTICOL)]
    assert marfa and re.search(r"· stoc \d+(?:,\d{1,2})? buc$", marfa[0]) and ".000" not in marfa[0], marfa
    pg.fill("#em-l0-descriere", PRODUS)
    pg.wait_for_function("() => document.querySelector('#em-l0-pret_unitar').value !== ''", timeout=20000)
    assert pg.input_value("#em-l0-pret_unitar") in ("150", "150.0", "150.00"), pg.input_value("#em-l0-pret_unitar")
    assert pg.input_value("#em-l0-um") == "ora"
    assert pg.is_visible("#em-l0-fara-articol") and "nu se descarcă din gestiune" in pg.inner_text("#em-l0-fara-articol")
    patron.captura("fara_articol")
    pg.select_option("#em-l0-articol", label=marfa[0])
    pg.wait_for_function("() => document.querySelector('#em-l0-fara-articol').hidden", timeout=10000)
    assert pg.input_value("#em-l0-um") == "buc"
    patron.captura("cu_articol")


def test_def_28_stocuri_arata_situatia_si_fara_retete_la_comert(patron, firma_e2e):
    """28. Stocuri: ecranul nu avea situația stocului; Rețete HoReCa la o firmă de comerț.
    Pașii contabilului: la o firmă de comerț (CAEN 4711) cu marfă în stoc deschide Stocuri: primul lucru e tabelul situației (articol,
    UM, cantitate, CMP, valoare, total); în „Mișcări, fișe de magazie…” nu apare secțiunea „Rețete (HoReCa)”."""
    pregateste_firma(patron, firma_e2e)
    articol_in_stoc(patron, firma_e2e)
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "stocuri", "#s-situatie-tabel")
    cap = pg.eval_on_selector_all("#s-situatie-tabel thead th", "els => els.map(e => e.textContent.trim())")
    rand = pg.eval_on_selector_all("#s-situatie-tabel tbody tr", "trs => trs.map(t => [...t.cells].map(c => c.textContent.trim()))")
    assert cap == ["Articol", "UM", "Cantitate", "CMP (lei)", "Valoare (lei)"], cap
    marfa = [r for r in rand if r[0] == ARTICOL]
    assert marfa and marfa[0][1] == "buc" and marfa[0][3] == "12,50", marfa
    assert pg.evaluate("() => { const s = document.querySelector('#s-situatie'); const t = document.querySelector('.pf-titlu'); "
                       "return !!s && s.previousElementSibling === t; }"), "situația nu e primul lucru de sub titlu"
    pg.click("#cv-toggle")
    pg.wait_for_selector("#cv-intrare", timeout=15000)
    patron.captura(intreaga=True)
    assert "Rețete (HoReCa)" not in pg.inner_text("#cv-zona")


def test_def_29_fereastra_firmei_grupata_sub_titluri(patron):
    """29. Fereastra firmei: peste 20 de carduri amestecate; grupare sub titluri.
    Pașii contabilului: deschide o firmă: cardurile stau sub titluri, în ordinea Zilnic · Registre · Raportări și declarații ·
    Operațiuni speciale · Firma; „Facturi” e la Zilnic, „Registru jurnal” la Registre, „Declarații” la Raportări."""
    patron.firma("Comert Micro TVA")
    pg = patron.pg
    grupuri = pg.eval_on_selector_all("section.firme-grup", """els => els.map(s => [s.querySelector('h3').textContent.trim(),
        [...s.querySelectorAll('.firme-optiune-titlu')].map(t => t.textContent.trim())])""")
    patron.captura(intreaga=True)
    titluri = [g[0] for g in grupuri]
    assert titluri == ["Zilnic", "Registre", "Raportări și declarații", "Operațiuni speciale", "Firma"], titluri
    pe = dict(grupuri)
    assert "Facturi" in pe["Zilnic"] and "Registru jurnal" in pe["Registre"] and "Declarații" in pe["Raportări și declarații"], pe
