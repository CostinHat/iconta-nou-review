"""17.5-Q10 — proba candidatului pe iconta_test:8019 (nu e în plasa fixă; se rulează prin rulare_8019.sh -> scripts/e2e_poarta.py --doar).

Măsoară, la 1366×768 și 603×590 (antetul și la 1920×1080), după două cadre livrate (rAF dublu) în fila vizibilă: DOM, stil calculat, hit-test,
captură și răspunsul API independent al aceleiași ferestre. Ieșirea: <E2E_CAPTURI>/17_5_Q10_probe/brut.json + capturile; verdictul pe celule
îl scrie `construieste_probe_q10.py` (masuri_ds.json, probe_fluxuri.json). Nicio secțiune nu oprește celelalte: eroarea ei se scrie în brut.
"""
import json
import os
import sys
import time
import traceback
from pathlib import Path

RAD_E2E = Path(__file__).resolve().parents[3] / "frontend_test" / "e2e"
sys.path.insert(0, str(RAD_E2E))
# conftest-ul plasei (frontend_test/e2e), încărcat sub numele lui propriu: rădăcina are alt conftest.py, deja importat de pytest ca „conftest”
import importlib.util as _iu  # noqa: E402
_spec = _iu.spec_from_file_location("conftest_e2e_q10", RAD_E2E / "conftest.py")
conftest_e2e = _iu.module_from_spec(_spec)
_spec.loader.exec_module(conftest_e2e)
sys.modules.setdefault("conftest", conftest_e2e) if "conftest" not in sys.modules else None
if getattr(sys.modules.get("conftest"), "sesiune", None) is None:
    sys.modules["conftest"] = conftest_e2e   # e2e_ferestre_17_5_Q5 importă din „conftest” (cel al plasei)

DIM = ((1366, 768), (603, 590))
CABINET = "dovada.71507@sesiuneab.test"
F1, F2 = "F1 Comert Stoc SRL", "F2 Profit Amortizare SRL"

STABIL = "() => new Promise(ok => requestAnimationFrame(() => requestAnimationFrame(ok)))"

DERULARI = """() => {
  const top = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra')].pop();
  if (!top) return null;
  const el = [top, ...top.querySelectorAll('*')].filter(e => {
    const s = getComputedStyle(e); if (!/(auto|scroll)/.test(s.overflowY + s.overflowX)) return false;
    return (e.scrollHeight > e.clientHeight + 2 || e.scrollWidth > e.clientWidth + 2) && e.getClientRects().length;
  });
  const corp = top.querySelector('.fereastra-corp');
  return {derulari: el.map(e => ({id: e.id, cls: String(e.className).slice(0, 60), sh: e.scrollHeight, ch: e.clientHeight, sw: e.scrollWidth, cw: e.clientWidth,
            xml: !!e.closest('.dec-xml-pre, pre')})),
          corp: corp ? {sh: corp.scrollHeight, ch: corp.clientHeight, sw: corp.scrollWidth, cw: corp.clientWidth} : null,
          fer: (() => { const r = top.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; })(),
          primare: [...top.querySelectorAll('.buton-primar, .fj-principal')].filter(b => b.checkVisibility({checkOpacity: true})).map(b => b.innerText.trim()),
          text: top.innerText.slice(0, 6000)};
}"""


def _pg(browser, w, h, email=CABINET, prima=False):
    sesiune = conftest_e2e.sesiune
    from core.ceas_proba import MOMENT_REF
    ctx = browser.new_context(viewport={"width": w, "height": h})
    ctx.clock.set_fixed_time(MOMENT_REF)
    ctx.add_init_script(sesiune(email, prima_intrare=prima))
    return ctx, ctx.new_page()


def _stabil(pg):
    pg.evaluate(STABIL)


