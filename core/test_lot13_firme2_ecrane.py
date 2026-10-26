# -*- coding: utf-8 -*-
"""[lotul 13, zona firme2] Ecranele din `firme.js` atinse de comanda 13.1, în Chromium, cu rutele simulate (se măsoară ecranul real, nu
scrierea în bază — aceea e a testelor de capăt la capăt din `frontend_test/e2e/e2e_lot13_firme2.py`).

Deficiențele, verbatim din comanda Costin 13.1 (`~/ghid_incoming/comanda_13_1.txt`):
  624: „Clasă: ecrane cu liste | Importuri, audit, casă, bancă la forma din 617/622; observații la clic; respinsele grupate”
  607: „Bancă (F1) | La comisionul bancar apare și «Alege facturile».”
  669: „Soldurile preluate pe parteneri trebuie să apară ca sume de încasat/plătit [...] la potrivirea extrasului bancar.”
  602: „Registru jurnal (F5) | «Document justificativ: nederivat» e termen de programator (clasa 500); data notei noi vine 01.10, nu data
       zilei.”
  563: „[...] Notă nouă: data precompletată 01.10.2026, nu ziua curentă (504); după salvare niciun mesaj, lista sare la început (529).”
  610: „Registru jurnal | La «Validează» pe o notă fără document, refuzul cu motiv apare de două ori”
  605: „Raport Z (F1) | Textul «raportul Z Raport Z nr» [...]; mesajul de confirmare sus, departe de buton (clasa 45).”
  612: „Inventar (F1) | Rândul cu lipsă e înghesuit”
  589: „Plan de conturi | [...] avertismentul apare după salvare; contul nu se poate șterge. Adăugarea manuală doar pentru analitice sub
       sintetic legal.”
  577: „F4 PFA: cardurile au descrieri de SRL — Declarații «D101», Verificări «Echilibru», Registrul de evidență fiscală «Profit · art. 19»”
  673: „[...] deschide o fereastră nouă, centrată”;  675: „[...] același set de butoane, în aceeași ordine; ce nu se aplică stă inactiv, cu
       motivul la trecerea cu mouse-ul”;  676: „Listele scurte (până la 6 opțiuni) nu sunt liste derulante”.

Ecranele REALE (`firme.js`, `tabel_note.js`, `navigator.js`, `api.js`, `stil.css` din arbore), la 1280×720. Mecanismele comune ale clasei
(butonul inactiv cu motiv, butoanele alăturate ale listei scurte, câmpul numeric românesc) sunt ale zonei DS (`api.js`): testul cere
arborele integrat.
Temei: N/A — reguli de interfață (DS cap.1 / cap.2a / cap.9 v2.102–v2.104; CLAUDE.md §9).
"""
import datetime
import functools
import http.server
import json
import os
import socketserver
import threading
import urllib.parse

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAT, INALT = 1280, 720
AZI = datetime.date.today()
T = {"id": 1, "nume": "Probă SRL", "cui": "14399840", "regim_contabil": "dubla", "tip_firma": "srl"}

PAGINA = """<!doctype html><html lang="ro"><head><meta charset="utf-8"><link rel="stylesheet" href="/static/stil.css"></head>
<body><div id="app"></div><script type="module">
sessionStorage.setItem("iconta_user", JSON.stringify({id: 5, rol: "admin_firma", nume: "Probă", bun_venit_vazut: true}));
const m = await import("/static/js/navigator.js");
window._nav = m.creeazaNavigator(document.getElementById("app"), () => {}); window._gata = true;
</script></body></html>"""


class _Tacut(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright
    from core.test_emitere_randuri_dinamice import _lanseaza_chromium
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(_Tacut, directory=RAD))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pw = sync_playwright().start()
    b = _lanseaza_chromium(pw)
    if b is None:
        pw.stop()
        srv.shutdown()
        pytest.fail("GARD headless nu poate rula: chromium indisponibil. NU e skip verde-fals.")
    try:
        yield b, srv.server_address[1]
    finally:
        b.close()
        pw.stop()
        srv.shutdown()


