# -*- coding: utf-8 -*-
"""Blocul C (DEFICIENTE.md 64–98) — deficiențele probate în browser, pașii contabilului, pe aplicația pornită de
`scripts/e2e_poarta.py` pe baza de TEST.

Datele: testele care SCRIU scriu numai pe firmele sintetice ale rulării — `firma_e2e` (din conftest), declarată aici
cantitativ-valoric, și o a doua firmă sintetică a acestui fișier, global-valorică (`firma_gv`, același prefix „E2E Probă”, deci
curățată și de conftest dacă rularea se întrerupe). Datele se creează pe drumul aplicației (core/*_api.py, cu autorul cererii
pus ca la middleware). Testele care doar deschid formulare citesc firmele de test comune; ciorna facturii stă în browser
(localStorage), nu pleacă la server.
"""
import datetime as _dt
import json
import os

import pytest

from conftest import BAZA, CAPTURI, INALT, LAT, PREFIX_FIRMA, Ecran, _db, _scoate_firmele_e2e, cui_cu_control, sql

AZI = _dt.date.today()


# ---------------------------------------------------------------- utilitare
def _uid(email):
    return sql("SELECT id, accounting_firm_id FROM public.users WHERE email = %s", (email,))[0]


def _token(email):
    from core import auth_api
    db = _db()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM public.users WHERE email=%s", (email,))
            u = cur.fetchone()
        s = auth_api.sesiune_pentru_user(conn, u[0])
        conn.rollback()
    assert s and s.get("ok"), email
    return s["token"], s["user"]


def _pune_sesiunea(pg, email):
    tok, user = _token(email)
    pg.evaluate("([t, u]) => { sessionStorage.setItem('iconta_token', t); sessionStorage.setItem('iconta_user', JSON.stringify(u)); }",
                [tok, user])


class _Fila:
    """O filă FĂRĂ scriptul de sesiune al conftest-ului (acela repune contul la fiecare încărcare): testele care schimbă
    utilizatorul în aceeași filă sau se autentifică în fila deja încărcată."""

    def __init__(self, browser, nume):
        self.ctx = browser.new_context(viewport={"width": LAT, "height": INALT})
        self.ecran = Ecran(self.ctx.new_page(), nume)

    def inchide(self):
        erori, rele = list(self.ecran.erori), list(self.ecran.cereri_rele)
        self.ctx.close()
        assert not erori, "erori JavaScript pe ecran: %s" % erori[:3]
        assert not rele, "cereri cu răspuns 5xx: %s" % rele[:3]


def _cu_autor(uid, fn):
    """Scrierea pe drumul aplicației, cu autorul cererii pus ca de middleware (`core/autor_cerere.py`), apoi — ca middleware-ul
    după orice cerere de modificare — notele ciornă ale unui utilizator fără drept de validare intră în coadă."""
    from core import autor_cerere
    tok = autor_cerere.seteaza(uid)
    try:
        return fn()
    finally:
        autor_cerere.reseteaza(tok)


def _nir(firma, nir, uid=None):
    from core import db, stocuri_api

    def scrie():
        with db.get_conn(firma["schema"]) as c:
            r = stocuri_api.adauga_nir(c, firma["schema"], nir)
            assert "eroare" not in r, r
            c.commit()
        return r
    r = _cu_autor(uid, scrie) if uid else scrie()
    if uid:
        from core import uc_coada
        uc_coada.note_in_coada(firma["tenant_id"], uid, firma["cabinet_id"])
    return r


def _deschide(ecran, firma, card, asteapta):
    ecran.firma(firma)
    ecran.pg.click("#fa-%s" % card)
    ecran.pg.wait_for_selector(asteapta, timeout=20000)


def _emite_factura(ecran, firma="Comert Micro TVA"):
    _deschide(ecran, firma, "facturi", "#fac-emite")
    ecran.pg.click("#fac-emite")
    ecran.pg.wait_for_selector("#em-l0-descriere", timeout=20000)


# ---------------------------------------------------------------- firmele sintetice
@pytest.fixture(scope="module")
def firma_cv(firma_e2e):
    """`firma_e2e` cu stocul declarat cantitativ-valoric (Date firmă, `salveaza_date` — jurnalizat cu patronul), numerotarea
    facturilor configurată (`seteaza_numerotare`), „Produs Pret 100” în nomenclator (`produse_api.creeaza`) și un articol
    „Marfa A <n>” intrat în fișa de magazie (`stocuri_cv_api.intrare`)."""
    from core import db, facturi_api, firma_profil_api
    uid, _cab = _uid("patron@prisma-cont.test")
    with db.get_conn(firma_e2e["schema"]) as c:
        r = firma_profil_api.salveaza_date(c, {"metoda_stoc": "cantitativ_valoric"}, firma_e2e["tenant_id"], uid)
        assert r.get("ok", True) is not False, r
        assert facturi_api.seteaza_numerotare(c, serie="BCE", numar_start=1)["ok"]
        c.commit()
    from core import produse_api
    with db.get_conn(firma_e2e["schema"]) as c:
        assert produse_api.creeaza(c, "Produs Pret 100", um="buc", pret_unitar=100, cota_tva=21, confirmat=True)["ok"]
        c.commit()
    marfa = "Marfa A %s" % firma_e2e["tenant_id"]
    from core import stocuri_cv_api                       # intrarea din „Mișcări, fișe de magazie” (nu prin NIR: NIR-ul e probat)
    with db.get_conn(firma_e2e["schema"]) as c:
        r = stocuri_cv_api.intrare(c, firma_e2e["schema"], {"denumire": marfa, "um": "buc", "data": AZI.isoformat(), "cantitate": 20,
                                                             "pret_unitar": 4, "document": "Inventar initial proba"})
        assert "eroare" not in r, r
        c.commit()
    return dict(firma_e2e, marfa=marfa)


