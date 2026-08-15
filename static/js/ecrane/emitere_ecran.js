// emitere_ecran.js  // [p124_orfani]  // [p123_scot_butoane] — emitere facturi (reutilizabil: portal client, gratuit, cabinet).
// Flux:
//   1. daca numerotarea nu e configurata -> intreaba "ai mai emis facturi?"
//      DA -> serie + ultimul numar (continuitate); NU -> serie optionala, start 1
//   2. formular emitere: beneficiar (CUI verificat ANAF) + linii (cota auto) + total live
// Apelare: randeazaEmitere(corp, nav, tenantId, { inapoi, dupaEmitere })
// [cap.24 batch 3b] randuri dinamice: model pozitional cu valori + re-randare integrala + stergere/rand (splice);
// validarea per-linie o face BACKENDUL (facturi_api.linii_campuri_lipsa -> 422.campuri {camp,eticheta}); frontendul
// NU mai filtreaza randuri si plaseaza erorile langa campul lor prin eroareCamp (cap.6 mecanism A).
import { api, dataRo, esc, eroareCamp, curataEroriCamp, semnAjutor } from "../api.js";

export async function randeazaEmitere(corp, nav, tenantId, opt = {}) {
  const inapoi = opt.inapoi || (() => nav && nav.inapoi && nav.inapoi());
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;

  // citesc numerotarea; daca nu e configurata (serie null si urmator 1 fara facturi) -> config
  let num = { serie: null, urmator_numar: 1, configurata: false };
  try { num = await api.get(`/tenants/${tenantId}/facturi/numerotare`); } catch {}
  // [tva_din_profil_v1] platitor_tva e deja in profil (Date firma/ANAF) - il citim ca sa NU re-intrebam (#16)
  let tvaProfil = null;
  try { const _v = await api.get(`/tenants/${tenantId}/vector`); if (_v && typeof _v.platitor_tva === "boolean") tvaProfil = _v.platitor_tva; }
  catch { tvaProfil = null; }  // vector indisponibil -> intreaba (nu presupune)

  const neconfigurat = !num.configurata;  // numerotare_configurata_v1
  if (neconfigurat) {
    configureazaNumerotare(corp, nav, tenantId, opt, tvaProfil);
  } else {
    // [punte_stoc_v1] F172: la firma de CABINET cu gestiune cantitativa (are articole), incarca
    // articolele de stoc pentru selectorul pe linie. Portalul client NU tine
    // gestiune -> nu se incarca, emit exact ca azi (fara poarta, fara articol_id).
    opt.articole = [];
    if (!opt.client) {
      try { opt.articole = (await api.get(`/tenants/${tenantId}/stocuri/articole`)).articole || []; } catch { opt.articole = []; }
    }
    formularEmitere(corp, nav, tenantId, num, opt);
  }
}

