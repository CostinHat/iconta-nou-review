# -*- coding: utf-8 -*-
"""UNEALTA 2 — emulare de dispozitiv mobil (Pixel 5: touch, fara hover, viewport ingust).
Acelasi traseu ca axe (nav_ecrane.ECRANE). Raporteaza, cu CIFRE, ce devine INACCESIBIL
pe telefon fata de desktop:

  (A) HOVER-ONLY prin title  = tooltip-ul title apare doar la hover cu mouse; pe touch NU
        exista hover -> continutul title e de neatins. Se numara TOATE [title], din care
        cele care cara INFORMATIE UNICA (fara aria si fara acelasi text vizibil) — pierdere reala.
  (B) HOVER-ONLY prin CSS    = elemente ascunse implicit pe care o regula :hover le arata
        (display/visibility/opacity). Pe touch nu se declanseaza -> ramin ascunse.
  (C) TINTE DE ATINGERE MICI  = elemente interactive sub 44x44 px (prag WCAG 2.5.5 / Apple).
  (D) OVERFLOW ORIZONTAL      = pagina mai lata decat ecranul (scroll lateral) + elementele vinovate.

NU repara nimic. Scrie raport_mobil.txt + .json + capturi mobil_<ecran>.png.
"""
import os, json, traceback
from playwright.sync_api import sync_playwright
from w_auth import INIT
from nav_ecrane import ECRANE

HERE = os.path.dirname(os.path.abspath(__file__))

# (A) title -> pierdut pe touch; marcheaza care cara info unica
HOVER_TITLE_JS = r"""() => {
  const norm = s => (s||'').toLowerCase().replace(/\s+/g,' ').trim();
  let total = 0; const unice = [];
  for (const e of document.querySelectorAll('[title]')) {
    const t = (e.getAttribute('title')||'').trim(); if (!t) continue;
    total++;
    const aria = e.getAttribute('aria-label') || e.getAttribute('aria-labelledby');
    const vis = (e.innerText || e.textContent || '').trim();
    const acc = norm((aria||'') + ' ' + vis);
    // info unica: title-ul NU e deja in numele accesibil (aria + vizibil)
    if (!acc.includes(norm(t))) unice.push({
      tag:e.tagName.toLowerCase(), cls:(e.className||'').toString().slice(0,40),
      title:t.slice(0,70), vizibil:vis.slice(0,26), are_aria: !!aria});
  }
  return {total_title: total, unice};
}"""

# (B) reguli CSS :hover care schimba vizibilitatea
HOVER_CSS_JS = r"""() => {
  const reg = [];
  for (const ss of document.styleSheets) {
    let rules; try { rules = ss.cssRules; } catch(e) { continue; }
    if (!rules) continue;
    for (const r of rules) {
      if (!r.selectorText || !r.selectorText.includes(':hover')) continue;
      const ct = (r.style && r.style.cssText || '');
      if (/display|visibility|opacity|max-height|transform|left|right|top|bottom/.test(ct)) {
        // selectorul de baza fara :hover -> cate elemente pe pagina
        const baza = r.selectorText.replace(/:hover/g, '').trim();
        let n = 0; try { n = document.querySelectorAll(baza).length; } catch(e) {}
        reg.push({sel: r.selectorText.slice(0,70), decl: ct.slice(0,60), elemente: n});
      }
    }
  }
  return reg;
}"""

# (C) tinte de atingere mici (<44) si (D) overflow orizontal
TAP_OVERFLOW_JS = r"""() => {
  const W = window.innerWidth;
  const mici = [];
  for (const e of document.querySelectorAll(
      'button, a[href], input:not([type=hidden]), select, [role=button], [onclick]')) {
    const r = e.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;      // ascuns -> nu conteaza ca tinta
    if (r.width < 44 || r.height < 44) mici.push({
      tag:e.tagName.toLowerCase(), cls:(e.className||'').toString().slice(0,34),
      w:Math.round(r.width), h:Math.round(r.height),
      txt:(e.innerText||e.textContent||'').trim().slice(0,20)});
  }
  // overflow orizontal
  const late = [];
  const doc = document.documentElement;
  const overflow = doc.scrollWidth > W + 2;
  if (overflow) {
    for (const e of document.querySelectorAll('*')) {
      const r = e.getBoundingClientRect();
      if (r.right > W + 2 && r.width > 20 && r.width <= W*2) late.push({
        tag:e.tagName.toLowerCase(), cls:(e.className||'').toString().slice(0,34),
        right:Math.round(r.right), w:Math.round(r.width)});
      if (late.length > 12) break;
    }
  }
  return {viewport: W, tinte_mici: mici, overflow_orizontal: overflow,
          scrollWidth: doc.scrollWidth, elemente_late: late};
}"""


