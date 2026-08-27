// firme.js — lista de firme a cabinetului (parte din desktop, NU fereastră).
// Click pe o firmă -> aceea se deschide central (fereastra firmei + "În lucru").

import { api, dataRo, arataMesaj, confirmaCaseta, deschideLupa, bani, esc, CULORI_CARD, pct, eroareCamp, curataEroriCamp, semnAjutor } from "../api.js?v=c20d0584e2";  /* msg_conventie_fe_v1 + generalizare_zi_v1 */
import { sesiune } from "../sesiune.js?v=5d142951c9";
import { fluxConcediu } from "./flux_concediu.js?v=ec0eaa8e7b";  /* cm_flux_v1 */
import { randeazaFacturi } from "./facturi_ecran.js?v=cc67d99e4b";
import { ecranRip } from "./rip_ecran.js?v=e1b8bf534a";
import { ecranOperatiuni } from "./operatiuni_ecran.js?v=7019abe613";
import { ecranEtransport } from "./etransport_ecran.js?v=0dca1ea392";
import { meniuMigrarePerFirma, randeazaMigrare } from "./migrare.js?v=05a5b55996";  // [p96_import_firma] + [Q4] import in masa
import { declaratiiPerFirma } from "./declaratii.js?v=cc81187e9a";  // [decl_firma_v1]
import { CULORI as CULORI_VERDICT, etichetaStare, randeazaCorpVerdict, legaVerdict } from "./control_verdict.js?v=ddd1606ae8";  // renderer unic verdict control fiscal (DS cap.20)
import { randeazaProduse } from "./produse_ecran.js?v=2caaba5417";  // [produse_firma_v1]
import { ecranMagazin } from "./woo_ecran.js?v=ae22f440bf";  // [wc_extras_v1]
import { randeazaDateFirma } from "./date_firma.js?v=410c457136";  // [date_firma_v1]
import { ecranMijloace } from "./mijloace_ecran.js?v=cec020b9da";  // [ecran_mf_v1]

// randează lista în containerul dat; `inapoi()` revine la panoul cu carduri
export function randeazaListaFirme(container, nav, inapoi) {
  container.innerHTML = `
    <div class="firme-cap">
      <span class="firme-spatiu"></span>
      <button class="buton-secundar" id="firme-import-masa">Import în masă (CSV)</button>
      <button class="buton-primar" id="firme-adauga">+ Adaugă firmă</button>
    </div>
    <p class="ecran-nota" style="margin:0 0 10px">Butonul <strong>Scoate</strong> de pe fiecare rând
       deschide o previzualizare, nu șterge. Acolo se vede care act e care:
       <strong>dezactivarea</strong> e reversibilă (firma iese din listă, datele rămân),
       <strong>ștergerea</strong> nu e — și se poate doar dacă firma n-a produs niciun document.</p>
    <div class="firme-cautare">
      <label class="camp-eticheta" for="firme-q">Caut\u0103</label>
      <input type="text" id="firme-q" class="camp-input" placeholder="Caută după nume sau CUI" autocomplete="off">
    </div>
    <div class="firme-lista" id="firme-lista"><div class="ecran-nota">Se încarcă firmele…</div></div>
    <div id="firme-dezactivate"></div>
  `;

  container.querySelector("#firme-import-masa")?.addEventListener("click", () =>
    nav.deschide("Migrare cabinet", (c) => randeazaMigrare(c, nav), { nivel: "cabinet" }));

  container.querySelector("#firme-adauga").addEventListener("click", () => {
    nav.deschide("Adaugă firmă", (corp) => {  /* firma_noua_v1 */
      corp.innerHTML = `
        <div class="camp" style="margin-bottom:14px">
          <label class="camp-eticheta">CUI</label>
          <input class="camp-input" id="fn-cui" placeholder="RO12345678 sau 12345678" autocomplete="off">
          <p class="ecran-nota" id="fn-cui-info" style="margin:6px 0 0"></p>
        </div>
        <div class="camp" style="margin-bottom:14px">
          <label class="camp-eticheta">Denumire firmă</label>
          <input class="camp-input" id="fn-nume" placeholder="Se completează automat de la ANAF">
        </div>
        <div class="camp" style="margin-bottom:14px">
          <label class="camp-eticheta">Tip firmă</label>
          <select class="camp-input" id="fn-tip">
            <option value="srl" selected>SRL / SA (partidă dublă)</option>
            <option value="pfa">PFA / II / IF / profesii liberale (partidă simplă)</option>
          </select>
          <p class="camp-ajutor">Tipul <strong>nu se mai poate schimba</strong> după creare: determină sistemul contabil (partidă dublă sau simplă) și, odată introduse date, acestea nu pot fi mutate în celălalt regim. Verifică înainte de a continua.</p>
        </div>
        <div class="camp" style="margin-bottom:14px">
          <label class="camp-eticheta">Email client (primește automat acces la portal)</label>
          <input class="camp-input" id="fn-email" type="email" placeholder="Opțional: emailul patronului — primește acces în portal" autocomplete="off">
        </div>
        <button class="buton-primar" id="fn-salveaza" disabled>Adaugă firma</button>
      `;
      const cui = corp.querySelector("#fn-cui"), nume = corp.querySelector("#fn-nume");
      const info = corp.querySelector("#fn-cui-info"), btn = corp.querySelector("#fn-salveaza");
      let t = null, ultimAnaf = "";  /* [F188] non-suprascriere: retine ultima denumire pusa de ANAF */
      cui.addEventListener("input", () => {
        clearTimeout(t); btn.disabled = true; info.textContent = "";
        const v = cui.value.replace(/\D/g, "");
        if (v.length < 6) return;
        t = setTimeout(async () => {  /* debounce 500ms: un apel per CUI, nu pe fiecare tasta (rate limit ANAF) */
          info.textContent = "Verific la ANAF...";
          try {
            const r = await api.get("/public/verifica-cui/" + v);
            if (r && r.gasit) {
              // [F188] SUGEREAZA, nu suprascrie orb: completeaza doar daca campul e gol sau neatins de user
              // de la ultima pre-completare ANAF (userul poate corecta datele stale ANAF fara sa i se piarda).
              if (!nume.value.trim() || nume.value === ultimAnaf) { nume.value = r.denumire; ultimAnaf = r.denumire; }
              info.textContent = "Din ANAF: " + r.denumire + " — verifică. Adresa/CAEN/Reg.Com./TVA se preiau la creare.";
              btn.disabled = false;
            } else { info.textContent = "CUI negăsit la ANAF. Poți completa denumirea manual."; btn.disabled = false; }
          } catch (e) {
            info.textContent = "Nu am putut verifica la ANAF acum. Completează denumirea manual.";
            btn.disabled = false;
          }
        }, 500);
      });
      nume.addEventListener("input", () => { if (nume.value.trim().length > 2 && cui.value.replace(/\D/g,"").length >= 6) btn.disabled = false; });
      btn.addEventListener("click", async () => {
        const emailCl = corp.querySelector("#fn-email").value.trim();  /* firma_email_optional_v1 */
        if (emailCl && !emailCl.includes("@")) { info.innerHTML = '<span class="msg-eroare">Emailul nu pare valid. Lasă gol dacă nu inviți pe nimeni acum.</span>'; return; }
        btn.disabled = true; btn.textContent = "Se creează...";
        try {
          const rT = await api.post("/tenants", { nume: nume.value.trim(), cui: cui.value.replace(/\D/g, ""), tip_firma: corp.querySelector("#fn-tip").value });  /* [tip_firma_v1] */
          if (emailCl) await api.post(`/tenants/${rT.tenant_id}/client-acces`, { email: emailCl, nume: "" });
          /* [26.08.2026] Crearea SE CONFIRMA. Pana azi formularul se inchidea in tacere, iar
             omul nu putea sti daca a mers — deci apasa din nou. A doua apasare era refuzata
             corect de poarta de CUI duplicat, iar refuzul ARATA ca si cum ar fi fost ignorat:
             firma exista deja, fiindca prima apasare o crease. Cauza n-a fost poarta, ci
             tacerea de dupa succes. Exercitat pe date 26.08: doua firme create in 4 minute. */
          nav.inapoi();
          await incarcaFirme();   /* [27.08.2026] era `incarca()` — nedefinita in scopul asta */
          _bannerFirmaCreata(nume.value.trim());
        } catch (e) {
          info.textContent = e.mesaj || e.message || "Eroare la creare.";
          btn.disabled = false; btn.textContent = "Adaugă firma";
        }
      });
    });
  });

  const lista = container.querySelector("#firme-lista");
  const cautare = container.querySelector("#firme-q");
  const zonaDez = container.querySelector("#firme-dezactivate");
  let toate = [], dezactivate = [], scoase = [];

  function deseneaza(filtru) {
    const f = (filtru || "").trim().toLowerCase();
    const vizibile = toate.filter((t) =>
      !f || (t.nume || "").toLowerCase().includes(f) || String(t.cui || "").includes(f)
    );
    if (toate.length === 0) {
      lista.innerHTML = `<div class="firme-gol">Nicio firmă încă. Adaugă prima firmă din portofoliu.</div>`;
      return;
    }
    if (vizibile.length === 0) {
      lista.innerHTML = `<div class="firme-gol">Nicio firmă nu se potrivește cu „${filtru}".</div>`;
      return;
    }
    lista.innerHTML = "";
    vizibile.forEach((t) => {
      // [R78, 27.08.2026] Decizia de a scoate o firmă se ia UNDE VEZI PORTOFOLIUL, nu după ce
      // intri în firmă și derulezi 26 de carduri de lucru. Măsurat înainte: butonul de dinainte
      // stătea la 1361 px într-o fereastră de 793 — exista, dar nu se găsea.
      // Un <button> nu poate conține alt <button>. Iar `button.firme-rand` e selectorul pe care
      // stau 36 de fișiere (`w_auth` și toată infra vizuală), deci randul RĂMÂNE buton: acțiunea
      // se așază lângă el, într-un înveliș. Se schimbă împrejurimea, nu rândul.
      const linie = document.createElement("div");
      linie.className = "firme-rand-linie";
      const deschide = document.createElement("button");
      deschide.className = "firme-rand";
      deschide.innerHTML = `
        <div class="firme-rand-text">
          <div class="firme-rand-nume">${esc(t.nume) || "(fără nume)"}</div>
          <div class="firme-rand-cui">CUI ${esc(String(t.cui || "—"))}</div>
        </div>
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#9aa3af" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>
      `;
      deschide.addEventListener("click", () => deschideFirma(t, nav));
      const scoate = document.createElement("button");
      scoate.className = "buton-secundar firme-rand-scoate";
      scoate.textContent = "Scoate";
      scoate.title = "Scoate firma din portofoliu — se deschide o previzualizare, nu se șterge de aici";
      // NU șterge de aici: un act ireversibil la un click de listă e prea aproape. Deschide
      // ACELAȘI ecran de previzualizare, cu confirmarea pe CUI.
      scoate.addEventListener("click", (ev) => {
        ev.stopPropagation();
        nav.deschide("Scoate firma", (c2) => ecranScoateFirma(c2, nav, t));
      });
      linie.appendChild(deschide);
      linie.appendChild(scoate);
      lista.appendChild(linie);
    });
  }

  cautare.addEventListener("input", () => deseneaza(cautare.value));

  // [R72] O firmă cu evidență nu se șterge — se dezactivează. Dacă ar ieși din listă fără nicio
  // cale de întoarcere, dezactivarea ar fi o ușă cu sens unic. De aceea lista se cere cu
  // `inactive=true` și se desparte aici: portofoliul de lucru sus, cele scoase din lucru jos.
  async function incarcaFirme() {
    try {
      const r = await api.get("/tenants?inactive=true");
      const lst = (r && r.tenants) || [];
      toate = lst.filter((t) => t.activ !== false);
      dezactivate = lst.filter((t) => t.activ === false);
    } catch {
      lista.innerHTML = `<div class="firme-gol">Firmele nu au putut fi încărcate.</div>`;
      return;
    }
    try { scoase = ((await api.get("/firme-scoase")) || {}).firme || []; } catch { scoase = []; }
    deseneaza(cautare.value);
    deseneazaDezactivate();
  }

  function deseneazaDezactivate() {
    if (!zonaDez) return;
    if (!dezactivate.length && !scoase.length) { zonaDez.innerHTML = ""; return; }
    zonaDez.innerHTML = `
      <div class="firme-cap" style="margin-top:18px">
        <span class="firme-spatiu"></span>
        ${dezactivate.length ? `<button class="buton-secundar" id="firme-vezi-dez">Firme dezactivate (${dezactivate.length})</button>` : ""}
        ${scoase.length ? `<button class="buton-secundar" id="firme-vezi-scoase">Firme scoase (${scoase.length})</button>` : ""}
      </div>`;
    // [27.08.2026] O urmă pe care n-o poate deschide nimeni fără `psql` nu e urmă pentru cabinet,
    // e urmă pentru administratorul serverului. (Costin) După o ștergere, asta e singura dovadă
    // că firma a existat.
    zonaDez.querySelector("#firme-vezi-scoase")?.addEventListener("click", () =>
      nav.deschide("Firme scoase", (c3) => randeazaFirmeScoase(c3, scoase)));
    zonaDez.querySelector("#firme-vezi-dez")?.addEventListener("click", () =>
      nav.deschide("Firme dezactivate", (c2) => {
        c2.innerHTML = `
          <p class="ecran-nota">Firmele de aici nu apar în portofoliul de lucru. Documentele lor
             au rămas neatinse; reactivarea le aduce înapoi exact cum erau.</p>
          <div class="firme-lista" id="fd-lista"></div>
          <div id="fd-mesaj"></div>`;
        const zl = c2.querySelector("#fd-lista"), zm = c2.querySelector("#fd-mesaj");
        zl.innerHTML = "";
        dezactivate.forEach((t) => {
          const rand = document.createElement("div");
          rand.className = "firme-rand";
          rand.innerHTML = `
            <div class="firme-rand-text">
              <div class="firme-rand-nume">${esc(t.nume) || "(fără nume)"}</div>
              <div class="firme-rand-cui">CUI ${esc(String(t.cui || "—"))}</div>
            </div>`;
          const b = document.createElement("button");
          b.className = "buton-secundar";
          b.textContent = "Reactivează";
          b.addEventListener("click", async () => {
            b.disabled = true;
            try {
              await api.post(`/tenants/${t.id}/activare`, { activ: true });
              arataMesaj(zm, `„${t.nume}" e din nou în portofoliu.`, "ok");
              await incarcaFirme();
              nav.inapoi();
            } catch (e) {
              b.disabled = false;
              arataMesaj(zm, e.mesaj || e.message || "Nu am putut reactiva firma.", "eroare");
            }
          });
          rand.appendChild(b);
          zl.appendChild(rand);
        });
      }));
  }

  incarcaFirme();
}

// [nume_anaf_v1, 27.08.2026] Denumirea din aplicație lângă cea de la ANAF.
// Decizia lui Costin, varianta (b): numele rămâne EDITABIL, dar instantaneul ANAF se păstrează cu
// data lui, iar divergența se ARATĂ. Varianta (a) — câmp needitabil — ar fi blocat firmele pe care
// ANAF nu le întoarce: „un câmp needitabil care nu se poate completa e mai rău decât unul editabil
// greșit."
// Precedentul e în aceeași aplicație: `platitor_tva` lângă `platitor_tva_anaf` + data lui.
const _NUME_ANAF_ZILE_STATUT = 180;

function _numeNrm(s) {
  return String(s || "").trim().replace(/\s+/g, " ").toLocaleLowerCase("ro");
}

// -> null (nimic de arătat) | {fel: "divergenta"|"veche", anaf, zile}
function _divergentaNume(t) {
  const anaf = (t && t.nume_anaf) || "";
  if (!anaf || !_numeNrm(anaf) || _numeNrm(anaf) === _numeNrm(t.nume)) return null;
  // [R77] Dacă întrebarea a primit deja răspuns, nu se mai pune — până când ANAF spune altceva.
  // O citire ANAF mai NOUĂ decât alegerea o redeschide: alegerea de azi nu acoperă o denumire
  // schimbată la registru mâine.
  if (t.nume_ales_la) {
    const ales = new Date(t.nume_ales_la), citit = t.nume_anaf_la ? new Date(t.nume_anaf_la) : null;
    if (!citit || isNaN(citit) || citit <= ales) return null;
  }
  // `nume_anaf_la` decide când e stătut: „o denumire ANAF veche de un an nu e divergență, e o
  // măsurătoare veche" (Costin). Fără dată, nu se poate spune — și atunci se spune asta.
  const la = t.nume_anaf_la ? new Date(t.nume_anaf_la) : null;
  const zile = la && !isNaN(la) ? Math.floor((Date.now() - la.getTime()) / 864e5) : null;
  return { fel: (zile === null || zile <= _NUME_ANAF_ZILE_STATUT) ? "divergenta" : "veche",
           anaf, zile };
}

function _randDivergentaNume(corp, nav, t) {
  const d = _divergentaNume(t);
  if (!d) return;
  const zona = document.createElement("div");
  if (d.fel === "veche") {
    zona.className = "caseta-info";
    zona.innerHTML = `<p style="margin:0">Ultima denumire văzută la ANAF era
      <strong>${esc(d.anaf)}</strong>, dar măsurătoarea are ${d.zile} de zile — <strong>nu e o
      divergență, e o citire veche</strong>. Se reîmprospătează la următoarea verificare de CUI.</p>`;
  } else {
    // [R77, 27.08.2026] AMÂNDOUĂ butoanele, niciunul implicit. Costin: „«a păstra pe a ta = a nu
    // face nimic» nu e o alegere. Cine nu apasă nimic nu decide — moștenește ce era acolo, și nu
    // află niciodată că a fost o divergență." Deci și „păstrez denumirea mea" e un act care scrie.
    zona.className = "caseta-atentie";
    zona.innerHTML = `
      <div class="ca-mesaj"><strong>Două denumiri, și trebuie aleasă una.</strong> Denumirea din
        aplicație diferă de cea de la ANAF${
        d.zile !== null ? ` (citită acum ${d.zile === 0 ? "azi" : d.zile + " zile"})` : ""}:
        <br>· în aplicație: <strong>${esc(t.nume || "")}</strong>
        <br>· la ANAF: <strong>${esc(d.anaf)}</strong>
        <br>Denumirea din aplicație e cea folosită în documente. Alegerea se consemnează — dacă
        ANAF va spune altceva mai târziu, întrebarea se pune din nou.</div>
      <div class="ca-actiuni">
        <button class="buton-secundar" id="dn-ia-anaf">Ia denumirea de la ANAF</button>
        <button class="buton-secundar" id="dn-pastrez">Păstrez denumirea mea</button>
      </div>`;
  }
  corp.insertBefore(zona, corp.children[1] || null);

  const alege = async (id, alegere, textLucru, textInapoi) => {
    const b = zona.querySelector(id);
    if (!b) return;
    b.addEventListener("click", async () => {
      zona.querySelectorAll("button").forEach((x) => { x.disabled = true; });
      b.textContent = textLucru;
      try {
        await api.post(`/tenants/${t.id}/nume-ales`, { alege: alegere });
        nav.acasa();
        nav.setFirmaInLucru("");
      } catch (e) {
        zona.querySelectorAll("button").forEach((x) => { x.disabled = false; });
        b.textContent = textInapoi;
        const m = document.createElement("p");
        m.className = "msg-eroare";
        m.textContent = e.mesaj || e.message || "Nu am putut consemna alegerea.";
        zona.appendChild(m);
      }
    });
  };
  alege("#dn-ia-anaf", "anaf", "Se schimbă…", "Ia denumirea de la ANAF");
  alege("#dn-pastrez", "aplicatie", "Se consemnează…", "Păstrez denumirea mea");
}

// deschide o firmă: setează "În lucru" + spațiul de lucru (meniu de acțiuni)
export function deschideFirma(t, nav) {   // [P2] reutilizat din termene.js — deschide fisa firmei
  nav.setFirmaInLucru(t.nume || "");
  nav.deschide((t.nume || "Firmă") + " \u00b7 CUI " + (t.cui || ""), (corp) => meniuFirma(corp, nav, t), { lat: "larg" });
}

