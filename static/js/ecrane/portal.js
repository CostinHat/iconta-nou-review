// portal.js  // [p93_facturi] — desktopul clientului (rol 'client'), READ-ONLY.
// Landing: panou status ANAF (semafor + scadente) sus + carduri de navigatie.
import { api } from "../api.js";
import { sesiune } from "../sesiune.js";
import { randeazaFacturi } from "./facturi_ecran.js";  // [p116_facturi_modul]

const SVG = (d, c) => `<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="${c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`;

const ICON = {
  facturi: '<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 13h6M9 17h4"/>',
  declaratii: '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
  povestea: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
  solicitari: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
  recomanda: '<path d="M20 12v10H4V12"/><path d="M2 7h20v5H2z"/><path d="M12 22V7"/><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"/>',
  documente: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>',
};

export function desktopPortal(continut, nav) {
  const u = sesiune.user() || {};
  const firma = u.nume_tenant || u.nume_firma || "firma ta";

  const CARDURI = [
    { cheie: "facturi", titlu: "Facturi", icon: "facturi", bg: "#e9f0fe", fg: "#1d4ed8",
      sinteza: "Vizualizeaza facturile emise si primite." },
    { cheie: "declaratii", titlu: "Declaratii depuse", icon: "declaratii", bg: "#dff4f2", fg: "#0a807b",
      sinteza: "Ce s-a depus la ANAF pentru tine" },
    { cheie: "documente", titlu: "Documente", icon: "documente", bg: "#e6f6ec", fg: "#16a34a",
      sinteza: "Recipise, balante, bilant" },
    { cheie: "solicitari", titlu: "Solicitari", icon: "solicitari", bg: "#faece7", fg: "#993c1d",
      sinteza: "Trimite o solicitare contabilului." },
    { cheie: "povestea", titlu: "Povestea lunii", icon: "povestea", bg: "#efebfe", fg: "#6d28d9",
      sinteza: "Raportul lunar de la contabil" },
    { cheie: "recomanda", titlu: "Recomanda", icon: "recomanda", bg: "#fbeedd", fg: "#92500a",
      sinteza: "Invita un antreprenor in iConta" },
  ];

  continut.innerHTML = `
    <div class="cab-salut portal-sus">
      <div class="cab-salut-nume">${firma}</div>
      <div class="cab-salut-sub">Portal Client</div>
    </div>
    <div class="pa-status" id="pa-status"><p class="ecran-nota">Se verifica situatia la ANAF...</p></div>
    <div class="cab-grila"></div>
  `;

  const grila = continut.querySelector(".cab-grila");
  CARDURI.forEach((c) => {
    const card = document.createElement("button");
    card.className = "cab-card";
    card.style.background = c.bg;
    card.style.color = c.fg;
    card.innerHTML = `
      <div class="cab-card-cap">${SVG(ICON[c.icon], c.fg)}<span class="cab-card-titlu">${c.titlu}</span></div>
      <div class="cab-card-sinteza">${c.sinteza}</div>
    `;
    card.addEventListener("click", () => deschideCard(c.cheie, nav));
    grila.appendChild(card);
  });

  actualizeazaStatusAcasa(continut);
}

function deschideCard(cheie, nav) {
  if (cheie === "facturi") nav.deschide("Facturi", (corp) => deschideFacturi(corp, nav));  // [p116_facturi_modul]
  else if (cheie === "declaratii") nav.deschide("Declaratii depuse", (corp) => ecranDeclaratii(corp, nav));
  else if (cheie === "povestea") nav.deschide("Povestea lunii", (corp) => ecranPovestea(corp, nav));
  else if (cheie === "solicitari") nav.deschide("Solicitari", (corp) => ecranSolicitari(corp, nav));  // ICRD_SOLICITARI_FRONT_V1
  else if (cheie === "recomanda") nav.deschide("Recomanda", (corp) => ecranRecomanda(corp, nav));
  else if (cheie === "documente") nav.deschide("Documente", (corp) => ecranDocumente(corp, nav));
}

