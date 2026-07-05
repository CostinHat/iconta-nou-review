// firme.js — lista de firme a cabinetului (parte din desktop, NU fereastră).
// Click pe o firmă -> aceea se deschide central (fereastra firmei + "În lucru").

import { api } from "../api.js";
import { sesiune } from "../sesiune.js";
import { randeazaFacturi } from "./facturi_ecran.js?v=2";
import { ecranRip } from "./rip_ecran.js?v=2";
import { ecranOperatiuni } from "./operatiuni_ecran.js?v=8";
import { ecranEtransport } from "./etransport_ecran.js?v=1";

// randează lista în containerul dat; `inapoi()` revine la panoul cu carduri
export function randeazaListaFirme(container, nav, inapoi) {
  container.innerHTML = `
    <div class="firme-cap">
      <button class="firme-inapoi" id="firme-inapoi" title="Înapoi la panou" aria-label="Înapoi la panou">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
      </button>
      <h1 class="firme-titlu">Firme</h1>
      <span class="firme-spatiu"></span>
      <button class="buton-primar buton-ingust" id="firme-adauga">+ Adaugă firmă</button>
    </div>
    <div class="firme-cautare">
      <input type="text" id="firme-q" placeholder="Caută după nume sau CUI" autocomplete="off">
    </div>
    <div class="firme-lista" id="firme-lista"><div class="ecran-nota">Se încarcă firmele…</div></div>
  `;

  container.querySelector("#firme-inapoi").addEventListener("click", inapoi);
  container.querySelector("#firme-adauga").addEventListener("click", () => {
    nav.deschide("Adaugă firmă", (corp) => {
      corp.innerHTML = `<p class="ecran-nota">Formular „Adaugă firmă" — în construcție.</p>`;
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
          <div class="firme-rand-nume">${t.nume || "(fără nume)"}</div>
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
  nav.deschide(t.nume || "Firmă", (corp) => meniuFirma(corp, nav, t));
}

// meniul de acțiuni pe o firmă (facturi activ; restul se activează pe rând)
function meniuFirma(corp, nav, t) {
  const optiuni = [
    { cheie: "facturi", titlu: "Facturi", desc: "Emite și vezi facturile firmei",
      bg: "#e9f0fe", fg: "#1d4ed8",
      icon: '<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 13h6M9 17h4"/>', activ: true },
    { cheie: "declaratii", titlu: "Declarații", desc: "D112, D300, D101 și restul",
      bg: "#e6f6ec", fg: "#16a34a",
      icon: '<path d="M9 13h6M9 17h4M9 9h1"/><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/>', activ: false },
    { cheie: "control", titlu: "Control fiscal", desc: "Semafor conformare pe firmă",
      bg: "#dff4f2", fg: "#0a807b",
      icon: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>', activ: false },
    { cheie: "salariati", titlu: "Salariați", desc: "Stat plată, fluturași, D112",
      bg: "#fdeef0", fg: "#a3344b",
      icon: '<circle cx="9" cy="7" r="3"/><path d="M2 21v-1a6 6 0 0 1 12 0v1"/><path d="M16 3.5a3 3 0 0 1 0 7M22 21v-1a6 6 0 0 0-4-5.7"/>', activ: true },
    { cheie: "bonuri", titlu: "Bonuri de verificat", desc: "Citite de AI \u2014 certifica si conteaza",
      bg: "#fdeef0", fg: "#a3344b",
      icon: '<path d="M9 11l3 3 8-8"/><path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>', activ: true },
    { cheie: "jurnal", titlu: "Registru jurnal", desc: "Notele contabile ale firmei",
      bg: "#eef0f3", fg: "#3a4250",
      icon: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>', activ: true },
    { cheie: "raportz", titlu: "Raport Z", desc: "Incasari zilnice \u2192 nota automata",
      bg: "#fbeedd", fg: "#92500a",
      icon: '<path d="M4 4h16M4 4l16 16M4 20h16"/>', activ: true },
    { cheie: "stocuri", titlu: "Stocuri", desc: "NIR, adaos, desc\u0103rcare gestiune",
      bg: "#fbeedd", fg: "#92500a",
      icon: '<path d="M21 8l-9-5-9 5v8l9 5 9-5V8z"/><path d="M3 8l9 5 9-5M12 13v8"/>', activ: true },
    { cheie: "balanta", titlu: "Balan\u021b\u0103 de verificare", desc: "PDF lunar, solduri si rulaje",
      bg: "#eef4ff", fg: "#1d4ed8",
      icon: '<path d="M12 3v18M3 7h18M6 7l-3 5h6l-3-5zM18 7l-3 5h6l-3-5z"/>', activ: true },
    { cheie: "bilant", titlu: "Bilan\u021b anual", desc: "S1005 micro / S1003 mici, validare ANAF",
      bg: "#eef4ff", fg: "#1d4ed8",
      icon: '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>', activ: true },
    { cheie: "casa", titlu: "Cas\u0103", desc: "Registru de cas\u0103, plafoane numerar",
      bg: "#e6f6ec", fg: "#16a34a",
      icon: '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M6 12h.01M18 12h.01"/>', activ: true },
    { cheie: "etransport", titlu: "e-Transport", desc: "Notificare UIT, XML pentru SPV",
      bg: "#fff7ed", fg: "#c2410c",
      icon: '<path d="M1 8h13v8H1zM14 11h4l3 3v2h-7z"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>', activ: true },
    { cheie: "operatiuni", titlu: "Operatiuni speciale", desc: "Leasing, marja, IC, sponsorizari si altele",
      bg: "#f3e8ff", fg: "#7c3aed",
      icon: '<path d="M12 2l2 4 4 .5-3 3 .8 4.5L12 12l-3.8 2 .8-4.5-3-3 4-.5z"/><path d="M5 18h14M5 21h14"/>', activ: true },
    { cheie: "rip", titlu: "Incasari/plati", desc: "Partida simpla PFA/II/IF, Fisa D212",
      bg: "#e6f6ec", fg: "#16a34a",
      icon: '<path d="M12 2v20M17 7H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>', activ: true },
    { cheie: "banca", titlu: "Banc\u0103", desc: "Import extras, propuneri contare",
      bg: "#e9f0fe", fg: "#1d4ed8",
      icon: '<path d="M3 21h18M4 18h16M6 18V9M10 18V9M14 18V9M18 18V9M2 9l10-6 10 6"/>', activ: true },
    { cheie: "verificari", titlu: "Verific\u0103ri", desc: "Echilibru, trezorerie, TVA",
      bg: "#eef4ff", fg: "#1d4ed8",
      icon: '<path d="M9 11l3 3 8-8"/><path d="M21 12v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h11"/>', activ: true },
    { cheie: "solicitari", titlu: "Solicitări client", desc: "Mesaje primite de la firma-client",
      bg: "#faece7", fg: "#993c1d",
      icon: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>', activ: true },
  ];

  corp.innerHTML = `
    <p class="pf-intro">CUI ${t.cui || "\u2014"}</p>
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

  const bFacturi = corp.querySelector("#fa-facturi");
  if (bFacturi) {
    bFacturi.addEventListener("click", () => {
      randeazaFacturi(corp, nav, t.id, { inapoi: () => meniuFirma(corp, nav, t) });
    });
  }
  const bSalariati = corp.querySelector("#fa-salariati");
  if (bSalariati && !bSalariati.disabled) {
    bSalariati.addEventListener("click", () => ecranSalariati(corp, nav, t));
  }
  const bBonuri = corp.querySelector("#fa-bonuri");
  if (bBonuri) {
    bBonuri.addEventListener("click", () => ecranBonuri(corp, nav, t));
  }
  const bJurnal = corp.querySelector("#fa-jurnal");
  if (bJurnal) {
    bJurnal.addEventListener("click", () => ecranJurnal(corp, nav, t));
  }
  const bZ = corp.querySelector("#fa-raportz");
  if (bZ) {
    bZ.addEventListener("click", () => ecranRaportZ(corp, nav, t));
  }
  const bBilant = corp.querySelector("#fa-bilant");
  if (bBilant) {
    bBilant.addEventListener("click", () => ecranBilant(corp, nav, t));
  }
  const bStocuri = corp.querySelector("#fa-stocuri");
  if (bStocuri) {
    bStocuri.addEventListener("click", () => ecranStocuri(corp, nav, t));
  }
  const bCasa = corp.querySelector("#fa-casa");
  if (bCasa) {
    bCasa.addEventListener("click", () => ecranCasa(corp, nav, t));
  }
  const bRip = corp.querySelector("#fa-rip");
  if (bRip) bRip.addEventListener("click", () => ecranRip(corp, nav, t));
  const bOperatiuni = corp.querySelector("#fa-operatiuni");
  if (bOperatiuni) bOperatiuni.addEventListener("click", () => ecranOperatiuni(corp, nav, t));
  const bEtransport = corp.querySelector("#fa-etransport");
  if (bEtransport) bEtransport.addEventListener("click", () => ecranEtransport(corp, nav, t));
  const bBalanta = corp.querySelector("#fa-balanta");
  if (bBalanta) bBalanta.addEventListener("click", () => ecranBalanta(corp, nav, t));
  const bBanca = corp.querySelector("#fa-banca");
  if (bBanca) {
    bBanca.addEventListener("click", () => ecranBanca(corp, nav, t));
  }
  const bVerif = corp.querySelector("#fa-verificari");
  if (bVerif) {
    bVerif.addEventListener("click", () => ecranVerificari(corp, nav, t));
  }
  const bSolicitari = corp.querySelector("#fa-solicitari");
  if (bSolicitari) {
    bSolicitari.addEventListener("click", () => {
      ecranSolicitariCabinet(corp, nav, t);
    });
  }
}

function fmtDataCab(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  const zz = String(d.getDate()).padStart(2, "0");
  const ll = String(d.getMonth() + 1).padStart(2, "0");
  return `${zz}/${ll}/${d.getFullYear()}`;
}

async function ecranSolicitariCabinet(corp, nav, t) {
  corp.innerHTML = `<p class="ecran-nota">Se incarca...</p>`;
  await randeazaSolicitariCabinet(corp, nav, t);
}

async function randeazaSolicitariCabinet(corp, nav, t) {
  let lista = [];
  try {
    const r = await api.get(`/tenants/${t.id}/solicitari`);
    lista = (r && r.solicitari) || [];
  } catch {}
  let firHtml = '<div class="mig-gol">Niciun mesaj inca.</div>';
  if (lista.length) {
    firHtml = lista.map((s) => {
      const cine = s.autor_rol === "cabinet" ? "Tu" : "Client";
      return `<div class="sol-rand sol-${s.autor_rol === "cabinet" ? "client" : "cabinet"}">
        <div class="sol-mesaj">${s.mesaj}</div>
        <div class="sol-meta">${cine} · ${fmtDataCab(s.creat_la)}</div>
      </div>`;
    }).join("");
  }
  corp.innerHTML = `
    <h2 class="pf-titlu">Solicitări — ${t.nume || ""}</h2>
    <p class="pf-intro">Mesaje de la firma-client.</p>
    <div class="sol-fir" id="sol-fir">${firHtml}</div>
    <div class="sol-trimite">
      <textarea id="sol-input" placeholder="Scrie un raspuns..." rows="3"></textarea>
      <button class="btn" id="sol-trimite-btn">Trimite</button>
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
        <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:${ok ? "#1d7a4d" : "#ff3b30"}"></span>
      </div>`;
    };
    corp.innerHTML = `
      <h2 class="pf-titlu">Verific\u0103ri \u00b7 ${t.nume || ""}</h2>
      <p class="pf-intro">Luna ${String(luna).padStart(2,"0")}/${an} \u00b7 ${r ? r.note : 0} note contabile
        <button class="btn-secundar" id="vf-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="btn-secundar" id="vf-next">luna \u2192</button></p>
      <div class="pf-lista">
        ${r ? rand("Echilibru balan\u021b\u0103", r.echilibru) : ""}
        ${r ? rand("Trezorerie (f\u0103r\u0103 solduri creditoare)", r.trezorerie) : ""}
        ${r ? `<div class="pf-frand"><div class="pf-frand-text"><div class="pf-frand-nume">TVA</div><div class="pf-frand-sub">${r.tva.rezultat === "de_plata" ? "de plat\u0103" : "de recuperat"}: ${r.tva.suma} lei (cont ${r.tva.cont})</div></div></div>` : ""}
        ${vs ? `<div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">Stocuri (contabil vs fi\u0219e CV)</div>
          <div class="pf-frand-sub">${vs.ok ? "in regula" : vs.conturi.filter(c=>!c.ok).map(c=>`cont ${c.cod || c.cont}: contabil ${c.sold_contabil} vs fi\u0219e ${c.valoare_fise_cv} (dif ${c.diferenta})`).join(" \u00b7 ")}</div>
        </div><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:${vs.ok ? "#1d7a4d" : "#ff3b30"}"></span></div>` : ""}
        ${intra ? `<div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">Intrastat (prag 1.000.000 lei/flux, an ${an})</div>
          <div class="pf-frand-sub">Introduceri: ${intra.introduceri ? intra.introduceri.cumulat + " lei (" + intra.introduceri.procent + "%)" + (intra.introduceri.status !== "sub_prag" ? " \u00b7 DEPASIT din luna " + intra.introduceri.luna_depasirii : "") : "-"} \u00b7 Expedieri: ${intra.expedieri ? intra.expedieri.cumulat + " lei (" + intra.expedieri.procent + "%)" + (intra.expedieri.status !== "sub_prag" ? " \u00b7 DEPASIT din luna " + intra.expedieri.luna_depasirii : "") : "-"}</div>
        </div><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:${(intra.introduceri && intra.introduceri.status !== "sub_prag") || (intra.expedieri && intra.expedieri.status !== "sub_prag") ? "#ff3b30" : "#1d7a4d"}"></span></div>` : ""}
        ${!r ? '<div class="mig-gol">Nu am putut rula verific\u0103rile.</div>' : ""}
      </div>`;
    corp.querySelector("#vf-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#vf-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
  };
  deseneaza();
}

// [salariati] Stat de plata lunar + fluturasi
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
            <div class="pf-frand-nume">${s.nume}</div>
            <div class="pf-frand-sub">brut ${s.brut.toFixed(2)} \u00b7 CAS ${s.cas.toFixed(2)} \u00b7 CASS ${s.cass.toFixed(2)} \u00b7 impozit ${s.impozit.toFixed(2)} \u00b7 <b>net ${s.net.toFixed(2)}</b> \u00b7 cost ${s.cost.toFixed(2)}</div>
          </div>
          <button class="btn" data-flut="${s.id}">Fluturas</button>
          <button class="btn btn-secundar" data-reges="${s.id}" style="margin-left:6px">REGES</button>
        </div>`).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">Stat de plat\u0103 \u00b7 ${t.nume || ""}</h2>
      <p class="pf-intro">Luna ${String(luna).padStart(2,"0")}/${an}
        <button class="btn btn-secundar" id="sp-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="btn btn-secundar" id="sp-next">luna \u2192</button>
        <button class="btn btn-secundar" id="sp-reges-cfg" style="margin-left:12px">Chei REGES</button>
        <button class="btn btn-secundar" id="sp-reges-poll">R\u0103spunsuri REGES</button></p>
      <div id="sp-reges-zona"></div>
      <div class="pf-lista">${randuri}</div>`;
    corp.querySelector("#sp-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#sp-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    const zonaReges = corp.querySelector("#sp-reges-zona");
    corp.querySelector("#sp-reges-cfg").addEventListener("click", () => {
      zonaReges.innerHTML = `<div class="pf-frand" style="display:block;margin:10px 0">
        <div class="pf-frand-nume" style="margin-bottom:8px">Chei API REGES (din aplicatia REGES Angajator)</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;max-width:700px">
          <label>Username<br><input type="text" id="rg-user" class="mig-text"></label>
          <label>Parola<br><input type="password" id="rg-pass" class="mig-text"></label>
          <label>Mediu<br><select id="rg-mediu" class="mig-text"><option value="test">Test</option><option value="prod">Productie</option></select></label>
        </div>
        <p style="margin-top:10px"><button class="btn" id="rg-salveaza">Salveaz\u0103</button></p>
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
          <div class="pf-frand-sub">${msgs.length ? msgs.map((m2) => `${m2.data || ""} \u00b7 ${m2.status || m2.tip || ""} \u00b7 ${m2.mesaj || m2.detalii || JSON.stringify(m2)}`).join("<br>") : "niciun raspuns nou"}</div></div>`;
      } catch (e) { zonaReges.innerHTML = `<div class="mig-gol">${e.mesaj || "eroare"}</div>`; }
    });
    corp.querySelectorAll("[data-reges]").forEach((b) => b.addEventListener("click", async () => {
      const adresa = prompt("Adresa salariatului (obligatorie REGES):");
      if (!adresa) return;
      try {
        const r = await api.post(`/tenants/${t.id}/reges-trimite-salariat`, { salariat_id: parseInt(b.dataset.reges), adresa });
        zonaReges.innerHTML = `<p class="pf-intro">Trimis in REGES${r.referinta ? " \u00b7 ref " + r.referinta : ""}. Verifica R\u0103spunsuri REGES.</p>`;
      } catch (e) { zonaReges.innerHTML = `<div class="mig-gol">${e.mesaj || "eroare"}</div>`; }
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
        } catch { alert("Nu am putut genera fluturasul."); }
      });
    });
  };
  deseneaza();
}




// [stocuri-cv] Fise de magazie (cantitativ-valoric)
async function sectiuneaCV(corp, t, zonaM) {
  const escV = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const zona = corp.querySelector("#cv-zona");
  let arts = [];
  try { const r = await api.get(`/tenants/${t.id}/stocuri/articole`); arts = r.articole || []; } catch {}
  const azi = new Date().toISOString().slice(0, 10);
  zona.innerHTML = `
    <div class="pf-frand" style="display:block;margin-bottom:14px">
      <div class="pf-frand-nume" style="margin-bottom:8px">Fi\u0219e de magazie (cantitativ-valoric, CMP)</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
        <select id="cv-art" class="mig-text" style="min-width:200px">
          <option value="">\u2014 articol nou \u2014</option>
          ${arts.map((a) => `<option value="${a.id}">${escV(a.denumire)} \u00b7 stoc ${a.stoc} ${escV(a.um)}${a.cmp ? " \u00b7 CMP " + a.cmp : ""}</option>`).join("")}
        </select>
        <input type="text" id="cv-den" class="mig-text" placeholder="denumire (articol nou)" style="flex:1;min-width:160px">
        <input type="date" id="cv-data" class="mig-text" value="${azi}">
        <input type="number" step="0.001" id="cv-cant" class="mig-text" placeholder="cant." style="width:90px">
        <input type="number" step="0.0001" id="cv-pret" class="mig-text" placeholder="pret unitar (la intrare)" style="width:170px">
        <input type="text" id="cv-doc" class="mig-text" placeholder="document" style="width:130px">
      </div>
      <p>
        <button class="btn" id="cv-intrare">Intrare</button>
        <button class="btn" id="cv-iesire" style="margin-left:6px">Ie\u0219ire la CMP (nota ciorn\u0103)</button>
        <button class="btn btn-secundar" id="cv-fisa" style="margin-left:6px">Vezi fi\u0219a</button>
      </p>
      <div style="margin-top:10px">
        <button class="btn btn-secundar" id="cv-inv">Inventar (stoc faptic)</button>
        <div id="cv-inv-zona" style="margin-top:8px"></div>
      </div>
      <div id="cv-fisa-zona"></div>
      <div class="pf-card" style="margin-top:14px">
        <h3 class="pf-subtitlu">Re\u021bete (HoReCa)</h3>
        <div id="rt-lista"></div>
        <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;align-items:flex-end">
          <label>Denumire<br><input class="mig-text" id="rt-den" placeholder="ex. Meniu zilei"></label>
          <label>Pre\u021b f\u0103r\u0103 TVA<br><input class="mig-text" type="number" step="0.01" id="rt-pret" style="width:110px"></label>
          <button class="btn btn-secundar" id="rt-plus">+ ingredient</button>
          <button class="btn" id="rt-salveaza">Salveaz\u0103 re\u021beta</button>
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
      zonaM.innerHTML = `<p class="pf-intro">Intrare inregistrata \u00b7 ${r.valoare} lei.</p>`;
      sectiuneaCV(corp, t, zonaM);
    } catch (e) { zonaM.innerHTML = `<div class="mig-gol">${escV(e.mesaj || "Eroare")}</div>`; }
  });
  zona.querySelector("#cv-iesire").addEventListener("click", async () => {
    if (!val("#cv-art")) { zonaM.innerHTML = `<div class="mig-gol">Alege articolul pentru iesire.</div>`; return; }
    try {
      const r = await api.post(`/tenants/${t.id}/stocuri/iesire`, {
        articol_id: parseInt(val("#cv-art")), data: val("#cv-data"),
        cantitate: parseFloat(val("#cv-cant")) || 0, document: val("#cv-doc") || null });
      zonaM.innerHTML = `<p class="pf-intro">Iesire la CMP ${r.cmp} \u00b7 ${r.valoare} lei \u00b7 nota ${escV(r.nota)} (ciorna).</p>`;
      sectiuneaCV(corp, t, zonaM);
    } catch (e) { zonaM.innerHTML = `<div class="mig-gol">${escV(e.mesaj || "Eroare")}</div>`; }
  });


  // [retete_v1] Retete HoReCa: CRUD + descarcare pe reteta + food cost
  const rtLista = zona.querySelector("#rt-lista");
  const rtIng = zona.querySelector("#rt-ingrediente");
  let rtLinii = [];
  const rtDeseneazaIng = () => {
    rtIng.innerHTML = rtLinii.map((l, i) => `
      <div style="display:flex;gap:6px;margin-top:6px;align-items:center">
        <select class="mig-text rt-art" data-i="${i}">${arts.map((a) =>
          `<option value="${a.id}" ${a.id == l.articol_id ? "selected" : ""}>${escV(a.denumire)} \u00b7 CMP ${a.cmp}</option>`).join("")}</select>
        <input class="mig-text rt-cant" data-i="${i}" type="number" step="0.001" value="${l.cantitate || ""}" placeholder="cant./por\u021bie" style="width:120px">
        <button class="btn btn-sters rt-scoate" data-i="${i}">\u2212</button>
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
              <div class="pf-frand-nume">${escV(r.denumire)} \u00b7 ${r.pret_fara_tva} lei</div>
              <div class="pf-frand-sub">cost/por\u021bie ${fc.cost_portie} \u00b7 food cost ${pct} \u00b7 ${(r.linii || []).map((l) => `${escV(l.denumire)} ${l.cantitate}${escV(l.um || "")}`).join(", ")}</div>
            </div>
            <input class="mig-text rt-portii" data-id="${r.id}" type="number" placeholder="por\u021bii" style="width:80px">
            <button class="btn rt-desc" data-id="${r.id}">Descarc\u0103 (ciorn\u0103)</button>
            <button class="btn btn-sters rt-del" data-id="${r.id}">\u0218terge</button>
          </div>`;
        }).join("");
    rtLista.querySelectorAll(".rt-desc").forEach((b) => b.addEventListener("click", async (e) => {
      const id = e.target.dataset.id;
      const p = rtLista.querySelector(`.rt-portii[data-id="${id}"]`).value;
      if (!p) { zonaM.innerHTML = `<div class="mig-gol">Completeaz\u0103 num\u0103rul de por\u021bii.</div>`; return; }
      try {
        const r = await api.post(`/tenants/${t.id}/retete/descarca`, { reteta_id: parseInt(id), portii: parseFloat(p), data: val("#cv-data") || new Date().toISOString().slice(0, 10) });
        zonaM.innerHTML = `<p class="pf-intro">Consum \u00eenregistrat (ciorn\u0103 #${r.inregistrare_id}) \u00b7 cost total ${r.cost_total} lei.</p>`;
        sectiuneaCV(corp, t, zonaM); rtIncarca();
      } catch (er) { zonaM.innerHTML = `<div class="mig-gol">${escV(er.mesaj || "Eroare")}</div>`; }
    }));
    rtLista.querySelectorAll(".rt-del").forEach((b) => b.addEventListener("click", async (e) => {
      try { await api.del(`/tenants/${t.id}/retete/${e.target.dataset.id}`); rtIncarca(); } catch {}
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
    } catch (er) { zonaM.innerHTML = `<div class="mig-gol">${escV(er.mesaj || "Eroare")}</div>`; }
  });
  rtIncarca();

  zona.querySelector("#cv-inv").addEventListener("click", () => {
    const z = zona.querySelector("#cv-inv-zona");
    z.innerHTML = `<div class="pf-lista">${arts.map((a) => `
      <div class="pf-frand"><div class="pf-frand-text">
        <div class="pf-frand-nume">${escV(a.denumire)} \u00b7 scriptic ${a.stoc} ${escV(a.um)}</div>
      </div>
      <input type="number" step="0.001" class="mig-text cvi-faptic" data-aid="${a.id}" placeholder="faptic" style="width:110px"></div>`).join("")}
      <p style="margin-top:8px"><button class="btn" id="cvi-salveaza">Salveaz\u0103 inventarul (note ciorne)</button></p>`;
    z.querySelector("#cvi-salveaza").addEventListener("click", async () => {
      const linii = [...z.querySelectorAll(".cvi-faptic")]
        .filter((i) => i.value !== "")
        .map((i) => ({ articol_id: parseInt(i.dataset.aid), faptic: parseFloat(i.value) }));
      if (!linii.length) { zonaM.innerHTML = `<div class="mig-gol">Completeaza stocul faptic la cel putin un articol.</div>`; return; }
      try {
        const r = await api.post(`/tenants/${t.id}/stocuri/inventar`,
          { data: val("#cv-data"), linii });
        zonaM.innerHTML = `<p class="pf-intro">${(r.rezultate || []).map((x) =>
          x.eroare ? `${escV(x.denumire || x.articol_id)}: ${escV(x.eroare)}`
          : x.diferenta === "0" ? `${escV(x.denumire)}: fara diferenta`
          : `${escV(x.denumire)}: ${x.diferenta > 0 ? "plus" : "minus"} ${x.diferenta} \u00b7 ${x.valoare} lei \u00b7 nota ${escV(x.nota)} (ciorna)`).join("<br>")}</p>`;
        sectiuneaCV(corp, t, zonaM);
      } catch (e) { zonaM.innerHTML = `<div class="mig-gol">${escV(e.mesaj || "Eroare")}</div>`; }
    });
  });
  zona.querySelector("#cv-fisa").addEventListener("click", async () => {
    if (!val("#cv-art")) return;
    try {
      const r = await api.get(`/tenants/${t.id}/stocuri/articole/${val("#cv-art")}/fisa`);
      zona.querySelector("#cv-fisa-zona").innerHTML = `
        <div class="pf-frand-nume" style="margin:8px 0">Fisa: ${escV(r.articol.denumire)}</div>
        <div class="pf-lista">${r.linii.map((l) => `
          <div class="pf-frand"><div class="pf-frand-text">
            <div class="pf-frand-nume">${escV(l.data)} \u00b7 ${l.tip === "intrare" ? "+" : "\u2212"}${l.cantitate} \u00b7 ${l.valoare} lei${l.pret_unitar ? " \u00b7 pret " + l.pret_unitar : ""}</div>
            <div class="pf-frand-sub">sold ${l.sold_cantitate} \u00b7 ${l.sold_valoare} lei${l.cmp ? " \u00b7 CMP " + l.cmp : ""}${l.document ? " \u00b7 " + escV(l.document) : ""}</div>
          </div></div>`).join("") || '<div class="mig-gol">Fara miscari.</div>'}</div>`;
    } catch { zona.querySelector("#cv-fisa-zona").innerHTML = `<div class="mig-gol">Nu am putut incarca fisa.</div>`; }
  });
}

// [stocuri] NIR + descarcare gestiune (global-valorica)

async function ecranBilant(corp, nav, t) {
  const escS = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  {
    corp.innerHTML = `
      <h2 class="pf-titlu">Bilan\u021b anual \u00b7 ${escS(t.nume || "")}</h2>
      <p class="pf-intro">Genereaz\u0103 \u0219i valideaz\u0103 situa\u021biile financiare (validator ANAF pe server).</p>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <label>An<br><input type="number" id="bl-an" class="mig-text" value="${new Date().getFullYear() - 1}" style="width:90px"></label>
        <label>Tip<br><select id="bl-tip" class="mig-text">
          <option value="s1005">S1005 \u00b7 microentit\u0103\u021bi</option>
          <option value="s1003">S1003 \u00b7 entit\u0103\u021bi mici</option>
        </select></label>
        <button class="btn" id="bl-val">Valideaz\u0103 (ANAF)</button>
        <button class="btn btn-secundar" id="bl-xml">Descarc\u0103 XML</button>
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
          (r.erori ? `<pre style="white-space:pre-wrap;font-size:12px;background:#f6f7f9;padding:8px;border-radius:8px">${escS(r.erori)}</pre>` : "") +
          (r.avertismente && r.avertismente.length
            ? `<p class="pf-intro">${r.avertismente.map(escS).join("<br>")}</p>` : "");
      } catch (e) { rez.innerHTML = `<div class="mig-gol">${escS(e.mesaj || "Eroare")}</div>`; }
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
          rez.innerHTML = `<p class="pf-intro">${r.avertismente.map(escS).join("<br>")}</p>`;
        }
      } catch (e) { rez.innerHTML = `<div class="mig-gol">${escS(e.mesaj || "Eroare")}</div>`; }
    });
  }
}

async function ecranStocuri(corp, nav, t) {
  const escS = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  let liniiNir = [];

  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se incarca...</p>`;
    let nirs = [];
    try { const r = await api.get(`/tenants/${t.id}/stocuri/nir?an=${an}&luna=${luna}`); nirs = r.nir || []; } catch {}
    const randuri = !nirs.length
      ? `<div class="mig-gol">Niciun NIR in luna asta.</div>`
      : nirs.map((n) => `
        <div class="pf-frand">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">NIR ${escS(n.numar)} \u00b7 ${escS(n.data)} \u00b7 ${escS(n.furnizor || "")}</div>
            <div class="pf-frand-sub">cost ${n.cost_total} \u00b7 adaos ${n.adaos_total} \u00b7 TVA neex. ${n.tva_neexigibila} \u00b7 raft ${n.valoare_vanzare} lei</div>
          </div>
        </div>`).join("");
    const randLinie = (l, i) => `
      <div style="display:flex;gap:8px;margin-bottom:6px;flex-wrap:wrap" data-i="${i}">
        <input type="text" class="mig-text sn-den" placeholder="denumire" value="${escS(l.denumire || "")}" style="flex:2;min-width:160px">
        <input type="number" step="0.001" class="mig-text sn-cant" placeholder="cant." value="${l.cantitate || ""}" style="width:90px">
        <input type="number" step="0.0001" class="mig-text sn-pa" placeholder="pret achizitie" value="${l.pret_achizitie || ""}" style="width:120px">
        <input type="number" step="0.0001" class="mig-text sn-pv" placeholder="pret raft (cu TVA)" value="${l.pret_vanzare || ""}" style="width:140px">
        <select class="mig-text sn-tva" style="width:80px">${[21, 11].map((c) => `<option value="${c}"${(l.cota_tva || 21) == c ? " selected" : ""}>${c}%</option>`).join("")}</select>
        <button class="btn btn-secundar sn-scoate">\u2212</button>
      </div>`;
    corp.innerHTML = `
      <h2 class="pf-titlu">Stocuri \u00b7 ${escS(t.nume || "")}</h2>
      <p class="pf-intro">Luna ${String(luna).padStart(2, "0")}/${an}
        <button class="btn btn-secundar" id="s-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="btn btn-secundar" id="s-next">luna \u2192</button>
        <button class="btn" id="s-desc" style="margin-left:12px">Descarc\u0103 gestiunea lunii</button></p>
      <div id="s-mesaj"></div>
      <div class="pf-frand" style="display:block;margin-bottom:14px">
        <div class="pf-frand-nume" style="margin-bottom:8px">NIR nou</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
          <input type="text" id="sn-numar" class="mig-text" placeholder="numar NIR" style="width:120px">
          <input type="date" id="sn-data" class="mig-text" value="${new Date().toISOString().slice(0, 10)}">
          <input type="text" id="sn-furn" class="mig-text" placeholder="furnizor" style="flex:1;min-width:160px">
          <input type="text" id="sn-cui" class="mig-text" placeholder="CUI" style="width:120px">
        </div>
        <div id="sn-linii">${liniiNir.map(randLinie).join("")}</div>
        <p><button class="btn btn-secundar" id="sn-plus">+ articol</button>
           <button class="btn" id="sn-salveaza" style="margin-left:6px">Salveaz\u0103 NIR (note ciorne)</button></p>
      </div>
      <div id="cv-zona"></div>
      <div class="pf-lista">${randuri}</div>`;
    const zonaM = corp.querySelector("#s-mesaj");
    const zonaL = corp.querySelector("#sn-linii");
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
      if (!linii.length) { zonaM.innerHTML = `<div class="mig-gol">Adauga cel putin un articol.</div>`; return; }
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
      } catch (e) { zonaM.innerHTML = `<div class="mig-gol">${escS(e.mesaj || "Eroare")}</div>`; }
    });
    corp.querySelector("#s-desc").addEventListener("click", async () => {
      if (!confirm(`Descarci gestiunea pe ${String(luna).padStart(2, "0")}/${an}? Se calculeaza din notele VALIDATE.`)) return;
      try {
        const r = await api.post(`/tenants/${t.id}/stocuri/descarcare?an=${an}&luna=${luna}`, {});
        zonaM.innerHTML = r.mesaj
          ? `<div class="mig-gol">${escS(r.mesaj)}</div>`
          : `<p class="pf-intro">K=${r.k} \u00b7 CMV ${r.cmv} \u00b7 adaos ${r.adaos} \u00b7 TVA ${r.tva} \u00b7 total 371: ${r.total_371} lei \u00b7 ${r.inregistrari.length} note ciorne.</p>`;
      } catch (e) { zonaM.innerHTML = `<div class="mig-gol">${escS(e.mesaj || "Eroare")}</div>`; }
    });
    sectiuneaCV(corp, t, zonaM);
  };
  liniiNir = [{}];
  deseneaza();
}

