// salut.js — partea de sus a paginii principale, ACEEAȘI la ambele roluri (contabilul-șef: cabinet.js; asistentul: asistent.js).
//
// [deficiențele 225 + 231, comanda Costin 12.10.2026, verbatim în DECIZII] „«Recomandă» și «Suport» sunt două benzi înguste, una lângă
// alta, deasupra cardurilor, la ambele roluri, ca la Cabinet.” · „Pagina principală are aceeași structură la ambele roluri.”
// Structura, la amândouă: banda de salut (titlul paginii + data, în stânga; cele două benzi, în dreapta), apoi grila de carduri —
// fără meniu lateral. Un singur loc o scrie (aici), deci cele două pagini nu mai pot diverge; gard `PAGINA_PRINCIPALA_UNA`
// (verificator) + `frontend_test/e2e/e2e_comanda_1210.py`.

import { api, dataRo, ICOANE, CULORI_CARD } from "../api.js?v=2561dbfd34";
import { randeazaRecomanda } from "./recomanda.js?v=239a4a2607"; // [p31_recomanda]
import { randeazaRaporteaza } from "./raporteaza.js?v=b330ba128c"; // [p34_raporteaza]

function svg(nume, culoare) {
  return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="${culoare}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICOANE[nume] || ""}</svg>`;
}

//: cele două benzi, în ordine (DS cap.12: Recomandă = chihlimbar, Suport = ardezie)
const BENZI = [
  { cheie: "recomanda", titlu: "Recomandă", icon: "gift", culori: CULORI_CARD.chihlimbar, deschide: randeazaRecomanda },
  { cheie: "raport", titlu: "Suport", icon: "suport", culori: CULORI_CARD.ardezie, deschide: randeazaRaporteaza },
];

// Banda de salut + grila (goală, de umplut de pagină). `prenume` vine din sesiune.
export function paginaPrincipala(prenume) {
  return `
    <div class="cab-salut">
      <div>
        <h1 class="cab-salut-nume">Salut, ${prenume}</h1>
        <div class="cab-salut-data">Spațiul tău de lucru — ${dataRo(new Date(), "lung")}</div>
      </div>
      <div class="cab-benzi">${BENZI.map((b) => `
        <button type="button" class="cab-card cab-banda" data-banda="${b.cheie}" style="background:${b.culori.bg};color:${b.culori.fg}">
          ${svg(b.icon, b.culori.fg)}<span class="cab-card-titlu">${b.titlu}</span>
        </button>`).join("")}
      </div>
    </div>
    <div class="cab-grila"></div>`;
}

// Leagă benzile (`nivel` = nivelul ferestrei, ca la cardurile paginii) și ține la zi numărul sesizărilor necitite pe „Suport”.
export function legaBenzile(continut, nav, nivel) {
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
