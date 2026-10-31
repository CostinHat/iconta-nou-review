// control_verdict.js — renderer UNIC al corpului verdictului de control fiscal.
// Sursa unica pentru DETALIU (control.js) si cardul din fisa firmei (firme.js): acelasi payload
// (/control-fiscal/{id}), aceleasi sectiuni, aceleasi chei. Inainte existau trei renderere divergente,
// fiecare cu alt subset hardcodat de chei din verificari_contabile -> constatari BLOCANTE invizibile pe
// unele ecrane (cazul DANTE 24.07: cele 4 rosii pe salarii nu apareau pe cardul din fisa).
// Regula DS cap.20: sectiunile pot diferi intre ecrane, cheile dintr-o sectiune randata NU. Garda
// VERDICT_PARITATE (verificator) impune paritatea prin inventarul declarat VC_RANDATE de mai jos.
import { VERDICT_POZITIV } from "./verdict.js?v=fb322c8d48";  // [P13c] punctul unic de verdict
import { api, cate, esc, dataRo, confirmaCaseta, arataMesaj, bani, focusFaraSalt, refuzPeRand, atributeInactiv } from "../api.js?v=4364ee71f3";
import { cuLegareaNir, interogareLegare } from "./nir_legare.js?v=b34abfe2ec";
import { ECRANE as ECRANE_DESTINATIE } from "./ecran_destinatie.js?v=5152ec2b0a";   // [D2, 14.3] butonul „de lămurit” spre Date firmă
import { randeazaStareSpv } from "./spv_stare.js?v=228cdfcde1";  /* [deficiența 463] starea SPV a firmei, aceeași ca în fereastra firmei */

// Paleta de semafor UNICA (inlocuieste control.js CULORI + firme.js _CF_CUL — erau doua copii divergente).
export const CULORI = {
  verde:  { dot:"radial-gradient(circle at 65% 30%, #6fc494, var(--verde) 60%)", txt:"la zi",       bg:"var(--verde-fundal)" },
  galben: { dot:"radial-gradient(circle at 65% 30%, #f0cd7a, var(--galben) 60%)", txt:"de urmărit",  bg:"var(--galben-fundal)" },
  rosu:   { dot:"radial-gradient(circle at 65% 30%, #ff8a80, var(--rosu-semafor) 60%)", txt:"restanță", bg:"var(--rosu-fundal)" },
  gri:    { dot:"var(--gri-semafor)", txt:"nu se poate verifica", bg:"var(--gri-fundal-semafor)" },
};

// INVENTAR DECLARAT — paritatea 1 (RANDARE). Fiecare cheie din payload-ul `verificari_contabile` (vc)
// trebuie sa aiba aici o destinatie: o sectiune randata, sau "via d.contabil", sau marcata contor. O cheie
// noua produsa de backend fara intrare aici = EROARE in verificator (VERDICT_PARITATE, sub-regula randare),
// nu omisiune tacuta. Sursa cheilor produse: dict-ul `rezultat` din _verificari_contabile (main.py). Cap.20.
export const VC_RANDATE = {
  tva_incrucisat:        "Declarație vs contabilitate",
  d112_incrucisat:       "Declarație vs contabilitate",
  d390_incrucisat:       "Declarație vs contabilitate",
  cota_tva_conformitate: "Conformitate facturi emise",
  tva:                   "Coerență TVA (balanță)",
  documente_pozate:      "Documente pozate",
  echilibru:             "via d.contabil — Verificări contabile",
  trezorerie:            "via d.contabil — Verificări contabile",
  note:                  "__contor__ (numar de note, nu constatare)",
};

// [deficiența 226, comanda Costin 12.10.2026, verbatim în DECIZII] „în fereastra Control fiscal, eticheta din dreapta fiecărei firme e una
// din cele 4 stări (restanță, de urmărit, la zi, nu se poate verifica). Acum apar «neconcordanță» și «2 nu se pot verifica». Detaliul
// rămâne pe rândul de dedesubt.” PIVOT pe [08.10 retest pct.7] (eticheta = cauza: „neconcordanță”) și [eticheta_din_fapt 20.08]
// (griul cu numărul): eticheta stării = numele culorii, una din patru; numărul și cauza stau în detaliu (rândul de dedesubt, grupele
// ferestrei firmei). Aceeași funcție pentru rândul listei și pentru antetul detaliului — o singură listă de nume (CULORI.txt).
export function etichetaStare(stare) {
  return (CULORI[stare] || CULORI.gri).txt;
}

// anatomie constatare (dot + mesaj + temei + remediu) — renderer unic pt «Verificari contabile» si audit.
// [01.09.2026] EXPORTAT: ecranul supervizorului randeaza aceeasi anatomie. A doua randare a ei ar
// diverge, iar TEMEIUL — partea ceruta explicit de Costin — e prima care s-ar pierde.
// [deficiența 220, decizia Costin 10.10.2026: „Roșu înseamnă termen depășit.”] În Control fiscal roșul e al RESTANȚELOR (termen trecut,
// nedepusă). O constatare — neconcordanță, declarație nedepusă înainte de termen, verificare contabilă eșuată, audit divergent — se
// arată cel mult galben. Serverul păstrează severitatea verificatorului (porțile cozii și alertele o folosesc); aici e numai culoarea.
// Gard: regula ROSU_DOAR_RESTANTA din verificator + `core/test_rosu_termen_depasit.py`.
export function stareAfisata(s) { return s === "rosu" ? "galben" : s; }

export function randA(c) {
  const dot = CULORI[c.stare] ? CULORI[c.stare].dot : CULORI.gri.dot;
  const r = c.remediu;
  const extra = r ? `<div class="cf-incr-remediu"><b>${esc(r.cauza || "")}</b><br>${esc(r.actiune || "")}</div>` : "";
  return `<div class="cf-incr-rand">
    <div class="cf-incr-cap"><span class="cf-dot" style="background:${dot}"></span><span>${esc(c.mesaj || "")}</span></div>
    <div class="cf-incr-temei">${esc(c.temei || "")}</div>
    ${extra}
  </div>`;
}

// [D2, 14.3] o constatare care știe ecranul unde se lămurește („de lămurit”: răspunsul OSS din Date firmă) trimite acolo; una fără ecran nu are ce trimite
function trimiteLaEcran(x) {
  if (!x.ecran) return "";
  return `<button type="button" class="btn-link" data-ecran-destinatie="${esc(x.ecran)}">${esc(x.eticheta_ecran || "Deschide")}</button>`;
}

