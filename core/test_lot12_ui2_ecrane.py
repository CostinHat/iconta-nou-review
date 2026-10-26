# -*- coding: utf-8 -*-
"""[lotul 12, pachetul ui2] Ecranele comenzii 12.2, în Chromium, cu rutele simulate (se măsoară ecranul real, nu scrierea în bază).

Deficiențele, verbatim din comanda Costin 12.2 (`~/ghid_incoming/comanda_12_2.txt`):
  617 (pct.9):  „Registru jurnal: fără căutare. Un câmp (cont, document, partener, sumă, nr. crt.) și filtru de stare; tabel cu un rând pe
                notă, detaliul la clic, explicațiile o singură dată. După «Validează» pagina sare sus fără confirmare.”
  622 (pct.12): „De validat: trei forme diferite, note afișate de două ori. Trei secțiuni cu număr, același tabel ca la 617,
                Validează/Respinge pe rând, căutare.”
  621 (pct.11): „Balanța: casetele de sus ocupă jumătate din fereastră, se văd 2–3 rânduri de tabel; caseta «Importă…» nu are buton spre
                import.”
  459.1 (pct.5): „la schimbarea CUI-ului denumirea adusă de la CUI-ul anterior (DANTE INTERNATIONAL SA) rămâne completată. Tot aici:
                textul «— verifică.» după denumire.”
  628 (pct.15, partea de ecran): „două deschideri consecutive arată liste diferite”.

Ecranele REALE (`firme.js`, `validat.js`, `tabel_note.js`, `navigator.js`, `stil.css` din arbore), la 1280×720. Mutațiile (raportul ui2):
tabelul comun scos din jurnal; `peLoc` scos de la „Validează”; ciornele trimise lăsate în a treia secțiune; caseta rulajelor pusă înapoi în
rezumat; `legaDateAnaf` fără ștergerea denumirii; contorul situației stocului înapoi pe modul -> ROȘU.

Temei: N/A — reguli de interfață (DS cap.9 v2.102 „Tabelul de note” și „Rezumatul nu mănâncă tabelul”; CLAUDE.md §9).
"""
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


def _pagina(browser, rute, cereri=None, lat=LAT, inalt=INALT):
    """`rute`: {sufixul căii: corpul JSON | funcție(metoda, cale, interogare, corp) -> corpul}. `cereri` primește (metoda, cale)."""
    b, port = browser
    pg = b.new_page(viewport={"width": lat, "height": inalt})
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))

    def raspuns(route):
        u = urllib.parse.urlsplit(route.request.url)
        if u.path.startswith("/static/"):
            return route.continue_()
        if cereri is not None:
            cereri.append((route.request.method, u.path))
        for k in sorted(rute, key=len, reverse=True):
            if u.path.endswith(k) or (k + "/") in u.path:
                v = rute[k]
                if callable(v):
                    v = v(route.request.method, u.path, urllib.parse.parse_qs(u.query), route.request.post_data)
                return route.fulfill(status=200, content_type="application/json", body=json.dumps(v))
        return route.fulfill(status=200, content_type="application/json", body="{}")
    pg.route("**/harness.html", lambda r: r.fulfill(status=200, content_type="text/html", body=PAGINA))
    for pref in ("/tenants", "/migrare/", "/auth/", "/notificari", "/versiune", "/eu/", "/admin/", "/coada", "/public/", "/cabinet/"):
        pg.route("**%s**" % pref, raspuns)
    pg.goto("http://127.0.0.1:%d/harness.html" % port)
    pg.wait_for_function("() => window._gata === true", timeout=20000)
    return pg, erori


_CORP = "() => [...document.querySelectorAll('.fereastra-corp')].pop()"
# rândul ales adus la mijlocul ferestrei; întoarce derularea corpului
_LA_MIJLOC = """() => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(), r = c.querySelector("%s");
  c.scrollTop += r.getBoundingClientRect().top - c.getBoundingClientRect().top - c.clientHeight / 2; return c.scrollTop; }"""


# ── datele Registrului jurnal ─────────────────────────────────────────────────────────────────────────────────────────────────────
def _nota(i, status="validata", **x):
    n = {"id": 1000 + i, "nr_curent": i if status == "validata" else None, "data": "2026-09-%02d" % (i % 28 + 1), "numar": None,
         "descriere": "Notă de probă %d" % i, "sursa": "manual", "status": status, "factura_id": None,
         "document_ref": "Extras %d" % i, "document": "Extras %d" % i,
         "linii": [{"debit": "627", "credit": "5121", "suma": 12.5 + i, "partener_nume": None, "partener_cui": None}]}
    n.update(x)
    return n