def _pagina(browser, rute, cereri=None, firma=T):
    """`rute`: {sufixul căii: corpul JSON | funcție(metoda, cale, interogare, corp) -> corpul}; firma deschisă în fereastra ei."""
    b, port = browser
    pg = b.new_page(viewport={"width": LAT, "height": INALT})
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))

    def raspuns(route):
        u = urllib.parse.urlsplit(route.request.url)
        if u.path.startswith("/static/"):
            return route.continue_()
        if cereri is not None:
            cereri.append((route.request.method, u.path, route.request.post_data))
        for k in sorted(rute, key=len, reverse=True):
            if u.path.endswith(k):
                v = rute[k]
                if callable(v):
                    v = v(route.request.method, u.path, urllib.parse.parse_qs(u.query), route.request.post_data)
                return route.fulfill(status=200, content_type="application/json", body=json.dumps(v))
        return route.fulfill(status=200, content_type="application/json", body="{}")
    pg.route("**/harness.html", lambda r: r.fulfill(status=200, content_type="text/html", body=PAGINA))
    for pref in ("/tenants", "/migrare/", "/auth/", "/notificari", "/versiune", "/eu/", "/admin/", "/coada", "/public/", "/cabinet/", "/firme/"):
        pg.route("**%s**" % pref, raspuns)
    pg.goto("http://127.0.0.1:%d/harness.html" % port)
    pg.wait_for_function("() => window._gata === true", timeout=20000)
    pg.evaluate("async (t) => { const f = await import('/static/js/ecrane/firme.js'); f.deschideFirma(t, window._nav); }", firma)
    pg.wait_for_selector(".firme-optiune", timeout=20000)
    return pg, erori


def _butoane(pg, sel):
    return pg.eval_on_selector_all(sel, "bs => bs.map((b) => [b.textContent.trim(), b.getAttribute('aria-disabled') === 'true', b.title])")


# ── Casă (624 / 673 / 675 / 676) ──────────────────────────────────────────────────────────────────────────────────────────────────
def _op(i, **x):
    o = {"id": i, "data": AZI.replace(day=1).isoformat(), "tip": "incasare", "categorie": "incasare_client", "document": "DI-%s" % i,
         "partener": "Client %s SRL" % i, "cui": "14399840", "suma": "100.00", "sold": "600.00", "inregistrare_id": 100 + (i or 99),
         "nota_status": "ciorna", "stornata": False, "storno_de": None, "factura": None, "avans": False, "nir": None, "se_leaga": False,
         "alt_modul": False, "chitanta_id": 7, "fara_chitanta": False, "categorie_eticheta": "Încasare client"}
    o.update(x)
    return o


REG_CASA = {"sold_initial": "500", "sold_final": "800", "sold_final_validat": "500", "avertismente": [], "operatiuni": [
    _op(1),
    _op(2, tip="plata", categorie="plata_furnizor", categorie_eticheta="Plată furnizor", chitanta_id=None, se_leaga=True,
        stare_coada="respinsa", motiv_respingere="lipsește documentul"),
    _op(3, tip="plata", categorie="plata_furnizor", categorie_eticheta="Plată furnizor", chitanta_id=None,
        stare_coada="respinsa", motiv_respingere="lipsește documentul"),
    _op(4, nota_status="validata", chitanta_id=None, fara_chitanta=True),
    _op(None, categorie=None, alt_modul=True, document="Raport Z nr 0042", partener="Raport Z", chitanta_id=None,
        categorie_eticheta="notă din raport Z")]}


