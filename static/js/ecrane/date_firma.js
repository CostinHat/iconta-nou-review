// date_firma.js — [date_firma_v1] datele fiscale ale firmei.
// Campurile pe care ANAF le cere OBLIGATORIU in declaratii. Pana azi nu existau
// deloc in interfata: firma_profil_api salva doar font/culoare/logo (modelul de
// factura), iar caen/telefon/banca/iban/reg_com se puteau completa doar direct in
// baza de date. O firma noua nu putea depune nicio declaratie.
// DS: cap.6 (asterisc pe obligatorii + ghidaj camp-ajutor + validari preventive cu
// mesaj explicativ), cap.9 (.grila-doc), cap.3 (nav.setInapoi).
// Apelare: randeazaDateFirma(corp, nav, tenantId, { inapoi })
import { api, arataMesaj, esc, eroareCamp, curataEroriCamp, dataRo, alegeDacaLipseste, focusFaraSalt, cate, confirmaCaseta, refuzPeRand, bani, arataRefuzul, numarCuSerie, atributeInactiv, numarRo } from "../api.js?v=cb524f997d";

// camp -> {eticheta, obligatoriu, ajutor}. Obligatoriile vin din validatoarele
// declaratiilor (core/firma_profil_api.OBLIGATORII) - o singura sursa de adevar.
const CAMPURI = [
  // [R81 → BLOC R, 28.08.2026] Câmpul `nume` A IEȘIT de aici. Istoricul lui, în trei pași, fiindcă
  // fiecare pas a fost adevărat la momentul lui:
  //   27.08 — eticheta „Denumirea firmei" s-a despărțit în două, fiindcă firma avea DOUĂ denumiri
  //           în două locuri, iar pe 4 din 17 chiar difereau;
  //   28.08 — R81 s-a decis (simetrie de scriere): cele două nu mai pot diferi, deci ecranul avea
  //           două casete pentru o singură valoare, iar salvarea trimitea două cereri care se
  //           puteau suprascrie tăcut una pe alta. Le-am legat, ca reparație imediată;
  //   28.08 — decizia lui Costin: **se comasează.** Legarea era un plasture pe un duplicat;
  //           duplicatul iese. Denumirea se editează într-un singur loc, sus, prin
  //           `PUT /tenants/{id}` — care scrie amândouă coloanele.
  // `firma_profil.nume` NU dispare din bază și nu iese din payload-ul de CITIRE: rămâne coloana
  // care pleacă pe declarații. Ce dispare e a doua CALE de scriere din ecranul ăsta.
  { k: "cui", e: "CUI", ob: true },
  { k: "reg_com", e: "Nr. registrul comer\u021bului", ob: true,
    aj: "Din certificatul de \u00eenregistrare (ex. J40/1234/2020).", ajOb: "Cerut la bilan\u021b." },
  { k: "caen", e: "Cod CAEN", ob: true,
    aj: "4 cifre, din certificatul constatator. ANAF nu \u00eel d\u0103 pentru toate firmele \u2014 completeaz\u0103-l manual." },
  { k: "adresa", e: "Adresa", ob: true },
  { k: "oras", e: "Localitatea", ob: true },   // [C69] D406 o cere în antet (S.AD.5 City „Mandatory”)
  { k: "judet", e: "Jude\u021bul", ob: true },   // [C69] bilanțul o cere (codTT „Cod judet sediu … DA”)
  { k: "cod_postal", e: "Cod po\u0219tal" },
  { k: "banca", e: "Banca", ob: true, aj: "Banca prin care se fac decont\u0103rile." },
  { k: "iban", e: "IBAN", ob: true },
  // [lotul 10, C69, decizia Costin „Varianta 1”] lângă IBAN: firma fără cont bancar scrie în D406 „Fara cont bancar” (schema ANAF S.BA.2);
  // rulajul / soldul pe 512 în perioadă o contrazice și oprește D406. Coloana are valoare mereu (Nu), deci se arată cea salvată.
  { k: "fara_cont_bancar", e: "Nu are cont bancar", tip: "danu",
    aj: "Da numai dacă firma nu are niciun cont la bancă: D406 declară atunci că firma nu are cont bancar, în locul IBAN-ului." },
  { k: "telefon", e: "Telefon", ob: true },
  // [R63] Nu „E-mail": la adresa asta pleaca pachetul lunar (`pachete_api`), iar ea NU e adresa
  // cu care clientul intra in portal. Doua campuri, doua nume.
  { k: "email", e: "E-mail firmă (aici se trimite pachetul lunar)" },
  // [R66] Numele administratorului: se tipărește pe adeverințe și pe contracte. Până azi
  // niciun ecran nu-l scria, iar documentele ieșeau cu un gol.
  { k: "patron_nume", e: "Nume administrator",
    aj: "Cine semnează pentru firmă. Apare pe adeverințe și pe contractele de muncă." },
  { k: "declarant_nume", e: "Nume declarant", ob: true },
  // [R101, 30.08.2026] OBLIGATORIU: structura ANAF a fiecareia din cele opt declaratii cere
  // `prenume_declar` cu marcaj DA. Pana azi campul era optional aici, iar generatorul il
  // fabrica drept "-" — o valoare inventata pe un document care pleaca la ANAF.
  { k: "declarant_prenume", e: "Prenume declarant", ob: true },
  { k: "declarant_functie", e: "Func\u021bia declarantului", ob: true },
  // [lotul 10, C69, decizia Costin „Câmpuri noi + blocaj”] cerute de bilanț (bifa marilor contribuabili / codul județului și forma de
  // proprietate, din nomenclatorul ANAF); neales = „— alege —”, salvarea îl lasă necompletat, bilanțul îl cere (DS cap.17, pct.5)
  { k: "mare_contribuabil", e: "Mare contribuabil", ob: true, tip: "danu",
    aj: "Da dacă firma e administrată de Direcția Generală de Administrare a Marilor Contribuabili.", ajOb: "Cerut la bilanț." },
  { k: "forma_proprietate", e: "Forma de proprietate", ob: true, tip: "lista", lista: "forme_proprietate",
    aj: "Din nomenclatorul ANAF al bilanțului (ex. societăți cu răspundere limitată).", ajOb: "Cerut la bilanț." },
  // [lotul 11, decizia Costin 10.3 pct.4] „interesul public în Date firmă” — bilanțul: „15. interes_public Entitati de interes public N(1)
  // DA” (structura ANAF SC 1225); neales = „— alege —”, bilanțul îl cere (generatorul scria 0 oricărei firme)
  { k: "interes_public", e: "Entitate de interes public", ob: true, tip: "danu",
    aj: "Da numai pentru entitățile de interes public definite de lege (ex. bănci, societăți de asigurare, societăți listate).", ajOb: "Cerut la bilanț." },
  // [lotul 13, deficiența 595, decizia Costin 26.10.2026 „6 da”] înregistrarea în regimul special OSS se întreabă aici, nu în formularul D398
  // (o singură sursă): neales = „— alege —” (fără răspuns implicit), D398 se oprește până se răspunde; nu e „obligatoriu” oricărei firme
  { k: "inregistrat_oss", e: "Înregistrată în regimul special OSS (a depus declarația de începere a activității)", tip: "danu",
    aj: "Răspunde Da numai dacă firma a depus declarația de începere a activității sale supuse regimului special de TVA (CF art.315 alin.(3)); D398 se generează numai atunci." },
];

// [lotul 11, deficiența 442] câmpurile capitalului (blocul „Capital social”), cu numele lor în „Profil incomplet” — „blochează emiterea
// facturilor” (Legea 31/1990 art. 74 alin. (3); aceeași regulă care refuză emiterea, `capital_social.lipsa`)
const ETICHETE_CAPITAL = { forma_juridica: "Forma juridică", capital_subscris: "Capital social subscris", capital_varsat: "Capital social vărsat" };

// [D394 Î2] Activitatea exceptată de la casa de marcat — OUG 28/1999 art. 2. Cu ea, chitanțele fără factură (cu cota
// lor) intră în D394 la Î2; încasările din casă nelegate de o factură/chitanță se semnalează (decizia lui Costin, 03.10.2026).
function _blocAmef(d) {
  const p = d.profil || {};
  const act = d.activitati_amef || [];
  return `
    <h2 class="pf-titlu" style="margin-top:26px">Casa de marcat</h2>
    <p class="pf-intro">Firmele care încasează din activități exceptate de la casa de marcat (OUG 28/1999 art. 2) emit chitanțe fără factură; încasările lor se declară în D394, secțiunea Î2.</p>
    <div class="grila-doc">
      <label class="camp">
        <span class="camp-eticheta">Activitate exceptată de la casa de marcat</span>
        <!-- [lotul 07.10 B, comanda Costin A.3] neales (NULL) = „— alege —”; se cere o dată, la prima chitanță fără factură / D394 -->
        <select class="camp-input" id="df-activitate_exceptata_amef" data-butoane="">${alegeDacaLipseste(p.activitate_exceptata_amef)}
          <option value="0"${p.activitate_exceptata_amef === false ? " selected" : ""}>Nu</option>
          <option value="1"${p.activitate_exceptata_amef === true ? " selected" : ""}>Da</option>
        </select>
      </label>
      <label class="camp" id="df-activitate_amef-camp"${p.activitate_exceptata_amef ? "" : ' style="display:none"'}>
        <span class="camp-eticheta">Activitatea (OUG 28/1999 art. 2)<span class="oblig">*</span></span>
        <select class="camp-input" id="df-activitate_amef"><option value="">— alege —</option>${act.map(([k, t]) =>
          `<option value="${esc(k)}"${k === p.activitate_amef ? " selected" : ""}>${esc(k)}) ${esc(t)}</option>`).join("")}</select>
      </label>
    </div>`;
}

