// api.js — singurul loc prin care frontendul vorbește cu serverul.
// Atașează automat token-ul (Bearer), tratează erorile uniform.
// Origin relativ: FastAPI servește și frontendul, și API-ul.

import { sesiune } from "./sesiune.js";

// [cap1_feedback_async_v1] Design System cap.1: butonul declansator se dezactiveaza
// automat pe durata oricarei actiuni asincrone. Textul devine "Se lucreaza..." si se
// restaureaza la final. Textele specifice ("Se salveaza...") raman posibile local.
let _ultimClick = { btn: null, t: 0 };
document.addEventListener("pointerdown", (e) => {
  const b = e.target.closest("button");
  if (b) _ultimClick = { btn: b, t: Date.now() };
}, true);
function butonDeclansator() {
  return (_ultimClick.btn && Date.now() - _ultimClick.t < 400 && !_ultimClick.btn.disabled) ? _ultimClick.btn : null;
}
function blocheazaButon(metoda) {
  if (metoda === "GET") return () => {};
  const b = butonDeclansator();
  if (!b) return () => {};
  const textOriginal = b.textContent;
  b.disabled = true;
  if (!/Se \S+eaz\u0103|Se lucreaz/.test(textOriginal)) b.textContent = "Se lucreaz\u0103...";
  return () => { b.disabled = false; b.textContent = textOriginal; };
}

async function cere(metoda, cale, corp) {
  const deblocheaza = blocheazaButon(metoda);
  try {
    return await _cere(metoda, cale, corp);
  } finally { deblocheaza(); }
}
// [login_401_v1] mesaj de eroare din raspuns, cu text prietenos pe statusuri fara corp
// (429 rate limit nginx = HTML, fara detail). Zero esec tacit: mereu un motiv lizibil.
// [G10 cap.6 v2.30 rule2/4] erorile per-camp din raspuns: detail.erori_campuri (lista {camp, mesaj}).
function _erisCampuri(date) {
  const d = date && date.detail;
  if (d && typeof d === "object" && Array.isArray(d.erori_campuri)) return d.erori_campuri;
  if (date && Array.isArray(date.erori_campuri)) return date.erori_campuri;
  return null;
}

function _mesajEroare(status, date) {
  const _d = date && date.detail;
  if (_d && typeof _d === "object") return _d.mesaj || "eroare";  // [G10] detail structurat {mesaj, erori_campuri}
  if (date && (date.detail || date.mesaj)) return date.detail || date.mesaj;
  if (status === 429) return "prea multe încercări — așteaptă un minut și reîncearcă";
  if (status === 502 || status === 503 || status === 504) return "serverul e temporar indisponibil — reîncearcă în câteva momente";
  return "eroare " + status;
}
async function _cere(metoda, cale, corp) {
  const optiuni = {
    method: metoda,
    headers: { "Content-Type": "application/json" },
  };
  const token = sesiune.token();
  if (token) optiuni.headers["Authorization"] = "Bearer " + token;
  if (corp !== undefined) optiuni.body = JSON.stringify(corp);

  const r = await fetch(cale, optiuni);

  // 401 = token invalid/expirat -> deconectare curată. DOAR daca aveam sesiune (token trimis):
  // /auth/login intoarce legitim 401 la credentiale gresite, iar acolo NU e sesiune de expirat -
  // iesi() ar re-randa ecranul si ar inghiti mesajul real ("email sau parola gresite"). [login_401_v1]
  if (r.status === 401 && token) {
    sesiune.iesi();
    throw { cod: 401, mesaj: "sesiune expirată, autentifică-te din nou" };
  }

  let date = null;
  try { date = await r.json(); } catch { date = null; }

  if (!r.ok) {
    throw { cod: r.status, mesaj: _mesajEroare(r.status, date), erori_campuri: _erisCampuri(date) };
  }
  return date;
}

// [p36_postform] trimitere multipart (FormData) - pt upload fisiere/imagini
async function cereForm(cale, formData) {
  const deblocheaza = blocheazaButon("POST");
  try {
    return await _cereForm(cale, formData);
  } finally { deblocheaza(); }
}
async function _cereForm(cale, formData) {
  const optiuni = { method: "POST", headers: {} };  // NU setam Content-Type (boundary auto)
  const token = sesiune.token();
  if (token) optiuni.headers["Authorization"] = "Bearer " + token;
  optiuni.body = formData;
  const r = await fetch(cale, optiuni);
  if (r.status === 401 && token) {  // [login_401_v1] doar cu sesiune (vezi _cere)
    sesiune.iesi();
    throw { cod: 401, mesaj: "sesiune expirată, autentifică-te din nou" };
  }
  let date = null;
  try { date = await r.json(); } catch { date = null; }
  if (!r.ok) {
    throw { cod: r.status, mesaj: _mesajEroare(r.status, date), erori_campuri: _erisCampuri(date) };
  }
  return date;
}