@pytest.fixture(scope="module")
def firma_gv():
    """A doua firmă sintetică a cabinetului de test, creată pe drumul aplicației (`provision_tenant`), cu stocul global-valoric,
    datele de identificare completate în Date firmă (`salveaza_date`) și asistentul alocat (cel care pregătește NIR-urile din
    coadă); scoasă la final."""
    import io as _io
    import time as _t
    from core import db, firma_profil_api
    from core import tenant_provisioning as tp
    nume = "%s GV %d SRL" % (PREFIX_FIRMA, int(_t.time() * 1000) % 1000000)
    rad = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sql_t = _io.open(os.path.join(rad, "tenant_template.sql"), encoding="utf-8").read()
    uid, cab = _uid("patron@prisma-cont.test")
    with db.get_conn() as c:
        r = tp.provision_tenant(c, nume, cui_cu_control(80000000 + int(_t.time() * 1000) % 9000000), cab, uid, sql_t)
        c.commit()
    f = {"tenant_id": r["tenant_id"], "schema": r["schema_name"], "nume": nume, "cabinet_id": cab}
    with db.get_conn(f["schema"]) as c:
        rr = firma_profil_api.salveaza_date(c, {"metoda_stoc": "global_valoric", "reg_com": "J2020001234408", "caen": "4711",
                                                "adresa": "Str. Proba nr. 1", "oras": "Bucuresti", "judet": "București",
                                                "banca": "Banca Test", "iban": "RO49AAAA1B31007593840000", "telefon": "0210000001",
                                                "declarant_nume": "Popescu", "declarant_prenume": "Ion",
                                                "declarant_functie": "ADMINISTRATOR"}, f["tenant_id"], uid)
        assert rr.get("ok", True) is not False, rr
        c.commit()
    asist = _uid("asistent@prisma-cont.test")[0]
    sql("INSERT INTO public.user_tenants (user_id, tenant_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (asist, f["tenant_id"]))
    yield f
    _scoate_firmele_e2e(f["tenant_id"])


@pytest.fixture(scope="module")
def asistent_pregatitor():
    """Asistentul cabinetului de test cu „Poate pregăti” și FĂRĂ „Poate valida” (ce descrie conftest-ul): numai notele unui
    utilizator fără drept de validare intră în coadă (`coada_api.e_validator`). Pe baza de test flagul a fost găsit pornit
    (09.10.2026) — se oprește pe durata rulării și se pune la loc valoarea găsită."""
    uid = _uid("asistent@prisma-cont.test")[0]
    era = sql("SELECT poate_valida FROM public.users WHERE id = %s", (uid,))[0][0]
    sql("UPDATE public.users SET poate_valida = false WHERE id = %s", (uid,))
    yield uid
    sql("UPDATE public.users SET poate_valida = %s WHERE id = %s", (era, uid))


def _linie_gv(den, cant=10, pa=5, pv=9.68):
    return {"denumire": den, "cantitate": cant, "pret_achizitie": pa, "pret_vanzare": pv, "cota_tva": 21}


# ================================================================ 64, 70 — versiunea nouă la autentificare


def _fila_pe_cod_vechi(browser, nume):
    """Fila încarcă aplicația (ecranul de intrare) pe amprenta „proba-inainte”; apoi „se publică” o versiune nouă (amprenta
    servită se schimbă — `page.route`, nimic scris pe disc)."""
    f = _Fila(browser, nume)
    amp = {"v": "proba-inainte"}
    f.ecran.pg.route("**/static/.publicat.json*", lambda r: r.fulfill(
        status=200, content_type="application/json", body=json.dumps({"commit": amp["v"]})))
    pg = f.ecran.pg
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_function("() => performance.getEntriesByType('resource').some(x => /\\.publicat\\.json/.test(x.name))",
                         timeout=20000)
    pg.wait_for_timeout(800)
    amp["v"] = "proba-dupa-publicare"
    pg.evaluate("() => { window.__marcaj_fila = 1; }")      # o reîncărcare reală îl șterge
    return f, amp


def _intra_in_fila(pg, email):
    """Autentificarea din formularul de intrare, fără reîncărcare: `sesiune.intra` pe modulul DEJA încărcat al filei."""
    tok, user = _token(email)
    pg.evaluate("""async ([t, u]) => {
        const e = performance.getEntriesByType('resource').map(x => x.name).find(n => /\\/static\\/js\\/sesiune\\.js/.test(n));
        const m = await import(e);
        m.sesiune.intra(t, u); }""", [tok, user])


def _anunt_vizibil(pg):
    return pg.eval_on_selector_all(".versiune-noua", "els => els.filter(e => e.offsetParent !== null).length") > 0


def test_def_64_fila_pe_cod_vechi_nu_ramane_tacuta(browser):
    """64. Factură: pierdută a patra oară (filă pe cod vechi, fără anunțul „Versiune nouă”).
    Pașii contabilului: deschide pagina de intrare; între timp se publică o versiune nouă; se autentifică în aceeași filă.
    Fila NU are voie să rămână tăcută pe codul vechi: ori se reîncarcă singură pe codul publicat, ori arată „Versiune nouă”."""
    f, _amp = _fila_pe_cod_vechi(browser, "test_def_64_fila_pe_cod_vechi_nu_ramane_tacuta")
    pg = f.ecran.pg
    try:
        _intra_in_fila(pg, "patron@prisma-cont.test")
        pg.wait_for_selector(".asi-arbore, .cab-grila, .cab-card", timeout=30000)
        pg.wait_for_function("() => window.__marcaj_fila === undefined || "
                             "[...document.querySelectorAll('.versiune-noua')].some(e => e.offsetParent !== null)", timeout=15000)
        reincarcata = pg.evaluate("() => window.__marcaj_fila === undefined")
        f.ecran.captura()
        assert reincarcata or _anunt_vizibil(pg), "fila a rămas pe codul vechi fără anunț"
    finally:
        f.inchide()


def test_def_70_reincarcare_la_autentificare_numai_fara_formular(browser):
    """70. General: reîncărcare automată la autentificare, doar fără formular început.
    Pașii contabilului: (1) fila e pe codul vechi și se autentifică — nu are nimic început, deci fila se reîncarcă singură;
    (2) după aceea începe o factură și se publică din nou: acum fila NU se reîncarcă (formularul s-ar pierde), apare anunțul
    „Versiune nouă”, iar formularul rămâne cum l-a scris."""
    f, amp = _fila_pe_cod_vechi(browser, "test_def_70_reincarcare_la_autentificare_numai_fara_formular")
    pg, ecran = f.ecran.pg, f.ecran
    try:
        _intra_in_fila(pg, "patron@prisma-cont.test")
        pg.wait_for_function("() => window.__marcaj_fila === undefined", timeout=15000)   # (1) reîncărcată
        pg.wait_for_selector(".cab-grila, .cab-card", timeout=30000)
        assert not _anunt_vizibil(pg)
        ecran.captura("reincarcata")
        _emite_factura(ecran, "Comert Micro TVA")
        pg.fill("#em-nume", "Client Proba Versiune SRL")
        pg.dispatch_event("#em-nume", "input")
        pg.evaluate("() => { window.__marcaj_fila = 2; }")
        amp["v"] = "proba-a-doua-publicare"                                           # (2) o publicare cu formular început
        pg.evaluate("() => document.dispatchEvent(new Event('visibilitychange'))")
        pg.wait_for_selector(".versiune-noua", state="visible", timeout=15000)
        assert "Versiune nouă" in pg.inner_text(".versiune-noua")
        pg.wait_for_timeout(1000)
        assert pg.evaluate("() => window.__marcaj_fila") == 2, "fila s-a reîncărcat peste formularul început"
        assert pg.input_value("#em-nume") == "Client Proba Versiune SRL"
        ecran.captura("cu_formular")
    finally:
        pg.evaluate("() => { try { Object.keys(localStorage).filter(k => k.startsWith('iconta_ciorna_factura')).forEach(k => "
                    "localStorage.removeItem(k)); } catch (e) {} }")
        f.inchide()


# ================================================================ 65–68, 88, 89 — formularul facturii
def test_def_68_scadenta_propusa_la_formularul_nou(patron):
    """68. Factură: scadența „zz.ll.aaaa” la formularul nou.
    Pașii contabilului: deschide firma -> Facturi -> Emite factură. Scadența trebuie PROPUSĂ (data emiterii + termenul legal,
    Legea 72/2013 art.3 alin.(3) lit.a — 30 de zile), editabilă, nu goală „zz.ll.aaaa”; o dată a emiterii schimbată o mută."""
    pg = patron.pg
    _emite_factura(patron)
    assert pg.input_value("#em-data") == AZI.isoformat()
    pg.wait_for_function("() => document.querySelector('#em-scadenta').value !== ''", timeout=10000)
    assert pg.input_value("#em-scadenta") == (AZI + _dt.timedelta(days=30)).isoformat(), pg.input_value("#em-scadenta")
    assert "Propusă la 30 de zile" in pg.inner_text("#em-scadenta-ajutor")
    patron.captura("propusa")
    pg.fill("#em-data", "2026-09-01")
    pg.dispatch_event("#em-data", "change")
    pg.wait_for_function("() => document.querySelector('#em-scadenta').value === '2026-10-01'", timeout=10000)
    pg.fill("#em-scadenta", "2026-12-15")
    pg.dispatch_event("#em-scadenta", "change")
    pg.fill("#em-data", "2026-09-05")
    pg.dispatch_event("#em-data", "change")
    pg.wait_for_timeout(300)
    assert pg.input_value("#em-scadenta") == "2026-12-15", "scadența scrisă de om a fost suprascrisă"
    patron.captura("editata")


def test_def_66_pretul_neales_de_om_nu_ramane_pe_rand(patron, firma_cv):
    """66. Factură: prețul unitar precompletat cu 100 la fiecare rând nou.
    Pașii: firma are în nomenclator „Produs Pret 100” (100,00 lei). Emite factură -> pe rând scrie „Produs Pret 100”: prețul
    100 vine ca PROPUNERE din nomenclator -> scrie peste denumire „Serviciu consultanta”: prețul propus pleacă (câmpul rămâne gol,
    nu 100 și nu 0) -> „+ Adaugă linie”: rândul nou are prețul gol. Un preț pe care nu l-a ales omul nu rămâne pe rând
    (CF art.319 alin.(20) lit.i — prețul unitar e al facturii, nu al aplicației)."""
    pg = patron.pg
    try:
        _emite_factura(patron, firma_cv["nume"])
        pg.fill("#em-l0-descriere", "Produs Pret 100")
        pg.dispatch_event("#em-l0-descriere", "input")
        pg.wait_for_function("() => document.querySelector('#em-l0-pret_unitar').value === '100'", timeout=15000)
        patron.captura("propus")
        pg.fill("#em-l0-descriere", "Serviciu consultanta")
        pg.dispatch_event("#em-l0-descriere", "input")
        pg.wait_for_timeout(1500)                                  # potrivirea denumirii noi a răspuns (fără preț în nomenclator)
        assert pg.input_value("#em-l0-pret_unitar") == "", "prețul propus pentru alt produs a rămas pe rând"
        pg.click("#em-add-linie")
        pg.wait_for_selector("#em-l1-pret_unitar", timeout=10000)
        assert pg.input_value("#em-l1-pret_unitar") == ""
        assert pg.input_value("#em-l0-pret_unitar") == ""
        pg.locator("#em-l1-pret_unitar").scroll_into_view_if_needed()
        patron.captura("golit")
    finally:
        pg.evaluate("() => { try { Object.keys(localStorage).filter(k => k.startsWith('iconta_ciorna_factura')).forEach(k => "
                    "localStorage.removeItem(k)); } catch (e) {} }")


def test_def_65_ciorna_facturii_nu_trece_la_alta_firma_sau_alt_utilizator(browser):
    """65. Factură: ciorna unui utilizator/firme nu trebuie să apară la altul.
    Pașii: contabilul-șef începe o factură la „Coafor Micro Neplatitor” (scrie clientul) și pleacă din formular. (a) Deschide
    „Emite factură” la „Comert Micro TVA”: formularul e gol, fără „Factura începută a fost păstrată”. (b) În același browser
    intră asistentul și deschide factura la „Coafor Micro Neplatitor”: nici el nu vede ciorna șefului. (c) Martor: șeful,
    înapoi la Coafor, își regăsește ciorna."""
    f = _Fila(browser, "test_def_65_ciorna_facturii_nu_trece_la_alta_firma_sau_alt_utilizator")
    pg, ecran = f.ecran.pg, f.ecran
    try:
        pg.goto(BAZA + "/", wait_until="domcontentloaded")
        _pune_sesiunea(pg, "patron@prisma-cont.test")
        _emite_factura(ecran, "Coafor Micro Neplatitor")
        pg.fill("#em-nume", "Client Ciorna Sef SRL")
        pg.dispatch_event("#em-nume", "input")
        _emite_factura(ecran, "Comert Micro TVA")                                     # (a) altă firmă
        assert pg.input_value("#em-nume") == ""
        assert "a fost păstrată" not in pg.inner_text("#em-ciorna")
        ecran.captura("alta_firma")
        _pune_sesiunea(pg, "asistent@prisma-cont.test")                                # (b) alt utilizator, același browser
        _emite_factura(ecran, "Coafor Micro Neplatitor")
        assert pg.input_value("#em-nume") == ""
        assert "a fost păstrată" not in pg.inner_text("#em-ciorna")
        ecran.captura("alt_utilizator")
        _pune_sesiunea(pg, "patron@prisma-cont.test")                                 # (c) martor
        _emite_factura(ecran, "Coafor Micro Neplatitor")
        assert pg.input_value("#em-nume") == "Client Ciorna Sef SRL"
        assert "a fost păstrată" in pg.inner_text("#em-ciorna")
        ecran.captura("martor")
    finally:
        pg.evaluate("() => { try { Object.keys(localStorage).filter(k => k.startsWith('iconta_ciorna_factura')).forEach(k => "
                    "localStorage.removeItem(k)); } catch (e) {} }")
        f.inchide()


def test_def_88_platitor_tva_ramane_dupa_restaurarea_ciornei(patron):
    """88. Factură: după restaurarea ciornei dispărea „plătitor TVA”.
    Pașii: Emite factură -> CUI client -> „Verifică” (răspunsul ANAF: plătitor de TVA) -> pleacă din formular -> revine la
    „Emite factură”: ciorna e restaurată ȘI arată în continuare „plătitor TVA” sub CUI. (Răspunsul ANAF e servit de probă, ca
    serviciu extern — `page.route`; ce se probează e ce face ecranul cu el.)"""
    pg = patron.pg
    cui = cui_cu_control(31000000)
    pg.route("**/verifica-cui/**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(
        {"gasit": True, "denumire": "Client Platitor Proba SRL", "adresa": "Str. Proba 1, Bucuresti", "platitor_tva": True,
         "inactiv": False})))
    try:
        _emite_factura(patron, "Comert Micro TVA")
        pg.fill("#em-cui", cui)
        pg.click("#em-verifica")
        pg.wait_for_function("() => (document.querySelector('#em-cui-stare') || {innerText: ''}).innerText.includes('plătitor TVA')", timeout=10000)
        patron.captura("verificat")
        _emite_factura(patron, "Comert Micro TVA")
        assert "a fost păstrată" in pg.inner_text("#em-ciorna")
        assert pg.input_value("#em-cui") == cui
        assert "plătitor TVA" in pg.inner_text("#em-cui-stare"), pg.inner_text("#em-cui-stare")
        patron.captura("restaurata")
    finally:
        pg.evaluate("() => { try { Object.keys(localStorage).filter(k => k.startsWith('iconta_ciorna_factura')).forEach(k => "
                    "localStorage.removeItem(k)); } catch (e) {} }")