def _api(pg, cale, metoda="GET", corp=None):
    return pg.evaluate("""async ([cale, metoda, corp]) => {
      const t = sessionStorage.getItem('iconta_token');
      const r = await fetch(cale, {method: metoda, headers: Object.assign({Authorization: 'Bearer ' + t}, corp ? {'Content-Type': 'application/json'} : {}),
                                    body: corp ? JSON.stringify(corp) : undefined, cache: 'no-store'});
      let d = null; try { d = await r.json(); } catch (e) {}
      return {status: r.status, date: d};
    }""", [cale, metoda, corp])


class Proba:
    def __init__(self, browser, director):
        self.b, self.dir, self.brut = browser, director, {}

    def captura(self, pg, nume):
        f = self.dir / ("%s.png" % nume)
        pg.screenshot(path=str(f))
        return f.name

    def scrie(self, cheie, valoare):
        self.brut[cheie] = valoare
        (self.dir / "brut.json").write_text(json.dumps(self.brut, ensure_ascii=False, indent=1, default=str))

    def sectiune(self, cheie, fn):
        t0 = time.time()
        try:
            v = fn()
            v = v if isinstance(v, dict) else {"rezultat": v}
        except Exception as e:  # noqa: BLE001 — o secțiune căzută se scrie, celelalte continuă
            v = {"eroare": "%s: %s" % (type(e).__name__, str(e)[:600]), "urma": traceback.format_exc()[-1500:]}
        v["durata_s"] = round(time.time() - t0, 1)
        self.scrie(cheie, v)


def _firma(pg, nume, control):
    from e2e_ferestre_17_5_Q5 import firma
    if not pg.url.startswith("http"):
        pg.goto(os.environ["PROBA_BAZA"] + "/", wait_until="domcontentloaded")
        pg.locator("button.cab-card:has([data-cheie='firme'])").wait_for()
    firma(pg, nume, control)
    _stabil(pg)


def _tenant(pg, nume):
    r = _api(pg, "/tenants")
    return next(t for t in r["date"]["tenants"] if t["nume"] == nume)


# ── AC188 — antetul ────────────────────────────────────────────────────────────────────────────────────────────────
ANTET = """() => {
  const v = document.querySelector('.bara .bara-identitate'), c = document.querySelector('.bara .cautare-globala input, .bara .cautare-globala'),
        x = document.querySelector('#nav-iesire'), u = JSON.parse(sessionStorage.getItem('iconta_user') || '{}');
  const r = (e) => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
  const hit = (e) => { const b = e.getBoundingClientRect(); const t = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2); return !!t && (e === t || e.contains(t)); };
  if (!v) return {lipsa: true};
  const s = getComputedStyle(v);
  const linii = Math.round(v.getBoundingClientRect().height / (parseFloat(s.lineHeight) || parseFloat(s.fontSize) * 1.2));
  return {cabinet: u.nume_firma || '', utilizator: [u.nume, u.prenume].filter(Boolean).join(' ') || u.email || '', text: v.textContent,
          titlu_integral: v.title, linii, text_overflow: s.textOverflow, overflow_x: s.overflowX, text_scroll_width: v.scrollWidth,
          text_client_width: v.clientWidth, latime_document: document.documentElement.scrollWidth, latime_viewport: window.innerWidth,
          inaltime_viewport: window.innerHeight, dreptunghi_veriga: r(v), dreptunghi_cautare: c ? r(c) : null, dreptunghi_iesire: r(x),
          hit_cautare: c ? hit(c) : false, hit_iesire: hit(x)};
}"""


def antet(P, email):
    out = {}
    for w, h in ((1920, 1080),) + DIM:
        ctx, pg = _pg(P.b, w, h, email)
        try:
            pg.goto(os.environ["PROBA_BAZA"] + "/", wait_until="domcontentloaded")
            pg.wait_for_selector("#nav-iesire")
            _stabil(pg)
            m = pg.evaluate(ANTET)
            m["captura"] = P.captura(pg, "AC188_%dx%d" % (w, h))
            out["%dx%d" % (w, h)] = m
        finally:
            ctx.close()
    return out


