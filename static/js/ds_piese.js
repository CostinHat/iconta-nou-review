// ds_piese.js — [15.1, zona A] piesele comune ale formularelor (DS: ds_butoane_campuri / ds_ferestre_tabele). O singură sursă pentru:
// grupurile formularului (Document, Furnizor / Client, Sume, Descriere), lățimea câmpului după rol (XS 9, S 16, M 38, L jumătate, XL
// toată lățimea) și cardul-rezumat de un rând cu detaliile pliate. Dimensiunile sunt în stil.css (`.ds-*`); aici stă numai alegerea
// clasei, ca ecranele să nu mai aleagă singure lățimi și grupuri.
import { esc, focusFaraSalt, cate } from "./api.js?v=0b48920b43";

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
      const g = o.parentElement && o.parentElement.tagName === "OPTGROUP" ? (o.parentElement.dataset.titlu || o.parentElement.label) : "";   // `data-titlu`: titlul scurt al grupului (eticheta lungă rămâne în opțiunea-sursă)
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
    // [15.1-E5, 727.2] Enter în căutare alege primul rând din filtru (nu trimite formularul și nu deschide nimic)
    if (c) c.addEventListener("keydown", (ev) => {
      if (ev.key !== "Enter") return;
      ev.preventDefault();
      const primul = cutie.querySelector(".ds-lista-rand:not(.ds-lista-inactiv)");
      if (primul) primul.click();
    });
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
  // [15.1-E5, 727.2] lista stă în eticheta câmpului: un clic pe rând (text, nu control) ar fi dat de browser primului control din etichetă — „?” de lângă titlu,
  // care deschide ajutorul. Clicul în listă nu activează eticheta; ajutorul se deschide numai din „?”.
  cutie.addEventListener("click", (ev) => { if (!(ev.target instanceof Element) || !ev.target.closest("button, input")) ev.preventDefault(); });
  new MutationObserver(deseneaza).observe(sel, { childList: true, subtree: true, attributes: true, attributeFilter: ["disabled", "selected", "hidden"] });
  sel.addEventListener("change", deseneaza);
  deseneaza();
  return cutie;
}

/** [15.1-E5, 740] Textul unui semnal: prima propoziție ÎNTREAGĂ, pe cel mult două rânduri (până la 200 de caractere); o propoziție mai lungă se rupte la
 *  ultimul cuvânt dinainte de limită, fără „…”, iar restul trece în detalii (textul întreg). */
export function textSemnal(t) {
  const prima = String(t).split(/(?<=\.)\s/)[0];
  if (prima.length <= 200) return prima;
  const taiat = prima.slice(0, 200);
  const sp = taiat.lastIndexOf(" ");
  return (sp > 120 ? taiat.slice(0, sp) : taiat).replace(/[\s,;—–-]+$/, "");
}

/** [15.1, 687.1] Semnalele unei ferestre: un rând de 36 px pe semnal (textul pe cel mult două rânduri, fără tăiere), „ce e de făcut” pliat sub el; fără derulare proprie: peste
 *  `limita` se arată primele și „încă n ▾”. `ton`: avertisment | eroare | ok (banda din stânga). Desenează în `zona`; întoarce elementul. */
