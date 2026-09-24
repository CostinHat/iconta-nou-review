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
  d301:"F032", d390:"F033", d394:"F034", d406:"F035", d710:"F192", d311:"F207", d307:"F217", d107:"F211", d177:"F210", d207:"F209", d200:"F221", d212:"F030", d201:"F222", d230:"F208", d204:"F223", d223:"F214", d216:"F225", d208:"F224", d221:"F215", d603:"F233", d600:"F227" };

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
    // [formular_manual_d230] redirectionare 3,5% catre ONG (PF): identitate + entitate beneficiara. In memorie, ca d200.
    d230: { cif_c: "", nume_c: "", initiala_c: "", prenume_c: "", adresa_c: "", telefon_c: "", email_c: "", den_entitate: "", cif_entitate: "", cont_entitate: "", suma_entitate: "", procent: "", valabilitate_distribuire: 1 },
    // [formular_manual_d204] asociere fara personalitate juridica: asociere + reprezentant + o activitate + asociati. In memorie, ca d200.
    d204: { d_rec: 0, asociere: { den: "", cif: "", adresa: "" }, reprezentant: { nume: "", cif: "", adresa: "", telefon: "", email: "" }, activitate: { categ_venit: 1, caen: "", judet: "", sector: "", sediu: "", nr_contr: "", data_contr: "", venit3: "", chelt3: "" }, asociati: [] },
    // [formular_manual_d223] venituri estimate asociere f.PJ: declarant + asociere + responsabil + activitate + asociati. In memorie, ca d200.
    d223: { declarant_nume: "", declarant_prenume: "", declarant_functie: "", d_rec1: 0, d_rec: 0, asociere: { nume: "", cif: "", adresa: "", telefon: "", email: "" }, responsabil: { den_r: "", cif_r: "", adresa_r: "" }, activitate: { categ_venit: "1", forma_org: "2", det_venit: "1", caen: "", judet: "", localitate: "", sector: "", sediu: "", nr_contr: "", data_contr: "", venit_brut: "", cheltuieli: "" }, asociati: [] },
    // [formular_manual_d216] impozit special bunuri de valoare mare: antet + liste imobile/mobile. In memorie, ca d200.
    d216: { nume: "", cif: "", domiciliuFiscal: "", nume_intocmit: "", functia_intocmit: "", d_rec: 0, nume_imputernicit: "", cif_imputernicit: "", imobile: [], mobile: [] },
    // [formular_manual_d208] transfer proprietati imobiliare (notari): antet + tranzactie/imobil + beneficiari + parti. In memorie, ca d200.
    d208: { nume: "", cif: "", domiciliu: "", nume_intocmit: "", functia_intocmit: "", dRec: 0, nr_act_notarial: "", mod_transfer: "1", taxa_notar: "", imobil: { judet: "", localitate: "", codSIRUTA: "", nr_cadastral: "", tip_imobil: "teren", val_tranzactie_imobil: "", val_piata_imobil: "" }, beneficiari: [], parti: [] },
    // [formular_manual_d221] venituri agricole pe norme: declarant + contribuabil + activitate + produse (+ asociati la forma_org=2). In memorie, ca d200.
    d221: { nume_declar: "", prenume_declar: "", functie_declar: "TITULAR", cif: "", nume_a: "", adresa_a: "", forma_org: "1", d_rec: 0, nr_contr: "", data_contr: "", activitate: { judet: "", localitate: "", optiune: "0" }, produse: [], asociati: [] },
    // [formular_manual_d603] exceptare CASS (PF): identitate + categorie + stat asigurare + perioada. In memorie, ca d200.
    d603: { numeContrib: "", cif: "", taraContrib: "RO", judetContrib: "", exceptare: "2", statAsigurare: "", dataInceput: "", dataSfarsit: "", dataExceptare: "", documente: "" },
    // [formular_manual_d600] baza CAS/CASS estimata (PF): identitate + optiune CAS + baza lunara (12 luni). In memorie, ca d200.
    d600: { nume_c: "", initiala_c: "", prenume_c: "", cif_c: "", adresa_c: "", cont_c: "", d_rec: 0, cas_opt: false, baza_lunara: "" },
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
  if (S.tip === "d230") body.manual = _d230Manual();              // [formular_manual_d230] identitate PF + entitate ONG
  if (S.tip === "d204") body.manual = _d204Manual();              // [formular_manual_d204] asociere + reprezentant + activitate + asociati
  if (S.tip === "d223") body.manual = _d223Manual();              // [formular_manual_d223] asociere estimat + responsabil + activitate + asociati
  if (S.tip === "d216") body.manual = _d216Manual();              // [formular_manual_d216] antet + liste bunuri imobile/mobile
  if (S.tip === "d208") body.manual = _d208Manual();              // [formular_manual_d208] notar + tranzactie/imobil + beneficiari + parti
  if (S.tip === "d221") body.manual = _d221Manual();              // [formular_manual_d221] contribuabil + activitate agricola + produse
  if (S.tip === "d603") body.manual = _d603Manual();              // [formular_manual_d603] exceptare CASS (identitate + categorie + stat + perioada)
  if (S.tip === "d600") body.manual = _d600Manual();              // [formular_manual_d600] identitate PF + optiune CAS + baza lunara

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
    ${S.tip === "d230" ? '<div id="dec-d230-form"></div>' : ""}
    ${S.tip === "d204" ? '<div id="dec-d204-form"></div>' : ""}
    ${S.tip === "d223" ? '<div id="dec-d223-form"></div>' : ""}
    ${S.tip === "d216" ? '<div id="dec-d216-form"></div>' : ""}
    ${S.tip === "d208" ? '<div id="dec-d208-form"></div>' : ""}
    ${S.tip === "d221" ? '<div id="dec-d221-form"></div>' : ""}
    ${S.tip === "d603" ? '<div id="dec-d603-form"></div>' : ""}
    ${S.tip === "d600" ? '<div id="dec-d600-form"></div>' : ""}
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
  if (S.tip === "d230") randeazaFormularD230(corp, nav);
  if (S.tip === "d204") randeazaFormularD204(corp, nav);
  if (S.tip === "d223") randeazaFormularD223(corp, nav);
  if (S.tip === "d216") randeazaFormularD216(corp, nav);
  if (S.tip === "d208") randeazaFormularD208(corp, nav);
  if (S.tip === "d221") randeazaFormularD221(corp, nav);
  if (S.tip === "d603") randeazaFormularD603(corp, nav);
  if (S.tip === "d600") randeazaFormularD600(corp, nav);
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
    ${S.tip === "d230" ? '<div id="dec-d230-form"></div>' : ""}
    ${S.tip === "d204" ? '<div id="dec-d204-form"></div>' : ""}
    ${S.tip === "d223" ? '<div id="dec-d223-form"></div>' : ""}
    ${S.tip === "d216" ? '<div id="dec-d216-form"></div>' : ""}
    ${S.tip === "d208" ? '<div id="dec-d208-form"></div>' : ""}
    ${S.tip === "d221" ? '<div id="dec-d221-form"></div>' : ""}
    ${S.tip === "d603" ? '<div id="dec-d603-form"></div>' : ""}
    ${S.tip === "d600" ? '<div id="dec-d600-form"></div>' : ""}
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
  if (S.tip === "d230") randeazaFormularD230(corp, nav);
  if (S.tip === "d204") randeazaFormularD204(corp, nav);
  if (S.tip === "d223") randeazaFormularD223(corp, nav);
  if (S.tip === "d216") randeazaFormularD216(corp, nav);
  if (S.tip === "d208") randeazaFormularD208(corp, nav);
  if (S.tip === "d221") randeazaFormularD221(corp, nav);
  if (S.tip === "d603") randeazaFormularD603(corp, nav);
  if (S.tip === "d600") randeazaFormularD600(corp, nav);
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

function _d230Manual() {
  const d = S.d230 || {};
  return {
    nume_c: (d.nume_c || "").trim(),
    initiala_c: (d.initiala_c || "").trim(),
    prenume_c: (d.prenume_c || "").trim(),
    cif_c: (d.cif_c || "").replace(/\s+/g, ""),
    adresa_c: (d.adresa_c || "").trim(),
    telefon_c: (d.telefon_c || "").trim(),
    email_c: (d.email_c || "").trim(),
    den_entitate: (d.den_entitate || "").trim(),
    cif_entitate: (d.cif_entitate || "").replace(/\s+/g, ""),
    cont_entitate: (d.cont_entitate || "").replace(/\s+/g, "").toUpperCase(),
    suma_entitate: (String(d.suma_entitate || "")).replace(/\s+/g, ""),
    procent: String(d.procent || "").trim(),
    valabilitate_distribuire: parseInt(d.valabilitate_distribuire, 10) === 2 ? 2 : 1,
  };
}

