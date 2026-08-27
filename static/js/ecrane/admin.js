// admin.js — desktopul superadmin (Admin iConta).
// Spatiu separat de cabinet: doar functiile de administrare iConta.
// Acum: cardul Raportari (raspuns la sesizari). Extensibil (adaugi un dict in DEF).

import { sesiune } from "../sesiune.js?v=5d142951c9";
import { api, arataMesaj, dataRo, ICOANE, CULORI_CARD, esc } from "../api.js?v=c20d0584e2";
import { randeazaAdminRaportari } from "./admin_raportari.js?v=f1b04de0db";
import { randeazaAdminActivitate } from "./admin_activitate.js?v=0b7fa80bea";
import { randeazaAdminSanatate } from "./admin_sanatate.js?v=aa317fad50";
import { randeazaAdminAnalytics } from "./admin_analytics.js?v=eb0ee9388f";

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
  { cheie:"anunturi", titlu:"Anunțuri", icon: "anunturi", ...CULORI_CARD.chihlimbar,
    sinteza:"Banner la logare pentru cabinete",
    actiune:(nav) => nav.deschide("Anunțuri", (corp) => randeazaAdminAnunturi(corp, nav), { lat: "larg" }) },  /* anunturi_larg_v1 */
  { cheie:"analytics", titlu:"Analytics public", icon: "trend", ...CULORI_CARD.albastru,
    sinteza:"Vizite landing, deschideri modal, click-uri, ghiduri",
    actiune:(nav) => nav.deschide("Analytics public", (corp) => randeazaAdminAnalytics(corp, nav), { lat: "larg" }) },
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
  // [running_head_v1] detector "running == HEAD" (DECIZII/GARZI iulie): superadmin vede un semnal DOAR daca
  // procesul viu ruleaza alt commit decat HEAD. Nimic cand e la zi. Nu reporneste, doar semnaleaza (cap.6).
  (async () => {
    try {
      const v = await api.get("/admin/versiune");
      if (v && v.divergent) {
        const box = document.createElement("div");
        box.className = "caseta-atentie";
        box.id = "running-stale";
        box.innerHTML = `<div class="ca-mesaj">Rularea NU e la zi: serviciul rulează commitul <b>${esc((v.running || "").slice(0, 7))}</b>, dar HEAD e <b>${esc((v.head || "").slice(0, 7))}</b>. Codul publicat nu e cel care rulează. Repornește serviciul la o fereastră sigură (nu în mijlocul unei operații a unui contabil). Detectorul nu repornește nimic și nu repară nimic.</div>`;
        continut.insertBefore(box, continut.firstChild);
      }
    } catch {}
  })();
}