def test_def_624_casa_tabel_observatii_la_clic_respinsele_grupate(browser):
    """ROȘU înainte: rândurile Casei erau carduri `.pf-frand`, observațiile pe fiecare rând, refuzurile la validare repetate."""
    pg, erori = _pagina(browser, {"/casa/registru": REG_CASA, "/firma-profil/date": {"profil": {}}})
    try:
        pg.click("#fa-casa")
        pg.wait_for_selector("#c-tabel")
        m = pg.evaluate("""() => { const tb = [...document.querySelectorAll('#c-tabel > tbody.tn-nota')];
          return {randuri: tb.length, detalii_vazute: tb.filter((t) => !t.querySelector('.tn-detaliu').hidden).length,
                  expl: document.querySelector('#c-explicatii').innerText}; }""")
        assert m["randuri"] == 5 and m["detalii_vazute"] == 0, m                      # un rând pe operațiune, detaliul închis
        # „respinsele grupate”: același motiv o dată, cu zilele lui (două operațiuni respinse pentru „lipsește documentul”)
        assert m["expl"].count("lipsește documentul") == 1 and "Note respinse la validare (2)" in m["expl"], m["expl"]
        assert "Încasare fără chitanță (1)" in m["expl"] and "Scrisă din alt ecran (1)" in m["expl"], m["expl"]
        # „observații la clic”: clic pe rând -> detaliul (partenerul, documentul, nota, PDF chitanță, Leagă de factură)
        pg.click("tbody[data-op-id='2'] .tn-rand td:nth-child(3)")
        # rândurile detaliului, fiecare întreg (nu un sub-șir din textul lipit): partenerul și refuzul la validare, pe rândul lor
        det = [" ".join(x.split()) for x in pg.inner_text("tbody[data-op-id='2'] .tn-detaliu").split("\n") if x.strip()]
        assert {"Partener: Client 2 SRL · CUI 14399840", "Respinsă la validare: lipsește documentul."} <= set(det), det
        # [675] același set de butoane pe fiecare operațiune, în aceeași ordine; ce nu se aplică stă inactiv, cu motivul
        for oid in ("1", "2", "4"):
            assert [x[0] for x in _butoane(pg, "tbody[data-op-id='%s'] .tn-actiuni button" % oid)] == ["Stornează", "Șterge"]
            assert [x[0] for x in _butoane(pg, "tbody[data-op-id='%s'] .tn-detaliu button" % oid)] == ["PDF chitanță", "Leagă de factură"]
        assert _butoane(pg, "tbody[data-op-id='4'] .tn-actiuni button")[1] == ["Șterge", True, "Nota e validată: operațiunea se stornează, nu se șterge."]
        assert _butoane(pg, "tbody[data-op-id='2'] .tn-detaliu button")[0] == ["PDF chitanță", True, "La plată nu se emite chitanță."]
        assert not erori, erori
    finally:
        pg.close()


def test_def_673_676_dispozitia_noua_in_fereastra_ei_cu_tipul_din_butoane(browser):
    """ROȘU înainte: „+ Dispoziție nouă” desfăcea formularul în pagina Casei; „Tip” era o listă derulantă de cinci opțiuni."""
    pg, erori = _pagina(browser, {"/casa/registru": REG_CASA, "/firma-profil/date": {"profil": {}}})
    try:
        pg.click("#fa-casa")
        pg.wait_for_selector("#c-tabel")
        n = pg.locator(".fereastra").count()
        pg.click("#c-toggle")
        pg.wait_for_selector("#c-campuri")
        assert pg.locator(".fereastra").count() == n and "Dispoziție nouă" in pg.inner_text(".fereastra .fereastra-antet, .fereastra h2")
        assert pg.locator("#c-tabel").count() == 0                                     # fereastra nouă, peste Casă
        assert [x[0] for x in _butoane(pg, ".alegere-butoane:has(+ #c-cat) button")] == [
            "Încasare client (5311=4111)", "Plată furnizor (401=5311)", "Ridicare de la bancă (5311=581)", "Depunere la bancă (581=5311)",
            "Avans spre decontare (542=5311)"]
        pg.click("#c-renunta")
        pg.wait_for_selector("#c-tabel")
        assert not erori, erori
    finally:
        pg.close()


# ── Bancă (624 / 607 / 669 / 673 / 675) ───────────────────────────────────────────────────────────────────────────────────────────
LINII = [
    {"id": 1, "data": AZI.isoformat(), "tip": "plata", "suma": "12.50", "descriere": "Comision administrare cont", "cui_detectat": None,
     "status": "nou", "alocari": {}, "nota_propusa": {"debit": "627", "credit": "5121"}},
    {"id": 2, "data": AZI.isoformat(), "tip": "incasare", "suma": "1500.00", "descriere": "Incasare sold vechi", "cui_detectat": None,
     "status": "nou", "alocari": {"motiv": "niciun CUI găsit în descriere"}, "nota_propusa": None},
    {"id": 3, "data": AZI.isoformat(), "tip": "plata", "suma": "300.00", "descriere": "Plata chirie", "cui_detectat": None, "status": "ignorat",
     "alocari": {}}]
FACT = {"facturi": [{"id": 9, "directie": "emisa", "serie": None, "numar": "Sold la 30.09.2026", "tert_nume": "Client Alfa Test SRL",
                     "tert_cui": "401007106", "sold": "1500.00", "data_emitere": "2026-09-30", "preluata": True}]}


