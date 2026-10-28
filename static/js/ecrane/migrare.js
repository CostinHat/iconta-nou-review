// migrare.js  // [p127_mig_loading] — Migrare cabinet  // [p86_fara_intro]  // [p85_fix]: meniu de operațiuni (straturi) + wizard per strat.
// Strat 1 (Firme) e funcțional: import ANAF -> decizie de finalizare (gata / mai am + notă).
// Restul straturilor: placeholder până le construim. Starea fiecăruia vine din /migrare/status.

import { api, ultimaCerere, esc, dataRo, bani, CULORI_CARD, baniRotund, arataMesaj, confirmaCaseta, cantitate, focusFaraSalt, eroareCamp, curataEroriCamp, ALEGE, dataIso, cate, dupaNumar, selectDaNu, daNu, cereAlegerile, alegeDacaLipseste } from "../api.js?v=c6c45aefe4";

// C2 (audit tenant_003): mesaj de succes care supravietuieste nav.inapoiPas() (tiparul _bonuriMesaj din
// firme.js). Setat de handlerele de salvare INAINTE de inapoiPas; consumat la re-randarea ecranului la care
// se revine. DS cap.6: succes = arataMesaj "ok" (verde), pe ecranul principal dupa revenire.
// [lotul 10, deficiența 423 a — clasa 410, DS cap.27] „după salvare nu apare niciun mesaj de confirmare”: mesajul se consuma NUMAI în
// meniul per firmă, iar pe drumul Migrare cabinet → <strat> → <firmă> salvarea revenea în lista stratului, care nu-l arăta (și ieșea mai
// târziu, în alt ecran). Acum ORICE ecran în care se revine după o salvare îl arată: fiecare funcție care deschide un pas (`nav.mergi` /
// `nav.deschide`) cheamă `_consumaMigMesaj(corp)` după ce s-a desenat. Gard: core/test_lot10_import_mesaje.py.
let _migMesaj = "";
let _migTip = "ok";   // [C24/C25] „avert” când salvarea a lăsat rânduri pe dinafară (succesul nu e întreg)
function _consumaMigMesaj(corp) {
  if (!_migMesaj || !corp) return;
  const z = document.createElement("div");
  z.style.margin = "0 0 6px";   // [lotul 11, 394 la 1280×720] confirmarea + aplicația aleasă încap fără derulare
  corp.insertBefore(z, corp.firstChild);
  arataMesaj(z, _migMesaj, _migTip);
  _migMesaj = ""; _migTip = "ok";
}
// [lotul 13, comanda Costin 13.1 — 663: „Stările pașilor sunt pe cabinet, nu pe firma în lucru”; 664: „Salvarea trebuie să ducă la pașii
// următori necesari.”; 580: „Lista straturilor și fiecare ecran de import nu arată ce s-a adus deja”; 584: „nu spun ce există deja […] și dacă
// importul adaugă, dublează sau înlocuiește”] STAREA PAȘILOR DE PRELUARE AI FIRMEI, derivată pe server din datele ei (`GET /migrare/firma/{id}`,
// `audit_preluare.stare_pasi`): o singură sursă pentru meniul Migrare cabinet (firma în lucru), meniul „Import date” al firmei, ecranele de
// import, mesajul de după salvare și fereastra firmei (662). Stările: gata / obligatoriu / nu e cazul / dacă e cazul.
const _caleStare = (tenantId) => `/migrare/firma/${encodeURIComponent(tenantId)}`;
async function _starePreluare(tenantId) {
  if (!tenantId) return null;
  try { return await api.get(_caleStare(tenantId)); } catch { return null; }
}
const CLASA_PAS = { gata: "mig-b-gata", obligatoriu: "mig-b-oblig", nu_e_cazul: "mig-b-curand", optional: "mig-b-curand" };
function _badgePas(p) {
  return p ? `<span class="mig-badge ${CLASA_PAS[p.stare] || "mig-b-curand"}" data-stare-pas="${esc(p.stare)}">${esc(p.eticheta)}</span>` : "";
}
function _titluStrat(cheie) { return (STRATURI.find((s) => s.cheie === cheie) || {}).titlu || cheie; }
// [664] pașii obligatorii rămași, numiți cu motivul lor (ce cont, ce sumă)
function _textUrmatori(st) {
  const u = (st && st.urmatori) || [];
  if (!u.length) return "";
  return `Pașii următori necesari pentru ${st.nume}:\n` + u.map((k) => `• ${_titluStrat(k)} — ${st.pasi[k].detaliu}`).join("\n");
}
// [664] după o salvare: confirmarea + pașii următori necesari ai firmei, pe ecranul în care se revine
// (fiecare salvare cheamă apoi `nav.inapoiPas()` ea însăși: mesajul și revenirea stau în aceeași funcție — garda 423a)
const cerereUrmatori = ultimaCerere();   // [C103] două salvări în șir: numai pașii următori ai ultimei ajung în mesaj
async function _adaugaUrmatorii(firma) {
  if (!firma || !firma.tenant_id) return;
  const actuala = cerereUrmatori();
  let st = null;
  try {
    st = await api.get(_caleStare(firma.tenant_id));
    if (!actuala()) return;
  } catch { if (!actuala()) return; }
  const t = _textUrmatori(st);
  if (t) { _migMesaj += (_migMesaj ? "\n" : "") + t; if (_migTip === "ok") _migTip = "avert"; }   // se adaugă la confirmarea salvării
}
// [580, 584] sub introducerea ecranului de import: ce s-a adus deja la pas și ce face importul cu ce există
async function _existaPas(corp, firma, strat) {
  const intro = corp.querySelector(".mig-intro");
  const st = await _starePreluare(firma && firma.tenant_id);
  const p = st && st.pasi && st.pasi[strat];
  if (!p || !intro || !intro.isConnected) return;
  const el = document.createElement("p");
  el.className = "mig-intro"; el.id = "mig-exista"; el.dataset.existaPas = strat;
  el.textContent = `${p.exista ? "Există deja: " + p.exista + "." : "Nu e nimic adus încă la acest pas."} ${p.comportament || ""}`.trim();
  intro.after(el);
}
// [lotul 10, deficiențele 421 / 424 — contractul cu fereastra (navigator + CSS, DS cap.9)] PREVIZUALIZAREA COMUNĂ a importurilor: rezumatul
// (intro, totaluri, banda stărilor, notele, avertismentele) stă lipit SUS (`rezumat-fix`), acțiunea principală cu mesajul și caseta
// refuzurilor stau lipite JOS (`bara-fixa`), iar tabelul dintre ele nu are derulare proprie. Toate cele nouă previzualizări trec pe aici.
// [lotul 13, deficiențele 667 + 581, comanda Costin 13.1: „Tabelul are derulare proprie și capul acoperă primele rânduri (clasa 285); textul
// explicativ și avertismentul sunt paragrafe lungi” / „casetele roșii fixe strâng tabelul rândurilor într-o bară albă”] în rezumatul lipit
// sus stau NUMAI titlul, totalurile și banda stărilor (butoanele de filtru); casetele (firma din fișier, înlocuirea, confruntarea cu balanța,
// rândurile ignorate, notele, avertismentul rulajelor, refuzurile) stau în pagină, deasupra tabelului — se citesc la încărcare, apoi derulează
// cu tabelul, fără să-l acopere. Gard: core/test_lot13_migr_previzualizare.py.
function _cadruPrev(sus, tabel, jos) {
  return `<div class="rezumat-fix">${sus}</div>${tabel}<div class="bara-fixa">${jos}</div>`;
}
// [lotul 10, deficiența 426 — CLASA] ÎNLOCUIREA CONFIRMATĂ, comună importurilor care înlocuiesc ce exista (balanța, soldurile pe parteneri,
// salariații, mijloacele fixe, istoricul declarațiilor). Comanda Costin 10.1: „Înainte de înlocuire: spune că există deja […], arată
// totalurile vechi și noi, cere confirmare”. Caseta de sus (`#mig-inlocuire`) arată textul serverului (`avertisment_inlocuire`: ce există,
// ce aduce fișierul, datele care se sprijină pe ele); salvarea cere confirmarea explicită; un 409 de la server (datele au apărut între
// timp) deschide aceeași confirmare, cu textul lui. Gard: core/test_lot10_inlocuire_clasa.py.
// [lotul 11, deficiența 446, comanda Costin 11.1 pct.14, verbatim în DECIZII: „la confirmarea duplicatelor, avertismentul apare de două
// ori, tabelul se strânge la un rând, iar «Salvează salariații» rămâne activ lângă «Actualizez fișele». Avertismentul nu e eroare.”]
// - avertismentul (textul serverului) stă O SINGURĂ DATĂ, sus, cu stilul avertismentului (`arataMesaj(…, "avert")`, DS cap.6: galben),
//   nu în caseta roșie a refuzului; zona e goală în șablon și se umple după desenare (`_arataInlocuirea`);
// - la salvare, confirmarea e o întrebare scurtă (`intrebare`), nu încă o dată avertismentul, deci bara de jos rămâne mică și tabelul
//   își păstrează locul;
// - cât confirmarea e deschisă, butonul principal e ascuns: o singură acțiune activă („Actualizez fișele” / „Renunță”); revine la „Renunță”.
function _casetaInlocuire(date) {
  return date.avertisment_inlocuire ? `<div id="mig-inlocuire" role="status"></div>` : "";
}
function _arataInlocuirea(corp, date, nav) {
  const z = corp.querySelector("#mig-inlocuire");
  // [lotul 14, 687] avertismentul înlocuirii e un card-rezumat de un rând (textul serverului, întreg, în fereastra cardului): nu mai împinge tabelul în jos
  if (z && date.avertisment_inlocuire) siraCarduri(z, [{ id: "inlocuire", ton: "atentie", text: "Firma are deja date de acest fel: salvarea le înlocuiește", titlu: "Înlocuirea datelor existente",
    deschide: (c) => { c.innerHTML = `<h2 class="pf-titlu">Înlocuirea datelor existente</h2><div id="mig-inlocuire-text"></div>`; arataMesaj(c.querySelector("#mig-inlocuire-text"), date.avertisment_inlocuire, "avert"); } }], nav);
}
// [deficiența 599, comanda Costin 12.1: „Importul de migrare primește fără întrebare balanța altei firme […]; compară firma din fișier
// cu firma aleasă și cere confirmare când diferă, la toate importurile.”] FIRMA DIN FIȘIER, comună celor nouă importuri: serverul citește
// denumirea / CUI-ul din antetul fișierului și le compară cu firma aleasă (`uc_migrare.firma_fisier` -> `date.firma_fisier`); când diferă,
// avertismentul stă sus (`_casetaFirma` / `_arataFirma`, lângă cel al înlocuirii), iar salvarea pornește numai după „Da, sunt ale acestei
// firme” (`_cuFirmaConfirmata`, înaintea confirmării înlocuirii). Gard: core/test_lot12_migr_firma_fisier.py.
function _firmaDifera(date) {
  return !!(date && date.firma_fisier && date.firma_fisier.difera);
}
function _casetaFirma(date) {
  return _firmaDifera(date) ? `<div id="mig-firma-fisier" role="alert"></div>` : "";
}
function _arataFirma(corp, date, nav) {
  const z = corp.querySelector("#mig-firma-fisier");
  // [lotul 14, 687] „Fișierul pare al altei firme” — card-rezumat (textul întreg, în fereastra cardului); salvarea cere în continuare confirmarea explicită
  if (z && _firmaDifera(date)) siraCarduri(z, [{ id: "firma-fisier", ton: "atentie", text: "Fișierul pare al altei firme: verifică înainte de salvare", titlu: "Fișierul pare al altei firme",
    deschide: (c) => { c.innerHTML = `<h2 class="pf-titlu">Fișierul pare al altei firme</h2><div id="mig-firma-fisier-text"></div>`; arataMesaj(c.querySelector("#mig-firma-fisier-text"), date.firma_fisier.mesaj, "avert"); } }], nav);
}
function _confirmaInLoculButonului(zona, mesajHtml, textOk, laConfirm) {
  const bara = zona.closest(".bara-fixa");
  const buton = bara ? bara.querySelector("button.mig-buton") : null;
  if (buton) buton.hidden = true;
  confirmaCaseta(zona, mesajHtml, () => { if (buton) buton.hidden = false; laConfirm(); }, { textOk });
  const nu = document.getElementById("ca-nu");
  if (nu && buton) nu.addEventListener("click", () => { buton.hidden = false; });
}
// [599] fișierul altei firme: salvarea (și, după ea, confirmarea înlocuirii) pornește numai după „Da, sunt ale acestei firme”
function _cuFirmaConfirmata(zona, date, continua) {
  if (!_firmaDifera(date)) { continua(); return; }
  _confirmaInLoculButonului(zona, esc(date.firma_fisier.intrebare), "Da, sunt ale acestei firme", continua);
}
function _confirmaInlocuirea(zona, date, textOk, salveaza, intrebare) {
  if (!date.avertisment_inlocuire) { salveaza(false); return; }
  _confirmaInLoculButonului(zona, esc(intrebare), textOk, () => salveaza(true));
}
function _inlocuire409(e, inlocuieste, zona, textOk, salveaza) {
  if (!(e && e.cod === 409 && !inlocuieste)) return false;
  _confirmaInLoculButonului(zona, esc(e.mesaj || ""), textOk, () => salveaza(true));   // datele au apărut între timp: textul serverului
  return true;
}
import { sesiune } from "../sesiune.js?v=898215e0ee";
import { siraCarduri } from "../carduri.js?v=98c15a1738";   // [lotul 14, 687]
import { permis } from "../drepturi.js?v=34d0fb0afd";  /* [drepturi_rol 04.10.2026] meniul de import fără niciun pas permis spune de ce */

// [drepturi_rol 04.10.2026] `actiune` = ruta care FACE pasul (METODĂ /cale, ca în main.py). Ghidul de bun venit
// arată numai pașii permiși utilizatorului (comanda Costin pct.5), iar rândurile meniurilor de import poartă
// `data-actiune` — poarta din drepturi.js le ascunde pe cele refuzate. Pasul „Firme” e al administratorului.
export const STRATURI = [
  { cheie:"firme", actiune:"POST /tenants|POST /migrare/importa", nr:1, titlu:"Firme", desc:"Validare CUI la ANAF · identificare + status fiscal",
    ...CULORI_CARD.albastru, construit:true,
    icon:'<path d="M3 21h18"/><path d="M5 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16"/><path d="M19 21V11a2 2 0 0 0-2-2h-2"/><path d="M9 7h2M9 11h2M9 15h2"/>' },
  { cheie:"vector_fiscal", actiune:"POST /tenants/{tenant_id}/vector", nr:2, titlu:"Vector fiscal", desc:"Ce declarații datorează firma (TVA, regim, intracomunitar)",
    ...CULORI_CARD.chihlimbar, obligatoriu:true, construit:true,
    icon:'<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>' },  // [p84_vector_front]
  { cheie:"solduri", actiune:"POST /tenants/{tenant_id}/solduri", nr:3, titlu:"Solduri inițiale", desc:"Balanța de deschidere per firmă (aduce și planul analitic)",
    ...CULORI_CARD.verde, obligatoriu:true, construit:true,
    icon:'<path d="M12 3v18"/><path d="M5 8h14"/><path d="M5 8l-2 5h4z"/><path d="M19 8l-2 5h4z"/>' },
  { cheie:"solduri_parteneri", actiune:"POST /tenants/{tenant_id}/parteneri", nr:4, titlu:"Solduri parteneri", desc:"4111/401 defalcat per client și furnizor",
    ...CULORI_CARD.teal, construit:true,
    icon:'<path d="M7 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z"/><path d="M17 21a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z"/><path d="M8.5 7L16 17"/>' },
  { cheie:"salariati", actiune:"POST /tenants/{tenant_id}/salariati-import", nr:5, titlu:"Salariați", desc:"Nume, CNP, salariu, date contract (payroll + D112)",
    ...CULORI_CARD.piersica, construit:true,
    icon:'<circle cx="9" cy="7" r="3"/><path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/><path d="M16 3.5a3 3 0 0 1 0 7M21 21v-2a4 4 0 0 0-3-3.8"/>' },
  { cheie:"asociati", actiune:"POST /tenants/{tenant_id}/asociati-import", nr:6, titlu:"Asociați", desc:"Nume, cotă % (pentru D205, dividende)",
    ...CULORI_CARD.violet, construit:true,
    icon:'<circle cx="12" cy="8" r="3.2"/><path d="M5 21v-1.5a5 5 0 0 1 5-5h4a5 5 0 0 1 5 5V21"/>' },
  { cheie:"mijloace_fixe", actiune:"POST /tenants/{tenant_id}/mijloace-fixe-import", nr:7, titlu:"Mijloace fixe", desc:"Registru amortizare în curs (valoare · durată · cumulat)",
    ...CULORI_CARD.piersica, construit:true,
    icon:'<path d="M3 21h18"/><path d="M5 21V9l7-5 7 5v12"/><path d="M9 21v-6h6v6"/>' },
  { cheie:"istoric_declaratii", actiune:"POST /tenants/{tenant_id}/istoric-declaratii-import", nr:8, titlu:"Istoric declarații", desc:"Ce s-a depus deja anul curent (ca să nu apară fals restanță)",
    ...CULORI_CARD.ardezie, construit:true,
    icon:'<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 13l2 2 4-4"/>' },
  { cheie:"plan_conturi", actiune:"POST /tenants/{tenant_id}/plan-conturi", nr:9, titlu:"Plan de conturi", desc:"Extinde planul standard cu conturi analitice sau nestandard, pentru firma aleasă",
    ...CULORI_CARD.violet, construit:true,
    icon:'<path d="M4 6h16M4 12h16M4 18h7"/>' },
  // [deficiența 371, comanda Costin 8.2: „Migrare cabinet arată toate straturile, filtrate pe regimul și tipul fiecărei firme, din aceeași sursă
  // unică ca meniul per firmă”] pașii care existau numai în meniul firmei; lista lor de firme vine filtrată de server (`/migrare/firme`)
  { cheie:"rip", actiune:"POST /tenants/{tenant_id}/rip-import/incarca", nr:10, titlu:"Import RIP (PFA)", desc:"Registrul de încasări și plăți al anului (partidă simplă)",
    ...CULORI_CARD.verde, construit:true, peFirma:(c, n, f) => importRipFirma(c, n, f),
    icon:'<path d="M4 4h16v16H4z"/><path d="M8 9h8M8 13h8M8 17h5"/>' },
  { cheie:"articole", actiune:"POST /tenants/{tenant_id}/articole-import", nr:11, titlu:"Articole și stoc inițial", desc:"Nomenclatorul de articole și cantitățile la preluare",
    ...CULORI_CARD.chihlimbar, construit:true, peFirma:(c, n, f) => importArticoleFirma(c, n, f),
    icon:'<path d="M3 7l9-4 9 4-9 4z"/><path d="M3 7v10l9 4 9-4V7"/>' },
  { cheie:"retete", actiune:"POST /tenants/{tenant_id}/retete-import", nr:12, titlu:"Rețete (HoReCa)", desc:"Rețetarul: ingredientele pe porție (după articolele din stoc)",
    ...CULORI_CARD.teal, construit:true, peFirma:(c, n, f) => importReteteFirma(c, n, f),
    icon:'<path d="M6 3v8a3 3 0 0 0 6 0V3"/><path d="M9 3v18"/><path d="M17 3c-2 2-2 6 0 8v10"/>' },
];

// [371] lista firmelor cărora li se aplică un strat (`/migrare/firme?strat=`, filtrată de server după regimul fiecărei firme); clicul
// deschide importul pe firma aleasă
async function wizardFirmeStrat(corp, nav, st) {
  nav.setInapoi(undefined);
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se încarcă firmele…</p>`;
  let firme = [];
  try { firme = ((await api.get(`/migrare/firme?strat=${encodeURIComponent(st.cheie)}`)) || {}).firme || []; } catch (e) {
    // DS cap.6: eroarea de încărcare e un mesaj (`.ecran-nota`), nu starea „listă goală”
    corp.innerHTML = `<p class="ecran-nota">Firmele nu s-au putut încărca: ${esc((e && e.mesaj) || "eroare")}.</p>`; return;
  }
  corp.innerHTML = `<p class="mig-intro">${esc(st.desc)}. Alege firma.</p><div class="mig-lista" id="mig-firme"></div>`;
  const lista = corp.querySelector("#mig-firme");
  if (!firme.length) lista.innerHTML = `<div class="stare-goala">Nicio firmă din portofoliu nu are pasul „${esc(st.titlu)}” (se aplică după regimul firmei).</div>`;
  firme.forEach((f) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    // [lotul 13, 668: „Lista de firme de aici nu are stări (ce firme au articole / au nevoie)”] starea pasului pe fiecare firmă (serverul)
    const ps = f.stare;
    rand.innerHTML = `<div class="mig-frand-text"><div class="mig-frand-nume">${esc(f.nume)}</div><div class="mig-frand-sub">${esc(f.cui || "")}${ps
      ? " · " + esc(ps.stare === "gata" && ps.exista ? ps.exista : ps.detaliu) : ""}</div></div>${_badgePas(ps)}`;
    rand.addEventListener("click", () => {
      // [396, clasa: ecranul unei firme deschis de la nivelul cabinetului] firma ale cărei date se importă devine firma în lucru, înainte
      // de pas (meniul firmei, `#fa-import`, o are deja: e deschis din fereastra ei)
      if (nav.setFirmaInLucru && (!nav.firmaInLucruId || nav.firmaInLucruId() !== f.tenant_id)) nav.setFirmaInLucru(f.nume || "", f.tenant_id);
      nav.mergi(st.titlu + " \u00b7 " + (f.nume || ""), (c) => st.peFirma(c, nav, f));
    });
    lista.appendChild(rand);
  });
  _consumaMigMesaj(corp);   // [423 a] confirmarea importului salvat dintr-o firmă a acestei liste (RIP, articole, rețete)
}

const SVG = (d, c) => `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="${c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`;

// [270, comanda Costin 15.10.2026, verbatim în DECIZII] Aplicația din care migrează cabinetul, aleasă din butoanele de sus. Registrul
// (ce aplicații sunt, care e activă, ce export se scoate pe fiecare pas) vine de la server (`GET /migrare/aplicatii`, sursa unică
// `core/aplicatii_migrare.py`): o aplicație devine activă când i se adaugă acolo un cititor, fără nicio schimbare aici.
// `null` = nicio aplicație aleasă: pașii cu modelele CSV, ca până acum. Ecranul per firmă („Import date”) nu o folosește.
let _aplicatie = null;

export function randeazaMigrare(corp, nav) {
  _aplicatie = null;
  meniuMigrare(corp, nav);
}

// exportul de scos din aplicația aleasă pentru pasul `cheie` — numai pe un pas pe care iConta.eu îl citește; altfel null
function _exportPas(app, cheie) {
  return (app && app.pasi && app.pasi[cheie] && app.pasi[cheie].export) || null;
}
function _exportHTML(app, cheie) {
  const e = _exportPas(app, cheie);
  return e ? `<p class="mig-intro" data-export-pas="${esc(cheie)}">Scoate din ${esc(app.nume)}: ${esc(e)}.</p>` : "";
}
function _enumera(xs) {
  return xs.length < 2 ? (xs[0] || "") : xs.slice(0, -1).join(", ") + " și " + xs[xs.length - 1];
}

// [270 b] textul de sub butoane, verbatim din comanda lui Costin
// [394, decizia Costin 19.10.2026 „Instrucțiunile pliate”, verbatim în DECIZII „Închiderea lotului 9”] textul stă într-un „Cum se face”
// pliat, deschis la cerere — toggle-ul secundar al aplicației (`<details class="dec-xml">`, DS v2.54 / v2.83); pașii rămân neatinși
const TEXT_FARA_BUTON = `
  <details class="dec-xml" id="mig-apl-cum"><summary>Cum se face</summary>
  <div class="mig-intro" id="mig-apl-text">
    <p style="margin:0 0 4px">Dacă aplicația ta nu are buton activ:</p>
    <ol style="margin:0 0 6px;padding-left:22px">
      <li>Trimite-ne din «Suport» → «Cerere import din altă aplicație» o captură cu meniul de export din aplicația ta și exportul unei singure firme (balanța de verificare, partenerii cu soldurile lor, salariații, mijloacele fixe).</li>
      <li>Analizăm exportul și îți răspundem dacă și când îl putem prelua automat.</li>
      <li>Până atunci, poți începe preluarea cu pașii de mai jos, folosind șabloanele CSV sau Excel.</li>
    </ol>
    <p style="margin:0">Fișierele trimise sunt văzute doar de echipa iConta.eu, se folosesc numai pentru import și le poți șterge oricând.</p>
  </div>
  </details>`;

