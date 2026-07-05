// cabinet.js — desktopul cabinetului (admin_firma / superadmin).
// Bandă de salut + 9 carduri pastel (grilă 3×3), fiecare cu sinteza lui.
// Click pe card -> deschide fereastra/funcția corespunzătoare.

import { api } from "../api.js";
import { semaforCard as _semaforCard } from "./semafor.js";  // [p87_asistent]
import { sesiune } from "../sesiune.js";
import { randeazaListaFirme } from "./firme.js?v=22";
import { randeazaMigrare } from "./migrare.js";
import { randeazaControl } from "./control.js";
import { randeazaActivitateCabinet } from "./activitate_cabinet.js"; // [p17_activitate]
import { randeazaSetari } from "./setari.js?v=2"; // [p28_setari]
import { randeazaRecomanda } from "./recomanda.js"; // [p31_recomanda]
import { randeazaRaporteaza } from "./raporteaza.js"; // [p34_raporteaza]
import { randeazaPachete } from "./pachete.js"; // [p63_pachete]
import { randeazaTermene } from "./termene.js";
import { randeazaValidat } from "./validat.js";
import { randeazaAsistenti } from "./asistenti.js";
import { randeazaCapacitate } from "./capacitate.js"; // [p71_capacitate]
import { randeazaTipare } from "./tipare.js"; // [p72_tipare]

// iconițe SVG inline (autonome, fără dependență externă de rețea)
const IC = {
  building: '<path d="M3 21h18"/><path d="M5 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16"/><path d="M19 21V11a2 2 0 0 0-2-2h-2"/><path d="M9 7h2M9 11h2M9 15h2"/>',
  shield: '<path d="M12 3l8 3v5c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-3z"/><path d="M9 12l2 2 4-4"/>',
  calendar: '<rect x="4" y="5" width="16" height="16" rx="2"/><path d="M4 9h16M8 3v4M16 3v4"/>',
  clipboard: '<rect x="8" y="3" width="8" height="4" rx="1"/><path d="M8 5H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><path d="M9 14l2 2 4-4"/>',
  users: '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3 3-5 6-5s6 2 6 5"/><path d="M16 6a3 3 0 0 1 0 6M21 20c0-2-1-3.5-3-4.5"/>',
  mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
  gift: '<rect x="3" y="11" width="18" height="10" rx="1"/><path d="M3 11V9a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v2M12 7v14"/>',
  report: '<path d="M21 11.5a8.5 8.5 0 0 1-8.5 8.5 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8A8.5 8.5 0 0 1 12.5 3 8.5 8.5 0 0 1 21 11.5z"/><path d="M12 8v4M12 15.5v.5"/>',
  brief: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M5 19l1.5-1.5M17.5 6.5L19 5"/>',  // [p74_card_brief]
  trend: '<path d="M3 17l6-6 4 4 8-8"/><path d="M17 7h4v4"/>',  // [p72_tipare]
  gauge: '<path d="M12 13a4 4 0 0 1 4-4"/><path d="M3 18a9 9 0 0 1 18 0"/><path d="M12 13l4-2"/>',  // [p71_capacitate]
  settings: '<circle cx="12" cy="12" r="3"/><path d="M12 3v2M12 19v2M5 12H3M21 12h-2M6 6l1.5 1.5M18 18l-1.5-1.5M6 18l1.5-1.5M18 6l-1.5 1.5"/>',
};
function svg(nume, culoare) {
  return `<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="${culoare}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${IC[nume]}</svg>`;
}

// fereastră placeholder până construim ecranul real al fiecărui card
function inLucru(titlu) {
  return (nav) => nav.deschide(titlu, (corp) => {
    corp.innerHTML = `<p class="ecran-nota">„${titlu}" — ecran în construcție.</p>`;
  });
}

