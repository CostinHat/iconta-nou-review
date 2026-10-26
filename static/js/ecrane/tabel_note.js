// tabel_note.js — TABELUL DE NOTE, o singură componentă pentru Registrul jurnal și pentru „De validat” (DS cap.9 „Tabelul de note”, v2.102).
// [lotul 12, comanda Costin 12.2 pct.9 și 12, deficiențele 617 și 622, verbatim]
//   617: „Registru jurnal: fără căutare. Un câmp (cont, document, partener, sumă, nr. crt.) și filtru de stare; tabel cu un rând pe notă,
//        detaliul la clic, explicațiile o singură dată. După «Validează» pagina sare sus fără confirmare.”
//   622: „De validat: trei forme diferite, note afișate de două ori. Trei secțiuni cu număr, același tabel ca la 617, Validează/Respinge pe
//        rând, căutare.”
// CLAUDE.md §9: „situații identice, soluții identice” — notele unei luni (jurnalul) și notele care așteaptă validarea (coada) se arată în
// ACELAȘI tabel: un rând pe notă (sau pe documentul cu notele lui, în coadă), cu numărul curent, data, explicația, documentul, conturile,
// suma și starea; acțiunea principală a stării pe rând (Validează / Respinge / Trimite din nou la validare / Refă din sursă); liniile notei
// și restul acțiunilor în detaliul care se deschide la clic pe rând (sau cu tastatura, pe butonul din prima celulă). Explicația unui semn
// din coloana Stare („fără document”, „depășită” …) stă O DATĂ, deasupra tabelului, nu pe fiecare rând (cum stătea caseta roșie a notei
// fără document, repetată pe fiecare rând). Căutarea caută în tot ce arată rândul și în liniile notei: cont, document, partener, sumă (scrisă
// „1.234,56”, „1234,56” sau „1234.56”), nr. crt., explicație, firmă.
//
// Ecranul dă rândurile deja pregătite (`randuri`), componenta le desenează, le filtrează și deschide detaliul. Ce face fiecare buton îl
// leagă ecranul (după `html`, pe elementele cu atributele lui) — componenta nu cheamă serverul, în afară de `incarcaLinii` (încărcarea
// liniilor unui rând care nu le are, la deschiderea detaliului sau la prima căutare).
import { esc, bani, dataRo, cate } from "../api.js?v=9bcf50c899";

/** Textul fără diacritice, cu litere mici — forma în care se compară căutarea. */
export function normalizeaza(x) {
  return String(x == null ? "" : x).normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase();
}

// o sumă în formele în care o poate scrie omul: „1.234,56” (cum o arată ecranul), „1234,56”, „1234.56”; „1.234” / „1234” la sume întregi
function formeSuma(v) {
  const n = Number(v);
  if (v == null || v === "" || !Number.isFinite(n)) return "";
  const b = bani(Math.abs(n));                       // „1.234,56”
  const fara = b.replace(/\./g, "");                 // „1234,56”
  const forme = [b, fara, fara.replace(",", ".")];
  if (b.endsWith(",00")) forme.push(b.slice(0, -3), fara.slice(0, -3));
  return forme.join("|");
}

/** Textul în care caută câmpul de căutare, pentru un rând: ce arată rândul, plus liniile notei (conturi, sume, parteneri). Câmpurile se
 *  despart cu „|”, ca un text căutat să nu se potrivească peste două câmpuri. */
export function textCautare(r) {
  const linii = r.linii || [];
  return normalizeaza([
    r.nrCrt != null ? `nr. crt. ${r.nrCrt}|nr ${r.nrCrt}|nr.crt.${r.nrCrt}` : "",
    r.data ? dataRo(r.data) : "", r.firma || "", r.explicatie || "", r.document || "", r.partener || "",
    (r.stare && r.stare.text) || "", (r.semne || []).map((s) => s.text).join(" "),
    formeSuma(r.rulaj), formeSuma(r.storno),
    ...linii.map((l) => `${l.debit || ""}|${l.credit || ""}|${l.debit || ""} = ${l.credit || ""}|${l.debit || ""}=${l.credit || ""}|${formeSuma(l.suma)}|${l.partener_nume || ""}|${l.partener_cui || ""}|${l.centru_nume || ""}`),
    r.cautaInPlus || "",
  ].join("|"));
}

