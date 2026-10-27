// declaratii.js — ecran asistent: creeaza o declaratie -> trimite in coada de validare.
// Flux 3 pasi intr-o fereastra: 1) firma+tip+perioada  2) genereaza+verifica  3) trimite in coada.
// inceput_la porneste la deschiderea ecranului (cronometru efort) si merge la /coada.
// Backend: GET /tenants, GET /declaratii/tipuri, POST /declaratii/{tip}/valideaza, POST /coada.
// [duk_valideaza_v1] Pasul 2 VALIDEAZA la ANAF (DUKIntegrator), nu doar genereaza:
// pana la 15.07.2026 spunea "declaratia pare in regula" fara sa fi validat nimic,
// iar asistentul trimitea in coada un XML nevalidat. Trei stari: valid/erori/gri.

import { api, ultimaCerere, esc, bani, arataMesaj, dataRo, eroareCamp, curataEroriCamp, semnAjutor, ALEGE, alegeDacaLipseste, cereAlegerile, selectDaNu, daNu, cate, focusFaraSalt, arataRefuzul } from "../api.js?v=c6c45aefe4";
import { trimiteInCoada, casetaTrimisa, etichetaTrimitere, deschideInCoada, legaturiNote } from "./coada_trimite.js?v=50cade9fc8";
import { butonSpreEcran } from "./ecran_destinatie.js?v=0a2b447df1";   // [lotul 10, 431] refuzul care trimite la ce lipsește
import { cautaInLista } from "./emitere_ecran.js?v=5b93aa95d0";   // [lotul 13, 653] căutarea în lista țărilor (aceeași ca la articole)
// [lotul 11, 440] numele câmpurilor din refuzul serverului -> id-ul de pe ecran (`pre` + nume), pentru `arataRefuzul` (toate erorile deodată)
const _campuriCu = (e, pre) => Object.fromEntries(((e && e.erori_campuri) || []).map((c) => [c.camp, pre + c.camp]));
// [ajutor_contextual] mapare tip declaratie -> ID functionalitate pentru semnul "?" dinamic
const _DECL_AJUTOR = { d100:"F026", d101:"F027", d112:"F028", d205:"F029", d300:"F031",
  d301:"F032", d390:"F033", d394:"F034", d406:"F035", d710:"F192", d311:"F207", d307:"F217", d107:"F211", d177:"F210", d207:"F209", d212:"F030", d230:"F208", d204:"F223", d216:"F225", d208:"F224", d603:"F233", d104:"F212", d114:"F230", d110:"F216", d398:"F242", d318:"F232" };

const LUNI = ["ianuarie","februarie","martie","aprilie","mai","iunie",
              "iulie","august","septembrie","octombrie","noiembrie","decembrie"];
const TRIM = ["T1 (ian-mar)","T2 (apr-iun)","T3 (iul-sep)","T4 (oct-dec)"];
const LUNI_TRIM = ["ian–mar", "apr–iun", "iul–sep", "oct–dec"];   // [Retest 2 pct.14] lunile trimestrului, după „T3/2026”

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

