// migrare.js  // [p127_mig_loading] — Migrare cabinet  // [p86_fara_intro]  // [p85_fix]: meniu de operațiuni (straturi) + wizard per strat.
// Strat 1 (Firme) e funcțional: import ANAF -> decizie de finalizare (gata / mai am + notă).
// Restul straturilor: placeholder până le construim. Starea fiecăruia vine din /migrare/status.

import { api, esc, dataRo, bani, CULORI_CARD, baniRotund, arataMesaj, confirmaCaseta } from "../api.js?v=3857bab660";
import { sesiune } from "../sesiune.js?v=5d142951c9";

export const STRATURI = [
  { cheie:"firme", nr:1, titlu:"Firme", desc:"Validare CUI la ANAF · identificare + status fiscal",
    ...CULORI_CARD.albastru, construit:true,
    icon:'<path d="M3 21h18"/><path d="M5 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16"/><path d="M19 21V11a2 2 0 0 0-2-2h-2"/><path d="M9 7h2M9 11h2M9 15h2"/>' },
  { cheie:"vector_fiscal", nr:2, titlu:"Vector fiscal", desc:"Ce declarații datorează firma (TVA, regim, intracomunitar)",
    ...CULORI_CARD.chihlimbar, obligatoriu:true, construit:true,
    icon:'<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>' },  // [p84_vector_front]
  { cheie:"solduri", nr:3, titlu:"Solduri inițiale", desc:"Balanța de deschidere per firmă (aduce și planul analitic)",
    ...CULORI_CARD.verde, obligatoriu:true, construit:true,
    icon:'<path d="M12 3v18"/><path d="M5 8h14"/><path d="M5 8l-2 5h4z"/><path d="M19 8l-2 5h4z"/>' },
  { cheie:"solduri_parteneri", nr:4, titlu:"Solduri parteneri", desc:"4111/401 defalcat per client și furnizor",
    ...CULORI_CARD.teal, construit:true,
    icon:'<path d="M7 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z"/><path d="M17 21a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z"/><path d="M8.5 7L16 17"/>' },
  { cheie:"salariati", nr:5, titlu:"Salariați", desc:"Nume, CNP, salariu, date contract (payroll + D112)",
    ...CULORI_CARD.piersica, construit:true,
    icon:'<circle cx="9" cy="7" r="3"/><path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/><path d="M16 3.5a3 3 0 0 1 0 7M21 21v-2a4 4 0 0 0-3-3.8"/>' },
  { cheie:"asociati", nr:6, titlu:"Asociați", desc:"Nume, cotă % (pentru D205, dividende)",
    ...CULORI_CARD.violet, construit:true,
    icon:'<circle cx="12" cy="8" r="3.2"/><path d="M5 21v-1.5a5 5 0 0 1 5-5h4a5 5 0 0 1 5 5V21"/>' },
  { cheie:"mijloace_fixe", nr:7, titlu:"Mijloace fixe", desc:"Registru amortizare în curs (valoare · durată · cumulat)",
    ...CULORI_CARD.piersica, construit:true,
    icon:'<path d="M3 21h18"/><path d="M5 21V9l7-5 7 5v12"/><path d="M9 21v-6h6v6"/>' },
  { cheie:"istoric_declaratii", nr:8, titlu:"Istoric declarații", desc:"Ce s-a depus deja anul curent (ca să nu apară fals restanță)",
    ...CULORI_CARD.ardezie, construit:true,
    icon:'<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 13l2 2 4-4"/>' },
  { cheie:"plan_conturi", nr:9, titlu:"Plan de conturi", desc:"Extinde planul standard cu conturi analitice/nestandard, per firmă",
    ...CULORI_CARD.violet, construit:true,
    icon:'<path d="M4 6h16M4 12h16M4 18h7"/>' },
];

const SVG = (d, c) => `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="${c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`;

export function randeazaMigrare(corp, nav) {
  meniuMigrare(corp, nav);
}

// ---------- MENIUL DE OPERAȚIUNI ----------
function latime(corp, larg) {
  const f = corp.closest(".fereastra");
  if (f) f.classList.toggle("fer-larg", !!larg);
}

async function meniuMigrare(corp, nav) {
  nav.setInapoi(null);
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  let status = {}, nrFirme = 0;
  try {
    const s = await api.get("/migrare/status");
    status = (s && s.status) || {};
  } catch {}
  try {
    const t = await api.get("/tenants");
    nrFirme = ((t && t.tenants) || []).length;
  } catch {}

  corp.innerHTML = `
    <div class="mig-meniu" id="mig-meniu"></div>
  `;
  const meniu = corp.querySelector("#mig-meniu");

  STRATURI.forEach((st) => {
    const stare = status[st.cheie];               // {stare, nota} sau undefined
    const rand = document.createElement(st.construit ? "button" : "div");
    rand.className = "mig-op" + (st.construit ? "" : " mig-op-inactiv");

    // badge de stare (dreapta)
    let badge = "";
    if (stare && stare.stare === "gata") {
      badge = `<span class="mig-badge mig-b-gata">gata</span>`;
    } else if (stare && stare.stare === "in_lucru") {
      badge = `<span class="mig-badge mig-b-lucru">de continuat</span>`;
    } else if (!st.construit) {
      badge = `<span class="mig-badge mig-b-curand">în curând</span>`;
    } else if (st.obligatoriu) {
      badge = `<span class="mig-badge mig-b-oblig">obligatoriu</span>`;
    }

    // sub-text: progres / notă
    let sub = st.desc;
    let subAlert = false;
    if (st.cheie === "firme" && nrFirme) {
      sub = `${nrFirme} ${nrFirme === 1 ? "firmă importată" : "firme importate"}`;
    }
    if (stare && stare.stare === "in_lucru" && stare.nota) {
      sub = `${esc(stare.nota)}`;
      subAlert = true;
    }

    rand.innerHTML = `
      <span class="mig-op-nr">${st.nr}</span>
      <span class="mig-op-icon" style="background:${st.bg}">${SVG(st.icon, st.fg)}</span>
      <span class="mig-op-text">
        <span class="mig-op-titlu">${st.titlu}</span>
        <span class="mig-op-sub${subAlert ? " mig-op-sub-alert" : ""}">${sub}</span>
      </span>
      ${badge}
    `;
    if (st.construit) {
      rand.addEventListener("click", () => {
        if (st.cheie === "firme") nav.deschide("Firme", (cc, nn) => wizardFirme(cc, nn));
        else if (st.cheie === "vector_fiscal") nav.deschide("Vector fiscal", (cc, nn) => wizardVector(cc, nn));  // [p84_vector_front]
        else if (st.cheie === "solduri") nav.deschide("Solduri inițiale", (cc, nn) => wizardSolduri(cc, nn));
        else if (st.cheie === "solduri_parteneri") nav.deschide("Solduri parteneri", (cc, nn) => wizardParteneri(cc, nn));
        else if (st.cheie === "salariati") nav.deschide("Salariați", (cc, nn) => wizardSalariati(cc, nn));
        else if (st.cheie === "asociati") nav.deschide("Asociați", (cc, nn) => wizardAsociati(cc, nn));
        else if (st.cheie === "mijloace_fixe") nav.deschide("Mijloace fixe", (cc, nn) => wizardMijloace(cc, nn));
        else if (st.cheie === "istoric_declaratii") nav.deschide("Istoric declarații", (cc, nn) => wizardIstoric(cc, nn));
        else if (st.cheie === "plan_conturi") nav.deschide("Plan de conturi", (cc, nn) => wizardPlanConturi(cc, nn));
      });
    }
    meniu.appendChild(rand);
  });
}

// ---------- WIZARD FIRME ----------
function wizardFirme(corp, nav) {
  nav.setInapoi(() => meniuMigrare(corp, nav));
  pasInput(corp, nav);
}

function pasInput(corp, nav) {
  nav.setInapoi(() => meniuMigrare(corp, nav));
  corp.innerHTML = `
    <p class="mig-intro">Încarcă-ți tot portofoliul în iConta.eu. Verificăm fiecare CUI direct la ANAF și completăm automat denumirea și datele firmei.</p>
    <div class="mig-eticheta">Lipește CUI-urile firmelor (unul pe linie)</div>
    <textarea id="mig-text" class="mig-textarea" placeholder="14837428&#10;1590082&#10;RO14399840"></textarea>
    <div class="mig-sau"><span></span>sau<span></span></div>
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" accept=".csv,.xlsx,.tsv" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#16a34a" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">Încarcă un fișier</div>
      <div class="mig-drop-desc">Excel sau CSV cu o coloană de CUI-uri</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <button class="buton-primar mig-buton" id="mig-valideaza">Validează la ANAF</button>
  `;

  const fileInput = corp.querySelector("#mig-file");
  const dropTitlu = corp.querySelector("#mig-drop-titlu");
  let fisierAles = null;
  fileInput.addEventListener("change", () => {
    fisierAles = fileInput.files[0] || null;
    dropTitlu.textContent = fisierAles ? fisierAles.name : "Încarcă un fișier";
  });

  corp.querySelector("#mig-valideaza").addEventListener("click", async () => {
    const eroare = corp.querySelector("#mig-eroare");
    const buton = corp.querySelector("#mig-valideaza");
    eroare.textContent = "";
    const text = corp.querySelector("#mig-text").value.trim();
    if (!text && !fisierAles) { eroare.textContent = "Lipește CUI-uri sau încarcă un fișier."; return; }
    buton.disabled = true; buton.textContent = "Verific la ANAF…";
    try {
      let raspuns;
      if (fisierAles) {
        raspuns = await incarcaFisier(fisierAles);
      } else {
        const cui_uri = text.split(/[\s,;]+/).filter(Boolean);
        raspuns = await api.post("/migrare/valideaza", { cui_uri });
      }
      const rez = (raspuns && raspuns.rezultate) || [];
      if (rez.length === 0) {
        eroare.textContent = "Niciun CUI valid de verificat.";
        buton.disabled = false; buton.textContent = "Validează la ANAF"; return;
      }
      pasRezultate(corp, nav, rez);
    } catch (e) {
      eroare.textContent = (e && e.mesaj) || "A apărut o eroare la validare.";
      buton.disabled = false; buton.textContent = "Validează la ANAF";
    }
  });
}

