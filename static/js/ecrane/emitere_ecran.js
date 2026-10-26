// emitere_ecran.js  // [p124_orfani]  // [p123_scot_butoane] — emitere facturi (reutilizabil: portal client, gratuit, cabinet).
// Flux:
//   1. daca numerotarea nu e configurata -> intreaba "ai mai emis facturi?"
//      DA -> serie + ultimul numar (continuitate); NU -> serie optionala, start 1
//   2. formular emitere: beneficiar (CUI verificat ANAF) + linii (cota auto) + total live
// Apelare: randeazaEmitere(corp, nav, tenantId, { inapoi, dupaEmitere })
// [cap.24 batch 3b] randuri dinamice: model pozitional cu valori + re-randare integrala + stergere/rand (splice);
// validarea per-linie o face BACKENDUL (facturi_api.linii_campuri_lipsa -> 422.campuri {camp,eticheta}); frontendul
// NU mai filtreaza randuri si plaseaza erorile langa campul lor prin eroareCamp (cap.6 mecanism A).
import { api, ultimaCerere, pastreazaCampulActiv, arataMesaj, cate, bani, cursValutar, dataRo, esc, eroareCamp, curataEroriCamp, semnAjutor, dataIso, cantitate, confirmaCaseta, focusFaraSalt, aduInVedere, numarCuSerie, arataRefuzul, cereCompletate } from "../api.js?v=e38843b1ec";
import { textStareSpv } from "./spv_stare.js?v=228cdfcde1";  /* [lotul 6, 275c] */
import { sesiune } from "../sesiune.js?v=898215e0ee";
import { optiuniTara as _optiuniTara, taraDinCui } from "./tari_partener.js?v=43a0fddc7d";   // [lotul 12, C160] sursa unică
import { butonSpreEcran } from "./ecran_destinatie.js?v=0a2b447df1";  // [lotul 07.10 pct.2] refuzul care trimite în alt ecran are buton spre el
import { propuneNumeAnaf } from "./nume_anaf.js?v=d59cd56b02";   // [lotul 11, 444] numele ANAF vs fișa clientului
import { ciornaPeServer } from "../ciorna_formular.js?v=461bec469f";   // [495] ciorna facturii pe server (transportul comun al ciornelor)
import { legaDateAnaf } from "./date_anaf.js?v=503d474ed1";   // [lotul 12, 459.1] datele aduse de la ANAF / VIES țin de CUI-ul lor

export async function randeazaEmitere(corp, nav, tenantId, opt = {}) {
  const inapoi = opt.inapoi || (() => nav && nav.inapoi && nav.inapoi());
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;

  // citesc numerotarea; daca nu e configurata (serie null si urmator 1 fara facturi) -> config
  let num = { serie: null, urmator_numar: 1, configurata: false };
  // data emiterii implicită = azi (local); cotele permise se cer LA EA, nu la „azi” de pe server
  try { num = await api.get(`/tenants/${tenantId}/facturi/numerotare?data=${dataIso()}`); } catch {}
  // [tva_din_profil_v1] platitor_tva e deja in profil (Date firma/ANAF) - il citim ca sa NU re-intrebam (#16)
  let tvaProfil = null, tvaIncasare = null;
  try {
    const _v = await api.get(`/tenants/${tenantId}/vector`);
    if (_v && typeof _v.platitor_tva === "boolean") tvaProfil = _v.platitor_tva;
    tvaIncasare = (_v && _v.tva_incasare) || null;   // [lotul 10, deficiența 428] regimul TVA la încasare, din perioadele firmei
  }
  catch { tvaProfil = null; }  // vector indisponibil -> intreaba (nu presupune)

  const neconfigurat = !num.configurata;  // numerotare_configurata_v1
  if (neconfigurat) {
    configureazaNumerotare(corp, nav, tenantId, opt, tvaProfil, tvaIncasare);
  } else {
    // [punte_stoc_v1] F172: la firma de CABINET cu gestiune cantitativa (are articole), incarca
    // articolele de stoc pentru selectorul pe linie. Portalul client NU tine
    // gestiune -> nu se incarca, emit exact ca azi (fara poarta, fara articol_id).
    opt.articole = [];
    if (!opt.client) {
      try { opt.articole = (await api.get(`/tenants/${tenantId}/stocuri/articole`)).articole || []; } catch { opt.articole = []; }
    }
    opt.tvaProfil = tvaProfil;   // [lot 19 pct.4d] neplatitor -> liniile nu poarta TVA (CF art.310 alin.(10) lit.b))
    opt.tvaIncasare = tvaIncasare;   // [lotul 11, C85] „Schimbă seria” deschide aceeași Configurare emitere: și ea arată sistemul TVA la încasare
    await incarcaCiorna(tenantId);   // [495] ciorna de pe server (sau copia netrimisă din browser), înainte de prima desenare
    formularEmitere(corp, nav, tenantId, num, opt);
  }
}

// ---------- CONFIGURARE NUMEROTARE (o data) ----------
function configureazaNumerotare(corp, nav, tenantId, opt, tvaProfil = null, tvaIncasare = null) {
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
    </div>` : `<p class="pf-intro" id="em-config-regim">Regim TVA: <b>${tvaProfil ? "plătitoare de TVA" : "neplătitoare"}</b>${tvaProfil ? textRegimIncasare(tvaIncasare) : ""} (din profilul firmei).</p>`}
    <div class="em-config">
      <div class="em-intrebare">Ai mai emis facturi până acum (în alt program sau pe hârtie)?</div>
      <div class="em-optiuni">
        <button data-fara-actiune="arată câmpurile răspunsului; scrierea e pe „Continuă”" class="buton-primar" id="em-da">Da, am mai emis</button>
        <button data-fara-actiune="arată câmpurile răspunsului; scrierea e pe „Continuă”" class="buton-secundar em-buton-sec" id="em-nu">Nu, încep acum</button>
      </div>
      <!-- [lotul 13, 673 — DS cap.2a v2.104] răspunsul la întrebare arată câmpurile lui, chiar sub întrebare, în același formular (nu un
           formular scris în pagină de buton): cele două secțiuni sunt desenate o dată, „Da” / „Nu” o arată pe a lui -->
      <div class="em-config-form" id="em-config-form">
        <div id="em-config-da" hidden>
          <div class="em-config-camp">
            <label for="em-serie">Seria facturilor (ex: KAI-)<span class="oblig">*</span></label>
            <input class="camp-input" id="em-serie" placeholder="ex: KAI-" autocomplete="off">
          </div>
          <div class="em-config-camp">
            <label for="em-ultim">Numărul ultimei facturi emise</label>
            <input class="camp-input" id="em-ultim" type="number" placeholder="ex: 147">
          </div>
          <p class="em-hint">Vom continua de la numărul următor.</p>
          <button class="buton-primar" id="em-salveaza-config" data-actiune="PUT /tenants/{tenant_id}/facturi/numerotare|POST /tenants/{tenant_id}/firma-profil/regim-tva">Continuă</button>
        </div>
        <div id="em-config-nu" hidden>
          <div class="em-config-camp">
            <label for="em-serie2">Seria facturilor (ex: FCT-)<span class="oblig">*</span></label>
            <input class="camp-input" id="em-serie2" placeholder="ex: FCT-" autocomplete="off">
          </div>
          <p class="em-hint">Prima factură va avea numărul 1.</p>
          <button class="buton-primar" id="em-salveaza-config2" data-actiune="PUT /tenants/{tenant_id}/facturi/numerotare|POST /tenants/{tenant_id}/firma-profil/regim-tva">Continuă</button>
        </div>
      </div>
    </div>`;

  const zona = corp.querySelector("#em-config-form");
  const tvaDinProfil = tvaProfil !== null;   // [tva_din_profil_v1] profilul stie -> nu re-intrebam, nu suprascriem (#16)
  let platitorTva = tvaProfil;  // null daca profilul nu stie -> obligatoriu ales
  const bTvaDa = corp.querySelector("#em-tva-da"), bTvaNu = corp.querySelector("#em-tva-nu");
  if (bTvaDa && bTvaNu) {
    bTvaDa.addEventListener("click", () => { platitorTva = true; bTvaDa.classList.add("buton-activ"); bTvaNu.classList.remove("buton-activ"); });
    bTvaNu.addEventListener("click", () => { platitorTva = false; bTvaNu.classList.add("buton-activ"); bTvaDa.classList.remove("buton-activ"); });
  }

  const bDa = corp.querySelector("#em-da"), bNu = corp.querySelector("#em-nu");
  const arataRaspuns = (da) => {
    corp.querySelector("#em-config-da").hidden = !da;
    corp.querySelector("#em-config-nu").hidden = da;
    bDa.classList.toggle("buton-activ", da);
    bNu.classList.toggle("buton-activ", !da);
    curataEroriCamp(zona);
    focusFaraSalt(corp.querySelector(da ? "#em-serie" : "#em-serie2"));
  };
  bDa.addEventListener("click", () => arataRaspuns(true));
  bNu.addEventListener("click", () => arataRaspuns(false));
  zona.querySelector("#em-salveaza-config").addEventListener("click", async () => {
    const serie = zona.querySelector("#em-serie").value.trim() || null;
    // [lotul 11, 440] toate câmpurile deodată, fiecare marcat lângă el (`cereCompletate` / `eroareCamp`), nu primul într-un <p> de mână
    curataEroriCamp(corp);
    let lipsa = cereCompletate(zona, [{ id: "em-serie", mesaj: "Completează seria: numărul facturii se dă într-o serie (CF art.319 alin.(20) lit.a)." }]);
    if (serie && /^\d+$/.test(serie)) lipsa = eroareCamp(zona, "em-serie", "Seria conține doar cifre. Seria e un prefix cu litere (ex: KAI- sau FCT-). Numărul ultimei facturi se pune în câmpul următor.") || lipsa;
    const ultim = parseInt((zona.querySelector("#em-ultim").value || "").trim(), 10);
    if (!Number.isFinite(ultim) || ultim < 1) lipsa = eroareCamp(zona, "em-ultim", "Completează numărul ultimei facturi emise (nu se poate presupune numărul 1).") || lipsa;
    const start = ultim + 1;   // #10: cerut explicit, nu fabricat
    if (platitorTva === null) lipsa = eroareCamp(corp, "em-tva-da", "Alege dacă firma e plătitoare de TVA.") || lipsa;
    if (lipsa) return;
    await salveazaConfig(tenantId, serie, start, tvaDinProfil ? null : platitorTva);
    if (opt.dupaSalvare) opt.dupaSalvare(); else randeazaEmitere(corp, nav, tenantId, opt);   // [pct.4] din „Schimbă seria”: înapoi la factură
  });

  zona.querySelector("#em-salveaza-config2").addEventListener("click", async () => {
    const serie = zona.querySelector("#em-serie2").value.trim() || null;
    curataEroriCamp(corp);   // [lotul 11, 440] toate deodată, lângă câmpuri
    let lipsa = cereCompletate(zona, [{ id: "em-serie2", mesaj: "Completează seria: numărul facturii se dă într-o serie (CF art.319 alin.(20) lit.a)." }]);
    if (serie && /^\d+$/.test(serie)) lipsa = eroareCamp(zona, "em-serie2", "Seria conține doar cifre. Seria e un prefix cu litere (ex: KAI- sau FCT-).") || lipsa;
    if (platitorTva === null) lipsa = eroareCamp(corp, "em-tva-da", "Alege dacă firma e plătitoare de TVA.") || lipsa;
    if (lipsa) return;
    await salveazaConfig(tenantId, serie, 1, tvaDinProfil ? null : platitorTva);
    if (opt.dupaSalvare) opt.dupaSalvare(); else randeazaEmitere(corp, nav, tenantId, opt);   // [pct.4] din „Schimbă seria”: înapoi la factură
  });
}

// [lotul 11, deficiența 428, retestul pe producție] „Configurare emitere nu arată sistemul”: arăta TVA la încasare numai dacă se aplica AZI,
// deci o perioadă care începe luna viitoare (opțiunea exercitată luna asta, CF art.282 alin.(3^1)) nu se vedea deloc. Acum: perioadele, în
// cuvintele serverului (`regim_tva_incasare.stare().text`), și dacă se aplică azi. Ce înseamnă pentru factura din formular o spune serverul,
// la data ei (`facturi/numerotare?data=` -> `tva_incasare`).
function textRegimIncasare(t) {
  if (!t) return "";
  if (t.text) return `, <b>TVA la încasare</b> ${esc(t.text)}${t.aplica_azi ? " — se aplică azi" : " — azi nu se aplică"}`;
  return t.fara_data ? ", aplică <b>TVA la încasare</b> (data de la care se aplică nu e scrisă în Date firmă)" : "";
}

