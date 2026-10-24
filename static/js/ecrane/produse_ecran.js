// produse_ecran.js  // [p123_scot_butoane] — nomenclator de produse, reutilizabil (portal, cabinet, gratuit).
// Scrii denumirea -> AI potriveste cota TVA din regula oficiala (preview live) ->
// vezi cota + justificarea -> salvezi. Cota se poate corecta manual: [lotul 12, 472] pe rândul produsului salvat, „Corectează cota”
// (PUT /produse/{id}, consemnat în `produse_cota_jurnal`); [471] articolele din stoc fără produs vin cu cota propusă (NIR / potrivire).
// Apelare: randeazaProduse(corp, nav, tenantId, { inapoi })
import { api, ultimaCerere, arataMesaj, confirmaCaseta, esc, bani, focusFaraSalt, eroareCamp, curataEroriCamp, arataRefuzul, cereCompletate } from "../api.js?v=309f4d66ae";  /* cap6_catch_v1b + investigatie_identitate_v1 */
import { permis } from "../drepturi.js?v=34d0fb0afd";  /* [lotul 12, 471] propunerea automată a cotei, numai cu dreptul ei */

const SVG_BACK = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>';

export async function randeazaProduse(corp, nav, tenantId, opt = {}) {
  const inapoi = opt.inapoi || (() => nav && nav.inapoi && nav.inapoi());
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;

  let lista = [];
  // [lotul 11, 449] categoriile cotei 0% (taxare inversă, scutit cu / fără drept de deducere, neimpozabil) și bunurile cu taxare inversă
  // vin de la server (`produse_api.categorii_pentru_ecran`, din `categorii_tva` și `d394.CODPR`), nu se scriu a doua oară aici
  const cat = { tva: [], c331: [] };
  try {
    const r = await api.get(`/tenants/${tenantId}/produse`);
    lista = (r && r.produse) || [];
    cat.tva = (r && r.categorii_tva) || [];
    cat.c331 = (r && r.categorii_331) || [];
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
  const optFara = Object.assign({}, opt, { mesaj: null, dupaSalvare: false });
  const reincarcaCu = (mesaj) => randeazaProduse(corp, nav, tenantId, Object.assign({}, optFara, { mesaj, dupaSalvare: true }));
  corp.querySelector("#pr-add").addEventListener("click", () => formularAdauga(corp, tenantId,
    () => randeazaProduse(corp, nav, tenantId, Object.assign({}, optFara, { dupaSalvare: true })), cat));
  corp.querySelector("#pr-cauta").addEventListener("input", (e) => {  // [pr_cauta_v1]
    const q = e.target.value.toLowerCase().trim();
    const filtrata = q ? lista.filter((x) => (x.denumire || "").toLowerCase().includes(q)) : lista;
    randeazaLista(corp, tenantId, filtrata, () => randeazaProduse(corp, nav, tenantId, optFara), reincarcaCu, cat);
  });

  randeazaLista(corp, tenantId, lista, () => randeazaProduse(corp, nav, tenantId, optFara), reincarcaCu, cat);
  // [lotul 10, 435] confirmarea salvării de pe rând rămâne vizibilă după reîncărcarea listei (DS cap.6, `arataMesaj` „ok”)
  if (opt.mesaj) arataMesaj(corp.querySelector("#pr-mesaj"), opt.mesaj, "ok");
  // [lotul 11, 445] deschis dintr-un refuz al altui formular (NIR, factura): după salvare, drumul înapoi la formularul păstrat
  // (ca Date firmă `#df-inapoi-la`; săgeata ferestrei îl spune oricum)
  if (opt.dupaSalvare && opt.inapoiLa && nav && nav.inapoi) {
    const bi = document.createElement("button");
    bi.type = "button"; bi.className = "buton-primar"; bi.id = "pr-inapoi-la";
    bi.dataset.faraActiune = "navigare înapoi la formularul de plecare";
    bi.textContent = "\u2190 \u00cenapoi la " + opt.inapoiLa;
    bi.addEventListener("click", () => nav.inapoi());
    corp.querySelector("#pr-mesaj").appendChild(bi);
  }
}

function badgeCota(cota, sursa, categorie, cat) {
  // [R29] LIPSA nu e 0%: `Number(null)` da 0, deci un produs fara cota s-ar fi afisat
  // „fara TVA" - o afirmatie falsa despre un produs necompletat.
  if (cota === null || cota === undefined || cota === "") {
    return `<span class="pr-badge prc-lipsa">cot\u0103 lips\u0103</span>`;
  }
  const c = Number(cota);
  const cls = c === 0 ? "prc-0" : (c === 11 ? "prc-11" : "prc-21");
  // [449] la cota 0% insigna spune categoria (taxare inversă / scutit cu sau fără drept / neimpozabil), nu „fără TVA” pentru toate
  const categ = c === 0 && categorie ? ((cat && cat.tva) || []).find((x) => x.cod === categorie) : null;
  const eticheta = c === 0 ? (categ ? "0% \u00b7 " + esc(categ.eticheta) : "f\u0103r\u0103 TVA") : `TVA ${c}%`;
  const semn = sursa === "ai" ? " \u00b7 AI" : (sursa === "fallback" ? " \u00b7 verific\u0103" : "");
  return `<span class="pr-badge ${cls}">${eticheta}${semn}</span>`;
}

// [lotul 10, deficiența 435] „Orice articol din stoc apare în nomenclator”: articolul din stoc fără produs vine de la server cu `din_stoc`,
// fără cotă; cota de TVA a vânzării se alege pe rândul lui și îl scrie în nomenclator (POST /produse, cu cota aleasă — nimic presupus)
// [lotul 11, 449] cota 0% se alege CU categoria ei (valoarea „0:<categorie>”), ca factura să pună codul din e-Factura (AE / E) și rândul din
// D300; taxarea inversă cere și bunul (codul din D394), în selectul de lângă
const optCota = (cat, gol) => `<option value="">${gol}</option><option value="21">21%</option><option value="11">11%</option>` +
  ((cat && cat.tva) || []).map((c) => `<option value="0:${esc(c.cod)}">0% \u2014 ${esc(c.eticheta)}</option>`).join("");
const optC331 = (cat) => `<option value="">— alege bunul (art.331) —</option>` +
  ((cat && cat.c331) || []).map((c) => `<option value="${esc(c.cod)}">${esc(c.eticheta)} (D394 cod ${esc(c.cod_d394)})</option>`).join("");
/** Valoarea selectului de cotă -> {cota_tva, categorie_tva}. */
const dinCota = (v) => { const [c, categ] = String(v).split(":"); return { cota_tva: Number(c), categorie_tva: categ || null }; };
/** Selectul bunului cu taxare inversă se vede numai la „0% — taxare inversă”. */
const legaC331 = (selCota, selC331) => { if (!selCota || !selC331) return; const f = () => { selC331.hidden = selCota.value !== "0:taxare_inversa"; if (selC331.hidden) selC331.value = ""; }; selCota.addEventListener("change", f); f(); };
const cheieRand = (p) => (p.din_stoc ? "s" + p.articol_id : String(p.id));
/** [lotul 12, 472] Cota spusă omului: „21%”, „0% (taxare inversă)” — categoria cotei 0% cu eticheta ei de la server. */
const etCota = (cota, categorie, cat) => {
  if (cota === null || cota === undefined) return "fără cotă";
  const c = Number(cota);
  const categ = c === 0 && categorie ? ((cat && cat.tva) || []).find((x) => x.cod === categorie) : null;
  return c + "%" + (categ ? ` (${categ.eticheta})` : "");
};
/** [471] Textul propunerii (deja cu sursa ei) și butonul care o pune în listă; la 0% fără categorie, numai textul (categoria o alege omul). */
const textPropunere = (text, v, cheie) => `${esc(text)}.${v
  ? ` <button type="button" class="buton-secundar buton-mic" id="pr-propunere-alege-${cheie}" data-fara-actiune="pune cota propusă în listă">Alege cota propusă</button>`
  : " Alege categoria cotei 0% în listă."}`;
/** [471] Valoarea selectului pentru o cotă propusă — numai dacă lista o are (cotele listei sunt cele de mai sus, `optCota`; 0% cere
 *  categoria, deci numai cu ea). "" = cota nu se poate alege din listă așa cum vine. */
const valCota = (cat, cota, categorie) => {
  if (cota === null || cota === undefined || cota === "") return "";
  const v = Number(cota) === 0 ? (categorie ? "0:" + categorie : "") : String(Number(cota));
  return v && [...optCota(cat, "").matchAll(/value="([^"]*)"/g)].some((m) => m[1] === v) ? v : "";
};

function randeazaLista(corp, tenantId, lista, reincarca, reincarcaCu, cat) {
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
        ${p.din_stoc ? `<div class="pr-rand-sub pr-propunere" id="pr-propunere-${cheieRand(p)}">${p.propunere
          ? textPropunere(`Cota propusă: ${etCota(p.propunere.cota_tva, null, cat)}, de pe rândul din ${p.propunere.document}`,
            valCota(cat, p.propunere.cota_tva, null), cheieRand(p))
          : "Se caută cota propusă\u2026"}</div>` : ""}
        ${p.ultima_corectare ? `<div class="pr-rand-sub" id="pr-corectat-${cheieRand(p)}">cota corectată pe ${esc(p.ultima_corectare.la)}: ${esc(etCota(p.ultima_corectare.cota_veche, p.ultima_corectare.categorie_veche, cat))} \u2192 ${esc(etCota(p.ultima_corectare.cota_noua, p.ultima_corectare.categorie_noua, cat))} (consemnată)</div>` : ""}
      </div>
      <div class="pr-rand-drept">
        ${badgeCota(p.cota_tva, p.sursa, p.categorie_tva, cat)}
        ${p.din_stoc ? `<select class="camp-input pr-mic pr-cota-rand" id="pr-cota-${cheieRand(p)}" aria-label="Cota TVA ${esc(p.denumire)}">${optCota(cat, "— alege cota —")}</select>
        <select class="camp-input pr-mic" id="pr-c331-${cheieRand(p)}" aria-label="Bunul cu taxare inversă ${esc(p.denumire)}" hidden>${optC331(cat)}</select>
        <button class="buton-primar pr-cota-salveaza" id="pr-cota-salveaza-${cheieRand(p)}" data-cheie="${cheieRand(p)}" data-actiune="POST /tenants/{tenant_id}/produse">Salveaz\u0103 cota</button>`
        : `<button class="buton-secundar pr-corecteaza" id="pr-corecteaza-${p.id}" data-id="${p.id}" data-fara-actiune="deschide corectura cotei pe rând">Corectează cota</button>
        <span class="pr-corectura" id="pr-corectura-${p.id}" hidden>
          <select class="camp-input pr-mic" id="pr-cota-${p.id}" aria-label="Cota TVA corectată ${esc(p.denumire)}">${optCota(cat, "— alege cota corectă —")}</select>
          <select class="camp-input pr-mic" id="pr-c331-${p.id}" aria-label="Bunul cu taxare inversă ${esc(p.denumire)}" hidden>${optC331(cat)}</select>
          <button class="buton-primar pr-corectura-salveaza" id="pr-corectura-salveaza-${p.id}" data-id="${p.id}" data-actiune="PUT /tenants/{tenant_id}/produse/{produs_id}">Salvează cota</button>
          <button class="buton-secundar pr-corectura-renunta" data-id="${p.id}" data-fara-actiune="închide corectura cotei">Renunță</button>
        </span>
        <button class="buton-sters pr-sterge" data-id="${p.id}" data-actiune="DELETE /tenants/{tenant_id}/produse/{produs_id}" title="\u0218terge" aria-label="\u0218terge">\u00d7</button>`}
      </div>
    </div>`).join("");
  // [lotul 12, deficiența 471] rândul din stoc vine cu cota propusă: din NIR-ul articolului (server, `propunere_din_nir` — aceeași regulă ca
  // NIR-ul salvat de acum, 415) sau, fără NIR, potrivirea automată din regula oficială (`/produse/potriveste`, ca la „+ Adaugă produs”).
  // Propunerea se spune, cu sursa ei, iar „Alege cota propusă” o pune în listă; lista NU vine aleasă (cota o alege omul — 435: „Cota nu
  // se ghicește”), iar în nomenclator intră numai la „Salvează cota”.
  const legaAlege = (p, v) => {
    const b = zona.querySelector(`#pr-propunere-alege-${cheieRand(p)}`);
    const sel = zona.querySelector(`#pr-cota-${cheieRand(p)}`);
    if (b && sel) b.addEventListener("click", () => { sel.value = v; sel.dispatchEvent(new Event("change")); curataEroriCamp(zona); focusFaraSalt(sel); });
  };
  // [C103] căutarea redesenează lista cât propunerea e în zbor: numai desenul cel nou o primește (răspunsul e ținut pe articol)
  const actuala = ultimaCerere(zona)();
  lista.filter((p) => p.din_stoc).forEach((p) => {
    const txt = zona.querySelector(`#pr-propunere-${cheieRand(p)}`);
    if (p.propunere) { legaAlege(p, valCota(cat, p.propunere.cota_tva, null)); return; }
    // fără dreptul potrivirii (cel al pregătirii), nici întrebarea, nici refuzul ei pe rând: cota se alege din listă
    if (!permis("POST /tenants/{tenant_id}/produse/potriveste")) { if (txt) txt.remove(); return; }
    // o singură întrebare pe articol: căutarea redesenează lista, iar răspunsul rămâne pe rândul lui
    p.cerereCota = p.cerereCota || api.post(`/tenants/${tenantId}/produse/potriveste`, { denumire: p.denumire });
    p.cerereCota.then((r) => {
      if (!actuala() || !txt || !txt.isConnected) return;
      if (r && r.ok && r.cota !== null && r.cota !== undefined) {
        const v = valCota(cat, r.cota, r.categorie_tva);
        txt.innerHTML = textPropunere(`Cota propusă automat: ${etCota(r.cota, r.categorie_tva, cat)}${r.justificare ? " — " + r.justificare : ""}`,
          v, cheieRand(p));
        legaAlege(p, v);
      } else {
        txt.textContent = "Nicio cotă propusă pentru această denumire: alege cota de TVA a vânzării.";
      }
    }).catch(() => {
      if (!actuala() || !txt || !txt.isConnected) return;
      txt.textContent = "Cota propusă nu s-a putut afla: alege cota de TVA a vânzării.";
    });
  });
  // [lotul 12, deficiența 472] corectura cotei unui produs salvat: pe rând, la cerere; schimbarea se consemnează pe server (cine, când)
  zona.querySelectorAll(".pr-corecteaza").forEach((b) => b.addEventListener("click", () => {
    const z = zona.querySelector(`#pr-corectura-${b.dataset.id}`);
    z.hidden = false; b.hidden = true;
    legaC331(zona.querySelector(`#pr-cota-${b.dataset.id}`), zona.querySelector(`#pr-c331-${b.dataset.id}`));
    focusFaraSalt(zona.querySelector(`#pr-cota-${b.dataset.id}`));
  }));
  zona.querySelectorAll(".pr-corectura-renunta").forEach((b) => b.addEventListener("click", () => {
    curataEroriCamp(zona);
    zona.querySelector(`#pr-corectura-${b.dataset.id}`).hidden = true;
    zona.querySelector(`#pr-corecteaza-${b.dataset.id}`).hidden = false;
  }));
  zona.querySelectorAll(".pr-corectura-salveaza").forEach((b) => b.addEventListener("click", async () => {
    const p = lista.find((x) => String(x.id) === b.dataset.id);
    const sel = zona.querySelector(`#pr-cota-${b.dataset.id}`);
    const sel331 = zona.querySelector(`#pr-c331-${b.dataset.id}`);
    curataEroriCamp(zona);
    if (!p || !sel) return;
    if (sel.value === "") { eroareCamp(zona, sel.id, `Alege cota corectă pentru ${p.denumire}.`); return; }
    const { cota_tva: cota, categorie_tva } = dinCota(sel.value);
    if (categorie_tva === "taxare_inversa" && sel331 && !sel331.value) {
      eroareCamp(zona, sel331.id, `Alege bunul cu taxare inversă (art.331) pentru ${p.denumire}: D394 îl declară cu codul lui.`); return;
    }
    if (cota === Number(p.cota_tva) && (categorie_tva || null) === (p.categorie_tva || null)) {
      eroareCamp(zona, sel.id, `${p.denumire} are deja cota ${etCota(cota, categorie_tva, cat)}: alege cota corectă, dacă e alta.`); return;
    }
    try {
      await api.put(`/tenants/${tenantId}/produse/${p.id}`, { cota_tva: cota, categorie_tva: categorie_tva || "",
        categorie_331: categorie_tva === "taxare_inversa" && sel331 ? sel331.value : "" });
      reincarcaCu(`Cota corectată: ${p.denumire}, din ${etCota(p.cota_tva, p.categorie_tva, cat)} în ${etCota(cota, categorie_tva, cat)}. `
        + "Facturile emise rămân cu cota lor; cele emise de acum înainte o iau pe cea nouă. Corectura e consemnată (cine și când).");
    } catch (e) {
      eroareCamp(zona, sel.id, (e && e.mesaj) || `Cota pentru ${p.denumire} nu s-a corectat. Încearcă din nou.`);
    }
  }));
  zona.querySelectorAll(".pr-cota-rand").forEach((s) => legaC331(s, zona.querySelector("#" + s.id.replace("pr-cota-", "pr-c331-"))));
  zona.querySelectorAll(".pr-cota-salveaza").forEach((b) => {
    b.addEventListener("click", async () => {
      const p = lista.find((x) => cheieRand(x) === b.dataset.cheie);
      const sel = zona.querySelector(`#pr-cota-${b.dataset.cheie}`);
      const sel331 = zona.querySelector(`#pr-c331-${b.dataset.cheie}`);
      curataEroriCamp(zona);
      if (!p || !sel) return;
      if (sel.value === "") { eroareCamp(zona, sel.id, `Alege cota de TVA a vânzării pentru ${p.denumire}.`); return; }
      const { cota_tva: cota, categorie_tva } = dinCota(sel.value);
      if (categorie_tva === "taxare_inversa" && sel331 && !sel331.value) {
        eroareCamp(zona, sel331.id, `Alege bunul cu taxare inversă (art.331) pentru ${p.denumire}: D394 îl declară cu codul lui.`); return;
      }
      try {
        await api.post(`/tenants/${tenantId}/produse`, { denumire: p.denumire, um: p.um || "buc", cota_tva: cota, confirmat: true,
          categorie_tva, categorie_331: categorie_tva === "taxare_inversa" && sel331 ? sel331.value : null });
        const et = cota === 0 ? `0% (${sel.options[sel.selectedIndex].text.replace(/^0% \u2014 /, "")})` : cota + "%";
        reincarcaCu(`Cota ${et} salvată: ${p.denumire} e acum în nomenclator, iar factura o ia de aici.`);
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

function formularAdauga(corp, tenantId, reincarca, cat) {
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
        <select class="camp-input pr-mic" id="pr-cota" aria-label="Cota TVA">${optCota(cat, "cot\u0103 (auto)")}</select>
        <select class="camp-input pr-mic" id="pr-c331" aria-label="Bunul cu taxare inversă (art.331)" hidden>${optC331(cat)}</select>
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
  const selC331 = zona.querySelector("#pr-c331");
  legaC331(selCota, selC331);
  focusFaraSalt(inputDen);

  // potrivire AI live (debounce), doar daca utilizatorul nu a ales manual cota
  let timer = null, ultimaDenum = "";
  const cerereCota = ultimaCerere();   // [C103] denumirea scrisă în reprize: numai cota propusă pentru ultima denumire ajunge în previzualizare
  inputDen.addEventListener("input", () => {
    const actuala = cerereCota();   // și alegerea manuală / o denumire scurtă (fără cerere) opresc propunerea cerută înainte
    const d = inputDen.value.trim();
    if (selCota.value) { preview.innerHTML = ""; return; }  // a ales manual
    clearTimeout(timer);
    if (d.length < 3) { preview.innerHTML = ""; return; }
    preview.innerHTML = `<span class="pr-cota-cauta">se verific\u0103 cota\u2026</span>`;
    timer = setTimeout(async () => {
      if (d === ultimaDenum) return;
      try {
        const r = await api.post(`/tenants/${tenantId}/produse/potriveste`, { denumire: d });
        if (!actuala()) return;
        ultimaDenum = d;   // [C103] denumirea „deja propusă” e numai cea al cărei răspuns a ajuns pe ecran
        if (r && r.ok) {
          preview.innerHTML = `<div class="pr-cota-rezultat">
            ${badgeCota(r.cota, r.sursa)}
            <span class="pr-cota-just">${r.justificare || ""}</span>
          </div>`;
        } else { preview.innerHTML = ""; }
      } catch { if (!actuala()) return; preview.innerHTML = ""; }
    }, 600);
  });

  zona.querySelector("#pr-anuleaza").addEventListener("click", () => { zona.innerHTML = ""; });
  zona.querySelector("#pr-salveaza").addEventListener("click", async () => {
    curataEroriCamp(zona);
    const denumire = inputDen.value.trim();
    // [lotul 11, 440] toate lipsurile deodată, lângă câmpurile lor: denumirea și (la taxare inversă) bunul art.331
    let lipsa = cereCompletate(zona, [{ id: "pr-den", mesaj: "Completează denumirea produsului sau serviciului." }]);
    const cotaMan = selCota.value;
    if (cotaMan !== "" && dinCota(cotaMan).categorie_tva === "taxare_inversa" && !selC331.value) {
      eroareCamp(zona, "pr-c331", "Alege bunul cu taxare inversă (art.331): D394 îl declară cu codul lui.");
      lipsa = true;
    }
    if (lipsa) return;
    const payload = {
      denumire,
      um: zona.querySelector("#pr-um").value.trim() || "buc",
      // [comanda Costin 06.10.2026 pct.1b, clasa] golul pleacă drept lipsă (nomenclatorul îl ține ca „fără preț”), nu ca 0 ales
      pret_unitar: zona.querySelector("#pr-pret").value === "" ? null : parseFloat(zona.querySelector("#pr-pret").value),
    };
    if (cotaMan !== "") Object.assign(payload, dinCota(cotaMan));   // [449] cota și, la 0%, categoria ei
    if (payload.categorie_tva === "taxare_inversa") payload.categorie_331 = selC331.value;
    try {
      await api.post(`/tenants/${tenantId}/produse`, payload);
      zona.innerHTML = "";
      reincarca();
    } catch (e) {
      /* [catch_tacut 27.07.2026] o salvare esuata parea reusita: formularul
         se golea, omul credea ca s-a salvat. DS cap.6 - niciodata tacere. */
      // [lotul 11, 440] erorile serverului lângă câmpurile lor, textul refuzului în formular
      arataRefuzul(zona, e && e.mesaj ? e : { ...(e || {}), mesaj: "Nu s-a putut salva. Încearcă din nou." }, zona,
        { campuri: { denumire: "pr-den", pret_unitar: "pr-pret", um: "pr-um", cota_tva: "pr-cota", categorie_tva: "pr-cota", categorie_331: "pr-c331" } });
    }
  });
}
