// ansamblu.js — Prezentarea de ANSAMBLU a aplicatiei.
// Doua intrari, acelasi continut:
//   - semnul "?" GENERAL din bara de stare (.nav-ghid) -> oricand;
//   - pagina de BUN-VENIT (overlay) -> o singura data, la prima logare.
// Continut DERIVAT, nu scris separat:
//   - firul de intrare = STRATURI (migrare.js): pasii de migrare, in ordine, migrarea prima;
//   - ansamblul = grupele din registru (/ansamblu, SURSA UNICA genereaza_grupe_functii.repartizeaza)
//     + coloana `ajutor` (semn "?" contextual pe functionalitatile care au ajutor scris).
import { api, esc, semnAjutor } from "../api.js";
import { STRATURI } from "./migrare.js?v=6";

function _firHTML() {
  return STRATURI.map((st) =>
    `<li class="ans-pas"><span class="ans-pas-nr">${st.nr}</span>` +
    `<span class="ans-pas-txt"><b>${esc(st.titlu)}</b> — ${esc(st.desc)}</span></li>`
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

async function _corpAnsamblu(corp, primaLogare) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă prezentarea…</p>`;
  let grupe = [];
  try { const d = await api.get("/ansamblu"); grupe = (d && d.grupe) || []; }
  catch (_e) { grupe = []; }
  corp.innerHTML =
    `<div class="ans-continut">` +
      `<p class="ans-intro">Orice solicitare de funcționalitate nouă sau modificare a celor existente se raportează prin cardul Suport și se rezolvă în maximum 48 de ore.</p>` +
      (primaLogare
        ? `<p class="ans-intro">Bun venit în iConta.eu. Mai jos e drumul de la preluarea unei firme până la operarea curentă — parcurge-l în ordine, începând cu migrarea. E o hartă a aplicației; n-o reține acum, o ai oricând la îndemână.</p>`
        : "") +
      `<section class="ans-sectiune">` +
        `<h3 class="ans-sec-titlu">Firul de intrare — pașii, în ordine</h3>` +
        `<ol class="ans-fir">${_firHTML()}</ol>` +
      `</section>` +
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

// pagina de BUN-VENIT (o data, la prima logare) — overlay peste desktop, inainte de operare
export function ecranBunVenit(radacina, laInchidere) {
  const ov = document.createElement("div");
  ov.className = "bun-venit-overlay";
  ov.innerHTML = `<div class="bun-venit-box"><div class="bun-venit-antet">iConta.eu · bun venit</div>` +
                 `<div class="bun-venit-corp"></div></div>`;
  radacina.appendChild(ov);
  const corp = ov.querySelector(".bun-venit-corp");
  _corpAnsamblu(corp, true).then(() => {
    const b = ov.querySelector("#ans-intra");
    if (b) b.addEventListener("click", () => { ov.remove(); if (laInchidere) laInchidere(); });
  });
}