# ── C238 / C239 — primul cadru al apariției ferestrei; caseta de bun-venit ──────────────────────────────────────────────
PRIMUL_CADRU = """() => new Promise(ok => {
  const mo = new MutationObserver(() => {
    const ov = document.querySelector('.fereastra-overlay'), f = ov && ov.querySelector('.fereastra');
    if (!f) return;
    mo.disconnect();
    const an = [...ov.getAnimations(), ...f.getAnimations()];
    ok({animatie_activa: an.length > 0, nume: an.map(a => a.animationName), timp_cadru_initial_ms: an.length ? Number(an[0].currentTime || 0) : null,
        opacitate_overlay: getComputedStyle(ov).opacity, opacitate_fereastra: getComputedStyle(f).opacity,
        fereastra_vizibila: f.checkVisibility({checkOpacity: true, checkVisibilityCSS: true}), t: performance.now()});
  });
  mo.observe(document.body, {childList: true, subtree: true});
  document.querySelector("button.cab-card:has([data-cheie='firme'])").click();
})"""


def cadru(P):
    out = {}
    for w, h in DIM:
        ctx, pg = _pg(P.b, w, h)
        try:
            pg.goto(os.environ["PROBA_BAZA"] + "/", wait_until="domcontentloaded")
            pg.locator("button.cab-card:has([data-cheie='firme'])").wait_for()
            _stabil(pg)
            salut = pg.evaluate("() => { const s = document.querySelector('.sumar-toast'); return s ? s.checkVisibility({checkOpacity: true}) : null; }")
            m = pg.evaluate(PRIMUL_CADRU)
            m["salut_pe_pagina"] = salut
            _stabil(pg)
            m["salut_sub_fereastra"] = pg.evaluate("() => { const s = document.querySelector('.sumar-toast'); return s ? s.checkVisibility({checkOpacity: true}) : null; }")
            m["click_pe_principala"] = pg.evaluate("""() => { const t = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) #opt-existente, .fereastra-overlay:not(.fundal) .fj-principal')][0];
              if (!t) return false; const b = t.getBoundingClientRect(); const e = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2); return !!e && (t === e || t.contains(e)); }""")
            m["captura"] = P.captura(pg, "cadru_%dx%d" % (w, h))
            out["%dx%d" % (w, h)] = m
        finally:
            ctx.close()
    return out


# ── F011 / F012 / F073 — Banca F2: deschidere, import, reimport în aceeași fereastră ─────────────────────────────────────
BANCA_DOM = """() => {
  const top = document.querySelector('.fereastra-overlay:not(.fundal)');
  const ids = (sel) => [...top.querySelectorAll(sel + ' tbody.tn-nota[data-tn]')].map(t => t.dataset.tn);
  const c = top.querySelector('#bk-cauta');
  const vis = (e) => !!e && e.checkVisibility({checkOpacity: true}) && e.getBoundingClientRect().height > 0;
  return {formate_vizibile: vis(top.querySelector('[data-card="formate"]')),
          eroare: (top.innerText.match(/Nu s-au putut încărca liniile\\./) || [''])[0],
          iduri_dom: [...ids('#bk-lucru'), ...ids('#bk-deoparte')], lucru: ids('#bk-lucru').length, deoparte: ids('#bk-deoparte').length,
          cautare: !!c, cautare_vizibila: vis(c), carduri: [...top.querySelectorAll('.sir-carduri .card-text')].map(x => x.textContent),
          motive_alege: [...top.querySelectorAll('[data-alege]')].map(b => [b.closest('tbody') && b.closest('tbody').dataset.tn, b.getAttribute('data-motiv-inactiv') || ''])};
}"""