def test_def_624_607_669_banca(browser):
    """ROȘU înainte: liniile erau carduri, cu „Alege facturile” activ și pe comisionul băncii (607), lista facturilor în zona de mesaj."""
    cereri = []
    pg, erori = _pagina(browser, {"/banca/reconciliere": {"linii": LINII}, "/banca/reconciliere/facturi-deschise": FACT,
                                  "/reconciliere/2/conteaza": {"nota": "5121=4111", "inregistrari": [5], "note_etichete": ["5121 = 4111"]}},
                        cereri)
    try:
        pg.click("#fa-banca")
        pg.wait_for_selector("#bk-tabel")
        # [624] liniile de lucru într-un tabel, cele puse deoparte grupate în tabelul lor
        assert pg.locator("#bk-tabel > tbody.tn-nota").count() == 2 and pg.locator("#bk-dp-tabel > tbody.tn-nota").count() == 1
        assert "Linii puse deoparte (1)" in pg.inner_text("#bk-deoparte")
        # [607 / 675] comisionul: „Contează 627=5121” activ, „Alege facturile” inactiv cu motivul
        com = _butoane(pg, "tbody[data-linie-id='1'] .tn-actiuni button")
        assert com[0] == ["Contează 627=5121", False, ""] and com[1][:2] == ["Alege facturile", True] and "operațiune a băncii" in com[1][2], com
        # [669 / 673] „Alege facturile” deschide fereastra lui, cu soldul preluat la migrare
        pg.click("tbody[data-linie-id='2'] [data-alege]")
        pg.wait_for_selector("#bk-pk-tabel")
        # celulele tabelului, fiecare întreagă: rândul soldului preluat la migrare și suma lui
        t = pg.eval_on_selector_all("#bk-pk-tabel td", "els => els.map((e) => e.innerText.replace(/\\s+/g, ' ').trim())")
        assert {"Sold la 30.09.2026 (sold preluat la migrare)", "1.500,00"} <= set(t), t
        pg.check("input[data-fid='9']")
        pg.click("#bk-pk-ok")
        pg.wait_for_selector("#bk-tabel")
        pg.wait_for_function("() => document.querySelector('#bk-mesaj').innerText.includes('creat')", timeout=10000)
        (cerere,) = [c for c in cereri if c[1].endswith("/reconciliere/2/conteaza")]
        assert json.loads(cerere[2]) == {"alocari": [{"factura_id": 9, "suma": "1500.00"}]}, cerere
        assert not erori, erori
    finally:
        pg.close()


# ── Registru jurnal (602 / 563 / 610 / 673 / 675) ─────────────────────────────────────────────────────────────────────────────────
def _jurnal_rute(stare):
    def jurnal(metoda, cale, q, corp):
        if metoda == "POST":
            n = json.loads(corp)
            stare["salvate"].append(n)
            stare["note"].append({"id": 1100, "nr_curent": None, "data": n["data"], "numar": None, "descriere": n["descriere"],
                                  "sursa": "manual", "status": "ciorna", "document_ref": n["document_ref"], "document": n["document_ref"],
                                  "linii": n["linii"]})
            return {"ok": True, "id": 1100}
        return {"note": stare["note"], "total_debit": 0, "total_credit": 0, "ciorne": {"note": 1, "total": 100}}
    return {"/jurnal": jurnal, "/centre-cost": {"centre": []}, "/perioade-blocate": {"blocate": []}}


