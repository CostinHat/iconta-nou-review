// date_firma.js — [date_firma_v1] datele fiscale ale firmei.
// Campurile pe care ANAF le cere OBLIGATORIU in declaratii. Pana azi nu existau
// deloc in interfata: firma_profil_api salva doar font/culoare/logo (modelul de
// factura), iar caen/telefon/banca/iban/reg_com se puteau completa doar direct in
// baza de date. O firma noua nu putea depune nicio declaratie.
// DS: cap.6 (asterisc pe obligatorii + ghidaj camp-ajutor + validari preventive cu
// mesaj explicativ), cap.9 (.grila-doc), cap.3 (nav.setInapoi).
// Apelare: randeazaDateFirma(corp, nav, tenantId, { inapoi })
import { api, arataMesaj, esc, eroareCamp, curataEroriCamp } from "../api.js?v=3857bab660";

// camp -> {eticheta, obligatoriu, ajutor}. Obligatoriile vin din validatoarele
// declaratiilor (core/firma_profil_api.OBLIGATORII) - o singura sursa de adevar.
const CAMPURI = [
  { k: "nume", e: "Denumirea firmei", ob: true },
  { k: "cui", e: "CUI", ob: true },
  { k: "reg_com", e: "Nr. registrul comer\u021bului", ob: true,
    aj: "Din certificatul de \u00eenregistrare (ex. J40/1234/2020). Cerut la bilan\u021b." },
  { k: "caen", e: "Cod CAEN", ob: true,
    aj: "4 cifre, din certificatul constatator. ANAF nu \u00eel d\u0103 pentru toate firmele \u2014 completeaz\u0103-l manual." },
  { k: "adresa", e: "Adresa", ob: true },
  { k: "oras", e: "Localitatea" },
  { k: "judet", e: "Jude\u021bul" },
  { k: "cod_postal", e: "Cod po\u0219tal" },
  { k: "banca", e: "Banca", ob: true, aj: "Banca prin care se fac decont\u0103rile." },
  { k: "iban", e: "IBAN", ob: true },
  { k: "telefon", e: "Telefon", ob: true },
  { k: "email", e: "E-mail" },
  { k: "declarant_nume", e: "Nume declarant" },
  { k: "declarant_prenume", e: "Prenume declarant" },
  { k: "declarant_functie", e: "Func\u021bia declarantului" },
];

function camp(c, val) {
  const ob = c.ob ? '<span class="oblig">*</span>' : "";
  const aj = c.aj ? `<span class="camp-ajutor">${esc(c.aj)}</span>` : "";
  return `
    <label class="camp">
      <span class="camp-eticheta">${esc(c.e)}${ob}</span>
      ${aj}
      <input type="text" class="camp-input" id="df-${c.k}" value="${esc(val || "")}">
    </label>`;
}

// [vector_date_firma_v1] Vectorul fiscal: cele 4 atribute din firma_profil pe care le
// citeste/scrie core/vector_fiscal_api (citeste/salveaza). Pana acum se completa
// DOAR la migrarea cabinetului (migrare.js) - o firma adaugata direct sau creata la
// inregistrare ramanea pe valorile implicite din template (micro, neplatitor TVA,
// fara intracom), adica pe presupuneri. Termenele si controlul fiscal mergeau pe ele.
// Sta aici, nu intr-un ecran separat: datele fiscale ale firmei sunt un tot (DS:
// aceeasi situatie = aceeasi rezolvare).
const VECTOR = [
  { k: "regim_fiscal", e: "Regim fiscal", ob: true, tip: "select",
    opt: [["micro", "Microintreprindere (impozit pe venit)"], ["profit", "Impozit pe profit"]],
    aj: "Decide D100 (micro, trimestrial) sau D101 (profit, anual)." },
  { k: "platitor_tva", e: "\u00cenregistrat\u0103 \u00een scopuri de TVA", ob: true, tip: "select",
    opt: [["nu", "Nu"], ["da", "Da"]],
    aj: "Din vectorul fiscal ANAF. Decide D300 si D394." },
  { k: "tip_decont", e: "Periodicitate TVA", tip: "select",
    opt: [["", "\u2014"], ["lunar", "Lunar"], ["trimestrial", "Trimestrial"]],
    aj: "Obligatorie doar la pl\u0103titorii de TVA. Decide dac\u0103 D300/D394 se depun lunar sau trimestrial." },
  { k: "operatiuni_ic", e: "Opera\u021biuni intracomunitare", tip: "select",
    opt: [["nu", "Nu"], ["da", "Da"]],
    aj: "Achizi\u021bii/livr\u0103ri din UE. Decide D390 (VIES)." },
  { k: "inreg_art317", e: "\u00cenregistrat\u0103 art. 317 (opera\u021biuni intracomunitare)", tip: "select",
    opt: [["nu", "Nu"], ["da", "Da"]],
    aj: "\u00cenregistrare special\u0103 \u00een scopuri de TVA (art. 317 CF) pentru achizi\u021bii/livr\u0103ri intracomunitare la nepl\u0103titori. Decide D390 (VIES) \u0219i pers_inreg \u00een D301." },
  // [tva_inceput] data inregistrarii in scopuri de TVA - EDITABILA, ceruta contabilului cand ANAF n-o are.
  // Vizibila DOAR la platitor (doarPlatitor). Fara ea, motorul da gri "necunoscut" pe D300/D394/D406 (regula 4).
  { k: "tva_data_inceput", e: "Data \u00eenregistr\u0103rii \u00een scopuri de TVA", tip: "data", doarPlatitor: true,
    aj: "Data de la care firma e \u00eenregistrat\u0103 \u00een scopuri de TVA (de pe certificatul ANAF). Necesar\u0103 ca s\u0103 \u0219tim de c\u00e2nd se datoreaz\u0103 D300/D394/D406 \u2014 f\u0103r\u0103 ea, verdictele pe lunile trecute r\u0103m\u00e2n \u00abnecunoscut\u00bb." },
];

