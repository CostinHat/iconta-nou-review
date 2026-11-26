"""17.5-Q12 — proba candidatului pe iconta_test:8019 (nu e în plasa fixă; se rulează prin rulare_8019.sh -> scripts/e2e_poarta.py --doar).

Pentru fiecare din cele 18 funcții ale celor 45 de celule: gestul, rezultatul din interfață (DOM după două cadre livrate, în fila vizibilă, cu
gardă de timp), dreptunghiuri și hit-test unde e o celulă de așezare, captura și sursa independentă (răspunsul API, documentul, PDF-ul).
Ieșirea: <E2E_CAPTURI>/17_5_Q12_probe/brut.json + capturile; verdictul pe celule îl scrie `construieste_rezultate_q12.py`.
Nicio secțiune nu oprește celelalte: eroarea ei se scrie în brut. Datele create pe copie (proba F017, F126, F034) sunt ale copiei de test.
"""
import json
import os
import re
import sys
import time
import traceback
from pathlib import Path

RAD_E2E = Path(__file__).resolve().parents[3] / "frontend_test" / "e2e"
sys.path.insert(0, str(RAD_E2E))
sys.path.insert(0, str(RAD_E2E.parent))
import importlib.util as _iu  # noqa: E402
_spec = _iu.spec_from_file_location("conftest_e2e_q12", RAD_E2E / "conftest.py")
conftest_e2e = _iu.module_from_spec(_spec)
_spec.loader.exec_module(conftest_e2e)
if getattr(sys.modules.get("conftest"), "sesiune", None) is None:
    sys.modules["conftest"] = conftest_e2e

DIM = ((1366, 768), (603, 590))
CABINET = "dovada.71507@sesiuneab.test"
F1, F5, F6, F7 = "F1 Comert Stoc SRL", "F5 SRL Salariati SRL", "F6 Migrare Test SRL", "F7 Preluare Test SRL"
FISCALOS = "FISCALOS ICONTA S.R.L."
TOP = ".fereastra-overlay:not(.fundal) "
MINUS = "−"

STABIL = """() => new Promise((ok, rau) => { const t = setTimeout(() => rau(Error('pagina nedesenata')), 3000);
  requestAnimationFrame(() => requestAnimationFrame(() => { clearTimeout(t); ok(); })); })"""

DERULARI = """() => {
  const top = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra')].pop();
  if (!top) return null;
  const el = [top, ...top.querySelectorAll('*')].filter(e => {
    const s = getComputedStyle(e); if (!/(auto|scroll)/.test(s.overflowY + s.overflowX)) return false;
    return (e.scrollHeight > e.clientHeight + 2 || e.scrollWidth > e.clientWidth + 2) && e.getClientRects().length;
  });
  const corp = top.querySelector('.fereastra-corp');
  return {derulari: el.map(e => ({id: e.id, cls: String(e.className).slice(0, 80), sh: e.scrollHeight, ch: e.clientHeight, sw: e.scrollWidth, cw: e.clientWidth,
            xml: !!e.closest('.dec-xml-pre, pre, .dec-xml'), corp: e === corp})),
          corp: corp ? {sh: corp.scrollHeight, ch: corp.clientHeight} : null,
          primare: [...top.querySelectorAll('.buton-primar, .fj-principal')].filter(b => b.checkVisibility({checkOpacity: true})).map(b => b.innerText.trim()),
          bare: [...top.querySelectorAll('.bara-fixa, .fereastra-jos')].map(b => ({cls: String(b.className).slice(0, 80), rect: (r => [r.top, r.bottom])(b.getBoundingClientRect()),
                  pozitie: getComputedStyle(b).position})),
          zone: [...top.querySelectorAll('.zona-derulare, [class*=lant]')].map(z => ({cls: String(z.className).slice(0, 80), rect: (r => [r.top, r.bottom])(z.getBoundingClientRect()), sh: z.scrollHeight, ch: z.clientHeight})),
          viewport: [innerWidth, innerHeight], text: top.innerText.slice(0, 9000)};
}"""


def _pg(browser, w, h, email=CABINET):
    from core.ceas_proba import MOMENT_REF
    ctx = browser.new_context(viewport={"width": w, "height": h}, accept_downloads=True)
    ctx.clock.set_fixed_time(MOMENT_REF)
    ctx.add_init_script(conftest_e2e.sesiune(email))
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


def _top_text(pg):
    return pg.locator(TOP + ".fereastra").last.inner_text()


class Proba:
    def __init__(self, browser, director):
        self.b, self.dir, self.brut = browser, director, {}

    def captura(self, pg, nume, plin=False):
        f = self.dir / ("%s.png" % nume)
        pg.screenshot(path=str(f), full_page=plin)
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
            v = {"eroare": "%s: %s" % (type(e).__name__, str(e)[:600]), "urma": traceback.format_exc()[-1800:]}
        v["durata_s"] = round(time.time() - t0, 1)
        self.scrie(cheie, v)

    def pe_rezolutii(self, cheie, fn):
        out = {}
        for w, h in DIM:
            z = "%dx%d" % (w, h)
            ctx, pg = _pg(self.b, w, h)
            try:
                out[z] = fn(pg, z)
            except Exception as e:  # noqa: BLE001
                try:
                    cap = self.captura(pg, "%s_%s_eroare" % (cheie, z))
                except Exception:  # noqa: BLE001
                    cap = None
                out[z] = {"eroare": "%s: %s" % (type(e).__name__, str(e)[:500]), "captura": cap, "urma": traceback.format_exc()[-1200:]}
            finally:
                ctx.close()
        return out


def _firma(pg, nume, control):
    from e2e_ferestre_17_5_Q5 import firma
    if not pg.url.startswith("http"):
        pg.goto(os.environ["PROBA_BAZA"] + "/", wait_until="domcontentloaded")
    firma(pg, nume, control)
    pg.wait_for_timeout(1500)
    _stabil(pg)


def _la_luna(pg, rez, prev, nxt, tinta):
    """Duce fereastra la luna `tinta` („MM/AAAA”) citind luna afișată în `rez` și apăsând înapoi / înainte."""
    ti = (lambda m, a: int(a) * 12 + int(m))(*tinta.split("/"))
    for _ in range(18):
        t = pg.locator(TOP + rez).first.inner_text()
        m = re.search(r"(\d{2})/(\d{4})", t)
        if not m:
            pg.wait_for_timeout(800); continue
        cur = int(m.group(2)) * 12 + int(m.group(1))
        if cur == ti:
            return True
        pg.locator(TOP + (prev if cur > ti else nxt)).first.click()
        pg.wait_for_timeout(1500)
    return False