// ---------- CONFIGURARE NUMEROTARE (o data) ----------
function configureazaNumerotare(corp, nav, tenantId, opt, tvaProfil = null) {
  if (nav && nav.setInapoi) nav.setInapoi(opt.inapoi || undefined);  // emitere_inapoi_v1
  const inapoi = opt.inapoi || (() => nav.inapoi());
  corp.innerHTML = `

    <h2 class="pf-titlu">Configurare emitere ${semnAjutor("F048")}</h2>
    <p class="pf-intro">Înainte de prima factură: numerotarea (ca să fie neîntreruptă) și regimul de TVA.</p>
    ${tvaProfil === null ? `<div class="em-config-camp" style="margin-bottom:12px">
      <label>Firma e plătitoare de TVA?<span class="oblig">*</span></label>
      <div class="em-optiuni">
        <button class="buton-secundar em-buton-sec" id="em-tva-da">Da, plătitoare</button>
        <button class="buton-secundar em-buton-sec" id="em-tva-nu">Nu</button>
      </div>
    </div>` : `<p class="pf-intro">Regim TVA: <b>${tvaProfil ? "plătitoare de TVA" : "neplătitoare"}</b> (din profilul firmei).</p>`}
    <div class="em-config">
      <div class="em-intrebare">Ai mai emis facturi până acum (în alt program sau pe hârtie)?</div>
      <div class="em-optiuni">
        <button class="buton-primar" id="em-da">Da, am mai emis</button>
        <button class="buton-secundar em-buton-sec" id="em-nu">Nu, încep acum</button>
      </div>
      <div class="em-config-form" id="em-config-form"></div>
    </div>`;

  const zona = corp.querySelector("#em-config-form");
  const tvaDinProfil = tvaProfil !== null;   // [tva_din_profil_v1] profilul stie -> nu re-intrebam, nu suprascriem (#16)
  let platitorTva = tvaProfil;  // null daca profilul nu stie -> obligatoriu ales
  const bTvaDa = corp.querySelector("#em-tva-da"), bTvaNu = corp.querySelector("#em-tva-nu");
  if (bTvaDa && bTvaNu) {
    bTvaDa.addEventListener("click", () => { platitorTva = true; bTvaDa.classList.add("buton-activ"); bTvaNu.classList.remove("buton-activ"); });
    bTvaNu.addEventListener("click", () => { platitorTva = false; bTvaNu.classList.add("buton-activ"); bTvaDa.classList.remove("buton-activ"); });
  }

  corp.querySelector("#em-da").addEventListener("click", () => {
    zona.innerHTML = `
      <div class="em-config-camp">
        <label>Seria ultimei facturi (dacă folosești, ex: KAI-)</label>
        <input class="camp-input" id="em-serie" placeholder="ex: KAI-" autocomplete="off">
      </div>
      <div class="em-config-camp">
        <label>Numărul ultimei facturi emise</label>
        <input class="camp-input" id="em-ultim" type="number" placeholder="ex: 147">
      </div>
      <p class="em-hint">Vom continua de la numărul următor.</p>
      <button class="buton-primar" id="em-salveaza-config">Continuă</button>`;
    zona.querySelector("#em-salveaza-config").addEventListener("click", async () => {
      const serie = zona.querySelector("#em-serie").value.trim() || null;
      if (serie && /^\d+$/.test(serie)) { let m = zona.querySelector(".msg-eroare"); if (!m) { m = document.createElement("p"); m.className = "msg-eroare"; zona.appendChild(m); } m.textContent = "Seria conține doar cifre. Seria e un prefix cu litere (ex: KAI- sau FCT-). Numărul ultimei facturi se pune în câmpul următor."; return; }
      const ultim = parseInt((zona.querySelector("#em-ultim").value || "").trim(), 10);
      if (!Number.isFinite(ultim) || ultim < 1) { let m = zona.querySelector(".msg-eroare"); if (!m) { m = document.createElement("p"); m.className = "msg-eroare"; zona.appendChild(m); } m.textContent = "Completează numărul ultimei facturi emise (nu putem presupune numărul 1)."; return; }
      const start = ultim + 1;   // #10: cerut explicit, nu fabricat
      if (platitorTva === null) { let m = zona.querySelector(".msg-eroare"); if (!m) { m = document.createElement("p"); m.className = "msg-eroare"; zona.appendChild(m); } m.textContent = "Alege dacă firma e plătitoare de TVA."; return; }
      await salveazaConfig(tenantId, serie, start, tvaDinProfil ? null : platitorTva);
      randeazaEmitere(corp, nav, tenantId, opt);
    });
  });

  corp.querySelector("#em-nu").addEventListener("click", () => {
    zona.innerHTML = `
      <div class="em-config-camp">
        <label>Serie (opțional, ex: FCT-)</label>
        <input class="camp-input" id="em-serie2" placeholder="lasă gol dacă nu folosești serie" autocomplete="off">
      </div>
      <p class="em-hint">Prima factură va avea numărul 1.</p>
      <button class="buton-primar" id="em-salveaza-config2">Continuă</button>`;
    zona.querySelector("#em-salveaza-config2").addEventListener("click", async () => {
      const serie = zona.querySelector("#em-serie2").value.trim() || null;
      if (serie && /^\d+$/.test(serie)) { let m = zona.querySelector(".msg-eroare"); if (!m) { m = document.createElement("p"); m.className = "msg-eroare"; zona.appendChild(m); } m.textContent = "Seria conține doar cifre. Seria e un prefix cu litere (ex: KAI- sau FCT-)."; return; }
      if (platitorTva === null) { let m = zona.querySelector(".msg-eroare"); if (!m) { m = document.createElement("p"); m.className = "msg-eroare"; zona.appendChild(m); } m.textContent = "Alege dacă firma e plătitoare de TVA."; return; }
      await salveazaConfig(tenantId, serie, 1, tvaDinProfil ? null : platitorTva);
      randeazaEmitere(corp, nav, tenantId, opt);
    });
  });
}