// [deficiența 324, 18.10.2026] `preset` = {tenant_id, tip, an, luna, trim}: „Generează din Declarații” din „De depus” deschide ecranul cu
// firma, tipul și perioada declarației depășite (o declarație veche, fără cererea păstrată); omul apasă „Continuă”, apoi „Înlocuiește”.
export async function randeazaDeclaratii(corp, nav, firmaFixa, preset = null) {
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
    rectConfirmata: null,                    // [lotul 12, C19] {cheie: tip|an|perioadă, amprenta}: rectificativa D394 cerută după diferențe
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
    // [lotul 10, decizia Costin B] D205 completat manual: beneficiarii de dividende pe care notele nu-i au (firma preluată — dividendele
    // plătite înainte de preluare există numai în balanța de deschidere). Gol = D205 din notele validate (calea automată).
    d205: { beneficiari: [] },
    // [formular_manual_d212] Declaratia unica PF: identitate (cif=CNP/nume/adresa) + fisa RIP AFISATA
    // (pull din registru; venitul/CAS/CASS/impozit — informativ). Increment: genereaza cazul minim
    // DUK-valid (identitate); popularea cap11/oblig_realizat din fisa = pas urmator. In memorie, ca d207.
    d212: { cif: "", nume_c: "", adresa_c: "", d_rec: 0, din_rip: null, pierdere_precedenta: "", caen: "", nr_zile_scutite_rip: "", fisa: null, fisa_eroare: "", norma: [], venituri: [], strainatate: [], alte_cass: {}, exceptie_minim_cass: "" },
    // [formular_manual_d230] redirectionare 3,5% catre ONG (PF): identitate + entitate beneficiara. In memorie, ca d207.
    d230: { cif_c: "", nume_c: "", initiala_c: "", prenume_c: "", adresa_c: "", telefon_c: "", email_c: "", den_entitate: "", cif_entitate: "", cont_entitate: "", suma_entitate: "", procent: "", valabilitate_distribuire: null },
    // [formular_manual_d204] asociere fara personalitate juridica: asociere + reprezentant + o activitate + asociati. In memorie, ca d207.
    d204: { d_rec: 0, asociere: { den: "", cif: "", adresa: "" }, reprezentant: { nume: "", cif: "", adresa: "", telefon: "", email: "" }, activitate: { categ_venit: null, forma_org: null, caen: "", judet: "", sector: "", sediu: "", nr_contr: "", data_contr: "", venit3: "", chelt3: "" }, asociati: [] },
    // [formular_manual_d216] impozit special bunuri de valoare mare: antet + liste imobile/mobile. In memorie, ca d207.
    d216: { nume: "", cif: "", domiciliuFiscal: "", nume_intocmit: "", functia_intocmit: "", d_rec: 0, nume_imputernicit: "", cif_imputernicit: "", imobile: [], mobile: [] },
    // [formular_manual_d208] transfer proprietati imobiliare (notari): antet + tranzactie/imobil + beneficiari + parti. In memorie, ca d207.
    d208: { nume: "", cif: "", domiciliu: "", nume_intocmit: "", functia_intocmit: "", dRec: 0, nr_act_notarial: "", mod_transfer: null, alt_mod_transfer: "", taxa_notar: "", imobil: { judet: "", localitate: "", codSIRUTA: "", nr_cadastral: "", tip_imobil: null, val_tranzactie_imobil: "", val_piata_imobil: "" }, beneficiari: [], parti: [] },
    // [formular_manual_d603] exceptare CASS (PF): identitate + categorie + stat asigurare + perioada. In memorie, ca d207.
    d603: { numeContrib: "", cif: "", taraContrib: "", judetContrib: "", exceptare: null, statAsigurare: "", dataInceput: "", dataSfarsit: "", dataExceptare: "", documente: "" },
    // [formular_manual_d104] distribuire venituri asociere f.PJ: declarant + asociere + profit + asociati. In memorie, ca d207.
    d104: { declarant_nume: "", declarant_prenume: "", declarant_functie: "", asociere: { cui: "", den: "", adresa: "" }, d_rec: 0, profit_pierd: "", asociati: [] },
    // [formular_manual_d114] CAM (situatii ne-D112): antet declarant + lista contracte (lucratori). In memorie, ca d207.
    d114: { cif_declarant: "", den_declarant: "", adresa_declarant: "", functia_intocmit: "", den_intocmit: "", d_rec: 0, contracte: [] },
    // [formular_manual_d110] regularizare impozit retinut la sursa: d_temei + IBAN/banca + lista obligatii. Identitatea din firma_profil. In memorie, ca d207.
    d110: { d_temei: null, d_rec: 0, iban: "", banca: "", obligatii: [] },
    // [formular_manual_d398] OSS TVA: regim + identitate + linii-supply pe stat de consum (grupate pe MS). In memorie, ca d207.
    d398: { moes_voes_imp: null, name: "", vat_id_no: "", e_int: null, currency: "EUR", d_rec: 0, linii: [] },
    // [formular_manual_d318] rambursare TVA din alt stat UE (Directiva 2008/9/CE): perioada + solicitant +
    // cont de rambursare + activitate NACE + facturi (achizitie/import) cu furnizor UE. In memorie, ca d207.
    d318: { an: "", annual: 1, luna_inceput: "", luna_sfarsit: "", refunding_country: null, cui: "", d_rec: 0,
            reference_number: "", iban: "", bic: "", owner_name: "", owner_type: null, currency: "",
            declarant: "", functie: "", sol_denumire: "", sol_strada: "", sol_email: "", sol_cod: "",
            act_nace: "", act_desc: "", facturi: [] },
  };
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  try {
    const t = await api.get("/tenants");
    S.firme = Array.isArray(t) ? t : (t.tenants || t.firme || []);
    // [deficiența 207, aceeași clasă] ecranul general pornește pe firma în lucru, dacă e în lista contului
    const inLucru = !S.tenant_id && nav && nav.firmaInLucruId ? nav.firmaInLucruId() : null;
    if (inLucru && S.firme.some((fr) => fr.id === inLucru)) S.tenant_id = inLucru;
    if (preset && S.firme.some((fr) => fr.id === preset.tenant_id)) {
      S.tenant_id = preset.tenant_id; S.tip = preset.tip || null;
      if (preset.an) S.an = preset.an;
      if (preset.luna) { S.luna = preset.luna; S.trim = Math.ceil(preset.luna / 3); }
      else if (preset.trim) { S.trim = preset.trim; S.luna = preset.trim * 3; }
      S.presetPerioada = true;
    }
    if (S.tenant_id) await incarcaTipuri(S.tenant_id);   // [G1] firma fixa -> tipurile+neaplicabile ale ei
    // [324] tipul dat e ales în listă: în grupa „Datorate” dacă perioada lui e acolo, altfel între celelalte
    if (S.presetPerioada) S.lunaDatorata = (S.datorate || []).some((d) => d.tip === S.tip && d.an === S.an && d.luna === S.luna) ? S.luna : null;
    // [lotul 13, poarta 1 — 324] perioada dată nu e între datorate, dar firma mai are ALTĂ perioadă datorată a aceluiași tip (D300 09/2026 depășită, D300 10/2026
    // datorată): tipul simplu stă în „Alte declarații”, pliate — fără ele deschise, tipul dat n-are nicio opțiune de ales și câmpul rămânea gol
    if (S.presetPerioada && S.tip && S.lunaDatorata == null) S.alteDeschise = true;
  } catch {
    corp.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca firmele.</p>`;
    return;
  }
  pas1(corp, nav);
}

// [G1] tipurile SI neaplicabile prin forma depind de FIRMA -> ruta cere tenant_id; se re-cer la fiecare schimbare de firma.
// [C103] firma schimbată de două ori în șir: numai tipurile ultimei firme alese intră în S; întoarce false pentru o cerere depășită,
// ca apelantul (refresh) să nu continue cu firma veche
const cerereTipuri = ultimaCerere();
async function incarcaTipuri(tenantId) {
  const actuala = cerereTipuri();
  try {
    const d = await api.get(`/declaratii/tipuri?tenant_id=${tenantId}`);
    if (!actuala()) return false;
    S.tipuri = d.tipuri || [];
    S.periodicitate = d.periodicitate || {};
    S.periodicitateEticheta = d.periodicitate_eticheta || {};
    S.neaplicabile = d.neaplicabile || {};
    S.datorate = d.datorate || [];   // [283] ce datorează firma, cu termenul (motorul termenelor)
    S.obligatiiD710 = d.obligatii_d710 || [];   // [9.1 A.3] codurile D710 cu denumirea oficială din nomenclator
    S.firmaDate = d.firma || {};                 // [lotul 13, 636 / 594] Date firmă pentru precompletarea formularelor manuale
    S.nomenclatoare = d.nomenclatoare || {};     // [lotul 13, 653 / 636] statele D207, monedele BNR
    S.tipuriEsuat = false;
  } catch {
    if (!actuala()) return false;
    S.tipuri = []; S.periodicitate = {}; S.neaplicabile = {}; S.datorate = []; S.firmaDate = {}; S.nomenclatoare = {}; S.tipuriEsuat = true;
  }
  return true;
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
    if (S.tipuriEsuat) return `<option value="">— nu s-au putut încărca tipurile — reîncarcă firma —</option>`;
    if (!S.tipuri.length) return `<option value="">— nicio declarație aplicabilă —</option>`;
    // [deficiența 283] întâi ce datorează firma în perioadă (din vectorul fiscal), cu termenul — alegerea fixează și perioada; restul separat
    const datorate = (S.datorate || []).filter((d) => S.tipuri.includes(d.tip) && !S.neaplicabile[d.tip]);
    const optDatorata = (d) => `<option value="${d.tip}" data-an="${d.an}" data-luna="${d.luna}"${d.tip === S.tip && d.an === S.an && d.luna === S.lunaDatorata ? " selected" : ""}>`
      + `${esc(d.tip.toUpperCase())} · ${esc(d.perioada)} · termen de depunere ${esc(dataRo(d.termen))}${d.inainte_de_preluare ? " · înainte de preluare" : ""}</option>`;
    // [lotul 10, deficiența 432] obligațiile pe perioade dinaintea preluării rămân vizibile (termenul cade după preluare), dar într-un grup
    // separat, marcate — regula de la 157 (decizia U2, 08.10); marcajul vine din motorul termenelor (`luna_preluare.inainte`)
    const deLaPreluare = datorate.filter((d) => !d.inainte_de_preluare), inainte = datorate.filter((d) => d.inainte_de_preluare);
    const grupaDatorate = (deLaPreluare.length ? `<optgroup label="Datorate de firmă (din vectorul fiscal și din operațiile înregistrate)">${deLaPreluare.map(optDatorata).join("")}</optgroup>` : "")
      + (inainte.length ? `<optgroup label="Datorate de firmă — înainte de preluare în iConta.eu">${inainte.map(optDatorata).join("")}</optgroup>` : "");
    const alte = S.tipuri.map((tp) => {
      const et = `${tp.toUpperCase()} · ${(S.periodicitateEticheta || {})[tp] || S.periodicitate[tp] || ""}`;   // [8.1 pct.6] D710: la cerere
      const neap = S.neaplicabile[tp];
      return neap
        ? `<option value="${tp}" disabled title="${esc(neap)}">${esc(neap)}</option>`
        : `<option value="${tp}" ${tp === S.tip && !S.lunaDatorata ? "selected" : ""}>${et}</option>`;
    }).join("");
    // [deficiența 301, comanda Costin 17.10.2026 7.2] „«Alte declarații» pliată, deschisă doar la cerere”: cu datorate, selectorul le arată
    // numai pe ele; restul apare după „Arată alte declarații” (sau dacă tipul ales e deja unul dintre ele, întors din pasul 2)
    const alteDeschise = !datorate.length || S.alteDeschise || (S.tip && !datorate.some((d) => d.tip === S.tip));
    return `<option value="">— alege tipul —</option>` + grupaDatorate
      + (!datorate.length ? alte : alteDeschise ? `<optgroup label="Alte declarații">${alte}</optgroup>` : "");
  }
  function butonAlte() {
    const datorate = (S.datorate || []).filter((d) => S.tipuri.includes(d.tip) && !S.neaplicabile[d.tip]);
    if (!S.tenant_id || !datorate.length) return "";
    const deschise = S.alteDeschise || (S.tip && !datorate.some((d) => d.tip === S.tip));
    return `<button type="button" class="btn-link" id="dec-alte" aria-expanded="${deschise ? "true" : "false"}">${deschise
      ? "Ascunde celelalte declarații" : "Arată alte declarații"}</button>`;
  }

  corp.innerHTML = `
    <p class="mig-intro">Pasul 1 din 3 — ${S.firmaFixa ? "alege" : "alege firma,"} tipul declarației și perioada.</p>
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
      <div id="dec-alte-zona">${butonAlte()}</div>
      <div id="dec-perioada">${randPerioada(per)}</div>
    </div>
    <div id="dec-existente"></div>
    <div class="dec-bara">
      <button class="buton-primar" id="dec-continua" data-actiune="POST /declaratii/{tip}/valideaza" disabled>Continuă →</button>
    </div>
  `;

  const selFirma = corp.querySelector("#dec-firma");  // null cand firma e fixa [decl_firma_v1]
  const selTip = corp.querySelector("#dec-tip");
  const cont = corp.querySelector("#dec-continua");
  const zonaP = corp.querySelector("#dec-perioada");

  let tipAnterior = S.tip;   // [294] perioada se propune numai la schimbarea tipului (întors din pasul 2, alegerea rămâne)
  async function refresh() {
    if (selFirma) {
      const nou = selFirma.value ? parseInt(selFirma.value) : null;
      if (nou !== S.tenant_id) {   // [G1] firma schimbata -> re-cere tipurile+neaplicabile ale ei, re-randeaza selectorul
        S.tenant_id = nou; S.tip = null;
        if (nou) { if (!(await incarcaTipuri(nou))) return; }   // [C103] o firmă aleasă între timp: refresh-ul ei desenează
        else { cerereTipuri(); S.tipuri = []; S.periodicitate = {}; S.neaplicabile = {}; }   // [C103] fără firmă: tipurile cerute înainte nu mai ajung
        S.alteDeschise = false;
        selTip.innerHTML = optiuniTip();
        declaratiiExistente(corp.querySelector("#dec-existente"), nou);
      }
    }
    legaAlte();
    S.tip = selTip.value || null;
    // [283] o obligație datorată aleasă din grupa de sus aduce și perioada ei (luna; la trimestru, luna de sfârșit)
    const o = selTip.selectedOptions[0];
    S.lunaDatorata = null;
    if (S.presetPerioada) {
      S.presetPerioada = false;   // [324] perioada declarației depășite rămâne la prima afișare; o schimbare de tip o propune din nou
    } else if (o && o.dataset.an) {
      S.an = parseInt(o.dataset.an); S.luna = parseInt(o.dataset.luna); S.trim = Math.ceil(S.luna / 3); S.lunaDatorata = S.luna;
    } else if (S.tip && S.tip !== tipAnterior) {
      // [deficiența 294, comanda Costin 16.10.2026] „Perioada implicită la orice declarație este cea mai apropiată perioadă scadentă și
      // nedepusă” (D100 propunea T4, în curs, în loc de T3, scadent pe 25.10). Ales din „Alte declarații”, tipul primește perioada lui
      // datorată (dacă e în vectorul fiscal) sau ultima perioadă încheiată (`perioadaImplicita`) — nu perioada în curs.
      const pi = perioadaImplicita(S.tip);
      S.an = pi.an; S.luna = pi.luna; S.trim = Math.ceil(pi.luna / 3);
    }
    tipAnterior = S.tip;
    const p = S.tip ? S.periodicitate[S.tip] : null;
    zonaP.innerHTML = randPerioada(p);
    legPerioada(zonaP);
    cont.disabled = !(S.tenant_id && S.tip);
    const _za = corp.querySelector("#dec-ajutor");  // [ajutor] "?" urmareste tipul ales
    if (_za) _za.innerHTML = (S.tip && _DECL_AJUTOR[S.tip]) ? semnAjutor(_DECL_AJUTOR[S.tip]) : "";
  }
  function legaAlte() {
    const z = corp.querySelector("#dec-alte-zona");
    if (!z) return;
    z.innerHTML = butonAlte();
    const b = z.querySelector("#dec-alte");
    if (b) b.addEventListener("click", () => {
      S.alteDeschise = b.getAttribute("aria-expanded") !== "true";
      const ales = selTip.value;
      selTip.innerHTML = optiuniTip();
      if (ales) selTip.value = ales;
      legaAlte();
      // [deficiența 325, 18.10.2026] focusul rămâne pe buton, NU pe listă: un focus pe lista derulantă îi deschide lista (pe telefon, și cu
      // tastatura) fără clicul omului. Regula: nicio listă / fereastră / formular nu se deschide singură (garda din plasa e2e).
      const b2 = z.querySelector("#dec-alte");
      if (b2) focusFaraSalt(b2);
    });
  }
  if (S.tenant_id) declaratiiExistente(corp.querySelector("#dec-existente"), S.tenant_id);
  if (selFirma) selFirma.addEventListener("change", refresh);
  selTip.addEventListener("change", refresh);
  legPerioada(zonaP);
  // [deficiența 485] pasul 2 e un PAS al ferestrei (`nav.mergi`), nu o redesenare pe loc: săgeata înapoi a navigatorului scoate întâi pasul
  // de pe traseu și întoarce la alegerea declarației; până azi, cu fereastra deschisă din fereastra firmei, săgeata închidea Declarațiile
  cont.addEventListener("click", () => nav.mergi("Declarații", (c) => pas2(c, nav)));
  refresh();
}

// [deficiența 299, comanda Costin 17.10.2026 7.2] „Ana nu are nicio listă a declarațiilor existente (cardul Declarații deschide direct
// pregătirea)”: sub alegere, declarațiile firmei aflate în coadă (la validare / de depus), fiecare cu drumul spre ea — înainte de a genera
// una a doua pe aceeași perioadă. Aceeași listă ca a cozii (`GET /coada`, numai firmele alocate asistentului).
const cerereExistente = ultimaCerere();   // [C103] firma schimbată în șir: numai coada ultimei firme alese apare sub alegere
async function declaratiiExistente(zona, tenantId) {
  const actuala = cerereExistente();
  if (!zona) return;
  zona.innerHTML = "";
  if (!tenantId) return;
  let coada = [];
  try { const r = await api.get("/coada");
        if (!actuala()) return;
        coada = (r.coada || []).filter((c) => c.tenant_id === tenantId && c.fel !== "nota"
                                         && (c.stare === "la_senior" || c.stare === "aprobata")); }
  catch { if (!actuala()) return; }   // refuzul cererii curente: coada rămâne goală -> ieșirea de mai jos
  if (!zona.isConnected || !coada.length) return;
  const stare = (c) => c.depasita ? "depășită, de generat din nou" : c.stare === "aprobata" ? "validată, de depus" : "la validare";
  zona.innerHTML = `<div class="caseta-info dec-existente"><div class="ci-mesaj"><b>Declarațiile firmei aflate deja în coadă</b>
      <ul>${coada.map((c, i) => `<li>${esc((c.tip || "").toUpperCase())} · ${esc(c.p_luna ? dataRo(new Date(c.p_an, c.p_luna - 1, 1), "luna_an_numeric")
        : c.p_trim ? `T${c.p_trim}/${c.p_an}` : `anul ${c.p_an}`)} · ${esc(stare(c))} · pregătită de ${esc(c.creat_de_nume || "—")}
        <button type="button" class="btn-link" data-coada="${i}">Deschide</button></li>`).join("")}</ul></div></div>`;
  zona.querySelectorAll("[data-coada]").forEach((b) => b.addEventListener("click", () => deschideInCoada(coada[Number(b.dataset.coada)].id)));
}

// [deficiența 294] Perioada propusă pentru un tip: cea mai apropiată perioadă scadentă și nedepusă din vectorul fiscal (`S.datorate`, sortată
// după termen — motorul termenelor, aceeași listă ca la 283); altfel ultima perioadă ÎNCHEIATĂ după periodicitatea tipului (luna trecută,
// trimestrul trecut, anul trecut) — perioada în curs nu e scadentă. {an, luna}: la trimestru, luna de sfârșit.
export function perioadaImplicita(tip, azi = new Date()) {
  const d = (S.datorate || []).find((x) => x.tip === tip);
  if (d) return { an: d.an, luna: d.luna };
  const per = S.periodicitate[tip];
  const an = azi.getFullYear(), l = azi.getMonth() + 1;
  if (per === "anual") return { an: an - 1, luna: 12 };
  if (per === "trimestrial") {
    const t = Math.ceil(l / 3) - 1;
    return t === 0 ? { an: an - 1, luna: 12 } : { an, luna: t * 3 };
  }
  return l === 1 ? { an: an - 1, luna: 12 } : { an, luna: l - 1 };
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
        <select id="dec-trim" class="camp-input" data-butoane="">
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

// [comanda Costin 07.10.2026, C2] UN SINGUR constructor al corpului: generarea (pasul 2) și coada (pasul 3) trimit ACELAȘI corp.
// Până azi pasul 3 își construia corpul separat, fără formularul manual și fără obligațiile D710 -> orice declarație cu formular
// (D311, D307, … D710) era refuzată la „Trimite în coadă” („nu are ce genera”), deși trecuse de validator la pasul 2.
function corpGenerare() {
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
  if (S.tip === "d205" && (S.d205.beneficiari || []).length) body.manual = _d205Manual();   // [lotul 10, decizia B] numai dacă s-au scris
  if (S.tip === "d212") body.manual = _d212Manual();              // [formular_manual_d212] identitatea PF din memorie
  if (S.tip === "d230") body.manual = _d230Manual();              // [formular_manual_d230] identitate PF + entitate ONG
  if (S.tip === "d204") body.manual = _d204Manual();              // [formular_manual_d204] asociere + reprezentant + activitate + asociati
  if (S.tip === "d216") body.manual = _d216Manual();              // [formular_manual_d216] antet + liste bunuri imobile/mobile
  if (S.tip === "d208") body.manual = _d208Manual();              // [formular_manual_d208] notar + tranzactie/imobil + beneficiari + parti
  if (S.tip === "d603") body.manual = _d603Manual();              // [formular_manual_d603] exceptare CASS (identitate + categorie + stat + perioada)
  if (S.tip === "d104") body.manual = _d104Manual();              // [formular_manual_d104] declarant + asociere + profit + asociati
  if (S.tip === "d114") body.manual = _d114Manual();              // [formular_manual_d114] declarant + contracte (CAM)
  if (S.tip === "d110") body.manual = _d110Manual();              // [formular_manual_d110] d_temei + IBAN/banca + obligatii
  if (S.tip === "d398") body.manual = _d398Manual();              // [formular_manual_d398] OSS: regim + linii pe stat de consum
  if (S.tip === "d318") body.manual = _d318Manual();              // [formular_manual_d318] rambursare TVA alt stat UE: perioada + solicitant + facturi
  // [lotul 12, C19] rectificativa D394 cerută de contabil după ce a văzut diferențele: confirmarea poartă amprenta conținutului văzut, numai
  // pentru aceeași declarație și perioadă (altă perioadă / alt tip -> nicio confirmare; serverul o cere din nou dacă datele s-au schimbat)
  if (S.rectConfirmata && S.rectConfirmata.cheie === _cheieRect()) body.date_extra = { rectificativa_confirmata: S.rectConfirmata.amprenta };
  return body;
}

function _cheieRect() { return [S.tenant_id, S.tip, S.an, S.periodicitate[S.tip] === "trimestrial" ? "T" + S.trim : S.luna].join("|"); }

// [lotul 13, deficiențele 651, 659, 594, 637] Declarațiile făcute dintr-un FORMULAR (beneficiari, facturi, sume scrise de contabil): la
// intrarea în pasul 2 nu se cere serverului nimic — formularul e gol, iar refuzul „D207 nu are ce genera” apărea roșu, ca o eroare, deși e
// starea normală a unei declarații încă necompletate (651, clasa 89); la D311 / D398 / D318 trei erori deodată, înainte de orice acțiune
// (659, 594, 637). Pasul 2 arată formularul, cu o notă neutră; declarația se generează și se validează la „Generează DXXX”
// (`regenereaza`). Fiecare tip de aici are formularul lui; D205 nu e aici (se generează din note, formularul e numai pentru completare).
const _FORMULARE = { d710: randeazaFormularD710, d311: randeazaFormularD311, d307: randeazaFormularD307, d107: randeazaFormularD107,
  d177: randeazaFormularD177, d207: randeazaFormularD207, d212: randeazaFormularD212, d230: randeazaFormularD230, d204: randeazaFormularD204,
  d216: randeazaFormularD216, d208: randeazaFormularD208, d603: randeazaFormularD603, d104: randeazaFormularD104, d114: randeazaFormularD114,
  d110: randeazaFormularD110, d398: randeazaFormularD398, d318: randeazaFormularD318 };
// panourile declarațiilor generate din evidență, cu rânduri adăugate de mână (păstrate în bază) — zona și desenarea lor
const _PANOURI = { d390: "dec-d390-clasif", d301: "dec-d301-op", d300: "dec-d300-manual", d205: "dec-d205-form" };

function _zonaFormular() {
  if (_FORMULARE[S.tip]) return `<div id="dec-${S.tip}-form"></div>`;
  return _PANOURI[S.tip] ? `<div id="${_PANOURI[S.tip]}"></div>` : "";
}
function _randeazaFormularul(corp, nav, deschisD205) {
  if (_FORMULARE[S.tip]) { _FORMULARE[S.tip](corp, nav); return; }
  if (S.tip === "d301") randeazaOperatiuniD301(corp, nav);
  if (S.tip === "d300") randeazaManualD300(corp, nav);
  if (S.tip === "d205") randeazaFormularD205(corp, nav, deschisD205);
}
// eticheta butonului de generare din formular: „Generează” până la prima generare, apoi „Regenerează”
function _etRegen() { return (S.rezultat ? "Regenerează " : "Generează ") + String(S.tip || "").toUpperCase(); }
// generarea cerută din formular sau din panou (butonul „Generează / Regenerează DXXX”, „Generează declarația rectificativă”)
function regenereaza(corp, nav) { S.cerutGenerare = true; pas2(corp, nav); }

// [lotul 13, 652 / 637] refuzul formularului care nu ține de un câmp (lista goală: „Adaugă cel puțin un beneficiar”) stă lângă butonul de
// generare, nu pe câmpul „Nume” completat corect; o singură dată (zona e în rândul butonului, deci caseta „NU s-a salvat” n-o repetă)
function _refuzLangaRegen(zona, mesaj) {
  const b = zona.querySelector('button[id$="-regen"]');
  if (!b) return;
  let z = b.parentElement.querySelector(":scope > .dec-regen-msg");
  if (!z) { z = document.createElement("span"); z.className = "dec-regen-msg"; z.setAttribute("role", "alert"); b.parentElement.appendChild(z); }
  arataMesaj(z, mesaj, "eroare");
}
function _eroareFormular(zona, id, mesaj) { return id ? eroareCamp(zona, id, mesaj) : _refuzLangaRegen(zona, mesaj); }

// [lotul 13, 652] câmpurile rândului de adăugat (beneficiar, factură, livrare …) completate, dar neadăugate cu „+ adaugă”: butoanele „+”
// ale lor. Completat = un câmp de text cu ceva scris sau o listă cu o alegere făcută (o listă care pornește aleasă nu se socotește).
function _completateNeadaugate(corp) {
  const out = [];
  corp.querySelectorAll('[id^="dec-d"][id$="-form"] button[id*="-add"], #dec-d300-manual button[id$="-add"], #dec-d301-op button[id$="-add"]').forEach((b) => {
    const rand = b.closest("[data-rand-adaugare]") || b.closest(".dec-man-form") || b.parentElement;
    const campuri = [...rand.querySelectorAll("input, select, textarea")].filter((el) => !el.disabled && !el.readOnly
      && !["checkbox", "radio", "hidden"].includes(el.type) && !el.hasAttribute("data-cautare"));
    const completat = campuri.some((el) => el.tagName === "SELECT"
      ? (el.value !== "" && !!el.querySelector('option[value=""]'))
      : String(el.value || "").trim() !== "");
    if (completat) out.push(b);
  });
  return out;
}

// [lotul 13, 657 / 654 / 652] o singură legare pe fereastra pasului 2 (corpul rămâne același la „Regenerează”):
//  - 652: „Generează / Regenerează” adaugă întâi rândurile completate și neadăugate (cu verificările butonului „+ adaugă”); un rând cu
//    greșeli oprește generarea, cu eroarea lângă câmpul lui;
//  - 657 / 654: orice modificare în formular sau în panoul declarației (tastare, alegere, ștergerea unui rând) scoate refuzul de generare
//    vechi și, dacă declarația fusese validată, anulează rezultatul: caseta verde și „Trimite în coadă” nu mai stau active pentru o
//    declarație care nu mai e cea de pe ecran.
function _legaModificari(corp) {
  if (corp.__decModificari) return;
  corp.__decModificari = true;
  corp.addEventListener("click", (ev) => {
    const b = ev.target instanceof Element ? ev.target.closest('button[id$="-regen"]') : null;
    if (!b || !corp.contains(b)) return;
    // numai formularele ținute în ecran (rândul se adaugă pe loc); panourile D300 / D301 / D390 scriu în bază, deci acolo „+ adaugă”
    // rămâne al omului. Fiecare buton o singură dată: un rând care nu se golește după adăugare nu se adaugă de două ori.
    const apasate = new Set();
    for (let i = 0; i < 10; i++) {
      const urm = _completateNeadaugate(corp).find((x) => !apasate.has(x.id) && x.closest('[id^="dec-d"][id$="-form"]'));
      if (!urm) break;
      apasate.add(urm.id);
      urm.click();
      if (corp.querySelector('[aria-invalid="true"]')) { ev.stopImmediatePropagation(); ev.preventDefault(); return; }
    }
  }, true);
  const zone = () => [...corp.querySelectorAll('[id^="dec-d"][id$="-form"], #dec-d390-clasif, #dec-d301-op, #dec-d300-manual')];
  const laModificare = (ev) => {
    if (!(ev.target instanceof Element) || !zone().some((z) => z.contains(ev.target) || !ev.target.isConnected)) return;
    if (ev.type === "click" && !ev.target.closest("button")) return;
    if (ev.type === "click" && ev.target.closest('button[id$="-regen"]')) return;
    setTimeout(() => valabilitateRezultat(corp), 0);
  };
  ["input", "change", "click"].forEach((t) => corp.addEventListener(t, laModificare));
}

// rezultatul de pe ecran mai e al declarației din formular? (corpul cererii validate, rândurile din panou, rânduri neadăugate)
function valabilitateRezultat(corp) {
  const refuz = corp.querySelector("#dec-refuz");
  if (refuz) refuz.remove();   // 654: refuzul generării de dinainte nu mai e despre ce e pe ecran
  const rez = corp.querySelector("#dec-rezultat");
  if (!rez || !S.rezultat) return;
  const modificat = JSON.stringify(corpGenerare()) !== S.corpValidat || !!S.panouModificat || _completateNeadaugate(corp).length > 0;
  rez.hidden = modificat;
  const inv = corp.querySelector("#dec-invalidat");
  if (inv) inv.innerHTML = modificat ? `<div class="caseta-atentie" role="status"><div class="ca-mesaj">Ai modificat declarația după ce a fost `
    + `generată și validată, deci rezultatul nu mai e valabil. Apasă „${esc(_etRegen())}” ca s-o generezi și s-o validezi din nou.</div></div>` : "";
  corp.querySelectorAll("#dec-trimite, #dec-gol-da").forEach((b) => {
    if (b.dataset.activInainte === undefined) b.dataset.activInainte = b.disabled ? "0" : "1";
    b.disabled = modificat || b.dataset.activInainte === "0";
    if (modificat) b.setAttribute("aria-describedby", "dec-invalidat");
    else if (b.dataset.activInainte === "1") b.removeAttribute("aria-describedby");
  });
}
// panourile cu rânduri păstrate în bază (D300 / D301 / D390): o adăugare sau o ștergere reușită schimbă declarația
function _panouModificat(corp) { S.panouModificat = true; valabilitateRezultat(corp); }

// ---------- PAS 2: genereaza + verifica ----------
async function pas2(corp, nav) {
  S.pas = 2;
  const cerut = S.cerutGenerare;
  S.cerutGenerare = false;
  _legaModificari(corp);
  if (_FORMULARE[S.tip] && !cerut) {   // [lotul 13, 651 / 659] formularul întâi, fără nicio cerere la server
    S.rezultat = null;
    const f0 = corp.closest(".fereastra"); if (f0) f0.classList.add("fer-larg");
    const T = esc(S.tip.toUpperCase());
    corp.innerHTML = `
    <div class="rezumat-fix"><p class="mig-intro">Pasul 2 din 3 — completează <b>${T}</b> · ${etPerioada()}</p></div>
    <div class="caseta-info" id="dec-completeaza" role="note"><div class="ci-mesaj">Completează formularul de mai jos, apoi apasă „Generează ${T}”: declarația se generează și se verifică cu validatorul ANAF abia atunci.</div></div>
    ${_zonaFormular()}`;
    _randeazaFormularul(corp, nav, true);
    return;
  }
  corp.innerHTML = `<p class="ecran-nota">Se generează declarația…</p>`;
  const body = corpGenerare();

  try {
    S.rezultat = await api.post(`/declaratii/${S.tip}/valideaza`, body);
  } catch (e) {
    S.rezultat = null;
    // [G2] surfaceaza eroarea SPECIFICA (422 cu temei / gri cu limita), nu un mesaj generic - exact unde
    // contabilul are nevoie de ea. Aliniat cu pas3. api.js arunca {cod, mesaj}.
    // [chicken-and-egg 16.08] Declaratiile cu panou editabil (d301/d390/d300) randeaza panoul CHIAR si pe
    // eroare de generare (ex. refuz zero-base): altfel o firma fara operatiuni nu poate ajunge la ecranul
    // unde le adauga. Eroarea explica DE CE; panoul lasa contabilul sa introduca + Regenereaza.
    corp.innerHTML = `
      <p class="mig-intro">Pasul 2 din 3 — generare</p>
      ${S.tip === "d390" ? '<div id="dec-d390-clasif"></div>' : ""}
      ${S.tip !== "d390" ? _zonaFormular() : ""}
      <div class="dec-eroare" id="dec-refuz">${esc((e && e.mesaj) || "Nu s-a putut genera declarația. Verifică datele firmei pentru perioada aleasă.")}</div>
      `;
    if (S.tip === "d390") randeazaClasificareD390(corp, nav);
    // [lotul 10, deficiența 431] „mesajul de refuz trimite la ce lipsește”: refuzul generatorului (`RefuzGenerare`) poartă notele de
    // deschis (nota de dividende în ciornă -> Registrul jurnal, în luna ei) și / sau ecranul (Date firmă → Asociați)
    const _det = (e && e.detaliu && typeof e.detaliu === "object") ? e.detaliu : {};
    if (_det.cod === "RECTIFICATIVA_DE_CONFIRMAT" || _det.cod === "RECTIFICATIVA_FARA_DIFERENTE") { randeazaDiferenteRectificativa(corp, nav, _det); return; }
    const _zEr = corp.querySelector(".dec-eroare");
    if (_zEr && (_det.note || []).length) legaturiNote(_zEr, S.tenant_id, _det.note);
    if (_zEr && _det.ecran) butonSpreEcran(_zEr, _det.ecran, nav, S.tenant_id, { clasa: "buton-secundar", inapoiLa: "declarație", camp: _det.camp_ecran || null });
    _randeazaFormularul(corp, nav, true);
    return;
  }

  const f = corp.closest(".fereastra"); if (f) f.classList.add("fer-larg");
  const avert = S.rezultat.avertismente || [];
  const constat = S.rezultat.note_rezultat || [];   // fapte NEUTRE despre rezultat (sectiune informativa separata, nu avertisment)
  // [lotul 10, deficiența 436, comanda Costin 10.2 pct.6] „când declarația știe că are cifra greșită din note nevalidate, depunerea se
  // blochează până la validare, cu motivul lângă buton, la toate declarațiile.” Serverul spune refuzul (`uc_declaratii.blocaj_depunere`,
  // același ca la intrarea în coadă): „Trimite în coadă” rămâne vizibil, dar inactiv, cu motivul imediat sub el, în bara fixă
  const _blocaj = S.rezultat.blocaj_depunere || null;
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
             <div class="dec-avert-cap">Nu s-a putut rula validarea cu DUKIntegrator (validatorul ANAF, local)</div>
             <ul><li>${esc(S.rezultat.temei || "Validatorul nu a rulat.")}</li>
                 <li>${esc(S.rezultat.limita || "")}</li></ul>
           </div>`);

  corp.innerHTML = `
    <div class="rezumat-fix"><p class="mig-intro">Pasul 2 din 3 — verifică <b>${S.tip.toUpperCase()}</b> · ${etPerioada()}</p></div>   <!-- [lotul 10, 421 / 424, DS cap.9 v2.97 pct.5] declarația și perioada rămân sus -->
    ${S.rezultat.rectificativa ? `<div class="caseta-info" id="dec-rectificativa" role="status"><div class="ci-mesaj">${esc(String(S.rezultat.rectificativa))}</div></div>` : ""}   <!-- [lotul 11, C77] declarația peste una deja depusă pe perioadă; DS cap.5 v2.12 .caseta-info -->
    ${S.tip === "d390" ? '<div id="dec-d390-clasif"></div>' : ""}
    ${S.tip !== "d390" ? _zonaFormular() : ""}
    <div id="dec-rezultat">
    ${blocANAF}
    ${constat.length ? `<div class="caseta-info">
        <div class="ci-mesaj" style="font-weight:600;margin-bottom:6px">Constatări (${constat.length})</div>
        <ul class="ci-mesaj" style="margin:0;padding-left:18px">${constat.map((c)=>`<li style="margin:3px 0">${esc(typeof c==="string"?c:(c.mesaj||"constatare fără detalii"))}</li>`).join("")}</ul>
      </div>` : ""}
    ${(S.rezultat.sinteza || []).length ? `<div class="caseta-info">
        <div class="ci-mesaj" style="font-weight:600;margin-bottom:6px">Rezumat</div>
        <ul class="ci-mesaj" style="margin:0;padding-left:18px">${S.rezultat.sinteza.map((x) => `<li style="margin:3px 0">${esc(String(x))}</li>`).join("")}</ul>
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
    </div>
    <div class="bara-fixa">${_blocaj ? `<div class="dec-bara">
      <button class="buton-primar" id="dec-trimite" data-actiune="POST /coada" disabled aria-describedby="dec-blocaj">Trimite în coadă →</button>
    </div>` : _esteGoala() ? `<div class="caseta-poarta">
        <div class="cp-mesaj">Declarația nu conține nicio operațiune. Dacă firma chiar n-a avut activitate în perioadă, se depune așa. Dacă a avut, întoarce-te și verifică dacă documentele perioadei sunt introduse și contabilizate.</div>
        <div class="cp-butoane">
          <button class="buton-primar" id="dec-gol-da">Da, fără activitate — trimite</button>
          <button class="buton-secundar" id="dec-gol-nu">Nu, mă întorc să verific</button>
        </div>
      </div>` : `<div class="dec-bara">
      <button class="buton-primar" id="dec-trimite" data-actiune="POST /coada">Trimite în coadă →</button>
    </div>`}
    <div id="dec-invalidat"></div>
    <div id="dec-coada-mesaj">${_blocaj ? `<div class="caseta-atentie" id="dec-blocaj" role="status"><div class="ca-mesaj">${esc(_mesajLangaNote(_blocaj))}</div></div>` : ""}</div></div>
    <p class="ecran-nota">${esc(S.rezultat.limita || "")}</p>
  `;
  // [lotul 10, 436] notele care opresc depunerea: fiecare cu drumul ei spre Registrul jurnal, în luna notei (ca refuzul porții TVA, 284)
  if (_blocaj && (_blocaj.note || []).length) legaturiNote(corp.querySelector("#dec-blocaj .ca-mesaj"), S.tenant_id, _blocaj.note);
  const _bt = corp.querySelector("#dec-trimite");
  if (_bt) { _bt.addEventListener("click", () => pas3(corp, nav)); etichetaTrimitere(_bt); }   // [313]
  const _bDa = corp.querySelector("#dec-gol-da");
  if (_bDa) _bDa.addEventListener("click", () => pas3(corp, nav));
  const _bNu = corp.querySelector("#dec-gol-nu");
  if (_bNu) _bNu.addEventListener("click", () => nav.inapoiPas());   // [485] înapoi la alegerea declarației, pe traseu
  if (S.tip === "d390") randeazaClasificareD390(corp, nav);
  _randeazaFormularul(corp, nav, false);
  // [lotul 13, 657] declarația validată = exact corpul de acum; orice abatere anulează rezultatul (`valabilitateRezultat`)
  S.corpValidat = JSON.stringify(body);
  S.panouModificat = false;
}

// [lotul 12, C19, comanda Costin 12.3 pct.6, verbatim în DECIZII] „rectificativa D394 pentru o perioadă deja depusă se generează doar la
// cererea contabilului, cu diferențele față de cea depusă arătate înainte; niciodată automat.” Serverul (`rectificativa.poarta_d394`) nu
// generează peste o depunere fără confirmare și trimite diferențele (secțiune / rând / câmp: depus → nou). Ecranul le arată; „Generează
// rectificativa” trimite confirmarea pentru exact conținutul văzut. Fără diferențe: o spune, fără buton. Propozițiile le scrie ecranul
// (DS cap.25.5); serverul dă faptele. Fereastră cu tabel (DS cap.9): rezumatul sus (`.rezumat-fix`, fără casete — v2.102, „Rezumatul nu
// mănâncă tabelul”: caseta stă sub el), acțiunea jos (`.bara-fixa`).
function randeazaDiferenteRectificativa(corp, nav, d) {
  const dif = d.diferente || [];
  const fara = d.cod === "RECTIFICATIVA_FARA_DIFERENTE";
  const per = etPerioada();
  // fraza serverului (`mesaj`) stă pe ecran întocmai — e și cea din coadă / notificare; ecranul adaugă numai ce ține de tabel
  const ce = esc(d.mesaj || "") + (fara ? "" : " " + (d.xml_depus_pastrat
    ? `Diferențele față de declarația depusă: ${esc(cate(dif.length, "rând", "rânduri"))}.`
    : "XML-ul declarației depuse nu e păstrat în iConta.eu, deci diferențele nu se pot calcula: mai jos e tot ce ar conține declarația rectificativă. Compară-l cu declarația depusă (recipisa din SPV) înainte s-o generezi."));
  corp.innerHTML = `
    <div class="rezumat-fix"><p class="mig-intro">Pasul 2 din 3 — <b>${esc(S.tip.toUpperCase())}</b> · ${esc(per)} e deja depusă</p></div>
    <div class="caseta-info" id="dec-rect-depusa" role="status"><div class="ci-mesaj">${ce}</div></div>   <!-- DS cap.9 v2.102: caseta sub rezumat, nu în el -->
    ${dif.length ? `<table class="fd-tabel" id="dec-rect-diferente">
        <thead><tr><th>Secțiune</th><th>Rând</th><th>Câmp</th><th>În declarația depusă</th><th>În rectificativă</th></tr></thead>
        <tbody>${dif.map((r) => `<tr><td>${esc(r.sectiune)}</td><td>${esc(r.rand)}</td><td>${esc(r.camp)}</td><td>${esc(String(r.depus))}</td><td>${esc(String(r.nou))}</td></tr>`).join("")}</tbody>
      </table>` : ""}
    <div class="bara-fixa"><div class="dec-bara">
      <button class="buton-secundar" id="dec-rect-inapoi" data-fara-actiune="navigare: înapoi la alegerea declarației">← Înapoi la alegerea declarației</button>
      ${fara ? "" : `<button class="buton-primar" id="dec-rect-genereaza" data-actiune="POST /declaratii/{tip}/valideaza">Generează declarația rectificativă →</button>`}
    </div></div>
  `;
  corp.querySelector("#dec-rect-inapoi").addEventListener("click", () => nav.inapoiPas());   // [485] înapoi la alegerea declarației, pe traseu
  const bG = corp.querySelector("#dec-rect-genereaza");
  if (bG) bG.addEventListener("click", () => { S.rectConfirmata = { cheie: _cheieRect(), amprenta: d.amprenta }; regenereaza(corp, nav); });
}

// [lotul 11, deficiența 436 afișare] „paragraful repetă notele pe care le arată butoanele”: lângă butoanele „Deschide nota …”
// (`legaturiNote`) refuzul spune câte note și ce e de făcut, nu le mai enumeră — serverul dă textul fără listă (`mesaj_langa_note`,
// `coada_api.blocaj_note_nevalidate`); textul cu lista (`mesaj`) rămâne pentru locurile fără butoane („De depus”, API-ul).
function _mesajLangaNote(refuz) {
  return (refuz.note || []).length ? refuz.mesaj_langa_note : (refuz.mesaj || "");
}

// [F125] panou clasificare D390: reclasifica operatiunile auto (servicii/triangulatie) + adauga
// linii manuale. Modifica evidenta persistata; "Regenereaza" reface pas2 cu noile clasificari.
const _D390_TIP_DIR = {
  emisa: [["L", "Livrare bunuri (L)"], ["T", "Triangulație (T)"], ["P", "Servicii prestate (P)"], ["R", "Agricol special (R)"]],
  primita: [["A", "Achiziție bunuri (A)"], ["S", "Servicii primite (S)"]],
};
const cerereD390 = ultimaCerere();   // [C103] două ștergeri / adăugări în șir: numai re-citirea ultimei ajunge în panou
async function randeazaClasificareD390(corp, nav) {
  const actuala = cerereD390();
  const zona = corp.querySelector("#dec-d390-clasif");
  if (!zona) return;
  let d;
  try { d = await api.get(`/tenants/${S.tenant_id}/d390-clasificare?an=${S.an}&luna=${S.luna}`); if (!actuala()) return; }
  catch (e) { if (!actuala()) return; zona.innerHTML = `<p class="ecran-nota">Nu s-a putut încărca clasificarea intracomunitară${e && e.mesaj ? " (" + esc(e.mesaj) + ")" : ""}. Reîncarcă declarația.</p>`; return; }
  const auto = d.auto || [], manual = d.manual || [];
  const optSel = (dir, cur) => (_D390_TIP_DIR[dir] || []).map(([v, l]) => `<option value="${v}" ${v === cur ? "selected" : ""}>${l}</option>`).join("");
  zona.innerHTML = `<details class="dec-xml" open><summary>Clasificare intracomunitară (servicii / triangulație)</summary>
    ${auto.length ? `<div class="camp-eticheta" style="margin:6px 0">Operațiuni din facturi — verifică tipul:</div>
      ${auto.map((o) => `<div class="dec-recl-rand">
        <span class="dec-recl-desc">${o.directie === "emisa" ? "↗ emisă" : "↘ primită"} · ${esc(o.tara)}${esc(o.cod)} ${esc(o.den || "")}</span>
        <span class="dec-recl-suma">${bani(o.baza)} lei</span>
        <select class="camp-input dec-recl" data-actiune-camp="PUT /tenants/{tenant_id}/d390-clasificare/reclasificare" aria-label="Tipul operațiunii" data-dir="${o.directie}" data-tara="${esc(o.tara)}" data-cod="${esc(o.cod)}">${optSel(o.directie, o.tip_curent)}</select>
      </div>`).join("")}` : `<div class="camp-eticheta dec-clasif-gol" style="margin:6px 0">Nicio operațiune din facturi în perioadă.</div>`}
    <div class="camp-eticheta" style="margin:10px 0 4px">Linii adăugate manual (fără factură în sistem):</div>
    ${manual.length ? manual.map((m) => `<div class="dec-man-rand">
        <span class="dec-recl-desc">${esc(m.tip)} · ${esc(m.tara)}${esc(m.cod)} ${esc(m.den || "")}</span>
        <span class="dec-recl-suma">${bani(m.baza)} lei</span>
        <button class="btn-link dec-man-del" data-actiune="DELETE /tenants/{tenant_id}/d390-clasificare/manual/{mid}" data-id="${m.id}">șterge</button></div>`).join("") : `<div class="camp-eticheta dec-clasif-gol">—</div>`}
    <div class="dec-man-form" style="margin-top:8px">
      <label class="camp" style="width:160px"><span class="camp-eticheta">Tip</span><select id="man-tip" class="camp-input" data-butoane="">${ALEGE}<option value="A">Achiziție bunuri IC fără cod furnizor — nota 1 (A)</option><option value="P">Servicii prestate (P)</option><option value="S">Servicii primite (S)</option><option value="T">Triangulație (T)</option><option value="R">Agricol special (R)</option></select></label>
      <label class="camp" style="width:100px"><span class="camp-eticheta">Țară</span><input id="man-tara" class="camp-input" placeholder="ex. DE"></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">Cod partener</span><input id="man-cod" class="camp-input" placeholder="fără prefix țară"></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">Denumire</span><input id="man-den" class="camp-input"></label>
      <label class="camp" style="width:110px"><span class="camp-eticheta">Bază (lei)</span><input id="man-baza" type="number" class="camp-input"></label>
      <button class="buton-secundar" id="man-add" data-actiune="POST /tenants/{tenant_id}/d390-clasificare/manual">+ adaugă</button>
    </div>
    <p class="ecran-nota" style="margin-top:4px">Tip <b>A</b> (nota 1): achiziție intracomunitară de bunuri de la un furnizor UE care nu a comunicat un cod valid de TVA — completează Țara (statul membru din care s-au transportat bunurile) și lasă Codul gol.</p>
    <div id="dec-clasif-msg"></div>
    <p style="margin-top:8px"><button class="buton-primar" id="dec-regen">Regenerează D390</button>
      <span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>
  </details>`;
  zona.querySelectorAll(".dec-recl").forEach((sel) => sel.addEventListener("change", async () => {
    try { await api.put(`/tenants/${S.tenant_id}/d390-clasificare/reclasificare`, { an: S.an, luna: S.luna, directie: sel.dataset.dir, tara: sel.dataset.tara, cod: sel.dataset.cod, tip: sel.value }); _panouModificat(corp); }   // [lotul 13, 657] declarația validată nu mai e cea de pe ecran
    catch (e) { arataRefuzul(zona, e, zona.querySelector("#dec-clasif-msg")); }
  }));
  zona.querySelectorAll(".dec-man-del").forEach((b) => b.addEventListener("click", async () => {
    try { await api.del(`/tenants/${S.tenant_id}/d390-clasificare/manual/${b.dataset.id}?an=${S.an}&luna=${S.luna}`); _panouModificat(corp); randeazaClasificareD390(corp, nav); }
    catch (e) { arataRefuzul(zona, e, zona.querySelector("#dec-clasif-msg")); }
  }));
  zona.querySelector("#man-add").addEventListener("click", async () => {
    const b = { an: S.an, luna: S.luna, tip: zona.querySelector("#man-tip").value,
      tara: zona.querySelector("#man-tara").value.trim().toUpperCase(), cod: zona.querySelector("#man-cod").value.trim(),
      den: zona.querySelector("#man-den").value.trim(), baza: parseFloat(zona.querySelector("#man-baza").value) || 0 };
    curataEroriCamp(zona);  // [G10] eroare langa camp
    if (cereAlegerile(zona, ["#man-tip"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    try { await api.post(`/tenants/${S.tenant_id}/d390-clasificare/manual`, b); _panouModificat(corp); randeazaClasificareD390(corp, nav); }
    catch (e) {
      curataEroriCamp(zona);
      arataRefuzul(zona, e, zona.querySelector("#dec-clasif-msg"), { campuri: _campuriCu(e, "man-") });
    }
  });
  zona.querySelector("#dec-regen").addEventListener("click", () => regenereaza(corp, nav));
}

// [D301 27.07.2026] panou introducere operatiuni D301 (decont special TVA), afisat in pas2 cand
// tip==="d301". Geaman cu randeazaClasificareD390: grila lunii + adaugare + stergere + regenerare.
// FISCAL: baza = val_valuta x curs (AFISATA, nestocata - generatorul o recalculeaza). TVA = baza x
// cota; cota din selector (standard period-aware din backend, nu literal), TVA calculat SE STOCHEAZA
// (d301.calcul_d301 il citeste din DB, nu-l recalculeaza). Etichetele celor 5 tipuri + valutele +
// cotele vin din backend (sursa unica, EXACT ca formularul oficial) - nu le rescriu in JS.
const cerereD301 = ultimaCerere();   // [C103] două ștergeri / adăugări în șir: numai re-citirea ultimei ajunge în grilă
async function randeazaOperatiuniD301(corp, nav) {
  const actuala = cerereD301();
  const zona = corp.querySelector("#dec-d301-op");
  if (!zona) return;
  let d;
  try { d = await api.get(`/tenants/${S.tenant_id}/d301-operatiuni?an=${S.an}&luna=${S.luna}`); if (!actuala()) return; }
  catch (e) { if (!actuala()) return; zona.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca operațiunile D301${e && e.mesaj ? " (" + esc(e.mesaj) + ")" : ""}. Reîncarcă declarația.</p>`; return; }
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
        <span class="dec-recl-desc" title="${esc(o.eticheta)}">Tip ${o.tip} · ${esc(o.nr_doc)}${o.data_doc ? " · " + esc(dataRo(o.data_doc)) : ""} · ${esc(o.tip_valuta)} ${bani(o.val_valuta)} × ${esc(String(o.curs))}${furnizor ? " · furnizor " + furnizor : ""}${d390}</span>
        <span class="dec-recl-suma">${bani(o.baza)} bază · ${bani(o.tva)} TVA (lei)</span>
        <button class="btn-link dec-d301-del" data-actiune="DELETE /tenants/{tenant_id}/d301-operatiuni/{op_id}" data-id="${o.id}">șterge</button></div>`;
      }).join("")
    : `<div class="stare-goala stare-goala--inline">Nicio operațiune pe ${etPerioada()}. D301 se depune doar cu achiziții intracomunitare / taxare inversă — introdu-le mai jos; fără ele, declarația e pe zero.</div>`;
  zona.innerHTML = `<details class="dec-xml" open><summary>Operațiuni D301 — introducere (${ops.length})</summary>
    ${grila}
    <div class="camp-eticheta" style="margin:10px 0 4px">Adaugă operațiune:</div>
    <div class="dec-man-form">
      <label class="camp" style="width:320px"><span class="camp-eticheta">Tip operațiune <span class="oblig">*</span></span>
        <select id="d301-tip" class="camp-input">${ALEGE}${tipuri.map((t) => `<option value="${t.val}">${t.val} — ${esc(t.eticheta)}</option>`).join("")}</select></label>
      <label class="camp" id="d301-temei-wrap" style="width:320px;display:none"><span class="camp-eticheta">Temei art. 307 (tip 4) <span class="oblig">*</span></span>
        <select id="d301-temei307" class="camp-input"><option value="">— alege alineatul —</option>${(d.temeiuri_307 || []).map((tm) => `<option value="${tm.val}">${esc(tm.eticheta)}</option>`).join("")}</select></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">Nr. document <span class="oblig">*</span></span><input id="d301-nrdoc" class="camp-input"></label>
      <label class="camp" style="width:130px"><span class="camp-eticheta">Data document <span class="oblig">*</span></span><input id="d301-datadoc" class="camp-input" placeholder="ZZ.LL.AAAA"></label>
      <label class="camp" style="width:90px"><span class="camp-eticheta">Valută <span class="oblig">*</span></span>
        <select id="d301-valuta" class="camp-input">${ALEGE}${valute.map((v) => `<option value="${v}">${v}</option>`).join("")}</select></label>
      <label class="camp" style="width:110px"><span class="camp-eticheta">Val. valută <span class="oblig">*</span></span><input id="d301-val" type="number" step="0.01" class="camp-input"></label>
      <label class="camp" style="width:100px"><span class="camp-eticheta">Curs <span class="oblig">*</span></span><input id="d301-curs" type="number" step="0.0001" class="camp-input"></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">Cotă TVA <span class="oblig">*</span></span>
        <select id="d301-cota" class="camp-input">${ALEGE}${cote.map((c) => `<option value="${c.val}">${esc(c.eticheta)}</option>`).join("")}</select></label>
      <label class="camp" style="width:90px"><span class="camp-eticheta">Țară furnizor</span><input id="d301-partener_tara" class="camp-input" placeholder="ex. DE" maxlength="2" style="text-transform:uppercase"></label>
      <label class="camp" style="width:170px"><span class="camp-eticheta">Cod TVA furnizor</span><input id="d301-partener_cod" class="camp-input" placeholder="fără prefix țară"></label>
      <label class="camp" style="width:200px"><span class="camp-eticheta">Denumire furnizor</span><input id="d301-partener_den" class="camp-input"></label>
      <button class="buton-secundar" id="d301-add" data-actiune="POST /tenants/{tenant_id}/d301-operatiuni">+ adaugă</button>
    </div>
    <p class="ecran-nota" style="margin-top:2px">Furnizorul UE (țară + cod TVA) e opțional pentru D301, dar dacă îl completezi, achiziția apare automat în D390 (bunuri tip 1/3 → cod A; servicii tip 5 → cod S). Fără țară, operațiunea nu intră în D390.</p>
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
    try { await api.del(`/tenants/${S.tenant_id}/d301-operatiuni/${b.dataset.id}?an=${S.an}&luna=${S.luna}`); _panouModificat(corp); randeazaOperatiuniD301(corp, nav); }
    catch (e) { arataRefuzul(zona, e, gv("#d301-msg")); }
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
    if (cereAlegerile(zona, ["#d301-tip", "#d301-valuta", "#d301-cota"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    try { const _r = await api.post(`/tenants/${S.tenant_id}/d301-operatiuni`, b); _panouModificat(corp); await randeazaOperatiuniD301(corp, nav); if (_r && _r.avertisment) arataMesaj(gv("#d301-msg"), _r.avertisment, "atentionare"); }
    catch (e) {
      curataEroriCamp(zona);
      arataRefuzul(zona, e, gv("#d301-msg"), { campuri: _campuriCu(e, "d301-") });   // fallback B (zona) daca #camp lipseste
    }
  });
  gv("#d301-regen").addEventListener("click", () => regenereaza(corp, nav));
}