def _titlu(pg):
    return pg.evaluate("() => { const f = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra')].pop(); const t = f && f.querySelector('.fir-acum, .fereastra-titlu'); return t ? t.textContent.trim() : ''; }")


def _tenant(pg, nume):
    r = _api(pg, "/tenants")
    return next(t for t in r["date"]["tenants"] if t["nume"] == nume)


def _schema(nume):
    return conftest_e2e.sql("SELECT schema_name, id FROM public.tenants WHERE nume = %s", (nume,))[0]


# ── F015 — minusul real în Casă (refuzul de sold) și în Istoric facturi ─────────────────────────────────────────────────
def f015(P):
    def casa(pg, z):
        _firma(pg, F1, "#fa-casa")
        pg.locator(TOP + "button", has_text="Dispoziție nouă").first.click()
        pg.locator(TOP + "button", has_text="Plată furnizor").first.click()
        pg.wait_for_timeout(500)
        pg.fill(TOP + "#c-suma", "100000")
        pg.fill(TOP + "#c-part", "DANTE INTERNATIONAL SA")
        pg.fill(TOP + "#c-cui", "14399840")
        pg.wait_for_selector(TOP + "#c-avans", timeout=20000)
        pg.check(TOP + "#c-avans")
        if pg.locator(TOP + "#c-avans-dest").count():
            pg.select_option(TOP + "#c-avans-dest", "servicii")
        pg.fill(TOP + "#c-doc", "DPQ12")
        pg.wait_for_function("() => !!document.querySelector('.fereastra-overlay:not(.fundal) #c-previz-refuz')", timeout=15000)
        _stabil(pg)
        previz = pg.locator(TOP + "#c-previz-refuz").inner_text()
        pg.locator(TOP + "#c-adauga").click()
        pg.wait_for_timeout(2500); _stabil(pg)
        camp = pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) .msg-eroare[data-camp=\"c-suma\"]') || {}).textContent || ''")
        tabel = pg.evaluate("() => [...document.querySelectorAll('.fereastra-overlay .tn-tabel td.fd-td-num, .fereastra-overlay td')].map(t => t.textContent.trim()).filter(t => /^[−-]\\d/.test(t)).slice(0, 12)")
        return {"previz_refuz": previz, "refuz_camp": camp, "sume_negative_tabel": tabel, "captura": P.captura(pg, "F015_casa_%s" % z)}

    def istoric(pg, z):
        _firma(pg, F1, "#fa-facturi")
        pg.locator(TOP + "#fac-istoric").click()
        pg.wait_for_selector(TOP + "#fac-prev", state="attached")
        _la_luna(pg, ".pf-intro", "#fac-prev", "#fac-next", "10/2026")
        for _ in range(5):
            if not pg.locator(TOP + "#fac-mai-multe").count():
                break
            pg.locator(TOP + "#fac-mai-multe").click(); pg.wait_for_timeout(1500)
        _stabil(pg)
        sume = pg.evaluate("() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .pf-frand-suma')].map(s => s.textContent.trim())")
        api = _api(pg, "/tenants/%s/facturi?an=2026&luna=10&directie=emisa" % _tenant(pg, F1)["id"])
        return {"sume": sume, "api_total_negative": [f.get("total") for f in ((api.get("date") or {}).get("facturi") or []) if str(f.get("total", "")).startswith("-")],
                "captura": P.captura(pg, "F015_istoric_%s" % z)}
    return {"casa": P.pe_rezolutii("F015_casa", casa), "istoric": P.pe_rezolutii("F015_istoric", istoric)}


# ── F017 — încasarea pe soldul preluat: registrul și explicația notei ───────────────────────────────────────────────────
def f017(P):
    schema, tid = _schema(F1)
    vechi = "Încasare de la client — chitanța CHF1-5 — factura Sold la 31.08.2026 din 31.08.2026 — Client Test SRL"
    nota = conftest_e2e.sql("""SELECT i.id FROM "%s".inregistrari i WHERE i.status <> 'validata' AND i.data >= '2026-11-01' ORDER BY i.id LIMIT 1""" % schema)
    creata = None
    if not nota:
        creata = conftest_e2e.sql("""INSERT INTO "%s".inregistrari (data, descriere, status, sursa) VALUES ('2026-11-20', %%s, 'ciorna', 'casa') RETURNING id""" % schema, (vechi,))
        nid = creata[0][0]
    else:
        nid = nota[0][0]
        conftest_e2e.sql("""UPDATE "%s".inregistrari SET descriere = %%s WHERE id = %%s""" % schema, (vechi, nid))

    def jurnal(pg, z):
        _firma(pg, F1, "#fa-jurnal")
        _la_luna(pg, "#j-rezumat", "#j-prev", "#j-next", "11/2026")
        pg.wait_for_timeout(1000); _stabil(pg)
        rand = pg.evaluate("""(nid) => { const t = document.querySelector('.fereastra-overlay:not(.fundal) tbody[data-nota-id="' + nid + '"]');
            return t ? {text: t.innerText, original: t.getAttribute('data-text-original')} : null; }""", nid)
        return {"nota_id": nid, "rand": rand, "captura": P.captura(pg, "F017_jurnal_%s" % z)}
    return {"text_vechi_scris_pe_nota": vechi, "nota_creata_pe_copie": bool(creata), "jurnal": P.pe_rezolutii("F017", jurnal)}


# ── F018 — PDF-ul secundar al Partenerilor, funcțional (ierarhia: testul fundației e.1–e.3) ───────────────────────────────
def f018(P):
    def parteneri(pg, z):
        _firma(pg, F1, "#fa-parteneri")
        pg.wait_for_selector(TOP + "#pt-tabel tbody tr", state="attached"); _stabil(pg)
        pg.evaluate("() => { window.__tiparit = 0; window.print = () => { window.__tiparit++; }; }")
        pdf = pg.locator(TOP + "#pt-pdf")
        stare = pdf.evaluate("""b => { const r = b.getBoundingClientRect(); const e = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2);
            return {clase: [...b.classList], vizibil: b.checkVisibility({checkOpacity: true}), activ: !b.disabled, clicabil: !!e && b.contains(e),
                    in_bara: !!b.closest('.fereastra-jos')}; }""")
        pdf.click()
        pg.wait_for_timeout(300)
        tinta = pg.evaluate("() => ({tiparit: window.__tiparit, corp: document.body.classList.contains('tipareste-tabel'), tinta: !!document.querySelector('.tipareste-tinta')})")
        principale = pg.evaluate("() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fj-principal, .fereastra-overlay:not(.fundal) .buton-primar')].filter(b => b.checkVisibility({checkOpacity:true})).map(b => [b.id, b.innerText.trim(), !!b.closest('.fj-butoane')])")
        cap = P.captura(pg, "F018_parteneri_%s" % z)
        fis = None
        if z == "1366x768":
            pg.emulate_media(media="print")
            out = P.dir / "F018_parteneri_export.pdf"
            pg.pdf(path=str(out))
            fis = out.name
            pg.emulate_media(media="screen")
        return {"pdf": stare, "dupa_clic": tinta, "principale": principale, "captura": cap, "pdf_tiparit": fis}
    return P.pe_rezolutii("F018", parteneri)


