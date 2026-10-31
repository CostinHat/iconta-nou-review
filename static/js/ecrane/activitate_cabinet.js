// activitate_cabinet.js — Ecran D: Activitate cabinet (centralizator + jurnal).
// Centralizator: cifre-cheie pe perioada (create/aprobate/respinse/depuse/in asteptare).
// Jurnal: evenimente cronologice (pregatit/aprobat/respins/depus), tabel scrollabil.
// Regula design: fer-larg, antet fix, doar tabelul scrolleaza (un singur scrollbar).

import { api, ultimaCerere, dataIso, esc, cate } from "../api.js?v=ec2094fd4f";

// perioade selectabile -> [de, pana] ISO (sau null pentru tot)
function interval(cheie) {
  const azi = new Date();
  const iso = (d) => dataIso(d);
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
  const cerereNoua = ultimaCerere();   // [C103] perioada schimbată în șir: numai răspunsul ultimei perioade alese ajunge pe ecran

  async function reincarca() {
    const actuala = cerereNoua();
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
      if (!actuala()) return;
      jur = await api.get("/asistenti/echipa/jurnal" + sfx + (sfx ? "&" : "?") + "limit=200");
      if (!actuala()) return;
    } catch {
      if (!actuala()) return;
      corp.innerHTML = `<p class="ecran-nota">Nu s-a putut încărca activitatea.</p>`;
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
      // [validare_note 06.10.2026] eticheta vine de la server (declarație SAU notă — sursa unică `coada_api.eticheta_element`);
      // textele scrise de om (motivul, descrierea notei, numele) se scapă — înainte intrau în HTML ca atare
      const motiv = e.motiv ? `<div class="ac-motiv">motiv: ${esc(e.motiv)}</div>` : "";
      return `
        <div class="mig-sold-rand ac-rand">
          <span class="ac-cand">${dataOraRo(e.cand)}</span>
          <span class="ac-cine">${esc(e.cine)}</span>
          <span class="ac-act"><span class="cab-pct ${a.cls}"></span>${a.txt}</span>
          <span class="ac-decl">${esc(e.eticheta || `${(e.tip || "").toUpperCase()} · ${e.perioada}`)}</span>
          <span class="ac-firma">${esc(e.firma)}</span>
        </div>${motiv}`;
    }).join("");

    // [lotul 10, 421 / 424 — rezumatul fix, DS cap.9 v2.97 pct.5] perioada, cifrele și numărul evenimentelor rămân sus cât derulezi jurnalul
    corp.innerHTML = `
      <div class="rezumat-fix">
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
      <div class="mig-intro">Jurnal cronologic — cine, ce și când (${cate(jur.total || 0, "eveniment", "evenimente")})</div>
      </div>
      <div class="mig-sold-tabel ac-tabel" tabindex="0" aria-label="Activitatea cabinetului">
        <div class="mig-sold-rand ac-cap">
          <span class="ac-cand">Când</span>
          <span class="ac-cine">Cine</span>
          <span class="ac-act">Acțiune</span>
          <span class="ac-decl">Declarație / notă</span>
          <span class="ac-firma">Firmă</span>
        </div>
        ${ev.length ? randuriJurnal : `<div class="stare-goala">Nicio activitate în perioada aleasă.</div>`}
      </div>
    `;

    corp.querySelectorAll(".ac-per").forEach((b) =>
      b.addEventListener("click", () => { perioada = b.dataset.per; reincarca(); }));
  }

  await reincarca();
}
