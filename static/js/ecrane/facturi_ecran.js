// facturi_ecran.js — cardul Facturi consolidat, REUTILIZABIL (portal client, gratuit, cabinet).
// Primeste tenantId -> merge din orice context. Contine:
//   meniu (Istoric / Emite / Model factura) + istoric + emitere.
//   Detalii / Storno / Model se adauga in pasii urmatori.
// Apelare: randeazaFacturi(corp, nav, tenantId, { inapoi, titluInapoi })
import { api, dataRo, arataMesaj, confirmaCaseta, esc, bani } from "../api.js";  /* esc_nc27 */
import { sesiune } from "../sesiune.js";
import { randeazaEmitere } from "./emitere_ecran.js";

const dirEticheta = (d) => (d === "iesire" || d === "emisa") ? "emis\u0103"
  : (d === "intrare" || d === "primita") ? "primit\u0103" : (d || "");

export function randeazaFacturi(corp, nav, tenantId, opt = {}) {
  meniuFacturi(corp, nav, tenantId, opt);
}

// ---------- MENIU (Istoric / Emite / Model) ----------
function meniuFacturi(corp, nav, tenantId, opt) {
  if (nav.setInapoi) nav.setInapoi(undefined);
  const inapoi = opt.inapoi || (() => nav && nav.inapoi && nav.inapoi());
  const titluInapoi = opt.titluInapoi || "Inapoi";
  corp.innerHTML = `
    <h2 class="pf-titlu">Facturi</h2>
    <p class="pf-intro">Ce vrei s\u0103 faci?</p>
    <div class="firme-optiuni">
      <button class="firme-optiune" id="fac-istoric">
        <div class="firme-optiune-icon accent-albastru">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h10"/></svg>
        </div>
        <div class="firme-optiune-titlu">Istoric facturi</div>
        <div class="firme-optiune-desc">Facturile emise \u0219i primite</div>
      </button>
      <button class="firme-optiune" id="fac-emite">
        <div class="firme-optiune-icon accent-verde">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>
        </div>
        <div class="firme-optiune-titlu">Emite factur\u0103</div>
        <div class="firme-optiune-desc">Creeaz\u0103 o factur\u0103 nou\u0103</div>
      </button>
      <button class="firme-optiune" id="fac-model">
        <div class="firme-optiune-icon accent-roz">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
        </div>
        <div class="firme-optiune-titlu">Model factur\u0103</div>
        <div class="firme-optiune-desc">Logo, font \u0219i culoare</div>
      </button>
      ${!opt.client ? `<button class="firme-optiune" id="fac-recurente">
        <div class="firme-optiune-icon accent-recomanda">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 3v5h-5"/></svg>
        </div>
        <div class="firme-optiune-titlu">Facturi recurente</div>
        <div class="firme-optiune-desc">\u0218abloane emise automat lunar</div>
      </button>` : ""}
    </div>`;
  corp.querySelector("#fac-istoric").addEventListener("click", () => nav.mergi("Istoric facturi", (c) => istoricFacturi(c, nav, tenantId, opt)));  // faza_b_traseu_v1
  corp.querySelector("#fac-emite").addEventListener("click", () => nav.mergi("Emite factur\u0103", (c) => emiteFactura(c, nav, tenantId, opt)));
  corp.querySelector("#fac-model").addEventListener("click", () => nav.mergi("Model factur\u0103", (c) => modelFactura(c, nav, tenantId, opt)));
  corp.querySelector("#fac-recurente")?.addEventListener("click", () => nav.mergi("Facturi recurente", (c) => listaRecurente(c, nav, tenantId, opt)));
}  // fac_recurente_v1

// ---------- ISTORIC ---------- /* facback_null_fix_v1 */
async function istoricFacturi(corp, nav, tenantId, opt) {
  const inapoiMeniu = () => meniuFacturi(corp, nav, tenantId, opt);
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  let afisate = 10;
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;
    let lista = [];
    try {
      const r = await api.get(`/tenants/${tenantId}/facturi?an=${an}&luna=${luna}&limit=${afisate + 1}`);
      lista = (r && r.facturi) || [];
    } catch {}
    const maiSunt = lista.length > afisate;
    if (maiSunt) lista = lista.slice(0, afisate);
    let corpuri = !lista.length
      ? `<div class="mig-gol">Nicio factur\u0103 \u00een luna aceasta.</div>`
      : lista.map((f) => {
          const suma = f.total != null ? bani(f.total) + " " + (f.moneda || "lei") : "";
          const dir = dirEticheta(f.directie);
          const storno = f.storno_din_id ? ' \u00b7 <span class="fac-storno-tag">storno</span>' : "";
          const tipTag = f.tip && f.tip !== "factura" ? ` \u00b7 <span class="fac-storno-tag">${f.tip}</span>` : "";
          return `
        <button class="buton-secundar pf-frand fac-frand-btn" data-id="${f.id}">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">${f.numar || "\u2014"}${f.tert_nume ? " \u00b7 " + esc(f.tert_nume) : ""}</div>
            <div class="pf-frand-sub">${dataRo(f.data_emitere)}${dir ? " \u00b7 " + dir : ""}${storno}${tipTag}</div>
          </div>
          <span class="pf-frand-suma">${suma}</span>
          ${!opt.client ? `<span class="btn-link fac-cont" data-cid="${f.id}" style="margin-left:8px">Conteaz\u0103</span>` : ""}
        </button>`;
        }).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">Istoric facturi</h2>
      <p class="pf-intro">Luna ${String(luna).padStart(2, "0")}/${an}
        <button class="buton-secundar" id="fac-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="buton-secundar" id="fac-next">luna \u2192</button>
        ${maiSunt ? '<button class="buton-secundar" id="fac-mai-multe" style="margin-left:12px">Vezi \u0219i facturile mai vechi din aceast\u0103 lun\u0103</button>' : ""}</p>
      <div class="pf-lista zebra-lista">${corpuri}</div>`;
    corp.querySelector("#fac-mai-multe")?.addEventListener("click", () => { afisate += 10; deseneaza(); });
    corp.querySelector("#fac-prev").addEventListener("click", () => { afisate = 10; luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#fac-next").addEventListener("click", () => { afisate = 10; luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    corp.querySelectorAll(".fac-cont").forEach((b) => b.addEventListener("click", async (ev) => {
      ev.stopPropagation();
      try {
        const r = await api.post(`/tenants/${tenantId}/facturi/${b.dataset.cid}/contabilizeaza`, {});
        b.outerHTML = `<span style="color:#1d7a4d;font-size:13px;margin-left:8px">ciorn\u0103 #${r.inregistrare_id}</span>`;
      } catch (e) {
        b.outerHTML = `<span style="color:#c9961f;font-size:13px;margin-left:8px">${(e.mesaj || "eroare")}</span>`;
      }
    }));
    corp.querySelectorAll(".fac-frand-btn").forEach((b) => {
      b.addEventListener("click", () => nav.mergi("Factur\u0103", (c) => detaliiFactura(c, nav, tenantId, b.dataset.id, opt)));  // faza_b_traseu_v1
    });
  };
  deseneaza();
}