export const api = {
  get: (cale) => cere("GET", cale),
  post: (cale, corp) => cere("POST", cale, corp),
  put: (cale, corp) => cere("PUT", cale, corp),
  del: (cale) => cere("DELETE", cale),
  postForm: (cale, formData) => cereForm(cale, formData),
};
// [msg_conventie_v1] helper global mesaje: tip = "eroare" | "avert" | "info"
export function arataMesaj(el, txt, tip = "info") {
  if (!el) return;
  el.textContent = txt || "";
  el.className = el.className.replace(/\bmsg-(eroare|avert|info|ok)\b/g, "").trim();
  el.classList.add("msg-" + tip);
}

// [G10 cap.6 v2.30] eroare de camp: <span class="msg-eroare" data-camp> imediat dupa inputul #idCamp.
// Intoarce false daca #idCamp nu exista -> apelantul cade la B (zona generica). Fallback OBLIGATORIU.
export function eroareCamp(root, idCamp, txt) {
  const inp = (root || document).querySelector("#" + idCamp);
  if (!inp) return false;
  let sp = inp.parentElement && inp.parentElement.querySelector('.msg-eroare[data-camp="' + idCamp + '"]');
  if (!sp) {
    sp = document.createElement("span");
    sp.className = "msg-eroare";
    sp.setAttribute("data-camp", idCamp);
    inp.insertAdjacentElement("afterend", sp);
  }
  sp.textContent = txt;
  return true;
}

export function curataEroriCamp(root) {
  (root || document).querySelectorAll(".msg-eroare[data-camp]").forEach((e) => e.remove());
}

// [STANDARD_ATENTIONARE] confirmare in caseta standard, inlocuieste confirm() nativ.
// Foloseste: confirmaCaseta(elementZona, "Mesaj...", () => { actiunea });
// Injecteaza caseta + butoane sub/inaintea zonei date; Renunta o inchide.
export function confirmaCaseta(zona, mesaj, laConfirm, optiuni = {}) {
  const vechi = document.getElementById("caseta-atentie-activa");
  if (vechi) vechi.remove();
  const div = document.createElement("div");
  div.id = "caseta-atentie-activa";
  div.innerHTML = `
    <div class="caseta-atentie"><div class="ca-mesaj" style="margin-bottom:0">${mesaj}</div></div>
    <div class="ca-actiuni" style="margin:10px 0 14px;display:flex;gap:8px">
      <button class="buton-primar" id="ca-ok">${optiuni.textOk || "Confirm"}</button>
      <button class="buton-secundar" id="ca-nu">Renun\u021b\u0103</button>
    </div>`;
  zona.parentNode.insertBefore(div, zona.nextSibling);
  div.querySelector("#ca-nu").addEventListener("click", () => div.remove());
  div.querySelector("#ca-ok").addEventListener("click", () => { div.remove(); laConfirm(); });
  div.scrollIntoView({ block: "nearest", behavior: "smooth" });
}


