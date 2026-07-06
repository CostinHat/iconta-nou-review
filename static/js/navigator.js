// navigator.js — managerul de ferestre (inima shell-ului).
//
// DESKTOP rolului:
//   bara albastră sus: logo + iConta + context rol + user + IEȘIRE (portocaliu, dreapta)
//   bara albastru-gri dedesubt (cabinet/asistent): firma în lucru
//   client: doar bara albastră (o singură firmă)
// FEREASTRĂ de lucru (modală, centrală peste overlay umbrit):
//   ← portocaliu stânga-sus -> ACASĂ (golește stiva); X dreapta-sus -> ÎNAPOI un pas

import { sesiune } from "./sesiune.js";

// [p21_bara_lant] contextul barei 1 ca LANT, citit din sesiune.user() (sursa unica)
function _functieAsistent(u) {
  return u.poate_valida ? "Asistent senior" : "Asistent junior";
}
function contextBara(u) {
  switch (u.rol) {
    case "client":  // [p90_client_bara] cabinet (slab) + firma clientului
      return { verigi: [
        { text: "Cabinet de contabilitate · " + (u.nume_firma || ""), slab: true },
        { text: u.nume_tenant || u.nume || "" },
      ] };
    case "angajat": {
      const nume = [u.nume, u.prenume].filter(Boolean).join(" ") || u.email || "";
      return { verigi: [  // [p23_bara_fix]
        { text: "Cabinet de contabilitate · " + (u.nume_firma || ""), slab: true },
        { text: nume },
        { text: _functieAsistent(u), slab: true },
      ] };
    }
    case "superadmin": // [p37_admin_desktop]
      return { verigi: [ { text: "Admin iConta" } ] };
    default:
      return { verigi: [
        { text: "Cabinet de contabilitate · " + (u.nume_firma || "") },
      ] };
  }
}

