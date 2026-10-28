# -*- coding: utf-8 -*-
"""[lotul 11, W4] Decizia Costin 10.3, verbatim în DECIZII „Comanda 10.3” pct.4: „Totalurile și rezumatul fix, mesajele lângă buton, 394
la 1280×720: da, reorganizezi ecranele; totul încape într-un ecran, fără derulare.” Răspunsul la patru întrebări din raportul lotului 10
(§6; consemnate în DECIZII „Lotul 10: integrarea” — „Rezumatul fix (421, clasa, Z)” și „394” din „comanda 10.2”, plus excepțiile „de decis
de Costin” din verificator, `rezumat_exceptii`):
  1. totalurile de sub tabel (Cartea mare, Jurnal regim marjă, Registrul fiscal …) rămân sub tabel sau se fixează?  -> se fixează;
  2. rezumatul fix pe Tipare, Înregistrare (cererile neconfirmate) și Stocuri, unde cere mutarea unor blocuri?        -> da;
  3. mesajele lângă butonul care le produce (Stocuri `#s-mesaj`, Înregistrare `#ins-cereri-msg`, sub tabel)?          -> da;
  4. 394 la 1280×720 (8 px de derulare la „Notă nouă” în partidă simplă; Migrare cabinet nemăsurat la 1280×720)?      -> fără derulare.

Ecranele REALE (`firme.js`, `migrare.js`, `admin.js`, `tipare.js`, `navigator.js`, `stil.css` din arbore), în Chromium headless, cu rutele
simulate (se măsoară așezarea, nu scrierea), la 1280×720 și 1366×768. Ce face imposibil:
  - 394: fereastra „Notă nouă” (Registru jurnal, partidă simplă și dublă, luna în curs = cazul cel mai înalt) și „Migrare cabinet” (fără
    aplicație, cu SAGA aleasă, cu confirmarea unui pas, cu „Cum se face” deschis) derulează vertical;
  - un total (rândul `tfoot` sau caseta `.fd-totaluri`) care nu se vede — sau stă sub bara de jos — cât tabelul de 40 de rânduri e la
    început sau la mijloc (Balanța, Cartea mare, Jurnal regim marjă, Registrul-inventar, Rapoarte comerciale, Registru jurnal, Stocuri,
    Registrul de evidență fiscală PF);
  - rezumatul care nu mai stă lipit sus după derulare (Stocuri, Registru jurnal, Tipare, Înregistrare) și mesajul unui buton din rezumat
    care apare departe de el (Stocuri „Descarcă gestiunea lunii”, Tipare „Generează analiză AI”, Înregistrare „Retrimite confirmarea”).
Mutațiile (raportul W4 §3): grila notei scoasă; rândul pașilor la loc (3 px); panoul „Cum se face” fără `position: absolute`; bara scoasă
de pe totalurile Cărții mari; `--bara-h` scos din navigator; `s-mesaj` mutat la loc sub situația stocului -> ROȘU.

Temei: N/A — regulă de UI (DS cap.9 v2.100, „Fereastra cu tabel” pct.7–8; cap.9 v2.95 „Lista de pași”, 394).
"""
import datetime
import functools
import http.server
import json
import urllib.parse
import os
import socketserver
import threading

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ECRANE = [(1280, 720), (1366, 768)]
N = 40   # rânduri: tabelul derulează la ambele mărimi