def _note_jurnal():
    note = [_nota(i) for i in range(1, 31)]
    note[4]["linii"] = [{"debit": "4111", "credit": "704", "suma": 1234.56, "partener_nume": "ALFA SRL", "partener_cui": "14399840"}]
    note += [_nota(31, "ciorna", document=None, document_ref=None, descriere="Comision fără extras"),
             _nota(32, "ciorna", document=None, document_ref=None, descriere="Alt comision fără extras"),
             _nota(33, "ciorna", descriere="Ciornă de validat"),
             _nota(34, "ciorna", descriere="Ciornă respinsă", validare={"stare_coada": "respinsa", "motiv_respingere": "lipsește extrasul"})]
    return note


def _rute_jurnal(stare):
    """Jurnalul lunii; „Validează” trece nota în validată (cu numărul ei curent) — ca serverul."""
    def jurnal(_m, _c, _q, _b):
        note = [dict(n) for n in stare["note"]]
        return {"note": note, "total_debit": 500, "total_credit": 500, "ciorne": {"note": sum(1 for n in note if n["status"] != "validata"),
                                                                                   "total": 10}, "note_fara_document": 2}

    def valideaza(_m, cale, _q, _b):
        nid = int(cale.split("/")[-2])
        for n in stare["note"]:
            if n["id"] == nid:
                n["status"], n["nr_curent"] = "validata", 99
        return {"ok": True}
    return {"/jurnal": jurnal, "/valideaza": valideaza, "/centre-cost": {"centre": []}, "/blocare-luna": {"blocate": []}}


def _deschide_jurnal(pg):
    pg.evaluate("""async () => { const f = await import('/static/js/ecrane/firme.js');
      window._nav.deschide('Registru jurnal', (c, n) => f.ecranJurnal(c, n, {id: 1, nume: 'Firma', regim_contabil: 'dubla'}, {an: 2026, luna: 9}),
                           {lat: 'tabel'}); }""")
    pg.wait_for_selector("table.tn-tabel tbody[data-nota-id]", timeout=15000)
    pg.wait_for_timeout(200)


def test_def_617_jurnal_un_rand_pe_nota_detaliul_la_clic_explicatia_o_data(browser):
    """ROȘU înainte: notele erau carduri `.pf-frand` (liniile, documentul și caseta roșie a notei fără document pe fiecare), fără tabel."""
    stare = {"note": _note_jurnal()}
    pg, erori = _pagina(browser, _rute_jurnal(stare))
    try:
        _deschide_jurnal(pg)
        m = pg.evaluate("""() => { const c = (%s)();
          const tb = [...c.querySelectorAll('table.tn-tabel > tbody[data-nota-id]')];
          return {note: tb.length, randuri: tb.map((t) => t.querySelectorAll(':scope > tr.tn-rand').length),
                  detalii_vazute: tb.filter((t) => !t.querySelector('.tn-detaliu').hidden).length,
                  explicatie: (c.innerText.match(/nu se validează fără documentul din care provine/g) || []).length,
                  legenda: !!c.querySelector('#jn-expl-fara_doc'),
                  aria: c.querySelector('[data-val="1031"]').getAttribute('aria-describedby'),
                  dezactivat: c.querySelector('[data-val="1031"]').getAttribute('aria-disabled') === 'true',
                  motiv: c.querySelector('[data-val="1031"]').title}; }""" % _CORP)
        assert m["note"] == 34 and set(m["randuri"]) == {1}, m              # „tabel cu un rând pe notă”
        assert m["detalii_vazute"] == 0, m                                   # „detaliul la clic”: închis la deschidere
        assert m["explicatie"] == 1 and m["legenda"], m                      # „explicațiile o singură dată” (două note fără document)
        assert m["dezactivat"] and "jn-expl-fara_doc" in m["aria"], m       # [386] „Validează” inactiv, legat de explicație
        # [lotul 13, 675 / 610] inactiv cu motivul (pasul notei) la trecerea cu mouse-ul — clicul nu dă niciun refuz
        assert m["motiv"].startswith("Notă fără document justificativ. Scrie referința"), m
        pg.click("tbody[data-nota-id='1005'] .tn-rand td:nth-child(4)")     # clic pe rând (în afara butoanelor)
        pg.wait_for_selector("#jn-det-1005", state="visible", timeout=5000)
        celule = pg.evaluate("""() => [...document.querySelectorAll('#jn-det-1005 table.tn-linii tbody tr')]
          .map((r) => [...r.cells].map((c) => c.textContent.trim()))""")
        assert celule == [["4111", "704", "1.234,56", "ALFA SRL"]], celule    # liniile notei, cu partenerul (celulele tabelului)
        assert pg.get_attribute("tbody[data-nota-id='1005'] .tn-deschide", "aria-expanded") == "true"
    finally:
        pg.close()
    assert not erori, erori