function _randeazaAplicatii(zona, aplicatii, corp, nav) {
  const inactive = aplicatii.filter((a) => !a.activa).map((a) => a.nume);
  // [lotul 11, 394 la 1280×720 — decizia Costin 10.3, verbatim în DECIZII „Comanda 10.3” pct.4: „totul încape într-un ecran, fără
  // derulare”] măsurat în Chromium: 4 px de derulare fără aplicație aleasă și 92 px cu aplicația activă aleasă (lotul 9 măsurase numai 1366×768 și
  // 1700×1000, fără aplicație aleasă). „Cum se face” stă pe rândul butoanelor (deschis, se arată peste pași, fără să-i împingă — stil.css
  // `.mig-apl-rand`), nota aplicației alese e pe două rânduri, iar rândurile pașilor sunt cu 2 px mai scunde.
  zona.innerHTML = `
    <div class="mig-apl-rand">
    <div role="group" aria-label="Aplicația din care migrezi" style="display:flex;gap:8px;flex-wrap:wrap">
      ${aplicatii.map((a) => {
        const ales = !!(_aplicatie && _aplicatie.cheie === a.cheie);
        return `<button type="button" class="buton-secundar${ales ? " buton-activ" : ""}" data-aplicatie="${esc(a.cheie)}" data-fara-actiune="alegerea aplicației din care migrezi — schimbă numai textul pașilor"${a.activa ? ` aria-pressed="${ales}"` : ` disabled aria-describedby="mig-apl-inactive"`}>${esc(a.nume)}</button>`;
      }).join("")}
    </div>
    ${TEXT_FARA_BUTON}
    </div>
    ${inactive.length ? `<p class="ecran-nota" id="mig-apl-inactive" style="margin:0 0 4px">${esc(_enumera(inactive))}: iConta.eu nu le citește încă exporturile. Butonul devine activ când începe să le citească.</p>` : ""}
    ${_aplicatie ? `<p class="mig-intro" id="mig-apl-aleasa">Pentru ${esc(_aplicatie.nume)}: unde pasul spune ce să scoți din ${esc(_aplicatie.nume)}, iConta.eu primește exportul direct; la ceilalți folosești modelul CSV.</p>` : ""}`;
  zona.querySelectorAll("button[data-aplicatie]:not([disabled])").forEach((b) => {
    b.addEventListener("click", () => {
      const a = aplicatii.find((x) => x.cheie === b.dataset.aplicatie);
      _aplicatie = (_aplicatie && _aplicatie.cheie === a.cheie) ? null : a;   // al doilea clic revine la pașii cu modele
      meniuMigrare(corp, nav);
    });
  });
}

// ---------- MENIUL DE OPERAȚIUNI ----------
function latime(corp, larg) {
  const f = corp.closest(".fereastra");
  if (f) f.classList.toggle("fer-larg", !!larg);
}

// [C103] un singur contor pe modul: ecranul „Migrare cabinet” e unul (fereastra de sus), iar starea lui (`_aplicatie`) stă tot pe modul
const cerereMeniu = ultimaCerere();   // [C103] aplicația aleasă în șir: numai meniul ultimei alegeri ajunge pe ecran
async function meniuMigrare(corp, nav) {
  const actuala = cerereMeniu();
  nav.setInapoi(null);
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  let status = {}, nrFirme = 0;
  try {
    const s = await api.get("/migrare/status");
    if (!actuala()) return;
    status = (s && s.status) || {};
  } catch { if (!actuala()) return; }
  try {
    const t = await api.get("/tenants");
    if (!actuala()) return;
    nrFirme = ((t && t.tenants) || []).length;
  } catch { if (!actuala()) return; }
  // [lotul 13, 663] cu o firmă în lucru, starea fiecărui pas e a EI (derivată din datele ei), iar pasul se deschide direct pe ea (668:
  // „cere din nou firma deși F7 e în lucru”); fără firmă în lucru, meniul rămâne al cabinetului (deciziile „gata / mai am”)
  const idLucru = nav.firmaInLucruId ? nav.firmaInLucruId() : null;
  // [C103] cererea stă aici, cu jetonul meniului: alegerea aplicației în șir redesenează meniul — numai starea ultimei cereri ajunge pe ecran
  let stareFirma = null;
  if (idLucru) {
    try {
      stareFirma = await api.get(_caleStare(idLucru));
      if (!actuala()) return;
    } catch { if (!actuala()) return; }
  }
  corp.innerHTML = `
    <div id="mig-aplicatii"></div>
    ${stareFirma ? `<p class="mig-intro" id="mig-firma-lucru">Starea pașilor e a firmei în lucru, <b>${esc(stareFirma.nume)}</b>${stareFirma.urmatori.length
      ? ` — de făcut: ${esc(stareFirma.urmatori.map(_titluStrat).join(", "))}` : ""}. Pasul se deschide pe ea; din el poți alege altă firmă.</p>` : ""}
    <div class="mig-meniu" id="mig-meniu"></div>
  `;
  const zonaApl = corp.querySelector("#mig-aplicatii");
  try {
    const r = await api.get("/migrare/aplicatii");
    if (!actuala()) return;
    if (!r || !Array.isArray(r.aplicatii)) throw new Error("registru gol");
    _aplicatie = _aplicatie ? (r.aplicatii.find((a) => a.cheie === _aplicatie.cheie && a.activa) || null) : null;
    _randeazaAplicatii(zonaApl, r.aplicatii, corp, nav);
  } catch {
    if (!actuala()) return;
    // registrul necitit nu e „nicio aplicație”: se spune, iar pașii rămân cu modelele CSV
    _aplicatie = null;
    zonaApl.innerHTML = `<p class="ecran-nota">Lista aplicațiilor din care se poate migra nu s-a putut încărca. Pașii de mai jos merg cu modelele CSV.</p>` + TEXT_FARA_BUTON;
  }
  const meniu = corp.querySelector("#mig-meniu");

  STRATURI.forEach((st) => {
    const stare = status[st.cheie];               // {stare, nota} sau undefined
    const rand = document.createElement(st.construit ? "button" : "div");
    rand.className = "mig-op" + (st.construit ? "" : " mig-op-inactiv");
    if (st.actiune) rand.dataset.actiune = st.actiune;  // [drepturi_rol] pasul refuzat rolului nu se arată
    // [663] pasul firmei în lucru: starea ei; pasul care nu i se aplică (ex. Import RIP la un SRL) se spune ca atare
    const pasFirma = stareFirma && st.cheie !== "firme" ? (stareFirma.pasi[st.cheie] || { stare: "nu_e_cazul", eticheta: "nu e cazul",
      detaliu: "Pasul nu se aplică firmei în lucru (regimul ei).", strain: true }) : null;

    // badge de stare (dreapta)
    let badge = "";
    if (pasFirma) {
      badge = _badgePas(pasFirma);
    } else if (stare && stare.stare === "gata") {
      badge = `<span class="mig-badge mig-b-gata">gata</span>`;
    } else if (stare && stare.stare === "in_lucru") {
      badge = `<span class="mig-badge mig-b-lucru">de continuat</span>`;
    } else if (!st.construit) {
      badge = `<span class="mig-badge mig-b-curand">în curând</span>`;
    } else if (st.obligatoriu) {
      badge = `<span class="mig-badge mig-b-oblig">obligatoriu</span>`;
    }

    // sub-text: progres / notă
    let sub = st.desc;
    let subAlert = false;
    if (st.cheie === "firme" && nrFirme) {
      sub = cate(nrFirme, "firmă importată", "firme importate");
    }
    if (pasFirma) {
      sub = esc(pasFirma.detaliu || st.desc);
      subAlert = pasFirma.stare === "obligatoriu";
    } else if (stare && stare.stare === "in_lucru" && stare.nota) {
      sub = `${esc(stare.nota)}`;
      subAlert = true;
    } else if (_exportPas(_aplicatie, st.cheie)) {
      sub = `Scoate din ${esc(_aplicatie.nume)}: ${esc(_exportPas(_aplicatie, st.cheie))}`;   // [270] pasul citit al aplicației alese
    }

    rand.innerHTML = `
      <span class="mig-op-nr">${st.nr}</span>
      <span class="mig-op-icon" style="background:${st.bg}">${SVG(st.icon, st.fg)}</span>
      <span class="mig-op-text">
        <span class="mig-op-titlu">${st.titlu}</span>
        <span class="mig-op-sub${subAlert ? " mig-op-sub-alert" : ""}">${sub}</span>
      </span>
      ${badge}
    `;
    // [394 „Rânduri mai compacte”] pe ecranul lat descrierea stă pe rândul titlului, tăiată cu „…” (stil.css `.mig-op-sub`); întreagă aici
    const subEl = rand.querySelector(".mig-op-sub");
    subEl.title = subEl.textContent;
    if (st.construit) {
      rand.addEventListener("click", () => {
        // [663, 668] firma în lucru: pasul se deschide direct pe ea, cu „Altă firmă” spre lista cabinetului
        if (pasFirma && !pasFirma.strain) {
          const f = { tenant_id: stareFirma.tenant_id, nume: stareFirma.nume };
          nav.deschide(st.titlu + " \u00b7 " + (f.nume || ""), (cc, nn) => _pasPeFirma(cc, nn, st, f));
          return;
        }
        if (st.cheie === "firme") nav.deschide("Firme", (cc, nn) => wizardFirme(cc, nn));
        else if (st.cheie === "vector_fiscal") nav.deschide("Vector fiscal", (cc, nn) => wizardVector(cc, nn));  // [p84_vector_front]
        else if (st.cheie === "solduri") nav.deschide("Solduri inițiale", (cc, nn) => wizardSolduri(cc, nn));
        else if (st.cheie === "solduri_parteneri") nav.deschide("Solduri parteneri", (cc, nn) => wizardParteneri(cc, nn));
        else if (st.cheie === "salariati") nav.deschide("Salariați", (cc, nn) => wizardSalariati(cc, nn));
        else if (st.cheie === "asociati") nav.deschide("Asociați", (cc, nn) => wizardAsociati(cc, nn));
        else if (st.cheie === "mijloace_fixe") nav.deschide("Mijloace fixe", (cc, nn) => wizardMijloace(cc, nn));
        else if (st.cheie === "istoric_declaratii") nav.deschide("Istoric declarații", (cc, nn) => wizardIstoric(cc, nn));
        else if (st.cheie === "plan_conturi") nav.deschide("Plan de conturi", (cc, nn) => wizardPlanConturi(cc, nn));
        else if (st.peFirma) nav.deschide(st.titlu, (cc, nn) => wizardFirmeStrat(cc, nn, st));   // [371] RIP, articole, rețete
      });
    }
    meniu.appendChild(rand);
  });
  _consumaMigMesaj(corp);   // [423 a] confirmarea deciziei „gata / mai am” a unui pas (randeazaDecizie)
}

// [lotul 13, 663 / 668] pasul deschis direct pe firma în lucru (ecranul de import al firmei), cu „Altă firmă” — lista cabinetului a
// pasului, cu starea fiecărei firme și decizia „gata / mai am” a cabinetului
const LISTA_PAS = {
  vector_fiscal: (c, n) => wizardVector(c, n), solduri: (c, n) => wizardSolduri(c, n), solduri_parteneri: (c, n) => wizardParteneri(c, n),
  salariati: (c, n) => wizardSalariati(c, n), asociati: (c, n) => wizardAsociati(c, n), mijloace_fixe: (c, n) => wizardMijloace(c, n),
  istoric_declaratii: (c, n) => wizardIstoric(c, n), plan_conturi: (c, n) => wizardPlanConturi(c, n),
};
function _ecranPasFirma(cheie) {
  return {
    vector_fiscal: (c, n, f) => formularVectorFirma(c, n, f), solduri: (c, n, f) => importSolduriFirma(c, n, f, _aplicatie),
    solduri_parteneri: (c, n, f) => importParteneriFirma(c, n, f, _aplicatie), salariati: (c, n, f) => importSalariatiFirma(c, n, f, _aplicatie),
    asociati: (c, n, f) => importAsociatiFirma(c, n, f), mijloace_fixe: (c, n, f) => importMijloaceFirma(c, n, f, _aplicatie),
    istoric_declaratii: (c, n, f) => importIstoricFirma(c, n, f), plan_conturi: (c, n, f) => importPlanConturiFirma(c, n, f),
    rip: (c, n, f) => importRipFirma(c, n, f), articole: (c, n, f) => importArticoleFirma(c, n, f), retete: (c, n, f) => importReteteFirma(c, n, f),
  }[cheie];
}
async function _pasPeFirma(corp, nav, st, firma) {
  nav.setInapoi(undefined);
  const ecran = _ecranPasFirma(st.cheie);
  await ecran(corp, nav, firma);
  const bara = document.createElement("div");
  bara.className = "mig-alta-firma";
  bara.innerHTML = `<button type="button" class="buton-secundar" id="mig-alta-firma" data-fara-actiune="alegerea altei firme pentru pasul de import — deschide lista firmelor">Altă firmă</button>`;
  corp.insertBefore(bara, corp.firstChild);
  _consumaMigMesaj(corp);   // [423 a, 664] salvarea din pasul deschis direct revine aici: confirmarea și pașii următori, sus
  bara.querySelector("#mig-alta-firma").addEventListener("click", () =>
    nav.mergi(st.titlu, (c) => (LISTA_PAS[st.cheie] ? LISTA_PAS[st.cheie](c, nav) : wizardFirmeStrat(c, nav, st))));
}

// ---------- WIZARD FIRME ----------
function wizardFirme(corp, nav) {
  pasInput(corp, nav);
}

function pasInput(corp, nav) {
  nav.setInapoi(undefined);
  corp.innerHTML = `
    <p class="mig-intro">Încarcă-ți tot portofoliul în iConta.eu. Verificăm fiecare CUI direct la ANAF și completăm automat denumirea și datele firmei.</p>
    <div class="mig-eticheta">Lipește CUI-urile firmelor (unul pe linie)</div>
    <textarea aria-label="Codurile fiscale ale firmelor, câte unul pe rând" id="mig-text" class="mig-textarea" placeholder="14837428&#10;1590082&#10;RO14399840"></textarea>
    <div class="mig-sau"><span></span>sau<span></span></div>
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" accept=".csv,.txt,.tsv,.xlsx,.xls" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#16a34a" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">Încarcă un fișier</div>
      <div class="mig-drop-desc">Excel sau CSV cu o coloană de CUI-uri</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <button class="buton-primar mig-buton" id="mig-valideaza" data-actiune="POST /migrare/valideaza|POST /migrare/incarca">Validează la ANAF</button>
  `;

  const fileInput = corp.querySelector("#mig-file");
  const dropTitlu = corp.querySelector("#mig-drop-titlu");
  let fisierAles = null;
  fileInput.addEventListener("change", () => {
    fisierAles = fileInput.files[0] || null;
    dropTitlu.textContent = fisierAles ? fisierAles.name : "Încarcă un fișier";
  });

  corp.querySelector("#mig-valideaza").addEventListener("click", async () => {
    const eroare = corp.querySelector("#mig-eroare");
    const buton = corp.querySelector("#mig-valideaza");
    eroare.textContent = "";
    const text = corp.querySelector("#mig-text").value.trim();
    if (!text && !fisierAles) { eroare.textContent = "Lipește CUI-uri sau încarcă un fișier."; return; }
    buton.disabled = true; buton.textContent = "Verific la ANAF…";
    try {
      let raspuns;
      if (fisierAles) {
        raspuns = await incarcaFisier(fisierAles);
      } else {
        const cui_uri = text.split(/[\s,;]+/).filter(Boolean);
        raspuns = await api.post("/migrare/valideaza", { cui_uri });
      }
      const rez = (raspuns && raspuns.rezultate) || [];
      const ignorate = (raspuns && raspuns.ignorate) || [];
      if (rez.length === 0) {
        eroare.textContent = ignorate.length
          ? ((ignorate.length === 1 ? "O intrare lipit\u0103 nu con\u021bine" : cate(ignorate.length, "intrare lipit\u0103", "intr\u0103ri lipite") + " nu con\u021bin") + " un CUI (ex. \u201e" + ignorate[0] + "\u201d) \u2014 un CUI are doar cifre.")
          : "Niciun CUI valid de verificat.";
        buton.disabled = false; buton.textContent = "Validează la ANAF"; return;
      }
      pasRezultate(corp, nav, rez, ignorate);
    } catch (e) {
      arataMesaj(eroare, (e && e.mesaj) || "A apărut o eroare la validare.", "eroare");
      buton.disabled = false; buton.textContent = "Validează la ANAF";
    }
  });
}

async function incarcaFisier(file) {
  const fd = new FormData();
  fd.append("fisier", file);
  const r = await fetch("/migrare/incarca", {
    method: "POST",
    headers: { "Authorization": "Bearer " + sesiune.token() },
    body: fd,
  });
  let date = null;
  try { date = await r.json(); } catch { date = null; }
  if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
  return date;
}

function pasRezultate(corp, nav, rezultate, ignorate) {
  ignorate = ignorate || [];
  const bannerIgnorate = ignorate.length
    ? `<div class="mig-avert" role="status"><b>${cate(ignorate.length, "intrare", "intr\u0103ri")} ${ignorate.length === 1 ? "nu con\u021bine" : "nu con\u021bin"} un CUI</b> \u0219i ${ignorate.length === 1 ? "a fost ignorat\u0103" : "au fost ignorate"}: ${ignorate.slice(0, 8).map((t) => "\u201e" + esc(t) + "\u201d").join(", ")}${ignorate.length > 8 ? " \u2026" : ""}. Un CUI are doar cifre \u2014 verific\u0103 dac\u0103 lipse\u0219te vreo firm\u0103.</div>`
    : "";
  nav.setInapoi(() => pasInput(corp, nav));
  corp.innerHTML = `
    <p class="mig-intro">${(() => {
      // [393, lotul 9] numărul spune câte coduri au ajuns la ANAF: cele cu cifra de control greșită nu se trimit
      const invalide = rezultate.filter((r) => r.cui_invalid).length, laAnaf = rezultate.length - invalide;
      return `${laAnaf ? `S-au verificat <b>${cate(laAnaf, "CUI", "CUI-uri")}</b> la ANAF.` : "Niciun CUI n-a ajuns la ANAF."}${invalide ? ` ${invalide === 1 ? "Un cod are" : `${invalide} coduri au`} cifra de control greșită și nu ${invalide === 1 ? "a fost trimis" : "au fost trimise"} (motivul e pe rând).` : ""}`;
    })()} Bifează firmele pe care le aduci în iConta.eu.</p>
    ${bannerIgnorate}
    <div class="mig-lista" id="mig-lista"></div>
    <div class="mig-eroare" id="mig-eroare"></div>
    <button class="buton-primar mig-buton" id="mig-importa" data-actiune="POST /migrare/importa">Importă firmele bifate</button>
  `;
  const lista = corp.querySelector("#mig-lista");
  rezultate.forEach((r, i) => {
    // [deficiențele 341 + 342, comanda Costin 8.2] o firmă deja în portofoliu nu se mai bifează și nu se mai oferă; un CUI cu cifra de
    // control greșită se numește ca atare (nu „negăsit la ANAF”)
    const deImportat = r.gasit && !r.deja_in_portofoliu;
    const rand = document.createElement("label");
    rand.className = "mig-rand" + (deImportat ? "" : " mig-rand-gol");
    const sub = r.cui_invalid ? esc(r.motiv)
      : r.deja_in_portofoliu ? `CUI ${esc(r.cui)} · e deja în portofoliu${r.nume_in_portofoliu ? " ca „" + esc(r.nume_in_portofoliu) + "”" : ""} — nu se importă a doua oară`
      : r.gasit ? ("CUI " + esc(r.cui) + " · " + (r.platitor_tva ? "plătitor TVA" : "neplătitor TVA"))
      : "nu a fost găsit la ANAF";
    const stare = r.cui_invalid ? ["mig-nok", "CUI greșit"] : r.deja_in_portofoliu ? ["mig-gri", "deja în portofoliu"]
      : r.gasit ? ["mig-ok", "găsită"] : ["mig-nok", "negăsită"];
    rand.innerHTML = `
      <input type="checkbox" data-i="${i}" ${deImportat ? "checked" : "disabled"}>
      <div class="mig-rand-text">
        <div class="mig-rand-nume">${esc(r.gasit ? r.denumire : ("CUI " + r.cui))}</div>
        <div class="mig-rand-sub">${sub}</div>
      </div>
      <span class="mig-stare ${stare[0]}">${stare[1]}</span>
    `;
    lista.appendChild(rand);
  });

  function actButon() {
    const n = lista.querySelectorAll('input[type=checkbox]:checked').length;
    const b = corp.querySelector("#mig-importa");
    b.textContent = n ? `Importă ${cate(n, "firmă", "firme")} în iConta.eu` : "Importă firmele bifate";
    b.disabled = n === 0;
  }
  lista.addEventListener("change", actButon); actButon();

  corp.querySelector("#mig-importa").addEventListener("click", async () => {
    const eroare = corp.querySelector("#mig-eroare");
    const buton = corp.querySelector("#mig-importa");
    eroare.textContent = "";
    const selectate = [];
    lista.querySelectorAll('input[type=checkbox]:checked').forEach((cb) => {
      const r = rezultate[parseInt(cb.dataset.i, 10)];
      selectate.push({ cui: r.cui, denumire: r.denumire });
    });
    if (selectate.length === 0) return;
    buton.disabled = true; buton.textContent = "Import în curs…";
    try {
      const raport = await api.post("/migrare/importa", { firme: selectate });
      pasFinal(corp, nav, raport);
    } catch (e) {
      arataMesaj(eroare, (e && e.mesaj) || "A apărut o eroare la import.", "eroare");
      buton.disabled = false; actButon();
    }
  });
}

// ---------- PAS FINAL: decizie de finalizare ----------
function pasFinal(corp, nav, raport) {
  nav.setInapoi(undefined);
  const creat = (raport && raport.creat) || [];
  const erori = (raport && raport.erori) || [];
  // Clasificare pe COD, nu pe proza. Pana la 21.08.2026 aici era
  // `(e.mesaj || "").includes("există deja")`: cine reformula mesajul din backend strica TACUT
  // numaratoarea, iar ecranul spunea „0 firme erau deja in portofoliu" despre un import in care erau.
  // `regula` vine din nomenclatorul inchis (core/migrare_api.REGULI) si nu se schimba cu textul.
  const dejaExista = erori.filter((e) => e.regula === "deja_exista").length;
  const alteErori = erori.length - dejaExista;
  let avert = "";
  if (dejaExista) avert += `<div class="mig-avert">${cate(dejaExista, "firmă", "firme")} ${dejaExista === 1 ? "era deja" : "erau deja"} în portofoliu — nu s-au dublat.</div>`;
  if (alteErori) avert += `<div class="mig-avert mig-avert-rosu">${cate(alteErori, "firmă", "firme")} ${alteErori === 1 ? "nu a putut fi adăugată" : "nu au putut fi adăugate"}.</div>`;

  // [341] bifa verde numai când chiar s-a adăugat ceva; „0 firme adăugate” nu e un succes
  const sumar = creat.length ? `
    <div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">${cate(creat.length, "firmă adăugată", "firme adăugate")} în iConta.eu</div>
    </div>
    ${avert}` : `<div class="mig-gata-titlu">Nicio firmă nouă adăugată.</div>${avert}`;
  randeazaDecizie(corp, nav, "firme", sumar, "Importul firmelor e complet?");
}

// decizie de finalizare reutilizabilă (firme, solduri, ...)
function randeazaDecizie(corp, nav, strat, sumarHTML, intrebare) {
  corp.innerHTML = `
    ${sumarHTML}
    <div class="mig-eticheta" style="margin-top:6px;">${intrebare}</div>
    <div class="mig-decizie">
      <button class="mig-dec" data-val="gata" id="dec-gata"><span>✓</span> Da, e gata</button>
      <button class="mig-dec" data-val="in_lucru" id="dec-lucru"><span>…</span> Nu, mai am</button>
    </div>
    <div id="mig-nota-zona" style="display:none;">
      <div class="mig-nota-et">Ce mai ai de adus? <span>(obligatoriu)</span></div>
      <textarea aria-label="Notă despre preluare" id="mig-nota" class="mig-textarea" style="height:64px" placeholder="Ex: aștept balanțele de la 2 clienți"></textarea>
    </div>
    <div class="mig-eroare" id="mig-eroare"></div>
    <button class="buton-primar mig-buton" id="mig-salveaza" data-actiune="POST /migrare/status" disabled>Salvează</button>
  `;
  let ales = null;
  const zona = corp.querySelector("#mig-nota-zona");
  const salv = corp.querySelector("#mig-salveaza");
  const decGata = corp.querySelector("#dec-gata");
  const decLucru = corp.querySelector("#dec-lucru");
  function alege(val) {
    ales = val;
    decGata.classList.toggle("mig-dec-sel", val === "gata");
    decLucru.classList.toggle("mig-dec-sel", val === "in_lucru");
    zona.style.display = val === "in_lucru" ? "block" : "none";
    salv.disabled = false;
  }
  decGata.addEventListener("click", () => alege("gata"));
  decLucru.addEventListener("click", () => alege("in_lucru"));
  salv.addEventListener("click", async () => {
    const eroare = corp.querySelector("#mig-eroare");
    eroare.textContent = "";
    if (!ales) return;
    const nota = ales === "in_lucru" ? corp.querySelector("#mig-nota").value.trim() : "";
    if (ales === "in_lucru" && !nota) { eroare.textContent = "Scrie ce mai ai de adus."; return; }
    salv.disabled = true; salv.textContent = "Salvez…";
    try {
      await api.post("/migrare/status", { strat, stare: ales, nota });
      // [lotul 10, 423 a — clasa 410] decizia salvată se confirmă pe ecranul în care se revine (meniul Migrare cabinet)
      const _titlu = (STRATURI.find((x) => x.cheie === strat) || {}).titlu || strat;
      _migMesaj = ales === "gata" ? `Pasul „${_titlu}” e marcat gata.` : `Pasul „${_titlu}” e notat „de continuat”: ${nota}`;
      _migTip = "ok";
      nav.inapoiPas();  // pop pe traseu -> firul reflecta pozitia reala (nu acumuleaza straturi)
    } catch (e) {
      arataMesaj(eroare, (e && e.mesaj) || "Eroare la salvare.", "eroare");
      salv.disabled = false; salv.textContent = "Salvează";
    }
  });
}

