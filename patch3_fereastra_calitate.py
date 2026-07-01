#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch3_fereastra_calitate.py  —  PATCH 3 (frontend: Calitate in fereastra asistentului)

Inlocuieste corpul lui deschideVizualizare() in
  static/js/ecrane/asistenti.js
ca sa arate Calitate (3 cifre + rata + timp mediu + acoperire + motive) DEASUPRA
activitatii existente. Adauga CSS-ul aferent in static/stil.css.

Frontend pur: dupa aplicare doar Ctrl+Shift+R, fara restart backend.
Idempotent: marker + .bak. Localizeaza functia prin ancora de start si
detecteaza capatul prin numararea acoladelor (nu pe numere de linie).

RULARE (ca 'costin'):
  cd ~/iconta_nou
  /opt/iconta/venv/bin/python3 patch3_fereastra_calitate.py
"""
import os, shutil

BASE = "/home/costin/iconta_nou"
JS  = os.path.join(BASE, "static", "js", "ecrane", "asistenti.js")
CSS = os.path.join(BASE, "static", "stil.css")
MARKER = "/* [patch3_fereastra_calitate] */"
JS_MARKER = "// [patch3_fereastra_calitate]"
ANCORA = "async function deschideVizualizare(uid, nav) {"

FUNC_NOUA = JS_MARKER + '''
async function deschideVizualizare(uid, nav) {
  let d, c;
  try {
    [d, c] = await Promise.all([
      api.get(`/asistenti/${uid}/activitate`),
      api.get(`/asistenti/${uid}/calitate`),
    ]);
  } catch {
    alert("Nu am putut incarca fisa asistentului.");
    return;
  }
  if (!d.ok) return;
  const nume =
    [d.actor.prenume, d.actor.nume].filter(Boolean).join(" ") || `#${d.actor.id}`;
  const acte = d.activitate || [];

  nav.deschide(`Asistent \\u2014 ${nume}`, (box) => {
    const cal = c && c.ok ? c : null;
    const motive = ((cal && cal.motive) || [])
      .map((m) => `<div class="asi-cal-motiv"><span>${m.motiv}</span><span class="asi-cal-motiv-nr">${m.nr}\\u00d7</span></div>`)
      .join("") || `<div class="mig-gol">Nicio respingere.</div>`;
    const zile = cal && cal.zile_mediu != null ? `${cal.zile_mediu} zile` : "\\u2014";
    const blocCalitate = cal
      ? `
      <div class="asi-sectiune-titlu">Calitate</div>
      <div class="asi-cal-carduri">
        <div class="asi-cal-card"><div class="asi-cal-eticheta">Pregatite</div><div class="asi-cal-cifra">${cal.pregatite}</div></div>
        <div class="asi-cal-card"><div class="asi-cal-eticheta">Aprobate</div><div class="asi-cal-cifra asi-cal-verde">${cal.aprobate}</div></div>
        <div class="asi-cal-card"><div class="asi-cal-eticheta">Respinse</div><div class="asi-cal-cifra asi-cal-rosu">${cal.respinse} \\u00b7 ${cal.rata_respins}%</div></div>
      </div>
      <div class="asi-cal-rand2">
        <span>Timp mediu pregatit\\u2192aprobat: <b>${zile}</b></span>
        <span>Acoperire: <b>${(cal.tipuri || []).join(", ") || "\\u2014"}</b></span>
      </div>
      <div class="asi-cal-motive-titlu">Top motive de respingere</div>
      ${motive}`
      : `<div class="mig-gol">Calitatea nu a putut fi incarcata.</div>`;

    const alertaPatruOchi =
      d.nr_self_approval > 0
        ? `<div class="asi-alerta-rosu">\\u26a0 ${d.nr_self_approval} declaratii aprobate de aceeasi persoana care le-a pregatit (control patru ochi incalcat).</div>`
        : `<div class="asi-alerta-verde">\\u2713 Nicio declaratie aprobata de propriul pregatitor.</div>`;
    const randuri = acte.length
      ? acte
          .map((c2) => {
            const roluri = [];
            if (c2.a_pregatit) roluri.push("pregatit");
            if (c2.a_aprobat) roluri.push("aprobat");
            if (c2.a_respins) roluri.push("respins");
            const flag = c2.self_approval
              ? `<span class="asi-flag-rosu">si-a aprobat singur</span>`
              : "";
            return `
            <div class="asi-act-rand ${c2.self_approval ? "asi-act-rosu" : ""}">
              <div class="asi-act-tip">${c2.tip} \\u00b7 ${c2.perioada}</div>
              <div class="asi-act-meta">firma #${c2.tenant_id} \\u00b7 ${roluri.join(", ")} \\u00b7 stare: ${c2.stare} ${flag}</div>
            </div>`;
          })
          .join("")
      : `<div class="mig-gol">Nicio activitate inregistrata.</div>`;

    box.innerHTML = `
      ${blocCalitate}
      ${alertaPatruOchi}
      <div class="asi-sectiune-titlu">Declaratii lucrate (max. 200)</div>
      <div id="asi-activitate">${randuri}</div>
    `;
  });
}'''

CSS_NOU = '''

''' + MARKER + '''
.asi-cal-carduri { display:flex; gap:10px; margin:8px 0 12px; }
.asi-cal-card { flex:1; background:#f5f6f8; border-radius:8px; padding:10px 12px; }
.asi-cal-eticheta { font-size:12px; color:#5f5e5a; margin-bottom:4px; }
.asi-cal-cifra { font-size:22px; font-weight:500; }
.asi-cal-verde { color:#1d7a4d; }
.asi-cal-rosu  { color:#b3261e; }
.asi-cal-rand2 { display:flex; gap:18px; flex-wrap:wrap; font-size:13px; color:#444; margin-bottom:14px; }
.asi-cal-motive-titlu { font-size:13px; font-weight:500; color:#5f5e5a; margin:6px 0 8px; }
.asi-cal-motiv { display:flex; justify-content:space-between; font-size:13px; padding:5px 0; border-top:0.5px solid #e6e5e1; }
.asi-cal-motiv-nr { color:#5f5e5a; }
'''


def backup(path, suf):
    bak = path + suf
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        print("  .bak ->", bak)


def gaseste_capat(src, start):
    """Pornind de la prima '{' dupa pozitia start, intoarce indexul de dupa '}'
    care o inchide (numarare de acolade)."""
    i = src.index("{", start)
    adanc = 0
    while i < len(src):
        ch = src[i]
        if ch == "{":
            adanc += 1
        elif ch == "}":
            adanc -= 1
            if adanc == 0:
                return i + 1
        i += 1
    raise SystemExit("Nu am gasit capatul functiei (acolade dezechilibrate).")


def patch_js():
    src = open(JS, encoding="utf-8").read()
    if JS_MARKER in src:
        print("asistenti.js deja patch-at — sar.")
        return
    p = src.find(ANCORA)
    if p < 0:
        raise SystemExit("ANCORA LIPSA (deschideVizualizare) — opresc, nu ghicesc.")
    if src.count(ANCORA) != 1:
        raise SystemExit("ANCORA NEUNICA — opresc.")
    capat = gaseste_capat(src, p)
    backup(JS, ".bak_calitate")
    nou = src[:p] + FUNC_NOUA + src[capat:]
    open(JS, "w", encoding="utf-8").write(nou)
    print("  asistenti.js: deschideVizualizare inlocuita (Calitate + Activitate)")


def patch_css():
    src = open(CSS, encoding="utf-8").read()
    if MARKER in src:
        print("stil.css deja patch-at — sar.")
        return
    backup(CSS, ".bak_calitate")
    open(CSS, "w", encoding="utf-8").write(src.rstrip() + "\\n" + CSS_NOU)
    print("  stil.css: stiluri asi-cal-* adaugate")


def main():
    for p in (JS, CSS):
        if not os.path.exists(p):
            raise SystemExit("Lipseste: " + p)
    patch_js()
    patch_css()
    print("\\nGATA. Frontend pur — fa Ctrl+Shift+R in browser (fara restart backend).")
    print("Test: login Nistor -> card Asistenti -> Vizualizeaza -> apare blocul Calitate sus.")
    print("Rollback: muta .bak_calitate peste asistenti.js si stil.css.")


if __name__ == "__main__":
    main()