@pytest.mark.parametrize("cautat, stare, asteptat", [
    ("5121", "", 33),                 # contul (toate în afară de nota pe 4111 = 704)
    ("704", "", 1),
    ("1.234,56", "", 1), ("1234,56", "", 1), ("1234.56", "", 1),     # suma, în cele trei forme
    ("alfa", "", 1), ("14399840", "", 1),                               # partenerul, după nume sau cod fiscal
    ("Extras 7", "", 1),                                                # documentul
    ("nr. crt. 12", "", 1),                                             # numărul curent
    ("", "validata", 30), ("", "ciorna", 4), ("", "respinsa", 1), ("", "fara_doc", 2),
    ("comision", "fara_doc", 2), ("comision", "validata", 0),
])
def test_def_617_cautarea_si_filtrul_de_stare(browser, cautat, stare, asteptat):
    """ROȘU înainte: Registrul jurnal n-avea niciun câmp de căutare și niciun filtru (`#jn-cauta` / `#jn-stare` lipseau)."""
    pg, erori = _pagina(browser, _rute_jurnal({"note": _note_jurnal()}))
    try:
        _deschide_jurnal(pg)
        if stare:
            pg.select_option("#jn-stare", stare)
        if cautat:
            pg.fill("#jn-cauta", cautat)
        pg.wait_for_timeout(100)
        m = pg.evaluate("""() => { const c = (%s)(); return {vazute: [...c.querySelectorAll('tbody[data-nota-id]')].filter((t) => !t.hidden).length,
          numar: (c.querySelector('#jn-numar') || {}).textContent, nimic: !c.querySelector('#jn-nimic').hidden}; }""" % _CORP)
    finally:
        pg.close()
    assert not erori, erori
    assert m["vazute"] == asteptat, (cautat, stare, m)
    assert m["numar"] == ("%d din 34 de note" % asteptat), m                   # câte se văd, din câte are luna
    assert m["nimic"] == (asteptat == 0), m


def test_def_617_dupa_valideaza_ramane_pe_loc_cu_starea_noua_si_confirmarea(browser):
    """ROȘU înainte: „Validează” chema `deseneaza()` — fereastra trecea prin „Se încarcă…” și sărea sus (scrollTop 0), fără confirmare."""
    stare = {"note": _note_jurnal()}
    pg, erori = _pagina(browser, _rute_jurnal(stare))
    try:
        _deschide_jurnal(pg)
        inainte = pg.evaluate(_LA_MIJLOC % "tbody[data-nota-id='1033']")
        assert inainte > 300, inainte                                          # anti-vacuu: fereastra chiar e derulată
        pg.evaluate("() => document.querySelector(\"[data-val='1033']\").click()")   # clicul omului, fără derularea lui Playwright
        pg.wait_for_function("() => ((document.querySelector('#j-mesaj') || {}).textContent || '').includes('Ai validat')", timeout=5000)
        m = pg.evaluate("""() => { const c = (%s)(), rc = c.getBoundingClientRect(), z = c.querySelector('#j-mesaj').getBoundingClientRect();
          const r = c.querySelector("tbody[data-nota-id='1033']");
          return {sus: c.scrollTop, mesaj: c.querySelector('#j-mesaj').textContent, in_vedere: z.top >= rc.top - 1 && z.bottom <= rc.bottom + 1,
                  stare: r.querySelector('.tn-rand').innerText, evid: r.classList.contains('val-evidentiat')}; }""" % _CORP)
    finally:
        pg.close()
    assert not erori, erori
    assert abs(m["sus"] - inainte) <= 40, (inainte, m)                        # „pagina sare sus” -> rămâne pe loc (± rândul mesajului)
    assert "Ai validat nota nr. crt. 99" in m["mesaj"] and m["in_vedere"], m   # confirmarea, în vedere
    assert "Validată" in m["stare"] and m["evid"], m                           # rândul arată starea nouă


