// navigator.js — managerul de ferestre (inima shell-ului).
//
// DESKTOP rolului:
//   bara albastră sus: logo + iConta + context rol + user + IEȘIRE (portocaliu, dreapta)
//   bara albastru-gri dedesubt (cabinet/asistent): firma în lucru
//   client: doar bara albastră (o singură firmă)
// FEREASTRĂ de lucru (modală, centrală peste overlay umbrit):
//   ← stânga-sus -> UN PAS ÎNAPOI pe traseul parcurs (apare doar când există drum);
//   X dreapta-sus -> ÎNCHIDE fereastra (acasă). Traseul e memorat de navigator (nav.mergi).

import { sesiune } from "./sesiune.js?v=898215e0ee";
import { esc, inchidereDialog, cate, ultimaCerere, dataRo } from "./api.js?v=e38843b1ec";  // esc canonic (cap.10): strip-html data-lossy inlocuit
import { deschideAnsamblu } from "./ecrane/ansamblu.js?v=1be335b472";  // [bun_venit_v1] "?" general (ansamblu)
import * as _coaja from "./coaja.js?v=2776271008";  // [DS cap.25] contractul proprietar<->chirias
import * as _versiune from "./versiune.js?v=9a0ee2174b";      // [R129] anunta o publicare noua, fara sa intrerupa
import { numeDeSalut } from "./ecrane/salut.js?v=10719d2154";   // [269] numele din salut, același loc ca pagina principală
import { reimprospateazaDrepturi } from "./drepturi.js?v=34d0fb0afd";   // [265] drepturile recitite pe ceasul aplicației

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
        { text: _functieAsistent(u), slab: true, functie: true },   // [265] rescrisă la o schimbare de drepturi
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

