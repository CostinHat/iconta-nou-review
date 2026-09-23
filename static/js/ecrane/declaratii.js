// declaratii.js — ecran asistent: creeaza o declaratie -> trimite in coada de validare.
// Flux 3 pasi intr-o fereastra: 1) firma+tip+perioada  2) genereaza+verifica  3) trimite in coada.
// inceput_la porneste la deschiderea ecranului (cronometru efort) si merge la /coada.
// Backend: GET /tenants, GET /declaratii/tipuri, POST /declaratii/{tip}/valideaza, POST /coada.
// [duk_valideaza_v1] Pasul 2 VALIDEAZA la ANAF (DUKIntegrator), nu doar genereaza:
// pana la 15.07.2026 spunea "declaratia pare in regula" fara sa fi validat nimic,
// iar asistentul trimitea in coada un XML nevalidat. Trei stari: valid/erori/gri.

import { api, esc, bani, arataMesaj, dataRo, eroareCamp, curataEroriCamp, semnAjutor } from "../api.js?v=1dccbc985b";
// [ajutor_contextual] mapare tip declaratie -> ID functionalitate pentru semnul "?" dinamic
const _DECL_AJUTOR = { d100:"F026", d101:"F027", d112:"F028", d205:"F029", d300:"F031",
  d301:"F032", d390:"F033", d394:"F034", d406:"F035", d710:"F192", d311:"F207", d307:"F217", d107:"F211", d177:"F210", d207:"F209", d200:"F221", d212:"F030", d201:"F222" };

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
    d710_obligatii: [],                      // [formular_manual_d710] obligatii corectate (in memorie, pt body)
    // [formular_manual_d311] situatiile fiscale dupa anularea codului de TVA (in memorie, pt body.manual).
    // Persista intre randari (Regenereaza reface pas2 -> re-randeaza formularul cu valorile pastrate).
    d311: { Data_A: "", motiv: "", d_rec: 0,
            OB_11: "", OB_12: "", OB_21: "", OB_22: "", OB_41: "", OB_42: "" },
    // [formular_manual_d307] operatiunile de ajustare TVA (lista in memorie, pt body.manual, ca d710).
    d307: { operatiuni: [], d_rec: 0, d_anulare: 0, temei: "" },
    // [formular_manual_d107] beneficiarii sponsorizarilor/mecenatului/burselor (lista in memorie, pt body.manual, ca d307).
    d107: { beneficiari: [], val2_ni: "", val3_ni: "", neindividualizati: [], d_rec: 0 },
    // [formular_manual_d177] redirectionarea impozitului pe profit catre ONG/cult (in memorie, pt body.manual).
    d177: { data_inceput: "", data_sfarsit: "", suma_max: "", suma_ant: "", suma_rest: "", d_rec: 0, beneficiari: [] },
    // [formular_manual_d207] beneficiarii nerezidenti carora firma le-a platit venituri cu retinere la sursa
    // (lista in memorie, pt body.manual, ca d107). Grupati pe tip_venit -> Sect_II; suma de control calculata.
    d207: { beneficiari: [], d_rec: 0 },
    // [formular_manual_d200] identitate PF + sectiuni pe categorie de venit (in memorie, pt body.manual, ca d207).
    d200: { cif_i: "", nume_c: "", prenume_c: "", adresa_i: "", cont_c: "", sectiuni: [], d_rec: 0 },
    // [formular_manual_d212] Declaratia unica PF: identitate (cif=CNP/nume/adresa) + fisa RIP AFISATA
    // (pull din registru; venitul/CAS/CASS/impozit — informativ). Increment: genereaza cazul minim
    // DUK-valid (identitate); popularea cap11/oblig_realizat din fisa = pas urmator. In memorie, ca d200.
    d212: { cif: "", nume_c: "", adresa_c: "", d_rec: 0, fisa: null, fisa_eroare: "" },
    // [formular_manual_d201] venituri din strainatate PF: identitate (CNP/nume/initiala tata/prenume) +
    // sectiuni pe (tara, categorie) - venit_B/chlt_D/imp1/imp2/pierdere; venit_N calculat. In memorie, ca d200.
    d201: { cif_c: "", nume_c: "", initiala_c: "", prenume_c: "", d_rec: 0, sectiuni: [] },
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
        ? `<option value="${tp}" disabled title="${esc(neap)}">${esc(neap)}</option>`
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
  if (S.tip === "d710") body.obligatii = S.d710_obligatii || [];  // [formular_manual_d710] din memorie
  if (S.tip === "d311") body.manual = _d311Manual();              // [formular_manual_d311] situatiile din memorie
  if (S.tip === "d307") body.manual = _d307Manual();              // [formular_manual_d307] operatiunile din memorie
  if (S.tip === "d107") body.manual = _d107Manual();              // [formular_manual_d107] beneficiarii din memorie
  if (S.tip === "d177") body.manual = _d177Manual();              // [formular_manual_d177] redirectionarea din memorie
  if (S.tip === "d207") body.manual = _d207Manual();              // [formular_manual_d207] beneficiarii nerezidenti din memorie
  if (S.tip === "d200") body.manual = _d200Manual();              // [formular_manual_d200] sectiunile de venit din memorie
  if (S.tip === "d212") body.manual = _d212Manual();              // [formular_manual_d212] identitatea PF din memorie
  if (S.tip === "d201") body.manual = _d201Manual();              // [formular_manual_d201] identitate + sectiuni strainatate

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
      ${S.tip === "d710" ? '<div id="dec-d710-form"></div>' : ""}
      ${S.tip === "d311" ? '<div id="dec-d311-form"></div>' : ""}
      ${S.tip === "d307" ? '<div id="dec-d307-form"></div>' : ""}
      ${S.tip === "d107" ? '<div id="dec-d107-form"></div>' : ""}
      ${S.tip === "d177" ? '<div id="dec-d177-form"></div>' : ""}
      ${S.tip === "d207" ? '<div id="dec-d207-form"></div>' : ""}
    ${S.tip === "d200" ? '<div id="dec-d200-form"></div>' : ""}
    ${S.tip === "d212" ? '<div id="dec-d212-form"></div>' : ""}
    ${S.tip === "d201" ? '<div id="dec-d201-form"></div>' : ""}
      <div class="dec-eroare">${esc((e && e.mesaj) || "Nu am putut genera declarația. Verifică datele firmei pentru perioada aleasă.")}</div>
      `;
    if (S.tip === "d390") randeazaClasificareD390(corp, nav);
    if (S.tip === "d301") randeazaOperatiuniD301(corp, nav);
    if (S.tip === "d300") randeazaManualD300(corp, nav);
    if (S.tip === "d710") randeazaFormularD710(corp, nav);
    if (S.tip === "d311") randeazaFormularD311(corp, nav);
    if (S.tip === "d307") randeazaFormularD307(corp, nav);
    if (S.tip === "d107") randeazaFormularD107(corp, nav);
    if (S.tip === "d177") randeazaFormularD177(corp, nav);
    if (S.tip === "d207") randeazaFormularD207(corp, nav);
  if (S.tip === "d200") randeazaFormularD200(corp, nav);
  if (S.tip === "d212") randeazaFormularD212(corp, nav);
  if (S.tip === "d201") randeazaFormularD201(corp, nav);
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
    ${S.tip === "d710" ? '<div id="dec-d710-form"></div>' : ""}
    ${S.tip === "d311" ? '<div id="dec-d311-form"></div>' : ""}
    ${S.tip === "d307" ? '<div id="dec-d307-form"></div>' : ""}
    ${S.tip === "d107" ? '<div id="dec-d107-form"></div>' : ""}
    ${S.tip === "d177" ? '<div id="dec-d177-form"></div>' : ""}
    ${S.tip === "d207" ? '<div id="dec-d207-form"></div>' : ""}
    ${S.tip === "d200" ? '<div id="dec-d200-form"></div>' : ""}
    ${S.tip === "d212" ? '<div id="dec-d212-form"></div>' : ""}
    ${S.tip === "d201" ? '<div id="dec-d201-form"></div>' : ""}
    ${blocANAF}
    ${constat.length ? `<div class="caseta-info">
        <div class="ci-mesaj" style="font-weight:600;margin-bottom:6px">Constatări (${constat.length})</div>
        <ul class="ci-mesaj" style="margin:0;padding-left:18px">${constat.map((c)=>`<li style="margin:3px 0">${esc(typeof c==="string"?c:(c.mesaj||"constatare fără detalii"))}</li>`).join("")}</ul>
      </div>` : ""}
    ${avert.length ? `<div class="dec-avert">
        <div class="dec-avert-cap">Avertismente (${avert.length})</div>
        <ul>${avert.map((a)=>`<li>${esc(typeof a==="string"?a:(a.mesaj||"avertisment fără detalii"))}</li>`).join("")}</ul>
      </div>` : ""}
    ${_blocComponente(S.rezultat.componente)}
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
  if (S.tip === "d710") randeazaFormularD710(corp, nav);
  if (S.tip === "d311") randeazaFormularD311(corp, nav);
  if (S.tip === "d307") randeazaFormularD307(corp, nav);
  if (S.tip === "d107") randeazaFormularD107(corp, nav);
  if (S.tip === "d177") randeazaFormularD177(corp, nav);
  if (S.tip === "d207") randeazaFormularD207(corp, nav);
  if (S.tip === "d200") randeazaFormularD200(corp, nav);
  if (S.tip === "d212") randeazaFormularD212(corp, nav);
  if (S.tip === "d201") randeazaFormularD201(corp, nav);
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
    ? ops.map((o) => {
        const furnizor = o.partener_tara ? `${esc(o.partener_tara)}${esc(o.partener_cod || "")}${o.partener_den ? " " + esc(o.partener_den) : ""}` : "";
        const temei307 = o.tip === 4
          ? (o.temei_neconfirmat
              ? ` <span class="mig-cnp-no" title="Alege alineatul art. 307 (gaz/energie / ieșire din regim suspensiv / nestabilit neînregistrat) ca excluderea din D390 să fie auditabilă.">⚠ temei art. 307 neconfirmat</span>`
              : (o.temei_307_eticheta ? ` <span class="ecran-nota">temei: ${esc(o.temei_307_eticheta)}</span>` : ""))
          : "";
        const d390 = o.d390_cod
          ? (o.d390_lipsa_furnizor
              ? ` <span class="mig-cnp-no" title="completează țara furnizorului ca operațiunea să apară în D390">⚠ fără furnizor — nu intră în D390 (cod ${o.d390_cod})</span>`
              : (furnizor ? ` <span class="mig-cnp-ok">→ D390 cod ${o.d390_cod}</span>` : ""))
          : ` <span class="ecran-nota">(nu intră în D390 — ${o.tip === 2 ? "mijloc de transport nou" : "art. 307 alin. (3)/(5)/(6)"})</span>${temei307}`;
        return `<div class="dec-man-rand">
        <span class="dec-recl-desc" title="${esc(o.eticheta)}">Tip ${o.tip} · ${esc(o.nr_doc)}${o.data_doc ? " · " + esc(o.data_doc) : ""} · ${esc(o.tip_valuta)} ${bani(o.val_valuta)} × ${esc(String(o.curs))}${furnizor ? " · furnizor " + furnizor : ""}${d390}</span>
        <span class="dec-recl-suma">${bani(o.baza)} bază · ${bani(o.tva)} TVA (lei)</span>
        <button class="btn-link dec-d301-del" data-id="${o.id}">șterge</button></div>`;
      }).join("")
    : `<div class="stare-goala stare-goala--inline">Nicio operațiune pe ${etPerioada()}. D301 se depune doar cu achiziții intracomunitare / taxare inversă — introdu-le mai jos; fără ele, declarația e pe zero.</div>`;
  zona.innerHTML = `<details class="dec-xml" open><summary>Operațiuni D301 — introducere (${ops.length})</summary>
    ${grila}
    <div class="camp-eticheta" style="margin:10px 0 4px">Adaugă operațiune:</div>
    <div class="dec-man-form">
      <label class="camp" style="width:320px"><span class="camp-eticheta">Tip operațiune <span class="oblig">*</span></span>
        <select id="d301-tip" class="camp-input">${tipuri.map((t) => `<option value="${t.val}">${t.val} — ${esc(t.eticheta)}</option>`).join("")}</select></label>
      <label class="camp" id="d301-temei-wrap" style="width:320px;display:none"><span class="camp-eticheta">Temei art. 307 (tip 4) <span class="oblig">*</span></span>
        <select id="d301-temei307" class="camp-input"><option value="">— alege alineatul —</option>${(d.temeiuri_307 || []).map((tm) => `<option value="${tm.val}">${esc(tm.eticheta)}</option>`).join("")}</select></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">Nr. document <span class="oblig">*</span></span><input id="d301-nrdoc" class="camp-input"></label>
      <label class="camp" style="width:130px"><span class="camp-eticheta">Data document <span class="oblig">*</span></span><input id="d301-datadoc" class="camp-input" placeholder="ZZ.LL.AAAA"></label>
      <label class="camp" style="width:90px"><span class="camp-eticheta">Valută <span class="oblig">*</span></span>
        <select id="d301-valuta" class="camp-input">${valute.map((v) => `<option value="${v}" ${v === "EUR" ? "selected" : ""}>${v}</option>`).join("")}</select></label>
      <label class="camp" style="width:110px"><span class="camp-eticheta">Val. valută <span class="oblig">*</span></span><input id="d301-val" type="number" step="0.01" class="camp-input"></label>
      <label class="camp" style="width:100px"><span class="camp-eticheta">Curs <span class="oblig">*</span></span><input id="d301-curs" type="number" step="0.0001" class="camp-input"></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">Cotă TVA <span class="oblig">*</span></span>
        <select id="d301-cota" class="camp-input">${cote.map((c) => `<option value="${c.val}">${esc(c.eticheta)}</option>`).join("")}</select></label>
      <label class="camp" style="width:90px"><span class="camp-eticheta">Țară furnizor</span><input id="d301-partener_tara" class="camp-input" placeholder="DE" maxlength="2" style="text-transform:uppercase"></label>
      <label class="camp" style="width:170px"><span class="camp-eticheta">Cod TVA furnizor</span><input id="d301-partener_cod" class="camp-input" placeholder="fără prefix țară"></label>
      <label class="camp" style="width:200px"><span class="camp-eticheta">Denumire furnizor</span><input id="d301-partener_den" class="camp-input"></label>
      <button class="buton-secundar" id="d301-add">+ adaugă</button>
    </div>
    <p class="ecran-nota" style="margin-top:2px">Furnizorul UE (țară + cod TVA) e opțional pentru D301, dar dacă îl completezi, achiziția apare AUTOMAT în D390 (bunuri tip 1/3 → cod A; servicii tip 5 → cod S). Fără țară, operațiunea nu intră în D390.</p>
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
  // [temei_307] selectul de temei art. 307 apare doar la tip 4 (obligatoriu la introducere)
  const _tipSel = gv("#d301-tip"), _temeiWrap = gv("#d301-temei-wrap");
  const _sincTemei = () => { if (_temeiWrap) _temeiWrap.style.display = (_tipSel.value === "4") ? "" : "none"; };
  if (_tipSel) { _tipSel.addEventListener("change", _sincTemei); _sincTemei(); }
  gv("#d301-add").addEventListener("click", async () => {
    const b = { an: S.an, luna: S.luna, tip: parseInt(gv("#d301-tip").value),
      nr_doc: gv("#d301-nrdoc").value.trim(), data_doc: gv("#d301-datadoc").value.trim(),
      tip_valuta: gv("#d301-valuta").value, val_valuta: parseFloat(gv("#d301-val").value) || 0,
      curs: parseFloat(gv("#d301-curs").value) || 0, cota: parseInt(gv("#d301-cota").value),
      partener_tara: gv("#d301-partener_tara").value.trim(), partener_cod: gv("#d301-partener_cod").value.trim(),
      partener_den: gv("#d301-partener_den").value.trim(),
      temei_307: (gv("#d301-tip").value === "4" && gv("#d301-temei307")) ? gv("#d301-temei307").value : "" };
    curataEroriCamp(zona);  // [G10] eroare langa camp
    try { const _r = await api.post(`/tenants/${S.tenant_id}/d301-operatiuni`, b); await randeazaOperatiuniD301(corp, nav); if (_r && _r.avertisment) arataMesaj(gv("#d301-msg"), _r.avertisment, "atentionare"); }
    catch (e) {
      curataEroriCamp(zona);
      const _ec = (e && e.erori_campuri) || [], _b = [];
      _ec.forEach((x) => { if (!eroareCamp(zona, "d301-" + x.camp, x.mesaj)) _b.push(x.mesaj); });  // fallback B daca #camp lipseste
      if (!_ec.length || _b.length) arataMesaj(gv("#d301-msg"), _b.length ? _b.join("; ") : ((e && e.mesaj) || "Eroare la adăugare."), "eroare");
    }
  });
  gv("#d301-regen").addEventListener("click", () => pas2(corp, nav));
}