// meniul de acțiuni pe o firmă (facturi activ; restul se activează pe rând)
function meniuFirma(corp, nav, t) {
  const optiuni = [
    { cheie: "facturi", regim: "ambele", titlu: "Facturi", desc: "Emite și vezi facturile firmei",
      ...CULORI_CARD.albastru,
      icon: '<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 13h6M9 17h4"/>', activ: true },
    { cheie: "produse", regim: "ambele", titlu: "Produse", desc: "Nomenclator cu cote TVA, potrivire AI",
      icon: '<path d="M21 8l-9-5-9 5 9 5 9-5z"/><path d="M3 8v8l9 5 9-5V8"/><path d="M12 13v8"/>', activ: true },  // [produse_firma_v1]
    { cheie: "declaratii", regim: "ambele", titlu: "Declarații", desc: "D112, D300, D101 și restul",
      ...CULORI_CARD.verde,
      icon: '<path d="M9 13h6M9 17h4M9 9h1"/><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/>', activ: true },
    { cheie: "control", regim: "ambele", titlu: "Control fiscal", desc: "Semafor conformare pe firmă",
      ...CULORI_CARD.teal,
      icon: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>', activ: true },
    { cheie: "salariati", regim: "ambele", titlu: "Salariați", desc: "Stat plată, fluturași, D112",
      ...CULORI_CARD.piersica,
      icon: '<circle cx="9" cy="7" r="3"/><path d="M2 21v-1a6 6 0 0 1 12 0v1"/><path d="M16 3.5a3 3 0 0 1 0 7M22 21v-1a6 6 0 0 0-4-5.7"/>', activ: true },
    { cheie: "bonuri", regim: "ambele", titlu: "Bonuri și chitanțe", desc: "Pozate de client \u2014 certifică și contează",
      ...CULORI_CARD.piersica,
      icon: '<path d="M9 11l3 3 8-8"/><path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>', activ: true },
    { cheie: "jurnal", regim: "dubla", titlu: "Registru jurnal", desc: "Notele contabile ale firmei",
      ...CULORI_CARD.ardezie,
      icon: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>', activ: true },
    { cheie: "raportz", regim: "ambele", titlu: "Raport Z", desc: "Încasări zilnice \u2192 notă automată",
      ...CULORI_CARD.chihlimbar,
      icon: '<path d="M4 4h16M4 4l16 16M4 20h16"/>', activ: true },
    { cheie: "stocuri", regim: "dubla", titlu: "Stocuri", desc: "NIR, adaos, desc\u0103rcare gestiune",
      ...CULORI_CARD.chihlimbar,
      icon: '<path d="M21 8l-9-5-9 5v8l9 5 9-5V8z"/><path d="M3 8l9 5 9-5M12 13v8"/>', activ: true },
    { cheie: "balanta", regim: "dubla", titlu: "Balan\u021b\u0103 de verificare", desc: "PDF lunar, solduri și rulaje",
      ...CULORI_CARD.albastru,
      icon: '<path d="M12 3v18M3 7h18M6 7l-3 5h6l-3-5zM18 7l-3 5h6l-3-5z"/>', activ: true },
    { cheie: "bilant", regim: "dubla", titlu: "Bilan\u021b anual", desc: "S1005 micro / S1003 mici, validare ANAF",
      ...CULORI_CARD.albastru,
      icon: '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>', activ: true },
    { cheie: "casa", regim: "ambele", titlu: "Cas\u0103", desc: "Registru de cas\u0103, plafoane numerar",
      ...CULORI_CARD.verde,
      icon: '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M6 12h.01M18 12h.01"/>', activ: true },
    { cheie: "etransport", regim: "ambele", titlu: "e-Transport", desc: "Notificare UIT, XML pentru SPV",
      ...CULORI_CARD.chihlimbar,
      icon: '<path d="M1 8h13v8H1zM14 11h4l3 3v2h-7z"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>', activ: true },
    { cheie: "operatiuni", regim: "dubla", titlu: "Operațiuni speciale", desc: "Leasing, marjă, IC, sponsorizări și altele",
      ...CULORI_CARD.violet,
      icon: '<path d="M12 2l2 4 4 .5-3 3 .8 4.5L12 12l-3.8 2 .8-4.5-3-3 4-.5z"/><path d="M5 18h14M5 21h14"/>', activ: true },
    { cheie: "mijloace", regim: "dubla", titlu: "Mijloace fixe", desc: "Registrul activelor: valoare, amortizat, casare, reevaluare",
      ...CULORI_CARD.chihlimbar,
      icon: '<rect x="3" y="4" width="18" height="6" rx="1"/><path d="M5 10v10h14V10"/><path d="M9 14h6M12 10v10"/>', activ: true },
    { cheie: "rip", regim: "simpla", titlu: "Încasări/plăți", desc: "Partidă simplă PFA/II/IF, Fișă D212",
      ...CULORI_CARD.verde,
      icon: '<path d="M12 2v20M17 7H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>', activ: true },
    { cheie: "banca", regim: "ambele", titlu: "Banc\u0103", desc: "Import extras, propuneri contare",
      ...CULORI_CARD.albastru,
      icon: '<path d="M3 21h18M4 18h16M6 18V9M10 18V9M14 18V9M18 18V9M2 9l10-6 10 6"/>', activ: true },
    { cheie: "magazin", regim: "ambele", titlu: "Magazin online", desc: "WooCommerce \u2192 facturi automate",
      ...CULORI_CARD.violet,
      icon: '<circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>', activ: true },  // wc_fe_v1
    { cheie: "verificari", regim: "ambele", titlu: "Verific\u0103ri", desc: "Echilibru, trezorerie, TVA",
      ...CULORI_CARD.albastru,
      icon: '<path d="M9 11l3 3 8-8"/><path d="M21 12v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h11"/>', activ: true },
    { cheie: "solicitari", regim: "ambele", titlu: "Solicitări client", desc: "Mesaje primite de la firma-client",
      ...CULORI_CARD.piersica,
      icon: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>', activ: true },
    { cheie: "acces", regim: "ambele", titlu: "Acces client", desc: "Invită clientul în portal",
      ...CULORI_CARD.verde,
      icon: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M19 8v6"/><path d="M22 11h-6"/>', activ: true },
    { cheie: "import", regim: "ambele", titlu: "Import date", desc: "Toate straturile de migrare, pentru aceast\u0103 firm\u0103",
      ...CULORI_CARD.albastru,
      icon: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>', activ: true },
    // [date_firma_v1] Datele pe care ANAF le cere in declaratii (CUI, denumire, CAEN,
    // adresa, banca, IBAN, telefon, reg.com). Pana acum nu se puteau completa din
    // interfata deloc - firma_profil_api salva doar font/culoare/logo. O firma noua
    // nu putea depune nimic pana nu se intervenea direct in baza de date.
    { cheie: "datefirma", regim: "ambele", titlu: "Date firm\u0103", desc: "Datele cerute de ANAF \u00een declara\u021bii",
      ...CULORI_CARD.ardezie,
      icon: '<path d="M3 21h18"/><path d="M5 21V7l8-4v18"/><path d="M19 21V11l-6-4"/><path d="M9 9v.01M9 12v.01M9 15v.01M9 18v.01"/>', activ: true },
    { cheie: "rapoarte", regim: "ambele", titlu: "Rapoarte comerciale", desc: "Vânzări pe partener, durata de încasare, fișă client",  // rap_com_v1
      ...CULORI_CARD.violet,
      icon: '<path d="M3 3v18h18"/><rect x="7" y="10" width="3" height="7"/><rect x="12" y="6" width="3" height="11"/><rect x="17" y="13" width="3" height="4"/>', activ: true },
    { cheie: "registratura", regim: "ambele", titlu: "Registratură", desc: "Numere de intrare/ieșire pe documente",  // registratura_v1
      ...CULORI_CARD.ardezie,
      icon: '<path d="M4 4h11l5 5v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z"/><path d="M14 4v5h5"/><path d="M8 13h6M8 16h6"/>', activ: true },
    { cheie: "contracte", regim: "ambele", titlu: "Contracte", desc: "Generează din șabloane cu datele partenerului",  // contracte_v1
      ...CULORI_CARD.ardezie,
      icon: '<path d="M4 4h11l5 5v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z"/><path d="M14 4v5h5"/><path d="M9 13l2 2 4-4"/>', activ: true },
    { cheie: "centrecost", regim: "dubla", titlu: "Centre de cost", desc: "Dimensiune pe notele manuale, pentru raport realizat pe centru",  // [F143]
      ...CULORI_CARD.teal,
      icon: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>', activ: true },
  ];

  // [regim_card 23.07] Vizibilitatea cardurilor deriva prin regim_contabil (O SURSA, ca STRATURI_META), NU din
  // liste hardcodate DOAR_SRL/DOAR_PFA (a 4-a sursa paralela la aceeasi intrebare, eliminata - dupa termene,
  // semafor, neaplicabile_forma). Fiecare card declara `regim` OBLIGATORIU (ambele/simpla/dubla) - garda CARD_REGIM
  // in verificator il impune (fara default tacit). Contract STRICT pe t.regim_contabil (expus de backend,
  // auth_api:409): daca lipseste -> esec VIZIBIL, nu degradare tacita la "doar ambele" (doctrina P2: meniuFirma cu
  // tip_firma). 'declaratii'=ambele (PFA datoreaza D112/D300/...; D100/D101/D406 dezactivate in dropdown prin G1).
  // Casa=ambele (Legea 70/2015 plafon PFA). Vezi DESIGN_SYSTEM cap.18 + DECIZII 23.07.
  const regimFirma = t.regim_contabil;
  if (regimFirma !== "simpla" && regimFirma !== "dubla") {
    throw new Error("regim_contabil lipsa/invalid pe firma (" + regimFirma + ") — contract strict, nu degradez tacit");
  }
  const vizibile = optiuni.filter((o) => o.regim === "ambele" || o.regim === regimFirma);

  // [antet_explicit 23.07] Antetul firmei (nume · CUI) se randeaza EXPLICIT aici, nu se lasa pe seama
  // auto-h2 din navigator (_steaza: prepend <h2 class="pf-titlu"> prin MutationObserver DACA corpul n-are
  // deja unul). Dependenta de auto-h2 e fragila (observer + euristica "fara h2" + timing). Textul e IDENTIC
  // cu titlul ferestrei pasat de deschideFirma, deci conditia !querySelector("h2") din _steaza devine falsa
  // si antetul NU se dubleaza. Robustete, nu schimbare vizuala (DS cap.9: antetul = titlul ecranului).
  const antetFirma = (t.nume || "Firmă") + " · CUI " + (t.cui || "");
  corp.innerHTML = `
    <h2 class="pf-titlu">${esc(antetFirma)}</h2>
    <div class="firme-optiuni">
      ${vizibile.map((o) => `
        <button class="firme-optiune" id="fa-${o.cheie}"${o.activ ? "" : ' disabled style="opacity:.55;cursor:default"'}>
          <div class="firme-optiune-icon" style="background:${o.bg}; color:${o.fg}">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${o.icon}</svg>
          </div>
          <div class="firme-optiune-titlu">${o.titlu}</div>
          <div class="firme-optiune-desc">${o.desc}${o.activ ? "" : " \u00b7 \u00een cur\u00e2nd"}</div>
        </button>`).join("")}
    </div>
    <div class="firme-scoatere" style="margin-top:24px;padding-top:14px;border-top:1px solid #e5e7eb">
      <button class="buton-secundar" id="firma-scoate">Scoate firma din portofoliu</button>
      <p class="ecran-nota" style="margin:8px 0 0">Două acte diferite, în același loc:
         <strong>dezactivarea</strong> e reversibilă (firma iese din listă, datele rămân),
         <strong>ștergerea</strong> nu e (firma dispare cu totul, și se poate doar dacă n-a produs
         niciun document). Ecranul următor spune care se poate și de ce.</p>
    </div>`;

  _randDivergentaNume(corp, nav, t);   // [nume_anaf_v1]

  const bScoate = corp.querySelector("#firma-scoate");
  if (bScoate) bScoate.addEventListener("click", () =>
    nav.deschide("Scoate firma", (c2) => ecranScoateFirma(c2, nav, t)));

  const bAcces = corp.querySelector("#fa-acces");
  if (bAcces) bAcces.addEventListener("click", () => nav.deschide("Acces client", (c2) => ecranAccesClient(c2, nav, t)));
  const bFacturi = corp.querySelector("#fa-facturi");
  if (bFacturi) {
    bFacturi.addEventListener("click", () => {
      nav.deschide("Facturi", (c2) => randeazaFacturi(c2, nav, t.id, {}), { lat: "larg" }); /* facturi_larg_v1 */
    });
    // [f131] alerta in aplicatie: badge cu nr. de facturi restante pe cardul Facturi
    // (tiparul cab-card-badge din cabinet.js). Nu blocheaza randarea - se ataseaza cand vine raspunsul.
    (async () => {
      try {
        const r = await api.get(`/tenants/${t.id}/scadentar`);
        const n = (r && r.rezumat && r.rezumat.restanta) || 0;
        if (n > 0) {
          const b = document.createElement("span");
          b.className = "cab-card-badge";
          b.textContent = n;
          b.title = `${n} factur${n === 1 ? "ă" : "i"} restant${n === 1 ? "ă" : "e"}`;
          bFacturi.style.position = "relative";
          bFacturi.appendChild(b);
        }
      } catch { /* scadentarul e best-effort pt badge; nu rupe cardul */ }
    })();
  }
  const bSalariati = corp.querySelector("#fa-salariati");
  if (bSalariati && !bSalariati.disabled) {
    bSalariati.addEventListener("click", () => { nav.deschide("Salariați", (c2) => ecranSalariati(c2, nav, t)); });
  }
  const bDateFirma = corp.querySelector("#fa-datefirma");  // [date_firma_v1]
  if (bDateFirma && !bDateFirma.disabled) {
    bDateFirma.addEventListener("click", () => { nav.deschide("Date firm\u0103", (c2) => randeazaDateFirma(c2, nav, t.id)); });
  }
  const bProduse = corp.querySelector("#fa-produse");  // [produse_firma_v1]
  if (bProduse && !bProduse.disabled) {
    bProduse.addEventListener("click", () => { nav.deschide("Produse", (c2) => randeazaProduse(c2, nav, t.id)); });
  }
  const bDeclaratii = corp.querySelector("#fa-declaratii");  // [decl_firma_v1]
  if (bDeclaratii && !bDeclaratii.disabled) {
    bDeclaratii.addEventListener("click", () => { nav.deschide("Declara\u021bii", (c2) => declaratiiPerFirma(c2, nav, { tenant_id: t.id, nume: t.nume })); });
  }
  const bControl = corp.querySelector("#fa-control");
  if (bControl && !bControl.disabled) {
    bControl.addEventListener("click", () => { nav.deschide("Control fiscal", (c2) => ecranControlFirma(c2, nav, t)); });
  }
  const bBonuri = corp.querySelector("#fa-bonuri");
  if (bBonuri) {
    bBonuri.addEventListener("click", () => { nav.deschide("Bonuri și chitanțe", (c2) => ecranBonuri(c2, nav, t), { lat: "larg" }); });  /* bon_flux_e4_v1 */
  }
  const bJurnal = corp.querySelector("#fa-jurnal");
  if (bJurnal) {
    bJurnal.addEventListener("click", () => { nav.deschide("Registru jurnal", (c2) => ecranJurnal(c2, nav, t)); });
  }
  const bMagazin = corp.querySelector("#fa-magazin");  // wc_fe_v1
  if (bMagazin) {
    bMagazin.addEventListener("click", () => nav.deschide("Magazin online", (c2) => ecranMagazin(c2, nav, t.id)));
  }
  const bZ = corp.querySelector("#fa-raportz");
  if (bZ) {
    bZ.addEventListener("click", () => { nav.deschide("Raport Z", (c2) => ecranRaportZ(c2, nav, t)); });
  }
  const bBilant = corp.querySelector("#fa-bilant");
  if (bBilant) {
    bBilant.addEventListener("click", () => { nav.deschide("Bilanț", (c2) => ecranBilant(c2, nav, t)); });
  }
  const bStocuri = corp.querySelector("#fa-stocuri");
  if (bStocuri) {
    bStocuri.addEventListener("click", () => { nav.deschide("Stocuri", (c2) => ecranStocuri(c2, nav, t)); });
  }
  const bCasa = corp.querySelector("#fa-casa");
  if (bCasa) {
    bCasa.addEventListener("click", () => { nav.deschide("Casă", (c2) => ecranCasa(c2, nav, t), { lat: "larg" }); });
  }
  const bRip = corp.querySelector("#fa-rip");
  if (bRip) bRip.addEventListener("click", () => { nav.deschide("Încasări/plăți", (c2) => ecranRip(c2, nav, t)); });
  const bOperatiuni = corp.querySelector("#fa-operatiuni");
  if (bOperatiuni) bOperatiuni.addEventListener("click", () => { nav.deschide("Operațiuni speciale", (c2) => ecranOperatiuni(c2, nav, t)); });
  const bMijloace = corp.querySelector("#fa-mijloace");  // [ecran_mf_v1]
  if (bMijloace) bMijloace.addEventListener("click", () => { nav.deschide("Mijloace fixe", (c2) => ecranMijloace(c2, nav, t.id)); });
  const bEtransport = corp.querySelector("#fa-etransport");
  if (bEtransport) bEtransport.addEventListener("click", () => { nav.deschide("e-Transport", (c2) => ecranEtransport(c2, nav, t)); });
  const bBalanta = corp.querySelector("#fa-balanta");
  if (bBalanta) bBalanta.addEventListener("click", () => { nav.deschide("Balanță de verificare", (c2) => ecranBalanta(c2, nav, t)); });
  const bRapoarte = corp.querySelector("#fa-rapoarte");  // rap_com_v1
  if (bRapoarte) bRapoarte.addEventListener("click", () => { nav.deschide("Rapoarte comerciale", (c2) => ecranRapoarte(c2, nav, t), { lat: "larg" }); });
  const bRegistratura = corp.querySelector("#fa-registratura");  // registratura_v1
  if (bRegistratura) bRegistratura.addEventListener("click", () => { nav.deschide("Registratură", (c2) => ecranRegistratura(c2, nav, t)); });
  const bContracte = corp.querySelector("#fa-contracte");  // contracte_v1
  if (bContracte) bContracte.addEventListener("click", () => { nav.deschide("Contracte", (c2) => ecranContracte(c2, nav, t)); });
  const bCentre = corp.querySelector("#fa-centrecost");  // [F143]
  if (bCentre) bCentre.addEventListener("click", () => { nav.deschide("Centre de cost", (c2) => ecranCentreCost(c2, nav, t)); });
  const bBanca = corp.querySelector("#fa-banca");
  if (bBanca) {
    bBanca.addEventListener("click", () => { nav.deschide("Bancă", (c2) => ecranBanca(c2, nav, t)); });
  }
  const bVerif = corp.querySelector("#fa-verificari");
  if (bVerif) {
    bVerif.addEventListener("click", () => { nav.deschide("Verificări", (c2) => ecranVerificari(c2, nav, t)); });
  }
  const bSolicitari = corp.querySelector("#fa-solicitari");
  if (bSolicitari) {
    bSolicitari.addEventListener("click", () => {
      ecranSolicitariCabinet(corp, nav, t);
    });
  }
  const bImport = corp.querySelector("#fa-import");
  if (bImport) {
    bImport.addEventListener("click", () => {
      nav.mergi("Import date", (c) => meniuMigrarePerFirma(c, nav, { tenant_id: t.id, nume: t.nume, tip_firma: t.tip_firma }));  // entitatea e in antet (DS cap.1), nu in titlu. tip_firma -> pasul RIP doar la PFA
    });
  }
}


async function ecranSolicitariCabinet(corp, nav, t) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
  await randeazaSolicitariCabinet(corp, nav, t);
}

async function randeazaSolicitariCabinet(corp, nav, t) {
  let lista = [];
  try {
    const r = await api.get(`/tenants/${t.id}/solicitari`);
    lista = (r && r.solicitari) || [];
  } catch { corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca mesajele.</p>`; return; }
  let firHtml = '<div class="stare-goala">Niciun mesaj încă.</div>';
  if (lista.length) {
    firHtml = lista.map((s) => {
      const cine = s.autor_rol === "cabinet" ? "Tu" : "Client";
      return `<div class="sol-rand sol-${s.autor_rol === "cabinet" ? "client" : "cabinet"}">
        <div class="sol-mesaj">${s.mesaj}</div>
        <div class="sol-meta">${cine} · ${dataRo(s.creat_la)}</div>
      </div>`;
    }).join("");
  }
  corp.innerHTML = `
    <h2 class="pf-titlu">Solicitări</h2>
    <p class="pf-intro">Mesaje de la firma-client.</p>
    <div class="sol-fir" id="sol-fir">${firHtml}</div>
    <div class="sol-trimite">
      <textarea id="sol-input" placeholder="Scrie un răspuns..." rows="3"></textarea>
      <button class="buton-primar" id="sol-trimite-btn">Trimite</button>
    </div>
  `;
  const fir = corp.querySelector("#sol-fir");
  if (fir) fir.scrollTop = fir.scrollHeight;
  const btn = corp.querySelector("#sol-trimite-btn");
  if (btn) btn.addEventListener("click", async () => {
    const inp = corp.querySelector("#sol-input");
    const txt = ((inp && inp.value) || "").trim();
    if (!txt) return;
    try {
      await api.post(`/tenants/${t.id}/solicitari`, { mesaj: txt });
      await randeazaSolicitariCabinet(corp, nav, t);
    } catch (e) {
      /* [catch_scriere 27.07.2026] mesajul netrimis parea trimis. DS cap.6. */
      arataMesaj(corp, (e && e.mesaj) || "Nu am putut trimite mesajul.", "eroare");
    }
  });
}

// [verificari] Verificari coerenta pe firma: echilibru, trezorerie, TVA
// [paritate_randare 24.07] Inventar DECLARAT pt garda VERDICT_PARITATE (DS cap.20). ecranVerificari consuma vc
// BRUT de la /firme/{id}/verificari (pe luna) si alege chei pe NUME. Fiecare cheie vc PRODUSA de backend trebuie
// sa fie ori randata mai jos, ori ignorata AICI cu motiv — nu tacut (aceeasi clasa care ascundea salariile pe
// cardul din fisa). Citit ca TEXT de verificator_conformitate.py (paritate de randare, al doilea consumator), nu
// la runtime. Randare noua NU se adauga aici — doar declaratia; cross-check-urile raman exclusiv in verdict.
const VC_VERIFICARI = {
  echilibru:             "randat — Echilibru (partidă dublă pe perioadă + orfani + solduri inițiale), prin randEchilibru",
  trezorerie:            "randat — Trezorerie (solduri creditoare)",
  documente_pozate:      "randat — Documente pozate de clienți",
  tva:                   "randat — TVA (rezultat + sold)",
  note:                  "randat — contor de note contabile în antet",
  tva_incrucisat:        "IGNORAT — acest ecran arată doar coerența brută lunară; cross-check-urile declarație-vs-contabilitate aparțin exclusiv verdictului din Control fiscal (control_verdict.js)",
  d112_incrucisat:       "IGNORAT — idem (salarii D112 vs contabilitate)",
  d390_incrucisat:       "IGNORAT — idem (operațiuni intracomunitare D390 vs evidență)",
  cota_tva_conformitate: "IGNORAT — idem (cotă TVA facturi emise vs perioadă)",
};
// [R33 varianta b\u2032\u2032, 26.08.2026] «Echilibru» e UN rand pe ecran, dar DOUA verificari in spate,
// cu moduri de esec DISJUNCTE (partida dubla pe liniile perioadei + orfani; inchiderea soldurilor
// initiale). Costin: *"cele doua se arata ca una singura, cu ce a gasit fiecare. Contabilul nu
// trebuie sa stie ca sunt doua module."* Randorul NU decide nimic: primeste `constatari` ca OBIECTE
// cu cifre (DS cap.13) si le pune in cuvinte. Textul se DERIVA din `fel`, nu se alege aici (P13).
// De ce nu merge prin `rand()` generic: acela citeste `.cod`, iar verdictul compus n-are un singur
// cod \u2014 are o lista. Trecut prin `rand()`, un verdict ROSU fara `.cod` ar fi iesit VERDE.
function detaliuEchilibru(x) {
  if (x.fel === "ledger_dezechilibrat")
    return `partid\u0103 dubl\u0103 rupt\u0103: \u03a3 debit ${bani(x.sigma_debit)} vs \u03a3 credit ${bani(x.sigma_credit)} (diferen\u021b\u0103 ${bani(x.diferenta)} lei)`;
  if (x.fel === "orfani")
    return `${x.numar} linie(i) trimit la o \u00eenregistrare care nu exist\u0103`;
  if (x.fel === "solduri_dezechilibrate")
    return `solduri ini\u021biale: diferen\u021b\u0103 ${bani(x.diferenta_solduri)} lei`;
  if (x.fel === "neverificat")
    return `nu am putut verifica ${esc(x.ce || "")}${x.motiv ? " \u2014 " + esc(x.motiv) : ""}`;
  return esc(x.fel || "");
}
function randEchilibru(e) {
  if (!e) return "";
  const c = e.constatari || [];
  const necunoscut = c.some((x) => x.fel === "neverificat");
  const detaliu = e.ok ? "\u00een regul\u0103" : c.map(detaliuEchilibru).join(" \u00b7 ");
  // gri pentru necunoscut, rosu pentru problema gasita: necunoscutul NU se randeaza ca defect,
  // dar nici ca "in regula" (P6 \u2014 necunoscut domina favorabil, problema domina necunoscutul).
  const clasa = e.ok ? "pct-verde" : (necunoscut && !c.some((x) => x.fel !== "neverificat") ? "pct-info" : "pct-rosu");
  return `<div class="pf-frand">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">Echilibru</div>
          <div class="pf-frand-sub">${detaliu}</div>
        </div>
        <span class="cab-pct ${clasa}"></span>
      </div>`;
}

async function ecranVerificari(corp, nav, t) {
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se verifica...</p>`;
    let r = null;
    try { r = await api.get(`/firme/${t.id}/verificari?an=${an}&luna=${luna}`); } catch {}
    let vs = null;  // [verif_stocuri_v1]
    let intra = null;  // [intrastat_v1]
    try { intra = await api.get(`/tenants/${t.id}/intrastat-praguri?an=${an}`); } catch {}
    try { vs = await api.get(`/tenants/${t.id}/verificare-stocuri`); } catch {}
    const rand = (nume, obj) => {
      const ok = obj && (obj.ok === true || obj.cod === undefined) && !(Array.isArray(obj) && obj.length);
      const detaliu = ok ? "in regula" : (Array.isArray(obj) ? obj.map(p=>p.cod).join(", ") : (obj && obj.cod) || "problema");
      return `<div class="pf-frand">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${nume}</div>
          <div class="pf-frand-sub">${detaliu}</div>
        </div>
        <span class="cab-pct ${ok ? 'pct-verde' : 'pct-rosu'}"></span>
      </div>`;
    };
    corp.innerHTML = `
      <h2 class="pf-titlu">Verific\u0103ri</h2>
      <p class="pf-intro">Luna ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")} \u00b7 ${r ? r.note : 0} note contabile
        <button class="buton-secundar" id="vf-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="buton-secundar" id="vf-next">luna \u2192</button></p>
      <div class="pf-lista">
        ${r ? randEchilibru(r.echilibru) : ""}
        ${r ? rand("Trezorerie (f\u0103r\u0103 solduri creditoare)", r.trezorerie) : ""}
        ${r && r.documente_pozate ? `<div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">Documente pozate de clien\u021bi</div>
          <div class="pf-frand-sub">${r.documente_pozate.ok ? "\u00een regul\u0103" : [r.documente_pozate.bonuri_neverificate ? r.documente_pozate.bonuri_neverificate + " document(e) confirmate de client, necontate de peste 3 zile" : "", r.documente_pozate.ciorne_casa ? r.documente_pozate.ciorne_casa + " not\u0103(e) de cas\u0103 ciorn\u0103, nevalidate de peste 3 zile" : ""].filter(Boolean).join(" \u00b7 ")}</div>
        </div><span class="cab-pct ${r.documente_pozate.ok ? 'pct-verde' : 'pct-rosu'}"></span></div>` : ""}
        ${r ? `<div class="pf-frand"><div class="pf-frand-text"><div class="pf-frand-nume">TVA</div><div class="pf-frand-sub">${r.tva.rezultat === "de_plata" ? "de plat\u0103" : "de recuperat"}: ${bani(r.tva.suma)} lei (cont ${r.tva.cont})</div></div><span class="cab-pct pct-info"></span></div>` : ""}
        ${vs ? `<div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">Stocuri (contabil vs fi\u0219e CV)</div>
          <div class="pf-frand-sub">${vs.ok ? "in regula" : vs.conturi.filter(c=>!c.ok).map(c=>`cont ${c.cod || c.cont}: contabil ${bani(c.sold_contabil)} vs fi\u0219e ${bani(c.valoare_fise_cv)} (dif ${bani(c.diferenta)})`).join(" \u00b7 ")}</div>
        </div><span class="cab-pct ${vs.ok ? 'pct-verde' : 'pct-rosu'}"></span></div>` : ""}
        ${intra ? `<div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">Intrastat (prag 1.000.000 lei/flux, an ${an})</div>
          <div class="pf-frand-sub">Introduceri: ${intra.introduceri ? intra.introduceri.cumulat + " lei (" + intra.introduceri.procent + "%)" + (intra.introduceri.status !== "sub_prag" ? " \u00b7 DEPASIT din luna " + intra.introduceri.luna_depasirii : "") : "-"} \u00b7 Expedieri: ${intra.expedieri ? intra.expedieri.cumulat + " lei (" + intra.expedieri.procent + "%)" + (intra.expedieri.status !== "sub_prag" ? " \u00b7 DEPASIT din luna " + intra.expedieri.luna_depasirii : "") : "-"}</div>
        </div><span class="cab-pct ${(intra.introduceri && intra.introduceri.status !== 'sub_prag') || (intra.expedieri && intra.expedieri.status !== 'sub_prag') ? 'pct-rosu' : 'pct-verde'}"></span></div>` : ""}
        ${!r ? '<div class="ecran-nota">Nu am putut rula verific\u0103rile.</div>' : ""}
      </div>`;
    corp.querySelector("#vf-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#vf-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
  };
  deseneaza();
}

// [salariati] Stat de plata lunar + fluturasi

// [F137] lookup COR: input de cautare (cod sau denumire) -> lista rezultate din /cor -> selectie
// seteaza codul in inputul ascuns #<prefix>-cor. Valoarea se seteaza DOAR prin selectie (nu free-text),
// ca sa nu ajunga in DB un cod inexistent (backend valideaza si el). Refoloseste zona inline existenta.
function legaCorLookup(scope, prefix, codInitial, denInitial) {
  const cauta = scope.querySelector(`#${prefix}-cor-cauta`);
  const hid = scope.querySelector(`#${prefix}-cor`);
  const rez = scope.querySelector(`#${prefix}-cor-rez`);
  if (!cauta || !hid || !rez) return;
  if (codInitial) { hid.value = codInitial; cauta.value = denInitial ? `${codInitial} — ${denInitial}` : codInitial; }
  let timer;
  cauta.addEventListener("input", () => {
    hid.value = "";  // orice tastare invalideaza selectia anterioara pana la o noua alegere
    clearTimeout(timer);
    const q = cauta.value.trim();
    if (q.length < 2) { rez.innerHTML = ""; return; }
    timer = setTimeout(async () => {
      let list = [];
      try { const r = await api.get(`/cor?q=${encodeURIComponent(q)}`); list = (r && r.rezultate) || []; }
      catch { rez.innerHTML = ""; return; }
      rez.innerHTML = list.length
        ? list.map((o) => `<div class="cor-opt" data-cod="${o.cod}" data-den="${esc(o.denumire)}" style="padding:6px 8px;cursor:pointer;border-bottom:1px solid var(--linie)">${o.cod} — ${esc(o.denumire)}</div>`).join("")
        : `<div style="padding:6px 8px;color:var(--gri)">nicio ocupație găsită</div>`;
      rez.querySelectorAll("[data-cod]").forEach((el) => el.addEventListener("click", () => {
        hid.value = el.dataset.cod;
        cauta.value = `${el.dataset.cod} — ${el.dataset.den}`;
        rez.innerHTML = "";
      }));
    }, 300);
  });
}

function campCorLookup(prefix, obligatoriu) {
  return `<div class="camp"><label class="camp-eticheta" for="${prefix}-cor-cauta">Ocupație (COR)${obligatoriu ? '<span class="oblig">*</span>' : ""}</label>
    <input type="text" id="${prefix}-cor-cauta" class="camp-input" placeholder="cod sau denumire (ex. programator)" autocomplete="off">
    <input type="hidden" id="${prefix}-cor">
    <div id="${prefix}-cor-rez" style="max-height:180px;overflow:auto"></div></div>`;
}

function formularSalariatNou(corp, nav, t, dupaSalvare) {
  const camp = (id, eticheta, tip, extra) => {
    const optional = !(extra && extra.obligatoriu);
    if (tip === "select") {
      const optiuni = (extra.optiuni || []).map(([v, l]) => `<option value="${v}">${l}</option>`).join("");
      return `<div class="camp"><label class="camp-eticheta" for="sn-${id}">${eticheta}${optional ? "" : '<span class="oblig">*</span>'}</label><select id="sn-${id}" class="camp-input">${optiuni}</select></div>`;
    }
    if (tip === "checkbox") {
      return `<div class="camp"><label class="camp-eticheta" for="sn-${id}">${eticheta}</label><input type="checkbox" id="sn-${id}"></div>`;
    }
    const inputTip = tip === "numar" ? "number" : (tip === "data" ? "date" : "text");
    const pas = (extra && extra.pas) || "0.01";
    const restrictii = tip === "numar" ? ` step="${pas}" min="0"` : "";
    return `<div class="camp"><label class="camp-eticheta" for="sn-${id}">${eticheta}${optional ? "" : '<span class="oblig">*</span>'}</label><input type="${inputTip}"${restrictii} id="sn-${id}" class="camp-input"></div>`;
  };
  corp.innerHTML = `
    <h2 class="pf-titlu">Salariat nou</h2>
    <div class="grila-campuri">
      ${camp("nume", "Nume", "text", { obligatoriu: true })}
      ${camp("prenume", "Prenume", "text")}
      ${camp("cnp", "CNP", "text")}
      ${camp("data_angajare", "Data angaj\u0103rii", "data")}
      ${camp("data_incetare", "Data încetării (gol = activ)", "data")}
      ${camp("tip_norma", "Tip norm\u0103", "select", { optiuni: [["intreaga","\u00centreag\u0103"],["partiala","Par\u021bial\u0103"]] })}
      ${camp("ore_zi", "Ore/zi (norm\u0103 par\u021bial\u0103)", "numar", { pas: "0.5" })}
      ${camp("salariu_brut", "Salariu brut", "numar", { obligatoriu: true })}
      ${camp("persoane_intretinere", "Persoane \u00een \u00eentre\u021binere", "numar", { pas: "1" })}
      ${camp("data_nastere", "Data nașterii (pentru deducerea tinerilor sub 26 de ani)", "data")}
      ${camp("copii_scolarizati", "Copii ≤ 18 ani înscriși în învățământ (deducere 100 lei/copil)", "numar", { pas: "1" })}
      ${camp("declaratie_copii", "Declarația părintelui pentru copii (art.77) — fără ea deducerea nu se acordă", "checkbox")}
      ${camp("judet_casa", "Jude\u021b CAS/CASS", "text")}
      ${campCorLookup("sn", true)}
      ${camp("iban", "IBAN (cont salariu pe card)", "text")}
      ${camp("tichet_masa_valoare", "Tichet de mas\u0103 (lei/zi lucrat\u0103, 0 = f\u0103r\u0103)", "numar")}
      ${camp("scutit_contrib_minim", "Scutit contribu\u021bie minim\u0103", "checkbox")}
    </div>
    <div id="sn-prapastie"></div>
    <p style="margin-top:12px">
      <button class="buton-primar" id="sn-salveaza">Salveaz\u0103</button>
      <button class="buton-secundar" id="sn-gata" style="margin-left:6px">Gata, \u00eenapoi la list\u0103</button></p>
    <div id="sn-mesaj"></div>`;
  legaCorLookup(corp, "sn");  // [F137] lookup ocupatie COR

  // [R49 (c)] Prapastia salariului minim, cu CIFRE. Nu se calculeaza in ecran (P3): ecranul
  // trimite elementele completate si afiseaza ce intoarce serverul. Apare INAINTE de buton
  // (DS cap.6, ghidaj preventiv), si dispare cand nu se aplica.
  const zonaPrapastie = corp.querySelector("#sn-prapastie");
  let ceasPrapastie = null;
  async function verificaPrapastia() {
    if (!zonaPrapastie) return;
    const brut = Number(corp.querySelector("#sn-salariu_brut").value) || 0;
    if (!(brut > 0)) { zonaPrapastie.innerHTML = ""; return; }
    let r;
    try {
      r = await api.post(`/tenants/${t.id}/prapastie-salariu`, {
        salariu_brut: brut,
        persoane_intretinere: Number(corp.querySelector("#sn-persoane_intretinere").value) || 0,
        data_nastere: corp.querySelector("#sn-data_nastere").value || null,
        copii_scolarizati: Number(corp.querySelector("#sn-copii_scolarizati").value) || 0,
        declaratie_copii: corp.querySelector("#sn-declaratie_copii").checked,
        tip_norma: corp.querySelector("#sn-tip_norma").value,
        ore_zi: Number(corp.querySelector("#sn-ore_zi").value) || null,
        data_angajare: corp.querySelector("#sn-data_angajare").value || null,
        scutit_contrib_minim: corp.querySelector("#sn-scutit_contrib_minim").checked,
      });
    } catch (e) { zonaPrapastie.innerHTML = ""; return; }
    if (!r || !r.aplicabil) { zonaPrapastie.innerHTML = ""; return; }
    const brutIntrodus = Number(corp.querySelector("#sn-salariu_brut").value);
    zonaPrapastie.innerHTML = `<div class="caseta-atentie">
      <b>Peste salariul minim, netul SCADE.</b>
      La ${bani(r.prag)} lei brut, netul e <b>${bani(r.net_la_prag)}</b> lei.
      La ${bani(brutIntrodus)} lei brut, netul e
      <b>${bani(r.net_acum)}</b> lei — cu <b>${bani(r.pierdere)}</b> lei mai puțin.
      ${r.brut_egal ? `Netul redevine cel de la minim abia de la <b>${bani(r.brut_egal)}</b> lei brut.` : ""}
      <div class="tip-micut">${esc(r.temei || "")} · prag: ${esc(r.prag_temei || "")}</div>
    </div>`;
  }
  ["#sn-salariu_brut", "#sn-persoane_intretinere", "#sn-data_nastere", "#sn-copii_scolarizati",
   "#sn-declaratie_copii", "#sn-tip_norma", "#sn-ore_zi", "#sn-data_angajare",
   "#sn-scutit_contrib_minim"].forEach((sel) => {
    const el = corp.querySelector(sel);
    if (el) el.addEventListener("input", () => {
      clearTimeout(ceasPrapastie);
      ceasPrapastie = setTimeout(verificaPrapastia, 400);
    });
  });
  corp.querySelector("#sn-gata").addEventListener("click", () => nav.inapoiPas());
  corp.querySelector("#sn-salveaza").addEventListener("click", async () => {
    const zona = corp.querySelector("#sn-mesaj");
    const nume = corp.querySelector("#sn-nume").value.trim();
    const brut = corp.querySelector("#sn-salariu_brut").value;
    curataEroriCamp(corp);  // [G10 cap.6 v2.30] eroare langa camp
    if (!nume) { eroareCamp(corp, "sn-nume", "Numele este obligatoriu."); return; }
    if (!brut || !(Number(brut) > 0)) { eroareCamp(corp, "sn-salariu_brut", "Salariul brut este obligatoriu și trebuie să fie mai mare ca 0."); return; }  // [#8]
    if (!corp.querySelector("#sn-cor").value.trim()) { eroareCamp(corp, "sn-cor-cauta", "Alege ocupația (cod COR) din listă — obligatorie pentru D112/REGES."); return; }  // [#7]
    const corpReq = {
      nume,
      prenume: corp.querySelector("#sn-prenume").value.trim() || null,
      cnp: corp.querySelector("#sn-cnp").value.trim() || null,
      data_angajare: corp.querySelector("#sn-data_angajare").value || null,
      data_incetare: corp.querySelector("#sn-data_incetare").value || null,
      tip_norma: corp.querySelector("#sn-tip_norma").value,
      ore_zi: corp.querySelector("#sn-ore_zi").value ? Number(corp.querySelector("#sn-ore_zi").value) : null,
      salariu_brut: brut ? Number(brut) : 0,
      persoane_intretinere: corp.querySelector("#sn-persoane_intretinere").value ? Number(corp.querySelector("#sn-persoane_intretinere").value) : 0,
      data_nastere: corp.querySelector("#sn-data_nastere").value || null,
      copii_scolarizati: corp.querySelector("#sn-copii_scolarizati").value ? Number(corp.querySelector("#sn-copii_scolarizati").value) : 0,
      declaratie_copii: corp.querySelector("#sn-declaratie_copii").checked,
      judet_casa: corp.querySelector("#sn-judet_casa").value.trim() || null,
      cor: corp.querySelector("#sn-cor").value.trim() || null,
      iban: corp.querySelector("#sn-iban").value.trim().replace(/\s/g, "").toUpperCase() || null,  // [F134]
      tichet_masa_valoare: corp.querySelector("#sn-tichet_masa_valoare").value ? Number(corp.querySelector("#sn-tichet_masa_valoare").value) : 0,  // [F133]
      scutit_contrib_minim: corp.querySelector("#sn-scutit_contrib_minim").checked,
    };
    try {
      await api.post(`/tenants/${t.id}/salariati`, corpReq);
      if (dupaSalvare) dupaSalvare();
      formularSalariatNou(corp, nav, t, dupaSalvare);
      corp.querySelector("#sn-mesaj").innerHTML = `<p class="pf-intro" style="color:var(--verde)">Salariat salvat. Po\u021bi ad\u0103uga altul.</p>`;
    } catch (e) {
      curataEroriCamp(corp);
      const _ec = e && e.erori_campuri;  // [G10 rule2/4] erorile per-camp din contractul backend
      if (_ec && _ec.length) _ec.forEach((x) => eroareCamp(corp, "sn-" + x.camp, x.mesaj));
      else arataMesaj(zona, (e && e.mesaj) || "eroare la salvare", "eroare");  // B: erori fara camp
    }
  });
}

// [control_firma_v1 + consolidat 24.07] Control fiscal per firma. Corpul verdictului (declaratii + TOATE
// verificarile contabile) e randat de control_verdict.js — renderer UNIC, acelasi cu ecranul Control fiscal
// (detaliuFirma). Inainte, aceasta functie citea un subset hardcodat din verificari_contabile (echilibru/
// tva/documente) si nu atingea cross-check-urile -> constatarile BLOCANTE pe salarii/trezorerie nu apareau
// (cazul DANTE 24.07). Aici raman doar anteta (semafor mare) + delegarea. Vezi DESIGN_SYSTEM cap.20.
async function ecranControlFirma(corp, nav, t) {
  corp.innerHTML = `<p class="ecran-nota">Se evaluează situația fiscală...</p>`;
  let d;
  try {
    d = await api.get(`/control-fiscal/${t.id}`);
  } catch (e) {
    corp.innerHTML = `<p class="msg-eroare">${(e && e.mesaj) || "Nu am putut evalua controlul fiscal."}</p>`;
    return;
  }
  const cul = CULORI_VERDICT[d.stare] || CULORI_VERDICT.gri;
  corp.innerHTML = `
    <h2 class="pf-titlu">Control fiscal ${semnAjutor("F022")}</h2>
    <p class="pf-intro">Situația fiscală a firmei: ce s-a depus vs ce e datorat, cu verificări de coerență.</p>
    <div class="cf-stare-mare" style="background:${cul.bg}">
      <span class="cf-dot" style="background:${cul.dot}"></span>
      <span class="cf-stare-txt">${etichetaStare(d.stare, (d.neclar || []).length)}</span>
      <span class="cf-stare-cifre tip-micut">${d.datorate || 0} datorate · ${d.depuse || 0} depuse</span>
    </div>
    ${randeazaCorpVerdict(d, { mod: "fisa" })}`;
  legaVerdict(corp, nav, { tenant_id: t.id, nume: t.nume, reincarca: () => ecranControlFirma(corp, nav, t) });
}
// F135: pontaj lunar informativ - marcheaza exceptiile pe zilele lucratoare (fara sarbatori)
async function ecranPontaj(corp, nav, t, sid, nume, an, luna) {
  const ZI_SAPT = ["dum", "lun", "mar", "mie", "joi", "vin", "sâm"];
  const STARI = [["prezent", "prezent"], ["absent_motivat", "absent motivat"],
    ["absent_nemotivat", "absent nemotivat"], ["concediu_odihna", "concediu odihnă"],
    ["concediu_medical", "concediu medical"], ["invoire", "învoire"], ["delegatie", "delegație"]];
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă pontajul…</p>`;
    let g;
    try { g = await api.get(`/tenants/${t.id}/salariati/${sid}/pontaj?an=${an}&luna=${luna}`); }
    catch { corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca pontajul.</p>`; return; }
    const rez = g.rezumat || {};
    const lucr = (g.zile || []).filter((z) => z.lucratoare && z.in_activitate);
    const randuri = lucr.map((z) => {
      const zid = new Date(z.zi + "T00:00:00").getDay();
      const opts = STARI.map(([v, l]) => `<option value="${v}"${z.stare === v ? " selected" : ""}>${l}</option>`).join("");
      return `<label class="camp"><span class="camp-eticheta">${String(z.zi_nr).padStart(2, "0")} ${ZI_SAPT[zid]}</span><select class="camp-input pj-sel" data-zi="${z.zi}">${opts}</select></label>`;
    }).join("");
    const pc = g.perioada_confirmata || {};
    const dataConf = pc.confirmat_la ? dataRo(String(pc.confirmat_la).slice(0, 10)) : "";
    const stareBloc = pc.confirmat
      ? `<div class="caseta-info"><span class="ci-mesaj"><span style="color:var(--verde)">\u25cf</span> Pontaj confirmat${dataConf ? " la " + dataConf : ""} \u2014 autoritativ pentru salarizare (tichete pe zile efectiv lucrate).</span></div>`
      : `<div class="caseta-info"><span class="ci-mesaj"><span style="color:var(--gri-semafor)">\u25cf</span> Pontaj neconfirmat \u2014 informativ; calculele din aval (tichete, statul de plat\u0103) se blocheaz\u0103 p\u00e2n\u0103 la confirmare.</span></div><p style="margin-top:8px"><button class="buton-verde" id="pj-confirma">Confirm\u0103 pontajul lunii</button></p>`;
    corp.innerHTML = `
      <h2 class="pf-titlu">Pontaj</h2>
      <p class="pf-intro">${esc(nume || "")} · luna ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")}
        <button class="buton-secundar" id="pj-prev" style="margin-left:12px">← luna</button>
        <button class="buton-secundar" id="pj-next">luna →</button></p>
      <div class="cf-sumar">
        <span class="cf-pastila">${rez.prezent || 0} prezent</span>
        <span class="cf-pastila">${(rez.absent_motivat || 0) + (rez.absent_nemotivat || 0)} absent</span>
        <span class="cf-pastila">${(rez.concediu_odihna || 0) + (rez.concediu_medical || 0)} concediu</span>
        <span class="cf-pastila">${rez.invoire || 0} învoire · ${rez.delegatie || 0} delegație</span>
      </div>
      ${stareBloc}
      <p class="pf-intro">Doar zilele lucrătoare (weekendul și sărbătorile legale nu se pontează). Prezent = implicit; evidență informativă, nu schimbă statul de plată.</p>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px;max-width:900px">${randuri || '<div class="stare-goala">Nicio zi lucrătoare în perioada de activitate.</div>'}</div>
      <div id="pj-msg" style="margin-top:10px"></div>`;
    corp.querySelector("#pj-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#pj-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    const btnConf = corp.querySelector("#pj-confirma");
    if (btnConf) btnConf.addEventListener("click", () => confirmaCaseta(btnConf,
      "Confirmi pontajul lunii? Devine autoritativ pentru salarizare \u2014 tichetele se calculeaz\u0103 pe zilele efectiv lucrate. O modificare ulterioar\u0103 \u00eel de-confirm\u0103.",
      async () => {
        try { await api.post(`/tenants/${t.id}/pontaj/confirma`, { an, luna }); deseneaza(); }
        catch (e) { arataMesaj(corp.querySelector("#pj-msg"), e.mesaj || "Eroare.", "eroare"); }
      }));
    corp.querySelectorAll(".pj-sel").forEach((sel) => sel.addEventListener("change", async () => {
      try { await api.put(`/tenants/${t.id}/salariati/${sid}/pontaj`, { zi: sel.dataset.zi, stare: sel.value }); deseneaza(); }
      catch (e) { arataMesaj(corp.querySelector("#pj-msg"), e.mesaj || "Eroare.", "eroare"); }
    }));
  };
  deseneaza();
}

// F136: formular adeverinta salariat -> PDF (art. 34(5) Codul muncii)
function formularAdeverinta(corp, nav, t, sid, nume, an, luna) {
  corp.innerHTML = `
    <h2 class="pf-titlu">Adeverință ${semnAjutor("F136")}</h2>
    <p class="pf-intro">Pentru ${esc(nume || "salariat")}. Denumirea firmei, numele, CNP-ul, funcția COR, data angajării și salariul brut/net se completează automat din datele firmei. Restul, mai jos.</p>
    <div class="caseta-atentie" style="margin:0 0 12px"><span class="ca-mesaj">Pentru credit bancar, băncile cer de obicei formularul propriu — un PDF generic nu e acceptat. Din 2026 verifică veniturile direct la ANAF.</span></div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;max-width:820px">
      <label class="camp"><span class="camp-eticheta">Scopul<span class="oblig">*</span></span><input id="ad-scop" class="camp-input" placeholder="ex. grădiniță, notar, instanță"></label>
      <label class="camp"><span class="camp-eticheta">Funcția</span><input id="ad-functie" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Departament</span><input id="ad-dept" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Serie CI</span><input id="ad-serieci" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Nr. CI</span><input id="ad-nrci" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Tip contract</span><select id="ad-tip" class="camp-input"><option value="nedeterminata">nedeterminată</option><option value="determinata">determinată</option></select></label>
      <label class="camp"><span class="camp-eticheta">Nr. CIM</span><input id="ad-nrcim" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Dată CIM</span><input type="date" id="ad-datacim" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Vechime în muncă</span><input id="ad-vm" class="camp-input" placeholder="ex. 8 ani 3 luni"></label>
      <label class="camp"><span class="camp-eticheta">Vechime specialitate</span><input id="ad-vs" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Nr. ieșire</span><input id="ad-nr" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Data ieșirii</span><input type="date" id="ad-data" class="camp-input"></label>
    </div>
    <label class="camp" style="max-width:820px;margin-top:10px"><span class="camp-eticheta">Mențiuni (opțional)</span><textarea id="ad-mentiuni" class="camp-input" rows="2"></textarea></label>
    <p style="margin-top:14px"><button class="buton-primar" id="ad-gen">Generează PDF</button> <button class="buton-secundar" id="ad-renunta" style="margin-left:8px">Renunță</button></p>
    <div id="ad-msg"></div>`;
  corp.querySelector("#ad-renunta").addEventListener("click", () => nav.inapoi && nav.inapoi());
  corp.querySelector("#ad-gen").addEventListener("click", async () => {
    const msg = corp.querySelector("#ad-msg");
    const val = (id) => corp.querySelector(id).value.trim();
    if (!val("#ad-scop")) { arataMesaj(msg, "Completează scopul adeverinței.", "eroare"); return; }
    const body = {
      scop: val("#ad-scop"), functie: val("#ad-functie"), departament: val("#ad-dept"),
      serie_ci: val("#ad-serieci"), nr_ci: val("#ad-nrci"), tip_contract: corp.querySelector("#ad-tip").value,
      nr_cim: val("#ad-nrcim"), data_cim: corp.querySelector("#ad-datacim").value || null,
      vechime_munca: val("#ad-vm"), vechime_specialitate: val("#ad-vs"),
      nr_iesire: val("#ad-nr"), data_iesire: corp.querySelector("#ad-data").value || null,
      mentiuni: val("#ad-mentiuni"), an, luna,
    };
    const btn = corp.querySelector("#ad-gen"); btn.disabled = true; btn.textContent = "Se generează…";
    try {
      const r = await fetch(`/tenants/${t.id}/salariati/${sid}/adeverinta`, {
        method: "POST",
        headers: { "Authorization": "Bearer " + sesiune.token(), "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!r.ok) throw new Error("pdf " + r.status);
      const url = URL.createObjectURL(await r.blob());
      window.open(url, "_blank");
      setTimeout(() => URL.revokeObjectURL(url), 60000);
      arataMesaj(msg, "Adeverință generată.", "ok");
    } catch { arataMesaj(msg, "Nu am putut genera adeverința.", "eroare"); }
    finally { btn.disabled = false; btn.textContent = "Generează PDF"; }
  });
}

async function ecranSalariati(corp, nav, t) {
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se calculeaz\u0103...</p>`;
    let stat = [];
    let areIban = false, regesOk = false;  // [dec2] preconditii SEPA/REGES (scop functie)
    try {
      const r = await api.get(`/tenants/${t.id}/stat-plata?an=${an}&luna=${luna}`);
      stat = (r && r.stat) || [];
    areIban = stat.some((s) => s.iban);  // [dec2 Costin] SEPA cere macar un IBAN
    regesOk = !!(r && r.reges_configurat);  // [dec2 Costin] REGES cere chei configurate
    } catch (e) { corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca statul de plată. ${esc((e && (e.mesaj || e.message)) || "")}</p>`; return; }  // [#1/#3] mesaj real, nu catch gol
    const pontajNeconf = stat.some((s) => s.pontaj_neconfirmat);  // [#1/#3] statul se afiseaza; tichete blocate
    const randuri = !stat.length
      ? `<div class="stare-goala">Niciun salariat activ încă.</div>`
      : stat.map((s) => `
        <div class="pf-frand" style="flex-wrap:wrap">
          <div class="pf-frand-text" style="flex:1 1 100%">
            <div class="pf-frand-nume">${esc(s.nume)}${s.baza_lipsa ? ' <span style="color:var(--rosu);font-weight:600">⚠ salariu de bază lipsă</span>' : ""}${s.pontaj_neconfirmat ? ' <span style="color:var(--gri);font-weight:600">tichete blocate</span>' : ""}</div>
            ${s.baza_lipsa ? `<div class="pf-frand-sub" style="color:var(--rosu)">Salariul de bază lipsește (0 lei) — completează-l cu butonul „Salariu" de pe salariat. Fără el statul nu e corect: net 0, dar angajatorul apare cu cost din suprataxa CAS/CASS pe podeaua salariului minim (art.146(5^6)/168(6^1)).</div>` : ""}
            ${s.pontaj_neconfirmat ? `<div class="pf-frand-sub" style="color:var(--gri)">Tichetele de masă sunt blocate până la confirmarea pontajului lunii (buton „Pontaj").</div>` : ""}
            <div class="pf-frand-sub">brut ${bani(s.brut)} \u00b7 CAS ${bani(s.cas)} \u00b7 CASS ${bani(s.cass)} \u00b7 impozit ${bani(s.impozit_salariu)} \u00b7 <b>net ${bani(s.net)}</b> \u00b7 cost ${bani(s.cost)}${s.tichete_nominal ? ` \u00b7 <span style="color:var(--teal)">tichete ${bani(s.tichete_nominal)} (${s.tichete_zile} zile)</span>` : ""}${s.tichete_vacanta ? ` · <span style="color:var(--teal)">vacanță ${bani(s.tichete_vacanta)}</span>${s.vacanta_peste_plafon ? ' <span style="color:var(--rosu)">⚠ peste plafon anual</span>' : ""}` : ""}${s.cadou ? ` · <span style="color:var(--teal)">cadou ${bani(s.cadou)}</span>${s.cadou_taxabil ? ' <span style="color:var(--rosu)">⚠ taxabil (>300 lei/eveniment sau eveniment nelegal)</span>' : ""}` : ""}${s.tichete_cultural ? ` · <span style="color:var(--teal)">cultural ${bani(s.tichete_cultural)}</span>` : ""}${s.tichete_cresa ? ` · <span style="color:var(--teal)">creșă ${bani(s.tichete_cresa)}</span>` : ""}${(s.tichete_nominal || s.tichete_vacanta) ? ` · <span style="color:var(--gri)">reținut pe tichete: CASS ${bani(s.cass_tichete)} + impozit ${bani(s.impozit_tichete)}</span>` : ""}${(s.tichete_nominal || s.tichete_vacanta || s.cadou) ? ` · <b>total disponibil ${bani(s.total_disponibil)}</b>` : ""}</div>
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-start;width:100%">
          <button class="buton-primar" data-flut="${s.id}">Flutura\u0219</button>
          <button class="buton-secundar" data-reges="${s.id}">REGES</button>
          <button class="buton-secundar" data-cm="${s.id}" data-nume="${esc(s.nume)}">Concediu</button>
          <button class="buton-secundar" data-adev="${s.id}" data-nume="${esc(s.nume)}">Adeverință</button>
          <button class="buton-secundar" data-pontaj="${s.id}" data-nume="${esc(s.nume)}">Pontaj</button>
          <button class="buton-secundar" data-vac="${s.id}" data-val="${s.tichete_vacanta || 0}" data-nume="${esc(s.nume)}">+ vacanță</button>
          <button class="buton-secundar" data-cadou="${s.id}" data-nume="${esc(s.nume)}">+ cadou</button>
          <button class="buton-secundar" data-cult="${s.id}" data-nume="${esc(s.nume)}">+ cultural</button>
          <button class="buton-secundar" data-cresa="${s.id}" data-nume="${esc(s.nume)}">+ creșă</button>
          <button class="buton-secundar" data-salariu="${s.id}" data-val="${s.salariu_baza || 0}" data-nume="${esc(s.nume)}">Salariu</button>
          <button class="buton-secundar" data-iban="${s.id}" data-val="${esc(s.iban || "")}" data-nume="${esc(s.nume)}">IBAN ${s.iban ? "✓" : "⚠"}</button>
          <button class="buton-secundar" data-cor="${s.id}" data-val="${esc(s.cor || "")}" data-nume="${esc(s.nume)}">COR ${s.cor ? "✓" : "⚠"}</button>
          <button class="buton-secundar" data-incet="${s.id}" data-val="${esc(s.data_incetare || "")}" data-nume="${esc(s.nume)}">${s.data_incetare ? "Plecat " + s.data_incetare : "Încetare"}</button>
          <button class="buton-secundar" data-date="${s.id}" data-dnume="${esc(s.nume_ed || "")}" data-dpren="${esc(s.prenume_ed || "")}" data-dcnp="${esc(s.cnp || "")}" data-dang="${esc(s.data_angajare || "")}" data-dnorma="${esc(s.tip_norma || "")}" data-dorezi="${esc(s.ore_zi == null ? "" : String(s.ore_zi))}">Corectează datele</button>
          </div>
        </div>`).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">Stat de plat\u0103 ${semnAjutor("F080")}</h2>
      <p class="pf-intro">Luna ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")}
        <button class="buton-secundar" id="sp-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="buton-secundar" id="sp-next">luna \u2192</button>
        <button class="buton-secundar" id="sp-reges-cfg" style="margin-left:12px">Chei REGES</button>
        <button class="buton-secundar" id="sp-reges-poll"${regesOk ? "" : " disabled"}>R\u0103spunsuri REGES</button>
        <button class="buton-primar" id="sp-salariat-nou" style="margin-left:12px">+ Salariat nou</button>
        <button class="buton-secundar" id="sp-plata-card" style="margin-left:12px"${areIban ? "" : " disabled"}>Fișier plată card (SEPA)</button>
        <button class="buton-secundar" id="sp-contare">Contabilizează statul</button></p>
      <div id="sp-contare-zona"></div>
      <div id="sp-plata-zona"></div>
      <div id="sp-reges-zona"></div>
      <div id="sp-vac-zona"></div>
      <div id="sp-cadou-zona"></div>
      <div id="sp-cultural-zona"></div>
      <div id="sp-cresa-zona"></div>
      <div id="sp-iban-zona"></div>
      <div id="sp-cor-zona"></div>
      <div id="sp-incet-zona"></div>
      <div id="sp-salariu-zona"></div>
      <div id="sp-date-zona"></div>
      ${!areIban ? `<div class="caseta-info"><span class="ci-mesaj">Fișierul de plată pe card (SEPA) e indisponibil: niciun salariat nu are IBAN completat. Adaugă IBAN-ul cu butonul „IBAN ⚠" de pe salariat.</span></div>` : ""}
      ${!regesOk ? `<div class="caseta-info"><span class="ci-mesaj">„Răspunsuri REGES" e indisponibil: cheile REGES nu sunt configurate încă. Configurează-le cu butonul „Chei REGES".</span></div>` : ""}
      ${pontajNeconf ? `<div class="caseta-info"><span class="ci-mesaj"><span style="color:var(--gri-semafor)">●</span> Pontajul lunii ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")} nu e confirmat — informativ; tichetele de masă rămân blocate până la confirmarea pontajului (buton „Pontaj" pe salariat).</div></div>` : ""}
      <div class="pf-lista">${randuri}</div>`;
    corp.querySelector("#sp-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#sp-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    corp.querySelector("#sp-salariat-nou").addEventListener("click", () => nav.mergi("Salariat nou", (c2) => formularSalariatNou(c2, nav, t, deseneaza)));
    // [R33, decizia Costin 25.08.2026] Semnalul de coerenta nota-vs-D112, LA PROPUNERE.
    // SEMNALEAZA, nu blocheaza: aplicatia compara o propunere cu o declaratie generata din alte
    // date, iar cand cele doua difera nu se stie CARE greseste. Un blocaj ar presupune ca
    // declaratia are dreptate. Semnalul arata AMBELE cifre si diferenta - nu "exista o divergenta".
    // Divergenta ramane vizibila si dupa contare: se recalculeaza de fiecare data, deci nu se
    // stinge prin ignorare.
    const zonaContare = corp.querySelector("#sp-contare-zona");
    const randDivergente = (p) => !p.divergente.length
      ? `<div class="caseta-info"><span class="ci-mesaj">Nota propusă coincide cu D112 pe toate cele patru conturi, în limita de toleranță.</span></div>`
      : `<div class="caseta-atentie">
          <b>Nota propusă nu coincide cu D112 pe ${p.divergente.length} ${p.divergente.length === 1 ? "cont" : "conturi"}.</b>
          <div class="tip-micut">Nu se blochează nimic: nu se poate ști din afară care dintre cele două greșește — poate declarația e veche, poate nota e corectă.</div>
          <table class="tabel-simplu" style="margin-top:8px">
            <thead><tr><th>Ce</th><th>Cont</th><th>Nota ar scrie</th><th>D112 declară</th><th>Diferență</th></tr></thead>
            <tbody>${p.divergente.map((d) => `<tr>
              <td>${esc(d.eticheta)}</td>
              <td>${esc(d.cont)}</td>
              <td>${bani(d.nota)}</td>
              <td>${bani(d.declaratie)}</td>
              <td style="color:var(--rosu);font-weight:600">${bani(d.diferenta)}</td>
            </tr>`).join("")}</tbody>
          </table>
          <div class="tip-micut">Toleranța aplicată: ${bani(p.divergente[0].toleranta)} lei (${p.nr_salariati} salariați).</div>
        </div>`;
    const arataPropunerea = (p) => {
      zonaContare.innerHTML = `<div class="pf-frand" style="display:block;margin:10px 0">
        <div class="pf-frand-nume">${esc(p.document_ref)} — ${p.note.length} ${p.note.length === 1 ? "linie" : "linii"}, total ${bani(p.total)} lei</div>
        ${randDivergente(p)}
        <table class="tabel-simplu" style="margin-top:8px">
          <thead><tr><th>Debit</th><th>Credit</th><th>Sumă</th></tr></thead>
          <tbody>${p.note.map((n) => `<tr><td>${esc(n.debit)}</td><td>${esc(n.credit)}</td><td>${bani(n.suma)}</td></tr>`).join("")}</tbody>
        </table>
        <p style="margin-top:10px">${p.deja_contata
          ? `<span class="tip-micut">Nota există deja în jurnal (ciornă #${p.nota_id}). Semnalul de mai sus se recalculează de fiecare dată, deci rămâne vizibil cât timp cifrele diferă.</span>`
          : `<button class="buton-primar" id="sp-contare-scrie">Scrie nota ciornă</button>
             <span class="tip-micut" style="margin-left:8px">Ciornă, nu validată: validării îi rămâne al doilea om.</span>`}</p>
      </div>`;
      const b = corp.querySelector("#sp-contare-scrie");
      if (b) b.addEventListener("click", async () => {
        b.disabled = true; b.textContent = "Se scrie…";
        try {
          const r = await api.post(`/tenants/${t.id}/salarii-contare?an=${an}&luna=${luna}`, {});
          arataPropunerea(r);
        } catch (e) {
          b.disabled = false; b.textContent = "Scrie nota ciornă";
          arataMesaj(zonaContare, (e && e.mesaj) || "Nu am putut scrie nota.", "eroare");
        }
      });
    };
    corp.querySelector("#sp-contare").addEventListener("click", async () => {
      zonaContare.innerHTML = `<p class="ecran-nota">Se calculează propunerea…</p>`;
      try {
        arataPropunerea(await api.post(`/tenants/${t.id}/salarii-contare/propunere?an=${an}&luna=${luna}`, {}));
      } catch (e) {
        zonaContare.innerHTML = "";
        arataMesaj(zonaContare, (e && e.mesaj) || "Nu am putut calcula propunerea.", "eroare");
      }
    });

    // [F134] fisier de plata pe card (SEPA pain.001): preview (cati, total, cine fara IBAN) -> download
    const zonaPlata = corp.querySelector("#sp-plata-zona");
    corp.querySelector("#sp-plata-card").addEventListener("click", async () => {
      zonaPlata.innerHTML = `<p class="ecran-nota">Se pregătește...</p>`;
      let m;
      try {
        m = await api.get(`/tenants/${t.id}/plata-salarii-preview?an=${an}&luna=${luna}`);
      } catch (e) { zonaPlata.innerHTML = ""; arataMesaj(zonaPlata, (e && e.mesaj) || "Nu se poate genera fișierul.", "eroare"); return; }
      const avert = (m.fara_iban && m.fara_iban.length)
        ? `<div style="color:var(--rosu);margin-top:6px">⚠ ${m.fara_iban.length} salariat(i) fără IBAN, excluși din fișier: ${m.fara_iban.map(esc).join(", ")}. Completează IBAN-ul (buton „IBAN ⚠") ca să-i incluzi.</div>`
        : "";
      zonaPlata.innerHTML = `<div class="pf-frand" style="display:block;margin:10px 0">
        <div class="pf-frand-nume">Plată salarii pe card · ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")}</div>
        <div class="pf-frand-sub">${m.nr_plati} plată/plăți · total ${bani(m.total)} lei · format SEPA pain.001</div>
        ${avert}
        <p style="margin-top:8px"><button class="buton-primar" id="plata-descarca">Descarcă fișierul</button>
          <button class="buton-secundar" id="plata-inchide" style="margin-left:6px">Închide</button></p></div>`;
      corp.querySelector("#plata-inchide").addEventListener("click", () => { zonaPlata.innerHTML = ""; });
      corp.querySelector("#plata-descarca").addEventListener("click", async () => {
        try {
          // [R45] POST: producerea fisierului care pleaca la banca e un act, si se pastreaza.
          const resp = await fetch(`/tenants/${t.id}/plata-salarii-fisier?an=${an}&luna=${luna}`, {
            method: "POST",
            headers: { "Authorization": "Bearer " + sesiune.token() } });
          if (!resp.ok) throw new Error();
          const blob = await resp.blob();
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url; a.download = `plata_salarii_${an}_${String(luna).padStart(2,"0")}.xml`; a.click();
          URL.revokeObjectURL(url);
        } catch { arataMesaj(zonaPlata, "Nu am putut descărca fișierul.", "eroare"); }
      });
    });
    const zonaReges = corp.querySelector("#sp-reges-zona");
    corp.querySelector("#sp-reges-cfg").addEventListener("click", () => {
      zonaReges.innerHTML = `<div style="display:block;margin:10px 0">
        <div class="pf-frand-nume" style="margin-bottom:8px">Chei API REGES (din aplicatia REGES Angajator)</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;max-width:700px">
          <label class="camp"><span class="camp-eticheta">Username</span><input type="text" id="rg-user" class="camp-input"></label>
          <label class="camp"><span class="camp-eticheta">Parola</span><input type="password" id="rg-pass" class="camp-input"></label>
          <label class="camp"><span class="camp-eticheta">Mediu</span><select id="rg-mediu" class="camp-input"><option value="test">Test</option><option value="prod">Productie</option></select></label>
        </div>
        <p style="margin-top:10px"><button class="buton-primar" id="rg-salveaza">Salveaz\u0103</button></p>
        <div id="rg-msg"></div></div>`;
      corp.querySelector("#rg-salveaza").addEventListener("click", async () => {
        const m = corp.querySelector("#rg-msg");
        try {
          await api.post(`/tenants/${t.id}/reges-config`, {
            username: corp.querySelector("#rg-user").value,
            parola: corp.querySelector("#rg-pass").value,
            mediu: corp.querySelector("#rg-mediu").value });
          m.innerHTML = '<p class="pf-intro">Chei salvate.</p>';
        } catch (e) { arataMesaj(m, e.mesaj || "eroare", "eroare"); }
      });
    });
    corp.querySelector("#sp-reges-poll").addEventListener("click", async () => {
      try {
        const r = await api.get(`/tenants/${t.id}/reges-poll`);
        const msgs = (r && (r.mesaje || r.raspunsuri)) || [];
        zonaReges.innerHTML = `<div class="pf-frand" style="display:block;margin:10px 0">
          <div class="pf-frand-nume">R\u0103spunsuri REGES</div>
          <div class="pf-frand-sub">${msgs.length ? msgs.map((m2) => `${m2.data ? dataRo(m2.data) : ""} \u00b7 ${m2.status || m2.tip || ""} \u00b7 ${m2.mesaj || m2.detalii || "răspuns fără detalii"}`).join("<br>") : "niciun răspuns nou"}</div></div>`;
      } catch (e) { arataMesaj(zonaReges, e.mesaj || "eroare", "eroare"); }
    });
    corp.querySelectorAll("[data-cm]").forEach((b) => b.addEventListener("click", () => {
      fluxConcediu(nav, t, { id: parseInt(b.dataset.cm), nume: b.dataset.nume });
    }));
    corp.querySelectorAll("[data-adev]").forEach((b) => b.addEventListener("click", () =>  // f136_adeverinta
      nav.mergi("Adeverință", (c2) => formularAdeverinta(c2, nav, t, parseInt(b.dataset.adev), b.dataset.nume, an, luna))));
    corp.querySelectorAll("[data-pontaj]").forEach((b) => b.addEventListener("click", () =>  // f135_pontaj
      nav.mergi("Pontaj", (c2) => ecranPontaj(c2, nav, t, parseInt(b.dataset.pontaj), b.dataset.nume, an, luna))));
    // [F133 Faza 2a] + vacanta: input one-off pe luna curenta, pe randul salariatului
    const zonaVac = corp.querySelector("#sp-vac-zona");
    corp.querySelectorAll("[data-vac]").forEach((b) => b.addEventListener("click", () => {
      const sid = b.dataset.vac;
      zonaVac.innerHTML = `<div style="display:flex;gap:8px;align-items:center;margin:10px 0;flex-wrap:wrap">
        <span class="camp-eticheta">Tichete vacanță · ${esc(b.dataset.nume)} · ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")}:</span>
        <input type="number" step="0.01" min="0" id="vac-input" class="camp-input" value="${b.dataset.val}" style="width:150px">
        <button class="buton-primar" id="vac-save">Salvează</button>
        <button class="buton-secundar" id="vac-cancel">Renunță</button></div>
        <div id="vac-msg"></div>`;
      const inp = corp.querySelector("#vac-input"); inp.focus(); inp.select();
      corp.querySelector("#vac-cancel").addEventListener("click", () => { zonaVac.innerHTML = ""; });
      corp.querySelector("#vac-save").addEventListener("click", async () => {
        const valoare = parseFloat(inp.value) || 0;
        try {
          await api.put(`/tenants/${t.id}/salariati/${sid}/beneficiu-lunar`, { an, luna, tip: "vacanta", valoare });
          zonaVac.innerHTML = ""; deseneaza();
        } catch (e) { arataMesaj(corp.querySelector("#vac-msg"), (e && e.mesaj) || "Eroare la salvare.", "eroare"); }
      });
    }));
    // [F133 Faza 2b1] + cadou: neimpozabil <=300/eveniment legal; selector eveniment + valoare
    const zonaCadou = corp.querySelector("#sp-cadou-zona");
    corp.querySelectorAll("[data-cadou]").forEach((b) => b.addEventListener("click", () => {
      const sid = b.dataset.cadou;
      const evenimente = [["paste", "Paște"], ["craciun", "Crăciun"], ["8martie", "8 Martie"],
                          ["1iunie", "1 Iunie"], ["altul", "alt eveniment (taxabil)"]];
      zonaCadou.innerHTML = `<div style="display:flex;gap:8px;align-items:center;margin:10px 0;flex-wrap:wrap">
        <span class="camp-eticheta">Tichete cadou · ${esc(b.dataset.nume)} · ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")}:</span>
        <select id="cadou-ev" class="camp-input" style="width:200px">${evenimente.map(([v, l]) => `<option value="${v}">${l}</option>`).join("")}</select>
        <input type="number" step="0.01" min="0" id="cadou-input" class="camp-input" placeholder="valoare (lei)" style="width:150px">
        <button class="buton-primar" id="cadou-save">Salvează</button>
        <button class="buton-secundar" id="cadou-cancel">Renunță</button></div>
        <div class="camp-eticheta" style="color:var(--gri)">Neimpozabil ≤ 300 lei/eveniment pentru evenimente legale; peste 300 sau alt eveniment = semnalat ca taxabil.</div>
        <div id="cadou-msg"></div>`;
      corp.querySelector("#cadou-input").focus();
      corp.querySelector("#cadou-cancel").addEventListener("click", () => { zonaCadou.innerHTML = ""; });
      corp.querySelector("#cadou-save").addEventListener("click", async () => {
        const valoare = parseFloat(corp.querySelector("#cadou-input").value) || 0;
        const eveniment = corp.querySelector("#cadou-ev").value;
        try {
          await api.put(`/tenants/${t.id}/salariati/${sid}/beneficiu-lunar`, { an, luna, tip: "cadou", eveniment, valoare });
          zonaCadou.innerHTML = ""; deseneaza();
        } catch (e) { arataMesaj(corp.querySelector("#cadou-msg"), (e && e.mesaj) || "Eroare la salvare.", "eroare"); }
      });
    }));
    // [tichete de cresa] Legea 165/2018 art.19: lunar, per copil; plafon 450/copil (indexare GRI blocata backend).
    const zonaCresa = corp.querySelector("#sp-cresa-zona");
    corp.querySelectorAll("[data-cresa]").forEach((b) => b.addEventListener("click", () => {
      const sid = b.dataset.cresa;
      zonaCresa.innerHTML = `<div style="display:flex;gap:8px;align-items:center;margin:10px 0;flex-wrap:wrap">
        <span class="camp-eticheta">Tichete de creșă · ${esc(b.dataset.nume)} · ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")}:</span>
        <input type="number" min="1" step="1" id="cresa-copii" class="camp-input" placeholder="1" style="width:120px" title="nr. copii la creșă (implicit 1)">
        <input type="number" step="10" min="0" id="cresa-input" class="camp-input" placeholder="valoare (multiplu de 10)" style="width:190px">
        <button class="buton-primar" id="cresa-save">Salvează</button>
        <button class="buton-secundar" id="cresa-cancel">Renunță</button></div>
        <div class="camp-eticheta" style="color:var(--gri)">450 lei/lună/copil (Legea 165/2018 art.19); valoare multiplu de 10. Indexarea peste bază (ex. 740) e neconfirmată la sursă (GRI) — blocată.</div>
        <div id="cresa-msg"></div>`;
      corp.querySelector("#cresa-input").focus();
      corp.querySelector("#cresa-cancel").addEventListener("click", () => { zonaCresa.innerHTML = ""; });
      corp.querySelector("#cresa-save").addEventListener("click", async () => {
        const valoare = parseFloat(corp.querySelector("#cresa-input").value) || 0;
        const nr_copii = parseInt(corp.querySelector("#cresa-copii").value, 10) || 1;
        try {
          await api.put(`/tenants/${t.id}/salariati/${sid}/beneficiu-lunar`, { an, luna, tip: "cresa", valoare, nr_copii });
          zonaCresa.innerHTML = ""; deseneaza();
        } catch (e) { arataMesaj(corp.querySelector("#cresa-msg"), (e && e.mesaj) || "Eroare la salvare.", "eroare"); }
      });
    }));
    // [tichete culturale] Legea 165/2018 cap.V: lunar sau ocazional; plafon semestrial indexat (fereastra
    // GRI oct.2025-mar.2026 blocata de backend cu mesaj). Valoare nominala multiplu de 10 (art.22).
    const zonaCult = corp.querySelector("#sp-cultural-zona");
    corp.querySelectorAll("[data-cult]").forEach((b) => b.addEventListener("click", () => {
      const sid = b.dataset.cult;
      zonaCult.innerHTML = `<div style="display:flex;gap:8px;align-items:center;margin:10px 0;flex-wrap:wrap">
        <span class="camp-eticheta">Tichete culturale · ${esc(b.dataset.nume)} · ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")}:</span>
        <select id="cult-tip" class="camp-input" style="width:180px"><option value="">lunar</option><option value="ocazional">ocazional (eveniment)</option></select>
        <input type="number" step="10" min="0" id="cult-input" class="camp-input" placeholder="valoare (multiplu de 10)" style="width:190px">
        <button class="buton-primar" id="cult-save">Salvează</button>
        <button class="buton-secundar" id="cult-cancel">Renunță</button></div>
        <div class="camp-eticheta" style="color:var(--gri)">Valoare nominală multiplu de 10 lei (Legea 165/2018 art.22); plafon lunar/eveniment indexat semestrial. Lunile din fereastra neconfirmată la sursă (oct.2025–mar.2026) sunt blocate.</div>
        <div id="cult-msg"></div>`;
      corp.querySelector("#cult-input").focus();
      corp.querySelector("#cult-cancel").addEventListener("click", () => { zonaCult.innerHTML = ""; });
      corp.querySelector("#cult-save").addEventListener("click", async () => {
        const valoare = parseFloat(corp.querySelector("#cult-input").value) || 0;
        const eveniment = corp.querySelector("#cult-tip").value;
        try {
          await api.put(`/tenants/${t.id}/salariati/${sid}/beneficiu-lunar`, { an, luna, tip: "cultural", eveniment, valoare });
          zonaCult.innerHTML = ""; deseneaza();
        } catch (e) { arataMesaj(corp.querySelector("#cult-msg"), (e && e.mesaj) || "Eroare la salvare.", "eroare"); }
      });
    }));
    // [F134] IBAN salariat: cont beneficiar pt fisierul de plata pe card (editabil pe rand)
    const zonaIban = corp.querySelector("#sp-iban-zona");
    corp.querySelectorAll("[data-iban]").forEach((b) => b.addEventListener("click", () => {
      const sid = b.dataset.iban;
      zonaIban.innerHTML = `<div style="display:flex;gap:8px;align-items:center;margin:10px 0;flex-wrap:wrap">
        <span class="camp-eticheta">IBAN salariu · ${esc(b.dataset.nume)}:</span>
        <input type="text" id="iban-input" class="camp-input" value="${esc(b.dataset.val)}" placeholder="RO.. cont pe card" style="width:280px">
        <button class="buton-primar" id="iban-save">Salvează</button>
        <button class="buton-secundar" id="iban-cancel">Renunță</button></div>
        <div class="camp-eticheta" style="color:var(--gri)">IBAN românesc (RO + 22 caractere); gol = fără plată pe card.</div>
        <div id="iban-msg"></div>`;
      const inp = corp.querySelector("#iban-input"); inp.focus();
      corp.querySelector("#iban-cancel").addEventListener("click", () => { zonaIban.innerHTML = ""; });
      corp.querySelector("#iban-save").addEventListener("click", async () => {
        const iban = inp.value.trim().replace(/\s/g, "").toUpperCase();
        try {
          await api.put(`/tenants/${t.id}/salariati/${sid}`, { iban });  // "" = sterge (goleste contul)
          zonaIban.innerHTML = ""; deseneaza();
        } catch (e) { arataMesaj(corp.querySelector("#iban-msg"), (e && e.mesaj) || "Eroare la salvare.", "eroare"); }
      });
    }));
    // PASUL 1: incetarea contractului (data_incetare). Marcheaza PLECAREA - inlocuieste stergerea la
    // plecare (istoricul sustine declaratiile depuse). DESIGN_SYSTEM cap.5 (INPUT): input in-ecran + buton.
    const zonaIncet = corp.querySelector("#sp-incet-zona");
    // [salariu_edit] editarea salariului de baza (schimbare de salariu -> intrare noua in salariu_istoric).
    // Cabla PUT /salariati/{id} {salariu_brut, valabil_din} (necablat pana acum) + repara cazul baza_lipsa.
    const zonaSalariu = corp.querySelector("#sp-salariu-zona");
    corp.querySelectorAll("[data-salariu]").forEach((b) => b.addEventListener("click", () => {
      const sid = b.dataset.salariu;
      const azi = new Date().toISOString().slice(0, 10);
      zonaSalariu.innerHTML = `<div style="display:flex;gap:8px;align-items:center;margin:10px 0;flex-wrap:wrap">
        <span class="camp-eticheta">Salariu de bază · ${esc(b.dataset.nume)}:</span>
        <input type="number" min="0" step="0.01" id="salariu-input" class="camp-input" value="${esc(b.dataset.val)}" style="width:140px">
        <span class="camp-eticheta">de la:</span>
        <input type="date" id="salariu-data" class="camp-input" value="${azi}" style="width:160px">
        <button class="buton-primar" id="salariu-save">Salvează</button>
        <button class="buton-secundar" id="salariu-cancel">Renunță</button></div>
        <div class="camp-eticheta" style="color:var(--gri)">Salariul de bază brut lunar (lei), din contractul de muncă (mai mare ca 0). „De la" = data de când e valabil: o mărire creează o intrare nouă în istoric; o corecție pune data angajării.</div>
        <div id="salariu-msg"></div>`;
      corp.querySelector("#salariu-input").focus();
      // [R28, decizia lui Costin 24.08.2026 - varianta 3: NIMIC] Aici se afisa „Net estimat: X lei"
      // si un avertisment cu doua cifre de net, calculate prin /salariu-efect. S-au SCOS, nu s-au
      // corectat. Motivul e masurat, nu de gust: ruta chema calcul_salariu(brut, la_data) - deci
      // din 18 parametri pasa DOI, iar restul luau valorile implicite: persoane=0, sub_26=False,
      // copii_scoala=0, norma_intreaga=True, data_angajare=None. Pentru un salariat cu persoane in
      // intretinere, sub 26 de ani, cu norma partiala sau angajat la mijloc de luna, cifra afisata
      // NU putea coincide cu fluturasul de peste o luna. La angajare se negociaza BRUTUL; netul si
      // costul angajatorului se calculeaza dupa salvare, cu toate elementele.
      corp.querySelector("#salariu-cancel").addEventListener("click", () => { zonaSalariu.innerHTML = ""; });
      corp.querySelector("#salariu-save").addEventListener("click", async () => {
        const val = Number(corp.querySelector("#salariu-input").value);
        const valabil_din = corp.querySelector("#salariu-data").value || null;
        if (!(val > 0)) { arataMesaj(corp.querySelector("#salariu-msg"), "Salariul de bază trebuie să fie mai mare ca 0.", "eroare"); return; }
        try {
          await api.put(`/tenants/${t.id}/salariati/${sid}`, { salariu_brut: val, valabil_din });
          zonaSalariu.innerHTML = ""; deseneaza();
        } catch (e) { arataMesaj(corp.querySelector("#salariu-msg"), (e && e.mesaj) || "Eroare la salvare.", "eroare"); }
      });
    }));
    corp.querySelectorAll("[data-incet]").forEach((b) => b.addEventListener("click", () => {
      const sid = b.dataset.incet;
      zonaIncet.innerHTML = `<div style="display:flex;gap:8px;align-items:center;margin:10px 0;flex-wrap:wrap">
        <span class="camp-eticheta">Data încetării contractului · ${esc(b.dataset.nume)}:</span>
        <input type="date" id="incet-input" class="camp-input" value="${esc(b.dataset.val)}" style="width:180px">
        <button class="buton-primar" id="incet-save">Salvează</button>
        <button class="buton-secundar" id="incet-cancel">Renunță</button></div>
        <div class="camp-eticheta" style="color:var(--gri)">Gol = contract activ. La plecare NU se șterge salariatul — se completează data încetării (istoricul susține declarațiile depuse).</div>
        <div id="incet-msg"></div>`;
      corp.querySelector("#incet-input").focus();
      corp.querySelector("#incet-cancel").addEventListener("click", () => { zonaIncet.innerHTML = ""; });
      corp.querySelector("#incet-save").addEventListener("click", async () => {
        const data_incetare = corp.querySelector("#incet-input").value || null;
        try {
          await api.put(`/tenants/${t.id}/salariati/${sid}`, { data_incetare });
          zonaIncet.innerHTML = ""; deseneaza();
        } catch (e) { arataMesaj(corp.querySelector("#incet-msg"), (e && e.mesaj) || "Eroare la salvare.", "eroare"); }
      });
    }));
    // [front_e] corectarea datelor de identitate/contract (nume/prenume/CNP/data angajare/norma).
    // Backend-ul (SalariatEdit + _CAMPURI_API) le accepta deja; UI-ul nu le cabla -> o eroare de tastare
    // in nume/CNP nu se putea corecta din UI (MEMORY §13). CNP validat client-side (checksum) inainte de PUT.
    const zonaDate = corp.querySelector("#sp-date-zona");
    const cnpValid = (c) => {
      if (!/^\d{13}$/.test(c)) return false;
      const w = [2,7,9,1,4,6,3,5,8,2,7,9]; let sm = 0;
      for (let i = 0; i < 12; i++) sm += (+c[i]) * w[i];
      let ctrl = sm % 11; if (ctrl === 10) ctrl = 1;
      return ctrl === (+c[12]);
    };
    corp.querySelectorAll("[data-date]").forEach((b) => b.addEventListener("click", () => {
      const sid = b.dataset.date;
      const norma = b.dataset.dnorma || "intreaga";
      zonaDate.innerHTML = `<div style="margin:10px 0;padding:12px;border:1px solid var(--linie);border-radius:var(--raza)">
        <div class="camp-eticheta" style="font-weight:600;margin-bottom:8px">Corectează datele salariatului</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px">
          <label class="camp"><span class="camp-eticheta">Nume</span><input id="ed-nume" class="camp-input" value="${esc(b.dataset.dnume)}"></label>
          <label class="camp"><span class="camp-eticheta">Prenume</span><input id="ed-pren" class="camp-input" value="${esc(b.dataset.dpren)}"></label>
          <label class="camp"><span class="camp-eticheta">CNP</span><input id="ed-cnp" class="camp-input" inputmode="numeric" maxlength="13" value="${esc(b.dataset.dcnp)}"></label>
          <label class="camp"><span class="camp-eticheta">Data angajării</span><input type="date" id="ed-ang" class="camp-input" value="${esc(b.dataset.dang)}"></label>
          <label class="camp"><span class="camp-eticheta">Normă</span><select id="ed-norma" class="camp-input">
            <option value="intreaga" ${norma === "intreaga" ? "selected" : ""}>Întreagă (8h)</option>
            <option value="partiala" ${norma === "partiala" ? "selected" : ""}>Parțială</option></select></label>
          <label class="camp"><span class="camp-eticheta">Ore/zi</span><input type="number" min="1" max="8" step="0.5" id="ed-orezi" class="camp-input" value="${esc(b.dataset.dorezi)}"></label>
        </div>
        <div class="camp-eticheta" style="color:var(--gri);margin-top:6px">Corectarea acestor date NU modifică declarațiile deja depuse. CNP-ul se validează la salvare.</div>
        <p style="margin-top:8px"><button class="buton-primar" id="ed-save">Salvează</button>
          <button class="buton-secundar" id="ed-cancel" style="margin-left:6px">Renunță</button></p>
        <div id="ed-msg"></div></div>`;
      corp.querySelector("#ed-nume").focus();
      corp.querySelector("#ed-cancel").addEventListener("click", () => { zonaDate.innerHTML = ""; });
      corp.querySelector("#ed-save").addEventListener("click", async () => {
        const msg = corp.querySelector("#ed-msg");
        const nume = corp.querySelector("#ed-nume").value.trim();
        const prenume = corp.querySelector("#ed-pren").value.trim();
        const cnp = corp.querySelector("#ed-cnp").value.trim();
        const data_angajare = corp.querySelector("#ed-ang").value || null;
        const tip_norma = corp.querySelector("#ed-norma").value;
        const ore_zi = Number(corp.querySelector("#ed-orezi").value) || null;
        if (!nume) { arataMesaj(msg, "Numele e obligatoriu.", "eroare"); return; }
        if (!cnpValid(cnp)) { arataMesaj(msg, "CNP invalid (13 cifre, cifră de control greșită).", "eroare"); return; }
        try {
          await api.put(`/tenants/${t.id}/salariati/${sid}`, { nume, prenume, cnp, data_angajare, tip_norma, ore_zi });
          zonaDate.innerHTML = ""; deseneaza();
        } catch (e) { arataMesaj(msg, (e && e.mesaj) || "Eroare la salvare.", "eroare"); }
      });
    }));
    // [F137] cod ocupatie COR: lookup din nomenclator, editabil pe rand (necesar REGES)
    const zonaCor = corp.querySelector("#sp-cor-zona");
    corp.querySelectorAll("[data-cor]").forEach((b) => b.addEventListener("click", () => {
      const sid = b.dataset.cor;
      zonaCor.innerHTML = `<div style="margin:10px 0;max-width:520px">
        <div class="camp-eticheta" style="margin-bottom:6px">Ocupație COR · ${esc(b.dataset.nume)}:</div>
        ${campCorLookup("cor-edit")}
        <p style="margin-top:8px"><button class="buton-primar" id="cor-save">Salvează</button>
          <button class="buton-secundar" id="cor-cancel" style="margin-left:6px">Renunță</button></p>
        <div id="cor-msg"></div></div>`;
      legaCorLookup(zonaCor, "cor-edit", b.dataset.val);
      corp.querySelector("#cor-cancel").addEventListener("click", () => { zonaCor.innerHTML = ""; });
      corp.querySelector("#cor-save").addEventListener("click", async () => {
        const cor = corp.querySelector("#cor-edit-cor").value.trim();
        try {
          await api.put(`/tenants/${t.id}/salariati/${sid}`, { cor });  // "" = sterge; cod invalid respins de backend
          zonaCor.innerHTML = ""; deseneaza();
        } catch (e) { arataMesaj(corp.querySelector("#cor-msg"), (e && e.mesaj) || "Eroare la salvare.", "eroare"); }
      });
    }));
    corp.querySelectorAll("[data-reges]").forEach((b) => b.addEventListener("click", () => {
      const sid = parseInt(b.dataset.reges);
      zonaReges.innerHTML = `<div style="display:block;margin:10px 0;max-width:520px">
        <div class="camp"><span class="camp-eticheta">Adresa salariatului<span class="oblig">*</span></span>
          <input type="text" id="rg-adresa" class="camp-input" placeholder="strada, nr, localitate, judet">
          <span class="camp-ajutor">Obligatorie pentru transmiterea in REGES.</span></div>
        <p style="margin-top:10px"><button class="buton-primar" id="rg-trimite">Trimite \u00een REGES</button>
          <button class="btn-link" id="rg-renunta" style="margin-left:10px">Renun\u021b\u0103</button></p>
        <div id="rg-rez"></div></div>`;
      zonaReges.querySelector("#rg-renunta").addEventListener("click", () => { zonaReges.innerHTML = ""; });
      zonaReges.querySelector("#rg-trimite").addEventListener("click", async () => {
        const adresa = zonaReges.querySelector("#rg-adresa").value.trim();
        const rez = zonaReges.querySelector("#rg-rez");
        if (!adresa) { rez.innerHTML = `<span class="msg-eroare">Completeaza adresa salariatului.</span>`; return; }
        const btn = zonaReges.querySelector("#rg-trimite");
        btn.disabled = true; btn.textContent = "Se trimite\u2026";
        try {
          const r = await api.post(`/tenants/${t.id}/reges-trimite-salariat`, { salariat_id: sid, adresa });
          zonaReges.innerHTML = `<p class="pf-intro">Trimis in REGES${r.referinta ? " \u00b7 ref " + r.referinta : ""}. Verifica R\u0103spunsuri REGES.</p>`;
        } catch (e) { btn.disabled = false; btn.textContent = "Trimite \u00een REGES"; rez.innerHTML = `<span class="msg-eroare">${esc(e.mesaj || "eroare")}</span>`; }
      });
    }));
    corp.querySelectorAll("[data-flut]").forEach((b) => {
      b.addEventListener("click", async () => {
        try {
          const resp = await fetch(`/tenants/${t.id}/fluturas/${b.dataset.flut}?an=${an}&luna=${luna}`, {
            headers: { "Authorization": "Bearer " + sesiune.token() }
          });
          if (!resp.ok) throw new Error();
          const blob = await resp.blob();
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url; a.download = `fluturas_${an}_${String(luna).padStart(2,"0")}.pdf`; a.click();
          URL.revokeObjectURL(url);
        } catch {
          b.parentElement.querySelectorAll(".msg-eroare").forEach((x) => x.remove());
          b.insertAdjacentHTML("afterend", '<span class="msg-eroare" style="margin-left:8px">Nu am putut genera fluturașul.</span>');
        }
      });
    });
  };
  deseneaza();
}




// [stocuri-cv] Fise de magazie (cantitativ-valoric)
export async function sectiuneaCV(corp, t, zonaM) {
  const zona = corp.querySelector("#cv-zona");
  let arts = [];
  try { const r = await api.get(`/tenants/${t.id}/stocuri/articole`); arts = r.articole || []; } catch {}
  let locInit = [];
  try { const r = await api.get(`/tenants/${t.id}/stocuri/locatii`); locInit = r.locatii || []; } catch {}
  zona.innerHTML = `
    <div style="display:block;margin-bottom:14px">
      <div class="pf-frand-nume" style="margin-bottom:8px">Fi\u0219e de magazie (cantitativ-valoric, CMP)</div>
      <div class="camp-eticheta">Mi\u0219care: articol \u00b7 denumire (nou) \u00b7 dat\u0103 \u00b7 cantitate \u00b7 pre\u021b unitar \u00b7 document</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
        <select id="cv-art" aria-label="Articol" class="camp-input" style="min-width:200px">
          <option value="">\u2014 articol nou \u2014</option>
          ${arts.map((a) => `<option value="${a.id}">${esc(a.denumire)} \u00b7 stoc ${a.stoc} ${esc(a.um)}${a.cmp ? " \u00b7 CMP " + a.cmp : ""}${a.barcode ? " \u00b7 cod " + esc(a.barcode) : ""}</option>`).join("")}
        </select>
        <input type="text" id="cv-den" class="camp-input" placeholder="denumire (articol nou)" aria-label="Denumire articol nou" style="flex:1;min-width:160px">
        <input type="date" id="cv-data" aria-label="Data document" class="camp-input">
        <input type="number" step="0.001" id="cv-cant" class="camp-input" placeholder="cant." aria-label="Cantitate" style="width:90px">
        <input type="number" step="0.0001" id="cv-pret" class="camp-input" placeholder="pret unitar (la intrare)" aria-label="Pre\u021b unitar la intrare" style="width:170px">
        <input type="text" id="cv-doc" class="camp-input" placeholder="document" aria-label="Document" style="width:130px">
        <input type="text" id="cv-loc" class="camp-input" placeholder="locație" aria-label="Locație" list="cv-loc-list" style="width:120px">
        <datalist id="cv-loc-list">${[...new Set((locInit || []).map((x) => x.locatie).filter((l) => l && l !== "(nespecificat)"))].map((l) => `<option value="${esc(l)}">`).join("")}</datalist>
      </div>
      <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-bottom:8px">
        <input type="text" id="cv-bc" class="camp-input" placeholder="cod de bare (scaneaz\u0103/tasteaz\u0103)" aria-label="Cod de bare" style="width:220px">
        <button class="buton-secundar" id="cv-bc-cauta">Caut\u0103 articol dup\u0103 cod</button>
        <button class="buton-secundar" id="cv-bc-set">Atribuie codul articolului selectat</button>
        <input type="number" step="0.001" id="cv-nm" class="camp-input" placeholder="nivel minim" aria-label="Nivel minim de stoc" style="width:120px">
        <button class="buton-secundar" id="cv-nm-set">Salveaz\u0103 nivelul minim</button>
      </div>
      <p>
        <button class="buton-primar" id="cv-intrare">Intrare</button>
        <button class="buton-primar" id="cv-iesire" style="margin-left:6px">Ie\u0219ire la CMP (nota ciorn\u0103)</button>
        <button class="buton-secundar" id="cv-fisa" style="margin-left:6px">Vezi fi\u0219a</button>
      </p>
      <div style="margin-top:10px">
        <button class="buton-secundar" id="cv-inv">Inventar (stoc faptic)</button>
        <button class="buton-secundar" id="cv-loc-vezi" style="margin-left:6px">Stoc pe locații</button>
        <button class="buton-secundar" id="cv-transfer-t" style="margin-left:6px">Transfer între locații</button>
        <button class="buton-secundar" id="cv-recl-t" style="margin-left:6px">Reclasificare tip produs</button>
        <button class="buton-secundar" id="cv-ana" style="margin-left:6px">Analitică stoc</button>
        <button class="buton-secundar" id="cv-inv-mobil" style="margin-left:6px">Inventar pe mobil</button>
        <div id="cv-inv-zona" style="margin-top:8px"></div>
        <div id="cv-loc-zona" style="margin-top:8px"></div>
      </div>
      <div id="cv-fisa-zona"></div>
      <div class="pf-card" style="margin-top:14px">
        <h3 class="pf-subtitlu">Re\u021bete (HoReCa)</h3>
        <div id="rt-lista"></div>
        <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;align-items:flex-end">
          <label class="camp"><span class="camp-eticheta">Denumire</span><input class="camp-input" id="rt-den" placeholder="ex. Meniu zilei"></label>
          <label class="camp"><span class="camp-eticheta">Pre\u021b f\u0103r\u0103 TVA</span><input class="camp-input" type="number" step="0.01" id="rt-pret" style="width:110px"></label>
          <button class="buton-secundar" id="rt-plus">+ ingredient</button>
          <button class="buton-primar" id="rt-salveaza">Salveaz\u0103 re\u021beta</button>
        </div>
        <div id="rt-ingrediente"></div>
      </div>

    </div>`;
  const val = (id) => zona.querySelector(id).value;
  // [F141] Coduri de bare: cauta articolul dupa cod / atribuie cod articolului selectat
  zona.querySelector("#cv-bc-cauta").addEventListener("click", async () => {
    const cod = val("#cv-bc").trim();
    if (!cod) { arataMesaj(zonaM, "Scanează sau tastează un cod de bare.", "eroare"); return; }
    try {
      const a = await api.get(`/tenants/${t.id}/stocuri/barcode/${encodeURIComponent(cod)}`);
      zona.querySelector("#cv-art").value = String(a.id);
      arataMesaj(zonaM, `Selectat: ${esc(a.denumire)}.`, "ok");
    } catch (e) { arataMesaj(zonaM, e.mesaj || "Niciun articol cu acest cod.", "eroare"); }
  });
  zona.querySelector("#cv-bc-set").addEventListener("click", async () => {
    if (!val("#cv-art")) { arataMesaj(zonaM, "Alege întâi articolul din listă.", "eroare"); return; }
    try {
      const r = await api.post(`/tenants/${t.id}/stocuri/articole/${parseInt(val("#cv-art"))}/barcode`, { barcode: val("#cv-bc").trim() });
      arataMesaj(zonaM, r.barcode ? `Cod „${esc(r.barcode)}” atribuit articolului.` : "Cod șters de pe articol.", "ok");
      sectiuneaCV(corp, t, zonaM);
    } catch (e) { arataMesaj(zonaM, e.mesaj || "Eroare la salvarea codului.", "eroare"); }
  });
  // [F140] Nivel minim de stoc (prag pentru stoc critic / necesar aprovizionare)
  zona.querySelector("#cv-nm-set").addEventListener("click", async () => {
    if (!val("#cv-art")) { arataMesaj(zonaM, "Alege întâi articolul din listă.", "eroare"); return; }
    try {
      const r = await api.post(`/tenants/${t.id}/stocuri/articole/${parseInt(val("#cv-art"))}/nivel-minim`, { nivel_minim: val("#cv-nm").trim() });
      arataMesaj(zonaM, r.nivel_minim ? `Nivel minim ${r.nivel_minim} setat.` : "Nivel minim șters.", "ok");
      sectiuneaCV(corp, t, zonaM);
    } catch (e) { arataMesaj(zonaM, e.mesaj || "Eroare la salvarea nivelului minim.", "eroare"); }
  });
  zona.querySelector("#cv-intrare").addEventListener("click", async () => {
    try {
      const corpReq = { data: val("#cv-data"), cantitate: parseFloat(val("#cv-cant")) || 0,
        pret_unitar: parseFloat(val("#cv-pret")) || 0, document: val("#cv-doc") || null,
        locatie: val("#cv-loc") || null };
      if (val("#cv-art")) corpReq.articol_id = parseInt(val("#cv-art"));
      else corpReq.denumire = val("#cv-den").trim();
      if (!corpReq.articol_id && !corpReq.denumire) { arataMesaj(zonaM, "Alege articolul sau da-i un nume.", "avert"); return; }
      const r = await api.post(`/tenants/${t.id}/stocuri/intrare`, corpReq);
      zonaM.innerHTML = `<p class="pf-intro">Intrare inregistrata \u00b7 ${bani(r.valoare)} lei.</p>`;
      sectiuneaCV(corp, t, zonaM);
    } catch (e) { arataMesaj(zonaM, e.mesaj || "eroare", "eroare"); }
  });
  zona.querySelector("#cv-iesire").addEventListener("click", async () => {
    if (!val("#cv-art")) { arataMesaj(zonaM, "Alege articolul pentru iesire.", "avert"); return; }
    try {
      const r = await api.post(`/tenants/${t.id}/stocuri/iesire`, {
        articol_id: parseInt(val("#cv-art")), data: val("#cv-data"),
        cantitate: parseFloat(val("#cv-cant")) || 0, document: val("#cv-doc") || null,
        locatie: val("#cv-loc") || null });
      zonaM.innerHTML = `<p class="pf-intro">Ieșire la CMP ${r.cmp} \u00b7 ${bani(r.valoare)} lei \u00b7 notă ${esc(r.nota)} (ciornă).</p>`;
      sectiuneaCV(corp, t, zonaM);
    } catch (e) { arataMesaj(zonaM, e.mesaj || "eroare", "eroare"); }
  });


  // [retete_v1] Retete HoReCa: CRUD + descarcare pe reteta + food cost
  const rtLista = zona.querySelector("#rt-lista");
  const rtIng = zona.querySelector("#rt-ingrediente");
  let rtLinii = [];
  const rtDeseneazaIng = () => {
    // cap.24: id-uri pozitionale rt-l{i}-* (backendul leaga eroarea de camp, cap.6); re-randare integrala din
    // model (regula 1); buton de stergere pe fiecare rand (regula 3).
    rtIng.innerHTML = rtLinii.map((l, i) => `
      <div class="em-linie" data-idx="${i}">
        <select class="camp-input rt-art" id="rt-l${i}-articol" data-i="${i}" aria-label="Articol ingredient">${arts.map((a) =>
          `<option value="${a.id}" ${a.id == l.articol_id ? "selected" : ""}>${esc(a.denumire)} · CMP ${a.cmp}</option>`).join("")}</select>
        <input class="camp-input rt-cant" id="rt-l${i}-cantitate" data-i="${i}" type="number" step="0.001" value="${l.cantitate || ""}" placeholder="cant./porție" aria-label="Cantitate pe porție" style="width:120px">
        <button type="button" class="buton-sters rt-scoate" data-i="${i}" title="Șterge">−</button>
      </div>`).join("");
    rtIng.querySelectorAll(".rt-art").forEach((s) => s.addEventListener("change", (e) => { rtLinii[e.target.dataset.i].articol_id = parseInt(e.target.value); }));
    rtIng.querySelectorAll(".rt-cant").forEach((s) => s.addEventListener("input", (e) => { rtLinii[e.target.dataset.i].cantitate = parseFloat(e.target.value); }));
    rtIng.querySelectorAll(".rt-scoate").forEach((b) => b.addEventListener("click", (e) => { rtLinii.splice(e.target.dataset.i, 1); rtDeseneazaIng(); }));
  };
  const rtIncarca = async () => {
    let rr = [];
    try { const r = await api.get(`/tenants/${t.id}/retete`); rr = r.retete || []; } catch { rtLista.innerHTML = `<p class="ecran-nota">Nu am putut încărca rețetele.</p>`; return; }
    rtLista.innerHTML = !rr.length ? `<div class="stare-goala">Nicio re\u021bet\u0103 \u00eenc\u0103.</div>`
      : rr.map((r) => {
          const fc = r.food_cost || {};
          const procent = fc.food_cost_pct == null ? "\u2013" : pct(fc.food_cost_pct);
          return `<div class="pf-frand">
            <div class="pf-frand-text">
              <div class="pf-frand-nume">${esc(r.denumire)} \u00b7 ${bani(r.pret_fara_tva)} lei</div>
              <div class="pf-frand-sub">cost/por\u021bie ${bani(fc.cost_portie)} \u00b7 food cost ${procent} \u00b7 ${(r.linii || []).map((l) => `${esc(l.denumire)} ${l.cantitate}${esc(l.um || "")}`).join(", ")}</div>
            </div>
            <input class="camp-input rt-portii" data-id="${r.id}" type="number" placeholder="por\u021bii" aria-label="Num\u0103r por\u021bii" style="width:80px">
            <button class="buton-primar rt-desc" data-id="${r.id}">Descarc\u0103 (ciorn\u0103)</button>
            <button class="buton-sters rt-del" data-id="${r.id}">\u0218terge</button>
          </div>`;
        }).join("");
    rtLista.querySelectorAll(".rt-desc").forEach((b) => b.addEventListener("click", async (e) => {
      const id = e.target.dataset.id;
      const p = rtLista.querySelector(`.rt-portii[data-id="${id}"]`).value;
      if (!p) { arataMesaj(zonaM, "Completeaz\u0103 num\u0103rul de por\u021bii.", "eroare"); return; }
      try {
        const r = await api.post(`/tenants/${t.id}/retete/descarca`, { reteta_id: parseInt(id), portii: parseFloat(p), data: val("#cv-data") || new Date().toISOString().slice(0, 10) });
        arataMesaj(zonaM, `Consum \u00eenregistrat (ciorn\u0103 #${r.inregistrare_id}) \u00b7 cost total ${bani(r.cost_total)} lei.`, "ok");
        sectiuneaCV(corp, t, zonaM); rtIncarca();
      } catch (er) { arataMesaj(zonaM, er.mesaj || "Eroare la desc\u0103rcare.", "eroare"); }
    }));
    rtLista.querySelectorAll(".rt-del").forEach((b) => b.addEventListener("click", async (e) => {
      try { await api.del(`/tenants/${t.id}/retete/${e.target.dataset.id}`); rtIncarca(); } catch (er) { arataMesaj(zonaM, er.mesaj || "Nu am putut \u0219terge re\u021beta.", "eroare"); }
    }));
  };
  zona.querySelector("#rt-plus").addEventListener("click", () => { rtLinii.push({ articol_id: arts[0] && arts[0].id, cantitate: "" }); rtDeseneazaIng(); });
  zona.querySelector("#rt-salveaza").addEventListener("click", async () => {
    curataEroriCamp(zona);
    const den = zona.querySelector("#rt-den").value.trim();
    // NU se filtreaza randuri (cap.24 regula 2): lista trimisa = lista randata. Backendul valideaza per-linie si
    // raporteaza langa campul lipsa (rt-l{i}-..), nu se arunca tacit un ingredient inceput.
    const linii = rtLinii.map((l) => ({ articol_id: l.articol_id, cantitate: l.cantitate }));
    try {
      await api.post(`/tenants/${t.id}/retete`, { denumire: den, pret_fara_tva: parseFloat(zona.querySelector("#rt-pret").value || 0), linii });
      zona.querySelector("#rt-den").value = ""; zona.querySelector("#rt-pret").value = ""; rtLinii = []; rtDeseneazaIng(); rtIncarca();
    } catch (er) {
      curataEroriCamp(zona);
      const eris = (er && er.erori_campuri) || [];
      const rest = [];
      eris.forEach((x) => { if (!eroareCamp(zona, x.camp, x.mesaj)) rest.push(x.mesaj); });
      arataMesaj(zonaM, (rest.length ? rest.join("; ") : (er.mesaj || "Eroare la salvare.")), "eroare");
    }
  });
  rtIncarca();

  zona.querySelector("#cv-inv").addEventListener("click", () => {
    const z = zona.querySelector("#cv-inv-zona");
    z.innerHTML = `<div class="pf-lista">${arts.map((a) => `
      <div class="pf-frand"><div class="pf-frand-text">
        <div class="pf-frand-nume">${esc(a.denumire)} \u00b7 scriptic ${a.stoc} ${esc(a.um)}</div>
      </div>
      <input type="number" step="0.001" class="camp-input cvi-faptic" id="cvi-a${a.id}-faptic" data-aid="${a.id}" placeholder="faptic" aria-label="Stoc faptic" style="width:110px"></div>`).join("")}
      <p style="margin-top:8px"><button class="buton-primar" id="cvi-salveaza">Salveaz\u0103 inventarul (note ciorne)</button></p>`;
    z.querySelector("#cvi-salveaza").addEventListener("click", async () => {
      curataEroriCamp(z);
      // NU se filtreaza randuri (cap.24 regula 2): se trimit TOATE articolele; backendul e autoritatea (sare
      // articolele necontorizate = faptic gol, NU e eroare; eroare per-linie doar la valoare invalida).
      const linii = [...z.querySelectorAll(".cvi-faptic")]
        .map((i) => ({ articol_id: parseInt(i.dataset.aid), faptic: i.value.trim() === "" ? null : i.value.trim() }));
      if (!linii.some((l) => l.faptic !== null)) { arataMesaj(zonaM, "Completeaza stocul faptic la cel putin un articol.", "avert"); return; }
      try {
        const r = await api.post(`/tenants/${t.id}/stocuri/inventar`,
          { data: val("#cv-data"), linii });
        curataEroriCamp(z);
        const rezultate = r.rezultate || [];
        const cuEroare = rezultate.filter((x) => x.eroare && x.camp);
        cuEroare.forEach((x) => eroareCamp(z, x.camp, x.eroare));
        const rest = rezultate.filter((x) => !(x.eroare && x.camp));
        zonaM.innerHTML = `<p class="pf-intro">${rest.map((x) =>
          x.eroare ? `${esc(x.denumire || x.articol_id)}: ${esc(x.eroare)}`
          : x.diferenta === "0" ? `${esc(x.denumire)}: fara diferenta`
          : `${esc(x.denumire)}: ${x.diferenta > 0 ? "plus" : "minus"} ${x.diferenta} · ${bani(x.valoare)} lei · nota ${esc(x.nota)} (ciorna)`).join("<br>")}</p>`;
        if (!cuEroare.length) sectiuneaCV(corp, t, zonaM);   // refresh doar cand nu sunt erori de camp de aratat
      } catch (e) { arataMesaj(zonaM, e.mesaj || "eroare", "eroare"); }
    });
  });
  // [F138 Tier 1] Locatii descriptive + transfer (CMP global) + reclasificare tip produs
  const optArts = (arts || []).map((a) => `<option value="${a.id}">${esc(a.denumire)} · stoc ${a.stoc} ${esc(a.um)}</option>`).join("");
  const locZona = zona.querySelector("#cv-loc-zona");
  zona.querySelector("#cv-loc-vezi").addEventListener("click", async () => {
    try {
      const r = await api.get(`/tenants/${t.id}/stocuri/locatii`);
      const l = r.locatii || [];
      locZona.innerHTML = !l.length ? `<div class="stare-goala">Nicio locație cu stoc încă.</div>`
        : `<div class="pf-frand-nume" style="margin:4px 0">Stoc pe locații (cantitativ; CMP rămâne global)</div>
           <div class="pf-lista">${l.map((x) => `
             <div class="pf-frand"><div class="pf-frand-text">
               <div class="pf-frand-nume">${esc(x.denumire)} · ${esc(x.locatie)}</div>
               <div class="pf-frand-sub">${x.cantitate} ${esc(x.um)}</div>
             </div></div>`).join("")}</div>`;
    } catch (e) { arataMesaj(locZona, e.mesaj || "eroare", "eroare"); }
  });
  zona.querySelector("#cv-transfer-t").addEventListener("click", () => {
    locZona.innerHTML = `
      <div class="pf-card">
        <div class="pf-frand-nume" style="margin-bottom:6px">Transfer între locații (fără notă contabilă, CMP global)</div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center">
          <select id="tr-art" class="camp-input" style="min-width:200px">${optArts}</select>
          <input type="text" id="tr-din" class="camp-input" placeholder="din locație" aria-label="Din locație" list="cv-loc-list" style="width:130px">
          <input type="text" id="tr-in" class="camp-input" placeholder="în locație" aria-label="În locație" list="cv-loc-list" style="width:130px">
          <input type="number" step="0.001" id="tr-cant" class="camp-input" placeholder="cant." aria-label="Cantitate" style="width:90px">
          <input type="date" id="tr-data" class="camp-input">
          <button class="buton-primar" id="tr-ok">Transferă</button>
        </div>
      </div>`;
    locZona.querySelector("#tr-ok").addEventListener("click", async () => {
      const g = (id) => locZona.querySelector(id).value;
      try {
        const r = await api.post(`/tenants/${t.id}/stocuri/transfer`, {
          articol_id: parseInt(g("#tr-art")), din_locatie: g("#tr-din") || null,
          in_locatie: g("#tr-in") || null, cantitate: parseFloat(g("#tr-cant")) || 0, data: g("#tr-data") });
        arataMesaj(zonaM, `Transfer ${r.cantitate} din „${esc(r.din_locatie)}” în „${esc(r.in_locatie)}” · ${bani(r.valoare)} lei la CMP ${r.cmp}.`, "ok");
        sectiuneaCV(corp, t, zonaM);
      } catch (e) { arataMesaj(zonaM, e.mesaj || "Eroare la transfer.", "eroare"); }
    });
  });
  zona.querySelector("#cv-recl-t").addEventListener("click", () => {
    locZona.innerHTML = `
      <div class="pf-card">
        <div class="pf-frand-nume" style="margin-bottom:6px">Reclasificare tip produs (ex. materie primă 301 → marfă 371)</div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center">
          <select id="rc-art" class="camp-input" style="min-width:200px">${optArts}</select>
          <input type="text" id="rc-cont" class="camp-input" placeholder="cont stoc nou (ex. 371)" aria-label="Cont stoc nou" style="width:150px">
          <input type="text" id="rc-chelt" class="camp-input" placeholder="cont cheltuială nou (ex. 607)" aria-label="Cont cheltuială nou" style="width:170px">
          <input type="date" id="rc-data" class="camp-input">
          <button class="buton-primar" id="rc-ok">Reclasifică</button>
        </div>
        <div class="camp-eticheta" style="margin-top:4px">Emite notă ciornă de reclasificare a soldului (cont nou = cont vechi) la CMP curent. Cantitatea nu se modifică.</div>
      </div>`;
    locZona.querySelector("#rc-ok").addEventListener("click", async () => {
      const g = (id) => locZona.querySelector(id).value;
      try {
        const r = await api.post(`/tenants/${t.id}/stocuri/reclasificare`, {
          articol_id: parseInt(g("#rc-art")), cont_stoc_nou: g("#rc-cont").trim(),
          cont_cheltuiala_nou: g("#rc-chelt").trim() || null, data: g("#rc-data") });
        arataMesaj(zonaM, r.nota
          ? `Reclasificat „${esc(r.denumire)}” din ${esc(r.cont_stoc_vechi)} în ${esc(r.cont_stoc)} · notă ${esc(r.nota)} ${bani(r.valoare_reclasificata)} lei (ciornă).`
          : `Reclasificat „${esc(r.denumire)}” în ${esc(r.cont_stoc)} (fără sold de reclasificat).`, "ok");
        sectiuneaCV(corp, t, zonaM);
      } catch (e) { arataMesaj(zonaM, e.mesaj || "Eroare la reclasificare.", "eroare"); }
    });
  });
  // [F142] Inventar pe mobil: scanare cod (keyboard-wedge) -> acumulare in timp real -> finalizare.
  // Numarare oarba (nu afiseaza scripticul). Fara schema noua: foloseste motorul inventar() existent.
  zona.querySelector("#cv-inv-mobil").addEventListener("click", () => {
    const z = zona.querySelector("#cv-inv-zona");
    const num = {};  // articol_id -> {denumire, um, faptic}
    const randList = () => Object.entries(num).map(([id, x]) =>
      `<div class="pf-frand"><div class="pf-frand-text">
         <div class="pf-frand-nume">${esc(x.denumire)}</div>
         <div class="pf-frand-sub">numărat ${x.faptic} ${esc(x.um)}</div>
       </div><button class="buton-sters im-scoate" data-id="${id}">−</button></div>`).join("");
    const deseneaza = () => {
      z.innerHTML = `
        <div class="pf-card">
          <div class="pf-frand-nume" style="margin-bottom:6px">Inventar pe mobil (numărare oarbă)</div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center">
            <input type="text" id="im-scan" class="camp-input" placeholder="scanează codul sau caută denumirea" aria-label="Scanează cod sau caută" style="flex:1;min-width:180px">
            <input type="number" step="0.001" id="im-cant" class="camp-input" placeholder="cant. (1)" aria-label="Cantitate numărată" style="width:100px">
            <button class="buton-primar" id="im-add">Adaugă la numărătoare</button>
          </div>
          <div id="im-hint" class="camp-eticheta" style="margin-top:4px"></div>
          <div class="pf-lista" style="margin-top:8px">${randList() || '<div class="stare-goala">Nimic numărat încă.</div>'}</div>
          <p style="margin-top:8px"><button class="buton-primar" id="im-fin">Finalizează inventarul (note ciorne)</button></p>
        </div>`;
      const scan = z.querySelector("#im-scan");
      scan.focus();
      const adauga = async () => {
        const q = scan.value.trim();
        if (!q) return;
        const cant = parseFloat(z.querySelector("#im-cant").value) || 1;
        let a = null;
        try { a = await api.get(`/tenants/${t.id}/stocuri/barcode/${encodeURIComponent(q)}`); } catch {}
        if (!a) {
          const m = arts.filter((x) => x.denumire.toLowerCase().includes(q.toLowerCase()));
          if (m.length === 1) a = m[0];
          else { z.querySelector("#im-hint").textContent = m.length ? `${m.length} potriviri — precizează denumirea sau scanează codul.` : "Niciun articol găsit."; return; }
        }
        num[a.id] = num[a.id] || { denumire: a.denumire, um: a.um || "buc", faptic: 0 };
        num[a.id].faptic = Math.round((num[a.id].faptic + cant) * 1000) / 1000;
        deseneaza();
      };
      z.querySelector("#im-add").addEventListener("click", adauga);
      scan.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); adauga(); } });
      z.querySelectorAll(".im-scoate").forEach((b) => b.addEventListener("click", () => { delete num[b.dataset.id]; deseneaza(); }));
      z.querySelector("#im-fin").addEventListener("click", async () => {
        const linii = Object.entries(num).map(([id, x]) => ({ articol_id: parseInt(id), faptic: x.faptic }));
        if (!linii.length) { arataMesaj(zonaM, "Nimic de inventariat.", "eroare"); return; }
        try {
          const r = await api.post(`/tenants/${t.id}/stocuri/inventar`, { data: val("#cv-data") || new Date().toISOString().slice(0, 10), linii });
          arataMesaj(zonaM, `Inventar finalizat · ${(r.rezultate || []).length} articole procesate (note ciorne pentru diferențe).`, "ok");
          sectiuneaCV(corp, t, zonaM);
        } catch (e) { arataMesaj(zonaM, e.mesaj || "Eroare la finalizare.", "eroare"); }
      });
    };
    deseneaza();
  });
  // [F140] Analitica de stoc: critic / inert / ABC / consum perioade comparabile
  zona.querySelector("#cv-ana").addEventListener("click", async () => {
    try {
      const r = await api.get(`/tenants/${t.id}/stocuri/analitica`);
      const lista = (titlu, randuri, gol) => `
        <div class="pf-frand-nume" style="margin:8px 0 4px">${titlu}</div>
        ${!randuri.length ? `<div class="stare-goala">${gol}</div>`
          : `<div class="pf-lista">${randuri.join("")}</div>`}`;
      const critic = (r.critic || []).map((x) => `
        <div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(x.denumire)}</div>
          <div class="pf-frand-sub">stoc ${x.stoc} ${esc(x.um)} · nivel minim ${x.nivel_minim} · necesar ${x.necesar} ${esc(x.um)}</div>
        </div></div>`);
      const inert = (r.inert || []).map((x) => `
        <div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(x.denumire)}</div>
          <div class="pf-frand-sub">stoc ${x.stoc} ${esc(x.um)} · ultima mișcare ${esc(x.ultima_miscare)} · ${x.zile} zile</div>
        </div></div>`);
      const abc = (r.abc || []).map((x) => `
        <div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(x.denumire)} · clasa ${esc(x.clasa)}</div>
          <div class="pf-frand-sub">valoare stoc ${bani(x.valoare)} lei · cumulat ${x.pondere_cumulata}%</div>
        </div></div>`);
      const consum = (r.consum || []).map((x) => `
        <div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(x.denumire)}</div>
          <div class="pf-frand-sub">ieșiri ultimele 30 zile ${x.iesiri_30z} ${esc(x.um)} · 30 zile anterioare ${x.iesiri_30z_anterior} ${esc(x.um)}</div>
        </div></div>`);
      locZona.innerHTML = `
        <div class="pf-card">
          ${lista(`Stoc critic (sub nivel minim)`, critic, "Niciun articol sub nivel minim (sau niciun nivel minim setat).")}
          ${lista(`Fără mișcare de peste ${r.zile_inert} zile`, inert, "Niciun articol inert.")}
          ${lista(`Clasificare ABC (Pareto pe valoarea stocului)`, abc, "Niciun stoc de clasificat.")}
          ${lista(`Consum — perioade comparabile`, consum, "Nicio ieșire în ultimele 60 de zile.")}
        </div>`;
    } catch (e) { arataMesaj(locZona, e.mesaj || "eroare", "eroare"); }
  });
  zona.querySelector("#cv-fisa").addEventListener("click", async () => {
    if (!val("#cv-art")) return;
    try {
      const r = await api.get(`/tenants/${t.id}/stocuri/articole/${val("#cv-art")}/fisa`);
      zona.querySelector("#cv-fisa-zona").innerHTML = `
        <div class="pf-frand-nume" style="margin:8px 0">Fisa: ${esc(r.articol.denumire)}</div>
        <div class="pf-lista">${r.linii.map((l) => `
          <div class="pf-frand"><div class="pf-frand-text">
            <div class="pf-frand-nume">${esc(l.data)} \u00b7 ${l.tip === "intrare" ? "+" : "\u2212"}${l.cantitate} \u00b7 ${bani(l.valoare)} lei${l.pret_unitar ? " \u00b7 pret " + l.pret_unitar : ""}</div>
            <div class="pf-frand-sub">sold ${l.sold_cantitate} \u00b7 ${bani(l.sold_valoare)} lei${l.cmp ? " \u00b7 CMP " + l.cmp : ""}${l.document ? " \u00b7 " + esc(l.document) : ""}</div>
          </div></div>`).join("") || '<div class="stare-goala">Fără mișcări în fișă.</div>'}</div>`;
    } catch { arataMesaj(zona.querySelector("#cv-fisa-zona"), "Nu am putut încărca fisa.", "eroare"); }
  });
}

// [stocuri] NIR + descarcare gestiune (global-valorica)

async function ecranBilant(corp, nav, t) {
  {
    corp.innerHTML = `
      <h2 class="pf-titlu">Bilan\u021b anual ${semnAjutor("F013")}</h2>
      <p class="pf-intro">Genereaz\u0103 \u0219i valideaz\u0103 situa\u021biile financiare (validator ANAF pe server).</p>
      <div style="display:flex;gap:8px;align-items:flex-end;flex-wrap:wrap">
        <label class="camp"><span class="camp-eticheta">An</span><input type="number" id="bl-an" class="camp-input" value="${new Date().getFullYear() - 1}" style="width:90px"></label>
        <label class="camp"><span class="camp-eticheta">Tip</span><select id="bl-tip" class="camp-input">
          <option value="s1005">S1005 \u00b7 microentit\u0103\u021bi</option>
          <option value="s1003">S1003 \u00b7 entit\u0103\u021bi mici</option>
        </select></label>
        <button class="buton-primar" id="bl-val">Valideaz\u0103 (ANAF)</button>
        <button class="buton-secundar" id="bl-xml">Descarc\u0103 XML</button>
      </div>
      <div id="bl-rez" style="margin-top:10px"></div>`;
    const rez = corp.querySelector("#bl-rez");
    const par = () => `an=${corp.querySelector("#bl-an").value}`;
    const tip = () => corp.querySelector("#bl-tip").value;
    corp.querySelector("#bl-val").addEventListener("click", async () => {
      arataMesaj(rez, "Se validează…", "info");
      try {
        const r = await api.post(`/tenants/${t.id}/${tip()}-valideaza?${par()}`, {});
        const sem = r.ok
          ? `<span style="color:var(--verde);font-weight:600">\u25cf Validare f\u0103r\u0103 erori</span>`
          : `<span style="color:var(--rosu);font-weight:600">\u25cf Erori la validare</span>`;
        rez.innerHTML = `<p>${sem}</p>` +
          (r.erori ? `<pre class="tip-micut" style="white-space:pre-wrap;background:var(--fundal);padding:8px;border-radius:var(--raza)">${esc(r.erori)}</pre>` : "") +
          (r.avertismente && r.avertismente.length
            ? `<p class="pf-intro">${r.avertismente.map(esc).join("<br>")}</p>` : "");
      } catch (e) { arataMesaj(rez, e.mesaj || "eroare", "eroare"); }
    });
    corp.querySelector("#bl-xml").addEventListener("click", async () => {
      try {
        const r = await api.get(`/tenants/${t.id}/${tip()}-xml?${par()}`);
        const b = new Blob([r.xml], { type: "application/xml" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(b);
        a.download = `${tip()}_${t.id}_${corp.querySelector("#bl-an").value}.xml`;
        a.click();
        if (r.avertismente && r.avertismente.length) {
          rez.innerHTML = `<p class="pf-intro">${r.avertismente.map(esc).join("<br>")}</p>`;
        }
      } catch (e) { arataMesaj(rez, e.mesaj || "eroare", "eroare"); }
    });
  }
}

export async function ecranStocuri(corp, nav, t) {
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  let liniiNir = [];

  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    let nirs = [];
    try { const r = await api.get(`/tenants/${t.id}/stocuri/nir?an=${an}&luna=${luna}`); nirs = r.nir || []; } catch { corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca NIR-urile.</p>`; return; }
    const randuri = !nirs.length
      ? `<div class="stare-goala">Niciun NIR \u00een luna asta.</div>`
      : nirs.map((n) => `
        <div class="pf-frand">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">NIR ${esc(n.numar)} \u00b7 ${dataRo(n.data)} \u00b7 ${esc(n.furnizor || "")}</div>
            <div class="pf-frand-sub">cost ${n.cost_total} \u00b7 adaos ${n.adaos_total} \u00b7 TVA neex. ${n.tva_neexigibila} \u00b7 raft ${bani(n.valoare_vanzare)} lei</div>
          </div>
        </div>`).join("");
    const linieNouaNir = () => ({ denumire: "", cantitate: "", pret_achizitie: "", pret_vanzare: "", cota_tva: "" });   // [R29] fără cotă implicită: serverul refuză lipsa (main.py:798), iar ecranul nu răspunde în locul contabilului
    const _vn = (x) => (x === "" || x == null) ? "" : esc(String(x));
    // randeaza O linie NIR DIN MODEL, id-uri pozitionale nir-l{i}-* (cap.24: id derivat din pozitie -> backendul
    // leaga eroarea de camp, cap.6); buton de stergere pe fiecare rand (regula 3).
    function randLinieNir(i) {
      const l = liniiNir[i];
      return `<div class="nir-linie" data-idx="${i}" style="display:flex;gap:8px;margin-bottom:6px;flex-wrap:wrap">
        <input type="text" class="camp-input" id="nir-l${i}-denumire" placeholder="denumire" aria-label="Denumire" value="${_vn(l.denumire)}" style="flex:2;min-width:160px">
        <input type="number" step="0.001" class="camp-input" id="nir-l${i}-cantitate" placeholder="cant." aria-label="Cantitate" value="${_vn(l.cantitate)}" style="width:90px">
        <input type="number" step="0.0001" class="camp-input" id="nir-l${i}-pret_achizitie" placeholder="preț achiziție" aria-label="Preț achiziție" value="${_vn(l.pret_achizitie)}" style="width:120px">
        <input type="number" step="0.0001" class="camp-input" id="nir-l${i}-pret_vanzare" placeholder="preț raft (cu TVA)" aria-label="Preț raft cu TVA" value="${_vn(l.pret_vanzare)}" style="width:140px">
        <select class="camp-input" id="nir-l${i}-cota_tva" aria-label="Cota TVA" style="width:90px"><option value=""${!l.cota_tva ? " selected" : ""}>alege</option>${[21, 11].map((c) => `<option value="${c}"${String(l.cota_tva) === String(c) ? " selected" : ""}>${c}%</option>`).join("")}</select>
        <button type="button" class="buton-sters nir-l-sterge" data-idx="${i}" title="Șterge">×</button>
      </div>`;
    }
    corp.innerHTML = 
    corp.innerHTML = `
      <h2 class="pf-titlu">Stocuri ${semnAjutor("F089")}</h2>
      <p class="pf-intro">Luna ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")}
        <button class="buton-secundar" id="s-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="buton-secundar" id="s-next">luna \u2192</button>
        <button class="buton-primar" id="s-desc" style="margin-left:12px">Descarc\u0103 gestiunea lunii</button></p>
      <div id="s-mesaj"></div>
      <p><button class="buton-secundar" id="sn-toggle">+ NIR nou</button></p>
      <div id="sn-zona" hidden style="display:block;margin-bottom:14px">
        <div class="pf-frand-nume" style="margin-bottom:8px">NIR nou</div>
        <div class="camp-eticheta">NIR: num\u0103r \u00b7 dat\u0103 \u00b7 furnizor \u00b7 CUI</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
          <input type="text" id="sn-numar" class="camp-input" placeholder="număr NIR" aria-label="Num\u0103r NIR" style="width:120px">
          <input type="date" id="sn-data" aria-label="Data intrare stoc" class="camp-input" value="${new Date().toISOString().slice(0, 10)}">
          <input type="text" id="sn-furn" class="camp-input" placeholder="furnizor" aria-label="Furnizor" style="flex:1;min-width:160px">
          <input type="text" id="sn-cui" class="camp-input" placeholder="CUI" aria-label="CUI furnizor" style="width:120px">
        </div>
        <div class="camp-eticheta">Articole: denumire \u00b7 cantitate \u00b7 pre\u021b achizi\u021bie \u00b7 pre\u021b raft (cu TVA) \u00b7 cot\u0103 TVA</div>
        <div id="sn-linii">${liniiNir.map((_, i) => randLinieNir(i)).join("")}</div>
        <div class="camp-eticheta">Cost accesoriu (landed cost) — se repartizează proporțional în costul de achiziție (OMFP 1802/2014). Contul de credit se confirmă de contabil.</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
          <input type="number" step="0.01" id="sn-transport" class="camp-input" placeholder="transport" aria-label="Transport" style="width:110px">
          <input type="text" id="sn-cont-transport" class="camp-input" value="401" aria-label="Cont credit transport" style="width:120px">
          <input type="number" step="0.01" id="sn-taxe" class="camp-input" placeholder="taxe" aria-label="Taxe" style="width:110px">
          <input type="text" id="sn-cont-taxe" class="camp-input" value="446" aria-label="Cont credit taxe" style="width:120px">
        </div>
        <p><button class="buton-secundar" id="sn-plus">+ articol</button>
           <button class="buton-primar" id="sn-salveaza" style="margin-left:6px">Salveaz\u0103 NIR (note ciorne)</button></p>
      </div>
      <div id="cv-zona"></div>
      <div class="pf-lista">${randuri}</div>`;
    const zonaM = corp.querySelector("#s-mesaj");
    const zonaL = corp.querySelector("#sn-linii");
    const _tg = (btnId, zonaId) => {  /* cap2_toggle_v1 */
      const b = corp.querySelector(btnId), z = corp.querySelector(zonaId);
      if (!b || !z) return;
      b.addEventListener("click", () => {
        z.hidden = !z.hidden;
        b.classList.toggle("buton-activ", !z.hidden);
      });
    };
    _tg("#sn-toggle", "#sn-zona");
    // model NIR: input-urile scriu in liniiNir (fara re-randare la tastare); add/delete re-randeaza integral
    // #sn-linii din model (cap.24 regula 1); fara filtrare la trimitere (regula 2); erori per-linie de la backend
    // langa camp (cap.6 mecanism A). Fetch-ul cotei nu exista aici (cota = select).
    function legaLinieNir(i) {
      const l = liniiNir[i];
      const g = (suf) => zonaL.querySelector("#nir-l" + i + "-" + suf);
      const den = g("denumire"), cant = g("cantitate"), pa = g("pret_achizitie"), pv = g("pret_vanzare"), tva = g("cota_tva");
      const del = zonaL.querySelector('.nir-l-sterge[data-idx="' + i + '"]');
      den.addEventListener("input", () => { l.denumire = den.value.trim(); });
      cant.addEventListener("input", () => { l.cantitate = cant.value; });
      pa.addEventListener("input", () => { l.pret_achizitie = pa.value; });
      pv.addEventListener("input", () => { l.pret_vanzare = pv.value; });
      tva.addEventListener("change", () => { l.cota_tva = parseFloat(tva.value); });
      del.addEventListener("click", () => { const p = liniiNir.indexOf(l); if (p >= 0) liniiNir.splice(p, 1); deseneazaLiniiNir(); });
    }
    function deseneazaLiniiNir() {
      zonaL.innerHTML = liniiNir.map((_, i) => randLinieNir(i)).join("");
      liniiNir.forEach((_, i) => legaLinieNir(i));
    }
    liniiNir.forEach((_, i) => legaLinieNir(i));   // leaga randurile deja randate in corp.innerHTML
    corp.querySelector("#s-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#s-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    corp.querySelector("#sn-plus").addEventListener("click", () => { liniiNir.push(linieNouaNir()); deseneazaLiniiNir(); });
    corp.querySelector("#sn-salveaza").addEventListener("click", async () => {
      const znir = corp.querySelector("#sn-zona");
      curataEroriCamp(znir);
      // NU se filtreaza randuri (cap.24 regula 2): lista trimisa = lista randata. Un articol incomplet se
      // valideaza pe backend si se raporteaza langa campul lui, nu dispare tacit.
      const linii = liniiNir.map((l) => ({
        denumire: l.denumire, cantitate: parseFloat(l.cantitate) || 0,
        pret_achizitie: parseFloat(l.pret_achizitie) || 0, pret_vanzare: parseFloat(l.pret_vanzare) || 0,
        cota_tva: (l.cota_tva === "" || l.cota_tva == null) ? null : Number(l.cota_tva),   // [R29]
      }));
      try {
        const r = await api.post(`/tenants/${t.id}/stocuri/nir`, {
          numar: corp.querySelector("#sn-numar").value.trim(),
          data: corp.querySelector("#sn-data").value,
          furnizor: corp.querySelector("#sn-furn").value || null,
          cui: corp.querySelector("#sn-cui").value || null,
          transport: parseFloat(corp.querySelector("#sn-transport").value) || 0,
          taxe: parseFloat(corp.querySelector("#sn-taxe").value) || 0,
          cont_transport: corp.querySelector("#sn-cont-transport").value.trim() || null,
          cont_taxe: corp.querySelector("#sn-cont-taxe").value.trim() || null,
          linii,
        });
        liniiNir = [];
        const acc = (parseFloat(r.transport) || 0) + (parseFloat(r.taxe) || 0);
        zonaM.innerHTML = `<p class="pf-intro">NIR salvat · ${r.inregistrari.length} note ciorne (cost ${r.cost_total}${acc > 0 ? " din care accesoriu " + bani(acc) : ""}, adaos ${r.adaos_total}, TVA neex. ${r.tva_neexigibila}).</p>`;
        deseneaza();
      } catch (e) {
        curataEroriCamp(corp.querySelector("#sn-zona"));
        const eris = (e && e.erori_campuri) || [];
        const rest = [];
        eris.forEach((x) => { if (!eroareCamp(corp.querySelector("#sn-zona"), x.camp, x.mesaj)) rest.push(x.mesaj); });
        arataMesaj(zonaM, (rest.length ? rest.join("; ") : (e.mesaj || "eroare")), "eroare");
      }
    });

    corp.querySelector("#s-desc").addEventListener("click", () => {
      const bD = corp.querySelector("#s-desc");
      confirmaCaseta(bD.parentElement || bD, `Descarci gestiunea pe ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")}? Se calculează din notele VALIDATE.`, async () => {  // audit_cab_lot2_v1
      try {
        const r = await api.post(`/tenants/${t.id}/stocuri/descarcare?an=${an}&luna=${luna}`, {});
        if (r.mesaj) arataMesaj(zonaM, r.mesaj, "info");  // mesaj de stare = arataMesaj (cap.6), nu clasa ad-hoc mig-gol
        else zonaM.innerHTML = `<p class="pf-intro">K=${r.k} \u00b7 CMV ${r.cmv} \u00b7 adaos ${r.adaos} \u00b7 TVA ${r.tva} \u00b7 total 371: ${bani(r.total_371)} lei \u00b7 ${r.inregistrari.length} note ciorne.</p>`;
      } catch (e) { arataMesaj(zonaM, e.mesaj || "eroare", "eroare"); }
      }, { textOk: "Descarcă gestiunea" });
    });
    sectiuneaCV(corp, t, zonaM);
  };
  liniiNir = [{}];
  deseneaza();
}

