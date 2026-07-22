// activitate_cabinet.js — Ecran D: Activitate cabinet (centralizator + jurnal).
// Centralizator: cifre-cheie pe perioada (create/aprobate/respinse/depuse/in asteptare).
// Jurnal: evenimente cronologice (pregatit/aprobat/respins/depus), tabel scrollabil.
// Regula design: fer-larg, antet fix, doar tabelul scrolleaza (un singur scrollbar).

import { api } from "../api.js";

// perioade selectabile -> [de, pana] ISO (sau null pentru tot)
function interval(cheie) {
  const azi = new Date();
  const iso = (d) => d.toISOString().slice(0, 10);
  if (cheie === "azi") return [iso(azi), iso(azi)];
  if (cheie === "luna") {
    const p = new Date(azi.getFullYear(), azi.getMonth(), 1);
    return [iso(p), iso(azi)];
  }
  if (cheie === "an") {
    const p = new Date(azi.getFullYear(), 0, 1);
    return [iso(p), iso(azi)];
  }
  return [null, null]; // tot
}

const ACTIUNI = {
  pregatit: { txt: "a pregătit", cls: "pct-verde" },
  aprobat:  { txt: "a aprobat",  cls: "pct-verde" },
  respins:  { txt: "a respins",  cls: "pct-rosu" },
  depus:    { txt: "a depus",    cls: "pct-verde" },
};

function dataOraRo(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  const zz = String(d.getDate()).padStart(2, "0");
  const ll = String(d.getMonth() + 1).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mi = String(d.getMinutes()).padStart(2, "0");
  return `${zz}.${ll}.${d.getFullYear()} ${hh}:${mi}`;
}

export async function randeazaActivitateCabinet(corp, nav) {
  // lateste fereastra (tabel) — regula design
  const f = corp.closest(".fereastra");
  if (f) f.classList.add("fer-larg");

  let perioada = "luna";

  async function reincarca() {
    const [de, pana] = interval(perioada);
    const qs = [];
    if (de) qs.push("de=" + de);
    if (pana) qs.push("pana=" + pana);
    const sfx = qs.length ? "?" + qs.join("&") : "";

    corp.innerHTML = `<p class="ecran-nota">Se încarcă activitatea…</p>`;
    let cen = { totaluri: {}, pe_asistent: [] };
    let jur = { evenimente: [], total: 0 };
    try {
      cen = await api.get("/asistenti/echipa/centralizator" + sfx);
      jur = await api.get("/asistenti/echipa/jurnal" + sfx + (sfx ? "&" : "?") + "limit=200");
    } catch {
      corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca activitatea.</p>`;
      return;
    }

    const t = cen.totaluri || {};
    const ev = jur.evenimente || [];

    const selBtn = (k, et) =>
      `<button class="ac-per ${perioada === k ? "ac-per-on" : ""}" data-per="${k}">${et}</button>`;

    const card = (cifra, descr, cls) =>
      `<div class="ac-card">
         <div class="ac-cifra ${cls || ""}">${cifra}</div>
         <div class="ac-descr">${descr}</div>
       </div>`;

    const randuriJurnal = ev.map((e) => {
      const a = ACTIUNI[e.actiune] || { txt: e.actiune, cls: "" };
      const motiv = e.motiv ? `<div class="ac-motiv">motiv: ${e.motiv}</div>` : "";
      return `
        <div class="mig-sold-rand ac-rand">
          <span class="ac-cand">${dataOraRo(e.cand)}</span>
          <span class="ac-cine">${e.cine}</span>
          <span class="ac-act"><span class="cab-pct ${a.cls}"></span>${a.txt}</span>
          <span class="ac-decl">${(e.tip||"").toUpperCase()} · ${e.perioada}</span>
          <span class="ac-firma">${e.firma}</span>
        </div>${motiv}`;
    }).join("");

    corp.innerHTML = `
      <div class="ac-perbar">
        ${selBtn("azi", "Azi")}${selBtn("luna", "Luna")}${selBtn("an", "Anul")}${selBtn("tot", "Tot")}
      </div>
      <div class="ac-carduri">
        ${card(t.create || 0, "create")}
        ${card(t.aprobate || 0, "aprobate")}
        ${card(t.respinse || 0, "respinse", t.respinse ? "ac-rosu" : "")}
        ${card(t.depuse || 0, "depuse")}
        ${card(t.in_asteptare || 0, "în așteptare")}
      </div>
      <div class="mig-intro">Jurnal cronologic — cine, ce și când (${jur.total || 0} evenimente)</div>
      <div class="mig-sold-tabel ac-tabel">
        <div class="mig-sold-rand ac-cap">
          <span class="ac-cand">CÂND</span>
          <span class="ac-cine">CINE</span>
          <span class="ac-act">ACȚIUNE</span>
          <span class="ac-decl">DECLARAȚIE</span>
          <span class="ac-firma">FIRMĂ</span>
        </div>
        ${ev.length ? randuriJurnal : `<div class="stare-goala">Nicio activitate în perioada aleasă.</div>`}
      </div>
    `;

    corp.querySelectorAll(".ac-per").forEach((b) =>
      b.addEventListener("click", () => { perioada = b.dataset.per; reincarca(); }));
  }

  await reincarca();
}
