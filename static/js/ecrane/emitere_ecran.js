// emitere_ecran.js  // [p124_orfani]  // [p123_scot_butoane] — emitere facturi (reutilizabil: portal client, gratuit, cabinet).
// Flux:
//   1. daca numerotarea nu e configurata -> intreaba "ai mai emis facturi?"
//      DA -> serie + ultimul numar (continuitate); NU -> serie optionala, start 1
//   2. formular emitere: beneficiar (CUI verificat ANAF) + linii (cota auto) + total live
// Apelare: randeazaEmitere(corp, nav, tenantId, { inapoi, dupaEmitere })
// [cap.24 batch 3b] randuri dinamice: model pozitional cu valori + re-randare integrala + stergere/rand (splice);
// validarea per-linie o face BACKENDUL (facturi_api.linii_campuri_lipsa -> 422.campuri {camp,eticheta}); frontendul
// NU mai filtreaza randuri si plaseaza erorile langa campul lor prin eroareCamp (cap.6 mecanism A).
import { api, bani, dataRo, esc, eroareCamp, curataEroriCamp, semnAjutor, dataIso, cantitate } from "../api.js?v=4c8f1ff171";
import { randeazaDateFirma } from "./date_firma.js?v=77c317b1d1";  // [lot 19 d12] refuzul capitalului trimite la Date firmă

