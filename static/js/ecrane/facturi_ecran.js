// facturi_ecran.js — cardul Facturi consolidat, REUTILIZABIL (portal client, gratuit, cabinet).
// Primeste tenantId -> merge din orice context. Contine:
//   meniu (Istoric / Emite / Model factura) + istoric + emitere.
//   Detalii / Storno / Model se adauga in pasii urmatori.
// Apelare: randeazaFacturi(corp, nav, tenantId, { inapoi, titluInapoi })
import { api, cate, cursValutar, dataRo, arataMesaj, confirmaCaseta, esc, bani, eroareCamp, curataEroriCamp, semnAjutor, descarca, deschide, dataIso, cantitate, selectDaNu, daNu, cereAlegerile, focusFaraSalt, refuzPeRand, stareNota, numarCuSerie, arataRefuzul, cereCompletate } from "../api.js?v=58f26a3fc4";  /* esc_nc27 */
import { randeazaStareSpv } from "./spv_stare.js?v=1f2821106d";  /* [lotul 6: 273, 275] */
import { sesiune } from "../sesiune.js?v=898215e0ee";
import { randeazaEmitere, intrebarePleacaMarfa, textDescarcare, textTvaIncasare, tvaDocument } from "./emitere_ecran.js?v=57e787b44e";
import { cuLegareaNir, interogareLegare } from "./nir_legare.js?v=b34abfe2ec";
import { propuneNumeAnaf } from "./nume_anaf.js?v=d59cd56b02";   // [lotul 11, 444]

// [deficiența 418c, clasa 410, DS cap.27] după un act reușit, confirmarea rămâne pe ecran și drumul înapoi e un buton — nu o navigare
// temporizată, care ștergea confirmarea înainte de a fi citită
function butonInapoi(zona, nav) {
  if (!nav || !nav.inapoi) return;
  const b = document.createElement("button");
  b.type = "button"; b.className = "buton-secundar"; b.style.marginTop = "8px";
  b.textContent = "\u2190 Înapoi";
  b.addEventListener("click", () => nav.inapoi());
  zona.appendChild(b);
}

const dirEticheta = (d) => (d === "iesire" || d === "emisa") ? "emis\u0103"
  : (d === "intrare" || d === "primita") ? "primit\u0103" : (d || "");

export function randeazaFacturi(corp, nav, tenantId, opt = {}) {
  meniuFacturi(corp, nav, tenantId, opt);
}

// ---------- MENIU (Istoric / Emite / Model) ----------
function meniuFacturi(corp, nav, tenantId, opt) {
  if (nav.setInapoi) nav.setInapoi(undefined);
  const inapoi = opt.inapoi || (() => nav && nav.inapoi && nav.inapoi());
  const titluInapoi = opt.titluInapoi || "Înapoi";
  corp.innerHTML = `
    <h2 class="pf-titlu">Facturi ${semnAjutor("F126")}</h2>
    <p class="pf-intro">Ce vrei s\u0103 faci?</p>
    <div class="firme-optiuni">
      <button class="firme-optiune" id="fac-istoric">
        <div class="firme-optiune-icon accent-albastru">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h10"/></svg>
        </div>
        <div class="firme-optiune-titlu">Istoric facturi</div>
        <div class="firme-optiune-desc">Facturile emise \u0219i primite</div>
      </button>
      <button class="firme-optiune" id="fac-scadentar">
        <div class="firme-optiune-icon accent-roz">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
        </div>
        <div class="firme-optiune-titlu">Scaden\u021bar</div>
        <div class="firme-optiune-desc">Facturi ne\u00eencasate: restante \u0219i care scad cur\u00e2nd</div>
      </button>
      <button class="firme-optiune" id="fac-emite" data-actiune="POST /tenants/{tenant_id}/facturi/emite">
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
      ${!opt.client ? `<button class="firme-optiune" id="fac-primite">
        <div class="firme-optiune-icon accent-albastru">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/></svg>
        </div>
        <div class="firme-optiune-titlu">Facturi primite (SPV)</div>
        <div class="firme-optiune-desc">De la furnizori — de validat înainte de cheltuieli</div>
      </button>` : ""}
      ${!opt.client ? `<button class="firme-optiune" id="fac-recurente">
        <div class="firme-optiune-icon accent-recomanda">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 3v5h-5"/></svg>
        </div>
        <div class="firme-optiune-titlu">Facturi recurente</div>
        <div class="firme-optiune-desc">\u0218abloane emise automat lunar</div>
      </button>` : ""}
    </div>`;
  corp.querySelector("#fac-istoric").addEventListener("click", () => nav.mergi("Istoric facturi", (c) => istoricFacturi(c, nav, tenantId, opt)));  // faza_b_traseu_v1
  corp.querySelector("#fac-scadentar").addEventListener("click", () => nav.mergi("Scadențar", (c) => scadentarEcran(c, nav, tenantId, opt)));  // f131_scadentar_v1
  corp.querySelector("#fac-emite").addEventListener("click", () => nav.mergi("Emite factur\u0103", (c) => emiteFactura(c, nav, tenantId, opt)));
  corp.querySelector("#fac-model").addEventListener("click", () => nav.mergi("Model factur\u0103", (c) => modelFactura(c, nav, tenantId, opt)));
  corp.querySelector("#fac-primite")?.addEventListener("click", () => nav.mergi("Facturi primite", (c) => primiteSPV(c, nav, tenantId, opt)));  // [efactura_primite_v1] F126 four-eyes
  corp.querySelector("#fac-recurente")?.addEventListener("click", () => nav.mergi("Facturi recurente", (c) => listaRecurente(c, nav, tenantId, opt)));
}  // fac_recurente_v1