function campVector(c, val) {
  const ob = c.ob ? '<span class="oblig">*</span>' : "";
  const aj = c.aj ? `<span class="camp-ajutor">${esc(c.aj)}</span>` : "";
  let control;
  if (c.tip === "data") {
    // [tva_inceput] input calendaristic (ISO 'YYYY-MM-DD'); valoarea vine pre-populata din /vector.
    control = `<input type="date" class="camp-input" id="vf-${c.k}" value="${esc(val || "")}">`;
  } else {
    const v = val === true ? "da" : val === false ? "nu" : (val || "");
    const opts = c.opt.map(([k, t]) =>
      `<option value="${esc(k)}"${String(k) === String(v) ? " selected" : ""}>${esc(t)}</option>`).join("");
    control = `<select class="camp-input" id="vf-${c.k}">${opts}</select>`;
  }
  return `
    <label class="camp" id="vf-camp-${c.k}">
      <span class="camp-eticheta">${esc(c.e)}${ob}</span>
      ${aj}
      ${control}
    </label>`;
}

export async function randeazaDateFirma(corp, nav, tenantId, opt = {}) {
  if (nav && nav.setInapoi) nav.setInapoi(opt.inapoi || null);
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;

  let d = { profil: {}, lipsuri: [] };
  let v = {};
  try {
    [d, v] = await Promise.all([
      api.get(`/tenants/${tenantId}/firma-profil/date`),
      api.get(`/tenants/${tenantId}/vector`).catch(() => ({})),
    ]);
  } catch (e) {
    corp.innerHTML = `<div id="df-msg"></div>`;
    arataMesaj(corp.querySelector("#df-msg"), (e && e.mesaj) || "Nu am putut citi datele firmei.", "eroare");
    return;
  }

  const lipsa = d.lipsuri || [];
  const blocaje = d.blocaje || [];
  const avert = lipsa.length
    ? `<div class="dec-avert">
         <div class="dec-avert-cap">Profil incomplet \u2014 ${lipsa.length} ${lipsa.length === 1 ? "c\u00e2mp obligatoriu lipse\u0219te" : "c\u00e2mpuri obligatorii lipsesc"}</div>
         <ul>${lipsa.map((l) => `<li><b>${esc(eticheta(l.camp))}</b> \u2014 blocheaz\u0103 ${esc(l.declaratii.join(", "))}</li>`).join("")}</ul>
       </div>`
    : blocaje.length
    ? `<div class="dec-avert">
         <div class="dec-avert-cap">C\u00e2mpurile obligatorii sunt completate, dar unele declara\u021bii nu se pot genera \u00eenc\u0103</div>
         <ul>${blocaje.map((b) => `<li><b>${esc(b.declaratie)}</b> \u2014 ${esc(b.motiv)}</li>`).join("")}</ul>
       </div>`
    : `<div class="dec-ok">Profil complet. C\u00e2mpurile obligatorii sunt completate.</div>`;

  corp.innerHTML = `
    <h2 class="pf-titlu">Date firm\u0103</h2>
    <p class="pf-intro">Datele pe care ANAF le cere \u00een declara\u021bii. C\u00e2mpurile cu <span class="oblig">*</span> sunt obligatorii \u2014 f\u0103r\u0103 ele declara\u021biile nu se pot depune.</p>
    ${avert}
    <div class="grila-doc">${CAMPURI.map((c) => camp(c, d.profil[c.k])).join("")}</div>

    <h2 class="pf-titlu" style="margin-top:26px">Vector fiscal</h2>
    <p class="pf-intro">Ce declara\u021bii datoreaz\u0103 firma. Termenele \u0219i controlul fiscal pornesc de aici.</p>
    <div class="grila-doc">${VECTOR.map((c) => campVector(c, v[c.k])).join("")}</div>

    <h2 class="pf-titlu" style="margin-top:26px">Cont contabil</h2>
    <p class="pf-intro">Contul de venit folosit implicit la emiterea facturilor. Se poate schimba pe fiecare factur\u0103.</p>
    <div class="grila-doc">
      <label class="camp">
        <span class="camp-eticheta">Cont venit implicit</span>
        <span class="camp-ajutor">Clasa 70 (cifra de afaceri): 707 m\u0103rfuri, 704 servicii, 701 produse.</span>
        <select class="camp-input" id="df-cont_venit">${Object.entries(d.conturi_venit || {}).map(([k, t]) =>
          `<option value="${esc(k)}"${String(k) === String(d.profil.cont_venit_implicit) ? " selected" : ""}>${esc(k)} \u2014 ${esc(t)}</option>`).join("")}</select>
      </label>
    </div>
    <div id="df-msg"></div>
    <div class="dec-bara">
      <button class="buton-primar" id="df-salveaza">Salveaz\u0103</button>
    </div>
  `;

  // [tva_inceput] campul "Data inregistrarii TVA" apare DOAR la platitor; comuta live la schimbarea selectului.
  const _tvaSel = corp.querySelector("#vf-platitor_tva");
  const _tvaCamp = corp.querySelector("#vf-camp-tva_data_inceput");
  const _tvaToggle = () => { if (_tvaCamp) _tvaCamp.style.display = (_tvaSel && _tvaSel.value === "da") ? "" : "none"; };
  if (_tvaSel) _tvaSel.addEventListener("change", _tvaToggle);
  _tvaToggle();

  corp.querySelector("#df-salveaza").addEventListener("click", async () => {
    const btn = corp.querySelector("#df-salveaza");
    const msg = corp.querySelector("#df-msg");
    const date = {};
    for (const c of CAMPURI) {
      date[c.k] = (corp.querySelector(`#df-${c.k}`).value || "").trim();
    }
    date.cont_venit_implicit = corp.querySelector("#df-cont_venit").value;  // [F182] preferinta contabila la emitere
    // validare preventiva in ecran: nu trimitem ca sa aflam de la server (DS cap.6)
    // [G10 cap.6 v2.30] validare preventiva CLIENT: colecteaza TOATE erorile de camp si le plaseaza fiecare
    // LANGA campul ei (eroareCamp), nu un mesaj generic sus si nu fail-fast. B (arataMesaj) ramane pentru
    // erorile de business/backend fara camp (catch-ul de mai jos).
    curataEroriCamp(corp);
    const goale = CAMPURI.filter((c) => c.ob && !date[c.k]);
    goale.forEach((c) => eroareCamp(corp, "df-" + c.k, "Completează " + c.e + "."));
    // vectorul: periodicitatea TVA e obligatorie DOAR la platitorii de TVA (vector_fiscal_api.salveaza - sursa unica)
    const vf = {
      regim_fiscal: corp.querySelector("#vf-regim_fiscal").value,
      platitor_tva: corp.querySelector("#vf-platitor_tva").value === "da",
      tip_decont: corp.querySelector("#vf-tip_decont").value || null,
      operatiuni_ic: corp.querySelector("#vf-operatiuni_ic").value === "da",
      inreg_art317: corp.querySelector("#vf-inreg_art317").value === "da",
      // [tva_inceput] are sens doar la platitor; la neplatitor trimitem null (backendul o goleste oricum)
      tva_data_inceput: corp.querySelector("#vf-platitor_tva").value === "da"
        ? (corp.querySelector("#vf-tva_data_inceput").value || null) : null,
    };
    const tvaLipsa = vf.platitor_tva && !vf.tip_decont;
    if (tvaLipsa) eroareCamp(corp, "vf-tip_decont", "Periodicitatea TVA e obligatorie la plătitorii de TVA (decide dacă D300 se depune lunar sau trimestrial).");
    if (goale.length || tvaLipsa) {
      (corp.querySelector(`#df-${(goale[0] || {}).k}`) || corp.querySelector("#vf-tip_decont"))?.focus();
      return;
    }
    btn.disabled = true;
    btn.textContent = "Se salveaz\u0103\u2026";
    try {
      await api.post(`/tenants/${tenantId}/firma-profil/date`, date);
      await api.post(`/tenants/${tenantId}/vector`, vf);
      await randeazaDateFirma(corp, nav, tenantId, opt);
      arataMesaj(corp.querySelector("#df-msg"), "Datele firmei au fost salvate.", "ok");
    } catch (e) {
      btn.disabled = false;
      btn.textContent = "Salveaz\u0103";
      arataMesaj(msg, (e && e.mesaj) || "Nu am putut salva.", "eroare");
    }
  });
}

function eticheta(k) {
  const c = CAMPURI.find((x) => x.k === k);
  return c ? c.e : k;
}