// [casa] Registru de casa
async function ecranCasa(corp, nav, t) {
  const CATEGORII = [
    ["incasare_client", "Încasare client (5311=4111)"],
    ["plata_furnizor", "Plată furnizor (401=5311)"],
    ["ridicare_banca", "Ridicare de la bancă (5311=581)"],
    ["depunere_banca", "Depunere la bancă (581=5311)"],
    ["avans_decontare", "Avans spre decontare (542=5311)"],
  ];
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    let reg = { operatiuni: [], sold_final: "0", avertismente: [] };
    try { reg = await api.get(`/tenants/${t.id}/casa/registru?an=${an}&luna=${luna}`); } catch { corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca registrul de casă.</p>`; return; }
    const ziAzi = new Date().toISOString().slice(0, 10);
    const _avertLinii = (reg.avertismente || []).map((a) =>
      `<div class="ca-mesaj">${esc(a.mesaj || a.cod || "")}${a.temei ? " \u00b7 " + esc(a.temei) : ""}</div>`).join("");
    // avertismentele registrului = atentionari -> o caseta canonica .caseta-atentie (cap.5), nu clasa ad-hoc mig-gol
    const avert = _avertLinii ? `<div class="caseta-atentie" style="margin-bottom:6px">${_avertLinii}</div>` : "";
    const randuri = !(reg.operatiuni || []).length
      ? `<div class="stare-goala">Nicio opera\u021biune \u00een luna asta.</div>`
      : reg.operatiuni.map((o) => `
        <div class="pf-frand">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">${esc(o.data)} \u00b7 ${o.tip === "plata" ? "\u2212" : "+"}${bani(o.suma)} lei \u00b7 sold ${bani(o.sold)} lei</div>
            <div class="pf-frand-sub">${esc(o.partener || "")}${o.document ? " \u00b7 doc " + esc(o.document) : ""} \u00b7 ${esc(o.categorie)}</div>
          </div>
          <button class="buton-secundar" data-del="${o.id}">\u0218terge</button>
        </div>`).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">Cas\u0103 ${semnAjutor("F015")}</h2>
      <p class="pf-intro">Luna ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")} \u00b7 sold final <b>${bani(reg.sold_final)} lei</b>
        <button class="buton-secundar" id="c-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="buton-secundar" id="c-next">luna \u2192</button></p>
      ${avert}
      <p><button class="buton-secundar" id="c-toggle">+ Dispozi\u021bie nou\u0103</button></p>
      <div id="c-zona" hidden style="display:block;margin-bottom:14px">
        <div class="pf-frand-nume" style="margin-bottom:8px">Dispoziție nouă</div>
        <div class="form-rand" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px">
          <label class="camp"><span class="camp-eticheta">Data</span><input type="date" id="c-data" class="camp-input"></label>
          <label class="camp"><span class="camp-eticheta">Tip</span><select id="c-cat" class="camp-input">${CATEGORII.map(([v, l]) => `<option value="${v}">${l}</option>`).join("")}</select></label>
          <label class="camp"><span class="camp-eticheta">Suma</span><input type="number" step="0.01" id="c-suma" class="camp-input" placeholder="0,00"></label>
          <label class="camp"><span class="camp-eticheta">Partener</span><input type="text" id="c-part" class="camp-input"></label>
          <label class="camp">
            <span class="camp-eticheta" style="display:flex;justify-content:space-between;align-items:center">
              CUI
              <button type="button" class="btn-link" id="c-cui-verif" style="font-weight:600">Verific\u0103</button>
            </span>
            <input type="text" id="c-cui" class="camp-input">
          </label>
          <label class="camp"><span class="camp-eticheta">Document</span><input type="text" id="c-doc" class="camp-input"></label>
        </div>
        <div class="em-cui-stare" id="c-cui-stare"></div>
        <p style="margin-top:10px"><button class="buton-primar" id="c-adauga" disabled title="Completeaz\u0103 data \u0219i suma \u00eent\u00e2i">Adaugă (notă ciornă)</button></p>
        <div id="c-mesaj"></div>
      </div>
      <div class="pf-lista">${randuri}</div>`;

    const _tg = (btnId, zonaId) => {  /* cap2_toggle_v1 */
      const b = corp.querySelector(btnId), z = corp.querySelector(zonaId);
      if (!b || !z) return;
      b.addEventListener("click", () => {
        z.hidden = !z.hidden;
        b.classList.toggle("buton-activ", !z.hidden);
      });
    };
    _tg("#c-toggle", "#c-zona");
    corp.querySelector("#c-cui-verif").addEventListener("click", async () => {  /* verificare_anaf_casa_v1 */
      const cui = corp.querySelector("#c-cui").value.trim();
      const stare = corp.querySelector("#c-cui-stare");
      if (!cui) return;
      stare.textContent = "se verific\u0103 la ANAF\u2026";
      stare.className = "em-cui-stare";
      try {
        const r = await api.get(`/tenants/${t.id}/verifica-cui/${encodeURIComponent(cui)}`);
        if (r && r.gasit) {
          corp.querySelector("#c-part").value = r.denumire || "";
          stare.innerHTML = `<span class="em-cui-info">${r.platitor_tva ? "pl\u0103titor TVA" : "nepl\u0103titor TVA"}${r.inactiv ? " \u00b7 <b style=\"color:var(--rosu)\">INACTIV\u0102 fiscal</b>" : ""}</span>`;
          stare.className = "em-cui-stare";
        } else {
          stare.textContent = "CUI neg\u0103sit la ANAF";
          stare.className = "em-cui-stare em-cui-rau";
        }
      } catch {
        stare.textContent = "verificarea a e\u0219uat";
        stare.className = "em-cui-stare em-cui-rau";
      }
    });
    corp.querySelector("#c-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#c-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    { const _cA = corp.querySelector("#c-adauga"), _cD = corp.querySelector("#c-data"), _cS = corp.querySelector("#c-suma");
      const _cChk = () => { if (_cA) _cA.disabled = !(_cD && _cD.value && _cS && parseFloat(_cS.value) > 0); };
      [_cD, _cS].forEach((el) => el && el.addEventListener("input", _cChk)); _cChk(); }
    corp.querySelector("#c-adauga").addEventListener("click", async () => {
      const zonaM = corp.querySelector("#c-mesaj");
      try {
        const r = await api.post(`/tenants/${t.id}/casa/operatiuni`, {
          data: corp.querySelector("#c-data").value,
          categorie: corp.querySelector("#c-cat").value,
          suma: parseFloat(corp.querySelector("#c-suma").value) || 0,
          partener: corp.querySelector("#c-part").value || null,
          cui: corp.querySelector("#c-cui").value || null,
          document: corp.querySelector("#c-doc").value || null,
        });
        const av = (r.avertismente || []).length;
        zonaM.innerHTML = `<p class="pf-intro">Nota ${esc(r.nota)} creata ca ciorna.${av ? ` <b style="color:var(--galben)">${av} avertisment(e) plafon.</b>` : ""}</p>`;
        deseneaza();
      } catch (e) { arataMesaj(zonaM, e.mesaj || "eroare", "eroare"); }
    });
    corp.querySelectorAll("[data-del]").forEach((b) => b.addEventListener("click", () => {
      confirmaCaseta(b.parentElement || b, "Ștergi operațiunea și ciorna legată?", async () => {  // audit_cab_lot2_v1
      try { await api.del(`/tenants/${t.id}/casa/operatiuni/${b.dataset.del}`); deseneaza(); }
      catch (e) {
        b.parentElement.querySelectorAll(".msg-eroare").forEach((x) => x.remove());
        b.insertAdjacentHTML("afterend", '<span class="msg-eroare" style="margin-left:8px">' + (e.mesaj || "Eroare la ștergere.") + '</span>');
      }
      }, { textOk: "Șterge" });
    }));
  };
  deseneaza();
}

