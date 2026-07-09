// produse_ecran.js  // [p123_scot_butoane] — nomenclator de produse, reutilizabil (portal, cabinet, gratuit).
// Scrii denumirea -> AI potriveste cota TVA din regula oficiala (preview live) ->
// vezi cota + justificarea -> salvezi. Cota se poate corecta manual.
// Apelare: randeazaProduse(corp, nav, tenantId, { inapoi })
import { api, arataMesaj, confirmaCaseta } from "../api.js";  /* cap6_catch_v1b + investigatie_identitate_v1 */

const SVG_BACK = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>';

export async function randeazaProduse(corp, nav, tenantId, opt = {}) {
  const inapoi = opt.inapoi || (() => nav && nav.inapoi && nav.inapoi());
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;

  let lista = [];
  try {
    const r = await api.get(`/tenants/${tenantId}/produse`);
    lista = (r && r.produse) || [];
  } catch {}

  corp.innerHTML = `
    
    <div class="pr-cap">
      <h2 class="pf-titlu">Produse \u0219i servicii</h2>
      <button class="buton-primar pr-add" id="pr-add">+ Adaug\u0103 produs</button>
    </div>
    <p class="pf-intro">Scrii denumirea, iar sistemul potrive\u0219te automat cota de TVA corect\u0103 din legisla\u021bie. O po\u021bi corecta oric\u00e2nd.</p>
    <div class="pr-form-zona" id="pr-form-zona"></div>
    <div class="pr-lista" id="pr-lista"></div>
  `;
  corp.querySelector("#pr-add").addEventListener("click", () => formularAdauga(corp, tenantId, () => randeazaProduse(corp, nav, tenantId, opt)));

  randeazaLista(corp, tenantId, lista, () => randeazaProduse(corp, nav, tenantId, opt));
}

function badgeCota(cota, sursa) {
  const c = Number(cota);
  const cls = c === 0 ? "prc-0" : (c === 11 ? "prc-11" : "prc-21");
  const eticheta = c === 0 ? "f\u0103r\u0103 TVA" : `TVA ${c}%`;
  const semn = sursa === "ai" ? " \u00b7 AI" : (sursa === "fallback" ? " \u00b7 verific\u0103" : "");
  return `<span class="pr-badge ${cls}">${eticheta}${semn}</span>`;
}

function randeazaLista(corp, tenantId, lista, reincarca) {
  const zona = corp.querySelector("#pr-lista");
  if (!zona) return;
  if (!lista.length) {
    zona.innerHTML = `<div class="mig-gol">Niciun produs \u00eenc\u0103. Adaug\u0103 primul produs — cota se completeaz\u0103 automat.</div>`;
    return;
  }
  zona.innerHTML = lista.map((p) => `
    <div class="pr-rand" data-id="${p.id}">
      <div class="pr-rand-text">
        <div class="pr-rand-nume">${p.denumire}</div>
        <div class="pr-rand-sub">${p.pret_unitar ? Number(p.pret_unitar).toLocaleString("ro-RO") + " lei / " + (p.um || "buc") : (p.um || "buc")}${p.justificare ? " \u00b7 " + p.justificare : ""}</div>
      </div>
      <div class="pr-rand-drept">
        ${badgeCota(p.cota_tva, p.sursa)}
        <button class="buton-sters pr-sterge" data-id="${p.id}" title="\u0218terge" aria-label="\u0218terge">\u00d7</button>
      </div>
    </div>`).join("");
  zona.querySelectorAll(".pr-sterge").forEach((b) => {
    b.addEventListener("click", (e) => {
      e.stopPropagation();
      const id = b.dataset.id;
      confirmaCaseta(b.parentElement || b, "\u0218tergi produsul?", async () => {
        try { await api.del(`/tenants/${tenantId}/produse/${id}`); reincarca(); }
        catch (er) { arataMesaj(zona.querySelector("#pr-form-zona"), er.mesaj || "Nu am putut \u0219terge produsul.", "eroare"); }
      });
    });
  });
}

function formularAdauga(corp, tenantId, reincarca) {
  const zona = corp.querySelector("#pr-form-zona");
  if (!zona) return;
  zona.innerHTML = `
    <div class="pr-form">
      <div class="pr-form-rand">
        <label class="camp-eticheta" for="pr-den">Denumire produs sau serviciu</label>
        <input class="pr-input pr-den" id="pr-den" placeholder="ex: paine alba, consultanta" autocomplete="off">
      </div>
      <div class="pr-cota-preview" id="pr-cota-preview"></div>
      <div class="camp-eticheta">Pre\u021b \u00b7 unitate de m\u0103sur\u0103 \u00b7 cot\u0103 TVA</div>
      <div class="pr-form-rand pr-form-detalii">
        <input class="pr-input pr-mic" id="pr-pret" type="number" step="0.01" placeholder="Pre\u021b" aria-label="Pre\u021b">
        <input class="pr-input pr-mic" id="pr-um" placeholder="UM (buc)" aria-label="Unitate de m\u0103sur\u0103" value="buc">
        <select class="pr-input pr-mic" id="pr-cota">
          <option value="">cot\u0103 (auto)</option>
          <option value="21">21%</option>
          <option value="11">11%</option>
          <option value="0">scutit / f\u0103r\u0103 TVA (art. 292)</option>
        </select>
      </div>
      <div class="pr-form-actiuni">
        <button class="buton-primar" id="pr-salveaza">Salveaz\u0103</button>
        <button class="buton-secundar pr-anuleaza" id="pr-anuleaza">Renun\u021b\u0103</button>
      </div>
    </div>
  `;
  const inputDen = zona.querySelector("#pr-den");
  const preview = zona.querySelector("#pr-cota-preview");
  const selCota = zona.querySelector("#pr-cota");
  inputDen.focus();

  // potrivire AI live (debounce), doar daca utilizatorul nu a ales manual cota
  let timer = null, ultimaDenum = "";
  inputDen.addEventListener("input", () => {
    const d = inputDen.value.trim();
    if (selCota.value) { preview.innerHTML = ""; return; }  // a ales manual
    clearTimeout(timer);
    if (d.length < 3) { preview.innerHTML = ""; return; }
    preview.innerHTML = `<span class="pr-cota-cauta">se verific\u0103 cota\u2026</span>`;
    timer = setTimeout(async () => {
      if (d === ultimaDenum) return;
      ultimaDenum = d;
      try {
        const r = await api.post(`/tenants/${tenantId}/produse/potriveste`, { denumire: d });
        if (r && r.ok) {
          preview.innerHTML = `<div class="pr-cota-rezultat">
            ${badgeCota(r.cota, r.sursa)}
            <span class="pr-cota-just">${r.justificare || ""}</span>
          </div>`;
        } else { preview.innerHTML = ""; }
      } catch { preview.innerHTML = ""; }
    }, 600);
  });

  zona.querySelector("#pr-anuleaza").addEventListener("click", () => { zona.innerHTML = ""; });
  zona.querySelector("#pr-salveaza").addEventListener("click", async () => {
    const denumire = inputDen.value.trim();
    if (!denumire) { inputDen.focus(); return; }
    const payload = {
      denumire,
      um: zona.querySelector("#pr-um").value.trim() || "buc",
      pret_unitar: parseFloat(zona.querySelector("#pr-pret").value) || 0,
    };
    const cotaMan = selCota.value;
    if (cotaMan !== "") payload.cota_tva = parseFloat(cotaMan);
    try {
      await api.post(`/tenants/${tenantId}/produse`, payload);
      zona.innerHTML = "";
      reincarca();
    } catch {}
  });
}
