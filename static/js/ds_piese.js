// ds_piese.js — [15.1, zona A] piesele comune ale formularelor (DS: ds_butoane_campuri / ds_ferestre_tabele). O singură sursă pentru:
// grupurile formularului (Document, Furnizor / Client, Sume, Descriere), lățimea câmpului după rol (XS 9, S 16, M 38, L jumătate, XL
// toată lățimea) și cardul-rezumat de un rând cu detaliile pliate. Dimensiunile sunt în stil.css (`.ds-*`); aici stă numai alegerea
// clasei, ca ecranele să nu mai aleagă singure lățimi și grupuri.
import { esc, focusFaraSalt } from "./api.js?v=760be1b9f8";

export const GRUPURI_FORMULAR = ["Document", "Furnizor / Client", "Sume", "Descriere"];

/** Lățimea implicită a unui câmp după rol (`lat` explicit are prioritate). */
export function latimeCamp(c) {
  if (c.lat) return c.lat;
  if (c.tip === "cui") return "cui";
  if (c.tip === "data" || c.tip === "numar" || c.tip === "moneda") return "s";
  if (c.tip === "select" && c.optiuni && c.optiuni.length <= 6) return "xl";   // grup de alegere: pe un rând, toată lățimea
  if (c.tip === "cota_tva") return "cota";
  if (c.nume === "descriere") return "plin";
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
  el.innerHTML = `<div class="ds-rezumat ds-rezumat-${esc(ton)}" role="status"><span class="ds-rezumat-text" title="${esc(text)}">${esc(scurt)}</span></div>`;
  const rand = el.firstElementChild;
  const buton = (clasa, eticheta, laClic) => {   // o piesă care nu are ce arăta nu pune buton deloc (nu e o acțiune care dispare: nu exista)
    const b = document.createElement("button");
    b.type = "button";
    b.className = "buton-secundar " + clasa;
    b.dataset.faraActiune = "navigare sau pliere în fereastra curentă";
    b.textContent = eticheta;
    b.addEventListener("click", laClic);
    rand.appendChild(b);
    return b;
  };
  if (actiune) buton("ds-rezumat-actiune", actiune.eticheta, actiune.laClic);
  if (detalii) {
    const d = document.createElement("div");
    d.className = "ds-rezumat-detalii";
    d.hidden = true;
    d.textContent = detalii;
    el.appendChild(d);
    const plie = buton("ds-rezumat-plie", "▾ detalii", () => {
      d.hidden = !d.hidden;
      plie.setAttribute("aria-expanded", String(!d.hidden));
      plie.textContent = d.hidden ? "▾ detalii" : "▴ detalii";
    });
    plie.setAttribute("aria-expanded", "false");
  }
  return el;
}

/** [15.1, 722] Lista cu căutare (DS: lista cu căutare, 720 px, rânduri de 44 px): înlocuiește vizual o listă derulantă cu texte lungi. Lista derulantă
 *  rămâne sursa valorii (ascuns): `value`, `change` și `select_option` din teste merg ca înainte. Fiecare opțiune poate purta
 *  `data-nume` (textul principal, în stânga), `data-motiv` (motivul scurt, în dreapta) și `data-detalii` (textul întreg, la clic);
 *  fără ele, textul opțiunii e textul principal. Opțiunile `disabled` se văd, dar nu se aleg; clicul pe ele arată detaliile.
 *  Nimic nu se deschide singur: lista se deschide la clic pe câmpul-titlu. Se redesenează când opțiunile select-ului se schimbă. */
