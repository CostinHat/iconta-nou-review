// login.js — poarta de intrare.
// Bara sus: logo + buton "Acces". Acces deschide central un modal umbrit
// cu 2 optiuni: Intra in cont (login existent) / Client nou (inregistrare cabinet).
import { api, arataMesaj, CULORI_CARD, ICOANE, esc } from "../api.js";
import { PRETURI_TITLU, PRETURI_SUBTITLU, preturiHTML } from "./preturi.js";  // [preturi_v1] sursa unica a continutului de preturi
import { sesiune } from "../sesiune.js";

function svgIcon(paths, w = 24) {
  return `<svg viewBox="0 0 24 24" width="${w}" height="${w}" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${paths}</svg>`;
}

const ICONI = {
  factura: '<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 13h6M9 17h4"/>',
  saft: '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
  ai: '<rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4M8 16h.01M16 16h.01"/>',
  pachet: '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
  cabinet: '<path d="M3 21h18"/><path d="M5 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16"/><path d="M19 21V11a2 2 0 0 0-2-2h-2"/><path d="M9 7h2M9 11h2M9 15h2"/>',
  scut: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
  raport: '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>',
  sageata: '<path d="M9 18l6-6-6-6"/>',
  scutmic: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
  nor: '<path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/>',
  oameni: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
  moneda: '<circle cx="12" cy="12" r="9"/><path d="M14.5 9.5a2.5 2.5 0 0 0-2.5-1.5c-1.5 0-2.5 1-2.5 2s1 1.5 2.5 2 2.5 1 2.5 2-1 2-2.5 2a2.5 2.5 0 0 1-2.5-1.5"/><path d="M12 6v2M12 16v2"/>',
};

const CARDURI_RAND1 = [
  { cheie: "saft", titlu: "SAF-T inclus", sub: "D100-D406, XML + PDF, validate DUKIntegrator.", ...CULORI_CARD.albastru, icon: ICONI.saft },
  { cheie: "ai", titlu: "AI care lucreaz\u0103 pentru tine", sub: "OCR, contare propus\u0103, sugestii care \u00eenva\u021b\u0103 din corec\u021biile tale, Povestea lunii.", ...CULORI_CARD.violet, icon: ICONI.ai },
  { cheie: "pachet", titlu: "Pachet lunar pentru client", sub: "Grafic, situa\u021bie financiar\u0103, cifre live \u0219i previziune bani \u00een portal.", ...CULORI_CARD.teal, icon: ICONI.pachet },
];
const CARDURI_RAND2 = [
  { cheie: "cabinete", titlu: "G\u00e2ndit pentru cabinete", sub: "Multi-client, multi-utilizator, drepturi pe rol.", ...CULORI_CARD.verde, icon: ICONI.cabinet },
  { cheie: "efactura", titlu: "Facturare cu e-Factura", sub: "Emitere, valut\u0103, import XML ANAF, storno.", ...CULORI_CARD.piersica, icon: ICONI.factura },
  { cheie: "control", titlu: "Control fiscal automat", sub: "Verific\u0103 D112 vs contabilitate, TVA vs declara\u021bii.", ...CULORI_CARD.chihlimbar, icon: ICONI.scut },
  { cheie: "conformitate", titlu: "Mereu conform legisla\u021biei", sub: "Monitoriz\u0103m ANAF automat; modific\u0103rile intr\u0103 \u00een vigoare la zi.", ...CULORI_CARD.albastru, icon: ICONI.raport },
];
const INCREDERE = [
  { titlu: "Date securizate", sub: "la standarde ridicate", icon: ICONI.scutmic },
  { titlu: "Acces de oriunde", sub: "din cloud", icon: ICONI.nor },
  { titlu: "Suport dedicat", sub: "pentru cabinete", icon: ICONI.oameni },
  { titlu: "F\u0103r\u0103 costuri ascunse", sub: "pl\u0103\u021bi transparente", icon: ICONI.moneda },
];

function randCard(c) {
  return `
    <div class="pagina-card" style="background:${c.bg}">
      <div class="pagina-card-icon" style="color:${c.fg}">${svgIcon(c.icon, 24)}</div>
      <div class="pagina-card-titlu">${c.titlu}</div>
      <div class="pagina-card-sub">${c.sub}</div>
      <span class="pagina-card-sageata" style="color:${c.fg}">${svgIcon(ICONI.sageata, 18)}</span>
    </div>`;
}

