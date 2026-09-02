// supervizor.js — ecranul SUPERVIZORULUI: constatările deschise pe firmele mele.
//
// [01.09.2026, Costin, verbatim] „Ce vede contabilul: constatările deschise pe firmele lui, cu
// temei, în ecran propriu. Clopoțelul rămâne roșu agregat, nu o notificare pe constatare."
//
// «CONSTATĂRI DESCHISE» = ce produce rularea CURENTĂ. Ecranul recalculează la fiecare deschidere,
// exact ca /control-fiscal — fără tabel propriu și fără ciclu de viață. Un ciclu de viață (apărut
// la · încă deschisă · rămas netratat) își capătă contractul când va avea consumator — stratul
// asistentului și urmărirea performanței —, nu înainte.
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

import { api, esc } from "../api.js?v=5b2978a5b9";
import { randA as randConstatare } from "./control_verdict.js?v=f019079e5a";

function perioada(r) {
  return `${String(r.luna).padStart(2, "0")}/${r.an}`;
}

function antet(r) {
  const z = r.rezumat || {};
  return `<div class="sv-antet">
    <div class="sv-cifre">
      <span class="sv-cifra"><b>${z.constatari_total || 0}</b> constatări pe <b>${z.CONSTATARI || 0}</b> firme</span>
      <span class="sv-cifra sv-cifra--sec"><b>${z.FARA_SUBIECT || 0}</b> fără subiect</span>
      <span class="sv-cifra sv-cifra--rau"><b>${z.NEVERIFICAT || 0}</b> neverificate</span>
      <span class="sv-cifra sv-cifra--sec">din <b>${z.firme_in_domeniu || 0}</b> firme</span>
    </div>
    <div class="cf-incr-temei">Perioada evaluată: ${esc(perioada(r))}. Domeniu: ${esc(r.domeniu || "")}</div>
    <div class="cf-incr-temei">Confruntare între declarații (axa orizontală). Recalculată acum, la
      deschiderea ecranului — nu e o listă păstrată. Supervizorul <b>nu blochează</b> nimic.</div>
  </div>`;
}

function blocFirma(f) {
  const cs = (f.constatari || []).map(randConstatare).join("");
  return `<section class="sv-firma">
    <h3 class="sv-firma-nume">${esc(f.nume || "Firmă")}</h3>
    ${cs}
  </section>`;
}

function blocNeverificate(firme) {
  if (!firme.length) return "";
  const randuri = firme.map((f) => `<div class="cf-incr-rand">
      <div class="cf-incr-cap"><span class="cf-dot" style="background:var(--gri-dot, #9aa0a6)"></span>
        <span>${esc(f.nume || "Firmă")}</span></div>
      <div class="cf-incr-temei">${esc((f.neverificat && f.neverificat.eroare) || "")}</div>
    </div>`).join("");
  return `<section class="sv-firma sv-firma--neverif">
    <h3 class="sv-firma-nume">Firme pe care verificarea NU a rulat</h3>
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
  corp.innerHTML = `<p class="ecran-nota">Se rulează confruntarea…</p>`;
  let r;
  try {
    r = await api.get("/supervizor");
  } catch (e) {
    // Eroarea de încărcare merge la `.ecran-nota`, NU la starea de conținut gol (DS cap.6):
    // aceea e o listă cu zero rânduri, care spune ce lipsește și pe unde se iese. Aici n-am
    // aflat nimic, deci n-am cum să afirm că e gol. Verificatorul păzește exact confuzia asta.
    corp.innerHTML = `<p class="ecran-nota">Nu am putut rula supervizorul: `
      + `${esc((e && e.mesaj) || "eroare necunoscută")}. Constatările NU sunt «zero» — sunt `
      + `necunoscute.</p>`;
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
