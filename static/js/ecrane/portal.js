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
      sinteza: "Facturile emise si primite" },
    { cheie: "declaratii", titlu: "Declaratii depuse", icon: "declaratii", bg: "#dff4f2", fg: "#0a807b",
      sinteza: "Ce s-a depus la ANAF pentru tine" },
    { cheie: "povestea", titlu: "Povestea lunii", icon: "povestea", bg: "#efebfe", fg: "#6d28d9",
      sinteza: "Raportul lunar de la contabil" },
    { cheie: "solicitari", titlu: "Solicitari", icon: "solicitari", bg: "#faece7", fg: "#993c1d",
      sinteza: "Cere ceva contabilului tau" },
    { cheie: "recomanda", titlu: "Recomanda", icon: "recomanda", bg: "#fbeedd", fg: "#92500a",
      sinteza: "Invita un antreprenor in iConta" },
    { cheie: "documente", titlu: "Documente", icon: "documente", bg: "#e6f6ec", fg: "#16a34a",
      sinteza: "Recipise, balante, bilant" },
  ];

  continut.innerHTML = `
    <div class="cab-salut">
      <div class="cab-salut-nume">Portalul firmei</div>
      <div class="cab-salut-sub">${firma}</div>
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
  else if (cheie === "povestea") nav.deschide("Povestea lunii", (corp) => ecranInLucru(corp, nav, "Povestea lunii"));
  else if (cheie === "solicitari") nav.deschide("Solicitari", (corp) => ecranInLucru(corp, nav, "Solicitari"));
  else if (cheie === "recomanda") nav.deschide("Recomanda", (corp) => ecranInLucru(corp, nav, "Recomanda"));
  else if (cheie === "documente") nav.deschide("Documente", (corp) => ecranInLucru(corp, nav, "Documente"));
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
    clasa = "pa-rosu"; titlu = `${restante.length} ${restante.length === 1 ? "declaratie restanta" : "declaratii restante"}`;
    sub = "Contabilul tau se ocupa - mai jos vezi ce e de depus.";
  } else if (d.stare === "galben") {
    clasa = "pa-galben"; titlu = `${urmarit.length} ${urmarit.length === 1 ? "termen apropiat" : "termene apropiate"}`;
    sub = "Scadente in perioada urmatoare.";
  }

  const linii = [...restante, ...urmarit];
  let listaHtml = "";
  if (linii.length) {
    listaHtml = `<div class="pa-lista">` + linii.map((x) =>
      `<div class="pa-rand">
        <span class="pa-tip">${x.tip}</span>
        <span class="pa-perioada">${x.perioada || ""}</span>
        <span class="pa-termen">pana pe ${fmtTermen(x.termen)}</span>
      </div>`).join("") + `</div>`;
  }

  zona.innerHTML = `<div class="pa-card ${clasa}">
    <div class="pa-titlu">${titlu}</div>
    <div class="pa-sub">${sub}</div>
    ${listaHtml}
  </div>`;
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

// ---------- IN LUCRU (placeholder pentru cardurile ce urmeaza) ----------
function ecranInLucru(corp, nav, nume) {
  corp.innerHTML = `<div class="mig-gol">"${nume}" vine in curand.</div>`;
}