export function ecranLogin(radacina) {
  const bara = document.createElement("header");
  bara.className = "pagina-bara";
  bara.innerHTML = `
    <div class="pagina-bara-stanga">
      <img class="pagina-bara-logo" src="/static/logo_simbol.png" alt="">
      <span class="pagina-bara-marca">iConta.eu</span>
    </div>
    <button class="pagina-bara-acces" id="pagina-acces-btn">Acces</button>
  `;
  radacina.appendChild(bara);

  const corp = document.createElement("div");
  corp.className = "pagina-corp";
  corp.innerHTML = `
    <div class="pagina-hero">
      <h1 class="pagina-hero-titlu">Un singur sistem.<br>Toate procesele.</h1>
      <p class="pagina-hero-sub">\u00cencarci documentele. iConta.eu le prelucreaz\u0103, propune contarea \u0219i verific\u0103 automat obliga\u021biile fiscale.</p>
    </div>
    <div class="pagina-carduri-sectiune">
      <div class="pagina-carduri-wrap">
        <div class="pagina-card-mare" style="background:#fdeef2">
          <div class="pagina-card-mare-icon accent-magenta">${svgIcon(ICOANE.brief, 30)}</div>
          <div class="pagina-card-mare-titlu">Funcționalități</div>
          <div class="pagina-card-mare-sub">Tot ce face platforma, pe șapte domenii — de la contabilitate la control fiscal.</div>
          <button type="button" class="pagina-card-buton" id="pagina-functionalitati-btn">Vezi tot</button>
        </div>
        <div class="pagina-carduri-randuri">
          <div class="pagina-carduri-rand">${CARDURI_RAND1.map(randCard).join("")}</div>
          <div class="pagina-carduri-rand">${CARDURI_RAND2.map(randCard).join("")}</div>
        </div>
      </div>
    </div>
    <div class="pagina-incredere">
      ${INCREDERE.map((i) => `
        <div class="pagina-incredere-item">
          <span class="pagina-incredere-icon">${svgIcon(i.icon, 22)}</span>
          <div>
            <div class="pagina-incredere-titlu">${i.titlu}</div>
            <div class="pagina-incredere-sub">${i.sub}</div>
          </div>
        </div>`).join("")}
    </div>
    <footer class="pagina-subsol">
      <a href="/public/termeni" target="_blank" rel="noopener">Termeni și condiții</a>
      <span> · </span><a href="/ghid">Ghiduri</a>
      <span> · </span><span>© iConta.eu · contact@iconta.eu</span>
    </footer>
  `;
  radacina.appendChild(corp);

  const overlay = document.createElement("div");
  overlay.className = "acces-overlay";
  overlay.hidden = true;
  overlay.innerHTML = `<div class="acces-modal" id="acces-modal"></div>`;
  radacina.appendChild(overlay);

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) inchideOverlay();
  });

  function deschideOverlay() {
    overlay.hidden = false;
    randeazaAlegere();
  }
  function inchideOverlay() {
    overlay.hidden = true;
  }

  document.querySelector("#pagina-acces-btn").addEventListener("click", deschideOverlay);
  const functBtn = document.querySelector("#pagina-functionalitati-btn");
  if (functBtn) functBtn.addEventListener("click", deschideFunctionalitati);

  const modal = overlay.querySelector("#acces-modal");

  // ---------- ecran 1: alege Intra in cont / Client nou ----------
  function randeazaAlegere() {
    modal.classList.remove("acces-modal-inreg");
    modal.innerHTML = `
      <button class="acces-x" id="acces-x" aria-label="Închide">✕</button>
      <div class="login-brand">
        <img class="login-logo-img" src="/static/logo_login.png" alt="iConta.eu">
        <span class="login-tagline">Contabilitatea cu control fiscal</span>
      </div>
      <div class="acces-alegere">
        <button class="acces-card" id="acces-intra">
          <div class="acces-card-icon" style="background:#e9f0fe;color:#1d4ed8">
            <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><path d="M10 17l5-5-5-5"/><path d="M15 12H3"/></svg>
          </div>
          <div class="acces-card-text">
            <div class="acces-card-titlu">Intră în cont</div>
            <div class="acces-card-sub">Ai deja un cont iConta.eu</div>
          </div>
          <svg class="acces-card-sageata" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>
        </button>
        <button class="acces-card" id="acces-client-nou">
          <div class="acces-card-icon accent-verde">
            <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18"/><path d="M5 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16"/><path d="M19 21V11a2 2 0 0 0-2-2h-2"/><path d="M9 7h2M9 11h2M9 15h2"/></svg>
          </div>
          <div class="acces-card-text">
            <div class="acces-card-titlu">Client nou</div>
            <div class="acces-card-sub">Înregistrează cabinetul tău</div>
          </div>
          <svg class="acces-card-sageata" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>
        </button>
      </div>
    `;
    modal.querySelector("#acces-x").addEventListener("click", inchideOverlay);
    modal.querySelector("#acces-intra").addEventListener("click", randeazaLogin);
    modal.querySelector("#acces-client-nou").addEventListener("click", randeazaPreturiInainte);
  }

  // ---------- ecran 2a: login (doua cai explicite) ----------  // ux_login_camera_v1
  function randeazaLogin() {
    modal.classList.remove("acces-modal-inreg");
    modal.innerHTML = `
      <button type="button" class="nav-sageata" id="login-la-alegere" title="Înapoi" aria-label="Înapoi" style="position:absolute;top:14px;left:14px"><span aria-hidden="true">←</span></button>
      <button class="acces-x" id="acces-x" aria-label="Închide">✕</button>
      <div class="login-brand">
        <img class="login-logo-img" src="/static/logo_login.png" alt="iConta.eu">
        <span class="login-tagline">Contabilitatea cu control fiscal</span>
      </div>
      <button class="acces-card meniu-card" id="lg-client">
        <div class="acces-card-text">
          <div class="acces-card-titlu">Sunt client al unui cabinet</div>
          <div class="acces-card-sub">Intri cu un link primit pe email — fără parolă</div>
        </div>
      </button>
      <button class="acces-card meniu-card" id="lg-cabinet">
        <div class="acces-card-text">
          <div class="acces-card-titlu">Sunt cabinet de contabilitate</div>
          <div class="acces-card-sub">Intri cu email și parolă</div>
        </div>
      </button>
    `;
    modal.querySelector("#acces-x").addEventListener("click", inchideOverlay);
    modal.querySelector("#lg-client").addEventListener("click", formClient);
    modal.querySelector("#lg-cabinet").addEventListener("click", formCabinet);
  }

  function formClient() {
    modal.innerHTML = `
      <button type="button" class="nav-sageata" id="lgc-inapoi" title="Înapoi" aria-label="Înapoi" style="position:absolute;top:14px;left:14px"><span aria-hidden="true">←</span></button>
      <button class="acces-x" id="acces-x" aria-label="Închide">✕</button>
      <div class="login-brand">
        <img class="login-logo-img" src="/static/logo_login.png" alt="iConta.eu">
        <span class="login-tagline">Portalul tău, fără parolă</span>
      </div>
      <form id="lg-form-client" onsubmit="return false">
      <label class="camp">
        <span class="camp-eticheta">Emailul cu care intri în portal</span>
        <input type="email" class="camp-input" id="lgc-email" autocomplete="username" autofocus>
      </label>
      <p class="ecran-nota" style="margin:0 0 12px">Îți trimitem pe email un link de logare. Îl apeși și ai intrat.</p>
      <button type="submit" class="buton-primar" id="lgc-trimite">Trimite-mi linkul de logare</button>
      <p id="lgc-msg" style="margin:10px 0 0"></p>
      </form>
    `;
    modal.querySelector("#acces-x").addEventListener("click", inchideOverlay);
    modal.querySelector("#lgc-inapoi").addEventListener("click", randeazaLogin);
    const email = modal.querySelector("#lgc-email");
    const btn = modal.querySelector("#lgc-trimite");
    btn.addEventListener("click", async () => {
      const msg = modal.querySelector("#lgc-msg");
      const em = (email.value || "").trim();
      if (!em.includes("@")) { arataMesaj(msg, "Completează emailul mai întâi.", "eroare"); return; }
      btn.disabled = true; btn.textContent = "Se trimite...";
      try {
        const r = await api.post("/public/magic-link", { email: em });
        arataMesaj(msg, r.mesaj || "Linkul a plecat. Verifică emailul (și Spam).", "info");
        btn.textContent = "Trimis ✓";
      } catch (e) {
        btn.disabled = false; btn.textContent = "Trimite-mi linkul de logare";
        arataMesaj(msg, e.mesaj || e.message, "eroare");
      }
    });
    email.addEventListener("keydown", (e) => { if (e.key === "Enter") btn.click(); });
  }

  function randeazaResetCere() {  // [reset_parola_v1] "Am uitat parola": email -> raspuns IDENTIC (anti-enumerare)
    modal.classList.remove("acces-modal-inreg");
    modal.innerHTML = `
      <button type="button" class="nav-sageata" id="rst-inapoi" title="Înapoi" aria-label="Înapoi" style="position:absolute;top:14px;left:14px"><span aria-hidden="true">←</span></button>
      <button class="acces-x" id="acces-x" aria-label="Închide">✕</button>
      <div class="login-brand">
        <img class="login-logo-img" src="/static/logo_login.png" alt="iConta.eu">
        <div class="login-subtagline">Am uitat parola</div>
      </div>
      <p class="ecran-nota" style="margin:0 0 12px">Introdu emailul contului de cabinet. Dacă adresa e înregistrată, primești pe email un link de resetare, valabil 60 de minute.</p>
      <label class="camp">
        <span class="camp-eticheta">Email</span>
        <input type="email" class="camp-input" id="rst-email" autocomplete="username" autofocus>
      </label>
      <button class="buton-primar" id="rst-trimite">Trimite linkul de resetare</button>
      <p id="rst-msg" style="margin:10px 0 0"></p>
    `;
    modal.querySelector("#acces-x").addEventListener("click", inchideOverlay);
    modal.querySelector("#rst-inapoi").addEventListener("click", randeazaLogin);
    const btn = modal.querySelector("#rst-trimite");
    const msg = modal.querySelector("#rst-msg");
    btn.addEventListener("click", async () => {
      const em = (modal.querySelector("#rst-email").value || "").trim();
      if (!em.includes("@")) { arataMesaj(msg, "Completează un email valid.", "eroare"); return; }
      btn.disabled = true;
      try {
        const r = await api.post("/public/reset-parola/cere", { email: em });
        arataMesaj(msg, (r && r.mesaj) || "Dacă adresa e înregistrată, vei primi un mesaj.", "info");
      } catch (e) { arataMesaj(msg, e.mesaj || "Prea multe cereri. Încearcă mai târziu.", "info"); }
      btn.disabled = false;
    });
  }

  function formCabinet() {
    modal.innerHTML = `
      <button type="button" class="nav-sageata" id="login-inapoi" title="Înapoi" aria-label="Înapoi" style="position:absolute;top:14px;left:14px"><span aria-hidden="true">←</span></button>
      <button class="acces-x" id="acces-x" aria-label="Închide">✕</button>
      <div class="login-brand">
        <img class="login-logo-img" src="/static/logo_login.png" alt="iConta.eu">
        <span class="login-tagline">Contabilitatea cu control fiscal</span>
      </div>
      <form id="login-form" onsubmit="return false">
      <label class="camp">
        <span class="camp-eticheta">Email<span class="oblig">*</span></span>
        <input type="email" name="email" class="camp-input" id="login-email" autocomplete="username" autofocus>
      </label>
      <label class="camp">
        <span class="camp-eticheta">Parol\u0103<span class="oblig">*</span></span>
        <input type="password" class="camp-input" name="password" id="login-parola" autocomplete="current-password">
      </label>
      <div class="login-eroare" id="login-eroare" hidden></div>
      <button type="submit" class="buton-primar" id="login-buton">Autentificare</button>
      <button type="button" class="btn-link" id="acc-magic" style="margin-top:10px;display:block">Trimite-mi link de logare (fără parolă)</button>
      <button type="button" class="btn-link" id="acc-reset" style="margin-top:4px;display:block">Am uitat parola</button>
      <p id="acc-magic-msg" style="margin:6px 0 0"></p>
      </form>
    `;
    modal.querySelector("#acces-x").addEventListener("click", inchideOverlay);
    modal.querySelector("#login-inapoi").addEventListener("click", randeazaLogin);
    // [beta_gate_v1] campul de cod = DERIVAT din BETA_COD_ACCES (o singura sursa), via /public/config;
    // apare DOAR cand poarta e activa. La repunerea portii diseara reapare singur, fara schimbare de cod.
    api.get("/public/config").then((cfg) => {
      if (cfg && cfg.beta) {
        const er = modal.querySelector("#login-eroare");
        if (!er) return;
        const lbl = document.createElement("label");
        lbl.className = "camp";
        lbl.innerHTML = '<span class="camp-eticheta">Cod acces</span><input type="text" class="camp-input" id="login-cod" autocomplete="off" placeholder="doar \u00een perioada de testare">';
        er.parentNode.insertBefore(lbl, er);
      }
    }).catch((e) => { console.warn("[beta_gate] /public/config indisponibil - campul de cod beta nu apare", e); });  // prefetch optional: nu e o actiune a userului; daca beta e activ, respingerea login-ului aduce mesajul real

    const email = modal.querySelector("#login-email");
    const parola = modal.querySelector("#login-parola");
    const bMagic = modal.querySelector("#acc-magic");  /* magic_link_fe_v2 */
    if (bMagic) bMagic.addEventListener("click", async () => {
      const msg = modal.querySelector("#acc-magic-msg");
      const em = (email.value || "").trim();
      if (!em.includes("@")) { arataMesaj(msg, "Completează emailul mai întâi.", "eroare"); return; }
      try {
        const r = await api.post("/public/magic-link", { email: em });
        arataMesaj(msg, r.mesaj, "info");
      } catch (e) { arataMesaj(msg, e.mesaj || e.message, "eroare"); }
    });
    const bReset = modal.querySelector("#acc-reset");  // [reset_parola_v1]
    if (bReset) bReset.addEventListener("click", randeazaResetCere);
    const buton = modal.querySelector("#login-buton");
    const eroare = modal.querySelector("#login-eroare");

    function arataEroare(text) {
      eroare.textContent = text;
      eroare.hidden = false;
    }
    async function intra() {
      eroare.hidden = true;
      if (!email.value || !parola.value) {
        arataEroare("Completează email și parolă.");
        return;
      }
      buton.disabled = true;
      buton.textContent = "Se verifică…";
      try {
        const r = await api.post("/auth/login", {
          email: email.value.trim(),
          parola: parola.value,
          cod_acces: (document.getElementById("login-cod")?.value || "").trim(),
        });
        sesiune.intra(r.token, r.user);
      } catch (e) {
        arataEroare(e.mesaj || "Autentificare eșuată.");
        buton.disabled = false;
        buton.textContent = "Autentificare";
      }
    }
    buton.addEventListener("click", intra);
    parola.addEventListener("keydown", (e) => { if (e.key === "Enter") intra(); });
    email.addEventListener("keydown", (e) => { if (e.key === "Enter") parola.focus(); });
  }

  // ---------- ecran 2b: inregistrare cabinet nou ----------
  function randeazaPreturiInainte() {  // [preturi_reg_v1] mereu pretul INTAI, apoi Continua -> formularul existent. O singura cale, fara detectie de provenienta. Continut din preturi.js (sursa unica).
    modal.classList.remove("acces-modal-inreg");
    modal.innerHTML = `
      <button type="button" class="nav-sageata" id="pr-inapoi" title="Înapoi" aria-label="Înapoi" style="position:absolute;top:14px;left:14px"><span aria-hidden="true">←</span></button>
      <button class="acces-x" id="acces-x" aria-label="Închide">✕</button>
      <div class="login-brand">
        <img class="login-logo-img" src="/static/logo_login.png" alt="iConta.eu">
        <div class="login-subtagline">${esc(PRETURI_TITLU)}</div>
      </div>
      <div class="preturi-text preturi-text-modal">${preturiHTML()}</div>
      <button class="buton-primar" id="pr-continua" style="margin-top:16px">Continuă</button>
    `;
    modal.querySelector("#acces-x").addEventListener("click", inchideOverlay);
    modal.querySelector("#pr-inapoi").addEventListener("click", randeazaAlegere);
    modal.querySelector("#pr-continua").addEventListener("click", randeazaInregistrare);
  }

  function randeazaInregistrare() {
    modal.classList.add("acces-modal-inreg");
    modal.innerHTML = `
      <button class="acces-x" id="acces-x" aria-label="Închide">✕</button>
      <div class="login-brand">
        <img class="login-logo-img" src="/static/logo_login.png" alt="iConta.eu">
        <span class="login-tagline">Contabilitatea cu control fiscal</span>
        <div class="login-subtagline">Înregistrează cabinetul tău</div>
      </div>
      <label class="camp">
        <span class="camp-eticheta">CUI</span>
        <div style="display:flex; gap:8px;">
          <input type="text" class="camp-input" id="reg-cui" autofocus style="flex:1">
          <button type="button" class="buton-primar acces-verifica-btn" id="reg-cui-verifica">Verifică la ANAF</button>
        </div>
        <div id="reg-cui-info" class="tip-micut" style="margin-top:6px"></div>
      </label>
      <label class="camp">
        <span class="camp-eticheta">Denumire cabinet de contabilitate/contabil<span class="oblig">*</span></span>
        <input type="text" class="camp-input" id="reg-cabinet">
      </label>
      <label class="camp">
        <span class="camp-eticheta">Nume administrator</span>
        <input type="text" class="camp-input" id="reg-nume-admin">
      </label>
      <label class="camp">
        <span class="camp-eticheta">Email<span class="oblig">*</span></span>
        <input type="email" class="camp-input" id="reg-email" autocomplete="off" placeholder="nume@firma.ro">
      </label>
      <label class="camp">
        <span class="camp-eticheta">Parol\u0103<span class="oblig">*</span></span>
        <input type="password" class="camp-input" id="reg-parola" autocomplete="off">
      </label>
      <label class="camp">
        <span class="camp-eticheta">Confirm\u0103 parola<span class="oblig">*</span></span>
        <input type="password" class="camp-input" id="reg-parola2" autocomplete="off">
      </label>
      <div class="login-eroare" id="reg-eroare" hidden></div>
      <label class="set-bifa" style="margin:4px 0 12px"><input type="checkbox" id="reg-termeni"> <span>Am citit și accept <a href="/public/termeni" target="_blank" rel="noopener">Termenii și condițiile</a><span class="oblig">*</span></span></label>
      <button class="buton-primar" id="reg-buton">Creează cont</button>
    `;
    modal.querySelector("#acces-x").addEventListener("click", inchideOverlay);

    const cui = modal.querySelector("#reg-cui");
    const cuiBtn = modal.querySelector("#reg-cui-verifica");
    const cuiInfo = modal.querySelector("#reg-cui-info");
    const cabinet = modal.querySelector("#reg-cabinet");
    const numeAdmin = modal.querySelector("#reg-nume-admin");  // null in modul gratuit
    const email = modal.querySelector("#reg-email");
    const parola = modal.querySelector("#reg-parola");
    const parola2 = modal.querySelector("#reg-parola2");
    const buton = modal.querySelector("#reg-buton");
    const eroare = modal.querySelector("#reg-eroare");

    cuiBtn.addEventListener("click", async () => {
      const val = (cui.value || "").trim();
      if (!val) { cuiInfo.textContent = "Introdu CUI-ul mai întâi."; cuiInfo.style.color = "#a32d2d"; return; }
      cuiBtn.disabled = true;
      cuiBtn.textContent = "Se verifică…";
      cuiInfo.textContent = "";
      try {
        const r = await api.get(`/public/verifica-cui/${encodeURIComponent(val)}`);
        if (!r || !r.gasit) {
          cuiInfo.textContent = "Nu apare la ANAF prin acest CUI (posibil înregistrat ca PFI, direct la ANAF, fără ONRC). Completează denumirea manual mai jos.";
          cuiInfo.style.color = "#92500a";
        } else {
          cabinet.value = r.denumire || cabinet.value;
          if (r.cod_caen && r.cod_caen !== "6920") {
            cuiInfo.textContent = `Găsit: ${r.denumire}. Atenție — CAEN ${r.cod_caen}, nu 6920 (contabilitate).`;
            cuiInfo.style.color = "#92500a";
          } else {
            cuiInfo.textContent = `Găsit: ${r.denumire}${r.cod_caen ? " · CAEN " + r.cod_caen : ""}.`;
            cuiInfo.style.color = "#16a34a";
          }
        }
      } catch {
        cuiInfo.textContent = "Nu am putut verifica automat la ANAF acum. Poți continua, completează datele manual mai jos.";
        cuiInfo.style.color = "#616161";
      }
      cuiBtn.disabled = false;
      cuiBtn.textContent = "Verifică la ANAF";
    });

    function arataEroare(text) {
      eroare.textContent = text;
      eroare.hidden = false;
    }
    function separaNume(numeComplet) {
      const parti = numeComplet.trim().split(/\s+/).filter(Boolean);
      if (parti.length === 0) return { nume: null, prenume: null };
      if (parti.length === 1) return { nume: parti[0], prenume: null };
      const prenume = parti[parti.length - 1];
      const nume = parti.slice(0, -1).join(" ");
      return { nume, prenume };
    }
    async function creeaza() {
      eroare.hidden = true;
      if (!cabinet.value || !email.value || !parola.value) {
        arataEroare("Completează denumire cabinet, email și parolă.");
        return;
      }
      if (parola.value !== parola2.value) {
        arataEroare("Parolele nu coincid.");
        return;
      }
      if (!modal.querySelector("#reg-termeni")?.checked) {
        arataEroare("Trebuie să accepți Termenii și condițiile.");
        return;
      }
      buton.disabled = true;
      buton.textContent = "Se creează…";
      const { nume, prenume } = separaNume((numeAdmin && numeAdmin.value) || "");
      try {
        /* [register_firma_v2 27.07.2026] Raspunsul de la register poarta `firma_creata`.
           Inainte era ARUNCAT: daca provisionarea primei firme esua, userul intra in
           aplicatie si gasea zero firme, fara nicio explicatie. Contul e valid, deci NU
           blocam intrarea - dar avertismentul se pastreaza si se arata dupa logare. */
        const _reg = await api.post("/auth/register", {
            email: email.value.trim(),
            parola: parola.value,
            nume_cabinet: cabinet.value.trim(),
            cui: (cui.value || "").trim(),  /* register_primul_tenant_v1 */
            nume,
            prenume,
            accept_termeni: !!modal.querySelector("#reg-termeni")?.checked,  /* [termeni_v1] */
        });
        const _avertReg = (_reg && _reg.firma_creata === false) ? (_reg.avertisment || "") : "";
        const r = await api.post("/auth/login", {
          email: email.value.trim(),
          parola: parola.value,
        });
        sesiune.intra(r.token, r.user);
        if (_avertReg) {
          /* mesaj de stare, nu caseta permanenta: situatia e temporara (firma se adauga
             din ecranul Firme). DS cap.6 - arataMesaj e singura cale pentru stari. */
          setTimeout(() => arataMesaj(document.body, _avertReg, "avert"), 400);
        }
      } catch (e) {
        arataEroare(e.mesaj || "Nu am putut crea contul.");
        buton.disabled = false;
        buton.textContent = "Creează cont";
      }
    }
    buton.addEventListener("click", creeaza);
  }
}