def banca(P):
    out = {}
    for w, h in DIM:
        ctx, pg = _pg(P.b, w, h)
        z = "%dx%d" % (w, h)
        try:
            _firma(pg, F2, "#fa-banca")
            pg.locator(".fereastra-overlay:not(.fundal) #bk-alege").wait_for(state="attached")
            pg.wait_for_timeout(1500); _stabil(pg)
            t = _tenant(pg, F2)
            pasi = []
            extras = "Data;Detalii;Suma\n12.11.2026;Comision proba Q10 %s;-3,25\n13.11.2026;Dobanda proba Q10 %s;1,10\n" % (z, z)
            for i in range(3):
                if i:
                    with pg.expect_response(lambda r: r.url.endswith("/banca/reconciliere") and r.request.method == "GET", timeout=60000):
                        pg.set_input_files(".fereastra-overlay:not(.fundal) #bk-fisier", {"name": "extras_q10_%s.csv" % z, "mimeType": "text/csv", "buffer": extras.encode()})
                    pg.wait_for_timeout(800)
                _stabil(pg)
                dom = pg.evaluate(BANCA_DOM)
                api = _api(pg, "/tenants/%s/banca/reconciliere" % t["id"])
                linii = (api["date"] or {}).get("linii") or []
                dom["http"] = api["status"]
                dom["iduri_api"] = [str(l["id"]) for l in linii]
                dom["cipuri_api"] = {"lucru": sum(1 for l in linii if l["status"] != "ignorat"), "deoparte": sum(1 for l in linii if l["status"] == "ignorat")}
                dom["cipuri_dom"] = {"lucru": dom["lucru"], "deoparte": dom["deoparte"]}
                if dom["cautare_vizibila"]:
                    tinta = next((l for l in linii if l.get("descriere")), None)
                    if tinta:
                        cauta = pg.locator(".fereastra-overlay:not(.fundal) #bk-cauta")
                        cauta.fill(tinta["descriere"][:12]); _stabil(pg)
                        dom["cautare_filtreaza"] = pg.evaluate("() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) #bk-lucru tbody.tn-nota')].filter(t => !t.hidden).length")
                        cauta.fill(""); _stabil(pg)
                dom["captura"] = P.captura(pg, "banca_%s_%d" % (z, i))
                pasi.append(dom)
            out[z] = {"pasi": pasi, "derulari": pg.evaluate(DERULARI)}
        finally:
            ctx.close()
    return out


# ── X02 — prima și a doua sesiune a unui asistent junior; prezentarea din „?” ───────────────────────────────────────────
def x02(P, email):
    out = {}
    for w, h in DIM:
        z = "%dx%d" % (w, h)
        m = {"rol": None, "sesiuni": []}
        for nr in (1, 2):
            ctx, pg = _pg(P.b, w, h, email, prima=(nr == 1))
            try:
                pg.goto(os.environ["PROBA_BAZA"] + "/", wait_until="domcontentloaded")
                pg.wait_for_selector("#nav-iesire"); pg.wait_for_timeout(1500); _stabil(pg)
                u = pg.evaluate("() => JSON.parse(sessionStorage.getItem('iconta_user') || '{}')")
                m["rol"] = "asistent junior" if u.get("rol") == "angajat" and not u.get("poate_valida") else u.get("rol")
                s = {"poarta": pg.evaluate("() => !!document.querySelector('.fereastra-overlay') && /telefon/i.test(document.querySelector('.fereastra-overlay').innerText)"),
                     "prezentare_automata": pg.evaluate("() => /Prezentarea aplicației/.test([...document.querySelectorAll('.fereastra-overlay .fir-acum')].map(x => x.textContent).join(' '))"),
                     "captura_intrare": P.captura(pg, "X02_%s_sesiunea%d" % (z, nr))}
                if s["poarta"]:
                    tel = pg.locator(".fereastra-overlay input[type=tel], .fereastra-overlay input[id*=telefon]").first
                    tel.fill("0722000111")
                    pg.locator(".fereastra-overlay button", has_text="Salvează").first.click(); pg.wait_for_timeout(1500)
                    cont = pg.locator(".fereastra-overlay button", has_text="Continuă")
                    if cont.count():
                        cont.first.click(); pg.wait_for_timeout(1000)
                    s["poarta_dupa_configurare"] = pg.evaluate("() => !!document.querySelector('.fereastra-overlay') && /telefon/i.test(document.querySelector('.fereastra-overlay').innerText)")
                inch = {}
                deschis = lambda: pg.evaluate("() => [...document.querySelectorAll('.fereastra-overlay .fir-acum')].some(x => x.textContent === 'Prezentarea aplicației')")  # noqa: E731
                for fel in ("x", "esc", "buton_jos", "esc_dupa_inapoi"):
                    pg.click("#nav-ghid"); pg.wait_for_timeout(1200); _stabil(pg)
                    s.setdefault("deschidere_manuala", deschis())
                    if fel == "x":
                        pg.locator(".fereastra-overlay:not(.fundal) .fereastra-antet .nav-x").click()
                    elif fel == "esc":
                        pg.keyboard.press("Escape")
                    elif fel == "buton_jos":
                        b = pg.locator(".fereastra-overlay:not(.fundal) #ans-inchide")
                        s["buton_jos_in_bara"] = b.evaluate("b => !!b.closest('.fereastra-jos')") if b.count() else False
                        if b.count():
                            b.click()
                    else:
                        pg.locator(".fereastra-overlay:not(.fundal) [data-card='ans-card-inceput']").click(); pg.wait_for_timeout(1200)
                        pg.locator(".fereastra-overlay:not(.fundal) .nav-inapoi").first.click(); pg.wait_for_timeout(1200); _stabil(pg)
                        s["captura_dupa_inapoi"] = P.captura(pg, "X02_%s_s%d_dupa_inapoi" % (z, nr))
                        pg.keyboard.press("Escape")
                    pg.wait_for_timeout(700); _stabil(pg)
                    inch[fel] = not deschis()
                    if not inch[fel]:
                        pg.goto(os.environ["PROBA_BAZA"] + "/", wait_until="domcontentloaded"); pg.wait_for_selector("#nav-iesire"); pg.wait_for_timeout(1000)
                s["inchideri"] = inch
                m["sesiuni"].append(s)
            finally:
                ctx.close()
        out[z] = m
    return out