// tip==="d710" (rectificativa D100). Geaman cu randeazaOperatiuniD301: lista obligatiilor corectate +
// adaugare + stergere + regenerare. Obligatiile stau IN MEMORIE (S.d710_obligatii) - D710 le primeste
// DIRECT in body (nu are tabel in DB). Fiecare: cod obligatie (121 micro / 103 profit), suma initiala
// (declarata gresit in D100) + suma corecta; cota % obligatorie la micro (121). Clasele DS din cap.6/D301.
const _D710_CODURI = [{ val: "121", et: "Impozit pe veniturile microîntreprinderilor (121)" },
                      { val: "103", et: "Impozit pe profit (103)" }];
function _d710_et(cod) { const c = _D710_CODURI.find((x) => x.val === cod); return c ? c.et : "Cod " + cod; }

function randeazaFormularD710(corp, nav) {
  const zona = corp.querySelector("#dec-d710-form");
  if (!zona) return;
  const obl = S.d710_obligatii || [];
  const grila = obl.length
    ? obl.map((o, i) => `<div class="dec-man-rand">
        <span class="dec-recl-desc">${esc(_d710_et(o.cod_oblig))} · inițial ${bani(o.suma_dat_i)} lei → corect ${bani(o.suma_dat_c)} lei${o.cota ? " · cotă " + esc(String(o.cota)) + "%" : ""}</span>
        <button class="btn-link dec-d710-del" data-idx="${i}">șterge</button></div>`).join("")
    : `<div class="stare-goala stare-goala--inline">Nicio obligație corectată. D710 corectează obligațiile declarate greșit în D100 — adaugă mai jos ce ai declarat inițial și cât e corect.</div>`;
  zona.innerHTML = `<details class="dec-xml" open><summary>Obligații corectate (${obl.length})</summary>
    ${grila}
    <div class="camp-eticheta" style="margin:10px 0 4px">Adaugă obligație corectată:</div>
    <div class="dec-man-form">
      <label class="camp" style="width:340px"><span class="camp-eticheta">Obligația <span class="oblig">*</span></span>
        <select id="d710-cod" class="camp-input">${_D710_CODURI.map((c) => `<option value="${c.val}">${esc(c.et)}</option>`).join("")}</select></label>
      <label class="camp" style="width:160px"><span class="camp-eticheta">Suma declarată inițial <span class="oblig">*</span></span><input id="d710-i" type="number" step="1" class="camp-input"></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">Suma corectă <span class="oblig">*</span></span><input id="d710-c" type="number" step="1" class="camp-input"></label>
      <label class="camp" style="width:120px" id="d710-cota-wrap"><span class="camp-eticheta">Cotă micro (%) <span class="oblig">*</span></span><input id="d710-cota" type="number" step="0.01" class="camp-input" placeholder="1"></label>
      <button class="buton-secundar" id="d710-add">+ adaugă</button>
    </div>
    <div id="d710-msg"></div>
    <p style="margin-top:8px"><button class="buton-primar" id="d710-regen">Regenerează D710</button>
      <span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>
  </details>`;
  const gv = (id) => zona.querySelector(id);
  const comutaCota = () => { gv("#d710-cota-wrap").style.display = gv("#d710-cod").value === "121" ? "" : "none"; };
  gv("#d710-cod").addEventListener("change", comutaCota); comutaCota();
  zona.querySelectorAll(".dec-d710-del").forEach((b) => b.addEventListener("click", () => {
    S.d710_obligatii.splice(parseInt(b.dataset.idx), 1); randeazaFormularD710(corp, nav);
  }));
  gv("#d710-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    const cod = gv("#d710-cod").value;
    const i = parseFloat(gv("#d710-i").value), c = parseFloat(gv("#d710-c").value);
    const err = [];
    if (isNaN(i)) err.push(["d710-i", "Completează suma declarată inițial (cât ai pus greșit în D100)."]);
    if (isNaN(c)) err.push(["d710-c", "Completează suma corectă (cât ar fi trebuit declarat)."]);
    if (!isNaN(i) && !isNaN(c) && i <= 0 && c <= 0) err.push(["d710-c", "Cel puțin una dintre sume trebuie să fie mai mare ca 0 — altfel nu e nimic de corectat."]);
    const rand = { cod_oblig: cod, suma_dat_i: isNaN(i) ? 0 : i, suma_dat_c: isNaN(c) ? 0 : c };
    if (cod === "121") {
      const cota = parseFloat(gv("#d710-cota").value);
      if (isNaN(cota) || cota <= 0) err.push(["d710-cota", "Cota micro (1% sau 3%) e obligatorie la impozitul pe veniturile microîntreprinderilor."]);
      else rand.cota = String(cota);
    }
    if (err.length) { err.forEach(([id, m]) => eroareCamp(zona, id, m)); return; }
    S.d710_obligatii.push(rand);
    randeazaFormularD710(corp, nav);
  });
  gv("#d710-regen").addEventListener("click", () => pas2(corp, nav));
}

// tip==="d311" (TVA datorata dupa anularea codului de TVA, situatii speciale art.316(11) CF). Formular
// de PANOU (nu lista, ca d710): contabilul introduce data anularii + motivul + bazele/TVA pe cele trei
// situatii oficiale (structura_D311, rd.01/02/04). Subtotalurile si totalul de control se CALCULEAZA
// (nu se cer). Valorile stau IN MEMORIE (S.d311) si persista intre randari (Regenereaza reface pas2).
// Clasele DS: .camp/.camp-eticheta/.camp-input/.oblig + details.dec-xml, exact ca formularul D710 de pe
// acelasi ecran (identitate cu situatia similara). Situatiile (etichete din sursa oficiala ANAF):
//   A.1 OB_11/OB_12  Livrari de bunuri / prestari de servicii
//   A.2 OB_21/OB_22  Achizitii cu taxare inversa (firma e obligata la plata taxei)
//   B   OB_41/OB_42  Livrari dinainte de anulare, cu TVA la incasare exigibila in perioada fara cod valid
const _D311_SITUATII = [
  { baza: "OB_11", tva: "OB_12", et: "Livrări de bunuri / prestări de servicii" },
  { baza: "OB_21", tva: "OB_22", et: "Achiziții cu taxare inversă (firma e obligată la plata taxei)" },
  { baza: "OB_41", tva: "OB_42", et: "Livrări dinainte de anulare, cu TVA la încasare exigibilă în perioada fără cod valid de TVA" },
];
const _D311_MOTIVE = [
  { val: "1", et: "Din oficiu (art. 316 alin. (11) lit. a)–e) sau h) CF)" },
  { val: "2", et: "La cerere — firmă care aplica TVA la încasare (art. 316 alin. (11) lit. g) CF)" },
];
function _n(v) { const x = parseFloat(v); return isNaN(x) ? 0 : x; }

// Construieste `manual` pentru body din starea formularului (S.d311). Sumele goale -> 0 (Python _i le trateaza).
function _d311Manual() {
  const d = S.d311 || {};
  return {
    schema: 1,
    Data_A: d.Data_A || "",
    d_anul1: d.motiv === "1" ? 1 : 0,
    d_anul2: d.motiv === "2" ? 1 : 0,
    d_rec: d.d_rec ? 1 : 0,
    OB_11: _n(d.OB_11), OB_12: _n(d.OB_12), OB_21: _n(d.OB_21),
    OB_22: _n(d.OB_22), OB_41: _n(d.OB_41), OB_42: _n(d.OB_42),
  };
}

