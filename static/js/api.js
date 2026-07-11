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
async function _cere(metoda, cale, corp) {
  const optiuni = {
    method: metoda,
    headers: { "Content-Type": "application/json" },
  };
  const token = sesiune.token();
  if (token) optiuni.headers["Authorization"] = "Bearer " + token;
  if (corp !== undefined) optiuni.body = JSON.stringify(corp);

  const r = await fetch(cale, optiuni);

  // 401 = token invalid/expirat -> deconectare curată
  if (r.status === 401) {
    sesiune.iesi();
    throw { cod: 401, mesaj: "sesiune expirată, autentifică-te din nou" };
  }

  let date = null;
  try { date = await r.json(); } catch { date = null; }

  if (!r.ok) {
    const mesaj = (date && (date.detail || date.mesaj)) || ("eroare " + r.status);
    throw { cod: r.status, mesaj };
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
  if (r.status === 401) {
    sesiune.iesi();
    throw { cod: 401, mesaj: "sesiune expirată, autentifică-te din nou" };
  }
  let date = null;
  try { date = await r.json(); } catch { date = null; }
  if (!r.ok) {
    const mesaj = (date && (date.detail || date.mesaj)) || ("eroare " + r.status);
    throw { cod: r.status, mesaj };
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
  el.className = el.className.replace(/\bmsg-(eroare|avert|info)\b/g, "").trim();
  el.classList.add("msg-" + tip);
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


// [esc_canonic_v1] Escapare HTML unica pentru date user randate in innerHTML (NC-27).
export function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}