// ---------- EMITE ----------
function emiteFactura(corp, nav, tenantId, opt) {
  randeazaEmitere(corp, nav, tenantId, {
    dupaEmitere: () => { nav.inapoiPas(); nav.mergi("Istoric facturi", (c) => istoricFacturi(c, nav, tenantId, opt)); },  // faza_b_traseu_v1
  });
}

// ---------- DETALII factura ----------
const _bani = (x, mon) => {
  if (x == null || x === "") return "";
  return mon ? `${bani(x)} ${mon}` : bani(x);
};

async function detaliiFactura(corp, nav, tenantId, facturaId, opt) {
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;
  corp.querySelector("#fac-back")?.addEventListener("click", () => istoricFacturi(corp, nav, tenantId, opt));

  let f = null;
  try {
    f = await api.get(`/tenants/${tenantId}/facturi/${facturaId}`);
  } catch {
    corp.innerHTML = `<div class="mig-gol">Nu am putut \u00eenc\u0103rca factura.</div>`;
    corp.querySelector("#fac-back")?.addEventListener("click", () => istoricFacturi(corp, nav, tenantId, opt));
    return;
  }

  const mon = f.moneda || "RON";
  const esteValuta = mon.toUpperCase() !== "RON";
  const linii = f.linii || [];

  // linii + defalcare pe cote
  const peCota = {};  // cota -> {baza, tva}
  const randuriLinii = linii.map((l) => {
    const cant = Number(l.cantitate) || 0;
    const pret = Number(l.pret_unitar) || 0;
    const cota = Number(l.cota_tva) || 0;
    const baza = cant * pret;
    const tva = baza * cota / 100;
    if (!peCota[cota]) peCota[cota] = { baza: 0, tva: 0 };
    peCota[cota].baza += baza;
    peCota[cota].tva += tva;
    return `
      <tr>
        <td class="fd-td-den">${esc(l.descriere)}</td>
        <td>${cant.toLocaleString("ro-RO")}</td>
        <td class="fd-td-um">${esc(l.um || "buc")}</td>
        <td class="fd-td-num">${_bani(pret)}</td>
        <td>${cota}%</td>
        <td class="fd-td-num">${_bani(baza, mon)}</td>
      </tr>`;
  }).join("");

  // totaluri pe cote
  const cote = Object.keys(peCota).map(Number).sort((a, b) => b - a);
  const randuriTot = cote.map((c) => `
      <div class="fd-tot-rand">
        <span>Baz\u0103 ${c}%</span><span>${_bani(peCota[c].baza, mon)}</span>
      </div>
      <div class="fd-tot-rand">
        <span>TVA ${c}%</span><span>${_bani(peCota[c].tva, mon)}</span>
      </div>`).join("");

  // bloc valuta (obligatoriu legal: TVA si in lei)
  let blocValuta = "";
  if (esteValuta) {
    const sursaTxt = f.curs_sursa === "manual" ? "curs introdus manual"
                   : f.curs_sursa === "bnr" ? "curs BNR" : "curs";
    blocValuta = `
      <div class="fd-valuta">
        <div class="fd-valuta-titlu">Conversie \u00een lei (art. 319 Cod fiscal)</div>
        <div class="fd-tot-rand"><span>TVA \u00een lei</span><span><b>${_bani(f.tva_lei, "lei")}</b></span></div>
        <div class="fd-tot-rand"><span>Total \u00een lei</span><span>${_bani(f.total_lei, "lei")}</span></div>
        <div class="fd-valuta-sub">${sursaTxt} ${f.curs_bnr ? Number(f.curs_bnr).toLocaleString("ro-RO", { minimumFractionDigits: 4 }) : ""} ${f.data_curs ? "\u00b7 " + dataRo(f.data_curs) : ""}</div>
      </div>`;
  }

  const dir = dirEticheta(f.directie);
  const partener = f.tert_nume ? `${esc(f.tert_nume)}${f.tert_cui ? " \u00b7 CUI " + esc(f.tert_cui) : ""}` : "";
  const statusTxt = f.storno_din_id ? "storno" : (f.status || "");

  corp.innerHTML = `
    <div class="fd-antet">
      <div class="fd-antet-sus">
        <h2 class="pf-titlu">${esc(f.numar || "\u2014")}</h2>
        ${statusTxt ? `<span class="fac-storno-tag">${esc(statusTxt)}</span>` : ""}
        <button class="buton-secundar em-buton-sec fd-pdf-btn" id="fd-pdf">PDF factur\u0103</button>
        <button class="buton-secundar em-buton-sec fd-email-btn" id="fd-email">Trimite pe email</button>
        ${(!opt.client && f.directie === "emisa" && !f.storno_din_id) ? '<button class="buton-secundar em-buton-sec fd-storno-btn" id="fd-storno">Storneaz\u0103</button>' : ""}
        ${(f.tip && f.tip !== "factura" && !f.transformat_in_id) ? '<button class="buton-secundar em-buton-sec" id="fd-transforma">Transform\u0103 \u00een factur\u0103</button>' : ""}
        ${f.platita_la ? '<span class="fac-storno-tag fac-tag-platit">pl\u0103tit\u0103</span>' : ""}
        ${(f.directie === "emisa" && f.tip === "factura" && !f.storno_din_id && !f.platita_la) ? '<button class="buton-secundar em-buton-sec" id="fd-plata">Link plat\u0103</button>' : ""}
        ${(f.directie === "emisa" && f.tip === "factura" && !f.storno_din_id && !f.platita_la) ? '<button class="buton-secundar em-buton-sec" id="fd-chitanta">Emite chitan\u021b\u0103</button>' : ""}
        ${f.transformat_in_id ? `<span class="fac-storno-tag">transformat \u00een #${f.transformat_in_id}</span>` : ""}
      </div>
      <div class="fd-email-zona" id="fd-email-zona"></div>
      <div class="fd-storno-zona" id="fd-storno-zona"></div>
      <div id="fd-plata-zona"></div>
      <div id="fd-chitanta-zona"></div>
      <div class="fd-antet-linie">${dir ? dir.charAt(0).toUpperCase() + dir.slice(1) : ""} \u00b7 ${dataRo(f.data_emitere)}${f.data_scadenta ? " \u00b7 scaden\u021b\u0103 " + dataRo(f.data_scadenta) : ""}</div>
      ${partener ? `<div class="fd-antet-linie">${dir === "primit\u0103" ? "De la" : "C\u0103tre"}: ${partener}</div>` : ""}
    </div>

    <table class="fd-tabel">
      <thead>
        <tr>
          <th>Denumire</th><th>Cant</th><th>UM</th>
          <th class="fd-td-num">Pre\u021b</th><th>Cot\u0103</th><th class="fd-td-num">Valoare</th>
        </tr>
      </thead>
      <tbody>${randuriLinii || `<tr><td colspan="6" class="fd-td-den">F\u0103r\u0103 linii.</td></tr>`}</tbody>
    </table>

    <div class="fd-totaluri">
      ${randuriTot}
      <div class="fd-tot-rand fd-tot-final"><span>Total</span><span>${_bani(f.total, mon)}</span></div>
    </div>
    ${blocValuta}`;

  corp.querySelector("#fac-back")?.addEventListener("click", () => istoricFacturi(corp, nav, tenantId, opt));

  const bPlata = corp.querySelector("#fd-plata");  /* plati_fe_v1 */
  if (bPlata) bPlata.addEventListener("click", async () => {
    const zona = corp.querySelector("#fd-plata-zona");
    try {
      const r = await api.post(`/tenants/${tenantId}/facturi/${facturaId}/link-plata`, {});
      zona.innerHTML = `<div class="msg-info">Link de plat\u0103: <a href="${r.link}" target="_blank">${r.link}</a> <button class="buton-secundar em-buton-sec" id="fd-plata-copiaza">Copiaz\u0103</button></div>`;
      zona.querySelector("#fd-plata-copiaza").addEventListener("click", () => navigator.clipboard.writeText(r.link));
    } catch (e) { arataMesaj(zona, e.mesaj || e.message, "eroare"); }
  });
  // [chitante] emitere chitanta (cod 14-4-1) + lista pe factura  // chitante_fe_v1
  const bChit = corp.querySelector("#fd-chitanta");
  const zonaChit = corp.querySelector("#fd-chitanta-zona");
  const totalDeIncasat = esteValuta ? (Number(f.total_lei) || 0) : (Number(f.total) || 0);
  async function chitanteAle() {
    try {
      const r = await api.get(`/tenants/${tenantId}/chitante?factura_id=${facturaId}`);
      return (r && r.chitante) || [];
    } catch { return []; }
  }
  async function arataChitante(mesaj) {
    if (!zonaChit) return 0;
    const chi = await chitanteAle();
    const incasat = chi.reduce((s, c) => s + (Number(c.suma) || 0), 0);
    zonaChit.innerHTML = (mesaj || "") + chi.map((c) => `
      <div class="fd-tot-rand"><span>Chitan\u021ba ${c.serie}-${c.numar} \u00b7 ${dataRo(c.data)} \u00b7 ${_bani(c.suma, "lei")}</span>
      <span><button class="btn-link" data-chpdf="${c.id}">PDF chitan\u021b\u0103</button></span></div>`).join("");
    zonaChit.querySelectorAll("[data-chpdf]").forEach((b) => b.addEventListener("click", async () => {
      try {
        const r = await fetch(`/tenants/${tenantId}/chitante/${b.dataset.chpdf}/pdf`,
          { headers: { "Authorization": "Bearer " + sesiune.token() } });
        if (!r.ok) throw new Error("pdf " + r.status);
        const url = URL.createObjectURL(await r.blob());
        window.open(url, "_blank");
        setTimeout(() => URL.revokeObjectURL(url), 60000);
      } catch { b.textContent = "Eroare \u2014 re\u00eencearc\u0103"; }
    }));
    return incasat;
  }
  if (zonaChit) arataChitante();
  if (bChit) bChit.addEventListener("click", async () => {
    if (zonaChit.querySelector("#fd-chit-form")) return;
    const chi = await chitanteAle();
    const incasat = chi.reduce((s, c) => s + (Number(c.suma) || 0), 0);
    const rest = Math.max(0, Math.round((totalDeIncasat - incasat) * 100) / 100);
    zonaChit.insertAdjacentHTML("afterbegin", `
      <div id="fd-chit-form" style="display:flex;gap:8px;align-items:end;flex-wrap:wrap;margin:8px 0">
        <label class="camp"><span class="camp-eticheta">Data \u00eencas\u0103rii</span><input class="camp-input" type="date" id="fd-chit-data" value="${new Date().toISOString().slice(0, 10)}"></label>
        <label class="camp"><span class="camp-eticheta">Suma \u00eencasat\u0103 (lei)</span><input class="camp-input" type="number" step="0.01" id="fd-chit-suma" value="${rest || totalDeIncasat}"></label>
        <button class="buton-primar" id="fd-chit-ok">Emite</button>
        <button class="btn-link" id="fd-chit-nu">Renun\u021b\u0103</button>
        <span class="msg-eroare" id="fd-chit-msg"></span>
      </div>`);
    const form = zonaChit.querySelector("#fd-chit-form");
    form.querySelector("#fd-chit-nu").addEventListener("click", () => form.remove());
    form.querySelector("#fd-chit-ok").addEventListener("click", async (ev) => {
      const b = ev.currentTarget, msg = form.querySelector("#fd-chit-msg");
      const suma = parseFloat(form.querySelector("#fd-chit-suma").value) || 0;
      const data = form.querySelector("#fd-chit-data").value;
      if (suma <= 0) { msg.textContent = "Suma trebuie s\u0103 fie mai mare ca zero."; return; }
      if (!data) { msg.textContent = "Completeaz\u0103 data \u00eencas\u0103rii."; return; }
      b.disabled = true; b.textContent = "Se emite...";
      try {
        const r = await api.post(`/tenants/${tenantId}/chitante`, { data, suma, factura_id: facturaId });
        const av = (r && r.avertismente) || [];
        form.remove();
        await arataChitante(`<p style="color:#1d7a4d;font-weight:600;margin:6px 0">Chitan\u021ba ${r.serie}-${r.numar} a fost emis\u0103 \u0219i \u00eenregistrat\u0103 \u00een Registrul de cas\u0103.${av.length ? " Aten\u021bie: " + av.join(" ") : ""}</p>`);
        if (rest > 0 && suma >= rest - 0.005 && bChit) bChit.style.display = "none";
      } catch (e) {
        b.disabled = false; b.textContent = "Emite";
        msg.textContent = e.mesaj || "Eroare la emitere.";
      }
    });
  });

  const btnPdf = corp.querySelector("#fd-pdf");
  if (btnPdf) {
    btnPdf.addEventListener("click", async () => {
      const txtVechi = btnPdf.textContent;
      btnPdf.disabled = true; btnPdf.textContent = "Se genereaz\u0103\u2026";
      try {
        const r = await fetch(`/tenants/${tenantId}/facturi/${facturaId}/pdf`, {
          headers: { "Authorization": "Bearer " + sesiune.token() },
        });
        if (!r.ok) throw new Error("pdf " + r.status);
        const blob = await r.blob();
        const url = URL.createObjectURL(blob);
        window.open(url, "_blank");
        setTimeout(() => URL.revokeObjectURL(url), 60000);
      } catch {
        btnPdf.textContent = "Eroare \u2014 re\u00eencearc\u0103";
        setTimeout(() => { btnPdf.textContent = txtVechi; }, 2000);
      } finally {
        btnPdf.disabled = false;
        if (btnPdf.textContent === "Se genereaz\u0103\u2026") btnPdf.textContent = txtVechi;
      }
    });
  }

  const btnEmail = corp.querySelector("#fd-email");
  const zonaEmail = corp.querySelector("#fd-email-zona");
  if (btnEmail && zonaEmail) {
    btnEmail.addEventListener("click", () => {
      if (zonaEmail.dataset.deschis === "1") {
        zonaEmail.dataset.deschis = ""; zonaEmail.innerHTML = ""; btnEmail.classList.remove("buton-activ"); return;
      }
      const zs = corp.querySelector("#fd-storno-zona");
      if (zs) { zs.dataset.deschis = ""; zs.innerHTML = ""; }
      corp.querySelector("#fd-storno")?.classList.remove("buton-activ");
      btnEmail.classList.add("buton-activ");
      zonaEmail.dataset.deschis = "1";
      const emailPre = (f.tert_email || "");
      zonaEmail.innerHTML = `
        <div class="fd-email-box">
          <label class="fd-email-eticheta">Trimite factura ${esc(f.numar || "")} c\u0103tre:</label>
          <div class="fd-email-rand">
            <input type="email" id="fd-email-input" class="fd-email-input" placeholder="email@client.ro" value="${esc(emailPre)}">
            <button class="buton-primar fd-email-send" id="fd-email-send">Trimite</button>
          </div>
          <div class="em-rezultat" id="fd-email-rez"></div>
        </div>`;
      const inp = zonaEmail.querySelector("#fd-email-input");
      inp.focus();
      zonaEmail.querySelector("#fd-email-send").addEventListener("click", async () => {
        const rez = zonaEmail.querySelector("#fd-email-rez");
        const send = zonaEmail.querySelector("#fd-email-send");
        const email = (inp.value || "").trim();
        if (!email || email.indexOf("@") < 1 || email.indexOf(".") < 0) {
          rez.textContent = "Introdu o adres\u0103 valid\u0103."; rez.className = "em-rezultat em-rau"; inp.focus(); return;
        }
        send.disabled = true; send.textContent = "Se trimite\u2026";
        try {
          await api.post(`/tenants/${tenantId}/facturi/${facturaId}/email`, { email });
          rez.innerHTML = `\u2713 Trimis c\u0103tre <b>${esc(email)}</b>.`;
          rez.className = "em-rezultat em-bun";
          send.textContent = "Trimite";
        } catch (e) {
          rez.textContent = "Trimiterea a e\u0219uat. \u00cencearc\u0103 din nou.";
          rez.className = "em-rezultat em-rau";
          send.textContent = "Trimite";
        }
        send.disabled = false;
      });
    });
  }

  const btnStorno = corp.querySelector("#fd-storno");
  const btnTransforma = corp.querySelector("#fd-transforma");
  if (btnTransforma) btnTransforma.addEventListener("click", async () => {
    try {
      const r = await api.post(`/tenants/${tenantId}/facturi/${f.id}/transforma`, {});
      btnTransforma.outerHTML = `<span class="fac-storno-tag">factura ${r.numar} emisa</span>`;
    } catch (e) {
      btnTransforma.insertAdjacentHTML("afterend", '<span class="msg-eroare" style="margin-left:8px">' + ((e && e.mesaj) || "Nu am putut transforma.") + '</span>');
    }
  });
  const zonaStorno = corp.querySelector("#fd-storno-zona");
  if (btnStorno && zonaStorno) {
    btnStorno.addEventListener("click", () => {
      if (zonaStorno.dataset.deschis === "1") {
        zonaStorno.dataset.deschis = ""; zonaStorno.innerHTML = ""; btnStorno.classList.remove("buton-activ"); return;
      }
      const ze = corp.querySelector("#fd-email-zona");
      if (ze) { ze.dataset.deschis = ""; ze.innerHTML = ""; }
      corp.querySelector("#fd-email")?.classList.remove("buton-activ");
      btnStorno.classList.add("buton-activ");
      zonaStorno.dataset.deschis = "1";
      zonaStorno.innerHTML = `
        <div class="fd-storno-box">
          <div class="fd-storno-avert" style="margin-bottom:0">Se creeaz\u0103 o factur\u0103 de stornare pentru <b>${esc(f.numar || "")}</b> (valori negative, document contabil). Ac\u021biunea nu poate fi anulat\u0103.</div>
        </div>
        <div class="fd-storno-actiuni" style="margin:10px 0 14px">
          <button class="buton-primar" id="fd-storno-ok">Confirm stornarea</button>
          <button class="buton-secundar" id="fd-storno-nu">Renun\u021b\u0103</button>
        </div>
        <div class="em-rezultat" id="fd-storno-rez"></div>`;
      zonaStorno.querySelector("#fd-storno-nu").addEventListener("click", () => {
        zonaStorno.dataset.deschis = ""; zonaStorno.innerHTML = "";
      });
      zonaStorno.querySelector("#fd-storno-ok").addEventListener("click", async () => {
        const rez = zonaStorno.querySelector("#fd-storno-rez");
        const ok = zonaStorno.querySelector("#fd-storno-ok");
        ok.disabled = true; ok.textContent = "Se storneaz\u0103\u2026";
        try {
          const r = await api.post(`/tenants/${tenantId}/facturi/${facturaId}/storno`, {});
          rez.innerHTML = `\u2713 Storno creat: <b>${esc(r.numar || "")}</b>.`;
          rez.className = "em-rezultat em-bun";
          setTimeout(() => istoricFacturi(corp, nav, tenantId, opt), 1200);
        } catch (e) {
          rez.textContent = (e && e.mesaj) ? String(e.mesaj) : "Stornarea a e\u0219uat.";
          rez.className = "em-rezultat em-rau";
          ok.disabled = false; ok.textContent = "Confirm stornarea";
        }
      });
    });
  }
}

// ---------- MODEL FACTURA (pas 3 - placeholder) ----------
// ---------- MODEL factura (logo / font / culoare + preview live) ----------
const MF_FONTURI = {
  sans: '-apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
  serif: 'Georgia, "Times New Roman", serif',
  mono: '"Courier New", monospace',
};
const MF_CULORI = ["#5b8dd9", "#4a9d97", "#4a9d6f", "#c15a70", "#8b6fc9", "#c17d3f", "#4b5563"];

async function modelFactura(corp, nav, tenantId, opt) {
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;
  corp.querySelector("#fac-back")?.addEventListener("click", () => meniuFacturi(corp, nav, tenantId, opt));

  let profil = {};
  try {
    profil = await api.get(`/tenants/${tenantId}/firma-profil`);
  } catch {
    corp.innerHTML = `<div class="mig-gol">Nu am putut \u00eenc\u0103rca profilul firmei.</div>`;
    corp.querySelector("#fac-back")?.addEventListener("click", () => meniuFacturi(corp, nav, tenantId, opt));
    return;
  }

  // stare curenta (se editeaza in ecran, se trimite la salvare)
  const stare = {
    font: MF_FONTURI[profil.font_factura] ? profil.font_factura : "sans",
    culoare: profil.culoare_factura || "#1d4ed8",
    logo: profil.logo || "",   // data URI base64 sau ""
  };

  corp.innerHTML = `
    <h2 class="pf-titlu">Model factur\u0103</h2>
    <p class="pf-intro">Logo, font \u0219i culoare \u2014 preview live.</p>
    <div class="mf-layout">
      <div class="mf-controale">
        <div class="mf-grup">
          <label class="mf-eticheta">Logo</label>
          <div class="mf-logo-zona">
            <img id="mf-logo-preview" class="mf-logo-preview" alt="logo" ${stare.logo ? `src="${stare.logo}"` : 'style="display:none"'}>
            <label class="buton-secundar em-buton-sec mf-logo-btn">
              \u00cencarc\u0103 imagine
              <input type="file" id="mf-logo-input" accept="image/png,image/jpeg,image/svg+xml" hidden>
            </label>
            <button class="buton-sters mf-logo-sterge" id="mf-logo-sterge" ${stare.logo ? "" : 'style="display:none"'}>\u0218terge</button>
          </div>
          <div class="mf-logo-info">PNG, JPG sau SVG \u00b7 max 500 KB \u00b7 ideal ~400px l\u0103\u021bime</div>
          <div class="mf-logo-msg" id="mf-logo-msg"></div>
        </div>
        <div class="mf-grup">
          <label class="mf-eticheta">Font</label>
          <div class="mf-fonturi">
            <button class="mf-font-opt" data-font="sans">Sans</button>
            <button class="mf-font-opt" data-font="serif">Serif</button>
            <button class="mf-font-opt" data-font="mono">Mono</button>
          </div>
        </div>
        <div class="mf-grup">
          <label class="mf-eticheta">Culoare accent</label>
          <div class="mf-culori">
            ${MF_CULORI.map((c) => `<button class="mf-culoare-opt" data-culoare="${c}" style="background:${c}" title="${c}"></button>`).join("")}
          </div>
        </div>
        <button class="buton-primar mf-salveaza" id="mf-salveaza">Salveaz\u0103</button>
        <div class="em-rezultat" id="mf-rezultat"></div>
      </div>
      <div class="mf-preview-wrap">
        <div class="mf-preview" id="mf-preview"></div>
      </div>
    </div>`;

  corp.querySelector("#fac-back")?.addEventListener("click", () => meniuFacturi(corp, nav, tenantId, opt));

  const preview = corp.querySelector("#mf-preview");

  function randPreview() {
    const ff = MF_FONTURI[stare.font];
    const ac = stare.culoare;
    const nr = (profil.serie_factura || "") + (profil.urmator_numar_factura || "1");
    const adr = [profil.adresa, profil.oras, profil.judet].filter(Boolean).join(", ");
    preview.style.fontFamily = ff;
    preview.innerHTML = `
      <div class="mfp-antet" style="border-color:${ac}">
        <div class="mfp-firma">
          ${stare.logo ? `<img src="${stare.logo}" class="mfp-logo">` : ""}
          <div>
            <div class="mfp-nume" style="color:${ac}">${esc(profil.nume || "Firma mea SRL")}</div>
            <div class="mfp-detalii">CUI ${esc(profil.cui || "\u2014")}${adr ? " \u00b7 " + esc(adr) : ""}</div>
            ${profil.iban ? `<div class="mfp-detalii">IBAN ${esc(profil.iban)}</div>` : ""}
          </div>
        </div>
        <div class="mfp-titlu" style="color:${ac}">FACTUR\u0102<br><span class="mfp-nr">${esc(nr)}</span></div>
      </div>
      <table class="mfp-tabel">
        <thead><tr style="background:${ac}">
          <th>Denumire</th><th class="mfp-num">Cant</th><th class="mfp-num">Pre\u021b</th><th class="mfp-num">Valoare</th>
        </tr></thead>
        <tbody>
          <tr><td>Serviciu exemplu</td><td class="mfp-num">1</td><td class="mfp-num">1.000,00</td><td class="mfp-num">1.000,00</td></tr>
          <tr><td>Produs exemplu</td><td class="mfp-num">2</td><td class="mfp-num">250,00</td><td class="mfp-num">500,00</td></tr>
        </tbody>
      </table>
      <div class="mfp-totaluri">
        <div><span>Baz\u0103</span><span>1.500,00</span></div>
        <div><span>TVA 21%</span><span>315,00</span></div>
        <div class="mfp-total" style="color:${ac}"><span>Total</span><span>1.815,00 lei</span></div>
      </div>`;
  }

  function marcheaza() {
    corp.querySelectorAll(".mf-font-opt").forEach((b) =>
      b.classList.toggle("mf-activ", b.dataset.font === stare.font));
    corp.querySelectorAll(".mf-culoare-opt").forEach((b) =>
      b.classList.toggle("mf-activ", b.dataset.culoare === stare.culoare));
  }

  // font
  corp.querySelectorAll(".mf-font-opt").forEach((b) =>
    b.addEventListener("click", () => { stare.font = b.dataset.font; marcheaza(); randPreview(); }));
  // culoare
  corp.querySelectorAll(".mf-culoare-opt").forEach((b) =>
    b.addEventListener("click", () => { stare.culoare = b.dataset.culoare; marcheaza(); randPreview(); }));
  // logo upload -> base64
  corp.querySelector("#mf-logo-input").addEventListener("change", (e) => {
    const file = e.target.files && e.target.files[0];
    const msg = corp.querySelector("#mf-logo-msg");
    if (!file) return;
    const kb = Math.round(file.size / 1024);
    if (file.size > 500 * 1024) {
      msg.className = "mf-logo-msg mf-logo-msg-rau";
      msg.innerHTML = `Imaginea are ${kb} KB (limita 500 KB). Mic\u0219oreaz-o la ~400px l\u0103\u021bime \u2014 \u00een Paint (Redimensionare) sau pe tinypng.com \u2014 \u0219i \u00eencarc-o din nou.`;
      e.target.value = "";
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      stare.logo = reader.result;
      const img = corp.querySelector("#mf-logo-preview");
      img.src = stare.logo; img.style.display = "";
      corp.querySelector("#mf-logo-sterge").style.display = "";
      msg.className = "mf-logo-msg mf-logo-msg-bun";
      msg.textContent = `\u2713 Logo \u00eenc\u0103rcat (${kb} KB).`;
      randPreview();
    };
    reader.readAsDataURL(file);
  });
  // sterge logo
  corp.querySelector("#mf-logo-sterge").addEventListener("click", () => {
    stare.logo = "";
    corp.querySelector("#mf-logo-preview").style.display = "none";
    corp.querySelector("#mf-logo-sterge").style.display = "none";
    const msg = corp.querySelector("#mf-logo-msg");
    if (msg) { msg.textContent = ""; msg.className = "mf-logo-msg"; }
    randPreview();
  });
  // salveaza
  corp.querySelector("#mf-salveaza").addEventListener("click", async () => {
    const rez = corp.querySelector("#mf-rezultat");
    const btn = corp.querySelector("#mf-salveaza");
    btn.disabled = true; btn.textContent = "Se salveaz\u0103\u2026";
    try {
      await api.post(`/tenants/${tenantId}/firma-profil/model`, {
        font: stare.font, culoare: stare.culoare, logo: stare.logo,
      });
      rez.textContent = "\u2713 Model salvat.";
      rez.className = "em-rezultat em-bun";
    } catch {
      rez.textContent = "Salvarea a e\u0219uat. \u00cencearc\u0103 din nou.";
      rez.className = "em-rezultat em-rau";
    }
    btn.disabled = false; btn.textContent = "Salveaz\u0103";
  });

  marcheaza();
  randPreview();
}


// ---------- RECURENTE ----------  // fac_recurente_v1
async function listaRecurente(corp, nav, tenantId, opt) {
  const inapoiMeniu = () => meniuFacturi(corp, nav, tenantId, opt);
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;
  corp.querySelector("#fac-back")?.addEventListener("click", inapoiMeniu);
  let sabloane = [];
  try {
    const r = await api.get(`/tenants/${tenantId}/facturi-recurente`);
    sabloane = (r && r.sabloane) || [];
  } catch {}
  randareRecurente(corp, nav, tenantId, opt, sabloane);
}

function randareRecurente(corp, nav, tenantId, opt, sabloane) {
  const inapoiMeniu = () => meniuFacturi(corp, nav, tenantId, opt);
  const corpuri = !sabloane.length
    ? `<div class="mig-gol">Niciun \u0219ablon \u00eenc\u0103.</div>`
    : sabloane.map((s) => {
        const suma = (s.linii || []).reduce((t, l) => t + (Number(l.cantitate) || 0) * (Number(l.pret_unitar) || 0), 0);
        const sumaTxt = bani(suma) + " " + (s.moneda || "RON");
        const stare = s.activ
          ? '<span style="color:#1d7a4d">activ</span>'
          : '<span style="color:var(--gri-clar)">inactiv</span>';
        return `
      <div class="pf-frand" data-id="${s.id}">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(s.tert_nume) || "\u2014"}</div>
          <div class="pf-frand-sub">ziua ${s.zi_emitere} \u00b7 ultima: ${dataRo(s.ultima_emitere) || "\u2014"} \u00b7 ${stare}</div>
        </div>
        <span class="pf-frand-suma">${sumaTxt}</span>
        <span class="btn-link fr-toggle" data-id="${s.id}" data-activ="${s.activ}" style="margin-left:8px">${s.activ ? "Dezactiveaz\u0103" : "Activeaz\u0103"}</span>
        <span class="btn-link fr-sterge" data-id="${s.id}" style="margin-left:8px;color:var(--rosu)">\u0218terge</span>
      </div>`;
      }).join("");

  corp.innerHTML = `
    <h2 class="pf-titlu">Facturi recurente</h2>
    <p class="pf-intro">\u0218abloane emise automat \u00een fiecare lun\u0103 (verificare zilnic\u0103 la 07:00).</p>
    <div class="pf-lista zebra-lista">${corpuri}</div>
    <button class="buton-primar" id="fr-add" style="margin-top:12px">+ \u0218ablon nou</button>`;
  corp.querySelector("#fac-back")?.addEventListener("click", inapoiMeniu);
  corp.querySelector("#fr-add").addEventListener("click", () => nav.mergi("\u0218ablon nou", (c) => formSablon(c, nav, tenantId, opt)));  // faza_b_traseu_v1

  corp.querySelectorAll(".fr-toggle").forEach((b) => b.addEventListener("click", async () => {
    const activNou = !(b.dataset.activ === "true");
    try {
      await api.put(`/tenants/${tenantId}/facturi-recurente/${b.dataset.id}?activ=${activNou}`);
      listaRecurente(corp, nav, tenantId, opt);
    } catch (e) {
      corp.querySelectorAll(".msg-eroare").forEach((x) => x.remove());
      corp.insertAdjacentHTML("afterbegin", '<p class="msg-eroare">' + (e.mesaj || e.message || "Eroare.") + '</p>');
    }
  }));
  corp.querySelectorAll(".fr-sterge").forEach((b) => b.addEventListener("click", () => {
    confirmaCaseta(b.parentElement, "\u0218tergi \u0219ablonul?", async () => {
      try {
        await api.del(`/tenants/${tenantId}/facturi-recurente/${b.dataset.id}`);
        listaRecurente(corp, nav, tenantId, opt);
      } catch (e) {
        corp.querySelectorAll(".msg-eroare").forEach((x) => x.remove());
        corp.insertAdjacentHTML("afterbegin", '<p class="msg-eroare">' + (e.mesaj || e.message || "Eroare.") + '</p>');
      }
    }, { textOk: "\u0218terge" });
  }));
}

// ---------- ADAUGA SABLON ----------  // fac_recurente_v1
function formSablon(corp, nav, tenantId, opt) {
  const inapoiLista = () => nav.inapoiPas();  // faza_b_traseu_v1
  corp.innerHTML = `
    <h2 class="pf-titlu">\u0218ablon nou</h2>

    <div class="em-sectiune">
      <div class="em-eticheta">Beneficiar</div>
      <label class="camp-eticheta" for="fr-cui">CUI beneficiar</label>
      <input class="pr-input" id="fr-cui" placeholder="ex: RO12345678" autocomplete="off">
      <label class="camp-eticheta" for="fr-nume">Denumire beneficiar</label>
      <input class="pr-input" id="fr-nume" autocomplete="off">
    </div>

    <div class="em-sectiune">
      <div class="em-eticheta">Produse \u0219i servicii</div>
      <div class="camp-eticheta">Linie: denumire \u00b7 cantitate \u00b7 pre\u021b unitar \u00b7 cot\u0103 TVA</div>
      <div class="em-linii" id="fr-linii"></div>
      <button class="buton-secundar em-buton-sec" id="fr-add-linie">+ Adaug\u0103 linie</button>
    </div>

    <div class="em-sectiune">
      <div class="em-eticheta">Emitere</div>
      <input class="pr-input" id="fr-zi" type="number" min="1" max="28" placeholder="1" title="Ziua din lun\u0103 la care se emite">
      <select class="pr-input" id="fr-moneda">
        <option value="RON">RON</option>
        <option value="EUR">EUR</option>
        <option value="USD">USD</option>
      </select>
    </div>

    <div class="em-actiuni">
      <button class="buton-primar" id="fr-salveaza">Salveaz\u0103 \u0219ablonul</button>
    </div>
    <div class="em-rezultat" id="fr-rezultat"></div>`;
  corp.querySelector("#fr-back").addEventListener("click", inapoiLista);

  const zonaLinii = corp.querySelector("#fr-linii");
  const linii = [];

  function adaugaLinie() {
    const idx = linii.length;
    linii.push({ descriere: "", cantitate: 1, pret_unitar: 0, cota_tva: null });
    const rand = document.createElement("div");
    rand.className = "em-linie";
    rand.dataset.idx = idx;
    rand.innerHTML = `
      <input class="pr-input em-l-den" placeholder="Denumire (ex: abonament mentenan\u021b\u0103)" aria-label="Denumire articol" autocomplete="off">
      <input class="pr-input em-l-cant" type="number" step="0.001" placeholder="Cant." aria-label="Cantitate" title="Cantitate">
      <input class="pr-input em-l-pret" type="number" step="0.01" placeholder="Pre\u021b" aria-label="Pre\u021b unitar" title="Pre\u021b unitar">
      <span class="em-l-cota" title="Cota TVA">\u2014</span>
      <button class="buton-sters em-l-sterge" title="\u0218terge">\u00d7</button>`;
    zonaLinii.appendChild(rand);

    const den = rand.querySelector(".em-l-den");
    const cant = rand.querySelector(".em-l-cant");
    const pret = rand.querySelector(".em-l-pret");
    const cotaEl = rand.querySelector(".em-l-cota");

    let timer = null;
    den.addEventListener("input", () => {
      linii[idx].descriere = den.value.trim();
      linii[idx].cota_tva = null;
      clearTimeout(timer);
      const d = den.value.trim();
      if (d.length < 3) { cotaEl.textContent = "\u2014"; return; }
      cotaEl.textContent = "\u2026";
      timer = setTimeout(async () => {
        try {
          const r = await api.post(`/tenants/${tenantId}/produse/potriveste`, { denumire: d });
          if (r && r.ok) {
            linii[idx].cota_tva = r.cota;
            cotaEl.textContent = r.cota === 0 ? "scutit" : r.cota + "%";
          } else {
            cotaEl.textContent = "\u2014";
          }
        } catch { cotaEl.textContent = "\u2014"; }
      }, 400);
    });
    cant.addEventListener("input", () => { linii[idx].cantitate = Number(cant.value) || 0; });
    pret.addEventListener("input", () => { linii[idx].pret_unitar = Number(pret.value) || 0; });
    rand.querySelector(".em-l-sterge").addEventListener("click", () => {
      linii.splice(idx, 1);
      rand.remove();
    });
  }
  adaugaLinie();
  corp.querySelector("#fr-add-linie").addEventListener("click", adaugaLinie);

  corp.querySelector("#fr-salveaza").addEventListener("click", async () => {
    const zona = corp.querySelector("#fr-rezultat");
    const corpCerere = {
      tert_cui: corp.querySelector("#fr-cui").value.trim() || null,
      tert_nume: corp.querySelector("#fr-nume").value.trim(),
      zi_emitere: Number(corp.querySelector("#fr-zi").value) || 1,
      moneda: corp.querySelector("#fr-moneda").value,
      linii: linii.filter((l) => l.descriere && l.cantitate),
    };
    try {
      await api.post(`/tenants/${tenantId}/facturi-recurente`, corpCerere);
      inapoiLista();
    } catch (e) {
      zona.innerHTML = `<span style="color:var(--rosu)">${e.mesaj || e.message || "eroare"}</span>`;
    }
  });
}

// chitante_fe_v1

// chitante_fe_v2_etichete

// audit_cab_lot1_v1

// faza_b_traseu_v1

// fara_precompletari_v1