function randeazaFormularD311(corp, nav) {
  const zona = corp.querySelector("#dec-d311-form");
  if (!zona) return;
  const d = S.d311;
  // total de control (OB_51+OB_52), calculat identic cu backendul (structura rd.05) -> cifra afisata
  // coincide cu ce genereaza serverul (Regula 14.2: aceeasi operatiune, aceeasi cifra pe tot traseul).
  const bazaT = _n(d.OB_11) + _n(d.OB_21) + _n(d.OB_41);
  const tvaT = _n(d.OB_12) + _n(d.OB_22) + _n(d.OB_42);
  const total = bazaT + tvaT;
  const camp = (id, val) => `<input id="${id}" type="number" step="1" min="0" class="camp-input" value="${val === "" || val == null ? "" : esc(String(val))}">`;
  // eticheta pe linie proprie, apoi Baza+TVA intr-un sub-rand care se IMPACHETEAZA (flex-wrap) ->
  // nu se revarsa orizontal pe telefon (proba Pixel 5: inainte inputul TVA iesea din ecran).
  const randuri = _D311_SITUATII.map((s, i) => `
    <div class="dec-man-rand" style="flex-direction:column;align-items:stretch;gap:6px">
      <span class="dec-recl-desc" style="flex:0 0 auto">${i + 1}. ${esc(s.et)}</span>
      <div style="display:flex;flex-wrap:wrap;gap:12px">
        <label class="camp" style="flex:1 1 130px"><span class="camp-eticheta">Bază (lei)</span>${camp("d311-" + s.baza, d[s.baza])}</label>
        <label class="camp" style="flex:1 1 130px"><span class="camp-eticheta">TVA (lei)</span>${camp("d311-" + s.tva, d[s.tva])}</label>
      </div>
    </div>`).join("");
  zona.innerHTML = `<details class="dec-xml" open><summary>Situația fiscală după anularea codului de TVA</summary>
    <div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:12px">
      <label class="camp" style="width:230px"><span class="camp-eticheta">Data anulării codului de TVA <span class="oblig">*</span></span>
        <input id="d311-data" type="date" class="camp-input" value="${esc(d.Data_A || "")}"></label>
      <label class="camp" style="width:430px"><span class="camp-eticheta">Motivul anulării <span class="oblig">*</span></span>
        <select id="d311-motiv" class="camp-input">
          <option value="">— alege motivul —</option>
          ${_D311_MOTIVE.map((mo) => `<option value="${mo.val}" ${d.motiv === mo.val ? "selected" : ""}>${esc(mo.et)}</option>`).join("")}
        </select></label>
      <label class="camp" style="width:auto;flex-direction:row;align-items:center;gap:6px">
        <input id="d311-rec" type="checkbox" ${d.d_rec ? "checked" : ""}><span class="camp-eticheta" style="margin:0">Declarație rectificativă</span></label>
    </div>
    <div class="camp-eticheta" style="margin:12px 0 4px">Sume pe operațiuni <span class="oblig">*</span> (cel puțin una &gt; 0):</div>
    ${randuri}
    <p class="camp-ajutor" style="margin-top:8px">Total de plată (control): <b id="d311-total">${bani(total)} lei</b> — se calculează automat din bazele și TVA de mai sus. Subtotalurile nu se completează.</p>
    <div id="d311-msg"></div>
    <p style="margin-top:8px"><button class="buton-primar" id="d311-regen">Regenerează D311</button>
      <span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>
  </details>`;
  const gv = (id) => zona.querySelector(id);
  // legare bidirectionala: input -> S.d311 (persista intre randari). Total-ul se reface la re-randare.
  gv("#d311-data").addEventListener("change", (e) => { S.d311.Data_A = e.target.value; });
  gv("#d311-motiv").addEventListener("change", (e) => { S.d311.motiv = e.target.value; });
  gv("#d311-rec").addEventListener("change", (e) => { S.d311.d_rec = e.target.checked ? 1 : 0; });
  // totalul de control se recalculeaza LIVE la tastare (Regula 14.2: cifra afisata coincide in orice
  // moment cu ce genereaza serverul), fara re-randare completa (pastreaza focusul in camp).
  const actualizeazaTotal = () => {
    const bt = _n(S.d311.OB_11) + _n(S.d311.OB_21) + _n(S.d311.OB_41);
    const tt = _n(S.d311.OB_12) + _n(S.d311.OB_22) + _n(S.d311.OB_42);
    const el = gv("#d311-total"); if (el) el.textContent = bani(bt + tt) + " lei";
  };
  _D311_SITUATII.forEach((s) => {
    ["baza", "tva"].forEach((k) => {
      const el = gv("#d311-" + s[k]);
      el.addEventListener("input", (e) => { S.d311[s[k]] = e.target.value; actualizeazaTotal(); });
    });
  });
  gv("#d311-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    // marcheaza campul vinovat INAINTE de a chema serverul (Regula 14.4: nu doar mesaj general dupa apasare).
    const err = [];
    if (!S.d311.Data_A) err.push(["d311-data", "Completează data la care ți-a fost anulat codul de TVA."]);
    if (!S.d311.motiv) err.push(["d311-motiv", "Alege motivul anulării codului de TVA (din oficiu sau la cerere)."]);
    const m = _d311Manual();
    const totalPlata = m.OB_11 + m.OB_21 + m.OB_41 + m.OB_12 + m.OB_22 + m.OB_42;
    if (totalPlata <= 0) err.push(["d311-OB_11", "Introdu cel puțin o sumă (bază sau TVA). D311 nu se depune pe zero."]);
    if (err.length) { err.forEach(([id, msg]) => eroareCamp(zona, id, msg)); return; }
    pas2(corp, nav);
  });
}

// tip==="d307" (ajustare/corectie/regularizare TVA). LISTA de operatiuni (model IDENTIC cu D710:
// lista in memorie -> body, add/sterge/regen; D307 n-are tabel DB). Fiecare operatiune: tip
// (A=transfer active / L=leasing / C=anularea codului de TVA), cod fiscal operator, denumire operator,
// suma TVA (poate fi <=0, permis de structura). tvaA/L/C si totalPlata_A=Σtva se CALCULEAZA. Clasele DS
// dec-man-rand/dec-man-form/camp, ca d710/d311 (identitate intre situatii similare). Etichete din
// core/d307.py (art.270(7)/324/316(11) CF): A codO=cedent, L codO=finantator, C codO=beneficiar.
const _D307_TIPURI = [
  { val: "A", et: "Transfer de active (cedent)" },
  { val: "L", et: "Leasing / transfer active la finalul contractului (finanțator)" },
  { val: "C", et: "Anularea codului de TVA (beneficiar)" },
];
const _D307_TEMEI = [
  { val: "1", et: "Îndeplinirea / neîndeplinirea unei condiții prevăzute de lege (art. 105 alin. (6) lit. a) L. 207/2015)" },
  { val: "2", et: "Hotărâre judecătorească definitivă (art. 105 alin. (6) lit. b) L. 207/2015)" },
];
function _d307_et(tip) { const t = _D307_TIPURI.find((x) => x.val === tip); return t ? t.et : "Tip " + tip; }

// Construieste `manual` pentru body din starea formularului (S.d307).
function _d307Manual() {
  const d = S.d307 || {};
  return {
    operatiuni: (d.operatiuni || []).map((o) => ({ tip: o.tip, cod: o.cod, den: o.den, tva: o.tva })),
    d_rec: d.d_rec ? 1 : 0,
    d_anulare: d.d_anulare ? 1 : 0,
    temei: d.d_anulare ? (d.temei || "") : "",
  };
}

function randeazaFormularD307(corp, nav) {
  const zona = corp.querySelector("#dec-d307-form");
  if (!zona) return;
  const d = S.d307;
  const ops = d.operatiuni || [];
  const total = ops.reduce((s, o) => s + (_n(o.tva) || 0), 0);
  const grila = ops.length
    ? ops.map((o, i) => `<div class="dec-man-rand">
        <span class="dec-recl-desc">${esc(_d307_et(o.tip))} · ${esc(o.den)} (CUI ${esc(String(o.cod))}) · TVA ${bani(o.tva)} lei</span>
        <button class="btn-link dec-d307-del" data-idx="${i}">șterge</button></div>`).join("")
    : `<div class="stare-goala stare-goala--inline">Nicio operațiune. D307 declară sumele de TVA din ajustări — adaugă mai jos fiecare operațiune (transfer de active, leasing, ori anularea codului de TVA).</div>`;
  zona.innerHTML = `<details class="dec-xml" open><summary>Operațiuni de ajustare TVA (${ops.length})</summary>
    <div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:6px">
      <label class="camp" style="width:auto;flex-direction:row;align-items:center;gap:6px">
        <input id="d307-rec" type="checkbox" ${d.d_rec ? "checked" : ""}><span class="camp-eticheta" style="margin:0">Declarație rectificativă</span></label>
      <label class="camp" style="width:auto;flex-direction:row;align-items:center;gap:6px">
        <input id="d307-anul" type="checkbox" ${d.d_anulare ? "checked" : ""}><span class="camp-eticheta" style="margin:0">Corectată după anularea rezervei verificării</span></label>
      <label class="camp" id="d307-temei-wrap" style="width:520px;${d.d_anulare ? "" : "display:none"}"><span class="camp-eticheta">Temeiul legal al corectării <span class="oblig">*</span></span>
        <select id="d307-temei" class="camp-input"><option value="">— alege temeiul —</option>
          ${_D307_TEMEI.map((t) => `<option value="${t.val}" ${d.temei === t.val ? "selected" : ""}>${esc(t.et)}</option>`).join("")}</select></label>
    </div>
    ${grila}
    <div class="camp-eticheta" style="margin:12px 0 4px">Adaugă operațiune:</div>
    <div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">
      <label class="camp" style="width:360px"><span class="camp-eticheta">Tipul operațiunii <span class="oblig">*</span></span>
        <select id="d307-tip" class="camp-input">${_D307_TIPURI.map((t) => `<option value="${t.val}">${esc(t.et)}</option>`).join("")}</select></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">CUI operator <span class="oblig">*</span></span><input id="d307-cod" type="text" class="camp-input"></label>
      <label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Denumire operator <span class="oblig">*</span></span><input id="d307-den" type="text" class="camp-input"></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">TVA (lei) <span class="oblig">*</span></span><input id="d307-tva" type="number" step="1" class="camp-input"></label>
      <button class="buton-secundar" id="d307-add">+ adaugă</button>
    </div>
    <div id="d307-msg"></div>
    <p class="camp-ajutor" style="margin-top:8px">Total ajustare TVA: <b>${bani(total)} lei</b> — se calculează automat din operațiunile de mai sus.</p>
    <p style="margin-top:8px"><button class="buton-primar" id="d307-regen">Regenerează D307</button>
      <span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>
  </details>`;
  const gv = (id) => zona.querySelector(id);
  gv("#d307-rec").addEventListener("change", (e) => { S.d307.d_rec = e.target.checked ? 1 : 0; });
  gv("#d307-anul").addEventListener("change", (e) => {
    S.d307.d_anulare = e.target.checked ? 1 : 0;
    gv("#d307-temei-wrap").style.display = e.target.checked ? "" : "none";
  });
  gv("#d307-temei").addEventListener("change", (e) => { S.d307.temei = e.target.value; });
  zona.querySelectorAll(".dec-d307-del").forEach((b) => b.addEventListener("click", () => {
    S.d307.operatiuni.splice(parseInt(b.dataset.idx), 1); randeazaFormularD307(corp, nav);
  }));
  gv("#d307-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    const tip = gv("#d307-tip").value;
    const cod = gv("#d307-cod").value.trim();
    const den = gv("#d307-den").value.trim();
    const tvaRaw = gv("#d307-tva").value;
    const err = [];
    if (!cod) err.push(["d307-cod", "Completează codul fiscal (CUI) al operatorului."]);
    if (!den) err.push(["d307-den", "Completează denumirea operatorului (cedent / finanțator / beneficiar)."]);
    if (tvaRaw === "" || isNaN(parseFloat(tvaRaw))) err.push(["d307-tva", "Completează suma TVA a operațiunii (poate fi și negativă la regularizare)."]);
    if (err.length) { err.forEach(([id, m]) => eroareCamp(zona, id, m)); return; }
    S.d307.operatiuni.push({ tip: tip, cod: cod, den: den, tva: parseFloat(tvaRaw) });
    randeazaFormularD307(corp, nav);
  });
  gv("#d307-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    // marcheaza campul vinovat INAINTE de a chema serverul (Regula 14.4)
    if (!(S.d307.operatiuni || []).length) {
      eroareCamp(zona, "d307-cod", "Adaugă cel puțin o operațiune de ajustare (butonul + adaugă). D307 nu se depune fără operațiuni.");
      return;
    }
    if (S.d307.d_anulare && !S.d307.temei) {
      eroareCamp(zona, "d307-temei", "Alege temeiul legal al corectării (ai bifat că declarația corectează una depusă după anularea rezervei).");
      return;
    }
    pas2(corp, nav);
  });
}