// anatomie constatare cu remediu EXECUTABIL (buton «Contabilizeaza facturile») — pt cross-check-uri.
function randConst(c) {
  const dot = CULORI[stareAfisata(c.stare)] ? CULORI[stareAfisata(c.stare)].dot : CULORI.gri.dot;
  let extra = "";
  if (c.remediu) {
    const r = c.remediu;
    // [lotul 13, 675 — DS cap.1] butonul stă la fiecare remediu; unde nu sunt facturi de contabilizat din aplicație, e inactiv, cu motivul
    const areFacturi = r.fel === "executabil" && (r.facturi || []).length > 0;
    // [694.1 b, 14.3] neconcordanța rezultatului decontului cu nota de închidere TVA: acțiunea e regularizarea TVA a perioadei (Închidere lună), nu contarea facturilor
    const buton = r.fel === "regularizare_tva"
      ? `<button class="buton-secundar cf-regulariza-tva" data-actiune="POST /tenants/{tenant_id}/inchidere/regularizare-tva" data-an="${esc(String(r.an))}" data-luna="${esc(String(r.luna))}" style="margin-top:8px">Regularizează TVA-ul perioadei</button>`
      : `<button class="buton-secundar cf-incr-btn" data-actiune="POST /tenants/{tenant_id}/facturi/{factura_id}/contabilizeaza" data-facturi="${esc((r.facturi || []).join(","))}" style="margin-top:8px"${
        areFacturi ? "" : atributeInactiv("Constatarea nu are facturi de contabilizat din aplicație; remediul e cel scris mai sus.")}>Contabilizează facturile</button>`;
    extra = `<div class="cf-incr-remediu"><b>${esc(r.cauza || "")}</b><br>${esc(r.actiune || "")}<div>${buton}</div></div>`;
  }
  return `<div class="cf-incr-rand">
    <div class="cf-incr-cap"><span class="cf-dot" style="background:${dot}"></span><span>${esc(c.mesaj || "")}</span></div>
    <div class="cf-incr-temei">${esc(c.temei || "")}</div>
    ${extra}
  </div>`;
}

// rand de declaratie cu termen (Restante / De urmarit / La zi) — poarta MOTIVUL pe orice culoare.
function randDecl(arr, clasa, marcabil = false) {
  // [08.10, decizia Costin U2] „O declarație anterioară se poate marca «depusă în afara iConta», cu recipisă opțională.”
  // [retest 08.10 pct.10] o MARCARE („în afara iConta.eu” / „de contabilul anterior”) se poate modifica sau anula
  const marcare = (x) => x.extern ? `
      <button class="buton-secundar cf-extern-btn" data-actiune="POST /control-fiscal/{tenant_id}/depusa-extern"
        data-tip="${esc(x.tip)}" data-an="${x.an}" data-luna="${x.luna}" data-perioada="${esc(x.perioada || "")}">Modifică marcarea</button>
      <button class="buton-secundar cf-extern-anuleaza" data-actiune="POST /control-fiscal/{tenant_id}/depusa-extern/anuleaza"
        data-tip="${esc(x.tip)}" data-an="${x.an}" data-luna="${x.luna}" data-perioada="${esc(x.perioada || "")}">Anulează marcarea</button>`
    : (!marcabil || !x.luna) ? "" : `
      <button class="buton-secundar cf-extern-btn" data-actiune="POST /control-fiscal/{tenant_id}/depusa-extern"
        data-tip="${esc(x.tip)}" data-an="${x.an}" data-luna="${x.luna}" data-perioada="${esc(x.perioada || "")}">Marchează depusă în afara iConta.eu</button>`;
  return arr.map((x) => `
    <div class="cf-decl-item" data-cheie="${esc(x.tip || "")}-${x.an || ""}-${x.luna || ""}">
      <div class="mig-sold-rand cf-rand-decl">
        <span class="mig-sold-cont">${esc((x.tip || "").toUpperCase())}</span>
        <span class="cf-perioada">${esc(x.perioada || "")}</span>
        <span class="cf-termen ${clasa}">termen ${dataRo(x.termen)}</span>
      </div>
      ${x.motiv ? `<div class="cf-incr-temei">${esc(x.motiv)}</div>` : ""}${marcare(x)}
    </div>`).join("");
}
// rand de declaratie fara termen (Nu se poate verifica / Nu se datoreaza) — doar tip + motiv.
// [R6 21.08.2026] Un motiv poate primi un SEMNAL: o depunere care îl pune la îndoială. Varianta (b),
// decisă de Costin: fiecare semnal stă lângă afirmația pe care o contrazice, nu într-un grup propriu —
// contradicția (defect al NOSTRU) și opinia (informație) cer lucruri diferite de la contabil.
// Semnalele care nu-și găsesc perechea NU dispar: se randează la coada grupului. Un semnal pierdut
// tăcut ar fi exact clasa de defect pe care mecanismul ăsta o vânează.
// [P3 21.08.2026] Domeniul unei afirmații, în limba contabilului. Felul NU se tipărește — contabilul
// n-are ce face cu „absenta_observatie" — dar își face treaba: decide CE se poate scrie ca perioadă.
// Oglinda lui `core/afirmatii.domeniu_text`; dacă afirmația n-are domeniu prin natura ei (`statut`),
// nu se inventează unul. Efectul care a cerut-o: D300 apărea și în «De urmărit · iul», și în «Nu pot
// verifica» fără nicio perioadă, deci cele două păreau să se contrazică deși vorbeau de luni diferite.
// „2025-12" -> „12.2025": acelasi registru ca restul ecranului (termene, blocaje), nu ISO. Vazut
// privind captura: „din 2025-12" statea langa „iul" in aceeasi lista, doua formate pentru acelasi fel
// de lucru.
// [Retest 2, pct.14] „perioade în trei formate («iun», «T3», «03.2026», «04/2026»)” — DS cap.4 v2.85: luna „LL/AAAA”, trimestrul
// „T3/2026”, anul „2026”. Perioada faptului vine gata de la server (`perioada`); domeniul unei necunoașteri se scrie la fel.
const _luniAn = (s) => (/^\d{4}-\d{2}$/.test(s || "") ? `${s.slice(5)}/${s.slice(0, 4)}` : (s || ""));

