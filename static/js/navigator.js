// navigator.js — managerul de ferestre (inima shell-ului).
//
// DESKTOP rolului:
//   bara albastră sus: logo + iConta + context rol + user + IEȘIRE (portocaliu, dreapta)
//   bara albastru-gri dedesubt (cabinet/asistent): firma în lucru
//   client: doar bara albastră (o singură firmă)
// FEREASTRĂ de lucru (modală, centrală peste overlay umbrit):
//   ← stânga-sus -> UN PAS ÎNAPOI pe traseul parcurs (apare doar când există drum);
//   X dreapta-sus -> ÎNCHIDE fereastra (acasă). Traseul e memorat de navigator (nav.mergi).

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
    _anunturiBanner(ecran);  /* anunturi_fe_v1 */
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
    const areInapoi = stiva.length > 1 || typeof sus.inapoi === "function" || (sus.pasi && sus.pasi.length > 0);  // traseu_automat_v1
    // breadcrumb_v1: drumul (breadcrumb) din traseul real — ferestre + pasi + curent
    const drum = [];
    for (let i = 0; i < stiva.length - 1; i++) drum.push({ text: stiva[i].titlu || "…", fereastra: i });
    (sus.pasi || []).forEach((p, i) => { if (p.titlu) drum.push({ text: p.titlu, pas: i }); });
    const drumHtml = drum.map((d, i) =>
      `<button class="fir-veriga" data-fer="${d.fereastra ?? ''}" data-pas="${d.pas ?? ''}">${String(d.text).replace(/[<>&]/g, "")}</button>` +
      (i < drum.length - 1 ? `<span class="fir-sep" aria-hidden="true">›</span>` : "")
    ).join("");  // fir_doar_parinti_v1: doar parintii; pasul curent = titlul din corp
    fer.innerHTML = `
      <div class="fereastra-antet">
        <button class="nav-sageata nav-inapoi" title="Înapoi" aria-label="Înapoi" ${areInapoi ? '' : 'style="display:none"'}><span aria-hidden="true">←</span></button>
        <span class="fereastra-fir">${drumHtml}</span>
        <span class="fereastra-spatiu"></span>
        <button class="nav-x" title="Închide" aria-label="Închide"><span aria-hidden="true">✕</span></button>
      </div>
      <div class="fereastra-corp"></div>
    `;
    fer.querySelectorAll(".fir-veriga").forEach((b) => b.addEventListener("click", () => {
      if (b.dataset.fer !== "") {  // sari la o fereastra de dedesubt
        stiva.length = Number(b.dataset.fer) + 1;
        randeazaFerestre();
        return;
      }
      const idx = Number(b.dataset.pas);  // sari la un pas de pe traseu
      const p = sus.pasi[idx];
      sus.pasi.length = idx;
      sus.curent = p.randator;
      sus.titluCurent = p.titlu || "";
      sus.inapoi = null;
      randeazaFerestre();
    }));
    const bInapoi = fer.querySelector(".nav-inapoi");
    if (bInapoi) {
      bInapoi.addEventListener("click", () => {  // traseu_automat_v1
        if (typeof sus.inapoi === "function") { sus.inapoi(); return; }
        if (sus.pasi && sus.pasi.length) {
          const p = sus.pasi.pop();
          sus.curent = p.randator;
          sus.titluCurent = p.titlu || "";  // breadcrumb_v1
          sus.scrollY = p.scrollY || 0;
          randeazaFerestre();
          return;
        }
        nav.inapoi();
      });
    }
    fer.querySelector(".nav-x").addEventListener("click", () => nav.acasa());
    overlay.appendChild(fer);
    radacina.appendChild(overlay);
    fer.classList.toggle("fer-larg", (sus.optiuni || {}).lat === "larg");
    (sus.curent || sus.randator)(fer.querySelector(".fereastra-corp"), nav);  // traseu_automat_v1
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
      {  // cap9_titlu_v11: titlul ecranului = DOAR titlul; entitatea traieste in bara mare de sus, nu se dubleaza aici
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
      stiva.push({ titlu, randator, curent: randator, pasi: [], optiuni: optiuni || {} }); randeazaFerestre(); }, /* fereastra_optiuni_v1 + traseu_automat_v1 */
    inapoi() { stiva.pop(); randeazaFerestre(); },
    inapoiPas() {  // faza_b_traseu_v1: un pas inapoi pe traseu, programatic (dupa o actiune reusita)
      if (!stiva.length) return;
      const sus = stiva[stiva.length - 1];
      if (sus.pasi && sus.pasi.length) {
        const p = sus.pasi.pop();
        sus.curent = p.randator;
        sus.titluCurent = p.titlu || "";
        sus.scrollY = p.scrollY || 0;
        randeazaFerestre();
      } else nav.inapoi();
    },
    mergi(titlu, fn) {  // traseu_automat_v1 + breadcrumb_v1: pas cu titlu pe traseu
      if (!stiva.length) return;
      if (typeof titlu === "function") { fn = titlu; titlu = ""; }  // compat: mergi(fn)
      const sus = stiva[stiva.length - 1];
      const c = document.querySelector(".fereastra-corp");
      sus.pasi.push({ randator: sus.curent || sus.randator, scrollY: c ? c.scrollTop : 0,
                      titlu: sus.titluCurent || sus.titlu || "" });
      sus.curent = fn;
      sus.titluCurent = titlu || "";
      sus.inapoi = null;
      sus.scrollY = 0;
      randeazaFerestre();
    },
    setInapoi(fn) {  // sageata_dinamica_v1
      if (!stiva.length) return;
      stiva[stiva.length - 1].inapoi = fn;
      const b = radacina.querySelector(".nav-inapoi");
      const sus2 = stiva[stiva.length - 1];
      if (b) b.style.display = (typeof fn === "function" || stiva.length > 1 || (sus2.pasi && sus2.pasi.length > 0)) ? "" : "none";  // traseu_automat_v1
    },
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
  try {  // generalizare_zi_v1: notificarile sunt de cabinet; pe client nu interogam (evita 403)
    const { sesiune } = await import("./sesiune.js");
    if (((sesiune.user() || {}).rol) === "client") {
      badge.style.display = "none";
      const btn = (container || document).querySelector("#nav-clopot");
      if (btn) btn.style.display = "none";
      return;
    }
  } catch {}
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


