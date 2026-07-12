// firme.js — lista de firme a cabinetului (parte din desktop, NU fereastră).
// Click pe o firmă -> aceea se deschide central (fereastra firmei + "În lucru").

import { api, dataRo, arataMesaj, confirmaCaseta, deschideLupa, bani, esc, CULORI_CARD } from "../api.js";  /* msg_conventie_fe_v1 + generalizare_zi_v1 */
import { sesiune } from "../sesiune.js";
import { fluxConcediu } from "./flux_concediu.js?v=8";  /* cm_flux_v1 */
import { randeazaFacturi } from "./facturi_ecran.js";
import { ecranRip } from "./rip_ecran.js";
import { ecranOperatiuni } from "./operatiuni_ecran.js";
import { ecranEtransport } from "./etransport_ecran.js";
import { meniuMigrarePerFirma } from "./migrare.js";  // [p96_import_firma]

// randează lista în containerul dat; `inapoi()` revine la panoul cu carduri
export function randeazaListaFirme(container, nav, inapoi) {
  container.innerHTML = `
    <div class="firme-cap">
      <button class="firme-inapoi" id="firme-inapoi" title="Înapoi la panou" aria-label="Înapoi la panou">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
      </button>
      <h1 class="firme-titlu"><span style="color:var(--gri-clar);font-weight:500">Panou \u203a Firme \u203a </span>Firme existente</h1>
      <span class="firme-spatiu"></span>
      <button class="buton-primar" id="firme-adauga" style="margin-top:16px">+ Adaugă firmă</button>
    </div>
    <div class="firme-cautare">
      <label class="camp-eticheta" for="firme-q">Caut\u0103</label>
      <input type="text" id="firme-q" placeholder="Caută după nume sau CUI" autocomplete="off">
    </div>
    <div class="firme-lista" id="firme-lista"><div class="ecran-nota">Se încarcă firmele…</div></div>
  `;

  container.querySelector("#firme-inapoi").addEventListener("click", inapoi);
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
          <label class="camp-eticheta">Email client (primește automat acces la portal)</label>
          <input class="camp-input" id="fn-email" type="email" placeholder="Opțional: emailul patronului — primește acces în portal" autocomplete="off">
        </div>
        <button class="buton-primar" id="fn-salveaza" disabled>Adaugă firma</button>
      `;
      const cui = corp.querySelector("#fn-cui"), nume = corp.querySelector("#fn-nume");
      const info = corp.querySelector("#fn-cui-info"), btn = corp.querySelector("#fn-salveaza");
      let t = null;
      cui.addEventListener("input", () => {
        clearTimeout(t); btn.disabled = true; info.textContent = "";
        const v = cui.value.replace(/\D/g, "");
        if (v.length < 6) return;
        t = setTimeout(async () => {
          info.textContent = "Verific la ANAF...";
          try {
            const r = await api.get("/public/verifica-cui/" + v);
            if (r && r.gasit) { nume.value = r.denumire; info.textContent = "Găsită: " + r.denumire; btn.disabled = false; }
            else { info.textContent = "CUI negăsit la ANAF. Poți completa denumirea manual."; btn.disabled = false; }
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
          const rT = await api.post("/tenants", { nume: nume.value.trim(), cui: cui.value.replace(/\D/g, "") });
          if (emailCl) await api.post(`/tenants/${rT.tenant_id}/client-acces`, { email: emailCl, nume: "" });
          nav.inapoi(); incarca();
        } catch (e) {
          info.textContent = e.mesaj || e.message || "Eroare la creare.";
          btn.disabled = false; btn.textContent = "Adaugă firma";
        }
      });
    });
  });

  const lista = container.querySelector("#firme-lista");
  const cautare = container.querySelector("#firme-q");
  let toate = [];

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
      const rand = document.createElement("button");
      rand.className = "firme-rand";
      rand.innerHTML = `
        <div class="firme-rand-text">
          <div class="firme-rand-nume">${esc(t.nume) || "(fără nume)"}</div>
          <div class="firme-rand-cui">CUI ${t.cui || "—"}</div>
        </div>
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#9aa3af" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>
      `;
      rand.addEventListener("click", () => deschideFirma(t, nav));
      lista.appendChild(rand);
    });
  }

  cautare.addEventListener("input", () => deseneaza(cautare.value));

  api.get("/tenants")
    .then((r) => { toate = (r && r.tenants) || []; deseneaza(""); })
    .catch(() => { lista.innerHTML = `<div class="firme-gol">Firmele nu au putut fi încărcate.</div>`; });
}

// deschide o firmă: setează "În lucru" + spațiul de lucru (meniu de acțiuni)
function deschideFirma(t, nav) {
  nav.setFirmaInLucru(t.nume || "");
  nav.deschide((t.nume || "Firmă") + " \u00b7 CUI " + (t.cui || ""), (corp) => meniuFirma(corp, nav, t), { lat: "larg" });
}

// meniul de acțiuni pe o firmă (facturi activ; restul se activează pe rând)
function meniuFirma(corp, nav, t) {
  const optiuni = [
    { cheie: "facturi", titlu: "Facturi", desc: "Emite și vezi facturile firmei",
      ...CULORI_CARD.albastru,
      icon: '<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 13h6M9 17h4"/>', activ: true },
    { cheie: "declaratii", titlu: "Declarații", desc: "D112, D300, D101 și restul",
      ...CULORI_CARD.verde,
      icon: '<path d="M9 13h6M9 17h4M9 9h1"/><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/>', activ: false },
    { cheie: "control", titlu: "Control fiscal", desc: "Semafor conformare pe firmă",
      ...CULORI_CARD.teal,
      icon: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>', activ: false },
    { cheie: "salariati", titlu: "Salariați", desc: "Stat plată, fluturași, D112",
      ...CULORI_CARD.piersica,
      icon: '<circle cx="9" cy="7" r="3"/><path d="M2 21v-1a6 6 0 0 1 12 0v1"/><path d="M16 3.5a3 3 0 0 1 0 7M22 21v-1a6 6 0 0 0-4-5.7"/>', activ: true },
    { cheie: "bonuri", titlu: "Bonuri și chitanțe", desc: "Pozate de client \u2014 certifică și contează",
      ...CULORI_CARD.piersica,
      icon: '<path d="M9 11l3 3 8-8"/><path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>', activ: true },
    { cheie: "jurnal", titlu: "Registru jurnal", desc: "Notele contabile ale firmei",
      ...CULORI_CARD.ardezie,
      icon: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>', activ: true },
    { cheie: "raportz", titlu: "Raport Z", desc: "Incasari zilnice \u2192 nota automata",
      ...CULORI_CARD.chihlimbar,
      icon: '<path d="M4 4h16M4 4l16 16M4 20h16"/>', activ: true },
    { cheie: "stocuri", titlu: "Stocuri", desc: "NIR, adaos, desc\u0103rcare gestiune",
      ...CULORI_CARD.chihlimbar,
      icon: '<path d="M21 8l-9-5-9 5v8l9 5 9-5V8z"/><path d="M3 8l9 5 9-5M12 13v8"/>', activ: true },
    { cheie: "balanta", titlu: "Balan\u021b\u0103 de verificare", desc: "PDF lunar, solduri si rulaje",
      ...CULORI_CARD.albastru,
      icon: '<path d="M12 3v18M3 7h18M6 7l-3 5h6l-3-5zM18 7l-3 5h6l-3-5z"/>', activ: true },
    { cheie: "bilant", titlu: "Bilan\u021b anual", desc: "S1005 micro / S1003 mici, validare ANAF",
      ...CULORI_CARD.albastru,
      icon: '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>', activ: true },
    { cheie: "casa", titlu: "Cas\u0103", desc: "Registru de cas\u0103, plafoane numerar",
      ...CULORI_CARD.verde,
      icon: '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M6 12h.01M18 12h.01"/>', activ: true },
    { cheie: "etransport", titlu: "e-Transport", desc: "Notificare UIT, XML pentru SPV",
      ...CULORI_CARD.chihlimbar,
      icon: '<path d="M1 8h13v8H1zM14 11h4l3 3v2h-7z"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>', activ: true },
    { cheie: "operatiuni", titlu: "Operatiuni speciale", desc: "Leasing, marja, IC, sponsorizari si altele",
      ...CULORI_CARD.violet,
      icon: '<path d="M12 2l2 4 4 .5-3 3 .8 4.5L12 12l-3.8 2 .8-4.5-3-3 4-.5z"/><path d="M5 18h14M5 21h14"/>', activ: true },
    { cheie: "rip", titlu: "Incasari/plati", desc: "Partida simpla PFA/II/IF, Fisa D212",
      ...CULORI_CARD.verde,
      icon: '<path d="M12 2v20M17 7H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>', activ: true },
    { cheie: "banca", titlu: "Banc\u0103", desc: "Import extras, propuneri contare",
      ...CULORI_CARD.albastru,
      icon: '<path d="M3 21h18M4 18h16M6 18V9M10 18V9M14 18V9M18 18V9M2 9l10-6 10 6"/>', activ: true },
    { cheie: "magazin", titlu: "Magazin online", desc: "WooCommerce \u2192 facturi automate",
      ...CULORI_CARD.violet,
      icon: '<circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>', activ: true },  // wc_fe_v1
    { cheie: "verificari", titlu: "Verific\u0103ri", desc: "Echilibru, trezorerie, TVA",
      ...CULORI_CARD.albastru,
      icon: '<path d="M9 11l3 3 8-8"/><path d="M21 12v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h11"/>', activ: true },
    { cheie: "solicitari", titlu: "Solicitări client", desc: "Mesaje primite de la firma-client",
      ...CULORI_CARD.piersica,
      icon: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>', activ: true },
    { cheie: "acces", titlu: "Acces client", desc: "Invită clientul în portal",
      ...CULORI_CARD.verde,
      icon: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M19 8v6"/><path d="M22 11h-6"/>', activ: true },
    { cheie: "import", titlu: "Import date", desc: "Toate straturile de migrare, pentru aceast\u0103 firm\u0103",
      ...CULORI_CARD.albastru,
      icon: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>', activ: true },
  ];

  corp.innerHTML = `
    
    <div class="firme-optiuni">
      ${optiuni.map((o) => `
        <button class="firme-optiune" id="fa-${o.cheie}"${o.activ ? "" : ' disabled style="opacity:.55;cursor:default"'}>
          <div class="firme-optiune-icon" style="background:${o.bg}; color:${o.fg}">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${o.icon}</svg>
          </div>
          <div class="firme-optiune-titlu">${o.titlu}</div>
          <div class="firme-optiune-desc">${o.desc}${o.activ ? "" : " \u00b7 \u00een cur\u00e2nd"}</div>
        </button>`).join("")}
    </div>`;

  const bAcces = corp.querySelector("#fa-acces");
  if (bAcces) bAcces.addEventListener("click", () => nav.deschide("Acces client", (c2) => ecranAccesClient(c2, nav, t)));
  const bFacturi = corp.querySelector("#fa-facturi");
  if (bFacturi) {
    bFacturi.addEventListener("click", () => {
      nav.deschide("Facturi", (c2) => randeazaFacturi(c2, nav, t.id, {}), { lat: "larg" }); /* facturi_larg_v1 */
    });
  }
  const bSalariati = corp.querySelector("#fa-salariati");
  if (bSalariati && !bSalariati.disabled) {
    bSalariati.addEventListener("click", () => { nav.deschide("Salariați", (c2) => ecranSalariati(c2, nav, t)); });
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
    bMagazin.addEventListener("click", () => nav.deschide("Magazin online", (c2) => ecranMagazin(c2, nav, t)));
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
  const bEtransport = corp.querySelector("#fa-etransport");
  if (bEtransport) bEtransport.addEventListener("click", () => { nav.deschide("e-Transport", (c2) => ecranEtransport(c2, nav, t)); });
  const bBalanta = corp.querySelector("#fa-balanta");
  if (bBalanta) bBalanta.addEventListener("click", () => { nav.deschide("Balanță de verificare", (c2) => ecranBalanta(c2, nav, t)); });
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
      nav.mergi("Import date \u00b7 " + (t.nume || ""), (c) => meniuMigrarePerFirma(c, nav, { tenant_id: t.id, nume: t.nume }));
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
  } catch {}
  let firHtml = '<div class="mig-gol">Niciun mesaj încă.</div>';
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
    } catch {}
  });
}

// [verificari] Verificari coerenta pe firma: echilibru, trezorerie, TVA
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
      <p class="pf-intro">Luna ${String(luna).padStart(2,"0")}/${an} \u00b7 ${r ? r.note : 0} note contabile
        <button class="buton-secundar" id="vf-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="buton-secundar" id="vf-next">luna \u2192</button></p>
      <div class="pf-lista">
        ${r ? rand("Echilibru balan\u021b\u0103", r.echilibru) : ""}
        ${r ? rand("Trezorerie (f\u0103r\u0103 solduri creditoare)", r.trezorerie) : ""}
        ${r && r.documente_pozate ? `<div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">Documente pozate de clien\u021bi</div>
          <div class="pf-frand-sub">${r.documente_pozate.ok ? "\u00een regul\u0103" : [r.documente_pozate.bonuri_neverificate ? r.documente_pozate.bonuri_neverificate + " document(e) confirmate de client, necontate de peste 3 zile" : "", r.documente_pozate.ciorne_casa ? r.documente_pozate.ciorne_casa + " not\u0103(e) de cas\u0103 ciorn\u0103, nevalidate de peste 3 zile" : ""].filter(Boolean).join(" \u00b7 ")}</div>
        </div><span class="cab-pct ${r.documente_pozate.ok ? 'pct-verde' : 'pct-rosu'}"></span></div>` : ""}
        ${r ? `<div class="pf-frand"><div class="pf-frand-text"><div class="pf-frand-nume">TVA</div><div class="pf-frand-sub">${r.tva.rezultat === "de_plata" ? "de plat\u0103" : "de recuperat"}: ${bani(r.tva.suma)} lei (cont ${r.tva.cont})</div></div><span class="cab-pct pct-info"></span></div>` : ""}
        ${r && r.d205_vs_457 ? `<div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">D205 vs cont 457 (dividende)</div>
          <div class="pf-frand-sub">${r.d205_vs_457.coerent ? "coincid: " + bani(r.d205_vs_457.suma_d205) + " lei" : "D205: " + bani(r.d205_vs_457.suma_d205) + " lei vs 457: " + bani(r.d205_vs_457.suma_457) + " lei (dif " + bani(r.d205_vs_457.diferenta) + ")"}</div>
        </div><span class="cab-pct ${r.d205_vs_457.coerent ? "pct-verde" : "pct-rosu"}"></span></div>` : ""}
        ${vs ? `<div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">Stocuri (contabil vs fi\u0219e CV)</div>
          <div class="pf-frand-sub">${vs.ok ? "in regula" : vs.conturi.filter(c=>!c.ok).map(c=>`cont ${c.cod || c.cont}: contabil ${c.sold_contabil} vs fi\u0219e ${c.valoare_fise_cv} (dif ${c.diferenta})`).join(" \u00b7 ")}</div>
        </div><span class="cab-pct ${vs.ok ? 'pct-verde' : 'pct-rosu'}"></span></div>` : ""}
        ${intra ? `<div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">Intrastat (prag 1.000.000 lei/flux, an ${an})</div>
          <div class="pf-frand-sub">Introduceri: ${intra.introduceri ? intra.introduceri.cumulat + " lei (" + intra.introduceri.procent + "%)" + (intra.introduceri.status !== "sub_prag" ? " \u00b7 DEPASIT din luna " + intra.introduceri.luna_depasirii : "") : "-"} \u00b7 Expedieri: ${intra.expedieri ? intra.expedieri.cumulat + " lei (" + intra.expedieri.procent + "%)" + (intra.expedieri.status !== "sub_prag" ? " \u00b7 DEPASIT din luna " + intra.expedieri.luna_depasirii : "") : "-"}</div>
        </div><span class="cab-pct ${(intra.introduceri && intra.introduceri.status !== 'sub_prag') || (intra.expedieri && intra.expedieri.status !== 'sub_prag') ? 'pct-rosu' : 'pct-verde'}"></span></div>` : ""}
        ${!r ? '<div class="mig-gol">Nu am putut rula verific\u0103rile.</div>' : ""}
      </div>`;
    corp.querySelector("#vf-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#vf-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
  };
  deseneaza();
}

