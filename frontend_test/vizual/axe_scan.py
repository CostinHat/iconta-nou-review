# -*- coding: utf-8 -*-
"""UNEALTA 1 — axe-core injectat in pagina randata cu Playwright.
Ruleaza pe cele 5 ecrane problematice (nav_ecrane.ECRANE) si raporteaza, cu CIFRE:
  - violarile axe grupate pe impact (critical/serious/moderate/minor) si pe regula;
  - cele trei interese ale lui Costin, extrase explicit:
      (a) CONTRAST      = regula axe 'color-contrast' (+ 'color-contrast-enhanced')
      (b) FARA ETICHETA = regulile 'label','select-name','aria-input-field-name',
                          'button-name','link-name','input-button-name'
      (c) TITLE-ONLY    = informatie livrata EXCLUSIV prin atributul title
                          (element cu title negol, fara text vizibil, fara aria-label/labelledby)
                          — check DOM custom, complementar axe (axe n-are regula directa).

NU repara nimic. Doar masoara. Scrie si un raport text linga scripturi: raport_axe.txt.
axe.min.js e vandorizat local (v4.10.2) -> offline, reproductibil.
"""
import os, json, traceback
from playwright.sync_api import sync_playwright
from w_auth import INIT
from nav_ecrane import ECRANE

HERE = os.path.dirname(os.path.abspath(__file__))
AXE = open(os.path.join(HERE, "axe.min.js"), encoding="utf-8").read()

CONTRAST_RULES = {"color-contrast", "color-contrast-enhanced"}
LABEL_RULES = {"label", "select-name", "aria-input-field-name", "button-name",
               "link-name", "input-button-name", "label-title-only", "form-field-multiple-labels"}

TITLE_ONLY_JS = r"""() => {
  // Doua categorii de 'informatie livrata exclusiv prin title':
  //  strict = title negol, ZERO text vizibil, fara aria -> axe nici n-o vede ca nume
  //  glif   = title negol, fara aria, vizibil doar un GLIF (<=2 car / doar simbol / doar cifre)
  //           -> numele real e in title; pe touch (fara hover) ramane doar glif-ul.
  const strict = [], glif = [], extra = [];
  const eGlif = s => !s || s.length <= 2 || /^[^\p{L}\p{N}]+$/u.test(s) || /^\d+$/.test(s);
  const norm = s => (s||'').toLowerCase().replace(/\s+/g,' ').trim();
  for (const e of document.querySelectorAll('[title]')) {
    const t = (e.getAttribute('title')||'').trim();
    if (!t) continue;
    const aria = e.getAttribute('aria-label') || e.getAttribute('aria-labelledby');
    const vis = (e.innerText || e.textContent || '').trim();
    const rec = {tag: e.tagName.toLowerCase(),
                 cls: (e.className||'').toString().slice(0,44),
                 title: t.slice(0,60), vizibil: vis.slice(0,24)};
    if (aria) continue;                 // numele accesibil vine din aria -> nu e title-only
    if (!vis) { strict.push(rec); continue; }          // title, zero text -> title-only strict
    if (eGlif(vis)) { glif.push(rec); continue; }       // vizibil doar glif -> nume real in title
    // vizibil are eticheta reala, dar title cara ALTA informatie (nu e in eticheta):
    if (!norm(vis).includes(norm(t)) && !norm(t).includes(norm(vis))) extra.push(rec);
  }
  return {strict, glif, extra};
}"""

AXE_RUN_JS = """async () => {
  const r = await axe.run(document, {
    runOnly: {type:'tag', values:['wcag2a','wcag2aa','wcag21a','wcag21aa']},
    resultTypes: ['violations']
  });
  return r.violations.map(v => ({
    id: v.id, impact: v.impact, help: v.help,
    n: v.nodes.length,
    exemple: v.nodes.slice(0,3).map(nd => (nd.target||[]).join(' ').slice(0,80))
  }));
}"""


def scaneaza(pg):
    pg.evaluate(AXE)                       # defineste window.axe
    viol = pg.evaluate(AXE_RUN_JS)         # lista violarilor
    title_only = pg.evaluate(TITLE_ONLY_JS)
    return viol, title_only


def main():
    raport = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        for nume, nav in ECRANE:
            ctx = b.new_context(viewport={"width": 1280, "height": 1800})
            ctx.add_init_script(INIT)
            pg = ctx.new_page()
            r = {"ecran": nume}
            try:
                nav(pg)
                viol, title_only = scaneaza(pg)
                impact = {}
                for v in viol:
                    impact[v["impact"] or "necunoscut"] = impact.get(v["impact"] or "necunoscut", 0) + v["n"]
                r["total_reguli_incalcate"] = len(viol)
                r["total_noduri"] = sum(v["n"] for v in viol)
                r["pe_impact"] = impact
                r["contrast_noduri"] = sum(v["n"] for v in viol if v["id"] in CONTRAST_RULES)
                r["fara_eticheta_noduri"] = sum(v["n"] for v in viol if v["id"] in LABEL_RULES)
                r["title_strict_noduri"] = len(title_only["strict"])
                r["title_glif_noduri"] = len(title_only["glif"])
                r["title_extra_noduri"] = len(title_only["extra"])
                r["title_exemple"] = (title_only["strict"] + title_only["glif"] + title_only["extra"])[:12]
                r["violari"] = sorted(viol, key=lambda v: -v["n"])
                r["ok"] = True
            except Exception as e:
                r["ok"] = False
                r["error"] = str(e).splitlines()[0][:140]
                traceback.print_exc()
            raport.append(r)
            ctx.close()
        b.close()

    # raport text compact
    linii = ["=== RAPORT axe-core (v4.10.2, wcag2a+2aa+21) — 5 ecrane ===", ""]
    linii.append("%-22s %6s %6s %8s %9s %8s %7s %7s" % (
        "ECRAN", "REGULI", "NODURI", "CONTRAST", "FARA-ETIC", "T-STRICT", "T-GLIF", "T-EXTRA"))
    for r in raport:
        if not r.get("ok"):
            linii.append("%-22s  EROARE: %s" % (r["ecran"], r.get("error"))); continue
        linii.append("%-22s %6d %6d %8d %9d %8d %7d %7d" % (
            r["ecran"], r["total_reguli_incalcate"], r["total_noduri"],
            r["contrast_noduri"], r["fara_eticheta_noduri"],
            r["title_strict_noduri"], r["title_glif_noduri"], r["title_extra_noduri"]))
    linii.append("")
    for r in raport:
        if not r.get("ok"):
            continue
        linii.append("--- %s (impact: %s) ---" % (r["ecran"], r["pe_impact"]))
        for v in r["violari"]:
            linii.append("   %-28s x%-4d [%s] %s" % (v["id"], v["n"], v["impact"], v["help"][:60]))
        if r["title_exemple"]:
            linii.append("   TITLE (strict %d / glif %d / extra %d) exemple:" % (
                r["title_strict_noduri"], r["title_glif_noduri"], r["title_extra_noduri"]))
            for e in r["title_exemple"]:
                linii.append("      <%s class=%r> title=%r vizibil=%r" % (
                    e["tag"], e["cls"], e["title"], e.get("vizibil", "")))
        linii.append("")
    txt = "\n".join(linii)
    open(os.path.join(HERE, "raport_axe.txt"), "w", encoding="utf-8").write(txt)
    print(txt)
    print("\n=== JSON complet -> raport_axe.json ===")
    open(os.path.join(HERE, "raport_axe.json"), "w", encoding="utf-8").write(
        json.dumps(raport, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