export function semnaleDS(zona, items, { titlu = "Semnale", ton = "avertisment", limita = 6 } = {}) {
  const lista = (items || []).map((x) => (typeof x === "string" ? { mesaj: x } : x)).filter((x) => x && x.mesaj);
  const scurt = textSemnal;
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
 *  `legaSemnale(radacina)`. `text` mai lung de 200 de caractere se rupe la ultimul cuvânt dinainte; textul întreg trece în detalii. */
// butonul de pliere al unui semnal / card: o singură funcție, chemată numai când sunt detalii de arătat (nu e o acțiune care dispare: nu există fără detalii)
const _butonPlie = (clasa) => `<button type="button" class="buton-secundar ${clasa}" aria-expanded="false" data-fara-actiune="plierea / arătarea detaliilor în fereastra curentă">▾ detalii</button>`;

export function semnalHtml({ ton = "avertisment", text, detaliiHtml = "", actiuneHtml = "" }) {
  const t = String(text || "");
  const scurt = textSemnal(t);
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
export function tabelDSHtml({ coloane, randuri, subsol = "", randCls = "" }) {
  const cap = coloane.map((c) => `<th scope="col" class="ds-tabel-${esc(c.tip || "text")}"${c.latime ? ` style="width:${esc(c.latime)}"` : ""}>${esc(c.titlu || "")}</th>`).join("");   // lățimea pe antet (bate regula pe clasă a coloanei „Acțiuni” / „Stare”)
  const corp = randuri.map((r) => {
    let k = 0;
    return `<tr class="cf-decl-item${randCls ? " " + esc(randCls) : ""}"${Object.entries(r.atribute || {}).map(([a, v]) => ` ${a}="${esc(String(v))}"`).join("")}>${coloane.map((c) => {
      if (c.tip === "stare") { const st = r.stare || {}; return `<td class="ds-tabel-stare"><span class="ds-pastila ds-pastila-${esc(st.ton || "info")}"${st.titlu ? ` title="${esc(st.titlu)}"` : ""}>${esc(st.text || "")}</span>${
        st.titlu ? ` <span class="ds-tabel-motiv" title="${esc(st.titlu)}">${esc(st.titlu)}</span>` : ""} </td>`; }   // motivul rândului, lângă pastilă (o linie, întreg în title)
      if (c.tip === "actiuni") return `<td class="ds-tabel-actiuni">${r.actiuniHtml || ""}</td>`;
      const v = (r.celule || [])[k++];
      const t = v && typeof v === "object" ? v.html : esc(v ?? "");
      return `<td class="ds-tabel-${esc(c.tip || "text")}${c.cls ? " " + esc(c.cls) : ""}" title="${esc(v && typeof v === "object" ? v.text || "" : v ?? "")}">${t} </td>`;   // spațiul de după text: coloanele se citesc cu spațiu între ele (textContent, copiere)
    }).join("")}</tr>`;
  }).join("");
  return `<div class="ds-tabel-cutie"><table class="ds-tabel"><thead><tr>${cap}</tr></thead><tbody>${corp}</tbody></table>${
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


// ── [15.1-E4] PIESELE APLICATE FERESTREI: tabelul DS și cardul-rezumat, o singură dată, pentru toate ecranele ───────────────────────────────────────
// Ecranele își desenează în continuare tabelele (`table`) și notele (`.ecran-nota`, `.caseta-info`, `.caseta-atentie`, paragrafele explicative); cadrul
// (`cadru.js`, la fiecare sincronizare, idempotent) le dă forma DS: aceeași clasă de piesă (`ds-tabel`, `ds-rezumat`), nu o reparație pe ecran (R8).
// Clasele vechi rămân pe element ca marcaje (clic pe rând, editare în celulă, id-uri, teste), nu ca aspect.

const _vizibilDS = (el) => !!(el.offsetParent || el.getClientRects().length);
const _txt = (t) => String(t || "").replace(/\s+/g, " ").trim();

// lățimile coloanelor după rol, aceleași în toate tabelele (Nr. crt. 7ch, Dată 12ch, Perioadă 10ch, Sumă 14ch, Stare 12ch, Acțiuni 12ch pe buton)
function _latimeColoana(th, celule) {
  const t = _txt(th.textContent);
  if (/^nr\.?\s*crt/i.test(t) || t === "Nr.") return "7ch";
  if (/^dat[ăa]\b/i.test(t)) return "12ch";
  if (/^perioad/i.test(t)) return "10ch";
  if (/^stare\b/i.test(t)) return "12ch";
  if (/^ac[țt]iuni\b/i.test(t) || (celule.length && celule.every((c) => c.querySelector("button") && _txt(c.textContent).length < 40))) {
    const n = Math.max(1, ...celule.map((c) => c.querySelectorAll("button").length));
    return 12 * n + "ch";
  }
  if (th.classList.contains("ds-tabel-num")) return "14ch";
  return "";
}

// [15.1-E5, 741] O celulă cu dată sau sumă nu se taie niciodată: coloana ei are lățimea celei mai late valori (nu mai puțin decât a fost cerută). Textul lung
// se taie numai în coloanele de descriere.
const _DATA_SAU_SUMA = /\b\d{1,2}\.\d{1,2}\.\d{4}\b|(^|[^\d.,])-?\d{1,3}(\.\d{3})*,\d{2}(\s|$)/;
export function coloaneDateSumeAplica(corp) {
  for (const t of corp.querySelectorAll("table.ds-tabel")) {
    if (!_vizibilDS(t) || !t.tHead) continue;
    const cap = [...t.tHead.rows[0].cells];
    cap.forEach((th, i) => {
      const celule = [...t.tBodies].flatMap((b) => [...b.rows]).map((r) => r.cells[i]).filter((c) => c && _vizibilDS(c) && _DATA_SAU_SUMA.test(c.textContent));
      if (!celule.length) return;
      const nevoie = Math.max(...celule.map((c) => c.scrollWidth)) + 2;
      if (celule.some((c) => c.scrollWidth > c.clientWidth + 1) && nevoie > th.getBoundingClientRect().width) th.style.width = nevoie + "px";
    });
  }
}

/** [15.1-E5, pct.1] Exportul tabelului DS: tipărește numai tabelul ferestrei (restul ferestrei e ascuns la tipărire, `@media print` din stil.css); din dialogul
 *  de tipărire se alege „Salvează ca PDF”. */
export function tiparesteTabel(corp) {
  const cutie = [...corp.querySelectorAll(".ds-tabel-cutie")].find(_vizibilDS) || [...corp.querySelectorAll("table")].find(_vizibilDS) || corp;   // fără tabel: conținutul ferestrei
  cutie.classList.add("tipareste-tinta");
  document.body.classList.add("tipareste-tabel");
  const gata = () => { cutie.classList.remove("tipareste-tinta"); document.body.classList.remove("tipareste-tabel"); window.removeEventListener("afterprint", gata); };
  window.addEventListener("afterprint", gata);
  window.print();
}

/** Tabelul vechi (`table` fără `ds-tabel`) devine tabelul DS: cutie cu subsol de 44 px (contorul de rânduri sau totalurile din `tfoot`), cap 40 px,
 *  rânduri 44 px, zebra, coloanele numerice la dreapta, lățimile după rol. Tabelele din `template`, din `[data-fara-piesa]` și cele cu structură
 *  de formular (fără `thead`) nu se ating. Subsolul își reîmprospătează contorul la fiecare sincronizare (rândurile filtrate nu se numără). */
export function tabeleDSAplica(corp) {
  const ingust = window.innerWidth < 900;   // fereastra de lucru DS e a ecranului lat; pe telefon tabelele rămân cum erau (rândurile nu încap pe o linie)
  for (const t of corp.querySelectorAll("table:not(.ds-tabel)")) {
    if (ingust || t.closest("template, [data-fara-piesa], .fereastra-antet, .ds-tabel-cutie:not(.ds-tabel-lista)") || !t.tHead || !_vizibilDS(t)) continue;
    // tabelul cu mai multe `tbody` (un tbody pe notă, rând detaliu care se desface: Registru jurnal, De validat) nu e o listă de rânduri de 44 px
    if (t.tBodies.length > 1 || t.querySelector("tbody.tn-nota, tr.tn-detaliu, tr[hidden]")) continue;
    // numai tabelul de citit: cel cu rând de totaluri (`tfoot`: lipit jos de ecran), cu câmpuri, cu butoane pe rând (ștergere, deschidere, bife) sau deja
    // într-o zonă de derulare rămâne cum e — conversia lui nu poate dovedi că totalul, bifa sau butonul rămân la vedere și la îndemână
    if (t.tFoot || t.querySelector("input, select, textarea") || t.tBodies[0].querySelector("button, a[href]") || t.closest(".zona-derulare")) continue;
    t.classList.add("ds-tabel");
    const cap = [...t.tHead.rows[0].cells];
    cap.forEach((th, i) => {
      const celule = [...t.tBodies].flatMap((b) => [...b.rows]).map((r) => r.cells[i]).filter(Boolean);
      const numeric = th.classList.contains("fd-td-num") || (celule.length && celule.every((c) => c.classList.contains("fd-td-num") || /^[−-]?[\d.\s]+(,\d+)?$/.test(_txt(c.textContent)) && _txt(c.textContent) !== ""));
      if (numeric) { th.classList.add("ds-tabel-num"); celule.forEach((c) => c.classList.add("ds-tabel-num")); }
      const lat = _latimeColoana(th, celule);
      if (lat) th.style.width = lat;
    });
    const cutie = document.createElement("div");
    cutie.className = "ds-tabel-cutie ds-tabel-vechi";
    t.replaceWith(cutie);
    cutie.appendChild(t);
    const sub = document.createElement("div");
    sub.className = "ds-tabel-subsol";
    cutie.appendChild(sub);
    // tabelul cu prea multe coloane pentru lățimea ferestrei nu se taie: celulele își păstrează rândurile (nimic ascuns în dreapta)
    if (cutie.scrollWidth > cutie.clientWidth + 1) cutie.classList.add("ds-tabel-lat");
  }
  for (const cutie of corp.querySelectorAll(".ds-tabel-vechi")) {
    const t = cutie.querySelector("table");
    const sub = cutie.querySelector(":scope > .ds-tabel-subsol");
    if (!t || !sub) continue;
    const randuri = [...t.tBodies].flatMap((b) => [...b.rows]).filter((r) => r.style.display !== "none" && !r.hidden && !r.classList.contains("fd-rand-gol"));
    const nou = cate(randuri.length, "rând", "rânduri");
    if (sub.textContent !== nou) sub.textContent = nou;
  }
}

const _TON = [
  [/caseta-atentie|msg-eroare|\beroare\b|mig-eroare/, "eroare"],
  [/avert|galben|dec-avert/, "avertisment"],
  [/caseta-ok|msg-ok|\bsucces\b/, "ok"],
];
const _SELECTOR_CARD = ".ecran-nota, .caseta-info, .caseta-atentie, .caseta-avertisment, .avertisment, .msg-info, .pf-intro, .tip-micut, .mig-intro";
// explicațiile (nu notele): numai când se rup pe mai multe rânduri — o explicație de un rând rămâne text
const _EXPLICATIE = ".pf-intro, .tip-micut, .mig-intro";
const _FARA_CARD = "template, [data-fara-piesa], .ds-rezumat-cutie, .ds-semnal, .ds-semnale, .ds-rezumat-detalii, .ds-semnal-detalii, table, button, .fereastra-antet, .fereastra-jos, details:not([open]), [hidden], .cautare-rez, .bara-fixa";
const _RANG = { avertisment: 0, ok: 1, info: 2 };

function _tonCard(el) {
  const c = String(el.className);
  for (const [re, ton] of _TON) if (re.test(c)) return ton;
  return "info";
}

/** Nota sau explicația devine cardul-rezumat (DS: 44 px, o linie, bandă stângă 4 px: portocaliu avertisment, roșu eroare, verde în regulă, gri informativ).
 *  Textul de peste 90 de caractere se taie cu „…” pe linia vizibilă și rămâne ÎNTREG sub „▾ detalii” (cu temeiul legal); eroarea își arată textul întreg,
 *  pe cât mai multe linii cât trebuie, mereu la vedere. Butoanele din notă rămân în rând, la dreapta (S). Din cardurile care nu sunt erori, cel mult 2 sunt
 *  la vedere (în ordinea avertisment, în regulă, informativ); restul stau sub „Semnale (n)”. Idempotent. */
const _BLOCURI = "table, ul, ol, form, .ds-tabel-cutie, h2, h3, h4, section, textarea, select, input";

// containerul de mesaj (`.msg-info` etc.) pe care ecranul l-a umplut apoi cu un tabel / listă / câmpuri nu e card: cardul automat se desface, conținutul rămâne la loc
function _desfaCard(el) {
  const sp = el.querySelector(":scope > .ds-rezumat-text");
  if (sp) { while (sp.firstChild) el.insertBefore(sp.firstChild, sp); sp.remove(); }
  el.querySelectorAll(":scope > .ds-rezumat-plie").forEach((b) => b.remove());
  if (el.__detalii) { el.__detalii.remove(); el.__detalii = null; }
  el.classList.remove("ds-rezumat", "ds-rezumat-sub", "ds-rezumat-sub-grup", "ds-rezumat-avertisment", "ds-rezumat-eroare", "ds-rezumat-ok", "ds-rezumat-info");
  delete el.dataset.dsAuto;
  el.querySelectorAll(".buton-s[data-ds-auto-s]").forEach((b) => { b.classList.remove("buton-s"); delete b.dataset.dsAutoS; });
}

export function carduriDSAplica(corp) {
  for (const el of corp.querySelectorAll("[data-ds-auto]")) if (el.querySelector(_BLOCURI)) _desfaCard(el);
  const vazute = [];
  // paragraful explicativ care se rupe pe mai multe rânduri (nu un câmp, nu o celulă) e tot o explicație: devine card
  const lungi = [...corp.querySelectorAll("p")].filter((p) => !p.matches(_SELECTOR_CARD) && !p.classList.contains("ds-rezumat") && !p.closest(_FARA_CARD + ", form, .ds-formular, .ds-grup, .ds-lista, .ds-semnale, .pf-frand") && _vizibilDS(p)
    && _txt(p.textContent).length >= 40 && p.getBoundingClientRect().height > (parseFloat(getComputedStyle(p).lineHeight) || 20) * 1.5);
  for (const el of new Set([...corp.querySelectorAll(_SELECTOR_CARD), ...lungi, ...corp.querySelectorAll(".ds-rezumat")])) {   // și cardurile făcute direct cu piesa (`cardRezumat`, `rezumatHtml`) intră în regula „cel mult 2”
    if (el.closest(_FARA_CARD) && !el.classList.contains("ds-rezumat")) continue;
    if (el.classList.contains("ds-rezumat") && el.closest(".ds-semnale, .ds-rezumat-detalii")) continue;
    if (!el.classList.contains("ds-rezumat") && (el.closest("label") || el.tagName === "SPAN")) continue;   // explicația dintr-o etichetă / bifă e text de câmp, nu card
    if (!el.classList.contains("ds-rezumat") && el.querySelector(_BLOCURI)) continue;
    if (!el.classList.contains("ds-rezumat") && [...el.querySelectorAll("button, a.buton-secundar")].some((b) => b.parentElement !== el)) continue;   // butonul din adâncimea notei rămâne unde l-a pus ecranul (nu se mută în rândul cardului)   // rândul de filtre / câmpuri nu e o explicație
    if (el.parentElement && el.parentElement.closest(".ds-rezumat")) continue;
    if (!_vizibilDS(el) && !el.classList.contains("ds-rezumat-sub")) continue;
    // textul propriu: fără butoane și câmpuri (rândul de acțiuni nu e text)
    let text = el.classList.contains("ds-rezumat") ? _txt((el.querySelector(":scope > .ds-rezumat-text") || el).textContent) : "";
    if (!el.classList.contains("ds-rezumat")) {
      const c = el.cloneNode(true);
      c.querySelectorAll("button, a.buton-secundar, select, input, textarea, .ajutor-btn").forEach((x) => x.remove());
      text = _txt(c.textContent);
      if (text.length < 8) continue;   // mesajul gol sau „…” de încărcare nu devine card
      if (el.matches(_EXPLICATIE) && !el.matches(".ecran-nota, .caseta-info, .caseta-atentie") && el.getBoundingClientRect().height <= (parseFloat(getComputedStyle(el).lineHeight) || 20) * 1.5) continue;
      if (el.matches(".tip-micut") && (el.closest(".pov-card, [class*=grafic], [class*=scara], [class*=legenda]") || text.length < 40)) continue;   // etichetele graficelor nu sunt explicații
    }
    const ton = el.classList.contains("ds-rezumat") ? [...el.classList].find((k) => /^ds-rezumat-(avertisment|eroare|ok|info)$/.test(k)).slice(11) : _tonCard(el);
    if (!el.classList.contains("ds-rezumat")) {
      el.classList.add("ds-rezumat", "ds-rezumat-" + ton);
      el.dataset.dsAuto = "1";
      const sp = document.createElement("span");
      sp.className = "ds-rezumat-text";
      const mut = [...el.childNodes].filter((n) => !(n.nodeType === 1 && n.matches("button, a.buton-secundar, .ca-actiuni")));
      mut.forEach((n) => sp.appendChild(n));
      el.prepend(sp);
      el.querySelectorAll("button, a.buton-secundar").forEach((b) => { if (!b.classList.contains("buton-s")) { b.classList.add("buton-s"); b.dataset.dsAutoS = "1"; } });
    }
    const sp = el.querySelector(":scope > .ds-rezumat-text");
    if (!sp) continue;
    // textul de pe linia vizibilă: întreg dacă încape în 90 de caractere; altfel tăiat cu „…” (CSS), întreg sub „▾ detalii”
    const intreg = _txt(sp.textContent);
    sp.title = intreg;
    if (ton !== "eroare" && intreg.length > 90 && !el.querySelector(":scope > .ds-rezumat-plie")) {
      const det = document.createElement("div");
      det.className = "ds-rezumat-detalii ds-rezumat-detalii-card";
      det.hidden = true;
      el.after(det);
      const plie = document.createElement("button");
      plie.type = "button";
      plie.className = "buton-secundar ds-rezumat-plie ds-rezumat-plie-auto";   // eticheta vine din CSS: textul cardului (și al testelor care îl citesc) rămâne al ecranului
      plie.dataset.faraActiune = "plierea / arătarea detaliilor în fereastra curentă";
      plie.setAttribute("aria-expanded", "false");
      plie.setAttribute("aria-label", "detalii");
      plie.addEventListener("click", () => {
        det.hidden = !det.hidden;
        plie.setAttribute("aria-expanded", String(!det.hidden));
      });
      el.appendChild(plie);
      el.__detalii = det;
    }
    if (el.__detalii && el.__detalii.textContent !== intreg) el.__detalii.textContent = intreg;
    if (ton !== "eroare") vazute.push({ el, ton, expl: el.matches(".msg-info, .msg-ok, .msg-avert, .msg-avertisment, .msg-eroare") ? 0 : 1 });
  }
  // cel mult 2 la vedere (cardurile de eroare nu se numără); restul sub „Semnale (n)”
  const ordonate = vazute.map((v, i) => ({ ...v, i })).sort((a, b) => (a.expl - b.expl) || (_RANG[a.ton] - _RANG[b.ton]) || (a.i - b.i));   // [15.1-E5] starea / rezultatul (mesajul ecranului) înaintea explicațiilor: „Neconectat” nu intră sub „Semnale (n)”
  // un card cu acțiune (buton, legătură, câmp) nu se ascunde sub „Semnale (n)”: acțiunea (ex. „Blochează luna”, „Deschide «Emite factură»”) trebuie să rămână la îndemână
  const cuActiune = (el) => !!el.querySelector("button:not(.ds-rezumat-plie), a[href], input, select, textarea");
  const de_ascuns = new Set(ordonate.slice(2).map((v) => v.el).filter((el) => !cuActiune(el)));
  let intrerupator = corp.querySelector(".ds-semnale-sub");   // [15.1-E5] oriunde în fereastră (comutatorul stă înaintea primului card ascuns, nu neapărat sub corp): altfel se făcea unul nou la fiecare sincronizare
  for (const { el } of vazute) {
    const ascuns = de_ascuns.has(el);
    el.classList.toggle("ds-rezumat-sub", ascuns && !(intrerupator && intrerupator.getAttribute("aria-expanded") === "true"));
    el.classList.toggle("ds-rezumat-sub-grup", ascuns);
    if (el.__detalii && ascuns) el.__detalii.hidden = true;
  }
  if (de_ascuns.size) {
    if (!intrerupator) {
      intrerupator = document.createElement("button");
      intrerupator.type = "button";
      intrerupator.className = "buton-secundar buton-s ds-semnale-sub";
      intrerupator.dataset.faraActiune = "plierea / arătarea semnalelor în fereastra curentă";
      intrerupator.setAttribute("aria-expanded", "false");
      intrerupator.addEventListener("click", () => {
        const deschis = intrerupator.getAttribute("aria-expanded") !== "true";
        intrerupator.setAttribute("aria-expanded", String(deschis));
        corp.querySelectorAll(".ds-rezumat-sub-grup").forEach((x) => x.classList.toggle("ds-rezumat-sub", !deschis));
        intrerupator.textContent = intrerupator.dataset.eticheta + (deschis ? " ▴" : " ▾");
      });
      const primul = [...de_ascuns][0];
      primul.before(intrerupator);
    }
    const eticheta = `Semnale (${de_ascuns.size})`;
    if (intrerupator.dataset.eticheta !== eticheta) {
      intrerupator.dataset.eticheta = eticheta;
      intrerupator.textContent = eticheta + (intrerupator.getAttribute("aria-expanded") === "true" ? " ▴" : " ▾");
    }
  } else if (intrerupator) {
    intrerupator.remove();
  }
}

// ── [15.1-E4] lista de înregistrări → tabelul DS ───────────────────────────────────────────────────────────────────────────────────────────────────
// Listele făcute din rânduri (cu buton, cu text pe două linii) sunt înlocuite de aceeași piesă ca tabelele: `table.ds-tabel` cu cap de 40 px, rânduri de
// 44 px, zebra, subsol cu contorul de rânduri; peste 20 de rânduri, căutare de 44 px deasupra. Rândul vechi (elementul însuși, cu clasa, id-ul, clicul și
// butoanele lui) trece ca CONȚINUT al celulei, deci clicul pe rând, editarea în celulă și testele ecranului merg ca înainte. Derularea o dă navigatorul
// (zona de derulare din jurul tabelului). Idempotent: rândurile adăugate după aceea intră în același tabel.
const LISTE_ASTEA = ".pf-lista, .mig-lista, .jn-lista, .pr-lista, .firme-lista, .sa-asist-lista, .rap-col-lista, .term-grup, .zebra-lista";
const _NU_LISTA = /(card|categorie|tab\b|-tab|pastila|optiune|nav-|op-|cab-|buton|alegere|camp|rap-|ds-|bara-fixa|fj-)/i;

function _titluColoana(lista, sub) {
  const t = lista.dataset.titlu || lista.getAttribute("aria-label");
  if (t) return t;
  const cap = lista.previousElementSibling && lista.previousElementSibling.matches("h2, h3, h4, .ds-sectiune-titlu, .ds-grup-titlu") ? _txt(lista.previousElementSibling.textContent) : "";
  return cap || sub;
}

export function listeDSAplica(corp) {
  if (window.innerWidth < 900) return;   // pe telefon listele rămân cum erau
  // 1. listele cunoscute (orice număr de rânduri) și grupurile de ≥3 frați cu aceeași clasă, fiecare cu text și acțiune (ca în verificator)
  const candidate = new Set([...corp.querySelectorAll(LISTE_ASTEA)]);
  for (const p of corp.querySelectorAll("*")) {
    if (p.closest("table, .cautare-rez, select, .ds-tabel-cutie, .ds-semnale, .ds-rezumat, .ds-rezumat-detalii, template, [data-fara-piesa], .ds-grup, .ds-lista") || !_vizibilDS(p)) continue;
    const grupe = new Map();
    for (const k of p.children) { const cl = k.tagName + "." + String(k.className).split(" ")[0]; grupe.set(cl, [...(grupe.get(cl) || []), k]); }
    for (const [cl, ks] of grupe) {
      if (ks.length < 3 || _NU_LISTA.test(cl)) continue;
      const faraButoane = (k) => { const c = k.cloneNode(true); c.querySelectorAll("button, a, select, input, textarea").forEach((x) => x.remove()); return _txt(c.textContent); };
      if (ks.every((k) => k.querySelector("button, a") && faraButoane(k).length > 10 && k.getBoundingClientRect().height > 30)) candidate.add(p);   // rândul-înregistrare are text al lui, nu doar butoane (rândurile de acțiuni nu sunt liste)
    }
  }
  for (const lista of candidate) {
    if (lista.closest("template, [data-fara-piesa], .ds-tabel-cutie, table, .fereastra-antet, .ds-lista, .ds-semnale") || lista.matches(".bara-fixa")) continue;
    // rândurile cu câmpuri (bife, câmpuri de editat) sau cu mai mult de două butoane nu intră în tabel: rămân cum sunt
    if (lista.querySelector("input, select, textarea") || [...lista.children].some((r) => r.querySelectorAll("button").length > 2)) continue;
    if (lista.querySelector(":scope > .ds-tabel-cutie:not(.ds-tabel-lista), :scope > table")) continue;   // ecranul și-a desenat deja tabelul DS în listă
    let cutie = lista.querySelector(":scope > .ds-tabel-cutie.ds-tabel-lista");
    const straine = [...lista.children].filter((k) => k !== cutie && !k.matches(".ds-tabel-cauta-rand, .ds-tabel-cutie, table, .ecran-nota, .ds-rezumat, .ds-rezumat-detalii, .ds-semnale-sub, .ds-grup-titlu, h2, h3, h4, .ds-sectiune-titlu, script, style, template") && !k.hidden && k.tagName !== "P");
    if (!straine.length && !cutie) continue;
    if (!cutie) {
      if (!_vizibilDS(lista)) continue;
      cutie = document.createElement("div");
      cutie.className = "ds-tabel-cutie ds-tabel-lista";
      const t = document.createElement("table");
      t.className = "ds-tabel ds-tabel-lista-tabel";
      const th = document.createElement("th");
      th.scope = "col";
      th.textContent = _titluColoana(lista, "Înregistrare");
      t.createTHead().insertRow().appendChild(th);
      t.createTBody();
      cutie.appendChild(t);
      const sub = document.createElement("div");
      sub.className = "ds-tabel-subsol";
      cutie.appendChild(sub);
      lista.appendChild(cutie);
      // derularea e a tabelului (navigatorul pune zona în jurul lui), nu a listei: capul și subsolul rămân la vedere
      lista.classList.remove("zona-derulare");
      lista.removeAttribute("data-zona-derulare");
    }
    const corpT = cutie.querySelector("tbody");
    for (const r of straine) {
      const tr = corpT.insertRow();
      tr.className = "ds-tabel-rand-lista";
      tr.insertCell().appendChild(r);   // rândul vechi, neschimbat, devine conținutul celulei
    }
    // contorul din subsol și căutarea (peste 20 de rânduri)
    const randuri = [...corpT.rows];
    const afisate = randuri.filter((tr) => !tr.hidden && tr.style.display !== "none");
    const sub = cutie.querySelector(":scope > .ds-tabel-subsol");
    const nou = cate(afisate.length, "rând", "rânduri");
    if (sub.textContent !== nou) sub.textContent = nou;
    for (const tr of randuri) if (!tr.firstElementChild.firstElementChild) tr.remove();   // rândul pe care ecranul l-a șters din celulă
    const arataCautare = randuri.length > 20;
    let rand = lista.querySelector(":scope > .ds-tabel-cauta-rand");
    if (arataCautare && !rand && !corp.querySelector("input[type=search], input[placeholder*='Caută' i]")) {
      rand = document.createElement("div");
      rand.className = "ds-tabel-cauta-rand";
      rand.innerHTML = `<input type="search" class="camp-input ds-tabel-cauta" placeholder="Caută în listă…" aria-label="Caută în listă">`;
      cutie.before(rand);
      rand.firstElementChild.addEventListener("input", (e) => {
        const f = e.target.value.trim().toLowerCase();
        for (const tr of corpT.rows) tr.hidden = !!f && !tr.textContent.toLowerCase().includes(f);
        const n = [...corpT.rows].filter((tr) => !tr.hidden).length;
        sub.textContent = cate(n, "rând", "rânduri");
      });
    }
  }
}