// [salariati] Stat de plata lunar + fluturasi

function formularSalariatNou(corp, nav, t, dupaSalvare) {
  const camp = (id, eticheta, tip, extra) => {
    const optional = !(extra && extra.obligatoriu);
    if (tip === "select") {
      const optiuni = (extra.optiuni || []).map(([v, l]) => `<option value="${v}">${l}</option>`).join("");
      return `<div class="camp"><label class="camp-eticheta" for="sn-${id}">${eticheta}${optional ? "" : " *"}</label><select id="sn-${id}" class="camp-input">${optiuni}</select></div>`;
    }
    if (tip === "checkbox") {
      return `<div class="camp"><label class="camp-eticheta" for="sn-${id}">${eticheta}</label><input type="checkbox" id="sn-${id}"></div>`;
    }
    const inputTip = tip === "numar" ? "number" : (tip === "data" ? "date" : "text");
    const pas = (extra && extra.pas) || "0.01";
    const restrictii = tip === "numar" ? ` step="${pas}" min="0"` : "";
    return `<div class="camp"><label class="camp-eticheta" for="sn-${id}">${eticheta}${optional ? "" : " *"}</label><input type="${inputTip}"${restrictii} id="sn-${id}" class="camp-input"></div>`;
  };
  corp.innerHTML = `
    <h2 class="pf-titlu">Salariat nou</h2>
    <div class="grila-campuri">
      ${camp("nume", "Nume", "text", { obligatoriu: true })}
      ${camp("prenume", "Prenume", "text")}
      ${camp("cnp", "CNP", "text")}
      ${camp("data_angajare", "Data angaj\u0103rii", "data")}
      ${camp("tip_norma", "Tip norm\u0103", "select", { optiuni: [["intreaga","\u00centreag\u0103"],["partiala","Par\u021bial\u0103"]] })}
      ${camp("ore_zi", "Ore/zi (norm\u0103 par\u021bial\u0103)", "numar", { pas: "0.5" })}
      ${camp("salariu_brut", "Salariu brut", "numar", { obligatoriu: true })}
      ${camp("persoane_intretinere", "Persoane \u00een \u00eentre\u021binere", "numar", { pas: "1" })}
      ${camp("judet_casa", "Jude\u021b CAS/CASS", "text")}
      ${camp("cor", "Cod COR", "text")}
      ${camp("scutit_contrib_minim", "Scutit contribu\u021bie minim\u0103", "checkbox")}
    </div>
    <p style="margin-top:12px">
      <button class="buton-primar" id="sn-salveaza">Salveaz\u0103</button>
      <button class="buton-secundar" id="sn-gata" style="margin-left:6px">Gata, \u00eenapoi la list\u0103</button></p>
    <div id="sn-mesaj"></div>`;
  corp.querySelector("#sn-gata").addEventListener("click", () => nav.inapoiPas());
  corp.querySelector("#sn-salveaza").addEventListener("click", async () => {
    const zona = corp.querySelector("#sn-mesaj");
    const nume = corp.querySelector("#sn-nume").value.trim();
    const brut = corp.querySelector("#sn-salariu_brut").value;
    if (!nume) { zona.innerHTML = '<div class="mig-gol">Numele este obligatoriu.</div>'; return; }
    const corpReq = {
      nume,
      prenume: corp.querySelector("#sn-prenume").value.trim() || null,
      cnp: corp.querySelector("#sn-cnp").value.trim() || null,
      data_angajare: corp.querySelector("#sn-data_angajare").value || null,
      tip_norma: corp.querySelector("#sn-tip_norma").value,
      ore_zi: corp.querySelector("#sn-ore_zi").value ? Number(corp.querySelector("#sn-ore_zi").value) : null,
      salariu_brut: brut ? Number(brut) : 0,
      persoane_intretinere: corp.querySelector("#sn-persoane_intretinere").value ? Number(corp.querySelector("#sn-persoane_intretinere").value) : 0,
      judet_casa: corp.querySelector("#sn-judet_casa").value.trim() || null,
      cor: corp.querySelector("#sn-cor").value.trim() || null,
      scutit_contrib_minim: corp.querySelector("#sn-scutit_contrib_minim").checked,
    };
    try {
      await api.post(`/tenants/${t.id}/salariati`, corpReq);
      if (dupaSalvare) dupaSalvare();
      formularSalariatNou(corp, nav, t, dupaSalvare);
      corp.querySelector("#sn-mesaj").innerHTML = `<p class="pf-intro" style="color:var(--verde)">Salariat salvat. Po\u021bi ad\u0103uga altul.</p>`;
    } catch (e) { zona.innerHTML = `<div class="mig-gol">${(e && e.mesaj) || "eroare la salvare"}</div>`; }
  });
}