export function creeazaNavigator(radacina, desktopRandator) {
  const stiva = [];        // ferestre deschise
  let firmaInLucru = null; // numele firmei-client procesate (bara de jos)

  function randeazaDesktop() {
    radacina.innerHTML = "";
    const u = sesiune.user() || {};
    const ctx = contextBara(u);
    const areBaraJos = u.rol !== "client";

    const ecran = document.createElement("div");
    ecran.className = "desktop";

    // --- bara albastră ---
    const bara = document.createElement("header");
    bara.className = "bara";
    bara.innerHTML = `
      <img class="bara-logo-img" src="/static/logo_simbol.png" alt="">
      <span class="bara-marca">iConta</span>
      ${ctx.verigi.map((v) => `<span class="bara-chevron" aria-hidden="true">\u203a</span>` +
        `<span class="${v.slab ? "bara-veriga-slab" : "bara-veriga"}">${v.text}</span>`).join("")}
      <span class="bara-spatiu"></span>
      <button class="nav-clopot" id="nav-clopot" title="Notificari" aria-label="Notificari"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></svg><span class="nav-clopot-badge" id="nav-clopot-badge"></span></button>
      <button class="nav-iesire" id="nav-iesire" title="Ieși din cont" aria-label="Ieși din cont"><span aria-hidden="true">←</span></button>
    `;
    bara.querySelector("#nav-iesire").addEventListener("click", () => sesiune.iesi());
    ecran.appendChild(bara);
    // [p58_clopot] clopotel notificari -- dupa append, ca badge-ul sa fie in DOM  // [p65_clopot_dom]
    _clopotInit(bara, ecran);
    _sumarLogin(ecran);  // [p64_sumar_toast]

    // --- bara albastru-gri (firma în lucru) ---
    if (areBaraJos) {
      const subbara = document.createElement("div");
      subbara.className = "subbara";
      const icon = `<svg class="subbara-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 21h18"/><path d="M5 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16"/><path d="M19 21V11a2 2 0 0 0-2-2h-2"/><path d="M9 7h2M9 11h2M9 15h2"/></svg>`;
      // ICRD_SUBBARA_ADMIN_SUMAR_V1
      if (u.rol === "superadmin") {
        subbara.classList.add("subbara--admin");
        subbara.innerHTML = `${icon}<span class="subbara-gol">Se încarcă centralizatorul...</span>`;
        import("./api.js").then(({ api }) => api.get("/admin/activitate/cabinete")).then((r) => {
          const cabinete = (r && r.cabinete) || [];
          const active = cabinete.filter((c) => c.activ).length;
          const firme = cabinete.reduce((s2, c) => s2 + (c.nr_firme || 0), 0);
          const angajati = cabinete.reduce((s2, c) => s2 + (c.nr_angajati || 0), 0);
          const facturi = cabinete.reduce((s2, c) => s2 + (c.nr_facturi || 0), 0);
          const declaratii = cabinete.reduce((s2, c) => s2 + (c.nr_declaratii || 0), 0);
          const recomandari = cabinete.reduce((s2, c) => s2 + (c.nr_recomandari || 0), 0);
          subbara.innerHTML = `${icon}<span class="subbara-admin-sumar">${active} cabinete active · ${firme} firme · ${angajati} angajați · ${facturi} facturi emise · ${declaratii} declarații depuse · ${recomandari} recomandări</span>`;
        }).catch(() => {
          subbara.innerHTML = `${icon}<span class="subbara-gol">Centralizatorul nu a putut fi încărcat.</span>`;
        });
      } else {
        subbara.innerHTML = firmaInLucru
          ? `${icon}<span class="subbara-cheie">În lucru:</span><span class="subbara-firma">${firmaInLucru}</span>`
          : `${icon}<span class="subbara-gol">Firmă activă: Nicio firmă selectată</span>`;
      }
      ecran.appendChild(subbara);
    }
    // [p25_bara3] bara 3 motivationala — doar asistent (angajat)
    if (u.rol === "angajat") {
      const bara3 = document.createElement("div");
      bara3.className = "bara3";
      bara3.innerHTML = `<span class="bara3-gol">se incarca realizarile tale...</span>`;
      ecran.appendChild(bara3);
      import("./api.js").then(({ api }) => api.get("/eu/calitate")).then((cal) => {
        if (!cal || !cal.ok) { bara3.innerHTML = ""; return; }
        const evaluate = cal.evaluate || 0;
        const proc = evaluate ? Math.round((cal.aprobate || 0) * 100 / evaluate) : 100;
        // [p26_motivationale] iteram peste lista din backend - oricate, flexibil
        const lista = cal.motivationale || [];
        if (!lista.length) { bara3.innerHTML = ""; return; }
        bara3.innerHTML = lista.map((m, i) =>
          (i ? `<span class="bara3-sep">·</span>` : "") +
          `<span class="bara3-item"><b>${m.valoare}</b> ${m.eticheta}</span>`
        ).join("");
      }).catch(() => { bara3.innerHTML = ""; });
    }

    const continut = document.createElement("main");
    continut.className = "desktop-continut";
    ecran.appendChild(continut);
    radacina.appendChild(ecran);

    desktopRandator(continut, nav);
    randeazaFerestre();
  }

  function randeazaFerestre() {
    radacina.querySelectorAll(".fereastra-overlay").forEach((o) => o.remove());
    if (stiva.length === 0) return;
    const sus = stiva[stiva.length - 1];

    const overlay = document.createElement("div");
    overlay.className = "fereastra-overlay";
    const fer = document.createElement("div");
    fer.className = "fereastra";
    // Sageata apare DOAR cand exista un "inapoi" real:
    //  - mai multe ferestre pe stiva, SAU
    //  - ecranul curent isi defineste o functie interna 'inapoi' (ex: migrare in cascada)
    const areInapoi = true; /* sageata mereu */
    fer.innerHTML = `
      <div class="fereastra-antet">
        ${areInapoi
          ? '<button class="nav-sageata nav-inapoi" title="Înapoi" aria-label="Înapoi"><span aria-hidden="true">←</span></button>'
          : ''}
        <span class="fereastra-spatiu"></span>
        <button class="nav-x" title="Închide" aria-label="Închide"><span aria-hidden="true">✕</span></button>
      </div>
      <div class="fereastra-corp"></div>
    `;
    const bInapoi = fer.querySelector(".nav-inapoi");
    if (bInapoi) {
      bInapoi.addEventListener("click", () => {
        if (typeof sus.inapoi === "function") sus.inapoi();
        else nav.inapoi();
      });
    }
    fer.querySelector(".nav-x").addEventListener("click", () => nav.acasa());
    overlay.appendChild(fer);
    radacina.appendChild(overlay);
    fer.classList.toggle("fer-larg", (sus.optiuni || {}).lat === "larg");
    sus.randator(fer.querySelector(".fereastra-corp"), nav);
    if (sus.scrollY) fer.querySelector(".fereastra-corp").scrollTop = sus.scrollY; /* scroll_memorat_v1 */
    /* stelute_rosii_v2: orice * din etichete devine rosu, oricand apare */
    const _corp = fer.querySelector(".fereastra-corp");
    const _steaza = () => { /* titlu_firma_v2 + titlu_global_v1 */
      if (!_corp.querySelector("h2") && sus.titlu && _corp.children.length) {
        const h = document.createElement("h2");
        h.className = "pf-titlu";
        h.textContent = sus.titlu;
        _corp.prepend(h);
      }
      if (firmaInLucru) {
        const h = _corp.querySelector("h2");
        if (h && !h.textContent.includes(firmaInLucru)) h.textContent += " \u00b7 " + firmaInLucru;
      }
      _corp.querySelectorAll("label, .camp-eticheta").forEach((l) => {
      l.childNodes.forEach((n) => {
        if (n.nodeType === 3 && n.textContent.includes("*")) {
          const span = document.createElement("span");
          span.innerHTML = n.textContent.replace(/\*/g, '<b style="color:#e11d1d">*</b>');
          n.replaceWith(span);
        }
      });
    }); };
    _steaza();
    new MutationObserver(_steaza).observe(_corp, { childList: true, subtree: true });
  }

  const nav = {
    deschide(titlu, randator, optiuni) {
      const c = document.querySelector(".fereastra-corp");
      if (c && stiva.length) stiva[stiva.length - 1].scrollY = c.scrollTop; /* scroll_memorat_v1 */
      stiva.push({ titlu, randator, optiuni: optiuni || {} }); randeazaFerestre(); }, /* fereastra_optiuni_v1 */
    inapoi() { stiva.pop(); randeazaFerestre(); },
    setInapoi(fn) { if (stiva.length) stiva[stiva.length - 1].inapoi = fn; },
    acasa() { stiva.length = 0; randeazaFerestre(); },
    // setează firma procesată (bara de jos) și re-randează desktopul
    setFirmaInLucru(nume) { firmaInLucru = nume; randeazaDesktop(); },
  };

  randeazaDesktop();
  return nav;
}


