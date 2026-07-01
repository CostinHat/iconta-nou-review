#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch13_semafor_unitar.py — un singur set de culori+dimensiune pentru TOATE
semafoarele. Referinta canonica: verde #1d7a4d, galben #c9961f, rosu #ff3b30, 10px.
Aliniaza .cab-pct (Control fiscal) la asi-sem si scoate culorile inline din cabinet.js."""
import os, shutil

BASE = "/home/costin/iconta_nou"
CAB = os.path.join(BASE, "static", "js", "ecrane", "cabinet.js")
CSS = os.path.join(BASE, "static", "stil.css")
M = "/* [patch13_semafor_unitar] */"
NL = chr(10)

# culori canonice
V, G, R = "#1d7a4d", "#c9961f", "#ff3b30"


def backup(p, suf):
    b = p + suf
    if not os.path.exists(b):
        shutil.copy2(p, b); print("  .bak ->", b)


def repl(t, old, new, label, n=1):
    c = t.count(old)
    if c != n: raise SystemExit(f"ANCORA {label}: {c} gasite, asteptat {n}")
    return t.replace(old, new)


# 1. CSS: .cab-pct la 10px + clase de culoare canonice (refolosite)
CSS_OLD = ".cab-pct { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; vertical-align: 1px; }"
CSS_NEW = (M + NL +
           ".cab-pct { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; vertical-align: 0px; }" + NL +
           ".pct-verde  { background: " + V + "; }" + NL +
           ".pct-galben { background: " + G + "; }" + NL +
           ".pct-rosu   { background: " + R + "; }")

# 2. cabinet.js Control fiscal (runtime) — scot inline, pun clase canonice
CAB_OLD1 = ('`<div><span class="cab-pct" style="background:#1d9e75"></span>${s.verde || 0} firme la zi</div>` +' + NL +
            '      `<div><span class="cab-pct" style="background:#ba7517"></span>${s.galben || 0} de urm\u0103rit</div>` +' + NL +
            '      `<div><span class="cab-pct" style="background:#e24b4a"></span>${s.rosu || 0} cu restan\u021b\u0103</div>`;')
CAB_NEW1 = ('`<div><span class="cab-pct pct-verde"></span>${s.verde || 0} firme la zi</div>` +' + NL +
            '      `<div><span class="cab-pct pct-galben"></span>${s.galben || 0} de urm\u0103rit</div>` +' + NL +
            '      `<div><span class="cab-pct pct-rosu"></span>${s.rosu || 0} cu restan\u021b\u0103</div>`;')

# 3. cabinet.js Control fiscal (sinteza initiala hardcodata in lista de carduri)
CAB_OLD2 = ('sinteza:\'<div><span class="cab-pct" style="background:#1d9e75"></span>8 firme la zi</div>'
            '<div><span class="cab-pct" style="background:#ba7517"></span>3 de urm\u0103rit</div>'
            '<div><span class="cab-pct" style="background:#e24b4a"></span>1 cu restan\u021b\u0103</div>\',')
CAB_NEW2 = ('sinteza:\'<div><span class="cab-pct pct-verde"></span>0 firme la zi</div>'
            '<div><span class="cab-pct pct-galben"></span>0 de urm\u0103rit</div>'
            '<div><span class="cab-pct pct-rosu"></span>0 cu restan\u021b\u0103</div>\',')


def main():
    for p in (CAB, CSS):
        if not os.path.exists(p): raise SystemExit("Lipseste: " + p)

    s = open(CSS, encoding="utf-8").read()
    if M in s:
        print("stil.css deja patch-at — sar.")
    else:
        backup(CSS, ".bak_p13")
        s = repl(s, CSS_OLD, CSS_NEW, "cab-pct dim")
        open(CSS, "w", encoding="utf-8").write(s)
        print("  stil.css: .cab-pct 10px + clase culoare canonice")

    s = open(CAB, encoding="utf-8").read()
    if "pct-verde" in s:
        print("cabinet.js deja patch-at — sar.")
    else:
        backup(CAB, ".bak_p13")
        s = repl(s, CAB_OLD1, CAB_NEW1, "control runtime")
        s = repl(s, CAB_OLD2, CAB_NEW2, "control sinteza")
        open(CAB, "w", encoding="utf-8").write(s)
        print("  cabinet.js: culori inline -> clase canonice")

    print(NL + "GATA. Frontend pur — Ctrl+Shift+R. Rollback: .bak_p13")


if __name__ == "__main__":
    main()