// ---------- STRAT 2: SOLDURI INIȚIALE (per firmă) ----------
// [p84_vector_front] ----- STRAT VECTOR FISCAL -----
// ═══════════════════════════════════════════════════════════════════════════
//  PROSPEȚIMEA REZUMATULUI — un necunoscut nu se rotunjește la „știu că nu"
// ═══════════════════════════════════════════════════════════════════════════
// [P3 val B, 09.09.2026] Ecranele de mai jos citesc modelul de citire P2, care întoarce pentru
// fiecare firmă o `prospetime.stare`. Până azi JS-ul o IGNORA — și atunci o firmă al cărei rezumat
// încă nu fusese calculat arăta identic cu una măsurată și găsită goală: „fără parteneri încă",
// „de încărcat". Adică un NECUNOSCUT prezentat ca un NU hotărât, exact interdicția 32/R39
// („niciun X înregistrat" nu poate deveni „nu se datorează").
//
//   curent    → se afișează valoarea. „fără parteneri" e legitim AICI, fiindcă acolo chiar s-a
//               măsurat și chiar nu sunt.
//   invalidat → sursa s-a schimbat după ultimul calcul. Valoarea veche NU se arată drept curentă.
//   lipseste  → niciodată calculat, sau rândul lipsește. Nu se știe.
//   eroare    → ultima încercare a eșuat. Nu se știe — și nu se pretinde altceva.
//
// Cele patru stări vin de la server derivate, nu stocate (`firma_rezumat.citeste`); ecranul doar
// le spune pe nume.
const PROSPETIME = {
  invalidat: { text: "se recalculează", scurt: "se recalculează", clasa: "mig-gri" },
  lipseste: { text: "încă necunoscut", scurt: "de calculat", clasa: "mig-gri" },
  eroare: { text: "temporar indisponibil", scurt: "indisponibil", clasa: "mig-nok" },
};
function starePros(f) {
  // LIPSA CÂMPULUI SE CITEȘTE CA „NU SE ȘTIE", nu ca „e curent".
  //
  // [prins de `test_NEVER_COMPUTED_nu_se_randeaza_ca_gol`, 09.09.2026] Prima formă cădea pe
  // „curent" când `prospetime` lipsea — iar atunci o firmă pe care modelul n-a calculat-o
  // NICIODATĂ apărea ca măsurată și găsită goală. Adică exact defectul pe care garda asta a venit
  // să-l închidă, reintrodus prin valoarea implicită.
  //
  // Toate ecranele care cheamă funcția asta citesc modelul de citire, iar rutele lor pun MEREU
  // câmpul. Dacă totuși lipsește, presupunerea sigură e că nu se știe — nu că se știe.
  return (f && f.prospetime && f.prospetime.stare) || "lipseste";
}
function seStie(f) {
  return starePros(f) === "curent";
}
function prosText(f) {
  return (PROSPETIME[starePros(f)] || PROSPETIME.lipseste).text;
}
function prosScurt(f) {
  return (PROSPETIME[starePros(f)] || PROSPETIME.lipseste).scurt;
}
function prosClasa(f) {
  return (PROSPETIME[starePros(f)] || PROSPETIME.lipseste).clasa;
}
// SUMARUL NU TOPEȘTE NECUNOSCUTUL ÎN NUMITOR. „7 din 14" spune că toate 14 au fost evaluate; dacă
// două n-au fost, minte. Când nu există necunoscute, formularea rămâne cea dinainte — n-are ce
// corecta acolo.
// [prins de `test_sumarul_nu_topeste_necunoscutul_in_numitor`, 09.09.2026] Contoarele de mai jos
// filtrează pe `seStie(f) && f.are_X`, NU doar pe `f.are_X`. O firmă `invalidat` păstrează în
// răspuns ultima valoare cunoscută; numărată fără filtru, ea intra în „2 firme au parteneri" —
// adică o valoare care nu mai e curentă, afirmată ca fiind curentă, în chiar cifra pe care omul o
// citește prima. *Rândul o arăta corect ca «se recalculează»; agregatul o mințea.*
function sumarStrat(firme, cu, eticheta) {
  const nec = firme.filter((f) => !seStie(f)).length;
  const et = cu === 1 ? eticheta.replace(/^au /, "are ") : eticheta;   // verbul acordat cu numărul firmelor care au
  if (nec === 0) return `${cu} din ${cate(firme.length, "firmă", "firme")} ${et}`;
  return `${cate(cu, "firmă", "firme")} ${et} · ${firme.length - cu - nec} fără · ${cate(nec, "necunoscută încă", "necunoscute încă")}`;
}

async function wizardVector(corp, nav) {
  nav.setInapoi(undefined);
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103 firmele\u2026</p>`;
  let firme = [];
  try {
    const r = await api.get("/migrare/vector");
    firme = (r && r.firme) || [];
  } catch {}
  const cu = firme.filter((f) => seStie(f) && f.are_vector).length;
  corp.innerHTML = `
    
    <p class="mig-intro">Spune sistemului ce declara\u021bii datoreaz\u0103 fiecare firm\u0103: dac\u0103 e pl\u0103titoare de TVA, ce regim are (micro/profit) \u0219i dac\u0103 face opera\u021biuni intracomunitare. F\u0103r\u0103 vectorul fiscal firma nu poate fi procesat\u0103.</p>
    <div class="mig-progres">${sumarStrat(firme, cu, "au vectorul completat")}</div>
    <div class="mig-lista" id="mig-firme"></div>
    <button class="buton-primar mig-buton" id="mig-finalizeaza" data-actiune="POST /migrare/status" style="margin-top:16px">Am terminat vectorul fiscal</button>
  `;
  const lista = corp.querySelector("#mig-firme");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio firm\u0103 \u00een portofoliu. Import\u0103 \u00eent\u00e2i firmele (pasul 1).</div>`;
  }
  firme.forEach((f) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    let sub = "de completat";
    if (f.are_vector) {
      const p = [];
      p.push(f.regim_fiscal === "profit" ? "profit" : (f.regim_fiscal === "micro" ? "micro" : "—"));  // null -> —, nu default tacit
      if (f.platitor_tva) p.push("TVA " + (f.tip_decont || ""));
      else p.push("neplatitor TVA");
      if (f.operatiuni_ic) p.push("intracomunitar");
      sub = p.join(" \u00b7 ");
    }
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${seStie(f) ? sub : prosText(f)}</div>
      </div>
      <span class="mig-stare ${seStie(f) ? (f.are_vector ? "mig-ok" : "mig-gri") : prosClasa(f)}">${seStie(f) ? (f.are_vector ? "\u2713 gata" : "de completat") : prosScurt(f)}</span>
    `;
    rand.addEventListener("click", () => nav.deschide("Vector firm\u0103", (cc, nn) => formularVectorFirma(cc, nn, f)));  // [p128_vector_cascada]
    lista.appendChild(rand);
  });
  corp.querySelector("#mig-finalizeaza").addEventListener("click", () => {
    const sumar = `<div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">Vector fiscal: ${cu} din ${cate(firme.length, "firmă", "firme")}</div>
    </div>`;
    randeazaDecizie(corp, nav, "vector_fiscal", sumar, "Vectorul fiscal e complet pentru toate firmele?");
  });
  _consumaMigMesaj(corp);   // [423 a] confirmarea salvării făcute dintr-o firmă a acestei liste
}

async function formularVectorFirma(corp, nav, f) {
  nav.setInapoi(undefined);
  latime(corp, false);
  // [fix_vector_perfirma] Sursa de adevar pentru o firma existenta = vectorul SALVAT. Pe traseul
  // per-firma (meniuMigrarePerFirma) `f` vine cu doar {tenant_id,nume,tip_firma} - fara campurile
  // vectorului si fara cui. Fara asta formularul apare GOL (regim gol, "Nu" tacit la TVA, cui gol -
  // incalca DEFAULT_FISCAL_TACIT cap.17: "nesetat" != "Nu") si ar SUPRASCRIE vectorul la salvare.
  // Citim GET /tenants/{id}/vector (citeste, sursa unica) si completam ce `f` nu aduce.
  corp.innerHTML = `<p class="ecran-nota">Se încarcă vectorul…</p>`;
  try {
    const sv = await api.get(`/tenants/${f.tenant_id}/vector`);
    if (sv && sv.ok !== false) {
      const lua = (a, b) => (a !== undefined ? a : b);   // pastreaza ce a adus `f`, altfel din vectorul salvat
      f = Object.assign({}, f, {
        nume: f.nume != null ? f.nume : sv.nume,
        cui: f.cui != null ? f.cui : sv.cui,
        regim_fiscal: lua(f.regim_fiscal, sv.regim_fiscal),
        platitor_tva: lua(f.platitor_tva, sv.platitor_tva),
        tip_decont: lua(f.tip_decont, sv.tip_decont),
        operatiuni_ic: lua(f.operatiuni_ic, sv.operatiuni_ic),
        regim_contabil: lua(f.regim_contabil, (sv.partida_simpla ? "simpla" : "dubla")),
      });
    }
  } catch {}
  // pre-completez din ANAF (platitor_tva e deja stiut la validarea CUI) daca firma n-are vector
  let tvaInit = f.platitor_tva;
  if (tvaInit === null || tvaInit === undefined) {
    try {
      const r = await api.post("/migrare/valideaza", { cui_uri: [f.cui] });  // [p85_fix]
      const z = (r && r.rezultate && r.rezultate[0]) || null;
      if (z) tvaInit = !!z.platitor_tva;
    } catch {}
  }
  const regim = f.regim_fiscal;   // fara fallback tacit; null la vector necompletat
  const partidaSimpla = f.regim_contabil === "simpla";   // PFA/profesie liberala: n-are regim CIT (micro/profit)
  const decont = f.tip_decont;   // fara preselectie tacita; obligatoriu la plator TVA (ANAF v9 nu aduce periodicitatea)
  const ic = f.operatiuni_ic;    // raw true/false/null: fara preselectie tacita, obligatoriu (decide obligatia D390)
  const tva = !!tvaInit;
  corp.innerHTML = `
    <h2 class="mig-form-titlu">Verificare fiscal\u0103</h2>
    <p class="mig-form-cui">${esc(f.nume)} \u00b7 CUI ${esc(f.cui)}</p>
    <div class="vf-form">
      ${partidaSimpla ? "" : `<div class="vf-grup">
        <div class="vf-eticheta">Regim fiscal <span class="oblig">*</span></div>
        <div class="vf-optiuni" id="vf-regim">
          <button class="vf-opt ${regim==="micro"?"vf-on":""}" data-v="micro">Microîntreprindere</button>
          <button class="vf-opt ${regim==="profit"?"vf-on":""}" data-v="profit">Impozit pe profit</button>
        </div>
      </div>`}
      <div class="vf-grup">
        <div class="vf-eticheta">Pl\u0103titoare de TVA?</div>
        <div class="vf-optiuni" id="vf-tva">
          <button class="vf-opt ${tva?"vf-on":""}" data-v="da">Da</button>
          <button class="vf-opt ${!tva?"vf-on":""}" data-v="nu">Nu</button>
        </div>
      </div>
      <div class="vf-grup" id="vf-decont-grup" style="${tva?"":"display:none"}">
        <div class="vf-eticheta">Periodicitate decont TVA <span class="oblig">*</span></div>
        <span class="camp-ajutor">Lunar (regula, art. 322 alin. 1 Cod fiscal). Trimestrial doar dacă în anul
          precedent cifra de afaceri a fost sub 100.000 euro (curs BNR 31.12) și nu ați efectuat achiziții
          intracomunitare de bunuri — art. 322 alin. 2.
          Obligatorie doar la plătitorii de TVA. Decide dacă D300/D394 se depun lunar sau trimestrial.</span>
        <div class="vf-optiuni" id="vf-decont">
          <button class="vf-opt ${decont==="lunar"?"vf-on":""}" data-v="lunar">Lunar</button>
          <button class="vf-opt ${decont==="trimestrial"?"vf-on":""}" data-v="trimestrial">Trimestrial</button>
        </div>
      </div>
      <div class="vf-grup">
        <div class="vf-eticheta">Opera\u021biuni intracomunitare? <span class="oblig">*</span></div>
        <span class="camp-ajutor">Livr\u0103ri, achizi\u021bii sau prest\u0103ri c\u0103tre/de la parteneri din UE.
          D390 se depune numai pentru lunile \u00een care exist\u0103 astfel de opera\u021biuni (instruc\u021biuni
          completare D390, anexa OPANAF 394/2017, pct. 1.2).</span>
        <div class="vf-optiuni" id="vf-ic">
          <button class="vf-opt ${ic === true ? "vf-on" : ""}" data-v="da">Da</button>
          <button class="vf-opt ${ic === false ? "vf-on" : ""}" data-v="nu">Nu</button>
        </div>
      </div>
      <div class="mig-eroare" id="vf-eroare"></div>
      <button class="buton-primar mig-buton" id="vf-salveaza" data-actiune="POST /tenants/{tenant_id}/vector" style="margin-top:8px">Salveaz\u0103 vectorul</button>
    </div>
  `;
  // selectie exclusiva in fiecare grup
  function grup(id, onChange) {
    const z = corp.querySelector(id);
    z.querySelectorAll(".vf-opt").forEach((b) => {
      b.addEventListener("click", () => {
        z.querySelectorAll(".vf-opt").forEach((x) => x.classList.remove("vf-on"));
        b.classList.add("vf-on");
        if (onChange) onChange(b.dataset.v);
      });
    });
    const on = z.querySelector(".vf-on");
    return () => (z.querySelector(".vf-on") || {}).dataset?.v;
  }
  const getRegim = partidaSimpla ? (() => null) : grup("#vf-regim");   // partida simpla: nu trimite regim_fiscal
  const getTva = grup("#vf-tva", (v) => {
    corp.querySelector("#vf-decont-grup").style.display = (v === "da") ? "" : "none";
  });
  const getDecont = grup("#vf-decont");
  const getIc = grup("#vf-ic");
  corp.querySelector("#vf-salveaza").addEventListener("click", async () => {
    const er = corp.querySelector("#vf-eroare");
    er.textContent = "";
    corp.querySelectorAll("#vf-regim, #vf-tva, #vf-decont, #vf-ic").forEach((z) => { z.classList.remove("camp-invalid"); z.removeAttribute("aria-invalid"); });
    const platitor = getTva() === "da";
    // DS cap.6 pct.4: COLECTEAZA toate campurile obligatorii lipsa si le marcheaza pe toate odata (fail-fast INTERZIS)
    const _lipsa = [];
    if (!partidaSimpla && !getRegim()) _lipsa.push(["vf-regim", "regimul fiscal"]);
    if (getTva() !== "da" && getTva() !== "nu") _lipsa.push(["vf-tva", "dacă e plătitoare de TVA (Da/Nu)"]);
    if (platitor && !getDecont()) _lipsa.push(["vf-decont", "periodicitatea decontului de TVA"]);
    if (getIc() !== "da" && getIc() !== "nu") _lipsa.push(["vf-ic", "operațiunile intracomunitare (Da/Nu)"]);
    if (_lipsa.length) {
      _lipsa.forEach(([id]) => { const g = corp.querySelector("#" + id); if (g) { g.classList.add("camp-invalid"); g.setAttribute("aria-invalid", "true"); } });
      const _prima = corp.querySelector("#" + _lipsa[0][0]); if (_prima) _prima.scrollIntoView({ block: "center" });
      er.textContent = "Completează: " + _lipsa.map((x) => x[1]).join(", ") + ".";
      return;
    }
    const payload = {
      regim_fiscal: getRegim(),
      platitor_tva: platitor,
      tip_decont: platitor ? getDecont() : null,
      // obligatoriu, fara default tacit: nimic ales -> null -> backend respinge (400). NU coercem la false.
      operatiuni_ic: getIc() === "da" ? true : (getIc() === "nu" ? false : null),
    };
    try {
      await api.post(`/tenants/${f.tenant_id}/vector`, payload);
      _migMesaj = "Vector fiscal salvat."; await _adaugaUrmatorii(f); nav.inapoiPas();   // [lotul 13, 664]
    } catch (e) {
      const _eris = (e && e.erori_campuri) || [];
      const _MAP = { regim_fiscal: "vf-regim", platitor_tva: "vf-tva", tip_decont: "vf-decont", operatiuni_ic: "vf-ic", tva_data_inceput: "vf-decont" };
      _eris.forEach((x) => { const g = corp.querySelector("#" + (_MAP[x.camp] || "_none")); if (g) { g.classList.add("camp-invalid"); g.setAttribute("aria-invalid", "true"); } });
      er.textContent = (e && (e.mesaj || e.message)) || "Nu s-a putut salva. \u00cencearc\u0103 din nou.";
    }
  });
}

async function wizardSolduri(corp, nav) {
  nav.setInapoi(undefined);
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se încarcă firmele…</p>`;
  let firme = [];
  try {
    const r = await api.get("/migrare/solduri");
    firme = (r && r.firme) || [];
  } catch {}

  const cuSolduri = firme.filter((f) => seStie(f) && f.are_solduri).length;
  corp.innerHTML = `
    <p class="mig-intro">Încarcă balanța de deschidere pentru fiecare firmă. Soldurile devin poziția de pornire, iar conturile analitice (clienți, furnizori) intră automat în plan.</p>
    <div class="mig-progres">${sumarStrat(firme, cuSolduri, "au solduri")}</div>
    <div class="mig-lista" id="mig-firme"></div>
    <button class="buton-primar mig-buton" id="mig-finalizeaza" data-actiune="POST /migrare/status" style="margin-top:16px">Am terminat soldurile inițiale</button>
  `;

  const lista = corp.querySelector("#mig-firme");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio firmă în portofoliu. Importă întâi firmele (pasul 1).</div>`;
  }
  firme.forEach((f) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${seStie(f) ? (f.are_solduri ? cate(f.randuri, "cont importat", "conturi importate") : "fără solduri încă") : prosText(f)}</div>
      </div>
      <span class="mig-stare ${seStie(f) ? (f.are_solduri ? "mig-ok" : "mig-gri") : prosClasa(f)}">${seStie(f) ? (f.are_solduri ? "✓ gata" : "de încărcat") : prosScurt(f)}</span>
    `;
    rand.addEventListener("click", () => nav.mergi("Import \u00b7 " + (f.nume || ""), (c) => importSolduriFirma(c, nav, f, _aplicatie)));  // faza_b3_migrare_v1
    lista.appendChild(rand);
  });

  corp.querySelector("#mig-finalizeaza").addEventListener("click", () => {
    const sumar = `<div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">Solduri: ${cuSolduri} din ${cate(firme.length, "firmă", "firme")}</div>
    </div>`;
    randeazaDecizie(corp, nav, "solduri", sumar, "Importul soldurilor e complet?");
  });
  _consumaMigMesaj(corp);   // [423 a] confirmarea salvării făcute dintr-o firmă a acestei liste
}

function descarcaModelSolduri() {
  // [Q10] model descarcabil: contabilul vede exact formatul asteptat, echilibrat (debit=credit=45000).
  _descarcaModelCSV(MODELE.solduri);
}