async function salveazaConfig(tenantId, serie, numar_start, platitor_tva) {
  // [tva_config_v1] fara catch mut: esecul configurarii trebuie vazut (DS cap.6)
  await api.put(`/tenants/${tenantId}/facturi/numerotare`, { serie, numar_start });
  if (platitor_tva !== undefined && platitor_tva !== null)
    await api.post(`/tenants/${tenantId}/firma-profil/regim-tva`, { platitor_tva });
}

// ---------- „PLEACĂ MARFA ACUM?” ----------
// [punte_stoc_v1 → C63, decizia Costin 19.10.2026: „la transformarea în factură se pune aceeași întrebare ca la orice factură”] Caseta-
// poartă (DS cap.5 v2.14: `.caseta-poarta` > `.cp-mesaj` + `.cp-butoane`, două alegeri care merg amândouă înainte) pe care o pune serverul
// prin refuzul `INTREABA_PLEACA_MARFA`: aceeași întrebare, același text, la emiterea din formular și la „Transformă în factură” (detaliul
// proformei / avizului, `facturi_ecran.js`). `laRaspuns(true|false)` retrimite cu răspunsul; `ids` = id-urile celor două butoane.
export function intrebarePleacaMarfa(zona, nrArticole, laRaspuns, ids) {
  zona.innerHTML = `
    <div class="caseta-poarta">
      <div class="cp-mesaj">Pleacă marfa acum? ${cate(nrArticole, "articol", "articole")} de pe factură se descarcă din gestiune dacă marfa pleacă fizic azi. Dacă e avans, livrare ulterioară sau serviciu, alege „Nu, doar factură".</div>
      <div class="cp-butoane">
        <button class="buton-primar" id="${ids.da}">Da, pleacă marfa</button>
        <button class="buton-secundar em-buton-sec" id="${ids.nu}">Nu, doar factură</button>
      </div>
    </div>`;
  zona.querySelector("#" + ids.da).addEventListener("click", () => laRaspuns(true));
  zona.querySelector("#" + ids.nu).addEventListener("click", () => laRaspuns(false));
  aduInVedere(zona);
}

// ---------- COTA ȘI CATEGORIA LINIEI ----------
// [lotul 12, comanda 12.3 pct.9, cererea pachetului fe3] forma liniei — cota (lista cotelor în vigoare la plătitor, propunerea în titlu; cota
// fixă la neplătitor, CF art.310 alin.(10) lit.b) și categoria cotei 0% — o singură sursă, pentru „Emite factură” și șablonul recurent
export function clasaCotei(cota) {
  return cota == null ? "" : (cota === 11 ? " cota-11" : cota === 0 ? " cota-0" : " cota-21");
}
export function htmlCotaLinie(id, l, cote, platitor) {
  if (!platitor) return `<span class="em-l-cota${clasaCotei(l.cota_tva)}" id="${id}" title="Cota TVA">${l.cota_tva == null ? "—" : l.cota_tva + "%"}</span>`;
  return `<select class="camp-input em-l-cota-sel${clasaCotei(l.cota_tva)}" id="${id}" aria-label="Cota TVA" title="${l.cota_propusa == null ? "Cota TVA" : "Cota TVA — propusă: " + l.cota_propusa + "%"}">
             <option value=""${l.cota_tva == null ? " selected" : ""}>—</option>
             ${cote.map((c) => `<option value="${c}"${l.cota_tva === c ? " selected" : ""}>${c}%</option>`).join("")}
           </select>`;
}
// categoria de TVA a liniei cu cota 0% (la plătitor; lista vine de la server, `categorii_tva`), ascunsă cât cota nu e 0
export function htmlCategorieLinie(id, l, categ) {
  if (!categ.length) return "";
  return `<select class="camp-input em-l-categorie" id="${id}" aria-label="Categoria de TVA a liniei cu cota 0%"${l.cota_tva === 0 ? "" : " hidden"}>
             <option value="">— categoria de TVA (cota 0%) —</option>
             ${categ.map((c) => `<option value="${esc(c.cod)}"${l.categorie_tva === c.cod ? " selected" : ""}>${esc(c.eticheta)}</option>`).join("")}
           </select>`;
}

// ---------- „AI DOVADA TRANSPORTULUI?” ----------
// [lotul 12, C84, decizia Costin 12.3 pct.7: „livrarea intracomunitară de bunuri fără dovada transportului primește avertisment la emitere,
// nu refuz”] Caseta-poartă (DS cap.5 v2.14, ca „Pleacă marfa acum?”): serverul o cere prin `INTREABA_DOVADA_TRANSPORT`, după ce liniile au
// trecut; întrebarea e a serverului (`intrebare`, `intracomunitar.INTREBARE_DOVADA_TRANSPORT`). „Nu” emite factura, iar avertismentul
// (ce lipsește, ce se întâmplă cu scutirea) vine în răspunsul emiterii. Exportată, ca întrebarea mărfii, pentru „Transformă în factură”.
export function intrebareDovadaTransport(zona, intrebare, laRaspuns, ids) {
  zona.innerHTML = `
    <div class="caseta-poarta">
      <div class="cp-mesaj">${esc(intrebare || "")} Dacă nu o ai încă, factura se emite și îți spune ce lipsește.</div>
      <div class="cp-butoane">
        <button class="buton-primar" id="${ids.da}">Da, am dovada transportului</button>
        <button class="buton-secundar em-buton-sec" id="${ids.nu}">Nu încă, emite factura</button>
      </div>
    </div>`;
  zona.querySelector("#" + ids.da).addEventListener("click", () => laRaspuns(true));
  zona.querySelector("#" + ids.nu).addEventListener("click", () => laRaspuns(false));
  aduInVedere(zona);
}

// [lotul 12, C157 / C84] avertismentele emiterii (`avertismente` din răspuns: neplătitorul neînregistrat art.317, livrarea fără dovada
// transportului) sub confirmare, prin calea unică a mesajelor (DS cap.6, `arataMesaj(…, "avert")`) — factura e emisă, nu refuzată
// [lotul 13, C199 / 550 — decizia Costin, verbatim: „VIES indisponibil = avertisment și reîncercare, nu refuz (550).”] Factura s-a emis cu
// scutirea, iar VIES n-a răspuns: butonul reîncearcă verificarea codului clientului (aceeași rută ca „Verifică” de la client) și spune
// rezultatul — valid, invalid (livrarea nu e scutită: corecția prin stornare) sau din nou indisponibil.
function reverificaVies(zona, cod) {
  const b = document.createElement("button");
  b.type = "button"; b.className = "buton-secundar"; b.id = "em-vies-reincearca"; b.textContent = "Reîncearcă verificarea în VIES";
  b.dataset.actiune = "GET /tenants/{tenant_id}/verifica-vies";
  const rez = document.createElement("div"); rez.id = "em-vies-rez";
  zona.appendChild(b); zona.appendChild(rez);
  b.addEventListener("click", async () => {
    b.disabled = true;
    try {
      const v = await api.get(`/tenants/${zona.dataset.tenant}/verifica-vies?cod_tva=${encodeURIComponent(cod)}`);
      const st = v.stare || (v.valid ? "valid" : "indisponibil");
      if (st === "valid") arataMesaj(rez, `Codul ${cod} e valid în VIES${v.nume ? " (" + v.nume + ")" : ""}: scutirea livrării se păstrează.`, "ok");
      else if (st === "invalid") arataMesaj(rez, `Codul ${cod} e invalid în VIES: livrarea nu e scutită (Cod fiscal art.294 alin.(2) lit.a). Corectează factura prin stornare și emite-o cu TVA românesc.`, "eroare");
      else arataMesaj(rez, `VIES tot nu răspunde pentru ${cod}. Reîncearcă peste câteva minute.`, "avert");
    } catch (e) { arataMesaj(rez, (e && e.mesaj) || "VIES nu răspunde acum. Reîncearcă peste câteva minute.", "avert"); }
    b.disabled = false;
  });
}

// [lotul 13, 680] monedele facturii — aceeași listă la „Emite factură” și pe șablonul facturii recurente (situații identice, soluții identice)
export const MONEDE_FACTURA = [["RON", "RON (lei)"], ["EUR", "EUR"], ["USD", "USD"], ["GBP", "GBP"], ["CHF", "CHF"], ["HUF", "HUF"], ["PLN", "PLN"]];
export function optiuniMoneda(aleasa) {
  return MONEDE_FACTURA.map(([v, t]) => `<option value="${v}"${v === aleasa ? " selected" : ""}>${t}</option>`).join("");
}

export function arataAvertismenteEmitere(zona, avertismente) {
  (avertismente || []).forEach((a) => {
    const z = document.createElement("div");
    z.className = "em-avertisment-emitere";
    zona.appendChild(z);
    arataMesaj(z, a, "avert");
  });
}

// [punte_stoc_v1 → C63] ce s-a descărcat din gestiune la „Da, pleacă marfa” (gol fără descărcare) — același text la emitere și la transformare
export function textDescarcare(d) {
  if (!d) return "";
  const nd = (d.descarcate || []).length, ne = (d.erori || []).length;
  return ` · ${cate(nd, "articol descărcat", "articole descărcate")} din gestiune` + (ne ? ` (${ne} nu — stoc insuficient)` : "");
}

// [lotul 11, deficiența 428] ce s-a întâmplat cu TVA-ul unei facturi emise în sistemul TVA la încasare, din contarea ei (`contare_facturi.
// contabilizeaza`: `regim_tva_incasare`) — același text la emitere, la transformarea proformei / avizului și la stornare (gol pe regulile
// generale). Temei: CF art.282 alin.(3) (exigibil la încasare), alin.(10) (stornarea anulează întâi TVA-ul rămas neexigibil).
export function textTvaIncasare(contare) {
  const rg = contare && contare.regim_tva_incasare;
  if (rg === "incasare") return " · TVA la încasare: TVA-ul e pe 4428 și devine exigibil la încasare; factura poartă mențiunea „TVA la încasare”";
  if (rg === "storno_incasare") return " · TVA la încasare: stornarea anulează întâi TVA-ul rămas neexigibil pe factura stornată (4428), restul e exigibil la data stornării";
  return "";
}

// [lotul 11, decizia Costin 10.3: „Rotunjirea TVA: o singură regulă pe toată aplicația, cea cerută de validatorul e-Factura.”] Oglinda
// EXACTĂ (aritmetică pe întregi, fără virgulă mobilă) a regulii din `core/tva_calcul.py` (EN 16931): valoarea netă a liniei la ban
// (BR-DEC-23), baza pe cotă = suma lor (BR-S-08), TVA-ul pe cotă = baza × cotă / 100 rotunjit o dată, jumătatea în sus (BR-CO-17), TVA-ul
// total = suma pe cote (BR-CO-14). Ecranul arată ce va scrie serverul; paritatea cu Python: `core/test_lot11_t_tva_unica.py` (Node).
// Întoarce {pe_cote: {cota: {baza, tva}}, baza, tva} în lei (numere cu 2 zecimale).
// BigInt(...) și nu literalele `1n`: analizorul JS al gărzilor (acorn -> JSON, `core/arbore_js.py`) nu serializează un literal BigInt
const _BI = BigInt, _ZECE = BigInt("10");   // baza zecimală (din text: nu e o cotă)
function _zec(x) {   // număr / text -> [întreg BigInt, zecimale]
  let s = String(x == null || x === "" ? 0 : x).trim();
  if (/e/i.test(s)) s = Number(s).toFixed(10);
  const neg = s.startsWith("-"); if (neg) s = s.slice(1);
  const [i, f = ""] = s.split(".");
  return [(neg ? _BI(-1) : _BI(1)) * _BI((i || "0") + f), f.length];
}
function _laBan(n, z) {   // n / 10^z -> bani (BigInt), jumătatea departe de zero (ROUND_HALF_UP pe valoarea absolută)
  if (z <= 2) return n * _ZECE ** _BI(2 - z);
  const d = _ZECE ** _BI(z - 2), a = n < _BI(0) ? -n : n, r = (a + d / _BI(2)) / d;
  return n < _BI(0) ? -r : r;
}
export function tvaDocument(linii) {
  const baze = new Map();
  (linii || []).forEach((l) => {
    if (!l) return;
    const [c, zc] = _zec(l.cantitate), [p, zp] = _zec(l.pret_unitar);
    const net = _laBan(c * p, zc + zp);
    const cota = Number(l.cota_tva || 0);
    baze.set(cota, (baze.get(cota) || _BI(0)) + net);
  });
  const pe_cote = {};
  let baza = _BI(0), tva = _BI(0);
  baze.forEach((b, cota) => {
    const [k, zk] = _zec(cota);
    const t = _laBan(b * k, zk + 4);   // (bani / 100) × (cotă / 100) lei -> bani
    pe_cote[cota] = { baza: Number(b) / 100, tva: Number(t) / 100 };
    baza += b; tva += t;
  });
  return { pe_cote, baza: Number(baza) / 100, tva: Number(tva) / 100 };
}

