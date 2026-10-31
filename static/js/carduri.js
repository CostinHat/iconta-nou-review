// carduri.js — [lotul 14, deficiența 687 — clasă, toate ferestrele de lucru; DS cap.9 v2.105 „Ce e secundar stă în carduri-rezumat”]
// Comanda Costin 14.1, verbatim: „Fereastra de lucru se deschide direct pe tot ecranul cu datele (tabel, formular), sub titlu și acțiunea
// principală, vizibile fără derulare. Tot ce e secundar (avertismente, verificări, explicații) devine un șir de carduri-rezumat de un rând
// sub titlu («45 de ciorne nevalidate», «Lipsesc rulajele ian.–aug.», «Balanța se închide ✓»), fiecare deschis la clic pe tot ecranul;
// nicio casetă nu împinge datele în jos. Citatele legale doar în cardul deschis.”
//
// UN singur mecanism: `siraCarduri(zona, carduri, nav)` desenează șirul (un rând, sub titlu), iar clicul pe un card deschide fereastra de
// lucru a lui (`nav.deschide`, `{ lat: "lucru" }`: centrată, cât ecranul — DS cap.2a). Cardul e un BUTON (DS cap.2a „Orice acțiune e un
// buton”); textul lui e O FRAZĂ SCURTĂ, cu cifra în ea; ce e mai lung (explicația, citatul legal, lista) stă în fereastra lui. Tonul
// (`ok` / `info` / `atentie` / `eroare`) dă culoarea punctului, nu a textului; „ok” nu înseamnă „nimic de făcut”, ci „verificat și în regulă”.
import { esc } from "./api.js?v=4364ee71f3";

/**
 * carduri: [{ id, ton, text, titlu?, deschide?(corp, nav), motiv? }]
 *   text     — rezumatul de un rând (cu cifra: „2 ciorne nevalidate”);
 *   titlu    — titlul ferestrei deschise (implicit `text`);
 *   deschide — desenează conținutul ferestrei cardului; fără el cardul e inactiv (rămâne la locul lui, `motiv` la trecerea cu mouse-ul);
 *   motiv    — de ce un card e inactiv sau ce spune pe scurt (atributul `title`).
 * Întoarce elementul șirului. `zona` = elementul în care se desenează (înlocuiește conținutul).
 */
export function siraCarduri(zona, carduri, nav) {
  if (!zona) return null;
  const lista = (carduri || []).filter(Boolean);
  zona.className = ((zona.className || "").replace(/\bsir-carduri\b/g, "").trim() + " sir-carduri").trim();
  zona.innerHTML = lista.map((c) => `<button type="button" class="card-rezumat card-${esc(c.ton || "info")}" data-card="${esc(c.id || "")}"${
    c.deschide ? "" : ' aria-disabled="true"'} title="${esc(c.motiv || c.text)}"><span class="card-punct" aria-hidden="true"></span><span class="card-text">${esc(c.text)}</span></button>`).join("");
  lista.forEach((c) => {
    const b = zona.querySelector(`[data-card="${CSS.escape(c.id || "")}"]`);
    if (!b || !c.deschide) return;
    b.addEventListener("click", () => { if (nav.dinRefuz) nav.dinRefuz(); nav.deschide(c.titlu || c.text, (corp) => c.deschide(corp, nav), { lat: "lucru" }); });   // dinRefuz: fereastra de dedesubt se păstrează (luna aleasă, filtrele), „înapoi” o regăsește
  });
  return zona;
}