// definiția celor 9 carduri (sinteză = text inițial; unele se actualizează din date live)
const DEF = [  /* cab_ordine_v2 */
  { cheie:"firme",     titlu:"Firme",          icon:"building",  bg:"#e9f0fe", fg:"#1d4ed8",
    sinteza:"se încarcă…", actiune:inLucru("Firme") },
  { cheie:"validat",   titlu:"De validat",     icon:"clipboard", bg:"#faece7", fg:"#993c1d",
    sinteza:'<b style="font-size:19px">4</b> declarații de validat și trimis', actiune:inLucru("De validat") },
  { cheie:"control",   titlu:"Control fiscal", icon:"shield",    bg:"#dff4f2", fg:"#0a807b",
    sinteza:'se încarcă…',
    actiune:inLucru("Control fiscal") },
  { cheie:"termene",   titlu:"Termene",        icon:"calendar",  bg:"#e6f6ec", fg:"#15803d",
    sinteza:"Următoarea scadență: …", actiune:inLucru("Termene") },
  { cheie:"brief",     titlu:"Sinteza zilei",  icon:"brief",     bg:"#efebfe", fg:"#6d28d9",
    sinteza:"Vezi prioritățile zilei", actiune:inLucru("Sinteza zilei") },
  { cheie:"activitate", titlu:"Activitate",     icon:"report",    bg:"#fbeaf0", fg:"#993556",
    sinteza:"Activitate recentă", actiune:inLucru("Activitate") },
  { cheie:"pachete",   titlu:"Pachete lunare", icon:"mail",      bg:"#eef4ff", fg:"#1d4ed8",
    sinteza:"Trimite pachetul lunar către clienți", actiune:inLucru("Pachete lunare") },
  { cheie:"capacitate", titlu:"Capacitate",     icon:"gauge",     bg:"#eaf6f0", fg:"#0f7a4d",
    sinteza:"Cum stă echipa cu ritmul", actiune:inLucru("Capacitate") },
  { cheie:"consolidare", titlu:"Consolidare", icon:"report", bg:"#eaeef6", fg:"#45597f",
    sinteza:"Cifrele tuturor firmelor" },  // consolidare_fe_v1
  { cheie:"asistenti", titlu:"Asistenți",      icon:"users",     bg:"#fbeaf0", fg:"#993556",
    sinteza:'<b style="font-size:19px">·</b> asistenți în echipă', actiune:inLucru("Asistenți") },
  { cheie:"setari",    titlu:"Setări cont",    icon:"settings",  bg:"#eef0f3", fg:"#3a4250",
    sinteza:"Parolă și date de profil", actiune:inLucru("Setări cont") },
  { cheie:"raport",    titlu:"Suport",     icon:"report",    bg:"#e6f2ec", fg:"#1d7a4d",
    sinteza:"Întrebări, probleme și asistență tehnică", actiune:inLucru("Raportează") },
];

// [p73_sinteza_azi] deschide un ecran existent dupa cheie (refoloseste ecranele, nu duplica)
function deschideEcran(cheie, nav, continut) {
  if (cheie === "validat") return nav.deschide("De validat", (corp) => randeazaValidat(corp, nav));
  if (cheie === "activitate") return nav.deschide("Activitate cabinet", (corp) => randeazaActivitateCabinet(corp, nav));
  if (cheie === "capacitate") return nav.deschide("Capacitate", (corp) => randeazaCapacitate(corp, nav));
  if (cheie === "tipare") return nav.deschide("Tipare", (corp) => randeazaTipare(corp, nav));
  if (cheie === "raport") return nav.deschide("Raporteaza", (corp) => randeazaRaporteaza(corp, nav));
}