// C4: modele CSV descarcabile per strat (format citit din parserul de import - core/*_import_api.py).
// [deficiența 350, comanda Costin 8.2] separatorul e `;` și zecimala virgula: în Excel cu setări românești modelul se deschide direct pe
// coloane (cu virgulă, totul cădea în coloana A). Importul citește deja `;` (`import_tabel._delimitator`).
const MODELE = {
  solduri: { fisier: "model_solduri_initiale.csv", coloane: ["cont", "denumire", "sold debitor", "sold creditor"],
    // [388, retestul 19.10.2026] 5121 (activ) are sold DEBITOR — modelul vechi îl punea creditor (20.000), pe partea opusă funcțiunii
    // (OMFP 1802/2014 pct.594: „5121. Conturi la bănci în lei (A)”); balanța rămâne echilibrată: debit = credit = 65.000
    randuri: [["1012", "Capital subscris vărsat", "0", "10000"], ["2131", "Echipamente tehnologice", "25000", "0"],
              ["2813", "Amortizarea instalațiilor și mijloacelor de transport", "0", "5000"], ["371", "Mărfuri", "8000", "0"],
              ["401", "Furnizori", "0", "15000"], ["4111", "Clienți", "12000", "0"], ["5121", "Conturi la bănci în lei", "20000", "0"],
              ["1171", "Rezultatul reportat reprezentând profitul nerepartizat sau pierderea neacoperită", "0", "35000"]] },
  // [388] CUI-uri REALE, cu cifra de control bună și găsite la ANAF (19.10.2026): modelul vechi avea 12345678 / 87654321, pe care propria
  // validare le respingea
  parteneri: { fisier: "model_solduri_parteneri.csv", coloane: ["cont", "cui", "denumire", "sold debitor", "sold creditor"],
    randuri: [["4111", "RO14399840", "DANTE INTERNATIONAL SA", "5000", "0"], ["401", "RO9010105", "ORANGE ROMANIA SA", "0", "3000"]] },
  salariati: { fisier: "model_salariati.csv",
    // [388] coloana „persoane in intretinere” (fără ea fiecare rând intra „cu observație”); CNP-ul scris ca text pentru Excel
    // (`="…"`, `textExcel`), altfel Excel îl face 2,9E+12 la deschiderea CSV-ului
    coloane: ["nume", "prenume", "cnp", "data angajare", "functie", "norma", "ore", "functie de baza", "scutit contributie minima",
              "persoane in intretinere", "brut", "judet", "cor", "iban"],
    randuri: [["Popescu", "Ana", textExcel("2900215410011"), "2020-01-15", "Contabil", "intreaga", "8", "da", "nu", "0", "5000", "B", "251401", "RO49AAAA1B31007593840000"],
              ["Ionescu", "Radu", textExcel("1850715410012"), "2021-03-01", "Ospătar", "partiala", "4", "da", "nu", "1", "6000", "CJ", "522101", ""]] },
  asociati: { fisier: "model_asociati.csv", coloane: ["nume", "cnp/cui", "cota %"],
    randuri: [["Popescu Ana", textExcel("2900215410011"), "60"], ["Ionescu Radu", textExcel("1850715410012"), "40"]] },
  mijloace: { fisier: "model_mijloace_fixe.csv",
    // [lotul 13, 587: „modelul trebuie să spună «valoare reziduală la sfârșitul duratei (de obicei 0)»”] nu „valoarea rămasă”
    coloane: ["cod", "denumire", "valoare intrare", "data PIF", "durata luni", "metoda", "cont imobilizare", "cont amortizare",
              "amortizare cumulata", "valoare reziduala la sfarsitul duratei (de obicei 0)"],
    randuri: [["MF001", "Laptop Dell Latitude", "6000", "2024-03-15", "36", "liniara", "2131", "2813", "3300", "0"],
              ["MF002", "Autoturism serviciu", "80000", "2023-06-01", "60", "liniara", "2133", "2813", "54666,67", "0"]] },
  istoric: { fisier: "model_istoric_declaratii.csv", coloane: ["tip", "an", "luna", "data depunere", "suma de plata"],
    randuri: [["D112", "2026", "1", "2026-02-25", ""], ["D300", "2026", "1", "2026-02-25", ""], ["D100", "2026", "3", "2026-04-24", "1200"]] },
  articole: { fisier: "model_articole.csv", coloane: ["denumire", "um", "cantitate", "pret", "cont stoc", "cont cheltuiala"],
    // [388] făina și uleiul sunt MATERII PRIME (HoReCa, producție): 301 / 601 (OMFP 1802/2014 pct.594: „301. Materii prime (A)”, „601.
    // Cheltuieli cu materiile prime”), nu marfă (371 / 607); al treilea rând e o marfă revândută ca atare
    randuri: [["Făină albă tip 000", "kg", "100", "3,50", "301", "601"], ["Ulei floarea soarelui", "L", "50", "8,20", "301", "601"],
              ["Apă minerală 0,5 L", "buc", "120", "1,90", "371", "607"]] },
  retete: { fisier: "model_retete.csv", coloane: ["reteta", "pret vanzare", "ingredient", "cantitate"],
    // [388, clasa: modelele trec de propria verificare] ingredientele sunt articolele din modelul de articole (rețeta cere ingredientul
    // în stoc: `retete_import_api.verifica_randuri`), în UM-ul lor (kg, L)
    randuri: [["Clătite", "18", "Făină albă tip 000", "0,08"], ["Clătite", "18", "Ulei floarea soarelui", "0,01"],
              ["Gogoși", "6", "Făină albă tip 000", "0,10"], ["Gogoși", "6", "Ulei floarea soarelui", "0,05"]] },
  rip: { fisier: "model_rip.csv", coloane: ["data", "tip", "explicatie", "suma", "categorie", "metoda"],
    randuri: [["2026-01-10", "incasare", "Factura 1001 client", "1500", "venituri", "banca"], ["2026-01-15", "plata", "Chirie spațiu ianuarie", "600", "cheltuieli", "numerar"]] },
};
const SEPARATOR_MODEL = ";";
// [388] o celulă pe care Excel trebuie s-o lase TEXT (CNP-ul de 13 cifre: altfel devine 2,9E+12 și își pierde cifrele) se scrie ca formula
// `="…"`, nescăpată; importul o citește ca textul dinăuntru (`import_tabel.celula`)
function textExcel(v) { return { textExcel: String(v) }; }
function _celulaCSV(v) {
  if (v && typeof v === "object" && "textExcel" in v) return "=" + String.fromCharCode(34) + v.textExcel + String.fromCharCode(34);
  const s = String(v ?? "");
  const GHILIMELE = String.fromCharCode(34);   // fără ghilimele literale într-un regex: cititorul JS al gărzilor le-ar lua drept șir
  return [SEPARATOR_MODEL, GHILIMELE, "\r", "\n"].some((c) => s.includes(c)) ? GHILIMELE + s.split(GHILIMELE).join(GHILIMELE + GHILIMELE) + GHILIMELE : s;
}
function _descarcaModelCSV(spec) {
  const linii = [spec.coloane, ...spec.randuri].map((r) => r.map(_celulaCSV).join(SEPARATOR_MODEL));
  const continut = "\ufeff" + linii.join("\r\n") + "\r\n";  // BOM: Excel citește UTF-8
  const blob = new Blob([continut], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = spec.fisier;
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
}

function importSolduriFirma(corp, nav, firma, app = null) {   // [270] `app` = aplicația aleasă în Migrare cabinet
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>Încarcă balanța de deschidere (cont · denumire · sold debitor · sold creditor) sau balanța de verificare exportată din programul vechi.</p>
    <details class="dec-xml" id="mig-cum-balanta"><summary>Ce se citește din balanță</summary><p class="ecran-nota">Din ea se iau soldurile finale și, dacă le are, soldurile de la 1 ianuarie și rulajele anului (sold inițial și sume precedente, cu toate conturile care au rulaj); fără ele, ecranul spune ce lipsește. Debitul total trebuie să fie egal cu creditul total. Analiticele din balanță (de exemplu 4111.01, 401.00012) se adaugă în planul de conturi, sub sinteticul lor; un cont care nu există în planul de conturi al normei firmei e respins, cu motivul. Un sold pe partea opusă funcțiunii contului (de exemplu 5121 creditor) se semnalează pe rând.</p></details>
    ${_exportHTML(app, "solduri") || `<button type="button" class="buton-secundar mig-model" id="mig-model">Descarcă model (CSV)</button>`}
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" data-actiune="POST /tenants/{tenant_id}/solduri/incarca" accept=".csv,.txt,.tsv,.xlsx,.xls" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#16a34a" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">Încarcă balanța</div>
      <div class="mig-drop-desc">Excel (XLSX, XLS) sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  _existaPas(corp, firma, "solduri");   // [lotul 13, 580 / 584] ce s-a adus deja și ce face importul cu ce există
  const fileInput = corp.querySelector("#mig-file");
  corp.querySelector("#mig-model")?.addEventListener("click", descarcaModelSolduri);
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    eroare.textContent = "Se citește balanța…";
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const r = await fetch(`/tenants/${firma.tenant_id}/solduri/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaSolduri(corp, nav, firma, date);
    } catch (e) {
      arataMesaj(eroare, (e && e.mesaj) || "Eroare la citirea balanței.", "eroare");
    }
  });
}

function previzualizeazaSolduri(corp, nav, firma, date) {
  latime(corp, true);
  const randuri = cuStari(date.randuri || [], date.erori);   // [comanda Costin 8.2 pct.4] starea fiecărui cont citit
  // [DESIGN_SYSTEM cap.6, arataMesaj v2] tipuri canonice: eroare/avert/info/ok; un "ok" (verde)
  // se afiseaza DOAR pe succes real. O balanta goala / cu structura straina (fisier gresit) NU e
  // succes -> badge verde "echilibrat" pe 0=0 ar fi status FALS. valida vine din backend
  // (solduri_api.balanta_valida): pe invalid aratam avert-ul si blocam salvarea.
  const valida = date.valida !== false;
  const echilibrat = valida && Math.abs(date.total_debit - date.total_credit) < 0.01;
  // [lotul 10, deficiența 425] balanța de verificare completă: soldul de la 1 ianuarie și rulajele anului intră și ele (sold inițial și
  // sume precedente), cu toate conturile care au rulaj; fără ele, ecranul spune ce lipsește și ce afectează
  const cuRulaje = !!date.rulaje;
  const soldNet = (d, c) => { const n = (Number(d) || 0) - (Number(c) || 0); return n ? `${bani(Math.abs(n))} ${n > 0 ? "D" : "C"}` : "—"; };
  const coloane = [
    { titlu: "Cont", celula: (r) => esc(r.cont) },
    { titlu: "Denumire", celula: (r) => esc(r.denumire || "") },
    ...(cuRulaje ? [
      { titlu: "Sold la 1 ianuarie", num: true, celula: (r) => soldNet(r.si_debit, r.si_credit) },
      { titlu: "Rulaj debitor an", num: true, celula: (r) => bani(r.rulaj_debit) },
      { titlu: "Rulaj creditor an", num: true, celula: (r) => bani(r.rulaj_credit) },
    ] : []),
    { titlu: cuRulaje ? "Sold final debitor" : "Debit", num: true, celula: (r) => bani(r.debit) },
    { titlu: cuRulaje ? "Sold final creditor" : "Credit", num: true, celula: (r) => bani(r.credit) },
  ];
  // [425] metoda de stoc, cerută când balanța are sold pe 371 și firma n-o are declarată (aceleași două valori ca în Date firmă)
  const metode = date.cere_metoda_stoc ? (date.metode_stoc || []) : [];
  // [lotul 11, 424] câmpurile salvării stau pe un rând, în bara de jos, cu ajutorul scurt: bara rămâne mică și tabelul își păstrează locul
  const campMetoda = metode.length ? `<label class="camp"><span class="camp-eticheta">Metoda de stoc a firmei <span class="oblig">*</span></span>
      <select id="mig-metoda-stoc" class="camp-input">${ALEGE}${metode.map(([v, et]) => `<option value="${esc(v)}">${esc(et)}</option>`).join("")}</select>
      <span class="camp-ajutor">Balanța are sold pe 371; de metodă depinde descărcarea mărfii. Se scrie în Date firmă.</span></label>` : "";
  // [527.1, 14.2] soldul de pe 117 (rezultat reportat) fără analitic: contabilul alege pe ce analitic se preia
  const analitice117 = date.cere_analitic_117 ? (date.analitice_117 || []) : [];
  const campAnalitic117 = analitice117.length ? `<label class="camp"><span class="camp-eticheta">Rezultatul reportat se preia pe <span class="oblig">*</span></span>
      <select id="mig-analitic-117" class="camp-input">${ALEGE}${analitice117.map(([c, et]) => `<option value="${esc(c)}">${esc(c)} — ${esc(et)}</option>`).join("")}</select>
      <span class="camp-ajutor">Balanța are soldul pe contul 117, fără analitic. Profitul nerepartizat sau pierderea neacoperită se preiau pe 1171; din 1171 se repartizează dividendele.</span></label>` : "";
  // [lotul 10, deficiența 426] „Înainte de înlocuire: spune că există deja o balanță, arată totalurile vechi și noi, cere confirmare”
  const existenta = date.existenta;

  corp.innerHTML = _cadruPrev(`
    <div class="mig-intro-rand"><p class="mig-intro"><b>${esc(firma.nume)}</b> · balanță încărcată</p><div class="mig-coer">${bandaStari(randuri)}</div></div>
    <div class="mig-sold-rezumat">
      <b>${randuri.length}</b> ${dupaNumar(randuri.length, "cont", "conturi")} · debit <b>${bani(date.total_debit)}</b> · credit <b>${bani(date.total_credit)}</b>
      ${!valida ? '<span class="mig-eq mig-eq-no">fișier nevalid</span>' : (echilibrat ? '<span class="mig-eq mig-eq-ok">echilibrat</span>' : '<span class="mig-eq mig-eq-no">neechilibrat</span>')}
    </div>`,
    `
    <div class="mig-avertismente">${_casetaFirma(date)}${_casetaInlocuire(date)}${_notaCititeBalanta(date)}</div>
    <div id="mig-rulaje"></div>
    ` + tabelPrevizualizare(coloane, randuri),
    `<div class="grila-doc" style="grid-template-columns:${(metode.length || analitice117.length) ? "repeat(auto-fit, minmax(220px, 1fr))" : "minmax(220px, 640px)"};margin-top:8px">
      <label class="camp camp-pe-rand"><span class="camp-eticheta">Data balanței <span class="oblig">*</span></span>
      <input type="date" id="mig-data-bal" aria-label="Data balanței" class="camp-input" max="${dataIso()}" value="${esc(date.data_propusa || "")}" title="De obicei ultima zi a lunii dinaintea preluării; din ea se propune luna de început." aria-describedby="mig-data-bal-ajutor">
      <span class="camp-ajutor" id="mig-data-bal-ajutor" hidden>De obicei ultima zi a lunii dinaintea preluării; din ea se propune luna de început.</span></label>
    ${campMetoda}${campAnalitic117}</div>
    <div class="mig-eroare" id="mig-eroare"></div>
    <button class="buton-primar mig-buton" id="mig-salveaza-sold" data-actiune="POST /tenants/{tenant_id}/solduri">${existenta ? "Înlocuiește balanța" : "Salvează soldurile"}</button>`);
  nav.setInapoi(() => nav.reiaPasul());   // [C140] „←” = alegerea fișierului, în pasul lui
  _arataFirma(corp, date, nav);   // [599]
  _arataInlocuirea(corp, date, nav);   // [446]
  // [425] fără rulaje: ce lipsește și ce afectează (textul vine de la server: sursa unică, aceeași frază și după salvare)
  if (!cuRulaje && date.avertisment_rulaje) arataMesaj(corp.querySelector("#mig-rulaje"), date.avertisment_rulaje, "avert");

  // Fisier nevalid (gol / structura straina): nu e succes -> avert + salvarea blocata (nu bulina verde).
  if (!valida) {
    arataMesaj(corp.querySelector("#mig-eroare"), date.motiv || "Fișier nerecunoscut ca balanță.", "avert");
    const bs = corp.querySelector("#mig-salveaza-sold");
    if (bs) { bs.disabled = true; bs.title = "Balanță nevalidă — verifică fișierul încărcat"; }
  } else if (!echilibrat) {
    // [Q10] balanta neechilibrata: backendul o refuza oricum (422). O spunem INAINTE de click.
    const dif = bani(Math.abs(date.total_debit - date.total_credit));
    arataMesaj(corp.querySelector("#mig-eroare"),
      "Balanța e neechilibrată: debitul diferă de credit cu " + dif + ". Corectează fișierul (debit = credit) înainte de salvare.", "avert");
    const bs = corp.querySelector("#mig-salveaza-sold");
    if (bs) { bs.disabled = true; bs.title = "Debit diferă de credit — corectează fișierul"; }
  }

  const textButon = existenta ? "Înlocuiește balanța" : "Salvează soldurile";
  corp.querySelector("#mig-salveaza-sold").addEventListener("click", () => {
    async function salveaza(inlocuieste) {
      const eroare = corp.querySelector("#mig-eroare");
      const buton = corp.querySelector("#mig-salveaza-sold");
      const data_referinta = corp.querySelector("#mig-data-bal").value;
      const metoda = corp.querySelector("#mig-metoda-stoc");
      const analitic117 = corp.querySelector("#mig-analitic-117");
      buton.disabled = true; buton.textContent = "Salvez…";
      try {
        const rez = await api.post(`/tenants/${firma.tenant_id}/solduri`, { randuri, data_referinta, inlocuieste,
          metoda_stoc: metoda ? metoda.value : null, analitic_117: analitic117 ? analitic117.value : null });
        // [423 a / 425 / 426, DS cap.27] confirmarea numește ce s-a scris și consecința: rulajele, balanța înlocuită, notele recalculate,
        // metoda de stoc; fără rulaje, lipsa lor se spune și după salvare
        const parti = [`${cate(rez.randuri, "cont salvat", "conturi salvate")}, cu soldurile la ${dataRo(data_referinta)}.`];
        if (rez.rulaje) parti.push("Soldurile de la 1 ianuarie și rulajele anului au intrat ca sold inițial și sume precedente.");
        if (rez.inlocuita) parti.push(`Balanța veche (${cate(rez.inlocuita.randuri, "cont", "conturi")}${rez.inlocuita.data_referinta ? ", la " + dataRo(rez.inlocuita.data_referinta) : ""}) a fost înlocuită.`);
        if (rez.note_dupa && rez.note_dupa.numar) parti.push(`Soldurile ${rez.note_dupa.numar === 1 ? "notei" : "celor " + cate(rez.note_dupa.numar, "notă", "note")} de după ${dataRo(data_referinta)} se recalculează pe balanța nouă.`);
        if (rez.metoda_stoc) parti.push(`Metoda de stoc a firmei: ${(metode.find((m) => m[0] === rez.metoda_stoc) || [null, rez.metoda_stoc])[1]} (în Date firmă).`);
        if (analitic117 && analitic117.value) parti.push(`Rezultatul reportat s-a preluat pe ${analitic117.value}.`);
        _migMesaj = parti.join(" ") + (rez.avertisment_rulaje ? "\n" + rez.avertisment_rulaje : "");
        _migTip = rez.avertisment_rulaje ? "avert" : "ok";
        await _adaugaUrmatorii(firma); nav.inapoiPas();   // [lotul 13, 664] „Salvarea trebuie să ducă la pașii următori necesari.”
      } catch (e) {
        buton.disabled = false; buton.textContent = textButon;
        // [426] balanța a apărut între timp (409): aceeași confirmare, cu totalurile spuse de server
        if (_inlocuire409(e, inlocuieste, eroare, "Înlocuiesc balanța", salveaza)) return;
        if (e && (e.erori_campuri || []).some((x) => x.camp === "metoda_stoc")) eroareCamp(corp, "mig-metoda-stoc", e.mesaj);
        else if (e && (e.erori_campuri || []).some((x) => x.camp === "analitic_117")) eroareCamp(corp, "mig-analitic-117", e.mesaj);
        else arataMesaj(eroare, (e && e.mesaj) || "Eroare la salvare.", "eroare");
      }
    }
    const eroare = corp.querySelector("#mig-eroare");
    eroare.textContent = "";
    curataEroriCamp(corp);
    // [C22, 14.10.2026] data balanței se CERE: din ea se propun data soldurilor și luna preluării (serverul refuză și el lipsa)
    if (!corp.querySelector("#mig-data-bal").value) {
      eroareCamp(corp, "mig-data-bal", "Scrie data la care sunt soldurile din balanță.");
      return;
    }
    if (cereAlegerile(corp, ["#mig-metoda-stoc"])) return;   // [425] metoda de stoc: aplicația nu alege în locul omului
    // [426] înlocuirea unei balanțe existente se confirmă explicit, cu totalurile vechi și noi (și notele care se recalculează)
    _cuFirmaConfirmata(eroare, date, () => _confirmaInlocuirea(eroare, date, "Înlocuiesc balanța", salveaza, "Înlocuiești balanța de deschidere a firmei cu cea din fișier?"));   // [599]
  });
}


// [C21, 14.10.2026] Ce s-a citit din fișier și ce NU a intrat — nimic nu dispare fără să se vadă: coloanele soldului final,
// rândurile care nu sunt conturi (totaluri, titluri de clasă), sinteticele înlocuite de analiticele lor, conturile fără sold.
function _notaCititeBalanta(date) {
  const c = date.coloane || {};
  const linii = [];
  if (c.debit || c.credit) linii.push(`Soldurile ${date.rulaje ? "finale " : ""}s-au citit din coloanele „${esc(c.debit || "—")}” și „${esc(c.credit || "—")}”.`);
  // [lotul 10, 425] perechile balanței de verificare citite: soldul de la 1 ianuarie și rulajele intră ca sold inițial și sume precedente
  const per = date.perechi || {};
  // [lotul 11, 439] și „rulajele precedente” / „totalul rulajelor”; la fiecare pereche cumulată, cum s-a citit (forma stabilită din date)
  const NUME_PER = { si: "soldurile la 1 ianuarie", sp: "sumele precedente", rp: "rulajele precedente", rl: "rulajele perioadei",
    tr: "totalul rulajelor", ts: "totalul sumelor" };
  const forma = date.forma_rulaje || {};
  const cuSi = (g) => (g in forma ? (forma[g] ? " (cu soldul inițial al anului)" : " (fără soldul inițial al anului)") : "");
  const citite = ["si", "sp", "rp", "rl", "tr", "ts"].filter((g) => per[g]).map((g) => `${NUME_PER[g]}${cuSi(g)} din „${esc(per[g][0])}” / „${esc(per[g][1])}”`);
  if (date.rulaje && citite.length) linii.push(`Din aceeași balanță s-au citit ${citite.join(", ")}: intră ca sold inițial și sume precedente (rulajele anului), cu toate conturile care au rulaj — și cele cu sold final 0.`);
  const ign = date.ignorate || [];
  if (ign.length) linii.push(`${ign.length === 1 ? "Un rând nu e cont și nu intră" : cate(ign.length, "rând", "rânduri") + " nu sunt conturi și nu intră"} (totaluri, titluri): ${ign.slice(0, 6).map((x) => "„" + esc(x) + "”").join(", ")}${ign.length > 6 ? " …" : ""}.`);
  const sin = date.sintetice_inlocuite || [];
  if (sin.length) linii.push(`${sin.length === 1 ? "Contul sintetic " + esc(sin[0]) + " e înlocuit" : "Conturile sintetice " + sin.slice(0, 8).map(esc).join(", ") + (sin.length > 8 ? " …" : "") + " sunt înlocuite"} de analiticele din fișier (același sold).`);
  if (date.fara_sold) linii.push(date.rulaje
    ? `${date.fara_sold === 1 ? "Un cont fără sold și fără rulaj nu intră" : cate(date.fara_sold, "cont", "conturi") + " fără sold și fără rulaj nu intră"}.`
    : `${date.fara_sold === 1 ? "Un cont cu sold final 0 nu intră" : cate(date.fara_sold, "cont", "conturi") + " cu sold final 0 nu intră"}.`);
  // [344] informativă (ce s-a citit), nu avertisment: caseta albastră, nu cea galbenă
  // [lotul 11, 424] cu mai multe rânduri, primul (coloanele soldului) e titlul unei note pliate, iar restul (perechile, totalurile,
  // sinteticele) stă în ea: e ce s-a citit, nu ce trebuie văzut cât derulezi tabelul — deschisă, lungea rezumatul lipit sus peste fereastră
  if (!linii.length) return "";
  if (linii.length === 1) return `<div class="caseta-info" role="status"><div class="ca-mesaj">${linii[0]}</div></div>`;
  return `<details class="dec-xml" id="mig-citit"><summary>${linii[0]}</summary><div class="caseta-info" role="status"><div class="ca-mesaj">${linii.slice(1).join("<br>")}</div></div></details>`;
}


// ---------- STRAT 3: SOLDURI PARTENERI (per firma) ----------
async function wizardParteneri(corp, nav) {
  nav.setInapoi(undefined);
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se încarcă firmele…</p>`;
  let firme = [];
  try {
    const r = await api.get("/migrare/parteneri");
    firme = (r && r.firme) || [];
  } catch {}

  // [lotul 13, 665] „gata” numai când partenerii dau soldul fiecărui cont de terți din balanță (`nedefalcate` gol, de la server)
  const cuParteneri = firme.filter((f) => seStie(f) && f.are_parteneri && !(f.nedefalcate || []).length).length;
  corp.innerHTML = `
    <p class="mig-intro">Defalcă soldurile de clienți (4111) și furnizori (401) pe fiecare partener. Suma pe fiecare cont se confruntă cu soldul lui la data preluării (balanța de deschidere, sau contabilitatea firmei dacă balanța lipsește); contul care nu se potrivește nu intră.</p>
    <div class="mig-progres">${sumarStrat(firme, cuParteneri, "au parteneri")}</div>
    <div class="mig-lista" id="mig-firme"></div>
    <button class="buton-primar mig-buton" id="mig-finalizeaza" data-actiune="POST /migrare/status" style="margin-top:16px">Am terminat soldurile pe parteneri</button>
    <p class="ecran-nota" id="mig-fin-motiv"></p>
  `;
  // [345] butonul nu e activ cât o firmă are în balanță solduri pe conturi de terți fără solduri pe parteneri (și spune care)
  // [lotul 13, 665: „Verificarea de la «Am terminat soldurile pe parteneri» numește doar F5 și omite F7.”] și cât partenerii unei firme
  // nu dau soldul unui cont de terți (401 refuzat la import, rămas nedefalcat): fiecare firmă, cu conturile ei
  const asteapta = firme.filter((f) => (f.nedefalcate || []).length || (!f.are_parteneri && (f.terti_in_balanta || []).length));
  if (asteapta.length) {
    corp.querySelector("#mig-finalizeaza").disabled = true;
    corp.querySelector("#mig-fin-motiv").textContent = `Nu se poate marca terminat: ${asteapta.map((f) => `${f.nume} (${(f.nedefalcate || []).length
      ? f.nedefalcate.map((c) => c.text).join("; ") : f.terti_in_balanta.join(", ") + " în balanță"})`).join("; ")} — încarcă soldurile lor pe parteneri.`;
  }

  const lista = corp.querySelector("#mig-firme");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio firmă în portofoliu. Importă întâi firmele (pasul 1).</div>`;
  }
  firme.forEach((f) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    // [lotul 13, 665 / 666] trei stări pe firmă: gata (partenerii dau fiecare cont de terți din balanță), de completat (un cont de terți
    // rămas nedefalcat — numit, cu soldul), nu e cazul (balanța n-are solduri pe conturi de terți; FISCALOS, fără solduri)
    const nedef = f.nedefalcate || [], terti = f.terti_in_balanta || [];
    const fel = nedef.length || (!f.are_parteneri && terti.length) ? "de_completat" : (f.are_parteneri ? "gata" : "nu_e_cazul");
    const sub = fel === "de_completat"
      ? `${f.are_parteneri ? cate(f.randuri, "partener importat", "parteneri importați") + " · " : ""}nedefalcat: ${nedef.length
        ? nedef.map((c) => c.text).join("; ") : terti.join(", ") + " în balanță"}`
      : (fel === "gata" ? cate(f.randuri, "partener importat", "parteneri importați") : "balanța n-are solduri pe conturi de terți");
    const eticheta = { gata: ["mig-ok", "✓ gata"], de_completat: ["mig-nok", "de completat"], nu_e_cazul: ["mig-gri", "nu e cazul"] }[fel];
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${seStie(f) ? esc(sub) : prosText(f)}</div>
      </div>
      <span class="mig-stare ${seStie(f) ? eticheta[0] : prosClasa(f)}">${seStie(f) ? eticheta[1] : prosScurt(f)}</span>
    `;
    rand.addEventListener("click", () => nav.mergi("Import \u00b7 " + (f.nume || ""), (c) => importParteneriFirma(c, nav, f, _aplicatie)));  // faza_b3_migrare_v1
    lista.appendChild(rand);
  });

  corp.querySelector("#mig-finalizeaza").addEventListener("click", () => {
    const sumar = `<div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">Parteneri: ${cuParteneri} din ${cate(firme.length, "firmă", "firme")}</div>
    </div>`;
    randeazaDecizie(corp, nav, "solduri_parteneri", sumar, "Defalcarea partenerilor e completă?");
  });
  _consumaMigMesaj(corp);   // [423 a] confirmarea salvării făcute dintr-o firmă a acestei liste
}

