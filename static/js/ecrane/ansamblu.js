// ansamblu.js — Prezentarea de ANSAMBLU a aplicatiei.
// Doua intrari, acelasi continut:
//   - semnul "?" GENERAL din bara de stare (.nav-ghid) -> oricand;
//   - pagina de BUN-VENIT (overlay) -> o singura data, la prima logare.
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
import { api, esc, semnAjutor, inchidereDialog } from "../api.js?v=158edee964";
import { STRATURI } from "./migrare.js?v=374541fcbc";
import { permis } from "../drepturi.js?v=34d0fb0afd";
import { sesiune } from "../sesiune.js?v=898215e0ee";

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

// Firul de intrare, după rol. Pentru asistent pasul „Firme” (adăugarea) e al administratorului, deci firul lui
// începe de la datele unei firme deja adăugate; fără „Poate pregăti” nu are niciun pas.
function _sectiuneFir(asistent, pasi) {
  if (!pasi.length) {
    return `<section class="ans-sectiune">` +
      `<h3 class="ans-sec-titlu">Firul de intrare</h3>` +
      `<p class="ans-fir-unde">Preluarea datelor unei firme (Import date) cere dreptul «Poate pregăti», pe care nu-l ai. ` +
      `Îl acordă administratorul cabinetului, din ecranul Asistenți. Până atunci poți urmări firmele alocate în Control fiscal și Termene.</p>` +
    `</section>`;
  }
  return `<section class="ans-sectiune">` +
    `<h3 class="ans-sec-titlu">Firul de intrare — pașii, în ordine</h3>` +
    `<p class="ans-fir-unde">Fiecare pas se face pentru firma respectivă, din cardul „Import date” al firmei (ecranul Firme → firma → Import date). Excepție: „Vector fiscal” se completează în ecranul „Date firmă”.` +
    (asistent ? ` Firma o adaugă în portofoliu administratorul cabinetului; tu preiei datele firmelor care ți-au fost alocate.` : "") +
    `</p>` +
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

async function _corpAnsamblu(corp, primaLogare) {
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
    ? `<p class="ans-intro">Bun venit în iConta.eu. Lucrezi pe firmele pe care ți le alocă administratorul cabinetului. Mai jos e ce poți face cu drepturile tale. E o hartă a aplicației; n-o reține acum, o ai oricând la îndemână.</p>`
    : `<p class="ans-intro">Bun venit în iConta.eu. Mai jos e drumul de la preluarea unei firme până la operarea curentă — parcurge-l în ordine, începând cu migrarea. E o hartă a aplicației; n-o reține acum, o ai oricând la îndemână.</p>`;
  corp.innerHTML =
    `<div class="ans-continut">` +
      (primaLogare ? intro : "") +
      `<p class="ans-intro">Orice solicitare de funcționalitate nouă sau modificare a celor existente se raportează din „Suport”, sus pe pagina principală, lângă „Recomandă”.</p>`   /* [deficiența 225, 12.10.2026] bandă, nu card */ +
      (asistent ? "" : _sectiuneSpv()) +
      (faraFirme
        ? `<p class="msg-avert ans-fara-firme" role="status">Nu ai firme asociate. Cere administratorului cabinetului să ți le aloce, din ecranul Asistenți.</p>`
        : _sectiuneFir(asistent, pasi)) +
      `<section class="ans-sectiune">` +
        `<h3 class="ans-sec-titlu">Ce cuprinde aplicația</h3>` +
        `<div class="ans-grupe">${grupe.length ? _grupeHTML(grupe) : '<p class="ecran-nota">—</p>'}</div>` +
      `</section>` +
      // [deficiența 320] „ghidul de început rămâne în butonul de ajutor (?)”: cardurile de început ale omului, de citit, cu starea lor
      `<section class="ans-sec" id="ans-inceput"></section>` +
      `<p class="ans-inchidere">` +
        `Semnul <span class="ans-mostra ans-mostra--general">?</span> din bara de sus redeschide oricând această prezentare de ansamblu. ` +
        `Semnele <span class="ans-mostra ans-mostra--contextual">?</span> de pe ecrane explică fiecare funcționalitate în parte.` +
      `</p>` +
      (primaLogare
        ? `<div class="ans-actiuni"><button type="button" class="buton-primar" id="ans-intra">Am înțeles, intru în aplicație</button></div>`
        : "") +
    `</div>`;
  import("./inceput.js?v=cf800c466e").then((m) => m.ghidulDeInceput(corp.querySelector("#ans-inceput"))).catch(() => {});
}

// semnul "?" GENERAL din bara de stare -> modalul de ansamblu (oricand)
// [deficiența 4, retestul Costin 09.10] fereastra se închide și cu Esc, prin mecanismul unic al dialogurilor (`inchidereDialog`):
// e o fereastră de citit, fără nimic de pierdut; X-ul ei rămâne cel al navigatorului
export function deschideAnsamblu() {
  if (!window._navGlobal) return;
  window._navGlobal.deschide("Prezentarea aplicației", (corp) => { _corpAnsamblu(corp, false); }, { nivel: "cabinet", lat: "larg" });   // [200] o hartă: lată, ca grupele să stea pe coloane
  const fer = [...document.querySelectorAll(".fereastra")].pop();
  if (fer) inchidereDialog(fer, () => { if (fer.isConnected) window._navGlobal.inapoi(); });
}

// pagina de BUN-VENIT (o data, la prima logare) — overlay peste desktop, inainte de operare.
// [dialog_inchidere 04.10.2026, comanda Costin pct.4] Se închide din X-ul din antet, cu Esc sau din butonul de la
// capăt — toate trei prin ACELAȘI `inchide`, deci toate marchează bun-venitul ca văzut (altfel X ar fi o ușă
// care-l face să reapară la fiecare intrare).
export function ecranBunVenit(radacina, laInchidere) {
  const ov = document.createElement("div");
  ov.className = "bun-venit-overlay";
  ov.setAttribute("role", "dialog");
  ov.setAttribute("aria-modal", "true");
  ov.setAttribute("aria-label", "Bun venit în iConta.eu");
  ov.dataset.deschidere = "aplicatie";   // [325] deschisă de aplicație, la prima logare (decizie), nu de un clic
  ov.innerHTML = `<div class="bun-venit-box"><div class="bun-venit-antet"><span class="bun-venit-titlu">iConta.eu · bun venit</span></div>` +
                 `<div class="bun-venit-corp"></div></div>`;
  radacina.appendChild(ov);
  const inchide = inchidereDialog(ov, () => { ov.remove(); if (laInchidere) laInchidere(); },
                                  ov.querySelector(".bun-venit-antet"));
  const corp = ov.querySelector(".bun-venit-corp");
  _corpAnsamblu(corp, true).then(() => {
    const b = ov.querySelector("#ans-intra");
    if (b) b.addEventListener("click", inchide);
  });
}