# ── AC190 — expirarea sesiunii (răspunsul 401 al serverului, simulat prin interceptarea cererilor protejate) ──────────────
def ac190(P):
    out = {}
    for w, h in DIM:
        ctx, pg = _pg(P.b, w, h)
        z = "%dx%d" % (w, h)
        jurnal = []
        try:
            pg.goto(os.environ["PROBA_BAZA"] + "/", wait_until="domcontentloaded")
            pg.locator("button.cab-card:has([data-cheie='firme'])").wait_for(); _stabil(pg)
            token = pg.evaluate("() => sessionStorage.getItem('iconta_token')")
            user = pg.evaluate("() => JSON.parse(sessionStorage.getItem('iconta_user'))")
            mod = {"fel": None}
            def ruta(route):
                req = route.request
                cale = req.url.split("8019", 1)[-1]
                if mod["fel"] == "401" and "/auth/" not in cale and req.headers.get("authorization"):
                    jurnal.append([cale, req.method, 401]); return route.fulfill(status=401, json={"detail": "token expirat"})
                if mod["fel"] == "403" and cale.startswith("/tenants") and req.headers.get("authorization"):
                    jurnal.append([cale, req.method, 403]); return route.fulfill(status=403, json={"detail": "Nu ai acces"})
                if mod["fel"] == "retea" and cale.startswith("/tenants"):
                    jurnal.append([cale, req.method, "abort"]); return route.abort()
                if cale.startswith("/auth/login") and mod["fel"] in ("login_gresit", "login_bun"):
                    st = 401 if mod["fel"] == "login_gresit" else 200
                    jurnal.append([cale, req.method, st])
                    return route.fulfill(status=st, json={"detail": "email sau parola greșite"} if st == 401 else {"token": token, "user": user})
                return route.continue_()
            pg.route("**/*", ruta)
            m = {}
            for fel in ("403", "retea"):
                mod["fel"] = fel
                pg.evaluate("() => { document.querySelector(\"button.cab-card:has([data-cheie='firme'])\").click(); }"); pg.wait_for_timeout(1500)
                m["reveniri_la_" + ("403" if fel == "403" else "eroare_retea")] = pg.locator(".reaut-overlay").count()
                pg.keyboard.press("Escape"); pg.goto(os.environ["PROBA_BAZA"] + "/", wait_until="domcontentloaded"); pg.wait_for_timeout(800)
            mod["fel"] = None
            pg.locator("button.cab-card:has([data-cheie='firme'])").wait_for()
            mod["fel"] = "401"
            pg.evaluate("""() => { const t = sessionStorage.getItem('iconta_token');
              ['/tenants', '/coada', '/notificari'].forEach(c => import('/static/js/api.js').then(m => m.api.get(c).catch(() => {}))); }""")
            pg.wait_for_timeout(2000); _stabil(pg)
            m["reveniri_login"] = pg.locator(".reaut-overlay").count()
            m["login_vizibil"] = pg.locator(".reaut-overlay #reaut-parola").is_visible() if m["reveniri_login"] else False
            m["text_motiv"] = pg.locator(".reaut-overlay").first.inner_text() if m["reveniri_login"] else ""
            m["motiv_vizibil"] = "expirat" in m["text_motiv"].casefold()
            m["captura_401"] = P.captura(pg, "AC190_%s_401" % z)
            m["status_protejate"] = sorted({x[2] for x in jurnal if x[2] == 401}) * 2 if sum(1 for x in jurnal if x[2] == 401) >= 2 else [x[2] for x in jurnal if x[2] == 401]
            mod["fel"] = "login_gresit"
            if m["reveniri_login"]:
                pg.fill(".reaut-overlay #reaut-parola", "parola-gresita"); pg.click(".reaut-overlay #reaut-continua"); pg.wait_for_timeout(1200)
                m["bucla_la_login_invalid"] = pg.locator(".reaut-overlay").count() != 1
                m["eroare_login_invalid"] = pg.locator(".reaut-overlay #reaut-eroare").inner_text()
                mod["fel"] = "login_bun"
                with pg.expect_response(lambda r: "/tenants" in r.url and r.request.method == "GET", timeout=20000) as rr:
                    pg.fill(".reaut-overlay #reaut-parola", "parola-buna"); pg.click(".reaut-overlay #reaut-continua")
                m["dupa_reautentificare"] = rr.value.status
            m["secventa_http"] = jurnal
            out[z] = m
        finally:
            ctx.close()
    return out


