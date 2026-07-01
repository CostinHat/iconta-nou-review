#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch8_lista_dezactivati.py — lista arata doar activii; dezactivatii sub toggle."""
import os, shutil

BASE = "/home/costin/iconta_nou"
JS  = os.path.join(BASE, "static", "js", "ecrane", "asistenti.js")
CSS = os.path.join(BASE, "static", "stil.css")
M_JS = "/* [patch8_lista_dez] */"
M_CSS = "/* [patch8_lista_dez] */"
NL = chr(10)

JS_OLD = '''  const lista = corp.querySelector("#asi-lista");
  if (!actori.length) {
    lista.innerHTML = `<div class="mig-gol">Niciun asistent în cabinet.</div>`;
    return;
  }
  actori.forEach((a) => lista.appendChild(randActor(a, corp, nav)));
}'''

JS_NEW = '''  const lista = corp.querySelector("#asi-lista");
  ''' + M_JS + '''
  if (!actori.length) {
    lista.innerHTML = `<div class="mig-gol">Niciun asistent în cabinet.</div>`;
    return;
  }
  const activi = actori.filter((a) => a.activ);
  const inactivi = actori.filter((a) => !a.activ);

  if (!activi.length) {
    lista.innerHTML = `<div class="mig-gol">Niciun asistent activ.</div>`;
  } else {
    activi.forEach((a) => lista.appendChild(randActor(a, corp, nav)));
  }

  if (inactivi.length) {
    const wrap = document.createElement("div");
    wrap.innerHTML = `
      <button class="asi-toggle-dez" id="asi-toggle-dez">Arată dezactivați (${inactivi.length})</button>
      <div id="asi-lista-dez" style="display:none;"></div>`;
    lista.appendChild(wrap);
    const cont = wrap.querySelector("#asi-lista-dez");
    inactivi.forEach((a) => cont.appendChild(randActor(a, corp, nav)));
    const btn = wrap.querySelector("#asi-toggle-dez");
    btn.onclick = () => {
      const deschis = cont.style.display !== "none";
      cont.style.display = deschis ? "none" : "";
      btn.textContent = (deschis ? "Arată" : "Ascunde") + ` dezactivați (${inactivi.length})`;
    };
  }
}'''

CSS_NOU = NL + NL + M_CSS + NL + '''.asi-toggle-dez {
  margin-top: 10px; padding: 7px 12px; font-family: inherit; font-size: 13px;
  background: var(--fundal, #f5f6f8); color: var(--gri, #5f5e5a);
  border: 0.5px solid var(--linie, #d0cfc9); border-radius: 8px; cursor: pointer;
}
.asi-toggle-dez:hover { background: #ecebe5; }
#asi-lista-dez { margin-top: 8px; }
'''


def backup(p, suf):
    b = p + suf
    if not os.path.exists(b):
        shutil.copy2(p, b); print("  .bak ->", b)


def once(t, old, new, label):
    if old not in t: raise SystemExit("ANCORA LIPSA: " + label)
    if t.count(old) != 1: raise SystemExit("ANCORA NEUNICA: " + label)
    return t.replace(old, new)


def main():
    for p in (JS, CSS):
        if not os.path.exists(p): raise SystemExit("Lipseste: " + p)

    s = open(JS, encoding="utf-8").read()
    if M_JS in s:
        print("asistenti.js deja patch-at — sar.")
    else:
        backup(JS, ".bak_p8")
        s = once(s, JS_OLD, JS_NEW, "lista actori")
        open(JS, "w", encoding="utf-8").write(s)
        print("  asistenti.js: separare activi/dezactivati + toggle")

    s = open(CSS, encoding="utf-8").read()
    if M_CSS in s:
        print("stil.css deja patch-at — sar.")
    else:
        backup(CSS, ".bak_p8")
        open(CSS, "w", encoding="utf-8").write(s.rstrip(NL) + NL + CSS_NOU)
        print("  stil.css: stil toggle")

    print(NL + "GATA. Frontend pur — Ctrl+Shift+R. Rollback: .bak_p8")


if __name__ == "__main__":
    main()
