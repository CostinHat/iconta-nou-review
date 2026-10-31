// ansamblu.js — Prezentarea de ANSAMBLU a aplicatiei.
// O intrare:
//   - semnul "?" GENERAL din bara de stare (.nav-ghid) -> oricand;
//   - [lotul 13, 562] pagina de BUN-VENIT care se deschidea singură la prima logare a fost scoasă: nimic nu se deschide singur.
// Continut DERIVAT, nu scris separat:
//   - firul de intrare = STRATURI (migrare.js): pasii de migrare, in ordine, migrarea prima;
//   - ansamblul = grupele din registru (/ansamblu, SURSA UNICA genereaza_grupe_functii.repartizeaza)
//     + coloana `ajutor` (semn "?" contextual pe functionalitatile care au ajutor scris).
//
// [drepturi_rol 04.10.2026, comanda Costin pct.5] Ghidul arată DOAR pașii permiși rolului: fiecare pas din
// STRATURI poartă ruta care îl face, iar `permis` (drepturi.js) răspunde din ce refuză serverul — aceeași sursă
// ca butoanele. Asistentului fără firme i se spune asta, nu i se arată un fir pe care nu-l poate parcurge.
// [pct.7] Termenul de rezolvare („se rezolvă în maximum 48 de ore”) a ieșit din fraza despre Suport: nu e un angajament
// decis (Costin). Fraza rămâne, fără termen.
import { api, esc, semnAjutor, inchidereDialog, cate } from "../api.js?v=7036a2d894";
import { STRATURI } from "./migrare.js?v=6d8714b398";
import { permis } from "../drepturi.js?v=34d0fb0afd";
import { sesiune } from "../sesiune.js?v=898215e0ee";
import { siraCarduri } from "../carduri.js?v=98c15a1738";

// [deficiența 230, comanda Costin 12.10.2026] numărul pasului e poziția lui în firul AFIȘAT, nu `nr` din STRATURI: pentru asistent
// pasul „Firme” e al administratorului și lipsește, iar firul începea de la „2”.
function _firHTML(pasi) {
  return pasi.map((st, i) =>
    `<li class="ans-pas"><span class="ans-pas-nr">${i + 1}</span>` +
    `<span class="ans-pas-txt"><b class="ans-pas-titlu">${esc(st.titlu)}</b>` +
    `<span class="ans-pas-desc">${esc(st.desc)}</span></span></li>`
  ).join("");
}

function _grupeHTML(grupe) {
  return grupe.map((gr) => {
    const li = gr.functii.map((f) =>
      `<li${f.actiune ? ` data-actiune="${esc(f.actiune)}"` : ""}>${esc(f.nume)}${f.are_ajutor && f.id ? " " + semnAjutor(f.id) : ""}</li>`
    ).join("");
    return `<div class="ans-grupa"><h4 class="ans-grupa-titlu">${esc(gr.titlu)}` +
      `<span class="ans-grupa-nr">${gr.functii.length}</span></h4>` +
      `<ul class="ans-grupa-lista">${li}</ul></div>`;
  }).join("");
}

// Firul de intrare al administratorului cabinetului ([562] asistentul nu-l mai primește: pașii de preluare sunt ai administratorului;
// administratorul are toate drepturile cabinetului, deci pașii lui nu sunt niciodată goi).
function _sectiuneFir(pasi) {
  return `<section class="ans-sectiune">` +
    `<h3 class="ans-sec-titlu">Firul de intrare — pașii, în ordine</h3>` +
    `<p class="ans-fir-unde">Fiecare pas se face pentru firma respectivă, din cardul „Import date” al firmei (ecranul Firme → firma → Import date). Excepție: „Vector fiscal” se completează în ecranul „Date firmă”.</p>` +
    // [270 e, comanda Costin 15.10.2026] rândul cerut, verbatim; numai unde există pași permiși (fără „Poate pregăti” nu e de unde începe)
    `<p class="ans-fir-unde" id="ans-alta-aplicatie">Vii din altă aplicație? Începe din Firme → Migrare cabinet.</p>` +
    `<ol class="ans-fir">${_firHTML(pasi)}</ol>` +
  `</section>`;
}