// tip==="d107" (informativa sponsorizari/mecenat/burse, exercitiu pe an calendaristic). Formular-lista de
// beneficiari (ca d307): fiecare cu denumire, cod fiscal, adresa si trei sume - acordata (Suma), reportata,
// dedusa. Anexa beneficiarilor neindividualizati exista DOAR daca suma reportata a lor > 0 (regula
// validatorului ANAF). Valorile stau IN MEMORIE (S.d107), persista intre randari (Regenereaza reface pas2).
// Totalurile pe cele trei coloane + suma de control se calculeaza si se afiseaza.
function _d107Manual() {
  const d = S.d107 || {};
  const ni = _n(d.val2_ni) > 0 ? (d.neindividualizati || []).map((n) => ({ den: n.den, cif: n.cif, adresa: n.adresa })) : [];
  return {
    beneficiari: (d.beneficiari || []).map((b) => ({ den: b.den, cif: b.cif, adresa: b.adresa, val1: b.val1, val2: b.val2, val3: b.val3 })),
    val2_ni: d.val2_ni, val3_ni: d.val3_ni,
    neindividualizati: ni,
    d_rec: d.d_rec ? 1 : 0,
  };
}

function randeazaFormularD107(corp, nav) {
  const zona = corp.querySelector("#dec-d107-form");
  if (!zona) return;
  const d = S.d107;
  const benef = d.beneficiari || [];
  const val2ni = _n(d.val2_ni), val3ni = _n(d.val3_ni);
  const ni = d.neindividualizati || [];
  const tval1 = benef.reduce((s, b) => s + (_n(b.val1) || 0), 0);
  const tval2 = benef.reduce((s, b) => s + (_n(b.val2) || 0), 0) + val2ni;
  const tval3 = benef.reduce((s, b) => s + (_n(b.val3) || 0), 0) + val3ni;
  const total = tval1 + tval2 + tval3;
  const grila = benef.length
    ? benef.map((b, i) => `<div class="dec-man-rand">
        <span class="dec-recl-desc">${esc(b.den)} (CUI ${esc(String(b.cif))}) · acordată ${bani(b.val1)} · reportată ${bani(b.val2)} · dedusă ${bani(b.val3)} lei</span>
        <button class="btn-link dec-d107-del" data-idx="${i}">șterge</button></div>`).join("")
    : `<div class="stare-goala stare-goala--inline">Niciun beneficiar. D107 declară beneficiarii sponsorizărilor, mecenatului și burselor private — adaugă mai jos fiecare beneficiar cu sumele acordate.</div>`;
  const grilaNI = ni.length
    ? ni.map((n, i) => `<div class="dec-man-rand">
        <span class="dec-recl-desc">${esc(n.den)} (CUI ${esc(String(n.cif))}) · ${esc(n.adresa)}</span>
        <button class="btn-link dec-d107-ni-del" data-idx="${i}">șterge</button></div>`).join("")
    : `<div class="stare-goala stare-goala--inline">Niciun beneficiar neindividualizat.</div>`;
  zona.innerHTML = `<details class="dec-xml" open><summary>Beneficiarii sponsorizărilor / mecenatului / burselor (${benef.length})</summary>
    <div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:6px">
      <label class="camp" style="width:auto;flex-direction:row;align-items:center;gap:6px">
        <input id="d107-rec" type="checkbox" ${d.d_rec ? "checked" : ""}><span class="camp-eticheta" style="margin:0">Declarație rectificativă</span></label>
    </div>
    ${grila}
    <div class="camp-eticheta" style="margin:12px 0 4px">Adaugă beneficiar:</div>
    <div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">
      <label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Denumire / nume beneficiar <span class="oblig">*</span></span><input id="d107-den" type="text" class="camp-input"></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">CUI / CNP <span class="oblig">*</span></span><input id="d107-cif" type="text" class="camp-input"></label>
      <label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Adresă <span class="oblig">*</span></span><input id="d107-adr" type="text" class="camp-input"></label>
      <label class="camp" style="width:130px"><span class="camp-eticheta">Suma acordată (lei)</span><input id="d107-val1" type="number" step="1" min="0" class="camp-input"></label>
      <label class="camp" style="width:130px"><span class="camp-eticheta">Suma reportată (lei)</span><input id="d107-val2" type="number" step="1" min="0" class="camp-input"></label>
      <label class="camp" style="width:130px"><span class="camp-eticheta">Suma dedusă (lei)</span><input id="d107-val3" type="number" step="1" min="0" class="camp-input"></label>
      <button class="buton-secundar" id="d107-add">+ adaugă</button>
    </div>
    <div id="d107-msg"></div>
    <details class="dec-xml" style="margin-top:10px"><summary>Anexă — beneficiari neindividualizați (rar)</summary>
      <p class="camp-ajutor">Se completează doar dacă ai sume reportate/deduse pentru beneficiari care nu se individualizează. Lista cu numele lor apare doar când suma reportată de mai jos este mai mare ca zero.</p>
      <div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">
        <label class="camp" style="width:200px"><span class="camp-eticheta">Suma reportată neindividualizați (lei)</span><input id="d107-val2ni" type="number" step="1" min="0" class="camp-input" value="${esc(String(d.val2_ni || ""))}"></label>
        <label class="camp" style="width:200px"><span class="camp-eticheta">Suma dedusă neindividualizați (lei)</span><input id="d107-val3ni" type="number" step="1" min="0" class="camp-input" value="${esc(String(d.val3_ni || ""))}"></label>
      </div>
      ${val2ni > 0 ? `${grilaNI}
        <div class="camp-eticheta" style="margin:12px 0 4px">Adaugă beneficiar neindividualizat:</div>
        <div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">
          <label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Denumire / nume <span class="oblig">*</span></span><input id="d107-ni-den" type="text" class="camp-input"></label>
          <label class="camp" style="width:150px"><span class="camp-eticheta">CUI / CNP <span class="oblig">*</span></span><input id="d107-ni-cif" type="text" class="camp-input"></label>
          <label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Adresă <span class="oblig">*</span></span><input id="d107-ni-adr" type="text" class="camp-input"></label>
          <button class="buton-secundar" id="d107-ni-add">+ adaugă</button>
        </div>` : ""}
      <div id="d107-ni-msg"></div>
    </details>
    <p class="camp-ajutor" id="d107-totaluri" style="margin-top:8px">Totaluri: acordată <b>${bani(tval1)}</b> · reportată <b>${bani(tval2)}</b> · dedusă <b>${bani(tval3)}</b> lei. Suma de control (total): <b>${bani(total)} lei</b> — se calculează automat din sumele de mai sus.</p>
    <p style="margin-top:8px"><button class="buton-primar" id="d107-regen">Regenerează D107</button>
      <span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>
  </details>`;
  const gv = (id) => zona.querySelector(id);
  gv("#d107-rec").addEventListener("change", (e) => { S.d107.d_rec = e.target.checked ? 1 : 0; });
  gv("#d107-val2ni").addEventListener("change", (e) => { S.d107.val2_ni = e.target.value; randeazaFormularD107(corp, nav); });
  gv("#d107-val3ni").addEventListener("change", (e) => { S.d107.val3_ni = e.target.value; randeazaFormularD107(corp, nav); });
  zona.querySelectorAll(".dec-d107-del").forEach((b) => b.addEventListener("click", () => {
    S.d107.beneficiari.splice(parseInt(b.dataset.idx), 1); randeazaFormularD107(corp, nav);
  }));
  zona.querySelectorAll(".dec-d107-ni-del").forEach((b) => b.addEventListener("click", () => {
    S.d107.neindividualizati.splice(parseInt(b.dataset.idx), 1); randeazaFormularD107(corp, nav);
  }));
  gv("#d107-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    const den = gv("#d107-den").value.trim();
    const cif = gv("#d107-cif").value.trim();
    const adr = gv("#d107-adr").value.trim();
    const err = [];
    if (!den) err.push(["d107-den", "Completează denumirea sau numele beneficiarului."]);
    if (!cif) err.push(["d107-cif", "Completează codul de identificare fiscală (CUI sau CNP)."]);
    if (!adr) err.push(["d107-adr", "Completează adresa beneficiarului."]);
    if (err.length) { err.forEach(([id, m]) => eroareCamp(zona, id, m)); return; }
    S.d107.beneficiari.push({ den: den, cif: cif, adresa: adr,
      val1: gv("#d107-val1").value, val2: gv("#d107-val2").value, val3: gv("#d107-val3").value });
    randeazaFormularD107(corp, nav);
  });
  const addNi = gv("#d107-ni-add");
  if (addNi) addNi.addEventListener("click", () => {
    curataEroriCamp(zona);
    const den = gv("#d107-ni-den").value.trim();
    const cif = gv("#d107-ni-cif").value.trim();
    const adr = gv("#d107-ni-adr").value.trim();
    const err = [];
    if (!den) err.push(["d107-ni-den", "Completează denumirea sau numele beneficiarului neindividualizat."]);
    if (!cif) err.push(["d107-ni-cif", "Completează codul de identificare fiscală."]);
    if (!adr) err.push(["d107-ni-adr", "Completează adresa."]);
    if (err.length) { err.forEach(([id, m]) => eroareCamp(zona, id, m)); return; }
    S.d107.neindividualizati.push({ den: den, cif: cif, adresa: adr });
    randeazaFormularD107(corp, nav);
  });
  gv("#d107-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    // marcheaza campul vinovat INAINTE de a chema serverul (Regula 14.4)
    if (!(S.d107.beneficiari || []).length) {
      eroareCamp(zona, "d107-den", "Adaugă cel puțin un beneficiar (butonul + adaugă). D107 nu se depune fără beneficiari.");
      return;
    }
    if (_n(S.d107.val2_ni) > 0 && !(S.d107.neindividualizati || []).length) {
      eroareCamp(zona, "d107-val2ni", "Ai o sumă reportată pentru beneficiari neindividualizați — adaugă-i în anexă sau șterge suma.");
      return;
    }
    pas2(corp, nav);
  });
}

const _D177_TIPB = [
  { val: "1", et: "Sponsorizare — persoane juridice fără scop lucrativ, inclusiv unități de cult" },
  { val: "2", et: "Sponsorizare — alți beneficiari, potrivit legii" },
  { val: "3", et: "Act de mecenat (persoană fizică)" },
  { val: "5", et: "UNICEF și alte organizații internaționale" },
];
function _d177TipEt(t) { const x = _D177_TIPB.find((y) => y.val === t); return x ? x.et : "Tip " + t; }

// tip==="d177" (cerere de redirectionare a unei parti din impozitul pe profit catre entitati nonprofit /
// unitati de cult, art.25(4)i/t CF). Formular-lista de beneficiari (ca d107/d307) + un antet cu plafoanele
// (suma maxima redirectionabila / redirectionata anterior / ramasa) si perioada fiscala. Fiecare beneficiar:
// tip (cult/nonprofit/mecenat/UNICEF), cod fiscal (CUI, ori CNP la mecenat), denumire, IBAN, suma, acord de
// informare, si contract (obligatoriu la tip 1/2/3, nu la UNICEF). Suma de control = 0 (D177 e informativa).
// Valorile stau IN MEMORIE (S.d177), persista intre randari. Zero clase noi.
function _d177Manual() {
  const d = S.d177 || {};
  return {
    tip_platitor: 1,
    data_inceput: d.data_inceput, data_sfarsit: d.data_sfarsit,
    suma_max: d.suma_max, suma_ant: d.suma_ant, suma_rest: d.suma_rest,
    d_rec: d.d_rec ? 1 : 0,
    beneficiari: (d.beneficiari || []).map((b) => ({
      tip: b.tip, cui: b.cui, den: b.den, iban: b.iban, suma: b.suma,
      acord: b.acord ? "1" : "0", adresa: b.adresa || "", contract: b.contract || "",
    })),
  };
}

