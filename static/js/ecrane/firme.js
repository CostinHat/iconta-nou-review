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

// [banca] Import extras bancar
async function ecranBanca(corp, nav, t) {
  corp.innerHTML = `
    <h2 class="pf-titlu">Banc\u0103 \u00b7 ${t.nume || ""}</h2>
    <p class="pf-intro">Incarca extrasul (.xls, .xlsx, .csv) \u2014 ING, Jasper.</p>
    <input type="file" id="bk-fisier" accept=".xls,.xlsx,.csv" style="margin-bottom:16px">
    <div id="bk-rezultat"></div>`;
  corp.querySelector("#bk-fisier").addEventListener("change", async (ev) => {
    const f = ev.target.files[0];
    if (!f) return;
    const zona = corp.querySelector("#bk-rezultat");
    zona.innerHTML = `<p class="ecran-nota">Se citeste extrasul...</p>`;
    const fd = new FormData();
    fd.append("fisier", f);
    try {
      const resp = await fetch(`/tenants/${t.id}/banca/parse-extras`, {
        method: "POST",
        headers: { "Authorization": "Bearer " + sesiune.token() },
        body: fd,
      });
      if (!resp.ok) throw new Error("eroare " + resp.status);
      const r = await resp.json();
      const tr = r.tranzactii || [];
      zona.innerHTML = `
        <p class="pf-intro"><b>${tr.length}</b> tranzactii citite.</p>
        <div class="pf-lista">${tr.map((x) => `
          <div class="pf-frand">
            <div class="pf-frand-text">
              <div class="pf-frand-nume">${x.data} \u00b7 ${x.suma < 0 ? "" : "+"}${x.suma.toFixed(2)} lei${x.cui ? " \u00b7 CUI " + x.cui : ""}</div>
              <div class="pf-frand-sub">${(x.detalii || "").slice(0, 90)} \u00b7 ${x.tip || ""}</div>
            </div>
          </div>`).join("")}</div>`;
    } catch { zona.innerHTML = `<div class="mig-gol">Nu am putut citi extrasul.</div>`; }
  });
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
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se incarca...</p>`;
    let note = [];
    try {
      const r = await api.get(`/tenants/${t.id}/jurnal?an=${an}&luna=${luna}`);
      note = (r && r.note) || [];
    } catch {}
    const randuri = !note.length
      ? `<div class="mig-gol">Nicio nota in luna asta.</div>`
      : note.map((n) => `
        <div class="pf-frand">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">${n.data} \u00b7 ${n.descriere || n.numar || "#" + n.id}</div>
            <div class="pf-frand-sub">${n.linii.map((l) => `${l.debit} = ${l.credit} \u00b7 ${l.suma.toFixed(2)}`).join("<br>")}</div>
          </div>
          <span class="mig-stare">${n.sursa || ""}</span>
        </div>`).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">Registru jurnal \u00b7 ${t.nume || ""}</h2>
      <p class="pf-intro">Luna ${String(luna).padStart(2,"0")}/${an} \u00b7 ${note.length} note
        <button class="btn btn-secundar" id="j-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="btn btn-secundar" id="j-next">luna \u2192</button></p>
      <div class="pf-lista">${randuri}</div>`;
    corp.querySelector("#j-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#j-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
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