// [p73_sinteza_azi] panou de intampinare: sinteza zilei, totul clickabil spre ecranele de detaliu
async function randeazaSintezaAzi(nav, continut) {  // [p74_brief_modal] modal central de intampinare
  const azi = new Date().toISOString().slice(0, 10);
  const sfx = "?de=" + azi + "&pana=" + azi;
  let cen = { totaluri: {}, pe_asistent: [] };
  let jur = { evenimente: [] };
  let rap = { necitite: 0 };
  try { cen = await api.get("/asistenti/echipa/centralizator" + sfx); } catch {}
  try { jur = await api.get("/asistenti/echipa/jurnal" + sfx + "&limit=5"); } catch {}
  try { rap = await api.get("/raportari/contor"); } catch {}

  const t = cen.totaluri || {};
  const u = sesiune.user() || {};
  const numeFirma = u.nume_firma || "Cabinet";
  const dataRo = new Date().toLocaleDateString("ro-RO", { day:"numeric", month:"long", year:"numeric" });

  function cifra(val, eticheta, cheie, accent) {
    const cls = cheie ? "sa-cifra sa-clic" : "sa-cifra";
    const cc = accent || "#1a1d21";
    return `<button class="${cls}" data-ecran="${cheie || ""}">
      <span class="sa-num" style="color:${cc}">${val}</span>
      <span class="sa-desc">${eticheta}</span></button>`;
  }
  const cifre = [
    cifra(t.create || 0, "pregatite", "activitate"),
    cifra(t.aprobate || 0, "validate", "activitate", "#1d7a4d"),
    cifra(t.respinse || 0, "respinse", "tipare", (t.respinse ? "#ff3b30" : null)),
    cifra(t.depuse || 0, "depuse", "activitate", "#1d7a4d"),
    cifra(t.in_asteptare || 0, "de validat", "validat", (t.in_asteptare ? "#c9961f" : null)),
    cifra(rap.necitite || 0, "sesizari noi", "raport", (rap.necitite ? "#ff3b30" : null)),
  ].join("");

  let asist = "";
  const pa = (cen.pe_asistent || []).filter((a) => (a.create_ || 0) > 0 || (a.respinse || 0) > 0);
  if (pa.length) {
    asist = pa.map((a) => `
      <button class="sa-asist sa-clic" data-ecran="capacitate">
        <span class="sa-asist-nume">${(a.nume || "").replace(/[<>&]/g,"")}</span>
        <span class="sa-asist-cifre">${a.create_ || 0} pregatite${a.respinse ? " · " + a.respinse + " respinse" : ""}</span>
      </button>`).join("");
  } else {
    asist = `<p class="sa-gol">Niciun asistent n-a produs inca azi.</p>`;
  }

  const ACT = { pregatit:"a pregatit", aprobat:"a aprobat", respins:"a respins", depus:"a depus" };
  let jurnal = "";
  const ev = (jur.evenimente || []).slice(0, 5);
  if (ev.length) {
    jurnal = ev.map((e) => {
      const act = ACT[e.actiune] || e.actiune || "";
      const cl = e.actiune === "respins" ? "pct-rosu" : "pct-verde";
      const ora = e.cand ? new Date(e.cand).toLocaleTimeString("ro-RO",{hour:"2-digit",minute:"2-digit"}) : "";
      return `<li class="sa-ev"><span class="sa-pct ${cl}"></span>
        <span class="sa-ev-txt"><b>${(e.cine||"").replace(/[<>&]/g,"")}</b> ${act}
        ${(e.tip||"").toUpperCase()} ${e.firma ? "· " + (e.firma||"").replace(/[<>&]/g,"") : ""}</span>
        <span class="sa-ev-ora">${ora}</span></li>`;
    }).join("");
  } else {
    jurnal = `<li class="sa-gol">Nicio activitate inca azi.</li>`;
  }

  const ov = document.createElement("div");
  ov.className = "pacm-overlay brief-overlay";
  ov.innerHTML = `
    <div class="brief">
      <div class="brief-cap">
        <div>
          <div class="brief-titlu">Sinteza zilei</div>
          <div class="brief-sub">${numeFirma.replace(/[<>&]/g,"")} · ${dataRo}</div>
        </div>
        <button class="pacm-x" id="brief-x" aria-label="Inchide">✕</button>
      </div>
      <div class="brief-corp">
        <div class="sa-sectiune">
          <div class="sa-cap">Astazi in cabinet</div>
          <div class="sa-cifre">${cifre}</div>
        </div>
        <div class="sa-doua">
          <div class="sa-sectiune sa-flex1">
            <div class="sa-cap">Productia echipei</div>
            <div class="sa-asist-lista">${asist}</div>
          </div>
          <div class="sa-sectiune sa-flex1">
            <div class="sa-cap-rand">
              <span class="sa-cap">Ultimele evenimente</span>
              <button class="sa-link" data-ecran="activitate">Vezi tot</button>
            </div>
            <ul class="sa-jurnal">${jurnal}</ul>
          </div>
        </div>
      </div>
    </div>`;
  document.body.appendChild(ov);

  function inchide() { ov.remove(); }
  ov.querySelector("#brief-x").addEventListener("click", inchide);
  ov.addEventListener("click", (e) => { if (e.target === ov) inchide(); });
  ov.querySelectorAll("[data-ecran]").forEach((el) => {
    const cheie = el.getAttribute("data-ecran");
    if (!cheie) return;
    el.addEventListener("click", () => { inchide(); deschideEcran(cheie, nav, continut); });
  });
}

