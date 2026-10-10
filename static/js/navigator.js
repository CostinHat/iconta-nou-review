// navigator.js — managerul de ferestre (inima shell-ului).
//
// DESKTOP rolului:
//   bara albastră sus: logo + iConta + context rol + user + IEȘIRE (portocaliu, dreapta)
//   bara albastru-gri dedesubt (cabinet/asistent): firma în lucru
//   client: doar bara albastră (o singură firmă)
// FEREASTRĂ de lucru (modală, centrală peste overlay umbrit):
//   ← stânga-sus -> UN PAS ÎNAPOI pe traseul parcurs (apare doar când există drum);
//   X dreapta-sus -> ÎNCHIDE fereastra (acasă). Traseul e memorat de navigator (nav.mergi).

import { sesiune } from "./sesiune.js?v=38c3e6f6fe";
import { esc, inchidereDialog } from "./api.js?v=2561dbfd34";  // esc canonic (cap.10): strip-html data-lossy inlocuit
import { deschideAnsamblu } from "./ecrane/ansamblu.js?v=12aa9d3248";  // [bun_venit_v1] "?" general (ansamblu)
import * as _coaja from "./coaja.js?v=2776271008";  // [DS cap.25] contractul proprietar<->chirias
import * as _versiune from "./versiune.js?v=89f5446dc9";      // [R129] anunta o publicare noua, fara sa intrerupa

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
  // [deficiența 207, retestul Costin 09.10: „Pachete lunare: câmpul «Firmă» nu vine cu firma în lucru”] firma în lucru are și id-ul,
  // ca ecranele generale (Pachete lunare, Declarații) să pornească pe ea; se ține în sesiunea tabului, ca o reîncărcare să n-o piardă
  const CHEIE_FIRMA_LUCRU = "iconta_firma_in_lucru";
  let firmaInLucru = null; // numele firmei-client procesate (bara de jos)
  let firmaInLucruId = null;
  try { const v = JSON.parse(sessionStorage.getItem(CHEIE_FIRMA_LUCRU) || "null"); if (v && v.nume) { firmaInLucru = v.nume; firmaInLucruId = v.id || null; } } catch { /* sesiune fără stocare: pornește fără firmă */ }

  function randeazaDesktop() {
    radacina.innerHTML = "";
    const u = sesiune.user() || {};
    const ctx = contextBara(u);
    const areBaraJos = u.rol !== "client";

    _coaja.uitaLocurile();   // [DS cap.25] coaja se re-randeaza: locurile vechi nu mai exista
    const ecran = document.createElement("div");
    ecran.className = "desktop";

    // --- antet (banner): inveleste tot chrome-ul de sus intr-un singur <header> landmark,
    // ca subbara/bara3/toasturile sa nu mai fie continut in afara oricarui landmark (axe: region). ---
    const antet = document.createElement("header");
    antet.className = "bara-antet";
    // --- bara albastră ---
    const bara = document.createElement("div");
    bara.className = "bara";
    bara.innerHTML = `
      <img class="bara-logo-img" src="/static/logo_simbol.png" alt="">
      <span class="bara-marca">iConta.eu</span>
      ${ctx.verigi.map((v) => `<span class="bara-chevron" aria-hidden="true">\u203a</span>` +
        `<span class="${v.slab ? "bara-veriga-slab" : "bara-veriga"}">${v.text}</span>`).join("")}
      <span class="bara-spatiu"></span>
      <button class="nav-ghid" id="nav-ghid" title="Prezentarea aplicației (ansamblu)" aria-label="Prezentarea aplicației (ansamblu)"><svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="1.3"/><rect x="14" y="3" width="7" height="7" rx="1.3"/><rect x="3" y="14" width="7" height="7" rx="1.3"/><rect x="14" y="14" width="7" height="7" rx="1.3"/></svg><span class="nav-ghid-q">?</span></button>
      <button class="nav-clopot" id="nav-clopot" title="Notificări" aria-label="Notificări"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></svg><span class="nav-clopot-badge" id="nav-clopot-badge"></span></button>
      <button class="nav-iesire" id="nav-iesire" title="Ieși din cont" aria-label="Ieși din cont"><span aria-hidden="true">←</span></button>
    `;
    bara.querySelector("#nav-iesire").addEventListener("click", () => sesiune.iesi());
    bara.querySelector("#nav-ghid").addEventListener("click", deschideAnsamblu);  // [bun_venit_v1]
    antet.appendChild(bara);
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
        import("./api.js?v=2561dbfd34").then(({ api }) => api.get("/admin/activitate/cabinete")).then((r) => {
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
      antet.appendChild(subbara);
      // [DS cap.25, 21.08.2026] Proprietarul isi DECLARA locul inchiriabil. Chiriasii (ecrane) cer
      // loc prin `coaja.pune(...)`, nu si-l iau cu `document.querySelector(".subbara")`.
      _coaja.inregistreazaLoc(_coaja.LOCURI.BARA_DE_STARE, subbara);
      // [R129] Al doilea chirias al barii: daca s-a gasit deja o versiune noua, anuntul revine
      // dupa re-randarea cojii (care sterge locurile si le declara din nou).
      _versiune.aseaza();
    }
    // [p25_bara3] bara 3 motivationala — doar asistent (angajat)
    if (u.rol === "angajat") {
      const bara3 = document.createElement("div");
      bara3.className = "bara3";
      bara3.innerHTML = `<span class="bara3-gol">se încarcă realizările tale…</span>`;
      antet.appendChild(bara3);
      // [lotul 07.10 pct.4] eticheta spune „luna aceasta”: cererea o cere pe luna curentă (înainte: tot istoricul)
      const _azi = new Date(), _de = `${_azi.getFullYear()}-${String(_azi.getMonth() + 1).padStart(2, "0")}-01`;
      import("./api.js?v=2561dbfd34").then(({ api }) => api.get(`/eu/calitate?de=${_de}`)).then((cal) => {
        if (!cal || !cal.ok) { bara3.innerHTML = ""; return; }
        // [p26_motivationale] iteram peste lista din backend - oricate, flexibil
        const lista = cal.motivationale || [];
        if (!lista.length) { bara3.innerHTML = ""; return; }
        bara3.innerHTML = lista.map((m, i) =>
          (i ? `<span class="bara3-sep">·</span>` : "") +
          `<span class="bara3-item"><b>${m.valoare}</b> ${m.eticheta}</span>`
        ).join("");
      }).catch(() => { bara3.innerHTML = ""; });
    }

    ecran.appendChild(antet);   // [a11y_landmark] banner cu tot chrome-ul de sus, INAINTE de main
    const continut = document.createElement("main");
    continut.className = "desktop-continut";
    ecran.appendChild(continut);
    radacina.appendChild(ecran);

    desktopRandator(continut, nav);
    _anunturiBanner(ecran);  /* anunturi_fe_v1 */
    randeazaFerestre();
  }

  // [comanda Costin 05.10.2026 pct.1b] „un contabil nu pierde niciodată ce a completat — … nici când e trimis să completeze
  // altceva”. Măsurat: refuzul emiterii trimitea la Date firmă, iar la „Înapoi” `randeazaFerestre` redesena factura de la zero.
  // Acum: o fereastră (sau un pas) în care omul a TASTAT ceva (`input`/`change`) își păstrează ELEMENTUL `.fereastra-corp` — cu
  // valorile, rândurile adăugate și ascultătorii lui — când se deschide altceva peste ea; la revenire, elementul se pune la loc în
  // locul redesenării și primește `nav:revenire` (un ecran care vrea să-și reîmprospăteze datele ascultă evenimentul). O fereastră
  // neatinsă se redesenează ca înainte. Gard: `core/test_sesiune_fara_pierdere.py` + proba din browser.
  function _corpCurent() { return radacina.querySelector(".fereastra-corp"); }
  function _dePastrat() {
    const c = _corpCurent();
    if (!c || !c.__murdar) return null;
    const f = c.closest(".fereastra");
    return { corp: c, clase: f ? f.className : "" };
  }
  function _marcheazaModificari(corp) {
    if (corp.__ascultaModificari) return;
    corp.__ascultaModificari = true;
    const murdar = (e) => { if (e.isTrusted) corp.__murdar = true; };
    corp.addEventListener("input", murdar, true);
    corp.addEventListener("change", murdar, true);
  }
  window._navAreModificari = () => {
    const c = _corpCurent();
    return !!((c && c.__murdar) || stiva.some((x) => x.pastrat || (x.pasi || []).some((p) => p.pastrat)));
  };

  function randeazaFerestre() {
    radacina.querySelectorAll(".fereastra-overlay").forEach((o) => o.remove());
    if (stiva.length === 0) return;
    const sus = stiva[stiva.length - 1];

    const overlay = document.createElement("div");
    overlay.className = "fereastra-overlay";  /* fereastra-de-lucru: doar X (DS cap.9, DECIZII 04.10.2026 — Esc nu aruncă un formular) */
    const fer = document.createElement("div");
    fer.className = "fereastra";
    // [a11y_landmark] fereastra de lucru e un dialog modal: role=dialog e frontiera de landmark
    // (continutul ei nu mai declanseaza regula axe "region") + nume accesibil din titlul ferestrei.
    fer.setAttribute("role", "dialog");
    fer.setAttribute("aria-modal", "true");
    fer.setAttribute("aria-label", String(sus.titluCurent || sus.titlu || "Fereastră de lucru"));
    // Sageata apare DOAR cand exista un "inapoi" real:
    //  - mai multe ferestre pe stiva, SAU
    //  - ecranul curent isi defineste o functie interna 'inapoi' (ex: migrare in cascada)
    const areInapoi = stiva.length > 1 || typeof sus.inapoi === "function" || (sus.pasi && sus.pasi.length > 0);  // traseu_automat_v1
    // breadcrumb_v1: drumul (breadcrumb) din traseul real — ferestre + pasi + curent
    const drum = [];
    for (let i = 0; i < stiva.length - 1; i++) drum.push({ text: stiva[i].titlu || "…", fereastra: i });
    (sus.pasi || []).forEach((p, i) => { if (p.titlu) drum.push({ text: p.titlu, pas: i }); });
    const drumHtml = drum.map((d, i) =>
      `<button class="fir-veriga" data-fer="${d.fereastra ?? ''}" data-pas="${d.pas ?? ''}">${esc(String(d.text))}</button>` +
      (i < drum.length - 1 ? `<span class="fir-sep" aria-hidden="true">›</span>` : "")
    ).join("");  // fir_doar_parinti_v1: doar parintii; pasul curent = titlul din corp
    fer.innerHTML = `
      <div class="fereastra-antet">
        <button class="nav-sageata nav-inapoi" title="Înapoi" aria-label="Înapoi" ${areInapoi ? '' : 'style="display:none"'}><span aria-hidden="true">←</span></button>
        <span class="fereastra-fir">${drumHtml}</span>
        <span class="fereastra-spatiu"></span>
        <button class="nav-x" title="Închide" aria-label="Închide"><span aria-hidden="true">✕</span></button>
      </div>
      <div class="fereastra-corp" tabindex="0"></div>
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
      sus.pastrat = p.pastrat || null;   // [pct.1b]
      randeazaFerestre();
    }));
    const bInapoi = fer.querySelector(".nav-inapoi");
    if (bInapoi) {
      bInapoi.addEventListener("click", () => {  // traseu_automat_v1
        // [fir_pop_v1 10.08.2026] Back CONSUMA pozitia reala INAINTE de setInapoi custom. Altfel un
        // setInapoi(()=>re-randare) sarea pop-ul si antetul acumula ferestre/pasi (dovedit in browser:
        // 'Migrare cabinet' > Solduri > Salariati...). Ordine: pop pas (traseu) -> pop fereastra (stiva>1)
        // -> setInapoi custom (doar fara pop natural) -> nav.inapoi.
        if (sus.pasi && sus.pasi.length) {
          const p = sus.pasi.pop();
          sus.curent = p.randator;
          sus.titluCurent = p.titlu || "";  // breadcrumb_v1
          sus.scrollY = p.scrollY || 0;
          sus.pastrat = p.pastrat || null;   // [pct.1b]
          randeazaFerestre();
          return;
        }
        if (stiva.length > 1) { nav.inapoi(); return; }
        if (typeof sus.inapoi === "function") { sus.inapoi(); return; }
        nav.inapoi();
      });
    }
    fer.querySelector(".nav-x").addEventListener("click", () => nav.acasa());
    overlay.appendChild(fer);
    radacina.appendChild(overlay);
    fer.classList.toggle("fer-larg", (sus.optiuni || {}).lat === "larg");
    // [08.10.2026, decizia Costin W5] fereastra cu tabele se lățește cât îi cere conținutul, până la marginea ecranului (DS cap.9)
    fer.classList.toggle("fer-tabel", (sus.optiuni || {}).lat === "tabel");
    const pastrat = sus.pastrat && sus.pastrat.pentru === (sus.curent || sus.randator) ? sus.pastrat : null;
    sus.pastrat = null;
    if (pastrat) {   // [pct.1b] revenire la o fereastră în care omul lucra: elementul ei, nu o redesenare
      fer.querySelector(".fereastra-corp").replaceWith(pastrat.corp);
      if (pastrat.clase) fer.className = pastrat.clase;
      pastrat.corp.dispatchEvent(new CustomEvent("nav:revenire"));
    } else {
      (sus.curent || sus.randator)(fer.querySelector(".fereastra-corp"), nav);  // traseu_automat_v1
    }
    if (sus.scrollY) fer.querySelector(".fereastra-corp").scrollTop = sus.scrollY; /* scroll_memorat_v1 */
    /* stelute_rosii_v2: orice * din etichete devine rosu, oricand apare */
    const _corp = fer.querySelector(".fereastra-corp");
    _marcheazaModificari(_corp);
    if (pastrat && _corp.__steaza) return;   // observatorul elementului păstrat merge deja
    const _steaza = () => { /* titlu_firma_v2 + titlu_global_v1 */
      if (!_corp.querySelector("h2") && (sus.titluCurent || sus.titlu) && _corp.children.length) {
        const h = document.createElement("h2");
        h.className = "pf-titlu";
        h.textContent = sus.titluCurent || sus.titlu;  // titlul pasului curent, nu al ferestrei (ferestra poarta entitatea - DS cap.1)
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
    _corp.__steaza = true;
    new MutationObserver(_steaza).observe(_corp, { childList: true, subtree: true });
  }

  const nav = {
    deschide(titlu, randator, optiuni) {
      const c = document.querySelector(".fereastra-corp");
      if (c && stiva.length) {
        const jos = stiva[stiva.length - 1];
        jos.scrollY = c.scrollTop; /* scroll_memorat_v1 */
        const p = _dePastrat();   // [pct.1b] fereastra de dedesubt își păstrează ce s-a tastat în ea
        if (p) jos.pastrat = Object.assign(p, { pentru: jos.curent || jos.randator });
      }
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
        sus.pastrat = p.pastrat || null;   // [pct.1b]
        randeazaFerestre();
      } else nav.inapoi();
    },
    mergi(titlu, fn) {  // traseu_automat_v1 + breadcrumb_v1: pas cu titlu pe traseu
      if (!stiva.length) return;
      if (typeof titlu === "function") { fn = titlu; titlu = ""; }  // compat: mergi(fn)
      const sus = stiva[stiva.length - 1];
      const c = document.querySelector(".fereastra-corp");
      const p = _dePastrat();   // [pct.1b] pasul de dinainte își păstrează ce s-a tastat în el
      sus.pasi.push({ randator: sus.curent || sus.randator, scrollY: c ? c.scrollTop : 0,
                      titlu: sus.titluCurent || sus.titlu || "",
                      pastrat: p ? Object.assign(p, { pentru: sus.curent || sus.randator }) : null });
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
    setFirmaInLucru(nume, id = null) {
      firmaInLucru = nume; firmaInLucruId = nume ? id : null;
      try { if (nume) sessionStorage.setItem(CHEIE_FIRMA_LUCRU, JSON.stringify({ nume, id: firmaInLucruId })); else sessionStorage.removeItem(CHEIE_FIRMA_LUCRU); } catch { /* fără stocare */ }
      randeazaDesktop();
    },
    firmaInLucruId() { return firmaInLucruId; },
  };

  randeazaDesktop();
  // [R129, 03.09.2026] Urmarirea versiunii publicate porneste O DATA, la construirea cojii.
  // NU re-randeaza nimic la detectie: aseaza un nod in locul declarat mai sus. *O re-randare ar fi
  // pierdut exact formularul pe jumatate completat pe care decizia lui Costin il apara.*
  _versiune.porneste();
  // [clopot_routing] expune nav-ul curent pentru routing-ul notificarilor din clopotel.
  // Handler-ul clopotelului (functie de modul, in afara acestui closure) il citea deja prin
  // window._navGlobal, dar nu era atribuit nicaieri -> routing mort. Aici se realizeaza pattern-ul.
  window._navGlobal = nav;
  return nav;
}


// [p58_clopot] clopotel notificari (badge + panou)
async function _clopotActualizeazaBadge(container) {  // [p66_badge_ref]
  const badge = (container || document).querySelector("#nav-clopot-badge");
  if (!badge) return;
  try {  // generalizare_zi_v1: notificarile sunt de cabinet; pe client nu interogam (evita 403)
    const { sesiune } = await import("./sesiune.js?v=38c3e6f6fe");
    if (((sesiune.user() || {}).rol) === "client") {
      badge.style.display = "none";
      const btn = (container || document).querySelector("#nav-clopot");
      if (btn) btn.style.display = "none";
      return;
    }
  } catch {}
  try {
    const { api } = await import("./api.js?v=2561dbfd34");
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
    panou.innerHTML = `<div class="clopot-cap"><span>Notificări</span></div><div class="clopot-lista" id="clopot-lista"><div class="clopot-gol">Se încarcă…</div></div>`;
    ecran.appendChild(panou);
    const { api } = await import("./api.js?v=2561dbfd34");
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
        // [retest 07.10 seara, S4] notificarea rezolvată (elementul și-a schimbat starea) nu mai e „de făcut”: o spune și nu mai
        // apare ca necitită
        const REZ = { validat: "rezolvată: validată", respins: "rezolvată: respinsă", inlocuit: "rezolvată: înlocuită",
                      inexistent: "rezolvată: elementul nu mai există" };   // [08.10 pct.4]
        it.className = "clopot-item" + (n.citit || n.rezolvata ? "" : " clopot-necitit");
        it.innerHTML = `<div class="clopot-text">${esc(n.text||"")}</div><div class="clopot-cand">${_clopotData(n.cand)}${n.rezolvata ? " · " + esc(REZ[n.rezolvata] || "rezolvată") : ""}</div>`;
        it.addEventListener("click", async () => {
          panou.remove();
          // [lotul 07.10 pct.8, comanda Costin 06.10.2026] „Click pe notificarea «Notă pregătită, de validat» doar închide lista;
          // trebuie să ducă la nota de validat.” `validat[:<coada_id>]` deschide „De validat” la element; `jurnal:<firmă>:<notă>
          // [:<an>:<lună>]` (cel care a pregătit nota n-are „De validat”) deschide Registrul jurnal al firmei, în luna notei.
          if (typeof n.link === "string" && (n.link === "validat" || n.link.startsWith("validat:")) && window._navGlobal) {
            const id = parseInt(n.link.split(":")[1], 10);
            try {
              const { randeazaValidat } = await import("./ecrane/validat.js?v=f25e1ed56e");
              window._navGlobal.acasa();
              window._navGlobal.deschide("De validat", (corp, nn) => randeazaValidat(corp, nn, Number.isFinite(id) ? { evidentiaza: id } : {}), { nivel: "cabinet" });
            } catch (e) { console.warn("[clopot] nu am putut deschide De validat:", e); }
          }
          else if (typeof n.link === "string" && n.link.startsWith("jurnal:") && window._navGlobal) {
            const [, tid, nid, an, luna] = n.link.split(":").map((x) => parseInt(x, 10));
            if (!Number.isFinite(tid)) { console.warn("[clopot] link jurnal malformat:", n.link); return; }
            try {
              const { api } = await import("./api.js?v=2561dbfd34");
              const { ecranJurnal } = await import("./ecrane/firme.js?v=8fc3bd020b");
              const t = ((await api.get("/tenants")).tenants || []).find((x) => x.id === tid);
              if (!t) { console.warn("[clopot] firma notificării nu e în lista ta:", tid); return; }
              window._navGlobal.acasa();
              window._navGlobal.deschide(`Registru jurnal · ${t.nume}`, (corp, nn) => ecranJurnal(corp, nn, t,
                Object.assign({ evidentiaza: Number.isFinite(nid) ? nid : null }, Number.isFinite(an) && Number.isFinite(luna) ? { an, luna } : {})));
            } catch (e) { console.warn("[clopot] nu am putut deschide Registrul jurnal:", e); }
          }
          // [F164_routing] notificare de control fiscal -> deschide ecranul FIRMEI respective (nu portofoliul).
          // Format link: "control-fiscal:{tid}". tid malformat -> log + fallback (ramai pe ecran, nu ecran alb).
          else if (typeof n.link === "string" && n.link.startsWith("control-fiscal:") && window._navGlobal) {
            const tid = parseInt(n.link.slice("control-fiscal:".length), 10);
            if (!Number.isFinite(tid)) { console.warn("[clopot] link control-fiscal malformat:", n.link); return; }
            try {
              const { randeazaControl } = await import("./ecrane/control.js?v=ad497d96e3");  // ?v=1 aliniat cu cabinet/asistent — fara versiune ar instantia o a doua copie a modulului
              window._navGlobal.deschide("Control fiscal", (corp, nn) => randeazaControl(corp, nn, tid), { nivel: "cabinet" });
            } catch (e) { console.warn("[clopot] nu am putut deschide control fiscal:", e); }
          }
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
    // [validare_note 06.10.2026] coada poartă declarații ȘI note: „lucrare” le numește pe amândouă
    de_validat: n === 1 ? "1 lucrare de validat" : n + " lucrări de validat",
    aprobata: n === 1 ? "1 lucrare validată" : n + " lucrări validate",
    respinsa: n === 1 ? "1 lucrare respinsă" : n + " lucrări respinse",
    depusa: n === 1 ? "1 declarație depusă" : n + " declarații depuse",
  };
  return map[tip] || (n === 1 ? "1 notificare" : n + " notificări");
}
async function _sumarLogin(ecran) {
  try {
    if (sessionStorage.getItem("iconta_sumar_aratat") === "1") return;
    const { api } = await import("./api.js?v=2561dbfd34");
    const r = await api.get("/notificari/sumar");
    const total = (r && r.necitite) || 0;
    sessionStorage.setItem("iconta_sumar_aratat", "1");
    if (total <= 0) return;
    const u = sesiune.user() || {};
    // [deficiența 198, retestul Costin 09.10: „«Buna, Dobrescu!» e fără diacritice”] salutul folosește prenumele, ca desktopul
    const nume = u.prenume || (u.nume || "").split(" ").slice(-1)[0] || "";
    const detalii = (r.pe_tip || []).map((x) => _sumarTextTip(x.tip, x.n)).join(", ");
    const t = document.createElement("div");
    t.className = "sumar-toast";
    t.setAttribute("role", "status");  // [a11y_landmark] toast = live region (polite), nu continut orfan
    t.innerHTML = `<div class="sumar-toast-cap">${nume ? "Bună, " + esc(nume) + "!" : "Bine ai revenit!"}</div>` +
      `<div class="sumar-toast-corp">${esc(detalii)}</div>`;
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
    const { api } = await import("./api.js?v=2561dbfd34");
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
    el.setAttribute("role", "dialog");
    el.setAttribute("aria-modal", "true");
    el.setAttribute("aria-label", "Mesaj de la iConta.eu");
    el.innerHTML = `<div class="fereastra" style="max-width:520px">
      <div class="fereastra-antet"><span class="fereastra-spatiu"></span></div>
      <div class="fereastra-corp" tabindex="0">
        <h2 class="pf-titlu">Mesaj de la iConta.eu</h2>
        <p class="anunt-text">${esc(a.mesaj || "")}</p>
        <button class="buton-primar anunt-ok">Am \u00een\u021beles</button>
      </div></div>`;
    // [dialog_inchidere 04.10.2026] X în antet + Esc = „Am înțeles” (DECIZII 04.10.2026): închiderea CONFIRMĂ
    // citirea — un X care închide fără confirmare ar fi o ușă înapoi spre același anunț la intrarea următoare.
    const confirma = async () => {
      try {
        const { api } = await import("./api.js?v=2561dbfd34");
        await api.post(`/eu/anunturi/${a.id}/confirma`, {});
        el.remove();
      } catch (e) {
        /* [catch_scriere 27.07.2026] confirmarea nesalvata parea salvata - anuntul
           disparea de pe ecran dar reapare la reincarcare, fara explicatie. */
        const t = el.querySelector(".anunt-text") || el;
        t.textContent = "Nu am putut confirma. Reîncarcă pagina și încearcă din nou.";
      }
    };
    document.body.appendChild(el);
    const inchide = inchidereDialog(el, confirma, el.querySelector(".fereastra-antet"));
    el.querySelector(".anunt-ok").addEventListener("click", inchide);
  });
}
// sageata_dinamica_v1

// traseu_automat_v1

// breadcrumb_v1

// faza_b_traseu_v1

// provenienta_v1

// uniformizare_fir_v1

// fir_doar_parinti_v1
