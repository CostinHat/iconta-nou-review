// salut.js — partea de sus a paginii principale, ACEEAȘI la ambele roluri (contabilul-șef: cabinet.js; asistentul: asistent.js).
//
// [deficiențele 225 + 231, comanda Costin 12.10.2026, verbatim în DECIZII] „«Recomandă» și «Suport» sunt două benzi înguste, una lângă
// alta, deasupra cardurilor, la ambele roluri, ca la Cabinet.” · „Pagina principală are aceeași structură la ambele roluri.”
// Structura, la amândouă: banda de salut (titlul paginii + data, în stânga; cele două benzi, în dreapta), apoi grila de carduri —
// fără meniu lateral. Un singur loc o scrie (aici), deci cele două pagini nu mai pot diverge; gard `PAGINA_PRINCIPALA_UNA`
// (verificator) + `frontend_test/e2e/e2e_comanda_1210.py`.

import { api, dataRo, esc, ICOANE, CULORI_CARD } from "../api.js?v=158edee964";
import { randeazaRecomanda } from "./recomanda.js?v=62f148fa2b"; // [p31_recomanda]
import { randeazaRaporteaza } from "./raporteaza.js?v=ff0c5ffd8d"; // [p34_raporteaza]

function svg(nume, culoare) {
  return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="${culoare}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICOANE[nume] || ""}</svg>`;
}

//: cele două benzi, în ordine (DS cap.12: Recomandă = chihlimbar, Suport = ardezie)
const BENZI = [
  { cheie: "recomanda", titlu: "Recomandă", icon: "gift", culori: CULORI_CARD.chihlimbar, deschide: randeazaRecomanda },
  { cheie: "raport", titlu: "Suport", icon: "suport", culori: CULORI_CARD.ardezie, deschide: randeazaRaporteaza },
];

// [269, Lotul 5: „salutul ia ultimul cuvânt din nume («Salut, 253» pentru «Test 253»)”] Numele din salut, UN SINGUR LOC pentru toate
// saluturile (pagina principală a ambelor roluri, Panou Admin, mesajul de la logare): prenumele, DOAR dacă a fost scris separat
// (Setări › Profil are câmpuri separate); altfel numele întreg, așa cum e scris — niciodată „ultimul cuvânt” din nume. Gard
// `core/test_date_neescapate.py`: nimeni nu mai taie numele (`.split(" ")`) pentru salut.
export function numeDeSalut(u) {
  const x = u || {};
  return String(x.prenume || "").trim() || String(x.nume || "").trim();
}

// Banda de salut + grila (goală, de umplut de pagină). `u` = utilizatorul din sesiune; numele trece prin `esc` (C37: e text scris de om).
export function paginaPrincipala(u) {
  const nume = numeDeSalut(u);
  return `
    <div class="cab-salut">
      <div>
        <h1 class="cab-salut-nume">${nume ? "Salut, " + esc(nume) : "Salut"}</h1>
        <div class="cab-salut-data">Spațiul tău de lucru — ${dataRo(new Date(), "lung")}</div>
      </div>
      <div class="cab-benzi">${BENZI.map((b) => `
        <button type="button" class="cab-card cab-banda" data-banda="${b.cheie}" data-deschide="${b.cheie}" style="background:${b.culori.bg};color:${b.culori.fg}">
          ${svg(b.icon, b.culori.fg)}<span class="cab-card-titlu">${b.titlu}</span>
        </button>`).join("")}
      </div>
    </div>
    <div class="inceput" id="inceput-carduri" hidden></div>
    <div class="cab-grila"></div>`;
}

// Leagă benzile (`nivel` = nivelul ferestrei, ca la cardurile paginii) și ține la zi numărul sesizărilor necitite pe „Suport”.
export function legaBenzile(continut, nav, nivel) {
  // [deficiențele 319 + 320] cardurile de început, sub banda de salut, la ambele roluri (pagina principală e una — 225 / 231)
  import("./inceput.js?v=cf800c466e").then((m) => m.cardurileDeInceput(continut.querySelector("#inceput-carduri"), nav)).catch(() => {});
  BENZI.forEach((b) => continut.querySelector(`[data-banda="${b.cheie}"]`)
    .addEventListener("click", () => nav.deschide(b.titlu, (corp) => b.deschide(corp, nav), nivel ? { nivel } : undefined)));
  const suport = continut.querySelector('[data-banda="raport"]');
  const contor = async () => {          // [p34_raporteaza] numărul răspunsurilor necitite, pe banda „Suport”
    try {
      const r = await api.get("/raportari/contor");
      const n = (r && r.necitite) || 0;
      let e = suport.querySelector(".cab-card-badge");
      if (n > 0) {
        if (!e) { e = document.createElement("span"); e.className = "cab-card-badge"; suport.appendChild(e); }
        e.textContent = n;
      } else if (e) { e.remove(); }
    } catch {}
  };
  contor();
  document.addEventListener("raportari:schimbat", contor);
}