/** Textul căutat, în forma în care se compară: fără diacritice, litere mici, spațiile strânse. */
function formaCautata(text) {
  return normalizeaza(text).replace(/\s+/g, " ").trim();
}

/** Se potrivește rândul cu textul căutat? Textul scris se caută întreg („Extras 7”, „nr. crt. 12”, „1.234,56”) într-un câmp al rândului
 *  sau al liniilor lui. Gol -> da. */
export function potriveste(r, text) {
  const t = formaCautata(text);
  return !t || textCautare(r).includes(t);
}

/** Rândul e în starea aleasă din filtru? `""` = toate. `r.stari` = cheile filtrului pe care le îndeplinește (o ciornă respinsă e și „ciorna”). */
export function inStare(r, stare) {
  return !stare || (r.stari || [(r.stare || {}).fel]).includes(stare);
}

// conturile notei, pe scurt: perechile distincte „debit = credit”, primele două, apoi „+ n”
function conturiScurt(linii) {
  if (!linii) return "";
  const perechi = [...new Set(linii.map((l) => `${l.debit || "?"} = ${l.credit || "?"}`))];
  return perechi.slice(0, 2).join(", ") + (perechi.length > 2 ? ` + ${perechi.length - 2}` : "");
}

/** Rulajul unui set de linii: partea înregistrată (sume pozitive) și stornarea (sumele cu minus, în valoare absolută). */
export function rulajLinii(linii) {
  let rulaj = 0, storno = 0;
  (linii || []).forEach((l) => { const s = Number(l.suma) || 0; if (s < 0) storno -= s; else rulaj += s; });
  return { rulaj, storno };
}

function celulaSuma(r) {
  const st = Number(r.storno) || 0, rj = Number(r.rulaj) || 0;
  if (st && !rj) return `−${bani(st)}`;
  return `${bani(rj)}${st ? `<div class="tip-desc">stornare −${bani(st)}</div>` : ""}`;
}

/** Tabelul liniilor unei note (în detaliu): debit, credit, sumă, partener, centru de cost — aceeași formă în jurnal și în coadă. */
export function tabelLinii(linii) {
  if (!linii || !linii.length) return `<p class="ecran-nota">Nota n-are linii.</p>`;
  const cuPartener = linii.some((l) => l.partener_nume || l.partener_cui), cuCentru = linii.some((l) => l.centru_nume);
  // un document cu mai multe note (contarea și ieșirea din stoc a aceleiași facturi): nota fiecărei linii, în prima coloană
  const cuNota = new Set(linii.map((l) => l.nota).filter(Boolean)).size > 1;
  return `<table class="fd-tabel tn-linii"><thead><tr>${cuNota ? "<th>Nota</th>" : ""}<th>Debit</th><th>Credit</th><th class="fd-td-num">Sumă (lei)</th>${cuPartener ? "<th>Partener</th>" : ""}${cuCentru ? "<th>Centru de cost</th>" : ""}</tr></thead>
    <tbody>${linii.map((l) => `<tr>${cuNota ? `<td>${esc(l.nota || "")}</td>` : ""}<td>${esc(l.debit)}</td><td>${esc(l.credit)}</td><td class="fd-td-num">${bani(l.suma)}</td>${cuPartener ? `<td>${esc(l.partener_nume || l.partener_cui || "")}</td>` : ""}${cuCentru ? `<td>${esc(l.centru_nume || "")}</td>` : ""}</tr>`).join("")}</tbody></table>`;
}