function randeazaFormularD230(corp, nav) {
  const zona = corp.querySelector("#dec-d230-form");
  if (!zona) return;
  const d = S.d230;
  const valab2 = parseInt(d.valabilitate_distribuire, 10) === 2;
  zona.innerHTML = '<details class="dec-xml" open><summary>Contribuabil + entitate beneficiară (redirecționare 3,5%)</summary>' +
    '<div class="camp-eticheta" style="margin:2px 0 4px">Persoana fizică (contribuabilul care redirecționează)</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">CNP <span class="oblig">*</span></span><input id="d230-cnp" type="text" maxlength="13" class="camp-input" value="' + esc(d.cif_c || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Nume <span class="oblig">*</span></span><input id="d230-nume" type="text" class="camp-input" value="' + esc(d.nume_c || "") + '"></label>' +
      '<label class="camp" style="width:110px"><span class="camp-eticheta">Inițiala tată</span><input id="d230-init" type="text" maxlength="1" class="camp-input" value="' + esc(d.initiala_c || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Prenume <span class="oblig">*</span></span><input id="d230-pren" type="text" class="camp-input" value="' + esc(d.prenume_c || "") + '"></label>' +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 260px"><span class="camp-eticheta">Adresă</span><input id="d230-adr" type="text" class="camp-input" value="' + esc(d.adresa_c || "") + '"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Telefon</span><input id="d230-tel" type="text" maxlength="15" class="camp-input" value="' + esc(d.telefon_c || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Email</span><input id="d230-email" type="text" class="camp-input" value="' + esc(d.email_c || "") + '"></label>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Entitatea nonprofit / unitatea de cult beneficiară</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 220px"><span class="camp-eticheta">Denumire entitate <span class="oblig">*</span></span><input id="d230-den" type="text" class="camp-input" value="' + esc(d.den_entitate || "") + '"></label>' +
      '<label class="camp" style="width:160px"><span class="camp-eticheta">CIF entitate <span class="oblig">*</span></span><input id="d230-cif" type="text" class="camp-input" value="' + esc(d.cif_entitate || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 240px"><span class="camp-eticheta">IBAN entitate <span class="oblig">*</span></span><input id="d230-iban" type="text" class="camp-input" value="' + esc(d.cont_entitate || "") + '"></label>' +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Sumă (lei, opțional)</span><input id="d230-suma" type="number" step="1" min="0" class="camp-input" value="' + esc(String(d.suma_entitate || "")) + '"></label>' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Procent (max 3,5)</span><input id="d230-proc" type="number" step="0.1" min="0" max="3.5" class="camp-input" value="' + esc(String(d.procent || "")) + '"></label>' +
      '<label class="camp" style="width:180px"><span class="camp-eticheta">Valabilitate <span class="oblig">*</span></span><select id="d230-valab" class="camp-input"><option value="1"' + (valab2 ? "" : " selected") + '>Un an</option><option value="2"' + (valab2 ? " selected" : "") + '>Doi ani</option></select></label>' +
    "</div>" +
    '<p class="camp-ajutor" style="margin:6px 0 0">Sumă goală = ANAF determină cuantumul (până la 3,5% din impozit). Termen: 25 mai a anului următor.</p>' +
    '<div id="d230-msg"></div>' +
    '<p style="margin-top:8px"><button class="buton-primar" id="d230-regen">Regenerează D230</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveaza = () => {
    S.d230.cif_c = gv("#d230-cnp").value.trim();
    S.d230.nume_c = gv("#d230-nume").value.trim();
    S.d230.initiala_c = gv("#d230-init").value.trim();
    S.d230.prenume_c = gv("#d230-pren").value.trim();
    S.d230.adresa_c = gv("#d230-adr").value.trim();
    S.d230.telefon_c = gv("#d230-tel").value.trim();
    S.d230.email_c = gv("#d230-email").value.trim();
    S.d230.den_entitate = gv("#d230-den").value.trim();
    S.d230.cif_entitate = gv("#d230-cif").value.trim();
    S.d230.cont_entitate = gv("#d230-iban").value.replace(/\s+/g, "").toUpperCase();
    S.d230.suma_entitate = gv("#d230-suma").value.trim();
    S.d230.procent = gv("#d230-proc").value.trim();
    S.d230.valabilitate_distribuire = parseInt(gv("#d230-valab").value, 10) === 2 ? 2 : 1;
  };
  ["#d230-cnp", "#d230-nume", "#d230-init", "#d230-pren", "#d230-adr", "#d230-tel", "#d230-email", "#d230-den", "#d230-cif", "#d230-iban", "#d230-suma", "#d230-proc", "#d230-valab"].forEach((id) => gv(id).addEventListener("change", salveaza));
  gv("#d230-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveaza();
    const err = [];
    if (!S.d230.cif_c) err.push(["d230-cnp", "Completează CNP-ul contribuabilului."]);
    if (!S.d230.nume_c) err.push(["d230-nume", "Completează numele."]);
    if (!S.d230.prenume_c) err.push(["d230-pren", "Completează prenumele."]);
    if (!S.d230.den_entitate) err.push(["d230-den", "Completează denumirea entității beneficiare."]);
    if (!S.d230.cif_entitate) err.push(["d230-cif", "Completează CIF-ul entității."]);
    if (!S.d230.cont_entitate) err.push(["d230-iban", "Completează IBAN-ul entității beneficiare."]);
    if (err.length) { err.forEach(([id, m]) => eroareCamp(zona, id, m)); return; }
    pas2(corp, nav);
  });
}

const _D204_JUDETE = [["1","Alba"],["2","Arad"],["3","Argeș"],["4","Bacău"],["5","Bihor"],["6","Bistrița-Năsăud"],["7","Botoșani"],["8","Brașov"],["9","Brăila"],["10","Buzău"],["11","Caraș-Severin"],["12","Cluj"],["13","Constanța"],["14","Covasna"],["15","Dâmbovița"],["16","Dolj"],["17","Galați"],["18","Gorj"],["19","Harghita"],["20","Hunedoara"],["21","Ialomița"],["22","Iași"],["23","Ilfov"],["24","Maramureș"],["25","Mehedinți"],["26","Mureș"],["27","Neamț"],["28","Olt"],["29","Prahova"],["30","Satu Mare"],["31","Sălaj"],["32","Sibiu"],["33","Suceava"],["34","Teleorman"],["35","Timiș"],["36","Tulcea"],["37","Vaslui"],["38","Vâlcea"],["39","Vrancea"],["40","București"],["51","Călărași"],["52","Giurgiu"]];

function _d204DataISO(v) {
  const s = String(v || "").trim();
  const m = s.match(/^(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})$/);
  if (m) return m[3] + "-" + ("0" + m[2]).slice(-2) + "-" + ("0" + m[1]).slice(-2);
  return s;
}

function _d204Manual() {
  const d = S.d204 || {};
  const a = d.asociere || {}, r = d.reprezentant || {}, ac = d.activitate || {};
  const cv = parseInt(ac.categ_venit, 10) || 1;
  return {
    d_rec: d.d_rec ? 1 : 0,
    asociere: { den: (a.den || "").trim(), cif: (a.cif || "").replace(/\s+/g, ""), adresa: (a.adresa || "").trim() },
    reprezentant: { nume: (r.nume || "").trim(), cif: (r.cif || "").replace(/\s+/g, ""), adresa: (r.adresa || "").trim(),
      telefon: (r.telefon || "").trim(), email: (r.email || "").trim() },
    activitate: { categ_venit: cv, det_ven_net: 1, caen: (ac.caen || "").replace(/\s+/g, ""),
      forma_org: cv === 3 ? 1 : (parseInt(ac.forma_org, 10) || 1),
      judet: (ac.judet || "").trim(), sector: (ac.sector || "").trim(), sediu: (ac.sediu || "").trim(),
      nr_contr: (ac.nr_contr || "").trim(), data_contr: (ac.data_contr || "").trim(),
      venit3: Math.round(_n(ac.venit3) || 0), chelt3: Math.round(_n(ac.chelt3) || 0) },
    asociati: (d.asociati || []).map((s) => ({ cif: (s.cif || "").replace(/\s+/g, ""), nume: (s.nume || "").trim(),
      cota: _n(s.cota) || 0, venit: Math.round(_n(s.venit) || 0), pierd: Math.round(_n(s.pierd) || 0) })),
  };
}

function randeazaFormularD204(corp, nav) {
  const zona = corp.querySelector("#dec-d204-form");
  if (!zona) return;
  const d = S.d204;
  const a = d.asociere || {}, r = d.reprezentant || {}, ac = d.activitate || {};
  const aso = d.asociati || [];
  const venit3 = Math.round(_n(ac.venit3) || 0), chelt3 = Math.round(_n(ac.chelt3) || 0);
  const net3 = Math.max(0, venit3 - chelt3), pierd3 = Math.max(0, chelt3 - venit3);
  let sCota = 0, sVen = 0, sPier = 0;
  aso.forEach((s) => { sCota += _n(s.cota) || 0; sVen += Math.round(_n(s.venit) || 0); sPier += Math.round(_n(s.pierd) || 0); });
  const bucuresti = String(ac.judet) === "40";
  const optJud = _D204_JUDETE.map((p) => '<option value="' + p[0] + '"' + (String(ac.judet) === p[0] ? " selected" : "") + ">" + esc(p[1]) + "</option>").join("");
  const grila = aso.length
    ? aso.map((s, i) => '<div class="dec-man-rand"><span class="dec-recl-desc">' + esc(s.nume || "(fără nume)") + " · CNP/CUI " + esc(s.cif || "?") +
        " · cotă " + esc(String(s.cota || 0)) + "% · venit " + bani(Math.round(_n(s.venit) || 0)) + (Math.round(_n(s.pierd) || 0) > 0 ? (" · pierdere " + bani(Math.round(_n(s.pierd) || 0))) : "") + " lei</span>" +
        '<button class="btn-link dec-d204-del" data-idx="' + i + '">șterge</button></div>').join("")
    : '<div class="stare-goala stare-goala--inline">Niciun asociat. Cotele trebuie să însumeze 100, iar venitul repartizat să egaleze venitul net.</div>';
  const okCota = Math.abs(sCota - 100) < 0.005, okVen = sVen === net3, okPier = sPier === pierd3;
  zona.innerHTML = '<details class="dec-xml" open><summary>Asociere fără personalitate juridică — venit anual (' + aso.length + " asociați)</summary>" +
    '<div class="camp-eticheta" style="margin:2px 0 4px">Asocierea (entitatea declarată)</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 220px"><span class="camp-eticheta">Denumire asociere <span class="oblig">*</span></span><input id="d204-aden" type="text" class="camp-input" value="' + esc(a.den || "") + '"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">CUI asociere <span class="oblig">*</span></span><input id="d204-acif" type="text" maxlength="10" class="camp-input" value="' + esc(a.cif || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 240px"><span class="camp-eticheta">Adresă asociere <span class="oblig">*</span></span><input id="d204-aadr" type="text" class="camp-input" value="' + esc(a.adresa || "") + '"></label>' +
      '<label class="set-bifa"><input id="d204-rec" type="checkbox" ' + (d.d_rec ? "checked" : "") + '> <span>Rectificativă</span></label>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Reprezentantul (asociatul desemnat care depune)</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Nume reprezentant <span class="oblig">*</span></span><input id="d204-rnume" type="text" class="camp-input" value="' + esc(r.nume || "") + '"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">CNP/CUI reprezentant <span class="oblig">*</span></span><input id="d204-rcif" type="text" maxlength="13" class="camp-input" value="' + esc(r.cif || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 220px"><span class="camp-eticheta">Adresă reprezentant <span class="oblig">*</span></span><input id="d204-radr" type="text" class="camp-input" value="' + esc(r.adresa || "") + '"></label>' +
      '<label class="camp" style="width:140px"><span class="camp-eticheta">Telefon</span><input id="d204-rtel" type="text" maxlength="15" class="camp-input" value="' + esc(r.telefon || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 180px"><span class="camp-eticheta">Email</span><input id="d204-remail" type="text" class="camp-input" value="' + esc(r.email || "") + '"></label>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Activitatea (sistem real — venit net; norma de venit nu e acoperită)</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Categorie venit <span class="oblig">*</span></span><input id="d204-categ" type="number" step="1" min="1" max="6" class="camp-input" value="' + esc(String(ac.categ_venit || 1)) + '"></label>' +
      '<label class="camp" style="width:120px"><span class="camp-eticheta">Cod CAEN <span class="oblig">*</span></span><input id="d204-caen" type="text" maxlength="4" class="camp-input" value="' + esc(ac.caen || "") + '"></label>' +
      '<label class="camp" style="width:190px"><span class="camp-eticheta">Județ <span class="oblig">*</span></span><select id="d204-judet" class="camp-input"><option value="">— alege —</option>' + optJud + "</select></label>" +
      (bucuresti ? '<label class="camp" style="width:110px"><span class="camp-eticheta">Sector <span class="oblig">*</span></span><input id="d204-sector" type="text" maxlength="1" class="camp-input" value="' + esc(ac.sector || "") + '"></label>' : "") +
      '<label class="camp" style="flex:1 1 220px"><span class="camp-eticheta">Sediu <span class="oblig">*</span></span><input id="d204-sediu" type="text" class="camp-input" value="' + esc(ac.sediu || "") + '"></label>' +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Nr. contract <span class="oblig">*</span></span><input id="d204-nrc" type="text" maxlength="20" class="camp-input" value="' + esc(ac.nr_contr || "") + '"></label>' +
      '<label class="camp" style="width:180px"><span class="camp-eticheta">Dată contract <span class="oblig">*</span></span><input id="d204-datac" type="date" class="camp-input" value="' + esc(_d204DataISO(ac.data_contr)) + '"></label>' +
      '<label class="camp" style="width:160px"><span class="camp-eticheta">Venit brut (lei)</span><input id="d204-venit3" type="number" step="1" min="0" class="camp-input" value="' + esc(String(venit3 || "")) + '"></label>' +
      '<label class="camp" style="width:160px"><span class="camp-eticheta">Cheltuieli (lei)</span><input id="d204-chelt3" type="number" step="1" min="0" class="camp-input" value="' + esc(String(chelt3 || "")) + '"></label>' +
    "</div>" +
    '<p class="camp-ajutor" style="margin:2px 0 6px">Venit net calculat: <b>' + net3 + "</b> lei" + (pierd3 > 0 ? (" · pierdere: <b>" + pierd3 + "</b> lei") : "") + ". Repartizează venitul net pe asociați (Σ venit_d = venit net).</p>" +
    grila +
    '<div class="camp-eticheta" style="margin:12px 0 4px">Adaugă asociat:</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">CNP/CUI <span class="oblig">*</span></span><input id="d204-acnp" type="text" maxlength="13" class="camp-input"></label>' +
      '<label class="camp" style="flex:1 1 160px"><span class="camp-eticheta">Nume <span class="oblig">*</span></span><input id="d204-anume" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:110px"><span class="camp-eticheta">Cotă % <span class="oblig">*</span></span><input id="d204-acota" type="number" step="0.01" min="0" max="100" class="camp-input"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Venit repartizat</span><input id="d204-avenit" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Pierdere repartizată</span><input id="d204-apierd" type="number" step="1" min="0" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d204-add">+ adaugă</button>' +
    "</div>" +
    '<div id="d204-msg"></div>' +
    '<p class="camp-ajutor" style="margin-top:8px">Σ cote: <b>' + (Math.round(sCota * 100) / 100) + "</b>% " + (okCota ? "✓" : "(trebuie 100)") +
      " · Σ venit repartizat: <b>" + sVen + "</b> / " + net3 + " lei " + (okVen ? "✓" : "(trebuie egal cu venitul net)") +
      (pierd3 > 0 ? (" · Σ pierdere: <b>" + sPier + "</b> / " + pierd3 + " " + (okPier ? "✓" : "(trebuie egal)")) : "") + "</p>" +
    '<p style="margin-top:8px"><button class="buton-primar" id="d204-regen">Regenerează D204</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveaza = () => {
    S.d204.d_rec = gv("#d204-rec").checked ? 1 : 0;
    S.d204.asociere = { den: gv("#d204-aden").value.trim(), cif: gv("#d204-acif").value.trim(), adresa: gv("#d204-aadr").value.trim() };
    S.d204.reprezentant = { nume: gv("#d204-rnume").value.trim(), cif: gv("#d204-rcif").value.trim(), adresa: gv("#d204-radr").value.trim(),
      telefon: gv("#d204-rtel").value.trim(), email: gv("#d204-remail").value.trim() };
    const sect = gv("#d204-sector");
    S.d204.activitate = { categ_venit: parseInt(gv("#d204-categ").value, 10) || 1, caen: gv("#d204-caen").value.trim(),
      judet: gv("#d204-judet").value, sector: sect ? sect.value.trim() : "", sediu: gv("#d204-sediu").value.trim(),
      nr_contr: gv("#d204-nrc").value.trim(), data_contr: gv("#d204-datac").value, venit3: _n(gv("#d204-venit3").value) || 0, chelt3: _n(gv("#d204-chelt3").value) || 0 };
  };
  ["#d204-aden", "#d204-acif", "#d204-aadr", "#d204-rnume", "#d204-rcif", "#d204-radr", "#d204-rtel", "#d204-remail", "#d204-categ", "#d204-caen", "#d204-sediu", "#d204-nrc", "#d204-datac", "#d204-venit3", "#d204-chelt3"].forEach((id) => { const e = gv(id); if (e) e.addEventListener("change", salveaza); });
  gv("#d204-rec").addEventListener("change", salveaza);
  gv("#d204-judet").addEventListener("change", () => { salveaza(); randeazaFormularD204(corp, nav); });
  const sect0 = gv("#d204-sector");
  if (sect0) sect0.addEventListener("change", salveaza);
  zona.querySelectorAll(".dec-d204-del").forEach((b) => b.addEventListener("click", () => {
    S.d204.asociati.splice(parseInt(b.dataset.idx), 1); randeazaFormularD204(corp, nav);
  }));
  gv("#d204-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    const cif = gv("#d204-acnp").value.trim(), nume = gv("#d204-anume").value.trim(), cota = gv("#d204-acota").value.trim();
    const err = [];
    if (!cif) err.push(["d204-acnp", "Completează CNP/CUI-ul asociatului."]);
    if (!nume) err.push(["d204-anume", "Completează numele asociatului."]);
    if (!cota) err.push(["d204-acota", "Completează cota de participare."]);
    if (err.length) { err.forEach((x) => eroareCamp(zona, x[0], x[1])); return; }
    salveaza();
    S.d204.asociati = S.d204.asociati || [];
    S.d204.asociati.push({ cif: cif, nume: nume, cota: _n(cota) || 0, venit: Math.round(_n(gv("#d204-avenit").value) || 0), pierd: Math.round(_n(gv("#d204-apierd").value) || 0) });
    randeazaFormularD204(corp, nav);
  });
  gv("#d204-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveaza();
    if (!(S.d204.asociati || []).length) { eroareCamp(zona, "d204-acnp", "Adaugă cel puțin un asociat înainte de a genera D204."); return; }
    pas2(corp, nav);
  });
}

function _d223Manual() {
  const d = S.d223 || {};
  const a = d.asociere || {}, r = d.responsabil || {}, ac = d.activitate || {};
  return {
    declarant_nume: (d.declarant_nume || "").trim(),
    declarant_prenume: (d.declarant_prenume || "").trim(),
    declarant_functie: (d.declarant_functie || "").trim(),
    d_rec1: d.d_rec1 ? 1 : 0, d_rec: d.d_rec ? 1 : 0,
    asociere: { nume: (a.nume || "").trim(), cif: (a.cif || "").replace(/\s+/g, ""), adresa: (a.adresa || "").trim(),
      telefon: (a.telefon || "").trim(), email: (a.email || "").trim() },
    responsabil: { den_r: (r.den_r || "").trim(), cif_r: (r.cif_r || "").replace(/\s+/g, ""), adresa_r: (r.adresa_r || "").trim() },
    activitate: { categ_venit: String(ac.categ_venit || "1"), forma_org: String(ac.forma_org || "2"), det_venit: String(ac.det_venit || "1"),
      caen: (ac.caen || "").replace(/\s+/g, ""), judet: (ac.judet || "").trim(), localitate: (ac.localitate || "").trim(),
      sector: (ac.sector || "").trim(), sediu: (ac.sediu || "").trim(), nr_contr: (ac.nr_contr || "").trim(),
      data_contr: (ac.data_contr || "").trim(), venit_brut: Math.round(_n(ac.venit_brut) || 0), cheltuieli: Math.round(_n(ac.cheltuieli) || 0) },
    asociati: (d.asociati || []).map((s) => ({ nume_d: (s.nume_d || "").trim(), cif_d: (s.cif_d || "").replace(/\s+/g, ""),
      dom_d: (s.dom_d || "").trim(), cota_d: _n(s.cota_d) || 0 })),
  };
}

function randeazaFormularD223(corp, nav) {
  const zona = corp.querySelector("#dec-d223-form");
  if (!zona) return;
  const d = S.d223;
  const a = d.asociere || {}, r = d.responsabil || {}, ac = d.activitate || {};
  const aso = d.asociati || [];
  const venit3 = Math.round(_n(ac.venit_brut) || 0), chelt3 = Math.round(_n(ac.cheltuieli) || 0);
  const net3 = Math.max(0, venit3 - chelt3);
  const norma = String(ac.det_venit) === "3";
  let sCota = 0;
  aso.forEach((s) => { sCota += _n(s.cota_d) || 0; });
  const okCota = Math.abs(sCota - 100) < 0.005;
  const bucuresti = String(ac.judet) === "40";
  const optJud = _D204_JUDETE.map((p) => '<option value="' + p[0] + '"' + (String(ac.judet) === p[0] ? " selected" : "") + ">" + esc(p[1]) + "</option>").join("");
  const optSel = (val, cur) => '<option value="' + val + '"' + (String(cur) === val ? " selected" : "") + ">";
  const grila = aso.length
    ? aso.map((s, i) => '<div class="dec-man-rand"><span class="dec-recl-desc">' + esc(s.nume_d || "(fără nume)") + " · CNP " + esc(s.cif_d || "?") +
        " · cotă " + esc(String(s.cota_d || 0)) + "%" + (norma ? "" : (" · venit estimat ≈ " + bani(Math.round(net3 * (_n(s.cota_d) || 0) / 100)))) + " lei</span>" +
        '<button class="btn-link dec-d223-del" data-idx="' + i + '">șterge</button></div>').join("")
    : '<div class="stare-goala stare-goala--inline">Niciun asociat. Cotele trebuie să însumeze 100; venitul net estimat se distribuie automat după cotă.</div>';
  zona.innerHTML = '<details class="dec-xml" open><summary>Venituri estimate — asociere fără personalitate juridică (' + aso.length + " asociați)</summary>" +
    '<div class="camp-eticheta" style="margin:2px 0 4px">Declarantul (persoana care depune)</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Nume declarant <span class="oblig">*</span></span><input id="d223-dnume" type="text" class="camp-input" value="' + esc(d.declarant_nume || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Prenume declarant <span class="oblig">*</span></span><input id="d223-dpren" type="text" class="camp-input" value="' + esc(d.declarant_prenume || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 160px"><span class="camp-eticheta">Funcție declarant <span class="oblig">*</span></span><input id="d223-dfunc" type="text" class="camp-input" value="' + esc(d.declarant_functie || "") + '"></label>' +
      '<label class="set-bifa"><input id="d223-rec" type="checkbox" ' + (d.d_rec ? "checked" : "") + '> <span>Rectificativă</span></label>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Asocierea</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Denumire asociere <span class="oblig">*</span></span><input id="d223-anume" type="text" class="camp-input" value="' + esc(a.nume || "") + '"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">CUI asociere <span class="oblig">*</span></span><input id="d223-acif" type="text" maxlength="10" class="camp-input" value="' + esc(a.cif || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 220px"><span class="camp-eticheta">Adresă asociere <span class="oblig">*</span></span><input id="d223-aadr" type="text" class="camp-input" value="' + esc(a.adresa || "") + '"></label>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Responsabilul asocierii</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Nume responsabil <span class="oblig">*</span></span><input id="d223-rden" type="text" class="camp-input" value="' + esc(r.den_r || "") + '"></label>' +
      '<label class="camp" style="width:160px"><span class="camp-eticheta">CNP/CUI responsabil <span class="oblig">*</span></span><input id="d223-rcif" type="text" maxlength="13" class="camp-input" value="' + esc(r.cif_r || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 220px"><span class="camp-eticheta">Adresă responsabil <span class="oblig">*</span></span><input id="d223-radr" type="text" class="camp-input" value="' + esc(r.adresa_r || "") + '"></label>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Activitatea</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Categorie venit <span class="oblig">*</span></span><select id="d223-categ" class="camp-input">' +
        ["1", "2", "4", "5", "6", "7"].map((v) => optSel(v, ac.categ_venit) + v + "</option>").join("") + "</select></label>" +
      '<label class="camp" style="width:220px"><span class="camp-eticheta">Formă organizare <span class="oblig">*</span></span><select id="d223-forma" class="camp-input">' +
        optSel("2", ac.forma_org) + "2 — asociere f.PJ</option>" + optSel("3", ac.forma_org) + "3 — transparență fiscală</option>" + optSel("4", ac.forma_org) + "4 — modificare</option></select></label>" +
      '<label class="camp" style="width:200px"><span class="camp-eticheta">Determinare venit <span class="oblig">*</span></span><select id="d223-det" class="camp-input">' +
        optSel("1", ac.det_venit) + "1 — sistem real</option>" + optSel("3", ac.det_venit) + "3 — normă de venit</option></select></label>" +
      '<label class="camp" style="width:120px"><span class="camp-eticheta">Cod CAEN <span class="oblig">*</span></span><input id="d223-caen" type="text" maxlength="4" class="camp-input" value="' + esc(ac.caen || "") + '"></label>' +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:190px"><span class="camp-eticheta">Județ <span class="oblig">*</span></span><select id="d223-judet" class="camp-input"><option value="">— alege —</option>' + optJud + "</select></label>" +
      '<label class="camp" style="flex:1 1 160px"><span class="camp-eticheta">Localitate <span class="oblig">*</span></span><input id="d223-loc" type="text" class="camp-input" value="' + esc(ac.localitate || "") + '"></label>' +
      (bucuresti ? '<label class="camp" style="width:110px"><span class="camp-eticheta">Sector <span class="oblig">*</span></span><input id="d223-sector" type="text" maxlength="1" class="camp-input" value="' + esc(ac.sector || "") + '"></label>' : "") +
      '<label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Sediu <span class="oblig">*</span></span><input id="d223-sediu" type="text" class="camp-input" value="' + esc(ac.sediu || "") + '"></label>' +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Nr. contract <span class="oblig">*</span></span><input id="d223-nrc" type="text" maxlength="15" class="camp-input" value="' + esc(ac.nr_contr || "") + '"></label>' +
      '<label class="camp" style="width:180px"><span class="camp-eticheta">Dată contract <span class="oblig">*</span></span><input id="d223-datac" type="date" class="camp-input" value="' + esc(_d204DataISO(ac.data_contr)) + '"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Venit brut estimat</span><input id="d223-venit" type="number" step="1" min="0" class="camp-input" value="' + esc(String(venit3 || "")) + '"' + (norma ? " disabled" : "") + "></label>" +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Cheltuieli estimate</span><input id="d223-chelt" type="number" step="1" min="0" class="camp-input" value="' + esc(String(chelt3 || "")) + '"' + (norma ? " disabled" : "") + "></label>" +
    "</div>" +
    '<p class="camp-ajutor" style="margin:2px 0 6px">' + (norma ? "Normă de venit: venitul repartizat pe asociați este 0 (norma o stabilește ANAF)." : ("Venit net estimat: <b>" + net3 + "</b> lei — se distribuie pe asociați după cotă.")) + "</p>" +
    grila +
    '<div class="camp-eticheta" style="margin:12px 0 4px">Adaugă asociat (persoană fizică):</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">CNP <span class="oblig">*</span></span><input id="d223-scnp" type="text" maxlength="13" class="camp-input"></label>' +
      '<label class="camp" style="flex:1 1 160px"><span class="camp-eticheta">Nume <span class="oblig">*</span></span><input id="d223-snume" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:110px"><span class="camp-eticheta">Cotă % <span class="oblig">*</span></span><input id="d223-scota" type="number" step="0.01" min="0" max="100" class="camp-input"></label>' +
      '<label class="camp" style="flex:1 1 180px"><span class="camp-eticheta">Domiciliu</span><input id="d223-sdom" type="text" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d223-add">+ adaugă</button>' +
    "</div>" +
    '<div id="d223-msg"></div>' +
    '<p class="camp-ajutor" style="margin-top:8px">Σ cote: <b>' + (Math.round(sCota * 100) / 100) + "</b>% " + (okCota ? "✓" : "(trebuie 100)") + "</p>" +
    '<p style="margin-top:8px"><button class="buton-primar" id="d223-regen">Regenerează D223</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveaza = () => {
    S.d223.declarant_nume = gv("#d223-dnume").value.trim();
    S.d223.declarant_prenume = gv("#d223-dpren").value.trim();
    S.d223.declarant_functie = gv("#d223-dfunc").value.trim();
    S.d223.d_rec = gv("#d223-rec").checked ? 1 : 0;
    S.d223.asociere = { nume: gv("#d223-anume").value.trim(), cif: gv("#d223-acif").value.trim(), adresa: gv("#d223-aadr").value.trim(),
      telefon: (S.d223.asociere || {}).telefon || "", email: (S.d223.asociere || {}).email || "" };
    S.d223.responsabil = { den_r: gv("#d223-rden").value.trim(), cif_r: gv("#d223-rcif").value.trim(), adresa_r: gv("#d223-radr").value.trim() };
    const sect = gv("#d223-sector");
    S.d223.activitate = { categ_venit: gv("#d223-categ").value, forma_org: gv("#d223-forma").value, det_venit: gv("#d223-det").value,
      caen: gv("#d223-caen").value.trim(), judet: gv("#d223-judet").value, localitate: gv("#d223-loc").value.trim(),
      sector: sect ? sect.value.trim() : "", sediu: gv("#d223-sediu").value.trim(), nr_contr: gv("#d223-nrc").value.trim(),
      data_contr: gv("#d223-datac").value, venit_brut: _n(gv("#d223-venit").value) || 0, cheltuieli: _n(gv("#d223-chelt").value) || 0 };
  };
  ["#d223-dnume", "#d223-dpren", "#d223-dfunc", "#d223-anume", "#d223-acif", "#d223-aadr", "#d223-rden", "#d223-rcif", "#d223-radr", "#d223-caen", "#d223-loc", "#d223-sediu", "#d223-nrc", "#d223-datac", "#d223-venit", "#d223-chelt"].forEach((id) => { const e = gv(id); if (e) e.addEventListener("change", salveaza); });
  gv("#d223-rec").addEventListener("change", salveaza);
  ["#d223-categ", "#d223-forma", "#d223-det", "#d223-judet"].forEach((id) => gv(id).addEventListener("change", () => { salveaza(); randeazaFormularD223(corp, nav); }));
  const sect0 = gv("#d223-sector");
  if (sect0) sect0.addEventListener("change", salveaza);
  zona.querySelectorAll(".dec-d223-del").forEach((b) => b.addEventListener("click", () => {
    S.d223.asociati.splice(parseInt(b.dataset.idx), 1); randeazaFormularD223(corp, nav);
  }));
  gv("#d223-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    const cif = gv("#d223-scnp").value.trim(), nume = gv("#d223-snume").value.trim(), cota = gv("#d223-scota").value.trim();
    const err = [];
    if (!/^\d{13}$/.test(cif)) err.push(["d223-scnp", "CNP-ul asociatului trebuie să aibă 13 cifre."]);
    if (!nume) err.push(["d223-snume", "Completează numele asociatului."]);
    if (!cota) err.push(["d223-scota", "Completează cota de participare."]);
    if (err.length) { err.forEach((x) => eroareCamp(zona, x[0], x[1])); return; }
    salveaza();
    S.d223.asociati = S.d223.asociati || [];
    S.d223.asociati.push({ nume_d: nume, cif_d: cif, cota_d: _n(cota) || 0, dom_d: gv("#d223-sdom").value.trim() });
    randeazaFormularD223(corp, nav);
  });
  gv("#d223-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveaza();
    if (!(S.d223.asociati || []).length) { eroareCamp(zona, "d223-scnp", "Adaugă cel puțin un asociat înainte de a genera D223."); return; }
    pas2(corp, nav);
  });
}

function _d216Round(x) { return x >= 0 ? Math.floor(x + 0.5) : -Math.floor(-x + 0.5); }
function _d216ImpImob(b) {
  const v = Math.round(_n(b.valoare_impozabila_imobil) || 0), p = Math.round(_n(b.plafon_imobil) || 0), c = _n(b.cota) || 0;
  const baza = _d216Round((v - p) * c / 100);
  return { baza: baza, imp: _d216Round(baza * 0.3 / 100) };
}
function _d216ImpMob(b) {
  const v = Math.round(_n(b.valoare_impozabila_mobil) || 0), p = Math.round(_n(b.plafon_mobil) || 0);
  const baza = v - p;
  return { baza: baza, imp: _d216Round(baza * 0.3 / 100) };
}

function _d216Manual() {
  const d = S.d216 || {};
  return {
    nume: (d.nume || "").trim(), cif: (d.cif || "").replace(/\s+/g, ""), domiciliuFiscal: (d.domiciliuFiscal || "").trim(),
    nume_intocmit: (d.nume_intocmit || "").trim(), functia_intocmit: (d.functia_intocmit || "").trim(), d_rec: d.d_rec ? 1 : 0,
    nume_imputernicit: (d.nume_imputernicit || "").trim(), cif_imputernicit: (d.cif_imputernicit || "").replace(/\s+/g, ""),
    imobile: (d.imobile || []).map((b) => ({ judet_imobil: (b.judet_imobil || "").trim(), cod_judet_imobil: (b.cod_judet_imobil || "").trim(),
      localitate_imobil: (b.localitate_imobil || "").trim(), cod_localitate_imobil: (b.cod_localitate_imobil || "").trim(),
      strada_imobil: (b.strada_imobil || "").trim(), cod_strada_imobil: (b.cod_strada_imobil || "").trim(),
      nr_strada: (b.nr_strada || "").trim(), nr_cadastral: (b.nr_cadastral || "").trim(),
      valoare_impozabila_imobil: Math.round(_n(b.valoare_impozabila_imobil) || 0), cota: _n(b.cota) || 0, plafon_imobil: Math.round(_n(b.plafon_imobil) || 0) })),
    mobile: (d.mobile || []).map((b) => ({ an_detinere: parseInt(b.an_detinere, 10) || 0, niv: parseInt(b.niv, 10) || 0,
      valoare_impozabila_mobil: Math.round(_n(b.valoare_impozabila_mobil) || 0), plafon_mobil: Math.round(_n(b.plafon_mobil) || 0) })),
  };
}

function randeazaFormularD216(corp, nav) {
  const zona = corp.querySelector("#dec-d216-form");
  if (!zona) return;
  const d = S.d216;
  const imob = d.imobile || [], mob = d.mobile || [];
  let tImob = 0, tMob = 0;
  const grilaI = imob.length
    ? imob.map((b, i) => { const r = _d216ImpImob(b); tImob += r.imp;
        return '<div class="dec-man-rand"><span class="dec-recl-desc">' + esc(b.localitate_imobil || "(imobil)") + " · " + esc(b.nr_cadastral || "") +
          " · valoare " + bani(Math.round(_n(b.valoare_impozabila_imobil) || 0)) + " · plafon " + bani(Math.round(_n(b.plafon_imobil) || 0)) + " · impozit " + bani(r.imp) + " lei</span>" +
          '<button class="btn-link dec-d216-deli" data-idx="' + i + '">șterge</button></div>'; }).join("")
    : '<div class="stare-goala stare-goala--inline">Niciun bun imobil.</div>';
  const grilaM = mob.length
    ? mob.map((b, i) => { const r = _d216ImpMob(b); tMob += r.imp;
        return '<div class="dec-man-rand"><span class="dec-recl-desc">Autovehicul/mobil an ' + esc(String(b.an_detinere || "")) + " · niv " + esc(String(b.niv || "")) +
          " · valoare " + bani(Math.round(_n(b.valoare_impozabila_mobil) || 0)) + " · impozit " + bani(r.imp) + " lei</span>" +
          '<button class="btn-link dec-d216-delm" data-idx="' + i + '">șterge</button></div>'; }).join("")
    : '<div class="stare-goala stare-goala--inline">Niciun bun mobil.</div>';
  zona.innerHTML = '<details class="dec-xml" open><summary>Impozit special pe bunuri de valoare mare (' + imob.length + " imobile · " + mob.length + " mobile)</summary>" +
    '<div class="camp-eticheta" style="margin:2px 0 4px">Contribuabilul</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Nume <span class="oblig">*</span></span><input id="d216-nume" type="text" class="camp-input" value="' + esc(d.nume || "") + '"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">CNP/CUI <span class="oblig">*</span></span><input id="d216-cif" type="text" maxlength="13" class="camp-input" value="' + esc(d.cif || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 240px"><span class="camp-eticheta">Domiciliu fiscal <span class="oblig">*</span></span><input id="d216-dom" type="text" class="camp-input" value="' + esc(d.domiciliuFiscal || "") + '"></label>' +
      '<label class="set-bifa"><input id="d216-rec" type="checkbox" ' + (d.d_rec ? "checked" : "") + '> <span>Rectificativă</span></label>' +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 180px"><span class="camp-eticheta">Întocmit de (nume) <span class="oblig">*</span></span><input id="d216-inume" type="text" class="camp-input" value="' + esc(d.nume_intocmit || "") + '"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Funcția <span class="oblig">*</span></span><input id="d216-ifunc" type="text" class="camp-input" value="' + esc(d.functia_intocmit || "") + '"></label>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Bunuri imobile rezidențiale (valoare peste plafon)</div>' +
    grilaI +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:8px;margin-top:6px">' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Județ</span><input id="d216-ijud" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:90px"><span class="camp-eticheta">Cod jud</span><input id="d216-icjud" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Localitate</span><input id="d216-iloc" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:90px"><span class="camp-eticheta">Cod loc</span><input id="d216-icloc" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Stradă</span><input id="d216-istr" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:90px"><span class="camp-eticheta">Cod str</span><input id="d216-icstr" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:120px"><span class="camp-eticheta">Nr. cadastral</span><input id="d216-icad" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:140px"><span class="camp-eticheta">Valoare impozabilă</span><input id="d216-ival" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:100px"><span class="camp-eticheta">Cotă %</span><input id="d216-icota" type="number" step="0.0001" min="0" max="100" class="camp-input" value="0.3"></label>' +
      '<label class="camp" style="width:140px"><span class="camp-eticheta">Plafon</span><input id="d216-iplaf" type="number" step="1" min="0" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d216-addi">+ imobil</button>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:12px 0 4px">Bunuri mobile de valoare mare (autovehicule etc.)</div>' +
    grilaM +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:8px;margin-top:6px">' +
      '<label class="camp" style="width:120px"><span class="camp-eticheta">An deținere</span><input id="d216-man" type="number" step="1" min="1900" class="camp-input"></label>' +
      '<label class="camp" style="width:100px"><span class="camp-eticheta">Niv</span><input id="d216-mniv" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Valoare impozabilă</span><input id="d216-mval" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:140px"><span class="camp-eticheta">Plafon</span><input id="d216-mplaf" type="number" step="1" min="0" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d216-addm">+ mobil</button>' +
    "</div>" +
    '<div id="d216-msg"></div>' +
    '<p class="camp-ajutor" style="margin-top:8px">Impozit imobile: <b>' + tImob + "</b> · impozit mobile: <b>" + tMob + "</b> lei (calculat cu rata validatorului 0,3%). Valoarea impozabilă trebuie să depășească plafonul.</p>" +
    '<p style="margin-top:8px"><button class="buton-primar" id="d216-regen">Regenerează D216</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveazaAntet = () => {
    S.d216.nume = gv("#d216-nume").value.trim();
    S.d216.cif = gv("#d216-cif").value.trim();
    S.d216.domiciliuFiscal = gv("#d216-dom").value.trim();
    S.d216.nume_intocmit = gv("#d216-inume").value.trim();
    S.d216.functia_intocmit = gv("#d216-ifunc").value.trim();
    S.d216.d_rec = gv("#d216-rec").checked ? 1 : 0;
  };
  ["#d216-nume", "#d216-cif", "#d216-dom", "#d216-inume", "#d216-ifunc"].forEach((id) => gv(id).addEventListener("change", salveazaAntet));
  gv("#d216-rec").addEventListener("change", salveazaAntet);
  zona.querySelectorAll(".dec-d216-deli").forEach((b) => b.addEventListener("click", () => { S.d216.imobile.splice(parseInt(b.dataset.idx), 1); randeazaFormularD216(corp, nav); }));
  zona.querySelectorAll(".dec-d216-delm").forEach((b) => b.addEventListener("click", () => { S.d216.mobile.splice(parseInt(b.dataset.idx), 1); randeazaFormularD216(corp, nav); }));
  gv("#d216-addi").addEventListener("click", () => {
    curataEroriCamp(zona);
    const val = Math.round(_n(gv("#d216-ival").value) || 0), plaf = Math.round(_n(gv("#d216-iplaf").value) || 0);
    const err = [];
    if (!gv("#d216-iloc").value.trim()) err.push(["d216-iloc", "Completează localitatea."]);
    if (!gv("#d216-icad").value.trim()) err.push(["d216-icad", "Completează numărul cadastral."]);
    if (val <= 0) err.push(["d216-ival", "Valoarea impozabilă trebuie > 0."]);
    if (val <= plaf) err.push(["d216-ival", "Valoarea impozabilă trebuie să depășească plafonul."]);
    if (err.length) { err.forEach((x) => eroareCamp(zona, x[0], x[1])); return; }
    salveazaAntet();
    S.d216.imobile = S.d216.imobile || [];
    S.d216.imobile.push({ judet_imobil: gv("#d216-ijud").value.trim(), cod_judet_imobil: gv("#d216-icjud").value.trim(),
      localitate_imobil: gv("#d216-iloc").value.trim(), cod_localitate_imobil: gv("#d216-icloc").value.trim(),
      strada_imobil: gv("#d216-istr").value.trim(), cod_strada_imobil: gv("#d216-icstr").value.trim(),
      nr_cadastral: gv("#d216-icad").value.trim(), valoare_impozabila_imobil: val, cota: _n(gv("#d216-icota").value) || 0, plafon_imobil: plaf });
    randeazaFormularD216(corp, nav);
  });
  gv("#d216-addm").addEventListener("click", () => {
    curataEroriCamp(zona);
    const val = Math.round(_n(gv("#d216-mval").value) || 0), plaf = Math.round(_n(gv("#d216-mplaf").value) || 0);
    const err = [];
    if ((parseInt(gv("#d216-man").value, 10) || 0) <= 0) err.push(["d216-man", "Completează anul de deținere."]);
    if (val <= 0) err.push(["d216-mval", "Valoarea impozabilă trebuie > 0."]);
    if (val <= plaf) err.push(["d216-mval", "Valoarea impozabilă trebuie să depășească plafonul."]);
    if (err.length) { err.forEach((x) => eroareCamp(zona, x[0], x[1])); return; }
    salveazaAntet();
    S.d216.mobile = S.d216.mobile || [];
    S.d216.mobile.push({ an_detinere: parseInt(gv("#d216-man").value, 10) || 0, niv: parseInt(gv("#d216-mniv").value, 10) || 0,
      valoare_impozabila_mobil: val, plafon_mobil: plaf });
    randeazaFormularD216(corp, nav);
  });
  gv("#d216-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveazaAntet();
    if (!(S.d216.imobile || []).length && !(S.d216.mobile || []).length) { eroareCamp(zona, "d216-iloc", "Adaugă cel puțin un bun (imobil sau mobil)."); return; }
    pas2(corp, nav);
  });
}