# ── F022 / F169 — Control fiscal F1: Coerența TVA și notele în ciornă, 10/2026 și luna martor ──────────────────────────────
def _control(pg, luna):
    _firma(pg, F1, "#fa-control")
    pg.wait_for_selector(TOP + "#cf-incrucisat", state="attached", timeout=60000)
    sel = pg.locator(TOP + "#cf-luna-comparata")
    if sel.count() and sel.input_value() != luna:
        sel.select_option(luna); pg.wait_for_timeout(5000)
    _stabil(pg)


def f022_f169(P):
    def fn(pg, z):
        out = {}
        for luna in ("2026-10", "2026-9"):
            _control(pg, luna)
            pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) details').forEach(d => d.open = true)")
            pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) .ds-semnal-detalii-btn, .fereastra-overlay:not(.fundal) button[aria-expanded=\"false\"]').forEach(b => { try { b.click(); } catch (e) {} })")
            pg.wait_for_timeout(500); _stabil(pg)
            sect = pg.evaluate("""() => { const t = (s) => { const g = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .ds-grup, .fereastra-overlay:not(.fundal) section, .fereastra-overlay:not(.fundal) .cf-grup')]
                .find(x => (x.querySelector('h3, .ds-grup-titlu, .ds-sectiune-titlu') || {textContent: ''}).textContent.includes(s)); return g ? g.innerText : null; };
              return {coerenta: t('Coerență TVA'), incrucisat: (document.querySelector('.fereastra-overlay:not(.fundal) #cf-incrucisat') || {}).innerText || null,
                      note: [...document.querySelectorAll('.fereastra-overlay:not(.fundal) button.cf-nota')].map(b => [b.dataset.nota, b.parentElement.innerText.slice(0, 200)])}; }""")
            sect["captura"] = P.captura(pg, "F022_F169_%s_%s" % (z, luna))
            tid = _tenant(pg, F1)["id"]
            an, l = luna.split("-")
            api = _api(pg, "/control-fiscal/%s?an=%s&luna=%s" % (tid, an, l))
            vc = ((api.get("date") or {}).get("verificari_contabile") or {})
            sect["api_tva"] = vc.get("tva")
            sect["api_incrucisat"] = [{k: c.get(k) for k in ("cont", "stare", "declarat", "contabil", "diferenta", "reconciliere_ciorne", "explicatie_ciorne")}
                                      | {"ciorne": [{k: n.get(k) for k in ("nota_id", "document", "suma", "fel", "sens")} for n in (c.get("ciorne") or [])]}
                                      for c in ((vc.get("tva_incrucisat") or {}).get("constatari") or [])]
            out[luna] = sect
        try:
            # o legătură de notă: Registrul jurnal, cu nota evidențiată
            _control(pg, "2026-10")
            b = pg.locator(TOP + "button.cf-nota").first
            if b.count():
                pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) details').forEach(d => d.open = true)")
                nid = b.get_attribute("data-nota")
                b.evaluate("e => e.click()")
                pg.wait_for_timeout(4000); _stabil(pg)
                out["link_nota"] = {"nota_id": nid, "fereastra": _titlu(pg),
                                    "evidentiata": pg.evaluate("(nid) => !!document.querySelector('.fereastra-overlay:not(.fundal) tbody[data-nota-id=\"' + nid + '\"]')", nid),
                                    "captura": P.captura(pg, "F169_link_%s" % z)}
        except Exception as e:  # noqa: BLE001
            out["link_nota"] = {"eroare": str(e)[:300]}
        return out
    return P.pe_rezolutii("F022_F169", fn)


# ── F023 — prețul articolului, în câmpul românesc; intrarea manuală dă același total ───────────────────────────────────────
PRET = """() => { const e = document.querySelector('.fereastra-overlay:not(.fundal) #em-l0-pret_unitar');
  if (!e) return null; const nativ = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').get.call(e);
  const tot = document.querySelector('.fereastra-overlay:not(.fundal) #em-total, .fereastra-overlay:not(.fundal) .em-total');
  return {afisat: nativ, valoare: e.value, data_numar: e.getAttribute('data-numar'), total: tot ? tot.textContent.trim() : ''}; }"""


def f023(P):
    def fn(pg, z):
        _firma(pg, F1, "#fa-facturi")
        _api(pg, "/tenants/%s/ciorne-formular/factura" % _tenant(pg, F1)["id"], "DELETE")   # fără ciorna rulării de dinainte
        pg.evaluate("() => { for (const k of Object.keys(localStorage)) if (/ciorna/i.test(k)) localStorage.removeItem(k); }")
        pg.locator(TOP + "#fac-emite").click()
        pg.wait_for_selector(TOP + "#em-cui", state="attached"); pg.wait_for_timeout(1500)
        sel = pg.locator(TOP + "#em-l0-articol")
        opt = sel.locator("option", has_text="Marfa A").first
        sel.select_option(opt.get_attribute("value"))
        pg.wait_for_timeout(2500); _stabil(pg)
        m = {"articol": opt.inner_text(), "dupa_articol": pg.evaluate(PRET)}
        pg.locator(TOP + "#em-l0-cantitate").fill("1"); pg.wait_for_timeout(800)
        m["dupa_cantitate"] = pg.evaluate(PRET)
        m["captura"] = P.captura(pg, "F023_%s" % z)
        pg.locator(TOP + "#em-l0-pret_unitar").fill("100"); pg.wait_for_timeout(800)
        m["manual"] = pg.evaluate(PRET)
        return m
    return P.pe_rezolutii("F023", fn)


# ── F028 / F031 / F034 — Declarații: pasul 2 ────────────────────────────────────────────────────────────────────────────────
def _decl(pg, tip, an, luna):
    from declaratie_tip import alege_tipul
    _firma(pg, F1, "#fa-declaratii")
    pg.wait_for_selector(TOP + "#dec-tip", state="attached")
    alege_tipul(pg, tip, zona=TOP)
    pg.wait_for_selector(TOP + "#dec-an", timeout=10000)
    conftest_e2e.alege_perioada(pg, an, luna, zona=TOP)
    pg.locator(TOP + "#dec-continua").click()
    pg.wait_for_selector(TOP + "#dec-rezultat, " + TOP + ".dec-eroare", timeout=120000)
    pg.wait_for_timeout(1500); _stabil(pg)