def test_def_67_randul_scris_de_mana_se_dezleaga_de_articol(patron, firma_cv):
    """67. Factură: un rând scris de mână rămânea legat de „Marfa A”.
    Pașii: firma cu stoc pe articole -> Emite factură -> pe rând alege articolul „Marfa A” (denumirea se completează) -> scrie
    peste denumire „Carte – Ghid contabil 2026”. Rândul NU mai e legat de „Marfa A” (lista arată „fără articol”), iar sub el
    apare informarea „Linie fără articol de stoc”."""
    pg = patron.pg
    try:
        _emite_factura(patron, firma_cv["nume"])
        pg.select_option("#em-l0-articol", label=pg.locator("#em-l0-articol option", has_text=firma_cv["marfa"]).first.inner_text())
        pg.wait_for_function("(m) => document.querySelector('#em-l0-descriere').value === m", arg=firma_cv["marfa"], timeout=5000)
        assert pg.input_value("#em-l0-articol") != ""
        pg.fill("#em-l0-descriere", "Carte – Ghid contabil 2026")
        pg.dispatch_event("#em-l0-descriere", "input")
        pg.wait_for_timeout(300)
        assert pg.input_value("#em-l0-articol") == "", "rândul scris de mână a rămas legat de articol"
        assert pg.is_visible("#em-l0-fara-articol")
        pg.locator("#em-l0-fara-articol").scroll_into_view_if_needed()
        patron.captura()
    finally:
        pg.evaluate("() => { try { Object.keys(localStorage).filter(k => k.startsWith('iconta_ciorna_factura')).forEach(k => "
                    "localStorage.removeItem(k)); } catch (e) {} }")


def test_def_89_linia_fara_articol_e_informare_nu_eroare(patron, firma_cv):
    """89. Factură: „Linie fără articol de stoc” roșu, ca eroare.
    Pașii: firma cu stoc pe articole -> Emite factură -> scrie un rând fără articol („Consultanță”). Sub rând apare textul
    „Linie fără articol de stoc…” ca INFORMARE (caseta informativă, fără roșu), nu ca eroare."""
    pg = patron.pg
    try:
        _emite_factura(patron, firma_cv["nume"])
        pg.fill("#em-l0-descriere", "Consultanta contabila")
        pg.dispatch_event("#em-l0-descriere", "input")
        pg.wait_for_selector("#em-l0-fara-articol", state="visible", timeout=5000)
        el = pg.locator("#em-l0-fara-articol")
        assert "Linie fără articol de stoc" in el.inner_text()
        cls = el.get_attribute("class")
        assert "caseta-info" in cls and "eroare" not in cls, cls
        culoare = pg.evaluate("() => getComputedStyle(document.querySelector('#em-l0-fara-articol .ci-mesaj') || "
                              "document.querySelector('#em-l0-fara-articol')).color")
        rosu = pg.evaluate("() => { const s = document.createElement('span'); s.className = 'msg-eroare'; document.body.append(s); "
                           "const c = getComputedStyle(s).color; s.remove(); return c; }")
        assert culoare != rosu, "informarea e colorată ca eroarea (%s)" % culoare
        el.scroll_into_view_if_needed()
        patron.captura()
    finally:
        pg.evaluate("() => { try { Object.keys(localStorage).filter(k => k.startsWith('iconta_ciorna_factura')).forEach(k => "
                    "localStorage.removeItem(k)); } catch (e) {} }")


# ================================================================ 82–87 — NIR-ul
def _formular_nir(ecran, firma):
    _deschide(ecran, firma, "stocuri", "#sn-toggle")
    ecran.pg.click("#sn-toggle")
    ecran.pg.wait_for_selector("#sn-numar", state="visible", timeout=10000)


def _nir_cv_din_ecran(ecran, firma, numar, articol_nou, cant="10", pret="5"):
    pg = ecran.pg
    _formular_nir(ecran, firma)
    pg.fill("#sn-numar", numar)
    pg.fill("#sn-furn", "Furnizor Ecran SRL")
    pg.select_option("#nir-l0-articol", "nou")
    pg.wait_for_selector("#nir-l0-denumire", timeout=5000)
    pg.fill("#nir-l0-denumire", articol_nou)
    pg.fill("#nir-l0-cantitate", cant)
    pg.fill("#nir-l0-pret_achizitie", pret)
    pg.select_option("#nir-l0-cota_tva", "21")
    pg.click("#sn-salveaza")
    pg.wait_for_function("() => (document.querySelector('#s-mesaj') || {innerText: ''}).innerText.includes('NIR salvat')",
                         timeout=20000)


def test_def_82_nir_la_cost_pe_cantitativ_valoric(patron, firma_cv):
    """82. NIR: pe CMP încărca 371 la preț de vânzare, ieșirile la CMP.
    Pașii: firma cantitativ-valorică -> Stocuri -> + NIR nou -> articol nou, 10 buc × 5,00 lei, TVA 21% -> Salvează. Marfa
    intră la COST: mesajul „la cost 50,00 lei”, notele 371 = 408 50,00 și 4428.01 = 408 10,50 (NIR fără factură), fără adaos
    378 și fără preț de raft (OMFP 1802/2014 pct.287 — consecvența metodei)."""
    pg = patron.pg
    _formular_nir(patron, firma_cv["nume"])
    assert pg.locator("#nir-l0-pret_vanzare").count() == 0, "la cost formularul cere preț de raft"
    _nir_cv_din_ecran(patron, firma_cv["nume"], "CV-82", "Articol 82 %s" % firma_cv["tenant_id"])
    assert "la cost 50,00 lei" in pg.inner_text("#s-mesaj"), pg.inner_text("#s-mesaj")
    patron.captura()
    s = firma_cv["schema"]
    note = sql('SELECT l.cont_debit, l.cont_credit, l.suma::text FROM "%s".nir n JOIN "%s".inregistrari_linii l ON '
               "n.inregistrari_ids @> to_jsonb(l.inregistrare_id) WHERE n.numar = 'CV-82' ORDER BY l.cont_debit" % (s, s))
    assert sorted(note) == [("371", "408", "50.00"), ("4428.01", "408", "10.50")], note


