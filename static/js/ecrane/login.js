// login.js — poarta de intrare.
// Bara sus: logo + buton "Acces". Acces deschide central un modal umbrit
// cu 2 optiuni: Intra in cont (login existent) / Client nou (inregistrare cabinet).
import { api, arataMesaj, CULORI_CARD } from "../api.js";
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
  { titlu: "Fara costuri ascunse", sub: "plati transparente", icon: ICONI.moneda },
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
      <span class="pagina-bara-marca">iConta</span>
    </div>
    <button class="pagina-bara-acces" id="pagina-acces-btn">Acces</button>
  `;
  radacina.appendChild(bara);

  const corp = document.createElement("div");
  corp.className = "pagina-corp";
  corp.innerHTML = `
    <div class="pagina-hero">
      <h1 class="pagina-hero-titlu">Un singur sistem.<br>Toate procesele.</h1>
      <p class="pagina-hero-sub">\u00cencarci documentele. iConta le prelucreaz\u0103, propune contarea \u0219i verific\u0103 automat obliga\u021biile fiscale.</p>
    </div>
    <div class="pagina-carduri-sectiune">
      <div class="pagina-carduri-wrap">
        <div class="pagina-card-mare" style="background:#fdeef2">
          <div class="pagina-card-mare-icon accent-magenta">${svgIcon(ICONI.factura, 30)}</div>
          <div class="pagina-card-mare-titlu">Facturare gratuit\u0103</div>
          <div class="pagina-card-mare-sub">Facturi, proforme, recurente \u0219i import din magazinul online \u2014 direct din platform\u0103.</div>
          <button type="button" class="pagina-card-buton" id="pagina-facturare-gratuita-btn">Acces</button>
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
  const facturareBtn = document.querySelector("#pagina-facturare-gratuita-btn");
  if (facturareBtn) facturareBtn.addEventListener("click", () => {
    overlay.hidden = false;
    randeazaInregistrare();
  });

  const modal = overlay.querySelector("#acces-modal");

  // ---------- ecran 1: alege Intra in cont / Client nou ----------
  function randeazaAlegere() {
    modal.classList.remove("acces-modal-inreg");
    modal.innerHTML = `
      <button class="acces-x" id="acces-x" aria-label="Închide">✕</button>
      <div class="login-brand">
        <img class="login-logo-img" src="/static/logo_login.png" alt="iConta">
        <span class="login-tagline">Contabilitatea cu control fiscal</span>
      </div>
      <div class="acces-alegere">
        <button class="acces-card" id="acces-intra">
          <div class="acces-card-icon" style="background:#e9f0fe;color:#1d4ed8">
            <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><path d="M10 17l5-5-5-5"/><path d="M15 12H3"/></svg>
          </div>
          <div class="acces-card-text">
            <div class="acces-card-titlu">Intră în cont</div>
            <div class="acces-card-sub">Ai deja un cont iConta</div>
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
    modal.querySelector("#acces-client-nou").addEventListener("click", randeazaInregistrare);
  }

  // ---------- ecran 2a: login (doua cai explicite) ----------  // ux_login_camera_v1
  function randeazaLogin() {
    modal.classList.remove("acces-modal-inreg");
    modal.innerHTML = `
      <button type="button" class="nav-sageata" id="login-la-alegere" title="Înapoi" aria-label="Înapoi" style="position:absolute;top:14px;left:14px"><span aria-hidden="true">←</span></button>
      <button class="acces-x" id="acces-x" aria-label="Închide">✕</button>
      <div class="login-brand">
        <img class="login-logo-img" src="/static/logo_login.png" alt="iConta">
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
        <img class="login-logo-img" src="/static/logo_login.png" alt="iConta">
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

  function formCabinet() {
    modal.innerHTML = `
      <button type="button" class="nav-sageata" id="login-inapoi" title="Înapoi" aria-label="Înapoi" style="position:absolute;top:14px;left:14px"><span aria-hidden="true">←</span></button>
      <button class="acces-x" id="acces-x" aria-label="Închide">✕</button>
      <div class="login-brand">
        <img class="login-logo-img" src="/static/logo_login.png" alt="iConta">
        <span class="login-tagline">Contabilitatea cu control fiscal</span>
      </div>
      <form id="login-form" onsubmit="return false">
      <label class="camp">
        <span class="camp-eticheta">Email</span>
        <input type="email" name="email" class="camp-input" id="login-email" autocomplete="username" autofocus>
      </label>
      <label class="camp">
        <span class="camp-eticheta">Parolă</span>
        <input type="password" class="camp-input" name="password" id="login-parola" autocomplete="current-password">
      </label>
      <div class="login-eroare" id="login-eroare" hidden></div>
      <button type="submit" class="buton-primar" id="login-buton">Autentificare</button>
      <button type="button" class="btn-link" id="acc-magic" style="margin-top:10px;display:block">Trimite-mi link de logare (fără parolă)</button>
      <p id="acc-magic-msg" style="margin:6px 0 0"></p>
      </form>
    `;
    modal.querySelector("#acces-x").addEventListener("click", inchideOverlay);
    modal.querySelector("#login-inapoi").addEventListener("click", randeazaLogin);

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
  function randeazaInregistrare() {
    modal.classList.add("acces-modal-inreg");
    modal.innerHTML = `
      <button class="acces-x" id="acces-x" aria-label="Închide">✕</button>
      <div class="login-brand">
        <img class="login-logo-img" src="/static/logo_login.png" alt="iConta">
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
        <span class="camp-eticheta">Denumire cabinet de contabilitate/contabil</span>
        <input type="text" class="camp-input" id="reg-cabinet">
      </label>
      <label class="camp">
        <span class="camp-eticheta">Nume administrator</span>
        <input type="text" class="camp-input" id="reg-nume-admin">
      </label>
      <label class="camp">
        <span class="camp-eticheta">Email</span>
        <input type="email" class="camp-input" id="reg-email" autocomplete="off" placeholder="nume@firma.ro">
      </label>
      <label class="camp">
        <span class="camp-eticheta">Parolă</span>
        <input type="password" class="camp-input" id="reg-parola" autocomplete="off">
      </label>
      <label class="camp">
        <span class="camp-eticheta">Confirmă parola</span>
        <input type="password" class="camp-input" id="reg-parola2" autocomplete="off">
      </label>
      <div class="login-eroare" id="reg-eroare" hidden></div>
      <button class="buton-primar" id="reg-buton">Creează cont</button>
    `;
    modal.querySelector("#acces-x").addEventListener("click", inchideOverlay);

    const cui = modal.querySelector("#reg-cui");
    const cuiBtn = modal.querySelector("#reg-cui-verifica");
    const cuiInfo = modal.querySelector("#reg-cui-info");
    const cabinet = modal.querySelector("#reg-cabinet");
    const numeAdmin = modal.querySelector("#reg-nume-admin");
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
      buton.disabled = true;
      buton.textContent = "Se creează…";
      const { nume, prenume } = separaNume(numeAdmin.value || "");
      try {
        await api.post("/auth/register", {
          email: email.value.trim(),
          parola: parola.value,
          nume_cabinet: cabinet.value.trim(),
          cui: (cui.value || "").trim(),  /* register_primul_tenant_v1 */
          nume,
          prenume,
        });
        const r = await api.post("/auth/login", {
          email: email.value.trim(),
          parola: parola.value,
        });
        sesiune.intra(r.token, r.user);
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