// [banca] Import extras + reconciliere pe facturi
async function ecranBanca(corp, nav, t) {
  const CUL = { verde: "var(--verde)", galben: "var(--galben)", rosu: "var(--rosu)", gri: "var(--gri-semafor)" };
  corp.innerHTML = `
    <h2 class="pf-titlu">Banc\u0103 ${semnAjutor("F011")}</h2>
    <p class="pf-intro">Încarcă extrasul (.xls, .xlsx, .csv) \u2014 liniile se potrivesc automat pe facturi dupa CUI.</p>
    <input type="file" id="bk-fisier" aria-label="Fisier extras bancar" accept=".xls,.xlsx,.csv" style="margin-bottom:16px">
    <div id="bk-mesaj"></div>
    <div id="bk-lista"></div>`;
  const zonaMesaj = corp.querySelector("#bk-mesaj");
  const zonaLista = corp.querySelector("#bk-lista");

  function badge(l) {
    if (l.status === "ignorat") return `<span style="color:var(--gri)">Ignorată</span> <button class="btn-link bk-undo" data-id="${l.id}">readu</button>`;
    if (l.status === "contat") return `<span style="color:${CUL.gri};font-weight:600">Contat \u2713</span>`;
    const m = (l.alocari || {}).status_match;
    if (m === "verde") return `<span style="color:${CUL.verde};font-weight:600">\u25cf Match exact</span>`;
    if (m === "galben") return `<span style="color:${CUL.galben};font-weight:600">\u25cf Par\u021bial</span>`;
    return `<span style="color:${CUL.rosu};font-weight:600">\u25cf F\u0103r\u0103 match</span>`;
  }

  function badgeIncredere(l) {  // ai_incredere_fe_v1
    const inc = (l.alocari || {}).incredere;
    if (!inc) return "";
    if (inc === "sigur") return ` <span class="tip-micut" style="color:${CUL.verde}">\u25cf sigur</span>`;
    if (inc === "de_verificat") return ` <span class="tip-micut" style="color:${CUL.rosu}">\u25cf de verificat</span>`;
    return ` <span class="tip-micut" style="color:${CUL.galben}">\u25cf probabil</span>`;
  }
  function randAlocari(l) {
    const al = ((l.alocari || {}).alocari || []);
    if (!al.length) return "";
    return `<div class="pf-frand-sub">${al.map((a) => {
      const f = a.factura || {};
      return `${esc(f.serie || "")}${esc(f.numar || "#" + a.factura_id)} \u00b7 ${esc(f.tert || "")} \u00b7 ${bani(a.suma)} lei`;
    }).join("<br>")}</div>`;
  }

  function randeaza(linii) {
    if (!linii.length) { zonaLista.innerHTML = `<div class="stare-goala">Nicio linie de extras. Încarcă un fișier.</div>`; return; }
    zonaLista.innerHTML = `<div class="pf-lista">${linii.map((l) => `
      <div class="pf-frand">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(l.data)} \u00b7 ${l.tip === "plata" ? "\u2212" : "+"}${bani(l.suma)} lei${l.cui_detectat ? " \u00b7 CUI " + esc(l.cui_detectat) : ""} \u00b7 ${badge(l)}</div>
          <div class="pf-frand-sub">${esc((l.descriere || "").slice(0, 90))}${(l.alocari || {}).motiv ? " \u00b7 " + esc(l.alocari.motiv) : ""}</div>
          ${randAlocari(l)}
        </div>
        <div>
          ${l.status === "potrivit" ? `<button class="buton-primar" data-cont="${l.id}">Conteaz\u0103</button>` : ""}${l.status === "nou" && l.nota_propusa && l.nota_propusa.debit ? `<button class="buton-primar" data-cont="${l.id}">Conteaz\u0103 ${l.nota_propusa.debit}=${l.nota_propusa.credit}</button>${badgeIncredere(l)}` : ""}
          ${l.status !== "contat" && l.status !== "ignorat" ? `<button class="buton-primar" data-alege="${l.id}" style="margin-left:6px">Alege facturile</button>` : ""}${l.status !== "contat" && l.status !== "ignorat" ? `<button class="buton-secundar" data-ign="${l.id}" style="margin-left:6px">Ignor\u0103</button>` : ""}
        </div>
      </div>`).join("")}</div>`;
    zonaLista.querySelectorAll("[data-cont]").forEach((b) =>
      b.addEventListener("click", () => conteaza(parseInt(b.dataset.cont), null)));
    zonaLista.querySelectorAll("[data-ign]").forEach((b) =>
      b.addEventListener("click", async () => {
        try { await api.post(`/tenants/${t.id}/banca/reconciliere/${b.dataset.ign}/ignora`, {}); incarca(); }
        catch (e) { arataMesaj(zonaMesaj, e.mesaj || "Eroare.", "eroare"); }
      }));
    zonaLista.querySelectorAll(".bk-undo").forEach((b) =>
      b.addEventListener("click", async () => {
        try { await api.post(`/tenants/${t.id}/banca/reconciliere/${b.dataset.id}/reactiveaza`, {}); incarca(); }
        catch (e) { arataMesaj(zonaMesaj, e.mesaj || "Eroare.", "eroare"); }
      }));
    zonaLista.querySelectorAll("[data-alege]").forEach((b) =>
      b.addEventListener("click", () => picker(linii.find((x) => x.id === parseInt(b.dataset.alege)))));
  }

  async function incarca() {
    try {
      const r = await api.get(`/tenants/${t.id}/banca/reconciliere`);
      randeaza(r.linii || []);
    } catch { arataMesaj(zonaLista, "Nu am putut încărca liniile.", "eroare"); }
  }

  async function conteaza(id, alocari) {
    zonaMesaj.innerHTML = "";
    try {
      const r = await api.post(`/tenants/${t.id}/banca/reconciliere/${id}/conteaza`, alocari ? { alocari } : {});
      arataMesaj(zonaMesaj, `Nota ${r.nota || ""} \u2014 ${(r.inregistrari || []).length} \u00eenregistr\u0103ri create.`, "ok");
      incarca();
    } catch (e) { arataMesaj(zonaMesaj, e.mesaj || "Eroare la contare", "eroare"); }
  }

  async function picker(l) {
    if (!l) return;
    zonaMesaj.innerHTML = `<p class="ecran-nota">Se încarcă facturile deschise...</p>`;
    let facturi = [];
    try {
      const r = await api.get(`/tenants/${t.id}/banca/reconciliere/facturi-deschise`);
      facturi = (r.facturi || []).filter((f) => f.directie === (l.tip === "incasare" ? "emisa" : "primita"));
    } catch { arataMesaj(zonaMesaj, "Nu am putut încărca facturile.", "eroare"); return; }
    if (!facturi.length) { zonaMesaj.innerHTML = `<div class="stare-goala">Nicio factura deschisa pe aceasta directie.</div>`; return; }
    zonaMesaj.innerHTML = `
      <div style="display:block">
        <div class="pf-frand-nume">Alege facturile pentru linia din ${esc(l.data)} \u00b7 ${bani(l.suma)} lei</div>
        <div class="pf-lista" style="margin-top:8px">${facturi.map((f) => `
          <label class="pf-frand" style="cursor:pointer">
            <input type="checkbox" data-fid="${f.id}" data-sold="${f.sold}" style="margin-right:10px">
            <div class="pf-frand-text">
              <div class="pf-frand-nume">${esc(f.serie || "")}${esc(f.numar)} \u00b7 ${esc(f.tert_nume || "")}</div>
              <div class="pf-frand-sub">${dataRo(f.data_emitere)} \u00b7 sold ${bani(f.sold)} lei \u00b7 CUI ${esc(f.tert_cui || "")}</div>
            </div>
          </label>`).join("")}</div>
        <p style="margin-top:10px">
          <button class="buton-primar" id="bk-pk-ok">Conteaz\u0103 selectate</button>
          <button class="buton-primar" id="bk-pk-nu" style="margin-left:6px">Renun\u021b\u0103</button>
        </p>
      </div>`;
    zonaMesaj.scrollIntoView({behavior:"smooth",block:"start"});
    zonaMesaj.querySelector("#bk-pk-nu").addEventListener("click", () => { zonaMesaj.innerHTML = ""; });
    zonaMesaj.querySelector("#bk-pk-ok").addEventListener("click", () => {
      let rest = parseFloat(l.suma);
      const aloc = [];
      zonaMesaj.querySelectorAll("input[data-fid]:checked").forEach((c) => {
        if (rest <= 0.005) return;
        const parte = Math.min(parseFloat(c.dataset.sold), rest);
        aloc.push({ factura_id: parseInt(c.dataset.fid), suma: parte.toFixed(2) });
        rest -= parte;
      });
      if (!aloc.length) { arataMesaj(zonaMesaj, "Nicio factura selectata.", "avert"); return; }
      conteaza(l.id, aloc);
    });
  }

  corp.querySelector("#bk-fisier").addEventListener("change", async (ev) => {
    const f = ev.target.files[0];
    if (!f) return;
    zonaMesaj.innerHTML = `<p class="ecran-nota">Se cite\u0219te \u0219i se potrive\u0219te extrasul...</p>`;
    const fd = new FormData();
    fd.append("fisier", f);
    try {
      const resp = await fetch(`/tenants/${t.id}/banca/reconciliere/import`, {
        method: "POST",
        headers: { "Authorization": "Bearer " + sesiune.token() },
        body: fd,
      });
      if (!resp.ok) throw new Error("eroare " + resp.status);
      const r = await resp.json();
      zonaMesaj.innerHTML = `<p class="pf-intro"><b>${(r.linii || []).length}</b> linii importate și potrivite.</p>`;
      incarca();
    } catch { arataMesaj(zonaMesaj, "Nu am putut citi extrasul.", "eroare"); }
    ev.target.value = "";
  });

  incarca();
}

