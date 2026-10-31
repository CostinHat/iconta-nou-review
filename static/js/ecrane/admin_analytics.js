// admin_analytics.js — Admin iConta: analytics public (doar superadmin).
// Cifre ANONIME din public.eveniment_public: pe eveniment, pe zi, pe pagina de provenienta.
// Tabela nu contine niciun identificator (fara IP/UA/cookie/sesiune) -> fara date personale.
import { api, esc, CULORI_CARD, cate, dupaNumar, dataRo } from "../api.js?v=7036a2d894";
import { siraCarduri } from "../carduri.js?v=98c15a1738";   // [lotul 14, 687] explicația despre date anonime e card, nu text pe ecran

// [lotul 13, deficiența 649 — „Cifrele includ vizitele noastre de testare […]; nu se pot separa vizitatorii reali. Fără a adăuga
// identificatori: evenimentele venite dintr-un browser cu sesiune iConta deschisă (cabinet sau admin) nu se numără, ori se arată separat.”]
// Varianta aleasă: NU SE NUMĂRĂ. Pagina principală a cabinetului / asistentului și Panou Admin scriu în browser (localStorage, nu cookie,
// nimic trimis serverului) momentul ultimei sesiuni deschise; pagina publică (login.js) nu trimite evenimentul cât acel moment e mai nou de
// `FEREASTRA_SESIUNE_MS` (durata unei sesiuni, 24 h). Serverul nu primește și nu ține nimic în plus: tabela rămâne fără identificatori.
export const CHEIE_SESIUNE_INTERNA = "iconta_sesiune_interna";
export const FEREASTRA_SESIUNE_MS = 24 * 3600 * 1000;
export function marcheazaSesiuneInterna() {
  try { localStorage.setItem(CHEIE_SESIUNE_INTERNA, String(Date.now())); } catch (_e) { /* navigare privată: nimic de marcat */ }
}
export function sesiuneInternaDeschisa(acum = Date.now()) {
  try {
    const t = Number(localStorage.getItem(CHEIE_SESIUNE_INTERNA) || 0);
    return t > 0 && acum - t < FEREASTRA_SESIUNE_MS;
  } catch (_e) { return false; }
}

const C = CULORI_CARD.albastru;
//: [649] ziua de la care vizitele dintr-o sesiune iConta deschisă nu se mai numără (publicarea lotului 13); de potrivit la publicare
export const NUMARARE_FARA_INTERN_DE_LA = "2026-10-26";

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
    corp.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca cifrele.</p>`;
    return;
  }
  // [lotul 14, 687] sus (fix): titlul, numărul de evenimente, cardul „Date anonime” și nota despre vizitele interne; cele trei liste stau
  // pe trei coloane, iar zona lor derulează (lista pe zile are 30 de rânduri)
  corp.innerHTML = `
    <div class="an-antet rezumat-fix">
      <h2 class="pf-titlu">Analytics public — ${d.zile === 1 ? "ultima zi" : "ultimele " + cate(d.zile, "zi", "zile")}</h2>
      <p class="ecran-nota"><strong>${Number(d.total) || 0}</strong> ${dupaNumar(Number(d.total) || 0, "eveniment înregistrat", "evenimente înregistrate")}.</p>
      <div id="an-carduri"></div>
      <p class="ecran-nota" id="an-intern">Nu se numără vizitele dintr-un browser în care e deschisă o sesiune iConta.eu (cabinet sau Panou
        Admin) — testele noastre. Zilele de dinainte de ${dataRo(NUMARARE_FARA_INTERN_DE_LA)} le cuprind încă.</p>
    </div>
    <div data-zona-derulare><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:4px 24px">
      <div>${sectiune("Pe eveniment", d.pe_eveniment, (r) => ETICHETE[r.tip] || r.tip)}</div>
      <div>${sectiune("Pe zi", d.pe_zi, (r) => dataRo(r.zi))}</div>
      <div>${sectiune("Pe pagină de proveniență", d.pe_pagina, (r) => r.pagina)}</div>
    </div></div>
  `;
  siraCarduri(corp.querySelector("#an-carduri"), [{ id: "an-card-anonime", ton: "ok", text: "Date anonime, fără identificatori", titlu: "Date anonime",
    deschide: (c) => { c.innerHTML = `<p class="ecran-nota">Se rețin doar tipul evenimentului, pagina de proveniență și momentul. Fără IP, fără cookie, fără amprentă de browser, fără niciun identificator de persoană.</p>`; } }], nav);
}