# ── AC189 — Verificări F1, Intrastat ───────────────────────────────────────────────────────────────────────────────────
def ac189(P):
    out = {}
    for w, h in DIM:
        ctx, pg = _pg(P.b, w, h)
        z = "%dx%d" % (w, h)
        try:
            _firma(pg, F1, "#fa-verificari"); pg.wait_for_timeout(2500); _stabil(pg)
            t = _tenant(pg, F1)
            api = _api(pg, "/tenants/%s/intrastat-praguri?an=2026" % t["id"])
            txt = pg.locator(".fereastra-overlay:not(.fundal)").inner_text()
            import re
            mi = re.search(r"Introduceri: ([^·]*?\)) ·", txt); me = re.search(r"Expedieri: ([^\n·]*?\))", txt)
            out[z] = {"api": api, "introduceri_dom": mi.group(1) if mi else None, "expedieri_dom": me.group(1) if me else None,
                      "captura": P.captura(pg, "AC189_%s" % z)}
        finally:
            ctx.close()
    return out


# ── geometria ferestrelor (o singură derulare; primul rând în vedere) ───────────────────────────────────────────────────
JURNAL_PRIMUL = """() => {
  const top = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-corp');
  const z = top.querySelector('.zona-derulare') || top, r = [...top.querySelectorAll('tbody.tn-nota')].find(t => t.offsetParent);
  if (!r) return {fara_note: true};
  const rz = z.getBoundingClientRect(), rr = r.getBoundingClientRect(), rc = top.getBoundingClientRect();
  return {zona: [rz.top, rz.bottom], rand: [rr.top, rr.bottom], corp: [rc.top, rc.bottom], vizibil: rr.top >= rz.top - 1 && rr.bottom <= Math.min(rz.bottom, rc.bottom) + 1,
          prima_nota: r.innerText.slice(0, 160)};
}"""