// landing_diacritice_v1

// landing_texte_v3

// landing_carduri_v2

// login_form_v1


// [F203] Pagina Functionalitati (client-side; replica VIZUALA a modalului DS - nav.deschide e shell autentificat, indisponibil pre-login)
// <GRUPE_FUNC_AUTO> generat de genereaza_grupe_functii.py --scrie; NU edita manual intre ancore (gardat de GRUPE_FUNC_STALE)
const GRUPE_FUNC = [{"titlu": "Contabilitate", "icon": "brief", "functii": ["Avansuri furnizori/clienti", "Bacsis HoReCa", "Bilant anual S1005/S1003", "Blocare perioade", "Centre de cost + bugete (management accounting intern)", "Contabilitate ONG", "Decontari asociati", "Deconturi deplasare si diurna", "Editor note contabile", "Incredere si invatare AI", "Leasing financiar si operational", "Lichidare/radiere societate", "Motor contabil (carte mare + inchidere)", "Perisabilitati si scazaminte", "Productie in curs si produse finite", "Provizioane si ajustari", "Rapoarte comerciale", "Rapoarte configurabile salvabile", "Reevaluare imobilizari", "Registru incasari/plati (partida simpla)", "SGR (garantie-returnare)", "Sponsorizari si credit fiscal", "Subventii"]}, {"titlu": "Fiscalitate", "icon": "declaratii", "functii": ["Coada de validare patru-ochi", "Curs valutar BNR", "D406 SAF-T lunar", "Declaratia D100", "Declaratia D101 + IMCA", "Declaratia D112", "Declaratia D205 + distribuire dividende", "Declaratia D300", "Declaratia D301", "Declaratia D390 (VIES)", "Declaratia D394", "Declaratia D710 (rectificativa D100)", "Diferente de curs valutar", "Dispatch declaratii", "Import/export extracomunitar", "Motor D212 (PFA/II/IF)", "Persistarea declaratiei depuse (xml + randuri) - F163v2", "Regim special agentii de turism", "Regim special agricultori", "Regim special aur de investitii", "Regim special marja (second-hand)", "Regula cotelor de TVA", "TVA la incasare", "Taxare inversa interna", "Trimitere D390 clasificari manuale"]}, {"titlu": "Control fiscal", "icon": "shield", "functii": ["Audit de preluare firma", "Avertisment regim TVA vs ANAF + semafor Control fiscal", "Calculul scadentelor", "Conformitate cota TVA facturi emise (punte legislatie->re-verificare v1)", "Control incrucisat: D112 (salarii) vs contabilitate", "Control incrucisat: D390 (bunuri IC) vs evidenta validata + D300 depus (D-vs-D real F198)", "Control incrucisat: declaratie vs contabilitate (TVA)", "Educatie AI pe tipare (varianta generativa)", "Educatie pe tipare de erori", "Push in-app findinguri rosii control fiscal (pull->push)", "Semafor conformare fiscala", "Vector fiscal per firma", "Verificatoare de coerenta", "Verificator praguri Intrastat"]}, {"titlu": "Facturare si e-Factura", "icon": "facturi", "functii": ["Chitante emise", "Comodat, chirii, refacturari", "Conector OAuth SPV/ANAF", "Conector WooCommerce", "Cont venit implicit setabil din UI", "Contare facturi + TVA + storno", "Export facturi emise catre SAGA", "Export facturi emise catre WinMENTOR", "Facturi recurente", "Import e-Factura (UBL)", "Link de plata pe factura", "Nomenclator produse + cota AI", "Notificare e-Transport", "Notificari de plata si alerte neplatnici", "Operatiuni intracomunitare", "PDF factura", "Parteneri (clienti/furnizori)", "Profil firma + model factura", "Trimitere e-Transport prin API SPV", "Validare CUI la ANAF", "e-Factura SPV complet"]}, {"titlu": "Salarizare", "icon": "users", "functii": ["Adeverinte salariati", "Calcul salarizare (brut->net)", "Client REGES-ONLINE", "Cod 10 CM in flux", "Coduri COR pe contracte", "Contracte de munca speciale", "Plata salariilor pe card (fisier bancar)", "Pontaj angajati", "Salariati (CRUD)", "Stat de plata + fluturasi", "Tichete de masa + vacanta + cadou in stat plata (Faza 1 + 2a + 2b1)"]}, {"titlu": "Stocuri, banca si casa", "icon": "building", "functii": ["Analitica de stoc", "Coduri de bare in gestiune", "Contabilizare extras de cont", "Credite bancare si garantii", "Import Raport Z din AMEF", "Import articole si stoc initial CV", "Import extras bancar MT940 (SWIFT)", "Inventar pe mobil", "Inventariere anuala", "Landed cost pe NIR", "Obiecte de inventar", "Parser extras bancar", "Punte factura -> stoc (descarcare la emitere)", "Reconciliere bancara (matching)", "Registru de casa + plafoane", "Retetar HoReCa (GV)", "Stocuri cantitativ-valorice (CMP)", "Stocuri global-valorice", "Transfer intre gestiuni"]}, {"titlu": "Cabinet si portal client", "icon": "documente", "functii": ["API portal (read-only, izolat)", "API public v1", "Alerte legislative programate", "Autoservire export date cabinet (buton)", "Canal de sesizari (Raporteaza)", "Cerere de stergere cont din aplicatie (GDPR art.17)", "Chei API publice per cabinet", "Documente pentru portal", "Export GDPR complet cabinet (portabilitate)", "Forecast cash-flow 8 saptamani", "Generare contracte", "Import la preluarea firmei", "Inregistrare cabinet self-service", "KPI client (portal)", "Magic-link (login fara parola)", "Management actori de cabinet", "Notificari in-app + email", "Notificari pe evenimente", "PWA (aplicatie instalabila)", "Panou Capacitate", "Povestea lunii (pachet lunar)", "Pre-completare date firma din ANAF v9 la onboarding", "Previzualizare portal client din cabinet (Acces Client)", "Registratura documente", "Scadente viitoare pe portofoliu", "Sinteza zilnica pe email", "Starea migrarii pe straturi", "Suspendare cabinet", "Triaj AI al sesizarilor"]}];
// </GRUPE_FUNC_AUTO>

