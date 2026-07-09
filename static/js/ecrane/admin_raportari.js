// admin_raportari.js — Panou Admin iConta (superadmin) pentru modulul Raporteaza.
// Doua casute (tab-uri): "De la utilizatori" (pentru_admin=false) si "Pentru tine" (pentru_admin=true).
// Master-detail: lista stanga, firul + raspuns dreapta.
// Backend: GET /raportari/admin, GET /raportari/{id}, POST /raportari/{id}/mesaj,
//          POST /raportari/{id}/citit, POST /raportari/{id}/pentru-admin,
//          POST /raportari/mesaj/{mid}/imagine.

import { api } from "../api.js";

const LUNI = ["ian.","feb.","mar.","apr.","mai","iun.",
              "iul.","aug.","sep.","oct.","noi.","dec."];

function dataScurta(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  const azi = new Date();
  const ora = `${String(d.getHours()).padStart(2,"0")}:${String(d.getMinutes()).padStart(2,"0")}`;
  if (d.toDateString() === azi.toDateString()) return `azi ${ora}`;
  return `${d.getDate()} ${LUNI[d.getMonth()]} ${ora}`;
}

function copiazaTot(corp) {
  const vrei = _tab === "tine";
  const lista = _toate.filter((r) => !!r.pentru_admin === vrei);
  if (!lista.length) return;
  const blocuri = lista.map((r, i) => {
    const cap = `[${i + 1}] ${r.cabinet || ""}${r.autor ? " · " + r.autor : ""} (${dataScurta(r.ultim_mesaj_la || r.creat_la)})`;
    const subj = (r.subiect && r.subiect.trim()) ? r.subiect.trim() : "(fără subiect)";
    return `${cap}\n${subj}\n${r.text || ""}`.trim();
  });
  const txt = blocuri.join("\n\n----------\n\n");
  const btn = corp.querySelector("#rap-copy-tot-text");
  navigator.clipboard.writeText(txt).then(() => {
    if (btn) { const v = btn.textContent; btn.textContent = `Copiat (${lista.length})`; setTimeout(() => (btn.textContent = v), 1400); }
  }).catch(() => {});
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"]/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

// stare modul
let _tab = "useri";   // "useri" (pentru_admin=false) | "tine" (pentru_admin=true)
let _activ = null;    // id sesizare deschisa
let _toate = [];      // cache lista (sursa unica, filtram local)

export async function randeazaAdminRaportari(corp, nav) {
  if (nav && nav.setInapoi) nav.setInapoi(undefined);
  // largeste fereastra (split master-detail), ca la ecranul de solduri
  const f = corp.closest(".fereastra");
  if (f) f.classList.add("fer-larg");
  _tab = "useri"; _activ = null;

  corp.innerHTML = `
    <p class="mig-intro">Sesizările de la utilizatori și cele care trebuie tratate de tine. Bulina roșie = fără răspuns.</p>
    <div class="rap-tabs">
      <button class="rap-tab rap-tab-activ" data-tab="useri">De la utilizatori <span class="rap-tab-nr" id="rap-nr-useri"></span></button>
      <button class="rap-tab" data-tab="tine">De la AI <span class="rap-tab-nr" id="rap-nr-tine"></span></button>
      <span class="rap-tabs-spatiu"></span>
      <button class="buton-secundar rap-copy-tot" id="rap-copy-tot" title="Copiază toate reclamațiile din această filă">
        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>
        <span id="rap-copy-tot-text">Copiază tot</span>
      </button>
    </div>
    <div class="rap-split">
      <div class="rap-col-lista"><div id="rap-lista"><p class="ecran-nota">Se încarcă…</p></div></div>
      <div class="rap-col-fir" id="rap-fir"><div class="rap-gol">Alege o sesizare din stânga.</div></div>
    </div>
  `;
  corp.querySelectorAll(".rap-tab").forEach((b) =>
    b.addEventListener("click", () => {
      _tab = b.dataset.tab; _activ = null;
      corp.querySelectorAll(".rap-tab").forEach((x) => x.classList.toggle("rap-tab-activ", x === b));
      corp.querySelector("#rap-fir").innerHTML = `<div class="rap-gol">Alege o sesizare din stânga.</div>`;
      randeazaLista(corp, nav);
    }));

  corp.querySelector("#rap-copy-tot").addEventListener("click", () => copiazaTot(corp));

  await incarcaLista(corp, nav);
}

async function incarcaLista(corp, nav) {
  try {
    const date = await api.get("/raportari/admin");
    _toate = Array.isArray(date) ? date : (date.raportari || []);
  } catch {
    corp.querySelector("#rap-lista").innerHTML = `<p class="ecran-nota">Nu am putut încărca sesizările.</p>`;
    return;
  }
  randeazaLista(corp, nav);
}

function randeazaLista(corp, nav) {
  const vrei = _tab === "tine";
  const lista = _toate.filter((r) => !!r.pentru_admin === vrei);

  // contoare pe tab-uri (fara raspuns)
  const nrUseri = _toate.filter((r) => !r.pentru_admin && r.stare !== "raspuns").length;
  const nrTine  = _toate.filter((r) =>  r.pentru_admin && r.stare !== "raspuns").length;
  const eU = corp.querySelector("#rap-nr-useri");
  const eT = corp.querySelector("#rap-nr-tine");
  if (eU) eU.textContent = nrUseri ? nrUseri : "";
  if (eT) eT.textContent = nrTine ? nrTine : "";

  const cont = corp.querySelector("#rap-lista");
  if (!lista.length) {
    cont.innerHTML = `<div class="rap-gol">${vrei ? "Nicio sesizare de la AI." : "Nicio sesizare de la utilizatori."}</div>`;
    return;
  }
  cont.innerHTML = "";
  lista.forEach((r) => {
    const faraRaspuns = r.stare !== "raspuns";
    const rand = document.createElement("button");
    rand.className = "rap-rand" + (r.id === _activ ? " rap-rand-activ" : "");
    rand.innerHTML = `
      <span class="rap-bulina ${faraRaspuns ? "rap-bulina-on" : ""}"></span>
      <span class="rap-rand-text">
        <span class="rap-rand-sus">
          <span class="rap-subiect">${esc(r.subiect || "(fără subiect)")}</span>
          <span class="rap-cand">${dataScurta(r.ultim_mesaj_la || r.creat_la)}</span>
        </span>
        <span class="rap-rand-jos">${esc(r.cabinet || "")}${r.autor ? " · " + esc(r.autor) : ""}</span>
      </span>
    `;
    rand.addEventListener("click", () => nav.mergi("Sesizare", (c) => deschideSesizare(c, nav, r.id)));  // faza_b2_traseu_v1
    cont.appendChild(rand);
  });
}

async function deschideSesizare(corp, nav, id) {
  _activ = id;
  corp.querySelectorAll(".rap-rand").forEach((b) => b.classList.remove("rap-rand-activ"));

  const fir = corp.querySelector("#rap-fir");
  fir.innerHTML = `<p class="ecran-nota">Se încarcă firul…</p>`;

  let d;
  try {
    d = await api.get(`/raportari/${id}`);
  } catch {
    fir.innerHTML = `<p class="ecran-nota">Nu am putut încărca sesizarea.</p>`;
    return;
  }
  const cap = d.raportare || d;
  const mesaje = d.mesaje || cap.mesaje || [];

  // marcheaza citit (admin citeste mesajele utilizatorului)
  try { await api.post(`/raportari/${id}/citit`, {}); } catch {}

  const eTine = _tab === "tine";
  const etMutare = eTine
    ? "↩ Mută înapoi la „De la utilizatori”"
    : "Nu ține de aplicație → mută la „De la AI”";

  fir.innerHTML = `
    <div class="rap-fir-cap">
      <div class="rap-fir-subiect">${esc(cap.subiect || "(fără subiect)")}</div>
      <div class="rap-fir-meta">${esc(cap.cabinet || "")}${cap.autor ? " · " + esc(cap.autor) : ""}</div>
      <button class="buton-secundar rap-muta" id="rap-muta">${etMutare}</button>
    </div>
    <div class="rap-mesaje" id="rap-mesaje"></div>
    <div class="rap-compose">
      <textarea id="rap-text" class="rap-text" placeholder="Scrie răspunsul…" rows="3"></textarea>
      <div class="rap-compose-bara">
        <label class="rap-atas"><input type="file" id="rap-img" accept="image/*" hidden><span>Atașează imagine</span></label>
        <button class="buton-primar rap-trimite" id="rap-trimite">Trimite</button>
      </div>
      <div class="rap-img-nume" id="rap-img-nume"></div>
    </div>
  `;
  randeazaMesaje(fir.querySelector("#rap-mesaje"), mesaje);
  randeazaLista(corp, nav); // reflecta becul/contoarele

  const inputImg = fir.querySelector("#rap-img");
  const numeImg = fir.querySelector("#rap-img-nume");
  inputImg.addEventListener("change", () => {
    numeImg.textContent = inputImg.files[0] ? inputImg.files[0].name : "";
  });
  fir.querySelector("#rap-trimite").addEventListener("click", () => trimiteRaspuns(corp, nav, id, fir));
  fir.querySelector("#rap-muta").addEventListener("click", () => mutaSesizare(corp, nav, id, !eTine));
}

function randeazaMesaje(cont, mesaje) {
  cont.innerHTML = "";
  if (!mesaje.length) { cont.innerHTML = `<div class="rap-gol">Fără mesaje.</div>`; return; }
  mesaje.forEach((m) => {
    const eAdmin = (m.rol_autor || m.rol) === "admin";
    const bloc = document.createElement("div");
    bloc.className = "rap-msg " + (eAdmin ? "rap-msg-admin" : "rap-msg-user");
    let imgHtml = "";
    (m.atasamente || []).forEach((a) => {
      const cale = a.cale || a.url || "";
      const src = cale.startsWith("/") ? cale : `/static/raportari/${cale}`;
      imgHtml += `<img class="rap-msg-img" src="${src}" alt="${esc(a.nume || "imagine")}">`;
    });
    bloc.innerHTML = `
      <div class="rap-msg-text">${esc(m.text || "")}</div>
      ${imgHtml}
      <div class="rap-msg-cand">${dataScurta(m.cand || m.creat_la)}</div>
    `;
    cont.appendChild(bloc);
  });
  cont.scrollTop = cont.scrollHeight;
}

async function trimiteRaspuns(corp, nav, id, fir) {
  const ta = fir.querySelector("#rap-text");
  const text = (ta.value || "").trim();
  const inputImg = fir.querySelector("#rap-img");
  const fisier = inputImg.files[0] || null;
  if (!text && !fisier) return;

  const btn = fir.querySelector("#rap-trimite");
  btn.disabled = true; btn.textContent = "Se trimite…";
  try {
    const r = await api.post(`/raportari/${id}/mesaj`, { text });
    const mid = r.mesaj_id ?? r.id ?? (r.mesaj && r.mesaj.id);
    if (fisier && mid != null) {
      const fd = new FormData();
      fd.append("fisier", fisier);
      await api.postForm(`/raportari/mesaj/${mid}/imagine`, fd);
    }
  } catch {
    btn.disabled = false; btn.textContent = "Trimite";
    btn.parentElement.querySelectorAll(".msg-eroare").forEach((x) => x.remove());
    btn.insertAdjacentHTML("afterend", '<span class="msg-eroare" style="margin-left:8px">Nu am putut trimite răspunsul.</span>');
    return;
  }
  await incarcaLista(corp, nav);
  await deschideSesizare(corp, nav, id);
}

async function mutaSesizare(corp, nav, id, valoare) {
  try {
    await api.post(`/raportari/${id}/pentru-admin`, { valoare });
  } catch {
    corp.querySelectorAll(".msg-eroare").forEach((x) => x.remove());
    corp.insertAdjacentHTML("afterbegin", '<p class="msg-eroare">Nu am putut muta sesizarea.</p>');
    return;
  }
  _activ = null;
  corp.querySelector("#rap-fir").innerHTML = `<div class="rap-gol">Mutată. Alege altă sesizare.</div>`;
  await incarcaLista(corp, nav);
}

// audit_cab_lot1_v1

// faza_b2_traseu_v1