def f028(P):
    def fn(pg, z):
        out = {}
        for luna in (9, 10):
            _decl(pg, "d112", 2026, luna)
            out["%02d" % luna] = {"titlu": pg.locator(TOP + ".rezumat-fix .mig-intro").last.inner_text(),
                                  "rezumat": pg.evaluate("() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .caseta-info li')].map(l => l.textContent)"),
                                  "xml_perioada": pg.evaluate("() => { const x = (document.querySelector('.fereastra-overlay:not(.fundal) .dec-xml-pre') || {}).textContent || ''; const m = x.match(/luna_r=\"(\\d+)\"[^>]*an_r=\"(\\d+)\"/); return m ? m.slice(1) : null; }"),
                                  "captura": P.captura(pg, "F028_d112_%02d_%s" % (luna, z))}
        return out
    return P.pe_rezolutii("F028", fn)


def f031(P):
    def fn(pg, z):
        _decl(pg, "d300", 2026, 10)
        pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) #dec-fata-balanta button[aria-expanded=\"false\"]').forEach(b => b.click())")
        pg.wait_for_timeout(500); _stabil(pg)
        fb = pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) #dec-fata-balanta') || {}).innerText || null")
        comp = pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) .dec-componente, .fereastra-overlay:not(.fundal) [id*=componente]') || {}).innerText || ''")
        legaturi = pg.evaluate("() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) #dec-fata-balanta [data-nota]')].map(b => b.textContent.trim())")
        m = {"fata_de_balanta": fb, "componente": comp[:3000], "legaturi_note": legaturi, "bara": pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) #dec-coada-mesaj') || {}).innerText || ''"),
             "derulari": pg.evaluate(DERULARI), "captura": P.captura(pg, "F031_d300_%s" % z)}
        b = pg.locator(TOP + "#dec-fata-balanta [data-nota]").first
        if b.count():
            b.evaluate("e => e.click()"); pg.wait_for_timeout(4000); _stabil(pg)
            m["link"] = {"fereastra": _titlu(pg), "captura": P.captura(pg, "F031_link_%s" % z)}
        return m
    return P.pe_rezolutii("F031", fn)


def f034(P):
    schema, tid = _schema(F1)
    ids = dict(conftest_e2e.sql("""SELECT numar, id FROM "%s".facturi WHERE numar IN ('BA-2', 'BA-3')""" % schema))

    def inainte(pg, z):
        _decl(pg, "d394", 2026, 10)
        der0 = pg.evaluate(DERULARI)   # pasul 2 cum se deschide (avertismentele pliate)
        pg.evaluate("() => { const c = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-corp'); c.scrollTop = c.scrollHeight; }")
        pg.wait_for_timeout(400); _stabil(pg)
        der_jos = pg.evaluate(DERULARI)   # și la capătul derulării
        pg.evaluate("() => { const c = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-corp'); c.scrollTop = 0; }")
        pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) .dec-avert button[aria-expanded=\"false\"]').forEach(b => b.click())")
        pg.wait_for_timeout(300); _stabil(pg)
        av = pg.evaluate("() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .dec-avert li, .fereastra-overlay:not(.fundal) .dec-avert .ds-semnal')].map(e => e.innerText.slice(0, 600))")
        scurte = pg.evaluate("() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .dec-avert .ds-semnal-text, .fereastra-overlay:not(.fundal) .dec-avert .ds-semnal')].map(e => (e.querySelector('.ds-semnal-text') || e).textContent.trim().slice(0, 300))")
        lat = pg.evaluate("""() => { const c = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .ds-tabel-cutie, .fereastra-overlay:not(.fundal) .zona-derulare')]
            .find(x => x.scrollWidth > x.clientWidth + 2); if (!c) return null; const rc = c.getBoundingClientRect();
            const lat = (e) => e.getBoundingClientRect().right > rc.right + 2;
            const frunze = [...c.querySelectorAll('*')].filter(e => lat(e) && ![...e.children].some(lat));
            return {cutie: String(c.className), sw: c.scrollWidth, cw: c.clientWidth, frunze: frunze.slice(0, 8).map(e => ({tag: e.tagName, cls: String(e.className).slice(0, 60),
                w: Math.round(e.getBoundingClientRect().width), sw: e.scrollWidth, text: (e.innerText || '').slice(0, 120), ws: getComputedStyle(e).whiteSpace,
                ow: getComputedStyle(e).overflowWrap, minw: getComputedStyle(e).minWidth, par: String(e.parentElement.className).slice(0, 60)}))}; }""")
        return {"avertismente": av, "texte_scurte": scurte, "derulari": der0, "derulari_la_capat": der_jos, "derulari_detalii_deschise": pg.evaluate(DERULARI), "lat": lat,
                "captura": P.captura(pg, "F034_d394_inainte_%s" % z)}

    def corectare(pg, z):
        _firma(pg, F1, "#fa-facturi")
        out = {}
        for nr, cod, jud in (("BA-2", "1001", None), ("BA-3", "1005", "IL")):
            pg.goto(os.environ["PROBA_BAZA"] + "/", wait_until="domcontentloaded")
            _firma(pg, F1, "#fa-facturi")
            api = _api(pg, "/tenants/%s/facturi/%s" % (tid, ids[nr]))
            out[nr] = {"api_inainte": {k: (api.get("date") or {}).get(k) for k in ("categorie_331", "tert_judet", "corectare_operatiune_n")}}
            refuz = _api(pg, "/tenants/%s/facturi/%s/operatiune-n" % (tid, ids[nr]), "POST", {"cod_nc": "", "judet": ""})
            out[nr]["refuz_fara_date"] = refuz
            r = _api(pg, "/tenants/%s/facturi/%s/operatiune-n" % (tid, ids[nr]), "POST", {"cod_nc": cod, "judet": jud or ""})
            out[nr]["corectare"] = r
        out["audit_log"] = conftest_e2e.sql("SELECT actiune, entitate_id, detalii::text FROM public.audit_log WHERE actiune = 'corectie_operatiune_n' ORDER BY id DESC LIMIT 2")
        return out

    def ecran_corectare(pg, z):
        # fișa BA-2 înainte de corectare: formularul (numai la prima rezoluție, înaintea corectării prin API)
        _firma(pg, F1, "#fa-facturi")
        pg.evaluate("""async ([tid, fid]) => { const m = await import('/static/js/ecrane/facturi_ecran.js'); }""", [tid, ids["BA-2"]])
        return {}

    def dupa(pg, z):
        _decl(pg, "d394", 2026, 10)
        x = pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) .dec-xml-pre') || {}).textContent || ''")
        anaf = pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) #dec-rezultat') || {}).innerText.slice(0, 1500)")
        return {"op_N": re.findall(r'<op1 [^>]*tip="N"[^>]*>\s*<op11[^>]*/>', x), "anaf": anaf, "derulari": pg.evaluate(DERULARI),
                "captura": P.captura(pg, "F034_d394_dupa_%s" % z)}
    out = {"inainte": P.pe_rezolutii("F034_inainte", inainte)}
    ctx, pg = _pg(P.b, 1366, 768)
    try:
        out["corectare"] = corectare(pg, "1366x768")
    finally:
        ctx.close()
    out["dupa"] = P.pe_rezolutii("F034_dupa", dupa)
    return out


