// admin.js — desktopul superadmin (Admin iConta).
// Spatiu separat de cabinet: doar functiile de administrare iConta.
// Acum: cardul Raportari (raspuns la sesizari). Extensibil (adaugi un dict in DEF).

import { sesiune } from "../sesiune.js";
import { api, arataMesaj, dataRo, ICOANE, CULORI_CARD, esc } from "../api.js";
import { randeazaAdminRaportari } from "./admin_raportari.js?v=5";
import { randeazaAdminActivitate } from "./admin_activitate.js?v=6";
import { randeazaAdminGratuite } from "./admin_gratuite.js";
import { randeazaAdminSanatate } from "./admin_sanatate.js";

// iconite SVG inline (autonome)
function svg(cheie, fg) {
  return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="${fg}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${ICOANE[cheie] || ""}</svg>`;
}

// cardurile panoului Admin iConta (extensibil)
const DEF = [
  { cheie:"raportari", titlu:"Raportări", icon:"report", ...CULORI_CARD.violet,
    sinteza:"Răspunde la sesizările utilizatorilor",
    actiune:(nav) => nav.deschide("Raportări", (corp) => randeazaAdminRaportari(corp, nav)) },
  { cheie:"activitate", titlu:"Activitate cabinete", icon: "activitate", ...CULORI_CARD.verde,
    sinteza:"Cine e activ, cine nu",
    actiune:(nav) => nav.deschide("Activitate cabinete", (corp) => randeazaAdminActivitate(corp, nav)) },
  { cheie:"gratuite", titlu:"Facturare gratuită", icon: "facturi", ...CULORI_CARD.albastru,
    sinteza:"Conturi gratuite: cine e activ, cine nu",
    actiune:(nav) => nav.deschide("Facturare gratuită", (corp) => randeazaAdminGratuite(corp, nav)) },
  { cheie:"anunturi", titlu:"Anunțuri", icon: "anunturi", ...CULORI_CARD.chihlimbar,
    sinteza:"Banner la logare pentru cabinete",
    actiune:(nav) => nav.deschide("Anunțuri", (corp) => randeazaAdminAnunturi(corp, nav)) },
  { cheie:"sanatate", titlu:"Sănătate server", icon: "server", ...CULORI_CARD.piersica,
    sinteza:"Server, aplicație, bază de date, erori",
    actiune:(nav) => nav.deschide("Sănătate server", (corp) => randeazaAdminSanatate(corp, nav)) },
];

export function desktopAdmin(continut, nav) {
  const u = sesiune.user() || {};
  const azi = dataRo(new Date(), "lung");
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
    <div class="camp" style="margin-bottom:10px"><label class="camp-eticheta">Afișare de la data (opțional — gol = imediat)</label>
      <input type="date" class="camp-input" id="an-data"></div>
    <button class="buton-primar" id="an-trimite">Trimite</button>
    <p id="an-msg" style="margin-top:8px"></p>
    <div id="an-propuneri"></div>`;
  incarcaPropuneri(corp);  // [F103 partea 2]
  const ta = corp.querySelector("#an-mesaj");  /* textarea_auto_v1 */
  ta.addEventListener("input", () => { ta.style.height = "auto"; ta.style.height = ta.scrollHeight + "px"; });
  corp.querySelector("#an-trimite").addEventListener("click", async () => {
    const msg = corp.querySelector("#an-msg");
    const mesaj = corp.querySelector("#an-mesaj").value.trim();
    if (!mesaj) { arataMesaj(msg, "Scrie mesajul.", "eroare"); return; }
    const cid = corp.querySelector("#an-cab").value;
    try {
      const r = await api.post("/admin/anunturi", { mesaj, cabinet_id: cid ? Number(cid) : null, data_afisare: corp.querySelector("#an-data").value || null });
      arataMesaj(msg, `Trimis către ${r.trimise} cabinet${r.trimise === 1 ? "" : "e"}.`, "info");
      corp.querySelector("#an-mesaj").value = "";
    } catch (e) { arataMesaj(msg, e.mesaj || e.message, "eroare"); }
  });
}
// [F103 partea 2] propunerile monitorului fiscal ca anunturi
async function incarcaPropuneri(corp) {
  const zona = corp.querySelector("#an-propuneri");
  if (!zona) return;
  let d = { alerte: [] };
  try { d = await api.get("/admin/alerte-fiscale"); } catch { return; }
  if (!d.alerte || !d.alerte.length) return;
  zona.innerHTML = `
    <h2 class="pf-titlu" style="margin-top:18px">Propuneri de la monitorul fiscal</h2>
    ${d.alerte.map((a) => `
      <div class="panou" style="margin-bottom:10px">
        <div><b>${esc(a.titlu)}</b>${a.relevanta === "mare" ? " \u00b7 relevan\u021b\u0103 mare" : ""}</div>
        <div class="tip-mic" style="margin:4px 0">${esc(a.rezumat || "")}</div>
        <button class="buton-secundar buton-mic" data-id="${a.id}">Preia \u00een mesaj</button>
      </div>`).join("")}`;
  zona.querySelectorAll("button[data-id]").forEach((b) => {
    b.addEventListener("click", async () => {
      const a = d.alerte.find((x) => String(x.id) === b.dataset.id);
      const ta2 = corp.querySelector("#an-mesaj");
      ta2.value = a.titlu + (a.rezumat ? "\n\n" + a.rezumat : "");
      ta2.dispatchEvent(new Event("input"));
      try { await api.post(`/admin/alerte-fiscale/${a.id}/tratat`, {}); } catch {}
      b.closest(".panou").remove();
      ta2.focus();
    });
  });
}
