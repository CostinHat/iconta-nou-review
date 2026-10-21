// produse_ecran.js  // [p123_scot_butoane] — nomenclator de produse, reutilizabil (portal, cabinet, gratuit).
// Scrii denumirea -> AI potriveste cota TVA din regula oficiala (preview live) ->
// vezi cota + justificarea -> salvezi. Cota se poate corecta manual.
// Apelare: randeazaProduse(corp, nav, tenantId, { inapoi })
import { api, arataMesaj, confirmaCaseta, esc, bani, focusFaraSalt, eroareCamp, curataEroriCamp } from "../api.js?v=ff30ebaf3f";  /* cap6_catch_v1b + investigatie_identitate_v1 */

const SVG_BACK = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>';

export async function randeazaProduse(corp, nav, tenantId, opt = {}) {
  const inapoi = opt.inapoi || (() => nav && nav.inapoi && nav.inapoi());
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;

  let lista = [];
  try {
    const r = await api.get(`/tenants/${tenantId}/produse`);
    lista = (r && r.produse) || [];
  } catch (e) {
    /* [B7 fix] load esuat: NU referi 'zona' (nedeclarata aici -> ReferenceError) si NU continua la
       randarea listei goale (parea reusit). Stare-goala cap.6 (gol + cauza + iesire), apoi return. */
    corp.innerHTML = `<div class="stare-goala">Nu s-au putut încărca produsele${e && e.mesaj ? " (" + esc(e.mesaj) + ")" : ""}. <button class="buton-mic" id="pr-reincarca">Reîncearcă</button></div>`;
    const _rb = corp.querySelector("#pr-reincarca");
    if (_rb) _rb.addEventListener("click", () => randeazaProduse(corp, nav, tenantId, opt));
    return;
  }

  corp.innerHTML = `
    
    <div class="pr-cap">
      <h2 class="pf-titlu">Produse \u0219i servicii</h2>
      <button class="buton-primar pr-add" id="pr-add" data-actiune="POST /tenants/{tenant_id}/produse">+ Adaug\u0103 produs</button>
    </div>
    <p class="pf-intro">Scrii denumirea, iar sistemul potrive\u0219te automat cota de TVA corect\u0103 din legisla\u021bie. O po\u021bi corecta oric\u00e2nd.</p>
    <input id="pr-cauta" class="camp-input" placeholder="Caut\u0103 produs..." aria-label="Caut\u0103 produs" style="margin-bottom:8px">
    <div id="pr-mesaj"></div>
    <div class="pr-form-zona" id="pr-form-zona"></div>
    <div class="pr-lista" id="pr-lista"></div>
  `;
  // [435] `opt.mesaj` e al unei singure redesenări: reîncărcarea următoare nu-l mai arată
  const optFara = Object.assign({}, opt, { mesaj: null });
  const reincarcaCu = (mesaj) => randeazaProduse(corp, nav, tenantId, Object.assign({}, optFara, { mesaj }));
  corp.querySelector("#pr-add").addEventListener("click", () => formularAdauga(corp, tenantId, () => randeazaProduse(corp, nav, tenantId, optFara)));
  corp.querySelector("#pr-cauta").addEventListener("input", (e) => {  // [pr_cauta_v1]
    const q = e.target.value.toLowerCase().trim();
    const filtrata = q ? lista.filter((x) => (x.denumire || "").toLowerCase().includes(q)) : lista;
    randeazaLista(corp, tenantId, filtrata, () => randeazaProduse(corp, nav, tenantId, optFara), reincarcaCu);
  });

  randeazaLista(corp, tenantId, lista, () => randeazaProduse(corp, nav, tenantId, optFara), reincarcaCu);
  // [lotul 10, 435] confirmarea salvării de pe rând rămâne vizibilă după reîncărcarea listei (DS cap.6, `arataMesaj` „ok”)
  if (opt.mesaj) arataMesaj(corp.querySelector("#pr-mesaj"), opt.mesaj, "ok");
}