async function incarcaFisier(file) {
  const fd = new FormData();
  fd.append("fisier", file);
  const r = await fetch("/migrare/incarca", {
    method: "POST",
    headers: { "Authorization": "Bearer " + sesiune.token() },
    body: fd,
  });
  let date = null;
  try { date = await r.json(); } catch { date = null; }
  if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
  return date;
}

function pasRezultate(corp, nav, rezultate) {
  nav.setInapoi(() => pasInput(corp, nav));
  corp.innerHTML = `
    <p class="mig-intro">Am verificat <b>${rezultate.length} CUI-uri</b> la ANAF. Bifează firmele pe care le aduci în iConta.eu.</p>
    <div class="mig-lista" id="mig-lista"></div>
    <div class="mig-eroare" id="mig-eroare"></div>
    <button class="buton-primar mig-buton" id="mig-importa">Importă firmele bifate</button>
  `;
  const lista = corp.querySelector("#mig-lista");
  rezultate.forEach((r, i) => {
    const rand = document.createElement("label");
    rand.className = "mig-rand" + (r.gasit ? "" : " mig-rand-gol");
    rand.innerHTML = `
      <input type="checkbox" data-i="${i}" ${r.gasit ? "checked" : "disabled"}>
      <div class="mig-rand-text">
        <div class="mig-rand-nume">${esc(r.gasit ? r.denumire : ("CUI " + r.cui))}</div>
        <div class="mig-rand-sub">${r.gasit
          ? ("CUI " + r.cui + " · " + (r.platitor_tva ? "plătitor TVA" : "neplătitor TVA"))
          : "nu a fost găsit la ANAF"}</div>
      </div>
      <span class="mig-stare ${r.gasit ? "mig-ok" : "mig-nok"}">${r.gasit ? "găsită" : "negăsită"}</span>
    `;
    lista.appendChild(rand);
  });

  function actButon() {
    const n = lista.querySelectorAll('input[type=checkbox]:checked').length;
    const b = corp.querySelector("#mig-importa");
    b.textContent = n ? `Importă ${n} ${n === 1 ? "firmă" : "firme"} în iConta.eu` : "Importă firmele bifate";
    b.disabled = n === 0;
  }
  lista.addEventListener("change", actButon); actButon();

  corp.querySelector("#mig-importa").addEventListener("click", async () => {
    const eroare = corp.querySelector("#mig-eroare");
    const buton = corp.querySelector("#mig-importa");
    eroare.textContent = "";
    const selectate = [];
    lista.querySelectorAll('input[type=checkbox]:checked').forEach((cb) => {
      const r = rezultate[parseInt(cb.dataset.i, 10)];
      selectate.push({ cui: r.cui, denumire: r.denumire });
    });
    if (selectate.length === 0) return;
    buton.disabled = true; buton.textContent = "Import în curs…";
    try {
      const raport = await api.post("/migrare/importa", { firme: selectate });
      pasFinal(corp, nav, raport);
    } catch (e) {
      eroare.textContent = (e && e.mesaj) || "A apărut o eroare la import.";
      buton.disabled = false; actButon();
    }
  });
}

// ---------- PAS FINAL: decizie de finalizare ----------
function pasFinal(corp, nav, raport) {
  nav.setInapoi(() => meniuMigrare(corp, nav));
  const creat = (raport && raport.creat) || [];
  const erori = (raport && raport.erori) || [];
  const dejaExista = erori.filter((e) => (e.mesaj || "").includes("există deja")).length;
  const alteErori = erori.length - dejaExista;
  let avert = "";
  if (dejaExista) avert += `<div class="mig-avert">${dejaExista} ${dejaExista === 1 ? "firmă era deja" : "firme erau deja"} în portofoliu — nu s-au dublat.</div>`;
  if (alteErori) avert += `<div class="mig-avert mig-avert-rosu">${alteErori} ${alteErori === 1 ? "firmă nu a putut fi adăugată" : "firme nu au putut fi adăugate"}.</div>`;

  const sumar = `
    <div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">${creat.length} ${creat.length === 1 ? "firmă adăugată" : "firme adăugate"} în iConta.eu</div>
    </div>
    ${avert}`;
  randeazaDecizie(corp, nav, "firme", sumar, "Importul firmelor e complet?");
}

// decizie de finalizare reutilizabilă (firme, solduri, ...)
function randeazaDecizie(corp, nav, strat, sumarHTML, intrebare) {
  corp.innerHTML = `
    ${sumarHTML}
    <div class="mig-eticheta" style="margin-top:6px;">${intrebare}</div>
    <div class="mig-decizie">
      <button class="mig-dec" data-val="gata" id="dec-gata"><span>✓</span> Da, e gata</button>
      <button class="mig-dec" data-val="in_lucru" id="dec-lucru"><span>…</span> Nu, mai am</button>
    </div>
    <div id="mig-nota-zona" style="display:none;">
      <div class="mig-nota-et">Ce mai ai de adus? <span>(obligatoriu)</span></div>
      <textarea id="mig-nota" class="mig-textarea" style="height:64px" placeholder="Ex: aștept balanțele de la 2 clienți"></textarea>
    </div>
    <div class="mig-eroare" id="mig-eroare"></div>
    <button class="buton-primar mig-buton" id="mig-salveaza" disabled>Salvează</button>
  `;
  let ales = null;
  const zona = corp.querySelector("#mig-nota-zona");
  const salv = corp.querySelector("#mig-salveaza");
  const decGata = corp.querySelector("#dec-gata");
  const decLucru = corp.querySelector("#dec-lucru");
  function alege(val) {
    ales = val;
    decGata.classList.toggle("mig-dec-sel", val === "gata");
    decLucru.classList.toggle("mig-dec-sel", val === "in_lucru");
    zona.style.display = val === "in_lucru" ? "block" : "none";
    salv.disabled = false;
  }
  decGata.addEventListener("click", () => alege("gata"));
  decLucru.addEventListener("click", () => alege("in_lucru"));
  salv.addEventListener("click", async () => {
    const eroare = corp.querySelector("#mig-eroare");
    eroare.textContent = "";
    if (!ales) return;
    const nota = ales === "in_lucru" ? corp.querySelector("#mig-nota").value.trim() : "";
    if (ales === "in_lucru" && !nota) { eroare.textContent = "Scrie ce mai ai de adus."; return; }
    salv.disabled = true; salv.textContent = "Salvez…";
    try {
      await api.post("/migrare/status", { strat, stare: ales, nota });
      if (nav && nav.inapoiPas) nav.inapoiPas(); else meniuMigrare(corp, nav);  // pop pe traseu -> firul reflecta pozitia reala (nu acumuleaza straturi)
    } catch (e) {
      eroare.textContent = (e && e.mesaj) || "Eroare la salvare.";
      salv.disabled = false; salv.textContent = "Salvează";
    }
  });
}

