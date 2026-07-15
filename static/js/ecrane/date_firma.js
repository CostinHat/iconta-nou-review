// date_firma.js — [date_firma_v1] datele fiscale ale firmei.
// Campurile pe care ANAF le cere OBLIGATORIU in declaratii. Pana azi nu existau
// deloc in interfata: firma_profil_api salva doar font/culoare/logo (modelul de
// factura), iar caen/telefon/banca/iban/reg_com se puteau completa doar direct in
// baza de date. O firma noua nu putea depune nicio declaratie.
// DS: cap.6 (asterisc pe obligatorii + ghidaj camp-ajutor + validari preventive cu
// mesaj explicativ), cap.9 (.grila-doc), cap.3 (nav.setInapoi).
// Apelare: randeazaDateFirma(corp, nav, tenantId, { inapoi })
import { api, arataMesaj, esc } from "../api.js";

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
];

function campVector(c, val) {
  const ob = c.ob ? '<span class="oblig">*</span>' : "";
  const aj = c.aj ? `<span class="camp-ajutor">${esc(c.aj)}</span>` : "";
  const v = val === true ? "da" : val === false ? "nu" : (val || "");
  const opts = c.opt.map(([k, t]) =>
    `<option value="${esc(k)}"${String(k) === String(v) ? " selected" : ""}>${esc(t)}</option>`).join("");
  return `
    <label class="camp">
      <span class="camp-eticheta">${esc(c.e)}${ob}</span>
      ${aj}
      <select class="camp-input" id="vf-${c.k}">${opts}</select>
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
  const avert = lipsa.length
    ? `<div class="dec-avert">
         <div class="dec-avert-cap">Profil incomplet \u2014 ${lipsa.length} c\u00e2mpuri obligatorii lipsesc</div>
         <ul>${lipsa.map((l) => `<li><b>${esc(eticheta(l.camp))}</b> \u2014 blocheaz\u0103 ${esc(l.declaratii.join(", "))}</li>`).join("")}</ul>
       </div>`
    : `<div class="dec-ok">Profil complet. Toate declara\u021biile se pot genera.</div>`;

  corp.innerHTML = `
    <h2 class="pf-titlu">Date firm\u0103</h2>
    <p class="pf-intro">Datele pe care ANAF le cere \u00een declara\u021bii. C\u00e2mpurile cu <span class="oblig">*</span> sunt obligatorii \u2014 f\u0103r\u0103 ele declara\u021biile nu se pot depune.</p>
    ${avert}
    <div class="grila-doc">${CAMPURI.map((c) => camp(c, d.profil[c.k])).join("")}</div>

    <h2 class="pf-titlu" style="margin-top:26px">Vector fiscal</h2>
    <p class="pf-intro">Ce declara\u021bii datoreaz\u0103 firma. Termenele \u0219i controlul fiscal pornesc de aici.</p>
    <div class="grila-doc">${VECTOR.map((c) => campVector(c, v[c.k])).join("")}</div>
    <div id="df-msg"></div>
    <div class="dec-bara">
      <button class="buton-primar" id="df-salveaza">Salveaz\u0103</button>
    </div>
  `;

  corp.querySelector("#df-salveaza").addEventListener("click", async () => {
    const btn = corp.querySelector("#df-salveaza");
    const msg = corp.querySelector("#df-msg");
    const date = {};
    for (const c of CAMPURI) {
      date[c.k] = (corp.querySelector(`#df-${c.k}`).value || "").trim();
    }
    // validare preventiva in ecran: nu trimitem ca sa aflam de la server (DS cap.6)
    const goale = CAMPURI.filter((c) => c.ob && !date[c.k]);
    if (goale.length) {
      arataMesaj(msg, "Completeaz\u0103: " + goale.map((c) => c.e).join(", ") + ".", "eroare");
      corp.querySelector(`#df-${goale[0].k}`).focus();
      return;
    }
    // vectorul: regim obligatoriu; periodicitatea e obligatorie DOAR la platitorii
    // de TVA (regula din vector_fiscal_api.salveaza - o singura sursa de adevar)
    const vf = {
      regim_fiscal: corp.querySelector("#vf-regim_fiscal").value,
      platitor_tva: corp.querySelector("#vf-platitor_tva").value === "da",
      tip_decont: corp.querySelector("#vf-tip_decont").value || null,
      operatiuni_ic: corp.querySelector("#vf-operatiuni_ic").value === "da",
    };
    if (vf.platitor_tva && !vf.tip_decont) {
      arataMesaj(msg, "Completeaz\u0103 periodicitatea TVA \u2014 obligatorie la pl\u0103titorii de TVA (decide dac\u0103 D300 se depune lunar sau trimestrial).", "eroare");
      corp.querySelector("#vf-tip_decont").focus();
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
