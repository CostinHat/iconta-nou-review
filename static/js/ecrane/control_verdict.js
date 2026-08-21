// control_verdict.js — renderer UNIC al corpului verdictului de control fiscal.
// Sursa unica pentru DETALIU (control.js) si cardul din fisa firmei (firme.js): acelasi payload
// (/control-fiscal/{id}), aceleasi sectiuni, aceleasi chei. Inainte existau trei renderere divergente,
// fiecare cu alt subset hardcodat de chei din verificari_contabile -> constatari BLOCANTE invizibile pe
// unele ecrane (cazul DANTE 24.07: cele 4 rosii pe salarii nu apareau pe cardul din fisa).
// Regula DS cap.20: sectiunile pot diferi intre ecrane, cheile dintr-o sectiune randata NU. Garda
// VERDICT_PARITATE (verificator) impune paritatea prin inventarul declarat VC_RANDATE de mai jos.
import { api, esc, dataRo, confirmaCaseta, arataMesaj, bani } from "../api.js?v=a7f9e80ae0";

// Paleta de semafor UNICA (inlocuieste control.js CULORI + firme.js _CF_CUL — erau doua copii divergente).
export const CULORI = {
  verde:  { dot:"radial-gradient(circle at 65% 30%, #6fc494, var(--verde) 60%)", txt:"la zi",       bg:"var(--verde-fundal)" },
  galben: { dot:"radial-gradient(circle at 65% 30%, #f0cd7a, var(--galben) 60%)", txt:"de urmărit",  bg:"var(--galben-fundal)" },
  rosu:   { dot:"radial-gradient(circle at 65% 30%, #ff8a80, var(--rosu-semafor) 60%)", txt:"restanță", bg:"var(--rosu-fundal)" },
  gri:    { dot:"var(--gri-semafor)", txt:"nu se poate verifica", bg:"var(--gri-fundal-semafor)" },
};

// INVENTAR DECLARAT — paritatea 1 (RANDARE). Fiecare cheie din payload-ul `verificari_contabile` (vc)
// trebuie sa aiba aici o destinatie: o sectiune randata, sau "via d.contabil", sau marcata contor. O cheie
// noua produsa de backend fara intrare aici = EROARE in verificator (VERDICT_PARITATE, sub-regula randare),
// nu omisiune tacuta. Sursa cheilor produse: dict-ul `rezultat` din _verificari_contabile (main.py). Cap.20.
export const VC_RANDATE = {
  tva_incrucisat:        "Declarație vs contabilitate",
  d112_incrucisat:       "Declarație vs contabilitate",
  d390_incrucisat:       "Declarație vs contabilitate",
  cota_tva_conformitate: "Conformitate facturi emise",
  tva:                   "Coerență TVA (balanță)",
  documente_pozate:      "Documente pozate",
  echilibru:             "via d.contabil — Verificări contabile",
  trezorerie:            "via d.contabil — Verificări contabile",
  note:                  "__contor__ (numar de note, nu constatare)",
};

// [eticheta_din_fapt 20.08.2026] Textul pastilei se leaga de FAPT, nu de culoare. `CULORI[x].txt` era
// un dictionar indexat pe culoare: griul afisa mereu "vector necompletat", inclusiv pe firme al caror
// vector e COMPLET (masurat pe Startup Partial 2026 si Trecere Micro Profit - niciun camp NULL).
// Griul are patru cauze acum (necunoastere, absenta de observatie, vector incomplet, existenta firmei),
// deci o eticheta fixa e falsa in trei cazuri din patru.
// NU alegem o "cauza dominanta": ordinea ar fi arbitrara, iar contabilul ar vedea o cauza si ar crede
// ca e singura. Afisam NUMARUL, exact ca la rosu ("3 restante") si galben ("2 de urmarit"); cauzele,
// toate, sunt in ecranul de detaliu. Un numar nu minte si nu alege.
export function etichetaStare(stare, n_neverificabile) {
  const col = CULORI[stare] || CULORI.gri;
  if (stare !== "gri") return col.txt;
  const n = Number(n_neverificabile || 0);
  if (!n) return col.txt;                       // gri fara numar (ex. eroare de evaluare) -> generic
  return `${n} ${n === 1 ? "nu se poate verifica" : "nu se pot verifica"}`;
}