def test_def_85_articolul_nir_se_alege_din_lista(patron, firma_cv):
    """85. NIR: articolul text liber.
    Pașii: firma cantitativ-valorică -> + NIR nou. Articolul se ALEGE din listă (nu e câmp de text liber); „+ articol nou…” cere
    explicit denumirea. Un articol „nou” scris „Marfa  A” (cu două spații) peste „Marfa A” existent se refuză lângă câmp, cu numele
    celui existent; ales din listă, NIR-ul se salvează pe articolul existent."""
    pg = patron.pg
    _formular_nir(patron, firma_cv["nume"])
    assert pg.evaluate("() => document.querySelector('#nir-l0-articol').tagName") == "SELECT"
    assert pg.locator("#nir-l0-denumire").count() == 0, "articolul are câmp de text liber"
    opt = pg.eval_on_selector_all("#nir-l0-articol option", "os => os.map(o => o.textContent.trim())")
    assert firma_cv["marfa"] in opt and "+ articol nou…" in opt, opt
    pg.fill("#sn-numar", "CV-85")
    pg.select_option("#nir-l0-articol", "nou")
    pg.wait_for_selector("#nir-l0-denumire", timeout=5000)
    pg.fill("#nir-l0-denumire", firma_cv["marfa"].replace("Marfa A", "Marfa  A"))
    pg.fill("#nir-l0-cantitate", "2")
    pg.fill("#nir-l0-pret_achizitie", "4")
    pg.select_option("#nir-l0-cota_tva", "21")
    pg.click("#sn-salveaza")
    pg.wait_for_selector(".msg-eroare[data-camp='nir-l0-denumire']", timeout=10000)
    msg = pg.inner_text(".msg-eroare[data-camp='nir-l0-denumire']")
    assert "există deja" in msg and firma_cv["marfa"] in msg, msg
    patron.captura("refuz")
    pg.select_option("#nir-l0-articol", label=firma_cv["marfa"])
    pg.wait_for_selector("#nir-l0-cantitate", timeout=5000)
    pg.fill("#nir-l0-cantitate", "2")
    pg.fill("#nir-l0-pret_achizitie", "4")
    pg.select_option("#nir-l0-cota_tva", "21")
    pg.click("#sn-salveaza")
    pg.wait_for_function("() => (document.querySelector('#s-mesaj') || {innerText: ''}).innerText.includes('NIR salvat')",
                         timeout=20000)
    patron.captura("ales")
    s = firma_cv["schema"]
    r = sql('SELECT a.denumire FROM "%s".nir_linii l JOIN "%s".nir n ON n.id = l.nir_id JOIN "%s".articole a ON a.id = l.articol_id '
            "WHERE n.numar = 'CV-85'" % (s, s, s))
    assert r == [(firma_cv["marfa"],)], r
    assert sql('SELECT count(*) FROM "%s".articole WHERE lower(regexp_replace(denumire, \'\\s+\', \' \', \'g\')) = lower(%%s)' % s,
               (firma_cv["marfa"],))[0][0] == 1


def test_def_86_nir_salvat_se_deschide(patron, firma_cv):
    """86. NIR: NIR-ul salvat nu se putea deschide din „NIR-urile lunii”.
    Pașii: Stocuri -> NIR-urile lunii -> pe NIR-ul salvat „Deschide NIR-ul: articolele și notele →”. Se deschide NIR-ul cu
    articolele lui (cantitate, preț) și notele lui, fiecare cu starea."""
    pg = patron.pg
    _nir_cv_din_ecran(patron, firma_cv["nume"], "CV-86", "Articol 86 %s" % firma_cv["tenant_id"], cant="3", pret="7")
    btn = pg.locator(".nir-deschide[data-numar='CV-86']")
    btn.click()
    pg.wait_for_selector("text=Notele NIR-ului", timeout=15000)
    t = patron.fereastra()
    assert "NIR CV-86" in t and "Articol 86" in t and "21,00" in t and "371" in t and "408" in t, t[:800]
    assert "ciornă" in t or "validat" in t
    patron.captura()


def test_def_87_stocul_arata_intrarea_nir_imediat(patron, firma_cv):
    """87. Stocuri: tabelul de stoc neschimbat după NIR, fără explicație.
    Pașii: firma cantitativ-valorică -> Stocuri -> NIR nou, articol nou 4 buc × 12,50 -> Salvează. Situația stocului de sus arată
    imediat articolul cu 4 buc și 50,00 lei, iar mesajul spune că intrarea e deja în fișa de magazie."""
    pg = patron.pg
    art = "Articol 87 %s" % firma_cv["tenant_id"]
    _nir_cv_din_ecran(patron, firma_cv["nume"], "CV-87", art, cant="4", pret="12.5")
    assert "stocul de mai sus o arată deja" in pg.inner_text("#s-mesaj")
    pg.wait_for_selector("#s-situatie-tabel", timeout=15000)
    rand = pg.locator("#s-situatie-tabel tbody tr", has_text=art)
    assert rand.count() == 1
    td = [x.strip() for x in rand.locator("td").all_inner_texts()]
    assert td[2] in ("4", "4,000", "4,00") and td[4] == "50,00", td
    patron.captura()


def test_def_83_pretul_de_raft_gol_se_cere_langa_camp(patron, firma_gv):
    """83. NIR: prețul de raft gol luat drept 0; refuz fără diacritice, departe de câmp.
    Pașii: firma global-valorică -> Stocuri -> + NIR nou -> fără factură -> articol 10 × 5,00, prețul de raft LĂSAT GOL -> Salvează.
    Refuzul apare lângă câmpul „preț raft”, cu diacritice („prețul de raft (cu TVA)”); nimic nu se salvează."""
    pg = patron.pg
    _formular_nir(patron, firma_gv["nume"])
    pg.fill("#sn-numar", "GV-83")
    pg.select_option("#sn-factura", "fara")
    pg.fill("#nir-l0-denumire", "Marfa Raft Gol")
    pg.fill("#nir-l0-cantitate", "10")
    pg.fill("#nir-l0-pret_achizitie", "5")
    pg.select_option("#nir-l0-cota_tva", "21")
    pg.click("#sn-salveaza")
    pg.wait_for_selector(".msg-eroare[data-camp='nir-l0-pret_vanzare']", timeout=10000)
    msg = pg.inner_text(".msg-eroare[data-camp='nir-l0-pret_vanzare']")
    assert "prețul de raft (cu TVA)" in msg, msg
    assert pg.get_attribute("#nir-l0-pret_vanzare", "aria-invalid") == "true"
    patron.captura()
    assert sql('SELECT count(*) FROM "%s".nir WHERE numar = %%s' % firma_gv["schema"], ("GV-83",))[0][0] == 0


def test_def_84_furnizorul_nir_din_anaf(patron, firma_gv):
    """84. NIR: furnizor și CUI de mână, fără „Verifică” din ANAF.
    Pașii: + NIR nou -> CUI furnizor -> „Verifică”: denumirea furnizorului se completează din răspunsul ANAF, iar sub CUI apare
    denumirea și „plătitor TVA”. (Răspunsul ANAF e servit de probă — serviciu extern, `page.route`.)"""
    pg = patron.pg
    cui = cui_cu_control(32000000)
    pg.route("**/verifica-cui/**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(
        {"gasit": True, "denumire": "Furnizor Anaf Proba SRL", "adresa": "Str. Proba 2", "platitor_tva": True, "inactiv": False})))
    _formular_nir(patron, firma_gv["nume"])
    assert pg.is_visible("#sn-verifica")
    pg.fill("#sn-cui", cui)
    pg.click("#sn-verifica")
    pg.wait_for_function("() => (document.querySelector('#sn-cui-stare') || {innerText: ''}).innerText.includes('plătitor TVA')", timeout=10000)
    assert pg.input_value("#sn-furn") == "Furnizor Anaf Proba SRL"
    assert "Furnizor Anaf Proba SRL" in pg.inner_text("#sn-cui-stare")
    patron.captura()


# ================================================================ 80, 91, 92 — coada de validare
def _coada(ecran):
    ecran.acasa()
    ecran.pg.click("button.cab-card:has([data-cheie='validat'])")
    ecran.pg.wait_for_selector("#val-titlu", timeout=20000)


def _card_firma(ecran, firma):
    return ecran.pg.locator(".val-card", has_text=firma["nume"])


