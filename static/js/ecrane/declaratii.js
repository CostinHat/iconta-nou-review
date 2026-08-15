// declaratii.js — ecran asistent: creeaza o declaratie -> trimite in coada de validare.
// Flux 3 pasi intr-o fereastra: 1) firma+tip+perioada  2) genereaza+verifica  3) trimite in coada.
// inceput_la porneste la deschiderea ecranului (cronometru efort) si merge la /coada.
// Backend: GET /tenants, GET /declaratii/tipuri, POST /declaratii/{tip}/valideaza, POST /coada.
// [duk_valideaza_v1] Pasul 2 VALIDEAZA la ANAF (DUKIntegrator), nu doar genereaza:
// pana la 15.07.2026 spunea "declaratia pare in regula" fara sa fi validat nimic,
// iar asistentul trimitea in coada un XML nevalidat. Trei stari: valid/erori/gri.

import { api, esc, bani, arataMesaj, dataRo, eroareCamp, curataEroriCamp, semnAjutor } from "../api.js?v=a0acf0511a";
// [ajutor_contextual] mapare tip declaratie -> ID functionalitate pentru semnul "?" dinamic
const _DECL_AJUTOR = { d100:"F026", d101:"F027", d112:"F028", d205:"F029", d300:"F031",
  d301:"F032", d390:"F033", d394:"F034", d406:"F035", d710:"F192" };

const LUNI = ["ianuarie","februarie","martie","aprilie","mai","iunie",
              "iulie","august","septembrie","octombrie","noiembrie","decembrie"];
const TRIM = ["T1 (ian-mar)","T2 (apr-iun)","T3 (iul-sep)","T4 (oct-dec)"];

// stare ecran
let S = null;

// XML-ul vine base64 din ruta de validare (fisierul validat, fara al doilea apel).
function _dinB64(b64) {
  try { return decodeURIComponent(escape(atob(b64))); } catch (e) { return ""; }
}



// [decl_firma_v1] varianta per-firma: firma fixata, fara selector (entitatea e in antet)
export async function declaratiiPerFirma(corp, nav, firma) {
  return randeazaDeclaratii(corp, nav, firma);
}