// ---------- FACTURI PRIMITE din SPV — four-eyes (F126, [efactura_primite_v1]) ----------
// Anatomia ecranului de bon OCR: date parsate (nu XML brut), cont sugerat editabil (om confirma),
// Valideaza (buton-verde) / Respinge (motiv in-ecran), XML brut la click. Fara confirm/alert.
async function primiteSPV(corp, nav, tenantId, opt) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  let lista = [], categorii331 = [];
  try { const r = await api.get(`/tenants/${tenantId}/facturi-primite`); lista = (r && r.primite) || []; categorii331 = (r && r.categorii_331) || []; } catch { corp.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca facturile primite din SPV.</p>`; return; }
  // [deficiența 273a/b, lotul 6] starea SPV a firmei (conectată? verificată când? ce a răspuns ANAF?), „Verifică acum în SPV” și importul
  // manual XML UBL. „apar aici automat” se spune NUMAI când firma chiar e citită automat (conectată și cu drept).
  corp.innerHTML = `
    <h2 class="pf-titlu">Facturi primite din SPV ${semnAjutor("F043")}</h2>
    <div id="fp-spv" style="margin-bottom:10px"></div>
    <p class="pf-intro" id="fp-actiuni">
      <button class="buton-secundar" id="fp-verifica" data-actiune="POST /tenants/{tenant_id}/spv/verifica-acum">Verifică acum în SPV</button>
      <label class="buton-secundar" style="margin-left:6px" data-actiune="POST /tenants/{tenant_id}/facturi-primite/import-xml">Importă XML UBL
        <input type="file" id="fp-xml" accept=".xml,.zip" multiple hidden aria-label="Fișier XML UBL al facturii primite"></label>
    </p>
    <div id="fp-mesaj"></div>
    <div id="fp-lista"></div>`;
  const zLista = corp.querySelector("#fp-lista"), zMsg = corp.querySelector("#fp-mesaj");
  // butoanele se leagă înaintea cererii de stare (un clic dat cât se citește starea nu se pierde — `core/test_legari_await.py`)
  corp.querySelector("#fp-verifica").addEventListener("click", async (ev) => {
    const b = ev.currentTarget;
    b.disabled = true;
    arataMesaj(zMsg, "Se citește SPV…", "info");
    try {
      const r = await api.post(`/tenants/${tenantId}/spv/verifica-acum`, {});
      const c = r.citire || {};
      const txt = c.eroare ? `ANAF a răspuns: „${c.eroare}”.` : `Citit din SPV: ${cate(c.mesaje || 0, "factură primită", "facturi primite")} în ultimele ${cate(c.zile, "zi", "zile")}; cele noi sunt în listă.`;
      primiteSPV(corp, nav, tenantId, opt).then(() => arataMesaj(corp.querySelector("#fp-mesaj"), txt, c.eroare ? "avert" : "ok"));
    } catch (e) { arataMesaj(zMsg, e.mesaj || "Citirea din SPV n-a mers.", "eroare"); b.disabled = false; }
  });
  corp.querySelector("#fp-xml").addEventListener("change", async (ev) => {
    const fs = [...ev.target.files];
    if (!fs.length) return;
    const fd = new FormData();
    fs.forEach((f) => fd.append("fisiere", f));
    try {
      const r = await api.postForm(`/tenants/${tenantId}/facturi-primite/import-xml`, fd);
      const txt = [`${cate(r.importate, "factură importată", "facturi importate")} în lista de validat`
        + (r.deja ? `; ${cate(r.deja, "era deja", "erau deja")} în listă` : "") + ".", ...(r.erori || [])].join("\n");
      primiteSPV(corp, nav, tenantId, opt).then(() => arataMesaj(corp.querySelector("#fp-mesaj"), txt, (r.erori || []).length ? "avert" : "ok"));
    } catch (e) { arataMesaj(zMsg, e.mesaj || "Importul n-a mers.", "eroare"); }
    ev.target.value = "";
  });
  const st = await randeazaStareSpv(corp.querySelector("#fp-spv"), nav, tenantId);
  const automat = !!(st && st.conectat && st.are_drept !== false);
  zLista.innerHTML = !lista.length
    ? `<div class="stare-goala">Nicio factură primită de validat.${automat ? " Facturile de la furnizori apar aici automat din SPV; le validezi înainte să intre în cheltuieli." : " Până la conectarea SPV, le încarci cu „Importă XML UBL”."}</div>`
    : `<p class="pf-intro">De la furnizori · de validat înainte de cheltuieli.</p>
    <div class="pf-lista zebra-lista">${lista.map((p) => `
      <button class="buton-secundar pf-frand fac-primita-btn" data-id="${p.id}">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(p.furnizor || p.cif_emitent || "—")}${p.numar ? " · " + esc(p.numar) : ""}</div>
          <div class="pf-frand-sub">${p.data ? dataRo(p.data) : ""}${p.parsabila ? "" : ' · <span style="color:var(--rosu)">neparsabilă</span>'}${p.de_completat && p.de_completat.length ? ' · de completat: ' + esc(p.de_completat.join(", ")) : ""}</div>
        </div>
        <span class="pf-frand-suma">${p.total ? bani(p.total) + " " + (p.moneda || "lei") : ""}</span>
      </button>`).join("")}</div>`;
  corp.querySelectorAll(".fac-primita-btn").forEach((b) => b.addEventListener("click", () => {
    const p = lista.find((x) => String(x.id) === b.dataset.id);
    nav.mergi("Validare factură", (c) => primitaDetaliu(c, nav, tenantId, p, opt, categorii331));
  }));
}

function primitaDetaliu(corp, nav, tenantId, p, opt, categorii331 = []) {
  const linii = p.linii || [];
  // [deficiența 418a] statutul furnizorului aflat din XML / ANAF (serverul): se arată cu sursa, nu se cere; numai ce nu s-a putut afla se alege
  const st = p.statut_furnizor || {};
  const afla = (v, sursa, eticheta) => `<input class="camp-input" readonly aria-readonly="true" aria-label="${esc(eticheta)}" value="${v ? "Da" : "Nu"}"><span class="camp-ajutor">Aflat din ${esc(sursa)}.</span>`;
  corp.innerHTML = `
    <h2 class="pf-titlu">Factură primită · ${esc(p.numar || "—")}</h2>
    ${!p.parsabila ? `<div class="caseta-atentie" style="margin:0 0 12px"><div class="ca-mesaj">XML neparsabil — verifică XML-ul brut înainte de validare.</div></div>` : ""}
    <div class="grila-doc" style="grid-template-columns:2fr 1fr 1fr 1fr">
      <label class="camp"><span class="camp-eticheta">Furnizor</span><input class="camp-input" value="${esc((p.furnizor || "") + (p.cif_emitent ? " · " + p.cif_emitent : ""))}" readonly aria-label="Furnizor"></label>
      <label class="camp"><span class="camp-eticheta">Data</span><input class="camp-input" value="${p.data ? dataRo(p.data) : ""}" readonly aria-label="Data"></label>
      <label class="camp"><span class="camp-eticheta">TVA</span><input class="camp-input" value="${esc(p.tva || "")}" readonly aria-label="TVA"></label>
      <label class="camp"><span class="camp-eticheta">Total</span><input class="camp-input" value="${esc(p.total || "")}" readonly aria-label="Total"></label>
    </div>
    <div style="margin-top:10px"><div class="camp-eticheta">Linii</div>
      <span class="camp-ajutor">Clasifică destinația TVA a fiecărei linii importate: <b>taxabilă</b> (deducere integrală, implicit), <b>scutită</b> (fără deducere), <b>mixtă</b> (intră în pro-rata, art. 300 alin. (5)). Faptul importat rămâne neschimbat — doar îl clasifici.</span>
      ${linii.map((l, i) => `<div class="pf-linie-clasif" style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:4px">
        <span class="pf-frand-sub" style="flex:1 1 200px">${esc(l.descriere)} · ${esc(cantitate(l.cantitate))} × ${esc(bani(l.pret))} · ${esc(l.cota)}%</span>
        <select class="camp-input pr-dest" data-i="${i}" aria-label="Destinație TVA linie" style="flex:0 0 auto;width:auto">
          <option value="taxabil" selected>Taxabilă</option>
          <option value="scutit">Scutită</option>
          <option value="mixt">Mixtă</option>
        </select>
        <input class="camp-input pr-cont-linie" data-i="${i}" id="pr-cont-l${i}" placeholder="contul facturii" aria-label="Contul liniei ${i + 1}" style="flex:0 0 130px;width:130px">
      </div>`).join("") || '<div class="pf-frand-sub">—</div>'}
      ${linii.length > 1 ? '<span class="camp-ajutor">Contul liniei: gol = contul facturii de mai jos. O linie de altă natură (cartea de birou lângă marfă) se contează pe contul ei; numai liniile pe un cont de stoc (371 / 301–303) intră în stoc.</span>' : ""}</div>
    <div class="grila-doc" style="grid-template-columns:2fr 1fr;margin-top:12px">
      <label class="camp"><span class="camp-eticheta">Contul facturii (sugerat, confirmă): cheltuială, sau 371 / 301–303 la marfă și materiale</span><input class="camp-input" id="pr-cont" value="${esc(p.cont_sugerat || "")}" placeholder="ex. 628 sau 371" aria-label="Contul facturii"></label>
    </div>
    <div class="grila-doc" style="grid-template-columns:2fr 1fr;margin-top:8px">
      <!-- [lotul 07.10 B, DS cap.17] DA/NU situațional: ales de om (căsuța nebifată răspundea „Nu” în locul lui) -->
      <label class="camp"><span class="camp-eticheta">Furnizorul aplică TVA la încasare (deducere amânată până la plată, art. 297 alin. (2))${st.tva_la_incasare == null ? '<span class="oblig">*</span>' : ""}</span>
        ${st.tva_la_incasare == null ? selectDaNu('id="pr-furnizor-incasare"', null, "Furnizor cu TVA la încasare") + '<span class="camp-ajutor">ANAF nu a răspuns: alege.</span>' : afla(st.tva_la_incasare, st.sursa_incasare, "Furnizor cu TVA la încasare")}</label>
      <label class="camp"><span class="camp-eticheta">Țara furnizorului (ISO)</span><input class="camp-input" id="pr-tara" value="${esc(((p.cif_emitent || "").match(/^[A-Za-z]{2}/) || ["RO"])[0].toUpperCase())}" placeholder="RO" aria-label="Țara furnizorului"></label>
    </div>
    <!-- [deficiența 273c] ce nu vine din XML: de completat înainte de validare -->
    <div class="grila-doc" style="grid-template-columns:2fr 1fr;margin-top:8px">
      <label class="camp"><span class="camp-eticheta">Furnizorul e înregistrat în scopuri de TVA (D394 îl declară după tip)${st.platitor_tva == null ? '<span class="oblig">*</span>' : ""}</span>
        ${st.platitor_tva == null ? selectDaNu('id="pr-platitor"', null, "Furnizorul e înregistrat în scopuri de TVA") + '<span class="camp-ajutor">ANAF nu a răspuns, iar XML-ul n-are codul de TVA al furnizorului: alege.</span>' : afla(st.platitor_tva, st.sursa_platitor, "Furnizorul e înregistrat în scopuri de TVA")}</label>
      ${p.taxare_inversa ? `<label class="camp"><span class="camp-eticheta">Categoria produsului cu taxare inversă (art.331; de completat — codul din D394)<span class="oblig">*</span></span>
        <select class="camp-input" id="pr-c331" aria-label="Categoria art.331"><option value="">— alege —</option>${categorii331.map((c) => `<option value="${esc(c)}">${esc(c.replace(/_/g, " "))}</option>`).join("")}</select></label>` : ""}
    </div>
    <div style="margin-top:14px">
      <button class="buton-verde" id="pr-valideaza" data-actiune="POST /tenants/{tenant_id}/facturi-primite/{primita_id}/valideaza">Validează (scrie nota pe contul ales)</button>
      <button data-actiune="POST /tenants/{tenant_id}/facturi-primite/{primita_id}/respinge" class="btn-link" id="pr-respinge" style="margin-left:10px">Respinge</button>
      <span class="btn-link" id="pr-xml" style="margin-left:10px">Vezi XML brut</span>
    </div>
    <div id="pr-zona" style="margin-top:10px"></div>
    <div id="pr-xml-zona" style="margin-top:10px"></div>`;
  const zona = corp.querySelector("#pr-zona");
  propuneNumeAnaf(corp.querySelector("#pr-zona"), p.fisa_vs_anaf, tenantId, { fel: "furnizori", pre: "pr" });   // [lotul 11, 444] numele ANAF vs fișa furnizorului
  corp.querySelector("#pr-valideaza").addEventListener("click", () => {
    curataEroriCamp(corp);
    if (cereAlegerile(corp, ["#pr-furnizor-incasare", "#pr-platitor", ...(p.taxare_inversa ? ["#pr-c331"] : [])])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    if (!(corp.querySelector("#pr-tara").value || "").trim()) { eroareCamp(corp, "pr-tara", "Scrie țara furnizorului (codul ISO, ex. RO)."); return; }
    confirmaCaseta(zona, "Validezi factura? Nota se scrie pe contul ales (la un cont de stoc, cu intrarea în stoc) și intră în evidența contabilă.", async () => {
      try {
        const _tara = corp.querySelector("#pr-tara").value.trim().toUpperCase();   // dedusă din CIF-ul emitentului, vizibilă (DS cap.17)
        const _dest = Array.from(corp.querySelectorAll(".pr-dest")).map((s) => s.value);  // [A12b] destinatie TVA per linie, ordinea liniilor
        // [decizia 08.10 pct.2] factura de marfă cu NIR „fără factură” nelegat la același furnizor: serverul cere alegerea
        const r = await cuLegareaNir(zona, "POST /tenants/{tenant_id}/facturi-primite/{primita_id}/valideaza", (alegere) =>
          api.post(`/tenants/${tenantId}/facturi-primite/${p.id}/valideaza`, {
            cont: corp.querySelector("#pr-cont").value.trim(),
            furnizor_tva_incasare: daNu(corp.querySelector("#pr-furnizor-incasare")),  // [B1 D300] ales de om
            tert_platitor_tva: daNu(corp.querySelector("#pr-platitor")),   // [273c] tipul furnizorului în D394
            categorie_331: p.taxare_inversa ? corp.querySelector("#pr-c331").value : null,
            tert_tara: _tara,
            destinatii: _dest, conturi: Array.from(corp.querySelectorAll(".pr-cont-linie")).map((x) => x.value.trim()),   // [418b] contul liniei
            ...alegere }));
        arataMesaj(zona, "Validată. Cheltuiala creată din factura " + (p.numar || "fără număr") + (p.data ? " din " + dataRo(p.data) : "") + ".", "ok");   // [258] factura cum o arată lista, nu id-ul ei
        butonInapoi(zona, nav);   // [418c / 410, DS cap.27] confirmarea rămâne; înapoi la cererea omului
      } catch (e) { arataRefuzul(corp, e, zona); }   // [lotul 11, 440] câmpurile refuzului lângă ele, restul în zonă
    }, { textOk: "Validează" });
  });
  corp.querySelector("#pr-respinge").addEventListener("click", () => {
    zona.innerHTML = `<label class="camp"><span class="camp-eticheta">Motiv respingere<span class="oblig">*</span></span><input class="camp-input" id="pr-motiv" aria-label="Motiv respingere"></label>
      <button class="buton-secundar" id="pr-respinge-ok" data-actiune="POST /tenants/{tenant_id}/facturi-primite/{primita_id}/respinge" style="margin-top:8px">Respinge factura</button>`;
    corp.querySelector("#pr-respinge-ok").addEventListener("click", async () => {
      const motiv = corp.querySelector("#pr-motiv").value.trim();
      curataEroriCamp(corp);
      if (!motiv) { eroareCamp(corp, "pr-motiv", "Scrie motivul respingerii."); return; }   // [lotul 11, 440] lângă câmp
      try {
        await api.post(`/tenants/${tenantId}/facturi-primite/${p.id}/respinge`, { motiv });
        arataMesaj(zona, "Respinsă (rămâne în istoric).", "ok");
        butonInapoi(zona, nav);   // [418c / 410, DS cap.27]
      } catch (e) { arataRefuzul(corp, e, zona); }   // [lotul 11, 440]
    });
  });
  corp.querySelector("#pr-xml").addEventListener("click", async () => {
    const xz = corp.querySelector("#pr-xml-zona");
    try {
      const r = await api.get(`/tenants/${tenantId}/facturi-primite/${p.id}/xml`);
      // [lotul 10, 421 / 424] cutia XML-ului canonică (`.dec-xml-pre`: rândurile se rup, deci nu derulează lateral), nu una scrisă inline
      xz.innerHTML = `<pre class="dec-xml-pre">${esc(r.xml || "")}</pre>`;
    } catch (e) { arataMesaj(xz, e.mesaj || "nu s-a putut încărca XML-ul", "eroare"); }
  });
}

// [retest 08.10, completarea pct.1, comanda Costin] „starea de încasare (încasată / parțial / neîncasată) trebuie să fie vizibilă pe
// factură și în lista «Istoric facturi»” — o singură etichetare, din `stare_incasare` (serverul, `facturi_api._cu_stare_incasare`);
// la factura primită, aceeași stare spusă din partea firmei: plătită / plătită parțial / neplătită.
export function etichetaIncasare(f) {
  const s = f.stare_incasare;
  if (!s) return "";
  const primita = f.directie === "primita";
  if (s.stare === "stornata") return "stornată";   // [416] stornată integral: nu mai e nimic de încasat
  if (s.stare === "incasata") return primita ? "plătită" : "încasată";
  if (s.stare === "partial") return `${primita ? "plătită parțial" : "încasată parțial"}: ${bani(s.incasat)} din ${bani(s.total)} lei`;
  return primita ? "neplătită" : "neîncasată";
}

// [deficiența 275b, lotul 6] Starea în SPV a facturii emise, cu termenul de transmitere (OUG 120/2021 art.10 alin.(7): 5 zile lucrătoare
// de la emitere) — o singură definiție pentru listă și detaliu (`facturi_api._cu_stare_spv`).
export function etichetaSpv(f) {
  const s = f.stare_spv;
  if (!s) return "";
  const ce = { netrimisa: "netrimisă în SPV", trimisa: "trimisă în SPV", acceptata: "acceptată în SPV", respinsa: "respinsă în SPV" }[s.stare] || s.stare;
  // [deficiența 307] clientul nestabilit în România (fără cod de TVA românesc): transmiterea nu e obligatorie — fără termen
  if (s.obligatorie === false) return s.stare === "netrimisa" ? "netrimisă în SPV · nu e obligatorie (clientul nu e stabilit în România)" : ce;
  const termen = s.stare === "netrimisa" && s.termen ? ` · termen de transmitere în SPV ${dataRo(s.termen)}${s.depasit ? " (depășit)" : ""}` : "";
  return ce + termen;
}

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
    } catch { corp.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca facturile emise.</p>`; return; }
    // [cap.23, 21.08.2026] ACTUL DE ÎNCHIDERE a lunii pe facturi. Cât timp luna nu e închisă, evidența
    // ei e informativă — iar semaforul nu se poate sprijini pe ea când spune că o declarație nu se
    // datorează. Nu se afișează în portalul clientului (închiderea e act de contabil).
    let per = null;
    if (!opt.client) {
      try { per = await api.get(`/tenants/${tenantId}/facturi/perioada?an=${an}&luna=${luna}`); }
      catch { per = null; }
    }
    const maiSunt = lista.length > afisate;
    if (maiSunt) lista = lista.slice(0, afisate);
    let corpuri = !lista.length
      ? `<div class="stare-goala">Nicio factur\u0103 \u00een luna aceasta.</div>`
      : lista.map((f) => {
          const suma = f.total != null ? bani(f.total) + " " + (f.moneda || "lei") : "";
          const dir = dirEticheta(f.directie);
          const storno = f.storno_din_id ? ' \u00b7 <span class="fac-storno-tag">storno</span>' : "";
          const tipTag = f.tip && f.tip !== "factura" ? ` \u00b7 <span class="fac-storno-tag">${f.tip}</span>` : "";
          const incasare = f.stare_incasare ? " \u00b7 " + esc(etichetaIncasare(f)) : "";   // [retest 08.10, completarea pct.1]
          const spv = f.stare_spv ? ` \u00b7 <span class="${f.stare_spv.depasit || f.stare_spv.stare === "respinsa" ? "msg-avert" : ""}">${esc(etichetaSpv(f))}</span>` : "";   // [275b]
          return `
        <button class="buton-secundar pf-frand fac-frand-btn" data-id="${f.id}">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">${f.numar ? esc(numarCuSerie(f.serie, f.numar)) : "\u2014"}${f.tert_nume ? " \u00b7 " + esc(f.tert_nume) : ""}</div>
            <div class="pf-frand-sub">${dataRo(f.data_emitere)}${dir ? " \u00b7 " + dir : ""}${storno}${tipTag}${incasare}${spv}</div>
          </div>
          <span class="pf-frand-suma">${suma}</span>
          ${(!opt.client && !f.nota_contare) ? `<span class="btn-link fac-cont" data-actiune="POST /tenants/{tenant_id}/facturi/{factura_id}/contabilizeaza" data-cid="${f.id}" style="margin-left:8px">Conteaz\u0103</span>` : ""}
        </button>`;
        }).join("");
    const dataInch = per && per.confirmat_la ? dataRo(String(per.confirmat_la).slice(0, 10)) : "";
    // [08.10.2026, retest pct.11] „«Închide luna» apare și în Istoric facturi — un singur loc, cardul.” Aici rămâne numai starea;
    // închiderea și redeschiderea evidenței se fac din cardul „Închidere lună” al firmei.
    const blocInchidere = !per ? "" : `<div class="caseta-info"><span class="ci-mesaj"><span style="color:var(${per.confirmat ? "--verde" : "--gri"})">\u25cf</span> ${per.confirmat
      ? `Eviden\u021ba facturilor e \u00eenchis\u0103${dataInch ? " la " + dataInch : ""} \u2014 e complet\u0103; semaforul se poate sprijini pe ea.`
      : "Eviden\u021ba facturilor e deschis\u0103 \u2014 informativ\u0103 p\u00e2n\u0103 la \u00eenchidere."} Se \u00eenchide \u0219i se redeschide din cardul \u201e\u00cenchidere lun\u0103\u201d al firmei.</span></div>`;
    corp.innerHTML = `
      <h2 class="pf-titlu">Istoric facturi</h2>
      <p class="pf-intro">Luna ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")}
        <button class="buton-secundar" id="fac-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="buton-secundar" id="fac-next">luna \u2192</button>
        <button class="buton-secundar" id="fac-saga-luna" data-actiune="POST /tenants/{tenant_id}/facturi/export-saga" style="margin-left:12px">Export SAGA lun\u0103</button>
        <button class="buton-secundar" id="fac-winmentor-luna" data-actiune="POST /tenants/{tenant_id}/facturi/export-winmentor">Export WinMentor lun\u0103</button>
        ${maiSunt ? '<button class="buton-secundar" id="fac-mai-multe" style="margin-left:12px">Vezi \u0219i facturile mai vechi din aceast\u0103 lun\u0103</button>' : ""}</p>
      ${blocInchidere}
      <div id="fac-saga-zona"></div>
      <div class="pf-lista zebra-lista">${corpuri}</div>`;
    corp.querySelector("#fac-mai-multe")?.addEventListener("click", () => { afisate += 10; deseneaza(); });
    corp.querySelector("#fac-prev").addEventListener("click", () => { afisate = 10; luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#fac-next").addEventListener("click", () => { afisate = 10; luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    corp.querySelector("#fac-saga-luna")?.addEventListener("click", async () => {  // [export_saga_v1] F171
      const zona = corp.querySelector("#fac-saga-zona");
      try {
        // [R45] POST: exportul e un act — se pastreaza ce s-a exportat si cand.
        await descarca(`/tenants/${tenantId}/facturi/export-saga?an=${an}&luna=${luna}`,
                       `export_saga_${an}_${String(luna).padStart(2, "0")}.zip`, { metoda: "POST" });
        arataMesaj(zona, "Arhivă SAGA descărcată (un XML per factură). În SAGA: Diverse → Import date din fișiere generate.", "ok");
      } catch (e) { arataMesaj(zona, (e && (e.mesaj || e.message)) || "eroare", "eroare"); }
    });
    corp.querySelector("#fac-winmentor-luna")?.addEventListener("click", async () => {  // [export_winmentor_v1] F187
      const zona = corp.querySelector("#fac-saga-zona");
      const btn = corp.querySelector("#fac-winmentor-luna");
      const _t = btn.textContent; btn.disabled = true; btn.textContent = "Se generează…";  // cap.1 feedback async
      try {
        // [R45] POST, acelasi motiv ca la SAGA.
        await descarca(`/tenants/${tenantId}/facturi/export-winmentor?an=${an}&luna=${luna}`,
                       `export_winmentor_${an}_${String(luna).padStart(2, "0")}.zip`, { metoda: "POST" });
        arataMesaj(zona, "Arhivă WinMentor descărcată (Facturi.txt + Articole.txt). În WinMentor: MENTOR → INTERNE → Import date din alte aplicații → Facturi ieșire.", "ok");
      } catch (e) { arataMesaj(zona, (e && (e.mesaj || e.message)) || "eroare", "eroare"); }
      finally { btn.disabled = false; btn.textContent = _t; }
    });
    corp.querySelectorAll(".fac-cont").forEach((b) => b.addEventListener("click", async (ev) => {
      ev.stopPropagation();
      const _zl = document.createElement("div");   // [decizia 08.10 pct.2] caseta alegerii NIR-ului, sub rândul facturii
      (b.closest(".fac-frand-btn") || b).after(_zl);   // nu ÎN rând: rândul e un <button>, iar caseta are câmpuri
      try {
        const url = `/tenants/${tenantId}/facturi/${b.dataset.cid}/contabilizeaza`;
        let q = "";   // alegerea NIR-ului, păstrată și pentru confirmarea de mai jos
        let r = await cuLegareaNir(_zl, "POST /tenants/{tenant_id}/facturi/{factura_id}/contabilizeaza", (alegere) => {
          q = interogareLegare(alegere);
          return api.post(url + (q ? "?" + q : ""), {});
        });
        if (r && r.cod === "NESCHIMBATA") {
          // [S3] aceeași notă ca cea respinsă: avertisment cu motivul + confirmare explicită (nu blocaj)
          confirmaCaseta(b.parentElement || b, r.mesaj, async () => {
            try {
              r = await api.post(url + "?confirma=true" + (q ? "&" + q : ""), {});
              b.outerHTML = `<span class="tip-desc" style="color:var(--verde);margin-left:8px">${stareNota(r)} ${esc(r.nota_eticheta || "")}</span>`;
            } catch (e2) { arataMesaj(b.parentElement || corp, (e2 && e2.mesaj) || "eroare", "eroare"); }
          }, { textOk: "Retrimite fără schimbări" });
          return;
        }
        b.outerHTML = `<span class="tip-desc" style="color:var(--verde);margin-left:8px">${stareNota(r)} ${esc(r.nota_eticheta || "")}</span>`;
      } catch (e) {
        b.outerHTML = `<span class="tip-desc pe-randuri" style="color:var(--galben-text);margin-left:8px">${esc((e.mesaj || "eroare"))}</span>`;
      } finally { _zl.remove(); }
    }));
    corp.querySelectorAll(".fac-frand-btn").forEach((b) => {
      b.addEventListener("click", () => nav.mergi("Factur\u0103", (c) => detaliiFactura(c, nav, tenantId, b.dataset.id, opt)));  // faza_b_traseu_v1
    });
  };
  deseneaza();
}