# ── 622: De validat ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _element_nota(cid, tid, nid, creat_de="7", doc="Factura F1A nr. 3 din 01.09.2026", **x):
    e = {"id": cid, "tenant_id": tid, "fel": "nota", "tip": "nota", "stare": "la_senior", "creat_de": creat_de, "creat_de_nume": "Asistent",
         "eticheta": "Notă · Contare factură", "perioada": "nota-%d" % nid,
         "nota": {"inregistrare_id": nid, "data": "2026-09-05", "descriere": "Contare factură %d" % nid, "document_ref": doc, "total": "121.00",
                  "rulaj": "121.00", "rulaj_storno": "0", "partener": "BETA SRL"}}
    e.update(x)
    return e


def _rute_validat(stare):
    def coada(_m, _c, _q, _b):
        return {"coada": [dict(e) for e in stare["coada"]]}

    def aproba(_m, cale, _q, _b):
        cid = int(cale.split("/")[-2])
        stare["coada"] = [e for e in stare["coada"] if e["id"] != cid]
        return {"ok": True}

    def continut(_m, cale, _q, _b):
        cid = int(cale.split("/")[-2])
        e = next((x for x in stare["coada"] if x["id"] == cid), None) or {"nota": {}}
        return {"fel": "nota", "nota": e["nota"], "linii": [{"debit": "4111", "credit": "704", "suma": 100}, {"debit": "4111", "credit": "4427", "suma": 21}]}
    return {"/coada": coada, "/aproba": aproba, "/continut": continut,
            "/tenants": {"tenants": [{"id": 1, "nume": "Firma Unu SRL"}, {"id": 2, "nume": "Firma Doi SRL"}]},
            "/eu/permisiuni": {"poate_valida": True, "poate_depune": True, "rol": "admin_firma"},
            "/eu/patru-ochi": {"activ": False, "efectiv": False},
            "/eu/ciorne": {"total": 2, "firme": [{"tenant_id": 1, "firma": "Firma Unu SRL", "note": [
                # a mea, trimisă la validare: e deja în „Note de validat” (elementul 503) — nu se arată a doua oară
                {"id": 903, "data": "2026-09-07", "descriere": "Contare factură 903", "document_ref": "Factura X", "rulaj": 50, "rulaj_storno": 0,
                 "in_coada": "la_senior", "motiv_respingere": None},
                {"id": 904, "data": "2026-09-08", "descriere": "Ciorna mea netrimisă", "document_ref": None, "rulaj": 20, "rulaj_storno": 0,
                 "in_coada": None, "motiv_respingere": None}]}]},
            "/drepturi": {"drepturi": None}}


def _coada_proba():
    return [_element_nota(501, 1, 901), _element_nota(502, 2, 902, doc=None),
            _element_nota(503, 1, 903, creat_de="5", doc="Factura X"),     # a mea (uid 5): „ai pregătit-o tu”
            {"id": 601, "tenant_id": 1, "fel": "declaratie", "tip": "d300", "stare": "la_senior", "creat_de": "7", "creat_de_nume": "Asistent",
             "perioada": "2026-10-25", "p_an": 2026, "p_luna": 9, "verdict_stare": {"stare": "proaspat", "verdict": "valid"}, "gata_de_depus": True}]


def _deschide_validat(pg):
    pg.evaluate("""async () => { const v = await import('/static/js/ecrane/validat.js');
      window._nav.deschide('De validat', (c, n) => v.randeazaValidat(c, n, {titlu: 'De validat'}), {nivel: 'cabinet'}); }""")
    pg.wait_for_selector("#val-note table.tn-tabel", timeout=15000)
    pg.wait_for_timeout(200)