// ---------- STRAT 2: SOLDURI INIȚIALE (per firmă) ----------
// [p84_vector_front] ----- STRAT VECTOR FISCAL -----
async function wizardVector(corp, nav) {
  nav.setInapoi(() => meniuMigrare(corp, nav));
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103 firmele\u2026</p>`;
  let firme = [];
  try {
    const r = await api.get("/migrare/vector");
    firme = (r && r.firme) || [];
  } catch {}
  const cu = firme.filter((f) => f.are_vector).length;
  corp.innerHTML = `
    
    <p class="mig-intro">Spune sistemului ce declara\u021bii datoreaz\u0103 fiecare firm\u0103: dac\u0103 e pl\u0103titoare de TVA, ce regim are (micro/profit) \u0219i dac\u0103 face opera\u021biuni intracomunitare. F\u0103r\u0103 vectorul fiscal firma nu poate fi procesat\u0103.</p>
    <div class="mig-progres">${cu} din ${firme.length} firme au vectorul completat</div>
    <div class="mig-lista" id="mig-firme"></div>
    <button class="buton-primar mig-buton" id="mig-finalizeaza" style="margin-top:16px">Finalizeaz\u0103 stratul Vector fiscal</button>
  `;
  const lista = corp.querySelector("#mig-firme");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio firm\u0103 \u00een portofoliu. Import\u0103 \u00eent\u00e2i firmele (stratul 1).</div>`;
  }
  firme.forEach((f) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    let sub = "de completat";
    if (f.are_vector) {
      const p = [];
      p.push(f.regim_fiscal === "profit" ? "profit" : (f.regim_fiscal === "micro" ? "micro" : "—"));  // null -> —, nu default tacit
      if (f.platitor_tva) p.push("TVA " + (f.tip_decont || ""));
      else p.push("neplatitor TVA");
      if (f.operatiuni_ic) p.push("intracomunitar");
      sub = p.join(" \u00b7 ");
    }
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${sub}</div>
      </div>
      <span class="mig-stare ${f.are_vector ? "mig-ok" : "mig-gri"}">${f.are_vector ? "\u2713 gata" : "de completat"}</span>
    `;
    rand.addEventListener("click", () => nav.deschide("Vector firm\u0103", (cc, nn) => formularVectorFirma(cc, nn, f)));  // [p128_vector_cascada]
    lista.appendChild(rand);
  });
  corp.querySelector("#mig-finalizeaza").addEventListener("click", () => {
    const sumar = `<div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">Vector fiscal: ${cu} din ${firme.length} firme</div>
    </div>`;
    randeazaDecizie(corp, nav, "vector_fiscal", sumar, "Vectorul fiscal e complet pentru toate firmele?");
  });
}

async function formularVectorFirma(corp, nav, f) {
  nav.setInapoi(() => wizardVector(corp, nav));
  latime(corp, false);
  // pre-completez din ANAF (platitor_tva e deja stiut la validarea CUI) daca firma n-are vector
  let tvaInit = f.platitor_tva;
  if (tvaInit === null || tvaInit === undefined) {
    try {
      const r = await api.post("/migrare/valideaza", { cui_uri: [f.cui] });  // [p85_fix]
      const z = (r && r.rezultate && r.rezultate[0]) || null;
      if (z) tvaInit = !!z.platitor_tva;
    } catch {}
  }
  const regim = f.regim_fiscal;   // fara fallback tacit; null la vector necompletat
  const partidaSimpla = f.regim_contabil === "simpla";   // PFA/profesie liberala: n-are regim CIT (micro/profit)
  const decont = f.tip_decont;   // fara preselectie tacita; obligatoriu la plator TVA (ANAF v9 nu aduce periodicitatea)
  const ic = f.operatiuni_ic;    // raw true/false/null: fara preselectie tacita, obligatoriu (decide obligatia D390)
  const tva = !!tvaInit;
  corp.innerHTML = `
    <h2 class="mig-form-titlu">Verificare fiscal\u0103</h2>
    <p class="mig-form-cui">${esc(f.nume)} \u00b7 CUI ${esc(f.cui)}</p>
    <div class="vf-form">
      ${partidaSimpla ? "" : `<div class="vf-grup">
        <div class="vf-eticheta">Regim fiscal <span class="oblig">*</span></div>
        <div class="vf-optiuni" id="vf-regim">
          <button class="vf-opt ${regim==="micro"?"vf-on":""}" data-v="micro">Microintreprindere</button>
          <button class="vf-opt ${regim==="profit"?"vf-on":""}" data-v="profit">Impozit pe profit</button>
        </div>
      </div>`}
      <div class="vf-grup">
        <div class="vf-eticheta">Pl\u0103titoare de TVA?</div>
        <div class="vf-optiuni" id="vf-tva">
          <button class="vf-opt ${tva?"vf-on":""}" data-v="da">Da</button>
          <button class="vf-opt ${!tva?"vf-on":""}" data-v="nu">Nu</button>
        </div>
      </div>
      <div class="vf-grup" id="vf-decont-grup" style="${tva?"":"display:none"}">
        <div class="vf-eticheta">Periodicitate decont TVA <span class="oblig">*</span></div>
        <span class="camp-ajutor">Lunar (regula, art. 322 alin. 1 Cod fiscal). Trimestrial doar dacă în anul
          precedent cifra de afaceri a fost sub 100.000 euro (curs BNR 31.12) ȘI nu ați efectuat achiziții
          intracomunitare de bunuri — art. 322 alin. 2.</span>
        <div class="vf-optiuni" id="vf-decont">
          <button class="vf-opt ${decont==="lunar"?"vf-on":""}" data-v="lunar">Lunar</button>
          <button class="vf-opt ${decont==="trimestrial"?"vf-on":""}" data-v="trimestrial">Trimestrial</button>
        </div>
      </div>
      <div class="vf-grup">
        <div class="vf-eticheta">Opera\u021biuni intracomunitare? <span class="oblig">*</span></div>
        <span class="camp-ajutor">Livr\u0103ri, achizi\u021bii sau prest\u0103ri c\u0103tre/de la parteneri din UE.
          D390 se depune numai pentru lunile \u00een care exist\u0103 astfel de opera\u021biuni (instruc\u021biuni
          completare D390, anexa OPANAF 394/2017, pct. 1.2).</span>
        <div class="vf-optiuni" id="vf-ic">
          <button class="vf-opt ${ic === true ? "vf-on" : ""}" data-v="da">Da</button>
          <button class="vf-opt ${ic === false ? "vf-on" : ""}" data-v="nu">Nu</button>
        </div>
      </div>
      <div class="mig-eroare" id="vf-eroare"></div>
      <button class="buton-primar mig-buton" id="vf-salveaza" style="margin-top:8px">Salveaz\u0103 vectorul</button>
    </div>
  `;
  // selectie exclusiva in fiecare grup
  function grup(id, onChange) {
    const z = corp.querySelector(id);
    z.querySelectorAll(".vf-opt").forEach((b) => {
      b.addEventListener("click", () => {
        z.querySelectorAll(".vf-opt").forEach((x) => x.classList.remove("vf-on"));
        b.classList.add("vf-on");
        if (onChange) onChange(b.dataset.v);
      });
    });
    const on = z.querySelector(".vf-on");
    return () => (z.querySelector(".vf-on") || {}).dataset?.v;
  }
  const getRegim = partidaSimpla ? (() => null) : grup("#vf-regim");   // partida simpla: nu trimite regim_fiscal
  const getTva = grup("#vf-tva", (v) => {
    corp.querySelector("#vf-decont-grup").style.display = (v === "da") ? "" : "none";
  });
  const getDecont = grup("#vf-decont");
  const getIc = grup("#vf-ic");
  corp.querySelector("#vf-salveaza").addEventListener("click", async () => {
    const er = corp.querySelector("#vf-eroare");
    er.textContent = "";
    const platitor = getTva() === "da";
    const payload = {
      regim_fiscal: getRegim(),
      platitor_tva: platitor,
      tip_decont: platitor ? getDecont() : null,
      // obligatoriu, fara default tacit: nimic ales -> null -> backend respinge (400). NU coercem la false.
      operatiuni_ic: getIc() === "da" ? true : (getIc() === "nu" ? false : null),
    };
    try {
      await api.post(`/tenants/${f.tenant_id}/vector`, payload);
      nav.deschide("Vector fiscal", (cc, nn) => wizardVector(cc, nn));
    } catch (e) {
      er.textContent = (e && (e.mesaj || e.message)) || "Nu am putut salva. \u00cencearc\u0103 din nou.";
    }
  });
}

async function wizardSolduri(corp, nav) {
  nav.setInapoi(() => meniuMigrare(corp, nav));
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se încarcă firmele…</p>`;
  let firme = [];
  try {
    const r = await api.get("/migrare/solduri");
    firme = (r && r.firme) || [];
  } catch {}

  const cuSolduri = firme.filter((f) => f.are_solduri).length;
  corp.innerHTML = `
    <p class="mig-intro">Încarcă balanța de deschidere pentru fiecare firmă. Soldurile devin poziția de pornire, iar conturile analitice (clienți, furnizori) intră automat în plan.</p>
    <div class="mig-progres">${cuSolduri} din ${firme.length} firme au solduri</div>
    <div class="mig-lista" id="mig-firme"></div>
    <button class="buton-primar mig-buton" id="mig-finalizeaza" style="margin-top:16px">Finalizează stratul Solduri</button>
  `;

  const lista = corp.querySelector("#mig-firme");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio firmă în portofoliu. Importă întâi firmele (stratul 1).</div>`;
  }
  firme.forEach((f) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${f.are_solduri ? `${f.randuri} conturi importate` : "fără solduri încă"}</div>
      </div>
      <span class="mig-stare ${f.are_solduri ? "mig-ok" : "mig-gri"}">${f.are_solduri ? "✓ gata" : "de încărcat"}</span>
    `;
    rand.addEventListener("click", () => nav.mergi("Import \u00b7 " + (f.nume || ""), (c) => importSolduriFirma(c, nav, f)));  // faza_b3_migrare_v1
    lista.appendChild(rand);
  });

  corp.querySelector("#mig-finalizeaza").addEventListener("click", () => {
    const sumar = `<div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">Solduri: ${cuSolduri} din ${firme.length} firme</div>
    </div>`;
    randeazaDecizie(corp, nav, "solduri", sumar, "Importul soldurilor e complet?");
  });
}

function importSolduriFirma(corp, nav, firma) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>Încarcă balanța de deschidere (cont · denumire · sold debitor · sold creditor).</p>
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" accept=".csv,.xlsx,.tsv" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#16a34a" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">Încarcă balanța</div>
      <div class="mig-drop-desc">Excel sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  const fileInput = corp.querySelector("#mig-file");
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    eroare.textContent = "Citesc balanța…";
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const r = await fetch(`/tenants/${firma.tenant_id}/solduri/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaSolduri(corp, nav, firma, date);
    } catch (e) {
      eroare.textContent = (e && e.mesaj) || "Eroare la citirea balanței.";
    }
  });
}

function previzualizeazaSolduri(corp, nav, firma, date) {
  latime(corp, true);
  const randuri = date.randuri || [];
  // [DESIGN_SYSTEM cap.6, arataMesaj v2] tipuri canonice: eroare/avert/info/ok; un "ok" (verde)
  // se afiseaza DOAR pe succes real. O balanta goala / cu structura straina (fisier gresit) NU e
  // succes -> badge verde "echilibrat" pe 0=0 ar fi status FALS. valida vine din backend
  // (solduri_api.balanta_valida): pe invalid aratam avert-ul si blocam salvarea.
  const valida = date.valida !== false;
  const echilibrat = valida && Math.abs(date.total_debit - date.total_credit) < 0.01;

  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b> · balanță încărcată</p>
    <div class="mig-sold-rezumat">
      <b>${randuri.length}</b> conturi · debit <b>${bani(date.total_debit)}</b> · credit <b>${bani(date.total_credit)}</b>
      ${!valida ? '<span class="mig-eq mig-eq-no">fișier nevalid</span>' : (echilibrat ? '<span class="mig-eq mig-eq-ok">echilibrat</span>' : '<span class="mig-eq mig-eq-no">neechilibrat</span>')}
    </div>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div class="mig-sold-cap">
      <span>Cont</span><span>Denumire</span><span>Debit</span><span>Credit</span>
    </div>
    <div class="mig-sold-tabel" id="mig-sold-tabel"></div>
    <button class="buton-primar mig-buton" id="mig-salveaza-sold">Salvează soldurile</button>
  `;
  nav.setInapoi(() => wizardSolduri(corp, nav));

  // Fisier nevalid (gol / structura straina): nu e succes -> avert + salvarea blocata (nu bulina verde).
  if (!valida) {
    arataMesaj(corp.querySelector("#mig-eroare"), date.motiv || "Fișier nerecunoscut ca balanță.", "avert");
    const bs = corp.querySelector("#mig-salveaza-sold");
    if (bs) { bs.disabled = true; bs.title = "Balanță nevalidă — verifică fișierul încărcat"; }
  }

  const tabel = corp.querySelector("#mig-sold-tabel");
  tabel.innerHTML = randuri.map((r) => `
    <div class="mig-sold-rand">
      <span class="mig-sold-cont">${esc(r.cont)}</span>
      <span class="mig-sold-den">${esc(r.denumire || "")}</span>
      <span class="mig-sold-val">${bani(r.debit)}</span>
      <span class="mig-sold-val">${bani(r.credit)}</span>
    </div>`).join("");

  corp.querySelector("#mig-salveaza-sold").addEventListener("click", async () => {
    const eroare = corp.querySelector("#mig-eroare");
    const buton = corp.querySelector("#mig-salveaza-sold");
    eroare.textContent = "";
    buton.disabled = true; buton.textContent = "Salvez…";
    try {
      await api.post(`/tenants/${firma.tenant_id}/solduri`, { randuri });
      nav.deschide("Solduri inițiale", (cc, nn) => wizardSolduri(cc, nn));
    } catch (e) {
      eroare.textContent = (e && e.mesaj) || "Eroare la salvare.";
      buton.disabled = false; buton.textContent = "Salvează soldurile";
    }
  });
}