def _luna(pg, tinta):
    for _ in range(14):
        txt = pg.locator(".fereastra-overlay:not(.fundal) #j-rezumat").inner_text()
        if "Luna " + tinta in txt:
            return True
        pg.locator(".fereastra-overlay:not(.fundal) #j-prev").click()
        pg.wait_for_timeout(1500)
    return False


def jurnal(P):
    out = {}
    for w, h in DIM:
        ctx, pg = _pg(P.b, w, h)
        z = "%dx%d" % (w, h)
        try:
            for luna in ("11/2026", "10/2026", "09/2026"):
                _firma(pg, F1, "#fa-jurnal"); pg.wait_for_timeout(2500)
                _luna(pg, luna); pg.wait_for_timeout(1500); _stabil(pg)
                m = pg.evaluate(JURNAL_PRIMUL)
                m["derulari"] = pg.evaluate(DERULARI)
                m["captura"] = P.captura(pg, "jurnal_%s_%s" % (z, luna.replace("/", "_")))
                out["%s %s" % (z, luna)] = m
        finally:
            ctx.close()
    return out


def fereastra(P, cheie, nume, control, dupa=None):
    out = {}
    for w, h in DIM:
        ctx, pg = _pg(P.b, w, h)
        z = "%dx%d" % (w, h)
        try:
            _firma(pg, nume, control); pg.wait_for_timeout(2500); _stabil(pg)
            extra = dupa(pg) if dupa else None
            pg.wait_for_timeout(800); _stabil(pg)
            m = pg.evaluate(DERULARI) or {}
            m["extra"] = extra
            m["captura"] = P.captura(pg, "%s_%s" % (cheie, z))
            out[z] = m
        except Exception as e:  # noqa: BLE001
            out[z] = {"eroare": "%s: %s" % (type(e).__name__, str(e)[:400])}
        finally:
            ctx.close()
    return out


# ── F023 — prețul adus din articol, în câmpul românesc ─────────────────────────────────────────────────────────────────────
PRET = """() => { const e = document.querySelector('.fereastra-overlay:not(.fundal) #em-l0-pret_unitar');
  if (!e) return null; const nativ = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').get.call(e);
  return {afisat: nativ, valoare: e.value, data_numar: e.getAttribute('data-numar'), total: (document.querySelector('.fereastra-overlay:not(.fundal) #em-total, .fereastra-overlay:not(.fundal) [id*=total]') || {}).textContent || ''}; }"""


def f023(P):
    out = {}
    for w, h in DIM:
        ctx, pg = _pg(P.b, w, h)
        z = "%dx%d" % (w, h)
        try:
            _firma(pg, F1, "#fa-facturi")
            pg.locator(".fereastra-overlay:not(.fundal) #fac-emite").click()
            pg.wait_for_selector(".fereastra-overlay:not(.fundal) #em-cui", state="attached"); pg.wait_for_timeout(1500)
            sel = pg.locator(".fereastra-overlay:not(.fundal) select[id^='em-l0-'][id$='articol'], .fereastra-overlay:not(.fundal) #em-l0-articol").first
            opt = sel.locator("option", has_text="Marfa A").first
            sel.select_option(opt.get_attribute("value"))
            pg.wait_for_timeout(2500); _stabil(pg)
            m = {"articol": opt.inner_text(), "dupa_articol": pg.evaluate(PRET)}
            pg.locator(".fereastra-overlay:not(.fundal) #em-l0-cantitate").fill("1")
            pg.wait_for_timeout(800)
            m["dupa_cantitate"] = pg.evaluate(PRET)
            m["captura"] = P.captura(pg, "F023_%s" % z)
            out[z] = m
        finally:
            ctx.close()
    return out