function _funcOverlay(inner) {
  const o = document.createElement("div");
  o.className = "fereastra-overlay func-overlay";
  o.innerHTML = inner;
  o.addEventListener("click", (e) => { if (e.target === o) o.remove(); });
  const x = o.querySelector(".nav-x");
  if (x) x.addEventListener("click", () => o.remove());
  document.body.appendChild(o);
  return o;
}

function deschideFereastraGrupa(gr) {
  const lista = gr.functii.map((f) => `<li>${esc(f)}</li>`).join("");
  _funcOverlay(
    `<div class="fereastra"><div class="fereastra-antet"><span class="fereastra-titlu">${esc(gr.titlu)}</span>` +
    `<button class="nav-x" type="button" title="Închide" aria-label="Închide">✕</button></div>` +
    `<div class="fereastra-corp"><ul class="func-lista">${lista}</ul></div></div>`
  );
}

function deschideFereastraPreturi() {  // [preturi_v1] continut din preturi.js (sursa unica), afisat ca fereastra ca la grupe
  _funcOverlay(
    `<div class="fereastra"><div class="fereastra-antet"><span class="fereastra-titlu">${esc(PRETURI_TITLU)}</span>` +
    `<button class="nav-x" type="button" title="Închide" aria-label="Închide">✕</button></div>` +
    `<div class="fereastra-corp"><div class="preturi-text">${preturiHTML()}</div></div></div>`
  );
}