function badgeCota(cota, sursa) {
  // [R29] LIPSA nu e 0%: `Number(null)` da 0, deci un produs fara cota s-ar fi afisat
  // „fara TVA" - o afirmatie falsa despre un produs necompletat.
  if (cota === null || cota === undefined || cota === "") {
    return `<span class="pr-badge prc-lipsa">cot\u0103 lips\u0103</span>`;
  }
  const c = Number(cota);
  const cls = c === 0 ? "prc-0" : (c === 11 ? "prc-11" : "prc-21");
  const eticheta = c === 0 ? "f\u0103r\u0103 TVA" : `TVA ${c}%`;
  const semn = sursa === "ai" ? " \u00b7 AI" : (sursa === "fallback" ? " \u00b7 verific\u0103" : "");
  return `<span class="pr-badge ${cls}">${eticheta}${semn}</span>`;
}

// [lotul 10, deficiența 435] „Orice articol din stoc apare în nomenclator”: articolul din stoc fără produs vine de la server cu `din_stoc`,
// fără cotă; cota de TVA a vânzării se alege pe rândul lui și îl scrie în nomenclator (POST /produse, cu cota aleasă — nimic presupus)
const OPT_COTA = `<option value="">— alege cota —</option><option value="21">21%</option><option value="11">11%</option><option value="0">scutit / f\u0103r\u0103 TVA (art. 292)</option>`;
const cheieRand = (p) => (p.din_stoc ? "s" + p.articol_id : String(p.id));