// ---------- STRAT 3: SOLDURI PARTENERI (per firma) ----------
async function wizardParteneri(corp, nav) {
  nav.setInapoi(() => meniuMigrare(corp, nav));
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se încarcă firmele…</p>`;
  let firme = [];
  try {
    const r = await api.get("/migrare/parteneri");
    firme = (r && r.firme) || [];
  } catch {}

  const cuParteneri = firme.filter((f) => f.are_parteneri).length;
  corp.innerHTML = `
    <p class="mig-intro">Defalcă soldurile de clienți (4111) și furnizori (401) pe fiecare partener. Sumele se verifică automat cu balanța de deschidere.</p>
    <div class="mig-progres">${cuParteneri} din ${firme.length} firme au parteneri</div>
    <div class="mig-lista" id="mig-firme"></div>
    <button class="buton-primar mig-buton" id="mig-finalizeaza" style="margin-top:16px">Finalizează stratul Parteneri</button>
  `;

  const lista = corp.querySelector("#mig-firme");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio firmă în portofoliu. Importă întâi firmele (stratul 1).</div>`;
  }
  firme.forEach((f) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${f.are_parteneri ? `${f.randuri} parteneri importați` : "fără parteneri încă"}</div>
      </div>
      <span class="mig-stare ${f.are_parteneri ? "mig-ok" : "mig-gri"}">${f.are_parteneri ? "✓ gata" : "de încărcat"}</span>
    `;
    rand.addEventListener("click", () => nav.mergi("Import \u00b7 " + (f.nume || ""), (c) => importParteneriFirma(c, nav, f)));  // faza_b3_migrare_v1
    lista.appendChild(rand);
  });

  corp.querySelector("#mig-finalizeaza").addEventListener("click", () => {
    const sumar = `<div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">Parteneri: ${cuParteneri} din ${firme.length} firme</div>
    </div>`;
    randeazaDecizie(corp, nav, "solduri_parteneri", sumar, "Defalcarea partenerilor e completă?");
  });
}

function importParteneriFirma(corp, nav, firma) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>Încarcă partenerii (cont · CUI · denumire · sold debitor · sold creditor).</p>
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" accept=".csv,.xlsx,.tsv" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#0a807b" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">Încarcă partenerii</div>
      <div class="mig-drop-desc">Excel sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  const fileInput = corp.querySelector("#mig-file");
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    eroare.textContent = "Citesc partenerii…";
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const r = await fetch(`/tenants/${firma.tenant_id}/parteneri/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaParteneri(corp, nav, firma, date);
    } catch (e) {
      eroare.textContent = (e && e.mesaj) || "Eroare la citirea fișierului.";
    }
  });
}

function previzualizeazaParteneri(corp, nav, firma, date) {
  latime(corp, true);
  const randuri = date.randuri || [];
  const coer = date.coerenta || [];

  // banda de coerenta per cont sintetic
  const coerHTML = coer.map((c) => {
    if (c.coincide === true) {
      return `<span class="mig-eq mig-eq-ok">${esc(c.cont)}: ✓ coincide</span>`;
    } else if (c.coincide === false) {
      return `<span class="mig-eq mig-eq-no">${esc(c.cont)}: ⚠ diferență ${bani(Math.abs(c.diferenta))}</span>`;
    }
    return `<span class="mig-eq mig-eq-gri">${esc(c.cont)}: fără balanță</span>`;
  }).join(" ");

  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b> · parteneri încărcați</p>
    <div class="mig-sold-rezumat">
      <b>${randuri.length}</b> parteneri · debit <b>${bani(date.total_debit)}</b> · credit <b>${bani(date.total_credit)}</b>
    </div>
    <div class="mig-coer">${coerHTML}</div>
    <div class="mig-sold-cap mig-cap-part">
      <span>Cont</span><span>CUI</span><span>Denumire</span><span>Debit</span><span>Credit</span>
    </div>
    <div class="mig-sold-tabel" id="mig-sold-tabel"></div>
    <div class="mig-eroare" id="mig-eroare"></div>
    <button class="buton-primar mig-buton" id="mig-salveaza-part">Salvează partenerii</button>
  `;
  nav.setInapoi(() => wizardParteneri(corp, nav));

  const tabel = corp.querySelector("#mig-sold-tabel");
  tabel.innerHTML = randuri.map((r) => `
    <div class="mig-sold-rand mig-rand-part">
      <span class="mig-sold-cont">${esc(r.cont)}</span>
      <span class="mig-sold-cui">${esc(r.cui || "")}</span>
      <span class="mig-sold-den">${esc(r.denumire || "")}</span>
      <span class="mig-sold-val">${bani(r.debit)}</span>
      <span class="mig-sold-val">${bani(r.credit)}</span>
    </div>`).join("");

  corp.querySelector("#mig-salveaza-part").addEventListener("click", async () => {
    const eroare = corp.querySelector("#mig-eroare");
    const buton = corp.querySelector("#mig-salveaza-part");
    eroare.textContent = "";
    buton.disabled = true; buton.textContent = "Salvez…";
    try {
      await api.post(`/tenants/${firma.tenant_id}/parteneri`, { randuri });
      nav.deschide("Solduri parteneri", (cc, nn) => wizardParteneri(cc, nn));
    } catch (e) {
      eroare.textContent = (e && e.mesaj) || "Eroare la salvare.";
      buton.disabled = false; buton.textContent = "Salvează partenerii";
    }
  });
}


// ---------- STRAT 4: SALARIATI (per firma) ----------
async function wizardSalariati(corp, nav) {
  nav.setInapoi(() => meniuMigrare(corp, nav));
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se încarcă firmele…</p>`;
  let firme = [];
  try {
    const r = await api.get("/migrare/salariati");
    firme = (r && r.firme) || [];
  } catch {}

  const cuSal = firme.filter((f) => f.are_salariati).length;
  corp.innerHTML = `
    <p class="mig-intro">Importă salariații din vechea aplicație (nume, CNP, salariu, contract). CNP-urile se verifică automat — cele greșite sunt semnalate și sărite.</p>
    <div class="mig-progres">${cuSal} din ${firme.length} firme au salariați</div>
    <div class="mig-lista" id="mig-firme"></div>
    <button class="buton-primar mig-buton" id="mig-finalizeaza" style="margin-top:16px">Finalizează stratul Salariați</button>
  `;

  const lista = corp.querySelector("#mig-firme");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio firmă în portofoliu. Importă întâi firmele (stratul 1).</div>`;
  }
  firme.forEach((f) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${f.are_salariati ? `${f.randuri} salariați importați` : "fără salariați încă"}</div>
      </div>
      <span class="mig-stare ${f.are_salariati ? "mig-ok" : "mig-gri"}">${f.are_salariati ? "✓ gata" : "de încărcat"}</span>
    `;
    rand.addEventListener("click", () => nav.mergi("Import \u00b7 " + (f.nume || ""), (c) => importSalariatiFirma(c, nav, f)));  // faza_b3_migrare_v1
    lista.appendChild(rand);
  });

  corp.querySelector("#mig-finalizeaza").addEventListener("click", () => {
    const sumar = `<div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">Salariați: ${cuSal} din ${firme.length} firme</div>
    </div>`;
    randeazaDecizie(corp, nav, "salariati", sumar, "Importul salariaților e complet?");
  });
}

