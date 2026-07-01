#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch14_semafor_ordine.py — semafor vertical, ordine ROSU->GALBEN->VERDE
(urgenta sus), unitar la Control fiscal si cardul Asistenti."""
import os, shutil

BASE = "/home/costin/iconta_nou"
CAB = os.path.join(BASE, "static", "js", "ecrane", "cabinet.js")
M = "/* [patch14_ordine_semafor] */"
NL = chr(10)


def backup(p, suf):
    b = p + suf
    if not os.path.exists(b):
        shutil.copy2(p, b); print("  .bak ->", b)


def repl(t, old, new, label, n=1):
    c = t.count(old)
    if c != n: raise SystemExit(f"ANCORA {label}: {c}, asteptat {n}")
    return t.replace(old, new)


# 1. Control fiscal runtime: inversez ordinea -> rosu, galben, verde
CTRL_OLD = ('`<div><span class="cab-pct pct-verde"></span>${s.verde || 0} firme la zi</div>` +' + NL +
            '      `<div><span class="cab-pct pct-galben"></span>${s.galben || 0} de urm\u0103rit</div>` +' + NL +
            '      `<div><span class="cab-pct pct-rosu"></span>${s.rosu || 0} cu restan\u021b\u0103</div>`;')
CTRL_NEW = (M + NL +
            '      `<div><span class="cab-pct pct-rosu"></span>${s.rosu || 0} cu restan\u021b\u0103</div>` +' + NL +
            '      `<div><span class="cab-pct pct-galben"></span>${s.galben || 0} de urm\u0103rit</div>` +' + NL +
            '      `<div><span class="cab-pct pct-verde"></span>${s.verde || 0} firme la zi</div>`;')

# 2. Control fiscal sinteza initiala: aceeasi ordine
SINT_OLD = ('sinteza:\'<div><span class="cab-pct pct-verde"></span>0 firme la zi</div>'
            '<div><span class="cab-pct pct-galben"></span>0 de urm\u0103rit</div>'
            '<div><span class="cab-pct pct-rosu"></span>0 cu restan\u021b\u0103</div>\',')
SINT_NEW = ('sinteza:\'<div><span class="cab-pct pct-rosu"></span>0 cu restan\u021b\u0103</div>'
            '<div><span class="cab-pct pct-galben"></span>0 de urm\u0103rit</div>'
            '<div><span class="cab-pct pct-verde"></span>0 firme la zi</div>\',')

# 3. card Asistenti: cifra activi + semafor vertical rosu/galben/verde din counts
ASI_OLD = '''    const n = (r && r.sumar && r.sumar.activi) || 0;
    /* [patch10_card_sem] */
    let pastila = "";
    try {
      const sm = await api.get("/asistenti/echipa/semafor");
      if (sm && sm.ok) { const M={rosu:"probleme",galben:"de urm\u0103rit",verde:"f\u0103r\u0103 probleme"}; pastila = `<span class="asi-sem asi-sem-${sm.culoare}" style="margin-left:8px;"></span><span class="asi-sem-txt">${M[sm.culoare]||""}</span>`; }
    } catch {}
    zona.innerHTML = `<b style="font-size:19px">${n}</b> ${n === 1 ? "asistent activ" : "asistenți activi"}${pastila}`;'''
ASI_NEW = '''    const n = (r && r.sumar && r.sumar.activi) || 0;
    /* [patch10_card_sem] */
    let semafor = "";
    try {
      const sm = await api.get("/asistenti/echipa/semafor");
      if (sm && sm.ok) {
        const c = sm.counts || {};
        semafor =
          `<div><span class="cab-pct pct-rosu"></span>${c.rosu || 0} cu probleme</div>` +
          `<div><span class="cab-pct pct-galben"></span>${c.galben || 0} de urmărit</div>` +
          `<div><span class="cab-pct pct-verde"></span>${c.verde || 0} fără probleme</div>`;
      }
    } catch {}
    zona.innerHTML = `<div style="margin-bottom:6px;"><b style="font-size:19px">${n}</b> ${n === 1 ? "asistent activ" : "asistenți activi"}</div>${semafor}`;'''


def main():
    if not os.path.exists(CAB): raise SystemExit("Lipseste: " + CAB)
    s = open(CAB, encoding="utf-8").read()
    if M in s:
        print("cabinet.js deja patch-at — sar.")
        return
    backup(CAB, ".bak_p14")
    s = repl(s, CTRL_OLD, CTRL_NEW, "control runtime")
    s = repl(s, SINT_OLD, SINT_NEW, "control sinteza")
    s = repl(s, ASI_OLD, ASI_NEW, "card asistenti")
    open(CAB, "w", encoding="utf-8").write(s)
    print("  cabinet.js: semafor vertical rosu->galben->verde (Control + Asistenti)")
    print(NL + "GATA. Frontend pur — Ctrl+Shift+R. Rollback: .bak_p14")


if __name__ == "__main__":
    main()