// [lot 19 d12] Capitalul social pe factură — Legea 31/1990 art. 74 alin. (3): SRL -> capitalul social; SA/SCA ->
// capitalul subscris și cel vărsat. Fără ele, factura unei societăți nu se emite (decizia lui Costin, 03.10.2026).
function _blocCapital(d) {
  const p = d.profil || {};
  const forme = d.forme_juridice || [];
  // [comanda Costin 05.10.2026 pct.2] forma necompletată, dar neechivocă (ANAF / denumire): preselectată, cu sursa spusă — se
  // confirmă salvând. Nu se scrie tacit în profil: e o propunere, iar alegerea rămâne a contabilului.
  const formaAleasa = p.forma_juridica || d.forma_juridica_propusa || "";
  const notaPropusa = !p.forma_juridica && d.forma_juridica_propusa
    ? `<span class="camp-ajutor" id="df-forma-propusa">Propusă din ${d.forma_juridica_sursa === "ANAF" ? "ANAF" : "denumirea firmei"}: ${esc(d.forma_juridica_propusa)} — verifică și salvează.</span>` : "";
  return `
    <h2 class="pf-titlu" style="margin-top:26px">Capital social</h2>
    <p class="pf-intro">Se tipărește pe facturi: la SRL capitalul social, la SA și SCA capitalul subscris și cel vărsat (Legea 31/1990 art. 74 alin. (3)). Fără el, factura unei societăți nu se emite.</p>
    <div class="grila-doc">
      <label class="camp">
        <span class="camp-eticheta">Forma juridică<span class="oblig">*</span></span>
        ${notaPropusa}
        <select class="camp-input" id="df-forma_juridica"><option value="">— alege —</option>${forme.map(([k, t]) =>
          `<option value="${esc(k)}"${k === formaAleasa ? " selected" : ""}>${esc(t)}</option>`).join("")}</select>
      </label>
      <label class="camp">
        <span class="camp-eticheta">Capital social subscris (lei)</span>
        <span class="camp-ajutor">Din actul constitutiv / certificatul constatator. La SRL, acesta e capitalul social.</span>
        <input type="number" step="0.01" min="0" class="camp-input" id="df-capital_subscris" value="${esc(p.capital_subscris || "")}">
      </label>
      <label class="camp">
        <span class="camp-eticheta">Capital social vărsat (lei)</span>
        <span class="camp-ajutor">Obligatoriu la SA și SCA.</span>
        <input type="number" step="0.01" min="0" class="camp-input" id="df-capital_varsat" value="${esc(p.capital_varsat || "")}">
      </label>
    </div>`;
}

// [06.10.2026, comanda Costin §6.3] Metoda de stoc: setare EXPLICITĂ, fără implicit — până se alege, „nedeclarată”, iar ieșirile
// de marfă și facturile cu marfă se refuză numit (core/metoda_stoc.py). De ea depinde cum se descarcă marfa, o singură dată.
// [decizia Costin 07.10.2026, pct.5] Seria chitanțelor: o stabilește firma (OMFP 2634/2015 anexa 1 pct.24), nu aplicația — fără
// „CH” din oficiu. Necompletată, prima chitanță se refuză cu trimitere aici; odată scrisă, nu se mai șterge.
function _blocChitante(d) {
  const sc = (d.profil || {}).serie_chitanta || "";
  return `
    <h2 class="pf-titlu" style="margin-top:26px">Chitanțe</h2>
    <div class="grila-doc">
      <label class="camp">
        <span class="camp-eticheta">Seria chitanțelor</span>
        <input class="camp-input" id="df-serie_chitanta" maxlength="10" value="${esc(sc)}" placeholder="litere și cifre, ex. seria din chitanțier" aria-label="Seria chitanțelor">
      </label>
    </div>`;
}

function _blocStoc(d) {
  const m = (d.profil || {}).metoda_stoc || "";
  return `
    <h2 class="pf-titlu" style="margin-top:26px">Stoc</h2>
    <p class="pf-intro">Cum ține firma evidența mărfii. Global-valoric: marfa se descarcă lunar, din toate vânzările (371/378/4428). Cantitativ-valoric: pe fiecare articol, la CMP (fișe de magazie, rețete). Fiecare ieșire se descarcă o singură dată.</p>
    <div class="grila-doc">
      <label class="camp">
        <span class="camp-eticheta">Metoda de stoc</span>
        <select class="camp-input" id="df-metoda_stoc">${m ? "" : `<option value="" selected>— nedeclarată —</option>`}${(d.metode_stoc || []).map(([k, t]) =>
          `<option value="${esc(k)}"${k === m ? " selected" : ""}>${esc(t)}</option>`).join("")}</select>
      </label>
    </div>`;
}

// [08.10.2026, decizia Costin §6 pct.4] „Luna preluării: editabilă în Date firmă, cu valoarea dedusă ca propunere, dar niciodată după
// luna primei note.” Nesalvată = propunerea (core/luna_preluare.py); de la ea se numără restanțele în Control fiscal.
// [retest 08.10 pct.20] „câmpul arată «---------- ----»; vine completat cu propunerea (06/2026), fără textul «Gol = propunerea»”.
// Câmpul arată luna efectivă (salvată, altfel propunerea); cât timp nu e schimbat, la salvare nu se trimite (rămâne ce era: propunerea
// rămâne propunere, deci se recalculează dacă se schimbă soldurile de preluare) — completarea nu fixează tacit o valoare pe care omul
// n-a ales-o. Luna aleasă egală cu propunerea, sau câmpul golit, = propunerea (null).
// [lotul 12, 169] Câmpul golit nu rămâne „---------- ----” (așa arată Chromium o lună goală): la ieșirea din câmp revine propunerea.
// [lotul 12, 147] Luna salvată e după prima notă (o notă mai veche, scrisă după alegere): câmpul arată luna efectivă, a primei note
// (`luna_preluare.efectiva`, plafonată), și spune de ce — limita „niciodată după prima notă” ține și după salvare.
function _blocPreluare(d) {
  const lp = (d.profil || {}).luna_preluare || {};
  const ro = (x) => (x ? `${x.slice(5, 7)}/${x.slice(0, 4)}` : "");
  const plafonata = lp.plafonata
    ? ` Luna aleasă, ${ro(lp.salvata)}, e după prima notă din jurnal (${ro(lp.prima_nota)}, scrisă după alegere): luna preluării se socotește ${ro(lp.efectiva)}.` : "";
  return `
    <h2 class="pf-titlu" style="margin-top:26px">Preluarea în iConta.eu</h2>
    <div class="grila-doc">
      <label class="camp">
        <span class="camp-eticheta">Luna preluării</span>
        <span class="camp-ajutor">De la ea se numără restanțele în Control fiscal.${lp.propunere ? ` ${lp.salvata ? "Propunerea iConta.eu" : "Completată cu propunerea"}: ${ro(lp.propunere)} — din soldurile de preluare sau data adăugării firmei, cel mult luna primei note.` : ""}${lp.prima_nota ? ` Nu poate fi după ${ro(lp.prima_nota)} (prima notă).` : ""}${plafonata}</span>
        <input type="month" class="camp-input" id="df-luna_preluare" value="${esc(lp.efectiva || "")}" data-initiala="${esc(lp.efectiva || "")}" data-propunere="${esc(lp.propunere || "")}"${lp.prima_nota ? ` max="${esc(lp.prima_nota)}"` : ""}>
      </label>
      <label class="camp">
        <span class="camp-eticheta">Data înființării</span>
        <span class="camp-ajutor">Din ANAF la adăugarea firmei. În anul înființării (primul exercițiu financiar) coloana „An precedent” a bilanțului rămâne goală.</span>
        <input type="date" class="camp-input" id="df-data_infiintare" value="${esc((d.profil || {}).data_infiintare || "")}">
      </label>
    </div>`;
}

// [06.10.2026, comanda Costin §6.4] „Orice modificare se jurnalizează (cine, când, valoare veche → nouă), inclusiv forma juridică
// și capitalul, iar jurnalul e vizibil cabinetului.”
const ETICHETE_JURNAL = { forma_juridica: "Forma juridică", capital_subscris: "Capital subscris", capital_varsat: "Capital vărsat",
  metoda_stoc: "Metoda de stoc", serie_chitanta: "Seria chitanțelor", platitor_tva: "Plătitor de TVA", tip_decont: "Periodicitatea decontului",
  inregistrat_oss: "Înregistrată în regimul special OSS", inreg_art317: "Înregistrat cf. art.317", activitate_exceptata_amef: "Exceptată de la AMEF", activitate_amef: "Activitatea exceptată",
  cont_venit_implicit: "Cont venit implicit", luna_preluare: "Luna preluării", data_infiintare: "Data înființării",
  // [lotul 10, 428 / 431] regimul TVA la încasare (perioadele și „se aplică azi”), asociații și cotele
  tva_incasare_perioade: "TVA la încasare (perioadele)", tva_la_incasare: "Aplică TVA la încasare azi", asociati: "Asociații și cotele",
  tva_incasare_data_optiune: "TVA la încasare (data notificării)" };   // [lotul 13, 541]
// [lotul 07.10 pct.19] valorile se arată cu eticheta pe care omul a ales-o pe ecran, nu cu cheia tehnică („cantitativ_valoric”):
// aceleași liste pe care le randează formularul (`metode_stoc`, `forme_juridice`, `activitati_amef`, opțiunile periodicității),
// iar „true” / „false” devin „da” / „nu”. O valoare fără etichetă cunoscută se arată așa cum e — nu se ghicește.
function _valoareJurnal(d, camp, x) {
  if (x == null || x === "") return "\u2014";
  const liste = { metoda_stoc: d.metode_stoc, forma_juridica: d.forme_juridice, activitate_amef: d.activitati_amef,
    forma_proprietate: d.forme_proprietate,   // [lotul 10, C69]
    tip_decont: [["lunar", "Lunar"], ["trimestrial", "Trimestrial"], ["L", "Lunar"], ["T", "Trimestrial"]] };
  const gasit = (liste[camp] || []).find(([k]) => String(k) === String(x));
  if (gasit) return esc(gasit[1]);
  if (x === "true" || x === true) return "da";
  if (x === "false" || x === false) return "nu";
  if (camp === "luna_preluare" && /^\d{4}-\d{2}/.test(x)) return `${x.slice(5, 7)}/${x.slice(0, 4)}`;
  return esc(x);
}
function _blocJurnal(d) {
  const j = d.jurnal || [];
  return `
    <h2 class="pf-titlu" style="margin-top:26px">Istoricul modificărilor</h2>
    ${!j.length ? `<div class="stare-goala">Nicio modificare înregistrată încă.</div>` : `<div class="df-jurnal-cadru"><table class="fd-tabel df-jurnal" id="df-jurnal">
      <thead><tr><th>Când</th><th>Cine</th><th>Câmp</th><th>Valoare veche</th><th>Valoare nouă</th></tr></thead>
      <tbody>${j.map((r) => `<tr><td>${dataRo(r.la, "cu_ora")}</td><td>${esc(r.cine || "")}</td><td>${esc(ETICHETE_JURNAL[r.camp] || eticheta(r.camp))}</td>
        <td>${_valoareJurnal(d, r.camp, r.vechi)}</td><td>${_valoareJurnal(d, r.camp, r.nou)}</td></tr>`).join("")}</tbody></table></div>`}`;
}