def test_def_622_trei_sectiuni_cu_numar_acelasi_tabel_nota_o_singura_data(browser):
    """ROȘU înainte: notele erau carduri `.val-card`, ciornele proprii o listă `ul.sa-jurnal`, declarațiile alte carduri; nota mea trimisă
    la validare apărea și în „Note de validat”, și în „Notele tale în ciornă”; nicio căutare."""
    pg, erori = _pagina(browser, _rute_validat({"coada": _coada_proba()}))
    try:
        _deschide_validat(pg)
        m = pg.evaluate("""() => { const c = (%s)();
          const ids = [...c.querySelectorAll('tbody.tn-nota')].map((t) => t.dataset.coadaIds || ('n' + t.dataset.ciorna));
          return {titluri: [...c.querySelectorAll('section > .cf-grup-titlu')].map((x) => x.textContent),
                  tabele: c.querySelectorAll('section table.tn-tabel').length, ids,
                  carduri_note: c.querySelectorAll('#val-note .val-card, #val-ciorne .val-card, .sa-jurnal').length,
                  pe_rand: [...c.querySelectorAll("#val-note tbody[data-coada-ids='501'] .tn-rand button")].map((b) => b.textContent.trim()),
                  cautare: !!c.querySelector('#val-rezumat #val-cauta')}; }""" % _CORP)
    finally:
        pg.close()
    assert not erori, erori
    assert m["titluri"] == ["Note de validat (3)", "Declarații (1)", "Notele tale în ciornă (1)"], m      # „Trei secțiuni cu număr”
    assert m["tabele"] == 2 and m["carduri_note"] == 0, m                                                  # „același tabel ca la 617”
    assert sorted(m["ids"]) == ["501", "502", "503", "n904"], m                                           # „note afișate de două ori”: o dată
    assert "Validează" in m["pe_rand"] and "Respinge" in m["pe_rand"], m                                  # „Validează/Respinge pe rând”
    assert m["cautare"], m


@pytest.mark.parametrize("cautat, asteptat", [("Firma Doi", 1), ("BETA", 3), ("4427", 3), ("d300", 1), ("netrimisă", 1), ("121,00", 3)])
def test_def_622_cautarea(browser, cautat, asteptat):
    """„căutare”: după firmă, partener, cont (liniile se încarcă la prima căutare), declarație, starea, sumă — în toate trei secțiunile."""
    pg, erori = _pagina(browser, _rute_validat({"coada": _coada_proba()}))
    try:
        _deschide_validat(pg)
        pg.fill("#val-cauta", cautat)
        pg.wait_for_timeout(600)
        vazute = pg.evaluate("""() => { const c = (%s)(); return [...c.querySelectorAll('tbody.tn-nota, #val-declaratii .val-card')]
          .filter((x) => !x.hidden).length; }""" % _CORP)
    finally:
        pg.close()
    assert not erori, erori
    assert vazute == asteptat, (cautat, vazute)


def test_def_622_validarea_ramane_pe_loc_cu_confirmarea_in_rezumat(browser):
    """ROȘU înainte: după „Validează”, coada trecea prin „Se încarcă coada…” (sărea sus); confirmarea stătea la capătul de sus al ferestrei."""
    coada = _coada_proba() + [_element_nota(700 + i, 1, 1700 + i) for i in range(30)]
    stare = {"coada": coada}
    pg, erori = _pagina(browser, _rute_validat(stare))
    try:
        _deschide_validat(pg)
        inainte = pg.evaluate(_LA_MIJLOC % "tbody[data-coada-ids='720']")
        assert inainte > 300, inainte
        pg.evaluate("() => document.querySelector(\"tbody[data-coada-ids='720'] .val-aproba\").click()")
        pg.wait_for_function("() => ((document.querySelector('#val-confirmare') || {}).textContent || '').includes('Ai validat')", timeout=5000)
        m = pg.evaluate("""() => { const c = (%s)(), rc = c.getBoundingClientRect(), z = c.querySelector('#val-confirmare').getBoundingClientRect();
          return {sus: c.scrollTop, in_vedere: z.top >= rc.top - 1 && z.bottom <= rc.bottom + 1,
                  ramas: !!c.querySelector("tbody[data-coada-ids='720']"), titlu: c.querySelector('#val-note-titlu').textContent}; }""" % _CORP)
    finally:
        pg.close()
    assert not erori, erori
    assert abs(m["sus"] - inainte) <= 80, (inainte, m)        # pe loc (rândul validat iese din listă: cel mult înălțimea lui)
    assert m["in_vedere"] and not m["ramas"] and m["titlu"] == "Note de validat (32)", m


# ── 621: rezumatul nu mănâncă tabelul ────────────────────────────────────────────────────────────────────────────────────────────
_COL = ["si_d", "si_c", "prec_d", "prec_c", "rul_d", "rul_c", "tot_d", "tot_c", "sf_d", "sf_c"]
_RULAJE = ("Rulajele de la 01.01.2026 până la 30.09.2026 lipsesc: evidența firmei în iConta.eu începe după 30.09.2026, iar balanța de "
           "deschidere are numai soldurile finale, fără soldurile inițiale ale anului și rulajele lui. Pe 2026, «Sold inițial» arată soldul de la "
           "data preluării, nu de la 1 ianuarie, iar «Sume precedente» nu cuprind lunile dinainte de preluare (veniturile și cheltuielile anului, "
           "deci rezultatul cumulat, ies mai mici). Importă din nou balanța de la 30.09.2026 cu soldurile inițiale ale anului și rulajele (Import "
           "date › Solduri inițiale), ca ele să intre ca sold inițial și sume precedente.")