def test_def_602_563_610_registrul_jurnal(browser):
    """ROȘU înainte: nota nouă venea cu data 1 a lunii, editorul se deschidea în pagină, după salvare lista sărea la început fără rândul
    notei; „Validează” pe nota fără document era `disabled`, fără motiv la trecerea cu mouse-ul."""
    stare = {"salvate": [], "note": [
        {"id": 1002, "nr_curent": None, "data": AZI.replace(day=1).isoformat(), "numar": None, "descriere": "Fără document", "sursa": "manual",
         "status": "ciorna", "document_ref": None, "document": None, "linii": [{"debit": "612", "credit": "401", "suma": 100}]},
        {"id": 1001, "nr_curent": 1, "data": AZI.replace(day=1).isoformat(), "numar": None, "descriere": "Comision", "sursa": "manual",
         "status": "validata", "document_ref": "Extras 1", "document": "Extras 1", "linii": [{"debit": "627", "credit": "5121", "suma": 12.5}]}]}
    pg, erori = _pagina(browser, _jurnal_rute(stare))
    try:
        pg.click("#fa-jurnal")
        pg.wait_for_selector("#jn-tabel")
        # [610 / 675] „Validează” inactiv, cu pasul notei la trecerea cu mouse-ul; „nederivat” nu apare nicăieri (602)
        v = _butoane(pg, "[data-val='1002']")[0]
        assert v[1] and v[2].startswith("Notă fără document justificativ. Scrie referința"), v
        assert "nederivat" not in pg.inner_text("body")
        # [675] nota validată: aceleași butoane, inactive, cu motivul
        assert [x[0] for x in _butoane(pg, "tbody[data-nota-id='1001'] .tn-actiuni button")] == ["Validează", "Trimite la validare"]
        assert all(x[1] for x in _butoane(pg, "tbody[data-nota-id='1001'] button[data-edit], tbody[data-nota-id='1001'] button[data-del]"))
        # [602 / 563 / 673] nota nouă: fereastra ei, data de azi
        pg.click("#j-nota-noua")
        pg.wait_for_selector("#je-data")
        assert pg.input_value("#je-data") == AZI.isoformat() and pg.locator("#jn-tabel").count() == 0
        pg.fill("#je-desc", "Probă 563")
        pg.fill("#je-doc", "PV 9")
        pg.fill(".je-deb", "612")
        pg.fill(".je-cre", "401")
        pg.fill(".je-sum", "123")
        pg.click("#je-salveaza")
        # [563 / 529] după salvare: registrul, cu confirmarea în rezumat și rândul notei evidențiat
        pg.wait_for_selector("tbody[data-nota-id='1100'].val-evidentiat", timeout=10000)
        assert pg.inner_text("#j-mesaj").startswith("Ai salvat nota din %s („Probă 563”)" % AZI.strftime("%d.%m.%Y")), pg.inner_text("#j-mesaj")
        assert stare["salvate"][-1]["data"] == AZI.isoformat()
        assert not erori, erori
    finally:
        pg.close()


# ── Plan de conturi (589 / 675) ───────────────────────────────────────────────────────────────────────────────────────────────────
PLAN = {"conturi": [{"simbol": "4111", "denumire": "Clienți", "sintetic": None, "folosit": True, "in_afara_planului": False,
                     "nu_se_sterge": "apare în note contabile (are rulaj), deci evidența îl folosește"},
                    {"simbol": "731", "denumire": "Test cont nelegal", "sintetic": None, "folosit": False, "in_afara_planului": True,
                     "nu_se_sterge": None}]}


def test_def_589_plan_de_conturi(browser):
    """ROȘU înainte: un sintetic din afara planului legal se trimitea la salvare (avertismentul venea după), „Șterge” lipsea fără motiv."""
    cereri = []
    pg, erori = _pagina(browser, {"/plan-conturi": PLAN}, cereri)
    try:
        pg.click("#fa-planconturi")
        pg.wait_for_selector("#pcf-lista [data-simbol='731']")
        assert _butoane(pg, "[data-simbol='731'] [data-sterge]")[0][:2] == ["Șterge", False]       # 731: fără rulaj -> se șterge
        assert _butoane(pg, "[data-simbol='4111'] [data-sterge]")[0][1:] == [True, "Contul nu se șterge: apare în note contabile (are rulaj), deci evidența îl folosește."]
        pg.fill("#pcf-simbol", "731")
        assert pg.inner_text("#pcf-avert").startswith("Contul 731 e sintetic")                     # înainte de salvare
        pg.fill("#pcf-simbol", "731.01")
        assert "nu e în planul de conturi al normei firmei" in pg.inner_text("#pcf-avert")
        pg.fill("#pcf-denumire", "Analitic sub nelegal")
        pg.click("#pcf-adauga")
        pg.wait_for_selector('.msg-eroare[data-camp="pcf-simbol"]', timeout=5000)
        assert not [c for c in cereri if c[0] == "POST" and c[1].endswith("/plan-conturi")]          # nimic trimis
        pg.fill("#pcf-simbol", "4111.02")
        assert pg.locator("#pcf-avert").count() == 0
        assert not erori, erori
    finally:
        pg.close()


# ── Raport Z (605 / 675) ──────────────────────────────────────────────────────────────────────────────────────────────────────────
RZ = {"rapoarte": [{"id": 77, "data": AZI.isoformat(), "numar": "Z-8000000001-0042", "status": "ciorna", "nui": "8000000001", "nr_bonuri": 3,
                    "incasat": "131.00", "vanzari_fara_tva": "108.26", "iesiri": 0, "fara_marfa": False, "valoare_descarcata": "0",
                    "stergere": {"refuz": None, "cod": None, "confirmare": "Ștergi raportul Z?"}}], "descarcare_pe_articol": True}