// [lotul 10, deficiența 428, comanda Costin 10.1] „Firma nu poate fi declarată ca aplicând sistemul [TVA la încasare]: vectorul fiscal are doar
// «Înregistrată în scopuri de TVA: Da/Nu» […]. Construiește regimul pe firmă, cu data de la care se aplică și verificarea în registrul ANAF.”
// Sub „Înregistrată în scopuri de TVA” (vizibil numai la „Da”): Nu / Da, de la …, până la … (ieșirea), verificarea ANAF (citire: propune
// datele, nu scrie), perioadele înregistrate. Regulile și temeiul (CF art.282 alin.(3^1), (5)) sunt pe server: core/regim_tva_incasare.py.
function _blocTvaIncasare(v) {
  const t = (v && v.tva_incasare) || {};
  const c = t.curenta || null;
  const da = !!c || !!t.fara_data;
  const per = t.perioade || [];
  const azi = t.aplica_azi ? "Azi firma aplică sistemul TVA la încasare." : (c ? "Azi firma nu aplică sistemul TVA la încasare." : "");
  const faraData = t.fara_data ? " Firma e marcată ca aplicând sistemul (din ANAF, la adăugare), dar fără dată: scrie data de la care se aplică." : "";
  const sursa = (p) => (p.sursa === "anaf" ? "ANAF" : "manual");
  // [lotul 13, deficiența 541: „Jurnalul perioadelor […] nu arată cine și când a schimbat, iar «Șterge» scoate perioada fără urmă.”] cine
  // și când, din jurnalul Date firmă (`regim_tva_incasare.istoric_perioade`, și pentru perioadele de dinainte); perioadele scoase rămân în
  // tabel, marcate, fără acțiuni
  const cineCand = (x) => (x ? `${esc(x.cine || "—")}, ${dataRo(x.la, "cu_ora")}` : "—");
  const scoase = t.scoase || [];
  return `
    <div class="camp" id="vf-camp-tva_incasare">
      <label class="camp-eticheta" for="vf-tva_incasare">Aplică sistemul TVA la încasare (Cod fiscal art. 282)</label>
      <span class="camp-ajutor">TVA-ul facturilor emise devine exigibil la încasare, nu la facturare (art. 282 alin. (3)). Numai la firmele înregistrate în scopuri de TVA.</span>
      <select class="camp-input" id="vf-tva_incasare" data-butoane=""><option value="nu"${da ? "" : " selected"}>Nu</option><option value="da"${da ? " selected" : ""}>Da</option></select>
      ${azi || faraData ? `<span class="camp-ajutor" id="vf-tva_incasare-azi">${esc(azi + faraData)}</span>` : ""}
      <button type="button" class="buton-secundar" id="vf-tva-incasare-anaf" data-actiune="GET /tenants/{tenant_id}/tva-incasare/verifica-anaf">Verifică în registrul ANAF</button>
      <div id="vf-tva-incasare-anaf-rez"></div>
      ${per.length || scoase.length ? `<table class="fd-tabel" id="vf-tva-incasare-perioade">
        <thead><tr><th>De la</th><th>Până la</th><th>Sursa</th><th>Data notificării</th><th>Verificat la ANAF</th><th>Scrisă de, când</th><th>Acțiune</th></tr></thead>
        <tbody>${per.map((p) => `<tr data-perioada-rand="${esc(p.id)}"><td>${dataRo(p.de_la)}</td><td>${p.pana_la ? dataRo(p.pana_la) : "în continuare"}</td><td>${sursa(p)}</td>
          <td>${p.data_optiune ? dataRo(p.data_optiune) : "\u2014"}</td>
          <td>${p.verificat_anaf_la ? dataRo(p.verificat_anaf_la) : "\u2014"}</td><td>${p.scrisa ? cineCand(p.scrisa) : (p.sursa === "anaf" ? "din ANAF, la adăugarea firmei" : "\u2014")}</td>
          <td><button type="button" class="buton-secundar" data-iesire="${esc(p.pana_la || "")}" data-actiune="GET /tenants/{tenant_id}/tva-incasare/neexigibile"${p.pana_la ? "" : atributeInactiv("Perioada e încă în curs: facturile rămase cu TVA neexigibil se văd după ce perioada are data „până la”.")}>Facturile rămase în sistem</button> <button type="button" class="buton-sters" data-perioada="${esc(p.id)}" data-actiune="DELETE /tenants/{tenant_id}/tva-incasare/{perioada_id}" aria-label="Șterge perioada de la ${esc(dataRo(p.de_la))}">Șterge</button></td></tr>`).join("")}${scoase.map((x) => `<tr class="df-perioada-scoasa" data-perioada-scoasa>
          <td colspan="5"><s>${esc(x.text)}</s></td><td>${cineCand(x)}</td><td>${x.inlocuita_cu ? `înlocuită cu „${esc(x.inlocuita_cu)}”` : "ștearsă"}</td></tr>`).join("")}</tbody></table>` : ""}
      ${(t.avertismente || []).map((a) => `<span class="camp-ajutor">${esc(a)}</span>`).join("")}
      <div id="vf-tva-incasare-iesire"></div>
    </div>
    <label class="camp" id="vf-camp-tva_incasare_data_optiune">
      <span class="camp-eticheta">Data notificării (opțiunii) depuse la ANAF</span>
      <span class="camp-ajutor">Sistemul se aplică de la prima zi a perioadei fiscale următoare celei în care s-a depus notificarea (art. 282 alin. (3^1) lit. a)). Cerută când „Aplică de la” cade în perioada fiscală în curs.</span>
      <input type="date" class="camp-input" id="vf-tva_incasare_data_optiune" value="${esc((c && c.data_optiune) || "")}">
    </label>
    <label class="camp" id="vf-camp-tva_incasare_de_la">
      <span class="camp-eticheta">Aplică de la<span class="oblig">*</span></span>
      <span class="camp-ajutor">Prima zi a perioadei fiscale de după opțiune, sau data înregistrării în scopuri de TVA (art. 282 alin. (3^1)).</span>
      <input type="date" class="camp-input" id="vf-tva_incasare_de_la" value="${esc((c && c.de_la) || "")}">
    </label>
    <label class="camp" id="vf-camp-tva_incasare_pana_la">
      <span class="camp-eticheta">Aplică până la (ieșirea din sistem)</span>
      <span class="camp-ajutor">Ultima zi în care s-a aplicat — sfârșitul unei perioade fiscale (art. 282 alin. (5)). Gol = se aplică în continuare.</span>
      <input type="date" class="camp-input" id="vf-tva_incasare_pana_la" value="${esc((c && c.pana_la) || "")}">
    </label>`;
}

// [lotul 10, deficiența 431, comanda Costin 10.1] „Fluxul e unul singur: asociații și cotele (cu istoricul cesiunilor) în datele firmei;
// nota de dividende împarte automat pe asociați; D205 preia din notele validate”. Până azi asociații intrau numai din importul CSV. Tabelul
// e un formular cu rânduri (DS cap.24: re-randare din model, id-ul `as-<rând>-<câmp>`, rândul adăugabil e și ștergibil); verificarea e pe
// server (aceeași cu importul: CNP / CUI cu cifra de control, cota, dubluri, suma 100%). Se salvează cu „Salvează” de jos, ca restul.
function _randuriAsociati(model) {
  return model.map((r, i) => `<tr>
      <td><input type="text" class="camp-input" id="as-${i + 1}-nume" value="${esc(r.nume || "")}" aria-label="Numele asociatului, rândul ${i + 1}"></td>
      <td><input type="text" class="camp-input" id="as-${i + 1}-cnp" value="${esc(r.cnp || "")}" inputmode="numeric" aria-label="CNP sau CUI, rândul ${i + 1}"></td>
      <td><input type="text" class="camp-input" id="as-${i + 1}-cota" value="${esc(r.cota || "")}" inputmode="decimal" aria-label="Cota în procente, rândul ${i + 1}"></td>
      <td><button type="button" class="buton-sters" data-as-sterge="${i}" data-fara-actiune="rând în formular; „Salvează” poartă acțiunea" aria-label="Scoate rândul ${i + 1}">Scoate</button></td>
    </tr>`).join("");
}
function _procent(x) { return String(x == null ? "" : x).replace(".", ",") + "%"; }
function _blocAsociati(a) {
  if (!a) return `
    <h2 class="pf-titlu" style="margin-top:26px">Asociați</h2>
    <div id="as-msg"></div>`;
  const ist = a.istoric || [];
  const perioada = (s) => (s.de_la ? `${dataRo(s.de_la)} – ${dataRo(s.pana_la)}` : `până la ${dataRo(s.pana_la)}`);
  return `
    <h2 class="pf-titlu" style="margin-top:26px">Asociați</h2>
    <p class="pf-intro">Cine deține părțile sociale și în ce cotă (Legea 31/1990 art. 7 lit. d)). Dividendele se împart după cote (art. 67 alin. (2)), după structura de la data distribuirii.${a.valabila_de_la ? ` Structura de acum e valabilă de la ${dataRo(a.valabila_de_la)}.` : ""}</p>
    <table class="fd-tabel" id="as-tabel">
      <thead><tr><th>Nume</th><th>CNP / CUI</th><th>Cota (%)</th><th>Acțiune</th></tr></thead>
      <tbody id="as-randuri"></tbody>
    </table>
    <p><button type="button" class="buton-secundar" id="as-adauga" data-fara-actiune="rând în formular; „Salvează” poartă acțiunea">+ Asociat</button>
      <span class="camp-ajutor" id="as-total" role="status" aria-label="Totalul cotelor"></span></p>
    <div class="grila-doc">
      <label class="camp">
        <span class="camp-eticheta">Data cesiunii (numai la o cesiune de părți sociale)</span>
        <span class="camp-ajutor">Gol = corectezi structura de acum, scrisă greșit. Cu o dată = de la ea e valabilă structura de mai sus (Legea 31/1990 art. 202), iar cea de până atunci rămâne în istoric: dividendele de dinainte se cuvin vechilor asociați (art. 67 alin. (6)).</span>
        <input type="date" class="camp-input" id="as-data-cesiune" value="">
      </label>
    </div>
    <h3 class="pf-titlu">Istoricul cesiunilor</h3>
    ${ist.length ? `<table class="fd-tabel" id="as-istoric">
      <thead><tr><th>Perioada</th><th>Asociații și cotele</th></tr></thead>
      <tbody>${ist.map((s) => `<tr><td>${perioada(s)}</td><td>${s.asociati.map((x) => `${esc(x.nume)} — ${esc(_procent(x.cota))}`).join("; ")}</td></tr>`).join("")}</tbody></table>`
      : `<div class="stare-goala stare-goala--inline" id="as-istoric-gol">Nicio cesiune înregistrată: structura de mai sus e cea de la început. O cesiune se înregistrează cu data ei, mai sus.</div>`}`;
}