export function desktopCabinet(continut, nav) {
  randeazaPanou(continut, nav);
  // [p74_brief_modal] briefing de intampinare, o data per sesiune
  if (sessionStorage.getItem("iconta_brief_aratat") !== "1") {
    sessionStorage.setItem("iconta_brief_aratat", "1");
    setTimeout(() => randeazaSintezaAzi(nav, continut), 200);
  }
}

// VEDEREA 1: panoul cu cele 9 carduri
function randeazaPanou(continut, nav) {
  const u = sesiune.user() || {};
  const azi = new Date().toLocaleDateString("ro-RO", { day:"numeric", month:"long", year:"numeric" });
  const prenume = u.prenume || (u.nume || "").split(" ").slice(-1)[0] || u.nume || "";

  continut.innerHTML = `
    <div class="cab-salut" style="display:flex;justify-content:space-between;align-items:flex-end;gap:12px">
      <div>
        <div class="cab-salut-nume">Salut, ${prenume}</div>
        <div class="cab-salut-data">Spațiul tău de lucru — ${azi}</div>
      </div>
      <button class="cab-card cab-card-mic" id="cab-recomanda-mic" style="background:#fbeedd;color:#92500a">
        <div class="cab-card-cap">${svg("gift", "#92500a")}<span class="cab-card-titlu">Recomandă</span></div>
      </button>
    </div>
    <div class="cab-grila"></div>
  `;

  const grila = continut.querySelector(".cab-grila");
  continut.querySelector("#cab-recomanda-mic").addEventListener("click", () => nav.deschide("Recomanda", (corp) => randeazaRecomanda(corp, nav)));  /* recomanda_mic_v1 */
  DEF.forEach((c) => {
    const card = document.createElement("button");
    card.className = "cab-card";
    card.style.background = c.bg;
    card.style.color = c.fg;
    card.innerHTML = `
      <div class="cab-card-cap">${svg(c.icon, c.fg)}<span class="cab-card-titlu">${c.titlu}</span></div>
      <div class="cab-card-sinteza" data-cheie="${c.cheie}">${c.sinteza}</div>
    `;
    // "Firme" intră în meniul cu 2 opțiuni (parte din desktop); restul deschid fereastră
    if (c.cheie === "firme") {
      card.addEventListener("click", () => randeazaMeniuFirme(continut, nav));
    } else if (c.cheie === "control") {
      card.addEventListener("click", () => nav.deschide("Control fiscal", (corp) => randeazaControl(corp, nav)));
    } else if (c.cheie === "termene") {
      card.addEventListener("click", () => nav.deschide("Termene", (corp) => randeazaTermene(corp, nav)));
    } else if (c.cheie === "validat") {
      card.addEventListener("click", () => nav.deschide("De validat", (corp) => randeazaValidat(corp, nav)));
    } else if (c.cheie === "asistenti") {
      card.addEventListener("click", () => nav.deschide("Asistenți", (corp) => randeazaAsistenti(corp, nav)));
    } else if (c.cheie === "activitate") {  // [p76_comasare_font] meniu Activitate (jurnal + tipare)
      card.addEventListener("click", () => randeazaMeniuActivitate(continut, nav));
    } else if (c.cheie === "consolidare") {  // consolidare_fe_v1
      card.addEventListener("click", () => nav.deschide("Consolidare", (corp) => randeazaConsolidare(corp, nav)));
    } else if (c.cheie === "capacitate") {  // [p71_capacitate]
      card.addEventListener("click", () => nav.deschide("Capacitate", (corp) => randeazaCapacitate(corp, nav)));
    } else if (c.cheie === "brief") {  // [p74_card_brief]
      card.addEventListener("click", () => randeazaSintezaAzi(nav, continut));
    } else if (c.cheie === "setari") {  // [p28_setari]
      card.addEventListener("click", () => nav.deschide("Setari cont", (corp) => randeazaSetari(corp, nav)));
    } else if (c.cheie === "recomanda") {  // [p31_recomanda]
      card.addEventListener("click", () => nav.deschide("Recomanda", (corp) => randeazaRecomanda(corp, nav)));
    } else if (c.cheie === "pachete") {  // [p63_pachete]
      card.addEventListener("click", () => nav.deschide("Pachete lunare", (corp) => randeazaPachete(corp, nav)));
    } else if (c.cheie === "raport") {  // [p34_raporteaza]
      card.addEventListener("click", () => nav.deschide("Raporteaza", (corp) => randeazaRaporteaza(corp, nav)));
    } else {
      card.addEventListener("click", () => c.actiune(nav));
    }
    grila.appendChild(card);
  });

  actualizeazaFirme(grila);
  actualizeazaControl(grila);
  actualizeazaTermene(grila);
  actualizeazaActivitate(grila);
  actualizeazaValidat(grila);
  actualizeazaAsistenti(grila);
  actualizeazaRaportari(grila);  // [p34_raporteaza]
  _educatiePatruOchi(continut);  // [p51_edu]
  document.addEventListener("raportari:schimbat", () => actualizeazaRaportari(grila));
}