function importSalariatiFirma(corp, nav, firma) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>Încarcă exportul de salariați (nume · CNP · salariu · date contract).</p>
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" accept=".csv,.xlsx,.tsv" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#c2415f" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">Încarcă salariații</div>
      <div class="mig-drop-desc">Excel sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  const fileInput = corp.querySelector("#mig-file");
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    eroare.textContent = "Citesc salariații…";
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const r = await fetch(`/tenants/${firma.tenant_id}/salariati-import/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaSalariati(corp, nav, firma, date);
    } catch (e) {
      eroare.textContent = (e && e.mesaj) || "Eroare la citirea fișierului.";
    }
  });
}

function previzualizeazaSalariati(corp, nav, firma, date) {
  latime(corp, true);
  const randuri = date.randuri || [];

  const banda = date.invalizi > 0
    ? `<span class="mig-eq mig-eq-ok">${date.valizi} valizi</span> <span class="mig-eq mig-eq-no">${date.invalizi} cu CNP greșit (vor fi sărite)</span>`
    : `<span class="mig-eq mig-eq-ok">toate ${date.valizi} CNP-urile sunt corecte</span>`;

  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b> · salariați încărcați</p>
    <div class="mig-sold-rezumat"><b>${randuri.length}</b> salariați</div>
    <div class="mig-coer">${banda}</div>
    <div class="mig-sold-cap mig-cap-sal">
      <span>Nume</span><span>CNP</span><span>Funcție</span><span>Brut</span><span>Normă</span>
    </div>
    <div class="mig-sold-tabel" id="mig-sold-tabel"></div>
    <div class="mig-eroare" id="mig-eroare"></div>
    <button class="buton-primar mig-buton" id="mig-salveaza-sal">Salvează salariații</button>
  `;
  nav.setInapoi(() => wizardSalariati(corp, nav));

  const tabel = corp.querySelector("#mig-sold-tabel");
  tabel.innerHTML = randuri.map((r) => {
    const ok = r.cnp_valid;
    const cnpCell = ok
      ? `<span class="mig-cnp-ok">${esc(r.cnp)}</span>`
      : `<span class="mig-cnp-no" title="${esc(r.cnp_motiv)}">${esc(r.cnp || "—")} ⚠</span>`;
    const norma = r.tip_norma === "partiala" ? `parțială ${r.ore_zi}h` : "întreagă";
    return `
      <div class="mig-sold-rand mig-rand-sal ${ok ? "" : "mig-rand-invalid"}">
        <span class="mig-sold-den">${esc(r.nume)} ${esc(r.prenume)}</span>
        <span class="mig-sold-cnp">${cnpCell}</span>
        <span class="mig-sold-cor">${esc(r.cor || "")}</span>
        <span class="mig-sold-val">${bani(r.salariu_brut)}</span>
        <span class="mig-sold-norma">${norma}</span>
      </div>`;
  }).join("");

  corp.querySelector("#mig-salveaza-sal").addEventListener("click", async () => {
    const eroare = corp.querySelector("#mig-eroare");
    const buton = corp.querySelector("#mig-salveaza-sal");
    eroare.textContent = "";
    buton.disabled = true; buton.textContent = "Salvez…";
    try {
      const r = await api.post(`/tenants/${firma.tenant_id}/salariati-import`, { randuri });
      const nSar = r.sarite_cnp || 0;
      const _mergiLaSalariati = () => nav.deschide("Salariați", (cc, nn) => wizardSalariati(cc, nn));
      // [D1a] raporteaza VIZIBIL randurile sarite (CNP invalid) - confirmare blocanta, fara navigare
      // tacuta peste pierderea de date (ON CONFLICT/skip tacut nu e suficient).
      if (nSar > 0) {
        buton.disabled = false; buton.textContent = "Salvează salariații";
        confirmaCaseta(eroare,
          `${r.importati || 0} salariați importați · ${nSar} săriți (CNP invalid). Verifică fișierul pentru rândurile respinse.`,
          _mergiLaSalariati, { textOk: "Vezi salariații" });
      } else {
        _mergiLaSalariati();
      }
    } catch (e) {
      eroare.textContent = (e && e.mesaj) || "Eroare la salvare.";
      buton.disabled = false; buton.textContent = "Salvează salariații";
    }
  });
}


// ---------- STRAT 5: ASOCIATI (per firma) ----------
async function wizardAsociati(corp, nav) {
  nav.setInapoi(() => meniuMigrare(corp, nav));
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se încarcă firmele…</p>`;
  let firme = [];
  try {
    const r = await api.get("/migrare/asociati");
    firme = (r && r.firme) || [];
  } catch {}

  const cuAsoc = firme.filter((f) => f.are_asociati).length;
  corp.innerHTML = `
    <p class="mig-intro">Importă asociații firmei (nume, CNP/CUI, cotă %). Cotele se verifică automat — ar trebui să dea 100%.</p>
    <div class="mig-progres">${cuAsoc} din ${firme.length} firme au asociați</div>
    <div class="mig-lista" id="mig-firme"></div>
    <button class="buton-primar mig-buton" id="mig-finalizeaza" style="margin-top:16px">Finalizează stratul Asociați</button>
  `;

  const lista = corp.querySelector("#mig-firme");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio firmă în portofoliu. Importă întâi firmele (stratul 1).</div>`;
  }
  firme.forEach((f) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${f.are_asociati ? `${f.randuri} asociați importați` : "fără asociați încă"}</div>
      </div>
      <span class="mig-stare ${f.are_asociati ? "mig-ok" : "mig-gri"}">${f.are_asociati ? "✓ gata" : "de încărcat"}</span>
    `;
    rand.addEventListener("click", () => nav.mergi("Import \u00b7 " + (f.nume || ""), (c) => importAsociatiFirma(c, nav, f)));  // faza_b3_migrare_v1
    lista.appendChild(rand);
  });

  corp.querySelector("#mig-finalizeaza").addEventListener("click", () => {
    const sumar = `<div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">Asociați: ${cuAsoc} din ${firme.length} firme</div>
    </div>`;
    randeazaDecizie(corp, nav, "asociati", sumar, "Importul asociaților e complet?");
  });
}

function importAsociatiFirma(corp, nav, firma) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>Încarcă asociații (nume · CNP/CUI · cotă %).</p>
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" accept=".csv,.xlsx,.tsv" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#6d28d9" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">Încarcă asociații</div>
      <div class="mig-drop-desc">Excel sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  const fileInput = corp.querySelector("#mig-file");
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    eroare.textContent = "Citesc asociații…";
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const r = await fetch(`/tenants/${firma.tenant_id}/asociati-import/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaAsociati(corp, nav, firma, date);
    } catch (e) {
      eroare.textContent = (e && e.mesaj) || "Eroare la citirea fișierului.";
    }
  });
}

function previzualizeazaAsociati(corp, nav, firma, date) {
  latime(corp, true);
  const randuri = date.randuri || [];
  const coer = date.coerenta || { total: 0, coincide: false };
  
  const banda = coer.coincide
    ? `<span class="mig-eq mig-eq-ok">total cote: ✓ 100%</span>`
    : `<span class="mig-eq mig-eq-no">total cote: ⚠ ${baniRotund(coer.total)}%</span>`;

  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b> · asociați încărcați</p>
    <div class="mig-sold-rezumat"><b>${randuri.length}</b> asociați</div>
    <div class="mig-coer">${banda}</div>
    <div class="mig-sold-cap mig-cap-asoc">
      <span>Nume</span><span>CNP/CUI</span><span>Tip</span><span>Cotă %</span>
    </div>
    <div class="mig-sold-tabel" id="mig-sold-tabel"></div>
    <div class="mig-eroare" id="mig-eroare"></div>
    <button class="buton-primar mig-buton" id="mig-salveaza-asoc">Salvează asociații</button>
  `;
  nav.setInapoi(() => wizardAsociati(corp, nav));

  const tabel = corp.querySelector("#mig-sold-tabel");
  tabel.innerHTML = randuri.map((r) => {
    const cod = r.tip === "fizica"
      ? (r.cnp_valid ? `<span class="mig-cnp-ok">${esc(r.cnp)}</span>` : `<span class="mig-cnp-no" title="${esc(r.cnp_motiv)}">${esc(r.cnp)} ⚠</span>`)
      : `<span>${esc(r.cnp)}</span>`;
    const tip = r.tip === "juridica" ? "juridică" : "fizică";
    return `
      <div class="mig-sold-rand mig-rand-asoc">
        <span class="mig-sold-den">${esc(r.nume)}</span>
        <span class="mig-sold-cnp">${cod}</span>
        <span class="mig-sold-tip">${tip}</span>
        <span class="mig-sold-val">${(r.cota ?? "")}</span>
      </div>`;
  }).join("");

  corp.querySelector("#mig-salveaza-asoc").addEventListener("click", async () => {
    const eroare = corp.querySelector("#mig-eroare");
    const buton = corp.querySelector("#mig-salveaza-asoc");
    eroare.textContent = "";
    buton.disabled = true; buton.textContent = "Salvez…";
    try {
      await api.post(`/tenants/${firma.tenant_id}/asociati-import`, { randuri });
      nav.deschide("Asociați", (cc, nn) => wizardAsociati(cc, nn));
    } catch (e) {
      eroare.textContent = (e && e.mesaj) || "Eroare la salvare.";
      buton.disabled = false; buton.textContent = "Salvează asociații";
    }
  });
}


// ---------- STRAT 6: MIJLOACE FIXE (per firma) ----------
async function wizardMijloace(corp, nav) {
  nav.setInapoi(() => meniuMigrare(corp, nav));
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se încarcă firmele…</p>`;
  let firme = [];
  try {
    const r = await api.get("/migrare/mijloace-fixe");
    firme = (r && r.firme) || [];
  } catch {}

  const cuMF = firme.filter((f) => f.are_mijloace).length;
  corp.innerHTML = `
    <p class="mig-intro">Importă registrul de mijloace fixe (valoare, durată, valoare rămasă). Amortizarea cumulată se păstrează ca să nu reluăm de la zero.</p>
    <div class="mig-progres">${cuMF} din ${firme.length} firme au mijloace fixe</div>
    <div class="mig-lista" id="mig-firme"></div>
    <button class="buton-primar mig-buton" id="mig-finalizeaza" style="margin-top:16px">Finalizează stratul Mijloace fixe</button>
  `;

  const lista = corp.querySelector("#mig-firme");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio firmă în portofoliu. Importă întâi firmele (stratul 1).</div>`;
  }
  firme.forEach((f) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${f.are_mijloace ? `${f.randuri} mijloace fixe importate` : "fără mijloace fixe încă"}</div>
      </div>
      <span class="mig-stare ${f.are_mijloace ? "mig-ok" : "mig-gri"}">${f.are_mijloace ? "✓ gata" : "de încărcat"}</span>
    `;
    rand.addEventListener("click", () => nav.mergi("Import \u00b7 " + (f.nume || ""), (c) => importMijloaceFirma(c, nav, f)));  // faza_b3_migrare_v1
    lista.appendChild(rand);
  });

  corp.querySelector("#mig-finalizeaza").addEventListener("click", () => {
    const sumar = `<div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">Mijloace fixe: ${cuMF} din ${firme.length} firme</div>
    </div>`;
    randeazaDecizie(corp, nav, "mijloace_fixe", sumar, "Importul mijloacelor fixe e complet?");
  });
}

