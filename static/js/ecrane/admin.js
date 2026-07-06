// admin.js — desktopul superadmin (Admin iConta).
// Spatiu separat de cabinet: doar functiile de administrare iConta.
// Acum: cardul Raportari (raspuns la sesizari). Extensibil (adaugi un dict in DEF).

import { sesiune } from "../sesiune.js";
import { api, arataMesaj } from "../api.js";
import { randeazaAdminRaportari } from "./admin_raportari.js";
import { randeazaAdminActivitate } from "./admin_activitate.js";
import { randeazaAdminGratuite } from "./admin_gratuite.js";
import { randeazaAdminSanatate } from "./admin_sanatate.js";

// iconite SVG inline (autonome)
const IC = {
  report: '<rect x="3" y="4" width="18" height="14" rx="2"/><path d="M3 8h18"/><path d="M7 12h7M7 15h4"/>',
};
function svg(cheie, fg) {
  return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="${fg}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${IC[cheie] || ""}</svg>`;
}

// cardurile panoului Admin iConta (extensibil)
const DEF = [
  { cheie:"raportari", titlu:"Raportări", icon:"report", bg:"#f3e8ff", fg:"#6d28d9",
    sinteza:"Răspunde la sesizările utilizatorilor",
    actiune:(nav) => nav.deschide("Raportări", (corp) => randeazaAdminRaportari(corp, nav)) },
  { cheie:"activitate", titlu:"Activitate cabinete", icon:"report", bg:"#e6f6ec", fg:"#16a34a",
    sinteza:"Cine e activ, cine nu",
    actiune:(nav) => nav.deschide("Activitate cabinete", (corp) => randeazaAdminActivitate(corp, nav)) },
  { cheie:"gratuite", titlu:"Facturare gratuită", icon:"report", bg:"#eef4ff", fg:"#1d4ed8",
    sinteza:"Conturi gratuite: cine e activ, cine nu",
    actiune:(nav) => nav.deschide("Facturare gratuită", (corp) => randeazaAdminGratuite(corp, nav)) },
  { cheie:"anunturi", titlu:"Anunțuri", icon:"report", bg:"#fff7e6", fg:"#b45309",
    sinteza:"Banner la logare pentru cabinete",
    actiune:(nav) => nav.deschide("Anunțuri", (corp) => randeazaAdminAnunturi(corp, nav)) },
  { cheie:"sanatate", titlu:"Sănătate server", icon:"report", bg:"#fdeef2", fg:"#c0246b",
    sinteza:"Server, aplicație, bază de date, erori",
    actiune:(nav) => nav.deschide("Sănătate server", (corp) => randeazaAdminSanatate(corp, nav)) },
];

export function desktopAdmin(continut, nav) {
  const u = sesiune.user() || {};
  const azi = new Date().toLocaleDateString("ro-RO", { day:"numeric", month:"long", year:"numeric" });
  const prenume = u.prenume || (u.nume || "").split(" ").slice(-1)[0] || u.nume || "";
  continut.innerHTML = `
    <div class="cab-salut">
      <div class="cab-salut-nume">Bună, ${prenume}</div>
      <div class="cab-salut-data">Panou Admin iConta — ${azi}</div>
    </div>
    <div class="cab-grila"></div>
  `;
  const grila = continut.querySelector(".cab-grila");
  DEF.forEach((c) => {
    const card = document.createElement("button");
    card.className = "cab-card";
    card.style.background = c.bg;
    card.style.color = c.fg;
    card.innerHTML = `
      <div class="cab-card-cap">${svg(c.icon, c.fg)}<span class="cab-card-titlu">${c.titlu}</span></div>
      <div class="cab-card-sinteza" data-cheie="${c.cheie}">${c.sinteza}</div>
    `;
    card.addEventListener("click", () => c.actiune(nav));
    grila.appendChild(card);
  });
}


// admin_anunturi_fe_v1
async function randeazaAdminAnunturi(corp, nav) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  let cabinete = [];
  try {
    const r = await api.get("/admin/activitate/cabinete");
    cabinete = (r && r.cabinete) || [];
  } catch {}
  corp.innerHTML = `
    <p class="mig-intro">Mesajul apare ca banner la logarea cabinetului, până apasă „Am înțeles".</p>
    <div class="camp" style="margin-bottom:10px"><label class="camp-eticheta">Destinatar</label>
      <select class="camp-input" id="an-cab">
        <option value="">Toate cabinetele</option>
        ${cabinete.map((c) => `<option value="${c.id}">${(c.nume || "").replace(/[<>&]/g, "")}</option>`).join("")}
      </select></div>
    <div class="camp" style="margin-bottom:10px"><label class="camp-eticheta">Mesaj</label>
      <textarea class="camp-input" id="an-mesaj" rows="4" style="resize:vertical;min-height:90px"></textarea></div>
    <button class="buton-primar" id="an-trimite">Trimite</button>
    <p id="an-msg" style="margin-top:8px"></p>`;
  const ta = corp.querySelector("#an-mesaj");  /* textarea_auto_v1 */
  ta.addEventListener("input", () => { ta.style.height = "auto"; ta.style.height = ta.scrollHeight + "px"; });
  corp.querySelector("#an-trimite").addEventListener("click", async () => {
    const msg = corp.querySelector("#an-msg");
    const mesaj = corp.querySelector("#an-mesaj").value.trim();
    if (!mesaj) { arataMesaj(msg, "Scrie mesajul.", "eroare"); return; }
    const cid = corp.querySelector("#an-cab").value;
    try {
      const r = await api.post("/admin/anunturi", { mesaj, cabinet_id: cid ? Number(cid) : null });
      arataMesaj(msg, `Trimis către ${r.trimise} cabinet${r.trimise === 1 ? "" : "e"}.`, "info");
      corp.querySelector("#an-mesaj").value = "";
    } catch (e) { arataMesaj(msg, e.mesaj || e.message, "eroare"); }
  });
}