def test_def_80_nir_un_singur_element_in_coada(patron, firma_gv, asistent_pregatitor):
    """80. Coadă: notele F1A3 apăreau separat; grupare și pentru NIR.
    Pașii: asistentul face un NIR (global-valoric, fără factură: 4 note) -> contabilul-șef deschide coada „De validat”: NIR-ul
    apare O SINGURĂ DATĂ, ca un document cu cele 4 note („Vezi notele →”), nu 4 elemente separate."""
    asist = _uid("asistent@prisma-cont.test")[0]
    _nir(firma_gv, {"numar": "GV-80", "data": AZI.isoformat(), "furnizor": "Furnizor Coada 80 SRL", "transport": 0, "taxe": 0,
                    "linii": [_linie_gv("Marfa Coada 80")]}, uid=asist)
    pg = patron.pg
    _coada(patron)
    carduri = pg.locator(".val-card", has_text="Furnizor Coada 80")
    pg.wait_for_function("() => [...document.querySelectorAll('.val-card')].some(c => c.innerText.includes('Furnizor Coada 80'))",
                         timeout=15000)
    assert carduri.count() == 1, "NIR-ul apare în %d elemente" % carduri.count()
    txt = carduri.first.inner_text()
    assert "Vezi notele" in txt and "4 note" in txt, txt
    carduri.first.scroll_into_view_if_needed()
    patron.captura()


def test_def_92_butonul_respinge_din_dialog_e_rosu_plin(patron, firma_gv, asistent_pregatitor):
    """92. Coadă: butonul „Respinge” părea dezactivat.
    Pașii: coada -> pe nota pregătită de asistent „Respinge” -> în dialog, butonul de confirmare „Respinge” arată ca butonul care
    l-a deschis (roșu plin, activ), nu roz-pal ca un buton dezactivat."""
    asist = _uid("asistent@prisma-cont.test")[0]
    _nir(firma_gv, {"numar": "GV-92", "data": AZI.isoformat(), "furnizor": "Furnizor Coada 92 SRL", "transport": 0, "taxe": 0,
                    "linii": [_linie_gv("Marfa Coada 92")]}, uid=asist)
    pg = patron.pg
    _coada(patron)
    card = pg.locator(".val-card", has_text="Furnizor Coada 92").first
    card.wait_for(timeout=15000)
    stil = "(e) => { const s = getComputedStyle(e); return [s.backgroundColor, s.color, s.opacity]; }"
    pe_card = card.locator(".val-respinge").evaluate(stil)
    card.locator(".val-respinge").click()
    pg.wait_for_selector("#dlg-ok", timeout=10000)
    in_dialog = pg.locator("#dlg-ok").evaluate(stil)
    patron.captura()
    assert pg.inner_text("#dlg-ok").strip() == "Respinge"
    assert in_dialog == pe_card, "dialog %s ≠ card %s" % (in_dialog, pe_card)
    pg.click("#dlg-anuleaza")


def test_def_91_respingerea_e_confirmata_pe_ecran(patron, firma_gv, asistent_pregatitor):
    """91. Coadă: după Respinge, mesajul nu confirma acțiunea.
    Pașii: coada -> NIR-ul pregătit de asistent -> „Respinge” -> motiv „lipsește factura” -> „Respinge”. Ecranul confirmă ce ai
    făcut: „Ai respins cele 4 note ale documentului … Motivul („lipsește factura”) apare …”, iar NIR-ul nu mai e în listă."""
    asist = _uid("asistent@prisma-cont.test")[0]
    _nir(firma_gv, {"numar": "GV-91", "data": AZI.isoformat(), "furnizor": "Furnizor Coada 91 SRL", "transport": 0, "taxe": 0,
                    "linii": [_linie_gv("Marfa Coada 91")]}, uid=asist)
    pg = patron.pg
    _coada(patron)
    card = pg.locator(".val-card", has_text="Furnizor Coada 91").first
    card.wait_for(timeout=15000)
    card.locator(".val-respinge").click()
    pg.wait_for_selector("#dlg-input", timeout=10000)
    pg.fill("#dlg-input", "lipsește factura")
    pg.click("#dlg-ok")
    pg.wait_for_function("() => [...document.querySelectorAll('.caseta-info')].some(e => e.innerText.includes('Ai respins'))",
                         timeout=15000)
    msg = pg.locator(".caseta-info", has_text="Ai respins").first.inner_text()
    assert "lipsește factura" in msg and "4 note" in msg, msg
    assert pg.locator(".val-card", has_text="Furnizor Coada 91").count() == 0
    patron.captura()


# ================================================================ 94 — metodele de stoc nesuportate
def test_def_94_metoda_de_stoc_nesuportata_refuzata_clar(patron):
    """94. Stoc: combinațiile nesuportate (cantitativ la preț de vânzare, FIFO) refuzate clar.
    Pașii: firma fără metodă declarată -> Date firmă -> Stoc: lista arată și cele două combinații „nesuportat încă” (nu le
    ascunde) -> alege „cantitativ-valoric la cost FIFO” -> Salvează: refuz clar „nu e suportată încă”, nimic salvat."""
    pg = patron.pg
    inainte = sql("SELECT metoda_stoc, reg_com FROM tenant_003.firma_profil")
    _deschide(patron, "Comert Micro TVA", "datefirma", "#df-metoda_stoc")
    opt = pg.eval_on_selector_all("#df-metoda_stoc option", "os => os.map(o => [o.value, o.textContent.trim()])")
    texte = [t for _v, t in opt]
    assert any("FIFO" in t and "nesuportat încă" in t for t in texte), texte
    assert any("preț de vânzare" in t and "nesuportat încă" in t for t in texte), texte
    pg.select_option("#df-metoda_stoc", "cantitativ_valoric_fifo")
    if not pg.input_value("#df-reg_com"):           # câmp obligatoriu gol pe firma de test: refuzul metodei vine înaintea oricărei scrieri
        pg.fill("#df-reg_com", "J40/1234/2020")
    pg.click("#df-salveaza")
    pg.wait_for_function("() => document.body.innerText.includes('nu e suportată încă')", timeout=15000)
    patron.captura()
    assert sql("SELECT metoda_stoc, reg_com FROM tenant_003.firma_profil") == inainte


# ================================================================ 71, 75, 76, 78 — Operațiuni speciale
def _operatiune(ecran, firma, titlu):
    _deschide(ecran, firma, "operatiuni", "[data-op]")
    ecran.pg.locator("button[data-op]", has_text=titlu).first.click()
    ecran.pg.wait_for_selector("#op-trimite", timeout=10000)


def test_def_71_mijlocul_fix_se_alege_din_registru(patron):
    """71. Mijloace fixe: „ID mijloc fix” la reevaluare și casare se tasta de mână.
    Pașii: firma cu un mijloc fix („Constructii Profit Trim”: MF001 Excavator CAT) -> Operațiuni speciale -> „Reevaluare
    imobilizări” -> Operație: Reevaluare MF. Mijlocul fix se ALEGE dintr-o listă din registrul activelor (cod · denumire · rămas),
    nu se tastează un ID intern. La fel la „Inventariere anuală” -> Casare."""
    pg = patron.pg
    _operatiune(patron, "Constructii Profit Trim", "Reevaluare imobilizări")
    pg.select_option("#op-operatie", "reevaluare")
    sel = pg.locator("#op-mijloc_fix_id")
    assert sel.evaluate("e => e.tagName") == "SELECT"
    pg.wait_for_function("() => [...document.querySelectorAll('#op-mijloc_fix_id option')].some(o => o.textContent.includes('Excavator CAT'))",
                         timeout=10000)
    assert "MF001" in pg.inner_text("#op-mijloc_fix_id")
    patron.captura("reevaluare")
    _operatiune(patron, "Constructii Profit Trim", "Inventariere anuală")
    pg.select_option("#op-operatie", "casare")
    assert pg.locator("#op-mijloc_fix_id").evaluate("e => e.tagName") == "SELECT"
    pg.wait_for_function("() => [...document.querySelectorAll('#op-mijloc_fix_id option')].some(o => o.textContent.includes('Excavator CAT'))",
                         timeout=10000)
    patron.captura("casare")


def test_def_75_achizitia_de_la_agricultor_deschide_formularul_ei(patron):
    """75. Operațiuni: „Achiziție de la agricultor” deschidea formularul de vânzare.
    Pașii: Operațiuni speciale -> „Achiziție de la agricultor (compensare 8%)”. Se deschide formularul ACHIZIȚIEI (titlul ei,
    „Agricultor în registru”, contul de cheltuială/stoc), nu „Vânzare către agricultor”."""
    pg = patron.pg
    _operatiune(patron, "Comert Micro TVA", "Achiziție de la agricultor")
    t = patron.fereastra()
    assert "Achiziție de la agricultor (compensare 8%)" in t, t[:300]
    assert "Vânzare către agricultor" not in t
    assert pg.locator("#op-agricultor_in_registru").count() == 1
    assert pg.locator("#op-cont_cheltuiala").count() == 1
    patron.captura()


def test_def_78_conturile_vin_precompletate_si_modificabile(patron):
    """78. Operațiuni: conturile trebuiau tastate; acum precompletate și modificabile.
    Pașii: Operațiuni speciale -> „Lichidare / radiere firmă” -> Vânzare activ la lichidare: „Cont imobilizare” vine 2131 și
    „Cont amortizare” 2813 (cazul uzual, vizibil înainte de generare), se pot schimba; golit, contul se cere („Câmp obligatoriu”)."""
    pg = patron.pg
    _operatiune(patron, "Comert Micro TVA", "Lichidare / radiere firmă")
    pg.select_option("#op-operatie", "vanzare_activ")
    assert pg.input_value("#op-cont_imobilizare") == "2131"
    assert pg.input_value("#op-cont_amortizare") == "2813"
    patron.captura("precompletat")
    pg.fill("#op-cont_imobilizare", "2133")
    assert pg.input_value("#op-cont_imobilizare") == "2133"
    pg.fill("#op-cont_imobilizare", "")
    pg.fill("#op-data", AZI.isoformat())
    for c in ("pret", "valoare_bruta", "amortizare_cumulata", "cota"):
        pg.fill("#op-%s" % c, "21" if c == "cota" else "100")
    pg.click("#op-trimite")
    pg.wait_for_function("() => (document.querySelector('#op-mesaj') || {innerText: ''}).innerText.includes('Câmp obligatoriu')", timeout=5000)
    assert "Cont imobilizare" in pg.inner_text("#op-mesaj")
    patron.captura("golit")