function importMijloaceFirma(corp, nav, firma) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>Încarcă registrul de mijloace fixe (cod · denumire · valoare · rezidual · durată · PIF · metodă).</p>
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" accept=".csv,.xlsx,.tsv" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#c0492b" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">Încarcă mijloacele fixe</div>
      <div class="mig-drop-desc">Excel sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  const fileInput = corp.querySelector("#mig-file");
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    eroare.textContent = "Citesc mijloacele fixe…";
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const r = await fetch(`/tenants/${firma.tenant_id}/mijloace-fixe-import/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaMijloace(corp, nav, firma, date);
    } catch (e) {
      eroare.textContent = (e && e.mesaj) || "Eroare la citirea fișierului.";
    }
  });
}

function previzualizeazaMijloace(corp, nav, firma, date) {
  latime(corp, true);
  const randuri = date.randuri || [];

  const banda = date.cu_avertismente > 0
    ? `<span class="mig-eq mig-eq-ok">${date.total - date.cu_avertismente} ok</span> <span class="mig-eq mig-eq-no">${date.cu_avertismente} cu avertisment</span>`
    : `<span class="mig-eq mig-eq-ok">toate ${date.total} corecte</span>`;

  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b> · mijloace fixe încărcate</p>
    <div class="mig-sold-rezumat">
      <b>${randuri.length}</b> mijloace · valoare <b>${bani(date.total_valoare)}</b> · rămas <b>${bani(date.total_rezidual)}</b>
    </div>
    <div class="mig-coer">${banda}</div>
    <div class="mig-sold-cap mig-cap-mf">
      <span>Cod</span><span>Denumire</span><span>Valoare</span><span>Rămas</span><span>Durată</span><span>Metodă</span>
    </div>
    <div class="mig-sold-tabel" id="mig-sold-tabel"></div>
    <div class="mig-eroare" id="mig-eroare"></div>
    <button class="buton-primar mig-buton" id="mig-salveaza-mf">Salvează mijloacele fixe</button>
  `;
  nav.setInapoi(() => wizardMijloace(corp, nav));

  const tabel = corp.querySelector("#mig-sold-tabel");
  tabel.innerHTML = randuri.map((r) => {
    const av = r.avertismente && r.avertismente.length
      ? `<span class="mig-cnp-no" title="${r.avertismente.join(', ')}"> ⚠</span>` : "";
    const luni = r.dnf_luni ? `${r.dnf_luni} luni` : "—";
    return `
      <div class="mig-sold-rand mig-rand-mf ${r.ok ? "" : "mig-rand-invalid"}">
        <span class="mig-sold-cont">${r.cod}</span>
        <span class="mig-sold-den">${esc(r.denumire)}${av}</span>
        <span class="mig-sold-val">${bani(r.valoare)}</span>
        <span class="mig-sold-val">${bani(r.rezidual)}</span>
        <span class="mig-sold-dur">${luni}</span>
        <span class="mig-sold-met">${r.metoda}</span>
      </div>`;
  }).join("");

  corp.querySelector("#mig-salveaza-mf").addEventListener("click", async () => {
    const eroare = corp.querySelector("#mig-eroare");
    const buton = corp.querySelector("#mig-salveaza-mf");
    eroare.textContent = "";
    buton.disabled = true; buton.textContent = "Salvez…";
    try {
      await api.post(`/tenants/${firma.tenant_id}/mijloace-fixe-import`, { randuri });
      nav.deschide("Mijloace fixe", (cc, nn) => wizardMijloace(cc, nn));
    } catch (e) {
      eroare.textContent = (e && e.mesaj) || "Eroare la salvare.";
      buton.disabled = false; buton.textContent = "Salvează mijloacele fixe";
    }
  });
}


// ---------- STRAT 7: ISTORIC DECLARATII (per firma) ----------
async function wizardIstoric(corp, nav) {
  nav.setInapoi(() => meniuMigrare(corp, nav));
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se încarcă firmele…</p>`;
  let firme = [];
  try {
    const r = await api.get("/migrare/istoric-declaratii");
    firme = (r && r.firme) || [];
  } catch {}

  const cuIst = firme.filter((f) => f.are_istoric).length;
  corp.innerHTML = `
    <p class="mig-intro">Importă declarațiile deja depuse anul curent (la vechiul program). Astfel iConta.eu nu le mai cere ca restanță.</p>
    <div class="mig-progres">${cuIst} din ${firme.length} firme au istoric</div>
    <div class="mig-lista" id="mig-firme"></div>
    <button class="buton-primar mig-buton" id="mig-finalizeaza" style="margin-top:16px">Finalizează stratul Istoric</button>
  `;

  const lista = corp.querySelector("#mig-firme");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio firmă în portofoliu. Importă întâi firmele (stratul 1).</div>`;
  }
  firme.forEach((f) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${f.are_istoric ? `${f.randuri} declarații înregistrate` : "fără istoric încă"}</div>
      </div>
      <span class="mig-stare ${f.are_istoric ? "mig-ok" : "mig-gri"}">${f.are_istoric ? "✓ gata" : "de încărcat"}</span>
    `;
    rand.addEventListener("click", () => nav.mergi("Import \u00b7 " + (f.nume || ""), (c) => importIstoricFirma(c, nav, f)));  // faza_b3_migrare_v1
    lista.appendChild(rand);
  });

  corp.querySelector("#mig-finalizeaza").addEventListener("click", () => {
    const sumar = `<div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">Istoric: ${cuIst} din ${firme.length} firme</div>
    </div>`;
    randeazaDecizie(corp, nav, "istoric_declaratii", sumar, "Istoricul declarațiilor e complet?");
  });
}

function importIstoricFirma(corp, nav, firma) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>Încarcă declarațiile depuse (tip · an · lună · data depunerii).</p>
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" accept=".csv,.xlsx,.tsv" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#45597f" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 13l2 2 4-4"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">Încarcă declarațiile</div>
      <div class="mig-drop-desc">Excel sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  const fileInput = corp.querySelector("#mig-file");
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    eroare.textContent = "Citesc declarațiile…";
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const r = await fetch(`/tenants/${firma.tenant_id}/istoric-declaratii-import/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaIstoric(corp, nav, firma, date);
    } catch (e) {
      eroare.textContent = (e && e.mesaj) || "Eroare la citirea fișierului.";
    }
  });
}