export async function randeazaEmitere(corp, nav, tenantId, opt = {}) {
  const inapoi = opt.inapoi || (() => nav && nav.inapoi && nav.inapoi());
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;

  // citesc numerotarea; daca nu e configurata (serie null si urmator 1 fara facturi) -> config
  let num = { serie: null, urmator_numar: 1, configurata: false };
  // data emiterii implicită = azi (local); cotele permise se cer LA EA, nu la „azi” de pe server
  try { num = await api.get(`/tenants/${tenantId}/facturi/numerotare?data=${dataIso()}`); } catch {}
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
    opt.tvaProfil = tvaProfil;   // [lot 19 pct.4d] neplatitor -> liniile nu poarta TVA (CF art.310 alin.(10) lit.b))
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
        <button data-actiune="PUT /tenants/{tenant_id}/facturi/numerotare|POST /tenants/{tenant_id}/firma-profil/regim-tva" class="buton-primar" id="em-da">Da, am mai emis</button>
        <button data-actiune="PUT /tenants/{tenant_id}/facturi/numerotare|POST /tenants/{tenant_id}/firma-profil/regim-tva" class="buton-secundar em-buton-sec" id="em-nu">Nu, încep acum</button>
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
        <label for="em-serie">Seria facturilor (ex: KAI-)<span class="oblig">*</span></label>
        <input class="camp-input" id="em-serie" placeholder="ex: KAI-" autocomplete="off">
      </div>
      <div class="em-config-camp">
        <label for="em-ultim">Numărul ultimei facturi emise</label>
        <input class="camp-input" id="em-ultim" type="number" placeholder="ex: 147">
      </div>
      <p class="em-hint">Vom continua de la numărul următor.</p>
      <button class="buton-primar" id="em-salveaza-config" data-actiune="PUT /tenants/{tenant_id}/facturi/numerotare|POST /tenants/{tenant_id}/firma-profil/regim-tva">Continuă</button>`;
    zona.querySelector("#em-salveaza-config").addEventListener("click", async () => {
      const serie = zona.querySelector("#em-serie").value.trim() || null;
      if (!serie) { let m = zona.querySelector(".msg-eroare"); if (!m) { m = document.createElement("p"); m.className = "msg-eroare"; zona.appendChild(m); } m.textContent = "Completează seria: numărul facturii se dă într-o serie (CF art.319 alin.(20) lit.a)."; return; }
      if (serie && /^\d+$/.test(serie)) { let m = zona.querySelector(".msg-eroare"); if (!m) { m = document.createElement("p"); m.className = "msg-eroare"; zona.appendChild(m); } m.textContent = "Seria conține doar cifre. Seria e un prefix cu litere (ex: KAI- sau FCT-). Numărul ultimei facturi se pune în câmpul următor."; return; }
      const ultim = parseInt((zona.querySelector("#em-ultim").value || "").trim(), 10);
      if (!Number.isFinite(ultim) || ultim < 1) { let m = zona.querySelector(".msg-eroare"); if (!m) { m = document.createElement("p"); m.className = "msg-eroare"; zona.appendChild(m); } m.textContent = "Completează numărul ultimei facturi emise (nu putem presupune numărul 1)."; return; }
      const start = ultim + 1;   // #10: cerut explicit, nu fabricat
      if (platitorTva === null) { let m = zona.querySelector(".msg-eroare"); if (!m) { m = document.createElement("p"); m.className = "msg-eroare"; zona.appendChild(m); } m.textContent = "Alege dacă firma e plătitoare de TVA."; return; }
      await salveazaConfig(tenantId, serie, start, tvaDinProfil ? null : platitorTva);
      if (opt.dupaSalvare) opt.dupaSalvare(); else randeazaEmitere(corp, nav, tenantId, opt);   // [pct.4] din „Schimbă seria”: înapoi la factură
    });
  });

  corp.querySelector("#em-nu").addEventListener("click", () => {
    zona.innerHTML = `
      <div class="em-config-camp">
        <label for="em-serie2">Seria facturilor (ex: FCT-)<span class="oblig">*</span></label>
        <input class="camp-input" id="em-serie2" placeholder="ex: FCT-" autocomplete="off">
      </div>
      <p class="em-hint">Prima factură va avea numărul 1.</p>
      <button class="buton-primar" id="em-salveaza-config2" data-actiune="PUT /tenants/{tenant_id}/facturi/numerotare|POST /tenants/{tenant_id}/firma-profil/regim-tva">Continuă</button>`;
    zona.querySelector("#em-salveaza-config2").addEventListener("click", async () => {
      const serie = zona.querySelector("#em-serie2").value.trim() || null;
      if (!serie) { let m = zona.querySelector(".msg-eroare"); if (!m) { m = document.createElement("p"); m.className = "msg-eroare"; zona.appendChild(m); } m.textContent = "Completează seria: numărul facturii se dă într-o serie (CF art.319 alin.(20) lit.a)."; return; }
      if (serie && /^\d+$/.test(serie)) { let m = zona.querySelector(".msg-eroare"); if (!m) { m = document.createElement("p"); m.className = "msg-eroare"; zona.appendChild(m); } m.textContent = "Seria conține doar cifre. Seria e un prefix cu litere (ex: KAI- sau FCT-)."; return; }
      if (platitorTva === null) { let m = zona.querySelector(".msg-eroare"); if (!m) { m = document.createElement("p"); m.className = "msg-eroare"; zona.appendChild(m); } m.textContent = "Alege dacă firma e plătitoare de TVA."; return; }
      await salveazaConfig(tenantId, serie, 1, tvaDinProfil ? null : platitorTva);
      if (opt.dupaSalvare) opt.dupaSalvare(); else randeazaEmitere(corp, nav, tenantId, opt);   // [pct.4] din „Schimbă seria”: înapoi la factură
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
      <span class="em-numar" id="em-numar">${num.serie ? `Seria <b>${esc(num.serie)}</b> · ` : ""}nr. <b>${esc(String(num.urmator_numar))}</b></span>
    </div>
    <div class="em-pregatire" id="em-pregatire" role="note"></div>
    <div class="em-sectiune em-date-doc">
      <div class="em-eticheta">Document (CF art. 319 alin. (20) lit. a–b)</div>
      <div class="em-date-rand">
        <label class="camp"><span class="camp-eticheta">Seria și numărul</span>
          <span class="em-serie-nr" id="em-serie-nr">${num.serie ? esc(num.serie) + " · " : "fără serie (se cere la emitere) · "}următorul număr: ${esc(String(num.urmator_numar))}</span>
          <button type="button" class="btn-link" id="em-schimba-serie" data-actiune="PUT /tenants/{tenant_id}/facturi/numerotare">Schimbă seria / numerotarea</button></label>
        <label class="camp"><span class="camp-eticheta">Data emiterii<span class="oblig">*</span></span>
          <input class="camp-input" id="em-data" type="date" value="${dataIso()}"></label>
        <label class="camp"><span class="camp-eticheta">Data scadenței</span>
          <input class="camp-input" id="em-scadenta" type="date"></label>
      </div>
      <p class="camp-ajutor">Scadența intră în scadențar; o factură fără scadență nu are termen de plată urmărit.</p>
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
      <div class="camp-eticheta">Linie: denumire · cantitate · preț unitar <span class="oblig">*</span> <span class="tip-micut">${opt.tvaProfil === false ? "(firma nu e plătitoare de TVA: liniile nu poartă TVA — regim special de scutire, art. 310 Cod fiscal)" : "(cota TVA e propusă automat pe baza denumirii produsului — verifică încadrarea și schimb-o din listă dacă e altfel; răspunderea corectitudinii cotei îți aparține, iar schimbarea se consemnează)"}</span></div>
      <div class="em-linie-antet" aria-hidden="true"><span>Denumire</span><span class="ant-cant">Cant.</span><span class="ant-um">UM</span><span class="ant-pret">Preț</span><span class="ant-cota">Cotă</span><span></span></div>
      <div class="em-linii" id="em-linii"></div>
      <button class="buton-secundar em-buton-sec" id="em-add-linie" data-fara-actiune="rând în formular; salvarea formularului poartă acțiunea">+ Adaugă linie</button>
    </div>

    <div class="em-total" id="em-total"></div>
    <div class="em-moneda-rand">
      <label class="em-moneda-eticheta" for="em-moneda">Monedă</label>
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
      <label class="camp-eticheta" for="em-bon-nr">Emisă pe baza bonului fiscal — nr. bon (dacă e cazul)</label>
      <input class="camp-input" id="em-bon-nr" type="text" maxlength="30" placeholder="ex. 0042">
      <label class="camp-eticheta" for="em-bon-data">Data bonului fiscal</label>
      <input class="camp-input" id="em-bon-data" type="date">
      <p class="camp-ajutor">Pentru o factură cerută de client pentru un bon deja emis: vânzarea e în raportul Z, deci factura nu se mai numără a doua oară (D300, D394, evidență, stoc). Pe factură apare „conform bon fiscal nr./data”.</p>
    </div>
    <div class="em-actiuni">
      <select id="em-tip" class="camp-input" aria-label="Tipul documentului emis" style="max-width:180px;margin-right:8px">
        <option value="factura">Factura</option>
        <option value="proforma">Proforma</option>
        <option value="aviz">Aviz insotire</option>
      </select>
      <button class="buton-primar em-emite" id="em-emite" data-actiune="POST /tenants/{tenant_id}/facturi/emite">Emite factură</button>
    </div>
    <div class="em-rezultat" id="em-rezultat"></div>`;

  // [comanda Costin 05.10.2026 pct.2] „Datele firmei care blochează emiterea se verifică la deschiderea «Emite factură», nu după
  // completarea întregului formular.” Lipsurile vin de la server (aceeași regulă ca refuzul emiterii, `capital_social.lipsa`).
  // „Emite” rămâne inactiv cu motivul vizibil; la revenirea din Date firmă (`nav:revenire`) se reverifică.
  const zonaPreg = corp.querySelector("#em-pregatire");
  const btnEmite = corp.querySelector("#em-emite");
  function aratăPregatirea(n) {
    const lipsuri = (n && n.lipsuri_firma) || [];
    if (!lipsuri.length) { zonaPreg.innerHTML = ""; btnEmite.disabled = false; btnEmite.title = ""; return; }
    zonaPreg.innerHTML = `<div class="caseta-atentie"><div class="ca-mesaj">${esc(n.mesaj_lipsuri || "")}</div></div>
      <div class="ca-actiuni"><button type="button" class="buton-secundar" id="em-date-firma-sus" data-fara-actiune="navigare la Date firmă (salvarea lor e acolo)">Deschide Date firmă</button></div>`;
    btnEmite.disabled = true;
    btnEmite.title = "Completează întâi în Date firmă: " + lipsuri.join(", ");
    zonaPreg.querySelector("#em-date-firma-sus").addEventListener("click", () =>
      nav.deschide("Date firmă", (c2) => randeazaDateFirma(c2, nav, tenantId)));
  }
  function aratăNumarul(n) {
    const sn = corp.querySelector("#em-serie-nr"), nr = corp.querySelector("#em-numar");
    if (sn) sn.textContent = (n.serie ? n.serie + " · " : "fără serie (se cere la emitere) · ") + "următorul număr: " + n.urmator_numar;
    if (nr) nr.innerHTML = (n.serie ? `Seria <b>${esc(n.serie)}</b> · ` : "") + `nr. <b>${esc(String(n.urmator_numar))}</b>`;
  }
  aratăPregatirea(num);
  // reîncarcă ce depinde de Date firmă și de DATA facturii: lipsurile, numerotarea, cotele permise la data aleasă
  async function reincarcaPregatirea() {
    const data = (corp.querySelector("#em-data") || {}).value || dataIso();
    try {
      const n = await api.get(`/tenants/${tenantId}/facturi/numerotare?data=${encodeURIComponent(data)}`);
      aratăPregatirea(n); aratăNumarul(n);
      const cote = (n.cote_permise && n.cote_permise.length) ? n.cote_permise : [];
      if (cote.join(",") !== COTE.join(",")) { COTE = cote; deseneazaLinii(); }   // altă perioadă de cote -> lista pe fiecare linie
    } catch { /* rămâne starea de dinainte */ }
  }
  corp.addEventListener("nav:revenire", reincarcaPregatirea);
  corp.querySelector("#em-data").addEventListener("change", reincarcaPregatirea);
  // [comanda Costin 05.10.2026 pct.4] seria se vede și se poate stabili: configurarea numerotării, într-o fereastră PESTE factură
  corp.querySelector("#em-schimba-serie").addEventListener("click", () =>
    nav.deschide("Numerotare facturi", (c2) => configureazaNumerotare(c2, nav, tenantId,
      Object.assign({}, opt, { dupaSalvare: () => nav.inapoi() }), opt.tvaProfil)));

  const zonaLinii = corp.querySelector("#em-linii");
  const linii = [];
  const articole = opt.articole || [];        // [punte_stoc_v1] F172: articole de stoc (gol la gratuit)
  let pleacaMarfaCurent = null;               // raspunsul la poarta "pleaca marfa acum?" pt emiterea curenta

  const linieNoua = () => ({ descriere: "", cantitate: "", um: "buc", pret_unitar: "", cota_tva: null, cota_propusa: null, articol_id: null });
  // [comanda Costin 05.10.2026 pct.3] „contabilul poate corecta cota; schimbarea rămâne consemnată (propus → ales, cine, când)”.
  // Cotele oferite = cele permise la data facturii, de la server (aceeași sursă ca validarea emiterii).
  let COTE = (num.cote_permise && num.cote_permise.length) ? num.cote_permise : [];   // se reîncarcă la schimbarea datei
  const platitor = opt.tvaProfil !== false;
  const _val = (x) => (x === "" || x == null) ? "" : esc(String(x));

  // randeaza O linie DIN MODEL (id-uri pozitionale em-l{i}-*, ca backendul sa lege eroarea de camp). Stergere/rand.
  function randLinie(i) {
    const l = linii[i];
    const cotaTxt = l.cota_tva == null ? "—" : (l.cota_tva === 0 ? "0%" : `${l.cota_tva}%`);
    const cotaCls = l.cota_tva == null ? "" : (l.cota_tva === 11 ? " cota-11" : l.cota_tva === 0 ? " cota-0" : " cota-21");
    const inputsHtml = `
      <input class="camp-input em-l-den" id="em-l${i}-descriere" data-actiune-camp="POST /tenants/{tenant_id}/produse/potriveste" value="${_val(l.descriere)}" placeholder="Denumire (ex: pâine, consultanță)" aria-label="Denumire articol" autocomplete="off">
      <input class="camp-input em-l-cant" id="em-l${i}-cantitate" type="number" step="0.001" value="${_val(l.cantitate)}" placeholder="Cant." aria-label="Cantitate" title="Cantitate">
      <input class="camp-input em-l-um" id="em-l${i}-um" maxlength="10" value="${_val(l.um)}" aria-label="Unitate de măsură" title="Unitate de măsură">
      <input class="camp-input em-l-pret" id="em-l${i}-pret_unitar" type="number" step="0.01" value="${_val(l.pret_unitar)}" placeholder="Preț" aria-label="Preț unitar" title="Preț unitar">
      ${platitor
        ? `<select class="camp-input em-l-cota-sel${cotaCls}" id="em-l${i}-cota" aria-label="Cota TVA" title="${l.cota_propusa == null ? "Cota TVA" : "Cota TVA — propusă: " + l.cota_propusa + "%"}">
             <option value=""${l.cota_tva == null ? " selected" : ""}>—</option>
             ${COTE.map((c) => `<option value="${c}"${l.cota_tva === c ? " selected" : ""}>${c}%</option>`).join("")}
           </select>`
        : `<span class="em-l-cota${cotaCls}" id="em-l${i}-cota" title="Cota TVA">${cotaTxt}</span>`}
      <button type="button" class="buton-sters em-l-sterge" data-idx="${i}" title="Șterge">×</button>`;
    if (articole.length) {
      const selArticol = `
        <select class="camp-input em-l-articol" id="em-l${i}-articol" aria-label="Articol de stoc" style="margin-bottom:6px">
          <option value="">— fără articol (serviciu) —</option>
          ${articole.map((a) => `<option value="${a.id}"${String(a.id) === String(l.articol_id) ? " selected" : ""} data-den="${esc(a.denumire)}" data-um="${esc(a.um || "")}">${esc(a.denumire)} · stoc ${esc(cantitate(a.stoc, a.um))}</option>`).join("")}
        </select>`;
      // [05.10.2026, comanda Costin pct.9] pe o firmă cu stoc, linia fără articol spune că marfa nu se descarcă din gestiune
      const faraArt = `<div class="caseta-atentie em-l-fara-articol" id="em-l${i}-fara-articol"${(l.descriere && !l.articol_id) ? "" : " hidden"}><div class="ca-mesaj">Linie fără articol de stoc: marfa de pe ea nu se descarcă din gestiune. Dacă e marfă, alege articolul; dacă e serviciu, lasă așa.</div></div>`;
      return `<div class="em-linie-wrap" data-idx="${i}">${selArticol}<div class="em-linie">${inputsHtml}</div>${faraArt}</div>`;
    }
    return `<div class="em-linie" data-idx="${i}">${inputsHtml}</div>`;
  }

  // actualizeaza afisajul cotei pt OBIECTUL l la pozitia lui CURENTA (splice-safe cu fetch-ul async in zbor)
  function setCota(l, text, cota) {
    const p = linii.indexOf(l);
    if (p < 0) return;
    const el = zonaLinii.querySelector("#em-l" + p + "-cota");
    if (!el) return;
    const cls = (cota === 11 ? " cota-11" : cota === 0 ? " cota-0" : cota != null ? " cota-21" : "");
    if (el.tagName === "SELECT") {   // plătitor: lista de cote, propunerea preselectată
      el.value = cota == null ? "" : String(cota);
      el.className = "camp-input em-l-cota-sel" + cls;
      el.title = l.cota_propusa == null ? "Cota TVA" : "Cota TVA — propusă: " + l.cota_propusa + "%";
      return;
    }
    el.textContent = text;
    el.className = "em-l-cota" + cls;
  }

  // inputurile scriu in MODEL (nu re-randeaza -> fara pierdere de focus la tastare). Fetch-ul cotei capteaza
  // OBIECTUL l (nu indexul), deci scrie corect chiar daca intre timp un splice a reindexat lista.
  function legaLinie(i) {
    const l = linii[i];
    const den = zonaLinii.querySelector("#em-l" + i + "-descriere");
    const cant = zonaLinii.querySelector("#em-l" + i + "-cantitate");
    const pret = zonaLinii.querySelector("#em-l" + i + "-pret_unitar");
    const um = zonaLinii.querySelector("#em-l" + i + "-um");
    const faraArt = zonaLinii.querySelector("#em-l" + i + "-fara-articol");
    const selArt = zonaLinii.querySelector("#em-l" + i + "-articol");
    const aratăFaraArticol = () => { if (faraArt) faraArt.hidden = !(l.descriere && !l.articol_id); };
    const del = zonaLinii.querySelector('.em-l-sterge[data-idx="' + i + '"]');
    let timer = null;
    den.addEventListener("input", () => {
      l.descriere = den.value.trim();
      aratăFaraArticol();
      l.cota_tva = null;  // reset -> se repotriveste
      clearTimeout(timer);
      const d = l.descriere;
      if (d.length < 3) { setCota(l, "—"); recalc(); return; }
      // [lot 19 pct.4d] neplatitor: cota e 0 prin lege, nu o propunere — fara apel de potrivire (care ar fi dat 21)
      if (opt.tvaProfil === false) { l.cota_tva = 0; setCota(l, "0%", 0); recalc(); return; }
      setCota(l, "…");
      timer = setTimeout(async () => {
        try {
          const r = await api.post(`/tenants/${tenantId}/produse/potriveste`, { denumire: d });
          if (r && r.ok) {
            l.cota_tva = r.cota; l.cota_propusa = r.cota; setCota(l, r.cota === 0 ? "0%" : `${r.cota}%`, r.cota);
            // [05.10.2026, comanda Costin pct.9] din nomenclator: prețul și UM, numai unde omul n-a scris deja altceva
            const p = linii.indexOf(l);
            if (r.um && !l.umScris) { l.um = r.um; const e = zonaLinii.querySelector("#em-l" + p + "-um"); if (e) e.value = r.um; }
            if (r.pret_unitar && !l.pret_unitar) { l.pret_unitar = r.pret_unitar; const e = zonaLinii.querySelector("#em-l" + p + "-pret_unitar"); if (e) e.value = r.pret_unitar; }
          }
        } catch {}
        recalc();
      }, 550);
    });
    const selCota = zonaLinii.querySelector("select#em-l" + i + "-cota");
    if (selCota) selCota.addEventListener("change", () => {   // [pct.3] contabilul alege; propunerea rămâne pentru jurnal
      l.cota_tva = selCota.value === "" ? null : Number(selCota.value);
      setCota(l, "", l.cota_tva);
      recalc();
    });
    cant.addEventListener("input", () => { l.cantitate = parseFloat(cant.value) || 0; recalc(); });
    um.addEventListener("input", () => { l.um = um.value.trim(); l.umScris = true; });
    pret.addEventListener("input", () => { l.pret_unitar = parseFloat(pret.value) || 0; recalc(); });
    if (selArt) selArt.addEventListener("change", () => {  // [punte_stoc_v1] F172
      l.articol_id = selArt.value ? parseInt(selArt.value, 10) : null;
      const o = selArt.selectedOptions[0];
      if (l.articol_id && o && o.dataset.um) { l.um = o.dataset.um; l.umScris = true; um.value = o.dataset.um; }   // UM-ul articolului din stoc
      aratăFaraArticol();
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

  // [R142, 04.09.2026] O COTA NECUNOSCUTA NU E O COTA DE ZERO.
  //
  // Pana azi linia de mai jos scria `(l.cota_tva || 0)`, deci o linie fara cota stabilita intra in
  // suma cu TVA zero — iar ecranul afisa «TVA 0,00» si «Total = Baza» pe o firma PLATITOARE de TVA.
  // Gasit apasand, in lotul 12: formular umplut, cota nealeasa, si totalul afirma linistit ca
  // factura n-are TVA. *Cifra de aici e ce citeste contabilul si ce pleaca mai departe; „Total =
  // Baza" pe un platitor de TVA e o afirmatie falsa despre bani.*
  //
  // Ecranul STIA deja raspunsul, cu doua sute de linii mai sus: coloana COTA a liniei randeaza „—"
  // cand `cota_tva == null` (randLinie). Acelasi ecran spunea „nu se stie" intr-o coloana si „zero"
  // in alta, despre acelasi lucru.
  //
  // CE NU SE SCHIMBA, si se declara: clasa `cota || 0` din restul aplicatiei ramane inchisa — garda
  // R29 o declara explicit in afara domeniului ei („defaultul pe ZERO, alta clasa, legitima in
  // aritmetica, 18 instante reale"), iar decizia lui Costin (04.09) e ca se repara INSTANTA de aici,
  // pentru ca aici cifra e citita de om, nu clasa. Celelalte 18 raman unde sunt.
  //
  // O linie de valoare ZERO nu blocheaza totalul: la valoare zero, TVA-ul e zero orice cota ar avea,
  // deci necunoasterea ei nu schimba nimic. Asa, o linie goala nou-adaugata nu face totalul „—".
  function recalc() {
    let baza = 0, tva = 0, faraCota = 0;
    linii.forEach((l) => {
      if (!l) return;
      const val = (l.cantitate || 0) * (l.pret_unitar || 0);
      baza += val;
      if (val !== 0 && (l.cota_tva === null || l.cota_tva === undefined)) { faraCota++; return; }
      // [interdictia 4, 23.08.2026] ROTUNJIRE PE LINIE, ca la server. Suma nerotunjita diverge:
      // 50 de randuri de 3 x 19,99 la 21% -> serverul 629,50, ecranul arata 629,69. Contabilul vedea
      // un total pe care factura salvata nu-l avea. Calculul RAMANE o duplicare a regulii fiscale in
      // prezentare (chiar interdictia 4) - aici se opreste doar cifra gresita, nu duplicarea.
      tva += Math.round(val * ((l.cota_tva || 0) / 100) * 100) / 100;
    });
    const cu = (x) => `${bani(x)} ${monedaSel}`;   // `bani()` e formatorul canonic (api.js); aici doar i se adauga moneda
    const nestiut = faraCota > 0;
    corp.querySelector("#em-total").innerHTML = `
      <div class="em-total-rand"><span>Bază</span><b>${cu(baza)}</b></div>
      <div class="em-total-rand"><span>TVA</span><b>${nestiut ? "—" : cu(tva)}</b></div>
      <div class="em-total-rand em-total-mare"><span>Total</span><b>${nestiut ? "—" : cu(baza + tva)}</b></div>
      ${nestiut ? `<p class="ecran-nota" id="em-total-nota">TVA-ul nu se poate calcula încă: cota nu e stabilită pe ${faraCota} lini${faraCota === 1 ? "e" : "i"}. Se propune automat din denumire — scrie denumirea articolului (sau alege-l din stoc) și așteaptă propunerea.</p>` : ""}`;
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
        descriere: l.descriere, cantitate: l.cantitate, um: l.um || "buc",
        pret_unitar: l.pret_unitar, cota_tva: l.cota_tva,
        cota_propusa: l.cota_propusa,   // [pct.3] pentru jurnalul „propus → ales”
        articol_id: l.articol_id || null,  // [punte_stoc_v1] F172
      })),
      tert_nume: corp.querySelector("#em-nume").value.trim() || null,
      tert_cui: corp.querySelector("#em-cui").value.trim() || null,
      tert_adresa: corp.querySelector("#em-adresa").value.trim() || null,
      moneda: monedaSel,
      tert_tara: (corp.querySelector("#em-tara") || {}).value || "RO",              // [B1 D300]
      tip_operatiune: (corp.querySelector("#em-tipop") || {}).value || "normal",    // [B1 D300]
      // [decizia A 02.10] factura emisă pe baza bonului fiscal (HG 1/2016 pct.97 alin.(1)); validarea e pe server
      bon_fiscal_nr: ((corp.querySelector("#em-bon-nr") || {}).value || "").trim() || null,
      bon_fiscal_data: (corp.querySelector("#em-bon-data") || {}).value || null,
      // [comanda Costin 05.10.2026 pct.4] data emiterii și scadența, stabilite pe formular
      data_emitere: (corp.querySelector("#em-data") || {}).value || null,
      data_scadenta: (corp.querySelector("#em-scadenta") || {}).value || null,
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
      const capLipsa = e && e.detaliu && e.detaliu.cod === "CAPITAL_SOCIAL_LIPSA";
      const serieLipsa = e && e.detaliu && e.detaliu.cod === "SERIE_LIPSA";
      if (cursIndisp) {
        arataCursIndisponibil(det);
      } else if (serieLipsa) {
        arataSerieLipsa(e.detaliu);
      } else if (capLipsa) {
        arataCapitalLipsa(e.detaliu);
      } else {
        plaseazaErori(rez2, e);
      }
      if (btn) { btn.disabled = false; btn.textContent = "Emite factură"; }
    }
  }

  // [lot 19 d12] Refuzul pentru capitalul social lipsă (Legea 31/1990 art. 74 alin. (3)): formularul rămâne cum l-a
  // scris omul; butonul deschide Date firmă, iar la întoarcere „Emite” trimite aceeași factură.
  function arataCapitalLipsa(det) {
    const rez = corp.querySelector("#em-rezultat");
    rez.className = "em-rezultat";
    rez.innerHTML = `
      <div class="em-curs-box">
        <div class="em-curs-titlu">⚠ ${esc(det.mesaj || "")}</div>
        <div class="em-curs-actiuni">
          <button class="buton-primar" id="em-deschide-date-firma">Deschide Date firmă</button>
        </div>
      </div>`;
    rez.querySelector("#em-deschide-date-firma").addEventListener("click", () => {
      nav.deschide("Date firmă", (c2) => randeazaDateFirma(c2, nav, tenantId));
    });
  }

  // [06.10.2026, comanda Costin §6.1] Seria obligatorie (CF art.319 alin.(20) lit.a): refuzul NU blochează — seria se
  // stabilește chiar aici, numărul următor rămâne același, iar emiterea continuă cu factura scrisă.
  function arataSerieLipsa(det) {
    const rez = corp.querySelector("#em-rezultat");
    rez.className = "em-rezultat";
    rez.innerHTML = `
      <div class="em-curs-box">
        <div class="em-curs-titlu">⚠ ${esc(det.mesaj || "")}</div>
        <label class="camp"><span class="camp-eticheta">Seria facturilor (ex: FCT)<span class="oblig">*</span></span>
          <input class="camp-input" id="em-serie-noua" autocomplete="off" maxlength="12"></label>
        <div class="em-curs-actiuni">
          <button class="buton-primar" id="em-serie-si-emite" data-actiune="PUT /tenants/{tenant_id}/facturi/numerotare">Stabilește seria și emite</button>
        </div>
      </div>`;
    const inp = rez.querySelector("#em-serie-noua");
    inp.focus();
    rez.querySelector("#em-serie-si-emite").addEventListener("click", async () => {
      curataEroriCamp(rez);
      const serie = inp.value.trim();
      if (!serie) { eroareCamp(rez, "em-serie-noua", "Completează seria (legea cere numărul facturii într-o serie)."); return; }
      if (/^\d+$/.test(serie)) { eroareCamp(rez, "em-serie-noua", "Seria e un prefix cu litere (ex: FCT), nu un număr."); return; }
      try {
        await api.put(`/tenants/${tenantId}/facturi/numerotare`, { serie });   // numărul următor rămâne cel de acum
      } catch (er) { eroareCamp(rez, "em-serie-noua", (er && er.mesaj) || "Seria nu s-a putut salva."); return; }
      await reincarcaPregatirea();
      porniEmitere();
    });
  }

  function arataCursIndisponibil(det) {
    const rez = corp.querySelector("#em-rezultat");
    rez.className = "em-rezultat";
    rez.innerHTML = `
      <div class="em-curs-box">
        <div class="em-curs-titlu">⚠ Cursul BNR nu e disponibil momentan (${det.moneda}, ${dataRo(det.data)}).</div>
        <div class="em-curs-actiuni">
          <button class="buton-primar em-curs-retry" id="em-curs-retry">Reîncearcă</button>
          <button data-actiune="POST /tenants/{tenant_id}/facturi/emite" class="buton-secundar em-buton-sec" id="em-curs-manual">Introdu manual</button>
        </div>
        <div id="em-curs-manual-zona"></div>
      </div>`;
    rez.querySelector("#em-curs-retry").addEventListener("click", () => trimiteEmitere(null));
    rez.querySelector("#em-curs-manual").addEventListener("click", () => {
      const zona = rez.querySelector("#em-curs-manual-zona");
      zona.innerHTML = `
        <div class="em-curs-manual">
          <label for="em-curs-val">Curs ${det.moneda} → RON pentru ${dataRo(det.data)}</label>
          <input type="number" step="0.0001" id="em-curs-val" placeholder="ex. 5.2438" class="camp-input">
          <button class="buton-primar" id="em-curs-ok" data-actiune="POST /tenants/{tenant_id}/facturi/emite">Emite cu acest curs</button>
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
    // [decizia A 02.10] factura din bon nu descarcă gestiunea (marfa a ieșit cu bonul) -> fără poartă
    const dinBon = !!((corp.querySelector("#em-bon-nr") || {}).value || "").trim();
    if (cuArticole && tip === "factura" && !dinBon) {
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
