// ds_piese.js — [15.1, zona A] piesele comune ale formularelor (DS: ds_butoane_campuri / ds_ferestre_tabele). O singură sursă pentru:
// grupurile formularului (Document, Furnizor / Client, Sume, Descriere), lățimea câmpului după rol (XS 9, S 16, M 38, L jumătate, XL
// toată lățimea) și cardul-rezumat de un rând cu detaliile pliate. Dimensiunile sunt în stil.css (`.ds-*`); aici stă numai alegerea
// clasei, ca ecranele să nu mai aleagă singure lățimi și grupuri.
import { esc, focusFaraSalt, cate } from "./api.js?v=83fcf3ce06";

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
    if (typeof detalii === "string") d.textContent = detalii; else d.appendChild(detalii);   // [15.1-E3] detaliile pot fi un element (rânduri cu butoane XS)
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
export function listaCuCautare(sel, { gol = "Alege din listă", cautare = "Caută în listă…", doarCare = null, ascuns = null, permanenta = false } = {}) {
  if (!sel || sel.__lista) return null;
  sel.__lista = true;
  const cutie = document.createElement("div");
  cutie.className = "ds-lista";
  sel.insertAdjacentElement("afterend", cutie);
  sel.classList.add("ds-lista-sursa");
  sel.setAttribute("tabindex", "-1");
  sel.setAttribute("aria-hidden", "true");
  let deschisa = permanenta;   // [15.1-E3, 722] lista permanentă: câmpul de căutare și rândurile sunt la vedere de la început (alegerea e lista, nu un meniu)
  let filtru = "";
  const opt = () => [...sel.options].filter((o) => !o.hasAttribute("data-alege") && o.value !== "" && (!doarCare || doarCare(o)));
  const text = (o) => (o.dataset.nume || o.textContent || "").trim();
  const alesTitlu = () => {
    const o = sel.options[sel.selectedIndex];
    return o && o.value ? text(o) : gol;
  };
  const deseneaza = () => {
    cutie.hidden = sel.hidden || (ascuns ? !!ascuns() : false);   // lista urmează select-ul sursă: ascuns / arătat de ecran (ex. categoria cotei 0%)
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
    cutie.classList.toggle("ds-lista-permanenta", permanenta);
    cutie.innerHTML = `${permanenta ? "" : `<button type="button" class="ds-lista-titlu buton-secundar" aria-expanded="${deschisa}" data-fara-actiune="deschide lista; alegerea din ea poartă acțiunea formularului"><span class="ds-lista-ales">${esc(alesTitlu())}</span><span aria-hidden="true">▾</span></button>`}
      ${deschisa ? `<div class="ds-lista-panou"><input type="search" class="camp-input ds-lista-cauta" placeholder="${esc(cautare)}" aria-label="${esc(cautare)}" value="${esc(filtru)}">
        <ul class="ds-lista-randuri" role="listbox">${potrivite.map((r, i) => r.grup
          ? `<li class="ds-lista-grup" role="presentation">${esc(r.grup)}</li>`
          : `<li class="ds-lista-rand${r.o.disabled ? " ds-lista-inactiv" : ""}${r.o.selected && r.o.value ? " ds-lista-ales-rand" : ""}" role="option" aria-selected="${!!(r.o.selected && r.o.value)}" data-i="${i}">
              <span class="ds-lista-nume" title="${esc(r.o.dataset.detalii || text(r.o))}">${esc(text(r.o))}</span>
              <span class="ds-lista-motiv">${esc(r.o.dataset.motiv || "")}</span></li>
            ${r.o.dataset.detalii ? `<li class="ds-lista-detalii" data-pentru="${i}" hidden>${esc(r.o.dataset.detalii)}</li>` : ""}`).join("")}
          ${potrivite.some((r) => !r.grup) ? "" : '<li class="ds-lista-gol">Nimic găsit. Schimbă textul căutat.</li>'}</ul></div>` : ""}`;
    const titlu = cutie.querySelector(".ds-lista-titlu");
    if (titlu) titlu.addEventListener("click", () => { deschisa = !deschisa; deseneaza(); if (deschisa) focusFaraSalt(cutie.querySelector(".ds-lista-cauta")); });
    const c = cutie.querySelector(".ds-lista-cauta");
    if (c) c.addEventListener("input", () => { filtru = c.value; deseneaza(); const n = cutie.querySelector(".ds-lista-cauta"); focusFaraSalt(n); n.setSelectionRange(n.value.length, n.value.length); });
    cutie.querySelectorAll(".ds-lista-rand").forEach((li) => li.addEventListener("click", () => {
      const r = potrivite[Number(li.dataset.i)];
      const det = cutie.querySelector(`.ds-lista-detalii[data-pentru="${li.dataset.i}"]`);
      if (r.o.disabled) { if (det) det.hidden = !det.hidden; return; }   // opțiunea care nu se poate alege își spune motivul întreg
      sel.value = r.o.value;
      deschisa = permanenta; filtru = permanenta ? filtru : "";
      sel.dispatchEvent(new Event("input", { bubbles: true }));
      sel.dispatchEvent(new Event("change", { bubbles: true }));
      deseneaza();
    }));
  };
  new MutationObserver(deseneaza).observe(sel, { childList: true, subtree: true, attributes: true, attributeFilter: ["disabled", "selected", "hidden"] });
  sel.addEventListener("change", deseneaza);
  deseneaza();
  return cutie;
}

