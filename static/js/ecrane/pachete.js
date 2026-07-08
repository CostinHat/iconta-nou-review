// pachete.js — Pachetul lunar / Povestea lunii.
// Flux: alegi firma+luna -> vezi rezumatul -> "Genereaza povestea" (AI) -> editezi -> aprobi -> trimiti.
// Backend: GET /tenants, GET /pachete/{tid}/rezumat, POST /pachete/{tid}/genereaza,
//          GET+POST /pachete/{tid}/poveste, POST /pachete/{tid}/trimite.

import { api } from "../api.js";

const LUNI = ["ianuarie","februarie","martie","aprilie","mai","iunie",
              "iulie","august","septembrie","octombrie","noiembrie","decembrie"];

let S = null;
function esc(s){ return String(s ?? "").replace(/[&<>"]/g,(c)=>({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;" }[c])); }
function bani(x){ try { return Number(x).toLocaleString("ro-RO",{minimumFractionDigits:2,maximumFractionDigits:2}) + " lei"; } catch { return x; } }

export async function randeazaPachete(corp, nav) {
  if (nav && nav.setInapoi) nav.setInapoi(undefined);
  const acum = new Date();
  // luna trecuta (pachetul se face pt luna inchisa)
  let an = acum.getFullYear(), luna = acum.getMonth(); // getMonth e 0-11 => luna trecuta 1-12
  if (luna === 0) { luna = 12; an -= 1; }
  S = { firme: [], tenant_id: null, an, luna, rezumat: null, text: "", status: null };
  corp.innerHTML = `<p class="ecran-nota">Se incarca…</p>`;
  try {
    const t = await api.get("/tenants");
    S.firme = Array.isArray(t) ? t : (t.tenants || []);
  } catch {
    corp.innerHTML = `<p class="ecran-nota">Nu am putut incarca firmele.</p>`;
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
      <label class="dec-camp">
        <span class="dec-eticheta">Firmă</span>
        <select id="pac-firma" class="dec-select">
          <option value="">— alege firma —</option>
          ${S.firme.map((fr)=>`<option value="${fr.id}" ${fr.id===S.tenant_id?"selected":""}>${esc(fr.nume||("Firma "+fr.id))}</option>`).join("")}
        </select>
      </label>
      <div class="dec-perioada-rand">
        <label class="dec-camp dec-camp-mic"><span class="dec-eticheta">An</span>
          <input id="pac-an" class="dec-input" type="number" min="2020" max="2030" value="${S.an}"></label>
        <label class="dec-camp dec-camp-mic"><span class="dec-eticheta">Lună</span>
          <select id="pac-luna" class="dec-select">
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
  corp.querySelector("#pac-an").addEventListener("change", refresh);
  corp.querySelector("#pac-luna").addEventListener("change", refresh);
  cont.addEventListener("click", () => pasLucru(corp, nav));
  refresh();
}

async function pasLucru(corp, nav) {
  if (nav && nav.setInapoi) nav.setInapoi(() => pasAlegere(corp, nav));
  const f = corp.closest(".fereastra"); if (f) f.classList.add("fer-larg");
  corp.innerHTML = `<p class="ecran-nota">Se incarca datele lunii…</p>`;
  // rezumat + poveste existenta (in paralel)
  try {
    const [rz, pv] = await Promise.all([
      api.get(`/pachete/${S.tenant_id}/rezumat?an=${S.an}&luna=${S.luna}`),
      api.get(`/pachete/${S.tenant_id}/poveste?an=${S.an}&luna=${S.luna}`),
    ]);
    S.rezumat = rz;
    if (pv && pv.exista) { S.text = pv.text || ""; S.status = pv.status; }
    else { S.text = ""; S.status = null; }
  } catch {
    corp.innerHTML = `<p class="ecran-nota">Nu am putut incarca datele.</p>
      <div class="dec-bara"><button class="buton-secundar" id="pac-back">\u2190</button></div>`;
    corp.querySelector("#pac-back").addEventListener("click", () => pasAlegere(corp, nav));
    return;
  }
  randeazaLucru(corp, nav);
}

function randeazaLucru(corp, nav) {
  const rz = S.rezumat || {};
  const depuse = (rz.declaratii_depuse || []).join(", ") || "—";
  corp.innerHTML = `
    <p class="mig-intro">${esc(rz.nume_firma||"Firma")} · ${LUNI[S.luna-1]} ${S.an}</p>
    <div class="pac-rezumat">
      <div class="pac-rez-rand"><span>Venituri</span><b>${bani(rz.venituri)}</b></div>
      <div class="pac-rez-rand"><span>Cheltuieli</span><b>${bani(rz.cheltuieli)}</b></div>
      <div class="pac-rez-rand pac-rez-total"><span>Rezultat</span><b>${bani(rz.rezultat)} (${esc(rz.tip)})</b></div>
      <div class="pac-rez-rand"><span>Declarații depuse</span><b>${esc(depuse)}</b></div>
      <div class="pac-rez-rand"><span>Email antreprenor</span><b>${esc(rz.email||"— nesetat —")}</b></div>
    </div>
    <div class="pac-deschide-zona">
      <div class="pac-deschide-stare" id="pac-deschide-stare">${S.status === "aprobat" ? "Povestea e aprobată ✓" : (S.text ? "Există o ciornă salvată" : "Încă nu există o poveste pentru această lună")}</div>
      <button class="buton-primar" id="pac-deschide">${S.text ? "Deschide povestea" : "Scrie povestea"}</button>
    </div>
    <div class="dec-bara"><button class="buton-secundar" id="pac-back">\u2190</button></div>
  `;
  corp.querySelector("#pac-back").addEventListener("click", () => pasAlegere(corp, nav));
  corp.querySelector("#pac-deschide").addEventListener("click", () => deschideModal(corp, nav));
}

// ---------- MODAL CENTRAL: povestea ----------
function deschideModal(corp, nav) {
  const rz = S.rezumat || {};
  // overlay peste tot ecranul
  const ov = document.createElement("div");
  ov.className = "pacm-overlay";
  ov.innerHTML = `
    <div class="pacm">
      <div class="pacm-cap">
        <div>
          <div class="pacm-titlu">Povestea lunii</div>
          <div class="pacm-sub">${esc(rz.nume_firma||"Firma")} · ${LUNI[S.luna-1]} ${S.an}</div>
        </div>
        <button class="pacm-x" id="pacm-x" aria-label="Inchide">✕</button>
      </div>
      <div class="pacm-corp" id="pacm-corp">
        <div class="pacm-editor" id="pacm-editor">
          <textarea id="pacm-text" class="pacm-text" placeholder="Scrie sau generează povestea pentru antreprenor…">${esc(S.text)}</textarea>
        </div>
        <div class="pacm-preview" id="pacm-preview" style="display:none"></div>
      </div>
      <div class="pacm-stare" id="pacm-stare"></div>
      <div class="pacm-bara">
        <button class="pac-genereaza" id="pacm-gen">✨ Generează cu AI</button>
        <button class="buton-secundar" id="pacm-vezi">Vezi ca email</button>
        <span class="pacm-spatiu"></span>
        <button class="buton-secundar" id="pacm-salveaza">Salvează ciornă</button>
        <button class="buton-primar" id="pacm-aproba">Aprobă</button>
        <button class="buton-primar" id="pacm-trimite">Trimite</button>
      </div>
    </div>
  `;
  document.body.appendChild(ov);

  const ta = ov.querySelector("#pacm-text");
  const stareEl = ov.querySelector("#pacm-stare");
  const editor = ov.querySelector("#pacm-editor");
  const preview = ov.querySelector("#pacm-preview");
  const btnVezi = ov.querySelector("#pacm-vezi");
  const btnTrimite = ov.querySelector("#pacm-trimite");

  function actualizeazaStare() {
    stareEl.textContent = S.status === "aprobat" ? "Stare: aprobată ✓ — gata de trimis" : (S.text ? "Stare: ciornă" : "");
    btnTrimite.disabled = (S.status !== "aprobat");
    btnTrimite.title = (S.status === "aprobat") ? "" : "Aprobă întâi povestea";
  }
  actualizeazaStare();

  const inchide = () => ov.remove();
  ov.querySelector("#pacm-x").addEventListener("click", inchide);
  ov.addEventListener("click", (e) => { if (e.target === ov) inchide(); });

  // generare AI
  ov.querySelector("#pacm-gen").addEventListener("click", async () => {
    const btn = ov.querySelector("#pacm-gen");
    btn.disabled = true; btn.textContent = "Se generează…";
    try {
      const r = await api.post(`/pachete/${S.tenant_id}/genereaza?an=${S.an}&luna=${S.luna}`, {});
      if (r && r.ok) { ta.value = r.text || ""; S.text = ta.value; S.status = "ciorna"; actualizeazaStare(); stareEl.textContent = "Generată de AI — citește, editează și aprobă."; }
      else if (r && r.cod === "AI_INDISPONIBIL") { alert("AI indisponibil (cheie lipsă). Scrie manual."); }
      else { alert("Nu am putut genera. " + ((r && r.mesaj) || "")); }
    } catch { alert("Eroare la generare."); }
    btn.disabled = false; btn.textContent = "✨ Generează cu AI";
  });

  // toggle preview email
  let modPreview = false;
  btnVezi.addEventListener("click", () => {
    modPreview = !modPreview;
    if (modPreview) {
      preview.innerHTML = _previewEmail(rz, ta.value);
      editor.style.display = "none"; preview.style.display = "block";
      btnVezi.textContent = "Înapoi la editare";
    } else {
      editor.style.display = "block"; preview.style.display = "none";
      btnVezi.textContent = "Vezi ca email";
    }
  });

  ov.querySelector("#pacm-salveaza").addEventListener("click", async () => {
    await _salveaza(ta.value, "ciorna"); actualizeazaStare();
    stareEl.textContent = "Ciornă salvată."; _reflectaStareEcran(corp);
  });
  ov.querySelector("#pacm-aproba").addEventListener("click", async () => {
    await _salveaza(ta.value, "aprobat"); actualizeazaStare();
    stareEl.textContent = "Aprobată ✓"; _reflectaStareEcran(corp);
  });
  btnTrimite.addEventListener("click", async () => {
    btnTrimite.disabled = true; btnTrimite.textContent = "Se trimite…";
    try {
      const r = await api.post(`/pachete/${S.tenant_id}/trimite?an=${S.an}&luna=${S.luna}`, {});
      if (r && r.ok) { stareEl.textContent = "Trimis la " + r.email + " ✓"; }
    } catch { alert("Nu am putut trimite. Verifică emailul firmei și aprobarea."); }
    btnTrimite.disabled = false; btnTrimite.textContent = "Trimite";
  });
}

function _previewEmail(rz, text) {
  const LL = String(S.luna).padStart(2,"0");
  return `
    <div class="pacm-mail">
      <div class="pacm-mail-h">Raport lunar — ${esc(rz.nume_firma||"Firma")}</div>
      <div class="pacm-mail-sub">Luna ${LL}/${S.an}</div>
      <div class="pacm-mail-box">${esc(text).replace(/\n/g,"<br>")}</div>
      <div class="pacm-mail-foot">Trimis prin iConta.</div>
    </div>`;
}

function _reflectaStareEcran(corp) {
  const el = corp.querySelector("#pac-deschide-stare");
  if (el) el.textContent = S.status === "aprobat" ? "Povestea e aprobată ✓" : (S.text ? "Există o ciornă salvată" : "");
}

async function _salveaza(text, status) {
  text = (text||"").trim();
  if (!text) { alert("Scrie povestea întâi."); return; }
  try {
    const r = await api.post(`/pachete/${S.tenant_id}/poveste?an=${S.an}&luna=${S.luna}`, { text, status });
    if (r && r.ok) { S.status = status; S.text = text; }
  } catch { alert("Nu am putut salva."); }
}