function importParteneriFirma(corp, nav, firma, app = null) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>Încarcă partenerii (cont · CUI · denumire · sold debitor · sold creditor) sau situația clienților / furnizorilor exportată din programul vechi (denumire · cod fiscal · neachitat final), pe parteneri sau pe facturi (nr. factură · data · scadență · sumă neachitată · TVA la încasare, opțional).</p>
    <label class="camp" style="max-width:420px;margin:10px 0"><span class="camp-eticheta">Contul partenerilor din fișier</span>
      <select id="mig-cont-part" class="camp-input" data-butoane="">${ALEGE}<option value="4111">4111 — Clienți</option><option value="401">401 — Furnizori</option></select>
      <span class="camp-ajutor">Numai dacă fișierul n-are coloana „Cont” — situația clienților (4111) sau a furnizorilor (401). Cu coloana „Cont”, contul se ia din fișier.</span></label>
    ${_exportHTML(app, "solduri_parteneri") || `<button type="button" class="buton-secundar mig-model" id="mig-model">Descarcă model (CSV)</button>`}
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" data-actiune="POST /tenants/{tenant_id}/parteneri/incarca" accept=".csv,.txt,.tsv,.xlsx,.xls" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#0a807b" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">Încarcă partenerii</div>
      <div class="mig-drop-desc">Excel (XLSX, XLS) sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  _existaPas(corp, firma, "solduri_parteneri");   // [lotul 13, 580 / 584] ce s-a adus deja și ce face importul cu ce există
  const fileInput = corp.querySelector("#mig-file");
  corp.querySelector("#mig-model")?.addEventListener("click", () => _descarcaModelCSV(MODELE.parteneri));
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    eroare.textContent = "Se citesc partenerii…";
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const contAles = corp.querySelector("#mig-cont-part").value;
      if (contAles) fd.append("cont", contAles);
      const r = await fetch(`/tenants/${firma.tenant_id}/parteneri/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaParteneri(corp, nav, firma, date);
    } catch (e) {
      arataMesaj(eroare, (e && e.mesaj) || "Eroare la citirea fișierului.", "eroare");
    }
  });
}

// [Q5 preview=salvare, 16.08.2026] Poarta UNICA: previzualizarea arata EXACT ce respinge salvarea
// (erori din verifica_randuri, backend - aceeasi poarta pe care importa o aplica), nu o a doua
// validare din extrage (cnp_valid/ok) care drifteaza. Randuri respinse -> lista vizibila + Salvare
// blocata (DS cap.5 caseta-atentie / cap.6 / cap.24). erori: [{rand, motiv, mesaj}].
// [comanda Costin 8.2 pct.4; deficiențele 349, 352, 357, 358, 360] PREVIZUALIZAREA COMUNĂ a importurilor de migrare: un TABEL (antetul stă
// deasupra valorilor prin construcție — grila cu antetul în afara zonei derulate le despărțea), starea fiecărui rând într-o coloană a ei,
// cu motivul pe rândul lui (nu înghesuit în celula „Tip” sau „Normă”), și o bandă care spune ce se întâmplă cu fiecare grup.
const STARI_RAND = { ok: "intră", semnalat: "intră, cu observație", respins: "respins — nu intră" };
// [lotul 13, deficiențele 581 + 624, comanda Costin 13.1: „Etichetele «1 rând cu observație» nu se pot apăsa.” / „observații la clic”]
// fiecare grup e un BUTON: apăsat, tabelul arată numai rândurile grupului (cu motivele lor); apăsat din nou, pe toate (DS cap.1: orice
// acțiune e buton — 674)
function bandaStari(randuri) {
  const n = (s) => randuri.filter((r) => (r.stare || "ok") === s).length;
  const ok = n("ok"), sem = n("semnalat"), resp = n("respins");
  const b = (stare, cls, text) => `<button type="button" class="mig-eq ${cls}" data-filtru-stare="${stare}" aria-pressed="false" title="Arată numai aceste rânduri în tabel; încă o apăsare le arată pe toate" style="border:0;cursor:pointer;font:inherit">${text}</button>`;
  return [ok ? b("ok", "mig-eq-ok", cate(ok, "rând intră", "rânduri intră")) : "",
          sem ? b("semnalat", "mig-eq-sem", cate(sem, "rând intră cu observație", "rânduri intră cu observație")) : "",
          resp ? b("respins", "mig-eq-no", cate(resp, "rând respins — nu intră", "rânduri respinse — nu intră")) : ""]
    .filter(Boolean).join(" ");
}
// [581 / 624] filtrul de stare al tabelului previzualizării (delegat: banda se redesenează la fiecare fișier încărcat)
function _filtreazaStare(buton) {
  const zona = buton.closest(".fereastra-corp") || buton.closest(".fereastra") || document;
  const activ = buton.getAttribute("aria-pressed") !== "true";
  zona.querySelectorAll("[data-filtru-stare]").forEach((x) => x.setAttribute("aria-pressed", String(activ && x === buton)));
  const stare = buton.dataset.filtruStare;
  zona.querySelectorAll(".mig-prev tbody tr").forEach((tr) => { tr.hidden = activ && !tr.classList.contains("mig-prev-" + stare); });
}
if (typeof document !== "undefined") {
  document.addEventListener("click", (ev) => {
    const b = ev.target && ev.target.closest ? ev.target.closest("[data-filtru-stare]") : null;
    if (b) _filtreazaStare(b);
  });
}
// starea rândurilor din respingerile serverului (`erori`, poarta unică previzualizare <-> salvare), unde serverul nu o pune pe rând
function cuStari(randuri, erori) {
  const pe = {};
  (erori || []).forEach((e) => { if (e.rand != null) (pe[e.rand] = pe[e.rand] || []).push(e.mesaj || e.motiv || ""); });
  randuri.forEach((r) => {
    if (r.stare) return;
    const m = pe[r.rand_fisier];
    r.stare = m ? "respins" : (r.semnale && r.semnale.length ? "semnalat" : "ok");
    r.motive = m || r.semnale || [];
  });
  return randuri;
}
// [349, comanda Costin 8.2 — clasa 285/331] motivele stau pe un sub-rând pe toată lățimea, sub rândul lor: într-o coloană îngustă
// înălțau rândul la sute de pixeli; „Starea” stă lângă numărul rândului, ca să se vadă și când tabelul are multe coloane
function tabelPrevizualizare(coloane, randuri) {
  const motive = (r) => (r.motive || []).map((m) => esc(typeof m === "string" ? m : (m.mesaj || m.motiv || "")));
  const nr = (r) => esc(String(r.rand_fisier || ""));
  return `<div class="mig-prev-cutie" tabindex="0" aria-label="Rândurile citite din fișier"><table class="fd-tabel mig-prev">
    <thead><tr><th>Rândul</th><th>Starea</th>${coloane.map((c) => `<th${c.num ? ' class="fd-td-num"' : ""}>${esc(c.titlu)}</th>`).join("")}</tr></thead>
    <tbody>${randuri.map((r) => `<tr class="mig-prev-${r.stare || "ok"}" data-rand="${nr(r)}"><td>${nr(r)}</td><td class="mig-prev-stare"><span class="mig-stare-${r.stare || "ok"}">${STARI_RAND[r.stare || "ok"]}</span></td>${coloane
      .map((c) => `<td${c.num ? ' class="fd-td-num"' : ""}>${c.celula(r)}</td>`).join("")}</tr>${motive(r).length
      ? `<tr class="mig-prev-${r.stare || "ok"} mig-prev-motive" data-rand="${nr(r)}"><td></td><td colspan="${coloane.length + 1}"><div class="mig-prev-motiv">${motive(r).join("<br>")}</div></td></tr>` : ""}`).join("")}
    </tbody></table></div>`;
}

// [366, comanda Costin 8.2] unde e respingerea: „rândul N”, sau domeniul ei când e despre tot setul (totalul cotelor) — nu „rând undefined”
const undeE = (e) => (e.rand != null ? `rândul ${e.rand}` : (e.unde || "fișierul"));
// [lotul 13, deficiențele 624 + 666: „respinsele grupate” / „mesajul pentru 401 se repetă identic pe fiecare rând”] același motiv o singură
// dată, cu toate rândurile lui („rândurile 3, 4: …”)
function listaRefuzuri(erori) {
  const grup = new Map();
  (erori || []).forEach((e) => {
    const m = e.mesaj || e.motiv || "";
    if (!grup.has(m)) grup.set(m, []);
    grup.get(m).push(e);
  });
  return `<ul style="margin:6px 0 0;padding-left:20px">${[...grup.entries()].map(([m, es]) => {
    const randuri = es.filter((e) => e.rand != null).map((e) => e.rand);
    const unde = es.length === 1 || randuri.length !== es.length ? es.map(undeE).join(", ") : `rândurile ${randuri.join(", ")}`;
    return `<li>${esc(unde)}: ${esc(m)}</li>`;
  }).join("")}</ul>`;
}
// [lotul 13, deficiența 581, comanda Costin 13.1: „La mărimea normală a ecranului, casetele roșii fixe strâng tabelul rândurilor într-o
// bară albă și acoperă câmpul de dată la derulare”] caseta refuzurilor stă în pagină, deasupra tabelului — nu în bara lipită jos, unde
// creștea cu fiecare rând refuzat până strângea tabelul și acoperea câmpurile barei
function _puneRefuzul(corp, buton, bloc) {
  const tabel = corp.querySelector(".mig-prev-cutie");
  const av = corp.querySelector(".mig-avertismente");   // [687] refuzul stă lângă celelalte avertismente, nu împinge tabelul în jos
  if (av) av.appendChild(bloc);
  else if (tabel && tabel.parentNode) tabel.parentNode.insertBefore(bloc, tabel);
  else buton.parentNode.insertBefore(bloc, buton);
}
function gateazaPreview(corp, butonId, erori) {
  erori = erori || [];
  if (!erori.length) return;
  const buton = corp.querySelector("#" + butonId);
  if (!buton) return;
  buton.disabled = true;
  const titlu = erori.length === 1 ? "un rând nu poate fi salvat" : (cate(erori.length, "rând", "rânduri") + " nu pot fi salvate");
  const bloc = document.createElement("div");
  bloc.className = "caseta-atentie"; bloc.id = "mig-refuzuri";
  bloc.innerHTML = `<div class="ca-mesaj"><b>${esc(titlu)}</b> — corectează fișierul și reîncarcă:` + listaRefuzuri(erori) + `</div>`;
  _puneRefuzul(corp, buton, bloc);
}

// [C24 / C25, decizia Costin 14.10.2026, verbatim în DECIZII: „fără blocare la salvare; rândul problemă se arată, restul se
// salvează”] Mijloacele fixe și istoricul declarațiilor: rândurile pe care salvarea le refuză se arată ÎNAINTE (aceeași poartă,
// `verifica_randuri`), iar butonul salvează rândurile bune și spune câte. Numai când niciun rând nu poate intra salvarea e blocată.
function gateazaPartial(corp, butonId, erori, total, eticheta) {
  erori = erori || [];
  const buton = corp.querySelector("#" + butonId);
  if (!buton || !erori.length) return;
  const nrRespinse = new Set(erori.map((e) => String(e.rand))).size;
  const bune = Math.max(0, total - nrRespinse);
  const titlu = nrRespinse === 1 ? "Un rând nu intră" : `${cate(nrRespinse, "rând", "rânduri")} nu intră`;
  const bloc = document.createElement("div");
  bloc.className = "caseta-atentie"; bloc.id = "mig-refuzuri";
  bloc.innerHTML = `<div class="ca-mesaj"><b>${esc(titlu)}</b> — ${bune ? "celelalte se salvează; corectează-le în fișier și reîncarcă-l pentru ele:" : "niciun rând nu poate fi salvat; corectează fișierul și reîncarcă-l:"}` +
    listaRefuzuri(erori) + `</div>`;
  _puneRefuzul(corp, buton, bloc);   // [581] în pagină, deasupra tabelului
  if (!bune) { buton.disabled = true; return; }
  buton.textContent = `Salvează ${bune === 1 ? "rândul bun" : "cele " + cate(bune, "rând bun", "rânduri bune")} (${eticheta})`;
}

// [lotul 11, deficiența 447, comanda Costin 11.1 pct.15: „mesajul după import: «0 noi, 3 fișe actualizate», nu «3 importați» plus «3
// actualizate»”] o singură numărătoare: câte au intrat NOI și câte au ACTUALIZAT ce exista (cum le-a numărat serverul la scriere);
// rândurile respinse le adaugă `_mesajSalvarePartiala`, numite, o singură dată.
function _noiActualizate(rez, actSg, actPl) {
  const noi = (rez && rez.noi) || 0, act = (rez && rez.actualizate) || 0;
  return `${cate(noi, "nou", "noi")}, ${cate(act, actSg, actPl)}`;
}
function _mesajSalvarePartiala(rez, ceSalvat) {
  const resp = (rez && rez.respinse) || [];
  if (!resp.length) return ceSalvat;
  _migTip = "avert";
  const n = new Set(resp.map((e) => String(e.rand))).size;
  return ceSalvat + `\n${n === 1 ? "Un rând nu a intrat" : cate(n, "rând", "rânduri") + " nu au intrat"}:\n` +
    resp.map((e) => `${undeE(e)}: ${e.mesaj || e.motiv || ""}`).join("\n");
}

// [lotul 12, deficiența 252] facturile deschise preluate: din forma pe facturi, câte una pe rând (`r.documente`, de la server); din forma pe
// solduri, soldul partenerului întreg de pe 4111 / 401 (un document „Sold la <data preluării>”, `solduri_parteneri_api.documente_din_randuri`)
const NOTA_FACTURI_PRELUATE = "Facturile deschise ale clienților (4111) și furnizorilor (401) intră în scadențar și se sting din Bancă, Casă sau Compensări. Nu se contează: soldul lor e deja în balanța de deschidere.";
// [lotul 12, 252, decizia Costin 12.3 pct.5: „coloana TVA la încasare e opțională în fișierul de preluare; dacă lipsește, se ia regimul
// firmei la data facturii”] ce se întâmplă cu TVA-ul facturilor deschise (`solduri_parteneri_api.cu_regimul_tva`)
const NOTA_TVA_INCASARE = "Coloana opțională „TVA la încasare” (da / nu) spune, pe fiecare factură, dacă TVA-ul din restul ei e încă neexigibil (4428). Unde lipsește, se ia regimul firmei la data facturii, din Date firmă. Cu TVA la încasare, încasarea sau plata mută TVA-ul pe 4427 / 4426 și îl duce în D300 și D394. Suma lui se ia din coloana opțională „TVA”; unde lipsește, se calculează la cota standard și factura e marcată „de verificat”.";
const TEXT_TVAI = (v) => (v === true ? "da" : v === false ? "nu" : "după Date firmă");
// [252, 12.3 pct.5] coloana „TVA la încasare” a fișierului, pe rândul partenerului: valoarea fiecărei facturi (sau a soldului întreg)
function tvaIncasare(r) {
  if (Array.isArray(r.documente)) {
    const de = r.documente.filter((d) => Number(d.suma) > 0);
    if (!de.length) return "—";
    const pe = {};
    de.forEach((d) => { const t = TEXT_TVAI(d.tva_la_incasare); (pe[t] = pe[t] || []).push(d.numar); });
    const chei = Object.keys(pe);
    return chei.length === 1 ? esc(chei[0]) : esc(chei.map((t) => `${t}: ${pe[t].join(", ")}`).join("; "));
  }
  return facturiDeschise(r) === "—" ? "—" : esc(TEXT_TVAI(r.tva_la_incasare));
}
const areColoanaTvai = (randuri) => randuri.some((r) => "tva_la_incasare" in r || (r.documente || []).some((d) => "tva_la_incasare" in d));
// [lotul 13, 252, decizia Costin 13.1: „dacă fișierul are suma TVA, se ia suma din fișier; doar unde lipsește se calculează la cota standard,
// iar factura e marcată «de verificat»”] coloana „TVA” a fișierului, pe rândul partenerului (fiecare factură, sau soldul întreg)
const areColoanaTva = (randuri) => randuri.some((r) => "tva_fisier" in r || (r.documente || []).some((d) => "tva_fisier" in d));
function tvaFisier(r) {
  const v = (x) => (x == null ? "calculat, de verificat" : bani(x));
  if (Array.isArray(r.documente)) return esc(r.documente.map((d) => `${d.numar}: ${v(d.tva_fisier)}`).join("; ") || "—");
  return facturiDeschise(r) === "—" ? "—" : esc(v(r.tva_fisier));
}
function facturiDeschise(r) {
  if (Array.isArray(r.documente)) {
    const de = r.documente.filter((d) => Number(d.suma) > 0);
    return de.length ? esc(de.map((d) => d.numar).join(", ")) : "—";
  }
  const cont = String(r.cont || "").split(".")[0];
  const deIncasat = cont === "4111" ? Number(r.debit) - Number(r.credit) : (cont === "401" ? Number(r.credit) - Number(r.debit) : 0);
  return deIncasat > 0.005 ? "soldul întreg" : "—";
}
function mesajFacturiPreluate(doc) {
  if (!doc || !doc.n) return "";
  const parti = [doc.emise ? `de încasat ${bani(doc.total_emise)} lei` : "", doc.primite ? `de plătit ${bani(doc.total_primite)} lei` : ""].filter(Boolean);
  // [252, 12.3 pct.5] TVA-ul încă neexigibil / nededus al facturilor preluate cu TVA la încasare, și confruntarea lui cu 4428
  const tvai = doc.la_incasare ? `\nCu TVA la încasare: ${cate(doc.la_incasare, "factură", "facturi")} — TVA neexigibil ${bani(doc.tva_emise || 0)} lei pe cele emise, nededus ${bani(doc.tva_primite || 0)} lei pe cele primite; încasarea sau plata îl mută pe 4427 / 4426 și îl duce în D300 și D394.` : "";
  if (doc.atentie_tva) _migTip = "avert";
  // [lotul 13, 252] facturile cu TVA-ul calculat la cota standard (lipsea suma din fișier), marcate „de verificat”
  const dv = (doc.tva_de_verificat || []);
  if (dv.length) _migTip = "avert";
  return ` ${cate(doc.n, "factură deschisă preluată", "facturi deschise preluate")} (${parti.join(", ")}): le sting încasările și plățile din Bancă, Casă sau Compensări.` +
    tvai + (dv.length ? `\nTVA calculat la cota standard (fișierul n-avea suma TVA), de verificat: ${dv.join("; ")}. Auditul de preluare le arată până le încarci cu coloana „TVA”.` : "") +
    (doc.atentie_tva ? `\n${doc.atentie_tva}` : "") +
    ((doc.neconvertite || []).length ? `\nFără factură deschisă: ${doc.neconvertite.join("; ")}.` : "");
}

function previzualizeazaParteneri(corp, nav, firma, date) {
  latime(corp, true);
  // [lotul 13, deficiența 666: „mesajul pentru 401 se repetă identic pe fiecare rând”] pe rândul tabelului, motivul scurt al contului
  // nepotrivit; mesajul întreg, cu cifrele, îl spun o dată confruntarea pe conturi și lista refuzurilor (grupată)
  const scurt = (e) => (e.regula === "parteneri_nu_dau_soldul"
    ? Object.assign({}, e, { mesaj: `nu intră: contul ${e.cont || ""} nu se potrivește cu soldul lui (cifrele, deasupra tabelului)` }) : e);
  const randuri = cuStari(date.randuri || [], (date.erori || []).map(scurt));
  const coer = date.coerenta || [];
  // [deficiențele 345 + 346, comanda Costin 8.2] pe fiecare cont, soldul cu care se compară (balanța de deschidere sau contabilitatea, la
  // data preluării) și ce se întâmplă: contul ale cărui parteneri nu-l dau nu intră
  const sold = (v) => `${v >= 0 ? "debitor" : "creditor"} ${bani(Math.abs(v))} lei`;
  const coerHTML = coer.map((c) => `<li><b>${esc(c.cont)}</b>: partenerii dau ${sold(c.suma_parteneri)}; ${esc(c.sursa)} la ${esc(dataRo(c.data))}: ${sold(c.sold_balanta)} · ${c.coincide
    ? '<span class="mig-stare-ok">se potrivesc</span>' : `<span class="mig-stare-respins">diferență ${bani(Math.abs(c.diferenta))} lei — rândurile contului nu intră</span>`}</li>`);   // [lotul 13] câte un <li> pe cont: notele de mai jos aleg conturile
  // [lotul 13, 666: „contul care se potrivește (4111) stă în caseta roșie cu eroarea”] conturile care se potrivesc stau în nota lor (pliată,
  // cu concluzia la vedere), cele care nu se potrivesc în caseta de atenție, numai ele; [581] amândouă în pagină, nu lipite sus (rezumatul
  // lipit creștea până strângea tabelul)
  const coerOk = coer.filter((c) => c.coincide), coerNu = coer.filter((c) => !c.coincide);
  const liCoer = (arr) => arr.map((c) => coerHTML[coer.indexOf(c)]).join("");
  // [lotul 13, 583: „Sus «4 parteneri · debit 1.700», în casetă «Fișierul nou: 0 parteneri, debit 0,00»”] rândurile citite și câte intră
  const intra = randuri.filter((r) => r.stare !== "respins").length;
  corp.innerHTML = _cadruPrev(`
    <div class="mig-intro-rand"><p class="mig-intro"><b>${esc(firma.nume)}</b> · parteneri încărcați</p><div class="mig-coer">${bandaStari(randuri)}</div></div>
    <div class="mig-sold-rezumat">
      <b>${randuri.length}</b> ${dupaNumar(randuri.length, "rând citit", "rânduri citite")} (${intra === randuri.length ? "toate intră" : `${intra} intră`}) · debit <b>${bani(date.total_debit)}</b> · credit <b>${bani(date.total_credit)}</b>
    </div>`,
    `
    <p class="ecran-nota" id="mig-nota-preluate">${NOTA_FACTURI_PRELUATE} ${NOTA_TVA_INCASARE}</p>
    <div class="mig-avertismente">${_casetaFirma(date)}${_casetaInlocuire(date)}</div>
    ${casetaIgnorate(date.ignorate)}
    ` + `${coerOk.length ? `<details class="dec-xml" id="mig-coer-cont"><summary>Soldurile pe parteneri, față de soldul fiecărui cont: se potrivesc (${coerOk.map((c) => esc(c.cont)).join(", ")})</summary><ul>${liCoer(coerOk)}</ul></details>` : ""}
    ${coerNu.length ? `<div class="caseta-atentie" id="mig-coer-nepotrivit" style="margin:8px 0"><div class="ca-mesaj">Nu se potrivesc cu soldul contului — rândurile acestor conturi nu intră:<ul>${liCoer(coerNu)}</ul></div></div>` : ""}` +
    tabelPrevizualizare([
      { titlu: "Cont", celula: (r) => esc(r.cont) },
      { titlu: "CUI", celula: (r) => esc(r.cui || "") },
      { titlu: "Denumire", celula: (r) => esc(r.denumire || "") },
      { titlu: "Debit", num: true, celula: (r) => bani(r.debit) },
      { titlu: "Credit", num: true, celula: (r) => bani(r.credit) },
      { titlu: "Facturi deschise", celula: facturiDeschise },
      ...(areColoanaTvai(randuri) ? [{ titlu: "TVA la încasare", celula: tvaIncasare }] : []),   // [252, 12.3 pct.5] numai cu coloana în fișier
      ...(areColoanaTva(randuri) ? [{ titlu: "TVA din rest", celula: tvaFisier }] : []),   // [lotul 13, 252] numai cu coloana „TVA” în fișier
    ], randuri),
    `<div class="mig-eroare" id="mig-eroare"></div>
    <button class="buton-primar mig-buton" id="mig-salveaza-part" data-actiune="POST /tenants/{tenant_id}/parteneri">${date.existenta ? "Înlocuiește partenerii" : "Salvează partenerii"}</button>`);
  nav.setInapoi(() => nav.reiaPasul());   // [C140] „←” = alegerea fișierului, în pasul lui
  _arataFirma(corp, date, nav);   // [599]
  _arataInlocuirea(corp, date, nav);   // [446]
  gateazaPartial(corp, "mig-salveaza-part", date.erori, randuri.length, "parteneri");   // [decizia Costin 14.10.2026 pct.2]
  const buton = corp.querySelector("#mig-salveaza-part");
  // [252, 12.3 pct.5] coloana „TVA la încasare” contrazice Date firmă: salvarea ar refuza tot (`solduri_parteneri_api.refuz_tva_incasare`)
  if (date.refuz_tva_incasare) {
    const bloc = document.createElement("div");
    bloc.className = "caseta-atentie"; bloc.id = "mig-refuz-tvai";
    bloc.innerHTML = `<div class="ca-mesaj">${esc(date.refuz_tva_incasare)}</div>`;
    buton.parentNode.insertBefore(bloc, buton);
    buton.disabled = true;
  }
  const textButon = buton.textContent;
  const eroare = corp.querySelector("#mig-eroare");

  buton.addEventListener("click", () => {
    async function salveaza(inlocuieste) {
      buton.disabled = true; buton.textContent = "Salvez…";
      try {
        const rez = await api.post(`/tenants/${firma.tenant_id}/parteneri`, { randuri, inlocuieste });
        const n = (rez && rez.randuri) || 0;
        // [426] confirmarea spune și ce s-a înlocuit
        const vechi = rez && rez.inlocuita ? ` Soldurile vechi (${cate(rez.inlocuita.randuri, "partener", "parteneri")}) au fost înlocuite.` : "";
        _migMesaj = _mesajSalvarePartiala(rez, `${n === 1 ? "Un partener salvat" : cate(n, "partener salvat", "parteneri salvați")}.${vechi}${mesajFacturiPreluate(rez && rez.documente)}`); await _adaugaUrmatorii(firma); nav.inapoiPas();   // [664]
      } catch (e) {
        buton.disabled = false; buton.textContent = textButon;
        if (_inlocuire409(e, inlocuieste, eroare, "Înlocuiesc soldurile pe parteneri", salveaza)) return;   // [426]
        arataMesaj(eroare, (e && e.mesaj) || "Eroare la salvare.", "eroare");
      }
    }
    eroare.textContent = "";
    _cuFirmaConfirmata(eroare, date, () => _confirmaInlocuirea(eroare, date, "Înlocuiesc soldurile pe parteneri", salveaza, "Înlocuiești soldurile pe parteneri cu cele din fișier?"));   // [599]; [426] cu totalurile vechi și noi
  });
}


// ---------- STRAT 4: SALARIATI (per firma) ----------
async function wizardSalariati(corp, nav) {
  nav.setInapoi(undefined);
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se încarcă firmele…</p>`;
  let firme = [];
  try {
    const r = await api.get("/migrare/salariati");
    firme = (r && r.firme) || [];
  } catch {}

  const cuSal = firme.filter((f) => seStie(f) && f.are_salariati).length;
  // [lotul 10, deficiența 423 b] „starea «gata» nu spune câți salariați rămân «de verificat»” — numărul lor, și unde se confirmă
  const deVerif = (f) => (f.de_verificat ? ` · ${f.de_verificat === 1 ? "unul are" : f.de_verificat + " au"} date de verificat în Stat de plată (butonul „De verificat”)` : "");
  corp.innerHTML = `
    <p class="mig-intro">Importă salariații din vechea aplicație (nume, CNP, salariu, contract). Fiecare rând se verifică înainte de salvare: rândurile bune intră, cele respinse (de exemplu CNP greșit) se arată cu motivul și le corectezi în fișier. Ce lipsește din fișier (norma, funcția de bază, persoanele în întreținere, scutirea) intră cu o propunere marcată „de verificat”, pe care o confirmi în Stat de plată.</p>
    <div class="mig-progres">${sumarStrat(firme, cuSal, "au salariați")}</div>
    <div class="mig-lista" id="mig-firme"></div>
    <button class="buton-primar mig-buton" id="mig-finalizeaza" data-actiune="POST /migrare/status" style="margin-top:16px">Am terminat salariații</button>
  `;

  const lista = corp.querySelector("#mig-firme");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio firmă în portofoliu. Importă întâi firmele (pasul 1).</div>`;
  }
  firme.forEach((f) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${seStie(f) ? (f.are_salariati ? cate(f.randuri, "salariat importat", "salariați importați") + deVerif(f) : "fără salariați încă") : prosText(f)}</div>
      </div>
      <span class="mig-stare ${seStie(f) ? (f.are_salariati ? "mig-ok" : "mig-gri") : prosClasa(f)}">${seStie(f) ? (f.are_salariati ? "✓ gata" + (f.de_verificat ? ` · ${f.de_verificat} de verificat` : "") : "de încărcat") : prosScurt(f)}</span>
    `;
    rand.addEventListener("click", () => nav.mergi("Import \u00b7 " + (f.nume || ""), (c) => importSalariatiFirma(c, nav, f, _aplicatie)));  // faza_b3_migrare_v1
    lista.appendChild(rand);
  });

  corp.querySelector("#mig-finalizeaza").addEventListener("click", () => {
    const sumar = `<div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">Salariați: ${cuSal} din ${cate(firme.length, "firmă", "firme")}</div>
    </div>`;
    randeazaDecizie(corp, nav, "salariati", sumar, "Importul salariaților e complet?");
  });
  _consumaMigMesaj(corp);   // [423 a] confirmarea salvării făcute dintr-o firmă a acestei liste
}

