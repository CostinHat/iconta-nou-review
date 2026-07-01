#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch6_editare_completa.py — fereastra Editare pe macheta (frontend pur)."""
import os, shutil

BASE = "/home/costin/iconta_nou"
JS  = os.path.join(BASE, "static", "js", "ecrane", "asistenti.js")
CSS = os.path.join(BASE, "static", "stil.css")
JS_MARKER = "// [patch6_editare_completa]"
CSS_MARKER = "/* [patch6_editare_completa] */"
ANCORA = "async function deschideEditare(uid, corp, nav) {"

FUNC = JS_MARKER + '''
async function deschideEditare(uid, corp, nav) {
  let d;
  try { d = await api.get(`/asistenti/${uid}`); }
  catch { alert("Nu am putut incarca asistentul."); return; }
  if (!d.ok) return;
  const a = d.actor;
  const firme = d.firme || [];
  const nume = [a.prenume, a.nume].filter(Boolean).join(" ") || a.email;
  const calcNivel = () => a.poate_depune ? 3 : (a.poate_valida ? 2 : 1);

  nav.deschide(`Editeaza \\u2014 ${nume}`, (box) => {
    const sectiuneFirme = a.atribuire_relevanta
      ? `
        <div class="asi-sectiune-titlu">Selecteaza firme</div>
        <p class="asi-mic">Asistentul vede doar firmele bifate. Bifarea = stare finala.</p>
        <input id="asi-cauta-firme" class="asi-cauta" placeholder="Cauta firma (nume sau CUI)..." style="width:100%;margin-bottom:8px;">
        <div id="asi-firme">${firme.map((f) => `
          <label class="asi-firma-rand">
            <input type="checkbox" data-tid="${f.id}" ${f.atribuit ? "checked" : ""}>
            <span>${f.nume}${f.cui ? ` \\u00b7 ${f.cui}` : ""}</span>
          </label>`).join("")}</div>`
      : `<p class="asi-mic">Administratorul vede automat tot portofoliul (nu se atribuie firme individual).</p>`;

    box.innerHTML = `
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
        <span class="asi-nivel-badge" id="asi-nivel-badge">Nivel ${calcNivel()}</span>
        <span style="font-size:13px;color:#5f5e5a;">${a.rol === "admin_firma" ? "administrator" : (a.functie || "asistent")}</span>
      </div>
      <div class="asi-sectiune-titlu">Alege competente</div>
      <div id="asi-perm-edit">
        ${PERM.map(([k, t]) => `
          <label class="asi-firma-rand">
            <input type="checkbox" data-perm="${k}" ${a[k] ? "checked" : ""}>
            <span>${t}</span>
          </label>`).join("")}
      </div>
      <div class="asi-info-patru">\\u2139 \\u201ePoate valida\\u201d permite aprobarea, dar niciodata a ceea ce a pregatit el insusi (patru ochi).</div>
      ${sectiuneFirme}
      <div class="asi-editbtns">
        <button class="mig-buton" id="asi-salveaza">Salveaza</button>
        ${a.rol !== "admin_firma" && a.activ
          ? `<button class="mig-buton-sec" id="asi-dezactiveaza">Dezactiveaza asistentul</button>` : ""}
        ${!a.activ
          ? `<button class="mig-buton-sec" id="asi-reactiveaza">Reactiveaza</button>` : ""}
      </div>
      <div class="mig-eroare" id="asi-edit-eroare"></div>
    `;

    const err = box.querySelector("#asi-edit-eroare");

    box.querySelectorAll("[data-perm]").forEach((cb) => {
      cb.addEventListener("change", () => {
        const val = box.querySelector('[data-perm="poate_valida"]')?.checked;
        const dep = box.querySelector('[data-perm="poate_depune"]')?.checked;
        const nv = dep ? 3 : (val ? 2 : 1);
        const bd = box.querySelector("#asi-nivel-badge");
        if (bd) bd.textContent = "Nivel " + nv;
      });
    });

    const cauta = box.querySelector("#asi-cauta-firme");
    if (cauta)
      cauta.oninput = () => {
        const q = cauta.value.toLowerCase();
        box.querySelectorAll("#asi-firme .asi-firma-rand").forEach((r) => {
          r.style.display = r.textContent.toLowerCase().includes(q) ? "" : "none";
        });
      };

    box.querySelector("#asi-salveaza").onclick = async () => {
      err.textContent = "";
      const valNou = box.querySelector('[data-perm="poate_valida"]')?.checked && !a.poate_valida;
      if (valNou && !confirm(`Acorzi dreptul de validare lui ${nume} (Nivel 2)? Asigura-te ca acopera tipurile pe care le va valida.`)) return;
      try {
        const permVals = {};
        box.querySelectorAll("[data-perm]").forEach((cb) => { permVals[cb.dataset.perm] = cb.checked; });
        await api.post(`/asistenti/${uid}/permisiuni`, permVals);
        if (a.atribuire_relevanta) {
          const initiale = {};
          firme.forEach((f) => (initiale[f.id] = f.atribuit));
          const tasks = [];
          box.querySelectorAll("[data-tid]").forEach((cb) => {
            const tid = Number(cb.dataset.tid);
            if (cb.checked && !initiale[tid]) tasks.push(api.post(`/asistenti/${uid}/firme/${tid}`));
            if (!cb.checked && initiale[tid]) tasks.push(api.del(`/asistenti/${uid}/firme/${tid}`));
          });
          await Promise.all(tasks);
        }
        nav.inapoi();
        randeazaAsistenti(corp, nav);
      } catch { err.textContent = "Nu am putut salva. Incearca din nou."; }
    };

    const bDez = box.querySelector("#asi-dezactiveaza");
    if (bDez) bDez.onclick = async () => {
      if (!confirm(`Dezactivezi ${nume}? Ramane in istoric, dar nu mai are acces.`)) return;
      try { await api.post(`/asistenti/${uid}/dezactiveaza`); nav.inapoi(); randeazaAsistenti(corp, nav); }
      catch { err.textContent = "Nu am putut dezactiva."; }
    };
    const bReact = box.querySelector("#asi-reactiveaza");
    if (bReact) bReact.onclick = async () => {
      try { await api.post(`/asistenti/${uid}/reactiveaza`); nav.inapoi(); randeazaAsistenti(corp, nav); }
      catch { err.textContent = "Nu am putut reactiva."; }
    };
  });
}'''