// [lotul 13, deficiența C71.1, comanda 13.1: „La F4 PFA […] formularul marchează cu * câmpuri de SRL «cerute la bilanț» (Nr. registrul
// comerțului, Mare contribuabil, Forma de proprietate, Entitate de interes public)”] `ob` e mulțimea maximă (= `OBLIGATORII`, gard
// `core/test_g9_oblig_backend.py`); câte din ele cere FIRMA asta spune serverul, după forma ei (`firma_profil_api.campuri_forma`: aceeași
// sursă cu „Profil incomplet”). Câmpurile numai-bilanț nu apar la o formă care nu întocmește bilanț (`fara_rost`); „Cerut la bilanț.”
// (`ajOb`) numai unde chiar e cerut.
function camp(c, val, d) {
  if (((d && d.fara_rost) || []).includes(c.k)) return "";
  const cerut = c.ob && (!(d && d.obligatorii) || d.obligatorii.includes(c.k));
  const ob = cerut ? '<span class="oblig">*</span>' : "";
  const textAj = [c.aj, cerut ? c.ajOb : null].filter(Boolean).join(" ");
  const aj = textAj ? `<span class="camp-ajutor">${esc(textAj)}</span>` : "";
  // [lotul 11, decizia 10.3] CUI-ul arătat cu „RO” numai la plătitorul de TVA (`cui_afisat`, regula din `core/cui_forma.afisare`)
  if (c.k === "cui" && val) return campCui(c, (d && d.profil && d.profil.cui_afisat) || val, ob);
  // [lotul 10, C69] Da / Nu (valoarea salvată, altfel „— alege —”) și lista din nomenclator (codul se trimite, denumirea se arată)
  if (c.tip === "danu") return `
    <label class="camp">
      <span class="camp-eticheta">${esc(c.e)}${ob}</span>
      ${aj}
      <select class="camp-input" id="df-${c.k}" data-butoane="">${alegeDacaLipseste(val)}
        <option value="0"${val === false ? " selected" : ""}>Nu</option>
        <option value="1"${val === true ? " selected" : ""}>Da</option>
      </select>
    </label>`;
  if (c.tip === "lista") return `
    <label class="camp">
      <span class="camp-eticheta">${esc(c.e)}${ob}</span>
      ${aj}
      <select class="camp-input" id="df-${c.k}">${alegeDacaLipseste(val)}${((d || {})[c.lista] || []).map(([k, t]) =>
        `<option value="${esc(k)}"${String(k) === String(val) ? " selected" : ""}>${esc(t)}</option>`).join("")}</select>
    </label>`;
  return `
    <label class="camp">
      <span class="camp-eticheta">${esc(c.e)}${ob}</span>
      ${aj}
      <input type="text" class="camp-input" id="df-${c.k}" value="${esc(val || "")}">
    </label>`;
}

// [deficiența 272, comanda Costin 16.10.2026] „CUI-ul nu se modifică din acest ecran, de niciun rol; o corectură reală de CUI e o
// operațiune separată, a administratorului, cu avertisment.” Câmpul se citește; corectura are butonul ei (ascuns cui n-are dreptul).
function campCui(c, val, ob) {
  return `
    <div class="camp">
      <label class="camp-eticheta" for="df-cui">${esc(c.e)}${ob}</label>
      <span class="camp-ajutor">Nu se modifică din Date firmă. Dacă e greșit, îl corectează administratorul cabinetului.</span>
      <input type="text" class="camp-input" id="df-cui" value="${esc(val)}" readonly aria-readonly="true">
      <button type="button" class="buton-secundar" id="df-cui-corecteaza" data-actiune="POST /tenants/{tenant_id}/cui/corectura">Corectează CUI-ul</button>
      <div id="df-cui-corectura"></div>
    </div>`;
}

// [vector_date_firma_v1] Vectorul fiscal: cele 4 atribute din firma_profil pe care le
// citeste/scrie core/vector_fiscal_api (citeste/salveaza). Pana acum se completa
// DOAR la migrarea cabinetului (migrare.js) - o firma adaugata direct sau creata la
// inregistrare ramanea pe valorile implicite din template (micro, neplatitor TVA,
// fara intracom), adica pe presupuneri. Termenele si controlul fiscal mergeau pe ele.
// Sta aici, nu intr-un ecran separat: datele fiscale ale firmei sunt un tot (DS:
// aceeasi situatie = aceeasi rezolvare).
const VECTOR = [
  // [alege] selecturi obligatorii FARA optiune-goala pre-existenta: la valoare NULL browserul afiseaza
  // prima optiune ca aleasa (default fabricat, Regula 4). `alege:true` -> campVector pune un placeholder
  // "\u2014 alege \u2014" cand valoarea lipseste, iar salvarea cere alegere explicita (nu trimite fabricat).
  { k: "regim_fiscal", e: "Regim fiscal", ob: true, alege: true, tip: "select",
    opt: [["micro", "Microîntreprindere (impozit pe venit)"], ["profit", "Impozit pe profit"]],
    aj: "Decide D100 (micro, trimestrial) sau D101 (profit, anual)." },
  { k: "platitor_tva", e: "\u00cenregistrat\u0103 \u00een scopuri de TVA", ob: true, alege: true, tip: "select",
    opt: [["nu", "Nu"], ["da", "Da"]],
    aj: "Din vectorul fiscal ANAF. Decide D300 și D394." },
  // [cerinta Costin, 06.09.2026] Acelasi text de ajutor ca in `migrare.js`, VERBATIM de acolo —
  // aceeasi alegere pusa in doua ecrane nu are voie sa aiba criteriul intr-unul singur. Nu se
  // rescrie si nu se rezuma: un temei citat din memorie intra in corpus ca fapt.
  // `core/test_ajutor_periodicitate_tva.py` compara cele doua texte RANDATE si pica daca diverg.
  { k: "tip_decont", e: "Periodicitate TVA", tip: "select",
    opt: [["", "\u2014"], ["lunar", "Lunar"], ["trimestrial", "Trimestrial"]],
    aj: "Lunar (regula, art. 322 alin. 1 Cod fiscal). Trimestrial doar dacă în anul precedent cifra de afaceri a fost sub 100.000 euro (curs BNR 31.12) și nu ați efectuat achiziții intracomunitare de bunuri — art. 322 alin. 2. Obligatorie doar la plătitorii de TVA. Decide dacă D300/D394 se depun lunar sau trimestrial." },
  { k: "operatiuni_ic", e: "Opera\u021biuni intracomunitare", alege: true, tip: "select",
    opt: [["nu", "Nu"], ["da", "Da"]],
    aj: "Achizi\u021bii/livr\u0103ri din UE. Decide D390 (VIES)." },
  // [lotul 07.10 B, comanda Costin A.3] `neales`: „— alege —” când nu e ales (NULL), FĂRĂ a fi obligatoriu la salvare — se cere o
  // singură dată la prima folosire (D301 pers_inreg); salvarea vectorului îl păstrează nul, nu „Nu”
  { k: "inreg_art317", e: "\u00cenregistrat\u0103 art. 317 (opera\u021biuni intracomunitare)", tip: "select", neales: true,
    opt: [["nu", "Nu"], ["da", "Da"]],
    aj: "\u00cenregistrare special\u0103 \u00een scopuri de TVA (art. 317 CF) pentru achizi\u021bii/livr\u0103ri intracomunitare la nepl\u0103titori. Decide D390 (VIES) \u0219i tipul persoanei \u00eenregistrate din D301." },
  // [tva_inceput] data inregistrarii in scopuri de TVA - EDITABILA, ceruta contabilului cand ANAF n-o are.
  // Vizibila DOAR la platitor (doarPlatitor). Fara ea, motorul da gri "necunoscut" pe D300/D394/D406 (regula 4).
  { k: "tva_data_inceput", e: "Data \u00eenregistr\u0103rii \u00een scopuri de TVA", tip: "data", doarPlatitor: true,
    aj: "Data de la care firma e \u00eenregistrat\u0103 \u00een scopuri de TVA (de pe certificatul ANAF). Necesar\u0103 ca s\u0103 \u0219tim de c\u00e2nd se datoreaz\u0103 D300/D394/D406 \u2014 f\u0103r\u0103 ea, verdictele pe lunile trecute r\u0103m\u00e2n \u00abnecunoscut\u00bb." },
];

function campVector(c, val, v) {
  // [lotul 13, C71.1] „oferă Regim fiscal micro/profit (D100/D101), care nu privesc un PFA”: la partida simplă (`v.partida_simpla`, fapt
  // unic al serverului — `vector_fiscal_api.citeste`, care refuză oricum un regim acolo) nu se oferă alegerea; se spune de ce. Câmpul
  // ascuns ține forma cererii (`regim_fiscal` gol = NULL, cum îl salvează serverul la partida simplă).
  if (c.k === "regim_fiscal" && v && v.partida_simpla) return `
    <div class="camp" id="vf-camp-regim_fiscal">
      <span class="camp-eticheta">${esc(c.e)}</span>
      <span class="camp-ajutor">Nu se aplică: microîntreprinderea și impozitul pe profit (D100 / D101) privesc persoanele juridice. O firmă în partidă simplă (PFA, II, IF) declară venitul în Declarația unică (D212).</span>
      <input type="hidden" id="vf-regim_fiscal" value="">
    </div>`;
  const ob = (c.ob || c.alege) ? '<span class="oblig">*</span>' : "";
  const aj = c.aj ? `<span class="camp-ajutor">${esc(c.aj)}</span>` : "";
  let control;
  if (c.tip === "data") {
    // [tva_inceput] input calendaristic (ISO 'YYYY-MM-DD'); valoarea vine pre-populata din /vector.
    control = `<input type="date" class="camp-input" id="vf-${c.k}" aria-label="${esc(c.e)}" value="${esc(val || "")}">`;
  } else {
    const v = val === true ? "da" : val === false ? "nu" : (val || "");
    // [alege] valoare lipsa pe select obligatoriu -> placeholder "— alege —" AFISAT (selected), dar
    // neselectabil (disabled hidden): fara el, browserul afiseaza prima optiune reala ca aleasa (Regula 4).
    const ph = ((c.alege || c.neales) && !v)
      ? `<option value="" selected disabled hidden>— alege —</option>` : "";
    const opts = c.opt.map(([k, t]) =>
      `<option value="${esc(k)}"${String(k) === String(v) ? " selected" : ""}>${esc(t)}</option>`).join("");
    control = `<select class="camp-input" id="vf-${c.k}" aria-label="${esc(c.e)}">${ph}${opts}</select>`;
  }
  return `
    <label class="camp" id="vf-camp-${c.k}">
      <span class="camp-eticheta">${esc(c.e)}${ob}</span>
      ${aj}
      ${control}
    </label>`;
}