function importSalariatiFirma(corp, nav, firma, app = null) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>Încarcă exportul de salariați (nume · CNP · salariu · date contract).</p>
    ${_exportHTML(app, "salariati") || `<button type="button" class="buton-secundar mig-model" id="mig-model">Descarcă model (CSV)</button>`}
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" data-actiune="POST /tenants/{tenant_id}/salariati-import/incarca" accept=".csv,.txt,.tsv,.xlsx,.xls" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#c2415f" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">Încarcă salariații</div>
      <div class="mig-drop-desc">Excel (XLSX, XLS) sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  _existaPas(corp, firma, "salariati");   // [lotul 13, 580 / 584] ce s-a adus deja și ce face importul cu ce există
  const fileInput = corp.querySelector("#mig-file");
  corp.querySelector("#mig-model")?.addEventListener("click", () => _descarcaModelCSV(MODELE.salariati));
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    eroare.textContent = "Se citesc salariații…";
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const r = await fetch(`/tenants/${firma.tenant_id}/salariati-import/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaSalariati(corp, nav, firma, date);
    } catch (e) {
      arataMesaj(eroare, (e && e.mesaj) || "Eroare la citirea fișierului.", "eroare");
    }
  });
}

function previzualizeazaSalariati(corp, nav, firma, date) {
  latime(corp, true);
  const randuri = cuStari(date.randuri || [], date.erori);

  // [comanda Costin 8.2 pct.4; 348/349] tabelul comun al previzualizării: fiecare rând citit, cu starea și motivul lui. Funcția vine
  // din fișier (codul COR dedesubt), data angajării are coloana ei, iar Norma e scurtă — detaliile (funcție de bază, scutire,
  // persoane în întreținere) au coloanele lor; ce s-a completat din oficiu e spus pe rând, ca semnal.
  // [decizii 07.10 pct.4] valorile se arată cum au venit din fișier; lipsa e „—”. [PIVOT 14.10 pct.3–4] persoanele și scutirea lipsă
  // intră 0 / „nescutit”, marcate de verificat.
  const dn = (x) => (x === true ? "Da" : x === false ? "Nu" : "—");
  // [349, retestul 19.10.2026: „rândul cu descriere COR lungă are ~230 px, iar tabelul are derulare orizontală”] denumirea COR lungă
  // (până la 126 de caractere în nomenclator) stă pe cel mult două rânduri, întreagă în `title`; „(de verificat)” coboară sub valoare
  const functie = (r) => {
    const den = r.functie || r.cor_denumire || "";
    const cod = r.cor ? `COR ${esc(r.cor)}${r.functie && r.cor_denumire ? " · " + esc(r.cor_denumire) : ""}` : "fără cod COR";
    const titlu = r.cor && r.cor_denumire ? ` title="${esc(`COR ${r.cor} · ${r.cor_denumire}`)}"` : "";
    return `<div class="mig-prev-scurt"${r.cor_denumire && !r.functie ? titlu : ""}>${esc(den || "—")}</div><div class="mig-prev-motiv mig-prev-scurt"${titlu}>${cod}</div>`;
  };
  const deVerificat = (v) => `${v}<div class="tip-desc">de verificat</div>`;
  const dv = (r) => r.de_verificat || [];
  // [lotul 11, 420] pe un salariat existent, câmpul lipsă din fișier arată valoarea din fișa lui (`salariati_import_api.din_fise`), pe care
  // o păstrează salvarea — spusă ca atare; pe un salariat nou, propunerea
  const dinFisa = (r, camp) => ((r.din_fisa || []).includes(camp) ? "din fișa existentă" : "propusă");
  const nr = (r) => esc(String(r.rand_fisier || ""));
  // [lotul 10, deficiența 420, comanda Costin 10.1] „Câmpurile lipsă se completează pe ecran, înainte de import, cu propunere editabilă
  // (normă întreagă, funcție de bază Da) […] (intră marcate «de verificat»)”: pe rândul unde fișierul n-are norma / funcția de bază,
  // propunerea serverului e un câmp de ales, nu text. Ce schimbă contabilul aici e ales de el (iese din marcaj); propunerea neatinsă
  // intră „de verificat” și se confirmă în Stat de plată.
  // rândurile cu propunere (fixate la desenare: rămân câmpuri și după ce contabilul alege)
  const normaEd = new Set(randuri.filter((r) => dv(r).includes("tip_norma")).map((r) => String(r.rand_fisier)));
  const fbazaEd = new Set(randuri.filter((r) => dv(r).includes("functie_baza")).map((r) => String(r.rand_fisier)));
  const normaText = (r) => (r.tip_norma === "partiala" ? `parțială, ${esc(String(r.ore_zi || "—"))} h` : r.tip_norma === "intreaga" ? "întreagă" : "—");
  const norma = (r) => {
    if (!normaEd.has(String(r.rand_fisier))) return normaText(r);
    const n = nr(r);
    return `<select id="mig-norma-${n}" class="camp-input" data-rand="${n}" data-propus="tip_norma" data-butoane="" aria-label="Norma de lucru — rândul ${n}">${alegeDacaLipseste(r.tip_norma)}<option value="intreaga"${r.tip_norma === "intreaga" ? " selected" : ""}>întreagă (8 h)</option><option value="partiala"${r.tip_norma === "partiala" ? " selected" : ""}>parțială</option></select>`
      + `<input type="number" id="mig-ore-${n}" class="camp-input" data-rand="${n}" data-propus="ore_zi" min="1" max="7.5" step="0.5" aria-label="Ore pe zi — rândul ${n}" value="${r.tip_norma === "partiala" ? esc(String(r.ore_zi || "")) : ""}"${r.tip_norma === "partiala" ? "" : " hidden"}>`
      + (dv(r).includes("tip_norma") ? `<div class="tip-desc">${dinFisa(r, "tip_norma")} — de verificat</div>` : "");
  };
  const functieBaza = (r) => {
    if (!fbazaEd.has(String(r.rand_fisier))) return dn(r.functie_baza);
    const n = nr(r);
    return selectDaNu(`id="mig-fbaza-${n}" data-rand="${n}" data-propus="functie_baza"`, r.functie_baza, `Funcția de bază — rândul ${n}`)
      + (dv(r).includes("functie_baza") ? `<div class="tip-desc">${dinFisa(r, "functie_baza")} — de verificat</div>` : "");
  };
  const coloane = [
    { titlu: "Nume", celula: (r) => esc(`${r.nume || ""} ${r.prenume || ""}`.trim() || "—") },
    { titlu: "CNP", celula: (r) => esc(r.cnp || "—") },
    { titlu: "Data angajării", celula: (r) => esc(dataRo(r.data_angajare) || "—") },
    { titlu: "Funcția", celula: functie },
    { titlu: "Brut", num: true, celula: (r) => bani(r.salariu_brut) },
    { titlu: "Normă", celula: norma },
    { titlu: "Funcție de bază", celula: functieBaza },
    // [lotul 11, 420] valoarea care intră (propunerea „Nu” / 0, sau cea din fișa existentă), nu un text fix
    { titlu: "Scutit minim", celula: (r) => (dv(r).includes("scutit_contrib_minim") ? deVerificat(dn(!!r.scutit_contrib_minim)) : dn(r.scutit_contrib_minim)) },
    { titlu: "Persoane în întreținere", num: true, celula: (r) => (dv(r).includes("persoane_intretinere") ? deVerificat(esc(String(r.persoane_intretinere || 0))) : esc(String(r.persoane_intretinere || 0))) },
  ];

  corp.innerHTML = _cadruPrev(`
    <div class="mig-intro-rand"><p class="mig-intro"><b>${esc(firma.nume)}</b> · salariați încărcați</p><div class="mig-coer">${bandaStari(randuri)}</div></div>
    <div class="mig-sold-rezumat"><b>${randuri.length}</b> ${dupaNumar(randuri.length, "salariat", "salariați")}</div>`,
    `
    <div class="mig-avertismente">${_casetaFirma(date)}${_casetaInlocuire(date)}</div>
    ` + tabelPrevizualizare(coloane, randuri),
    `<div class="mig-eroare" id="mig-eroare"></div>
    <button class="buton-primar mig-buton" id="mig-salveaza-sal" data-actiune="POST /tenants/{tenant_id}/salariati-import">Salvează salariații</button>`);
  nav.setInapoi(() => nav.reiaPasul());   // [C140] „←” = alegerea fișierului, în pasul lui
  _arataFirma(corp, date, nav);   // [599]
  _arataInlocuirea(corp, date, nav);   // [446]
  gateazaPartial(corp, "mig-salveaza-sal", date.erori, randuri.length, "salariați");   // [decizia Costin 14.10.2026 pct.2]

  // [420] alegerea contabilului pe rând: valoarea intră în rândul trimis la salvare și iese din marcajul „de verificat”
  const randul = (el) => randuri.find((x) => String(x.rand_fisier) === el.dataset.rand);
  const confirmat = (r, camp) => { r.de_verificat = dv(r).filter((x) => x !== camp); };
  corp.querySelectorAll('[data-propus="tip_norma"]').forEach((sel) => sel.addEventListener("change", () => {
    const r = randul(sel);
    if (!r) return;
    r.tip_norma = sel.value;
    const ore = corp.querySelector(`#mig-ore-${CSS.escape(sel.dataset.rand)}`);
    ore.hidden = sel.value !== "partiala";
    r.ore_zi = sel.value === "partiala" ? (Number(ore.value) || 0) : 8;
    confirmat(r, "tip_norma");
  }));
  corp.querySelectorAll('[data-propus="ore_zi"]').forEach((inp) => inp.addEventListener("input", () => {
    const r = randul(inp);
    if (r) { r.ore_zi = Number(inp.value) || 0; confirmat(r, "tip_norma"); }
  }));
  corp.querySelectorAll('[data-propus="functie_baza"]').forEach((sel) => sel.addEventListener("change", () => {
    const r = randul(sel);
    if (r) { r.functie_baza = daNu(sel); confirmat(r, "functie_baza"); }
  }));

  const buton = corp.querySelector("#mig-salveaza-sal");
  const textButon = buton.textContent;
  buton.addEventListener("click", () => {
    async function salveaza(inlocuieste) {
      const eroare = corp.querySelector("#mig-eroare");
      buton.disabled = true; buton.textContent = "Salvez…";
      try {
        const rez = await api.post(`/tenants/${firma.tenant_id}/salariati-import`, { randuri, inlocuieste });
        // [decizia Costin 14.10.2026 pct.2] rândurile refuzate nu intră și se spun numite; celelalte s-au scris
        const refuzate = new Set(((rez && rez.respinse) || []).map((e) => String(e.rand)));   // rândurile care n-au intrat nu se numără
        const marcati = randuri.filter((r) => (r.de_verificat || []).length && !refuzate.has(String(r.rand_fisier))).length;
        // [lotul 11, 447: „«0 noi, 3 fișe actualizate», nu «3 importați» plus «3 actualizate»”] noi și actualizate, numărate la scriere
        _migMesaj = _mesajSalvarePartiala(rez, `Salariați: ${_noiActualizate(rez, "fișă actualizată", "fișe actualizate")}.`
          + (marcati ? ` ${marcati === 1 ? "Un salariat are" : cate(marcati, "salariat", "salariați") + " au"} date de verificat în Stat de plată (butonul „De verificat”).` : ""));
        if (marcati) _migTip = "avert";
        await _adaugaUrmatorii(firma); nav.inapoiPas();   // [664]
      } catch (e) {
        buton.disabled = false; buton.textContent = textButon;
        if (_inlocuire409(e, inlocuieste, eroare, "Actualizez fișele", salveaza)) return;   // [426]
        arataMesaj(eroare, (e && e.mesaj) || "Eroare la salvare.", "eroare");
      }
    }
    const eroare = corp.querySelector("#mig-eroare");
    eroare.textContent = "";
    curataEroriCamp(corp);
    // [420] norma parțială aleasă pe ecran cere orele pe zi (aceeași regulă ca salvarea: `ore_lipsa`)
    const faraOre = [...corp.querySelectorAll('[data-propus="ore_zi"]')].filter((i) => !i.hidden && !(Number(i.value) >= 1 && Number(i.value) <= 7.5));
    faraOre.forEach((i) => eroareCamp(corp, i.id, "Scrie orele pe zi ale normei parțiale (între 1 și 7,5)."));
    if (faraOre.length) return;
    // [FAPT_FISCAL_NECERUT] fiecare câmp propus are o valoare aleasă (propunerea sau alegerea contabilului) înainte de trimitere
    if (cereAlegerile(corp, [...normaEd].map((n) => `#mig-norma-${n}`).concat([...fbazaEd].map((n) => `#mig-fbaza-${n}`)))) return;
    _cuFirmaConfirmata(eroare, date, () => _confirmaInlocuirea(eroare, date, "Actualizez fișele", salveaza, "Actualizezi fișele salariaților existenți cu datele din fișier?"));   // [599]; [426] fișele salariaților existenți se actualizează confirmat
  });
}


// ---------- STRAT 5: ASOCIATI (per firma) ----------
async function wizardAsociati(corp, nav) {
  nav.setInapoi(undefined);
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se încarcă firmele…</p>`;
  let firme = [];
  try {
    const r = await api.get("/migrare/asociati");
    firme = (r && r.firme) || [];
  } catch {}

  const cuAsoc = firme.filter((f) => seStie(f) && f.are_asociati).length;
  corp.innerHTML = `
    <p class="mig-intro">Importă asociații firmei (nume, CNP/CUI, cotă %). Cotele se verifică automat — ar trebui să dea 100%.</p>
    <div class="mig-progres">${sumarStrat(firme, cuAsoc, "au asociați")}</div>
    <div class="mig-lista" id="mig-firme"></div>
    <button class="buton-primar mig-buton" id="mig-finalizeaza" data-actiune="POST /migrare/status" style="margin-top:16px">Am terminat asociații</button>
  `;

  const lista = corp.querySelector("#mig-firme");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio firmă în portofoliu. Importă întâi firmele (pasul 1).</div>`;
  }
  firme.forEach((f) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${seStie(f) ? (f.are_asociati ? cate(f.randuri, "asociat importat", "asociați importați") : "fără asociați încă") : prosText(f)}</div>
      </div>
      <span class="mig-stare ${seStie(f) ? (f.are_asociati ? "mig-ok" : "mig-gri") : prosClasa(f)}">${seStie(f) ? (f.are_asociati ? "✓ gata" : "de încărcat") : prosScurt(f)}</span>
    `;
    rand.addEventListener("click", () => nav.mergi("Import \u00b7 " + (f.nume || ""), (c) => importAsociatiFirma(c, nav, f)));  // faza_b3_migrare_v1
    lista.appendChild(rand);
  });

  corp.querySelector("#mig-finalizeaza").addEventListener("click", () => {
    const sumar = `<div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">Asociați: ${cuAsoc} din ${cate(firme.length, "firmă", "firme")}</div>
    </div>`;
    randeazaDecizie(corp, nav, "asociati", sumar, "Importul asociaților e complet?");
  });
  _consumaMigMesaj(corp);   // [423 a] confirmarea salvării făcute dintr-o firmă a acestei liste
}

function importAsociatiFirma(corp, nav, firma) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>Încarcă asociații (nume · CNP/CUI · cotă %).</p>
    <button type="button" class="buton-secundar mig-model" id="mig-model">Descarcă model (CSV)</button>
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" data-actiune="POST /tenants/{tenant_id}/asociati-import/incarca" accept=".csv,.txt,.tsv,.xlsx,.xls" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#6d28d9" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">Încarcă asociații</div>
      <div class="mig-drop-desc">Excel (XLSX, XLS) sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  _existaPas(corp, firma, "asociati");   // [lotul 13, 580 / 584] ce s-a adus deja și ce face importul cu ce există
  const fileInput = corp.querySelector("#mig-file");
  corp.querySelector("#mig-model")?.addEventListener("click", () => _descarcaModelCSV(MODELE.asociati));
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    eroare.textContent = "Se citesc asociații…";
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const r = await fetch(`/tenants/${firma.tenant_id}/asociati-import/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaAsociati(corp, nav, firma, date);
    } catch (e) {
      arataMesaj(eroare, (e && e.mesaj) || "Eroare la citirea fișierului.", "eroare");
    }
  });
}

function previzualizeazaAsociati(corp, nav, firma, date) {
  latime(corp, true);
  const randuri = cuStari(date.randuri || [], date.erori);
  const coer = date.coerenta || { total: 0, coincide: false };

  // [comanda Costin 8.2 pct.4; 364–367] tabelul comun: fiecare rând citit (și cel fără nume), cu starea și motivul lui; tipul nu se
  // ghicește pentru rândul fără CNP/CUI; CUI-ul persoanei juridice e confruntat cu ANAF (serverul spune dacă n-a putut).
  const banda = (coer.coincide
    ? `<span class="mig-eq mig-eq-ok">total cote: ✓ 100%</span>`
    : `<span class="mig-eq mig-eq-no">total cote: ⚠ ${baniRotund(coer.total)}%</span>`) + " " + bandaStari(randuri);
  const tip = (r) => (r.tip === "juridica" ? "juridică" : r.tip === "fizica" ? "fizică" : "—");
  const coloane = [
    { titlu: "Nume", celula: (r) => esc(r.nume || "—") },
    { titlu: "CNP / CUI", celula: (r) => esc(r.cnp || "—") },
    { titlu: "Persoană", celula: tip },
    { titlu: "Cotă %", num: true, celula: (r) => esc(String(r.cota ?? "—")) },
  ];

  corp.innerHTML = _cadruPrev(`
    <div class="mig-intro-rand"><p class="mig-intro"><b>${esc(firma.nume)}</b> · asociați încărcați</p><div class="mig-coer">${banda}</div></div>
    <div class="mig-sold-rezumat"><b>${randuri.length}</b> ${dupaNumar(randuri.length, "rând citit", "rânduri citite")}</div>`,
    `
    <div class="mig-avertismente">${_casetaFirma(date)}${_casetaInlocuire(date)}</div>
    ` + tabelPrevizualizare(coloane, randuri),
    `<div class="grila-doc" style="grid-template-columns:minmax(200px, 260px) minmax(240px, 1fr);margin-top:8px">
      <label class="camp"><span class="camp-eticheta">Data cesiunii</span>
      <input type="date" id="mig-asoc-cesiune" class="camp-input"></label>
      <span class="camp-ajutor">Numai dacă structura nouă o înlocuiește pe una anterioară: data transmiterii părților sociale (actul de cesiune / ONRC). Dividendele distribuite înainte rămân ale vechilor asociați (Legea 31/1990 art.67 alin.(6)). Gol = corectezi structura actuală.</span></div>
    <div class="mig-eroare" id="mig-eroare"></div>
    <button class="buton-primar mig-buton" id="mig-salveaza-asoc" data-actiune="POST /tenants/{tenant_id}/asociati-import">Salvează asociații</button>`);
  nav.setInapoi(() => nav.reiaPasul());   // [C140] „←” = alegerea fișierului, în pasul lui
  _arataFirma(corp, date, nav);   // [599]
  _arataInlocuirea(corp, date, nav);   // [446]
  gateazaPreview(corp, "mig-salveaza-asoc", date.erori);

  corp.querySelector("#mig-salveaza-asoc").addEventListener("click", () => {
    const eroare = corp.querySelector("#mig-eroare");
    const buton = corp.querySelector("#mig-salveaza-asoc");
    const data_cesiune = corp.querySelector("#mig-asoc-cesiune").value || null;
    async function salveaza(inlocuieste) {
      buton.disabled = true; buton.textContent = "Salvez…";
      try {
        const rez = await api.post(`/tenants/${firma.tenant_id}/asociati-import`, { randuri, data_cesiune, inlocuieste });
        // [426] confirmarea spune și ce structură s-a înlocuit (corectura) sau ce a rămas în istoric (cesiunea)
        const vechi = rez && rez.inlocuit ? ` Structura veche (${cate(rez.inlocuit.randuri, "asociat", "asociați")}) a fost înlocuită.` : "";
        _migMesaj = `${cate(randuri.length, "asociat salvat", "asociați salvați")}.` + vechi + (rez && rez.arhivati ? ` Structura anterioară (${cate(rez.arhivati, "asociat", "asociați")}) rămâne valabilă până la ${dataRo(data_cesiune)} exclusiv, pentru dividendele distribuite înainte.` : "");
        await _adaugaUrmatorii(firma); nav.inapoiPas();   // [664]
      } catch (e) {
        buton.disabled = false; buton.textContent = "Salvează asociații";
        if (_inlocuire409(e, inlocuieste, eroare, "Înlocuiesc asociații", salveaza)) return;   // [426]
        arataMesaj(eroare, (e && e.mesaj) || "Eroare la salvare.", "eroare");
      }
    }
    eroare.textContent = "";
    // [426] cu data cesiunii structura de acum intră în istoric (nu se pierde) -> fără confirmare; fără ea, corectura cere confirmarea,
    // cu structura veche și nouă și notele de dividende care se împart după ea
    if (data_cesiune) _cuFirmaConfirmata(eroare, date, () => salveaza(false));   // [599]
    else _cuFirmaConfirmata(eroare, date, () => _confirmaInlocuirea(eroare, date, "Înlocuiesc asociații", salveaza, "Înlocuiești asociații firmei cu cei din fișier?"));   // [599]
  });
}


// ---------- STRAT 6: MIJLOACE FIXE (per firma) ----------
async function wizardMijloace(corp, nav) {
  nav.setInapoi(undefined);
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se încarcă firmele…</p>`;
  let firme = [];
  try {
    const r = await api.get("/migrare/mijloace-fixe");
    firme = (r && r.firme) || [];
  } catch {}

  const cuMF = firme.filter((f) => seStie(f) && f.are_mijloace).length;
  corp.innerHTML = `
    <p class="mig-intro">Importă registrul de mijloace fixe: valoarea de intrare, data PIF, durata, metoda, conturile și amortizarea cumulată la data preluării. iConta.eu o compară cu cea calculată din PIF, durată și metodă și confruntă totalurile cu balanța de deschidere; amortizarea continuă, nu se reia de la zero. Valoarea reziduală (opțională, implicit 0) e partea care nu se amortizează — nu valoarea rămasă.</p>
    <div class="mig-progres">${sumarStrat(firme, cuMF, "au mijloace fixe")}</div>
    <div class="mig-lista" id="mig-firme"></div>
    <button class="buton-primar mig-buton" id="mig-finalizeaza" data-actiune="POST /migrare/status" style="margin-top:16px">Am terminat mijloacele fixe</button>
  `;

  const lista = corp.querySelector("#mig-firme");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio firmă în portofoliu. Importă întâi firmele (pasul 1).</div>`;
  }
  firme.forEach((f) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${seStie(f) ? (f.are_mijloace ? cate(f.randuri, "mijloc fix importat", "mijloace fixe importate") : "fără mijloace fixe încă") : prosText(f)}</div>
      </div>
      <span class="mig-stare ${seStie(f) ? (f.are_mijloace ? "mig-ok" : "mig-gri") : prosClasa(f)}">${seStie(f) ? (f.are_mijloace ? "✓ gata" : "de încărcat") : prosScurt(f)}</span>
    `;
    rand.addEventListener("click", () => nav.mergi("Import \u00b7 " + (f.nume || ""), (c) => importMijloaceFirma(c, nav, f, _aplicatie)));  // faza_b3_migrare_v1
    lista.appendChild(rand);
  });

  corp.querySelector("#mig-finalizeaza").addEventListener("click", () => {
    const sumar = `<div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">Mijloace fixe: ${cuMF} din ${cate(firme.length, "firmă", "firme")}</div>
    </div>`;
    randeazaDecizie(corp, nav, "mijloace_fixe", sumar, "Importul mijloacelor fixe e complet?");
  });
  _consumaMigMesaj(corp);   // [423 a] confirmarea salvării făcute dintr-o firmă a acestei liste
}

function importMijloaceFirma(corp, nav, firma, app = null) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>Încarcă registrul de mijloace fixe (cod · denumire · valoare de intrare · durată · PIF · metodă · cont imobilizare · cont amortizare · amortizarea cumulată · valoarea reziduală la sfârșitul duratei, de obicei 0 — nu valoarea rămasă). Un bun sub plafonul de mijloc fix la data intrării e obiect de inventar și nu intră.</p>
    ${_exportHTML(app, "mijloace_fixe") || `<button type="button" class="buton-secundar mig-model" id="mig-model">Descarcă model (CSV)</button>`}
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" data-actiune="POST /tenants/{tenant_id}/mijloace-fixe-import/incarca" accept=".csv,.txt,.tsv,.xlsx,.xls" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#c0492b" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">Încarcă mijloacele fixe</div>
      <div class="mig-drop-desc">Excel (XLSX, XLS) sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  _existaPas(corp, firma, "mijloace_fixe");   // [lotul 13, 580 / 584] ce s-a adus deja și ce face importul cu ce există
  const fileInput = corp.querySelector("#mig-file");
  corp.querySelector("#mig-model")?.addEventListener("click", () => _descarcaModelCSV(MODELE.mijloace));
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    eroare.textContent = "Se citesc mijloacele fixe…";
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const r = await fetch(`/tenants/${firma.tenant_id}/mijloace-fixe-import/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaMijloace(corp, nav, firma, date);
    } catch (e) {
      arataMesaj(eroare, (e && e.mesaj) || "Eroare la citirea fișierului.", "eroare");
    }
  });
}