# ── F034 — formularul corectării în fișa borderoului (înainte de corectare: altă rulare, aceeași bază) ──────────────────────
def f034_fisa(P):
    schema, tid = _schema(F1)
    fid = conftest_e2e.sql("""SELECT id FROM "%s".facturi WHERE numar = 'BA-3'""" % schema)[0][0]

    def fn(pg, z):
        _firma(pg, F1, "#fa-facturi")
        pg.evaluate("""async ([tid, fid]) => { const nav = window._navGlobal; const m = await import('/static/js/ecrane/facturi_ecran.js');
            if (m.deschideFactura) m.deschideFactura(nav, tid, fid); }""", [tid, fid])
        pg.wait_for_timeout(3000); _stabil(pg)
        return {"formular": pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) #fd-op-n') || {}).innerText || null"),
                "captura": P.captura(pg, "F034_fisa_%s" % z)}
    return P.pe_rezolutii("F034_fisa", fn)


# ── F045 — emiterea cu și fără adresa beneficiarului; refuzul 422 fără CUI, poziția casetei la 603 ─────────────────────────
def _emitere(pg):
    _firma(pg, F1, "#fa-facturi")
    _api(pg, "/tenants/%s/ciorne-formular/factura" % _tenant(pg, F1)["id"], "DELETE")
    pg.evaluate("() => { for (const k of Object.keys(localStorage)) if (/ciorna/i.test(k)) localStorage.removeItem(k); }")
    pg.locator(TOP + "#fac-emite").click()
    pg.wait_for_selector(TOP + "#em-cui", state="attached"); pg.wait_for_timeout(1500)


def _linie(pg):
    pg.fill(TOP + "#em-l0-descriere", "Servicii consultanta Q12")
    pg.wait_for_timeout(900)
    pg.fill(TOP + "#em-l0-cantitate", "1")
    pg.fill(TOP + "#em-l0-um", "buc")
    pg.fill(TOP + "#em-l0-pret_unitar", "100")
    if pg.locator(TOP + "select#em-l0-cota").count():
        pg.select_option(TOP + "select#em-l0-cota", "21")
    pg.wait_for_timeout(800)


CASETA = """() => { const b = document.querySelector('.fereastra-overlay:not(.fundal) .refuz-salvare'); const bara = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-jos');
  if (!b) return null; const r = b.getBoundingClientRect(), rb = bara ? bara.getBoundingClientRect() : null;
  const e = document.elementFromPoint(r.x + r.width / 2, r.y + Math.min(r.height / 2, 12));
  const c = b.closest('.fereastra-corp');
  return {caseta: [r.top, r.bottom], bara: rb ? [rb.top, rb.bottom] : null, deasupra_barei: rb ? r.bottom <= rb.top + 1 : true, in_viewport: r.top >= 0 && r.bottom <= innerHeight,
          hit: !!e && b.contains(e), text: b.innerText, in_corp: !!c, corp: c ? [c.scrollTop, c.scrollHeight, c.clientHeight, c.getBoundingClientRect().bottom] : null,
          parinte: String(b.parentElement.className), bara_in_corp: !!(bara && c && c.contains(bara))}; }"""


def f045(P):
    def fn(pg, z):
        out = {}
        _emitere(pg)
        pg.fill(TOP + "#em-nume", "Client Fara Cui Q12")
        _linie(pg)
        pg.evaluate("""() => { window.__sv = []; const o = Element.prototype.scrollIntoView; Element.prototype.scrollIntoView = function (a) {
            window.__sv.push([performance.now() | 0, this.tagName, String(this.className).slice(0, 40), JSON.stringify(a)]); return o.call(this, a); };
            window.__t = []; const t0 = performance.now(); const iv = setInterval(() => { const b = document.querySelector('.fereastra-overlay:not(.fundal) .refuz-salvare');
              const c = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-corp');
              window.__t.push([performance.now() - t0 | 0, b ? (r => [r.top | 0, r.bottom | 0])(b.getBoundingClientRect()) : null, c ? c.scrollTop : null,
                b ? String(b.parentElement.className) : null]); if (performance.now() - t0 > 4000) clearInterval(iv); }, 150); }""")
        pg.locator(TOP + "#em-emite").click()
        pg.wait_for_timeout(4200); _stabil(pg)
        out["fara_cui"] = {"caseta": pg.evaluate(CASETA), "urma": pg.evaluate("() => ({sv: window.__sv, t: window.__t})"), "captura": P.captura(pg, "F045_fara_cui_%s" % z)}
        _emitere(pg)
        pg.fill(TOP + "#em-cui", "403000015")
        pg.fill(TOP + "#em-nume", "Client Fara Adresa Q12")
        _linie(pg)
        pg.locator(TOP + "#em-emite").click()
        pg.wait_for_timeout(4000); _stabil(pg)
        out["fara_adresa"] = {"caseta": pg.evaluate(CASETA), "camp": pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) .msg-eroare[data-camp=\"em-adresa\"]') || {}).textContent || null"),
                              "rezultat": pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) #em-rezultat') || {}).innerText || ''"),
                              "captura": P.captura(pg, "F045_fara_adresa_%s" % z)}
        if z == "1366x768":
            pg.fill(TOP + "#em-adresa", "Str. Proba nr. 12, Cluj-Napoca")
            pg.wait_for_timeout(500)
            pg.locator(TOP + "#em-emite").click()
            pg.wait_for_timeout(2500)
            if pg.locator(TOP + "#em-pleaca-nu, " + TOP + "button:has-text('Nu')").count() and "Pleacă marfa" in _top_text(pg):
                pg.locator(TOP + "button:has-text('Nu')").first.click(); pg.wait_for_timeout(3000)
            _stabil(pg)
            rez = pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) #em-rezultat') || {}).innerText || ''")
            out["cu_adresa"] = {"rezultat": rez, "captura": P.captura(pg, "F045_cu_adresa_%s" % z)}
            schema, tid = _schema(F1)
            f = conftest_e2e.sql("""SELECT id, serie, numar, tert_adresa FROM "%s".facturi WHERE tert_nume = 'Client Fara Adresa Q12' ORDER BY id DESC LIMIT 1""" % schema)
            out["cu_adresa"]["factura"] = f
            if f:
                pdf = pg.evaluate("""async ([tid, fid]) => { const t = sessionStorage.getItem('iconta_token');
                    const r = await fetch('/tenants/' + tid + '/facturi/' + fid + '/pdf', {headers: {Authorization: 'Bearer ' + t}});
                    const b = new Uint8Array(await r.arrayBuffer()); let s = ''; for (const x of b) s += String.fromCharCode(x); return {status: r.status, octeti: b.length, b64: btoa(s)}; }""", [tid, f[0][0]])
                import base64
                (P.dir / "F045_factura.pdf").write_bytes(base64.b64decode(pdf.pop("b64") or ""))
                out["cu_adresa"]["pdf"] = dict(pdf, fisier="F045_factura.pdf")
        return out
    return P.pe_rezolutii("F045", fn)