// tip==="d710" (rectificativa D100). Geaman cu randeazaOperatiuniD301: lista obligatiilor corectate +
// adaugare + stergere + regenerare. Obligatiile stau IN MEMORIE (S.d710_obligatii) - D710 le primeste
// DIRECT in body (nu are tabel in DB). Fiecare: cod obligatie (121 micro / 103 profit), suma initiala
// (declarata gresit in D100) + suma corecta; cota % obligatorie la micro (121). Clasele DS din cap.6/D301.
// [comanda Costin 9.1, A.3] codurile și denumirile vin de la server (`/declaratii/tipuri` -> `obligatii_d710`), din nomenclatorul oficial
// (OPANAF 587/2016, anexa nr. 3) — nu dintr-o listă scrisă aici
function _d710_et(cod) { const c = (S.obligatiiD710 || []).find((x) => x.cod === cod); return c ? c.denumire + " (" + c.cod + ")" : "Cod " + cod; }

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
        <select id="d710-cod" class="camp-input">${ALEGE}${(S.obligatiiD710 || []).map((c) => `<option value="${c.cod}">${esc(_d710_et(c.cod))}</option>`).join("")}</select></label>
      <label class="camp" style="width:160px"><span class="camp-eticheta">Suma declarată inițial <span class="oblig">*</span></span><input id="d710-i" type="number" step="1" class="camp-input"></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">Suma corectă <span class="oblig">*</span></span><input id="d710-c" type="number" step="1" class="camp-input"></label>
      <label class="camp" style="width:120px" id="d710-cota-wrap"><span class="camp-eticheta">Cotă micro (%) <span class="oblig">*</span></span><input id="d710-cota" type="number" step="0.01" class="camp-input" placeholder="ex. 1"></label>
      <button class="buton-secundar" id="d710-add" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ adaugă</button>
    </div>
    <div id="d710-msg"></div>
    <p style="margin-top:8px"><button class="buton-primar" id="d710-regen">${_etRegen()}</button>
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
    if (cereAlegerile(zona, ["#d710-cod"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
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
    if (err.length) { err.forEach(([id, m]) => _eroareFormular(zona, id, m)); return; }
    S.d710_obligatii.push(rand);
    randeazaFormularD710(corp, nav);
  });
  gv("#d710-regen").addEventListener("click", () => regenereaza(corp, nav));
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
  const camp = (id, val, et) => `<input id="${id}" aria-label="${esc(et)}" type="number" step="1" min="0" class="camp-input" value="${val === "" || val == null ? "" : esc(String(val))}">`;
  // eticheta pe linie proprie, apoi Baza+TVA intr-un sub-rand care se IMPACHETEAZA (flex-wrap) ->
  // nu se revarsa orizontal pe telefon (proba Pixel 5: inainte inputul TVA iesea din ecran).
  const randuri = _D311_SITUATII.map((s, i) => `
    <div class="dec-man-rand" style="flex-direction:column;align-items:stretch;gap:6px">
      <span class="dec-recl-desc" style="flex:0 0 auto">${i + 1}. ${esc(s.et)}</span>
      <div style="display:flex;flex-wrap:wrap;gap:12px">
        <label class="camp" style="flex:1 1 130px"><span class="camp-eticheta">Bază (lei)</span>${camp("d311-" + s.baza, d[s.baza], s.et + " — bază (lei)")}</label>
        <label class="camp" style="flex:1 1 130px"><span class="camp-eticheta">TVA (lei)</span>${camp("d311-" + s.tva, d[s.tva], s.et + " — TVA (lei)")}</label>
      </div>
    </div>`).join("");
  zona.innerHTML = `<details class="dec-xml" open><summary>Situația fiscală după anularea codului de TVA</summary>
    <div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:12px">
      <label class="camp" style="width:230px"><span class="camp-eticheta">Data anulării codului de TVA <span class="oblig">*</span></span>
        <input id="d311-data" type="date" class="camp-input" value="${esc(d.Data_A || "")}"></label>
      <label class="camp" style="width:430px"><span class="camp-eticheta">Motivul anulării <span class="oblig">*</span></span>
        <select id="d311-motiv" class="camp-input" data-butoane="">
          ${alegeDacaLipseste(d.motiv)}
          ${_D311_MOTIVE.map((mo) => `<option value="${mo.val}" ${d.motiv === mo.val ? "selected" : ""}>${esc(mo.et)}</option>`).join("")}
        </select></label>
      <label class="camp" style="width:auto;flex-direction:row;align-items:center;gap:6px">
        <input id="d311-rec" type="checkbox" ${d.d_rec ? "checked" : ""}><span class="camp-eticheta" style="margin:0">Declarație rectificativă</span></label>
    </div>
    <div class="camp-eticheta" style="margin:12px 0 4px">Sume pe operațiuni <span class="oblig">*</span> (cel puțin una &gt; 0):</div>
    ${randuri}
    <p class="camp-ajutor" style="margin-top:8px">Total de plată (control): <b id="d311-total">${bani(total)} lei</b> — se calculează automat din bazele și TVA de mai sus. Subtotalurile nu se completează.</p>
    <div id="d311-msg"></div>
    <p style="margin-top:8px"><button class="buton-primar" id="d311-regen">${_etRegen()}</button>
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
    regenereaza(corp, nav);
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
        <select id="d307-temei" class="camp-input" data-butoane="">${alegeDacaLipseste(d.temei)}
          ${_D307_TEMEI.map((t) => `<option value="${t.val}" ${d.temei === t.val ? "selected" : ""}>${esc(t.et)}</option>`).join("")}</select></label>
    </div>
    ${grila}
    <div class="camp-eticheta" style="margin:12px 0 4px">Adaugă operațiune:</div>
    <div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">
      <label class="camp" style="width:360px"><span class="camp-eticheta">Tipul operațiunii <span class="oblig">*</span></span>
        <select id="d307-tip" class="camp-input" data-butoane="">${ALEGE}${_D307_TIPURI.map((t) => `<option value="${t.val}">${esc(t.et)}</option>`).join("")}</select></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">CUI operator <span class="oblig">*</span></span><input id="d307-cod" type="text" class="camp-input"></label>
      <label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Denumire operator <span class="oblig">*</span></span><input id="d307-den" type="text" class="camp-input"></label>
      <label class="camp" style="width:150px"><span class="camp-eticheta">TVA (lei) <span class="oblig">*</span></span><input id="d307-tva" type="number" step="1" class="camp-input"></label>
      <button class="buton-secundar" id="d307-add" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ adaugă</button>
    </div>
    <div id="d307-msg"></div>
    <p class="camp-ajutor" style="margin-top:8px">Total ajustare TVA: <b>${bani(total)} lei</b> — se calculează automat din operațiunile de mai sus.</p>
    <p style="margin-top:8px"><button class="buton-primar" id="d307-regen">${_etRegen()}</button>
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
    if (cereAlegerile(zona, ["#d307-tip"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    const tip = gv("#d307-tip").value;
    const cod = gv("#d307-cod").value.trim();
    const den = gv("#d307-den").value.trim();
    const tvaRaw = gv("#d307-tva").value;
    const err = [];
    if (!cod) err.push(["d307-cod", "Completează codul fiscal (CUI) al operatorului."]);
    if (!den) err.push(["d307-den", "Completează denumirea operatorului (cedent / finanțator / beneficiar)."]);
    if (tvaRaw === "" || isNaN(parseFloat(tvaRaw))) err.push(["d307-tva", "Completează suma TVA a operațiunii (poate fi și negativă la regularizare)."]);
    if (err.length) { err.forEach(([id, m]) => _eroareFormular(zona, id, m)); return; }
    S.d307.operatiuni.push({ tip: tip, cod: cod, den: den, tva: parseFloat(tvaRaw) });
    randeazaFormularD307(corp, nav);
  });
  gv("#d307-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    // marcheaza campul vinovat INAINTE de a chema serverul (Regula 14.4)
    if (!(S.d307.operatiuni || []).length) {
      _refuzLangaRegen(zona, "Adaugă cel puțin o operațiune de ajustare (butonul + adaugă). D307 nu se depune fără operațiuni.");
      return;
    }
    if (S.d307.d_anulare && !S.d307.temei) {
      eroareCamp(zona, "d307-temei", "Alege temeiul legal al corectării (ai bifat că declarația corectează una depusă după anularea rezervei).");
      return;
    }
    regenereaza(corp, nav);
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
  const val2ni = _n(d.val2_ni);
  const ni = d.neindividualizati || [];
  // [lotul 12, C-nou] totalurile se rescriu singure la „change” pe sumele neindividualizate — fără re-desenarea formularului
  const totaluri = () => {
    const tval1 = benef.reduce((s, b) => s + (_n(b.val1) || 0), 0);
    const tval2 = benef.reduce((s, b) => s + (_n(b.val2) || 0), 0) + _n(S.d107.val2_ni);
    const tval3 = benef.reduce((s, b) => s + (_n(b.val3) || 0), 0) + _n(S.d107.val3_ni);
    return `Totaluri: acordată <b>${bani(tval1)}</b> · reportată <b>${bani(tval2)}</b> · dedusă <b>${bani(tval3)}</b> lei. Suma de control (total): <b>${bani(tval1 + tval2 + tval3)} lei</b> — se calculează automat din sumele de mai sus.`;
  };
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
      <button class="buton-secundar" id="d107-add" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ adaugă</button>
    </div>
    <div id="d107-msg"></div>
    <details class="dec-xml" style="margin-top:10px"><summary>Anexă — beneficiari neindividualizați (rar)</summary>
      <p class="camp-ajutor">Se completează doar dacă ai sume reportate/deduse pentru beneficiari care nu se individualizează. Lista cu numele lor apare doar când suma reportată de mai jos este mai mare ca zero.</p>
      <div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">
        <label class="camp" style="width:200px"><span class="camp-eticheta">Suma reportată neindividualizați (lei)</span><input id="d107-val2ni" type="number" step="1" min="0" class="camp-input" value="${esc(String(d.val2_ni || ""))}"></label>
        <label class="camp" style="width:200px"><span class="camp-eticheta">Suma dedusă neindividualizați (lei)</span><input id="d107-val3ni" type="number" step="1" min="0" class="camp-input" value="${esc(String(d.val3_ni || ""))}"></label>
      </div>
      <div id="d107-ni-bloc"${val2ni > 0 ? "" : " hidden"}>${grilaNI}
        <div class="camp-eticheta" style="margin:12px 0 4px">Adaugă beneficiar neindividualizat:</div>
        <div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">
          <label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Denumire / nume <span class="oblig">*</span></span><input id="d107-ni-den" type="text" class="camp-input"></label>
          <label class="camp" style="width:150px"><span class="camp-eticheta">CUI / CNP <span class="oblig">*</span></span><input id="d107-ni-cif" type="text" class="camp-input"></label>
          <label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Adresă <span class="oblig">*</span></span><input id="d107-ni-adr" type="text" class="camp-input"></label>
          <button class="buton-secundar" id="d107-ni-add" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ adaugă</button>
        </div>
      </div>
      <div id="d107-ni-msg"></div>
    </details>
    <p class="camp-ajutor" id="d107-totaluri" style="margin-top:8px">${totaluri()}</p>
    <p style="margin-top:8px"><button class="buton-primar" id="d107-regen">${_etRegen()}</button>
      <span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>
  </details>`;
  const gv = (id) => zona.querySelector(id);
  gv("#d107-rec").addEventListener("change", (e) => { S.d107.d_rec = e.target.checked ? 1 : 0; });
  gv("#d107-val2ni").addEventListener("change", (e) => {   // lista neindividualizaților se arată / se ascunde, fără re-desenarea formularului
    S.d107.val2_ni = e.target.value; gv("#d107-ni-bloc").hidden = !(_n(S.d107.val2_ni) > 0); gv("#d107-totaluri").innerHTML = totaluri();
  });
  gv("#d107-val3ni").addEventListener("change", (e) => { S.d107.val3_ni = e.target.value; gv("#d107-totaluri").innerHTML = totaluri(); });
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
    if (err.length) { err.forEach(([id, m]) => _eroareFormular(zona, id, m)); return; }
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
    if (err.length) { err.forEach(([id, m]) => _eroareFormular(zona, id, m)); return; }
    S.d107.neindividualizati.push({ den: den, cif: cif, adresa: adr });
    randeazaFormularD107(corp, nav);
  });
  gv("#d107-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    // marcheaza campul vinovat INAINTE de a chema serverul (Regula 14.4)
    if (!(S.d107.beneficiari || []).length) {
      _refuzLangaRegen(zona, "Adaugă cel puțin un beneficiar (butonul + adaugă). D107 nu se depune fără beneficiari.");
      return;
    }
    if (_n(S.d107.val2_ni) > 0 && !(S.d107.neindividualizati || []).length) {
      eroareCamp(zona, "d107-val2ni", "Ai o sumă reportată pentru beneficiari neindividualizați — adaugă-i în anexă sau șterge suma.");
      return;
    }
    regenereaza(corp, nav);
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
  // [lotul 12, C-nou] totalurile se rescriu singure la „change” pe sumă — fără re-desenarea formularului în care stă câmpul
  const totaluri = () => {
    const sr = _n(S.d177.suma_rest), tb = (S.d177.beneficiari || []).reduce((s, b) => s + _n(b.suma), 0);
    return `Alocat beneficiarilor: <b>${bani(tb)}</b> din <b>${bani(sr)}</b> lei rămași · nealocat: <b>${bani(sr - tb)}</b> lei. Suma de control a declarației este 0 (D177 e informativă).`;
  };
  const grila = benef.length
    ? benef.map((b, i) => `<div class="dec-man-rand">
        <span class="dec-recl-desc">${esc(_d177TipEt(b.tip))} · ${esc(b.den)} (${b.tip === "3" ? "CNP" : "CUI"} ${esc(String(b.cui))}) · ${bani(_n(b.suma))} lei${b.contract ? " · contract " + esc(b.contract) : ""} · ${b.acord ? "cu acord de informare" : "fără acord de informare"}</span>
        <button class="btn-link dec-d177-del" data-idx="${i}">șterge</button></div>`).join("")
    : `<div class="stare-goala stare-goala--inline">Niciun beneficiar. D177 redirecționează o parte din impozitul pe profit către entități nonprofit / unități de cult — adaugă mai jos fiecare beneficiar cu suma redirecționată.</div>`;
  zona.innerHTML = `<details class="dec-xml" open><summary>Redirecționarea impozitului pe profit (${cate(benef.length, "beneficiar", "beneficiari")})</summary>
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
        <select id="d177-tip" class="camp-input" data-butoane="">${ALEGE}${_D177_TIPB.map((t) => `<option value="${t.val}">${esc(t.et)}</option>`).join("")}</select></label>
      <label class="camp" style="width:160px"><span class="camp-eticheta" id="d177-cui-et">CUI beneficiar <span class="oblig">*</span></span><input id="d177-cui" type="text" class="camp-input"></label>
      <label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Denumire / nume beneficiar <span class="oblig">*</span></span><input id="d177-den" type="text" class="camp-input"></label>
      <label class="camp" style="width:240px"><span class="camp-eticheta">IBAN (RO…) <span class="oblig">*</span></span><input id="d177-iban" type="text" class="camp-input"></label>
      <label class="camp" style="width:160px"><span class="camp-eticheta">Suma redirecționată (lei) <span class="oblig">*</span></span><input id="d177-suma" type="number" step="1" min="0" class="camp-input"></label>
      <label class="camp" id="d177-contract-wrap" style="width:190px"><span class="camp-eticheta">Nr. și data contractului <span class="oblig">*</span></span><input id="d177-contract" type="text" class="camp-input"></label>
      <label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Adresa beneficiar</span><input id="d177-adr" type="text" class="camp-input"></label>
      <label class="camp" style="width:230px"><span class="camp-eticheta">Acord pentru informarea beneficiarului <span class="oblig">*</span></span>${selectDaNu('id="d177-acord"', null, "Acord pentru informarea beneficiarului")}</label>
      <button class="buton-secundar" id="d177-add" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ adaugă</button>
    </div>
    <div id="d177-msg"></div>
    <p class="camp-ajutor" id="d177-totaluri" style="margin-top:8px">${totaluri()}</p>
    <p style="margin-top:8px"><button class="buton-primar" id="d177-regen">${_etRegen()}</button>
      <span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>
  </details>`;
  const gv = (id) => zona.querySelector(id);
  gv("#d177-di").addEventListener("change", (e) => { S.d177.data_inceput = e.target.value; });
  gv("#d177-ds").addEventListener("change", (e) => { S.d177.data_sfarsit = e.target.value; });
  gv("#d177-smax").addEventListener("change", (e) => { S.d177.suma_max = e.target.value; });
  gv("#d177-sant").addEventListener("change", (e) => { S.d177.suma_ant = e.target.value; });
  gv("#d177-srest").addEventListener("change", (e) => { S.d177.suma_rest = e.target.value; gv("#d177-totaluri").innerHTML = totaluri(); });
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
    if (cereAlegerile(zona, ["#d177-tip", "#d177-acord"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    const tip = gv("#d177-tip").value;
    const cui = gv("#d177-cui").value.trim();
    const den = gv("#d177-den").value.trim();
    const iban = gv("#d177-iban").value.replace(/\s/g, "").toUpperCase();
    const sumaRaw = gv("#d177-suma").value;
    const contract = gv("#d177-contract").value.trim();
    const adr = gv("#d177-adr").value.trim();
    const acord = daNu(gv("#d177-acord"));   // [lotul 07.10 B] declarat la ANAF: ales de om, nu căsuță nebifată
    const err = [];
    if (!cui) err.push(["d177-cui", tip === "3" ? "Completează CNP-ul beneficiarului." : "Completează codul fiscal (CUI) al beneficiarului."]);
    if (!den) err.push(["d177-den", "Completează denumirea sau numele beneficiarului."]);
    if (!/^RO[0-9]{2}[0-9A-Z]{20}$/.test(iban)) err.push(["d177-iban", "IBAN-ul trebuie să înceapă cu RO și să aibă 24 de caractere."]);
    if (sumaRaw === "" || isNaN(parseFloat(sumaRaw)) || parseFloat(sumaRaw) <= 0) err.push(["d177-suma", "Completează suma redirecționată (mai mare ca zero)."]);
    if (tip !== "5" && !contract) err.push(["d177-contract", "Completează numărul și data contractului de sponsorizare / mecenat."]);
    if (err.length) { err.forEach(([id, m]) => _eroareFormular(zona, id, m)); return; }
    S.d177.beneficiari.push({ tip: tip, cui: cui, den: den, iban: iban, suma: sumaRaw, contract: contract, adresa: adr, acord: acord ? 1 : 0 });
    randeazaFormularD177(corp, nav);
  });
  gv("#d177-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    // marcheaza campul vinovat INAINTE de a chema serverul (Regula 14.4)
    // [lotul 11, 440] toate lipsurile deodată (alegerile + câmpurile), apoi un singur `return`
    const err = [];
    if (!(S.d177.beneficiari || []).length) err.push([null, "Adaugă cel puțin un beneficiar (butonul + adaugă). D177 nu se depune fără beneficiari."]);
    const totB = (S.d177.beneficiari || []).reduce((s, b) => s + _n(b.suma), 0);
    if (_n(S.d177.suma_rest) <= 0) err.push(["d177-srest", "Completează suma rămasă de redirecționat (mai mare ca zero)."]);
    else if (totB > _n(S.d177.suma_rest)) err.push(["d177-srest", "Suma alocată beneficiarilor depășește suma rămasă de redirecționat."]);
    if (_n(S.d177.suma_max) < _n(S.d177.suma_ant) + _n(S.d177.suma_rest)) {
      err.push(["d177-smax", "Suma maximă trebuie să fie cel puțin cât suma redirecționată anterior plus suma rămasă."]);
    }
    if (!S.d177.data_inceput || !S.d177.data_sfarsit) err.push(["d177-di", "Completează perioada fiscală (de la / până la)."]);
    if (err.length) { err.forEach(([id, m]) => _eroareFormular(zona, id, m)); return; }
    regenereaza(corp, nav);
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
    valabilitate_distribuire: parseInt(d.valabilitate_distribuire, 10),
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
      '<label class="camp" style="width:180px"><span class="camp-eticheta">Valabilitate <span class="oblig">*</span></span><select id="d230-valab" class="camp-input">' + alegeDacaLipseste(d.valabilitate_distribuire) + '<option value="1"' + (String(d.valabilitate_distribuire) === "1" ? " selected" : "") + '>Un an</option><option value="2"' + (valab2 ? " selected" : "") + '>Doi ani</option></select></label>' +
    "</div>" +
    '<p class="camp-ajutor" style="margin:6px 0 0">Sumă goală = ANAF determină cuantumul (până la 3,5% din impozit). Termen: 25 mai a anului următor.</p>' +
    '<div id="d230-msg"></div>' +
    '<p style="margin-top:8px"><button class="buton-primar" id="d230-regen">' + _etRegen() + '</button>' +
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
    S.d230.valabilitate_distribuire = gv("#d230-valab").value ? parseInt(gv("#d230-valab").value, 10) : null;
  };
  ["#d230-cnp", "#d230-nume", "#d230-init", "#d230-pren", "#d230-adr", "#d230-tel", "#d230-email", "#d230-den", "#d230-cif", "#d230-iban", "#d230-suma", "#d230-proc", "#d230-valab"].forEach((id) => gv(id).addEventListener("change", salveaza));
  gv("#d230-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveaza();
    if (cereAlegerile(zona, ["#d230-valab"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    const err = [];
    if (!S.d230.cif_c) err.push(["d230-cnp", "Completează CNP-ul contribuabilului."]);
    if (!S.d230.nume_c) err.push(["d230-nume", "Completează numele."]);
    if (!S.d230.prenume_c) err.push(["d230-pren", "Completează prenumele."]);
    if (!S.d230.den_entitate) err.push(["d230-den", "Completează denumirea entității beneficiare."]);
    if (!S.d230.cif_entitate) err.push(["d230-cif", "Completează CIF-ul entității."]);
    if (!S.d230.cont_entitate) err.push(["d230-iban", "Completează IBAN-ul entității beneficiare."]);
    if (err.length) { err.forEach(([id, m]) => _eroareFormular(zona, id, m)); return; }
    regenereaza(corp, nav);
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
  const cv = parseInt(ac.categ_venit, 10) || null;   // [lotul 07.10 B] categoria se scrie, nu vine „1” (DS cap.17)
  return {
    d_rec: d.d_rec ? 1 : 0,
    asociere: { den: (a.den || "").trim(), cif: (a.cif || "").replace(/\s+/g, ""), adresa: (a.adresa || "").trim() },
    reprezentant: { nume: (r.nume || "").trim(), cif: (r.cif || "").replace(/\s+/g, ""), adresa: (r.adresa || "").trim(),
      telefon: (r.telefon || "").trim(), email: (r.email || "").trim() },
    activitate: { categ_venit: cv, det_ven_net: 1, caen: (ac.caen || "").replace(/\s+/g, ""),
      forma_org: parseInt(ac.forma_org, 10) || null,   // [lotul 07.10 B] aleasă pe ecran; până azi pleca „1” fără câmp
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
  const optSel = (val, cur) => '<option value="' + val + '"' + (String(cur) === val ? " selected" : "") + ">";
  const optJud = _D204_JUDETE.map((p) => '<option value="' + p[0] + '"' + (String(ac.judet) === p[0] ? " selected" : "") + ">" + esc(p[1]) + "</option>").join("");
  const grila = aso.length
    ? aso.map((s, i) => '<div class="dec-man-rand"><span class="dec-recl-desc">' + esc(s.nume || "(fără nume)") + " · CNP/CUI " + esc(s.cif || "?") +
        " · cotă " + esc(String(s.cota || 0)) + "% · venit " + bani(Math.round(_n(s.venit) || 0)) + (Math.round(_n(s.pierd) || 0) > 0 ? (" · pierdere " + bani(Math.round(_n(s.pierd) || 0))) : "") + " lei</span>" +
        '<button class="btn-link dec-d204-del" data-idx="' + i + '">șterge</button></div>').join("")
    : '<div class="stare-goala stare-goala--inline">Niciun asociat. Cotele trebuie să însumeze 100, iar venitul repartizat să egaleze venitul net.</div>';
  const okCota = Math.abs(sCota - 100) < 0.005, okVen = sVen === net3, okPier = sPier === pierd3;
  zona.innerHTML = '<details class="dec-xml" open><summary>Asociere fără personalitate juridică — venit anual (' + cate(aso.length, "asociat", "asociați") + ")</summary>" +
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
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Categorie venit <span class="oblig">*</span></span><input id="d204-categ" type="number" step="1" min="1" max="6" class="camp-input" value="' + esc(ac.categ_venit == null ? "" : String(ac.categ_venit)) + '"></label>' +
      // [lotul 07.10 B] forma de organizare: nomenclatorul structurii ANAF D204 (1 asociere fără personalitate juridică, 2 entitate
      // supusă regimului transparenței fiscale), probat pe validatorul instalat: 1 și 2 valide, 3 „nu se afla in lista”
      '<label class="camp" style="width:260px"><span class="camp-eticheta">Formă de organizare <span class="oblig">*</span></span><select id="d204-forma" class="camp-input">' + alegeDacaLipseste(ac.forma_org) +
        optSel("1", ac.forma_org) + "1 — asociere fără personalitate juridică</option>" + optSel("2", ac.forma_org) + "2 — entitate în regim de transparență fiscală</option></select></label>" +
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
      '<button class="buton-secundar" id="d204-add" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ adaugă</button>' +
    "</div>" +
    '<div id="d204-msg"></div>' +
    '<p class="camp-ajutor" style="margin-top:8px">Σ cote: <b>' + (Math.round(sCota * 100) / 100) + "</b>% " + (okCota ? "✓" : "(trebuie 100)") +
      " · Σ venit repartizat: <b>" + sVen + "</b> / " + net3 + " lei " + (okVen ? "✓" : "(trebuie egal cu venitul net)") +
      (pierd3 > 0 ? (" · Σ pierdere: <b>" + sPier + "</b> / " + pierd3 + " " + (okPier ? "✓" : "(trebuie egal)")) : "") + "</p>" +
    '<p style="margin-top:8px"><button class="buton-primar" id="d204-regen">' + _etRegen() + '</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveaza = () => {
    S.d204.d_rec = gv("#d204-rec").checked ? 1 : 0;
    S.d204.asociere = { den: gv("#d204-aden").value.trim(), cif: gv("#d204-acif").value.trim(), adresa: gv("#d204-aadr").value.trim() };
    S.d204.reprezentant = { nume: gv("#d204-rnume").value.trim(), cif: gv("#d204-rcif").value.trim(), adresa: gv("#d204-radr").value.trim(),
      telefon: gv("#d204-rtel").value.trim(), email: gv("#d204-remail").value.trim() };
    const sect = gv("#d204-sector");
    S.d204.activitate = { categ_venit: parseInt(gv("#d204-categ").value, 10) || null, forma_org: gv("#d204-forma").value || null, caen: gv("#d204-caen").value.trim(),
      judet: gv("#d204-judet").value, sector: sect ? sect.value.trim() : "", sediu: gv("#d204-sediu").value.trim(),
      nr_contr: gv("#d204-nrc").value.trim(), data_contr: gv("#d204-datac").value, venit3: _n(gv("#d204-venit3").value) || 0, chelt3: _n(gv("#d204-chelt3").value) || 0 };
  };
  ["#d204-aden", "#d204-acif", "#d204-aadr", "#d204-rnume", "#d204-rcif", "#d204-radr", "#d204-rtel", "#d204-remail", "#d204-categ", "#d204-caen", "#d204-sediu", "#d204-nrc", "#d204-datac", "#d204-venit3", "#d204-chelt3"].forEach((id) => { const e = gv(id); if (e) e.addEventListener("change", salveaza); });
  gv("#d204-rec").addEventListener("change", salveaza);
  gv("#d204-forma").addEventListener("change", salveaza);
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
    if (err.length) { err.forEach((x) => _eroareFormular(zona, x[0], x[1])); return; }
    salveaza();
    S.d204.asociati = S.d204.asociati || [];
    S.d204.asociati.push({ cif: cif, nume: nume, cota: _n(cota) || 0, venit: Math.round(_n(gv("#d204-avenit").value) || 0), pierd: Math.round(_n(gv("#d204-apierd").value) || 0) });
    randeazaFormularD204(corp, nav);
  });
  gv("#d204-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveaza();
    // [lotul 11, 440] toate lipsurile deodată (alegerile + câmpurile), apoi un singur `return`
    let faraAlegere = false; if (cereAlegerile(zona, ["#d204-forma"])) faraAlegere = true;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    const err = [];
    if (!(S.d204.asociati || []).length) err.push([null, "Adaugă cel puțin un asociat înainte de a genera D204."]);
    if (S.d204.activitate.categ_venit == null) err.push(["d204-categ", "Scrie categoria de venit."]);
    if (err.length || faraAlegere) { err.forEach(([id, m]) => _eroareFormular(zona, id, m)); return; }
    regenereaza(corp, nav);
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
  zona.innerHTML = '<details class="dec-xml" open><summary>Impozit special pe bunuri de valoare mare (' + cate(imob.length, "imobil", "imobile") + " · " + cate(mob.length, "bun mobil", "bunuri mobile") + ")</summary>" +
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
      '<label class="camp" style="width:100px"><span class="camp-eticheta">Cota de deținere % <span class="oblig">*</span></span><input id="d216-icota" type="number" step="0.0001" min="0" max="100" class="camp-input" placeholder="ex. 100"></label>' +
      '<label class="camp" style="width:140px"><span class="camp-eticheta">Plafon</span><input id="d216-iplaf" type="number" step="1" min="0" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d216-addi" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ imobil</button>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:12px 0 4px">Bunuri mobile de valoare mare (autovehicule etc.)</div>' +
    grilaM +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:8px;margin-top:6px">' +
      '<label class="camp" style="width:120px"><span class="camp-eticheta">An deținere</span><input id="d216-man" type="number" step="1" min="1900" class="camp-input"></label>' +
      '<label class="camp" style="width:100px"><span class="camp-eticheta">Niv</span><input id="d216-mniv" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Valoare impozabilă</span><input id="d216-mval" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:140px"><span class="camp-eticheta">Plafon</span><input id="d216-mplaf" type="number" step="1" min="0" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d216-addm" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ mobil</button>' +
    "</div>" +
    '<div id="d216-msg"></div>' +
    '<p class="camp-ajutor" style="margin-top:8px">Impozit imobile: <b>' + tImob + "</b> · impozit mobile: <b>" + tMob + "</b> lei (calculat cu rata validatorului 0,3%). Valoarea impozabilă trebuie să depășească plafonul.</p>" +
    '<p style="margin-top:8px"><button class="buton-primar" id="d216-regen">' + _etRegen() + '</button>' +
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
    // [lotul 07.10 B] „Cota de deţinere” = „cota-parte deţinută din imobil” (broșura ANAF D216, rd.3; R28.1: baza = (valoare - plafon) × cotă / 100) nu mai vine „0.3” (era cota
    // impozitului, pusă în câmpul greșit); o scrie omul: 0 < cotă ≤ 100
    const cotaPI = _n(gv("#d216-icota").value);
    if (!(cotaPI > 0 && cotaPI <= 100)) err.push(["d216-icota", "Scrie cota de deținere din imobil (între 0 și 100)."]);
    if (err.length) { err.forEach((x) => _eroareFormular(zona, x[0], x[1])); return; }
    salveazaAntet();
    S.d216.imobile = S.d216.imobile || [];
    S.d216.imobile.push({ judet_imobil: gv("#d216-ijud").value.trim(), cod_judet_imobil: gv("#d216-icjud").value.trim(),
      localitate_imobil: gv("#d216-iloc").value.trim(), cod_localitate_imobil: gv("#d216-icloc").value.trim(),
      strada_imobil: gv("#d216-istr").value.trim(), cod_strada_imobil: gv("#d216-icstr").value.trim(),
      nr_cadastral: gv("#d216-icad").value.trim(), valoare_impozabila_imobil: val, cota: cotaPI, plafon_imobil: plaf });
    randeazaFormularD216(corp, nav);
  });
  gv("#d216-addm").addEventListener("click", () => {
    curataEroriCamp(zona);
    const val = Math.round(_n(gv("#d216-mval").value) || 0), plaf = Math.round(_n(gv("#d216-mplaf").value) || 0);
    const err = [];
    if ((parseInt(gv("#d216-man").value, 10) || 0) <= 0) err.push(["d216-man", "Completează anul de deținere."]);
    if (val <= 0) err.push(["d216-mval", "Valoarea impozabilă trebuie > 0."]);
    if (val <= plaf) err.push(["d216-mval", "Valoarea impozabilă trebuie să depășească plafonul."]);
    if (err.length) { err.forEach((x) => _eroareFormular(zona, x[0], x[1])); return; }
    salveazaAntet();
    S.d216.mobile = S.d216.mobile || [];
    S.d216.mobile.push({ an_detinere: parseInt(gv("#d216-man").value, 10) || 0, niv: parseInt(gv("#d216-mniv").value, 10) || 0,
      valoare_impozabila_mobil: val, plafon_mobil: plaf });
    randeazaFormularD216(corp, nav);
  });
  gv("#d216-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveazaAntet();
    if (!(S.d216.imobile || []).length && !(S.d216.mobile || []).length) { _refuzLangaRegen(zona, "Adaugă cel puțin un bun (imobil sau mobil)."); return; }
    regenereaza(corp, nav);
  });
}

function _d208Manual() {
  const d = S.d208 || {};
  const im = d.imobil || {};
  return {
    nume: (d.nume || "").trim(), cif: (d.cif || "").replace(/\s+/g, ""), domiciliu: (d.domiciliu || "").trim(),
    nume_intocmit: (d.nume_intocmit || "").trim(), functia_intocmit: (d.functia_intocmit || "").trim(), dRec: d.dRec ? "1" : "0",
    nr_act_notarial: (d.nr_act_notarial || "").trim(), mod_transfer: d.mod_transfer ? String(d.mod_transfer) : "", alt_mod_transfer: String(d.mod_transfer) === "4" ? (d.alt_mod_transfer || "").trim() : "", taxa_notar: Math.round(_n(d.taxa_notar) || 0),
    imobile: [{
      judet: (im.judet || "").trim(), localitate: (im.localitate || "").trim(), codSIRUTA: (im.codSIRUTA || "").replace(/\s+/g, ""),
      nr_cadastral: (im.nr_cadastral || "").trim(), tip_imobil: String(im.tip_imobil),
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
  const optTip = (v, lbl) => '<option value="' + v + '"' + (String(im.tip_imobil) === v ? " selected" : "") + ">" + lbl + "</option>";
  const grilaB = ben.length
    ? ben.map((b, i) => '<div class="dec-man-rand"><span class="dec-recl-desc">' + esc(b.nume || "(beneficiar)") + " · CUI " + esc(b.cui || "?") +
        " · cotă " + esc(String(b.cota || 0)) + "% · cotăImpozit " + esc(String(b.cotaImpozit || 0)) + " · impozit " + bani(Math.round(_n(b.impozit) || 0)) + " lei</span>" +
        '<button class="btn-link dec-d208-delb" data-idx="' + i + '">șterge</button></div>').join("")
    : '<div class="stare-goala stare-goala--inline">Niciun beneficiar (obligatoriu; cotele însumează 100).</div>';
  const grilaP = par.length
    ? par.map((p, i) => '<div class="dec-man-rand"><span class="dec-recl-desc">' + esc(p.nume || "(parte)") + " · CUI " + esc(p.cui || "?") + " · cotă " + esc(String(p.cota || 0)) + "%</span>" +
        '<button class="btn-link dec-d208-delp" data-idx="' + i + '">șterge</button></div>').join("")
    : '<div class="stare-goala stare-goala--inline">Nicio altă parte contractantă (obligatoriu; cotele însumează 100).</div>';
  zona.innerHTML = '<details class="dec-xml" open><summary>Transfer proprietăți imobiliare — declarație notarială (' + cate(ben.length, "beneficiar", "beneficiari") + " · " + cate(par.length, "parte", "părți") + ")</summary>" +
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
      // [lotul 07.10 B] modalitatea de transfer: structura ANAF D208 v1.0.0 (19.02.2024) poz.22, mod_transfer IN (1,2,3,4); până azi
      // pleca „1” (vânzare-cumpărare) fără câmp — o moștenire sau o donație ieșea declarată vânzare
      '<label class="camp" style="width:230px"><span class="camp-eticheta">Modalitatea de transfer <span class="oblig">*</span></span><select id="d208-mod" class="camp-input">' + alegeDacaLipseste(d.mod_transfer) +
        [["1", "act de vânzare-cumpărare"], ["2", "moștenire"], ["3", "donație"], ["4", "altă modalitate de transfer"]].map(([v, l]) => '<option value="' + v + '"' + (String(d.mod_transfer) === v ? " selected" : "") + ">" + l + "</option>").join("") + "</select></label>" +
      (String(d.mod_transfer) === "4" ? '<label class="camp" style="width:260px"><span class="camp-eticheta">Explicații altă modalitate <span class="oblig">*</span></span><input id="d208-altmod" type="text" maxlength="250" class="camp-input" value="' + esc(d.alt_mod_transfer || "") + '"></label>' : "") +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Taxă notar</span><input id="d208-taxa" type="number" step="1" min="0" class="camp-input" value="' + esc(String(d.taxa_notar || "")) + '"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Județ <span class="oblig">*</span></span><select id="d208-jud" class="camp-input"><option value="">— alege —</option>' + optJud + "</select></label>" +
      '<label class="camp" style="flex:1 1 180px"><span class="camp-eticheta">Localitate <span class="oblig">*</span></span><input id="d208-loc" type="text" class="camp-input" value="' + esc(im.localitate || "") + '"></label>' +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Cod SIRUTA <span class="oblig">*</span></span><input id="d208-sir" type="text" class="camp-input" value="' + esc(im.codSIRUTA || "") + '"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Nr. cadastral <span class="oblig">*</span></span><input id="d208-cad" type="text" class="camp-input" value="' + esc(im.nr_cadastral || "") + '"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Tip imobil</span><select id="d208-tip" class="camp-input">' + alegeDacaLipseste(im.tip_imobil) + optTip("teren", "Teren") + optTip("cladire", "Clădire") + optTip("unitate", "Unitate") + "</select></label>" +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Valoare tranzacție</span><input id="d208-valt" type="number" step="1" min="0" class="camp-input" value="' + esc(String(im.val_tranzactie_imobil || "")) + '"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Valoare piață</span><input id="d208-valp" type="number" step="1" min="0" class="camp-input" value="' + esc(String(im.val_piata_imobil || "")) + '"></label>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Beneficiari (dobânditori) — cotele însumează 100</div>' +
    grilaB +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:8px;margin-top:6px">' +
      '<label class="camp" style="width:160px"><span class="camp-eticheta">CUI/CNP</span><input id="d208-bcui" type="text" maxlength="13" class="camp-input"></label>' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Nume</span><input id="d208-bnume" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:90px"><span class="camp-eticheta">Cotă %</span><input id="d208-bcota" type="number" step="0.01" min="0" max="100" class="camp-input"></label>' +
      '<label class="camp" style="width:120px"><span class="camp-eticheta">Cotă impozit</span><select id="d208-bci" class="camp-input" data-butoane="">' + ALEGE + '<option value="0">0</option><option value="1">1</option><option value="3">3</option></select></label>' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Bază calcul</span><input id="d208-bbaza" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:120px"><span class="camp-eticheta">Impozit</span><input id="d208-bimp" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:120px"><span class="camp-eticheta">Impozit scutit</span><input id="d208-bsc" type="number" step="1" min="0" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d208-addb" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ beneficiar</button>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:12px 0 4px">Celelalte părți contractante (înstrăinători) — cotele însumează 100</div>' +
    grilaP +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:8px;margin-top:6px">' +
      '<label class="camp" style="width:160px"><span class="camp-eticheta">CUI/CNP</span><input id="d208-pcui" type="text" maxlength="13" class="camp-input"></label>' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Nume</span><input id="d208-pnume" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:90px"><span class="camp-eticheta">Cotă %</span><input id="d208-pcota" type="number" step="0.01" min="0" max="100" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d208-addp" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ parte</button>' +
    "</div>" +
    '<div id="d208-msg"></div>' +
    '<p class="camp-ajutor" style="margin-top:8px">Σ cote beneficiari: <b>' + (Math.round(sBen * 100) / 100) + "</b>% " + (okBen ? "✓" : "(trebuie 100)") +
      " · Σ cote părți: <b>" + (Math.round(sPar * 100) / 100) + "</b>% " + (okPar ? "✓" : "(trebuie 100)") + " · impozit total: <b>" + tImp + "</b> lei</p>" +
    '<p style="margin-top:8px"><button class="buton-primar" id="d208-regen">' + _etRegen() + '</button>' +
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
    S.d208.mod_transfer = gv("#d208-mod").value || null;
    const altm = gv("#d208-altmod"); if (altm) S.d208.alt_mod_transfer = altm.value.trim();
    S.d208.taxa_notar = _n(gv("#d208-taxa").value) || 0;
    S.d208.imobil = { judet: gv("#d208-jud").value, localitate: gv("#d208-loc").value.trim(), codSIRUTA: gv("#d208-sir").value.trim(),
      nr_cadastral: gv("#d208-cad").value.trim(), tip_imobil: gv("#d208-tip").value,
      val_tranzactie_imobil: _n(gv("#d208-valt").value) || 0, val_piata_imobil: _n(gv("#d208-valp").value) || 0 };
  };
  ["#d208-nume", "#d208-cif", "#d208-dom", "#d208-inume", "#d208-ifunc", "#d208-act", "#d208-taxa", "#d208-jud", "#d208-loc", "#d208-sir", "#d208-cad", "#d208-tip", "#d208-valt", "#d208-valp"].forEach((id) => gv(id).addEventListener("change", salveaza));
  gv("#d208-mod").addEventListener("change", () => { salveaza(); randeazaFormularD208(corp, nav); });
  { const altm0 = gv("#d208-altmod"); if (altm0) altm0.addEventListener("change", salveaza); }
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
    if (err.length) { err.forEach((x) => _eroareFormular(zona, x[0], x[1])); return; }
    salveaza();
    if (cereAlegerile(zona, ["#d208-bci"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
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
    if (err.length) { err.forEach((x) => _eroareFormular(zona, x[0], x[1])); return; }
    salveaza();
    S.d208.parti = S.d208.parti || [];
    S.d208.parti.push({ cui: cui, nume: nume, cota: _n(cota) || 0 });
    randeazaFormularD208(corp, nav);
  });
  gv("#d208-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveaza();
    // [lotul 11, 440] toate lipsurile deodată (alegerile + câmpurile), apoi un singur `return`
    let faraAlegere = false; if (cereAlegerile(zona, ["#d208-mod", "#d208-tip"])) faraAlegere = true;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    const err = [];
    if (String(S.d208.mod_transfer) === "4" && !S.d208.alt_mod_transfer) err.push(["d208-altmod", "Explică modalitatea de transfer."]);
    if (!(S.d208.beneficiari || []).length) err.push([null, "Adaugă cel puțin un beneficiar."]);
    if (!(S.d208.parti || []).length) err.push([null, "Adaugă cel puțin o parte contractantă."]);
    if (err.length || faraAlegere) { err.forEach(([id, m]) => _eroareFormular(zona, id, m)); return; }
    regenereaza(corp, nav);
  });
}

const _D603_JUDETE = [["AB","Alba"],["AR","Arad"],["AG","Argeș"],["BC","Bacău"],["BH","Bihor"],["BN","Bistrița-Năsăud"],["BT","Botoșani"],["BV","Brașov"],["BR","Brăila"],["BZ","Buzău"],["CS","Caraș-Severin"],["CL","Călărași"],["CJ","Cluj"],["CT","Constanța"],["CV","Covasna"],["DB","Dâmbovița"],["DJ","Dolj"],["GL","Galați"],["GR","Giurgiu"],["GJ","Gorj"],["HR","Harghita"],["HD","Hunedoara"],["IL","Ialomița"],["IS","Iași"],["IF","Ilfov"],["MM","Maramureș"],["MH","Mehedinți"],["MS","Mureș"],["NT","Neamț"],["OT","Olt"],["PH","Prahova"],["SM","Satu Mare"],["SJ","Sălaj"],["SB","Sibiu"],["SV","Suceava"],["TR","Teleorman"],["TM","Timiș"],["TL","Tulcea"],["VS","Vaslui"],["VL","Vâlcea"],["VN","Vrancea"],["B","București"]];

function _d603Manual() {
  const d = S.d603 || {};
  return {
    numeContrib: (d.numeContrib || "").trim(), cif: (d.cif || "").replace(/\s+/g, ""),
    taraContrib: (d.taraContrib || "").trim().toUpperCase(), judetContrib: (d.judetContrib || "").trim().toUpperCase(),
    exceptare: parseInt(d.exceptare, 10), statAsigurare: (d.statAsigurare || "").trim().toUpperCase(),
    dataInceput: (d.dataInceput || "").trim(), dataSfarsit: (d.dataSfarsit || "").trim(), dataExceptare: (d.dataExceptare || "").trim(),
    documente: (d.documente || "").trim(), imputernicit: 0,
  };
}

function randeazaFormularD603(corp, nav) {
  const zona = corp.querySelector("#dec-d603-form");
  if (!zona) return;
  const d = S.d603;
  const roTara = String(d.taraContrib || "").toUpperCase() === "RO";
  const optJud = _D603_JUDETE.map((p) => '<option value="' + p[0] + '"' + (String(d.judetContrib).toUpperCase() === p[0] ? " selected" : "") + ">" + esc(p[1]) + "</option>").join("");
  const optExc = (v) => '<option value="' + v + '"' + (String(d.exceptare) === v ? " selected" : "") + ">" + v + "</option>";
  zona.innerHTML = '<details class="dec-xml" open><summary>Exceptare de la plata CASS — declarație pe propria răspundere</summary>' +
    '<div class="camp-eticheta" style="margin:2px 0 4px">Persoana fizică</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 220px"><span class="camp-eticheta">Nume și prenume <span class="oblig">*</span></span><input id="d603-nume" type="text" class="camp-input" value="' + esc(d.numeContrib || "") + '"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">CNP <span class="oblig">*</span></span><input id="d603-cif" type="text" maxlength="13" class="camp-input" value="' + esc(d.cif || "") + '"></label>' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Țară <span class="oblig">*</span></span><input id="d603-tara" type="text" maxlength="2" class="camp-input" value="' + esc(d.taraContrib || "") + '" placeholder="ex. RO"></label>' +
      // [lotul 12, C-nou] județul stă mereu în formular, ascuns în afara României: țara schimbată nu mai re-desenează formularul
      '<label class="camp" id="d603-jud-camp" style="width:180px"' + (roTara ? "" : " hidden") + '><span class="camp-eticheta">Județ <span class="oblig">*</span></span><select id="d603-jud" class="camp-input"><option value="">— alege —</option>' + optJud + "</select></label>" +
    "</div>" +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Exceptarea</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:160px"><span class="camp-eticheta">Categorie exceptare <span class="oblig">*</span></span><select id="d603-exc" class="camp-input">' + alegeDacaLipseste(d.exceptare) + optExc("2") + optExc("3") + optExc("4") + "</select></label>" +
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
    '<p style="margin-top:8px"><button class="buton-primar" id="d603-regen">' + _etRegen() + '</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveaza = () => {
    S.d603.numeContrib = gv("#d603-nume").value.trim();
    S.d603.cif = gv("#d603-cif").value.trim();
    S.d603.taraContrib = gv("#d603-tara").value.trim().toUpperCase();
    const jud = gv("#d603-jud"); S.d603.judetContrib = jud && S.d603.taraContrib === "RO" ? jud.value : "";
    S.d603.exceptare = gv("#d603-exc").value;
    S.d603.statAsigurare = gv("#d603-stat").value.trim().toUpperCase();
    S.d603.dataInceput = gv("#d603-di").value;
    S.d603.dataSfarsit = gv("#d603-ds").value;
    S.d603.dataExceptare = gv("#d603-de").value;
    S.d603.documente = gv("#d603-doc").value.trim();
  };
  ["#d603-nume", "#d603-cif", "#d603-exc", "#d603-stat", "#d603-di", "#d603-ds", "#d603-de", "#d603-doc"].forEach((id) => gv(id).addEventListener("change", salveaza));
  gv("#d603-tara").addEventListener("change", () => { salveaza(); gv("#d603-jud-camp").hidden = S.d603.taraContrib !== "RO"; });
  const jud0 = gv("#d603-jud"); if (jud0) jud0.addEventListener("change", salveaza);
  gv("#d603-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveaza();
    if (cereAlegerile(zona, ["#d603-exc"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    const err = [];
    if (!S.d603.numeContrib) err.push(["d603-nume", "Completează numele."]);
    if (!/^\d{13}$/.test(S.d603.cif)) err.push(["d603-cif", "CNP-ul trebuie să aibă 13 cifre."]);
    if (!/^[A-Z]{2}$/.test(S.d603.taraContrib)) err.push(["d603-tara", "Scrie țara persoanei: codul din două litere (ex. RO)."]);   // [lotul 13, 504] fără „RO” pus de ecran
    else if (S.d603.taraContrib === "RO" && !S.d603.judetContrib) err.push(["d603-jud", "Alege județul."]);
    if (!S.d603.statAsigurare) err.push(["d603-stat", "Completează statul de asigurare."]);
    else if (S.d603.statAsigurare === "RO") err.push(["d603-stat", "Statul de asigurare trebuie diferit de RO."]);
    if (!S.d603.dataInceput || !S.d603.dataSfarsit || !S.d603.dataExceptare) err.push(["d603-di", "Completează cele trei date."]);
    if (!S.d603.documente) err.push(["d603-doc", "Completează documentele justificative."]);
    if (err.length) { err.forEach((x) => _eroareFormular(zona, x[0], x[1])); return; }
    regenereaza(corp, nav);
  });
}

function _d104Manual() {
  const d = S.d104 || {};
  const a = d.asociere || {};
  return {
    declarant_nume: (d.declarant_nume || "").trim(), declarant_prenume: (d.declarant_prenume || "").trim(),
    declarant_functie: (d.declarant_functie || "").trim(),
    asociere: { cui: (a.cui || "").replace(/\s+/g, ""), den: (a.den || "").trim(), adresa: (a.adresa || "").trim() },
    d_rec: d.d_rec ? 1 : 0, profit_pierd: Math.round(_n(d.profit_pierd) || 0),
    asociati: (d.asociati || []).map((s) => ({ den: (s.den || "").trim(), cif: (s.cif || "").replace(/\s+/g, ""),
      adresa: (s.adresa || "").trim(), cota: _n(s.cota) || 0, venit: Math.round(_n(s.venit) || 0),
      chelt: Math.round(_n(s.chelt) || 0), imp_datorat: Math.round(_n(s.imp_datorat) || 0),
      imp_declarat: Math.round(_n(s.imp_declarat) || 0) })),
  };
}

function randeazaFormularD104(corp, nav) {
  const zona = corp.querySelector("#dec-d104-form");
  if (!zona) return;
  const d = S.d104;
  const a = d.asociere || {};
  const aso = d.asociati || [];
  const defin = Number(S.trim) === 4;
  let tVen = 0, tCh = 0, tImp = 0;
  aso.forEach((s) => { tVen += Math.round(_n(s.venit) || 0); tCh += Math.round(_n(s.chelt) || 0); tImp += Math.round(_n(s.imp_datorat) || 0); });
  const grila = aso.length
    ? aso.map((s, i) => '<div class="dec-man-rand"><span class="dec-recl-desc">' + esc(s.den || "(asociat)") + " · CUI/CNP " + esc(s.cif || "?") +
        " · cotă " + esc(String(s.cota || 0)) + "% · venit " + bani(Math.round(_n(s.venit) || 0)) + " · impozit " + bani(Math.round(_n(s.imp_datorat) || 0)) + " lei</span>" +
        '<button class="btn-link dec-d104-del" data-idx="' + i + '">șterge</button></div>').join("")
    : '<div class="stare-goala stare-goala--inline">Niciun asociat. Adaugă fiecare asociat cu cota și sumele de distribuit.</div>';
  zona.innerHTML = '<details class="dec-xml" open><summary>Distribuire venituri/cheltuieli pe asociați (' + cate(aso.length, "asociat", "asociați") + " · " + (defin ? "definitivare an" : "trimestrial cumulat") + ")</summary>" +
    '<div class="camp-eticheta" style="margin:2px 0 4px">Declarantul (reprezentantul asocierii)</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Nume <span class="oblig">*</span></span><input id="d104-dnume" type="text" class="camp-input" value="' + esc(d.declarant_nume || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Prenume <span class="oblig">*</span></span><input id="d104-dpren" type="text" class="camp-input" value="' + esc(d.declarant_prenume || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Funcție <span class="oblig">*</span></span><input id="d104-dfunc" type="text" class="camp-input" value="' + esc(d.declarant_functie || "") + '"></label>' +
      '<label class="set-bifa"><input id="d104-rec" type="checkbox" ' + (d.d_rec ? "checked" : "") + '> <span>Rectificativă</span></label>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Asocierea (fără personalitate juridică)</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 220px"><span class="camp-eticheta">Denumire asociere <span class="oblig">*</span></span><input id="d104-aden" type="text" class="camp-input" value="' + esc(a.den || "") + '"></label>' +
      '<label class="camp" style="width:160px"><span class="camp-eticheta">CUI asociere <span class="oblig">*</span></span><input id="d104-acui" type="text" class="camp-input" value="' + esc(a.cui || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 220px"><span class="camp-eticheta">Adresă asociere <span class="oblig">*</span></span><input id="d104-aadr" type="text" class="camp-input" value="' + esc(a.adresa || "") + '"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Profit(+)/pierdere(-) <span class="oblig">*</span></span><input id="d104-profit" type="number" step="1" class="camp-input" value="' + esc(String(d.profit_pierd === "" ? "" : (d.profit_pierd || 0))) + '"></label>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Asociați (distribuția)</div>' +
    grila +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:8px;margin-top:6px">' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Nume/denumire</span><input id="d104-sden" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">CUI/CNP</span><input id="d104-scif" type="text" maxlength="13" class="camp-input"></label>' +
      '<label class="camp" style="width:90px"><span class="camp-eticheta">Cotă %</span><input id="d104-scota" type="number" step="0.01" min="0" max="100" class="camp-input"></label>' +
      '<label class="camp" style="width:120px"><span class="camp-eticheta">Venit</span><input id="d104-sven" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:120px"><span class="camp-eticheta">Cheltuieli</span><input id="d104-sch" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:120px"><span class="camp-eticheta">Impozit datorat</span><input id="d104-simpd" type="number" step="1" min="0" class="camp-input"></label>' +
      (defin ? '<label class="camp" style="width:120px"><span class="camp-eticheta">Impozit declarat</span><input id="d104-simpr" type="number" step="1" min="0" class="camp-input"></label>' : "") +
      '<button class="buton-secundar" id="d104-add" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ asociat</button>' +
    "</div>" +
    '<div id="d104-msg"></div>' +
    '<p class="camp-ajutor" style="margin-top:8px">Σ venit: <b>' + tVen + "</b> · Σ cheltuieli: <b>" + tCh + "</b> · Σ impozit datorat: <b>" + tImp + "</b> lei. " + (defin ? "Definitivare (trim 4 -> luna 12): se completează și impozitul declarat." : "Trimestrial cumulat: impozitul declarat se completează doar la definitivare.") + "</p>" +
    '<p style="margin-top:8px"><button class="buton-primar" id="d104-regen">' + _etRegen() + '</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveaza = () => {
    S.d104.declarant_nume = gv("#d104-dnume").value.trim();
    S.d104.declarant_prenume = gv("#d104-dpren").value.trim();
    S.d104.declarant_functie = gv("#d104-dfunc").value.trim();
    S.d104.d_rec = gv("#d104-rec").checked ? 1 : 0;
    S.d104.asociere = { cui: gv("#d104-acui").value.trim(), den: gv("#d104-aden").value.trim(), adresa: gv("#d104-aadr").value.trim() };
    S.d104.profit_pierd = _n(gv("#d104-profit").value) || 0;
  };
  ["#d104-dnume", "#d104-dpren", "#d104-dfunc", "#d104-acui", "#d104-aden", "#d104-aadr", "#d104-profit"].forEach((id) => gv(id).addEventListener("change", salveaza));
  gv("#d104-rec").addEventListener("change", salveaza);
  zona.querySelectorAll(".dec-d104-del").forEach((b) => b.addEventListener("click", () => { S.d104.asociati.splice(parseInt(b.dataset.idx), 1); randeazaFormularD104(corp, nav); }));
  gv("#d104-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    const den = gv("#d104-sden").value.trim(), cif = gv("#d104-scif").value.trim(), cota = gv("#d104-scota").value.trim();
    const err = [];
    if (!den) err.push(["d104-sden", "Completează numele asociatului."]);
    if (!cif) err.push(["d104-scif", "Completează CUI/CNP-ul."]);
    if (!cota) err.push(["d104-scota", "Completează cota."]);
    if (err.length) { err.forEach((x) => _eroareFormular(zona, x[0], x[1])); return; }
    salveaza();
    S.d104.asociati = S.d104.asociati || [];
    const impr = gv("#d104-simpr");
    S.d104.asociati.push({ den: den, cif: cif, cota: _n(cota) || 0, venit: Math.round(_n(gv("#d104-sven").value) || 0),
      chelt: Math.round(_n(gv("#d104-sch").value) || 0), imp_datorat: Math.round(_n(gv("#d104-simpd").value) || 0),
      imp_declarat: impr ? Math.round(_n(impr.value) || 0) : 0 });
    randeazaFormularD104(corp, nav);
  });
  gv("#d104-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveaza();
    if (!(S.d104.asociati || []).length) { _refuzLangaRegen(zona, "Adaugă cel puțin un asociat."); return; }
    regenereaza(corp, nav);
  });
}

function _d114Manual() {
  const d = S.d114 || {};
  return {
    cif_declarant: (d.cif_declarant || "").replace(/\s+/g, ""), den_declarant: (d.den_declarant || "").trim(),
    adresa_declarant: (d.adresa_declarant || "").trim(), functia_intocmit: (d.functia_intocmit || "").trim(),
    den_intocmit: (d.den_intocmit || "").trim(), d_rec: d.d_rec ? "1" : "0",
    contracte: (d.contracte || []).map((c) => {
      const v = Math.round(_n(c.venit_lucrator) || 0);
      return { cui_lucrator: (c.cui_lucrator || "").replace(/\s+/g, ""), den_lucrator: (c.den_lucrator || "").trim(),
        nui_lucrator: (c.nui_lucrator || "").trim(), nr_contract: (c.nr_contract || "").trim(),
        data_contract: (c.data_contract || "").trim(), venit_lucrator: v, contributie_lucrator: Math.round(v / 100) };
    }),
  };
}

function randeazaFormularD114(corp, nav) {
  const zona = corp.querySelector("#dec-d114-form");
  if (!zona) return;
  const d = S.d114;
  const ct = d.contracte || [];
  let tVen = 0, tCam = 0;
  ct.forEach((c) => { const v = Math.round(_n(c.venit_lucrator) || 0); tVen += v; tCam += Math.round(v / 100); });
  const grila = ct.length
    ? ct.map((c, i) => { const v = Math.round(_n(c.venit_lucrator) || 0);
        return '<div class="dec-man-rand"><span class="dec-recl-desc">' + esc(c.den_lucrator || "(lucrător)") + " · CUI/CNP " + esc(c.cui_lucrator || "?") +
          " · venit " + bani(v) + " · CAM (1%) " + bani(Math.round(v / 100)) + " lei</span>" +
          '<button class="btn-link dec-d114-del" data-idx="' + i + '">șterge</button></div>'; }).join("")
    : '<div class="stare-goala stare-goala--inline">Niciun lucrător. Adaugă contractele pentru care se datorează CAM (dar nu se declară prin D112).</div>';
  zona.innerHTML = '<details class="dec-xml" open><summary>CAM — contribuția asiguratorie pentru muncă (situații ne-D112, ' + cate(ct.length, "lucrător", "lucrători") + ")</summary>" +
    '<div class="camp-eticheta" style="margin:2px 0 4px">Declarantul (angajatorul)</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:160px"><span class="camp-eticheta">CIF declarant <span class="oblig">*</span></span><input id="d114-cif" type="text" maxlength="10" class="camp-input" value="' + esc(d.cif_declarant || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Denumire <span class="oblig">*</span></span><input id="d114-den" type="text" class="camp-input" value="' + esc(d.den_declarant || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 220px"><span class="camp-eticheta">Adresă <span class="oblig">*</span></span><input id="d114-adr" type="text" class="camp-input" value="' + esc(d.adresa_declarant || "") + '"></label>' +
      '<label class="set-bifa"><input id="d114-rec" type="checkbox" ' + (d.d_rec ? "checked" : "") + '> <span>Rectificativă</span></label>' +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="flex:1 1 180px"><span class="camp-eticheta">Întocmit de (nume) <span class="oblig">*</span></span><input id="d114-inume" type="text" class="camp-input" value="' + esc(d.den_intocmit || "") + '"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Funcția <span class="oblig">*</span></span><input id="d114-ifunc" type="text" class="camp-input" value="' + esc(d.functia_intocmit || "") + '"></label>' +
    "</div>" +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Contracte / lucrători (CAM = 1% din venit)</div>' +
    grila +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:8px;margin-top:6px">' +
      '<label class="camp" style="width:160px"><span class="camp-eticheta">CUI/CNP lucrător</span><input id="d114-lcui" type="text" maxlength="13" class="camp-input"></label>' +
      '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">Nume lucrător</span><input id="d114-lden" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:110px"><span class="camp-eticheta">NUI</span><input id="d114-lnui" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:120px"><span class="camp-eticheta">Nr. contract</span><input id="d114-lnr" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Dată contract</span><input id="d114-ldata" type="text" class="camp-input" placeholder="zz.ll.aaaa"></label>' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Venit (bază)</span><input id="d114-lven" type="number" step="1" min="0" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d114-add" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ lucrător</button>' +
    "</div>" +
    '<div id="d114-msg"></div>' +
    '<p class="camp-ajutor" style="margin-top:8px">Σ venit: <b>' + tVen + "</b> · Σ CAM (1%): <b>" + tCam + "</b> lei. Contribuția se calculează automat = 1% din venit (regula validatorului). Perioada lunară din selectorul de sus.</p>" +
    '<p style="margin-top:8px"><button class="buton-primar" id="d114-regen">' + _etRegen() + '</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveaza = () => {
    S.d114.cif_declarant = gv("#d114-cif").value.trim();
    S.d114.den_declarant = gv("#d114-den").value.trim();
    S.d114.adresa_declarant = gv("#d114-adr").value.trim();
    S.d114.den_intocmit = gv("#d114-inume").value.trim();
    S.d114.functia_intocmit = gv("#d114-ifunc").value.trim();
    S.d114.d_rec = gv("#d114-rec").checked ? 1 : 0;
  };
  ["#d114-cif", "#d114-den", "#d114-adr", "#d114-inume", "#d114-ifunc"].forEach((id) => gv(id).addEventListener("change", salveaza));
  gv("#d114-rec").addEventListener("change", salveaza);
  zona.querySelectorAll(".dec-d114-del").forEach((b) => b.addEventListener("click", () => { S.d114.contracte.splice(parseInt(b.dataset.idx), 1); randeazaFormularD114(corp, nav); }));
  gv("#d114-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    const cui = gv("#d114-lcui").value.trim(), den = gv("#d114-lden").value.trim();
    const nui = gv("#d114-lnui").value.trim(), nr = gv("#d114-lnr").value.trim();
    const data = gv("#d114-ldata").value.trim(), ven = Math.round(_n(gv("#d114-lven").value) || 0);
    const err = [];
    if (!cui) err.push(["d114-lcui", "Completează CUI/CNP-ul lucrătorului."]);
    if (!den) err.push(["d114-lden", "Completează numele."]);
    if (!nui) err.push(["d114-lnui", "Completează NUI-ul."]);
    if (!nr) err.push(["d114-lnr", "Completează numărul contractului."]);
    if (!data) err.push(["d114-ldata", "Completează data contractului (zz.ll.aaaa)."]);
    if (ven <= 0) err.push(["d114-lven", "Venitul trebuie > 0."]);
    if (err.length) { err.forEach((x) => _eroareFormular(zona, x[0], x[1])); return; }
    salveaza();
    S.d114.contracte = S.d114.contracte || [];
    S.d114.contracte.push({ cui_lucrator: cui, den_lucrator: den, nui_lucrator: nui, nr_contract: nr, data_contract: data, venit_lucrator: ven, contributie_lucrator: Math.round(ven / 100) });
    randeazaFormularD114(corp, nav);
  });
  gv("#d114-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveaza();
    if (!(S.d114.contracte || []).length) { _refuzLangaRegen(zona, "Adaugă cel puțin un lucrător."); return; }
    regenereaza(corp, nav);
  });
}

const _D110_CODURI = ["602","604","605","606","607","608","611","619","621","622","623","625","626","627","628","629","631","632","633","634","635","636","637","638","639","640","641","642","690"];

function _d110Manual() {
  const d = S.d110 || {};
  return {
    d_temei: d.d_temei, d_rec: d.d_rec ? 1 : 0,
    iban: (d.iban || "").replace(/\s+/g, "").toUpperCase(), banca: (d.banca || "").trim(),
    obligatii: (d.obligatii || []).map((o) => ({ cod_oblig: String(o.cod_oblig || ""),
      suma_dat: Math.round(_n(o.suma_dat) || 0), suma_rest: Math.round(_n(o.suma_rest) || 0) })),
  };
}

function randeazaFormularD110(corp, nav) {
  const zona = corp.querySelector("#dec-d110-form");
  if (!zona) return;
  const d = S.d110;
  const rest = !!d.d_temei;
  const obl = d.obligatii || [];
  let sPlata = 0, sRest = 0;
  obl.forEach((o) => { const sd = Math.round(_n(o.suma_dat) || 0), sr = Math.round(_n(o.suma_rest) || 0);
    if (sd >= sr) sPlata += sd - sr; else sRest += sr - sd; });
  const optCod = _D110_CODURI.map((c) => '<option value="' + c + '">' + c + "</option>").join("");
  const grila = obl.length
    ? obl.map((o, i) => { const sd = Math.round(_n(o.suma_dat) || 0), sr = Math.round(_n(o.suma_rest) || 0);
        const dp = sd >= sr ? sd - sr : 0, dr = sd < sr ? sr - sd : 0;
        return '<div class="dec-man-rand"><span class="dec-recl-desc">cod ' + esc(String(o.cod_oblig)) + " · datorat " + bani(sd) + " · reținut " + bani(sr) +
          (dp > 0 ? (" · de plată " + bani(dp)) : "") + (dr > 0 ? (" · de restituit " + bani(dr)) : "") + " lei</span>" +
          '<button class="btn-link dec-d110-del" data-idx="' + i + '">șterge</button></div>'; }).join("")
    : '<div class="stare-goala stare-goala--inline">Nicio obligație. Adaugă codul obligației + impozitul datorat și cel reținut.</div>';
  const incoerent = (rest && sRest === 0) || (!rest && sRest > 0);
  zona.innerHTML = '<details class="dec-xml" open><summary>Regularizare impozit reținut la sursă (' + cate(obl.length, "obligație", "obligații") + ")</summary>" +
    '<p class="camp-ajutor" style="margin:2px 0 8px">Identitatea plătitorului (denumire, CUI, adresă, declarant) se preia din profilul firmei.</p>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:260px"><span class="camp-eticheta">Tip <span class="oblig">*</span></span><select id="d110-temei" class="camp-input">' + alegeDacaLipseste(d.d_temei) + '<option value="0"' + (String(d.d_temei) === "0" ? " selected" : "") + ">Regularizare (fără restituire)</option><option value=\"1\"" + (rest ? " selected" : "") + ">Cerere de restituire</option></select></label>" +
      '<label class="set-bifa"><input id="d110-rec" type="checkbox" ' + (d.d_rec ? "checked" : "") + '> <span>Rectificativă</span></label>' +
    "</div>" +
    (rest ?
      '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
        '<label class="camp" style="width:260px"><span class="camp-eticheta">IBAN (restituire) <span class="oblig">*</span></span><input id="d110-iban" type="text" class="camp-input" value="' + esc(d.iban || "") + '"></label>' +
        '<label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Bancă <span class="oblig">*</span></span><input id="d110-banca" type="text" class="camp-input" value="' + esc(d.banca || "") + '"></label>' +
      "</div>" : "") +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Obligații (impozit reținut la sursă)</div>' +
    grila +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:8px;margin-top:6px">' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Cod obligație</span><select id="d110-cod" class="camp-input">' + ALEGE + optCod + "</select></label>" +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Impozit datorat</span><input id="d110-dat" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Impozit reținut</span><input id="d110-rest" type="number" step="1" min="1" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d110-add" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ obligație</button>' +
    "</div>" +
    '<div id="d110-msg"></div>' +
    '<p class="camp-ajutor" style="margin-top:8px">Σ de plată: <b>' + sPlata + "</b> · Σ de restituit: <b>" + sRest + "</b> lei. " +
      (incoerent ? (rest ? "(cerere de restituire dar nicio diferență de restituit)" : "(există diferențe de restituit — alege „Cerere de restituire\" + IBAN)") : "") + "</p>" +
    '<p style="margin-top:8px"><button class="buton-primar" id="d110-regen">' + _etRegen() + '</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveaza = () => {
    S.d110.d_temei = gv("#d110-temei").value === "" ? null : parseInt(gv("#d110-temei").value, 10);
    S.d110.d_rec = gv("#d110-rec").checked ? 1 : 0;
    const ib = gv("#d110-iban"), bc = gv("#d110-banca");
    if (ib) S.d110.iban = ib.value.replace(/\s+/g, "").toUpperCase();
    if (bc) S.d110.banca = bc.value.trim();
  };
  gv("#d110-temei").addEventListener("change", () => { salveaza(); randeazaFormularD110(corp, nav); });
  gv("#d110-rec").addEventListener("change", salveaza);
  const ib0 = gv("#d110-iban"); if (ib0) ib0.addEventListener("change", salveaza);
  const bc0 = gv("#d110-banca"); if (bc0) bc0.addEventListener("change", salveaza);
  zona.querySelectorAll(".dec-d110-del").forEach((b) => b.addEventListener("click", () => { S.d110.obligatii.splice(parseInt(b.dataset.idx), 1); randeazaFormularD110(corp, nav); }));
  gv("#d110-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    const sr = Math.round(_n(gv("#d110-rest").value) || 0);
    salveaza();
    // [lotul 11, 440] toate lipsurile deodată (alegerile + câmpurile), apoi un singur `return`
    let faraAlegere = false; if (cereAlegerile(zona, ["#d110-cod"])) faraAlegere = true;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    if (sr <= 0) { eroareCamp(zona, "d110-rest", "Impozitul reținut trebuie > 0."); return; }
    if (faraAlegere) return;
    S.d110.obligatii = S.d110.obligatii || [];
    S.d110.obligatii.push({ cod_oblig: gv("#d110-cod").value, suma_dat: Math.round(_n(gv("#d110-dat").value) || 0), suma_rest: sr });
    randeazaFormularD110(corp, nav);
  });
  gv("#d110-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveaza();
    // [lotul 11, 440] toate lipsurile deodată (alegerile + câmpurile), apoi un singur `return`
    let faraAlegere = false; if (cereAlegerile(zona, ["#d110-temei"])) faraAlegere = true;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    if (!(S.d110.obligatii || []).length) { _refuzLangaRegen(zona, "Adaugă cel puțin o obligație."); return; }
    if (faraAlegere) return;
    regenereaza(corp, nav);
  });
}

