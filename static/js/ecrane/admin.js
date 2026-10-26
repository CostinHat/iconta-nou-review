// admin.js — desktopul superadmin (Admin iConta).
// Spatiu separat de cabinet: doar functiile de administrare iConta.
// Acum: cardul Raportari (raspuns la sesizari). Extensibil (adaugi un dict in DEF).

import { sesiune } from "../sesiune.js?v=898215e0ee";
import { api, ultimaCerere, arataMesaj, dataRo, ICOANE, CULORI_CARD, esc, focusFaraSalt, cate, refuzPeRand, confirmaCaseta } from "../api.js?v=c6c45aefe4";
import { randeazaAdminRaportari } from "./admin_raportari.js?v=75ecec94e0";
import { randeazaAdminActivitate } from "./admin_activitate.js?v=0f96afcd4e";
import { randeazaAdminSanatate } from "./admin_sanatate.js?v=ad3794a4df";
import { randeazaAdminAnalytics, marcheazaSesiuneInterna } from "./admin_analytics.js?v=440f824e89";
import { numeDeSalut } from "./salut.js?v=f5a3ed7133";
import { panouNotificari } from "./setari.js?v=ae0ddd2b13";   // [17.10.2026, lotul 7] același panou ca în Setări cont   // [269] numele din salut, același loc ca pagina principală

// iconite SVG inline (autonome)
function svg(cheie, fg) {
  return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="${fg}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${ICOANE[cheie] || ""}</svg>`;
}

