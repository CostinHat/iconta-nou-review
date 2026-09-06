// date_firma.js — [date_firma_v1] datele fiscale ale firmei.
// Campurile pe care ANAF le cere OBLIGATORIU in declaratii. Pana azi nu existau
// deloc in interfata: firma_profil_api salva doar font/culoare/logo (modelul de
// factura), iar caen/telefon/banca/iban/reg_com se puteau completa doar direct in
// baza de date. O firma noua nu putea depune nicio declaratie.
// DS: cap.6 (asterisc pe obligatorii + ghidaj camp-ajutor + validari preventive cu
// mesaj explicativ), cap.9 (.grila-doc), cap.3 (nav.setInapoi).
// Apelare: randeazaDateFirma(corp, nav, tenantId, { inapoi })
import { api, arataMesaj, esc, eroareCamp, curataEroriCamp } from "../api.js?v=1dccbc985b";

// camp -> {eticheta, obligatoriu, ajutor}. Obligatoriile vin din validatoarele
// declaratiilor (core/firma_profil_api.OBLIGATORII) - o singura sursa de adevar.
const CAMPURI = [
  // [R81 → BLOC R, 28.08.2026] Câmpul `nume` A IEȘIT de aici. Istoricul lui, în trei pași, fiindcă
  // fiecare pas a fost adevărat la momentul lui:
  //   27.08 — eticheta „Denumirea firmei" s-a despărțit în două, fiindcă firma avea DOUĂ denumiri
  //           în două locuri, iar pe 4 din 17 chiar difereau;
  //   28.08 — R81 s-a decis (simetrie de scriere): cele două nu mai pot diferi, deci ecranul avea
  //           două casete pentru o singură valoare, iar salvarea trimitea două cereri care se
  //           puteau suprascrie tăcut una pe alta. Le-am legat, ca reparație imediată;
  //   28.08 — decizia lui Costin: **se comasează.** Legarea era un plasture pe un duplicat;
  //           duplicatul iese. Denumirea se editează într-un singur loc, sus, prin
  //           `PUT /tenants/{id}` — care scrie amândouă coloanele.
  // `firma_profil.nume` NU dispare din bază și nu iese din payload-ul de CITIRE: rămâne coloana
  // care pleacă pe declarații. Ce dispare e a doua CALE de scriere din ecranul ăsta.
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
  // [R63] Nu „E-mail": la adresa asta pleaca pachetul lunar (`pachete_api`), iar ea NU e adresa
  // cu care clientul intra in portal. Doua campuri, doua nume.
  { k: "email", e: "E-mail firmă (aici se trimite pachetul lunar)" },
  // [R66] Numele administratorului: se tipărește pe adeverințe și pe contracte. Până azi
  // niciun ecran nu-l scria, iar documentele ieșeau cu un gol.
  { k: "patron_nume", e: "Nume administrator",
    aj: "Cine semnează pentru firmă. Apare pe adeverințe și pe contractele de muncă." },
  { k: "declarant_nume", e: "Nume declarant", ob: true },
  // [R101, 30.08.2026] OBLIGATORIU: structura ANAF a fiecareia din cele opt declaratii cere
  // `prenume_declar` cu marcaj DA. Pana azi campul era optional aici, iar generatorul il
  // fabrica drept "-" — o valoare inventata pe un document care pleaca la ANAF.
  { k: "declarant_prenume", e: "Prenume declarant", ob: true },
  { k: "declarant_functie", e: "Func\u021bia declarantului", ob: true },
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
  // [alege] selecturi obligatorii FARA optiune-goala pre-existenta: la valoare NULL browserul afiseaza
  // prima optiune ca aleasa (default fabricat, Regula 4). `alege:true` -> campVector pune un placeholder
  // "\u2014 alege \u2014" cand valoarea lipseste, iar salvarea cere alegere explicita (nu trimite fabricat).
  { k: "regim_fiscal", e: "Regim fiscal", ob: true, alege: true, tip: "select",
    opt: [["micro", "Microintreprindere (impozit pe venit)"], ["profit", "Impozit pe profit"]],
    aj: "Decide D100 (micro, trimestrial) sau D101 (profit, anual)." },
  { k: "platitor_tva", e: "\u00cenregistrat\u0103 \u00een scopuri de TVA", ob: true, alege: true, tip: "select",
    opt: [["nu", "Nu"], ["da", "Da"]],
    aj: "Din vectorul fiscal ANAF. Decide D300 si D394." },
  // [cerinta Costin, 06.09.2026] Acelasi text de ajutor ca in `migrare.js`, VERBATIM de acolo —
  // aceeasi alegere pusa in doua ecrane nu are voie sa aiba criteriul intr-unul singur. Nu se
  // rescrie si nu se rezuma: un temei citat din memorie intra in corpus ca fapt.
  // `core/test_ajutor_periodicitate_tva.py` compara cele doua texte RANDATE si pica daca diverg.
  { k: "tip_decont", e: "Periodicitate TVA", tip: "select",
    opt: [["", "\u2014"], ["lunar", "Lunar"], ["trimestrial", "Trimestrial"]],
    aj: "Lunar (regula, art. 322 alin. 1 Cod fiscal). Trimestrial doar dacă în anul precedent cifra de afaceri a fost sub 100.000 euro (curs BNR 31.12) ȘI nu ați efectuat achiziții intracomunitare de bunuri — art. 322 alin. 2." },
  { k: "operatiuni_ic", e: "Opera\u021biuni intracomunitare", alege: true, tip: "select",
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
  const ob = (c.ob || c.alege) ? '<span class="oblig">*</span>' : "";
  const aj = c.aj ? `<span class="camp-ajutor">${esc(c.aj)}</span>` : "";
  let control;
  if (c.tip === "data") {
    // [tva_inceput] input calendaristic (ISO 'YYYY-MM-DD'); valoarea vine pre-populata din /vector.
    control = `<input type="date" class="camp-input" id="vf-${c.k}" value="${esc(val || "")}">`;
  } else {
    const v = val === true ? "da" : val === false ? "nu" : (val || "");
    // [alege] valoare lipsa pe select obligatoriu -> placeholder "— alege —" AFISAT (selected), dar
    // neselectabil (disabled hidden): fara el, browserul afiseaza prima optiune reala ca aleasa (Regula 4).
    const ph = (c.alege && !v)
      ? `<option value="" selected disabled hidden>— alege —</option>` : "";
    const opts = c.opt.map(([k, t]) =>
      `<option value="${esc(k)}"${String(k) === String(v) ? " selected" : ""}>${esc(t)}</option>`).join("");
    control = `<select class="camp-input" id="vf-${c.k}">${ph}${opts}</select>`;
  }
  return `
    <label class="camp" id="vf-camp-${c.k}">
      <span class="camp-eticheta">${esc(c.e)}${ob}</span>
      ${aj}
      ${control}
    </label>`;
}

// [R77 + R81, 27.08.2026] Denumirea firmei, scrisă o dată și explicată o dată.
//
// Costin: *„un cabinet trebuie să poată corecta o denumire — o firmă se redenumește la registru,
// iar aplicația nu poate refuza să urmeze."* Deci câmpul există. Iar poarta construită în aceeași
// zi devine vie: cine tastează altceva decât spune ANAF face o **alegere**, consemnată cu autor
// și dată — nu o editare tăcută.
//
// De ce sunt două câmpuri și nu unul: firma are două denumiri, în două locuri. Cea din
// PORTOFOLIU (`tenants.nume`) e cea din listă și din bara de sus. Cea FISCALĂ
// (`firma_profil.nume`) pleacă în declarații și pe bilanț. Măsurat 27.08: pe **4 din 17** firme
// ele diferă deja. Tiparul e cel din R63 — două lucruri diferite, două nume, iar când coincid se
// spune. A treia, `nume_anaf`, nu se editează: e ce zice registrul.
function _blocDenumire(t, profil) {
  const nume = (t && t.nume) || "";
  const anaf = (t && t.nume_anaf) || "";
  const fiscal = (profil && profil.nume) || "";
  const nrm = (s) => String(s || "").trim().replace(/\s+/g, " ").toLowerCase();

  const randAnaf = anaf
    ? `<p class="camp-ajutor">La ANAF: <strong>${esc(anaf)}</strong>${
        t.nume_anaf_la ? ` (citit\u0103 la ${esc(String(t.nume_anaf_la).slice(0, 10))})` : ""}.
       Dac\u0103 scrii altceva, alegerea se consemneaz\u0103 \u2014 cu cine a f\u0103cut-o \u0219i c\u00e2nd.</p>`
    : `<p class="camp-ajutor">Pentru firma asta nu avem \u00eenc\u0103 denumirea de la ANAF, deci nu exist\u0103 cu ce s\u0103 difere. C\u00e2mpul e liber.</p>`;

  const divergenta = (fiscal && nrm(fiscal) !== nrm(nume))
    ? `<div class="dec-avert" data-e1="denumire-firma">
         <div class="dec-avert-cap">Cele dou\u0103 denumiri difer\u0103</div>
         <ul><li>\u00een portofoliu: <b data-e1-sursa="portofoliu">${esc(nume)}</b> \u2014 ce vezi \u00een list\u0103 \u0219i \u00een bara de sus</li>
             <li>\u00een declara\u021bii: <b data-e1-sursa="fiscal">${esc(fiscal)}</b> \u2014 <b data-e1-efect="fiscal">asta pleac\u0103 pe h\u00e2rtie</b></li></ul>
       </div>`
    : "";

  return `
    <h2 class="pf-titlu">Denumirea firmei</h2>
    ${divergenta}
    <div class="grila-doc">
      <label class="camp">
        <span class="camp-eticheta">Denumirea firmei<span class="oblig">*</span></span>
        <p class="camp-ajutor">Una singur\u0103, \u0219i se scrie \u00eentr-un singur loc: aceea\u0219i \u00een list\u0103, \u00een bara de sus \u0219i pe declara\u021bii (D100, D101, D205, D301, D390, D394, D406, bilan\u021b).</p>
        ${randAnaf}
        <input type="text" class="camp-input" id="df-nume-portofoliu" value="${esc(nume)}">
      </label>
    </div>`;
}


export async function randeazaDateFirma(corp, nav, tenantId, opt = {}) {
  if (nav && nav.setInapoi) nav.setInapoi(opt.inapoi || null);
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;

  let d = { profil: {}, lipsuri: [] };
  let v = {};
  let t = {};   // [R77] rândul din `public.tenants`: denumirea din portofoliu + ce spune ANAF
  try {
    [d, v, t] = await Promise.all([
      api.get(`/tenants/${tenantId}/firma-profil/date`),
      api.get(`/tenants/${tenantId}/vector`).catch(() => ({})),
      api.get(`/tenants/${tenantId}`).catch(() => ({})),
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
    ${_blocDenumire(t, d.profil)}
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

  // [BLOC R, 28.08.2026] Legarea celor două casete de denumire a fost scoasă odată cu a doua
  // casetă. Era reparația corectă cât timp duplicatul exista; nu mai are ce lega.

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
    // [R77] denumirea din portofoliu: alt tabel, deci alt apel — dar o singură apăsare pentru om.
    const numePortofoliu = (corp.querySelector("#df-nume-portofoliu").value || "").trim();
    if (!numePortofoliu) {
      eroareCamp(corp, "df-nume-portofoliu", "Completează denumirea din portofoliu.");
      goale.push({ k: "nume-portofoliu" });
    }
    // vectorul: periodicitatea TVA e obligatorie DOAR la platitorii de TVA (vector_fiscal_api.salveaza - sursa unica)
    // [alege] tri-stare: "" (placeholder neales) -> null, NU false tacit. Backendul refuza null cu mesaj
    // clar (regim REGIM_INVALID pt SRL, TVA_LIPSA, IC_LIPSA); dar validam preventiv aici (DS cap.6).
    const _regimV = corp.querySelector("#vf-regim_fiscal").value;
    const _tvaV = corp.querySelector("#vf-platitor_tva").value;
    const _icV = corp.querySelector("#vf-operatiuni_ic").value;
    const triBool = (x) => (x === "da" ? true : x === "nu" ? false : null);
    const vf = {
      regim_fiscal: _regimV || null,
      platitor_tva: triBool(_tvaV),
      tip_decont: corp.querySelector("#vf-tip_decont").value || null,
      operatiuni_ic: triBool(_icV),
      inreg_art317: corp.querySelector("#vf-inreg_art317").value === "da",
      // [tva_inceput] are sens doar la platitor; la neplatitor trimitem null (backendul o goleste oricum)
      tva_data_inceput: _tvaV === "da"
        ? (corp.querySelector("#vf-tva_data_inceput").value || null) : null,
    };
    // [alege] alegerile obligatorii ale vectorului. regim NU se cere la partida simpla (PFA/II/PFL n-are
    // micro/profit — vine din payload, fapt unic backend). tva si ic se cer la orice firma.
    const vecOblig = [];
    if (!(v && v.partida_simpla) && !vf.regim_fiscal)
      vecOblig.push(["vf-regim_fiscal", "Alege regimul fiscal (micro sau profit) — decide D100/D101."]);
    if (vf.platitor_tva === null)
      vecOblig.push(["vf-platitor_tva", "Alege dacă firma e înregistrată în scopuri de TVA (Da sau Nu) — decide D300/D394."]);
    if (vf.operatiuni_ic === null)
      vecOblig.push(["vf-operatiuni_ic", "Alege dacă firma are operațiuni intracomunitare (Da sau Nu) — decide D390."]);
    vecOblig.forEach(([id, m]) => eroareCamp(corp, id, m));
    const tvaLipsa = vf.platitor_tva === true && !vf.tip_decont;
    if (tvaLipsa) eroareCamp(corp, "vf-tip_decont", "Periodicitatea TVA e obligatorie la plătitorii de TVA (decide dacă D300 se depune lunar sau trimestrial).");
    if (goale.length || vecOblig.length || tvaLipsa) {
      (corp.querySelector(`#df-${(goale[0] || {}).k}`)
        || corp.querySelector(`#${(vecOblig[0] || [])[0]}`)
        || corp.querySelector("#vf-tip_decont"))?.focus();
      return;
    }
    btn.disabled = true;
    btn.textContent = "Se salveaz\u0103\u2026";
    let pas = 0;
    try {
      // [LOTUL 11, 04.09.2026] ORDINEA E REPARAȚIA. Până azi redenumirea pleca PRIMA: dacă
      // datele erau apoi refuzate, omul citea „Nu am putut salva" pe un ecran în care firma
      // TOCMAI fusese redenumită. Măsurat apăsând, cu formularul umplut cu semne:
      // `PUT /tenants/4838` → 200, `POST /firma-profil/date` → 422. Refuz pe ecran, denumire
      // schimbată în bBază, în două tabele, si de acolo pe `den` din D394.
      // Aceeași clasă ca R128 („poarta cădea DUPĂ aprobare"), a doua instanță: un act care se
      // refuză nu are voie să lase în urmă jumătate din el. Se scrie întâi ce poate fi refuzat,
      // și abia la urmă ce schimbă IDENTITATEA firmei.
      await api.post(`/tenants/${tenantId}/firma-profil/date`, date);
      await api.post(`/tenants/${tenantId}/vector`, vf);
      pas = 2;
      // [R77] Denumirea din portofoliu stă în alt tabel, deci e alt apel — dar o singură
      // apăsare pentru om. Se trimite DOAR dacă s-a schimbat: un `PUT` la fiecare salvare ar
      // consemna o „alegere" pe care nimeni n-a făcut-o.
      if (numePortofoliu !== ((t && t.nume) || "")) {
        await api.put(`/tenants/${tenantId}`, { nume: numePortofoliu });
      }
      await randeazaDateFirma(corp, nav, tenantId, opt);
      arataMesaj(corp.querySelector("#df-msg"), "Datele firmei au fost salvate.", "ok");
    } catch (e) {
      // [LOTUL 11] Mesajul spune CE a apucat să intre. `pas === 2` = profilul și vectorul sunt
      // înregistrate și a căzut DOAR redenumirea — acolo „Nu am putut salva" ar fi o afirmație
      // falsă despre date. *Actul rămâne cu confirmarea lui vizibilă pe calea de reușită (DS
      // cap.27): un `try` propriu pentru redenumire ar fi mutat confirmarea din blocul actului.*
      if (pas === 2) {
        await randeazaDateFirma(corp, nav, tenantId, opt);
        arataMesaj(corp.querySelector("#df-msg"),
          "Restul datelor s-au salvat, dar DENUMIREA nu: "
          + ((e && e.mesaj) || "a fost refuzată")
          + " Ecranul de mai jos arată ce e înregistrat acum.", "eroare");
        return;
      }
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