// anatomie constatare (dot + mesaj + temei + remediu) — renderer unic pt «Verificari contabile» si audit.
function randA(c) {
  const dot = CULORI[c.stare] ? CULORI[c.stare].dot : CULORI.gri.dot;
  const r = c.remediu;
  const extra = r ? `<div class="cf-incr-remediu"><b>${esc(r.cauza || "")}</b><br>${esc(r.actiune || "")}</div>` : "";
  return `<div class="cf-incr-rand">
    <div class="cf-incr-cap"><span class="cf-dot" style="background:${dot}"></span><span>${esc(c.mesaj || "")}</span></div>
    <div class="cf-incr-temei">${esc(c.temei || "")}</div>
    ${extra}
  </div>`;
}

// anatomie constatare cu remediu EXECUTABIL (buton «Contabilizeaza facturile») — pt cross-check-uri.
function randConst(c) {
  const dot = CULORI[c.stare] ? CULORI[c.stare].dot : CULORI.gri.dot;
  let extra = "";
  if (c.remediu) {
    const r = c.remediu;
    const buton = (r.fel === "executabil" && (r.facturi || []).length)
      ? `<button class="buton-secundar cf-incr-btn" data-facturi="${esc((r.facturi || []).join(","))}" style="margin-top:8px">Contabilizează facturile</button>` : "";
    extra = `<div class="cf-incr-remediu"><b>${esc(r.cauza || "")}</b><br>${esc(r.actiune || "")}${buton ? `<div>${buton}</div>` : ""}</div>`;
  }
  return `<div class="cf-incr-rand">
    <div class="cf-incr-cap"><span class="cf-dot" style="background:${dot}"></span><span>${esc(c.mesaj || "")}</span></div>
    <div class="cf-incr-temei">${esc(c.temei || "")}</div>
    ${extra}
  </div>`;
}

// rand de declaratie cu termen (Restante / De urmarit / La zi) — poarta MOTIVUL pe orice culoare.
function randDecl(arr, clasa) {
  return arr.map((x) => `
    <div class="cf-decl-item">
      <div class="mig-sold-rand cf-rand-decl">
        <span class="mig-sold-cont">${esc((x.tip || "").toUpperCase())}</span>
        <span class="cf-perioada">${esc(x.perioada || "")}</span>
        <span class="cf-termen ${clasa}">termen ${dataRo(x.termen)}</span>
      </div>
      ${x.motiv ? `<div class="cf-incr-temei">${esc(x.motiv)}</div>` : ""}
    </div>`).join("");
}
// rand de declaratie fara termen (Nu pot verifica / Nu se datoreaza) — doar tip + motiv.
// [R6 21.08.2026] Un motiv poate primi un SEMNAL: o depunere care îl pune la îndoială. Varianta (b),
// decisă de Costin: fiecare semnal stă lângă afirmația pe care o contrazice, nu într-un grup propriu —
// contradicția (defect al NOSTRU) și opinia (informație) cer lucruri diferite de la contabil.
// Semnalele care nu-și găsesc perechea NU dispar: se randează la coada grupului. Un semnal pierdut
// tăcut ar fi exact clasa de defect pe care mecanismul ăsta o vânează.
// [P3 21.08.2026] Domeniul unei afirmații, în limba contabilului. Felul NU se tipărește — contabilul
// n-are ce face cu „absenta_observatie" — dar își face treaba: decide CE se poate scrie ca perioadă.
// Oglinda lui `core/afirmatii.domeniu_text`; dacă afirmația n-are domeniu prin natura ei (`statut`),
// nu se inventează unul. Efectul care a cerut-o: D300 apărea și în «De urmărit · iul», și în «Nu pot
// verifica» fără nicio perioadă, deci cele două păreau să se contrazică deși vorbeau de luni diferite.
// „2025-12" -> „12.2025": acelasi registru ca restul ecranului (termene, blocaje), nu ISO. Vazut
// privind captura: „din 2025-12" statea langa „iul" in aceeasi lista, doua formate pentru acelasi fel
// de lucru.
const _luniAn = (s) => (/^\d{4}-\d{2}$/.test(s || "") ? `${s.slice(5)}.${s.slice(0, 4)}` : (s || ""));