function _d208Manual() {
  const d = S.d208 || {};
  const im = d.imobil || {};
  return {
    nume: (d.nume || "").trim(), cif: (d.cif || "").replace(/\s+/g, ""), domiciliu: (d.domiciliu || "").trim(),
    nume_intocmit: (d.nume_intocmit || "").trim(), functia_intocmit: (d.functia_intocmit || "").trim(), dRec: d.dRec ? "1" : "0",
    nr_act_notarial: (d.nr_act_notarial || "").trim(), mod_transfer: String(d.mod_transfer || "1"), taxa_notar: Math.round(_n(d.taxa_notar) || 0),
    imobile: [{
      judet: (im.judet || "").trim(), localitate: (im.localitate || "").trim(), codSIRUTA: (im.codSIRUTA || "").replace(/\s+/g, ""),
      nr_cadastral: (im.nr_cadastral || "").trim(), tip_imobil: String(im.tip_imobil || "teren"),
      val_tranzactie_imobil: Math.round(_n(im.val_tranzactie_imobil) || 0),
      val_piata_imobil: Math.round(_n(im.val_piata_imobil || im.val_tranzactie_imobil) || 0),
      beneficiari: (d.beneficiari || []).map((b) => ({ cui: (b.cui || "").replace(/\s+/g, ""), nume: (b.nume || "").trim(), cota: _n(b.cota) || 0,
        cotaImpozit: parseInt(b.cotaImpozit, 10) || 0, baza_calcul: Math.round(_n(b.baza_calcul) || 0), impozit: Math.round(_n(b.impozit) || 0), impozit_scutit: Math.round(_n(b.impozit_scutit) || 0) })),
      parti: (d.parti || []).map((p) => ({ cui: (p.cui || "").replace(/\s+/g, ""), nume: (p.nume || "").trim(), cota: _n(p.cota) || 0 })),
    }],
  };
}