// admin_anunturi_fe_v1
async function randeazaAdminAnunturi(corp, nav) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  let cabinete = [];
  try {
    const r = await api.get("/admin/activitate/cabinete");
    cabinete = (r && r.cabinete) || [];
  } catch {}
  // [anunturi_meniu_v1] DS cap.2a: optiunile se deschid ca pasi de navigator, nu inline
  const stare = window._anStare = window._anStare || { segment: null, cabIds: null };  // persistenta intre re-randari (mergi/inapoi re-executa radacina)
  const rezumat = () => {
    if (stare.segment === "cabinete") return stare.cabIds ? `${stare.cabIds.length} cabinete alese` : "toate cabinetele";
    return "nimeni ales înc\u0103";
  };
  const meniu = () => {
    if (nav.setInapoi) nav.setInapoi(undefined);
    corp.innerHTML = `
      <h2 class="pf-titlu">Anun\u021buri</h2>
      <p class="mig-intro">Mesajul apare ca banner la logare, p\u00e2n\u0103 la \u201eAm \u00een\u021beles\u201d. Alege destinatarii, apoi scrie mesajul.</p>
      <div class="firme-meniu">
        <button class="firme-optiune" id="an-op-cab">
          <div class="firme-optiune-icon accent-albastru"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 21h18M5 21V7l7-4 7 4v14M9 9h1M9 13h1M14 9h1M14 13h1"/></svg></div>
          <div class="firme-optiune-titlu">Cabinete</div>
          <div class="firme-optiune-desc">${stare.segment === "cabinete" ? esc(rezumat()) : "alege cabinetele destinatare"}</div>
        </button>
        <button class="firme-optiune" id="an-op-msg">
          <div class="firme-optiune-icon accent-roz"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z"/></svg></div>
          <div class="firme-optiune-titlu">Mesaj</div>
          <div class="firme-optiune-desc">c\u0103tre: ${esc(rezumat())}</div>
        </button>
      </div>
      <div id="an-propuneri"></div>`;
    corp.querySelector("#an-op-cab").addEventListener("click", () => nav.mergi("Cabinete", (c) => pasSelectie(c, "cabinete")));
    corp.querySelector("#an-op-msg").addEventListener("click", () => nav.mergi("Mesaj", (c) => pasMesaj(c)));
    incarcaPropuneri(corp);
  };
  function pasSelectie(c, seg) {
    const idsCur = stare.cabIds;
    c.innerHTML = `
      <h2 class="pf-titlu">Cabinete destinatare</h2>
      <p class="mig-intro">Bifeaz\u0103 destinatarii. Nimic bifat = anun\u021bul merge la to\u021bi.</p>
      <input type="text" class="camp-input" id="sel-cauta" placeholder="caut\u0103" style="max-width:340px;margin-bottom:10px">
      <div class="pf-lista zebra-lista" id="an-sel-lista">
        ${cabinete.map((x, i) => `<label class="pf-frand set-bifa sel-rand" data-zebra="${i % 2}" style="cursor:pointer;display:flex;align-items:center;gap:12px"><input type="checkbox" class="sel-bifa" value="${x.id}" ${idsCur && idsCur.includes(x.id) ? "checked" : ""} style="flex-shrink:0">
          <div class="pf-frand-text" style="flex:1;text-align:left"><div class="pf-frand-nume">${esc(x.nume || "")}</div></div>
        </label>`).join("")}
      </div>`;
    c.querySelector("#sel-cauta").addEventListener("input", (e) => {
      const q = e.target.value.trim().toLowerCase();
      c.querySelectorAll(".sel-rand").forEach((r) => { r.style.display = !q || r.textContent.toLowerCase().includes(q) ? "" : "none"; });
    });
    const salveaza = () => {  // [sel_direct_v1] bifarea E selectia; nimic bifat = toate
      const ids = [...c.querySelectorAll(".sel-bifa:checked")].map((b) => Number(b.value));
      stare.segment = seg;
      const val = ids.length ? ids : null;
      stare.cabIds = val;
    };
    c.querySelectorAll(".sel-bifa").forEach((b) => b.addEventListener("change", salveaza));
    salveaza();
  }
  function pasMesaj(c) {
    c.innerHTML = `
      <h2 class="pf-titlu">Mesaj</h2>
      <p class="mig-intro">C\u0103tre: <b>${esc(rezumat())}</b></p>
      <div class="camp" style="margin-bottom:10px"><label class="camp-eticheta">Mesaj<span class="oblig">*</span></label>
        <textarea class="camp-input" id="an-mesaj" rows="4" style="resize:vertical;min-height:90px"></textarea></div>
      <div class="camp" style="margin-bottom:10px"><label class="camp-eticheta">Afi\u0219are de la data (op\u021bional \u2014 gol = imediat)</label>
        <input type="date" class="camp-input" id="an-data"></div>
      <button class="buton-primar" id="an-trimite">Trimite</button>
      <p id="an-msg" style="margin-top:8px"></p>`;
    const ta = c.querySelector("#an-mesaj");
    ta.addEventListener("input", () => { ta.style.height = "auto"; ta.style.height = ta.scrollHeight + "px"; });
    c.querySelector("#an-trimite").addEventListener("click", async () => {
      const msg = c.querySelector("#an-msg");
      const mesaj = ta.value.trim();
      if (!mesaj) { arataMesaj(msg, "Scrie mesajul.", "eroare"); return; }
      if (!stare.segment) { arataMesaj(msg, "Alege \u00eent\u00e2i destinatarii (Cabinete).", "eroare"); return; }
      try {
        const r = await api.post("/admin/anunturi", { mesaj, segment: stare.segment, cabinet_ids: stare.cabIds, cabinet_id: null, data_afisare: c.querySelector("#an-data").value || null });
        arataMesaj(msg, `Trimis c\u0103tre ${r.trimise} destinatar${r.trimise === 1 ? "" : "i"}.`, "ok");
        ta.value = "";
      } catch (e) { arataMesaj(msg, e.mesaj || e.message, "eroare"); }
    });
  }
  meniu();
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