CSS_NOU = '''

''' + CSS_MARKER + '''
.asi-cauta { padding:7px 10px; border:0.5px solid #d0cfc9; border-radius:8px; font-size:13px; box-sizing:border-box; }
.asi-info-patru { font-size:12px; color:#8a6516; background:#fcf0d6; border-radius:8px; padding:8px 10px; margin:8px 0 14px; }
'''


def backup(path, suf):
    bak = path + suf
    if not os.path.exists(bak):
        shutil.copy2(path, bak); print("  .bak ->", bak)


def gaseste_capat(src, start):
    i = src.index("{", start); adanc = 0
    while i < len(src):
        if src[i] == "{": adanc += 1
        elif src[i] == "}":
            adanc -= 1
            if adanc == 0: return i + 1
        i += 1
    raise SystemExit("Acolade dezechilibrate.")


def patch_js():
    src = open(JS, encoding="utf-8").read()
    if JS_MARKER in src:
        print("asistenti.js editare deja patch-at — sar."); return
    p = src.find(ANCORA)
    if p < 0: raise SystemExit("ANCORA LIPSA (deschideEditare).")
    if src.count(ANCORA) != 1: raise SystemExit("ANCORA NEUNICA.")
    capat = gaseste_capat(src, p)
    backup(JS, ".bak_p6")
    open(JS, "w", encoding="utf-8").write(src[:p] + FUNC + src[capat:])
    print("  asistenti.js: deschideEditare completa")


def patch_css():
    src = open(CSS, encoding="utf-8").read()
    if CSS_MARKER in src:
        print("stil.css editare deja patch-at — sar."); return
    backup(CSS, ".bak_p6")
    open(CSS, "w", encoding="utf-8").write(src.rstrip() + "\\n" + CSS_NOU)
    print("  stil.css: asi-cauta/asi-info-patru adaugate")


def main():
    for p in (JS, CSS):
        if not os.path.exists(p): raise SystemExit("Lipseste: " + p)
    patch_js(); patch_css()
    print("\\nGATA. Ctrl+Shift+R. Rollback: .bak_p6")


if __name__ == "__main__":
    main()