function randeazaFormularD208(corp, nav) {
  const zona = corp.querySelector("#dec-d208-form");
  if (!zona) return;
  const d = S.d208;
  const im = d.imobil || {};
  const ben = d.beneficiari || [], par = d.parti || [];
  let sBen = 0, sPar = 0, tImp = 0;
  ben.forEach((b) => { sBen += _n(b.cota) || 0; tImp += Math.round(_n(b.impozit) || 0); });
  par.forEach((p) => { sPar += _n(p.cota) || 0; });
  const okBen = ben.length && Math.abs(sBen - 100) < 0.005, okPar = par.length && Math.abs(sPar - 100) < 0.005;
  const optJud = _D204_JUDETE.map((p) => '<option value="' + p[0] + '"' + (String(im.judet) === p[0] ? " selected" : "") + ">" + esc(p[1]) + "</option>").join("");
  const optTip = (v, lbl) => '<option value="' + v + '"' + (String(im.tip_imobil || "teren") === v ? " selected" : "") + ">" + lbl + "</option>";
  const grilaB = ben.length
    ? ben.map((b, i) => '<div class="dec-man-rand"><span class="dec-recl-desc">' + esc(b.nume || "(beneficiar)") + " · CUI " + esc(b.cui || "?") +
        " · cotă " + esc(String(b.cota || 0)) + "% · cotăImpozit " + esc(String(b.cotaImpozit || 0)) + " · impozit " + bani(Math.round(_n(b.impozit) || 0)) + " lei</span>" +
        '<button class="btn-link dec-d208-delb" data-idx="' + i + '">șterge</button></div>').join("")
    : '<div class="stare-goala stare-goala--inline">Niciun beneficiar (obligatoriu; cotele însumează 100).</div>';
  const grilaP = par.length
    ? par.map((p, i) => '<div class="dec-man-rand"><span class="dec-recl-desc">' + esc(p.nume || "(parte)") + " · CUI " + esc(p.cui || "?") + " · cotă " + esc(String(p.cota || 0)) + "%</span>" +
        '<button class="btn-link dec-d208-delp" data-idx="' + i + '">șterge</button></div>').join("")
    : '<div class="stare-goala stare-goala--inline">Nicio altă parte contractantă (obligatoriu; cotele însumează 100).</div>';
  zona.innerHTML = '<details class="dec-xml" open><summary>Transfer proprietăți imobiliare — declarație notarială (' + ben.length + " beneficiari · " + par.length + " părți)</summary>" +
    '<div class="camp-eticheta" style="margin:2px 0 4px">Biroul notarial</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 240px"><span class="camp-eticheta">Denumire birou notarial <span class="oblig">*</span></span><input id="d208-nume" type="text" class="camp-input" value="' + esc(d.nume || "") + '"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">CIF <span class="oblig">*</span></span><input id="d208-cif" type="text" maxlength="10" class="camp-input" value="' + esc(d.cif || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 240px"><span class="camp-eticheta">Domiciliu fiscal <span class="oblig">*</span></span><input id="d208-dom" type="text" class="camp-input" value="' + esc(d.domiciliu || "") + '"></label>' +
      '<label class="set-bifa"><input id="d208-rec" type="checkbox" ' + (d.dRec && String(d.dRec) !== "0" ? "checked" : "") + '> <span>Rectificativă</span></label>' +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 180px"><span class="camp-eticheta">Întocmit de (nume) <span class="oblig">*</span></span><input id="d208-inume" type="text" class="camp-input" value="' + esc(d.nume_intocmit || "") + '"></label>' +
      '<label class="camp" style="width:180px"><span class="camp-eticheta">Funcția <span class="oblig">*</span></span><input id="d208-ifunc" type="text" class="camp-input" value="' + esc(d.functia_intocmit || "") + '"></label>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Tranzacția și imobilul</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Nr. act notarial <span class="oblig">*</span></span><input id="d208-act" type="text" class="camp-input" value="' + esc(d.nr_act_notarial || "") + '"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Taxă notar</span><input id="d208-taxa" type="number" step="1" min="0" class="camp-input" value="' + esc(String(d.taxa_notar || "")) + '"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Județ <span class="oblig">*</span></span><select id="d208-jud" class="camp-input"><option value="">— alege —</option>' + optJud + "</select></label>" +
      '<label class="camp" style="flex:1 1 180px"><span class="camp-eticheta">Localitate <span class="oblig">*</span></span><input id="d208-loc" type="text" class="camp-input" value="' + esc(im.localitate || "") + '"></label>' +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Cod SIRUTA <span class="oblig">*</span></span><input id="d208-sir" type="text" class="camp-input" value="' + esc(im.codSIRUTA || "") + '"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Nr. cadastral <span class="oblig">*</span></span><input id="d208-cad" type="text" class="camp-input" value="' + esc(im.nr_cadastral || "") + '"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Tip imobil</span><select id="d208-tip" class="camp-input">' + optTip("teren", "Teren") + optTip("cladire", "Clădire") + optTip("unitate", "Unitate") + "</select></label>" +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Valoare tranzacție</span><input id="d208-valt" type="number" step="1" min="0" class="camp-input" value="' + esc(String(im.val_tranzactie_imobil || "")) + '"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Valoare piață</span><input id="d208-valp" type="number" step="1" min="0" class="camp-input" value="' + esc(String(im.val_piata_imobil || "")) + '"></label>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Beneficiari (dobânditori) — cotele însumează 100</div>' +
    grilaB +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:8px;margin-top:6px">' +
      '<label class="camp" style="width:160px"><span class="camp-eticheta">CUI/CNP</span><input id="d208-bcui" type="text" maxlength="13" class="camp-input"></label>' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Nume</span><input id="d208-bnume" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:90px"><span class="camp-eticheta">Cotă %</span><input id="d208-bcota" type="number" step="0.01" min="0" max="100" class="camp-input"></label>' +
      '<label class="camp" style="width:120px"><span class="camp-eticheta">Cotă impozit</span><select id="d208-bci" class="camp-input"><option value="0">0</option><option value="1">1</option><option value="3" selected>3</option></select></label>' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Bază calcul</span><input id="d208-bbaza" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:120px"><span class="camp-eticheta">Impozit</span><input id="d208-bimp" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:120px"><span class="camp-eticheta">Impozit scutit</span><input id="d208-bsc" type="number" step="1" min="0" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d208-addb">+ beneficiar</button>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:12px 0 4px">Celelalte părți contractante (înstrăinători) — cotele însumează 100</div>' +
    grilaP +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:8px;margin-top:6px">' +
      '<label class="camp" style="width:160px"><span class="camp-eticheta">CUI/CNP</span><input id="d208-pcui" type="text" maxlength="13" class="camp-input"></label>' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Nume</span><input id="d208-pnume" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:90px"><span class="camp-eticheta">Cotă %</span><input id="d208-pcota" type="number" step="0.01" min="0" max="100" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d208-addp">+ parte</button>' +
    "</div>" +
    '<div id="d208-msg"></div>' +
    '<p class="camp-ajutor" style="margin-top:8px">Σ cote beneficiari: <b>' + (Math.round(sBen * 100) / 100) + "</b>% " + (okBen ? "✓" : "(trebuie 100)") +
      " · Σ cote părți: <b>" + (Math.round(sPar * 100) / 100) + "</b>% " + (okPar ? "✓" : "(trebuie 100)") + " · impozit total: <b>" + tImp + "</b> lei</p>" +
    '<p style="margin-top:8px"><button class="buton-primar" id="d208-regen">Regenerează D208</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveaza = () => {
    S.d208.nume = gv("#d208-nume").value.trim();
    S.d208.cif = gv("#d208-cif").value.trim();
    S.d208.domiciliu = gv("#d208-dom").value.trim();
    S.d208.dRec = gv("#d208-rec").checked ? "1" : "0";
    S.d208.nume_intocmit = gv("#d208-inume").value.trim();
    S.d208.functia_intocmit = gv("#d208-ifunc").value.trim();
    S.d208.nr_act_notarial = gv("#d208-act").value.trim();
    S.d208.taxa_notar = _n(gv("#d208-taxa").value) || 0;
    S.d208.imobil = { judet: gv("#d208-jud").value, localitate: gv("#d208-loc").value.trim(), codSIRUTA: gv("#d208-sir").value.trim(),
      nr_cadastral: gv("#d208-cad").value.trim(), tip_imobil: gv("#d208-tip").value,
      val_tranzactie_imobil: _n(gv("#d208-valt").value) || 0, val_piata_imobil: _n(gv("#d208-valp").value) || 0 };
  };
  ["#d208-nume", "#d208-cif", "#d208-dom", "#d208-inume", "#d208-ifunc", "#d208-act", "#d208-taxa", "#d208-jud", "#d208-loc", "#d208-sir", "#d208-cad", "#d208-tip", "#d208-valt", "#d208-valp"].forEach((id) => gv(id).addEventListener("change", salveaza));
  gv("#d208-rec").addEventListener("change", salveaza);
  zona.querySelectorAll(".dec-d208-delb").forEach((b) => b.addEventListener("click", () => { S.d208.beneficiari.splice(parseInt(b.dataset.idx), 1); randeazaFormularD208(corp, nav); }));
  zona.querySelectorAll(".dec-d208-delp").forEach((b) => b.addEventListener("click", () => { S.d208.parti.splice(parseInt(b.dataset.idx), 1); randeazaFormularD208(corp, nav); }));
  gv("#d208-addb").addEventListener("click", () => {
    curataEroriCamp(zona);
    const cui = gv("#d208-bcui").value.trim(), nume = gv("#d208-bnume").value.trim(), cota = gv("#d208-bcota").value.trim();
    const err = [];
    if (!cui) err.push(["d208-bcui", "Completează CUI/CNP-ul beneficiarului."]);
    if (!nume) err.push(["d208-bnume", "Completează numele."]);
    if (!cota) err.push(["d208-bcota", "Completează cota."]);
    if (err.length) { err.forEach((x) => eroareCamp(zona, x[0], x[1])); return; }
    salveaza();
    S.d208.beneficiari = S.d208.beneficiari || [];
    S.d208.beneficiari.push({ cui: cui, nume: nume, cota: _n(cota) || 0, cotaImpozit: parseInt(gv("#d208-bci").value, 10) || 0,
      baza_calcul: Math.round(_n(gv("#d208-bbaza").value) || 0), impozit: Math.round(_n(gv("#d208-bimp").value) || 0), impozit_scutit: Math.round(_n(gv("#d208-bsc").value) || 0) });
    randeazaFormularD208(corp, nav);
  });
  gv("#d208-addp").addEventListener("click", () => {
    curataEroriCamp(zona);
    const cui = gv("#d208-pcui").value.trim(), nume = gv("#d208-pnume").value.trim(), cota = gv("#d208-pcota").value.trim();
    const err = [];
    if (!cui) err.push(["d208-pcui", "Completează CUI/CNP-ul părții."]);
    if (!nume) err.push(["d208-pnume", "Completează numele."]);
    if (!cota) err.push(["d208-pcota", "Completează cota."]);
    if (err.length) { err.forEach((x) => eroareCamp(zona, x[0], x[1])); return; }
    salveaza();
    S.d208.parti = S.d208.parti || [];
    S.d208.parti.push({ cui: cui, nume: nume, cota: _n(cota) || 0 });
    randeazaFormularD208(corp, nav);
  });
  gv("#d208-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveaza();
    if (!(S.d208.beneficiari || []).length) { eroareCamp(zona, "d208-bcui", "Adaugă cel puțin un beneficiar."); return; }
    if (!(S.d208.parti || []).length) { eroareCamp(zona, "d208-pcui", "Adaugă cel puțin o parte contractantă."); return; }
    pas2(corp, nav);
  });
}

