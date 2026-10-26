// supervizor.js — ecranul SUPERVIZORULUI: constatările deschise pe firmele mele.
//
// [01.09.2026, Costin, verbatim] „Ce vede contabilul: constatările deschise pe firmele lui, cu
// temei, în ecran propriu. Clopoțelul rămâne roșu agregat, nu o notificare pe constatare."
//
// «CONSTATĂRI DESCHISE» = ce a produs ultima rulare a lucrătorului (P1: rezultatul persistat, `supervizor_cache`, recalculat de
// `firma_rezumat.main` la 5 minute pe firmele schimbate — deficiența 484: lucrătorul nu era chemat de nimeni). Ecranul CITEȘTE; fără
// ciclu de viață. Un ciclu de viață (apărut la · încă deschisă · rămas netratat) își capătă contractul când va avea consumator.
//
// CE NU FACE, și e cerut explicit: nu împinge nimic în clopoțel. Clopoțelul e cablat deja, prin
// verifica_d390 -> alerte_control_fiscal, AGREGAT PE FIRMĂ. Un push de aici ar fi al doilea mecanism.
//
// RENDERER-UL UNEI CONSTATĂRI E ÎMPRUMUTAT din control_verdict.js (randA), nu rescris: două randări
// ale aceleiași anatomii ar diverge, iar TEMEIUL e chiar partea care s-ar pierde prima.
//
// CELE TREI REZULTATE NU SE TOPESC ÎNTR-UNUL. «Zero constatări» nu înseamnă «totul e verde»: poate
// însemna că n-a fost ce compara, sau că verificarea n-a rulat deloc. Ecranul le ține despărțite,
// fiindcă exact aici se naște cifra validă și falsă.

import { api, esc, dupaNumar, dataRo } from "../api.js?v=9bcf50c899";
import { randA as randConstatare } from "./control_verdict.js?v=3dc9eca249";

function perioada(r) {
  return dataRo(new Date(r.an, r.luna - 1, 1), "luna_an_numeric");   // DS cap.4: „10/2026”, din formatorul unic
}

function antet(r) {
  const z = r.rezumat || {};
  return `<div class="sv-antet">
    <div class="sv-cifre">
      <span class="sv-cifra"><b>${z.constatari_total || 0}</b> ${dupaNumar(z.constatari_total || 0, "constatare", "constatări")} pe <b>${z.CONSTATARI || 0}</b> ${dupaNumar(z.CONSTATARI || 0, "firmă", "firme")}</span>
      <span class="sv-cifra sv-cifra--sec"><b>${z.FARA_SUBIECT || 0}</b> fără subiect</span>
      <span class="sv-cifra sv-cifra--rau"><b>${z.NEVERIFICAT || 0}</b> ${dupaNumar(z.NEVERIFICAT || 0, "neverificată", "neverificate")}</span>
      <span class="sv-cifra sv-cifra--sec">din <b>${z.firme_in_domeniu || 0}</b> ${dupaNumar(z.firme_in_domeniu || 0, "firmă", "firme")}</span>
    </div>
    <div class="cf-incr-temei">Perioada evaluată: ${esc(perioada(r))}. Domeniu: ${esc(r.domeniu || "")}</div>
    <div class="cf-incr-temei">Confruntare între declarații, pe ultima lună încheiată. Se recalculează în câteva minute după
      fiecare schimbare a datelor firmei. Supervizorul <b>nu blochează</b> nimic.</div>
  </div>`;
}

// [lotul 12, C147] rezultatul calculat înaintea ultimei schimbări (a datelor firmei sau a regulilor de verificare) se arată, dar
// ETICHETAT (`uc_supervizor`: „se arată, dar etichetat”) — până azi arăta ca unul curent până la tura următoare
function etichetaVechi(f) {
  const p = f.prospetime || {};
  if (p.stare !== "invalidat") return "";
  return `<div class="cf-incr-temei" data-prospetime="invalidat">Rezultat calculat${p.calculat_la ? " la " + esc(dataRo(p.calculat_la, "cu_ora")) : ""}, înaintea ultimei schimbări a datelor firmei sau a regulilor de verificare: se recalculează în câteva minute.</div>`;
}

function blocFirma(f) {
  const cs = (f.constatari || []).map(randConstatare).join("");
  return `<section class="sv-firma">
    <h3 class="sv-firma-nume">${esc(f.nume || "Firmă")}</h3>
    ${etichetaVechi(f)}
    ${cs}
  </section>`;
}

function blocNeverificate(firme) {
  if (!firme.length) return "";
  const randuri = firme.map((f) => `<div class="cf-incr-rand">
      <div class="cf-incr-cap"><span class="cf-dot" style="background:var(--gri-dot, #9aa0a6)"></span>
        <span>${esc(f.nume || "Firmă")}</span></div>
      <div class="cf-incr-temei">${esc((f.neverificat && f.neverificat.eroare) || "")}</div>
      ${etichetaVechi(f)}
    </div>`).join("");
  return `<section class="sv-firma sv-firma--neverif">
    <h3 class="sv-firma-nume">Firme pe care verificarea nu a rulat</h3>
    <div class="cf-incr-temei">Nu înseamnă «e în regulă» — înseamnă că nu s-a putut verifica.
      Cât timp cauza de mai jos rămâne, firmele astea nu sunt acoperite de nicio confruntare.</div>
    ${randuri}
  </section>`;
}

function blocGol(r) {
  const z = r.rezumat || {};
  const fs = z.FARA_SUBIECT || 0;
  const nv = z.NEVERIFICAT || 0;
  let text;
  if (nv && !fs) {
    text = "Nicio constatare — dar nu fiindcă e curat: verificarea n-a rulat pe niciuna dintre firme.";
  } else if (fs && !nv) {
    text = "Nicio constatare, fiindcă n-a fost ce compara. Confruntarea are nevoie de o declarație "
         + "depusă prin aplicație, cu rândurile păstrate; până atunci nu afirmă nimic despre firme.";
  } else if (fs && nv) {
    text = "Nicio constatare: pe unele firme n-a fost ce compara, pe altele verificarea n-a rulat. "
         + "Nici una dintre situații nu înseamnă «e în regulă».";
  } else {
    text = "Nicio firmă în domeniu.";
  }
  return `<div class="stare-goala">${esc(text)}</div>`;
}

export async function randeazaSupervizor(corp, nav) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă confruntarea…</p>`;
  let r;
  try {
    r = await api.get("/supervizor");
  } catch (e) {
    // Eroarea de încărcare merge la `.ecran-nota`, NU la starea de conținut gol (DS cap.6):
    // aceea e o listă cu zero rânduri, care spune ce lipsește și pe unde se iese. Aici n-am
    // aflat nimic, deci n-am cum să afirm că e gol. Verificatorul păzește exact confuzia asta.
    corp.innerHTML = `<p class="ecran-nota">Nu s-a putut rula supervizorul: `
      + `${esc((e && e.mesaj) || "eroare necunoscută")}. Constatările nu sunt «zero», ci necunoscute.</p>`;
    return;
  }
  const firme = r.firme || [];
  const cuConstatari = firme.filter((f) => (f.constatari || []).length);
  const neverificate = firme.filter((f) => f.rezultat === "NEVERIFICAT");
  const corpuri = cuConstatari.map(blocFirma).join("");
  corp.innerHTML = antet(r)
    + (corpuri || blocGol(r))
    + blocNeverificate(neverificate);
}