def _balanta(inchide=True):
    perechi = [{"ce": c, "debit": 10, "credit": 10 if inchide else 9, "diferenta": 0 if inchide else 1, "inchisa": inchide}
               for c in ("sold inițial", "sume precedente", "rulaje curente", "total sume", "sold final")]
    return {"randuri": [dict(cont="%d" % (4000 + i), denumire="Cont %d" % i, **{k: 1000 + i for k in _COL}) for i in range(40)],
            "totaluri": {k: 99999 for k in _COL}, "note_lunii": 3, "ciorne": {"luna": 2, "inainte": 3},
            "avertismente": [{"fel": "necunoastere", "tip": "rulaje_preluare", "motiv": _RULAJE}],
            "inchidere": {"stare": "se_inchide" if inchide else "nu_se_inchide", "randuri": 40, "perechi": perechi}}


_REZ = """() => { const c = (%s)(), r = c.querySelector('.rezumat-fix'); return {rez: r ? r.offsetHeight : null, corp: c.clientHeight}; }""" % _CORP


@pytest.mark.parametrize("inchide", [True, False])
def test_def_621_balanta_rezumatul_lipit_ramane_mic_si_importul_are_buton(browser, inchide):
    """ROȘU înainte (1280×720, ciorne + rulaje lipsă): rezumatul lipit sus avea ~360 px dintr-un corp de ~610 — „casetele de sus ocupă jumătate
    din fereastră”; caseta rulajelor n-avea buton spre import."""
    rute = {"/balanta": _balanta(inchide), "/migrare/straturi": {"straturi": ["solduri"]}}
    pg, erori = _pagina(browser, rute)
    try:
        pg.evaluate("""async () => { const f = await import('/static/js/ecrane/firme.js');
          f.deschideFirma({id: 1, nume: 'Firma Probă SRL', cui: '1', regim_contabil: 'dubla', tip_firma: 'srl', platitor_tva: true}, window._nav); }""")
        pg.wait_for_selector("#fa-balanta", timeout=15000)
        pg.click("#fa-balanta")
        pg.wait_for_selector("#b-rulaje-import", timeout=15000)
        pg.wait_for_timeout(300)
        m = pg.evaluate(_REZ)
        pg.evaluate("() => { const c = (%s)(); c.scrollTop = c.scrollHeight / 2; }" % _CORP)
        pg.wait_for_timeout(100)
        # cât derulezi, rândurile de tabel care se văd între rezumat și bara de jos
        randuri = pg.evaluate("""() => { const c = (%s)(), rc = c.getBoundingClientRect(), rez = c.querySelector('.rezumat-fix').getBoundingClientRect();
          const bara = [...c.querySelectorAll('.bara-fixa')].pop().getBoundingClientRect();
          return [...c.querySelectorAll('table.fd-tabel tbody tr')].filter((r) => { const b = r.getBoundingClientRect();
            return b.top >= rez.bottom - 1 && b.bottom <= Math.min(bara.top, rc.bottom) + 1; }).length; }""" % _CORP)
        pg.evaluate("() => { (%s)().scrollTop = 0; }" % _CORP)
        pg.click("#b-rulaje-import")
        pg.wait_for_selector("#mig-pasi", timeout=10000)
        titlu = pg.inner_text("#mig-pasi")
    finally:
        pg.close()
    assert not erori, erori
    assert m["rez"] <= 0.25 * m["corp"], m                       # „Casetele nu mănâncă tabelul”
    assert randuri >= 10, randuri                                 # cât derulezi se văd cel puțin 10 rânduri (erau 2–3)
    assert "Solduri inițiale" in titlu, titlu                     # „«Importă…» are butonul spre ecranul de import”