const _D398_TRIM = [["01.01", "31.03"], ["01.04", "30.06"], ["01.07", "30.09"], ["01.10", "31.12"]];

function _d398Manual() {
  const d = S.d398 || {};
  const trim = Number(S.trim) || 1;
  const an = S.an;
  const q = _D398_TRIM[trim - 1];
  const moes = parseInt(d.moes_voes_imp, 10);   // [FAPT_FISCAL_NECERUT] regimul se alege; nu „1” din ecran
  const byState = {};
  (d.linii || []).forEach((l) => {
    const st = (l.mscon_state || "").toUpperCase();
    (byState[st] = byState[st] || []).push({
      supply_type: parseInt(l.supply_type, 10), trade_type: parseInt(l.trade_type, 10),   // [lotul 07.10 B] alese la rând (cereAlegerile) — fără „|| 1”
      vat_rate_type: parseInt(l.vat_rate_type, 10), vat_rate: _n(l.vat_rate) || 0,
      taxable_amount: _n(l.taxable_amount) || 0, vat_id_no_msest: (l.vat_id_no_msest || "").replace(/\s+/g, "").toUpperCase() });
  });
  const ms = Object.keys(byState).map((st) => ({ mscon_state: st, supplies: byState[st] }));
  const m = {
    moes_voes_imp: moes, name: (d.name || "").trim(), vat_id_no: (d.vat_id_no || "").replace(/\s+/g, "").toUpperCase(),
    an_r: an, luna_r: trim * 3, period_start_date: q[0] + "." + an, period_end_date: q[1] + "." + an,
    d_rec: d.d_rec ? 1 : 0, currency: "EUR", ms: ms,   // CF art.314 alin.(10) / art.315 alin.(12) / art.315^2 alin.(22): „se întocmește în euro”
  };
  if (moes === 1) m.e_int = d.e_int ? 1 : 0;
  return m;
}