/** Explicațiile semnelor prezente, o singură dată: `explicatii` = {cheie: {text, atentie}}; numai semnele care apar pe rânduri. */
function htmlExplicatii(pre, randuri, explicatii) {
  const nr = {};
  randuri.forEach((r) => (r.semne || []).forEach((s) => { nr[s.fel] = (nr[s.fel] || 0) + 1; }));
  const chei = Object.keys(explicatii || {}).filter((k) => nr[k]);
  if (!chei.length) return "";
  const rand = (k) => `<div class="${explicatii[k].atentie ? "ca-mesaj" : "ci-mesaj"} tn-explicatie" id="${pre}-expl-${k}"><b>${esc(explicatii[k].titlu)} (${nr[k]}):</b> ${esc(explicatii[k].text)}</div>`;
  const at = chei.filter((k) => explicatii[k].atentie), inf = chei.filter((k) => !explicatii[k].atentie);
  return `<div class="tn-explicatii" id="${pre}-explicatii">${at.length ? `<div class="caseta-atentie">${at.map(rand).join("")}</div>` : ""}${inf.length ? `<div class="caseta-info">${inf.map(rand).join("")}</div>` : ""}</div>`;
}

/** HTML-ul tabelului. `opt`: {pre, randuri, nrCrt (coloana Nr. crt.), firma (coloana Firma), explicatii, gol, deschise (Set de chei)}.
 *  Rândul: {cheie, atribute (obiect -> data-* pe <tbody>), nrCrt, data, firma, explicatie, document, partener, linii, rulaj, storno,
 *  stare: {fel, text, culoare}, stari, semne: [{fel, text}], inainte (HTML în prima celulă, ex. bifa), actiuni (HTML, pe rând),
 *  detaliu (HTML: mesajele și acțiunile de sub linii), editor (HTML: înlocuiește detaliul, deschis), clasa (pe <tbody>)}. */
export function htmlTabelNote(opt) {
  const { pre, randuri = [], nrCrt = false, firma = false, explicatii = {}, gol = "Nicio notă." } = opt;
  const deschise = opt.deschise || new Set();
  if (!randuri.length) return `<div class="stare-goala" id="${pre}-gol">${esc(gol)}</div>`;
  const nCol = 7 + (nrCrt ? 1 : 0) + (firma ? 1 : 0);
  const corp = randuri.map((r) => {
    const k = esc(String(r.cheie));
    const deschis = !!r.editor || deschise.has(String(r.cheie));
    const atr = Object.entries(r.atribute || {}).map(([a, v]) => ` data-${a}="${esc(String(v))}"`).join("");
    const stare = r.stare || {};
    const semne = (r.semne || []).map((s) => `<div class="tip-desc tn-semn" data-semn="${esc(s.fel)}">${esc(s.text)}</div>`).join("");
    // prima celulă: nr. crt. (jurnalul; ciorna n-are încă număr: „—”) sau data (coada) — butonul care deschide detaliul
    const eticheta = nrCrt ? (r.nrCrt != null ? esc(String(r.nrCrt)) : "—") : dataRo(r.data);
    const deschide = `<button type="button" class="btn-link tn-deschide" aria-expanded="${deschis}" aria-controls="${pre}-det-${k}" aria-label="Detaliul notei din ${dataRo(r.data)}: liniile și restul acțiunilor">${eticheta}</button>`;
    const linii = r.linii ? tabelLinii(r.linii) : `<div class="tn-linii-loc"><p class="ecran-nota">Se încarcă liniile notei…</p></div>`;
    return `<tbody class="tn-nota${r.clasa ? " " + r.clasa : ""}"${atr} data-tn="${k}">
      <tr class="tn-rand${deschis ? " tn-deschis" : ""}">
        <td>${r.inainte || ""}${deschide}</td>${nrCrt ? `<td>${dataRo(r.data)}</td>` : ""}
        ${firma ? `<td>${esc(r.firma || "")}</td>` : ""}
        <td>${esc(r.explicatie || "fără explicație")}</td>
        <td>${r.document ? esc(r.document) : `<span class="tip-desc">fără document</span>`}</td>
        <td>${esc(conturiScurt(r.linii))}</td>
        <td class="fd-td-num">${celulaSuma(r)}</td>
        <td><span style="color:${stare.culoare || "var(--ardezie)"};font-weight:600">● ${esc(stare.text || "")}</span>${semne}</td>
        <td class="tn-actiuni">${r.actiuni || ""}</td>
      </tr>
      <tr class="tn-detaliu" id="${pre}-det-${k}"${deschis ? "" : " hidden"}><td colspan="${nCol}">${r.editor || `${linii}${r.detaliu || ""}`}</td></tr>
    </tbody>`;
  }).join("");
  return `${htmlExplicatii(pre, randuri, explicatii)}
    <table class="fd-tabel tn-tabel" id="${pre}-tabel">
      <thead><tr><th>${nrCrt ? "Nr. crt." : "Data"}</th>${nrCrt ? "<th>Data</th>" : ""}${firma ? "<th>Firma</th>" : ""}<th>Explicație</th><th>Document</th><th>Conturi</th><th class="fd-td-num">Sumă (lei)</th><th>Stare</th><th>Acțiune</th></tr></thead>
      ${corp}
    </table>
    <div class="stare-goala" id="${pre}-nimic" hidden>Nicio notă nu se potrivește căutării. Schimbă textul căutat sau starea aleasă.</div>`;
}