// cardurile panoului Admin iConta (extensibil)
const DEF = [
  { cheie:"raportari", titlu:"Raportări", icon:"solicitari", ...CULORI_CARD.violet,   // [05.10.2026] „report” nu mai e în ICOANE — desena gol
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
  // [14.10.2026, comanda Costin pct.3, verbatim în DECIZII „Lotul 2”] invitațiile; [15.10.2026, lotul 4 pct.5] a doua cale
  { cheie:"invitatii", titlu:"Invitații cabinete", icon: "mail", ...CULORI_CARD.verde,
    sinteza:"Contul unui cabinet adus de tine, creat din invitație",
    actiune:(nav) => nav.deschide("Invitații cabinete", (corp) => randeazaAdminInvitatii(corp)) },
  // [17.10.2026, lotul 7 pct.2.2–2.3] canalul notificărilor superadminului (sesizările, cererile de import, alertele legislative)
  { cheie:"notificari_cont", titlu:"Notificări", icon: "mail", ...CULORI_CARD.ardezie,
    sinteza:"Telefonul și canalul tău: email sau WhatsApp",
    actiune:(nav) => nav.deschide("Notificări", (corp) => panouNotificari(corp)) },
  // [15.10.2026, „Lotul 4” pct.6, verbatim în DECIZII] comutatorul înregistrării, fără publicare
  { cheie:"inregistrare", titlu:"Înregistrare", icon: "users", ...CULORI_CARD.albastru,
    sinteza:"Liberă, cu confirmarea emailului, sau numai prin invitație",
    actiune:(nav) => nav.deschide("Înregistrare", (corp) => randeazaAdminInregistrare(corp)) },
];

export function desktopAdmin(continut, nav) {
  marcheazaSesiuneInterna();   // [lotul 13, 649] vizitele publice din acest browser nu se numără cât sesiunea e deschisă
  const azi = dataRo(new Date(), "lung");
  const nume = numeDeSalut(sesiune.user());
  continut.innerHTML = `
    <div class="cab-salut">
      <div class="cab-salut-nume">${nume ? "Bună, " + esc(nume) : "Bună"}</div>
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
    card.dataset.deschide = c.cheie;   // [17.10.2026, lotul 7] ținta unei notificări (`navigator.deschideCheie`)
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
        box.innerHTML = `<div class="ca-mesaj">Rularea nu e la zi: serviciul rulează commitul <b>${esc((v.running || "").slice(0, 7))}</b>, dar HEAD e <b>${esc((v.head || "").slice(0, 7))}</b>. Codul publicat nu e cel care rulează. Repornește serviciul la o fereastră sigură (nu în mijlocul unei operații a unui contabil). Detectorul nu repornește nimic și nu repară nimic.</div>`;
        continut.insertBefore(box, continut.firstChild);
      }
    } catch {}
  })();
}


// admin_anunturi_fe_v1
// [lotul 13, deficiența 646 — anexa comenzii 13.1, decizia Costin 24.10.2026, verbatim: „(a) «Nimic bifat = anunțul merge la toți» e
// periculos: o bifă uitată trimite la toate cabinetele. Decis: bifă explicită «Toate cabinetele» sus; fără nicio bifă trimiterea e
// refuzată; înainte de trimitere confirmarea spune la câte cabinete pleacă. (b) Propunerile monitorului fiscal nu au data publicării și
// data intrării în vigoare. (c) Nu există lista anunțurilor trimise (către cine, citit sau nu, retragere).”]
async function randeazaAdminAnunturi(corp, nav) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  let cabinete = [];
  try {
    const r = await api.get("/admin/activitate/cabinete");
    cabinete = ((r && r.cabinete) || []).filter((c) => c.activ);   // anunțul ajunge numai la cabinetele active (cele suspendate nu intră)
  } catch {}
  // [anunturi_meniu_v1] DS cap.2a: optiunile se deschid ca pasi de navigator, nu inline
  const stare = window._anStare = window._anStare || { segment: null, cabIds: null };  // persistenta intre re-randari (mergi/inapoi re-executa radacina)
  const cateCabinete = () => stare.segment === "toate" ? cabinete.length : (stare.cabIds || []).length;
  const rezumat = () => {
    if (stare.segment === "toate") return `toate cabinetele (${cate(cabinete.length, "cabinet activ", "cabinete active")})`;
    if (stare.segment === "cabinete" && stare.cabIds && stare.cabIds.length) return cate(stare.cabIds.length, "cabinet ales", "cabinete alese");
    return "niciun destinatar ales";
  };
  const meniu = () => {
    if (nav.setInapoi) nav.setInapoi(undefined);
    corp.innerHTML = `
      <h2 class="pf-titlu">Anun\u021buri</h2>
      <p class="mig-intro">Mesajul apare la logare, p\u00e2n\u0103 la \u201eAm \u00een\u021beles\u201d. Alege destinatarii, apoi scrie mesajul.</p>
      <div class="firme-meniu">
        <button class="firme-optiune" id="an-op-cab">
          <div class="firme-optiune-icon accent-albastru"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 21h18M5 21V7l7-4 7 4v14M9 9h1M9 13h1M14 9h1M14 13h1"/></svg></div>
          <div class="firme-optiune-titlu">Destinatari</div>
          <div class="firme-optiune-desc">${esc(rezumat())}</div>
        </button>
        <button class="firme-optiune" id="an-op-msg">
          <div class="firme-optiune-icon accent-roz"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z"/></svg></div>
          <div class="firme-optiune-titlu">Mesaj</div>
          <div class="firme-optiune-desc">c\u0103tre: ${esc(rezumat())}</div>
        </button>
        <button class="firme-optiune" id="an-op-trimise">
          <div class="firme-optiune-icon accent-albastru"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h10"/></svg></div>
          <div class="firme-optiune-titlu">Anunțuri trimise</div>
          <div class="firme-optiune-desc">către cine, citit sau nu, retragere</div>
        </button>
      </div>
      <div id="an-propuneri"></div>`;
    corp.querySelector("#an-op-cab").addEventListener("click", () => nav.mergi("Destinatari", (c) => pasSelectie(c)));
    corp.querySelector("#an-op-msg").addEventListener("click", () => nav.mergi("Mesaj", (c) => pasMesaj(c)));
    corp.querySelector("#an-op-trimise").addEventListener("click", () => nav.mergi("Anunțuri trimise", (c) => pasTrimise(c)));
    propuneri();
  };
  // [F103 partea 2] propunerile monitorului fiscal ca anunțuri; [646 b] cu data publicării actului și data intrării în vigoare.
  // „Preia în mesaj” deschide pasul „Mesaj” cu textul propunerii (până azi căuta câmpul mesajului în meniu, unde nu e)
  async function propuneri() {
    const zona = corp.querySelector("#an-propuneri");
    if (!zona) return;
    let d = { alerte: [] };
    try { d = await api.get("/admin/alerte-fiscale"); } catch { return; }
    if (!d.alerte || !d.alerte.length || !zona.isConnected) return;
    const zi = (v) => v ? dataRo(v) : "nu apare în sursă";
    zona.innerHTML = `
      <h2 class="pf-titlu" style="margin-top:18px">Propuneri de la monitorul fiscal</h2>
      ${d.alerte.map((a) => `
        <div class="panou" style="margin-bottom:10px" data-alerta="${a.id}">
          <div><b>${esc(a.titlu)}</b>${a.relevanta === "mare" ? " \u00b7 relevan\u021b\u0103 mare" : ""}</div>
          <div class="tip-micut an-date-act">Publicat: ${zi(a.data_publicarii)} \u00b7 intră în vigoare: ${zi(a.data_vigoare)}</div>
          <div class="tip-mic" style="margin:4px 0">${esc(a.rezumat || "")}</div>
          <button class="buton-secundar buton-mic" data-id="${a.id}" data-actiune="POST /admin/alerte-fiscale/{aid}/tratat">Preia \u00een mesaj</button>
        </div>`).join("")}`;
    zona.querySelectorAll("button[data-id]").forEach((b) => b.addEventListener("click", async () => {
      const a = d.alerte.find((x) => String(x.id) === b.dataset.id);
      try { await api.post(`/admin/alerte-fiscale/${a.id}/tratat`, {}); } catch {}
      nav.mergi("Mesaj", (c) => pasMesaj(c, a.titlu + (a.rezumat ? "\n\n" + a.rezumat : "")));
    }));
  }
  function pasSelectie(c) {
    const idsCur = stare.cabIds || [];
    c.innerHTML = `
      <h2 class="pf-titlu">Destinatari</h2>
      <p class="mig-intro">Bifează «Toate cabinetele» sau cabinetele cărora le trimiți anunțul. Fără nicio bifă anunțul nu pleacă.</p>
      <label class="set-bifa" style="margin:0 0 10px"><input type="checkbox" id="an-toate" ${stare.segment === "toate" ? "checked" : ""}> <span><b>Toate cabinetele</b> (${cate(cabinete.length, "cabinet activ", "cabinete active")})</span></label>
      <input aria-label="Caută" type="text" class="camp-input" id="sel-cauta" placeholder="caut\u0103" style="max-width:340px;margin-bottom:10px">
      <div class="pf-lista zebra-lista" id="an-sel-lista">
        ${cabinete.map((x, i) => `<label class="pf-frand set-bifa sel-rand" data-zebra="${i % 2}" style="cursor:pointer;display:flex;align-items:center;gap:12px"><input type="checkbox" class="sel-bifa" value="${x.id}" ${idsCur.includes(x.id) ? "checked" : ""} style="flex-shrink:0">
          <div class="pf-frand-text" style="flex:1;text-align:left"><div class="pf-frand-nume">${esc(x.nume || "")}</div></div>
        </label>`).join("")}
      </div>`;
    c.querySelector("#sel-cauta").addEventListener("input", (e) => {
      const q = e.target.value.trim().toLowerCase();
      c.querySelectorAll(".sel-rand").forEach((r) => { r.style.display = !q || r.textContent.toLowerCase().includes(q) ? "" : "none"; });
    });
    const toate = c.querySelector("#an-toate");
    const salveaza = () => {  // [sel_direct_v1] bifarea E selectia; [646 a] fără nicio bifă = niciun destinatar (nu „toate”)
      const ids = [...c.querySelectorAll(".sel-bifa:checked")].map((b) => Number(b.value));
      c.querySelectorAll(".sel-bifa").forEach((b) => { b.disabled = toate.checked; });
      stare.segment = toate.checked ? "toate" : (ids.length ? "cabinete" : null);
      stare.cabIds = toate.checked ? null : ids;
    };
    toate.addEventListener("change", salveaza);
    c.querySelectorAll(".sel-bifa").forEach((b) => b.addEventListener("change", salveaza));
    salveaza();
  }
  function pasMesaj(c, textPropunere) {
    c.innerHTML = `
      <h2 class="pf-titlu">Mesaj</h2>
      <p class="mig-intro">C\u0103tre: <b id="an-catre">${esc(rezumat())}</b></p>
      <div class="camp" style="margin-bottom:10px"><label for="an-mesaj" class="camp-eticheta">Mesaj<span class="oblig">*</span></label>
        <textarea class="camp-input" id="an-mesaj" rows="4" style="resize:vertical;min-height:90px"></textarea></div>
      <div class="camp" style="margin-bottom:10px"><label for="an-data" class="camp-eticheta">Afi\u0219are de la data (op\u021bional \u2014 gol = imediat)</label>
        <input type="date" class="camp-input" id="an-data"></div>
      <div class="bara-fixa">
        <button class="buton-primar" id="an-trimite" data-actiune="POST /admin/anunturi">Trimite</button>
        <p id="an-msg" style="margin-top:8px"></p>
      </div>`;
    const ta = c.querySelector("#an-mesaj");
    ta.addEventListener("input", () => { ta.style.height = "auto"; ta.style.height = ta.scrollHeight + "px"; });
    if (textPropunere) { ta.value = textPropunere; ta.dispatchEvent(new Event("input")); }   // ales de om: „Preia în mesaj”
    const b = c.querySelector("#an-trimite");
    b.addEventListener("click", () => {
      const msg = c.querySelector("#an-msg");
      const mesaj = ta.value.trim();
      if (!mesaj) { arataMesaj(msg, "Scrie mesajul.", "eroare"); return; }
      if (!stare.segment) { arataMesaj(msg, "Alege destinatarii: bifează «Toate cabinetele» sau cabinetele cărora le trimiți anunțul.", "eroare"); return; }
      const n = cateCabinete();
      confirmaCaseta(b, `Anunțul pleacă la ${esc(cate(n, "cabinet", "cabinete"))}${stare.segment === "toate" ? " (toate cabinetele active)" : ""}. Trimiți?`, async () => {
        try {
          const r = await api.post("/admin/anunturi", { mesaj, segment: stare.segment, cabinet_ids: stare.segment === "cabinete" ? stare.cabIds : null,
                                                       cabinet_id: null, data_afisare: c.querySelector("#an-data").value || null });
          arataMesaj(msg, `Trimis c\u0103tre ${cate(r.trimise, "cabinet", "cabinete")}. Îl găsești în «Anunțuri trimise».`, "ok");
          ta.value = "";
        } catch (e) { arataMesaj(msg, (e && e.mesaj) || "Anunțul nu s-a putut trimite.", "eroare"); }
      }, { textOk: "Trimite" });
    });
  }
  async function pasTrimise(c) {
    c.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
    let lst = [];
    try { lst = ((await api.get("/admin/anunturi")) || {}).trimiteri || []; } catch (e) {
      c.innerHTML = `<p class="ecran-nota pe-randuri">${esc((e && e.mesaj) || "Lista anunțurilor nu se poate încărca.")}</p>`; return;
    }
    if (!lst.length) { c.innerHTML = `<h2 class="pf-titlu">Anunțuri trimise</h2><div class="stare-goala">Niciun anunț trimis încă.</div>`; return; }
    c.innerHTML = `<h2 class="pf-titlu">Anunțuri trimise</h2>
      <div class="rezumat-fix"><div id="an-trimise-msg"></div></div>
      <table class="fd-tabel" id="an-trimise"><thead><tr><th>Trimis</th><th>Mesaj</th><th>Către</th><th class="fd-td-num">Citit</th><th>Stare</th><th>Acțiuni</th></tr></thead><tbody>
      ${lst.map((t) => `<tr data-lot="${t.lot}"><td>${dataRo(t.creat_la, "cu_ora")}${t.data_afisare ? `<div class="tip-micut">afișat de la ${dataRo(t.data_afisare)}</div>` : ""}${t.trimis_de ? `<div class="tip-micut">de ${esc(t.trimis_de)}</div>` : ""}</td>
        <td>${esc(t.text_anunt || "")}</td><td>${esc(cate(t.destinatari, "cabinet", "cabinete"))}</td><td class="fd-td-num">${t.citite} din ${t.destinatari}</td>
        <td>${t.retras_la ? `retras ${dataRo(t.retras_la, "cu_ora")}` : "activ"}</td>
        <td><button class="buton-secundar buton-mic" data-dest="${t.lot}" data-fara-actiune="lista destinatarilor (citire)">Destinatari</button>
          <button class="buton-sters buton-mic" data-retrage="${t.lot}" data-actiune="POST /admin/anunturi/{lot}/retrage" ${t.retras_la ? `disabled title="Anunțul e retras deja."` : (t.citite === t.destinatari ? `disabled title="L-au citit toate cabinetele: nu mai are cui să fie retras."` : "")}>Retrage</button></td></tr>`).join("")}
      </tbody></table>`;
    c.querySelectorAll("[data-dest]").forEach((b) => b.addEventListener("click", () => {
      const t = lst.find((x) => String(x.lot) === b.dataset.dest);
      nav.deschide("Destinatarii anunțului", (cd) => {
        cd.innerHTML = `<h2 class="pf-titlu">Destinatarii anunțului</h2><div class="rezumat-fix"><p class="pf-intro">${esc(t.text_anunt || "")} · citit de ${t.citite} din ${t.destinatari}</p></div>
          <table class="fd-tabel" id="an-destinatari"><thead><tr><th>Cabinet</th><th>Citit</th></tr></thead><tbody>
          ${t.cabinete.map((d) => `<tr><td>${esc(d.cabinet)}</td><td>${d.citit_la ? `citit ${dataRo(d.citit_la, "cu_ora")}` : "necitit"}</td></tr>`).join("")}
          </tbody></table>`;
      });
    }));
    c.querySelectorAll("[data-retrage]").forEach((b) => b.addEventListener("click", () => {
      const t = lst.find((x) => String(x.lot) === b.dataset.retrage);
      confirmaCaseta(b, `Retragi anunțul? Necitit e la ${esc(cate(t.destinatari - t.citite, "cabinet", "cabinete"))}; după retragere nu-l mai vede niciunul.`, async () => {
        try {
          await api.post(`/admin/anunturi/${t.lot}/retrage`, {});
          await pasTrimise(c);
          arataMesaj(c.querySelector("#an-trimise-msg"), "Anunțul e retras.", "ok");
        } catch (e) { refuzPeRand(b, (e && e.mesaj) || "Anunțul nu s-a putut retrage."); }
      }, { textOk: "Retrage" });
    }));
  }
  meniu();
}
// [14.10.2026, comanda Costin pct.3] Invitațiile: emailul invitat primește linkul (14 zile, o singură folosire). Linkul se arată
// o singură dată, aici, ca superadminul să-l poată da direct dacă emailul nu ajunge.
async function randeazaAdminInvitatii(corp) {
  corp.innerHTML = `
    <h2 class="pf-titlu">Invitații cabinete</h2>
    <p class="pf-intro">Invitația creează contul unui cabinet adus de tine, oricum ar fi setată înregistrarea (cardul „Înregistrare”). E valabilă 14 zile și se folosește o singură dată, numai cu emailul invitat.</p>
    <div class="rezumat-fix">   <!-- [lotul 10, 421 / 424, DS cap.9 v2.97 pct.5-6] invitația nouă și mesajul ei rămân sus cât derulezi lista -->
    <label class="camp" style="max-width:420px"><span class="camp-eticheta">Email cabinet <span class="oblig">*</span></span>
      <input type="email" id="inv-email" class="camp-input" autocomplete="off" placeholder="nume@cabinet.ro"></label>
    <button class="buton-primar" id="inv-trimite" data-actiune="POST /admin/invitatii">Trimite invitația</button>
    <div id="inv-msg" style="margin-top:10px"></div>
    </div>
    <div id="inv-lista" style="margin-top:16px"></div>`;
  const lista = corp.querySelector("#inv-lista");
  // [lotul 13, găsită la e2e: încărcarea de la deschidere, lentă, sosea DUPĂ cea de după „Trimite invitația” și redesena lista peste
  // întrebarea „Retragi invitația?” deja deschisă] numai ultima cerere a listei ajunge pe ecran (C103)
  const ultimaLista = ultimaCerere(lista);
  async function incarca() {
    const actuala = ultimaLista();
    try {
      const r = await api.get("/admin/invitatii");
      if (!actuala()) return;
      const v = (r && r.invitatii) || [];
      // [lotul 13, 646 e] starea fiecărei invitații și „Retrage” pe cea încă valabilă (inactiv, cu motivul, pe celelalte — 675)
      const motivNu = { "folosită": "Invitația a fost folosită: contul cabinetului există.", "retrasă": "Invitația e retrasă deja.",
                        "expirată": "Invitația a expirat: linkul ei nu mai creează cont." };
      lista.innerHTML = v.length ? `<table class="fd-tabel" id="inv-tabel"><thead><tr><th>Email</th><th>Trimisă</th><th>Expiră</th><th>Folosită</th><th>Stare</th><th>Acțiune</th></tr></thead><tbody>
        ${v.map((x) => `<tr data-invitatie="${x.id}"><td>${esc(x.email)}</td><td>${dataRo(x.creat_la, "cu_ora")}</td><td>${dataRo(x.expira_la, "cu_ora")}</td><td>${x.folosita_la ? dataRo(x.folosita_la, "cu_ora") : "—"}</td>
          <td>${esc(x.stare || "")}${x.retrasa_la ? " " + dataRo(x.retrasa_la, "cu_ora") : ""}</td>
          <td><button class="buton-sters buton-mic" data-retrage-inv="${x.id}" data-actiune="POST /admin/invitatii/{invitatie_id}/retrage"${x.stare !== "valabilă" ? ` disabled title="${esc(motivNu[x.stare] || "")}"` : ""}>Retrage</button></td></tr>`).join("")}
        </tbody></table>` : `<div class="stare-goala">Nicio invitație trimisă încă. Scrie emailul cabinetului mai sus și apasă „Trimite invitația”.</div>`;
      lista.querySelectorAll("[data-retrage-inv]").forEach((b) => b.addEventListener("click", () => {
        const x = v.find((y) => String(y.id) === b.dataset.retrageInv);
        confirmaCaseta(b, `Retragi invitația pentru ${esc(x.email)}? Linkul ei nu mai creează cont.`, async () => {
          try {
            await api.post(`/admin/invitatii/${x.id}/retrage`, {});
            await incarca();
            arataMesaj(corp.querySelector("#inv-msg"), `Invitația pentru ${x.email} e retrasă.`, "ok");
          } catch (e) { refuzPeRand(b, (e && e.mesaj) || "Invitația nu s-a putut retrage."); }
        }, { textOk: "Retrage" });
      }));
    } catch (e) { if (actuala()) arataMesaj(lista, (e && e.mesaj) || "Lista invitațiilor nu se poate încărca.", "eroare"); }
  }
  corp.querySelector("#inv-trimite").addEventListener("click", async () => {
    const msg = corp.querySelector("#inv-msg");
    const email = corp.querySelector("#inv-email").value.trim();
    if (!email) { arataMesaj(msg, "Scrie emailul cabinetului invitat.", "eroare"); return; }
    const b = corp.querySelector("#inv-trimite");
    b.disabled = true; b.textContent = "Se trimite…";
    try {
      const r = await api.post("/admin/invitatii", { email });
      const [cls, m] = r.email_trimis ? ["caseta-info", "ci-mesaj"] : ["caseta-atentie", "ca-mesaj"];   // emailul netrimis = atenție
      msg.innerHTML = `<div class="${cls}" id="inv-rezultat"><div class="${m}">${r.email_trimis ? `Invitația a plecat pe <b>${esc(r.email)}</b>.` : `Emailul către <b>${esc(r.email)}</b> nu s-a putut trimite — dă-i linkul de mai jos direct.`} Linkul (valabil ${cate(r.valabila_zile, "zi", "zile")}, o singură folosire):</div>
        <div class="camp-cu-buton" style="display:flex;gap:8px;margin-top:6px"><input type="text" class="camp-input" id="inv-link" readonly aria-label="Linkul invitației" value="${esc(r.link)}" style="flex:1 1 auto;min-width:0">
          <button type="button" class="buton-secundar" id="inv-copiaza" data-fara-actiune="copiază linkul în memoria browserului">Copiază</button></div>
        <span class="tip-micut" id="inv-copiat" role="status"></span></div>`;
      // [lotul 13, 646 e] „lipsesc «Copiază» lângă link”: linkul se arată o singură dată (în bază stă numai hash-ul lui)
      corp.querySelector("#inv-copiaza").addEventListener("click", async () => {
        const st = corp.querySelector("#inv-copiat");
        try { await navigator.clipboard.writeText(r.link); st.textContent = "Linkul e copiat."; }
        catch { corp.querySelector("#inv-link").select(); st.textContent = "Browserul nu permite copierea automată: linkul e selectat, apasă Ctrl+C."; }
      });
      corp.querySelector("#inv-email").value = "";
      await incarca();
    } catch (e) {
      arataMesaj(msg, (e && e.mesaj) || "Invitația nu s-a putut crea.", "eroare");
    }
    b.disabled = false; b.textContent = "Trimite invitația";
  });
  await incarca();
}


// [deficiența 282, comanda Costin 16.10.2026, verbatim în DECIZII] „Cardul «Înregistrare» le listează: data, denumirea cabinetului,
// emailul, dacă emailul de confirmare a plecat și când expiră linkul, cu acțiunea «Retrimite confirmarea».”
// [C103] contor pe modul: lista e chemată numai din ecranul „Înregistrare” (unul singur, fereastra de sus); retrimiterile pe rânduri
// diferite în șir: numai lista ultimei cereri ajunge pe ecran
const cerereNoua = ultimaCerere();
async function cereriNeconfirmate(zona) {
  const actuala = cerereNoua();
  let r;
  try { r = await api.get("/admin/inregistrari-neconfirmate"); if (!actuala()) return; } catch (e) {
    if (!actuala()) return;
    arataMesaj(zona, (e && e.mesaj) || "Cererile neconfirmate nu se pot încărca.", "eroare");
    return;
  }
  const v = r.cereri || [];
  if (!v.length) { zona.innerHTML = `<div class="stare-goala">Nicio cerere neconfirmată.</div>`; return; }
  const trimis = (x) => x.email_trimis_la
    ? `trimis ${dataRo(x.email_trimis_la, "cu_ora")}${x.retrimiteri ? ` (${cate(x.retrimiteri, "retrimitere", "retrimiteri")})` : ""}` : "netrimis";
  // [deficiența 316, comanda Costin 17.10.2026 7.2] cererea expirată rămâne în listă, marcată „expirată” (cu data la care se șterge);
  // data, emailul și butonul nu se mai rup pe rânduri (`.ins-cereri`, fără `overflow-wrap: anywhere` pe coloanele lor)
  // [lotul 11, decizia Costin 10.3: „rezumatul fix, mesajele lângă buton […]: da, reorganizezi ecranele”] confirmarea lui „Retrimite
  // confirmarea” stătea SUB tabelul cererilor; acum zona ei e rezumatul lipit sus al tabelului (refuzul rămâne pe rând, `refuzPeRand`)
  zona.innerHTML = `<div class="rezumat-fix" id="ins-cereri-msg"></div><table class="fd-tabel ins-cereri"><thead><tr><th>Data</th><th>Cabinet</th><th>Email</th><th>Emailul de confirmare</th><th>Starea linkului</th><th>Acțiune</th></tr></thead><tbody>
    ${v.map((x) => `<tr data-cerere="${x.id}"${x.expirata ? ' class="ins-expirata"' : ""}><td class="ins-nerupt">${dataRo(x.creat_la, "cu_ora")}</td><td>${esc(x.nume_cabinet)}</td><td class="ins-nerupt">${esc(x.email)}</td>
      <td>${trimis(x)}</td><td>${x.expirata ? `<b>expirată</b> pe ${dataRo(x.expira_la, "cu_ora")} · se șterge pe ${dataRo(x.se_sterge_la)}` : `valabilă până la ${dataRo(x.expira_la, "cu_ora")}`}</td>
      <td class="ins-nerupt"><button class="buton-secundar" data-retrimite="${x.id}" data-actiune="POST /admin/inregistrari-neconfirmate/{cerere_id}/retrimite">Retrimite confirmarea</button></td></tr>`).join("")}
    </tbody></table>`;
  zona.querySelectorAll("[data-retrimite]").forEach((b) => b.addEventListener("click", async () => {
    b.disabled = true;
    try {
      const x = await api.post(`/admin/inregistrari-neconfirmate/${b.dataset.retrimite}/retrimite`, {});
      await cereriNeconfirmate(zona);
      arataMesaj(zona.querySelector("#ins-cereri-msg"), `Confirmarea a plecat din nou pe ${x.email}: link nou, valabil ${cate(x.valabila_ore, "oră", "ore")}.`, "ok");
    } catch (e) { b.disabled = false; refuzPeRand(b, (e && e.mesaj) || "Confirmarea nu s-a putut retrimite."); }
  }));
}

// [15.10.2026, „Lotul 4” pct.6, verbatim în DECIZII] „Comutator în Panou Admin: «Înregistrare: liberă, cu confirmarea emailului /
// numai prin invitație», ca să o pot schimba eu fără publicare.” Valoarea stă în baza de date (`setari_platforma`), nu în cod.
async function randeazaAdminInregistrare(corp) {
  corp.innerHTML = `<h2 class="pf-titlu">Înregistrare</h2><p class="ecran-nota">Se încarcă…</p>`;
  let st;
  try { st = await api.get("/admin/setari/inregistrare"); } catch (e) {
    corp.innerHTML = `<h2 class="pf-titlu">Înregistrare</h2><p class="ecran-nota pe-randuri">${esc((e && e.mesaj) || "Setarea nu se poate încărca.")}</p>`;
    return;
  }
  const deseneaza = () => {
    corp.innerHTML = `
      <h2 class="pf-titlu">Înregistrare</h2>
      <p class="pf-intro">Cum își creează contul un cabinet nou. Schimbarea se aplică imediat, fără publicare. Invitațiile (cardul „Invitații cabinete”) funcționează în ambele moduri.</p>
      <fieldset class="camp" id="ins-moduri" style="border:0;padding:0;margin:0 0 12px">
        <legend class="camp-eticheta">Înregistrare</legend>
        ${st.moduri.map((m) => `<label class="set-bifa"><input type="radio" name="ins-mod" value="${esc(m.mod)}" ${m.mod === st.mod ? "checked" : ""}> <span>${esc(m.eticheta)}</span></label>`).join("")}
      </fieldset>
      ${st.mod === "libera" && !st.email_functional ? `<div class="caseta-atentie" id="ins-fara-email"><div class="ca-mesaj">Emailul nu poate pleca acum, deci înregistrarea liberă rămâne închisă: ${esc((st.refuz && st.refuz.motiv) || "")}</div></div>` : ""}
      <p class="ecran-nota" id="ins-stare">Acum: ${esc(st.eticheta)}${st.modificat_la ? ` · schimbat${st.modificat_de ? " de " + esc(st.modificat_de) : ""} la ${dataRo(st.modificat_la, "cu_ora")}` : ""}.</p>
      <button class="buton-primar" id="ins-salveaza" data-actiune="PUT /admin/setari/inregistrare">Salvează</button>
      <div id="ins-msg" style="margin-top:10px"></div>
      <h3 class="pf-subtitlu" style="margin-top:22px">Cereri neconfirmate</h3>
      <p class="pf-intro">Cabinetele care s-au înregistrat și n-au apăsat încă linkul din email. Contul se creează abia la confirmare. „Retrimite confirmarea” trimite un link nou, valabil din nou; cel vechi nu mai merge.</p>
      <div id="ins-cereri"><p class="ecran-nota">Se încarcă…</p></div>`;
    cereriNeconfirmate(corp.querySelector("#ins-cereri"));
    corp.querySelector("#ins-salveaza").addEventListener("click", async () => {
      const ales = corp.querySelector("input[name='ins-mod']:checked");
      const msg = corp.querySelector("#ins-msg");
      if (!ales) { arataMesaj(msg, "Alege unul din cele două moduri.", "eroare"); return; }
      const b = corp.querySelector("#ins-salveaza");
      b.disabled = true; b.textContent = "Se salvează…";
      try {
        st = await api.put("/admin/setari/inregistrare", { mod: ales.value });
        deseneaza();
        arataMesaj(corp.querySelector("#ins-msg"), `Înregistrarea e acum: ${st.eticheta}.`, "ok");
      } catch (e) {
        b.disabled = false; b.textContent = "Salvează";
        arataMesaj(msg, (e && e.mesaj) || "Setarea nu s-a putut salva.", "eroare");
      }
    });
  };
  deseneaza();
}
