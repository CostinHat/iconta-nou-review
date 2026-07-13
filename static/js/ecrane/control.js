// control.js — ecranul Control fiscal (semafor conformare portofoliu + drill-down).
// Nivel 1: lista firmelor cu pastila colorata (verde/galben/rosu).
// Nivel 2: click pe firma -> declaratiile lipsa + de urmarit, cu termene.

import { api, esc, dataRo } from "../api.js";  /* esc_nc27 */

const CULORI = {
  verde:  { dot:"radial-gradient(circle at 65% 30%, #6fc494, #1d7a4d 60%)", txt:"la zi",       bg:"var(--verde-fundal)" },
  galben: { dot:"radial-gradient(circle at 65% 30%, #f0cd7a, #c9961f 60%)", txt:"de urmărit",  bg:"var(--galben-fundal)" },
  rosu:   { dot:"radial-gradient(circle at 65% 30%, #ff8a80, var(--rosu-semafor) 60%)", txt:"restanță",    bg:"var(--rosu-fundal)" },
  gri:    { dot:"var(--gri-semafor)", txt:"necompletat", bg:"var(--gri-fundal-semafor)" },
};
const LUNI = ["", "ian", "feb", "mar", "apr", "mai", "iun", "iul", "aug", "sep", "oct", "noi", "dec"];


export async function randeazaControl(corp, nav) {
  corp.innerHTML = `<p class="ecran-nota">Se evaluează portofoliul…</p>`;
  let date = { firme: [], sumar: {} };
  try {
    date = await api.get("/control-fiscal");
  } catch (e) {
    corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca controlul fiscal.</p>`;
    return;
  }
  const firme = date.firme || [];
  const s = date.sumar || {};

  corp.innerHTML = `
    <p class="mig-intro">Starea fiscală a fiecărei firme: ce s-a depus vs ce e datorat, cu termenele ANAF.</p>
    <div class="cf-sumar">
      <span class="cf-pastila"><span class="cf-dot" style="background:${CULORI.verde.dot}"></span>${s.verde || 0} la zi</span>
      <span class="cf-pastila"><span class="cf-dot" style="background:${CULORI.galben.dot}"></span>${s.galben || 0} de urmărit</span>
      <span class="cf-pastila"><span class="cf-dot" style="background:${CULORI.rosu.dot}"></span>${s.rosu || 0} cu restanță</span>
    </div>
    <div class="mig-lista" id="cf-lista"></div>
  `;

  const lista = corp.querySelector("#cf-lista");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="mig-gol">Nicio firmă în portofoliu.</div>`;
    return;
  }
  // sortare: rosu intai, apoi galben, apoi verde
  const ord = { rosu: 0, galben: 1, verde: 2, gri: 3 };
  firme.sort((a, b) => (ord[a.stare] ?? 9) - (ord[b.stare] ?? 9));

  firme.forEach((f) => {
    const col = CULORI[f.stare] || CULORI.gri;
    let detaliu = f.stare === "rosu" ? `${f.lipsa} restanț${f.lipsa === 1 ? "ă" : "e"}`
      : f.stare === "galben" ? `${f.urmarit} de urmărit`
      : f.stare === "verde" ? "totul la zi" : "vector necompletat";
    if ((f.contabil || []).length) detaliu += " \u00b7 " + f.contabil.join(" \u00b7 ");
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${detaliu}</div>
      </div>
      <span class="cf-stare" style="background:${col.bg}">
        <span class="cf-dot" style="background:${col.dot}"></span>${col.txt}
      </span>
    `;
    rand.addEventListener("click", () => nav.deschide("Detaliu firm\u0103", (cc, nn) => detaliuFirma(cc, nn, f)));  // [p122_nav_stiva]
    lista.appendChild(rand);
  });
}

async function detaliuFirma(corp, nav, firma) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;

  let d = { lipsa: [], urmarit: [] };
  try {
    d = await api.get(`/control-fiscal/${firma.tenant_id}`);
  } catch {}

  const lipsa = d.lipsa || [];
  const urmarit = d.urmarit || [];
  const col = CULORI[d.stare] || CULORI.gri;

  const randDecl = (arr, clasa) => arr.map((x) => `
    <div class="mig-sold-rand cf-rand-decl">
      <span class="mig-sold-cont">${x.tip}</span>
      <span class="cf-perioada">${x.perioada}</span>
      <span class="cf-termen ${clasa}">termen ${dataRo(x.termen)}</span>
    </div>`).join("");

  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b> · <span style="color:${col.dot}">${col.txt}</span></p>
    ${lipsa.length ? `
      <div class="cf-grup-titlu cf-rosu">Restanțe (${lipsa.length})</div>
      <div class="cf-decl">${randDecl(lipsa, "cf-termen-rosu")}</div>` : ""}
    ${urmarit.length ? `
      <div class="cf-grup-titlu cf-galben">De urmărit (${urmarit.length})</div>
      <div class="cf-decl">${randDecl(urmarit, "cf-termen-galben")}</div>` : ""}
    ${(() => { /* cf_detaliu_contabil_v1 */
      const vc = d.verificari_contabile || null;
      if (!vc) return "";
      const probleme = [];
      if (vc.echilibru && vc.echilibru.ok === false) probleme.push("balanță dezechilibrată");
      const tz = vc.trezorerie;
      if ((Array.isArray(tz) && tz.length) || (tz && !Array.isArray(tz) && tz.ok === false)) probleme.push("solduri creditoare trezorerie");
      if (firma.contabil) firma.contabil.forEach((p) => { if (!probleme.includes(p) && p !== "balanta dezechilibrata" && p !== "solduri creditoare trezorerie") probleme.push(p); }); /* cf_detaliu_contabil_v2 */
      if (!probleme.length) return "";
      return `<div class="cf-grup-titlu cf-rosu">Verificări contabile (${probleme.length})</div>
        <div class="cf-decl">${probleme.map((p) => `<div class="mig-sold-rand cf-rand-decl"><span class="mig-sold-cont">${p}</span></div>`).join("")}</div>`;
    })()}
    ${(!lipsa.length && !urmarit.length) ? `
      <div class="mig-gata" style="padding:30px 0">
        <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
        <div class="mig-gata-titlu">Totul depus la zi</div>
      </div>` : ""}
  `;
}