// [lupa] vizualizare poza cu zoom (rotita / dublu-click) si tragere — element comun  // generalizare_zi_v1
export function deschideLupa(u, rotInit) {  // bon_flux_e9_v1
  const ov = document.createElement("div");
  ov.className = "lupa-overlay";
  const img = document.createElement("img");
  img.src = u; img.className = "lupa-mare"; img.draggable = false;
  let scara = 1, tx = 0, ty = 0, drag = null;
  let rot = Number(rotInit) || 0;  // bon_flux_e9b_v1
  const aplica = () => { img.style.transform = `translate(${tx}px,${ty}px) scale(${scara}) rotate(${rot}deg)`; };
  aplica();
  ov.addEventListener("wheel", (e) => {
    e.preventDefault();
    if (e.shiftKey) {
      rot = (rot + (e.deltaY < 0 ? -2 : 2) + 360) % 360;
    } else {
      scara = Math.min(8, Math.max(1, scara * (e.deltaY < 0 ? 1.25 : 0.8)));
      if (scara === 1) { tx = 0; ty = 0; }
    }
    aplica();
  }, { passive: false });
  ov.addEventListener("contextmenu", (e) => { e.preventDefault(); rot = (rot + 90) % 360; aplica(); });
  img.addEventListener("dblclick", () => { scara = scara > 1 ? 1 : 3; if (scara === 1) { tx = 0; ty = 0; } aplica(); });
  img.addEventListener("mousedown", (e) => { e.preventDefault(); drag = { x: e.clientX - tx, y: e.clientY - ty }; });
  const misca = (e) => { if (drag) { tx = e.clientX - drag.x; ty = e.clientY - drag.y; aplica(); } };
  const lasa = () => { drag = null; };
  window.addEventListener("mousemove", misca);
  window.addEventListener("mouseup", lasa);
  img.addEventListener("click", (e) => e.stopPropagation());
  const inchide = () => {  // bon_flux_e9c_v1
    window.removeEventListener("mousemove", misca);
    window.removeEventListener("mouseup", lasa);
    window.removeEventListener("keydown", peTasta);
    ov.remove();
  };
  const peTasta = (e) => { if (e.key === "Escape") inchide(); };
  window.addEventListener("keydown", peTasta);
  ov.addEventListener("click", inchide);
  const bX = document.createElement("button");
  bX.className = "lupa-x"; bX.setAttribute("aria-label", "\u00cenchide"); bX.textContent = "\u2715";
  bX.addEventListener("click", (e) => { e.stopPropagation(); inchide(); });
  ov.appendChild(bX);
  ov.appendChild(img);
  document.body.appendChild(ov);
}

// bon_flux_e9_v1

// bon_flux_e9b_v1

// bon_flux_e9c_v1

