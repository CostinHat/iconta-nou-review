// login.js — poarta de intrare.
// Bara sus: logo + buton "Acces". Acces deschide central un modal umbrit
// cu 2 optiuni: Intra in cont (login existent) / Client nou (inregistrare cabinet).
import { api, arataMesaj, arataRefuzul, CULORI_CARD, ICOANE, esc, semnAjutor, inchidereDialog, focusFaraSalt, cate } from "../api.js?v=9bcf50c899";
import { PRETURI_TITLU, preturiHTML } from "./preturi.js?v=0e00a65657";  // [preturi_v1] sursa unica a continutului de preturi
import { sesiune } from "../sesiune.js?v=898215e0ee";
import { ciornaFormular } from "../ciorna_formular.js?v=461bec469f";  // [267] ciorna formularului de înregistrare
import { legaDateAnaf } from "./date_anaf.js?v=503d474ed1";   // [lotul 12, 459.1] datele aduse de la ANAF țin de CUI-ul lor
import { sesiuneInternaDeschisa } from "./admin_analytics.js?v=440f824e89";   // [lotul 13, 649] vizitele noastre nu se numără

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

// [analytics_public_v1] eveniment public anonim (ce/de unde/cand) - fire-and-forget, nu blocheaza
// randarea, fara date personale (fara IP/UA/cookie/sesiune). Endpoint intern /api/eveniment-public.
// [lotul 13, 649] vizitele dintr-un browser cu o sesiune iConta deschisă (cabinet sau Panou Admin — testele noastre) nu se numără;
// nimic în plus nu pleacă la server (`admin_analytics.sesiuneInternaDeschisa`)
function evPublic(tip, pagina) {
  if (sesiuneInternaDeschisa()) return;
  try {
    const corp = JSON.stringify({ tip, pagina: pagina || "landing" });
    if (navigator.sendBeacon) {
      navigator.sendBeacon("/api/eveniment-public", new Blob([corp], { type: "application/json" }));
    } else {
      fetch("/api/eveniment-public", { method: "POST", headers: { "Content-Type": "application/json" }, body: corp, keepalive: true });
    }
  } catch (_e) { /* niciodata nu strica pagina */ }
}