/** [15.1, 687.1] Semnalele unei ferestre: un rând de 36 px pe semnal (cel mult 90 de caractere), „ce e de făcut” pliat sub el; fără derulare proprie: peste
 *  `limita` se arată primele și „încă n ▾”. `ton`: avertisment | eroare | ok (banda din stânga). Desenează în `zona`; întoarce elementul. */
export function semnaleDS(zona, items, { titlu = "Semnale", ton = "avertisment", limita = 6 } = {}) {
  const lista = (items || []).map((x) => (typeof x === "string" ? { mesaj: x } : x)).filter((x) => x && x.mesaj);
  const scurt = (t) => { const p = String(t).split(/(?<=\.)\s/)[0]; return p.length > 90 ? p.slice(0, 89) + "…" : p; };
  zona.innerHTML = `<section class="ds-semnale"><h3 class="ds-sectiune-titlu">${esc(titlu)} (${lista.length})</h3><ul class="ds-semnale-lista"></ul></section>`;
  const ul = zona.querySelector(".ds-semnale-lista");
  const buton = (clasa, text, laClic) => {   // butoanele se creează numai când au ce arăta: nu e o acțiune care dispare, ci una care nu există
    const b = document.createElement("button");
    b.type = "button";
    b.className = "buton-secundar " + clasa;
    b.dataset.faraActiune = "plierea / arătarea semnalelor în fereastra curentă";
    b.textContent = text;
    b.addEventListener("click", laClic);
    return b;
  };
  lista.forEach((x, i) => {
    const text = String(x.mesaj), s = scurt(text), are = text.trim() !== s.trim();
    const li = document.createElement("li");
    li.className = "ds-semnal-cutie";
    if (i >= limita) li.hidden = true;
    const rand = document.createElement("div");
    rand.className = "ds-semnal ds-semnal-" + ton;
    const sp = document.createElement("span");
    sp.className = "ds-semnal-text";
    sp.title = text;
    sp.textContent = s;
    rand.appendChild(sp);
    li.appendChild(rand);
    if (are) {
      const det = document.createElement("div");
      det.className = "ds-semnal-detalii";
      det.hidden = true;
      det.textContent = text;
      const plie = buton("ds-semnal-plie", "▾ detalii", () => {
        det.hidden = !det.hidden;
        plie.setAttribute("aria-expanded", String(!det.hidden));
        plie.textContent = det.hidden ? "▾ detalii" : "▴ detalii";
      });
      plie.setAttribute("aria-expanded", "false");
      rand.appendChild(plie);
      li.appendChild(det);
    }
    if (x.actiune) {   // [15.1-E3, 732] acțiunea semnalului: buton S lângă rând, nu casetă în mijlocul textului
      const a = buton("buton-s ds-semnal-actiune", x.actiune.eticheta, x.actiune.laClic);
      a.dataset.faraActiune = x.actiune.faraActiune || "navigare în fereastra curentă";
      li.insertBefore(a, li.children[1] || null);
    }
    ul.appendChild(li);
  });
  if (lista.length > limita) {
    const inca = buton("ds-semnale-inca", `încă ${lista.length - limita} ▾`, () => { ul.querySelectorAll(".ds-semnal-cutie[hidden]").forEach((e) => { e.hidden = false; }); inca.remove(); });
    zona.querySelector(".ds-semnale").appendChild(inca);
  }
  return zona;
}


