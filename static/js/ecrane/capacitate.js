// capacitate.js — Ecran C: Capacitate cabinet (doar patron).
// Trei sectiuni: 1) cabinet (cat e de facut vs ritm), 2) pe asistent
// (incarcare per procesator), 3) timp mediu pe tip de declaratie.
// Regula 4: control/comparatii doar la cabinet, niciodata la asistent.
import { api } from "../api.js";

function celulaCifra(valoare, eticheta, accent) {
  const c = accent || "#1a1d21";
  return `<div class="cap-cifra-bloc">
    <div class="cap-cifra" style="color:${c}">${valoare}</div>
    <div class="cap-cifra-desc">${eticheta}</div>
  </div>`;
}

export async function randeazaCapacitate(corp, nav) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă capacitatea…</p>`;
  let d;
  try {
    d = await api.get("/capacitate");
  } catch (e) {
    corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca capacitatea.</p>`;
    return;
  }

  const cab = d.cabinet || {};
  const asistenti = d.asistenti || [];
  const timp = d.timp || { pe_tip: [], total_mostre: 0 };

  // --- 1) CABINET ---
  const sectCabinet = `
    <div class="cap-cifre">
      ${celulaCifra(cab.in_lucru ?? 0, "în lucru")}
      ${celulaCifra(cab.de_validat ?? 0, "de validat", cab.de_validat ? "#c9961f" : null)}
      ${celulaCifra(cab.depuse_luna ?? 0, "depuse luna asta", "#1d7a4d")}
      ${celulaCifra((cab.ritm_pe_zi ?? 0), "ritm / zi lucrătoare")}
    </div>
    <p class="cap-nota">Ritmul e calculat pe ${cab.zile_lucratoare ?? 0} zile lucrătoare din luna curentă.</p>
  `;

  // --- 2) PE ASISTENT ---
  let randuriAsist = "";
  if (!asistenti.length) {
    randuriAsist = `<tr><td colspan="5" class="cap-gol">Niciun procesator cu competențe.</td></tr>`;
  } else {
    asistenti.forEach((a) => {
      const pct = (a.pct_acceptate === null || a.pct_acceptate === undefined)
        ? "—" : a.pct_acceptate + "%";
      const rol = a.poate_valida ? "senior" : "junior";
      randuriAsist += `
        <tr>
          <td>${(a.nume || "—").replace(/[<>&]/g, "")} <span class="cap-rol">${rol}</span></td>
          <td class="cap-num">${a.in_lucru ?? 0}</td>
          <td class="cap-num">${a.pregatite_luna ?? 0}</td>
          <td class="cap-num">${a.depuse_luna ?? 0}</td>
          <td class="cap-num">${pct}</td>
        </tr>`;
    });
  }
  const sectAsist = `
    <h3 class="cap-titlu">Pe asistent</h3>
    <div class="cap-tabel-wrap">
      <table class="cap-tabel">
        <thead><tr>
          <th>Asistent</th><th class="cap-num">În lucru</th>
          <th class="cap-num">Pregătite</th><th class="cap-num">Depuse</th>
          <th class="cap-num">% acceptate</th>
        </tr></thead>
        <tbody>${randuriAsist}</tbody>
      </table>
    </div>
  `;

  // --- 3) TIMP ---
  let randuriTimp = "";
  if (!timp.pe_tip.length) {
    randuriTimp = `<tr><td colspan="3" class="cap-gol">Încă nu sunt declarații cronometrate.</td></tr>`;
  } else {
    timp.pe_tip.forEach((t) => {
      randuriTimp += `
        <tr>
          <td>${(t.tip || "").toUpperCase()}</td>
          <td class="cap-num">${t.durata_medie || "—"}</td>
          <td class="cap-num">${t.n}</td>
        </tr>`;
    });
  }
  const sectTimp = `
    <h3 class="cap-titlu">Timp mediu pe tip</h3>
    <div class="cap-tabel-wrap">
      <table class="cap-tabel">
        <thead><tr>
          <th>Declarație</th><th class="cap-num">Durată medie</th><th class="cap-num">Mostre</th>
        </tr></thead>
        <tbody>${randuriTimp}</tbody>
      </table>
    </div>
    <p class="cap-nota">Durata = de la deschiderea ecranului până la generare. Pe ${timp.total_mostre} declarații; devine mai precisă în timp.</p>
  `;

  corp.innerHTML = `<div class="cap-ecran">${sectCabinet}${sectAsist}${sectTimp}</div>`;
}