// [p58_clopot] clopotel notificari (badge + panou)
async function _clopotActualizeazaBadge(container) {  // [p66_badge_ref]
  const badge = (container || document).querySelector("#nav-clopot-badge");
  if (!badge) return;
  try {
    const { api } = await import("./api.js");
    const r = await api.get("/notificari/contor");
    const n = (r && r.necitite) || 0;
    badge.textContent = n > 0 ? (n > 9 ? "9+" : String(n)) : "";
    badge.style.display = n > 0 ? "flex" : "none";
  } catch { badge.style.display = "none"; }
}

function _clopotInit(bara, ecran) {  // [p60_clopot]
  const btn = bara.querySelector("#nav-clopot");
  if (!btn) return;
  _clopotActualizeazaBadge(bara);  // [p66_badge_ref] bara ca referinta
  btn.addEventListener("click", async (e) => {
    e.stopPropagation();
    let panou = ecran.querySelector("#nav-clopot-panou");
    if (panou) { panou.remove(); return; }
    panou = document.createElement("div");
    panou.className = "clopot-panou";
    panou.id = "nav-clopot-panou";
    panou.innerHTML = `<div class="clopot-cap"><span>Notificări</span></div><div class="clopot-lista" id="clopot-lista"><div class="clopot-gol">Se incarca…</div></div>`;
    ecran.appendChild(panou);
    const { api } = await import("./api.js");
    let date;
    try { date = await api.get("/notificari"); } catch { date = { notificari: [] }; }
    const lista = panou.querySelector("#clopot-lista");
    const items = (date.notificari || []);
    if (!items.length) {
      lista.innerHTML = `<div class="clopot-gol">Nicio notificare.</div>`;
    } else {
      lista.innerHTML = "";
      items.forEach((n) => {
        const it = document.createElement("button");
        it.className = "clopot-item" + (n.citit ? "" : " clopot-necitit");
        it.innerHTML = `<div class="clopot-text">${(n.text||"").replace(/[<>&]/g,"")}</div><div class="clopot-cand">${_clopotData(n.cand)}</div>`;
        it.addEventListener("click", () => {
          panou.remove();
          if (n.link === "validat" && window._navGlobal) { try { window._navGlobal.acasa(); } catch {} }
        });
        lista.appendChild(it);
      });
    }
    // [p60_clopot] deschiderea panoului = le-am vazut -> marcheaza toate citite + stinge badge
    try { await api.post("/notificari/citit", {}); } catch {}
    await _clopotActualizeazaBadge(bara);  // [p66_badge_ref]
    // inchide la click in afara
    setTimeout(() => {
      const off = (ev) => { if (!panou.contains(ev.target) && ev.target !== btn && !btn.contains(ev.target)) { panou.remove(); document.removeEventListener("click", off); } };
      document.addEventListener("click", off);
    }, 0);
  });
}