/* Confirmarea crearii unei firme. Acelasi mecanism ca bannerul de la confirmarea adresei
   (app.js): un act care schimba starea si nu spune nimic il face pe om sa-l repete. */


// [R72, 27.08.2026] Scoaterea unei firme din portofoliu.
// Instanța: două firme `PROBA PORTAL SRL` create din greșeală au rămas în portofoliu fiindcă nu
// exista nicio cale de a le scoate. Iar duplicatul a costat în aceeași zi — un ecran corect
// („Niciun cont de client încă") a fost citit ca fals, fiindcă se deschisese cealaltă firmă.
// De aceea confirmarea de aici e pe CUI, NU pe nume: numele se pot repeta, CUI-ul nu.
async function ecranScoateFirma(corp, nav, t) {
  corp.innerHTML = `<p class="ecran-nota" id="sf-stare">Se verifică ce a produs firma…</p>
                    <div id="sf-corp"></div><div id="sf-mesaj"></div>`;
  const zonaM = corp.querySelector("#sf-mesaj");
  let p;
  try { p = await api.get(`/tenants/${t.id}/scoatere`); }
  catch (e) {
    arataMesaj(corp.querySelector("#sf-stare"),
               e.mesaj || e.message || "Nu am putut verifica firma.", "eroare");
    return;
  }
  corp.querySelector("#sf-stare").remove();
  const zona = corp.querySelector("#sf-corp");
  const cap = `<h3 style="margin:0 0 4px">${esc(p.nume || "")}</h3>
               <p class="ecran-nota" style="margin:0 0 16px">CUI ${esc(String(p.cui || "—"))}</p>`;

  if (p.se_poate_sterge) {
    // [R50 (c)] Ce dispare, numărat înainte de apăsare. O ștergere care spune doar „se șterge
    // tot" nu se poate confrunta cu nimic după.
    const rd = p.randuri_de_sters || {};
    const chei = Object.keys(rd);
    const cl = p.clienti_de_dezactivat || [];
    const ceCuClientii = cl.length
      ? `<p class="ecran-nota" style="margin:10px 0 0"><strong>${cl.length} cont${cl.length === 1 ? "" : "uri"} de client</strong>
           ${cl.length === 1 ? "rămâne" : "rămân"} fără nicio firmă și ${cl.length === 1 ? "va fi dezactivat" : "vor fi dezactivate"}:
           ${cl.map((c) => esc(c.email)).join(" · ")}. Contul nu se șterge — persoana nu e a firmei —
           dar nu mai poate intra în portal.</p>`
      : "";
    const ceDispare = chei.length
      ? `<p class="ecran-nota" style="margin:10px 0 0">Dispar și: ${chei.map((k) =>
           `${rd[k]} × <code>${esc(k)}</code>`).join(" · ")}, plus schema de date a firmei.</p>`
      : `<p class="ecran-nota" style="margin:10px 0 0">Firma nu are niciun rând în tabelele
           comune. Dispare doar schema ei de date.</p>`;
    zona.innerHTML = `${cap}
      <div class="caseta-atentie">
        <div class="ca-mesaj"><strong>Act ireversibil.</strong> Firma nu a produs niciun document:
          nicio declarație depusă sau în coadă, nicio notă contabilă, factură, chitanță sau stat de
          plată. Se poate scoate cu totul. <strong>Ștergerea nu se poate întoarce</strong> — datele
          firmei și schema ei dispar, iar backupul off-site nu se poate șterge selectiv.</div>
      </div>
      ${ceDispare}
      ${ceCuClientii}
      ${(() => {
        const u = p.urme_de_pastrat || {};
        const n = Object.values(u).reduce((a, b) => a + b, 0);
        return n
          ? `<p class="ecran-nota" style="margin:10px 0 0">Se <strong>păstrează</strong> ${n} urme
               de portal (cine a primit acces, ce adresă s-a schimbat și când). Le găsești după
               ștergere sub „Firme scoase".</p>`
          : "";
      })()}
      <div class="camp" style="margin:14px 0">
        <label class="camp-eticheta" for="sf-cui">Scrie CUI-ul firmei ca să confirmi</label>
        <input class="camp-input" id="sf-cui" autocomplete="off" placeholder="${esc(String(p.cui || ""))}">
        <p class="camp-ajutor">Se cere CUI-ul, nu numele: două firme pot avea același nume.</p>
      </div>
      <button class="buton-primar" id="sf-sterge" disabled>Scoate firma definitiv</button>
      <p class="ecran-nota" style="margin:16px 0 6px"><strong>Sau, dacă vrei doar s-o scoți din
         listă:</strong> dezactivarea e <strong>reversibilă</strong> — firma iese din portofoliul
         de lucru, datele rămân neatinse, iar de sub „Firme dezactivate" o poți aduce înapoi
         oricând. Ștergerea de mai sus <strong>nu se poate întoarce</strong>.</p>
      <button class="buton-secundar" id="sf-dezactiveaza-2">Dezactivează firma (reversibil)</button>`;
    const bDez2 = zona.querySelector("#sf-dezactiveaza-2");
    bDez2.addEventListener("click", async () => {
      bDez2.disabled = true; bDez2.textContent = "Se dezactivează…";
      try {
        await api.post(`/tenants/${t.id}/activare`, { activ: false });
        nav.acasa();
        nav.setFirmaInLucru("");
      } catch (e) {
        bDez2.disabled = false; bDez2.textContent = "Dezactivează firma (reversibil)";
        arataMesaj(zonaM, e.mesaj || e.message || "Nu am putut dezactiva firma.", "eroare");
      }
    });
    const inp = zona.querySelector("#sf-cui"), btn = zona.querySelector("#sf-sterge");
    inp.addEventListener("input", () => {
      btn.disabled = inp.value.trim() !== String(p.cui || "").trim();
    });
    btn.addEventListener("click", async () => {
      btn.disabled = true; btn.textContent = "Se scoate…";
      try {
        await api.del(`/tenants/${t.id}?confirmare=${encodeURIComponent(inp.value.trim())}`);
        nav.acasa();
        nav.setFirmaInLucru("");
      } catch (e) {
        btn.disabled = false; btn.textContent = "Scoate firma definitiv";
        arataMesaj(zonaM, e.mesaj || e.message || "Nu am putut scoate firma.", "eroare");
      }
    });
    return;
  }

  // Are evidență: nu se șterge. Se SPUNE ce s-a găsit — un refuz fără motiv nu se poate verifica.
  const motive = (p.evidenta && p.evidenta.motive) || [];
  zona.innerHTML = `${cap}
    <div class="caseta-atentie">
      <div class="ca-mesaj">Firma <strong>nu se poate șterge</strong>: a produs documente care au
        ajuns la cineva din afară. Ce s-a găsit:
        <ul style="margin:8px 0 0 18px">${motive.map((m) => `<li>${esc(m)}</li>`).join("")}</ul>
      </div>
    </div>
    <p class="ecran-nota" style="margin:14px 0">O poți <strong>dezactiva</strong> — act
       <strong>reversibil</strong>: iese din portofoliul de lucru, documentele rămân neatinse, iar
       de sub „Firme dezactivate" o aduci înapoi oricând, în starea de dinainte.</p>
    <button class="buton-primar" id="sf-dezactiveaza">Dezactivează firma (reversibil)</button>`;
  zona.querySelector("#sf-dezactiveaza").addEventListener("click", async () => {
    const b = zona.querySelector("#sf-dezactiveaza");
    b.disabled = true; b.textContent = "Se dezactivează…";
    try {
      await api.post(`/tenants/${t.id}/activare`, { activ: false });
      nav.acasa();
      nav.setFirmaInLucru("");
    } catch (e) {
      b.disabled = false; b.textContent = "Dezactivează firma";
      arataMesaj(zonaM, e.mesaj || e.message || "Nu am putut dezactiva firma.", "eroare");
    }
  });
}




// [R72, 27.08.2026] Urma firmelor scoase — CITITĂ, nu doar scrisă.
// `public.firme_scoase` era, în ziua în care s-a construit, a doua instanță a clasei declarate
// dimineață la `urme-portal`: scrisă, necitită de om. Ecranul ăsta o închide.
function randeazaFirmeScoase(corp, scoase) {
  if (!scoase.length) {
    corp.innerHTML = `<p class="ecran-nota">Nicio firmă scoasă din portofoliu.</p>`;
    return;
  }
  const rand = (f) => {
    const rs = f.randuri_sterse || {};
    const chei = Object.keys(rs).filter((k) => k !== "tenants" && rs[k]);
    const up = (f.urme_pastrate || {}).urme_portal || [];
    const se = (f.urme_pastrate || {}).schimbari_email || [];
    return `
      <div class="firme-rand" style="display:block;cursor:default">
        <div class="firme-rand-nume">${esc(f.nume || "(fără nume)")}</div>
        <div class="firme-rand-cui">CUI ${esc(String(f.cui || "—"))} · schema <code>${esc(f.schema_name || "")}</code></div>
        <p class="ecran-nota" style="margin:6px 0 0">
          Scoasă la <strong>${esc(dataRo(f.scos_la, "cu_ora"))}</strong>
          de <strong>${esc(f.scos_de || "utilizator șters")}</strong>
          ${f.motiv === "gdpr_cabinet" ? "· prin ștergerea cabinetului (GDPR)" : ""}
        </p>
        <p class="ecran-nota" style="margin:6px 0 0">S-au curățat: ${
          chei.length ? chei.map((k) => `${rs[k]} × <code>${esc(k)}</code>`).join(" · ") : "niciun rând în tabelele comune"
        }, plus schema de date.</p>
        ${up.length || se.length ? `
          <details style="margin-top:8px">
            <summary style="cursor:pointer">Urme păstrate din portal (${up.length + se.length})</summary>
            <ul style="margin:8px 0 0 18px">
              ${up.map((u) => `<li><strong>${esc(u.actiune)}</strong> — ${esc(u.detaliu)}
                    <span class="ecran-nota">(${esc(dataRo(u.creat_la, "cu_ora"))})</span></li>`).join("")}
              ${se.map((s) => `<li><strong>schimbare de adresă</strong> — ${esc(s.email_vechi)} →
                    ${esc(s.email_nou)} <span class="ecran-nota">(cerută ${esc(dataRo(s.cerut_la, "cu_ora"))}${
                      s.confirmat_la ? ", confirmată " + esc(dataRo(s.confirmat_la, "cu_ora")) : ", NECONFIRMATĂ"})</span></li>`).join("")}
            </ul>
          </details>` : `<p class="ecran-nota" style="margin:6px 0 0">Nicio urmă de portal păstrată.</p>`}
      </div>`;
  };
  corp.innerHTML = `
    <p class="ecran-nota">Firmele de aici nu mai există. Rândul rămâne ca dovadă că au existat,
       cine le-a scos și ce s-a curățat odată cu ele. Urmele de portal se păstrează la scoaterea
       din portofoliu; la o ștergere GDPR nu se păstrează nimic.</p>
    <div class="firme-lista">${scoase.map(rand).join("")}</div>`;
}


function _bannerFirmaCreata(nume) {
  const vechi = document.getElementById("firma-creata-bine");
  if (vechi) vechi.remove();
  const b = document.createElement("div");
  b.id = "firma-creata-bine";
  b.className = "caseta-info";
  b.style.cssText = "position:fixed;left:50%;top:16px;transform:translateX(-50%);z-index:99999;max-width:min(520px,92vw)";
  b.innerHTML = `<div class="ci-mesaj">Firma <b>${esc(nume)}</b> a fost creată și apare în listă.</div>`;
  document.body.appendChild(b);
  setTimeout(() => { if (b.parentNode) b.remove(); }, 8000);
}

// [horeca] Raport Z zilnic
async function ecranRaportZ(corp, nav, t) {
  const azi = new Date().toISOString().slice(0, 10);
  corp.innerHTML = `
    <h2 class="pf-titlu">Raport Z</h2>
    <p class="pf-intro">Totaluri cu TVA inclus. Numerar + card = total. NUI-ul casei de marcat și numărul raportului sunt în antetul bonului Z tipărit — ele fac raportul unic, ca să nu se înregistreze de două ori.</p>
    <p><label class="buton-secundar" style="cursor:pointer">Import fi\u0219ier AMEF (p7b/XML)
      <input type="file" id="z-amef" accept=".p7b,.xml" style="display:none"></label></p>
    <div id="z-amef-msg"></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:480px">
      <label class="camp"><span class="camp-eticheta">Data</span><input type="date" id="z-data" class="camp-input"></label>
      <span></span>
      <label class="camp"><span class="camp-eticheta">NUI casă de marcat</span><input id="z-nui" class="camp-input" placeholder="8000000001"></label>
      <label class="camp"><span class="camp-eticheta">Nr. raport Z</span><input id="z-nr" class="camp-input" placeholder="0042"></label>
      <label class="camp"><span class="camp-eticheta">Total 11% (m\u00e2ncare)</span><input type="number" step="0.01" id="z-11" class="camp-input" placeholder="0,00"></label>
      <label class="camp"><span class="camp-eticheta">Total 21% (alcool, sucuri)</span><input type="number" step="0.01" id="z-21" class="camp-input" placeholder="0,00"></label>
      <label class="camp"><span class="camp-eticheta">Numerar</span><input type="number" step="0.01" id="z-num" class="camp-input" placeholder="0,00"></label>
      <label class="camp"><span class="camp-eticheta">Card</span><input type="number" step="0.01" id="z-card" class="camp-input" placeholder="0,00"></label>
    </div>
    <div id="z-rezultat" style="margin-top:16px"></div>
    <p style="margin-top:16px"><button class="buton-primar" id="z-salveaza">Genereaz\u0103 not\u0103</button></p>`;
  corp.querySelector("#z-amef").addEventListener("change", async (ev) => {
      const f = ev.target.files[0];
      const zona = corp.querySelector("#z-amef-msg");
      if (!f) return;
      const fd = new FormData();
      fd.append("fisier", f);
      try {
        const resp = await fetch(`/tenants/${t.id}/horeca/import-amef`, {
          method: "POST", headers: { Authorization: "Bearer " + sesiune.token() }, body: fd });
        const r = await resp.json();
        if (!resp.ok) throw new Error(r.detail || "eroare");
        zona.innerHTML = `<p class="pf-intro">Importat: Z din ${dataRo(r.data)}, total ${bani(r.total)} (numerar ${bani(r.numerar)}, card ${bani(r.card_altele)}), TVA ${r.tva_total}. Nota <b>ciorna</b> #${r.inregistrare_id} - verifica cu Z-ul tiparit.</p>`;
      } catch (e) { arataMesaj(zona, e.mesaj || e.message || "eroare", "eroare"); }
      ev.target.value = "";
    });
    corp.querySelector("#z-salveaza").addEventListener("click", async () => {
    const v = (id) => parseFloat(corp.querySelector(id).value) || 0;
    const zona = corp.querySelector("#z-rezultat");
    try {
      const r = await api.post(`/tenants/${t.id}/horeca/raport-z`, {
        data: corp.querySelector("#z-data").value,
        // [R61] cheia de unicitate a raportului Z: casa de marcat + numarul raportului
        nui: corp.querySelector("#z-nui").value.trim(),
        nr_raport: corp.querySelector("#z-nr").value.trim(),
        total_11: v("#z-11"), total_21: v("#z-21"),
        numerar: v("#z-num"), card: v("#z-card"),
      });
      zona.innerHTML = `<div class="pf-frand"><div class="pf-frand-text">
        <div class="pf-frand-nume">Notă generată (#${r.nota_id})</div>
        <div class="pf-frand-sub">TVA 11%: ${bani(r.tva_11)} \u00b7 TVA 21%: ${bani(r.tva_21)} \u00b7 baze: ${bani(r.baza_11)} / ${bani(r.baza_21)}</div>
      </div><span class="pf-frand-ok">\u2713</span></div>`;
      // [z_desc_v1] propune descarcarea gestiunii GV a lunii dupa nota Z
      const dz = new Date(corp.querySelector("#z-data").value || new Date());
      const anz = dz.getFullYear(), lz = dz.getMonth() + 1;
      const zb = document.createElement("p");
      zb.innerHTML = `<button class="buton-secundar" id="z-desc-gv">Descarc\u0103 gestiunea GV ${dataRo(`${anz}-${String(lz).padStart(2, "0")}-01`, "luna_an_numeric")} (not\u0103 ciorn\u0103)</button>`;
      zona.appendChild(zb);
      zb.querySelector("#z-desc-gv").addEventListener("click", async () => {
        try {
          const rd = await api.post(`/tenants/${t.id}/stocuri/descarcare?an=${anz}&luna=${lz}`, {});
          zb.innerHTML = `<span class="pf-intro">Desc\u0103rcare GV \u00eenregistrat\u0103 (ciorn\u0103): 607 = ${rd.cmv != null ? bani(rd.cmv) : "?"} lei (K=${rd.k ?? "?"}).</span>`;
        } catch (e2) { zb.innerHTML = `<span class="pf-intro">${(e2.mesaj || "Eroare la desc\u0103rcare")}</span>`; }
      });
        } catch (e) { arataMesaj(zona, e.mesaj || "eroare", "eroare"); }
  });
}