function domeniuAfirmatie(x) {
  if (x.fel === "fapt") return x.perioada || (x.luna ? dataRo(new Date(x.an, x.luna - 1, 1), "luna_an_numeric") : String(x.an || ""));
  if (x.fel === "necunoastere") {
    const dd = x.domeniu_de || "", dp = x.domeniu_pana || "";
    if (/^\d{4}-01$/.test(dd) && dp === `${dd.slice(0, 4)}-12`) return dd.slice(0, 4);   // un an întreg
    const de = _luniAn(dd), pana = _luniAn(dp);
    if (de && pana) return de === pana ? de : `${de} – ${pana}`;
    return de ? `din ${de}` : "";
  }
  return "";
}

function randMotiv(arr, semnale = [], felCls = "") {
  const folosite = new Set();
  const potrivite = (x) => semnale.filter((s, i) => {
    const acelasiTip = s.tip === x.tip;
    const acelasiInterval = x.an == null || (s.an === x.an && s.luna === x.luna);
    if (acelasiTip && acelasiInterval) { folosite.add(i); return true; }
    return false;
  });
  const randSemnal = (s) => `<div class="cf-semnal ${felCls}">${esc(s.mesaj || "")}</div>`;
  const corp = arr.map((x) => `
    <div class="cf-decl-item">
      <div class="cf-incr-cap"><span class="mig-sold-cont">${esc((x.tip || "").toUpperCase())}</span>${
        domeniuAfirmatie(x) ? `<span class="cf-perioada">${esc(domeniuAfirmatie(x))}</span>` : ""}</div>
      <div class="cf-incr-temei">${esc(x.motiv || "")}</div>
      ${trimiteLaEcran(x)}
      ${x.surse_consultate ? `<div class="cf-incr-temei">Căutat în: ${esc(x.surse_consultate)}</div>` : ""}
      ${x.temei_completitudine ? `<div class="cf-incr-temei">Pe ce se sprijină: ${esc(x.temei_completitudine)}</div>` : ""}
      ${potrivite(x).map(randSemnal).join("")}
    </div>`).join("");
  const orfane = semnale.filter((_, i) => !folosite.has(i));
  return corp + (orfane.length
    ? `<div class="cf-decl-item">${orfane.map(randSemnal).join("")}</div>` : "");
}
// verificare booleana (echilibru/tva/documente) — dot verde/rosu dupa .ok.
function randVerif(eticheta, ok, detaliu) {
  return `<div class="cf-verif">
    <span class="cf-verif-dot" style="background:${ok ? "var(--verde)" : "var(--galben)"}"></span>
    <span class="cf-verif-txt">${eticheta}${detaliu ? ` <span class="tip-micut">${detaliu}</span>` : ""}</span>
  </div>`;
}

const RANG = { rosu: 3, galben: 2, gri: 1, verde: 0 };
// etichetele constatarilor incrucisate care apar deja in «Declaratie vs contabilitate» -> filtrate din
// «Verificari contabile» ca sa nu se dubleze (sumarul lor e in contabil, constatarea intreaga e in incrucisat).
// [08.10, decizia Costin U2] și variantele „nedeclarat” (nimic depus pe perioadă) — oglinda lui uc_comun.ETICHETE_INCRUCISAT
// [deficiența 463] constatările e-Factura stau în secțiunea lor («e-Factura — transmiterea în SPV»); oglinda lui uc_comun.ETICHETA_SPV_*
const DEJA_IN_EFACTURA = ["Facturi netransmise în SPV după termen", "SPV fără drept pe firmă"];
const DEJA_IN_INCRUCISAT = ["TVA declarat diferă de contabilitate", "Salarii declarate diferă de contabilitate",
  "Operațiuni intracomunitare declarate diferă de evidență", "Facturi emise cu cotă TVA greșită pentru perioadă",
  "TVA nedeclarat", "Salarii nedeclarate", "Operațiuni intracomunitare nedeclarate"];

