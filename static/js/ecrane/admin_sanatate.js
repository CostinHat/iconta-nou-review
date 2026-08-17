// admin_sanatate.js — Admin iConta: sanatate infrastructura (doar superadmin).
// Server (CPU/RAM/disk), aplicatie (uptime), baza de date, erori recente (500+), grafice istoric.
import { dataRo, api, arataMesaj, esc } from "../api.js?v=427bd69bf5";


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

function culoareProcent(p) {
  if (p == null) return "var(--gri-semafor)";
  if (p >= 90) return "var(--rosu-semafor)";
  if (p >= 70) return "var(--galben)";
  return "var(--verde)";
}

// grafic SVG simplu (polyline), fara librarie externa
function grafic(istoric, camp, titlu, culoare, maxFix) {
  const valori = istoric.map((r) => (r[camp] == null ? null : Number(r[camp])));
  const puncteValide = valori.filter((v) => v != null);
  if (!puncteValide.length) {
    return `<div class="pov-card"><div class="tip-desc" style="margin-bottom:6px">${titlu}</div><div class="stare-goala">Fără date încă. Se umple când apar primele evenimente.</div></div>`;
  }
  const W = 560, H = 120, PAD = 8;
  const maxVal = maxFix != null ? maxFix : Math.max(...puncteValide, 1);
  const minVal = 0;
  const n = istoric.length;
  const pasX = n > 1 ? (W - 2 * PAD) / (n - 1) : 0;
  let puncte = [];
  istoric.forEach((r, i) => {
    const v = r[camp];
    if (v == null) return;
    const x = PAD + i * pasX;
    const y = H - PAD - ((Number(v) - minVal) / (maxVal - minVal || 1)) * (H - 2 * PAD);
    puncte.push(`${x.toFixed(1)},${y.toFixed(1)}`);
  });
  const ultimulR = istoric[istoric.length - 1];
  const ultimaVal = ultimulR ? ultimulR[camp] : null;
  const _cuZi = (iso) => { const d = new Date(iso); return isNaN(d) ? "" : `${d.getDate()}.${String(d.getMonth()+1).padStart(2,"0")} ${fmtOra(iso)}`; };
  const _multizi = (new Date(istoric[istoric.length-1].creat_la) - new Date(istoric[0].creat_la)) > 20*3600*1000;
  const primaOra = _multizi ? _cuZi(istoric[0].creat_la) : fmtOra(istoric[0].creat_la);
  const ultimaOra = _multizi ? _cuZi(istoric[istoric.length - 1].creat_la) : fmtOra(istoric[istoric.length - 1].creat_la);
  return `
    <div class="pov-card">
      <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px">
        <div class="tip-desc">${titlu}</div>
        <div class="tip-figura" style="color:${culoare}">${ultimaVal != null ? ultimaVal : "—"}</div>
      </div>
      <svg viewBox="0 0 ${W} ${H}" style="width:100%;height:${H}px" preserveAspectRatio="none">
        <polyline points="${puncte.join(" ")}" fill="none" stroke="${culoare}" stroke-width="2" />
      </svg>
      <div class="tip-micut" style="display:flex;justify-content:space-between;color:var(--gri-clar);margin-top:2px">
        <span>${primaOra}</span><span>${ultimaOra}</span>
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
    corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca sănătatea serverului.</p>`;
    return;
  }
  const srv = d.server || {};
  const ram = srv.ram || {};
  const disc = srv.disc || {};
  const app = d.aplicatie || {};
  const bd = d.baza_date || {};
  const erori = d.erori_lista || [];
  const istoric = (istoricR && istoricR.istoric) || [];

  const cifra = (val, eticheta, procent) => `
    <div class="cap-cifra-bloc">
      <div class="cap-cifra" style="color:${procent != null ? culoareProcent(procent) : "#1a1d21"}">${val}</div>
      <div class="cap-cifra-desc">${eticheta}</div>
    </div>`;

  corp.innerHTML = `
    <h2 class="pf-titlu">Sănătate server</h2>

    <h3 class="cap-titlu">Server</h3>
    <div class="cap-cifre">
      ${cifra((srv.load1 ?? "—"), "load average (1 min)")}
      ${cifra(ram.folosit_procent != null ? ram.folosit_procent + "%" : "—", `RAM folosită (${ram.disponibil_mb ?? "—"} MB liber din ${ram.total_mb ?? "—"} MB)`, ram.folosit_procent)}
      ${cifra(disc.folosit_procent != null ? disc.folosit_procent + "%" : "—", `disc folosit (${disc.liber_gb ?? "—"} GB liber din ${disc.total_gb ?? "—"} GB)`, disc.folosit_procent)}
    </div>

    <h3 class="cap-titlu">Aplicație</h3>
    <div class="cap-cifre">
      ${cifra(fmtUptime(app.uptime_secunde), "activă de")}
    </div>

    <h3 class="cap-titlu">Bază de date</h3>
    <div class="cap-cifre">
      ${cifra(bd.conexiuni ?? "—", "conexiuni active")}
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
      ${grafic(istoric, "ram_procent", "RAM folosită (%)", "#2563eb", 100)}
      ${grafic(istoric, "disc_procent", "Disc folosit (%)", "#7c3aed", 100)}
      ${grafic(istoric, "load1", "Load average", "var(--galben)")}
      ${grafic(istoric, "conexiuni_db", "Conexiuni DB", "#16a34a")}
    </div>
    <div style="margin-top:16px">
      <button class="buton-secundar" id="san-test-alerta">Trimite alert\u0103 de test</button>
      <span id="san-test-msg"></span>
    </div>
  `;
  const bTest = corp.querySelector("#san-test-alerta");
  bTest.addEventListener("click", async () => {  // [test_alerta_v1] verifica livrarea emailurilor de alerta
    bTest.disabled = true;
    try {
      const r = await api.post("/admin/sanatate/test-alerta", {});
      arataMesaj(corp.querySelector("#san-test-msg"), `Alert\u0103 de test trimis\u0103 la ${r.trimis_catre}. Verific\u0103 inboxul.`, "ok");
    } catch {
      arataMesaj(corp.querySelector("#san-test-msg"), "Nu am putut trimite alerta de test.", "eroare");
    }
    bTest.disabled = false;
  });
}
