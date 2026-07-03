// firme.js — lista de firme a cabinetului (parte din desktop, NU fereastră).
// Click pe o firmă -> aceea se deschide central (fereastra firmei + "În lucru").

import { api } from "../api.js";
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
      icon: '<circle cx="9" cy="7" r="3"/><path d="M2 21v-1a6 6 0 0 1 12 0v1"/><path d="M16 3.5a3 3 0 0 1 0 7M22 21v-1a6 6 0 0 0-4-5.7"/>', activ: false },
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