DATE_ECRANE = {
    "/jurnal": {"note": _note_jurnal(), "total_debit": 500, "total_credit": 500, "ciorne": {"note": 4, "total": 10}, "note_fara_document": 2},
    "/centre-cost": {"centre": []},
    "/stocuri/nir": {"nir": []},
    "/firma-profil/date": {"profil": {"metoda_stoc": "cantitativ_valoric"}},
    "/stocuri/articole": {"articole": [dict(id=i, denumire="Marfa %02d" % i, um="buc", stoc=10, cmp=2.5, valoare=25) for i in range(40)]},
    "/stocuri/locatii": {"locatii": []},
    "/fisa-cont": {"conturi": ["5121"], "formular": "14-6-22", "fisa": {
        "randuri": [dict(data="2026-09-%02d" % (i % 28 + 1), document="Doc %d" % i, explicatie="Plată %d" % i, cont_corespondent="401",
                         debit=10, credit=0, sold=10 * i, sens_sold="D", jurnal="J") for i in range(40)],
        "sold_initial_declarat": True, "sold_initial": 100, "total_debit": 400, "total_credit": 0, "sold_final": 500, "sens_sold_final": "D",
        "temei_completitudine": "x"}},
}


@pytest.mark.parametrize("card", ["#fa-balanta", "#fa-jurnal", "#fa-stocuri", "#fa-fisacont"])
def test_def_621_rezumatul_ecranelor_cu_tabel_ramane_sub_un_sfert_din_fereastra(browser, card):
    """Clasa 621, pe ecranele firmei cu tabel și cu cele mai multe blocuri sus (ciorne, rulaje lipsă, căutare, motivul amortizării)."""
    rute = dict(DATE_ECRANE, **{"/balanta": _balanta(False)})
    pg, erori = _pagina(browser, rute)
    try:
        pg.evaluate("""async () => { const f = await import('/static/js/ecrane/firme.js');
          f.deschideFirma({id: 1, nume: 'Firma Probă SRL', cui: '1', regim_contabil: 'dubla', tip_firma: 'srl', platitor_tva: true}, window._nav); }""")
        pg.wait_for_selector(card, timeout=15000)
        pg.click(card)
        pg.wait_for_selector(".fereastra-corp .rezumat-fix", timeout=15000)
        pg.wait_for_selector(".fereastra-corp table", timeout=15000)
        pg.wait_for_timeout(400)
        m = pg.evaluate(_REZ)
    finally:
        pg.close()
    assert not erori, erori
    assert m["rez"] and m["rez"] <= 0.25 * m["corp"], (card, m)


# ── 459.1: datele aduse de la ANAF țin de CUI-ul lor ─────────────────────────────────────────────────────────────────────────────
def _verifica_cui(_m, cale, _q, _b):
    cui = urllib.parse.unquote(cale.rsplit("/", 1)[-1])
    return {"gasit": True, "denumire": "DANTE INTERNATIONAL SA"} if cui == "14399840" else {"gasit": False}


def test_def_459_1_denumirea_adusa_de_la_anaf_dispare_la_schimbarea_cui_ului(browser):
    """ROȘU înainte: după CUI-ul 14399840 (DANTE INTERNATIONAL SA), un alt CUI lăsa denumirea DANTE în câmp; rândul de sub CUI se încheia
    cu „— verifică.”."""
    pg, erori = _pagina(browser, {"/verifica-cui": _verifica_cui, "/tenants": {"tenants": []}})
    try:
        pg.evaluate("""async () => { const f = await import('/static/js/ecrane/firme.js'); document.body.insertAdjacentHTML('beforeend', '<div id="lista"></div>');
          f.randeazaListaFirme(document.getElementById('lista'), window._nav, () => {}); }""")
        pg.click("#firme-adauga")
        pg.wait_for_selector("#fn-cui", timeout=10000)
        pg.fill("#fn-cui", "14399840")
        pg.wait_for_function("() => document.querySelector('#fn-nume').value === 'DANTE INTERNATIONAL SA'", timeout=5000)
        info = pg.inner_text("#fn-cui-info")
        pg.fill("#fn-cui", "1439984")                    # CUI-ul schimbat (o cifră scoasă)
        nume_dupa = pg.input_value("#fn-nume")
        pg.fill("#fn-cui", "14399840")
        pg.wait_for_function("() => document.querySelector('#fn-nume').value === 'DANTE INTERNATIONAL SA'", timeout=5000)
        pg.fill("#fn-nume", "DANTE INTERNATIONAL SA — corectat de mine")   # scris de om
        pg.fill("#fn-cui", "18547290")
        pg.wait_for_timeout(700)
        nume_om = pg.input_value("#fn-nume")
    finally:
        pg.close()
    assert not erori, erori
    assert info.startswith("Din ANAF: DANTE INTERNATIONAL SA.") and "verifică" not in info, info
    assert nume_dupa == "", nume_dupa                                     # „denumirea adusă de la CUI-ul anterior” nu mai rămâne
    assert nume_om == "DANTE INTERNATIONAL SA — corectat de mine", nume_om  # ce a scris omul rămâne (F188)


