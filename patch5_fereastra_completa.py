#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch5_fereastra_completa.py  —  PATCH 5 (fereastra asistentului pe macheta)

Inlocuieste deschideVizualizare (versiunea Patch 3) cu fereastra completa:
  - header: badge Nivel + semafor (rosu=sistematic, galben=drift, verde=ok) + rol
  - selector perioada (Tot/Azi/Luna/An) FUNCTIONAL pe Calitate (re-fetch /calitate)
  - Calitate: 3 carduri ORIZONTALE (layout inline -> bate orice regula globala)
  - Tipare sistematice si greseli noi: badge sistematic/accident + nou(drift)
  - Activitate (jos, neschimbata)
Frontend pur: dupa aplicare doar Ctrl+Shift+R.
Idempotent: marker + .bak. Inlocuire prin ancora + numarare de acolade.

NOTE (onest, fara mock):
  - Perioada guverneaza Calitatea (backend /calitate?de=&pana= exista).
    Activitatea ramane completa (activitate() nu are inca filtru perioada -> patch viitor).
  - Footer cu actiuni: omis. Editare/Dezactivare sunt deja in lista de asistenti.

RULARE (ca 'costin'):
  cd ~/iconta_nou
  /opt/iconta/venv/bin/python3 patch5_fereastra_completa.py
