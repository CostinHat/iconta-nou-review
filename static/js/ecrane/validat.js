// validat.js — coada de validare a declarațiilor (perspectiva seniorului / admin_firma).
// Sectiuni: "De validat" (la_senior -> Aprobă/Respinge) si "Aprobate, de depus" (aprobata -> Depune).
// Butoanele se rescriu după permisiunile actorului curent (poate_valida / poate_depune),
// proaspete de la GET /eu/permisiuni. Control „patru ochi": cine a pregătit nu poate aproba
// (ascuns vizual + blocat în backend).
// Dialogurile (motiv respingere / index SPV) folosesc ferestre modale proprii (nav.deschide).
import { api } from "../api.js";
import { sesiune } from "../sesiune.js";

function numeFirma(firme, tid) {
  const f = firme.find((x) => x.tenant_id === tid || x.id === tid);
  return f ? f.nume : `firma #${tid}`;
}

// uid-ul actorului curent, ca string (creat_de/aprobat_de sunt UID-uri text în coadă)
function uidCurent() {
  const u = sesiune.user();
  return u && u.id != null ? String(u.id) : null;
}

export async function randeazaValidat(corp, nav) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă coada…</p>`;
  let coada = [];
  let firme = [];
  let perm = { poate_valida: false, poate_depune: false, rol: null };
  try {
    const [rc, rf, rp] = await Promise.all([
      api.get("/coada"),
      api.get("/tenants"),
      api.get("/eu/permisiuni"),
    ]);
    coada = (rc && rc.coada) || [];
    firme = (rf && rf.tenants) || [];
    if (rp) perm = rp;
  } catch {
    corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca coada.</p>`;
    return;
  }
  const deValidat = coada.filter((c) => c.stare === "la_senior");
  const deDepus = coada.filter((c) => c.stare === "aprobata");
  corp.innerHTML = `
    <p class="mig-intro">Declarațiile pregătite de asistenți așteaptă validarea ta înainte de depunere. Nimic nu se depune nevalidat.</p>
    <div id="val-deValidat"></div>
    <div id="val-deDepus"></div>
    <div class="mig-eroare" id="val-eroare"></div>
  `;
  const z1 = corp.querySelector("#val-deValidat");
  const z2 = corp.querySelector("#val-deDepus");
  if (deValidat.length === 0 && deDepus.length === 0) {
    z1.innerHTML = `<div class="mig-gol">Nimic de validat. Coada e goală.</div>`;
    return;
  }
  if (deValidat.length) {
    z1.innerHTML = `<div class="cf-grup-titlu cf-galben">De validat (${deValidat.length})</div>`;
    deValidat.forEach((c) => z1.appendChild(randDeclaratie(c, firme, corp, nav, "valida", perm)));
  }
  if (deDepus.length) {
    z2.innerHTML = `<div class="cf-grup-titlu" style="color:var(--verde)">Aprobate, de depus (${deDepus.length})</div>`;
    deDepus.forEach((c) => z2.appendChild(randDeclaratie(c, firme, corp, nav, "depune", perm)));
  }
}

function randDeclaratie(c, firme, corp, nav, mod, perm) {
  const div = document.createElement("div");
  div.className = "val-card";
  const coer = c.coerenta
    ? `<span class="val-coer val-coer-ok">✓ ${c.coerenta}</span>`
    : `<span class="val-coer val-coer-gri">neverificat</span>`;

  const uid = uidCurent();
  const euAmPregatit = uid != null && c.creat_de != null && String(c.creat_de) === uid;

  let actiuni = "";
  if (mod === "valida") {
    // Aprobă — doar dacă pot valida ȘI nu eu am pregătit-o (patru ochi)
    if (!perm.poate_valida) {
      actiuni += `<span class="val-nota-perm">nu ai dreptul de validare</span>`;
    } else if (euAmPregatit) {
      actiuni += `<span class="val-nota-perm">ai pregătit-o tu — o validează altcineva</span>`;
    } else {
      actiuni += `<button class="buton-primar val-btn val-aproba" data-act="aproba">Aprobă</button>`;
    }
    // Respinge — îl poate face oricine cu drept de validare (și care n-a pregătit-o)
    if (perm.poate_valida && !euAmPregatit) {
      actiuni += `<button class="buton-sters val-btn val-respinge" data-act="respinge">Respinge</button>`;
    }
  } else {
    // depune -> "Confirmă depunerea"
    if (!perm.poate_depune) {
      actiuni += `<span class="val-nota-perm">nu ai dreptul de depunere</span>`;
    } else {
      actiuni += `<button class="buton-primar val-btn val-depune" data-act="depune">Confirmă depunerea</button>`;
    }
  }

  div.innerHTML = `
    <div class="val-info">
      <div class="val-titlu"><b>${c.tip}</b> · ${c.perioada}</div>
      <div class="val-sub">${numeFirma(firme, c.tenant_id)} · pregătit de ${c.creat_de || "—"}</div>
    </div>
    <div class="val-mij">${coer}</div>
    <div class="val-actiuni">${actiuni}</div>
  `;
  div.querySelectorAll(".val-btn").forEach((btn) => {
    btn.addEventListener("click", () => actioneaza(c, btn.dataset.act, firme, corp, nav));
  });
  return div;
}

