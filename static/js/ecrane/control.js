// control.js — ecranul Control fiscal (semafor conformare portofoliu + drill-down).
// Nivel 1: lista firmelor cu pastila colorata (verde/galben/rosu).
// Nivel 2: click pe firma -> declaratiile lipsa + de urmarit, cu termene.

import { api, esc, dataRo, confirmaCaseta, arataMesaj } from "../api.js";  /* esc_nc27 */

const CULORI = {
  verde:  { dot:"radial-gradient(circle at 65% 30%, #6fc494, #1d7a4d 60%)", txt:"la zi",       bg:"var(--verde-fundal)" },
  galben: { dot:"radial-gradient(circle at 65% 30%, #f0cd7a, #c9961f 60%)", txt:"de urmărit",  bg:"var(--galben-fundal)" },
  rosu:   { dot:"radial-gradient(circle at 65% 30%, #ff8a80, var(--rosu-semafor) 60%)", txt:"restanță",    bg:"var(--rosu-fundal)" },
  gri:    { dot:"var(--gri-semafor)", txt:"necompletat", bg:"var(--gri-fundal-semafor)" },
};
const LUNI = ["", "ian", "feb", "mar", "apr", "mai", "iun", "iul", "aug", "sep", "oct", "noi", "dec"];


export async function randeazaControl(corp, nav, tidAuto) {
  corp.innerHTML = `<p class="ecran-nota">Se evaluează portofoliul…</p>`;
  let date = { firme: [], sumar: {} };
  try {
    date = await api.get("/control-fiscal");
  } catch (e) {
    corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca controlul fiscal.</p>`;
    return;
  }
  const firme = date.firme || [];
  const s = date.sumar || {};

  corp.innerHTML = `
    <p class="mig-intro">Starea fiscală a fiecărei firme: ce s-a depus vs ce e datorat, cu termenele ANAF.</p>
    <div class="cf-sumar">
      <span class="cf-pastila"><span class="cf-dot" style="background:${CULORI.verde.dot}"></span>${s.verde || 0} la zi</span>
      <span class="cf-pastila"><span class="cf-dot" style="background:${CULORI.galben.dot}"></span>${s.galben || 0} de urmărit</span>
      <span class="cf-pastila"><span class="cf-dot" style="background:${CULORI.rosu.dot}"></span>${s.rosu || 0} cu restanță</span>
    </div>
    <div class="mig-lista" id="cf-lista"></div>
  `;

  const lista = corp.querySelector("#cf-lista");
  if (firme.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio firmă în portofoliu încă.</div>`;
    return;
  }
  // sortare: rosu intai, apoi galben, apoi verde
  const ord = { rosu: 0, galben: 1, verde: 2, gri: 3 };
  firme.sort((a, b) => (ord[a.stare] ?? 9) - (ord[b.stare] ?? 9));

  firme.forEach((f) => {
    const col = CULORI[f.stare] || CULORI.gri;
    let detaliu = f.stare === "rosu" ? `${f.lipsa} restanț${f.lipsa === 1 ? "ă" : "e"}`
      : f.stare === "galben" ? `${f.urmarit} de urmărit`
      : f.stare === "verde" ? "totul la zi" : "vector necompletat";
    if ((f.contabil || []).length) detaliu += " \u00b7 " + f.contabil.map((c) => (c && c.eticheta) || c).join(" \u00b7 ");
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${detaliu}</div>
      </div>
      <span class="cf-stare" style="background:${col.bg}">
        <span class="cf-dot" style="background:${col.dot}"></span>${col.txt}
      </span>
    `;
    rand.addEventListener("click", () => nav.deschide("Detaliu firm\u0103", (cc, nn) => detaliuFirma(cc, nn, f)));  // [p122_nav_stiva]
    lista.appendChild(rand);
  });

  // [F164_routing] deschis din notificarea de control fiscal (link control-fiscal:{tid}) -> auto-drill in
  // detaliul FIRMEI, reutilizand exact click-ul de rand (acelasi obiect firma: nume+contabil, aceeasi stiva
  // portofoliu->detaliu). Firma negasita (fara acces / tid gresit) -> ramai pe portofoliu, nu crapa.
  if (tidAuto != null) {
    const f = firme.find((x) => x.tenant_id === tidAuto);
    if (f) nav.deschide("Detaliu firm\u0103", (cc, nn) => detaliuFirma(cc, nn, f));
    else console.warn("[control] firma", tidAuto, "negasita in portofoliu (fara acces sau tid gresit)");
  }
}

async function detaliuFirma(corp, nav, firma) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;

  let d = { lipsa: [], urmarit: [] };
  try {
    d = await api.get(`/control-fiscal/${firma.tenant_id}`);
  } catch {}

  const lipsa = d.lipsa || [];
  const urmarit = d.urmarit || [];
  const confirmate = d.confirmate || [];
  const neclar = d.neclar || [];
  const neaplicabile = d.neaplicabile || [];
  const col = CULORI[d.stare] || CULORI.gri;

  // [semafor_b_v1] fiecare declaratie poarta MOTIVUL (temei), pe orice culoare - aliniat cu
  // sectiunea Declaratie vs contabilitate (cf-incr-temei). Decizie DECIZII 18.07 B.
  const randDecl = (arr, clasa) => arr.map((x) => `
    <div class="cf-decl-item">
      <div class="mig-sold-rand cf-rand-decl">
        <span class="mig-sold-cont">${(x.tip||"").toUpperCase()}</span>
        <span class="cf-perioada">${x.perioada}</span>
        <span class="cf-termen ${clasa}">termen ${dataRo(x.termen)}</span>
      </div>
      ${x.motiv ? `<div class="cf-incr-temei">${esc(x.motiv)}</div>` : ""}
    </div>`).join("");
  const randMotiv = (arr) => arr.map((x) => `
    <div class="cf-decl-item">
      <div class="cf-incr-cap"><span class="mig-sold-cont">${esc((x.tip||"").toUpperCase())}</span></div>
      <div class="cf-incr-temei">${esc(x.motiv || "")}</div>
    </div>`).join("");

  // [F183/verdict] renderer UNIC de anatomie constatare (dot + mesaj + temei + remediu) — folosit de
  // «Verificări contabile» ȘI de auditul de preluare. Fără cale paralelă de randare (bare-label eliminat).
  const randA = (c) => {
    const dot = CULORI[c.stare] ? CULORI[c.stare].dot : CULORI.gri.dot;
    const r = c.remediu;
    const extra = r ? `<div class="cf-incr-remediu"><b>${esc(r.cauza || "")}</b><br>${esc(r.actiune || "")}</div>` : "";
    return `<div class="cf-incr-rand">
      <div class="cf-incr-cap"><span class="cf-dot" style="background:${dot}"></span><span>${esc(c.mesaj || "")}</span></div>
      <div class="cf-incr-temei">${esc(c.temei || "")}</div>
      ${extra}
    </div>`;
  };

  corp.innerHTML = `
    <p class="mig-intro"><b>${esc(firma.nume)}</b> · <span style="color:${col.dot}">${col.txt}</span></p>
    ${lipsa.length ? `
      <div class="cf-grup-titlu cf-rosu">Restanțe (${lipsa.length})</div>
      <div class="cf-decl">${randDecl(lipsa, "cf-termen-rosu")}</div>` : ""}
    ${urmarit.length ? `
      <div class="cf-grup-titlu cf-galben">De urmărit (${urmarit.length})</div>
      <div class="cf-decl">${randDecl(urmarit, "cf-termen-galben")}</div>` : ""}
    ${confirmate.length ? `
      <div class="cf-grup-titlu cf-verde">La zi (${confirmate.length})</div>
      <div class="cf-decl">${randDecl(confirmate, "cf-termen-verde")}</div>` : ""}
    ${neclar.length ? `
      <div class="cf-grup-titlu">Nu pot verifica (${neclar.length})</div>
      <div class="cf-decl">${randMotiv(neclar)}</div>` : ""}
    ${neaplicabile.length ? `
      <div class="cf-grup-titlu">Nu se datorează (${neaplicabile.length})</div>
      <div class="cf-decl">${randMotiv(neaplicabile)}</div>` : ""}
    ${(() => { /* [control_incrucisat_v1 + F163_ui] declaratie vs contabilitate: TVA + D112 + D390,
        aceeasi anatomie (dot + mesaj + temei + remediu + limita), sub un singur grup. Gri se AFISEAZA
        gri (nu ascuns) - filozofia control_incrucisat: gri e informatie, nu absenta. */
      const vc = d.verificari_contabile || {};
      const verificatori = [vc.tva_incrucisat, vc.d112_incrucisat, vc.d390_incrucisat].filter(Boolean);
      const cuFinding = verificatori.filter((v) => (v.constatari || []).length);
      if (!cuFinding.length) return "";
      const rang = { rosu: 3, galben: 2, gri: 1, verde: 0 };
      const worst = cuFinding.reduce((m, v) => ((rang[v.stare] || 0) > (rang[m] || 0) ? v.stare : m), "verde");
      const clsTitlu = worst === "rosu" ? "cf-rosu" : (worst === "galben" ? "cf-galben" : "");
      const randConst = (c) => {
        const dot = CULORI[c.stare] ? CULORI[c.stare].dot : CULORI.gri.dot;
        let extra = "";
        if (c.remediu) {
          const r = c.remediu;
          const buton = (r.fel === "executabil" && (r.facturi || []).length)
            ? `<button class="buton-secundar cf-incr-btn" data-facturi="${esc((r.facturi || []).join(","))}"
                 style="margin-top:8px">Contabilizeaz\u0103 facturile</button>` : "";
          extra = `<div class="cf-incr-remediu"><b>${esc(r.cauza || "")}</b><br>${esc(r.actiune || "")}${buton ? `<div>${buton}</div>` : ""}</div>`;
        }
        return `<div class="cf-incr-rand">
          <div class="cf-incr-cap"><span class="cf-dot" style="background:${dot}"></span><span>${esc(c.mesaj || "")}</span></div>
          <div class="cf-incr-temei">${esc(c.temei || "")}</div>
          ${extra}
        </div>`;
      };
      const blocuri = cuFinding.map((v) =>
        (v.constatari || []).map(randConst).join("")
        + (v.limita ? `<div class="cf-incr-temei">${esc(v.limita)}</div>` : "")
      ).join("");
      return `<div class="cf-grup-titlu ${clsTitlu}">Declarație vs contabilitate</div>
        <div class="cf-decl">${blocuri}</div>`;
    })()}
    ${(() => { /* [F184] conformitate cota TVA facturi emise — grup SEPARAT (nu declaratie-vs-contabilitate,
        ci verificare de conformitate a facturilor emise cu cota standard pe perioada). Aceeasi anatomie. */
      const cf = (d.verificari_contabile || {}).cota_tva_conformitate;
      if (!cf || !(cf.constatari || []).length) return "";
      const clsT = cf.stare === "rosu" ? "cf-rosu" : (cf.stare === "gri" ? "" : "");
      const randuri = (cf.constatari || []).map((c) => {
        const dot = CULORI[c.stare] ? CULORI[c.stare].dot : CULORI.gri.dot;
        let extra = "";
        if (c.remediu) {
          const r = c.remediu;
          extra = `<div class="cf-incr-remediu"><b>${esc(r.cauza || "")}</b><br>${esc(r.actiune || "")}</div>`;
        }
        return `<div class="cf-incr-rand">
          <div class="cf-incr-cap"><span class="cf-dot" style="background:${dot}"></span><span>${esc(c.mesaj || "")}</span></div>
          <div class="cf-incr-temei">${esc(c.temei || "")}</div>
          ${extra}
        </div>`;
      }).join("");
      const limita = cf.limita ? `<div class="cf-incr-temei">${esc(cf.limita)}</div>` : "";
      return `<div class="cf-grup-titlu ${clsT}">Conformitate facturi emise</div>
        <div class="cf-decl">${randuri}${limita}</div>`;
    })()}
    ${(() => { /* cf_detaliu_contabil_v3: constatari STRUCTURATE din portofoliu (firma.contabil = {stare,
        eticheta, mesaj, temei, remediu}), randate prin randA — dot + mesaj + TEMEI + remediu, nu bare-label.
        Cross-check-urile D-vs-contabilitate apar deja in «Declaratie vs contabilitate» -> filtrate dupa
        eticheta ca sa nu se dubleze. (Reparatie clasa BACKEND_UI_BRUT/verdict: temeiul nu se mai pierde.) */
      const dejaInIncrucisat = ["TVA declarat diferă de contabilitate", "Salarii declarate diferă de contabilitate", "Operațiuni intracomunitare declarate diferă de evidență", "Facturi emise cu cotă TVA greșită pentru perioadă"];
      // d.contabil = calcul PROASPAT din detaliu (aceeasi functie ca lista, aceeasi severitate ca headerul);
      // firma.contabil = snapshot din lista, doar fallback. Asa headerul si aceste constatari NU se contrazic.
      const items = ((d.contabil || firma.contabil) || []).filter((c) => c && typeof c === "object" && !dejaInIncrucisat.includes(c.eticheta));
      if (!items.length) return "";
      const rang = { rosu: 3, galben: 2, gri: 1, verde: 0 };
      const worst = items.reduce((m, c) => ((rang[c.stare] || 0) > (rang[m] || 0) ? c.stare : m), "verde");
      const clsTitlu = worst === "rosu" ? "cf-rosu" : (worst === "galben" ? "cf-galben" : "");
      return `<div class="cf-grup-titlu ${clsTitlu}">Verificări contabile (${items.length})</div>
        <div class="cf-decl">${items.map(randA).join("")}</div>`;
    })()}
    ${d.stare === "verde" ? `
      <div class="mig-gata" style="padding:30px 0">
        <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
        <div class="mig-gata-titlu">Totul depus la zi</div>
      </div>` : ""}
    <div class="cf-grup-titlu" style="margin-top:20px">Audit de preluare</div>
    <div class="cf-decl" id="cf-audit-zona">
      <div class="cf-incr-temei">Coerența internă a pachetului preluat de la contabilul anterior:
        balanță, solduri parteneri, istoric declarații, registru PFA. Raport datat, repetabil pe
        măsură ce apar documentele.</div>
      <button class="buton-secundar" id="cf-audit-run" style="margin-top:10px">Rulează auditul de preluare</button>
    </div>
  `;

  // [control_incrucisat_v1] remediu executabil: contabilizeaza facturile cu cauza dovedita.
  // Notele se creeaza CIORNA (endpoint existent) -> patru-ochi ramane intact.
  corp.querySelectorAll(".cf-incr-btn").forEach((b) => b.addEventListener("click", () => {
    const ids = (b.dataset.facturi || "").split(",").filter(Boolean);
    if (!ids.length) return;
    confirmaCaseta(b.parentElement,
      `Se creeaz\u0103 ${ids.length} note contabile ciorn\u0103. Continui?`,
      async () => {
        b.disabled = true;
        b.textContent = "Se contabilizeaz\u0103\u2026";
        let ok = 0;
        const err = [];
        for (const id of ids) {
          try {
            await api.post(`/tenants/${firma.tenant_id}/facturi/${id}/contabilizeaza`, {});
            ok++;
          } catch (e) {
            err.push(`${id}: ${e.mesaj || e.message}`);
          }
        }
        if (err.length) {
          b.disabled = false;
          b.textContent = "Contabilizeaz\u0103 facturile";
          arataMesaj(b.parentElement, `${ok} contabilizate. Erori: ${err.join("; ")}`, "avert");
        } else {
          detaliuFirma(corp, nav, firma);  // reincarca: constatarea trece pe verde
        }
      }, { textOk: "Contabilizeaz\u0103" });
  }));

  // [F183] audit de preluare \u2014 ruleaza la cerere (repetabil, datat), randeaza cele trei categorii
  // reutilizand randA (renderer unic de anatomie, definit mai sus). Motor separat pe backend.
  async function ruleazaAudit() {
    const zona = corp.querySelector("#cf-audit-zona");
    const btn = corp.querySelector("#cf-audit-run");
    if (btn) { btn.disabled = true; btn.textContent = "Se ruleaz\u0103\u2026"; }
    let a;
    try {
      a = await api.get(`/control-fiscal/${firma.tenant_id}/audit-preluare`);
    } catch (e) {
      if (btn) { btn.disabled = false; btn.textContent = "Ruleaz\u0103 auditul de preluare"; }
      arataMesaj(zona, `Nu am putut rula auditul: ${e.mesaj || e.message}`, "avert");
      return;
    }
    const grup = (titlu, stare, cls) => {
      const arr = (a.constatari || []).filter((c) => c.stare === stare);
      if (!arr.length) return "";
      return `<div class="cf-grup-titlu ${cls}">${titlu} (${arr.length})</div>${arr.map(randA).join("")}`;
    };
    const col = CULORI[a.stare] || CULORI.gri;
    zona.innerHTML = `
      <div class="cf-incr-temei">${a.in_iconta_din ? `Firm\u0103 \u00een iConta din ${dataRo(a.in_iconta_din)} \u00b7 ` : ""}Audit rulat ${dataRo(a.data, "cu_ora")} \u00b7 <span style="color:${col.dot}">${col.txt}</span>
        \u00b7 ${a.coerent} coerent \u00b7 ${a.divergent} divergent \u00b7 ${a.neverificat} neverificat</div>
      ${grup("Coerent", "verde", "cf-verde")}
      ${grup("Divergent", "rosu", "cf-rosu")}
      ${grup("Neverificat", "gri", "")}
      ${a.limita ? `<div class="cf-incr-temei">${esc(a.limita)}</div>` : ""}
      <button class="buton-secundar" id="cf-audit-run" style="margin-top:12px">Reruleaz\u0103 auditul</button>
    `;
    corp.querySelector("#cf-audit-run").addEventListener("click", ruleazaAudit);
  }
  const auditBtn = corp.querySelector("#cf-audit-run");
  if (auditBtn) auditBtn.addEventListener("click", ruleazaAudit);
}