/** Tabelul DS (15.1-D): cap de 40 px fix, rânduri de 44 px, zebra pe rândurile pare, starea numai ca pastilă în coloana „Stare”, acțiunile ca butoane XS în
 *  ultima coloană, un rând nu se rupe pe două linii (textul lung se taie cu „…”, întreg în `title`). Un rând întreg poate fi apăsabil (`laClic`).
 *  coloane: [{ cheie, titlu, tip: "text" | "num" | "stare" | "actiuni" }]
 *  randuri: [{ celule: { cheie: text }, stare: { text, ton: "eroare" | "avertisment" | "ok" | "info" }, actiuni: [{ eticheta, laClic, motivInactiv }], laClic }] */
export function tabelDS(zona, { coloane, randuri, gol = "Nimic de arătat.", subsol = "" }) {
  zona.innerHTML = "";
  if (!randuri || !randuri.length) {
    const p = document.createElement("p");
    p.className = "ds-tabel-gol";
    p.textContent = gol;
    zona.appendChild(p);
    return null;
  }
  const cutie = document.createElement("div");
  cutie.className = "ds-tabel-cutie";
  const tabel = document.createElement("table");
  tabel.className = "ds-tabel";
  const cap = tabel.createTHead().insertRow();
  coloane.forEach((c) => {
    const th = document.createElement("th");
    th.scope = "col";
    th.className = "ds-tabel-" + (c.tip || "text");
    th.textContent = c.titlu || "";
    cap.appendChild(th);
  });
  const corp = tabel.createTBody();
  randuri.forEach((r) => {
    const tr = corp.insertRow();
    if (r.laClic) { tr.classList.add("ds-tabel-apasabil"); tr.tabIndex = 0; tr.addEventListener("click", r.laClic); tr.addEventListener("keydown", (e) => { if (e.key === "Enter") r.laClic(); }); }
    coloane.forEach((c) => {
      const td = tr.insertCell();
      td.className = "ds-tabel-" + (c.tip || "text");
      if (c.tip === "stare") {
        const st = r.stare || {};
        const sp = document.createElement("span");
        sp.className = "ds-pastila ds-pastila-" + (st.ton || "info");
        sp.textContent = st.text || "";
        td.appendChild(sp);
      } else if (c.tip === "actiuni") {
        (r.actiuni || []).forEach((a) => {
          const b = document.createElement("button");
          b.type = "button";
          b.className = "buton-secundar buton-xs";
          b.textContent = a.eticheta;
          b.dataset.faraActiune = a.faraActiune || "navigare în fereastra curentă";
          if (a.motivInactiv) { b.setAttribute("aria-disabled", "true"); b.dataset.motivInactiv = a.motivInactiv; b.title = a.motivInactiv; }
          else b.addEventListener("click", (e) => { e.stopPropagation(); a.laClic(e); });
          td.appendChild(b);
        });
      } else {
        const t = String((r.celule || {})[c.cheie] ?? "");
        td.textContent = t;
        td.title = t;
      }
    });
  });
  cutie.appendChild(tabel);
  const sub = document.createElement("div");   // [15.1-E3] subsolul de 44 px cu totalul (DS: tabelul are cap, rânduri și subsol)
  sub.className = "ds-tabel-subsol";
  sub.textContent = subsol || cate(randuri.length, "rând", "rânduri");
  cutie.appendChild(sub);
  zona.appendChild(cutie);
  return tabel;
}


/** [15.1-E3, 731 / 732] Un semnal ca text HTML (pentru ecranele care își compun corpul ca șir): același rând de 36 px ca `semnaleDS`, cu „ce e de făcut” pliat
 *  (`detaliiHtml`, deja scăpat) și, când are acțiune, butonul S lângă rând (`actiuneHtml`, un `<button class="buton-secundar buton-s">`). Pliarea o leagă
 *  `legaSemnale(radacina)`. `text` mai lung de 90 de caractere se taie la prima propoziție; textul întreg trece în detalii. */
// butonul de pliere al unui semnal / card: o singură funcție, chemată numai când sunt detalii de arătat (nu e o acțiune care dispare: nu există fără detalii)
const _butonPlie = (clasa) => `<button type="button" class="buton-secundar ${clasa}" aria-expanded="false" data-fara-actiune="plierea / arătarea detaliilor în fereastra curentă">▾ detalii</button>`;