function randeazaFormularD398(corp, nav) {
  const zona = corp.querySelector("#dec-d398-form");
  if (!zona) return;
  const d = S.d398;
  const moes = parseInt(d.moes_voes_imp, 10);   // [FAPT_FISCAL_NECERUT] regimul se alege; nu „1” din ecran
  const linii = d.linii || [];
  let gt = 0;
  linii.forEach((l) => { gt += Math.round((_n(l.taxable_amount) || 0) * (_n(l.vat_rate) || 0)) / 100; });
  const optRegim = (v, lbl) => '<option value="' + v + '"' + (String(d.moes_voes_imp) === v ? " selected" : "") + ">" + lbl + "</option>";
  const grila = linii.length
    ? linii.map((l, i) => { const va = Math.round((_n(l.taxable_amount) || 0) * (_n(l.vat_rate) || 0)) / 100;
        return '<div class="dec-man-rand"><span class="dec-recl-desc">' + esc((l.mscon_state || "?").toUpperCase()) + " · " +
          (String(l.supply_type) === "2" ? "servicii" : "bunuri") + " · " + (String(l.trade_type) === "2" ? "din sediul fix din alt stat membru" : "din România") +
          " · cotă " + esc(String(l.vat_rate || 0)) + "% · bază " + esc(String(l.taxable_amount || 0)) + " · TVA " + va.toFixed(2) + "</span>" +
          '<button class="btn-link dec-d398-del" data-idx="' + i + '">șterge</button></div>'; }).join("")
    : '<div class="stare-goala stare-goala--inline">Nicio livrare. Adaugă pe fiecare stat de consum livrările (bunuri/servicii) cu cota și baza.</div>';
  // [lotul 13, 594] denumirea și codul de TVA vin din Date firmă (vizibile, modificabile); textele în limba contabilului, fără numele
  // atributelor XML (msid / msest / e_int); trimestrul e cel ales la pasul 1, spus cu numele lui
  const fd = S.firmaDate || {};
  if (!d.name && fd.nume) d.name = fd.nume;
  if (!d.vat_id_no && fd.cui) d.vat_id_no = /^RO/i.test(String(fd.cui)) ? String(fd.cui).toUpperCase() : "RO" + String(fd.cui).replace(/\D/g, "");
  zona.innerHTML = '<details class="dec-xml" open><summary>OSS — TVA regimuri speciale (' + cate(linii.length, "livrare", "livrări") + ")</summary>" +
    '<div class="camp-eticheta" style="margin:2px 0 4px">Contribuabilul și regimul</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-start;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:230px"><span class="camp-eticheta">Regim special <span class="oblig">*</span></span><select id="d398-moes" class="camp-input">' + alegeDacaLipseste(d.moes_voes_imp) + optRegim("1", "UE (bunuri și servicii)") + optRegim("2", "non-UE (servicii)") + optRegim("3", "import (bunuri)") + "</select></label>" +
      '<label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Denumire <span class="oblig">*</span></span><input id="d398-name" type="text" class="camp-input" value="' + esc(d.name || "") + '"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Cod de TVA <span class="oblig">*</span></span><input id="d398-vat" type="text" class="camp-input" value="' + esc(d.vat_id_no || "") + '"></label>' +
      '<label class="camp" style="width:110px"><span class="camp-eticheta">Monedă</span><input id="d398-cur" type="text" class="camp-input" value="EUR" readonly aria-readonly="true" aria-label="Monedă: euro, impusă de lege" title="Impusă de lege: declarația specială de TVA se întocmește în euro (CF art.314 alin.(10), art.315 alin.(12), art.315^2 alin.(22))"></label>' +
      (moes === 1 ? '<label class="camp" style="width:240px"><span class="camp-eticheta">Are sedii fixe în alte state membre? <span class="oblig">*</span></span>' + selectDaNu('id="d398-eint"', d.e_int, "Sedii fixe în alte state membre") + "</label>" : "") +
    "</div>" +
    '<p class="camp-ajutor" style="margin:2px 0 8px">Declarația e pe trimestrul ales la pasul 1: <b>' + esc(etPerioada()) + '</b>. TVA-ul se calculează singur, bază × cotă / 100, pe fiecare stat de consum.</p>' +
    grila +
    '<div class="dec-man-form" data-rand-adaugare style="flex-wrap:wrap;align-items:flex-start;gap:8px;margin-top:6px">' +
      '<label class="camp" style="width:110px"><span class="camp-eticheta">Stat de consum</span><input id="d398-stat" type="text" maxlength="2" class="camp-input" placeholder="ex. DE"></label>' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Ce se livrează</span><select id="d398-sup" class="camp-input" data-butoane="">' + ALEGE + '<option value="1">bunuri</option><option value="2">servicii</option></select></label>' +
      '<label class="camp" style="width:210px"><span class="camp-eticheta">De unde pleacă livrarea</span><select id="d398-trade" class="camp-input" data-butoane="">' + ALEGE + '<option value="1">din România</option><option value="2">din sediul fix din alt stat membru</option></select></label>' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Tip cotă</span><select id="d398-vrt" class="camp-input" data-butoane="">' + ALEGE + '<option value="1">standard</option><option value="2">redusă</option></select></label>' +
      '<label class="camp" style="width:100px"><span class="camp-eticheta">Cotă %</span><input id="d398-rate" type="number" step="0.01" min="0" max="100" class="camp-input"></label>' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Bază impozabilă</span><input id="d398-baza" type="number" step="0.01" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:200px"><span class="camp-eticheta">Codul de TVA al sediului fix</span><input id="d398-vatmsest" type="text" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d398-add" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ livrare</button>' +
    "</div>" +
    '<div id="d398-msg"></div>' +
    '<p class="camp-ajutor" style="margin-top:8px">Total TVA datorat: <b>' + gt.toFixed(2) + "</b> " + esc(d.currency || "EUR") + ". Livrarea din sediul fix din alt stat membru există numai în regimul UE; regimul non-UE are numai servicii, iar regimul de import numai bunuri.</p>" +
    '<p style="margin-top:8px"><button class="buton-primar" id="d398-regen">' + _etRegen() + '</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveaza = () => {
    S.d398.moes_voes_imp = gv("#d398-moes").value;
    S.d398.name = gv("#d398-name").value.trim();
    S.d398.vat_id_no = gv("#d398-vat").value.replace(/\s+/g, "").toUpperCase();
    const ei = gv("#d398-eint"); if (ei) { const v = daNu(ei); S.d398.e_int = v === null ? null : (v ? 1 : 0); }
  };
  gv("#d398-moes").addEventListener("change", () => { salveaza(); randeazaFormularD398(corp, nav); });
  ["#d398-name", "#d398-vat"].forEach((id) => gv(id).addEventListener("change", salveaza));
  const ei0 = gv("#d398-eint"); if (ei0) ei0.addEventListener("change", salveaza);
  zona.querySelectorAll(".dec-d398-del").forEach((b) => b.addEventListener("click", () => { S.d398.linii.splice(parseInt(b.dataset.idx), 1); randeazaFormularD398(corp, nav); }));
  gv("#d398-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    if (cereAlegerile(zona, ["#d398-sup", "#d398-trade", "#d398-vrt"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    const stat = gv("#d398-stat").value.trim().toUpperCase(), rate = _n(gv("#d398-rate").value) || 0, baza = _n(gv("#d398-baza").value) || 0;
    const tt = gv("#d398-trade").value, msest = gv("#d398-vatmsest").value.trim();
    const err = [];
    if (!/^[A-Z]{2}$/.test(stat)) err.push(["d398-stat", "Statul de consum: codul țării, 2 litere (ex. DE)."]);
    if (!(rate > 0 && rate <= 100)) err.push(["d398-rate", "Cota trebuie în (0, 100]."]);
    if (baza <= 0) err.push(["d398-baza", "Baza impozabilă trebuie > 0."]);
    if (tt === "2" && !msest) err.push(["d398-vatmsest", "La livrarea din sediul fix din alt stat membru, completează codul de TVA al sediului fix."]);
    if (err.length) { err.forEach((x) => _eroareFormular(zona, x[0], x[1])); return; }
    salveaza();
    S.d398.linii = S.d398.linii || [];
    S.d398.linii.push({ mscon_state: stat, supply_type: gv("#d398-sup").value, trade_type: tt,
      vat_rate_type: gv("#d398-vrt").value, vat_rate: rate, taxable_amount: baza, vat_id_no_msest: tt === "2" ? msest : "" });
    randeazaFormularD398(corp, nav);
  });
  gv("#d398-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveaza();
    // [lotul 11, 440] toate lipsurile deodată (alegerile + câmpurile), apoi un singur `return`
    let faraAlegere = false; if (cereAlegerile(zona, ["#d398-moes", "#d398-eint"])) faraAlegere = true;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    if (!(S.d398.linii || []).length) { _refuzLangaRegen(zona, "Adaugă cel puțin o livrare."); return; }
    if (faraAlegere) return;
    regenereaza(corp, nav);
  });
}

