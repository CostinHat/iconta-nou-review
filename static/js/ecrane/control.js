// control.js — ecranul Control fiscal (semafor conformare portofoliu + drill-down).
// Nivel 1: lista firmelor cu pastila colorata (verde/galben/rosu).
// Nivel 2: click pe firma -> corpul verdictului, randat de control_verdict.js (renderer UNIC, DS cap.20).

import { api, esc } from "../api.js?v=a7f9e80ae0";  /* esc_nc27 */
import { CULORI, etichetaStare, randeazaCorpVerdict, legaVerdict } from "./control_verdict.js?v=e0cd124f13";  // renderer unic al verdictului (DS cap.20)


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
    <p class="mig-intro">Starea fiscală a fiecărei firme: declarațiile datorate vs depuse (cu termenele ANAF) și coerența lor cu contabilitatea — TVA, salarii, operațiuni intracomunitare, cota facturilor emise, echilibru și trezorerie.</p>
    <div class="cf-sumar">
      <span class="cf-pastila"><span class="cf-dot" style="background:${CULORI.verde.dot}"></span>${s.verde || 0} la zi</span>
      <span class="cf-pastila"><span class="cf-dot" style="background:${CULORI.galben.dot}"></span>${s.galben || 0} de urmărit</span>
      <span class="cf-pastila"><span class="cf-dot" style="background:${CULORI.rosu.dot}"></span>${s.rosu || 0} cu restanță</span>
      <!-- [eticheta_din_fapt] al 4-lea contor: fara el, o firma gri DISPAREA din sumar (totalul nu mai
           dadea numarul de firme din cabinet). Backendul il numara de la inceput (sumar["gri"]). -->
      <span class="cf-pastila"><span class="cf-dot" style="background:${CULORI.gri.dot}"></span>${s.gri || 0} nu se pot verifica</span>
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
      : f.stare === "verde" ? "totul la zi"
      : `${f.neclar || 0} declarați${(f.neclar || 0) === 1 ? "e nu se poate verifica" : "i nu se pot verifica"}`;
    if ((f.contabil || []).length) detaliu += " · " + f.contabil.map((c) => (c && c.eticheta) || c).join(" · ");
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${detaliu}</div>
      </div>
      <span class="cf-stare" style="background:${col.bg}">
        <span class="cf-dot" style="background:${col.dot}"></span>${etichetaStare(f.stare, f.neclar)}
      </span>
    `;
    rand.addEventListener("click", () => nav.deschide("Detaliu firmă", (cc, nn) => detaliuFirma(cc, nn, f)));  // [p122_nav_stiva]
    lista.appendChild(rand);
  });

  // [F164_routing] deschis din notificarea de control fiscal (link control-fiscal:{tid}) -> auto-drill in
  // detaliul FIRMEI, reutilizand exact click-ul de rand (acelasi obiect firma: nume+contabil, aceeasi stiva
  // portofoliu->detaliu). Firma negasita (fara acces / tid gresit) -> ramai pe portofoliu, nu crapa.
  if (tidAuto != null) {
    const f = firme.find((x) => x.tenant_id === tidAuto);
    if (f) nav.deschide("Detaliu firmă", (cc, nn) => detaliuFirma(cc, nn, f));
    else console.warn("[control] firma", tidAuto, "negasita in portofoliu (fara acces sau tid gresit)");
  }
}

// Nivel 2 — corpul verdictului per firma. Randarea traieste in control_verdict.js (renderer UNIC, partajat
// cu cardul din fisa firmei): acelasi payload, aceleasi sectiuni, aceleasi chei. Aici doar anteta (nume +
// stare) + delegarea. reincarca = re-drill dupa o contabilizare reusita (constatarea trece pe verde).
async function detaliuFirma(corp, nav, firma) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  let d = { lipsa: [], urmarit: [] };
  try {
    d = await api.get(`/control-fiscal/${firma.tenant_id}`);
  } catch (e) {
    corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca controlul fiscal. Reîncearcă.</p>`;
    return;
  }
  const col = CULORI[d.stare] || CULORI.gri;
  corp.innerHTML =
    `<p class="mig-intro"><b>${esc(firma.nume)}</b> · <span style="color:${col.dot}">${etichetaStare(d.stare, (d.neclar || []).length)}</span></p>`
    + randeazaCorpVerdict(d, { mod: "detaliu" });
  legaVerdict(corp, nav, { tenant_id: firma.tenant_id, nume: firma.nume, reincarca: () => detaliuFirma(corp, nav, firma) });
}