# ── F070 — temeiul cu diacritice; duplicatul „Pâine albă” refuzat ───────────────────────────────────────────────────────────
def f070(P):
    def fn(pg, z):
        _firma(pg, F1, "#fa-produse")
        pg.wait_for_timeout(1500); _stabil(pg)
        inainte = pg.evaluate("() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .pr-rand-sub')].map(e => e.textContent.trim())")
        n0 = _api(pg, "/tenants/%s/produse" % _tenant(pg, F1)["id"])
        pg.locator(TOP + "button", has_text="Adaugă produs").first.click()
        pg.wait_for_timeout(800)
        camp = pg.locator(TOP + "input[id*='den'], " + TOP + "#pr-denumire").first
        camp.fill("Pâine albă")
        pg.wait_for_timeout(2500)
        pg.locator(TOP + "button", has_text="Salvează").first.click()
        pg.wait_for_timeout(2500); _stabil(pg)
        n1 = _api(pg, "/tenants/%s/produse" % _tenant(pg, F1)["id"])
        cnt = lambda r: len(r["date"] if isinstance(r.get("date"), list) else (r.get("date") or {}).get("produse") or [])
        return {"temeiuri_pe_rand": inainte, "mesaj": pg.evaluate("() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .msg-avert, .fereastra-overlay:not(.fundal) .msg-eroare, .fereastra-overlay:not(.fundal) .msg-info')].map(e => e.textContent).filter(Boolean)"),
                "produse_inainte": cnt(n0), "produse_dupa": cnt(n1), "captura": P.captura(pg, "F070_%s" % z)}
    return P.pe_rezolutii("F070", fn)


# ── F078 — F5, salariat nou cu CNP invalid: refuzul într-o singură derulare ──────────────────────────────────────────────
def f078(P):
    def fn(pg, z):
        _firma(pg, F5, "#fa-salariati")
        pg.locator(TOP + "button", has_text="Salariat nou").first.click()
        pg.wait_for_timeout(1500)
        cnp = pg.locator(TOP + "input[id*='cnp']").first
        cnp.fill("1234567890123")
        pg.locator(TOP + ".fj-principal, " + TOP + "button:has-text('Salvează')").first.click()
        pg.wait_for_timeout(3000); _stabil(pg)
        d = pg.evaluate(DERULARI)
        return {"derulari": d["derulari"] if d else None, "refuz": pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) .refuz-salvare') || {}).innerText || null"),
                "invalide": pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) [aria-invalid=\"true\"]').length"),
                "captura": P.captura(pg, "F078_%s" % z)}
    return {"603x590": P.pe_rezolutii("F078", fn).get("603x590")}


# ── F085 — F7, previzualizarea soldurilor pe parteneri: scadența documentată sau „termen necunoscut” ───────────────────────
FISIER_F085 = ("Cont;CUI;Denumire;Nr factura;Data factura;Data scadenta;Suma neachitata\n"
               "4111;14399840;DANTE INTERNATIONAL SA;66;10.07.2026;09.08.2026;600\n"
               "4111;14399840;DANTE INTERNATIONAL SA;71;20.07.2026;;400\n")


def f085(P):
    def fn(pg, z):
        from e2e_ferestre_17_5_Q5 import import_pas
        pg.goto(os.environ["PROBA_BAZA"] + "/", wait_until="domcontentloaded")
        import_pas(pg, F7, "Solduri parteneri", "input[type=file]")
        f = P.dir / "F085_parteneri.csv"
        f.write_text(FISIER_F085, encoding="utf-8")
        pg.locator(TOP + "input[type=file]").first.set_input_files(str(f))
        pg.wait_for_timeout(4000); _stabil(pg)
        tabel = pg.evaluate("""() => { const t = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) table')].find(x => x.innerText.includes('Scadență'));
            if (!t) return null; return [...t.rows].map(r => [...r.cells].map(c => c.innerText.trim())); }""")
        return {"tabel": tabel, "text": _top_text(pg)[:2500], "captura": P.captura(pg, "F085_%s" % z)}
    return P.pe_rezolutii("F085", fn)


# ── F126 / AC196 — Istoric facturi FISCALOS 11/2026: numele lungi pe mai multe rânduri, fără suprapunere ────────────────────
NUME_LUNG = "AMZUICĂ ȘI ASOCIAȚII CONSULTANȚĂ FISCALĂ, CONTABILITATE ȘI AUDIT FINANCIAR SOCIETATE CU RĂSPUNDERE LIMITATĂ"
RANDURI = """() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fac-frand-btn')].map(b => {
  const r = b.getBoundingClientRect(), n = b.querySelector('.pf-frand-nume'), s = b.querySelector('.pf-frand-sub'), m = b.querySelector('.pf-frand-suma');
  const R = (e) => { if (!e) return null; const x = e.getBoundingClientRect(); return [x.left, x.top, x.right, x.bottom]; };
  return {doc: b.dataset.doc, rand: R(b), nume: R(n), sub: R(s), suma: R(m), tr: R(b.closest('tr') || b), text: b.innerText};
})"""