PAGINA = """<!doctype html><html lang="ro"><head><meta charset="utf-8"><link rel="stylesheet" href="/static/stil.css"></head>
<body><div id="app"></div><div id="desk"></div><script type="module">
sessionStorage.setItem("iconta_user", JSON.stringify({rol: "admin_firma", nume: "Probă", bun_venit_vazut: true}));
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


def _pagina(browser, lat, inalt, rute):
    b, port = browser
    pg = b.new_page(viewport={"width": lat, "height": inalt})
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))

    def raspuns(route):
        u = route.request.url
        if urllib.parse.urlsplit(u).path.startswith("/static/"):   # calea cererii, nu un sub-șir al URL-ului (core/test_garzi_pe_text.py)
            return route.continue_()
        cale = u.split("?")[0]
        for k in sorted(rute, key=len, reverse=True):      # ruta cea mai lungă câștigă (`/jurnal-marja` înaintea lui `/jurnal`)
            if cale.endswith(k) or (k + "/") in cale:
                return route.fulfill(status=200, content_type="application/json", body=json.dumps(rute[k]))
        return route.fulfill(status=200, content_type="application/json", body="{}")
    pg.route("**/harness.html", lambda r: r.fulfill(status=200, content_type="text/html", body=PAGINA))
    for pref in ("/tenants", "/migrare/", "/auth/", "/notificari", "/versiune", "/eu/", "/admin/", "/tipare", "/cabinet/"):
        pg.route("**%s**" % pref, raspuns)
    pg.goto("http://127.0.0.1:%d/harness.html" % port)
    pg.wait_for_function("() => window._gata === true", timeout=20000)
    return pg, erori


# ── datele (40 de rânduri pe fiecare tabel) ────────────────────────────────────────────────────────────────────────────────────
def _nota(i, status="validata"):
    return {"id": 1000 + i, "nr_curent": i, "data": "2026-09-%02d" % (i % 28 + 1), "numar": None, "descriere": "Notă de probă %d" % i,
            "sursa": "manual", "status": status, "factura_id": None, "document_ref": "Extras %d" % i, "document": "Extras %d" % i,
            "linii": [{"debit": "627", "credit": "5121", "suma": 12.5 + i}]}


_COL = ["si_d", "si_c", "prec_d", "prec_c", "rul_d", "rul_c", "tot_d", "tot_c", "sf_d", "sf_c"]
DATE = {
    "/balanta": {"randuri": [dict(cont="%d" % (4000 + i), denumire="Cont %d" % i, **{k: 1000 + i for k in _COL}) for i in range(N)],
                 "totaluri": {k: 99999 for k in _COL}, "note_lunii": 3, "ciorne": {}, "inchidere": None},
    "/fisa-cont": {"conturi": ["5121"], "formular": "14-6-22", "fisa": {
        "randuri": [dict(data="2026-09-%02d" % (i % 28 + 1), document="Doc %d" % i, explicatie="Plată %d" % i, cont_corespondent="401",
                         debit=10, credit=0, sold=10 * i, sens_sold="D", jurnal="J") for i in range(N)],
        "sold_initial_declarat": True, "sold_initial": 100, "total_debit": 400, "total_credit": 0, "sold_final": 500, "sens_sold_final": "D",
        "temei_completitudine": "x"}},
    "/registru-inventar": {"randuri": [dict(nr_curent=i, cont="371", element="Marfă %d" % i, valoare_contabila=10, valoare_inventar=10,
                                            diferenta=0, cauza=None) for i in range(N)],
                           "total_valoare_contabila": 400, "total_valoare_inventar": 400, "randuri_cu_diferenta": 0, "temei": "t",
                           "temei_obligatie": "t", "temei_completitudine": "t"},
    "/rapoarte-comerciale": {"parteneri": [], "vanzari": {"parteneri": [dict(nume="Client %d" % i, cui="1%d" % i, nr=2, net=100) for i in range(N)],
                                                          "total_net": 4000}, "durata_incasare": {}, "profit_produs": []},
    "/rapoarte-salvate": {"variante": []},
    "/jurnal-marja": {"note": [dict(data="2026-09-01", eticheta="N%d" % i, descriere="v", status="validata", cost=1, marja_neta=1, tva=1)
                               for i in range(N)], "numar_note": N, "total_cost": 40, "total_baza_marja_neta": 40, "total_tva_colectata": 8},
    "/jurnal": {"note": [_nota(i) for i in range(N)], "total_debit": 500, "total_credit": 500, "ciorne": {"note": 0, "total": 0}},
    "/centre-cost": {"centre": []},
    "/registru-evidenta-fiscala": {"temei": "t", "temei_completitudine": "t", "corp": {"sectiuni": []}, "sectiuni": [
        {"categorie": 1, "categorie_eticheta": "Cedarea folosinței bunurilor", "sursa": "Apartament", "total_venit_brut": 40000,
         "total_cheltuieli": 0, "venit_net": 40000,
         "randuri": [dict(nr_crt=i, venit_brut=1000, cheltuieli_deductibile=0, venit_net=1000, rectificare=False) for i in range(N)]}]},
    "/ajustari-fiscale": {"ajustari": [], "randuri": [], "din_conturi": []},
    "/stocuri/nir": {"nir": []},
    "/firma-profil/date": {"profil": {"metoda_stoc": "cantitativ_valoric"}},
    "/stocuri/articole": {"articole": [dict(id=i, denumire="Marfa %02d" % i, um="buc", stoc=10, cmp=2.5, valoare=25) for i in range(N)],
                          "retete_vizibile": False},
    "/stocuri/locatii": {"locatii": []},
    "/stocuri/descarcare": {"mesaj": "Nimic de descărcat pe luna asta: nicio ieșire din stoc."},
}
FIRMA = "{id: 1, nume: 'Firma Probă SRL', cui: '1', regim_contabil: 'dubla', tip_firma: 'srl', platitor_tva: true}"

#: ecranul -> (cardul din fereastra firmei, selectorul totalului, pasul de după deschidere)
TOTALURI = {
    "balanta": ("#fa-balanta", "tfoot td:last-child", None),
    "cartea_mare": ("#fa-fisacont", ".bara-fixa .fd-totaluri", None),
    "jurnal_marja": ("#fa-marja", ".bara-fixa .fd-totaluri", None),
    "registru_inventar": ("#fa-reginventar", "tfoot td:nth-child(2)", None),
    "rapoarte": ("#fa-rapoarte", "tfoot td:last-child", None),
    "registru_jurnal": ("#fa-jurnal", ".bara-fixa .fd-totaluri", None),
    "registru_fiscal_pf": ("#fa-regfiscal", "tfoot td:nth-child(2)", "venituri_pf"),
    "stocuri": ("#fa-stocuri", "#s-situatie-tabel tfoot td:last-child", None),
}

_VEDE = """(sel) => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(), rc = c.getBoundingClientRect();
  const t = c.querySelector(sel); if (!t) return null;
  const r = t.getBoundingClientRect(), x = r.left + Math.min(20, r.width / 2), y = r.top + r.height / 2, el = document.elementFromPoint(x, y);
  return {in_corp: r.top >= rc.top - 1 && r.bottom <= rc.bottom + 1, vizibil: !!(el && t.contains(el)), sus: Math.round(r.top - rc.top)}; }"""


def _deschide_firma(pg, card):
    pg.evaluate("async () => { const f = await import('/static/js/ecrane/firme.js'); f.deschideFirma(%s, window._nav); }" % FIRMA)
    pg.wait_for_selector(card, timeout=15000)
    pg.click(card)


# ── 4. 394 la 1280×720 ──────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("lat, inalt", ECRANE)
@pytest.mark.parametrize("regim", ["simpla", "dubla"])
def test_def_394_nota_noua_nu_deruleaza(browser, lat, inalt, regim):
    """ROȘU înainte: 1280×720, partidă simplă, luna în curs (rândul „notele sunt interne” + motivul amortizării): 621 px de conținut
    într-un corp de 613 (8 px de derulare). Acum data, descrierea și documentul stau pe un rând (`.grila-campuri`)."""
    azi = datetime.date.today()
    pg, erori = _pagina(browser, lat, inalt, {"/jurnal": {"note": [_nota(i, "ciorna") for i in range(8)], "total_debit": 0,
                                                          "total_credit": 0, "ciorne": {"note": 8, "total": 100}},
                                              "/centre-cost": {"centre": []}})
    try:
        pg.evaluate("""async ([an, luna, regim]) => { const f = await import('/static/js/ecrane/firme.js');
          window._nav.deschide('Registru jurnal', (c, n) => f.ecranJurnal(c, n, {id: 1, nume: 'Firma', regim_contabil: regim}, {an, luna}),
                               {lat: 'tabel'}); }""", [azi.year, azi.month, regim])
        pg.wait_for_selector("#j-nota-noua", timeout=15000)
        pg.click("#j-nota-noua")
        pg.wait_for_selector("#je-salveaza", timeout=5000)
        pg.wait_for_timeout(200)
        m = pg.evaluate("""() => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(), s = document.querySelector('#je-salveaza');
          return {sh: c.scrollHeight, ch: c.clientHeight, jos_s: s.getBoundingClientRect().bottom, jos_c: c.getBoundingClientRect().bottom}; }""")
    finally:
        pg.close()
    assert not erori, erori
    # 10.3: „394 la 1280×720 […] totul încape într-un ecran, fără derulare”
    assert m["sh"] <= m["ch"] + 1 and m["jos_s"] <= m["jos_c"], (lat, inalt, regim, m)


_MESAJ_PAS = """() => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(); const z = document.createElement('div');
  z.style.margin = '0 0 6px'; c.insertBefore(z, c.firstChild);
  z.className = 'msg-ok'; z.textContent = 'Pasul „Solduri inițiale” e marcat gata: iConta.eu nu-l mai arată ca de continuat.'; }"""


@pytest.mark.parametrize("lat, inalt", ECRANE)
@pytest.mark.parametrize("stare", ["fara_aplicatie", "saga", "saga_cu_confirmare", "saga_cum_se_face"])
def test_def_394_migrare_cabinet_nu_deruleaza(browser, lat, inalt, stare):
    """ROȘU înainte, la 1280×720: 4 px de derulare fără aplicație, 92 px cu SAGA aleasă, 326 px cu „Cum se face” deschis. Confirmarea
    unui pas (`_consumaMigMesaj`, privată în modul) e pusă cum o pune funcția: primul copil al corpului, cu marginea ei."""
    from core import aplicatii_migrare
    pg, erori = _pagina(browser, lat, inalt, {"/migrare/status": {"status": {}}, "/migrare/aplicatii": {"aplicatii": aplicatii_migrare.registru()},
                                              "/tenants": {"tenants": [{"id": 1}]}})
    try:
        pg.evaluate("""async () => { const m = await import('/static/js/ecrane/migrare.js');
          window._nav.deschide('Migrare cabinet', (c, n) => m.randeazaMigrare(c, n), {nivel: 'cabinet'}); }""")
        pg.wait_for_selector(".mig-op", timeout=15000)
        if stare != "fara_aplicatie":
            pg.click("button[data-aplicatie='saga']")
            pg.wait_for_selector("#mig-apl-aleasa", timeout=5000)
        if stare == "saga_cu_confirmare":
            pg.evaluate(_MESAJ_PAS)
        if stare == "saga_cum_se_face":
            pg.click("#mig-apl-cum > summary")
            pg.wait_for_selector("#mig-apl-text", state="visible", timeout=5000)
        pg.wait_for_timeout(200)
        m = pg.evaluate("""() => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(), rc = c.getBoundingClientRect();
          const pasi = [...c.querySelectorAll('#mig-meniu .mig-op')], t = c.querySelector('#mig-apl-text');
          const rt = t && t.offsetParent ? t.getBoundingClientRect() : null;
          return {sh: c.scrollHeight, ch: c.clientHeight, la_vedere: pasi.filter((x) => x.getBoundingClientRect().bottom <= rc.bottom + 1).length,
                  pasi: pasi.length, h_pas: Math.min(...pasi.map((x) => x.getBoundingClientRect().height)),
                  cum_in_corp: rt ? rt.bottom <= rc.bottom + 1 : null}; }""")
    finally:
        pg.close()
    assert not erori, erori
    # 10.3: „394 la 1280×720 […] totul încape într-un ecran, fără derulare” — cei 12 pași la vedere
    assert m["sh"] <= m["ch"] + 1 and m["la_vedere"] == m["pasi"] == 12, (lat, inalt, stare, m)
    assert m["h_pas"] >= 24, m                      # ținta de atingere a desktopului rămâne (WCAG 2.5.8, interactiune_scan: ≥ 24 px)
    if stare == "saga_cum_se_face":
        assert m["cum_in_corp"], m                  # textul „Cum se face” se citește întreg, în fereastră


# ── 1. totalurile rămân în vedere ────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("lat, inalt", ECRANE)
@pytest.mark.parametrize("ecran", sorted(TOTALURI))
def test_totalul_tabelului_ramane_in_vedere(browser, lat, inalt, ecran):
    """ROȘU înainte: totalul stătea sub tabel — la începutul tabelului de 40 de rânduri, între 900 și 5.000 px sub marginea ferestrei
    (Balanța 914, Cartea mare 1.174, Registru jurnal 5.035 la 1280×720). Acum rândul `tfoot` e lipit jos, deasupra barei, sau caseta
    `.fd-totaluri` stă în `.bara-fixa`."""
    card, sel, varianta = TOTALURI[ecran]
    pg, erori = _pagina(browser, lat, inalt, DATE)
    try:
        _deschide_firma(pg, card)
        if varianta:
            pg.wait_for_selector("#rf-var", timeout=15000)
            pg.select_option("#rf-var", varianta)
        pg.wait_for_selector(sel, timeout=15000)
        pg.wait_for_timeout(300)
        deruleaza = pg.evaluate("() => { const c0 = [...document.querySelectorAll('.fereastra-corp')].pop(), c = c0.querySelector('.zona-derulare') || c0; return c.scrollHeight - c.clientHeight; }")   # [lotul 14, 687] tabelul derulează în zona lui
        vazut = {}
        for loc in ("inceput", "mijloc"):
            pg.evaluate("""(loc) => { const c0 = [...document.querySelectorAll('.fereastra-corp')].pop(), c = c0.querySelector('.zona-derulare') || c0, t = c.querySelector('table, .pf-lista');
              c.scrollTop = loc === 'inceput' ? 0 : Math.max(0, t.offsetTop + t.offsetHeight / 2 - c.clientHeight / 2); }""", loc)
            pg.wait_for_timeout(50)
            vazut[loc] = pg.evaluate(_VEDE, sel)
    finally:
        pg.close()
    assert not erori, erori
    assert deruleaza > 300, (ecran, deruleaza)        # anti-vacuu: tabelul chiar derulează, deci totalul ar fi ieșit din vedere
    # 10.3: „Totalurile […] fix” — totalul se vede (nu e acoperit de bară) și la începutul, și la mijlocul tabelului
    assert all(v and v["in_corp"] and v["vizibil"] for v in vazut.values()), (ecran, lat, inalt, vazut)


def test_consolidarea_portofoliului_tine_totalul_in_vedere(browser):
    """Lista-tabel fără `<table>` (Consolidare portofoliu, `cabinet.js`): rândul „Total” stătea la capătul listei firmelor; cu 40 de firme,
    sub marginea ferestrei. Acum stă în `.bara-fixa` (`#cons-total`)."""
    kpi = {"venituri": 1000, "cheltuieli": 500, "profit": 500, "cash": 100}
    rute = {"/cabinet/consolidare": {"an": 2026, "luna": 9, "firme": [{"nume": "Firma %02d SRL" % i, "kpi": kpi} for i in range(N)],
                                     "total": {"venituri": 40000, "cheltuieli": 20000, "profit": 20000, "cash": 4000}}}
    pg, erori = _pagina(browser, 1280, 720, rute)
    try:
        pg.evaluate("""async () => { const m = await import('/static/js/ecrane/cabinet.js'); m.desktopCabinet(document.querySelector('#desk'), window._nav);
          document.querySelector('.cab-card-sinteza[data-cheie="consolidare"]').closest('button').click(); }""")
        pg.wait_for_function("() => document.body.innerText.includes('Firma 39 SRL')", timeout=15000)
        v = pg.evaluate(_VEDE, "#cons-total")
    finally:
        pg.close()
    assert not erori, erori
    assert v and v["in_corp"] and v["vizibil"], v      # 10.3: „Totalurile […] fix”


# ── 2 + 3. rezumatul lipit sus și mesajul lângă buton ─────────────────────────────────────────────────────────────────────────────
_REZ = """(rezSel) => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(), z = c.querySelector('.zona-derulare') || c;
  const r = c.querySelector(rezSel); if (!r) return null; const sus = () => Math.round(r.getBoundingClientRect().top - c.getBoundingClientRect().top);
  const inainte = sus(); z.scrollTop = z.scrollHeight; c.scrollTop = c.scrollHeight;
  return [inainte, sus(), z === c, c.scrollHeight - c.clientHeight]; }"""
_LANGA = """([btn, msg]) => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(), rc = c.getBoundingClientRect();
  const b = document.querySelector(btn).getBoundingClientRect(), m = document.querySelector(msg).getBoundingClientRect();
  return {in_corp: m.top >= rc.top - 1 && m.bottom <= rc.bottom + 1, distanta: Math.round(Math.max(0, m.top - b.bottom, b.top - m.bottom)),
          text: document.querySelector(msg).innerText.trim().slice(0, 60)}; }"""


def test_stocuri_rezumatul_sus_si_mesajul_descarcarii_langa_buton(browser):
    """ROȘU înainte: luna, „Descarcă gestiunea lunii” și `#s-mesaj` stăteau SUB situația stocului (40 de articole): mesajul descărcării
    apărea la ~1.500 px sub buton; după derulare, luna nu se mai vedea."""
    pg, erori = _pagina(browser, 1280, 720, DATE)
    try:
        _deschide_firma(pg, "#fa-stocuri")
        pg.wait_for_selector("#s-situatie-tabel", timeout=15000)
        # [lotul 12, C198] pe luna în curs „Descarcă gestiunea lunii” e inactiv (cu motivul): descărcarea se probează pe luna trecută
        pg.click("#s-prev")
        pg.wait_for_function("() => { const b = document.querySelector('#s-desc'); return b && !b.disabled; }", timeout=15000)
        pg.wait_for_selector("#s-situatie-tabel", timeout=15000)
        pg.wait_for_timeout(200)
        sus = pg.evaluate(_REZ, "#s-rezumat")
        pg.evaluate("() => { [...document.querySelectorAll('.fereastra-corp')].pop().scrollTop = 0; }")
        pg.click("#s-desc")
        pg.wait_for_selector("#ca-ok", timeout=5000)
        pg.click("#ca-ok")
        pg.wait_for_function("() => (document.querySelector('#s-mesaj') || {}).innerText", timeout=5000)
        langa = pg.evaluate(_LANGA, ["#s-desc", "#s-mesaj"])
    finally:
        pg.close()
    assert not erori, erori
    assert sus is not None and (sus[1] <= 1 or (sus[1] == sus[0] and sus[1] <= 80)), sus   # [lotul 14, 687] lipit sus (sticky) sau nemișcat în partea de sus la derularea zonei/corpului: [înainte, după, corpul e zona, cât derulează corpul]                                # „rezumatul fix”: lipit sus după derularea la capăt
    assert langa["in_corp"] and langa["distanta"] <= 80, langa               # „mesajele lângă buton”


def test_registru_jurnal_rezumatul_ramane_sus(browser):
    pg, erori = _pagina(browser, 1280, 720, DATE)
    try:
        _deschide_firma(pg, "#fa-jurnal")
        pg.wait_for_selector("[data-nota-id]", timeout=15000)
        sus = pg.evaluate(_REZ, "#j-rezumat")
    finally:
        pg.close()
    assert not erori, erori
    assert sus is not None and (sus[1] <= 1 or (sus[1] == sus[0] and sus[1] <= 80)), sus   # [lotul 14, 687] lipit sus (sticky) sau nemișcat în partea de sus la derularea zonei/corpului: [înainte, după, corpul e zona, cât derulează corpul]     # luna, butoanele ei și `#j-mesaj` rămân sus cât derulezi notele (10.3: „rezumatul fix”)


def test_tipare_rezumatul_sus_si_analiza_langa_buton(browser):
    """ROȘU înainte: „Generează analiză AI” și rezultatul lui stăteau sub cele trei tabele; fereastra n-avea rezumat (excepția „de decis de
    Costin” din verificator)."""
    rute = {"/tipare/ai": {"disponibil": True, "analiza": "Motivul cel mai des: CUI greșit al partenerului."},
            "/tipare": {"are_date": True, "motive": [{"motiv": "Motiv %d" % i, "n": i} for i in range(N)],
                        "tipuri": [{"tip": "d300", "respinse": 3, "total": 10, "pct": 30}], "firme": [{"nume": "F%d" % i, "respinse": 1, "total": 2} for i in range(N)]}}
    pg, erori = _pagina(browser, 1280, 720, rute)
    try:
        pg.evaluate("""async () => { const m = await import('/static/js/ecrane/tipare.js');
          window._nav.deschide('Tipare', (c, n) => m.randeazaTipare(c, n), {nivel: 'cabinet'}); }""")
        pg.wait_for_selector("#tip-ai", timeout=15000)
        sus = pg.evaluate(_REZ, ".rezumat-fix")
        pg.evaluate("() => { [...document.querySelectorAll('.fereastra-corp')].pop().scrollTop = 0; }")
        pg.click("#tip-ai")
        pg.wait_for_function("() => (document.querySelector('#tip-ai-rez') || {}).innerText", timeout=5000)
        langa = pg.evaluate(_LANGA, ["#tip-ai", "#tip-ai-rez"])
    finally:
        pg.close()
    assert not erori, erori
    assert sus is not None and (sus[1] <= 1 or (sus[1] == sus[0] and sus[1] <= 80)), sus   # [lotul 14, 687] lipit sus (sticky) sau nemișcat în partea de sus la derularea zonei/corpului: [înainte, după, corpul e zona, cât derulează corpul]
    assert langa["in_corp"] and langa["distanta"] <= 80, langa


def test_inregistrare_confirmarea_retrimiterii_langa_tabel_sus(browser):
    """ROȘU înainte: `#ins-cereri-msg` stătea sub tabelul cererilor; cu 40 de cereri, confirmarea „a plecat din nou” apărea sub ele."""
    cereri = [{"id": i, "creat_la": "2026-10-20T10:00:00", "nume_cabinet": "Cabinet %d" % i, "email": "c%d@exemplu.ro" % i,
               "email_trimis_la": "2026-10-20T10:00:00", "retrimiteri": 0, "expirata": False, "expira_la": "2026-10-23T10:00:00"} for i in range(N)]
    rute = {"/admin/setari/inregistrare": {"mod": "libera", "moduri": [{"mod": "libera", "eticheta": "Liberă"}, {"mod": "invitatie", "eticheta": "Prin invitație"}],
                                           "eticheta": "Liberă", "email_functional": True},
            "/admin/inregistrari-neconfirmate": {"cereri": cereri},
            "/retrimite": {"email": "c20@exemplu.ro", "valabila_ore": 72}}
    pg, erori = _pagina(browser, 1280, 720, rute)
    try:
        pg.evaluate("""async () => { const m = await import('/static/js/ecrane/admin.js'); m.desktopAdmin(document.querySelector('#desk'), window._nav);
          document.querySelector('[data-deschide="inregistrare"]').click(); }""")
        pg.wait_for_selector("[data-retrimite='20']", timeout=15000)
        pg.eval_on_selector("[data-retrimite='20']", "b => b.scrollIntoView({block: 'center'})")
        pg.click("[data-retrimite='20']")
        pg.wait_for_function("() => (document.querySelector('#ins-cereri-msg') || {}).innerText", timeout=5000)
        pg.wait_for_timeout(200)
        m = pg.evaluate("""() => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(), rc = c.getBoundingClientRect();
          const z = document.querySelector('#ins-cereri-msg'), r = z.getBoundingClientRect(), t = document.querySelector('.ins-cereri').getBoundingClientRect();
          return {in_corp: r.top >= rc.top - 1 && r.bottom <= rc.bottom + 1, deasupra_tabelului: r.top <= t.top + 1 || z.classList.contains('rezumat-fix')}; }""")
    finally:
        pg.close()
    assert not erori, erori
    # 10.3: „mesajele lângă buton” — confirmarea se vede fără derulare, în rezumatul tabelului, nu sub cele 40 de cereri
    assert m["in_corp"] and m["deasupra_tabelului"], m