function previzualizeazaIstoric(corp, nav, firma, date) {
  latime(corp, true);
  const randuri = date.randuri || [];
  const luni = ["", "ian", "feb", "mar", "apr", "mai", "iun", "iul", "aug", "sep", "oct", "noi", "dec"];

  const banda = date.cu_avertismente > 0
    ? `<span class="mig-eq mig-eq-ok">${date.total - date.cu_avertismente} ok</span> <span class="mig-eq mig-eq-no">${date.cu_avertismente} cu avertisment</span>`
    : `<span class="mig-eq mig-eq-ok">toate ${date.total} recunoscute</span>`;

  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b> · istoric declarații</p>
    <div class="mig-sold-rezumat"><b>${randuri.length}</b> declarații depuse</div>
    <div class="mig-coer">${banda}</div>
    <div class="mig-sold-cap mig-cap-ist">
      <span>Tip</span><span>An</span><span>Lună</span><span>Data depunerii</span>
    </div>
    <div class="mig-sold-tabel" id="mig-sold-tabel"></div>
    <div class="mig-eroare" id="mig-eroare"></div>
    <button class="buton-primar mig-buton" id="mig-salveaza-ist">Salvează istoricul</button>
  `;
  nav.setInapoi(() => wizardIstoric(corp, nav));

  const tabel = corp.querySelector("#mig-sold-tabel");
  tabel.innerHTML = randuri.map((r) => {
    const av = r.avertisment && r.avertisment.length
      ? `<span class="mig-cnp-no" title="${r.avertisment.join(', ')}"> ⚠</span>` : "";
    const tipCls = r.tip_cunoscut ? "mig-cnp-ok" : "mig-cnp-no";
    const lunaTxt = (r.luna >= 1 && r.luna <= 12) ? luni[r.luna] : (r.luna || "—");
    return `
      <div class="mig-sold-rand mig-rand-ist ${r.ok ? "" : "mig-rand-invalid"}">
        <span class="mig-sold-cont ${tipCls}">${r.tip}${av}</span>
        <span class="mig-sold-an">${r.an || "—"}</span>
        <span class="mig-sold-luna">${lunaTxt}</span>
        <span class="mig-sold-den">${dataRo(r.data_depunere) || "—"}</span>
      </div>`;
  }).join("");

  corp.querySelector("#mig-salveaza-ist").addEventListener("click", async () => {
    const eroare = corp.querySelector("#mig-eroare");
    const buton = corp.querySelector("#mig-salveaza-ist");
    eroare.textContent = "";
    buton.disabled = true; buton.textContent = "Salvez…";
    try {
      await api.post(`/tenants/${firma.tenant_id}/istoric-declaratii-import`, { randuri });
      nav.deschide("Istoric declarații", (cc, nn) => wizardIstoric(cc, nn));
    } catch (e) {
      eroare.textContent = (e && e.mesaj) || "Eroare la salvare.";
      buton.disabled = false; buton.textContent = "Salvează istoricul";
    }
  });
}

// faza_b3_migrare_v1

// ---------- WIZARD PLAN DE CONTURI [p95_plan_conturi] ----------
async function wizardPlanConturi(corp, nav) {
  nav.setInapoi(() => meniuMigrare(corp, nav));
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103 firmele\u2026</p>`;
  let firme = [];
  try {
    const r = await api.get("/migrare/plan-conturi");
    firme = (r && r.firme) || [];
  } catch {}
  corp.innerHTML = `
    <p class="mig-intro">Planul standard OMFP e deja \u00eencărcat automat la fiecare firm\u0103. Aici adaugi conturi analitice sau nestandard (ex: leasing IFRS) pentru firme cu nevoi speciale.</p>
    <div class="mig-lista" id="mig-firme"></div>
    <button class="buton-primar mig-buton" id="mig-finalizeaza" style="margin-top:16px">Finalizeaz\u0103 stratul Plan de conturi</button>
  `;
  const lista = corp.querySelector("#mig-firme");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio firm\u0103 \u00een portofoliu. Import\u0103 \u00eent\u00e2i firmele (stratul 1).</div>`;
  }
  firme.forEach((f) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${f.nr_conturi} conturi \u00een plan</div>
      </div>
      <span class="mig-stare ${f.nr_conturi > 0 ? "mig-ok" : "mig-gri"}">${f.nr_conturi > 0 ? "\u2713 populat" : "gol"}</span>
    `;
    rand.addEventListener("click", () => nav.mergi("Plan de conturi \u00b7 " + (f.nume || ""), (c) => importPlanConturiFirma(c, nav, f)));
    lista.appendChild(rand);
  });
  corp.querySelector("#mig-finalizeaza").addEventListener("click", () => {
    const sumar = `<div class="mig-gata">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">Plan de conturi: ${firme.length} firme verificate</div>
    </div>`;
    randeazaDecizie(corp, nav, "plan_conturi", sumar, "Planul de conturi e complet pentru toate firmele?");
  });
}
function importPlanConturiFirma(corp, nav, firma) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>Caut\u0103 \u00een planul existent sau adaug\u0103 un cont nou.</p>
    <input type="text" class="camp-input" id="pc-cauta" aria-label="Caut\u0103 \u00een plan" placeholder="Caut\u0103 dup\u0103 simbol sau denumire\u2026" style="width:100%;margin-bottom:10px">
    <div class="mig-lista" id="pc-rezultate"></div>
    <div class="mig-eticheta" style="margin-top:16px">Adaug\u0103 cont nou</div>
    <div style="display:flex;gap:8px;margin-top:6px">
      <input type="text" class="camp-input" id="pc-simbol" aria-label="Simbol cont" placeholder="Simbol (ex: 4428)" style="width:140px">
      <input type="text" class="camp-input" id="pc-denumire" aria-label="Denumire cont" placeholder="Denumire" style="flex:1">
    </div>
    <div class="mig-eroare" id="pc-eroare"></div>
    <button class="buton-primar mig-buton" id="pc-adauga" style="margin-top:10px">Adaug\u0103 cont</button>
  `;
  const rezZona = corp.querySelector("#pc-rezultate");
  const cautaInput = corp.querySelector("#pc-cauta");
  async function cauta(q) {
    rezZona.innerHTML = `<p class="ecran-nota">Se caut\u0103\u2026</p>`;
    try {
      const r = await api.get(`/tenants/${firma.tenant_id}/plan-conturi${q ? "?q=" + encodeURIComponent(q) : ""}`);
      const conturi = (r && r.conturi) || [];
      rezZona.innerHTML = conturi.length
        ? conturi.map((c) => `<div class="mig-frand" style="cursor:default">
            <div class="mig-frand-text">
              <div class="mig-frand-nume">${esc(c.simbol)} \u00b7 ${esc(c.denumire)}</div>
              <div class="mig-frand-sub">${c.tip || ""}</div>
            </div>
          </div>`).join("")
        : `<div class="stare-goala">Niciun cont g\u0103sit cu acest termen.</div>`;
    } catch {
      arataMesaj(rezZona, "Eroare la căutare.", "eroare");
    }
  }
  cauta("");
  let timer = null;
  cautaInput.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => cauta(cautaInput.value.trim()), 300);
  });
  corp.querySelector("#pc-adauga").addEventListener("click", async () => {
    const eroare = corp.querySelector("#pc-eroare");
    eroare.textContent = "";
    const simbol = corp.querySelector("#pc-simbol").value.trim();
    const denumire = corp.querySelector("#pc-denumire").value.trim();
    if (!simbol || !denumire) { eroare.textContent = "Simbol \u0219i denumire sunt obligatorii."; return; }
    try {
      await api.post(`/tenants/${firma.tenant_id}/plan-conturi`, { simbol, denumire });
      corp.querySelector("#pc-simbol").value = "";
      corp.querySelector("#pc-denumire").value = "";
      cauta(cautaInput.value.trim());
    } catch (e) {
      eroare.textContent = (e && e.mesaj) || "Eroare la salvare.";
    }
  });
}

// ---------- MENIU MIGRARE PER FIRMA [p96_import_firma] ----------
// Deschis din fisa unei firme (cardul "Import date") - sare peste pasul de
// selectie a firmei, duce direct in ecranul de import per-strat pentru firma curenta.
export async function meniuMigrarePerFirma(corp, nav, firma) {
  nav.setInapoi(null);
  latime(corp, false);
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;
  // [p_pfa_rip 20.07] Straturile aplicabile regimului vin din backend (straturi_pentru), SURSA UNICA -
  // meniul NU reinventeaza in JS ce strat apartine carui regim (nu deriva din regim_contabil aici).
  // Pasii cu 'strat' apar doar daca stratul e aplicabil; pasii fara 'strat' (articole/retete) raman mereu.
  const tip = firma.tip_firma.toLowerCase();   // backendul garanteaza tip_firma; fara fallback tacit
  let aplicabile = null;
  try {
    const r = await api.get(`/migrare/straturi?tip_firma=${encodeURIComponent(tip)}`);
    aplicabile = (r && r.straturi) || null;
  } catch {}
  if (!aplicabile || !aplicabile.length) {
    // straturi_pentru nu a raspuns -> NU ghicim filtrarea in JS (un PFA ar vedea pasii de partida dubla).
    // Stare-goala canonica + reincercare, nu "arata tot".
    corp.innerHTML = `<div class="stare-goala">Nu am putut încărca pașii de import pentru firmă.
      <button class="btn-link" id="mig-reincearca">Reîncearcă</button></div>`;
    corp.querySelector("#mig-reincearca").addEventListener("click", () => meniuMigrarePerFirma(corp, nav, firma));
    return;
  }
  const PASI = [
    { titlu: "Vector fiscal", desc: "TVA, regim, intracomunitar", strat: "vector_fiscal", fn: (c, n) => formularVectorFirma(c, n, firma) },
    { titlu: "Solduri ini\u021biale", desc: "Balan\u021ba de deschidere", strat: "solduri", fn: (c, n) => importSolduriFirma(c, n, firma) },
    { titlu: "Solduri parteneri", desc: "4111/401 pe client \u0219i furnizor", strat: "solduri_parteneri", fn: (c, n) => importParteneriFirma(c, n, firma) },
    { titlu: "Salaria\u021bi", desc: "Nume, CNP, salariu, contract", strat: "salariati", fn: (c, n) => importSalariatiFirma(c, n, firma) },
    { titlu: "Asocia\u021bi", desc: "Nume, cot\u0103 % (D205)", strat: "asociati", fn: (c, n) => importAsociatiFirma(c, n, firma) },
    { titlu: "Mijloace fixe", desc: "Registru amortizare", strat: "mijloace_fixe", fn: (c, n) => importMijloaceFirma(c, n, firma) },
    { titlu: "Istoric declara\u021bii", desc: "Ce s-a depus deja", strat: "istoric_declaratii", fn: (c, n) => importIstoricFirma(c, n, firma) },
    { titlu: "Plan de conturi", desc: "Cont\u0103 analitice/nestandard", strat: "plan_conturi", fn: (c, n) => importPlanConturiFirma(c, n, firma) },
    { titlu: "Articole \u0219i stoc ini\u021bial", desc: "Nomenclator + cantit\u0103\u021bi la CMP (gestiune CV)", fn: (c, n) => importArticoleFirma(c, n, firma) },
    { titlu: "Re\u021bete (HoReCa)", desc: "Re\u021betar: ingrediente \u0219i cantit\u0103\u021bi pe por\u021bie", fn: (c, n) => importReteteFirma(c, n, firma) },
  ];
  // [p_pfa_rip 20.07] Pas DOAR pentru PFA (partida simpla): registru incasari-plati.
  // Gated explicit pe tip==='pfa' (robust chiar daca /migrare/straturi pica).
  if (tip === "pfa") {
    PASI.push({ titlu: "Import RIP", desc: "Registru \u00eencas\u0103ri-pl\u0103\u021bi (istoric PFA, partid\u0103 simpl\u0103)", strat: "rip", fn: (c, n) => importRipFirma(c, n, firma) });
  }
  // ascunde straturile neaplicabile regimului (ex: PFA nu vede partida dubla). aplicabile = garantat
  // non-null aici (altfel am iesit mai sus cu stare-goala) -> filtram mereu, fara "arata tot".
  const pasiVizibili = PASI.filter((p) => !p.strat || aplicabile.includes(p.strat));
  corp.innerHTML = `
    <p class="mig-intro">Alege ce vrei s\u0103 aduci pentru aceast\u0103 firm\u0103.</p>
    <div class="mig-lista" id="mig-pasi"></div>
  `;
  const lista = corp.querySelector("#mig-pasi");
  pasiVizibili.forEach((p) => {
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${p.titlu}</div>
        <div class="mig-frand-sub">${p.desc}</div>
      </div>
    `;
    rand.addEventListener("click", () => nav.mergi(p.titlu, (c) => p.fn(c, nav)));  // titlul = pasul; firma e in antet (fisa) sau in intro (drum cabinet) - DS cap.1
    lista.appendChild(rand);
  });
}