// ── [lotul 11, deficiența 445, comanda Costin 11.1 pct.21, verbatim: „orice buton «Deschide X» dintr-un refuz întoarce în formularul de
// plecare, cu datele intacte.”] Inventarul lotului 11: ce s-a TASTAT se păstra la „←” (pct.1b, mai jos), dar (1) un formular în care omul
// doar a ales / a apăsat se redesena de la zero; (2) X din destinație arunca tot drumul, cu formularul; (3) numai patru ecrane spuneau
// „Înapoi la <formular>”, iar butoanele puse automat lângă refuz (api.js) nu treceau `inapoiLa`. UN mecanism, aici:
//   - `nav.dinRefuz()` (chemat de `butonSpreEcran` chiar înainte de `deschide`): fereastra de dedesubt se păstrează ORICUM (elementul ei,
//     cu valorile, rândurile și refuzul afișat), iar fereastra nouă ține minte unde întoarce (`intoarcere`);
//   - săgeata ferestrei-destinație spune „← Înapoi la <formular>”, iar X o închide numai pe ea și întoarce la formular;
//   - `nav.titluCurent()` dă destinației numele formularului (`inapoiLa` implicit).
// Gard: verificator INTOARCERE_DIN_REFUZ + `core/test_lot11_u0_intoarcere.py` (în browser) + e2e `test_def_445_*`.
let _dinRefuz = 0;
function _butonInapoi(sus, areInapoi) {
  const ascuns = areInapoi ? "" : ' style="display:none"';
  if (sus.intoarcere && sus.intoarcere.titlu && !(sus.pasi && sus.pasi.length)) {
    const t = esc("Înapoi la " + sus.intoarcere.titlu);
    return `<button class="nav-sageata nav-inapoi nav-inapoi-la" title="${t}" aria-label="${t}"${ascuns}><span aria-hidden="true">←</span><span>${t}</span></button>`;
  }
  return `<button class="nav-sageata nav-inapoi" title="Înapoi" aria-label="Înapoi"${ascuns}><span aria-hidden="true">←</span></button>`;
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
        `<span class="${v.slab ? "bara-veriga-slab" : "bara-veriga"}"${v.functie ? " data-functie-asistent" : ""}>${esc(v.text)}</span>`).join("")}
      <span class="bara-spatiu"></span>
      <button class="nav-ghid" id="nav-ghid" title="Prezentarea aplicației (ansamblu)" aria-label="Prezentarea aplicației (ansamblu)"><svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="1.3"/><rect x="14" y="3" width="7" height="7" rx="1.3"/><rect x="3" y="14" width="7" height="7" rx="1.3"/><rect x="14" y="14" width="7" height="7" rx="1.3"/></svg><span class="nav-ghid-q">?</span></button>
      <button class="nav-clopot" id="nav-clopot" data-deschide="notificari" title="Notificări" aria-label="Notificări"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></svg><span class="nav-clopot-badge" id="nav-clopot-badge"></span></button>
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
        // [15.10.2026, deficiența 256] textul centralizatorului stă în span-ul LUI: rescrierea întregii bare (innerHTML) ștergea
        // anunțul „Versiune nouă” pus între timp de `_versiune.aseaza()` — superadminul nu afla niciodată de publicare.
        subbara.innerHTML = `${icon}<span class="subbara-gol" data-sumar-admin>Se încarcă centralizatorul...</span>`;
        const sumarAdmin = subbara.querySelector("[data-sumar-admin]");
        // [lotul 13, 644 a — clasa 286] „După suspendare bara de sus rămâne «2 cabinete active» până la reîncărcare”: centralizatorul se
        // recitește după orice scriere reușită pe un cabinet (`iconta:schimbare` din api.js, cu căile scrise), ca pagina principală (286)
        const citesteSumarAdmin = () => import("./api.js?v=e38843b1ec").then(({ api }) => api.get("/admin/activitate/cabinete")).then((r) => {
          const cabinete = (r && r.cabinete) || [];
          const active = cabinete.filter((c) => c.activ).length;
          const firme = cabinete.reduce((s2, c) => s2 + (c.nr_firme || 0), 0);
          const utilizatori = cabinete.reduce((s2, c) => s2 + (c.nr_utilizatori || 0), 0);   // [644 b] conturile, nu salariații
          const facturi = cabinete.reduce((s2, c) => s2 + (c.nr_facturi || 0), 0);
          const declaratii = cabinete.reduce((s2, c) => s2 + (c.nr_declaratii || 0), 0);
          const recomandari = cabinete.reduce((s2, c) => s2 + (c.nr_recomandari || 0), 0);
          sumarAdmin.className = "subbara-admin-sumar";
          sumarAdmin.textContent = `${cate(active, "cabinet activ", "cabinete active")} · ${cate(firme, "firmă", "firme")} · ${cate(utilizatori, "utilizator", "utilizatori")} · ${cate(facturi, "factură emisă", "facturi emise")} · ${cate(declaratii, "declarație depusă", "declarații depuse")} · ${cate(recomandari, "recomandare", "recomandări")}`;
        }).catch(() => {
          sumarAdmin.textContent = "Centralizatorul nu a putut fi încărcat.";
        });
        citesteSumarAdmin();
        const laSchimbareCabinet = (ev) => {
          if (!sumarAdmin.isConnected) { window.removeEventListener("iconta:schimbare", laSchimbareCabinet); return; }
          if (((ev.detail && ev.detail.cai) || []).some((c) => String(c).startsWith("/admin/cabinete/"))) citesteSumarAdmin();
        };
        window.addEventListener("iconta:schimbare", laSchimbareCabinet);
      } else {
        subbara.innerHTML = firmaInLucru
          ? `${icon}<span class="subbara-cheie">În lucru:</span> <span class="subbara-firma">${esc(firmaInLucru)}</span>`   /* [331] spațiul și în text, nu numai în `gap` */
          : `${icon}<span class="subbara-gol">Firmă activă: Nicio firmă selectată</span>`;
      }
      antet.appendChild(subbara);
      // [DS cap.25, 21.08.2026] Proprietarul isi DECLARA locul inchiriabil. Chiriasii (ecrane) cer
      // loc prin `coaja.pune(...)`, nu si-l iau cu `document.querySelector(".subbara")`.
      _coaja.inregistreazaLoc(_coaja.LOCURI.BARA_DE_STARE, subbara);
      // [R129] Al doilea chirias al barii: daca s-a gasit deja o versiune noua, anuntul revine
      // dupa re-randarea cojii (care sterge locurile si le declara din nou).
      _versiune.aseaza();
      _versiune.aseazaActualizat();   // [256] „s-a actualizat la versiunea nouă”, după o reîncărcare făcută de aplicație
    }
    // [p25_bara3] bara 3 motivationala — doar asistent (angajat)
    if (u.rol === "angajat") {
      const bara3 = document.createElement("div");
      bara3.className = "bara3";
      bara3.innerHTML = `<span class="bara3-gol">se încarcă realizările tale…</span>`;
      antet.appendChild(bara3);
      urmaresteBara3(bara3);
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
  function _dePastrat(oricum = false) {
    const c = _corpCurent();
    if (!c || (!c.__murdar && !oricum)) return null;   // [445] `oricum`: deschiderea dintr-un refuz păstrează formularul și neatins
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
  window._navPeAcasa = () => stiva.length === 0;   // [256] pe pagina principală (nicio fereastră deschisă)
  window._navAreModificari = () => {
    const c = _corpCurent();
    return !!((c && c.__murdar) || stiva.some((x) => x.pastrat || (x.pasi || []).some((p) => p.pastrat)));
  };

  // ── [lotul 12, C140 (găsită la 485)] SĂGEATA = UN PAS ÎNAPOI, întâi în ecran (DS cap.3: „duce MEREU exact un pas înapoi în ierarhia
  // ecranului”). Un ecran care se redesenează pe loc (editorul de șablon din Contracte, previzualizarea unui import) își declară pasul de
  // dinainte cu `nav.setInapoi(fn)`. Ordinea veche — pas pe traseu -> fereastră -> `setInapoi` — nu ajungea niciodată la `setInapoi` pe a
  // doua fereastră sau într-un pas: „←” din editor închidea Contracte. Acum: (1) pasul intern al ecranului, o singură dată (se consumă
  // înainte de chemare); (2) pasul de pe traseu (`nav.mergi`); (3) fereastra. Ca un `setInapoi` vechi să nu ajungă în alt ecran: un ecran
  // desenat de la început pornește fără pas intern (rădăcina își spune singură, DS cap.3), iar pasul / fereastra la care se revine cu
  // elementul păstrat (pct.1b) își primește înapoi și pasul intern. X nu se schimbă: închide fereastra (deficiența 4); Esc nu închide
  // ferestrele de lucru (DECIZII 04.10.2026). Garda: `core/test_lot12_inapoi_sageata.py` + e2e `test_def_c140_*`.
  function _arataSageata() {
    const b = radacina.querySelector(".nav-inapoi");
    const sus = stiva[stiva.length - 1];
    if (b && sus) b.style.display = (typeof sus.inapoi === "function" || stiva.length > 1 || (sus.pasi && sus.pasi.length > 0)) ? "" : "none";  // traseu_automat_v1
  }
  function _laPas(sus, idx) {   // întoarcerea la pasul `idx` de pe traseu (săgeata, firul, `inapoiPas`)
    const p = sus.pasi[idx];
    sus.pasi.length = idx;
    sus.curent = p.randator;
    sus.titluCurent = p.titlu || "";  // breadcrumb_v1
    sus.scrollY = p.scrollY || 0;
    sus.pastrat = p.pastrat || null;   // [pct.1b]
    sus.inapoi = p.inapoi || null;     // [C140] pasul intern al pasului păstrat; `randeazaFerestre` îl scoate dacă pasul se redesenează
  }

  function randeazaFerestre() {
    radacina.querySelectorAll(".fereastra-overlay").forEach((o) => o.remove());
    if (stiva.length === 0) return;
    const sus = stiva[stiva.length - 1];
    const pastrat = sus.pastrat && sus.pastrat.pentru === (sus.curent || sus.randator) ? sus.pastrat : null;
    sus.pastrat = null;
    if (!pastrat) sus.inapoi = null;   // [C140] ecran desenat de la început: niciun pas intern până nu și-l declară el

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
        ${_butonInapoi(sus, areInapoi)}
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
      _laPas(sus, Number(b.dataset.pas));  // sari la un pas de pe traseu
      randeazaFerestre();
    }));
    const bInapoi = fer.querySelector(".nav-inapoi");
    if (bInapoi) {
      bInapoi.addEventListener("click", () => {  // traseu_automat_v1
        // [C140] ordinea: pasul intern al ecranului (o dată) -> pasul de pe traseu -> fereastra. [fir_pop_v1 10.08.2026] Acumularea de
        // ferestre / pași venea din ecrane care-și declarau ca pas intern ecranul ferestrei de dedesubt; rădăcina unei ferestre sau a unui
        // pas nu-și declară pas intern (DS cap.3) — garda `core/test_lot12_inapoi_sageata.py` o face imposibilă.
        if (typeof sus.inapoi === "function") { const f = sus.inapoi; sus.inapoi = null; f(); _arataSageata(); return; }
        if (sus.pasi && sus.pasi.length) { _laPas(sus, sus.pasi.length - 1); randeazaFerestre(); return; }
        nav.inapoi();
      });
    }
    // [445] fereastra deschisă dintr-un refuz: X o închide pe ea și întoarce la formularul de plecare (păstrat), nu aruncă tot drumul
    fer.querySelector(".nav-x").addEventListener("click", () => (sus.intoarcere && stiva.length > 1 ? nav.inapoi() : nav.acasa()));
    overlay.appendChild(fer);
    radacina.appendChild(overlay);
    fer.classList.toggle("fer-larg", (sus.optiuni || {}).lat === "larg");
    // [08.10.2026, decizia Costin W5] fereastra cu tabele se lățește cât îi cere conținutul, până la marginea ecranului (DS cap.9)
    fer.classList.toggle("fer-tabel", (sus.optiuni || {}).lat === "tabel");
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
      // [deficiența 331, 18.10.2026] titlul pus aici cât ecranul se încarcă iese când ecranul își scrie titlul lui (mai adânc, într-un
      // panou — „Conectare SPV” apărea de două ori); clasa: orice ecran care se încarcă într-un copil și își pune singur titlul
      const pus = _corp.querySelector(":scope > h2[data-titlu-pus]");
      if (pus && _corp.querySelectorAll("h2").length > 1) pus.remove();
      if (!_corp.querySelector("h2") && (sus.titluCurent || sus.titlu) && _corp.children.length) {
        const h = document.createElement("h2");
        h.dataset.titluPus = "navigator";
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
    // [deficiența 285, comanda Costin 16.10.2026, verbatim în DECIZII] „nicio fereastră nu are derulare; acțiunea principală și mesajele
    // de refuz/eroare se văd mereu (… detaliul facturii, derulare orizontală)”. Fereastra al cărei conținut e mai lat decât ea se
    // lățește singură (`fer-tabel`, decizia W5, DS cap.9): nu mai depinde de ecranul care ar fi trebuit s-o ceară. Se verifică la
    // fiecare schimbare a conținutului și la redimensionare.
    // [lotul 10, deficiențele 421 și 424, comanda Costin 10.1 pct.5, verbatim în DECIZII] „Regula: ferestrele cu tabele se deschid
    // aproape pe tot ecranul (cum e deja Balanța de verificare); rezumatul stă fix sus și acțiunea principală fix jos; se derulează doar
    // tabelul din mijloc, niciodată lateral.” Orice fereastră care CONȚINE un tabel (`<table>` sau lista-tabel declarată
    // `.mig-sold-tabel`) devine fereastră cu tabel (`fer-tabel`, DS cap.9 v2.96), oricine ar fi ecranul. Clasa nu se mai scoate cât
    // fereastra e deschisă: „Se încarcă…” dintre două luni ar strânge-o și ar lăți-o la loc la fiecare lună. Tabelul care nici așa nu
    // încape (corpul nu derulează lateral) se strânge în trepte, cât e nevoie (`fer-strans`, apoi `fer-rupt`: litera și celula mai mici,
    // apoi textul rupt oriunde — stil.css „FEREASTRA CU TABEL”); fiecare treaptă se măsoară imediat, fără să aștepte altă schimbare.
    // Cutia previzualizării (`.mig-prev-cutie`, 349) nu mai derulează ea însăși, deci depășirea ei se vede în corp.
    // Fereastra se ia din corp, nu din închidere: la revenirea într-o fereastră păstrată (pct.1b) corpul stă într-o fereastră nouă.
    const _prealata = () => _corp.scrollWidth > _corp.clientWidth + 1;
    const _cuTabel = () => !!_corp.querySelector("table, .mig-sold-tabel");
    const _lateste = () => {
      const f = _corp.closest(".fereastra") || fer;
      if (!f.classList.contains("fer-tabel") && (_cuTabel() || _prealata())) f.classList.add("fer-tabel");
      if (f.classList.contains("fer-tabel")) for (const treapta of ["fer-strans", "fer-rupt"]) { if (!_prealata()) break; f.classList.add(treapta); }
      const rez = _corp.querySelector(".rezumat-fix");   // antetul tabelului se lipește sub rezumatul lipit sus
      _corp.style.setProperty("--rezumat-h", (rez ? rez.offsetHeight : 0) + "px");
      // [lotul 11, decizia Costin 10.3: „Totalurile … fix”] rândul de total (`tfoot`) se lipește jos, deasupra barei de acțiune (DS cap.9 v2.100)
      const bara = [..._corp.querySelectorAll(".bara-fixa")].pop();
      if (bara) _corp.style.setProperty("--bara-h", bara.offsetHeight + "px"); else _corp.style.removeProperty("--bara-h");
    };
    _lateste();
    // [lotul 12, comanda Costin 12.2 pct.9, deficiența 617 — clasa „după o acțiune pe rând fereastra sare sus”, DS cap.9 v2.102] Un ecran
    // care se redesenează după o acțiune pe un rând trece prin „Se încarcă…”: conținutul scade la un rând, derularea cade la 0 și, când
    // lista revine, omul e sus, nu la rândul pe care a lucrat (56 de redesenări de felul ăsta, în 9 ecrane). Navigatorul ține minte
    // derularea din clipa clicului într-un rând (celula unui tabel, detaliul unui rând, rândul-card `.pf-frand` / `.val-card`, un rând de
    // listă) și, dacă în cel mult 10 s ecranul trece prin „Se încarcă…”, o pune la loc când conținutul revine. Clicurile din rezumatul de
    // sus (luna ←/→, filtrele) nu intră: acolo vine altă listă. Gard: `core/test_lot12_ui2_derulare.py`.
    let _clicPeRand = null, _susDeRefacut = null;
    _corp.addEventListener("click", (e) => {
      if (e.target.closest("td, .tn-detaliu, .pf-frand, .val-card, .mig-sold-rand, li") && !e.target.closest(".rezumat-fix"))
        _clicPeRand = { la: Date.now(), sus: _corp.scrollTop };
    }, true);
    const _seIncarca = () => { const k = [..._corp.children].filter((x) => !x.matches("h2[data-titlu-pus]"));
      return k.length === 1 && k[0].matches("p.ecran-nota"); };
    const _derulare = () => {
      if (_seIncarca()) {
        if (_susDeRefacut == null && _clicPeRand && _clicPeRand.sus > 0 && Date.now() - _clicPeRand.la < 10000) _susDeRefacut = _clicPeRand.sus;
        _clicPeRand = null;
        return;
      }
      if (_susDeRefacut != null) { const v = _susDeRefacut; _susDeRefacut = null; _corp.scrollTop = v; }
    };
    new MutationObserver(() => { _derulare(); _steaza(); _lateste(); }).observe(_corp, { childList: true, subtree: true });
    if (window.ResizeObserver) new ResizeObserver(_lateste).observe(_corp);
  }

  const nav = {
    deschide(titlu, randator, optiuni) {
      // [256] de pe pagina principală, cu o versiune nouă deja știută și fără formular început: întâi versiunea nouă (reîncărcare)
      if (!stiva.length && _versiune.reincarcaInLocDeDeschidere()) return;
      const c = document.querySelector(".fereastra-corp");
      const dinRefuz = _dinRefuz && Date.now() - _dinRefuz < 1000;   // [445] cerută de `butonSpreEcran` chiar înainte
      _dinRefuz = 0;
      let intoarcere = null;
      if (c && stiva.length) {
        const jos = stiva[stiva.length - 1];
        jos.scrollY = c.scrollTop; /* scroll_memorat_v1 */
        const p = _dePastrat(dinRefuz);   // [pct.1b] fereastra de dedesubt își păstrează ce s-a tastat în ea; [445] din refuz: oricum
        if (p) jos.pastrat = Object.assign(p, { pentru: jos.curent || jos.randator });
        if (dinRefuz) intoarcere = { titlu: String(jos.titluCurent || jos.titlu || "") };
      }
      stiva.push({ titlu, randator, curent: randator, pasi: [], optiuni: optiuni || {}, intoarcere }); randeazaFerestre(); }, /* fereastra_optiuni_v1 + traseu_automat_v1 */
    // [445] următoarea `deschide` vine dintr-un buton „Deschide X” al unui refuz (`ecran_destinatie.butonSpreEcran`)
    dinRefuz() { _dinRefuz = Date.now(); },
    // [445] titlul ferestrei de sus (pasul curent), ca destinația să spună „Înapoi la <titlu>”
    titluCurent() { const s = stiva[stiva.length - 1]; return s ? String(s.titluCurent || s.titlu || "") : ""; },
    inapoi() { stiva.pop(); randeazaFerestre(); if (!stiva.length) _versiune.laAcasa(); },   // [256] ultima fereastră închisă = acasă
    inapoiPas() {  // faza_b_traseu_v1: un pas inapoi pe traseu, programatic (dupa o actiune reusita)
      if (!stiva.length) return;
      // [C140] după o acțiune reușită se iese din pas, nu se ia pasul intern al ecranului (`setInapoi`)
      const sus = stiva[stiva.length - 1];
      if (sus.pasi && sus.pasi.length) {
        _laPas(sus, sus.pasi.length - 1);
        randeazaFerestre();
      } else nav.inapoi();
    },
    reiaPasul() {  // [C140] pasul curent, de la început (cu argumentele lui): din previzualizarea unui import, înapoi la alegerea fișierului
      if (!stiva.length) return;
      stiva[stiva.length - 1].scrollY = 0;
      randeazaFerestre();
    },
    mergi(titlu, fn) {  // traseu_automat_v1 + breadcrumb_v1: pas cu titlu pe traseu
      if (!stiva.length) return;
      if (typeof titlu === "function") { fn = titlu; titlu = ""; }  // compat: mergi(fn)
      const sus = stiva[stiva.length - 1];
      const c = document.querySelector(".fereastra-corp");
      const p = _dePastrat();   // [pct.1b] pasul de dinainte își păstrează ce s-a tastat în el
      sus.pasi.push({ randator: sus.curent || sus.randator, scrollY: c ? c.scrollTop : 0,
                      titlu: sus.titluCurent || sus.titlu || "",
                      pastrat: p ? Object.assign(p, { pentru: sus.curent || sus.randator }) : null,
                      inapoi: p ? sus.inapoi : null });   // [C140] pasul intern merge cu elementul păstrat
      sus.curent = fn;
      sus.titluCurent = titlu || "";
      sus.scrollY = 0;
      randeazaFerestre();   // [C140] pasul nou pornește fără pas intern (`randeazaFerestre`)
    },
    setInapoi(fn) {  // sageata_dinamica_v1
      if (!stiva.length) return;
      stiva[stiva.length - 1].inapoi = fn;
      _arataSageata();
    },
    acasa() { stiva.length = 0; randeazaFerestre(); _versiune.laAcasa(); },   // [256] pagina principală se încarcă în versiunea nouă
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
  // [deficiența 265, comanda Costin 15.10.2026] „Ecranul urmează drepturile fără re-autentificare.” Pe același ceas cu versiunea: dacă
  // bifele s-au schimbat, drepturi.js a reaplicat deja poarta pe pagină; aici se pun în sesiune (fără redesenare), se rescrie eticheta
  // senior/junior, iar cardurile paginii principale se redesenează — acum, dacă omul e pe pagina principală fără formular început,
  // altfel la întoarcerea acasă. Clientul și previzualizarea portalului n-au poartă (app.js), deci nici drepturi de recitit.
  if (sesiune.rol() !== "client" && !(sesiune.estePreview && sesiune.estePreview())) {
    let carduriVechi = false;
    _versiune.peAcelasiCeas("drepturi", async () => {
      const nou = await reimprospateazaDrepturi();
      if (nou) {
        const u = sesiune.actualizeazaInLoc(nou.bife) || {};
        const et = radacina.querySelector("[data-functie-asistent]");
        if (et && u.rol === "angajat") et.textContent = _functieAsistent(u);
        carduriVechi = true;
      }
      if (carduriVechi && !stiva.length && !window._navAreModificari()) {
        const continut = radacina.querySelector(".desktop-continut");
        if (continut) { carduriVechi = false; desktopRandator(continut, nav); }
      }
    });
  }
  // [clopot_routing] expune nav-ul curent pentru routing-ul notificarilor din clopotel.
  // Handler-ul clopotelului (functie de modul, in afara acestui closure) il citea deja prin
  // window._navGlobal, dar nu era atribuit nicaieri -> routing mort. Aici se realizeaza pattern-ul.
  window._navGlobal = nav;
  return nav;
}