function domeniuAfirmatie(x) {
  if (x.fel === "fapt") return x.luna ? `${String(x.luna).padStart(2, "0")}.${x.an}` : String(x.an || "");
  if (x.fel === "necunoastere") {
    const de = _luniAn(x.domeniu_de), pana = _luniAn(x.domeniu_pana);
    if (de && pana) return de === pana ? de : `${de} – ${pana}`;
    return de ? `din ${de}` : "";
  }
  return "";
}

function randMotiv(arr, semnale = [], felCls = "") {
  const folosite = new Set();
  const potrivite = (x) => semnale.filter((s, i) => {
    const acelasiTip = s.tip === x.tip;
    const acelasiInterval = x.an == null || (s.an === x.an && s.luna === x.luna);
    if (acelasiTip && acelasiInterval) { folosite.add(i); return true; }
    return false;
  });
  const randSemnal = (s) => `<div class="cf-semnal ${felCls}">${esc(s.mesaj || "")}</div>`;
  const corp = arr.map((x) => `
    <div class="cf-decl-item">
      <div class="cf-incr-cap"><span class="mig-sold-cont">${esc((x.tip || "").toUpperCase())}</span>${
        domeniuAfirmatie(x) ? `<span class="cf-perioada">${esc(domeniuAfirmatie(x))}</span>` : ""}</div>
      <div class="cf-incr-temei">${esc(x.motiv || "")}</div>
      ${x.surse_consultate ? `<div class="cf-incr-temei">Căutat în: ${esc(x.surse_consultate)}</div>` : ""}
      ${x.temei_completitudine ? `<div class="cf-incr-temei">Pe ce se sprijină: ${esc(x.temei_completitudine)}</div>` : ""}
      ${potrivite(x).map(randSemnal).join("")}
    </div>`).join("");
  const orfane = semnale.filter((_, i) => !folosite.has(i));
  return corp + (orfane.length
    ? `<div class="cf-decl-item">${orfane.map(randSemnal).join("")}</div>` : "");
}
// verificare booleana (echilibru/tva/documente) — dot verde/rosu dupa .ok.
function randVerif(eticheta, ok, detaliu) {
  return `<div class="cf-verif">
    <span class="cf-verif-dot" style="background:${ok ? "var(--verde)" : "var(--rosu-semafor)"}"></span>
    <span class="cf-verif-txt">${eticheta}${detaliu ? ` <span class="tip-micut">${detaliu}</span>` : ""}</span>
  </div>`;
}

const RANG = { rosu: 3, galben: 2, gri: 1, verde: 0 };
// etichetele constatarilor incrucisate care apar deja in «Declaratie vs contabilitate» -> filtrate din
// «Verificari contabile» ca sa nu se dubleze (sumarul lor e in contabil, constatarea intreaga e in incrucisat).
const DEJA_IN_INCRUCISAT = ["TVA declarat diferă de contabilitate", "Salarii declarate diferă de contabilitate",
  "Operațiuni intracomunitare declarate diferă de evidență", "Facturi emise cu cotă TVA greșită pentru perioadă"];