async function salveazaConfig(tenantId, serie, numar_start, platitor_tva) {
  // [tva_config_v1] fara catch mut: esecul configurarii trebuie vazut (DS cap.6)
  await api.put(`/tenants/${tenantId}/facturi/numerotare`, { serie, numar_start });
  if (platitor_tva !== undefined && platitor_tva !== null)
    await api.post(`/tenants/${tenantId}/firma-profil/regim-tva`, { platitor_tva });
}

// ---------- FORMULAR EMITERE ----------
function formularEmitere(corp, nav, tenantId, num, opt) {
  if (nav && nav.setInapoi) nav.setInapoi(opt.inapoi || undefined);  // emitere_inapoi_v1
  let monedaSel = "RON";
  // [B1 D300] Tara partenerului decide ruta in generator (RO->intern, UE->livrare IC/taxare inversa,
  // non-UE->export). Grupul UE OGLINDESTE core/d390.TARI_UE ca incadrarea sa coincida cu backendul.
  const TARI_UE_JS = { AT:"Austria", BE:"Belgia", BG:"Bulgaria", CY:"Cipru", CZ:"Cehia",
    DE:"Germania", DK:"Danemarca", EE:"Estonia", EL:"Grecia", ES:"Spania", FI:"Finlanda",
    FR:"Franța", HR:"Croația", HU:"Ungaria", IE:"Irlanda", IT:"Italia", LT:"Lituania",
    LU:"Luxemburg", LV:"Letonia", MT:"Malta", NL:"Țările de Jos", PL:"Polonia", PT:"Portugalia",
    SE:"Suedia", SI:"Slovenia", SK:"Slovacia", GB:"Regatul Unit", XI:"Irlanda de Nord" };
  const TARI_NONUE_JS = { US:"Statele Unite", CH:"Elveția", TR:"Turcia", CN:"China",
    MD:"Republica Moldova", NO:"Norvegia", RS:"Serbia", UA:"Ucraina" };
  const optiuniTara = `<option value="RO" selected>România (RO)</option>`
    + `<optgroup label="Uniunea Europeană">`
    + Object.keys(TARI_UE_JS).sort().map((c) => `<option value="${c}">${esc(TARI_UE_JS[c])} (${c})</option>`).join("")
    + `</optgroup><optgroup label="În afara UE (export)">`
    + Object.keys(TARI_NONUE_JS).sort().map((c) => `<option value="${c}">${esc(TARI_NONUE_JS[c])} (${c})</option>`).join("")
    + `</optgroup>`;
  const inapoi = opt.inapoi || (() => nav.inapoi());
  const numarProxim = num.serie ? `${num.serie}${num.urmator_numar}` : `${num.urmator_numar}`;

  corp.innerHTML = `

    <div class="pr-cap">
      <h2 class="pf-titlu">Emite factură</h2>
      <span class="em-numar">Număr: <b>${numarProxim}</b></span>
    </div>

    <div class="em-sectiune">
      <div class="em-eticheta">Beneficiar</div>
      <label class="camp-eticheta" for="em-cui">CUI beneficiar</label>
      <div class="em-benef">
        <input class="camp-input em-cui" id="em-cui" placeholder="ex: RO12345678" autocomplete="off">
        <button class="buton-secundar em-buton-sec" id="em-verifica">Verifică</button>  <!-- [p114_buton_anaf: eticheta neutra, acopera ANAF+VIES] -->
      </div>
      <label class="camp-eticheta" for="em-nume">Denumire beneficiar<span class="oblig">*</span></label>
      <input class="camp-input em-nume" id="em-nume" autocomplete="off">
      <label class="camp-eticheta" for="em-adresa">Adresă beneficiar (art. 319)</label>
      <input class="camp-input em-adresa" id="em-adresa" autocomplete="off">
      <div class="em-cui-stare" id="em-cui-stare"></div>
    </div>

    <div class="em-sectiune">
      <div class="em-eticheta">Produse și servicii</div>
      <div class="camp-eticheta">Linie: denumire · cantitate · preț unitar <span class="oblig">*</span> <span class="tip-micut">(cota TVA e propusă automat pe baza denumirii produsului — verifică încadrarea; răspunderea corectitudinii cotei îți aparține)</span></div>
      <div class="em-linie-antet" aria-hidden="true"><span>Denumire</span><span class="ant-cant">Cant.</span><span class="ant-pret">Preț</span><span class="ant-cota">Cotă</span><span></span></div>
      <div class="em-linii" id="em-linii"></div>
      <button class="buton-secundar em-buton-sec" id="em-add-linie">+ Adaugă linie</button>
    </div>

    <div class="em-total" id="em-total"></div>
    <div class="em-moneda-rand">
      <label class="em-moneda-eticheta">Monedă</label>
      <select class="camp-input" id="em-moneda">
        <option value="RON" selected>RON (lei)</option>
        <option value="EUR">EUR</option>
        <option value="USD">USD</option>
        <option value="GBP">GBP</option>
        <option value="CHF">CHF</option>
        <option value="HUF">HUF</option>
        <option value="PLN">PLN</option>
      </select>
      <span class="em-moneda-nota" id="em-moneda-nota"></span>
    </div>
    <div class="em-sectiune">
      <div class="em-eticheta">Clasificare TVA (D300)</div>
      <label class="camp-eticheta" for="em-tara">Țara partenerului</label>
      <select class="camp-input" id="em-tara">${optiuniTara}</select>
      <label class="camp-eticheta" for="em-tipop">Tip operațiune</label>
      <select class="camp-input" id="em-tipop">
        <option value="normal" selected>Operațiune normală</option>
        <option value="avans">Avans încasat</option>
        <option value="regularizare_avans">Regularizare avans</option>
      </select>
    </div>
    <div class="em-actiuni">
      <select id="em-tip" class="camp-input" style="max-width:180px;margin-right:8px">
        <option value="factura">Factura</option>
        <option value="proforma">Proforma</option>
        <option value="aviz">Aviz insotire</option>
      </select>
      <button class="buton-primar em-emite" id="em-emite">Emite factură</button>
    </div>
    <div class="em-rezultat" id="em-rezultat"></div>`;

  const zonaLinii = corp.querySelector("#em-linii");
  const linii = [];
  const articole = opt.articole || [];        // [punte_stoc_v1] F172: articole de stoc (gol la gratuit)
  let pleacaMarfaCurent = null;               // raspunsul la poarta "pleaca marfa acum?" pt emiterea curenta

  const linieNoua = () => ({ descriere: "", cantitate: "", pret_unitar: "", cota_tva: null, articol_id: null });
  const _val = (x) => (x === "" || x == null) ? "" : esc(String(x));

  // randeaza O linie DIN MODEL (id-uri pozitionale em-l{i}-*, ca backendul sa lege eroarea de camp). Stergere/rand.
  function randLinie(i) {
    const l = linii[i];
    const cotaTxt = l.cota_tva == null ? "—" : (l.cota_tva === 0 ? "0%" : `${l.cota_tva}%`);
    const cotaCls = l.cota_tva == null ? "" : (l.cota_tva === 11 ? " cota-11" : l.cota_tva === 0 ? " cota-0" : " cota-21");
    const inputsHtml = `
      <input class="camp-input em-l-den" id="em-l${i}-descriere" value="${_val(l.descriere)}" placeholder="Denumire (ex: pâine, consultanță)" aria-label="Denumire articol" autocomplete="off">
      <input class="camp-input em-l-cant" id="em-l${i}-cantitate" type="number" step="0.001" value="${_val(l.cantitate)}" placeholder="Cant." aria-label="Cantitate" title="Cantitate">
      <input class="camp-input em-l-pret" id="em-l${i}-pret_unitar" type="number" step="0.01" value="${_val(l.pret_unitar)}" placeholder="Preț" aria-label="Preț unitar" title="Preț unitar">
      <span class="em-l-cota${cotaCls}" id="em-l${i}-cota" title="Cota TVA">${cotaTxt}</span>
      <button type="button" class="buton-sters em-l-sterge" data-idx="${i}" title="Șterge">×</button>`;
    if (articole.length) {
      const selArticol = `
        <select class="camp-input em-l-articol" id="em-l${i}-articol" aria-label="Articol de stoc" style="margin-bottom:6px">
          <option value="">— fără articol (serviciu) —</option>
          ${articole.map((a) => `<option value="${a.id}"${String(a.id) === String(l.articol_id) ? " selected" : ""} data-den="${esc(a.denumire)}">${esc(a.denumire)} · stoc ${esc(a.stoc)}</option>`).join("")}
        </select>`;
      return `<div class="em-linie-wrap" data-idx="${i}">${selArticol}<div class="em-linie">${inputsHtml}</div></div>`;
    }
    return `<div class="em-linie" data-idx="${i}">${inputsHtml}</div>`;
  }

  // actualizeaza afisajul cotei pt OBIECTUL l la pozitia lui CURENTA (splice-safe cu fetch-ul async in zbor)
  function setCota(l, text, cota) {
    const p = linii.indexOf(l);
    if (p < 0) return;
    const el = zonaLinii.querySelector("#em-l" + p + "-cota");
    if (!el) return;
    el.textContent = text;
    el.className = "em-l-cota" + (cota === 11 ? " cota-11" : cota === 0 ? " cota-0" : cota != null ? " cota-21" : "");
  }

  // inputurile scriu in MODEL (nu re-randeaza -> fara pierdere de focus la tastare). Fetch-ul cotei capteaza
  // OBIECTUL l (nu indexul), deci scrie corect chiar daca intre timp un splice a reindexat lista.
  function legaLinie(i) {
    const l = linii[i];
    const den = zonaLinii.querySelector("#em-l" + i + "-descriere");
    const cant = zonaLinii.querySelector("#em-l" + i + "-cantitate");
    const pret = zonaLinii.querySelector("#em-l" + i + "-pret_unitar");
    const selArt = zonaLinii.querySelector("#em-l" + i + "-articol");
    const del = zonaLinii.querySelector('.em-l-sterge[data-idx="' + i + '"]');
    let timer = null;
    den.addEventListener("input", () => {
      l.descriere = den.value.trim();
      l.cota_tva = null;  // reset -> se repotriveste
      clearTimeout(timer);
      const d = l.descriere;
      if (d.length < 3) { setCota(l, "—"); recalc(); return; }
      setCota(l, "…");
      timer = setTimeout(async () => {
        try {
          const r = await api.post(`/tenants/${tenantId}/produse/potriveste`, { denumire: d });
          if (r && r.ok) { l.cota_tva = r.cota; setCota(l, r.cota === 0 ? "0%" : `${r.cota}%`, r.cota); }
        } catch {}
        recalc();
      }, 550);
    });
    cant.addEventListener("input", () => { l.cantitate = parseFloat(cant.value) || 0; recalc(); });
    pret.addEventListener("input", () => { l.pret_unitar = parseFloat(pret.value) || 0; recalc(); });
    if (selArt) selArt.addEventListener("change", () => {  // [punte_stoc_v1] F172
      l.articol_id = selArt.value ? parseInt(selArt.value, 10) : null;
      const o = selArt.selectedOptions[0];
      if (l.articol_id && o && o.dataset.den) {
        l.descriere = o.dataset.den;
        den.value = o.dataset.den;
        den.dispatchEvent(new Event("input"));  // completeaza denumirea + declanseaza potrivirea cotei
      }
    });
    del.addEventListener("click", () => { const p = linii.indexOf(l); if (p >= 0) linii.splice(p, 1); deseneazaLinii(); });
  }

  // re-randare INTEGRALA din model (cap.24 regula 1): NU se muta noduri individual; valorile tastate pe randurile
  // ramase supravietuiesc (sunt in model). Se re-leaga listenerii cu indici proaspeti.
  function deseneazaLinii() {
    zonaLinii.innerHTML = linii.map((_, i) => randLinie(i)).join("");
    linii.forEach((_, i) => legaLinie(i));
    recalc();
  }

  function recalc() {
    let baza = 0, tva = 0;
    linii.forEach((l) => {
      if (!l) return;
      const val = (l.cantitate || 0) * (l.pret_unitar || 0);
      baza += val;
      tva += val * ((l.cota_tva || 0) / 100);
    });
    const total = baza + tva;
    corp.querySelector("#em-total").innerHTML = `
      <div class="em-total-rand"><span>Bază</span><b>${baza.toLocaleString("ro-RO", {minimumFractionDigits:2, maximumFractionDigits:2})} ${monedaSel}</b></div>
      <div class="em-total-rand"><span>TVA</span><b>${tva.toLocaleString("ro-RO", {minimumFractionDigits:2, maximumFractionDigits:2})} ${monedaSel}</b></div>
      <div class="em-total-rand em-total-mare"><span>Total</span><b>${total.toLocaleString("ro-RO", {minimumFractionDigits:2, maximumFractionDigits:2})} ${monedaSel}</b></div>`;
  }

  corp.querySelector("#em-add-linie").addEventListener("click", () => { linii.push(linieNoua()); deseneazaLinii(); });
  linii.push(linieNoua());  // prima linie
  deseneazaLinii();

  // verificare CUI
  corp.querySelector("#em-verifica").addEventListener("click", async () => {
    const cui = corp.querySelector("#em-cui").value.trim();
    const stare = corp.querySelector("#em-cui-stare");
    if (!cui) return;
    // [vies_emitere_v1] cod TVA UE (prefix stat membru != RO) -> verificare VIES, nu ANAF
    const pfx = (cui.slice(0, 2) || "").toUpperCase();
    const UE = ["AT","BE","BG","CY","CZ","DE","DK","EE","EL","ES","FI","FR","HR","HU","IE","IT","LT","LU","LV","MT","NL","PL","PT","SE","SI","SK","XI"];
    if (UE.includes(pfx)) {
      stare.textContent = "se verifică în VIES…";
      stare.className = "em-cui-stare";
      try {
        const v = await api.get(`/tenants/${tenantId}/verifica-vies?cod_tva=${encodeURIComponent(cui)}`);
        if (v && v.valid) {
          // unele state (ex. DE) nu divulga nume/adresa -> VIES intoarce "---"
          if (v.nume && v.nume !== "---") corp.querySelector("#em-nume").value = v.nume;
          if (v.adresa && v.adresa !== "---") corp.querySelector("#em-adresa").value = v.adresa.trim();
          stare.innerHTML = `<span class="em-cui-info">valid în VIES · ${esc(v.tara || pfx)}</span>`;
          stare.className = "em-cui-stare";
        } else {
          stare.textContent = "cod TVA INVALID în VIES — scutirea intracomunitară nu se aplică";
          stare.className = "em-cui-stare em-cui-rau";
        }
      } catch {
        stare.textContent = "VIES indisponibil — reîncearcă";
        stare.className = "em-cui-stare em-cui-rau";
      }
      return;
    }
    stare.textContent = "se verifică la ANAF…";
    stare.className = "em-cui-stare";
    try {
      const r = await api.get(`/tenants/${tenantId}/verifica-cui/${encodeURIComponent(cui)}`);
      if (r && r.gasit) {
        corp.querySelector("#em-nume").value = r.denumire || "";
        if (r.adresa) corp.querySelector("#em-adresa").value = r.adresa;
        // [p113_doar_gri] doar info TVA cu gri, fara verde/bifa/"gasita"
        stare.innerHTML = `<span class="em-cui-info">${r.platitor_tva ? "plătitor TVA" : "neplătitor TVA"}</span>`;
        stare.className = "em-cui-stare";
        // [p109_avert_inactiv] avertisment mare pentru firma INACTIVA
        const av = corp.querySelector("#em-avert-inactiv");
        if (av) av.remove();
        if (r.inactiv) {
          const box = document.createElement("div");
          box.id = "em-avert-inactiv";
          box.className = "em-avert-inactiv";
          box.innerHTML = `
            <div class="em-avert-titlu">⚠ ATENȚIE: firmă INACTIVă fiscal la ANAF</div>
            <div class="em-avert-text">
              Dacă emiți factura către această firmă:<br>
              • beneficiarul <b>NU își poate deduce cheltuiala și nici TVA-ul</b> de pe factura ta (art. 11 Cod fiscal);<br>
              • o firmă inactivă poate fi în curs de dizolvare — există risc real de <b>neplată</b>;<br>
              • tranzacția poate atrage <b>controale ANAF</b>.<br>
              Verifică situația înainte de a continua. Poți emite, dar pe răspunderea ta.
            </div>`;
          stare.parentNode.insertBefore(box, stare.nextSibling);
        }
      } else {
        stare.textContent = "CUI negăsit la ANAF";
        stare.className = "em-cui-stare em-cui-rau";
      }
    } catch {
      stare.textContent = "verificarea a eșuat";
      stare.className = "em-cui-stare em-cui-rau";
    }
  });

  // emitere
  // selector moneda -> actualizeaza starea + totalurile + nota
  const selMon = corp.querySelector("#em-moneda");
  const notaMon = corp.querySelector("#em-moneda-nota");
  if (selMon) {
    selMon.addEventListener("change", () => {
      monedaSel = selMon.value || "RON";
      if (notaMon) notaMon.textContent = monedaSel === "RON"
        ? "" : "TVA se convertește în lei la cursul BNR (art. 319).";
      recalc();
    });
  }

  // plaseaza erorile field-keyed din 422 (backendul: {camp: em-l{i}-..., eticheta}, purtate de api.js ca
  // {camp, mesaj}) LANGA campul lor (cap.6 mecanism A). Cele fara #camp in DOM -> zona generica (fallback B).
  function plaseazaErori(rez, e) {
    curataEroriCamp(corp);
    const eris = (e && e.erori_campuri) || [];
    const rest = [];
    eris.forEach((x) => { if (!eroareCamp(corp, x.camp, x.mesaj)) rest.push(x.mesaj); });
    if (rest.length) { rez.textContent = "Completează câmpurile: " + rest.join("; "); rez.className = "em-rezultat em-rau"; }
    else if (!eris.length) { rez.textContent = (e && typeof e.mesaj === "string" && e.mesaj) || "Emiterea a eșuat. Încearcă din nou."; rez.className = "em-rezultat em-rau"; }
    else { rez.textContent = ""; rez.className = "em-rezultat"; }
  }

  async function trimiteEmitere(cursManual) {
    const rez = corp.querySelector("#em-rezultat");
    curataEroriCamp(corp);
    // NU se filtreaza randuri (cap.24 regula 2): lista trimisa = lista randata. Un rand incomplet se
    // valideaza pe backend si se raporteaza langa campul lui, nu dispare tacit.
    const payload = {
      linii: linii.map((l) => ({
        descriere: l.descriere, cantitate: l.cantitate,
        pret_unitar: l.pret_unitar, cota_tva: l.cota_tva,
        articol_id: l.articol_id || null,  // [punte_stoc_v1] F172
      })),
      tert_nume: corp.querySelector("#em-nume").value.trim() || null,
      tert_cui: corp.querySelector("#em-cui").value.trim() || null,
      tert_adresa: corp.querySelector("#em-adresa").value.trim() || null,
      moneda: monedaSel,
      tert_tara: (corp.querySelector("#em-tara") || {}).value || "RO",              // [B1 D300]
      tip_operatiune: (corp.querySelector("#em-tipop") || {}).value || "normal",    // [B1 D300]
    };
    if (cursManual != null) payload.curs_manual = cursManual;
    if (pleacaMarfaCurent !== null) payload.pleaca_marfa = pleacaMarfaCurent;  // [punte_stoc_v1] raspuns poarta

    const btn = corp.querySelector("#em-emite");
    if (btn) { btn.disabled = true; btn.textContent = "Se emite…"; }
    const rez2 = corp.querySelector("#em-rezultat");
    try {
      const selTip = corp.querySelector("#em-tip");
      if (selTip) payload.tip = selTip.value;
      const r = await api.post(`/tenants/${tenantId}/facturi/emite`, payload);
      let notaStoc = "";  // [punte_stoc_v1] rezultatul descarcarii de gestiune, daca poarta a fost DA
      if (r.descarcare) {
        const nd = (r.descarcare.descarcate || []).length, ne = (r.descarcare.erori || []).length;
        notaStoc = ` · ${nd} articol${nd === 1 ? "" : "e"} descărcat${nd === 1 ? "" : "e"} din gestiune`;
        if (ne) notaStoc += ` (${ne} nu — stoc insuficient)`;
      }
      rez2.innerHTML = `✓ Factura <b>${esc(r.numar)}</b> emisă · total ${Number(r.total).toLocaleString("ro-RO", {minimumFractionDigits:2})} ${monedaSel}${notaStoc}. A fost trimisă către contabil.`;
      rez2.className = "em-rezultat em-bun";
      setTimeout(() => { if (opt.dupaEmitere) opt.dupaEmitere(); }, 1200);
    } catch (e) {
      const det = e && e.mesaj;
      const cursIndisp = e && e.cod === 409 && det && typeof det === "object" && det.cod === "CURS_INDISPONIBIL";
      if (cursIndisp) {
        arataCursIndisponibil(det);
      } else {
        plaseazaErori(rez2, e);
      }
      if (btn) { btn.disabled = false; btn.textContent = "Emite factură"; }
    }
  }

  function arataCursIndisponibil(det) {
    const rez = corp.querySelector("#em-rezultat");
    rez.className = "em-rezultat";
    rez.innerHTML = `
      <div class="em-curs-box">
        <div class="em-curs-titlu">⚠ Cursul BNR nu e disponibil momentan (${det.moneda}, ${dataRo(det.data)}).</div>
        <div class="em-curs-actiuni">
          <button class="buton-primar em-curs-retry" id="em-curs-retry">Reîncearcă</button>
          <button class="buton-secundar em-buton-sec" id="em-curs-manual">Introdu manual</button>
        </div>
        <div id="em-curs-manual-zona"></div>
      </div>`;
    rez.querySelector("#em-curs-retry").addEventListener("click", () => trimiteEmitere(null));
    rez.querySelector("#em-curs-manual").addEventListener("click", () => {
      const zona = rez.querySelector("#em-curs-manual-zona");
      zona.innerHTML = `
        <div class="em-curs-manual">
          <label>Curs ${det.moneda} → RON pentru ${dataRo(det.data)}</label>
          <input type="number" step="0.0001" id="em-curs-val" placeholder="ex. 5.2438" class="camp-input">
          <button class="buton-primar" id="em-curs-ok">Emite cu acest curs</button>
          <div class="em-curs-avertisment">Introdu cursul BNR valabil pentru data facturii. Răspunderea corectitudinii îți revine.</div>
        </div>`;
      zona.querySelector("#em-curs-ok").addEventListener("click", () => {
        const v = parseFloat(zona.querySelector("#em-curs-val").value);
        if (!v || v <= 0) { zona.querySelector("#em-curs-val").focus(); return; }
        trimiteEmitere(v);
      });
    });
  }

  // [punte_stoc_v1] F172: poarta "pleaca marfa acum?" INAINTE de emitere, la firma CV cu linie de
  // articol (caseta-poarta, DS cap.5 v2.14). Fara articole -> emitere directa, flux identic cu azi.
  function porniEmitere() {
    const tip = (corp.querySelector("#em-tip") || {}).value || "factura";
    const cuArticole = linii.filter((l) => l && l.articol_id).length;
    if (cuArticole && tip === "factura") {
      const rez = corp.querySelector("#em-rezultat");
      rez.className = "em-rezultat";
      rez.innerHTML = `
        <div class="caseta-poarta">
          <div class="cp-mesaj">Pleacă marfa acum? ${cuArticole} articol${cuArticole === 1 ? "" : "e"} de pe factură se descarcă din gestiune dacă marfa pleacă fizic azi. Dacă e avans, livrare ulterioară sau serviciu, alege „Nu, doar factură".</div>
          <div class="cp-butoane">
            <button class="buton-primar" id="em-poarta-da">Da, pleacă marfa</button>
            <button class="buton-secundar em-buton-sec" id="em-poarta-nu">Nu, doar factură</button>
          </div>
        </div>`;
      rez.querySelector("#em-poarta-da").addEventListener("click", () => { pleacaMarfaCurent = true; trimiteEmitere(null); });
      rez.querySelector("#em-poarta-nu").addEventListener("click", () => { pleacaMarfaCurent = false; trimiteEmitere(null); });
    } else {
      pleacaMarfaCurent = null;
      trimiteEmitere(null);
    }
  }
  corp.querySelector("#em-emite").addEventListener("click", porniEmitere);
}

// audit_cab_lot1_v1

// emitere_inapoi_v1

// numerotare_configurata_v1

// fara_precompletari_v1
// emitere_std_v1 · batch 3b: randuri dinamice cap.24 (model pozitional + re-randare + stergere splice + backend autoritar 422.campuri)