def f126(P):
    schema, tid = _schema(FISCALOS)
    if not conftest_e2e.sql("""SELECT 1 FROM "%s".facturi WHERE serie = 'FIC' LIMIT 1""" % schema):
        for i in range(1, 6):
            nume = NUME_LUNG if i != 3 else "Client Scurt Q12 SRL"
            conftest_e2e.sql("""INSERT INTO "%s".facturi (serie, numar, data_emitere, directie, total, tva, moneda, status, tert_nume, tert_cui, tip)
                                VALUES ('FIC', %%s, %%s, 'emisa', %%s, 0, 'RON', 'emisa', %%s, '14399840', 'factura')""" % schema,
                             (str(i), "2026-11-%02d" % (2 + i), 100 * i, nume))

    def fn(pg, z, zoom=None):
        _firma(pg, FISCALOS, "#fa-facturi")
        pg.locator(TOP + "#fac-istoric").click()
        pg.wait_for_selector(TOP + "#fac-prev", state="attached")
        for _ in range(4):
            if "11/2026" in pg.locator(TOP + ".pf-intro").first.inner_text():
                break
            pg.locator(TOP + "#fac-prev").click(); pg.wait_for_timeout(1500)
        pg.wait_for_timeout(1000); _stabil(pg)
        rand = pg.evaluate(RANDURI)
        supra = []
        for a, b in zip(rand, rand[1:]):
            if a["rand"] and b["rand"] and a["rand"][3] > b["rand"][1] + 0.5:
                supra.append([a["doc"], b["doc"]])
            for k in ("nume", "sub", "suma"):
                if a[k] and b["rand"] and a[k][3] > b["rand"][1] + 0.5:
                    supra.append([a["doc"], k, b["doc"]])
        return {"viewport": pg.evaluate("() => [innerWidth, innerHeight, devicePixelRatio]"), "randuri": rand, "suprapuneri": supra,
                "captura": P.captura(pg, "F126_%s%s" % (z, "_zoom" if zoom else ""))}
    out = {"1366x768": None, "1366x768_zoom125": None}
    ctx, pg = _pg(P.b, 1366, 768)
    try:
        out["1366x768"] = fn(pg, "1366x768")
    finally:
        ctx.close()
    # zoomul 125% al ecranului de 1366×768: viewportul CSS e 1093×614 la scara 1,25 (zoomul din constatarea AC196 nu e cunoscut: se consemnează acesta)
    from core.ceas_proba import MOMENT_REF
    ctx = P.b.new_context(viewport={"width": 1093, "height": 614}, device_scale_factor=1.25)
    ctx.clock.set_fixed_time(MOMENT_REF); ctx.add_init_script(conftest_e2e.sesiune(CABINET))
    pg = ctx.new_page()
    try:
        out["1366x768_zoom125"] = fn(pg, "1366x768", zoom=1.25)
    finally:
        ctx.close()
    return out


# ── F139 — antetele NIR 3, întregi ──────────────────────────────────────────────────────────────────────────────────────
def f139(P):
    def fn(pg, z):
        _firma(pg, F1, "#fa-stocuri")
        pg.wait_for_timeout(1500)
        _la_luna(pg, ".rezumat-fix, .ds-rezumat", "button:has-text('← luna')", "button:has-text('luna →')", "10/2026")
        pg.locator(TOP + "button", has_text="NIR-uri în luna aleasă").first.click()
        pg.wait_for_selector(TOP + ".nir-deschide", state="attached")
        pg.locator(TOP + '.nir-deschide[data-numar="3"]').first.click()
        pg.wait_for_selector(TOP + "#nir-detaliu-linii", state="attached"); pg.wait_for_timeout(1500); _stabil(pg)
        th = pg.evaluate("""() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) #nir-detaliu-linii th')].map(t => ({text: t.innerText, sw: t.scrollWidth, cw: t.clientWidth,
            sh: t.scrollHeight, ch: t.clientHeight, ws: getComputedStyle(t).whiteSpace, ov: getComputedStyle(t).overflow, rect: (r => [r.width, r.height])(t.getBoundingClientRect())}))""")
        return {"antete": th, "captura": P.captura(pg, "F139_%s" % z)}
    return {"1366x768": P.pe_rezolutii("F139", fn).get("1366x768")}


# ── F179 — citirea SPV pe rezultat (transport controlat: răspunsul serverului e cel al lui `spv_receive.pe_rezultat`) ─────────
def f179(P):
    def fn(pg, z):
        _firma(pg, F1, "#fa-facturi")
        raspuns = {"citire": {"cif": "401002001", "zile": 10, "mesaje": 4, "eroare": None,
                              "pe_rezultat": {"gasite": 4, "importate": 1, "duplicate": 2, "refuzate": 1, "neimportate": 0}},
                   "stare": {"conectat": True, "acoperire": "acoperit", "cui": "401002001", "verificat_la": "2026-11-26T10:00:00+02:00", "mesaje": 4}}
        pg.route("**/spv/verifica-acum", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(raspuns)))
        pg.route("**/spv/stare", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(raspuns["stare"] | {"are_drept": True})))
        pg.locator(TOP + "button", has_text="Facturi primite").first.click()
        pg.wait_for_selector(TOP + "#fp-verifica", state="attached"); pg.wait_for_timeout(1500)
        pg.locator(TOP + "#fp-verifica").click()
        pg.wait_for_timeout(3000); _stabil(pg)
        return {"transport_controlat": raspuns["citire"], "text": pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) #fp-mesaj, .fereastra-overlay:not(.fundal) .msg-ok, .fereastra-overlay:not(.fundal) .msg-avert') || {}).innerText || ''"),
                "fereastra": _top_text(pg)[:2000], "captura": P.captura(pg, "F179_%s" % z)}
    return P.pe_rezolutii("F179", fn)