def test_def_76_datele_citite_de_server_sunt_cerute_de_formular(patron, firma_cv):
    """76. Formulare: 33 de date citite de server nu erau cerute de formular.
    Pașii (cazul probat la reparație): Operațiuni speciale -> „Credite bancare” -> Plată rată: formularul cere acum dobânda,
    comisionul și „Dobânda a fost înregistrată deja pe 666” (Da/Nu, fără preselecție). Rata 1.000 (sub 1 an) + dobândă 200
    neangajată + comision 50 -> nota are rata (… = 5121 1.000), 666 = 5121 200 și 627 = 5121 50 (înainte: doar rata)."""
    pg = patron.pg
    _operatiune(patron, firma_cv["nume"], "Credite bancare")
    pg.select_option("#op-operatie", "plata")
    for c in ("dobanda", "rata", "comision", "dobanda_angajata"):
        assert pg.is_visible("#op-%s" % c), c
    assert pg.input_value("#op-dobanda_angajata") == "", "Da/Nu preselectat"
    pg.fill("#op-data", AZI.isoformat())
    pg.select_option("#op-tip", "scurt")
    pg.fill("#op-rata", "1000")
    pg.fill("#op-dobanda", "200")
    pg.fill("#op-comision", "50")
    pg.select_option("#op-dobanda_angajata", label="Nu")
    pg.fill("#op-descriere", "Rata credit proba 76")
    pg.click("#op-trimite")
    pg.wait_for_function("() => (document.querySelector('#op-mesaj') || {innerText: ''}).innerText.includes('Notă generată')", timeout=15000)
    patron.captura()
    nid = int(pg.inner_text("#op-mesaj").split("#")[1].split(".")[0])
    linii = sql('SELECT cont_debit, cont_credit, suma::text FROM "%s".inregistrari_linii WHERE inregistrare_id = %%s ORDER BY cont_debit'
                % firma_cv["schema"], (nid,))
    assert ("666", "5121", "200.00") in linii and ("627", "5121", "50.00") in linii, linii
    assert any(cr == "5121" and s == "1000.00" for _d, cr, s in linii), linii


# ================================================================ 77 — preselecția permisă (cazul uzual / dedus)
def test_def_77_preselectia_uzuala_si_dedusa_vizibila(patron):
    """77. Formulare: regula DS cap.17 aplicată prea strict.
    Pașii: Emite factură: moneda vine RON, tipul operației „Operațiune normală”, documentul „Factura” (cazul uzual, vizibil,
    schimbabil — nu „— alege —”); un CUI „DE123456789” face ca țara să fie DEDUSĂ Germania (DE), schimbabilă din listă."""
    pg = patron.pg
    try:
        _emite_factura(patron, "Comert Micro TVA")
        assert pg.input_value("#em-moneda") == "RON"
        assert pg.input_value("#em-tipop") == "normal"
        assert pg.input_value("#em-tip") == "factura"
        assert pg.input_value("#em-tara") == "RO"
        pg.fill("#em-cui", "DE123456789")
        pg.dispatch_event("#em-cui", "change")
        pg.wait_for_function("() => document.querySelector('#em-tara').value === 'DE'", timeout=5000)
        pg.select_option("#em-tara", "AT")
        assert pg.input_value("#em-tara") == "AT"
        patron.captura()
    finally:
        pg.evaluate("() => { try { Object.keys(localStorage).filter(k => k.startsWith('iconta_ciorna_factura')).forEach(k => "
                    "localStorage.removeItem(k)); } catch (e) {} }")


# ================================================================ 72 — bilanțul prin coadă
def test_def_72_bilantul_intra_in_coada(patron, firma_gv):
    """72. Bilanț: nu trecea prin coada pregătit → validat → depus.
    Pașii: firma -> Bilanț anual -> an 2025, S1005 -> „Trimite în coadă →”. Bilanțul intră în coada de validare (mesaj „a intrat
    în coada de validare”), iar în coada cabinetului apare S1005 al firmei."""
    pg = patron.pg
    _deschide(patron, firma_gv["nume"], "bilant", "#bl-coada")
    pg.fill("#bl-an", "2025")
    pg.select_option("#bl-tip", "s1005")
    pg.click("#bl-coada")
    pg.wait_for_function("() => (document.querySelector('#bl-coada-mesaj') || {innerText: ''}).innerText.trim() !== ''", timeout=60000)
    patron.captura("trimis")
    msg = pg.inner_text("#bl-coada-mesaj")
    assert "a intrat în coada de validare" in msg, msg
    r = sql("SELECT tip, stare FROM public.declaratii_coada WHERE tenant_id = %s AND tip = 's1005'", (firma_gv["tenant_id"],))
    assert len(r) == 1 and r[0][1] in ("la_senior", "aprobata"), r


# ================================================================ 79 — Da/Nu din schemă, cerute la prima folosire
def test_def_79_da_nu_din_schema_cerute_la_prima_folosire(patron, firma_gv):
    """79. Date firmă: Da/Nu implicite din schemă se cer o dată, la prima folosire.
    Pașii: firma nouă -> Date firmă: „Exceptată de la casa de marcat” și „Înregistrată art. 317” stau pe „— alege —” (nu „Nu”
    pus de schemă). Prima folosire — D301 — cere răspunsul: „Nedeclarat în Date firmă: firma e înregistrată … art. 317 CF?”."""
    pg = patron.pg
    _deschide(patron, firma_gv["nume"], "datefirma", "#df-activitate_exceptata_amef")
    assert pg.input_value("#df-activitate_exceptata_amef") == ""
    assert pg.input_value("#vf-inreg_art317") == ""
    assert "alege" in pg.locator("#df-activitate_exceptata_amef option:checked").inner_text()
    patron.captura("date_firma")
    _deschide(patron, firma_gv["nume"], "declaratii", "#dec-tip")
    pg.select_option("#dec-tip", "d301")
    pg.click("#dec-continua")
    pg.wait_for_function("() => document.body.innerText.includes('art. 317 CF?')", timeout=60000)
    patron.captura("d301")


# ================================================================ 96 — raportul Z la cantitativ-valoric
def test_def_96_raportul_z_nu_se_valideaza_fara_descarcare(patron, firma_cv):
    """96. Raport Z: la cantitativ-valoric nu se validează fără descărcarea pe articol.
    Pașii: firma cantitativ-valorică -> Raport Z: 121,00 lei la 21%, numerar, 3 bonuri -> Generează notă: nota e CIORNĂ, iar
    secțiunea de descărcare arată Z-ul „Nedescărcat”. Registru jurnal -> „Validează” pe nota Z: refuz „nu se validează fără
    descărcarea mărfii vândute”, nota rămâne ciornă."""
    pg = patron.pg
    _deschide(patron, firma_cv["nume"], "raportz", "#z-salveaza")
    pg.fill("#z-data", AZI.isoformat())
    pg.fill("#z-nui", "8000000096")
    pg.fill("#z-nr", "0096")
    pg.fill("#z-21", "121")
    pg.fill("#z-num", "121")
    pg.fill("#z-bonuri", "3")
    pg.click("#z-salveaza")
    pg.wait_for_function("() => (document.querySelector('#z-rezultat') || {innerText: ''}).innerText.includes('Nota e ciornă')", timeout=15000)
    nid = int(pg.inner_text("#z-rezultat").split("#")[1].split(")")[0])
    pg.wait_for_function("() => (document.querySelector('#z-descarcare') || {innerText: ''}).innerText.includes('Nedescărcat')", timeout=15000)
    patron.captura("z")
    _deschide(patron, firma_cv["nume"], "jurnal", "#j-nota-noua")
    pg.click("[data-val='%d']" % nid)
    pg.wait_for_function("() => (document.querySelector('#j-mesaj') || {innerText: ''}).innerText.includes('nu se validează fără descărcarea')",
                         timeout=15000)
    pg.locator("#j-mesaj").scroll_into_view_if_needed()
    patron.captura("refuz")
    assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % firma_cv["schema"], (nid,)) == [("ciorna",)]


# ================================================================ 97 — salariații la import
def _cnp(baza12):
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    c = sum(int(baza12[i]) * ch[i] for i in range(12)) % 11
    return baza12 + str(1 if c == 10 else c)