function _d221Manual() {
  const d = S.d221 || {};
  const ac = d.activitate || {};
  const forma = String(d.forma_org || "1");
  const m = {
    nume_declar: (d.nume_declar || "").trim(), prenume_declar: (d.prenume_declar || "").trim(),
    functie_declar: (d.functie_declar || "TITULAR").trim(),
    cif: (d.cif || "").replace(/\s+/g, ""), nume_a: (d.nume_a || "").trim(), adresa_a: (d.adresa_a || "").trim(),
    forma_org: forma, d_rec: d.d_rec ? 1 : 0,
    activitati: [{ judet: (ac.judet || "").trim(), localitate: (ac.localitate || "").trim(), optiune: String(ac.optiune || "0"),
      produse: (d.produse || []).map((p) => ({ codp: (p.codp || "").trim(), prod1: _n(p.prod1) || 0 })) }],
    asociati: forma === "2" ? (d.asociati || []).map((s) => ({ nume_d: (s.nume_d || "").trim(), cif_d: (s.cif_d || "").replace(/\s+/g, ""),
      dom_d: (s.dom_d || "").trim(), cota_d: _n(s.cota_d) || 0 })) : [],
  };
  if (forma === "2") { m.nr_contr = (d.nr_contr || "").trim(); m.data_contr = (d.data_contr || "").trim(); }
  return m;
}