// [jurnal] Registru jurnal lunar
async function ecranJurnal(corp, nav, t) {
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  let inEditare = null; // id-ul notei deschise in editor

  const badge = (n) => n.status === "ciorna"
    ? `<span style="color:var(--galben);font-weight:600">\u25cf Ciorn\u0103</span>`
    : `<span style="color:var(--verde);font-weight:600">\u25cf Validat\u0103</span>`;

  let centre = [];  // [F143] centre active, pentru selectorul de pe linia de nota manuala
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    let note = [];
    try {
      const r = await api.get(`/tenants/${t.id}/jurnal?an=${an}&luna=${luna}`);
      note = (r && r.note) || [];
    } catch { corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca jurnalul.</p>`; return; }
    try {
      const rc = await api.get(`/tenants/${t.id}/centre-cost?doar_active=true`);
      centre = (rc && rc.centre) || [];
    } catch { centre = []; }
    const optCentru = (sel) => `<option value="">— centru —</option>` +
      centre.map((c) => `<option value="${c.id}"${sel === c.id ? " selected" : ""}>${esc(c.nume)}</option>`).join("");
    const rand = (n) => {
      if (inEditare === n.id) return editor(n);
      const butoane = n.status === "ciorna" ? `
        <button class="buton-primar" data-val="${n.id}">Valideaz\u0103</button>
        <button class="buton-secundar" data-edit="${n.id}">Editeaz\u0103</button>
        <button class="buton-secundar" data-del="${n.id}">\u0218terge</button>` : "";
      return `
        <div class="pf-frand">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">${dataRo(n.data)} \u00b7 ${esc(n.descriere || n.numar || "#" + n.id)} \u00b7 ${badge(n)}</div>
            <div class="pf-frand-sub">${n.linii.map((l) => `${esc(l.debit)} = ${esc(l.credit)} \u00b7 ${bani(l.suma)}${l.centru_nume ? ` \u00b7 <span style="color:var(--teal)">${esc(l.centru_nume)}</span>` : ""}`).join("<br>")}${n.sursa ? " \u00b7 sursa: " + esc(n.sursa) : ""}</div>
          </div>
          <div style="display:flex;flex-direction:column;gap:6px;align-items:stretch">${butoane}</div>
        </div>`;
    };
    const editor = (n) => `
      <div style="display:block;border:1px solid var(--galben)">
        <div class="pf-frand-nume" style="margin-bottom:8px">${n.id === "nou" || !n.id ? "Not\u0103 nou\u0103" : "Editare not\u0103 #" + n.id} \u00b7 ${dataRo(n.data)}</div>${n.factura_id ? `<div class="caseta-atentie" style="margin-bottom:8px"><div class="ca-mesaj">Aten\u021bie: nota e legat\u0103 de factura #${n.factura_id} \u2014 modificarea sumei schimb\u0103 soldul facturii.</div></div>` : ""}
        <label class="camp"><span class="camp-eticheta">Descriere</span><input type="text" id="je-desc" class="camp-input" style="width:100%" value="${esc(n.descriere || "")}"></label>
        <div class="camp-eticheta" style="margin-top:8px">Linii: cont debit = cont credit \u00b7 sum\u0103</div>
        <div id="je-linii">${n.linii.map((l, i) => `
          <div style="display:flex;gap:8px;margin-bottom:6px" data-lin="${i}">
            <input type="text" class="camp-input je-deb" placeholder="debit" aria-label="Cont debit" value="${esc(l.debit)}" style="width:90px">
            <span style="align-self:center">=</span>
            <input type="text" class="camp-input je-cre" placeholder="credit" aria-label="Cont credit" value="${esc(l.credit)}" style="width:90px">
            <input type="number" step="0.01" class="camp-input je-sum" value="${l.suma.toFixed(2)}" style="width:120px">
            <select class="camp-input je-centru" aria-label="Centru de cost" style="width:140px">${optCentru(l.centru_cost_id)}</select>
            <button class="buton-secundar je-scoate">\u2212</button>
          </div>`).join("")}</div>
        <p><button class="buton-secundar" id="je-plus">+ linie</button></p>
        <p style="margin-top:10px">
          <button class="buton-primar" id="je-salveaza">Salveaz\u0103</button>
          <button class="buton-secundar" id="je-renunta" style="margin-left:6px">Renun\u021b\u0103</button>
        </p>
      </div>`;
    const notaNoua = { id: "nou", data: `${an}-${String(luna).padStart(2,"0")}-01`, descriere: "", linii: [{ debit: "", credit: "", suma: 0 }] };
    const randuri = (inEditare === "nou" ? editor(notaNoua) : "") +
      (!note.length
        ? (inEditare === "nou" ? "" : `<div class="stare-goala">Nicio not\u0103 \u00een luna asta.</div>`)
        : note.map(rand).join(""));
    const ciorne = note.filter((n) => n.status === "ciorna").length;
    corp.innerHTML = `
      <h2 class="pf-titlu">Registru jurnal ${semnAjutor("F061")}</h2>
      <p class="pf-intro">Luna ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")} \u00b7 ${note.length} note${ciorne ? ` \u00b7 <span style="color:var(--galben);font-weight:600">${ciorne} de validat</span>` : ""}
        <button class="buton-secundar" id="j-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="buton-secundar" id="j-next">luna \u2192</button>
        <button class="buton-primar" id="j-amort" style="margin-left:12px">Genereaz\u0103 amortizarea</button>
        <button class="buton-secundar" id="j-nota-noua" style="margin-left:6px">+ Not\u0103 nou\u0103</button>
        <button class="buton-secundar" id="j-lock" style="margin-left:6px"></button>${semnAjutor("F118")}</p>
      <div id="j-mesaj"></div>
      <div class="pf-lista">${randuri}</div>`;
    const zonaMesaj = corp.querySelector("#j-mesaj");
    const bLock = corp.querySelector("#j-lock");
    let lunaBlocata = false;
    try {
      const pb = await api.get(`/tenants/${t.id}/perioade-blocate`);
      lunaBlocata = (pb.blocate || []).some((p) => p.an === an && p.luna === luna);
    } catch {}
    bLock.textContent = lunaBlocata ? "Deblocheaz\u0103 luna" : "Blocheaz\u0103 luna";
    bLock.addEventListener("click", async () => {
      try {
        if (lunaBlocata) await api.del(`/tenants/${t.id}/perioade-blocate?an=${an}&luna=${luna}`);
        else await api.post(`/tenants/${t.id}/perioade-blocate?an=${an}&luna=${luna}`, {});
        deseneaza();
      } catch (e) { arataMesaj(zonaMesaj, (e && e.mesaj) || "eroare", "eroare"); }
    });
    const eroare = (e, txt) => { arataMesaj(zonaMesaj, (e && e.mesaj) || txt, "eroare"); };
    corp.querySelector("#j-prev").addEventListener("click", () => { inEditare = null; luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#j-next").addEventListener("click", () => { inEditare = null; luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    corp.querySelector("#j-nota-noua").addEventListener("click", () => { inEditare = "nou"; deseneaza(); });
    corp.querySelector("#j-amort").addEventListener("click", async () => {
      try {
        const r = await api.post(`/tenants/${t.id}/amortizare?an=${an}&luna=${luna}`, {});
        if (r.linii) {
          arataMesaj(zonaMesaj, `Notă generată: ${r.linii} mijloace fixe, total ${bani(r.total)} lei`, "ok");
          deseneaza();   // re-randare ca sa apara nota noua
        } else {
          arataMesaj(zonaMesaj, "Nimic de amortizat.", "info");   // FARA deseneaza() - altfel sterge mesajul (bug #9)
        }
      } catch (e) { eroare(e, "Eroare la generarea notei de amortizare."); }
    });
    corp.querySelectorAll("[data-val]").forEach((b) => b.addEventListener("click", async () => {
      try { await api.post(`/tenants/${t.id}/jurnal/${b.dataset.val}/valideaza`, {}); deseneaza(); }
      catch (e) { eroare(e, "Eroare la validare"); }
    }));
    corp.querySelectorAll("[data-del]").forEach((b) => b.addEventListener("click", () => {
      confirmaCaseta(b.parentElement || b, "Ștergi această ciornă?", async () => {  // audit_cab_lot2_v1
        try { await api.del(`/tenants/${t.id}/jurnal/${b.dataset.del}`); deseneaza(); }
        catch (e) { eroare(e, "Eroare la stergere"); }
      }, { textOk: "Șterge" });
    }));
    corp.querySelectorAll("[data-edit]").forEach((b) => b.addEventListener("click", () => {
      inEditare = parseInt(b.dataset.edit); deseneaza();
    }));
    if (inEditare !== null) {
      const zona = corp.querySelector("#je-linii");
      const leaga = () => zona.querySelectorAll(".je-scoate").forEach((b) =>
        b.addEventListener("click", () => { if (zona.children.length > 1) b.parentElement.remove(); }));
      leaga();
      corp.querySelector("#je-plus").addEventListener("click", () => {
        const d = document.createElement("div");
        d.style.cssText = "display:flex;gap:8px;margin-bottom:6px";
        d.innerHTML = `<input type="text" class="camp-input je-deb" placeholder="debit" aria-label="Cont debit" style="width:90px">
          <span style="align-self:center">=</span>
          <input type="text" class="camp-input je-cre" placeholder="credit" aria-label="Cont credit" style="width:90px">
          <input type="number" step="0.01" class="camp-input je-sum" placeholder="0,00" aria-label="Sum\u0103" style="width:120px">
          <select class="camp-input je-centru" aria-label="Centru de cost" style="width:140px">${optCentru(null)}</select>
          <button class="buton-secundar je-scoate">\u2212</button>`;
        zona.appendChild(d); leaga();
      });
      corp.querySelector("#je-renunta").addEventListener("click", () => { inEditare = null; deseneaza(); });
      corp.querySelector("#je-salveaza").addEventListener("click", async () => {
        const linii = [...zona.children].map((r) => ({
          debit: r.querySelector(".je-deb").value.trim(),
          credit: r.querySelector(".je-cre").value.trim(),
          suma: parseFloat(r.querySelector(".je-sum").value) || 0,
          centru_cost_id: (r.querySelector(".je-centru") && r.querySelector(".je-centru").value) || null,  // [F143]
        }));
        try {
          if (inEditare === "nou") {
            await api.post(`/tenants/${t.id}/jurnal`,
              { descriere: corp.querySelector("#je-desc").value, data: notaNoua.data, linii });
          } else {
            await api.put(`/tenants/${t.id}/jurnal/${inEditare}`,
              { descriere: corp.querySelector("#je-desc").value, linii });
          }
          inEditare = null; deseneaza();
        } catch (e) { eroare(e, "Eroare la salvare"); }
      });
    }
  };
  deseneaza();
}


// [F143] Centre de cost — nomenclator de management (dimensiune pe notele manuale)
async function ecranCentreCost(corp, nav, t) {
  const azi = new Date();
  const anCur = azi.getFullYear();
  const aziIso = `${anCur}-${String(azi.getMonth() + 1).padStart(2, "0")}-${String(azi.getDate()).padStart(2, "0")}`;
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    let centre = [];
    try { const r = await api.get(`/tenants/${t.id}/centre-cost`); centre = (r && r.centre) || []; } catch { corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca centrele de cost.</p>`; return; }
    const rand = (c) => `
      <div class="pf-frand">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(c.nume)}</div>
          <div class="pf-frand-sub">${c.activ ? "activ" : "inactiv — nu se mai oferă la note noi"}</div>
        </div>
        <button class="buton-secundar" data-toggle="${c.id}" data-activ="${c.activ ? 1 : 0}">${c.activ ? "Dezactivează" : "Reactivează"}</button>
      </div>`;
    corp.innerHTML = `
      <h2 class="pf-titlu">Centre de cost</h2>
      <p class="pf-intro">Dimensiune de management pe notele manuale (Registru jurnal). Un centru scos din uz se dezactivează — rămâne pe notele vechi, nu se mai oferă la note noi.</p>
      <div style="display:flex;gap:8px;max-width:520px;margin-bottom:12px">
        <input type="text" id="cc-nume" class="camp-input" placeholder="Nume centru (ex: Vânzări, Producție)" aria-label="Nume centru" style="flex:1">
        <button class="buton-primar" id="cc-add">Adaugă</button>
      </div>
      <div id="cc-mesaj"></div>
      <div class="pf-lista">${centre.length ? centre.map(rand).join("") : '<div class="stare-goala">Niciun centru încă. Adaugă primul.</div>'}</div>
      <h3 class="cap-titlu" style="margin-top:22px">Realizat pe centre</h3>
      <p class="pf-intro">Din notele validate: cheltuieli (clasa 6) și venituri (clasa 7) pe fiecare centru, în perioada aleasă.</p>
      <div style="display:flex;gap:8px;align-items:center;margin-bottom:10px;flex-wrap:wrap">
        <input type="date" id="cc-de" class="camp-input" value="${anCur}-01-01" style="width:160px" aria-label="De la">
        <span>–</span>
        <input type="date" id="cc-pana" class="camp-input" value="${aziIso}" style="width:160px" aria-label="Până la">
        <button class="buton-secundar" id="cc-raport">Vezi realizat</button>
      </div>
      <div id="cc-raport-zona"></div>
      <h3 class="cap-titlu" style="margin-top:22px">Bugete și varianță (anual)</h3>
      <p class="pf-intro">Plan anual pe centru (cheltuieli + venituri), comparat cu realizatul din notele validate ale anului. Abaterea e colorată: <b>roșu</b> = orice abatere nefavorabilă (cheltuieli peste buget sau venituri sub plan), <b>verde</b> = favorabil sau exact pe țintă. Fără culoare dacă bugetul respectiv nu e setat.</p>
      <div style="display:flex;gap:8px;align-items:center;margin-bottom:10px">
        <label class="camp-eticheta" for="cc-an">An</label>
        <input type="number" id="cc-an" class="camp-input" value="${anCur}" style="width:100px">
        <button class="buton-secundar" id="cc-bugete">Vezi bugete</button>
      </div>
      <div id="cc-bugete-zona"></div>`;
    const msg = corp.querySelector("#cc-mesaj");
    const adauga = async () => {
      const nume = corp.querySelector("#cc-nume").value.trim();
      if (!nume) { arataMesaj(msg, "Scrie un nume.", "avert"); return; }
      try { await api.post(`/tenants/${t.id}/centre-cost`, { nume }); deseneaza(); }
      catch (e) { arataMesaj(msg, (e && e.mesaj) || "Eroare la adăugare.", "eroare"); }
    };
    corp.querySelector("#cc-add").addEventListener("click", adauga);
    corp.querySelector("#cc-nume").addEventListener("keydown", (e) => { if (e.key === "Enter") adauga(); });
    corp.querySelectorAll("[data-toggle]").forEach((b) => b.addEventListener("click", async () => {
      try { await api.put(`/tenants/${t.id}/centre-cost/${b.dataset.toggle}`, { activ: b.dataset.activ !== "1" }); deseneaza(); }
      catch (e) { arataMesaj(msg, (e && e.mesaj) || "Eroare.", "eroare"); }
    }));
    const raportZona = corp.querySelector("#cc-raport-zona");
    const linieRaport = (nume, ch, ve, net, inactiv) => `
      <div class="pf-frand">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(nume)}${inactiv ? " · <span style='color:var(--gri)'>inactiv</span>" : ""}</div>
          <div class="pf-frand-sub">cheltuieli ${bani(ch)} · venituri ${bani(ve)}</div>
        </div>
        <div style="font-weight:600;align-self:center;color:${net >= 0 ? 'var(--verde)' : 'var(--rosu)'}">${bani(net)}</div>
      </div>`;
    corp.querySelector("#cc-raport").addEventListener("click", async () => {
      const de = corp.querySelector("#cc-de").value, pana = corp.querySelector("#cc-pana").value;
      if (!de || !pana) { arataMesaj(msg, "Alege perioada.", "avert"); return; }
      raportZona.innerHTML = `<p class="ecran-nota">Se calculează...</p>`;
      try {
        const r = await api.get(`/tenants/${t.id}/centre-cost/raport?de=${de}&pana=${pana}`);
        const centre = (r && r.centre) || [];
        const nz = (r && r.nealocat) || { cheltuieli: 0, venituri: 0 };
        let html = centre.length
          ? centre.map((c) => linieRaport(c.nume, c.cheltuieli, c.venituri, c.net, !c.activ)).join("")
          : `<div class="stare-goala">Niciun centru definit.</div>`;
        if (nz.cheltuieli || nz.venituri) {
          html += linieRaport("Nealocat (fără centru)", nz.cheltuieli, nz.venituri, nz.venituri - nz.cheltuieli, false);
        }
        raportZona.innerHTML = `<div class="pf-lista">${html}</div>`;
      } catch (e) { arataMesaj(raportZona, (e && e.mesaj) || "Eroare la raport.", "eroare"); }
    });
    // [F143 Faza 2] bugete anuale + varianta buget vs realizat
    const bugeteZona = corp.querySelector("#cc-bugete-zona");
    const randBuget = (c) => {
      const dch = c.realizat_cheltuieli - c.buget_cheltuieli;  // >0 = peste buget (rau la cheltuieli)
      const dve = c.realizat_venituri - c.buget_venituri;      // >=0 = peste plan (bun la venituri)
      const chTxt = c.buget_cheltuieli ? ` <span style="color:${dch > 0 ? 'var(--rosu)' : 'var(--verde)'}">(${dch > 0 ? '+' : ''}${bani(dch)})</span>` : "";
      const veTxt = c.buget_venituri ? ` <span style="color:${dve >= 0 ? 'var(--verde)' : 'var(--rosu)'}">(${dve >= 0 ? '+' : ''}${bani(dve)})</span>` : "";
      return `<div class="pf-frand" style="align-items:center">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(c.nume)}${c.activ ? "" : " · <span style='color:var(--gri)'>inactiv</span>"}</div>
          <div class="pf-frand-sub">chelt: buget ${bani(c.buget_cheltuieli)} / realizat ${bani(c.realizat_cheltuieli)}${chTxt} · venit: buget ${bani(c.buget_venituri)} / realizat ${bani(c.realizat_venituri)}${veTxt}</div>
        </div>
        <div style="display:flex;gap:6px;align-items:center">
          <input type="number" step="0.01" class="camp-input bg-ch" value="${c.buget_cheltuieli}" style="width:100px" aria-label="Buget cheltuieli">
          <input type="number" step="0.01" class="camp-input bg-ve" value="${c.buget_venituri}" style="width:100px" aria-label="Buget venituri">
          <button class="buton-secundar bg-save" data-c="${c.id}">Salvează</button>
        </div>
      </div>`;
    };
    const incarcaBugete = async () => {
      const an = parseInt(corp.querySelector("#cc-an").value) || anCur;
      bugeteZona.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
      try {
        const r = await api.get(`/tenants/${t.id}/centre-cost/varianta?an=${an}`);
        const centre = (r && r.centre) || [];
        bugeteZona.innerHTML = centre.length
          ? `<div class="pf-lista">${centre.map(randBuget).join("")}</div>`
          : `<div class="stare-goala">Niciun centru definit — adaugă un centru mai sus.</div>`;
        bugeteZona.querySelectorAll(".bg-save").forEach((b) => b.addEventListener("click", async () => {
          const row = b.closest(".pf-frand");
          try {
            await api.put(`/tenants/${t.id}/centre-cost/${b.dataset.c}/buget`,
              { an, buget_cheltuieli: row.querySelector(".bg-ch").value, buget_venituri: row.querySelector(".bg-ve").value });
            incarcaBugete();
          } catch (e) { arataMesaj(msg, (e && e.mesaj) || "Eroare la salvare buget.", "eroare"); }
        }));
      } catch (e) { arataMesaj(bugeteZona, (e && e.mesaj) || "Eroare.", "eroare"); }
    };
    corp.querySelector("#cc-bugete").addEventListener("click", incarcaBugete);
  };
  deseneaza();
}


