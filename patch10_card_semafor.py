#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch10_card_semafor.py — frontend: banner semafor echipa + drill erori +
bulina semafor pe cardul dashboard."""
import os, shutil

BASE = "/home/costin/iconta_nou"
ASI = os.path.join(BASE, "static", "js", "ecrane", "asistenti.js")
CAB = os.path.join(BASE, "static", "js", "ecrane", "cabinet.js")
CSS = os.path.join(BASE, "static", "stil.css")
M_ASI = "/* [patch10_banner_erori] */"
M_CAB = "/* [patch10_card_sem] */"
M_CSS = "/* [patch10_card_sem] */"
NL = chr(10)


def backup(p, suf):
    b = p + suf
    if not os.path.exists(b):
        shutil.copy2(p, b); print("  .bak ->", b)


def once(t, old, new, label):
    if old not in t: raise SystemExit("ANCORA LIPSA: " + label)
    if t.count(old) != 1: raise SystemExit("ANCORA NEUNICA: " + label)
    return t.replace(old, new)


# ---- 1. asistenti.js: container banner + apel + functiile noi ----
# 1a. adaug <div id="asi-banner"> in corp + apel _asiBannerEchipa
ASI_OLD1 = '''    <div class="asi-sumar">${sumar.total} asistenț${sumar.total === 1 ? "ă" : "i"} · ${sumar.activi} activ${sumar.activi === 1 ? "" : "i"}</div>
    <div id="asi-lista"></div>'''
ASI_NEW1 = '''    <div class="asi-sumar">${sumar.total} asistenț${sumar.total === 1 ? "ă" : "i"} · ${sumar.activi} activ${sumar.activi === 1 ? "" : "i"}</div>
    <div id="asi-banner"></div>
    <div id="asi-lista"></div>'''

ASI_OLD2 = '''  const lista = corp.querySelector("#asi-lista");
  /* [patch8_lista_dez] */'''
ASI_NEW2 = '''  _asiBannerEchipa(corp, nav);
  const lista = corp.querySelector("#asi-lista");
  /* [patch8_lista_dez] */'''

# 1b. functiile noi la final de fisier
ASI_FUNCS = NL + NL + M_ASI + NL + '''async function _asiBannerEchipa(corp, nav) {
  let s;
  try { s = await api.get("/asistenti/echipa/semafor"); } catch { return; }
  if (!s || !s.ok) return;
  const host = corp.querySelector("#asi-banner");
  if (!host) return;
  const cnt = s.counts || {};
  const detalii = [];
  if (cnt.rosu) detalii.push(`${cnt.rosu} cu tipare`);
  if (cnt.galben) detalii.push(`${cnt.galben} de urmarit`);
  if (cnt.verde) detalii.push(`${cnt.verde} ok`);
  const text = detalii.length ? detalii.join(" \u00b7 ") : "fara activitate recenta";
  const areErori = (cnt.rosu || 0) + (cnt.galben || 0) > 0;
  host.innerHTML = `
    <div class="asi-echipa-banner">
      <span class="asi-sem asi-sem-${s.culoare}"></span>
      <span class="asi-echipa-text">Calitatea echipei (${s.zile} zile): ${text}</span>
      ${areErori ? `<button class="asi-echipa-btn" id="asi-vezi-erori">Vezi erorile</button>` : ""}
    </div>`;
  const b = host.querySelector("#asi-vezi-erori");
  if (b) b.onclick = () => deschideEchipaErori(nav);
}

async function deschideEchipaErori(nav) {
  let d;
  try { d = await api.get("/asistenti/echipa/erori"); }
  catch { alert("Nu am putut incarca erorile."); return; }
  if (!d.ok) return;
  nav.deschide("Erori \u2014 echipa", (box) => {
    const lst = d.asistenti || [];
    if (!lst.length) {
      box.innerHTML = `<div class="asi-alerta-verde">\u2713 Nicio respingere in ultimele ${d.zile} zile.</div>`;
      return;
    }
    const carduri = lst.map((a) => {
      const tipare = (a.tipare || []).map((t) => {
        const bt = t.tip === "sistematic"
          ? `<span class="asi-badge asi-badge-rosu">sistematic</span>`
          : `<span class="asi-badge asi-badge-gri">accident</span>`;
        const bn = t.nou ? `<span class="asi-badge asi-badge-galben">nou</span>` : "";
        return `<div class="asi-cal-motiv"><span>${t.motiv}</span><span>${bt} ${bn} <b>${t.nr}\u00d7</b></span></div>`;
      }).join("");
      return `
        <div class="val-card" style="display:block;">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
            <span class="asi-sem asi-sem-${a.culoare}"></span>
            <b>${a.nume}</b>
            <span style="font-size:13px;color:#5f5e5a;">${a.respinse} respinse \u00b7 ${a.rata}%</span>
          </div>
          ${tipare}
        </div>`;
    }).join("");
    box.innerHTML = `<p class="mig-intro">Cine a produs respingeri in ultimele ${d.zile} zile, sortat dupa volum.</p>${carduri}`;
  });
}
'''

# ---- 2. cabinet.js: bulina semafor pe card ----
CAB_OLD = '''    const n = (r && r.sumar && r.sumar.activi) || 0;
    zona.innerHTML = `<b style="font-size:19px">${n}</b> ${n === 1 ? "asistent activ" : "asistenți activi"}`;'''
CAB_NEW = '''    const n = (r && r.sumar && r.sumar.activi) || 0;
    ''' + M_CAB + '''
    let pastila = "";
    try {
      const sm = await api.get("/asistenti/echipa/semafor");
      if (sm && sm.ok) pastila = `<span class="asi-sem asi-sem-${sm.culoare}" style="margin-left:6px;"></span>`;
    } catch {}
    zona.innerHTML = `<b style="font-size:19px">${n}</b> ${n === 1 ? "asistent activ" : "asistenți activi"}${pastila}`;'''

CSS_NOU = NL + NL + M_CSS + NL + '''.asi-echipa-banner {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; margin: 4px 0 12px;
  background: var(--fundal, #f5f6f8); border-radius: 10px;
}
.asi-echipa-text { font-size: 13px; color: var(--ardezie, #2c2b28); flex: 1; }
.asi-echipa-btn {
  padding: 6px 12px; font-family: inherit; font-size: 13px; cursor: pointer;
  background: #fff; border: 0.5px solid var(--linie, #d0cfc9); border-radius: 8px;
  color: var(--ardezie, #2c2b28);
}
.asi-echipa-btn:hover { background: #ecebe5; }
'''


def main():
    for p in (ASI, CAB, CSS):
        if not os.path.exists(p): raise SystemExit("Lipseste: " + p)

    s = open(ASI, encoding="utf-8").read()
    if M_ASI in s:
        print("asistenti.js deja patch-at — sar.")
    else:
        backup(ASI, ".bak_p10")
        s = once(s, ASI_OLD1, ASI_NEW1, "container banner")
        s = once(s, ASI_OLD2, ASI_NEW2, "apel banner")
        s = s.rstrip(NL) + ASI_FUNCS
        open(ASI, "w", encoding="utf-8").write(s)
        print("  asistenti.js: banner + drill erori")

    s = open(CAB, encoding="utf-8").read()
    if M_CAB in s:
        print("cabinet.js deja patch-at — sar.")
    else:
        backup(CAB, ".bak_p10")
        s = once(s, CAB_OLD, CAB_NEW, "bulina card")
        open(CAB, "w", encoding="utf-8").write(s)
        print("  cabinet.js: bulina semafor pe card")

    s = open(CSS, encoding="utf-8").read()
    if M_CSS in s:
        print("stil.css deja patch-at — sar.")
    else:
        backup(CSS, ".bak_p10")
        open(CSS, "w", encoding="utf-8").write(s.rstrip(NL) + NL + CSS_NOU)
        print("  stil.css: stil banner echipa")

    print(NL + "GATA. Frontend pur — Ctrl+Shift+R. Rollback: .bak_p10")


if __name__ == "__main__":
    main()
