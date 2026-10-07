// capacitate.js — Ecran C: Capacitate cabinet (doar patron).
// Trei sectiuni: 1) cabinet (cat e de facut vs ritm), 2) pe asistent
// (incarcare per procesator), 3) timp mediu pe tip de declaratie.
// Regula 4: control/comparatii doar la cabinet, niciodata la asistent.
import { api, esc } from "../api.js?v=e9cf26e11b";
import { randeazaAsistenti } from "./asistenti.js?v=b8e3412a1e";
import { permis } from "../drepturi.js?v=df020d220f";  /* [drepturi_rol 04.10.2026] */

function celulaCifra(valoare, eticheta, accent) {
  const c = accent || "#1a1d21";
  return `<div class="cap-cifra-bloc">
    <div class="cap-cifra" style="color:${c}">${valoare}</div>
    <div class="cap-cifra-desc">${eticheta}</div>
  </div>`;
}

export async function randeazaCapacitate(corp, nav) {
  // [drepturi_rol 04.10.2026] Panoul e al administratorului (cardul stă doar pe desktopul cabinetului); dacă
  // s-ar deschide totuși, spune DE CE nu arată nimic, în loc de un „nu am putut încărca” fals.
  if (!permis("GET /capacitate")) { corp.innerHTML = `<p class="ecran-nota">Capacitatea cabinetului o vede doar administratorul cabinetului.</p>`; return; }
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

  // --- PRAG ECHILIBRU: sub 5 actori care poarta munca (patron inclus),
  // semnalul e gol pe echipa mica -> nu afisam cifrele, ci empty state + indrumare.
  const PRAG_ECHILIBRU = 5;
  if (asistenti.length < PRAG_ECHILIBRU) {
    corp.innerHTML = `
      <div class="cap-ecran">
        <div class="stare-goala">
          <p>Într-o echipă care crește, munca nu se împarte singură în mod egal.</p>
          <p>Unii duc trei firme, alții șapte — și afli abia când cineva cedează în perioada de declarații. Capacitate îți arată cine cât duce, unde e presiune și unde e loc, ca s-o echilibrezi din vreme, nu în criză.</p>
          <p>Semnalul are sens de la 5 persoane care lucrează declarații în sus. Momentan sunt ${asistenti.length}, inclusiv administratorul dacă are competențe — până atunci, îi vezi pe toți dintr-o privire.</p>
          <p><button type="button" class="buton-secundar" id="cap-adauga-asistenti" data-actiune="POST /asistenti">Adaugă asistenți</button></p>
        </div>
      </div>`;
    corp.querySelector("#cap-adauga-asistenti").addEventListener("click",
      () => nav.deschide("Asistenți", (c) => randeazaAsistenti(c, nav), { nivel: "cabinet" }));
    return;
  }

  // --- 1) CABINET ---
  const sectCabinet = `
    <div class="cap-cifre">
      ${celulaCifra(cab.in_lucru ?? 0, "în lucru")}
      ${celulaCifra(cab.de_validat ?? 0, "de validat", cab.de_validat ? "var(--galben-text)" : null)}
      ${celulaCifra(cab.depuse_luna ?? 0, "depuse luna asta", (cab.depuse_luna ? "var(--verde)" : null))}
      ${celulaCifra((cab.ritm_pe_zi ?? 0), "ritm / zi lucrătoare")}
    </div>
    <p class="cap-nota">Ritmul e calculat pe ${cab.zile_lucratoare ?? 0} zile lucrătoare din luna curentă.</p>
  `;

  // --- 2) PE ASISTENT ---
  let randuriAsist = "";
  if (!asistenti.length) {
    randuriAsist = `<tr><td colspan="6" class="stare-goala">Niciun procesator cu competențe.</td></tr>`;
  } else {
    asistenti.forEach((a) => {
      const pct = (a.pct_acceptate === null || a.pct_acceptate === undefined)
        ? "—" : a.pct_acceptate + "%";
      const rol = a.poate_valida ? "senior" : "junior";
      randuriAsist += `
        <tr>
          <td>${esc(a.nume || "—")} <span class="cap-rol">${rol}</span></td>
          <td class="cap-num">${a.firme_atribuite ?? 0}</td>
          <td class="cap-num">${a.in_lucru ?? 0}</td>
          <td class="cap-num">${a.pregatite_luna ?? 0}</td>
          <td class="cap-num">${a.depuse_luna ?? 0}</td>
          <td class="cap-num">${pct}</td>
        </tr>`;
    });
  }
  const sectAsist = `
    <h3 class="cap-titlu">Pe asistent<span class="cap-rol">luna curentă</span></h3>
    <div class="cap-tabel-wrap">
      <table class="cap-tabel">
        <thead><tr>
          <th>Asistent</th><th class="cap-num">Firme</th><th class="cap-num">În lucru</th>
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
    randuriTimp = `<tr><td colspan="3" class="stare-goala">Încă nu sunt declarații cronometrate.</td></tr>`;
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
    <h3 class="cap-titlu">Timp mediu pe tip<span class="cap-rol">istoric complet</span></h3>
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