def test_def_605_raport_z(browser):
    """ROȘU înainte: rândul Z-ului scria cheia internă („Z-8000000001-0042”), confirmarea notei stătea deasupra butonului, „Validează” lipsea
    pe Z-ul nedescărcat (fără motiv), etichetele „mâncare / alcool” la o firmă de comerț."""
    pg, erori = _pagina(browser, {"/horeca/rapoarte-z": RZ, "/stocuri/articole": {"articole": [], "alimentatie_publica": False}})
    try:
        pg.click("#fa-raportz")
        pg.wait_for_selector("[data-z='77']")
        assert " ".join(pg.inner_text("[data-z='77'] .pf-frand-nume").split()).startswith("Raport Z nr 0042 · casa 8000000001")
        assert "Z-8000000001" not in pg.inner_text("#z-descarcare")
        assert pg.inner_text("#z-et-11") == "Total 11%" and pg.inner_text("#z-et-21") == "Total 21%"
        assert pg.evaluate("() => !!(document.querySelector('#z-salveaza').compareDocumentPosition(document.querySelector('#z-rezultat'))"
                           " & Node.DOCUMENT_POSITION_FOLLOWING)")
        v = _butoane(pg, "#zd-val-77")[0]
        assert v[1] and v[2].startswith("Descarcă întâi marfa vândută"), v
        assert not erori, erori
    finally:
        pg.close()


# ── Inventar (612 / 606 / 673 / 676) ──────────────────────────────────────────────────────────────────────────────────────────────
ARTS = {"articole": [{"id": 1, "denumire": "Marfa cu denumire lungă pentru inventarul de probă, ambalaj de carton", "um": "buc", "stoc": "5",
                      "cmp": "10", "valoare": "50"}], "alimentatie_publica": False, "retete_vizibile": False}


def test_def_612_inventarul_in_fereastra_lui_randul_lipsei_sub_articol(browser):
    """ROȘU înainte: inventarul se desfăcea în pagina Stocurilor, iar încadrarea lipsei stătea lângă denumire, care se rupea pe rânduri."""
    pg, erori = _pagina(browser, {"/stocuri/articole": ARTS, "/stocuri/locatii": {"locatii": []}, "/stocuri/nir": {"nir": []},
                                  "/firma-profil/date": {"profil": {"metoda_stoc": "cantitativ_valoric"}}})
    try:
        pg.click("#fa-stocuri")
        pg.wait_for_selector("#cv-toggle")
        pg.click("#cv-toggle")
        pg.click("#cv-inv")
        pg.wait_for_selector("#cvi-tabel")
        assert pg.locator("#cv-zona").count() == 0                                     # fereastra nouă, peste Stocuri
        pg.fill("#cvi-a1-faptic", "3")
        pg.wait_for_selector("#cvi-a1-lipsa-zona", state="visible")
        g = pg.evaluate("""() => { const n = document.querySelector('#cvi-a1-rand .cvi-denumire'), z = document.querySelector('#cvi-a1-lipsa-zona');
          const lh = parseFloat(getComputedStyle(n).lineHeight) || 20;
          return {randuri: Math.round(n.getBoundingClientRect().height / lh), sub: z.getBoundingClientRect().top >= n.getBoundingClientRect().bottom - 1,
                  butoane: [...z.querySelectorAll('.alegere-butoane button')].map((b) => b.textContent)}; }""")
        assert g["sub"] and g["randuri"] <= 2, g
        assert g["butoane"] == ["lipsă imputabilă", "lipsă neimputabilă", "lipsă justificată (distrusă, pierdută, furată — dovedit)"], g
        assert not erori, erori
    finally:
        pg.close()


# ── PFA (577) ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_577_cardurile_pfa_au_descrieri_de_pfa(browser):
    pfa = dict(T, regim_contabil="simpla", tip_firma="pfa", nume="Probă PFA")
    pg, erori = _pagina(browser, {}, firma=pfa)
    try:
        d = {k: pg.inner_text("#fa-%s .firme-optiune-desc" % k) for k in ("declaratii", "verificari", "regfiscal")}
        assert d == {"declaratii": "D212 (declarația unică), D300, D112 și restul", "verificari": "Trezorerie, TVA, documente pozate",
                     "regfiscal": "Venituri și cheltuieli · persoane fizice · art. 68"}, d
        assert not erori, erori
    finally:
        pg.close()