// [R77 + R81, 27.08.2026] Denumirea firmei, scrisă o dată și explicată o dată.
//
// Costin: *„un cabinet trebuie să poată corecta o denumire — o firmă se redenumește la registru,
// iar aplicația nu poate refuza să urmeze."* Deci câmpul există. Iar poarta construită în aceeași
// zi devine vie: cine tastează altceva decât spune ANAF face o **alegere**, consemnată cu autor
// și dată — nu o editare tăcută.
//
// De ce sunt două câmpuri și nu unul: firma are două denumiri, în două locuri. Cea din
// PORTOFOLIU (`tenants.nume`) e cea din listă și din bara de sus. Cea FISCALĂ
// (`firma_profil.nume`) pleacă în declarații și pe bilanț. Măsurat 27.08: pe **4 din 17** firme
// ele diferă deja. Tiparul e cel din R63 — două lucruri diferite, două nume, iar când coincid se
// spune. A treia, `nume_anaf`, nu se editează: e ce zice registrul.
function _blocDenumire(t, profil) {
  const nume = (t && t.nume) || "";
  const anaf = (t && t.nume_anaf) || "";
  const fiscal = (profil && profil.nume) || "";
  const nrm = (s) => String(s || "").trim().replace(/\s+/g, " ").toLowerCase();

  const randAnaf = anaf
    ? `<p class="camp-ajutor">La ANAF: <strong>${esc(anaf)}</strong>${
        t.nume_anaf_la ? ` (citit\u0103 la ${esc(dataRo(String(t.nume_anaf_la).slice(0, 10)))})` : ""}.
       Dac\u0103 scrii altceva, alegerea se consemneaz\u0103 \u2014 cu cine a f\u0103cut-o \u0219i c\u00e2nd.</p>`
    : `<p class="camp-ajutor">Denumirea de la ANAF nu e \u00eenc\u0103 adus\u0103 pentru firma asta, deci nu avem cu ce o compara. Scrie denumirea din actele firmei.</p>`;

  const divergenta = (fiscal && nrm(fiscal) !== nrm(nume))
    ? `<div class="dec-avert" data-e1="denumire-firma">
         <div class="dec-avert-cap">Cele dou\u0103 denumiri difer\u0103</div>
         <ul><li>\u00een portofoliu: <b data-e1-sursa="portofoliu">${esc(nume)}</b> \u2014 ce vezi \u00een list\u0103 \u0219i \u00een bara de sus</li>
             <li>\u00een declara\u021bii: <b data-e1-sursa="fiscal">${esc(fiscal)}</b> \u2014 <b data-e1-efect="fiscal">asta pleac\u0103 pe h\u00e2rtie</b></li></ul>
       </div>`
    : "";

  return `
    <h2 class="pf-titlu">Denumirea firmei</h2>
    ${divergenta}
    <div class="grila-doc">
      <label class="camp">
        <span class="camp-eticheta">Denumirea firmei<span class="oblig">*</span></span>
        <p class="camp-ajutor">Una singur\u0103, \u0219i se scrie \u00eentr-un singur loc: aceea\u0219i \u00een list\u0103, \u00een bara de sus \u0219i pe declara\u021bii (D100, D101, D205, D301, D390, D394, D406, bilan\u021b).</p>
        ${randAnaf}
        <input type="text" class="camp-input" id="df-nume-portofoliu" data-actiune-camp="PUT /tenants/{tenant_id}" value="${esc(nume)}">
      </label>
    </div>`;
}

// [lotul 12, deficiența 627 — comanda Costin 12.2 pct.14: „după o salvare parțială, «Profil incomplet» nu se actualizează”] lista
// câmpurilor obligatorii lipsă (sau a blocajelor declarațiilor), din `GET …/firma-profil/date`; stă în `#df-profil-stare`, ca salvarea
// parțială s-o poată reface din bază fără să redeseneze formularul (ce n-a intrat rămâne scris pe ecran, lângă refuzul lui).
function _blocProfil(d) {
  const lipsa = d.lipsuri || [];
  const blocaje = d.blocaje || [];
  return lipsa.length
    ? `<div class="dec-avert">
         <div class="dec-avert-cap">Profil incomplet \u2014 ${cate(lipsa.length, "c\u00e2mp obligatoriu", "c\u00e2mpuri obligatorii")} ${lipsa.length === 1 ? "lipse\u0219te" : "lipsesc"}</div>
         <ul>${lipsa.map((l) => `<li><b>${esc(eticheta(l.camp))}</b> \u2014 blocheaz\u0103 ${esc(l.declaratii.join(", "))}</li>`).join("")}</ul>
       </div>`
    : blocaje.length
    ? `<div class="dec-avert">
         <div class="dec-avert-cap">C\u00e2mpurile obligatorii sunt completate, dar unele declara\u021bii nu se pot genera \u00eenc\u0103</div>
         <ul>${blocaje.map((b) => `<li><b>${esc(b.declaratie)}</b> \u2014 ${esc(b.motiv)}</li>`).join("")}</ul>
       </div>`
    : `<div class="dec-ok">Profil complet. C\u00e2mpurile obligatorii sunt completate.</div>`;
}