// [p64_sumar_toast] toast de bun-venit la login (o singura data per sesiune browser)
function _sumarTextTip(tip, n) {
  const map = {
    de_validat: n === 1 ? "1 declaratie de validat" : n + " declaratii de validat",
    aprobata: n === 1 ? "1 declaratie aprobata" : n + " declaratii aprobate",
    respinsa: n === 1 ? "1 declaratie respinsa" : n + " declaratii respinse",
    depusa: n === 1 ? "1 declaratie depusa" : n + " declaratii depuse",
  };
  return map[tip] || (n + " notificari");
}
async function _sumarLogin(ecran) {
  try {
    if (sessionStorage.getItem("iconta_sumar_aratat") === "1") return;
    const { api } = await import("./api.js");
    const r = await api.get("/notificari/sumar");
    const total = (r && r.necitite) || 0;
    sessionStorage.setItem("iconta_sumar_aratat", "1");
    if (total <= 0) return;
    const u = sesiune.user() || {};
    const nume = (u.nume || u.prenume || "").split(" ")[0] || "";
    const detalii = (r.pe_tip || []).map((x) => _sumarTextTip(x.tip, x.n)).join(", ");
    const t = document.createElement("div");
    t.className = "sumar-toast";
    t.innerHTML = `<div class="sumar-toast-cap">${nume ? "Buna, " + nume.replace(/[<>&]/g, "") + "!" : "Bine ai revenit!"}</div>` +
      `<div class="sumar-toast-corp">${detalii.replace(/[<>&]/g, "")}</div>`;
    ecran.appendChild(t);
    requestAnimationFrame(() => t.classList.add("sumar-toast-vizibil"));
    const inchide = () => { t.classList.remove("sumar-toast-vizibil"); setTimeout(() => t.remove(), 300); };
    t.addEventListener("click", inchide);
    setTimeout(inchide, 7000);
  } catch {}
}
function _clopotData(iso) {
  if (!iso) return "";
  const d = new Date(iso); if (isNaN(d)) return "";
  const azi = new Date();
  const ora = `${String(d.getHours()).padStart(2,"0")}:${String(d.getMinutes()).padStart(2,"0")}`;
  if (d.toDateString() === azi.toDateString()) return `azi ${ora}`;
  return `${d.getDate()}.${d.getMonth()+1} ${ora}`;
}