"""
import os, shutil

BASE = "/home/costin/iconta_nou"
JS  = os.path.join(BASE, "static", "js", "ecrane", "asistenti.js")
CSS = os.path.join(BASE, "static", "stil.css")
JS_MARKER = "// [patch5_fereastra_completa]"
CSS_MARKER = "/* [patch5_fereastra_completa] */"
ANCORA_PREV = "// [patch3_fereastra_calitate]"
ANCORA_FUNC = "async function deschideVizualizare(uid, nav) {"

FUNC = JS_MARKER + '''
async function deschideVizualizare(uid, nav) {
  const qp = (de, pana) => {
    const p = [];
    if (de) p.push("de=" + de);
    if (pana) p.push("pana=" + pana);
    return p.length ? "?" + p.join("&") : "";
  };
  const iso = (x) => x.toISOString().slice(0, 10);

  let d0;
  try { d0 = await api.get(`/asistenti/${uid}/activitate`); }
  catch { alert("Nu am putut incarca fisa."); return; }
  if (!d0.ok) return;
  const nume = [d0.actor.prenume, d0.actor.nume].filter(Boolean).join(" ") || `#${d0.actor.id}`;

  nav.deschide(`Asistent \\u2014 ${nume}`, (box) => {
    async function reincarca(de, pana) {
      let c;
      try { c = await api.get(`/asistenti/${uid}/calitate` + qp(de, pana)); }
      catch { c = null; }
      box.innerHTML = _asiRandeazaFereastra(d0, c);
    }
    box.addEventListener("change", (e) => {
      const t = e.target;
      if (!(t && t.classList && t.classList.contains("asi-per-sel"))) return;
      const azi = new Date();
      let de = null, pana = null;
      if (t.value === "azi") { de = iso(azi); pana = iso(azi); }
      else if (t.value === "luna") { de = iso(new Date(azi.getFullYear(), azi.getMonth(), 1)); pana = iso(azi); }
      else if (t.value === "an") { de = iso(new Date(azi.getFullYear(), 0, 1)); pana = iso(azi); }
      reincarca(de, pana);
    });
    reincarca(null, null);
  });
}

function _asiRandeazaFereastra(d, c) {
  const cal = c && c.ok ? c : null;
  const nivel = cal ? cal.nivel : 1;
  let sem = "verde";
  if (cal && (cal.tipare || []).some((t) => t.tip === "sistematic")) sem = "rosu";
  else if (cal && (cal.tipare || []).some((t) => t.nou)) sem = "galben";

  const header = `
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
      <span class="asi-nivel-badge">Nivel ${nivel}</span>
      <span class="asi-sem asi-sem-${sem}"></span>
      <span style="font-size:13px;color:#5f5e5a;">${d.actor.rol}</span>
    </div>`;

  const perioada = `
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
      <span style="font-size:13px;color:#5f5e5a;">Perioada:</span>
      <select class="asi-per-sel" style="width:auto;">
        <option value="tot">Tot</option>
        <option value="azi">Azi</option>
        <option value="luna">Luna curenta</option>
        <option value="an">Anul curent</option>
      </select>
    </div>`;

  const calitate = cal ? `
    <div class="asi-sectiune-titlu">Calitate</div>
    <div style="display:flex;gap:10px;margin:8px 0 12px;">
      <div class="asi-cal-card" style="flex:1;"><div class="asi-cal-eticheta">Pregatite</div><div class="asi-cal-cifra">${cal.pregatite}</div></div>
      <div class="asi-cal-card" style="flex:1;"><div class="asi-cal-eticheta">Aprobate</div><div class="asi-cal-cifra asi-cal-verde">${cal.aprobate}</div></div>
      <div class="asi-cal-card" style="flex:1;"><div class="asi-cal-eticheta">Respinse</div><div class="asi-cal-cifra asi-cal-rosu">${cal.respinse} \\u00b7 ${cal.rata_respins}%</div></div>
    </div>
    <div class="asi-cal-rand2">
      <span>Timp mediu pregatit\\u2192aprobat: <b>${cal.zile_mediu != null ? cal.zile_mediu + " zile" : "\\u2014"}</b></span>
      <span>Acoperire: <b>${(cal.tipuri || []).join(", ") || "\\u2014"}</b></span>
    </div>` : `<div class="mig-gol">Calitatea nu a putut fi incarcata.</div>`;

  let tipare = "";
  if (cal) {
    const lst = cal.tipare || [];
    const rows = lst.length ? lst.map((t) => {
      const bt = t.tip === "sistematic"
        ? `<span class="asi-badge asi-badge-rosu">sistematic</span>`
        : `<span class="asi-badge asi-badge-gri">accident</span>`;
      const bn = t.nou ? `<span class="asi-badge asi-badge-galben">nou</span>` : "";
      return `<div class="asi-cal-motiv"><span>${t.motiv}</span><span>${bt} ${bn} <b>${t.nr}\\u00d7</b></span></div>`;
    }).join("") : `<div class="mig-gol">Nicio respingere.</div>`;
    tipare = `<div class="asi-sectiune-titlu">Tipare sistematice si greseli noi</div>${rows}`;
  }

  const acte = d.activitate || [];
  const alerta = d.nr_self_approval > 0
    ? `<div class="asi-alerta-rosu">\\u26a0 ${d.nr_self_approval} declaratii aprobate de propriul pregatitor (patru ochi).</div>`
    : `<div class="asi-alerta-verde">\\u2713 Nicio declaratie aprobata de propriul pregatitor.</div>`;
  const randuri = acte.length ? acte.map((c2) => {
    const roluri = [];
    if (c2.a_pregatit) roluri.push("pregatit");
    if (c2.a_aprobat) roluri.push("aprobat");
    if (c2.a_respins) roluri.push("respins");
    const flag = c2.self_approval ? `<span class="asi-flag-rosu">si-a aprobat singur</span>` : "";
    return `<div class="asi-act-rand ${c2.self_approval ? "asi-act-rosu" : ""}"><div class="asi-act-tip">${c2.tip} \\u00b7 ${c2.perioada}</div><div class="asi-act-meta">firma #${c2.tenant_id} \\u00b7 ${roluri.join(", ")} \\u00b7 stare: ${c2.stare} ${flag}</div></div>`;
  }).join("") : `<div class="mig-gol">Nicio activitate inregistrata.</div>`;

  return `${header}${perioada}${calitate}${tipare}${alerta}<div class="asi-sectiune-titlu">Declaratii lucrate (max. 200)</div><div id="asi-activitate">${randuri}</div>`;
}'''

CSS_NOU = '''

''' + CSS_MARKER + '''
.asi-nivel-badge { font-size:13px; font-weight:500; background:#e6eefb; color:#1c4fa3; padding:3px 10px; border-radius:8px; }
.asi-sem { width:10px; height:10px; border-radius:50%; display:inline-block; }
.asi-sem-verde  { background:#1d7a4d; }
.asi-sem-galben { background:#c9961f; }
.asi-sem-rosu   { background:#b3261e; }
.asi-badge { font-size:11px; padding:1px 7px; border-radius:6px; }
.asi-badge-rosu   { background:#fae0de; color:#9c2a22; }
.asi-badge-galben { background:#fcf0d6; color:#8a6516; }
.asi-badge-gri    { background:#eceae3; color:#5f5e5a; }
'''


def backup(path, suf):
    bak = path + suf
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        print("  .bak ->", bak)


def gaseste_capat(src, start):
    i = src.index("{", start)
    adanc = 0
    while i < len(src):
        if src[i] == "{": adanc += 1
        elif src[i] == "}":
            adanc -= 1
            if adanc == 0: return i + 1
        i += 1
    raise SystemExit("Acolade dezechilibrate — opresc.")


def patch_js():
    src = open(JS, encoding="utf-8").read()
    if JS_MARKER in src:
        print("asistenti.js deja la Patch 5 — sar.")
        return
    # start = marker-ul Patch 3 daca exista, altfel direct functia
    p_marker = src.find(ANCORA_PREV)
    p_func = src.find(ANCORA_FUNC)
    if p_func < 0:
        raise SystemExit("ANCORA LIPSA (deschideVizualizare) — opresc.")
    if src.count(ANCORA_FUNC) != 1:
        raise SystemExit("ANCORA NEUNICA (deschideVizualizare) — opresc.")
    start = p_marker if (0 <= p_marker < p_func) else p_func
    capat = gaseste_capat(src, p_func)
    backup(JS, ".bak_p5")
    nou = src[:start] + FUNC + src[capat:]
    open(JS, "w", encoding="utf-8").write(nou)
    print("  asistenti.js: fereastra completa (Patch 5)")


def patch_css():
    src = open(CSS, encoding="utf-8").read()
    if CSS_MARKER in src:
        print("stil.css deja la Patch 5 — sar.")
        return
    backup(CSS, ".bak_p5")
    open(CSS, "w", encoding="utf-8").write(src.rstrip() + "\\n" + CSS_NOU)
    print("  stil.css: nivel/semafor/badge adaugate")


def main():
    for p in (JS, CSS):
        if not os.path.exists(p):
            raise SystemExit("Lipseste: " + p)
    patch_js()
    patch_css()
    print("\\nGATA. Frontend pur — Ctrl+Shift+R in browser.")
    print("Rollback: muta .bak_p5 peste asistenti.js si stil.css.")


if __name__ == "__main__":
    main()