// [bonuri] documente pozate de client: lista -> detaliu la selectie  // bon_flux_e5_v1
let _bonuriMesaj = "";  // faza_b_traseu_v1
async function ecranBonuri(corp, nav, t) {
  const fmtPrimit = (iso) => {  // bon_flux_e7b_v1
    if (!iso) return "";
    const d = new Date(iso);
    const dd = (n) => String(n).padStart(2, "0");
    return "primit " + dd(d.getDate()) + "." + dd(d.getMonth() + 1) + "." + d.getFullYear() + " " + dd(d.getHours()) + ":" + dd(d.getMinutes());
  };
  let urlsPoze = [];
  let mesajSucces = "";
  let docs = [];

  const curata = () => { urlsPoze.forEach((u) => URL.revokeObjectURL(u)); urlsPoze = []; };

  async function pozaUrl(bonId, n) {
    const resp = await fetch(`/tenants/${t.id}/bonuri/${bonId}/imagine/${n}`,
      { headers: { Authorization: "Bearer " + sesiune.token() } });
    if (!resp.ok) throw new Error("imagine " + resp.status);
    // CSP nginx: img-src 'self' data: (fara blob:) -> data:URL prin FileReader, nu createObjectURL.
    const blob = await resp.blob();
    const u = await new Promise((rez, resp2) => {
      const fr = new FileReader();
      fr.onload = () => rez(fr.result);
      fr.onerror = () => resp2(fr.error || new Error("Nu am putut citi imaginea."));
      fr.readAsDataURL(blob);
    });
    urlsPoze.push(u);
    return u;
  }

  async function randeazaLista() {
    nav.setInapoi(undefined);
    curata();
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    let err = null;
    try {
      const r = await api.get(`/tenants/${t.id}/bonuri/de-verificat`);
      docs = (r && r.bonuri) || [];
    } catch (e) { err = e; }
    if (err) {
      corp.innerHTML = `<h2 class="pf-titlu">Bonuri și chitanțe ${semnAjutor("F017")}</h2>
        <p class="msg-eroare">${err.mesaj || "Nu am putut încărca documentele."}</p>`;
      return;
    }
    const itemi = !docs.length
      ? `<div class="stare-goala">Niciun document de verificat. Clienții pozează, aici certifici.</div>`
      : docs.map((b, i) => `
        <button class="acces-card meniu-card pf-frand" data-doc="${i}" style="width:100%;text-align:left">
          <b>${b.tip === "chitanta" ? "Chitanță" : "Bon fiscal"}</b> · ${b.comerciant || "emitent necitit"}
          · ${b.total ? bani(b.total) + " lei" : "sumă necitită"}${b.data ? " · din " + dataRo(b.data) : ""}
          · <b>${fmtPrimit(b.primit_la)}</b>
        </button>`).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">Bonuri și chitanțe ${semnAjutor("F017")}</h2>
      <p class="pf-intro">Documente pozate de clienți sau adăugate de tine. Alege unul ca să-l verifici și să-l contezi.</p>
      <div style="margin:0 0 12px">
        <button class="buton-secundar" id="bc-adauga">Adaugă document (pozează / încarcă)</button>
        <input type="file" id="bc-fisier" accept="image/*" multiple hidden>
        <span class="msg-eroare" id="bc-msg" style="margin-left:8px"></span>
      </div>
      ${(mesajSucces || _bonuriMesaj) ? '<p style="color:var(--verde);font-weight:600;margin:0 0 12px">' + (mesajSucces || _bonuriMesaj) + '</p>' : ""}
      ${itemi}`;
    mesajSucces = ""; _bonuriMesaj = "";
    const bcInput = corp.querySelector("#bc-fisier");  // bon_cabinet_v1
    const bcBtn = corp.querySelector("#bc-adauga");
    bcBtn.addEventListener("click", () => bcInput.click());
    bcInput.addEventListener("change", async () => {
      const fs = Array.from(bcInput.files);
      if (!fs.length) return;
      const msg = corp.querySelector("#bc-msg");
      bcBtn.disabled = true; bcBtn.textContent = "Citesc documentul...";
      const fd = new FormData();
      fs.forEach((f) => fd.append("fisiere", f));
      try {
        const r = await api.postForm(`/portal/bon?tenant_id=${t.id}`, fd);
        await api.post(`/portal/bon/${r.bon_id}/confirma?tenant_id=${t.id}`, {});
        mesajSucces = "Document adăugat — deschide-l din listă ca să-l verifici și să-l contezi.";
        randeazaLista();
      } catch (e) {
        bcBtn.disabled = false; bcBtn.textContent = "Adaugă document (pozează / încarcă)";
        msg.textContent = e.mesaj || "Nu am putut citi documentul. Încearcă o poză mai clară.";
      }
    });
    corp.querySelectorAll("[data-doc]").forEach((el) =>
      el.addEventListener("click", () => {  // faza_b_traseu_v1
        const i = parseInt(el.dataset.doc);
        const b = docs[i];
        nav.mergi((b.tip === "chitanta" ? "Chitan\u021b\u0103" : "Bon fiscal") + (b.comerciant ? " \u00b7 " + b.comerciant : ""),
          (c) => { corp = c; randeazaDetaliu(i); });
      }));
  }

  async function randeazaDetaliu(i) {
    curata();  // faza_b_traseu_v1
    const b = docs[i];
    const eChitanta = b.tip === "chitanta";
    const sumaArt = (b.articole || []).reduce((s, a) => s + (Number(a.valoare) || 0), 0);
    const dif = (b.articole || []).length ? Math.abs(Math.round((sumaArt - b.total) * 100) / 100) : 0;

    corp.innerHTML = `
      <h2 class="pf-titlu">${eChitanta ? "Chitanță" : "Bon fiscal"}${b.numar_document ? " · nr. " + b.numar_document : ""}</h2>
      ${b.mentiuni ? `<p class="pf-intro">reprezentând: ${b.mentiuni}</p>` : ""}
      ${!eChitanta && dif > 0.05 ? `<div class="caseta-atentie" style="margin:0 0 12px"><div class="ca-mesaj">Suma articolelor citite (${bani(sumaArt)}) nu se închide cu totalul (${bani(b.total)}) — verifică cu poza.</div></div>` : ""}
      <div class="doc-split">
      <div class="doc-poza" id="d-poze"><p class="ecran-nota">Se încarcă poza...</p></div>
      <div class="doc-campuri">
      <div class="grila-doc" style="grid-template-columns:${eChitanta ? "2fr 1fr 1fr" : "2fr 1fr 1fr 1fr"}">
        <label class="camp"><span class="camp-eticheta">${eChitanta ? "Emitent (furnizor)" : "Comerciant"}</span><input class="camp-input" id="d-com" value="${b.comerciant || ""}"></label>
        <label class="camp"><span class="camp-eticheta">${eChitanta ? "Data plății" : "Data"}</span><input class="camp-input" type="date" id="d-data" value="${b.data || ""}"></label>
        <label class="camp"><span class="camp-eticheta">${eChitanta ? "Suma plătită" : "Total"}</span><input class="camp-input" type="number" step="0.01" id="d-tot" value="${Number(b.total || 0).toFixed(2)}"></label>
        ${eChitanta ? "" : `<label class="camp"><span class="camp-eticheta">TVA total</span><input class="camp-input" type="number" step="0.01" id="d-tva" value="${Number(b.tva || 0).toFixed(2)}"></label>`}
      </div>
      ${eChitanta
        ? `<div id="d-cand" style="margin-top:12px"><p class="ecran-nota">Caut facturi de potrivit...</p></div>`
        : `<div style="margin-top:8px"><div class="camp-eticheta">Denumire \u00b7 valoare \u00b7 cont</div>${(b.articole || []).map((a, j) => `
            <div class="grila-doc" style="grid-template-columns:2fr 1fr 1fr;margin-top:4px">
              <input class="camp-input" id="d-den-${j}" value="${esc(a.denumire || "")}" readonly>
              <input class="camp-input" type="number" step="0.01" id="d-val-${j}" value="${Number(a.valoare || 0).toFixed(2)}">
              <input class="camp-input" id="d-cont-${j}" value="${a.cont_propus || ""}" placeholder="cont" aria-label="Cont propus">
            </div>`).join("")}</div>`}
      <div style="margin-top:14px">
        <button class="buton-verde" id="d-certifica">${eChitanta ? "Certifică plata (401 = 5311)" : "Certifică și contează"}</button>
        <button class="btn-link" id="d-renunta" style="margin-left:10px">Renunță</button>
        <span class="msg-eroare" id="d-msg" style="margin-left:10px"></span>
      </div>
      </div>
      </div>`;

    corp.querySelector("#d-renunta").addEventListener("click", () => nav.inapoiPas());  // faza_b_traseu_v1

    // pozele: mari, fixe langa date; rotita = zoom, tragere = mutare, dublu-click = ecran complet  // bon_flux_e8_v1
    (async () => {
      const zona = corp.querySelector("#d-poze");
      zona.innerHTML = "";
      for (let n = 1; n <= (b.nr_imagini || 0); n++) {
        try {
          const u = await pozaUrl(b.id, n);
          const cadru = document.createElement("div");
          cadru.className = "doc-poza-cadru";
          const img = document.createElement("img");
          img.src = u; img.alt = "document"; img.draggable = false;
          let scara = 1, tx = 0, ty = 0, drag = null, rot = Number(b.orientare) || 0;  // bon_flux_e9_v1
          const aplica = () => { img.style.transform = `translate(${tx}px,${ty}px) scale(${scara}) rotate(${rot}deg)`; };
          aplica();
          cadru.addEventListener("wheel", (e) => {
            e.preventDefault();
            if (e.shiftKey) {  // bon_flux_e9b_v1: rotire fina, indrepti bonul la orice unghi
              rot = (rot + (e.deltaY < 0 ? -2 : 2) + 360) % 360;
            } else {
              scara = Math.min(6, Math.max(1, scara * (e.deltaY < 0 ? 1.2 : 1 / 1.2)));
              if (scara === 1) { tx = 0; ty = 0; }
            }
            aplica();
          }, { passive: false });
          cadru.addEventListener("contextmenu", (e) => { e.preventDefault(); rot = (rot + 90) % 360; aplica(); });
          img.addEventListener("mousedown", (e) => { e.preventDefault(); drag = { x: e.clientX - tx, y: e.clientY - ty }; });
          cadru.addEventListener("mousemove", (e) => { if (drag) { tx = e.clientX - drag.x; ty = e.clientY - drag.y; aplica(); } });
          window.addEventListener("mouseup", () => { drag = null; });
          img.addEventListener("dblclick", () => deschideLupa(u, rot));
          cadru.appendChild(img);
          zona.appendChild(cadru);
          const bRot = document.createElement("button");
          bRot.className = "btn-link"; bRot.textContent = "\u21bb Rote\u0219te";
          bRot.addEventListener("click", () => { rot = (rot + 90) % 360; aplica(); });
          zona.appendChild(bRot);
        } catch {}
      }
      if (!zona.children.length) zona.innerHTML = `<p class="ecran-nota">Fără poză (document mai vechi).</p>`;
      else zona.insertAdjacentHTML("beforeend", '<p class="ecran-nota" style="margin:0">Rotița = mărește · Shift+rotița = îndreaptă · click-dreapta = rotește 90° · trage = mută · dublu-click = ecran complet</p>');
    })();

    // facturile candidate (doar chitanta)
    if (eChitanta) (async () => {
      const zona = corp.querySelector("#d-cand");
      let fc = [];
      try {
        const r = await api.get(`/tenants/${t.id}/bonuri/${b.id}/facturi-candidate`);
        fc = (r && r.facturi) || [];
      } catch {}
      const idPref = (fc.find((f) => f.potrivire_cui && f.potrivire_suma) || {}).id;
      zona.innerHTML = `
        <div class="camp-eticheta" style="margin-bottom:6px">Ce plătește chitanța?</div>
        ${fc.map((f) => `
          <label style="display:flex;gap:8px;align-items:center;padding:4px 0">
            <input type="radio" name="d-fact" value="${f.id}" ${f.id === idPref ? "checked" : ""}>
            <span>Factura ${f.numar || f.id} · ${f.furnizor || ""} · ${f.data ? dataRo(f.data) : ""} · ${bani(f.total)} lei${f.potrivire_cui ? '<span style="color:var(--verde);font-weight:600"> ✓ CUI</span>' : ""}${f.potrivire_suma ? '<span style="color:var(--verde);font-weight:600"> ✓ sumă</span>' : ""}</span>
          </label>`).join("")}
        <label style="display:flex;gap:8px;align-items:center;padding:4px 0">
          <input type="radio" name="d-fact" value="" ${idPref ? "" : "checked"}>
          <span>Plată directă, fără factură în sistem</span>
        </label>
        ${!fc.length ? '<p class="ecran-nota" style="margin:4px 0 0">Nicio factură primită neplătită găsită — rămâne plata directă.</p>' : ""}`;
    })();

    // certificare
    corp.querySelector("#d-certifica").addEventListener("click", async (ev) => {
      const btn = ev.currentTarget;
      const v = (id) => corp.querySelector(id).value;
      const msg = corp.querySelector("#d-msg");
      msg.textContent = "";
      if (eChitanta) {
        const suma = parseFloat(v("#d-tot")) || 0;
        if (suma <= 0) { msg.textContent = "Completează suma plătită (citește-o de pe poză)."; return; }
        if (!v("#d-data")) { msg.textContent = "Completează data plății."; return; }
        const ales = corp.querySelector('input[name="d-fact"]:checked');
        btn.disabled = true; btn.textContent = "Se contează...";
        try {
          const r = await api.post(`/tenants/${t.id}/bonuri/${b.id}/stinge`, {
            data: v("#d-data"), suma,
            partener: v("#d-com"), cui: b.cui || "",
            document: b.numar_document || "",
            factura_id: ales && ales.value ? parseInt(ales.value) : null,
          });
          const av = (r && r.avertismente) || [];
          _bonuriMesaj = "Plata a fost înregistrată în Registrul de casă." + (av.length ? " Atenție: " + av.join(" ") : "");
          nav.inapoiPas();
        } catch (e) {
          btn.disabled = false; btn.textContent = "Certifică plata (401 = 5311)";
          msg.textContent = e.mesaj || "Eroare la înregistrare.";
        }
      } else {
        const grupe = {};
        let ok = true;
        (b.articole || []).forEach((a, j) => {
          const cont = v(`#d-cont-${j}`).trim();
          const val = parseFloat(v(`#d-val-${j}`)) || 0;
          if (!cont) ok = false;
          grupe[cont] = (grupe[cont] || 0) + val;
        });
        if (!ok) { msg.textContent = "Pune contul pe fiecare articol."; return; }
        const linii = Object.entries(grupe).map(([cont, valoare]) => ({ cont, valoare: Math.round(valoare * 100) / 100 }));
        btn.disabled = true; btn.textContent = "Se contează...";
        try {
          await api.post(`/tenants/${t.id}/bonuri/${b.id}/aproba`, {
            comerciant: v("#d-com"), data: v("#d-data"),
            total: parseFloat(v("#d-tot")) || 0,
            tva: parseFloat(v("#d-tva")) || 0,
            linii,
          });
          _bonuriMesaj = "Bonul a fost contat.";
          nav.inapoiPas();
        } catch (e) {
          btn.disabled = false; btn.textContent = "Certifică și contează";
          msg.textContent = e.mesaj || "Eroare la contare.";
        }
      }
    });
  }

  randeazaLista();
}