// ---------- PANOU STATUS ANAF (Acasa) ----------
async function actualizeazaStatusAcasa(continut) {
  const zona = continut.querySelector("#pa-status");
  if (!zona) return;
  let d = {};
  try {
    d = await api.get("/portal/acasa");
  } catch {
    zona.innerHTML = "";
    return;
  }
  const luni = ["", "ian", "feb", "mar", "apr", "mai", "iun", "iul", "aug", "sep", "oct", "noi", "dec"];
  const fmtTermen = (iso) => {
    if (!iso) return "";
    const p = iso.split("-");
    return p.length === 3 ? `${p[2]} ${luni[parseInt(p[1], 10)]}` : iso;
  };
  const restante = d.restante || [];
  const urmarit = d.de_urmarit || [];

  if (d.mesaj === "vector fiscal necompletat" || d.stare === "gri") {
    zona.innerHTML = `<div class="pa-card pa-neutru">
      <div class="pa-titlu">Situatia fiscala se configureaza</div>
      <div class="pa-sub">Contabilul tau finalizeaza inca setarea firmei.</div>
    </div>`;
    return;
  }

  let clasa = "pa-verde", titlu = "Totul e la zi", sub = "Nicio declaratie restanta. Contabilul tau are situatia sub control.";
  if (d.stare === "rosu") {
    clasa = "pa-rosu"; titlu = `${restante.length} ${restante.length === 1 ? "declaratie trebuie depusa" : "declaratii trebuie depuse"}`;
    sub = "Contabilul tau se ocupa.";
  } else if (d.stare === "galben") {
    clasa = "pa-galben"; titlu = `${urmarit.length} ${urmarit.length === 1 ? "termen apropiat" : "termene apropiate"}`;
    sub = "Scadente in perioada urmatoare.";
  }

  const linii = [...restante, ...urmarit];
  let listaHtml = "";
  if (linii.length) {
    listaHtml = `<div class="pa-lista" id="pa-lista" hidden>` + linii.map((x) =>
      `<div class="pa-rand">
        <span class="pa-tip">${x.tip}</span>
        <span class="pa-perioada">${x.perioada || ""}</span>
        <span class="pa-termen">pana pe ${fmtTermen(x.termen)}</span>
      </div>`).join("") + `</div>`;
  }

  zona.innerHTML = `<div class="pa-card ${clasa}" id="pa-card" style="${linii.length ? "cursor:pointer" : ""}">
    <div class="pa-titlu">${titlu}</div>
    <div class="pa-sub">${sub}</div>
    ${listaHtml}
  </div>`;

  if (linii.length) {
    const card = zona.querySelector("#pa-card");
    const lista = zona.querySelector("#pa-lista");
    card.addEventListener("click", () => { lista.hidden = !lista.hidden; });
  }
}

// [p107_facturi_meniu] MENIU FACTURI: doua optiuni (Istoric / Emite)
// [p116_facturi_modul] Facturi -> modul reutilizabil facturi_ecran.js
async function deschideFacturi(corp, nav) {
  let tenantId = null;
  try {
    const f = await api.get("/portal/firma");
    tenantId = (f && (f.tenant_id || f.id)) || null;
  } catch {}
  if (!tenantId) {
    const u = sesiune.user() || {};
    tenantId = u.tenant_id || u.tenant || null;
  }
  if (!tenantId) {
    corp.innerHTML = `<div class="mig-gol">Nu am putut identifica firma.</div>`;
    return;
  }
  randeazaFacturi(corp, nav, tenantId);  // [p125_portal_curat]
}

// ---------- DECLARATII DEPUSE ----------
async function ecranDeclaratii(corp, nav) {
  corp.innerHTML = `<p class="ecran-nota">Se incarca...</p>`;
  let lista = [];
  try {
    const r = await api.get("/portal/declaratii");
    lista = (r && r.declaratii) || [];
  } catch {}
  let corpuri = !lista.length
    ? `<div class="mig-gol">Nicio declaratie depusa inca.</div>`
    : lista.map((d) => `
      <div class="pf-frand">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${d.tip || ""} \u00b7 ${d.perioada || ""}</div>
          <div class="pf-frand-sub">depusa ${d.depus_la || d.data || ""}</div>
        </div>
        <span class="pf-frand-ok">\u2713 depusa</span>
      </div>`).join("");
  corp.innerHTML = `
    <h2 class="pf-titlu">Declaratii depuse</h2>
    <p class="pf-intro">Ce a fost depus la ANAF pentru firma ta.</p>
    <div class="pf-lista">${corpuri}</div>`;
}

// ---------- SOLICITARI (chat cu contabilul) ----------  // ICRD_SOLICITARI_FRONT_V1
function fmtData(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  const zz = String(d.getDate()).padStart(2, "0");
  const ll = String(d.getMonth() + 1).padStart(2, "0");
  return `${zz}/${ll}/${d.getFullYear()}`;
}

async function ecranSolicitari(corp, nav) {
  corp.innerHTML = `<p class="ecran-nota">Se incarca...</p>`;
  await randeazaSolicitari(corp, nav);
}