function randeazaFormularD177(corp, nav) {
  const zona = corp.querySelector("#dec-d177-form");
  if (!zona) return;
  const d = S.d177;
  if (!d.data_inceput) d.data_inceput = S.an + "-01-01";
  if (!d.data_sfarsit) d.data_sfarsit = S.an + "-12-31";
  const benef = d.beneficiari || [];
  const srest = _n(d.suma_rest);
  const totB = benef.reduce((s, b) => s + _n(b.suma), 0);
  const ramas = srest - totB;
  const grila = benef.length
    ? benef.map((b, i) => `<div class="dec-man-rand">
        <span class="dec-recl-desc">${esc(_d177TipEt(b.tip))} · ${esc(b.den)} (${b.tip === "3" ? "CNP" : "CUI"} ${esc(String(b.cui))}) · ${bani(_n(b.suma))} lei${b.contract ? " · contract " + esc(b.contract) : ""} · ${b.acord ? "cu acord de informare" : "fără acord de informare"}</span>
        <button class="btn-link dec-d177-del" data-idx="${i}">șterge</button></div>`).join("")
    : `<div class="stare-goala stare-goala--inline">Niciun beneficiar. D177 redirecționează o parte din impozitul pe profit către entități nonprofit / unități de cult — adaugă mai jos fiecare beneficiar cu suma redirecționată.</div>`;
  zona.innerHTML = `<details class="dec-xml" open><summary>Redirecționarea impozitului pe profit (${benef.length} beneficiari)</summary>
    <p class="camp-ajutor">Plătitor de impozit pe profit. Suma maximă redirecționabilă = min(20% din impozitul pe profit, 0,75% din cifra de afaceri) — o calculezi din situația firmei și o treci mai jos.</p>
    <div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:6px">
      <label class="camp" style="width:150px"><span class="camp-eticheta">Perioada de la <span class="oblig">*</span></span><input id="d177-di" type="date" class="camp-input" value="${esc(d.data_inceput)}"></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">până la <span class="oblig">*</span></span><input id="d177-ds" type="date" class="camp-input" value="${esc(d.data_sfarsit)}"></label>
      <label class="camp" style="width:180px"><span class="camp-eticheta">Suma maximă redirecționabilă (lei) <span class="oblig">*</span></span><input id="d177-smax" type="number" step="1" min="0" class="camp-input" value="${esc(String(d.suma_max || ""))}"></label>
      <label class="camp" style="width:180px"><span class="camp-eticheta">Redirecționată anterior (lei)</span><input id="d177-sant" type="number" step="1" min="0" class="camp-input" value="${esc(String(d.suma_ant || ""))}"></label>
      <label class="camp" style="width:180px"><span class="camp-eticheta">Rămasă de redirecționat (lei) <span class="oblig">*</span></span><input id="d177-srest" type="number" step="1" min="0" class="camp-input" value="${esc(String(d.suma_rest || ""))}"></label>
      <label class="camp" style="width:auto;flex-direction:row;align-items:center;gap:6px">
        <input id="d177-rec" type="checkbox" ${d.d_rec ? "checked" : ""}><span class="camp-eticheta" style="margin:0">Declarație rectificativă</span></label>
    </div>
    ${grila}
    <div class="camp-eticheta" style="margin:12px 0 4px">Adaugă beneficiar:</div>
    <div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">
      <label class="camp" style="flex:1 1 320px"><span class="camp-eticheta">Tipul beneficiarului <span class="oblig">*</span></span>
        <select id="d177-tip" class="camp-input">${_D177_TIPB.map((t) => `<option value="${t.val}">${esc(t.et)}</option>`).join("")}</select></label>
      <label class="camp" style="width:160px"><span class="camp-eticheta" id="d177-cui-et">CUI beneficiar <span class="oblig">*</span></span><input id="d177-cui" type="text" class="camp-input"></label>
      <label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Denumire / nume beneficiar <span class="oblig">*</span></span><input id="d177-den" type="text" class="camp-input"></label>
      <label class="camp" style="width:240px"><span class="camp-eticheta">IBAN (RO…) <span class="oblig">*</span></span><input id="d177-iban" type="text" class="camp-input"></label>
      <label class="camp" style="width:160px"><span class="camp-eticheta">Suma redirecționată (lei) <span class="oblig">*</span></span><input id="d177-suma" type="number" step="1" min="0" class="camp-input"></label>
      <label class="camp" id="d177-contract-wrap" style="width:190px"><span class="camp-eticheta">Nr. și data contractului <span class="oblig">*</span></span><input id="d177-contract" type="text" class="camp-input"></label>
      <label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Adresa beneficiar</span><input id="d177-adr" type="text" class="camp-input"></label>
      <label class="camp" style="width:auto;flex-direction:row;align-items:center;gap:6px">
        <input id="d177-acord" type="checkbox"><span class="camp-eticheta" style="margin:0">Sunt de acord cu informarea beneficiarului</span></label>
      <button class="buton-secundar" id="d177-add">+ adaugă</button>
    </div>
    <div id="d177-msg"></div>
    <p class="camp-ajutor" id="d177-totaluri" style="margin-top:8px">Alocat beneficiarilor: <b>${bani(totB)}</b> din <b>${bani(srest)}</b> lei rămași · nealocat: <b>${bani(ramas)}</b> lei. Suma de control a declarației este 0 (D177 e informativă).</p>
    <p style="margin-top:8px"><button class="buton-primar" id="d177-regen">Regenerează D177</button>
      <span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>
  </details>`;
  const gv = (id) => zona.querySelector(id);
  gv("#d177-di").addEventListener("change", (e) => { S.d177.data_inceput = e.target.value; });
  gv("#d177-ds").addEventListener("change", (e) => { S.d177.data_sfarsit = e.target.value; });
  gv("#d177-smax").addEventListener("change", (e) => { S.d177.suma_max = e.target.value; });
  gv("#d177-sant").addEventListener("change", (e) => { S.d177.suma_ant = e.target.value; });
  gv("#d177-srest").addEventListener("change", (e) => { S.d177.suma_rest = e.target.value; randeazaFormularD177(corp, nav); });
  gv("#d177-rec").addEventListener("change", (e) => { S.d177.d_rec = e.target.checked ? 1 : 0; });
  const syncTip = () => {
    const t = gv("#d177-tip").value;
    gv("#d177-contract-wrap").style.display = (t === "5") ? "none" : "";
    gv("#d177-cui-et").firstChild.textContent = (t === "3") ? "CNP beneficiar " : "CUI beneficiar ";
  };
  gv("#d177-tip").addEventListener("change", syncTip); syncTip();
  zona.querySelectorAll(".dec-d177-del").forEach((btn) => btn.addEventListener("click", () => {
    S.d177.beneficiari.splice(parseInt(btn.dataset.idx), 1); randeazaFormularD177(corp, nav);
  }));
  gv("#d177-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    const tip = gv("#d177-tip").value;
    const cui = gv("#d177-cui").value.trim();
    const den = gv("#d177-den").value.trim();
    const iban = gv("#d177-iban").value.replace(/\s/g, "").toUpperCase();
    const sumaRaw = gv("#d177-suma").value;
    const contract = gv("#d177-contract").value.trim();
    const adr = gv("#d177-adr").value.trim();
    const acord = gv("#d177-acord").checked;
    const err = [];
    if (!cui) err.push(["d177-cui", tip === "3" ? "Completează CNP-ul beneficiarului." : "Completează codul fiscal (CUI) al beneficiarului."]);
    if (!den) err.push(["d177-den", "Completează denumirea sau numele beneficiarului."]);
    if (!/^RO[0-9]{2}[0-9A-Z]{20}$/.test(iban)) err.push(["d177-iban", "IBAN-ul trebuie să înceapă cu RO și să aibă 24 de caractere."]);
    if (sumaRaw === "" || isNaN(parseFloat(sumaRaw)) || parseFloat(sumaRaw) <= 0) err.push(["d177-suma", "Completează suma redirecționată (mai mare ca zero)."]);
    if (tip !== "5" && !contract) err.push(["d177-contract", "Completează numărul și data contractului de sponsorizare / mecenat."]);
    if (err.length) { err.forEach(([id, m]) => eroareCamp(zona, id, m)); return; }
    S.d177.beneficiari.push({ tip: tip, cui: cui, den: den, iban: iban, suma: sumaRaw, contract: contract, adresa: adr, acord: acord ? 1 : 0 });
    randeazaFormularD177(corp, nav);
  });
  gv("#d177-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    // marcheaza campul vinovat INAINTE de a chema serverul (Regula 14.4)
    if (!(S.d177.beneficiari || []).length) {
      eroareCamp(zona, "d177-cui", "Adaugă cel puțin un beneficiar (butonul + adaugă). D177 nu se depune fără beneficiari.");
      return;
    }
    if (_n(S.d177.suma_rest) <= 0) { eroareCamp(zona, "d177-srest", "Completează suma rămasă de redirecționat (mai mare ca zero)."); return; }
    if (_n(S.d177.suma_max) < _n(S.d177.suma_ant) + _n(S.d177.suma_rest)) {
      eroareCamp(zona, "d177-smax", "Suma maximă trebuie să fie cel puțin cât suma redirecționată anterior plus suma rămasă."); return;
    }
    if (!S.d177.data_inceput || !S.d177.data_sfarsit) { eroareCamp(zona, "d177-di", "Completează perioada fiscală (de la / până la)."); return; }
    const totB = (S.d177.beneficiari || []).reduce((s, b) => s + _n(b.suma), 0);
    if (totB > _n(S.d177.suma_rest)) { eroareCamp(zona, "d177-srest", "Suma alocată beneficiarilor depășește suma rămasă de redirecționat."); return; }
    pas2(corp, nav);
  });
}

// tip==="d200" (venituri realizate din Romania - persoane fizice, anuala). Formular-LISTA de sectiuni pe
// categorie de venit (ca d207): identitate contribuabil (CNP/nume/adresa) + cate o sectiune per categorie.
// Nomenclatorul categ_venit = din structura oficiala ANAF (structura_D200, lista curenta 1,2,3,4,5,7,9,10,13,14);
// codul 15 (alte surse) e in afara plajei acceptate de core/d200.py, deci nu e oferit. Regulile pe categorie
// (14=castig/pierdere; 13=cere organizator) din core/d200.py, probate pe validatorul D200 v3. Zero clase noi.
// venit_net se calculeaza (venit_brut-chelt); impozitul NU se declara aici (il stabileste ANAF). Valorile stau
// IN MEMORIE (S.d200), persista intre randari. Sume in LEI intregi.
const _D200_CATEG = [
  ["1", "Venituri din activități de producție, comerț, prestări servicii"],
  ["2", "Venituri din profesii liberale"],
  ["3", "Venituri din drepturi de proprietate intelectuală"],
  ["4", "Venituri din cedarea folosinței bunurilor"],
  ["5", "Venituri din activități agricole"],
  ["7", "Venituri din cedarea folosinței bunurilor calificată ca activitate independentă"],
  ["9", "Venituri din silvicultură"],
  ["10", "Venituri din piscicultură"],
  ["13", "Venituri din jocuri de noroc"],
  ["14", "Câștig din transferul titlurilor de valoare și alte instrumente financiare"],
];
function _d200EsteCastig(c) { return String(c) === "14"; }
function _d200CereOrg(c) { return String(c) === "13"; }
function _d200CategEt(c) {
  const x = _D200_CATEG.find((y) => y[0] === String(c)); return x ? x[0] + " — " + x[1] : "categoria " + c;
}

function _d200Manual() {
  const d = S.d200 || {};
  return {
    cif_i: (d.cif_i || "").trim(),
    nume_c: (d.nume_c || "").trim(),
    prenume_c: (d.prenume_c || "").trim(),
    den_i: ((d.nume_c || "").trim() + " " + (d.prenume_c || "").trim()).trim(),  // identificare = nume + prenume
    adresa_i: (d.adresa_i || "").trim(),
    cont_c: (d.cont_c || "").replace(/\s+/g, "").toUpperCase(),
    sectiuni: (d.sectiuni || []).map((s) => ({
      categ_venit: s.categ_venit, caen: s.caen || "",
      venit_brut: s.venit_brut || 0, chelt: s.chelt || 0,
      castig: s.castig || 0, pierdere: s.pierdere || 0,
      den_orgJN: s.den_orgJN || "", cif_orgJN: s.cif_orgJN || "",
    })),
    d_rec: d.d_rec ? 1 : 0,
  };
}

