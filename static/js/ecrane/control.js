// control.js — ecranul Control fiscal (semafor conformare portofoliu + drill-down).
// Nivel 1: lista firmelor cu pastila colorata (verde/galben/rosu).
// Nivel 2: click pe firma -> corpul verdictului, randat de control_verdict.js (renderer UNIC, DS cap.20).

import { VERDICT_POZITIV } from "./verdict.js?v=59fd410a82";  // [P13c] punctul unic de verdict
import { api, esc, cate } from "../api.js?v=58f26a3fc4";  /* esc_nc27 */
import { semaforPatruLumini, publicaSumarControl } from "./semafor.js?v=60f4db5322";  // [125 + 224] aceleași patru lumini ca ale cardului
import { CULORI, etichetaStare, randeazaCorpVerdict, legaVerdict } from "./control_verdict.js?v=2daa29640d";  // renderer unic al verdictului (DS cap.20)


export async function randeazaControl(corp, nav, tidAuto) {
  corp.innerHTML = `<p class="ecran-nota">Se evaluează portofoliul…</p>`;
  let date = { firme: [], sumar: {} };
  try {
    date = await api.get("/control-fiscal");
  } catch (e) {
    corp.innerHTML = `<p class="ecran-nota">Nu s-a putut încărca controlul fiscal.</p>`;
    return;
  }
  const firme = date.firme || [];
  publicaSumarControl(date.sumar);   // [125 + 224] cardul care a deschis fereastra arată aceeași citire

  corp.innerHTML = `
    <p class="mig-intro">Starea fiscală a fiecărei firme: declarațiile datorate vs depuse (cu termenele ANAF) și coerența lor cu contabilitatea — TVA, salarii, operațiuni intracomunitare, cota facturilor emise, echilibru și trezorerie.</p>
    <div class="cf-sumar">
      <!-- [125 + 224, decizia Costin 11.10.2026] aceleași patru stări, cu aceleași numere, ca pe cardul care deschide fereastra:
           aceeași funcție (semaforPatruLumini) peste același câmp (sumar din /control-fiscal) — fiecare firmă într-o singură stare -->
      ${semaforPatruLumini(date.sumar)}
    </div>
    <p class="ecran-nota">Din ${cate(firme.length, "firmă", "firme")}; fiecare firmă e numărată o singură dată, în starea de pe rândul ei.</p>
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
    // [08.10.2026, retest pct.7] detaliul numără faptele (restanțe, de urmărit, neverificabile), nu repetă culoarea
    // [deficiențele 156/173, retestul Costin 09.10] „nu se poate verifica” vine de la server (același predicat ca contorul de sus), iar
    // verificările contabile gri sunt spuse acolo — aici rămân numai cele cu constatare (roșu / galben)
    const fapte = [(f.lipsa || 0) ? cate(f.lipsa, "restanță", "restanțe") : "",
      (f.urmarit || 0) ? `${f.urmarit} de urmărit` : "",
      f.neverificabil ? esc(f.neverificabil) : ""].filter(Boolean);
    let detaliu = fapte.length ? fapte.join(" · ") : (f.stare === "verde" ? VERDICT_POZITIV.control_firma : "");
    const cuConstatare = (f.contabil || []).filter((c) => !(c && c.stare === "gri"));
    if (cuConstatare.length) detaliu += (detaliu ? " · " : "") + cuConstatare.map((c) => esc((c && c.eticheta) || c)).join(" · ");
    const rand = document.createElement("button");
    rand.className = "mig-frand";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${detaliu}</div>
      </div>
      <span class="cf-stare" style="background:${col.bg}">
        <span class="cf-dot" style="background:${col.dot}"></span>${etichetaStare(f.stare)}
      </span>
    `;
    rand.addEventListener("click", () => deschideDetaliu(nav, f));  // [p122_nav_stiva] [396]
    lista.appendChild(rand);
  });

  // [F164_routing] deschis din notificarea de control fiscal (link control-fiscal:{tid}) -> auto-drill in
  // detaliul FIRMEI, reutilizand exact click-ul de rand (acelasi obiect firma: nume+contabil, aceeasi stiva
  // portofoliu->detaliu). Firma negasita (fara acces / tid gresit) -> ramai pe portofoliu, nu crapa.
  if (tidAuto != null) {
    const f = firme.find((x) => x.tenant_id === tidAuto);
    if (f) deschideDetaliu(nav, f);
    else console.warn("[control] firma", tidAuto, "negasita in portofoliu (fara acces sau tid gresit)");
  }
}

// Nivel 2 — corpul verdictului per firma. Randarea traieste in control_verdict.js (renderer UNIC, partajat
// cu cardul din fisa firmei): acelasi payload, aceleasi sectiuni, aceleasi chei. Aici doar anteta (nume +
// stare) + delegarea. reincarca = re-drill dupa o contabilizare reusita (constatarea trece pe verde).
// [396, retestul 19.10.2026: „Bara «În lucru» rămâne pe F1 când Control fiscal arată auditul F5”] firma al cărei control se deschide
// devine firma în lucru — ÎNAINTE de deschiderea ferestrei, ca la `deschideFirma` (bara se redesenează cu tot desktopul; chemată din
// randarea ferestrei, ar redesena-o la nesfârșit)
function deschideDetaliu(nav, f) {
  if (nav.setFirmaInLucru && (!nav.firmaInLucruId || nav.firmaInLucruId() !== f.tenant_id)) nav.setFirmaInLucru(f.nume || "", f.tenant_id);
  nav.deschide("Detaliu firmă", (cc, nn) => detaliuFirma(cc, nn, f));
}

async function detaliuFirma(corp, nav, firma) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  let d = { lipsa: [], urmarit: [] };
  try {
    d = await api.get(`/control-fiscal/${firma.tenant_id}`);
  } catch (e) {
    corp.innerHTML = `<p class="ecran-nota">Nu s-a putut încărca controlul fiscal. Reîncearcă.</p>`;
    return;
  }
  const col = CULORI[d.stare] || CULORI.gri;
  corp.innerHTML =
    `<p class="mig-intro"><b>${esc(firma.nume)}</b> · <span style="color:${col.dot}">${etichetaStare(d.stare)}</span></p>`
    + randeazaCorpVerdict(d, { mod: "detaliu" });
  legaVerdict(corp, nav, { tenant_id: firma.tenant_id, nume: firma.nume, reincarca: () => detaliuFirma(corp, nav, firma) });
}