// [deficiența 289c, comanda Costin 16.10.2026, textul verbatim] conectarea SPV e a cabinetului, o singură dată — nu un pas al fiecărei
// firme, deci stă înaintea firului de intrare; o face administratorul cabinetului (asistentul n-are ecranul „Conectare SPV”)
export const PAS_CONECTARE_SPV = "Conectează cabinetul la SPV: Setări cont → Conectare SPV. Te autentifici o singură dată cu certificatul "
  + "digital; conexiunea acoperă toate firmele pentru care ai împuternicire la ANAF. Fără acest pas facturile nu pleacă în SPV și nici "
  + "cele de la furnizori nu vin automat.";

function _sectiuneSpv() {
  return `<section class="ans-sectiune" id="ans-spv">` +
    `<h3 class="ans-sec-titlu">Primul pas al cabinetului</h3>` +
    `<p class="ans-fir-unde">${esc(PAS_CONECTARE_SPV)}</p>` +
  `</section>`;
}

// [lotul 13, deficiența 562 — anexa comenzii 13.1: „La prima intrare a asistentului junior (doar «Poate pregăti»), fereastra se deschide
// singură (contrar regulii: nimic nu se deschide fără să fie ales) și îi arată pașii de administrator (vector fiscal, solduri inițiale,
// asociați, migrare cabinet). […] Fereastra încalcă 320: ghidul de început rămâne în butonul de ajutor (?), nu se deschide singur, și e
// pe rol.”] (1) Prezentarea NU se mai deschide singură la prima logare (pentru niciun rol — CLAUDE.md §9: „Nimic nu se deschide singur”);
// o deschide omul din „?”. (2) Pe rol: asistentul nu mai primește firul de preluare (pașii administratorului); primește ce i se potrivește
// — firmele lui și ce are voie (cardurile lui de început, ca pagina „Primii pași”), plus catalogul filtrat pe drepturi.
async function _corpAnsamblu(corp) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă prezentarea…</p>`;
  const asistent = sesiune.rol() === "angajat";
  let grupe = [];
  let nrFirme = null;
  try { const d = await api.get("/ansamblu"); grupe = (d && d.grupe) || []; }
  catch (_e) { grupe = []; }
  if (asistent) {
    try { const r = await api.get("/tenants"); nrFirme = ((r && r.tenants) || []).length; }
    catch (_e) { nrFirme = null; }   // necunoscut ≠ zero: fără listă nu afirmăm „nu ai firme”
  }
  const pasi = STRATURI.filter((st) => permis(st.actiune));
  const faraFirme = asistent && nrFirme === 0;
  const intro = asistent
    ? `<p class="ans-intro">Bun venit în iConta.eu. Lucrezi pe firmele pe care ți le alocă administratorul cabinetului; ce ai voie să faci pe ele stabilește tot el, în ecranul Asistenți. Mai jos sunt pașii tăi de început și ce cuprinde aplicația, după drepturile tale.</p>`
    : `<p class="ans-intro">Bun venit în iConta.eu. Mai jos e drumul de la preluarea unei firme până la operarea curentă — parcurge-l în ordine, începând cu migrarea. E o hartă a aplicației; n-o reține acum, o ai oricând la îndemână.</p>`;
  // [lotul 14, 687] fereastra încape pe un ecran: explicațiile (conectarea SPV, firul de intrare) sunt carduri-rezumat, deschise la clic
  // în fereastra lor (aceleași elemente, aceleași id-uri); numai catalogul de funcții derulează, în zona lui.
  const carduri = [];
  if (!asistent) carduri.push({ id: "ans-card-spv", ton: "info", text: "Primul pas al cabinetului: conectarea la SPV", titlu: "Primul pas al cabinetului",
    deschide: (c) => { c.innerHTML = `<div class="ans-continut">${_sectiuneSpv()}</div>`; } });
  if (!asistent && !faraFirme) carduri.push({ id: "ans-card-fir", ton: "info", text: `Firul de intrare: ${cate(pasi.length, "pas", "pași")}, în ordine`, titlu: "Firul de intrare",
    deschide: (c) => { c.innerHTML = `<div class="ans-continut">${_sectiuneFir(pasi)}</div>`; } });
  carduri.push({ id: "ans-card-inceput", ton: "info", text: "Primii pași în aplicație", titlu: "Primii pași",
    deschide: (c) => {
      c.innerHTML = `<div class="ans-continut"><section class="ans-sec" id="ans-inceput"></section></div>`;
      import("./inceput.js?v=9a8b26bf4b").then((m) => m.ghidulDeInceput(c.querySelector("#ans-inceput"))).catch(() => {});
    } });
  corp.innerHTML =
    `<div class="ans-continut">` +
      intro +
      `<p class="ans-intro">Orice solicitare de funcționalitate nouă sau modificare a celor existente se raportează din „Suport”, sus pe pagina principală, lângă „Recomandă”.</p>`   /* [deficiența 225, 12.10.2026] bandă, nu card */ +
      `<div id="ans-carduri"></div>` +
      (faraFirme
        ? `<p class="msg-avert ans-fara-firme" role="status">Nu ai firme asociate. Cere administratorului cabinetului să ți le aloce, din ecranul Asistenți.</p>`
        : "") +
      // [deficiența 320] „ghidul de început rămâne în butonul de ajutor (?)”: cardurile de început ale omului, de citit, cu starea lor
      // (acum în cardul „Primii pași în aplicație”)
      `<section class="ans-sectiune">` +
        `<h3 class="ans-sec-titlu">Ce cuprinde aplicația</h3>` +
        `<div data-zona-derulare><div class="ans-grupe">${grupe.length ? _grupeHTML(grupe) : '<p class="ecran-nota">—</p>'}</div>` +
      `<p class="ans-inchidere">` +
        `Semnul <span class="ans-mostra ans-mostra--general">?</span> din bara de sus redeschide oricând această prezentare de ansamblu. ` +
        `Semnele <span class="ans-mostra ans-mostra--contextual">?</span> de pe ecrane explică fiecare funcționalitate în parte.` +
      `</p></div>` +
      `</section>` +
    `</div>`;
  if (carduri.length) siraCarduri(corp.querySelector("#ans-carduri"), carduri, window._navGlobal);
  else corp.querySelector("#ans-carduri").remove();
}

// semnul "?" GENERAL din bara de stare -> modalul de ansamblu (oricand)
// [deficiența 4, retestul Costin 09.10] fereastra se închide și cu Esc, prin mecanismul unic al dialogurilor (`inchidereDialog`):
// e o fereastră de citit, fără nimic de pierdut; X-ul ei rămâne cel al navigatorului
// [lotul 13, 562] singurul drum spre prezentare (nu se mai deschide singură la prima logare); prima deschidere o marchează văzută
export function deschideAnsamblu() {
  if (!window._navGlobal) return;
  window._navGlobal.deschide("Prezentarea aplicației", (corp) => { _corpAnsamblu(corp); }, { nivel: "cabinet", lat: "larg" });   // [200] o hartă: lată, ca grupele să stea pe coloane
  const fer = [...document.querySelectorAll(".fereastra")].pop();
  if (fer) inchidereDialog(fer, () => { if (fer.isConnected) window._navGlobal.inapoi(); });
  const u = sesiune.user();
  if (u && u.bun_venit_vazut === false) {
    api.post("/cont/bun-venit-vazut", {}).then(() => sesiune.marcheazaBunVenit()).catch(() => {});
  }
}