export function listaCuCautare(sel, { gol = "Alege din listă", cautare = "Caută în listă…" } = {}) {
  if (!sel || sel.__lista) return null;
  sel.__lista = true;
  const cutie = document.createElement("div");
  cutie.className = "ds-lista";
  sel.insertAdjacentElement("afterend", cutie);
  sel.classList.add("ds-lista-sursa");
  sel.setAttribute("tabindex", "-1");
  sel.setAttribute("aria-hidden", "true");
  let deschisa = false;
  let filtru = "";
  const opt = () => [...sel.options].filter((o) => !o.hasAttribute("data-alege") && o.value !== "");
  const text = (o) => (o.dataset.nume || o.textContent || "").trim();
  const alesTitlu = () => {
    const o = sel.options[sel.selectedIndex];
    return o && o.value ? text(o) : gol;
  };
  const deseneaza = () => {
    const randuri = [];
    let grup = null;
    for (const o of opt()) {
      const g = o.parentElement && o.parentElement.tagName === "OPTGROUP" ? o.parentElement.label : "";
      if (g !== grup) { grup = g; if (g) randuri.push({ grup: g }); }
      randuri.push({ o });
    }
    const f = filtru.trim().toLowerCase();
    const filtrate = randuri.filter((r) => r.grup || !f || (text(r.o) + " " + (r.o.dataset.motiv || "")).toLowerCase().includes(f));
    // un titlu de grup fără niciun rând sub el nu se arată
    const potrivite = filtrate.filter((r, i) => !r.grup || (filtrate[i + 1] && !filtrate[i + 1].grup));
    cutie.innerHTML = `<button type="button" class="ds-lista-titlu buton-secundar" aria-expanded="${deschisa}" data-fara-actiune="deschide lista; alegerea din ea poartă acțiunea formularului"><span class="ds-lista-ales">${esc(alesTitlu())}</span><span aria-hidden="true">▾</span></button>
      ${deschisa ? `<div class="ds-lista-panou"><input type="search" class="camp-input ds-lista-cauta" placeholder="${esc(cautare)}" aria-label="${esc(cautare)}" value="${esc(filtru)}">
        <ul class="ds-lista-randuri" role="listbox">${potrivite.map((r, i) => r.grup
          ? `<li class="ds-lista-grup" role="presentation">${esc(r.grup)}</li>`
          : `<li class="ds-lista-rand${r.o.disabled ? " ds-lista-inactiv" : ""}${r.o.selected && r.o.value ? " ds-lista-ales-rand" : ""}" role="option" aria-selected="${!!(r.o.selected && r.o.value)}" data-i="${i}">
              <span class="ds-lista-nume" title="${esc(r.o.dataset.detalii || text(r.o))}">${esc(text(r.o))}</span>
              <span class="ds-lista-motiv">${esc(r.o.dataset.motiv || "")}</span></li>
            ${r.o.dataset.detalii ? `<li class="ds-lista-detalii" data-pentru="${i}" hidden>${esc(r.o.dataset.detalii)}</li>` : ""}`).join("")}
          ${potrivite.some((r) => !r.grup) ? "" : '<li class="ds-lista-gol">Nimic găsit. Schimbă textul căutat.</li>'}</ul></div>` : ""}`;
    cutie.querySelector(".ds-lista-titlu").addEventListener("click", () => { deschisa = !deschisa; deseneaza(); if (deschisa) focusFaraSalt(cutie.querySelector(".ds-lista-cauta")); });
    const c = cutie.querySelector(".ds-lista-cauta");
    if (c) c.addEventListener("input", () => { filtru = c.value; deseneaza(); const n = cutie.querySelector(".ds-lista-cauta"); focusFaraSalt(n); n.setSelectionRange(n.value.length, n.value.length); });
    cutie.querySelectorAll(".ds-lista-rand").forEach((li) => li.addEventListener("click", () => {
      const r = potrivite[Number(li.dataset.i)];
      const det = cutie.querySelector(`.ds-lista-detalii[data-pentru="${li.dataset.i}"]`);
      if (r.o.disabled) { if (det) det.hidden = !det.hidden; return; }   // opțiunea care nu se poate alege își spune motivul întreg
      sel.value = r.o.value;
      deschisa = false; filtru = "";
      sel.dispatchEvent(new Event("input", { bubbles: true }));
      sel.dispatchEvent(new Event("change", { bubbles: true }));
      deseneaza();
    }));
  };
  new MutationObserver(deseneaza).observe(sel, { childList: true, subtree: true, attributes: true, attributeFilter: ["disabled", "selected"] });
  sel.addEventListener("change", deseneaza);
  deseneaza();
  return cutie;
}
