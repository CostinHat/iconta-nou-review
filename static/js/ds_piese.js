// ds_piese.js — [15.1, zona A] piesele comune ale formularelor (DS: ds_butoane_campuri / ds_ferestre_tabele). O singură sursă pentru:
// grupurile formularului (Document, Furnizor / Client, Sume, Descriere), lățimea câmpului după rol (XS 9, S 16, M 38, L jumătate, XL
// toată lățimea) și cardul-rezumat de un rând cu detaliile pliate. Dimensiunile sunt în stil.css (`.ds-*`); aici stă numai alegerea
// clasei, ca ecranele să nu mai aleagă singure lățimi și grupuri.
import { esc } from "./api.js?v=c6c45aefe4";

export const GRUPURI_FORMULAR = ["Document", "Furnizor / Client", "Sume", "Descriere"];

/** Lățimea implicită a unui câmp după rol (`lat` explicit are prioritate). */
export function latimeCamp(c) {
  if (c.lat) return c.lat;
  if (c.tip === "cui") return "cui";
  if (c.tip === "data" || c.tip === "numar" || c.tip === "moneda") return "s";
  if (c.tip === "select" && c.optiuni && c.optiuni.length <= 6) return "xl";   // grup de alegere: pe un rând, toată lățimea
  if (c.tip === "cota_tva") return "xl";
  if (c.nume === "descriere") return "xl";
  return "l";
}

/** Grupul unui câmp: explicit (`grup`) sau după rol. */
export function grupCamp(c) {
  if (c.grup) return c.grup;
  if (c.nume === "descriere") return "Descriere";
  if (c.tip === "cui" || c.numeCamp || /_nume$/.test(c.nume)) return "Furnizor / Client";
  if (c.tip === "numar" || c.tip === "cota_tva") return "Sume";
  return "Document";
}

/** HTML-ul formularului grupat: `htmlCamp(c, clasaLatime)` produce un câmp; câmpurile intră pe grupuri, în ordinea contabilului. */
export function formularGrupat(campuri, htmlCamp) {
  const pe = new Map(GRUPURI_FORMULAR.map((g) => [g, []]));
  for (const c of campuri) {
    const g = grupCamp(c);
    if (!pe.has(g)) pe.set(g, []);
    pe.get(g).push(c);
  }
  return `<div class="ds-formular">${[...pe].filter(([, cs]) => cs.length).map(([g, cs]) =>
    `<section class="ds-grup" data-grup="${esc(g)}"><h3 class="ds-grup-titlu">${esc(g)}</h3>
       <div class="ds-grup-campuri">${cs.map((c) => htmlCamp(c, "ds-lat-" + latimeCamp(c))).join("")}</div></section>`).join("")}</div>`;
}

/** După fiecare schimbare de câmpuri vizibile: grupul fără niciun câmp la vedere dispare; dacă rămâne un număr impar de grupuri
 *  alăturate, ultimul ia toată lățimea (nu rămâne jumătate de ecran goală). */
export function actualizeazaGrupe(radacina) {
  const grupuri = [...radacina.querySelectorAll(".ds-grup")];
  for (const g of grupuri) {
    const are = [...g.querySelectorAll(".ds-grup-campuri > .camp")].some((c) => c.style.display !== "none" && !c.classList.contains("camp-dedus"));
    g.hidden = !are;
    // Document (cu grupul de alegere al felului pe un rând) și Descriere iau toată lățimea; celelalte stau alăturat
    g.classList.toggle("ds-grup-lat", are && (g.dataset.grup === "Descriere" || g.dataset.grup === "Document"));
  }
  const perechi = grupuri.filter((g) => !g.hidden && !g.classList.contains("ds-grup-lat"));
  if (perechi.length % 2 === 1) perechi[perechi.length - 1].classList.add("ds-grup-lat");
}

/** Cardul-rezumat de un rând (44 px), cu detaliile pliate sub „▾ detalii”. `ton`: avertisment | eroare | ok. Întoarce elementul. */
export function cardRezumat({ text, ton = "avertisment", detalii = "", actiune = null }) {
  const el = document.createElement("div");
  el.className = "ds-rezumat-cutie";
  const scurt = String(text).length > 90 ? String(text).slice(0, 89) + "…" : String(text);
  el.innerHTML = `<div class="ds-rezumat ds-rezumat-${esc(ton)}" role="status"><span class="ds-rezumat-text" title="${esc(text)}">${esc(scurt)}</span>
      ${actiune ? `<button type="button" class="buton-secundar ds-rezumat-actiune" data-fara-actiune="navigare spre ecranul numit în buton">${esc(actiune.eticheta)}</button>` : ""}
      ${detalii ? `<button type="button" class="buton-secundar ds-rezumat-plie" aria-expanded="false" data-fara-actiune="plierea detaliilor">▾ detalii</button>` : ""}</div>
    ${detalii ? `<div class="ds-rezumat-detalii" hidden>${esc(detalii)}</div>` : ""}`;
  const plie = el.querySelector(".ds-rezumat-plie");
  if (plie) plie.addEventListener("click", () => {
    const d = el.querySelector(".ds-rezumat-detalii");
    d.hidden = !d.hidden;
    plie.setAttribute("aria-expanded", String(!d.hidden));
    plie.textContent = d.hidden ? "▾ detalii" : "▴ detalii";
  });
  const act = el.querySelector(".ds-rezumat-actiune");
  if (act && actiune) act.addEventListener("click", actiune.laClic);
  return el;
}