def test_probe_17_5_Q10():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            _ruleaza(browser)
        finally:
            browser.close()


def _ruleaza(browser):
    CAPTURI, BAZA = conftest_e2e.CAPTURI, conftest_e2e.BAZA
    from e2e_ferestre_17_5_Q5 import origine_proba
    origine_proba(BAZA)
    os.environ["PROBA_BAZA"] = BAZA
    director = Path(CAPTURI) / "17_5_Q10_probe"
    director.mkdir(parents=True, exist_ok=True)
    P = Proba(browser, director)
    # asistentul junior (numai «Poate pregăti») al cabinetului contului de probă, din baza restaurată
    r = conftest_e2e.sql("""SELECT u.email FROM public.users u WHERE u.rol = 'angajat' AND NOT COALESCE(u.poate_valida, false)
                             AND COALESCE(u.activ, true) AND u.accounting_firm_id = (SELECT accounting_firm_id FROM public.users WHERE email = %s) ORDER BY u.id LIMIT 1""", (CABINET,))
    junior = os.environ.get("Q10_JUNIOR") or (r[0][0] if r else None)
    P.scrie("cont_junior", {"email_anonimizat": (junior or "")[:3] + "…" if junior else None, "gasit": bool(junior)})
    P.sectiune("AC188", lambda: antet(P, junior))
    P.sectiune("AC188_cabinet", lambda: antet(P, CABINET))
    P.sectiune("cadru", lambda: cadru(P))
    P.sectiune("banca", lambda: banca(P))
    P.sectiune("AC189", lambda: ac189(P))
    P.sectiune("AC190", lambda: ac190(P))
    P.sectiune("jurnal", lambda: jurnal(P))
    P.sectiune("parteneri", lambda: fereastra(P, "parteneri", F1, "#fa-parteneri", lambda pg: pg.evaluate(
        "() => { const c = document.querySelector('.fereastra-overlay:not(.fundal) #pt-cauta'); return {cauta: !!c && c.checkVisibility(), nou: document.querySelector('.fereastra-overlay:not(.fundal) #pt-nou').className}; }")))
    P.sectiune("clienti", lambda: fereastra(P, "clienti", F1, "#fa-clienti", lambda pg: pg.evaluate(
        "() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .cl-salveaza')].map(b => [b.getAttribute('aria-disabled'), (document.getElementById(b.id + '-motiv') || {}).textContent || '', b.getAttribute('aria-describedby')])")))
    P.sectiune("furnizori", lambda: fereastra(P, "furnizori", F1, "#fa-furnizori"))
    P.sectiune("produse_formular", lambda: fereastra(P, "produse_formular", F1, "#fa-produse", lambda pg: pg.locator(".fereastra-overlay:not(.fundal) button", has_text="Adaugă produs").first.click()))
    P.sectiune("raportz", lambda: fereastra(P, "raportz", F1, "#fa-raportz", lambda pg: (
        pg.locator(".fereastra-overlay:not(.fundal) #z-salveaza").click(), pg.wait_for_timeout(800),
        pg.evaluate("() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .msg-eroare[data-camp]')].map(e => [e.dataset.camp, e.textContent])"))[2]))
    P.sectiune("casa", lambda: fereastra(P, "casa", F1, "#fa-casa"))
    P.sectiune("banca_f1", lambda: fereastra(P, "banca_f1", F1, "#fa-banca", lambda pg: pg.evaluate(
        "() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) [data-alege]')].map(b => b.getAttribute('data-motiv-inactiv') || '').filter(Boolean)")))
    P.sectiune("stocuri", lambda: fereastra(P, "stocuri", F1, "#fa-stocuri"))
    P.sectiune("F023", lambda: f023(P))
    P.sectiune("X02", lambda: x02(P, junior))
    erori = {k: v["eroare"] for k, v in P.brut.items() if isinstance(v, dict) and "eroare" in v}
    print("PROBA_Q10 sectiuni:", len(P.brut), "erori:", json.dumps(erori, ensure_ascii=False)[:2000])