def main():
    raport = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        pixel5 = pw.devices["Pixel 5"]
        for nume, nav in ECRANE:
            ctx = b.new_context(**pixel5)     # touch=True, isMobile=True, viewport 393x851
            ctx.add_init_script(INIT)
            pg = ctx.new_page()
            r = {"ecran": nume}
            try:
                nav(pg)
                r["titlu"] = pg.eval_on_selector_all("h1,h2", "e=>e.map(x=>x.textContent.trim()).slice(0,2)")
                r["hover_title"] = pg.evaluate(HOVER_TITLE_JS)
                r["hover_css"] = pg.evaluate(HOVER_CSS_JS)
                r["tap_overflow"] = pg.evaluate(TAP_OVERFLOW_JS)
                r["ok"] = True
                pg.screenshot(path=os.path.join(HERE, "mobil_%s.png" % nume), full_page=True)
            except Exception as e:
                r["ok"] = False
                r["error"] = str(e).splitlines()[0][:140]
                traceback.print_exc()
                try:
                    pg.screenshot(path=os.path.join(HERE, "mobil_%s_ERR.png" % nume), full_page=True)
                except Exception:
                    pass
            raport.append(r)
            ctx.close()
        b.close()

    linii = ["=== RAPORT emulare MOBIL (Pixel 5: touch, fara hover, 393px) — 5 ecrane ===", ""]
    linii.append("%-22s %8s %10s %8s %9s %10s" % (
        "ECRAN", "TITLE", "TITLE-UNIC", "CSS:hov", "TAP<44", "OVERFLOW-X"))
    for r in raport:
        if not r.get("ok"):
            linii.append("%-22s  EROARE: %s" % (r["ecran"], r.get("error"))); continue
        ht, hc, to = r["hover_title"], r["hover_css"], r["tap_overflow"]
        linii.append("%-22s %8d %10d %8d %9d %10s" % (
            r["ecran"], ht["total_title"], len(ht["unice"]),
            sum(1 for x in hc if x["elemente"] > 0), len(to["tinte_mici"]),
            ("DA(%d)" % to["scrollWidth"]) if to["overflow_orizontal"] else "nu"))
    linii.append("")
    for r in raport:
        if not r.get("ok"):
            continue
        linii.append("--- %s ---" % r["ecran"])
        linii.append("  HOVER-ONLY prin title, info UNICA pierduta pe touch (%d):"
                     % len(r["hover_title"]["unice"]))
        for u in r["hover_title"]["unice"][:8]:
            linii.append("     <%s.%s> title=%r (vizibil=%r, aria=%s)"
                         % (u["tag"], u["cls"], u["title"], u["vizibil"], u["are_aria"]))
        hc_activ = [x for x in r["hover_css"] if x["elemente"] > 0]
        linii.append("  HOVER-ONLY prin CSS :hover (reguli cu elemente pe pagina: %d):" % len(hc_activ))
        for x in hc_activ[:6]:
            linii.append("     %s { %s } -> %d elem" % (x["sel"], x["decl"], x["elemente"]))
        to = r["tap_overflow"]
        linii.append("  TINTE DE ATINGERE <44px: %d ; OVERFLOW-X: %s (scrollWidth=%d, viewport=%d)"
                     % (len(to["tinte_mici"]), to["overflow_orizontal"], to["scrollWidth"], to["viewport"]))
        for t in to["tinte_mici"][:5]:
            linii.append("     mic <%s.%s> %dx%d %r" % (t["tag"], t["cls"], t["w"], t["h"], t["txt"]))
        for e in to["elemente_late"][:4]:
            linii.append("     lat <%s.%s> right=%d w=%d" % (e["tag"], e["cls"], e["right"], e["w"]))
        linii.append("")
    txt = "\n".join(linii)
    open(os.path.join(HERE, "raport_mobil.txt"), "w", encoding="utf-8").write(txt)
    print(txt)
    open(os.path.join(HERE, "raport_mobil.json"), "w", encoding="utf-8").write(
        json.dumps(raport, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