/* bani_v1 — formator monetar canonic (Design System v1.1): 1.234,56 */
export function bani(v) {
  const n = Number(v);
  if (v === null || v === undefined || v === "" || !isFinite(n)) return v ?? "";
  return n.toLocaleString("ro-RO", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
/* baniRotund — cifre de ansamblu rotunjite la leu (cockpit cabinet, cifrele firmei client). 1.234 (fara zecimale) */
export function baniRotund(v) {
  const n = Number(v);
  if (v === null || v === undefined || v === "" || !isFinite(n)) return v ?? "";
  return n.toLocaleString("ro-RO", { maximumFractionDigits: 0 });
}

/* CULORI_CARD — paleta canonica de carduri de meniu (Design System cap.12). 7 culori-concept.
   Fiecare card foloseste o cheie de aici, NU hex ad-hoc. bg = fundal pastel, fg = titlu/icon saturat. */
export const CULORI_CARD = {
  albastru:  { bg: "#e9f0fe", fg: "#1d4ed8" },
  verde:     { bg: "#e6f6ec", fg: "#16a34a" },
  teal:      { bg: "#dff4f2", fg: "#0a807b" },
  violet:    { bg: "#efebfe", fg: "#6d28d9" },
  piersica:  { bg: "#faece7", fg: "#993c1d" },
  chihlimbar:{ bg: "#fbeedd", fg: "#92500a" },
  ardezie:   { bg: "#eaeef6", fg: "#45597f" },
};

/* ICOANE — dictionar canonic unic de iconite SVG (path-uri interne, viewBox 24x24, stroke). Design System cap.13.
   O iconita sugestiva per concept. NU se duplica dictionarul in ecrane; toate importa de aici. */
export const ICOANE = {
  building: '<path d="M3 21h18"/><path d="M5 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16"/><path d="M19 21V11a2 2 0 0 0-2-2h-2"/><path d="M9 7h2M9 11h2M9 15h2"/>',
  shield: '<path d="M12 3l8 3v5c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-3z"/><path d="M9 12l2 2 4-4"/>',
  calendar: '<rect x="4" y="5" width="16" height="16" rx="2"/><path d="M4 9h16M8 3v4M16 3v4"/>',
  clipboard: '<rect x="8" y="3" width="8" height="4" rx="1"/><path d="M8 5H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><path d="M9 14l2 2 4-4"/>',
  users: '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3 3-5 6-5s6 2 6 5"/><path d="M16 6a3 3 0 0 1 0 6M21 20c0-2-1-3.5-3-4.5"/>',
  mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
  gift: '<rect x="3" y="11" width="18" height="10" rx="1"/><path d="M3 11V9a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v2M12 7v14"/>',
  brief: '<path d="M4 5h16M4 10h16M4 15h10M4 20h6"/><circle cx="18" cy="18" r="3"/><path d="M18 16.5v1.5l1 1"/>',
  trend: '<path d="M3 17l6-6 4 4 8-8"/><path d="M17 7h4v4"/>',
  gauge: '<path d="M12 13a4 4 0 0 1 4-4"/><path d="M3 18a9 9 0 0 1 18 0"/><path d="M12 13l4-2"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M12 3v2M12 19v2M5 12H3M21 12h-2M6 6l1.5 1.5M18 18l-1.5-1.5M6 18l1.5-1.5M18 6l-1.5 1.5"/>',
  facturi: '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 7h6M9 11h6M9 15h4"/>',
  declaratii: '<path d="M14 3v5h5"/><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M8 13h8M8 17h5"/>',
  documente: '<path d="M14 3v5h5"/><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>',
  solicitari: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
  povestea: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
  recomanda: '<path d="M12 2l2.4 7.4H22l-6 4.6 2.3 7.4L12 17l-6.3 4.4L8 14 2 9.4h7.6z"/>',
  anunturi: '<path d="M3 11v2a1 1 0 0 0 1 1h2l5 4V6L6 10H4a1 1 0 0 0-1 1z"/><path d="M15 9a3 3 0 0 1 0 6M18 6a7 7 0 0 1 0 12"/>',
  server: '<rect x="3" y="4" width="18" height="7" rx="2"/><rect x="3" y="13" width="18" height="7" rx="2"/><path d="M7 7.5v.01M7 16.5v.01"/>',
  suport: '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 0 1 4.5 1.5c0 1.5-2 2-2 3M12 17v.01"/>',
  consolidare: '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
  activitate: '<path d="M3 12h4l2 6 4-14 2 8h6"/>',
};


// [esc_canonic_v1] Escapare HTML unica pentru date user randate in innerHTML (NC-27).
// dataRo — SINGURA functie de formatare data in aplicatie (Design System cap.4).
// Accepta: string ISO (yyyy-mm-dd), obiect Date, sau null/gol -> "".
// stil "scurt" (implicit): zz.ll.aaaa (numeric, aliniabil in tabele).
// stil "lung": "11 iulie 2026" (pentru titluri). "luna_an": "iulie 2026" (perioade lunare, fara zi).
// "zi_luna_text": "11 iul". "zi_luna": "11.07". "cu_ora": "11.07.2026 14:30".
const _LUNI_RO = ["ianuarie","februarie","martie","aprilie","mai","iunie","iulie","august","septembrie","octombrie","noiembrie","decembrie"];
const _LUNI_SCURT = ["ian","feb","mar","apr","mai","iun","iul","aug","sep","oct","noi","dec"];
export function dataRo(d, stil) {
  if (!d) return "";
  let dt;
  if (d instanceof Date) dt = d;
  else {
    const full = String(d);
    const mDoar = full.slice(0, 10).match(/^(\d{4})-(\d{2})-(\d{2})$/);
    // daca string-ul are si ora (ISO cu T sau spatiu), pastreaza timestamp-ul intreg
    if (mDoar && full.length > 10) { dt = new Date(full); if (isNaN(dt)) dt = new Date(+mDoar[1], +mDoar[2] - 1, +mDoar[3]); }
    else if (mDoar) dt = new Date(+mDoar[1], +mDoar[2] - 1, +mDoar[3]);
    else { dt = new Date(full); if (isNaN(dt)) return String(d); }
  }
  if (isNaN(dt)) return String(d);
  const zz = String(dt.getDate()).padStart(2, "0");
  const ll = String(dt.getMonth() + 1).padStart(2, "0");
  const aa = dt.getFullYear();
  if (stil === "lung") return `${dt.getDate()} ${_LUNI_RO[dt.getMonth()]} ${aa}`;
  if (stil === "cu_ora") {
    const hh = String(dt.getHours()).padStart(2, "0");
    const mi = String(dt.getMinutes()).padStart(2, "0");
    return `${zz}.${ll}.${aa} ${hh}:${mi}`;
  }
  if (stil === "zi_luna_text") return `${dt.getDate()} ${_LUNI_SCURT[dt.getMonth()]}`;
  if (stil === "luna_an") return `${_LUNI_RO[dt.getMonth()]} ${aa}`;   // "iulie 2026" — titluri/texte narative
  if (stil === "luna_an_numeric") return `${String(dt.getMonth() + 1).padStart(2, "0")}/${aa}`;  // "07/2026" — antete de ecran (DS v2.21)
  if (stil === "zi_luna") return `${zz}.${ll}`;
  return `${zz}.${ll}.${aa}`;
}

// pct(v) — singurul formator de procent: numar intreg + "%" (12%), o zecimala cand exista (12,5%)
export function pct(v) {
  const n = Number(v) || 0;
  const t = Number.isInteger(n) ? String(n) : n.toFixed(1).replace(".", ",");
  return t + "%";
}

export function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}