// [comanda Costin 8.2 pct.4: „orice rând citit e afișat sau semnalat cu motiv”] rândurile citite care nu sunt de importat (total, titlu,
// sold 0) — spuse cu motivul lor, nu sărite în tăcere
function casetaIgnorate(ignorate) {
  ignorate = ignorate || [];
  if (!ignorate.length) return "";
  // [lotul 11, 424] numărul la vedere, lista pliată (totalurile, partenerii cu sold 0): nu lungește rezumatul lipit sus
  return `<details class="dec-xml" id="mig-ignorate"><summary>${ignorate.length === 1 ? "Un rând citit nu e de importat" : cate(ignorate.length, "rând citit nu e", "rânduri citite nu sunt") + " de importat"}</summary><ul>${ignorate.map((x) => `<li>${esc(undeE(x))}: ${esc(x.motiv || "")}</li>`).join("")}</ul></details>`;
}

// [359 / 374, comanda Costin 8.2] registrul preluat (mijloace fixe, stoc) față de balanța de deschidere, pe fiecare cont atins
function casetaReconciliere(rec, data, numeRegistru, conturi, fel) {
  rec = rec || [];
  if (!rec.length) return "";
  if (rec.every((c) => c.balanta == null)) {
    return `<div class="caseta-info" style="margin:8px 0"><div class="ca-mesaj">Balanța de deschidere nu e încă importată (Solduri inițiale), deci totalurile pe ${esc(conturi)} nu se pot confrunta cu ea; auditul de preluare le confruntă după.</div></div>`;
  }
  // [lotul 13, deficiența 609: „Soldurile creditoare și diferențele apar cu minus”] diferența fără semn, cu sensul ei în cuvinte
  const dif = (d) => (d < 0 ? `în ${numeRegistru} lipsesc ${bani(Math.abs(d))} lei` : `în ${numeRegistru} sunt cu ${bani(d)} lei mai mult`);
  const nepotrivit = rec.some((c) => c.diferenta != null && Math.abs(c.diferenta) > 0.005);
  const linie = (c) => `<li>${esc(c.cont)}${fel ? ` (${esc(fel(c))})` : ""}: ${esc(numeRegistru)} ${bani(c.registru)} lei · balanță ${bani(Math.abs(c.balanta))} lei${Math.abs(c.diferenta) > 0.005 ? ` · <b>${dif(c.diferenta)}</b>` : " · se potrivesc"}</li>`;
  // [668] la stocul inițial, contul nepotrivit nu intră (serverul îi respinge rândurile): spus în casetă
  return `<div class="${nepotrivit ? "caseta-atentie" : "caseta-info"}" id="mig-reconciliere" style="margin:8px 0"><div class="ca-mesaj">Față de balanța de deschidere${data ? " la " + esc(dataRo(data)) : ""}${nepotrivit && numeRegistru === "stoc inițial" ? " — rândurile contului care nu se potrivește nu intră" : ""}:<ul>${rec.map(linie).join("")}</ul></div></div>`;
}

function previzualizeazaMijloace(corp, nav, firma, date) {
  latime(corp, true);
  const randuri = date.randuri || [];
  // [359] reconcilierea cu balanța de deschidere, pe fiecare cont atins: imobilizarea (valoarea de intrare), amortizarea (cea preluată)
  const recHtml = casetaReconciliere(date.reconciliere, date.data_preluare, "registru", "conturile 2xx / 28xx",
    (c) => (c.fel === "imobilizare" ? "valoarea de intrare" : "amortizarea preluată"));
  corp.innerHTML = _cadruPrev(`
    <div class="mig-intro-rand"><p class="mig-intro"><b>${esc(firma.nume)}</b> · mijloace fixe încărcate${date.data_preluare ? ` · amortizarea preluată se compară la ${esc(dataRo(date.data_preluare))}, data balanței de deschidere` : ""}</p><div class="mig-coer">${bandaStari(randuri)}</div></div>
    <div class="mig-sold-rezumat"><b>${randuri.length}</b> ${dupaNumar(randuri.length, "rând citit", "rânduri citite")} · valoare de intrare <b>${bani(date.total_valoare)}</b> lei</div>`,
    `
    <div class="mig-avertismente">${_casetaFirma(date)}${_casetaInlocuire(date)}${recHtml}</div>
    ` + tabelPrevizualizare([   // [581] confruntarea cu balanța în pagină, nu în rezumatul lipit sus
      { titlu: "Cod", celula: (r) => esc(r.cod || "—") },
      { titlu: "Denumire", celula: (r) => esc(r.denumire || "—") },
      { titlu: "Valoare intrare", num: true, celula: (r) => `${bani(r.valoare)} lei` },
      { titlu: "Data PIF", celula: (r) => esc(dataRo(r.data_pif) || r.data_pif_brut || "—") },
      { titlu: "Durată", celula: (r) => r.dnf_luni ? esc(cate(r.dnf_luni, "lună", "luni")) : "—" },
      { titlu: "Metodă", celula: (r) => esc(r.metoda || r.metoda_brut || "—") },
      { titlu: "Cont imobilizare", celula: (r) => esc(r.cont_imobilizare || "—") },
      { titlu: "Cont amortizare", celula: (r) => esc(r.cont_amortizare || "—") },
      { titlu: "Amortizare preluată", num: true, celula: (r) => r.amortizat_preluat != null ? `${bani(r.amortizat_preluat)} lei` : "—" },
      { titlu: "Amortizare calculată", num: true, celula: (r) => r.amortizat_calculat != null ? `${bani(r.amortizat_calculat)} lei` : "—" },
      { titlu: "Valoare reziduală (neamortizată)", num: true, celula: (r) => `${bani(r.rezidual)} lei` },   // [587] nu „valoarea rămasă”
    ], randuri),
    `<div class="mig-eroare" id="mig-eroare"></div>
    <button class="buton-primar mig-buton" id="mig-salveaza-mf" data-actiune="POST /tenants/{tenant_id}/mijloace-fixe-import">${date.existenta ? "Înlocuiește registrul" : "Salvează mijloacele fixe"}</button>`);
  nav.setInapoi(() => nav.reiaPasul());   // [C140] „←” = alegerea fișierului, în pasul lui
  _arataFirma(corp, date, nav);   // [599]
  _arataInlocuirea(corp, date, nav);   // [446]
  gateazaPartial(corp, "mig-salveaza-mf", date.erori, randuri.length, "mijloace fixe");
  const buton = corp.querySelector("#mig-salveaza-mf");
  const textButon = buton.textContent;
  const eroare = corp.querySelector("#mig-eroare");
  // [426] registrul cu reevaluări / schimbări consemnate pe fișă nu se înlocuiește prin import: spus înainte, salvarea oprită
  if (date.inlocuire_refuzata) {
    arataMesaj(eroare, date.inlocuire_refuzata, "avert");
    buton.disabled = true;
  }

  buton.addEventListener("click", () => {
    async function salveaza(inlocuieste) {
      buton.disabled = true; buton.textContent = "Salvez…";
      try {
        const rez = await api.post(`/tenants/${firma.tenant_id}/mijloace-fixe-import`, { randuri, inlocuieste });
        const n = (rez && rez.importati) || 0;
        // [426] confirmarea spune și ce registru s-a înlocuit
        const vechi = rez && rez.inlocuit ? ` Registrul vechi (${cate(rez.inlocuit.randuri, "mijloc fix", "mijloace fixe")}) a fost înlocuit.` : "";
        _migMesaj = _mesajSalvarePartiala(rez, `${n === 1 ? "Un mijloc fix importat" : cate(n, "mijloc fix importat", "mijloace fixe importate")}.${vechi}`); await _adaugaUrmatorii(firma); nav.inapoiPas();   // [664]
      } catch (e) {
        buton.disabled = false; buton.textContent = textButon;
        if (_inlocuire409(e, inlocuieste, eroare, "Înlocuiesc registrul", salveaza)) return;   // [426]
        arataMesaj(eroare, (e && e.mesaj) || "Eroare la salvare.", "eroare");
      }
    }
    eroare.textContent = "";
    _cuFirmaConfirmata(eroare, date, () => _confirmaInlocuirea(eroare, date, "Înlocuiesc registrul", salveaza, "Înlocuiești registrul mijloacelor fixe cu cel din fișier?"));   // [599]; [426] cu valorile vechi și noi și amortizările înregistrate
  });
}


// ---------- STRAT 7: ISTORIC DECLARATII (per firma) ----------
async function wizardIstoric(corp, nav) {
  nav.setInapoi(undefined);
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se încarcă firmele…</p>`;
  let firme = [];
  try {
    const r = await api.get("/migrare/istoric-declaratii");
    firme = (r && r.firme) || [];
  } catch {}

  const cuIst = firme.filter((f) => f.are_istoric).length;
  corp.innerHTML = `
    <p class="mig-intro">Importă declarațiile deja depuse anul curent (la vechiul program). Astfel iConta.eu nu le mai cere ca restanță.</p>
    <div class="mig-progres">${cuIst} din ${cate(firme.length, "firmă", "firme")} ${cuIst === 1 ? "are" : "au"} istoric</div>
    <div class="mig-lista" id="mig-firme"></div>
    <button class="buton-primar mig-buton" id="mig-finalizeaza" data-actiune="POST /migrare/status" style="margin-top:16px">Am terminat istoricul declarațiilor</button>
  `;

  const lista = corp.querySelector("#mig-firme");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio firmă în portofoliu. Importă întâi firmele (pasul 1).</div>`;
  }
  firme.forEach((f) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${f.are_istoric ? cate(f.randuri, "declarație înregistrată", "declarații înregistrate") : "fără istoric încă"}</div>
      </div>
      <span class="mig-stare ${f.are_istoric ? "mig-ok" : "mig-gri"}">${f.are_istoric ? "✓ gata" : "de încărcat"}</span>
    `;
    rand.addEventListener("click", () => nav.mergi("Import \u00b7 " + (f.nume || ""), (c) => importIstoricFirma(c, nav, f)));  // faza_b3_migrare_v1
    lista.appendChild(rand);
  });

  corp.querySelector("#mig-finalizeaza").addEventListener("click", () => {
    const sumar = `<div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">Istoric: ${cuIst} din ${cate(firme.length, "firmă", "firme")}</div>
    </div>`;
    randeazaDecizie(corp, nav, "istoric_declaratii", sumar, "Istoricul declarațiilor e complet?");
  });
  _consumaMigMesaj(corp);   // [423 a] confirmarea salvării făcute dintr-o firmă a acestei liste
}

function importIstoricFirma(corp, nav, firma) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>Încarcă declarațiile depuse (tip · an · lună · data depunerii · suma de plată). La o declarație trimestrială, luna e ultima a trimestrului (03 = T1). Suma de plată se cere la D100 pe impozitul pe profit: D100 de pe trimestrele următoare scade impozitul deja declarat.</p>
    <button type="button" class="buton-secundar mig-model" id="mig-model">Descarcă model (CSV)</button>
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" data-actiune="POST /tenants/{tenant_id}/istoric-declaratii-import/incarca" accept=".csv,.txt,.tsv,.xlsx,.xls" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#45597f" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 13l2 2 4-4"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">Încarcă declarațiile</div>
      <div class="mig-drop-desc">Excel (XLSX, XLS) sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  _existaPas(corp, firma, "istoric_declaratii");   // [lotul 13, 580 / 584] ce s-a adus deja și ce face importul cu ce există
  const fileInput = corp.querySelector("#mig-file");
  corp.querySelector("#mig-model")?.addEventListener("click", () => _descarcaModelCSV(MODELE.istoric));
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    eroare.textContent = "Se citesc declarațiile…";
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const r = await fetch(`/tenants/${firma.tenant_id}/istoric-declaratii-import/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaIstoric(corp, nav, firma, date);
    } catch (e) {
      arataMesaj(eroare, (e && e.mesaj) || "Eroare la citirea fișierului.", "eroare");
    }
  });
}

function previzualizeazaIstoric(corp, nav, firma, date) {
  latime(corp, true);
  const randuri = date.randuri || [];
  // [351] declarația anuală se arată ca anuală, nu cu luna 12 („dec”) sub care se ține în evidență; luna + anul prin formatorul canonic
  // (DS cap.4: „03/2026”); o lună în afara 1–12 sau anul lipsă se arată cum au venit din fișier
  // [389, lotul 9] perioada vine de la server, după profilul firmei („T1/2026” la declarațiile ei trimestriale)
  const perioada = (r) => r.perioada ? r.perioada : r.anuala ? `anuală ${r.an || "—"}`
    : (r.luna >= 1 && r.luna <= 12 && r.an ? dataRo(new Date(r.an, r.luna - 1, 1), "luna_an_numeric") : `${r.luna || "—"} ${r.an || "—"}`);
  corp.innerHTML = _cadruPrev(`
    <div class="mig-intro-rand"><p class="mig-intro"><b>${esc(firma.nume)}</b> · istoric declarații</p><div class="mig-coer">${bandaStari(randuri)}</div></div>
    <div class="mig-sold-rezumat"><b>${randuri.length}</b> ${dupaNumar(randuri.length, "rând citit", "rânduri citite")} din fișier</div>`,
    `
    <div class="mig-avertismente">${_casetaFirma(date)}${_casetaInlocuire(date)}</div>
    ` + tabelPrevizualizare([
      { titlu: "Tip", celula: (r) => esc(r.tip || "—") },
      { titlu: "Perioada", celula: (r) => esc(perioada(r)) },
      { titlu: "Data depunerii", celula: (r) => esc(dataRo(r.data_depunere) || r.data_brut || "—") },
      { titlu: "Suma declarată", num: true, celula: (r) => r.suma != null ? `${bani(r.suma)} lei` : (r.tip === "D100" ? "—" : "") },
    ], randuri),
    `<div class="mig-eroare" id="mig-eroare"></div>
    <button class="buton-primar mig-buton" id="mig-salveaza-ist" data-actiune="POST /tenants/{tenant_id}/istoric-declaratii-import">${date.existenta ? "Înlocuiește istoricul" : "Salvează istoricul"}</button>`);
  nav.setInapoi(() => nav.reiaPasul());   // [C140] „←” = alegerea fișierului, în pasul lui
  _arataFirma(corp, date, nav);   // [599]
  _arataInlocuirea(corp, date, nav);   // [446]
  gateazaPartial(corp, "mig-salveaza-ist", date.erori, randuri.length, "declarații");
  const buton = corp.querySelector("#mig-salveaza-ist");
  const textButon = buton.textContent;
  const eroare = corp.querySelector("#mig-eroare");

  buton.addEventListener("click", () => {
    async function salveaza(inlocuieste) {
      buton.disabled = true; buton.textContent = "Salvez…";
      try {
        const rez = await api.post(`/tenants/${firma.tenant_id}/istoric-declaratii-import`, { randuri, inlocuieste });
        const n = (rez && rez.importati) || 0;
        // [426] confirmarea spune și ce istoric s-a înlocuit
        const vechi = rez && rez.inlocuit ? ` Istoricul preluat vechi (${cate(rez.inlocuit.randuri, "declarație", "declarații")}) a fost înlocuit.` : "";
        _migMesaj = _mesajSalvarePartiala(rez, `${n === 1 ? "O declarație din istoric salvată" : cate(n, "declarație din istoric salvată", "declarații din istoric salvate")}.${vechi}`); await _adaugaUrmatorii(firma); nav.inapoiPas();   // [664]
      } catch (e) {
        buton.disabled = false; buton.textContent = textButon;
        if (_inlocuire409(e, inlocuieste, eroare, "Înlocuiesc istoricul", salveaza)) return;   // [426]
        arataMesaj(eroare, (e && e.mesaj) || "Eroare la salvare.", "eroare");
      }
    }
    eroare.textContent = "";
    _cuFirmaConfirmata(eroare, date, () => _confirmaInlocuirea(eroare, date, "Înlocuiesc istoricul", salveaza, "Înlocuiești istoricul declarațiilor preluat cu cel din fișier?"));   // [599]; [426] cu declarațiile și perioadele vechi și noi
  });
}

// faza_b3_migrare_v1

// ---------- WIZARD PLAN DE CONTURI [p95_plan_conturi] ----------
async function wizardPlanConturi(corp, nav) {
  nav.setInapoi(undefined);
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103 firmele\u2026</p>`;
  let firme = [];
  try {
    const r = await api.get("/migrare/plan-conturi");
    firme = (r && r.firme) || [];
  } catch {}
  corp.innerHTML = `
    <p class="mig-intro">Planul standard OMFP e deja \u00eencărcat automat la fiecare firm\u0103. Aici adaugi conturi analitice sau nestandard (ex: leasing IFRS) pentru firme cu nevoi speciale.</p>
    <div class="mig-lista" id="mig-firme"></div>
    <button class="buton-primar mig-buton" id="mig-finalizeaza" data-actiune="POST /migrare/status" style="margin-top:16px">Am terminat planul de conturi</button>
  `;
  const lista = corp.querySelector("#mig-firme");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio firm\u0103 \u00een portofoliu. Import\u0103 \u00eent\u00e2i firmele (pasul 1).</div>`;
  }
  firme.forEach((f) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${seStie(f) ? `${cate(f.nr_conturi, "cont", "conturi")} \u00een plan` : prosText(f)}</div>
      </div>
      <span class="mig-stare ${seStie(f) ? (f.nr_conturi > 0 ? "mig-ok" : "mig-gri") : prosClasa(f)}">${seStie(f) ? (f.nr_conturi > 0 ? "\u2713 populat" : "gol") : prosScurt(f)}</span>
    `;
    rand.addEventListener("click", () => nav.mergi("Plan de conturi \u00b7 " + (f.nume || ""), (c) => importPlanConturiFirma(c, nav, f)));
    lista.appendChild(rand);
  });
  corp.querySelector("#mig-finalizeaza").addEventListener("click", () => {
    const sumar = `<div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">Plan de conturi: ${cate(firme.length, "firmă verificată", "firme verificate")}</div>
    </div>`;
    randeazaDecizie(corp, nav, "plan_conturi", sumar, "Planul de conturi e complet pentru toate firmele?");
  });
  _consumaMigMesaj(corp);   // [423 a] confirmarea salvării făcute dintr-o firmă a acestei liste
}
function importPlanConturiFirma(corp, nav, firma) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>Caut\u0103 \u00een planul existent sau adaug\u0103 un cont nou.</p>
    <input type="text" class="camp-input" id="pc-cauta" aria-label="Caut\u0103 \u00een plan" placeholder="Caut\u0103 dup\u0103 simbol sau denumire\u2026" style="width:100%;margin-bottom:10px">
    <div class="mig-lista" id="pc-rezultate"></div>
    <div class="mig-eticheta" style="margin-top:16px">Adaug\u0103 cont nou <span class="oblig">*</span></div>
    <div style="display:flex;gap:8px;margin-top:6px">
      <input type="text" class="camp-input" id="pc-simbol" aria-label="Simbol cont" aria-required="true" placeholder="Simbol (ex: 4428)" style="width:140px">
      <input type="text" class="camp-input" id="pc-denumire" aria-label="Denumire cont" aria-required="true" placeholder="Denumire" style="flex:1">
    </div>
    <div class="mig-eroare" id="pc-eroare"></div>
    <button class="buton-primar mig-buton" id="pc-adauga" data-actiune="POST /tenants/{tenant_id}/plan-conturi" style="margin-top:10px">Adaug\u0103 cont</button>
  `;
  const rezZona = corp.querySelector("#pc-rezultate");
  const cautaInput = corp.querySelector("#pc-cauta");
  const cerereNoua = ultimaCerere();   // [C103] căutarea la tastare: numai rezultatul ultimului termen tastat ajunge pe ecran
  async function cauta(q) {
    const actuala = cerereNoua();
    rezZona.innerHTML = `<p class="ecran-nota">Se caut\u0103\u2026</p>`;
    try {
      const r = await api.get(`/tenants/${firma.tenant_id}/plan-conturi${q ? "?q=" + encodeURIComponent(q) : ""}`);
      if (!actuala()) return;
      const conturi = (r && r.conturi) || [];
      rezZona.innerHTML = conturi.length
        ? conturi.map((c) => `<div class="mig-frand" style="cursor:default">
            <div class="mig-frand-text">
              <div class="mig-frand-nume">${esc(c.simbol)} \u00b7 ${esc(c.denumire)}</div>
              <div class="mig-frand-sub">${esc(c.tip || "")}${c.in_afara_planului ? " \u00b7 în afara planului legal al normei firmei" : ""}</div>
            </div>
          </div>`).join("")
        : `<div class="stare-goala">Niciun cont g\u0103sit cu acest termen.</div>`;
    } catch {
      if (!actuala()) return;
      arataMesaj(rezZona, "Eroare la căutare.", "eroare");
    }
  }
  cauta("");
  let timer = null;
  cautaInput.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => cauta(cautaInput.value.trim()), 300);
  });
  corp.querySelector("#pc-adauga").addEventListener("click", async () => {
    const eroare = corp.querySelector("#pc-eroare");
    const inpS = corp.querySelector("#pc-simbol"), inpD = corp.querySelector("#pc-denumire");
    eroare.textContent = "";
    [inpS, inpD].forEach((i) => { i.classList.remove("camp-invalid"); i.removeAttribute("aria-invalid"); });
    const simbol = inpS.value.trim();
    const denumire = inpD.value.trim();
    if (!simbol || !denumire) {   // Regula 14.4 pct.4: marcheaza CARE camp lipseste, nu mesaj generic
      if (!simbol) { inpS.classList.add("camp-invalid"); inpS.setAttribute("aria-invalid", "true"); }
      if (!denumire) { inpD.classList.add("camp-invalid"); inpD.setAttribute("aria-invalid", "true"); }
      eroare.textContent = (!simbol && !denumire) ? "Completează simbolul și denumirea contului."
        : (!simbol ? "Completează simbolul contului (ex. 4428)." : "Completează denumirea contului.");
      focusFaraSalt(!simbol ? inpS : inpD);
      return;
    }
    try {
      const rs = await api.post(`/tenants/${firma.tenant_id}/plan-conturi`, { simbol, denumire });
      inpS.value = ""; inpD.value = "";
      await cauta(cautaInput.value.trim());
      // [08.10, V3] „un cont care nu e în planul legal nu se poate crea … fără avertisment”
      if (rs && rs.avertisment) arataMesaj(eroare, rs.avertisment.motiv || "Cont în afara planului legal.", "avert");
      // [lotul 10, 423 a — clasa 410, DS cap.27] actul se încheie cu o confirmare care numește contul
      else arataMesaj(eroare, `Contul ${simbol} — ${denumire} a fost adăugat în planul de conturi al firmei.`, "ok");
    } catch (e) {
      if (e && e.cod === 409) { inpS.classList.add("camp-invalid"); inpS.setAttribute("aria-invalid", "true"); focusFaraSalt(inpS); }
      eroare.textContent = (e && e.mesaj) || "Eroare la salvare.";
    }
  });
}

// [lotul 13, deficiența 662, comanda Costin 13.1: „O firmă abia creată, fără solduri, se deschide pe «Zilnic» (facturi, salarii); preluarea nu
// apare nicăieri. Firma nouă trebuie să deschidă cu «Începe preluarea».”] În fereastra firmei, deasupra grupurilor de carduri: firma fără
// nimic adus și fără activitate -> „Începe preluarea”; preluarea începută (balanța adusă, nicio notă încă) cu pași obligatorii rămași ->
// „Continuă preluarea”, cu pașii numiți (664). Butonul deschide „Import date” al firmei; nimic nu se deschide singur.
export async function randeazaPreluareFirma(corp, nav, t) {
  if (!corp) return;
  const st = await _starePreluare(t.id);
  if (!st || !corp.isConnected) return;
  const urm = st.urmatori || [];
  if (!st.incepe_preluarea && !(st.in_preluare && urm.length)) { corp.innerHTML = ""; _consumaMigMesaj(corp); return; }
  corp.innerHTML = `<div class="caseta-info" id="firma-preluare-caseta" style="margin-bottom:12px"><div class="ca-mesaj">${st.incepe_preluarea
    ? "Firma e nouă în iConta.eu: nu are încă nimic adus din programul vechi (vectorul fiscal, balanța de deschidere, partenerii, stocurile). Începe cu preluarea."
    : `Preluarea firmei nu e terminată. De făcut: ${esc(urm.map(_titluStrat).join(", "))}.`}</div>
    <div class="ca-actiuni"><button type="button" class="buton-primar" id="fa-preluare" data-fara-actiune="deschide Import date al firmei">${st.incepe_preluarea
      ? "Începe preluarea" : "Continuă preluarea"}</button></div></div>`;
  corp.querySelector("#fa-preluare").addEventListener("click", () =>
    nav.mergi("Import date", (c) => meniuMigrarePerFirma(c, nav, { tenant_id: t.id, nume: t.nume, tip_firma: t.tip_firma })));
  _consumaMigMesaj(corp);   // [423 a] fereastra firmei e ecran în care se revine: o confirmare rămasă se arată aici, nu se pierde
}

