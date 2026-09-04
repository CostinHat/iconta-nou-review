// admin_analytics.js — Admin iConta: analytics public (doar superadmin).
// Cifre ANONIME din public.eveniment_public: pe eveniment, pe zi, pe pagina de provenienta.
// Tabela nu contine niciun identificator (fara IP/UA/cookie/sesiune) -> fara date personale.
import { api, esc, CULORI_CARD } from "../api.js?v=1dccbc985b";

const C = CULORI_CARD.albastru;

const ETICHETE = {
  vizita_landing: "Vizite landing",
  modal_functionalitati: "Deschideri modal „Funcționalități și prețuri”",
  deschide_preturi: "Deschideri card Prețuri",
  intra_in_cont: "Click „Intră în cont”",
  vizita_ghid: "Vizite pagini de ghid",
};

function bara(n, max) {
  const pct = max > 0 ? Math.round((n / max) * 100) : 0;
  return `<div class="an-bara" style="height:6px;overflow:hidden;background:${C.bg};margin-top:5px">`
    + `<div style="height:100%;width:${pct}%;background:${C.fg}"></div></div>`;
}

function sectiune(titlu, randuri, label) {
  if (!randuri || !randuri.length) {
    return `<h2 class="pf-titlu">${esc(titlu)}</h2><div class="stare-goala">Niciun eveniment încă.</div>`;
  }
  const max = Math.max.apply(null, randuri.map((r) => Number(r.n) || 0));
  const lst = randuri.map((r, i) => `
    <div class="pf-frand" data-zebra="${i % 2}">
      <div class="pf-frand-text">
        <div class="pf-frand-nume">${esc(label(r))}</div>
        ${bara(Number(r.n) || 0, max)}
      </div>
      <strong class="an-cifra" style="margin-left:12px">${Number(r.n) || 0}</strong>
    </div>`).join("");
  return `<h2 class="pf-titlu">${esc(titlu)}</h2><div class="pf-lista zebra-lista">${lst}</div>`;
}

export async function randeazaAdminAnalytics(corp, nav) {
  const f = corp.closest(".fereastra");
  if (f) f.classList.add("fer-larg-simplu");
  corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
  let d;
  try {
    d = await api.get("/admin/analytics?zile=30");
  } catch {
    corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca cifrele.</p>`;
    return;
  }
  corp.innerHTML = `
    <div class="an-antet">
      <h2 class="pf-titlu">Analytics public — ultimele ${d.zile} zile</h2>
      <p class="ecran-nota"><strong>${Number(d.total) || 0}</strong> evenimente înregistrate. Date anonime:
        se rețin doar tipul evenimentului, pagina de proveniență și momentul. Fără IP, fără cookie, fără
        amprentă de browser, fără niciun identificator de persoană.</p>
    </div>
    ${sectiune("Pe eveniment", d.pe_eveniment, (r) => ETICHETE[r.tip] || r.tip)}
    ${sectiune("Pe zi", d.pe_zi, (r) => r.zi)}
    ${sectiune("Pe pagină de proveniență", d.pe_pagina, (r) => r.pagina)}
  `;
}