function randeazaFormularD221(corp, nav) {
  const zona = corp.querySelector("#dec-d221-form");
  if (!zona) return;
  const d = S.d221;
  const ac = d.activitate || {};
  const forma = String(d.forma_org || "1");
  const prod = d.produse || [], aso = d.asociati || [];
  let sCota = 0;
  aso.forEach((s) => { sCota += _n(s.cota_d) || 0; });
  const okCota = aso.length && Math.abs(sCota - 100) < 0.005;
  const optJud = _D204_JUDETE.map((p) => '<option value="' + p[0] + '"' + (String(ac.judet) === p[0] ? " selected" : "") + ">" + esc(p[1]) + "</option>").join("");
  const grilaP = prod.length
    ? prod.map((p, i) => '<div class="dec-man-rand"><span class="dec-recl-desc">Cod produs ' + esc(p.codp || "?") + " · suprafață/nr. capete " + esc(String(p.prod1 || 0)) + "</span>" +
        '<button class="btn-link dec-d221-delp" data-idx="' + i + '">șterge</button></div>').join("")
    : '<div class="stare-goala stare-goala--inline">Niciun produs. Adaugă codul produsului agricol și suprafața (ha) sau numărul de capete.</div>';
  const grilaA = aso.length
    ? aso.map((s, i) => '<div class="dec-man-rand"><span class="dec-recl-desc">' + esc(s.nume_d || "(asociat)") + " · CNP " + esc(s.cif_d || "?") + " · cotă " + esc(String(s.cota_d || 0)) + "%</span>" +
        '<button class="btn-link dec-d221-dela" data-idx="' + i + '">șterge</button></div>').join("")
    : '<div class="stare-goala stare-goala--inline">Niciun asociat (forma asociere cere minim 2, cotele însumează 100).</div>';
  zona.innerHTML = '<details class="dec-xml" open><summary>Venituri agricole pe norme de venit (' + prod.length + " produse" + (forma === "2" ? (" · " + aso.length + " asociați") : "") + ")</summary>" +
    '<div class="camp-eticheta" style="margin:2px 0 4px">Contribuabilul / titularul</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Nume declarant <span class="oblig">*</span></span><input id="d221-dnume" type="text" class="camp-input" value="' + esc(d.nume_declar || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Prenume declarant <span class="oblig">*</span></span><input id="d221-dpren" type="text" class="camp-input" value="' + esc(d.prenume_declar || "") + '"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">CNP contribuabil <span class="oblig">*</span></span><input id="d221-cif" type="text" maxlength="13" class="camp-input" value="' + esc(d.cif || "") + '"></label>' +
      '<label class="set-bifa"><input id="d221-rec" type="checkbox" ' + (d.d_rec ? "checked" : "") + '> <span>Rectificativă</span></label>' +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Nume/denumire contribuabil <span class="oblig">*</span></span><input id="d221-numea" type="text" class="camp-input" value="' + esc(d.nume_a || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 240px"><span class="camp-eticheta">Adresă <span class="oblig">*</span></span><input id="d221-adr" type="text" class="camp-input" value="' + esc(d.adresa_a || "") + '"></label>' +
      '<label class="camp" style="width:200px"><span class="camp-eticheta">Formă organizare <span class="oblig">*</span></span><select id="d221-forma" class="camp-input"><option value="1"' + (forma === "2" ? "" : " selected") + ">1 — individual</option><option value=\"2\"" + (forma === "2" ? " selected" : "") + ">2 — asociere f.PJ</option></select></label>" +
    "</div>" +
    (forma === "2" ?
      '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
        '<label class="camp" style="width:160px"><span class="camp-eticheta">Nr. contract <span class="oblig">*</span></span><input id="d221-nrc" type="text" class="camp-input" value="' + esc(d.nr_contr || "") + '"></label>' +
        '<label class="camp" style="width:180px"><span class="camp-eticheta">Dată contract <span class="oblig">*</span></span><input id="d221-datac" type="date" class="camp-input" value="' + esc(_d204DataISO(d.data_contr)) + '"></label>' +
      "</div>" : "") +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Activitatea agricolă</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:190px"><span class="camp-eticheta">Județ <span class="oblig">*</span></span><select id="d221-jud" class="camp-input"><option value="">— alege —</option>' + optJud + "</select></label>" +
      '<label class="camp" style="flex:1 1 180px"><span class="camp-eticheta">Localitate <span class="oblig">*</span></span><input id="d221-loc" type="text" class="camp-input" value="' + esc(ac.localitate || "") + '"></label>' +
      '<label class="camp" style="width:200px"><span class="camp-eticheta">Opțiune normă</span><select id="d221-opt" class="camp-input"><option value="0"' + (String(ac.optiune) === "1" ? "" : " selected") + '>0 — normă de venit</option><option value="1"' + (String(ac.optiune) === "1" ? " selected" : "") + ">1 — sistem real</option></select></label>" +
    "</div>" +
    grilaP +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:8px;margin-top:6px">' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Cod produs</span><input id="d221-pcod" type="text" maxlength="3" class="camp-input"></label>' +
      '<label class="camp" style="width:200px"><span class="camp-eticheta">Suprafață (ha) / nr. capete</span><input id="d221-pval" type="number" step="0.01" min="0" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d221-addp">+ produs</button>' +
    "</div>" +
    (forma === "2" ?
      '<div class="camp-eticheta" style="margin:12px 0 4px">Asociați (minim 2; cotele însumează 100)</div>' + grilaA +
      '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:8px;margin-top:6px">' +
        '<label class="camp" style="width:160px"><span class="camp-eticheta">CNP</span><input id="d221-acnp" type="text" maxlength="13" class="camp-input"></label>' +
        '<label class="camp" style="flex:1 1 140px"><span class="camp-eticheta">Nume</span><input id="d221-anume" type="text" class="camp-input"></label>' +
        '<label class="camp" style="flex:1 1 140px"><span class="camp-eticheta">Domiciliu</span><input id="d221-adom" type="text" class="camp-input"></label>' +
        '<label class="camp" style="width:90px"><span class="camp-eticheta">Cotă %</span><input id="d221-acota" type="number" step="0.01" min="0" max="100" class="camp-input"></label>' +
        '<button class="buton-secundar" id="d221-adda">+ asociat</button>' +
      "</div>" +
      '<p class="camp-ajutor" style="margin-top:6px">Σ cote asociați: <b>' + (Math.round(sCota * 100) / 100) + "</b>% " + (okCota ? "✓" : "(trebuie 100)") + "</p>"
      : "") +
    '<div id="d221-msg"></div>' +
    '<p class="camp-ajutor" style="margin-top:6px">D221 nu conține sume de impozit — ANAF aplică normele de venit intern (totalPlata_A=0).</p>' +
    '<p style="margin-top:8px"><button class="buton-primar" id="d221-regen">Regenerează D221</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveaza = () => {
    S.d221.nume_declar = gv("#d221-dnume").value.trim();
    S.d221.prenume_declar = gv("#d221-dpren").value.trim();
    S.d221.cif = gv("#d221-cif").value.trim();
    S.d221.d_rec = gv("#d221-rec").checked ? 1 : 0;
    S.d221.nume_a = gv("#d221-numea").value.trim();
    S.d221.adresa_a = gv("#d221-adr").value.trim();
    S.d221.forma_org = gv("#d221-forma").value;
    const nrc = gv("#d221-nrc"), dtc = gv("#d221-datac");
    if (nrc) S.d221.nr_contr = nrc.value.trim();
    if (dtc) S.d221.data_contr = dtc.value;
    S.d221.activitate = { judet: gv("#d221-jud").value, localitate: gv("#d221-loc").value.trim(), optiune: gv("#d221-opt").value };
  };
  ["#d221-dnume", "#d221-dpren", "#d221-cif", "#d221-numea", "#d221-adr", "#d221-jud", "#d221-loc", "#d221-opt"].forEach((id) => gv(id).addEventListener("change", salveaza));
  gv("#d221-rec").addEventListener("change", salveaza);
  gv("#d221-forma").addEventListener("change", () => { salveaza(); randeazaFormularD221(corp, nav); });
  ["#d221-nrc", "#d221-datac"].forEach((id) => { const e = gv(id); if (e) e.addEventListener("change", salveaza); });
  zona.querySelectorAll(".dec-d221-delp").forEach((b) => b.addEventListener("click", () => { S.d221.produse.splice(parseInt(b.dataset.idx), 1); randeazaFormularD221(corp, nav); }));
  zona.querySelectorAll(".dec-d221-dela").forEach((b) => b.addEventListener("click", () => { S.d221.asociati.splice(parseInt(b.dataset.idx), 1); randeazaFormularD221(corp, nav); }));
  gv("#d221-addp").addEventListener("click", () => {
    curataEroriCamp(zona);
    const cod = gv("#d221-pcod").value.trim();
    if (!cod) { eroareCamp(zona, "d221-pcod", "Completează codul produsului."); return; }
    salveaza();
    S.d221.produse = S.d221.produse || [];
    S.d221.produse.push({ codp: cod, prod1: _n(gv("#d221-pval").value) || 0 });
    randeazaFormularD221(corp, nav);
  });
  const adda = gv("#d221-adda");
  if (adda) adda.addEventListener("click", () => {
    curataEroriCamp(zona);
    const cif = gv("#d221-acnp").value.trim(), nume = gv("#d221-anume").value.trim(), cota = gv("#d221-acota").value.trim();
    const err = [];
    if (!/^\d{13}$/.test(cif)) err.push(["d221-acnp", "CNP-ul asociatului trebuie să aibă 13 cifre."]);
    if (!nume) err.push(["d221-anume", "Completează numele."]);
    if (!cota) err.push(["d221-acota", "Completează cota."]);
    if (err.length) { err.forEach((x) => eroareCamp(zona, x[0], x[1])); return; }
    salveaza();
    S.d221.asociati = S.d221.asociati || [];
    S.d221.asociati.push({ nume_d: nume, cif_d: cif, dom_d: gv("#d221-adom").value.trim(), cota_d: _n(cota) || 0 });
    randeazaFormularD221(corp, nav);
  });
  gv("#d221-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveaza();
    if (!(S.d221.produse || []).length) { eroareCamp(zona, "d221-pcod", "Adaugă cel puțin un produs agricol."); return; }
    if (String(S.d221.forma_org) === "2" && (S.d221.asociati || []).length < 2) { eroareCamp(zona, "d221-acnp", "Forma asociere cere minim 2 asociați."); return; }
    pas2(corp, nav);
  });
}

