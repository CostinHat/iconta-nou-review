// firme.js — lista de firme a cabinetului (parte din desktop, NU fereastră).
// Click pe o firmă -> aceea se deschide central (fereastra firmei + "În lucru").

import { api } from "../api.js";
import { sesiune } from "../sesiune.js";
import { randeazaFacturi } from "./facturi_ecran.js";

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
        </div>`).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">Stat de plat\u0103 \u00b7 ${t.nume || ""}</h2>
      <p class="pf-intro">Luna ${String(luna).padStart(2,"0")}/${an}
        <button class="btn btn-secundar" id="sp-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="btn btn-secundar" id="sp-next">luna \u2192</button></p>
      <div class="pf-lista">${randuri}</div>`;
    corp.querySelector("#sp-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#sp-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
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
          ${l.status !== "contat" ? `<button class="btn" data-alege="${l.id}" style="margin-left:6px">Alege facturile</button>` : ""}
        </div>
      </div>`).join("")}</div>`;
    zonaLista.querySelectorAll("[data-cont]").forEach((b) =>
      b.addEventListener("click", () => conteaza(parseInt(b.dataset.cont), null)));
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
        <div class="pf-frand-nume" style="margin-bottom:8px">Editare nota #${n.id} \u00b7 ${escJ(n.data)}</div>
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