export async function randeazaDateFirma(corp, nav, tenantId, opt = {}) {
  if (nav && nav.setInapoi) nav.setInapoi(opt.inapoi || null);
  // [lotul 13, 525] redesenarea de după o acțiune (`peLoc`, ca DS cap.9 v2.102) nu trece prin „Se încarcă…”: conținutul nu scade la un
  // rând, deci derularea nu cade la începutul ferestrei
  if (!opt.peLoc) corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;

  let d = { profil: {}, lipsuri: [] };
  let v = {};
  let t = {};   // [R77] rândul din `public.tenants`: denumirea din portofoliu + ce spune ANAF
  let a = null;   // [lotul 10, 431] asociații și cotele; null = necitite (secțiunea spune de ce)
  let aEroare = null;
  try {
    [d, v, t, a] = await Promise.all([
      api.get(`/tenants/${tenantId}/firma-profil/date`),
      api.get(`/tenants/${tenantId}/vector`).catch(() => ({})),
      api.get(`/tenants/${tenantId}`).catch(() => ({})),
      api.get(`/tenants/${tenantId}/asociati`).catch((e) => { aEroare = (e && e.mesaj) || "Asociații nu s-au putut citi."; return null; }),
    ]);
  } catch (e) {
    corp.innerHTML = `<div id="df-msg"></div>`;
    arataMesaj(corp.querySelector("#df-msg"), (e && e.mesaj) || "Nu s-au putut citi datele firmei.", "eroare");
    return;
  }

  corp.innerHTML = `
    <h2 class="pf-titlu">Date firm\u0103</h2>
    <p class="pf-intro">Datele pe care ANAF le cere în declarații. Câmpurile cu <span class="oblig">*</span> sunt obligatorii pentru declarații — ce lipsește nu oprește salvarea, ci declarațiile care îl cer (lista de mai jos).</p>
    <div id="df-profil-stare">${_blocProfil(d)}</div>
    ${_blocDenumire(t, d.profil)}
    <div class="grila-doc">${CAMPURI.map((c) => camp(c, d.profil[c.k], d)).join("")}</div>

    <h2 class="pf-titlu" style="margin-top:26px">Vector fiscal</h2>
    <p class="pf-intro">Ce declara\u021bii datoreaz\u0103 firma. Termenele \u0219i controlul fiscal pornesc de aici.</p>
    <div class="grila-doc">${VECTOR.map((c) => campVector(c, v[c.k], v) + (c.k === "platitor_tva" ? _blocTvaIncasare(v) : "")).join("")}</div>

    <h2 class="pf-titlu" style="margin-top:26px">Cont contabil</h2>
    <p class="pf-intro">Contul de venit folosit implicit la emiterea facturilor. Se poate schimba pe fiecare factur\u0103.</p>
    <div class="grila-doc">
      <label class="camp">
        <span class="camp-eticheta">Cont venit implicit</span>
        <span class="camp-ajutor">Clasa 70 (cifra de afaceri): 707 m\u0103rfuri, 704 servicii, 701 produse.</span>
        <select class="camp-input" id="df-cont_venit">${Object.entries(d.conturi_venit || {}).map(([k, t]) =>
          `<option value="${esc(k)}"${String(k) === String(d.profil.cont_venit_implicit) ? " selected" : ""}>${esc(k)} \u2014 ${esc(t)}</option>`).join("")}</select>
      </label>
    </div>
    ${d.profil.tip_firma === "pfa" ? "" : _blocCapital(d)}
    ${d.profil.tip_firma === "pfa" ? "" : _blocAsociati(a)}
    ${_blocAmef(d)}
    ${_blocChitante(d)}
    ${_blocStoc(d)}
    ${_blocPreluare(d)}
    <div class="bara-fixa"><div id="df-msg"></div>
    <div class="dec-bara">
      <button class="buton-primar" id="df-salveaza" data-actiune="POST /tenants/{tenant_id}/firma-profil/date|POST /tenants/{tenant_id}/vector|POST /tenants/{tenant_id}/tva-incasare|POST /tenants/{tenant_id}/asociati|POST /tenants/{tenant_id}/asociati/cesiune|PUT /tenants/{tenant_id}">Salvează</button>
    </div></div>
    ${_blocJurnal(d)}
  `;
  if (aEroare && corp.querySelector("#as-msg")) arataMesaj(corp.querySelector("#as-msg"), aEroare, "eroare");

  const _btnCui = corp.querySelector("#df-cui-corecteaza");
  if (_btnCui) _btnCui.addEventListener("click", () => _corecturaCui(corp, nav, tenantId, opt));
  // [D394 Î2] activitatea apare DOAR cu bifa „Da”
  const _amefSel = corp.querySelector("#df-activitate_exceptata_amef");
  if (_amefSel) _amefSel.addEventListener("change", () => {
    corp.querySelector("#df-activitate_amef-camp").style.display = _amefSel.value === "1" ? "" : "none";
  });
  // [tva_inceput] campul "Data inregistrarii TVA" apare DOAR la platitor; comuta live la schimbarea selectului.
  // [lotul 10, 428] la fel regimul TVA la încasare; datele lui, numai cu „Da”
  const _tvaSel = corp.querySelector("#vf-platitor_tva");
  const _tvaiSel = corp.querySelector("#vf-tva_incasare");
  const _tvaToggle = () => {
    const plat = !!(_tvaSel && _tvaSel.value === "da");
    const aratat = (id, da) => { const el = corp.querySelector(id); if (el) el.style.display = da ? "" : "none"; };
    aratat("#vf-camp-tva_data_inceput", plat);
    aratat("#vf-camp-tva_incasare", plat);
    aratat("#vf-camp-tva_incasare_de_la", plat && _tvaiSel && _tvaiSel.value === "da");
    aratat("#vf-camp-tva_incasare_data_optiune", plat && _tvaiSel && _tvaiSel.value === "da");   // [lotul 13, 541]
    aratat("#vf-camp-tva_incasare_pana_la", plat && _tvaiSel && _tvaiSel.value === "da");
  };
  if (_tvaSel) _tvaSel.addEventListener("change", _tvaToggle);
  if (_tvaiSel) _tvaiSel.addEventListener("change", _tvaToggle);
  _tvaToggle();
  _legaTvaIncasare(corp, nav, tenantId, opt);
  const asoc = _legaAsociati(corp, a);
  // [lotul 12, 169] „Luna preluării” golită revine, la ieșirea din câmp, la propunere — nu rămâne „---------- ----” (luna goală în Chromium)
  const _lpIn = corp.querySelector("#df-luna_preluare");
  _lpIn.addEventListener("blur", () => { if (!_lpIn.value && _lpIn.dataset.propunere) _lpIn.value = _lpIn.dataset.propunere; });
  _pozitioneaza(corp, opt);

  // [BLOC R, 28.08.2026] Legarea celor două casete de denumire a fost scoasă odată cu a doua
  // casetă. Era reparația corectă cât timp duplicatul exista; nu mai are ce lega.

  // [lotul 10, deficiența 427, comanda Costin 10.1] „completarea vectorului fiscal nu se poate salva cât timp lipsesc Nr. registrul
  // comerțului, CAEN și adresa. Ce s-a completat se salvează; lipsurile rămân în «Profil incomplet» și blochează doar declarațiile
  // afectate, cum spune deja ecranul.” Un câmp obligatoriu gol NU mai oprește salvarea (nici aici, nici pe server): după salvare,
  // mesajul spune ce lipsește și ce declarații blochează. Părțile formularului se salvează FIECARE pe drumul ei — un refuz al uneia
  // (o valoare invalidă) nu le mai pierde pe celelalte; refuzul stă lângă câmpul lui (DS cap.6, G10) și în „NU s-a salvat” (410).
  // Refuzul fiecărei cereri se pune pe loc, în `catch`-ul ei (atunci leagă `api.js` refuzul de buton, 410); `pre` = prefixul id-urilor
  // DOM ale părții (`df-` profilul, `vf-` vectorul și regimul TVA la încasare; asociații trimit id-ul întreg).
  corp.querySelector("#df-salveaza").addEventListener("click", async () => {
    const btn = corp.querySelector("#df-salveaza");
    const msg = corp.querySelector("#df-msg");
    const date = _dateDinFormular(corp);
    curataEroriCamp(corp);
    // [R77] denumirea din portofoliu: alt tabel, deci alt apel — dar o singură apăsare pentru om.
    const numePortofoliu = (corp.querySelector("#df-nume-portofoliu").value || "").trim();
    const refuzuriClient = numePortofoliu ? [] : [["df-nume-portofoliu", "Completează denumirea din portofoliu."]];
    const { vf, vecOblig } = _vectorDinFormular(corp, v);
    refuzuriClient.push(...vecOblig);
    // [428] regimul TVA la încasare: se trimite numai dacă s-a schimbat (fiecare salvare a lui întreabă și registrul ANAF)
    const tvai = _tvaiDinFormular(corp, v, vf.platitor_tva);
    if (tvai && tvai.aplica && !tvai.de_la) refuzuriClient.push(["vf-tva_incasare_de_la", "Scrie data de la care firma aplică sistemul TVA la încasare."]);
    // [431] asociații: se trimit numai dacă tabelul s-a schimbat; cu data cesiunii = cesiune, fără ea = corectură
    const as = asoc ? asoc.dinFormular() : null;
    if (as && as.dataCesiune && !as.schimbat) refuzuriClient.push(["as-data-cesiune", "Scrie în tabel noua structură a asociaților: cesiunea o înregistrează de la data ei."]);
    refuzuriClient.forEach(([id, m]) => eroareCamp(corp, id, m));
    const refuzat = new Set(refuzuriClient.map(([id]) => id));
    btn.disabled = true;
    btn.textContent = "Se salveaz\u0103\u2026";
    const salvate = [];
    const faraCamp = [];
    // [lotul 11, 440] fiecare eroare a părții refuzate lângă câmpul ei (`arataRefuzul`, numele din server -> id-ul de pe ecran); ce n-are
    // câmp pe ecran intră cu textul lui în mesajul de sub buton — și atunci când alte erori ale aceleiași părți și-au găsit câmpul
    const pune = (pre) => (e) => {
      const ec = (e && e.erori_campuri) || [];
      const campuri = Object.fromEntries(ec.map((c) => [c.camp, c.camp === "cont_venit_implicit" ? "df-cont_venit" : pre + c.camp]));
      const puse = arataRefuzul(corp, e, null, { campuri });
      if (puse < ec.length || !ec.length) {
        const m = (e && e.mesaj) || "Nu s-a putut salva.";
        const rest = ec.filter((c) => c.mesaj && !corp.querySelector("#" + CSS.escape(campuri[c.camp])) && m.indexOf(c.mesaj) < 0).map((c) => c.mesaj);
        faraCamp.push([m].concat(rest).join(" "));
      }
      return null;
    };
    const parte = (nume, p, pre) => p.then((r) => { salvate.push(nume); return r || {}; }, pune(pre));
    const asteptate = ["datele firmei"];   // părțile trimise; „toate bune” = toate au intrat
    const pProfil = parte("datele firmei", api.post(`/tenants/${tenantId}/firma-profil/date`, date), "df-");
    let pVector = Promise.resolve(null);
    if (!vecOblig.length) {
      asteptate.push("vectorul fiscal");
      pVector = parte("vectorul fiscal", api.post(`/tenants/${tenantId}/vector`, vf), "vf-");
    }
    // regimul TVA la încasare cere firma înregistrată în scopuri de TVA: dacă „Da” vine chiar acum, după vector; altfel odată cu restul
    let pTvai = Promise.resolve(null);
    if (tvai && !refuzat.has("vf-tva_incasare_de_la")) {
      asteptate.push("regimul TVA la încasare");
      const trimite = () => parte("regimul TVA la încasare", api.post(`/tenants/${tenantId}/tva-incasare`, tvai), "vf-");
      pTvai = v.platitor_tva === true ? trimite() : pVector.then((r) => (r ? trimite()
        : (eroareCamp(corp, "vf-tva_incasare", "Nu s-a salvat: întâi vectorul fiscal (înregistrată în scopuri de TVA)."), null)));
    }
    let pAsoc = Promise.resolve(null);
    if (as && as.schimbat && !refuzat.has("as-data-cesiune")) {
      asteptate.push("asociații");
      pAsoc = parte("asociații", as.dataCesiune
        ? api.post(`/tenants/${tenantId}/asociati/cesiune`, { data_cesiune: as.dataCesiune, randuri: as.randuri })
        : api.post(`/tenants/${tenantId}/asociati`, { randuri: as.randuri }), "");
    }
    const [rProfil, , rTvai] = await Promise.all([pProfil, pVector, pTvai, pAsoc]);
    if (refuzuriClient.length || faraCamp.length || salvate.length !== asteptate.length) {
      btn.disabled = false;
      btn.textContent = "Salveaz\u0103";
      const linii = salvate.length ? ["S-au salvat: " + salvate.join(", ") + ". Restul NU — " + (faraCamp.length ? "motivele:" : "vezi câmpurile marcate.")] : [];
      linii.push(...faraCamp);
      // [627] ce a intrat schimbă lista „Profil incomplet”: se recitește din bază (numai blocul ei; formularul rămâne cum l-a scris omul);
      // dacă recitirea cade, lista veche nu rămâne (ar spune lipsă un câmp tocmai salvat): în locul ei, de ce nu e la zi
      if (salvate.length) {
        const zp = corp.querySelector("#df-profil-stare");
        try { zp.innerHTML = _blocProfil(await api.get(`/tenants/${tenantId}/firma-profil/date`)); }
        catch (e) { arataMesaj(zp, "Lista câmpurilor obligatorii lipsă nu s-a putut reciti după salvare: " + ((e && e.mesaj) || "redeschide Date firmă."), "avert"); }
      }
      if (faraCamp.length || salvate.length) arataMesaj(msg, linii.join("\n"), "eroare");   // [410] nu tot s-a salvat = refuz, nu avertisment
      return;
    }
    let redenumit = false;
    try {
      // [LOTUL 11, 04.09.2026] Denumirea (identitatea firmei) se scrie LA URMĂ și numai după ce restul a intrat: un act care se refuză nu
      // lasă în urmă o firmă redenumită. Se trimite DOAR dacă s-a schimbat (un `PUT` la fiecare salvare ar consemna o „alegere" pe care
      // nimeni n-a făcut-o). Confirmarea vizibilă stă în același bloc cu actul (DS cap.27).
      if (numePortofoliu !== ((t && t.nume) || "")) await api.put(`/tenants/${tenantId}`, { nume: numePortofoliu });
      redenumit = true;
      await _redeseneazaPeLoc(corp, nav, tenantId, opt);   // [retest 08.10] după salvare nu se mai sare la câmp; [525] rămâi unde lucrai
      // [427] „Salvat. Lipsesc X, Y — blochează D…” (din lipsurile întoarse de salvare); [428] avertismentele regimului + verificarea ANAF
      arataMesaj(corp.querySelector("#df-msg"), _mesajSalvat(rProfil, rTvai), ((rProfil && rProfil.lipsuri) || []).length
        || (rTvai && ((rTvai.avertismente || []).length || (rTvai.anaf && rTvai.anaf.fel !== "fapt"))) ? "avert" : "ok");
      // [lotul 07.10 pct.2] deschis dintr-un refuz al altui formular (factura): drumul înapoi, la formularul păstrat
      if (opt.inapoiLa && nav && nav.inapoi) {
        const bi = document.createElement("button");
        bi.type = "button"; bi.className = "buton-primar"; bi.id = "df-inapoi-la"; bi.style.marginLeft = "10px";
        bi.textContent = "\u2190 \u00cenapoi la " + opt.inapoiLa;
        bi.addEventListener("click", () => nav.inapoi());
        corp.querySelector("#df-msg").appendChild(bi);
      }
    } catch (e) {
      if (redenumit) {   // actele au intrat; a căzut numai redesenarea ecranului
        arataMesaj(msg, "Datele s-au salvat, dar ecranul nu s-a putut reîncărca: " + ((e && e.mesaj) || "redeschide Date firmă."), "eroare");
        return;
      }
      // [LOTUL 11] Mesajul spune CE a apucat să intre: restul datelor e înregistrat și a căzut DOAR redenumirea.
      await _redeseneazaPeLoc(corp, nav, tenantId, opt);
      arataMesaj(corp.querySelector("#df-msg"), "Restul datelor s-au salvat, dar denumirea nu: " + ((e && e.mesaj) || "a fost refuzată")
        + " Ecranul de mai jos arată ce e înregistrat acum.", "eroare");
    }
  });
}