// ---------- CIORNA FACTURII ----------
// [lotul 07.10 pct.2, comanda Costin 06.10.2026 — GRAV, factura pierdută a treia oară] „O factură începută rămâne păstrată
// oricum ar naviga contabilul în aplicație, până o emite sau o abandonează explicit.” Ce s-a scris e o CIORNĂ a utilizatorului pe
// firmă: scrisă la fiecare modificare, citită la deschiderea formularului, ștearsă NUMAI la emitere, la „Renunță la factură” sau
// când omul golește formularul.
// [deficiența 495, lotul 12] „Ciorna facturii e salvată doar în browser; pe alt calculator nu se regăsește.” Locul ciornei e acum
// SERVERUL (`core/ciorne_formular.py`, pe utilizator + firmă). Browserul ține doar copia NETRIMISĂ: fiecare modificare se scrie întâi
// aici (o reîncărcare imediată nu pierde ultima tastă), apoi pleacă la server; după ce serverul a primit-o, copia locală se șterge.
// La deschidere (`incarcaCiorna`), o copie rămasă în browser — netrimisă, sau ciorna veche de dinainte de 495 — se urcă întâi pe
// server și e cea refăcută; altfel se reface ciorna de pe server (scrisă de pe orice calculator).
// Gard: `core/test_lot0710_ui.py` (drumurile de ștergere, cheia pe utilizator + firmă), `core/test_lot12_emit_ciorna.py`.
function cheieCiorna(tenantId) {
  const u = sesiune.user();
  return `iconta_ciorna_factura:${u && u.id != null ? u.id : "anonim"}:${tenantId}`;
}
// [495] transportul ciornei spre server e cel comun al ciornelor de formular (`ciorna_formular.js`, `ciornaPeServer`): copia netrimisă
// în browser, trimisă după o pauză de tastare, ștearsă din browser după ce serverul a primit-o; cererile pleacă pe rând
const _transport = (tenantId) => ciornaPeServer(cheieCiorna(tenantId), `/tenants/${tenantId}/ciorne-formular/factura`);
const _ciorne = {};          // tenantId -> ciorna citită la deschidere (`incarcaCiorna`) și ținută la zi de `scrieCiorna`
// La deschiderea formularului: ciorna serverului (scrisă de pe orice calculator); copia netrimisă din browser, dacă e mai nouă (sau
// serverul n-are nimic — ciorna veche, de dinainte de 495), urcă pe server și e ea cea refăcută. Una mai veche decât a serverului
// (lăsată pe calculatorul ăsta, între timp continuată pe altul) se aruncă: rămâne factura continuată.
export async function incarcaCiorna(tenantId) {
  _ciorne[tenantId] = await _transport(tenantId).incarca();
  return _ciorne[tenantId];
}
export function citesteCiorna(tenantId) {
  return _ciorne[tenantId] || null;
}
function scrieCiorna(tenantId, c) {
  _ciorne[tenantId] = c;
  _transport(tenantId).scrie(c);
}
export function stergeCiorna(tenantId) {
  const t = _transport(tenantId);
  const exista = _ciorne[tenantId] != null;   // formularul gol, tastat din nou: nicio cerere la server
  _ciorne[tenantId] = null;
  t.sterge(exista);
}