// VEDEREA 2: meniul Firme — două opțiuni (existente / migrare cabinet)
// [p76_comasare_font] meniul Activitate: doua optiuni (jurnal/centralizator + tipare)
// [p_activ_alerta] sinteza card Activitate: gol daca e curat, altfel N tipare
async function actualizeazaActivitate(grila) {
  const zona = grila.querySelector('[data-cheie="activitate"]');
  if (!zona) return;
  try {
    const r = await api.get("/asistenti/semafor");
    const n = (r.counts?.rosu || 0) + (r.counts?.galben || 0);
    window._activAlerta = n;
    zona.innerHTML = n === 0 ? "Activitate recentă" : `<b>${n}</b> ${n === 1 ? "tipar necesită atenție" : "tipare necesită atenție"}`;
  } catch {}
}
function randeazaMeniuActivitate(continut, nav) {
  continut.innerHTML = `
    <div class="sub-cap">
      <button class="sub-inapoi" id="sub-inapoi">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
      </button>
      <h1 class="sub-titlu">Activitate</h1>
    </div>
    <div class="firme-optiuni">
      <button class="firme-optiune" id="opt-jurnal">
        <div class="firme-optiune-icon" style="background:#e9f0fe; color:#1d4ed8">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h10"/></svg>
        </div>
        <div class="firme-optiune-titlu">Activitatea echipei</div>
        <div class="firme-optiune-desc">Centralizator si jurnal cronologic: cine ce a pregatit, validat, depus</div>
      </button>
      <button class="firme-optiune" id="opt-tipare">
        <div class="firme-optiune-icon" style="background:#fdeef0; color:#a3344b">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 17l6-6 4 4 8-8"/><path d="M17 7h4v4"/></svg>
        </div>
        <div class="firme-optiune-titlu">Tipare de erori ${window._activAlerta ? '<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#ff3b30;margin-left:6px"></span>' : ""}</div>
        <div class="firme-optiune-desc">Unde se greseste des si de ce — educatie din respingerile reale</div>
      </button>
    </div>
  `;
  continut.querySelector("#sub-inapoi").addEventListener("click", () => randeazaPanou(continut, nav));
  continut.querySelector("#opt-jurnal").addEventListener("click", () =>
    nav.deschide("Activitate cabinet", (corp) => randeazaActivitateCabinet(corp, nav)));
  continut.querySelector("#opt-tipare").addEventListener("click", () =>
    nav.deschide("Tipare", (corp) => randeazaTipare(corp, nav)));
}