async function actioneaza(c, act, firme, corp, nav) {
  const eroare = corp.querySelector("#val-eroare");
  if (eroare) eroare.textContent = "";
  if (act === "respinge") {
    dialogInput(nav, {
      titlu: "Respinge declarația",
      eticheta: `Motiv respingere pentru ${c.tip} (${c.perioada}):`,
      placeholder: "ex: TVA necorelată cu jurnalul de vânzări",
      obligatoriu: true,
      buton: "Respinge",
      butonClasa: "val-respinge",
      onConfirm: async (motiv) => {
        await api.post(`/coada/${c.id}/respinge`, { motiv });
        nav.inapoi();
        randeazaValidat(corp, nav);
      },
    });
    return;
  }
  if (act === "depune") {
    dialogInput(nav, {
      titlu: "Confirmă depunerea",
      eticheta: `Index SPV pentru ${c.tip} (${c.perioada}) — opțional:`,
      placeholder: "lasă gol dacă nu ai indexul încă",
      obligatoriu: false,
      buton: "Confirmă depunerea",
      butonClasa: "val-depune",
      onConfirm: async (spv) => {
        await api.post(`/coada/${c.id}/depune`, spv ? { spv_index: spv } : {});
        nav.inapoi();
        randeazaValidat(corp, nav);
      },
    });
    return;
  }
  // aproba — fara dialog, direct
  try {
    await api.post(`/coada/${c.id}/aproba`, {});
    randeazaValidat(corp, nav);
  } catch (e) {
    if (eroare) eroare.textContent = (e && e.mesaj) || "Eroare la aprobare.";
  }
}

// dialog modal cu un input (foloseste fereastra standard nav.deschide)
function dialogInput(nav, opt) {
  nav.deschide(opt.titlu, (corp) => {
    corp.innerHTML = `
      <label class="dlg-eticheta">${opt.eticheta}</label>
      <input class="dlg-input" id="dlg-input" type="text" placeholder="${opt.placeholder || ""}" autocomplete="off">
      <div class="dlg-eroare" id="dlg-eroare"></div>
      <div class="dlg-actiuni">
        <button class="buton-secundar val-btn dlg-anuleaza" id="dlg-anuleaza">Anulează</button>
        <button class="val-btn ${opt.butonClasa}" id="dlg-ok">${opt.buton}</button>
      </div>
    `;
    const input = corp.querySelector("#dlg-input");
    const er = corp.querySelector("#dlg-eroare");
    input.focus();
    const confirma = async () => {
      const val = input.value.trim();
      if (opt.obligatoriu && !val) {
        er.textContent = "Câmpul e obligatoriu.";
        input.focus();
        return;
      }
      const btn = corp.querySelector("#dlg-ok");
      btn.disabled = true;
      try {
        await opt.onConfirm(val);
      } catch (e) {
        btn.disabled = false;
        er.textContent = (e && e.mesaj) || "Eroare. Încearcă din nou.";
      }
    };
    corp.querySelector("#dlg-ok").addEventListener("click", confirma);
    corp.querySelector("#dlg-anuleaza").addEventListener("click", () => nav.inapoi());
    input.addEventListener("keydown", (ev) => { if (ev.key === "Enter") confirma(); });
  });
}