// [casa] Registru de casa
async function ecranCasa(corp, nav, t) {
  const escC = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const CATEGORII = [
    ["incasare_client", "Incasare client (5311=4111)"],
    ["plata_furnizor", "Plata furnizor (401=5311)"],
    ["ridicare_banca", "Ridicare de la banca (5311=581)"],
    ["depunere_banca", "Depunere la banca (581=5311)"],
    ["avans_decontare", "Avans spre decontare (542=5311)"],
  ];
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se incarca...</p>`;
    let reg = { operatiuni: [], sold_final: "0", avertismente: [] };
    try { reg = await api.get(`/tenants/${t.id}/casa/registru?an=${an}&luna=${luna}`); } catch {}
    const ziAzi = new Date().toISOString().slice(0, 10);
    const avert = (reg.avertismente || []).map((a) =>
      `<div class="mig-gol" style="margin-bottom:6px">${escC(a.mesaj || a.cod || "")}${a.temei ? " \u00b7 " + escC(a.temei) : ""}</div>`).join("");
    const randuri = !(reg.operatiuni || []).length
      ? `<div class="mig-gol">Nicio operatiune in luna asta.</div>`
      : reg.operatiuni.map((o) => `
        <div class="pf-frand">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">${escC(o.data)} \u00b7 ${o.tip === "plata" ? "\u2212" : "+"}${o.suma} lei \u00b7 sold ${o.sold} lei</div>
            <div class="pf-frand-sub">${escC(o.partener || "")}${o.document ? " \u00b7 doc " + escC(o.document) : ""} \u00b7 ${escC(o.categorie)}</div>
          </div>
          <button class="btn btn-secundar" data-del="${o.id}">\u0218terge</button>
        </div>`).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">Cas\u0103 \u00b7 ${escC(t.nume || "")}</h2>
      <p class="pf-intro">Luna ${String(luna).padStart(2, "0")}/${an} \u00b7 sold final <b>${reg.sold_final} lei</b>
        <button class="btn btn-secundar" id="c-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="btn btn-secundar" id="c-next">luna \u2192</button></p>
      ${avert}
      <div class="pf-frand" style="display:block;margin-bottom:14px">
        <div class="pf-frand-nume" style="margin-bottom:8px">Dispozitie noua</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;max-width:900px">
          <label>Data<br><input type="date" id="c-data" class="mig-text" value="${ziAzi}"></label>
          <label>Tip<br><select id="c-cat" class="mig-text">${CATEGORII.map(([v, l]) => `<option value="${v}">${l}</option>`).join("")}</select></label>
          <label>Suma<br><input type="number" step="0.01" id="c-suma" class="mig-text" value="0"></label>
          <label>Partener<br><input type="text" id="c-part" class="mig-text"></label>
          <label>CUI<br><input type="text" id="c-cui" class="mig-text"></label>
          <label>Document<br><input type="text" id="c-doc" class="mig-text"></label>
        </div>
        <p style="margin-top:10px"><button class="btn" id="c-adauga">Adauga (nota ciorna)</button></p>
        <div id="c-mesaj"></div>
      </div>
      <div class="pf-lista">${randuri}</div>`;
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
        zonaM.innerHTML = `<p class="pf-intro">Nota ${escC(r.nota)} creata ca ciorna.${av ? ` <b style="color:#c9961f">${av} avertisment(e) plafon.</b>` : ""}</p>`;
        deseneaza();
      } catch (e) { zonaM.innerHTML = `<div class="mig-gol">${escC(e.mesaj || "Eroare")}</div>`; }
    });
    corp.querySelectorAll("[data-del]").forEach((b) => b.addEventListener("click", async () => {
      if (!confirm("Stergi operatiunea si ciorna legata?")) return;
      try { await api.del(`/tenants/${t.id}/casa/operatiuni/${b.dataset.del}`); deseneaza(); }
      catch (e) { alert(e.mesaj || "Eroare"); }
    }));
  };
  deseneaza();
}