// RENDERER UNIC al corpului. Primeste payload-ul d de la /control-fiscal/{id}. Sectiunile difera de la ecran
// la ecran doar prin ce anteta/pastila pune APELANTUL deasupra; corpul (constatarile) e IDENTIC. opt.mod e
// rezervat pentru diferente cosmetice viitoare, NU pentru a ascunde constatari.
export function randeazaCorpVerdict(d, opt = {}) {
  const vc = d.verificari_contabile || {};
  // [C4, decizie 23.07] restantele: lista plata (fara grupare pe tip), sortata pe vechimea depasirii
  // termenului (cel mai vechi intai; ISO -> sort lexical). Acelasi criteriu pe ambele ecrane, prin renderer.
  const lipsa = (d.lipsa || []).slice().sort((a, b) => (a.termen || "").localeCompare(b.termen || ""));
  const urmarit = (d.urmarit || []).slice().sort((a, b) => (a.termen || "").localeCompare(b.termen || ""));
  const confirmate = d.confirmate || [];
  // [DESIGN_SYSTEM cap.8 — semafor: ordine roșu→galben→verde + tokeni de culoare] «La zi» (verde) =
  // depus LA termen. O depunere DUPĂ termen nu e verde, dar nici restanță (roșu) -> categorie proprie
  // (chihlimbar/galben), informativă. NU urcă pastila firmei (control_fiscal_api._stare neatins).
  const cu_intarziere = d.cu_intarziere || [];
  const inainte = (d.inainte_de_preluare || []).slice().sort((a, b) => (a.termen || "").localeCompare(b.termen || ""));
  const neclar = d.neclar || [];
  const neaplicabile = d.neaplicabile || [];
  // [R6] depuneri fara obligatie pereche: „contrazice" langa «Nu se datoreaza», „opinie" langa
  // «Nu se poate verifica». NU urca pastila (control_fiscal_api._stare neatins): rosul pastilei inseamna
  // „ai restante"; o incoerenta de verdict e un defect al nostru, nu o datorie a firmei.
  const semnale = d.depuneri_fara_obligatie || [];
  const contraziceri = semnale.filter((x) => x.fel === "contrazice");
  const opinii = semnale.filter((x) => x.fel === "opinie");

  const declaratii = `
    ${lipsa.length ? `<div class="cf-grup-titlu cf-rosu">Restanțe (${lipsa.length})</div><div class="cf-decl">${randDecl(lipsa, "cf-termen-rosu", true)}</div>` : ""}
    ${urmarit.length ? `<div class="cf-grup-titlu cf-galben">De urmărit (${urmarit.length})</div><div class="cf-decl">${randDecl(urmarit, "cf-termen-galben")}</div>` : ""}
    ${neclar.length || opinii.length ? `<div class="cf-grup-titlu">Nu se poate verifica (${neclar.length})</div><div class="cf-decl">${randMotiv(neclar, opinii, "cf-semnal-opinie")}</div>` : ""}
    ${neaplicabile.length || contraziceri.length ? `<div class="cf-grup-titlu">Nu se datorează (${neaplicabile.length})</div><div class="cf-decl">${randMotiv(neaplicabile, contraziceri, "cf-semnal-contra")}</div>` : ""}
    ${cu_intarziere.length ? `<div class="cf-grup-titlu cf-galben">Depuse cu întârziere (${cu_intarziere.length})</div><div class="cf-decl">${randDecl(cu_intarziere, "cf-termen-galben")}</div>` : ""}
    ${confirmate.length ? `<div class="cf-grup-titlu cf-verde">La zi (${confirmate.length})</div><div class="cf-decl">${randDecl(confirmate, "cf-termen-verde")}</div>` : ""}
    ${inainte.length ? `<div class="cf-grup-titlu cf-inainte-titlu">Înainte de preluare în iConta.eu — până la ${esc(d.luna_inainte_de_preluare || "")} (${inainte.length}, nu se numără la restanțe)</div>
      <div class="dec-bara"><button type="button" class="buton-secundar cf-inainte-btn" data-fara-actiune="deschide declarațiile de dinainte de preluare, în fereastra lor">Vezi declarațiile de dinainte de preluare (${inainte.length})</button></div>
      <template class="cf-inainte-sablon"><div class="cf-inainte">
        <p class="cf-incr-temei">Luna preluării în iConta.eu e ${esc(d.luna_preluare || "")}${d.luna_preluare_din ? ` (${esc(d.luna_preluare_din)})` : ""}: declarațiile pe ${esc(d.luna_preluare || "")} și după se numără la restanțe, cele până la ${esc(d.luna_inainte_de_preluare || "")} nu se numără la restanțe. O declarație depusă în afara iConta.eu sau de contabilul anterior se marchează pe rândul ei.</p>
        <div class="dec-bara"><button class="buton-secundar cf-anterior-toate" data-actiune="POST /control-fiscal/{tenant_id}/depuse-anterior"
          data-perioade='${esc(JSON.stringify(inainte.filter((x) => x.luna && !x.extern).map((x) => ({ tip: x.tip, an: x.an, luna: x.luna }))))}'${
          /* [lotul 13, 675 — DS cap.1] butonul stă și când nu mai e nimic de marcat: inactiv, cu motivul (până acum dispărea, iar rândurile
             de sub el urcau pe ecran după ultima marcare — e2e 171) */
          inainte.some((x) => x.luna && !x.extern) ? "" : atributeInactiv("Toate declarațiile de dinainte de preluare sunt marcate.")}>Marchează toate ca depuse de contabilul anterior</button></div>
        <div class="cf-decl">${randDecl(inainte, "", true)}</div></div></template>` : ""}`;

  // «Declaratie vs contabilitate» — vc.tva_incrucisat/d112_incrucisat/d390_incrucisat (aceeasi anatomie) + d.reconciliere_surse.
  // [deficiența 484, lotul 12: „Control încrucișat: confruntarea declarații–contabilitate nu rulează”] (1) confruntarea rula pe luna în
  // curs, unde nu e nimic de comparat („coincid” pe 0 cu 0), iar luna care chiar se declară nu apărea nicăieri — acum serverul confruntă
  // luna încheiată (`control_fiscal_api.luna_confruntata`) și ecranul o SPUNE; (2) reconcilierea fiecărei declarații datorate cu
  // documentele perioadei (D300, D394, D390, D301, D112, D406, D100, D101, D205: `reconciliere_surse`) se calcula și nu se arăta
  // deloc — acum are rândurile ei, fiecare cu numele declarației.
  const recon = d.reconciliere_surse || null;
  const sectIncrucisat = (() => {
    const verificatori = [vc.tva_incrucisat, vc.d112_incrucisat, vc.d390_incrucisat].filter(Boolean);
    const cuFinding = verificatori.filter((v) => (v.constatari || []).length);
    // [Retest 2, pct.9] ce nu se aplică firmei (D390 față de D300 la un neplătitor) se spune explicit, nu se tace
    const neaplic = verificatori.flatMap((v) => v.nu_se_aplica || []);
    const reconRand = (recon && recon.constatari) || [];
    if (!cuFinding.length && !neaplic.length && !reconRand.length) return "";
    const stari = cuFinding.map((v) => v.stare).concat(reconRand.map((c) => c.stare));
    const worst = stari.reduce((m, x) => ((RANG[x] || 0) > (RANG[m] || 0) ? x : m), "verde");
    const cls = (worst === "rosu" || worst === "galben") ? "cf-galben" : "";
    // [lotul 14, 694] fiecare comparație își arată perioada (D300 / D390 pe perioada fiscală completă, D112 pe lună), nu „luna în curs”
    const perioade = [["D300", vc.tva_incrucisat], ["D112", vc.d112_incrucisat], ["D390", vc.d390_incrucisat]].filter(([, v]) => v && v.perioada);
    const antet = perioade.length ? `<div class="cf-incr-temei" id="cf-perioade">Perioada comparată: ${perioade.map(([n, v]) => `<b>${esc(n)} ${esc(v.perioada)}</b>`).join(" · ")} — ultima perioadă încheiată, a cărei declarație se depune.</div>` : "";
    const blocuri = cuFinding.map((v) => (v.constatari || []).map(randConst).join("")
      + (v.limita ? `<div class="cf-incr-temei">${esc(v.limita)}</div>` : "")).join("")
      + neaplic.map((t) => `<div class="cf-incr-temei">${esc(t)}</div>`).join("");
    // fiecare rând al reconcilierii poartă numele declarației: „D300 (decont TVA): Recalculul … confirmă cifrele declarației.”
    const cuNume = (c) => (c.eticheta && !String(c.mesaj || "").startsWith(c.eticheta)
      ? Object.assign({}, c, { mesaj: `${c.eticheta}: ${c.mesaj || ""}` }) : c);
    const reconBloc = reconRand.length ? `<div class="cf-incr-temei"><b>Declarațiile recalculate din documente</b></div>`
      + reconRand.map((c) => randConst(cuNume(c))).join("") + (recon.limita ? `<div class="cf-incr-temei">${esc(recon.limita)}</div>` : "") : "";
    return `<div class="cf-grup-titlu ${cls}">Declarație vs contabilitate</div><div class="cf-decl" id="cf-incrucisat">${antet}${blocuri}${reconBloc}</div>`;
  })();

  // «Conformitate facturi emise» — vc.cota_tva_conformitate.
  const sectCota = (() => {
    const cf = vc.cota_tva_conformitate;
    if (!cf || !(cf.constatari || []).length) return "";
    const cls = cf.stare === "rosu" ? "cf-galben" : "";
    const randuri = (cf.constatari || []).map(randConst).join("");
    const limita = cf.limita ? `<div class="cf-incr-temei">${esc(cf.limita)}</div>` : "";
    return `<div class="cf-grup-titlu ${cls}">Conformitate facturi emise</div><div class="cf-decl">${randuri}${limita}</div>`;
  })();

  // «Coerenta TVA (balanta)» — vc.tva (coerenta bruta 4427/4426; distincta de tva_incrucisat = D300 vs contab).
  const sectTva = (() => {
    const t = vc.tva;
    if (!t) return "";
    // [deficiența 211] neplătitorul de TVA: verificarea nu are subiect — se spune, gri, fără bulină verde
    if (t.nu_se_aplica) return `<div class="cf-grup-titlu">Coerență TVA (balanță)</div><div class="cf-decl"><div class="cf-incr-temei">${esc(t.nu_se_aplica)}</div></div>`;
    // [694.1 c, 14.3] fiecare cifră își spune perioada, iar o neconcordanță cu decontul nu e verde
    const np = t.nepotrivire;
    const ok = (t.suma === 0 || !!t.rezultat) && !np;
    const la = t.la_data ? ` la ${dataRo(t.la_data)}` : "";
    const det = `${t.rezultat === "de_plata" ? "de plată" : (t.rezultat === "de_recuperat" ? "de recuperat" : "")} ${bani(t.suma || 0)} lei`
      + (np ? ` — decontul D300 ${np.perioada ? esc(np.perioada) + " " : ""}declară ${np.rezultat === "de_plata" ? "de plată" : "de recuperat"} ${bani(np.declarat)} lei: perioade diferite sau diferență de regularizat` : "");
    return `<div class="cf-grup-titlu">Coerență TVA (balanță)</div><div class="cf-decl">${randVerif(`TVA vs sold balanță${la}`, ok, det)}</div>`;
  })();

  // «Documente pozate» — vc.documente_pozate (bonuri/note de casa confirmate de client, necontate).
  const sectDocumente = (() => {
    const dp = vc.documente_pozate;
    if (!dp) return "";
    const det = dp.ok ? "" : (dp.bonuri_neverificate ? cate(dp.bonuri_neverificate, "bon neverificat", "bonuri neverificate") : "");
    return `<div class="cf-grup-titlu">Documente pozate</div><div class="cf-decl">${randVerif("Documente confirmate de client, contate", dp.ok, det)}</div>`;
  })();

  // «Verificari contabile» — d.contabil (echilibru, trezorerie, stocuri, Intrastat, regim TVA + sumar incrucisat).
  const sectContabil = (() => {
    const items = (d.contabil || []).filter((c) => c && typeof c === "object" && !DEJA_IN_INCRUCISAT.includes(c.eticheta)
      && !DEJA_IN_EFACTURA.includes(c.eticheta));
    if (!items.length) return "";
    const worst = items.reduce((m, c) => ((RANG[c.stare] || 0) > (RANG[m] || 0) ? c.stare : m), "verde");
    const cls = (worst === "rosu" || worst === "galben") ? "cf-galben" : "";
    return `<div class="cf-grup-titlu ${cls}">Verificări contabile (${items.length})</div><div class="cf-decl">${items.map((c) => randA(Object.assign({}, c, { stare: stareAfisata(c.stare) }))).join("")}</div>`;
  })();

  // «e-Factura — transmiterea în SPV» — d.efactura_spv. [deficiența 463, lotul 12: „Termene SPV absente din Control fiscal; lipsa
  // dreptului aflată târziu”] facturile emise de la luna preluării care trebuie transmise și nu sunt, fiecare cu termenul de 5 zile
  // lucrătoare (`facturi_api.termen_spv`), plus starea dreptului SPV al firmei (aceeași ca în fereastra firmei, `spv_stare.js`) —
  // aflată aici, înainte de prima trimitere refuzată
  const sectEfactura = (() => {
    const e = d.efactura_spv;
    if (!e) return "";
    const fs = e.facturi || [];
    const cls = fs.some((f) => f.depasit) ? "cf-galben" : "";
    const rand = (f) => `<div class="cf-decl-item"><div class="mig-sold-rand cf-rand-decl">
        <span class="mig-sold-cont">${esc(f.numar || "")}</span><span class="cf-perioada">din ${dataRo(f.data_emitere)} · ${esc(f.client || "")}</span>
        <span class="cf-termen ${f.depasit ? "cf-termen-galben" : ""}">termen ${dataRo(f.termen)}${f.depasit ? " (depășit)" : ""}</span></div>
        ${f.stare === "respinsa" ? `<div class="cf-incr-temei">Respinsă de ANAF${f.eroare ? `: ${esc(f.eroare)}` : ""} — se corectează și se transmite din nou.</div>` : ""}</div>`;
    const lista = fs.length ? fs.map(rand).join("")
      : `<div class="cf-incr-temei">Nicio factură emisă${e.de_la ? ` din ${esc(e.de_la)}` : ""} nu așteaptă transmiterea în SPV.</div>`;
    return `<div class="cf-grup-titlu ${cls}">e-Factura — transmiterea în SPV${fs.length ? ` (${fs.length})` : ""}</div>
      <div class="cf-decl" id="cf-efactura"><div id="cf-spv-stare"></div>${e.eroare ? `<div class="cf-incr-temei">${esc(e.eroare)}</div>` : ""}${lista}
      <div class="cf-incr-temei">Termenul: 5 zile lucrătoare de la emitere (OUG 120/2021 art.10 alin.(7)). Facturile dinaintea lunii preluării${e.de_la ? ` (${esc(e.de_la)})` : ""} nu se urmăresc aici.</div></div>`;
  })();

  const gata = d.stare === "verde" ? `
    <div class="mig-gata" style="padding:30px 0">
      <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d9e75" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>
      <div class="mig-gata-titlu">${VERDICT_POZITIV.control_depus}</div>
    </div>` : "";

  const audit = `
    <div class="cf-grup-titlu" style="margin-top:20px">Audit de preluare</div>
    <div class="cf-decl" id="cf-audit-zona">
      <div class="cf-incr-temei">Coerența internă a pachetului preluat de la contabilul anterior: balanță, solduri parteneri, mijloace fixe, istoric declarații, registru PFA. Raport datat, repetabil pe măsură ce apar documentele; primul audit rămâne păstrat.</div>
      <div id="cf-audit-istoric"></div>
      <button class="buton-secundar" id="cf-audit-run" data-actiune="POST /control-fiscal/{tenant_id}/audit-preluare" style="margin-top:10px">Rulează auditul de preluare</button>
    </div>`;

  // [P4, DS cap.25.4] „Ce nu poate spune verificarea asta" — despre CAPACITATE, nu despre date.
  // PERMANENTĂ: dacă ar apărea doar câteodată, prezența ei ar deveni semnal și absența ei ar minți.
  // Necolorată (nu e o problemă de rezolvat), jos (nu e alarmă), compactă cu detaliul la extindere
  // (nu într-un „?", care dispare exact pentru cine ar avea nevoie).
  const sectLimite = (() => {
    const lim = d.limite || [];
    if (!lim.length) return "";
    // Rezumatul e o ETICHETĂ, nu o limită: dacă ar consuma un rând din sursă, numărul randat n-ar mai
    // fi egal cu numărul din payload — și un rând pierdut la randare e chiar clasa pe care harta o
    // păzește. Prinsă de `test_randurile_randate_egal_cu_randurile_din_sursa`.
    return `<div class="cf-grup-titlu" style="margin-top:20px">Ce nu poate spune verificarea asta</div>
      <div class="cf-decl"><details class="cf-limite">
        <summary class="cf-incr-temei">Ce am privit, ce nu compar, și ce ar întări verdictul
          <span class="tip-micut">(${lim.length})</span></summary>
        ${lim.map((x) => `<div class="cf-decl-item"><div class="cf-incr-temei">${esc(x.text)}</div></div>`).join("")}
      </details></div>`;
  })();

  // [lotul 14, 687] verdictul stă într-o zonă proprie de derulare (titlul și starea firmei rămân sus): fereastra nu derulează
  return `<div class="cf-corp" data-zona-derulare>` + declaratii + sectIncrucisat + sectCota + sectTva + sectDocumente + sectContabil + sectEfactura + gata
       + sectLimite + audit + `</div>`;
}