function randeazaFormularD200(corp, nav) {
  const zona = corp.querySelector("#dec-d200-form");
  if (!zona) return;
  const d = S.d200;
  const sec = d.sectiuni || [];
  // oglinda calcul_d200: suma de control = suma pe sectiuni a (venit_net + castig + pierdere)
  let total = 0;
  const grila = sec.length
    ? sec.map((s, i) => {
        const c = String(s.categ_venit);
        let rez;
        if (_d200EsteCastig(c)) {
          const cg = Math.round(_n(s.castig) || 0), pj = Math.round(_n(s.pierdere) || 0);
          total += cg + pj; rez = cg > 0 ? ("câștig " + bani(cg)) : ("pierdere " + bani(pj));
        } else {
          const vb = Math.round(_n(s.venit_brut) || 0), ch = Math.round(_n(s.chelt) || 0);
          const vn = Math.max(0, vb - ch), pd = Math.max(0, ch - vb);
          total += vn + pd; rez = "venit net " + bani(vn) + (pd > 0 ? (" · pierdere " + bani(pd)) : "");
        }
        return '<div class="dec-man-rand"><span class="dec-recl-desc">' + esc(_d200CategEt(c)) +
          (s.caen ? (" · CAEN " + esc(s.caen)) : "") + (s.den_orgJN ? (" · " + esc(s.den_orgJN)) : "") +
          " · " + rez + ' lei</span><button class="btn-link dec-d200-del" data-idx="' + i + '">șterge</button></div>';
      }).join("")
    : '<div class="stare-goala stare-goala--inline">Nicio secțiune de venit. D200 declară veniturile realizate din România, pe categorii — adaugă mai jos fiecare categorie de venit.</div>';
  const optCateg = _D200_CATEG.map((c) => '<option value="' + c[0] + '">' + esc(c[0] + " — " + c[1]) + '</option>').join("");
  zona.innerHTML = '<details class="dec-xml" open><summary>Contribuabil + secțiuni de venit (' + sec.length + ')</summary>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:180px"><span class="camp-eticheta">CNP contribuabil <span class="oblig">*</span></span><input id="d200-cnp" type="text" maxlength="13" class="camp-input" value="' + esc(d.cif_i || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 160px"><span class="camp-eticheta">Nume <span class="oblig">*</span></span><input id="d200-nume" type="text" class="camp-input" value="' + esc(d.nume_c || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 160px"><span class="camp-eticheta">Prenume <span class="oblig">*</span></span><input id="d200-pren" type="text" class="camp-input" value="' + esc(d.prenume_c || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 260px"><span class="camp-eticheta">Adresa <span class="oblig">*</span></span><input id="d200-adr" type="text" class="camp-input" value="' + esc(d.adresa_i || "") + '"></label>' +
      '<label class="camp" style="width:230px"><span class="camp-eticheta">IBAN restituire (opțional)</span><input id="d200-iban" type="text" class="camp-input" value="' + esc(d.cont_c || "") + '"></label>' +
      '<label class="set-bifa"><input id="d200-rec" type="checkbox" ' + (d.d_rec ? "checked" : "") + '> <span>Rectificativă</span></label>' +
    '</div>' + grila +
    '<div class="camp-eticheta" style="margin:12px 0 4px">Adaugă secțiune de venit:</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">' +
      '<label class="camp" style="flex:1 1 320px"><span class="camp-eticheta">Categoria de venit <span class="oblig">*</span></span><select id="d200-categ" class="camp-input">' + optCateg + '</select></label>' +
      '<label class="camp" style="width:110px"><span class="camp-eticheta">CAEN</span><input id="d200-caen" type="text" maxlength="4" class="camp-input"></label>' +
      '<label class="camp d200-vn" style="width:150px"><span class="camp-eticheta">Venit brut (lei)</span><input id="d200-vb" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp d200-vn" style="width:150px"><span class="camp-eticheta">Cheltuieli (lei)</span><input id="d200-ch" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp d200-cg" style="width:150px"><span class="camp-eticheta">Câștig (lei)</span><input id="d200-cg" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp d200-cg" style="width:150px"><span class="camp-eticheta">Pierdere (lei)</span><input id="d200-pd" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp d200-org" style="flex:1 1 220px"><span class="camp-eticheta">Denumire organizator</span><input id="d200-den" type="text" class="camp-input"></label>' +
      '<label class="camp d200-org" style="width:160px"><span class="camp-eticheta">CUI organizator</span><input id="d200-cifo" type="text" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d200-add">+ adaugă</button>' +
    '</div>' +
    '<p class="camp-ajutor" id="d200-nota" style="margin:4px 0 0"></p>' +
    '<div id="d200-msg"></div>' +
    '<p class="camp-ajutor" id="d200-totaluri" style="margin-top:8px">' + sec.length + ' secțiune(i) · suma de control (venit net + câștig + pierdere): <b>' + total + '</b> lei — impozitul NU se declară aici (îl stabilește ANAF prin decizie de impunere).</p>' +
    '<p style="margin-top:8px"><button class="buton-primar" id="d200-regen">Regenerează D200</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  '</details>';
  const gv = (id) => zona.querySelector(id);
  const salveazaAntet = () => {
    S.d200.cif_i = gv("#d200-cnp").value.trim();
    S.d200.nume_c = gv("#d200-nume").value.trim();
    S.d200.prenume_c = gv("#d200-pren").value.trim();
    S.d200.adresa_i = gv("#d200-adr").value.trim();
    S.d200.cont_c = gv("#d200-iban").value.trim();
    S.d200.d_rec = gv("#d200-rec").checked ? 1 : 0;
  };
  ["#d200-cnp", "#d200-nume", "#d200-pren", "#d200-adr", "#d200-iban"].forEach((id) => gv(id).addEventListener("change", salveazaAntet));
  gv("#d200-rec").addEventListener("change", salveazaAntet);
  const reflCateg = () => {
    const c = gv("#d200-categ").value, cg = _d200EsteCastig(c), org = _d200CereOrg(c);
    zona.querySelectorAll(".d200-vn").forEach((e) => { e.style.display = cg ? "none" : ""; });
    zona.querySelectorAll(".d200-cg").forEach((e) => { e.style.display = cg ? "" : "none"; });
    zona.querySelectorAll(".d200-org").forEach((e) => { e.style.display = org ? "" : "none"; });
    gv("#d200-nota").textContent = cg
      ? "Categorie pe câștig/pierdere: completează câștigul SAU pierderea (nu venit brut/cheltuieli)."
      : (org ? "Jocuri de noroc: completează denumirea și CUI-ul organizatorului." : "");
  };
  gv("#d200-categ").addEventListener("change", reflCateg);
  reflCateg();
  zona.querySelectorAll(".dec-d200-del").forEach((b) => b.addEventListener("click", () => {
    S.d200.sectiuni.splice(parseInt(b.dataset.idx), 1); randeazaFormularD200(corp, nav);
  }));
  gv("#d200-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    const c = gv("#d200-categ").value, caen = gv("#d200-caen").value.trim();
    const cg = _d200EsteCastig(c), org = _d200CereOrg(c);
    const err = [];
    const s = { categ_venit: parseInt(c, 10), caen: caen };
    if (cg) {
      s.castig = Math.round(_n(gv("#d200-cg").value) || 0);
      s.pierdere = Math.round(_n(gv("#d200-pd").value) || 0);
      if (s.castig <= 0 && s.pierdere <= 0) err.push(["d200-cg", "Completează câștigul sau pierderea (una dintre ele > 0)."]);
    } else {
      s.venit_brut = Math.round(_n(gv("#d200-vb").value) || 0);
      s.chelt = Math.round(_n(gv("#d200-ch").value) || 0);
    }
    if (org) {
      s.den_orgJN = gv("#d200-den").value.trim();
      s.cif_orgJN = gv("#d200-cifo").value.trim();
      if (!s.den_orgJN) err.push(["d200-den", "Jocuri de noroc: completează denumirea organizatorului."]);
      if (!s.cif_orgJN) err.push(["d200-cifo", "Jocuri de noroc: completează CUI-ul organizatorului."]);
    }
    if (err.length) { err.forEach(([id, m]) => eroareCamp(zona, id, m)); return; }
    salveazaAntet();
    S.d200.sectiuni.push(s);
    randeazaFormularD200(corp, nav);
  });
  gv("#d200-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveazaAntet();
    if (!(S.d200.sectiuni || []).length) {
      eroareCamp(zona, "d200-categ", "Adaugă cel puțin o secțiune de venit (butonul + adaugă). D200 nu se depune fără venituri.");
      return;
    }
    pas2(corp, nav);
  });
}

// tip==="d201" (venituri din strainatate PF, anuala). Formular-LISTA de sectiuni pe (tara, categorie de
// venit), model d200: identitate (CNP/nume/initiala tata/prenume) + cate o sectiune per pereche. Valorile
// numerice vin de la contabil (aplicatia n-are registrul veniturilor externe); venit_N = venit_B - chlt_D
// calculat; DUK + d201.erori_generare arbitreaza. Reguli: categ=23 = doar venit net (venit_B/chlt_D=0);
// imp2 (impozit salarii) doar la categ=14; perechea (tara, categorie) unica. Sume in LEI intregi.
function _d201EsteSalarii(c) { return String(c) === "14"; }
function _d201NetOnly(c) { return String(c) === "23"; }

function _d201Manual() {
  const d = S.d201 || {};
  return {
    cif_c: (d.cif_c || "").replace(/\s+/g, ""),
    nume_c: (d.nume_c || "").trim(),
    initiala_c: (d.initiala_c || "").trim(),
    prenume_c: (d.prenume_c || "").trim(),
    d_rec: d.d_rec ? 1 : 0,
    sectiuni: (d.sectiuni || []).map((s) => ({
      categ_venit: s.categ_venit, statul: s.statul,
      venit_B: s.venit_B || 0, chlt_D: s.chlt_D || 0, venit_N: s.venit_N || 0,
      imp1: s.imp1 || 0, imp2: s.imp2 || 0,
    })),
  };
}