// [formular_manual_d318] D318 (rambursare TVA achitata in alt stat membru UE, Directiva 2008/9/CE, MANUALA /
// la cerere): perioada de rambursare (implicit anuala 1 ian - 31 dec), solicitantul RO + IBAN-ul contului de
// rambursare, activitatea (cod NACE) si facturile de achizitie/import din statul de rambursare (furnizor UE +
// baza + TVA deductibila ceruta). amount = suma TVA deductibila (o calculeaza backendul). Valorile persista in
// S.d318 intre randari. Lista tarilor UE de rambursare (GB scos din 01.03.2021):
const _D318_TARI_UE = ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT",
  "LV", "LT", "LU", "MT", "NL", "PL", "PT", "SK", "SI", "ES", "SE"];

function _d318Manual() {
  const d = S.d318 || {};
  const annual = d.annual ? 1 : 0;
  // [lotul 13, 504] lunile cererii neanuale le scrie omul (fără 1 / 12 puse de ecran); lipsă -> null, refuzat lângă câmp la generare
  const li = annual ? 1 : (parseInt(d.luna_inceput, 10) || null);
  const ls = annual ? 12 : (parseInt(d.luna_sfarsit, 10) || null);
  const achizitii = [], importuri = [];
  (d.facturi || []).forEach((f) => {
    const linie = {
      reference_number: (f.reference_number || "").trim(),
      issuing_date: (f.issuing_date || "").trim(),
      taxable_amount: _n(f.taxable_amount) || 0,
      vat_amount: _n(f.vat_amount) || 0,
      deductible_vat: _n(f.deductible_vat) || 0,
      currency: (d.currency || "").toUpperCase(),
      furnizor: {
        denumire: (f.fz_denumire || "").trim(), strada: (f.fz_strada || "").trim(),
        tara: (f.fz_tara || d.refunding_country || "").toUpperCase(),
        vat_id: (f.fz_vat || "").replace(/\s+/g, "").toUpperCase(),
      },
      bunuri: f.cod_bun ? [{ code: String(f.cod_bun).trim() }] : [],
    };
    if (String(f.fel) === "import") importuri.push(linie); else achizitii.push(linie);
  });
  const m = {
    an: parseInt(d.an, 10) || S.an, luna_inceput: li, luna_sfarsit: ls, annual: annual,
    cui: (d.cui || "").replace(/\s+/g, ""), d_rec: d.d_rec ? 1 : 0,
    refunding_country: (d.refunding_country || "").toUpperCase(), currency: (d.currency || "").toUpperCase(),
    iban: (d.iban || "").replace(/\s+/g, "").toUpperCase(), bic: (d.bic || "").replace(/\s+/g, "").toUpperCase(),
    owner_name: (d.owner_name || "").trim(), owner_type: d.owner_type,
    declarant: (d.declarant || "").trim(), functie: (d.functie || "").trim(),
    solicitant: {
      denumire: (d.sol_denumire || "").trim(), strada: (d.sol_strada || "").trim(),
      email: (d.sol_email || "").trim(), cod_postal: (d.sol_cod || "").trim(),
    },
    activitati: (d.act_nace || "").trim() ? [{ activitate: (d.act_nace || "").trim(), descriere: (d.act_desc || "").trim() }] : [],
    achizitii: achizitii, importuri: importuri,
  };
  if (d.d_rec && (d.reference_number || "").trim()) m.reference_number = d.reference_number.trim();
  return m;
}

function randeazaFormularD318(corp, nav) {
  const zona = corp.querySelector("#dec-d318-form");
  if (!zona) return;
  const d = S.d318;
  // [lotul 13, 636] ce știe aplicația din Date firmă vine completat (vizibil, modificabil): CUI, denumire, adresă, email, IBAN, titularul
  // contului, declarantul și funcția lui, codul CAEN (NACE); [638] anul cererii = anul ales la pasul 1, ca titlul să spună același an
  const fd = S.firmaDate || {};
  const _pune = (k, v) => { if ((d[k] === "" || d[k] === null || d[k] === undefined) && v) d[k] = v; };
  _pune("an", String(S.an || ""));
  _pune("cui", String(fd.cui || "").replace(/\s+/g, ""));   // CUI-ul din Date firmă e deja în forma păstrată, fără „RO” (decizia 10.3 pct.4)
  _pune("sol_denumire", fd.nume); _pune("owner_name", fd.nume);
  _pune("sol_strada", [fd.adresa, fd.oras, fd.judet].filter(Boolean).join(", "));
  _pune("sol_email", fd.email); _pune("sol_cod", fd.cod_postal);
  _pune("iban", String(fd.iban || "").replace(/\s+/g, "").toUpperCase());
  _pune("declarant", [fd.declarant_prenume, fd.declarant_nume].filter(Boolean).join(" ")); _pune("functie", fd.declarant_functie);
  _pune("act_nace", fd.caen);
  const annual = d.annual ? 1 : 0;
  const facturi = d.facturi || [];
  let totalDed = 0;
  facturi.forEach((f) => { totalDed += _n(f.deductible_vat) || 0; });
  const optTara = (sel) => _D318_TARI_UE.map((x) => '<option value="' + x + '"' + (String(sel || "").toUpperCase() === x ? " selected" : "") + ">" + x + "</option>").join("");
  const grila = facturi.length
    ? facturi.map((f, i) => '<div class="dec-man-rand"><span class="dec-recl-desc">' +
        (String(f.fel) === "import" ? "import" : "achiziție") + " · " + esc(f.reference_number || "?") + " · " + esc(f.issuing_date || "?") +
        " · " + esc(f.fz_denumire || "?") + " (" + esc((f.fz_tara || d.refunding_country || "?").toUpperCase()) + ")" +
        " · bază " + esc(String(f.taxable_amount || 0)) + " · TVA ded. " + esc(String(f.deductible_vat || 0)) + "</span>" +
        '<button class="btn-link dec-d318-del" data-idx="' + i + '">șterge</button></div>').join("")
    : '<div class="stare-goala stare-goala--inline">Nicio factură. Adaugă cel puțin o factură de achiziție sau de import din statul de rambursare.</div>';
  const inp = (id, lbl, val, w, extra) => '<label class="camp" style="width:' + w + '"><span class="camp-eticheta">' + lbl + '</span><input id="' + id + '" ' + (extra || 'type="text"') + ' class="camp-input" value="' + esc(val || "") + '"></label>';
  zona.innerHTML = '<details class="dec-xml" open><summary>Rambursare TVA din alt stat UE (' + cate(facturi.length, "factură", "facturi") + ")</summary>" +
    '<div class="camp-eticheta" style="margin:2px 0 4px">Perioada de rambursare și solicitantul</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:6px">' +
      inp("d318-an", "An rambursare <span class=\"oblig\">*</span>", d.an || "", "120px", 'type="number" min="2010" max="2099"') +
      '<label class="set-bifa"><input id="d318-annual" type="checkbox" ' + (annual ? "checked" : "") + '> <span>Cerere anuală (1 ian – 31 dec)</span></label>' +
      (annual ? "" :
        '<label class="camp" style="width:110px"><span class="camp-eticheta">Luna început <span class="oblig">*</span></span><input id="d318-li" type="number" min="1" max="12" class="camp-input" value="' + esc(String(d.luna_inceput || "")) + '"></label>' +
        '<label class="camp" style="width:110px"><span class="camp-eticheta">Luna sfârșit <span class="oblig">*</span></span><input id="d318-ls" type="number" min="1" max="12" class="camp-input" value="' + esc(String(d.luna_sfarsit || "")) + '"></label>') +
      '<label class="camp" style="width:140px"><span class="camp-eticheta">Stat rambursare <span class="oblig">*</span></span><select id="d318-tara" class="camp-input">' + alegeDacaLipseste(d.refunding_country) + optTara(d.refunding_country) + "</select></label>" +
      inp("d318-cui", "CUI solicitant <span class=\"oblig\">*</span>", d.cui, "150px") +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:6px">' +
      '<label class="camp" style="width:180px"><span class="camp-eticheta">Tip cerere</span><select id="d318-drec" class="camp-input" data-butoane=""><option value="0"' + (d.d_rec ? "" : " selected") + ">inițială</option><option value=\"1\"" + (d.d_rec ? " selected" : "") + ">rectificativă</option></select></label>" +
      (d.d_rec ? inp("d318-ref", "Nr. referință (RO…) <span class=\"oblig\">*</span>", d.reference_number, "200px") : "") +
    "</div>" +
    '<div class="camp-eticheta" style="margin:6px 0 4px">Contul de rambursare</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:6px">' +
      inp("d318-iban", "IBAN <span class=\"oblig\">*</span>", d.iban, "260px") +
      inp("d318-bic", "BIC/SWIFT <span class=\"oblig\">*</span>", d.bic, "150px") +
      inp("d318-owner", "Titular cont <span class=\"oblig\">*</span>", d.owner_name, "200px") +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Tip titular</span><select id="d318-ownt" class="camp-input">' + alegeDacaLipseste(d.owner_type) + '<option value="A"' + (d.owner_type === "A" ? " selected" : "") + ">A — solicitant</option><option value=\"R\"" + (d.owner_type === "R" ? " selected" : "") + ">R — reprezentant</option></select></label>" +
      // [lotul 13, 636, clasa 631] moneda din lista monedelor BNR, nu scrisă de mână; fără alegere implicită (o alege omul: a statului de rambursare)
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Monedă <span class="oblig">*</span></span><select id="d318-cur" class="camp-input" title="Moneda statului membru de rambursare (HG 1/2016 pct.73 alin.(6) lit.e)">' + alegeDacaLipseste(d.currency) +
        ((S.nomenclatoare || {}).monede_bnr || []).map((m) => '<option value="' + esc(m) + '"' + (String(d.currency || "").toUpperCase() === m ? " selected" : "") + ">" + esc(m) + "</option>").join("") + "</select></label>" +
    "</div>" +
    '<div class="camp-eticheta" style="margin:6px 0 4px">Identitatea solicitantului</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:6px">' +
      inp("d318-soldenumire", "Denumire <span class=\"oblig\">*</span>", d.sol_denumire, "220px") +
      inp("d318-solstrada", "Adresă <span class=\"oblig\">*</span>", d.sol_strada, "260px") +
      inp("d318-solemail", "Email <span class=\"oblig\">*</span>", d.sol_email, "220px") +
      inp("d318-solcod", "Cod poștal", d.sol_cod, "120px") +
    "</div>" +
    '<div class="camp-eticheta" style="margin:6px 0 4px">Declarant și activitatea</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:6px">' +
      inp("d318-declarant", "Declarant <span class=\"oblig\">*</span>", d.declarant, "200px") +
      inp("d318-functie", "Funcție <span class=\"oblig\">*</span>", d.functie, "180px") +
      inp("d318-nace", "Cod activitate NACE <span class=\"oblig\">*</span>", d.act_nace, "170px") +
      inp("d318-actdesc", "Descriere activitate", d.act_desc, "260px") +
    "</div>" +
    '<div class="camp-eticheta" style="margin:8px 0 4px">Facturi (achiziții / importuri din statul de rambursare)</div>' +
    grila +
    '<div class="dec-man-form" data-rand-adaugare style="flex-wrap:wrap;align-items:flex-start;gap:8px;margin-top:6px">' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Fel</span><select id="d318-fel" class="camp-input" data-butoane="">' + ALEGE + '<option value="achizitie">achiziție</option><option value="import">import</option></select></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Nr. factură</span><input id="d318-fnr" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Data (dd.mm.aaaa)</span><input id="d318-fdata" type="text" class="camp-input" placeholder="15.06.' + esc(String(d.an || "")) + '"></label>' +
      '<label class="camp" style="width:110px"><span class="camp-eticheta">Bază</span><input id="d318-fbaza" type="number" step="0.01" class="camp-input"></label>' +
      '<label class="camp" style="width:110px"><span class="camp-eticheta">TVA</span><input id="d318-ftva" type="number" step="0.01" class="camp-input"></label>' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">TVA deductibil</span><input id="d318-fded" type="number" step="0.01" class="camp-input"></label>' +
      '<label class="camp" style="width:180px"><span class="camp-eticheta">Furnizor</span><input id="d318-ffz" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:200px"><span class="camp-eticheta">Adresă furnizor</span><input id="d318-ffzstr" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:110px"><span class="camp-eticheta">Țară furnizor</span><select id="d318-ffztara" class="camp-input">' + ALEGE + optTara(null) + "</select></label>" +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Cod TVA furnizor</span><input id="d318-ffzvat" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:120px"><span class="camp-eticheta">Cod bun/serv.</span><input id="d318-fcod" type="text" class="camp-input" placeholder="1–10"></label>' +
      '<button class="buton-secundar" id="d318-add" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ factură</button>' +
    "</div>" +
    '<div id="d318-msg"></div>' +
    '<p class="camp-ajutor" style="margin-top:8px">Total TVA deductibil cerut la rambursare: <b>' + totalDed.toFixed(2) + "</b> " + esc(d.currency || "") +
      ". Pragul minim al cererii: 400 euro pe o perioadă mai scurtă de un an, 50 euro pe un an sau pe restul anului (HG 1/2016 pct.73 alin.(13)–(14)). Codul bunului / serviciului (1–10) e clasificarea statului de rambursare.</p>" +
    '<p style="margin-top:8px"><button class="buton-primar" id="d318-regen">' + _etRegen() + '</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveaza = () => {
    d.an = gv("#d318-an").value.trim();
    const ann = gv("#d318-annual"); d.annual = ann && ann.checked ? 1 : 0;
    const li = gv("#d318-li"), ls = gv("#d318-ls");
    if (li) d.luna_inceput = li.value.trim();
    if (ls) d.luna_sfarsit = ls.value.trim();
    d.refunding_country = gv("#d318-tara").value;
    d.cui = gv("#d318-cui").value.replace(/\s+/g, "");
    d.d_rec = parseInt(gv("#d318-drec").value, 10);   // [lotul 07.10 B] „inițială” vizibil = cazul uzual (DS cap.17), ca bifa „rectificativă” de la celelalte
    const ref = gv("#d318-ref"); if (ref) d.reference_number = ref.value.trim();
    d.iban = gv("#d318-iban").value.replace(/\s+/g, "").toUpperCase();
    d.bic = gv("#d318-bic").value.replace(/\s+/g, "").toUpperCase();
    d.owner_name = gv("#d318-owner").value.trim();
    d.owner_type = gv("#d318-ownt").value;
    d.currency = gv("#d318-cur").value.trim().toUpperCase();
    if (d.an && /^\d{4}$/.test(String(d.an))) S.an = parseInt(d.an, 10);   // [lotul 13, 638] anul cererii = anul declarației (titlul)
    d.sol_denumire = gv("#d318-soldenumire").value.trim();
    d.sol_strada = gv("#d318-solstrada").value.trim();
    d.sol_email = gv("#d318-solemail").value.trim();
    d.sol_cod = gv("#d318-solcod").value.trim();
    d.declarant = gv("#d318-declarant").value.trim();
    d.functie = gv("#d318-functie").value.trim();
    d.act_nace = gv("#d318-nace").value.trim();
    d.act_desc = gv("#d318-actdesc").value.trim();
  };
  gv("#d318-annual").addEventListener("change", () => { salveaza(); randeazaFormularD318(corp, nav); });
  gv("#d318-drec").addEventListener("change", () => { salveaza(); randeazaFormularD318(corp, nav); });
  ["#d318-an", "#d318-tara", "#d318-cui", "#d318-iban", "#d318-bic", "#d318-owner", "#d318-ownt", "#d318-cur",
   "#d318-soldenumire", "#d318-solstrada", "#d318-solemail", "#d318-solcod", "#d318-declarant", "#d318-functie",
   "#d318-nace", "#d318-actdesc"].forEach((id) => { const el = gv(id); if (el) el.addEventListener("change", salveaza); });
  ["#d318-li", "#d318-ls", "#d318-ref"].forEach((id) => { const el = gv(id); if (el) el.addEventListener("change", salveaza); });
  zona.querySelectorAll(".dec-d318-del").forEach((b) => b.addEventListener("click", () => { d.facturi.splice(parseInt(b.dataset.idx), 1); randeazaFormularD318(corp, nav); }));
  gv("#d318-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveaza();
    if (cereAlegerile(zona, ["#d318-fel", "#d318-ffztara"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    const nr = gv("#d318-fnr").value.trim(), data = gv("#d318-fdata").value.trim();
    const baza = _n(gv("#d318-fbaza").value) || 0, tva = _n(gv("#d318-ftva").value) || 0, ded = _n(gv("#d318-fded").value) || 0;
    const fz = gv("#d318-ffz").value.trim(), fzstr = gv("#d318-ffzstr").value.trim();
    const err = [];
    if (!nr) err.push(["d318-fnr", "Numărul facturii e obligatoriu."]);
    if (!/^\d{2}\.\d{2}\.\d{4}$/.test(data)) err.push(["d318-fdata", "Data facturii: dd.mm.aaaa (ex. 15.06.2025)."]);
    if (!(baza > 0)) err.push(["d318-fbaza", "Baza impozabilă trebuie > 0."]);
    if (Math.abs(tva) > Math.abs(baza)) err.push(["d318-ftva", "TVA nu poate depăși baza."]);
    if (!fz) err.push(["d318-ffz", "Denumirea furnizorului e obligatorie."]);
    if (!fzstr) err.push(["d318-ffzstr", "Adresa furnizorului e obligatorie."]);
    if (err.length) { err.forEach((x) => _eroareFormular(zona, x[0], x[1])); return; }
    d.facturi = d.facturi || [];
    d.facturi.push({
      fel: gv("#d318-fel").value, reference_number: nr, issuing_date: data,
      taxable_amount: baza, vat_amount: tva, deductible_vat: ded,
      fz_denumire: fz, fz_strada: fzstr, fz_tara: gv("#d318-ffztara").value,
      fz_vat: gv("#d318-ffzvat").value.trim(), cod_bun: gv("#d318-fcod").value.trim(),
    });
    randeazaFormularD318(corp, nav);
  });
  gv("#d318-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveaza();
    // [lotul 11, 440] toate lipsurile deodată (alegerile + câmpurile), apoi un singur `return`
    let faraAlegere = false; if (cereAlegerile(zona, ["#d318-tara", "#d318-ownt", "#d318-cur"])) faraAlegere = true;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    const err = [];
    // [lotul 07.10 B] moneda nu mai vine „EUR”: e a statului de rambursare (HG 1/2016 pct.73 alin.(6) lit.e) și o scrie omul
    if (!d.annual) {   // [lotul 13, 504] cererea pe o parte din an: lunile le scrie omul
      const li = parseInt(d.luna_inceput, 10), ls = parseInt(d.luna_sfarsit, 10);
      const luna = (x) => Number.isInteger(x) && x >= 1 && x <= 12;
      if (!luna(li)) err.push(["d318-li", "Scrie luna de început a perioadei (1–12)."]);
      if (!luna(ls)) err.push(["d318-ls", "Scrie luna de sfârșit a perioadei (1–12)."]);
      else if (luna(li) && ls < li) err.push(["d318-ls", "Luna de sfârșit nu poate fi înaintea lunii de început."]);
    }
    if (!(d.facturi || []).length) err.push([null, "Adaugă cel puțin o factură."]);
    if (err.length || faraAlegere) { err.forEach(([id, m]) => _eroareFormular(zona, id, m)); return; }
    regenereaza(corp, nav);
  });
}

// tip==="d212" (Declaratia unica, persoane fizice, anuala). Increment "proof-of-pattern": formularul
// strange IDENTITATEA (CNP/nume/adresa) si AFISEAZA fisa RIP (venit net + CAS/CASS + impozit din
// registrul de incasari/plati, ruta /rip/d212/{an}, informativ). Genereaza cazul MINIM DUK-valid
// (identitate + bife 0; totalPlata_A = suma cifrelor CNP). [D212 Etapa 2] Cu bifa „Include venitul din
// registrul RIP", serverul completeaza subsectiunea I.1.1 (sistem real) din registru (din_rip); impozitul si
// CAS/CASS si impozitul (oblig_realizat, sectiunile 3/4/7) le calculeaza serverul [D212 Etapa 4]. Valorile din memorie (S.d212).
// [D212 Etapa 3] Activitatile pe norma de venit (Subsectiunea a 2-a lit.A, cap12): lista de randuri (DS cap.24) —
// contabilul da norma DGRFP si datele activitatii; venitul net, cel impozabil si impozitul le calculeaza serverul.
function _d212Manual() {
  const d = S.d212 || {};
  const m = {
    cif: (d.cif || "").replace(/\s+/g, ""),
    nume_c: (d.nume_c || "").trim(),
    adresa_c: (d.adresa_c || "").trim(),
    d_rec: d.d_rec ? 1 : 0,
  };
  if (d.din_rip) {
    m.din_rip = true;
    m.pierdere_precedenta = Number(d.pierdere_precedenta || 0);
    if ((d.caen || "").trim()) m.caen = d.caen.trim();
    if (Number(d.nr_zile_scutite_rip) > 0) m.nr_zile_scutite_rip = Number(d.nr_zile_scutite_rip);
  }
  // [D212 Etapa 4] CAS/CASS și impozitul (oblig_realizat) le calculează serverul; de aici vin doar cele două alegeri
  // pe care evidența nu le poate ști: excepția de la baza minimă CASS (CF art.174 alin.(7)-(8)). Opțiunea CAS sub 12 sm
  // n-are căsuță în formularul validatorului instalat -> refuz pe server, deci nu se oferă aici.
  if (d.exceptie_minim_cass) m.exceptie_minim_cass = d.exceptie_minim_cass;
  if ((d.norma || []).length) {
    m.norma = d.norma.map((a) => ({
      caen: a.caen, sediu: a.sediu, nr_doc_autoriz: a.nr_doc_autoriz, data_doc_autoriz: a.data_doc_autoriz,
      forma_org: a.forma_org, norma: a.norma, norma_ajustata: a.norma_ajustata, data_incep: a.data_incep,
      data_sf: a.data_sf, zile_intrerupere: a.zile_intrerupere, nr_zile_scutite: a.nr_zile_scutite }));
  }
  // [D212 Etapa 5] veniturile fără date în aplicație (Subsecțiunea I.1.1 pe categorii): rândurile le calculează serverul
  if ((d.venituri || []).length) m.venituri = d.venituri.map((v) => Object.assign({}, v));
  // [D212 Etapa 5c] veniturile din străinătate (Secțiunea 2, cap14): câte o sursă pe țară; rândurile le calculează serverul
  if ((d.strainatate || []).length) m.strainatate = d.strainatate.map((v) => Object.assign({}, v));
  const ac = d.alte_cass || {};
  const alte = {};
  ["asociere_pj", "dividende_dobanzi", "cass_retinuta"].forEach((k) => { if (Number(ac[k]) > 0) alte[k] = Number(ac[k]); });
  if (Object.keys(alte).length) m.alte_cass = alte;
  return m;
}

// Categoriile introduse de contabil — codurile = `d212.CATEG_MANUALE` (gardate de test_d212_categorii); 1021-1024 =
// alte surse pe literele art.114 alin.(2) (D212Pdf Pdf_v5/v6).
const _D212_CATEG = [
  ["1016", "Activități independente (sistem real, din afara registrului)"],
  ["1003", "Drepturi de proprietate intelectuală"],
  ["1015", "Cedarea folosinței bunurilor (chirii)"],
  ["1006", "Închirierea în scop turistic a camerelor din locuința proprie"],
  ["1009", "Activități agricole (sistem real)"],
  ["1010", "Silvicultură (sistem real)"],
  ["1011", "Piscicultură (sistem real)"],
  ["1012", "Transferul titlurilor de valoare și alte operațiuni cu instrumente financiare"],
  ["1021", "Alte surse — art.114 alin.(2) lit.k^1 (creanțe ANRP)"],
  ["1022", "Alte surse — art.114 alin.(2) lit.l (cesiuni de creanță)"],
  ["1023", "Alte surse — art.114 alin.(2) lit.m (monedă virtuală)"],
  ["1024", "Alte surse — celelalte venituri din alte surse"],
];
// Categoriile din străinătate — codurile = `d212.CATEG_STRAINATATE` (gardate de test_d212_cap14).
const _D212_CATEG_STR = [
  ["2027", "Activități independente"], ["2003", "Drepturi de proprietate intelectuală"],
  ["2004", "Cedarea folosinței bunurilor"], ["2009", "Activități agricole"], ["2010", "Silvicultură"], ["2011", "Piscicultură"],
  ["2012", "Transferul titlurilor de valoare și alte operațiuni cu instrumente financiare"], ["2017", "Dobânzi"],
  ["2018", "Dividende"], ["2014", "Alte venituri"], ["2028", "Lichidarea unei persoane juridice"],
  ["2016", "Salarii plătite din România pentru activitatea desfășurată în străinătate"],
  ["2025", "Premii (câte un rând pe premiu)"], ["2013", "Jocuri de noroc (câte un rând pe venit primit)"],
  ["2029", "Transferul proprietăților imobiliare deținute cel mult 3 ani"],
  ["2030", "Transferul proprietăților imobiliare deținute mai mult de 3 ani"],
  ["2024", "Transferul proprietăților imobiliare cu titlu de moștenire"],
  ["2020", "Pensii"],
  ["2015", "Remunerații ale administratorilor, membrilor consiliului de administrație, cenzorilor și venituri similare"],
];
// Câmpurile fiecărei categorii din străinătate (instrucțiunile D212 pct.39.6); restul se ascund.
const _D212_STR_REAL = ["2027", "2009", "2010", "2011"];
const _D212_STR_TOATE = _D212_CATEG_STR.map((o) => o[0]);
const _D212_CAMP_STR = {
  "d212-s-det": ["2003"], "d212-s-brut": _D212_STR_TOATE.filter((c) => c !== "2012" && c !== "2016"),
  "d212-s-chelt": _D212_STR_REAL.concat(["2003", "2028", "2015"]), "d212-s-pp": _D212_STR_REAL.concat(["2003", "2012"]),
  "d212-s-castig": ["2012"], "d212-s-baza": ["2016"], "d212-s-tipjoc": ["2013"], "d212-s-dataplata": ["2013"],
  "d212-s-luni": ["2020"], "d212-s-lunicass": ["2020"],
  "d212-s-inc": _D212_STR_REAL.concat(["2003", "2004"]), "d212-s-sf": _D212_STR_REAL.concat(["2003", "2004"]),
};
// Ce câmpuri cere fiecare categorie (instrucțiunile D212, Subsecțiunea 1 pct.3-9); restul se ascund. 1016 = activitate
// independentă în sistem real din afara registrului (a doua activitate, altă formă de exercitare în același an).
const _D212_SISTEM_REAL = ["1016", "1009", "1010", "1011"];
const _D212_ALTE = ["1021", "1022", "1023", "1024"];
const _D212_CAMP_CAT = {
  "d212-v-det": ["1003"], "d212-v-faracota": ["1003"], "d212-v-forma": ["1003"].concat(_D212_SISTEM_REAL),
  "d212-v-caen": ["1003"].concat(_D212_SISTEM_REAL), "d212-v-scut": ["1003"].concat(_D212_SISTEM_REAL),
  "d212-v-sediu": ["1003", "1015", "1006"].concat(_D212_SISTEM_REAL), "d212-v-doc": ["1003", "1015", "1006"].concat(_D212_SISTEM_REAL),
  "d212-v-docdata": ["1003", "1015", "1006"].concat(_D212_SISTEM_REAL), "d212-v-inc": ["1003", "1015", "1006"].concat(_D212_SISTEM_REAL),
  "d212-v-sf": ["1003", "1015", "1006"].concat(_D212_SISTEM_REAL), "d212-v-brut": ["1003", "1015", "1006"].concat(_D212_SISTEM_REAL),
  "d212-v-chelt": ["1003", "1006"].concat(_D212_SISTEM_REAL), "d212-v-pp": ["1003", "1012"].concat(_D212_SISTEM_REAL),
  "d212-v-castig": ["1012"], "d212-v-vimp": _D212_ALTE,
};

