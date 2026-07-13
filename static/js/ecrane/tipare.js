// tipare.js — Ecran G: Educatie pe tipare (statistic, fara AI).
// Trei sectiuni: motive de respingere, tipuri cu rata, firme cu respingeri.
// Doar patron (regula 4). La teste se umple; AI-ul (stratul 5) il foloseste.
import { api } from "../api.js";

function bara(pct) {
  // bara de proportie pentru rata de respingere
  const c = pct >= 30 ? "var(--rosu-semafor)" : (pct >= 10 ? "var(--galben)" : "var(--verde)");
  return `<div class="tip-bara"><div class="tip-bara-fill" style="width:${pct}%;background:${c}"></div></div>`;
}

export async function randeazaTipare(corp, nav) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă tiparele…</p>`;
  let d;
  try {
    d = await api.get("/tipare");
  } catch (e) {
    corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca tiparele.</p>`;
    return;
  }

  if (!d.are_date) {
    corp.innerHTML = `
      <div class="tip-ecran">
        <div class="tip-gol-mare">
          <h3 class="tip-titlu">Încă nu sunt tipare de arătat</h3>
          <p class="cap-nota">Pe măsură ce echipa pregătește și validează declarații, aici apar
          motivele de respingere recurente, tipurile cu cea mai mare rată de respingere și firmele
          care cer mai multă atenție. Datele se adună singure din munca de zi cu zi.</p>
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
    randMotive = `<tr><td colspan="2" class="cap-gol">Nicio respingere înregistrată.</td></tr>`;
  } else {
    motive.forEach((m) => {
      randMotive += `<tr>
        <td>${(m.motiv || "").replace(/[<>&]/g, "")}</td>
        <td class="cap-num">${m.n}</td>
      </tr>`;
    });
  }
  const sectMotive = `
    <h3 class="tip-titlu">Motive de respingere recurente</h3>
    <div class="cap-tabel-wrap">
      <table class="cap-tabel">
        <thead><tr><th>Motiv</th><th class="cap-num">De câte ori</th></tr></thead>
        <tbody>${randMotive}</tbody>
      </table>
    </div>
  `;

  // --- 2) TIPURI cu rata ---
  let randTipuri = "";
  const tipuriCuResp = tipuri.filter((t) => t.respinse > 0);
  if (!tipuriCuResp.length) {
    randTipuri = `<tr><td colspan="4" class="cap-gol">Niciun tip cu respingeri.</td></tr>`;
  } else {
    tipuriCuResp.forEach((t) => {
      randTipuri += `<tr>
        <td>${(t.tip || "").toUpperCase()}</td>
        <td class="cap-num">${t.respinse} / ${t.total}</td>
        <td class="cap-num">${t.pct}%</td>
        <td class="tip-bara-cel">${bara(t.pct)}</td>
      </tr>`;
    });
  }
  const sectTipuri = `
    <h3 class="tip-titlu">Tipuri de declarații cu rată de respingere</h3>
    <div class="cap-tabel-wrap">
      <table class="cap-tabel">
        <thead><tr>
          <th>Declarație</th><th class="cap-num">Respinse</th>
          <th class="cap-num">Rată</th><th></th>
        </tr></thead>
        <tbody>${randTipuri}</tbody>
      </table>
    </div>
  `;

  // --- 3) FIRME ---
  let randFirme = "";
  if (!firme.length) {
    randFirme = `<tr><td colspan="3" class="cap-gol">Nicio firmă cu respingeri.</td></tr>`;
  } else {
    firme.forEach((f) => {
      const cui = f.cui ? ` <span class="cap-rol">${f.cui}</span>` : "";
      randFirme += `<tr>
        <td>${(f.nume || "").replace(/[<>&]/g, "")}${cui}</td>
        <td class="cap-num">${f.respinse}</td>
        <td class="cap-num">${f.total}</td>
      </tr>`;
    });
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
  `;

  corp.innerHTML = `<div class="tip-ecran">${sectMotive}${sectTipuri}${sectFirme}
    <p class="cap-nota">Tiparele se construiesc din respingerile reale. Mai târziu, asistentul AI
    va folosi exact aceste date ca să propună corecții.</p></div>`;
}