# ── F183 — F6, auditul de preluare: butonul deschide importul pe pasul lui; înapoi și rerulare ───────────────────────────────
def f183(P):
    def deschide(pg):
        _firma(pg, F6, "#fa-control")
        pg.wait_for_selector(TOP + "#cf-audit-zona", state="attached", timeout=60000)
        pg.wait_for_timeout(5000)
        n0 = pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) #cf-audit-zona button[data-ecran-destinatie]').length")
        if not n0:   # auditul păstrat pe copie e dinaintea butoanelor: o rulare nouă îl desenează cu ele
            pg.locator(TOP + "#cf-audit-run").first.click()
            pg.wait_for_function("() => !!document.querySelector('.fereastra-overlay:not(.fundal) #cf-audit-zona button[data-ecran-destinatie]')", timeout=60000)
        pg.wait_for_timeout(1000); _stabil(pg)
        return n0

    def fn(pg, z):
        n0 = deschide(pg)
        butoane = pg.evaluate("() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) #cf-audit-zona button[data-ecran-destinatie]')].map(b => [b.innerText.trim(), b.dataset.pas, (b.closest('li, .ds-semnal') || b.parentElement).innerText.slice(0, 300)])")
        pg.locator(TOP + "#cf-audit-zona button[data-ecran-destinatie]").first.scroll_into_view_if_needed(); _stabil(pg)
        out = {"butoane_la_deschidere": n0, "butoane": butoane, "captura_audit": P.captura(pg, "F183_audit_%s" % z)}
        for i in range(min(2, len(butoane))):
            if i:
                deschide(pg)
            b = pg.locator(TOP + "#cf-audit-zona button[data-ecran-destinatie]").nth(i)
            b.scroll_into_view_if_needed(); b.click()
            pg.wait_for_timeout(4000); _stabil(pg)
            out["clic_%d" % i] = {"buton": butoane[i][0], "fereastra": _titlu(pg),
                                  "pas_deschis": pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) .mig-intro, .fereastra-overlay:not(.fundal) h2') || {}).innerText || ''"),
                                  "captura": P.captura(pg, "F183_import_%d_%s" % (i, z))}
            for _ in range(3):   # înapoi până la Control fiscal (pasul de import, apoi meniul importului)
                if _titlu(pg) == "Control fiscal":
                    break
                pg.locator(TOP + ".nav-sageata.nav-inapoi:visible").first.click(); pg.wait_for_timeout(2500)
            out["clic_%d" % i]["dupa_inapoi"] = _titlu(pg)
            out["clic_%d" % i]["sageti"] = pg.evaluate("() => [...document.querySelectorAll('.nav-inapoi, .nav-sageata')].map(b => [String(b.className), b.checkVisibility(), !!b.closest('.fereastra-overlay:not(.fundal)'), b.textContent.trim()])")
            out["clic_%d" % i]["captura_inapoi"] = P.captura(pg, "F183_inapoi_%d_%s" % (i, z))
        r = pg.locator(TOP + "#cf-audit-run")
        if r.count():
            r.first.click(); pg.wait_for_timeout(8000); _stabil(pg)
            out["rerulare"] = {"text": (pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) #cf-audit-istoric') || {}).innerText || ''"))[:1500],
                               "butoane_dupa": pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) #cf-audit-zona button[data-ecran-destinatie]').length"),
                               "captura": P.captura(pg, "F183_rerulare_%s" % z)}
        return out
    return P.pe_rezolutii("F183", fn)


# ── F252 — fișa facturii la 603×590: titlul și semnele de ajutor F045 / F046, înainte și după derulare ───────────────────────
def f252(P):
    schema, tid = _schema(F1)
    fid = conftest_e2e.sql("""SELECT id FROM "%s".facturi WHERE serie = 'F1A' ORDER BY id DESC LIMIT 1""" % schema)[0][0]
    TINTE = """() => { const R = (e) => { const r = e.getBoundingClientRect(); const c = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2);
        return {rect: [r.left, r.top, r.right, r.bottom], hit: !!c && (e === c || e.contains(c)), deasupra: c ? (c.id || c.className) : null}; };
      const top = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-corp');
      const h = top.querySelector('h2.pf-titlu'), s = [...top.querySelectorAll('.semne-ajutor .semn-ajutor, .semne-ajutor button')];
      return {titlu: h ? Object.assign(R(h), {text: h.innerText}) : null, semne: s.map(x => Object.assign(R(x), {cod: x.dataset.cod || x.getAttribute('aria-label') || x.textContent})),
              scund: getComputedStyle(top).getPropertyValue('--antet-scund').trim()}; }"""

    def fn(pg, z):
        _firma(pg, F1, "#fa-facturi")
        pg.evaluate("""async ([tid, fid]) => { const m = await import('/static/js/ecrane/facturi_ecran.js'); if (m.deschideFactura) m.deschideFactura(window._navGlobal, tid, fid); }""", [tid, fid])
        pg.wait_for_timeout(3000); _stabil(pg)
        a = pg.evaluate(TINTE)
        cap_a = P.captura(pg, "F252_inainte_%s" % z)
        pg.evaluate("() => { const c = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-corp'); c.scrollTop = 400; }")
        pg.wait_for_timeout(500); _stabil(pg)
        b = pg.evaluate(TINTE)
        cap_b = P.captura(pg, "F252_dupa_derulare_%s" % z)
        ajutor = None
        s = pg.locator(TOP + ".semne-ajutor button, " + TOP + ".semne-ajutor .semn-ajutor").first
        if s.count():
            s.click(); pg.wait_for_timeout(1500)
            ajutor = pg.evaluate("() => (document.querySelector('.ajutor-panou, .fereastra-overlay:not(.fundal) .ajutor, [role=dialog]') || {}).innerText || null")
        return {"factura_id": fid, "inainte": a, "dupa_derulare": b, "ajutor": (ajutor or "")[:400], "capturi": [cap_a, cap_b, P.captura(pg, "F252_ajutor_%s" % z)]}
    return P.pe_rezolutii("F252", fn)


# ── AC189 — Verificări F1, Intrastat (valori controlate: răspunsul serverului fixat la 0 și 4.000,00) ───────────────────────
def ac189(P):
    def fn(pg, z):
        raspuns = {"an": 2026, "introduceri": {"cumulat": "0.00", "status": "sub_prag", "luna_depasirii": None, "procent": "0.0", "prag": "1000000"},
                   "expedieri": {"cumulat": "4000.00", "status": "sub_prag", "luna_depasirii": None, "procent": "0.4", "prag": "1000000"}, "nivel": None, "nota": ""}
        pg.route("**/intrastat-praguri**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(raspuns)))
        _firma(pg, F1, "#fa-verificari"); pg.wait_for_timeout(2500); _stabil(pg)
        txt = _top_text(pg)
        mi = re.search(r"Introduceri: ([^·]*?\)) ·", txt)
        me = re.search(r"Expedieri: ([^\n·]*?\))", txt)
        return {"sursa_numerica": raspuns, "introduceri_dom": mi.group(1) if mi else None, "expedieri_dom": me.group(1) if me else None, "captura": P.captura(pg, "AC189_%s" % z)}
    return P.pe_rezolutii("AC189", fn)


def test_probe_17_5_Q12():
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
    director = Path(CAPTURI) / "17_5_Q12_probe"
    director.mkdir(parents=True, exist_ok=True)
    P = Proba(browser, director)
    doar = [x for x in os.environ.get("Q12_SECTIUNI", "").split(",") if x]
    sectiuni = [("F015", f015), ("F017", f017), ("F018", f018), ("F022_F169", f022_f169), ("F023", f023), ("F028", f028), ("F031", f031),
                ("F034_fisa", f034_fisa), ("F034", f034), ("F045", f045), ("F070", f070), ("F078", f078), ("F085", f085), ("F126", f126),
                ("F139", f139), ("F179", f179), ("F183", f183), ("F252", f252), ("AC189", ac189)]
    for cheie, fn in sectiuni:
        if doar and cheie not in doar:
            continue
        P.sectiune(cheie, lambda fn=fn: fn(P))
    erori = {k: v["eroare"] for k, v in P.brut.items() if isinstance(v, dict) and "eroare" in v}
    print("PROBA_Q12 sectiuni:", len(P.brut), "erori:", json.dumps(erori, ensure_ascii=False)[:2000])