// Leaga evenimentele corpului dupa inserare (butoane remediu executabil + audit de preluare on-demand).
// firma: { tenant_id, nume, reincarca? } — reincarca() e apelat dupa contabilizarea reusita, ca sa se
// re-evalueze verdictul (constatarea trece pe verde). Fiecare apelant isi da propriul reincarca.
// [retest 08.10 pct.10] după o marcare fereastra NU sare sus: reîncărcarea păstrează poziția de derulare
// [Retest 2, 09.10.2026, pct.1] „după «Salvează» și după «Anulează marcarea», grupul «Înainte de preluare» se pliază singur și ecranul
// sare departe de rând. […] Grupul rămâne cum l-a lăsat utilizatorul, iar ecranul rămâne pe rândul atins.” Reîncărcarea redesenează tot:
// se țin minte grupurile deschise (clasă + indice) și locul RÂNDULUI atins pe ecran (cheia tip-an-lună), apoi se refac pe rândul regăsit
// — nu pe un număr de pixeli, fiindcă rândurile de deasupra își pot schimba înălțimea.
async function reincarcaPePozitie(corp, firma, atins) {
  const c = corp.closest(".fereastra-corp") || document.scrollingElement;
  const cheieGrup = (d) => `${d.className}#${[...corp.querySelectorAll("details")].filter((x) => x.className === d.className).indexOf(d)}`;
  const deschise = new Set([...corp.querySelectorAll("details")].filter((d) => d.open).map(cheieGrup));
  const rand = atins && atins.closest("[data-cheie]");
  const cheie = rand ? rand.dataset.cheie : null, y0 = rand ? rand.getBoundingClientRect().top : null, sus = c ? c.scrollTop : 0;
  if (typeof firma.reincarca === "function") await firma.reincarca();
  corp.querySelectorAll("details").forEach((d) => { if (deschise.has(cheieGrup(d))) d.open = true; });
  const nou = cheie && [...corp.querySelectorAll("[data-cheie]")].find((e) => e.dataset.cheie === cheie);
  if (c && nou) c.scrollTop += nou.getBoundingClientRect().top - y0;
  else if (c) c.scrollTop = sus;
}