// [balanta] Balanta de verificare - descarcare PDF lunar
async function ecranBalanta(corp, nav, t) {
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  const deseneaza = () => {
    corp.innerHTML = `
      <h2 class="pf-titlu">Balan\u021b\u0103 de verificare</h2>
      <p class="pf-intro">Luna ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")}
        <button class="buton-secundar" id="b-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="buton-secundar" id="b-next">luna \u2192</button></p>
      <p><button class="buton-primar" id="b-pdf">Descarc\u0103 PDF</button></p>
      <div id="b-mesaj"></div>`;
    corp.querySelector("#b-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#b-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    corp.querySelector("#b-pdf").addEventListener("click", async () => {
      const zona = corp.querySelector("#b-mesaj");
      try {
        const resp = await fetch(`/tenants/${t.id}/documente/balanta?an=${an}&luna=${luna}`, {
          headers: { Authorization: "Bearer " + sesiune.token() } });
        if (!resp.ok) throw new Error("eroare " + resp.status);
        const url = URL.createObjectURL(await resp.blob());
        const a = document.createElement("a");
        a.href = url; a.download = `balanta_${an}_${String(luna).padStart(2, "0")}.pdf`; a.click();
        URL.revokeObjectURL(url);
        zona.innerHTML = `<p class="pf-intro">Balanta descarcata.</p>`;
      } catch (e) { arataMesaj(zona, e.mesaj || e.message || "eroare", "eroare"); }
    });
  };
  deseneaza();
}


// [rap_com_v1] F144 v1 — Rapoarte comerciale (read-only). Doar felia constructibila
// pe schema actuala (fisa client/furnizor, vanzari pe partener, durata de incasare).
// Profit/articol/agent = decizie deschisa (DECIZII.md 17.07 + DE_FACUT.md CARENTE pct.4).
async function ecranRapoarte(corp, nav, t) {
  let an = new Date().getFullYear();
  let fisaCui = "";
  let parteneriCui = new Set();  // [rap145] partenerii existenti (toate facturile), pt validarea referintei salvate

  const randeazaFisa = async () => {
    const zona = corp.querySelector("#r-fisa");
    if (!zona) return;
    if (!fisaCui) { zona.innerHTML = ""; return; }
    // [rap145] referinta din varianta poate muri (partener sters/redenumit): gol + cauza + iesire (DS cap.6)
    if (!parteneriCui.has(fisaCui)) {
      zona.innerHTML = "";
      arataMesaj(zona, "Varianta trimite la un partener care nu mai există în facturile firmei. Alege alt partener.", "avert");
      fisaCui = "";
      const sel = corp.querySelector("#r-fisa-sel");
      if (sel) sel.value = "";
      return;
    }
    zona.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    let f;
    try {
      f = await api.get(`/tenants/${t.id}/rapoarte-comerciale/fisa?cui=${encodeURIComponent(fisaCui)}&de=${an}-01-01&pana=${an}-12-31`);
    } catch (e) { arataMesaj(zona, (e && e.mesaj) || "eroare", "eroare"); return; }
    const s = f.sumar || {};
    const rand = (r) => `
      <tr><td>${dataRo(r.data)}</td><td>${esc(r.numar)}</td>
          <td>${r.directie === "emisa" ? "Emisă" : "Primită"}</td>
          <td class="fd-td-num">${bani(r.total)}</td>
          <td class="fd-td-num">${bani(r.decontat)}</td>
          <td class="fd-td-num">${bani(r.sold)}</td>
          <td>${r.stare === "achitata" ? "achitată" : "deschisă"}</td></tr>`;
    zona.innerHTML = (f.facturi || []).length ? `
      <table class="fd-tabel">
        <thead><tr><th>Data</th><th>Număr</th><th>Direcție</th>
          <th class="fd-td-num">Total</th><th class="fd-td-num">Decontat</th>
          <th class="fd-td-num">Sold</th><th>Stare</th></tr></thead>
        <tbody>${f.facturi.map(rand).join("")}
          <tr><td colspan="3"><b>Total (${s.nr})</b></td>
            <td class="fd-td-num"><b>${bani(s.facturat)}</b></td>
            <td class="fd-td-num"><b>${bani(s.decontat)}</b></td>
            <td class="fd-td-num"><b>${bani(s.sold)}</b></td><td></td></tr>
        </tbody>
      </table>` : `<div class="stare-goala">Nicio factură pentru acest partener în perioadă.</div>`;
  };

  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    let d, variante = [];
    try {
      d = await api.get(`/tenants/${t.id}/rapoarte-comerciale?de=${an}-01-01&pana=${an}-12-31`);
    } catch (e) { arataMesaj(corp, (e && e.mesaj) || "eroare", "eroare"); return; }
    try {
      const rv = await api.get(`/tenants/${t.id}/rapoarte-salvate?tip_raport=comercial`);
      variante = rv.variante || [];
    } catch { /* variantele nu blocheaza raportul */ }
    parteneriCui = new Set((d.parteneri || []).map((p) => p.cui));
    const v = d.vanzari || { parteneri: [], total_net: 0 };
    const di = d.durata_incasare || {};
    const randVanzari = (v.parteneri || []).map((p) => `
      <tr><td>${esc(p.nume)}</td><td>${esc(p.cui || "")}</td>
          <td class="fd-td-num">${p.nr}</td>
          <td class="fd-td-num">${bani(p.net)}</td></tr>`).join("");
    const optParteneri = (d.parteneri || []).map((p) =>
      `<option value="${esc(p.cui)}"${p.cui === fisaCui ? " selected" : ""}>${esc(p.nume)}</option>`).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">Rapoarte comerciale ${semnAjutor("F144")}</h2>
      <p class="pf-intro">Anul ${an}
        <button class="buton-secundar" id="r-prev" style="margin-left:12px">← an</button>
        <button class="buton-secundar" id="r-next">an →</button></p>
      <div class="caseta-info"><span class="ci-mesaj">Profit pe produs și vânzări pe articol/agent nu apar aici: vânzarea și descărcarea gestiunii sunt documente separate, iar liniile de factură nu sunt legate de catalogul de produse.</span></div>

      <h3 class="pf-subtitlu">Durata medie de încasare</h3>
      <p class="pf-intro">${di.zile_medii != null
        ? `<b>${di.zile_medii} zile</b> · din ${di.nr_facturi} facturi încasate integral`
        : "Nicio factură încasată integral în perioadă."}</p>

      <h3 class="pf-subtitlu">Vânzări pe partener</h3>
      ${(v.parteneri || []).length ? `
        <table class="fd-tabel">
          <thead><tr><th>Partener</th><th>CUI</th>
            <th class="fd-td-num">Facturi</th><th class="fd-td-num">Vânzări (net)</th></tr></thead>
          <tbody>${randVanzari}
            <tr><td colspan="3"><b>Total</b></td>
              <td class="fd-td-num"><b>${bani(v.total_net)}</b></td></tr>
          </tbody>
        </table>` : `<div class="stare-goala">Nicio vânzare în perioadă.</div>`}

      <h3 class="pf-subtitlu">Profit pe produs</h3>
      ${(d.profit_produs || []).length ? `
        <table class="fd-tabel">
          <thead><tr><th>Articol</th><th class="fd-td-num">Cant.</th>
            <th class="fd-td-num">Venit</th><th class="fd-td-num">Cost</th><th class="fd-td-num">Profit</th></tr></thead>
          <tbody>${(d.profit_produs || []).map((p) => `
            <tr><td>${esc(p.articol)}</td><td class="fd-td-num">${p.cant}</td>
              <td class="fd-td-num">${bani(p.venit)}</td><td class="fd-td-num">${bani(p.cost)}</td>
              <td class="fd-td-num">${bani(p.profit)}</td></tr>`).join("")}</tbody>
        </table>` : `<div class="stare-goala">Niciun profit pe produs în perioadă. Disponibil doar la gestiune cantitativă (CV), pe articolele descărcate din stoc la emitere (poarta „pleacă marfa"). La global-valoric costul pe articol nu există.</div>`}

      <h3 class="pf-subtitlu">Fișă client/furnizor</h3>
      <p><select id="r-fisa-sel" aria-label="Partener fisa" class="camp-input" style="max-width:360px">
        <option value="">— alege partenerul —</option>${optParteneri}</select></p>
      <div id="r-fisa"></div>

      <h3 class="pf-subtitlu">Variantele firmei</h3>
      ${variante.length ? `<div class="pf-lista">${variante.map((vr) => `
        <div class="pf-frand">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">${esc(vr.nume)}</div>
            <div class="pf-frand-sub">anul ${(vr.filtru && vr.filtru.an) || "?"}${vr.filtru && vr.filtru.cui ? " · partener " + esc(vr.filtru.cui) : ""} · creată de ${esc(vr.autor)}</div>
          </div>
          <div style="display:flex;gap:6px;align-items:center">
            <button class="buton-secundar" data-incarca="${vr.id}">Încarcă</button>
            <button class="buton-secundar" data-sterge="${vr.id}">Șterge</button>
          </div>
        </div>`).join("")}</div>` : `<div class="stare-goala">Nicio variantă salvată încă.</div>`}
      <p style="margin-top:10px">
        <input class="camp-input" id="r-var-nume" aria-label="Nume variantă" placeholder="Nume variantă (ex. Anul curent, client X)" style="max-width:320px" maxlength="80" autocomplete="off">
        <button class="buton-primar" id="r-var-salveaza" style="margin-left:6px">Salvează varianta curentă</button>
        <span class="msg-eroare" id="r-var-msg" style="margin-left:8px"></span>
      </p>
      <div id="r-var-zona"></div>`;
    corp.querySelector("#r-prev").addEventListener("click", () => { an--; deseneaza(); });
    corp.querySelector("#r-next").addEventListener("click", () => { an++; deseneaza(); });
    const sel = corp.querySelector("#r-fisa-sel");
    sel.addEventListener("change", () => { fisaCui = sel.value; randeazaFisa(); });
    // [rap145] salveaza varianta curenta (an + partener selectat)
    corp.querySelector("#r-var-salveaza").addEventListener("click", async () => {
      const msg = corp.querySelector("#r-var-msg");
      const nume = corp.querySelector("#r-var-nume").value.trim();
      msg.textContent = "";
      if (!nume) { msg.textContent = "Dă un nume variantei."; return; }
      try {
        await api.post(`/tenants/${t.id}/rapoarte-salvate`, { tip_raport: "comercial", nume, filtru: { an, cui: fisaCui || null } });
        deseneaza();
      } catch (e) { msg.textContent = (e && e.mesaj) || "eroare"; }
    });
    // [rap145] incarca varianta: aplica filtrul; validarea partenerului se face in randeazaFisa
    corp.querySelectorAll("[data-incarca]").forEach((b) => b.addEventListener("click", () => {
      const vr = variante.find((x) => String(x.id) === b.dataset.incarca);
      if (!vr) return;
      const fl = vr.filtru || {};
      if (fl.an) an = parseInt(fl.an, 10) || an;
      fisaCui = fl.cui || "";
      deseneaza();
    }));
    // [rap145] sterge varianta (ireversibil -> caseta de confirmare, nu dialog nativ de browser)
    corp.querySelectorAll("[data-sterge]").forEach((b) => b.addEventListener("click", () => {
      const vr = variante.find((x) => String(x.id) === b.dataset.sterge);
      confirmaCaseta(corp.querySelector("#r-var-zona"), `Ștergi varianta „${vr ? esc(vr.nume) : ""}"?`, async () => {
        try { await api.del(`/tenants/${t.id}/rapoarte-salvate/${b.dataset.sterge}`); deseneaza(); }
        catch (e) { arataMesaj(corp.querySelector("#r-var-zona"), (e && e.mesaj) || "eroare", "eroare"); }
      });
    }));
    if (fisaCui) randeazaFisa();
  };

  deseneaza();
}


// [registratura_v1] F146 — Registratură documente (registru unic intrare-ieșire, v1 manual).
async function ecranRegistratura(corp, nav, t) {
  let an = new Date().getFullYear();
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    let d;
    try { d = await api.get(`/tenants/${t.id}/registratura?an=${an}`); }
    catch (e) { arataMesaj(corp, (e && e.mesaj) || "eroare", "eroare"); return; }
    const rand = (r) => `
      <div class="pf-frand">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${r.numar}/${r.an} · ${r.directie === "intrare" ? "Intrare" : "Ieșire"} · ${dataRo(r.data)}</div>
          <div class="pf-frand-sub">${esc(r.descriere)}${r.partener ? " · " + esc(r.partener) : ""}</div>
        </div>
      </div>`;
    corp.innerHTML = `
      <h2 class="pf-titlu">Registratură</h2>
      <p class="pf-intro">Anul ${an} · registru unic de intrare-ieșire
        <button class="buton-secundar" id="rg-prev" style="margin-left:12px">← an</button>
        <button class="buton-secundar" id="rg-next">an →</button></p>
      <div class="panou" style="margin-bottom:14px">
        <div class="camp" style="margin-bottom:8px">
          <label class="camp-eticheta">Direcție <span class="oblig">*</span></label>
          <select class="camp-input" id="rg-dir" aria-label="Directie inregistrare" style="max-width:200px">
            <option value="intrare">Intrare</option>
            <option value="iesire">Ieșire</option></select>
        </div>
        <div class="camp" style="margin-bottom:8px">
          <label class="camp-eticheta">Data</label>
          <input type="date" class="camp-input" id="rg-data" aria-label="Data inregistrare" style="max-width:200px" value="${new Date().toISOString().slice(0, 10)}">
        </div>
        <div class="camp" style="margin-bottom:8px">
          <label class="camp-eticheta">Descriere <span class="oblig">*</span></label>
          <input type="text" class="camp-input" id="rg-desc" placeholder="Ex. Factură furnizor X, adeverință salariat Y" autocomplete="off">
        </div>
        <div class="camp" style="margin-bottom:10px">
          <label class="camp-eticheta">Partener</label>
          <input type="text" class="camp-input" id="rg-part" placeholder="opțional" autocomplete="off">
        </div>
        <button class="buton-primar" id="rg-add">Înregistrează</button>
        <span class="msg-eroare" id="rg-msg" style="margin-left:8px"></span>
      </div>
      <div class="pf-lista">${(d.inregistrari || []).length
        ? d.inregistrari.map(rand).join("")
        : `<div class="stare-goala">Niciun document înregistrat în ${an} încă. Prima înregistrare primește numărul 1.</div>`}</div>`;
    corp.querySelector("#rg-prev").addEventListener("click", () => { an--; deseneaza(); });
    corp.querySelector("#rg-next").addEventListener("click", () => { an++; deseneaza(); });
    corp.querySelector("#rg-add").addEventListener("click", async () => {
      const msg = corp.querySelector("#rg-msg"); msg.textContent = "";
      const corpReq = {
        directie: corp.querySelector("#rg-dir").value,
        data: corp.querySelector("#rg-data").value || null,
        descriere: corp.querySelector("#rg-desc").value.trim(),
        partener: corp.querySelector("#rg-part").value.trim() || null,
      };
      if (!corpReq.descriere) { msg.textContent = "Descrierea e obligatorie."; return; }
      try {
        const r = await api.post(`/tenants/${t.id}/registratura`, corpReq);
        if (r.an !== an) an = r.an;  // data dintr-un alt an -> sari la anul respectiv
        deseneaza();
      } catch (e) { msg.textContent = (e && e.mesaj) || "eroare"; }
    });
  };
  deseneaza();
}


// [contracte_v1] F147 — Generare contracte din sabloane (mail-merge). Firma isi scrie textul cu
// marcaje {{...}}; generarea completeaza datele partenerului (clienti) + firmei si scoate PDF.
async function ecranContracte(corp, nav, t) {
  let mesajSucces = "";

  async function randeazaPrincipal() {
    nav.setInapoi(undefined);
    corp.innerHTML = '<p class="ecran-nota">Se încarcă...</p>';
    let sabloane = [];
    try { sabloane = (await api.get(`/tenants/${t.id}/contracte/sabloane`)).sabloane || []; } catch { corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca șabloanele de contract.</p>`; return; }
    const rand = (s) => `
      <div class="pf-frand">
        <div class="pf-frand-text"><div class="pf-frand-nume">${esc(s.nume)}</div></div>
        <div style="display:flex;gap:6px;align-items:center">
          <button class="buton-secundar" data-gen="${s.id}">Generează</button>
          <button class="buton-secundar" data-edit="${s.id}">Editează</button>
          <button class="buton-secundar" data-del="${s.id}">Șterge</button>
        </div>
      </div>`;
    corp.innerHTML = `
      <h2 class="pf-titlu">Contracte</h2>
      <p class="pf-intro">Șabloane proprii cu marcaje {{...}}; generarea completează datele partenerului și scoate PDF.</p>
      ${mesajSucces ? '<p style="color:var(--verde);font-weight:600;margin:0 0 12px">' + mesajSucces + '</p>' : ""}
      <p><button class="buton-primar" id="c-nou">+ Șablon nou</button></p>
      <div class="pf-lista">${sabloane.length
        ? sabloane.map(rand).join("")
        : '<div class="stare-goala">Niciun șablon de contract încă. Creează primul cu „+ Șablon nou".</div>'}</div>
      <div id="c-zona"></div>`;
    mesajSucces = "";
    corp.querySelector("#c-nou").addEventListener("click", () => randeazaEditor(null));
    corp.querySelectorAll("[data-edit]").forEach((b) => b.addEventListener("click", () =>
      randeazaEditor(sabloane.find((s) => String(s.id) === b.dataset.edit))));
    corp.querySelectorAll("[data-gen]").forEach((b) => b.addEventListener("click", () =>
      randeazaGenerare(sabloane.find((s) => String(s.id) === b.dataset.gen))));
    corp.querySelectorAll("[data-del]").forEach((b) => b.addEventListener("click", () => {
      const s = sabloane.find((x) => String(x.id) === b.dataset.del);
      confirmaCaseta(corp.querySelector("#c-zona"), `Ștergi șablonul „${esc(s ? s.nume : "")}"?`, async () => {
        try { await api.del(`/tenants/${t.id}/contracte/sabloane/${b.dataset.del}`); mesajSucces = "Șablon șters."; randeazaPrincipal(); }
        catch (e) { arataMesaj(corp.querySelector("#c-zona"), (e && e.mesaj) || "eroare", "eroare"); }
      });
    }));
  }

  async function randeazaEditor(sablon) {
    nav.setInapoi(randeazaPrincipal);
    let marcaje = {};
    try { marcaje = (await api.get(`/contracte/marcaje`)).marcaje || {}; } catch (e) {}
    const chips = Object.entries(marcaje).map(([k, v]) =>
      `<code style="padding:2px 6px;margin:0 4px 4px 0;display:inline-block" title="${esc(v)}">{{${k}}}</code>`).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">${sablon ? "Editează șablon" : "Șablon nou"}</h2>
      <div class="camp" style="margin-bottom:8px">
        <label class="camp-eticheta">Nume <span class="oblig">*</span></label>
        <input type="text" class="camp-input" id="c-nume" style="max-width:360px" value="${sablon ? esc(sablon.nume) : ""}" autocomplete="off">
      </div>
      <p class="camp-eticheta" style="margin:8px 0 4px">Marcaje disponibile:</p>
      <div style="margin-bottom:8px">${chips}</div>
      <div class="camp" style="margin-bottom:10px">
        <label class="camp-eticheta">Text contract <span class="oblig">*</span></label>
        <textarea class="camp-input" id="c-continut" rows="16" style="width:100%">${sablon ? esc(sablon.continut) : ""}</textarea>
      </div>
      <button class="buton-primar" id="c-salveaza">Salvează</button>
      <button class="btn-link" id="c-renunta" style="margin-left:10px">Renunță</button>
      <span class="msg-eroare" id="c-msg" style="margin-left:8px"></span>`;
    corp.querySelector("#c-renunta").addEventListener("click", randeazaPrincipal);
    corp.querySelector("#c-salveaza").addEventListener("click", async () => {
      const msg = corp.querySelector("#c-msg"); msg.textContent = "";
      try {
        await api.post(`/tenants/${t.id}/contracte/sabloane`, {
          id: sablon ? sablon.id : null,
          nume: corp.querySelector("#c-nume").value.trim(),
          continut: corp.querySelector("#c-continut").value,
        });
        mesajSucces = "Șablon salvat."; randeazaPrincipal();
      } catch (e) { msg.textContent = (e && e.mesaj) || "eroare"; }
    });
  }

  async function randeazaGenerare(sablon) {
    if (!sablon) return;
    nav.setInapoi(randeazaPrincipal);
    corp.innerHTML = '<p class="ecran-nota">Se încarcă...</p>';
    let clienti = [];
    try { const r = await api.get(`/tenants/${t.id}/clienti`); clienti = r.clienti || (Array.isArray(r) ? r : []); } catch (e) {}
    corp.innerHTML = `
      <h2 class="pf-titlu">Generează contract</h2>
      <p class="pf-intro">Șablon: ${esc(sablon.nume)}</p>
      <div class="camp" style="margin-bottom:8px">
        <label class="camp-eticheta">Partener (client)</label>
        <select class="camp-input" id="c-client" style="max-width:360px">
          <option value="">— alege clientul —</option>
          ${clienti.map((c) => `<option value="${c.id}">${esc(c.nume)}${c.cui ? " · " + esc(c.cui) : ""}</option>`).join("")}
        </select>
        <span class="camp-ajutor">Datele partenerului se iau din client; câmpurile lipsă rămân goale în contract.</span>
      </div>
      <button class="buton-primar" id="c-gen">Descarcă PDF</button>
      <button class="btn-link" id="c-inapoi" style="margin-left:10px">Înapoi</button>
      <span class="msg-eroare" id="c-genmsg" style="margin-left:8px"></span>`;
    corp.querySelector("#c-inapoi").addEventListener("click", randeazaPrincipal);
    corp.querySelector("#c-gen").addEventListener("click", async () => {
      const msg = corp.querySelector("#c-genmsg"); msg.textContent = "";
      try {
        const resp = await fetch(`/tenants/${t.id}/contracte/genereaza`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: "Bearer " + sesiune.token() },
          body: JSON.stringify({ sablon_id: sablon.id, client_id: corp.querySelector("#c-client").value || null }),
        });
        if (!resp.ok) throw new Error("eroare " + resp.status);
        const url = URL.createObjectURL(await resp.blob());
        const a = document.createElement("a");
        a.href = url; a.download = `contract_${sablon.nume.replace(/[^a-z0-9]+/gi, "_")}.pdf`; a.click();
        URL.revokeObjectURL(url);
      } catch (e) { msg.textContent = e.mesaj || e.message || "eroare"; }
    });
  }

  randeazaPrincipal();
}


// [wc_extras_v1] ecranMagazin mutat in ./woo_ecran.js (reutilizat de cont gratuit F156).

/* acces_client_ui_v1 */
async function ecranAccesClient(corp, nav, t) {
  let mesajSucces = "";
  async function randeazaPrincipal() {
    nav.setInapoi(undefined);
    corp.innerHTML = `
      ${mesajSucces ? '<p style="color:var(--verde);font-weight:600;margin:0 0 14px">' + mesajSucces + '</p>' : ""}
      <h3 style="margin:0 0 8px">Conturi client</h3>
      <div id="ac-lista" style="margin-bottom:16px"><p class="ecran-nota">Se încarcă...</p></div>
      <button class="buton-secundar" id="ac-btn-invita">Invit\u0103 client nou</button>
      <button class="buton-secundar" id="ac-btn-preview" style="margin-left:8px">Previzualizeaz\u0103 portalul</button>
      <div id="ac-msg" style="margin-top:10px"></div>
    `;
    mesajSucces = "";
    corp.querySelector("#ac-btn-invita").addEventListener("click", randeazaFormular);
    corp.querySelector("#ac-btn-preview").addEventListener("click", async (e) => {  // [F-preview] deschide portalul clientului in tab nou, read-only
      const b = e.currentTarget; const _t = b.textContent;
      b.disabled = true; b.textContent = "Se preg\u0103te\u0219te\u2026";  // cap.1 feedback async
      try {
        const r = await api.post(`/tenants/${t.id}/acces-portal`, {});
        // [F-preview] tokenul + userul (nume_tenant/tenant_are_cabinet) trec prin URL catre tab-ul nou;
        // fara user, preview-ul cade pe portalul gratuit (F197). URLSearchParams encodeaza corect JSON-ul.
        const _p = new URLSearchParams({ acces: r.token, u: JSON.stringify(r.user || { rol: "client" }) });
        window.open(`/#${_p.toString()}`, "_blank");
      } catch (err) {
        arataMesaj(corp.querySelector("#ac-msg"), (err && err.mesaj) || "Nu am putut deschide previzualizarea.", "eroare");
      }
      b.disabled = false; b.textContent = _t;
    });
    const zona = corp.querySelector("#ac-lista");
    try {
      const r = await api.get(`/tenants/${t.id}/client-acces`);
      const cl = r.clienti || [];
      { const _pv = corp.querySelector("#ac-btn-preview"); if (_pv && !cl.length) { _pv.disabled = true; _pv.title = "Nu exist\u0103 client. Invit\u0103 un client \u00eent\u00e2i."; } }
      if (!cl.length) { zona.innerHTML = `<p class="ecran-nota">Niciun cont de client încă.</p>`; }
      else {
        zona.innerHTML = cl.map((c) => `
          <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #e5e9f0">
            <div><b>${esc(c.email)}</b> · ${esc(c.nume || "")} ${c.activ ? "" : ' · <span style="color:var(--rosu)">dezactivat</span>'}</div>
            ${c.activ ? `<button class="buton-secundar" data-id="${c.id}">Revoc\u0103</button>` : ""}
          </div>`).join("");
        zona.querySelectorAll("button[data-id]").forEach((b) => b.addEventListener("click", () => {
          confirmaCaseta(b.parentElement, "Revoci accesul acestui client?", async () => {
            await api.del(`/tenants/${t.id}/client-acces/${b.dataset.id}`);
            randeazaPrincipal();
          }, { textOk: "Revoc\u0103" });
        }));
      }
    } catch (e) { zona.innerHTML = `<p class="ecran-nota">${e.mesaj || e.message}</p>`; }
  }
  function randeazaFormular() {
    nav.setInapoi(randeazaPrincipal);
    corp.innerHTML = `
      <div class="camp" style="margin-bottom:12px">
        <label class="camp-eticheta">Email client</label>
        <input class="camp-input" id="ac-email" type="email" placeholder="client@firma.ro" autocomplete="off" autofocus>
      </div>
      <div class="camp" style="margin-bottom:14px">
        <label class="camp-eticheta">Nume (optional)</label>
        <input class="camp-input" id="ac-nume" placeholder="Numele persoanei">
      </div>
      <p class="ecran-nota" id="ac-msg" style="margin:0 0 10px"></p>
      <button class="buton-primar" id="ac-btn">Trimite invitatia</button>
      <button class="btn-link" id="ac-renunta" style="margin-left:10px">Renun\u021b\u0103</button>
    `;
    const msg = corp.querySelector("#ac-msg");
    corp.querySelector("#ac-renunta").addEventListener("click", randeazaPrincipal);
    corp.querySelector("#ac-btn").addEventListener("click", async () => {
      const email = corp.querySelector("#ac-email").value.trim();
      if (!email.includes("@")) { msg.innerHTML = '<span class="msg-eroare">Email invalid.</span>'; return; }
      msg.textContent = "Se trimite...";
      try {
        await api.post(`/tenants/${t.id}/client-acces`, { email, nume: corp.querySelector("#ac-nume").value.trim() });
        mesajSucces = "Invitatie trimisa pe " + email + ".";
        randeazaPrincipal();
      } catch (e) { msg.innerHTML = '<span class="msg-eroare">' + (e.mesaj || e.message) + '</span>'; }
    });
  }
  randeazaPrincipal();
}
// fara_mesaj_v1

// inapoi_meniu_v1

// module_stiva_v1

// casa_std_v1

// verif_doc_pozate_v1

// bon_flux_e6_v1

// bon_flux_e7_v1

// bon_flux_e8_v1

// bon_flux_e9_v1

// bon_flux_e9b_v1

// audit_cab_lot1_v1

// audit_cab_lot2_v1

// bon_cabinet_v1

// firma_email_optional_v1

// faza_b_traseu_v1

// provenienta_v1

// fara_precompletari_v1

// entitate_sursa_unica_v1

// casa_conform_v1

// precompletari_rest_v1