// anunturi_fe_v1: bannere anunturi de la Admin iConta, cu confirmare
async function _anunturiBanner(ecran) {
  const u = sesiune.user() || {};
  if (u.rol === "client" || u.rol === "superadmin") return;
  let d;
  try {
    const { api } = await import("./api.js");
    d = await api.get("/eu/anunturi");
  } catch { return; }
  const lista = (d && d.anunturi) || [];
  if (!lista.length) return;
  const cont = ecran.querySelector(".desktop-continut");
  if (!cont) return;
  lista.forEach((a) => {  /* anunt_modal_v2: modal central */
    const el = document.createElement("div");
    el.className = "fereastra-overlay";
    el.style.zIndex = "300";
    el.innerHTML = `<div class="fereastra" style="max-width:520px">
      <div class="fereastra-corp">
        <h2 class="pf-titlu">Mesaj de la iConta</h2>
        <p class="anunt-text">${(a.mesaj || "").replace(/[<>&]/g, "")}</p>
        <button class="buton-primar anunt-ok">Am \u00een\u021beles</button>
      </div></div>`;
    el.querySelector(".anunt-ok").addEventListener("click", async () => {
      try {
        const { api } = await import("./api.js");
        await api.post(`/eu/anunturi/${a.id}/confirma`, {});
        el.remove();
      } catch {}
    });
    document.body.appendChild(el);
  });
}
// sageata_dinamica_v1

// traseu_automat_v1

// breadcrumb_v1

// faza_b_traseu_v1

// provenienta_v1

// uniformizare_fir_v1

// fir_doar_parinti_v1
