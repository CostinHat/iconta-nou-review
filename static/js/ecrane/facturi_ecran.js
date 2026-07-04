// facturi_ecran.js — cardul Facturi consolidat, REUTILIZABIL (portal client, gratuit, cabinet).
// Primeste tenantId -> merge din orice context. Contine:
//   meniu (Istoric / Emite / Model factura) + istoric + emitere.
//   Detalii / Storno / Model se adauga in pasii urmatori.
// Apelare: randeazaFacturi(corp, nav, tenantId, { inapoi, titluInapoi })
import { api } from "../api.js";
import { sesiune } from "../sesiune.js";
import { randeazaEmitere } from "./emitere_ecran.js";

const fmtData = (iso) => {
  if (!iso) return "";
  const p = String(iso).split("-");
  return p.length === 3 ? `${p[2]}.${p[1]}.${p[0]}` : iso;
};
const dirEticheta = (d) => (d === "iesire" || d === "emisa") ? "emis\u0103"
  : (d === "intrare" || d === "primita") ? "primit\u0103" : (d || "");

export function randeazaFacturi(corp, nav, tenantId, opt = {}) {
  meniuFacturi(corp, nav, tenantId, opt);
}

// ---------- MENIU (Istoric / Emite / Model) ----------
function meniuFacturi(corp, nav, tenantId, opt) {
  const inapoi = opt.inapoi || (() => nav && nav.inapoi && nav.inapoi());
  const titluInapoi = opt.titluInapoi || "Inapoi";
  corp.innerHTML = `
    <h2 class="pf-titlu">Facturi</h2>
    <p class="pf-intro">Ce vrei s\u0103 faci?</p>
    <div class="fac-meniu">
      <button class="fac-optiune" id="fac-istoric">
        <div class="fac-opt-titlu">Istoric facturi</div>
        <div class="fac-opt-sub">Facturile emise \u0219i primite</div>
      </button>
      <button class="fac-optiune" id="fac-emite">
        <div class="fac-opt-titlu">Emite factur\u0103</div>
        <div class="fac-opt-sub">Creeaz\u0103 o factur\u0103 nou\u0103</div>
      </button>
      <button class="fac-optiune" id="fac-model">
        <div class="fac-opt-titlu">Model factur\u0103</div>
        <div class="fac-opt-sub">Logo, font \u0219i culoare</div>
      </button>
    </div>`;
  corp.querySelector("#fac-istoric").addEventListener("click", () => istoricFacturi(corp, nav, tenantId, opt));
  corp.querySelector("#fac-emite").addEventListener("click", () => emiteFactura(corp, nav, tenantId, opt));
  corp.querySelector("#fac-model").addEventListener("click", () => modelFactura(corp, nav, tenantId, opt));
}

// ---------- ISTORIC ----------
async function istoricFacturi(corp, nav, tenantId, opt) {
  const inapoiMeniu = () => meniuFacturi(corp, nav, tenantId, opt);
  corp.innerHTML = `<button class="mig-inapoi" id="fac-back">\u2190</button><p class="ecran-nota">Se incarca...</p>`;
  corp.querySelector("#fac-back").addEventListener("click", inapoiMeniu);
  let lista = [];
  try {
    const r = await api.get(`/tenants/${tenantId}/facturi`);
    lista = (r && r.facturi) || [];
  } catch {}
  let corpuri = !lista.length
    ? `<div class="mig-gol">Nicio factura inregistrata inca.</div>`
    : lista.map((f) => {
        const suma = f.total != null ? Number(f.total).toLocaleString("ro-RO") + " " + (f.moneda || "lei") : "";
        const dir = dirEticheta(f.directie);
        const storno = f.storno_din_id ? ' \u00b7 <span class="fac-storno-tag">storno</span>' : "";
        return `
      <button class="pf-frand fac-frand-btn" data-id="${f.id}">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${f.numar || "\u2014"}${f.tert_nume ? " \u00b7 " + f.tert_nume : ""}</div>
          <div class="pf-frand-sub">${fmtData(f.data_emitere)}${dir ? " \u00b7 " + dir : ""}${storno}</div>
        </div>
        <span class="pf-frand-suma">${suma}</span>
        <span class="btn-link fac-cont" data-cid="${f.id}" style="margin-left:8px">Conteaz\u0103</span>
      </button>`;
      }).join("");
  corp.innerHTML = `
    <button class="mig-inapoi" id="fac-back">\u2190</button>
    <h2 class="pf-titlu">Istoric facturi</h2>
    <p class="pf-intro">Apas\u0103 o factur\u0103 pentru detalii.</p>
    <div class="pf-lista">${corpuri}</div>`;
  corp.querySelector("#fac-back").addEventListener("click", inapoiMeniu);
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
    b.addEventListener("click", () => detaliiFactura(corp, nav, tenantId, b.dataset.id, opt));
  });
}

// ---------- EMITE ----------
function emiteFactura(corp, nav, tenantId, opt) {
  randeazaEmitere(corp, nav, tenantId, {
    inapoi: () => meniuFacturi(corp, nav, tenantId, opt),
    dupaEmitere: () => istoricFacturi(corp, nav, tenantId, opt),
  });
}