const _D603_JUDETE = [["AB","Alba"],["AR","Arad"],["AG","Argeș"],["BC","Bacău"],["BH","Bihor"],["BN","Bistrița-Năsăud"],["BT","Botoșani"],["BV","Brașov"],["BR","Brăila"],["BZ","Buzău"],["CS","Caraș-Severin"],["CL","Călărași"],["CJ","Cluj"],["CT","Constanța"],["CV","Covasna"],["DB","Dâmbovița"],["DJ","Dolj"],["GL","Galați"],["GR","Giurgiu"],["GJ","Gorj"],["HR","Harghita"],["HD","Hunedoara"],["IL","Ialomița"],["IS","Iași"],["IF","Ilfov"],["MM","Maramureș"],["MH","Mehedinți"],["MS","Mureș"],["NT","Neamț"],["OT","Olt"],["PH","Prahova"],["SM","Satu Mare"],["SJ","Sălaj"],["SB","Sibiu"],["SV","Suceava"],["TR","Teleorman"],["TM","Timiș"],["TL","Tulcea"],["VS","Vaslui"],["VL","Vâlcea"],["VN","Vrancea"],["B","București"]];

function _d603Manual() {
  const d = S.d603 || {};
  return {
    numeContrib: (d.numeContrib || "").trim(), cif: (d.cif || "").replace(/\s+/g, ""),
    taraContrib: (d.taraContrib || "RO").trim().toUpperCase(), judetContrib: (d.judetContrib || "").trim().toUpperCase(),
    exceptare: parseInt(d.exceptare, 10) || 2, statAsigurare: (d.statAsigurare || "").trim().toUpperCase(),
    dataInceput: (d.dataInceput || "").trim(), dataSfarsit: (d.dataSfarsit || "").trim(), dataExceptare: (d.dataExceptare || "").trim(),
    documente: (d.documente || "").trim(), imputernicit: 0,
  };
}