async function randeazaSolicitari(corp, nav) {
  let lista = [];
  try {
    const r = await api.get("/portal/solicitari");
    lista = (r && r.solicitari) || [];
  } catch {}
  let firHtml = '<div class="mig-gol">Niciun mesaj inca.</div>';
  if (lista.length) {
    firHtml = lista.map((s) => {
      const cine = s.autor_rol === "cabinet" ? "Contabil" : "Tu";
      return `<div class="sol-rand sol-${s.autor_rol}">
        <div class="sol-mesaj">${s.mesaj}</div>
        <div class="sol-meta">${cine} · ${fmtData(s.creat_la)}</div>
      </div>`;
    }).join("");
  }
  corp.innerHTML = `
    <h2 class="pf-titlu">Solicitari</h2>
    <p class="pf-intro">Cere ceva contabilului tau.</p>
    <div class="sol-fir" id="sol-fir">${firHtml}</div>
    <div class="sol-trimite">
      <textarea id="sol-input" placeholder="Scrie un mesaj..." rows="3"></textarea>
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
      await api.post("/portal/solicitari", { mesaj: txt });
      await randeazaSolicitari(corp, nav);
    } catch {}
  });
}

// ---------- POVESTEA LUNII ----------
async function ecranPovestea(corp, nav) {
  corp.innerHTML = `<p class="ecran-nota">Se incarca...</p>`;
  let lista = [];
  try {
    const r = await api.get("/portal/povesti");
    lista = (r && r.povesti) || [];
  } catch {}
  const luni = ["", "ianuarie", "februarie", "martie", "aprilie", "mai", "iunie",
                "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie"];
  if (!lista.length) {
    corp.innerHTML = `
      <h2 class="pf-titlu">Povestea lunii</h2>
      <p class="pf-intro">Raportul lunar de la contabil.</p>
      <div class="mig-gol">Inca nu ai primit niciun raport lunar.</div>`;
    return;
  }
  const fmtDif = (p) => {
    if (typeof p.diferenta !== "number") return "";
    const semn = p.diferenta > 0 ? "+" : "";
    const culoare = p.diferenta > 0 ? "#16a34a" : (p.diferenta < 0 ? "#dc2626" : "#666");
    return `<span style="color:${culoare};font-weight:600">${semn}${p.diferenta.toLocaleString("ro-RO")} lei fata de luna anterioara</span>`;
  };
  const corpuri = lista.map((p) => `
    <div class="pf-frand">
      <div class="pf-frand-text">
        <div class="pf-frand-nume">${luni[p.luna] || p.luna} ${p.an}</div>
        <div class="pf-frand-sub">${(p.text || "").slice(0, 80)}...</div>
        <div class="pf-frand-sub">${fmtDif(p)}</div>
      </div>
    </div>`).join("");
  corp.innerHTML = `
    <h2 class="pf-titlu">Povestea lunii</h2>
    <p class="pf-intro">Raportul lunar de la contabil.</p>
    <div class="pf-lista" id="pov-lista">${corpuri}</div>
    <div id="pov-detaliu"></div>`;
  corp.querySelectorAll(".pf-frand").forEach((el, i) => {
    el.style.cursor = "pointer";
    el.addEventListener("click", () => {
      const p = lista[i];
      corp.querySelector("#pov-detaliu").innerHTML = `
        <div class="pov-card">
          <h3>${luni[p.luna] || p.luna} ${p.an}</h3>
          <div class="pov-text">${(p.text || "").replace(/\n/g, "<br>")}</div>
          ${typeof p.diferenta === "number" ? `<div class="pov-dif">${fmtDif(p)}</div>` : ""}
        </div>`;
    });
  });
}

// ---------- RECOMANDA ----------
async function ecranRecomanda(corp, nav) {
  corp.innerHTML = `<p class="ecran-nota">Se incarca...</p>`;
  let previewHtml = "";
  try {
    const p = await api.get("/portal/recomanda/preview");
    previewHtml = (p && p.html) || "";
  } catch {}
  corp.innerHTML = `
    <h2 class="pf-titlu">Recomanda</h2>
    <p class="pf-intro">Invita un antreprenor prieten sa afle despre iConta.</p>
    <div class="pov-card" style="margin-bottom:16px">
      <button type="button" id="rec-vezi-mesaj" class="btn" style="background:#fff;color:#111;border:1px solid #ddd">Vezi mesajul</button>
      <div id="rec-preview" style="display:none;margin-top:10px;border:1px solid #eee;border-radius:8px;padding:16px;background:#fafafa">${previewHtml}</div>
    </div>
    <textarea id="rec-emails" placeholder="email1@exemplu.ro, email2@exemplu.ro" rows="4"
      style="width:100%;padding:10px;border-radius:8px;border:1px solid #ddd;font-family:inherit;font-size:15px"></textarea>
    <p class="ecran-nota">Separa mai multe adrese prin virgula. Maxim 10.</p>
    <button class="btn" id="rec-trimite-btn" style="margin-top:14px">Trimite recomandarea</button>
    <div id="rec-rezultat" style="margin-top:16px"></div>
  `;
  const bVezi = corp.querySelector("#rec-vezi-mesaj");
  if (bVezi) bVezi.addEventListener("click", () => {
    const zona = corp.querySelector("#rec-preview");
    zona.style.display = zona.style.display === "none" ? "block" : "none";
  });
  corp.querySelector("#rec-trimite-btn").addEventListener("click", async () => {
    const raw = corp.querySelector("#rec-emails").value || "";
    const emails = raw.split(",").map((e) => e.trim()).filter(Boolean);
    const zona = corp.querySelector("#rec-rezultat");
    if (!emails.length) {
      zona.innerHTML = `<div class="mig-gol" style="color:#dc2626">Scrie cel putin un email.</div>`;
      return;
    }
    zona.innerHTML = `<p class="ecran-nota">Se trimite...</p>`;
    try {
      const r = await api.post("/portal/recomanda", { emails });
      const rez = (r && r.rezultate) || [];
      zona.innerHTML = rez.map((x) =>
        `<div class="pf-frand"><div class="pf-frand-text">${x.email} — ${x.stare === "trimis" ? "trimis" : "esuat"}</div></div>`
      ).join("");
    } catch {
      zona.innerHTML = `<div class="mig-gol">A aparut o eroare. Incearca din nou.</div>`;
    }
  });
}

// ---------- IN LUCRU (placeholder pentru cardurile ce urmeaza) ----------
async function ecranDocumente(corp, nav) {
  corp.innerHTML = `<p class="ecran-nota">Se incarca...</p>`;
  let luni = [];
  let decl = [];
  try {
    const r = await api.get("/portal/documente/luni");
    luni = (r && r.luni) || [];
    decl = (r && r.declaratii) || [];
  } catch {}
  const numeLuni = ["ianuarie","februarie","martie","aprilie","mai","iunie","iulie","august","septembrie","octombrie","noiembrie","decembrie"];
  let corpuri = !luni.length
    ? `<div class="mig-gol">Nicio luna cu date contabile inca.</div>`
    : luni.map((iso) => {
      const [an, ll] = iso.split("-");
      return `
      <div class="pf-frand">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">Balanta de verificare · ${numeLuni[parseInt(ll)-1]} ${an}</div>
          <div class="pf-frand-sub">generata automat din datele contabile</div>
        </div>
        <button class="btn" data-bal="${an}-${ll}">Descarca PDF</button>
      </div>`;
    }).join("");
  corp.innerHTML = `
    <h2 class="pf-titlu">Documente</h2>
    <p class="pf-intro">Balante lunare, generate automat.</p>
    <div class="pf-lista">${corpuri}</div>
    <h2 class="pf-titlu" style="margin-top:24px">Declaratii depuse</h2>
    <div class="pf-lista">${!decl.length ? '<div class="mig-gol">Nicio declaratie depusa inca.</div>' : decl.map((d) => `
      <div class="pf-frand">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${d.tip} \u00b7 ${String(d.luna).padStart(2,"0")}/${d.an}</div>
          <div class="pf-frand-sub">depusa ${fmtData(d.data)}</div>
        </div>
        <span class="pf-frand-ok">\u2713 depusa</span>
      </div>`).join("")}</div>`;
  corp.querySelectorAll("[data-bal]").forEach((b) => {
    b.addEventListener("click", async () => {
      const [an, ll] = b.dataset.bal.split("-");
      try {
        const resp = await fetch(`/portal/documente/balanta?an=${an}&luna=${parseInt(ll)}`, {
          headers: { "Authorization": "Bearer " + sesiune.token() }
        });
        if (!resp.ok) throw new Error("eroare " + resp.status);
        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = `balanta_${an}_${ll}.pdf`; a.click();
        URL.revokeObjectURL(url);
      } catch { alert("Nu am putut genera documentul."); }
    });
  });
}
function ecranInLucru(corp, nav, nume) {
  corp.innerHTML = `<div class="mig-gol">"${nume}" vine in curand.</div>`;
}