// ---------- DETALII factura ----------
const _esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const _bani = (x, mon) => {
  if (x == null || x === "") return "";
  const n = Number(x).toLocaleString("ro-RO", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  return mon ? `${n} ${mon}` : n;
};

async function detaliiFactura(corp, nav, tenantId, facturaId, opt) {
  corp.innerHTML = `<button class="mig-inapoi" id="fac-back">\u2190</button><p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;
  corp.querySelector("#fac-back").addEventListener("click", () => istoricFacturi(corp, nav, tenantId, opt));

  let f = null;
  try {
    f = await api.get(`/tenants/${tenantId}/facturi/${facturaId}`);
  } catch {
    corp.innerHTML = `<button class="mig-inapoi" id="fac-back">\u2190</button><div class="mig-gol">Nu am putut \u00eenc\u0103rca factura.</div>`;
    corp.querySelector("#fac-back").addEventListener("click", () => istoricFacturi(corp, nav, tenantId, opt));
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
        <td class="fd-td-den">${_esc(l.descriere)}</td>
        <td class="fd-td-num">${cant.toLocaleString("ro-RO")}</td>
        <td class="fd-td-um">${_esc(l.um || "buc")}</td>
        <td class="fd-td-num">${_bani(pret)}</td>
        <td class="fd-td-num">${cota}%</td>
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
        <div class="fd-valuta-sub">${sursaTxt} ${f.curs_bnr ? Number(f.curs_bnr).toLocaleString("ro-RO", { minimumFractionDigits: 4 }) : ""} ${f.data_curs ? "\u00b7 " + fmtData(f.data_curs) : ""}</div>
      </div>`;
  }

  const dir = dirEticheta(f.directie);
  const partener = f.tert_nume ? `${_esc(f.tert_nume)}${f.tert_cui ? " \u00b7 CUI " + _esc(f.tert_cui) : ""}` : "";
  const statusTxt = f.storno_din_id ? "storno" : (f.status || "");

  corp.innerHTML = `
    <button class="mig-inapoi" id="fac-back">\u2190</button>
    <div class="fd-antet">
      <div class="fd-antet-sus">
        <h2 class="pf-titlu">${_esc(f.numar || "\u2014")}</h2>
        ${statusTxt ? `<span class="fac-storno-tag">${_esc(statusTxt)}</span>` : ""}
        <button class="em-buton-sec fd-pdf-btn" id="fd-pdf">Vezi PDF</button>
        <button class="em-buton-sec fd-email-btn" id="fd-email">Trimite pe email</button>
        ${(f.directie === "emisa" && !f.storno_din_id) ? '<button class="em-buton-sec fd-storno-btn" id="fd-storno">Storneaz\u0103</button>' : ""}
      </div>
      <div class="fd-email-zona" id="fd-email-zona"></div>
      <div class="fd-storno-zona" id="fd-storno-zona"></div>
      <div class="fd-antet-linie">${dir ? dir.charAt(0).toUpperCase() + dir.slice(1) : ""} \u00b7 ${fmtData(f.data_emitere)}${f.data_scadenta ? " \u00b7 scaden\u021b\u0103 " + fmtData(f.data_scadenta) : ""}</div>
      ${partener ? `<div class="fd-antet-linie">${dir === "primit\u0103" ? "De la" : "C\u0103tre"}: ${partener}</div>` : ""}
    </div>

    <table class="fd-tabel">
      <thead>
        <tr>
          <th>Denumire</th><th class="fd-td-num">Cant</th><th>UM</th>
          <th class="fd-td-num">Pre\u021b</th><th class="fd-td-num">Cot\u0103</th><th class="fd-td-num">Valoare</th>
        </tr>
      </thead>
      <tbody>${randuriLinii || `<tr><td colspan="6" class="fd-td-den">F\u0103r\u0103 linii.</td></tr>`}</tbody>
    </table>

    <div class="fd-totaluri">
      ${randuriTot}
      <div class="fd-tot-rand fd-tot-final"><span>Total</span><span>${_bani(f.total, mon)}</span></div>
    </div>
    ${blocValuta}`;

  corp.querySelector("#fac-back").addEventListener("click", () => istoricFacturi(corp, nav, tenantId, opt));

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
        zonaEmail.dataset.deschis = ""; zonaEmail.innerHTML = ""; return;
      }
      zonaEmail.dataset.deschis = "1";
      const emailPre = (f.tert_email || "");
      zonaEmail.innerHTML = `
        <div class="fd-email-box">
          <label class="fd-email-eticheta">Trimite factura ${_esc(f.numar || "")} c\u0103tre:</label>
          <div class="fd-email-rand">
            <input type="email" id="fd-email-input" class="fd-email-input" placeholder="email@client.ro" value="${_esc(emailPre)}">
            <button class="mig-buton fd-email-send" id="fd-email-send">Trimite</button>
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
          rez.innerHTML = `\u2713 Trimis c\u0103tre <b>${_esc(email)}</b>.`;
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
  const zonaStorno = corp.querySelector("#fd-storno-zona");
  if (btnStorno && zonaStorno) {
    btnStorno.addEventListener("click", () => {
      if (zonaStorno.dataset.deschis === "1") {
        zonaStorno.dataset.deschis = ""; zonaStorno.innerHTML = ""; return;
      }
      zonaStorno.dataset.deschis = "1";
      zonaStorno.innerHTML = `
        <div class="fd-storno-box">
          <div class="fd-storno-avert">Se creeaz\u0103 o factur\u0103 de stornare pentru <b>${_esc(f.numar || "")}</b> (valori negative, document contabil). Ac\u021biunea nu poate fi anulat\u0103.</div>
          <div class="fd-storno-actiuni">
            <button class="mig-buton fd-storno-ok" id="fd-storno-ok">Confirm stornarea</button>
            <button class="em-buton-sec" id="fd-storno-nu">Renun\u021b\u0103</button>
          </div>
          <div class="em-rezultat" id="fd-storno-rez"></div>
        </div>`;
      zonaStorno.querySelector("#fd-storno-nu").addEventListener("click", () => {
        zonaStorno.dataset.deschis = ""; zonaStorno.innerHTML = "";
      });
      zonaStorno.querySelector("#fd-storno-ok").addEventListener("click", async () => {
        const rez = zonaStorno.querySelector("#fd-storno-rez");
        const ok = zonaStorno.querySelector("#fd-storno-ok");
        ok.disabled = true; ok.textContent = "Se storneaz\u0103\u2026";
        try {
          const r = await api.post(`/tenants/${tenantId}/facturi/${facturaId}/storno`, {});
          rez.innerHTML = `\u2713 Storno creat: <b>${_esc(r.numar || "")}</b>.`;
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
const MF_CULORI = ["#1d4ed8", "#0a807b", "#1d7a4d", "#a3344b", "#6d28d9", "#b45309"];

async function modelFactura(corp, nav, tenantId, opt) {
  corp.innerHTML = `<button class="mig-inapoi" id="fac-back">\u2190</button><p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;
  corp.querySelector("#fac-back").addEventListener("click", () => meniuFacturi(corp, nav, tenantId, opt));

  let profil = {};
  try {
    profil = await api.get(`/tenants/${tenantId}/firma-profil`);
  } catch {
    corp.innerHTML = `<button class="mig-inapoi" id="fac-back">\u2190</button><div class="mig-gol">Nu am putut \u00eenc\u0103rca profilul firmei.</div>`;
    corp.querySelector("#fac-back").addEventListener("click", () => meniuFacturi(corp, nav, tenantId, opt));
    return;
  }

  // stare curenta (se editeaza in ecran, se trimite la salvare)
  const stare = {
    font: MF_FONTURI[profil.font_factura] ? profil.font_factura : "sans",
    culoare: profil.culoare_factura || "#1d4ed8",
    logo: profil.logo || "",   // data URI base64 sau ""
  };

  corp.innerHTML = `
    <button class="mig-inapoi" id="fac-back">\u2190</button>
    <h2 class="pf-titlu">Model factur\u0103</h2>
    <p class="pf-intro">Logo, font \u0219i culoare \u2014 preview live.</p>
    <div class="mf-layout">
      <div class="mf-controale">
        <div class="mf-grup">
          <label class="mf-eticheta">Logo</label>
          <div class="mf-logo-zona">
            <img id="mf-logo-preview" class="mf-logo-preview" alt="logo" ${stare.logo ? `src="${stare.logo}"` : 'style="display:none"'}>
            <label class="em-buton-sec mf-logo-btn">
              \u00cencarc\u0103 imagine
              <input type="file" id="mf-logo-input" accept="image/png,image/jpeg,image/svg+xml" hidden>
            </label>
            <button class="mf-logo-sterge" id="mf-logo-sterge" ${stare.logo ? "" : 'style="display:none"'}>\u0218terge</button>
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
        <button class="mig-buton mf-salveaza" id="mf-salveaza">Salveaz\u0103</button>
        <div class="em-rezultat" id="mf-rezultat"></div>
      </div>
      <div class="mf-preview-wrap">
        <div class="mf-preview" id="mf-preview"></div>
      </div>
    </div>`;

  corp.querySelector("#fac-back").addEventListener("click", () => meniuFacturi(corp, nav, tenantId, opt));

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
            <div class="mfp-nume" style="color:${ac}">${_esc(profil.nume || "Firma mea SRL")}</div>
            <div class="mfp-detalii">CUI ${_esc(profil.cui || "\u2014")}${adr ? " \u00b7 " + _esc(adr) : ""}</div>
            ${profil.iban ? `<div class="mfp-detalii">IBAN ${_esc(profil.iban)}</div>` : ""}
          </div>
        </div>
        <div class="mfp-titlu" style="color:${ac}">FACTUR\u0102<br><span class="mfp-nr">${_esc(nr)}</span></div>
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