def test_def_97_importul_cere_norma_functia_de_baza_si_scutirea(patron, firma_gv):
    """97. Salariați: prin API/import trebuie cerute funcția de bază, scutirea și norma.
    Pașii: firma -> Import date -> Salariați -> încarcă un fișier fără coloanele „norma”, „functie de baza”, „scutit contributie
    minima”. Previzualizarea arată „—” la ele, rândul e refuzat cu motivul numit (norma, funcția de bază, scutirea) și
    „Salvează salariații” e inactiv; nimic nu se scrie."""
    pg = patron.pg
    cnp = _cnp("185071541001")
    csv = ("nume,prenume,cnp,data angajare,brut,judet,cor\nPopescu,Ana,%s,2025-01-15,5000,B,251401\n" % cnp).encode("utf-8")
    _deschide(patron, firma_gv["nume"], "import", ".mig-frand")
    pg.locator(".mig-frand", has_text="Salariați").first.click()
    pg.wait_for_selector("#mig-file", state="attached", timeout=10000)
    pg.set_input_files("#mig-file", files=[{"name": "salariati_proba.csv", "mimeType": "text/csv", "buffer": csv}])
    pg.wait_for_selector("#mig-salveaza-sal", timeout=15000)
    t = patron.fereastra()
    assert "funcție de bază: —" in t and "scutit minim: —" in t, t[:800]
    assert "norma de lucru lipsește" in t and "funcția de bază (Da/Nu) lipsește" in t and "scutirea de contribuția minimă" in t, t[:1500]
    assert pg.is_disabled("#mig-salveaza-sal")
    patron.captura()
    assert sql('SELECT count(*) FROM "%s".salariati' % firma_gv["schema"])[0][0] == 0


# ================================================================ 98 — seria chitanțelor
def test_def_98_seria_chitantei_nu_vine_ch_din_oficiu(patron, firma_gv):
    """98. Chitanțe: seria venea din oficiu „CH”.
    Pașii: firma exceptată de la casa de marcat, fără serie de chitanțe -> Casă -> „+ Chitanță fără factură” -> 100 lei, 21% ->
    Emite: refuz „firma n-are serie pentru chitanțe … scrie-o în Date firmă” (OMFP 2634/2015 anexa 1 pct.24), nicio chitanță
    „CH” emisă; în Date firmă, „Seria chitanțelor” e goală."""
    from core import db, firma_profil_api
    uid = _uid("patron@prisma-cont.test")[0]
    with db.get_conn(firma_gv["schema"]) as c:
        r = firma_profil_api.salveaza_date(c, {"activitate_exceptata_amef": "1", "activitate_amef": "a"}, firma_gv["tenant_id"], uid)
        assert r.get("ok", True) is not False, r
        c.commit()
    assert sql('SELECT serie_chitanta FROM "%s".firma_profil' % firma_gv["schema"]) == [(None,)]
    pg = patron.pg
    _deschide(patron, firma_gv["nume"], "casa", "#c-chit-toggle")
    pg.click("#c-chit-toggle")
    pg.fill("#ch-data", AZI.isoformat())
    pg.fill("#ch-suma", "100")
    pg.select_option("#ch-cota", "21")
    pg.fill("#ch-client", "Client Chitanta Proba")
    pg.click("#ch-emite")
    pg.wait_for_function("() => (document.querySelector('#ch-mesaj') || {innerText: ''}).innerText.trim() !== ''", timeout=15000)
    msg = pg.inner_text("#ch-mesaj")
    patron.captura("refuz")
    assert "n-are serie pentru chitanțe" in msg and "Date firmă" in msg, msg
    assert sql('SELECT count(*) FROM "%s".chitante' % firma_gv["schema"])[0][0] == 0
    _deschide(patron, firma_gv["nume"], "datefirma", "#df-serie_chitanta")
    assert pg.input_value("#df-serie_chitanta") == ""
    patron.captura("date_firma")


# ================================================================ 90, 81 — nota de salarii la validare / respinsă
@pytest.fixture(scope="module")
def salariat_gv(firma_gv):
    """Un salariat al firmei sintetice, creat pe drumul aplicației (`salariati_api.creeaza_salariat`), CNP cu cifra de control."""
    from core import db, salariati_api
    with db.get_conn(firma_gv["schema"]) as c:
        r = salariati_api.creeaza_salariat(c, nume="Ionescu", prenume="Radu", cnp=_cnp("185071541002"), data_angajare="2026-09-01",
                                           tip_norma="intreaga", ore_zi=8, salariu_brut=5000, cor="251401", functie_baza=True,
                                           scutit_contrib_minim=False, judet_casa="B")
        c.commit()
    return r


def _contabilizeaza_statul(ecran, firma):
    pg = ecran.pg
    _deschide(ecran, firma["nume"], "salariati", "#sp-contare")
    pg.click("#sp-contare")
    try:
        pg.wait_for_selector("#sp-contare-scrie", timeout=30000)
    except Exception:
        ecran.captura("propunerea")
        raise AssertionError("propunerea notei de salarii: %s" % pg.inner_text("#sp-contare-zona")[:600])


def test_def_90_confirmarea_notei_la_validare_e_vizibila(asistent, firma_gv, salariat_gv, asistent_pregatitor):
    """90. Coadă: confirmarea „Nota #3 e la validare” mică și gri.
    Pașii: asistentul -> firma -> Salariați -> „Contabilizează statul” -> „Scrie nota ciornă”. Confirmarea „Nota #N e la validare
    în cabinet.” apare într-o casetă informativă (DS cap.5), nu ca text mic gri."""
    pg = asistent.pg
    _contabilizeaza_statul(asistent, firma_gv)
    pg.click("#sp-contare-scrie")
    pg.wait_for_function("() => (document.querySelector('#sp-contare-zona') || {innerText: ''}).innerText.includes('e la validare în cabinet')",
                         timeout=30000)
    el = pg.locator("#sp-contare-zona .ci-mesaj", has_text="e la validare în cabinet").first
    cutie = el.evaluate("e => e.closest('.caseta-info') ? 'caseta-info' : e.parentElement.className")
    asistent.captura()
    assert cutie == "caseta-info", cutie


def test_def_81_nota_de_salarii_respinsa_se_reface_din_stat(asistent, patron, firma_gv, salariat_gv, asistent_pregatitor):
    """81. Salarii: nota respinsă o trimitea pe Ana în Registrul jurnal; recontabilizarea n-o refăcea.
    Pașii: cabinetul respinge nota de salarii („lipsește pontajul”) -> asistentul deschide Salariați: statul spune că nota se
    corectează din statul de plată, nu din Registrul-jurnal -> „Contabilizează statul” › „Recontabilizează statul” (confirmă
    „Retrimite fără schimbări”) -> „Nota respinsă #a a fost înlocuită cu nota #b … și trimisă la validare”; noua notă e la validare."""
    from core import coada_api, db
    s = firma_gv["schema"]
    if not sql("SELECT 1 FROM public.declaratii_coada WHERE tenant_id = %s AND fel = 'nota' AND stare = 'la_senior'",
               (firma_gv["tenant_id"],)):
        _contabilizeaza_statul(asistent, firma_gv)
        asistent.pg.click("#sp-contare-scrie")
        asistent.pg.wait_for_function("() => (document.querySelector('#sp-contare-zona') || {innerText: ''}).innerText.includes('e la validare')",
                                      timeout=30000)
    nota = sql('SELECT id FROM "%s".inregistrari WHERE sursa = \'salarii\' AND status = \'ciorna\' ORDER BY id DESC LIMIT 1' % s)[0][0]
    cid = sql("SELECT id FROM public.declaratii_coada WHERE tenant_id = %s AND fel = 'nota' AND perioada = %s AND stare = 'la_senior'",
              (firma_gv["tenant_id"], "nota-%d" % nota))[0][0]
    puid = _uid("patron@prisma-cont.test")[0]
    with db.get_conn() as c:
        r = coada_api.respinge(c, cid, "patron", "lipsește pontajul", respins_de_id=puid, cabinet_id_apelant=firma_gv["cabinet_id"],
                               schema_nota=s)
        c.commit()
    assert r.get("ok", True) is not False, r
    pg = asistent.pg
    _deschide(asistent, firma_gv["nume"], "salariati", "#sp-contare")
    pg.wait_for_function("() => (document.querySelector('#sp-contare-zona') || {innerText: ''}).innerText.includes('nu din Registrul-jurnal')",
                         timeout=15000)
    assert "lipsește pontajul" in pg.inner_text("#sp-contare-zona")
    asistent.captura("respinsa")
    pg.click("#sp-contare")
    pg.wait_for_selector("#sp-contare-scrie", timeout=30000)
    assert pg.inner_text("#sp-contare-scrie").strip() == "Recontabilizează statul"
    pg.click("#sp-contare-scrie")
    pg.wait_for_selector("#ca-ok", timeout=15000)
    pg.click("#ca-ok")
    pg.wait_for_function("() => (document.querySelector('#sp-contare-zona') || {innerText: ''}).innerText.includes('a fost înlocuită cu nota')",
                         timeout=30000)
    asistent.captura("refacuta")
    noua = sql('SELECT id FROM "%s".inregistrari WHERE sursa = \'salarii\' AND status = \'ciorna\' ORDER BY id DESC LIMIT 1' % s)[0][0]
    assert noua != nota
    assert sql("SELECT stare FROM public.declaratii_coada WHERE tenant_id = %s AND perioada = %s ORDER BY id DESC LIMIT 1",
               (firma_gv["tenant_id"], "nota-%d" % noua)) == [("la_senior",)]


