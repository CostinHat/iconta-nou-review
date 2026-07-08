// declaratii.js — ecran asistent: creeaza o declaratie -> trimite in coada de validare.
// Flux 3 pasi intr-o fereastra: 1) firma+tip+perioada  2) genereaza+verifica  3) trimite in coada.
// inceput_la porneste la deschiderea ecranului (cronometru efort) si merge la /coada.
// Backend: GET /tenants, GET /declaratii/tipuri, POST /declaratii/{tip}, POST /coada.

import { api } from "../api.js";

const LUNI = ["ianuarie","februarie","martie","aprilie","mai","iunie",
              "iulie","august","septembrie","octombrie","noiembrie","decembrie"];
const TRIM = ["T1 (ian-mar)","T2 (apr-iun)","T3 (iul-sep)","T4 (oct-dec)"];

// stare ecran
let S = null;

function esc(s){ return String(s ?? "").replace(/[&<>"]/g,(c)=>({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;" }[c])); }

export async function randeazaDeclaratii(corp, nav) {
  if (nav && nav.setInapoi) nav.setInapoi(undefined);
  const acum = new Date();
  S = {
    inceput_la: acum.toISOString(),          // cronometru efort (datoria p15)
    pas: 1,
    firme: [], tipuri: [], periodicitate: {},
    tenant_id: null, tip: null,
    an: acum.getFullYear(),
    luna: acum.getMonth() + 1,
    trim: Math.floor(acum.getMonth()/3) + 1,
    rezultat: null,                          // {xml, avertismente}
  };
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  try {
    const [t, d] = await Promise.all([ api.get("/tenants"), api.get("/declaratii/tipuri") ]);
    S.firme = Array.isArray(t) ? t : (t.tenants || t.firme || []);
    S.tipuri = d.tipuri || [];
    S.periodicitate = d.periodicitate || {};
  } catch {
    corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca firmele sau tipurile de declarații.</p>`;
    return;
  }
  pas1(corp, nav);
}

// ---------- PAS 1: firma + tip + perioada ----------
function pas1(corp, nav) {
  if (nav && nav.setInapoi) nav.setInapoi(undefined);
  const f = corp.closest(".fereastra"); if (f) f.classList.remove("fer-larg");
  S.pas = 1;
  const per = S.tip ? S.periodicitate[S.tip] : null;

  corp.innerHTML = `
    <p class="mig-intro">Pasul 1 din 3 — alege firma, tipul declarației și perioada.</p>
    <div class="dec-form">
      <label class="dec-camp">
        <span class="dec-eticheta">Firmă</span>
        <select id="dec-firma" class="dec-select">
          <option value="">— alege firma —</option>
          ${S.firme.map((fr) => `<option value="${fr.id}" ${fr.id===S.tenant_id?"selected":""}>${esc(fr.nume || fr.denumire || ("Firma "+fr.id))}</option>`).join("")}
        </select>
      </label>
      <label class="dec-camp">
        <span class="dec-eticheta">Tip declarație</span>
        <select id="dec-tip" class="dec-select">
          <option value="">— alege tipul —</option>
          ${S.tipuri.map((tp) => `<option value="${tp}" ${tp===S.tip?"selected":""}>${tp.toUpperCase()} · ${S.periodicitate[tp]||""}</option>`).join("")}
        </select>
      </label>
      <div id="dec-perioada">${randPerioada(per)}</div>
    </div>
    <div class="dec-bara">
      <button class="buton-primar" id="dec-continua" disabled>Continuă →</button>
    </div>
  `;

  const selFirma = corp.querySelector("#dec-firma");
  const selTip = corp.querySelector("#dec-tip");
  const cont = corp.querySelector("#dec-continua");
  const zonaP = corp.querySelector("#dec-perioada");

  function refresh() {
    S.tenant_id = selFirma.value ? parseInt(selFirma.value) : null;
    S.tip = selTip.value || null;
    const p = S.tip ? S.periodicitate[S.tip] : null;
    zonaP.innerHTML = randPerioada(p);
    legPerioada(zonaP);
    cont.disabled = !(S.tenant_id && S.tip);
  }
  selFirma.addEventListener("change", refresh);
  selTip.addEventListener("change", refresh);
  legPerioada(zonaP);
  cont.addEventListener("click", () => pas2(corp, nav));
  refresh();
}

function randPerioada(per) {
  if (!per) return "";
  const an = `<label class="dec-camp dec-camp-mic">
      <span class="dec-eticheta">An</span>
      <input id="dec-an" class="dec-input" type="number" min="2020" max="2030" value="${S.an}">
    </label>`;
  if (per === "anual") return `<div class="dec-perioada-rand">${an}</div>`;
  if (per === "trimestrial") {
    return `<div class="dec-perioada-rand">${an}
      <label class="dec-camp dec-camp-mic">
        <span class="dec-eticheta">Trimestru</span>
        <select id="dec-trim" class="dec-select">
          ${TRIM.map((t,i)=>`<option value="${i+1}" ${i+1===S.trim?"selected":""}>${t}</option>`).join("")}
        </select>
      </label></div>`;
  }
  // lunar
  return `<div class="dec-perioada-rand">${an}
    <label class="dec-camp dec-camp-mic">
      <span class="dec-eticheta">Lună</span>
      <select id="dec-luna" class="dec-select">
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
    S.rezultat = await api.post(`/declaratii/${S.tip}`, body);
  } catch (e) {
    corp.innerHTML = `
      <p class="mig-intro">Pasul 2 din 3 — generare</p>
      <div class="dec-eroare">Nu am putut genera declarația. Verifică datele firmei pentru perioada aleasă.</div>
      <div class="dec-bara"><button class="buton-secundar" id="dec-inapoi">\u2190</button></div>`;
    corp.querySelector("#dec-inapoi").addEventListener("click", () => pas1(corp, nav));
    return;
  }

  const f = corp.closest(".fereastra"); if (f) f.classList.add("fer-larg");
  const avert = S.rezultat.avertismente || [];
  const xml = S.rezultat.xml || "";

  corp.innerHTML = `
    <p class="mig-intro">Pasul 2 din 3 — verifică <b>${S.tip.toUpperCase()}</b> · ${etPerioada()}</p>
    ${avert.length ? `<div class="dec-avert">
        <div class="dec-avert-cap">Avertismente (${avert.length})</div>
        <ul>${avert.map((a)=>`<li>${esc(typeof a==="string"?a:(a.mesaj||JSON.stringify(a)))}</li>`).join("")}</ul>
      </div>` : `<div class="dec-ok">Fără avertismente. Declarația pare în regulă.</div>`}
    <details class="dec-xml">
      <summary>Vezi XML-ul generat</summary>
      <pre class="dec-xml-pre">${esc(xml)}</pre>
    </details>
    <div class="dec-bara">
      <button class="buton-secundar" id="dec-inapoi">\u2190</button>
      <button class="buton-primar" id="dec-trimite">Trimite în coadă →</button>
    </div>
  `;
  corp.querySelector("#dec-inapoi").addEventListener("click", () => pas1(corp, nav));
  corp.querySelector("#dec-trimite").addEventListener("click", () => pas3(corp, nav));
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
    alert("Nu am putut trimite în coadă. Poate există deja o declarație pentru această perioadă.");
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
  if (per === "trimestrial") return `${TRIM[S.trim-1]} ${S.an}`;
  return `${LUNI[S.luna-1]} ${S.an}`;
}
