// declaratii.js — ecran asistent: creeaza o declaratie -> trimite in coada de validare.
// Flux 3 pasi intr-o fereastra: 1) firma+tip+perioada  2) genereaza+verifica  3) trimite in coada.
// inceput_la porneste la deschiderea ecranului (cronometru efort) si merge la /coada.
// Backend: GET /tenants, GET /declaratii/tipuri, POST /declaratii/{tip}/valideaza, POST /coada.
// [duk_valideaza_v1] Pasul 2 VALIDEAZA la ANAF (DUKIntegrator), nu doar genereaza:
// pana la 15.07.2026 spunea "declaratia pare in regula" fara sa fi validat nimic,
// iar asistentul trimitea in coada un XML nevalidat. Trei stari: valid/erori/gri.

import { api, esc } from "../api.js";

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
    firme: [], tipuri: [], periodicitate: {},
    firmaFixa: firmaFixa || null,
    tenant_id: firmaFixa ? firmaFixa.tenant_id : null, tip: null,
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
${S.firmaFixa ? "" : `      <label class="camp">
        <span class="camp-eticheta">Firmă</span>
        <select id="dec-firma" class="camp-input">
          <option value="">— alege firma —</option>
          ${S.firme.map((fr) => `<option value="${fr.id}" ${fr.id===S.tenant_id?"selected":""}>${esc(fr.nume || fr.denumire || ("Firma "+fr.id))}</option>`).join("")}
        </select>
      </label>`}
      <label class="camp">
        <span class="camp-eticheta">Tip declarație</span>
        <select id="dec-tip" class="camp-input">
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

  const selFirma = corp.querySelector("#dec-firma");  // null cand firma e fixa [decl_firma_v1]
  const selTip = corp.querySelector("#dec-tip");
  const cont = corp.querySelector("#dec-continua");
  const zonaP = corp.querySelector("#dec-perioada");

  function refresh() {
    if (selFirma) S.tenant_id = selFirma.value ? parseInt(selFirma.value) : null;
    S.tip = selTip.value || null;
    const p = S.tip ? S.periodicitate[S.tip] : null;
    zonaP.innerHTML = randPerioada(p);
    legPerioada(zonaP);
    cont.disabled = !(S.tenant_id && S.tip);
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
    corp.innerHTML = `
      <p class="mig-intro">Pasul 2 din 3 — generare</p>
      <div class="dec-eroare">Nu am putut genera declarația. Verifică datele firmei pentru perioada aleasă.</div>
      `;
    return;
  }

  const f = corp.closest(".fereastra"); if (f) f.classList.add("fer-larg");
  const avert = S.rezultat.avertismente || [];
  const xml = S.rezultat.xml_b64 ? _dinB64(S.rezultat.xml_b64) : (S.rezultat.xml || "");
  const stare = S.rezultat.stare || "gri";
  const erANAF = (S.rezultat.erori || "").trim();
  const blocANAF = stare === "valid"
    ? `<div class="dec-ok">Validat la ANAF, fără erori.</div>`
    : (stare === "erori"
        ? `<div class="dec-eroare">
             <div class="dec-avert-cap">Validatorul ANAF a găsit erori</div>
             <pre class="dec-xml-pre">${esc(erANAF)}</pre>
           </div>`
        : `<div class="dec-avert">
             <div class="dec-avert-cap">Nu am putut valida la ANAF</div>
             <ul><li>${esc(S.rezultat.temei || "Validatorul nu a rulat.")}</li>
                 <li>${esc(S.rezultat.limita || "")}</li></ul>
           </div>`);

  corp.innerHTML = `
    <p class="mig-intro">Pasul 2 din 3 — verifică <b>${S.tip.toUpperCase()}</b> · ${etPerioada()}</p>
    ${blocANAF}
    ${avert.length ? `<div class="dec-avert">
        <div class="dec-avert-cap">Avertismente (${avert.length})</div>
        <ul>${avert.map((a)=>`<li>${esc(typeof a==="string"?a:(a.mesaj||JSON.stringify(a)))}</li>`).join("")}</ul>
      </div>` : ""}
    <details class="dec-xml">
      <summary>Vezi XML-ul generat</summary>
      <pre class="dec-xml-pre">${esc(xml)}</pre>
    </details>
    <div class="dec-bara">
      <button class="buton-primar" id="dec-trimite">Trimite în coadă →</button>
    </div>
    <p class="ecran-nota">${esc(S.rezultat.limita || "")}</p>
  `;
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
  if (per === "trimestrial") return `${TRIM[S.trim-1]} ${S.an}`;
  return `${LUNI[S.luna-1]} ${S.an}`;
}

// audit_cab_lot1_v1