function randeazaMeniuFirme(continut, nav) {
  continut.innerHTML = `
    <div class="sub-cap">
      <button class="sub-inapoi" id="sub-inapoi">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
      </button>
      <h1 class="sub-titlu">Firme</h1>
    </div>
    <div class="firme-optiuni">
      <button class="firme-optiune" id="opt-existente">
        <div class="firme-optiune-icon" style="background:#e9f0fe; color:#1d4ed8">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 21h18"/><path d="M5 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16"/><path d="M19 21V11a2 2 0 0 0-2-2h-2"/><path d="M9 7h2M9 11h2M9 15h2"/></svg>
        </div>
        <div class="firme-optiune-titlu">Firme existente</div>
        <div class="firme-optiune-desc">Vezi portofoliul, caută o firmă și deschide-o ca să lucrezi pe ea</div>
      </button>
      <button class="firme-optiune" id="opt-migrare">
        <div class="firme-optiune-icon" style="background:#e6f6ec; color:#16a34a">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12M8 11l4 4 4-4"/><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/></svg>
        </div>
        <div class="firme-optiune-titlu">Migrare cabinet</div>
        <div class="firme-optiune-desc">Adu-ți tot cabinetul în iConta — firmele se validează automat la ANAF</div>
      </button>
    </div>
  `;
  continut.querySelector("#sub-inapoi").addEventListener("click", () => randeazaPanou(continut, nav));
  continut.querySelector("#opt-existente").addEventListener("click", () =>
    randeazaListaFirme(continut, nav, () => randeazaMeniuFirme(continut, nav))
  );
  continut.querySelector("#opt-migrare").addEventListener("click", () =>
    nav.deschide("Migrare cabinet", (corp) => randeazaMigrare(corp, nav))
  );
}

// Firme: sinteză din date live (/tenants)
async function actualizeazaFirme(grila) {
  const zona = grila.querySelector('[data-cheie="firme"]');
  if (!zona) return;
  try {
    const r = await api.get("/tenants");
    const lista = (r && r.tenants) || [];
    const total = lista.length;
    const active = lista.filter((t) => t.activ).length;
    zona.innerHTML = `<b>${active}</b> ${active === 1 ? "firmă activă" : "firme active"}`;
  } catch (e) {
    zona.innerHTML = "—";
  }

  // reminder de migrare: dacă există pași în lucru, doar semnalul scurt pe card
  try {
    const s = await api.get("/migrare/status");
    const rem = (s && s.reminder) || [];
    if (rem.length) {
      const card = zona.closest(".cab-card");
      if (card) {
        const el = document.createElement("div");
        el.className = "cab-reminder";
        el.innerHTML = `<div class="cab-reminder-cap">⬇ Migrare nefinalizată</div>`;
        card.appendChild(el);
        card.classList.add("cab-card-alert");
      }
    }
  } catch {}
}


