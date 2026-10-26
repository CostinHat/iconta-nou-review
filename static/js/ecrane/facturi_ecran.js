// facturi_ecran.js — cardul Facturi consolidat, REUTILIZABIL (portal client, gratuit, cabinet).
// Primeste tenantId -> merge din orice context. Contine:
//   meniu (Istoric / Emite / Model factura) + istoric + emitere.
//   Detalii / Storno / Model se adauga in pasii urmatori.
// Apelare: randeazaFacturi(corp, nav, tenantId, { inapoi, titluInapoi })
import { api, ultimaCerere, cate, cursValutar, dataRo, arataMesaj, confirmaCaseta, esc, bani, eroareCamp, curataEroriCamp, semnAjutor, descarca, deschide, dataIso, cantitate, selectDaNu, daNu, cereAlegerile, focusFaraSalt, refuzPeRand, stareNota, numarCuSerie, arataRefuzul, cereCompletate, ALEGE, pastreazaCampulActiv, atributeInactiv } from "../api.js?v=e38843b1ec";  /* esc_nc27 */
import { randeazaStareSpv } from "./spv_stare.js?v=228cdfcde1";  /* [lotul 6: 273, 275] */
import { sesiune } from "../sesiune.js?v=898215e0ee";
import { permis } from "../drepturi.js?v=34d0fb0afd";
import { randeazaEmitere, intrebarePleacaMarfa, intrebareDovadaTransport, arataAvertismenteEmitere, textDescarcare, textTvaIncasare, tvaDocument, clasaCotei, htmlCotaLinie, htmlCategorieLinie, optiuniMoneda, UM_SERVICIU } from "./emitere_ecran.js?v=8d3aa3015f";
import { cuLegareaNir, interogareLegare } from "./nir_legare.js?v=b34abfe2ec";
import { propuneNumeAnaf } from "./nume_anaf.js?v=d59cd56b02";   // [lotul 11, 444]
import { legaDateAnaf } from "./date_anaf.js?v=503d474ed1";   // [lotul 12, 459.1] datele aduse de la ANAF țin de CUI-ul lor
import { optiuniTara, taraDinCui } from "./tari_partener.js?v=43a0fddc7d";   // [lotul 12, C160] țara clientului pe șablonul facturii recurente

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

// [lotul 13, deficiența 543 — „La lipsa seriei de chitanțe, aplicația trimite în Date firmă, iar la factură seria se cere pe loc”] Refuzul
// `SERIE_CHITANTA_LIPSA` (serverul: `uc_tenants.chitanta_serie_sau_refuz`) se rezolvă pe loc, ca seria facturii (`emitere_ecran.arataSerieLipsa`):
// câmpul seriei sub butonul apăsat, salvat în Date firmă (`POST /firma-profil/date`, numai `serie_chitanta` — salvarea parțială, jurnalizată),
// apoi aceeași acțiune se reia (`reia`). Folosit de chitanța din detaliul facturii și de Casă (chitanța fără factură, încasarea facturii).
// Întoarce true dacă refuzul a fost al seriei (și l-a preluat), altfel false (apelantul îl arată ca de obicei).
export function cereSeriaChitanteiPeLoc(zona, tenantId, e, reia) {
  const det = e && e.detaliu;
  if (!zona || !det || det.cod !== "SERIE_CHITANTA_LIPSA") return false;
  // caseta stă LÂNGĂ zona de mesaj, nu în ea: zona e o `.msg-eroare`, pe care tastarea într-un câmp al ferestrei o golește
  // (`api.stergeEroriDupaCorectare`, 290) — câmpul seriei ar dispărea la prima literă
  const vechi = document.getElementById("ser-chit-box");
  if (vechi) vechi.parentElement.remove();   // caseta de la refuzul de dinainte, cu cutia ei
  zona.textContent = "";
  const cutie = document.createElement("div");
  zona.insertAdjacentElement("afterend", cutie);
  zona = cutie;
  zona.innerHTML = `
    <div class="em-curs-box" id="ser-chit-box">
      <span data-ecran-destinatie="date_firma" hidden></span>
      <div class="em-curs-titlu">⚠ ${esc(e.mesaj || det.mesaj || "")}</div>
      <label class="camp"><span class="camp-eticheta">Seria chitanțelor (ex: CH)<span class="oblig">*</span></span>
        <input class="camp-input" id="ser-chit-serie" maxlength="10" autocomplete="off"></label>
      <div class="em-curs-actiuni">
        <button class="buton-primar" id="ser-chit-ok" data-actiune="POST /tenants/{tenant_id}/firma-profil/date">Stabilește seria și emite chitanța</button>
      </div>
    </div>`;
  const inp = zona.querySelector("#ser-chit-serie");
  focusFaraSalt(inp);
  zona.querySelector("#ser-chit-ok").addEventListener("click", async () => {
    curataEroriCamp(zona);
    const serie = inp.value.trim().toUpperCase();
    if (!serie) { eroareCamp(zona, "ser-chit-serie", "Completează seria chitanțelor (o stabilește firma: OMFP 2634/2015 anexa 1 pct.24)."); return; }
    try {
      await api.post(`/tenants/${tenantId}/firma-profil/date`, { serie_chitanta: serie });
    } catch (er) {
      const pe = ((er && er.erori_campuri) || []).find((x) => x.camp === "serie_chitanta");
      eroareCamp(zona, "ser-chit-serie", (pe && pe.mesaj) || (er && er.mesaj) || "Seria nu s-a putut salva.");
      return;
    }
    zona.remove();
    reia();
  });
  return true;
}