// RENDERER UNIC al corpului. Primeste payload-ul d de la /control-fiscal/{id}. Sectiunile difera de la ecran
// la ecran doar prin ce anteta/pastila pune APELANTUL deasupra; corpul (constatarile) e IDENTIC. opt.mod e
// rezervat pentru diferente cosmetice viitoare, NU pentru a ascunde constatari.
export function randeazaCorpVerdict(d, opt = {}) {
  const vc = d.verificari_contabile || {};
  // [C4, decizie 23.07] restantele: lista plata (fara grupare pe tip), sortata pe vechimea depasirii
  // termenului (cel mai vechi intai; ISO -> sort lexical). Acelasi criteriu pe ambele ecrane, prin renderer.
  const lipsa = (d.lipsa || []).slice().sort((a, b) => (a.termen || "").localeCompare(b.termen || ""));
  const urmarit = (d.urmarit || []).slice().sort((a, b) => (a.termen || "").localeCompare(b.termen || ""));
  const confirmate = d.confirmate || [];
  // [DESIGN_SYSTEM cap.8 — semafor: ordine roșu→galben→verde + tokeni de culoare] «La zi» (verde) =
  // depus LA termen. O depunere DUPĂ termen nu e verde, dar nici restanță (roșu) -> categorie proprie
  // (chihlimbar/galben), informativă. NU urcă pastila firmei (control_fiscal_api._stare neatins).
  const cu_intarziere = d.cu_intarziere || [];
  const neclar = d.neclar || [];
  const neaplicabile = d.neaplicabile || [];
  // [R6] depuneri fara obligatie pereche: „contrazice" langa «Nu se datoreaza», „opinie" langa
  // «Nu pot verifica». NU urca pastila (control_fiscal_api._stare neatins): rosul pastilei inseamna
  // „ai restante"; o incoerenta de verdict e un defect al nostru, nu o datorie a firmei.
  const semnale = d.depuneri_fara_obligatie || [];
  const contraziceri = semnale.filter((x) => x.fel === "contrazice");
  const opinii = semnale.filter((x) => x.fel === "opinie");

  const declaratii = `
    ${lipsa.length ? `<div class="cf-grup-titlu cf-rosu">Restanțe (${lipsa.length})</div><div class="cf-decl">${randDecl(lipsa, "cf-termen-rosu")}</div>` : ""}
    ${urmarit.length ? `<div class="cf-grup-titlu cf-galben">De urmărit (${urmarit.length})</div><div class="cf-decl">${randDecl(urmarit, "cf-termen-galben")}</div>` : ""}
    ${neclar.length || opinii.length ? `<div class="cf-grup-titlu">Nu pot verifica (${neclar.length})</div><div class="cf-decl">${randMotiv(neclar, opinii, "cf-semnal-opinie")}</div>` : ""}
    ${neaplicabile.length || contraziceri.length ? `<div class="cf-grup-titlu">Nu se datorează (${neaplicabile.length})</div><div class="cf-decl">${randMotiv(neaplicabile, contraziceri, "cf-semnal-contra")}</div>` : ""}
    ${cu_intarziere.length ? `<div class="cf-grup-titlu cf-galben">Depuse cu întârziere (${cu_intarziere.length})</div><div class="cf-decl">${randDecl(cu_intarziere, "cf-termen-galben")}</div>` : ""}
    ${confirmate.length ? `<div class="cf-grup-titlu cf-verde">La zi (${confirmate.length})</div><div class="cf-decl">${randDecl(confirmate, "cf-termen-verde")}</div>` : ""}`;

  // «Declaratie vs contabilitate» — vc.tva_incrucisat/d112_incrucisat/d390_incrucisat (aceeasi anatomie).
  const sectIncrucisat = (() => {
    const verificatori = [vc.tva_incrucisat, vc.d112_incrucisat, vc.d390_incrucisat].filter(Boolean);
    const cuFinding = verificatori.filter((v) => (v.constatari || []).length);
    if (!cuFinding.length) return "";
    const worst = cuFinding.reduce((m, v) => ((RANG[v.stare] || 0) > (RANG[m] || 0) ? v.stare : m), "verde");
    const cls = worst === "rosu" ? "cf-rosu" : (worst === "galben" ? "cf-galben" : "");
    const blocuri = cuFinding.map((v) => (v.constatari || []).map(randConst).join("")
      + (v.limita ? `<div class="cf-incr-temei">${esc(v.limita)}</div>` : "")).join("");
    return `<div class="cf-grup-titlu ${cls}">Declarație vs contabilitate</div><div class="cf-decl">${blocuri}</div>`;
  })();

  // «Conformitate facturi emise» — vc.cota_tva_conformitate.
  const sectCota = (() => {
    const cf = vc.cota_tva_conformitate;
    if (!cf || !(cf.constatari || []).length) return "";
    const cls = cf.stare === "rosu" ? "cf-rosu" : "";
    const randuri = (cf.constatari || []).map(randConst).join("");
    const limita = cf.limita ? `<div class="cf-incr-temei">${esc(cf.limita)}</div>` : "";
    return `<div class="cf-grup-titlu ${cls}">Conformitate facturi emise</div><div class="cf-decl">${randuri}${limita}</div>`;
  })();

  // «Coerenta TVA (balanta)» — vc.tva (coerenta bruta 4427/4426; distincta de tva_incrucisat = D300 vs contab).
  const sectTva = (() => {
    const t = vc.tva;
    if (!t) return "";
    const ok = (t.suma === 0 || !!t.rezultat);
    const det = `${t.rezultat === "de_plata" ? "de plată" : (t.rezultat === "de_recuperat" ? "de recuperat" : "")} ${bani(t.suma || 0)} lei`;
    return `<div class="cf-grup-titlu">Coerență TVA (balanță)</div><div class="cf-decl">${randVerif("TVA vs sold balanță", ok, det)}</div>`;
  })();

  // «Documente pozate» — vc.documente_pozate (bonuri/note de casa confirmate de client, necontate).
  const sectDocumente = (() => {
    const dp = vc.documente_pozate;
    if (!dp) return "";
    const det = dp.ok ? "" : (dp.bonuri_neverificate ? `${dp.bonuri_neverificate} neverificate` : "");
    return `<div class="cf-grup-titlu">Documente pozate</div><div class="cf-decl">${randVerif("Documente confirmate de client, contate", dp.ok, det)}</div>`;
  })();

  // «Verificari contabile» — d.contabil (echilibru, trezorerie, stocuri, Intrastat, regim TVA + sumar incrucisat).
  const sectContabil = (() => {
    const items = (d.contabil || []).filter((c) => c && typeof c === "object" && !DEJA_IN_INCRUCISAT.includes(c.eticheta));
    if (!items.length) return "";
    const worst = items.reduce((m, c) => ((RANG[c.stare] || 0) > (RANG[m] || 0) ? c.stare : m), "verde");
    const cls = worst === "rosu" ? "cf-rosu" : (worst === "galben" ? "cf-galben" : "");
    return `<div class="cf-grup-titlu ${cls}">Verificări contabile (${items.length})</div><div class="cf-decl">${items.map(randA).join("")}</div>`;
  })();

  const gata = d.stare === "verde" ? `
    <div class="mig-gata" style="padding:30px 0">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">Totul depus la zi</div>
    </div>` : "";

  const audit = `
    <div class="cf-grup-titlu" style="margin-top:20px">Audit de preluare</div>
    <div class="cf-decl" id="cf-audit-zona">
      <div class="cf-incr-temei">Coerența internă a pachetului preluat de la contabilul anterior: balanță, solduri parteneri, istoric declarații, registru PFA. Raport datat, repetabil pe măsură ce apar documentele.</div>
      <button class="buton-secundar" id="cf-audit-run" style="margin-top:10px">Rulează auditul de preluare</button>
    </div>`;

  // [P4, DS cap.25.4] „Ce nu poate spune verificarea asta" — despre CAPACITATE, nu despre date.
  // PERMANENTĂ: dacă ar apărea doar câteodată, prezența ei ar deveni semnal și absența ei ar minți.
  // Necolorată (nu e o problemă de rezolvat), jos (nu e alarmă), compactă cu detaliul la extindere
  // (nu într-un „?", care dispare exact pentru cine ar avea nevoie).
  const sectLimite = (() => {
    const lim = d.limite || [];
    if (!lim.length) return "";
    const per = lim.find((x) => x.fel === "perimetru");
    const rest = lim.filter((x) => x !== per);
    return `<div class="cf-grup-titlu" style="margin-top:20px">Ce nu poate spune verificarea asta</div>
      <div class="cf-decl"><details class="cf-limite">
        <summary class="cf-incr-temei">${esc(per ? per.text : "Ce am privit și ce nu.")}
          <span class="tip-micut">(vezi toate limitele: ${rest.length})</span></summary>
        ${rest.map((x) => `<div class="cf-incr-temei">${esc(x.text)}</div>`).join("")}
      </details></div>`;
  })();

  return declaratii + sectIncrucisat + sectCota + sectTva + sectDocumente + sectContabil + gata
       + sectLimite + audit;
}