export function semnalHtml({ ton = "avertisment", text, detaliiHtml = "", actiuneHtml = "" }) {
  const t = String(text || "");
  const prima = t.split(/(?<=\.)\s/)[0];
  const scurt = prima.length > 90 ? prima.slice(0, 89) + "…" : prima;
  const are = detaliiHtml || t.trim() !== scurt.trim();
  const detalii = (detaliiHtml || "") + (t.trim() !== scurt.trim() ? `<p class="ds-semnal-intreg">${esc(t)}</p>` : "");
  return `<div class="ds-semnal-cutie"><div class="ds-semnal ds-semnal-${esc(ton)}"><span class="ds-semnal-text" title="${esc(t)}">${esc(scurt)}</span>${
    are ? _butonPlie("ds-semnal-plie") : ""}</div>${actiuneHtml}${
    are ? `<div class="ds-semnal-detalii" hidden>${detalii}</div>` : ""}</div>`;
}

/** Leagă pliarea semnalelor `semnalHtml` din `radacina` (o singură dată pe rădăcină; semnalele noi intră în aceeași legare). */
export function legaSemnale(radacina) {
  if (!radacina || radacina.__semnale) return;
  radacina.__semnale = true;
  radacina.addEventListener("click", (e) => {
    const b = e.target instanceof Element && e.target.closest(".ds-semnal-plie, .ds-rezumat-plie");
    if (!b || !radacina.contains(b)) return;
    const det = b.closest(".ds-semnal-cutie, .ds-rezumat-cutie").querySelector(".ds-semnal-detalii, .ds-rezumat-detalii");
    if (!det) return;
    det.hidden = !det.hidden;
    b.setAttribute("aria-expanded", String(!det.hidden));
    b.textContent = det.hidden ? "▾ detalii" : "▴ detalii";
  });
}

/** Tabelul DS ca text HTML (aceleași clase ca `tabelDS`): `coloane` [{ titlu, tip, latime? }], `randuri` [{ atribute?, celule: [text | { html }], stare?: { text, ton }, actiuniHtml? }];
 *  `subsol` = textul subsolului de 44 px (totalul). Celulele de text sunt scăpate aici; butoanele XS vin gata făcute în `actiuniHtml`. */
export function tabelDSHtml({ coloane, randuri, subsol = "" }) {
  const col = coloane.map((c) => `<col${c.latime ? ` style="width:${c.latime}"` : ""}>`).join("");
  const cap = coloane.map((c) => `<th scope="col" class="ds-tabel-${esc(c.tip || "text")}">${esc(c.titlu || "")}</th>`).join("");
  const corp = randuri.map((r) => {
    let k = 0;
    return `<tr class="cf-decl-item"${Object.entries(r.atribute || {}).map(([a, v]) => ` ${a}="${esc(String(v))}"`).join("")}>${coloane.map((c) => {
      if (c.tip === "stare") { const st = r.stare || {}; return `<td class="ds-tabel-stare"><span class="ds-pastila ds-pastila-${esc(st.ton || "info")}"${st.titlu ? ` title="${esc(st.titlu)}"` : ""}>${esc(st.text || "")}</span></td>`; }
      if (c.tip === "actiuni") return `<td class="ds-tabel-actiuni">${r.actiuniHtml || ""}</td>`;
      const v = (r.celule || [])[k++];
      const t = v && typeof v === "object" ? v.html : esc(v ?? "");
      return `<td class="ds-tabel-${esc(c.tip || "text")}" title="${esc(v && typeof v === "object" ? v.text || "" : v ?? "")}">${t}</td>`;
    }).join("")}</tr>`;
  }).join("");
  return `<div class="ds-tabel-cutie"><table class="ds-tabel"><colgroup>${col}</colgroup><thead><tr>${cap}</tr></thead><tbody>${corp}</tbody></table>${
    `<div class="ds-tabel-subsol">${esc(subsol || cate(randuri.length, "rând", "rânduri"))}</div>`}</div>`;
}

/** Card-rezumat ca text HTML (aceleași clase ca `cardRezumat`): o linie de 44 px, banda din stânga după ton, butonul S (`actiuneHtml`) în dreapta, detaliile pliate. */
export function rezumatHtml({ ton = "avertisment", text, detaliiHtml = "", actiuneHtml = "" }) {
  const t = String(text || "");
  const scurt = t.length > 90 ? t.slice(0, 89) + "…" : t;
  return `<div class="ds-rezumat-cutie"><div class="ds-rezumat ds-rezumat-${esc(ton)}" role="status"><span class="ds-rezumat-text" title="${esc(t)}">${esc(scurt)}</span>${actiuneHtml}${
    detaliiHtml ? _butonPlie("ds-rezumat-plie") : ""}</div>${
    detaliiHtml ? `<div class="ds-rezumat-detalii" hidden>${detaliiHtml}</div>` : ""}</div>`;
}