// [lotul 12, găsită la integrare] deschiderea detaliului unui rând legat (`comuta(tb, true)`): liniile se încarcă și cheia intră în
// `deschise` (redesenarea îl lasă deschis). `locInDetaliu` o cere de aici, ca deschiderea de la o întrebare să fie aceeași cu clicul pe rând.
const _deschideri = new WeakMap();

/** Leagă tabelul desenat în `zona`: clic pe rând (în afara butoanelor) sau pe butonul din prima celulă -> detaliul; `incarcaLinii(r)` ->
 *  liniile rândului care nu le are (o singură dată). Întoarce {filtreaza(text, stare) -> {vazute, total}, incarcaToateLiniile()}. */
export function legaTabelNote(zona, opt) {
  const { pre, randuri = [] } = opt;
  const deschise = opt.deschise || new Set();
  const dupaCheie = new Map(randuri.map((r) => [String(r.cheie), r]));
  const incarcate = new Map();   // cheie -> promisiunea liniilor
  const linii = (r) => {
    if (r.linii || !opt.incarcaLinii) return Promise.resolve(r.linii || []);
    if (!incarcate.has(String(r.cheie))) {
      incarcate.set(String(r.cheie), opt.incarcaLinii(r).then((l) => { r.linii = l || []; return r.linii; }).catch(() => null));
    }
    return incarcate.get(String(r.cheie));
  };
  const umple = async (tb, r) => {
    const loc = tb.querySelector(".tn-linii-loc");
    if (!loc) return;
    const l = await linii(r);
    if (!loc.isConnected) return;
    loc.outerHTML = l == null ? `<p class="ecran-nota">Liniile notei nu s-au putut încărca. Închide și deschide din nou rândul.</p>` : tabelLinii(l);
    const td = tb.querySelector(`.tn-rand td:nth-child(${(opt.nrCrt ? 1 : 0) + (opt.firma ? 1 : 0) + 4})`);
    if (td && l) td.textContent = conturiScurt(l);
  };
  const comuta = (tb, deschide) => {
    const r = dupaCheie.get(tb.dataset.tn);
    const det = tb.querySelector(".tn-detaliu"), b = tb.querySelector(".tn-deschide"), rand = tb.querySelector(".tn-rand");
    if (!det || !r) return;
    const da = deschide == null ? det.hidden : deschide;
    det.hidden = !da;
    rand.classList.toggle("tn-deschis", da);
    if (b) b.setAttribute("aria-expanded", String(da));
    if (da) { deschise.add(tb.dataset.tn); umple(tb, r); } else deschise.delete(tb.dataset.tn);
  };
  zona.querySelectorAll("tbody.tn-nota").forEach((tb) => {
    const rand = tb.querySelector(".tn-rand");
    if (!rand) return;
    rand.addEventListener("click", (ev) => {
      if (ev.target.closest("button:not(.tn-deschide), a, input, select, textarea, label, details")) return;   // acțiunile rândului
      comuta(tb);
    });
    if (!tb.querySelector(".tn-detaliu").hidden) umple(tb, dupaCheie.get(tb.dataset.tn));
    _deschideri.set(tb, () => comuta(tb, true));
  });
  const nimic = zona.querySelector(`#${pre}-nimic`), tabel = zona.querySelector(`#${pre}-tabel`);
  return {
    async incarcaToateLiniile() { await Promise.all(randuri.map(linii)); },
    filtreaza(text, stare) {
      let vazute = 0;
      zona.querySelectorAll("tbody.tn-nota").forEach((tb) => {
        const r = dupaCheie.get(tb.dataset.tn);
        const da = !!r && potriveste(r, text) && inStare(r, stare);
        tb.hidden = !da;
        if (da) vazute++;
      });
      if (nimic) nimic.hidden = vazute > 0 || !randuri.length;
      if (tabel) tabel.hidden = vazute === 0;
      return { vazute, total: randuri.length };
    },
    deschide(cheie) { const tb = zona.querySelector(`tbody.tn-nota[data-tn="${CSS.escape(String(cheie))}"]`); if (tb) comuta(tb, true); return tb; },
  };
}

