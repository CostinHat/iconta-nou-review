// admin_sanatate.js — Admin iConta: sanatate infrastructura (doar superadmin).
// Server (CPU/RAM/disk), aplicatie (uptime), baza de date, erori recente (500+), grafice istoric.
import { dataRo, api, arataMesaj, esc, cantitate, pct } from "../api.js?v=9bcf50c899";

// [lotul 13, deficiența 643 — „Load average afișat «1.53369140625» (11 zecimale, punct), fără pragul de alertă alături; graficele pe 24 h
// fără scară verticală și fără linia pragului; «32.9» cu punct.”] Cifrele în format românesc (DS cap.4: virgula zecimală), încărcarea cu
// două zecimale; pragul de alertă al buclei de sănătate (`core/alerta_load.praguri`, același cu al alertei) lângă cifră și ca linie pe grafic.
function numar2(v) {
  return v == null || v === "" || !isFinite(Number(v)) ? "—" : cantitate(Math.round(Number(v) * 100) / 100);
}
// procentul cu o zecimală (rotunjirea o face `toFixed`, nu o formulă pe un literal — garda aritmeticii pe nume neutre)
function procent(v) { return v == null || v === "" || !isFinite(Number(v)) ? "—" : pct(Number(Number(v).toFixed(1))); }


function fmtOra(iso) {
  const d = new Date(iso);
  if (isNaN(d)) return "";
  return String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0");
}

function fmtUptime(sec) {
  if (sec == null) return "—";
  const zile = Math.floor(sec / 86400);
  const ore = Math.floor((sec % 86400) / 3600);
  const min = Math.floor((sec % 3600) / 60);
  if (zile > 0) return `${zile}z ${ore}h`;
  if (ore > 0) return `${ore}h ${min}m`;
  return `${min}m`;
}

function culoareProcent(p) {   // culoare de TEXT (cifra procentului): tokenii de text, nu cei de semafor (DS cap.8 v2.70)
  if (p == null) return "var(--gri)";
  if (p >= 90) return "var(--rosu)";
  if (p >= 70) return "var(--galben-text)";
  return "var(--verde)";
}

// grafic SVG simplu (polyline), fara librarie externa. [643] scara verticală (0, mijlocul, vârful) și linia pragului de alertă, punctată
function grafic(istoric, camp, titlu, culoare, maxFix, prag, fmt) {
  const valori = istoric.map((r) => (r[camp] == null ? null : Number(r[camp])));
  const puncteValide = valori.filter((v) => v != null);
  if (!puncteValide.length) {
    return `<div class="pov-card"><div class="tip-desc" style="margin-bottom:6px">${titlu}</div><div class="stare-goala">Fără date încă. Se umple când apar primele evenimente.</div></div>`;
  }
  const W = 560, H = 120, PAD = 8;
  const maxVal = maxFix != null ? maxFix : Math.max(...puncteValide, prag != null ? prag * 1.15 : 0, 1);
  const minVal = 0;
  const n = istoric.length;
  const pasX = n > 1 ? (W - 2 * PAD) / (n - 1) : 0;
  const y = (v) => H - PAD - ((Number(v) - minVal) / (maxVal - minVal || 1)) * (H - 2 * PAD);
  let puncte = [];
  istoric.forEach((r, i) => {
    const v = r[camp];
    if (v == null) return;
    puncte.push(`${(PAD + i * pasX).toFixed(1)},${y(v).toFixed(1)}`);
  });
  const ultimulR = istoric[istoric.length - 1];
  const ultimaVal = ultimulR ? ultimulR[camp] : null;
  const _cuZi = (iso) => { const d = new Date(iso); return isNaN(d) ? "" : `${d.getDate()}.${String(d.getMonth()+1).padStart(2,"0")} ${fmtOra(iso)}`; };
  const _multizi = (new Date(istoric[istoric.length-1].creat_la) - new Date(istoric[0].creat_la)) > 20*3600*1000;
  const primaOra = _multizi ? _cuZi(istoric[0].creat_la) : fmtOra(istoric[0].creat_la);
  const ultimaOra = _multizi ? _cuZi(istoric[istoric.length - 1].creat_la) : fmtOra(istoric[istoric.length - 1].creat_la);
  const linPrag = prag != null && prag <= maxVal
    ? `<line class="san-prag" x1="${PAD}" x2="${W - PAD}" y1="${y(prag).toFixed(1)}" y2="${y(prag).toFixed(1)}" stroke="var(--rosu)" stroke-width="1.5" stroke-dasharray="6 4" />` : "";
  return `
    <div class="pov-card" data-grafic="${camp}">
      <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px">
        <div class="tip-desc">${titlu}</div>
        <div class="tip-figura" style="color:${culoare}">${ultimaVal != null ? fmt(ultimaVal) : "—"}</div>
      </div>
      <div style="display:flex;gap:6px;align-items:stretch">
        <div class="tip-micut san-scara" style="display:flex;flex-direction:column;justify-content:space-between;text-align:right;color:var(--gri);min-width:44px;height:${H}px">
          <span>${fmt(maxVal)}</span><span>${fmt(maxVal / 2)}</span><span>${fmt(0)}</span>
        </div>
        <svg viewBox="0 0 ${W} ${H}" style="flex:1;width:100%;height:${H}px" preserveAspectRatio="none" role="img" aria-label="${esc(titlu)}">
          ${linPrag}
          <polyline points="${puncte.join(" ")}" fill="none" stroke="${culoare}" stroke-width="2" />
        </svg>
      </div>
      <div class="tip-micut" style="display:flex;justify-content:space-between;color:var(--gri);margin:2px 0 0 50px">
        <span>${primaOra}</span><span>${prag != null ? `<span style="color:var(--rosu)">- - -</span> pragul de alertă: ${fmt(prag)}` : ""}</span><span>${ultimaOra}</span>
      </div>
    </div>`;
}