function deschideFunctionalitati() {
  // [preturi_v1] cardul Preturi = PRIMUL, scris de mana (in afara zonei auto GRUPE_FUNC); nu se sterge la --scrie
  const cardPreturi =
    `<button class="func-card func-card-preturi" type="button" data-preturi="1"><span class="func-card-icon">${svgIcon(ICOANE.gauge, 26)}</span>` +
    `<span class="func-card-titlu">${esc(PRETURI_TITLU)}</span><span class="func-card-nr">${esc(PRETURI_SUBTITLU)}</span></button>`;
  const carduri = cardPreturi + GRUPE_FUNC.map((gr, i) =>
    `<button class="func-card" type="button" data-i="${i}"><span class="func-card-icon">${svgIcon(ICOANE[gr.icon], 26)}</span>` +
    `<span class="func-card-titlu">${esc(gr.titlu)}</span><span class="func-card-nr">${gr.functii.length} funcții</span></button>`
  ).join("");
  const o = _funcOverlay(
    `<div class="fereastra fer-larg"><div class="fereastra-antet"><span class="fereastra-titlu">Funcționalități</span>` +
    `<button class="nav-x" type="button" title="Închide" aria-label="Închide">✕</button></div>` +
    `<div class="fereastra-corp"><div class="func-grila">${carduri}</div></div></div>`
  );
  o.querySelector(".func-card-preturi").addEventListener("click", deschideFereastraPreturi);
  o.querySelectorAll(".func-card:not(.func-card-preturi)").forEach((b) =>
    b.addEventListener("click", () => deschideFereastraGrupa(GRUPE_FUNC[+b.dataset.i])));
}