// [lotul 13, deficiența 525, comanda 13.1: „«Deschide Date firmă» de la refuzul dividendelor deschide fereastra de la început, nu la
// secțiunea Asociați; după Salvează fereastra sare la început. Trimiterea duce la locul de completat, iar după salvare rămâi unde lucrai.”]
// Poziția ferestrei se pune DUPĂ ce s-a desenat tot ce îi schimbă înălțimea (tabelul asociaților, secțiunile vectorului ascunse / arătate):
// pusă înainte (cum era), „+ Asociat” se muta după aducerea în vedere (măsurat în `core/test_lot13_portal_p3_ecrane.py`: derularea
// 3305 px, butonul tot în afara ferestrei), iar omul vedea capul ferestrei.
//   - `opt.camp`: câmpul cerut de refuzul care a trimis aici (`detail.camp_ecran`), adus la mijloc, cu focus (retest 08.10 pct.2);
//   - `opt.sus`: derularea de dinaintea unei redesenări pe loc (`_redeseneazaPeLoc`) — omul rămâne unde lucra.
function _pozitioneaza(corp, opt) {
  const cadru = corp.closest(".fereastra-corp") || corp;
  const _tinta = opt.camp ? corp.querySelector("#" + CSS.escape(opt.camp)) : null;
  if (_tinta) { _tinta.scrollIntoView({ block: "center" }); focusFaraSalt(_tinta); } else if (opt.sus != null) cadru.scrollTop = opt.sus;
}

// [525] Redesenarea de după o acțiune (Salvează, ștergerea unei perioade, corectura CUI-ului): pe loc, fără „Se încarcă…” și fără să mai
// sară la câmpul refuzului de la deschidere — derularea rămâne cea din clipa acțiunii.
function _redeseneazaPeLoc(corp, nav, tenantId, opt) {
  const cadru = corp.closest(".fereastra-corp") || corp;
  return randeazaDateFirma(corp, nav, tenantId, { ...opt, camp: null, peLoc: true, sus: cadru.scrollTop });
}

// [427 / 428] Mesajul de după salvare: lipsurile profilului cu declarațiile pe care le blochează, avertismentele regimului TVA la încasare
// și verificarea ANAF, când nu confirmă.
function _mesajSalvat(rProfil, rTvai) {
  const lip = (rProfil && rProfil.lipsuri) || [];
  const linii = [lip.length ? `Salvat. ${lip.length === 1 ? "Lipsește" : "Lipsesc"} ${lip.map((l) => eticheta(l.camp)).join(", ")} — blochează ${[...new Set(lip.flatMap((l) => l.declaratii))].join(", ")}.` : "Datele firmei au fost salvate."];
  if (rTvai) {
    linii.push(...(rTvai.avertismente || []));
    if (rTvai.anaf && rTvai.anaf.fel !== "fapt") linii.push(rTvai.anaf.mesaj);   // afirmația tipată: „fapt” = confirmare
  }
  return linii.join("\n");
}

// Vectorul fiscal citit din formular + alegerile lui obligatorii (validare preventivă, DS cap.6). Scoasă din handlerul „Salvează”, ca
// `_dateDinFormular`: sonda drepturilor leagă un apel de butonul lui pe o fereastră de 80 de linii.
function _vectorDinFormular(corp, v) {
  // [alege] tri-stare: "" (placeholder neales) -> null, NU false tacit. Backendul refuza null cu mesaj
  // clar (regim REGIM_INVALID pt SRL, TVA_LIPSA, IC_LIPSA); dar validam preventiv aici (DS cap.6).
  const _tvaV = corp.querySelector("#vf-platitor_tva").value;
  const triBool = (x) => (x === "da" ? true : x === "nu" ? false : null);
  const vf = {
    regim_fiscal: corp.querySelector("#vf-regim_fiscal").value || null,
    platitor_tva: triBool(_tvaV),
    tip_decont: corp.querySelector("#vf-tip_decont").value || null,
    operatiuni_ic: triBool(corp.querySelector("#vf-operatiuni_ic").value),
    inreg_art317: triBool(corp.querySelector("#vf-inreg_art317").value),   // [lotul 07.10 B] neales -> null
    // [tva_inceput] are sens doar la platitor; la neplatitor trimitem null (backendul o goleste oricum)
    tva_data_inceput: _tvaV === "da" ? (corp.querySelector("#vf-tva_data_inceput").value || null) : null,
  };
  // [alege] alegerile obligatorii ale vectorului. regim NU se cere la partida simpla (PFA/II/PFL n-are
  // micro/profit — vine din payload, fapt unic backend). tva si ic se cer la orice firma. Periodicitatea: DOAR la plătitori.
  const vecOblig = [];
  if (!(v && v.partida_simpla) && !vf.regim_fiscal)
    vecOblig.push(["vf-regim_fiscal", "Alege regimul fiscal (micro sau profit) — decide D100/D101."]);
  if (vf.platitor_tva === null)
    vecOblig.push(["vf-platitor_tva", "Alege dacă firma e înregistrată în scopuri de TVA (Da sau Nu) — decide D300/D394."]);
  if (vf.operatiuni_ic === null)
    vecOblig.push(["vf-operatiuni_ic", "Alege dacă firma are operațiuni intracomunitare (Da sau Nu) — decide D390."]);
  if (vf.platitor_tva === true && !vf.tip_decont)
    vecOblig.push(["vf-tip_decont", "Periodicitatea TVA e obligatorie la plătitorii de TVA (decide dacă D300 se depune lunar sau trimestrial)."]);
  return { vf, vecOblig };
}

// [lotul 10, 428] Ce trimite „Salvează” pentru regimul TVA la încasare, sau null dacă nu s-a schimbat nimic (sau firma nu e înregistrată
// în scopuri de TVA: secțiunea e ascunsă și nu se trimite). Starea de la încărcare: `v.tva_incasare`.
function _tvaiDinFormular(corp, v, platitor) {
  const sel = corp.querySelector("#vf-tva_incasare");
  if (!sel || platitor !== true) return null;
  const t = (v && v.tva_incasare) || {};
  const c = t.curenta || {};
  const aplica = sel.value === "da";
  // [lotul 12, deficiența 626 — comanda Costin 12.2 pct.13: „după ce scrii și golești «Aplică de la», perioada nouă rămâne obligatorie și
  // oprește salvarea. Perioadă nouă doar la cerere.”] pe o firmă cu perioada înregistrată, „Aplică de la” golit nu cere nimic: rămâne data
  // înregistrată (câmpul o și reia la ieșire, `_legaTvaIncasare`); o perioadă nouă se cere scriind data ei. Fără perioadă înregistrată,
  // „Da” e cererea, deci data rămâne de scris.
  const de_la = aplica ? (corp.querySelector("#vf-tva_incasare_de_la").value || c.de_la || null) : null;
  const pana_la = aplica ? (corp.querySelector("#vf-tva_incasare_pana_la").value || null) : null;
  // [lotul 13, 541] data notificării: verificată de server la „de la” nou sau schimbat (CF art.282 alin.(3^1) lit.a))
  const data_optiune = aplica ? (corp.querySelector("#vf-tva_incasare_data_optiune").value || null) : null;
  const eraDa = !!t.curenta || !!t.fara_data;
  if (aplica === eraDa && (!aplica || (de_la === (c.de_la || null) && pana_la === (c.pana_la || null)
    && data_optiune === (c.data_optiune || null)))) return null;
  return { aplica, de_la, pana_la, data_optiune };
}

// [lotul 10, 428] „Verifică în registrul ANAF” (citire: propune datele, spune dacă diferă; nu scrie) și ștergerea unei perioade scrise greșit.
function _legaTvaIncasare(corp, nav, tenantId, opt) {
  // [626] „Aplică de la” golit revine, la ieșirea din câmp, la data înregistrată (ca „Luna preluării”, 169): golirea nu e o perioadă nouă
  const deLa = corp.querySelector("#vf-tva_incasare_de_la");
  if (deLa && deLa.defaultValue) deLa.addEventListener("blur", () => { if (!deLa.value) deLa.value = deLa.defaultValue; });
  const btn = corp.querySelector("#vf-tva-incasare-anaf");
  const rez = corp.querySelector("#vf-tva-incasare-anaf-rez");
  if (btn) btn.addEventListener("click", async () => {
    rez.innerHTML = "";
    try {
      const r = await api.get(`/tenants/${tenantId}/tva-incasare/verifica-anaf`);
      arataMesaj(rez, r.mesaj, r.fel === "fapt" ? "ok" : "avert");   // afirmația tipată (`compara_anaf`): „fapt” = coincide
      if (r.propunere) {
        const b = document.createElement("button");
        b.type = "button"; b.className = "buton-secundar"; b.id = "vf-tva-incasare-anaf-preia";
        b.setAttribute("data-fara-actiune", "completează formularul cu datele ANAF; „Salvează” poartă acțiunea");
        b.textContent = "Completează cu datele ANAF";
        b.addEventListener("click", () => {
          corp.querySelector("#vf-tva_incasare").value = "da";
          corp.querySelector("#vf-tva_incasare_de_la").value = r.propunere.de_la || "";
          corp.querySelector("#vf-tva_incasare_pana_la").value = r.propunere.pana_la || "";
          corp.querySelector("#vf-tva_incasare").dispatchEvent(new Event("change"));
          arataMesaj(rez, "Completat cu datele ANAF — verifică și apasă „Salvează”.", "info");
        });
        rez.appendChild(b);
      }
    } catch (e) { arataMesaj(rez, (e && e.mesaj) || "Verificarea în registrul ANAF nu s-a putut face.", "eroare"); }
  });
  // [lotul 10, deficiența 428] „ieșirea din sistem face regularizarea”: la data ieșirii, facturile emise / primite în sistem cu TVA încă
  // neexigibil (4428) și ce se întâmplă cu fiecare — CF art.282 alin.(7) lit.b: cele emise înainte de ieșire rămân în sistem până la
  // încasare; nimic nu se mută în 4427 fără încasare (citire, `GET …/tva-incasare/neexigibile`)
  corp.querySelectorAll("#vf-tva-incasare-perioade button[data-iesire]").forEach((b) => b.addEventListener("click", async () => {
    const z = corp.querySelector("#vf-tva-incasare-iesire");
    z.innerHTML = "";
    try {
      const r = await api.get(`/tenants/${tenantId}/tva-incasare/neexigibile?la=${encodeURIComponent(b.dataset.iesire)}`);
      const f = r.facturi || [];
      z.innerHTML = !f.length
        ? `<p class="pf-intro">La ieșirea din ${esc(dataRo(r.la))} nu rămâne nicio factură cu TVA neexigibil: nimic de regularizat.</p>`
        : `<p class="pf-intro">La ieșirea din ${esc(dataRo(r.la))} rămân în sistem ${cate(f.length, "factură", "facturi")}: TVA neexigibil pe emise ${bani(r.tva_neexigibil_emise)} lei, TVA nededus pe primite ${bani(r.tva_nededus_primite)} lei (Cod fiscal art. 282 alin. (7) lit. b).</p>
          <table class="fd-tabel" id="vf-tva-incasare-iesire-tabel"><thead><tr><th>Factură</th><th>Data</th><th class="fd-td-num">TVA</th>
            <th class="fd-td-num">Exigibil până acum</th><th class="fd-td-num">Rămas pe 4428</th><th>Ce se întâmplă</th></tr></thead>
          <tbody>${f.map((x) => `<tr><td>${esc(x.directie === "emisa" ? "emisă" : "primită")} ${esc(numarCuSerie(x.serie, x.numar))}</td>
            <td>${esc(dataRo(x.data_emitere))}</td><td class="fd-td-num">${bani(x.tva)}</td><td class="fd-td-num">${bani(x.exigibil)}</td>
            <td class="fd-td-num">${bani(x.rest_neexigibil)}</td><td>${esc(x.ce_se_intampla)}</td></tr>`).join("")}</tbody></table>`;
    } catch (e) { arataMesaj(z, (e && e.mesaj) || "Lista facturilor rămase în sistem nu s-a putut încărca.", "eroare"); }
  }));
  corp.querySelectorAll("#vf-tva-incasare-perioade button[data-perioada]").forEach((b) => b.addEventListener("click", () => {
    confirmaCaseta(b.closest("table"), "Ștergi perioada? Se face numai pentru o perioadă scrisă din greșeală; ieșirea din sistem se scrie la „Aplică până la”.",
      async () => {
        try {
          await api.del(`/tenants/${tenantId}/tva-incasare/${b.dataset.perioada}`);
          await _redeseneazaPeLoc(corp, nav, tenantId, opt);
          arataMesaj(corp.querySelector("#df-msg"), "Perioada a fost ștearsă. Schimbarea e în istoricul de mai jos.", "ok");
        } catch (e) { refuzPeRand(b, (e && e.mesaj) || "Perioada nu s-a putut șterge."); }
      }, { textOk: "Șterge perioada" });
  }));
}

