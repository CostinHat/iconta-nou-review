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
import { api, esc, semnAjutor, inchidereDialog } from "../api.js?v=91e1c0701a";
import { STRATURI } from "./migrare.js?v=b059f0d009";
import { permis } from "../drepturi.js?v=df020d220f";
import { sesiune } from "../sesiune.js?v=5d142951c9";

function _firHTML(pasi) {
  return pasi.map((st) =>
    `<li class="ans-pas"><span class="ans-pas-nr">${st.nr}</span>` +
    `<span class="ans-pas-txt"><b class="ans-pas-titlu">${esc(st.titlu)}</b>` +
    `<span class="ans-pas-desc">${esc(st.desc)}</span></span></li>`
  ).join("");
}

function _grupeHTML(grupe) {
  return grupe.map((gr) => {
    const li = gr.functii.map((f) =>
      `<li>${esc(f.nume)}${f.are_ajutor && f.id ? " " + semnAjutor(f.id) : ""}</li>`
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
    `<ol class="ans-fir">${_firHTML(pasi)}</ol>` +
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
      `<p class="ans-intro">Orice solicitare de funcționalitate nouă sau modificare a celor existente se raportează prin cardul Suport.</p>` +
      (faraFirme
        ? `<p class="msg-avert ans-fara-firme" role="status">Nu ai firme asociate. Cere administratorului cabinetului să ți le aloce, din ecranul Asistenți.</p>`
        : _sectiuneFir(asistent, pasi)) +
      `<section class="ans-sectiune">` +
        `<h3 class="ans-sec-titlu">Ce cuprinde aplicația</h3>` +
        `<div class="ans-grupe">${grupe.length ? _grupeHTML(grupe) : '<p class="ecran-nota">—</p>'}</div>` +
      `</section>` +
      `<p class="ans-inchidere">` +
        `Semnul <span class="ans-mostra ans-mostra--general">?</span> din bara de sus redeschide oricând această prezentare de ansamblu. ` +
        `Semnele <span class="ans-mostra ans-mostra--contextual">?</span> de pe ecrane explică fiecare funcționalitate în parte.` +
      `</p>` +
      (primaLogare
        ? `<div class="ans-actiuni"><button type="button" class="buton-primar" id="ans-intra">Am înțeles, intru în aplicație</button></div>`
        : "") +
    `</div>`;
}

// semnul "?" GENERAL din bara de stare -> modalul de ansamblu (oricand)
export function deschideAnsamblu() {
  if (!window._navGlobal) return;
  window._navGlobal.deschide("Prezentarea aplicației", (corp) => { _corpAnsamblu(corp, false); }, { nivel: "cabinet" });
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