// Control fiscal: sinteza din /control-fiscal
// [p87_asistent] _semaforCard importat din semafor.js (alias mai jos)

async function actualizeazaControl(grila) {
  const zona = grila.querySelector('[data-cheie="control"]');
  if (!zona) return;
  try {
    const r = await api.get("/control-fiscal");
    const s = (r && r.sumar) || {};
    zona.innerHTML = _semaforCard([
      { n: s.rosu, cls: "pct-rosu", txt: s.rosu === 1 ? "alertă fiscală" : "alerte fiscale" },
      { n: s.galben, cls: "pct-galben", txt: "de urmărit" },
    ], "Toate firmele la zi");
  } catch {}
}


// Termene: sinteza din /termene (urmatoarea scadenta)
async function actualizeazaTermene(grila) {
  const zona = grila.querySelector('[data-cheie="termene"]');
  if (!zona) return;
  try {
    const r = await api.get("/termene");
    const u = r && r.urmatoarea;
    if (!u) { zona.innerHTML = "Nicio scadență apropiată"; return; }  // [p80_texte_scurte]
    const luni = ["ian","feb","mar","apr","mai","iun","iul","aug","sep","oct","noi","dec"];
    const p = u.termen.split("-");
    const dataTxt = `${parseInt(p[2])} ${luni[parseInt(p[1]) - 1]}`;
    zona.innerHTML = `Următoarea scadență: <b>${dataTxt}</b>`;
  } catch {}
}


// De validat: sinteza din /coada (cate sunt la_senior)
async function actualizeazaValidat(grila) {
  const zona = grila.querySelector('[data-cheie="validat"]');
  if (!zona) return;
  try {
    const r = await api.get("/coada");
    const coada = (r && r.coada) || [];
    const n = coada.filter((c) => c.stare === "la_senior").length;
    zona.innerHTML = `<b style="font-size:19px">${n}</b> declaraț${n === 1 ? "ie de validat" : "ii de validat"} și trimis`;
  } catch {}
}

async function actualizeazaAsistenti(grila) {
  const zona = grila.querySelector('[data-cheie="asistenti"]');
  if (!zona) return;
  try {
    const r = await api.get("/asistenti");
    const n = (r && r.sumar && r.sumar.activi) || 0;
    /* [patch10_card_sem] */
    let pastila = ""; let randuri = "";
    try {
      const sm = await api.get("/asistenti/echipa/semafor");
      if (sm && sm.ok) {
        const c = sm.counts || {rosu:0, galben:0, verde:0};
        const na = (c.rosu || 0) + (c.galben || 0);
        randuri = na === 0 ? "" : _semaforCard([
          { n: na, cls: c.rosu ? "pct-rosu" : "pct-galben", txt: na === 1 ? "activitate care necesită atenție" : "activități care necesită atenție" },
        ], "");
      }
    } catch {}
    zona.innerHTML = randuri || `<span class="cab-stare"><span class="cab-pct pct-verde"></span>Echipă activă</span>`;  // [p76_comasare_font]
    void n;
  } catch {}
}


// [p34_raporteaza] badge rosu pe cardul Raporteaza
async function actualizeazaRaportari(grila) {
  const card = grila.querySelector('[data-cheie="raport"]');
  const host = card ? card.closest(".cab-card") : null;
  if (!host) return;
  try {
    const r = await api.get("/raportari/contor");
    const n = (r && r.necitite) || 0;
    let b = host.querySelector(".cab-card-badge");
    if (n > 0) {
      if (!b) {
        b = document.createElement("span");
        b.className = "cab-card-badge";
        host.style.position = "relative";
        host.appendChild(b);
      }
      b.textContent = n;
    } else if (b) { b.remove(); }
  } catch {}
}