// [banca] Import extras + reconciliere pe facturi
async function ecranBanca(corp, nav, t) {
  const escB = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const CUL = { verde: "#1d7a4d", galben: "#c9961f", rosu: "#ff3b30", gri: "#3a4250" };
  corp.innerHTML = `
    <h2 class="pf-titlu">Banc\u0103 \u00b7 ${escB(t.nume || "")}</h2>
    <p class="pf-intro">Incarca extrasul (.xls, .xlsx, .csv) \u2014 liniile se potrivesc automat pe facturi dupa CUI.</p>
    <input type="file" id="bk-fisier" accept=".xls,.xlsx,.csv" style="margin-bottom:16px">
    <div id="bk-mesaj"></div>
    <div id="bk-lista"></div>`;
  const zonaMesaj = corp.querySelector("#bk-mesaj");
  const zonaLista = corp.querySelector("#bk-lista");

  function badge(l) {
    if (l.status === "ignorat") return `<span style="color:#3a4250">Ignorată</span> <button class="btn-link bk-undo" data-id="${l.id}">readu</button>`;
    if (l.status === "contat") return `<span style="color:${CUL.gri};font-weight:600">Contat \u2713</span>`;
    const m = (l.alocari || {}).status_match;
    if (m === "verde") return `<span style="color:${CUL.verde};font-weight:600">\u25cf Match exact</span>`;
    if (m === "galben") return `<span style="color:${CUL.galben};font-weight:600">\u25cf Par\u021bial</span>`;
    return `<span style="color:${CUL.rosu};font-weight:600">\u25cf F\u0103r\u0103 match</span>`;
  }

  function randAlocari(l) {
    const al = ((l.alocari || {}).alocari || []);
    if (!al.length) return "";
    return `<div class="pf-frand-sub">${al.map((a) => {
      const f = a.factura || {};
      return `${escB(f.serie || "")}${escB(f.numar || "#" + a.factura_id)} \u00b7 ${escB(f.tert || "")} \u00b7 ${a.suma} lei`;
    }).join("<br>")}</div>`;
  }

  function randeaza(linii) {
    if (!linii.length) { zonaLista.innerHTML = `<div class="mig-gol">Nicio linie de extras. Incarca un fisier.</div>`; return; }
    zonaLista.innerHTML = `<div class="pf-lista">${linii.map((l) => `
      <div class="pf-frand">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${escB(l.data)} \u00b7 ${l.tip === "plata" ? "\u2212" : "+"}${l.suma} lei${l.cui_detectat ? " \u00b7 CUI " + escB(l.cui_detectat) : ""} \u00b7 ${badge(l)}</div>
          <div class="pf-frand-sub">${escB((l.descriere || "").slice(0, 90))}${(l.alocari || {}).motiv ? " \u00b7 " + escB(l.alocari.motiv) : ""}</div>
          ${randAlocari(l)}
        </div>
        <div>
          ${l.status === "potrivit" ? `<button class="btn" data-cont="${l.id}">Conteaz\u0103</button>` : ""}${l.status === "nou" && l.nota_propusa && l.nota_propusa.debit ? `<button class="btn" data-cont="${l.id}">Conteaz\u0103 ${l.nota_propusa.debit}=${l.nota_propusa.credit}</button>` : ""}
          ${l.status !== "contat" && l.status !== "ignorat" ? `<button class="btn" data-alege="${l.id}" style="margin-left:6px">Alege facturile</button>` : ""}${l.status !== "contat" && l.status !== "ignorat" ? `<button class="btn btn-secundar" data-ign="${l.id}" style="margin-left:6px">Ignor\u0103</button>` : ""}
        </div>
      </div>`).join("")}</div>`;
    zonaLista.querySelectorAll("[data-cont]").forEach((b) =>
      b.addEventListener("click", () => conteaza(parseInt(b.dataset.cont), null)));
    zonaLista.querySelectorAll("[data-ign]").forEach((b) =>
      b.addEventListener("click", async () => {
        try { await api.post(`/tenants/${t.id}/banca/reconciliere/${b.dataset.ign}/ignora`, {}); incarca(); }
        catch (e) { zonaMesaj.innerHTML = `<div class="mig-gol">${e.mesaj || "Eroare"}</div>`; }
      }));
    zonaLista.querySelectorAll(".bk-undo").forEach((b) =>
      b.addEventListener("click", async () => {
        try { await api.post(`/tenants/${t.id}/banca/reconciliere/${b.dataset.id}/reactiveaza`, {}); incarca(); }
        catch (e) { zonaMesaj.innerHTML = `<div class="mig-gol">${e.mesaj || "Eroare"}</div>`; }
      }));
    zonaLista.querySelectorAll("[data-alege]").forEach((b) =>
      b.addEventListener("click", () => picker(linii.find((x) => x.id === parseInt(b.dataset.alege)))));
  }

  async function incarca() {
    try {
      const r = await api.get(`/tenants/${t.id}/banca/reconciliere`);
      randeaza(r.linii || []);
    } catch { zonaLista.innerHTML = `<div class="mig-gol">Nu am putut incarca liniile.</div>`; }
  }

  async function conteaza(id, alocari) {
    zonaMesaj.innerHTML = "";
    try {
      const r = await api.post(`/tenants/${t.id}/banca/reconciliere/${id}/conteaza`, alocari ? { alocari } : {});
      zonaMesaj.innerHTML = `<p class="pf-intro">Nota ${escB(r.nota || "")} \u2014 ${(r.inregistrari || []).length} inregistrari create.</p>`;
      incarca();
    } catch (e) { zonaMesaj.innerHTML = `<div class="mig-gol">${escB(e.mesaj || "Eroare la contare")}</div>`; }
  }

  async function picker(l) {
    if (!l) return;
    zonaMesaj.innerHTML = `<p class="ecran-nota">Se incarca facturile deschise...</p>`;
    let facturi = [];
    try {
      const r = await api.get(`/tenants/${t.id}/banca/reconciliere/facturi-deschise`);
      facturi = (r.facturi || []).filter((f) => f.directie === (l.tip === "incasare" ? "emisa" : "primita"));
    } catch { zonaMesaj.innerHTML = `<div class="mig-gol">Nu am putut incarca facturile.</div>`; return; }
    if (!facturi.length) { zonaMesaj.innerHTML = `<div class="mig-gol">Nicio factura deschisa pe aceasta directie.</div>`; return; }
    zonaMesaj.innerHTML = `
      <div class="pf-frand" style="display:block">
        <div class="pf-frand-nume">Alege facturile pentru linia din ${escB(l.data)} \u00b7 ${l.suma} lei</div>
        <div class="pf-lista" style="margin-top:8px">${facturi.map((f) => `
          <label class="pf-frand" style="cursor:pointer">
            <input type="checkbox" data-fid="${f.id}" data-sold="${f.sold}" style="margin-right:10px">
            <div class="pf-frand-text">
              <div class="pf-frand-nume">${escB(f.serie || "")}${escB(f.numar)} \u00b7 ${escB(f.tert_nume || "")}</div>
              <div class="pf-frand-sub">${escB(f.data_emitere)} \u00b7 sold ${f.sold} lei \u00b7 CUI ${escB(f.tert_cui || "")}</div>
            </div>
          </label>`).join("")}</div>
        <p style="margin-top:10px">
          <button class="btn" id="bk-pk-ok">Conteaz\u0103 selectate</button>
          <button class="btn" id="bk-pk-nu" style="margin-left:6px">Renun\u021b\u0103</button>
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
    <h2 class="pf-titlu">Raport Z \u00b7 ${t.nume || ""}</h2>
    <p class="pf-intro">Totaluri cu TVA inclus. Numerar + card = total.</p>
    <p><label class="btn btn-secundar" style="cursor:pointer">Import fisier AMEF (p7b/XML)
      <input type="file" id="z-amef" accept=".p7b,.xml" style="display:none"></label></p>
    <div id="z-amef-msg"></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:480px">
      <label>Data<br><input type="date" id="z-data" value="${azi}" class="mig-text"></label>
      <span></span>
      <label>Total 11% (mancare)<br><input type="number" step="0.01" id="z-11" class="mig-text" value="0"></label>
      <label>Total 21% (alcool, sucuri)<br><input type="number" step="0.01" id="z-21" class="mig-text" value="0"></label>
      <label>Numerar<br><input type="number" step="0.01" id="z-num" class="mig-text" value="0"></label>
      <label>Card<br><input type="number" step="0.01" id="z-card" class="mig-text" value="0"></label>
    </div>
    <div id="z-rezultat" style="margin-top:16px"></div>
    <p style="margin-top:16px"><button class="btn" id="z-salveaza">Genereaza nota</button></p>`;
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
        zona.innerHTML = `<p class="pf-intro">Importat: Z din ${r.data}, total ${r.total} (numerar ${r.numerar}, card ${r.card_altele}), TVA ${r.tva_total}. Nota <b>ciorna</b> #${r.inregistrare_id} - verifica cu Z-ul tiparit.</p>`;
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
        <div class="pf-frand-sub">TVA 11%: ${r.tva_11.toFixed(2)} \u00b7 TVA 21%: ${r.tva_21.toFixed(2)} \u00b7 baze: ${r.baza_11.toFixed(2)} / ${r.baza_21.toFixed(2)}</div>
      </div><span class="pf-frand-ok">\u2713</span></div>`;
      // [z_desc_v1] propune descarcarea gestiunii GV a lunii dupa nota Z
      const dz = new Date(corp.querySelector("#z-data").value || new Date());
      const anz = dz.getFullYear(), lz = dz.getMonth() + 1;
      const zb = document.createElement("p");
      zb.innerHTML = `<button class="btn btn-secundar" id="z-desc-gv">Descarc\u0103 gestiunea GV ${String(lz).padStart(2,"0")}/${anz} (not\u0103 ciorn\u0103)</button>`;
      zona.appendChild(zb);
      zb.querySelector("#z-desc-gv").addEventListener("click", async () => {
        try {
          const rd = await api.post(`/tenants/${t.id}/stocuri/descarcare?an=${anz}&luna=${lz}`, {});
          zb.innerHTML = `<span class="pf-intro">Desc\u0103rcare GV \u00eenregistrat\u0103 (ciorn\u0103): 607 = ${rd.cmv ?? "?"} lei (K=${rd.k ?? "?"}).</span>`;
        } catch (e2) { zb.innerHTML = `<span class="pf-intro">${(e2.mesaj || "Eroare la desc\u0103rcare")}</span>`; }
      });
        } catch (e) { zona.innerHTML = `<div class="mig-gol">${e.mesaj || "Eroare"}</div>`; }
  });
}


// [jurnal] Registru jurnal lunar
async function ecranJurnal(corp, nav, t) {
  const escJ = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  let inEditare = null; // id-ul notei deschise in editor

  const badge = (n) => n.status === "ciorna"
    ? `<span style="color:#c9961f;font-weight:600">\u25cf Ciorn\u0103</span>`
    : `<span style="color:#1d7a4d;font-weight:600">\u25cf Validat\u0103</span>`;

  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se incarca...</p>`;
    let note = [];
    try {
      const r = await api.get(`/tenants/${t.id}/jurnal?an=${an}&luna=${luna}`);
      note = (r && r.note) || [];
    } catch {}
    const rand = (n) => {
      if (inEditare === n.id) return editor(n);
      const butoane = n.status === "ciorna" ? `
        <button class="btn" data-val="${n.id}">Valideaz\u0103</button>
        <button class="btn btn-secundar" data-edit="${n.id}" style="margin-left:6px">Editeaz\u0103</button>
        <button class="btn btn-secundar" data-del="${n.id}" style="margin-left:6px">\u0218terge</button>` : "";
      return `
        <div class="pf-frand">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">${escJ(n.data)} \u00b7 ${escJ(n.descriere || n.numar || "#" + n.id)} \u00b7 ${badge(n)}</div>
            <div class="pf-frand-sub">${n.linii.map((l) => `${escJ(l.debit)} = ${escJ(l.credit)} \u00b7 ${l.suma.toFixed(2)}`).join("<br>")}${n.sursa ? " \u00b7 sursa: " + escJ(n.sursa) : ""}</div>
          </div>
          <div>${butoane}</div>
        </div>`;
    };
    const editor = (n) => `
      <div class="pf-frand" style="display:block;border:1px solid #c9961f">
        <div class="pf-frand-nume" style="margin-bottom:8px">Editare nota #${n.id} \u00b7 ${escJ(n.data)}</div>${n.factura_id ? `<div class="mig-gol" style="margin-bottom:8px">Aten\u021bie: nota e legat\u0103 de factura #${n.factura_id} \u2014 modificarea sumei schimb\u0103 soldul facturii.</div>` : ""}
        <label>Descriere<br><input type="text" id="je-desc" class="mig-text" style="width:100%" value="${escJ(n.descriere || "")}"></label>
        <div id="je-linii" style="margin-top:8px">${n.linii.map((l, i) => `
          <div style="display:flex;gap:8px;margin-bottom:6px" data-lin="${i}">
            <input type="text" class="mig-text je-deb" placeholder="debit" value="${escJ(l.debit)}" style="width:90px">
            <span style="align-self:center">=</span>
            <input type="text" class="mig-text je-cre" placeholder="credit" value="${escJ(l.credit)}" style="width:90px">
            <input type="number" step="0.01" class="mig-text je-sum" value="${l.suma.toFixed(2)}" style="width:120px">
            <button class="btn btn-secundar je-scoate">\u2212</button>
          </div>`).join("")}</div>
        <p><button class="btn btn-secundar" id="je-plus">+ linie</button></p>
        <p style="margin-top:10px">
          <button class="btn" id="je-salveaza">Salveaz\u0103</button>
          <button class="btn btn-secundar" id="je-renunta" style="margin-left:6px">Renun\u021b\u0103</button>
        </p>
      </div>`;
    const randuri = !note.length
      ? `<div class="mig-gol">Nicio nota in luna asta.</div>`
      : note.map(rand).join("");
    const ciorne = note.filter((n) => n.status === "ciorna").length;
    corp.innerHTML = `
      <h2 class="pf-titlu">Registru jurnal \u00b7 ${escJ(t.nume || "")}</h2>
      <p class="pf-intro">Luna ${String(luna).padStart(2, "0")}/${an} \u00b7 ${note.length} note${ciorne ? ` \u00b7 <span style="color:#c9961f;font-weight:600">${ciorne} de validat</span>` : ""}
        <button class="btn btn-secundar" id="j-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="btn btn-secundar" id="j-next">luna \u2192</button>
        <button class="btn" id="j-amort" style="margin-left:12px">Genereaza amortizarea</button></p>
      <div id="j-mesaj"></div>
      <div class="pf-lista">${randuri}</div>`;
    const zonaMesaj = corp.querySelector("#j-mesaj");
    const eroare = (e, txt) => { zonaMesaj.innerHTML = `<div class="mig-gol">${escJ((e && e.mesaj) || txt)}</div>`; };
    corp.querySelector("#j-prev").addEventListener("click", () => { inEditare = null; luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#j-next").addEventListener("click", () => { inEditare = null; luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    corp.querySelector("#j-amort").addEventListener("click", async () => {
      try {
        const r = await api.post(`/tenants/${t.id}/amortizare?an=${an}&luna=${luna}`, {});
        alert(r.linii ? `Nota generata: ${r.linii} mijloace fixe, total ${r.total} lei` : "Nimic de amortizat.");
        deseneaza();
      } catch (e) { alert(e.mesaj || "Eroare"); }
    });
    corp.querySelectorAll("[data-val]").forEach((b) => b.addEventListener("click", async () => {
      try { await api.post(`/tenants/${t.id}/jurnal/${b.dataset.val}/valideaza`, {}); deseneaza(); }
      catch (e) { eroare(e, "Eroare la validare"); }
    }));
    corp.querySelectorAll("[data-del]").forEach((b) => b.addEventListener("click", async () => {
      if (!confirm("Stergi aceasta ciorna?")) return;
      try { await api.del(`/tenants/${t.id}/jurnal/${b.dataset.del}`); deseneaza(); }
      catch (e) { eroare(e, "Eroare la stergere"); }
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
        d.innerHTML = `<input type="text" class="mig-text je-deb" placeholder="debit" style="width:90px">
          <span style="align-self:center">=</span>
          <input type="text" class="mig-text je-cre" placeholder="credit" style="width:90px">
          <input type="number" step="0.01" class="mig-text je-sum" value="0.00" style="width:120px">
          <button class="btn btn-secundar je-scoate">\u2212</button>`;
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
          await api.put(`/tenants/${t.id}/jurnal/${inEditare}`,
            { descriere: corp.querySelector("#je-desc").value, linii });
          inEditare = null; deseneaza();
        } catch (e) { eroare(e, "Eroare la salvare"); }
      });
    }
  };
  deseneaza();
}


// [bonuri] verificare + contare bonuri citite de AI (linii multiple)
async function ecranBonuri(corp, nav, t) {
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se incarca...</p>`;
    let bonuri = [];
    try {
      const r = await api.get(`/tenants/${t.id}/bonuri/de-verificat`);
      bonuri = (r && r.bonuri) || [];
    } catch {}
    const randuri = !bonuri.length
      ? `<div class="mig-gol">Niciun bon de verificat.</div>`
      : bonuri.map((b, i) => `
        <div class="pf-frand" style="flex-wrap:wrap">
          <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:8px;width:100%;align-items:end">
            <label>Comerciant<br><input class="mig-text" id="b-com-${i}" value="${b.comerciant || ""}"></label>
            <label>Data<br><input class="mig-text" type="date" id="b-data-${i}" value="${b.data || ""}"></label>
            <label>Total<br><input class="mig-text" type="number" step="0.01" id="b-tot-${i}" value="${b.total}"></label>
            <label>TVA total<br><input class="mig-text" type="number" step="0.01" id="b-tva-${i}" value="${b.tva}"></label>
          </div>
          <div id="b-linii-${i}" style="width:100%;margin-top:8px">
            ${(b.articole || []).map((a, j) => `
              <div style="display:grid;grid-template-columns:2fr 1fr 1fr;gap:8px;margin-top:4px">
                <input class="mig-text" id="b-den-${i}-${j}" value="${a.denumire || ""}" readonly>
                <input class="mig-text" type="number" step="0.01" id="b-val-${i}-${j}" value="${a.valoare || 0}">
                <input class="mig-text" id="b-cont-${i}-${j}" value="${a.cont_propus || ""}" placeholder="cont">
              </div>`).join("")}
          </div>
          <div style="margin-top:8px"><button class="btn" data-aproba="${i}">Certifica si conteaza</button></div>
        </div>`).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">Bonuri de verificat \u00b7 ${t.nume || ""}</h2>
      <p class="pf-intro">Verifica articolele, pune contul pe fiecare, apoi certifica. Liniile cu acelasi cont se aduna.</p>
      <div class="pf-lista">${randuri}</div>`;
    corp.querySelectorAll("[data-aproba]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const i = parseInt(btn.dataset.aproba);
        const b = bonuri[i];
        const v = (id) => corp.querySelector(id).value;
        const grupe = {};
        let ok = true;
        (b.articole || []).forEach((a, j) => {
          const cont = v(`#b-cont-${i}-${j}`).trim();
          const val = parseFloat(v(`#b-val-${i}-${j}`)) || 0;
          if (!cont) ok = false;
          grupe[cont] = (grupe[cont] || 0) + val;
        });
        if (!ok) { alert("Pune contul pe fiecare articol."); return; }
        const linii = Object.entries(grupe).map(([cont, valoare]) => ({ cont, valoare: Math.round(valoare * 100) / 100 }));
        try {
          await api.post(`/tenants/${t.id}/bonuri/${b.id}/aproba`, {
            comerciant: v(`#b-com-${i}`), data: v(`#b-data-${i}`),
            total: parseFloat(v(`#b-tot-${i}`)) || 0,
            tva: parseFloat(v(`#b-tva-${i}`)) || 0,
            linii,
          });
          deseneaza();
        } catch (e) { alert(e.mesaj || "Eroare"); }
      });
    });
  };
  deseneaza();
}

// [balanta] Balanta de verificare - descarcare PDF lunar
async function ecranBalanta(corp, nav, t) {
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  const deseneaza = () => {
    corp.innerHTML = `
      <h2 class="pf-titlu">Balan\u021b\u0103 de verificare \u00b7 ${String(t.nume || "")}</h2>
      <p class="pf-intro">Luna ${String(luna).padStart(2, "0")}/${an}
        <button class="btn btn-secundar" id="b-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="btn btn-secundar" id="b-next">luna \u2192</button></p>
      <p><button class="btn" id="b-pdf">Descarc\u0103 PDF</button></p>
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