function randeazaFormularD201(corp, nav) {
  const zona = corp.querySelector("#dec-d201-form");
  if (!zona) return;
  const d = S.d201;
  const sec = d.sectiuni || [];
  let totalNet = 0, totalImp = 0;
  const grila = sec.length
    ? sec.map((s, i) => {
        const c = String(s.categ_venit);
        const vn = _d201NetOnly(c) ? Math.round(_n(s.venit_N) || 0)
          : Math.max(0, Math.round(_n(s.venit_B) || 0) - Math.round(_n(s.chlt_D) || 0));
        const im = Math.round(_n(s.imp1) || 0) + Math.round(_n(s.imp2) || 0);
        totalNet += vn; totalImp += im;
        return '<div class="dec-man-rand"><span class="dec-recl-desc">categ. ' + esc(c) + " · țara " + esc(String(s.statul)) +
          " · venit net " + bani(vn) + (im > 0 ? (" · impozit " + bani(im)) : "") + " lei</span>" +
          '<button class="btn-link dec-d201-del" data-idx="' + i + '">șterge</button></div>';
      }).join("")
    : '<div class="stare-goala stare-goala--inline">Nicio secțiune. D201 declară veniturile din străinătate pe perechi (țară, categorie de venit) — adaugă mai jos fiecare pereche.</div>';
  zona.innerHTML = '<details class="dec-xml" open><summary>Contribuabil + secțiuni de venit din străinătate (' + sec.length + ")</summary>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">CNP contribuabil <span class="oblig">*</span></span><input id="d201-cnp" type="text" maxlength="13" class="camp-input" value="' + esc(d.cif_c || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Nume <span class="oblig">*</span></span><input id="d201-nume" type="text" class="camp-input" value="' + esc(d.nume_c || "") + '"></label>' +
      '<label class="camp" style="width:110px"><span class="camp-eticheta">Inițiala tată <span class="oblig">*</span></span><input id="d201-init" type="text" maxlength="1" class="camp-input" value="' + esc(d.initiala_c || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Prenume <span class="oblig">*</span></span><input id="d201-pren" type="text" class="camp-input" value="' + esc(d.prenume_c || "") + '"></label>' +
      '<label class="set-bifa"><input id="d201-rec" type="checkbox" ' + (d.d_rec ? "checked" : "") + '> <span>Rectificativă</span></label>' +
    "</div>" + grila +
    '<div class="camp-eticheta" style="margin:12px 0 4px">Adaugă secțiune (o pereche țară + categorie):</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Categorie venit <span class="oblig">*</span></span><input id="d201-categ" type="number" step="1" min="1" class="camp-input"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Țară (cod numeric) <span class="oblig">*</span></span><input id="d201-tara" type="number" step="1" min="1" class="camp-input"></label>' +
      '<label class="camp d201-vb" style="width:140px"><span class="camp-eticheta">Venit brut (lei)</span><input id="d201-vb" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp d201-vb" style="width:140px"><span class="camp-eticheta">Cheltuieli (lei)</span><input id="d201-ch" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp d201-vn" style="width:140px"><span class="camp-eticheta">Venit net (lei)</span><input id="d201-vn" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Impozit străinătate (lei)</span><input id="d201-imp1" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp d201-imp2" style="width:140px"><span class="camp-eticheta">Impozit salarii (lei)</span><input id="d201-imp2" type="number" step="1" min="0" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d201-add">+ adaugă</button>' +
    "</div>" +
    '<p class="camp-ajutor" id="d201-nota" style="margin:4px 0 0">Coduri oficiale ANAF (D201). Țara = cod ISO-3166 numeric (ex. Germania 276, Franța 250, Italia 380, Austria 40, Spania 724). Categorie 23 = doar venit net; categorie 14 (salarii) = admite impozit pe salarii.</p>' +
    '<div id="d201-msg"></div>' +
    '<p class="camp-ajutor" id="d201-totaluri" style="margin-top:8px">' + sec.length + " secțiune(i) · venit net total: <b>" + totalNet + "</b> lei · impozit total: <b>" + totalImp + "</b> lei — creditul fiscal extern îl stabilește ANAF, nu se fabrică aici.</p>" +
    '<p style="margin-top:8px"><button class="buton-primar" id="d201-regen">Regenerează D201</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveazaAntet = () => {
    S.d201.cif_c = gv("#d201-cnp").value.trim();
    S.d201.nume_c = gv("#d201-nume").value.trim();
    S.d201.initiala_c = gv("#d201-init").value.trim();
    S.d201.prenume_c = gv("#d201-pren").value.trim();
    S.d201.d_rec = gv("#d201-rec").checked ? 1 : 0;
  };
  ["#d201-cnp", "#d201-nume", "#d201-init", "#d201-pren"].forEach((id) => gv(id).addEventListener("change", salveazaAntet));
  gv("#d201-rec").addEventListener("change", salveazaAntet);
  const reflCateg = () => {
    const c = gv("#d201-categ").value, net = _d201NetOnly(c), sal = _d201EsteSalarii(c);
    zona.querySelectorAll(".d201-vb").forEach((e) => { e.style.display = net ? "none" : ""; });
    zona.querySelectorAll(".d201-vn").forEach((e) => { e.style.display = net ? "" : "none"; });
    zona.querySelectorAll(".d201-imp2").forEach((e) => { e.style.display = sal ? "" : "none"; });
  };
  gv("#d201-categ").addEventListener("change", reflCateg);
  reflCateg();
  zona.querySelectorAll(".dec-d201-del").forEach((b) => b.addEventListener("click", () => {
    S.d201.sectiuni.splice(parseInt(b.dataset.idx), 1); randeazaFormularD201(corp, nav);
  }));
  gv("#d201-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    const c = gv("#d201-categ").value.trim(), tara = gv("#d201-tara").value.trim();
    const err = [];
    if (!c) err.push(["d201-categ", "Completează categoria de venit."]);
    if (!tara) err.push(["d201-tara", "Completează codul de țară (ISO-3166 numeric)."]);
    if (err.length) { err.forEach(([id, m]) => eroareCamp(zona, id, m)); return; }
    const net = _d201NetOnly(c), sal = _d201EsteSalarii(c);
    const s = { categ_venit: parseInt(c, 10), statul: parseInt(tara, 10),
      imp1: Math.round(_n(gv("#d201-imp1").value) || 0) };
    if (net) {
      s.venit_N = Math.round(_n(gv("#d201-vn").value) || 0); s.venit_B = 0; s.chlt_D = 0;
    } else {
      s.venit_B = Math.round(_n(gv("#d201-vb").value) || 0);
      s.chlt_D = Math.round(_n(gv("#d201-ch").value) || 0);
    }
    if (sal) s.imp2 = Math.round(_n(gv("#d201-imp2").value) || 0);
    salveazaAntet();
    S.d201.sectiuni.push(s);
    randeazaFormularD201(corp, nav);
  });
  gv("#d201-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveazaAntet();
    if (!(S.d201.sectiuni || []).length) {
      eroareCamp(zona, "d201-categ", "Adaugă cel puțin o secțiune de venit (butonul + adaugă). D201 nu se depune fără venituri.");
      return;
    }
    pas2(corp, nav);
  });
}

// tip==="d212" (Declaratia unica, persoane fizice, anuala). Increment "proof-of-pattern": formularul
// strange IDENTITATEA (CNP/nume/adresa) si AFISEAZA fisa RIP (venit net + CAS/CASS + impozit din
// registrul de incasari/plati, ruta /rip/d212/{an}, informativ). Genereaza cazul MINIM DUK-valid
// (identitate + bife 0; totalPlata_A = suma cifrelor CNP). Popularea cap11/oblig_realizat din fisa =
// pas urmator (cifrele NU intra inca in XML). Valorile din memorie (S.d212), persista intre randari.
function _d212Manual() {
  const d = S.d212 || {};
  return {
    cif: (d.cif || "").replace(/\s+/g, ""),
    nume_c: (d.nume_c || "").trim(),
    adresa_c: (d.adresa_c || "").trim(),
    d_rec: d.d_rec ? 1 : 0,
  };
}

function randeazaFormularD212(corp, nav) {
  const zona = corp.querySelector("#dec-d212-form");
  if (!zona) return;
  const d = S.d212;
  const f = d.fisa;
  let blocFisa;
  if (d.fisa_eroare) {
    blocFisa = '<div class="caseta-info"><div class="ci-mesaj">Fișa RIP nu s-a putut încărca: ' + esc(d.fisa_eroare) + "</div></div>";
  } else if (f) {
    const casNota = f.cas && !f.cas.obligatoriu ? " (neobligatoriu — sub 12 salarii minime)" : "";
    const cassNota = f.cass && !f.cass.obligatoriu ? " (neobligatoriu — sub 6 salarii minime)" : "";
    blocFisa = '<div class="caseta-info">' +
      '<div class="ci-mesaj" style="font-weight:600;margin-bottom:6px">Fișa RIP ' + esc(String(f.an || S.an)) + " (informativ — din registrul de încasări/plăți)</div>" +
      '<div class="ecran-nota">Venit brut: <b>' + bani(f.venit_brut || 0) + "</b> · Cheltuieli deductibile: <b>" + bani(f.cheltuieli_deductibile || 0) + "</b> · Venit net: <b>" + bani(f.venit_net || 0) + "</b> lei<br>" +
      "CAS: <b>" + bani((f.cas || {}).cas || 0) + "</b> lei" + casNota + " · CASS: <b>" + bani((f.cass || {}).cass || 0) + "</b> lei" + cassNota + "<br>" +
      "Bază impozit: <b>" + bani(f.baza_impozit || 0) + "</b> · Impozit: <b>" + bani(f.impozit || 0) + "</b> lei</div>" +
      (f.avertisment ? '<div class="ecran-nota" style="margin-top:4px">' + esc(f.avertisment) + "</div>" : "") +
      '<div class="ecran-nota" style="margin-top:6px">Cifrele vin din registrul firmei și sunt afișate ca reper. Popularea capitolelor de venit și contribuții în declarație e pasul următor; deocamdată se generează declarația de identificare.</div>' +
      "</div>";
  } else {
    blocFisa = '<div class="stare-goala stare-goala--inline">Apasă „Trage fișa RIP" ca să vezi venitul net și contribuțiile calculate din registrul de încasări/plăți al firmei, pentru anul ales.</div>';
  }
  zona.innerHTML = '<details class="dec-xml" open><summary>Declarația unică — persoană fizică (identificare + fișa RIP)</summary>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:180px"><span class="camp-eticheta">CNP contribuabil <span class="oblig">*</span></span><input id="d212-cnp" type="text" maxlength="13" class="camp-input" value="' + esc(d.cif || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 220px"><span class="camp-eticheta">Nume și prenume <span class="oblig">*</span></span><input id="d212-nume" type="text" class="camp-input" value="' + esc(d.nume_c || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 260px"><span class="camp-eticheta">Adresa <span class="oblig">*</span></span><input id="d212-adr" type="text" class="camp-input" value="' + esc(d.adresa_c || "") + '"></label>' +
      '<label class="set-bifa"><input id="d212-rec" type="checkbox" ' + (d.d_rec ? "checked" : "") + '> <span>Rectificativă</span></label>' +
    "</div>" +
    '<p style="margin:4px 0 8px"><button class="buton-secundar" id="d212-fisa">Trage fișa RIP ' + esc(String(S.an)) + "</button></p>" +
    blocFisa +
    '<p style="margin-top:10px"><button class="buton-primar" id="d212-regen">Regenerează D212</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveazaAntet = () => {
    S.d212.cif = gv("#d212-cnp").value.trim();
    S.d212.nume_c = gv("#d212-nume").value.trim();
    S.d212.adresa_c = gv("#d212-adr").value.trim();
    S.d212.d_rec = gv("#d212-rec").checked ? 1 : 0;
  };
  ["#d212-cnp", "#d212-nume", "#d212-adr"].forEach((id) => gv(id).addEventListener("change", salveazaAntet));
  gv("#d212-rec").addEventListener("change", salveazaAntet);
  gv("#d212-fisa").addEventListener("click", async () => {
    salveazaAntet();
    S.d212.fisa = null; S.d212.fisa_eroare = "";
    try {
      const r = await api.get(`/tenants/${S.tenant_id}/rip/d212/${S.an}`);
      if (r && r.eroare) S.d212.fisa_eroare = r.eroare;
      else S.d212.fisa = r;
    } catch (e) {
      S.d212.fisa_eroare = (e && e.mesaj) || "eroare la încărcarea fișei";
    }
    randeazaFormularD212(corp, nav);
  });
  gv("#d212-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveazaAntet();
    if (!S.d212.cif || !S.d212.nume_c || !S.d212.adresa_c) {
      eroareCamp(zona, "d212-cnp", "Completează CNP, nume și adresă — D212 nu se poate genera fără identificarea persoanei fizice.");
      return;
    }
    pas2(corp, nav);
  });
}

// tip==="d207" (informativa impozit retinut la sursa - beneficiari nerezidenti). Formular-LISTA de beneficiari
// (ca d107): fiecare cu tip de venit, nume/denumire, stat de rezidenta, cod fiscal (RO sau strainatate), act
// normativ, baza si impozit retinut/suportat. Backend agrega pe tip_venit (Sect_II) si calculeaza suma de
// control. Nomenclatorul tip venit + regula scutit (12-21) = din structura_D207_2025 (cap.III). Zero clase noi.
// Valorile stau IN MEMORIE (S.d207), persista intre randari (Regenereaza reface pas2).
const _D207_TIP = {
  impozabile: [
    ["01", "Dividende (art.223(1) lit.a)"],
    ["02", "Dobânzi (art.223(1) lit.b, c)"],
    ["03", "Redevențe (art.223(1) lit.d, e)"],
    ["04", "Comisioane (art.223(1) lit.f, g)"],
    ["05", "Activități sportive și de divertisment (art.223(1) lit.h)"],
    ["06", "Remunerații administratori/fondatori/consiliu (art.223(1) lit.j)"],
    ["07", "Servicii prestate de nerezidenți (art.223(1) lit.i, k, l)"],
    ["08", "Premii la concursuri în România (art.223(1) lit.m)"],
    ["10", "Lichidarea unui rezident (art.223(1) lit.o)"],
    ["11", "Transfer masă patrimonială fiduciară (art.223(1) lit.p)"],
    ["22", "Dividende, cf. convenției de evitare a dublei impuneri"],
    ["23", "Dobânzi, cf. convenției de evitare a dublei impuneri"],
    ["24", "Redevențe, cf. convenției de evitare a dublei impuneri"],
    ["25", "Comisioane, cf. convenției de evitare a dublei impuneri"],
    ["26", "Plăți pentru servicii tehnice (Acord România–India, L329/2013)"],
  ],
  scutite: [
    ["12", "Dobânzi (art.229(1) lit.a, b, g, h)"],
    ["13", "Tranzacții cu instrumente financiare / titluri de stat (art.229(1) lit.a)"],
    ["14", "Dividende (art.229(1) lit.c)"],
    ["15", "Premii (art.229(1) lit.d, e)"],
    ["16", "Redevențe (art.229(1) lit.g)"],
    ["17", "Activități de consultanță (art.229(1) lit.f)"],
    ["18", "Câștiguri din jocuri de noroc într-un alt stat (art.229(1) lit.i)"],
    ["19", "Dobânzi, cf. convenției de evitare a dublei impuneri"],
    ["20", "Dividende, cf. convenției de evitare a dublei impuneri"],
    ["21", "Redevențe, cf. convenției de evitare a dublei impuneri"],
  ],
};
const _D207_ACT = [["1", "Codul fiscal (Legea 227/2015)"], ["2", "Convenție de evitare a dublei impuneri"], ["3", "Acord internațional"]];
function _d207Scutit(tv) { const n = parseInt(tv, 10); return n >= 12 && n <= 21; }
function _d207TipEt(tv) {
  const all = _D207_TIP.impozabile.concat(_D207_TIP.scutite);
  const x = all.find((y) => y[0] === String(tv)); return x ? x[0] + " — " + x[1] : "tip " + tv;
}