function randeazaFormularD603(corp, nav) {
  const zona = corp.querySelector("#dec-d603-form");
  if (!zona) return;
  const d = S.d603;
  const roTara = String(d.taraContrib || "RO").toUpperCase() === "RO";
  const optJud = _D603_JUDETE.map((p) => '<option value="' + p[0] + '"' + (String(d.judetContrib).toUpperCase() === p[0] ? " selected" : "") + ">" + esc(p[1]) + "</option>").join("");
  const optExc = (v) => '<option value="' + v + '"' + (String(d.exceptare || "2") === v ? " selected" : "") + ">" + v + "</option>";
  zona.innerHTML = '<details class="dec-xml" open><summary>Exceptare de la plata CASS — declarație pe propria răspundere</summary>' +
    '<div class="camp-eticheta" style="margin:2px 0 4px">Persoana fizică</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 220px"><span class="camp-eticheta">Nume și prenume <span class="oblig">*</span></span><input id="d603-nume" type="text" class="camp-input" value="' + esc(d.numeContrib || "") + '"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">CNP <span class="oblig">*</span></span><input id="d603-cif" type="text" maxlength="13" class="camp-input" value="' + esc(d.cif || "") + '"></label>' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Țară <span class="oblig">*</span></span><input id="d603-tara" type="text" maxlength="2" class="camp-input" value="' + esc(d.taraContrib || "RO") + '"></label>' +
      (roTara ? '<label class="camp" style="width:180px"><span class="camp-eticheta">Județ <span class="oblig">*</span></span><select id="d603-jud" class="camp-input"><option value="">— alege —</option>' + optJud + "</select></label>" : "") +
    "</div>" +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Exceptarea</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:160px"><span class="camp-eticheta">Categorie exceptare <span class="oblig">*</span></span><select id="d603-exc" class="camp-input">' + optExc("2") + optExc("3") + optExc("4") + "</select></label>" +
      '<label class="camp" style="width:180px"><span class="camp-eticheta">Stat de asigurare <span class="oblig">*</span></span><input id="d603-stat" type="text" maxlength="2" class="camp-input" value="' + esc(d.statAsigurare || "") + '" placeholder="ex. DE"></label>' +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Data început <span class="oblig">*</span></span><input id="d603-di" type="date" class="camp-input" value="' + esc(_d204DataISO(d.dataInceput)) + '"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Data sfârșit <span class="oblig">*</span></span><input id="d603-ds" type="date" class="camp-input" value="' + esc(_d204DataISO(d.dataSfarsit)) + '"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Data exceptării <span class="oblig">*</span></span><input id="d603-de" type="date" class="camp-input" value="' + esc(_d204DataISO(d.dataExceptare)) + '"></label>' +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">' +
      '<label class="camp" style="flex:1 1 320px"><span class="camp-eticheta">Documente justificative <span class="oblig">*</span></span><input id="d603-doc" type="text" class="camp-input" value="' + esc(d.documente || "") + '"></label>' +
    "</div>" +
    '<p class="camp-ajutor" style="margin:6px 0 0">Statul de asigurare trebuie să fie diferit de RO (ești asigurat în alt stat). D603 nu conține sume — doar perioada și categoria exceptării.</p>' +
    '<div id="d603-msg"></div>' +
    '<p style="margin-top:8px"><button class="buton-primar" id="d603-regen">Regenerează D603</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveaza = () => {
    S.d603.numeContrib = gv("#d603-nume").value.trim();
    S.d603.cif = gv("#d603-cif").value.trim();
    S.d603.taraContrib = gv("#d603-tara").value.trim().toUpperCase();
    const jud = gv("#d603-jud"); S.d603.judetContrib = jud ? jud.value : "";
    S.d603.exceptare = gv("#d603-exc").value;
    S.d603.statAsigurare = gv("#d603-stat").value.trim().toUpperCase();
    S.d603.dataInceput = gv("#d603-di").value;
    S.d603.dataSfarsit = gv("#d603-ds").value;
    S.d603.dataExceptare = gv("#d603-de").value;
    S.d603.documente = gv("#d603-doc").value.trim();
  };
  ["#d603-nume", "#d603-cif", "#d603-exc", "#d603-stat", "#d603-di", "#d603-ds", "#d603-de", "#d603-doc"].forEach((id) => gv(id).addEventListener("change", salveaza));
  gv("#d603-tara").addEventListener("change", () => { salveaza(); randeazaFormularD603(corp, nav); });
  const jud0 = gv("#d603-jud"); if (jud0) jud0.addEventListener("change", salveaza);
  gv("#d603-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveaza();
    const err = [];
    if (!S.d603.numeContrib) err.push(["d603-nume", "Completează numele."]);
    if (!/^\d{13}$/.test(S.d603.cif)) err.push(["d603-cif", "CNP-ul trebuie să aibă 13 cifre."]);
    if (String(S.d603.taraContrib) === "RO" && !S.d603.judetContrib) err.push(["d603-jud", "Alege județul."]);
    if (!S.d603.statAsigurare) err.push(["d603-stat", "Completează statul de asigurare."]);
    else if (S.d603.statAsigurare === "RO") err.push(["d603-stat", "Statul de asigurare trebuie diferit de RO."]);
    if (!S.d603.dataInceput || !S.d603.dataSfarsit || !S.d603.dataExceptare) err.push(["d603-di", "Completează cele trei date."]);
    if (!S.d603.documente) err.push(["d603-doc", "Completează documentele justificative."]);
    if (err.length) { err.forEach((x) => eroareCamp(zona, x[0], x[1])); return; }
    pas2(corp, nav);
  });
}

function _d600Manual() {
  const d = S.d600 || {};
  const m = {
    nume_c: (d.nume_c || "").trim(), initiala_c: (d.initiala_c || "").trim(), prenume_c: (d.prenume_c || "").trim(),
    cif_c: (d.cif_c || "").replace(/\s+/g, ""), adresa_c: (d.adresa_c || "").trim(),
    cont_c: (d.cont_c || "").replace(/\s+/g, "").toUpperCase(), d_rec: d.d_rec ? 1 : 0,
  };
  if (d.cas_opt) {
    m.cas_opt = 1;
    const b = Math.round(_n(d.baza_lunara) || 0);
    for (let i = 1; i <= 12; i++) m["baza" + i] = b;
  }
  return m;
}

function randeazaFormularD600(corp, nav) {
  const zona = corp.querySelector("#dec-d600-form");
  if (!zona) return;
  const d = S.d600;
  const cas = !!d.cas_opt;
  const baza = Math.round(_n(d.baza_lunara) || 0);
  zona.innerHTML = '<details class="dec-xml" open><summary>Bază CAS/CASS estimată — persoană fizică</summary>' +
    '<div class="camp-eticheta" style="margin:2px 0 4px">Contribuabilul</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">CNP <span class="oblig">*</span></span><input id="d600-cnp" type="text" maxlength="13" class="camp-input" value="' + esc(d.cif_c || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Nume <span class="oblig">*</span></span><input id="d600-nume" type="text" class="camp-input" value="' + esc(d.nume_c || "") + '"></label>' +
      '<label class="camp" style="width:110px"><span class="camp-eticheta">Inițiala tată <span class="oblig">*</span></span><input id="d600-init" type="text" maxlength="1" class="camp-input" value="' + esc(d.initiala_c || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Prenume <span class="oblig">*</span></span><input id="d600-pren" type="text" class="camp-input" value="' + esc(d.prenume_c || "") + '"></label>' +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 260px"><span class="camp-eticheta">Adresă <span class="oblig">*</span></span><input id="d600-adr" type="text" class="camp-input" value="' + esc(d.adresa_c || "") + '"></label>' +
      '<label class="camp" style="width:240px"><span class="camp-eticheta">IBAN (opțional)</span><input id="d600-cont" type="text" class="camp-input" value="' + esc(d.cont_c || "") + '"></label>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Contribuția de asigurări sociale (CAS)</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">' +
      '<label class="set-bifa"><input id="d600-cas" type="checkbox" ' + (cas ? "checked" : "") + '> <span>Datorez CAS (estimare)</span></label>' +
      (cas ? '<label class="camp" style="width:200px"><span class="camp-eticheta">Bază lunară estimată <span class="oblig">*</span></span><input id="d600-baza" type="number" step="1" min="0" class="camp-input" value="' + esc(String(baza || "")) + '"></label>' : "") +
    "</div>" +
    '<p class="camp-ajutor" style="margin:6px 0 0">' + (cas ? ("Baza lunară se aplică pentru toate cele 12 luni (trebuie ≥ salariul minim brut). CAS estimat = opțiune + 12 baze.") : "Bifează dacă datorezi CAS și introdu baza lunară estimată. (CASS pe categorii = increment ulterior.)") + "</p>" +
    '<div id="d600-msg"></div>' +
    '<p style="margin-top:8px"><button class="buton-primar" id="d600-regen">Regenerează D600</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveaza = () => {
    S.d600.cif_c = gv("#d600-cnp").value.trim();
    S.d600.nume_c = gv("#d600-nume").value.trim();
    S.d600.initiala_c = gv("#d600-init").value.trim();
    S.d600.prenume_c = gv("#d600-pren").value.trim();
    S.d600.adresa_c = gv("#d600-adr").value.trim();
    S.d600.cont_c = gv("#d600-cont").value.replace(/\s+/g, "").toUpperCase();
    S.d600.cas_opt = gv("#d600-cas").checked;
    const bz = gv("#d600-baza"); if (bz) S.d600.baza_lunara = _n(bz.value) || 0;
  };
  ["#d600-cnp", "#d600-nume", "#d600-init", "#d600-pren", "#d600-adr", "#d600-cont"].forEach((id) => gv(id).addEventListener("change", salveaza));
  gv("#d600-cas").addEventListener("change", () => { salveaza(); randeazaFormularD600(corp, nav); });
  const bz0 = gv("#d600-baza"); if (bz0) bz0.addEventListener("change", salveaza);
  gv("#d600-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveaza();
    const err = [];
    if (!/^\d{13}$/.test(S.d600.cif_c)) err.push(["d600-cnp", "CNP-ul trebuie să aibă 13 cifre."]);
    if (!S.d600.nume_c) err.push(["d600-nume", "Completează numele."]);
    if (!S.d600.adresa_c) err.push(["d600-adr", "Completează adresa."]);
    if (!S.d600.cas_opt) err.push(["d600-cas", "Bifează cel puțin CAS (declarația trebuie să aibă o contribuție)."]);
    else if ((_n(S.d600.baza_lunara) || 0) <= 0) err.push(["d600-baza", "Completează baza lunară estimată."]);
    if (err.length) { err.forEach((x) => eroareCamp(zona, x[0], x[1])); return; }
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