# ================================================================ 93 — clopoțelul de la cabinet
def test_def_93_cifra_clopotelului_nu_acopera_gliful(patron, firma_gv, asistent_pregatitor):
    """93. Antet: la cabinet, clopoțelul doar ca cifră.
    Pașii: asistentul pregătește un NIR (notificare „de validat” pentru cabinet) -> contabilul-șef deschide aplicația: în antet
    se vede CLOPOȚELUL, cu cifra în colțul butonului, în afara glifului (cifra acoperă sub 10% din clopoțel), nu o cifră pusă
    peste el."""
    asist = _uid("asistent@prisma-cont.test")[0]
    _nir(firma_gv, {"numar": "GV-93", "data": AZI.isoformat(), "furnizor": "Furnizor Clopot 93 SRL", "transport": 0, "taxe": 0,
                    "linii": [_linie_gv("Marfa Clopot 93")]}, uid=asist)
    pg = patron.pg
    patron.acasa()
    pg.wait_for_function("() => (document.querySelector('#nav-clopot-badge') || {textContent: ''}).textContent.trim() !== ''",
                         timeout=15000)
    g = pg.locator("#nav-clopot svg").bounding_box()
    b = pg.locator("#nav-clopot-badge").bounding_box()
    ix = max(0, min(g["x"] + g["width"], b["x"] + b["width"]) - max(g["x"], b["x"]))
    iy = max(0, min(g["y"] + g["height"], b["y"] + b["height"]) - max(g["y"], b["y"]))
    acoperit = ix * iy / (g["width"] * g["height"])
    pg.locator("#nav-clopot").screenshot(path=os.path.join(CAPTURI, "93_cifra_clopotelului_nu_acopera_gliful_zoom.png"))
    patron.captura()
    assert pg.is_visible("#nav-clopot svg")
    assert acoperit < 0.10, "cifra acoperă %.0f%% din clopoțel" % (acoperit * 100)


# ================================================================ 73, 74 — declarațiile în coadă
def _curata_coada(tenant_id, peste_id):
    """Elementele de coadă puse de test pe o firmă de test comună (și notificările lor) se scot în același test."""
    ids = [r[0] for r in sql("SELECT id FROM public.declaratii_coada WHERE tenant_id = %s AND id > %s", (tenant_id, peste_id))]
    for i in ids:
        sql("DELETE FROM public.notificari WHERE link = %s", ("validat:%d" % i,))
    sql("DELETE FROM public.declaratii_coada WHERE tenant_id = %s AND id > %s", (tenant_id, peste_id))


def _declaratie_pas1(ecran, firma, tip, an, luna=None, trim=None):
    pg = ecran.pg
    _deschide(ecran, firma, "declaratii", "#dec-tip")
    pg.select_option("#dec-tip", tip)
    pg.wait_for_selector("#dec-an", timeout=10000)
    pg.fill("#dec-an", str(an))
    pg.dispatch_event("#dec-an", "change")
    if luna and pg.locator("#dec-luna").count():
        pg.select_option("#dec-luna", str(luna))
    if trim and pg.locator("#dec-trim").count():
        pg.select_option("#dec-trim", str(trim))
    pg.click("#dec-continua")


def _trimite_si_asteapta(ecran):
    pg = ecran.pg
    pg.wait_for_selector("#dec-trimite, #dec-gol-da", timeout=90000)
    pg.click("#dec-trimite" if pg.locator("#dec-trimite").count() else "#dec-gol-da")
    pg.wait_for_function("() => document.body.innerText.includes('Trimisă în coada de validare') || "
                         "(document.querySelector('#dec-coada-mesaj') || {innerText: ''}).innerText.trim() !== ''", timeout=90000)


def test_def_73_d390_intra_in_coada_fara_eroare_500(patron):
    """73. D390: eroare 500, nu intra în coadă.
    Pașii: „Distributie Profit IC” (achiziție intracomunitară din DE în 08/2026) -> Declarații -> D390, august 2026 -> Continuă
    -> „Trimite în coadă →”: declarația intră în coadă („Trimisă în coada de validare”), fără nicio cerere 5xx (înainte:
    `POST /coada` = 500 la copierea avertismentelor cu locul facturii)."""
    tid = 4839
    peste = sql("SELECT COALESCE(max(id), 0) FROM public.declaratii_coada")[0][0]
    try:
        _declaratie_pas1(patron, "Distributie Profit IC", "d390", 2026, luna=8)
        _trimite_si_asteapta(patron)
        patron.captura()
        t = patron.fereastra()
        assert "Trimisă în coada de validare" in t, t[:1200]
        assert sql("SELECT count(*) FROM public.declaratii_coada WHERE tenant_id = %s AND tip = 'd390' AND id > %s",
                   (tid, peste))[0][0] == 1
    finally:
        _curata_coada(tid, peste)


def test_def_74_declaratia_cu_formular_manual_intra_in_coada(patron):
    """74. Declarații: cele cu formular completat de mână nu se trimiteau în coadă.
    Pașii: „Comert Micro TVA” -> Declarații -> D710 (rectificativa D100) -> Continuă -> în formular: impozit micro (121), declarat
    inițial 100, corect 150, cotă 1% -> „+ adaugă” -> „Regenerează D710” -> „Trimite în coadă →”: D710 intră în coadă cu
    obligația scrisă de mână (înainte: refuz „nu are ce genera”, pasul 3 nu trimitea formularul)."""
    tid = 4838
    peste = sql("SELECT COALESCE(max(id), 0) FROM public.declaratii_coada")[0][0]
    pg = patron.pg
    try:
        _declaratie_pas1(patron, "Comert Micro TVA", "d710", 2026, luna=9, trim=3)
        pg.wait_for_selector("#d710-cod", timeout=60000)
        pg.select_option("#d710-cod", "121")
        pg.fill("#d710-i", "100")
        pg.fill("#d710-c", "150")
        pg.fill("#d710-cota", "1")
        pg.click("#d710-add")
        pg.click("#d710-regen")
        _trimite_si_asteapta(patron)
        patron.captura()
        t = patron.fereastra()
        assert "Trimisă în coada de validare" in t, t[:1200]
        r = sql("SELECT payload->>'xml' FROM public.declaratii_coada WHERE tenant_id = %s AND tip = 'd710' AND id > %s", (tid, peste))
        assert len(r) == 1 and "150" in (r[0][0] or ""), r
    finally:
        _curata_coada(tid, peste)


# ================================================================ 95 — NIR legat de factura primită (global-valoric)
def test_def_95_nir_legat_de_factura_scrie_doar_adaosul_si_tva_neexigibila(patron, firma_gv):
    """95. NIR: la global-valoric, NIR legat de factură scrie doar adaosul și TVA neexigibilă.
    Pașii: firma global-valorică are factura primită FP-95 (10 buc × 5,00 lei + TVA 21%, contată pe 371/4426 = 401) -> Stocuri ->
    + NIR nou -> „Factura primită a recepției”: FP-95 -> 10 × 5,00, raft 9,68 cu TVA -> Salvează. NIR-ul legat scrie NUMAI adaosul
    (371 = 378) și TVA neexigibilă (371 = 4428.02) — costul e deja în factură; mesajul spune „legat de factura … Costul (50,00 lei)
    e în factură” (OMFP 1802/2014 pct.287)."""
    from core import db, facturi_api
    s = firma_gv["schema"]
    with db.get_conn(s) as c:
        f = facturi_api.creeaza_factura(c, "FP-95", AZI.isoformat(), "primita",
                                        [{"descriere": "Marfa Legata 95", "cantitate": 10, "pret_unitar": 5, "cota_tva": 21, "um": "buc"}],
                                        tert_nume="Furnizor Factura 95 SRL", tert_cui=cui_cu_control(33000000))
        c.commit()
    assert f.get("id") or f.get("factura_id"), f
    pg = patron.pg
    _formular_nir(patron, firma_gv["nume"])
    pg.fill("#sn-numar", "GV-95")
    opt = pg.locator("#sn-factura option", has_text="FP-95").first
    pg.select_option("#sn-factura", opt.get_attribute("value"))
    pg.fill("#nir-l0-denumire", "Marfa Legata 95")
    pg.fill("#nir-l0-cantitate", "10")
    pg.fill("#nir-l0-pret_achizitie", "5")
    pg.fill("#nir-l0-pret_vanzare", "9.68")
    pg.select_option("#nir-l0-cota_tva", "21")
    pg.click("#sn-salveaza")
    pg.wait_for_function("() => (document.querySelector('#s-mesaj') || {innerText: ''}).innerText.includes('NIR salvat')", timeout=20000)
    msg = pg.inner_text("#s-mesaj")
    patron.captura()
    assert "legat de factura" in msg and "Costul (50,00 lei) e în factură" in msg, msg
    note = sql('SELECT l.cont_debit, l.cont_credit FROM "%s".nir n JOIN "%s".inregistrari_linii l ON '
               "n.inregistrari_ids @> to_jsonb(l.inregistrare_id) WHERE n.numar = 'GV-95'" % (s, s))
    assert sorted(note) == [("371", "378"), ("371", "4428.02")], note