export function ecranLogin(radacina) {
  evPublic("vizita_landing");
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
          <div class="pagina-card-mare-titlu">Funcționalități și prețuri</div>
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
  overlay.className = "acces-overlay";  /* fereastra-de-lucru: doar X — poartă formularele de intrare/înregistrare (DECIZII 04.10.2026) */
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

  // [14.10.2026, comanda Costin pct.3, verbatim în DECIZII „Lotul 2”] „Înregistrarea liberă se închide: în pilot, conturile noi se
  // creează numai prin invitație.” Linkul din emailul de invitație (`/#invitatie=<token>`) deschide direct drumul înregistrării;
  // fără el, „Client nou” spune cum se cere invitația (formularul nu se mai arată).
  const INVITATIE = (location.hash.match(/#invitatie=([\w-]+)/) || [])[1] || "";
  if (INVITATIE) { overlay.hidden = false; randeazaPreturiInainte(); }   // [14.10.2026] linkul de invitație deschide înregistrarea
  // [15.10.2026, „Lotul 4” pct.2, verbatim în DECIZII] linkul din emailul de confirmare (`/#confirmare=<token>`) activează contul
  const CONFIRMARE = (location.hash.match(/#confirmare=([\w-]+)/) || [])[1] || "";
  if (CONFIRMARE) { overlay.hidden = false; randeazaConfirmare(); }

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
    modal.querySelector("#acces-intra").addEventListener("click", () => { evPublic("intra_in_cont"); randeazaLogin(); });
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
      <p class="ecran-nota" style="margin:12px 0 0;text-align:center">Nu ai cont? <button type="button" class="btn-link" id="acc-inreg" style="display:inline">\u00cenregistreaz\u0103 cabinetul</button></p>
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
        lbl.innerHTML = '<span class="camp-eticheta">Cod acces</span><input aria-label="Cod acces" type="text" class="camp-input" id="login-cod" autocomplete="off" placeholder="doar \u00een perioada de testare">';
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
    const bInreg = modal.querySelector("#acc-inreg");  // [login_spre_inregistrare_v1] cale catre inregistrare din ecranul de autentificare
    if (bInreg) bInreg.addEventListener("click", randeazaPreturiInainte);
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
    email.addEventListener("keydown", (e) => { if (e.key === "Enter") focusFaraSalt(parola); });
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
    modal.querySelector("#pr-continua").addEventListener("click", INVITATIE ? () => randeazaInregistrare(null) : randeazaDupaMod);
  }

  // ---------- [15.10.2026, lotul 4] „Client nou” fără invitație: comutatorul din Panou Admin decide (serverul spune) ----------
  async function randeazaDupaMod() {
    let st = null;
    try { st = await api.get("/public/inregistrare"); } catch (e) {
      randeazaFaraInvitatie();
      const m = modal.querySelector("#fi-mesaj");   // refuzul serverului, arătat pe loc (garda „refuz tăcut”)
      m.className = "caseta-atentie";
      m.innerHTML = `<div class="ca-mesaj pe-randuri">${esc((e && e.mesaj) || "Nu se poate verifica acum dacă înregistrarea e deschisă. Încearcă din nou peste câteva minute.")}</div>`;
      return;
    }
    if (st && st.deschisa) randeazaInregistrare(st); else randeazaFaraInvitatie(st && st.refuz && st.refuz.motiv);
  }

  // ---------- ecran 2b': fără invitație, cu înregistrarea închisă ----------
  function randeazaFaraInvitatie(mesaj) {
    modal.classList.remove("acces-modal-inreg");
    modal.innerHTML = `
      <button type="button" class="nav-sageata" id="fi-inapoi" title="Înapoi" aria-label="Înapoi" style="position:absolute;top:14px;left:14px"><span aria-hidden="true">←</span></button>
      <button class="acces-x" id="acces-x" aria-label="Închide">✕</button>
      <div class="login-brand">
        <img class="login-logo-img" src="/static/logo_login.png" alt="iConta.eu">
        <span class="login-tagline">Contabilitatea cu control fiscal</span>
      </div>
      <div class="caseta-info" id="fi-mesaj"><div class="ci-mesaj">${esc(mesaj || "Înregistrarea nu e disponibilă acum.").replace("contact@iconta.eu", '<a href="mailto:contact@iconta.eu">contact@iconta.eu</a>')}</div></div>
    `;
    modal.querySelector("#acces-x").addEventListener("click", inchideOverlay);
    modal.querySelector("#fi-inapoi").addEventListener("click", randeazaAlegere);
  }

  // ---------- [15.10.2026, lotul 4] după formularul liber: contul nu există până la clicul pe linkul din email ----------
  function randeazaVerificaEmail(em, ore) {
    modal.classList.remove("acces-modal-inreg");
    modal.innerHTML = `
      <button class="acces-x" id="acces-x" aria-label="Închide">✕</button>
      <div class="login-brand">
        <img class="login-logo-img" src="/static/logo_login.png" alt="iConta.eu">
        <span class="login-tagline">Contabilitatea cu control fiscal</span>
      </div>
      <div class="caseta-info" id="reg-verifica"><div class="ci-mesaj">Emailul de confirmare a plecat la <b>${esc(em)}</b>. Apasă linkul din el (valabil ${esc(cate(ore || 24, "oră", "ore"))}) ca să activezi contul. Până atunci contul nu există: nu te poți autentifica și nu se creează nicio firmă.</div></div>
      <p class="ecran-nota" style="margin:12px 0 0">Nu l-ai primit în câteva minute? Verifică și dosarul Spam.</p>
    `;
    modal.querySelector("#acces-x").addEventListener("click", inchideOverlay);
  }

  // ---------- [15.10.2026, lotul 4] clicul pe linkul de confirmare: abia acum se creează contul ----------
  async function randeazaConfirmare() {
    modal.classList.remove("acces-modal-inreg");
    const brand = `
      <button class="acces-x" id="acces-x" aria-label="Închide">✕</button>
      <div class="login-brand">
        <img class="login-logo-img" src="/static/logo_login.png" alt="iConta.eu">
        <span class="login-tagline">Contabilitatea cu control fiscal</span>
      </div>`;
    modal.innerHTML = `${brand}<p class="ecran-nota" id="conf-stare">Se activează contul…</p>`;
    let r = null;
    try { r = await api.post("/public/confirma-inregistrare", { token: CONFIRMARE }); } catch (e) {
      history.replaceState(null, "", location.pathname);   // tokenul nu rămâne în bara adresei
      // refuzul serverului (link folosit, expirat, inexistent), arătat pe loc (garda „refuz tăcut”)
      modal.innerHTML = `${brand}<div class="caseta-atentie" id="conf-rezultat"><div class="ca-mesaj pe-randuri">${esc((e && e.mesaj) || "Activarea contului nu s-a putut face acum. Încearcă din nou peste câteva minute.")}</div></div>
        <button class="buton-secundar" id="conf-inapoi" style="margin-top:12px">Înapoi</button>`;
      modal.querySelector("#conf-inapoi").addEventListener("click", randeazaAlegere);
      modal.querySelector("#acces-x").addEventListener("click", inchideOverlay);
      return;
    }
    history.replaceState(null, "", location.pathname);   // tokenul nu rămâne în bara adresei
    {
      modal.innerHTML = `${brand}<div class="caseta-info" id="conf-rezultat"><div class="ci-mesaj">Contul cabinetului <b>${esc(r.nume_cabinet)}</b> e activ. Intră cu emailul <b>${esc(r.email)}</b> și parola aleasă la înregistrare.</div></div>
        <button class="buton-primar" id="conf-intra" style="margin-top:12px">Intră în cont</button>`;
      modal.querySelector("#conf-intra").addEventListener("click", () => {
        formCabinet();
        const em = modal.querySelector("#login-email");
        if (em) { em.value = r.email; const p = modal.querySelector("#login-parola"); if (p) focusFaraSalt(p); }
      });
    }
    modal.querySelector("#acces-x").addEventListener("click", inchideOverlay);
  }

  async function randeazaInregistrare(liber) {
    // [14.10.2026] cu invitație validă: emailul vine din invitație (contul se creează numai cu el).
    // [15.10.2026, lotul 4] `liber` = starea înregistrării libere (cu cheia publică a widgetului anti-roboți, 257): emailul se scrie, contul vine la confirmare.
    let inv = null;
    if (!liber) {
      try { inv = await api.get(`/public/invitatie/${encodeURIComponent(INVITATIE)}`); } catch (e) { inv = { valida: false, refuz: { motiv: (e && e.mesaj) || "Invitația nu se poate verifica acum." } }; }
    }
    if (!liber && (!inv || !inv.valida)) {
      randeazaFaraInvitatie();
      const m = modal.querySelector("#fi-mesaj");
      m.className = "caseta-atentie";
      m.innerHTML = `<div class="ca-mesaj">${esc((inv && inv.refuz && inv.refuz.motiv) || "Invitația nu e valabilă.")}</div>`;
      return;
    }
    modal.classList.add("acces-modal-inreg");
    modal.innerHTML = `
      <button class="acces-x" id="acces-x" aria-label="Închide">✕</button>
      <div class="login-brand">
        <img class="login-logo-img" src="/static/logo_login.png" alt="iConta.eu">
        <span class="login-tagline">Contabilitatea cu control fiscal</span>
        <div class="login-subtagline">Înregistrează cabinetul tău ${semnAjutor("F108")}</div>
      </div>
      <p class="ecran-nota" id="reg-ciorna" hidden></p>
      <div class="grila-doc reg-grila" style="grid-template-columns:repeat(auto-fit, minmax(240px, 1fr))">
      <label class="camp">
        <span class="camp-eticheta">CUI</span>
        <div class="camp-cu-buton" style="display:flex; gap:8px;">
          <input type="text" class="camp-input" id="reg-cui" autofocus style="flex:1 1 90px; min-width:0">
          <button type="button" class="buton-primar acces-verifica-btn" id="reg-cui-verifica">Verifică la ANAF</button>
        </div>
        <div id="reg-cui-info" class="tip-micut"></div>
      </label>
      <label class="camp">
        <span class="camp-eticheta">Denumire cabinet de contabilitate/contabil<span class="oblig">*</span></span>
        <input type="text" class="camp-input" id="reg-cabinet">
      </label>
      <label class="camp">
        <span class="camp-eticheta">Email<span class="oblig">*</span></span>
        <input type="email" class="camp-input" id="reg-email" autocomplete="off" placeholder="nume@firma.ro"${liber ? "" : " readonly"}>
        <span class="camp-ajutor">${liber ? "Aici vine linkul de confirmare — contul se activează după clic." : "Emailul din invitație — contul se creează cu el."}</span>
      </label>
      <label class="camp">
        <span class="camp-eticheta">Telefon</span>
        <input type="tel" class="camp-input" id="reg-telefon" autocomplete="tel" placeholder="07xx xxx xxx">
        <span class="camp-ajutor">Opțional: pentru notificări pe WhatsApp, după intrarea în cont (Setări cont → Notificări).</span>
      </label>
      <label class="camp">
        <span class="camp-eticheta">Parol\u0103<span class="oblig">*</span></span>
        <input type="password" class="camp-input" id="reg-parola" autocomplete="off">
      </label>
      <label class="camp">
        <span class="camp-eticheta">Confirm\u0103 parola<span class="oblig">*</span></span>
        <input type="password" class="camp-input" id="reg-parola2" autocomplete="off">
      </label>
      <label class="camp">
        <span class="camp-eticheta">Nume administrator</span>
        <input type="text" class="camp-input" id="reg-nume-admin">
      </label>
      ${liber ? '<div class="camp" id="reg-robot"></div>' : ""}
      </div>
      <div class="reg-actiune">
        <label class="set-bifa"><input type="checkbox" id="reg-termeni"> <span>Am citit și accept <a href="/public/termeni" target="_blank" rel="noopener">Termenii și condițiile</a><span class="oblig">*</span></span></label>
        <div class="login-eroare pe-randuri" id="reg-eroare" hidden></div>
        <button class="buton-primar" id="reg-buton">Creează cont</button>
      </div>
    `;
    modal.querySelector("#acces-x").addEventListener("click", inchideOverlay);

    const cui = modal.querySelector("#reg-cui");
    const cuiBtn = modal.querySelector("#reg-cui-verifica");
    const cuiInfo = modal.querySelector("#reg-cui-info");
    const cabinet = modal.querySelector("#reg-cabinet");
    const numeAdmin = modal.querySelector("#reg-nume-admin");  // null in modul gratuit
    const email = modal.querySelector("#reg-email");
    if (!liber) email.value = inv.email;   // [14.10.2026] emailul invitației, needitabil
    const parola = modal.querySelector("#reg-parola");
    const parola2 = modal.querySelector("#reg-parola2");
    const buton = modal.querySelector("#reg-buton");
    const eroare = modal.querySelector("#reg-eroare");
    // [267] ce s-a completat rămâne la închidere / ieșirea din pagină și revine la redeschidere — fără parole; se șterge la cont creat
    const ciorna = ciornaFormular(modal, liber ? "iconta_ciorna_inregistrare" : "iconta_ciorna_inregistrare_invitatie",
      ["reg-cui", "reg-cabinet", "reg-nume-admin", "reg-email", "reg-telefon", "reg-termeni"]);
    if (ciorna.refacuta) {
      const nota = modal.querySelector("#reg-ciorna");
      nota.textContent = "Datele completate data trecută au fost păstrate (parolele nu se păstrează).";
      nota.hidden = false;
    }
    // [257] Cloudflare Turnstile: verificarea anti-roboți, numai la înregistrarea liberă (invitația e deja nominală). Tokenul ei se
    // folosește o singură dată: după un refuz al serverului, widgetul se resetează și dă unul nou.
    let tokenRobot = null;
    let widgetRobot = null;
    if (liber) {
      incarcaTurnstile(liber.turnstile_script).then((ts) => {
        widgetRobot = ts.render(modal.querySelector("#reg-robot"), {
          sitekey: liber.turnstile_sitekey,
          language: "ro",
          callback: (t) => { tokenRobot = t; },
          "expired-callback": () => { tokenRobot = null; },
          "error-callback": () => { tokenRobot = null; arataEroare("Verificarea anti-roboți nu s-a putut face. Reîncarcă pagina și încearcă din nou."); },
        });
      }).catch(() => arataEroare("Verificarea anti-roboți nu s-a putut încărca (Cloudflare nu răspunde). Încearcă din nou peste câteva minute."));
    }

    // [lotul 12, 642] verdictul „Verifică la ANAF” e al CUI-ului verificat: la orice schimbare a CUI-ului dispare (ca la Date firmă,
    // corectura CUI-ului), altfel ar sta lângă un alt CUI — sau, la refuzul de la „Creează cont”, ar repeta textul refuzului.
    // [lotul 12, 459.1, comanda Costin 12.2 pct.5] la fel denumirea cabinetului adusă de ANAF, dacă omul n-a schimbat-o (`date_anaf.js`, F188)
    const anaf = legaDateAnaf(cui, [cabinet], cuiInfo);
    cuiBtn.addEventListener("click", async () => {
      const val = (cui.value || "").trim();
      if (!val) { cuiInfo.textContent = "Introdu CUI-ul mai întâi."; cuiInfo.style.color = "#a32d2d"; return; }
      cuiBtn.disabled = true;
      cuiBtn.textContent = "Se verifică…";
      cuiInfo.textContent = "";
      try {
        const r = await api.get(`/public/verifica-cui/${encodeURIComponent(val)}`);
        if (r && r.cui_invalid) {
          cuiInfo.textContent = r.motiv;   // [459] CUI-ul greșit, înainte de ANAF (nu „Nu apare la ANAF”)
          cuiInfo.style.color = "#a32d2d";
        } else if (!r || !r.gasit) {
          cuiInfo.textContent = "Nu apare la ANAF prin acest CUI (posibil înregistrat ca PFI, direct la ANAF, fără ONRC). Completează denumirea manual mai jos.";
          cuiInfo.style.color = "#92500a";
        } else {
          anaf.pune([r.denumire], { suprascrie: true });   // „Verifică la ANAF” e cerut de om: denumirea ANAF intră și peste ce era scris
          if (r.cod_caen && r.cod_caen !== "6920") {
            cuiInfo.textContent = `Găsit: ${r.denumire}. Atenție — CAEN ${r.cod_caen}, nu 6920 (contabilitate).`;
            cuiInfo.style.color = "#92500a";
          } else {
            cuiInfo.textContent = `Găsit: ${r.denumire}${r.cod_caen ? " · CAEN " + r.cod_caen : ""}.`;
            cuiInfo.style.color = "#16a34a";
          }
        }
      } catch {
        cuiInfo.textContent = "Nu s-a putut verifica automat la ANAF acum. Poți continua, completează datele manual mai jos.";
        cuiInfo.style.color = "#616161";
      }
      cuiBtn.disabled = false;
      cuiBtn.textContent = "Verifică la ANAF";
    });

    function arataEroare(text) {
      eroare.textContent = text;
      eroare.hidden = false;
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
      if (liber && !tokenRobot) {
        arataEroare("Așteaptă bifa verde din caseta de verificare anti-roboți de deasupra butonului, apoi apasă din nou „Creează cont”.");
        return;
      }
      buton.disabled = true;
      buton.textContent = "Se creează…";
      // [269] numele administratorului se trimite așa cum l-a scris omul — nu se mai împarte („Test 253” dădea prenumele „253”)
      const nume = ((numeAdmin && numeAdmin.value) || "").trim() || null;
      try {
        /* [lotul 12, 642] contul și firma proprie (din CUI) se creează împreună sau deloc (`uc_auth._firma_proprie`): un refuz al
           firmei e refuzul contului (mai jos, în `catch`), deci nu mai există „cont creat, firma lipsă” */
        const _reg = await api.post("/auth/register", {
            email: email.value.trim(),
            parola: parola.value,
            nume_cabinet: cabinet.value.trim(),
            cui: (cui.value || "").trim(),  /* register_primul_tenant_v1 */
            nume,
            prenume: null,
            accept_termeni: !!modal.querySelector("#reg-termeni")?.checked,  /* [termeni_v1] */
            invitatie: liber ? null : INVITATIE,  /* [14.10.2026] invitația; [15.10.2026] sau înregistrarea liberă */
            turnstile: liber ? tokenRobot : null,   /* [257] tokenul Cloudflare Turnstile, validat pe server */
            telefon: (modal.querySelector("#reg-telefon").value || "").trim() || null,   /* [17.10.2026, lotul 7] opțional */
        });
        ciorna.sterge();   // [267] contul (sau cererea lui) s-a creat: ciorna nu mai are rost
        if (_reg && _reg.confirmare_trimisa) { randeazaVerificaEmail(_reg.email, _reg.valabila_ore); return; }
        history.replaceState(null, "", location.pathname);   // invitația s-a consumat: linkul nu mai rămâne în bară
        const r = await api.post("/auth/login", {
          email: email.value.trim(),
          parola: parola.value,
        });
        sesiune.intra(r.token, r.user);
      } catch (e) {
        // [lotul 12, deficiența 642 — comanda Costin 12.2 pct.19: „mesajul de refuz apare de două ori”] refuzul serverului, O DATĂ:
        // erorile de câmp lângă câmpurile lor (`arataRefuzul`, și în caseta „NU s-a salvat.” de lângă buton, api.js 410/440), iar în zona
        // de lângă „Creează cont” numai refuzul fără câmp; verdictul „Verifică la ANAF” cu același text pleacă (refuzul îl spune acum)
        if (cuiInfo.textContent.trim() && String((e && e.mesaj) || "").includes(cuiInfo.textContent.trim())) cuiInfo.textContent = "";
        const ec = (e && e.erori_campuri) || [];
        arataRefuzul(modal, e, null);
        const nepuse = ec.filter((c) => !modal.querySelector("#" + CSS.escape(String(c.camp || "")))).map((c) => c.mesaj);
        if (!ec.length) arataEroare((e && e.mesaj) || "Nu s-a putut crea contul.");
        else if (nepuse.length) arataEroare(nepuse.join("\n"));
        buton.disabled = false;
        buton.textContent = "Creează cont";
        if (widgetRobot !== null) { tokenRobot = null; window.turnstile.reset(widgetRobot); }   // [257] tokenul s-a consumat
      }
    }
    buton.addEventListener("click", creeaza);
  }
}

// [257] Scriptul Cloudflare Turnstile se încarcă o singură dată, la cerere, numai pe formularul liber
// (CSP: `script-src` și `frame-src` https://challenges.cloudflare.com — config/nginx-iconta).
let _turnstile = null;
function incarcaTurnstile(src) {
  if (!_turnstile) {
    _turnstile = new Promise((gata, esec) => {
      const s = document.createElement("script");
      s.src = src;
      s.async = true;
      s.onload = () => (window.turnstile ? gata(window.turnstile) : esec(new Error("turnstile")));
      s.onerror = () => { _turnstile = null; esec(new Error("turnstile")); };
      document.head.appendChild(s);
    });
  }
  return _turnstile;
}

// landing_diacritice_v1

// landing_texte_v3

// landing_carduri_v2

// login_form_v1


// [F203] Pagina Functionalitati (client-side; replica VIZUALA a modalului DS - nav.deschide e shell autentificat, indisponibil pre-login)
// <DECLARATII_AUTO> generat de genereaza_declaratii_lista.py --scrie; NU edita manual intre ancore
const DECLARATII_50 = [{"tip": "D100", "per": "trimestrial", "ce_e": "Declarație privind obligațiile de plată la bugetul de stat"}, {"tip": "D101", "per": "anual", "ce_e": "Declarație privind impozitul pe profit"}, {"tip": "D101G", "per": "anual", "ce_e": "Declarație CONSOLIDATĂ privind impozitul pe profit determinat de GRUPUL FISCAL"}, {"tip": "D104", "per": "trimestrial", "ce_e": "Declarație privind distribuirea între asociați a veniturilor și cheltuielilor"}, {"tip": "D106", "per": "anual", "ce_e": "Declarație informativă privind dividendele cuvenite acționarilor"}, {"tip": "D107", "per": "anual", "ce_e": "Declarație informativă privind beneficiarii sponsorizărilor / mecenatului / burselor private"}, {"tip": "D108", "per": "anual", "ce_e": "Declarație privind impozitul pe reprezentanță"}, {"tip": "D110", "per": "lunar", "ce_e": "Declarație de regularizare / cerere de restituire privind impozitul pe venit reținut la sursă"}, {"tip": "D112", "per": "lunar", "ce_e": "Declarație privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate"}, {"tip": "D114", "per": "lunar", "ce_e": "Declarație privind obligațiile de plată a contribuției asiguratorii pentru muncă"}, {"tip": "D119", "per": "lunar", "ce_e": "Declarație specială privind obligațiile de plată la bugetul de stat"}, {"tip": "D120", "per": "anual", "ce_e": "Decont privind accizele"}, {"tip": "D130", "per": "anual", "ce_e": "Decont privind impozitul la țițeiul din producția internă"}, {"tip": "D169", "per": "anual", "ce_e": "Declarație de înregistrare a contractelor de fiducie sau a construcțiilor juridice similare fiduciei"}, {"tip": "D169N", "per": "anual", "ce_e": "Declarație privind neconcordanțele dintre informațiile privind beneficiarii reali"}, {"tip": "D177", "per": "anual", "ce_e": "Cerere privind redirecționarea impozitului pe profit către entități nonprofit"}, {"tip": "D204", "per": "anual", "ce_e": "Declarație anuală de venit pentru asocieri fără personalitate juridică"}, {"tip": "D205", "per": "anual", "ce_e": "Declarație informativă privind impozitul reținut la sursă și câștigurile/pierderile din investiții, pe beneficiari de venit"}, {"tip": "D207", "per": "anual", "ce_e": "Declarație informativă privind impozitul reținut la sursă pe beneficiari nerezidenți"}, {"tip": "D208", "per": "lunar", "ce_e": "Declarație informativă privind impozitul pe veniturile din transferul proprietăților imobiliare din patrimoniul personal"}, {"tip": "D212", "per": "anual", "ce_e": "Declarația unică privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice"}, {"tip": "D213", "per": "anual", "ce_e": "Declarație privind veniturile realizate de persoana fizică și/sau asocierea fără personalitate juridică"}, {"tip": "D214", "per": "anual", "ce_e": "Cerere pentru stabilirea impozitului pe venitul din înstrăinarea de terenuri agricole"}, {"tip": "D216", "per": "anual", "ce_e": "Declarație privind impozitul special pe bunurile imobile și mobile de valoare mare"}, {"tip": "D230", "per": "anual", "ce_e": "Cerere privind destinația sumei de până la 3,5% din impozitul anual (redirecționare ONG)"}, {"tip": "D300", "per": "lunar", "ce_e": "Decont de TVA"}, {"tip": "D301", "per": "lunar", "ce_e": "Decont special de TVA"}, {"tip": "D307", "per": "lunar", "ce_e": "Declarație privind sumele rezultate din ajustarea/corecția ajustărilor/regularizarea TVA"}, {"tip": "D311", "per": "lunar", "ce_e": "TVA datorată de persoane impozabile al căror cod de TVA a fost anulat"}, {"tip": "D318", "per": "anual", "ce_e": "Cerere de rambursare a TVA pentru persoane impozabile stabilite în România, depusă în alt stat membru"}, {"tip": "D390", "per": "lunar", "ce_e": "Declarație recapitulativă VIES privind livrările/achizițiile/prestările intracomunitare"}, {"tip": "D393", "per": "anual", "ce_e": "Declarație informativă privind biletele de călătorie pentru transportul rutier de persoane"}, {"tip": "D394", "per": "lunar", "ce_e": "Declarație informativă privind livrările/prestările și achizițiile efectuate pe teritoriul național"}, {"tip": "D395", "per": "lunar", "ce_e": "Declarație informativă privind trimiterile poștale contra ramburs"}, {"tip": "D397", "per": "lunar", "ce_e": "Declarație informativă privind activitățile de transport alternativ cu autoturism și conducător auto"}, {"tip": "D398", "per": "trimestrial", "ce_e": "Declarație specială de TVA pentru regimurile speciale UE / non-UE / import (OSS)"}, {"tip": "D399", "per": "trimestrial", "ce_e": "Declarație specială de TVA pentru regimul special de import (IOSS)"}, {"tip": "D401", "per": "anual", "ce_e": "Declarație informativă privind proprietățile imobiliare deținute de rezidenți ai altor state membre UE"}, {"tip": "D402", "per": "anual", "ce_e": "Declarație informativă privind veniturile de natură salarială plătite de intermediari"}, {"tip": "D403", "per": "anual", "ce_e": "Declarație informativă privind produsele de asigurare de viață contractate de rezidenți ai altor state membre UE"}, {"tip": "D406", "per": "lunar", "ce_e": "Fișierul Standard de Control Fiscal (SAF-T) pentru România"}, {"tip": "D407", "per": "semestrial", "ce_e": "Declarație informativă privind persoanele și sumele/produsele declarate de intermediari"}, {"tip": "D603", "per": "anual", "ce_e": "Declarație pe propria răspundere pentru exceptarea de la plata contribuției de asigurări sociale de sănătate"}, {"tip": "D710", "per": "trimestrial", "ce_e": "Declarație rectificativă"}];
// </DECLARATII_AUTO>
// <GRUPE_FUNC_AUTO> generat de genereaza_grupe_functii.py --scrie; NU edita manual intre ancore (gardat de GRUPE_FUNC_STALE)
const GRUPE_FUNC = [{"titlu": "Contabilitate", "icon": "brief", "functii": ["Asociații și cotele, cu istoricul cesiunilor, în Date firmă", "Avansuri furnizori/clienți", "Bacșiș HoReCa", "Balanța de deschidere cu soldurile inițiale ale anului și rulajele preluate", "Bilanț anual S1005/S1003", "Blocare perioade", "Cartea mare și închiderea perioadei", "Centre de cost și bugete (contabilitate de gestiune)", "Compensări de creanțe și datorii", "Contabilitate ONG", "Deconturi deplasare și diurnă", "Decontări asociați", "Editor note contabile", "Jurnal regim marjă (raport)", "Leasing financiar și operațional", "Lichidare/radiere societate", "Mijloace fixe (registrul activelor)", "Perisabilități și scăzăminte", "Producție în curs și produse finite", "Propunerea notei de închidere a exercițiului", "Provizioane și ajustări", "Rapoarte comerciale", "Rapoarte configurabile salvabile", "Reevaluare imobilizări", "Reevaluarea lunară a soldurilor în valută, propusă de aplicație", "Registru încasări/plăți (partidă simplă)", "SGR (garanție-returnare)", "Sponsorizări și credit fiscal", "Subvenții", "Încredere și învățare AI"]}, {"titlu": "Fiscalitate", "icon": "declaratii", "functii": ["Achiziție de la neînregistrat (persoană fizică)", "Calculul Declarației unice D212 (PFA/II/IF)", "Coada de validare patru-ochi", "Curs valutar BNR", "Declarația D100", "Declarația D101 și IMCA", "Declarația D104 (distribuire venituri asocieri)", "Declarația D107 (beneficiari sponsorizări/mecenat/burse)", "Declarația D110 (regularizare impozit reținut la sursă)", "Declarația D112", "Declarația D114 (contribuția asiguratorie pentru muncă - CAM)", "Declarația D177 (redirecționare impozit profit)", "Declarația D204 (asocieri fără personalitate juridică)", "Declarația D205 și distribuirea dividendelor", "Declarația D207 (impozit reținut nerezidenți)", "Declarația D208 (transfer proprietăți imobiliare - notari)", "Declarația D212 (declarația unică)", "Declarația D216 (impozit special pe bunuri de valoare mare)", "Declarația D230 (redirecționare 3,5%)", "Declarația D300", "Declarația D301", "Declarația D307 (ajustare TVA)", "Declarația D311 (TVA cod anulat)", "Declarația D318 (rambursare TVA din alt stat membru UE)", "Declarația D390 (VIES)", "Declarația D394", "Declarația D398 (TVA regim special OSS - UE/non-UE)", "Declarația D406 (SAF-T)", "Declarația D603 (exceptare de la plata CASS)", "Declarația D710 (rectificativă D100)", "Diferențe de curs valutar", "Generarea declarațiilor (tip, periodicitate, formular)", "Import/export extracomunitar", "Păstrarea declarației depuse (XML și rânduri)", "Regim special agenții de turism", "Regim special agricultori", "Regim special al marjei (bunuri second-hand)", "Regim special aur de investiții", "Regimul TVA la încasare pe firmă (perioadele, verificarea ANAF, efectul pe facturi și declarații)", "Regula cotelor de TVA", "Rând manual D300", "TVA la încasare", "Taxare inversă internă", "Trimitere D390 clasificări manuale"]}, {"titlu": "Control fiscal", "icon": "shield", "functii": ["Audit de preluare a firmei", "Avertisment: regimul de TVA față de ANAF, în semaforul Control fiscal", "Calculul scadențelor", "Control încrucișat: D112 (salarii) față de contabilitate", "Control încrucișat: D390 (bunuri intracomunitare) față de evidența validată și de D300 depus", "Control încrucișat: declarația de TVA față de contabilitate", "Cota de TVA pe facturile emise, reverificată la schimbarea legii", "Notificare în aplicație pentru constatările roșii din Control fiscal", "Semafor conformare fiscală", "Tiparele de respingere ale declarațiilor", "Vector fiscal per firmă", "Verificatoare de coerență", "Verificator praguri Intrastat"]}, {"titlu": "Facturare și e-Factura", "icon": "facturi", "functii": ["Chitanțe emise", "Clasificare TVA pe factură", "Comodat, chirii, refacturări", "Conectarea la SPV (ANAF)", "Conector WooCommerce", "Cont de venit implicit, ales în Date firmă", "Contarea facturilor, cu TVA și stornare", "Export facturi emise către SAGA", "Export facturi emise către WinMENTOR", "Facturi recurente", "Factură emisă pe baza bonului fiscal", "Fișele clienților și persoana afiliată", "Import e-Factura (UBL)", "Legătură de plată pe factură", "Nomenclator produse, cu cota de TVA propusă de AI", "Notificare e-Transport", "Notificări de plată și alerte neplătnici", "Operațiuni intracomunitare", "PDF factură", "Parteneri (clienți/furnizori)", "Profilul firmei și modelul facturii", "Trimitere e-Transport direct în SPV", "Validare CUI la ANAF", "e-Factura SPV complet"]}, {"titlu": "Salarizare", "icon": "users", "functii": ["Adeverințe salariați", "Calcul salarizare (de la brut la net)", "Cod 10 CM în flux", "Coduri COR pe contracte", "Conexiunea cu registrul REGES", "Contracte de muncă speciale", "Plata salariilor pe card (fișier bancar)", "Pontaj angajați", "Salariați (adăugare, modificare, ștergere)", "Statul de plată și fluturașii", "Tichete de masă, de vacanță și cadouri în statul de plată"]}, {"titlu": "Stocuri, bancă și casă", "icon": "building", "functii": ["Analitică de stoc", "Chitanță de vânzare fără factură (activitate exceptată de la AMEF)", "Citirea extrasului bancar", "Coduri de bare în gestiune", "Contabilizare extras de cont", "Costul complet de achiziție pe NIR (transport, vamă)", "Credite bancare și garanții", "Descărcarea stocului la emiterea facturii", "Import Raport Z din AMEF", "Import articole și stoc inițial (cantitativ-valoric)", "Import extras bancar MT940 (SWIFT)", "Inventar pe mobil", "Inventariere anuală", "Obiecte de inventar", "Reconciliere bancară (potrivirea plăților cu facturile)", "Registrul de casă și plafoanele de numerar", "Rețetar HoReCa (global-valoric)", "Stocuri cantitativ-valorice (CMP)", "Stocuri global-valorice", "Transfer între gestiuni"]}, {"titlu": "Cabinet și portal client", "icon": "documente", "functii": ["Alerte legislative programate", "Aplicație instalabilă pe telefon", "Canal de sesizări (Raportează)", "Cardurile de început (primii pași) și prima intrare", "Cerere de ștergere cont din aplicație (GDPR art.17)", "Chei API publice per cabinet", "Contabilii și asistenții cabinetului", "Documente pentru portal", "Exportul datelor cabinetului, din aplicație", "Generare contracte", "Import la preluarea firmei", "Indicatorii clientului (portal)", "Intrare în portal prin legătură pe email (fără parolă)", "Notificări în aplicație și pe email", "Panoul de capacitate", "Povestea lunii (pachet lunar)", "Precompletarea datelor firmei din ANAF la adăugarea firmei", "Previziunea fluxului de numerar pe 8 săptămâni", "Previzualizare portal client din cabinet (Acces Client)", "Registratură documente", "Scadențe viitoare pe portofoliu", "Starea migrării pe straturi"]}];
// </GRUPE_FUNC_AUTO>

function _funcOverlay(inner) {
  const o = document.createElement("div");
  o.className = "fereastra-overlay func-overlay";
  o.innerHTML = inner;
  document.body.appendChild(o);
  // [dialog_inchidere 04.10.2026] X + Esc prin mecanismul unic (DS cap.9) — pagina informativă, fără câmpuri
  const inchide = inchidereDialog(o, () => o.remove(), o.querySelector(".fereastra-antet"));
  o.addEventListener("click", (e) => { if (e.target === o) inchide(); });
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
  evPublic("deschide_preturi");
  _funcOverlay(
    `<div class="fereastra"><div class="fereastra-antet"><span class="fereastra-titlu">${esc(PRETURI_TITLU)}</span>` +
    `<button class="nav-x" type="button" title="Închide" aria-label="Închide">✕</button></div>` +
    `<div class="fereastra-corp"><div class="preturi-text">${preturiHTML()}</div></div></div>`
  );
}

function deschideDeclaratii() {
  evPublic("modal_declaratii");
  const celule = DECLARATII_50.map((d) =>
    `<li class="decl-chip"><span class="decl-cod">${esc(d.tip)}</span>` +
    `<button class="ajutor-btn decl-ce" type="button" data-tip="${esc(d.tip)}" ` +
    `aria-label="Ce este ${esc(d.tip)}">?</button></li>`).join("");
  const o = _funcOverlay(
    `<div class="fereastra fer-larg"><div class="fereastra-antet">` +
    `<span class="fereastra-titlu">Toate cele ${cate(DECLARATII_50.length, "declarație", "declarații")}</span>` +
    `<button class="nav-x" type="button" title="Închide" aria-label="Închide">✕</button></div>` +
    `<div class="fereastra-corp">` +
    `<ul class="decl-grila">${celule}</ul>` +
    `<div class="decl-explicatie" aria-live="polite">` +
    `Apasă <b>?</b> lângă o declarație ca să vezi ce este.</div>` +
    `</div></div>`
  );
  const zona = o.querySelector(".decl-explicatie");
  o.querySelectorAll(".decl-ce").forEach((b) => b.addEventListener("click", () => {
    const d = DECLARATII_50.find((x) => x.tip === b.dataset.tip);
    if (!d) return;
    o.querySelectorAll(".decl-chip").forEach((c) => c.classList.remove("decl-chip-activ"));
    b.closest(".decl-chip").classList.add("decl-chip-activ");
    zona.innerHTML = `<b>${esc(d.tip)}</b> — ${esc(d.ce_e)} <span class="decl-per">(${esc(d.per)})</span>`;
  }));
}

function deschideFunctionalitati() {
  evPublic("modal_functionalitati");
  // [preturi_v1] cardul Preturi = PRIMUL, scris de mana (in afara zonei auto GRUPE_FUNC); nu se sterge la --scrie
  const cardPreturi =
    `<button class="func-card func-card-preturi" type="button" data-preturi="1"><span class="func-card-icon">${svgIcon(ICOANE.gauge, 26)}</span>` +
    `<span class="func-card-titlu">${esc(PRETURI_TITLU)}</span></button>`;
  // [decl50_v1] cardul „Toate declarațiile" — scris de mana, in afara zonei auto GRUPE_FUNC.
  // Numarul NU e scris aici: vine din lista derivata, ca sa nu poata ramane in urma.
  const cardDecl =
    `<button class="func-card func-card-decl" type="button" data-decl="1"><span class="func-card-icon">${svgIcon(ICOANE.declaratii, 26)}</span>` +
    `<span class="func-card-titlu">Toate declarațiile</span><span class="func-card-nr">${cate(DECLARATII_50.length, "tip", "tipuri")}</span></button>`;
  const carduri = cardPreturi + cardDecl + GRUPE_FUNC.map((gr, i) =>
    `<button class="func-card" type="button" data-i="${i}"><span class="func-card-icon">${svgIcon(ICOANE[gr.icon], 26)}</span>` +
    `<span class="func-card-titlu">${esc(gr.titlu)}</span><span class="func-card-nr">${cate(gr.functii.length, "funcție", "funcții")}</span></button>`
  ).join("");
  const o = _funcOverlay(
    `<div class="fereastra fer-larg"><div class="fereastra-antet"><span class="fereastra-titlu">Funcționalități și prețuri</span>` +
    `<button class="nav-x" type="button" title="Închide" aria-label="Închide">✕</button></div>` +
    `<div class="fereastra-corp"><div class="func-grila">${carduri}</div></div></div>`
  );
  o.querySelector(".func-card-preturi").addEventListener("click", deschideFereastraPreturi);
  o.querySelector(".func-card-decl").addEventListener("click", deschideDeclaratii);
  o.querySelectorAll(".func-card:not(.func-card-preturi)").forEach((b) =>
    b.addEventListener("click", () => deschideFereastraGrupa(GRUPE_FUNC[+b.dataset.i])));
}