function _d207Manual() {
  const d = S.d207 || {};
  return {
    beneficiari: (d.beneficiari || []).map((b) => ({
      tip_venit: b.tip_venit, den: b.den, stat: b.stat, cif_ro: b.cif_ro, cif_strain: b.cif_strain,
      act_n: b.act_n, baza: b.baza, imp: b.imp, imp_suportat: b.imp_suportat })),
    d_rec: d.d_rec ? 1 : 0,
  };
}

function randeazaFormularD207(corp, nav) {
  const zona = corp.querySelector("#dec-d207-form");
  if (!zona) return;
  const d = S.d207;
  const benef = d.beneficiari || [];
  // oglinda calcul_d207: grupare pe tip_venit -> Sect_II; totalPlata_A = sum(nrben+Tscutit+Tbaza+Timp+Timps)
  const sec = {};
  benef.forEach((b) => {
    const tv = String(b.tip_venit || "").padStart(2, "0");
    const x = sec[tv] || (sec[tv] = { nrben: 0, Tbaza: 0, Tscutit: 0, Timp: 0, Timps: 0 });
    x.nrben += 1;
    const baza = Math.round(_n(b.baza) || 0);
    if (_d207Scutit(tv)) { x.Tscutit += baza; }
    else { x.Tbaza += baza; x.Timp += Math.round(_n(b.imp) || 0); x.Timps += Math.round(_n(b.imp_suportat) || 0); }
  });
  const secv = Object.keys(sec).map((k) => sec[k]);
  const Tbaza = secv.reduce((a, x) => a + x.Tbaza, 0);
  const Tscutit = secv.reduce((a, x) => a + x.Tscutit, 0);
  const Timp = secv.reduce((a, x) => a + x.Timp, 0);
  const Timps = secv.reduce((a, x) => a + x.Timps, 0);
  const totalCtrl = secv.reduce((a, x) => a + x.nrben + x.Tscutit + x.Tbaza + x.Timp + x.Timps, 0);
  const grila = benef.length
    ? benef.map((b, i) => {
        const tv = String(b.tip_venit || "").padStart(2, "0");
        const cf = b.cif_ro ? ("RO " + b.cif_ro) : (b.cif_strain || "—");
        const sc = _d207Scutit(tv);
        return '<div class="dec-man-rand">' +
          '<span class="dec-recl-desc">' + esc(b.den) + ' · ' + esc(String(b.stat || "").toUpperCase()) +
          ' · cod fiscal ' + esc(String(cf)) + ' · ' + esc(_d207TipEt(tv)) +
          ' · ' + (sc ? "venit scutit " : "bază ") + bani(_n(b.baza)) + ' lei' +
          (sc ? "" : ' · impozit ' + bani(_n(b.imp)) + ' lei') + '</span>' +
          '<button class="btn-link dec-d207-del" data-idx="' + i + '">șterge</button></div>';
      }).join("")
    : '<div class="stare-goala stare-goala--inline">Niciun beneficiar. D207 declară veniturile plătite beneficiarilor nerezidenți și impozitul reținut la sursă — adaugă mai jos fiecare beneficiar.</div>';
  const optTip = '<optgroup label="Venituri impozabile">' +
    _D207_TIP.impozabile.map((t) => '<option value="' + t[0] + '">' + esc(t[0] + " — " + t[1]) + '</option>').join("") +
    '</optgroup><optgroup label="Venituri scutite">' +
    _D207_TIP.scutite.map((t) => '<option value="' + t[0] + '">' + esc(t[0] + " — " + t[1]) + '</option>').join("") +
    '</optgroup>';
  const optAct = _D207_ACT.map((a) => '<option value="' + a[0] + '">' + esc(a[1]) + '</option>').join("");
  zona.innerHTML = '<details class="dec-xml" open><summary>Beneficiari nerezidenți (' + benef.length + ')</summary>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:6px">' +
      '<label class="camp" style="width:auto;flex-direction:row;align-items:center;gap:6px">' +
        '<input id="d207-rec" type="checkbox" ' + (d.d_rec ? "checked" : "") + '><span class="camp-eticheta" style="margin:0">Declarație rectificativă</span></label>' +
    '</div>' +
    grila +
    '<div class="camp-eticheta" style="margin:12px 0 4px">Adaugă beneficiar nerezident:</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">' +
      '<label class="camp" style="flex:1 1 280px"><span class="camp-eticheta">Tip venit plătit <span class="oblig">*</span></span>' +
        '<select id="d207-tip" class="camp-input">' + optTip + '</select></label>' +
      '<label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Nume / denumire beneficiar <span class="oblig">*</span></span><input id="d207-den" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Stat rezidență (2 litere) <span class="oblig">*</span></span><input id="d207-stat" type="text" maxlength="2" class="camp-input" style="text-transform:uppercase"></label>' +
      '<label class="camp" style="width:160px"><span class="camp-eticheta">Cod fiscal România</span><input id="d207-cifro" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:160px"><span class="camp-eticheta">Cod fiscal străinătate</span><input id="d207-cifs" type="text" class="camp-input"></label>' +
      '<label class="camp" style="flex:1 1 240px"><span class="camp-eticheta">Act normativ aplicabil <span class="oblig">*</span></span>' +
        '<select id="d207-act" class="camp-input">' + optAct + '</select></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Bază / venit brut (lei)</span><input id="d207-baza" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Impozit reținut (lei)</span><input id="d207-imp" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:190px"><span class="camp-eticheta">Impozit suportat de plătitor (lei)</span><input id="d207-imps" type="number" step="1" min="0" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d207-add">+ adaugă</button>' +
    '</div>' +
    '<p class="camp-ajutor" id="d207-scutit-nota" style="margin:4px 0 0"></p>' +
    '<div id="d207-msg"></div>' +
    '<p class="camp-ajutor" id="d207-totaluri" style="margin-top:8px">' + benef.length + ' beneficiar(i) · bază impozabilă <b>' + bani(Tbaza) + '</b> · venit scutit <b>' + bani(Tscutit) + '</b> · impozit reținut <b>' + bani(Timp) + '</b> · impozit suportat de plătitor <b>' + bani(Timps) + '</b> lei. Suma de control a declarației: <b>' + totalCtrl + '</b> — se calculează automat din datele de mai sus.</p>' +
    '<p style="margin-top:8px"><button class="buton-primar" id="d207-regen">Regenerează D207</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  '</details>';
  const gv = (id) => zona.querySelector(id);
  gv("#d207-rec").addEventListener("change", (e) => { S.d207.d_rec = e.target.checked ? 1 : 0; });
  // tip de venit scutit (12-21) -> impozitul retinut/suportat sunt 0 (regula validatorului): dezactiveaza + noteaza
  const reflScutit = () => {
    const sc = _d207Scutit(gv("#d207-tip").value);
    gv("#d207-imp").disabled = sc; gv("#d207-imps").disabled = sc;
    if (sc) { gv("#d207-imp").value = ""; gv("#d207-imps").value = ""; }
    gv("#d207-scutit-nota").textContent = sc
      ? "Tip de venit scutit — impozitul reținut și cel suportat de plătitor sunt 0 pentru acest beneficiar."
      : "";
  };
  gv("#d207-tip").addEventListener("change", reflScutit);
  reflScutit();
  zona.querySelectorAll(".dec-d207-del").forEach((b) => b.addEventListener("click", () => {
    S.d207.beneficiari.splice(parseInt(b.dataset.idx), 1); randeazaFormularD207(corp, nav);
  }));
  gv("#d207-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    const tip = gv("#d207-tip").value;
    const den = gv("#d207-den").value.trim();
    const stat = gv("#d207-stat").value.trim().toUpperCase();
    const cifro = gv("#d207-cifro").value.trim();
    const cifs = gv("#d207-cifs").value.trim();
    const act = gv("#d207-act").value;
    const err = [];
    if (!den) err.push(["d207-den", "Completează numele sau denumirea beneficiarului nerezident."]);
    if (!stat) err.push(["d207-stat", "Completează statul de rezidență (codul de țară din 2 litere)."]);
    if (!cifro && !cifs) err.push(["d207-cifro", "Completează codul de identificare fiscală — cel din România sau cel din străinătate (măcar unul)."]);
    if (err.length) { err.forEach(([id, m]) => eroareCamp(zona, id, m)); return; }
    const sc = _d207Scutit(tip);
    S.d207.beneficiari.push({ tip_venit: tip, den: den, stat: stat, cif_ro: cifro, cif_strain: cifs,
      act_n: act, baza: gv("#d207-baza").value,
      imp: sc ? "" : gv("#d207-imp").value, imp_suportat: sc ? "" : gv("#d207-imps").value });
    randeazaFormularD207(corp, nav);
  });
  gv("#d207-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    // marcheaza campul vinovat INAINTE de a chema serverul (Regula 14.4)
    if (!(S.d207.beneficiari || []).length) {
      eroareCamp(zona, "d207-den", "Adaugă cel puțin un beneficiar nerezident (butonul + adaugă). D207 nu se depune fără beneficiari.");
      return;
    }
    pas2(corp, nav);
  });
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
// [lista 5, 30.08.2026] DIN CE e facuta declaratia, nu doar CATE randuri are.
//
// Pana azi ecranul arata contorul - „valid, 18 operatiuni" - si nu exista nicio cale prin care
// contabilul sa vada CARE 18: pasul 1c a masurat 0 din 92 de iesiri care isi arata componentele.
// Randurile vin GATA COMPUSE din `core/declaratii_componente.py`, impreuna cu numele coloanelor si
// cu lista coloanelor MONETARE - ecranul nu stie nimic despre nicio declaratie anume, si nici nu
// ghiceste care numar e o suma.
//
// Ce NU se poate desface o spune, nu o tace: `acoperire !== "completa"` vine cu motivul scris.
function _blocComponente(c) {
  if (!c) return "";
  // Propozitia o detine ECRANUL, nu raspunsul: un text trimis de server ar fi o afirmatie in proza
  // intr-un payload (interzis din 21.08), iar aici e text de interfata - explicit in afara regulii
  // (DS cap.25.5). Serverul trimite doar cuvantul din nomenclatorul inchis `ACOPERIRE`.
  if (c.acoperire !== "completa") {
    const spune = c.acoperire === "absenta"
      ? "Declara\u021bia asta nu-\u0219i poate desface \u00eenc\u0103 cifra: motorul care o produce nu \u00eentoarce pozi\u021biile, doar XML-ul. Compozi\u021bia se vede \u00een fi\u0219ierul generat."
      : "Nu \u0219tiu s\u0103 desfac cifra acestui tip de declara\u021bie \u2014 nu e trecut \u00een harta de componente. Ce vezi mai sus e num\u0103rul de opera\u021biuni, nu compozi\u021bia lor.";
    return `<div class="caseta-info"><span class="ci-mesaj">${spune}</span></div>`;
  }
  if (!c.total) return "";
  const tabel = (s) => {
    const coloane = Object.keys(s.randuri[0] || {});
    const mon = new Set(s.monetare || []);
    const celula = (r, k) => (r[k] == null ? "" : (mon.has(k) ? bani(r[k]) : esc(String(r[k]))));
    return `<div style="margin-top:10px">
        <div class="camp-eticheta">${esc(s.nume)} \u2014 ${s.total} ${s.total === 1 ? "r\u00e2nd" : "r\u00e2nduri"}${s.aratate < s.total ? `, se arat\u0103 primele ${s.aratate}` : ""}</div>
        <table class="fd-tabel">
          <thead><tr>${coloane.map((k) => `<th${mon.has(k) ? ' class="fd-td-num"' : ""}>${esc(k)}</th>`).join("")}</tr></thead>
          <tbody>${s.randuri.map((r) => `<tr>${coloane.map((k) => `<td${mon.has(k) ? ' class="fd-td-num"' : ""}>${celula(r, k)}</td>`).join("")}</tr>`).join("")}</tbody>
        </table>
      </div>`;
  };
  const cuRanduri = c.sectiuni.filter((s) => s.randuri.length);
  if (!cuRanduri.length) return "";
  return `<details class="dec-xml">
      <summary>Din ce e f\u0103cut\u0103 declara\u021bia \u2014 ${c.total} ${c.total === 1 ? "r\u00e2nd" : "r\u00e2nduri"}</summary>
      ${cuRanduri.map(tabel).join("")}
    </details>`;
}

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