// [lotul 12, 468] moneda unei sume, scrisă: RON -> „lei”, altfel codul ei (EUR, USD…)
export const monedaScrisa = (m) => (!m || String(m).toUpperCase() === "RON") ? "lei" : String(m).toUpperCase();   // [lotul 13, 559] și în „Cifrele firmei” (portal.js)

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
// [C103] „Verifică acum în SPV” și importul XML re-citesc aceeași fereastră: numai ultima citire ajunge pe ecran (contorul e pe `corp`,
// deci două ferestre „Facturi primite” nu se anulează între ele), iar mesajul fiecărei operații se arată de citirea care termină ultima
const _mesajePrimite = new WeakMap();
async function primiteSPV(corp, nav, tenantId, opt, mesaj = null) {
  const actuala = ultimaCerere(corp)();
  if (mesaj) _mesajePrimite.set(corp, [...(_mesajePrimite.get(corp) || []), mesaj]);
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  let lista = [], categorii331 = [];
  try {
    const r = await api.get(`/tenants/${tenantId}/facturi-primite`);
    if (!actuala()) return;
    lista = (r && r.primite) || []; categorii331 = (r && r.categorii_331) || [];
  } catch { if (!actuala()) return; corp.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca facturile primite din SPV.</p>`; return; }
  // [deficiența 273a/b, lotul 6] starea SPV a firmei (conectată? verificată când? ce a răspuns ANAF?), „Verifică acum în SPV” și importul
  // manual XML UBL. „apar aici automat” se spune NUMAI când firma chiar e citită automat (conectată și cu drept).
  corp.innerHTML = `
    <h2 class="pf-titlu">Facturi primite din SPV ${semnAjutor("F043")}</h2>
    <div id="fp-spv" style="margin-bottom:10px"></div>
    <p class="pf-intro" id="fp-actiuni">
      <button class="buton-secundar" id="fp-verifica" data-actiune="POST /tenants/{tenant_id}/spv/verifica-acum">Verifică acum în SPV</button>
      <label class="buton-secundar" style="margin-left:6px" data-actiune="POST /tenants/{tenant_id}/facturi-primite/import-xml">Importă XML UBL
        <input type="file" id="fp-xml" accept=".xml,.zip" multiple hidden aria-label="Fișier XML UBL al facturii primite"></label>
      <button class="buton-secundar" id="fp-manual" style="margin-left:6px" data-actiune="POST /tenants/{tenant_id}/facturi-primite/manual">Introdu factura de mână</button>
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
      const txt = c.eroare ? (c.de_la_anaf === false ? c.eroare : `ANAF a răspuns: „${c.eroare}”.`) :   // [lotul 12, clasa 598] motivul aplicației nu e pus pe seama ANAF
         `Citit din SPV: ${cate(c.mesaje || 0, "factură primită", "facturi primite")} în ultimele ${cate(c.zile, "zi", "zile")}; cele noi sunt în listă.`;
      primiteSPV(corp, nav, tenantId, opt, { txt, tip: c.eroare ? "avert" : "ok" });
    } catch (e) { arataMesaj(zMsg, e.mesaj || "Citirea din SPV n-a mers.", "eroare"); b.disabled = false; }
  });
  // [lotul 12, 477] factura primită pe hârtie / PDF (fără XML): formularul ei, validat pe același drum ca factura din XML
  corp.querySelector("#fp-manual").addEventListener("click", () => nav.mergi("Factură primită de mână", (c) => primitaManuala(c, nav, tenantId, opt)));
  corp.querySelector("#fp-xml").addEventListener("change", async (ev) => {
    const fs = [...ev.target.files];
    if (!fs.length) return;
    const fd = new FormData();
    fs.forEach((f) => fd.append("fisiere", f));
    try {
      const r = await api.postForm(`/tenants/${tenantId}/facturi-primite/import-xml`, fd);
      const txt = [`${cate(r.importate, "factură importată", "facturi importate")} în lista de validat`
        + (r.deja ? `; ${cate(r.deja, "era deja", "erau deja")} în listă` : "") + ".", ...(r.erori || [])].join("\n");
      primiteSPV(corp, nav, tenantId, opt, { txt, tip: (r.erori || []).length ? "avert" : "ok" });
    } catch (e) { arataMesaj(zMsg, e.mesaj || "Importul n-a mers.", "eroare"); }
    ev.target.value = "";
  });
  const st = await randeazaStareSpv(corp.querySelector("#fp-spv"), nav, tenantId);
  if (!actuala()) return;
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
  const m = _mesajePrimite.get(corp) || [];
  _mesajePrimite.delete(corp);
  if (m.length) arataMesaj(zMsg, m.map((x) => x.txt).join("\n"), m.some((x) => x.tip !== "ok") ? "avert" : "ok");
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
      <label class="camp"><span class="camp-eticheta">TVA</span><input class="camp-input" id="pr-tva" value="${esc(sumaCuMoneda(p.tva, p.moneda))}" readonly aria-label="TVA"></label>
      <label class="camp"><span class="camp-eticheta">Total</span><input class="camp-input" id="pr-total" value="${esc(sumaCuMoneda(p.total, p.moneda))}" readonly aria-label="Total"></label>
    </div>
    <div class="fd-valuta" id="pr-valuta" aria-live="polite" hidden></div>
    <div style="margin-top:10px"><div class="camp-eticheta">Linii</div>
      <span class="camp-ajutor">Clasifică destinația TVA a fiecărei linii importate: <b>taxabilă</b> (deducere integrală, implicit), <b>scutită</b> (fără deducere), <b>mixtă</b> (intră în pro-rata, art. 300 alin. (5)). Faptul importat rămâne neschimbat — doar îl clasifici.</span>
      ${linii.map((l, i) => `<div class="pf-linie-clasif" style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:4px">
        <span class="pf-frand-sub" style="flex:1 1 200px">${esc(l.descriere)} · ${esc(cantitate(l.cantitate))} × ${esc(bani(l.pret))} · ${esc(l.cota)}%</span>
        <select class="camp-input pr-dest" data-i="${i}" aria-label="Destinație TVA linie" style="flex:0 0 auto;width:auto" data-butoane="">
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
      <label class="camp"><span class="camp-eticheta">Țara furnizorului (ISO)</span><input class="camp-input" id="pr-tara" value="${esc(((p.cif_emitent || "").match(/^[A-Za-z]{2}/) || ["RO"])[0].toUpperCase())}" placeholder="ex. RO" aria-label="Țara furnizorului"></label>
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
  arataCursulValidarii(corp.querySelector("#pr-valuta"), tenantId, p.moneda, p.data, { tva: p.tva, total: p.total });   // [lotul 12, cursul vechi la validare (a)]; [lotul 13, 634 a] echivalentul în lei
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
        // [lotul 13, deficiența 634 (b) — „După validare: «Cheltuiala creată» deși contul e 371 (marfă), fără legătură spre notă”] mesajul
        // spune ce s-a scris, pe contul ales (marfă / materiale / cheltuială), cu nota (conturile ei) și butonul spre ea în Registrul jurnal
        const ct = (r && r.contare) || {};
        const cont = corp.querySelector("#pr-cont").value.trim();
        const fel = /^(371|30[1-3])/.test(cont) ? "marfa / materialele intră în stoc" : (/^2/.test(cont) ? "imobilizarea intră în evidență" : "cheltuiala intră în evidență");
        const conturi = (ct.linii || []).map((l) => `${l.debit} = ${l.credit} ${bani(l.suma)}`).join("; ");
        arataMesaj(zona, `Validată: factura ${p.numar || "fără număr"}${p.data ? " din " + dataRo(p.data) : ""} — ${fel} (contul ${cont || "sugerat"}).`
          + (ct.inregistrare_id ? ` Nota ciornă, de validat: ${conturi}.` : (ct.stare === "refuzata" ? " Nota n-a putut fi scrisă automat: o scrii din Registrul jurnal." : "")), "ok");   // [258] factura cum o arată lista, nu id-ul ei
        if (ct.inregistrare_id) {
          const bn = document.createElement("button");
          bn.type = "button"; bn.className = "buton-secundar"; bn.id = "pr-vezi-nota"; bn.textContent = "Vezi nota în Registrul jurnal";
          bn.addEventListener("click", async () => {
            const { ecranJurnal } = await import("./firme.js?v=2b27eebcaf");   // dinamic, ca „nota …” din detaliul facturii
            const [an, luna] = String(p.data || dataIso()).slice(0, 10).split("-").map(Number);
            nav.deschide("Registru jurnal", (c2) => ecranJurnal(c2, nav, { id: tenantId }, { an, luna, evidentiaza: ct.inregistrare_id }), { lat: "tabel" });
          });
          zona.appendChild(bn);
        }
        anuntaCursulValidat(zona, r);   // [lotul 12, cursul vechi la validare (a)]
        butonInapoi(zona, nav);   // [418c / 410, DS cap.27] confirmarea rămâne; înapoi la cererea omului
      } catch (e) { arataRefuzul(corp, e, zona); }   // [lotul 11, 440] câmpurile refuzului lângă ele, restul în zonă
    }, { textOk: "Validează" });
  });
  // [lotul 13, 673 — DS cap.2a v2.104] „Respinge” își cere motivul într-o fereastră nouă (înainte: câmpul apărea în zona de jos a facturii)
  corp.querySelector("#pr-respinge").addEventListener("click", () => {
    nav.deschide("Respinge factura primită", (c2) => {
      c2.innerHTML = `<label class="camp"><span class="camp-eticheta">Motiv respingere<span class="oblig">*</span></span><input class="camp-input" id="pr-motiv" aria-label="Motiv respingere"></label>
        <button class="buton-secundar" id="pr-respinge-ok" data-actiune="POST /tenants/{tenant_id}/facturi-primite/{primita_id}/respinge" style="margin-top:8px">Respinge factura</button>
        <div id="pr-respinge-mesaj"></div>`;
      focusFaraSalt(c2.querySelector("#pr-motiv"));
      c2.querySelector("#pr-respinge-ok").addEventListener("click", async () => {
        const motiv = c2.querySelector("#pr-motiv").value.trim();
        curataEroriCamp(c2);
        if (!motiv) { eroareCamp(c2, "pr-motiv", "Scrie motivul respingerii."); return; }   // [lotul 11, 440] lângă câmp
        try {
          await api.post(`/tenants/${tenantId}/facturi-primite/${p.id}/respinge`, { motiv });
          nav.inapoi();   // înapoi la factură, cu confirmarea în zona ei (DS cap.27); fereastra redesenată își citește singură starea
          if (zona.isConnected) { arataMesaj(zona, "Respinsă (rămâne în istoric).", "ok"); butonInapoi(zona, nav); }   // [418c / 410]
        } catch (e) { arataRefuzul(c2, e, c2.querySelector("#pr-respinge-mesaj")); }   // [lotul 11, 440]
      });
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

// [lotul 12, C105, DS cap.4 „Sumele: format românesc”] o sumă afișată într-un câmp readonly: cu `bani` (1.694,00) și cu moneda ei, nu
// textul brut din XML („1694.00”)
function sumaCuMoneda(x, moneda) {
  if (x == null || x === "") return "";
  return `${bani(x)} ${monedaScrisa(moneda)}`;
}

// [lotul 12, decizia Costin „cursul vechi la validare (a)”: „anunțul la validare, ca la emitere”] cursul cu care se va valida factura primită
// în valută — ACEEAȘI rută ca formularul de emitere (`POST /tenants/{tenant_id}/facturi/previzualizare-lei`, `facturi_api.curs_automat`), iar când cursul zilei
// lipsește și se folosește unul mai vechi, ACELAȘI anunț (`curs_bnr.cursul_zilei_lipsa`, act „validare”; DS cap.6: avert)
// [lotul 13, deficiența 634 (a) — „Detaliul facturii în valută arată TVA și total fără monedă, cu punct, fără cursul BNR și echivalentul în
// lei înainte de validare”] suma × cursul, la ban, rotunjită aritmetic (ca `facturi_api.sume_lei`: ROUND_HALF_UP), în numere întregi (bani ×
// zecimi de miime ale cursului) — fără virgulă mobilă
function leiLaCurs(suma, curs) {
  const N = (x) => BigInt(x);   // BigInt prin apel (fără literali „…n”: parserul gărzilor îi serializează în JSON)
  const intreg = (x, zec) => {
    const t = String(x).trim(), semn = t.startsWith("-") ? N(-1) : N(1);
    const [a, b = ""] = t.replace(/^[-+]/, "").split(".");
    return semn * N((a || "0") + (b + "0".repeat(zec)).slice(0, zec));
  };
  const bani = intreg(suma, 2), c = intreg(curs, 6);
  const prod = bani * c;                                   // bani × curs × 10^6
  const neg = prod < N(0), abs = neg ? -prod : prod;
  const rez = (abs + N(500000)) / N(1000000);              // ROUND_HALF_UP la ban
  const v = (neg ? -rez : rez).toString().padStart(3, "0");
  return v.slice(0, -2) + "." + v.slice(-2);
}

async function arataCursulValidarii(zona, tenantId, moneda, data, sume = null) {
  if (!zona) return;
  const actuala = ultimaCerere(zona)();   // [C103] moneda / data schimbate în șir: numai ultimul curs cerut ajunge pe ecran
  const m = String(moneda || "RON").toUpperCase();
  if (m === "RON" || !data) { zona.hidden = true; zona.innerHTML = ""; return; }
  // [lotul 12] fără dreptul previzualizării (al pregătirii): nici cererea, nici refuzul ei — cursul îl scrie oricum validarea
  if (!permis("POST /tenants/{tenant_id}/facturi/previzualizare-lei")) { zona.hidden = true; zona.innerHTML = ""; return; }
  const titlu = `<div class="fd-valuta-titlu">Conversie în lei (art. 319 Cod fiscal), cum o va scrie validarea</div>`;
  zona.hidden = false;
  zona.innerHTML = `${titlu}<div class="fd-valuta-sub">Se citește cursul BNR…</div>`;
  let r;
  try { r = await api.post(`/tenants/${tenantId}/facturi/previzualizare-lei`, { moneda: m, data_emitere: String(data).slice(0, 10), act: "validare" }); }
  catch (e) { if (!actuala()) return; zona.innerHTML = `${titlu}<div class="pr-curs-mesaj"></div>`; arataMesaj(zona.querySelector(".pr-curs-mesaj"), (e && e.mesaj) || "Cursul BNR nu s-a putut citi acum.", "eroare"); return; }
  if (!actuala() || !zona.isConnected) return;
  if (!r || !r.ok) { zona.innerHTML = `${titlu}<div class="pr-curs-mesaj"></div>`; arataMesaj(zona.querySelector(".pr-curs-mesaj"), (r && r.mesaj) || "Cursul BNR nu e disponibil acum.", "eroare"); return; }
  const lei = (x) => (x == null || x === "") ? "" : bani(leiLaCurs(x, r.curs)) + " lei";
  zona.innerHTML = `${titlu}
    <div class="fd-tot-rand"><span>Curs BNR ${esc(m)}</span><span class="pr-curs"><b>${cursValutar(r.curs)}</b> din ${esc(dataRo(r.data_curs))}</span></div>
    ${sume ? `<div class="fd-tot-rand" id="pr-tva-lei"><span>TVA în lei</span><span><b>${lei(sume.tva)}</b></span></div>
    <div class="fd-tot-rand" id="pr-total-lei"><span>Total în lei</span><span>${lei(sume.total)}</span></div>` : ""}
    ${r.curs_zilei_lipsa ? `<div class="pr-curs-lipsa"></div>`
      : `<div class="fd-valuta-sub">Ultimul curs comunicat de BNR înaintea datei facturii (${esc(dataRo(String(data).slice(0, 10)))}); se fixează la validare.</div>`}`;
  if (r.curs_zilei_lipsa) arataMesaj(zona.querySelector(".pr-curs-lipsa"), r.curs_zilei_lipsa.mesaj, "avert");
}

// după validare: cursul mai vechi folosit (serverul îl spune în răspuns) rămâne anunțat lângă confirmare
function anuntaCursulValidat(zona, r) {
  if (!(r && r.curs_zilei_lipsa && r.curs_zilei_lipsa.mesaj)) return;
  const d = document.createElement("div");
  d.className = "pr-curs-validat";
  zona.appendChild(d);
  arataMesaj(d, r.curs_zilei_lipsa.mesaj, "avert");
}

// ---------- FACTURĂ PRIMITĂ INTRODUSĂ DE MÂNĂ (lotul 12, deficiența 477) ----------
// Factura de la un furnizor pe hârtie / PDF, fără XML: furnizorul (CUI verificat la ANAF — `verifica-cui`, ca la NIR), seria / numărul,
// data, scadența, moneda (cursul BNR ca la validarea facturii din XML), liniile cu cotele în vigoare la data facturii (registrul de
// parametri fiscali, `GET /tenants/{tenant_id}/facturi/numerotare`), contul facturii și al fiecărei linii, destinația TVA a liniei. Validarea e ACEEAȘI ca la
// factura din XML (`uc_factura_primita.valideaza`): nota, gestiunea pe un cont de stoc, alegerea NIR-ului „fără factură”.
// [lotul 13, regula UM — `facturi.MESAJ_UM_LIPSA`] UM-ul pornește gol (nu „buc”): îl scrie omul de pe factură; gol -> refuzul lângă câmp
const linieManuala = () => ({ descriere: "", cantitate: "", um: "", pret_unitar: "", cota_tva: "", dest: "taxabil", cont: "" });

function primitaManuala(corp, nav, tenantId, opt) {
  const linii = [linieManuala()];
  let COTE = [];
  const tara = () => ((corp.querySelector("#pm-tara") || {}).value || "").trim().toUpperCase();
  corp.innerHTML = `
    <h2 class="pf-titlu">Factură primită · introdusă de mână</h2>
    <p class="pf-intro">De pe factura furnizorului (hârtie sau PDF). Se validează la fel ca o factură venită din SPV: nota pe contul ales și, la un cont de stoc, intrarea în gestiune.</p>
    <div class="grila-doc" style="grid-template-columns:1fr 2fr 2fr">
      <label class="camp"><span class="camp-eticheta">Țara furnizorului (ISO)<span class="oblig">*</span></span><input class="camp-input" id="pm-tara" maxlength="2" placeholder="ex. RO" aria-label="Țara furnizorului"></label>
      <label class="camp"><span class="camp-eticheta">Codul fiscal al furnizorului<span class="oblig">*</span></span>
        <span style="display:flex;gap:6px;align-items:center"><input class="camp-input" id="pm-cui" aria-label="Codul fiscal al furnizorului" placeholder="ex. 14399840">
        <button class="buton-secundar" type="button" id="pm-verifica" data-actiune="GET /tenants/{tenant_id}/verifica-cui/{cui}">Verifică la ANAF</button></span>
        <span class="em-cui-stare" id="pm-cui-stare"></span></label>
      <label class="camp"><span class="camp-eticheta">Furnizor<span class="oblig">*</span></span><input class="camp-input" id="pm-furnizor" aria-label="Furnizor"></label>
    </div>
    <div class="grila-doc" style="grid-template-columns:1fr 1fr 1fr 1fr 1fr;margin-top:8px">
      <label class="camp"><span class="camp-eticheta">Seria</span><input class="camp-input" id="pm-serie" aria-label="Seria facturii"></label>
      <label class="camp"><span class="camp-eticheta">Numărul<span class="oblig">*</span></span><input class="camp-input" id="pm-numar" aria-label="Numărul facturii"></label>
      <label class="camp"><span class="camp-eticheta">Data facturii<span class="oblig">*</span></span><input class="camp-input" type="date" id="pm-data" aria-label="Data facturii"></label>
      <label class="camp"><span class="camp-eticheta">Scadența</span><input class="camp-input" type="date" id="pm-scadenta" aria-label="Scadența"></label>
      <label class="camp"><span class="camp-eticheta">Moneda<span class="oblig">*</span></span>
        <select class="camp-input" id="pm-moneda" aria-label="Moneda facturii" data-actiune-camp="POST /tenants/{tenant_id}/facturi/previzualizare-lei">
          <option value="RON" selected>RON (lei)</option><option value="EUR">EUR</option><option value="USD">USD</option><option value="GBP">GBP</option>
          <option value="CHF">CHF</option><option value="HUF">HUF</option><option value="PLN">PLN</option></select></label>
    </div>
    <div style="margin-top:12px"><div class="camp-eticheta">Liniile facturii</div>
      <span class="camp-ajutor">Unitatea de măsură, prețul unitar fără TVA și cota de pe factură (cotele în vigoare la data facturii). Contul liniei: gol = contul facturii de mai jos; numai liniile pe un cont de stoc (371 / 301–303) intră în stoc. Destinația TVA: <b>taxabilă</b> (deducere integrală), <b>scutită</b> (fără deducere), <b>mixtă</b> (intră în pro-rata, art. 300 alin. (5)).</span>
      <div id="pm-linii"></div>
      <button class="buton-secundar" type="button" id="pm-add-linie" style="margin-top:6px" data-fara-actiune="adaugă o linie în formular, fără scriere">+ linie</button>
      <div class="fd-tot-rand" id="pm-total" style="margin-top:8px"></div>
    </div>
    <div class="fd-valuta" id="pr-valuta" aria-live="polite" hidden></div>
    <div class="grila-doc" style="grid-template-columns:2fr 1fr;margin-top:12px">
      <label class="camp"><span class="camp-eticheta">Contul facturii: cheltuială, sau 371 / 301–303 la marfă și materiale<span class="oblig">*</span></span><input class="camp-input" id="pr-cont" placeholder="ex. 628 sau 371" aria-label="Contul facturii"></label>
    </div>
    <div class="grila-doc" id="pm-statut" style="grid-template-columns:2fr 2fr;margin-top:8px" hidden></div>
    <div style="margin-top:14px">
      <button class="buton-verde" id="pm-valideaza" data-actiune="POST /tenants/{tenant_id}/facturi-primite/manual">Validează (scrie nota pe contul ales)</button>
    </div>
    <div id="pr-zona" style="margin-top:10px"></div>`;
  const zona = corp.querySelector("#pr-zona");
  // tipul furnizorului (D394) și TVA la încasare: aflate din ANAF la validare; cerute numai când ANAF nu le poate spune (furnizor din altă
  // țară — de la început —, sau ANAF fără răspuns — la refuzul serverului). DS cap.17: Da/Nu situațional, ales de om
  const arataStatutul = () => {
    const z = corp.querySelector("#pm-statut");
    if (!z.hidden) return;
    z.hidden = false;
    z.innerHTML = `
      <label class="camp"><span class="camp-eticheta">Furnizorul e înregistrat în scopuri de TVA (D394 îl declară după tip)<span class="oblig">*</span></span>
        ${selectDaNu('id="pr-platitor"', null, "Furnizorul e înregistrat în scopuri de TVA")}</label>
      ${tara() === "RO" ? `<label class="camp"><span class="camp-eticheta">Furnizorul aplică TVA la încasare (deducere amânată până la plată, art. 297 alin. (2))<span class="oblig">*</span></span>
        ${selectDaNu('id="pr-furnizor-incasare"', null, "Furnizor cu TVA la încasare")}</label>` : ""}`;
  };
  const stergeStatutul = () => { const z = corp.querySelector("#pm-statut"); z.hidden = true; z.innerHTML = ""; };
  const valuta = () => arataCursulValidarii(corp.querySelector("#pr-valuta"), tenantId, corp.querySelector("#pm-moneda").value,
                                            corp.querySelector("#pm-data").value);
  const cuCota = (l) => l.cota_tva !== "" && l.cota_tva != null;
  const totaluri = () => {
    const z = corp.querySelector("#pm-total");
    const complete = linii.every((l) => l.cantitate !== "" && l.pret_unitar !== "" && cuCota(l));
    if (!complete) { z.innerHTML = ""; return; }
    const t = tvaDocument(linii.map((l) => ({ cantitate: Number(l.cantitate), pret_unitar: Number(l.pret_unitar), cota_tva: Number(l.cota_tva) })));
    const m = monedaScrisa(corp.querySelector("#pm-moneda").value);
    z.innerHTML = `<span>Total fără TVA <b>${bani(t.baza)} ${m}</b> · TVA <b>${bani(t.tva)} ${m}</b></span><span id="pm-total-cu-tva">Total <b>${bani(t.baza + t.tva)} ${m}</b></span>`;
  };
  const deseneazaLinii = () => {
    const z = corp.querySelector("#pm-linii");
    z.innerHTML = linii.map((l, k) => {
      const i = k + 1;
      return `<div class="pf-linie-clasif" style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:6px" data-k="${k}">
        <input class="camp-input pm-camp" data-c="descriere" id="pm-l${i}-descriere" value="${esc(l.descriere)}" placeholder="denumirea de pe factură" aria-label="Denumirea liniei ${i}" style="flex:1 1 220px">
        <input class="camp-input pm-camp" data-c="cantitate" id="pm-l${i}-cantitate" value="${esc(l.cantitate)}" inputmode="decimal" placeholder="cantitate" aria-label="Cantitatea liniei ${i}" style="flex:0 0 100px;width:100px">
        <input class="camp-input pm-camp" data-c="um" id="pm-l${i}-um" value="${esc(l.um)}" placeholder="UM" aria-label="Unitatea de măsură a liniei ${i}" style="flex:0 0 70px;width:70px">
        <input class="camp-input pm-camp" data-c="pret_unitar" id="pm-l${i}-pret" value="${esc(l.pret_unitar)}" inputmode="decimal" placeholder="preț fără TVA" aria-label="Prețul unitar fără TVA al liniei ${i}" style="flex:0 0 120px;width:120px">
        <select class="camp-input pm-cota pm-camp" data-c="cota_tva" id="pm-l${i}-cota" aria-label="Cota de TVA a liniei ${i}" style="flex:0 0 auto;width:auto">${ALEGE}${COTE.map((c) => `<option value="${c}"${String(l.cota_tva) === String(c) ? " selected" : ""}>${c}%</option>`).join("")}</select>
        <select class="camp-input pr-dest pm-camp" data-c="dest" aria-label="Destinație TVA linie ${i}" style="flex:0 0 auto;width:auto" data-butoane="">
          <option value="taxabil"${l.dest === "taxabil" ? " selected" : ""}>Taxabilă</option><option value="scutit"${l.dest === "scutit" ? " selected" : ""}>Scutită</option><option value="mixt"${l.dest === "mixt" ? " selected" : ""}>Mixtă</option></select>
        <input class="camp-input pm-camp pr-cont-linie" data-c="cont" id="pm-l${i}-cont" value="${esc(l.cont)}" placeholder="contul facturii" aria-label="Contul liniei ${i}" style="flex:0 0 130px;width:130px">
        <button class="buton-sters buton-mic pm-sterge" type="button" data-k="${k}" data-fara-actiune="scoate linia din formular, fără scriere" aria-label="Șterge linia ${i}"${linii.length > 1 ? "" : atributeInactiv("Factura are o singură linie: rămâne cel puțin una.")}>Șterge</button>
      </div>`;
    }).join("");
    z.querySelectorAll(".pm-camp").forEach((el) => el.addEventListener(el.tagName === "SELECT" ? "change" : "input", () => {
      linii[Number(el.closest("[data-k]").dataset.k)][el.dataset.c] = el.value;
      totaluri();
    }));
    z.querySelectorAll(".pm-sterge").forEach((b) => b.addEventListener("click", () => { linii.splice(Number(b.dataset.k), 1); deseneazaLinii(); }));
    if (!COTE.length) {
      z.querySelectorAll(".pm-cota").forEach((sel) => { sel.disabled = true; sel.title = "Alege întâi data facturii: cotele sunt cele în vigoare atunci."; });
    }
    totaluri();
  };
  const cerereCote = ultimaCerere();
  const incarcaCotele = async () => {
    const actuala = cerereCote();
    const d = corp.querySelector("#pm-data").value;
    if (!d) { COTE = []; deseneazaLinii(); return; }
    try {
      const n = await api.get(`/tenants/${tenantId}/facturi/numerotare?data=${encodeURIComponent(d)}`);
      if (!actuala()) return;
      COTE = (n.cote_permise && n.cote_permise.length) ? n.cote_permise : [];
      linii.forEach((l) => { if (cuCota(l) && !COTE.map(String).includes(String(l.cota_tva))) l.cota_tva = ""; });   // cota altei perioade nu rămâne aleasă
      pastreazaCampulActiv(corp, deseneazaLinii);
    } catch (e) {
      if (!actuala()) return;
      eroareCamp(corp, "pm-data", `Cotele de TVA în vigoare la data aleasă nu s-au putut citi${e && e.mesaj ? ": " + e.mesaj : ""} — alege data din nou.`);
    }
  };
  deseneazaLinii();
  corp.querySelector("#pm-add-linie").addEventListener("click", () => { linii.push(linieManuala()); deseneazaLinii(); });
  corp.querySelector("#pm-data").addEventListener("change", () => { incarcaCotele(); valuta(); });
  corp.querySelector("#pm-moneda").addEventListener("change", () => { valuta(); totaluri(); });
  corp.querySelector("#pm-tara").addEventListener("change", () => { stergeStatutul(); if (tara() && tara() !== "RO") arataStatutul(); });
  // [lotul 13, 504 — DS cap.6 v2.104: „câmpul rămâne gol”] țara nu mai vine „RO” din oficiu: se DEDUCE din codul fiscal scris (prefixul
  // statului; cod numeric sau „RO…” -> RO — `taraDinCui`, ca la „Emite factură”, C160), cât omul n-a scris-o el; altfel o scrie omul
  let taraScrisaDeOm = false;
  corp.querySelector("#pm-tara").addEventListener("input", (ev) => { taraScrisaDeOm = !!ev.target.value.trim(); });
  corp.querySelector("#pm-cui").addEventListener("change", (ev) => {
    const t = taraDinCui(ev.target.value), el = corp.querySelector("#pm-tara");
    if (!t || taraScrisaDeOm || el.value === t) return;
    el.value = t;
    el.dispatchEvent(new Event("change"));
  });
  // [lotul 12, 459.1, comanda Costin 12.2 pct.5] furnizorul adus de „Verifică la ANAF” și linia de sub CUI țin de CUI-ul verificat: la
  // tastarea altui CUI pleacă (denumirea, numai dacă omul n-a schimbat-o — `date_anaf.js`, F188)
  const anaf = legaDateAnaf(corp.querySelector("#pm-cui"), [corp.querySelector("#pm-furnizor")], corp.querySelector("#pm-cui-stare"));
  const bV = corp.querySelector("#pm-verifica");
  bV.addEventListener("click", async () => {
    const cui = corp.querySelector("#pm-cui").value.trim(), st = corp.querySelector("#pm-cui-stare");
    curataEroriCamp(corp);
    if (!cui) { eroareCamp(corp, "pm-cui", "Scrie codul fiscal al furnizorului."); return; }
    st.textContent = "se verifică la ANAF…"; st.className = "em-cui-stare";
    try {
      const r = await api.get(`/tenants/${tenantId}/verifica-cui/${encodeURIComponent(cui)}?nume=${encodeURIComponent(corp.querySelector("#pm-furnizor").value.trim())}`);
      if (r && r.gasit) {
        anaf.pune([r.denumire], { suprascrie: true });   // „Verifică la ANAF” e cerut de om: denumirea ANAF intră și peste ce era scris
        st.innerHTML = `<span class="em-cui-info">${esc(r.denumire || "")} · ${r.platitor_tva ? "plătitor TVA" : "neplătitor TVA"}</span>`;
        propuneNumeAnaf(st, r, tenantId, { fel: "furnizori", pre: "pm" });   // [lotul 11, 444] fișa furnizorului cu alt nume decât ANAF
      } else { st.textContent = "CUI negăsit la ANAF"; st.className = "em-cui-stare em-cui-rau"; }
    } catch (e) { st.textContent = (e && e.mesaj) || "Verificarea nu s-a putut face — reîncearcă."; st.className = "em-cui-stare em-cui-rau pe-randuri"; }
  });
  const cerere = () => {
    const v = (id) => (corp.querySelector("#" + id) || {}).value || "";
    return {
      tert_tara: tara(), tert_cui: v("pm-cui").trim(), tert_nume: v("pm-furnizor").trim(), serie: v("pm-serie").trim(), numar: v("pm-numar").trim(),
      data_emitere: v("pm-data"), data_scadenta: v("pm-scadenta"), moneda: v("pm-moneda"), cont: v("pr-cont").trim(),
      linii: linii.map((l) => ({ descriere: l.descriere.trim(), cantitate: l.cantitate, um: (l.um || "").trim(), pret_unitar: l.pret_unitar, cota_tva: l.cota_tva })),
      destinatii: linii.map((l) => l.dest), conturi: linii.map((l) => (l.cont || "").trim()),
      tert_platitor_tva: daNu(corp.querySelector("#pr-platitor")), furnizor_tva_incasare: daNu(corp.querySelector("#pr-furnizor-incasare")),
    };
  };
  corp.querySelector("#pm-valideaza").addEventListener("click", () => {
    curataEroriCamp(corp);
    if (cereAlegerile(corp, [...linii.map((_l, k) => `#pm-l${k + 1}-cota`), "#pr-platitor", "#pr-furnizor-incasare"])) return;   // [FAPT_FISCAL_NECERUT]
    confirmaCaseta(zona, "Validezi factura? Nota se scrie pe contul ales (la un cont de stoc, cu intrarea în stoc) și intră în evidența contabilă.", async () => {
      const c = cerere();
      try {
        // [decizia 08.10 pct.2] factura de marfă cu NIR „fără factură” nelegat la același furnizor: serverul cere alegerea
        const r = await cuLegareaNir(zona, "POST /tenants/{tenant_id}/facturi-primite/manual", (alegere) =>
          api.post(`/tenants/${tenantId}/facturi-primite/manual`, { ...c, ...alegere }));
        arataMesaj(zona, `Validată. Cheltuiala creată din factura ${numarCuSerie(c.serie, c.numar)} din ${dataRo(c.data_emitere)}.`, "ok");
        anuntaCursulValidat(zona, r);
        corp.querySelector("#pm-valideaza").disabled = true;   // aceeași factură nu se validează a doua oară din formularul ăsta
        butonInapoi(zona, nav);   // [418c / 410, DS cap.27] confirmarea rămâne; înapoi la cererea omului
      } catch (e) {
        if (e && e.detaliu && e.detaliu.cod === "TERT_PLATITOR_DE_COMPLETAT") arataStatutul();   // ANAF n-a spus tipul furnizorului
        arataRefuzul(corp, e, zona);   // [lotul 11, 440] câmpurile refuzului lângă ele, restul în zonă
      }
    }, { textOk: "Validează" });
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
  const cerereNoua = ultimaCerere();   // [C103] luna / „mai multe” apăsate în șir: numai lista lunii cerute ultima ajunge pe ecran
  const deseneaza = async () => {
    const actuala = cerereNoua();
    corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;
    let lista = [];
    try {
      const r = await api.get(`/tenants/${tenantId}/facturi?an=${an}&luna=${luna}&limit=${afisate + 1}`);
      if (!actuala()) return;
      lista = (r && r.facturi) || [];
    } catch { if (!actuala()) return; corp.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca facturile emise.</p>`; return; }
    // [cap.23, 21.08.2026] ACTUL DE ÎNCHIDERE a lunii pe facturi. Cât timp luna nu e închisă, evidența
    // ei e informativă — iar semaforul nu se poate sprijini pe ea când spune că o declarație nu se
    // datorează. Nu se afișează în portalul clientului (închiderea e act de contabil).
    let per = null;
    if (!opt.client) {
      try { per = await api.get(`/tenants/${tenantId}/facturi/perioada?an=${an}&luna=${luna}`); if (!actuala()) return; }
      catch { if (!actuala()) return; per = null; }
    }
    const maiSunt = lista.length > afisate;
    if (maiSunt) lista = lista.slice(0, afisate);
    let corpuri = !lista.length
      ? `<div class="stare-goala">Nicio factur\u0103 \u00een luna aceasta.</div>`
      : lista.map((f) => {
          // [lotul 13, 546] totalul de plată (factura primită cu taxare inversă: fără TVA-ul determinat de firmă — CF art.331 alin.(3))
          const suma = f.total != null ? bani(f.total_de_plata != null ? f.total_de_plata : f.total) + " " + (f.moneda || "lei") : "";
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
        <button class="buton-secundar" id="fac-mai-multe" style="margin-left:12px"${maiSunt ? "" : atributeInactiv("Toate facturile lunii sunt afișate.")}>Vezi \u0219i facturile mai vechi din aceast\u0103 lun\u0103</button></p>
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
        arataMesaj(zona, "Arhivă WinMentor descărcată (Facturi.txt + Articole.txt). În WinMentor: meniul „MENTOR → INTERNE → Import date din alte aplicații → Facturi ieșire”.", "ok");
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
            } catch (e2) { refuzPeRand(b, (e2 && e2.mesaj) || "eroare"); }   // [lotul 12, C164] sub buton, nu peste rândul lui
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
  // [lotul 12, 468] suma cu moneda ei scrisă: lei (RON) separat de euro; nicio sumă fără monedă
  const cuMoneda = (suma, m) => `${bani(suma)} ${monedaScrisa(m)}`;
  const solduriText = (sl, camp) => (sl || []).filter((x) => Number(x[camp]) > 0).map((x) => cuMoneda(x[camp], x.moneda)).join(" + ");
  const randFactura = (l) => {
    const s = SEM[l.stare] || SEM.fara_scadenta;
    const sub = l.stare === "restanta" ? `${cate(-l.zile, "zi de întârziere", "zile de întârziere")}`
      : l.stare === "scade_curand" ? `scade în ${cate(l.zile, "zi", "zile")}`
      : l.stare === "fara_scadenta" ? "fără scadență în sistem"
      : `scadență ${dataRo(l.data_scadenta)}`;
    // [lotul 12, 252] factura deschisă adusă la preluare (din programul vechi) se spune pe rând
    const preluata = l.tip === "preluata" ? " · preluată din programul vechi" : "";
    // [lotul 12, 466] încasată parțial: restul e suma rândului, iar totalul facturii se spune lângă
    const partial = l.stare_incasare && l.stare_incasare.stare === "partial"
      ? ` · încasată parțial, rest din ${cuMoneda(l.total_valuta, l.moneda)}` : "";
    // supapa per factura - doar cand notificarile sunt active (altfel n-ar avea efect)
    let valva = "";
    if (d.optin) {
      const amanat = l.notificare_amanata_pana && l.notificare_amanata_pana >= aziISO;
      valva = l.notificare_stop ? ` · <b>notificări oprite</b> <span class="btn-link" data-reia="${l.id}" data-actiune="PUT /tenants/{tenant_id}/facturi/{factura_id}/notificare">reia</span>`
        : amanat ? ` · amânat până ${dataRo(l.notificare_amanata_pana)} <span class="btn-link" data-reia="${l.id}" data-actiune="PUT /tenants/{tenant_id}/facturi/{factura_id}/notificare">reia</span>`
        : ` · <span class="btn-link" data-stop="${l.id}" data-actiune="PUT /tenants/{tenant_id}/facturi/{factura_id}/notificare">nu notifica</span> <span class="btn-link" data-amana="${l.id}" data-actiune="PUT /tenants/{tenant_id}/facturi/{factura_id}/notificare">amână 30 zile</span>`;
    }
    // [lotul 12, 467] rândul deschide factura (ca în „Istoric facturi”)
    return `
      <button class="buton-secundar pf-frand sc-fact-btn" data-id="${l.id}">
        <span class="cf-dot" style="background:${s.dot};flex-shrink:0"></span>
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${l.numar ? esc(numarCuSerie(l.serie, l.numar)) : "—"}${l.tert_nume ? " · " + esc(l.tert_nume) : ""}</div>
          <div class="pf-frand-sub">${sub}${preluata}${partial}${valva}</div>
        </div>
        <span class="pf-frand-suma">${cuMoneda(l.suma, l.moneda)}</span>
      </button>`;
  };
  const randFacturi = (linii) => {
    if (!(linii || []).length) return `<div class="stare-goala">Nicio factură emisă neîncasată.</div>`;
    return linii.map(randFactura).join("");
  };

  const randClienti = () => {
    if (!(d.clienti || []).length) return `<div class="stare-goala">Niciun client cu facturi neîncasate.</div>`;
    return d.clienti.map((c) => {
      // [lotul 12, 468] soldul și restanța PE MONEDĂ (serverul nu le mai adună): „1.210,00 lei + 500,00 EUR”
      const restant = solduriText(c.solduri, "restant");
      const rest = restant ? `<span style="color:var(--rosu)">${restant} restant</span> · ` : "";
      const fara = c.email ? "" : " · fără email";
      // [lotul 12, 467] rândul clientului deschide fișa lui
      return `
      <button class="buton-secundar pf-frand sc-client-btn" data-cheie="${esc(c.cheie)}">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(c.nume || c.cui || "—")}</div>
          <div class="pf-frand-sub">${cate(c.nr, "factură neîncasată", "facturi neîncasate")}${fara}</div>
        </div>
        <span class="pf-frand-suma">${rest}${solduriText(c.solduri, "sold")}</span>
      </button>`;
    }).join("");
  };

  const reincarca = async () => { try { d = await api.get(`/tenants/${tenantId}/scadentar`); } catch {} deseneaza(); };
  const supapa = async (fid, body) => {
    try { await api.put(`/tenants/${tenantId}/facturi/${fid}/notificare`, body); await reincarca(); }
    catch (e) { arataRefuzul(corp, e, corp.querySelector("#sc-msg")); }   // [lotul 11, 440]
  };
  // supapa și deschiderea facturii, pe rândurile din `zona` (lista scadențarului sau fișa clientului)
  const leagaRanduri = (zona) => {
    zona.querySelectorAll("[data-stop]").forEach((b) => b.addEventListener("click", (ev) => { ev.stopPropagation(); supapa(b.dataset.stop, { stop: true }); }));
    zona.querySelectorAll("[data-reia]").forEach((b) => b.addEventListener("click", (ev) => { ev.stopPropagation(); supapa(b.dataset.reia, { stop: false, amanata_pana: null }); }));
    zona.querySelectorAll("[data-amana]").forEach((b) => b.addEventListener("click", (ev) => {
      ev.stopPropagation();
      const pana = dataIso(new Date(Date.now() + 30 * 864e5));
      supapa(b.dataset.amana, { stop: false, amanata_pana: pana });
    }));
    zona.querySelectorAll(".sc-fact-btn").forEach((b) => b.addEventListener("click", () =>
      nav.mergi("Factură", (c) => detaliiFactura(c, nav, tenantId, b.dataset.id, opt))));
  };
  // [lotul 12, 467] „Fișă client”: facturile neîncasate ale clientului, cu soldul pe monedă; fiecare deschide factura
  const fisaClient = (c, cheie) => {
    const cl = (d.clienti || []).find((x) => x.cheie === cheie);
    const aleClientului = (d.linii || []).filter((l) => l.client_cheie === cheie);   // facturile clientului din Scadențar (afișare, nu un formular)
    if (!cl) { c.innerHTML = `<div class="stare-goala">Clientul nu mai are facturi neîncasate.</div>`; return; }
    const restant = solduriText(cl.solduri, "restant");
    c.innerHTML = `
      <h2 class="pf-titlu">Fișă client</h2>
      <p class="pf-intro"><b id="sc-fisa-client">${esc(cl.nume || cl.cui || "—")}</b> · ${cl.cui ? "Cod fiscal " + esc(cl.cui) + " · " : ""}${cate(cl.nr, "factură neîncasată", "facturi neîncasate")}${cl.email ? " · " + esc(cl.email) : " · fără email"}</p>
      <div class="cf-sumar" id="sc-fisa-sold">
        <span class="cf-pastila">De încasat: <b>${solduriText(cl.solduri, "sold")}</b></span>
        ${restant ? `<span class="cf-pastila"><span class="cf-dot" style="background:${SEM.restanta.dot}"></span>Restant: <b>${restant}</b></span>` : ""}
      </div>
      <div class="pf-lista zebra-lista" id="sc-fisa-lista">${randFacturi(aleClientului)}</div>`;
    leagaRanduri(c);
  };

  const deseneaza = () => {
    // [lotul 12, 469, DS cap.1 `.buton-activ`] vederea aleasă e marcată activă (albastru închis, apăsată), nu dezactivată: cea aleasă
    // arăta gri, ca un buton care nu merge, iar cealaltă părea cea activă
    const vb = (id, v, text) => `<button class="buton-secundar${vedere === v ? " buton-activ" : ""}" id="${id}" aria-pressed="${vedere === v}">${text}</button>`;
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
        ${vb("sc-facturi", "facturi", "Facturi neîncasate")}
        ${vb("sc-clienti", "clienti", "Fișă client")}
      </p>
      <div class="pf-lista zebra-lista" id="sc-lista">${vedere === "facturi" ? randFacturi(d.linii) : randClienti()}</div>`;
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
    leagaRanduri(corp);
    corp.querySelectorAll(".sc-client-btn").forEach((b) => b.addEventListener("click", () =>
      nav.mergi("Fișă client", (c) => fisaClient(c, b.dataset.cheie))));
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

// [lotul 12, 252] detaliul facturii deschise preluate: numărul, starea încasării, data și scadența, partenerul, restul de la preluare
const TEXT_FACTURA_PRELUATA = "Factură deschisă adusă la preluarea firmei, cu restul ei de la data preluării. Soldul ei e în balanța de deschidere: nu se contează și nu intră în declarații. Se stinge din Bancă, Casă sau Compensări.";
function detaliuFacturaPreluata(f) {
  const dir = dirEticheta(f.directie);
  const partener = f.tert_nume ? `${esc(f.tert_nume)}${f.tert_cui ? " \u00b7 CUI " + esc(f.tert_cui) : ""}` : "";
  return `
    <div class="fd-antet rezumat-fix">
      <div class="fd-antet-sus">
        <h2 class="pf-titlu">${esc(numarCuSerie(f.serie, f.numar))}</h2>
        <span class="fd-stare">preluată din programul vechi</span>
        ${f.stare_incasare ? `<span class="fd-stare${f.stare_incasare.stare === "incasata" ? " fd-stare-verde" : ""}">${esc(etichetaIncasare(f))}</span>` : ""}
      </div>
      <div class="fd-antet-linie">${dir ? dir.charAt(0).toUpperCase() + dir.slice(1) : ""} \u00b7 ${dataRo(f.data_emitere)}${f.data_scadenta ? " \u00b7 scaden\u021b\u0103 " + dataRo(f.data_scadenta) : " \u00b7 f\u0103r\u0103 scaden\u021b\u0103"}</div>
      ${partener ? `<div class="fd-antet-linie">${dir === "primit\u0103" ? "De la" : "C\u0103tre"}: ${partener}</div>` : ""}
      <div class="fd-antet-linie" id="fd-preluata">${TEXT_FACTURA_PRELUATA}</div>
      ${Number(f.tva) > 0 ? `<div class="fd-antet-linie" id="fd-preluata-tvai">TVA la încasare: ${_bani(f.tva, f.moneda || "RON")} încă ${f.directie === "primita" ? "nededus" : "neexigibil"} (4428); încasarea sau plata îl mută pe ${f.directie === "primita" ? "4426" : "4427"} și îl duce în D300 și D394.</div>` : ""}
    </div>
    <div class="bara-fixa"><div class="fd-totaluri">
      <div class="fd-tot-rand fd-tot-final"><span>Rest la preluare</span><span>${_bani(f.total, f.moneda || "RON")}</span></div>
    </div></div>`;
}

// [lotul 12, C164 — comanda Costin 12.3 pct.4, verbatim: „C164: pe ecranele scunde, antetul detaliului facturii se strânge pe un rând
// (număr, client, total, stare SPV); acțiunea principală rămâne fixă jos (clasa 285).”; DS cap.9 „Antetul documentului pe ecranul scund”]
// Pe un ecran mai scund decât antetul lipit, rezultatul unei acțiuni scris în antet nu mai putea intra în vedere (antetul nu derula). Ecranul
// scund îl spune stil.css (`--antet-scund: 1`, media query-ul pe înălțime — singura sursă a pragului): atunci rezumatul lipit sus devine
// rândul scurt (numărul, clientul, totalul, starea SPV), iar butoanele detaliului și zonele lor de rezultat coboară în bara lipită jos,
// lângă totaluri (DS cap.6, 285: acțiunea și mesajul ei se văd mereu). Restul antetului (stările, data, partenerul) rămâne deasupra
// tabelului și derulează. Se MUTĂ aceleași noduri (cu ascultătorii și conținutul lor), iar înapoi fiecare se pune exact în locul lui.
const ZONE_ACTIUNI = ["#fd-storno-zona", "#fd-chitanta-zona", "#fd-saga-zona", "#fd-spv-zona", "#fd-act-rez"];
function ecranScund(el) {
  return getComputedStyle(el || document.documentElement).getPropertyValue("--antet-scund").trim() === "1";
}
function aseazaAntetul(corp) {
  const scurt = corp.querySelector("#fd-antet-scurt"), antet = corp.querySelector(".fd-antet"), bara = corp.querySelector("#fd-bara-actiuni");
  if (!scurt || !antet || !bara) return;
  const scund = ecranScund(corp);
  if (scund === (scurt.dataset.scund === "1")) return;
  scurt.dataset.scund = scund ? "1" : "";
  const sus = antet.querySelector(".fd-antet-sus");
  // ce se mută: numărul și starea SPV în rândul scurt; butoanele (în ordinea lor) și zonele lor de rezultat în bară
  const deMutat = [[sus.querySelector(":scope > h2"), (el) => scurt.prepend(el)],
    [sus.querySelector(":scope > #fd-stare-spv"), (el) => scurt.append(el)]];
  let rand = bara.querySelector(".fd-bara-butoane");
  if (!rand) { rand = document.createElement("div"); rand.className = "fd-bara-butoane"; bara.appendChild(rand); }
  sus.querySelectorAll(":scope > button.buton-secundar").forEach((b) => deMutat.push([b, (el) => rand.appendChild(el)]));
  ZONE_ACTIUNI.forEach((s) => deMutat.push([antet.querySelector(":scope > " + s), (el) => bara.appendChild(el)]));
  if (!scund) {
    // înapoi: fiecare nod în locul lui din antet (semnul lăsat la plecare), rândul de butoane gol iese din bară
    [...scurt.children, ...rand.children, ...bara.children].forEach((el) => { if (el._fdLoc) { el._fdLoc.replaceWith(el); el._fdLoc = null; } });
    rand.remove();
  } else {
    deMutat.forEach(([el, pune]) => { if (!el) return; el._fdLoc = document.createComment("fd-loc"); el.before(el._fdLoc); pune(el); });
  }
  scurt.hidden = !scund;
  scurt.classList.toggle("rezumat-fix", scund);   // rezumatul lipit sus (navigatorul îl măsoară: `--rezumat-h`) e rândul scurt
  antet.classList.toggle("rezumat-fix", !scund);
}

// [lotul 13, deficiența 546] factura primită cu taxare inversă: furnizorul nu înscrie TVA-ul (CF art.331 alin.(3)), deci totalul de plată e
// baza; TVA-ul determinat de firmă (4426 = 4427, în decont colectat și deductibil) se arată separat, ca taxare inversă, nu în total
function randuriTaxareInversa(f, peCota, mon) {
  const cote = Object.keys(peCota).map(Number).sort((a, b) => b - a);
  return cote.map((c) => `<div class="fd-tot-rand"><span>Bază ${c}%</span><span>${_bani(peCota[c].baza, mon)}</span></div>`).join("") + `
      <div class="fd-tot-rand" id="fd-tva-ti"><span>TVA taxare inversă (art. 331): o determini tu, 4426 = 4427 — nu se plătește furnizorului</span><span>${_bani(f.tva_taxare_inversa, mon)}</span></div>
      <div class="fd-tot-rand fd-tot-final" id="fd-total-de-plata"><span>Total de plată</span><span>${_bani(f.total_de_plata, mon)}</span></div>`;
}

// [lotul 13, deficiența 547] factura primită se șterge cât nota ei e ciornă (serverul: `facturi_api._sterge_primita_cu_notele_ciorna`);
// altfel butonul stă inactiv, cu motivul (DS: comenzile se văd mereu, cele care nu se aplică inactive cu motiv — 675)
function motivStergerePrimita(f) {
  if (f.contabilizata) return "Nota facturii e validată: factura e în evidență și nu se mai șterge. Se corectează prin stornare.";
  if (f.stare_incasare && f.stare_incasare.stare !== "neincasata") return "Factura are plăți legate: dezleagă întâi plata (Bancă / Casă).";
  return "";
}

// [lotul 13, 673] confirmarea unei acțiuni făcute în fereastra deschisă peste detaliu (chitanța): detaliul se reface la întoarcere — păstrat
// sau redesenat de navigator — și o arată o dată, în zona lui de rezultat
const _laRevenire = {};
function laRevenire(tenantId, facturaId, arata) { _laRevenire[tenantId + ":" + facturaId] = arata; }
function mesajDupaRevenire(tenantId, facturaId, text, fel) {
  laRevenire(tenantId, facturaId, (c) => arataMesaj(c.querySelector("#fd-act-rez") || c, text, fel));
}

// [lotul 13, 675] de ce „Emite factura lunii” nu se aplică șablonului (butonul stă la locul lui, inactiv, cu motivul): aceleași condiții ca
// serverul (`facturi_recurente.de_emis(…, mod="ciorna")` -> `de_emis_acum`), spuse pe rând
function motivNeemis(s) {
  if (s.mod_emitere !== "ciorna") return "Șablonul se emite singur în ziua lui: nu se emite de mână.";
  if (!s.activ) return "Șablonul e dezactivat: „Activează” îl pune la loc.";
  const azi = dataIso();
  if (s.ultima_emitere && String(s.ultima_emitere).slice(0, 7) === azi.slice(0, 7)) return `Factura lunii s-a emis pe ${dataRo(s.ultima_emitere)}.`;
  if (s.data_inceput && String(s.data_inceput) > azi) return `Șablonul e valabil de la ${dataRo(s.data_inceput)}.`;
  if (s.data_sfarsit && String(s.data_sfarsit) < azi) return `Șablonul a fost valabil până la ${dataRo(s.data_sfarsit)}.`;
  if (Number(azi.slice(8, 10)) < Number(s.zi_emitere)) return `Ziua emiterii (${s.zi_emitere}) n-a venit.`;
  return "Factura lunii din acest șablon nu e de emis azi.";
}

async function detaliiFactura(corp, nav, tenantId, facturaId, opt) {
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;

  let f = null;
  try {
    f = await api.get(`/tenants/${tenantId}/facturi/${facturaId}`);
  } catch {
    arataMesaj(corp, "Nu s-a putut încărca factura.", "eroare");
    return;
  }

  // [lotul 12, deficiența 252] factura deschisă preluată: e a programului vechi, cu restul ei de la preluare — fără acțiuni de document
  // fiscal (serverul le refuză și el: `facturi_api.refuza_sold_preluat`)
  if (f.tip === "preluata") { corp.innerHTML = detaliuFacturaPreluata(f); return; }
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
  // [lotul 13, 675 — DS cap.1 v2.104: „entitățile de același tip (… facturi …) au același set de butoane, în aceeași ordine; ce nu se
  // aplică stă inactiv, cu motivul la trecerea cu mouse-ul”] butoanele detaliului sunt aceleași pe orice document; cel care nu se aplică
  // stă la locul lui, inactiv (`atributeInactiv`), cu motivul. Ascunse rămân numai acțiunile refuzate ROLULUI (portalul clientului,
  // `opt.client`; DS cap.9 v2.64). Motivul gol = butonul se aplică.
  const emisa = f.directie === "emisa", eFactura = f.tip === "factura";
  const felDoc = eFactura ? "factură" : (f.tip === "proforma" ? "proformă" : (f.tip === "aviz" ? "aviz" : "document"));
  const inactivDaca = (motiv) => (motiv ? atributeInactiv(motiv) : "");
  const motiv = {
    trimiteEmail: emisa ? "" : "Factura primită e a furnizorului: nu se trimite pe email din iConta.",
    sterge: emisa ? "Factura emisă nu se șterge: se corectează prin stornare." : (!eFactura ? "Se șterge numai o factură primită."
      : motivStergerePrimita(f)),
    storno: !emisa ? "Factura primită se stornează de furnizor: stornarea lui intră ca factură primită."
      : (f.storno_din_id ? "E chiar o factură de stornare." : (stornata ? "Factura e stornată integral: nu mai e nimic de stornat." : "")),
    transforma: f.transformat_in_id ? "Documentul e transformat deja în factură." : (eFactura || !f.tip ? "Documentul e deja factură." : ""),
    chitanta: !emisa ? "Chitanța se emite numai pe o factură emisă." : (!eFactura ? "Chitanța se emite pe factură, nu pe " + felDoc + "."
      : (f.storno_din_id ? "Factura de stornare nu se încasează." : (f.platita_la ? "Factura e încasată."
      : (stornata ? "Factura e stornată integral: nu mai e nimic de încasat." : "")))),
    saga: !emisa ? "Exportul SAGA din detaliu e pentru facturile emise." : (!eFactura ? "Exportul SAGA e pentru facturi, nu pentru " + felDoc + "." : ""),
    spv: !emisa ? "Factura primită vine din SPV: nu se trimite." : (!eFactura ? "În SPV se trimit facturile, nu " + felDoc + "-ul."
      : (f.din_efactura || "")),
  };

  // [lotul 10, deficiențele 421 / 424, DS cap.9 v2.96] „rezumatul stă fix sus și acțiunea principală fix jos; se derulează doar tabelul
  // din mijloc”: antetul facturii (numărul, stările, acțiunile, zona lor de mesaj, data și partenerul) e rezumatul — rămâne lipit sus cât
  // se derulează liniile, deci rezultatul unei acțiuni („Trimite în SPV”, „Emite chitanță”) se vede și de la capătul tabelului.
  // [lotul 12, C164] pe ecranul scund rezumatul e rândul scurt `#fd-antet-scurt`, iar acțiunile coboară în bara de jos (`aseazaAntetul`)
  corp.innerHTML = `
    <div class="fd-antet-scurt" id="fd-antet-scurt" hidden>
      <span class="fd-scurt-client" title="${esc(f.tert_nume || "")}">${esc(f.tert_nume || "")}</span>
      <span class="fd-scurt-total">${_bani(f.total_de_plata != null ? f.total_de_plata : f.total, mon)}</span>
    </div>
    <div class="fd-antet rezumat-fix">
      <div class="fd-antet-sus">
        <h2 class="pf-titlu">Factur\u0103 ${f.numar ? esc(numarCuSerie(f.serie, f.numar)) : "\u2014"}</h2>
        ${statusTxt ? `<span class="fd-stare">${esc(statusTxt)}</span>` : ""}
        ${opt.client ? "" : `<button class="btn-link" id="fd-vezi-nota"${nc ? "" : atributeInactiv("Factura n-are încă notă contabilă: nota se propune la contare.")}>${nc ? "nota " + esc(nc.eticheta || "") : "nota contabilă"}</button>`}
        <button class="buton-secundar em-buton-sec fd-pdf-btn" id="fd-pdf">PDF factur\u0103</button>
        <button data-actiune="POST /tenants/{tenant_id}/facturi/{factura_id}/email" class="buton-secundar em-buton-sec fd-email-btn" id="fd-email"${inactivDaca(motiv.trimiteEmail)}>Trimite pe email</button>
        ${opt.client ? "" : `<button data-actiune="DELETE /tenants/{tenant_id}/facturi/{factura_id}" class="buton-secundar em-buton-sec" id="fd-sterge"${inactivDaca(motiv.sterge)}>Șterge factura</button>`}
        ${opt.client ? "" : `<button data-actiune="POST /tenants/{tenant_id}/facturi/{factura_id}/storno" class="buton-secundar em-buton-sec fd-storno-btn" id="fd-storno"${inactivDaca(motiv.storno)}>Storneaz\u0103</button>`}
        <button class="buton-secundar em-buton-sec" id="fd-transforma" data-actiune="POST /tenants/{tenant_id}/facturi/{factura_id}/transforma"${inactivDaca(motiv.transforma)}>Transform\u0103 \u00een factur\u0103</button>
        ${f.stare_incasare ? `<span class="fd-stare${f.stare_incasare.stare === "incasata" ? " fd-stare-verde" : ""}">${esc(etichetaIncasare(f))}</span>` : ""}
        ${f.stare_spv ? `<span class="fd-stare${f.stare_spv.stare === "acceptata" ? " fd-stare-verde" : ""}" id="fd-stare-spv" title="${esc(etichetaSpv(f))}">${esc(etichetaSpv(f))}</span>` : ""}
        ${f.platita_la && f.plata_confirmata_de === "mock" ? '<span class="fd-stare fd-stare-galben" title="Confirmare de simulare, nu de la un procesator de pl\u0103\u021bi. Nu dovede\u0219te c\u0103 au intrat bani.">pl\u0103tit\u0103 prin simulare</span>' : ""}
        <!-- [06.09.2026] Butonul «Link plata» a fost SCOS: calea de plata online e inchisa prin
             decizie — incasarea se face prin transfer bancar, confirmat din extras. Eticheta
             «platita prin SIMULARE» de mai sus RAMANE: nicio factura n-o poarta azi, dar daca
             vreuna ar purta-o vreodata, nu are voie sa treaca drept incasare obisnuita. -->
        <button class="buton-secundar em-buton-sec" id="fd-chitanta" data-actiune="POST /tenants/{tenant_id}/chitante"${inactivDaca(motiv.chitanta)}>Emite chitan\u021b\u0103</button>
        <button class="buton-secundar em-buton-sec" id="fd-saga"${inactivDaca(motiv.saga)}>Export SAGA</button>
        <!-- [C62] și stornarea pleacă în SPV: OUG 120/2021 art.4 alin.(10) — „Factura electronică corectată se transmite în cadrul
             aceluiași sistem național privind factura electronică RO e-Factura”; XML-ul ei trimite la factura stornată (BG-3, 417) -->
        <!-- [lotul 11, C86] factura emisă venită din XML-ul e-Factura e deja transmisă de cine a emis-o: fără „Trimite în SPV” (serverul
             refuză și el, efactura_trimitere.refuz_din_efactura), cu motivul în locul butonului — textul vine de la server -->
        ${(f.directie === "emisa" && f.tip === "factura" && f.din_efactura) ? `<span class="fd-stare" id="fd-spv-motiv">${esc(f.din_efactura)}</span>` : ""}
        <button class="buton-secundar em-buton-sec" id="fd-spv" data-actiune="POST /tenants/{tenant_id}/facturi/{factura_id}/trimite-spv"${inactivDaca(motiv.spv)}>Trimite în SPV</button>
        <!-- [lotul 13, 675] „transformată în …” e o STARE a documentului (ca „stornată”), cu legătura spre factura rezultată: apare numai când
             starea există; acțiunea e „Transformă în factură”, care stă mereu la locul ei -->
        ${f.transformat_in_id ? `<span class="fd-stare"><button class="btn-link" id="fd-vezi-transformata">transformat\u0103 \u00een ${esc(f.transformat_in_numar ? numarCuSerie(f.transformat_in_serie, f.transformat_in_numar) : "factur\u0103")}</button></span>` : ""}
      </div>
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
    <div class="bara-fixa"><div class="fd-bara-actiuni" id="fd-bara-actiuni"></div><div class="fd-totaluri">   <!-- [lotul 11, decizia Costin 10.3: „Totalurile … fix”] totalurile facturii rămân jos, în vedere (DS cap.9 v2.100) -->
      ${f.tva_taxare_inversa != null ? randuriTaxareInversa(f, peCota, mon) : `${randuriTot}
      <div class="fd-tot-rand fd-tot-final"><span>Total</span><span>${_bani(f.total, mon)}</span></div>`}
    </div></div>`;


  aseazaAntetul(corp);   // [lotul 12, C164] rândul scurt + acțiunile jos pe ecranul scund; urmărește și schimbarea ecranului
  const dupaRevenire = _laRevenire[tenantId + ":" + facturaId];   // [lotul 13, 673] confirmarea acțiunii din fereastra de deasupra
  if (dupaRevenire) {
    delete _laRevenire[tenantId + ":" + facturaId];
    dupaRevenire(corp);
  }
  if (!corp._fdAsezare) {
    corp._fdAsezare = () => { if (corp.isConnected) aseazaAntetul(corp); };
    window.addEventListener("resize", corp._fdAsezare);
  }

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
              arataMesaj(zonaSpv, "Structură invalidă — nu s-a trimis. ANAF:\n" + (r.erori || []).join("\n"), "avert");
            } else {
              // [lotul 10, 10.2 pct.7f — clasa lui 419: starea veche rămâne pe detaliu după act] trimiterea schimbă starea SPV a facturii:
              // detaliul se reface ACUM (eticheta „netrimisă în SPV · termen …” din antet nu mai rămâne lângă „în prelucrare”), iar
              // răspunsul stă în zona de mesaj a detaliului refăcut — nu în zona SPV, pe care starea citită o rescrie (DS cap.27 v2.94)
              const trimisa = r.stare === "incarcat" || r.stare === "in_prelucrare";
              await detaliiFactura(corp, nav, tenantId, facturaId, opt);
              arataMesaj(corp.querySelector("#fd-act-rez") || corp, trimisa
                ? "Trimisă în SPV (index " + (r.index_incarcare || "—") + "). ANAF o prelucrează; recipișa se preia separat."
                : (r.stare === "eroare_upload" ? (r.erori || []).join("\n")   // [lotul 12, clasa 598] eroarea trimiterii e a aplicației, nu răspuns ANAF
                  : "Răspuns ANAF:\n" + (r.erori || [r.mesaj || "eroare"]).join("\n")), trimisa ? "ok" : "avert");
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
        // [lotul 12, C164] sub buton (`refuzPeRand`), nu în locul lui: `arataMesaj` pe părinte ștergea butonul „PDF chitanță”
        refuzPeRand(b, (e && (e.mesaj || e.message)) || "eroare");
      }
    }));
    return incasat;
  }
  if (zonaChit) arataChitante();
  // [lotul 13, 673 — DS cap.2a v2.104] „Emite chitanță” deschide formularul într-o fereastră nouă (înainte: un rând de câmpuri în zona
  // chitanțelor detaliului). După emitere, „←” e făcut de ecran: detaliul se reface de la server, cu confirmarea în zona lui (DS cap.27)
  if (bChit) bChit.addEventListener("click", async () => {
    const chi = await chitanteAle();
    const incasat = chi.reduce((s, c) => s + (Number(c.suma) || 0), 0);
    const rest = Math.max(0, Math.round((totalDeIncasat - incasat) * 100) / 100);
    nav.deschide("Emite chitanță", (c2) => {
      c2.innerHTML = `
      <div id="fd-chit-form" style="display:flex;gap:8px;align-items:end;flex-wrap:wrap;margin:8px 0">
        <label class="camp"><span class="camp-eticheta">Data \u00eencas\u0103rii<span class="oblig">*</span></span><input class="camp-input" type="date" id="fd-chit-data" value="${dataIso()}"></label>
        <label class="camp"><span class="camp-eticheta">Suma \u00eencasat\u0103 (lei)<span class="oblig">*</span></span><input class="camp-input" type="number" step="0.01" id="fd-chit-suma" value="${rest || totalDeIncasat}"></label>
        <button class="buton-primar" id="fd-chit-ok" data-actiune="POST /tenants/{tenant_id}/chitante">Emite</button>
        <button class="btn-link" id="fd-chit-nu">Renun\u021b\u0103</button>
        <span class="msg-eroare" id="fd-chit-msg"></span>
      </div>`;
      const form = c2.querySelector("#fd-chit-form");
      form.querySelector("#fd-chit-nu").addEventListener("click", () => nav.inapoi());
      // funcția are nume: după seria stabilită pe loc (543) emiterea se reia chemând-o, nu printr-un clic dat de cod
      form.querySelector("#fd-chit-ok").addEventListener("click", async function emiteChitanta() {
        const b = form.querySelector("#fd-chit-ok"), msg = form.querySelector("#fd-chit-msg");
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
          // [lotul 10, 10.2 pct.7f — clasa lui 419: „rămâne «neîncasată» până la reîmprospătare”] chitanța schimbă starea de încasare:
          // detaliul se reface ACUM, de la server (starea, lista chitanțelor, „Emite chitanță” numai cât mai e ceva de încasat), iar
          // confirmarea stă în zona de mesaj a detaliului refăcut (DS cap.27 v2.93–v2.94) — și când navigatorul îl redesenează la întoarcere
          mesajDupaRevenire(tenantId, facturaId, `Chitan\u021ba ${esc(numarCuSerie(r.serie, String(r.numar)))} a fost emis\u0103 \u0219i \u00eenregistrat\u0103 \u00een Registrul de cas\u0103.${av.length ? " Aten\u021bie: " + av.join(" ") : ""}`,
            av.length ? "avert" : "ok");
          nav.inapoi();
          if (corp.isConnected) await detaliiFactura(corp, nav, tenantId, facturaId, opt);   // fereastra păstrată: se reface aici
        } catch (e) {
          b.disabled = false; b.textContent = "Emite";
          if (cereSeriaChitanteiPeLoc(msg, tenantId, e, emiteChitanta)) return;   // [lotul 13, 543] seria se cere pe loc
          arataRefuzul(form, e, msg, { campuri: { suma: "fd-chit-suma", data: "fd-chit-data" } });   // [lotul 11, 440] câmpurile serverului lângă ele
        }
      });
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
        // [R131] motivul serverului; [lotul 12, C164] în zona de rezultat a detaliului, nu în părintele butonului: `arataMesaj` pe rândul
        // butoanelor îi rescria tot conținutul (numărul, stările și toate acțiunile dispăreau, înlocuite de mesaj)
        arataMesaj(corp.querySelector("#fd-act-rez") || corp, (e && (e.mesaj || e.message)) || "eroare", "eroare");
        btnPdf.textContent = txtVechi;
      } finally {
        btnPdf.disabled = false;
        if (btnPdf.textContent === "Se genereaz\u0103\u2026") btnPdf.textContent = txtVechi;
      }
    });
  }

  const btnSterge = corp.querySelector("#fd-sterge");
  if (btnSterge && !motiv.sterge) {
    btnSterge.addEventListener("click", () => {
      const zr = corp.querySelector("#fd-act-rez");
      confirmaCaseta(zr, `Ștergi factura ${esc(numarCuSerie(f.serie, f.numar))} de la ${esc(f.tert_nume || "furnizor")}? Se șterg și notele ei, care sunt încă ciornă (nimic din ea n-a intrat în evidență).`, async () => {
        try {
          await api.del(`/tenants/${tenantId}/facturi/${facturaId}`);
          corp.innerHTML = `<h2 class="pf-titlu">Factură ștearsă</h2><div id="fd-sters-rez"></div>`;
          arataMesaj(corp.querySelector("#fd-sters-rez"), `Factura ${esc(numarCuSerie(f.serie, f.numar))} de la ${esc(f.tert_nume || "furnizor")} și notele ei ciornă au fost șterse.`, "ok");
          butonInapoi(corp.querySelector("#fd-sters-rez"), nav);
        } catch (e) { arataRefuzul(corp, e, zr); }
      }, { textOk: "Șterge factura" });
    });
  }

  const btnEmail = corp.querySelector("#fd-email");
  // [lotul 13, 673 — DS cap.2a v2.104: „orice acțiune din orice fereastră: deschide o fereastră nouă, centrată”] „Trimite pe email” își
  // deschide formularul într-o fereastră nouă (înainte: o bandă în antetul detaliului); „←” readuce detaliul facturii
  if (btnEmail) btnEmail.addEventListener("click", () => {
    nav.deschide("Trimite factura pe email", (c2) => {
      c2.innerHTML = `
        <div class="fd-email-box">
          <label for="fd-email-input" class="fd-email-eticheta">Trimite factura ${esc(numarCuSerie(f.serie, f.numar))} c\u0103tre:</label>
          <div class="fd-email-rand">
            <input type="email" id="fd-email-input" class="camp-input fd-email-input" placeholder="email@client.ro" value="${esc(f.tert_email || "")}">
            <button class="buton-primar fd-email-send" id="fd-email-send" data-actiune="POST /tenants/{tenant_id}/facturi/{factura_id}/email">Trimite</button>
          </div>
          <div class="em-rezultat" id="fd-email-rez"></div>
        </div>`;
      const inp = c2.querySelector("#fd-email-input");
      focusFaraSalt(inp);
      c2.querySelector("#fd-email-send").addEventListener("click", async () => {
        const rez = c2.querySelector("#fd-email-rez");
        const send = c2.querySelector("#fd-email-send");
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
  });

  const btnVeziNota = corp.querySelector("#fd-vezi-nota");
  if (btnVeziNota) btnVeziNota.addEventListener("click", async () => {
    const { ecranJurnal } = await import("./firme.js?v=4c2b4e3117");   // dinamic: firme.js importă deja ecranul facturilor
    const [an, luna] = String(nc.data).split("-").map(Number);
    nav.deschide("Registru jurnal", (c2) => ecranJurnal(c2, nav, { id: tenantId }, { an, luna, evidentiaza: nc.id }), { lat: "tabel" });   // [394] [470] pe nota facturii
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
  // [lotul 12, C84, decizia Costin 12.3 pct.7] a doua întrebare a emiterii, „Ai dovada transportului?” (livrarea intracomunitară de bunuri,
  // `INTREABA_DOVADA_TRANSPORT`, după „Pleacă marfa acum?”): răspunsurile date se păstrează și pleacă împreună la retrimitere
  if (btnTransforma) btnTransforma.addEventListener("click", () => {
    const raspunsuri = {};
    const transforma = async (pleacaMarfa) => {
      if (pleacaMarfa != null) raspunsuri.pleaca_marfa = pleacaMarfa;
      btnTransforma.disabled = true;
      try {
        const r = await api.post(`/tenants/${tenantId}/facturi/${f.id}/transforma`, { ...raspunsuri });
        await detaliiFactura(corp, nav, tenantId, f.id, opt);
        // [C64, DS cap.27 v2.94] confirmarea peste detaliul redesenat, în zona ei — nu în locul lui; „transformată în …” e drumul spre factură
        // [lotul 11, 428] factura din proform\u0103 / aviz \u00een sistemul TVA la \u00eencasare: acela\u0219i text ca la emitere
        // [lotul 12, 443.1] seria și numărul separat („F1A nr. 15”), ca în Istoric
        const zonaRez = corp.querySelector("#fd-act-rez");
        arataMesaj(zonaRez, `Factura ${numarCuSerie(r.serie, r.numar)} a fost emis\u0103${textDescarcare(r.descarcare)}${textTvaIncasare(r.contare)}.`, "ok");
        arataAvertismenteEmitere(zonaRez, r.avertismente);   // [lotul 12, C157 / C84] emisă, cu ce trebuie știut — ca la „Emite factură”
      } catch (e) {
        btnTransforma.disabled = false;
        const zona = corp.querySelector("#fd-act-rez");
        if (e && e.detaliu && e.detaliu.cod === "INTREABA_PLEACA_MARFA") {
          intrebarePleacaMarfa(zona, (f.linii || []).filter((l) => l && l.articol_id).length, transforma, { da: "fd-poarta-da", nu: "fd-poarta-nu" });
          return;
        }
        if (e && e.detaliu && e.detaliu.cod === "INTREABA_DOVADA_TRANSPORT") {
          intrebareDovadaTransport(zona, e.detaliu.intrebare, (da) => { raspunsuri.dovada_transport = da; transforma(null); },
            { da: "fd-dovada-da", nu: "fd-dovada-nu" });
          return;
        }
        if (zona) zona.innerHTML = "";   // întrebarea la care s-a răspuns nu rămâne lângă refuz
        refuzPeRand(btnTransforma, ((e && e.mesaj) || "Nu s-a putut transforma."));
      }
    };
    transforma(null);
  });
  // [lotul 13, 673 — DS cap.2a v2.104: „fereastra mică rămâne doar pentru confirmări”] „Stornează” cere confirmarea într-o fereastră mică
  // (înainte: o casetă în antetul detaliului, care pe ecranul scund cobora în bara de jos și ieșea din vedere). După stornare, „←” e făcut de
  // ecran: detaliul se reface de la server (starea „stornată”), cu confirmarea în zona stornării lui (DS cap.27 v2.93–v2.94)
  if (btnStorno) {
    corp.querySelector("#fd-storno").addEventListener("click", () => {   // = btnStorno; selectorul pe rând leagă handlerul de buton (drepturi_ui)
      // [deficiența 419] factura care a descărcat stocul: întrebarea „marfa se întoarce?” — alegere explicită, fără răspuns implicit
      const iesiri = f.iesiri_stoc || [];
      const intrebareRetur = iesiri.length ? `
          <label class="camp" style="margin-top:10px;display:block"><span class="camp-eticheta">Marfa ieșită cu factura (${esc(iesiri.map((x) => x.articol + " × " + x.cantitate_text).join("; "))}) se întoarce în stoc?</span>
            ${selectDaNu('id="fd-storno-retur"', null, "Marfa se întoarce în stoc")}
            <span class="camp-ajutor">Da = retur: marfa revine în magazie, iar costul ieșirii se stornează. Nu = marfa rămâne la client (numai corecția valorii): stocul nu se schimbă.</span></label>` : "";
      nav.deschide("Stornează factura", (c2) => {
        c2.innerHTML = `
          <div class="fd-storno-box">
            <div class="fd-storno-avert" style="margin-bottom:0">Se creeaz\u0103 o factur\u0103 de stornare pentru <b>${esc(numarCuSerie(f.serie, f.numar))}</b> (valori negative, document contabil). Ac\u021biunea nu poate fi anulat\u0103.</div>
            ${intrebareRetur}
          </div>
          <div class="fd-storno-actiuni" style="margin:10px 0 14px">
            <button class="buton-primar" id="fd-storno-ok" data-actiune="POST /tenants/{tenant_id}/facturi/{factura_id}/storno">Confirm stornarea</button>
            <button class="buton-secundar" id="fd-storno-nu">Renun\u021b\u0103</button>
          </div>
          <div class="em-rezultat" id="fd-storno-rez"></div>`;
        c2.querySelector("#fd-storno-nu").addEventListener("click", () => nav.inapoi());
        c2.querySelector("#fd-storno-ok").addEventListener("click", async () => {
          const rez = c2.querySelector("#fd-storno-rez");
          const ok = c2.querySelector("#fd-storno-ok");
          curataEroriCamp(c2);
          if (cereAlegerile(c2, ["#fd-storno-retur"])) return;   // [419] fără răspuns nu se trimite
          const corpStorno = iesiri.length ? { retur: daNu(c2.querySelector("#fd-storno-retur")) } : {};
          ok.disabled = true; ok.textContent = "Se storneaz\u0103\u2026";
          try {
            const r = await api.post(`/tenants/${tenantId}/facturi/${facturaId}/storno`, corpStorno);
            const retur = (r.retur || []).length ? ` Marfa a revenit în stoc: ${esc(r.retur.map((x) => x.articol + " × " + cantitate(x.cantitate, x.um)).join("; "))} (notele de retur sunt ciornă, în Registrul jurnal).` : "";
            // [lotul 10, 10.2 pct.7f, 419] detaliul se reface ACUM, de la server (starea „stornată”, „Stornează” / „Emite chitanță” inactive),
            // iar confirmarea se pune în zona de stornare a detaliului refăcut (DS cap.27 v2.93–v2.94)
            laRevenire(tenantId, facturaId, (c) => {
              const zs = c.querySelector("#fd-storno-zona");
              if (!zs) { arataMesaj(c, `Storno creat: ${numarCuSerie(r.serie, r.numar)}.`, "ok"); return; }
              zs.innerHTML = `<div class="em-rezultat em-bun" id="fd-storno-rez">\u2713 Storno creat: <b>${esc(numarCuSerie(r.serie, r.numar))}</b>${esc(textTvaIncasare(r.contare))}.${retur}</div>`;
              // [418c / 410, DS cap.27] confirmarea (și returul) rămâne pe ecran; istoricul se deschide la cererea omului
              const bi = document.createElement("button");
              bi.type = "button"; bi.className = "buton-secundar"; bi.id = "fd-spre-istoric"; bi.style.marginLeft = "10px";
              bi.textContent = "Înapoi la Istoric facturi";
              bi.addEventListener("click", () => istoricFacturi(c, nav, tenantId, opt));
              zs.querySelector("#fd-storno-rez").appendChild(bi);
            });
            nav.inapoi();
            if (corp.isConnected) await detaliiFactura(corp, nav, tenantId, facturaId, opt);   // fereastra păstrată: se reface aici
          } catch (e) {
            arataRefuzul(c2, e, rez);   // [lotul 11, 440] câmpurile refuzului (returul pe linie) lângă ele, restul aici
            rez.className = "em-rezultat em-rau";
            ok.disabled = false; ok.textContent = "Confirm stornarea";
          }
        });
      }, { lat: "mic" });
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
        // [lotul 12, C109 \u2014 comanda Costin 12.3 pct.1, verbatim: \u201epe \u0219ablon se vede \u0219i starea ultimei emiteri\u201d] ultima factur\u0103 emis\u0103 \u0219i,
        // dac\u0103 emiterea automat\u0103 a fost refuzat\u0103 dup\u0103 ea, refuzul cu ziua \u0219i motivul (golit la urm\u0103toarea emitere reu\u0219it\u0103) \u2014 DS cap.8:
        // starea \u00een text, cu tokenul de text `--rosu`
        const emisa = s.ultima_emitere ? `ultima factur\u0103 emis\u0103: ${dataRo(s.ultima_emitere)}` : "nicio factur\u0103 emis\u0103 \u00eenc\u0103";
        const refuz = s.ultimul_refuz
          ? `<div class="pf-frand-sub fr-refuz" id="fr-refuz-${s.id}"><span style="color:var(--rosu)">Emiterea automat\u0103 refuzat\u0103 la ${dataRo(s.ultimul_refuz_la)}:</span> ${esc(s.ultimul_refuz)}</div>`
          : "";
        // [lotul 13, 680] cum se emite (singură / ciornă), SPV-ul, scadența și perioada, scrise pe rând; ciorna lunii, cu „Emite factura lunii”
        const mod = s.mod_emitere === "ciorna" ? "ciornă pregătită — o emiți tu" : "se emite singură" + (s.trimite_spv ? " și pleacă în SPV" : "");
        const scad = s.scadenta_zile != null ? ` \u00b7 scadența la ${cate(s.scadenta_zile, "zi", "zile")}` : "";
        const perioada = s.data_inceput ? ` \u00b7 valabil ${dataRo(s.data_inceput)} – ${s.data_sfarsit ? dataRo(s.data_sfarsit) : "până la oprire"}` : "";
        return `
      <div class="pf-frand" data-id="${s.id}">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(s.tert_nume) || "\u2014"}</div>
          <div class="pf-frand-sub">ziua ${s.zi_emitere} \u00b7 ${emisa} \u00b7 ${stare}${s.tert_tara && s.tert_tara !== "RO" ? ` \u00b7 client din ${esc(s.tert_tara)}` : ""}</div>
          <div class="pf-frand-sub fr-mod-rand">${esc(mod)}${scad}${perioada}</div>
          ${refuz}
          <div class="fr-rez" id="fr-rez-${s.id}"></div>
        </div>
        <span class="pf-frand-suma">${sumaTxt}</span>
        <button type="button" class="buton-primar fr-emite" data-actiune="POST /tenants/{tenant_id}/facturi-recurente/{sid}/emite" data-id="${s.id}" style="margin-left:8px"${s.de_emis_acum ? "" : atributeInactiv(motivNeemis(s))}>Emite factura lunii</button>
        <button type="button" class="buton-secundar fr-toggle" data-actiune="PUT /tenants/{tenant_id}/facturi-recurente/{sid}" data-id="${s.id}" data-activ="${s.activ}" style="margin-left:8px">${s.activ ? "Dezactiveaz\u0103" : "Activeaz\u0103"}</button>
        <button type="button" class="buton-secundar fr-sterge" data-actiune="DELETE /tenants/{tenant_id}/facturi-recurente/{sid}" data-id="${s.id}" style="margin-left:8px">\u0218terge</button>
      </div>`;
      }).join("");

  corp.innerHTML = `
    <h2 class="pf-titlu">Facturi recurente ${semnAjutor("F047")}</h2>
    <p class="pf-intro">\u0218abloanele facturilor lunare: fiecare se emite singur în ziua lui sau se pregătește ca ciornă, pe care o emiți tu (verificare zilnic\u0103 la 07:00).</p>
    <div class="pf-lista zebra-lista">${corpuri}</div>
    <button class="buton-primar" id="fr-add" data-actiune="POST /tenants/{tenant_id}/facturi-recurente" style="margin-top:12px">+ \u0218ablon nou</button>
    <div id="fr-msg" role="alert"></div>`;
  corp.querySelector("#fr-add").addEventListener("click", () => nav.mergi("\u0218ablon nou", (c) => formSablon(c, nav, tenantId, opt)));  // faza_b_traseu_v1

  corp.querySelectorAll(".fr-emite").forEach((b) => b.addEventListener("click", async () => {
    const z = corp.querySelector(`#fr-rez-${b.dataset.id}`);
    b.disabled = true;
    try {
      const r = await api.post(`/tenants/${tenantId}/facturi-recurente/${b.dataset.id}/emite`, {});
      b.remove();
      arataMesaj(z, `Factura ${esc(r.factura || "")} a fost emisă din șablon.` + ((r.avertismente || []).length ? " " + r.avertismente.join(" ") : ""),
        (r.avertismente || []).length ? "avert" : "ok");
    } catch (e) { b.disabled = false; arataMesaj(z, (e && e.mesaj) || "Factura nu s-a emis.", "eroare"); }
  }));
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
// [lotul 12, comanda 12.3 pct.9] cota și categoria liniei șablonului: aceeași formă și aceleași clase ca linia emiterii, dintr-o singură
// sursă (`emitere_ecran.js`: `clasaCotei`, `htmlCotaLinie`, `htmlCategorieLinie`)

// [lotul 12, comanda Costin 12.3 pct.9, verbatim: „Da: cota și categoria pe linia șablonului recurent, ca la factură.”] Cotele în vigoare,
// categoriile cotei 0% și bunurile cu taxare inversă vin de la ruta „Emite factură” (`facturi/numerotare`, `facturi_api.pregatire_emitere`),
// statutul de plătitor din vector (ca acolo). Cota aleasă și categoria pleacă pe linia șablonului, iar categoria produsului (art.331) pe
// șablon; proba de la salvare și emiterea lunară le verifică ca la factura obișnuită (`categorii_tva.verifica_linii`).
export async function formSablon(corp, nav, tenantId, opt) {
  const inapoiLista = () => nav.inapoiPas();  // faza_b_traseu_v1
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  let num = {}, tvaProfil = null;
  // [lotul 12, integrarea I3 — clasa „citire tăcută”] cotele, categoriile și statutul de plătitor fac formularul: dacă nu se pot citi,
  // se spune și formularul nu se deschide (înainte: listă de cote goală și plătitor presupus, fără niciun semn)
  try {
    num = (await api.get(`/tenants/${tenantId}/facturi/numerotare?data=${dataIso()}`)) || {};
    const _v = await api.get(`/tenants/${tenantId}/vector`);
    if (_v && typeof _v.platitor_tva === "boolean") tvaProfil = _v.platitor_tva;
  } catch (e) {
    arataMesaj(corp, (e && e.mesaj) || "Cotele de TVA și statutul de plătitor al firmei nu s-au putut citi, deci șablonul nu se poate completa. Încearcă din nou.", "eroare");
    return;
  }
  const platitor = tvaProfil !== false;   // profilul fără statut: ca la emitere, plătitor (lista cotelor), nu cota 0 presupusă
  // [lotul 13, 680] clienții firmei (fișele și partenerii facturilor emise), pentru alegerea beneficiarului ca la „Emite factură” —
  // citiți după desenarea formularului (`incarcaClientii`); o citire eșuată se spune sub CUI
  let clienti = [];
  const COTE = (num.cote_permise && num.cote_permise.length) ? num.cote_permise : [];
  const CATEG = platitor ? (num.categorii_tva || []) : [];
  const C331 = num.categorii_331 || [];
  corp.innerHTML = `
    <h2 class="pf-titlu">Șablon nou</h2>

    <div class="em-sectiune">
      <div class="em-eticheta">Beneficiar</div>
      <label class="camp-eticheta" for="fr-client-cauta">Alege din clienți (fișele și clienții facturilor)</label>
      <input class="camp-input" id="fr-client-cauta" placeholder="Caută după nume sau cod fiscal…" autocomplete="off">
      <select class="camp-input" id="fr-client" aria-label="Clientul din listă">
        <option value="">— alege clientul —</option>
      </select>
      <label class="camp-eticheta" for="fr-cui">CUI beneficiar</label>
      <div class="em-cui-rand"><input class="camp-input" id="fr-cui" placeholder="ex: RO12345678" autocomplete="off">
        <button type="button" class="buton-secundar" id="fr-anaf" data-actiune="GET /tenants/{tenant_id}/verifica-cui/{cui}">Verifică la ANAF</button></div>
      <div id="fr-anaf-stare"></div>
      <label class="camp-eticheta" for="fr-tara">Țara beneficiarului</label>
      <select class="camp-input" id="fr-tara">${optiuniTara()}</select>
      <label class="camp-eticheta" for="fr-nume">Denumire beneficiar</label>
      <input class="camp-input" id="fr-nume" autocomplete="off">
    </div>

    <div class="em-sectiune">
      <div class="em-eticheta">Produse și servicii</div>
      <div class="camp-eticheta">Linie: denumire · cantitate · preț unitar · cotă TVA${platitor && CATEG.length ? " (la 0%, categoria de TVA)" : ""}</div>
      <div class="em-linii" id="fr-linii"></div>
      <button class="buton-secundar em-buton-sec" id="fr-add-linie" data-fara-actiune="rând în formular; salvarea formularului poartă acțiunea">+ Adaugă linie</button>
      <label class="camp-eticheta" for="fr-c331" id="fr-c331-et" hidden>Categoria produsului cu taxare inversă (art.331; codul din D394)</label>
      <select class="camp-input" id="fr-c331" hidden><option value="">— alege —</option>${C331.map((c) => `<option value="${esc(c.cod)}">${esc(c.eticheta)}</option>`).join("")}</select>
    </div>

    <div class="em-sectiune">
      <div class="em-eticheta">Emitere</div>
      <p class="pf-intro" id="fr-serie">Seria facturilor: <b>${esc(num.serie || "nestabilită încă (se cere la prima emitere)")}</b> — numerotarea firmei, aceeași ca la „Emite factură”.</p>
      <div class="grila-doc" style="grid-template-columns:1fr 1fr 1fr">
        <label class="camp"><span class="camp-eticheta">Ziua din lună la care se emite (1–28)<span class="oblig">*</span></span>
          <input class="camp-input" id="fr-zi" type="number" min="1" max="28"></label>
        <label class="camp"><span class="camp-eticheta">Moneda</span><select class="camp-input" id="fr-moneda">${optiuniMoneda("RON")}</select></label>
        <label class="camp"><span class="camp-eticheta">Termen de plată (zile de la emitere)<span class="oblig">*</span></span>
          <input class="camp-input" id="fr-scadenta" type="number" min="0" max="365"></label>
      </div>
      <div class="grila-doc" style="grid-template-columns:1fr 2fr">
        <label class="camp"><span class="camp-eticheta">Valabil de la<span class="oblig">*</span></span><input class="camp-input" id="fr-inceput" type="date"></label>
        <div class="camp"><span class="camp-eticheta">Până când<span class="oblig">*</span></span>
          <div class="em-optiuni" id="fr-pana" role="group" aria-label="Până când e valabil șablonul">
            <button type="button" class="buton-secundar" data-val="data">Până la o dată</button>
            <button type="button" class="buton-secundar" data-val="oprire">Până îl opresc</button>
          </div>
          <input class="camp-input" id="fr-sfarsit" type="date" hidden aria-label="Valabil până la"></div>
      </div>
      <div class="camp"><span class="camp-eticheta">Cum se emite factura lunii<span class="oblig">*</span></span>
        <div class="em-optiuni" id="fr-mod" role="group" aria-label="Cum se emite factura lunii">
          <button type="button" class="buton-secundar" data-val="automata">Se emite singură, în ziua ei</button>
          <button type="button" class="buton-secundar" data-val="ciorna">Ciornă pregătită — o emit eu</button>
        </div></div>
      <div class="camp" id="fr-spv-camp" hidden><span class="camp-eticheta">După emitere, în SPV (RO e-Factura)<span class="oblig">*</span></span>
        <div class="em-optiuni" id="fr-spv" role="group" aria-label="Trimiterea în SPV">
          <button type="button" class="buton-secundar" data-val="true">Pleacă singură în SPV</button>
          <button type="button" class="buton-secundar" data-val="false">O trimit eu din Istoric facturi</button>
        </div></div>
    </div>

    <div class="em-actiuni">
      <button class="buton-primar" id="fr-salveaza" data-actiune="POST /tenants/{tenant_id}/facturi-recurente">Salvează șablonul</button>
    </div>
    <div class="em-rezultat" id="fr-rezultat"></div>`;

  const zonaLinii = corp.querySelector("#fr-linii");
  const linii = [];
  const _val = (x) => (x === "" || x == null) ? "" : esc(String(x));
  // [comanda Costin 06.10.2026 pct.1b, clasa] rândul nou NU poartă un preț (era 0): „un preț pe care nu l-a ales nimeni nu se propune”
  // [lotul 13, 680] la neplătitor cota e 0 prin lege (CF art.310 alin.(10) lit.b) și se arată de la început („0%”, nu „—”)
  // [lotul 13, regula UM — `facturi.um_linie`] UM-ul liniei pornește gol: îl scrie omul sau vine, vizibil, din nomenclator (UM-ul produsului,
  // „serv.” la servicii); gol la salvare -> refuzul lângă câmp (`facturi_recurente.verificari_drum`)
  const linieNoua = () => ({ descriere: "", cantitate: 1, um: "", pret_unitar: "", cota_tva: platitor ? null : 0, cota_propusa: null, categorie_tva: null });

  // randeaza O linie DIN MODEL, id-uri pozitionale fr-l{i}-* (cap.24: id derivat din pozitie, ca backendul sa
  // lege eroarea de camp). Buton de stergere pe fiecare rand (cap.24 regula 3).
  function randLinie(i) {
    const l = linii[i];
    return `<div class="em-linie" data-idx="${i}">
      <input class="camp-input em-l-den" id="fr-l${i}-descriere" data-actiune-camp="POST /tenants/{tenant_id}/produse/potriveste" value="${_val(l.descriere)}" placeholder="Denumire (ex: abonament mentenanță)" aria-label="Denumire articol" autocomplete="off">
      <input class="camp-input em-l-cant" id="fr-l${i}-cantitate" type="number" step="0.001" value="${_val(l.cantitate)}" placeholder="Cant." aria-label="Cantitate" title="Cantitate">
      <input class="camp-input em-l-um" id="fr-l${i}-um" maxlength="10" value="${_val(l.um)}" aria-label="Unitate de măsură" title="Unitate de măsură">
      <input class="camp-input em-l-pret" id="fr-l${i}-pret_unitar" type="number" step="0.01" value="${_val(l.pret_unitar)}" placeholder="Preț" aria-label="Preț unitar" title="Preț unitar">
      ${htmlCotaLinie("fr-l" + i + "-cota", l, COTE, platitor)}
      <button type="button" class="buton-sters em-l-sterge" data-idx="${i}" title="Șterge">×</button>
      ${platitor ? htmlCategorieLinie("fr-l" + i + "-categorie", l, CATEG) : ""}
    </div>`;
  }

  // categoria produsului (art.331) se cere cât timp o linie e cu taxare inversă — ca la emitere (`actualizeazaC331`)
  function actualizeazaC331() {
    const are = linii.some((x) => x.categorie_tva === "taxare_inversa");
    ["#fr-c331", "#fr-c331-et"].forEach((s) => { const e = corp.querySelector(s); if (e) e.hidden = !are; });
  }
  // cota stabilită (propusă, aleasă, golită) pe OBIECTUL l, la poziția lui curentă; categoria se cere numai la 0%
  function setCota(l, cota, text) {
    const p = linii.indexOf(l);
    if (p < 0) return;
    const el = zonaLinii.querySelector("#fr-l" + p + "-cota");
    if (el && el.tagName === "SELECT") {
      el.value = cota == null ? "" : String(cota);
      el.className = "camp-input em-l-cota-sel" + clasaCotei(cota);
      el.title = l.cota_propusa == null ? "Cota TVA" : "Cota TVA — propusă: " + l.cota_propusa + "%";
    } else if (el) {
      el.textContent = text != null ? text : (cota == null ? "—" : cota + "%");
      el.className = "em-l-cota" + clasaCotei(cota);
    }
    const sc = zonaLinii.querySelector("#fr-l" + p + "-categorie");
    if (sc) {
      sc.hidden = l.cota_tva !== 0;
      if (l.cota_tva !== 0) { sc.value = ""; l.categorie_tva = null; } else sc.value = l.categorie_tva || "";
    }
    actualizeazaC331();
  }

  // inputurile scriu in MODEL (fara re-randare la tastare -> fara pierdere de focus). Fetch-ul cotei capteaza
  // OBIECTUL l (nu indexul) -> scrie corect chiar daca un splice a reindexat lista intre timp.
  function legaLinie(i) {
    const l = linii[i];
    const den = zonaLinii.querySelector("#fr-l" + i + "-descriere");
    const cant = zonaLinii.querySelector("#fr-l" + i + "-cantitate");
    const pret = zonaLinii.querySelector("#fr-l" + i + "-pret_unitar");
    const um = zonaLinii.querySelector("#fr-l" + i + "-um");
    const del = zonaLinii.querySelector('.em-l-sterge[data-idx="' + i + '"]');
    // UM-ul propus (nu scris de om) se schimbă cu denumirea; cel scris de om rămâne al lui
    const puneUm = (v) => { if (l.umScris) return; l.um = v; const e = zonaLinii.querySelector("#fr-l" + linii.indexOf(l) + "-um"); if (e) e.value = v; };
    let timer = null;
    const cerereCota = ultimaCerere();   // [C103] denumirea scrisă în reprize: numai cota pentru ultima denumire ajunge pe linie
    den.addEventListener("input", () => {
      l.descriere = den.value.trim();
      l.cota_tva = null; l.cota_propusa = null; l.categorie_tva = null; l.cotaAleasa = false;   // denumire nouă, propunere nouă (ca la emitere)
      puneUm("");
      clearTimeout(timer);
      const actuala = cerereCota();   // și o denumire scurtă (fără cerere) oprește cota cerută înainte
      const d = l.descriere;
      if (d.length < 3) { setCota(l, null); return; }
      // neplătitorul: cota e 0 prin lege, nu o propunere (CF art.310 alin.(10) lit.b) — fără cerere de potrivire
      if (!platitor) { l.cota_tva = 0; setCota(l, 0); return; }
      setCota(l, null, "…");
      timer = setTimeout(async () => {
        try {
          const r = await api.post(`/tenants/${tenantId}/produse/potriveste`, { denumire: d });
          if (!actuala()) return;
          if (r && r.ok) {
            l.cota_propusa = r.cota;
            if (l.cotaAleasa) { setCota(l, l.cota_tva); return; }   // cota aleasă de om între timp rămâne a lui; propunerea, în titlu
            l.cota_tva = r.cota;
            // [lotul 11, 449] la cota 0 din nomenclator, categoria de TVA a produsului se propune (ca la emitere)
            if (r.cota === 0 && r.categorie_tva) l.categorie_tva = r.categorie_tva;
            setCota(l, r.cota);
            if (r.um) puneUm(r.um); else if (r.tip === "servicii") puneUm(UM_SERVICIU);   // [regula UM] propunerea, vizibilă (ca la emitere)
          } else if (!l.cotaAleasa) setCota(l, null);
        } catch { if (!actuala() || l.cotaAleasa) return; setCota(l, null); }
      }, 400);
    });
    const selCota = zonaLinii.querySelector("select#fr-l" + i + "-cota");
    if (selCota) selCota.addEventListener("change", () => {   // contabilul alege; propunerea rămâne în titlul listei
      l.cota_tva = selCota.value === "" ? null : Number(selCota.value);
      l.cotaAleasa = true;
      setCota(l, l.cota_tva);
    });
    const selCateg = zonaLinii.querySelector("#fr-l" + i + "-categorie");
    if (selCateg) selCateg.addEventListener("change", () => { l.categorie_tva = selCateg.value || null; actualizeazaC331(); });
    cant.addEventListener("input", () => { l.cantitate = Number(cant.value) || 0; });
    um.addEventListener("input", () => { l.um = um.value.trim(); l.umScris = !!l.um; });
    pret.addEventListener("input", () => { const v = parseFloat(pret.value); l.pret_unitar = Number.isFinite(v) ? v : ""; });   // [pct.1b] golul rămâne gol
    del.addEventListener("click", () => { const p = linii.indexOf(l); if (p >= 0) linii.splice(p, 1); deseneazaLinii(); });
  }

  // re-randare INTEGRALA din model (cap.24 regula 1): nu se muta noduri individual; valorile tastate pe randurile
  // ramase supravietuiesc (sunt in model). Se re-leaga listenerii cu indici proaspeti.
  function deseneazaLinii() {
    zonaLinii.innerHTML = linii.map((_, i) => randLinie(i)).join("");
    linii.forEach((_, i) => legaLinie(i));
    actualizeazaC331();
  }

  corp.querySelector("#fr-add-linie").addEventListener("click", () => { linii.push(linieNoua()); deseneazaLinii(); });
  // [lotul 12, C160] țara clientului DEDUSĂ din codul fiscal, ca la „Emite factură” (DS cap.17): vizibilă și modificabilă din listă
  corp.querySelector("#fr-cui").addEventListener("change", (ev) => {
    const t = taraDinCui(ev.target.value), sel = corp.querySelector("#fr-tara");
    if (t && sel.value !== t) sel.value = t;
  });
  linii.push(linieNoua());  // prima linie
  deseneazaLinii();

  // [lotul 13, 680] alegerile cu butoane alăturate (DS 676: listele scurte nu sunt liste derulante): nimic ales din oficiu
  const alegeri = {};
  const legaAlegere = (id, laSchimbare) => corp.querySelectorAll(`#${id} button`).forEach((b) => b.addEventListener("click", () => {
    corp.querySelectorAll(`#${id} button`).forEach((x) => x.classList.toggle("buton-activ", x === b));
    alegeri[id] = b.dataset.val;
    if (laSchimbare) laSchimbare(b.dataset.val);
  }));
  legaAlegere("fr-pana", (v) => { corp.querySelector("#fr-sfarsit").hidden = v !== "data"; });
  legaAlegere("fr-mod", (v) => { corp.querySelector("#fr-spv-camp").hidden = v !== "automata"; });
  legaAlegere("fr-spv");
  // beneficiarul ales din clienți (căutare deasupra listei, ca articolul pe linia facturii) sau verificat la ANAF (ca la „Emite factură”)
  const selCl = corp.querySelector("#fr-client"), cautaCl = corp.querySelector("#fr-client-cauta");
  cautaCl.addEventListener("input", () => {
    const q = cautaCl.value.trim().toLowerCase();
    [...selCl.options].forEach((o) => { if (o.value) o.hidden = !!q && !o.dataset.cauta.includes(q); });
  });
  const anafFr = legaDateAnaf(corp.querySelector("#fr-cui"), [corp.querySelector("#fr-nume")], corp.querySelector("#fr-anaf-stare"));
  let clientId = null;
  selCl.addEventListener("change", () => {
    const c = clienti[Number(selCl.value)];
    clientId = c && c.id ? c.id : null;
    if (!c) return;
    corp.querySelector("#fr-cui").value = c.cui || "";
    corp.querySelector("#fr-nume").value = c.nume || "";
    const t = taraDinCui(c.cui || ""); if (t) corp.querySelector("#fr-tara").value = t;
  });
  corp.querySelector("#fr-anaf").addEventListener("click", async () => {
    const cui = corp.querySelector("#fr-cui").value.trim(), st = corp.querySelector("#fr-anaf-stare");
    curataEroriCamp(corp);
    if (!cui) { eroareCamp(corp, "fr-cui", "Scrie codul fiscal ca să-l verifici la ANAF."); return; }
    try {
      const r = await api.get(`/tenants/${tenantId}/verifica-cui/${encodeURIComponent(cui)}`);
      if (!(r && r.gasit)) { st.textContent = "CUI negăsit la ANAF."; return; }
      anafFr.pune([r.denumire], { suprascrie: true });
      st.innerHTML = `<span class="em-cui-info">La ANAF: „${esc(r.denumire)}” · ${r.platitor_tva ? "plătitor TVA" : "neplătitor TVA"}.</span>`;
    } catch (e) { st.textContent = (e && e.mesaj) || "Verificarea nu s-a putut face — reîncearcă."; }
  });

  // plaseaza erorile field-keyed din 422 (backendul: erori_campuri [{camp: fr-l{i}-.., mesaj}]) LANGA campul lor
  // (cap.6 mecanism A). Cele fara #camp in DOM -> zona generica (fallback B).
  corp.querySelector("#fr-salveaza").addEventListener("click", async () => {
    curataEroriCamp(corp);
    // NU se filtreaza randuri (cap.24 regula 2): lista trimisa = lista randata. Un rand incomplet se valideaza
    // pe backend si se raporteaza langa campul lui, nu dispare tacit.
    const c331 = corp.querySelector("#fr-c331");
    const corpCerere = {
      tert_cui: corp.querySelector("#fr-cui").value.trim() || null,
      tert_nume: corp.querySelector("#fr-nume").value.trim(),
      tert_tara: corp.querySelector("#fr-tara").value,   // [C160] țara clientului, până la emitere
      client_id: clientId,   // [lotul 13, 680] clientul ales din listă (fișa lui)
      zi_emitere: corp.querySelector("#fr-zi").value === "" ? null : Number(corp.querySelector("#fr-zi").value),
      moneda: corp.querySelector("#fr-moneda").value,
      // [lotul 13, 680] întrebările emiterii, fiecare aleasă de om (serverul refuză lipsa, lângă câmp)
      scadenta_zile: corp.querySelector("#fr-scadenta").value === "" ? null : Number(corp.querySelector("#fr-scadenta").value),
      data_inceput: corp.querySelector("#fr-inceput").value || null,
      valabil_pana: alegeri["fr-pana"] || null,
      data_sfarsit: alegeri["fr-pana"] === "data" ? (corp.querySelector("#fr-sfarsit").value || null) : null,
      mod_emitere: alegeri["fr-mod"] || null,
      trimite_spv: alegeri["fr-spv"] === "true" ? true : (alegeri["fr-spv"] === "false" ? false : null),
      linii: linii.map((l) => ({ descriere: l.descriere, cantitate: l.cantitate, um: (l.um || "").trim(),   // [regula UM] gol = refuzat lângă câmp
        pret_unitar: (l.pret_unitar === "" || l.pret_unitar == null) ? null : l.pret_unitar, cota_tva: l.cota_tva,   // [pct.1b] gol = lipsă, refuzat lângă câmp
        ...(l.cota_tva === 0 && l.categorie_tva ? { categorie_tva: l.categorie_tva } : {}) })),   // [12.3 pct.9] categoria liniei cu 0%, ca la emitere (lipsa ei = linia fără categorie)
      categorie_331: c331 && !c331.hidden ? (c331.value || null) : null,   // [12.3 pct.9] bunul cu taxare inversă (art.331)
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
  // [lotul 13, 680] lista clienților, după ce toate butoanele sunt legate (un clic dat cât se citește lista nu se pierde)
  try {
    const rc = await api.get(`/tenants/${tenantId}/clienti`);
    clienti = [...((rc && rc.clienti) || []), ...((rc && rc.parteneri_fara_fisa) || [])].filter((x) => x.nume || x.cui);
    selCl.insertAdjacentHTML("beforeend", clienti.map((c, i) => `<option value="${i}" data-cauta="${esc(String((c.nume || "") + " " + (c.cui || "")).toLowerCase())}">${esc(c.nume || "")}${c.cui ? " · " + esc(c.cui) : ""}</option>`).join(""));
    if (!clienti.length) { selCl.disabled = cautaCl.disabled = true; selCl.title = cautaCl.title = "Niciun client încă: scrie codul fiscal și verifică-l la ANAF."; }
  } catch (e) {
    selCl.disabled = cautaCl.disabled = true;
    arataMesaj(corp.querySelector("#fr-anaf-stare"), `Lista clienților nu s-a putut citi (${(e && e.mesaj) || "eroare"}): scrie codul fiscal și verifică-l la ANAF.`, "avert");
  }
}

// chitante_fe_v1

// chitante_fe_v2_etichete

// audit_cab_lot1_v1

// faza_b_traseu_v1

// fara_precompletari_v1