// [17.10.2026, lotul 7 pct.2.1] Locul din aplicație numit de o notificare (email / WhatsApp: `/deschide/<cheie>` -> `/#deschide=<cheie>`;
// clopoțelul: `deschide:<cheie>`): elementul desktopului cu `data-deschide="<cheie>"` se apasă. Cheile: `core/notificari.DESCHIDERI`.
export function deschideCheie(cheie) {
  if (window._navGlobal) window._navGlobal.acasa();
  const el = document.querySelector(`[data-deschide="${String(cheie).replace(/[^\w-]/g, "")}"]`);
  if (el) el.click();
  return !!el;
}

export function deschideDinAdresa() {
  const m = (location.hash || "").match(/^#deschide=([\w-]+)$/);
  if (!m) return false;
  history.replaceState(null, "", location.pathname + location.search);
  return deschideCheie(m[1]);
}

// [p58_clopot] clopotel notificari (badge + panou)
// [deficiența 492, lotul 12: „contorul «pregătite» se actualizează abia după reîncărcare”] Bara realizărilor asistentului se citea o dată,
// la construirea barei. Acum se recitește pe ACELAȘI semnal ca clopoțelul și contoarele paginii principale (422): `iconta:schimbare`,
// după orice scriere reușită prin `api.*` (nota trimisă la validare, retrimiterea) și când clopoțelul vede o schimbare din afară (colegul
// a validat sau a respins -> „acceptate din prima”). Răspunsul unei citiri vechi nu se scrie peste unul nou (`ultimaCerere`, C103).
// [lotul 07.10 pct.4] eticheta spune „luna aceasta”: cererea o cere pe luna curentă (înainte: tot istoricul).
export function urmaresteBara3(bara3) {
  const cerereNoua = ultimaCerere();
  const citeste = async () => {
    const actuala = cerereNoua();
    const _azi = new Date(), _de = `${_azi.getFullYear()}-${String(_azi.getMonth() + 1).padStart(2, "0")}-01`;
    let cal = null;
    try { const { api } = await import("./api.js?v=e38843b1ec"); cal = await api.get(`/eu/calitate?de=${_de}`); } catch { cal = null; }
    if (!actuala()) return;
    // [p26_motivationale] iteram peste lista din backend - oricate, flexibil
    const lista = (cal && cal.ok && cal.motivationale) || [];
    bara3.innerHTML = lista.map((m, i) =>
      (i ? `<span class="bara3-sep">·</span>` : "") +
      `<span class="bara3-item"><b>${esc(String(m.valoare))}</b> ${esc(m.eticheta)}</span>`
    ).join("");
  };
  const laSchimbare = () => {
    if (!bara3.isConnected) { window.removeEventListener("iconta:schimbare", laSchimbare); return; }
    citeste();
  };
  window.addEventListener("iconta:schimbare", laSchimbare);
  citeste();
  return citeste;
}

async function _clopotActualizeazaBadge(container) {  // [p66_badge_ref]
  const badge = (container || document).querySelector("#nav-clopot-badge");
  if (!badge) return;
  try {  // generalizare_zi_v1: notificarile sunt de cabinet; pe client nu interogam (evita 403)
    const { sesiune } = await import("./sesiune.js?v=898215e0ee");
    if (((sesiune.user() || {}).rol) === "client") {
      badge.style.display = "none";
      const btn = (container || document).querySelector("#nav-clopot");
      if (btn) btn.style.display = "none";
      return;
    }
  } catch {}
  try {
    const { api } = await import("./api.js?v=e38843b1ec");
    const r = await api.get("/notificari/contor");
    const n = (r && r.necitite) || 0;
    badge.textContent = n > 0 ? (n > 9 ? "9+" : String(n)) : "";
    badge.style.display = n > 0 ? "flex" : "none";
    return n;
  } catch { badge.style.display = "none"; }
  return null;
}

// [lotul 11, deficiența 422 — clasa 286, decizia Costin 10.3: „contorul «De validat» și clopoțelul nu se actualizează după acțiuni; se
// repară.”] Insigna se citea o dată, la construirea barei. Acum, un singur mecanism, aici, nu câte un apel pe ecran:
//   - după ORICE scriere reușită prin `api.*` (validare, respingere, ciornă generată, ștergere, trimitere la validare) vine semnalul
//     `iconta:schimbare` (api.js, 286): insigna și lista deschisă a clopoțelului se recitesc;
//   - ce schimbă ALTCINEVA (asistentul trimite o notă la validare, colegul validează) nu trece prin `api.js`-ul acestei file: contorul se
//     recitește la CLOPOT_INTERVAL_MS și la întoarcerea în filă; când s-a schimbat, semnalul pleacă mai departe (`din: "notificari"`), ca
//     pagina principală să-și recitească contoarele („De validat”, „De depus” — cabinet.js) fără reîncărcare.
// Gard: `core/test_lot11_j_contoare.py` (în browser, pe codul real al navigatorului și al lui api.js).
export const CLOPOT_INTERVAL_MS = 60000;
export function urmaresteClopotul(bara) {   // exportată pentru gard (o folosește numai `_clopotInit`)
  let ultim = null;
  const reia = async (dinAfara, cai = []) => {
    const n = await _clopotActualizeazaBadge(bara);
    if (n === null) return;
    const schimbat = ultim !== null && n !== ultim;
    if (dinAfara && schimbat) {
      window.dispatchEvent(new CustomEvent("iconta:schimbare", { detail: { cai: [], din: "notificari" } }));
    }
    ultim = n;
    // lista deschisă: la o scriere (alta decât „le-am văzut”, pe care o face chiar deschiderea ei) sau la o schimbare din afară
    const lista = document.querySelector("#nav-clopot-panou #clopot-lista");
    if (lista && lista.__reia && (dinAfara ? schimbat : !cai.every((c) => c === "/notificari/citit"))) lista.__reia();
  };
  const laSchimbare = (ev) => {
    if (!bara.isConnected) { window.removeEventListener("iconta:schimbare", laSchimbare); return; }
    if (ev.detail && ev.detail.din === "notificari") return;   // semnalul pornit chiar de aici
    reia(false, (ev.detail && ev.detail.cai) || []);
  };
  window.addEventListener("iconta:schimbare", laSchimbare);
  const ceas = setInterval(() => {
    if (!bara.isConnected) { clearInterval(ceas); return; }
    if (document.visibilityState === "visible") reia(true);
  }, CLOPOT_INTERVAL_MS);
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible" && bara.isConnected) reia(true); });
  return reia;
}

function _clopotInit(bara, ecran) {  // [p60_clopot]
  const btn = bara.querySelector("#nav-clopot");
  if (!btn) return;
  urmaresteClopotul(bara)(false);  // [p66_badge_ref] bara ca referinta; [422] și după fiecare scriere / schimbare din afară
  btn.addEventListener("click", async (e) => {
    e.stopPropagation();
    let panou = ecran.querySelector("#nav-clopot-panou");
    if (panou) { panou.remove(); return; }
    panou = document.createElement("div");
    panou.className = "clopot-panou";
    panou.id = "nav-clopot-panou";
    panou.innerHTML = `<div class="clopot-cap"><span>Notificări</span></div><div class="clopot-lista" id="clopot-lista"><div class="clopot-gol">Se încarcă…</div></div>`;
    ecran.appendChild(panou);
    const { api } = await import("./api.js?v=e38843b1ec");
    const lista = panou.querySelector("#clopot-lista");
    // [422] lista deschisă se reumple la o schimbare (o notificare rezolvată de validarea de alături, una nouă de la un coleg)
    const umple = async () => {
    let date;
    try { date = await api.get("/notificari"); } catch { date = { notificari: [] }; }
    if (!lista.isConnected) return;
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
          // [17.10.2026, lotul 7 pct.2.3] `deschide:<cheie>` (notificările de platformă ale superadminului) apasă elementul
          // `[data-deschide="<cheie>"]` al desktopului — același drum ca linkul din email / WhatsApp (`deschideDinAdresa`)
          if (typeof n.link === "string" && n.link.startsWith("deschide:")) {
            deschideCheie(n.link.slice("deschide:".length));
          }
          else if (typeof n.link === "string" && (n.link === "validat" || n.link.startsWith("validat:")) && window._navGlobal) {
            const id = parseInt(n.link.split(":")[1], 10);
            try {
              const { randeazaValidat } = await import("./ecrane/validat.js?v=83581fee57");
              window._navGlobal.acasa();
              window._navGlobal.deschide("De validat", (corp, nn) => randeazaValidat(corp, nn, Number.isFinite(id) ? { evidentiaza: id } : {}), { nivel: "cabinet" });
            } catch (e) { console.warn("[clopot] nu s-a putut deschide De validat:", e); }
          }
          else if (typeof n.link === "string" && n.link.startsWith("jurnal:") && window._navGlobal) {
            const [, tid, nid, an, luna] = n.link.split(":").map((x) => parseInt(x, 10));
            if (!Number.isFinite(tid)) { console.warn("[clopot] link jurnal malformat:", n.link); return; }
            try {
              const { api } = await import("./api.js?v=e38843b1ec");
              const { ecranJurnal } = await import("./ecrane/firme.js?v=2b27eebcaf");
              const t = ((await api.get("/tenants")).tenants || []).find((x) => x.id === tid);
              if (!t) { console.warn("[clopot] firma notificării nu e în lista ta:", tid); return; }
              window._navGlobal.acasa();
              window._navGlobal.deschide(`Registru jurnal · ${t.nume}`, (corp, nn) => ecranJurnal(corp, nn, t,
                Object.assign({ evidentiaza: Number.isFinite(nid) ? nid : null }, Number.isFinite(an) && Number.isFinite(luna) ? { an, luna } : {})),
                { lat: "tabel" });   // [394] Registrul jurnal se deschide lat de pe orice drum
            } catch (e) { console.warn("[clopot] nu s-a putut deschide Registrul jurnal:", e); }
          }
          // [F164_routing] notificare de control fiscal -> deschide ecranul FIRMEI respective (nu portofoliul).
          // Format link: "control-fiscal:{tid}". tid malformat -> log + fallback (ramai pe ecran, nu ecran alb).
          else if (typeof n.link === "string" && n.link.startsWith("control-fiscal:") && window._navGlobal) {
            const tid = parseInt(n.link.slice("control-fiscal:".length), 10);
            if (!Number.isFinite(tid)) { console.warn("[clopot] link control-fiscal malformat:", n.link); return; }
            try {
              const { randeazaControl } = await import("./ecrane/control.js?v=2c85c083b5");  // ?v=1 aliniat cu cabinet/asistent — fara versiune ar instantia o a doua copie a modulului
              window._navGlobal.deschide("Control fiscal", (corp, nn) => randeazaControl(corp, nn, tid), { nivel: "cabinet" });
            } catch (e) { console.warn("[clopot] nu s-a putut deschide control fiscal:", e); }
          }
        });
        lista.appendChild(it);
      });
    }
    };
    await umple();
    lista.__reia = umple;
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
    de_validat: cate(n, "lucrare de validat", "lucrări de validat"),
    aprobata: cate(n, "lucrare validată", "lucrări validate"),
    respinsa: cate(n, "lucrare respinsă", "lucrări respinse"),
    depusa: cate(n, "declarație depusă", "declarații depuse"),
  };
  return map[tip] || cate(n, "notificare", "notificări");
}
async function _sumarLogin(ecran) {
  try {
    if (sessionStorage.getItem("iconta_sumar_aratat") === "1") return;
    const { api } = await import("./api.js?v=e38843b1ec");
    const r = await api.get("/notificari/sumar");
    const total = (r && r.necitite) || 0;
    sessionStorage.setItem("iconta_sumar_aratat", "1");
    if (total <= 0) return;
    // [deficiența 198, retestul Costin 09.10: „«Buna, Dobrescu!» e fără diacritice”] salutul, ca desktopul: [269] `numeDeSalut`
    const nume = numeDeSalut(sesiune.user());
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
    const { api } = await import("./api.js?v=e38843b1ec");
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
    el.dataset.deschidere = "aplicatie";   // [325] anunțul iConta.eu se arată singur (decizie), nu de un clic
    el.innerHTML = `<div class="fereastra" style="max-width:520px">
      <div class="fereastra-antet"><span class="fereastra-spatiu"></span></div>
      <div class="fereastra-corp" tabindex="0">
        <h2 class="pf-titlu">Mesaj de la iConta.eu</h2>
        <p class="tip-micut anunt-data">Trimis pe ${dataRo(a.data_afisare || a.creat_la)}</p>   <!-- [lotul 13, 646 d] fereastra anunțului arată data -->
        <p class="anunt-text">${esc(a.mesaj || "")}</p>
        <button class="buton-primar anunt-ok">Am \u00een\u021beles</button>
      </div></div>`;
    // [dialog_inchidere 04.10.2026] X în antet + Esc = „Am înțeles” (DECIZII 04.10.2026): închiderea CONFIRMĂ
    // citirea — un X care închide fără confirmare ar fi o ușă înapoi spre același anunț la intrarea următoare.
    const confirma = async () => {
      try {
        const { api } = await import("./api.js?v=e38843b1ec");
        await api.post(`/eu/anunturi/${a.id}/confirma`, {});
        el.remove();
      } catch (e) {
        /* [catch_scriere 27.07.2026] confirmarea nesalvata parea salvata - anuntul
           disparea de pe ecran dar reapare la reincarcare, fara explicatie. */
        const t = el.querySelector(".anunt-text") || el;
        t.textContent = "Nu s-a putut confirma. Reîncarcă pagina și încearcă din nou.";
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