# ── 628: contorul situației stocului e al ferestrei ──────────────────────────────────────────────────────────────────────────────
def test_628_doua_ferestre_stocuri_nu_isi_anuleaza_lista(browser):
    """ROȘU înainte: contorul `cerereCV` era al modulului — a doua fereastră (altă firmă) scotea din joc cererea în zbor a primei, care
    rămânea pe „Se încarcă situația stocului…”."""
    b, port = browser
    pg = b.new_page(viewport={"width": LAT, "height": INALT})
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))
    try:
        def h(route):
            u = urllib.parse.urlsplit(route.request.url)
            if u.path.startswith("/static/"):
                return route.continue_()
            tid = u.path.split("/")[2]
            if u.path.endswith("/stocuri/articole"):
                arts = [dict(id=i, denumire="Marfa %s-%d" % (tid, i), um="kg", stoc=1, cmp=1, valoare=1) for i in range(4 if tid == "1" else 6)]
                if tid == "1":
                    pg.wait_for_timeout(600)               # prima firmă răspunde ultima
                return route.fulfill(status=200, content_type="application/json", body=json.dumps({"articole": arts}))
            return route.fulfill(status=200, content_type="application/json", body=json.dumps({"locatii": []}))
        pg.route("**/tenants/**", h)
        pg.goto("http://127.0.0.1:%d/static/" % port)
        n = pg.evaluate("""async () => { const f = await import('/static/js/ecrane/firme.js');
          document.body.innerHTML = '<div id="a"><div id="s-situatie"></div><div id="cv-zona"></div></div><div id="b"><div id="s-situatie"></div><div id="cv-zona"></div></div>';
          const A = document.getElementById('a'), B = document.getElementById('b');
          const pa = f.sectiuneaCV(A, {id: 1}, null); const pb = f.sectiuneaCV(B, {id: 2}, null);
          await Promise.all([pa, pb]);
          return [A.querySelectorAll('#s-situatie tbody tr').length, B.querySelectorAll('#s-situatie tbody tr').length]; }""")
    finally:
        pg.close()
    assert not [e for e in erori if "Cannot read" not in e or "cv-" not in e], erori
    assert n == [4, 6], n


# ── defect găsit de pachetul form2: „Șterge” la ajustarea fiscală nu făcea nimic ────────────────────────────────────────────────
def test_ajustarea_fiscala_se_sterge_dupa_confirmare(browser):
    """ROȘU înainte: `await confirmaCaseta("Ștergi ajustarea?…", {…})` — funcția primea textul în locul zonei (`zona.parentNode` ->
    TypeError în consolă) și nu întoarce promisiune: clicul nu arăta întrebarea și nu ștergea nimic. Acum: întrebarea neutră
    (`.caseta-intrebare`), „Da, șterge ajustarea” -> cererea DELETE pe ajustarea aleasă."""
    cereri = []
    rute = {"/registru-evidenta-fiscala": {"temei": "t", "temei_completitudine": "t", "corp": {"sectiuni": []}},
            "/ajustari-fiscale": {"ajustari": [{"id": 77, "an": 2026, "trim": 3, "eticheta": "Cheltuieli cu amenzi", "suma": 100,
                                                "descriere": "Amendă", "document": "PV 1"}], "randuri": [], "din_conturi": [], "anuale": []}}
    pg, erori = _pagina(browser, rute, cereri)
    try:
        pg.evaluate("""async () => { const f = await import('/static/js/ecrane/firme.js');
          f.deschideFirma({id: 1, nume: 'Firma Probă SRL', cui: '1', regim_contabil: 'dubla', tip_firma: 'srl', platitor_tva: true}, window._nav); }""")
        pg.wait_for_selector("#fa-regfiscal", timeout=15000)
        pg.click("#fa-regfiscal")
        pg.wait_for_selector("[data-aj-sterge='77']", timeout=15000)
        pg.click("[data-aj-sterge='77']")
        pg.wait_for_selector(".caseta-intrebare #ca-ok", timeout=5000)
        pg.click(".caseta-intrebare #ca-ok")
        pg.wait_for_timeout(400)
    finally:
        pg.close()
    assert not erori, erori
    assert ("DELETE", "/tenants/1/ajustari-fiscale/77") in cereri, cereri