async function ecranSalariati(corp, nav, t) {
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se calculeaza...</p>`;
    let stat = [];
    try {
      const r = await api.get(`/tenants/${t.id}/stat-plata?an=${an}&luna=${luna}`);
      stat = (r && r.stat) || [];
    } catch {}
    const randuri = !stat.length
      ? `<div class="mig-gol">Niciun salariat activ.</div>`
      : stat.map((s) => `
        <div class="pf-frand">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">${esc(s.nume)}</div>
            <div class="pf-frand-sub">brut ${bani(s.brut)} \u00b7 CAS ${bani(s.cas)} \u00b7 CASS ${bani(s.cass)} \u00b7 impozit ${bani(s.impozit)} \u00b7 <b>net ${bani(s.net)}</b> \u00b7 cost ${bani(s.cost)}</div>
          </div>
          <button class="buton-primar" data-flut="${s.id}">Fluturas</button>
          <button class="buton-secundar" data-reges="${s.id}" style="margin-left:6px">REGES</button>
          <button class="buton-secundar" data-cm="${s.id}" data-nume="${esc(s.nume)}" style="margin-left:6px">Concediu</button>
        </div>`).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">Stat de plat\u0103</h2>
      <p class="pf-intro">Luna ${String(luna).padStart(2,"0")}/${an}
        <button class="buton-secundar" id="sp-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="buton-secundar" id="sp-next">luna \u2192</button>
        <button class="buton-secundar" id="sp-reges-cfg" style="margin-left:12px">Chei REGES</button>
        <button class="buton-secundar" id="sp-reges-poll">R\u0103spunsuri REGES</button>
        <button class="buton-primar" id="sp-salariat-nou" style="margin-left:12px">+ Salariat nou</button></p>
      <div id="sp-reges-zona"></div>
      <div class="pf-lista">${randuri}</div>`;
    corp.querySelector("#sp-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#sp-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    corp.querySelector("#sp-salariat-nou").addEventListener("click", () => nav.mergi("Salariat nou", (c2) => formularSalariatNou(c2, nav, t, deseneaza)));
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
        } catch (e) { m.innerHTML = `<div class="mig-gol">${e.mesaj || "eroare"}</div>`; }
      });
    });
    corp.querySelector("#sp-reges-poll").addEventListener("click", async () => {
      try {
        const r = await api.get(`/tenants/${t.id}/reges-poll`);
        const msgs = (r && (r.mesaje || r.raspunsuri)) || [];
        zonaReges.innerHTML = `<div class="pf-frand" style="display:block;margin:10px 0">
          <div class="pf-frand-nume">R\u0103spunsuri REGES</div>
          <div class="pf-frand-sub">${msgs.length ? msgs.map((m2) => `${m2.data ? dataRo(m2.data) : ""} \u00b7 ${m2.status || m2.tip || ""} \u00b7 ${m2.mesaj || m2.detalii || JSON.stringify(m2)}`).join("<br>") : "niciun răspuns nou"}</div></div>`;
      } catch (e) { zonaReges.innerHTML = `<div class="mig-gol">${e.mesaj || "eroare"}</div>`; }
    });
    corp.querySelectorAll("[data-cm]").forEach((b) => b.addEventListener("click", () => {
      fluxConcediu(nav, t, { id: parseInt(b.dataset.cm), nume: b.dataset.nume });
    }));
    corp.querySelectorAll("[data-reges]").forEach((b) => b.addEventListener("click", () => {
      const sid = parseInt(b.dataset.reges);
      zonaReges.innerHTML = `<div style="display:block;margin:10px 0;max-width:520px">
        <div class="camp"><span class="camp-eticheta">Adresa salariatului<span class="oblig">*</span></span>
          <input type="text" id="rg-adresa" class="camp-input" placeholder="strada, nr, localitate, judet">
          <span class="camp-ajutor">Obligatorie pentru transmiterea in REGES.</span></div>
        <p style="margin-top:10px"><button class="buton-primar" id="rg-trimite">Trimite in REGES</button>
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
        } catch (e) { btn.disabled = false; btn.textContent = "Trimite in REGES"; rez.innerHTML = `<span class="msg-eroare">${esc(e.mesaj || "eroare")}</span>`; }
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
async function sectiuneaCV(corp, t, zonaM) {
  const zona = corp.querySelector("#cv-zona");
  let arts = [];
  try { const r = await api.get(`/tenants/${t.id}/stocuri/articole`); arts = r.articole || []; } catch {}
  const azi = new Date().toISOString().slice(0, 10);
  zona.innerHTML = `
    <div style="display:block;margin-bottom:14px">
      <div class="pf-frand-nume" style="margin-bottom:8px">Fi\u0219e de magazie (cantitativ-valoric, CMP)</div>
      <div class="camp-eticheta">Mi\u0219care: articol \u00b7 denumire (nou) \u00b7 dat\u0103 \u00b7 cantitate \u00b7 pre\u021b unitar \u00b7 document</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
        <select id="cv-art" class="camp-input" style="min-width:200px">
          <option value="">\u2014 articol nou \u2014</option>
          ${arts.map((a) => `<option value="${a.id}">${esc(a.denumire)} \u00b7 stoc ${a.stoc} ${esc(a.um)}${a.cmp ? " \u00b7 CMP " + a.cmp : ""}</option>`).join("")}
        </select>
        <input type="text" id="cv-den" class="camp-input" placeholder="denumire (articol nou)" aria-label="Denumire articol nou" style="flex:1;min-width:160px">
        <input type="date" id="cv-data" class="camp-input">
        <input type="number" step="0.001" id="cv-cant" class="camp-input" placeholder="cant." aria-label="Cantitate" style="width:90px">
        <input type="number" step="0.0001" id="cv-pret" class="camp-input" placeholder="pret unitar (la intrare)" aria-label="Pre\u021b unitar la intrare" style="width:170px">
        <input type="text" id="cv-doc" class="camp-input" placeholder="document" aria-label="Document" style="width:130px">
      </div>
      <p>
        <button class="buton-primar" id="cv-intrare">Intrare</button>
        <button class="buton-primar" id="cv-iesire" style="margin-left:6px">Ie\u0219ire la CMP (nota ciorn\u0103)</button>
        <button class="buton-secundar" id="cv-fisa" style="margin-left:6px">Vezi fi\u0219a</button>
      </p>
      <div style="margin-top:10px">
        <button class="buton-secundar" id="cv-inv">Inventar (stoc faptic)</button>
        <div id="cv-inv-zona" style="margin-top:8px"></div>
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
  zona.querySelector("#cv-intrare").addEventListener("click", async () => {
    try {
      const corpReq = { data: val("#cv-data"), cantitate: parseFloat(val("#cv-cant")) || 0,
        pret_unitar: parseFloat(val("#cv-pret")) || 0, document: val("#cv-doc") || null };
      if (val("#cv-art")) corpReq.articol_id = parseInt(val("#cv-art"));
      else corpReq.denumire = val("#cv-den").trim();
      if (!corpReq.articol_id && !corpReq.denumire) { zonaM.innerHTML = `<div class="mig-gol">Alege articolul sau da-i un nume.</div>`; return; }
      const r = await api.post(`/tenants/${t.id}/stocuri/intrare`, corpReq);
      zonaM.innerHTML = `<p class="pf-intro">Intrare inregistrata \u00b7 ${bani(r.valoare)} lei.</p>`;
      sectiuneaCV(corp, t, zonaM);
    } catch (e) { zonaM.innerHTML = `<div class="mig-gol">${esc(e.mesaj || "eroare")}</div>`; }
  });
  zona.querySelector("#cv-iesire").addEventListener("click", async () => {
    if (!val("#cv-art")) { zonaM.innerHTML = `<div class="mig-gol">Alege articolul pentru iesire.</div>`; return; }
    try {
      const r = await api.post(`/tenants/${t.id}/stocuri/iesire`, {
        articol_id: parseInt(val("#cv-art")), data: val("#cv-data"),
        cantitate: parseFloat(val("#cv-cant")) || 0, document: val("#cv-doc") || null });
      zonaM.innerHTML = `<p class="pf-intro">Iesire la CMP ${r.cmp} \u00b7 ${bani(r.valoare)} lei \u00b7 nota ${esc(r.nota)} (ciorna).</p>`;
      sectiuneaCV(corp, t, zonaM);
    } catch (e) { zonaM.innerHTML = `<div class="mig-gol">${esc(e.mesaj || "eroare")}</div>`; }
  });


  // [retete_v1] Retete HoReCa: CRUD + descarcare pe reteta + food cost
  const rtLista = zona.querySelector("#rt-lista");
  const rtIng = zona.querySelector("#rt-ingrediente");
  let rtLinii = [];
  const rtDeseneazaIng = () => {
    rtIng.innerHTML = rtLinii.map((l, i) => `
      <div style="display:flex;gap:6px;margin-top:6px;align-items:center">
        <select class="camp-input rt-art" data-i="${i}">${arts.map((a) =>
          `<option value="${a.id}" ${a.id == l.articol_id ? "selected" : ""}>${esc(a.denumire)} \u00b7 CMP ${a.cmp}</option>`).join("")}</select>
        <input class="camp-input rt-cant" data-i="${i}" type="number" step="0.001" value="${l.cantitate || ""}" placeholder="cant./por\u021bie" aria-label="Cantitate pe por\u021bie" style="width:120px">
        <button class="buton-sters rt-scoate" data-i="${i}">\u2212</button>
      </div>`).join("");
    rtIng.querySelectorAll(".rt-art").forEach((s) => s.addEventListener("change", (e) => { rtLinii[e.target.dataset.i].articol_id = parseInt(e.target.value); }));
    rtIng.querySelectorAll(".rt-cant").forEach((s) => s.addEventListener("input", (e) => { rtLinii[e.target.dataset.i].cantitate = parseFloat(e.target.value); }));
    rtIng.querySelectorAll(".rt-scoate").forEach((b) => b.addEventListener("click", (e) => { rtLinii.splice(e.target.dataset.i, 1); rtDeseneazaIng(); }));
  };
  const rtIncarca = async () => {
    let rr = [];
    try { const r = await api.get(`/tenants/${t.id}/retete`); rr = r.retete || []; } catch {}
    rtLista.innerHTML = !rr.length ? `<div class="mig-gol">Nicio re\u021bet\u0103 \u00eenc\u0103.</div>`
      : rr.map((r) => {
          const fc = r.food_cost || {};
          const pct = fc.food_cost_pct == null ? "\u2013" : fc.food_cost_pct + "%";
          return `<div class="pf-frand">
            <div class="pf-frand-text">
              <div class="pf-frand-nume">${esc(r.denumire)} \u00b7 ${bani(r.pret_fara_tva)} lei</div>
              <div class="pf-frand-sub">cost/por\u021bie ${bani(fc.cost_portie)} \u00b7 food cost ${pct} \u00b7 ${(r.linii || []).map((l) => `${esc(l.denumire)} ${l.cantitate}${esc(l.um || "")}`).join(", ")}</div>
            </div>
            <input class="camp-input rt-portii" data-id="${r.id}" type="number" placeholder="por\u021bii" aria-label="Num\u0103r por\u021bii" style="width:80px">
            <button class="buton-primar rt-desc" data-id="${r.id}">Descarc\u0103 (ciorn\u0103)</button>
            <button class="buton-sters rt-del" data-id="${r.id}">\u0218terge</button>
          </div>`;
        }).join("");
    rtLista.querySelectorAll(".rt-desc").forEach((b) => b.addEventListener("click", async (e) => {
      const id = e.target.dataset.id;
      const p = rtLista.querySelector(`.rt-portii[data-id="${id}"]`).value;
      if (!p) { zonaM.innerHTML = `<div class="mig-gol">Completeaz\u0103 num\u0103rul de por\u021bii.</div>`; return; }
      try {
        const r = await api.post(`/tenants/${t.id}/retete/descarca`, { reteta_id: parseInt(id), portii: parseFloat(p), data: val("#cv-data") || new Date().toISOString().slice(0, 10) });
        zonaM.innerHTML = `<p class="pf-intro">Consum \u00eenregistrat (ciorn\u0103 #${r.inregistrare_id}) \u00b7 cost total ${bani(r.cost_total)} lei.</p>`;
        sectiuneaCV(corp, t, zonaM); rtIncarca();
      } catch (er) { zonaM.innerHTML = `<div class="mig-gol">${esc(er.mesaj || "eroare")}</div>`; }
    }));
    rtLista.querySelectorAll(".rt-del").forEach((b) => b.addEventListener("click", async (e) => {
      try { await api.del(`/tenants/${t.id}/retete/${e.target.dataset.id}`); rtIncarca(); } catch (er) { zonaM.innerHTML = `<div class="mig-gol">${esc(er.mesaj || "Nu am putut \u0219terge re\u021beta.")}</div>`; }
    }));
  };
  zona.querySelector("#rt-plus").addEventListener("click", () => { rtLinii.push({ articol_id: arts[0] && arts[0].id, cantitate: "" }); rtDeseneazaIng(); });
  zona.querySelector("#rt-salveaza").addEventListener("click", async () => {
    const den = zona.querySelector("#rt-den").value.trim();
    const linii = rtLinii.filter((l) => l.articol_id && l.cantitate > 0);
    if (!den || !linii.length) { zonaM.innerHTML = `<div class="mig-gol">Completeaz\u0103 denumirea \u0219i cel pu\u021bin un ingredient.</div>`; return; }
    try {
      await api.post(`/tenants/${t.id}/retete`, { denumire: den, pret_fara_tva: parseFloat(zona.querySelector("#rt-pret").value || 0), linii });
      zona.querySelector("#rt-den").value = ""; zona.querySelector("#rt-pret").value = ""; rtLinii = []; rtDeseneazaIng(); rtIncarca();
    } catch (er) { zonaM.innerHTML = `<div class="mig-gol">${esc(er.mesaj || "eroare")}</div>`; }
  });
  rtIncarca();

  zona.querySelector("#cv-inv").addEventListener("click", () => {
    const z = zona.querySelector("#cv-inv-zona");
    z.innerHTML = `<div class="pf-lista">${arts.map((a) => `
      <div class="pf-frand"><div class="pf-frand-text">
        <div class="pf-frand-nume">${esc(a.denumire)} \u00b7 scriptic ${a.stoc} ${esc(a.um)}</div>
      </div>
      <input type="number" step="0.001" class="camp-input cvi-faptic" data-aid="${a.id}" placeholder="faptic" aria-label="Stoc faptic" style="width:110px"></div>`).join("")}
      <p style="margin-top:8px"><button class="buton-primar" id="cvi-salveaza">Salveaz\u0103 inventarul (note ciorne)</button></p>`;
    z.querySelector("#cvi-salveaza").addEventListener("click", async () => {
      const linii = [...z.querySelectorAll(".cvi-faptic")]
        .filter((i) => i.value !== "")
        .map((i) => ({ articol_id: parseInt(i.dataset.aid), faptic: parseFloat(i.value) }));
      if (!linii.length) { zonaM.innerHTML = `<div class="mig-gol">Completeaza stocul faptic la cel putin un articol.</div>`; return; }
      try {
        const r = await api.post(`/tenants/${t.id}/stocuri/inventar`,
          { data: val("#cv-data"), linii });
        zonaM.innerHTML = `<p class="pf-intro">${(r.rezultate || []).map((x) =>
          x.eroare ? `${esc(x.denumire || x.articol_id)}: ${esc(x.eroare)}`
          : x.diferenta === "0" ? `${esc(x.denumire)}: fara diferenta`
          : `${esc(x.denumire)}: ${x.diferenta > 0 ? "plus" : "minus"} ${x.diferenta} \u00b7 ${bani(x.valoare)} lei \u00b7 nota ${esc(x.nota)} (ciorna)`).join("<br>")}</p>`;
        sectiuneaCV(corp, t, zonaM);
      } catch (e) { zonaM.innerHTML = `<div class="mig-gol">${esc(e.mesaj || "eroare")}</div>`; }
    });
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
          </div></div>`).join("") || '<div class="mig-gol">Fără mișcări.</div>'}</div>`;
    } catch { zona.querySelector("#cv-fisa-zona").innerHTML = `<div class="mig-gol">Nu am putut încărca fisa.</div>`; }
  });
}

// [stocuri] NIR + descarcare gestiune (global-valorica)

async function ecranBilant(corp, nav, t) {
  {
    corp.innerHTML = `
      <h2 class="pf-titlu">Bilan\u021b anual</h2>
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
      rez.innerHTML = `<div class="mig-gol">Se valideaz\u0103...</div>`;
      try {
        const r = await api.post(`/tenants/${t.id}/${tip()}-valideaza?${par()}`, {});
        const sem = r.ok
          ? `<span style="color:#1d7a4d;font-weight:600">\u25cf Validare f\u0103r\u0103 erori</span>`
          : `<span style="color:#ff3b30;font-weight:600">\u25cf Erori la validare</span>`;
        rez.innerHTML = `<p>${sem}</p>` +
          (r.erori ? `<pre class="tip-micut" style="white-space:pre-wrap;background:var(--fundal);padding:8px;border-radius:var(--raza)">${esc(r.erori)}</pre>` : "") +
          (r.avertismente && r.avertismente.length
            ? `<p class="pf-intro">${r.avertismente.map(esc).join("<br>")}</p>` : "");
      } catch (e) { rez.innerHTML = `<div class="mig-gol">${esc(e.mesaj || "eroare")}</div>`; }
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
      } catch (e) { rez.innerHTML = `<div class="mig-gol">${esc(e.mesaj || "eroare")}</div>`; }
    });
  }
}

async function ecranStocuri(corp, nav, t) {
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  let liniiNir = [];

  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    let nirs = [];
    try { const r = await api.get(`/tenants/${t.id}/stocuri/nir?an=${an}&luna=${luna}`); nirs = r.nir || []; } catch {}
    const randuri = !nirs.length
      ? `<div class="mig-gol">Niciun NIR in luna asta.</div>`
      : nirs.map((n) => `
        <div class="pf-frand">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">NIR ${esc(n.numar)} \u00b7 ${esc(n.data)} \u00b7 ${esc(n.furnizor || "")}</div>
            <div class="pf-frand-sub">cost ${n.cost_total} \u00b7 adaos ${n.adaos_total} \u00b7 TVA neex. ${n.tva_neexigibila} \u00b7 raft ${bani(n.valoare_vanzare)} lei</div>
          </div>
        </div>`).join("");
    const randLinie = (l, i) => `
      <div style="display:flex;gap:8px;margin-bottom:6px;flex-wrap:wrap" data-i="${i}">
        <input type="text" class="camp-input sn-den" placeholder="denumire" aria-label="Denumire" value="${esc(l.denumire || "")}" style="flex:2;min-width:160px">
        <input type="number" step="0.001" class="camp-input sn-cant" placeholder="cant." aria-label="Cantitate" value="${l.cantitate || ""}" style="width:90px">
        <input type="number" step="0.0001" class="camp-input sn-pa" placeholder="pret achizitie" aria-label="Pre\u021b achizi\u021bie" value="${l.pret_achizitie || ""}" style="width:120px">
        <input type="number" step="0.0001" class="camp-input sn-pv" placeholder="pret raft (cu TVA)" aria-label="Pre\u021b raft cu TVA" value="${l.pret_vanzare || ""}" style="width:140px">
        <select class="camp-input sn-tva" style="width:80px">${[21, 11].map((c) => `<option value="${c}"${(l.cota_tva || 21) == c ? " selected" : ""}>${c}%</option>`).join("")}</select>
        <button class="buton-secundar sn-scoate">\u2212</button>
      </div>`;
    corp.innerHTML = `
      <h2 class="pf-titlu">Stocuri</h2>
      <p class="pf-intro">Luna ${String(luna).padStart(2, "0")}/${an}
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
          <input type="date" id="sn-data" class="camp-input" value="${new Date().toISOString().slice(0, 10)}">
          <input type="text" id="sn-furn" class="camp-input" placeholder="furnizor" aria-label="Furnizor" style="flex:1;min-width:160px">
          <input type="text" id="sn-cui" class="camp-input" placeholder="CUI" aria-label="CUI furnizor" style="width:120px">
        </div>
        <div class="camp-eticheta">Articole: denumire \u00b7 cantitate \u00b7 pre\u021b achizi\u021bie \u00b7 pre\u021b raft (cu TVA) \u00b7 cot\u0103 TVA</div>
        <div id="sn-linii">${liniiNir.map(randLinie).join("")}</div>
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
    const citesteLinii = () => [...zonaL.children].map((r) => ({
      denumire: r.querySelector(".sn-den").value.trim(),
      cantitate: parseFloat(r.querySelector(".sn-cant").value) || 0,
      pret_achizitie: parseFloat(r.querySelector(".sn-pa").value) || 0,
      pret_vanzare: parseFloat(r.querySelector(".sn-pv").value) || 0,
      cota_tva: parseFloat(r.querySelector(".sn-tva").value),
    }));
    const leaga = () => zonaL.querySelectorAll(".sn-scoate").forEach((b) =>
      b.addEventListener("click", () => { b.parentElement.remove(); }));
    leaga();
    corp.querySelector("#s-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } liniiNir = citesteLinii(); deseneaza(); });
    corp.querySelector("#s-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } liniiNir = citesteLinii(); deseneaza(); });
    corp.querySelector("#sn-plus").addEventListener("click", () => {
      const d = document.createElement("div");
      d.outerHTML_tmp = null;
      d.innerHTML = randLinie({}, zonaL.children.length);
      zonaL.appendChild(d.firstElementChild);
      leaga();
    });
    corp.querySelector("#sn-salveaza").addEventListener("click", async () => {
      const linii = citesteLinii().filter((l) => l.denumire);
      if (!linii.length) { zonaM.innerHTML = `<div class="mig-gol">Adaugă cel puțin un articol.</div>`; return; }
      try {
        const r = await api.post(`/tenants/${t.id}/stocuri/nir`, {
          numar: corp.querySelector("#sn-numar").value.trim(),
          data: corp.querySelector("#sn-data").value,
          furnizor: corp.querySelector("#sn-furn").value || null,
          cui: corp.querySelector("#sn-cui").value || null,
          linii,
        });
        liniiNir = [];
        zonaM.innerHTML = `<p class="pf-intro">NIR salvat \u00b7 ${r.inregistrari.length} note ciorne (cost ${r.cost_total}, adaos ${r.adaos_total}, TVA neex. ${r.tva_neexigibila}).</p>`;
        deseneaza();
      } catch (e) { zonaM.innerHTML = `<div class="mig-gol">${esc(e.mesaj || "eroare")}</div>`; }
    });
    corp.querySelector("#s-desc").addEventListener("click", () => {
      const bD = corp.querySelector("#s-desc");
      confirmaCaseta(bD.parentElement || bD, `Descarci gestiunea pe ${String(luna).padStart(2, "0")}/${an}? Se calculează din notele VALIDATE.`, async () => {  // audit_cab_lot2_v1
      try {
        const r = await api.post(`/tenants/${t.id}/stocuri/descarcare?an=${an}&luna=${luna}`, {});
        zonaM.innerHTML = r.mesaj
          ? `<div class="mig-gol">${esc(r.mesaj)}</div>`
          : `<p class="pf-intro">K=${r.k} \u00b7 CMV ${r.cmv} \u00b7 adaos ${r.adaos} \u00b7 TVA ${r.tva} \u00b7 total 371: ${bani(r.total_371)} lei \u00b7 ${r.inregistrari.length} note ciorne.</p>`;
      } catch (e) { zonaM.innerHTML = `<div class="mig-gol">${esc(e.mesaj || "eroare")}</div>`; }
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
    try { reg = await api.get(`/tenants/${t.id}/casa/registru?an=${an}&luna=${luna}`); } catch {}
    const ziAzi = new Date().toISOString().slice(0, 10);
    const avert = (reg.avertismente || []).map((a) =>
      `<div class="mig-gol" style="margin-bottom:6px">${esc(a.mesaj || a.cod || "")}${a.temei ? " \u00b7 " + esc(a.temei) : ""}</div>`).join("");
    const randuri = !(reg.operatiuni || []).length
      ? `<div class="mig-gol">Nicio operatiune in luna asta.</div>`
      : reg.operatiuni.map((o) => `
        <div class="pf-frand">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">${esc(o.data)} \u00b7 ${o.tip === "plata" ? "\u2212" : "+"}${bani(o.suma)} lei \u00b7 sold ${bani(o.sold)} lei</div>
            <div class="pf-frand-sub">${esc(o.partener || "")}${o.document ? " \u00b7 doc " + esc(o.document) : ""} \u00b7 ${esc(o.categorie)}</div>
          </div>
          <button class="buton-secundar" data-del="${o.id}">\u0218terge</button>
        </div>`).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">Cas\u0103</h2>
      <p class="pf-intro">Luna ${String(luna).padStart(2, "0")}/${an} \u00b7 sold final <b>${bani(reg.sold_final)} lei</b>
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
        <p style="margin-top:10px"><button class="buton-primar" id="c-adauga">Adaugă (notă ciornă)</button></p>
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
        zonaM.innerHTML = `<p class="pf-intro">Nota ${esc(r.nota)} creata ca ciorna.${av ? ` <b style="color:#c9961f">${av} avertisment(e) plafon.</b>` : ""}</p>`;
        deseneaza();
      } catch (e) { zonaM.innerHTML = `<div class="mig-gol">${esc(e.mesaj || "eroare")}</div>`; }
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
  const CUL = { verde: "#1d7a4d", galben: "#c9961f", rosu: "#ff3b30", gri: "#3a4250" };
  corp.innerHTML = `
    <h2 class="pf-titlu">Banc\u0103</h2>
    <p class="pf-intro">Încarcă extrasul (.xls, .xlsx, .csv) \u2014 liniile se potrivesc automat pe facturi dupa CUI.</p>
    <input type="file" id="bk-fisier" accept=".xls,.xlsx,.csv" style="margin-bottom:16px">
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
    if (!linii.length) { zonaLista.innerHTML = `<div class="mig-gol">Nicio linie de extras. Încarcă un fișier.</div>`; return; }
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
    } catch { zonaLista.innerHTML = `<div class="mig-gol">Nu am putut încărca liniile.</div>`; }
  }

  async function conteaza(id, alocari) {
    zonaMesaj.innerHTML = "";
    try {
      const r = await api.post(`/tenants/${t.id}/banca/reconciliere/${id}/conteaza`, alocari ? { alocari } : {});
      arataMesaj(zonaMesaj, `Nota ${r.nota || ""} \u2014 ${(r.inregistrari || []).length} \u00eenregistr\u0103ri create.`, "ok");
      incarca();
    } catch (e) { zonaMesaj.innerHTML = `<div class="mig-gol">${esc(e.mesaj || "Eroare la contare")}</div>`; }
  }

  async function picker(l) {
    if (!l) return;
    zonaMesaj.innerHTML = `<p class="ecran-nota">Se încarcă facturile deschise...</p>`;
    let facturi = [];
    try {
      const r = await api.get(`/tenants/${t.id}/banca/reconciliere/facturi-deschise`);
      facturi = (r.facturi || []).filter((f) => f.directie === (l.tip === "incasare" ? "emisa" : "primita"));
    } catch { zonaMesaj.innerHTML = `<div class="mig-gol">Nu am putut încărca facturile.</div>`; return; }
    if (!facturi.length) { zonaMesaj.innerHTML = `<div class="mig-gol">Nicio factura deschisa pe aceasta directie.</div>`; return; }
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
      if (!aloc.length) { zonaMesaj.innerHTML = `<div class="mig-gol">Nicio factura selectata.</div>`; return; }
      conteaza(l.id, aloc);
    });
  }

  corp.querySelector("#bk-fisier").addEventListener("change", async (ev) => {
    const f = ev.target.files[0];
    if (!f) return;
    zonaMesaj.innerHTML = `<p class="ecran-nota">Se citeste si se potriveste extrasul...</p>`;
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
      zonaMesaj.innerHTML = `<p class="pf-intro"><b>${(r.linii || []).length}</b> linii importate si potrivite.</p>`;
      incarca();
    } catch { zonaMesaj.innerHTML = `<div class="mig-gol">Nu am putut citi extrasul.</div>`; }
    ev.target.value = "";
  });

  incarca();
}

// [horeca] Raport Z zilnic
async function ecranRaportZ(corp, nav, t) {
  const azi = new Date().toISOString().slice(0, 10);
  corp.innerHTML = `
    <h2 class="pf-titlu">Raport Z</h2>
    <p class="pf-intro">Totaluri cu TVA inclus. Numerar + card = total.</p>
    <p><label class="buton-secundar" style="cursor:pointer">Import fisier AMEF (p7b/XML)
      <input type="file" id="z-amef" accept=".p7b,.xml" style="display:none"></label></p>
    <div id="z-amef-msg"></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:480px">
      <label class="camp"><span class="camp-eticheta">Data</span><input type="date" id="z-data" class="camp-input"></label>
      <span></span>
      <label class="camp"><span class="camp-eticheta">Total 11% (mancare)</span><input type="number" step="0.01" id="z-11" class="camp-input" placeholder="0,00"></label>
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
        zona.innerHTML = `<p class="pf-intro">Importat: Z din ${dataRo(r.data)}, total ${r.total} (numerar ${r.numerar}, card ${r.card_altele}), TVA ${r.tva_total}. Nota <b>ciorna</b> #${r.inregistrare_id} - verifica cu Z-ul tiparit.</p>`;
      } catch (e) { zona.innerHTML = `<div class="mig-gol">${e.message || "eroare"}</div>`; }
      ev.target.value = "";
    });
    corp.querySelector("#z-salveaza").addEventListener("click", async () => {
    const v = (id) => parseFloat(corp.querySelector(id).value) || 0;
    const zona = corp.querySelector("#z-rezultat");
    try {
      const r = await api.post(`/tenants/${t.id}/horeca/raport-z`, {
        data: corp.querySelector("#z-data").value,
        total_11: v("#z-11"), total_21: v("#z-21"),
        numerar: v("#z-num"), card: v("#z-card"),
      });
      zona.innerHTML = `<div class="pf-frand"><div class="pf-frand-text">
        <div class="pf-frand-nume">Nota generata (#${r.nota_id})</div>
        <div class="pf-frand-sub">TVA 11%: ${bani(r.tva_11)} \u00b7 TVA 21%: ${bani(r.tva_21)} \u00b7 baze: ${bani(r.baza_11)} / ${bani(r.baza_21)}</div>
      </div><span class="pf-frand-ok">\u2713</span></div>`;
      // [z_desc_v1] propune descarcarea gestiunii GV a lunii dupa nota Z
      const dz = new Date(corp.querySelector("#z-data").value || new Date());
      const anz = dz.getFullYear(), lz = dz.getMonth() + 1;
      const zb = document.createElement("p");
      zb.innerHTML = `<button class="buton-secundar" id="z-desc-gv">Descarc\u0103 gestiunea GV ${String(lz).padStart(2,"0")}/${anz} (not\u0103 ciorn\u0103)</button>`;
      zona.appendChild(zb);
      zb.querySelector("#z-desc-gv").addEventListener("click", async () => {
        try {
          const rd = await api.post(`/tenants/${t.id}/stocuri/descarcare?an=${anz}&luna=${lz}`, {});
          zb.innerHTML = `<span class="pf-intro">Desc\u0103rcare GV \u00eenregistrat\u0103 (ciorn\u0103): 607 = ${rd.cmv != null ? bani(rd.cmv) : "?"} lei (K=${rd.k ?? "?"}).</span>`;
        } catch (e2) { zb.innerHTML = `<span class="pf-intro">${(e2.mesaj || "Eroare la desc\u0103rcare")}</span>`; }
      });
        } catch (e) { zona.innerHTML = `<div class="mig-gol">${e.mesaj || "eroare"}</div>`; }
  });
}


// [jurnal] Registru jurnal lunar
async function ecranJurnal(corp, nav, t) {
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  let inEditare = null; // id-ul notei deschise in editor

  const badge = (n) => n.status === "ciorna"
    ? `<span style="color:#c9961f;font-weight:600">\u25cf Ciorn\u0103</span>`
    : `<span style="color:#1d7a4d;font-weight:600">\u25cf Validat\u0103</span>`;

  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    let note = [];
    try {
      const r = await api.get(`/tenants/${t.id}/jurnal?an=${an}&luna=${luna}`);
      note = (r && r.note) || [];
    } catch {}
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
            <div class="pf-frand-sub">${n.linii.map((l) => `${esc(l.debit)} = ${esc(l.credit)} \u00b7 ${bani(l.suma)}`).join("<br>")}${n.sursa ? " \u00b7 sursa: " + esc(n.sursa) : ""}</div>
          </div>
          <div style="display:flex;flex-direction:column;gap:6px;align-items:stretch">${butoane}</div>
        </div>`;
    };
    const editor = (n) => `
      <div style="display:block;border:1px solid var(--galben)">
        <div class="pf-frand-nume" style="margin-bottom:8px">${n.id === "nou" || !n.id ? "Not\u0103 nou\u0103" : "Editare not\u0103 #" + n.id} \u00b7 ${dataRo(n.data)}</div>${n.factura_id ? `<div class="mig-gol" style="margin-bottom:8px">Aten\u021bie: nota e legat\u0103 de factura #${n.factura_id} \u2014 modificarea sumei schimb\u0103 soldul facturii.</div>` : ""}
        <label class="camp"><span class="camp-eticheta">Descriere</span><input type="text" id="je-desc" class="camp-input" style="width:100%" value="${esc(n.descriere || "")}"></label>
        <div class="camp-eticheta" style="margin-top:8px">Linii: cont debit = cont credit \u00b7 sum\u0103</div>
        <div id="je-linii">${n.linii.map((l, i) => `
          <div style="display:flex;gap:8px;margin-bottom:6px" data-lin="${i}">
            <input type="text" class="camp-input je-deb" placeholder="debit" aria-label="Cont debit" value="${esc(l.debit)}" style="width:90px">
            <span style="align-self:center">=</span>
            <input type="text" class="camp-input je-cre" placeholder="credit" aria-label="Cont credit" value="${esc(l.credit)}" style="width:90px">
            <input type="number" step="0.01" class="camp-input je-sum" value="${l.suma.toFixed(2)}" style="width:120px">
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
        ? (inEditare === "nou" ? "" : `<div class="mig-gol">Nicio nota in luna asta.</div>`)
        : note.map(rand).join(""));
    const ciorne = note.filter((n) => n.status === "ciorna").length;
    corp.innerHTML = `
      <h2 class="pf-titlu">Registru jurnal</h2>
      <p class="pf-intro">Luna ${String(luna).padStart(2, "0")}/${an} \u00b7 ${note.length} note${ciorne ? ` \u00b7 <span style="color:#c9961f;font-weight:600">${ciorne} de validat</span>` : ""}
        <button class="buton-secundar" id="j-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="buton-secundar" id="j-next">luna \u2192</button>
        <button class="buton-primar" id="j-amort" style="margin-left:12px">Genereaz\u0103 amortizarea</button>
        <button class="buton-secundar" id="j-nota-noua" style="margin-left:6px">+ Not\u0103 nou\u0103</button>
        <button class="buton-secundar" id="j-lock" style="margin-left:6px"></button></p>
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
      } catch (e) { zonaMesaj.innerHTML = `<div class="mig-gol">${(e && e.mesaj) || "eroare"}</div>`; }
    });
    const eroare = (e, txt) => { zonaMesaj.innerHTML = `<div class="mig-gol">${esc((e && e.mesaj) || txt)}</div>`; };
    corp.querySelector("#j-prev").addEventListener("click", () => { inEditare = null; luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#j-next").addEventListener("click", () => { inEditare = null; luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    corp.querySelector("#j-nota-noua").addEventListener("click", () => { inEditare = "nou"; deseneaza(); });
    corp.querySelector("#j-amort").addEventListener("click", async () => {
      try {
        const r = await api.post(`/tenants/${t.id}/amortizare?an=${an}&luna=${luna}`, {});
        arataMesaj(zonaMesaj, r.linii ? `Notă generată: ${r.linii} mijloace fixe, total ${bani(r.total)} lei` : "Nimic de amortizat.", r.linii ? "ok" : "info");
        deseneaza();
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
          <button class="buton-secundar je-scoate">\u2212</button>`;
        zona.appendChild(d); leaga();
      });
      corp.querySelector("#je-renunta").addEventListener("click", () => { inEditare = null; deseneaza(); });
      corp.querySelector("#je-salveaza").addEventListener("click", async () => {
        const linii = [...zona.children].map((r) => ({
          debit: r.querySelector(".je-deb").value.trim(),
          credit: r.querySelector(".je-cre").value.trim(),
          suma: parseFloat(r.querySelector(".je-sum").value) || 0,
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
    const u = URL.createObjectURL(await resp.blob());
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
      corp.innerHTML = `<h2 class="pf-titlu">Bonuri și chitanțe</h2>
        <p class="msg-eroare">${err.mesaj || "Nu am putut încărca documentele."}</p>`;
      return;
    }
    const itemi = !docs.length
      ? `<div class="mig-gol">Niciun document de verificat. Clienții pozează, aici certifici.</div>`
      : docs.map((b, i) => `
        <button class="acces-card meniu-card pf-frand" data-doc="${i}" style="width:100%;text-align:left">
          <b>${b.tip === "chitanta" ? "Chitanță" : "Bon fiscal"}</b> · ${b.comerciant || "emitent necitit"}
          · ${b.total ? bani(b.total) + " lei" : "sumă necitită"}${b.data ? " · din " + dataRo(b.data) : ""}
          · <b>${fmtPrimit(b.primit_la)}</b>
        </button>`).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">Bonuri și chitanțe</h2>
      <p class="pf-intro">Documente pozate de clienți sau adăugate de tine. Alege unul ca să-l verifici și să-l contezi.</p>
      <div style="margin:0 0 12px">
        <button class="buton-secundar" id="bc-adauga">Adaugă document (pozează / încarcă)</button>
        <input type="file" id="bc-fisier" accept="image/*" multiple hidden>
        <span class="msg-eroare" id="bc-msg" style="margin-left:8px"></span>
      </div>
      ${(mesajSucces || _bonuriMesaj) ? '<p style="color:#1d7a4d;font-weight:600;margin:0 0 12px">' + (mesajSucces || _bonuriMesaj) + '</p>' : ""}
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
      <div style="display:grid;grid-template-columns:${eChitanta ? "2fr 1fr 1fr" : "2fr 1fr 1fr 1fr"};gap:8px;align-items:end">
        <label class="camp"><span class="camp-eticheta">${eChitanta ? "Emitent (furnizor)" : "Comerciant"}</span><input class="camp-input" id="d-com" value="${b.comerciant || ""}"></label>
        <label class="camp"><span class="camp-eticheta">${eChitanta ? "Data plății" : "Data"}</span><input class="camp-input" type="date" id="d-data" value="${b.data || ""}"></label>
        <label class="camp"><span class="camp-eticheta">${eChitanta ? "Suma plătită" : "Total"}</span><input class="camp-input" type="number" step="0.01" id="d-tot" value="${b.total}"></label>
        ${eChitanta ? "" : `<label class="camp"><span class="camp-eticheta">TVA total</span><input class="camp-input" type="number" step="0.01" id="d-tva" value="${b.tva}"></label>`}
      </div>
      ${eChitanta
        ? `<div id="d-cand" style="margin-top:12px"><p class="ecran-nota">Caut facturi de potrivit...</p></div>`
        : `<div style="margin-top:8px"><div class="camp-eticheta">Denumire \u00b7 valoare \u00b7 cont</div>${(b.articole || []).map((a, j) => `
            <div style="display:grid;grid-template-columns:2fr 1fr 1fr;gap:8px;margin-top:4px">
              <input class="camp-input" id="d-den-${j}" value="${esc(a.denumire || "")}" readonly>
              <input class="camp-input" type="number" step="0.01" id="d-val-${j}" value="${a.valoare || 0}">
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
            <span>Factura ${f.numar || f.id} · ${f.furnizor || ""} · ${f.data ? dataRo(f.data) : ""} · ${bani(f.total)} lei${f.potrivire_cui ? '<span style="color:#1d7a4d;font-weight:600"> ✓ CUI</span>' : ""}${f.potrivire_suma ? '<span style="color:#1d7a4d;font-weight:600"> ✓ sumă</span>' : ""}</span>
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
      <p class="pf-intro">Luna ${String(luna).padStart(2, "0")}/${an}
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
      } catch (e) { zona.innerHTML = `<div class="mig-gol">${e.message || "eroare"}</div>`; }
    });
  };
  deseneaza();
}


// ---------- MAGAZIN ONLINE (WooCommerce) ----------  // wc_fe_v1
async function ecranMagazin(corp, nav, t) {
  let mesajSucces = "";
  async function randeazaPrincipal() {
    nav.setInapoi(undefined);
    corp.innerHTML = '<p class="ecran-nota">Se încarcă...</p>';
    let cfg = { configurat: false, url: null };
    try { cfg = await api.get(`/tenants/${t.id}/woocommerce/config`); } catch (e) {}
    corp.innerHTML = `
      <h2 class="pf-titlu">Magazin online</h2>
      <p class="pf-intro">Comenzile din WooCommerce devin facturi emise automat (zilnic la 07:30).</p>
      ${mesajSucces ? '<p style="color:#1d7a4d;font-weight:600;margin:0 0 14px">' + mesajSucces + '</p>' : ""}
      <p style="margin:0 0 16px"><b>Stare:</b> ${cfg.configurat ? "conectat la " + cfg.url : "neconfigurat"}</p>
      ${cfg.configurat ? '<button class="buton-primar" id="wc-sinc" style="margin-bottom:12px">Sincronizeaza acum</button><br>' : ""}
      <button class="acces-card meniu-card" id="wc-btn-config">${cfg.configurat ? "Modifica configurarea" : "Configureaza magazinul"}</button>
      <div class="em-rezultat" id="wc-rezultat"></div>
    `;
    mesajSucces = "";
    corp.querySelector("#wc-btn-config").addEventListener("click", randeazaConfig);
    const zona = corp.querySelector("#wc-rezultat");
    const bs = corp.querySelector("#wc-sinc");
    if (bs) bs.addEventListener("click", async () => {
      zona.innerHTML = `<p class="ecran-nota">Se sincronizeaza...</p>`;
      try {
        const r = await api.post(`/tenants/${t.id}/woocommerce/sincronizeaza`, {});
        const n = (r.importate || []).length;
        zona.innerHTML = `<span style="color:#1d7a4d">${n} facturi importate, ${r.sarite || 0} deja existente.</span>`;
      } catch (e) { zona.innerHTML = `<span style="color:var(--rosu)">${e.mesaj || "eroare"}</span>`; }
    });
  }
  function randeazaConfig() {
    nav.setInapoi(randeazaPrincipal);
    corp.innerHTML = `
      <h2 class="pf-titlu">Configurare magazin</h2>
      <div class="camp" style="margin-bottom:10px">
        <label class="camp-eticheta">URL magazin</label>
        <input class="camp-input" id="wc-url" placeholder="https://magazin.ro" autocomplete="off" autofocus>
      </div>
      <div class="camp" style="margin-bottom:10px">
        <label class="camp-eticheta">Consumer Key</label>
        <input class="camp-input" id="wc-ck" placeholder="ck_..." autocomplete="off">
      </div>
      <div class="camp" style="margin-bottom:14px">
        <label class="camp-eticheta">Consumer Secret</label>
        <input class="camp-input" id="wc-cs" placeholder="cs_..." type="password" autocomplete="off">
      </div>
      <button class="buton-primar" id="wc-salveaza">Salveaz\u0103</button>
      <button class="btn-link" id="wc-renunta" style="margin-left:10px">Renun\u021b\u0103</button>
      <p class="ecran-nota" id="wc-msg" style="margin:10px 0 0"></p>
    `;
    corp.querySelector("#wc-renunta").addEventListener("click", randeazaPrincipal);
    corp.querySelector("#wc-salveaza").addEventListener("click", async () => {
      const msg = corp.querySelector("#wc-msg");
      try {
        await api.put(`/tenants/${t.id}/woocommerce/config`, {
          url: corp.querySelector("#wc-url").value.trim() || null,
          ck: corp.querySelector("#wc-ck").value.trim() || null,
          cs: corp.querySelector("#wc-cs").value.trim() || null,
        });
        mesajSucces = "Configurare salvata.";
        randeazaPrincipal();
      } catch (e) { msg.innerHTML = '<span class="msg-eroare">' + (e.mesaj || "eroare") + '</span>'; }
    });
  }
  randeazaPrincipal();
}
/* acces_client_ui_v1 */
async function ecranAccesClient(corp, nav, t) {
  let mesajSucces = "";
  async function randeazaPrincipal() {
    nav.setInapoi(undefined);
    corp.innerHTML = `
      ${mesajSucces ? '<p style="color:#1d7a4d;font-weight:600;margin:0 0 14px">' + mesajSucces + '</p>' : ""}
      <h3 style="margin:0 0 8px">Conturi client</h3>
      <div id="ac-lista" style="margin-bottom:16px"><p class="ecran-nota">Se încarcă...</p></div>
      <button class="acces-card meniu-card" id="ac-btn-invita">Invita client nou</button>
    `;
    mesajSucces = "";
    corp.querySelector("#ac-btn-invita").addEventListener("click", randeazaFormular);
    const zona = corp.querySelector("#ac-lista");
    try {
      const r = await api.get(`/tenants/${t.id}/client-acces`);
      const cl = r.clienti || [];
      if (!cl.length) { zona.innerHTML = `<p class="ecran-nota">Niciun cont de client încă.</p>`; }
      else {
        zona.innerHTML = cl.map((c) => `
          <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #e5e9f0">
            <div><b>${esc(c.email)}</b> · ${esc(c.nume || "")} ${c.activ ? "" : ' · <span style="color:var(--rosu)">dezactivat</span>'}</div>
            ${c.activ ? `<button class="buton-secundar" data-id="${c.id}">Revoca</button>` : ""}
          </div>`).join("");
        zona.querySelectorAll("button[data-id]").forEach((b) => b.addEventListener("click", () => {
          confirmaCaseta(b.parentElement, "Revoci accesul acestui client?", async () => {
            await api.del(`/tenants/${t.id}/client-acces/${b.dataset.id}`);
            randeazaPrincipal();
          }, { textOk: "Revoca" });
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