// Excepțiile de la baza minimă CASS — cheile = `d212_engine.EXCEPTII_MINIM_CASS` (gardate de test_d212_oblig_realizat)
const _D212_EXCEPTII_CASS = [
  ["", "nicio excepție — CASS cel puțin la baza de 6 salarii minime"],
  ["salarii", "are salarii de cel puțin 6 salarii minime (art.174 alin.(7) lit.a)"],
  ["venituri_c_h", "are alte venituri (chirii, investiții etc.) cu CASS de cel puțin 6 salarii minime (alin.(7) lit.b)"],
  ["pensii", "are venituri din pensii (alin.(7) lit.c)"],
  ["exceptat_art154", "a fost exceptat de la CASS în anul precedent (art.154; alin.(8) lit.a)"],
  ["optiune_art180", "a optat pentru CASS în anul precedent (art.180; alin.(8) lit.b)"],
];
const _D212_FORMA_ORG = [["1", "individual"], ["2", "asociere fără personalitate juridică"]];

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
    // CF art.174 alin.(6): sub 6 salarii minime se datorează diferența până la baza minimă, afară de excepțiile alin.(7)-(8)
    const cassNota = f.cass && f.cass.diferenta_minim > 0
      ? " (din care " + bani(f.cass.diferenta_minim) + " lei diferența până la baza minimă de 6 salarii minime — nu se datorează dacă persoana are salarii, pensii sau alte venituri cu CASS de cel puțin 6 salarii minime; atunci CASS = " + bani(f.cass.cass_pe_venit) + " lei)"
      : "";
    blocFisa = '<div class="caseta-info">' +
      '<div class="ci-mesaj" style="font-weight:600;margin-bottom:6px">Fișa RIP ' + esc(String(f.an || S.an)) + " (informativ — din registrul de încasări/plăți)</div>" +
      '<div class="ecran-nota">Venit brut: <b>' + bani(f.venit_brut || 0) + "</b> · Cheltuieli deductibile: <b>" + bani(f.cheltuieli_deductibile || 0) + "</b> · Venit net: <b>" + bani(f.venit_net || 0) + "</b> lei<br>" +
      "CAS: <b>" + bani((f.cas || {}).cas || 0) + "</b> lei" + casNota + " · CASS: <b>" + bani((f.cass || {}).cass || 0) + "</b> lei" + cassNota + "<br>" +
      "Bază impozit: <b>" + bani(f.baza_impozit || 0) + "</b> · Impozit: <b>" + bani(f.impozit || 0) + "</b> lei</div>" +
      (f.avertisment ? '<div class="ecran-nota" style="margin-top:4px">' + esc(f.avertisment) + "</div>" : "") +
      '<div class="ecran-nota" style="margin-top:6px">Cifrele vin din registrul firmei. Cu „Include venitul din registrul RIP", venitul brut, cheltuielile și venitul net intră în subsecțiunea I.1.1 (sistem real); CAS, CASS și impozitul se calculează la generare, în secțiunile 3, 4 și 7.</div>' +
      "</div>";
  } else {
    blocFisa = '<div class="stare-goala stare-goala--inline">Apasă „Trage fișa RIP" ca să vezi venitul net și contribuțiile calculate din registrul de încasări/plăți al firmei, pentru anul ales.</div>';
  }
  const norme = d.norma || [];
  const randuriNorma = norme.length
    ? norme.map((a, i) => '<div class="dec-man-rand">' +
        '<span class="dec-recl-desc">Activitatea ' + (i + 1) + (a.caen ? " · CAEN " + esc(a.caen) : "") +
        (a.sediu ? " · " + esc(a.sediu) : "") + " · normă " + bani(_n(a.norma)) + " lei" +
        (a.norma_ajustata !== "" && a.norma_ajustata != null ? " · ajustată " + bani(_n(a.norma_ajustata)) + " lei" : "") +
        (a.data_incep ? " · început " + esc(a.data_incep) : "") + (a.data_sf ? " · încetare " + esc(a.data_sf) : "") +
        (Number(a.zile_intrerupere) ? " · " + esc(cate(a.zile_intrerupere, "zi de întrerupere", "zile de întrerupere")) : "") +
        (Number(a.nr_zile_scutite) ? " · " + esc(cate(a.nr_zile_scutite, "zi scutită", "zile scutite")) : "") + "</span>" +
        '<button class="buton-sters d212-n-del" data-idx="' + i + '" aria-label="Șterge activitatea ' + (i + 1) + '">Șterge</button></div>').join("")
    : '<div class="stare-goala stare-goala--inline">Nicio activitate pe normă. Dacă persoana a avut venituri impuse pe normă de venit, adaugă fiecare activitate (fiecare loc) mai jos.</div>';
  const optForma = _D212_FORMA_ORG.map((o) => '<option value="' + o[0] + '">' + esc(o[1]) + "</option>").join("");
  const optExc = _D212_EXCEPTII_CASS.map((o) => '<option value="' + o[0] + '"' + (d.exceptie_minim_cass === o[0] ? " selected" : "") + ">" + esc(o[1]) + "</option>").join("");
  const ac = d.alte_cass || {};
  const blocContributii = '<div class="camp-eticheta" style="margin:14px 0 4px">Contribuții și impozit (secțiunile 3, 4 și 7 — calculate din veniturile de mai sus)</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">' +
      '<label class="camp" style="flex:1 1 320px"><span class="camp-eticheta">Excepție de la baza minimă CASS (venit sub 6 salarii minime)</span><select id="d212-exccass" class="camp-input">' + (d.exceptie_minim_cass === undefined || d.exceptie_minim_cass === null ? ALEGE : "") + optExc + "</select></label>" +
      '<label class="camp" style="width:230px"><span class="camp-eticheta">Venit distribuit din asocieri cu persoane juridice (lei)</span><input id="d212-c-asc" type="number" min="0" step="1" class="camp-input" value="' + esc(String(ac.asociere_pj || "")) + '"></label>' +
      '<label class="camp" style="width:230px"><span class="camp-eticheta">Dividende și dobânzi încasate, nete de impozit (lei)</span><input id="d212-c-div" type="number" min="0" step="1" class="camp-input" value="' + esc(String(ac.dividende_dobanzi || "")) + '"></label>' +
      '<label class="camp" style="width:230px"><span class="camp-eticheta">CASS reținută de plătitori pe aceste venituri (lei)</span><input id="d212-c-ret" type="number" min="0" step="1" class="camp-input" value="' + esc(String(ac.cass_retinuta || "")) + '"></label>' +
    "</div>" +
    '<p class="camp-ajutor" style="margin:4px 0 0">CASS pe drepturile de proprietate intelectuală, chirii, investiții, activități agricole și alte surse se datorează pe trepte: baza e 6, 12 sau 24 de salarii minime, după cât au însumat aceste venituri (sub 6 salarii minime nu se datorează). Dividendele, dobânzile și venitul din asocieri cu persoane juridice nu au secțiune proprie în declarație, dar intră în calculul treptei — de aceea se scriu aici.</p>';
  const blocNorma = '<div class="camp-eticheta" style="margin:14px 0 4px">Venit pe normă de venit — activități independente (subsecțiunea I.1.2)</div>' +
    randuriNorma +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-top:6px">' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Cod CAEN</span><input id="d212-n-caen" type="text" maxlength="4" class="camp-input"></label>' +
      '<label class="camp" style="flex:1 1 220px"><span class="camp-eticheta">Sediul / locul activității</span><input id="d212-n-sediu" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Nr. document autorizare</span><input id="d212-n-doc" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Data documentului</span><input id="d212-n-docdata" type="date" class="camp-input"></label>' +
      '<label class="camp" style="width:220px"><span class="camp-eticheta">Forma de organizare</span><select id="d212-n-forma" class="camp-input">' + ALEGE + optForma + "</select></label>" +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-top:6px">' +
      '<label class="camp" style="width:190px"><span class="camp-eticheta">Norma anuală de venit (lei) <span class="oblig">*</span></span><input id="d212-n-norma" type="number" min="0" step="1" class="camp-input"></label>' +
      '<label class="camp" style="width:190px"><span class="camp-eticheta">Norma ajustată (lei)</span><input id="d212-n-ajust" type="number" min="0" step="1" class="camp-input"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Data începerii (în an)</span><input id="d212-n-inc" type="date" class="camp-input"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Data încetării (în an)</span><input id="d212-n-sf" type="date" class="camp-input"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Zile de întrerupere</span><input id="d212-n-intr" type="number" min="0" step="1" class="camp-input"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Zile scutite</span><input id="d212-n-scut" type="number" min="0" step="1" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d212-n-add" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ adaugă activitatea</button>' +
    "</div>" +
    '<p class="camp-ajutor" style="margin:4px 0 0">Norma e cea publicată de direcția regională pentru locul activității; norma ajustată, dacă s-au aplicat coeficienți de corecție. Data începerii/încetării și zilele de întrerupere se completează doar când activitatea n-a durat tot anul — venitul net se calculează proporțional, pe 365 de zile; impozitul e 10% din venitul impozabil. Zilele scutite = zilele în care persoana a fost scutită de impozit (handicap grav sau accentuat).</p>';
  const etCat = (c) => ((_D212_CATEG.find((o) => o[0] === String(c)) || [])[1]) || String(c);
  const venituri = d.venituri || [];
  const randuriVenit = venituri.length
    ? venituri.map((v, i) => '<div class="dec-man-rand">' +
        '<span class="dec-recl-desc">Venitul ' + (i + 1) + " · " + esc(etCat(v.categ_venit)) +
        (String(v.categ_venit) === "1003" ? (String(v.det_ven_net) === "1" ? " · sistem real" : " · cote forfetare") : "") +
        (v.venit_brut !== "" && v.venit_brut != null ? " · venit brut " + bani(_n(v.venit_brut)) + " lei" : "") +
        (v.chelt_deduc !== "" && v.chelt_deduc != null ? " · cheltuieli " + bani(_n(v.chelt_deduc)) + " lei" : "") +
        (v.castig_net !== "" && v.castig_net != null ? " · câștig net " + bani(_n(v.castig_net)) + " lei" : "") +
        (v.venit_impozabil !== "" && v.venit_impozabil != null ? " · venit impozabil " + bani(_n(v.venit_impozabil)) + " lei" : "") +
        (Number(v.pierdere_precedenta) ? " · pierderi reportate " + bani(_n(v.pierdere_precedenta)) + " lei" : "") +
        (v.sediu ? " · " + esc(v.sediu) : "") + (Number(v.nr_zile_scutite) ? " · " + esc(cate(v.nr_zile_scutite, "zi scutită", "zile scutite")) : "") + "</span>" +
        '<button class="buton-sters d212-v-del" data-idx="' + i + '" aria-label="Șterge venitul ' + (i + 1) + '">Șterge</button></div>').join("")
    : '<div class="stare-goala stare-goala--inline">Niciun alt venit. Dacă persoana a avut și venituri din drepturi de autor, chirii, investiții, activități agricole, alte surse sau o altă activitate independentă ținută în afara registrului acestei firme, adaugă fiecare sursă mai jos.</div>';
  const optCat = _D212_CATEG.map((o) => '<option value="' + o[0] + '">' + esc(o[1]) + "</option>").join("");
  const blocVenituri = '<div class="camp-eticheta" style="margin:14px 0 4px">Alte venituri ale persoanei — din România (subsecțiunea I.1.1, câte o sursă)</div>' +
    randuriVenit +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-top:6px">' +
      '<label class="camp" style="flex:1 1 320px"><span class="camp-eticheta">Categoria de venit <span class="oblig">*</span></span><select id="d212-v-cat" class="camp-input">' + ALEGE + optCat + "</select></label>" +
      '<label class="camp" style="width:220px"><span class="camp-eticheta">Determinarea venitului net</span><select id="d212-v-det" class="camp-input" data-butoane="">' + ALEGE + '<option value="2">cote forfetare de cheltuieli</option><option value="1">sistem real (contabilitate)</option></select></label>' +
      '<label class="camp" style="width:300px"><span class="camp-eticheta">Moștenitor / drept de suită — fără cota forfetară <span class="oblig">*</span></span>' + selectDaNu('id="d212-v-faracota"', null, "Moștenitor / drept de suită — fără cota forfetară") + "</label>" +
      '<label class="camp" style="width:220px"><span class="camp-eticheta">Forma de organizare</span><select id="d212-v-forma" class="camp-input">' + ALEGE + optForma + "</select></label>" +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Cod CAEN</span><input id="d212-v-caen" type="text" maxlength="4" class="camp-input"></label>' +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-top:6px">' +
      '<label class="camp" style="flex:1 1 260px"><span class="camp-eticheta">Sediul / bunul (adresa, nr. de înmatriculare etc.)</span><input id="d212-v-sediu" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Nr. contract / document</span><input id="d212-v-doc" type="text" class="camp-input"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Data contractului / documentului</span><input id="d212-v-docdata" type="date" class="camp-input"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Data începerii (în an)</span><input id="d212-v-inc" type="date" class="camp-input"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Data încetării (în an)</span><input id="d212-v-sf" type="date" class="camp-input"></label>' +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-top:6px">' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Venit brut (lei)</span><input id="d212-v-brut" type="number" min="0" step="1" class="camp-input"></label>' +
      '<label class="camp" style="width:200px"><span class="camp-eticheta">Cheltuieli deductibile (lei)</span><input id="d212-v-chelt" type="number" min="0" step="1" class="camp-input"></label>' +
      '<label class="camp" style="width:200px"><span class="camp-eticheta">Pierderi reportate din anii precedenți (lei)</span><input id="d212-v-pp" type="number" min="0" step="1" class="camp-input"></label>' +
      '<label class="camp" style="width:200px"><span class="camp-eticheta">Câștig net anual (pierderea cu minus)</span><input id="d212-v-castig" type="number" step="1" class="camp-input"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Venit impozabil (lei)</span><input id="d212-v-vimp" type="number" min="0" step="1" class="camp-input"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Zile scutite (handicap)</span><input id="d212-v-scut" type="number" min="0" step="1" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d212-v-add" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ adaugă venitul</button>' +
    "</div>" +
    '<p class="camp-ajutor" style="margin:4px 0 0">Se arată doar câmpurile categoriei alese. Cheltuielile la cote forfetare le calculează aplicația (40% la drepturile de autor, 20% la chirii) — se scriu doar în sistem real sau, la moștenitori și dreptul de suită, sumele cuvenite organismelor de gestiune colectivă. La investiții se scrie câștigul net al anului, iar la alte surse venitul impozabil. Impozitul (10%) și CASS se calculează la generare. Regulile sunt cele pentru veniturile 2025.</p>';
  const etStr = (c) => ((_D212_CATEG_STR.find((o) => o[0] === String(c)) || [])[1]) || String(c);
  const etMetoda = { "1": "creditul fiscal", "2": "scutirea", "4": "scutit prin acord internațional" };
  const str = d.strainatate || [];
  const randuriStr = str.length
    ? str.map((v, i) => '<div class="dec-man-rand">' +
        '<span class="dec-recl-desc">Străinătate ' + (i + 1) + " · " + esc(String(v.tara || "")) + " · " + esc(etStr(v.categ_venit)) +
        (v.dubla_impunere ? " · " + esc(etMetoda[String(v.dubla_impunere)] || "") : "") +
        (v.venit_brut !== "" && v.venit_brut != null ? " · venit brut " + bani(_n(v.venit_brut)) + " lei" : "") +
        (v.castig_net !== "" && v.castig_net != null ? " · câștig net " + bani(_n(v.castig_net)) + " lei" : "") +
        (v.venit_baza !== "" && v.venit_baza != null ? " · venit bază de calcul " + bani(_n(v.venit_baza)) + " lei" : "") +
        (Number(v.impozit_platit) ? " · impozit plătit acolo " + bani(_n(v.impozit_platit)) + " lei" : "") +
        (v.fara_contributii ? " · fără CAS/CASS în România" : "") + "</span>" +
        '<button class="buton-sters d212-s-del" data-idx="' + i + '" aria-label="Șterge venitul din străinătate ' + (i + 1) + '">Șterge</button></div>').join("")
    : '<div class="stare-goala stare-goala--inline">Niciun venit din străinătate. Dacă persoana a avut venituri din alte țări, adaugă fiecare sursă (o țară, o categorie) mai jos.</div>';
  const optStr = _D212_CATEG_STR.map((o) => '<option value="' + o[0] + '">' + esc(o[1]) + "</option>").join("");
  const blocStrainatate = '<div class="camp-eticheta" style="margin:14px 0 4px">Venituri din străinătate (secțiunea I.2.1, câte o țară și o sursă)</div>' +
    randuriStr +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-top:6px">' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Țara (cod, ex. DE) <span class="oblig">*</span></span><input id="d212-s-tara" type="text" maxlength="2" class="camp-input"></label>' +
      '<label class="camp" style="flex:1 1 300px"><span class="camp-eticheta">Categoria de venit <span class="oblig">*</span></span><select id="d212-s-cat" class="camp-input">' + ALEGE + optStr + "</select></label>" +
      '<label class="camp" style="width:240px"><span class="camp-eticheta">Evitarea dublei impuneri</span><select id="d212-s-metoda" class="camp-input" data-butoane=""><option value="">fără convenție aplicată</option><option value="1">metoda creditului fiscal</option><option value="2">metoda scutirii</option><option value="4">venit scutit prin acord internațional</option></select></label>' +
      '<label class="camp" style="width:220px"><span class="camp-eticheta">Determinarea venitului net</span><select id="d212-s-det" class="camp-input" data-butoane="">' + ALEGE + '<option value="2">cote forfetare de cheltuieli</option><option value="1">sistem real (contabilitate)</option></select></label>' +
      '<label class="camp" style="width:300px"><span class="camp-eticheta">Fără CAS/CASS în România (asigurat în alt stat) <span class="oblig">*</span></span>' + selectDaNu('id="d212-s-faracontrib"', null, "Fără CAS/CASS în România") + "</label>" +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-top:6px">' +
      '<label class="camp" style="width:200px"><span class="camp-eticheta">Venit brut / valoarea tranzacției (lei)</span><input id="d212-s-brut" type="number" min="0" step="1" class="camp-input"></label>' +
      '<label class="camp" style="width:240px"><span class="camp-eticheta">Felul jocului</span><select id="d212-s-tipjoc" class="camp-input" data-butoane="">' + ALEGE + '<option value="cazinou">cazinou, poker, slot-machine, lozuri</option><option value="altele">alte jocuri de noroc</option></select></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Data plății</span><input id="d212-s-dataplata" type="date" class="camp-input"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Luni cu pensie în an</span><input id="d212-s-luni" type="number" min="1" max="12" step="1" class="camp-input"></label>' +
      '<label class="camp" style="width:240px"><span class="camp-eticheta">Luni august–decembrie cu CASS în România</span><input id="d212-s-lunicass" type="number" min="0" max="5" step="1" class="camp-input"></label>' +
      '<label class="camp" style="width:200px"><span class="camp-eticheta">Cheltuieli / sume deductibile (lei)</span><input id="d212-s-chelt" type="number" min="0" step="1" class="camp-input"></label>' +
      '<label class="camp" style="width:200px"><span class="camp-eticheta">Câștig net anual (pierderea cu minus)</span><input id="d212-s-castig" type="number" step="1" class="camp-input"></label>' +
      '<label class="camp" style="width:200px"><span class="camp-eticheta">Venit bază de calcul (lei)</span><input id="d212-s-baza" type="number" min="0" step="1" class="camp-input"></label>' +
      '<label class="camp" style="width:200px"><span class="camp-eticheta">Pierderi reportate din anii precedenți (lei)</span><input id="d212-s-pp" type="number" min="0" step="1" class="camp-input"></label>' +
      '<label class="camp" style="width:200px"><span class="camp-eticheta">Impozit plătit în străinătate (lei)</span><input id="d212-s-platit" type="number" min="0" step="1" class="camp-input"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Data începerii (în an)</span><input id="d212-s-inc" type="date" class="camp-input"></label>' +
      '<label class="camp" style="width:170px"><span class="camp-eticheta">Data încetării (în an)</span><input id="d212-s-sf" type="date" class="camp-input"></label>' +
      '<button class="buton-secundar" id="d212-s-add" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ adaugă venitul din străinătate</button>' +
    "</div>" +
    '<p class="camp-ajutor" style="margin:4px 0 0">Sumele se scriu în lei, la cursul mediu anual BNR al anului. Se arată doar câmpurile categoriei alese. Impozitul în România se calculează cu cota categoriei; la metoda creditului fiscal, impozitul plătit în străinătate se scade, dar cel mult până la impozitul român; la metoda scutirii sau la venitul scutit prin acord, impozitul în România e zero. Salariile plătite din România: venitul bază de calcul din documentul angajatorului. Premiile: suma neimpozabilă de 600 lei pe premiu se scade singură. Jocurile de noroc: baremul se alege după data plății (altul de la 1 august 2025); la cazinouri, poker, slot-machine și lozuri primii 66.750 lei din fiecare plată nu se impozitează. Pensiile: venitul brut al anului și numărul lunilor cu pensie — suma neimpozabilă de 3.000 lei pe lună se scade singură; dacă de la august 2025 persoana datorează CASS în România pe pensie, aplicația refuză (formularul ANAF instalat n-are încă secțiunea). Remunerațiile de administrator, cenzor și similare: CAS și CASS datorate în România se calculează; pentru un asigurat în alt stat se bifează „Fără CAS/CASS în România” și se scriu la contribuții cele plătite acolo. Transferul unei proprietăți: valoarea tranzacției; moștenirea: valoarea masei succesorale, doar dacă succesiunea nu s-a finalizat în 2 ani. Veniturile din străinătate intră și în CAS și CASS, afară de cazul în care persoana e asigurată în alt stat (legislația europeană sau un acord de securitate socială) — atunci bifează „Fără CAS/CASS în România”. Regulile sunt cele pentru veniturile 2025.</p>';
  zona.innerHTML = '<details class="dec-xml" open><summary>Declarația unică — persoană fizică (identificare + fișa RIP)</summary>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:180px"><span class="camp-eticheta">CNP contribuabil <span class="oblig">*</span></span><input id="d212-cnp" type="text" maxlength="13" class="camp-input" value="' + esc(d.cif || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 220px"><span class="camp-eticheta">Nume și prenume <span class="oblig">*</span></span><input id="d212-nume" type="text" class="camp-input" value="' + esc(d.nume_c || "") + '"></label>' +
      '<label class="camp" style="flex:1 1 260px"><span class="camp-eticheta">Adresa <span class="oblig">*</span></span><input id="d212-adr" type="text" class="camp-input" value="' + esc(d.adresa_c || "") + '"></label>' +
      '<label class="set-bifa"><input id="d212-rec" type="checkbox" ' + (d.d_rec ? "checked" : "") + '> <span>Rectificativă</span></label>' +
    "</div>" +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:8px">' +
      '<label class="camp" style="width:330px"><span class="camp-eticheta">Include venitul din registrul RIP (subsecțiunea I.1.1, sistem real) <span class="oblig">*</span></span>' + selectDaNu('id="d212-rip"', d.din_rip, "Include venitul din registrul RIP") + "</label>" +
      '<label class="camp" style="width:240px"><span class="camp-eticheta">Pierderi fiscale reportate din anii precedenți (lei)</span><input id="d212-pp" type="number" min="0" step="1" class="camp-input" value="' + esc(String(d.pierdere_precedenta || "")) + '"></label>' +
      '<label class="camp" style="width:130px"><span class="camp-eticheta">Cod CAEN</span><input id="d212-caen" type="text" maxlength="4" class="camp-input" value="' + esc(d.caen || "") + '"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Zile scutite (handicap)</span><input id="d212-scut" type="number" min="0" step="1" class="camp-input" value="' + esc(String(d.nr_zile_scutite_rip || "")) + '"></label>' +
    "</div>" +
    '<p style="margin:4px 0 8px"><button class="buton-secundar" id="d212-fisa">Trage fișa RIP ' + esc(String(S.an)) + "</button></p>" +
    blocFisa +
    blocNorma +
    blocVenituri +
    blocStrainatate +
    blocContributii +
    '<p style="margin-top:10px"><button class="buton-primar" id="d212-regen">' + _etRegen() + '</button>' +
      '<span class="ecran-nota" style="margin-left:8px">după modificări, regenerează pentru a revalida.</span></p>' +
  "</details>";
  const gv = (id) => zona.querySelector(id);
  const salveazaAntet = () => {
    S.d212.cif = gv("#d212-cnp").value.trim();
    S.d212.nume_c = gv("#d212-nume").value.trim();
    S.d212.adresa_c = gv("#d212-adr").value.trim();
    S.d212.d_rec = gv("#d212-rec").checked ? 1 : 0;
    { const v = daNu(gv("#d212-rip")); S.d212.din_rip = v === null ? null : (v ? 1 : 0); }
    S.d212.pierdere_precedenta = gv("#d212-pp").value.trim();
    S.d212.caen = gv("#d212-caen").value.trim();
    S.d212.exceptie_minim_cass = gv("#d212-exccass").value;
    S.d212.nr_zile_scutite_rip = gv("#d212-scut").value.trim();
    S.d212.alte_cass = { asociere_pj: gv("#d212-c-asc").value.trim(), dividende_dobanzi: gv("#d212-c-div").value.trim(),
      cass_retinuta: gv("#d212-c-ret").value.trim() };
  };
  ["#d212-cnp", "#d212-nume", "#d212-adr", "#d212-pp", "#d212-caen", "#d212-scut", "#d212-c-asc", "#d212-c-div", "#d212-c-ret"].forEach((id) => gv(id).addEventListener("change", salveazaAntet));
  // câmpurile categoriei alese (restul ascunse — nu se trimit)
  const arataCampuriVenit = () => {
    const cat = gv("#d212-v-cat").value;
    Object.keys(_D212_CAMP_CAT).forEach((id) => {
      const el = gv("#" + id);
      const camp = el && el.closest("label");
      if (camp) camp.style.display = _D212_CAMP_CAT[id].includes(cat) ? "" : "none";   // .camp are display:flex — `hidden` n-ar ascunde
    });
  };
  gv("#d212-v-cat").addEventListener("change", arataCampuriVenit);
  arataCampuriVenit();
  const arataCampuriStr = () => {
    const cat = gv("#d212-s-cat").value;
    Object.keys(_D212_CAMP_STR).forEach((id) => {
      const camp = gv("#" + id) && gv("#" + id).closest("label");
      if (camp) camp.style.display = _D212_CAMP_STR[id].includes(cat) ? "" : "none";   // .camp are display:flex
    });
  };
  gv("#d212-s-cat").addEventListener("change", arataCampuriStr);
  arataCampuriStr();
  zona.querySelectorAll(".d212-s-del").forEach((b) => b.addEventListener("click", () => {
    salveazaAntet();
    S.d212.strainatate.splice(parseInt(b.dataset.idx, 10), 1);
    randeazaFormularD212(corp, nav);
  }));
  gv("#d212-s-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveazaAntet();
    if (cereAlegerile(zona, ["#d212-s-cat", "#d212-s-det", "#d212-s-tipjoc", "#d212-s-faracontrib"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    const tara = gv("#d212-s-tara").value.trim().toUpperCase();
    if (!/^[A-Z]{2}$/.test(tara)) {
      eroareCamp(zona, "d212-s-tara", "Scrie codul țării din două litere (ex. DE pentru Germania, AT pentru Austria; Grecia = EL).");
      return;
    }
    const cat = gv("#d212-s-cat").value;
    const v = { tara: tara, categ_venit: cat };
    const metoda = gv("#d212-s-metoda").value;
    if (metoda) v.dubla_impunere = metoda;
    const ia = { "d212-s-det": "det_ven_net", "d212-s-brut": "venit_brut", "d212-s-chelt": "chelt_deduc",
      "d212-s-castig": "castig_net", "d212-s-baza": "venit_baza", "d212-s-pp": "pierdere_precedenta",
      "d212-s-inc": "data_incep", "d212-s-sf": "data_sf", "d212-s-tipjoc": "tip_joc", "d212-s-dataplata": "data_plata",
      "d212-s-luni": "nr_luni", "d212-s-lunicass": "luni_cass_ro" };
    Object.keys(ia).forEach((id) => {
      if (!_D212_CAMP_STR[id].includes(cat)) return;
      const val = gv("#" + id).value.trim();
      if (val !== "") v[ia[id]] = val;
    });
    const platit = gv("#d212-s-platit").value.trim();
    if (platit !== "") v.impozit_platit = platit;
    if (daNu(gv("#d212-s-faracontrib")) === true) v.fara_contributii = true;
    S.d212.strainatate = S.d212.strainatate || [];
    S.d212.strainatate.push(v);
    randeazaFormularD212(corp, nav);
  });
  zona.querySelectorAll(".d212-v-del").forEach((b) => b.addEventListener("click", () => {
    salveazaAntet();
    S.d212.venituri.splice(parseInt(b.dataset.idx, 10), 1);
    randeazaFormularD212(corp, nav);
  }));
  gv("#d212-v-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveazaAntet();
    if (cereAlegerile(zona, ["#d212-v-cat", "#d212-v-det", "#d212-v-forma", "#d212-v-faracota"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    const cat = gv("#d212-v-cat").value;
    const v = { categ_venit: cat };
    const ia = { "d212-v-det": "det_ven_net", "d212-v-forma": "forma_org", "d212-v-caen": "caen", "d212-v-sediu": "sediu",
      "d212-v-doc": "nr_doc", "d212-v-docdata": "data_doc", "d212-v-inc": "data_incep", "d212-v-sf": "data_sf",
      "d212-v-brut": "venit_brut", "d212-v-chelt": "chelt_deduc", "d212-v-pp": "pierdere_precedenta",
      "d212-v-castig": "castig_net", "d212-v-vimp": "venit_impozabil", "d212-v-scut": "nr_zile_scutite" };
    Object.keys(ia).forEach((id) => {
      if (!_D212_CAMP_CAT[id].includes(cat)) return;
      const val = gv("#" + id).value.trim();
      if (val !== "") v[ia[id]] = val;
    });
    if (_D212_CAMP_CAT["d212-v-faracota"].includes(cat) && daNu(gv("#d212-v-faracota")) === true) v.fara_cota_forfetara = true;
    S.d212.venituri = S.d212.venituri || [];
    S.d212.venituri.push(v);
    randeazaFormularD212(corp, nav);
  });
  ["#d212-rec", "#d212-rip", "#d212-exccass"].forEach((id) => gv(id).addEventListener("change", salveazaAntet));
  zona.querySelectorAll(".d212-n-del").forEach((b) => b.addEventListener("click", () => {
    salveazaAntet();
    S.d212.norma.splice(parseInt(b.dataset.idx, 10), 1);
    randeazaFormularD212(corp, nav);
  }));
  gv("#d212-n-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    salveazaAntet();
    if (cereAlegerile(zona, ["#d212-n-forma"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    const norma = gv("#d212-n-norma").value.trim();
    if (!(Number(norma) > 0)) {
      eroareCamp(zona, "d212-n-norma", "Completează norma anuală de venit (în lei) — cea din lista direcției regionale pentru locul activității.");
      return;
    }
    S.d212.norma = S.d212.norma || [];
    S.d212.norma.push({ caen: gv("#d212-n-caen").value.trim(), sediu: gv("#d212-n-sediu").value.trim(),
      nr_doc_autoriz: gv("#d212-n-doc").value.trim(), data_doc_autoriz: gv("#d212-n-docdata").value,
      forma_org: gv("#d212-n-forma").value, norma: norma, norma_ajustata: gv("#d212-n-ajust").value.trim(),
      data_incep: gv("#d212-n-inc").value, data_sf: gv("#d212-n-sf").value,
      zile_intrerupere: gv("#d212-n-intr").value.trim(), nr_zile_scutite: gv("#d212-n-scut").value.trim() });
    randeazaFormularD212(corp, nav);
  });
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
    if (cereAlegerile(zona, ["#d212-exccass", "#d212-rip"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    if (!S.d212.cif || !S.d212.nume_c || !S.d212.adresa_c) {
      eroareCamp(zona, "d212-cnp", "Completează CNP, nume și adresă — D212 nu se poate genera fără identificarea persoanei fizice.");
      return;
    }
    if (S.d212.din_rip && S.d212.pierdere_precedenta !== "" && !(Number(S.d212.pierdere_precedenta) >= 0)) {
      eroareCamp(zona, "d212-pp", "Pierderea reportată se scrie în lei, ca număr pozitiv (sau lasă câmpul gol dacă nu există).");
      return;
    }
    if (S.d212.din_rip && S.d212.caen && !/^\d{4}$/.test(S.d212.caen)) {
      eroareCamp(zona, "d212-caen", "Codul CAEN are 4 cifre (ex. 6201).");
      return;
    }
    regenereaza(corp, nav);
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

// [lotul 10, decizia Costin B: „Da, cu completare manuală”] D205 cu beneficiarii scriși de contabil. Cazul: firma preluată, cu dividende
// plătite înainte de preluare (debitul 457 din balanța de deschidere): notele lor nu sunt în iConta.eu, deci nici împărțirea pe asociați.
// Coloanele urmează instrucțiunile D205 (OPANAF 179/2022, cap.II pct.9): col.3 dividendul distribuit, col.4 plătit, col.5 baza, col.6
// impozitul. Lista goală = D205 din notele validate. Deschis după un refuz (sau cu rânduri scrise), altfel pliat.
function _d205Manual() {
  // sumele ca NUMERE (câmpul gol = 0): serverul le rotunjește aritmetic (`d205._i`), un text gol nu e o sumă
  return { beneficiari: (S.d205.beneficiari || []).map((b) => ({ categ: "1.a", nume: b.nume, cif: b.cif, divid_d: _n(b.divid_d),
    divid_p: _n(b.divid_p), baza: _n(b.baza), imp: _n(b.imp) })) };
}

function randeazaFormularD205(corp, nav, deschis) {
  const zona = corp.querySelector("#dec-d205-form");
  if (!zona) return;
  const benef = S.d205.beneficiari || [];
  const tot = (k) => benef.reduce((a, b) => a + Math.round(_n(b[k]) || 0), 0);
  const grila = benef.length
    ? benef.map((b, i) => '<div class="dec-man-rand"><span class="dec-recl-desc">' + esc(b.nume) + ' · CNP ' + esc(b.cif) +
        ' · distribuit ' + bani(_n(b.divid_d)) + ' · plătit ' + bani(_n(b.divid_p)) + ' · bază ' + bani(_n(b.baza)) +
        ' · impozit ' + bani(_n(b.imp)) + ' lei</span><button class="btn-link dec-d205-del" data-idx="' + i + '">șterge</button></div>').join("")
    : '<div class="stare-goala stare-goala--inline">Niciun beneficiar scris de mână: D205 se face din notele de dividende validate. ' +
      'Completează beneficiarii aici numai când notele nu-i au (de exemplu, dividendele plătite înainte de preluarea firmei).</div>';
  const camp = (id, et, lat, tip) => '<label class="camp" style="' + lat + '"><span class="camp-eticheta">' + et + '</span>' +
    '<input id="' + id + '" type="' + (tip || "number") + '"' + (tip ? "" : ' step="1" min="0"') + ' class="camp-input"></label>';
  zona.innerHTML = '<details class="dec-xml"' + (deschis || benef.length ? " open" : "") + '><summary>Beneficiari completați manual (' + benef.length + ')</summary>' +
    grila +
    '<div class="camp-eticheta" style="margin:12px 0 4px">Adaugă beneficiar (asociat):</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-end;gap:10px">' +
      camp("d205-nume", 'Nume și prenume <span class="oblig">*</span>', "flex:1 1 220px", "text") +
      camp("d205-cif", 'CNP <span class="oblig">*</span>', "width:170px", "text") +
      camp("d205-divd", "Dividende distribuite (lei)", "width:170px") +
      camp("d205-divp", "Dividende plătite (lei)", "width:170px") +
      camp("d205-baza", "Baza impozitului (lei)", "width:160px") +
      camp("d205-imp", "Impozit reținut (lei)", "width:160px") +
      '<button class="buton-secundar" id="d205-add" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ adaugă</button>' +
    '</div><div id="d205-msg"></div>' +
    '<p class="camp-ajutor" style="margin-top:8px">' + cate(benef.length, "beneficiar", "beneficiari") + ' · distribuit <b>' + bani(tot("divid_d")) + '</b> · plătit <b>' +
      bani(tot("divid_p")) + '</b> · bază <b>' + bani(tot("baza")) + '</b> · impozit <b>' + bani(tot("imp")) + '</b> lei (Cod fiscal art.97 alin.(7)).</p>' +
    '<p style="margin-top:8px"><button class="buton-primar" id="d205-regen">Regenerează D205</button></p></details>';
  const gv = (id) => zona.querySelector(id);
  zona.querySelectorAll(".dec-d205-del").forEach((b) => b.addEventListener("click", () => {
    S.d205.beneficiari.splice(parseInt(b.dataset.idx, 10), 1); randeazaFormularD205(corp, nav, true);
  }));
  gv("#d205-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    const nume = gv("#d205-nume").value.trim(), cif = gv("#d205-cif").value.trim();
    const err = [];
    if (!nume) err.push(["d205-nume", "Completează numele asociatului."]);
    if (!/^\d{13}$/.test(cif)) err.push(["d205-cif", "Completează CNP-ul asociatului (13 cifre)."]);
    if (!["#d205-divd", "#d205-divp", "#d205-baza", "#d205-imp"].some((s) => _n(gv(s).value) > 0))
      err.push(["d205-divd", "Completează cel puțin o sumă: dividendele distribuite, plătite, baza sau impozitul."]);
    if (err.length) { err.forEach(([id, m]) => _eroareFormular(zona, id, m)); return; }
    S.d205.beneficiari.push({ nume: nume, cif: cif, divid_d: gv("#d205-divd").value, divid_p: gv("#d205-divp").value,
      baza: gv("#d205-baza").value, imp: gv("#d205-imp").value });
    randeazaFormularD205(corp, nav, true);
  });
  gv("#d205-regen").addEventListener("click", () => { curataEroriCamp(zona); regenereaza(corp, nav); });
}

// [lotul 13, 653] numele țării în română, din browser (`Intl.DisplayNames`), după codul validatorului; un cod pe care browserul nu-l
// cunoaște (ex. „AN”, „XC”) rămâne codul
function _numeTara(cod) {
  try { const n = new Intl.DisplayNames(["ro"], { type: "region" }).of(cod); return n && n !== cod ? n : cod; } catch { return cod; }
}
function _optiuniStat(coduri) {
  return coduri.map((c) => [c, _numeTara(c)]).sort((a, b) => a[1].localeCompare(b[1], "ro"))
    .map(([c, n]) => '<option value="' + esc(c) + '">' + esc(n) + (n !== c ? " (" + esc(c) + ")" : "") + "</option>").join("");
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
          '<span class="dec-recl-desc">' + esc(b.den) + ' · ' + esc(_numeTara(String(b.stat || "").toUpperCase())) +
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
    // [lotul 13, 653] statul de rezidență din lista validatorului D207, cu căutare (clasa 85); codurile fiscale „măcar unul” spus de la
    // început, nu abia la eroare; rândurile aliniate sus, ca un mesaj de eroare sub un câmp să nu le strice (clasa 259)
    '<div class="dec-d207-adauga" data-rand-adaugare>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-start;gap:10px">' +
      '<label class="camp" style="flex:1 1 280px"><span class="camp-eticheta">Tip venit plătit <span class="oblig">*</span></span>' +
        '<select id="d207-tip" class="camp-input">' + ALEGE + optTip + '</select></label>' +
      '<label class="camp" style="flex:1 1 200px"><span class="camp-eticheta">Nume / denumire beneficiar <span class="oblig">*</span></span><input id="d207-den" type="text" class="camp-input"></label>' +
      '<label class="camp" style="flex:1 1 240px"><span class="camp-eticheta">Stat de rezidență <span class="oblig">*</span></span>' +
        '<input type="text" id="d207-stat-cauta" class="camp-input" data-cautare placeholder="Caută țara…" aria-label="Caută statul de rezidență" autocomplete="off" style="margin-bottom:6px">' +
        '<select id="d207-stat" class="camp-input" aria-label="Statul de rezidență">' + ALEGE + _optiuniStat((S.nomenclatoare || {}).d207_stat_r || []) + '</select></label>' +
    '</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-start;gap:10px">' +
      '<div class="camp" style="flex:1 1 340px"><span class="camp-eticheta">Cod de identificare fiscală <span class="oblig">*</span> — completează măcar unul</span>' +
        '<div style="display:flex;flex-wrap:wrap;gap:10px;align-items:flex-start">' +
          '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">în România</span><input id="d207-cifro" type="text" class="camp-input"></label>' +
          '<label class="camp" style="flex:1 1 150px"><span class="camp-eticheta">în statul de rezidență</span><input id="d207-cifs" type="text" class="camp-input"></label>' +
        '</div></div>' +
      '<label class="camp" style="flex:1 1 240px"><span class="camp-eticheta">Act normativ aplicabil <span class="oblig">*</span></span>' +
        '<select id="d207-act" class="camp-input">' + ALEGE + optAct + '</select></label>' +
    '</div>' +
    '<div class="dec-man-form" style="flex-wrap:wrap;align-items:flex-start;gap:10px">' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Bază / venit brut (lei)</span><input id="d207-baza" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:150px"><span class="camp-eticheta">Impozit reținut (lei)</span><input id="d207-imp" type="number" step="1" min="0" class="camp-input"></label>' +
      '<label class="camp" style="width:190px"><span class="camp-eticheta">Impozit suportat de plătitor (lei)</span><input id="d207-imps" type="number" step="1" min="0" class="camp-input"></label>' +
    '</div>' +
    '<p style="margin:6px 0 0"><button class="buton-secundar" id="d207-add" data-fara-actiune="rând în formularul declarației (în memorie); generarea și trimiterea poartă acțiunea">+ adaugă beneficiarul</button></p>' +
    '</div>' +
    '<p class="camp-ajutor" id="d207-scutit-nota" style="margin:4px 0 0"></p>' +
    '<div id="d207-msg"></div>' +
    '<p class="camp-ajutor" id="d207-totaluri" style="margin-top:8px">' + cate(benef.length, "beneficiar", "beneficiari") + ' · bază impozabilă <b>' + bani(Tbaza) + '</b> · venit scutit <b>' + bani(Tscutit) + '</b> · impozit reținut <b>' + bani(Timp) + '</b> · impozit suportat de plătitor <b>' + bani(Timps) + '</b> lei. Suma de control a declarației: <b>' + totalCtrl + '</b> — se calculează automat din datele de mai sus.</p>' +
    '<p style="margin-top:8px"><button class="buton-primar" id="d207-regen">' + _etRegen() + '</button>' +
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
  cautaInLista(gv("#d207-stat-cauta"), gv("#d207-stat"));   // [lotul 13, 653] lista țărilor cu căutare (aceeași căutare ca la articole)
  gv("#d207-tip").addEventListener("change", reflScutit);
  reflScutit();
  zona.querySelectorAll(".dec-d207-del").forEach((b) => b.addEventListener("click", () => {
    S.d207.beneficiari.splice(parseInt(b.dataset.idx), 1); randeazaFormularD207(corp, nav);
  }));
  gv("#d207-add").addEventListener("click", () => {
    curataEroriCamp(zona);
    // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite; [lotul 13, 653] alegerile și câmpurile lipsă deodată (DS cap.6, 440)
    let faraAlegere = false; if (cereAlegerile(zona, ["#d207-tip", "#d207-act", "#d207-stat"])) faraAlegere = true;
    const tip = gv("#d207-tip").value;
    const den = gv("#d207-den").value.trim();
    const stat = gv("#d207-stat").value.trim().toUpperCase();
    const cifro = gv("#d207-cifro").value.trim();
    const cifs = gv("#d207-cifs").value.trim();
    const act = gv("#d207-act").value;
    const err = [];
    if (!den) err.push(["d207-den", "Completează numele sau denumirea beneficiarului nerezident."]);
    if (!cifro && !cifs) err.push(["d207-cifro", "Completează măcar unul dintre codurile de identificare fiscală."]);
    const sc = _d207Scutit(tip);
    // [lotul 13, 656] impozitul e un procent din bază: nu o poate depăși (verificarea serverului, `verificare_bun_simt`, o face și ea)
    const _baza = _n(gv("#d207-baza").value), _imp = sc ? 0 : _n(gv("#d207-imp").value) + _n(gv("#d207-imps").value);   // sumele prin `_n` (655: un singur loc de citire)
    if (_imp > _baza) err.push(["d207-imp", "Impozitul (" + bani(_imp) + " lei) e mai mare decât baza (" + bani(_baza) + " lei): impozitul reținut e un procent din venitul brut."]);
    if (err.length || faraAlegere) { err.forEach(([id, m]) => _eroareFormular(zona, id, m)); return; }
    S.d207.beneficiari.push({ tip_venit: tip, den: den, stat: stat, cif_ro: cifro, cif_strain: cifs,
      act_n: act, baza: gv("#d207-baza").value,
      imp: sc ? "" : gv("#d207-imp").value, imp_suportat: sc ? "" : gv("#d207-imps").value });
    randeazaFormularD207(corp, nav);
  });
  gv("#d207-regen").addEventListener("click", () => {
    curataEroriCamp(zona);
    // marcheaza campul vinovat INAINTE de a chema serverul (Regula 14.4)
    if (!(S.d207.beneficiari || []).length) {
      _refuzLangaRegen(zona, "Adaugă cel puțin un beneficiar nerezident (butonul + adaugă). D207 nu se depune fără beneficiari.");
      return;
    }
    regenereaza(corp, nav);
  });
}

// tip==="d300". Geaman cu randeazaOperatiuniD301: grila randurilor manuale + adaugare (upsert) +
// stergere + regenerare. Randurile pe care generatorul NU le deriva din facturi (scutiri/regularizari/
// ajustari) se introduc aici, PERSISTAT (tabel d300_manual); "Regenereaza D300" reface pas2, iar calea
// de depunere (/coada) le citeste din DB -> acelasi XML (paritate preview<->depunere). Etichetele
// oficiale + lista randurilor disponibile (allow-list minus auto-derivate) vin din backend, nu din JS.
// Sume in LEI intregi (ca generatorul). catch NON-gol (scrie in #d300-msg / zona) - garda test_catch_vizibil.
const cerereD300 = ultimaCerere();   // [C103] două ștergeri / adăugări în șir: numai re-citirea ultimei ajunge în grilă
async function randeazaManualD300(corp, nav) {
  const actuala = cerereD300();
  const zona = corp.querySelector("#dec-d300-manual");
  if (!zona) return;
  let d;
  try { d = await api.get(`/tenants/${S.tenant_id}/d300-manual?an=${S.an}&luna=${S.luna}`); if (!actuala()) return; }
  catch (e) { if (!actuala()) return; zona.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca rândurile manuale D300${e && e.mesaj ? " (" + esc(e.mesaj) + ")" : ""}. Reîncarcă declarația.</p>`; return; }
  const randuri = d.randuri || [], disp = d.randuri_disponibile || [];
  const grila = randuri.length
    ? randuri.map((o) => `<div class="dec-man-rand">
        <span class="dec-recl-desc" title="${esc(o.eticheta)}">${esc(o.rand)} · ${esc(o.eticheta)}</span>
        <span class="dec-recl-suma">${o.cu_baza === false ? "" : bani(o.baza) + " bază"}${o.cu_tva ? (o.cu_baza === false ? "" : " · ") + bani(o.tva) + " TVA" : ""} (lei)${o.descriere ? " · " + esc(o.descriere) : ""}</span>
        <button class="btn-link dec-d300-del" data-actiune="DELETE /tenants/{tenant_id}/d300-manual/{rid}" data-id="${o.id}">șterge</button></div>`).join("")
    : `<div class="stare-goala stare-goala--inline">Niciun rând manual pe ${etPerioada()}. Rândurile pe care generatorul le derivă din facturi apar automat în decont; aici introduci doar ce nu se derivă (scutiri, regularizări, ajustări).</div>`;
  const optiuni = disp.map((r) => `<option value="${esc(r.cod)}" data-cutva="${r.cu_tva ? 1 : 0}" data-cubaza="${r.cu_baza === false ? 0 : 1}">${esc(r.cod)} — ${esc(r.eticheta)}</option>`).join("");
  zona.innerHTML = `<details class="dec-xml" open><summary>Rânduri manuale D300 — introducere (${randuri.length})</summary>
    ${grila}
    ${disp.length ? `<div class="camp-eticheta" style="margin:10px 0 4px">Adaugă rând:</div>
    <div class="dec-man-form">
      <label class="camp" style="width:440px"><span class="camp-eticheta">Rând <span class="oblig">*</span></span>
        <select id="d300-rand" class="camp-input">${ALEGE}${optiuni}</select></label>
      <label class="camp" style="width:130px" id="d300-baza-wrap"><span class="camp-eticheta">Bază (lei) <span class="oblig">*</span></span><input id="d300-baza" type="number" step="1" class="camp-input"></label>
      <label class="camp" style="width:130px" id="d300-tva-wrap"><span class="camp-eticheta">TVA (lei)</span><input id="d300-tva" type="number" step="1" class="camp-input"></label>
      <label class="camp" style="width:220px"><span class="camp-eticheta">Descriere</span><input id="d300-descriere" class="camp-input"></label>
      <button class="buton-secundar" id="d300-add" data-actiune="POST /tenants/{tenant_id}/d300-manual">+ adaugă</button>
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
    // rândurile fără col.1 (R29, R31, R35…): baza nu există în structura ANAF -> câmpul dispare
    const cuBaza = !(o && o.dataset.cubaza === "0");
    const wb = gv("#d300-baza-wrap"); if (wb) wb.style.display = cuBaza ? "" : "none";
    if (!cuBaza) { const t = gv("#d300-baza"); if (t) t.value = ""; }
  }
  if (gv("#d300-rand")) { gv("#d300-rand").addEventListener("change", sincTva); sincTva(); }
  zona.querySelectorAll(".dec-d300-del").forEach((b) => b.addEventListener("click", async () => {
    try { await api.del(`/tenants/${S.tenant_id}/d300-manual/${b.dataset.id}`); _panouModificat(corp); randeazaManualD300(corp, nav); }
    catch (e) { arataRefuzul(zona, e, gv("#d300-msg")); }
  }));
  const bAdd = gv("#d300-add");
  if (bAdd) bAdd.addEventListener("click", async () => {
    const tvaEl = gv("#d300-tva");
    const b = { an: S.an, luna: S.luna, rand: gv("#d300-rand").value,
      baza: parseInt(gv("#d300-baza").value, 10) || 0,
      tva: parseInt((tvaEl && tvaEl.value) || "0", 10) || 0,
      descriere: gv("#d300-descriere").value.trim() };
    curataEroriCamp(zona);  // [G10] eroare langa camp
    if (cereAlegerile(zona, ["#d300-rand"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    try { await api.post(`/tenants/${S.tenant_id}/d300-manual`, b); _panouModificat(corp); randeazaManualD300(corp, nav); }
    catch (e) {
      curataEroriCamp(zona);
      arataRefuzul(zona, e, gv("#d300-msg"), { campuri: _campuriCu(e, "d300-") });   // fallback B (zona) daca #camp lipseste
    }
  });
  gv("#d300-regen").addEventListener("click", () => regenereaza(corp, nav));
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
// [08.10.2026, decizia Costin V4] „Secțiunea «Din ce e făcută declarația» afișează «[object Object]» în coloana «linii». Trebuie să
// arate cont, debit/credit și sumă.” O valoare-obiect (liniile unei note D406: {cont, debit, credit, …}) sau o listă de obiecte se
// scrie rând cu rând: „cont · debit/credit sumă”; alt obiect, ca perechi „cheie: valoare”. Niciun obiect nu ajunge la String().
export function celulaObiect(v) {
  const unu = (x) => {
    if (x == null) return "";
    if (typeof x !== "object") return esc(String(x));
    if ("cont" in x) {
      const d = Number(x.debit || 0), c = Number(x.credit || 0);
      return `${esc(String(x.cont))} \u00b7 ${d ? "debit " + bani(d) : "credit " + bani(c)}`;
    }
    return Object.entries(x).map(([a, b]) => `${esc(a)}: ${esc(b == null ? "" : (typeof b === "object" ? JSON.stringify(b) : String(b)))}`).join(", ");
  };
  return Array.isArray(v) ? v.map(unu).join("<br>") : unu(v);
}

export function _blocComponente(c) {
  if (!c) return "";
  // Propozitia o detine ECRANUL, nu raspunsul: un text trimis de server ar fi o afirmatie in proza
  // intr-un payload (interzis din 21.08), iar aici e text de interfata - explicit in afara regulii
  // (DS cap.25.5). Serverul trimite doar cuvantul din nomenclatorul inchis `ACOPERIRE`.
  // [lotul 13, 658 / 638] declarația făcută din formularul de mai sus: compoziția ei e chiar formularul — nimic de adăugat
  if (c.acoperire === "formular") return "";
  if (c.acoperire !== "completa") {
    const spune = c.acoperire === "absenta"
      ? "Declarația asta nu-și poate desface încă cifra pe operațiuni în aplicație. Compoziția se vede în fișierul XML generat."
      : "Rândurile din care e făcută declarația nu se pot arăta aici; le vezi în fișierul XML generat, mai jos.";
    return `<div class="caseta-info"><span class="ci-mesaj">${spune}</span></div>`;
  }
  if (!c.total) return "";
  const tabel = (s) => {
    const coloane = Object.keys(s.randuri[0] || {});
    const mon = new Set(s.monetare || []);
    const celula = (r, k) => (r[k] == null ? "" : (typeof r[k] === "object" ? celulaObiect(r[k])
      : (mon.has(k) ? bani(r[k]) : (/^\d{4}-\d{2}-\d{2}$/.test(String(r[k])) ? dataRo(r[k]) : esc(String(r[k]))))));   // [Retest 2 pct.14] data în forma românească
    return `<div style="margin-top:10px">
        <div class="camp-eticheta">${esc(s.nume)} \u2014 ${cate(s.total, "r\u00e2nd", "r\u00e2nduri")}${s.aratate < s.total ? `, se arat\u0103 primele ${s.aratate}` : ""}</div>
        <table class="fd-tabel">
          <thead><tr>${coloane.map((k) => `<th${mon.has(k) ? ' class="fd-td-num"' : ""}>${esc(k)}</th>`).join("")}</tr></thead>
          <tbody>${s.randuri.map((r) => `<tr>${coloane.map((k) => `<td${mon.has(k) ? ' class="fd-td-num"' : ""}>${celula(r, k)}</td>`).join("")}</tr>`).join("")}</tbody>
        </table>
      </div>`;
  };
  const cuRanduri = c.sectiuni.filter((s) => s.randuri.length);
  if (!cuRanduri.length) return "";
  return `<details class="dec-xml">
      <summary>Din ce e f\u0103cut\u0103 declara\u021bia \u2014 ${cate(c.total, "r\u00e2nd", "r\u00e2nduri")}</summary>
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
  const btn = corp.querySelector("#dec-trimite");
  if (btn) { btn.disabled = true; btn.textContent = "Se trimite…"; }
  const body = Object.assign(corpGenerare(), { tip: S.tip, inceput_la: S.inceput_la });   // [C2] același corp ca la pasul 2
  // [C1/C3] drumul comun al cozii; succesul (și după o confirmare a atenționărilor) desenează ecranul „Trimisă”
  const r = await trimiteInCoada(corp.querySelector("#dec-coada-mesaj"), body, (r) => pas3Gata(corp, nav, r));
  if (!r && btn) { btn.disabled = false; btn.textContent = btn.dataset.eticheta || "Trimite în coadă →"; }
}

function pas3Gata(corp, nav, r) {
  const f = corp.closest(".fereastra"); if (f) f.classList.remove("fer-larg");
  corp.innerHTML = `
    ${casetaTrimisa(S.tip.toUpperCase(), etPerioada(), (r && r.pas_urmator && r.pas_urmator.mesaj) || "a intrat în coadă.",
      r && r.pas_urmator && r.pas_urmator.cod !== "validare" ? "Trimisă în coadă" : "Trimisă în coada de validare")}
    <div id="dec-gata-avert"></div>
    <div class="dec-bara">
      <button class="buton-secundar" id="dec-alta" data-fara-actiune="navigare: alt tip de declarație">+ Altă declarație</button>
      <button class="buton-primar" id="dec-gata-ok">Gata</button>
    </div>
  `;
  // [08.10.2026, decizia Costin §6 pct.7 — R36] ciornele perioadei: avertisment, nu blocaj — rămâne vizibil lângă confirmare
  if (r && (r.avertismente_poarta || []).length) arataMesaj(corp.querySelector("#dec-gata-avert"), r.avertismente_poarta.join(" "), "avert");
  corp.querySelector("#dec-alta").addEventListener("click", () => nav.inapoiPas());   // [485] alegerea declarației, cu firma ferestrei
  corp.querySelector("#dec-gata-ok").addEventListener("click", () => nav.acasa());
}

function etPerioada() {
  const per = S.periodicitate[S.tip];
  if (per === "anual") return `anul ${S.an}`;
  if (per === "trimestrial") return `T${S.trim}/${S.an} (${LUNI_TRIM[S.trim - 1]})`;   // [Retest 2 pct.14] DS cap.4 v2.85: „T3/2026”
  // [G3] eticheta luna-an prin dataRo canonic (nu LUNI[S.luna-1] local); LUNI ramane pentru picker
  return dataRo(`${S.an}-${String(S.luna).padStart(2, "0")}`, "luna_an");
}

// audit_cab_lot1_v1