// ---------- MENIU MIGRARE PER FIRMA [p96_import_firma] ----------
// Deschis din fisa unei firme (cardul "Import date") - sare peste pasul de
// selectie a firmei, duce direct in ecranul de import per-strat pentru firma curenta.
export async function meniuMigrarePerFirma(corp, nav, firma) {
  nav.setInapoi(null);
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;
  // [p_pfa_rip 20.07] Straturile aplicabile regimului vin din backend (straturi_pentru), SURSA UNICA -
  // meniul NU reinventeaza in JS ce strat apartine carui regim (nu deriva din regim_contabil aici).
  // Pasii cu 'strat' apar doar daca stratul e aplicabil; pasii fara 'strat' (articole/retete) raman mereu.
  const tip = firma.tip_firma.toLowerCase();   // backendul garanteaza tip_firma; fara fallback tacit
  let aplicabile = null;
  try {
    // [371, lotul 9] straturile FIRMEI (regim + HoReCa la Rețete), din aceeași regulă ca lista din Migrare cabinet
    const r = await api.get(`/migrare/straturi?tip_firma=${encodeURIComponent(tip)}&tenant_id=${encodeURIComponent(firma.tenant_id)}`);
    aplicabile = (r && r.straturi) || null;
  } catch {}
  if (!aplicabile || !aplicabile.length) {
    // straturi_pentru nu a raspuns -> NU ghicim filtrarea in JS (un PFA ar vedea pasii de partida dubla).
    // Stare-goala canonica + reincercare, nu "arata tot".
    corp.innerHTML = `<div class="stare-goala">Nu s-au putut încărca pașii de import pentru firmă.
      <button class="btn-link" id="mig-reincearca">Reîncearcă</button></div>`;
    corp.querySelector("#mig-reincearca").addEventListener("click", () => meniuMigrarePerFirma(corp, nav, firma));
    return;
  }
  const PASI = [
    { titlu: "Vector fiscal", desc: "TVA, regim, intracomunitar", strat: "vector_fiscal", fn: (c, n) => formularVectorFirma(c, n, firma) },
    { titlu: "Solduri ini\u021biale", desc: "Balan\u021ba de deschidere", strat: "solduri", fn: (c, n) => importSolduriFirma(c, n, firma) },
    { titlu: "Solduri parteneri", desc: "4111/401 pe client \u0219i furnizor", strat: "solduri_parteneri", fn: (c, n) => importParteneriFirma(c, n, firma) },
    { titlu: "Salaria\u021bi", desc: "Nume, CNP, salariu, contract", strat: "salariati", fn: (c, n) => importSalariatiFirma(c, n, firma) },
    { titlu: "Asocia\u021bi", desc: "Nume, cot\u0103 % (D205)", strat: "asociati", fn: (c, n) => importAsociatiFirma(c, n, firma) },
    { titlu: "Mijloace fixe", desc: "Registru amortizare", strat: "mijloace_fixe", fn: (c, n) => importMijloaceFirma(c, n, firma) },
    { titlu: "Istoric declara\u021bii", desc: "Ce s-a depus deja", strat: "istoric_declaratii", fn: (c, n) => importIstoricFirma(c, n, firma) },
    { titlu: "Plan de conturi", desc: "Conturi analitice sau nestandard", strat: "plan_conturi", fn: (c, n) => importPlanConturiFirma(c, n, firma) },
    { titlu: "Import RIP", desc: "Registru \u00eencas\u0103ri-pl\u0103\u021bi (istoric PFA, partid\u0103 simpl\u0103)", strat: "rip", fn: (c, n) => importRipFirma(c, n, firma) },
    { titlu: "Articole \u0219i stoc ini\u021bial", desc: "Nomenclator + cantit\u0103\u021bi la CMP (gestiune CV)", strat: "articole", fn: (c, n) => importArticoleFirma(c, n, firma) },
    { titlu: "Re\u021bete (HoReCa)", desc: "Re\u021betar: ingrediente \u0219i cantit\u0103\u021bi pe por\u021bie", strat: "retete", fn: (c, n) => importReteteFirma(c, n, firma) },
  ];
  // [368 / 371] fiecare pas are stratul lui; aplicabilitatea pe regim vine NUMAI din `/migrare/straturi` (`migrare_api.STRATURI_META`)
  // ascunde straturile neaplicabile regimului (ex: PFA nu vede partida dubla). aplicabile = garantat
  // non-null aici (altfel am iesit mai sus cu stare-goala) -> filtram mereu, fara "arata tot".
  const pasiVizibili = PASI.filter((p) => aplicabile.includes(p.strat));
  // [lotul 13, 663 / 580 / 664] starea fiecărui pas al firmei (gata / obligatoriu / nu e cazul / dacă e cazul) și ce s-a adus deja
  const stare = await _starePreluare(firma.tenant_id);
  const pasi = (stare && stare.pasi) || {};
  const urm = (stare && stare.urmatori) || [];
  corp.innerHTML = `
    <p class="mig-intro">Alege ce vrei s\u0103 aduci pentru aceast\u0103 firm\u0103.${stare && stare.incepe_preluarea
      ? " Firma nu are încă nimic adus: începe cu vectorul fiscal și soldurile inițiale (balanța de deschidere)." : ""}</p>
    ${urm.length ? `<p class="mig-intro mig-op-sub-alert" id="mig-urmatori">De făcut: ${esc(urm.map(_titluStrat).join(", "))}.</p>` : ""}
    <div class="mig-lista" id="mig-pasi"></div>
  `;
  const lista = corp.querySelector("#mig-pasi");
  pasiVizibili.forEach((p) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.dataset.strat = p.strat;
    // [drepturi_rol 04.10.2026] pasul poartă ruta care îl face — din STRATURI (sursa unică) sau, pentru cele trei
    // importuri fără strat, scrisă pe pas; poarta din drepturi.js ascunde pasul refuzat rolului
    const _act = p.actiune || (STRATURI.find((s) => s.cheie === p.strat) || {}).actiune;
    if (_act) rand.dataset.actiune = _act;
    const ps = pasi[p.strat];
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${p.titlu}</div>
        <div class="mig-frand-sub">${ps ? esc(ps.stare === "gata" && ps.exista ? ps.exista : ps.detaliu) : p.desc}</div>
      </div>
      ${_badgePas(ps)}
    `;
    rand.addEventListener("click", () => nav.mergi(p.titlu, (c) => p.fn(c, nav)));  // titlul = pasul; firma e in antet (fisa) sau in intro (drum cabinet) - DS cap.1
    lista.appendChild(rand);
  });
  // [drepturi_rol 04.10.2026] Niciun pas permis (asistent fără „Poate pregăti”): ecranul spune DE CE e gol și cine dă
  // dreptul, în loc de „Alege ce vrei să aduci” deasupra unei liste goale.
  if (!pasiVizibili.some((p) => permis(p.actiune || (STRATURI.find((s) => s.cheie === p.strat) || {}).actiune))) {
    lista.insertAdjacentHTML("afterend", `<p class="ecran-nota drept-motiv" id="mig-fara-drept">Importul datelor firmei cere dreptul «Poate pregăti», pe care nu-l ai. Îl acordă administratorul cabinetului, din ecranul Asistenți.</p>`);
  }
  _consumaMigMesaj(corp);
}

// [F150] Import retete HoReCa (pasul 11)
function importReteteFirma(corp, nav, firma) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>\u00cencarc\u0103 re\u021betarul: un r\u00e2nd per ingredient (re\u021bet\u0103 \u00b7 pre\u021b v\u00e2nzare \u00b7 ingredient \u00b7 cantitate/por\u021bie). Ingredientele se potrivesc pe articolele din stoc dup\u0103 denumire, deci <b>articolele se import\u0103 \u00eenaintea re\u021betelor</b> (pasul \u201eArticole \u0219i stoc ini\u021bial\u201d). Cantitatea pe por\u021bie e \u00een UM-ul articolului.</p>
    <button type="button" class="buton-secundar mig-model" id="mig-model">Descarcă model (CSV)</button>
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" data-actiune="POST /tenants/{tenant_id}/retete-import/incarca" accept=".csv,.txt,.tsv,.xlsx,.xls" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#0a807b" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">\u00cencarc\u0103 re\u021betele</div>
      <div class="mig-drop-desc">Excel (XLSX, XLS) sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  _existaPas(corp, firma, "retete");   // [lotul 13, 580 / 584] ce s-a adus deja și ce face importul cu ce există
  const fileInput = corp.querySelector("#mig-file");
  corp.querySelector("#mig-model")?.addEventListener("click", () => _descarcaModelCSV(MODELE.retete));
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    arataMesaj(eroare, "Se citesc re\u021betele\u2026", "info");
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const r = await fetch(`/tenants/${firma.tenant_id}/retete-import/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaRetete(corp, nav, firma, date);
    } catch (e) {
      arataMesaj(eroare, (e && e.mesaj) || "Eroare la citirea fi\u0219ierului.", "eroare");
    }
  });
}

function previzualizeazaRetete(corp, nav, firma, date) {
  latime(corp, true);
  const randuri = cuStari(date.randuri || [], date.erori);
  const rez = date.rezumat || {};
  // [comanda Costin 8.2 pct.4; 375] fiecare rând citit (un ingredient), cu starea lui; cantitatea pe porție se arată în UM-ul articolului
  const cant = (r) => (r.cantitate == null ? esc(r.cantitate_brut || "—") : `${cantitate(r.cantitate)}${r.articol_um ? " " + esc(r.articol_um) : ""}`);
  // [lotul 11, 424] previzualizarea ia corpul ferestrei, ca la celelalte importuri: sub zona de încărcare, rezumatul se lipea numai în
  // `#mig-preview`, iar intro-ul, modelul și zona de încărcare derulau deasupra lui (se derula toată fereastra, nu doar tabelul)
  const zona = corp;
  zona.innerHTML = _cadruPrev(`
    <div class="mig-intro-rand"><p class="mig-intro"><b>${esc(firma.nume)}</b> · rețete încărcate</p><div class="mig-coer">${bandaStari(randuri)}</div></div>
    <div class="mig-sold-rezumat"><b>${randuri.length}</b> ${dupaNumar(randuri.length, "rând citit", "rânduri citite")} · ${cate(rez.valide || 0, "rețetă intră", "rețete intră")} din ${rez.total || 0}</div>`,
    `
    ${_casetaFirma(date)}
    ` + tabelPrevizualizare([
      { titlu: "Rețeta", celula: (r) => esc(r.reteta || "—") },
      { titlu: "Preț vânzare", num: true, celula: (r) => (r.pret == null ? esc(r.pret_brut || "—") : `${bani(r.pret)} lei`) },
      { titlu: "Ingredient", celula: (r) => esc(r.ingredient || "—") },
      { titlu: "Articolul din stoc", celula: (r) => esc(r.articol_denumire || "—") },
      { titlu: "Cantitate pe porție", num: true, celula: cant },
    ], randuri),
    `<div class="mig-eroare" id="mig-eroare-ret"></div>
    <button class="buton-primar mig-buton" id="mig-importa" data-actiune="POST /tenants/{tenant_id}/retete-import">Importă rețetele</button>`);
  nav.setInapoi(() => nav.reiaPasul());   // [C140] „←” = alegerea fișierului, în pasul lui
  _arataFirma(zona, date, nav);   // [599]
  gateazaPartial(zona, "mig-importa", date.erori, randuri.length, "rețete");
  const b = zona.querySelector("#mig-importa");
  // [375] o rețetă intră întreagă: butonul numără rețetele, nu rândurile, și nu e activ la 0
  b.textContent = rez.valide ? `Importă ${cate(rez.valide, "rețetă", "rețete")}` : "Nicio rețetă nu poate intra";
  b.disabled = !rez.valide;
  const eroare = zona.querySelector("#mig-eroare-ret");
  b.addEventListener("click", () => _cuFirmaConfirmata(eroare, date, async () => {   // [599]
    b.disabled = true; b.textContent = "Import\u2026";
    try {
      const r = await api.post(`/tenants/${firma.tenant_id}/retete-import`, { randuri });
      const deja = ((r && r.sarite) || []).filter((x) => x.regula === "deja_exista").length;
      _migMesaj = _mesajSalvarePartiala(r, `${cate(r.create, "rețetă importată", "rețete importate")}.`
        + (deja ? ` ${cate(deja, "rețetă exista", "rețete existau")} deja (nedublate).` : ""));
      await _adaugaUrmatorii(firma); nav.inapoiPas();   // [664]
    } catch (e) {
      b.disabled = false; b.textContent = `Importă ${cate(rez.valide || 0, "rețetă", "rețete")}`;
      arataMesaj(eroare, (e && e.mesaj) || "Eroare la import.", "eroare");
    }
  }));
}

// [lotul 13, deficiența 668 — clasa 666: „observația «607 dedus din 371» repetată pe fiecare rând”] contul de cheltuială dedus din contul de
// stoc, o singură dată pe pereche, cu câte rânduri
function _notaDeduse(randuri) {
  const pe = {};
  randuri.filter((r) => r.cont_cheltuiala_dedus && r.stare !== "respins").forEach((r) => {
    const k = `${r.cont_stoc} → ${r.cont_cheltuiala}`;
    pe[k] = (pe[k] || 0) + 1;
  });
  const k = Object.keys(pe);
  return k.length ? `<p class="ecran-nota" id="mig-deduse">Contul de cheltuială lipsea din fișier și s-a dedus din contul de stoc: ${k.map((x) => `${esc(x)} (${cate(pe[x], "rând", "rânduri")})`).join(", ")}.</p>` : "";
}

// [F151] Import articole + stoc initial CV (pasul 10)
function importArticoleFirma(corp, nav, firma) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>\u00cencarc\u0103 nomenclatorul de articole cu stocul ini\u021bial (denumire \u00b7 UM \u00b7 cantitate \u00b7 pre\u021b unitar \u00b7 cont stoc \u00b7 op\u021bional cont cheltuial\u0103, dedus altfel din contul de stoc).</p>
    <button type="button" class="buton-secundar mig-model" id="mig-model">Descarcă model (CSV)</button>
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" data-actiune="POST /tenants/{tenant_id}/articole-import/incarca" accept=".csv,.txt,.tsv,.xlsx,.xls" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#0a807b" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">\u00cencarc\u0103 articolele</div>
      <div class="mig-drop-desc">Excel (XLSX, XLS) sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  _existaPas(corp, firma, "articole");   // [lotul 13, 580 / 584] ce s-a adus deja și ce face importul cu ce există
  const fileInput = corp.querySelector("#mig-file");
  corp.querySelector("#mig-model")?.addEventListener("click", () => _descarcaModelCSV(MODELE.articole));
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    arataMesaj(eroare, "Se citesc articolele\u2026", "info");
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const r = await fetch(`/tenants/${firma.tenant_id}/articole-import/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaArticole(corp, nav, firma, date);
    } catch (e) {
      arataMesaj(eroare, (e && e.mesaj) || "Eroare la citirea fi\u0219ierului.", "eroare");
    }
  });
}

function previzualizeazaArticole(corp, nav, firma, date) {
  latime(corp, true);
  // [lotul 13, 668 — clasa 666] pe rândul tabelului, motivul scurt al contului de stoc nepotrivit; cifrele lui, o dată (confruntarea, refuzurile)
  // (rândurile vin cu starea și motivele de la server, `articole_import_api.eticheteaza`: motivul se scurtează pe rând, nu în listă)
  const lungi = {};
  (date.erori || []).filter((e) => e.regula === "stoc_nu_da_soldul").forEach((e) => { lungi[e.mesaj] = e.cont || ""; });
  const randuri = cuStari(date.randuri || [], date.erori);
  randuri.forEach((r) => { r.motive = (r.motive || []).map((m) => (m in lungi
    ? `nu intră: contul ${lungi[m]} nu se potrivește cu soldul lui din balanță (cifrele, deasupra tabelului)` : m)); });
  const rez = date.rezumat || {};
  // [comanda Costin 8.2 pct.4; 373/374] fiecare rând citit (și cel fără denumire), cu starea lui; contul de stoc se vede, iar valoarea
  // pe fiecare cont de stoc se confruntă cu balanța de deschidere.
  const nr = (v, brut) => (v == null ? esc(brut || "—") : cantitate(v));
  // [lotul 11, 424] previzualizarea ia corpul ferestrei, ca la celelalte importuri: sub zona de încărcare, rezumatul se lipea numai în
  // `#mig-preview`, iar intro-ul, modelul și zona de încărcare derulau deasupra lui (se derula toată fereastra, nu doar tabelul)
  const zona = corp;
  zona.innerHTML = _cadruPrev(`
    <div class="mig-intro-rand"><p class="mig-intro"><b>${esc(firma.nume)}</b> · articole încărcate</p><div class="mig-coer">${bandaStari(randuri)}</div></div>
    <div class="mig-sold-rezumat"><b>${randuri.length}</b> ${dupaNumar(randuri.length, "rând citit", "rânduri citite")} · ${cate(rez.cu_stoc || 0, "articol cu stoc", "articole cu stoc")} · valoare <b>${bani(rez.valoare_totala || 0)}</b> lei${date.data_sold ? ` · stocul inițial la ${esc(dataRo(date.data_sold))}` : ""}</div>`,
    `
    ${_casetaFirma(date)}
    ` + // [581] confruntarea cu balanța în pagină; [668] contul de cheltuială dedus, spus o singură dată
    casetaReconciliere(date.reconciliere, date.data_sold, "stoc inițial", "conturile de stoc") + _notaDeduse(randuri) + tabelPrevizualizare([
      { titlu: "Denumire", celula: (r) => esc(r.denumire || "—") },
      { titlu: "UM", celula: (r) => esc(r.um || "—") },
      { titlu: "Cantitate", num: true, celula: (r) => nr(r.cantitate, r.cantitate_brut) },
      { titlu: "Preț unitar", num: true, celula: (r) => (r.pret == null ? esc(r.pret_brut || "—") : `${bani(r.pret)} lei`) },
      { titlu: "Valoare", num: true, celula: (r) => (r.valoare != null ? `${bani(r.valoare)} lei` : "—") },
      { titlu: "Cont stoc", celula: (r) => esc(r.cont_stoc || "—") },
      { titlu: "Cont cheltuială", celula: (r) => esc(r.cont_cheltuiala || "—") },
    ], randuri),
    `<div class="mig-eroare" id="mig-eroare-art"></div>
    <button class="buton-primar mig-buton" id="mig-importa" data-actiune="POST /tenants/{tenant_id}/articole-import">Importă articolele</button>`);
  nav.setInapoi(() => nav.reiaPasul());   // [C140] „←” = alegerea fișierului, în pasul lui
  _arataFirma(zona, date, nav);   // [599]
  gateazaPartial(zona, "mig-importa", date.erori, randuri.length, "articole");   // [373] butonul nu e activ când niciun rând nu intră
  zona.querySelector("#mig-importa").addEventListener("click", () => _cuFirmaConfirmata(zona.querySelector("#mig-eroare-art"), date, async () => {   // [599]
    const b = zona.querySelector("#mig-importa");
    const eroare = zona.querySelector("#mig-eroare-art");
    b.disabled = true; b.textContent = "Import\u2026";
    try {
      const r = await api.post(`/tenants/${firma.tenant_id}/articole-import`, { randuri, data_sold: date.data_sold || null });
      const deja = ((r && r.sarite) || []).filter((x) => x.regula === "deja_exista").length;
      _migMesaj = _mesajSalvarePartiala(r, `${cate(r.create, "articol importat", "articole importate")}.`
        + (deja ? ` ${cate(deja, "articol exista", "articole existau")} deja în nomenclator (nedublate).` : ""));
      await _adaugaUrmatorii(firma); nav.inapoiPas();   // [664]
    } catch (e) {
      b.disabled = false; b.textContent = "Importă articolele";
      arataMesaj(eroare, (e && e.mesaj) || "Eroare la import.", "eroare");
    }
  }));
}

// [p_pfa_rip 20.07] Import registru incasari-plati (RIP) \u2014 preluare PFA (partida simpla).
// Istoric cronologic al anului curent, NU balanta de deschidere. [372, comanda Costin 8.2] Doi pași, ca la celelalte importuri:
// previzualizarea (fiecare rând cu starea lui) și apoi salvarea rândurilor bune.
function importRipFirma(corp, nav, firma) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>\u00cencarc\u0103 registrul de \u00eencas\u0103ri-pl\u0103\u021bi (istoric cronologic: dat\u0103 \u00b7 tip \u00b7 explica\u021bie \u00b7 sum\u0103 \u00b7 categorie \u00b7 metod\u0103). Partida simpl\u0103 nu are balan\u021b\u0103 de deschidere \u2014 soldul rezult\u0103 din opera\u021biuni.</p>
    <button type="button" class="buton-secundar mig-model" id="mig-model">Descarcă model (CSV)</button>
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" data-actiune="POST /tenants/{tenant_id}/rip-import/incarca" accept=".csv,.txt,.tsv,.xlsx,.xls" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#16a34a" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">\u00cencarc\u0103 registrul</div>
      <div class="mig-drop-desc">Excel (XLSX, XLS) sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  _existaPas(corp, firma, "rip");   // [lotul 13, 580 / 584] ce s-a adus deja și ce face importul cu ce există
  const fileInput = corp.querySelector("#mig-file");
  corp.querySelector("#mig-model")?.addEventListener("click", () => _descarcaModelCSV(MODELE.rip));
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    arataMesaj(eroare, "Se citește registrul de \u00eencas\u0103ri-pl\u0103\u021bi\u2026", "info");
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const r = await fetch(`/tenants/${firma.tenant_id}/rip-import/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaRip(corp, nav, firma, date);
    } catch (e) {
      arataMesaj(eroare, (e && e.mesaj) || "Eroare la import.", "eroare");
    }
  });
}

function previzualizeazaRip(corp, nav, firma, date) {
  latime(corp, true);
  const randuri = cuStari(date.randuri || [], date.erori);
  const tip = (r) => (r.tip === "incasare" ? "încasare" : r.tip === "plata" ? "plată" : esc(r.tip_brut || "—"));
  const metoda = (r) => (r.metoda === "banca" ? "bancă" : r.metoda === "numerar" ? "numerar" : esc(r.metoda_brut || "—"));
  const coloane = [
    { titlu: "Data", celula: (r) => esc(dataRo(r.data) || r.data_brut || "—") },
    { titlu: "Tip", celula: tip },
    { titlu: "Explicație", celula: (r) => esc(r.explicatie || "—") },
    { titlu: "Suma", num: true, celula: (r) => (r.suma != null ? bani(r.suma) : esc(r.suma_brut || "—")) },
    { titlu: "Metoda", celula: metoda },
    { titlu: "Categoria", celula: (r) => esc(r.categorie || "—") },
    { titlu: "Document", celula: (r) => esc(r.document_numar || "—") },
  ];
  // [lotul 11, 424] previzualizarea ia corpul ferestrei, ca la celelalte importuri: sub zona de încărcare, rezumatul se lipea numai în
  // `#mig-preview`, iar intro-ul, modelul și zona de încărcare derulau deasupra lui (se derula toată fereastra, nu doar tabelul)
  const zona = corp;
  zona.innerHTML = _cadruPrev(`
    <div class="mig-intro-rand"><p class="mig-intro"><b>${esc(firma.nume)}</b> · registrul de încasări și plăți încărcat</p><div class="mig-coer">${bandaStari(randuri)}</div></div>
    <div class="mig-sold-rezumat"><b>${randuri.length}</b> ${dupaNumar(randuri.length, "rând citit", "rânduri citite")}</div>`,
    `
    ${_casetaFirma(date)}
    ` + tabelPrevizualizare(coloane, randuri),
    `<div class="mig-eroare" id="mig-eroare-rip"></div>
    <button class="buton-primar mig-buton" id="mig-salveaza-rip" data-actiune="POST /tenants/{tenant_id}/rip-import">Salvează registrul</button>`);
  nav.setInapoi(() => nav.reiaPasul());   // [C140] „←” = alegerea fișierului, în pasul lui
  _arataFirma(zona, date, nav);   // [599]
  gateazaPartial(zona, "mig-salveaza-rip", date.erori, randuri.length, "operațiuni");

  zona.querySelector("#mig-salveaza-rip").addEventListener("click", () => _cuFirmaConfirmata(zona.querySelector("#mig-eroare-rip"), date, async () => {   // [599]
    const eroare = zona.querySelector("#mig-eroare-rip");
    const buton = zona.querySelector("#mig-salveaza-rip");
    eroare.textContent = "";
    buton.disabled = true; buton.textContent = "Salvez…";
    try {
      const rez = await api.post(`/tenants/${firma.tenant_id}/rip-import`, { randuri });
      const n = (rez && rez.importate) || 0, dubluri = (rez && rez.sarite_duplicat) || 0;
      _migMesaj = _mesajSalvarePartiala(rez, `${n === 1 ? "O operațiune importată" : cate(n, "operațiune importată", "operațiuni importate")}.`
        + (dubluri ? ` ${cate(dubluri, "operațiune era", "operațiuni erau")} deja în registru (sărite).` : ""));
      await _adaugaUrmatorii(firma); nav.inapoiPas();   // [664]
    } catch (e) {
      arataMesaj(eroare, (e && e.mesaj) || "Eroare la salvare.", "eroare");
      buton.disabled = false; buton.textContent = "Salvează registrul";
    }
  }));
}