// [p51_edu] banner educatie patru-ochi (apare cand creste nr de validatori)
async function _educatiePatruOchi(continut) {  // [p55_decizie]
  let date;
  try { date = await api.get("/eu/educatie"); } catch { return; }
  const ed = (date.educatii || []).find((e) => e.cheie === "patru-ochi");
  if (!ed) return;
  const banner = document.createElement("div");
  banner.className = "edu-banner";
  banner.innerHTML = `
    <div class="edu-icon">i</div>
    <div class="edu-text">
      <div class="edu-titlu">Validare în doi (patru ochi)</div>
      <div class="edu-corp">Cabinetul are acum o persoană care pregătește și alta care poate valida. Poți activa validarea în doi: nimeni nu depune singur o declarație pe care a pregătit-o el însuși — o validează altcineva. Este protecția care nu te lasă să depui ce poate aduce control fiscal. O poți activa acum sau lăsa pe mai târziu.</div>
      <div class="edu-actiuni">
        <button class="edu-ok" id="edu-activ">Activează validarea în doi</button>
        <button class="edu-nu" id="edu-nu">Nu acum</button>
      </div>
    </div>
  `;
  continut.insertBefore(banner, continut.firstChild);
  banner.querySelector("#edu-activ").addEventListener("click", async () => {
    try { await api.post("/eu/patru-ochi", { activ: true }); } catch {}
    banner.remove();
  });
  banner.querySelector("#edu-nu").addEventListener("click", async () => {
    // "Nu acum": marcheaza vazut la nivelul curent; revine cand mai apare un validator
    try { await api.post("/eu/educatie/patru-ochi/vazut", {}); } catch {}
    banner.remove();
  });
}
// [p81_raport_text]


// ---------- CONSOLIDARE ----------  // consolidare_fe_v1
async function randeazaConsolidare(corp, nav) {
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103...</p>`;
  let d = null;
  try { d = await api.get("/cabinet/consolidare"); }
  catch (e) { corp.innerHTML = `<div class="mig-gol">${e.mesaj || e.message || "eroare"}</div>`; return; }
  const lei = (v) => (Number(v) || 0).toLocaleString("ro-RO", { maximumFractionDigits: 0 });
  const luni = ["", "ianuarie", "februarie", "martie", "aprilie", "mai", "iunie",
    "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie"];
  const cap = `
    <div class="pf-frand" style="font-weight:600">
      <div class="pf-frand-text" style="flex:2">Firma</div>
      <span style="flex:1;text-align:right">Venituri</span>
      <span style="flex:1;text-align:right">Cheltuieli</span>
      <span style="flex:1;text-align:right">Profit</span>
      <span style="flex:1;text-align:right">Cash</span>
    </div>`;
  const rand = (nume, k, bold) => `
    <div class="pf-frand" style="${bold ? "font-weight:700;border-top:2px solid #ccc" : ""}">
      <div class="pf-frand-text" style="flex:2">${nume}</div>
      <span style="flex:1;text-align:right">${k ? lei(k.venituri) : "\u2014"}</span>
      <span style="flex:1;text-align:right">${k ? lei(k.cheltuieli) : "\u2014"}</span>
      <span style="flex:1;text-align:right;${k && k.profit < 0 ? "color:#c0392b" : ""}">${k ? lei(k.profit) : "\u2014"}</span>
      <span style="flex:1;text-align:right">${k ? lei(k.cash) : "\u2014"}</span>
    </div>`;
  corp.innerHTML = `
    <h2 class="pf-titlu">Consolidare portofoliu</h2>
    <p class="pf-intro">Cumulat de la \u00eenceputul anului, p\u00e2n\u0103 la ${luni[d.luna]} ${d.an}. Valori \u00een lei.</p>
    <div class="pf-lista">
      ${cap}
      ${(d.firme || []).map((f) => rand(f.nume, f.kpi)).join("")}
      ${rand("TOTAL", d.total, true)}
    </div>`;
}

// cab_culori_v2