// [deficiența 213, retestul Costin 09.10: „confirmarea anulării marcării scrie «D406 03/2026» pentru T1/2026”] perioada rândului, așa cum
// o scrie rândul („T1/2026”, „2025”, „08/2026” — DS v2.85 cap.4), nu luna de ancoră a declarației
function perioadaButonului(b) {
  return b.dataset.perioada || dataRo(new Date(+b.dataset.an, +b.dataset.luna - 1, 1), "luna_an_numeric");
}

export function legaVerdict(corp, nav, firma) {
  // [lotul 13, 674 — DS cap.2a „Orice acțiune e un buton”; comanda Costin 13.1 supersedează forma „pliat implicit” din 158 (DECIZII)] grupul
  // „Înainte de preluare” nu mai e un grup pliat pe care se dă clic: butonul lui deschide o fereastră nouă (673) cu declarațiile, marcările
  // pe rând și „Marchează toate”. Ce cerea 158 rămâne: grupul nu stă desfăcut din oficiu. Fereastra se desenează din șablonul randat al
  // ecranului de dedesubt; după o marcare se reîncarcă ecranul de dedesubt (`firma.reincarca`) și se redesenează fereastra din șablonul nou.
  // [lotul 13, e2e 122] o declarație marcată „depusă în afara iConta.eu” CU DATA nu mai e „înainte de preluare”: serverul o mută la „La zi”
  // / „Depuse cu întârziere” (`control_fiscal_api`: grupul cuprinde numai obligațiile NEDEPUSE dinaintea preluării). Rândul atins nu se
  // mai găsește în fereastra grupului, deci fereastra se închide și contabilul îl vede în Control fiscal, în grupul în care a ajuns.
  // [D2, 14.3] o necunoaștere cu `ecran` (D398 „de lămurit”) are buton direct spre ecranul unde se lămurește (aceeași tabelă ca refuzurile)
  // [694.1 b, 14.3] „Regularizează TVA-ul perioadei”: Închidere lună, pe luna de sfârșit a perioadei fiscale
  corp.querySelectorAll("button.cf-regulariza-tva").forEach((b) => b.addEventListener("click", async () => {
    const { deschideInchidereLuna } = await import("./firme.js?v=eecc415409");
    deschideInchidereLuna(nav, firma.tenant_id, Number(b.dataset.an), Number(b.dataset.luna));
  }));
  corp.querySelectorAll("button[data-ecran-destinatie]").forEach((b) => b.addEventListener("click", () => {
    const e = ECRANE_DESTINATIE[b.dataset.ecranDestinatie];
    if (e) e.deschide(nav, firma.tenant_id, null, null);
  }));
  corp.querySelectorAll(".cf-inainte-btn").forEach((b) => b.addEventListener("click", () => {
    nav.deschide("Înainte de preluare în iConta.eu", (cc, nn) => {
      let atins = null;
      cc.addEventListener("click", (e) => { const r = e.target instanceof Element && e.target.closest("[data-cheie]"); if (r) atins = r.dataset.cheie; }, true);
      const deseneaza = () => {
        const s = corp.querySelector("template.cf-inainte-sablon");
        cc.innerHTML = s ? s.innerHTML : `<p class="ecran-nota">Nu mai e nicio declarație de dinainte de preluare de arătat; închide fereastra.</p>`;
        legaVerdict(cc, nn, Object.assign({}, firma, {
          reincarca: async () => {
            if (typeof firma.reincarca === "function") await firma.reincarca();
            const s2 = corp.querySelector("template.cf-inainte-sablon");
            if (atins && !(s2 && s2.content.querySelector(`[data-cheie="${CSS.escape(atins)}"]`))) { nn.inapoi(); return; }
            deseneaza();
          } }));
      };
      deseneaza();
    });
  }));
  // [08.10, decizia Costin U2] „depusă în afara iConta”: data depunerii (de pe recipisă) obligatorie, numărul recipisei opțional
  corp.querySelectorAll(".cf-extern-btn").forEach((b) => b.addEventListener("click", () => {
    const item = b.closest(".cf-decl-item");
    if (item.querySelector(".cf-extern-form")) return;
    const per = perioadaButonului(b);
    const f = document.createElement("div");
    f.className = "cf-extern-form";
    f.style.cssText = "display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:8px";
    f.innerHTML = `
      <input type="date" class="camp-input" style="max-width:170px" aria-label="Data depunerii ${esc(b.dataset.tip.toUpperCase())} ${per}" required>
      <input type="text" class="camp-input" style="max-width:220px" maxlength="100" placeholder="nr. recipisă (opțional)" aria-label="Număr recipisă ${esc(b.dataset.tip.toUpperCase())} ${per}">
      <button class="buton-primar cf-extern-salveaza" data-actiune="POST /control-fiscal/{tenant_id}/depusa-extern">Salvează</button>
      <button class="buton-secundar cf-extern-renunta" type="button">Renunță</button>`;
    item.appendChild(f);
    const data = f.querySelector("input[type=date]"), rec = f.querySelector("input[type=text]");
    const ok = f.querySelector(".cf-extern-salveaza"), nu = f.querySelector(".cf-extern-renunta");
    focusFaraSalt(data);
    nu.addEventListener("click", () => f.remove());
    // [retest 08.10 pct.10] mesajul „Scrie data” dispare odată ce data e scrisă (rămânea după completare)
    data.addEventListener("input", () => { const m = f.querySelector(".msg-in-formular"); if (m && data.value) m.remove(); });
    ok.addEventListener("click", async () => {
      if (!data.value) { arataMesaj(f, "Scrie data depunerii, de pe recipisă.", "avert"); focusFaraSalt(data); return; }
      try {
        await api.post(`/control-fiscal/${firma.tenant_id}/depusa-extern`,
          { tip: b.dataset.tip, an: Number(b.dataset.an), luna: Number(b.dataset.luna), data_depunere: data.value, recipisa: rec.value.trim() || null });
        await reincarcaPePozitie(corp, firma, b);
      } catch (e) { arataMesaj(f, e.mesaj || "Nu s-a putut marca declarația.", "eroare"); }
    });
  }));
  corp.querySelectorAll(".cf-extern-anuleaza").forEach((b) => b.addEventListener("click", () => {
    confirmaCaseta(b.parentElement, `Anulezi marcarea ${b.dataset.tip.toUpperCase()} ${perioadaButonului(b)}? Declarația redevine nedepusă.`, async () => {
      try {
        await api.post(`/control-fiscal/${firma.tenant_id}/depusa-extern/anuleaza`, { tip: b.dataset.tip, an: Number(b.dataset.an), luna: Number(b.dataset.luna) });
        await reincarcaPePozitie(corp, firma, b);
      } catch (e) { refuzPeRand(b, e.mesaj || "Nu s-a putut anula marcarea."); }   // [lotul 12, C188] nu rescrie tot rândul
    });
  }));
  corp.querySelectorAll(".cf-anterior-toate").forEach((b) => b.addEventListener("click", () => {
    const perioade = JSON.parse(b.dataset.perioade || "[]");
    confirmaCaseta(b.parentElement, `Marchezi ${cate(perioade.length, "declarație", "declarații")} ca depuse de contabilul anterior? Data depunerii nu se cunoaște; o poți completa apoi pe fiecare.`, async () => {
      try {
        await api.post(`/control-fiscal/${firma.tenant_id}/depuse-anterior`, { perioade });
        await reincarcaPePozitie(corp, firma, b);
      } catch (e) { refuzPeRand(b, e.mesaj || "Nu s-au putut marca declarațiile."); }
    });
  }));

  corp.querySelectorAll(".cf-incr-btn").forEach((b) => b.addEventListener("click", () => {
    const ids = (b.dataset.facturi || "").split(",").filter(Boolean);
    if (!ids.length) return;
    confirmaCaseta(b.parentElement, `Se creează ${cate(ids.length, "notă contabilă ciornă", "note contabile ciornă")}. Continui?`, async () => {
      b.disabled = true;
      b.textContent = "Se contabilizează…";
      let ok = 0;
      const err = [];
      for (const id of ids) {
        // [decizia 08.10 pct.2] o factură de marfă cu NIR „fără factură” nelegat: alegerea se cere pe rând, aici
        const _zl = document.createElement("div");
        b.parentElement.appendChild(_zl);
        try {
          const r = await cuLegareaNir(_zl, "POST /tenants/{tenant_id}/facturi/{factura_id}/contabilizeaza", (alegere) => {
            const q = interogareLegare(alegere);
            return api.post(`/tenants/${firma.tenant_id}/facturi/${id}/contabilizeaza` + (q ? "?" + q : ""), {});
          });
          // [S3] refacerea identică cu nota respinsă nu se face în masă: cere confirmarea pe factură
          if (r && r.cod === "NESCHIMBATA") err.push(`${id}: ${r.mesaj}`); else ok++;
        }
        catch (e) { err.push(`${id}: ${e.mesaj || e.message}`); }
        finally { _zl.remove(); }
      }
      if (err.length) {
        b.disabled = false;
        b.textContent = "Contabilizează facturile";
        { const z = document.createElement("div"); b.after(z); arataMesaj(z, `${cate(ok, "factură contabilizată", "facturi contabilizate")}. Erori: ${err.join("; ")}`, "avert"); }
      } else if (typeof firma.reincarca === "function") {
        firma.reincarca();
      } else {   // [327, clasa] fără reîncărcare ecranul rămâne: butonul nu rămâne „Se contabilizează…”
        b.textContent = "Contabilizate ✓";
      }
    }, { textOk: "Contabilizează" });
  }));

  // [deficiența 370, comanda Costin 8.2] un audit randat (verdictul păstrat sau cel tocmai rulat) — aceeași formă pentru primul și ultimul
  const htmlAudit = (a, eticheta) => {
    // [lotul 13, deficiența 623, comanda Costin 13.1: „Audit de preluare: același paragraf repetat la fiecare rând”] constatările aceleiași
    // verificări (aceeași etichetă, același temei) stau împreună: fiecare mesaj pe rândul lui, temeiul și remediile o singură dată — și pe
    // auditurile păstrate dinainte (gruparea se face la afișare)
    const grup = (titlu, stare, cls) => {
      const arr = (a.constatari || []).filter((c) => c.stare === stare);
      if (!arr.length) return "";
      const pe = new Map();
      arr.forEach((c) => { const k = (c.eticheta || "") + "\u0000" + (c.temei || ""); if (!pe.has(k)) pe.set(k, []); pe.get(k).push(c); });
      return `<div class="cf-grup-titlu ${cls}">${titlu} (${arr.length})</div>` + [...pe.values()].map((cs) => {
        if (cs.length === 1) return randA(Object.assign({}, cs[0], { stare: stareAfisata(cs[0].stare) }));
        const dot = (CULORI[stareAfisata(stare)] || CULORI.gri).dot;
        const rem = [...new Map(cs.filter((c) => c.remediu).map((c) => [(c.remediu.cauza || "") + "|" + (c.remediu.actiune || ""), c.remediu])).values()];
        return `<div class="cf-incr-rand cf-audit-grup">${cs.map((c) => `<div class="cf-incr-cap"><span class="cf-dot" style="background:${dot}"></span><span>${esc(c.mesaj || "")}</span></div>`).join("")}
          <div class="cf-incr-temei">${esc(cs[0].temei || "")}</div>
          ${rem.map((r) => `<div class="cf-incr-remediu"><b>${esc(r.cauza || "")}</b><br>${esc(r.actiune || "")}</div>`).join("")}</div>`;
      }).join("");
    };
    // [deficiența 220] auditul nu e o restanță: „divergent” e galben și se spune pe nume (eticheta paletei ar fi zis „restanță”)
    const col = CULORI[stareAfisata(a.stare)] || CULORI.gri;
    const txtAudit = a.stare === "rosu" ? "divergent" : col.txt;
    return `<div class="cf-incr-temei">${eticheta}${a.in_iconta_din ? ` · firmă în iConta.eu din ${dataRo(a.in_iconta_din)}` : ""} · rulat ${dataRo(a.data, "cu_ora")} · <span class="cf-dot" style="background:${col.dot}"></span> ${txtAudit} · ${a.coerent} coerent · ${a.divergent} divergent · ${a.neverificat} neverificat</div>
      ${grup("Coerent", "verde", "cf-verde")}
      ${grup("Divergent", "rosu", "cf-galben")}
      ${grup("Neverificat", "gri", "")}
      ${a.limita ? `<div class="cf-incr-temei">${esc(a.limita)}</div>` : ""}`;
  };
  // primul audit (dovada a ce s-a primit de la contabilul anterior) stă lângă ultimul; o rulare nouă nu-l înlocuiește
  async function arataIstoricAudit() {
    const zona = corp.querySelector("#cf-audit-istoric");
    if (!zona) return;
    let ist;
    try { ist = await api.get(`/control-fiscal/${firma.tenant_id}/audit-preluare/istoric`); } catch { return; }
    if (!ist || !ist.primul || !ist.primul.audit) { zona.innerHTML = ""; return; }
    const cine = (x) => x.rulat_de ? ` de ${esc(x.rulat_de)}` : "";
    const titluPrimul = `<b>Primul audit după preluare</b>${cine(ist.primul)} — păstrat: ce s-a primit de la contabilul anterior`;
    zona.innerHTML = ist.ultimul && ist.ultimul.audit
      ? `<div class="cf-audit-ultimul">${htmlAudit(ist.ultimul.audit, `<b>Ultimul audit</b>${cine(ist.ultimul)} (${cate(ist.rulari, "rulare", "rulări")})`)}</div>
         <details class="cf-audit-primul"><summary>${titluPrimul}, ${dataRo(ist.primul.rulat_la, "cu_ora")}</summary>${htmlAudit(ist.primul.audit, "Primul audit")}</details>`
      : `<div class="cf-audit-primul">${htmlAudit(ist.primul.audit, titluPrimul)}</div>`;
    const btn = corp.querySelector("#cf-audit-run");
    if (btn) btn.textContent = "Rerulează auditul";
  }
  async function ruleazaAudit() {
    const btn = corp.querySelector("#cf-audit-run");
    if (btn) { btn.disabled = true; btn.textContent = "Se rulează…"; }
    try {
      // [R45] POST: auditul e un act (butonul de deasupra), iar verdictul lui se pastreaza.
      await api.post(`/control-fiscal/${firma.tenant_id}/audit-preluare`, {});
    } catch (e) {
      if (btn) { btn.disabled = false; btn.textContent = "Rulează auditul de preluare"; }
      arataMesaj(corp.querySelector("#cf-audit-istoric"), `Nu s-a putut rula auditul: ${e.mesaj || e.message}`, "eroare");
      return;
    }
    if (btn) btn.disabled = false;
    await arataIstoricAudit();
  }
  arataIstoricAudit();
  const zonaSpv = corp.querySelector("#cf-spv-stare");   // [deficiența 463] dreptul SPV, cu drumul spre Conectare SPV când lipsește
  if (zonaSpv) randeazaStareSpv(zonaSpv, nav, firma.tenant_id);
  const auditBtn = corp.querySelector("#cf-audit-run");
  if (auditBtn) auditBtn.addEventListener("click", ruleazaAudit);
}