// [deficiența 488, lotul 12] „lista de articole fără căutare, greu de folosit la sute de articole”. Căutarea într-o listă derulantă:
// la fiecare tastă în `intrare`, lista păstrează numai opțiunile care conțin textul (în eticheta lor sau în `data-cauta`, ex. codul de
// bare), fără diacritice și majuscule; opțiunea goală („— fără articol —”, „— alege —”) și cea deja aleasă rămân mereu, deci căutarea nu
// schimbă alegerea. Nimic potrivit: o linie inactivă spune asta. Generică — orice listă lungă a aplicației o poate primi.
function _faraDiacritice(t) {
  return String(t || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
}
export function cautaInLista(intrare, lista) {
  const toate = [...lista.options].map((o) => ({ html: o.outerHTML, valoare: o.value,
    text: _faraDiacritice(o.textContent + " " + (o.dataset.cauta || "")) }));
  intrare.addEventListener("input", () => {
    const q = _faraDiacritice(intrare.value), ales = lista.value;
    const pastrate = toate.filter((o) => o.valoare === "" || o.valoare === ales || !q || o.text.includes(q));
    const nimic = q && !pastrate.some((o) => o.valoare !== "" && o.valoare !== ales)
      ? `<option value="" disabled>Nimic din listă nu conține „${esc(intrare.value.trim())}”</option>` : "";
    const goale = pastrate.filter((o) => o.valoare === "").map((o) => o.html).join("");
    lista.innerHTML = goale + nimic + pastrate.filter((o) => o.valoare !== "").map((o) => o.html).join("");
    lista.value = ales;
  });
}

// ---------- FORMULAR EMITERE ----------
function formularEmitere(corp, nav, tenantId, num, opt) {
  if (nav && nav.setInapoi) nav.setInapoi(opt.inapoi || undefined);  // emitere_inapoi_v1
  // [lotul 07.10 B, DS cap.17 corectat] PRESELECȚIE PERMISĂ: moneda RON e cazul uzual, se vede înainte de emitere și se schimbă
  let monedaSel = "RON";
  // [B1 D300] Tara partenerului decide ruta in generator (RO->intern, UE->livrare IC/taxare inversa, non-UE->export): lista țărilor și
  // deducerea din CUI stau în `tari_partener.js` (sursa unică, și pentru șablonul facturii recurente — lotul 12, C160)
  // [C61, decizia Costin 19.10.2026 „Da, câmpuri și la român”] județul clientului român: codul (ISO 3166-2:RO, ca `dcod_JudetAuto` din
  // ANAF și `efactura_send._JUD`), afișat cu numele; aceeași listă ca `factura_pdf.JUDETE_NUME` (paritatea: core/test_c61_adresa_client_ro.py)
  const JUDETE_RO = [["AB","Alba"],["AR","Arad"],["AG","Argeș"],["BC","Bacău"],["BH","Bihor"],["BN","Bistrița-Năsăud"],["BT","Botoșani"],
    ["BV","Brașov"],["BR","Brăila"],["BZ","Buzău"],["CS","Caraș-Severin"],["CL","Călărași"],["CJ","Cluj"],["CT","Constanța"],["CV","Covasna"],
    ["DB","Dâmbovița"],["DJ","Dolj"],["GL","Galați"],["GR","Giurgiu"],["GJ","Gorj"],["HR","Harghita"],["HD","Hunedoara"],["IL","Ialomița"],
    ["IS","Iași"],["IF","Ilfov"],["MM","Maramureș"],["MH","Mehedinți"],["MS","Mureș"],["NT","Neamț"],["OT","Olt"],["PH","Prahova"],
    ["SM","Satu Mare"],["SJ","Sălaj"],["SB","Sibiu"],["SV","Suceava"],["TR","Teleorman"],["TM","Timiș"],["TL","Tulcea"],["VS","Vaslui"],
    ["VL","Vâlcea"],["VN","Vrancea"],["B","București"]];
  // [lotul 07.10 B, DS cap.17 corectat] țara se DEDUCE din CUI-ul partenerului (`taraDinCui`), vizibil și modificabil; fără prefix = RO
  // [274b] categoria de TVA a liniei cu 0% (core/categorii_tva, de la server): obligatorie la plătitor; la neplătitor e „O”, automat
  const CATEG = num.categorii_tva || [];
  const C331 = num.categorii_331 || [];
  const optiuniTara = _optiuniTara();
  const inapoi = opt.inapoi || (() => nav.inapoi());
  const numarProxim = numarCuSerie(num.serie, String(num.urmator_numar));   // [lotul 11, 443] „F6 nr. 1”, nu „F61”

  corp.innerHTML = `

    <div class="em-ciorna" id="em-ciorna" role="note"></div>
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
      <p class="camp-ajutor" id="em-scadenta-ajutor">${num.scadenta_zile ? `Propusă la ${cate(num.scadenta_zile, "zi", "zile")} de la emitere — termenul din lege când contractul nu prevede altul (${esc(num.scadenta_temei || "")}). O poți schimba; ` : ""}scadența intră în scadențar; o factură fără scadență nu are termen de plată urmărit.</p>
      <div class="caseta-info" id="em-tva-incasare" role="note" hidden><div class="ci-mesaj"></div></div>
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
      <div class="camp-eticheta">Linie: denumire · cantitate · preț unitar <span class="oblig">*</span> <span class="tip-micut">${opt.tvaProfil === false ? "(firma nu e plătitoare de TVA: liniile nu poartă TVA — regim special de scutire, art. 310 Cod fiscal)" : "(la un articol din stoc, cota TVA vine din articol; la o linie fără articol, cota e propusă pe baza denumirii — verifică încadrarea și schimb-o din listă dacă e altfel; răspunderea corectitudinii cotei îți aparține, iar schimbarea se consemnează)"}</span></div>
      <div class="em-linie-antet" aria-hidden="true"><span>Denumire</span><span class="ant-cant">Cant.</span><span class="ant-um">UM</span><span class="ant-pret">Preț</span><span class="ant-cota">Cotă</span><span></span></div>
      <div class="em-linii" id="em-linii"></div>
      <button class="buton-secundar em-buton-sec" id="em-add-linie" data-fara-actiune="rând în formular; salvarea formularului poartă acțiunea">+ Adaugă linie</button>
    </div>

    <div class="em-total" id="em-total"></div>
    <div class="em-moneda-rand">
      <label class="em-moneda-eticheta" for="em-moneda">Monedă</label>
      <select class="camp-input" id="em-moneda" data-actiune-camp="POST /tenants/{tenant_id}/facturi/previzualizare-lei">
        ${optiuniMoneda("RON")}
      </select>
      <span class="em-moneda-nota" id="em-moneda-nota"></span>
    </div>
    <div class="fd-valuta" id="em-valuta" aria-live="polite" hidden></div>
    <div class="em-sectiune">
      <div class="em-eticheta">Clasificare TVA (D300)</div>
      <label class="camp-eticheta" for="em-tara">Țara partenerului</label>
      <select class="camp-input" id="em-tara">${optiuniTara}</select>
      <label class="camp-eticheta" for="em-oras" id="em-oras-et">Localitatea clientului</label>
      <input class="camp-input" id="em-oras" type="text" maxlength="100">
      <label class="camp-eticheta em-ro" for="em-judet">Județul clientului</label>
      <select class="camp-input em-ro" id="em-judet"><option value="">— alege —</option>${JUDETE_RO.map(([c, n]) => `<option value="${c}">${esc(n)}</option>`).join("")}</select>
      <label class="camp-eticheta em-strain" for="em-regiune" hidden>Regiunea clientului (provincie, land, comitat)</label>
      <input class="camp-input em-strain" id="em-regiune" type="text" maxlength="100" hidden>
      <label class="camp-eticheta" for="em-c331" id="em-c331-et" hidden>Categoria produsului cu taxare inversă (art.331; codul din D394)</label>
      <select class="camp-input" id="em-c331" hidden><option value="">— alege —</option>${C331.map((c) => `<option value="${esc(c.cod)}">${esc(c.eticheta)}</option>`).join("")}</select>
      <label class="camp-eticheta" for="em-tipop">Tip operațiune</label>
      <select class="camp-input" id="em-tipop" data-butoane="">
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
    <div class="bara-fixa"><div class="em-rezultat" id="em-rezultat"></div><div class="em-actiuni">
      <select id="em-tip" class="camp-input" aria-label="Tipul documentului emis" style="max-width:180px;margin-right:8px" data-butoane="">
        <option value="factura" selected>Factură</option>
        <option value="proforma">Proforma</option>
        <option value="aviz">Aviz de însoțire</option>
      </select>
      <button class="buton-primar em-emite" id="em-emite" data-actiune="POST /tenants/{tenant_id}/facturi/emite">Emite factură</button>
      <button class="buton-secundar" id="em-renunta" data-fara-actiune="ciorna e a celui care o scrie: oricine vede formularul poate renunța la ciorna lui, fără un drept anume" style="margin-left:8px">Renunță la factură</button>
    </div></div>`;

  // [comanda Costin 05.10.2026 pct.2] „Datele firmei care blochează emiterea se verifică la deschiderea «Emite factură», nu după
  // completarea întregului formular.” Lipsurile vin de la server (aceeași regulă ca refuzul emiterii, `capital_social.lipsa`).
  // „Emite” rămâne inactiv cu motivul vizibil; la revenirea din Date firmă (`nav:revenire`) se reverifică.
  const zonaPreg = corp.querySelector("#em-pregatire");
  const btnEmite = corp.querySelector("#em-emite");
  function aratăPregatirea(n) {
    const lipsuri = (n && n.lipsuri_firma) || [];
    if (!lipsuri.length) { zonaPreg.innerHTML = ""; btnEmite.disabled = false; btnEmite.title = ""; return; }
    zonaPreg.innerHTML = `<div class="caseta-atentie"><div class="ca-mesaj pe-randuri">${esc(n.mesaj_lipsuri || "")}</div></div>
      <div class="ca-actiuni" id="em-pregatire-actiuni"></div>`;
    btnEmite.disabled = true;
    btnEmite.title = "Completează întâi în Date firmă: " + lipsuri.join(", ");
    butonSpreEcran(zonaPreg.querySelector("#em-pregatire-actiuni"), "date_firma", nav, tenantId,
      { id: "em-date-firma-sus", clasa: "buton-secundar", inapoiLa: "factură", camp: n.camp_ecran || null });
  }
  function aratăNumarul(n) {
    const sn = corp.querySelector("#em-serie-nr"), nr = corp.querySelector("#em-numar");
    if (sn) sn.textContent = (n.serie ? n.serie + " · " : "fără serie (se cere la emitere) · ") + "următorul număr: " + n.urmator_numar;
    if (nr) nr.innerHTML = (n.serie ? `Seria <b>${esc(n.serie)}</b> · ` : "") + `nr. <b>${esc(String(n.urmator_numar))}</b>`;
  }
  // [lotul 11, deficiența 428] sistemul TVA la încasare LA DATA FACTURII, în cuvintele serverului (`tva_incasare.text_regim_emitere`):
  // TVA pe 4428 cu mențiunea „TVA la încasare”, sau — înaintea intrării / după ieșire — TVA la emitere (CF art.282 alin.(3), (7))
  function aratăRegimulTva(n) {
    const z = corp.querySelector("#em-tva-incasare");
    const t = n && n.tva_incasare;
    z.hidden = !t;
    z.querySelector(".ci-mesaj").textContent = t ? t.mesaj : "";
  }
  aratăPregatirea(num);
  aratăRegimulTva(num);
  // reîncarcă ce depinde de Date firmă și de DATA facturii: lipsurile, numerotarea, cotele permise la data aleasă
  const cererePregatire = ultimaCerere();   // [C103] data facturii schimbată în șir: numai numerotarea și cotele ultimei date ajung pe ecran
  async function reincarcaPregatirea() {
    const actuala = cererePregatire();
    const data = (corp.querySelector("#em-data") || {}).value || dataIso();
    try {
      const n = await api.get(`/tenants/${tenantId}/facturi/numerotare?data=${encodeURIComponent(data)}`);
      if (!actuala()) return;
      aratăPregatirea(n); aratăNumarul(n); aratăRegimulTva(n);
      const cote = (n.cote_permise && n.cote_permise.length) ? n.cote_permise : [];
      // altă perioadă de cote -> lista pe fiecare linie; [C103] cantitatea / prețul scrise între timp pe o linie nu se pierd
      if (cote.join(",") !== COTE.join(",")) { COTE = cote; pastreazaCampulActiv(corp, deseneazaLinii); }
    } catch { if (!actuala()) return; /* rămâne starea de dinainte */ }
  }
  corp.addEventListener("nav:revenire", reincarcaPregatirea);
  corp.querySelector("#em-data").addEventListener("change", reincarcaPregatirea);
  // [lotul 07.10 pct.18] scadența PROPUSĂ = data emiterii + termenul legal (serverul dă zilele și temeiul, Legea 72/2013
  // art.3 alin.(3) lit.a); urmărește data emiterii până când omul o schimbă — de atunci rămâne a lui.
  const inScad = corp.querySelector("#em-scadenta");
  let scadentaScrisa = false;
  function propuneScadenta() {
    if (scadentaScrisa || !num.scadenta_zile) return;
    const d = (corp.querySelector("#em-data") || {}).value;
    if (!d) return;
    const t = new Date(d + "T00:00:00");
    t.setDate(t.getDate() + Number(num.scadenta_zile));
    inScad.value = `${t.getFullYear()}-${String(t.getMonth() + 1).padStart(2, "0")}-${String(t.getDate()).padStart(2, "0")}`;
  }
  inScad.addEventListener("input", () => { scadentaScrisa = true; });
  inScad.addEventListener("change", () => { scadentaScrisa = true; });
  corp.querySelector("#em-data").addEventListener("change", propuneScadenta);
  corp.querySelector("#em-data").addEventListener("change", () => recalc());   // [lotul 10, 7g] altă dată a facturii, alt curs BNR
  propuneScadenta();
  // [comanda Costin 05.10.2026 pct.4] seria se vede și se poate stabili: configurarea numerotării, într-o fereastră PESTE factură
  corp.querySelector("#em-schimba-serie").addEventListener("click", () =>
    nav.deschide("Numerotare facturi", (c2) => configureazaNumerotare(c2, nav, tenantId,
      Object.assign({}, opt, { dupaSalvare: () => nav.inapoi() }), opt.tvaProfil, opt.tvaIncasare)));

  const zonaLinii = corp.querySelector("#em-linii");
  const linii = [];
  const articole = opt.articole || [];        // [punte_stoc_v1] F172: articole de stoc (gol la gratuit)
  let pleacaMarfaCurent = null;               // raspunsul la poarta "pleaca marfa acum?" pt emiterea curenta
  let semnMarfa = null;                       // [lotul 07.10 pct.17] articolele pentru care s-a dat răspunsul
  let dovadaTransportCurent = null;           // [lotul 12, C84] răspunsul la „Ai dovada transportului?” (livrarea intracomunitară)
  let semnDovada = null;                      // liniile de livrare intracomunitară pentru care s-a dat răspunsul

  const UM_SERVICIU = "serv.";   // [331] cod E48 în e-Factura și D406 (`efactura_send._UM`, `d406.UOM_UNECE`)
  const linieNoua = () => ({ descriere: "", cantitate: "", um: "buc", pret_unitar: "", cota_tva: null, cota_propusa: null, articol_id: null,
    categorie_tva: null });
  // [comanda Costin 05.10.2026 pct.3] „contabilul poate corecta cota; schimbarea rămâne consemnată (propus → ales, cine, când)”.
  // Cotele oferite = cele permise la data facturii, de la server (aceeași sursă ca validarea emiterii).
  let COTE = (num.cote_permise && num.cote_permise.length) ? num.cote_permise : [];   // se reîncarcă la schimbarea datei
  const platitor = opt.tvaProfil !== false;
  const _val = (x) => (x === "" || x == null) ? "" : esc(String(x));

  // randeaza O linie DIN MODEL (id-uri pozitionale em-l{i}-*, ca backendul sa lege eroarea de camp). Stergere/rand.
  function randLinie(i) {
    const l = linii[i];
    const inputsHtml = `
      <input class="camp-input em-l-den" id="em-l${i}-descriere" data-actiune-camp="POST /tenants/{tenant_id}/produse/potriveste" value="${_val(l.descriere)}" placeholder="Denumire (ex: pâine, consultanță)" aria-label="Denumire articol" autocomplete="off">
      <input class="camp-input em-l-cant" id="em-l${i}-cantitate" type="number" step="0.001" value="${_val(l.cantitate)}" placeholder="Cant." aria-label="Cantitate" title="Cantitate">
      <input class="camp-input em-l-um" id="em-l${i}-um" maxlength="10" value="${_val(l.um)}" aria-label="Unitate de măsură" title="Unitate de măsură">
      <input class="camp-input em-l-pret" id="em-l${i}-pret_unitar" type="number" step="0.01" value="${_val(l.pret_unitar)}" placeholder="Preț" aria-label="Preț unitar" title="Preț unitar">
      ${htmlCotaLinie("em-l" + i + "-cota", l, COTE, platitor)}
      <button type="button" class="buton-sters em-l-sterge" data-idx="${i}" title="Șterge">×</button>
      ${platitor ? htmlCategorieLinie("em-l" + i + "-categorie", l, CATEG) : ""}`;
    if (articole.length) {
      // [deficiența 488, lotul 12] deasupra listei, căutarea după denumire sau cod de bare (`cautaInLista`); alegerea rămâne a omului
      const selArticol = `
        <input type="text" class="camp-input em-l-cauta-articol" id="em-l${i}-cauta-articol" aria-label="Caută articolul în stoc" placeholder="Caută articolul în stoc (denumire sau cod de bare)…" autocomplete="off" style="margin-bottom:4px">
        <select class="camp-input em-l-articol" id="em-l${i}-articol" aria-label="Articol de stoc" style="margin-bottom:6px">
          <option value="">— fără articol (serviciu) —</option>
          ${articole.map((a) => `<option value="${a.id}"${String(a.id) === String(l.articol_id) ? " selected" : ""} data-den="${esc(a.denumire)}" data-um="${esc(a.um || "")}" data-cauta="${esc(a.barcode || "")}">${esc(a.denumire)} · stoc ${esc(cantitate(a.stoc, a.um))}</option>`).join("")}
        </select>`;
      // [05.10.2026, comanda Costin pct.9] pe o firmă cu stoc, linia fără articol spune că marfa nu se descarcă din gestiune
      // [lotul 07.10 B, C12b] o atenționare, nu o eroare: casetă informativă (DS cap.5 — roșul rămâne pentru ce blochează)
      const faraArt = `<div class="caseta-info em-l-fara-articol" id="em-l${i}-fara-articol"${(l.descriere && !l.articol_id) ? "" : " hidden"}><span class="ci-mesaj">Linie fără articol de stoc: marfa de pe ea nu se descarcă din gestiune. Dacă e marfă, alege articolul; dacă e serviciu, lasă așa.</span></div>`;
      return `<div class="em-linie-wrap" data-idx="${i}">${selArticol}<div class="em-linie">${inputsHtml}</div>${faraArt}<div class="em-l-cota-mesaj" id="em-l${i}-cota-mesaj"></div></div>`;
    }
    return `<div class="em-linie" data-idx="${i}">${inputsHtml}</div>`;
  }

  // [deficiența 326, 18.10.2026] clientul din alt stat UE, cu codul de TVA VALID în VIES (verificat pe ecran): o linie de SERVICIU are
  // locul prestării la client (CF art.278 alin.(2)) — se propune cota 0 cu categoria „serviciu_extern”, nu 21%. Numai propunere, pe
  // liniile la care omul n-a ales el cota; schimbarea clientului (alt CUI / altă țară) o retrage.
  let viesValid = null;   // țara (codul VIES) pentru care codul de TVA al clientului a ieșit valid
  const clientUeVies = () => !!viesValid && corp.querySelector("#em-tara").value === viesValid && viesValid !== "RO";
  function propuneServiciuExtern(l) {
    if (!platitor || l.tipLinie !== "servicii" || l.cotaAleasa) return;
    const p = linii.indexOf(l);
    if (clientUeVies()) {
      l.cota_tva = 0; l.cota_propusa = 0; l.categorie_tva = "serviciu_extern"; l.categoriePropusa = true;
      setCota(l, "0%", 0);
      const sc = zonaLinii.querySelector("#em-l" + p + "-categorie");
      if (sc) { sc.hidden = false; sc.value = "serviciu_extern"; }
      actualizeazaC331();
    } else if (l.categoriePropusa) {   // clientul nu mai e UE valid: propunerea se retrage la cota denumirii
      l.categoriePropusa = false; l.categorie_tva = null;
      l.cota_tva = l.cotaDenumire == null ? null : l.cotaDenumire; l.cota_propusa = l.cota_tva;
      setCota(l, l.cota_tva == null ? "—" : `${l.cota_tva}%`, l.cota_tva);
    }
  }
  const repropuneLiniile = () => { linii.forEach(propuneServiciuExtern); recalc(); };

  // actualizeaza afisajul cotei pt OBIECTUL l la pozitia lui CURENTA (splice-safe cu fetch-ul async in zbor)
  function setCota(l, text, cota) {
    const p = linii.indexOf(l);
    if (p < 0) return;
    aratăCategoria(l);   // [274b] orice cotă stabilită (aleasă, propusă, golită) decide dacă se cere categoria
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

  // [274b] categoria se cere numai pe linia cu 0%; o cotă schimbată de pe 0% o golește. Categoria produsului (art.331) se cere cât timp
  // o linie e cu taxare inversă.
  function aratăCategoria(l) {
    const p = linii.indexOf(l);
    const sc = p < 0 ? null : zonaLinii.querySelector("#em-l" + p + "-categorie");
    if (sc) {
      sc.hidden = l.cota_tva !== 0;
      if (l.cota_tva !== 0) { sc.value = ""; l.categorie_tva = null; }
    }
    actualizeazaC331();
  }
  function actualizeazaC331() {
    const are = linii.some((x) => x.categorie_tva === "taxare_inversa");
    ["#em-c331", "#em-c331-et"].forEach((s) => { const e = corp.querySelector(s); if (e) e.hidden = !are; });
  }

  // [pct.1b] ce a venit din PROPUNERE (prețul de vânzare din nomenclator, UM-ul articolului) nu e ales de om: când denumirea se
  // schimbă, propunerea nu mai e a liniei și se golește. Ce a scris omul (`pretPropus` / `umPropus` false) rămâne neatins.
  function golestePropunerea(l, pret, um) {
    if (l.pretPropus) { l.pret_unitar = ""; l.pretPropus = false; if (pret) pret.value = ""; }
    if (l.umPropus) { l.um = "buc"; l.umScris = false; l.umPropus = false; if (um) um.value = "buc"; }
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
    const cerereCota = ultimaCerere();   // [C103] denumirea scrisă în reprize: numai propunerea pentru ultima denumire ajunge pe linie
    den.addEventListener("input", () => {
      l.descriere = den.value.trim();
      // [comanda Costin 06.10.2026 pct.1c] denumirea scrisă de mână, diferită de articolul ales, DEZLEAGĂ linia de articol: altfel
      // „Carte – Ghid contabil 2026” pleca la emitere cu articolul „Marfa A” și se descărca din stocul lui (măsurat: articol_id
      // păstrat în cererea de emitere). Alegerea din listă scrie ea însăși denumirea articolului — aceea nu dezleagă.
      if (l.articol_id && selArt) {
        const o = selArt.selectedOptions[0];
        if (!o || (o.dataset.den || "").trim() !== l.descriere) { l.articol_id = null; selArt.value = ""; }
      }
      // [pct.1b] „Un preț pe care nu l-a ales nimeni nu se propune.” Prețul și UM-ul venite din propunere (articolul ales /
      // nomenclatorul) erau ale denumirii vechi: se golesc; propunerea denumirii noi (dacă are una) le pune la loc.
      golestePropunerea(l, pret, um);
      aratăFaraArticol();
      l.cota_tva = null;  // reset -> se repotriveste
      l.cotaAleasa = false; l.categoriePropusa = false; l.tipLinie = null; l.categorie_tva = null;   // [326] denumire nouă, propunere nouă
      clearTimeout(timer);
      const actuala = cerereCota();   // și o denumire scurtă / neplătitorul (fără cerere) opresc propunerea cerută înainte
      const d = l.descriere;
      if (d.length < 3) { setCota(l, "—"); recalc(); return; }
      // [lot 19 pct.4d] neplatitor: cota e 0 prin lege, nu o propunere — fara apel de potrivire (care ar fi dat 21)
      if (opt.tvaProfil === false) { l.cota_tva = 0; setCota(l, "0%", 0); recalc(); return; }
      setCota(l, "…");
      const zCota = zonaLinii.querySelector("#em-l" + linii.indexOf(l) + "-cota-mesaj");
      if (zCota) zCota.innerHTML = "";
      timer = setTimeout(async () => {
        try {
          const r = await api.post(`/tenants/${tenantId}/produse/potriveste`, { denumire: d, articol: !!l.articol_id });
          if (!actuala()) return;
          if (r && !r.ok && r.cod === "ARTICOL_FARA_COTA") {   // [274a] articolul de stoc fără cotă în nomenclator: se spune, cu drumul spre Produse
            const z = zonaLinii.querySelector("#em-l" + linii.indexOf(l) + "-cota-mesaj");
            if (z) {
              z.innerHTML = `<div class="caseta-atentie"><div class="ca-mesaj pe-randuri">${esc(r.mesaj)}</div></div>`;
              butonSpreEcran(z.querySelector(".caseta-atentie"), r.ecran, nav, tenantId, { clasa: "buton-secundar", inapoiLa: "factură" });
            }
            setCota(l, "—");
          } else if (r && r.ok) {
            // [lotul 12, C189] propunerea sosită DUPĂ ce omul a ales cota pe linie nu i-o mai înlocuiește: rămâne numai ca propunere
            // (titlul listei, jurnalul „propus → ales”, comanda Costin 05.10.2026 pct.3)
            l.cota_propusa = r.cota;
            if (l.cotaAleasa) { setCota(l, "", l.cota_tva); recalc(); return; }
            l.cota_tva = r.cota; l.cota_propusa = r.cota; l.cotaDenumire = r.cota; l.tipLinie = r.tip || null;
            setCota(l, r.cota === 0 ? "0%" : `${r.cota}%`, r.cota);
            // [05.10.2026, comanda Costin pct.9] din nomenclator: prețul și UM, numai unde omul n-a scris deja altceva
            const p = linii.indexOf(l);
            // [lotul 11, 449, patch B/P5] la cota 0 din nomenclator, categoria de TVA a produsului (și bunul cu taxare inversă) se propune
            if (r.cota === 0 && r.categorie_tva && !l.cotaAleasa) {
              l.categorie_tva = r.categorie_tva; l.categoriePropusa = true;
              const sc2 = zonaLinii.querySelector("#em-l" + p + "-categorie");
              if (sc2) { sc2.hidden = false; sc2.value = r.categorie_tva; }
              const c3 = corp.querySelector("#em-c331");
              if (r.categorie_331 && c3 && !c3.value) c3.value = r.categorie_331;
              actualizeazaC331();
            }
            if (r.um && !l.umScris) { l.um = r.um; l.umPropus = true; const e = zonaLinii.querySelector("#em-l" + p + "-um"); if (e) e.value = r.um; }
            if (r.pret_unitar && (l.pret_unitar === "" || l.pret_unitar == null)) {   // prețul de vânzare din nomenclator: propunere
              l.pret_unitar = r.pret_unitar; l.pretPropus = true;
              const e = zonaLinii.querySelector("#em-l" + p + "-pret_unitar"); if (e) e.value = r.pret_unitar;
            }
            // [331, 18.10.2026] serviciul nu e „buc”: UM propus „serv.” (E48, „service unit”, UN/ECE Rec.20 — acceptat de validatorul
            // e-Factura ANAF și în lista D406), numai unde omul n-a scris altceva și nomenclatorul n-a dat UM
            if (l.tipLinie === "servicii" && !r.um && !l.umScris) {
              l.um = UM_SERVICIU; l.umPropus = true; const e = zonaLinii.querySelector("#em-l" + p + "-um"); if (e) e.value = UM_SERVICIU;
            }
            propuneServiciuExtern(l);   // [326]
          }
        } catch { if (!actuala()) return; }
        recalc();
      }, 550);
    });
    const selCota = zonaLinii.querySelector("select#em-l" + i + "-cota");
    if (selCota) selCota.addEventListener("change", () => {   // [pct.3] contabilul alege; propunerea rămâne pentru jurnal
      l.cota_tva = selCota.value === "" ? null : Number(selCota.value);
      l.cotaAleasa = true; l.categoriePropusa = false;   // [326] alegerea omului nu mai e înlocuită de propunere
      setCota(l, "", l.cota_tva);
      // [lotul 10, 10.2 pct.7d, deficiența 415] „mesajul roșu «Articolul n-are cota TVA» rămâne după ce cota a fost aleasă pe linie”:
      // mesajul spunea „alege cota pe linie” — aleasă, linia nu mai e cea refuzată, deci mesajul ei (cu butonul spre Produse) dispare
      // (DS cap.6 v2.92, clasa 290: eroarea dispare când câmpul e corectat). Golită la loc („—”), linia rămâne fără cotă și emiterea o cere.
      if (l.cota_tva != null) { const z = zonaLinii.querySelector("#em-l" + linii.indexOf(l) + "-cota-mesaj"); if (z) z.innerHTML = ""; }
      recalc();
    });
    const selCateg = zonaLinii.querySelector("#em-l" + i + "-categorie");
    if (selCateg) selCateg.addEventListener("change", () => { l.categorie_tva = selCateg.value || null; l.cotaAleasa = true; l.categoriePropusa = false; actualizeazaC331(); });
    cant.addEventListener("input", () => { l.cantitate = parseFloat(cant.value) || 0; recalc(); });
    um.addEventListener("input", () => { l.um = um.value.trim(); l.umScris = true; l.umPropus = false; });
    // [pct.1b] prețul golit rămâne GOL (era `|| 0`: un câmp șters pleca drept preț 0, pe care nu-l scrisese nimeni)
    pret.addEventListener("input", () => { const v = parseFloat(pret.value); l.pret_unitar = Number.isFinite(v) ? v : ""; l.pretPropus = false; recalc(); });
    const cautaArt = zonaLinii.querySelector("#em-l" + i + "-cauta-articol");
    if (cautaArt && selArt) cautaInLista(cautaArt, selArt);   // [488] lista se strânge; articolul ales rămâne în ea
    if (selArt) selArt.addEventListener("change", () => {  // [punte_stoc_v1] F172
      l.articol_id = selArt.value ? parseInt(selArt.value, 10) : null;
      const o = selArt.selectedOptions[0];
      if (l.articol_id && o && o.dataset.um) { l.um = o.dataset.um; l.umScris = true; l.umPropus = true; um.value = o.dataset.um; }   // UM-ul articolului din stoc
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
    });
    // [lotul 11, decizia 10.3] TVA-ul pe regula unică (e-Factura, `tvaDocument` = `core/tva_calcul.py`): pe cotă, rotunjit o dată — nu pe
    // linie (fosta regulă a ecranului, 23.08.2026: 50 × 3 × 19,99 la 21% dădea 629,50; regula e-Factura dă 629,69, ca serverul)
    const _t = tvaDocument(linii.filter((l) => l && l.cota_tva !== null && l.cota_tva !== undefined));
    baza = tvaDocument(linii.map((l) => l && { cantitate: l.cantitate, pret_unitar: l.pret_unitar, cota_tva: 0 })).baza;
    tva = _t.tva;
    const cu = (x) => `${bani(x)} ${monedaSel || ""}`;   // `bani()` e formatorul canonic (api.js); aici doar i se adauga moneda
    const nestiut = faraCota > 0;
    corp.querySelector("#em-total").innerHTML = `
      <div class="em-total-rand"><span>Bază</span><b>${cu(baza)}</b></div>
      <div class="em-total-rand"><span>TVA</span><b>${nestiut ? "—" : cu(tva)}</b></div>
      <div class="em-total-rand em-total-mare"><span>Total</span><b>${nestiut ? "—" : cu(baza + tva)}</b></div>
      ${nestiut ? `<p class="ecran-nota" id="em-total-nota">TVA-ul nu se poate calcula încă: cota nu e stabilită pe ${cate(faraCota, "linie", "linii")}. Se propune automat din denumire — scrie denumirea articolului (sau alege-l din stoc) și așteaptă propunerea.</p>` : ""}`;
    actualizeazaLei(nestiut);   // [lotul 10, 7g] factura în valută: cursul BNR și sumele în lei, înainte de emitere
    salveazaCiorna();   // [lotul 07.10 pct.2] modelul liniilor se schimbă și fără tastă: cota propusă, o linie ștearsă
  }

  // [lotul 10, comanda 10.2 pct.7g] „Factură în valută: cursul BNR și TVA-ul în lei nu se văd înainte de emitere.” La o monedă străină,
  // sub totaluri: cursul BNR cu care VA emite serverul (data lui) și TVA-ul / totalul în lei — calculate de server (`facturi_api.
  // previzualizare_lei`: același curs, aceeași conversie ca la emitere, CF art.319 alin.(20) lit.j: „suma taxei colectate, exprimate în
  // lei”), nu aici: ecranul nu duplică regula (interdicția 4). Cererea pleacă după ce omul s-a oprit din scris; un răspuns întârziat,
  // pentru o stare deja schimbată, nu se mai afișează. Cât cota nu e stabilită pe o linie cu valoare, sumele în lei sunt „—”, ca totalul.
  let leiTimer = null;
  const cerereLei = ultimaCerere();   // [C103] moneda, data sau o linie schimbate în șir: numai conversia ultimei cereri ajunge pe ecran
  function actualizeazaLei(nestiut) {
    const z = corp.querySelector("#em-valuta");
    if (!z) return;
    clearTimeout(leiTimer);
    const actuala = cerereLei();
    if (!monedaSel || monedaSel === "RON") { z.hidden = true; z.innerHTML = ""; return; }
    const moneda = monedaSel, data = (corp.querySelector("#em-data") || {}).value || dataIso();
    // DS cap.24 regula 2: lista trimisă e lista de pe ecran, nefiltrată — cât un rând e incomplet, numai cursul (ca la cota nestabilită)
    const incomplet = linii.some((l) => !l || l.cantitate === "" || l.cantitate == null || l.pret_unitar === "" || l.pret_unitar == null);
    const cerere = { moneda, data_emitere: data, linii: (nestiut || incomplet) ? null : linii
      .map((l) => ({ cantitate: l.cantitate, pret_unitar: l.pret_unitar, cota_tva: l.cota_tva })) };
    // refuzul cursului (DS cap.6 v2.93, 410): zona sub monedă, cu titlul ei; mesajul îl pune `arataMesaj`
    const zonaRefuzului = () => {
      z.hidden = false;
      z.innerHTML = `<div class="fd-valuta-titlu">Conversie în lei (art. 319 Cod fiscal)</div><div id="em-valuta-mesaj"></div>`;
      return z.querySelector("#em-valuta-mesaj");
    };
    const reincearca = " La emitere vei putea reîncerca sau scrie cursul de mână, cu data lui.";
    leiTimer = setTimeout(async () => {
      let r;
      try { r = await api.post(`/tenants/${tenantId}/facturi/previzualizare-lei`, cerere); }
      catch (e) {
        if (!actuala()) return;
        if (z.isConnected) arataMesaj(zonaRefuzului(), `${(e && e.mesaj) || "Cursul BNR nu s-a putut citi acum."}${reincearca}`, "eroare");
        return;
      }
      if (!actuala()) return;   // între timp s-a schimbat moneda, data sau o linie
      if (!z.isConnected) return;
      z.hidden = false;
      if (!r || !r.ok) {
        arataMesaj(zonaRefuzului(), `${(r && r.mesaj) || ""}${r && r.cod === "MONEDA_NECOTATA" ? "" : reincearca}`, "eroare");
        return;
      }
      const sume = r.tva_lei != null;
      z.innerHTML = `
        <div class="fd-valuta-titlu">Conversie în lei (art. 319 Cod fiscal), cum o va scrie factura</div>
        <div class="fd-tot-rand"><span>Curs BNR ${esc(moneda)}</span><span id="em-valuta-curs"><b>${cursValutar(r.curs)}</b> din ${esc(dataRo(r.data_curs))}</span></div>
        <div class="fd-tot-rand"><span>TVA în lei</span><span id="em-valuta-tva"><b>${sume ? bani(r.tva_lei) + " lei" : "—"}</b></span></div>
        <div class="fd-tot-rand"><span>Total în lei</span><span id="em-valuta-total">${sume ? bani(r.total_lei) + " lei" : "—"}</span></div>
        ${r.curs_zilei_lipsa ? `<div id="em-valuta-lipsa"></div>`
          : `<div class="fd-valuta-sub">Ultimul curs comunicat de BNR înaintea datei facturii (${esc(dataRo(data))}); se fixează la emitere.</div>`}`;
      // [460] cursul zilei lipsește (ultimul comunicat înaintea datei facturii): ce lipsește și ce se folosește, spus de server (DS cap.6: avert)
      if (r.curs_zilei_lipsa) arataMesaj(z.querySelector("#em-valuta-lipsa"), r.curs_zilei_lipsa.mesaj, "avert");
    }, 350);
  }

  corp.querySelector("#em-add-linie").addEventListener("click", () => { linii.push(linieNoua()); deseneazaLinii(); salveazaCiorna(); });
  // [lotul 07.10 pct.2] ciorna: câmpurile simple, după id; liniile din model; moneda; răspunsul la „Pleacă marfa acum?”
  const CAMPURI_CIORNA = ["em-cui", "em-nume", "em-adresa", "em-oras", "em-judet", "em-regiune",   // [C61] și localitatea / județul
    "em-data", "em-scadenta", "em-tara", "em-tipop", "em-bon-nr", "em-bon-data", "em-tip"];
  const areContinut = () => ["em-cui", "em-nume", "em-adresa", "em-bon-nr"].some((id) => ((corp.querySelector("#" + id) || {}).value || "").trim())
    || linii.some((l) => l && (l.descriere || l.pret_unitar || l.cantitate || l.articol_id));
  let ciornaPornita = false;   // nimic nu se scrie până nu s-a citit (altfel prima redesenare ar suprascrie ciorna cu gol)
  function salveazaCiorna() {
    if (!ciornaPornita) return;
    if (!areContinut()) { stergeCiorna(tenantId); return; }
    // [lotul 07.10 B, C12a] și ce a spus ANAF despre client (plătitor / neplătitor TVA): restaurarea îl arată din nou, ca text
    // [lotul 12, C166] la fel răspunsurile negative (CUI negăsit, cod invalid în VIES, ANAF / VIES care nu răspund); „se verifică…” nu e un
    // răspuns: o ciornă lăsată în timpul verificării nu-l păstrează (la revenire n-ar mai veni nimic după el)
    const _st = corp.querySelector("#em-cui-stare");
    const c = { v: 1, salvat_la: new Date().toISOString(), linii: linii.map((l) => Object.assign({}, l)), moneda: monedaSel,
                scadentaScrisa, pleacaMarfa: pleacaMarfaCurent, semnMarfa, campuri: {},
                stareCui: _st && !_st.dataset.seVerifica ? { text: _st.textContent, rau: _st.classList.contains("em-cui-rau") } : null };
    CAMPURI_CIORNA.forEach((id) => { const e = corp.querySelector("#" + id); if (e) c.campuri[id] = e.value; });
    scrieCiorna(tenantId, c);
  }
  const ciorna = citesteCiorna(tenantId);
  if (ciorna && Array.isArray(ciorna.linii) && ciorna.linii.length) {
    ciorna.linii.forEach((l) => linii.push(Object.assign(linieNoua(), l)));
    Object.entries(ciorna.campuri || {}).forEach(([id, v]) => { const e = corp.querySelector("#" + id); if (e && v != null) e.value = v; });
    if (ciorna.moneda) { monedaSel = ciorna.moneda; const sm = corp.querySelector("#em-moneda"); if (sm) sm.value = monedaSel; }
    if (ciorna.stareCui && ciorna.stareCui.text) {
      const st = corp.querySelector("#em-cui-stare");
      st.className = "em-cui-stare" + (ciorna.stareCui.rau ? " em-cui-rau pe-randuri" : "");   // ca la răspunsul verificării
      st.innerHTML = ciorna.stareCui.rau ? esc(ciorna.stareCui.text) : `<span class="em-cui-info">${esc(ciorna.stareCui.text)}</span>`;
    }
    scadentaScrisa = !!ciorna.scadentaScrisa;
    pleacaMarfaCurent = ciorna.pleacaMarfa == null ? null : ciorna.pleacaMarfa;
    semnMarfa = ciorna.semnMarfa || null;
    const zc = corp.querySelector("#em-ciorna");
    const cand = ciorna.salvat_la ? new Date(ciorna.salvat_la) : null;
    zc.innerHTML = `<div class="caseta-info"><span class="ci-mesaj">Factura începută${cand ? " (ultima modificare: " + esc(dataRo(ciorna.salvat_la.slice(0, 10))) + ", " + String(cand.getHours()).padStart(2, "0") + ":" + String(cand.getMinutes()).padStart(2, "0") + ")" : ""} a fost păstrată, așa cum ai lăsat-o. Rămâne până o emiți sau apeși „Renunță la factură”.</span></div>`;
    // [lotul 11, 428] data restaurată din ciornă (alta decât azi): ce depinde de dată — regimul TVA la încasare, cotele — se recitește la ea
    const dataCiorna = (ciorna.campuri || {})["em-data"];
    if (dataCiorna && dataCiorna !== dataIso()) reincarcaPregatirea();
  } else {
    linii.push(linieNoua());  // prima linie
  }
  deseneazaLinii();
  ciornaPornita = true;
  corp.addEventListener("input", salveazaCiorna);
  corp.addEventListener("change", salveazaCiorna);
  corp.querySelector("#em-renunta").addEventListener("click", (ev) => {
    confirmaCaseta(ev.currentTarget, "Renunți la factura începută? Ce ai scris pe ea se șterge; nu se emite nimic.", () => {
      stergeCiorna(tenantId);
      randeazaEmitere(corp, nav, tenantId, opt);
    }, { textOk: "Da, renunț la factură", textNu: "Continui factura" });   // [330] nu două „Renunță” alăturate
  });

  // [274b] clientul din afara României: localitatea și regiunea lui (adresa de livrare a livrării intracomunitare în e-Factura)
  // [C61] clientul român: localitatea și județul (lista), precompletate din ANAF la „Verifică”; aceeași localitate, alt nume la străin
  const aratăStrain = () => {
    const s = corp.querySelector("#em-tara").value !== "RO";
    corp.querySelectorAll(".em-strain").forEach((e) => { e.hidden = !s; });
    corp.querySelectorAll(".em-ro").forEach((e) => { e.hidden = s; });
    corp.querySelector("#em-oras-et").textContent = s ? "Localitatea clientului (adresa de livrare din e-Factura)" : "Localitatea clientului";
  };
  aratăStrain();   // țara restaurată din ciornă arată câmpurile ei
  // [deficiența 304, rest din 290] refuzul calculat pentru clientul de dinainte (categoria față de țară) nu mai rămâne pe ecran după
  // schimbarea clientului: erorile liniilor și mesajul de jos se scot la orice schimbare a clientului (CUI, țară, denumire), inclusiv când
  // țara se pune din cod (CUI-ul, VIES) — acolo nu se declanșează niciun „change”
  // [lotul 12, 304 redeschisă: „după «Emite» cu clientul român și categoria «livrare intracomunitară», CUI-ul schimbat lasă pe ecran caseta
  // «NU s-a salvat» și fereastra refuzului cu «(țara clientului: RO)»”] tot refuzul emiterii pleacă: și caseta „NU s-a salvat.” de lângă
  // buton, și fereastra „Am înțeles” a refuzului (pusă de api.js când textul lui întreg nu e pe ecran) — și încă de la prima tastă în CUI /
  // denumire, nu abia la ieșirea din câmp
  const curataRefuzulClientului = () => {
    curataEroriCamp(corp);
    const r = corp.querySelector("#em-rezultat"); if (r) r.innerHTML = "";
    (corp.closest(".fereastra") || corp).querySelectorAll(".refuz-salvare").forEach((x) => x.remove());
    const f = document.getElementById("refuz-nevazut");
    if (f && String(f.dataset.ruta || "").startsWith(`/tenants/${tenantId}/facturi`)) f.remove();
  };
  corp.querySelector("#em-tara").addEventListener("change", () => { curataRefuzulClientului(); aratăStrain(); repropuneLiniile(); });
  corp.querySelector("#em-nume").addEventListener("input", curataRefuzulClientului);
  // [lotul 12, 459.1, comanda Costin 12.2 pct.5] denumirea, adresa, localitatea și județul aduse de „Verifică” (ANAF sau VIES) țin de
  // CUI-ul verificat: la tastarea altui CUI pleacă, dacă omul nu le-a schimbat (`date_anaf.js`, F188). Linia de stare o golește mai jos
  // handlerul 304 (și clasa „răspuns negativ”, și „se verifică…”), deci nu se mai dă aici.
  const anaf = legaDateAnaf(corp.querySelector("#em-cui"),
    ["#em-nume", "#em-adresa", "#em-oras", "#em-judet"].map((id) => corp.querySelector(id)));
  corp.querySelector("#em-cui").addEventListener("input", () => {
    curataRefuzulClientului();
    // [304, aceeași clasă] răspunsul verificării de dinainte (plătitor / negăsit / VIES, firma inactivă) era al CUI-ului vechi
    const st = corp.querySelector("#em-cui-stare");
    if (st) { st.textContent = ""; st.className = "em-cui-stare"; delete st.dataset.seVerifica; }
    const av = corp.querySelector("#em-avert-inactiv");
    if (av) av.remove();
  });
  corp.querySelector("#em-cui").addEventListener("change", (ev) => {
    viesValid = null;   // [326] alt cod: verificarea VIES de dinainte nu mai e a lui
    const t = taraDinCui(ev.target.value), sel = corp.querySelector("#em-tara");
    if (t && sel && sel.value !== t) { sel.value = t; salveazaCiorna(); }
    curataRefuzulClientului();
    aratăStrain();
  });

  // verificare CUI
  // [deficiența 303, comanda Costin 17.10.2026 7.2] „«Verifică» CUI nu arată nimic cât așteaptă ANAF; pare stricat”: butonul spune
  // „Se verifică…” și e blocat cât așteaptă; un ANAF care nu răspunde se spune cu mesajul serverului, nu cu „verificarea a eșuat”
  const bVerif = corp.querySelector("#em-verifica");
  bVerif.addEventListener("click", async () => {
    if (bVerif.disabled) return;
    bVerif.disabled = true; bVerif.setAttribute("aria-busy", "true"); bVerif.textContent = "Se verifică…";
    try { await verificaCui(); } finally { bVerif.disabled = false; bVerif.removeAttribute("aria-busy"); bVerif.textContent = "Verifică"; }
  });
  // [deficiența 305] VIES dă adresa ca text (de obicei „strada\ncod poștal localitate”): localitatea e ultimul rând fără codul poștal; un
  // ultim rând care e numai codul poștal (Eircode, „D02 X285”) lasă localitatea pe rândul dinainte
  const localitateDinAdresa = (adresa) => {
    const r = String(adresa || "").split(/\n|,/).map((x) => x.trim()).filter(Boolean);
    while (r.length > 1 && /^[A-Z]{0,3}\d[\dA-Z\s-]{0,7}$/i.test(r[r.length - 1]) && r[r.length - 1].length <= 9) r.pop();
    const ultim = r.length > 1 ? r[r.length - 1] : "";
    return ultim.replace(/^[A-Z]{0,3}[-\s]?\d[\d\s-]*\s+/i, "").trim();
  };
  async function verificaCui() {
    const cui = corp.querySelector("#em-cui").value.trim();
    const stare = corp.querySelector("#em-cui-stare");
    if (!cui) return;
    // [vies_emitere_v1] cod TVA UE (prefix stat membru != RO) -> verificare VIES, nu ANAF
    const pfx = (cui.slice(0, 2) || "").toUpperCase();
    const UE = ["AT","BE","BG","CY","CZ","DE","DK","EE","EL","ES","FI","FR","HR","HU","IE","IT","LT","LU","LV","MT","NL","PL","PT","SE","SI","SK","XI"];
    if (UE.includes(pfx)) {
      stare.textContent = "se verifică în VIES…";
      stare.className = "em-cui-stare";
      stare.dataset.seVerifica = "1";
      try {
        const v = await api.get(`/tenants/${tenantId}/verifica-vies?cod_tva=${encodeURIComponent(cui)}`);
        if (v && v.valid) {
          delete stare.dataset.seVerifica;
          // unele state (ex. DE) nu divulga nume/adresa -> VIES intoarce "---"
          const adr = v.adresa && v.adresa !== "---" ? v.adresa.trim() : null;
          anaf.pune([v.nume && v.nume !== "---" ? v.nume : null, adr], { suprascrie: true });
          if (adr) anaf.pune([null, null, localitateDinAdresa(v.adresa)]);   // [305] localitatea clientului străin, din adresa VIES (numai în câmpul gol)
          const sel = corp.querySelector("#em-tara");
          if (sel && (v.tara || pfx) && sel.value !== (v.tara || pfx)) {
            const t = v.tara || pfx;   // codurile VIES ale listei (Grecia = EL)
            if ([...sel.options].some((o) => o.value === t)) { sel.value = t; curataRefuzulClientului(); aratăStrain(); }
          }
          stare.innerHTML = `<span class="em-cui-info">valid în VIES · ${esc(v.tara || pfx)}</span>`;
          stare.className = "em-cui-stare";
          viesValid = v.tara || pfx; repropuneLiniile();   // [326] liniile de serviciu deja scrise primesc categoria
          salveazaCiorna();
        } else {
          delete stare.dataset.seVerifica;
          stare.textContent = "cod TVA invalid în VIES — scutirea intracomunitară nu se aplică";
          stare.className = "em-cui-stare em-cui-rau pe-randuri";
          salveazaCiorna();   // [C166] și răspunsul negativ intră în ciornă
        }
      } catch (e) {
        delete stare.dataset.seVerifica;
        stare.textContent = (e && e.mesaj) || "VIES nu răspunde acum — încearcă din nou peste un minut.";
        stare.className = "em-cui-stare em-cui-rau pe-randuri";
        salveazaCiorna();   // [C166]
      }
      return;
    }
    stare.textContent = "se verifică la ANAF…";
    stare.className = "em-cui-stare";
    stare.dataset.seVerifica = "1";
    try {
      // [lotul 11, 444] numele scris pe factură pleacă la server ÎNAINTE de a fi înlocuit cu cel de la ANAF (`nume_dat_diferit`)
      const r = await api.get(`/tenants/${tenantId}/verifica-cui/${encodeURIComponent(cui)}?nume=${encodeURIComponent(corp.querySelector("#em-nume").value.trim())}`);
      delete stare.dataset.seVerifica;
      if (r && r.gasit) {
        // [C61] localitatea și județul domiciliului fiscal (aceeași adresă ca `adresa`), modificabile; PDF-ul nu le repetă când adresa
        // le cuprinde deja (`factura_pdf.adresa_tert`). „Verifică” e cerut de om: datele ANAF intră și peste ce era scris (județul numai
        // dacă e în listă)
        anaf.pune([r.denumire, r.adresa, r.localitate, r.judet], { suprascrie: true });
        // [p113_doar_gri] doar info TVA cu gri, fara verde/bifa/"gasita"
        stare.innerHTML = `<span class="em-cui-info">${r.platitor_tva ? "plătitor TVA" : "neplătitor TVA"}</span>`;
        stare.className = "em-cui-stare";
        propuneNumeAnaf(stare, r, tenantId, { fel: "clienti", pre: "em" });   // [lotul 11, 444] fișa clientului cu alt nume decât ANAF: se spune și se propune actualizarea
        salveazaCiorna();   // [lotul 07.10 B, C12a] răspunsul ANAF intră în ciornă: restaurarea îl arată
        // [p109_avert_inactiv] avertisment mare pentru firma INACTIVA
        const av = corp.querySelector("#em-avert-inactiv");
        if (av) av.remove();
        if (r.inactiv) {
          const box = document.createElement("div");
          box.id = "em-avert-inactiv";
          box.className = "em-avert-inactiv";
          box.innerHTML = `
            <div class="em-avert-titlu">⚠ Atenție: firmă inactivă fiscal la ANAF</div>
            <div class="em-avert-text">
              Dacă emiți factura către această firmă:<br>
              • beneficiarul <b>nu își poate deduce cheltuiala și nici TVA-ul</b> de pe factura ta (art. 11 Cod fiscal);<br>
              • o firmă inactivă poate fi în curs de dizolvare — există risc real de <b>neplată</b>;<br>
              • tranzacția poate atrage <b>controale ANAF</b>.<br>
              Verifică situația înainte de a continua. Poți emite, dar pe răspunderea ta.
            </div>`;
          stare.parentNode.insertBefore(box, stare.nextSibling);
        }
      } else {
        stare.textContent = "CUI negăsit la ANAF";
        stare.className = "em-cui-stare em-cui-rau pe-randuri";
        salveazaCiorna();   // [C166] și „CUI negăsit” intră în ciornă
      }
    } catch (e) {
      delete stare.dataset.seVerifica;
      stare.textContent = (e && e.mesaj) || "ANAF nu răspunde acum la verificarea CUI — încearcă din nou peste un minut.";
      stare.className = "em-cui-stare em-cui-rau pe-randuri";
      salveazaCiorna();   // [C166]
    }
  }

  // emitere
  // selector moneda -> actualizeaza starea + totalurile + nota
  const selMon = corp.querySelector("#em-moneda");
  const notaMon = corp.querySelector("#em-moneda-nota");
  if (selMon) {
    selMon.addEventListener("change", () => {
      monedaSel = selMon.value;
      if (notaMon) notaMon.textContent = monedaSel === "RON"
        ? "" : "TVA se convertește în lei la cursul BNR (art. 319).";
      recalc();
    });
  }

  // plaseaza erorile field-keyed din 422 (backendul: {camp: em-l{i}-..., eticheta}, purtate de api.js ca
  // {camp, mesaj}) LANGA campul lor (cap.6 mecanism A). Cele fara #camp in DOM -> zona generica (fallback B).
  function plaseazaErori(rez, e) {
    curataEroriCamp(corp);
    // [lotul 11, 440] drumul unic al refuzului (`arataRefuzul`): câmpurile `em-l{i}-…` lângă ele, textul fiecărui refuz fără câmp în zonă
    const eris = (e && e.erori_campuri) || [];
    rez.textContent = "";
    arataRefuzul(corp, eris.length || (e && e.mesaj) ? e : { mesaj: "Emiterea a eșuat. Încearcă din nou." }, rez);
    rez.className = rez.textContent ? "em-rezultat em-rau" : "em-rezultat";
  }

  async function trimiteEmitere(cursManual) {
    const rez = corp.querySelector("#em-rezultat");
    curataEroriCamp(corp);
    // NU se filtreaza randuri (cap.24 regula 2): lista trimisa = lista randata. Un rand incomplet se
    // valideaza pe backend si se raporteaza langa campul lui, nu dispare tacit.
    const payload = {
      linii: linii.map((l) => ({
        descriere: l.descriere, cantitate: l.cantitate, um: l.um || "buc",
        pret_unitar: (l.pret_unitar === "" || l.pret_unitar == null) ? null : l.pret_unitar, cota_tva: l.cota_tva,   // [pct.1b] gol = lipsă
        cota_propusa: l.cota_propusa,   // [pct.3] pentru jurnalul „propus → ales”
        articol_id: l.articol_id || null,  // [punte_stoc_v1] F172
        categorie_tva: l.cota_tva === 0 ? (l.categorie_tva || null) : null,   // [274b] categoria liniei cu 0%
      })),
      // [274b] categoria produsului la taxarea inversă; localitatea și regiunea clientului străin (adresa de livrare din e-Factura)
      // [C61] la clientul român localitatea și județul (codul din listă) — scrise pe factură și pe PDF
      categorie_331: (() => { const e = corp.querySelector("#em-c331"); return e && !e.hidden ? (e.value || null) : null; })(),
      tert_oras: (corp.querySelector("#em-oras").value || "").trim() || null,
      tert_judet: ((corp.querySelector(corp.querySelector("#em-tara").value !== "RO" ? "#em-regiune" : "#em-judet") || {}).value || "").trim() || null,
      tert_nume: corp.querySelector("#em-nume").value.trim() || null,
      tert_cui: corp.querySelector("#em-cui").value.trim() || null,
      tert_adresa: corp.querySelector("#em-adresa").value.trim() || null,
      moneda: monedaSel,
      tert_tara: corp.querySelector("#em-tara").value,              // [B1 D300] — dedusă din CUI, vizibilă înainte de emitere (DS cap.17)
      tip_operatiune: corp.querySelector("#em-tipop").value,    // [B1 D300] — „normală” vizibil (cazul uzual), schimbabilă
      // [decizia A 02.10] factura emisă pe baza bonului fiscal (HG 1/2016 pct.97 alin.(1)); validarea e pe server
      bon_fiscal_nr: ((corp.querySelector("#em-bon-nr") || {}).value || "").trim() || null,
      bon_fiscal_data: (corp.querySelector("#em-bon-data") || {}).value || null,
      // [comanda Costin 05.10.2026 pct.4] data emiterii și scadența, stabilite pe formular
      data_emitere: (corp.querySelector("#em-data") || {}).value || null,
      data_scadenta: (corp.querySelector("#em-scadenta") || {}).value || null,
    };
    if (cursManual != null) payload.curs_manual = cursManual;
    if (pleacaMarfaCurent !== null) payload.pleaca_marfa = pleacaMarfaCurent;  // [punte_stoc_v1] raspuns poarta
    if (dovadaTransportCurent !== null) payload.dovada_transport = dovadaTransportCurent;   // [lotul 12, C84] răspunsul întrebării

    const btn = corp.querySelector("#em-emite");
    if (btn) { btn.disabled = true; btn.textContent = "Se emite…"; }
    const rez2 = corp.querySelector("#em-rezultat");
    rez2.dataset.tenant = String(tenantId);   // [lotul 13, C199] reîncercarea VIES de după emitere (`reverificaVies`)
    try {
      const selTip = corp.querySelector("#em-tip");
      if (selTip) payload.tip = selTip.value;
      const r = await api.post(`/tenants/${tenantId}/facturi/emite`, payload);
      const notaStoc = textDescarcare(r.descarcare);  // [punte_stoc_v1] rezultatul descarcarii de gestiune, daca poarta a fost DA
      // [deficiența 327, 18.10.2026] „a fost trimisă către contabil” numai când emite clientul (portalul); contabilul care emite e chiar
      // contabilul. Butonul nu rămâne „Se emite…”: factura e emisă (o a doua emitere nu se oferă). Mesajul de după emitere (și caseta
      // SPV) nu mai are derulare proprie (285): butonul nu mai are nimic de făcut, deci nu trebuie ținut vizibil sub mesaj.
      const notaTvai = esc(textTvaIncasare(r.contare));   // [lotul 11, 428] factura în sistemul TVA la încasare: unde e TVA-ul
      // [lotul 12, 443.1] „Factura F62 emisă” / „Factura F1A14 emisă”: seria și numărul separat, ca în Istoric („F1A nr. 14”)
      rez2.innerHTML = `✓ Factura <b>${esc(numarCuSerie(r.serie, r.numar))}</b> emisă · total ${Number(r.total).toLocaleString("ro-RO", {minimumFractionDigits:2})} ${monedaSel}${notaStoc}${notaTvai}.${sesiune.rol() === "client" ? " A fost trimisă către contabil." : ""}`;
      rez2.className = "em-rezultat em-bun em-emisa";
      arataAvertismenteEmitere(rez2, r.avertismente);   // [lotul 12, C157 / C84] emisă, cu ce trebuie știut
      if (r.vies_de_reverificat) reverificaVies(rez2, r.vies_de_reverificat);   // [lotul 13, C199 / 550] VIES n-a răspuns: reîncercarea
      if (btn) btn.textContent = "Emisă ✓";
      stergeCiorna(tenantId);   // [lotul 07.10 pct.2] emisă: ciorna și-a terminat rostul
      ciornaPornita = false;
      // [391, retestul 19.10.2026: „după emitere (F1A7) e încă oferit «Renunță la factură», cu mesajul fals «Ce ai scris se șterge; nu se
      // emite nimic»”] factura e emisă: nu mai e nimic la care să renunți
      const bRenunta = corp.querySelector("#em-renunta");
      if (bRenunta) bRenunta.remove();
      const cRenunta = document.getElementById("caseta-atentie-activa");
      if (cRenunta && corp.contains(cRenunta)) cRenunta.remove();
      // [deficiența 275c] firma neconectată la SPV (sau fără drept pentru CUI): se spune DE LA EMITERE, cu drumul spre conectare — și
      // formularul nu mai pleacă singur, ca mesajul să poată fi citit
      let stSpv = null;
      try { stSpv = await api.get(`/tenants/${tenantId}/spv/stare`); } catch (e) {
        const z = document.createElement("div");
        rez2.appendChild(z);
        arataMesaj(z, `Starea SPV a firmei nu s-a putut citi (${e.mesaj || "eroare"}): o vezi în lista facturilor, pe rândul facturii.`, "avert");
      }
      const tSpv = stSpv ? textStareSpv(stSpv) : null;
      if (tSpv && tSpv.spreConectare) {
        const z = document.createElement("div");
        z.className = "caseta-atentie";
        z.style.marginTop = "8px";
        // [307] termenul de 5 zile e al facturii OBLIGATORII (client stabilit / înregistrat în scopuri de TVA în România)
        const strain = ((corp.querySelector("#em-tara") || {}).value || "RO").toUpperCase() !== "RO"
          && !/^(RO|\d)/i.test(((corp.querySelector("#em-cui") || {}).value || "").trim());
        z.innerHTML = `<div class="ca-mesaj">${esc(tSpv.text)} Factura emisă rămâne netrimisă în SPV; ${strain
          ? "pentru un client care nu e stabilit în România, transmiterea în RO e-Factura nu e obligatorie (OUG 120/2021 art.10 alin.(1))."
          : "termenul de transmitere e de 5 zile lucrătoare de la emitere (OUG 120/2021 art.10 alin.(7))."}</div>`;
        rez2.appendChild(z);
        butonSpreEcran(z, "conectare_spv", nav, tenantId, { clasa: "buton-secundar" });
      }
      // [418c / 410, DS cap.27] confirmarea emiterii rămâne pe ecran; istoricul se deschide la cererea omului, nu singur după 1,2 s
      if (opt.dupaEmitere) {
        const b = document.createElement("button");
        b.type = "button"; b.className = "buton-secundar"; b.id = "em-spre-istoric"; b.style.marginTop = "8px";
        b.textContent = "Vezi factura în Istoric facturi \u2192";
        b.addEventListener("click", () => opt.dupaEmitere());
        rez2.appendChild(b);
      }
    } catch (e) {
      const det = e && e.mesaj;
      const cursIndisp = e && e.cod === 409 && det && typeof det === "object" && det.cod === "CURS_INDISPONIBIL";
      const serieLipsa = e && e.detaliu && e.detaliu.cod === "SERIE_LIPSA";
      const spreEcran = e && e.detaliu && typeof e.detaliu === "object" && e.detaliu.ecran && e.detaliu.ecran !== "numerotare";
      if (e && e.detaliu && e.detaliu.cod === "INTREABA_PLEACA_MARFA") {
        intreabaPleacaMarfa();   // [304] liniile au trecut: abia acum întrebarea
      } else if (e && e.detaliu && e.detaliu.cod === "INTREABA_DOVADA_TRANSPORT") {
        intreabaDovada(e.detaliu.intrebare);   // [lotul 12, C84] după linii și după „Pleacă marfa acum?”
      } else if (cursIndisp) {
        arataCursIndisponibil(det);
      } else if (serieLipsa) {
        arataSerieLipsa(e.detaliu);
      } else if (spreEcran) {
        arataRefuzCuEcran(e.detaliu);
      } else {
        plaseazaErori(rez2, e);
      }
      if (btn) { btn.disabled = false; btn.textContent = "Emite factură"; }
    }
  }

  // [lot 19 d12 → lotul 07.10 pct.2] Refuzul care trimite în ALT ecran (capitalul social, metoda de stoc, orice `detaliu.ecran`):
  // butonul deschide ecranul PESTE factură, iar „←” readuce formularul exact cum era (și ciorna îl păstrează pe orice alt drum).
  function arataRefuzCuEcran(det) {
    const rez = corp.querySelector("#em-rezultat");
    rez.className = "em-rezultat";
    rez.innerHTML = `
      <div class="em-curs-box">
        <div class="em-curs-titlu">⚠ ${esc(det.mesaj || "")}</div>
        <div class="em-curs-actiuni" id="em-refuz-actiuni"></div>
      </div>`;
    butonSpreEcran(rez.querySelector("#em-refuz-actiuni"), det.ecran, nav, tenantId,
      { id: det.ecran === "date_firma" ? "em-deschide-date-firma" : null, inapoiLa: "factură", camp: det.camp_ecran || null });
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
        <label class="camp"><span class="camp-eticheta">Numărul primei facturi din serie (gol = 1; dacă seria a mai fost folosită, după ultima emisă în ea)</span>
          <input class="camp-input" id="em-serie-start" type="number" min="1" step="1" autocomplete="off"></label>
        <div class="em-curs-actiuni">
          <button class="buton-primar" id="em-serie-si-emite" data-actiune="PUT /tenants/{tenant_id}/facturi/numerotare">Stabilește seria și emite</button>
        </div>
      </div>`;
    const inp = rez.querySelector("#em-serie-noua");
    focusFaraSalt(inp);
    rez.querySelector("#em-serie-si-emite").addEventListener("click", async () => {
      curataEroriCamp(rez);
      const serie = inp.value.trim();
      if (!serie) { eroareCamp(rez, "em-serie-noua", "Completează seria (legea cere numărul facturii într-o serie)."); return; }
      if (/^\d+$/.test(serie)) { eroareCamp(rez, "em-serie-noua", "Seria e un prefix cu litere (ex: FCT), nu un număr."); return; }
      // [lotul 13, 542] seria nouă pornește de la 1 (serverul: `facturi_api.urmatorul_in_serie`) sau de la numărul ales aici
      const st = rez.querySelector("#em-serie-start").value.trim();
      if (st && !(/^\d+$/.test(st) && Number(st) >= 1)) { eroareCamp(rez, "em-serie-start", "Numărul primei facturi e un număr întreg, de la 1."); return; }
      try {
        await api.put(`/tenants/${tenantId}/facturi/numerotare`, st ? { serie, numar_start: Number(st) } : { serie });
      } catch (er) {
        const ec = (er && er.erori_campuri) || [];
        const pe = ec.find((x) => x.camp === "numar_start");
        eroareCamp(rez, pe ? "em-serie-start" : "em-serie-noua", (pe && pe.mesaj) || (er && er.mesaj) || "Seria nu s-a putut salva."); return;
      }
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
      </div>`;
    rez.querySelector("#em-curs-retry").addEventListener("click", () => trimiteEmitere(null));
    // [lotul 13, 673 — DS cap.2a v2.104] „Introdu manual” deschide o fereastră nouă cu cursul (înainte: câmpul apărea în zona rezultatului);
    // „Emite cu acest curs” întoarce la factură (formularul ei, completat, e păstrat de navigator) și emite de acolo
    rez.querySelector("#em-curs-manual").addEventListener("click", () => {
      nav.deschide("Cursul introdus de mână", (c2) => {
        c2.innerHTML = `
          <div class="em-curs-manual">
            <label for="em-curs-val">Curs ${det.moneda} → RON pentru ${dataRo(det.data)}</label>
            <input type="number" step="0.0001" id="em-curs-val" placeholder="ex. 5.2438" class="camp-input">
            <button class="buton-primar" id="em-curs-ok" data-actiune="POST /tenants/{tenant_id}/facturi/emite">Emite cu acest curs</button>
            <div class="em-curs-avertisment">Introdu cursul BNR valabil pentru data facturii. Răspunderea corectitudinii îți revine.</div>
          </div>`;
        focusFaraSalt(c2.querySelector("#em-curs-val"));
        c2.querySelector("#em-curs-ok").addEventListener("click", () => {
          curataEroriCamp(c2);
          const v = parseFloat(c2.querySelector("#em-curs-val").value);
          if (!v || v <= 0) { eroareCamp(c2, "em-curs-val", "Scrie cursul BNR al zilei facturii (un număr mai mare ca 0)."); return; }
          nav.inapoi();
          trimiteEmitere(v);
        });
      });
    });
  }

  // [punte_stoc_v1] F172: poarta "pleaca marfa acum?" INAINTE de emitere, la firma CV cu linie de
  // articol (caseta-poarta, DS cap.5 v2.14). Fara articole -> emitere directa, flux identic cu azi.
  function porniEmitere() {
    curataEroriCamp(corp);
    // [lotul 12, C84] răspunsul la „Ai dovada transportului?” rămâne numai pentru aceleași linii de livrare intracomunitară (ca marfa)
    if (dovadaTransportCurent !== null && semnDovada !== semnLivrareIc()) dovadaTransportCurent = null;
    const tip = corp.querySelector("#em-tip").value;
    const cuArticole = linii.filter((l) => l && l.articol_id).length;
    // [decizia A 02.10] factura din bon nu descarcă gestiunea (marfa a ieșit cu bonul) -> fără poartă
    const dinBon = !!((corp.querySelector("#em-bon-nr") || {}).value || "").trim();
    if (cuArticole && tip === "factura" && !dinBon) {
      // [lotul 07.10 pct.17] întrebarea s-a pus deja pentru exact aceste articole: răspunsul rămâne (seria stabilită din
      // refuz, revenirea din Date firmă, a doua apăsare pe „Emite”); se pune din nou numai dacă s-au schimbat articolele.
      if (pleacaMarfaCurent !== null && semnMarfa === semnArticole()) { trimiteEmitere(null); return; }
      // [deficiența 304] întâi serverul verifică liniile (fără răspuns la întrebare): un refuz vine acum, nu după „Pleacă marfa acum?”;
      // numai dacă liniile trec, serverul cere răspunsul (`INTREABA_PLEACA_MARFA`) și atunci se pune întrebarea
      pleacaMarfaCurent = null;
      trimiteEmitere(null);
    } else {
      pleacaMarfaCurent = null;
      trimiteEmitere(null);
    }
  }
  function intreabaDovada(intrebare) {
    const rez = corp.querySelector("#em-rezultat");
    rez.className = "em-rezultat";
    intrebareDovadaTransport(rez, intrebare, (da) => {
      dovadaTransportCurent = da; semnDovada = semnLivrareIc(); trimiteEmitere(null);
    }, { da: "em-dovada-da", nu: "em-dovada-nu" });
  }
  function semnLivrareIc() {
    // cheie internă (nu se afișează): liniile de livrare intracomunitară pentru care s-a răspuns
    return linii.filter((l) => l && l.categorie_tva === "livrare_ic").map((l) => [l.descriere, l.cantitate, l.pret_unitar].join(":")).join(",");
  }
  function intreabaPleacaMarfa() {
    const rez = corp.querySelector("#em-rezultat");
    rez.className = "em-rezultat";
    intrebarePleacaMarfa(rez, linii.filter((l) => l && l.articol_id).length, (da) => {
      pleacaMarfaCurent = da; semnMarfa = semnArticole(); salveazaCiorna(); trimiteEmitere(null);
    }, { da: "em-poarta-da", nu: "em-poarta-nu" });
  }
  function semnArticole() {
    // cheie internă (nu se afișează): articolele și cantitățile pentru care s-a răspuns
    return linii.filter((l) => l && l.articol_id).map((l) => [l.articol_id, l.cantitate].join(":")).join(",");
  }
  corp.querySelector("#em-emite").addEventListener("click", porniEmitere);
}

// audit_cab_lot1_v1

// emitere_inapoi_v1

// numerotare_configurata_v1

// fara_precompletari_v1
// emitere_std_v1 · batch 3b: randuri dinamice cap.24 (model pozitional + re-randare + stergere splice + backend autoritar 422.campuri)
