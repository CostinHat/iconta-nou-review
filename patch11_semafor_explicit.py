#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch11_semafor_explicit.py — bulina + eticheta text peste tot, rosu pronuntat.
Legenda unica: rosu=probleme, galben=de urmarit, verde=fara probleme."""
import os, shutil

BASE = "/home/costin/iconta_nou"
ASI = os.path.join(BASE, "static", "js", "ecrane", "asistenti.js")
CAB = os.path.join(BASE, "static", "js", "ecrane", "cabinet.js")
CSS = os.path.join(BASE, "static", "stil.css")
M_ASI = "/* [patch11_semafor_explicit] */"
M_CAB = "/* [patch11_semafor_explicit] */"
M_CSS = "/* [patch11_semafor_explicit] */"
NL = chr(10)


def backup(p, suf):
    b = p + suf
    if not os.path.exists(b):
        shutil.copy2(p, b); print("  .bak ->", b)


def repl(t, old, new, label, n=1):
    c = t.count(old)
    if c == 0: raise SystemExit("ANCORA LIPSA: " + label)
    if c != n: raise SystemExit(f"ANCORA: {label} apare {c}, asteptat {n}")
    return t.replace(old, new)


# helper unic, pus dupa import-ul api in asistenti.js
HELPER = '''import { api } from "../api.js";
''' + M_ASI + '''
function _semaforEticheta(culoare) {
  const M = { rosu: "probleme", galben: "de urm\\u0103rit", verde: "f\\u0103r\\u0103 probleme" };
  const t = M[culoare] || "";
  return `<span class="asi-sem asi-sem-${culoare}"></span><span class="asi-sem-txt">${t}</span>`;
}'''
HELPER_OLD = 'import { api } from "../api.js";'

# 1. fereastra vizualizare (l.266): header semafor -> eticheta
ASI1_OLD = '''      <span class="asi-sem asi-sem-${sem}"></span>
      <span style="font-size:13px;color:#5f5e5a;">${d.actor.rol}</span>'''
ASI1_NEW = '''      ${_semaforEticheta(sem)}
      <span style="font-size:13px;color:#5f5e5a;">${d.actor.rol}</span>'''

# 2. banner (l.338)
ASI2_OLD = '''      <span class="asi-sem asi-sem-${s.culoare}"></span>
      <span class="asi-echipa-text">'''
ASI2_NEW = '''      ${_semaforEticheta(s.culoare)}
      <span class="asi-echipa-text">'''

# 3. drill (l.368)
ASI3_OLD = '''            <span class="asi-sem asi-sem-${a.culoare}"></span>
            <b>${a.nume}</b>'''
ASI3_NEW = '''            ${_semaforEticheta(a.culoare)}
            <b>${a.nume}</b>'''

# 4. cabinet.js card: pastila bulina -> bulina+text
CAB_OLD = 'if (sm && sm.ok) pastila = `<span class="asi-sem asi-sem-${sm.culoare}" style="margin-left:6px;"></span>`;'
CAB_NEW = ('if (sm && sm.ok) { const M={rosu:"probleme",galben:"de urm\\u0103rit",verde:"f\\u0103r\\u0103 probleme"}; '
           'pastila = `<span class="asi-sem asi-sem-${sm.culoare}" style="margin-left:8px;"></span>'
           '<span class="asi-sem-txt">${M[sm.culoare]||""}</span>`; }')

# CSS: rosu pronuntat + stil eticheta
CSS_OLD = ".asi-sem-rosu   { background:#b3261e; }"
CSS_NEW = (".asi-sem-rosu   { background:#e3342f; }" + NL + NL + M_CSS + NL +
           ".asi-sem-txt { font-size:12.5px; color:#5f5e5a; margin-left:5px; }")


def main():
    for p in (ASI, CAB, CSS):
        if not os.path.exists(p): raise SystemExit("Lipseste: " + p)

    s = open(ASI, encoding="utf-8").read()
    if M_ASI in s:
        print("asistenti.js deja patch-at — sar.")
    else:
        backup(ASI, ".bak_p11")
        s = repl(s, HELPER_OLD, HELPER, "helper semafor")
        s = repl(s, ASI1_OLD, ASI1_NEW, "fereastra vizualizare")
        s = repl(s, ASI2_OLD, ASI2_NEW, "banner")
        s = repl(s, ASI3_OLD, ASI3_NEW, "drill")
        open(ASI, "w", encoding="utf-8").write(s)
        print("  asistenti.js: helper + 3 semafoare explicite")

    s = open(CAB, encoding="utf-8").read()
    if M_CAB in s:
        print("cabinet.js deja patch-at — sar.")
    else:
        backup(CAB, ".bak_p11")
        s = repl(s, CAB_OLD, CAB_NEW, "card dashboard")
        open(CAB, "w", encoding="utf-8").write(s)
        print("  cabinet.js: semafor card explicit")

    s = open(CSS, encoding="utf-8").read()
    if M_CSS in s:
        print("stil.css deja patch-at — sar.")
    else:
        backup(CSS, ".bak_p11")
        s = repl(s, CSS_OLD, CSS_NEW, "rosu pronuntat")
        open(CSS, "w", encoding="utf-8").write(s)
        print("  stil.css: rosu pronuntat + eticheta")

    print(NL + "GATA. Frontend pur — Ctrl+Shift+R. Rollback: .bak_p11")


if __name__ == "__main__":
    main()