export async function randeazaDeclaratii(corp, nav, firmaFixa) {
  if (nav && nav.setInapoi) nav.setInapoi(undefined);
  const acum = new Date();
  S = {
    inceput_la: acum.toISOString(),          // cronometru efort (datoria p15)
    pas: 1,
    firme: [], tipuri: [], periodicitate: {}, neaplicabile: {},   // [G1] neaplicabile prin forma, per firma
    firmaFixa: firmaFixa || null,
    tenant_id: firmaFixa ? firmaFixa.tenant_id : null, tip: null,
    an: acum.getFullYear(),
    luna: acum.getMonth() + 1,
    trim: Math.floor(acum.getMonth()/3) + 1,
    rezultat: null,                          // {xml, avertismente}
  };
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  try {
    const t = await api.get("/tenants");
    S.firme = Array.isArray(t) ? t : (t.tenants || t.firme || []);
    if (S.tenant_id) await incarcaTipuri(S.tenant_id);   // [G1] firma fixa -> tipurile+neaplicabile ale ei
  } catch {
    corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca firmele.</p>`;
    return;
  }
  pas1(corp, nav);
}

// [G1] tipurile SI neaplicabile prin forma depind de FIRMA -> ruta cere tenant_id; se re-cer la fiecare schimbare de firma.
async function incarcaTipuri(tenantId) {
  try {
    const d = await api.get(`/declaratii/tipuri?tenant_id=${tenantId}`);
    S.tipuri = d.tipuri || [];
    S.periodicitate = d.periodicitate || {};
    S.neaplicabile = d.neaplicabile || {};
    S.tipuriEsuat = false;
  } catch {
    S.tipuri = []; S.periodicitate = {}; S.neaplicabile = {}; S.tipuriEsuat = true;
  }
}

// ---------- PAS 1: firma + tip + perioada ----------
function pas1(corp, nav) {
  if (nav && nav.setInapoi) nav.setInapoi(undefined);
  const f = corp.closest(".fereastra"); if (f) f.classList.remove("fer-larg");
  S.pas = 1;
  const per = S.tip ? S.periodicitate[S.tip] : null;

  // [G1] optiunile de tip depind de FIRMA: fara firma -> selectorul cere firma; tipurile neaplicabile prin
  // forma (D101/D406 la un PFA) apar DEZACTIVATE cu temeiul scurt (nu ascunse tacit; temei complet in title).
  function optiuniTip() {
    if (!S.tenant_id) return `<option value="">— alege firma întâi —</option>`;
    if (S.tipuriEsuat) return `<option value="">— nu am putut încărca tipurile — reîncarcă firma —</option>`;
    if (!S.tipuri.length) return `<option value="">— nicio declarație aplicabilă —</option>`;
    return `<option value="">— alege tipul —</option>` + S.tipuri.map((tp) => {
      const et = `${tp.toUpperCase()} · ${S.periodicitate[tp] || ""}`;
      const neap = S.neaplicabile[tp];
      return neap
        ? `<option value="${tp}" disabled title="${esc(neap)}">${et} — nu se aplică (partidă simplă)</option>`
        : `<option value="${tp}" ${tp === S.tip ? "selected" : ""}>${et}</option>`;
    }).join("");
  }

  corp.innerHTML = `
    <p class="mig-intro">Pasul 1 din 3 — alege firma, tipul declarației și perioada.</p>
    <div class="dec-form">
${S.firmaFixa ? "" : `      <label class="camp">
        <span class="camp-eticheta">Firmă</span>
        <select id="dec-firma" class="camp-input">
          <option value="">— alege firma —</option>
          ${S.firme.map((fr) => `<option value="${fr.id}" ${fr.id===S.tenant_id?"selected":""}>${esc(fr.nume || fr.denumire || ("Firma "+fr.id))}</option>`).join("")}
        </select>
      </label>`}
      <label class="camp">
        <span class="camp-eticheta">Tip declarație <span id="dec-ajutor"></span></span>
        <select id="dec-tip" class="camp-input">${optiuniTip()}</select>
      </label>
      <div id="dec-perioada">${randPerioada(per)}</div>
    </div>
    <div class="dec-bara">
      <button class="buton-primar" id="dec-continua" disabled>Continuă →</button>
    </div>
  `;

  const selFirma = corp.querySelector("#dec-firma");  // null cand firma e fixa [decl_firma_v1]
  const selTip = corp.querySelector("#dec-tip");
  const cont = corp.querySelector("#dec-continua");
  const zonaP = corp.querySelector("#dec-perioada");

  async function refresh() {
    if (selFirma) {
      const nou = selFirma.value ? parseInt(selFirma.value) : null;
      if (nou !== S.tenant_id) {   // [G1] firma schimbata -> re-cere tipurile+neaplicabile ale ei, re-randeaza selectorul
        S.tenant_id = nou; S.tip = null;
        if (nou) await incarcaTipuri(nou); else { S.tipuri = []; S.periodicitate = {}; S.neaplicabile = {}; }
        selTip.innerHTML = optiuniTip();
      }
    }
    S.tip = selTip.value || null;
    const p = S.tip ? S.periodicitate[S.tip] : null;
    zonaP.innerHTML = randPerioada(p);
    legPerioada(zonaP);
    cont.disabled = !(S.tenant_id && S.tip);
    const _za = corp.querySelector("#dec-ajutor");  // [ajutor] "?" urmareste tipul ales
    if (_za) _za.innerHTML = (S.tip && _DECL_AJUTOR[S.tip]) ? semnAjutor(_DECL_AJUTOR[S.tip]) : "";
  }
  if (selFirma) selFirma.addEventListener("change", refresh);
  selTip.addEventListener("change", refresh);
  legPerioada(zonaP);
  cont.addEventListener("click", () => pas2(corp, nav));
  refresh();
}

function randPerioada(per) {
  if (!per) return "";
  const an = `<label class="camp camp camp-mic">
      <span class="camp-eticheta">An</span>
      <input id="dec-an" class="camp-input" type="number" min="2020" max="2030" value="${S.an}">
    </label>`;
  if (per === "anual") return `<div class="dec-perioada-rand">${an}</div>`;
  if (per === "trimestrial") {
    return `<div class="dec-perioada-rand">${an}
      <label class="camp camp camp-mic">
        <span class="camp-eticheta">Trimestru</span>
        <select id="dec-trim" class="camp-input">
          ${TRIM.map((t,i)=>`<option value="${i+1}" ${i+1===S.trim?"selected":""}>${t}</option>`).join("")}
        </select>
      </label></div>`;
  }
  // lunar
  return `<div class="dec-perioada-rand">${an}
    <label class="camp camp camp-mic">
      <span class="camp-eticheta">Lună</span>
      <select id="dec-luna" class="camp-input">
        ${LUNI.map((l,i)=>`<option value="${i+1}" ${i+1===S.luna?"selected":""}>${l}</option>`).join("")}
      </select>
    </label></div>`;
}

function legPerioada(zona) {
  const an = zona.querySelector("#dec-an");
  const luna = zona.querySelector("#dec-luna");
  const trim = zona.querySelector("#dec-trim");
  if (an) an.addEventListener("change", () => S.an = parseInt(an.value) || S.an);
  if (luna) luna.addEventListener("change", () => S.luna = parseInt(luna.value));
  if (trim) trim.addEventListener("change", () => S.trim = parseInt(trim.value));
}

// ---------- PAS 2: genereaza + verifica ----------
async function pas2(corp, nav) {
  if (nav && nav.setInapoi) nav.setInapoi(() => pas1(corp, nav));
  S.pas = 2;
  corp.innerHTML = `<p class="ecran-nota">Se generează declarația…</p>`;
  const per = S.periodicitate[S.tip];
  const body = { tenant_id: S.tenant_id, an: S.an };
  if (per === "lunar") body.luna = S.luna;
  if (per === "trimestrial") body.trim = S.trim;

  try {
    S.rezultat = await api.post(`/declaratii/${S.tip}/valideaza`, body);
  } catch (e) {
    // [G2] surfaceaza eroarea SPECIFICA (422 cu temei / gri cu limita), nu un mesaj generic - exact unde
    // contabilul are nevoie de ea. Aliniat cu pas3. api.js arunca {cod, mesaj}.
    // [chicken-and-egg 16.08] Declaratiile cu panou editabil (d301/d390/d300) randeaza panoul CHIAR si pe
    // eroare de generare (ex. refuz zero-base): altfel o firma fara operatiuni nu poate ajunge la ecranul
    // unde le adauga. Eroarea explica DE CE; panoul lasa contabilul sa introduca + Regenereaza.
    corp.innerHTML = `
      <p class="mig-intro">Pasul 2 din 3 — generare</p>
      ${S.tip === "d390" ? '<div id="dec-d390-clasif"></div>' : ""}
      ${S.tip === "d301" ? '<div id="dec-d301-op"></div>' : ""}
      ${S.tip === "d300" ? '<div id="dec-d300-manual"></div>' : ""}
      <div class="dec-eroare">${esc((e && e.mesaj) || "Nu am putut genera declarația. Verifică datele firmei pentru perioada aleasă.")}</div>
      `;
    if (S.tip === "d390") randeazaClasificareD390(corp, nav);
    if (S.tip === "d301") randeazaOperatiuniD301(corp, nav);
    if (S.tip === "d300") randeazaManualD300(corp, nav);
    return;
  }

  const f = corp.closest(".fereastra"); if (f) f.classList.add("fer-larg");
  const avert = S.rezultat.avertismente || [];
  const constat = S.rezultat.note_rezultat || [];   // fapte NEUTRE despre rezultat (sectiune informativa separata, nu avertisment)
  const xml = S.rezultat.xml_b64 ? _dinB64(S.rezultat.xml_b64) : (S.rezultat.xml || "");
  const stare = S.rezultat.stare || "gri";
  const erANAF = (S.rezultat.erori || "").trim();
  const sev = S.rezultat.severitate;  // [A2] "eroare" (E:) vs "atentionare" (A:) - DUK pune ambele in stare="erori"
  const blocANAF = stare === "valid"
    ? `<div class="dec-ok">Validat cu DUKIntegrator (validatorul oficial ANAF rulat local), fără erori. Nu a fost depusă la ANAF.</div>`
    : (stare === "erori"
        ? (sev === "atentionare"
            ? `<div class="dec-avert">
                 <div class="dec-avert-cap">DUKIntegrator (validatorul oficial ANAF, local) a semnalat atenționări (nu blochează depunerea — verifică)</div>
                 <pre class="dec-xml-pre">${esc(erANAF)}</pre>
               </div>`
            : `<div class="dec-eroare">
                 <div class="dec-avert-cap">DUKIntegrator (validatorul oficial ANAF, local) a găsit erori</div>
                 <pre class="dec-xml-pre">${esc(erANAF)}</pre>
               </div>`)
        : `<div class="dec-avert">
             <div class="dec-avert-cap">Nu am putut rula validarea cu DUKIntegrator (validatorul ANAF, local)</div>
             <ul><li>${esc(S.rezultat.temei || "Validatorul nu a rulat.")}</li>
                 <li>${esc(S.rezultat.limita || "")}</li></ul>
           </div>`);

  corp.innerHTML = `
    <p class="mig-intro">Pasul 2 din 3 — verifică <b>${S.tip.toUpperCase()}</b> · ${etPerioada()}</p>
    ${S.tip === "d390" ? '<div id="dec-d390-clasif"></div>' : ""}
    ${S.tip === "d301" ? '<div id="dec-d301-op"></div>' : ""}
    ${S.tip === "d300" ? '<div id="dec-d300-manual"></div>' : ""}
    ${blocANAF}
    ${constat.length ? `<div class="caseta-info">
        <div class="ci-mesaj" style="font-weight:600;margin-bottom:6px">Constatări (${constat.length})</div>
        <ul class="ci-mesaj" style="margin:0;padding-left:18px">${constat.map((c)=>`<li style="margin:3px 0">${esc(typeof c==="string"?c:(c.mesaj||"constatare fără detalii"))}</li>`).join("")}</ul>
      </div>` : ""}
    ${avert.length ? `<div class="dec-avert">
        <div class="dec-avert-cap">Avertismente (${avert.length})</div>
        <ul>${avert.map((a)=>`<li>${esc(typeof a==="string"?a:(a.mesaj||"avertisment fără detalii"))}</li>`).join("")}</ul>
      </div>` : ""}
    <details class="dec-xml">
      <summary>Vezi XML-ul generat</summary>
      <pre class="dec-xml-pre">${esc(xml)}</pre>
    </details>
    ${_esteGoala() ? `<div class="caseta-poarta">
        <div class="cp-mesaj">Declarația nu conține nicio operațiune. Dacă firma chiar n-a avut activitate în perioadă, se depune așa. Dacă a avut, întoarce-te și verifică dacă documentele perioadei sunt introduse și contabilizate.</div>
        <div class="cp-butoane">
          <button class="buton-primar" id="dec-gol-da">Da, fără activitate — trimite</button>
          <button class="buton-secundar" id="dec-gol-nu">Nu, mă întorc să verific</button>
        </div>
      </div>` : `<div class="dec-bara">
      <button class="buton-primar" id="dec-trimite">Trimite în coadă →</button>
    </div>`}
    <p class="ecran-nota">${esc(S.rezultat.limita || "")}</p>
  `;
  const _bt = corp.querySelector("#dec-trimite");
  if (_bt) _bt.addEventListener("click", () => pas3(corp, nav));
  const _bDa = corp.querySelector("#dec-gol-da");
  if (_bDa) _bDa.addEventListener("click", () => pas3(corp, nav));
  const _bNu = corp.querySelector("#dec-gol-nu");
  if (_bNu) _bNu.addEventListener("click", () => pas1(corp, nav));
  if (S.tip === "d390") randeazaClasificareD390(corp, nav);
  if (S.tip === "d301") randeazaOperatiuniD301(corp, nav);
  if (S.tip === "d300") randeazaManualD300(corp, nav);
}

// [F125] panou clasificare D390: reclasifica operatiunile auto (servicii/triangulatie) + adauga
// linii manuale. Modifica evidenta persistata; "Regenereaza" reface pas2 cu noile clasificari.
const _D390_TIP_DIR = {
  emisa: [["L", "Livrare bunuri (L)"], ["T", "Triangulație (T)"], ["P", "Servicii prestate (P)"], ["R", "Agricol special (R)"]],
  primita: [["A", "Achiziție bunuri (A)"], ["S", "Servicii primite (S)"]],
};
async function randeazaClasificareD390(corp, nav) {
  const zona = corp.querySelector("#dec-d390-clasif");
  if (!zona) return;
  let d;
  try { d = await api.get(`/tenants/${S.tenant_id}/d390-clasificare?an=${S.an}&luna=${S.luna}`); }
  catch (e) { zona.innerHTML = `<p class="ecran-nota">Nu am putut încărca clasificarea intracomunitară${e && e.mesaj ? " (" + esc(e.mesaj) + ")" : ""}. Reîncarcă declarația.</p>`; return; }
  const auto = d.auto || [], manual = d.manual || [];
  const optSel = (dir, cur) => (_D390_TIP_DIR[dir] || []).map(([v, l]) => `<option value="${v}" ${v === cur ? "selected" : ""}>${l}</option>`).join("");
  zona.innerHTML = `<details class="dec-xml" open><summary>Clasificare intracomunitară (servicii / triangulație)</summary>
    ${auto.length ? `<div class="camp-eticheta" style="margin:6px 0">Operațiuni din facturi — verifică tipul:</div>
      ${auto.map((o) => `<div class="dec-recl-rand">
        <span class="dec-recl-desc">${o.directie === "emisa" ? "↗ emisă" : "↘ primită"} · ${esc(o.tara)}${esc(o.cod)} ${esc(o.den || "")}</span>
        <span class="dec-recl-suma">${bani(o.baza)} lei</span>
        <select class="camp-input dec-recl" data-dir="${o.directie}" data-tara="${esc(o.tara)}" data-cod="${esc(o.cod)}">${optSel(o.directie, o.tip_curent)}</select>
      </div>`).join("")}` : `<div class="camp-eticheta dec-clasif-gol" style="margin:6px 0">Nicio operațiune din facturi în perioadă.</div>`}
    <div class="camp-eticheta" style="margin:10px 0 4px">Linii adăugate manual (fără factură în sistem):</div>
    ${manual.length ? manual.map((m) => `<div class="dec-man-rand">
        <span class="dec-recl-desc">${esc(m.tip)} · ${esc(m.tara)}${esc(m.cod)} ${esc(m.den || "")}</span>
        <span class="dec-recl-suma">${bani(m.baza)} lei</span>
        <button class="btn-link dec-man-del" data-id="${m.id}">șterge</button></div>`).join("") : `<div class="camp-eticheta dec-clasif-gol">—</div>`}
    <div class="dec-man-form" style="margin-top:8px">
      <label class="camp" style="width:160px"><span class="camp-eticheta">Tip</span><select id="man-tip" class="camp-input"><option value="A">Achiziție bunuri IC fără cod furnizor — NOTA 1 (A)</option><option value="P">Servicii prestate (P)</option><option value="S">Servicii primite (S)</option><option value="T">Triangulație (T)</option><option value="R">Agricol special (R)</option></select></label>
      <label class="camp" style="width:100px"><span class="camp-eticheta">Țară</span><input id="man-tara" class="camp-input" placeholder="DE"></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">Cod partener</span><input id="man-cod" class="camp-input" placeholder="fără prefix țară"></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">Denumire</span><input id="man-den" class="camp-input"></label>
      <label class="camp" style="width:110px"><span class="camp-eticheta">Bază (lei)</span><input id="man-baza" type="number" class="camp-input"></label>
      <button class="buton-secundar" id="man-add">+ adaugă</button>
    </div>
    <p class="ecran-nota" style="margin-top:4px">Tip <b>A</b> (NOTA 1): achiziție intracomunitară de bunuri de la un furnizor UE care nu a comunicat un cod valid de TVA — completează Țara (statul membru din care s-au transportat bunurile) și lasă Codul gol.</p>
    <div id="dec-clasif-msg"></div>
    <p style="margin-top:8px"><button class="buton-primar" id="dec-regen">Regenerează D390</button>
      <span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>
  </details>`;
  zona.querySelectorAll(".dec-recl").forEach((sel) => sel.addEventListener("change", async () => {
    try { await api.put(`/tenants/${S.tenant_id}/d390-clasificare/reclasificare`, { an: S.an, luna: S.luna, directie: sel.dataset.dir, tara: sel.dataset.tara, cod: sel.dataset.cod, tip: sel.value }); }
    catch (e) { arataMesaj(zona.querySelector("#dec-clasif-msg"), (e && e.mesaj) || "Eroare la salvare.", "eroare"); }
  }));
  zona.querySelectorAll(".dec-man-del").forEach((b) => b.addEventListener("click", async () => {
    try { await api.del(`/tenants/${S.tenant_id}/d390-clasificare/manual/${b.dataset.id}?an=${S.an}&luna=${S.luna}`); randeazaClasificareD390(corp, nav); }
    catch (e) { arataMesaj(zona.querySelector("#dec-clasif-msg"), (e && e.mesaj) || "Eroare la ștergere.", "eroare"); }
  }));
  zona.querySelector("#man-add").addEventListener("click", async () => {
    const b = { an: S.an, luna: S.luna, tip: zona.querySelector("#man-tip").value,
      tara: zona.querySelector("#man-tara").value.trim().toUpperCase(), cod: zona.querySelector("#man-cod").value.trim(),
      den: zona.querySelector("#man-den").value.trim(), baza: parseFloat(zona.querySelector("#man-baza").value) || 0 };
    curataEroriCamp(zona);  // [G10] eroare langa camp
    try { await api.post(`/tenants/${S.tenant_id}/d390-clasificare/manual`, b); randeazaClasificareD390(corp, nav); }
    catch (e) {
      curataEroriCamp(zona);
      const _ec = (e && e.erori_campuri) || [], _b = [];
      _ec.forEach((x) => { if (!eroareCamp(zona, "man-" + x.camp, x.mesaj)) _b.push(x.mesaj); });
      if (!_ec.length || _b.length) arataMesaj(zona.querySelector("#dec-clasif-msg"), _b.length ? _b.join("; ") : ((e && e.mesaj) || "Eroare la adăugare."), "eroare");
    }
  });
  zona.querySelector("#dec-regen").addEventListener("click", () => pas2(corp, nav));
}

// [D301 27.07.2026] panou introducere operatiuni D301 (decont special TVA), afisat in pas2 cand
// tip==="d301". Geaman cu randeazaClasificareD390: grila lunii + adaugare + stergere + regenerare.
// FISCAL: baza = val_valuta x curs (AFISATA, nestocata - generatorul o recalculeaza). TVA = baza x
// cota; cota din selector (standard period-aware din backend, nu literal), TVA calculat SE STOCHEAZA
// (d301.calcul_d301 il citeste din DB, nu-l recalculeaza). Etichetele celor 5 tipuri + valutele +
// cotele vin din backend (sursa unica, EXACT ca formularul oficial) - nu le rescriu in JS.
async function randeazaOperatiuniD301(corp, nav) {
  const zona = corp.querySelector("#dec-d301-op");
  if (!zona) return;
  let d;
  try { d = await api.get(`/tenants/${S.tenant_id}/d301-operatiuni?an=${S.an}&luna=${S.luna}`); }
  catch (e) { zona.innerHTML = `<p class="ecran-nota">Nu am putut încărca operațiunile D301${e && e.mesaj ? " (" + esc(e.mesaj) + ")" : ""}. Reîncarcă declarația.</p>`; return; }
  const ops = d.operatiuni || [], tipuri = d.tipuri || [], valute = d.valute || [], cote = d.cote || [];
  const grila = ops.length
    ? ops.map((o) => `<div class="dec-man-rand">
        <span class="dec-recl-desc" title="${esc(o.eticheta)}">Tip ${o.tip} · ${esc(o.nr_doc)}${o.data_doc ? " · " + esc(o.data_doc) : ""} · ${esc(o.tip_valuta)} ${bani(o.val_valuta)} × ${esc(String(o.curs))}</span>
        <span class="dec-recl-suma">${bani(o.baza)} bază · ${bani(o.tva)} TVA (lei)</span>
        <button class="btn-link dec-d301-del" data-id="${o.id}">șterge</button></div>`).join("")
    : `<div class="stare-goala stare-goala--inline">Nicio operațiune pe ${etPerioada()}. D301 se depune doar cu achiziții intracomunitare / taxare inversă — introdu-le mai jos; fără ele, declarația e pe zero.</div>`;
  zona.innerHTML = `<details class="dec-xml" open><summary>Operațiuni D301 — introducere (${ops.length})</summary>
    ${grila}
    <div class="camp-eticheta" style="margin:10px 0 4px">Adaugă operațiune:</div>
    <div class="dec-man-form">
      <label class="camp" style="width:320px"><span class="camp-eticheta">Tip operațiune <span class="oblig">*</span></span>
        <select id="d301-tip" class="camp-input">${tipuri.map((t) => `<option value="${t.val}">${t.val} — ${esc(t.eticheta)}</option>`).join("")}</select></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">Nr. document <span class="oblig">*</span></span><input id="d301-nrdoc" class="camp-input"></label>
      <label class="camp" style="width:130px"><span class="camp-eticheta">Data document <span class="oblig">*</span></span><input id="d301-datadoc" class="camp-input" placeholder="ZZ.LL.AAAA"></label>
      <label class="camp" style="width:90px"><span class="camp-eticheta">Valută <span class="oblig">*</span></span>
        <select id="d301-valuta" class="camp-input">${valute.map((v) => `<option value="${v}" ${v === "EUR" ? "selected" : ""}>${v}</option>`).join("")}</select></label>
      <label class="camp" style="width:110px"><span class="camp-eticheta">Val. valută <span class="oblig">*</span></span><input id="d301-val" type="number" step="0.01" class="camp-input"></label>
      <label class="camp" style="width:100px"><span class="camp-eticheta">Curs <span class="oblig">*</span></span><input id="d301-curs" type="number" step="0.0001" class="camp-input"></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">Cotă TVA <span class="oblig">*</span></span>
        <select id="d301-cota" class="camp-input">${cote.map((c) => `<option value="${c.val}">${esc(c.eticheta)}</option>`).join("")}</select></label>
      <button class="buton-secundar" id="d301-add">+ adaugă</button>
    </div>
    <div class="camp-ajutor" id="d301-preview" style="margin-top:4px"></div>
    <div id="d301-msg"></div>
    <p style="margin-top:8px"><button class="buton-primar" id="d301-regen">Regenerează D301</button>
      <span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>
  </details>`;
  const gv = (id) => zona.querySelector(id);
  function preview() {
    const val = parseFloat(gv("#d301-val").value) || 0;
    const curs = parseFloat(gv("#d301-curs").value) || 0;
    const cota = parseInt(gv("#d301-cota").value) || 0;
    const baza = Math.round(val * curs);
    const tva = Math.round(baza * cota / 100);
    gv("#d301-preview").textContent = (val && curs) ? `Bază ${bani(baza)} lei · TVA ${cota}% = ${bani(tva)} lei (se stochează)` : "";
  }
  ["#d301-val", "#d301-curs", "#d301-cota"].forEach((s) => gv(s).addEventListener("input", preview));
  zona.querySelectorAll(".dec-d301-del").forEach((b) => b.addEventListener("click", async () => {
    try { await api.del(`/tenants/${S.tenant_id}/d301-operatiuni/${b.dataset.id}?an=${S.an}&luna=${S.luna}`); randeazaOperatiuniD301(corp, nav); }
    catch (e) { arataMesaj(gv("#d301-msg"), (e && e.mesaj) || "Eroare la ștergere.", "eroare"); }
  }));
  gv("#d301-add").addEventListener("click", async () => {
    const b = { an: S.an, luna: S.luna, tip: parseInt(gv("#d301-tip").value),
      nr_doc: gv("#d301-nrdoc").value.trim(), data_doc: gv("#d301-datadoc").value.trim(),
      tip_valuta: gv("#d301-valuta").value, val_valuta: parseFloat(gv("#d301-val").value) || 0,
      curs: parseFloat(gv("#d301-curs").value) || 0, cota: parseInt(gv("#d301-cota").value) };
    curataEroriCamp(zona);  // [G10] eroare langa camp
    try { await api.post(`/tenants/${S.tenant_id}/d301-operatiuni`, b); randeazaOperatiuniD301(corp, nav); }
    catch (e) {
      curataEroriCamp(zona);
      const _ec = (e && e.erori_campuri) || [], _b = [];
      _ec.forEach((x) => { if (!eroareCamp(zona, "d301-" + x.camp, x.mesaj)) _b.push(x.mesaj); });  // fallback B daca #camp lipseste
      if (!_ec.length || _b.length) arataMesaj(gv("#d301-msg"), _b.length ? _b.join("; ") : ((e && e.mesaj) || "Eroare la adăugare."), "eroare");
    }
  });
  gv("#d301-regen").addEventListener("click", () => pas2(corp, nav));
}

// tip==="d300". Geaman cu randeazaOperatiuniD301: grila randurilor manuale + adaugare (upsert) +
// stergere + regenerare. Randurile pe care generatorul NU le deriva din facturi (scutiri/regularizari/
// ajustari) se introduc aici, PERSISTAT (tabel d300_manual); "Regenereaza D300" reface pas2, iar calea
// de depunere (/coada) le citeste din DB -> acelasi XML (paritate preview<->depunere). Etichetele
// oficiale + lista randurilor disponibile (allow-list minus auto-derivate) vin din backend, nu din JS.
// Sume in LEI intregi (ca generatorul). catch NON-gol (scrie in #d300-msg / zona) - garda test_catch_vizibil.
async function randeazaManualD300(corp, nav) {
  const zona = corp.querySelector("#dec-d300-manual");
  if (!zona) return;
  let d;
  try { d = await api.get(`/tenants/${S.tenant_id}/d300-manual?an=${S.an}&luna=${S.luna}`); }
  catch (e) { zona.innerHTML = `<p class="ecran-nota">Nu am putut încărca rândurile manuale D300${e && e.mesaj ? " (" + esc(e.mesaj) + ")" : ""}. Reîncarcă declarația.</p>`; return; }
  const randuri = d.randuri || [], disp = d.randuri_disponibile || [];
  const grila = randuri.length
    ? randuri.map((o) => `<div class="dec-man-rand">
        <span class="dec-recl-desc" title="${esc(o.eticheta)}">${esc(o.rand)} · ${esc(o.eticheta)}</span>
        <span class="dec-recl-suma">${bani(o.baza)} bază${o.cu_tva ? " · " + bani(o.tva) + " TVA" : ""} (lei)${o.descriere ? " · " + esc(o.descriere) : ""}</span>
        <button class="btn-link dec-d300-del" data-id="${o.id}">șterge</button></div>`).join("")
    : `<div class="stare-goala stare-goala--inline">Niciun rând manual pe ${etPerioada()}. Rândurile pe care generatorul le derivă din facturi apar automat în decont; aici introduci doar ce nu se derivă (scutiri, regularizări, ajustări).</div>`;
  const optiuni = disp.map((r) => `<option value="${esc(r.cod)}" data-cutva="${r.cu_tva ? 1 : 0}">${esc(r.cod)} — ${esc(r.eticheta)}</option>`).join("");
  zona.innerHTML = `<details class="dec-xml" open><summary>Rânduri manuale D300 — introducere (${randuri.length})</summary>
    ${grila}
    ${disp.length ? `<div class="camp-eticheta" style="margin:10px 0 4px">Adaugă rând:</div>
    <div class="dec-man-form">
      <label class="camp" style="width:440px"><span class="camp-eticheta">Rând <span class="oblig">*</span></span>
        <select id="d300-rand" class="camp-input">${optiuni}</select></label>
      <label class="camp" style="width:130px"><span class="camp-eticheta">Bază (lei) <span class="oblig">*</span></span><input id="d300-baza" type="number" step="1" class="camp-input"></label>
      <label class="camp" style="width:130px" id="d300-tva-wrap"><span class="camp-eticheta">TVA (lei)</span><input id="d300-tva" type="number" step="1" class="camp-input"></label>
      <label class="camp" style="width:220px"><span class="camp-eticheta">Descriere</span><input id="d300-descriere" class="camp-input"></label>
      <button class="buton-secundar" id="d300-add">+ adaugă</button>
    </div>` : `<p class="ecran-nota" style="margin-top:8px">Toate rândurile manual-acceptabile sunt fie deja introduse, fie derivate automat din facturile perioadei.</p>`}
    <div id="d300-msg"></div>
    <p style="margin-top:8px"><button class="buton-primar" id="d300-regen">Regenerează D300</button>
      <span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>
  </details>`;
  const gv = (id) => zona.querySelector(id);
  function sincTva() {
    const sel = gv("#d300-rand"); if (!sel) return;
    const o = sel.selectedOptions[0];
    const cuTva = !!(o && o.dataset.cutva === "1");
    const w = gv("#d300-tva-wrap"); if (w) w.style.display = cuTva ? "" : "none";
    if (!cuTva) { const t = gv("#d300-tva"); if (t) t.value = ""; }
  }
  if (gv("#d300-rand")) { gv("#d300-rand").addEventListener("change", sincTva); sincTva(); }
  zona.querySelectorAll(".dec-d300-del").forEach((b) => b.addEventListener("click", async () => {
    try { await api.del(`/tenants/${S.tenant_id}/d300-manual/${b.dataset.id}`); randeazaManualD300(corp, nav); }
    catch (e) { arataMesaj(gv("#d300-msg"), (e && e.mesaj) || "Eroare la ștergere.", "eroare"); }
  }));
  const bAdd = gv("#d300-add");
  if (bAdd) bAdd.addEventListener("click", async () => {
    const tvaEl = gv("#d300-tva");
    const b = { an: S.an, luna: S.luna, rand: gv("#d300-rand").value,
      baza: parseInt(gv("#d300-baza").value, 10) || 0,
      tva: parseInt((tvaEl && tvaEl.value) || "0", 10) || 0,
      descriere: gv("#d300-descriere").value.trim() };
    curataEroriCamp(zona);  // [G10] eroare langa camp
    try { await api.post(`/tenants/${S.tenant_id}/d300-manual`, b); randeazaManualD300(corp, nav); }
    catch (e) {
      curataEroriCamp(zona);
      const _ec = (e && e.erori_campuri) || [], _b = [];
      _ec.forEach((x) => { if (!eroareCamp(zona, "d300-" + x.camp, x.mesaj)) _b.push(x.mesaj); });  // fallback B daca #camp lipseste
      if (!_ec.length || _b.length) arataMesaj(gv("#d300-msg"), _b.length ? _b.join("; ") : ((e && e.mesaj) || "Eroare la adăugare."), "eroare");
    }
  });
  gv("#d300-regen").addEventListener("click", () => pas2(corp, nav));
}

// [poarta_gol_v1 27.07.2026] O declaratie GOALA legitima (firma fara activitate) si una
// golita de un query rupt arata IDENTIC: acelasi XML valid, aceleasi zero randuri. Validatorul
// ANAF nu poate face diferenta. Poarta (DS cap.5 v2.14, .caseta-poarta) cere omului sa confirme
// FAPTUL, nu regula: nu spunem noi care declaratie se depune pe zero - aia e chestiune fiscala.
// `operatiuni === null` inseamna "nu se poate numara" (d101/d112) -> fara poarta, nu falsificam
// necunoscutul in zero.
function _esteGoala() {
  return S.rezultat && S.rezultat.operatiuni === 0;
}

// ---------- PAS 3: trimite in coada ----------
async function pas3(corp, nav) {
  if (nav && nav.setInapoi) nav.setInapoi(() => pas2(corp, nav));
  const btn = corp.querySelector("#dec-trimite");
  if (btn) { btn.disabled = true; btn.textContent = "Se trimite…"; }
  const per = S.periodicitate[S.tip];
  const body = { tenant_id: S.tenant_id, tip: S.tip, an: S.an, inceput_la: S.inceput_la };
  if (per === "lunar") body.luna = S.luna;
  if (per === "trimestrial") body.trim = S.trim;

  try {
    await api.post("/coada", body);
  } catch (e) {
    if (btn) { btn.disabled = false; btn.textContent = "Trimite în coadă →"; }
    if (btn) {
      btn.parentElement.querySelectorAll(".msg-eroare").forEach((x) => x.remove());
      btn.insertAdjacentHTML("afterend", '<span class="msg-eroare" style="margin-left:8px">Nu am putut trimite în coadă. Poate există deja o declarație pentru această perioadă.</span>');
    }
    return;
  }

  const f = corp.closest(".fereastra"); if (f) f.classList.remove("fer-larg");
  corp.innerHTML = `
    <div class="dec-gata">
      <div class="dec-gata-bif">✓</div>
      <div class="dec-gata-titlu">Trimisă în coada de validare</div>
      <div class="dec-gata-sub"><b>${S.tip.toUpperCase()}</b> · ${etPerioada()} a fost trimisă seniorului pentru validare.</div>
    </div>
    <div class="dec-bara">
      <button class="buton-secundar" id="dec-alta">+ Altă declarație</button>
      <button class="buton-primar" id="dec-gata-ok">Gata</button>
    </div>
  `;
  corp.querySelector("#dec-alta").addEventListener("click", () => randeazaDeclaratii(corp, nav));
  corp.querySelector("#dec-gata-ok").addEventListener("click", () => nav.acasa());
}

function etPerioada() {
  const per = S.periodicitate[S.tip];
  if (per === "anual") return `anul ${S.an}`;
  if (per === "trimestrial") return `${TRIM[S.trim-1]} ${S.an}`;   // TRIM = etichete de trimestru, fara echivalent dataRo (legitim)
  // [G3] eticheta luna-an prin dataRo canonic (nu LUNI[S.luna-1] local); LUNI ramane pentru picker
  return dataRo(`${S.an}-${String(S.luna).padStart(2, "0")}`, "luna_an");
}

// audit_cab_lot1_v1