// ---------- SCADENȚAR (F131) ----------
async function scadentarEcran(corp, nav, tenantId, opt) {
  // Semafor stare factura (DS cap.8): rosu restanta -> galben scade curand -> verde in termen.
  // Gradientele dot mirror tiparul din control.js (nuantele deschise sunt permise in dot:, HEX_SEMAFOR).
  const SEM = {
    restanta:      { dot: "radial-gradient(circle at 65% 30%, #ff8a80, var(--rosu-semafor) 60%)" },
    scade_curand:  { dot: "radial-gradient(circle at 65% 30%, #f0cd7a, var(--galben) 60%)" },
    in_termen:     { dot: "radial-gradient(circle at 65% 30%, #6fc494, var(--verde) 60%)" },
    fara_scadenta: { dot: "var(--gri-semafor)" },
  };
  corp.innerHTML = `<p class="ecran-nota">Se încarcă scadențarul…</p>`;
  let d = { linii: [], rezumat: {}, clienti: [] };
  try { d = await api.get(`/tenants/${tenantId}/scadentar`); }
  catch { corp.innerHTML = `<p class="ecran-nota">Nu s-a putut încărca scadențarul.</p>`; return; }
  const rez = d.rezumat || {};
  let vedere = "facturi";

  const aziISO = dataIso();
  const randFacturi = () => {
    if (!(d.linii || []).length) return `<div class="stare-goala">Nicio factură emisă neîncasată.</div>`;
    return d.linii.map((l) => {
      const s = SEM[l.stare] || SEM.fara_scadenta;
      const sub = l.stare === "restanta" ? `${cate(-l.zile, "zi de întârziere", "zile de întârziere")}`
        : l.stare === "scade_curand" ? `scade în ${cate(l.zile, "zi", "zile")}`
        : l.stare === "fara_scadenta" ? "fără scadență în sistem"
        : `scadență ${dataRo(l.data_scadenta)}`;
      // supapa per factura - doar cand notificarile sunt active (altfel n-ar avea efect)
      let valva = "";
      if (d.optin) {
        const amanat = l.notificare_amanata_pana && l.notificare_amanata_pana >= aziISO;
        valva = l.notificare_stop ? ` · <b>notificări oprite</b> <span class="btn-link" data-reia="${l.id}" data-actiune="PUT /tenants/{tenant_id}/facturi/{factura_id}/notificare">reia</span>`
          : amanat ? ` · amânat până ${dataRo(l.notificare_amanata_pana)} <span class="btn-link" data-reia="${l.id}" data-actiune="PUT /tenants/{tenant_id}/facturi/{factura_id}/notificare">reia</span>`
          : ` · <span class="btn-link" data-stop="${l.id}" data-actiune="PUT /tenants/{tenant_id}/facturi/{factura_id}/notificare">nu notifica</span> <span class="btn-link" data-amana="${l.id}" data-actiune="PUT /tenants/{tenant_id}/facturi/{factura_id}/notificare">amână 30 zile</span>`;
      }
      return `
      <div class="mig-frand" style="cursor:default">
        <span class="cf-dot" style="background:${s.dot};flex-shrink:0"></span>
        <div class="mig-frand-text">
          <div class="mig-frand-nume">${l.numar || "—"}${l.tert_nume ? " · " + esc(l.tert_nume) : ""}</div>
          <div class="mig-frand-sub">${sub}${valva}</div>
        </div>
        <span class="pf-frand-suma">${bani(l.suma)} ${l.moneda || "lei"}</span>
      </div>`;
    }).join("");
  };

  const randClienti = () => {
    if (!(d.clienti || []).length) return `<div class="stare-goala">Niciun client cu facturi neîncasate.</div>`;
    return d.clienti.map((c) => {
      const rest = Number(c.restant) > 0 ? `<span style="color:var(--rosu)">${bani(c.restant)} restant</span> · ` : "";
      const fara = c.email ? "" : " · fără email";
      return `
      <div class="mig-frand" style="cursor:default">
        <div class="mig-frand-text">
          <div class="mig-frand-nume">${esc(c.nume || c.cui || "—")}</div>
          <div class="mig-frand-sub">${cate(c.nr, "factură neîncasată", "facturi neîncasate")}${fara}</div>
        </div>
        <span class="pf-frand-suma">${rest}${bani(c.sold)} lei</span>
      </div>`;
    }).join("");
  };

  const reincarca = async () => { try { d = await api.get(`/tenants/${tenantId}/scadentar`); } catch {} deseneaza(); };
  const supapa = async (fid, body) => {
    try { await api.put(`/tenants/${tenantId}/facturi/${fid}/notificare`, body); await reincarca(); }
    catch (e) { arataRefuzul(corp, e, corp.querySelector("#sc-msg")); }   // [lotul 11, 440]
  };

  const deseneaza = () => {
    corp.innerHTML = `
      <h2 class="pf-titlu">Scadențar</h2>
      <label class="set-bifa" style="margin:0 0 10px"><input type="checkbox" id="sc-optin" data-actiune="PUT /tenants/{tenant_id}/scadentar/opt-in"${d.optin ? " checked" : ""}> <span>Trimite automat notificări de plată clienților, în numele firmei</span></label>
      <div id="sc-msg"></div>
      <div class="cf-sumar">
        <span class="cf-pastila"><span class="cf-dot" style="background:${SEM.restanta.dot}"></span>${cate(rez.restanta, "restantă", "restante")}</span>
        <span class="cf-pastila"><span class="cf-dot" style="background:${SEM.scade_curand.dot}"></span>${cate(rez.scade_curand, "scadență apropiată", "scadențe apropiate")}</span>
        <span class="cf-pastila"><span class="cf-dot" style="background:${SEM.in_termen.dot}"></span>${rez.in_termen || 0} în termen</span>
      </div>
      <p class="pf-intro">
        <button class="buton-secundar" id="sc-facturi"${vedere === "facturi" ? " disabled" : ""}>Facturi neîncasate</button>
        <button class="buton-secundar" id="sc-clienti"${vedere === "clienti" ? " disabled" : ""}>Fișă client</button>
      </p>
      <div class="mig-lista zebra-lista">${vedere === "facturi" ? randFacturi() : randClienti()}</div>`;
    const chk = corp.querySelector("#sc-optin");
    chk.addEventListener("change", async () => {
      try {
        await api.put(`/tenants/${tenantId}/scadentar/opt-in`, { activ: chk.checked });
        d.optin = chk.checked;
        arataMesaj(corp.querySelector("#sc-msg"), chk.checked ? "Notificări automate active." : "Notificări dezactivate.", "ok");
        deseneaza();
      } catch (e) { chk.checked = !chk.checked; arataMesaj(corp.querySelector("#sc-msg"), e.mesaj || "Eroare.", "eroare"); }
    });
    corp.querySelector("#sc-facturi").addEventListener("click", () => { vedere = "facturi"; deseneaza(); });
    corp.querySelector("#sc-clienti").addEventListener("click", () => { vedere = "clienti"; deseneaza(); });
    corp.querySelectorAll("[data-stop]").forEach((b) => b.addEventListener("click", () => supapa(b.dataset.stop, { stop: true })));
    corp.querySelectorAll("[data-reia]").forEach((b) => b.addEventListener("click", () => supapa(b.dataset.reia, { stop: false, amanata_pana: null })));
    corp.querySelectorAll("[data-amana]").forEach((b) => b.addEventListener("click", () => {
      const pana = dataIso(new Date(Date.now() + 30 * 864e5));
      supapa(b.dataset.amana, { stop: false, amanata_pana: pana });
    }));
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

  let f = null;
  try {
    f = await api.get(`/tenants/${tenantId}/facturi/${facturaId}`);
  } catch {
    arataMesaj(corp, "Nu s-a putut încărca factura.", "eroare");
    return;
  }

  const mon = f.moneda || "RON";
  const esteValuta = mon.toUpperCase() !== "RON";
  const linii = f.linii || [];

  // linii + defalcare pe cote
  // [lotul 11, decizia 10.3] defalcarea pe cote pe regula unică (e-Factura, `tvaDocument` = `core/tva_calcul.py`): TVA-ul cotei din baza ei,
  // rotunjit o dată — aceleași cifre ca PDF-ul și XML-ul (înainte: suma TVA-urilor rotunjite pe linie)
  // [lotul 11, C82] valoarea liniei: la factura importată, BT-131 de pe factură (`valoare_neta`, exact — prețul ținut la 2 zecimale × o
  // cantitate neîntreagă nu o reface); altfel cantitate × preț. Aceeași regulă ca `tva_calcul.net_linie` (PDF-ul, nota, declarațiile).
  const _deCalcul = (l, cota) => (l.valoare_neta != null && l.valoare_neta !== ""
    ? { cantitate: 1, pret_unitar: l.valoare_neta, cota_tva: cota }
    : { cantitate: l.cantitate, pret_unitar: l.pret_unitar, cota_tva: cota });
  const peCota = tvaDocument(linii.map((l) => _deCalcul(l, Number(l.cota_tva) || 0))).pe_cote;
  const randuriLinii = linii.map((l) => {
    const cant = Number(l.cantitate) || 0;
    const pret = Number(l.pret_unitar) || 0;
    const cota = Number(l.cota_tva) || 0;
    const baza = tvaDocument([_deCalcul(l, 0)]).baza;   // valoarea netă, la ban
    return `
      <tr>
        <td class="fd-td-den">${esc(l.descriere)}</td>
        <td>${cant.toLocaleString("ro-RO")}</td>
        <td class="fd-td-um">${esc(l.um || "buc")}</td>
        <td class="fd-td-num">${_bani(pret)}</td>
        <td>${cota}%${cota === 0 && l.categorie_tva_eticheta ? `<div class="tip-micut fd-categorie">${esc(l.categorie_tva_eticheta)}</div>` : ""}</td>
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
        <div class="fd-valuta-sub">${sursaTxt} ${f.curs_bnr ? cursValutar(f.curs_bnr) : ""} ${f.data_curs ? "\u00b7 " + dataRo(f.data_curs) : ""}</div>
      </div>`;
  }

  const dir = dirEticheta(f.directie);
  // [deficiența 306] codul clientului cu eticheta lui (Cod TVA / CIF / CUI, ca pe PDF) și adresa completă (cu țara, la clientul străin)
  const partener = f.tert_nume ? `${esc(f.tert_nume)}${f.tert_cod ? ` \u00b7 ${esc(f.tert_cod_eticheta || "CUI")} ${esc(f.tert_cod)}`
    : (f.tert_cui ? " \u00b7 CUI " + esc(f.tert_cui) : "")}${f.tert_adresa_completa ? `<div class="tip-micut">${esc(f.tert_adresa_completa)}</div>` : ""}` : "";
  // STATUS_ETICHETA - sincronizat 1:1 cu core/nomenclator_status_factura.ETICHETE (interdictia 31).
  // Garda core/test_eticheta_status_factura.py pica la orice divergenta (stare fara eticheta / eticheta fara stare).
  const STATUS_ETICHETA = { emisa: "emis\u0103", importata: "importat\u0103", de_recunoscut: "de recunoscut", de_preluat: "de preluat", ciorna: "ciorn\u0103", descarcata: "desc\u0103rcat\u0103", anulata: "anulat\u0103", stornata: "stornat\u0103" };
  // [05.10.2026, comanda Costin pct.7] starea spune adevărul: „contabilizată” abia cu nota de contare VALIDATĂ; cât e ciornă,
  // „notă propusă, de validat”. Din factură se ajunge la nota ei (Registrul jurnal, luna notei).
  const nc = f.nota_contare;
  const statusTxt = f.storno_din_id ? "storno" : (f.contabilizata ? "contabilizat\u0103"
    : (nc ? "not\u0103 propus\u0103, de validat" : (STATUS_ETICHETA[f.status] || f.status || "")));
  // [lotul 10, 10.2 pct.7f, 419] factura stornat\u0103 integral (aceea\u0219i defini\u021bie ca starea \u201estornat\u0103\u201d, 416): nu mai e nimic de stornat \u0219i
  // nimic de \u00eencasat \u2014 \u201eStorneaz\u0103\u201d \u0219i \u201eEmite chitan\u021b\u0103\u201d nu se mai ofer\u0103 (serverul refuz\u0103 \u0219i el a doua stornare, `facturi_api.storneaza`)
  const stornata = !!(f.stare_incasare && f.stare_incasare.stare === "stornata");

  // [lotul 10, deficiențele 421 / 424, DS cap.9 v2.96] „rezumatul stă fix sus și acțiunea principală fix jos; se derulează doar tabelul
  // din mijloc”: antetul facturii (numărul, stările, acțiunile, zona lor de mesaj, data și partenerul) e rezumatul — rămâne lipit sus cât
  // se derulează liniile, deci rezultatul unei acțiuni („Trimite în SPV”, „Emite chitanță”) se vede și de la capătul tabelului
  corp.innerHTML = `
    <div class="fd-antet rezumat-fix">
      <div class="fd-antet-sus">
        <h2 class="pf-titlu">Factur\u0103 ${f.numar ? esc(numarCuSerie(f.serie, f.numar)) : "\u2014"}</h2>
        ${statusTxt ? `<span class="fd-stare">${esc(statusTxt)}</span>` : ""}
        ${(!opt.client && nc) ? `<button class="btn-link" id="fd-vezi-nota">nota ${esc(nc.eticheta || "")}</button>` : ""}
        <button class="buton-secundar em-buton-sec fd-pdf-btn" id="fd-pdf">PDF factur\u0103</button>
        <button data-actiune="POST /tenants/{tenant_id}/facturi/{factura_id}/email" class="buton-secundar em-buton-sec fd-email-btn" id="fd-email">Trimite pe email</button>
        ${(!opt.client && f.directie === "emisa" && !f.storno_din_id && !stornata) ? '<button data-actiune="POST /tenants/{tenant_id}/facturi/{factura_id}/storno" class="buton-secundar em-buton-sec fd-storno-btn" id="fd-storno">Storneaz\u0103</button>' : ""}
        ${(f.tip && f.tip !== "factura" && !f.transformat_in_id) ? '<button class="buton-secundar em-buton-sec" id="fd-transforma" data-actiune="POST /tenants/{tenant_id}/facturi/{factura_id}/transforma">Transform\u0103 \u00een factur\u0103</button>' : ""}
        ${f.stare_incasare ? `<span class="fd-stare${f.stare_incasare.stare === "incasata" ? " fd-stare-verde" : ""}">${esc(etichetaIncasare(f))}</span>` : ""}
        ${f.stare_spv ? `<span class="fd-stare${f.stare_spv.stare === "acceptata" ? " fd-stare-verde" : ""}" id="fd-stare-spv">${esc(etichetaSpv(f))}</span>` : ""}
        ${f.platita_la && f.plata_confirmata_de === "mock" ? '<span class="fd-stare fd-stare-galben" title="Confirmare de simulare, nu de la un procesator de pl\u0103\u021bi. Nu dovede\u0219te c\u0103 au intrat bani.">pl\u0103tit\u0103 prin SIMULARE</span>' : ""}
        <!-- [06.09.2026] Butonul «Link plata» a fost SCOS: calea de plata online e inchisa prin
             decizie — incasarea se face prin transfer bancar, confirmat din extras. Eticheta
             «platita prin SIMULARE» de mai sus RAMANE: nicio factura n-o poarta azi, dar daca
             vreuna ar purta-o vreodata, nu are voie sa treaca drept incasare obisnuita. -->
        ${(f.directie === "emisa" && f.tip === "factura" && !f.storno_din_id && !f.platita_la && !stornata) ? '<button class="buton-secundar em-buton-sec" id="fd-chitanta" data-actiune="POST /tenants/{tenant_id}/chitante">Emite chitan\u021b\u0103</button>' : ""}
        ${(f.directie === "emisa" && f.tip === "factura") ? '<button class="buton-secundar em-buton-sec" id="fd-saga">Export SAGA</button>' : ""}
        <!-- [C62] și stornarea pleacă în SPV: OUG 120/2021 art.4 alin.(10) — „Factura electronică corectată se transmite în cadrul
             aceluiași sistem național privind factura electronică RO e-Factura”; XML-ul ei trimite la factura stornată (BG-3, 417) -->
        <!-- [lotul 11, C86] factura emisă venită din XML-ul e-Factura e deja transmisă de cine a emis-o: fără „Trimite în SPV” (serverul
             refuză și el, efactura_trimitere.refuz_din_efactura), cu motivul în locul butonului — textul vine de la server -->
        ${(f.directie === "emisa" && f.tip === "factura" && f.din_efactura) ? `<span class="fd-stare" id="fd-spv-motiv">${esc(f.din_efactura)}</span>` : ""}
        ${(f.directie === "emisa" && f.tip === "factura" && !f.din_efactura) ? '<button class="buton-secundar em-buton-sec" id="fd-spv" data-actiune="POST /tenants/{tenant_id}/facturi/{factura_id}/trimite-spv">Trimite în SPV</button>' : ""}
        ${f.transformat_in_id ? `<button class="btn-link" id="fd-vezi-transformata">transformat\u0103 \u00een ${esc(f.transformat_in_numar || "factur\u0103")}</button>` : ""}
      </div>
      <div class="fd-email-zona" id="fd-email-zona"></div>
      <div class="fd-storno-zona" id="fd-storno-zona"></div>
      <div id="fd-chitanta-zona"></div>
      <div id="fd-saga-zona"></div>
      <div id="fd-spv-zona"></div>
      <div id="fd-act-rez"></div>
      <div class="fd-antet-linie">${dir ? dir.charAt(0).toUpperCase() + dir.slice(1) : ""} \u00b7 ${dataRo(f.data_emitere)}${f.data_scadenta ? " \u00b7 scaden\u021b\u0103 " + dataRo(f.data_scadenta) : ""}</div>
      ${partener ? `<div class="fd-antet-linie">${dir === "primit\u0103" ? "De la" : "C\u0103tre"}: ${partener}</div>` : ""}
      ${f.mentiune_storno ? `<div class="fd-antet-linie" id="fd-storno-din"><button class="btn-link" id="fd-vezi-stornata">${esc(f.mentiune_storno)}</button></div>` : ""}
      ${(f.mentiuni || []).map((m) => `<div class="fd-antet-linie">${esc(m)}</div>`).join("")}
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

    ${blocValuta}
    <div class="bara-fixa"><div class="fd-totaluri">   <!-- [lotul 11, decizia Costin 10.3: „Totalurile … fix”] totalurile facturii rămân jos, în vedere (DS cap.9 v2.100) -->
      ${randuriTot}
      <div class="fd-tot-rand fd-tot-final"><span>Total</span><span>${_bani(f.total, mon)}</span></div>
    </div></div>`;


  const bSaga = corp.querySelector("#fd-saga");  // [export_saga_v1] F171
  if (bSaga) bSaga.addEventListener("click", async () => {
    const zona = corp.querySelector("#fd-saga-zona");
    try {
      await descarca(`/tenants/${tenantId}/facturi/${facturaId}/export-saga`, "factura_saga.xml");
      arataMesaj(zona, "XML SAGA descărcat. În SAGA: Diverse → Import date din fișiere generate.", "ok");
    } catch (e) { arataMesaj(zona, (e && (e.mesaj || e.message)) || "eroare", "eroare"); }
  });

  const bSpv = corp.querySelector("#fd-spv");  // [efactura_send_v1] F160/F126 — trimitere e-Factura in SPV
  if (bSpv) {
    const zonaSpv = corp.querySelector("#fd-spv-zona");
    // semafor: gri = netrimisa/pending drept; galben = in prelucrare; verde = ok (recipisa); rosu = nok/eroare
    // culori de TEXT (eticheta stării SPV), nu de semafor: --galben/--gri-semafor/--rosu-semafor n-au contrast pe alb (DS cap.8 v2.70)
    const CUL = { ok: "var(--verde)", in_prelucrare: "var(--galben-text)", incarcat: "var(--galben-text)",
                  investigatie: "var(--gri)", nok: "var(--rosu)", eroare_upload: "var(--rosu)" };
    const ET = { ok: "trimisă (recipișă primită)", in_prelucrare: "în prelucrare la ANAF",
                 incarcat: "încărcată, în prelucrare la ANAF", investigatie: "blocată la ANAF — verifică în SPV",
                 nok: "respinsă de ANAF", eroare_upload: "eroare la trimitere" };
    async function pictaStareSpv() {
      let st = null;
      try { const m = await api.get(`/tenants/${tenantId}/trimiteri-spv`); st = m[String(facturaId)]; } catch {}
      if (!st || !st.stare) return;   // netrimisa -> butonul ramane gri, fara text
      const cul = CUL[st.stare] || "var(--gri)";
      bSpv.disabled = ["ok", "in_prelucrare", "incarcat", "investigatie"].includes(st.stare);  // send viu/blocat -> nu retrimite (idempotency)
      zonaSpv.innerHTML = `<span class="fd-stare" style="color:${cul}">SPV: ${ET[st.stare] || st.stare}</span>`
        + (st.error_message ? ` <span class="btn-link" id="fd-spv-det">vezi mesajul</span>` : "");
      corp.querySelector("#fd-spv-det")?.addEventListener("click", () =>
        arataMesaj(zonaSpv, st.error_message, st.stare === "nok" ? "avert" : "eroare"));
    }
    pictaStareSpv();
    bSpv.addEventListener("click", () => {
      confirmaCaseta(zonaSpv,
        "Trimiți factura în SPV (e-Factura ANAF)? Se validează întâi la ANAF — dacă structura nu e validă, nu se trimite nimic.",
        async () => {
          arataMesaj(zonaSpv, "Se validează la ANAF și se trimite…", "info");
          try {
            const r = await api.post(`/tenants/${tenantId}/facturi/${facturaId}/trimite-spv`, {});
            if (r.stare === "nevalidat") {
              arataMesaj(zonaSpv, "Structură invalidă — NU s-a trimis. ANAF:\n" + (r.erori || []).join("\n"), "avert");
            } else {
              // [lotul 10, 10.2 pct.7f — clasa lui 419: starea veche rămâne pe detaliu după act] trimiterea schimbă starea SPV a facturii:
              // detaliul se reface ACUM (eticheta „netrimisă în SPV · termen …” din antet nu mai rămâne lângă „în prelucrare”), iar
              // răspunsul stă în zona de mesaj a detaliului refăcut — nu în zona SPV, pe care starea citită o rescrie (DS cap.27 v2.94)
              const trimisa = r.stare === "incarcat" || r.stare === "in_prelucrare";
              await detaliiFactura(corp, nav, tenantId, facturaId, opt);
              arataMesaj(corp.querySelector("#fd-act-rez") || corp, trimisa
                ? "Trimisă în SPV (index " + (r.index_incarcare || "—") + "). ANAF o prelucrează; recipișa se preia separat."
                : "Răspuns ANAF:\n" + (r.erori || [r.mesaj || "eroare"]).join("\n"), trimisa ? "ok" : "avert");
            }
          } catch (e) {
            arataMesaj(zonaSpv, e.mesaj || e.message || "eroare la trimitere", "eroare");
          }
        }, { textOk: "Trimite în SPV" });
    });
  }

  // [06.09.2026] Handlerul «Link plata» a fost SCOS odata cu butonul: calea de plata online e
  // inchisa prin decizie. Un buton scos care lasa in urma codul care il asculta e o urma de
  // intentie — si o cale care se redeschide cu o singura linie de HTML.
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
      <div class="fd-tot-rand"><span>Chitan\u021ba ${esc(numarCuSerie(c.serie, String(c.numar)))} \u00b7 ${dataRo(c.data)} \u00b7 ${_bani(c.suma, "lei")}</span>
      <span><button class="btn-link" data-chpdf="${c.id}" data-actiune="GET /tenants/{tenant_id}/chitante/{chitanta_id}/pdf">PDF chitan\u021b\u0103</button></span></div>`).join("");
    zonaChit.querySelectorAll("[data-chpdf]").forEach((b) => b.addEventListener("click", async () => {
      try {
        await deschide(`/tenants/${tenantId}/chitante/${b.dataset.chpdf}/pdf`);
      } catch (e) {
        // [R131] motivul serverului, nu „reincearca": la o chitanta inexistenta a doua apasare
        // da acelasi raspuns, iar sfatul trimite omul intr-un cerc.
        arataMesaj(b.parentElement, (e && (e.mesaj || e.message)) || "eroare", "eroare");
      }
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
        <label class="camp"><span class="camp-eticheta">Data \u00eencas\u0103rii<span class="oblig">*</span></span><input class="camp-input" type="date" id="fd-chit-data" value="${dataIso()}"></label>
        <label class="camp"><span class="camp-eticheta">Suma \u00eencasat\u0103 (lei)<span class="oblig">*</span></span><input class="camp-input" type="number" step="0.01" id="fd-chit-suma" value="${rest || totalDeIncasat}"></label>
        <button class="buton-primar" id="fd-chit-ok" data-actiune="POST /tenants/{tenant_id}/chitante">Emite</button>
        <button class="btn-link" id="fd-chit-nu">Renun\u021b\u0103</button>
        <span class="msg-eroare" id="fd-chit-msg"></span>
      </div>`);
    const form = zonaChit.querySelector("#fd-chit-form");
    form.querySelector("#fd-chit-nu").addEventListener("click", () => form.remove());
    form.querySelector("#fd-chit-ok").addEventListener("click", async (ev) => {
      const b = ev.currentTarget, msg = form.querySelector("#fd-chit-msg");
      const suma = parseFloat(form.querySelector("#fd-chit-suma").value) || 0;
      const data = form.querySelector("#fd-chit-data").value;
      // [lotul 11, 440] toate câmpurile deodată, fiecare lângă el (`cereCompletate` / `eroareCamp`), nu primul în zona de jos
      curataEroriCamp(form);
      if (cereCompletate(form, [{ id: "fd-chit-data", mesaj: "Completeaz\u0103 data \u00eencas\u0103rii." }])
          | (suma <= 0 && eroareCamp(form, "fd-chit-suma", "Suma trebuie s\u0103 fie mai mare ca zero."))) return;
      b.disabled = true; b.textContent = "Se emite...";
      try {
        const r = await api.post(`/tenants/${tenantId}/chitante`, { data, suma, factura_id: facturaId });
        const av = (r && r.avertismente) || [];
        form.remove();
        // [lotul 10, 10.2 pct.7f — clasa lui 419: „rămâne «neîncasată» până la reîmprospătare”] chitanța schimbă starea de încasare:
        // detaliul se reface ACUM, de la server (starea, lista chitanțelor, „Emite chitanță” numai cât mai e ceva de încasat), iar
        // confirmarea stă în zona de mesaj a detaliului refăcut (DS cap.27 v2.93–v2.94)
        await detaliiFactura(corp, nav, tenantId, facturaId, opt);
        arataMesaj(corp.querySelector("#fd-act-rez") || corp, `Chitan\u021ba ${esc(numarCuSerie(r.serie, String(r.numar)))} a fost emis\u0103 \u0219i \u00eenregistrat\u0103 \u00een Registrul de cas\u0103.${av.length ? " Aten\u021bie: " + av.join(" ") : ""}`,
          av.length ? "avert" : "ok");
      } catch (e) {
        b.disabled = false; b.textContent = "Emite";
        arataRefuzul(form, e, msg, { campuri: { suma: "fd-chit-suma", data: "fd-chit-data" } });   // [lotul 11, 440] câmpurile serverului lângă ele
      }
    });
  });

  const btnPdf = corp.querySelector("#fd-pdf");
  if (btnPdf) {
    btnPdf.addEventListener("click", async () => {
      const txtVechi = btnPdf.textContent;
      btnPdf.disabled = true; btnPdf.textContent = "Se genereaz\u0103\u2026";
      try {
        await deschide(`/tenants/${tenantId}/facturi/${facturaId}/pdf`);
      } catch (e) {
        arataMesaj(btnPdf.parentElement, (e && (e.mesaj || e.message)) || "eroare", "eroare");   // [R131]
        btnPdf.textContent = txtVechi;
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
          <label for="fd-email-input" class="fd-email-eticheta">Trimite factura ${esc(numarCuSerie(f.serie, f.numar))} c\u0103tre:</label>
          <div class="fd-email-rand">
            <input type="email" id="fd-email-input" class="camp-input fd-email-input" placeholder="email@client.ro" value="${esc(emailPre)}">
            <button class="buton-primar fd-email-send" id="fd-email-send" data-actiune="POST /tenants/{tenant_id}/facturi/{factura_id}/email">Trimite</button>
          </div>
          <div class="em-rezultat" id="fd-email-rez"></div>
        </div>`;
      const inp = zonaEmail.querySelector("#fd-email-input");
      focusFaraSalt(inp);
      zonaEmail.querySelector("#fd-email-send").addEventListener("click", async () => {
        const rez = zonaEmail.querySelector("#fd-email-rez");
        const send = zonaEmail.querySelector("#fd-email-send");
        const email = (inp.value || "").trim();
        if (!email || email.indexOf("@") < 1 || email.indexOf(".") < 0) {
          rez.textContent = "Introdu o adres\u0103 valid\u0103."; rez.className = "em-rezultat em-rau"; focusFaraSalt(inp); return;
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

  const btnVeziNota = corp.querySelector("#fd-vezi-nota");
  if (btnVeziNota) btnVeziNota.addEventListener("click", async () => {
    const { ecranJurnal } = await import("./firme.js?v=020b99dd0c");   // dinamic: firme.js importă deja ecranul facturilor
    const [an, luna] = String(nc.data).split("-").map(Number);
    nav.deschide("Registru jurnal", (c2) => ecranJurnal(c2, nav, { id: tenantId }, { an, luna }), { lat: "tabel" });   // [394]
  });
  // [lotul 10, 10.2 pct.7e, deficiența 417] „pe ecranul de detaliu al facturii de stornare nu apare trimiterea la factura inițială (pe
  // PDF apare)”: sub client, aceeași mențiune ca pe PDF („Stornare factura F1A nr. 8 din 19.10.2026”, de la server — `facturi.
  // mentiune_storno`, CF art.330 alin.(1) lit.b: „se înscriu numărul și data facturii corectate”); clic = factura stornată
  const btnVeziStornata = corp.querySelector("#fd-vezi-stornata");
  if (btnVeziStornata) btnVeziStornata.addEventListener("click", () => detaliiFactura(corp, nav, tenantId, f.storno_din_id, opt));
  const btnVeziTransformata = corp.querySelector("#fd-vezi-transformata");
  if (btnVeziTransformata) btnVeziTransformata.addEventListener("click", () => detaliiFactura(corp, nav, tenantId, f.transformat_in_id, opt));
  const btnStorno = corp.querySelector("#fd-storno");
  const btnTransforma = corp.querySelector("#fd-transforma");
  // [C63, decizia Costin 19.10.2026: „la transformarea în factură se pune aceeași întrebare ca la orice factură, «Pleacă marfa acum?»”]
  // documentul cu articol de stoc: serverul cere răspunsul (`INTREABA_PLEACA_MARFA`, nimic scris) -> întrebarea emiterii, în zona de
  // mesaj a detaliului, apoi retrimiterea cu răspunsul (Da: marfa se descarcă o dată; Nu: stocul nu se atinge)
  // handlerul butonului cuprinde trimiterea (și retrimiterea cu răspunsul): apelul rutei stă pe elementul care o declară
  if (btnTransforma) btnTransforma.addEventListener("click", () => {
    const transforma = async (pleacaMarfa) => {
      btnTransforma.disabled = true;
      try {
        const r = await api.post(`/tenants/${tenantId}/facturi/${f.id}/transforma`, pleacaMarfa == null ? {} : { pleaca_marfa: pleacaMarfa });
        await detaliiFactura(corp, nav, tenantId, f.id, opt);
        // [C64, DS cap.27 v2.94] confirmarea peste detaliul redesenat, în zona ei — nu în locul lui; „transformată în …” e drumul spre factură
        // [lotul 11, 428] factura din proform\u0103 / aviz \u00een sistemul TVA la \u00eencasare: acela\u0219i text ca la emitere
        arataMesaj(corp.querySelector("#fd-act-rez"), `Factura ${r.numar} a fost emis\u0103${textDescarcare(r.descarcare)}${textTvaIncasare(r.contare)}.`, "ok");
      } catch (e) {
        btnTransforma.disabled = false;
        const zona = corp.querySelector("#fd-act-rez");
        if (e && e.detaliu && e.detaliu.cod === "INTREABA_PLEACA_MARFA") {
          intrebarePleacaMarfa(zona, (f.linii || []).filter((l) => l && l.articol_id).length, transforma, { da: "fd-poarta-da", nu: "fd-poarta-nu" });
          return;
        }
        if (zona) zona.innerHTML = "";   // întrebarea la care s-a răspuns nu rămâne lângă refuz
        refuzPeRand(btnTransforma, ((e && e.mesaj) || "Nu s-a putut transforma."));
      }
    };
    transforma(null);
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
      // [deficiența 419] factura care a descărcat stocul: întrebarea „marfa se întoarce?” — alegere explicită, fără răspuns implicit
      const iesiri = f.iesiri_stoc || [];
      const intrebareRetur = iesiri.length ? `
          <label class="camp" style="margin-top:10px;display:block"><span class="camp-eticheta">Marfa ieșită cu factura (${esc(iesiri.map((x) => x.articol + " × " + x.cantitate_text).join("; "))}) se întoarce în stoc?</span>
            ${selectDaNu('id="fd-storno-retur"', null, "Marfa se întoarce în stoc")}
            <span class="camp-ajutor">Da = retur: marfa revine în magazie, iar costul ieșirii se stornează. Nu = marfa rămâne la client (numai corecția valorii): stocul nu se schimbă.</span></label>` : "";
      zonaStorno.innerHTML = `
        <div class="fd-storno-box">
          <div class="fd-storno-avert" style="margin-bottom:0">Se creeaz\u0103 o factur\u0103 de stornare pentru <b>${esc(numarCuSerie(f.serie, f.numar))}</b> (valori negative, document contabil). Ac\u021biunea nu poate fi anulat\u0103.</div>
          ${intrebareRetur}
        </div>
        <div class="fd-storno-actiuni" style="margin:10px 0 14px">
          <button class="buton-primar" id="fd-storno-ok" data-actiune="POST /tenants/{tenant_id}/facturi/{factura_id}/storno">Confirm stornarea</button>
          <button class="buton-secundar" id="fd-storno-nu">Renun\u021b\u0103</button>
        </div>
        <div class="em-rezultat" id="fd-storno-rez"></div>`;
      zonaStorno.querySelector("#fd-storno-nu").addEventListener("click", () => {
        zonaStorno.dataset.deschis = ""; zonaStorno.innerHTML = "";
      });
      zonaStorno.querySelector("#fd-storno-ok").addEventListener("click", async () => {
        const rez = zonaStorno.querySelector("#fd-storno-rez");
        const ok = zonaStorno.querySelector("#fd-storno-ok");
        curataEroriCamp(zonaStorno);
        if (cereAlegerile(zonaStorno, ["#fd-storno-retur"])) return;   // [419] fără răspuns nu se trimite
        const corpStorno = iesiri.length ? { retur: daNu(zonaStorno.querySelector("#fd-storno-retur")) } : {};
        ok.disabled = true; ok.textContent = "Se storneaz\u0103\u2026";
        try {
          const r = await api.post(`/tenants/${tenantId}/facturi/${facturaId}/storno`, corpStorno);
          const retur = (r.retur || []).length ? ` Marfa a revenit în stoc: ${esc(r.retur.map((x) => x.articol + " × " + cantitate(x.cantitate, x.um)).join("; "))} (notele de retur sunt ciornă, în Registrul jurnal).` : "";
          // [lotul 10, 10.2 pct.7f, 419] „după stornare butonul rămâne «Se stornează…»; factura stornată rămâne «neîncasată» până la
          // reîmprospătare”: detaliul se reface ACUM, de la server (starea „stornată”, fără „Stornează” / „Emite chitanță”), iar confirmarea
          // se pune în zona de stornare a detaliului refăcut, nu în locul lui (DS cap.27 v2.93–v2.94: „o listă care trebuie reîmprospătată
          // se reface ACUM, iar confirmarea se pune peste ea”, „în zona de mesaj a ecranului redesenat”)
          await detaliiFactura(corp, nav, tenantId, facturaId, opt);
          const zs = corp.querySelector("#fd-storno-zona");
          if (!zs) {   // detaliul nu s-a putut reîncărca: actul a reușit, deci confirmarea se spune oricum, cu drumul spre el
            arataMesaj(corp, `Storno creat: ${r.numar || ""}. Factura nu s-a putut reîncărca; o vezi în Istoric facturi.`, "ok");
            return;
          }
          zs.innerHTML = `<div class="em-rezultat em-bun" id="fd-storno-rez">\u2713 Storno creat: <b>${esc(r.numar || "")}</b>${esc(textTvaIncasare(r.contare))}.${retur}</div>`;
          const rezNou = zs.querySelector("#fd-storno-rez");
          // [418c / 410, DS cap.27] confirmarea (și returul) rămâne pe ecran; istoricul se deschide la cererea omului
          const bi = document.createElement("button");
          bi.type = "button"; bi.className = "buton-secundar"; bi.id = "fd-spre-istoric"; bi.style.marginLeft = "10px";
          bi.textContent = "Înapoi la Istoric facturi";
          bi.addEventListener("click", () => istoricFacturi(corp, nav, tenantId, opt));
          rezNou.appendChild(bi);
        } catch (e) {
          arataRefuzul(corp, e, rez);   // [lotul 11, 440] câmpurile refuzului (returul pe linie) lângă ele, restul aici
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

  let profil = {};
  try {
    profil = await api.get(`/tenants/${tenantId}/firma-profil`);
  } catch {
    arataMesaj(corp, "Nu s-a putut încărca profilul firmei.", "eroare");
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
        <button class="buton-primar mf-salveaza" id="mf-salveaza" data-actiune="POST /tenants/{tenant_id}/firma-profil/model">Salveaz\u0103</button>
        <div class="em-rezultat" id="mf-rezultat"></div>
      </div>
      <div class="mf-preview-wrap">
        <div class="mf-preview" id="mf-preview"></div>
      </div>
    </div>`;


  const preview = corp.querySelector("#mf-preview");

  function randPreview() {
    const ff = MF_FONTURI[stare.font];
    const ac = stare.culoare;
    const nr = numarCuSerie(profil.serie_factura, String(profil.urmator_numar_factura || "1"));   // [lotul 11, 443] „FCT nr. 1”, nu „FCT1”
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
  let sabloane = [];
  try {
    const r = await api.get(`/tenants/${tenantId}/facturi-recurente`);
    sabloane = (r && r.sabloane) || [];
  } catch { corp.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca șabloanele de facturi recurente.</p>`; return; }
  randareRecurente(corp, nav, tenantId, opt, sabloane);
}

function randareRecurente(corp, nav, tenantId, opt, sabloane) {
  const inapoiMeniu = () => meniuFacturi(corp, nav, tenantId, opt);
  const corpuri = !sabloane.length
    ? `<div class="stare-goala">Niciun \u0219ablon \u00eenc\u0103.</div>`
    : sabloane.map((s) => {
        const suma = (s.linii || []).reduce((t, l) => t + (Number(l.cantitate) || 0) * (Number(l.pret_unitar) || 0), 0);
        const sumaTxt = bani(suma) + " " + (s.moneda || "RON");
        const stare = s.activ
          ? '<span style="color:var(--verde)">activ</span>'
          : '<span style="color:var(--gri)">inactiv</span>';
        return `
      <div class="pf-frand" data-id="${s.id}">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(s.tert_nume) || "\u2014"}</div>
          <div class="pf-frand-sub">ziua ${s.zi_emitere} \u00b7 ultima: ${dataRo(s.ultima_emitere) || "\u2014"} \u00b7 ${stare}</div>
        </div>
        <span class="pf-frand-suma">${sumaTxt}</span>
        <span class="btn-link fr-toggle" data-actiune="PUT /tenants/{tenant_id}/facturi-recurente/{sid}" data-id="${s.id}" data-activ="${s.activ}" style="margin-left:8px">${s.activ ? "Dezactiveaz\u0103" : "Activeaz\u0103"}</span>
        <span class="btn-link fr-sterge" data-actiune="DELETE /tenants/{tenant_id}/facturi-recurente/{sid}" data-id="${s.id}" style="margin-left:8px;color:var(--rosu)">\u0218terge</span>
      </div>`;
      }).join("");

  corp.innerHTML = `
    <h2 class="pf-titlu">Facturi recurente ${semnAjutor("F047")}</h2>
    <p class="pf-intro">\u0218abloane emise automat \u00een fiecare lun\u0103 (verificare zilnic\u0103 la 07:00).</p>
    <div class="pf-lista zebra-lista">${corpuri}</div>
    <button class="buton-primar" id="fr-add" data-actiune="POST /tenants/{tenant_id}/facturi-recurente" style="margin-top:12px">+ \u0218ablon nou</button>
    <div id="fr-msg" role="alert"></div>`;
  corp.querySelector("#fr-add").addEventListener("click", () => nav.mergi("\u0218ablon nou", (c) => formSablon(c, nav, tenantId, opt)));  // faza_b_traseu_v1

  corp.querySelectorAll(".fr-toggle").forEach((b) => b.addEventListener("click", async () => {
    const activNou = !(b.dataset.activ === "true");
    try {
      await api.put(`/tenants/${tenantId}/facturi-recurente/${b.dataset.id}?activ=${activNou}`);
      listaRecurente(corp, nav, tenantId, opt);
    } catch (e) {
      arataMesaj(corp.querySelector("#fr-msg"), e.mesaj || e.message || "Eroare.", "eroare");   // [lotul 11, 440] zona de mesaj, nu HTML de mână
    }
  }));
  corp.querySelectorAll(".fr-sterge").forEach((b) => b.addEventListener("click", () => {
    confirmaCaseta(b.parentElement, "\u0218tergi \u0219ablonul?", async () => {
      try {
        await api.del(`/tenants/${tenantId}/facturi-recurente/${b.dataset.id}`);
        listaRecurente(corp, nav, tenantId, opt);
      } catch (e) {
        arataMesaj(corp.querySelector("#fr-msg"), e.mesaj || e.message || "Eroare.", "eroare");   // [lotul 11, 440]
      }
    }, { textOk: "\u0218terge" });
  }));
}

// ---------- ADAUGA SABLON ----------  // fac_recurente_v1
export function formSablon(corp, nav, tenantId, opt) {
  const inapoiLista = () => nav.inapoiPas();  // faza_b_traseu_v1
  corp.innerHTML = `
    <h2 class="pf-titlu">\u0218ablon nou</h2>

    <div class="em-sectiune">
      <div class="em-eticheta">Beneficiar</div>
      <label class="camp-eticheta" for="fr-cui">CUI beneficiar</label>
      <input class="camp-input" id="fr-cui" placeholder="ex: RO12345678" autocomplete="off">
      <label class="camp-eticheta" for="fr-nume">Denumire beneficiar</label>
      <input class="camp-input" id="fr-nume" autocomplete="off">
    </div>

    <div class="em-sectiune">
      <div class="em-eticheta">Produse \u0219i servicii</div>
      <div class="camp-eticheta">Linie: denumire \u00b7 cantitate \u00b7 pre\u021b unitar \u00b7 cot\u0103 TVA</div>
      <div class="em-linii" id="fr-linii"></div>
      <button class="buton-secundar em-buton-sec" id="fr-add-linie" data-fara-actiune="rând în formular; salvarea formularului poartă acțiunea">+ Adaug\u0103 linie</button>
    </div>

    <div class="em-sectiune">
      <div class="em-eticheta">Emitere</div>
      <input class="camp-input" id="fr-zi" type="number" min="1" max="28" placeholder="1" aria-label="Ziua din lun\u0103 la care se emite" title="Ziua din lun\u0103 la care se emite">
      <select class="camp-input" id="fr-moneda" aria-label="Moneda">
        <option value="RON" selected>RON</option>
        <option value="EUR">EUR</option>
        <option value="USD">USD</option>
      </select>
    </div>

    <div class="em-actiuni">
      <button class="buton-primar" id="fr-salveaza" data-actiune="POST /tenants/{tenant_id}/facturi-recurente">Salveaz\u0103 \u0219ablonul</button>
    </div>
    <div class="em-rezultat" id="fr-rezultat"></div>`;

  const zonaLinii = corp.querySelector("#fr-linii");
  const linii = [];
  const _val = (x) => (x === "" || x == null) ? "" : esc(String(x));
  // [comanda Costin 06.10.2026 pct.1b, clasa] rândul nou NU poartă un preț (era 0): „un preț pe care nu l-a ales nimeni nu se propune”
  const linieNoua = () => ({ descriere: "", cantitate: 1, pret_unitar: "", cota_tva: null });

  // randeaza O linie DIN MODEL, id-uri pozitionale fr-l{i}-* (cap.24: id derivat din pozitie, ca backendul sa
  // lege eroarea de camp). Buton de stergere pe fiecare rand (cap.24 regula 3).
  function randLinie(i) {
    const l = linii[i];
    const cotaTxt = l.cota_tva == null ? "—" : (l.cota_tva === 0 ? "scutit" : `${l.cota_tva}%`);
    return `<div class="em-linie" data-idx="${i}">
      <input class="camp-input em-l-den" id="fr-l${i}-descriere" data-actiune-camp="POST /tenants/{tenant_id}/produse/potriveste" value="${_val(l.descriere)}" placeholder="Denumire (ex: abonament mentenanță)" aria-label="Denumire articol" autocomplete="off">
      <input class="camp-input em-l-cant" id="fr-l${i}-cantitate" type="number" step="0.001" value="${_val(l.cantitate)}" placeholder="Cant." aria-label="Cantitate" title="Cantitate">
      <input class="camp-input em-l-pret" id="fr-l${i}-pret_unitar" type="number" step="0.01" value="${_val(l.pret_unitar)}" placeholder="Preț" aria-label="Preț unitar" title="Preț unitar">
      <span class="em-l-cota" id="fr-l${i}-cota" title="Cota TVA">${cotaTxt}</span>
      <button type="button" class="buton-sters em-l-sterge" data-idx="${i}" title="Șterge">×</button>
    </div>`;
  }

  function setCota(l, text) {
    const p = linii.indexOf(l);
    if (p < 0) return;
    const el = zonaLinii.querySelector("#fr-l" + p + "-cota");
    if (el) el.textContent = text;
  }

  // inputurile scriu in MODEL (fara re-randare la tastare -> fara pierdere de focus). Fetch-ul cotei capteaza
  // OBIECTUL l (nu indexul) -> scrie corect chiar daca un splice a reindexat lista intre timp.
  function legaLinie(i) {
    const l = linii[i];
    const den = zonaLinii.querySelector("#fr-l" + i + "-descriere");
    const cant = zonaLinii.querySelector("#fr-l" + i + "-cantitate");
    const pret = zonaLinii.querySelector("#fr-l" + i + "-pret_unitar");
    const del = zonaLinii.querySelector('.em-l-sterge[data-idx="' + i + '"]');
    let timer = null;
    den.addEventListener("input", () => {
      l.descriere = den.value.trim();
      l.cota_tva = null;
      clearTimeout(timer);
      const d = l.descriere;
      if (d.length < 3) { setCota(l, "—"); return; }
      setCota(l, "…");
      timer = setTimeout(async () => {
        try {
          const r = await api.post(`/tenants/${tenantId}/produse/potriveste`, { denumire: d });
          if (r && r.ok) { l.cota_tva = r.cota; setCota(l, r.cota === 0 ? "scutit" : r.cota + "%"); }
          else setCota(l, "—");
        } catch { setCota(l, "—"); }
      }, 400);
    });
    cant.addEventListener("input", () => { l.cantitate = Number(cant.value) || 0; });
    pret.addEventListener("input", () => { const v = parseFloat(pret.value); l.pret_unitar = Number.isFinite(v) ? v : ""; });   // [pct.1b] golul rămâne gol
    del.addEventListener("click", () => { const p = linii.indexOf(l); if (p >= 0) linii.splice(p, 1); deseneazaLinii(); });
  }

  // re-randare INTEGRALA din model (cap.24 regula 1): nu se muta noduri individual; valorile tastate pe randurile
  // ramase supravietuiesc (sunt in model). Se re-leaga listenerii cu indici proaspeti.
  function deseneazaLinii() {
    zonaLinii.innerHTML = linii.map((_, i) => randLinie(i)).join("");
    linii.forEach((_, i) => legaLinie(i));
  }

  corp.querySelector("#fr-add-linie").addEventListener("click", () => { linii.push(linieNoua()); deseneazaLinii(); });
  linii.push(linieNoua());  // prima linie
  deseneazaLinii();

  // plaseaza erorile field-keyed din 422 (backendul: erori_campuri [{camp: fr-l{i}-.., mesaj}]) LANGA campul lor
  // (cap.6 mecanism A). Cele fara #camp in DOM -> zona generica (fallback B).
  corp.querySelector("#fr-salveaza").addEventListener("click", async () => {
    const zona = corp.querySelector("#fr-rezultat");
    curataEroriCamp(corp);
    // NU se filtreaza randuri (cap.24 regula 2): lista trimisa = lista randata. Un rand incomplet se valideaza
    // pe backend si se raporteaza langa campul lui, nu dispare tacit.
    const corpCerere = {
      tert_cui: corp.querySelector("#fr-cui").value.trim() || null,
      tert_nume: corp.querySelector("#fr-nume").value.trim(),
      zi_emitere: Number(corp.querySelector("#fr-zi").value) || 1,
      moneda: corp.querySelector("#fr-moneda").value,
      linii: linii.map((l) => ({ descriere: l.descriere, cantitate: l.cantitate,
        pret_unitar: (l.pret_unitar === "" || l.pret_unitar == null) ? null : l.pret_unitar, cota_tva: l.cota_tva })),   // [pct.1b] gol = lipsă, refuzat lângă câmp
    };
    try {
      await api.post(`/tenants/${tenantId}/facturi-recurente`, corpCerere);
      inapoiLista();
    } catch (e) {
      // [lotul 11, 440] drumul unic al refuzului: câmpurile `fr-…` lângă ele, textul fiecărui refuz fără câmp în zonă (nu o buclă proprie)
      curataEroriCamp(corp);
      const _z = corp.querySelector("#fr-rezultat");
      _z.textContent = "";
      arataRefuzul(corp, e, _z);
    }
  });
}

// chitante_fe_v1

// chitante_fe_v2_etichete

// audit_cab_lot1_v1

// faza_b_traseu_v1

// fara_precompletari_v1