// Leaga evenimentele corpului dupa inserare (butoane remediu executabil + audit de preluare on-demand).
// firma: { tenant_id, nume, reincarca? } — reincarca() e apelat dupa contabilizarea reusita, ca sa se
// re-evalueze verdictul (constatarea trece pe verde). Fiecare apelant isi da propriul reincarca.
export function legaVerdict(corp, nav, firma) {
  corp.querySelectorAll(".cf-incr-btn").forEach((b) => b.addEventListener("click", () => {
    const ids = (b.dataset.facturi || "").split(",").filter(Boolean);
    if (!ids.length) return;
    confirmaCaseta(b.parentElement, `Se creează ${ids.length} note contabile ciornă. Continui?`, async () => {
      b.disabled = true;
      b.textContent = "Se contabilizează…";
      let ok = 0;
      const err = [];
      for (const id of ids) {
        try { await api.post(`/tenants/${firma.tenant_id}/facturi/${id}/contabilizeaza`, {}); ok++; }
        catch (e) { err.push(`${id}: ${e.mesaj || e.message}`); }
      }
      if (err.length) {
        b.disabled = false;
        b.textContent = "Contabilizează facturile";
        arataMesaj(b.parentElement, `${ok} contabilizate. Erori: ${err.join("; ")}`, "avert");
      } else if (typeof firma.reincarca === "function") {
        firma.reincarca();
      }
    }, { textOk: "Contabilizează" });
  }));

  async function ruleazaAudit() {
    const zona = corp.querySelector("#cf-audit-zona");
    const btn = corp.querySelector("#cf-audit-run");
    if (btn) { btn.disabled = true; btn.textContent = "Se rulează…"; }
    let a;
    try {
      a = await api.get(`/control-fiscal/${firma.tenant_id}/audit-preluare`);
    } catch (e) {
      if (btn) { btn.disabled = false; btn.textContent = "Rulează auditul de preluare"; }
      arataMesaj(zona, `Nu am putut rula auditul: ${e.mesaj || e.message}`, "avert");
      return;
    }
    const grup = (titlu, stare, cls) => {
      const arr = (a.constatari || []).filter((c) => c.stare === stare);
      if (!arr.length) return "";
      return `<div class="cf-grup-titlu ${cls}">${titlu} (${arr.length})</div>${arr.map(randA).join("")}`;
    };
    const col = CULORI[a.stare] || CULORI.gri;
    zona.innerHTML = `
      <div class="cf-incr-temei">${a.in_iconta_din ? `Firmă în iConta.eu din ${dataRo(a.in_iconta_din)} · ` : ""}Audit rulat ${dataRo(a.data, "cu_ora")} · <span style="color:${col.dot}">${col.txt}</span> · ${a.coerent} coerent · ${a.divergent} divergent · ${a.neverificat} neverificat</div>
      ${grup("Coerent", "verde", "cf-verde")}
      ${grup("Divergent", "rosu", "cf-rosu")}
      ${grup("Neverificat", "gri", "")}
      ${a.limita ? `<div class="cf-incr-temei">${esc(a.limita)}</div>` : ""}
      <button class="buton-secundar" id="cf-audit-run" style="margin-top:12px">Rerulează auditul</button>`;
    corp.querySelector("#cf-audit-run").addEventListener("click", ruleazaAudit);
  }
  const auditBtn = corp.querySelector("#cf-audit-run");
  if (auditBtn) auditBtn.addEventListener("click", ruleazaAudit);
}