/** Locul din detaliul rândului unde se pune o întrebare de confirmare (`confirmaCaseta(loc, …)` o inserează DUPĂ el): ultimul element
 *  din detaliu, cu detaliul deschis — pe drumul clicului pe rând (liniile încărcate, rândul ținut deschis la redesenare), nu numai arătat:
 *  deschis direct, detaliul rămânea pe „Se încarcă liniile notei…” și se închidea la redesenare. O casetă pusă lângă butonul din celulă
 *  ar intra între celulele rândului. */
export function locInDetaliu(buton) {
  const tb = buton && buton.closest && buton.closest("tbody.tn-nota");
  if (!tb) return (buton && buton.parentElement) || buton;
  const det = tb.querySelector(".tn-detaliu"), td = det && det.querySelector(":scope > td");
  if (!td) return buton.parentElement || buton;
  if (det.hidden) {
    const deschide = _deschideri.get(tb);
    if (deschide) deschide(); else det.hidden = false;   // un tabel nelegat (fără `legaTabelNote`): numai arătat, ca întrebarea să se vadă
  }
  let ultim = td.lastElementChild;
  if (!ultim) { ultim = document.createElement("div"); td.appendChild(ultim); }
  return ultim;
}

/** Câmpul de căutare și filtrul de stare (în rezumatul lipit sus). `stari` = [[cheie, eticheta]] (fără filtru: căutarea singură). */
export function htmlCautare(pre, { stari = null, valoare = "", stare = "", eticheta = "Caută: cont, document, partener, sumă, nr. crt." } = {}) {
  return `<span class="tn-cautare">
    <input type="search" id="${pre}-cauta" class="camp-input" style="max-width:340px" placeholder="${esc(eticheta)}" aria-label="${esc(eticheta)}" autocomplete="off" value="${esc(valoare)}">
    ${stari ? `<select id="${pre}-stare" class="camp-input" style="max-width:220px" aria-label="Starea notelor arătate">${stari.map(([k, e]) => `<option value="${esc(k)}"${k === stare ? " selected" : ""}>${esc(e)}</option>`).join("")}</select>` : ""}
    <span class="tip-desc" id="${pre}-numar" aria-live="polite"></span></span>`;
}

/** Textul de lângă căutare: „12 note” sau „3 din 12 note”. */
export function textNumar(vazute, total, singular = "notă", plural = "note") {
  return vazute === total ? cate(total, singular, plural) : `${vazute} din ${cate(total, singular, plural)}`;
}
