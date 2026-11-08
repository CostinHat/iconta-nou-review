# uz: masoara.py <WxH> <tinta>...   (cu 8019 pornit; sesiunea de test a contului de dovadă)
import sys, os, json, importlib.util
RAD = os.path.expanduser("~/iconta_lot17_5")
sys.path.insert(0, RAD + "/scripts"); sys.path.insert(0, RAD)
import sesiune_test
from playwright.sync_api import sync_playwright
from core import ceas_proba
spec = importlib.util.spec_from_file_location("parcurs_lot", RAD + "/docs/dovezi/17_5/parcurs_17_5.py")
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
TOP = P.TOP

JS = r"""() => {
  const ov = [...document.querySelectorAll('.fereastra-overlay:not(.fundal)')].pop();
  if (!ov) return {eroare: 'fără fereastră'};
  const corp = ov.querySelector('.fereastra-corp'); const jos = ov.querySelector('.fereastra-jos');
  if (corp) corp.scrollTop = corp.scrollHeight;
  const vis = (e) => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.height > 0 && r.width > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const kids = corp ? [...corp.children].filter((e) => e !== jos && vis(e)) : [];
  const ultim = kids.length ? Math.max(...kids.map((e) => e.getBoundingClientRect().bottom)) : null;
  const cs = corp ? getComputedStyle(corp) : null;
  const deruleaza = [...ov.querySelectorAll('*')].filter((e) => vis(e) && e.scrollHeight > e.clientHeight + 1 && /(auto|scroll)/.test(getComputedStyle(e).overflowY))
    .map((e) => (e.id ? '#' + e.id : e.tagName.toLowerCase() + '.' + String(e.className).split(' ')[0]) + ' ' + e.scrollHeight + '/' + e.clientHeight);
  const lat = [...ov.querySelectorAll('*')].filter((e) => vis(e) && e.scrollWidth > e.clientWidth + 1 && !/^(svg|path)$/i.test(e.tagName) && getComputedStyle(e).overflowX !== 'visible')
    .map((e) => (e.id ? '#' + e.id : e.tagName.toLowerCase() + '.' + String(e.className).split(' ')[0]) + ' ' + e.scrollWidth + '/' + e.clientWidth).slice(0, 6);
  return {titlu: (ov.querySelector('.fir-acum') || {}).textContent, banda: (jos && ultim != null) ? Math.round(jos.getBoundingClientRect().top - ultim) : null,
    paddingJos: cs ? cs.paddingBottom : null, josH: jos ? Math.round(jos.getBoundingClientRect().height) : null, josPoz: jos ? getComputedStyle(jos).position : null, corpScroll: corp ? corp.scrollHeight + '/' + corp.clientHeight : null, deruleaza, lat,
    principal: [...ov.querySelectorAll('.fereastra-jos [data-actiune-principala]')].map((b) => b.textContent.trim()),
    butoaneJos: jos ? [...jos.querySelectorAll('button')].map((b) => b.textContent.trim()) : []};
}"""

def spv_conectat(pg):
    import json as _j
    cui = [{"cui": "40100%04d" % i, "nume": "Firma de proba %d SRL" % i, "are_drept": i % 3 != 0, "verificat_la": "2026-11-03T09:00:00"} for i in range(1, 13)]
    corp = _j.dumps({"conectat": True, "emitent_certificat": "CertSign", "access_expira": "2026-12-01T10:00:00", "cuiuri": cui, "explicatie_fara_drept": "Firmele fără drept în SPV nu pot fi conectate cu acest certificat."})
    pg.route("**/spv/stare", lambda r: r.fulfill(status=200, content_type="application/json", body=corp))
    setari_meniu(pg, "SPV")

def setari_meniu(pg, text):
    P.acasa(pg); pg.click(P.card("setari"), timeout=10000); pg.wait_for_selector(".set-meniu", timeout=20000)
    pg.locator(TOP + "button.meniu-card", has_text=text).first.click(timeout=10000); pg.wait_for_timeout(1500)

TINTE = {
  "firma": lambda pg: P.firma(pg, P.F1),
  "facturi": lambda pg: (P.firma(pg, P.F1), P.intra(pg, "fa-facturi", TOP + "#fac-emite")),
  "emite": lambda pg: (P.firma(pg, P.F1), P.intra(pg, "fa-facturi", TOP + "#fac-emite"), pg.click(TOP + "#fac-emite"), pg.wait_for_selector(TOP + "#em-data-scadenta, " + TOP + "input[type=date]", timeout=20000), pg.wait_for_timeout(1500)),
  "operatiuni": lambda pg: (P.firma(pg, P.F1), pg.click(TOP + "#fa-operatiuni"), pg.wait_for_timeout(1500)),
  "salariat": P.ecran_salariat, "parola": P.ecran_parola, "d104": P.ecran_d104, "plan": P.ecran_plan, "clienti": P.ecran_clienti, "casa": P.ecran_casa, "produse": P.ecran_produse, "tipare": P.ecran_tipare,
  "cabinet": lambda pg: setari_meniu(pg, "Date cabinet"),
  "gdpr": lambda pg: setari_meniu(pg, "(GDPR)"),
  "spv": lambda pg: setari_meniu(pg, "SPV"),
  "spvc": spv_conectat,
  "setari": lambda pg: (P.acasa(pg), pg.click(P.card("setari")), pg.wait_for_selector(".set-meniu"), pg.wait_for_timeout(800)),
}

def main(w, h, tinte):
    w_, h_ = map(int, w.split("x"))
    sc = sesiune_test.sesiune("dovada.71507@sesiuneab.test")
    with sync_playwright() as p:
        b = p.chromium.launch()
        try:
            for t in tinte:
                c = b.new_context(viewport={"width": w_, "height": h_}); c.clock.set_fixed_time(ceas_proba.MOMENT_REF); c.add_init_script(sc)
                pg = c.new_page(); pg.goto(os.environ.get("BAZA", "http://127.0.0.1:8019") + "/", wait_until="load", timeout=30000)
                try:
                    TINTE[t](pg); P.asteapta_principal(pg); pg.wait_for_timeout(500)
                    r = pg.evaluate(JS)
                    if len(sys.argv) > 0 and os.environ.get("EXTRA"):
                        r["extra"] = pg.evaluate(os.environ["EXTRA"])
                    if os.environ.get("CAPT"): pg.screenshot(path=os.environ["CAPT"] + "_%s_%s.png" % (t, w))
                except Exception as e:
                    r = {"eroare": "%s: %s" % (type(e).__name__, str(e).splitlines()[0][:150])}
                print(t, w, json.dumps(r, ensure_ascii=False)); c.close()
        finally:
            b.close()

main(sys.argv[1], None, sys.argv[2:]) if False else None
if __name__ == "__main__":
    w = sys.argv[1]
    main(w, None, sys.argv[2:])