export async function randeazaAdminSanatate(corp, nav) {
  const f = corp.closest(".fereastra");
  if (f) f.classList.add("fer-larg-simplu");
  corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
  let d, istoricR;
  try {
    [d, istoricR] = await Promise.all([
      api.get("/admin/sanatate"),
      api.get("/admin/sanatate/istoric?ore=24"),
    ]);
  } catch {
    corp.innerHTML = `<p class="ecran-nota">Nu s-a putut încărca sănătatea serverului.</p>`;
    return;
  }
  const srv = d.server || {};
  const ram = srv.ram || {};
  const disc = srv.disc || {};
  const app = d.aplicatie || {};
  const bd = d.baza_date || {};
  const erori = d.erori_lista || [];
  const istoric = (istoricR && istoricR.istoric) || [];
  const bnr = d.curs_bnr || {};   // [460] cursul zilei: în aplicație sau lipsă (bucla de sănătate îl completează din BNR)
  const pr = d.praguri || {};      // [643] pragurile alertei, aceleași cu ale buclei de sănătate

  const cifra = (val, eticheta, procent) => `
    <div class="cap-cifra-bloc">
      <div class="cap-cifra" style="color:${procent != null ? culoareProcent(procent) : "#1a1d21"}">${val}</div>
      <div class="cap-cifra-desc">${eticheta}</div>
    </div>`;

  corp.innerHTML = `
    <h2 class="pf-titlu">Sănătate server</h2>

    <h3 class="cap-titlu">Server</h3>
    <div class="cap-cifre" id="san-server">
      ${cifra(numar2(srv.load1), `încărcarea pe 1 minut · pe 15 minute: ${numar2(srv.load15)} · pragul de alertă: ${numar2(pr.load)} (media pe 15 minute, numărul de procesoare)`)}
      ${cifra(procent(ram.folosit_procent), `RAM folosită (${numar2(ram.disponibil_mb)} MB liber din ${numar2(ram.total_mb)} MB) · pragul de alertă: ${procent(pr.ram_procent)}`, ram.folosit_procent)}
      ${cifra(procent(disc.folosit_procent), `disc folosit (${numar2(disc.liber_gb)} GB liber din ${numar2(disc.total_gb)} GB) · pragul de alertă: ${procent(pr.disc_procent)}`, disc.folosit_procent)}
    </div>

    <h3 class="cap-titlu">Aplicație</h3>
    <div class="cap-cifre">
      ${cifra(fmtUptime(app.uptime_secunde), "activă de")}
    </div>

    <h3 class="cap-titlu">Curs BNR</h3>
    <div class="cap-cifre" id="san-bnr">
      ${cifra(bnr.ultima_zi ? dataRo(bnr.ultima_zi) : "—", "ultimul curs BNR din aplicație")}
      ${cifra(bnr.asteptat ? dataRo(bnr.asteptat) : "—", "cursul de care au nevoie facturile de azi", bnr.lipsa ? 100 : bnr.lipsa === false ? 0 : null)}
    </div>
    <div id="san-bnr-msg"></div>

    <h3 class="cap-titlu">Bază de date</h3>
    <div class="cap-cifre">
      ${cifra(bd.conexiuni ?? "—", `conexiuni active · pragul de alertă: ${pr.conexiuni_db ?? "—"}`)}
      ${cifra(bd.marime ?? "—", "mărime bază de date")}
    </div>

    <h3 class="cap-titlu">Erori (ultimele 24h)</h3>
    <div class="cap-cifre">
      ${cifra(d.erori_24h ?? 0, "erori server (500+)", d.erori_24h > 0 ? 100 : 0)}
    </div>
    <div class="pf-lista zebra-lista" style="margin-top:12px">
      ${erori.length
        ? erori.map((e) => `
          <div class="pf-frand">
            <div class="pf-frand-text">
              <div class="pf-frand-nume">${esc(e.actiune || "")}</div>
              <div class="pf-frand-sub">status ${(e.detalii && e.detalii.status) || "?"} · ${dataRo(e.created_at, "cu_ora")}</div>
            </div>
          </div>`).join("")
        : `<div class="stare-goala">Nicio eroare în ultimele 24h.</div>`}
    </div>

    <h3 class="cap-titlu">Evoluție (ultimele 24h)</h3>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      ${grafic(istoric, "ram_procent", "RAM folosită", "#2563eb", 100, pr.ram_procent, procent)}
      ${grafic(istoric, "disc_procent", "Disc folosit", "#7c3aed", 100, pr.disc_procent, procent)}
      ${grafic(istoric, "load15", "Încărcarea (media pe 15 minute)", "var(--galben)", null, pr.load, numar2)}
      ${grafic(istoric, "conexiuni_db", "Conexiuni DB", "#16a34a", null, pr.conexiuni_db, (v) => numar2(Math.round(v)))}
    </div>
    <div style="margin-top:16px">
      <button class="buton-secundar" id="san-test-alerta">Trimite alert\u0103 de test</button>
      <span id="san-test-msg"></span>
    </div>
  `;
  // [460] cursul zilei lipsește: alertă pentru administratorul platformei (DS cap.6: `arataMesaj`, eroare), cu golurile anului
  const lipsaBnr = (bnr.zile_lipsa || []).map((z) => dataRo(z));
  if (bnr.lipsa) {
    arataMesaj(corp.querySelector("#san-bnr-msg"), `Cursul BNR comunicat pe ${dataRo(bnr.asteptat)} lipsește din aplicație: facturile în valută de azi `
      + `primesc cursul din ${bnr.ultima_zi ? dataRo(bnr.ultima_zi) : "—"}, iar contabilul vede asta pe factură. Aplicația reîncearcă singură la 10 minute.`
      + (lipsaBnr.length ? ` Zile lipsă în ${bnr.asteptat.slice(0, 4)}: ${lipsaBnr.join(", ")}.` : ""), "eroare");
  } else if (lipsaBnr.length) {
    arataMesaj(corp.querySelector("#san-bnr-msg"), `Zile fără curs BNR în aplicație (se completează din arhiva BNR): ${lipsaBnr.join(", ")}.`, "avert");
  } else if (bnr.lipsa === false) {
    arataMesaj(corp.querySelector("#san-bnr-msg"), `Cursul BNR e la zi: toate zilele bancare din ${bnr.asteptat.slice(0, 4)} sunt în aplicație.`, "ok");
  }
  const bTest = corp.querySelector("#san-test-alerta");
  bTest.addEventListener("click", async () => {  // [test_alerta_v1] verifica livrarea emailurilor de alerta
    bTest.disabled = true;
    try {
      const r = await api.post("/admin/sanatate/test-alerta", {});
      arataMesaj(corp.querySelector("#san-test-msg"), `Alert\u0103 de test trimis\u0103 la ${r.trimis_catre}. Verific\u0103 inboxul.`, "ok");
    } catch {
      arataMesaj(corp.querySelector("#san-test-msg"), "Nu s-a putut trimite alerta de test.", "eroare");
    }
    bTest.disabled = false;
  });
}