// [F150] Import retete HoReCa (pasul 11)
function importReteteFirma(corp, nav, firma) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>\u00cencarc\u0103 re\u021betarul: un r\u00e2nd per ingredient (re\u021bet\u0103 \u00b7 pre\u021b v\u00e2nzare \u00b7 ingredient \u00b7 cantitate/por\u021bie). Ingredientele se potrivesc pe articolele din stoc dup\u0103 denumire.</p>
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" accept=".csv,.xlsx,.tsv" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#0a807b" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">\u00cencarc\u0103 re\u021betele</div>
      <div class="mig-drop-desc">Excel sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  const fileInput = corp.querySelector("#mig-file");
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    arataMesaj(eroare, "Citesc re\u021betele\u2026", "info");
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const r = await fetch(`/tenants/${firma.tenant_id}/retete-import/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaRetete(corp, nav, firma, date);
    } catch (e) {
      arataMesaj(eroare, (e && e.mesaj) || "Eroare la citirea fi\u0219ierului.", "eroare");
    }
  });
}

function previzualizeazaRetete(corp, nav, firma, date) {
  latime(corp, true);
  const retete = date.retete || [];
  const rez = date.rezumat || {};
  const zona = corp.querySelector("#mig-preview");
  zona.innerHTML = `
    <div class="mig-eticheta" style="margin-top:10px">${rez.valide || 0} re\u021bete valide din ${rez.total || 0} \u00b7 ${rez.ingrediente || 0} ingrediente${rez.invalide ? ` \u00b7 <span style="color:var(--rosu)">${rez.invalide} invalide</span>` : ""}</div>
    <div class="mig-lista">
      ${retete.slice(0, 50).map((rt) => `
        <div class="mig-rand${rt.valid ? "" : " mig-rand-rosu"}">
          <span>${esc(rt.denumire)} \u00b7 ${rt.linii.length} ingrediente</span>
          <span>${bani(rt.pret || 0)} lei${rt.valid ? "" : " \u00b7 " + esc(rt.motiv)}</span>
        </div>`).join("")}
      ${retete.length > 50 ? `<div class="mig-eticheta">\u2026 \u0219i \u00eenc\u0103 ${retete.length - 50}</div>` : ""}
    </div>
    <button class="buton-primar mig-buton" id="mig-importa">Import\u0103 ${rez.valide || 0} re\u021bete</button>
  `;
  zona.querySelector("#mig-importa").addEventListener("click", async () => {
    const b = zona.querySelector("#mig-importa");
    b.disabled = true; b.textContent = "Import\u2026";
    try {
      const r = await api.post(`/tenants/${firma.tenant_id}/retete-import`, { retete });
      arataMesaj(zona, `${r.create} re\u021bete importate${r.sarite && r.sarite.length ? ` \u00b7 ${r.sarite.length} s\u0103rite (existente/invalide)` : ""}`, "ok");
    } catch (e) {
      b.disabled = false; b.textContent = "Import\u0103";
      arataMesaj(corp.querySelector("#mig-eroare"), (e && e.mesaj) || "Eroare la import.", "eroare");
    }
  });
}

// [F151] Import articole + stoc initial CV (pasul 10)
function importArticoleFirma(corp, nav, firma) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>\u00cencarc\u0103 nomenclatorul de articole cu stocul ini\u021bial (denumire \u00b7 UM \u00b7 cantitate \u00b7 pre\u021b unitar).</p>
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" accept=".csv,.xlsx,.tsv" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#0a807b" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">\u00cencarc\u0103 articolele</div>
      <div class="mig-drop-desc">Excel sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  const fileInput = corp.querySelector("#mig-file");
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    arataMesaj(eroare, "Citesc articolele\u2026", "info");
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const r = await fetch(`/tenants/${firma.tenant_id}/articole-import/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaArticole(corp, nav, firma, date);
    } catch (e) {
      arataMesaj(eroare, (e && e.mesaj) || "Eroare la citirea fi\u0219ierului.", "eroare");
    }
  });
}

function previzualizeazaArticole(corp, nav, firma, date) {
  latime(corp, true);
  const randuri = date.randuri || [];
  const rez = date.rezumat || {};
  const zona = corp.querySelector("#mig-preview");
  zona.innerHTML = `
    <div class="mig-eticheta" style="margin-top:10px">${rez.valide || 0} articole valide \u00b7 ${rez.cu_stoc || 0} cu stoc \u00b7 valoare total\u0103 ${bani(rez.valoare_totala || 0)} lei${rez.invalide ? ` \u00b7 <span style="color:var(--rosu)">${rez.invalide} invalide</span>` : ""}</div>
    <div class="mig-lista">
      ${randuri.slice(0, 50).map((a) => `
        <div class="mig-rand${a.valid ? "" : " mig-rand-rosu"}">
          <span>${esc(a.denumire)} \u00b7 ${esc(a.um)}</span>
          <span>${a.cantitate} \u00d7 ${bani(a.pret)} lei${a.valid ? "" : " \u00b7 " + esc(a.motiv)}</span>
        </div>`).join("")}
      ${randuri.length > 50 ? `<div class="mig-eticheta">\u2026 \u0219i \u00eenc\u0103 ${randuri.length - 50}</div>` : ""}
    </div>
    <button class="buton-primar mig-buton" id="mig-importa">Import\u0103 ${rez.valide || 0} articole</button>
  `;
  zona.querySelector("#mig-importa").addEventListener("click", async () => {
    const b = zona.querySelector("#mig-importa");
    b.disabled = true; b.textContent = "Import\u2026";
    try {
      const r = await api.post(`/tenants/${firma.tenant_id}/articole-import`, { randuri });
      arataMesaj(zona, `${r.create} articole importate${r.sarite && r.sarite.length ? ` \u00b7 ${r.sarite.length} s\u0103rite (existente/invalide)` : ""}`, "ok");
    } catch (e) {
      b.disabled = false; b.textContent = "Import\u0103";
      arataMesaj(corp.querySelector("#mig-eroare"), (e && e.mesaj) || "Eroare la import.", "eroare");
    }
  });
}

// [p_pfa_rip 20.07] Import registru incasari-plati (RIP) \u2014 preluare PFA (partida simpla).
// Istoric cronologic al anului curent, NU balanta de deschidere. Ruta importa imediat
// (un singur pas): randurile ambigue/incomplete se RAPORTEAZA, cele valide se scriu.
function importRipFirma(corp, nav, firma) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b><br>\u00cencarc\u0103 registrul de \u00eencas\u0103ri-pl\u0103\u021bi (istoric cronologic: dat\u0103 \u00b7 tip \u00b7 explica\u021bie \u00b7 sum\u0103 \u00b7 categorie \u00b7 metod\u0103). Partida simpl\u0103 nu are balan\u021b\u0103 de deschidere \u2014 soldul rezult\u0103 din opera\u021biuni.</p>
    <label class="mig-drop" id="mig-drop">
      <input type="file" id="mig-file" accept=".csv,.xlsx,.tsv" hidden>
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#16a34a" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6M9 14l3-3 3 3"/></svg>
      <div class="mig-drop-titlu" id="mig-drop-titlu">\u00cencarc\u0103 registrul</div>
      <div class="mig-drop-desc">Excel sau CSV</div>
    </label>
    <div class="mig-eroare" id="mig-eroare"></div>
    <div id="mig-preview"></div>
  `;
  const fileInput = corp.querySelector("#mig-file");
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    corp.querySelector("#mig-drop-titlu").textContent = file.name;
    const eroare = corp.querySelector("#mig-eroare");
    arataMesaj(eroare, "Import registru \u00eencas\u0103ri-pl\u0103\u021bi\u2026", "info");
    try {
      const fd = new FormData();
      fd.append("fisier", file);
      const r = await fetch(`/tenants/${firma.tenant_id}/rip-import/incarca`, {
        method: "POST", headers: { "Authorization": "Bearer " + sesiune.token() }, body: fd,
      });
      const date = await r.json();
      if (!r.ok) throw { mesaj: (date && (date.detail || date.mesaj)) || ("eroare " + r.status) };
      eroare.textContent = "";
      previzualizeazaRip(corp, nav, firma, date);
    } catch (e) {
      arataMesaj(eroare, (e && e.mesaj) || "Eroare la import.", "eroare");
    }
  });
}

function previzualizeazaRip(corp, nav, firma, date) {
  latime(corp, true);
  const raport = date.raport || {};
  const respinse = raport.respinse || [];
  const importate = date.importate || 0;
  const dubluri = date.sarite_duplicat || 0;
  const banda = [
    `<span class="mig-eq mig-eq-ok">${importate} importate</span>`,
    dubluri ? `<span class="mig-eq mig-eq-gri">${dubluri} deja existente (s\u0103rite)</span>` : "",
    respinse.length ? `<span class="mig-eq mig-eq-no">${respinse.length} respinse</span>` : "",
  ].filter(Boolean).join(" ");
  const zona = corp.querySelector("#mig-preview");
  zona.innerHTML = `
    <div class="mig-sold-rezumat"><b>${importate}</b> opera\u021biuni importate${dubluri ? ` \u00b7 ${dubluri} s\u0103rite (deja \u00een registru)` : ""}${raport.metoda_prezumata ? ` \u00b7 ${raport.metoda_prezumata} cu metod\u0103 prezumat\u0103 (banc\u0103)` : ""}</div>
    <div class="mig-coer">${banda}</div>
    ${respinse.length ? `
      <div class="mig-eticheta" style="margin-top:10px">R\u00e2nduri respinse (de corectat \u00een fi\u0219ier \u0219i re\u00eenc\u0103rcat):</div>
      <div class="mig-lista">
        ${respinse.map((x) => `<div class="mig-rand mig-rand-rosu"><span>R\u00e2nd ${x.rand}</span><span>${esc(x.motiv)}</span></div>`).join("")}
      </div>` : `<p class="mig-intro" style="margin-top:10px">Registrul a fost preluat integral. Stratul RIP e marcat ca gata.</p>`}
  `;
  nav.setInapoi(() => meniuMigrarePerFirma(corp, nav, firma));
}
