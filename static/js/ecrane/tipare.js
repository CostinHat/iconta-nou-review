// tipare.js — Ecran G: Educatie pe tipare (statistic + [F120] analiza generativa AI).
// Trei sectiuni statistice: motive de respingere, tipuri cu rata, firme cu respingeri.
// Plus [F120] buton "Genereaza analiza AI" care cere lui Claude explicatii + recomandari.
// Doar patron (regula 4).
import { api, esc } from "../api.js?v=427bd69bf5";

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
    randTipuri = `<tr><td colspan="4" class="stare-goala">Niciun tip cu respingeri.</td></tr>`;
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
    <div class="tip-analiza" style="margin-top:16px">
      <h3 class="tip-titlu">Analiză AI</h3>
      <p class="cap-nota">Claude citește exact tiparele de mai sus și propune explicații și recomandări concrete.</p>
      <p><button class="buton-primar" id="tip-ai">Generează analiză AI</button></p>
      <div id="tip-ai-rez"></div>
    </div></div>`;
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
      rez.innerHTML = `<p class="ecran-nota">Nu am putut genera analiza.</p>`;
    }
    btn.disabled = false;
  });
}
