// pachete.js — Pachetul lunar / Povestea lunii.
// Flux: alegi firma+luna -> vezi rezumatul -> "Genereaza povestea" (AI) -> editezi -> aprobi -> trimiti.
// Backend: GET /tenants, GET /pachete/{tid}/rezumat, POST /pachete/{tid}/genereaza,
//          GET+POST /pachete/{tid}/poveste, POST /pachete/{tid}/trimite.

import { api, dataRo, esc, arataMesaj } from "../api.js?v=91e1c0701a";

// LUNI = pentru pickerul de luna (<option>); etichetele luna-an trec prin dataRo("luna_an"). [G3 23.07]
const LUNI = ["ianuarie","februarie","martie","aprilie","mai","iunie",
              "iulie","august","septembrie","octombrie","noiembrie","decembrie"];

let S = null;
function bani(x){ try { return Number(x).toLocaleString("ro-RO",{minimumFractionDigits:2,maximumFractionDigits:2}) + " lei"; } catch { return x; } }

export async function randeazaPachete(corp, nav) {
  if (nav && nav.setInapoi) nav.setInapoi(undefined);
  const acum = new Date();
  // luna trecuta (pachetul se face pt luna inchisa)
  let an = acum.getFullYear(), luna = acum.getMonth(); // getMonth e 0-11 => luna trecuta 1-12
  if (luna === 0) { luna = 12; an -= 1; }
  S = { firme: [], tenant_id: null, an, luna, rezumat: null, text: "", status: null };
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  try {
    const t = await api.get("/tenants");
    S.firme = Array.isArray(t) ? t : (t.tenants || []);
  } catch {
    corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca firmele.</p>`;
    return;
  }
  pasAlegere(corp, nav);
}

function pasAlegere(corp, nav) {
  if (nav && nav.setInapoi) nav.setInapoi(undefined);
  const f = corp.closest(".fereastra"); if (f) f.classList.remove("fer-larg");
  corp.innerHTML = `
    <p class="mig-intro">Trimite antreprenorului „povestea lunii” — un rezumat clar al lunii, scris de AI și aprobat de tine.</p>
    <div class="dec-form">
      <label class="camp">
        <span class="camp-eticheta">Firmă</span>
        <select id="pac-firma" class="camp-input">
          <option value="">— alege firma —</option>
          ${S.firme.map((fr)=>`<option value="${fr.id}" ${fr.id===S.tenant_id?"selected":""}>${esc(fr.nume||("Firma "+fr.id))}${fr.cui?" \u00b7 "+esc(fr.cui):""}</option>`).join("")}
        </select>
      </label>
      <div class="dec-perioada-rand">
        <label class="camp camp camp-mic"><span class="camp-eticheta">An</span>
          <input id="pac-an" class="camp-input" type="number" min="2020" max="2030" value="${S.an}"></label>
        <label class="camp camp camp-mic"><span class="camp-eticheta">Lună</span>
          <select id="pac-luna" class="camp-input">
            ${LUNI.map((l,i)=>`<option value="${i+1}" ${i+1===S.luna?"selected":""}>${l}</option>`).join("")}
          </select></label>
      </div>
    </div>
    <div class="dec-bara"><button class="buton-primar" id="pac-continua" disabled>Continuă →</button></div>
  `;
  const selF = corp.querySelector("#pac-firma");
  const cont = corp.querySelector("#pac-continua");
  const refresh = () => {
    S.tenant_id = selF.value ? parseInt(selF.value) : null;
    S.an = parseInt(corp.querySelector("#pac-an").value) || S.an;
    S.luna = parseInt(corp.querySelector("#pac-luna").value);
    cont.disabled = !S.tenant_id;
  };
  selF.addEventListener("change", refresh);
  // [comanda Costin 05.10.2026 pct.6] alegerea firmei = UN control (forma de la Declarații); câmpul de căutare separat a ieșit
  corp.querySelector("#pac-an").addEventListener("change", refresh);
  corp.querySelector("#pac-luna").addEventListener("change", refresh);
  cont.addEventListener("click", () => nav.mergi("Pachetul lunii", (c) => pasLucru(c, nav)));  // faza_b2_traseu_v1
  refresh();
}

async function pasLucru(corp, nav) {
  const f = corp.closest(".fereastra"); if (f) f.classList.add("fer-larg");
  corp.innerHTML = `<p class="ecran-nota">Se încarcă datele lunii…</p>`;
  // rezumat + poveste existenta (in paralel)
  try {
    const [rz, pv] = await Promise.all([
      api.get(`/pachete/${S.tenant_id}/rezumat?an=${S.an}&luna=${S.luna}`),
      api.get(`/pachete/${S.tenant_id}/poveste?an=${S.an}&luna=${S.luna}`),
    ]);
    S.rezumat = rz;
    if (pv && pv.exista) { S.text = pv.text || ""; S.status = pv.status; }
    else { S.text = ""; S.status = null; }
  } catch (e) {
    // [R156, 05.09.2026] Serverul refuza precis (`an invalid: -99999999 (aștept 1990-2100)`,
    // din `_cere_perioada`), iar ecranul il inlocuia cu „Nu am putut încărca datele.” — adica
    // spunea „n-am putut” despre ceva ce aplicatia STIA. `api.js` pune mesajul in `e.mesaj`.
    corp.innerHTML = `<p class="ecran-nota">${esc((e && e.mesaj) || "Nu am putut încărca datele.")}</p>
      `;
    return;
  }
  randeazaLucru(corp, nav);
}

function randeazaLucru(corp, nav) {
  const rz = S.rezumat || {};
  const depuse = (rz.declaratii_depuse || []).join(", ") || "—";
  corp.innerHTML = `
    <p class="mig-intro">${esc(rz.nume_firma||"Firma")} · ${dataRo(`${S.an}-${String(S.luna).padStart(2,"0")}`, "luna_an")}</p>
    <div class="panou pac-rezumat">
      <div class="pac-rez-rand"><span>Venituri</span><b>${bani(rz.venituri)}</b></div>
      <div class="pac-rez-rand"><span>Cheltuieli</span><b>${bani(rz.cheltuieli)}</b></div>
      <div class="pac-rez-rand pac-rez-total"><span>Rezultat</span><b>${bani(rz.rezultat)} (${esc(rz.tip)})</b></div>
      <div class="pac-rez-rand"><span>Declarații depuse</span><b>${esc(depuse)}</b></div>
      <div class="pac-rez-rand"><span>Email antreprenor</span><b>${esc(rz.email||"— nesetat —")}</b></div>
    </div>
    <div class="panou pac-deschide-zona">
      <div class="pac-deschide-stare" id="pac-deschide-stare">${S.status === "aprobat" ? "Povestea e aprobată ✓" : (S.text ? "Există o ciornă salvată" : "Încă nu există o poveste pentru această lună")}</div>
      <button class="buton-primar" id="pac-deschide">${S.text ? "Deschide povestea" : "Scrie povestea"}</button>
    </div>

  `;
  corp.querySelector("#pac-deschide").addEventListener("click", () => deschideModal(corp, nav));
}

// ---------- MODAL CENTRAL: povestea ----------
function deschideModal(corp, nav) {
  const rz = S.rezumat || {};
  // overlay peste tot ecranul
  const ov = document.createElement("div");
  ov.className = "pacm-overlay";  /* fereastra-de-lucru: doar X — e un editor (povestea nesalvată), Esc n-o aruncă (DECIZII 04.10.2026) */
  ov.innerHTML = `
    <div class="pacm">
      <div class="pacm-cap">
        <div>
          <div class="pacm-titlu">Povestea lunii</div>
          <div class="pacm-sub">${esc(rz.nume_firma||"Firma")} · ${dataRo(`${S.an}-${String(S.luna).padStart(2,"0")}`, "luna_an")}</div>
        </div>
        <button class="pacm-x" id="pacm-x" aria-label="\u00cenchide">✕</button>
      </div>
      <div class="pacm-corp" id="pacm-corp">
        <div class="pacm-editor" id="pacm-editor">
          <textarea aria-label="Povestea pentru antreprenor" id="pacm-text" class="pacm-text" placeholder="Scrie sau generează povestea pentru antreprenor…">${esc(S.text)}</textarea>
        </div>
        <div class="pacm-preview" id="pacm-preview" style="display:none"></div>
      </div>
      <div class="pacm-stare" id="pacm-stare"></div>
      <div class="pacm-abateri" id="pacm-abateri" role="note"></div>
      <div class="pacm-bara">
        <button class="buton-primar pac-genereaza" id="pacm-gen" data-actiune="POST /pachete/{tenant_id}/genereaza">✨ Generează cu AI</button>
        <button class="buton-secundar" id="pacm-vezi">Vezi ca email</button>
        <span class="pacm-spatiu"></span>
        <button class="buton-secundar" id="pacm-salveaza" data-actiune="POST /pachete/{tenant_id}/poveste">Salvează ciornă</button>
        <button class="buton-primar" id="pacm-aproba" data-actiune="POST /pachete/{tenant_id}/poveste/aproba">Aprobă</button>
        <button class="buton-primar" id="pacm-trimite" data-actiune="POST /pachete/{tenant_id}/trimite">Trimite</button>
      </div>
      <p class="ecran-nota pacm-motiv-trimite" id="pacm-motiv-trimite"></p>
    </div>
  `;
  document.body.appendChild(ov);

  const ta = ov.querySelector("#pacm-text");
  const stareEl = ov.querySelector("#pacm-stare");
  const editor = ov.querySelector("#pacm-editor");
  const preview = ov.querySelector("#pacm-preview");
  const btnVezi = ov.querySelector("#pacm-vezi");
  const btnTrimite = ov.querySelector("#pacm-trimite");

  const motivTrimite = ov.querySelector("#pacm-motiv-trimite");
  const abateriEl = ov.querySelector("#pacm-abateri");
  // [comanda Costin 05.10.2026 pct.7] „cu povestea goală, «Trimite» rămâne inactiv cu motiv” — motivul se VEDE lângă butoane,
  // nu doar ca `title` (care nu apare pe telefon și nu se citește fără mouse). Se recalculează și la tastare: pleacă textul
  // SALVAT și aprobat, iar un editor golit nu are ce aproba.
  function motivInactiv() {
    if (!(ta.value || "").trim()) return "„Trimite” e inactiv: povestea e goală. Scrie sau generează povestea, apoi aprob-o.";
    if (S.status !== "aprobat") return "„Trimite” e inactiv: povestea nu e aprobată încă.";
    if ((ta.value || "").trim() !== (S.text || "").trim()) return "„Trimite” e inactiv: textul s-a schimbat după aprobare — aprobă din nou.";
    return "";
  }
  function actualizeazaStare() {
    if (S.status === "aprobat") arataMesaj(stareEl, "Stare: aprobată ✓ — gata de trimis", "ok");
    else if (S.text) arataMesaj(stareEl, "Stare: ciornă", "info");
    else arataMesaj(stareEl, "", "info");
    const motiv = motivInactiv();
    btnTrimite.disabled = !!motiv;
    btnTrimite.title = motiv;
    motivTrimite.textContent = motiv;
  }
  actualizeazaStare();
  ta.addEventListener("input", actualizeazaStare);

  const inchide = () => ov.remove();
  ov.querySelector("#pacm-x").addEventListener("click", inchide);
  ov.addEventListener("click", (e) => { if (e.target === ov) inchide(); });

  // generare AI
  ov.querySelector("#pacm-gen").addEventListener("click", async () => {
    const btn = ov.querySelector("#pacm-gen");
    btn.disabled = true; btn.textContent = "Se generează…";
    try {
      const r = await api.post(`/pachete/${S.tenant_id}/genereaza?an=${S.an}&luna=${S.luna}`, {});
      if (r && r.ok) {
        ta.value = r.text || ""; S.text = ta.value; S.status = "ciorna"; actualizeazaStare();
        arataMesaj(stareEl, "Generată de AI — citește, editează și aprobă.", "info");
        // [comanda Costin 05.10.2026 pct.1] ce a scris AI-ul altfel decât pachetul (termen sau sumă) — de corectat înainte de aprobare
        arataMesaj(abateriEl, (r.abateri && r.abateri.length)
          ? "Atenție — textul generat se abate de la pachet (" + r.abateri.join("; ") + "). Corectează înainte de aprobare: pachetul spune venituri, cheltuieli și rezultat."
          : "", "avert");
      }
      else if (r && r.cod === "AI_INDISPONIBIL") { arataMesaj(stareEl, "AI indisponibil (cheie lipsă). Scrie manual.", "eroare"); }
      else { arataMesaj(stareEl, "Nu am putut genera. " + ((r && r.mesaj) || ""), "eroare"); }
    } catch { arataMesaj(stareEl, "Eroare la generare.", "eroare"); }
    btn.disabled = false; btn.textContent = "✨ Generează cu AI";
  });

  // toggle preview email
  let modPreview = false;
  btnVezi.addEventListener("click", async () => {
    modPreview = !modPreview;
    if (modPreview) {
      editor.style.display = "none"; preview.style.display = "block";
      btnVezi.textContent = "Înapoi la editare";
      preview.innerHTML = `<div class="pacm-mail">Se încarcă previzualizarea…</div>`;
      try {
        const r = await api.get(`/pachete/${S.tenant_id}/preview?an=${S.an}&luna=${S.luna}&text=${encodeURIComponent(ta.value)}`);
        preview.innerHTML = (r && r.html) || "";
      } catch (e) {
        preview.innerHTML = `<div class="pacm-mail">${esc((e && e.mesaj) || "Nu am putut încărca previzualizarea.")}</div>`;
      }
    } else {
      editor.style.display = "block"; preview.style.display = "none";
      btnVezi.textContent = "Vezi ca email";
    }
  });

  ov.querySelector("#pacm-salveaza").addEventListener("click", async () => {
    if (!await _salveaza(ta.value, "ciorna", stareEl, (text) => api.post(`/pachete/${S.tenant_id}/poveste?an=${S.an}&luna=${S.luna}`, { text, status: "ciorna" }))) return;  // [R159] refuzul ramane pe ecran
    actualizeazaStare();
    arataMesaj(stareEl, "Ciornă salvată.", "info"); _reflectaStareEcran(corp);
  });
  ov.querySelector("#pacm-aproba").addEventListener("click", async () => {
    // [comanda Costin 05.10.2026 pct.2] aprobarea are ruta ei („Poate valida”); apelul stă în handlerul butonului care o poartă
    if (!await _salveaza(ta.value, "aprobat", stareEl, (text) => api.post(`/pachete/${S.tenant_id}/poveste/aproba?an=${S.an}&luna=${S.luna}`, { text }))) return;  // [R159]
    actualizeazaStare();
    arataMesaj(stareEl, "Aprobată ✓", "ok"); _reflectaStareEcran(corp);
  });
  btnTrimite.addEventListener("click", async () => {
    btnTrimite.disabled = true; btnTrimite.textContent = "Se trimite…";
    try {
      const r = await api.post(`/pachete/${S.tenant_id}/trimite?an=${S.an}&luna=${S.luna}`, {});
      if (r && r.ok) { arataMesaj(stareEl, "Trimis la " + r.email + " ✓", "ok"); }
    } catch (e) {
      // api.js impacheteaza HTTPException(400, detail) in e.mesaj (via _mesajEroare); nu exista e.detail.
      arataMesaj(stareEl, (e && e.mesaj) || "Nu am putut trimite. Verifică emailul firmei și aprobarea.", "eroare");
    }
    btnTrimite.disabled = false; btnTrimite.textContent = "Trimite";
  });
}

function _reflectaStareEcran(corp) {
  const el = corp.querySelector("#pac-deschide-stare");
  if (el) el.textContent = S.status === "aprobat" ? "Povestea e aprobată ✓" : (S.text ? "Există o ciornă salvată" : "");
}

// [R159, 05.09.2026] Intoarce ACUM daca s-a salvat, si apelantii se uita la raspuns.
// Pana azi intorcea `undefined` pe toate cele trei cai — refuz, esec, reusita — iar cei doi
// apelanti tipareau «Ciornă salvată.» / «Aprobată ✓» oricum. *Un mesaj de reusita care nu se
// uita la rezultat nu e o confirmare, e o afirmatie falsa.* Si `r.ok === false` era inghitit.
async function _salveaza(text, status, stareEl, cerere) {  // audit_cab_lot1_v1 — `cerere(text)` = apelul, din handlerul butonului
  text = (text||"").trim();
  if (!text) { if (stareEl) arataMesaj(stareEl, "Scrie povestea întâi.", "eroare"); return false; }
  try {
    const r = await cerere(text);
    if (r && r.ok) { S.status = status; S.text = text; return true; }
    if (stareEl) arataMesaj(stareEl, (r && r.mesaj) || "Nu am putut salva.", "eroare");
    return false;
  } catch (e) { if (stareEl) arataMesaj(stareEl, (e && e.mesaj) || "Nu am putut salva.", "eroare"); return false; }
}

// audit_cab_lot1_v1

// faza_b2_traseu_v1