// [lotul 10, 431] Tabelul asociaților: modelul, re-randarea la adăugare / scoatere (DS cap.24), totalul cotelor, ce trimite „Salvează”.
function _legaAsociati(corp, a) {
  const tb = corp.querySelector("#as-randuri");
  if (!tb || !a) return null;
  const initial = (a.asociati || []).map((x) => ({ nume: x.nume, cnp: x.cnp, cota: String(x.cota) }));
  let model = initial.length ? initial.map((x) => ({ ...x })) : [{ nume: "", cnp: "", cota: "" }];
  const citeste = () => model.forEach((r, i) => {
    r.nume = (corp.querySelector(`#as-${i + 1}-nume`).value || "").trim();
    r.cnp = (corp.querySelector(`#as-${i + 1}-cnp`).value || "").trim();
    r.cota = (corp.querySelector(`#as-${i + 1}-cota`).value || "").trim();
  });
  const total = () => {
    const s = model.reduce((x, r) => x + (numarRo(r.cota).valoare || 0), 0);   // [655] cota scrisă de om, citită românește (DS cap.6)
    const el = corp.querySelector("#as-total");
    const txt = (Math.round(s * 100) / 100).toString().replace(".", ",");
    el.textContent = `Total cote: ${txt}%` + (Math.abs(s - 100) < 0.005 ? "" : " — cotele trebuie să însumeze 100% (tot capitalul social).");
  };
  const randeaza = () => {
    tb.innerHTML = _randuriAsociati(model);
    tb.querySelectorAll("button[data-as-sterge]").forEach((b) => b.addEventListener("click", () => {
      citeste(); model.splice(Number(b.dataset.asSterge), 1); randeaza();
    }));
    total();
  };
  tb.addEventListener("input", () => { citeste(); total(); });
  corp.querySelector("#as-adauga").addEventListener("click", () => { citeste(); model.push({ nume: "", cnp: "", cota: "" }); randeaza(); });
  randeaza();
  return {
    dinFormular() {
      citeste();
      // un rând complet gol (cel pus din oficiu la o firmă fără asociați) nu e un asociat început: nu se trimite
      const randuri = model.filter((r) => r.nume || r.cnp || r.cota);
      const schimbat = JSON.stringify(randuri) !== JSON.stringify(initial);
      return { randuri, schimbat, dataCesiune: corp.querySelector("#as-data-cesiune").value || null };
    },
  };
}

// [deficiența 272] corectura CUI-ului: CUI-ul corect -> avertismentul serverului -> confirmarea -> scrierea (ambele locuri + jurnal)
function _corecturaCui(corp, nav, tenantId, opt) {
  const zona = corp.querySelector("#df-cui-corectura");
  zona.innerHTML = `<label class="camp"><span class="camp-eticheta">CUI-ul corect<span class="oblig">*</span></span>
      <input type="text" class="camp-input" id="df-cui-nou" aria-label="CUI-ul corect"></label>
    <button type="button" class="buton-primar" id="df-cui-continua" data-actiune="POST /tenants/{tenant_id}/cui/corectura">Continuă</button>
    <div id="df-cui-aviz"></div>
    <div id="df-cui-msg"></div>`;
  const msg = zona.querySelector("#df-cui-msg");
  const cuiScris = () => (zona.querySelector("#df-cui-nou").value || "").trim();
  // [lotul 11, 440] refuzul serverului: erorile lui stau lângă singurul câmp al pasului (CUI-ul corect), textul fără câmp în zona pasului
  const laCui = (e) => ({ campuri: Object.fromEntries(((e && e.erori_campuri) || []).map((c) => [c.camp, "df-cui-nou"])) });
  // pasul 1: CUI-ul corect -> avertismentul serverului (nimic scris), cu butonul de confirmare
  zona.querySelector("#df-cui-continua").addEventListener("click", async () => {
    curataEroriCamp(zona);
    zona.querySelector("#df-cui-aviz").innerHTML = "";
    if (!cuiScris()) { eroareCamp(zona, "df-cui-nou", "Scrie CUI-ul corect."); return; }
    try {
      const r = await api.post(`/tenants/${tenantId}/cui/corectura`, { cui: cuiScris(), confirmat: false });
      // [459, comanda Costin 11.3 pct.5] datele ANAF ale CUI-ului nou, câmp cu câmp (acum -> ANAF): confirmarea le preia; fără ANAF, ce
      // rămâne de verificat — nimic din CUI-ul vechi nu rămâne tacit
      const an = r.anaf || {};
      const schimbari = (an.schimbari || []).map((s) => `<li><b>${esc(s.eticheta)}</b>: ${esc(s.acum)} → ${esc(s.anaf)}</li>`).join("");
      zona.querySelector("#df-cui-aviz").innerHTML = `<div class="caseta-atentie"><div class="ca-mesaj">${esc(r.avertisment || "")}
          <div id="df-cui-anaf"><p>${esc(an.mesaj || "")}</p>${schimbari ? `<ul>${schimbari}</ul>` : ""}</div></div>
        <button type="button" class="buton-primar" id="df-cui-confirma" data-actiune="POST /tenants/{tenant_id}/cui/corectura">Corectez CUI-ul</button></div>`;
      // pasul 2: confirmarea -> scrierea (ambele locuri + jurnal)
      zona.querySelector("#df-cui-confirma").addEventListener("click", async () => {
        try {
          const r2 = await api.post(`/tenants/${tenantId}/cui/corectura`, { cui: cuiScris(), confirmat: true });
          const a2 = r2.anaf || {};
          const preluate = (a2.schimbari || []).map((s) => s.eticheta).join(", ");
          await _redeseneazaPeLoc(corp, nav, tenantId, opt);
          arataMesaj(corp.querySelector("#df-msg"), `CUI-ul a fost corectat: ${r2.cui}. ${a2.gasit ? (preluate ? `Din ANAF s-au preluat: ${preluate}.` : "")
            : (a2.mesaj || "")} Schimbarea e în jurnalul de mai jos.`, a2.gasit ? "ok" : "avert");
        } catch (e) { arataRefuzul(zona, e, msg, laCui(e)); }
      });
    } catch (e) { arataRefuzul(zona, e, msg, laCui(e)); }
  });
  zona.querySelector("#df-cui-nou").addEventListener("input", () => { zona.querySelector("#df-cui-aviz").innerHTML = ""; });   // avertismentul era pentru CUI-ul de dinainte
}

// Câmpurile Date firmă, citite din formular (o singură citire; handlerul „Salvează” le trimite). [08.10.2026] scoasă din handler:
// sonda drepturilor leagă un apel de butonul lui pe o fereastră de 80 de linii, iar citirea câmpurilor o depășea.
function _dateDinFormular(corp) {
  const date = {};
  for (const c of CAMPURI) {
    const el = corp.querySelector(`#df-${c.k}`);   // [lotul 13, C71.1] un câmp fără rost pentru forma firmei nu e pe ecran: nu se trimite
    if (el) date[c.k] = (el.value || "").trim();
  }
  date.cont_venit_implicit = corp.querySelector("#df-cont_venit").value;  // [F182] preferinta contabila la emitere
  // [lot 19 d12] forma juridică + capitalul (Legea 31/1990 art. 74 alin. (3)); lipsesc la PFA/II/IF
  date.activitate_exceptata_amef = corp.querySelector("#df-activitate_exceptata_amef").value;   // [D394 Î2]
  date.activitate_amef = corp.querySelector("#df-activitate_amef").value || null;
  date.metoda_stoc = corp.querySelector("#df-metoda_stoc").value || null;   // [06.10.2026 §6.3]
  date.serie_chitanta = corp.querySelector("#df-serie_chitanta").value.trim() || null;   // [decizii 07.10 pct.5]
  // [08.10 §6 pct.4 + retest 08.10 pct.20] luna neschimbată nu se trimite (rămâne ce era); golită sau egală cu propunerea = propunerea
  // (null), nu o valoare fixată; [lotul 12, 147] luna efectivă plafonată la prima notă, nemișcată, nu rescrie tacit luna aleasă
  const _lp = corp.querySelector("#df-luna_preluare");
  if (_lp.value !== _lp.dataset.initiala) date.luna_preluare = (_lp.value && _lp.value !== _lp.dataset.propunere) ? _lp.value : null;
  date.data_infiintare = corp.querySelector("#df-data_infiintare").value || null;   // [deficiența 229]
  if (corp.querySelector("#df-forma_juridica")) {
    date.forma_juridica = corp.querySelector("#df-forma_juridica").value || null;
    date.capital_subscris = (corp.querySelector("#df-capital_subscris").value || "").trim() || null;
    date.capital_varsat = (corp.querySelector("#df-capital_varsat").value || "").trim() || null;
  }
  return date;
}

function eticheta(k) {
  const c = CAMPURI.find((x) => x.k === k);
  return c ? c.e : (ETICHETE_CAPITAL[k] || k);
}