function randeazaLista(corp, tenantId, lista, reincarca, reincarcaCu) {
  const zona = corp.querySelector("#pr-lista");
  if (!zona) return;
  if (!lista.length) {
    zona.innerHTML = `<div class="stare-goala">Niciun produs \u00eenc\u0103. Adaug\u0103 primul produs — cota se completeaz\u0103 automat.</div>`;
    return;
  }
  zona.innerHTML = lista.map((p) => `
    <div class="pr-rand" data-id="${p.id}" id="pr-rand-${cheieRand(p)}"${p.din_stoc ? ' style="flex-wrap:wrap"' : ""}>
      <div class="pr-rand-text">
        <div class="pr-rand-nume">${esc(p.denumire)}</div>
        <div class="pr-rand-sub">${p.din_stoc ? `în stoc, ${esc(p.um || "buc")} \u00b7 alege cota de TVA a vânzării, ca factura să o ia de aici` : (p.pret_unitar ? bani(p.pret_unitar) + " lei / " + (p.um || "buc") : (p.um || "buc")) + (p.justificare ? " \u00b7 " + esc(p.justificare) : "")}</div>
      </div>
      <div class="pr-rand-drept">
        ${badgeCota(p.cota_tva, p.sursa)}
        ${p.din_stoc ? `<select class="camp-input pr-mic pr-cota-rand" id="pr-cota-${cheieRand(p)}" aria-label="Cota TVA ${esc(p.denumire)}">${OPT_COTA}</select>
        <button class="buton-primar pr-cota-salveaza" id="pr-cota-salveaza-${cheieRand(p)}" data-cheie="${cheieRand(p)}" data-actiune="POST /tenants/{tenant_id}/produse">Salveaz\u0103 cota</button>`
        : `<button class="buton-sters pr-sterge" data-id="${p.id}" data-actiune="DELETE /tenants/{tenant_id}/produse/{produs_id}" title="\u0218terge" aria-label="\u0218terge">\u00d7</button>`}
      </div>
    </div>`).join("");
  zona.querySelectorAll(".pr-cota-salveaza").forEach((b) => {
    b.addEventListener("click", async () => {
      const p = lista.find((x) => cheieRand(x) === b.dataset.cheie);
      const sel = zona.querySelector(`#pr-cota-${b.dataset.cheie}`);
      curataEroriCamp(zona);
      if (!p || !sel) return;
      if (sel.value === "") { eroareCamp(zona, sel.id, `Alege cota de TVA a vânzării pentru ${p.denumire}.`); return; }
      try {
        await api.post(`/tenants/${tenantId}/produse`, { denumire: p.denumire, um: p.um || "buc", cota_tva: Number(sel.value), confirmat: true });
        const cota = Number(sel.value);
        reincarcaCu(`Cota ${cota === 0 ? "„scutit / fără TVA”" : cota + "%"} salvată: ${p.denumire} e acum în nomenclator, iar factura o ia de aici.`);
      } catch (e) {
        eroareCamp(zona, sel.id, (e && e.mesaj) || `Cota pentru ${p.denumire} nu s-a salvat. Încearcă din nou.`);
      }
    });
  });
  zona.querySelectorAll(".pr-sterge").forEach((b) => {
    b.addEventListener("click", (e) => {
      e.stopPropagation();
      const id = b.dataset.id;
      confirmaCaseta(b.parentElement || b, "\u0218tergi produsul?", async () => {
        try { await api.del(`/tenants/${tenantId}/produse/${id}`); reincarca(); }
        catch (er) { arataMesaj(corp.querySelector("#pr-mesaj"), er.mesaj || "Nu s-a putut \u0219terge produsul.", "eroare"); }   // [435] zona era căutată în listă (null): refuzul nu se vedea
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
        <label class="camp-eticheta" for="pr-den">Denumire produs sau serviciu<span class="oblig">*</span></label>
        <input class="camp-input pr-den" id="pr-den" data-actiune-camp="POST /tenants/{tenant_id}/produse/potriveste" placeholder="ex: p\u00e2ine alb\u0103, consultan\u021b\u0103" autocomplete="off">
      </div>
      <div class="pr-cota-preview" id="pr-cota-preview"></div>
      <div class="camp-eticheta">Pre\u021b \u00b7 unitate de m\u0103sur\u0103 \u00b7 cot\u0103 TVA</div>
      <div class="pr-form-rand pr-form-detalii">
        <input class="camp-input pr-mic" id="pr-pret" type="number" step="0.01" placeholder="Pre\u021b" aria-label="Pre\u021b">
        <input class="camp-input pr-mic" id="pr-um" placeholder="UM (buc)" aria-label="Unitate de m\u0103sur\u0103" value="buc">
        <select class="camp-input pr-mic" id="pr-cota" aria-label="Cota TVA">
          <option value="">cot\u0103 (auto)</option>
          <option value="21">21%</option>
          <option value="11">11%</option>
          <option value="0">scutit / f\u0103r\u0103 TVA (art. 292)</option>
        </select>
      </div>
      <div class="pr-form-actiuni">
        <button class="buton-primar" id="pr-salveaza" data-actiune="POST /tenants/{tenant_id}/produse">Salveaz\u0103</button>
        <button class="buton-secundar pr-anuleaza" id="pr-anuleaza">Renun\u021b\u0103</button>
      </div>
    </div>
  `;
  const inputDen = zona.querySelector("#pr-den");
  const preview = zona.querySelector("#pr-cota-preview");
  const selCota = zona.querySelector("#pr-cota");
  focusFaraSalt(inputDen);

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
    if (!denumire) { arataMesaj(preview, "Completează denumirea produsului sau serviciului.", "eroare"); focusFaraSalt(inputDen); return; }
    const payload = {
      denumire,
      um: zona.querySelector("#pr-um").value.trim() || "buc",
      // [comanda Costin 06.10.2026 pct.1b, clasa] golul pleacă drept lipsă (nomenclatorul îl ține ca „fără preț”), nu ca 0 ales
      pret_unitar: zona.querySelector("#pr-pret").value === "" ? null : parseFloat(zona.querySelector("#pr-pret").value),
    };
    const cotaMan = selCota.value;
    if (cotaMan !== "") payload.cota_tva = parseFloat(cotaMan);
    try {
      await api.post(`/tenants/${tenantId}/produse`, payload);
      zona.innerHTML = "";
      reincarca();
    } catch (e) {
      /* [catch_tacut 27.07.2026] o salvare esuata parea reusita: formularul
         se golea, omul credea ca s-a salvat. DS cap.6 - niciodata tacere. */
      arataMesaj(zona, (e && e.mesaj) || "Nu s-a putut salva. Încearcă din nou.", "eroare");
    }
  });
}
