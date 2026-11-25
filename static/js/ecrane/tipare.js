// tipare.js — Ecran G: Educatie pe tipare (statistic + [F120] analiza generativa AI).
// Trei sectiuni statistice: motive de respingere, tipuri cu rata, firme cu respingeri.
// Plus [F120] buton "Genereaza analiza AI" care cere lui Claude explicatii + recomandari.
// Doar patron (regula 4).
import { api, semnAjutor, esc, atributeInactiv } from "../api.js?v=dc526532b7";
import { permis } from "../drepturi.js?v=34d0fb0afd";  /* [drepturi_rol 04.10.2026] */

// [574] cum se numește felul pregătirii (aceeași regulă ca `tipare_api.eticheta_tip`)
function etichetaTip(tip) { return tip === "nota" ? "Note contabile" : String(tip || "").toUpperCase(); }

function bara(pct) {
  // bara de proportie pentru rata de respingere
  const c = pct >= 30 ? "var(--rosu-semafor)" : (pct >= 10 ? "var(--galben)" : "var(--verde)");
  return `<div class="tip-bara" style="margin-top:4px"><div class="tip-bara-fill" style="width:${pct}%;background:${c}"></div></div>`;
}

export async function randeazaTipare(corp, nav) {
  // [drepturi_rol 04.10.2026] Tiparele echipei sunt ale administratorului (cardul stă doar pe desktopul cabinetului).
  if (!permis("GET /tipare")) { corp.innerHTML = `<p class="ecran-nota">Tiparele de erori ale echipei le vede doar administratorul cabinetului.</p>`; return; }
  corp.innerHTML = `<p class="ecran-nota">Se încarcă tiparele…</p>`;
  let d;
  try {
    d = await api.get("/tipare");
  } catch (e) {
    corp.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca tiparele.</p>`;
    return;
  }

  if (!d.are_date) {
    corp.innerHTML = `
      <div class="tip-ecran">
        <h2 class="pf-titlu">${esc(nav.titluCurent ? nav.titluCurent() : "")} ${semnAjutor("F094")}</h2>
        <div class="tip-gol-mare">
          <h3 class="tip-titlu">Încă nu sunt tipare de arătat</h3>
          <p class="cap-nota">Pe măsură ce echipa pregătește și validează declarații și note, aici apar
          motivele pentru care colegii le-au respins, felurile cu cea mai mare rată de respingere și firmele
          care cer mai multă atenție. Regenerările automate nu se numără. Datele se adună singure din munca de zi cu zi.</p>
          <p class="cap-nota"><b>Analiză AI</b> ${semnAjutor("F120")}</p>   <!-- [17.5-R, R3] F120 după eticheta «Analiză AI» și în starea goală; F094 pe titlul ferestrei -->
          <!-- [17.5] acțiunea ferestrei stă în bară și fără date, inactivă, cu motivul (DS cap.1, 675): „Generează analiză AI” are ce analiza numai după prima respingere -->
          <button class="buton-primar" id="tip-ai" data-actiune="GET /tipare/ai"${atributeInactiv("Nu există încă nicio respingere de analizat: analiza AI se poate genera după prima.")}>Generează analiză AI</button>
        </div>
      </div>`;
    return;
  }

  const motive = d.motive || [];
  const tipuri = d.tipuri || [];
  const firme = d.firme || [];

  // --- 1) MOTIVE ---
  let randMotive = "";
  if (!motive.length) {
    randMotive = `<tr><td colspan="2" class="stare-goala">Nicio respingere înregistrată.</td></tr>`;
  } else {
    motive.forEach((m) => {
      randMotive += `<tr>
        <td>${esc(m.motiv)}</td>
        <td class="cap-num">${m.n}</td>
      </tr>`;
    });
  }
  const sectMotive = `
    <h3 class="tip-titlu">Motive de respingere</h3>
    <div class="cap-tabel-wrap">
      <table class="cap-tabel">
        <thead><tr><th>Motiv</th><th class="cap-num">De câte ori</th></tr></thead>
        <tbody>${randMotive}</tbody>
      </table>
    </div>
  `;

  // --- 2) TIPURI cu rata ---
  // [lotul 13, 575 — „Tabelul declarațiilor din Tipare: valorile nu stau sub coloane”] trei coloane cu antetul lor (era un al patrulea
  // antet, „Acțiune”, deasupra barei, iar antetele numerice stăteau la stânga peste cifre aliniate la dreapta); bara stă în celula ratei.
  // [574] rândurile cuprind și notele contabile respinse de om („Note contabile”)
  let randTipuri = "";
  // [17.5-M, AC034] toate tipurile primite (cele fără respingeri apar «0 din N»), urmate de totalul pregătirilor lor
  if (!tipuri.length) {
    randTipuri = `<tr><td colspan="3" class="stare-goala">Nicio declarație sau notă respinsă la validare încă — rata pe tip apare după primele respingeri.</td></tr>`;
  } else {
    tipuri.forEach((t) => {
      randTipuri += `<tr>
        <td>${esc(etichetaTip(t.tip))}</td>
        <td class="cap-num">${t.respinse} din ${t.total}</td>
        <td class="cap-num tip-rata">${t.pct}%${bara(t.pct)}</td>
      </tr>`;
    });
    const sumaResp = tipuri.reduce((a, t) => a + (t.respinse || 0), 0);
    const sumaTot = tipuri.reduce((a, t) => a + (t.total || 0), 0);
    const pctTot = sumaTot ? Math.round((sumaResp * 100) / sumaTot) : 0;
    randTipuri += `<tr class="cap-total">
        <td><b>Total (toate pregătirile)</b></td>
        <td class="cap-num"><b>${sumaResp} din ${sumaTot}</b></td>
        <td class="cap-num tip-rata"><b>${pctTot}%</b>${bara(pctTot)}</td>
      </tr>`;
  }
  const sectTipuri = `
    <h3 class="tip-titlu">Declarații și note: rata de respingere</h3>
    <div class="cap-tabel-wrap">
      <table class="cap-tabel" id="tip-tabel-tipuri">
        <thead><tr>
          <th>Declarație sau notă</th><th class="cap-num">Respinse din pregătite</th><th class="cap-num">Rată</th>
        </tr></thead>
        <tbody>${randTipuri}</tbody>
      </table>
    </div>
  `;

  // --- 3) FIRME ---
  let randFirme = "";
  if (!firme.length) {
    randFirme = `<tr><td colspan="3" class="stare-goala">Nicio firmă cu respingeri.</td></tr>`;
  } else {
    firme.forEach((f) => {
      const cui = f.cui ? ` <span class="cap-rol">${f.cui}</span>` : "";
      randFirme += `<tr>
        <td>${esc(f.nume)}${cui}</td>
        <td class="cap-num">${f.respinse}</td>
        <td class="cap-num">${f.total}</td>
      </tr>`;
    });
    // [17.5-M, AC034] totalul firmelor cu respingeri; populația lui e numită în nota de sub tabel
    randFirme += `<tr class="cap-total">
        <td><b>Total (firmele cu respingeri)</b></td>
        <td class="cap-num"><b>${firme.reduce((a, f) => a + (f.respinse || 0), 0)}</b></td>
        <td class="cap-num"><b>${firme.reduce((a, f) => a + (f.total || 0), 0)}</b></td>
      </tr>`;
  }
  const sectFirme = `
    <h3 class="tip-titlu">Firme cu cele mai multe respingeri</h3>
    <div class="cap-tabel-wrap">
      <table class="cap-tabel">
        <thead><tr>
          <th>Firmă</th><th class="cap-num">Respinse</th><th class="cap-num">Total</th>
        </tr></thead>
        <tbody>${randFirme}</tbody>
      </table>
    </div>
    <p class="cap-nota">Numai firmele cu respingeri, cel mult 15; „Total” numără pregătirile acestor firme, nu pe toate ale cabinetului.</p>
  `;

  // [17.5-M, AC035] asistenții marcați de semafor (roșu = tipar sistematic, galben = tipar nou); fără niciunul secțiunea nu apare
  let sectAtentie = "";
  try {
    const sem = await api.get("/asistenti/echipa/semafor");
    const marcati = (sem.asistenti || []).filter((a) => a.culoare === "rosu" || a.culoare === "galben");
    if (marcati.length) {
      sectAtentie = `
    <h3 class="tip-titlu">Asistenți care necesită atenție</h3>
    <div class="cap-tabel-wrap">
      <table class="cap-tabel">
        <thead><tr><th>Asistent</th><th>Tipar</th><th class="cap-num">Respinse</th><th class="cap-num">Rată</th></tr></thead>
        <tbody>${marcati.map((a) => `<tr>
          <td>${esc(a.nume)}</td>
          <td>${a.culoare === "rosu" ? "tipar sistematic" : "tipar nou"}</td>
          <td class="cap-num">${a.respinse}</td>
          <td class="cap-num">${a.rata}%</td>
        </tr>`).join("")}</tbody>
      </table>
    </div>`;
    }
  } catch {
    sectAtentie = `<p class="ecran-nota">Asistenții care necesită atenție nu s-au putut încărca.</p>`;
  }

  // [lotul 11, decizia Costin 10.3, verbatim în DECIZII „Comanda 10.3” pct.4: „Totalurile și rezumatul fix, mesajele lângă buton […]:
  // da, reorganizezi ecranele”] „Generează analiză AI” stătea sub cele trei tabele, iar rezultatul lui la capătul lor: acum butonul e în
  // rezumatul lipit sus, iar rezultatul chiar sub el, deasupra tabelelor (DS cap.9 v2.100)
  corp.innerHTML = `<div class="tip-ecran">
    <h2 class="pf-titlu">${esc(nav.titluCurent ? nav.titluCurent() : "")} ${semnAjutor("F094")}</h2>
    <div class="rezumat-fix tip-analiza">
      <p class="cap-nota"><b>Analiză AI</b> ${semnAjutor("F120")} — Claude citește exact tiparele de mai jos (numai respingerile făcute de colegi) și propune explicații și recomandări concrete.
        <button class="buton-primar" id="tip-ai" data-actiune="GET /tipare/ai" style="margin-left:8px">Generează analiză AI</button></p>
    </div>
    <div id="tip-ai-rez"></div>
    ${sectAtentie}${sectMotive}${sectTipuri}${sectFirme}</div>`;
  corp.querySelector("#tip-ai").addEventListener("click", async () => {
    const btn = corp.querySelector("#tip-ai");
    const rez = corp.querySelector("#tip-ai-rez");
    btn.disabled = true; rez.innerHTML = `<p class="ecran-nota">Se analizează… (câteva secunde)</p>`;
    try {
      const r = await api.get("/tipare/ai");
      if (r && r.disponibil) {
        rez.innerHTML = `<div class="pf-frand" style="display:block;white-space:pre-wrap">${esc(r.analiza || "")}</div>`;
      } else {
        rez.innerHTML = `<p class="ecran-nota">${esc((r && r.motiv) || "Analiza nu e disponibilă acum.")}</p>`;
      }
    } catch (e) {
      rez.innerHTML = `<p class="ecran-nota">Nu s-a putut genera analiza.</p>`;
    }
    btn.disabled = false;
  });
}
