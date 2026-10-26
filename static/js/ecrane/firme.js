// firme.js — lista de firme a cabinetului (parte din desktop, NU fereastră).
// Click pe o firmă -> aceea se deschide central (fereastra firmei + "În lucru").

import { api, textScurt, dataRo, arataMesaj, aduInVedere, confirmaCaseta, deschideLupa, bani, esc, CULORI_CARD, pct, eroareCamp, curataEroriCamp, semnAjutor, descarca, deschide, cereBlob, dataIso, numarCuSerie, cantitate, pretUnitar, ALEGE, alegeDacaLipseste, selectDaNu, daNu, cereAlegerile, focusFaraSalt, cate, dupaNumar, refuzPeRand, stareNota, pasNota, refuzuriInterne, TEXT_NOTA_INTERNA, atributeInactiv } from "../api.js?v=9bcf50c899";  /* msg_conventie_fe_v1 + generalizare_zi_v1 */
import { htmlCentru, valoareCentru } from "./centre_cost_linie.js?v=d776200e2b";   // [lotul 13, 536] centrul pe salariați și pe mijloace fixe
import { dupaGenerare, butonGenerat, butonDeGenerat, noteGenerate } from "../api.js?v=9bcf50c899";  /* [8c] după generarea unei note — DS cap.6 v2.98 */
import { arataRefuzul, cereCompletate, ultimaCerere, pastreazaCampulActiv } from "../api.js?v=9bcf50c899";  /* [lotul 11, 440] refuzul serverului / câmpurile goale: toate deodată */
// [lotul 11, 440] „Corectează datele” salariatului (PUT /salariati): numele câmpurilor din refuzul serverului (`valideaza_salariat`, corpul
// cererii) -> id-ul de pe ecran, pentru `arataRefuzul`
const CAMPURI_ED_SALARIAT = { nume: "ed-nume", prenume: "ed-pren", cnp: "ed-cnp", data_angajare: "ed-ang", tip_norma: "ed-norma", ore_zi: "ed-orezi",
  nr_cim: "ed-nrcim", data_cim: "ed-datacim", tip_contract: "ed-tipcim", data_nastere: "ed-nastere", copii_scolarizati: "ed-copii",
  functie_baza: "ed-fbaza", declaratie_copii: "ed-declcopii", scutit_contrib_minim: "ed-scutit", motiv_exceptare: "ed-motiv" };   // [C133]
// [front_e; lotul 11, 454: o singură funcție pentru „Salariat nou” și „Corectează datele”] CNP-ul: 13 cifre și cifra de control (cheia
// 279146358279; restul 10 -> 1) — aceeași regulă ca pe server (`core.identitate.valideaza_cnp`), ca eroarea să apară înainte de salvare
// [lotul 12, C198 — clasa 216/333] luna în curs (sau una viitoare) nu s-a încheiat: serverul refuză notele care închid luna
// (`uc_comun._cere_luna_incheiata`, regula `inchidere_luna.luna_in_curs`); butoanele lor nu se oferă ca să fie refuzate, ci stau inactive,
// cu motivul lângă ele. O singură definiție pentru amortizare și descărcarea gestiunii.
function lunaNeincheiata(an, luna) {
  const azi = new Date();
  return an * 12 + luna >= azi.getFullYear() * 12 + azi.getMonth() + 1;
}

// [C198] motivul de lângă butoanele descărcării gestiunii pe luna în curs (refuzul serverului spune același lucru, cu data de azi)
const MOTIV_DESCARCARE_LUNA_IN_CURS = "Descărcarea gestiunii lunii se face după ce luna se încheie.";

function cnpValid(c) {
  if (!/^\d{13}$/.test(c)) return false;
  const w = [2,7,9,1,4,6,3,5,8,2,7,9]; let sm = 0;
  for (let i = 0; i < 12; i++) sm += (+c[i]) * w[i];
  let ctrl = sm % 11; if (ctrl === 10) ctrl = 1;
  return ctrl === (+c[12]);
}
import { sesiune } from "../sesiune.js?v=898215e0ee";
import { permis } from "../drepturi.js?v=34d0fb0afd";
import { ciornaFormular } from "../ciorna_formular.js?v=461bec469f";  /* [267, clasa] ciorna formularelor lungi de creare */  /* [drepturi_rol 04.10.2026] acțiunile a căror rută depinde de stare */
import { fluxConcediu } from "./flux_concediu.js?v=e7e0501a77";  /* cm_flux_v1 */
import { sumaRo } from "./sal_sume.js?v=cd0be29c82";  /* [lotul 13, 655] suma scrisă de om, prin `numarRo` */
import { MESAJ_NUMAR_RO } from "../api.js?v=9bcf50c899";  /* [lotul 13, 655] (`atributeInactiv`, 675, vine din importul de sus) */
import { randeazaStareSpv } from "./spv_stare.js?v=228cdfcde1";  /* [lotul 6: 273, 275, 289] */
import { randeazaFacturi, cereSeriaChitanteiPeLoc } from "./facturi_ecran.js?v=c0a800d25f";   // [lotul 13, 543] seria chitanțelor pe loc
import { cautaInLista } from "./emitere_ecran.js?v=5b93aa95d0";   /* [lotul 12, 488] căutarea în listele lungi de articole */
import { ecranRip } from "./rip_ecran.js?v=b9fdb13bcc";
import { trimiteInCoada, casetaTrimisa, etichetaTrimitere, motivInFraza } from "./coada_trimite.js?v=6f3dd3794d";  /* [C11, 07.10.2026] bilanțul prin coadă */
import { ecranOperatiuni } from "./operatiuni_ecran.js?v=54dc44fa27";
import { ecranBorderou } from "./borderou_ecran.js?v=6c00f2b8cf";   /* [lotul 11, 450 / pct.23] borderoul de achiziție, lângă NIR */
import { ecranEtransport } from "./etransport_ecran.js?v=d8c78d67e3";
import { meniuMigrarePerFirma, randeazaMigrare, randeazaPreluareFirma } from "./migrare.js?v=f6b23a2d2a";  // [p96_import_firma] + [Q4] import in masa
import { declaratiiPerFirma } from "./declaratii.js?v=b22d32280e";  // [decl_firma_v1]
import { CULORI as CULORI_VERDICT, etichetaStare, randeazaCorpVerdict, legaVerdict } from "./control_verdict.js?v=3dc9eca249";  // renderer unic verdict control fiscal (DS cap.20)
import { randeazaProduse } from "./produse_ecran.js?v=862d71a030";  // [produse_firma_v1]
import { ecranMagazin } from "./woo_ecran.js?v=885f441ff4";  // [wc_extras_v1]
import { randeazaDateFirma } from "./date_firma.js?v=499702a340";  // [date_firma_v1]
import { ecranMijloace } from "./mijloace_ecran.js?v=891835ddea";  // [ecran_mf_v1]
import { ecranReevaluareValuta } from "./reevaluare_ecran.js?v=bf9065cbb3";  // [lotul 10, 429]
import { ecranCompensari } from "./compensari_ecran.js?v=ed3e73a2f0";  // [lotul 10, 428 — decizia Costin „Construiesc acum”]
import { ecranClienti, ecranFurnizori, ecranParteneriFirmei } from "./clienti_ecran.js?v=91f9fce823";  // [lotul 10, 428 — decizia Costin „Bifă pe client”]; [lotul 11] furnizorii
import { propuneNumeAnaf } from "./nume_anaf.js?v=d59cd56b02";
import { legaDateAnaf } from "./date_anaf.js?v=503d474ed1";  // [lotul 12, 459.1] datele aduse de la ANAF țin de CUI-ul lor
import { htmlTabelNote, legaTabelNote, htmlCautare, textNumar, rulajLinii, locInDetaliu } from "./tabel_note.js?v=1ba09ef3b2";  // [lotul 12, 617 / 622] tabelul comun de note  // [lotul 11, 444] numele de la ANAF față de fișa partenerului (NIR, casă)

// randează lista în containerul dat; `inapoi()` revine la panoul cu carduri
export function randeazaListaFirme(container, nav, inapoi) {
  container.innerHTML = `
    <div class="firme-cap">
      <span class="firme-spatiu"></span>
      <button class="buton-secundar" id="firme-import-masa" data-actiune="POST /migrare/importa">Import în masă (CSV)</button>
      <button class="buton-primar" id="firme-adauga" data-actiune="POST /tenants">+ Adaugă firmă</button>
    </div>
    <p class="ecran-nota" data-actiune="POST /tenants/{tenant_id}/activare|DELETE /tenants/{tenant_id}" style="margin:0 0 10px">Butonul <strong>Scoate</strong> de pe fiecare rând
       deschide o previzualizare, nu șterge. Acolo se vede care act e care:
       <strong>dezactivarea</strong> e reversibilă (firma iese din listă, datele rămân),
       <strong>ștergerea</strong> nu e — și se poate doar dacă firma n-a produs niciun document.</p>
    <div class="firme-cautare">
      <label class="camp-eticheta" for="firme-q">Caut\u0103</label>
      <input type="text" id="firme-q" class="camp-input" placeholder="Caută după nume sau CUI" autocomplete="off">
    </div>
    <div class="firme-lista" id="firme-lista"><div class="ecran-nota">Se încarcă firmele…</div></div>
    <div id="firme-dezactivate"></div>
  `;

  container.querySelector("#firme-import-masa")?.addEventListener("click", () =>
    nav.deschide("Migrare cabinet", (c) => randeazaMigrare(c, nav), { nivel: "cabinet" }));

  container.querySelector("#firme-adauga").addEventListener("click", () => {
    nav.deschide("Adaugă firmă", (corp) => {  /* firma_noua_v1 */
      corp.innerHTML = `
        <div class="camp" style="margin-bottom:14px">
          <label for="fn-cui" class="camp-eticheta">CUI</label>
          <input class="camp-input" id="fn-cui" placeholder="RO12345678 sau 12345678" autocomplete="off">
          <p class="ecran-nota" id="fn-cui-info" style="margin:6px 0 0"></p>
        </div>
        <div class="camp" style="margin-bottom:14px">
          <label for="fn-nume" class="camp-eticheta">Denumire firmă</label>
          <input class="camp-input" id="fn-nume" placeholder="Se completează automat de la ANAF">
        </div>
        <div class="camp" style="margin-bottom:14px">
          <label for="fn-tip" class="camp-eticheta">Tip firmă</label>
          <select class="camp-input" id="fn-tip" data-butoane>${ALEGE}
            <option value="srl">SRL / SA (partidă dublă)</option>
            <option value="pfa">PFA / II / IF / profesii liberale (partidă simplă)</option>
          </select>
          <p class="camp-ajutor">Tipul <strong>nu se mai poate schimba</strong> după creare: determină sistemul contabil (partidă dublă sau simplă) și, odată introduse date, acestea nu pot fi mutate în celălalt regim. Verifică înainte de a continua.</p>
        </div>
        <div class="camp" style="margin-bottom:14px">
          <label for="fn-email" class="camp-eticheta">Email client (primește automat acces la portal)</label>
          <input class="camp-input" id="fn-email" type="email" placeholder="Opțional: emailul patronului — primește acces în portal" autocomplete="off">
        </div>
        <button class="buton-primar" id="fn-salveaza" data-actiune="POST /tenants|POST /tenants/{tenant_id}/client-acces" disabled>Adaugă firma</button>
        <p id="fn-msg" role="alert" style="margin:8px 0 0"></p>
      `;
      const cui = corp.querySelector("#fn-cui"), nume = corp.querySelector("#fn-nume");
      const info = corp.querySelector("#fn-cui-info"), btn = corp.querySelector("#fn-salveaza");
      let t = null, cuiGresit = false, anaf = legaDateAnaf(cui, [nume]);   // [F188 + lotul 12, 459.1] `date_anaf.js` (ca la NIR și casă)
      const cerereCui = ultimaCerere();   // [C103] CUI-ul tastat în șir: numai răspunsul ANAF pentru CUI-ul din câmp ajunge sub el
      // [459] CUI-ul pleacă așa cum e scris (serverul scoate „RO” și spațiile): o literă sau o cratimă nu mai dispar tacit în cifre
      const cuiScris = () => cui.value.trim();
      cui.addEventListener("input", () => {
        const actuala = cerereCui();   // orice tastare scoate din joc răspunsul cererii de dinainte (și când CUI-ul scade sub 6 cifre)
        clearTimeout(t); btn.disabled = true; info.textContent = ""; cuiGresit = false;
        curataEroriCamp(cui.closest(".camp"));
        const v = cui.value.replace(/\D/g, "");
        if (v.length < 6) return;
        t = setTimeout(async () => {  /* debounce 500ms: un apel per CUI, nu pe fiecare tasta (rate limit ANAF) */
          info.textContent = "Verific la ANAF...";
          try {
            const r = await api.get("/public/verifica-cui/" + encodeURIComponent(cuiScris()));
            if (!actuala()) return;
            if (r && r.cui_invalid) {
              // [459, comanda Costin 11.3 pct.5] CUI-ul greșit (cifra de control) se spune lângă câmp, înainte de orice scriere; „Adaugă
              // firma” rămâne inactiv până la un CUI valabil (serverul îl refuză oricum, pe același motiv)
              info.textContent = ""; cuiGresit = true;
              eroareCamp(corp, "fn-cui", r.motiv);
            } else if (r && r.gasit) {
              // [F188] SUGEREAZA, nu suprascrie orb: completeaza doar daca campul e gol sau neatins de user
              // de la ultima pre-completare ANAF (userul poate corecta datele stale ANAF fara sa i se piarda).
              anaf.pune([r.denumire]);   // [459.1] fără „— verifică.”: rândul spune ce a dat ANAF și ce se preia la creare
              info.textContent = "Din ANAF: " + r.denumire + ". La creare se preiau și adresa, localitatea, județul, codul CAEN, numărul de la Registrul Comerțului și înregistrarea în scopuri de TVA.";
              btn.disabled = false;
            } else { info.textContent = "CUI negăsit la ANAF. Poți completa denumirea manual."; btn.disabled = false; }
          } catch (e) {
            if (!actuala()) return;
            info.textContent = "Nu s-a putut verifica la ANAF acum. Completează denumirea manual.";
            btn.disabled = false;
          }
        }, 500);
      });
      nume.addEventListener("input", () => { if (!cuiGresit && nume.value.trim().length > 2 && cui.value.replace(/\D/g,"").length >= 6) btn.disabled = false; });
      btn.addEventListener("click", async () => {
        const emailCl = corp.querySelector("#fn-email").value.trim();  /* firma_email_optional_v1 */
        // [comanda Costin 04.10.2026 pct.1] Refuzul se vede LÂNGĂ buton (#fn-msg, stil de eroare) și pe câmpul vinovat.
        // Până azi cădea în rândul gri de sub CUI (`#fn-cui-info`), la 333 px deasupra butonului: „nu se întâmplă nimic”.
        const msg = corp.querySelector("#fn-msg");
        curataEroriCamp(corp); arataMesaj(msg, "", "info");
        // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite; [lotul 11, 440] alegerea și emailul greșit se arată deodată
        let lipsa = false; if (cereAlegerile(corp, ["#fn-tip"])) lipsa = true;
        if (emailCl && !emailCl.includes("@")) { eroareCamp(corp, "fn-email", "Emailul nu pare valid. Lasă gol dacă nu inviți pe nimeni acum."); lipsa = true; }
        if (lipsa) return;
        btn.disabled = true; btn.textContent = "Se creează...";
        let rT = null;
        try {
          // [pct.3] emailul pleacă ÎMPREUNĂ cu firma: serverul îl judecă înainte de creare (adresă cu alt rol -> refuz pe câmp)
          rT = await api.post("/tenants", { nume: nume.value.trim(), cui: cuiScris(), tip_firma: corp.querySelector("#fn-tip").value,  /* [tip_firma_v1] [459] */
                                            email_client: emailCl || null });
          if (emailCl) await api.post(`/tenants/${rT.tenant_id}/client-acces`, { email: emailCl, nume: "" });
          /* [26.08.2026] Crearea SE CONFIRMA. Pana azi formularul se inchidea in tacere, iar
             omul nu putea sti daca a mers — deci apasa din nou. A doua apasare era refuzata
             corect de poarta de CUI duplicat, iar refuzul ARATA ca si cum ar fi fost ignorat:
             firma exista deja, fiindca prima apasare o crease. Cauza n-a fost poarta, ci
             tacerea de dupa succes. Exercitat pe date 26.08: doua firme create in 4 minute. */
          nav.inapoi();
          await incarcaFirme();   /* [27.08.2026] era `incarca()` — nedefinita in scopul asta */
          _bannerFirmaCreata(nume.value.trim());
        } catch (e) {
          const CAMP = { email_client: "fn-email", email: "fn-email", cui: "fn-cui", nume: "fn-nume" };
          // [lotul 11, 440] fiecare eroare lângă câmpul ei (`arataRefuzul`); sub buton, ce s-a întâmplat și textul fiecărei erori (nu
          // „câmpul marcat mai sus”). Firma creată + invitația refuzată: se spune EXACT asta — altfel omul apasă din nou și lovește
          // CUI-ul duplicat.
          const peCamp = arataRefuzul(corp, e, null, { campuri: CAMP });
          const motiv = e.mesaj || e.message || "eroare";
          const texte = (e.erori_campuri || []).map((c) => c.mesaj).filter(Boolean);
          arataMesaj(msg, rT ? "Firma a fost creată, dar accesul clientului n-a plecat: " + motiv + " Îl poți da din firmă › Acces client."
                             : (peCamp ? "Firma nu s-a creat: " + texte.join(" ") : (e.mesaj || e.message || "Eroare la creare.")), "eroare");
          btn.disabled = false; btn.textContent = "Adaugă firma";
        }
      });
    });
  });

  const lista = container.querySelector("#firme-lista");
  const cautare = container.querySelector("#firme-q");
  const zonaDez = container.querySelector("#firme-dezactivate");
  let toate = [], dezactivate = [], scoase = [];

  function deseneaza(filtru) {
    const f = (filtru || "").trim().toLowerCase();
    const vizibile = toate.filter((t) =>
      !f || (t.nume || "").toLowerCase().includes(f) || String(t.cui || "").includes(f)
    );
    if (toate.length === 0) {
      lista.innerHTML = `<div class="firme-gol">Nicio firmă încă. Adaugă prima firmă din portofoliu.</div>`;
      return;
    }
    if (vizibile.length === 0) {
      lista.innerHTML = `<div class="firme-gol">Nicio firmă nu se potrivește cu „${filtru}".</div>`;
      return;
    }
    lista.innerHTML = "";
    vizibile.forEach((t) => {
      // [R78, 27.08.2026] Decizia de a scoate o firmă se ia UNDE VEZI PORTOFOLIUL, nu după ce
      // intri în firmă și derulezi 26 de carduri de lucru. Măsurat înainte: butonul de dinainte
      // stătea la 1361 px într-o fereastră de 793 — exista, dar nu se găsea.
      // Un <button> nu poate conține alt <button>. Iar `button.firme-rand` e selectorul pe care
      // stau 36 de fișiere (`w_auth` și toată infra vizuală), deci randul RĂMÂNE buton: acțiunea
      // se așază lângă el, într-un înveliș. Se schimbă împrejurimea, nu rândul.
      const linie = document.createElement("div");
      linie.className = "firme-rand-linie";
      const deschide = document.createElement("button");
      deschide.className = "firme-rand";
      deschide.innerHTML = `
        <div class="firme-rand-text">
          <div class="firme-rand-nume">${esc(t.nume) || "(fără nume)"}</div>
          <div class="firme-rand-cui">CUI ${esc(String(t.cui || "—"))}</div>
        </div>
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#9aa3af" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>
      `;
      deschide.addEventListener("click", () => deschideFirma(t, nav));
      const scoate = document.createElement("button");
      scoate.className = "buton-secundar firme-rand-scoate";
      scoate.dataset.actiune = "POST /tenants/{tenant_id}/activare|DELETE /tenants/{tenant_id}";  // [drepturi_rol] doar administratorul
      scoate.textContent = "Scoate";
      scoate.title = "Scoate firma din portofoliu — se deschide o previzualizare, nu se șterge de aici";
      // NU șterge de aici: un act ireversibil la un click de listă e prea aproape. Deschide
      // ACELAȘI ecran de previzualizare, cu confirmarea pe CUI.
      scoate.addEventListener("click", (ev) => {
        ev.stopPropagation();
        nav.deschide("Scoate firma", (c2) => ecranScoateFirma(c2, nav, t));
      });
      linie.appendChild(deschide);
      linie.appendChild(scoate);
      lista.appendChild(linie);
    });
  }

  cautare.addEventListener("input", () => deseneaza(cautare.value));

  // [R72] O firmă cu evidență nu se șterge — se dezactivează. Dacă ar ieși din listă fără nicio
  // cale de întoarcere, dezactivarea ar fi o ușă cu sens unic. De aceea lista se cere cu
  // `inactive=true` și se desparte aici: portofoliul de lucru sus, cele scoase din lucru jos.
  async function incarcaFirme() {
    try {
      const r = await api.get("/tenants?inactive=true");
      const lst = (r && r.tenants) || [];
      toate = lst.filter((t) => t.activ !== false);
      dezactivate = lst.filter((t) => t.activ === false);
    } catch {
      lista.innerHTML = `<div class="firme-gol">Firmele nu au putut fi încărcate.</div>`;
      return;
    }
    // [drepturi_rol] istoricul scoaterilor e al întregului cabinet -> doar administratorul (nu se mai cere, ca să fie refuzat)
    try { scoase = permis("GET /firme-scoase") ? (((await api.get("/firme-scoase")) || {}).firme || []) : []; } catch { scoase = []; }
    deseneaza(cautare.value);
    deseneazaDezactivate();
  }

  function deseneazaDezactivate() {
    if (!zonaDez) return;
    // [lotul 13, 675] cele două butoane stau mereu la locul lor; fără firme, inactive, cu motivul (DS cap.1 v2.104)
    zonaDez.innerHTML = `
      <div class="firme-cap" style="margin-top:18px">
        <span class="firme-spatiu"></span>
        <button class="buton-secundar" id="firme-vezi-dez" data-actiune="POST /tenants/{tenant_id}/activare"${dezactivate.length ? "" : atributeInactiv("Nicio firmă dezactivată.")}>Firme dezactivate (${dezactivate.length})</button>
        <button class="buton-secundar" id="firme-vezi-scoase" data-actiune="GET /firme-scoase"${scoase.length ? "" : atributeInactiv("Nicio firmă scoasă din portofoliu.")}>Firme scoase (${scoase.length})</button>
      </div>`;
    // [27.08.2026] O urmă pe care n-o poate deschide nimeni fără `psql` nu e urmă pentru cabinet,
    // e urmă pentru administratorul serverului. (Costin) După o ștergere, asta e singura dovadă
    // că firma a existat.
    zonaDez.querySelector("#firme-vezi-scoase")?.addEventListener("click", () =>
      nav.deschide("Firme scoase", (c3) => randeazaFirmeScoase(c3, scoase)));
    zonaDez.querySelector("#firme-vezi-dez")?.addEventListener("click", () =>
      nav.deschide("Firme dezactivate", (c2) => {
        c2.innerHTML = `
          <p class="ecran-nota">Firmele de aici nu apar în portofoliul de lucru. Documentele lor
             au rămas neatinse; reactivarea le aduce înapoi exact cum erau.</p>
          <div class="firme-lista" id="fd-lista"></div>
          <div id="fd-mesaj"></div>`;
        const zl = c2.querySelector("#fd-lista"), zm = c2.querySelector("#fd-mesaj");
        zl.innerHTML = "";
        dezactivate.forEach((t) => {
          const rand = document.createElement("div");
          rand.className = "firme-rand";
          rand.innerHTML = `
            <div class="firme-rand-text">
              <div class="firme-rand-nume">${esc(t.nume) || "(fără nume)"}</div>
              <div class="firme-rand-cui">CUI ${esc(String(t.cui || "—"))}</div>
            </div>`;
          const b = document.createElement("button");
          b.className = "buton-secundar";
          b.textContent = "Reactivează";
          b.dataset.actiune = "POST /tenants/{tenant_id}/activare";  // [deficiența 262, clasa] doar administratorul
          b.addEventListener("click", async () => {
            b.disabled = true;
            try {
              await api.post(`/tenants/${t.id}/activare`, { activ: true });
              await incarcaFirme();
              nav.inapoi();
              // [GG, 28.08.2026] Aici era un `arataMesaj(zm, …)` ÎNAINTE de `nav.inapoi()` — adică
              // mesajul se scria în `#fd-mesaj`, o zonă din fereastra pe care rândul următor o
              // închide. Confirmarea exista o fracțiune de secundă și murea cu fereastra.
              //
              // Gardul E2 o vedea drept confirmată: `arataMesaj` chiar e chemat, în blocul `try`.
              // Iar eu am scris, în docstringul gardului, că „ecranul ei NU se demontează înainte de
              // mesaj" — **fals**, scris din citirea celeilalte ramuri. A prins-o proba pe ecran, nu
              // recitirea: aștepta `.msg-ok` și nu-l găsea niciodată.
              //
              // E chiar clasa lui R82, ascunsă în spatele unui apel care PARE o confirmare.
              _bannerFirma(`<b>${esc(t.nume || "Firma")}</b> e din nou în portofoliu, în starea de
                 dinainte. O găsești în listă.`);
            } catch (e) {
              b.disabled = false;
              arataMesaj(zm, e.mesaj || e.message || "Nu s-a putut reactiva firma.", "eroare");
            }
          });
          rand.appendChild(b);
          zl.appendChild(rand);
        });
      }));
  }

  incarcaFirme();
}

// [nume_anaf_v1, 27.08.2026] Denumirea din aplicație lângă cea de la ANAF.
// Decizia lui Costin, varianta (b): numele rămâne EDITABIL, dar instantaneul ANAF se păstrează cu
// data lui, iar divergența se ARATĂ. Varianta (a) — câmp needitabil — ar fi blocat firmele pe care
// ANAF nu le întoarce: „un câmp needitabil care nu se poate completa e mai rău decât unul editabil
// greșit."
// Precedentul e în aceeași aplicație: `platitor_tva` lângă `platitor_tva_anaf` + data lui.
const _NUME_ANAF_ZILE_STATUT = 180;

function _numeNrm(s) {
  return String(s || "").trim().replace(/\s+/g, " ").toLocaleLowerCase("ro");
}

// -> null (nimic de arătat) | {fel: "divergenta"|"veche", anaf, zile}
function _divergentaNume(t) {
  const anaf = (t && t.nume_anaf) || "";
  if (!anaf || !_numeNrm(anaf) || _numeNrm(anaf) === _numeNrm(t.nume)) return null;
  // [R77] Dacă întrebarea a primit deja răspuns, nu se mai pune — până când ANAF spune altceva.
  // O citire ANAF mai NOUĂ decât alegerea o redeschide: alegerea de azi nu acoperă o denumire
  // schimbată la registru mâine.
  if (t.nume_ales_la) {
    const ales = new Date(t.nume_ales_la), citit = t.nume_anaf_la ? new Date(t.nume_anaf_la) : null;
    if (!citit || isNaN(citit) || citit <= ales) return null;
  }
  // `nume_anaf_la` decide când e stătut: „o denumire ANAF veche de un an nu e divergență, e o
  // măsurătoare veche" (Costin). Fără dată, nu se poate spune — și atunci se spune asta.
  const la = t.nume_anaf_la ? new Date(t.nume_anaf_la) : null;
  const zile = la && !isNaN(la) ? Math.floor((Date.now() - la.getTime()) / 864e5) : null;
  return { fel: (zile === null || zile <= _NUME_ANAF_ZILE_STATUT) ? "divergenta" : "veche",
           anaf, zile };
}

function _randDivergentaNume(corp, nav, t) {
  const d = _divergentaNume(t);
  if (!d) return;
  const zona = document.createElement("div");
  if (d.fel === "veche") {
    zona.className = "caseta-info";
    zona.innerHTML = `<p style="margin:0">Ultima denumire văzută la ANAF era
      <strong>${esc(d.anaf)}</strong>, dar măsurătoarea are ${cate(d.zile, "zi", "zile")} —<strong>nu e o
      divergență, e o citire veche</strong>. Se reîmprospătează la următoarea verificare de CUI.</p>`;
  } else {
    // [R77, 27.08.2026] AMÂNDOUĂ butoanele, niciunul implicit. Costin: „«a păstra pe a ta = a nu
    // face nimic» nu e o alegere. Cine nu apasă nimic nu decide — moștenește ce era acolo, și nu
    // află niciodată că a fost o divergență." Deci și „păstrez denumirea mea" e un act care scrie.
    zona.className = "caseta-atentie";
    // [Q1/Q2, 28.08.2026 — R81 DECISĂ: simetrie de scriere] Textul a trecut azi prin două forme, și
    // amândouă erau adevărate când s-au scris. Ieri: „alegerea schimbă numai eticheta din
    // portofoliu" — fiindcă ramura `anaf` chiar atingea un singur loc din două. Azi: denumirea
    // firmei e UNA, scrisă în amândouă locurile în aceeași tranzacție (`scrie_denumirea`), deci
    // formularea simplă redevine adevărată — **structural**, nu doar azi.
    //
    // MARCAJUL E1 RĂMÂNE, și nu ca decor: e plasa de siguranță cerută explicit („nu te baza orb pe
    // invariant"). Un invariant e o afirmație despre codul de azi; scrierile din afara aplicației —
    // semănătoare, importuri, SQL de mână — nu trec prin scriitorul unic. Dacă cele două valori
    // ajung vreodată să difere, confruntarea trebuie să REAPARĂ, nu să rămână ascunsă în spatele
    // unui text care presupune sincronia. `data-e1-absent="fiscal"` rămâne fiindcă lista tot nu
    // CITEȘTE `firma_profil.nume`: ecranul afirmă egalitatea prin construcție, n-o verifică. Cine o
    // verifică la rulare e „Date firmă", care are amândouă valorile și le compară la fiecare
    // randare.
    zona.innerHTML = `
      <div class="ca-mesaj" data-e1="denumire-firma"><strong>Două denumiri, și trebuie aleasă
        una.</strong> Denumirea firmei diferă de cea de la ANAF${
        d.zile !== null ? ` (${d.zile === 0 ? "citită azi" : "citită acum " + cate(d.zile, "zi", "zile")})` : ""}:
        <br>· în aplicație: <strong data-e1-sursa="portofoliu">${esc(t.nume || "")}</strong>
        <br>· la ANAF: <strong>${esc(d.anaf)}</strong>
        <br><span data-e1-efect="fiscal" data-e1-absent="fiscal">Denumirea aplicată e cea de pe
        documente: o firmă are <strong>o singură denumire</strong> — aceeași în listă, în bara de
        sus și pe declarații.</span>
        <br>· <strong>„Ia denumirea de la ANAF"</strong> schimbă denumirea firmei peste tot,
        <strong>inclusiv pe declarații și pe bilanț</strong>.
        <br>· <strong>„Păstrez denumirea mea"</strong> nu schimbă nimic — consemnează că ai ales
        deliberat.
        <br>Alegerea se consemnează — dacă ANAF va spune altceva mai târziu, întrebarea se pune din
        nou.</div>
      <div class="ca-actiuni">
        <button class="buton-secundar" id="dn-ia-anaf" data-actiune="POST /tenants/{tenant_id}/nume-ales">Ia denumirea de la ANAF</button>
        <button class="buton-secundar" id="dn-pastrez" data-actiune="POST /tenants/{tenant_id}/nume-ales">Păstrez denumirea mea</button>
      </div>`;
  }
  corp.insertBefore(zona, corp.children[1] || null);

  const alege = async (id, alegere, textLucru, textInapoi) => {
    const b = zona.querySelector(id);
    if (!b) return;
    b.addEventListener("click", async () => {
      zona.querySelectorAll("button").forEach((x) => { x.disabled = true; });
      b.textContent = textLucru;
      try {
        await api.post(`/tenants/${t.id}/nume-ales`, { alege: alegere });
        // [R82/AA1] Actul ăsta a fost apăsat de un om pe 27.08 la 19:16:24, iar ecranul n-a spus
        // nimic: caseta a dispărut fiindcă `nav.acasa()` demontează tot. Confirmarea numește
        // entitatea ȘI consecința, și e diferită pe cele două ramuri, fiindcă fac lucruri diferite.
        const _den = alegere === "anaf" ? (d.anaf || "") : (t.nume || "");
        nav.acasa();
        nav.setFirmaInLucru("");
        _bannerFirma(alegere === "anaf"
          ? `Denumirea firmei e acum <b>${esc(_den)}</b>, cea de la ANAF. Se folosește peste tot —
             în listă, în bara de sus și pe declarații.`
          : `<b>${esc(_den)}</b> rămâne denumirea firmei. Alegerea a fost consemnată, cu data și
             autorul ei; întrebarea nu se mai pune până când ANAF spune altceva.`);
      } catch (e) {
        zona.querySelectorAll("button").forEach((x) => { x.disabled = false; });
        b.textContent = textInapoi;
        const m = document.createElement("p");
        m.className = "msg-eroare";
        m.textContent = e.mesaj || e.message || "Nu s-a putut consemna alegerea.";
        zona.appendChild(m);
      }
    });
  };
  alege("#dn-ia-anaf", "anaf", "Se schimbă…", "Ia denumirea de la ANAF");
  alege("#dn-pastrez", "aplicatie", "Se consemnează…", "Păstrez denumirea mea");
}

// deschide o firmă: setează "În lucru" + spațiul de lucru (meniu de acțiuni)
export function deschideFirma(t, nav) {   // [P2] reutilizat din termene.js — deschide fisa firmei
  // [deficiența 320] asistentul a deschis una dintre firmele lui: cardul de început „Firmele tale și ce ai voie să faci” e făcut (în
  // ecranul real, nu la apăsarea cardului); o singură dată, fără să aștepte răspunsul
  if (sesiune.rol() === "angajat" && !deschideFirma._vazut) { deschideFirma._vazut = true; api.post("/eu/inceput/firme-vazute", {}).catch(() => {}); }
  nav.setFirmaInLucru(t.nume || "", t.id);
  nav.deschide((t.nume || "Firmă") + " \u00b7 CUI " + (t.cui || ""), (corp) => meniuFirma(corp, nav, t), { lat: "larg" });
}

// meniul de acțiuni pe o firmă (facturi activ; restul se activează pe rând)
// [05.10.2026, comanda Costin pct.11] Grupurile ferestrei firmei — SURSA UNICĂ. Fiecare card din `meniuFirma` declară `grup`
// (cheie de aici); ordinea titlurilor e ordinea de aici; un titlu fără niciun card vizibil nu apare. Fără arbore: titlu + carduri.
// DS cap.18 (v2.71) + verificator `GRUP_FIRMA`.
export const GRUPURI_FIRMA = [
  ["zilnic", "Zilnic"],
  ["registre", "Registre"],
  ["raportari", "Raportări și declarații"],
  ["speciale", "Operațiuni speciale"],
  ["firma", "Firma"],
];

// Cardurile vizibile, pe grupuri, în ordinea din GRUPURI_FIRMA; grupurile fără niciun card vizibil nu apar.
export function grupeazaCarduri(vizibile) {
  return GRUPURI_FIRMA.map(([g, titlu]) => [g, titlu, vizibile.filter((o) => o.grup === g)]).filter(([, , c]) => c.length);
}

function meniuFirma(corp, nav, t) {
  const optiuni = [
    { cheie: "facturi", regim: "ambele", grup: "zilnic", titlu: "Facturi", desc: "Emite și vezi facturile firmei",
      ...CULORI_CARD.albastru,
      icon: '<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 13h6M9 17h4"/>', activ: true },
    { cheie: "produse", regim: "ambele", grup: "firma", titlu: "Produse", desc: "Nomenclator cu cote TVA, potrivire AI",
      ...CULORI_CARD.teal,   // [05.10.2026] lipsea: iconița ieșea pe fundal „undefined” (DS cap.12)
      icon: '<path d="M21 8l-9-5-9 5 9 5 9-5z"/><path d="M3 8v8l9 5 9-5V8"/><path d="M12 13v8"/>', activ: true },  // [produse_firma_v1]
    // [lotul 13, deficiența 577, comanda Costin 13.1: „F4 PFA: cardurile au descrieri de SRL — Declarații «D101», Verificări «Echilibru»,
    // Registrul de evidență fiscală «Profit · art. 19»”] la partida simplă cardul spune ce are PFA-ul (`descSimpla`): D101 / D100 / D406 nu se
    // aplică formei (`control_fiscal_api.neaplicabile_forma`), D212 e declarația lui
    { cheie: "declaratii", regim: "ambele", grup: "raportari", titlu: "Declarații", desc: "D112, D300, D101 și restul",
      descSimpla: "D212 (declarația unică), D300, D112 și restul",
      ...CULORI_CARD.verde,
      icon: '<path d="M9 13h6M9 17h4M9 9h1"/><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/>', activ: true },
    { cheie: "control", regim: "ambele", grup: "raportari", titlu: "Control fiscal", desc: "Semafor conformare pe firmă",
      ...CULORI_CARD.teal,
      icon: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>', activ: true },
    { cheie: "salariati", regim: "ambele", grup: "zilnic", titlu: "Salariați", desc: "Stat plată, fluturași, D112",
      ...CULORI_CARD.piersica,
      icon: '<circle cx="9" cy="7" r="3"/><path d="M2 21v-1a6 6 0 0 1 12 0v1"/><path d="M16 3.5a3 3 0 0 1 0 7M22 21v-1a6 6 0 0 0-4-5.7"/>', activ: true },
    { cheie: "bonuri", regim: "ambele", grup: "zilnic", titlu: "Bonuri și chitanțe", desc: "Pozate de client \u2014 certifică și contează",
      ...CULORI_CARD.piersica,
      icon: '<path d="M9 11l3 3 8-8"/><path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>', activ: true },
    { cheie: "jurnal", regim: "dubla", grup: "registre", titlu: "Registru jurnal", desc: "Notele contabile ale firmei",
      ...CULORI_CARD.ardezie,
      icon: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>', activ: true },
    // [368, lotul 9] la PFA nu există note contabile: Z-ul intră în registrul de încasări și plăți (`descSimpla`)
    { cheie: "raportz", regim: "ambele", grup: "zilnic", titlu: "Raport Z", desc: "Încasări zilnice \u2192 notă automată",
      descSimpla: "Încasări zilnice \u2192 registrul de încasări și plăți",
      ...CULORI_CARD.chihlimbar,
      icon: '<path d="M4 4h16M4 4l16 16M4 20h16"/>', activ: true },
    { cheie: "stocuri", regim: "dubla", grup: "zilnic", titlu: "Stocuri", desc: "NIR, adaos, desc\u0103rcare gestiune",
      ...CULORI_CARD.chihlimbar,
      icon: '<path d="M21 8l-9-5-9 5v8l9 5 9-5V8z"/><path d="M3 8l9 5 9-5M12 13v8"/>', activ: true },
    // [08.10.2026, decizia Costin U3] „Închidere lună”: card separat, în grupul Zilnic
    { cheie: "inchidere", regim: "ambele", grup: "zilnic", titlu: "\u00cenchidere lun\u0103", desc: "Blocarea perioadei \u0219i \u00eenchiderea eviden\u021bei facturilor",
      ...CULORI_CARD.teal,
      icon: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>', activ: true },
    { cheie: "fisacont", regim: "dubla", grup: "registre", titlu: "Cartea mare", desc: "Fi\u0219\u0103 de cont 14-6-22, pe cont \u0219i perioad\u0103",
      ...CULORI_CARD.ardezie,
      icon: '<path d="M4 4h16v16H4z"/><path d="M4 9h16"/><path d="M9 4v16"/>', activ: true },
    { cheie: "marja", regim: "dubla", grup: "speciale", titlu: "Jurnal regim marj\u0103", desc: "Art. 312 second-hand \u00b7 art. 311 turism",
      ...CULORI_CARD.piersica,
      icon: '<path d="M3 6h18"/><path d="M7 12h10"/><path d="M10 18h4"/>', activ: true },
    { cheie: "regfiscal", regim: "ambele", grup: "registre", titlu: "Registrul de eviden\u021b\u0103 fiscal\u0103", desc: "Profit \u00b7 art. 19 \u00b7 persoane fizice \u00b7 art. 68",
      descSimpla: "Venituri și cheltuieli · persoane fizice · art. 68",   // [577]
      ...CULORI_CARD.albastru,
      icon: '<path d="M4 3h16v18H4z"/><path d="M8 8h8M8 12h8M8 16h4"/>', activ: true },
    { cheie: "reginventar", regim: "dubla", grup: "registre", titlu: "Registrul-inventar", desc: "Cod 14-1-2 \u00b7 rezultatele inventarierii",
      ...CULORI_CARD.ardezie,
      icon: '<path d="M9 2h6v4H9z"/><rect x="4" y="6" width="16" height="16" rx="2"/><path d="M8 12h8M8 16h5"/>', activ: true },
    { cheie: "registre321", regim: "ambele", grup: "speciale", titlu: "Registre art. 321", desc: "Nontransferuri \u00b7 bunuri primite pentru lucr\u0103ri",
      ...CULORI_CARD.piersica,
      icon: '<path d="M3 7h18v13H3z"/><path d="M3 7l3-4h12l3 4"/><path d="M9 12h6"/>', activ: true },
    { cheie: "balanta", regim: "dubla", grup: "registre", titlu: "Balan\u021b\u0103 de verificare", desc: "Solduri \u0219i rulaje pe ecran, cu \u00eenchiderea soldurilor",
      ...CULORI_CARD.albastru,
      icon: '<path d="M12 3v18M3 7h18M6 7l-3 5h6l-3-5zM18 7l-3 5h6l-3-5z"/>', activ: true },
    { cheie: "bilant", regim: "dubla", grup: "raportari", titlu: "Bilan\u021b anual", desc: "S1005 micro / S1003 mici, validare ANAF",
      ...CULORI_CARD.albastru,
      icon: '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>', activ: true },
    { cheie: "casa", regim: "ambele", grup: "zilnic", titlu: "Cas\u0103", desc: "Registru de cas\u0103, plafoane numerar",
      ...CULORI_CARD.verde,
      icon: '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M6 12h.01M18 12h.01"/>', activ: true },
    { cheie: "etransport", regim: "ambele", grup: "zilnic", titlu: "e-Transport", desc: "Notificare UIT, XML pentru SPV",
      ...CULORI_CARD.chihlimbar,
      icon: '<path d="M1 8h13v8H1zM14 11h4l3 3v2h-7z"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>', activ: true },
    { cheie: "operatiuni", regim: "dubla", grup: "speciale", titlu: "Operațiuni speciale", desc: "Leasing, marjă, IC, sponsorizări și altele",
      ...CULORI_CARD.violet,
      icon: '<path d="M12 2l2 4 4 .5-3 3 .8 4.5L12 12l-3.8 2 .8-4.5-3-3 4-.5z"/><path d="M5 18h14M5 21h14"/>', activ: true },
    // [lotul 10, 428, deciziile Costin 20.10.2026] compensarea facturilor emise și primite ale aceluiași partener (stinge ambele, mută TVA-ul la
    // încasare ca banca și casa) și fișele clienților (bifa „persoană afiliată”, CF art.282 alin.(6) lit.d)
    { cheie: "compensari", regim: "dubla", grup: "zilnic", titlu: "Compensări", desc: "Facturi emise și primite ale aceluiași partener",
      ...CULORI_CARD.violet,
      icon: '<path d="M7 7h10l-3-3M17 17H7l3 3"/>', activ: true },
    { cheie: "clienti", regim: "ambele", grup: "firma", titlu: "Clienți", desc: "Fișele clienților, persoane afiliate",
      ...CULORI_CARD.teal,
      icon: '<circle cx="9" cy="7" r="3"/><path d="M2 21v-1a6 6 0 0 1 12 0v1"/>', activ: true },
    // [lotul 11, decizia Costin 10.3 pct.4] fișele furnizorilor: localitatea și județul (D406 / D394 le citesc din fișă când factura nu le are)
    { cheie: "furnizori", regim: "ambele", grup: "firma", titlu: "Furnizori", desc: "Fișele furnizorilor: localitate, județ",
      ...CULORI_CARD.teal,
      icon: '<path d="M1 8h13v8H1zM14 11h4l3 3v2h-7z"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>', activ: true },
    // [lotul 12, deficiența 461, comanda Costin 12.1 pct.8] partenerii firmei
    { cheie: "parteneri", regim: "ambele", grup: "firma", titlu: "Parteneri", desc: "Clienți și furnizori: fișa, documentele, soldul",
      ...CULORI_CARD.teal,
      icon: '<circle cx="8" cy="8" r="3"/><circle cx="16" cy="8" r="3"/><path d="M2 20v-1a6 6 0 0 1 12 0v1M10 20v-1a6 6 0 0 1 12 0v1"/>', activ: true },
    // [368, lotul 9 — decizia Costin 8.2: „Mijloace fixe rămâne vizibil și la PFA”] registrul activelor e și al PFA (amortizarea fiscală în
    // D212); casarea și reevaluarea, care scriu note, nu se oferă la partidă simplă (`ecranMijloace`, opt.simpla)
    { cheie: "mijloace", regim: "ambele", grup: "registre", titlu: "Mijloace fixe", desc: "Registrul activelor: valoare, amortizat, casare, reevaluare",
      ...CULORI_CARD.chihlimbar,
      icon: '<rect x="3" y="4" width="18" height="6" rx="1"/><path d="M5 10v10h14V10"/><path d="M9 14h6M12 10v10"/>', activ: true },
    { cheie: "rip", regim: "simpla", grup: "zilnic", titlu: "Încasări/plăți", desc: "Partidă simplă PFA/II/IF, Fișă D212",
      ...CULORI_CARD.verde,
      icon: '<path d="M12 2v20M17 7H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>', activ: true },
    { cheie: "banca", regim: "ambele", grup: "zilnic", titlu: "Banc\u0103", desc: "Import extras, propuneri contare",
      ...CULORI_CARD.albastru,
      icon: '<path d="M3 21h18M4 18h16M6 18V9M10 18V9M14 18V9M18 18V9M2 9l10-6 10 6"/>', activ: true },
    { cheie: "magazin", regim: "ambele", grup: "zilnic", titlu: "Magazin online", desc: "WooCommerce \u2192 facturi automate",
      ...CULORI_CARD.violet,
      icon: '<circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>', activ: true },  // wc_fe_v1
    { cheie: "verificari", regim: "ambele", grup: "raportari", titlu: "Verific\u0103ri", desc: "Echilibru, trezorerie, TVA",
      descSimpla: "Trezorerie, TVA, documente pozate",   // [577] la partida simplă evidența e registrul de încasări și plăți
      ...CULORI_CARD.albastru,
      icon: '<path d="M9 11l3 3 8-8"/><path d="M21 12v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h11"/>', activ: true },
    { cheie: "solicitari", regim: "ambele", grup: "zilnic", titlu: "Solicitări client", desc: "Mesaje primite de la firma-client",
      ...CULORI_CARD.piersica,
      icon: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>', activ: true },
    { cheie: "acces", regim: "ambele", grup: "firma", titlu: "Acces client", desc: "Invită clientul în portal",
      ...CULORI_CARD.verde,
      icon: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M19 8v6"/><path d="M22 11h-6"/>', activ: true },
    { cheie: "import", regim: "ambele", grup: "firma", titlu: "Import date", desc: "Toate straturile de migrare, pentru aceast\u0103 firm\u0103",
      ...CULORI_CARD.albastru,
      icon: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>', activ: true },
    // [date_firma_v1] Datele pe care ANAF le cere in declaratii (CUI, denumire, CAEN,
    // adresa, banca, IBAN, telefon, reg.com). Pana acum nu se puteau completa din
    // interfata deloc - firma_profil_api salva doar font/culoare/logo. O firma noua
    // nu putea depune nimic pana nu se intervenea direct in baza de date.
    { cheie: "datefirma", regim: "ambele", grup: "firma", titlu: "Date firm\u0103", desc: "Datele cerute de ANAF \u00een declara\u021bii",
      ...CULORI_CARD.ardezie,
      icon: '<path d="M3 21h18"/><path d="M5 21V7l8-4v18"/><path d="M19 21V11l-6-4"/><path d="M9 9v.01M9 12v.01M9 15v.01M9 18v.01"/>', activ: true },
    { cheie: "rapoarte", regim: "ambele", grup: "raportari", titlu: "Rapoarte comerciale", desc: "Vânzări pe partener, durata de încasare, fișă client",  // rap_com_v1
      ...CULORI_CARD.violet,
      icon: '<path d="M3 3v18h18"/><rect x="7" y="10" width="3" height="7"/><rect x="12" y="6" width="3" height="11"/><rect x="17" y="13" width="3" height="4"/>', activ: true },
    { cheie: "registratura", regim: "ambele", grup: "zilnic", titlu: "Registratură", desc: "Numere de intrare/ieșire pe documente",  // registratura_v1
      ...CULORI_CARD.ardezie,
      icon: '<path d="M4 4h11l5 5v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z"/><path d="M14 4v5h5"/><path d="M8 13h6M8 16h6"/>', activ: true },
    { cheie: "contracte", regim: "ambele", grup: "firma", titlu: "Contracte", desc: "Generează din șabloane cu datele partenerului",  // contracte_v1
      ...CULORI_CARD.ardezie,
      icon: '<path d="M4 4h11l5 5v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z"/><path d="M14 4v5h5"/><path d="M9 13l2 2 4-4"/>', activ: true },
    // [Retest 2 pct.13, decizia Costin O12] „listă cu căutare după cont sau denumire, analiticele afișate sub contul sintetic, adăugare
    // de analitic de către contabil, iar un cont folosit în note nu se poate șterge”
    { cheie: "planconturi", regim: "dubla", grup: "firma", titlu: "Plan de conturi", desc: "Conturile firmei, cu analiticele sub sintetic",
      ...CULORI_CARD.ardezie,
      icon: '<path d="M4 4h16v4H4z"/><path d="M8 12h12M8 16h12M8 20h12"/><path d="M4 12h.01M4 16h.01M4 20h.01"/>', activ: true },
    { cheie: "centrecost", regim: "dubla", grup: "firma", titlu: "Centre de cost", desc: "Venituri și cheltuieli pe centre: note, facturi, salarii, mijloace fixe, stoc",  // [F143]
      ...CULORI_CARD.teal,
      icon: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>', activ: true },
  ];

  // [regim_card 23.07] Vizibilitatea cardurilor deriva prin regim_contabil (O SURSA, ca STRATURI_META), NU din
  // liste hardcodate DOAR_SRL/DOAR_PFA (a 4-a sursa paralela la aceeasi intrebare, eliminata - dupa termene,
  // semafor, neaplicabile_forma). Fiecare card declara `regim` OBLIGATORIU (ambele/simpla/dubla) - garda CARD_REGIM
  // in verificator il impune (fara default tacit). Contract STRICT pe t.regim_contabil (expus de backend,
  // auth_api:409): daca lipseste -> esec VIZIBIL, nu degradare tacita la "doar ambele" (doctrina P2: meniuFirma cu
  // tip_firma). 'declaratii'=ambele (PFA datoreaza D112/D300/...; D100/D101/D406 dezactivate in dropdown prin G1).
  // Casa=ambele (Legea 70/2015 plafon PFA). Vezi DESIGN_SYSTEM cap.18 + DECIZII 23.07.
  const regimFirma = t.regim_contabil;
  if (regimFirma !== "simpla" && regimFirma !== "dubla") {
    throw new Error("regim_contabil lipsa/invalid pe firma (" + regimFirma + ") — contract strict, nu degradez tacit");
  }
  const vizibile = optiuni.filter((o) => o.regim === "ambele" || o.regim === regimFirma);

  // [antet_explicit 23.07] Antetul firmei (nume · CUI) se randeaza EXPLICIT aici, nu se lasa pe seama
  // auto-h2 din navigator (_steaza: prepend <h2 class="pf-titlu"> prin MutationObserver DACA corpul n-are
  // deja unul). Dependenta de auto-h2 e fragila (observer + euristica "fara h2" + timing). Textul e IDENTIC
  // cu titlul ferestrei pasat de deschideFirma, deci conditia !querySelector("h2") din _steaza devine falsa
  // si antetul NU se dubleaza. Robustete, nu schimbare vizuala (DS cap.9: antetul = titlul ecranului).
  const antetFirma = (t.nume || "Firmă") + " · CUI " + (t.cui || "");
  corp.innerHTML = `
    <h2 class="pf-titlu">${esc(antetFirma)}</h2>
    <div id="firma-spv" style="margin-bottom:12px"></div>
    <div id="firma-preluare"></div>
    ${grupeazaCarduri(vizibile).map(([g, titluGrup, carduri]) => {
      return `<section class="firme-grup" aria-labelledby="fg-${g}">
      <h3 class="pf-subtitlu" id="fg-${g}">${titluGrup}</h3>
      <div class="firme-optiuni">
      ${carduri.map((o) => `
        <button class="firme-optiune" id="fa-${o.cheie}"${o.activ ? "" : ' disabled style="opacity:.55;cursor:default"'}>
          <div class="firme-optiune-icon" style="background:${o.bg}; color:${o.fg}">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${o.icon}</svg>
          </div>
          <div class="firme-optiune-titlu">${o.titlu}</div>
          <div class="firme-optiune-desc">${(regimFirma === "simpla" && o.descSimpla) || o.desc}${o.activ ? "" : " \u00b7 \u00een cur\u00e2nd"}</div>
        </button>`).join("")}
      </div></section>`;
    }).join("")}
    <div class="firme-scoatere" data-actiune="POST /tenants/{tenant_id}/activare|DELETE /tenants/{tenant_id}" data-zona-drepturi style="margin-top:24px;padding-top:14px;border-top:1px solid #e5e7eb">
      <button class="buton-secundar" id="firma-scoate" data-actiune="POST /tenants/{tenant_id}/activare|DELETE /tenants/{tenant_id}">Scoate firma din portofoliu</button>
      <p class="ecran-nota" style="margin:8px 0 0">Două acte diferite, în același loc:
         <strong>dezactivarea</strong> e reversibilă (firma iese din listă, datele rămân),
         <strong>ștergerea</strong> nu e (firma dispare cu totul, și se poate doar dacă n-a produs
         niciun document). Ecranul următor spune care se poate și de ce.</p>
    </div>`;

  _randDivergentaNume(corp, nav, t);   // [nume_anaf_v1]
  randeazaStareSpv(corp.querySelector("#firma-spv"), nav, t.id);   // [deficiența 289b] starea SPV a firmei, cu drum spre Conectare SPV
  // [lotul 13, deficiența 662] firma nouă se deschide cu „Începe preluarea” (preluarea începută și neterminată: „Continuă preluarea”)
  randeazaPreluareFirma(corp.querySelector("#firma-preluare"), nav, t);

  // [deficiența 262, comanda Costin 15.10.2026] „asistentul vede «Scoate firma din portofoliu» în fereastra firmei; se ascunde, ca în
  // lista de firme.” Blocul întreg (butonul + nota lui) poartă acțiunile ecranului de scoatere — amândouă numai ale administratorului —,
  // deci poarta din drepturi.js îl scoate; butonul le poartă și el, fiindcă gardul (`scan_drepturi_ui.intrari_in_ecrane_doar_admin`)
  // citește elementul legat de handler. Blocul e și zona motivului (`data-zona-drepturi`): motivul porții stă în bloc și dispare cu el —
  // pus în fereastra firmei, ar fi spus „Acțiunile de aici nu se afișează” deasupra a două duzini de carduri de lucru.
  const bScoate = corp.querySelector("#firma-scoate");
  if (bScoate) bScoate.addEventListener("click", () =>
    nav.deschide("Scoate firma", (c2) => ecranScoateFirma(c2, nav, t)));

  const bAcces = corp.querySelector("#fa-acces");
  if (bAcces) bAcces.addEventListener("click", () => nav.deschide("Acces client", (c2) => ecranAccesClient(c2, nav, t)));
  const bFacturi = corp.querySelector("#fa-facturi");
  if (bFacturi) {
    bFacturi.addEventListener("click", () => {
      nav.deschide("Facturi", (c2) => randeazaFacturi(c2, nav, t.id, {}), { lat: "larg" }); /* facturi_larg_v1 */
    });
    // [f131] alerta in aplicatie: badge cu nr. de facturi restante pe cardul Facturi
    // (tiparul cab-card-badge din cabinet.js). Nu blocheaza randarea - se ataseaza cand vine raspunsul.
    (async () => {
      try {
        const r = await api.get(`/tenants/${t.id}/scadentar`);
        const n = (r && r.rezumat && r.rezumat.restanta) || 0;
        if (n > 0) {
          const b = document.createElement("span");
          b.className = "cab-card-badge";
          b.textContent = n;
          b.title = cate(n, "factură restantă", "facturi restante");
          bFacturi.style.position = "relative";
          bFacturi.appendChild(b);
        }
      } catch { /* scadentarul e best-effort pt badge; nu rupe cardul */ }
    })();
  }
  const bSalariati = corp.querySelector("#fa-salariati");
  if (bSalariati && !bSalariati.disabled) {
    bSalariati.addEventListener("click", () => { nav.deschide("Salariați", (c2) => ecranSalariati(c2, nav, t)); });
  }
  const bDateFirma = corp.querySelector("#fa-datefirma");  // [date_firma_v1]
  if (bDateFirma && !bDateFirma.disabled) {
    bDateFirma.addEventListener("click", () => { nav.deschide("Date firm\u0103", (c2) => randeazaDateFirma(c2, nav, t.id)); });
  }
  const bProduse = corp.querySelector("#fa-produse");  // [produse_firma_v1]
  if (bProduse && !bProduse.disabled) {
    bProduse.addEventListener("click", () => { nav.deschide("Produse", (c2) => randeazaProduse(c2, nav, t.id)); });
  }
  const bDeclaratii = corp.querySelector("#fa-declaratii");  // [decl_firma_v1]
  if (bDeclaratii && !bDeclaratii.disabled) {
    bDeclaratii.addEventListener("click", () => { nav.deschide("Declara\u021bii", (c2) => declaratiiPerFirma(c2, nav, { tenant_id: t.id, nume: t.nume }), { lat: "tabel" }); });   // [08.10, W5]
  }
  const bControl = corp.querySelector("#fa-control");
  if (bControl && !bControl.disabled) {
    bControl.addEventListener("click", () => { nav.deschide("Control fiscal", (c2) => ecranControlFirma(c2, nav, t)); });
  }
  const bBonuri = corp.querySelector("#fa-bonuri");
  if (bBonuri) {
    bBonuri.addEventListener("click", () => { nav.deschide("Bonuri și chitanțe", (c2) => ecranBonuri(c2, nav, t), { lat: "larg" }); });  /* bon_flux_e4_v1 */
  }
  const bJurnal = corp.querySelector("#fa-jurnal");
  if (bJurnal) {
    // [394, lotul 9] fereastra lată (ca Mijloace fixe): rândul unei linii de notă (debit = credit · sumă · centru · partener) încape pe un
    // rând, iar „Notă nouă” nu mai derulează pe un ecran de laptop (1366×768)
    bJurnal.addEventListener("click", () => { nav.deschide("Registru jurnal", (c2) => ecranJurnal(c2, nav, t), { lat: "tabel" }); });
  }
  const bMagazin = corp.querySelector("#fa-magazin");  // wc_fe_v1
  if (bMagazin) {
    bMagazin.addEventListener("click", () => nav.deschide("Magazin online", (c2) => ecranMagazin(c2, nav, t.id)));
  }
  const bZ = corp.querySelector("#fa-raportz");
  if (bZ) {
    bZ.addEventListener("click", () => { nav.deschide("Raport Z", (c2) => ecranRaportZ(c2, nav, t)); });
  }
  const bBilant = corp.querySelector("#fa-bilant");
  if (bBilant) {
    bBilant.addEventListener("click", () => { nav.deschide("Bilanț", (c2) => ecranBilant(c2, nav, t)); });
  }
  const bInchidere = corp.querySelector("#fa-inchidere");   // [08.10, U3]
  if (bInchidere) bInchidere.addEventListener("click", () => { nav.deschide("Închidere lună", (c2) => ecranInchidereLuna(c2, nav, t)); });
  const bStocuri = corp.querySelector("#fa-stocuri");
  if (bStocuri) {
    bStocuri.addEventListener("click", () => { nav.deschide("Stocuri", (c2) => ecranStocuri(c2, nav, t)); });
  }
  const bCasa = corp.querySelector("#fa-casa");
  if (bCasa) {
    bCasa.addEventListener("click", () => { nav.deschide("Casă", (c2) => ecranCasa(c2, nav, t), { lat: "larg" }); });
  }
  const bRip = corp.querySelector("#fa-rip");
  if (bRip) bRip.addEventListener("click", () => { nav.deschide("Încasări/plăți", (c2) => ecranRip(c2, nav, t)); });
  const bOperatiuni = corp.querySelector("#fa-operatiuni");
  if (bOperatiuni) bOperatiuni.addEventListener("click", () => { nav.deschide("Operațiuni speciale", (c2) => ecranOperatiuni(c2, nav, t)); });
  const bComp = corp.querySelector("#fa-compensari");   // [lotul 10, 428]
  if (bComp) bComp.addEventListener("click", () => nav.deschide("Compensări", (c2) => ecranCompensari(c2, nav, t,
    { jurnal: (o) => nav.deschide("Registru jurnal", (c3) => ecranJurnal(c3, nav, t, o), { lat: "tabel" }) }), { lat: "tabel" }));
  const bCl = corp.querySelector("#fa-clienti");   // [lotul 10, 428]
  if (bCl) bCl.addEventListener("click", () => nav.deschide("Clienți", (c2) => ecranClienti(c2, nav, t), { lat: "tabel" }));
  const bFz = corp.querySelector("#fa-furnizori");   // [lotul 11, decizia 10.3] fișele furnizorilor
  if (bFz) bFz.addEventListener("click", () => nav.deschide("Furnizori", (c2) => ecranFurnizori(c2, nav, t), { lat: "tabel" }));
  const bPt = corp.querySelector("#fa-parteneri");   // [lotul 12, 461] partenerii firmei
  if (bPt) bPt.addEventListener("click", () => nav.deschide("Parteneri", (c2) => ecranParteneriFirmei(c2, nav, t), { lat: "tabel" }));
  const bMijloace = corp.querySelector("#fa-mijloace");  // [ecran_mf_v1]
  if (bMijloace) bMijloace.addEventListener("click", () => { nav.deschide("Mijloace fixe", (c2) => ecranMijloace(c2, nav, t.id, { simpla: t.regim_contabil === "simpla" }), { lat: "tabel" }); });   // [08.10, W5] [368]
  const bEtransport = corp.querySelector("#fa-etransport");
  if (bEtransport) bEtransport.addEventListener("click", () => { nav.deschide("e-Transport", (c2) => ecranEtransport(c2, nav, t)); });
  const bBalanta = corp.querySelector("#fa-balanta");
  if (bBalanta) bBalanta.addEventListener("click", () => { nav.deschide("Balanță de verificare", (c2) => ecranBalanta(c2, nav, t), { lat: "tabel" }); });   // [08.10, W5]
  const bFisa = corp.querySelector("#fa-fisacont");   // [lista 3] Cartea mare, prin fisa de cont 14-6-22
  if (bFisa) bFisa.addEventListener("click", () => { nav.deschide("Cartea mare", (c2) => ecranFisaCont(c2, nav, t)); });
  const bMarja = corp.querySelector("#fa-marja");     // [lista 3] jurnalul special de regim marja
  if (bMarja) bMarja.addEventListener("click", () => { nav.deschide("Jurnal regim marjă", (c2) => ecranJurnalMarja(c2, nav, t)); });
  const bRegFisc = corp.querySelector("#fa-regfiscal");  // [lista 3] registrul de evidenta fiscala
  if (bRegFisc) bRegFisc.addEventListener("click", () => { nav.deschide("Registrul de evidență fiscală", (c2) => ecranRegistruFiscal(c2, nav, t), { lat: "larg" }); });
  const bRegInv = corp.querySelector("#fa-reginventar");  // [lista 3] registrul-inventar 14-1-2
  if (bRegInv) bRegInv.addEventListener("click", () => { nav.deschide("Registrul-inventar", (c2) => ecranRegistruInventar(c2, nav, t), { lat: "larg" }); });
  const bReg321 = corp.querySelector("#fa-registre321");  // [lista 3] cele doua registre din normele art. 321
  if (bReg321) bReg321.addEventListener("click", () => { nav.deschide("Registre art. 321", (c2) => ecranRegistre321(c2, nav, t), { lat: "larg" }); });
  const bRapoarte = corp.querySelector("#fa-rapoarte");  // rap_com_v1
  if (bRapoarte) bRapoarte.addEventListener("click", () => { nav.deschide("Rapoarte comerciale", (c2) => ecranRapoarte(c2, nav, t), { lat: "larg" }); });
  const bRegistratura = corp.querySelector("#fa-registratura");  // registratura_v1
  if (bRegistratura) bRegistratura.addEventListener("click", () => { nav.deschide("Registratură", (c2) => ecranRegistratura(c2, nav, t)); });
  const bContracte = corp.querySelector("#fa-contracte");  // contracte_v1
  if (bContracte) bContracte.addEventListener("click", () => { nav.deschide("Contracte", (c2) => ecranContracte(c2, nav, t)); });
  const bPlan = corp.querySelector("#fa-planconturi");   // [Retest 2 pct.13]
  if (bPlan) bPlan.addEventListener("click", () => { nav.deschide("Plan de conturi", (c2) => ecranPlanConturi(c2, nav, t)); });
  const bCentre = corp.querySelector("#fa-centrecost");  // [F143]
  if (bCentre) bCentre.addEventListener("click", () => { nav.deschide("Centre de cost", (c2) => ecranCentreCost(c2, nav, t)); });
  const bBanca = corp.querySelector("#fa-banca");
  if (bBanca) {
    bBanca.addEventListener("click", () => { nav.deschide("Bancă", (c2) => ecranBanca(c2, nav, t)); });
  }
  const bVerif = corp.querySelector("#fa-verificari");
  if (bVerif) {
    bVerif.addEventListener("click", () => { nav.deschide("Verificări", (c2) => ecranVerificari(c2, nav, t)); });
  }
  const bSolicitari = corp.querySelector("#fa-solicitari");
  if (bSolicitari) {
    bSolicitari.addEventListener("click", () => {   // [05.10.2026] DS cap.2a: un card = o fereastră (se deschidea inline, peste meniu)
      nav.deschide("Solicitări client", (c2) => ecranSolicitariCabinet(c2, nav, t));
    });
  }
  const bImport = corp.querySelector("#fa-import");
  if (bImport) {
    bImport.addEventListener("click", () => {
      nav.mergi("Import date", (c) => meniuMigrarePerFirma(c, nav, { tenant_id: t.id, nume: t.nume, tip_firma: t.tip_firma }));  // entitatea e in antet (DS cap.1), nu in titlu. tip_firma -> pasul RIP doar la PFA
    });
  }
}


async function ecranSolicitariCabinet(corp, nav, t) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
  await randeazaSolicitariCabinet(corp, nav, t);
}

async function randeazaSolicitariCabinet(corp, nav, t) {
  let lista = [];
  try {
    const r = await api.get(`/tenants/${t.id}/solicitari`);
    lista = (r && r.solicitari) || [];
  } catch { corp.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca mesajele.</p>`; return; }
  let firHtml = '<div class="stare-goala">Niciun mesaj încă.</div>';
  if (lista.length) {
    firHtml = lista.map((s) => {
      const cine = s.autor_rol === "cabinet" ? "Tu" : "Client";
      return `<div class="sol-rand sol-${s.autor_rol === "cabinet" ? "client" : "cabinet"}">
        <div class="sol-mesaj">${esc(s.mesaj)}</div>
        <div class="sol-meta">${cine} · ${dataRo(s.creat_la)}</div>
      </div>`;
    }).join("");
  }
  corp.innerHTML = `
    <h2 class="pf-titlu">Solicitări</h2>
    <p class="pf-intro">Mesaje de la firma-client.</p>
    <div class="sol-fir" id="sol-fir">${firHtml}</div>
    <div class="sol-trimite">
      <textarea aria-label="Răspunsul tău" id="sol-input" placeholder="Scrie un răspuns..." rows="3"></textarea>
      <button class="buton-primar" id="sol-trimite-btn" data-actiune="POST /tenants/{tenant_id}/solicitari">Trimite</button>
    </div>
  `;
  const fir = corp.querySelector("#sol-fir");
  if (fir) fir.scrollTop = fir.scrollHeight;
  const btn = corp.querySelector("#sol-trimite-btn");
  if (btn) btn.addEventListener("click", async () => {
    const inp = corp.querySelector("#sol-input");
    const txt = ((inp && inp.value) || "").trim();
    if (!txt) return;
    try {
      await api.post(`/tenants/${t.id}/solicitari`, { mesaj: txt });
      await randeazaSolicitariCabinet(corp, nav, t);
    } catch (e) {
      /* [catch_scriere 27.07.2026] mesajul netrimis parea trimis. DS cap.6. */
      arataMesaj(corp, (e && e.mesaj) || "Nu s-a putut trimite mesajul.", "eroare");
    }
  });
}

// [verificari] Verificari coerenta pe firma: echilibru, trezorerie, TVA
// [paritate_randare 24.07] Inventar DECLARAT pt garda VERDICT_PARITATE (DS cap.20). ecranVerificari consuma vc
// BRUT de la /firme/{id}/verificari (pe luna) si alege chei pe NUME. Fiecare cheie vc PRODUSA de backend trebuie
// sa fie ori randata mai jos, ori ignorata AICI cu motiv — nu tacut (aceeasi clasa care ascundea salariile pe
// cardul din fisa). Citit ca TEXT de verificator_conformitate.py (paritate de randare, al doilea consumator), nu
// la runtime. Randare noua NU se adauga aici — doar declaratia; cross-check-urile raman exclusiv in verdict.
const VC_VERIFICARI = {
  echilibru:             "randat — Echilibru (partidă dublă pe perioadă + orfani + solduri inițiale), prin randEchilibru",
  trezorerie:            "randat — Trezorerie (solduri creditoare)",
  documente_pozate:      "randat — Documente pozate de clienți",
  tva:                   "randat — TVA (rezultat + sold)",
  note:                  "randat — contor de note contabile în antet",
  tva_incrucisat:        "IGNORAT — acest ecran arată doar coerența brută lunară; cross-check-urile declarație-vs-contabilitate aparțin exclusiv verdictului din Control fiscal (control_verdict.js)",
  d112_incrucisat:       "IGNORAT — idem (salarii D112 vs contabilitate)",
  d390_incrucisat:       "IGNORAT — idem (operațiuni intracomunitare D390 vs evidență)",
  cota_tva_conformitate: "IGNORAT — idem (cotă TVA facturi emise vs perioadă)",
};
// [R33 varianta b\u2032\u2032, 26.08.2026] «Echilibru» e UN rand pe ecran, dar DOUA verificari in spate,
// cu moduri de esec DISJUNCTE (partida dubla pe liniile perioadei + orfani; inchiderea soldurilor
// initiale). Costin: *"cele doua se arata ca una singura, cu ce a gasit fiecare. Contabilul nu
// trebuie sa stie ca sunt doua module."* Randorul NU decide nimic: primeste `constatari` ca OBIECTE
// cu cifre (DS cap.13) si le pune in cuvinte. Textul se DERIVA din `fel`, nu se alege aici (P13).
// De ce nu merge prin `rand()` generic: acela citeste `.cod`, iar verdictul compus n-are un singur
// cod \u2014 are o lista. Trecut prin `rand()`, un verdict ROSU fara `.cod` ar fi iesit VERDE.
function detaliuEchilibru(x) {
  if (x.fel === "ledger_dezechilibrat")
    return `partid\u0103 dubl\u0103 rupt\u0103: \u03a3 debit ${bani(x.sigma_debit)} vs \u03a3 credit ${bani(x.sigma_credit)} (diferen\u021b\u0103 ${bani(x.diferenta)} lei)`;
  if (x.fel === "orfani")
    return `${cate(x.numar, "linie trimite", "linii trimit")} la o \u00eenregistrare care nu exist\u0103`;
  if (x.fel === "solduri_dezechilibrate")
    return `solduri ini\u021biale: diferen\u021b\u0103 ${bani(x.diferenta_solduri)} lei`;
  if (x.fel === "neverificat")
    return `nu s-a putut verifica ${esc(x.ce || "")}${x.motiv ? " \u2014 " + esc(x.motiv) : ""}`;
  return esc(x.fel || "");
}
function randEchilibru(e) {
  if (!e) return "";
  const c = e.constatari || [];
  const necunoscut = c.some((x) => x.fel === "neverificat");
  const detaliu = e.ok ? "\u00een regul\u0103" : c.map(detaliuEchilibru).join(" \u00b7 ");
  // gri pentru necunoscut, rosu pentru problema gasita: necunoscutul NU se randeaza ca defect,
  // dar nici ca "in regula" (P6 \u2014 necunoscut domina favorabil, problema domina necunoscutul).
  const clasa = e.ok ? "pct-verde" : (necunoscut && !c.some((x) => x.fel !== "neverificat") ? "pct-info" : "pct-rosu");
  return `<div class="pf-frand">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">Echilibru</div>
          <div class="pf-frand-sub">${detaliu}</div>
        </div>
        <span class="cab-pct ${clasa}"></span>
      </div>`;
}

async function ecranVerificari(corp, nav, t) {
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  const cerereNoua = ultimaCerere();   // [C103] luna schimbată în șir (← / →): numai verificările lunii afișate ajung pe ecran
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se verifică…</p>`;
    const actuala = cerereNoua();
    let r = null;
    try { r = await api.get(`/firme/${t.id}/verificari?an=${an}&luna=${luna}`); } catch {}
    if (!actuala()) return;
    let vs = null;  // [verif_stocuri_v1]
    let intra = null;  // [intrastat_v1]
    try { intra = await api.get(`/tenants/${t.id}/intrastat-praguri?an=${an}`); } catch {}
    if (!actuala()) return;
    try { vs = await api.get(`/tenants/${t.id}/verificare-stocuri`); } catch {}
    if (!actuala()) return;
    const rand = (nume, obj) => {
      const ok = obj && (obj.ok === true || obj.cod === undefined) && !(Array.isArray(obj) && obj.length);
      // [Retest 2 pct.2] mesajul problemei, nu codul ei intern („TREZORERIE_NEGATIVA”)
      const detaliu = ok ? "în regulă" : esc((Array.isArray(obj) ? obj.map((p) => p.mesaj || p.cod).join(" · ") : (obj && (obj.mesaj || obj.cod))) || "problemă");
      return `<div class="pf-frand">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(nume)}</div>
          <div class="pf-frand-sub">${detaliu}</div>
        </div>
        <span class="cab-pct ${ok ? 'pct-verde' : 'pct-rosu'}"></span>
      </div>`;
    };
    corp.innerHTML = `
      <h2 class="pf-titlu">Verific\u0103ri</h2>
      <p class="pf-intro">Luna ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")} \u00b7 ${cate(r ? r.note : 0, "not\u0103 contabil\u0103", "note contabile")}
        <button class="buton-secundar" id="vf-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="buton-secundar" id="vf-next">luna \u2192</button></p>
      <div class="pf-lista">
        ${r ? randEchilibru(r.echilibru) : ""}
        ${r ? rand("Trezorerie (f\u0103r\u0103 solduri creditoare)", r.trezorerie) : ""}
        ${r && r.documente_pozate ? `<div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">Documente pozate de clien\u021bi</div>
          <div class="pf-frand-sub">${r.documente_pozate.ok ? "\u00een regul\u0103" : [r.documente_pozate.bonuri_neverificate ? cate(r.documente_pozate.bonuri_neverificate, "document confirmat de client, necontat", "documente confirmate de client, necontate") + " de peste 3 zile" : "", r.documente_pozate.ciorne_casa ? cate(r.documente_pozate.ciorne_casa, "not\u0103 de cas\u0103 \u00een ciorn\u0103, nevalidat\u0103", "note de cas\u0103 \u00een ciorn\u0103, nevalidate") + " de peste 3 zile" : ""].filter(Boolean).join(" \u00b7 ")}</div>
        </div><span class="cab-pct ${r.documente_pozate.ok ? 'pct-verde' : 'pct-rosu'}"></span></div>` : ""}
        ${r ? `<div class="pf-frand"><div class="pf-frand-text"><div class="pf-frand-nume">TVA</div><div class="pf-frand-sub">${r.tva.rezultat === "de_plata" ? "de plat\u0103" : "de recuperat"}: ${bani(r.tva.suma)} lei (cont ${r.tva.cont})</div></div><span class="cab-pct pct-info"></span></div>` : ""}
        ${vs ? `<div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">Stocuri (contabil vs fi\u0219e CV)</div>
          <div class="pf-frand-sub">${vs.ok ? "în regulă" : vs.conturi.filter(c=>!c.ok).map(c=>`cont ${c.cod || c.cont}: contabil ${bani(c.sold_contabil)} vs fi\u0219e ${bani(c.valoare_fise_cv)} (diferență ${bani(c.diferenta)})`).join(" \u00b7 ")}</div>
        </div><span class="cab-pct ${vs.ok ? 'pct-verde' : 'pct-rosu'}"></span></div>` : ""}
        ${intra ? `<div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">Intrastat (prag 1.000.000 lei/flux, an ${an})</div>
          <div class="pf-frand-sub">Introduceri: ${intra.introduceri ? intra.introduceri.cumulat + " lei (" + intra.introduceri.procent + "%)" + (intra.introduceri.status !== "sub_prag" ? " \u00b7 depășit din luna " + intra.introduceri.luna_depasirii : "") : "-"} \u00b7 Expedieri: ${intra.expedieri ? intra.expedieri.cumulat + " lei (" + intra.expedieri.procent + "%)" + (intra.expedieri.status !== "sub_prag" ? " \u00b7 depășit din luna " + intra.expedieri.luna_depasirii : "") : "-"}</div>
        </div><span class="cab-pct ${(intra.introduceri && intra.introduceri.status !== 'sub_prag') || (intra.expedieri && intra.expedieri.status !== 'sub_prag') ? 'pct-rosu' : 'pct-verde'}"></span></div>` : ""}
        ${!r ? '<div class="ecran-nota">Nu s-au putut rula verific\u0103rile.</div>' : ""}
      </div>`;
    corp.querySelector("#vf-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#vf-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
  };
  deseneaza();
}

// [salariati] Stat de plata lunar + fluturasi

// [F137] lookup COR: input de cautare (cod sau denumire) -> lista rezultate din /cor -> selectie
// seteaza codul in inputul ascuns #<prefix>-cor. Valoarea se seteaza DOAR prin selectie (nu free-text),
// ca sa nu ajunga in DB un cod inexistent (backend valideaza si el). Refoloseste zona inline existenta.
function legaCorLookup(scope, prefix, codInitial, denInitial) {
  const cauta = scope.querySelector(`#${prefix}-cor-cauta`);
  const hid = scope.querySelector(`#${prefix}-cor`);
  const rez = scope.querySelector(`#${prefix}-cor-rez`);
  if (!cauta || !hid || !rez) return;
  if (codInitial) { hid.value = codInitial; cauta.value = denInitial ? `${codInitial} — ${denInitial}` : codInitial; }
  let timer;
  const cerereCor = ultimaCerere();   // [C103] căutarea tastată în șir: numai rezultatele textului din câmp ajung în listă
  cauta.addEventListener("input", () => {
    const actuala = cerereCor();   // orice tastare scoate din joc răspunsul cererii de dinainte (și când textul scade sub 2 litere)
    hid.value = "";  // orice tastare invalideaza selectia anterioara pana la o noua alegere
    clearTimeout(timer);
    const q = cauta.value.trim();
    if (q.length < 2) { rez.innerHTML = ""; return; }
    timer = setTimeout(async () => {
      let list = [];
      try { const r = await api.get(`/cor?q=${encodeURIComponent(q)}`); if (!actuala()) return; list = (r && r.rezultate) || []; }
      catch { if (!actuala()) return; rez.innerHTML = ""; return; }
      rez.innerHTML = list.length
        // [lotul 13, 674] fiecare ocupație găsită e un buton (se alege și din tastatură), nu un rând de text pe care se dă clic
        ? list.map((o) => `<button type="button" class="btn-link cor-opt" data-cod="${esc(o.cod)}" data-actiune="POST /tenants/{tenant_id}/prapastie-salariu" data-den="${esc(o.denumire)}" style="display:block;width:100%;text-align:left;padding:6px 8px;border-bottom:1px solid var(--linie)">${esc(o.cod)} — ${esc(o.denumire)}</button>`).join("")
        : `<div style="padding:6px 8px;color:var(--gri)">nicio ocupație găsită</div>`;
      rez.querySelectorAll("[data-cod]").forEach((el) => el.addEventListener("click", () => {
        hid.value = el.dataset.cod;
        cauta.value = `${el.dataset.cod} — ${el.dataset.den}`;
        rez.innerHTML = "";
      }));
    }, 300);
  });
}

function campCorLookup(prefix, obligatoriu) {
  return `<div class="camp"><label class="camp-eticheta" for="${prefix}-cor-cauta">Ocupație (COR)${obligatoriu ? '<span class="oblig">*</span>' : ""}</label>
    <input type="text" id="${prefix}-cor-cauta" class="camp-input" placeholder="cod sau denumire (ex. programator)" autocomplete="off">
    <input type="hidden" id="${prefix}-cor">
    <div id="${prefix}-cor-rez" class="cor-rez-lista"></div></div>`;
}

// [lotul 12, C133] Motivul scutirii de contribuția minimă (D112 `motivExc`), după OPANAF 605/2026 anexa 2, secțiunea „Date de
// identificare ale asiguratului”, pct.12 (CF art.146 alin.(5^7) lit.a–e); serverul primește numărul (`salariati_api.MOTIVE_EXCEPTARE`).
// [lotul 13, 676] Lista scurtă a salarizării (≤ 6 opțiuni): un select cu `data-butoane`, pe care mecanismul comun (`api.alegereButoane`,
// DS cap.2a) îl arată ca butoane alăturate; „— alege —” când nu e nimic salvat (DS cap.17), iar salvarea o cere cu `cereAlegerile`. O valoare
// salvată care nu e printre opțiuni nu alege tacit prima opțiune: rămâne „— alege —”.
// Da / Nu ca listă scurtă (aceleași valori ca `selectDaNu`, citite cu `daNu`): helperul formularului „Salariat nou” face câmpurile din id
const DA_NU = [["true", "Da"], ["false", "Nu"]];
function selectScurt(id, optiuni, ales, eticheta) {
  const a = optiuni.some(([v]) => String(v) === String(ales ?? "")) ? String(ales) : "";
  return `<select id="${id}" class="camp-input" data-butoane="" aria-label="${esc(eticheta || "")}">${a ? "" : ALEGE}${optiuni.map(([v, l]) =>
    `<option value="${esc(String(v))}"${a === String(v) ? " selected" : ""}>${esc(l)}</option>`).join("")}</select>`;
}
const MOTIVE_EXCEPTARE = [
  [1, "elev sau student până la 26 de ani, într-o formă de școlarizare"],
  [2, "ucenic până la 18 ani, cu contract de ucenicie"],
  [3, "persoană cu dizabilități sau căreia legea îi permite să lucreze mai puțin de 8 ore pe zi"],
  [4, "pensionar pentru limită de vârstă în sistemul public de pensii"],
  [5, "are două sau mai multe contracte, cu baza cumulată cel puțin salariul minim"],
];
// câmpul motivului: vizibil numai când scutirea e „Da”, fără nicio opțiune aleasă (nimic precompletat)
// [lotul 13, 676] cinci motive: butoane alăturate (`selectScurt`), nimic ales
function campMotivScutire(id) {
  return `<div class="camp" id="${id}-camp" hidden><span class="camp-eticheta">Motivul scutirii<span class="oblig">*</span></span>
    ${selectScurt(id, MOTIVE_EXCEPTARE, "", "Motivul scutirii")}
    <span class="camp-ajutor">Intră în D112 (motivul exceptării de la contribuția minimă).</span></div>`;
}
function legaMotivScutire(corp, idScutit, idMotiv, mereu) {
  const sc = corp.querySelector("#" + idScutit), camp = corp.querySelector("#" + idMotiv + "-camp");
  const arata = () => { camp.hidden = !(mereu || (sc && daNu(sc) === true)); };
  if (sc) sc.addEventListener("change", arata);
  arata();
}
// [C133, comanda Costin 12.3 pct.8] corecturile scutirii salariatului (`salariati_jurnal`: cine, când, vechi → nou), în „Corectează
// datele” — aceeași formă ca „Istoricul modificărilor” din Date firmă (tabelul `fd-tabel`, data cu ora, numele persoanei)
const ETICHETE_JURNAL_SCUTIRE = { scutit_contrib_minim: "Scutit de contribuția minimă", motiv_exceptare: "Motivul scutirii" };
function _valoareScutire(camp, x) {
  if (x == null || x === "") return "\u2014";
  if (camp === "scutit_contrib_minim") return x === "true" ? "Da" : (x === "false" ? "Nu" : esc(x));
  const m = MOTIVE_EXCEPTARE.find(([v]) => String(v) === String(x));
  return m ? esc(m[1]) : esc(x);
}
function blocJurnalScutire(j) {
  if (!j || !j.length) return "";
  return `<div class="camp-eticheta" style="font-weight:600;margin-top:8px">Corecturile scutirii</div>
    <table class="fd-tabel" id="ed-jurnal-tabel"><thead><tr><th>Când</th><th>Cine</th><th>Câmp</th><th>Valoare veche</th><th>Valoare nouă</th></tr></thead>
    <tbody>${j.slice(0, 5).map((r) => `<tr><td>${dataRo(r.la, "cu_ora")}</td><td>${esc(r.cine || "")}</td><td>${esc(ETICHETE_JURNAL_SCUTIRE[r.camp] || r.camp)}</td>
      <td>${_valoareScutire(r.camp, r.vechi)}</td><td>${_valoareScutire(r.camp, r.nou)}</td></tr>`).join("")}</tbody></table>
    ${j.length > 5 ? `<div class="camp-ajutor">${esc(cate(j.length - 5, "corectură mai veche", "corecturi mai vechi"))} în jurnal.</div>` : ""}`;
}
function motivAles(corp, idMotiv) {
  const el = corp.querySelector("#" + idMotiv), camp = corp.querySelector("#" + idMotiv + "-camp");
  return el && camp && !camp.hidden && el.value ? Number(el.value) : null;
}

// [decizia Costin 14.10.2026 pct.3–4] avertismentul din statul de plată pentru câmpurile importate fără valoare, până la confirmare
function _avertDeVerificat(s) {
  const dv = s.de_verificat || [];
  if (!dv.length) return "";
  const parti = [];
  if (dv.includes("persoane_intretinere")) parti.push("persoane în întreținere de completat (s-au importat 0 — deducerea personală poate fi greșită)");
  if (dv.includes("scutit_contrib_minim")) parti.push("scutirea de contribuția minimă de verificat (s-a importat „nescutit”)");
  // [lotul 10, deficiența 420] norma și funcția de bază lipsă din fișierul importat: intrate cu propunerea, de confirmat
  if (dv.includes("tip_norma")) parti.push("norma de lucru de verificat (fișierul n-o avea; s-a propus " + (s.tip_norma === "partiala" ? "normă parțială" : "normă întreagă") + ")");
  if (dv.includes("functie_baza")) parti.push("funcția de bază de verificat (fișierul n-o avea; s-a propus „Da” — decide deducerea personală)");
  if (dv.includes("motiv_exceptare")) parti.push("motivul scutirii de contribuția minimă de ales (D112 îl declară)");   // [C133]
  return `<div class="pf-frand-sub" role="status" style="color:var(--rosu)">⚠ ${esc(parti.join("; "))}. Confirmă cu butonul „De verificat”.</div>`;
}

function formularSalariatNou(corp, nav, t, dupaSalvare) {
  const camp = (id, eticheta, tip, extra) => {
    const optional = !(extra && extra.obligatoriu);
    if (tip === "select") {
      // [lotul 13, 676] listele scurte (normă, tip contract): butoane alăturate, nimic ales
      return `<div class="camp"><span class="camp-eticheta">${eticheta}${optional ? "" : '<span class="oblig">*</span>'}</span>${selectScurt(`sn-${id}`, extra.optiuni || [], "", eticheta)}</div>`;
    }
    if (tip === "danu") {
      // [lotul 07.10 B, DS cap.17] DA/NU situațional, fără preselecție; [lotul 13, 676] două butoane alăturate
      return `<div class="camp"><span class="camp-eticheta">${eticheta}<span class="oblig">*</span></span>${selectScurt(`sn-${id}`, DA_NU, null, eticheta)}</div>`;
    }
    // [lotul 13, 655] sumele și numerele se scriu ca text, citite în format românesc (`sumaRo`): „1.000” = o mie
    const inputTip = tip === "data" ? "date" : "text";
    const mod = tip === "numar" ? ' inputmode="decimal"' : "";
    return `<div class="camp"><label class="camp-eticheta" for="sn-${id}">${eticheta}${optional ? "" : '<span class="oblig">*</span>'}</label><input type="${inputTip}"${mod} id="sn-${id}" class="camp-input"></div>`;
  };
  corp.innerHTML = `
    <h2 class="pf-titlu">Salariat nou</h2>
    <div class="grila-campuri">
      ${camp("nume", "Nume", "text", { obligatoriu: true })}
      ${camp("prenume", "Prenume", "text")}
      ${camp("cnp", "CNP", "text", { obligatoriu: true })}
      ${camp("data_angajare", "Data angaj\u0103rii", "data")}
      ${camp("data_incetare", "Data încetării (gol = activ)", "data")}
      ${camp("tip_norma", "Tip norm\u0103", "select", { obligatoriu: true, optiuni: [["intreaga","\u00centreag\u0103"],["partiala","Par\u021bial\u0103"]] })}
      ${camp("ore_zi", "Ore/zi (norm\u0103 par\u021bial\u0103)", "numar", { pas: "0.5" })}
      ${camp("salariu_brut", "Salariu brut", "numar", { obligatoriu: true })}
      ${camp("persoane_intretinere", "Persoane \u00een \u00eentre\u021binere", "numar", { pas: "1" })}
      ${camp("data_nastere", "Data nașterii (pentru deducerea tinerilor sub 26 de ani)", "data")}
      ${camp("copii_scolarizati", "Copii ≤ 18 ani înscriși în învățământ (deducere 100 lei/copil)", "numar", { pas: "1" })}
      ${camp("declaratie_copii", "Declarația părintelui pentru copii (art.77) — fără ea deducerea nu se acordă", "danu")}
      ${camp("functie_baza", "Funcția de bază la acest angajator (fără ea nu se acordă deducerea personală — CF art. 77 alin. (1))", "danu")}
      ${camp("judet_casa", "Jude\u021b CAS/CASS", "text")}
      ${campCorLookup("sn", true)}
      ${camp("iban", "IBAN (cont salariu pe card)", "text")}
      ${camp("tichet_masa_valoare", "Tichet de mas\u0103 (lei/zi lucrat\u0103, 0 = f\u0103r\u0103)", "numar")}
      ${camp("scutit_contrib_minim", "Scutit contribu\u021bie minim\u0103", "danu")}
      ${campMotivScutire("sn-motiv_exceptare")}
      ${camp("tip_contract", "Tip contract", "select", { optiuni: [["nedeterminata", "nedeterminată"], ["determinata", "determinată"]] })}
      ${camp("nr_cim", "Nr. CIM", "text")}
      ${camp("data_cim", "Dată CIM", "data")}
    </div>
    <div id="sn-prapastie"></div>
    <p style="margin-top:12px">
      <button class="buton-primar" id="sn-salveaza" data-actiune="POST /tenants/{tenant_id}/salariati">Salveaz\u0103</button>
      <button class="buton-secundar" id="sn-gata" style="margin-left:6px">Gata, \u00eenapoi la list\u0103</button></p>
    <div id="sn-mesaj"></div>`;
  legaCorLookup(corp, "sn");  // [F137] lookup ocupatie COR
  legaMotivScutire(corp, "sn-scutit_contrib_minim", "sn-motiv_exceptare");   // [C133]
  // [267, clasa „formularele lungi”] salariatul nou rămâne completat la închidere / ieșirea din pagină și revine la redeschidere;
  // ciorna se șterge la salvare
  const _ciornaSal = ciornaFormular(corp, "iconta_ciorna_salariat:" + t.id,
    ["sn-nume", "sn-prenume", "sn-cnp", "sn-data_angajare", "sn-data_incetare", "sn-tip_norma", "sn-ore_zi", "sn-salariu_brut",
     "sn-persoane_intretinere", "sn-data_nastere", "sn-copii_scolarizati", "sn-declaratie_copii", "sn-functie_baza", "sn-judet_casa",
     "sn-iban", "sn-tichet_masa_valoare", "sn-scutit_contrib_minim", "sn-motiv_exceptare", "sn-cor", "sn-cor-cauta", "sn-tip_contract", "sn-nr_cim", "sn-data_cim"],
    { tenantId: t.id, formular: "salariat_nou" });   // [lotul 12, 495] ciorna pe server, pe utilizator + firmă
  // ciorna refăcută: câmpul motivului se arată după scutirea refăcută (butonul ales îl marchează mecanismul comun)
  const _laCiorna = () => { corp.querySelector("#sn-scutit_contrib_minim").dispatchEvent(new Event("change")); };
  _laCiorna();
  _ciornaSal.gata.then((ref) => { if (ref) _laCiorna(); });

  // [R49 (c)] Prapastia salariului minim, cu CIFRE. Nu se calculeaza in ecran (P3): ecranul
  // trimite elementele completate si afiseaza ce intoarce serverul. Apare INAINTE de buton
  // (DS cap.6, ghidaj preventiv), si dispare cand nu se aplica.
  const zonaPrapastie = corp.querySelector("#sn-prapastie");
  let ceasPrapastie = null;
  async function verificaPrapastia() {
    if (!zonaPrapastie) return;
    const brut = sumaRo(corp.querySelector("#sn-salariu_brut")) || 0;
    if (!(brut > 0)) { zonaPrapastie.innerHTML = ""; return; }
    let r;
    try {
      r = await api.post(`/tenants/${t.id}/prapastie-salariu`, {
        salariu_brut: brut,
        persoane_intretinere: sumaRo(corp.querySelector("#sn-persoane_intretinere")) || 0,
        data_nastere: corp.querySelector("#sn-data_nastere").value || null,
        copii_scolarizati: sumaRo(corp.querySelector("#sn-copii_scolarizati")) || 0,
        // previzualizare (nu scrie nimic): un DA/NU încă neales intră ca „nu” doar în calculul informativ al prăpastiei
        declaratie_copii: daNu(corp.querySelector("#sn-declaratie_copii")) === true,
        functie_baza: daNu(corp.querySelector("#sn-functie_baza")) === true,
        tip_norma: corp.querySelector("#sn-tip_norma").value,
        ore_zi: sumaRo(corp.querySelector("#sn-ore_zi")) || null,
        data_angajare: corp.querySelector("#sn-data_angajare").value || null,
        scutit_contrib_minim: daNu(corp.querySelector("#sn-scutit_contrib_minim")) === true,
        // [lotul 12, C133] fără motivul scutirii: netul nu depinde de el (scutirea intră prin bifă); îl primește salvarea, pentru D112
      });
    } catch (e) { zonaPrapastie.innerHTML = ""; return; }
    if (!r || !r.aplicabil) { zonaPrapastie.innerHTML = ""; return; }
    const brutIntrodus = sumaRo(corp.querySelector("#sn-salariu_brut"));
    zonaPrapastie.innerHTML = `<div class="caseta-atentie">
      <b>Peste salariul minim, netul scade.</b>
      La ${bani(r.prag)} lei brut, netul e <b>${bani(r.net_la_prag)}</b> lei.
      La ${bani(brutIntrodus)} lei brut, netul e
      <b>${bani(r.net_acum)}</b> lei — cu <b>${bani(r.pierdere)}</b> lei mai puțin.
      ${r.brut_egal ? `Netul redevine cel de la minim abia de la <b>${bani(r.brut_egal)}</b> lei brut.` : ""}
      <div class="tip-micut">${esc(r.temei || "")} · prag: ${esc(r.prag_temei || "")}</div>
    </div>`;
  }
  ["#sn-salariu_brut", "#sn-persoane_intretinere", "#sn-data_nastere", "#sn-copii_scolarizati",
   "#sn-declaratie_copii", "#sn-tip_norma", "#sn-ore_zi", "#sn-data_angajare",
   "#sn-scutit_contrib_minim", "#sn-functie_baza"].forEach((sel) => {
    const el = corp.querySelector(sel);
    if (el) el.addEventListener(el.tagName === "SELECT" ? "change" : "input", () => {
      clearTimeout(ceasPrapastie);
      ceasPrapastie = setTimeout(verificaPrapastia, 400);
    });
  });
  corp.querySelector("#sn-gata").addEventListener("click", () => nav.inapoiPas());
  corp.querySelector("#sn-salveaza").addEventListener("click", async () => {
    const zona = corp.querySelector("#sn-mesaj");
    const nume = corp.querySelector("#sn-nume").value.trim();
    const brut = sumaRo(corp.querySelector("#sn-salariu_brut"));
    curataEroriCamp(corp);  // [G10 cap.6 v2.30] eroare langa camp
    // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite; [lotul 11, 440] alegerile și câmpurile lipsă se marchează DEODATĂ, apoi un `return`
    let lipsa = false; if (cereAlegerile(corp, ["#sn-tip_norma", "#sn-declaratie_copii", "#sn-functie_baza", "#sn-scutit_contrib_minim", "#sn-motiv_exceptare"])) lipsa = true;
    if (cereCompletate(corp, [{ id: "sn-nume", mesaj: "Numele este obligatoriu." },
                              { id: "sn-cnp", mesaj: "CNP-ul este obligatoriu — D112 declară salariatul după CNP." }])) lipsa = true;
    // [lotul 11, 454] CNP-ul completat, dar greșit, se spune la aceeași salvare cu celelalte (nu după răspunsul serverului)
    const _cnpSn = corp.querySelector("#sn-cnp").value.trim();
    if (_cnpSn && !cnpValid(_cnpSn)) { eroareCamp(corp, "sn-cnp", "CNP invalid (13 cifre, cifră de control greșită)."); lipsa = true; }
    if (Number.isNaN(brut)) { eroareCamp(corp, "sn-salariu_brut", MESAJ_NUMAR_RO); lipsa = true; }
    else if (!brut || !(brut > 0)) { eroareCamp(corp, "sn-salariu_brut", "Salariul brut este obligatoriu și trebuie să fie mai mare ca 0."); lipsa = true; }  // [#8]
    // [lotul 13, 655] numerele scrise în format românesc; unul care nu se poate citi fără ghicit se spune lângă câmpul lui, cu celelalte
    const [_ore, _pers, _copii, _tichet] = ["sn-ore_zi", "sn-persoane_intretinere", "sn-copii_scolarizati", "sn-tichet_masa_valoare"]
      .map((id) => sumaRo(corp.querySelector("#" + id)));
    [["sn-ore_zi", _ore], ["sn-persoane_intretinere", _pers], ["sn-copii_scolarizati", _copii], ["sn-tichet_masa_valoare", _tichet]]
      .forEach(([id, v]) => { if (Number.isNaN(v)) { eroareCamp(corp, id, "Scrie un număr, cu virgulă la zecimale."); lipsa = true; } });
    if (!corp.querySelector("#sn-cor").value.trim()) { eroareCamp(corp, "sn-cor-cauta", "Alege ocupația (cod COR) din listă — obligatorie pentru D112/REGES."); lipsa = true; }  // [#7]
    if (lipsa) return;
    const corpReq = {
      nume,
      prenume: corp.querySelector("#sn-prenume").value.trim() || null,
      cnp: corp.querySelector("#sn-cnp").value.trim() || null,
      data_angajare: corp.querySelector("#sn-data_angajare").value || null,
      data_incetare: corp.querySelector("#sn-data_incetare").value || null,
      tip_norma: corp.querySelector("#sn-tip_norma").value,
      ore_zi: _ore,
      salariu_brut: brut || 0,
      persoane_intretinere: _pers || 0,
      data_nastere: corp.querySelector("#sn-data_nastere").value || null,
      copii_scolarizati: _copii || 0,
      declaratie_copii: daNu(corp.querySelector("#sn-declaratie_copii")),
      judet_casa: corp.querySelector("#sn-judet_casa").value.trim() || null,
      cor: corp.querySelector("#sn-cor").value.trim() || null,
      iban: corp.querySelector("#sn-iban").value.trim().replace(/\s/g, "").toUpperCase() || null,  // [F134]
      tichet_masa_valoare: _tichet || 0,  // [F133]
      scutit_contrib_minim: daNu(corp.querySelector("#sn-scutit_contrib_minim")),
      motiv_exceptare: motivAles(corp, "sn-motiv_exceptare"),   // [C133] numai cu scutirea „Da”
      functie_baza: daNu(corp.querySelector("#sn-functie_baza")),  // [3c · CF art.77(1)] deducerea doar la functia de baza
      // [412] contractul individual de muncă pe fișă (Codul muncii art.12, art.16): adeverința le precompletează
      tip_contract: corp.querySelector("#sn-tip_contract").value || null,
      nr_cim: corp.querySelector("#sn-nr_cim").value.trim() || null,
      data_cim: corp.querySelector("#sn-data_cim").value || null,
    };
    try {
      await api.post(`/tenants/${t.id}/salariati`, corpReq);
      _ciornaSal.sterge();
      if (dupaSalvare) dupaSalvare();
      formularSalariatNou(corp, nav, t, dupaSalvare);
      arataMesaj(corp.querySelector("#sn-mesaj"), `Salariat salvat: ${nume}. Poți adăuga altul sau te întorci la statul de plată.`, "ok");
    } catch (e) {
      curataEroriCamp(corp);
      // [G10 rule2/4] erorile per-camp din contractul backend (`sn-` + numele); [lotul 11, 440] toate, iar cele fără câmp pe ecran în zonă
      const _ec = (e && e.erori_campuri) || [];
      arataRefuzul(corp, e && e.mesaj ? e : { ...(e || {}), mesaj: "eroare la salvare" }, zona,
        { campuri: Object.fromEntries(_ec.map((x) => [x.camp, x.camp === "cor" ? "sn-cor-cauta" : "sn-" + x.camp])) });   // [454] COR: câmpul vizibil al căutării, nu cel ascuns
    }
  });
}

// [control_firma_v1 + consolidat 24.07] Control fiscal per firma. Corpul verdictului (declaratii + TOATE
// verificarile contabile) e randat de control_verdict.js — renderer UNIC, acelasi cu ecranul Control fiscal
// (detaliuFirma). Inainte, aceasta functie citea un subset hardcodat din verificari_contabile (echilibru/
// tva/documente) si nu atingea cross-check-urile -> constatarile BLOCANTE pe salarii/trezorerie nu apareau
// (cazul DANTE 24.07). Aici raman doar anteta (semafor mare) + delegarea. Vezi DESIGN_SYSTEM cap.20.
async function ecranControlFirma(corp, nav, t) {
  corp.innerHTML = `<p class="ecran-nota">Se evaluează situația fiscală...</p>`;
  let d;
  try {
    d = await api.get(`/control-fiscal/${t.id}`);
  } catch (e) {
    corp.innerHTML = `<p class="msg-eroare">${esc((e && e.mesaj) || "Nu s-a putut evalua controlul fiscal.")}</p>`;
    return;
  }
  const cul = CULORI_VERDICT[d.stare] || CULORI_VERDICT.gri;
  corp.innerHTML = `
    <h2 class="pf-titlu">Control fiscal ${semnAjutor("F022")}</h2>
    <p class="pf-intro">Situația fiscală a firmei: ce s-a depus vs ce e datorat, cu verificări de coerență.</p>
    <div class="cf-stare-mare" style="background:${cul.bg}">
      <span class="cf-dot" style="background:${cul.dot}"></span>
      <span class="cf-stare-txt">${etichetaStare(d.stare)}</span>
      <span class="cf-stare-cifre tip-micut">${cate(d.datorate || 0, "datorată", "datorate")} · ${cate(d.depuse || 0, "depusă", "depuse")}</span>
    </div>
    ${randeazaCorpVerdict(d, { mod: "fisa" })}`;
  legaVerdict(corp, nav, { tenant_id: t.id, nume: t.nume, reincarca: () => ecranControlFirma(corp, nav, t) });
}
// ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
// [lotul 13, comanda Costin 13.1] SALARIZAREA: statul de plată (677), fereastra salariatului (673–676), pontajul (671, 678), primele /
// sporurile / orele suplimentare (679), „+ masă” (672).
//   677: „tabel compact, un rând pe salariat (nume, zile lucrate, brut, net, cost, semnele lunii: CM, concediu, de verificat), rând de
//        total, căutare deasupra […] Rândul deschide fereastra salariatului, cât ecranul, cu toate butoanele (675) și compoziția netului în
//        trei coloane”;
//   673: „orice acțiune din orice fereastră: deschide o fereastră nouă, centrată; fereastra de lucru (formular, detalii) ocupă ecranul ca
//        fereastra cu tabel, fără derulare; fereastra mică rămâne doar pentru confirmări; explicația din fereastră are cel mult o frază”
//        -> fiecare acțiune a statului și a salariatului se deschide cu `nav.deschide(…, { lat: "tabel" })`, nu într-o zonă din pagină;
//   674: orice acțiune e un buton (fără „▸ Compoziția netului” pe care se dă clic: compoziția stă deschisă în fereastra salariatului);
//   675: „entitățile de același tip (salariați…) au același set de butoane, în aceeași ordine; ce nu se aplică stă inactiv, cu motivul la
//        trecerea cu mouse-ul. Nicio setare care schimbă cifre nu stă ascunsă într-un formular de corectare. La salariat: + masă, alături de
//        + vacanță, + cadou, + cultural, + creșă” -> `BUTOANE_SALARIAT`; setările care schimbă cifrele stau în „Date de calcul” și în
//        butoanele lor (Salariu, + masă), cu valorile la vedere („Din ce se calculează”); „Corectează datele” ține numai identitatea și CIM-ul;
//   676: listele de cel mult 6 opțiuni sunt butoane alăturate (`selectScurt` / `selectDaNu`, prin mecanismul comun `alegereButoane` din api.js).
// Luna aleasă a statului se ține pe firmă (`LUNA_STAT`): închiderea ferestrei salariatului redesenează statul pe aceeași lună.
const LUNA_STAT = {};
function _lunaStat(t) {
  const azi = new Date();
  if (!LUNA_STAT[t.id]) LUNA_STAT[t.id] = { an: azi.getFullYear(), luna: azi.getMonth() + 1 };
  return LUNA_STAT[t.id];
}
const _lunaTxt = (an, luna) => dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric");
// confirmarea unui act făcut într-o fereastră a salariatului, arătată în fereastra salariatului când se redesenează (DS cap.27)
const CONFIRMARI_SALARIAT = {};
// suma în lei pentru totaluri: în bani întregi, ca adunarea să nu aducă zgomot de virgulă mobilă (valorile vin cu cel mult 2 zecimale)
const _bani100 = (v) => Math.round(Number(v || 0) * 100);

// F135 + [lotul 13, 671 / 678]: pontajul lunii = un calendar compact pe un ecran (rânduri pe săptămâni, coloane luni–vineri), implicit
// „prezent”; contabilul alege ce marchează și apasă doar zilele care sunt altfel. Concediul medical vine din certificate, suspendările din
// „Suspendare / CFP”: zilele lor apar marcate și nu se schimbă de aici (serverul le refuză, `pontaj.seteaza`). Regula (ce schimbă pontajul,
// ce așteaptă confirmarea) vine de la server (`pontaj.REGULA_PONTAJ`) — aceeași frază ca în statul de plată.
const MARCAJE_PONTAJ = [["concediu_odihna", "concediu de odihnă"], ["delegatie", "delegație"], ["absent_motivat", "absent motivat"],
  ["absent_nemotivat", "absent nemotivat"], ["invoire", "învoire"], ["prezent", "prezent"]];
async function ecranPontaj(corp, nav, t, sid, nume, an, luna) {
  const cerereNoua = ultimaCerere();   // [C103] luna schimbată în șir sau zilele pontate una după alta: numai pontajul cerut ultimul ajunge pe ecran
  let marcaj = "";   // nimic ales la deschidere (cap.17): contabilul alege ce marchează
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă pontajul…</p>`;
    const actuala = cerereNoua();
    let g;
    try { g = await api.get(`/tenants/${t.id}/salariati/${sid}/pontaj?an=${an}&luna=${luna}`); if (!actuala()) return; }
    catch { if (!actuala()) return; corp.innerHTML = `<p class="ecran-nota">Nu s-a putut încărca pontajul.</p>`; return; }
    const rez = g.rezumat || {};
    const zile = g.zile || [];
    // săptămânile lunii, de luni până vineri (sâmbăta și duminica nu se pontează)
    const saptamani = [];
    let sapt = null;
    zile.forEach((z) => {
      if (z.zi_saptamana > 4) return;
      if (!sapt || z.zi_saptamana === 0) { sapt = [null, null, null, null, null]; saptamani.push(sapt); }
      sapt[z.zi_saptamana] = z;
    });
    const celula = (z) => {
      if (!z) return "<td></td>";
      const altfel = z.stare !== "prezent";
      const txt = `${String(z.zi_nr).padStart(2, "0")}<br><span class="tip-micut">${esc(z.eticheta)}</span>`;
      if (!z.editabil) {
        return `<td><button type="button" class="buton-secundar pj-zi-blocata" data-zi="${z.zi}" data-stare="${esc(z.stare)}" disabled title="${esc((z.afirmatie && z.afirmatie.motiv) || "")}" style="width:100%">${txt}</button></td>`;
      }
      return `<td><button type="button" class="pj-zi buton-secundar${altfel ? " buton-activ" : ""}" data-zi="${z.zi}" data-stare="${esc(z.stare)}" aria-pressed="${altfel}" data-actiune-camp="PUT /tenants/{tenant_id}/salariati/{salariat_id}/pontaj" title="${esc((z.afirmatie && z.afirmatie.motiv) || z.eticheta)}" style="width:100%">${txt}</button></td>`;
    };
    const pc = g.perioada_confirmata || {};
    const dataConf = pc.confirmat_la ? dataRo(String(pc.confirmat_la).slice(0, 10)) : "";
    corp.innerHTML = `
      <div class="rezumat-fix">
        <h2 class="pf-titlu">Pontaj · ${_lunaTxt(an, luna)}</h2>
        <p class="pf-intro"><button class="buton-secundar" id="pj-prev">← luna</button>
          <button class="buton-secundar" id="pj-next">luna →</button>
          ${pc.confirmat ? `<span class="cf-pastila" style="margin-left:12px"><span style="color:var(--verde)">●</span> confirmat${dataConf ? " la " + dataConf : ""}</span>`
            : `<button class="buton-verde" id="pj-confirma" style="margin-left:12px" data-actiune="POST /tenants/{tenant_id}/pontaj/confirma">Confirmă pontajul lunii</button>`}</p>
        <div class="cf-sumar">
          <span class="cf-pastila">${cate(rez.prezent || 0, "zi de prezență", "zile de prezență")}</span>
          <span class="cf-pastila">${cate(rez.concediu_medical || 0, "zi de concediu medical", "zile de concediu medical")}</span>
          <span class="cf-pastila">${cate(rez.concediu_odihna || 0, "zi de concediu de odihnă", "zile de concediu de odihnă")}</span>
          <span class="cf-pastila">${cate((rez.absent_motivat || 0) + (rez.absent_nemotivat || 0), "zi de absență", "zile de absență")}</span>
          <span class="cf-pastila">${cate(rez.invoire || 0, "zi de învoire", "zile de învoire")} · ${cate(rez.delegatie || 0, "zi de delegație", "zile de delegație")}</span>
          ${(rez.cfp || 0) + (rez.suspendare || 0) ? `<span class="cf-pastila">${cate((rez.cfp || 0) + (rez.suspendare || 0), "zi fără plată", "zile fără plată")}</span>` : ""}
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center"><span class="camp-eticheta">Marchează ca:</span>
          ${selectScurt("pj-marcaj", MARCAJE_PONTAJ, marcaj, "Ce marchezi pe zilele apăsate")}</div>
        <div id="pj-msg"></div>
      </div>
      <div class="caseta-info"><span class="ci-mesaj">${esc(g.regula || "")}</span></div>
      ${(g.avertismente || []).map((a) => `<div class="caseta-atentie"><span class="ca-mesaj">${esc(a)}</span></div>`).join("")}
      <table class="fd-tabel" id="pj-calendar" style="table-layout:fixed">
        <thead><tr><th>Luni</th><th>Marți</th><th>Miercuri</th><th>Joi</th><th>Vineri</th></tr></thead>
        <tbody>${saptamani.map((s) => `<tr>${s.map(celula).join("")}</tr>`).join("")}</tbody>
      </table>`;
    corp.querySelector("#pj-marcaj").addEventListener("change", (e) => { marcaj = e.target.value; });
    corp.querySelector("#pj-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#pj-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    const btnConf = corp.querySelector("#pj-confirma");
    if (btnConf) btnConf.addEventListener("click", () => confirmaCaseta(btnConf,
      "Confirmi pontajul lunii? Tichetele de masă se calculează pe zilele lui; o modificare ulterioară îl de-confirmă.",
      async () => {
        try { await api.post(`/tenants/${t.id}/pontaj/confirma`, { an, luna }); deseneaza(); }
        catch (e) { arataMesaj(corp.querySelector("#pj-msg"), (e && e.mesaj) || "Pontajul nu s-a confirmat.", "eroare"); }
      }));
    corp.querySelectorAll(".pj-zi").forEach((b) => b.addEventListener("click", async () => {   // zilele inactive nu primesc clicul
      const msg = corp.querySelector("#pj-msg");
      if (!marcaj) { arataMesaj(msg, "Alege întâi ce marchezi (butoanele de deasupra calendarului), apoi apasă zilele.", "eroare"); return; }
      // a doua apăsare pe o zi deja marcată așa o readuce la „prezent”
      const stare = b.dataset.stare === marcaj ? "prezent" : marcaj;
      try { await api.put(`/tenants/${t.id}/salariati/${sid}/pontaj`, { zi: b.dataset.zi, stare }); deseneaza(); }
      catch (e) { arataMesaj(msg, (e && e.mesaj) || "Ziua nu s-a marcat.", "eroare"); }
    }));
  };
  deseneaza();
}

// F136: formular adeverinta salariat -> PDF (art. 34(5) Codul muncii)
function formularAdeverinta(corp, nav, t, sid, nume, an, luna, cor = "") {
  corp.innerHTML = `
    <h2 class="pf-titlu">Adeverință ${semnAjutor("F136")}</h2>
    <p class="pf-intro">Pentru ${esc(nume || "salariat")}: datele firmei, ale salariatului și salariul se completează din aplicație.</p>
    <div class="caseta-atentie" style="margin:0 0 12px"><span class="ca-mesaj">Pentru credit bancar, băncile cer de obicei formularul propriu — un PDF generic nu e acceptat. Din 2026 verifică veniturile direct la ANAF.</span></div>
    <div class="grila-campuri">
      <label class="camp"><span class="camp-eticheta">Scopul<span class="oblig">*</span></span><input id="ad-scop" class="camp-input" placeholder="ex. grădiniță, notar, instanță"></label>
      <label class="camp"><span class="camp-eticheta">Funcția</span><input id="ad-functie" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Departament</span><input id="ad-dept" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Serie CI</span><input id="ad-serieci" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Nr. CI</span><input id="ad-nrci" class="camp-input"></label>
      <div class="camp"><span class="camp-eticheta">Tip contract<span class="oblig">*</span></span>${selectScurt("ad-tip", TIPURI_CIM, "", "Tip contract")}</div>
      <label class="camp"><span class="camp-eticheta">Nr. CIM</span><input id="ad-nrcim" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Dată CIM</span><input type="date" id="ad-datacim" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Vechime în muncă</span><input id="ad-vm" class="camp-input" placeholder="ex. 8 ani 3 luni"></label>
      <label class="camp"><span class="camp-eticheta">Vechime specialitate</span><input id="ad-vs" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Nr. ieșire</span><input id="ad-nr" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Data ieșirii</span><input type="date" id="ad-data" class="camp-input"></label>
    </div>
    <label class="camp" style="max-width:820px;margin-top:10px"><span class="camp-eticheta">Mențiuni (opțional)</span><textarea id="ad-mentiuni" class="camp-input" rows="2"></textarea></label>
    <div class="bara-fixa"><p style="margin-top:14px"><button class="buton-primar" id="ad-gen" data-actiune="POST /tenants/{tenant_id}/salariati/{salariat_id}/adeverinta">Generează PDF</button> <button class="buton-secundar" id="ad-renunta" style="margin-left:8px">Renunță</button></p>
    <div id="ad-msg"></div></div>`;
  corp.querySelector("#ad-renunta").addEventListener("click", () => nav.inapoi());
  // [deficiența 412] funcția din fișa salariatului: denumirea ocupației COR a lui (nomenclatorul COR), precompletată și modificabilă
  if (cor) api.get(`/cor?q=${encodeURIComponent(cor)}`).then((r) => {
    const o = ((r && (r.ocupatii || r.rezultate)) || (Array.isArray(r) ? r : [])).find((x) => String(x.cod) === String(cor));
    const f = corp.querySelector("#ad-functie");
    if (o && f && !f.value) f.value = o.denumire || "";
  }).catch(() => {});
  // [deficiența 412] tipul contractului și Nr. / Dată CIM din fișa salariatului (salariati.tip_contract / nr_cim / data_cim),
  // precompletate și modificabile; ce a scris deja omul nu se suprascrie
  api.get(`/tenants/${t.id}/salariati/${sid}`).then((d) => {
    if (!d) return;
    const tip = corp.querySelector("#ad-tip"), nr = corp.querySelector("#ad-nrcim"), dt = corp.querySelector("#ad-datacim");
    if (tip && d.tip_contract && !tip.value) tip.value = d.tip_contract;
    if (nr && d.nr_cim && !nr.value) nr.value = d.nr_cim;
    if (dt && d.data_cim && !dt.value) dt.value = String(d.data_cim).slice(0, 10);
  }).catch(() => {});
  corp.querySelector("#ad-gen").addEventListener("click", async () => {
    const msg = corp.querySelector("#ad-msg");
    const val = (id) => corp.querySelector(id).value.trim();
    curataEroriCamp(corp);
    let lipsa = cereCompletate(corp, [{ id: "ad-scop", mesaj: "Completează scopul adeverinței." }]);
    if (cereAlegerile(corp, ["#ad-tip"])) lipsa = true;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    if (lipsa) return;
    const body = {
      scop: val("#ad-scop"), functie: val("#ad-functie"), departament: val("#ad-dept"),
      serie_ci: val("#ad-serieci"), nr_ci: val("#ad-nrci"), tip_contract: corp.querySelector("#ad-tip").value,
      nr_cim: val("#ad-nrcim"), data_cim: corp.querySelector("#ad-datacim").value || null,
      vechime_munca: val("#ad-vm"), vechime_specialitate: val("#ad-vs"),
      nr_iesire: val("#ad-nr"), data_iesire: corp.querySelector("#ad-data").value || null,
      mentiuni: val("#ad-mentiuni"), an, luna,
    };
    const btn = corp.querySelector("#ad-gen"); btn.disabled = true; btn.textContent = "Se generează…";
    try {
      await deschide(`/tenants/${t.id}/salariati/${sid}/adeverinta`, { metoda: "POST", corp: body });
      arataMesaj(msg, "Adeverință generată.", "ok");
    } catch (e) { arataMesaj(msg, (e && (e.mesaj || e.message)) || "eroare", "eroare"); }   // [R131]
    finally { btn.disabled = false; btn.textContent = "Generează PDF"; }
  });
}

const TIPURI_CIM = [["nedeterminata", "nedeterminată"], ["determinata", "determinată"]];
const NORME = [["intreaga", "întreagă (8 ore)"], ["partiala", "parțială"]];

// [lotul 13, 677] Compoziția netului pe trei coloane — venituri / rețineri / rezultat —, gata compusă de server
// (`stat_plata_api.compozitie_coloane`, din aceleași câmpuri ca fluturașul); ecranul o așază, nu o recalculează. Stă deschisă în fereastra
// salariatului (674: fără „▸ Compoziția netului” pe care se dă clic).
function compozitieColoane(s) {
  const c = s.compozitie_coloane;
  if (!c) return "";
  const rand = (x) => {
    const suma = x.valoare == null ? "" : `${bani(x.valoare)} lei${x.net != null ? ` · net ${bani(x.net)} lei` : ""}`;
    const et = `${esc(x.eticheta)}${x.detaliu ? `<span class="tip-micut"> · ${esc(x.detaliu)}</span>` : ""}`;
    const date = ` data-eticheta="${esc(x.eticheta)}" data-valoare="${x.valoare == null ? "" : x.valoare}"${x.net != null ? ` data-net="${x.net}"` : ""}`;
    if (x.fel === "total" || x.fel === "subtotal") return `<tr${date}><td><b>${et}</b></td><td class="fd-td-num"><b>${suma}</b></td></tr>`;
    if (x.fel === "info") return `<tr${date}><td style="color:var(--gri)">${et}</td><td class="fd-td-num" style="color:var(--gri)">${suma}</td></tr>`;
    return `<tr${date}><td>${et}</td><td class="fd-td-num">${suma}</td></tr>`;
  };
  const col = (titlu, lista, id) => `<table class="fd-tabel" id="${id}"><thead><tr><th>${titlu}</th><th class="fd-td-num">Suma</th></tr></thead>
    <tbody>${lista.map(rand).join("")}</tbody></table>`;
  return `<div class="grila-doc" id="ss-compozitie" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr));align-items:start">
    ${col("Venituri", c.venituri || [], "ss-venituri")}${col("Rețineri", c.retineri || [], "ss-retineri")}${col("Rezultat", c.rezultat || [], "ss-rezultat")}</div>`;
}

// [lotul 13, 675] Butoanele salariatului: ACELAȘI set, în aceeași ordine, la fiecare salariat; ce nu se aplică stă inactiv, cu motivul la
// trecerea cu mouse-ul (`title`). Cheia = atributul `data-<cheie>` al butonului (= id-ul salariatului).
function butoaneSalariat(s, regesOk) {
  const nume = s.nume;
  // ce nu se aplică: `atributeInactiv` (DS cap.1, 675) — rămâne focusabil, motivul la trecerea cu mouse-ul (un `disabled` nu arată `title`)
  const b = (cheie, text, actiune, opt = {}) => `<button class="buton-secundar" data-${cheie}="${s.id}" data-nume="${esc(nume)}"`
    + `${actiune ? ` data-actiune="${actiune}"` : ""}${opt.inactiv ? atributeInactiv(opt.inactiv) : (opt.titlu ? ` title="${esc(opt.titlu)}"` : "")}>${text}</button>`;
  const dv = (s.de_verificat || []).length;
  return [
    `<button class="buton-primar" data-flut="${s.id}" data-nume="${esc(nume)}" data-actiune="GET /tenants/{tenant_id}/fluturas/{salariat_id}">Fluturaș</button>`,
    b("pontaj", "Pontaj", ""),   // deschide pontajul (citire); scrierea e pe zilele lui
    b("cm", "Concediu medical", ""),   // deschide lista certificatelor; „+ Certificat nou” poartă scrierea
    b("susp", (s.suspendari || []).length ? `Suspendare / CFP (${s.suspendari.length})` : "Suspendare / CFP", "PUT /tenants/{tenant_id}/salariati/{salariat_id}"),
    b("elem", `Prime, sporuri, ore supl.${(s.elemente || []).length ? ` (${s.elemente.length})` : ""}`, "POST /tenants/{tenant_id}/salariati/{salariat_id}/elemente"),
    b("salariu", "Salariu", "PUT /tenants/{tenant_id}/salariati/{salariat_id}"),
    b("masa", "+ masă", "PUT /tenants/{tenant_id}/salariati/{salariat_id}"),
    b("vac", "+ vacanță", "PUT /tenants/{tenant_id}/salariati/{salariat_id}/beneficiu-lunar"),
    b("cadou", "+ cadou", "PUT /tenants/{tenant_id}/salariati/{salariat_id}/beneficiu-lunar"),
    b("cult", "+ cultural", "PUT /tenants/{tenant_id}/salariati/{salariat_id}/beneficiu-lunar"),
    b("cresa", "+ creșă", "PUT /tenants/{tenant_id}/salariati/{salariat_id}/beneficiu-lunar"),
    b("calcul", "Date de calcul", "PUT /tenants/{tenant_id}/salariati/{salariat_id}"),
    b("date", "Corectează datele", "PUT /tenants/{tenant_id}/salariati/{salariat_id}"),
    b("iban", `IBAN ${s.iban ? "✓" : "⚠"}`, "PUT /tenants/{tenant_id}/salariati/{salariat_id}"),
    b("cor", `COR ${s.cor ? "✓" : "⚠"}`, "PUT /tenants/{tenant_id}/salariati/{salariat_id}"),
    b("incet", s.data_incetare ? "Plecat " + dataRo(s.data_incetare) : "Încetare", "PUT /tenants/{tenant_id}/salariati/{salariat_id}"),
    b("adev", "Adeverință", ""),   // deschide formularul; „Generează PDF” poartă acțiunea
    b("reges", "REGES", "POST /tenants/{tenant_id}/reges-trimite-salariat",
      { inactiv: regesOk ? "" : "Cheile REGES nu sunt configurate: se pun din statul de plată, cu „Chei REGES”." }),
    b("verif", dv ? `De verificat (${dv})` : "De verificat", "PUT /tenants/{tenant_id}/salariati/{salariat_id}",
      { inactiv: dv ? "" : "Salariatul nu are date importate de confirmat." }),
  ].join("");
}

// „Din ce se calculează”: setările salariatului care schimbă cifrele statului, la vedere (675: niciuna ascunsă într-un formular de corectare)
function dinCeSeCalculeaza(s) {
  const dn = (v) => (v === true ? "da" : (v === false ? "nu" : "necompletat"));
  const f = [
    ["Salariul de bază (contract)", s.salariu_baza ? `${bani(s.salariu_baza)} lei` : "lipsește"],
    ["Norma", s.tip_norma === "partiala" ? `parțială, ${cate(Number(s.ore_zi || 0), "oră", "ore")} pe zi` : "întreagă"],
    ["Angajat la", s.data_angajare ? dataRo(s.data_angajare) : "necompletat"],
    ["Funcția de bază", dn(s.functie_baza)],
    ["Persoane în întreținere", String(s.persoane_intretinere || 0)],
    ["Data nașterii", s.data_nastere ? dataRo(s.data_nastere) : "necompletată"],
    ["Copii școlarizați", `${s.copii_scolarizati || 0}${s.copii_scolarizati ? ` (declarația: ${dn(s.declaratie_copii)})` : ""}`],
    ["Scutit de contribuția minimă", dn(s.scutit_contrib_minim)],
    ["Tichet de masă", Number(s.tichet_masa_valoare) > 0 ? `${bani(s.tichet_masa_valoare)} lei pe zi lucrată` : "fără"],
  ];
  return `<table class="fd-tabel" id="ss-calcul"><tbody>${f.map(([e, v]) => `<tr><td>${esc(e)}</td><td><b>${esc(v)}</b></td></tr>`).join("")}</tbody></table>`;
}

export async function ecranSalariati(corp, nav, t) {   // exportat: garda S2 în browser (ca ecranStocuri)
  const L = _lunaStat(t);
  const cerereNoua = ultimaCerere();   // [C103] luna schimbată în șir (← / →): numai statul lunii afișate ajunge pe ecran
  let filtru = "";
  const deseneaza = async () => {
    const { an, luna } = L;
    corp.innerHTML = `<p class="ecran-nota">Se calculează...</p>`;
    const actuala = cerereNoua();
    let r;
    try {
      r = await api.get(`/tenants/${t.id}/stat-plata?an=${an}&luna=${luna}`);
      if (!actuala()) return;
    } catch (e) { if (!actuala()) return; corp.innerHTML = `<p class="ecran-nota">Nu s-a putut încărca statul de plată. ${esc((e && (e.mesaj || e.message)) || "")}</p>`; return; }  // [#1/#3] mesaj real, nu catch gol
    const stat = (r && r.stat) || [];
    const areIban = stat.some((s) => s.iban);  // [dec2 Costin] SEPA cere macar un IBAN
    const regesOk = !!(r && r.reges_configurat);  // [dec2 Costin] REGES cere chei configurate
    const notaSalarii = (r && r.nota_salarii) || null;  // [lotul 07.10 pct.15] nota lunii și starea ei în coada de validare
    const pontajNeconf = stat.some((s) => s.pontaj_neconfirmat);  // [#1/#3] statul se afiseaza; tichete blocate
    const total = (k) => stat.reduce((a, s) => a + _bani100(s[k]), 0) / 100;
    const semne = (s) => (s.semne || []).map((x) => `<span class="cf-pastila" title="${esc(x.titlu || "")}"${x.cod === "verifica" ? ' style="color:var(--rosu);font-weight:600"' : ""}>${esc(x.text)}</span>`).join(" ");
    const randuri = stat.map((s) => `<tr class="sp-rand" data-sid="${s.id}" data-nume="${esc(s.nume)}">
        <td><button class="btn-link sp-deschide" data-sal="${s.id}" data-fara-actiune="deschide fereastra salariatului">${esc(s.nume)}</button></td>
        <td class="fd-td-num">${s.zile_lucrate != null ? `${s.zile_lucrate} din ${s.zile_lucratoare_luna}` : ""}</td>
        <td class="fd-td-num">${bani(s.brut)}</td>
        <td class="fd-td-num"><b>${bani(s.net_de_plata != null ? s.net_de_plata : s.net)}</b></td>
        <td class="fd-td-num">${bani(s.cost_total != null ? s.cost_total : s.cost)}</td>
        <td>${semne(s)}</td></tr>`).join("");
    // [lotul 10, 421/424] luna și acțiunile statului lipite sus (fereastra cu tabel: rezumatul fix sus, numai conținutul derulează);
    // [lotul 13, 673] fiecare acțiune a statului se deschide într-o fereastră nouă
    corp.innerHTML = `
      <div class="rezumat-fix">
      <h2 class="pf-titlu">Stat de plată ${semnAjutor("F080")}</h2>
      <p class="pf-intro">Luna ${_lunaTxt(an, luna)}
        <button class="buton-secundar" id="sp-prev" style="margin-left:12px">← luna</button>
        <button class="buton-secundar" id="sp-next">luna →</button>
        <button class="buton-primar" id="sp-salariat-nou" data-actiune="POST /tenants/{tenant_id}/salariati" style="margin-left:12px">+ Salariat nou</button>
        <button class="buton-secundar" id="sp-contare" data-actiune="POST /tenants/{tenant_id}/salarii-contare/propunere">Contabilizează statul</button>
        <button data-actiune="POST /tenants/{tenant_id}/plata-salarii-fisier" class="buton-secundar" id="sp-plata-card"${areIban ? "" : " disabled"}>Fișier plată card (SEPA)</button>
        <button data-actiune="POST /tenants/{tenant_id}/reges-config" class="buton-secundar" id="sp-reges-cfg">Chei REGES</button>
        <button class="buton-secundar" id="sp-reges-poll" data-actiune="POST /tenants/{tenant_id}/reges-poll"${regesOk ? "" : " disabled"}>Răspunsuri REGES</button></p>
      ${stat.length ? `<input type="search" id="sp-cauta" class="camp-input" style="max-width:340px" placeholder="Caută salariatul" aria-label="Caută salariatul" autocomplete="off" value="${esc(filtru)}">` : ""}
      <div id="sp-msg"></div>
      </div>
      <div id="sp-contare-zona"></div>
      ${!areIban && stat.length ? `<div class="caseta-info"><span class="ci-mesaj">Fișierul de plată pe card (SEPA) e indisponibil: niciun salariat nu are IBAN completat. IBAN-ul se pune din fereastra salariatului, butonul „IBAN ⚠”.</span></div>` : ""}
      ${/* [deficiența 11, retestul Costin 09.10] caseta numai cui vede „Răspunsuri REGES”; trimiterea la „Chei REGES” numai cui are butonul */ ""}
      ${!regesOk && permis("POST /tenants/{tenant_id}/reges-poll") ? `<div class="caseta-info"><span class="ci-mesaj">„Răspunsuri REGES" e indisponibil: cheile REGES nu sunt configurate încă. ${permis("POST /tenants/{tenant_id}/reges-config") ? "Configurează-le cu butonul „Chei REGES”." : "Le configurează administratorul cabinetului."}</span></div>` : ""}
      ${pontajNeconf ? `<div class="caseta-info"><span class="ci-mesaj"><span style="color:var(--gri)">●</span> Pontajul lunii ${_lunaTxt(an, luna)} nu e confirmat. ${esc((stat.find((s) => s.regula_pontaj) || {}).regula_pontaj || "")}</span></div>` : ""}
      ${!stat.length ? `<div class="stare-goala">Niciun salariat activ încă.</div>` : `
      <table class="fd-tabel" id="sp-tabel">
        <thead><tr><th>Salariat</th><th class="fd-td-num">Zile lucrate</th><th class="fd-td-num">Brut</th><th class="fd-td-num">Net de plată</th><th class="fd-td-num">Cost angajator</th><th>Semnele lunii</th></tr></thead>
        <tbody>${randuri}</tbody>
        <tfoot><tr><td><b>Total</b> · ${cate(stat.length, "salariat", "salariați")}</td><td></td><td class="fd-td-num"><b>${bani(total("brut"))}</b></td>
          <td class="fd-td-num"><b>${bani(stat.reduce((a, s) => a + _bani100(s.net_de_plata != null ? s.net_de_plata : s.net), 0) / 100)}</b></td>
          <td class="fd-td-num"><b>${bani(stat.reduce((a, s) => a + _bani100(s.cost_total != null ? s.cost_total : s.cost), 0) / 100)}</b></td><td></td></tr></tfoot>
      </table>`}`;
    const zonaContare = corp.querySelector("#sp-contare-zona");
    // [lotul 07.10 pct.15, comanda Costin 06.10.2026] „Respingerea apare pe statul de plată abia după «Contabilizează statul»; se
    // vede la deschiderea statului.” Starea notei vine odată cu statul (`nota_salarii`), deci se arată fără niciun clic.
    if (notaSalarii && notaSalarii.validare && notaSalarii.validare.stare_coada === "respinsa") {
      zonaContare.innerHTML = `<div class="caseta-atentie"><div class="ca-mesaj">Nota de salarii ${esc(notaSalarii.nota_eticheta || "")} a fost respinsă la validare: ${esc(motivInFraza(notaSalarii.validare.motiv_respingere))} Se corectează din statul de plată, nu din Registrul-jurnal: corectează salariații, pontajul sau contractele, apoi «Contabilizează statul» › «Recontabilizează statul» — nota respinsă se înlocuiește și pleacă din nou la validare.</div></div>`;
    } else if (notaSalarii && notaSalarii.validare && notaSalarii.validare.stare_coada === "la_senior") {
      // [lotul 07.10 B, C12c] confirmarea trimiterii se vede (casetă informativă, DS cap.5), nu text mic gri
      zonaContare.innerHTML = `<div class="caseta-info"><span class="ci-mesaj">Nota de salarii ${esc(notaSalarii.nota_eticheta || "")} e la validare în cabinet.</span></div>`;
    }
    const aplicaFiltru = () => {
      const q = filtru.trim().toLowerCase();
      corp.querySelectorAll("#sp-tabel tbody tr.sp-rand").forEach((tr) => { tr.hidden = !!q && !String(tr.dataset.nume || "").toLowerCase().includes(q); });
    };
    const cauta = corp.querySelector("#sp-cauta");
    if (cauta) { cauta.addEventListener("input", () => { filtru = cauta.value; aplicaFiltru(); }); aplicaFiltru(); }
    corp.querySelector("#sp-prev").addEventListener("click", () => { L.luna--; if (L.luna < 1) { L.luna = 12; L.an--; } deseneaza(); });
    corp.querySelector("#sp-next").addEventListener("click", () => { L.luna++; if (L.luna > 12) { L.luna = 1; L.an++; } deseneaza(); });
    corp.querySelector("#sp-salariat-nou").addEventListener("click", () => nav.deschide("Salariat nou", (c2) => formularSalariatNou(c2, nav, t, null), { lat: "tabel" }));
    // [677] rândul deschide fereastra salariatului (numele e butonul; clicul oriunde pe rând face același lucru)
    const deschideSal = (sid, nume) => nav.deschide(nume, (c2) => ecranSalariat(c2, nav, t, sid), { lat: "tabel" });
    corp.querySelectorAll("#sp-tabel tbody tr.sp-rand").forEach((tr) => tr.addEventListener("click", () => deschideSal(Number(tr.dataset.sid), tr.dataset.nume)));
    // propunerea se calculează la apăsare (nu la desenarea ferestrei: o redesenare n-o recere), apoi se deschide fereastra ei
    corp.querySelector("#sp-contare").addEventListener("click", async () => {
      let p;
      try { p = await api.post(`/tenants/${t.id}/salarii-contare/propunere?an=${an}&luna=${luna}`, {}); }
      catch (e) { arataMesaj(corp.querySelector("#sp-msg"), (e && e.mesaj) || "Nu s-a putut calcula propunerea.", "eroare"); return; }
      nav.deschide("Contabilizarea statului " + _lunaTxt(an, luna), (c2) => ecranContareStat(c2, nav, t, an, luna, p), { lat: "tabel" });
    });
    corp.querySelector("#sp-plata-card").addEventListener("click", () => nav.deschide("Plată salarii pe card", (c2) => ecranPlataCard(c2, nav, t, an, luna), { lat: "tabel" }));
    corp.querySelector("#sp-reges-cfg").addEventListener("click", () => nav.deschide("Chei REGES", (c2) => ecranCheiReges(c2, nav, t), { lat: "tabel" }));
    // [C5] cererea consumă un mesaj din coada REGES: se face o singură dată, la apăsare; fereastra arată ce a venit (o redesenare nu recere)
    corp.querySelector("#sp-reges-poll").addEventListener("click", async () => {
      let r;
      try { r = await api.post(`/tenants/${t.id}/reges-poll`, {}); }   /* [drepturi_rol 04.10.2026] ruta e POST (consumă un mesaj din coada REGES) */
      catch (e) { arataMesaj(corp.querySelector("#sp-msg"), (e && e.mesaj) || "eroare", "eroare"); return; }
      nav.deschide("Răspunsuri REGES", (c2) => ecranRaspunsReges(c2, nav, t, r), { lat: "tabel" });
    });
  };
  deseneaza();
}

// [lotul 13, 677 / 675] Fereastra salariatului: cât ecranul, cu toate butoanele și compoziția netului pe trei coloane. Fiecare acțiune se
// deschide într-o fereastră nouă (673); la închiderea ei fereastra salariatului se redesenează din statul de acum, cu confirmarea actului.
async function ecranSalariat(corp, nav, t, sid) {
  const { an, luna } = _lunaStat(t);
  corp.innerHTML = `<p class="ecran-nota">Se calculează...</p>`;
  let r;
  try { r = await api.get(`/tenants/${t.id}/stat-plata?an=${an}&luna=${luna}`); }
  catch (e) { corp.innerHTML = `<p class="ecran-nota">Nu s-a putut încărca statul de plată. ${esc((e && (e.mesaj || e.message)) || "")}</p>`; return; }
  const s = ((r && r.stat) || []).find((x) => Number(x.id) === Number(sid));
  if (!s) { corp.innerHTML = `<div class="stare-goala">Salariatul nu e activ în ${_lunaTxt(an, luna)}.</div>`; return; }
  const regesOk = !!(r && r.reges_configurat);
  const confirmare = CONFIRMARI_SALARIAT[sid];
  delete CONFIRMARI_SALARIAT[sid];
  corp.innerHTML = `
    <div class="rezumat-fix">
      <h2 class="pf-titlu">Fișa salariatului · ${_lunaTxt(an, luna)}</h2>
      <div class="cf-sumar">${(s.semne || []).map((x) => `<span class="cf-pastila" title="${esc(x.titlu || "")}"${x.cod === "verifica" ? ' style="color:var(--rosu);font-weight:600"' : ""}>${esc(x.text)}${x.titlu ? ": " + esc(x.titlu) : ""}</span>`).join("")}</div>
      <div id="ss-butoane" style="display:flex;flex-wrap:wrap;gap:6px">${butoaneSalariat(s, regesOk)}</div>
      <div id="ss-msg"></div>
    </div>
    ${s.baza_lipsa ? `<div class="caseta-atentie"><span class="ca-mesaj">Salariul de bază lipsește (0 lei): completează-l cu „Salariu”. Fără el netul e 0, dar angajatorul are cost din contribuția minimă (CF art.146 alin.(5^6)).</span></div>` : ""}
    ${s.pontaj_neconfirmat ? `<div class="caseta-info"><span class="ci-mesaj">Tichetele de masă așteaptă confirmarea pontajului lunii (butonul „Pontaj”).</span></div>` : ""}
    ${_avertDeVerificat(s)}
    <h3 class="pf-subtitlu">Compoziția netului</h3>
    ${compozitieColoane(s)}
    <h3 class="pf-subtitlu">Din ce se calculează</h3>
    ${dinCeSeCalculeaza(s)}`;
  if (confirmare) arataMesaj(corp.querySelector("#ss-msg"), confirmare, "ok");
  const dupa = (mesaj) => { CONFIRMARI_SALARIAT[sid] = mesaj; nav.inapoi(); };   // închide fereastra actului; salariatul se redesenează cu confirmarea
  const fer = (titlu, fn) => nav.deschide(titlu, fn, { lat: "tabel" });
  const nume = s.nume;
  const on = (cheie, fn) => { const b = corp.querySelector(`#ss-butoane [data-${cheie}]`); if (b) b.addEventListener("click", () => fn(b)); };
  const bFlut = corp.querySelector("#ss-butoane [data-flut]");
  bFlut.addEventListener("click", async () => {
    try { await descarca(`/tenants/${t.id}/fluturas/${sid}?an=${an}&luna=${luna}`, `fluturas_${an}_${String(luna).padStart(2, "0")}.pdf`); }
    catch (e) { refuzPeRand(bFlut, (e && (e.mesaj || e.message)) || "eroare"); }   // [R131]
  });
  on("pontaj", () => fer("Pontaj · " + nume, (c2) => ecranPontaj(c2, nav, t, sid, nume, an, luna)));
  on("cm", () => fluxConcediu(nav, t, { id: sid, nume }));
  on("susp", () => fer("Suspendări contract · " + nume, (c2) => ecranSuspendari(c2, nav, t, s, dupa)));
  on("elem", () => fer("Prime, sporuri, ore suplimentare · " + nume, (c2) => ecranElemente(c2, nav, t, sid, nume, an, luna)));
  on("salariu", () => fer("Salariu de bază · " + nume, (c2) => ecranSalariuBaza(c2, nav, t, s, an, luna, dupa)));
  on("masa", () => fer("Tichet de masă · " + nume, (c2) => ecranTichetMasa(c2, nav, t, s, dupa)));
  on("vac", () => fer("Tichete de vacanță · " + nume, (c2) => ecranBeneficiu(c2, nav, t, s, an, luna, "vacanta", dupa)));
  on("cadou", () => fer("Tichete cadou · " + nume, (c2) => ecranBeneficiu(c2, nav, t, s, an, luna, "cadou", dupa)));
  on("cult", () => fer("Tichete culturale · " + nume, (c2) => ecranBeneficiu(c2, nav, t, s, an, luna, "cultural", dupa)));
  on("cresa", () => fer("Tichete de creșă · " + nume, (c2) => ecranBeneficiu(c2, nav, t, s, an, luna, "cresa", dupa)));
  on("calcul", () => fer("Date de calcul · " + nume, (c2) => ecranDateCalcul(c2, nav, t, s, dupa)));
  on("date", () => fer("Corectează datele · " + nume, (c2) => ecranCorecteazaDatele(c2, nav, t, s, dupa)));
  on("iban", () => fer("IBAN salariu · " + nume, (c2) => ecranIbanSalariat(c2, nav, t, s, dupa)));
  on("cor", () => fer("Ocupație COR · " + nume, (c2) => ecranCorSalariat(c2, nav, t, s, dupa)));
  on("incet", () => fer("Încetarea contractului · " + nume, (c2) => ecranIncetare(c2, nav, t, s, dupa)));
  // [lotul 10, deficiența 433] codul COR pentru adeverință: din rândul statului, nu din butonul COR
  on("adev", () => fer("Adeverință · " + nume, (c2) => formularAdeverinta(c2, nav, t, sid, nume, an, luna, s.cor || "")));
  on("reges", () => fer("Trimitere în REGES · " + nume, (c2) => ecranRegesSalariat(c2, nav, t, s)));
  on("verif", () => fer("De verificat · " + nume, (c2) => ecranDeVerificat(c2, nav, t, s, dupa)));
}

// Butoanele de la capătul unei ferestre de lucru: acțiunea principală lipită jos, cu „Renunță” care închide fereastra (DS cap.9 pct.6)
// (butonul se scrie întreg la locul chemării, cu `id` și `data-actiune` în clar: drepturile îl leagă de handlerul lui — `scan_drepturi_ui`)
const baraActiune = (buton, idMsg) => `<div class="bara-fixa"><p style="margin-top:10px">
  ${buton}
  <button class="buton-secundar" data-renunta style="margin-left:6px">Renunță</button></p><div id="${idMsg}"></div></div>`;
const legaRenunta = (corp, nav) => corp.querySelectorAll("[data-renunta]").forEach((b) => b.addEventListener("click", () => nav.inapoi()));

// [salariu_edit] editarea salariului de baza (schimbare de salariu -> intrare noua in salariu_istoric).
// Cabla PUT /salariati/{id} {salariu_brut, valabil_din} (necablat pana acum) + repara cazul baza_lipsa.
function ecranSalariuBaza(corp, nav, t, s, an, luna, dupa) {
  const sid = s.id;
  // [retest 07.10 seara, S2] „de la” pornește cu PRIMA ZI A LUNII LUCRATE (statul afișat), nu cu data de azi: pe 07.10 se
  // lucrează pe 09/2026, iar o schimbare de salariu „de la azi” ar fi căzut în altă lună decât cea pe care o vede contabilul
  const deLa = `${an}-${String(luna).padStart(2, "0")}-01`;
  corp.innerHTML = `<h2 class="pf-titlu">Salariu de bază</h2>
    <p class="pf-intro">Salariul de bază brut lunar din contract; o mărire „de la” o zi din lună împarte luna pe zile între cele două salarii.</p>
    <div class="grila-campuri">
      <label class="camp"><span class="camp-eticheta">Salariul de bază brut (lei)<span class="oblig">*</span></span><input type="text" inputmode="decimal" id="salariu-input" class="camp-input" value="${esc(String(s.salariu_baza ?? ""))}"></label>
      <label class="camp"><span class="camp-eticheta">De la<span class="oblig">*</span></span><input type="date" id="salariu-data" class="camp-input" value="${deLa}"></label>
    </div>
    <div id="salariu-istoric" class="camp-eticheta" style="margin-top:6px"></div>
    ${baraActiune(`<button class="buton-primar" id="salariu-save" data-actiune="PUT /tenants/{tenant_id}/salariati/{salariat_id}">Salvează</button>`, "salariu-msg")}`;
  legaRenunta(corp, nav);
  focusFaraSalt(corp.querySelector("#salariu-input"));
  // [salariul în timp, decizia Costin 04.10.2026] istoricul vizibil: ce date sunt deja ocupate
  api.get(`/tenants/${t.id}/salariati/${sid}`).then((d) => {
    const ist = (d && d.istoric_salariu) || [];
    const z = corp.querySelector("#salariu-istoric");
    if (z && ist.length) z.textContent = "Istoric: " + ist.map((x) => `de la ${dataRo(x.valabil_din)} — ${bani(x.salariu_brut)} lei`).join(" · ");
  }).catch(() => {});
  corp.querySelector("#salariu-save").addEventListener("click", async function trimite(_ev, inlocuieste = false) {
    const val = sumaRo(corp.querySelector("#salariu-input"));
    const valabil_din = corp.querySelector("#salariu-data").value || null;
    const zonaM = corp.querySelector("#salariu-msg");
    curataEroriCamp(corp);
    zonaM.innerHTML = "";
    let lipsa = false;
    if (Number.isNaN(val)) { eroareCamp(corp, "salariu-input", MESAJ_NUMAR_RO); lipsa = true; }
    else if (!(val > 0)) { eroareCamp(corp, "salariu-input", "Salariul de bază trebuie să fie mai mare ca 0."); lipsa = true; }
    if (!valabil_din) { eroareCamp(corp, "salariu-data", "Alege data de la care se aplică salariul."); lipsa = true; }
    if (lipsa) return;
    try {
      await api.put(`/tenants/${t.id}/salariati/${sid}`, { salariu_brut: val, valabil_din, inlocuieste: !!inlocuieste });
      dupa(`Salariul de bază al lui ${s.nume} e ${bani(val)} lei de la ${dataRo(valabil_din)}; statul se calculează cu el.`);
    } catch (e) {
      // refuzul stă lângă câmpul vinovat; ce s-a tastat rămâne în casete (fereastra nu se redesenează)
      const eris = (e && e.erori_campuri) || [];
      eris.forEach((x) => eroareCamp(corp, x.camp === "valabil_din" ? "salariu-data" : "salariu-input", x.mesaj));
      if (!eris.length) arataMesaj(zonaM, (e && e.mesaj) || "Eroare la salvare.", "eroare");
      const ex = e && e.detaliu && e.detaliu.cod === "SALARIU_DATA_OCUPATA" ? e.detaliu.existent : null;
      if (ex) {
        zonaM.insertAdjacentHTML("beforeend", `<button class="buton-secundar" id="salariu-inlocuieste">Înlocuiește salariul de la ${esc(dataRo(ex.valabil_din))} (${esc(bani(ex.salariu_brut))} → ${esc(bani(ex.salariu_nou))} lei)</button>`);
        corp.querySelector("#salariu-inlocuieste").addEventListener("click", () => trimite(null, true));
      }
    }
  });
  // [R28, decizia lui Costin 24.08.2026 - varianta 3: NIMIC] Fără „net estimat” calculat cu doi parametri din 18: netul și costul se
  // calculează după salvare, cu toate elementele (statul de plată).

}

// [lotul 13, deficiența 672] „Tichetul de masă nu se poate pune sau schimba la un salariat existent […] Orice setare a salariatului care
// schimbă cifrele statului se poate corecta oricând.” Butonul „+ masă” (675, lângă „+ vacanță”): valoarea tichetului pe zi lucrată, salvată
// pe fișa salariatului (PUT /salariati {tichet_masa_valoare}, același câmp ca la „Salariat nou”); plafonul legal îl verifică serverul.
function ecranTichetMasa(corp, nav, t, s, dupa) {
  corp.innerHTML = `<h2 class="pf-titlu">Tichet de masă</h2>
    <p class="pf-intro">Valoarea tichetului pe zi lucrată (0 = fără tichete); numărul tichetelor vine din zilele lucrate ale lunii (HG 1045/2018 art.10 alin.(3)).</p>
    <div class="grila-campuri">
      <label class="camp"><span class="camp-eticheta">Valoarea tichetului (lei pe zi)<span class="oblig">*</span></span><input type="text" inputmode="decimal" id="masa-input" class="camp-input" value="${esc(String(s.tichet_masa_valoare ?? ""))}"></label>
    </div>
    ${baraActiune(`<button class="buton-primar" id="masa-save" data-actiune="PUT /tenants/{tenant_id}/salariati/{salariat_id}">Salvează</button>`, "masa-msg")}`;
  legaRenunta(corp, nav);
  focusFaraSalt(corp.querySelector("#masa-input"));
  corp.querySelector("#masa-save").addEventListener("click", async () => {
    curataEroriCamp(corp);
    const v = sumaRo(corp.querySelector("#masa-input"));
    if (v === null || Number.isNaN(v) || v < 0) { eroareCamp(corp, "masa-input", v === null ? "Scrie valoarea tichetului (0 = fără tichete)." : MESAJ_NUMAR_RO); return; }
    try {
      await api.put(`/tenants/${t.id}/salariati/${s.id}`, { tichet_masa_valoare: v });
      dupa(v > 0 ? `${s.nume} primește tichete de masă de ${bani(v)} lei pe zi lucrată.` : `${s.nume} nu mai primește tichete de masă.`);
    } catch (e) { arataRefuzul(corp, e, corp.querySelector("#masa-msg"), { campuri: { tichet_masa_valoare: "masa-input" } }); }
  });
}

// [F133] tichete de vacanță / cadou / culturale / creșă, pe luna statului (`beneficiu-lunar`). Plafoanele le verifică serverul.
const EVENIMENTE_CADOU = [["paste", "Paște"], ["craciun", "Crăciun"], ["8martie", "8 Martie"], ["1iunie", "1 Iunie"], ["altul", "alt eveniment (taxabil)"]];
const BENEFICII = {
  vacanta: { titlu: "Tichete de vacanță", ajutor: "Valoarea tichetelor de vacanță acordate în lună; peste plafonul anual (6 salarii minime) excesul devine venit salarial." },
  cadou: { titlu: "Tichete cadou", ajutor: "Neimpozabile până la 300 lei pe eveniment legal; peste 300 sau alt eveniment = taxabil (CF art.76 alin.(4) lit.a)." },
  cultural: { titlu: "Tichete culturale", ajutor: "Valoare nominală multiplu de 10 lei (Legea 165/2018 art.22); plafonul se verifică la salvare." },
  cresa: { titlu: "Tichete de creșă", ajutor: "Plafon lunar pe copil (Legea 165/2018 art.19), verificat la salvare; valoare multiplu de 10." },
};
function ecranBeneficiu(corp, nav, t, s, an, luna, tip, dupa) {
  const B = BENEFICII[tip];
  const extra = tip === "cadou" ? `<div class="camp"><span class="camp-eticheta">Evenimentul<span class="oblig">*</span></span>${selectScurt("ben-ev", EVENIMENTE_CADOU, "", "Evenimentul tichetelor cadou")}</div>`
    : tip === "cultural" ? `<div class="camp"><span class="camp-eticheta">Felul<span class="oblig">*</span></span>${selectScurt("ben-ev", [["lunar", "lunar"], ["ocazional", "ocazional (eveniment)"]], "", "Felul tichetelor culturale")}</div>`
    : tip === "cresa" ? `<label class="camp"><span class="camp-eticheta">Număr de copii la creșă<span class="oblig">*</span></span><input type="text" inputmode="numeric" id="ben-copii" class="camp-input"></label>` : "";
  const valInit = tip === "vacanta" ? String(s.tichete_vacanta ?? "") : "";
  corp.innerHTML = `<h2 class="pf-titlu">${B.titlu} · ${_lunaTxt(an, luna)}</h2>
    <p class="pf-intro">${esc(B.ajutor)}</p>
    <div class="grila-campuri">${extra}
      <label class="camp"><span class="camp-eticheta">Valoarea (lei)<span class="oblig">*</span></span><input type="text" inputmode="decimal" id="ben-input" class="camp-input" value="${esc(valInit)}"></label>
    </div>
    ${baraActiune(`<button class="buton-primar" id="ben-save" data-actiune="PUT /tenants/{tenant_id}/salariati/{salariat_id}/beneficiu-lunar">Salvează</button>`, "ben-msg")}`;
  legaRenunta(corp, nav);
  focusFaraSalt(corp.querySelector("#ben-input"));
  corp.querySelector("#ben-save").addEventListener("click", async () => {
    curataEroriCamp(corp);
    let lipsa = tip === "cadou" || tip === "cultural" ? cereAlegerile(corp, ["#ben-ev"]) : false;   // [FAPT_FISCAL_NECERUT]
    const valoare = sumaRo(corp.querySelector("#ben-input"));
    if (valoare === null || Number.isNaN(valoare) || valoare < 0) { eroareCamp(corp, "ben-input", valoare === null ? "Scrie valoarea (0 = fără)." : MESAJ_NUMAR_RO); lipsa = true; }
    let nr_copii = null;
    if (tip === "cresa") {
      nr_copii = sumaRo(corp.querySelector("#ben-copii"));
      if (!(Number.isInteger(nr_copii) && nr_copii >= 1)) { eroareCamp(corp, "ben-copii", "Scrie numărul de copii (cel puțin 1)."); lipsa = true; }
    }
    if (lipsa) return;
    const corpReq = { an, luna, tip, valoare };
    if (tip === "cadou") corpReq.eveniment = corp.querySelector("#ben-ev").value;
    if (tip === "cultural") corpReq.eveniment = corp.querySelector("#ben-ev").value === "ocazional" ? "ocazional" : "";
    if (tip === "cresa") corpReq.nr_copii = nr_copii;
    try {
      await api.put(`/tenants/${t.id}/salariati/${s.id}/beneficiu-lunar`, corpReq);
      dupa(`${B.titlu} pentru ${s.nume}: ${bani(valoare)} lei în ${_lunaTxt(an, luna)}.`);
    } catch (e) { arataRefuzul(corp, e, corp.querySelector("#ben-msg"), { campuri: { valoare: "ben-input", eveniment: "ben-ev", nr_copii: "ben-copii" } }); }   // [lotul 11, 440]
  });
}

// [F134] IBAN salariat: cont beneficiar pt fisierul de plata pe card
function ecranIbanSalariat(corp, nav, t, s, dupa) {
  corp.innerHTML = `<h2 class="pf-titlu">IBAN salariu</h2>
    <p class="pf-intro">IBAN românesc (RO + 22 caractere); gol = fără plată pe card.</p>
    <div class="grila-campuri"><label class="camp"><span class="camp-eticheta">IBAN</span><input type="text" id="iban-input" class="camp-input" value="${esc(s.iban || "")}" placeholder="RO.. cont pe card"></label></div>
    ${baraActiune(`<button class="buton-primar" id="iban-save" data-actiune="PUT /tenants/{tenant_id}/salariati/{salariat_id}">Salvează</button>`, "iban-msg")}`;
  legaRenunta(corp, nav);
  focusFaraSalt(corp.querySelector("#iban-input"));
  corp.querySelector("#iban-save").addEventListener("click", async () => {
    const iban = corp.querySelector("#iban-input").value.trim().replace(/\s/g, "").toUpperCase();
    try {
      await api.put(`/tenants/${t.id}/salariati/${s.id}`, { iban });  // "" = sterge (goleste contul)
      dupa(iban ? `IBAN-ul lui ${s.nume} s-a salvat.` : `${s.nume} nu mai are IBAN: nu intră în fișierul de plată pe card.`);
    } catch (e) { arataRefuzul(corp, e, corp.querySelector("#iban-msg"), { campuri: { iban: "iban-input" } }); }   // [lotul 11, 440]
  });
}

// [F137] cod ocupatie COR: lookup din nomenclator (necesar REGES)
function ecranCorSalariat(corp, nav, t, s, dupa) {
  corp.innerHTML = `<h2 class="pf-titlu">Ocupație COR</h2>
    <div style="max-width:520px">${campCorLookup("cor-edit")}</div>
    ${baraActiune(`<button class="buton-primar" id="cor-save" data-actiune="PUT /tenants/{tenant_id}/salariati/{salariat_id}">Salvează</button>`, "cor-msg")}`;
  legaCorLookup(corp, "cor-edit", s.cor || "");
  legaRenunta(corp, nav);
  corp.querySelector("#cor-save").addEventListener("click", async () => {
    const cor = corp.querySelector("#cor-edit-cor").value.trim();
    try {
      await api.put(`/tenants/${t.id}/salariati/${s.id}`, { cor });  // "" = sterge; cod invalid respins de backend
      dupa(`Ocupația COR a lui ${s.nume} s-a salvat.`);
    } catch (e) { arataRefuzul(corp, e, corp.querySelector("#cor-msg"), { campuri: { cor: "cor-edit-cor" } }); }   // [lotul 11, 440]
  });
}

// PASUL 1: incetarea contractului (data_incetare). Marcheaza PLECAREA - inlocuieste stergerea la plecare (istoricul sustine declaratiile depuse).
function ecranIncetare(corp, nav, t, s, dupa) {
  corp.innerHTML = `<h2 class="pf-titlu">Încetarea contractului</h2>
    <p class="pf-intro">Gol = contract activ. La plecare salariatul nu se șterge: se completează data încetării.</p>
    <div class="grila-campuri"><label class="camp"><span class="camp-eticheta">Data încetării</span><input type="date" id="incet-input" class="camp-input" value="${esc(s.data_incetare || "")}"></label></div>
    ${baraActiune(`<button class="buton-primar" id="incet-save" data-actiune="PUT /tenants/{tenant_id}/salariati/{salariat_id}">Salvează</button>`, "incet-msg")}`;
  legaRenunta(corp, nav);
  focusFaraSalt(corp.querySelector("#incet-input"));
  corp.querySelector("#incet-save").addEventListener("click", async () => {
    const data_incetare = corp.querySelector("#incet-input").value || null;
    try {
      await api.put(`/tenants/${t.id}/salariati/${s.id}`, { data_incetare });
      dupa(data_incetare ? `Contractul lui ${s.nume} încetează la ${dataRo(data_incetare)}.` : `Contractul lui ${s.nume} e activ.`);
    } catch (e) { arataRefuzul(corp, e, corp.querySelector("#incet-msg"), { campuri: { data_incetare: "incet-input" } }); }   // [lotul 11, 440]
  });
}

// [front_e + lotul 13, 675] „Corectează datele”: identitatea și contractul individual de muncă (nume, prenume, CNP, tipul și numărul CIM).
// Setările care schimbă cifrele statului nu mai stau aici: sunt în „Date de calcul”, „Salariu” și „+ masă”, cu valorile la vedere.
// CNP validat client-side (checksum) inainte de PUT.
function ecranCorecteazaDatele(corp, nav, t, s, dupa) {
  const sid = s.id;
  corp.innerHTML = `<h2 class="pf-titlu">Corectează datele</h2>
    <p class="pf-intro">Identitatea și contractul de muncă. Corectarea nu modifică declarațiile deja depuse.</p>
    <div class="grila-campuri">
      <label class="camp"><span class="camp-eticheta">Nume<span class="oblig">*</span></span><input id="ed-nume" class="camp-input" value="${esc(s.nume_ed || "")}"></label>
      <label class="camp"><span class="camp-eticheta">Prenume</span><input id="ed-pren" class="camp-input" value="${esc(s.prenume_ed || "")}"></label>
      <label class="camp"><span class="camp-eticheta">CNP<span class="oblig">*</span></span><input id="ed-cnp" class="camp-input" inputmode="numeric" maxlength="13" value="${esc(s.cnp || "")}"></label>
      <div class="camp"><span class="camp-eticheta">Tip contract</span>${selectScurt("ed-tipcim", TIPURI_CIM, "", "Tip contract")}</div>
      <label class="camp"><span class="camp-eticheta">Nr. CIM</span><input id="ed-nrcim" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Dată CIM</span><input type="date" id="ed-datacim" class="camp-input"></label>
    </div>
    ${baraActiune(`<button class="buton-primar" id="ed-save" data-actiune="PUT /tenants/{tenant_id}/salariati/{salariat_id}">Salvează</button>`, "ed-msg")}`;
  legaRenunta(corp, nav);
  focusFaraSalt(corp.querySelector("#ed-nume"));
  // [412] contractul individual de muncă din fișă (Codul muncii art.12, art.16): se arată cel salvat; până nu s-a citit, salvarea
  // nu-l trimite (un câmp gol pentru că fișa n-a venit încă nu golește ce era salvat)
  let cimCitit = false;
  api.get(`/tenants/${t.id}/salariati/${sid}`).then((d) => {
    if (!d || !corp.querySelector("#ed-tipcim")) return;
    const tip = corp.querySelector("#ed-tipcim"), nr = corp.querySelector("#ed-nrcim"), dt = corp.querySelector("#ed-datacim");
    if (d.tip_contract && !tip.value) tip.value = d.tip_contract;   // ce a ales / tastat deja omul nu se suprascrie
    if (d.nr_cim && !nr.value) nr.value = d.nr_cim;
    if (d.data_cim && !dt.value) dt.value = String(d.data_cim).slice(0, 10);
    cimCitit = true;
  }).catch(() => {});
  corp.querySelector("#ed-save").addEventListener("click", async () => {
    const msg = corp.querySelector("#ed-msg");
    curataEroriCamp(corp);
    // [lotul 11, 440] numele și CNP-ul greșite se marchează DEODATĂ, fiecare lângă câmpul lui
    let lipsa = false;
    const nume = corp.querySelector("#ed-nume").value.trim();
    const prenume = corp.querySelector("#ed-pren").value.trim();
    const cnp = corp.querySelector("#ed-cnp").value.trim();
    if (cereCompletate(corp, [{ id: "ed-nume", mesaj: "Numele e obligatoriu." }])) lipsa = true;
    if (!cnpValid(cnp)) { eroareCamp(corp, "ed-cnp", "CNP invalid (13 cifre, cifră de control greșită)."); lipsa = true; }
    if (lipsa) return;
    try {
      // `undefined` nu intră în JSON: un câmp CIM gol se trimite (golire) numai după ce fișa a fost citită; completat, se trimite mereu
      const cimVal = (v) => (cimCitit || v ? (v || null) : undefined);
      const tip_contract = cimVal(corp.querySelector("#ed-tipcim").value);
      const nr_cim = cimVal(corp.querySelector("#ed-nrcim").value.trim());
      const data_cim = cimVal(corp.querySelector("#ed-datacim").value);
      await api.put(`/tenants/${t.id}/salariati/${sid}`, { nume, prenume, cnp, tip_contract, nr_cim, data_cim });
      // [clasa 410, DS cap.27] confirmarea numește salariatul și consecința
      dupa(`${`${nume} ${prenume}`.trim()}: datele corectate s-au salvat.`);
    } catch (e) {   // [lotul 11, 440] lista completă a serverului (`valideaza_salariat`), fiecare eroare lângă câmpul ei
      arataRefuzul(corp, e && e.mesaj ? e : { ...(e || {}), mesaj: "Eroare la salvare." }, msg, { campuri: CAMPURI_ED_SALARIAT });
    }
  });
}

// [lotul 13, 675] „Date de calcul”: setările salariatului din care se calculează statul — data angajării, norma, deducerile (CF art.77) și
// contribuția minimă (CF art.146 alin.(5^7)) — corectabile oricând, la vedere în fereastra salariatului („Din ce se calculează”).
function ecranDateCalcul(corp, nav, t, s, dupa) {
  const sid = s.id;
  corp.innerHTML = `<h2 class="pf-titlu">Date de calcul</h2>
    <p class="pf-intro">Datele din care se calculează statul; corectura intră de la luna de după ultima D112 depusă.</p>
    <div class="grila-campuri">
      <label class="camp"><span class="camp-eticheta">Data angajării</span><input type="date" id="ed-ang" class="camp-input" value="${esc(s.data_angajare || "")}"></label>
      <div class="camp"><span class="camp-eticheta">Normă<span class="oblig">*</span></span>${selectScurt("ed-norma", NORME, s.tip_norma || "", "Normă")}</div>
      <label class="camp" id="ed-orezi-camp"><span class="camp-eticheta">Ore pe zi (normă parțială)</span><input type="text" inputmode="decimal" id="ed-orezi" class="camp-input" value="${esc(String(s.ore_zi ?? ""))}"></label>
      <div class="camp"><span class="camp-eticheta">Funcția de bază la acest angajator<span class="oblig">*</span></span>${selectDaNu('id="ed-fbaza"', null, "Funcția de bază la acest angajator")}
        <span class="camp-ajutor">Deducerea personală se acordă numai la funcția de bază (CF art. 77 alin. (1)).</span></div>
      <label class="camp"><span class="camp-eticheta">Persoane în întreținere</span><input type="text" inputmode="numeric" id="ed-persoane" class="camp-input" value="${esc(String(s.persoane_intretinere ?? ""))}"></label>
      <label class="camp"><span class="camp-eticheta">Data nașterii</span><input type="date" id="ed-nastere" class="camp-input">
        <span class="camp-ajutor">Pentru deducerea tinerilor sub 26 de ani (CF art. 77 alin. (10) lit. a).</span></label>
      <label class="camp"><span class="camp-eticheta">Copii ≤ 18 ani înscriși în învățământ</span><input type="text" inputmode="numeric" id="ed-copii" class="camp-input">
        <span class="camp-ajutor">100 lei pe lună pentru fiecare copil (CF art. 77 alin. (10) lit. b).</span></label>
      <div class="camp"><span class="camp-eticheta">Declarația părintelui pentru copii<span class="oblig">*</span></span>${selectDaNu('id="ed-declcopii"', null, "Declarația părintelui pentru copii")}
        <span class="camp-ajutor">Fără ea deducerea pentru copii nu se acordă (CF art. 77 alin. (12)).</span></div>
      <div class="camp"><span class="camp-eticheta">Scutit de contribuția minimă<span class="oblig">*</span></span>${selectDaNu('id="ed-scutit"', null, "Scutit de contribuția minimă")}
        <span class="camp-ajutor">Intră în D112 (CF art. 146 alin. (5^7)). Corectura rămâne în jurnal: cine, când, vechi → nou.</span></div>
      ${campMotivScutire("ed-motiv")}
    </div>
    <div id="ed-jurnal-scutire"></div>
    ${baraActiune(`<button class="buton-primar" id="ed-save" data-actiune="PUT /tenants/{tenant_id}/salariati/{salariat_id}">Salvează</button>`, "ed-msg")}`;
  legaRenunta(corp, nav);
  const oreCamp = corp.querySelector("#ed-orezi-camp");
  const aratOre = () => { oreCamp.hidden = corp.querySelector("#ed-norma").value !== "partiala"; };
  corp.querySelector("#ed-norma").addEventListener("change", aratOre);
  aratOre();
  let deducCitite = false;   // [lotul 10] datele deducerilor: necitite = netrimise (nu se golește ce era salvat)
  api.get(`/tenants/${t.id}/salariati/${sid}`).then((d) => {
    if (!d || !corp.querySelector("#ed-fbaza")) return;
    // [lotul 10, SalariatEdit] datele deducerilor (CF art.77): cele salvate se arată; ce a ales / tastat deja omul nu se suprascrie
    const fb = corp.querySelector("#ed-fbaza"), nas = corp.querySelector("#ed-nastere");
    const cop = corp.querySelector("#ed-copii"), dec = corp.querySelector("#ed-declcopii");
    if (typeof d.functie_baza === "boolean" && !fb.value) fb.value = String(d.functie_baza);
    if (d.data_nastere && !nas.value) nas.value = String(d.data_nastere).slice(0, 10);
    if (d.copii_scolarizati != null && cop.value === "") cop.value = String(d.copii_scolarizati);
    if (typeof d.declaratie_copii === "boolean" && !dec.value) dec.value = String(d.declaratie_copii);
    deducCitite = true;
    // [C133, comanda Costin 12.3 pct.8] scutirea și motivul salvate se arată (ce a ales deja omul nu se suprascrie); cele marcate „de
    // verificat” la import NU se precompletează — importul a pus „nescutit”, alegerea e a contabilului
    const sc = corp.querySelector("#ed-scutit"), mv = corp.querySelector("#ed-motiv"), dvs = d.de_verificat || [];
    if (typeof d.scutit_contrib_minim === "boolean" && !sc.value && !dvs.includes("scutit_contrib_minim")) sc.value = String(d.scutit_contrib_minim);
    if (d.motiv_exceptare != null && !mv.value && !dvs.includes("motiv_exceptare")) mv.value = String(d.motiv_exceptare);
    sc.dispatchEvent(new Event("change"));
    corp.querySelector("#ed-jurnal-scutire").innerHTML = blocJurnalScutire(d.jurnal_scutire);
  }).catch(() => {});
  legaMotivScutire(corp, "ed-scutit", "ed-motiv");   // [C133] motivul se cere numai la „Scutit” = Da
  corp.querySelector("#ed-save").addEventListener("click", async () => {
    const msg = corp.querySelector("#ed-msg");
    curataEroriCamp(corp);
    // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite; [lotul 11, 440] toate lipsurile deodată, fiecare lângă câmpul lui
    let lipsa = false; if (cereAlegerile(corp, ["#ed-norma", "#ed-fbaza", "#ed-declcopii", "#ed-scutit", "#ed-motiv"])) lipsa = true;
    const tip_norma = corp.querySelector("#ed-norma").value;
    const ore_zi = tip_norma === "partiala" ? sumaRo(corp.querySelector("#ed-orezi")) : 8;
    if (tip_norma === "partiala" && !(ore_zi >= 1 && ore_zi <= 7.5)) { eroareCamp(corp, "ed-orezi", "Scrie orele pe zi ale normei parțiale (între 1 și 7,5)."); lipsa = true; }
    const pers = sumaRo(corp.querySelector("#ed-persoane"));
    if (!(Number.isInteger(pers) && pers >= 0)) { eroareCamp(corp, "ed-persoane", "Scrie numărul persoanelor în întreținere (0 dacă nu are)."); lipsa = true; }
    const cop = corp.querySelector("#ed-copii").value.trim();
    const copN = cop === "" ? 0 : sumaRo(cop);
    if (!(Number.isInteger(copN) && copN >= 0)) { eroareCamp(corp, "ed-copii", "Scrie numărul copiilor (0 dacă nu are)."); lipsa = true; }
    if (lipsa) return;
    try {
      // [lotul 10, decizia sesiunii principale „SalariatEdit”] deducerile CF art.77 alin.(1), (10), (12); data nașterii și copiii se trimit după
      // ce fișa a fost citită (un câmp gol pentru că fișa n-a venit încă nu golește ce era salvat), sau când omul le-a completat.
      const deduceri = { functie_baza: daNu(corp.querySelector("#ed-fbaza")), declaratie_copii: daNu(corp.querySelector("#ed-declcopii")),
        persoane_intretinere: pers };
      const nas = corp.querySelector("#ed-nastere").value;
      if (deducCitite || nas) deduceri.data_nastere = nas || null;
      if (deducCitite || cop !== "") deduceri.copii_scolarizati = copN;
      // [C133] scutirea (aleasă mai sus) și motivul ei, numai la „Da”; la „Nu” serverul golește motivul (și consemnează corectura)
      const scutire = { scutit_contrib_minim: daNu(corp.querySelector("#ed-scutit")) };
      if (scutire.scutit_contrib_minim === true) scutire.motiv_exceptare = motivAles(corp, "ed-motiv");
      const data_angajare = corp.querySelector("#ed-ang").value || null;
      const rez = await api.put(`/tenants/${t.id}/salariati/${sid}`, { data_angajare, tip_norma, ore_zi, ...deduceri, ...scutire });
      // [clasa 410, DS cap.27] confirmarea numește salariatul și consecința; [C133] la scutirea corectată, și efectul în D112
      dupa(`${s.nume}: datele de calcul s-au salvat; statul se calculează cu ele.` + (rez && rez.scutire_corectata && rez.efect_d112 ? " " + rez.efect_d112 : ""));
    } catch (e) {   // [lotul 11, 440] lista completă a serverului (`valideaza_salariat`), fiecare eroare lângă câmpul ei
      arataRefuzul(corp, e && e.mesaj ? e : { ...(e || {}), mesaj: "Eroare la salvare." }, msg,
        { campuri: { ...CAMPURI_ED_SALARIAT, persoane_intretinere: "ed-persoane", tip_norma: "ed-norma", functie_baza: "ed-fbaza",
          declaratie_copii: "ed-declcopii", scutit_contrib_minim: "ed-scutit", motiv_exceptare: "ed-motiv" } });
    }
  });
}

// [decizia Costin 14.10.2026 pct.3–4, verbatim în DECIZII] câmpurile importate fără valoare din fișier („de verificat”): se confirmă aici —
// persoanele în întreținere (numărul) și scutirea de contribuția minimă (Da/Nu, fără preselecție). Salvarea câmpului îl scoate din marcaj.
function ecranDeVerificat(corp, nav, t, s0, dupa) {
  const sid = s0.id;
  const dv = s0.de_verificat || [];
  corp.innerHTML = `<h2 class="pf-titlu">De verificat</h2>
    <div class="grila-campuri">
      ${dv.includes("persoane_intretinere") ? `<label class="camp"><span class="camp-eticheta">Persoane în întreținere <span class="oblig">*</span></span>
        <input type="text" inputmode="numeric" id="dv-persoane" class="camp-input" value="${esc(String(s0.persoane_intretinere ?? ""))}">
        <span class="camp-ajutor">Fișierul importat nu le avea; s-a pus 0. Din declarația salariatului (CF art.77).</span></label>` : ""}
      ${dv.includes("scutit_contrib_minim") ? `<div class="camp"><span class="camp-eticheta">Scutit de contribuția minimă <span class="oblig">*</span></span>
        ${selectDaNu('id="dv-scutit"', null, "Scutit de contribuția minimă")}
        <span class="camp-ajutor">Fișierul importat nu avea coloana; s-a importat „nescutit”. Intră în D112.</span></div>` : ""}
      ${dv.includes("scutit_contrib_minim") || dv.includes("motiv_exceptare") ? campMotivScutire("dv-motiv") : ""}
      ${dv.includes("tip_norma") ? `<div class="camp"><span class="camp-eticheta">Norma de lucru <span class="oblig">*</span></span>
        ${selectScurt("dv-norma", NORME, "", "Norma de lucru")}
        <span class="camp-ajutor">Fișierul importat n-o avea; s-a propus ${s0.tip_norma === "partiala" ? `normă parțială, ${s0.ore_zi ? esc(cate(Number(s0.ore_zi), "oră", "ore")) : "orele pe zi nescrise"}` : "normă întreagă"}. Intră în D112.</span></div>
      <label class="camp" id="dv-ore-camp" hidden><span class="camp-eticheta">Ore pe zi (normă parțială) <span class="oblig">*</span></span>
        <input type="text" inputmode="decimal" id="dv-ore" class="camp-input" value="${s0.tip_norma === "partiala" ? esc(String(s0.ore_zi ?? "")) : ""}"></label>` : ""}
      ${dv.includes("functie_baza") ? `<div class="camp"><span class="camp-eticheta">Funcția de bază la acest angajator <span class="oblig">*</span></span>
        ${selectDaNu('id="dv-fbaza"', null, "Funcția de bază la acest angajator")}
        <span class="camp-ajutor">Fișierul importat n-o avea; s-a propus „Da”. Deducerea personală se acordă numai la funcția de bază (CF art. 77 alin. (1)).</span></div>` : ""}
    </div>
    ${baraActiune(`<button class="buton-primar" id="dv-save" data-actiune="PUT /tenants/{tenant_id}/salariati/{salariat_id}">Confirmă</button>`, "dv-msg")}`;
  legaRenunta(corp, nav);
  // [C133] motivul scutirii: cerut când scutirea se alege „Da” aici, sau direct (salariatul e deja scutit, fără motiv)
  if (corp.querySelector("#dv-motiv")) legaMotivScutire(corp, "dv-scutit", "dv-motiv", !dv.includes("scutit_contrib_minim"));
  // [lotul 10, 420] orele pe zi se cer numai la norma parțială
  corp.querySelector("#dv-norma")?.addEventListener("change", (ev) => { corp.querySelector("#dv-ore-camp").hidden = ev.target.value !== "partiala"; });
  corp.querySelector("#dv-save").addEventListener("click", async () => {
    const msg = corp.querySelector("#dv-msg");
    curataEroriCamp(corp);
    const corpReq = {};
    // [lotul 11, 440] toate lipsurile deodată (câmpurile și alegerile), apoi un singur `return`
    let lipsa = false;
    if (dv.includes("persoane_intretinere")) {
      const v = sumaRo(corp.querySelector("#dv-persoane"));
      if (!(Number.isInteger(v) && v >= 0)) { eroareCamp(corp, "dv-persoane", "Scrie numărul persoanelor în întreținere (0 dacă nu are)."); lipsa = true; }
      corpReq.persoane_intretinere = v;
    }
    if (dv.includes("scutit_contrib_minim")) {
      if (cereAlegerile(corp, ["#dv-scutit"])) lipsa = true;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
      corpReq.scutit_contrib_minim = daNu(corp.querySelector("#dv-scutit"));
    }
    if (corp.querySelector("#dv-motiv")) {   // [C133] ascuns (scutirea „Nu”): nu se cere și nu se trimite
      if (cereAlegerile(corp, ["#dv-motiv"])) lipsa = true;
      const m = motivAles(corp, "dv-motiv");
      if (m !== null) corpReq.motiv_exceptare = m;
    }
    // [lotul 10, deficiența 420] norma și funcția de bază propuse la import: alegerea contabilului le confirmă (ies din marcaj)
    if (cereAlegerile(corp, ["#dv-norma", "#dv-fbaza"])) lipsa = true;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
    if (dv.includes("tip_norma")) {
      corpReq.tip_norma = corp.querySelector("#dv-norma").value;
      if (corpReq.tip_norma === "partiala") {
        const o = sumaRo(corp.querySelector("#dv-ore"));
        if (!(o >= 1 && o <= 7.5)) { eroareCamp(corp, "dv-ore", "Scrie orele pe zi ale normei parțiale (între 1 și 7,5)."); lipsa = true; }
        corpReq.ore_zi = o;
      } else corpReq.ore_zi = 8;
    }
    if (lipsa) return;
    if (dv.includes("functie_baza")) corpReq.functie_baza = daNu(corp.querySelector("#dv-fbaza"));
    const btn = corp.querySelector("#dv-save");
    btn.disabled = true; btn.textContent = "Se salvează…";
    try {
      const rez = await api.put(`/tenants/${t.id}/salariati/${sid}`, corpReq);
      // DS cap.27: confirmarea numește salariatul și consecința; [C133] scutirea schimbată: și efectul în D112
      dupa(`${s0.nume}: datele de verificat sunt confirmate; statul se calculează cu ele.` + (rez && rez.scutire_corectata && rez.efect_d112 ? " " + rez.efect_d112 : ""));
    } catch (e) {
      btn.disabled = false; btn.textContent = "Confirmă";
      arataRefuzul(corp, e && e.mesaj ? e : { ...(e || {}), mesaj: "Eroare la salvare." }, msg,   // [lotul 11, 440]
        { campuri: { persoane_intretinere: "dv-persoane", scutit_contrib_minim: "dv-scutit", motiv_exceptare: "dv-motiv", tip_norma: "dv-norma", ore_zi: "dv-ore", functie_baza: "dv-fbaza" } });
    }
  });
}

// [retest 07.10 seara, S1] elementele variabile ale lunii pe salariat: primă / spor / ore suplimentare, cu denumirea scrisă de contabil (tipul
// se alege — fără preselecție); intră în brut și în baze, apar distinct pe fluturaș. [lotul 13, 679] La orele suplimentare suma nu se cere: o
// calculează serverul din ore × tariful orar × (100% + spor) și se arată cu calculul ei (`elemente_salariale.adauga`).
const TIPURI_ELEMENT = [["prima", "Primă"], ["spor", "Spor"], ["ore_suplimentare", "Ore suplimentare"]];
async function ecranElemente(corp, nav, t, sid, nume, an, luna) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  let s0;
  try { s0 = (((await api.get(`/tenants/${t.id}/stat-plata?an=${an}&luna=${luna}`)) || {}).stat || []).find((x) => Number(x.id) === Number(sid)) || {}; }
  catch (e) { corp.innerHTML = `<p class="ecran-nota">Nu s-a putut încărca statul de plată. ${esc((e && e.mesaj) || "")}</p>`; return; }
  const el = s0.elemente || [];
  const calculOre = (e) => (e.tarif_orar && e.spor_procent != null
    ? `${esc(cate(Number(e.ore), "oră", "ore"))} × ${bani(e.tarif_orar)} lei × ${String(100 + Number(e.spor_procent)).replace(".", ",")}%${e.spor_dedus ? " (sporul rezultă din suma scrisă)" : ""}` : (e.ore ? esc(cate(Number(e.ore), "oră", "ore")) : "—"));
  corp.innerHTML = `
    <div class="rezumat-fix"><h2 class="pf-titlu">Prime, sporuri, ore suplimentare · ${_lunaTxt(an, luna)}</h2></div>
    ${el.length ? `<table class="fd-tabel" id="el-tabel"><thead><tr><th>Tip</th><th>Denumire</th><th>Calculul</th><th class="fd-td-num">Sumă</th><th>Acțiune</th></tr></thead><tbody>
      ${el.map((e) => `<tr><td>${esc(e.eticheta_tip)}</td><td>${esc(e.denumire)}</td><td>${e.tip === "ore_suplimentare" ? calculOre(e) : "—"}</td><td class="fd-td-num">${bani(e.suma)} lei</td>
        <td><button class="buton-sters buton-mic el-sterge" data-id="${e.id}" data-actiune="DELETE /tenants/{tenant_id}/salariati/{salariat_id}/elemente/{element_id}">Șterge</button></td></tr>`).join("")}</tbody></table>`
      : `<div class="stare-goala">Niciun element variabil în luna asta.</div>`}
    <div id="el-formular">
    <div class="grila-campuri" style="max-width:none">
      <div class="camp"><span class="camp-eticheta">Tipul<span class="oblig">*</span></span>${selectScurt("el-tip", TIPURI_ELEMENT, "", "Tipul elementului de salariu")}</div>
      <label class="camp"><span class="camp-eticheta">Denumirea, cum apare pe fluturaș<span class="oblig">*</span></span><input type="text" class="camp-input" id="el-denumire"></label>
      <label class="camp" id="el-ore-camp" hidden><span class="camp-eticheta">Orele suplimentare<span class="oblig">*</span></span><input type="text" inputmode="decimal" class="camp-input" id="el-ore"></label>
      <label class="camp" id="el-spor-camp" hidden><span class="camp-eticheta">Sporul din contract (%)<span class="oblig">*</span></span><input type="text" inputmode="decimal" class="camp-input" id="el-spor"></label>
      <label class="camp" id="el-suma-camp" hidden><span class="camp-eticheta">Suma brută (lei)<span class="oblig">*</span></span><input type="text" inputmode="decimal" class="camp-input" id="el-suma"></label>
      <div class="camp"><button class="buton-primar" id="el-adauga" data-actiune="POST /tenants/{tenant_id}/salariati/{salariat_id}/elemente">Adaugă</button></div>
      <div class="camp"><button class="buton-secundar" id="el-renunta">Închide</button></div>
    </div>
    <div class="tip-micut" id="el-explicatie">${s0.tarif_orar ? `La orele suplimentare suma se calculează: ore × ${bani(s0.tarif_orar)} lei/oră (salariul de bază ${bani(s0.salariu_baza)} lei / orele normei lunii) × (100% + spor). Sporul e cel puțin 75% (Codul muncii art.123 alin.(2)).` : "Elementul intră în brut, în CAS, CASS și impozit și apare distinct pe fluturaș."}</div>
    <div id="el-msg"></div></div>`;
  const arata = () => {
    const tip = corp.querySelector("#el-tip").value;
    corp.querySelector("#el-ore-camp").hidden = corp.querySelector("#el-spor-camp").hidden = tip !== "ore_suplimentare";
    corp.querySelector("#el-suma-camp").hidden = !tip || tip === "ore_suplimentare";
  };
  corp.querySelector("#el-tip").addEventListener("change", arata);
  arata();
  corp.querySelector("#el-renunta").addEventListener("click", () => nav.inapoi());
  corp.querySelectorAll(".el-sterge").forEach((x) => x.addEventListener("click", () => {
    confirmaCaseta(x.parentElement || x, "Ștergi elementul de salariu? Statul se recalculează.", async () => {
      try { await api.del(`/tenants/${t.id}/salariati/${sid}/elemente/${x.dataset.id}`); ecranElemente(corp, nav, t, sid, nume, an, luna); }
      catch (e) { arataMesaj(corp.querySelector("#el-msg"), (e && e.mesaj) || "Nu s-a șters.", "eroare"); }
    });
  }));
  corp.querySelector("#el-adauga").addEventListener("click", async () => {
    curataEroriCamp(corp);
    if (cereAlegerile(corp, ["#el-tip"])) return;   // [FAPT_FISCAL_NECERUT] tipul se alege
    const tip = corp.querySelector("#el-tip").value;
    const v = (id) => corp.querySelector(id).value.trim();
    const n = (id) => sumaRo(corp.querySelector(id));
    const cerere = { an, luna, tip, denumire: v("#el-denumire") };
    let lipsa = false;
    if (tip === "ore_suplimentare") {
      cerere.ore = n("#el-ore");
      cerere.spor_procent = n("#el-spor");
      if (Number.isNaN(cerere.ore)) { eroareCamp(corp, "el-ore", "Scrie orele cu virgulă la zecimale (ex. 7,5)."); lipsa = true; }
      if (Number.isNaN(cerere.spor_procent)) { eroareCamp(corp, "el-spor", "Scrie sporul în procente (ex. 75)."); lipsa = true; }
    } else {
      cerere.suma = n("#el-suma");
      if (Number.isNaN(cerere.suma)) { eroareCamp(corp, "el-suma", MESAJ_NUMAR_RO); lipsa = true; }
    }
    if (lipsa) return;
    try {
      const rez = await api.post(`/tenants/${t.id}/salariati/${sid}/elemente`, cerere);
      await ecranElemente(corp, nav, t, sid, nume, an, luna);
      arataMesaj(corp.querySelector("#el-msg"), `S-a adăugat: ${cerere.denumire} — ${bani(rez && rez.suma)} lei.${rez && rez.avertisment ? " " + rez.avertisment : ""}`,
        rez && rez.avertisment ? "avert" : "ok");
    } catch (e) {
      const ec = (e && e.erori_campuri) || [];
      ec.forEach((x) => eroareCamp(corp, x.camp === "tip" ? "el-tip" : "el-" + x.camp, x.mesaj));
      if (!ec.length) arataMesaj(corp.querySelector("#el-msg"), (e && e.mesaj) || "Elementul nu s-a salvat.", "eroare");
    }
  });
}

// [lot 19 pct.4c] Suspendari FARA drepturi salariale (CFP / suspendare) - Codul muncii art.49 alin.(2), art.54, art.153.
// Statul de plata si D112 proratizeaza brutul pe zilele lucratoare active. DS cap.24: lista se RE-RANDEAZA din model,
// fiecare rand se poate sterge (.buton-sters), id-uri {prefix}{i}-{camp}; validarea e a backendului.
const TIP_SUSP = [["cfp", "Concediu fără plată"], ["suspendare", "Suspendare fără drepturi salariale"]];
function ecranSuspendari(corp, nav, t, sal, dupa) {
  const sid = sal.id;
  const model = (sal.suspendari || []).map((x) => ({ ...x }));
  const citeste = () => model.forEach((x, i) => {
    x.data_inceput = corp.querySelector(`#susp${i}-inceput`).value;
    x.data_sfarsit = corp.querySelector(`#susp${i}-sfarsit`).value;
    x.tip = corp.querySelector(`#susp${i}-tip`).value;
    x.temei = corp.querySelector(`#susp${i}-temei`).value.trim();
  });
  const randeaza = () => {
    const lista = model.length
      ? model.map((x, i) => `<div class="grila-campuri" style="max-width:none;margin:6px 0">
          <label class="camp"><span class="camp-eticheta">De la<span class="oblig">*</span></span><input type="date" id="susp${i}-inceput" class="camp-input" value="${esc(x.data_inceput || "")}"></label>
          <label class="camp"><span class="camp-eticheta">Până la<span class="oblig">*</span></span><input type="date" id="susp${i}-sfarsit" class="camp-input" value="${esc(x.data_sfarsit || "")}"></label>
          <div class="camp"><span class="camp-eticheta">Tip<span class="oblig">*</span></span>${selectScurt(`susp${i}-tip`, TIP_SUSP, x.tip || "", "Tipul suspendării")}</div>
          <label class="camp"><span class="camp-eticheta">Act / temei</span><input id="susp${i}-temei" class="camp-input" value="${esc(x.temei || "")}"></label>
          <div class="camp"><button class="buton-sters buton-mic" data-susp-sterge="${i}" data-fara-actiune="rând în formular; salvarea formularului poartă acțiunea">Șterge</button></div></div>`).join("")
      : `<div class="stare-goala stare-goala--inline">Nicio suspendare înregistrată: luna se plătește pe toate zilele din contract.</div>`;
    corp.innerHTML = `<h2 class="pf-titlu">Suspendări contract</h2>
      <p class="pf-intro">Concediul fără plată și suspendarea fără drepturi salariale scad brutul pe zilele lucrătoare din interval (Codul muncii art.49 alin.(2)), în statul de plată și în D112.</p>
      <div id="susp-lista">${lista}</div>
      <p style="margin-top:8px"><button class="buton-secundar" id="susp-adauga" data-fara-actiune="rând în formular; salvarea formularului poartă acțiunea">+ Adaugă</button></p>
      ${baraActiune(`<button class="buton-primar" id="susp-save" data-actiune="PUT /tenants/{tenant_id}/salariati/{salariat_id}">Salvează</button>`, "susp-msg")}`;
    legaRenunta(corp, nav);
    corp.querySelectorAll("[data-susp-sterge]").forEach((x) => x.addEventListener("click", () => {
      citeste(); model.splice(Number(x.dataset.suspSterge), 1); randeaza();
    }));
    corp.querySelector("#susp-adauga").addEventListener("click", () => {
      citeste(); model.push({ data_inceput: "", data_sfarsit: "", tip: "", temei: "" }); randeaza();
    });
    corp.querySelector("#susp-save").addEventListener("click", async (ev) => {
      citeste();
      curataEroriCamp(corp);
      if (cereAlegerile(corp, model.map((_x, i) => `#susp${i}-tip`))) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
      const btn = ev.currentTarget;
      btn.disabled = true; btn.textContent = "Se salvează…";
      try {
        await api.put(`/tenants/${t.id}/salariati/${sid}`, { suspendari: model });
        dupa(`Suspendările lui ${sal.nume} au fost salvate (${model.length}). Statul de plată și D112 calculează brutul pe zilele active din contract.`);
      } catch (e) {
        btn.disabled = false; btn.textContent = "Salvează";
        arataMesaj(corp.querySelector("#susp-msg"), (e && e.mesaj) || "Eroare la salvare.", "eroare");
      }
    });
  };
  randeaza();
}

function ecranRegesSalariat(corp, nav, t, s) {
  corp.innerHTML = `<h2 class="pf-titlu">Trimitere în REGES</h2>
    <div class="grila-campuri"><label class="camp"><span class="camp-eticheta">Adresa salariatului<span class="oblig">*</span></span>
      <input type="text" id="rg-adresa" class="camp-input" placeholder="strada, nr., localitate, județ">
      <span class="camp-ajutor">Obligatorie pentru transmiterea în REGES.</span></label></div>
    ${baraActiune(`<button class="buton-primar" id="rg-trimite" data-actiune="POST /tenants/{tenant_id}/reges-trimite-salariat">Trimite în REGES</button>`, "rg-rez")}`;
  legaRenunta(corp, nav);
  corp.querySelector("#rg-trimite").addEventListener("click", async () => {
    const adresa = corp.querySelector("#rg-adresa").value.trim();
    const rez = corp.querySelector("#rg-rez");
    curataEroriCamp(corp);
    // [lotul 11, 440] lângă câmp, prin helper (intră în caseta „NU s-a salvat.”)
    if (cereCompletate(corp, [{ id: "rg-adresa", mesaj: "Completează adresa salariatului." }])) return;
    const btn = corp.querySelector("#rg-trimite");
    btn.disabled = true; btn.textContent = "Se trimite…";
    try {
      await api.post(`/tenants/${t.id}/reges-trimite-salariat`, { salariat_id: s.id, adresa });
      // [C5 clasa, 07.10.2026] referința sosește la Răspunsuri REGES.
      arataMesaj(rez, "Trimis în REGES. Referința salariatului sosește la „Răspunsuri REGES” (statul de plată).", "ok");
      btn.textContent = "Trimis";
    } catch (e) { btn.disabled = false; btn.textContent = "Trimite în REGES"; arataRefuzul(corp, e, rez, { campuri: { adresa: "rg-adresa" } }); }   // [lotul 11, 440]
  });
}

// [R33, decizia Costin 25.08.2026] Semnalul de coerenta nota-vs-D112, LA PROPUNERE. SEMNALEAZA, nu blocheaza: aplicatia compara o
// propunere cu o declaratie generata din alte date, iar cand cele doua difera nu se stie CARE greseste. Semnalul arata AMBELE cifre si
// diferenta. [lotul 13, 673] Propunerea se deschide în fereastra ei, nu sub lista statului.
async function ecranContareStat(corp, nav, t, an, luna, propunere) {
  corp.innerHTML = `<div class="rezumat-fix"><h2 class="pf-titlu">Contabilizarea statului · ${_lunaTxt(an, luna)}</h2></div><div id="sp-contare-zona"></div>`;
  const zonaContare = corp.querySelector("#sp-contare-zona");
  const randDivergente = (p) => !p.divergente.length
    // [lot 06.10 pct.11] verdele spune CE s-a verificat: soldul 421 egal la ban cu netul fluturașilor (fără toleranță)
    ? `<div class="caseta-info"><span class="ci-mesaj">Contul 421 se soldează exact cu netul fluturașilor (${bani(p.net_fluturasi)} lei).${p.net_cm_fluturasi != null ? ` Contul 423 se soldează exact cu netul indemnizațiilor de concediu medical (${bani(p.net_cm_fluturasi)} lei).` : ""} CAS, CASS, impozitul și CAM sunt cele declarate în D112.</span></div>`
    : `<div class="caseta-atentie">
        <b>Nota propusă nu se potrivește pe ${cate(p.divergente.length, "cont", "conturi")}.</b>
        ${p.divergente.some((d) => d.fata_de === "D112") ? `<div class="tip-micut">Nu se blochează nimic: nu se poate ști din afară care dintre cele două greșește — poate declarația e veche, poate nota e corectă.</div>` : ""}
        ${p.divergente.some((d) => d.cont === "421") ? `<div class="tip-micut">Pe 421: după plata netului de pe fluturași, contul ar rămâne cu diferența de mai sus — nota debitează rețineri pentru care nu are brutul corespunzător.</div>` : ""}
        ${p.divergente.some((d) => d.cont === "423") ? `<div class="tip-micut">Pe 423: după plata indemnizațiilor nete de pe fluturași, contul ar rămâne cu diferența de mai sus — reținerile declarate pe indemnizație nu sunt cele din certificatele salvate.</div>` : ""}
        <table class="fd-tabel" style="margin-top:8px">
          <thead><tr><th>Ce</th><th>Cont</th><th>Nota ar scrie</th><th>Față de</th><th>Diferență</th></tr></thead>
          <tbody>${p.divergente.map((d) => `<tr>
            <td>${esc(d.eticheta)}</td>
            <td>${esc(d.cont)}</td>
            <td>${bani(d.nota)}</td>
            <td>${esc(d.fata_de)}: ${bani(d.declaratie)}</td>
            <td style="color:var(--rosu);font-weight:600">${bani(d.diferenta)}</td>
          </tr>`).join("")}</tbody>
        </table>
        <div class="tip-micut">${p.divergente.some((d) => d.fata_de === "D112") ? `Toleranța față de D112: ${bani(p.divergente.find((d) => d.fata_de === "D112").toleranta)} lei (${cate(p.nr_salariati, "salariat", "salariați")}). ` : ""}Contul 421 se compară fără toleranță.</div>
      </div>`;
  const arataPropunerea = (p) => {
    zonaContare.innerHTML = `<div class="pf-frand" style="display:block;margin:10px 0">
      <div class="pf-frand-nume">${esc(p.document_ref)} — ${cate(p.note.length, "linie", "linii")}, total ${bani(p.total)} lei</div>
      ${randDivergente(p)}
      <table class="fd-tabel" style="margin-top:8px">
        <thead><tr><th>Debit</th><th>Credit</th><th>Sumă</th></tr></thead>
        <tbody>${p.note.map((n) => `<tr><td>${esc(n.debit)}</td><td>${esc(n.credit)}</td><td>${bani(n.suma)}</td></tr>`).join("")}</tbody>
      </table>
      <div class="bara-fixa"><p style="margin-top:10px">${p.neincheiata
        // [deficiența 414] luna în curs: niciun buton care scrie nota (serverul o refuză, `_cere_luna_incheiata`) — nici înlocuirea, nici
        // recontabilizarea; ciorna veche, scrisă înainte de încheierea lunii, se spune și se reface după
        ? `<span class="caseta-info" style="display:block" id="sp-contare-neincheiata"><span class="ci-mesaj">Nota salariilor se scrie după ce luna se încheie: ${esc(p.neincheiata)}${p.deja_contata && p.ciorna_alte_sume ? ` Ciorna ${esc(p.nota_eticheta || "")} din jurnal a fost scrisă înainte de încheierea lunii, din alte sume: după încheiere, „Înlocuiește ciorna” o reface din statul de atunci.` : ""}</span></span>`
        : p.deja_contata
        ? (p.ciorna_alte_sume
          // [retest 08.10 pct.1, decizia Costin] „nu rămâne niciodată o ciornă cu alte sume decât statul afișat”
          ? `<span class="caseta-atentie" style="display:block"><span class="ca-mesaj">Ciorna ${esc(p.nota_eticheta || "")} din jurnal are alte sume decât statul afișat — e scrisă din statul de dinainte. Contabilizarea o înlocuiește cu nota de mai sus.</span></span>
             <button class="buton-primar" id="sp-contare-scrie" style="margin-top:8px" data-genereaza-nota="redesenat" data-actiune="POST /tenants/{tenant_id}/salarii-contare|POST /tenants/{tenant_id}/salarii-contare/propunere">Înlocuiește ciorna cu nota din statul de acum</button>`
          : p.validare && p.validare.stare_coada === "respinsa"
          // [lotul 07.10 B, C9] nota derivată din stat se corectează din stat: recontabilizarea o înlocuiește și o retrimite
          ? `<span class="caseta-atentie" style="display:block"><span class="ca-mesaj">Nota ${esc(p.nota_eticheta || "")} a fost respinsă la validare: ${esc(motivInFraza(p.validare.motiv_respingere))} Se corectează din statul de plată: după corectare, recontabilizarea scrie nota din nou, o înlocuiește pe cea respinsă și o trimite la validare.</span></span>
             <button class="buton-primar" id="sp-contare-scrie" style="margin-top:8px" data-genereaza-nota="redesenat" data-actiune="POST /tenants/{tenant_id}/salarii-contare|POST /tenants/{tenant_id}/salarii-contare/propunere">Recontabilizează statul</button>`
          : `<span class="${p.validare && p.validare.stare_coada === "la_senior" ? "caseta-info" : "tip-micut"}" style="display:block"><span class="ci-mesaj">${p.validare && p.validare.stare_coada === "la_senior" ? `Nota ${esc(p.nota_eticheta || "")} e la validare în cabinet.`
            // [lotul 12, C165] starea din notă (nota_status), nu numai din coadă: o notă validată direct n-are element în coadă
            : (p.nota_status === "validata" || (p.validare && p.validare.stare_coada === "aprobata") ? `Nota ${esc(p.nota_eticheta || "")} e validată.` : `Nota există deja în jurnal (${esc(p.nota_eticheta || "")}, ciornă).`)}${p.divergente.length ? " Diferențele de mai sus se recalculează la fiecare deschidere: rămân afișate până când nota și declarația au aceleași cifre." : ""}</span></span>`)
        : (`<button class="buton-primar" id="sp-contare-scrie" data-genereaza-nota="redesenat" data-actiune="POST /tenants/{tenant_id}/salarii-contare|POST /tenants/{tenant_id}/salarii-contare/propunere">Scrie nota ciornă</button>
           <span class="tip-micut" style="margin-left:8px">Ciornă, nu validată: validării îi rămâne al doilea om.</span>`)}</p></div>   <!-- [lotul 10, 421 / 424, DS cap.9 v2.97 pct.6] acțiunea notei, lipită jos -->
    </div>`;
    const b = corp.querySelector("#sp-contare-scrie");
    if (b) b.addEventListener("click", async () => {
      b.disabled = true; b.textContent = "Se scrie…";
      try {
        const scrisa = await api.post(`/tenants/${t.id}/salarii-contare?an=${an}&luna=${luna}`, {});
        if (scrisa && scrisa.cod === "NESCHIMBATA") {
          // [S3] aceeași notă ca cea respinsă: avertisment cu motivul alături + confirmare explicită (nu blocaj)
          b.disabled = false; b.textContent = "Recontabilizează statul";
          confirmaCaseta(b.parentElement || b, scrisa.mesaj, async () => {
            await api.post(`/tenants/${t.id}/salarii-contare?an=${an}&luna=${luna}&confirma=true`, {});
            const p2 = await api.post(`/tenants/${t.id}/salarii-contare/propunere?an=${an}&luna=${luna}`, {});
            arataPropunerea(p2);
            // [258] nota numită ca în Registrul jurnal (`nota_eticheta`), nu prin id; cea respinsă nu mai există, deci nu se numește
            zonaContare.insertAdjacentHTML("afterbegin", `<div class="caseta-info"><span class="ci-mesaj">Nota respinsă a fost înlocuită cu nota ${esc(p2.nota_eticheta || "")}, fără schimbări (confirmat), și trimisă la validare.</span></div>`);
          }, { textOk: "Retrimite fără schimbări" });
          return;
        }
        // [validare_note] propunerea se recitește: arată nota scrisă ȘI unde a ajuns în coada de validare
        const p2 = await api.post(`/tenants/${t.id}/salarii-contare/propunere?an=${an}&luna=${luna}`, {});
        arataPropunerea(p2);
        // [8c] confirmarea pe drumul unic (stil de succes, conturile și sumele notei scrise), deasupra propunerii refăcute
        const zConf = document.createElement("div");
        zonaContare.prepend(zConf);
        dupaGenerare(zConf, null, { titlu: `Nota salariilor ${_lunaTxt(an, luna)} e scrisă`,
          eticheta: `Nota ${p2.nota_eticheta || ""}`, linii: p2.note,
          pas: scrisa && scrisa.cod === "INLOCUITA" ? `Nota respinsă a fost înlocuită cu nota ${esc(p2.nota_eticheta || "")}, scrisă din statul de acum, și trimisă la validare.`
            : scrisa && scrisa.cod === "CIORNA_INLOCUITA" ? `Ciorna cu sumele statului de dinainte a fost înlocuită cu nota ${esc(p2.nota_eticheta || "")}, scrisă din statul de acum — ciornă de validat.`   // [retest 08.10 pct.1]
            : `Nota e ${stareNota(scrisa)}. ${pasNota(scrisa)}` });
      } catch (e) {
        b.disabled = false; b.textContent = "Scrie nota ciornă";
        arataMesaj(zonaContare, (e && e.mesaj) || "Nu s-a putut scrie nota.", "eroare");
      }
    });
  };
  arataPropunerea(propunere);
}

// [F134] fisier de plata pe card (SEPA pain.001): preview (cati, total, cine fara IBAN) -> download
async function ecranPlataCard(corp, nav, t, an, luna) {
  corp.innerHTML = `<p class="ecran-nota">Se pregătește...</p>`;
  let m;
  try { m = await api.get(`/tenants/${t.id}/plata-salarii-preview?an=${an}&luna=${luna}`); }
  catch (e) { corp.innerHTML = ""; arataMesaj(corp, (e && e.mesaj) || "Nu se poate genera fișierul.", "eroare"); return; }
  const avert = (m.fara_iban && m.fara_iban.length)
    ? `<div class="caseta-atentie"><span class="ca-mesaj">${cate(m.fara_iban.length, "salariat fără IBAN, exclus", "salariați fără IBAN, excluși")} din fișier: ${m.fara_iban.map(esc).join(", ")}. IBAN-ul se completează din fereastra salariatului.</span></div>`
    : "";
  corp.innerHTML = `<h2 class="pf-titlu">Plată salarii pe card · ${_lunaTxt(an, luna)}</h2>
    <p class="pf-intro">${cate(m.nr_plati, "plată", "plăți")} · total ${bani(m.total)} lei · format SEPA pain.001</p>
    ${avert}
    <div class="bara-fixa"><p style="margin-top:8px"><button class="buton-primar" id="plata-descarca" data-actiune="POST /tenants/{tenant_id}/plata-salarii-fisier">Descarcă fișierul</button>
      <button class="buton-secundar" data-renunta style="margin-left:6px">Închide</button></p><div id="plata-msg"></div></div>`;
  legaRenunta(corp, nav);
  corp.querySelector("#plata-descarca").addEventListener("click", async () => {
    try {
      // [R45] POST: producerea fisierului care pleaca la banca e un act, si se pastreaza.
      await descarca(`/tenants/${t.id}/plata-salarii-fisier?an=${an}&luna=${luna}`, `plata_salarii_${an}_${String(luna).padStart(2, "0")}.xml`, { metoda: "POST" });
      arataMesaj(corp.querySelector("#plata-msg"), "Fișierul de plată s-a descărcat.", "ok");
    } catch (e) { arataMesaj(corp.querySelector("#plata-msg"), (e && (e.mesaj || e.message)) || "eroare", "eroare"); }   // [R131]
  });
}

function ecranCheiReges(corp, nav, t) {
  corp.innerHTML = `<h2 class="pf-titlu">Chei API REGES</h2>
    <p class="pf-intro">Din aplicația REGES Angajator.</p>
    <div class="grila-campuri">
      <label class="camp"><span class="camp-eticheta">Username</span><input type="text" id="rg-user" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Parola</span><input type="password" id="rg-pass" class="camp-input"></label>
      <div class="camp"><span class="camp-eticheta">Mediu<span class="oblig">*</span></span>${selectScurt("rg-mediu", [["test", "Test"], ["prod", "Producție"]], "", "Mediul REGES")}</div>
    </div>
    ${baraActiune(`<button class="buton-primar" id="rg-salveaza" data-actiune="POST /tenants/{tenant_id}/reges-config">Salvează</button>`, "rg-msg")}`;
  legaRenunta(corp, nav);
  corp.querySelector("#rg-salveaza").addEventListener("click", async () => {
    const m = corp.querySelector("#rg-msg");
    curataEroriCamp(corp);
    if (cereAlegerile(corp, ["#rg-mediu"])) return;
    try {
      await api.post(`/tenants/${t.id}/reges-config`, {
        username: corp.querySelector("#rg-user").value,
        parola: corp.querySelector("#rg-pass").value,
        mediu: corp.querySelector("#rg-mediu").value });
      arataMesaj(m, "Cheile REGES s-au salvat.", "ok");
    } catch (e) { arataMesaj(m, e.mesaj || "eroare", "eroare"); }
  });
}

function ecranRaspunsReges(corp, nav, t, r) {
  corp.innerHTML = `<h2 class="pf-titlu">Răspunsuri REGES</h2><div id="rg-raspuns"></div>`;
  const z = corp.querySelector("#rg-raspuns");
  {
    // [C5 clasa, comanda Costin 07.10.2026] spune ce a venit, pentru ce mesaj și dacă s-a păstrat (DS cap.27)
    const ce = !r || !r.primit ? "Niciun răspuns nou."
      : r.message_id
      ? `Răspuns primit pentru mesajul ${esc(r.message_id)}`
        + (r.referinta_salariat ? ` · referința salariatului ${esc(r.referinta_salariat)}` : "")
        + (r.referinta_contract ? ` · referința contractului ${esc(r.referinta_contract)}` : "")
        + (r.salvat ? " · păstrat în evidența mesajelor REGES ale firmei."
                    : " · mesajul nu e unul trimis de firma aceasta — nu s-a păstrat.")
      : `REGES a răspuns fără identificator de mesaj (nu s-a păstrat): ${esc(textScurt(r.raspuns, 300))}`;
    z.innerHTML = `<div class="caseta-info"><span class="ci-mesaj">${ce}</span></div>`;
  }
}




// [stocuri-cv] Fise de magazie (cantitativ-valoric)
// [05.10.2026, comanda Costin pct.10] Situația stocului: articol · UM · cantitate · CMP · valoare, cu totalul valorii. Se
// desenează în `#s-situatie` (ecranul Stocuri) din aceeași listă de articole ca formularele, deci se reîmprospătează odată cu ele.
function randeazaSituatiaStocului(corp, arts) {
  const z = corp.querySelector("#s-situatie");
  if (!z) return;
  if (!arts.length) { z.innerHTML = `<div class="stare-goala">Niciun articol în gestiune. Intrările se fac prin NIR sau din „Mișcări, fișe de magazie”.</div>`; return; }
  const total = arts.reduce((s, a) => s + (Number(a.valoare) || 0), 0);
  z.innerHTML = `<table class="fd-tabel" id="s-situatie-tabel">
    <thead><tr><th>Articol</th><th>UM</th><th class="fd-td-num">Cantitate</th><th class="fd-td-num">CMP (lei)</th><th class="fd-td-num">Valoare (lei)</th></tr></thead>
    <tbody>${arts.map((a) => `<tr><td>${esc(a.denumire)}</td><td>${esc(a.um || "")}</td><td class="fd-td-num">${cantitate(a.stoc)}</td>
      <td class="fd-td-num">${a.cmp == null ? "\u2014" : pretUnitar(a.cmp)}</td><td class="fd-td-num">${bani(a.valoare)}</td></tr>`).join("")}</tbody>
    <tfoot><tr><td colspan="4"><b>Total valoare stoc</b></td><td class="fd-td-num"><b>${bani(total)}</b></td></tr></tfoot>
  </table>`;
}

// [lotul 13, deficiențele 612 și 673, comanda Costin 13.1, verbatim: „612: Inventar (F1) | Rândul cu lipsă e înghesuit (rămas de la 404)”]
// Inventarul (stocul faptic) în fereastra lui (DS cap.2a v2.104), ca tabel: un rând pe articol — articolul, UM, scripticul, faptic —, iar
// la lipsă (faptic sub scriptic) încadrarea ei, cota TVA și suma imputată pe un rând al lor, sub articol, pe toată lățimea: denumirea nu
// mai stă pe același rând cu cele trei câmpuri (era ruptă pe 5 rânduri, apoi „înghesuită” lângă ele). [676] Încadrarea = trei butoane
// alăturate (`data-butoane`), cu diacritice (606). Câmpurile și cererea sunt cele de până acum (`cvi-a<id>-…`, `POST /stocuri/inventar`).
const LIPSE_INVENTAR = [["imputabila", "lipsă imputabilă"], ["neimputabila", "lipsă neimputabilă"],
  ["justificata", "lipsă justificată (distrusă, pierdută, furată — dovedit)"]];
function ecranInventarCV(corp, nav, t, arts, cheie) {
  corp.innerHTML = `
    <div class="rezumat-fix"><h2 class="pf-titlu">Inventar — stoc faptic</h2>
      <p class="pf-intro">Scrie stocul numărat; la o lipsă alege încadrarea ei. Articolul lăsat gol nu se inventariază.</p>
      <label class="camp" style="max-width:220px"><span class="camp-eticheta">Data inventarului</span><input type="date" id="cvi-data" class="camp-input" value="${dataIso()}"></label></div>
    ${!arts.length ? `<div class="stare-goala">Niciun articol în gestiune.</div>` : `<table class="fd-tabel" id="cvi-tabel">
      <thead><tr><th>Articol</th><th>UM</th><th class="fd-td-num">Scriptic</th><th>Faptic</th></tr></thead>
      ${arts.map((a) => `<tbody class="cvi-articol" data-aid="${a.id}">
        <tr id="cvi-a${a.id}-rand"><td><span class="cvi-denumire">${esc(a.denumire)}</span></td><td>${esc(a.um || "")}</td><td class="fd-td-num">${esc(cantitate(a.stoc))}</td>
          <td><input type="number" step="0.001" class="camp-input cvi-faptic" id="cvi-a${a.id}-faptic" data-aid="${a.id}" aria-label="Stoc faptic ${esc(a.denumire)}" style="width:120px"></td></tr>
        <tr class="cvi-lipsa-rand" id="cvi-a${a.id}-lipsa-zona" hidden><td colspan="4"><div class="grila-campuri">
          <div class="camp"><span class="camp-eticheta">Încadrarea lipsei</span><select class="camp-input" id="cvi-a${a.id}-lipsa" data-butoane aria-label="Lipsa ${esc(a.denumire)}">${ALEGE}${LIPSE_INVENTAR.map(([v, l]) => `<option value="${v}">${l}</option>`).join("")}</select></div>
          <label class="camp"><span class="camp-eticheta">Cota TVA dedusă (gol = cea din nomenclator)</span><input type="number" step="0.01" class="camp-input" id="cvi-a${a.id}-cota" aria-label="Cota TVA ${esc(a.denumire)}"></label>
          <label class="camp"><span class="camp-eticheta">Suma imputată, la lipsa imputabilă (lei)</span><input type="number" step="0.01" class="camp-input" id="cvi-a${a.id}-imputat" aria-label="Suma imputată ${esc(a.denumire)}"></label>
        </div></td></tr></tbody>`).join("")}
    </table>`}
    <div class="bara-fixa"><p style="margin-top:8px"><button class="buton-primar" id="cvi-salveaza" data-genereaza-nota="redesenat" data-actiune="POST /tenants/{tenant_id}/stocuri/inventar">Salvează inventarul (note ciorne)</button>
      <button type="button" class="buton-secundar" data-renunta data-fara-actiune="închide fereastra, fără scriere" style="margin-left:6px">Renunță</button></p>
    <div id="cvi-mesaj"></div></div>`;
  legaRenunta(corp, nav);
  // [deficiența 404] faptic sub scriptic = lipsă: încadrarea ei (imputabilă / neimputabilă / justificată) se cere pe rândul de sub articol
  corp.querySelectorAll(".cvi-faptic").forEach((i) => i.addEventListener("input", () => {
    const lipsa = i.value.trim() !== "" && Number(i.value) < Number((arts.find((x) => String(x.id) === i.dataset.aid) || {}).stoc);
    corp.querySelector(`#cvi-a${i.dataset.aid}-lipsa-zona`).hidden = !lipsa;
  }));
  corp.querySelector("#cvi-salveaza").addEventListener("click", async () => {
    const zm = corp.querySelector("#cvi-mesaj");
    curataEroriCamp(corp);
    // NU se filtreaza randuri (cap.24 regula 2): se trimit TOATE articolele; backendul e autoritatea (sare
    // articolele necontorizate = faptic gol, NU e eroare; eroare per-linie doar la valoare invalida).
    const linii = [...corp.querySelectorAll(".cvi-faptic")]
      .map((i) => {
        const g = (suf) => (corp.querySelector(`#cvi-a${i.dataset.aid}-${suf}`) || {}).value || "";
        return { articol_id: parseInt(i.dataset.aid), faptic: i.value.trim() === "" ? null : i.value.trim(),
          lipsa: g("lipsa") || null, cota_tva: g("cota") === "" ? null : Number(g("cota")), suma_imputata: g("imputat") === "" ? null : Number(g("imputat")) };   // [404]
      });
    if (!linii.some((l) => l.faptic !== null)) { arataMesaj(zm, "Completează stocul faptic la cel puțin un articol.", "eroare"); return; }
    const dataInv = corp.querySelector("#cvi-data").value || dataIso();
    try {
      const r = await api.post(`/tenants/${t.id}/stocuri/inventar`, { data: dataInv, linii });
      const rezultate = r.rezultate || [];
      const cuEroare = rezultate.filter((x) => x.eroare && x.camp);
      cuEroare.forEach((x) => eroareCamp(corp, x.camp, x.eroare));
      const rest = rezultate.filter((x) => !(x.eroare && x.camp));
      const randInv = (x) => x.eroare ? `${x.denumire || x.articol_id}: ${x.eroare}`
        : x.diferenta === "0" ? `${x.denumire}: fără diferență`
        : `${x.denumire}: ${x.diferenta > 0 ? "plus" : "minus"} ${cantitate(Math.abs(Number(x.diferenta)))} · ${bani(x.valoare)} lei · nota ${x.nota} (${stareNota(r)})${x.semnal ? " · " + x.semnal.motiv : ""}`;
      if (cuEroare.length) {   // erorile de câmp rămân lângă câmpurile lor, în fereastra inventarului; restul, sub buton
        if (rest.length) zm.innerHTML = `<p class="pf-intro">${rest.map((x) => esc(randInv(x))).join("<br>")}</p>`;
        return;
      }
      const ids = rest.map((x) => x.inregistrare_id).filter(Boolean);
      // [8c] notele diferențelor, pe drumul unic al confirmării (conturile și sumele din jurnal), în Stocuri, după închiderea ferestrei
      const note = ids.length ? await noteGenerate(t.id, ids, dataInv) : null;
      inchideCuConfirmarea(nav, cheie, note
        ? (zonaS) => dupaGenerare(zonaS, null, { titlu: `Inventarul din ${dataRo(dataInv)}: ${cate(ids.length, "notă a diferențelor", "note ale diferențelor")}, ${stareNota(r, ids.length > 1)}`,
          note, detalii: rest.map(randInv) })
        : rest.map((x) => esc(randInv(x))).join("<br>"));
    } catch (e) { arataRefuzul(corp, e, zm); }
  });
}

// [C103] fișele reîncărcate după mișcări în șir: numai articolele cerute ultimele ajung pe ecran. [lotul 12, 628] contorul e al ferestrei
// (`ultimaCerere(corp)`), nu al modulului: cu unul comun, o reîncărcare într-o fereastră (Stocuri, altă firmă / altă deschidere) scotea din
// joc cererea în zbor a celeilalte, care rămânea pe „Se încarcă situația stocului...” sau pe lista de dinainte
// [lotul 13, 673] situația stocului (tabelul articolelor), citită și desenată o dată, pentru fereastra Stocuri și pentru secțiunea
// mișcărilor; jetonul e al ferestrei (contorul e al ferestrei, `ultimaCerere(corp)` — C177). Întoarce răspunsul sau null (depășită).
async function incarcaSituatiaStocului(corp, t) {
  const actuala = ultimaCerere(corp)();
  let r = {};
  try { r = await api.get(`/tenants/${t.id}/stocuri/articole`) || {}; } catch { if (!actuala()) return null; r = {}; }
  if (!actuala()) return null;
  randeazaSituatiaStocului(corp, r.articole || []);
  return r;
}

export async function sectiuneaCV(corp, t, zonaM, nav = null) {   // [lotul 13, 673] `nav`: ferestrele acțiunilor
  const zona = corp.querySelector("#cv-zona");
  // [05.10.2026, pct.10] situația se reîmprospătează odată cu formularele
  const rArt = await incarcaSituatiaStocului(corp, t);
  if (!rArt) return;
  // jetonul de după situație: continuarea rulează imediat după răspuns (microtask), deci nicio cerere nouă nu poate porni între ele
  const actuala = ultimaCerere(corp)();
  const arts = rArt.articole || [], reteteVizibile = !!rArt.retete_vizibile;
  let locInit = [];
  try { const r = await api.get(`/tenants/${t.id}/stocuri/locatii`); locInit = r.locatii || []; } catch {}
  if (!actuala()) return;
  zona.innerHTML = `
    <div style="display:block;margin-bottom:14px">
      <div class="pf-frand-nume" style="margin-bottom:8px">Fi\u0219e de magazie (cantitativ-valoric, CMP)</div>
      <div class="camp-eticheta">Mi\u0219care: articol \u00b7 denumire (nou) \u00b7 dat\u0103 \u00b7 cantitate \u00b7 pre\u021b unitar \u00b7 document</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
        <input type="text" id="cv-art-cauta" class="camp-input" placeholder="Caută articolul în stoc…" aria-label="Caută articolul" autocomplete="off" style="min-width:180px">
        <select id="cv-art" aria-label="Articol" class="camp-input" style="min-width:200px">
          <option value="">\u2014 articol nou \u2014</option>
          ${arts.map((a) => `<option value="${a.id}">${esc(a.denumire)} \u00b7 stoc ${esc(cantitate(a.stoc, a.um))}${a.cmp ? " \u00b7 CMP " + pretUnitar(a.cmp) + " lei" : ""}${a.barcode ? " \u00b7 cod " + esc(a.barcode) : ""}</option>`).join("")}
        </select>
        <input type="text" id="cv-den" class="camp-input" placeholder="denumire (articol nou)" aria-label="Denumire articol nou" style="flex:1;min-width:160px">
        <input type="date" id="cv-data" aria-label="Data document" class="camp-input" value="${dataIso()}">
        <input type="number" step="0.001" id="cv-cant" class="camp-input" placeholder="cant." aria-label="Cantitate" style="width:90px">
        <input type="number" step="0.0001" id="cv-pret" class="camp-input" placeholder="preț unitar (la intrare)" aria-label="Pre\u021b unitar la intrare" style="width:170px">
        <input type="text" id="cv-doc" class="camp-input" placeholder="document" aria-label="Document" style="width:130px">
        <input type="text" id="cv-loc" class="camp-input" placeholder="locație" aria-label="Locație" list="cv-loc-list" style="width:120px">
        <datalist id="cv-loc-list">${[...new Set((locInit || []).map((x) => x.locatie).filter((l) => l && l !== "(nespecificat)"))].map((l) => `<option value="${esc(l)}">`).join("")}</datalist>
      </div>
      <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-bottom:8px">
        <input type="text" id="cv-bc" class="camp-input" placeholder="cod de bare (scaneaz\u0103/tasteaz\u0103)" aria-label="Cod de bare" style="width:220px">
        <button class="buton-secundar" id="cv-bc-cauta">Caut\u0103 articol dup\u0103 cod</button>
        <button class="buton-secundar" id="cv-bc-set" data-actiune="POST /tenants/{tenant_id}/stocuri/articole/{articol_id}/barcode">Atribuie codul articolului selectat</button>
        <input type="number" step="0.001" id="cv-nm" class="camp-input" placeholder="nivel minim" aria-label="Nivel minim de stoc" style="width:120px">
        <button class="buton-secundar" id="cv-nm-set" data-actiune="POST /tenants/{tenant_id}/stocuri/articole/{articol_id}/nivel-minim">Salveaz\u0103 nivelul minim</button>
      </div>
      <p>
        <button class="buton-primar" id="cv-intrare" data-actiune="POST /tenants/{tenant_id}/stocuri/intrare">Intrare</button>
        <button class="buton-primar" id="cv-iesire" data-actiune="POST /tenants/{tenant_id}/stocuri/iesire" style="margin-left:6px">Ie\u0219ire la CMP (nota ciorn\u0103)</button>
        <button class="buton-secundar" id="cv-fisa" style="margin-left:6px">Vezi fi\u0219a</button>
      </p>
      <div style="margin-top:10px">
        <button data-actiune="POST /tenants/{tenant_id}/stocuri/inventar" class="buton-secundar" id="cv-inv">Inventar (stoc faptic)</button>
        <button class="buton-secundar" id="cv-loc-vezi" style="margin-left:6px">Stoc pe locații</button>
        <button data-actiune="POST /tenants/{tenant_id}/stocuri/transfer" class="buton-secundar" id="cv-transfer-t" style="margin-left:6px">Transfer între locații</button>
        <button data-actiune="POST /tenants/{tenant_id}/stocuri/reclasificare" class="buton-secundar" id="cv-recl-t" style="margin-left:6px">Reclasificare tip produs</button>
        <button class="buton-secundar" id="cv-ana" style="margin-left:6px">Analitică stoc</button>
        <button data-actiune="POST /tenants/{tenant_id}/stocuri/inventar" class="buton-secundar" id="cv-inv-mobil" style="margin-left:6px">Inventar pe mobil</button>
        <div id="cv-inv-zona" style="margin-top:8px"></div>
        <div id="cv-loc-zona" style="margin-top:8px"></div>
      </div>
      <div id="cv-fisa-zona"></div>
      ${reteteVizibile ? `<div class="pf-card" style="margin-top:14px">
        <h3 class="pf-subtitlu">Re\u021bete (HoReCa)</h3>
        <div id="rt-lista"></div>
        <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;align-items:flex-end">
          <label class="camp"><span class="camp-eticheta">Denumire</span><input class="camp-input" id="rt-den" placeholder="ex. Meniu zilei"></label>
          <label class="camp"><span class="camp-eticheta">Pre\u021b f\u0103r\u0103 TVA</span><input class="camp-input" type="number" step="0.01" id="rt-pret" style="width:110px"></label>
          <button class="buton-secundar" id="rt-plus" data-fara-actiune="rând în formular; salvarea formularului poartă acțiunea">+ ingredient</button>
          <button class="buton-primar" id="rt-salveaza" data-actiune="POST /tenants/{tenant_id}/retete">Salveaz\u0103 re\u021beta</button>
        </div>
        <div id="rt-ingrediente"></div>
      </div>` : ""}

    </div>`;
  const val = (id) => zona.querySelector(id).value;
  // [lotul 11, 440] refuzul serverului pe fișa de magazie: fiecare eroare lângă câmpul ei (numele din cerere -> id-ul de pe ecran)
  const CAMPURI_CV = { data: "cv-data", cantitate: "cv-cant", pret_unitar: "cv-pret", document: "cv-doc", locatie: "cv-loc",
    articol_id: "cv-art", denumire: "cv-den", barcode: "cv-bc", nivel_minim: "cv-nm" };
  // [F141] Coduri de bare: cauta articolul dupa cod / atribuie cod articolului selectat
  zona.querySelector("#cv-bc-cauta").addEventListener("click", async () => {
    const cod = val("#cv-bc").trim();
    curataEroriCamp(zona);
    if (cereCompletate(zona, [{ id: "cv-bc", mesaj: "Scanează sau tastează un cod de bare." }])) return;   // [440] lângă câmp
    try {
      const a = await api.get(`/tenants/${t.id}/stocuri/barcode/${encodeURIComponent(cod)}`);
      zona.querySelector("#cv-art").value = String(a.id);
      arataMesaj(zonaM, `Selectat: ${esc(a.denumire)}.`, "ok");
    } catch (e) { arataRefuzul(zona, e, zonaM, { campuri: CAMPURI_CV }); }
  });
  zona.querySelector("#cv-bc-set").addEventListener("click", async () => {
    curataEroriCamp(zona);
    if (!val("#cv-art")) { eroareCamp(zona, "cv-art", "Alege întâi articolul din listă."); return; }   // [440] lângă câmp
    try {
      const r = await api.post(`/tenants/${t.id}/stocuri/articole/${parseInt(val("#cv-art"))}/barcode`, { barcode: val("#cv-bc").trim() });
      arataMesaj(zonaM, r.barcode ? `Cod „${esc(r.barcode)}” atribuit articolului.` : "Cod șters de pe articol.", "ok");
      sectiuneaCV(corp, t, zonaM, nav);
    } catch (e) { arataRefuzul(zona, e, zonaM, { campuri: CAMPURI_CV }); }
  });
  // [F140] Nivel minim de stoc (prag pentru stoc critic / necesar aprovizionare)
  zona.querySelector("#cv-nm-set").addEventListener("click", async () => {
    curataEroriCamp(zona);
    if (!val("#cv-art")) { eroareCamp(zona, "cv-art", "Alege întâi articolul din listă."); return; }   // [440] lângă câmp
    try {
      const r = await api.post(`/tenants/${t.id}/stocuri/articole/${parseInt(val("#cv-art"))}/nivel-minim`, { nivel_minim: val("#cv-nm").trim() });
      arataMesaj(zonaM, r.nivel_minim ? `Nivel minim ${cantitate(r.nivel_minim)} setat.` : "Nivel minim șters.", "ok");
      sectiuneaCV(corp, t, zonaM, nav);
    } catch (e) { arataRefuzul(zona, e, zonaM, { campuri: CAMPURI_CV }); }
  });
  // [comanda Costin 06.10.2026 pct.1c, clasa] fișa de magazie: un articol ALES și un nume de articol NOU scris în același timp — numele
  // era ignorat tacit (mișcarea mergea pe articolul ales). Acum se exclud: scrierea numelui trece lista pe „articol nou”, alegerea
  // unui articol golește numele.
  zona.querySelector("#cv-den").addEventListener("input", () => { if (val("#cv-den").trim()) zona.querySelector("#cv-art").value = ""; });
  zona.querySelector("#cv-art").addEventListener("change", () => { if (val("#cv-art")) zona.querySelector("#cv-den").value = ""; });
  cautaInLista(zona.querySelector("#cv-art-cauta"), zona.querySelector("#cv-art"));   // [488]
  zona.querySelector("#cv-intrare").addEventListener("click", async () => {
    curataEroriCamp(zona);
    try {
      const corpReq = { data: val("#cv-data"), cantitate: parseFloat(val("#cv-cant")) || 0,
        // [comanda Costin 06.10.2026 pct.1b, clasa] golul pleacă drept lipsă (serverul îl refuză), nu ca preț 0 pe care nu l-a ales nimeni
        pret_unitar: val("#cv-pret") === "" ? null : parseFloat(val("#cv-pret")), document: val("#cv-doc") || null,
        locatie: val("#cv-loc") || null };
      if (val("#cv-art")) corpReq.articol_id = parseInt(val("#cv-art"));
      else corpReq.denumire = val("#cv-den").trim();
      if (!corpReq.articol_id && !corpReq.denumire) { eroareCamp(zona, "cv-art", "Alege articolul sau da-i un nume."); return; }   // [440] lângă câmp
      const r = await api.post(`/tenants/${t.id}/stocuri/intrare`, corpReq);
      zonaM.innerHTML = `<p class="pf-intro">Intrare înregistrată \u00b7 ${bani(r.valoare)} lei.</p>`;
      sectiuneaCV(corp, t, zonaM, nav);
    } catch (e) { arataRefuzul(zona, e, zonaM, { campuri: CAMPURI_CV }); }
  });
  zona.querySelector("#cv-iesire").addEventListener("click", async () => {
    curataEroriCamp(zona);
    if (!val("#cv-art")) { eroareCamp(zona, "cv-art", "Alege articolul pentru ieșire."); return; }   // [440] lângă câmp
    try {
      const r = await api.post(`/tenants/${t.id}/stocuri/iesire`, {
        articol_id: parseInt(val("#cv-art")), data: val("#cv-data"),
        cantitate: parseFloat(val("#cv-cant")) || 0, document: val("#cv-doc") || null,
        locatie: val("#cv-loc") || null });
      zonaM.innerHTML = `<p class="pf-intro">Ieșire la CMP ${pretUnitar(r.cmp)} lei \u00b7 ${bani(r.valoare)} lei \u00b7 notă ${esc(r.nota)} (${stareNota(r)}).</p>`;
      sectiuneaCV(corp, t, zonaM, nav);
    } catch (e) { arataRefuzul(zona, e, zonaM, { campuri: CAMPURI_CV }); }
  });


  // [retete_v1] Retete HoReCa: CRUD + descarcare pe reteta + food cost. [05.10.2026, pct.10] numai la firma HoReCa
  // (CAEN din CF art.48 alin.(2^2) / art.54 alin.(4)) sau care are deja rețete — `retete_vizibile` de la server.
  if (reteteVizibile) legaRetete();
  function legaRetete() {
  const rtLista = zona.querySelector("#rt-lista");
  const rtIng = zona.querySelector("#rt-ingrediente");
  let rtLinii = [];
  const rtDeseneazaIng = () => {
    // cap.24: id-uri pozitionale rt-l{i}-* (backendul leaga eroarea de camp, cap.6); re-randare integrala din
    // model (regula 1); buton de stergere pe fiecare rand (regula 3).
    rtIng.innerHTML = rtLinii.map((l, i) => `
      <div class="em-linie" data-idx="${i}">
        <input type="text" class="camp-input rt-art-cauta" id="rt-l${i}-articol-cauta" data-i="${i}" placeholder="Caută articolul în stoc…" aria-label="Caută articolul" autocomplete="off" style="width:180px">
        <select class="camp-input rt-art" id="rt-l${i}-articol" data-i="${i}" aria-label="Articol ingredient"><option value=""${l.articol_id ? "" : " selected"}>— alege articolul —</option>${arts.map((a) =>
          `<option value="${a.id}" ${a.id == l.articol_id ? "selected" : ""}>${esc(a.denumire)}${a.cmp ? " · CMP " + pretUnitar(a.cmp) + " lei" : ""}</option>`).join("")}</select>
        <input class="camp-input rt-cant" id="rt-l${i}-cantitate" data-i="${i}" type="number" step="0.001" value="${l.cantitate || ""}" placeholder="cant./porție" aria-label="Cantitate pe porție" style="width:120px">
        <button type="button" class="buton-sters rt-scoate" data-i="${i}" title="Șterge">−</button>
      </div>`).join("");
    rtIng.querySelectorAll(".rt-art-cauta").forEach((c) => cautaInLista(c, rtIng.querySelector("#rt-l" + c.dataset.i + "-articol")));   // [488]
    rtIng.querySelectorAll(".rt-art").forEach((s) => s.addEventListener("change", (e) => { rtLinii[e.target.dataset.i].articol_id = e.target.value ? parseInt(e.target.value) : null; }));
    rtIng.querySelectorAll(".rt-cant").forEach((s) => s.addEventListener("input", (e) => { rtLinii[e.target.dataset.i].cantitate = parseFloat(e.target.value); }));
    rtIng.querySelectorAll(".rt-scoate").forEach((b) => b.addEventListener("click", (e) => { rtLinii.splice(e.target.dataset.i, 1); rtDeseneazaIng(); }));
  };
  const cerereRetete = ultimaCerere();   // [C103] rețetele reîncărcate după descărcări / ștergeri în șir: numai lista cerută ultima ajunge pe ecran
  const rtIncarca = async () => {
    const actuala = cerereRetete();
    let rr = [];
    try { const r = await api.get(`/tenants/${t.id}/retete`); if (!actuala()) return; rr = r.retete || []; } catch { if (!actuala()) return; rtLista.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca rețetele.</p>`; return; }
    rtLista.innerHTML = !rr.length ? `<div class="stare-goala">Nicio re\u021bet\u0103 \u00eenc\u0103.</div>`
      : rr.map((r) => {
          const fc = r.food_cost || {};
          const procent = fc.food_cost_pct == null ? "\u2013" : pct(fc.food_cost_pct);
          return `<div class="pf-frand">
            <div class="pf-frand-text">
              <div class="pf-frand-nume">${esc(r.denumire)} \u00b7 ${Number(r.pret_fara_tva) > 0 ? bani(r.pret_fara_tva) + " lei" : "fără preț"}</div>
              <div class="pf-frand-sub">cost/por\u021bie ${bani(fc.cost_portie)} \u00b7 food cost ${procent} \u00b7 ${(r.linii || []).map((l) => `${esc(l.denumire)} ${esc(cantitate(l.cantitate, l.um))}`).join(", ")}</div>
            </div>
            <input class="camp-input rt-portii" data-id="${r.id}" type="number" placeholder="por\u021bii" aria-label="Num\u0103r por\u021bii" style="width:80px">
            <button class="buton-primar rt-desc" data-actiune="POST /tenants/{tenant_id}/retete/descarca" data-id="${r.id}">Descarc\u0103 (ciorn\u0103)</button>
            <button class="buton-sters rt-del" data-actiune="DELETE /tenants/{tenant_id}/retete/{reteta_id}" data-id="${r.id}">\u0218terge</button>
          </div>`;
        }).join("");
    rtLista.querySelectorAll(".rt-desc").forEach((b) => b.addEventListener("click", async (e) => {
      const id = e.target.dataset.id;
      const p = rtLista.querySelector(`.rt-portii[data-id="${id}"]`).value;
      if (!p) { arataMesaj(zonaM, "Completeaz\u0103 num\u0103rul de por\u021bii.", "eroare"); return; }
      try {
        const r = await api.post(`/tenants/${t.id}/retete/descarca`, { reteta_id: parseInt(id), portii: parseFloat(p), data: val("#cv-data") || dataIso() });
        arataMesaj(zonaM, `Consum \u00eenregistrat (nota ${esc(r.nota_eticheta || "")}, ${stareNota(r)}) \u00b7 cost total ${bani(r.cost_total)} lei.`, "ok");
        sectiuneaCV(corp, t, zonaM, nav); rtIncarca();
      } catch (er) { arataMesaj(zonaM, er.mesaj || "Eroare la desc\u0103rcare.", "eroare"); }
    }));
    rtLista.querySelectorAll(".rt-del").forEach((b) => b.addEventListener("click", async (e) => {
      try { await api.del(`/tenants/${t.id}/retete/${e.target.dataset.id}`); rtIncarca(); } catch (er) { arataMesaj(zonaM, er.mesaj || "Nu s-a putut \u0219terge re\u021beta.", "eroare"); }
    }));
  };
  // [comanda Costin 06.10.2026 pct.1c, clasa] ingredientul nou NU vine legat de primul articol din listă (unul pe care nu l-a ales nimeni)
  zona.querySelector("#rt-plus").addEventListener("click", () => { rtLinii.push({ articol_id: null, cantitate: "" }); rtDeseneazaIng(); });
  zona.querySelector("#rt-salveaza").addEventListener("click", async () => {
    curataEroriCamp(zona);
    const den = zona.querySelector("#rt-den").value.trim();
    // NU se filtreaza randuri (cap.24 regula 2): lista trimisa = lista randata. Backendul valideaza per-linie si
    // raporteaza langa campul lipsa (rt-l{i}-..), nu se arunca tacit un ingredient inceput.
    const linii = rtLinii.map((l) => ({ articol_id: l.articol_id, cantitate: l.cantitate }));
    try {
      const pretRt = zona.querySelector("#rt-pret").value;   // [pct.1b, clasa] gol = „fără preț” (food cost „–”), nu 0 ales
      await api.post(`/tenants/${t.id}/retete`, { denumire: den, pret_fara_tva: pretRt === "" ? null : parseFloat(pretRt), linii });
      zona.querySelector("#rt-den").value = ""; zona.querySelector("#rt-pret").value = ""; rtLinii = []; rtDeseneazaIng(); rtIncarca();
    } catch (er) {
      curataEroriCamp(zona);
      const eris = (er && er.erori_campuri) || [];
      const rest = [];
      eris.forEach((x) => { if (!eroareCamp(zona, x.camp, x.mesaj)) rest.push(x.mesaj); });
      arataMesaj(zonaM, (rest.length ? rest.join("; ") : (er.mesaj || "Eroare la salvare.")), "eroare");
    }
  });
  rtIncarca();
  }

  // [lotul 13, deficiențele 673 și 612, comanda Costin 13.1] inventarul, transferul între locații, reclasificarea și inventarul pe mobil
  // se deschid fiecare în fereastra lor (DS cap.2a v2.104), nu într-o zonă a secțiunii; după reușită fereastra se închide, iar Stocuri se
  // redesenează cu confirmarea (`_revenireFereastra`, cheia „stocuri:<firmă>”). Fără navigator (garda din browser, `sectiuneaCV` singură)
  // butoanele nu au unde deschide și nu fac nimic.
  const cheieStoc = "stocuri:" + t.id;
  const fereastra = (titlu, randator) => { if (nav) deschideActiunea(nav, cheieStoc, {}, titlu, randator); };
  const optArts = `<option value="">— alege articolul —</option>` + (arts || []).map((a) => `<option value="${a.id}">${esc(a.denumire)} · stoc ${esc(cantitate(a.stoc, a.um))}</option>`).join("");
  zona.querySelector("#cv-inv").addEventListener("click", () => fereastra("Inventar — stoc faptic", (c2) => ecranInventarCV(c2, nav, t, arts, cheieStoc)));
  // [F138 Tier 1] Locatii descriptive + transfer (CMP global) + reclasificare tip produs
  // [comanda Costin 06.10.2026 pct.1c, clasa] transferul și reclasificarea porneau pe PRIMUL articol (fără opțiune goală): un articol pe
  // care nu l-a ales nimeni. Acum lista începe gol, iar butonul refuză până se alege.
  const locZona = zona.querySelector("#cv-loc-zona");
  zona.querySelector("#cv-loc-vezi").addEventListener("click", async () => {
    try {
      const r = await api.get(`/tenants/${t.id}/stocuri/locatii`);
      const l = r.locatii || [];
      locZona.innerHTML = !l.length ? `<div class="stare-goala">Nicio locație cu stoc încă.</div>`
        : `<div class="pf-frand-nume" style="margin:4px 0">Stoc pe locații (cantitativ; CMP rămâne global)</div>
           <div class="pf-lista">${l.map((x) => `
             <div class="pf-frand"><div class="pf-frand-text">
               <div class="pf-frand-nume">${esc(x.denumire)} · ${esc(x.locatie)}</div>
               <div class="pf-frand-sub">${esc(cantitate(x.cantitate, x.um))}</div>
             </div></div>`).join("")}</div>`;
    } catch (e) { arataMesaj(locZona, e.mesaj || "eroare", "eroare"); }
  });
  zona.querySelector("#cv-transfer-t").addEventListener("click", () => fereastra("Transfer între locații", (c2) => {
    c2.innerHTML = `
      <h2 class="pf-titlu">Transfer între locații</h2>
      <p class="pf-intro">Fără notă contabilă: costul (CMP) rămâne al firmei, se mută numai locul mărfii.</p>
      <div class="grila-campuri">
        <label class="camp"><span class="camp-eticheta">Articolul</span><select id="tr-art" aria-label="Articolul transferat" class="camp-input">${optArts}</select></label>
        <label class="camp"><span class="camp-eticheta">Din locația</span><input type="text" id="tr-din" class="camp-input" aria-label="Din locație" list="cv-loc-list"></label>
        <label class="camp"><span class="camp-eticheta">În locația</span><input type="text" id="tr-in" class="camp-input" aria-label="În locație" list="cv-loc-list"></label>
        <label class="camp"><span class="camp-eticheta">Cantitatea</span><input type="number" step="0.001" id="tr-cant" class="camp-input" aria-label="Cantitate"></label>
        <label class="camp"><span class="camp-eticheta">Data</span><input type="date" id="tr-data" aria-label="Data transferului" class="camp-input" value="${dataIso()}"></label>
      </div>
      <datalist id="cv-loc-list">${[...new Set((locInit || []).map((x) => x.locatie).filter((l) => l && l !== "(nespecificat)"))].map((l) => `<option value="${esc(l)}">`).join("")}</datalist>
      <div class="bara-fixa"><p style="margin-top:10px"><button class="buton-primar" id="tr-ok" data-actiune="POST /tenants/{tenant_id}/stocuri/transfer">Transferă</button>
        <button type="button" class="buton-secundar" data-renunta data-fara-actiune="închide fereastra, fără scriere" style="margin-left:6px">Renunță</button></p>
      <div id="tr-mesaj"></div></div>`;
    legaRenunta(c2, nav);
    c2.querySelector("#tr-ok").addEventListener("click", async () => {
      const g = (id) => c2.querySelector(id).value;
      const zm = c2.querySelector("#tr-mesaj");
      curataEroriCamp(c2);
      if (!g("#tr-art")) { eroareCamp(c2, "tr-art", "Alege articolul transferat."); return; }
      try {
        const r = await api.post(`/tenants/${t.id}/stocuri/transfer`, {
          articol_id: parseInt(g("#tr-art")), din_locatie: g("#tr-din") || null,
          in_locatie: g("#tr-in") || null, cantitate: parseFloat(g("#tr-cant")) || 0, data: g("#tr-data") });
        inchideCuConfirmarea(nav, cheieStoc, `Transfer ${cantitate(r.cantitate)} din „${esc(r.din_locatie)}” în „${esc(r.in_locatie)}” · ${bani(r.valoare)} lei la CMP ${pretUnitar(r.cmp)} lei.`);
      } catch (e) { arataRefuzul(c2, e, zm, { campuri: CAMPURI_CV }); }   // [lotul 11, 440] erorile serverului (`tr-…`) lângă câmpuri, o dată
    });
  }));
  zona.querySelector("#cv-recl-t").addEventListener("click", () => fereastra("Reclasificare tip produs", (c2) => {
    c2.innerHTML = `
      <h2 class="pf-titlu">Reclasificare tip produs</h2>
      <p class="pf-intro">Ex. materie primă 301 → marfă 371: o notă ciornă mută soldul articolului (cont nou = cont vechi) la CMP-ul de acum; cantitatea rămâne.</p>
      <div class="grila-campuri">
        <label class="camp"><span class="camp-eticheta">Articolul</span><select id="rc-art" aria-label="Articolul reclasificat" class="camp-input">${optArts}</select></label>
        <label class="camp"><span class="camp-eticheta">Contul de stoc nou</span><input type="text" id="rc-cont" class="camp-input" placeholder="ex. 371" aria-label="Cont stoc nou"></label>
        <label class="camp"><span class="camp-eticheta">Contul de cheltuială nou</span><input type="text" id="rc-chelt" class="camp-input" placeholder="ex. 607" aria-label="Cont cheltuială nou"></label>
        <label class="camp"><span class="camp-eticheta">Data</span><input type="date" id="rc-data" aria-label="Data reclasificării" class="camp-input" value="${dataIso()}"></label>
      </div>
      <div class="bara-fixa"><p style="margin-top:10px"><button class="buton-primar" id="rc-ok" data-actiune="POST /tenants/{tenant_id}/stocuri/reclasificare">Reclasifică</button>
        <button type="button" class="buton-secundar" data-renunta data-fara-actiune="închide fereastra, fără scriere" style="margin-left:6px">Renunță</button></p>
      <div id="rc-mesaj"></div></div>`;
    legaRenunta(c2, nav);
    c2.querySelector("#rc-ok").addEventListener("click", async () => {
      const g = (id) => c2.querySelector(id).value;
      const zm = c2.querySelector("#rc-mesaj");
      curataEroriCamp(c2);
      if (!g("#rc-art")) { eroareCamp(c2, "rc-art", "Alege articolul reclasificat."); return; }
      try {
        const r = await api.post(`/tenants/${t.id}/stocuri/reclasificare`, {
          articol_id: parseInt(g("#rc-art")), cont_stoc_nou: g("#rc-cont").trim(),
          cont_cheltuiala_nou: g("#rc-chelt").trim() || null, data: g("#rc-data") });
        inchideCuConfirmarea(nav, cheieStoc, r.nota
          ? `Reclasificat „${esc(r.denumire)}” din ${esc(r.cont_stoc_vechi)} în ${esc(r.cont_stoc)} · notă ${esc(r.nota)} ${bani(r.valoare_reclasificata)} lei (${stareNota(r)}).`
          : `Reclasificat „${esc(r.denumire)}” în ${esc(r.cont_stoc)} (fără sold de reclasificat).`);
      } catch (e) { arataRefuzul(c2, e, zm, { campuri: CAMPURI_CV }); }   // [lotul 11, 440]
    });
  }));
  // [F142] Inventar pe mobil: scanare cod (keyboard-wedge) -> acumulare in timp real -> finalizare.
  // Numarare oarba (nu afiseaza scripticul). Fara schema noua: foloseste motorul inventar() existent.
  zona.querySelector("#cv-inv-mobil").addEventListener("click", () => fereastra("Inventar pe mobil", (fm) => {
    const num = {};  // articol_id -> {denumire, um, faptic}
    const randList = () => Object.entries(num).map(([id, x]) =>
      `<div class="pf-frand"><div class="pf-frand-text">
         <div class="pf-frand-nume">${esc(x.denumire)}</div>
         <div class="pf-frand-sub">numărat ${esc(cantitate(x.faptic, x.um))}</div>
       </div><button class="buton-sters im-scoate" data-id="${id}" aria-label="Scoate ${esc(x.denumire)} din numărătoare">−</button></div>`).join("");
    const dataInv = dataIso();
    const deseneaza = () => {
      fm.innerHTML = `
        <h2 class="pf-titlu">Inventar pe mobil (numărare oarbă)</h2>
        <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center">
          <input type="text" id="im-scan" class="camp-input" placeholder="scanează codul sau caută denumirea" aria-label="Scanează cod sau caută" style="flex:1;min-width:180px">
          <input type="number" step="0.001" id="im-cant" class="camp-input" placeholder="cantitatea (1 dacă e gol)" aria-label="Cantitate numărată" style="width:190px">
          <button class="buton-primar" id="im-add" data-fara-actiune="numărătoarea se ține în memorie; finalizarea inventarului poartă acțiunea">Adaugă la numărătoare</button>
        </div>
        <div id="im-hint" class="camp-eticheta" style="margin-top:4px"></div>
        <div class="pf-lista" style="margin-top:8px">${randList() || '<div class="stare-goala">Nimic numărat încă.</div>'}</div>
        <div class="bara-fixa"><p style="margin-top:8px"><button class="buton-primar" id="im-fin" data-genereaza-nota="redesenat" data-actiune="POST /tenants/{tenant_id}/stocuri/inventar">Finalizează inventarul (note ciorne)</button>
          <button type="button" class="buton-secundar" data-renunta data-fara-actiune="închide fereastra, fără scriere" style="margin-left:6px">Renunță</button></p>
        <div id="im-mesaj"></div></div>`;
      legaRenunta(fm, nav);
      const scan = fm.querySelector("#im-scan");
      focusFaraSalt(scan);
      const adauga = async () => {
        const q = scan.value.trim();
        if (!q) return;
        const cant = parseFloat(fm.querySelector("#im-cant").value) || 1;
        let a = null;
        try { a = await api.get(`/tenants/${t.id}/stocuri/barcode/${encodeURIComponent(q)}`); } catch {}
        if (!a) {
          const m = arts.filter((x) => x.denumire.toLowerCase().includes(q.toLowerCase()));
          if (m.length === 1) a = m[0];
          else { fm.querySelector("#im-hint").textContent = m.length ? `${cate(m.length, "potrivire", "potriviri")} — precizează denumirea sau scanează codul.` : "Niciun articol găsit."; return; }
        }
        num[a.id] = num[a.id] || { denumire: a.denumire, um: a.um || "buc", faptic: 0 };
        num[a.id].faptic = Math.round((num[a.id].faptic + cant) * 1000) / 1000;
        deseneaza();
      };
      fm.querySelector("#im-add").addEventListener("click", adauga);
      scan.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); adauga(); } });
      fm.querySelectorAll(".im-scoate").forEach((b) => b.addEventListener("click", () => { delete num[b.dataset.id]; deseneaza(); }));
      fm.querySelector("#im-fin").addEventListener("click", async () => {
        const zm = fm.querySelector("#im-mesaj");
        const linii = Object.entries(num).map(([id, x]) => ({ articol_id: parseInt(id), faptic: x.faptic }));
        if (!linii.length) { arataMesaj(zm, "Nimic de inventariat: adaugă întâi articolele numărate.", "eroare"); return; }
        try {
          const r = await api.post(`/tenants/${t.id}/stocuri/inventar`, { data: dataInv, linii });
          // [lotul 11, 8c] refuzurile pe articol (ex. lipsa fără încadrare) nu se acoperă cu „finalizat”: se spun, rând cu rând, și
          // fereastra rămâne; altfel notele diferențelor, pe drumul unic al confirmării (conturile și sumele din jurnal)
          const rz = r.rezultate || [], erori = rz.filter((x) => x.eroare), ids = rz.map((x) => x.inregistrare_id).filter(Boolean);
          if (erori.length) { arataMesaj(zm, erori.map((x) => `${x.denumire || x.articol_id}: ${x.eroare}`).join("\n"), "eroare"); return; }
          const note = await noteGenerate(t.id, ids, dataInv);
          inchideCuConfirmarea(nav, cheieStoc, (zonaS) => dupaGenerare(zonaS, null, {
            titlu: `Inventar finalizat: ${cate(rz.length, "articol procesat", "articole procesate")} (notele diferențelor: ${stareNota(r, true)})`, note }));
        } catch (e) { arataRefuzul(fm, e, zm, { campuri: CAMPURI_CV }); }   // [lotul 11, 440]
      });
    };
    deseneaza();
  }));
  // [F140] Analitica de stoc: critic / inert / ABC / consum perioade comparabile
  zona.querySelector("#cv-ana").addEventListener("click", async () => {
    try {
      const r = await api.get(`/tenants/${t.id}/stocuri/analitica`);
      const lista = (titlu, randuri, gol) => `
        <div class="pf-frand-nume" style="margin:8px 0 4px">${titlu}</div>
        ${!randuri.length ? `<div class="stare-goala">${gol}</div>`
          : `<div class="pf-lista">${randuri.join("")}</div>`}`;
      const critic = (r.critic || []).map((x) => `
        <div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(x.denumire)}</div>
          <div class="pf-frand-sub">stoc ${esc(cantitate(x.stoc, x.um))} · nivel minim ${esc(cantitate(x.nivel_minim))} · necesar ${esc(cantitate(x.necesar, x.um))}</div>
        </div></div>`);
      const inert = (r.inert || []).map((x) => `
        <div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(x.denumire)}</div>
          <div class="pf-frand-sub">stoc ${esc(cantitate(x.stoc, x.um))} · ultima mișcare ${esc(x.ultima_miscare)} · ${cate(x.zile, "zi", "zile")}</div>
        </div></div>`);
      const abc = (r.abc || []).map((x) => `
        <div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(x.denumire)} · clasa ${esc(x.clasa)}</div>
          <div class="pf-frand-sub">valoare stoc ${bani(x.valoare)} lei · cumulat ${x.pondere_cumulata}%</div>
        </div></div>`);
      const consum = (r.consum || []).map((x) => `
        <div class="pf-frand"><div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(x.denumire)}</div>
          <div class="pf-frand-sub">ieșiri ultimele 30 zile ${x.iesiri_30z} ${esc(x.um)} · 30 zile anterioare ${x.iesiri_30z_anterior} ${esc(x.um)}</div>
        </div></div>`);
      locZona.innerHTML = `
        <div class="pf-card">
          ${lista(`Stoc critic (sub nivel minim)`, critic, "Niciun articol sub nivel minim (sau niciun nivel minim setat).")}
          ${lista(`Fără mișcare de peste ${cate(r.zile_inert, "zi", "zile")}`, inert, "Niciun articol inert.")}
          ${lista(`Clasificare ABC (Pareto pe valoarea stocului)`, abc, "Niciun stoc de clasificat.")}
          ${lista(`Consum — perioade comparabile`, consum, "Nicio ieșire în ultimele 60 de zile.")}
        </div>`;
    } catch (e) { arataMesaj(locZona, e.mesaj || "eroare", "eroare"); }
  });
  zona.querySelector("#cv-fisa").addEventListener("click", async () => {
    if (!val("#cv-art")) return;
    try {
      const r = await api.get(`/tenants/${t.id}/stocuri/articole/${val("#cv-art")}/fisa`);
      zona.querySelector("#cv-fisa-zona").innerHTML = `
        <div class="pf-frand-nume" style="margin:8px 0">Fișa: ${esc(r.articol.denumire)}</div>
        <div class="pf-lista">${r.linii.map((l) => `
          <div class="pf-frand"><div class="pf-frand-text">
            <div class="pf-frand-nume">${dataRo(l.data)} \u00b7 ${l.tip === "ajustare" ? `diferen\u021b\u0103 de pre\u021b ${bani(l.valoare)} lei` : miscareFisa(l)}${l.pret_unitar ? " \u00b7 pre\u021b " + pretUnitar(l.pret_unitar) + " lei" : ""}</div>
            <div class="pf-frand-sub">sold ${cantitate(l.sold_cantitate)} \u00b7 ${bani(l.sold_valoare)} lei${l.cmp ? " \u00b7 CMP " + pretUnitar(l.cmp) + " lei" : ""}${l.document ? " \u00b7 " + esc(l.document) : ""}</div>
          </div></div>`).join("") || '<div class="stare-goala">Fără mișcări în fișă.</div>'}</div>`;
    } catch { arataMesaj(zona.querySelector("#cv-fisa-zona"), "Nu s-a putut încărca fișa.", "eroare"); }
  });
}

// [lotul 10, deficiența 419, comanda Costin 10.2 pct.7f, verbatim] „în fișa de magazie, rândul de retur din stornare apare «−-1 · -27,50
// lei»”. Stornarea în roșu (OMFP 1802/2014 pct.69: „corectarea cu semnul minus a operațiunii inițiale”) vine cu cantitatea și valoarea
// negative (`storno` de la server), iar semnul rândului se punea și el în față. Rândul spune ce s-a întâmplat cu stocul, cu UN semn:
// returul (ieșirea stornată) +1 · 27,50 lei, intrarea stornată −5 · 100,00 lei, numite ca atare.
function miscareFisa(l) {
  const cant = Math.abs(Number(l.cantitate)), val = Math.abs(Number(l.valoare));
  const creste = (l.tip === "intrare") !== Boolean(l.storno);
  const fel = l.storno ? (l.tip === "iesire" ? "retur în stoc (ieșirea stornată în roșu) " : "intrare stornată în roșu ") : "";
  return `${fel}${creste ? "+" : "−"}${cantitate(cant)} · ${bani(val)} lei`;
}

// [stocuri] NIR + descarcare gestiune (global-valorica)

// [lista 3, 30.08.2026] CARTEA MARE (14-1-3), prin inlocuitorul ei legal: Fisa de cont 14-6-22
// (OMFP 2634/2015, Anexa 2). Producatorul exista din iulie si producea pe date reale — 6 firme, 43
// de conturi — dar n-avea nici ruta, nici ecran, deci artefactul nu ajungea la nimeni.
//
// Ecranul NU calculeaza nimic: soldul curent dupa fiecare operatiune, totalurile si sensul soldului
// vin de la server. Iar `temei_completitudine` — DE CE credem ca s-a vazut tot — se ARATA, fiindca
// exact el face fisa aparabila la un control: fara el, o fisa care omite o nota arata identic cu una
// completa.
async function ecranFisaCont(corp, nav, t) {
  const azi = new Date();
  let an = azi.getFullYear(), luna = 0, cont = "";
  const cerereNoua = ultimaCerere();   // [C103] anul, perioada și contul alese în șir: numai fișa contului din filtre ajunge pe ecran

  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    const actuala = cerereNoua();
    let d = null;
    try {
      const q = `an=${an}${luna ? `&luna=${luna}` : ""}${cont ? `&cont=${encodeURIComponent(cont)}` : ""}`;
      d = await api.get(`/tenants/${t.id}/fisa-cont?${q}`);
      if (!actuala()) return;
    } catch (e) {
      if (!actuala()) return;
      corp.innerHTML = `<p class="ecran-nota">Nu s-a putut \u00eenc\u0103rca fi\u0219a de cont. ${esc((e && (e.mesaj || e.message)) || "")}</p>`;
      return;
    }
    const conturi = (d && d.conturi) || [];
    const f = d && d.fisa;
    const optCont = `<option value="">\u2014 alege contul \u2014</option>` +
      conturi.map((c) => `<option value="${esc(c)}"${c === cont ? " selected" : ""}>${esc(c)}</option>`).join("");
    const optLuna = `<option value="0"${luna === 0 ? " selected" : ""}>tot anul</option>` +
      Array.from({ length: 12 }, (_, i) => `<option value="${i + 1}"${luna === i + 1 ? " selected" : ""}>${dataRo(`${an}-${String(i + 1).padStart(2, "0")}-01`, "luna_an_numeric")}</option>`).join("");

    let corpFisa;
    if (!conturi.length) {
      corpFisa = `<div class="stare-goala">Niciun cont cu mi\u0219care \u00een perioada asta, deci fi\u0219a n-are ce ar\u0103ta. Fi\u0219a se face din notele validate — o ciorn\u0103 nu e eviden\u021b\u0103. Treci pe alt\u0103 perioad\u0103, sau valideaz\u0103 notele lunii din Registrul jurnal.</div>`;
    } else if (!f) {
      corpFisa = `<div class="stare-goala stare-goala--inline">Alege un cont din list\u0103 — sunt ${conturi.length} cu mi\u0219care \u00een perioada asta.</div>`;
    } else {
      corpFisa = `
        <table class="fd-tabel">
          <thead><tr><th>Data</th><th>Document</th><th>Explica\u021bie</th><th>Cont coresp.</th>
            <th class="fd-td-num">Debit</th><th class="fd-td-num">Credit</th>
            <th class="fd-td-num">Sold</th><th>Jurnal</th></tr></thead>
          <tbody>${f.randuri.map((r) => `<tr>
              <td>${dataRo(r.data)}</td><td>${esc(r.document || "")}</td>
              <td>${esc(r.explicatie || "")}</td><td>${esc(r.cont_corespondent)}</td>
              <td class="fd-td-num">${r.debit ? bani(r.debit) : ""}</td>
              <td class="fd-td-num">${r.credit ? bani(r.credit) : ""}</td>
              <td class="fd-td-num">${bani(r.sold)}${r.sens_sold === "0" ? "" : " " + r.sens_sold}</td>
              <td>${esc(r.jurnal || "")}</td></tr>`).join("")}</tbody>
        </table>
        <details class="dec-xml" style="margin-top:12px">
          <summary>Ce acoper\u0103 fi\u0219a asta \u2014 temeiul de completitudine</summary>
          <p class="ecran-nota">${esc(f.temei_completitudine || "")}</p>
        </details>
        <div class="bara-fixa"><div class="fd-totaluri">   <!-- [lotul 11, decizia Costin 10.3: \u201eTotalurile \u2026 fix\u201d] totalurile fi\u0219ei r\u0103m\u00e2n jos, \u00een vedere, c\u00e2t derulezi tabelul (DS cap.9 v2.100) -->
          <div class="fd-tot-rand"><span>Sold ini\u021bial</span><span>${f.sold_initial_declarat ? bani(f.sold_initial) + " lei" : "nedeclarat \u2014 fi\u0219a porne\u0219te de la 0"}</span></div>
          <div class="fd-tot-rand"><span>Total debit</span><span>${bani(f.total_debit)} lei</span></div>
          <div class="fd-tot-rand"><span>Total credit</span><span>${bani(f.total_credit)} lei</span></div>
          <div class="fd-tot-rand fd-tot-final"><span>Sold final</span><span>${bani(f.sold_final)} lei${f.sens_sold_final === "0" ? "" : " " + f.sens_sold_final}</span></div>
        </div></div>`;
    }

    corp.innerHTML = `
      <h2 class="pf-titlu">Cartea mare</h2>
      <p class="pf-intro">Fi\u0219\u0103 de cont pentru opera\u021biuni diverse, cod <b>${esc((d && d.formular) || "")}</b> \u2014 \u00eenlocuitorul legal al Registrului Cartea mare (OMFP 2634/2015, Anexa 2, cod 14-1-3).</p>
      <div class="rezumat-fix" style="display:flex;gap:8px;align-items:flex-end;flex-wrap:wrap;margin-bottom:10px">   <!-- [lotul 10, 421 / 424, DS cap.9 v2.97 pct.5] anul, perioada și contul rămân sus -->
        <label class="camp"><span class="camp-eticheta">An</span><input type="number" id="fc-an" class="camp-input" value="${an}" style="width:90px"></label>
        <label class="camp"><span class="camp-eticheta">Perioada</span><select id="fc-luna" class="camp-input">${optLuna}</select></label>
        <label class="camp"><span class="camp-eticheta">Cont</span><select id="fc-cont" class="camp-input" style="min-width:160px">${optCont}</select></label>
      </div>
      ${corpFisa}`;
    corp.querySelector("#fc-an").addEventListener("change", (e) => { an = parseInt(e.target.value) || an; cont = ""; deseneaza(); });
    corp.querySelector("#fc-luna").addEventListener("change", (e) => { luna = parseInt(e.target.value) || 0; cont = ""; deseneaza(); });
    corp.querySelector("#fc-cont").addEventListener("change", (e) => { cont = e.target.value; deseneaza(); });
  };
  deseneaza();
}


// [lista 3, 30.08.2026] JURNALUL SPECIAL DE REGIM MARJA (normele CF, pct. 86). Ruta exista din
// campania de API intern, cu comentariul „fara UI inca, pastrat deliberat" — deci artefactul se
// producea si nu ajungea la om. Ecranul nu aduna nimic: totalurile perioadei vin de la server.
async function ecranJurnalMarja(corp, nav, t) {
  const azi = new Date();
  let tip = "secondhand";
  let luna = `${azi.getFullYear()}-${String(azi.getMonth() + 1).padStart(2, "0")}`;
  const cerereNoua = ultimaCerere();   // [C103] tipul și luna alese în șir: numai jurnalul din filtre ajunge pe ecran

  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    const actuala = cerereNoua();
    let d = null;
    try {
      d = await api.get(`/tenants/${t.id}/jurnal-marja?tip=${tip}&luna=${luna}`);
      if (!actuala()) return;
    } catch (e) {
      if (!actuala()) return;
      corp.innerHTML = `<p class="ecran-nota">Nu s-a putut \u00eenc\u0103rca jurnalul. ${esc((e && (e.mesaj || e.message)) || "")}</p>`;
      return;
    }
    const note = (d && d.note) || [];
    const tabel = !note.length
      ? `<div class="stare-goala">Nicio v\u00e2nzare \u00een regim marj\u0103 \u00een luna asta. Jurnalul se umple din notele emise cu <b>V\u00e2nzare regim marj\u0103</b> — dac\u0103 firma a avut astfel de v\u00e2nz\u0103ri, \u00eenregistreaz\u0103-le de pe ecranul de opera\u021biuni.</div>`
      : `<table class="fd-tabel">
          <thead><tr><th>Data</th><th>Nota</th><th>Explica\u021bie</th><th>Client</th><th>Stare</th>
            <th class="fd-td-num">Pre\u021b v\u00e2nzare</th><th class="fd-td-num">Pre\u021b cump\u0103rare</th><th class="fd-td-num">Marj\u0103 net\u0103</th>
            <th class="fd-td-num">TVA colectat\u0103</th></tr></thead>
          <tbody>${note.map((n) => `<tr>
              <td>${dataRo(n.data)}</td><td>${esc(n.eticheta || "")}</td>
              <td>${esc(n.descriere || "")}</td><td>${esc(n.client || "\u2014")}</td><td>${esc(n.status || "")}</td>
              <td class="fd-td-num">${bani(n.pret_vanzare)}</td>
              <td class="fd-td-num" title="${n.cost == null ? "v\u00e2nzare dinaintea lotului 13: pre\u021bul de cump\u0103rare nu e \u00een eviden\u021b\u0103" : ""}">${n.cost == null ? "\u2014" : bani(n.cost)}</td>
              <td class="fd-td-num">${n.marja_neta == null ? "\u2014" : bani(n.marja_neta)}</td>
              <td class="fd-td-num">${bani(n.tva)}</td></tr>`).join("")}</tbody>
        </table>
        <div class="bara-fixa"><div class="fd-totaluri">   <!-- [lotul 11, decizia Costin 10.3: \u201eTotalurile \u2026 fix\u201d] totalurile lunii r\u0103m\u00e2n jos, \u00een vedere (DS cap.9 v2.100) -->
          <div class="fd-tot-rand"><span>Note \u00een lun\u0103</span><span>${d.numar_note}</span></div>
          <div class="fd-tot-rand"><span>Total v\u00e2nz\u0103ri</span><span>${bani(d.total_vanzari)} lei</span></div>
          <div class="fd-tot-rand"><span>Total pre\u021b de cump\u0103rare</span><span>${bani(d.total_cost)} lei</span></div>
          <div class="fd-tot-rand"><span>Total baz\u0103 (marj\u0103 net\u0103)</span><span>${bani(d.total_baza_marja_neta)} lei</span></div>
          <div class="fd-tot-rand fd-tot-final"><span>Total TVA colectat\u0103</span><span>${bani(d.total_tva_colectata)} lei</span></div>
        </div></div>`;
    corp.innerHTML = `
      <h2 class="pf-titlu">Jurnal regim marj\u0103</h2>
      <p class="pf-intro">Jurnalul special cerut de normele Codului fiscal, pct. 86, pentru v\u00e2nz\u0103rile \u00een regim de marj\u0103.</p>
      <div class="rezumat-fix" style="display:flex;gap:8px;align-items:flex-end;flex-wrap:wrap;margin-bottom:10px">   <!-- [lotul 10, 421 / 424, DS cap.9 v2.97 pct.5] regimul și luna rămân sus -->
        <label class="camp"><span class="camp-eticheta">Regim</span><select id="jm-tip" class="camp-input" data-butoane>
          <option value="secondhand"${tip === "secondhand" ? " selected" : ""}>Bunuri second-hand \u00b7 art. 312</option>
          <option value="turism"${tip === "turism" ? " selected" : ""}>Agen\u021bii de turism \u00b7 art. 311</option>
        </select></label>
        <label class="camp"><span class="camp-eticheta">Luna</span><input type="month" id="jm-luna" class="camp-input" value="${luna}"></label>
      </div>
      ${tabel}`;
    corp.querySelector("#jm-tip").addEventListener("change", (e) => { tip = e.target.value; deseneaza(); });
    corp.querySelector("#jm-luna").addEventListener("change", (e) => { luna = e.target.value || luna; deseneaza(); });
  };
  deseneaza();
}


// [lista 3, 30.08.2026] REGISTRUL DE EVIDENTA FISCALA. Sunt DOUA, nu unul — chiar greseala de la
// care a pornit constructia: „nu se poate face" a fost scris dupa ce se citise doar articolul.
//
// PROFIT (art. 19 alin. (7) + HG 1/2016 pct. 8): se DERIVA, din aceleasi campuri din care iese D101.
// Nu se completeaza de mana, si nu se poate: un al doilea calcul al aceluiasi an ar putea sa nu
// coincida cu declaratia pe care registrul exista tocmai ca s-o justifice.
//
// PERSOANE FIZICE (art. 68 + OMFP 3254/2017): se COMPLETEAZA, pe fiecare sursa din fiecare
// categorie. Cheltuielile se inscriu doar cand venitul net se stabileste in sistem real — la norma
// de venit norma spune expres ca nu, iar ecranul ascunde campul in loc sa-l lase sa induca in eroare.
async function ecranRegistruFiscal(corp, nav, t) {
  const azi = new Date();
  let an = azi.getFullYear() - 1;
  // [lotul 13, 577] varianta registrului după forma firmei: PFA / II / IF (partidă simplă) — persoane fizice, art.68; societatea — profit, art.19
  let varianta = t.regim_contabil === "simpla" ? "venituri_pf" : "profit";
  const cerereNoua = ultimaCerere();   // [C103] varianta și anul alese în șir: numai registrul din filtre ajunge pe ecran

  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103...</p>`;
    const actuala = cerereNoua();
    let d = null, eroare = null;
    try {
      d = await api.get(`/tenants/${t.id}/registru-evidenta-fiscala?an=${an}&varianta=${varianta}`);
      if (!actuala()) return;
    } catch (e) { if (!actuala()) return; eroare = e; }

    const selector = `
      <div class="rezumat-fix" style="display:flex;gap:8px;align-items:flex-end;flex-wrap:wrap;margin-bottom:10px">   <!-- [lotul 10, 421 / 424, DS cap.9 v2.97 pct.5] varianta și anul rămân sus -->
        <label class="camp"><span class="camp-eticheta">Varianta</span><select id="rf-var" class="camp-input" data-butoane>
          <option value="profit"${varianta === "profit" ? " selected" : ""}>Impozit pe profit \u00b7 art. 19 alin. (7)</option>
          <option value="venituri_pf"${varianta === "venituri_pf" ? " selected" : ""}>Persoane fizice \u00b7 art. 68 alin. (8)-(9)</option>
        </select></label>
        <label class="camp"><span class="camp-eticheta">Anul</span><input type="number" id="rf-an" class="camp-input" value="${an}" style="max-width:120px"></label>
      </div>`;

    if (eroare) {
      corp.innerHTML = `<h2 class="pf-titlu">Registrul de eviden\u021b\u0103 fiscal\u0103</h2>${selector}
        <div class="dec-avert" role="alert"><div class="dec-avert-cap">Nu s-a putut \u00eentocmi registrul pe ${esc(String(an))}.</div>
        <p>${esc((eroare && (eroare.mesaj || eroare.message)) || "")}</p></div>${varianta === "profit" ? '<div id="rf-ajustari"></div>' : ""}`;
      legaSelector();
      if (varianta === "profit") ajustari(corp.querySelector("#rf-ajustari"));
      return;
    }

    let corpHtml = "";
    if (varianta === "profit") {
      const s = (d.corp && d.corp.sectiuni) || [];
      corpHtml = `<div><table class="fd-tabel">
        <thead><tr><th>Categoria cerut\u0103 de norm\u0103</th><th>Temei</th><th>R\u00e2nduri D101</th><th class="fd-td-num">Total</th></tr></thead>
        <tbody>${s.map((x) => `<tr>
          <td>${esc(x.eticheta)}</td><td><small>${esc(x.temei)}</small></td>
          <td><small>${x.randuri.map((r) => `${esc(r.camp)} ${bani(r.valoare)}`).join(" \u00b7 ")}</small></td>
          <td class="fd-td-num">${bani(x.total)} lei</td></tr>`).join("")}</tbody></table></div>
        <p class="pf-intro" style="margin-top:10px">Cifrele sunt <b>cele din D101</b> pe acela\u0219i an, nu un al doilea calcul. Registrul exist\u0103 ca s\u0103 justifice declara\u021bia, deci nu are voie s-o contrazic\u0103.</p>
        <div id="rf-ajustari"></div>`;
    } else {
      const s = d.sectiuni || [];
      corpHtml = !s.length
        ? `<div class="stare-goala"><b>Niciun r\u00e2nd \u00eenscris.</b> Registrul se \u021bine pe fiecare surs\u0103 din fiecare categorie de venit. Pe persoan\u0103 fizic\u0103 nu exist\u0103 contabilitate din care s\u0103 ias\u0103 cifrele \u2014 de aceea se \u00eenscriu aici.</div>`
        : s.map((x) => `<h3 style="margin-top:18px">${esc(x.categorie_eticheta || ("categorie " + x.categorie))} \u2014 ${esc(x.sursa)}</h3>
            <div><table class="fd-tabel">
              <thead><tr><th>Nr. crt.</th><th class="fd-td-num">Venit brut</th><th class="fd-td-num">Cheltuieli deductibile</th><th class="fd-td-num">Venit net</th><th>Rectificare</th></tr></thead>
              <tbody>${x.randuri.map((r) => `<tr><td>${esc(String(r.nr_crt))}</td>
                <td class="fd-td-num">${bani(r.venit_brut)} lei</td>
                <td class="fd-td-num">${bani(r.cheltuieli_deductibile)} lei</td>
                <td class="fd-td-num">${bani(r.venit_net)} lei</td>
                <td>${r.rectificare ? esc(r.motiv_rectificare || "da") : "\u2014"}</td></tr>`).join("")}</tbody>
              <tfoot><tr><td>Total anual</td>   <!-- [lotul 11, decizia Costin 10.3: \u201eTotalurile \u2026 fix\u201d] r\u00e2ndul de total al sursei r\u0103m\u00e2ne jos, \u00een vedere, sub coloanele lui (DS cap.9 v2.100) -->
                <td class="fd-td-num">${bani(x.total_venit_brut)} lei</td>
                <td class="fd-td-num">${bani(x.total_cheltuieli)} lei</td>
                <td class="fd-td-num">${x.venit_net < 0 ? "Pierdere net\u0103 anual\u0103: " : "Venit net anual: "}${bani(Math.abs(x.venit_net))} lei</td><td></td></tr></tfoot>
            </table></div>`).join("");
      corpHtml += formularPf(d);
    }

    corp.innerHTML = `
      <h2 class="pf-titlu">Registrul de eviden\u021b\u0103 fiscal\u0103</h2>
      <p class="pf-intro">Sunt <b>dou\u0103</b> registre distincte, pentru doi contribuabili diferi\u021bi.<br><small>${esc(d.temei || "")}</small></p>
      ${selector}
      <p class="pf-intro">${esc(d.temei_completitudine || "")}</p>
      ${d.model_elidat ? (() => { const c = d.model_elidat; return `<p class="pf-intro"><small><b>Ce nu s-a putut cita:</b> din <b>${esc(c.act)}</b>, ${esc(c.unde)} — ${esc(c.ce_lipseste)} (${esc(c.cum_apare)}), căutată în ${esc(cate((c.fisiere_verificate || []).length, "fișier", "fișiere"))}, ${esc(cate(c.aparitii_in_fisier, "apariție", "apariții"))}. Conținutul de mai jos vine din ${esc(c.de_unde_vine_continutul)}.</small></p>`; })() : ""}
      ${corpHtml}`;
    legaSelector();
    if (varianta === "venituri_pf") legaFormular(d);
    if (varianta === "profit") ajustari(corp.querySelector("#rf-ajustari"));
  };

  // [deficiența 378, comanda Costin 8.2, 18.10.2026] AJUSTĂRILE FISCALE ale rezultatului (cheltuieli nedeductibile, venituri
  // neimpozabile, deduceri, pierderea din anii anteriori), scrise de contabil pe trimestrul lor și pe rândul D101: aceeași sursă pentru
  // D100 trimestrial (rezultatul fiscal cumulat de la 01.01) și pentru D101. Până azi nu aveau niciun ecran.
  const cerereAjustari = ultimaCerere();   // [C103] ajustările reîncărcate la anul schimbat în șir: numai lista anului cerut ultimul ajunge pe ecran
  const ajustari = async (zona) => {
    if (!zona) return;
    const actuala = cerereAjustari();
    let d;
    try { d = await api.get(`/tenants/${t.id}/ajustari-fiscale?an=${an}`); if (!actuala()) return; } catch (e) {
      if (!actuala()) return;
      zona.innerHTML = `<p class="ecran-nota">Ajust\u0103rile fiscale nu s-au putut \u00eenc\u0103rca: ${esc((e && e.mesaj) || "eroare")}.</p>`; return;
    }
    const grupe = { nedeductibile: "Cheltuieli nedeductibile", neimpozabile: "Venituri neimpozabile", deduceri: "Deduceri",
                    similare: "Elemente similare", pierdere: "Pierderea din anii anteriori" };
    const optiuni = Object.keys(grupe).map((g) => `<optgroup label="${esc(grupe[g])}">${d.randuri.filter((r) => r.grupa === g)
      .map((r) => `<option value="${esc(r.rand)}">${esc(r.eticheta)}</option>`).join("")}</optgroup>`).join("");
    const lista = !d.ajustari.length
      ? `<div class="stare-goala">Nicio ajustare fiscal\u0103 pe ${esc(String(an))}. Impozitul pe profit (D100 trimestrial \u0219i D101) se calculeaz\u0103 atunci pe rezultatul contabil plus rezerva legal\u0103.</div>`
      : `<div><table class="fd-tabel"><thead><tr><th>Trimestrul</th><th>R\u00e2ndul D101</th><th class="fd-td-num">Suma</th><th>Descriere</th><th>Document</th><th>Acțiune</th></tr></thead>
        <tbody>${d.ajustari.map((a) => `<tr><td>${a.trim ? `T${a.trim}/${esc(String(a.an))}` : `anul ${esc(String(a.an))}`}</td><td>${esc(a.eticheta)}</td><td class="fd-td-num">${bani(a.suma)} lei</td>
          <td>${esc(a.descriere || "\u2014")}</td><td>${esc(a.document || "\u2014")}</td>
          <td><button class="buton-secundar" data-aj-sterge="${a.id}" data-actiune="DELETE /tenants/{tenant_id}/ajustari-fiscale/{ajustare_id}">\u0218terge</button></td></tr>`).join("")}</tbody></table></div>`;
    // [378, lotul 9] rândurile luate din conturi cât timp omul nu le scrie (amenzile din 6581 -> rd.25)
    const dinConturi = (d.din_conturi || []).length ? `<div class="caseta-info" id="aj-din-conturi" style="margin-top:10px"><b>Din conturi, f\u0103r\u0103 s\u0103 le scrii:</b><ul>${d.din_conturi.map((r) =>
      `<li>${esc(r.eticheta)}: ${bani(r.suma)} lei, din ${esc(r.sursa)}${r.inlocuit ? " \u2014 <b>\u00eenlocuit de r\u00e2ndul scris de tine</b>" : ""}</li>`).join("")}</ul>
      Dac\u0103 o parte e deductibil\u0103 (o desp\u0103gubire sau o penalitate contractual\u0103), scrie r\u00e2ndul cu suma nedeductibil\u0103: cifra ta \u00eenlocuie\u0219te contul pe tot anul.</div>` : "";
    pastreazaCampulActiv(zona, () => {   // [C103] rândul / trimestrul ales cât se reîncarcă lista nu se pierd
      zona.innerHTML = `<h3 style="margin-top:22px">Ajust\u0103ri fiscale pe ${esc(String(an))}</h3>
        <p class="pf-intro">Ce face diferen\u021ba dintre profitul contabil \u0219i cel impozabil (CF art.19 alin.(1)), pe trimestrul \u00een care s-a produs. Intr\u0103 cumulat \u00een D100 pe trimestrele I\u2013III \u0219i \u00een D101. Pierderea din anii anteriori se scrie o dat\u0103 pe an \u0219i se recupereaz\u0103 cel mult 70% din profit (CF art.31).</p>
        ${dinConturi}${lista}
        <div style="display:flex;gap:10px;flex-wrap:wrap;max-width:960px;margin-top:10px">
          <label class="camp"><span class="camp-eticheta">R\u00e2ndul D101</span><select id="aj-rand" class="camp-input">${ALEGE}${optiuni}</select></label>
          <label class="camp" id="aj-trim-camp"><span class="camp-eticheta">Trimestrul</span><select id="aj-trim" class="camp-input">${ALEGE}
            ${[1, 2, 3, 4].map((q) => `<option value="${q}">T${q}/${esc(String(an))}</option>`).join("")}</select></label>
          <label class="camp"><span class="camp-eticheta">Suma (lei)</span><input type="number" step="0.01" min="0.01" id="aj-suma" class="camp-input"></label>
          <label class="camp"><span class="camp-eticheta">Descriere</span><input type="text" id="aj-descriere" class="camp-input"></label>
          <label class="camp"><span class="camp-eticheta">Document</span><input type="text" id="aj-document" class="camp-input"></label>
        </div>
        <div class="bara-fixa" style="margin-top:12px"><button class="buton-primar" id="aj-adauga" data-actiune="POST /tenants/{tenant_id}/ajustari-fiscale">Adaug\u0103 ajustarea</button><div id="aj-mesaj"></div></div>`; });   // [lotul 11, \u201emesajele l\u00e2ng\u0103 buton\u201d \u2014 DS cap.9 v2.100] zona de mesaj l\u00e2ng\u0103 \u201eAdaug\u0103 ajustarea\u201d, nu sub tabel
    const sel = zona.querySelector("#aj-rand");
    const potriveste = () => { zona.querySelector("#aj-trim-camp").style.display = (d.anuale || []).includes(sel.value) ? "none" : ""; };
    sel.addEventListener("change", potriveste);
    potriveste();
    zona.querySelector("#aj-adauga").addEventListener("click", async () => {
      const m = zona.querySelector("#aj-mesaj");
      m.innerHTML = "";
      curataEroriCamp(zona);
      const anuala = (d.anuale || []).includes(sel.value);
      if (cereAlegerile(zona, anuala ? ["#aj-rand"] : ["#aj-rand", "#aj-trim"])) return;
      try {
        await api.post(`/tenants/${t.id}/ajustari-fiscale`, { an, rand: sel.value, trim: anuala ? null : Number(zona.querySelector("#aj-trim").value),
          suma: zona.querySelector("#aj-suma").value, descriere: zona.querySelector("#aj-descriere").value, document: zona.querySelector("#aj-document").value });
        deseneaza();
      } catch (e) { arataMesaj(m, (e && e.mesaj) || "Ajustarea nu s-a scris.", "eroare"); }
    });
    // [lotul 12, defect găsit de form2] „Șterge” nu făcea nimic: `confirmaCaseta` nu întoarce o promisiune și primea textul în locul
    // zonei (`zona.parentNode` -> TypeError). Forma cu funcția de confirmare, ca în restul fișierului
    zona.querySelectorAll("[data-aj-sterge]").forEach((b) => b.addEventListener("click", () => {
      confirmaCaseta(b.parentElement || b, "\u0218tergi ajustarea? D100 \u0219i D101 se calculeaz\u0103 din nou f\u0103r\u0103 ea.", async () => {
        try { await api.del(`/tenants/${t.id}/ajustari-fiscale/${b.dataset.ajSterge}`); deseneaza(); }
        catch (e) { arataMesaj(zona.querySelector("#aj-mesaj"), (e && e.mesaj) || "Ajustarea nu s-a \u0219ters.", "eroare"); }
      }, { textOk: "Da, \u0219terge ajustarea", textNu: "P\u0103streaz\u0103" });
    }));
  };

  const formularPf = (d) => `
      <h3 style="margin-top:22px">\u00censcrie un r\u00e2nd</h3>
      <div id="rf-eroare"></div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;max-width:960px">
        <label class="camp"><span class="camp-eticheta">Categoria de venit</span><select id="rf-categorie" class="camp-input">${ALEGE}
          ${Object.keys(d.categorii || {}).map((k) => `<option value="${esc(k)}">${esc(d.categorii[k])}</option>`).join("")}
        </select></label>
        <label class="camp"><span class="camp-eticheta">Sursa de venit</span><input type="text" id="rf-sursa_venit" class="camp-input"></label>
        <label class="camp"><span class="camp-eticheta">Venitul net se stabile\u0219te</span><select id="rf-mod_venit_net" class="camp-input">${ALEGE}
          ${Object.keys(d.moduri_venit_net || {}).map((k) => `<option value="${esc(k)}">${esc(d.moduri_venit_net[k])}</option>`).join("")}
        </select></label>
        <label class="camp"><span class="camp-eticheta">Venit brut</span><input type="number" step="0.01" id="rf-venit_brut" class="camp-input"></label>
        <label class="camp" id="rf-ch-camp"><span class="camp-eticheta">Cheltuieli deductibile</span><input type="number" step="0.01" id="rf-cheltuieli_deductibile" class="camp-input"></label>
      </div>
      <p class="pf-intro" id="rf-nota-ch"></p>
      <div class="bara-fixa" style="margin-top:12px"><button class="buton-primar" id="rf-adauga" data-actiune="POST /tenants/{tenant_id}/registru-evidenta-fiscala">\u00censcrie \u00een registru</button></div>`;

  const legaSelector = () => {
    const v = corp.querySelector("#rf-var"), a = corp.querySelector("#rf-an");
    if (v) v.addEventListener("change", (e) => { varianta = e.target.value; deseneaza(); });
    if (a) a.addEventListener("change", (e) => { an = Number(e.target.value) || an; deseneaza(); });
  };

  const legaFormular = () => {
    const mod = corp.querySelector("#rf-mod_venit_net");
    const cat = corp.querySelector("#rf-categorie");
    if (!mod) return;
    // Regula din art. 1: la NORMA DE VENIT nu se inscriu cheltuieli. Campul se ASCUNDE, nu se lasa
    // gol si refuzat dupa apasare — un camp care se poate completa si apoi e respins invata omul ca
    // aplicatia e capricioasa, cand de fapt norma e clara.
    const potriveste = () => {
      const norma = mod.value === "3";
      const pi = cat.value === "3";
      corp.querySelector("#rf-ch-camp").style.display = norma ? "none" : "";
      corp.querySelector("#rf-nota-ch").innerHTML = norma
        ? "La <b>norma de venit</b> nu se \u00eenscriu cheltuieli \u00een registru (art. 1 alin. (2))."
        : (pi ? "La drepturi de proprietate intelectual\u0103, cheltuielile sunt <b>op\u021bionale</b> (art. 1 alin. (3))."
              : "\u00cen sistem real, cheltuielile se \u00eenscriu. <b>Zero e un r\u0103spuns valid</b> \u2014 gol nu e.");
    };
    mod.addEventListener("change", potriveste);
    cat.addEventListener("change", potriveste);
    potriveste();

    corp.querySelector("#rf-adauga").addEventListener("click", async () => {
      if (cereAlegerile(corp, ["#rf-categorie", "#rf-mod_venit_net"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
      const corpJson = { an: an, categorie: Number(cat.value), mod_venit_net: Number(mod.value),
                         sursa_venit: corp.querySelector("#rf-sursa_venit").value,
                         venit_brut: corp.querySelector("#rf-venit_brut").value };
      const ch = corp.querySelector("#rf-cheltuieli_deductibile");
      if (mod.value !== "3" && ch.value !== "") corpJson.cheltuieli_deductibile = ch.value;
      const zona = corp.querySelector("#rf-eroare");
      zona.innerHTML = "";
      curataEroriCamp(corp);
      try {
        await api.post(`/tenants/${t.id}/registru-evidenta-fiscala`, corpJson);
        deseneaza();
      } catch (e) {
        const eris = (e && e.erori_campuri) || [];
        eris.forEach((x) => { if (x.camp) eroareCamp(corp, `rf-${x.camp}`, x.mesaj || ""); });
        zona.innerHTML = `<div class="dec-avert" role="alert">
          <div class="dec-avert-cap">${esc((e && e.mesaj) || "R\u00e2ndul nu s-a \u00eenscris.")}</div>
          <ul>${eris.map((x) => `<li>${esc(x.mesaj || "")}</li>`).join("")}</ul></div>`;
      }
    });
  };

  deseneaza();
}


// [lista 3, 30.08.2026] REGISTRUL-INVENTAR (cod 14-1-2), al doilea registru obligatoriu din
// Legea 82/1991 art. 20. Continutul: OMFP 2634/2015, Anexa 2 — sase coloane.
//
// ECRANUL NU COMPLETEAZA COLOANA 4. Butonul „Adu soldurile din balanta" umple coloana 3 (valoarea
// contabila) si LASA GOALA coloana 4 (valoarea de inventar), fiindca aceea vine din numarare, nu
// din evidenta. Daca s-ar completa singura, registrul ar iesi cu zero diferente pe toate conturile
// — ar arata ca o inventariere facuta bine si ar fi una care nu s-a facut deloc.
//
// Diferenta si totalurile se ARATA calculate, nu se tasteaza: coloana 5 e, prin norma, diferenta
// dintre 3 si 4, iar un camp tastat le-ar putea contrazice pe amandoua.
async function ecranRegistruInventar(corp, nav, t) {
  const azi = new Date();
  let exercitiu = azi.getFullYear();
  let momentul = "sfarsit_exercitiu";
  let propunere = [];

  const MOMENTE = {
    inceput_activitate: "La \u00eenceputul activit\u0103\u021bii",
    sfarsit_exercitiu: "La sf\u00e2r\u0219itul exerci\u021biului financiar",
    incetare_activitate: "La \u00eencetarea activit\u0103\u021bii",
  };
  const ETICHETE = {
    cont: "Contul", element: "Elementul inventariat", gestiune: "Gestiunea",
    valoare_contabila: "Valoarea contabil\u0103", valoare_inventar: "Valoarea de inventar",
    cauza: "Cauza diferen\u021bei", data_inventariere: "Data inventarierii",
    document: "Lista / procesul-verbal",
  };
  // [C103] exercițiul, momentul și soldurile din balanță cerute în șir: un singur contor, deci numai registrul (și propunerea) cerute ultimele ajung pe ecran
  const cerereNoua = ultimaCerere();

  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103...</p>`;
    const actuala = cerereNoua();
    let d = null;
    try {
      d = await api.get(`/tenants/${t.id}/registru-inventar?exercitiu=${exercitiu}&momentul=${momentul}`);
      if (!actuala()) return;
    } catch (e) {
      if (!actuala()) return;
      corp.innerHTML = `<p class="ecran-nota">Nu s-a putut \u00eenc\u0103rca registrul. ${esc((e && (e.mesaj || e.message)) || "")}</p>`;
      return;
    }
    const randuri = (d && d.randuri) || [];

    const tabel = !randuri.length
      ? `<div class="stare-goala"><b>Niciun r\u00e2nd \u00eenscris.</b> Registrul gol \u00eenseamn\u0103 <i>nicio inventariere \u00eenscris\u0103</i> \u2014 <b>nu</b> \u201etotul se potrive\u0219te\u201d. Valoarea de inventar vine din num\u0103rarea faptic\u0103, pe baza listelor de inventariere, deci nu se poate deduce din eviden\u021b\u0103.</div>`
      : `<div><table class="fd-tabel">
          <thead><tr><th>Nr. crt.</th><th>Contul</th><th>Elementul inventariat</th>
            <th class="fd-td-num">Valoarea contabil\u0103</th><th class="fd-td-num">Valoarea de inventar</th>
            <th class="fd-td-num">Diferen\u021be din evaluare</th><th>Cauzele diferen\u021belor</th></tr></thead>
          <tbody>${randuri.map((r) => `<tr>
              <td>${esc(String(r.nr_curent))}</td><td>${esc(r.cont || "")}</td>
              <td>${esc(r.element || "")}${r.gestiune ? ` <small>(${esc(r.gestiune)})</small>` : ""}</td>
              <td class="fd-td-num">${bani(r.valoare_contabila)} lei</td>
              <td class="fd-td-num">${bani(r.valoare_inventar)} lei</td>
              <td class="fd-td-num">${r.diferenta ? bani(r.diferenta) + " lei" : "\u2014"}</td>
              <td>${esc(r.cauza || "\u2014")}</td></tr>`).join("")}</tbody>
          <tfoot><tr><td colspan="3">Total</td>   <!-- [lotul 11, decizia Costin 10.3: \u201eTotalurile \u2026 fix\u201d] r\u00e2ndul de total r\u0103m\u00e2ne jos, \u00een vedere, sub coloanele lui (DS cap.9 v2.100) -->
            <td class="fd-td-num">${bani(d.total_valoare_contabila)} lei</td>
            <td class="fd-td-num">${bani(d.total_valoare_inventar)} lei</td>
            <td class="fd-td-num">${esc(String(d.randuri_cu_diferenta))} din ${esc(String(randuri.length))} cu diferen\u021b\u0103</td><td></td></tr></tfoot>
        </table></div>`;

    const propuse = !propunere.length ? "" : `
      <h3 style="margin-top:22px">Solduri din balan\u021b\u0103 (${cate(propunere.length, "cont", "conturi")})</h3>
      <p class="pf-intro">Astea sunt <b>coloana 3</b>. <b>Coloana 4 r\u0103m\u00e2ne goal\u0103</b> \u2014 valoarea de inventar o \u0219tie doar cine a num\u0103rat. Alege un cont ca s\u0103-l duci \u00een formular.</p>
      <div><table class="fd-tabel">
        <tbody>${propunere.map((p, i) => `<tr>
          <td>${esc(p.cont)}</td><td>${esc(p.element)}</td>
          <td class="fd-td-num">${bani(p.valoare_contabila)} lei ${esc(p.sens)}</td>
          <td><button class="buton-secundar ri-ia" data-i="${i}">Duc \u00een formular</button></td></tr>`).join("")}</tbody>
      </table></div>`;

    corp.innerHTML = `
      <h2 class="pf-titlu">Registrul-inventar</h2>
      <p class="pf-intro">Registru obligatoriu (Legea 82/1991, art. 20), cod 14-1-2. Se \u00eentocme\u0219te <b>f\u0103r\u0103 \u0219ters\u0103turi \u0219i f\u0103r\u0103 spa\u021bii libere</b>, pe baza listelor de inventariere \u0219i a proceselor-verbale.<br><small>${esc(d.temei_obligatie || "")}</small><br><small>${esc(d.temei || "")}</small></p>
      <div class="rezumat-fix" style="display:flex;gap:8px;align-items:flex-end;flex-wrap:wrap;margin-bottom:10px">   <!-- [lotul 10, 421] exercițiul și momentul rămân sus -->
        <label class="camp"><span class="camp-eticheta">Exerci\u021biul</span><input type="number" id="ri-an" class="camp-input" value="${exercitiu}" style="max-width:120px"></label>
        <label class="camp"><span class="camp-eticheta">Momentul</span><select id="ri-moment" class="camp-input">
          ${Object.keys(MOMENTE).map((k) => `<option value="${k}"${momentul === k ? " selected" : ""}>${esc(MOMENTE[k])}</option>`).join("")}
        </select></label>
        <button class="buton-secundar" id="ri-propune">Adu soldurile din balan\u021b\u0103</button>
      </div>
      <p class="pf-intro">${esc(d.temei_completitudine || "")}</p>
      ${tabel}
      ${propuse}
      <h3 style="margin-top:22px">\u00censcrie un r\u00e2nd</h3>
      <div style="display:flex;gap:10px;flex-wrap:wrap;max-width:960px">
        ${["cont", "element", "gestiune"].map((c) => `<label class="camp"><span class="camp-eticheta">${esc(ETICHETE[c])}</span><input type="text" id="ri-${c}" class="camp-input"></label>`).join("")}
        ${["valoare_contabila", "valoare_inventar"].map((c) => `<label class="camp"><span class="camp-eticheta">${esc(ETICHETE[c])}</span><input type="number" step="0.01" id="ri-${c}" class="camp-input"></label>`).join("")}
        <label class="camp"><span class="camp-eticheta">${esc(ETICHETE.cauza)}</span><input type="text" id="ri-cauza" class="camp-input"></label>
        <label class="camp"><span class="camp-eticheta">${esc(ETICHETE.data_inventariere)}</span><input type="date" id="ri-data_inventariere" class="camp-input"></label>
        <label class="camp"><span class="camp-eticheta">${esc(ETICHETE.document)}</span><input type="text" id="ri-document" class="camp-input"></label>
      </div>
      <p class="pf-intro" id="ri-dif">Diferen\u021ba se calculeaz\u0103 singur\u0103, dup\u0103 norm\u0103: valoarea contabil\u0103 minus valoarea de inventar.</p>
      <div class="bara-fixa"><div id="ri-eroare"></div><button class="buton-primar" id="ri-adauga" data-actiune="POST /tenants/{tenant_id}/registru-inventar">\u00censcrie \u00een registru</button></div>`;   // [lotul 10, 421/424] acțiunea și refuzul ei, lipite jos

    corp.querySelector("#ri-an").addEventListener("change", (e) => { exercitiu = Number(e.target.value) || exercitiu; propunere = []; deseneaza(); });
    corp.querySelector("#ri-moment").addEventListener("change", (e) => { momentul = e.target.value; deseneaza(); });
    corp.querySelector("#ri-propune").addEventListener("click", async () => {
      const actuala = cerereNoua();
      try {
        const p = await api.get(`/tenants/${t.id}/registru-inventar/propunere?an=${exercitiu}&luna=12`);
        if (!actuala()) return;
        propunere = (p && p.randuri) || [];
        deseneaza();
      } catch (e) { if (!actuala()) return; arataMesaj((e && (e.mesaj || e.message)) || "nu s-au putut aduce soldurile", "rau"); }
    });
    corp.querySelectorAll(".ri-ia").forEach((b) => b.addEventListener("click", () => {
      const p = propunere[Number(b.dataset.i)];
      if (!p) return;
      corp.querySelector("#ri-cont").value = p.cont;
      corp.querySelector("#ri-element").value = p.element;
      corp.querySelector("#ri-valoare_contabila").value = p.valoare_contabila;
      // coloana 4 se lasa goala INTENTIONAT — vezi comentariul de deasupra ecranului
      focusFaraSalt(corp.querySelector("#ri-valoare_inventar"));
    }));

    const arataDif = () => {
      const vc = Number(corp.querySelector("#ri-valoare_contabila").value);
      const vi = corp.querySelector("#ri-valoare_inventar").value;
      const z = corp.querySelector("#ri-dif");
      if (vi === "" || isNaN(vc)) {
        z.textContent = "Diferen\u021ba se calculeaz\u0103 singur\u0103, dup\u0103 norm\u0103: valoarea contabil\u0103 minus valoarea de inventar.";
        return;
      }
      const dif = vc - Number(vi);
      z.innerHTML = dif === 0
        ? "Diferen\u021b\u0103 <b>0</b> \u2014 cauza nu se cere."
        : `Diferen\u021b\u0103 <b>${bani(dif)} lei</b> \u2014 <b>cauza e obligatorie</b> (coloana 6).`;
    };
    ["#ri-valoare_contabila", "#ri-valoare_inventar"].forEach((s) =>
      corp.querySelector(s).addEventListener("input", arataDif));

    corp.querySelector("#ri-adauga").addEventListener("click", async () => {
      const corpJson = { exercitiu: exercitiu, momentul: momentul };
      ["cont", "element", "gestiune", "valoare_contabila", "valoare_inventar", "cauza",
       "data_inventariere", "document"].forEach((c) => {
        const el = corp.querySelector(`#ri-${c}`);
        if (el && el.value !== "") corpJson[c] = el.value;
      });
      const zonaEroare = corp.querySelector("#ri-eroare");
      zonaEroare.innerHTML = "";
      curataEroriCamp(corp);
      try {
        await api.post(`/tenants/${t.id}/registru-inventar`, corpJson);
        propunere = [];
        deseneaza();
      } catch (e) {
        const eris = (e && e.erori_campuri) || [];
        eris.forEach((x) => { if (x.camp) eroareCamp(corp, `ri-${x.camp}`, x.mesaj || ""); });
        zonaEroare.innerHTML = `<div class="dec-avert" role="alert">
          <div class="dec-avert-cap">${esc((e && e.mesaj) || "R\u00e2ndul nu s-a \u00eenscris.")}</div>
          <ul>${eris.map((x) => `<li><b>${esc(ETICHETE[x.camp] || x.camp || "")}</b> \u2014 ${esc(x.mesaj || "")}</li>`).join("")}</ul>
        </div>`;
      }
    });
  };
  deseneaza();
}


// [lista 3, 30.08.2026] CELE DOUA REGISTRE cerute de art. 321 alin. (4) CF, prin normele lui.
//
// Ecranul e locul unde se INSCRIE, nu doar unde se citeste: substanta lor nu se deriva din facturi
// (un nontransfer e o miscare de bunuri FARA vanzare), deci fara formular registrul ar ramane gol
// pentru totdeauna. De-aia are si POST, spre deosebire de Cartea mare sau jurnalul de marja.
//
// EXCEPTIILE se ARATA, nu se aplica: aplicatia nu hotaraste ca un bun intra intr-una din cele cinci
// scutiri. O scutire decisa de masina pe descrierea unui bun ar produce exact evidenta care nu se
// poate apara la control — completa la vedere, incompleta in fapt.
async function ecranRegistre321(corp, nav, t) {
  let fel = "nontransfer";

  const ETICHETE = {
    partener_denumire: "Denumirea partenerului", partener_adresa: "Adresa partenerului",
    data_transport: "Data transportului", descriere: "Descrierea bunurilor",
    cantitate: "Cantitatea", valoare: "Valoarea (lei)",
    data_retur: "Data returului", descriere_returnate: "Descrierea bunurilor returnate",
    cantitate_returnate: "Cantitatea returnat\u0103", descriere_nereturnate: "Descrierea bunurilor nereturnate",
    cantitate_nereturnate: "Cantitatea nereturnat\u0103",
    documente: "Documentele emise", data_documente: "Data documentelor",
  };
  const RETUR = ["data_retur", "descriere_returnate", "cantitate_returnate",
                 "descriere_nereturnate", "cantitate_nereturnate"];

  const camp = (c, tip) => `<label class="camp"><span class="camp-eticheta">${esc(ETICHETE[c] || c)}</span>` +
    `<input type="${tip || "text"}" id="r3-${c}" class="camp-input"${tip === "number" ? ' step="0.001"' : ""}></label>`;

  const tipul = (c) => (c === "data_transport" || c === "data_retur" || c === "data_documente") ? "date"
    : (c.indexOf("cantitate") === 0 || c === "valoare") ? "number" : "text";
  const cerereNoua = ultimaCerere();   // [C103] registrul (fel) schimbat în șir: numai registrul ales ultimul ajunge pe ecran

  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103...</p>`;
    const actuala = cerereNoua();
    let d = null;
    try {
      d = await api.get(`/tenants/${t.id}/registre-art321/${fel}`);
      if (!actuala()) return;
    } catch (e) {
      if (!actuala()) return;
      corp.innerHTML = `<p class="ecran-nota">Nu s-a putut \u00eenc\u0103rca registrul. ${esc((e && (e.mesaj || e.message)) || "")}</p>`;
      return;
    }
    const randuri = (d && d.randuri) || [];
    const cerute = (d && d.campuri_cerute) || [];
    const coloane = cerute.concat(RETUR, ["documente", "data_documente"]);

    const tabel = !randuri.length
      ? `<div class="stare-goala">Niciun r\u00e2nd \u00eenscris \u00een registrul acesta. <b>Nu se completeaz\u0103 singur</b> \u2014 opera\u021biunile pe care le consemneaz\u0103 sunt mi\u0219c\u0103ri de bunuri f\u0103r\u0103 v\u00e2nzare, deci nu se pot deduce din facturi.</div>`
      : `<div><table class="fd-tabel">
          <thead><tr><th>Nr. ord.</th>${coloane.map((c) => `<th>${esc(ETICHETE[c] || c)}</th>`).join("")}</tr></thead>
          <tbody>${randuri.map((r) => `<tr><td>${esc(String(r.nr_ordine))}</td>` +
            coloane.map((c) => {
              const v = r[c];
              if (v == null || v === "") return `<td>\u2014</td>`;
              if (tipul(c) === "date") return `<td>${dataRo(v)}</td>`;
              if (tipul(c) === "number") return `<td class="fd-td-num">${bani(v)}</td>`;
              return `<td>${esc(String(v))}</td>`;
            }).join("") + `</tr>`).join("")}</tbody>
        </table></div>`;

    const exceptii = (d.exceptii && d.exceptii.length)
      ? `<details style="margin-top:14px;max-width:760px"><summary><b>Cinci cazuri pentru care norma spune c\u0103 registrul <i>nu</i> se completeaz\u0103</b></summary>
         <p class="pf-intro" style="margin-top:6px">Sunt aici ca s\u0103 le cite\u0219ti tu. <b>Aplica\u021bia nu hot\u0103r\u0103\u0219te c\u0103 un bun intr\u0103 \u00eentr-unul din ele</b> \u2014 o scutire aplicat\u0103 automat pe descrierea unui bun ar l\u0103sa o eviden\u021b\u0103 incomplet\u0103 la control.</p>
         <ul>${d.exceptii.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></details>`
      : "";

    corp.innerHTML = `
      <h2 class="pf-titlu">Registre art. 321</h2>
      <p class="pf-intro">Cele dou\u0103 registre pe care normele metodologice ale art. 321 alin. (4) din Codul fiscal le cer expres. <br><small>${esc(d.temei || "")}</small></p>
      <div class="rezumat-fix" style="display:flex;gap:8px;align-items:flex-end;flex-wrap:wrap;margin-bottom:10px">   <!-- [lotul 10, 421 / 424, DS cap.9 v2.97 pct.5] registrul ales rămâne sus -->
        <label class="camp"><span class="camp-eticheta">Registrul</span><select id="r3-fel" class="camp-input" data-butoane>
          <option value="nontransfer"${fel === "nontransfer" ? " selected" : ""}>Nontransferuri \u00b7 lit. e)</option>
          <option value="bunuri_primite"${fel === "bunuri_primite" ? " selected" : ""}>Bunuri primite pentru lucr\u0103ri \u00b7 lit. f)</option>
        </select></label>
      </div>
      <p class="pf-intro">${esc(d.temei_completitudine || "")}</p>
      ${tabel}
      ${exceptii}
      <h3 style="margin-top:22px">\u00censcrie un r\u00e2nd</h3>
      <p class="pf-intro">Num\u0103rul de ordine se d\u0103 singur. C\u00e2mpurile cerute de norm\u0103 nu se pot l\u0103sa goale \u2014 iar dac\u0103 lipse\u0219te unul, \u00ee\u021bi spunem <b>care</b> \u0219i <b>sub ce norm\u0103</b>.</p>
      <div style="display:flex;gap:10px;flex-wrap:wrap;max-width:960px">
        ${cerute.map((c) => camp(c, tipul(c))).join("")}
      </div>
      <details style="margin-top:10px;max-width:960px"><summary>Retur dup\u0103 lucr\u0103ri \u0219i documente (se completeaz\u0103 c\u00e2nd bunurile se \u00eentorc)</summary>
        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:8px">
          ${RETUR.concat(["documente", "data_documente"]).map((c) => camp(c, tipul(c))).join("")}
        </div></details>
      <div class="bara-fixa"><div id="r3-eroare"></div><button class="buton-primar" id="r3-adauga" data-actiune="POST /tenants/{tenant_id}/registre-art321/{fel}">\u00censcrie \u00een registru</button></div>`;   // [lotul 10, 421/424]

    corp.querySelector("#r3-fel").addEventListener("change", (e) => { fel = e.target.value; deseneaza(); });
    corp.querySelector("#r3-adauga").addEventListener("click", async () => {
      const corpJson = {};
      coloane.forEach((c) => {
        const el = corp.querySelector(`#r3-${c}`);
        if (el && el.value !== "") corpJson[c] = el.value;
      });
      const zonaEroare = corp.querySelector("#r3-eroare");
      zonaEroare.innerHTML = "";
      curataEroriCamp(corp);
      try {
        await api.post(`/tenants/${t.id}/registre-art321/${fel}`, corpJson);
        deseneaza();
      } catch (e) {
        // Marcajul pe INPUT, prin helperul comun: la un formular de 13 campuri o lista de erori
        // iti spune CE lipseste, dar nu UNDE. `eroareCamp` pune conturul rosu si `aria-invalid`.
        const eris = (e && e.erori_campuri) || [];
        eris.forEach((x) => { if (x.camp) eroareCamp(corp, `r3-${x.camp}`, x.mesaj || ""); });
        zonaEroare.innerHTML = `<div class="dec-avert" role="alert">
          <div class="dec-avert-cap">${esc((e && e.mesaj) || "Rândul nu s-a înscris.")}</div>
          <ul>${eris.map((x) => `<li><b>${esc(ETICHETE[x.camp] || x.camp || "")}</b> — ${esc(x.mesaj || "")}</li>`).join("")}</ul>
        </div>`;
      }
    });
  };
  deseneaza();
}


// [R3, lista 3, 30.08.2026] CATEGORIA DE MARIME, aratata langa selectorul care pana azi o GHICEA.
//
// Ecranul NU o alege. Situatiile financiare datorate depind de categorie (OMFP 1802/2014 pct.9), dar
// derivarea are nevoie de DOUA exercitii consecutive (pct.13) — iar cand nu le are, raspunsul corect
// e „nu se poate determina", nu „micro". Deci se ARATA ce iese din date, cu motivul, si alegerea
// ramane a contabilului: aplicatia spune ce stie, nu decide in locul lui pe o derivare fara date.
function _casetaCategorie(c) {
  if (!c) return "";
  const cat = c.categorie;
  const ind = (x, cheie) => (x && x[cheie] != null ? bani(x[cheie]) : "\u2014");
  const tabel = (c.indicatori_curent || c.indicatori_precedent) ? `
    <table class="fd-tabel" style="max-width:620px;margin-top:8px">
      <thead><tr><th>Criteriu</th><th class="fd-td-num">Exerci\u021biul precedent</th>
        <th class="fd-td-num">Exerci\u021biul curent</th><th class="fd-td-num">Prag microentit\u0103\u021bi</th></tr></thead>
      <tbody>
        <tr><td>Totalul activelor</td><td class="fd-td-num">${ind(c.indicatori_precedent, "total_active")}</td>
            <td class="fd-td-num">${ind(c.indicatori_curent, "total_active")}</td>
            <td class="fd-td-num">${bani(c.praguri.micro.total_active)}</td></tr>
        <tr><td>Cifra de afaceri net\u0103</td><td class="fd-td-num">${ind(c.indicatori_precedent, "cifra_afaceri_neta")}</td>
            <td class="fd-td-num">${ind(c.indicatori_curent, "cifra_afaceri_neta")}</td>
            <td class="fd-td-num">${bani(c.praguri.micro.cifra_afaceri_neta)}</td></tr>
        <tr><td>Num\u0103rul mediu de salaria\u021bi</td>
            <td class="fd-td-num">${c.indicatori_precedent ? (c.indicatori_precedent.nr_mediu_salariati ?? "\u2014") : "\u2014"}</td>
            <td class="fd-td-num">${c.indicatori_curent ? (c.indicatori_curent.nr_mediu_salariati ?? "\u2014") : "\u2014"}</td>
            <td class="fd-td-num">${c.praguri.micro.nr_mediu_salariati}</td></tr>
      </tbody></table>` : "";
  const numit = { micro: "microentitate", mici: "entitate mic\u0103", mijlocii_mari: "entitate mijlocie sau mare" };
  // [deficiența 235, comanda Costin 12.10.2026] primul exercițiu: încadrarea după regula entităților nou-înființate (OMFP 1802/2014 pct.22
  // alin.(1) — formatul se alege), casetă de informare, nu de atenție; textul normei vine de la server (`motiv`)
  if (cat === "primul_exercitiu") {
    return `<div class="caseta-info" style="margin-top:10px"><span class="ci-mesaj">${esc(c.motiv || "")}</span></div>`;
  }
  if (cat === "nedeterminata") {
    return `<div class="caseta-atentie" style="margin-top:10px">
        <div class="ca-mesaj"><b>Categoria de m\u0103rime nu se poate determina, deci aplica\u021bia nu poate \u0219ti care situa\u021bie financiar\u0103 e datorat\u0103.</b>
          ${esc(c.motiv || "")}. Alege tipul mai jos pe r\u0103spunderea ta, sau completeaz\u0103 eviden\u021ba exerci\u021biului precedent.</div>
      </div>${tabel}`;
  }
  return `<div class="caseta-info" style="margin-top:10px"><span class="ci-mesaj">
      Din date, firma e <b>${esc(numit[cat] || cat)}</b> \u2014 ${esc(c.motiv || "")}.
      ${c.decis_de_numarul_de_salariati ? "<b>Aten\u021bie:</b> \u00eencadrarea depinde de num\u0103rul mediu de salaria\u021bi, care e o aproximare lunar\u0103, nu num\u0103rul mediu din metodologia oficial\u0103." : ""}
      Alegerea tipului r\u0103m\u00e2ne a ta.</span></div>${tabel}`;
}

async function ecranBilant(corp, nav, t) {
  {
    corp.innerHTML = `
      <h2 class="pf-titlu">Bilan\u021b anual ${semnAjutor("F013")}</h2>
      <p class="pf-intro">Genereaz\u0103 \u0219i valideaz\u0103 situa\u021biile financiare (validator ANAF pe server).</p>
      <div class="rezumat-fix" style="display:flex;gap:8px;align-items:flex-end;flex-wrap:wrap">   <!-- [lotul 10, 421 / 424, DS cap.9 v2.97 pct.5-6] anul, tipul și acțiunile rămân sus -->
        <label class="camp"><span class="camp-eticheta">An</span><input type="number" id="bl-an" class="camp-input" value="${new Date().getFullYear() - 1}" style="width:90px"></label>
        <label class="camp"><span class="camp-eticheta">Tip</span><select id="bl-tip" class="camp-input" data-butoane>${ALEGE}
          <option value="s1005">S1005 \u00b7 microentit\u0103\u021bi</option>
          <option value="s1003">S1003 \u00b7 entit\u0103\u021bi mici</option>
        </select></label>
        <button class="buton-primar" id="bl-val" data-actiune="POST /tenants/{tenant_id}/s1003-valideaza|POST /tenants/{tenant_id}/s1005-valideaza">Valideaz\u0103 (ANAF)</button>
        <button class="buton-secundar" id="bl-xml">Descarc\u0103 XML</button>
        <button class="buton-primar" id="bl-coada" data-actiune="POST /coada">Trimite \u00een coad\u0103 \u2192</button>
        <span class="ecran-nota" id="bl-actiuni-motiv" role="status" style="align-self:center"></span>
      </div>
      <div id="bl-categorie"></div>
      <div id="bl-precedent"></div>
      <div id="bl-rez" style="margin-top:10px"></div>
      <div id="bl-coada-mesaj"></div>`;
    const rez = corp.querySelector("#bl-rez");
    const zonaCat = corp.querySelector("#bl-categorie");
    // [proba plasei, 151/188: primul clic pe „Validează” / „Descarcă XML” se pierdea] părăsirea câmpului „An” emite din nou `change`, cu
    // aceeași valoare; caseta categoriei era înlocuită cu „Se calculează…”, fereastra (centrată) se micșora, iar butonul fugea între
    // apăsarea și ridicarea mouse-ului. Categoria se cere numai pentru un an NOU, iar caseta veche rămâne până sosește cea nouă.
    let anCategorie = null;
    const cerereCategoria = ultimaCerere();   // [C103] anul schimbat în șir: numai caseta anului cerut ultimul ajunge pe ecran
    const cereCategoria = async () => {
      const an = corp.querySelector("#bl-an").value;
      if (an === anCategorie) return;
      anCategorie = an;
      const actuala = cerereCategoria();
      if (!zonaCat.innerHTML.trim()) zonaCat.innerHTML = `<p class="ecran-nota">Se calculeaz\u0103 categoria de m\u0103rime...</p>`;
      zonaCat.setAttribute("aria-busy", "true");
      try {
        const c = await api.get(`/tenants/${t.id}/categorie-marime?an=${an}`);
        if (!actuala()) return;   // un an schimbat între timp își aduce propria casetă
        zonaCat.innerHTML = _casetaCategorie(c);
      } catch (e) {
        if (!actuala()) return;
        anCategorie = null;
        zonaCat.innerHTML = "";
        arataMesaj(zonaCat, (e && e.mesaj) || "Nu s-a putut calcula categoria de m\u0103rime.", "eroare");
      } finally { zonaCat.removeAttribute("aria-busy"); }
    };
    corp.querySelector("#bl-an").addEventListener("change", cereCategoria);
    cereCategoria();
    const par = () => `an=${corp.querySelector("#bl-an").value}`;
    const tip = () => corp.querySelector("#bl-tip").value;
    // [deficiența 236, comanda Costin 12.10.2026] „Reține ultimul tip ales pentru fiecare firmă.” Ultima alegere a omului, în acest
    // browser, pe utilizator + firmă (ca ciorna facturii); fără alegere salvată, „— alege —” (nimic ales în locul lui). Gard: e2e 236.
    const cheieTip = () => { const u = sesiune.user(); return `iconta_bilant_tip:${u && u.id != null ? u.id : "anonim"}:${t.id}`; };
    try { const v = localStorage.getItem(cheieTip()); if (v === "s1005" || v === "s1003") corp.querySelector("#bl-tip").value = v; } catch { /* stocare blocată */ }
    corp.querySelector("#bl-tip").addEventListener("change", () => {
      try { if (tip()) localStorage.setItem(cheieTip(), tip()); else localStorage.removeItem(cheieTip()); } catch { /* stocare blocată */ }
    });
    // [deficiența 222, comanda Costin 10.10.2026] fără tip de declarație ales, acțiunile pe declarație sunt inactive — ca „Continuă”
    // din Declarații (DS cap.1 v2.87, gard ACTIUNE_FARA_TIP). `cereAlegerile` din handlere rămâne refuzul de lângă câmp (FAPT_FISCAL_NECERUT).
    // [deficiența 228, comanda Costin 12.10.2026] „«Validează» și «Trimite în coadă» sunt inactive până se completează coloana «An
    // precedent», cu motivul afișat lângă ele.” Serverul refuză generarea cu coloana goală (221) — și XML-ul, deci și „Descarcă XML”.
    // Starea coloanei e a anului și tipului ALESE: cât nu e citită (sau citirea a eșuat), acțiunile rămân inactive (fail-closed).
    const actiuniTip = ["#bl-val", "#bl-xml", "#bl-coada"].map((s) => corp.querySelector(s));
    const motivActiuni = corp.querySelector("#bl-actiuni-motiv");
    let stareaPrec = { cheie: "", motiv: "" };          // motiv gol = coloana „An precedent” e completă pentru `cheie`
    const cheiaAleasa = () => `${parseInt(corp.querySelector("#bl-an").value, 10)}|${tip()}`;
    const legaTip = () => {
      const motiv = !tip() ? "" : (stareaPrec.cheie !== cheiaAleasa() ? "Se citește coloana „An precedent”…" : stareaPrec.motiv);
      actiuniTip.forEach((b) => { b.disabled = !tip() || !!motiv; });
      motivActiuni.textContent = motiv;
    };
    corp.querySelector("#bl-tip").addEventListener("change", legaTip);
    corp.querySelector("#bl-an").addEventListener("change", legaTip);
    legaTip();
    // [deficiența 221, decizia Costin 11.10.2026] coloana „An precedent”: din bilanțul anului precedent din aplicație, altfel completată
    // manual cu avertisment vizibil; fără ea serverul refuză generarea. Zona spune sursa și, unde lipsește, cere completarea.
    const zonaPrec = corp.querySelector("#bl-precedent");
    const SURSA = { bilant: "bilanțul pe %AN validat în aplicație", evidenta: "evidența pe %AN din aplicație", manual: "completată manual" };
    // ca la categoria de mărime (151/188): zona veche rămâne până sosește cea nouă — golirea ei mișca fereastra (centrată) sub cursor
    const cererePrec = ultimaCerere();   // [C103] anul și tipul schimbate în șir: numai zona anului și tipului aleși ultimii ajunge pe ecran
    let ultimaPropunere = null;                   // [244] mesajul propunerii rămâne după recitirea refuzului
    // [lotul 11, 440 — decizia Costin 10.3 „mesajele lângă buton: da, reorganizezi”] refuzul stă LÂNGĂ butoanele pe care le face inactive,
    // cu textul lui, o singură dată: zona „An precedent” care îl ține urcă imediat sub rândul acțiunilor; fără refuz (formularul coloanei,
    // sursa ei) stă la locul ei, după categoria de mărime
    const zonaLangaButoane = (da) => {
      const ref = da ? corp.querySelector(".rezumat-fix") : zonaCat;
      if (ref && ref.nextElementSibling !== zonaPrec) ref.insertAdjacentElement("afterend", zonaPrec);
    };
    const incarcaPrecedent = async () => {
      const actuala = cererePrec();   // și fără tip: o citire pornită înainte nu mai umple zona golită
      if (!tip()) { zonaPrec.innerHTML = ""; zonaPrec.removeAttribute("data-pentru"); zonaLangaButoane(false); legaTip(); return; }
      const an = parseInt(corp.querySelector("#bl-an").value, 10);
      const cheie = `${an}|${tip()}`;
      let p;
      legaTip();
      try { p = await api.get(`/tenants/${t.id}/bilant-an-precedent?an=${an}&tip=${tip()}`); } catch (e) {
        if (!actuala()) return;   // refuzul unei citiri vechi nu acoperă zona anului și tipului aleși
        const m = (e && e.mesaj) || "Nu s-a putut citi coloana „An precedent”.";
        zonaLangaButoane(true);
        zonaPrec.innerHTML = `<div class="bl-prec-refuz"></div>`;
        arataMesaj(zonaPrec.querySelector(".bl-prec-refuz"), m, "eroare");
        zonaPrec.dataset.pentru = cheie;          // zona e a anului și tipului aleși și când spune refuzul
        // [varianta (a), decizia Costin 13.10.2026] „Aplicația propune, la cererea contabilului, nota de închidere la 31.12 …” — lângă
        // refuzul cu clasele 6/7 neînchise, câte un buton pe anul de închis; notele intră ciornă și se validează în Jurnal (R36)
        const ani = (e && e.detaliu && e.detaliu.ani_inchidere) || [];
        // [deficiența 244] notele propuse care așteaptă validarea: legătura deschide Registrul jurnal pe luna lor (decembrie), cu ele
        // evidențiate — nu un text de căutat („Jurnal — notele de validat” ducea la Jurnalul regim marjă)
        const propuse = (e && e.detaliu && e.detaliu.propuse) || [];
        if (ani.length || propuse.length) {
          const dinNou = new Set(propuse.map((p) => p.an));
          zonaPrec.insertAdjacentHTML("beforeend", `<div class="bl-inchidere" style="margin-top:8px">${propuse.map((p) =>
            `<button class="btn-link bl-inchidere-jurnal" data-an="${esc(String(p.an))}" data-note="${esc(p.note.map((n) => n.id).join(","))}">`
            + `Deschide notele de închidere în Registrul jurnal — decembrie ${esc(String(p.an))}</button>`).join(" ")}${ani.map((a) =>
            `<button class="buton-secundar bl-inchidere-propune" data-an="${esc(String(a))}" data-actiune="POST /tenants/{tenant_id}/bilant-inchidere-propunere">`
            + `${dinNou.has(a) ? "Propune din nou" : "Propune"} nota de închidere la 31.12.${esc(String(a))}</button>`).join(" ")}<div class="bl-inchidere-mesaj"></div></div>`);
          zonaPrec.querySelectorAll(".bl-inchidere-jurnal").forEach((b) => b.addEventListener("click", () => {
            if (nav.dinRefuz) nav.dinRefuz();   // [lotul 11, 445] din refuz: bilanțul de dedesubt se păstrează, X / „← Înapoi” întorc la el
            nav.deschide("Registru jurnal", (c2) => ecranJurnal(c2, nav, t, { an: parseInt(b.dataset.an, 10), luna: 12,
              evidentiaza: b.dataset.note.split(",").map(Number) }), { lat: "tabel" });   // [394] ca la cardul jurnalului
          }));
          if (ultimaPropunere && ultimaPropunere.cheie === cheie) arataMesaj(zonaPrec.querySelector(".bl-inchidere-mesaj"), ultimaPropunere.mesaj, "ok");
          zonaPrec.querySelectorAll(".bl-inchidere-propune").forEach((b) => b.addEventListener("click", async () => {
            const zm = zonaPrec.querySelector(".bl-inchidere-mesaj");
            b.disabled = true;
            try {
              const r = await api.post(`/tenants/${t.id}/bilant-inchidere-propunere?an=${b.dataset.an}`, {});
              // [244] refuzul se recitește: după propunere spune că notele așteaptă validarea, cu legătura spre ele
              ultimaPropunere = { cheie, mesaj: `${r.mesaj} Notele sunt ${stareNota(r, true)}. ${pasNota(r, true)}` };
              await incarcaPrecedent();
              if (cheie === cheiaAleasa() && !zonaPrec.querySelector(".bl-inchidere-mesaj")) {   // fără refuz: mesajul deasupra zonei
                zonaPrec.insertAdjacentHTML("afterbegin", `<div class="bl-inchidere-mesaj"></div>`);
                arataMesaj(zonaPrec.querySelector(".bl-inchidere-mesaj"), ultimaPropunere.mesaj, "ok");
              }
            } catch (e2) { arataMesaj(zm, (e2 && e2.mesaj) || "Nu s-a putut propune nota de închidere.", "eroare"); b.disabled = false; }
          }));
        }
        // [deficiența 237, retestul Costin 12.10.2026] „mesajul de oprire apare de două ori … Trebuie să apară o singură dată.” Refuzul
        // stă o dată (roșu), imediat sub rândul butoanelor; [lotul 11, 440, DS cap.6 v2.99] nota de lângă butoane nu-l repetă și nu
        // trimite la el fără text („motivul e mai jos”): spune numai că butoanele așteaptă rezolvarea lui, iar el urmează chiar dedesubt
        stareaPrec = { cheie, motiv: "Inactive până se rezolvă refuzul:" };
        legaTip();
        return;
      }
      if (!actuala()) return;          // un an / tip schimbat între timp își aduce propria zonă
      zonaLangaButoane(false);
      zonaPrec.dataset.pentru = cheie;
      stareaPrec = { cheie, motiv: p.lipsa.length
        ? `Inactive până completezi coloana „An precedent” (${p.lipsa.join(", ")}) mai jos și o salvezi.` : "" };
      legaTip();
      // [deficiența 229] primul exercițiu: coloana e goală prin lege — se spune de ce, fără formular de completat
      const sectiuni = Object.keys(p.sursa);       // [C14] F10, F20 — și F30 cap.XIX la S1005
      const primul = sectiuni.every((s) => p.sursa[s] === "primul_exercitiu");
      const surse = sectiuni.filter((s) => p.sursa[s] && p.sursa[s] !== "manual" && p.sursa[s] !== "primul_exercitiu")
        .map((s) => `${s}: ${SURSA[p.sursa[s]].replace("%AN", an - 1)}`);
      const info = primul
        ? `<div class="caseta-info bl-prec-primul" style="margin-top:10px"><span class="ci-mesaj">${esc((p.afirmatie && p.afirmatie.motiv) || "")}</span></div>`
        : (surse.length ? `<div class="caseta-info" style="margin-top:10px"><span class="ci-mesaj">Coloana „An precedent” vine din ${esc(surse.join("; "))}.</span></div>` : "");
      if (!p.de_completat.length) { zonaPrec.innerHTML = info; return; }
      // [deficiența 233, comanda Costin 12.10.2026] „Totalurile se calculează automat din componente și se afișează fără câmp.” Formula
      // fiecărui total vine de la server (`totaluri` = calculul formularului, `bilant.NOMENCLATOR_TOTALURI`); se trimit numai componentele,
      // serverul calculează totalurile la fel. [deficiența 234] rândurile în ordinea formularului, cu codul tipărit pe el („06a (301)”).
      const totaluri = (s) => (p.totaluri && p.totaluri[s]) || {};
      const valoare = (s, r, v) => {
        const f = totaluri(s)[r];
        if (!f) return v[r] || 0;
        const x = f.termeni.reduce((a, [semn, k]) => a + semn * valoare(s, k, v), 0);
        return f.pozitiv ? Math.max(x, 0) : x;
      };
      const sectiune = (s) => {
        const ordine = ((p.ordine && p.ordine[s]) || p.randuri[s]).filter((r) => p.randuri[s].includes(r));
        return `<h3 class="pf-subtitlu">An precedent — ${s === "F30" ? "F30, cap.XIX Situația veniturilor și cheltuielilor" : s}</h3>
        <table class="fd-tabel bl-prec-tabel" data-sectiune="${s}"><thead><tr><th>Rândul</th><th>Denumirea de pe formular</th><th class="fd-td-num">An precedent (lei)</th></tr></thead><tbody>
        ${ordine.map((r) => { const den = (p.denumiri && p.denumiri[s] && p.denumiri[s][r]) || "";   // [deficiența 227] numele de pe formular
          const cod = (p.coduri && p.coduri[s] && p.coduri[s][r]) || String(r);
          if (totaluri(s)[r]) return `<tr class="bl-prec-rand-total"><td>rândul ${esc(cod)}</td><td class="bl-prec-den">${esc(den)}</td><td class="fd-td-num bl-prec-total" data-rand="${r}"></td></tr>`;
          return `<tr><td>rândul ${esc(cod)}</td><td class="bl-prec-den">${esc(den)}</td><td class="fd-td-num"><input type="number" step="1" class="camp-input bl-prec-val" data-rand="${r}"
          value="${p.valori[s] && p.valori[s][r] != null ? p.valori[s][r] : ""}" aria-label="${s} rândul ${esc(cod)}${den ? " — " + esc(den) : ""}, an precedent"></td></tr>`; }).join("")}</tbody></table>`;
      };
      const recalculeaza = (tb) => {
        const v = {};
        tb.querySelectorAll(".bl-prec-val").forEach((i) => { v[i.dataset.rand] = parseInt(i.value, 10) || 0; });
        tb.querySelectorAll(".bl-prec-total").forEach((c) => { c.textContent = bani(valoare(tb.dataset.sectiune, parseInt(c.dataset.rand, 10), v)); });
      };
      zonaPrec.innerHTML = info + `<div class="caseta-atentie bl-prec-atentie" style="margin-top:10px"><div class="ca-mesaj"><b>${esc((p.afirmatie && p.afirmatie.motiv) || "")}</b></div></div>
        ${p.de_completat.map(sectiune).join("")}
        <div class="bara-fixa"><button class="buton-secundar" id="bl-prec-salveaza" data-actiune="POST /tenants/{tenant_id}/bilant-an-precedent-manual">Salvează coloana „An precedent”</button>
        <div id="bl-prec-mesaj"></div></div>`;   // [lotul 10, 421 / 424, DS cap.9 v2.97 pct.6] salvarea coloanei și mesajul ei, lipite jos
      zonaPrec.querySelectorAll(".bl-prec-tabel").forEach((tb) => { recalculeaza(tb); tb.addEventListener("input", () => recalculeaza(tb)); });
      zonaPrec.querySelector("#bl-prec-salveaza").addEventListener("click", async () => {
        const corpCerere = {};
        zonaPrec.querySelectorAll(".bl-prec-tabel").forEach((tb) => {
          const v = {};
          tb.querySelectorAll(".bl-prec-val").forEach((i) => { v[i.dataset.rand] = i.value.trim() === "" ? 0 : parseInt(i.value, 10); });
          corpCerere[tb.dataset.sectiune] = v;
        });
        const msg = zonaPrec.querySelector("#bl-prec-mesaj");
        try {
          await api.post(`/tenants/${t.id}/bilant-an-precedent-manual?an=${an}&tip=${tip()}`, corpCerere);
          await incarcaPrecedent();
          arataMesaj(zonaPrec.querySelector("#bl-prec-mesaj") || zonaPrec, "Coloana „An precedent” a fost salvată.", "ok");
        } catch (e) { arataMesaj(msg, (e && e.mesaj) || "Nu s-a putut salva coloana.", "eroare"); }
      });
    };
    corp.querySelector("#bl-tip").addEventListener("change", incarcaPrecedent);
    corp.querySelector("#bl-an").addEventListener("change", incarcaPrecedent);
    incarcaPrecedent();   // [deficiența 236] cu tipul reținut, coloana lui se citește la deschidere (fără tip: zona rămâne goală)
    corp.querySelector("#bl-val").addEventListener("click", async () => {
      curataEroriCamp(corp); if (cereAlegerile(corp, ["#bl-tip"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
      arataMesaj(rez, "Se validează…", "info");
      try {
        const r = await api.post(`/tenants/${t.id}/${tip()}-valideaza?${par()}`, {});
        const sem = r.ok
          ? `<span style="color:var(--verde);font-weight:600">\u25cf Validare f\u0103r\u0103 erori</span>`
          : `<span style="color:var(--rosu);font-weight:600">\u25cf Erori la validare</span>`;
        // [deficiența 188] rândurile care se depun, cu cifrele lor, citite din XML-ul validat (nu doar verdictul)
        // [227 + C11, 12.10.2026] fiecare rând cu denumirea de pe formular; datele informative (F30) au alte coloane decât „An precedent” /
        // „An curent” (numerele lor nu sunt sume pe doi ani), deci stau în tabelul lor, cu valorile așa cum se depun
        // [C14] F30 cap.XIX e tot pe doi ani (serverul o spune: `doi_ani`); numai F30 rd.01–03 au numărul și suma
        const doiAni = (r.randuri || []).filter((x) => x.doi_ani);
        const f30 = (r.randuri || []).filter((x) => !x.doi_ani);
        const randuri = doiAni.map((x) => `<tr><td>${esc(x.formular)}</td><td>rândul ${esc(x.cod || String(x.rand))}</td><td>${esc(x.denumire || "")}</td>`
          + `<td class="fd-td-num">${bani(x.an_precedent)}</td><td class="fd-td-num">${bani(x.an_curent)}</td></tr>`).join("");
        const randuriF30 = f30.map((x) => `<tr><td>rândul ${esc(x.cod || String(x.rand))}</td><td>${esc(x.denumire || "")}</td>`
          + `<td class="fd-td-num">${esc(String(x.an_precedent))}</td><td class="fd-td-num">${esc(String(x.an_curent))}</td></tr>`).join("");
        rez.innerHTML = `<p>${sem}</p>` +
          (r.erori ? `<pre class="tip-micut" style="white-space:pre-wrap;background:var(--fundal);padding:8px;border-radius:var(--raza)">${esc(r.erori)}</pre>` : "") +
          (r.avertismente && r.avertismente.length
            ? `<p class="pf-intro">${r.avertismente.map(esc).join("<br>")}</p>` : "") +
          (randuri ? `<h3 class="pf-subtitlu">Ce se depune — ${cate(doiAni.length, "rând cu valoare", "rânduri cu valoare")}</h3>
            <table class="fd-tabel" id="bl-randuri"><thead><tr><th>Formular</th><th>Rândul</th><th>Denumirea de pe formular</th><th class="fd-td-num">An precedent</th>`
            + `<th class="fd-td-num">An curent</th></tr></thead><tbody>${randuri}</tbody></table>` : "")
          + (randuriF30 ? `<h3 class="pf-subtitlu">Date informative (F30)</h3>
            <table class="fd-tabel" id="bl-randuri-f30"><thead><tr><th>Rândul</th><th>Denumirea de pe formular</th><th class="fd-td-num">Coloana 1</th>`
            + `<th class="fd-td-num">Coloana 2</th></tr></thead><tbody>${randuriF30}</tbody></table>` : "");
      } catch (e) { arataMesaj(rez, e.mesaj || "eroare", "eroare"); }
    });
    // [decizia Costin 07.10.2026, C11] bilanțul trece prin coadă (pregătit → validat → depus), cu drepturile declarațiilor:
    // același drum ca la orice declarație (`trimiteInCoada`: poarta validatorului, atenționările cu confirmare, refuzul real).
    etichetaTrimitere(corp.querySelector("#bl-coada"));   // [313] numele urmează pasul real
    corp.querySelector("#bl-coada").addEventListener("click", async () => {
      const zona = corp.querySelector("#bl-coada-mesaj");
      curataEroriCamp(corp); if (cereAlegerile(corp, ["#bl-tip"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
      // [deficiența 222] confirmarea = caseta „Trimisă” a declarațiilor (rescrie zona: caseta atenționărilor, dacă a fost, pleacă)
      await trimiteInCoada(zona, { tenant_id: t.id, tip: tip(), an: parseInt(corp.querySelector("#bl-an").value, 10) },
        () => { zona.innerHTML = casetaTrimisa(tip().toUpperCase(), corp.querySelector("#bl-an").value,
          "a intrat în coada de validare — cabinetul o validează și o depune."); aduInVedere(zona); });
    });
    corp.querySelector("#bl-xml").addEventListener("click", async () => {
      curataEroriCamp(corp); if (cereAlegerile(corp, ["#bl-tip"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
      try {
        const r = await api.get(`/tenants/${t.id}/${tip()}-xml?${par()}`);
        const b = new Blob([r.xml], { type: "application/xml" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(b);
        a.download = `${tip()}_${t.id}_${corp.querySelector("#bl-an").value}.xml`;
        a.click();
        if (r.avertismente && r.avertismente.length) {
          rez.innerHTML = `<p class="pf-intro">${r.avertismente.map(esc).join("<br>")}</p>`;
        }
      } catch (e) { arataMesaj(rez, e.mesaj || "eroare", "eroare"); }
    });
  }
}

export async function ecranStocuri(corp, nav, t) {
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  const cheie = "stocuri:" + t.id;
  // [lotul 13, 673] întors din fereastra NIR-ului (sau a unei acțiuni): luna lui și confirmarea (cea a salvării traversează redesenarea —
  // fosta `mesajNir`, R162 / C12c)
  let revenire = starePastrata(cheie);
  if (revenire && revenire.an && revenire.luna) { an = revenire.an; luna = revenire.luna; }
  const cerereNoua = ultimaCerere();   // [C103] luna schimbată în șir: numai NIR-urile lunii afișate ajung pe ecran

  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    const actuala = cerereNoua();
    let nirs = [];
    try { const r = await api.get(`/tenants/${t.id}/stocuri/nir?an=${an}&luna=${luna}`); if (!actuala()) return; nirs = r.nir || []; } catch { if (!actuala()) return; corp.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca NIR-urile.</p>`; return; }
    // [lotul 07.10 B, C10] metoda de stoc a firmei spune evaluarea: cantitativ-valoric = la cost (articol ales, fără preț de raft),
    // global-valoric = la preț de vânzare (preț de raft cerut). Nedeclarată: salvarea se refuză cu trimitere la Date firmă.
    // o citire căzută NU se ghicește (ar arăta formularul altei metode): ecranul spune că n-a putut citi și se oprește
    let metoda = null, artsNir = [];
    try {
      metoda = ((await api.get(`/tenants/${t.id}/firma-profil/date`)).profil || {}).metoda_stoc || null;
      if (!actuala()) return;
      if (metoda === "cantitativ_valoric") artsNir = (await api.get(`/tenants/${t.id}/stocuri/articole`)).articole || [];
      if (!actuala()) return;
    } catch (e) {
      if (!actuala()) return;
      corp.innerHTML = `<p class="ecran-nota">Nu s-a putut citi metoda de stoc sau articolele firmei: ${esc((e && e.mesaj) || "reîncearcă")}.</p>`;
      return;
    }
    const laCost = metoda === "cantitativ_valoric";
    // [decizii 07.10 pct.2] la global-valoric NIR-ul se leagă de factura primită a recepției (atunci scrie numai 371=378 și
    // 371=4428; costul vine din factură) sau e declarat explicit fără factură (NIR complet). Alegerea se cere: o factură deja
    // contată + un NIR complet ar încărca 371 de două ori.
    let facturiPrimite = [];
    const cuFactura = metoda === "global_valoric";   // alegerea există numai la global-valoric (metoda nedeclarată: serverul refuză)
    if (cuFactura) {
      try {
        facturiPrimite = ((await api.get(`/tenants/${t.id}/facturi?directie=primita`)).facturi || [])
          .filter((f) => (f.tip || "factura") === "factura" && !f.storno_din_id);
        if (!actuala()) return;
      } catch (e) {
        if (!actuala()) return;
        corp.innerHTML = `<p class="ecran-nota">Nu s-au putut citi facturile primite: ${esc((e && e.mesaj) || "reîncearcă")}.</p>`;
        return;
      }
    }
    // [retest 08.10 pct.5] NIR-ul respins și refăcut nu mai stă primul, cu card complet: se reduce la o linie, lângă cel valabil
    const inlocuite = {};
    nirs.filter((n) => n.inlocuit_de).forEach((n) => { (inlocuite[n.inlocuit_de.id] = inlocuite[n.inlocuit_de.id] || []).push(n); });
    const liniaInlocuit = (v) => `<div class="pf-frand-sub nir-inlocuit" style="margin:-4px 0 10px 14px">NIR ${esc(v.numar)} din ${dataRo(v.data)} · Respins · înlocuit de NIR nr ${esc(v.inlocuit_de.numar)} din ${dataRo(v.inlocuit_de.data)} <button type="button" class="btn-link nir-deschide" data-nir="${v.id}" data-numar="${esc(v.numar)}">Deschide →</button></div>`;
    const randuri = !nirs.length
      ? `<div class="stare-goala">Niciun NIR \u00een luna asta.</div>`
      : nirs.filter((n) => !(n.inlocuit_de && nirs.some((x) => x.id === n.inlocuit_de.id))).map((n) => `
        <div class="pf-frand">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">NIR ${esc(n.numar)} \u00b7 ${dataRo(n.data)} \u00b7 ${esc(n.furnizor || "")}</div>
            <div class="pf-frand-sub">${n.metoda_stoc === "cantitativ_valoric" ? `la cost ${bani(n.cost_total)} lei` : `cost ${bani(n.cost_total)} \u00b7 adaos ${bani(n.adaos_total)} \u00b7 TVA neex. ${bani(n.tva_neexigibila)} \u00b7 raft ${bani(n.valoare_vanzare)} lei`}</div>
            ${n.respins ? `<span class="caseta-atentie" style="display:block"><span class="ca-mesaj">Respins la validare: ${esc(motivInFraza(n.respins.motiv_respingere))}${n.refacut_in ? ` Refăcut în NIR-ul ${esc(n.refacut_in)}.` : (n.metoda_stoc === "cantitativ_valoric" ? " Intrarea lui în stoc a fost stornată." : "")}</span></span>` : ""}
            <button type="button" class="btn-link nir-deschide" data-nir="${n.id}" data-numar="${esc(n.numar)}">Deschide NIR-ul: articolele și notele →</button>
            ${butonRand("buton-secundar nir-reface", `data-nir="${n.id}" data-actiune="POST /tenants/{tenant_id}/stocuri/nir"`, "Refă NIR-ul",   // [lotul 13, 675]
              n.refacut_in ? `NIR-ul e refăcut deja, în NIR-ul ${n.refacut_in}.` : n.respins ? null : "NIR-ul nu e respins la validare: n-are ce reface.")}
          </div>
        </div>${(inlocuite[n.id] || []).map(liniaInlocuit).join("")}`).join("");
    // [05.10.2026, comanda Costin pct.10] „ecranul se deschide cu situația stocului (articol, UM, cantitate, CMP, valoare),
    // formularele (NIR, mișcări, coduri, nivel minim) stau sub ea, la cerere”.
    // [lotul 11, decizia Costin 10.3, verbatim în DECIZII „Comanda 10.3” pct.4: „Totalurile și rezumatul fix, mesajele lângă buton […]:
    // da, reorganizezi ecranele”] luna, „Descarcă gestiunea lunii” și zona lor de mesaj stăteau SUB situația stocului (deci mesajul
    // descărcării apărea la capătul tabelului, departe de antet); acum sunt rezumatul lipit sus, iar situația rămâne primul tabel, deasupra
    // formularelor (decizia din 05.10.2026 pct.10). Totalul valorii stocului (`tfoot`) rămâne jos, în vedere (DS cap.9 v2.100).
    corp.innerHTML = `
      <div class="rezumat-fix" id="s-rezumat">
      <h2 class="pf-titlu">Stocuri ${semnAjutor("F089")}</h2>
      <p class="pf-intro">Luna ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")}
        <button class="buton-secundar" id="s-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="buton-secundar" id="s-next">luna \u2192</button>
        <button class="buton-primar" id="s-desc" data-genereaza-nota data-actiune="POST /tenants/{tenant_id}/stocuri/descarcare" style="margin-left:12px"${lunaNeincheiata(an, luna) ? ' disabled aria-describedby="s-desc-motiv"' : ""}>Descarc\u0103 gestiunea lunii</button></p>
      ${lunaNeincheiata(an, luna) ? `<p class="tip-micut" id="s-desc-motiv">${esc(MOTIV_DESCARCARE_LUNA_IN_CURS)}</p>` : ""}
      <div id="s-mesaj"></div>
      </div>
      <div id="s-situatie"><p class="ecran-nota">Se încarcă situația stocului...</p></div>
      <p><button class="buton-secundar" id="sn-toggle" data-actiune="POST /tenants/{tenant_id}/stocuri/nir">+ NIR nou</button>
         <button class="buton-secundar" id="cv-toggle" style="margin-left:6px">Mișcări, fișe de magazie, coduri, nivel minim</button>
         <button class="buton-secundar" id="s-borderou" data-fara-actiune="deschide ecranul borderoului; generarea de acolo poartă acțiunea" style="margin-left:6px">Borderou de achiziție</button></p>
      <h3 class="pf-subtitlu">NIR-urile lunii</h3>
      <div class="pf-lista">${randuri}</div>`;
    const zonaM = corp.querySelector("#s-mesaj");
    if (revenire && revenire.mesaj) { if (typeof revenire.mesaj === "function") revenire.mesaj(zonaM); else arataMesaj(zonaM, revenire.mesaj, "ok"); }
    revenire = null;
    // [lotul 13, 673] „+ NIR nou” și „Mișcări, fișe de magazie…” deschid fiecare fereastra lor, nu o zonă din pagina Stocurilor
    const ctxNir = { cheie, laCost, cuFactura, facturiPrimite, artsNir };
    const deschideNir = (refacere, liniiNir) => deschideActiunea(nav, cheie, { an, luna }, refacere ? "Refaci NIR-ul " + refacere.numar : "NIR nou",
      (c2) => ecranNirNou(c2, nav, t, { ...ctxNir, refacere, liniiNir }));
    corp.querySelector("#sn-toggle").addEventListener("click", () => deschideNir(null, null));
    corp.querySelector("#cv-toggle").addEventListener("click", () =>
      deschideActiunea(nav, cheie, { an, luna }, "Mișcări, fișe de magazie, coduri, nivel minim", (c2) => ecranMiscariStoc(c2, nav, t)));
    // [lotul 11, comanda Costin 11.1 pct.23] „butonul borderoului stă în «TVA regimuri speciale» cu nume tehnic”: borderoul de achiziție stă
    // unde se caută achizițiile, lângă NIR, cu numele documentului (OMFP 2634/2015, cod 14-4-13)
    corp.querySelector("#s-borderou").addEventListener("click", () => nav.mergi("Borderou de achiziție", (c2) => ecranBorderou(c2, nav, t)));
    corp.querySelector("#s-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#s-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    // [lotul 07.10 B, C11d] un NIR salvat se deschide: articolele și notele lui, cu starea fiecăreia
    corp.querySelectorAll(".nir-deschide").forEach((b) => b.addEventListener("click", () =>
      nav.mergi("NIR " + b.dataset.numar, (c2) => ecranNir(c2, t, Number(b.dataset.nir)))));
    // [retest 07.10 R1] „Refă NIR-ul”: formularul pornește cu antetul și articolele NIR-ului respins
    corp.querySelectorAll(".nir-reface").forEach((b) => b.addEventListener("click", async () => {
      const actuala = cerereNoua();   // [C103] același contor cu ecranul: „Refă” pe alt NIR sau luna schimbată între timp câștigă
      try {
        const d = await api.get(`/tenants/${t.id}/stocuri/nir/${b.dataset.nir}`);
        if (!actuala()) return;
        const n = d.nir || {};
        const refacere = { id: n.id, numar: n.numar, data: n.data, furnizor: n.furnizor, cui: n.cui, motiv: (n.respins || {}).motiv_respingere };
        // [retest 08.10 pct.4] valorile se arată ca numere, nu cu zecimalele coloanei (10, nu 10,000; 55,00, nu 55,0000), iar
        // articolul unui NIR făcut fără articol (logica veche) se DEDUCE din denumire — numai la potrivire unică, vizibil,
        // schimbabil (DS cap.17 v2.79); fără potrivire unică rămâne „— alege articolul —”
        const _nr = (x) => (x === "" || x == null || !Number.isFinite(Number(x))) ? "" : String(Number(x));
        const _bani = (x) => { const v = Number(x); return (x === "" || x == null || !Number.isFinite(v)) ? "" : (Math.round(v * 100) / 100 === v ? v.toFixed(2) : String(v)); };
        const _cheie = (x) => String(x || "").trim().replace(/\s+/g, " ").toLowerCase();
        const _dedus = (den) => { const g = artsNir.filter((a) => _cheie(a.denumire) === _cheie(den)); return g.length === 1 ? String(g[0].id) : ""; };
        const liniiNir = (d.linii || []).map((l) => ({
          denumire: l.denumire || "", cantitate: _nr(l.cantitate), pret_achizitie: _bani(l.pret_achizitie),
          pret_vanzare: _bani(l.pret_vanzare), cota_tva: l.cota_tva == null ? "" : Number(l.cota_tva),
          articol_id: l.articol_id ? String(l.articol_id) : (laCost ? _dedus(l.denumire) : ""), articol_nou: false }));
        deschideNir(refacere, liniiNir.length ? liniiNir : [{}]);   // [lotul 13, 673] formularul NIR-ului respins, în fereastra lui
      } catch (e) { if (!actuala()) return; arataMesaj(zonaM, (e && e.mesaj) || "NIR-ul nu s-a putut încărca.", "eroare"); }
    }));

    corp.querySelector("#s-desc").addEventListener("click", () => {
      const bD = corp.querySelector("#s-desc");
      confirmaCaseta(bD.parentElement || bD, `Descarci gestiunea pe ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")}? Se calculează din notele validate.`, async () => {  // audit_cab_lot2_v1
      try {
        const r = await api.post(`/tenants/${t.id}/stocuri/descarcare?an=${an}&luna=${luna}`, {});
        if (r.mesaj) arataMesaj(zonaM, r.mesaj, "info");  // mesaj de stare = arataMesaj (cap.6), nu clasa ad-hoc mig-gol
        // [8c] confirmarea pe drumul unic: conturile notelor desc\u0103rc\u0103rii (citite din jurnal dup\u0103 id-uri), butonul inactiv cu motivul
        else dupaGenerare(zonaM, bD, { titlu: `Desc\u0103rcarea gestiunii: K=${r.k} \u00b7 CMV ${r.cmv} \u00b7 adaos ${r.adaos} \u00b7 TVA ${r.tva} \u00b7 total 371: ${bani(r.total_371)} lei \u00b7${cate(r.inregistrari.length, "notă " + stareNota(r), "note " + stareNota(r, true))}`,
          note: await noteGenerate(t.id, r.inregistrari, dataIso(new Date(an, luna, 0))) });
      } catch (e) { arataMesaj(zonaM, e.mesaj || "eroare", "eroare"); }
      }, { textOk: "Descarcă gestiunea" });
    });
    incarcaSituatiaStocului(corp, t);   // [05.10.2026, pct.10] situația stocului, primul tabel al ecranului
  };
  // [lotul 13, 673] Stocuri păstrate (omul scrisese în căutare) se redesenează ele la închiderea ferestrei NIR-ului / a mișcărilor
  corp.addEventListener("nav:revenire", () => {
    revenire = starePastrata(cheie);
    if (!revenire) return;
    if (revenire.an && revenire.luna) { an = revenire.an; luna = revenire.luna; }
    deseneaza();
  });
  deseneaza();
}

// [lotul 13, 673] „Mișcări, fișe de magazie, coduri, nivel minim” — secțiunea stocului cantitativ-valoric (`sectiuneaCV`) în fereastra ei;
// acțiunile ei (inventarul, transferul, reclasificarea, inventarul pe mobil) se deschid la rândul lor peste ea, iar la întoarcere
// confirmarea lor stă aici, în zona de mesaj a ferestrei
function ecranMiscariStoc(corp, nav, t) {
  const cheie = "stocuri:" + t.id;
  corp.innerHTML = `<div class="rezumat-fix"><h2 class="pf-titlu">Mișcări, fișe de magazie, coduri, nivel minim</h2><div id="s-mesaj"></div></div>
    <div id="cv-zona"></div>`;
  const zonaM = corp.querySelector("#s-mesaj");
  const arata = () => {
    const rev = starePastrata(cheie);
    if (rev && rev.mesaj) { if (typeof rev.mesaj === "function") rev.mesaj(zonaM); else arataMesaj(zonaM, rev.mesaj, "ok"); }
    return !!rev;
  };
  arata();
  corp.addEventListener("nav:revenire", () => { if (arata()) sectiuneaCV(corp, t, zonaM, nav); });
  sectiuneaCV(corp, t, zonaM, nav);
}

// [lotul 13, deficiența 673 — clasă, comanda Costin 13.1: „Acțiunile din interiorul ferestrelor își deschid conținutul în pagină [...]
// deschide o fereastră nouă”] „+ NIR nou” și „Refă NIR-ul”: formularul NIR în fereastra lui (DS cap.2a v2.104), cu tot ce avea în Stocuri
// (articolele, factura sosită / legată, costul accesoriu, „Verifică” la ANAF, refacerea NIR-ului respins); după salvare fereastra se
// închide, iar Stocuri se redesenează pe luna NIR-ului, cu confirmarea. `ctx`: {cheie, laCost, cuFactura, facturiPrimite, artsNir,
// refacere, liniiNir} — citite de Stocuri la desenare.
function ecranNirNou(corp, nav, t, ctx) {
  const { laCost, cuFactura, facturiPrimite, artsNir, refacere } = ctx;
  let liniiNir = ctx.liniiNir && ctx.liniiNir.length ? ctx.liniiNir : [{}];
  const linieNouaNir = () => ({ denumire: "", cantitate: "", pret_achizitie: "", pret_vanzare: "", cota_tva: "", articol_id: "", articol_nou: false });   // [R29] fără cotă implicită: serverul refuză lipsa (main.py:798), iar ecranul nu răspunde în locul contabilului
  const _vn = (x) => (x === "" || x == null) ? "" : esc(String(x));
  // randeaza O linie NIR DIN MODEL, id-uri pozitionale nir-l{i}-* (cap.24: id derivat din pozitie -> backendul
  // leaga eroarea de camp, cap.6); buton de stergere pe fiecare rand (regula 3).
  function randLinieNir(i) {
    const l = liniiNir[i];
    // [lotul 07.10 B, C11c] la cost (cantitativ-valoric) articolul se ALEGE din listă sau se creează explicit („+ articol nou”),
    // niciodată tacit după denumire — „Marfa  A” nu devine un al doilea articol lângă „Marfa A”
    const alegereArt = laCost ? `<input type="text" class="camp-input" id="nir-l${i}-articol-cauta" placeholder="Caută articolul în stoc…" aria-label="Caută articolul" autocomplete="off" style="flex:1;min-width:150px">
      <select class="camp-input" id="nir-l${i}-articol" aria-label="Articol" style="flex:2;min-width:180px">
        <option value=""${!l.articol_id && !l.articol_nou ? " selected" : ""} data-alege disabled hidden>— alege articolul —</option>
        ${artsNir.map((a) => `<option value="${a.id}"${String(l.articol_id) === String(a.id) ? " selected" : ""}>${esc(a.denumire)}</option>`).join("")}
        <option value="nou"${l.articol_nou ? " selected" : ""}>+ articol nou…</option></select>` : "";
    const denumire = (!laCost || l.articol_nou) ? `<input type="text" class="camp-input" id="nir-l${i}-denumire" placeholder="${laCost ? "denumirea articolului nou" : "denumire"}" aria-label="Denumire" value="${_vn(l.denumire)}" style="flex:2;min-width:160px">` : "";
    return `<div class="nir-linie" data-idx="${i}" style="display:flex;gap:8px;margin-bottom:6px;flex-wrap:wrap">
      ${alegereArt}${denumire}
      <input type="number" step="0.001" class="camp-input" id="nir-l${i}-cantitate" placeholder="cant." aria-label="Cantitate" value="${_vn(l.cantitate)}" style="width:90px">
      <input type="number" step="0.0001" class="camp-input" id="nir-l${i}-pret_achizitie" placeholder="preț achiziție" aria-label="Preț achiziție" value="${_vn(l.pret_achizitie)}" style="width:120px">
      ${laCost ? "" : `<input type="number" step="0.0001" class="camp-input" id="nir-l${i}-pret_vanzare" placeholder="preț raft (cu TVA)" aria-label="Preț raft cu TVA" value="${_vn(l.pret_vanzare)}" style="width:140px">`}
      <select class="camp-input" id="nir-l${i}-cota_tva" data-butoane aria-label="Cota TVA" style="width:90px"><option value=""${!l.cota_tva ? " selected" : ""}>alege</option>${[21, 11].map((c) => `<option value="${c}"${String(l.cota_tva) === String(c) ? " selected" : ""}>${c}%</option>`).join("")}</select>
      <button type="button" class="buton-sters nir-l-sterge" data-idx="${i}" title="Șterge">×</button>
    </div>`;
  }
  corp.innerHTML = `
    <h2 class="pf-titlu">${refacere ? "Refaci NIR-ul " + esc(refacere.numar) : "NIR nou"}</h2>
        ${refacere ? `<div class="caseta-info"><span class="ci-mesaj">Refaci NIR-ul ${esc(refacere.numar)}, respins la validare (${esc(refacere.motiv || "fără motiv")}). La salvare, ciornele lui respinse se scot; motivul rămâne în coadă.</span></div>` : ""}
        <div class="camp-eticheta">NIR: num\u0103r \u00b7 dat\u0103 \u00b7 furnizor \u00b7 CUI</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
          <input type="text" id="sn-numar" class="camp-input" placeholder="număr NIR" aria-label="Num\u0103r NIR" style="width:120px" value="${refacere ? esc(refacere.numar) : ""}">
          <input type="date" id="sn-data" aria-label="Data intrare stoc" class="camp-input" value="${refacere ? esc(String(refacere.data).slice(0, 10)) : dataIso()}">
          <input type="text" id="sn-furn" class="camp-input" placeholder="furnizor" aria-label="Furnizor" style="flex:1;min-width:160px" value="${refacere ? esc(refacere.furnizor || "") : ""}">
          <input type="text" id="sn-cui" class="camp-input" placeholder="CUI" aria-label="CUI furnizor" style="width:120px" value="${refacere ? esc(refacere.cui || "") : ""}">
          <button type="button" class="buton-secundar" id="sn-verifica" data-fara-actiune="citire ANAF (completează furnizorul în formular); salvarea NIR-ului poartă acțiunea">Verifică</button>
        </div>
        <div class="em-cui-stare" id="sn-cui-stare"></div>
        ${!cuFactura ? "" : `<div class="camp-eticheta">Factura primită a recepției — legat, NIR-ul scrie numai adaosul și TVA neexigibilă (costul vine din factură)</div>
        <div style="margin-bottom:8px"><select id="sn-factura" class="camp-input" aria-label="Factura primită a recepției" style="min-width:280px;max-width:100%">
          ${ALEGE}
          <option value="fara">fără factură — NIR complet (cost, adaos, TVA neexigibilă)</option>
          ${facturiPrimite.map((f) => `<option value="${f.id}">factura ${esc(numarCuSerie(f.serie, f.numar))} din ${dataRo(f.data_emitere)} · ${esc(f.tert_nume || "")} · ${bani(f.total)} ${esc(f.moneda || "RON")}</option>`).join("")}
        </select></div>`}
        ${cuFactura ? "" : `<label class="camp" style="display:block;margin-bottom:8px;max-width:420px"><span class="camp-eticheta">Factura furnizorului a sosit?<span class="oblig">*</span></span>
          ${selectDaNu('id="sn-factura-sosita"', null, "Factura furnizorului a sosit")}
          <span class="camp-ajutor">Nu = factură nesosită: datoria intră pe 408, iar TVA-ul stă neexigibil până la factură. ${laCost ? "Da = factura aduce ea marfa în stoc (Facturi primite), fără NIR." : "Da = alege factura, ca NIR-ul să se lege de ea."}</span></label>`}
        <div class="camp-eticheta">${laCost ? "Articole: articolul (din listă sau nou) \u00b7 cantitate \u00b7 pre\u021b achizi\u021bie \u00b7 cot\u0103 TVA — marfa intră la cost (stoc cantitativ-valoric, CMP)" : "Articole: denumire \u00b7 cantitate \u00b7 pre\u021b achizi\u021bie \u00b7 pre\u021b raft (cu TVA) \u00b7 cot\u0103 TVA — marfa intră la preț de vânzare (global-valoric)"}</div>
        <div id="sn-linii">${liniiNir.map((_, i) => randLinieNir(i)).join("")}</div>
        <div class="camp-eticheta">Cost accesoriu (landed cost) — se repartizează proporțional în costul de achiziție (OMFP 1802/2014). Contul de credit se confirmă de contabil.</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
          <input type="number" step="0.01" id="sn-transport" class="camp-input" placeholder="transport" aria-label="Transport" style="width:110px">
          <select id="sn-transport-cota" class="camp-input" data-butoane aria-label="Cota TVA a transportului" style="width:130px">${ALEGE}${[21, 11, 0].map((c) => `<option value="${c}">TVA transport ${c}%</option>`).join("")}</select>
          <input type="text" id="sn-cont-transport" class="camp-input" value="" placeholder="cont furnizor (401 / 408)" aria-label="Cont credit transport" style="width:170px">
          <input type="number" step="0.01" id="sn-taxe" class="camp-input" placeholder="taxe" aria-label="Taxe" style="width:110px">
          <input type="text" id="sn-cont-taxe" class="camp-input" placeholder="cont taxe (ex. 446)" aria-label="Cont credit taxe" style="width:150px">   <!-- [lotul 13, 504] gol: contul îl scrie contabilul, nu vine ales -->
        </div>
        <p><button class="buton-secundar" id="sn-plus" data-fara-actiune="rând în formular; salvarea formularului poartă acțiunea">+ articol</button></p>
        <div class="bara-fixa"><p style="margin-top:10px"><button class="buton-primar" id="sn-salveaza" data-actiune="POST /tenants/{tenant_id}/stocuri/nir">Salveaz\u0103 NIR (note ciorne)</button>
          <button type="button" class="buton-secundar" data-renunta data-fara-actiune="închide fereastra, fără scriere" style="margin-left:6px">Renunță</button></p>
        <div id="s-mesaj"></div></div>
`;
  legaRenunta(corp, nav);
  const zonaM = corp.querySelector("#s-mesaj");
  const zonaL = corp.querySelector("#sn-linii");
  // model NIR: input-urile scriu in liniiNir (fara re-randare la tastare); add/delete re-randeaza integral
  // #sn-linii din model (cap.24 regula 1); fara filtrare la trimitere (regula 2); erori per-linie de la backend
  // langa camp (cap.6 mecanism A). Fetch-ul cotei nu exista aici (cota = select).
  function legaLinieNir(i) {
    const l = liniiNir[i];
    const g = (suf) => zonaL.querySelector("#nir-l" + i + "-" + suf);
    const den = g("denumire"), cant = g("cantitate"), pa = g("pret_achizitie"), pv = g("pret_vanzare"), tva = g("cota_tva"), art = g("articol");
    if (art && g("articol-cauta")) cautaInLista(g("articol-cauta"), art);   // [488]
    const del = zonaL.querySelector('.nir-l-sterge[data-idx="' + i + '"]');
    if (art) art.addEventListener("change", () => {
      l.articol_nou = art.value === "nou"; l.articol_id = l.articol_nou ? "" : art.value;
      deseneazaLiniiNir();   // „articol nou” arată câmpul de denumire
    });
    if (den) den.addEventListener("input", () => { l.denumire = den.value.trim(); });
    cant.addEventListener("input", () => { l.cantitate = cant.value; });
    pa.addEventListener("input", () => { l.pret_achizitie = pa.value; });
    if (pv) pv.addEventListener("input", () => { l.pret_vanzare = pv.value; });
    tva.addEventListener("change", () => { l.cota_tva = parseFloat(tva.value); });
    del.addEventListener("click", () => { const p = liniiNir.indexOf(l); if (p >= 0) liniiNir.splice(p, 1); deseneazaLiniiNir(); });
  }
  function deseneazaLiniiNir() {
    zonaL.innerHTML = liniiNir.map((_, i) => randLinieNir(i)).join("");
    liniiNir.forEach((_, i) => legaLinieNir(i));
  }
  liniiNir.forEach((_, i) => legaLinieNir(i));   // leaga randurile deja randate in corp.innerHTML
  corp.querySelector("#sn-plus").addEventListener("click", () => { liniiNir.push(linieNouaNir()); deseneazaLiniiNir(); });
  corp.querySelector("#sn-salveaza").addEventListener("click", async () => {
    curataEroriCamp(corp);
    // [FAPT_FISCAL_NECERUT] legat sau nu, se alege; [399] factura sosită sau nu și cota TVA a transportului: alese de om, nu presupuse
    // (serverul le cere și el) — toate deodată
    let alegereLipsa = false;
    if (cuFactura && cereAlegerile(corp, ["#sn-factura"])) alegereLipsa = true;
    if (!cuFactura && cereAlegerile(corp, ["#sn-factura-sosita"])) alegereLipsa = true;
    if ((parseFloat(corp.querySelector("#sn-transport").value) || 0) > 0 && cereAlegerile(corp, ["#sn-transport-cota"])) alegereLipsa = true;
    // [lotul 13, 504] contul de credit al taxelor nu mai vine precompletat (446): cu taxe scrise, contul se cere lângă câmp
    if ((parseFloat(corp.querySelector("#sn-taxe").value) || 0) > 0 && !corp.querySelector("#sn-cont-taxe").value.trim()) {
      eroareCamp(corp, "sn-cont-taxe", "Scrie contul de credit al taxelor (de obicei 446 „Alte impozite, taxe și vărsăminte asimilate”).");
      alegereLipsa = true;
    }
    if (alegereLipsa) {
      // [lotul 11, 440] alegerile lipsă opresc trimiterea: câmpurile goale ale articolelor se marchează ODATĂ cu ele (serverul le-ar
      // spune abia la apăsarea următoare); aceleași texte ca serverul (`stocuri_api._nir_campuri_lipsa`), care rămâne autoritar
      cereCompletate(corp, liniiNir.flatMap((_, i) => [
        ...(laCost ? [] : [{ id: `nir-l${i}-denumire`, mesaj: `Scrie denumirea articolului ${i + 1} sau alege-l din stoc.` }]),
        { id: `nir-l${i}-cantitate`, mesaj: `Articolul ${i + 1}: scrie cantitatea, un număr mai mare decât zero.` },
        { id: `nir-l${i}-pret_achizitie`, mesaj: `Articolul ${i + 1}: scrie prețul de achiziție, un număr mai mare decât zero.` },
        ...(laCost ? [] : [{ id: `nir-l${i}-pret_vanzare`, mesaj: `Articolul ${i + 1}: scrie prețul de raft (cu TVA), un număr mai mare decât zero.` }]),
      ]));
      return;
    }
    const fSel = cuFactura ? corp.querySelector("#sn-factura").value : "";
    // NU se filtreaza randuri (cap.24 regula 2): lista trimisa = lista randata. Un articol incomplet se
    // valideaza pe backend si se raporteaza langa campul lui, nu dispare tacit.
    // [lotul 07.10 B, C11a] un câmp gol pleacă GOL (null), nu 0: prețul pe care nu l-a scris nimeni nu e „0” — serverul îl cere
    // lângă câmp. La cost, prețul de raft nu există; articolul pleacă ales (`articol_id`) sau nou (`articol_nou`).
    const nr = (x) => (x === "" || x == null || Number.isNaN(parseFloat(x))) ? null : parseFloat(x);
    const linii = liniiNir.map((l) => ({
      denumire: l.denumire, cantitate: nr(l.cantitate), pret_achizitie: nr(l.pret_achizitie),
      ...(laCost ? { articol_id: l.articol_id ? Number(l.articol_id) : null, articol_nou: !!l.articol_nou } : { pret_vanzare: nr(l.pret_vanzare) }),
      cota_tva: (l.cota_tva === "" || l.cota_tva == null) ? null : Number(l.cota_tva),   // [R29]
    }));
    const bSal = corp.querySelector("#sn-salveaza");
    try {
      const corpNir = {
        numar: corp.querySelector("#sn-numar").value.trim(),
        data: corp.querySelector("#sn-data").value,
        furnizor: corp.querySelector("#sn-furn").value || null,
        cui: corp.querySelector("#sn-cui").value || null,
        transport: parseFloat(corp.querySelector("#sn-transport").value) || 0,
        taxe: parseFloat(corp.querySelector("#sn-taxe").value) || 0,
        cont_transport: corp.querySelector("#sn-cont-transport").value.trim() || null,   // [398] gol = contul furnizorului mărfii
        cota_tva_transport: corp.querySelector("#sn-transport-cota").value === "" ? null : Number(corp.querySelector("#sn-transport-cota").value),   // [399]
        // [399] factura sosită sau nu: aleasă de om (la NIR-ul legat, factura aleasă o spune singură)
        factura_sosita: cuFactura ? (fSel === "fara" ? false : null) : daNu(corp.querySelector("#sn-factura-sosita")),
        cont_taxe: corp.querySelector("#sn-cont-taxe").value.trim() || null,
        ...(fSel && fSel !== "fara" ? { factura_id: Number(fSel) } : {}),
        ...(refacere ? { refacut_din_id: refacere.id } : {}),
        linii,
      };
      let r = await api.post(`/tenants/${t.id}/stocuri/nir`, corpNir);
      if (r && r.cod === "NESCHIMBATA") {   // [S3] NIR-ul refăcut identic cu cel respins: confirmare explicită
        await new Promise((gata) => confirmaCaseta(bSal.parentElement || bSal, r.mesaj, async () => {
          r = await api.post(`/tenants/${t.id}/stocuri/nir`, { ...corpNir, confirma_neschimbata: true }); gata();
        }, { textOk: "Retrimite fără schimbări" }));
      }
      const acc = (parseFloat(r.transport) || 0) + (parseFloat(r.taxe) || 0);
      const mesajNir = r.metoda === "cantitativ_valoric"
        ? `<div class="caseta-info"><span class="ci-mesaj">NIR salvat · ${cate(r.inregistrari.length, "notă " + stareNota(r), "note " + stareNota(r, true))}, la cost ${bani(r.cost_total)} lei${acc > 0 ? " (din care accesoriu " + bani(acc) + ")" : ""}. Intrarea e în fișa de magazie: stocul de mai sus o arată deja. ${pasNota(r, r.inregistrari.length > 1)}</span></div>`
        : r.factura_id
        ? `<div class="caseta-info"><span class="ci-mesaj">NIR salvat, legat de factura ${esc(r.factura_ref || "")} · ${cate(r.inregistrari.length, "notă " + stareNota(r), "note " + stareNota(r, true))}: adaos ${bani(r.adaos_total)}, TVA neex. ${bani(r.tva_neexigibila)} lei. Costul (${bani(r.cost_total)} lei) e în factură.</span></div>`
        : `<div class="caseta-info"><span class="ci-mesaj">NIR salvat · ${cate(r.inregistrari.length, "notă " + stareNota(r), "note " + stareNota(r, true))} (cost ${bani(r.cost_total)}${acc > 0 ? " din care accesoriu " + bani(acc) : ""}, adaos ${bani(r.adaos_total)}, TVA neex. ${bani(r.tva_neexigibila)} lei).</span></div>`;
      // [lotul 13, 673] fereastra NIR-ului se închide; Stocuri se redesenează pe luna NIR-ului, cu confirmarea (situația stocului îl arată)
      const dz = new Date(corpNir.data + "T00:00:00");
      inchideCuConfirmarea(nav, ctx.cheie, (zonaS) => { zonaS.innerHTML = mesajNir; }, { an: dz.getFullYear(), luna: dz.getMonth() + 1 });
    } catch (e) {
      curataEroriCamp(corp);
      // [lotul 11, 440] fiecare eroare a serverului lângă câmpul ei (id-urile NIR-ului: `sn-…`, `nir-l<i>-…`); textul refuzului sub
      // formular numai pentru ce n-are câmp pe ecran (înainte: mereu, deci de două ori)
      arataRefuzul(corp, e, zonaM);
    }
  });

  // [lotul 07.10 B, C11b] furnizorul din ANAF, ca la factură („Verifică”): CUI -> denumire, cu plătitor / neplătitor de TVA
  // [303, comanda 7.2] ca la factură: butonul e blocat și spune „Se verifică…” cât așteaptă; ANAF căzut se spune cu mesajul serverului
  const bSn = corp.querySelector("#sn-verifica");
  // [lotul 12, 459.1] denumirea furnizorului adusă de la ANAF dispare când se schimbă CUI-ul (cea scrisă de om rămâne)
  const anafSn = legaDateAnaf(corp.querySelector("#sn-cui"), [corp.querySelector("#sn-furn")], corp.querySelector("#sn-cui-stare"));
  bSn.addEventListener("click", async () => {
    const cui = corp.querySelector("#sn-cui").value.trim(), st = corp.querySelector("#sn-cui-stare");
    if (!cui) { eroareCamp(corp, "sn-cui", "Scrie CUI-ul furnizorului."); return; }
    if (bSn.disabled) return;
    const textB = bSn.textContent;
    bSn.disabled = true; bSn.setAttribute("aria-busy", "true"); bSn.textContent = "Se verifică…";
    st.textContent = "se verifică la ANAF…"; st.className = "em-cui-stare";
    try {
      const r = await api.get(`/tenants/${t.id}/verifica-cui/${encodeURIComponent(cui)}`);
      if (r && r.gasit) {
        anafSn.pune([r.denumire], { suprascrie: true });   // „Verifică” e cererea explicită a omului
        st.innerHTML = `<span class="em-cui-info">${esc(r.denumire || "")} · ${r.platitor_tva ? "plătitor TVA" : "neplătitor TVA"}</span>`;
        // [lotul 11, 444] fișa furnizorului cu acest CUI are alt nume decât ANAF: se spune și se propune actualizarea
        propuneNumeAnaf(st, r, t.id, { fel: "furnizori", pre: "sn" });
      } else { st.textContent = "CUI negăsit la ANAF"; st.className = "em-cui-stare em-cui-rau"; }
    } catch (e) { st.textContent = (e && e.mesaj) || "Verificarea nu s-a putut face — reîncearcă."; st.className = "em-cui-stare em-cui-rau pe-randuri"; }
    finally { bSn.disabled = false; bSn.removeAttribute("aria-busy"); bSn.textContent = textB; }
  });
}

// [lotul 07.10 B, C11d] NIR-ul salvat: antetul, articolele și notele lui, fiecare cu starea la validare.
async function ecranNir(corp, t, nirId) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă NIR-ul…</p>`;
  let d;
  try { d = await api.get(`/tenants/${t.id}/stocuri/nir/${nirId}`); } catch (e) { corp.innerHTML = `<p class="ecran-nota pe-randuri">${esc((e && e.mesaj) || "NIR-ul nu s-a putut încărca.")}</p>`; return; }
  const n = d.nir, laCost = n.metoda_stoc === "cantitativ_valoric";
  const stare = (v) => !v ? "ciornă (netrimisă la validare)" : v.stare_coada === "la_senior" ? "la validare în cabinet"
    : v.stare_coada === "aprobata" ? "validată" : v.stare_coada === "respinsa" ? "respinsă: " + (v.motiv_respingere || "fără motiv") : v.stare_coada;
  // [lotul 10, 421 / 424 — rezumatul fix, DS cap.9 v2.97 pct.5] antetul NIR-ului (numărul, data, furnizorul) rămâne sus; [lotul 12, 621] caseta
  // respingerii stă sub el, nu lipită (DS cap.9 v2.102 „Rezumatul nu mănâncă tabelul”)
  corp.innerHTML = `
    <div class="rezumat-fix">
    <h2 class="pf-titlu">NIR ${esc(n.numar)} · ${dataRo(n.data)}</h2>
    <p class="pf-intro">${esc(n.furnizor || "furnizor nescris")}${n.cui ? " · CUI " + esc(n.cui) : ""} · ${laCost ? "la cost (cantitativ-valoric)" : "la preț de vânzare (global-valoric)"}${n.factura_id ? ` · legat de factura ${esc(n.factura_ref || "")} (costul e în factură)` : ""}</p>
    </div>
    ${n.respins ? `<div class="caseta-atentie"><div class="ca-mesaj">Respins la validare: ${esc(motivInFraza(n.respins.motiv_respingere))}${n.refacut_in ? ` Refăcut în NIR-ul ${esc(n.refacut_in)}.` : (laCost ? " Intrarea lui în stoc a fost stornată; NIR-ul se reface din lista NIR-urilor lunii." : " NIR-ul se reface din lista NIR-urilor lunii.")}</div></div>` : ""}
    <table class="fd-tabel" id="nir-detaliu-linii"><thead><tr><th>Articol</th><th>Cantitate</th><th>Preț achiziție</th>${laCost ? "" : "<th>Preț raft</th>"}<th>Cotă</th><th>Transport și taxe repartizate</th><th>Cost final</th><th>Cost unitar final</th></tr></thead>
      <tbody>${d.linii.map((l) => `<tr><td>${esc(l.denumire)}</td><td>${esc(cantitate(l.cantitate))}</td><td>${bani(l.pret_achizitie)}</td>${laCost ? "" : `<td>${bani(l.pret_vanzare)}</td>`}<td>${esc(String(Number(l.cota_tva)))}%</td><td>${bani(l.accesoriu)}</td><td>${bani(l.cost_final)}</td><td>${esc(pretUnitar(l.cost_unitar_final))}</td></tr>`).join("")}</tbody></table>
    <h3 class="pf-subtitlu">Notele NIR-ului</h3>
    <table class="fd-tabel"><thead><tr><th>Notă</th><th>Debit</th><th>Credit</th><th>Sumă</th><th>Stare</th></tr></thead>
      <tbody>${d.note.map((x) => `<tr><td>${esc(x.eticheta || "")}</td><td>${esc(x.cont_debit)}</td><td>${esc(x.cont_credit)}</td><td>${bani(x.suma)}</td><td>${esc(x.status === "validata" ? "validată" : stare(x.validare))}</td></tr>`).join("") || `<tr><td colspan="5">—</td></tr>`}</tbody></table>`;
}

// [deficiența 279] starea REALĂ a notei operațiunii, pe rând (nu presupusă: din coada de validare)
function stareNotaCasa(o, t) {
  // [368, decizia Costin 19.10.2026] la partidă simplă nota e internă (validată automat; evidența e registrul de încasări și plăți)
  if (o.nota_status === "validata") return t && t.regim_contabil === "simpla" ? "notă internă" : "notă validată";
  if (o.stare_coada === "la_senior") return "notă la validare în cabinet";
  if (o.stare_coada === "respinsa") return "notă respinsă la validare" + (o.motiv_respingere ? ": " + o.motiv_respingere : "");
  return "notă ciornă";
}

// [lotul 13, deficiența 673 — clasă, DS cap.2a v2.104] o acțiune dintr-o fereastră (dispoziția nouă, chitanța, legarea de factură, alegerea
// facturilor unei linii de extras) se deschide într-o FEREASTRĂ NOUĂ, nu într-o zonă a ferestrei de dedesubt. După reușită fereastra actului
// se închide, iar fereastra de dedesubt se redesenează cu confirmarea lui (și pe luna lui): starea trece prin `_revenireFereastra[cheie]`
// (cheia = ecranul + firma), ca `CONFIRMARI_SALARIAT` al statului de plată. Fereastra de dedesubt păstrată (omul scrisese în ea, pct.1b al
// navigatorului) nu se redesenează singură: ascultă `nav:revenire` și se redesenează ea.
const _revenireFereastra = {};
function deschideActiunea(nav, cheie, stare, titlu, randator) {
  _revenireFereastra[cheie] = { ...stare, mesaj: "" };
  nav.deschide(titlu, randator, { lat: "tabel" });
}
function inchideCuConfirmarea(nav, cheie, mesaj, stare = {}) {
  _revenireFereastra[cheie] = { ...(_revenireFereastra[cheie] || {}), ...stare, mesaj };
  nav.inapoi();
}
function starePastrata(cheie) {
  const s = _revenireFereastra[cheie];
  delete _revenireFereastra[cheie];
  return s || null;
}
// [lotul 13, 669] documentul deschis din ofertele Casei și Băncii: factura „F1A nr. 8 din 01.10.2026”, soldul preluat la migrare „Sold la
// 30.09.2026 (sold preluat la migrare)” — fără „din <data>” repetat după data din numele lui
// numărul documentului cu seria lui, pentru rândul listei (forma `numarCuSerie`)
const cuSerieSiNumar = (f) => ({ ...f, numar: numarCuSerie(f.serie, f.numar) });
const numeDocDeschis = (f, cuData = true) => f.preluata ? `${esc(f.numar)} <span class="tip-desc">(sold preluat la migrare)</span>`
  : `${esc(f.numar)}${cuData ? " din " + dataRo(f.data_emitere) : ""}`;
// [lotul 13, 675] butonul unei acțiuni a rândului: la locul lui, activ — sau inactiv cu motivul (`atributeInactiv`, DS cap.1 v2.104)
const butonRand = (cls, atribute, eticheta, motiv) => `<button type="button" class="${cls}" ${atribute}${motiv ? atributeInactiv(motiv) : ""}>${eticheta}</button>`;
// [lotul 13, 624] o explicație repetată (aceeași, pe mai multe rânduri) se spune O DATĂ, cu rândurile ei (ca `listaRefuzuri` din Import date)
function grupeazaMesaje(linii) {
  const g = new Map();
  linii.forEach(({ text, unde }) => { if (!g.has(text)) g.set(text, []); if (unde) g.get(text).push(unde); });
  return [...g.entries()].map(([text, unde]) => unde.length > 1 ? `${text} (${unde.join(", ")})` : (unde.length ? `${text} (${unde[0]})` : text));
}

// [casa] Registru de casa
// [lotul 13, comanda Costin 13.1, verbatim]
//   624: „Clasă: ecrane cu liste | Importuri, audit, casă, bancă la forma din 617/622; observații la clic; respinsele grupate; «Salvează
//        cota» iese din ecran”
//   673: „Acțiunile din interiorul ferestrelor își deschid conținutul în pagină, departe de locul apăsării [...] deschide o fereastră nouă”
//   675: „entitățile de același tip [...] au același set de butoane, în aceeași ordine; ce nu se aplică stă inactiv, cu motivul”
//   676: „Listele scurte (până la 6 opțiuni) nu sunt liste derulante [...] (ex. [...] Sursa Casa/Banca)”
// Registrul lunii e tabelul de note (DS cap.9 v2.102, `tabel_note.js`): un rând pe operațiune — data, documentul, partenerul și felul
// operațiunii, încasarea / plata, soldul, nota —, cu „Stornează” și „Șterge” pe rând; observațiile operațiunii (factura stinsă, avansul,
// chitanța, motivul respingerii) și „PDF chitanță”, „Leagă de factură”, cota chitanței fără cotă în detaliul care se deschide la clic. Un
// semn repetat se explică o dată, deasupra tabelului; notele respinse la validare stau grupate pe motiv. „+ Dispoziție nouă”, „+ Chitanță
// fără factură” și „Leagă de factură” deschid fiecare fereastra lor.
const CATEGORII_CASA = [
  ["incasare_client", "Încasare client (5311=4111)"],
  ["plata_furnizor", "Plată furnizor (401=5311)"],
  ["ridicare_banca", "Ridicare de la bancă (5311=581)"],
  ["depunere_banca", "Depunere la bancă (581=5311)"],
  ["avans_decontare", "Avans spre decontare (542=5311)"],
];
const EXPLICATII_CASA = {
  respinsa: { atentie: true, titlu: "Note respinse la validare",
    text: "corectezi operațiunea (o ștergi și o scrii din nou), iar nota nouă merge din nou la validare. Motivele:" },
  fara_chitanta: { atentie: false, titlu: "Încasare fără chitanță",
    text: "chitanța nu s-a emis în aplicație (încasare scrisă înainte ca aplicația s-o emită singură); nu se emite cu dată trecută." },
  alt_modul: { atentie: false, titlu: "Scrisă din alt ecran",
    text: "rândul vine din raportul Z, statul de plată sau Registrul jurnal: se corectează de acolo." },
  stornata: { atentie: false, titlu: "Stornată",
    text: "operațiunea validată e anulată de rândul ei de stornare (cu minus), care trece și el prin validare." },
};
const STARI_CASA = [["", "Toate operațiunile"], ["ciorna", "Note ciornă"], ["validata", "Note validate"], ["la_validare", "La validare în cabinet"],
  ["respinsa", "Respinse la validare"]];

// [675] motivul pentru care un buton al rândului de casă nu se aplică (null = se aplică)
function motiveCasa(o) {
  const altModul = "Rândul e scris din alt ecran (raportul Z, statul de plată, o notă din Registru jurnal): se corectează de acolo.";
  const laValidare = "Nota așteaptă validarea în cabinet: nu se modifică până nu e validată sau respinsă.";
  const m = {};
  if (o.alt_modul) { m.storno = m.sterge = m.leaga = altModul; m.pdf = "Rândul n-are chitanță emisă din Casă."; return m; }
  m.pdf = o.chitanta_id ? null : (o.tip === "plata" ? "La plată nu se emite chitanță." : "Operațiunea n-are chitanță emisă.");
  if (o.storno_de) {
    m.storno = "Rândul e chiar stornarea unei operațiuni.";
    m.sterge = "Stornarea rămâne în registru, ca operațiunea pe care o anulează.";
  } else if (o.stornata) {
    m.storno = m.sterge = "Operațiunea e stornată: rândul ei de stornare e în registru.";
  } else if (o.nota_status === "validata") {
    m.storno = null;
    m.sterge = "Nota e validată: operațiunea se stornează, nu se șterge.";
  } else if (o.stare_coada === "la_senior") {
    m.storno = m.sterge = laValidare;
  } else {
    m.storno = "Nota operațiunii nu e validată: operațiunea se șterge (stornarea e pentru nota validată).";
    m.sterge = null;
  }
  m.leaga = o.se_leaga && o.stare_coada !== "la_senior" ? null
    : !["incasare_client", "plata_furnizor"].includes(o.categorie) ? "Numai încasarea de la client și plata furnizorului se leagă de o factură."
    : o.factura ? `Operațiunea e legată de factura ${o.factura}.`
    : o.storno_de || o.stornata ? "Operațiunea stornată nu se mai leagă."
    : o.stare_coada === "la_senior" ? laValidare
    : o.nota_status === "validata" ? "Nota e validată: legătura cu factura se face înainte de validare."
    : o.categorie === "plata_furnizor" && o.avans ? "Avansul acordat furnizorului se compensează la factura finală, nu se leagă."
    : "Operațiunea nu se poate lega de o factură.";
  return m;
}

async function ecranCasa(corp, nav, t) {
  const cheie = "casa:" + t.id;
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  // [R162] mesajul de reusita TRAVERSEAZA re-randarea — v. antetul reparatiei; [673] și închiderea ferestrei unei acțiuni (luna ei)
  let mesajSucces = "";
  const preia = () => {
    const st = starePastrata(cheie);
    if (!st) return false;
    if (st.an && st.luna) { an = st.an; luna = st.luna; }
    mesajSucces = st.mesaj || "";
    return true;
  };
  preia();
  const filtru = { text: "", stare: "" };
  const deschise = new Set();
  const cerereNoua = ultimaCerere();   // [C103] luna schimbată în șir: numai registrul de casă al lunii afișate ajunge pe ecran
  const deseneaza = async (mod = {}) => {
    if (!mod.peLoc) corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    const actuala = cerereNoua();
    let reg = { operatiuni: [], sold_final: "0", avertismente: [] };
    try { reg = await api.get(`/tenants/${t.id}/casa/registru?an=${an}&luna=${luna}`); if (!actuala()) return; } catch { if (!actuala()) return; corp.innerHTML = `<p class="ecran-nota">Nu s-a putut încărca registrul de casă.</p>`; return; }
    // [D394 Î2] chitanța de vânzare fără factură — doar la firma marcată exceptată de la casa de marcat (Date firmă)
    let exceptata = false;
    try { exceptata = !!((await api.get(`/tenants/${t.id}/firma-profil/date`)).profil || {}).activitate_exceptata_amef; if (!actuala()) return; } catch { if (!actuala()) return; exceptata = false; }
    // [624] avertismentele de plafon: același text se spune o dată, nu o dată pe zi; stau în caseta atenționărilor de deasupra tabelului
    // (avertismentele registrului = atenționări -> caseta canonică .caseta-atentie, DS cap.5)
    const _avertLinii = grupeazaMesaje((reg.avertismente || []).map((a) => ({ text: (a.mesaj || a.cod || "") + (a.temei ? " · " + a.temei : "") })))
      .map((x) => `<div class="ca-mesaj pe-randuri c-avertisment">${esc(x)}</div>`).join("");
    const ops = reg.operatiuni || [];
    const randuri = ops.map((o, i) => {
      const respinsa = o.nota_status !== "validata" && o.stare_coada === "respinsa";
      const fel = o.nota_status === "validata" ? "validata" : o.stare_coada === "la_senior" ? "la_validare" : respinsa ? "respinsa" : "ciorna";
      const semne = [o.fara_chitanta && { fel: "fara_chitanta", text: "fără chitanță" }, o.alt_modul && { fel: "alt_modul", text: "din alt ecran" },
        o.stornata && { fel: "stornata", text: "stornată" }, respinsa && { fel: "respinsa", text: "motivul în detaliu" }].filter(Boolean);
      return { cheie: o.id != null ? "op" + o.id : "n" + (o.inregistrare_id || i), o, fel, respinsa, semne,
        data: o.data, explicatie: o.categorie_eticheta || "", document: o.document || "", partener: `${o.partener || ""} ${o.cui || ""}`,
        rulaj: Math.abs(Number(o.suma)), stare: { text: stareNotaCasa(o, t) }, stari: [fel, fel === "respinsa" ? "ciorna" : ""].filter(Boolean),
        cautaInPlus: [o.factura, o.nir, o.avans ? "avans" : ""].filter(Boolean).join(" ") };
    });
    // [624] explicațiile semnelor, o dată; notele respinse grupate pe motiv (același motiv o dată, cu zilele lui)
    const nr = {};
    randuri.forEach((r) => r.semne.forEach((s) => { nr[s.fel] = (nr[s.fel] || 0) + 1; }));
    const motiveRespinse = grupeazaMesaje(randuri.filter((r) => r.respinsa).map((r) => ({ text: `„${r.o.motiv_respingere || "fără motiv scris"}”`, unde: dataRo(r.o.data) })));
    const explicatie = (k) => `<div class="${EXPLICATII_CASA[k].atentie ? "ca-mesaj" : "ci-mesaj"} tn-explicatie" id="c-expl-${k}"><b>${esc(EXPLICATII_CASA[k].titlu)} (${nr[k]}):</b> ${esc(EXPLICATII_CASA[k].text)}${k === "respinsa" ? " " + esc(motiveRespinse.join("; ")) + "." : ""}</div>`;
    const chei = Object.keys(EXPLICATII_CASA).filter((k) => nr[k]);
    const at = chei.filter((k) => EXPLICATII_CASA[k].atentie), inf = chei.filter((k) => !EXPLICATII_CASA[k].atentie);
    const explicatii = chei.length || _avertLinii ? `<div class="tn-explicatii" id="c-explicatii">${at.length || _avertLinii ? `<div class="caseta-atentie" id="c-avertismente">${_avertLinii}${at.map(explicatie).join("")}</div>` : ""}${inf.length ? `<div class="caseta-info">${inf.map(explicatie).join("")}</div>` : ""}</div>` : "";
    const culoare = { validata: "var(--verde)", la_validare: "var(--galben-text)", respinsa: "var(--rosu)", ciorna: "var(--galben-text)" };
    const randHtml = (r) => {
      const o = r.o, m = motiveCasa(o), k = esc(r.cheie);
      const deschis = deschise.has(r.cheie);
      const suma = `${Number(o.suma) < 0 ? "−" : ""}${bani(Math.abs(Number(o.suma)))}`;
      const obs = [
        o.partener || o.cui ? `Partener: ${esc(o.partener || "")}${o.cui ? " · CUI " + esc(o.cui) : ""}` : "",
        o.document ? `Document: ${esc(o.document)}` : "Document: nescris pe operațiune",
        o.factura ? `Stinge factura ${esc(o.factura)}` : "", o.avans ? "Avans (fără factură stinsă)" : "", o.nir ? `Plata pentru ${esc(o.nir)}` : "",
        o.storno_de ? "Rândul stornează o operațiune validată." : "", o.stornata ? "Operațiunea e stornată." : "",
        o.fara_chitanta ? "Încasare fără chitanță emisă în aplicație." : "",
        `Nota: ${esc(stareNotaCasa(o, t))}`,
      ].filter(Boolean).map((x) => `<p class="pf-frand-sub">${x}</p>`).join("");
      const cota = exceptata && o.chitanta_neclasificata ? `<span class="c-cota-zona" style="display:inline-flex;gap:6px;align-items:center;flex-wrap:wrap">
          <select class="camp-input" id="c-cota-${o.chitanta_neclasificata}" data-butoane aria-label="Cota TVA a chitanței" style="width:auto">${ALEGE}${[21, 11, 0].map((c) => `<option value="${c}">${c ? c + "%" : "0% (scutit)"}</option>`).join("")}</select>
          <button type="button" class="buton-secundar" data-cota="${o.chitanta_neclasificata}" data-actiune="PUT /tenants/{tenant_id}/chitante/{chitanta_id}/cota">Stabilește cota</button></span>` : "";
      const actDetaliu = [
        butonRand("buton-secundar", `data-chpdf="${o.chitanta_id || ""}" data-actiune="GET /tenants/{tenant_id}/chitante/{chitanta_id}/pdf"`, "PDF chitanță", m.pdf),
        butonRand("buton-secundar", `data-leaga="${o.id || ""}" data-cui="${esc(o.cui || "")}" data-cat="${esc(o.categorie || "")}" data-suma="${esc(o.suma)}" data-actiune="POST /tenants/{tenant_id}/casa/operatiuni/{op_id}/leaga|POST /tenants/{tenant_id}/casa/previzualizare"`, "Leagă de factură", m.leaga),
        cota].filter(Boolean).join(" ");
      return `<tbody class="tn-nota" data-tn="${k}"${o.id != null ? ` data-op-id="${o.id}"` : ""}>
        <tr class="tn-rand${deschis ? " tn-deschis" : ""}">
          <td><button type="button" class="btn-link tn-deschide" aria-expanded="${deschis}" aria-controls="c-det-${k}" aria-label="Detaliul operațiunii din ${dataRo(o.data)}">${dataRo(o.data)}</button></td>
          <td>${o.document ? esc(o.document) : `<span class="tip-desc">fără document</span>`}</td>
          <td>${esc(o.partener || "")}<div class="tip-desc">${esc(o.categorie_eticheta || "")}${o.factura ? " · factura " + esc(o.factura) : ""}${o.avans ? " · avans" : ""}${o.nir ? " pentru " + esc(o.nir) : ""}</div></td>
          <td class="fd-td-num">${o.tip !== "plata" ? suma : ""}</td>
          <td class="fd-td-num">${o.tip === "plata" ? suma : ""}</td>
          <td class="fd-td-num">${bani(o.sold)}</td>
          <td><span style="color:${culoare[r.fel]};font-weight:600">● ${esc(r.respinsa ? "notă respinsă la validare" : stareNotaCasa(o, t))}</span>${r.semne.filter((s) => s.fel !== "respinsa").map((s) => `<div class="tip-desc tn-semn" data-semn="${esc(s.fel)}">${esc(s.text)}</div>`).join("")}</td>
          <td class="tn-actiuni">${butonRand("buton-secundar", `data-storno="${o.id || ""}" data-actiune="POST /tenants/{tenant_id}/casa/operatiuni/{op_id}/storneaza"`, "Stornează", m.storno)}
            ${butonRand("buton-secundar", `data-del="${o.id || ""}" data-actiune="DELETE /tenants/{tenant_id}/casa/operatiuni/{op_id}"`, "Șterge", m.sterge)}</td>
        </tr>
        <tr class="tn-detaliu" id="c-det-${k}"${deschis ? "" : " hidden"}><td colspan="8">${obs}${r.respinsa ? `<div class="caseta-atentie"><div class="ca-mesaj">Respinsă la validare: ${esc(motivInFraza(o.motiv_respingere))}</div></div>` : ""}<p class="tn-detaliu-actiuni">${actDetaliu}</p></td></tr>
      </tbody>`;
    };
    const tabel = !ops.length ? `${explicatii}<div class="stare-goala" id="c-gol">Nicio operațiune în luna asta.</div>`
      : `${explicatii}<table class="fd-tabel tn-tabel" id="c-tabel">
          <thead><tr><th>Data</th><th>Document</th><th>Partener · operațiunea</th><th class="fd-td-num">Încasare (lei)</th><th class="fd-td-num">Plată (lei)</th><th class="fd-td-num">Sold (lei)</th><th>Nota</th><th>Acțiune</th></tr></thead>
          ${randuri.map(randHtml).join("")}</table>
        <div class="stare-goala" id="c-nimic" hidden>Nicio operațiune nu se potrivește căutării. Schimbă textul căutat sau starea aleasă.</div>`;
    const motivChit = exceptata ? null : "Chitanța fără factură e numai a activității exceptate de la casa de marcat (Date firmă › Activitate exceptată AMEF).";
    corp.innerHTML = `
      <div class="rezumat-fix" id="c-rezumat">
      <h2 class="pf-titlu">Casă ${semnAjutor("F015")}</h2>
      ${mesajSucces ? `<p class="pf-intro c-confirmare" id="c-confirmare" style="color:var(--verde);font-weight:600">${mesajSucces}</p>` : ""}
      <p class="pf-intro">Luna ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")} · sold la început <b id="c-sold-inceput">${bani(reg.sold_initial || 0)} lei</b> · sold final <b id="c-sold-final">${bani(reg.sold_final)} lei</b>${reg.sold_final_validat != null && Number(reg.sold_final_validat) !== Number(reg.sold_final) ? ` (din care în contabilitate, pe notele validate — fișa contului 5311: <b id="c-sold-validat">${bani(reg.sold_final_validat)} lei</b>; restul sunt note ciornă)` : ""}
        <button class="buton-secundar" id="c-prev" style="margin-left:12px">← luna</button>
        <button class="buton-secundar" id="c-next">luna →</button></p>
      <p><button class="buton-secundar" id="c-toggle" data-actiune="POST /tenants/{tenant_id}/casa/operatiuni">+ Dispoziție nouă</button>
        ${butonRand("buton-secundar", `id="c-chit-toggle" data-actiune="POST /tenants/{tenant_id}/chitante"`, "+ Chitanță fără factură", motivChit)}
        ${ops.length ? `<span style="margin-left:12px">${htmlCautare("c", { stari: STARI_CASA, valoare: filtru.text, stare: filtru.stare, eticheta: "Caută: partener, document, sumă, factură" })}</span>` : ""}</p>
      <div id="c-rand-mesaj"></div>
      </div>
      ${tabel}`;
    mesajSucces = "";  // [R162] se goleste dupa randare, ca sa nu ramana lipit la urmatoarea
    const zonaRand = corp.querySelector("#c-rand-mesaj");
    const tn = ops.length ? legaTabelNote(corp, { pre: "c", randuri, deschise }) : null;
    const aplicaFiltru = () => {
      if (!tn) return;
      const r = tn.filtreaza(filtru.text, filtru.stare);
      const z = corp.querySelector("#c-numar");
      if (z) z.textContent = filtru.text || filtru.stare ? textNumar(r.vazute, r.total, "operațiune", "operațiuni") : "";
    };
    aplicaFiltru();
    const cCauta = corp.querySelector("#c-cauta"), cStare = corp.querySelector("#c-stare");
    if (cCauta) cCauta.addEventListener("input", () => { filtru.text = cCauta.value; aplicaFiltru(); });
    if (cStare) cStare.addEventListener("change", () => { filtru.stare = cStare.value; aplicaFiltru(); });
    const confirma = (tb, text) => { arataMesaj(zonaRand, text, "ok"); if (tb) tb.classList.add("val-evidentiat"); };
    const numeOp = (b) => { const tb = b.closest("tbody.tn-nota"); const r = tb && randuri.find((x) => x.cheie === tb.dataset.tn); return r ? `operațiunea din ${dataRo(r.o.data)} (${bani(Math.abs(Number(r.o.suma)))} lei${r.o.partener ? ", " + r.o.partener : ""})` : "operațiunea"; };
    // [673] dispoziția nouă / chitanța / legarea: fereastra lor; la întoarcere Casa se redesenează pe luna lor, cu confirmarea
    const stareLuna = { an, luna };
    corp.querySelector("#c-toggle").addEventListener("click", () =>
      deschideActiunea(nav, cheie, stareLuna, "Dispoziție nouă", (c2) => ecranDispozitieNoua(c2, nav, t, cheie)));
    corp.querySelector("#c-chit-toggle").addEventListener("click", () =>
      deschideActiunea(nav, cheie, stareLuna, "Chitanță fără factură", (c2) => ecranChitantaFaraFactura(c2, nav, t, cheie)));
    corp.querySelector("#c-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#c-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    // facturile deschise se citesc în handlerul butonului (care poartă acțiunea `casa/previzualizare`), apoi se deschide fereastra cu ele
    corp.querySelectorAll("[data-leaga]").forEach((b) => b.addEventListener("click", async () => {
      const op = { id: b.dataset.leaga, cui: b.dataset.cui, categorie: b.dataset.cat, suma: b.dataset.suma, eticheta: numeOp(b) };
      let fs;
      try { fs = (await api.post(`/tenants/${t.id}/casa/previzualizare`, { data: dataIso(), categorie: op.categorie, suma: Number(op.suma), cui: op.cui || null })).facturi || []; }
      catch (e) { arataMesaj(zonaRand, e.mesaj || "Nu s-au putut încărca facturile deschise.", "eroare"); return; }
      deschideActiunea(nav, cheie, stareLuna, "Leagă de factură", (c2) => ecranLeagaDeFactura(c2, nav, t, cheie, op, fs));
    }));
    // [D394 Î2] chitanța fără factură și fără cotă (emisă înainte de marcarea exceptării): D394 o refuză numită până aici
    corp.querySelectorAll("[data-cota]").forEach((b) => b.addEventListener("click", async () => {
      const id = b.dataset.cota;
      curataEroriCamp(corp);
      const v = corp.querySelector(`#c-cota-${id}`).value;
      if (v === "") { eroareCamp(corp, `c-cota-${id}`, "Alege cota de TVA (0% dacă activitatea e scutită)."); return; }
      try {
        const r = await api.put(`/tenants/${t.id}/chitante/${id}/cota`, { cota_tva: Number(v) });
        mesajSucces = `Cota ${esc(String(r.cota_tva))}% stabilită; nota chitanței e acum ${esc(r.nota || "")} (${stareNota(r)}).`;
        deseneaza({ peLoc: true });
      } catch (e) { refuzPeRand(b, e.mesaj || "eroare"); }
    }));
    // [lotul 11, 456] PDF-ul chitanței de pe rând (aceeași rută ca în detaliul facturii)
    corp.querySelectorAll("[data-chpdf]").forEach((b) => b.addEventListener("click", async () => {
      try { await deschide(`/tenants/${t.id}/chitante/${b.dataset.chpdf}/pdf`); }
      catch (e) { refuzPeRand(b, e.mesaj || "PDF-ul chitanței nu s-a putut deschide."); }
    }));
    corp.querySelectorAll("[data-storno]").forEach((b) => b.addEventListener("click", () => {
      confirmaCaseta(locInDetaliu(b), "Stornezi operațiunea? Nota ei e validată: se scrie operațiunea inversă în registru și o notă în roșu, care trece prin validare. Chitanța ei se anulează.", async () => {
        const nume = numeOp(b), tb = b.closest("tbody.tn-nota");
        try { await api.post(`/tenants/${t.id}/casa/operatiuni/${b.dataset.storno}/storneaza`, { data: dataIso() }); if (tb) deschise.delete(tb.dataset.tn); await deseneaza({ peLoc: true }); confirma(null, `Ai stornat ${nume}: rândul de stornare e în registru.`); }
        catch (e) { refuzPeRand(b, e.mesaj || "Nu s-a putut storna operațiunea."); }
      }, { textOk: "Stornează" });
    }));
    corp.querySelectorAll("[data-del]").forEach((b) => b.addEventListener("click", () => {
      // [lotul 11, 456] chitanța emisă pe operațiune nu se șterge: se anulează și rămâne în evidență
      const tb = b.closest("tbody.tn-nota");
      const cuChitanta = !!(tb && tb.querySelector('[data-chpdf]:not([aria-disabled="true"])'));
      confirmaCaseta(locInDetaliu(b), "Ștergi operațiunea și ciorna legată?" + (cuChitanta ? " Chitanța ei se anulează (rămâne în evidență, anulată)." : ""), async () => {  // audit_cab_lot2_v1
        const nume = numeOp(b);
        try { await api.del(`/tenants/${t.id}/casa/operatiuni/${b.dataset.del}`); if (tb) deschise.delete(tb.dataset.tn); await deseneaza({ peLoc: true }); confirma(null, `Ai șters ${nume} și ciorna ei.`); }
        catch (e) { refuzPeRand(b, e.mesaj || "Eroare la ștergere."); }
      }, { textOk: "Șterge" });
    }));
  };
  // [673] Casa păstrată (omul scrisese în căutare) nu se redesenează la închiderea ferestrei de deasupra: se redesenează ea, cu confirmarea
  corp.addEventListener("nav:revenire", () => { if (preia()) deseneaza(); });
  deseneaza();
}

// [lotul 13, 673] „+ Dispoziție nouă” — fereastra ei (DS cap.2a v2.104), cu tot ce avea formularul din Casă: factura stinsă, avansul, NIR-ul
// fără factură, plafonul (deficiența 278, `casa/previzualizare`, aceeași sursă ca salvarea). [676] Tipul — cinci opțiuni — e butoane alăturate
// (`data-butoane`, mecanismul DS). După „Adaugă” fereastra se închide, iar Casa se redesenează pe luna dispoziției, cu confirmarea.
function ecranDispozitieNoua(corp, nav, t, cheie) {
  // [deficiența 332, 18.10.2026] data dispoziției noi = data faptului, azi (clasa 68: data propusă pe formularul nou; DECIZII S2
  // „emiterea, încasarea, registrul au data faptului de azi”); omul o schimbă dacă faptul e din altă zi. Garda: core/test_332_data_propusa.py
  corp.innerHTML = `
    <h2 class="pf-titlu">Dispoziție nouă</h2>
    <div class="grila-campuri" id="c-campuri" data-actiune="POST /tenants/{tenant_id}/casa/previzualizare">
      <label class="camp"><span class="camp-eticheta">Data</span><input type="date" id="c-data" class="camp-input" value="${dataIso()}"></label>
      <label class="camp"><span class="camp-eticheta">Tip</span><select id="c-cat" class="camp-input" data-butoane>${ALEGE}${CATEGORII_CASA.map(([v, l]) => `<option value="${v}">${l}</option>`).join("")}</select></label>
      <label class="camp"><span class="camp-eticheta">Suma (lei)</span><input type="number" step="0.01" id="c-suma" class="camp-input"></label>
      <label class="camp" id="c-l-part"><span class="camp-eticheta">Partener</span><input type="text" id="c-part" class="camp-input"></label>
      <label class="camp" id="c-l-cui">
        <span class="camp-eticheta" style="display:flex;justify-content:space-between;align-items:center">
          CUI
          <button type="button" class="buton-secundar buton-mic" id="c-cui-verif">Verifică la ANAF</button>
        </span>
        <input type="text" id="c-cui" class="camp-input">
      </label>
      <!-- [lotul 13, 683] „Avans spre decontare” (542) se dă unui SALARIAT, ales din evidența firmei: în locul partenerului și al CUI-ului -->
      <div class="camp" id="c-zona-salariat" hidden>
        <label class="camp-eticheta" for="c-salariat">Salariatul<span class="oblig">*</span></label>
        <input type="text" id="c-salariat-cauta" class="camp-input" data-cautare placeholder="Caută salariatul…" aria-label="Caută salariatul" autocomplete="off" style="margin-bottom:6px">
        <select id="c-salariat" class="camp-input"><option value="" data-alege>— se încarcă salariații… —</option></select>
      </div>
      <label class="camp"><span class="camp-eticheta">Document</span><input type="text" id="c-doc" class="camp-input"></label>
    </div>
    <div class="em-cui-stare" id="c-cui-stare"></div>
    <div id="c-facturi" hidden style="margin-top:10px"></div>
    <div id="c-previz" style="margin-top:10px"></div>
    <div class="bara-fixa"><p style="margin-top:10px"><button class="buton-primar" id="c-adauga" data-actiune="POST /tenants/{tenant_id}/casa/operatiuni">Adaugă</button>
      <button type="button" class="buton-secundar" id="c-renunta" data-fara-actiune="închide fereastra, fără scriere">Renunță</button></p>
    <div id="c-mesaj"></div></div>`;
  // [deficiența 310] „formularul «Dispoziție nouă» n-are Renunță”: închide fereastra, fără scriere
  corp.querySelector("#c-renunta").addEventListener("click", () => nav.inapoi());
  const bCv = corp.querySelector("#c-cui-verif");
  // [lotul 12, 459.1] numele partenerului adus de la ANAF dispare când se schimbă CUI-ul (cel scris de om rămâne)
  const anafC = legaDateAnaf(corp.querySelector("#c-cui"), [corp.querySelector("#c-part")], corp.querySelector("#c-cui-stare"));
  bCv.addEventListener("click", async () => {  /* verificare_anaf_casa_v1 */
    const cui = corp.querySelector("#c-cui").value.trim();
    const stare = corp.querySelector("#c-cui-stare");
    if (!cui || bCv.disabled) return;
    const textB = bCv.textContent;  // [303, comanda 7.2] blocat cât așteaptă, ca la factură
    bCv.disabled = true; bCv.setAttribute("aria-busy", "true"); bCv.textContent = "Se verifică…";
    stare.textContent = "se verifică la ANAF…";
    stare.className = "em-cui-stare";
    try {
      const r = await api.get(`/tenants/${t.id}/verifica-cui/${encodeURIComponent(cui)}`);
      if (r && r.gasit) {
        anafC.pune([r.denumire], { suprascrie: true });   // „Verifică la ANAF” e cererea explicită a omului
        stare.innerHTML = `<span class="em-cui-info">${r.platitor_tva ? "plătitor TVA" : "neplătitor TVA"}${r.inactiv ? " · <b style=\"color:var(--rosu)\">INACTIVĂ fiscal</b>" : ""}</span>`;
        stare.className = "em-cui-stare";
        // [lotul 11, 444] fișa clientului / furnizorului cu acest CUI are alt nume decât ANAF: se spune și se propune actualizarea
        propuneNumeAnaf(stare, r, t.id, { pre: "c" });
      } else {
        stare.textContent = "CUI negăsit la ANAF";
        stare.className = "em-cui-stare em-cui-rau";
      }
    } catch (e) {
      stare.textContent = (e && e.mesaj) || "Verificarea nu s-a putut face — reîncearcă.";
      stare.className = "em-cui-stare em-cui-rau pe-randuri";
    } finally { bCv.disabled = false; bCv.removeAttribute("aria-busy"); bCv.textContent = textB; }
  });
  // [deficiența 278] Factura stinsă de dispoziție, avansul și plafonul — din formular, înainte de „Adaugă” (`casa/previzualizare`,
  // aceeași sursă ca salvarea: `casa_api.semnale` + `casa.verifica_plafon` cu operațiunea propusă inclusă).
  const alese = new Set();
  let facturiPart = [], facturiAsteptare = [], avansFaraFactura = false, tPreviz = null;
  // [deficiența 405] NIR-urile fără factură ale furnizorului (marfa pe 408), alese ca facturile: plata lor e avans 4091 = 5311
  const aleseNir = new Set();
  let niruriPart = [];
  // [deficiența 407] avansul acordat furnizorului: destinația lui (contul 409x), aleasă de om; `avansInPlata` = previzualizarea a găsit avans
  let avansDest = "", avansInPlata = false;
  const DEST_AVANS = [["stocuri", "bunuri (4091)"], ["servicii", "servicii (4092)"], ["imobilizari", "imobilizări corporale (4093)"],
    ["imobilizari_necorporale", "imobilizări necorporale (4094)"]];
  const zFact = corp.querySelector("#c-facturi"), zPrev = corp.querySelector("#c-previz");
  const cuFacturi = () => ["incasare_client", "plata_furnizor"].includes(corp.querySelector("#c-cat").value);
  const alocari = () => {
    let rest = parseFloat(corp.querySelector("#c-suma").value) || 0;
    const out = [];
    facturiPart.filter((f) => alese.has(f.id)).forEach((f) => {
      if (rest <= 0.005) return;
      const parte = Math.min(parseFloat(f.sold), rest);
      out.push({ factura_id: f.id, suma: parte.toFixed(2) });
      rest -= parte;
    });
    // [405] după facturi, NIR-urile alese, fiecare cel mult cât mai e de plătit din el
    const nir = [];
    niruriPart.filter((n) => aleseNir.has(n.id)).forEach((n) => {
      if (rest <= 0.005) return;
      const parte = Math.min(parseFloat(n.rest), rest);
      nir.push({ nir_id: n.id, suma: parte.toFixed(2) });
      rest -= parte;
    });
    return { facturi: out, niruri: nir };
  };
  // [lotul 13, 683] la „Avans spre decontare” partenerul e salariatul (lista lui, cu căutare), nu un partener scris: câmpurile Partener și CUI
  // se ascund, iar corpul poartă `salariat_id`. Lista salariaților activi se aduce o dată, la prima alegere a categoriei; nimic precompletat.
  const zSal = corp.querySelector("#c-zona-salariat"), selSal = corp.querySelector("#c-salariat");
  let salariatiIncarcati = false;
  const cuSalariat = () => corp.querySelector("#c-cat").value === "avans_decontare";
  const salariatiInLista = async () => {
    if (salariatiIncarcati) return;
    salariatiIncarcati = true;
    try {
      const r = await api.get(`/tenants/${t.id}/salariati?activ=true`);
      const sal = (r && r.salariati) || [];
      selSal.innerHTML = sal.length ? ALEGE + sal.map((x) => `<option value="${x.id}">${esc([x.nume, x.prenume].filter(Boolean).join(" "))}</option>`).join("")
        : `<option value="" data-alege>Firma nu are salariați în Salarizare</option>`;
      cautaInLista(corp.querySelector("#c-salariat-cauta"), selSal);
    } catch (e) {
      salariatiIncarcati = false;
      selSal.innerHTML = `<option value="" data-alege>Salariații nu s-au putut încărca — reîncearcă</option>`;
    }
  };
  corp.querySelector("#c-cat").addEventListener("change", () => {
    const sal = cuSalariat();
    zSal.hidden = !sal;
    corp.querySelector("#c-l-part").hidden = corp.querySelector("#c-l-cui").hidden = sal;
    if (sal) salariatiInLista();
  });
  const opPropusa = () => ({
    data: corp.querySelector("#c-data").value, categorie: corp.querySelector("#c-cat").value,
    suma: parseFloat(corp.querySelector("#c-suma").value) || 0,
    partener: cuSalariat() ? null : corp.querySelector("#c-part").value || null,
    cui: cuSalariat() ? null : corp.querySelector("#c-cui").value || null, document: corp.querySelector("#c-doc").value || null,
    salariat_id: cuSalariat() && selSal.value ? Number(selSal.value) : null,   // [683]
    facturi: cuFacturi() ? alocari().facturi : [], niruri: cuFacturi() ? alocari().niruri : [],   // [405]
    avans: cuFacturi() && avansFaraFactura && !alese.size && !aleseNir.size,
    avans_destinatie: avansDest || null,   // [407]
  });
  // [lotul 11, 440] zona desenată ultima oară: o previzualizare care nu schimbă nimic NU rescrie zona. `change`-ul de la PĂRĂSIREA
  // câmpului (CUI, document) vine chiar la clicul pe „Adaugă” și pornește previzualizarea; rescrierea zonei, la 250 ms după refuzul
  // serverului, ștergea eroarea de lângă „Avansul e pentru” (`c-avans-dest`) — se vedea o clipă, apoi dispărea.
  let htmlFact = "";
  const deseneazaFacturi = () => {
    if (!cuFacturi()) { zFact.hidden = true; zFact.innerHTML = ""; htmlFact = ""; return; }
    zFact.hidden = false;
    const inc = corp.querySelector("#c-cat").value === "incasare_client";
    // [lotul 13, 669] soldurile preluate la migrare („Sold la …”) sunt în listă ca facturile: se sting la încasare / plată
    const html = `<div class="pf-frand-nume" style="margin-bottom:6px">${inc ? "Factura încasată (sau soldul preluat al clientului)" : "Factura plătită (sau soldul preluat al furnizorului)"}</div>` +
      (facturiPart.length ? facturiPart.map((f) => `<label class="set-bifa" style="display:block"><input type="checkbox" data-cf="${f.id}"${alese.has(f.id) ? " checked" : ""}>
        ${numeDocDeschis(f)} · ${esc(f.tert_nume || "")} · rămas ${bani(f.sold)} lei</label>`).join("")
        : `<p class="ecran-nota">${inc ? "Nicio factură emisă neîncasată și niciun sold preluat de încasat" : "Nicio factură primită neplătită și niciun sold preluat de plătit"}${corp.querySelector("#c-cui").value ? " pentru acest CUI" : ""}.</p>`) +
      // [deficiența 310] factura stinsă de o notă încă la validare nu e în listă — și se spune de ce
      facturiAsteptare.map((f) => `<p class="ecran-nota c-fact-asteptare">${esc(f.numar)} din ${dataRo(f.data_emitere)} (${bani(f.suma)} lei) nu e în listă: e ${inc
        ? "încasată" : "plătită"} printr-o notă care așteaptă validarea (${esc(f.note.join(", "))}). Dacă nota se respinge, factura apare din nou aici.</p>`).join("") +
      // [deficiența 405] NIR-urile fără factură (datoria pe 408), cu ce mai e de plătit: plata lor e avans acordat furnizorului, compensat la factură
      (!inc && niruriPart.length ? `<div class="pf-frand-nume" id="c-niruri" style="margin:8px 0 6px">NIR fără factură plătit (avans 4091 = 5311, compensat la sosirea facturii)</div>` +
        niruriPart.map((n) => `<label class="set-bifa" style="display:block"><input type="checkbox" data-cn="${n.id}"${aleseNir.has(n.id) ? " checked" : ""}>
        ${esc(n.eticheta)} · ${esc(n.furnizor || "")} · rămas ${bani(n.rest)} lei</label>`).join("") : "") +
      `<label class="set-bifa" style="display:block;margin-top:4px"><input type="checkbox" id="c-avans"${avansFaraFactura ? " checked" : ""}${alese.size || aleseNir.size ? " disabled" : ""}>
        Avans, fără factură (${inc ? "factura de avans se emite după" : "factura de avans vine de la furnizor"})</label>` +
      // [407] la plată, avansul acordat furnizorului merge pe 409x: destinația se alege (bunuri / servicii / imobilizări)
      (!inc && (avansInPlata || avansFaraFactura) ? `<label class="camp" style="display:block;margin-top:6px;max-width:360px"><span class="camp-eticheta">Avansul e pentru<span class="oblig">*</span></span>
        <select id="c-avans-dest" class="camp-input" data-butoane aria-label="Destinația avansului">${avansDest ? "" : ALEGE}${DEST_AVANS.map(([v, l]) => `<option value="${v}"${v === avansDest ? " selected" : ""}>${l}</option>`).join("")}</select></label>` : "");
    if (html === htmlFact) return;   // [440] nimic schimbat: câmpurile, bifele și erorile de lângă ele rămân cum sunt
    htmlFact = html;
    zFact.innerHTML = html;
    zFact.querySelectorAll("[data-cf]").forEach((c) => c.addEventListener("change", () => {
      const id = Number(c.dataset.cf);
      if (c.checked) alese.add(id); else alese.delete(id);
      const f = facturiPart.find((x) => x.id === id);
      if (c.checked && f && !corp.querySelector("#c-part").value) {
        corp.querySelector("#c-part").value = f.tert_nume || "";
        corp.querySelector("#c-cui").value = f.tert_cui || "";
      }
      programeazaPreviz();
    }));
    zFact.querySelectorAll("[data-cn]").forEach((c) => c.addEventListener("change", () => {   // [405]
      const id = Number(c.dataset.cn);
      if (c.checked) aleseNir.add(id); else aleseNir.delete(id);
      const n = niruriPart.find((x) => x.id === id);
      if (c.checked && n && !corp.querySelector("#c-part").value) {
        corp.querySelector("#c-part").value = n.furnizor || "";
        corp.querySelector("#c-cui").value = n.cui || "";
      }
      programeazaPreviz();
    }));
    const ca = zFact.querySelector("#c-avans");
    ca.addEventListener("change", () => { avansFaraFactura = ca.checked; programeazaPreviz(); });
    const cd = zFact.querySelector("#c-avans-dest");
    // [440] alegerea destinației schimbă operațiunea propusă: previzualizarea se reface (alegerea golește, ca orice corectare — 290 —,
    // refuzul de formular al zonei, deci și „nu încape în casă” de sub formular, care altfel nu mai revenea)
    if (cd) cd.addEventListener("change", () => { avansDest = cd.value; programeazaPreviz(); });
  };
  // [278] previzualizarea (facturile partenerului, avansul, plafonul) se cere la orice schimbare a câmpurilor dispoziției, cu o
  // întârziere de 250 ms la tastare. Ascultarea stă pe zona câmpurilor (`#c-campuri`, marcată cu acțiunea — `scan_drepturi_ui` leagă
  // cererea de elementul ei); tastarea și bifele facturilor trimit tot acolo un `change`.
  const zCampuri = corp.querySelector("#c-campuri");
  const programeazaPreviz = () => zCampuri.dispatchEvent(new Event("change"));
  const cererePreviz = ultimaCerere();   // [C103] câmpurile dispoziției editate în șir: numai previzualizarea ultimei completări ajunge pe ecran
  zCampuri.addEventListener("change", () => {
    const actuala = cererePreviz();   // orice schimbare scoate din joc previzualizarea cerută înainte (și când câmpurile rămân incomplete)
    clearTimeout(tPreviz);
    tPreviz = setTimeout(async () => {
      // [C51, 18.10.2026, prins de plasă sub încărcare: „Cannot read properties of null (reading 'value')” în `opPropusa`] cronometrul
      // programat la ultima tastare poate porni DUPĂ ce „Adaugă” a salvat și a închis fereastra: formularul ei nu mai e — se oprește
      if (!zCampuri.isConnected) return;
      const op = opPropusa();
      if (!op.data || !op.categorie || !(op.suma > 0)) { zPrev.innerHTML = ""; deseneazaFacturi(); return; }
      let r;
      try { r = await api.post(`/tenants/${t.id}/casa/previzualizare`, op); if (!actuala()) return; } catch (e) {
        if (!actuala()) return;
        zPrev.innerHTML = "<div></div>";
        arataMesaj(zPrev.firstChild, `Facturile clientului / furnizorului, avansul și plafonul nu s-au putut calcula (${e.mesaj || "eroare"}); `
          + "salvarea le verifică oricum.", "eroare");
        return;
      }
      if (!zCampuri.isConnected) return;   // [C51] aceeași cursă, cu cererea în zbor
      facturiPart = r.facturi || [];
      facturiAsteptare = r.facturi_asteptare || [];
      avansInPlata = !!r.avans && op.categorie === "plata_furnizor";   // [407]
      [...alese].forEach((id) => { if (!facturiPart.some((f) => f.id === id)) alese.delete(id); });
      niruriPart = r.niruri || [];   // [405]
      [...aleseNir].forEach((id) => { if (!niruriPart.some((n) => n.id === id)) aleseNir.delete(id); });
      pastreazaCampulActiv(corp, deseneazaFacturi);   // [C103] suma scrisă pe o factură cât sosește previzualizarea nu se pierde
      const linii = [...(r.avans ? [r.avans.mesaj] : []), ...(r.semnale || []),
        ...(r.avertismente || []).map((a) => (a.mesaj || a.cod || "") + (a.temei ? " · " + a.temei : ""))];
      zPrev.innerHTML = linii.length ? `<div class="caseta-atentie" id="c-previz-avert">${linii.map((x) => `<div class="ca-mesaj">${esc(x)}</div>`).join("")}</div>` : "";
      // [deficiența 406] plata care ar duce casa sub zero: refuzul salvării, spus înainte de „Adaugă”
      if (r.refuz) { zPrev.insertAdjacentHTML("afterbegin", "<div id=\"c-previz-refuz\"></div>"); arataMesaj(zPrev.querySelector("#c-previz-refuz"), r.refuz, "eroare"); }
    }, 250);
  });
  zCampuri.addEventListener("input", programeazaPreviz);
  // [R161, 05.09.2026] Butonul nu mai sta STINS cu motivul in `title`. Se apasa mereu, iar
  // refuzul se aseaza langa campul vinovat (`eroareCamp`: contur rosu + `aria-invalid` +
  // mesaj ancorat) — acelasi ajutor ca in restul aplicatiei. *Un buton care nu se poate
  // apasa nu poate raspunde, iar un motiv care traieste in `title` nu se vede pe atingere.*
  // [lotul 13, 543] funcția are nume: după seria stabilită pe loc, operația se reia chemând-o, nu printr-un clic dat de cod
  corp.querySelector("#c-adauga").addEventListener("click", async function adaugaOperatiaCasa() {
    const zonaM = corp.querySelector("#c-mesaj");
    curataEroriCamp(corp);
    const _d = corp.querySelector("#c-data").value;
    const _s = parseFloat(corp.querySelector("#c-suma").value);
    let _lipsa = false;
    // doua campuri, doua mesaje: care lipseste se spune pe randul lui, amandoua daca e cazul
    if (!_d) { eroareCamp(corp, "c-data", "Completează data dispoziției."); _lipsa = true; }
    if (!(_s > 0)) {
      eroareCamp(corp, "c-suma", "Suma trebuie să fie un număr mai mare ca 0.");
      _lipsa = true;
    }
    // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite; [lotul 11, 440] categoria lipsă se marchează odată cu data și suma
    if (cereAlegerile(corp, ["#c-cat", "#c-salariat"])) _lipsa = true;   // [683] salariatul se cere numai când lista lui e vizibilă
    if (_lipsa) return;
    try {
      const r = await api.post(`/tenants/${t.id}/casa/operatiuni`, opPropusa());
      const ops = r.operatiuni || [];
      const parti = ops.map((o) => o.factura_id ? `${bani(o.suma)} lei pe factură` : o.nir_id ? `${bani(o.suma)} lei avans pe NIR`
        : o.avans ? `${bani(o.suma)} lei avans` : `${bani(o.suma)} lei`);
      const av = (r.avertismente || []).length;
      // [deficiența 279] starea REALĂ a notei (ciornă sau plecată la validare), nu „ciornă” scris de mână
      const textSucces = [`Dispoziția a fost salvată${ops.length > 1 ? ": " + parti.join(", ") : ""}.`,
        ops.length > 1 ? `Notele ${r.nota} sunt ${stareNota(r, true)}.` : `Nota ${r.nota} e ${stareNota(r)}.`, pasNota(r, ops.length > 1),
        // [lotul 11, 456] chitanța emisă automat pe încasarea facturii, cu seria firmei (PDF-ul ei pe rândul operațiunii)
        ...(r.chitante || []).map((c) => `Chitanța ${numarCuSerie(c.serie, String(c.numar))} a fost emisă.`),
        ...(r.avans ? [r.avans.mesaj] : []), ...(r.semnale || []),
        ...(av ? [`${cate(av, "avertisment", "avertismente")} de plafon (Legea 70/2015).`] : [])].join(" ");
      // [673; lotul 12, C118 — clasa] fereastra se închide; Casa se redesenează pe luna dispoziției, cu confirmarea
      const dz = new Date(_d + "T00:00:00");
      inchideCuConfirmarea(nav, cheie, esc(textSucces), { an: dz.getFullYear(), luna: dz.getMonth() + 1 });
    } catch (e) {
      if (cereSeriaChitanteiPeLoc(zonaM, t.id, e, adaugaOperatiaCasa)) return;   // [lotul 13, 543] seria chitanțelor pe loc, ca la factură
      arataRefuzul(corp, e, zonaM);   // [lotul 11, 440] toate erorile serverului (id-urile câmpurilor Casă), fiecare lângă câmpul ei
    }
  });
}

// [lotul 13, 673] „+ Chitanță fără factură” — fereastra ei; [D394 Î2] doar la firma exceptată de la casa de marcat (Date firmă)
function ecranChitantaFaraFactura(corp, nav, t, cheie) {
  corp.innerHTML = `
    <h2 class="pf-titlu">Chitanță fără factură</h2>
    <p class="pf-intro">Vânzare din activitatea exceptată de la casa de marcat.</p>
    <div class="grila-campuri">
      <label class="camp"><span class="camp-eticheta">Data</span><input type="date" id="ch-data" class="camp-input" value="${dataIso()}"></label>
      <label class="camp"><span class="camp-eticheta">Suma încasată, cu TVA (lei)</span><input type="number" step="0.01" id="ch-suma" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Cota TVA</span><select id="ch-cota" class="camp-input" data-butoane>${ALEGE}${[21, 11, 0].map((c) => `<option value="${c}">${c ? c + "%" : "0% (scutit)"}</option>`).join("")}</select></label>
      <label class="camp"><span class="camp-eticheta">Client</span><input type="text" id="ch-client" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Reprezentând</span><input type="text" id="ch-repr" class="camp-input"></label>
    </div>
    <div class="bara-fixa"><p style="margin-top:10px"><button class="buton-primar" id="ch-emite" data-actiune="POST /tenants/{tenant_id}/chitante">Emite chitanța</button>
      <button type="button" class="buton-secundar" id="ch-renunta" data-fara-actiune="închide fereastra, fără scriere">Renunță</button></p>
    <div id="ch-mesaj"></div></div>`;
  corp.querySelector("#ch-renunta").addEventListener("click", () => nav.inapoi());
  // [lotul 13, 543] funcția are nume: după seria stabilită pe loc, emiterea se reia chemând-o, nu printr-un clic dat de cod
  corp.querySelector("#ch-emite").addEventListener("click", async function emiteChitantaCasa() {
    const zonaM = corp.querySelector("#ch-mesaj");
    curataEroriCamp(corp);
    const data = corp.querySelector("#ch-data").value;
    const suma = parseFloat(corp.querySelector("#ch-suma").value);
    const cota = corp.querySelector("#ch-cota").value;
    let lipsa = false;
    if (!data) { eroareCamp(corp, "ch-data", "Completează data chitanței."); lipsa = true; }
    if (!(suma > 0)) { eroareCamp(corp, "ch-suma", "Suma trebuie să fie un număr mai mare ca 0."); lipsa = true; }
    if (cota === "") { eroareCamp(corp, "ch-cota", "Alege cota de TVA (0% dacă activitatea e scutită)."); lipsa = true; }
    if (lipsa) return;
    try {
      const r = await api.post(`/tenants/${t.id}/chitante`, {
        data, suma, cota_tva: Number(cota),
        client_nume: corp.querySelector("#ch-client").value || null,
        reprezentand: corp.querySelector("#ch-repr").value || null,
      });
      const av = (r.avertismente || []).length;
      // [lotul 11, 443] seria și numărul, separat: „KAI nr. 12” (numarCuSerie), nu „KAI-12”
      const dz = new Date(data + "T00:00:00");
      inchideCuConfirmarea(nav, cheie, `Chitanța ${esc(numarCuSerie(r.serie, String(r.numar)))} a fost emisă; nota ${esc(r.nota || "")} e ${stareNota(r)}.${av ? ` ${cate(av, "avertisment", "avertismente")} de plafon.` : ""}`,
        { an: dz.getFullYear(), luna: dz.getMonth() + 1 });
    } catch (e) {   // [lotul 11, 440] fiecare eroare a serverului lângă câmpul ei, textul refuzului sub buton
      if (cereSeriaChitanteiPeLoc(zonaM, t.id, e, emiteChitantaCasa)) return;   // [lotul 13, 543] seria chitanțelor pe loc, ca la factură
      arataRefuzul(corp, e, zonaM, { campuri: { data: "ch-data", suma: "ch-suma", cota_tva: "ch-cota", client_nume: "ch-client", reprezentand: "ch-repr" } });
    }
  });
}

// [lotul 13, 673] „Leagă de factură” — fereastra ei: [278] o încasare / plată salvată fără factură (sau avansul) se leagă de factura pe
// care o stinge — facturile deschise ale partenerului (și soldurile lui preluate la migrare, 669) cu rămas de cel puțin suma operațiunii;
// `fs` = facturile citite de butonul care deschide fereastra
function ecranLeagaDeFactura(corp, nav, t, cheie, op, fs) {
  fs = fs.filter((f) => Number(f.sold) + 0.005 >= Number(op.suma));
  corp.innerHTML = `
    <h2 class="pf-titlu">Leagă de factură · ${esc(op.eticheta)}</h2>
    <div class="c-leaga-zona">${fs.length ? fs.map((f) => `
      <button type="button" class="buton-secundar" data-leaga-f="${f.id}" data-actiune="POST /tenants/{tenant_id}/casa/operatiuni/{op_id}/leaga" style="margin:0 6px 6px 0">${numeDocDeschis(f)} · ${esc(f.tert_nume || "")} · rămas ${bani(f.sold)} lei</button>`).join("")
      : `<div class="stare-goala" id="c-leaga-gol">Nicio factură deschisă a partenerului (și niciun sold preluat) cu rămas de cel puțin ${bani(op.suma)} lei.</div>`}</div>
    <div class="bara-fixa"><p style="margin-top:10px"><button type="button" class="buton-secundar" id="c-leaga-renunta" data-fara-actiune="închide fereastra, fără scriere">Renunță</button></p>
    <div id="c-leaga-mesaj"></div></div>`;
  corp.querySelector("#c-leaga-renunta").addEventListener("click", () => nav.inapoi());
  corp.querySelectorAll("[data-leaga-f]").forEach((x) => x.addEventListener("click", async () => {
    try {
      const r = await api.post(`/tenants/${t.id}/casa/operatiuni/${op.id}/leaga`, { factura_id: Number(x.dataset.leagaF) });
      inchideCuConfirmarea(nav, cheie, `Operațiunea e legată de factura ${esc(r.factura)}.`);
    } catch (e) { arataMesaj(corp.querySelector("#c-leaga-mesaj"), e.mesaj || "Nu s-a putut lega.", "eroare"); }
  }));
}

// [16.10.2026, lotul 6 pct.2b, 276] Soldurile extrasului (MT940 `:60F:` / `:62F:`) față de contul băncii din contabilitate, la aceeași zi.
function randuriSolduri(sd) {
  if (!sd) return ["Soldurile: extrasul în tabel (.xls, .xlsx, .csv) nu are sold inițial și final, deci nu s-au comparat cu 5121."];
  return [["initial", "Sold inițial"], ["final", "Sold final"]].filter(([k]) => sd[k]).map(([k, et]) => {
    const x = sd[k];
    if (x.contabil === null) return `${et} la ${dataRo(x.data)}: ${bani(x.extras)} ${sd.valuta} în extras; în contabilitate necunoscut (ziua e dinaintea soldurilor de preluare).`;
    const d = Number(x.diferenta);
    return `${et} la ${dataRo(x.data)}: ${bani(x.extras)} ${sd.valuta} în extras, ${bani(x.contabil)} în ${sd.cont} (din notele validate) — ${d === 0 ? "identic" : "diferență " + bani(x.diferenta)}.`;
  });
}

// [banca] Import extras + reconciliere pe facturi
// [lotul 13, comanda Costin 13.1, verbatim]
//   624: „Importuri, audit, casă, bancă la forma din 617/622; observații la clic; respinsele grupate”
//   607: „Bancă (F1) | La comisionul bancar apare și «Alege facturile».”
//   669: „Soldurile preluate pe parteneri trebuie să apară ca sume de încasat/plătit [...] Aceeași verificare [...] la potrivirea extrasului
//        bancar.”
// Liniile extrasului în tabelul de note (DS cap.9 v2.102): un rând pe linie — data, suma, descrierea, CUI-ul, potrivirea —, cu „Contează” și
// „Alege facturile” pe fiecare rând (675: ce nu se aplică stă inactiv, cu motivul — la comisionul băncii „Alege facturile” e inactiv: linia
// se contează pe nota propusă, nu stinge o factură, 607); motivul potrivirii, facturile stinse, nota propusă și „Ignoră” / „Readu” în
// detaliul de la clic; explicația fiecărui semn o dată, deasupra; liniile puse deoparte („Ignorată”) grupate în tabelul lor, sub cele de
// lucru. „Alege facturile” deschide fereastra ei (673), cu facturile deschise ale direcției liniei și soldurile preluate la migrare („Sold
// la …”, 669 — aceeași sursă ca în Casă și în Compensări, `reconciliere_api.facturi_deschise`).
const EXPLICATII_BK = {
  fara_potrivire: { atentie: true, titlu: "Fără potrivire",
    text: "linia nu s-a potrivit pe nicio factură după CUI: alege factura cu „Alege facturile” (lista are și soldurile preluate la migrare, „Sold la …”) sau pune linia deoparte cu „Ignoră”, din detaliul ei." },
  de_verificat: { atentie: true, titlu: "Potrivire de verificat",
    text: "potrivirea făcută după descriere nu e sigură: deschide rândul și verifică factura înainte de „Contează”." },
  partial: { atentie: false, titlu: "Potrivire parțială", text: "suma liniei nu acoperă exact facturile găsite: în detaliu e ce se stinge." },
  nota_propusa: { atentie: false, titlu: "Operațiune a băncii",
    text: "linia e recunoscută din descriere (comision, dobândă, TVA …): se contează pe nota propusă, fără factură." },
  nevalidata: { atentie: false, titlu: "Contată, notă nevalidată", text: "nota liniei intră în evidență după validare (Registru jurnal)." },
};
const STARI_BK = [["", "Toate liniile"], ["de_lucru", "De contat"], ["contat", "Contate"], ["ignorat", "Puse deoparte"]];

async function ecranBanca(corp, nav, t) {
  const cheie = "banca:" + t.id;
  const CUL = { verde: "var(--verde)", rosu: "var(--rosu)" };   // [05.10.2026] galben/gri de semafor nu mai colorează text (DS cap.8 v2.70)
  const filtru = { text: "", stare: "" };
  const deschise = new Set();
  corp.innerHTML = `
    <div class="rezumat-fix" id="bk-rezumat">
    <h2 class="pf-titlu">Bancă ${semnAjutor("F011")}</h2>
    <p class="pf-intro">Încarcă extrasul de cont: liniile se potrivesc automat pe facturi după CUI, iar o linie care există deja (aceeași
      dată, sumă, sens, referință sau descriere și același cont) nu se adaugă a doua oară.</p>
    <ul class="pf-intro" id="bk-formate">
      <li><b>MT940</b> (formatul SWIFT al extrasului, fișier .sta, .940 sau .txt), de la orice bancă care îl exportă: se citesc și contul, și
        soldul inițial și final, comparate cu 5121.</li>
      <li><b>ING</b>: extrasul în .xls, .xlsx sau .csv.</li>
      <li><b>Altă bancă</b>: tabel .xls, .xlsx sau .csv cu coloanele Data, Detalii și Debit + Credit (sau o coloană Sumă, cu semn). Din tabel
        nu se citesc soldurile.</li>
    </ul>
    <p><input type="file" id="bk-fisier" aria-label="Fișier extras bancar" accept=".xls,.xlsx,.csv,.sta,.940,.txt,.mt940">
      <span id="bk-cautare-loc" style="margin-left:12px"></span></p>
    <div id="bk-mesaj"></div>
    </div>
    <div id="bk-lista"></div>`;
  const zonaMesaj = corp.querySelector("#bk-mesaj");
  const zonaLista = corp.querySelector("#bk-lista");
  const preia = () => { const st = starePastrata(cheie); if (st && st.mesaj) arataMesaj(zonaMesaj, st.mesaj, "ok"); return !!st; };
  preia();

  // [624] starea liniei (o culoare, un cuvânt) și semnele ei — explicațiile semnelor stau o dată, deasupra tabelului
  const partenerNota = (np) => !!(np && [np.debit, np.credit].some((c) => /^(4111|401)/.test(String(c || ""))));
  const opBanca = (l) => !!(l.nota_propusa && l.nota_propusa.debit && l.nota_propusa.credit && !partenerNota(l.nota_propusa));
  function stareLinie(l) {
    if (l.status === "ignorat") return { fel: "ignorat", text: "Ignorată", culoare: "var(--gri)", semne: [] };
    // [deficiența 309] contată, dar nota nu e încă validată -> nu „Contat ✓” (nota nu e în evidență până o validează cineva)
    // [lotul 11, deficiența 457] starea REALĂ a notei (ciornă / la validare în cabinet / respinsă), din coadă (`reconciliere_api.stare_note_linie`)
    const ns = l.nota_stare;
    if (l.status === "contat") return ns && ns.nota_status !== "validata"
      ? { fel: "contat", text: `Contată · ${stareNotaCasa(ns, t)}${ns.nevalidate > 1 ? ` (${cate(ns.nevalidate, "notă", "note")})` : ""}`, culoare: "var(--galben-text)", semne: [{ fel: "nevalidata", text: "notă nevalidată" }] }
      : { fel: "contat", text: "Contat ✓", culoare: "var(--gri)", semne: [] };
    const inc = (l.alocari || {}).incredere;
    const semnInc = inc === "de_verificat" ? [{ fel: "de_verificat", text: "de verificat" }] : inc ? [{ fel: "incredere", text: inc === "sigur" ? "sigur" : "probabil" }] : [];
    const m = (l.alocari || {}).status_match;
    if (m === "verde") return { fel: "de_lucru", text: "Potrivire exactă", culoare: CUL.verde, semne: semnInc };
    if (m === "galben") return { fel: "de_lucru", text: "Parțial", culoare: "var(--galben-text)", semne: [{ fel: "partial", text: "parțial" }, ...semnInc] };
    // [309] o operațiune recunoscută din descriere (comision, dobândă, TVA…) n-are factură de potrivit: are nota propusă — nu e o eroare
    if (opBanca(l)) return { fel: "de_lucru", text: `Notă propusă ${l.nota_propusa.debit} = ${l.nota_propusa.credit}`, culoare: "var(--gri)", semne: [{ fel: "nota_propusa", text: "operațiune a băncii" }, ...semnInc] };
    return { fel: "de_lucru", text: "Fără potrivire", culoare: CUL.rosu, semne: [{ fel: "fara_potrivire", text: "alege factura" }, ...semnInc] };
  }
  // [675] aceleași butoane pe fiecare linie: „Contează”, „Alege facturile” (pe rând), „Ignoră” / „Readu” (în detaliu)
  function butoaneLinie(l) {
    const np = l.nota_propusa;
    const contPropus = l.status === "nou" && np && np.debit;
    const motivCont = l.status === "contat" ? "Linia e contată: nota ei e în Registrul jurnal."
      : l.status === "ignorat" ? "Linia e pusă deoparte: „Readu” (în detaliul ei) o întoarce la lucru."
      : l.status === "potrivit" || contPropus ? null : "Linia nu s-a potrivit pe nicio factură: alege facturile.";
    const motivAlege = l.status === "contat" ? "Linia e contată: facturile ei sunt stinse."
      : l.status === "ignorat" ? "Linia e pusă deoparte: „Readu” (în detaliul ei) o întoarce la lucru."
      : opBanca(l) ? `Linia e o operațiune a băncii (nota propusă ${np.debit} = ${np.credit}), nu plata unei facturi: se contează pe nota propusă.` : null;   // [607]
    const bCont = butonRand("buton-primar", `data-cont="${l.id}" data-actiune="POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/conteaza"`,
      contPropus && l.status === "nou" ? `Contează ${esc(np.debit)}=${esc(np.credit)}` : "Contează", motivCont);
    const bAlege = butonRand("buton-secundar", `data-alege="${l.id}" data-actiune="POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/conteaza"`, "Alege facturile", motivAlege);
    const bIgn = l.status === "ignorat"
      ? butonRand("buton-secundar bk-undo", `data-id="${l.id}" data-actiune="POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/reactiveaza"`, "Readu", null)
      : butonRand("buton-secundar", `data-ign="${l.id}" data-actiune="POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/ignora"`, "Ignoră",
        l.status === "contat" ? "Linia e contată: nu se mai pune deoparte." : null);
    return { peRand: `${bCont} ${bAlege}`, inDetaliu: bIgn };
  }
  function randLinie(l) {
    const st = stareLinie(l), b = butoaneLinie(l), k = String(l.id);
    const deschis = deschise.has(k);
    const al = ((l.alocari || {}).alocari || []);
    const np = l.nota_propusa;
    const obs = [
      `Descrierea din extras: ${esc(l.descriere || "fără descriere")}`,
      (l.alocari || {}).motiv ? `Potrivirea: ${esc((l.alocari || {}).motiv)}` : "",
      ...al.map((a) => { const f = a.factura || {}; return `Stinge ${esc(f.numar ? numarCuSerie(f.serie, f.numar) : "factură fără număr")} · ${esc(f.tert || "")} · ${bani(a.suma)} lei`; }),
      np && np.debit && np.credit ? `Nota propusă: ${esc(np.debit)} = ${esc(np.credit)}` : "",
      (l.alocari || {}).incredere ? `Încrederea potrivirii: ${esc({ sigur: "sigur", de_verificat: "de verificat" }[(l.alocari || {}).incredere] || "probabil")}` : "",
    ].filter(Boolean).map((x) => `<p class="pf-frand-sub">${x}</p>`).join("");
    return `<tbody class="tn-nota" data-tn="${esc(k)}" data-linie-id="${l.id}">
      <tr class="tn-rand${deschis ? " tn-deschis" : ""}">
        <td><button type="button" class="btn-link tn-deschide" aria-expanded="${deschis}" aria-controls="bk-det-${esc(k)}" aria-label="Detaliul liniei din ${esc(dataRo(l.data))}">${esc(dataRo(l.data))}</button></td>
        <td class="fd-td-num">${l.tip === "plata" ? "−" : "+"}${bani(l.suma)}</td>
        <td>${esc(textScurt(l.descriere, 90))}</td>
        <td>${esc(l.cui_detectat || "")}</td>
        <td><span class="bk-stare" style="color:${st.culoare};font-weight:600">● ${esc(st.text)}</span>${st.semne.map((s) => `<div class="tip-desc tn-semn" data-semn="${esc(s.fel)}">${esc(s.text)}</div>`).join("")}</td>
        <td class="tn-actiuni">${b.peRand}</td>
      </tr>
      <tr class="tn-detaliu" id="bk-det-${esc(k)}"${deschis ? "" : " hidden"}><td colspan="6">${obs}<p class="tn-detaliu-actiuni">${b.inDetaliu}</p></td></tr>
    </tbody>`;
  }
  const randFiltru = (l) => { const st = stareLinie(l); const al = ((l.alocari || {}).alocari || []);
    return { cheie: String(l.id), data: l.data, explicatie: l.descriere || "", partener: [l.cui_detectat, ...al.map((a) => (a.factura || {}).tert)].filter(Boolean).join(" "),
      document: al.map((a) => (a.factura || {}).numar ? numarCuSerie((a.factura || {}).serie, a.factura.numar) : "").join(" "), rulaj: Number(l.suma),
      stare: { text: st.text }, semne: st.semne, stari: [st.fel], cautaInPlus: l.nota_propusa ? `${l.nota_propusa.debit} = ${l.nota_propusa.credit}` : "" }; };
  const tabelLinii = (pre, linii) => `<table class="fd-tabel tn-tabel" id="${pre}-tabel">
      <thead><tr><th>Data</th><th class="fd-td-num">Suma (lei)</th><th>Descriere</th><th>CUI</th><th>Potrivire</th><th>Acțiune</th></tr></thead>
      ${linii.map(randLinie).join("")}</table>
    <div class="stare-goala" id="${pre}-nimic" hidden>Nicio linie nu se potrivește căutării. Schimbă textul căutat sau starea aleasă.</div>`;

  let liniiAfisate = [];   // [lotul 12, C150] linia contată se numește în confirmare
  // „Linia din 28.09.2026, −1.210,00 lei (Plata chirie septembrie): ” — două contări din aceeași zi nu mai primesc același text
  const ceLinie = (l) => l ? `Linia din ${esc(dataRo(l.data))}, ${l.tip === "plata" ? "−" : "+"}${bani(l.suma)} lei${l.descriere ? ` (${esc(textScurt(l.descriere, 60))})` : ""}: ` : "";

  function randeaza(linii) {
    liniiAfisate = linii;
    const loc = corp.querySelector("#bk-cautare-loc");
    if (!linii.length) { loc.innerHTML = ""; zonaLista.innerHTML = `<div class="stare-goala">Nicio linie de extras. Încarcă un fișier.</div>`; return; }
    const lucru = linii.filter((l) => l.status !== "ignorat"), deoparte = linii.filter((l) => l.status === "ignorat");
    // [624] explicațiile semnelor, o dată, cu numărul liniilor
    const nr = {};
    linii.forEach((l) => stareLinie(l).semne.forEach((s) => { nr[s.fel] = (nr[s.fel] || 0) + 1; }));
    const chei = Object.keys(EXPLICATII_BK).filter((k) => nr[k]);
    const expl = (k) => `<div class="${EXPLICATII_BK[k].atentie ? "ca-mesaj" : "ci-mesaj"} tn-explicatie" id="bk-expl-${k}"><b>${esc(EXPLICATII_BK[k].titlu)} (${nr[k]}):</b> ${esc(EXPLICATII_BK[k].text)}</div>`;
    const at = chei.filter((k) => EXPLICATII_BK[k].atentie), inf = chei.filter((k) => !EXPLICATII_BK[k].atentie);
    loc.innerHTML = htmlCautare("bk", { stari: STARI_BK, valoare: filtru.text, stare: filtru.stare, eticheta: "Caută: sumă, CUI, descriere, factură" });
    zonaLista.innerHTML = `${chei.length ? `<div class="tn-explicatii" id="bk-explicatii">${at.length ? `<div class="caseta-atentie">${at.map(expl).join("")}</div>` : ""}${inf.length ? `<div class="caseta-info">${inf.map(expl).join("")}</div>` : ""}</div>` : ""}
      <div id="bk-lucru">${lucru.length ? tabelLinii("bk", lucru) : `<div class="stare-goala" id="bk-gol">Nicio linie de contat: toate sunt contate sau puse deoparte.</div>`}</div>
      ${deoparte.length ? `<div id="bk-deoparte"><h3 class="pf-subtitlu" id="bk-deoparte-titlu">Linii puse deoparte (${deoparte.length})</h3>
        <p class="tip-desc">Nu se contează; „Readu”, din detaliul liniei, o întoarce la lucru.</p>${tabelLinii("bk-dp", deoparte)}</div>` : ""}`;
    // fiecare tabel cu legătura lui (filtrarea unuia nu ascunde rândurile celuilalt)
    const tn = [lucru.length ? legaTabelNote(zonaLista.querySelector("#bk-lucru"), { pre: "bk", randuri: lucru.map(randFiltru), deschise }) : null,
      deoparte.length ? legaTabelNote(zonaLista.querySelector("#bk-deoparte"), { pre: "bk-dp", randuri: deoparte.map(randFiltru), deschise }) : null].filter(Boolean);
    const aplicaFiltru = () => {
      let v = 0, tot = 0;
      tn.forEach((x) => { const r = x.filtreaza(filtru.text, filtru.stare); v += r.vazute; tot += r.total; });
      const z = corp.querySelector("#bk-numar");
      if (z) z.textContent = filtru.text || filtru.stare ? textNumar(v, tot, "linie", "linii") : "";
    };
    aplicaFiltru();
    const cCauta = corp.querySelector("#bk-cauta"), cStare = corp.querySelector("#bk-stare");
    if (cCauta) cCauta.addEventListener("input", () => { filtru.text = cCauta.value; aplicaFiltru(); });
    if (cStare) cStare.addEventListener("change", () => { filtru.stare = cStare.value; aplicaFiltru(); });
    zonaLista.querySelectorAll("[data-cont]").forEach((b) =>
      b.addEventListener("click", () => conteaza(parseInt(b.dataset.cont), null)));
    zonaLista.querySelectorAll("[data-ign]").forEach((b) =>
      b.addEventListener("click", async () => {
        try { await api.post(`/tenants/${t.id}/banca/reconciliere/${b.dataset.ign}/ignora`, {}); arataMesaj(zonaMesaj, `${ceLinie(liniiAfisate.find((x) => x.id === Number(b.dataset.ign)))}pusă deoparte (o găsești la „Linii puse deoparte”).`, "ok"); incarca(); }
        catch (e) { refuzPeRand(b, e.mesaj || "Eroare."); }
      }));
    zonaLista.querySelectorAll(".bk-undo").forEach((b) =>
      b.addEventListener("click", async () => {
        try { await api.post(`/tenants/${t.id}/banca/reconciliere/${b.dataset.id}/reactiveaza`, {}); arataMesaj(zonaMesaj, `${ceLinie(liniiAfisate.find((x) => x.id === Number(b.dataset.id)))}readusă la lucru.`, "ok"); incarca(); }
        catch (e) { refuzPeRand(b, e.mesaj || "Eroare."); }
      }));
    // [673] alegerea facturilor: fereastra ei; după contare se închide, iar Banca se redesenează cu confirmarea
    zonaLista.querySelectorAll("[data-alege]").forEach((b) =>
      b.addEventListener("click", () => {
        const l = linii.find((x) => x.id === parseInt(b.dataset.alege));
        if (l) deschideActiunea(nav, cheie, {}, "Alege facturile", (c2) => ecranAlegeFacturiBanca(c2, nav, t, cheie, l, ceLinie(l)));
      }));
  }

  const cerereLinii = ultimaCerere();   // [C103] liniile reîncărcate după importuri / contări în șir: numai lista cerută ultima ajunge pe ecran
  async function incarca() {
    const actuala = cerereLinii();
    try {
      const r = await api.get(`/tenants/${t.id}/banca/reconciliere`);
      if (!actuala()) return;
      randeaza(r.linii || []);
    } catch { if (!actuala()) return; arataMesaj(zonaLista, "Nu s-au putut încărca liniile.", "eroare"); }
  }

  async function conteaza(id, alocari) {
    zonaMesaj.innerHTML = "";
    try {
      const r = await api.post(`/tenants/${t.id}/banca/reconciliere/${id}/conteaza`, alocari ? { alocari } : {});
      arataMesaj(zonaMesaj, mesajContareBanca(r, ceLinie(liniiAfisate.find((x) => x.id === id))), "ok");
      incarca();
    } catch (e) { arataMesaj(zonaMesaj, e.mesaj || "Eroare la contare", "eroare"); }
  }

  // [lotul 12, C121] extrasul altui cont decât al firmei: serverul nu scrie nimic și întreabă (`cere_confirmare`); importul se reia numai
  // după „Da, e extrasul acestei firme” (avertismentul galben sus, ca la fișierul altei firme din migrare — 599)
  const importa = async (f, confirmaCont) => {
    zonaMesaj.innerHTML = `<p class="ecran-nota">Se citește și se potrivește extrasul...</p>`;
    const fd = new FormData();
    fd.append("fisier", f);
    if (confirmaCont) fd.append("confirma_cont", "true");
    try {
      // [R131] prin `api.postForm`, care e deja instrumentat: refuzul serverului (format
      // necunoscut, fisier ilizibil) ajunge la om cu motivul lui, nu ca „Nu s-a putut citi".
      const r = await api.postForm(`/tenants/${t.id}/banca/reconciliere/import`, fd);
      if (r.cere_confirmare && !confirmaCont) {
        arataMesaj(zonaMesaj, r.cere_confirmare.mesaj, "avert");
        confirmaCaseta(zonaMesaj, esc(r.cere_confirmare.intrebare), () => importa(f, true), { textOk: "Da, e extrasul acestei firme" });
        return;
      }
      // [16.10.2026, lotul 6 pct.1c, 277] serverul hotărăște duplicatul pe MIȘCARE (dată, sumă, sens, cont, referință / descriere);
      // mesajul spune ce linii au fost găsite deja și ce linii sunt noi. [05.10.2026 pct.8] noile se numără: potrivite / fără potrivire.
      const z = r.rezumat || { noi: (r.linii || []).length, deja: 0, potrivite: 0, fara_potrivire: 0 };
      const linieExtras = (d) => `  ${dataRo(d.data)} · ${bani(d.suma)} lei · ${d.tip === "incasare" ? "încasare" : "plată"} · ${d.descriere || "fără descriere"}`;
      const randuri = [];
      if (z.noi) randuri.push(`${cate(z.noi, "linie importată", "linii importate")}: ${cate(z.potrivite, "potrivită", "potrivite")} pe facturi, ${z.fara_potrivire} fără potrivire (alege factura sau contează pe nota propusă).`);
      else randuri.push("Nicio linie nouă: nu s-a adăugat nimic.");
      if (z.deja) randuri.push(`${cate(z.deja, "linie găsită deja", "linii găsite deja")} (aceeași mișcare există, nu s-a adăugat din nou):`, ...(r.deja || []).map(linieExtras));
      // [lotul 12, 479] aceeași mișcare venită din alt format (tabel <-> MT940): adăugată, dar pusă deoparte („Ignorată”, cu «readu»)
      if (z.probabil_deja) randuri.push(`${cate(z.probabil_deja, "linie pare deja importată", "linii par deja importate")} din alt extras (aceeași dată, sumă și sens; un extras are contul băncii, celălalt nu): ${z.probabil_deja === 1 ? "pusă" : "puse"} deoparte, ca «Ignorată», ca să nu se conteze de două ori. Dacă e altă mișcare, apasă «Readu» în detaliul liniei, la „Linii puse deoparte”:`, ...(r.probabil_deja || []).map(linieExtras));
      randuri.push(...randuriSolduri(r.solduri));
      const dif = r.solduri && ["initial", "final"].some((k) => r.solduri[k] && Number(r.solduri[k].diferenta || 0) !== 0);
      arataMesaj(zonaMesaj, randuri.join("\n"), z.noi && !dif && !z.probabil_deja ? "ok" : "avert");
      incarca();
    } catch (e) { arataMesaj(zonaMesaj, (e && (e.mesaj || e.message)) || "eroare", "eroare"); }
  };
  corp.querySelector("#bk-fisier").addEventListener("change", async (ev) => {
    const f = ev.target.files[0];
    if (!f) return;
    await importa(f, false);
    ev.target.value = "";
  });
  // [673] Banca păstrată (omul scrisese în căutare) se redesenează ea la închiderea ferestrei „Alege facturile”, cu confirmarea
  corp.addEventListener("nav:revenire", () => { if (preia()) incarca(); });
  incarca();
}

// [05.10.2026, comanda Costin pct.8] mesajul contării spune exact ce s-a creat: nota, câte, în ce stare și unde se validează; [lotul 12, C150]
// precedat de linia contată
function mesajContareBanca(r, pre) {
  const n = (r.inregistrari || []).length;
  const mesaj = n === 1
    ? `Notă ${r.nota} creată (${esc((r.note_etichete || [])[0] || "")}, ${stareNota(r)}). ${pasNota(r)}`
    : `${cate(n, `notă ${r.nota} creată`, `note ${r.nota} create`)} (${esc((r.note_etichete || []).join(", "))}, ${stareNota(r, true)}). ${pasNota(r, true)}`;
  return pre ? pre + mesaj.charAt(0).toLowerCase() + mesaj.slice(1) : mesaj;
}

// [lotul 13, 673 / 669] „Alege facturile” al unei linii de extras — fereastra ei: facturile deschise ale direcției liniei (emise la încasare,
// primite la plată), cu soldurile preluate la migrare („Sold la …”); suma liniei se împarte pe cele bifate, în ordinea din listă
async function ecranAlegeFacturiBanca(corp, nav, t, cheie, l, pre) {
  const inc = l.tip === "incasare";
  corp.innerHTML = `<p class="ecran-nota">Se încarcă facturile deschise...</p>`;
  let facturi = [];
  try {
    const r = await api.get(`/tenants/${t.id}/banca/reconciliere/facturi-deschise`);
    facturi = (r.facturi || []).filter((f) => f.directie === (inc ? "emisa" : "primita"));
  } catch (e) {
    corp.innerHTML = `<h2 class="pf-titlu">Alege facturile</h2><div id="bk-pk-mesaj"></div>`;
    arataMesaj(corp.querySelector("#bk-pk-mesaj"), (e && e.mesaj) || "Nu s-au putut încărca facturile.", "eroare");
    return;
  }
  corp.innerHTML = `
    <div class="rezumat-fix"><h2 class="pf-titlu">Alege facturile · linia din ${esc(dataRo(l.data))}, ${inc ? "+" : "−"}${bani(l.suma)} lei</h2>
      <p class="pf-intro">${inc ? "Facturile emise neîncasate" : "Facturile primite neplătite"} și soldurile preluate la migrare („Sold la …”): bifează ce stinge linia; suma se împarte pe ele în ordinea din listă.</p></div>
    ${facturi.length ? `<table class="fd-tabel" id="bk-pk-tabel"><thead><tr><th>Alege</th><th>Factură</th><th>Partener</th><th>CUI</th><th>Data</th><th class="fd-td-num">Rămas (lei)</th></tr></thead>
      <tbody>${facturi.map((f) => `<tr><td><input type="checkbox" data-fid="${f.id}" data-sold="${f.sold}" aria-label="Alege ${esc(numarCuSerie(f.serie, f.numar))}"></td>
        <td>${numeDocDeschis(cuSerieSiNumar(f), false)}</td><td>${esc(f.tert_nume || "")}</td><td>${esc(f.tert_cui || "")}</td><td>${dataRo(f.data_emitere)}</td><td class="fd-td-num">${bani(f.sold)}</td></tr>`).join("")}</tbody></table>`
      : `<div class="stare-goala" id="bk-pk-gol">${inc ? "Nicio factură emisă neîncasată" : "Nicio factură primită neplătită"} și niciun sold preluat deschis.</div>`}
    <div class="bara-fixa"><p class="dec-bara"><button class="buton-primar" id="bk-pk-ok" data-actiune="POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/conteaza"${facturi.length ? "" : atributeInactiv("Nu e nicio factură deschisă de ales pe această direcție.")}>Contează selectate</button>
      <button type="button" class="buton-secundar" id="bk-pk-nu" data-fara-actiune="închide fereastra, fără scriere" style="margin-left:6px">Renunță</button></p>
    <div id="bk-pk-mesaj"></div></div>`;
  corp.querySelector("#bk-pk-nu").addEventListener("click", () => nav.inapoi());
  corp.querySelector("#bk-pk-ok").addEventListener("click", async () => {
    const zm = corp.querySelector("#bk-pk-mesaj");
    let rest = parseFloat(l.suma);
    const aloc = [];
    corp.querySelectorAll("input[data-fid]:checked").forEach((c) => {
      if (rest <= 0.005) return;
      const parte = Math.min(parseFloat(c.dataset.sold), rest);
      aloc.push({ factura_id: parseInt(c.dataset.fid), suma: parte.toFixed(2) });
      rest -= parte;
    });
    if (!aloc.length) { arataMesaj(zm, "Bifează cel puțin o factură.", "eroare"); return; }
    try {
      const r = await api.post(`/tenants/${t.id}/banca/reconciliere/${l.id}/conteaza`, { alocari: aloc });
      inchideCuConfirmarea(nav, cheie, mesajContareBanca(r, pre));
    } catch (e) { arataMesaj(zm, (e && e.mesaj) || "Eroare la contare", "eroare"); }
  });
}

/* Confirmarea crearii unei firme. Acelasi mecanism ca bannerul de la confirmarea adresei
   (app.js): un act care schimba starea si nu spune nimic il face pe om sa-l repete. */


// [R72, 27.08.2026] Scoaterea unei firme din portofoliu.
// Instanța: două firme `PROBA PORTAL SRL` create din greșeală au rămas în portofoliu fiindcă nu
// exista nicio cale de a le scoate. Iar duplicatul a costat în aceeași zi — un ecran corect
// („Niciun cont de client încă") a fost citit ca fals, fiindcă se deschisese cealaltă firmă.
// De aceea confirmarea de aici e pe CUI, NU pe nume: numele se pot repeta, CUI-ul nu.
async function ecranScoateFirma(corp, nav, t) {
  corp.innerHTML = `<p class="ecran-nota" id="sf-stare">Se verifică ce a produs firma…</p>
                    <div id="sf-corp"></div><div id="sf-mesaj"></div>`;
  const zonaM = corp.querySelector("#sf-mesaj");
  let p;
  try { p = await api.get(`/tenants/${t.id}/scoatere`); }
  catch (e) {
    arataMesaj(corp.querySelector("#sf-stare"),
               e.mesaj || e.message || "Nu s-a putut verifica firma.", "eroare");
    return;
  }
  corp.querySelector("#sf-stare").remove();
  const zona = corp.querySelector("#sf-corp");
  const cap = `<h3 style="margin:0 0 4px">${esc(p.nume || "")}</h3>
               <p class="ecran-nota" style="margin:0 0 16px">CUI ${esc(String(p.cui || "—"))}</p>`;

  if (p.se_poate_sterge) {
    // [R50 (c)] Ce dispare, numărat înainte de apăsare. O ștergere care spune doar „se șterge
    // tot" nu se poate confrunta cu nimic după.
    const cl = p.clienti_de_dezactivat || [];
    const ceCuClientii = cl.length
      ? `<p class="ecran-nota" style="margin:10px 0 0"><strong>${cate(cl.length, "cont de client", "conturi de client")}</strong>
           ${cl.length === 1 ? "rămâne" : "rămân"} fără nicio firmă și ${cl.length === 1 ? "va fi dezactivat" : "vor fi dezactivate"}:
           ${cl.map((c) => esc(c.email)).join(" · ")}. Contul nu se șterge — persoana nu e a firmei —
           dar nu mai poate intra în portal.</p>`
      : "";
    // [C123, lotul 12] asistenții cabinetului care lucrau numai firma asta: ștergerea le aplică regula „zero firme” (contul se
    // dezactivează, competențele se golesc, rămâne în istoric) — spus înainte de apăsare, cu numele lor
    const asi = p.asistenti_de_dezactivat || [];
    const ceCuAsistentii = asi.length
      ? `<p class="ecran-nota" id="sf-asistenti" style="margin:10px 0 0">${asi.length === 1 ? "Asistentul" : "Asistenții"}
           ${asi.map((a) => `<strong>${esc(a.nume || a.email)}</strong>`).join(", ")}
           ${asi.length === 1 ? "rămâne fără nicio firmă, deci contul se dezactivează" : "rămân fără nicio firmă, deci conturile lor se dezactivează"}:
           competențele se golesc, iar contul rămâne în istoric. Îl reactivează administratorul din Asistenți, cu firmele alese din nou.</p>`
      : "";
    // [C136, lotul 12] ce mai dispare, în cuvintele contabilului (textul serverului, `tenant_stergere.ce_dispare`), nu numele tabelelor
    const ce = p.ce_dispare || [];
    const ceDispare = ce.length
      ? `<p class="ecran-nota" id="sf-ce-dispare" style="margin:10px 0 0">Dispar și: ${ce.map((x) => esc(x)).join(" · ")}, plus toate datele contabile ale firmei.</p>`
      : `<p class="ecran-nota" id="sf-ce-dispare" style="margin:10px 0 0">Dispar numai datele contabile ale firmei.</p>`;
    zona.innerHTML = `${cap}
      <div class="caseta-atentie">
        <div class="ca-mesaj"><strong>Act ireversibil.</strong> Firma nu a produs niciun document:
          nicio declarație depusă sau în coadă, nicio notă contabilă, factură, chitanță sau stat de
          plată. Se poate scoate cu totul. <strong>Ștergerea nu se poate întoarce</strong> — datele
          firmei dispar cu totul din aplicație, iar backupul off-site nu se poate șterge selectiv.</div>
      </div>
      ${ceDispare}
      ${ceCuClientii}
      ${ceCuAsistentii}
      ${(() => {
        const u = p.urme_de_pastrat || {};
        const n = Object.values(u).reduce((a, b) => a + b, 0);
        return n
          ? `<p class="ecran-nota" style="margin:10px 0 0">Se <strong>păstrează</strong> ${cate(n, "urmă", "urme")}
               de portal (cine a primit acces, ce adresă s-a schimbat și când). Le găsești după
               ștergere sub „Firme scoase".</p>`
          : "";
      })()}
      <div class="camp" style="margin:14px 0">
        <label class="camp-eticheta" for="sf-cui">Scrie CUI-ul firmei ca să confirmi</label>
        <input class="camp-input" id="sf-cui" autocomplete="off" placeholder="${esc(String(p.cui || ""))}">
        <p class="camp-ajutor">Se cere CUI-ul, nu numele: două firme pot avea același nume.</p>
      </div>
      <button class="buton-primar" id="sf-sterge" data-actiune="DELETE /tenants/{tenant_id}" disabled>Scoate firma definitiv</button>
      <p class="ecran-nota" style="margin:16px 0 6px"><strong>Sau, dacă vrei doar s-o scoți din
         listă:</strong> dezactivarea e <strong>reversibilă</strong> — firma iese din portofoliul
         de lucru, datele rămân neatinse, iar de sub „Firme dezactivate" o poți aduce înapoi
         oricând. Ștergerea de mai sus <strong>nu se poate întoarce</strong>.</p>
      <button class="buton-secundar" id="sf-dezactiveaza-2" data-actiune="POST /tenants/{tenant_id}/activare">Dezactivează firma (reversibil)</button>`;
    const bDez2 = zona.querySelector("#sf-dezactiveaza-2");
    bDez2.addEventListener("click", async () => {
      bDez2.disabled = true; bDez2.textContent = "Se dezactivează…";
      try {
        await api.post(`/tenants/${t.id}/activare`, { activ: false });
        nav.acasa();
        nav.setFirmaInLucru("");
        _bannerFirma(`<b>${esc(t.nume || "Firma")}</b> a fost dezactivată — iese din portofoliul de
           lucru, iar datele ei rămân neatinse. O aduci înapoi din „Firme dezactivate".`);
      } catch (e) {
        bDez2.disabled = false; bDez2.textContent = "Dezactivează firma (reversibil)";
        arataMesaj(zonaM, e.mesaj || e.message || "Nu s-a putut dezactiva firma.", "eroare");
      }
    });
    const inp = zona.querySelector("#sf-cui"), btn = zona.querySelector("#sf-sterge");
    inp.addEventListener("input", () => {
      btn.disabled = inp.value.trim() !== String(p.cui || "").trim();
    });
    btn.addEventListener("click", async () => {
      btn.disabled = true; btn.textContent = "Se scoate…";
      try {
        await api.del(`/tenants/${t.id}?confirmare=${encodeURIComponent(inp.value.trim())}`);
        nav.acasa();
        nav.setFirmaInLucru("");
        // Cel mai puțin reversibil act al aplicației — deci cel la care confirmarea e cea mai
        // obligatorie (DS cap.27).
        //
        // [BB1, 28.08.2026] Textul e al lui Costin. Ce spuneam eu — *„datele ei nu mai există"* —
        // era prea tare: schema chiar se șterge, dar rândul din `firme_scoase` rămâne, iar
        // formularea lui e mai exactă (*nu mai sunt ACCESIBILE*) și numește ce rămâne, nu ce a
        // dispărut. Numele firmei stă în față, fiindcă textul lui e generic: fără el, banner-ul ar
        // confirma **un act**, nu **actul asupra firmei ăsteia** (DS cap.27 cere entitatea).
        //
        // [CC1] `autoDismiss=false`: singurul din cele cinci care nu dispare singur.
        _bannerFirma(`<b>${esc(t.nume || "Firma")}</b> — scoasă definitiv din portofoliu.
           Datele fiscale ale firmei nu mai sunt accesibile. Rămâne doar înregistrarea scoaterii,
           vizibilă la „Firme scoase".`, false);
      } catch (e) {
        btn.disabled = false; btn.textContent = "Scoate firma definitiv";
        arataMesaj(zonaM, e.mesaj || e.message || "Nu s-a putut scoate firma.", "eroare");
      }
    });
    return;
  }

  // Are evidență: nu se șterge. Se SPUNE ce s-a găsit — un refuz fără motiv nu se poate verifica.
  const motive = (p.evidenta && p.evidenta.motive) || [];
  zona.innerHTML = `${cap}
    <div class="caseta-atentie">
      <div class="ca-mesaj">Firma <strong>nu se poate șterge</strong>: a produs documente care au
        ajuns la cineva din afară. Ce s-a găsit:
        <ul style="margin:8px 0 0 18px">${motive.map((m) => `<li>${esc(m)}</li>`).join("")}</ul>
      </div>
    </div>
    <p class="ecran-nota" style="margin:14px 0">O poți <strong>dezactiva</strong> — act
       <strong>reversibil</strong>: iese din portofoliul de lucru, documentele rămân neatinse, iar
       de sub „Firme dezactivate" o aduci înapoi oricând, în starea de dinainte.</p>
    <button class="buton-primar" id="sf-dezactiveaza" data-actiune="POST /tenants/{tenant_id}/activare">Dezactivează firma (reversibil)</button>`;
  zona.querySelector("#sf-dezactiveaza").addEventListener("click", async () => {
    const b = zona.querySelector("#sf-dezactiveaza");
    b.disabled = true; b.textContent = "Se dezactivează…";
    try {
      await api.post(`/tenants/${t.id}/activare`, { activ: false });
      nav.acasa();
      nav.setFirmaInLucru("");
      _bannerFirma(`<b>${esc(t.nume || "Firma")}</b> a fost dezactivată — iese din portofoliul de
         lucru, iar documentele ei rămân neatinse. O aduci înapoi din „Firme dezactivate".`);
    } catch (e) {
      b.disabled = false; b.textContent = "Dezactivează firma (reversibil)";   // [327, clasa] eticheta de dinainte, întocmai
      arataMesaj(zonaM, e.mesaj || e.message || "Nu s-a putut dezactiva firma.", "eroare");
    }
  });
}




// [R72, 27.08.2026] Urma firmelor scoase — CITITĂ, nu doar scrisă.
// `public.firme_scoase` era, în ziua în care s-a construit, a doua instanță a clasei declarate
// dimineață la `urme-portal`: scrisă, necitită de om. Ecranul ăsta o închide.
function randeazaFirmeScoase(corp, scoase) {
  if (!scoase.length) {
    corp.innerHTML = `<p class="ecran-nota">Nicio firmă scoasă din portofoliu.</p>`;
    return;
  }
  const rand = (f) => {
    const up = (f.urme_pastrate || {}).urme_portal || [];
    const se = (f.urme_pastrate || {}).schimbari_email || [];
    return `
      <div class="firme-rand" style="display:block;cursor:default">
        <div class="firme-rand-nume">${esc(f.nume || "(fără nume)")}</div>
        <div class="firme-rand-cui">CUI ${esc(String(f.cui || "—"))}</div>
        <p class="ecran-nota" style="margin:6px 0 0">
          Scoasă la <strong>${esc(dataRo(f.scos_la, "cu_ora"))}</strong>
          de <strong>${esc(f.scos_de || "utilizator șters")}</strong>
          ${f.motiv === "gdpr_cabinet" ? "· prin ștergerea cabinetului (GDPR)" : ""}
        </p>
        <p class="ecran-nota" style="margin:6px 0 0">S-au curățat: ${(f.curatate || []).length ? f.curatate.map((x) => esc(x)).join(" · ") : "numai datele contabile ale firmei"}, plus datele contabile ale firmei.</p>
        ${up.length || se.length ? `
          <details style="margin-top:8px">
            <summary style="cursor:pointer">Urme păstrate din portal (${up.length + se.length})</summary>
            <ul style="margin:8px 0 0 18px">
              ${up.map((u) => `<li><strong>${esc(u.actiune)}</strong> — ${esc(u.detaliu)}
                    <span class="ecran-nota">(${esc(dataRo(u.creat_la, "cu_ora"))})</span></li>`).join("")}
              ${se.map((s) => `<li><strong>schimbare de adresă</strong> — ${esc(s.email_vechi)} →
                    ${esc(s.email_nou)} <span class="ecran-nota">(cerută ${esc(dataRo(s.cerut_la, "cu_ora"))}${
                      s.confirmat_la ? ", confirmată " + esc(dataRo(s.confirmat_la, "cu_ora")) : ", neconfirmată"})</span></li>`).join("")}
            </ul>
          </details>` : `<p class="ecran-nota" style="margin:6px 0 0">Nicio urmă de portal păstrată.</p>`}
      </div>`;
  };
  corp.innerHTML = `
    <p class="ecran-nota">Firmele de aici nu mai există. Rândul rămâne ca dovadă că au existat,
       cine le-a scos și ce s-a curățat odată cu ele. Urmele de portal se păstrează la scoaterea
       din portofoliu; la o ștergere GDPR nu se păstrează nimic.</p>
    <div class="firme-lista">${scoase.map(rand).join("")}</div>`;
}


// [R82/AA1, 28.08.2026] Confirmarea care SUPRAVIEȚUIEȘTE navigării.
//
// Regula (DS cap.27, E2): *un act cu efect asupra unei entități se încheie cu o confirmare vizibilă
// care numește entitatea și consecința. Demontarea ecranului NU e confirmare.* Cele patru acte de
// nivel firmă se terminau toate cu `nav.acasa()` — adică ecranul dispărea, iar „a dispărut" arăta
// identic cu „a reușit" și cu „s-a rupt ceva".
//
// Un `arataMesaj` obișnuit n-ar fi ținut: zona lui e demontată odată cu ecranul. De-aia banner-ul
// stă pe `document.body`, în afara oricărui ecran — exact mecanismul construit pe 26.08 pentru
// crearea firmei, acum generalizat. **Zero clase noi**: `caseta-info` / `ci-mesaj`, ca înainte.
// [CC1, 28.08.2026] `autoDismiss` — implicit `true`, ca până acum. Pe `false`, banner-ul **nu
// dispare singur** și primește un „✕".
//
// De ce nu la toate: o confirmare care rămâne pe ecran până o închizi e utilă exact cât e actul de
// greu de întors. La o dezactivare — reversibilă dintr-un click — un banner care persistă ar deveni
// zgomot, iar zgomotul se învață să nu mai fie citit (aceeași grijă ca la alerte, R73). La o
// **scoatere definitivă**, opusul: cine se uită în altă parte opt secunde pierde singura confirmare
// a unui act pe care nu-l mai poate întoarce.
//
// **Zero clase noi**: `nav-x` e butonul de închidere folosit deja de fereastra de lucru și de
// ecranele de acces (`static/stil.css`). Poziționarea e inline, ca restul banner-ului, care oricum
// trăiește în afara oricărui ecran.
function _bannerFirma(html, autoDismiss = true) {
  const vechi = document.getElementById("firma-creata-bine");
  if (vechi) vechi.remove();
  const b = document.createElement("div");
  b.id = "firma-creata-bine";
  b.className = "caseta-info";
  // [LL1, 28.08.2026] LATIME EXPLICITA. Un element `position:fixed` fara latime se stange la
  // continut, iar pe telefon asta insemna o coloana de 188 px din 375 — text rupt in 15 randuri,
  // lizibil dar inghesuit (masurat la 375 px, II). `calc(100% - 32px)` ii da latimea disponibila,
  // minus o margine de o parte si de alta; `max-width` il tine la 520 pe ecran mare, deci desktopul
  // ramane exact cum era.
  b.style.cssText = "position:fixed;left:50%;top:16px;transform:translateX(-50%);z-index:99999;"
    + "width:calc(100% - 32px);max-width:min(520px,92vw)"
    + (autoDismiss ? "" : ";padding-right:44px");
  b.innerHTML = `<div class="ci-mesaj">${html}</div>`
    // [FF1, 28.08.2026] Starea de REPAUS a butonului. `nav-x` e hover-only, si acolo e corect:
    // in fereastra de lucru „✕" e redundant (ai si Escape, si click in afara, si butonul de inapoi).
    // Aici e SINGURA iesire — banner-ul nu mai dispare singur —, iar un „✕" pe care nu-l vezi
    // transforma o confirmare intr-un obstacol. Contur + fundal alb, pe tokeni, nu culori scrise
    // de mana. Restul locurilor unde se foloseste `nav-x` raman NEATINSE.
    + (autoDismiss ? "" : `<button type="button" class="nav-x" id="firma-banner-x"
         style="position:absolute;top:6px;right:6px;background:var(--alb);border:1px solid var(--linie)"
         title="Închide" aria-label="Închide">✕</button>`);
  document.body.appendChild(b);
  if (autoDismiss) {
    setTimeout(() => { if (b.parentNode) b.remove(); }, 8000);
  } else {
    b.querySelector("#firma-banner-x").addEventListener("click", () => b.remove());
  }
  return b;
}

function _bannerFirmaCreata(nume) {
  return _bannerFirma(`Firma <b>${esc(nume)}</b> a fost creată și apare în listă.`);
}

// [368, lotul 9] ce se întâmplă cu un Z la PFA, spus o singură dată (Z-ul scris și importul AMEF)
const zInRip = (numerar, card) => (Number(numerar) > 0
  ? `Numerarul (${bani(numerar)} lei) e în registrul de încasări și plăți, ca încasare de validat (cardul Încasări/plăți).`
  : "Raportul nu are numerar: în registrul de încasări și plăți nu s-a scris nimic.")
  + (Number(card) > 0 ? ` Cardul (${bani(card)} lei) intră în registru când banii ajung în cont, din extrasul de bancă.` : "");

// [horeca] Raport Z zilnic
async function ecranRaportZ(corp, nav, t) {
  const azi = dataIso();
  // [lotul 11, comanda 11.1 pct.23] „etichetele «mâncare» / «alcool» și «Consum pe rețetă» la firme de comerț”: ele sunt ale alimentației
  // publice. Criteriul e regula existentă a ecranului Stocuri (`stocuri_cv_api.retete_vizibile`: CAEN-ul HoReCa din CF art.48 alin.(2^2) /
  // art.54 alin.(4), `core/horeca.py`, sau rețete deja definite); la comerț, cotele rămân neutre („Total 11%”, „Total 21%”).
  // [lotul 12, deficiența 473] etichetele cotelor („mâncare”, „alcool, sucuri” — CF art.291 alin.(2) lit.n: restaurantul și cateringul la
  // cota redusă, „cu excepția băuturilor alcoolice, precum și a băuturilor nealcoolice care se încadrează la codul NC 2202”) descriu
  // ACTIVITATEA: numai după CAEN-ul HoReCa (`alimentatie_publica`, `core/horeca.py`), nu după existența unor rețete — o firmă de comerț cu
  // rețete importate din greșeală le arăta. Rețetele existente păstrează numai butonul „Consum pe rețetă” (datele nu se ascund).
  let alimentatie = false;
  try { alimentatie = (await api.get(`/tenants/${t.id}/stocuri/articole`)).alimentatie_publica === true; } catch {}
  if (!corp.isConnected) return;
  corp.innerHTML = `
    <h2 class="pf-titlu">Raport Z</h2>
    <p class="pf-intro">Totaluri cu TVA inclus. Numerar + card = total. NUI-ul casei de marcat și numărul raportului sunt în antetul bonului Z tipărit — ele fac raportul unic, ca să nu se înregistreze de două ori. Numărul de bonuri fiscale e tot pe raportul Z și intră în D394.</p>
    <p><label class="buton-secundar" style="cursor:pointer">Import fi\u0219ier AMEF (p7b/XML)
      <input type="file" id="z-amef" data-actiune="POST /tenants/{tenant_id}/horeca/import-amef" accept=".p7b,.xml" style="display:none"></label></p>
    <div id="z-amef-msg"></div>
    <div class="grila-campuri" id="z-campuri">   <!-- [lotul 13, 509] câmpurile aliniate în grila comună (DS cap.9), nu într-o grilă scrisă pe loc -->
      <label class="camp"><span class="camp-eticheta">Data</span><input type="date" id="z-data" class="camp-input" value="${dataIso()}"></label>
      <label class="camp"><span class="camp-eticheta">NUI casă de marcat</span><input id="z-nui" class="camp-input" placeholder="ex. 8000000001"></label>
      <label class="camp"><span class="camp-eticheta">Nr. raport Z</span><input id="z-nr" class="camp-input" placeholder="ex. 0042"></label>
      <label class="camp"><span class="camp-eticheta" id="z-et-11">Total 11%${alimentatie ? " (m\u00e2ncare)" : ""}</span><input type="number" step="0.01" id="z-11" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta" id="z-et-21">Total 21%${alimentatie ? " (alcool, sucuri)" : ""}</span><input type="number" step="0.01" id="z-21" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Numerar</span><input type="number" step="0.01" id="z-num" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Card</span><input type="number" step="0.01" id="z-card" class="camp-input"></label>
      <label class="camp"><span class="camp-eticheta">Nr. bonuri fiscale</span><input type="number" min="1" step="1" id="z-bonuri" class="camp-input"></label>
    </div>
    <p style="margin-top:16px"><button class="buton-primar" id="z-salveaza" data-genereaza-nota data-actiune="POST /tenants/{tenant_id}/horeca/raport-z">${t.regim_contabil === "simpla" ? "\u00cenregistreaz\u0103 raportul Z" : "Genereaz\u0103 not\u0103"}</button></p>
    <div id="z-rezultat"></div>
    <div id="z-descarcare"></div>`;
  // [decizii 07.10 pct.3] la stocul cantitativ-valoric Z-ul se validează numai cu descărcarea mărfii pe articol (manual sau prin
  // rețetă) — ori cu declarația explicită „fără marfă din stoc”. Rapoartele Z nevalidate ale lunii, cu descărcarea fiecăruia.
  const zDesc = corp.querySelector("#z-descarcare");
  const azd = new Date(); let zAn = azd.getFullYear(), zLuna = azd.getMonth() + 1;
  // [368] la PFA nota Z-ului se reîncearcă la validarea internă după descărcare / „fără marfă”: rezultatul se spune după redesenare
  // (validată -> notă internă, în zona de sus; refuzată -> motivul, la rândul Z-ului)
  // [lotul 10, comanda 10.2 pct.8e] „După descărcare nu se vede valoarea descărcată și nici butonul de validare a Z-ului.” -> confirmarea
  // cu valoarea (`ok`, DS cap.6 / 410: după o salvare reușită, mesaj de confirmare vizibil), iar rândul Z-ului arată valoarea și „Validează”
  // [lotul 13, 605 — clasa 45] „mesajul de confirmare sus, departe de buton”: confirmarea și refuzul unei acțiuni pe un raport Z stau pe
  // rândul lui, sub butoanele lui (`#zd-msg-<id>`), aduse în vedere — nu în capul listei
  const peRandZ = (zid, text, tip) => {
    const loc = zDesc.querySelector(`#zd-msg-${zid}`) || zDesc.querySelector("#zd-rez");
    if (!loc) return;
    arataMesaj(loc, text, tip);
    aduInVedere(loc);
  };
  const dupaDescarcare = async (r, zid, ok = "") => {
    await deseneazaDescarcarea();
    const rf = refuzuriInterne(r);
    if (!(r && ((r.interne || []).length || rf.length))) {
      if (ok) peRandZ(zid, ok, "ok");
      return;
    }
    peRandZ(zid, pasNota(r), rf.length ? "eroare" : "info");
  };
  // [605] raportul Z numit ca documentul lui („Raport Z nr 0042 · casa 8000000001”), nu prin cheia internă „Z-8000000001-0042”
  const numeZ = (z) => {
    const pref = `Z-${z.nui}-`;
    const nr = z.numar && String(z.numar).startsWith(pref) ? String(z.numar).slice(pref.length) : "";
    return nr ? `Raport Z nr ${nr} · casa ${z.nui}` : "Raport Z";
  };
  const poateValidaZ = t.regim_contabil !== "simpla" && permis("POST /tenants/{tenant_id}/jurnal/{nota_id}/valideaza");
  const cerereDescarcare = ultimaCerere();   // [C103] luna Z-urilor schimbată sau descărcări în șir: numai rapoartele cerute ultimele ajung pe ecran
  const deseneazaDescarcarea = async () => {
    const actuala = cerereDescarcare();
    let d, arts = [], rets = [], reteteZ = false, cv = false;
    try {
      d = await api.get(`/tenants/${t.id}/horeca/rapoarte-z?an=${zAn}&luna=${zLuna}`);
      if (!actuala()) return;
      // [lotul 12, C139] lista rapoartelor Z ale lunii se vede la ORICE metodă de stoc (rândul poartă „Șterge raportul Z”); descărcarea pe
      // articol rămâne a stocului cantitativ-valoric
      cv = !!d.descarcare_pe_articol;
      if (cv) {
        const ra = await api.get(`/tenants/${t.id}/stocuri/articole`);
        if (!actuala()) return;
        arts = ra.articole || [];
        reteteZ = !!ra.retete_vizibile;   // [lotul 11, pct.23] „Consum pe rețetă” numai la alimentația publică (regula ecranului Stocuri)
        if (reteteZ) rets = (await api.get(`/tenants/${t.id}/retete`)).retete || [];
        if (!actuala()) return;
      }
    } catch (e) { if (!actuala()) return; zDesc.innerHTML = `<p class="ecran-nota">Nu s-au putut citi rapoartele Z: ${esc((e && e.mesaj) || "reîncearcă")}.</p>`; return; }
    const rapoarte = d.rapoarte || [];
    const nevalidate = rapoarte.filter((z) => z.status === "ciorna");
    const optArt = `${ALEGE}` + arts.map((a) => `<option value="${a.id}">${esc(a.denumire)} (stoc ${esc(cantitate(a.stoc))})</option>`).join("");
    const optRet = `${ALEGE}` + rets.map((x) => `<option value="${x.id}">${esc(x.denumire)}</option>`).join("");
    const lunaZ = dataRo(`${zAn}-${String(zLuna).padStart(2, "0")}-01`, "luna_an_numeric");
    // [lotul 12, C139] Z-ul validat nu se șterge (a intrat în evidență: corectura e stornarea, OMFP 1802/2014 pct.69); [lotul 13, 675] butoanele
    // rândului stau la locul lor, inactive, cu motivul
    const validatZ = "Raportul Z e validat: a intrat în evidență.";
    const randValidat = (z) => `
      <div class="pf-frand" style="display:block" data-z-validat="${z.id}">
        <div class="pf-frand-nume">${esc(numeZ(z))} · ${dataRo(z.data)} · încasat ${bani(z.incasat)} lei · validat</div>
        <div class="pf-frand-sub">${esc((z.stergere && z.stergere.refuz) || "Validat: a intrat în evidență.")}</div>
        <p style="margin:8px 0 0;display:flex;gap:8px;flex-wrap:wrap">${t.regim_contabil !== "simpla" && poateValidaZ ? butonRand("buton-primar", `data-z="${z.id}" data-actiune="POST /tenants/{tenant_id}/jurnal/{nota_id}/valideaza"`, "Validează raportul Z", validatZ) : ""}
          ${butonRand("buton-sters buton-mic", `data-z="${z.id}" data-actiune="DELETE /tenants/{tenant_id}/horeca/raport-z/{nota_id}"`, "Șterge raportul Z", (z.stergere && z.stergere.refuz) || validatZ)}</p>
        <div id="zd-msg-${z.id}"></div>
      </div>`;
    pastreazaCampulActiv(zDesc, () => {   // [C103] cantitatea / articolul scris cât sosește lista (un raport Z importat) nu se pierd
      zDesc.innerHTML = `<h3 class="pf-subtitlu">${cv ? `Descărcarea mărfii vândute — rapoartele Z (${lunaZ})` : `Rapoartele Z din ${lunaZ}`}</h3>
        ${cv ? `<p class="pf-intro">La stocul cantitativ-valoric raportul Z nu are articole: ce s-a vândut din stoc spui tu, pe articol${reteteZ ? " sau prin rețetă" : ""}. Z-ul se validează numai după descărcare — sau dacă declari că n-a vândut marfă din stoc.</p>` : ""}
        <div id="zd-rez"></div>
        ${!rapoarte.length ? `<div class="stare-goala">Niciun raport Z în luna asta.</div>` : rapoarte.map((z) => z.status !== "ciorna" ? randValidat(z) : `
        <div class="pf-frand" style="display:block" data-z="${z.id}">
          <div class="pf-frand-nume">${esc(numeZ(z))} · ${dataRo(z.data)} · încasat ${bani(z.incasat)} lei · nevalidat</div>
          ${!cv ? "" : z.iesiri ? `<div class="caseta-info"><span class="ci-mesaj" id="zd-valoare-${z.id}">Descărcat: ${cate(z.iesiri, "ieșire din stoc legată", "ieșiri din stoc legate")} de acest Z, în valoare de ${bani(z.valoare_descarcata)} lei (la cost). Se poate valida.</span></div>`
            : z.fara_marfa ? `<div class="caseta-info"><span class="ci-mesaj">Declarat fără marfă din stoc. Se poate valida.</span></div>`
            : `<div class="caseta-atentie"><div class="ca-mesaj">Nedescărcat: Z-ul nu se validează până nu descarci marfa vândută (sau declari că n-a fost).</div></div>`}
          ${poateValidaZ ? `<p style="margin:8px 0 0">${butonRand("buton-primar zd-valideaza", `id="zd-val-${z.id}" data-z="${z.id}" data-zd-valideaza="1" data-actiune="POST /tenants/{tenant_id}/jurnal/{nota_id}/valideaza"`, "Validează raportul Z",
              !cv || z.iesiri || z.fara_marfa ? null : "Descarcă întâi marfa vândută din stoc (sau declară „fără marfă din stoc”), apoi validează.")}</p>`
            : t.regim_contabil !== "simpla" ? `<p class="ecran-nota" style="margin:8px 0 0">Validarea o face un coleg cu dreptul „Poate valida”, din Registru jurnal.</p>` : ""}
          ${!cv ? "" : `<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:8px">
            <input type="text" class="camp-input zd-art-cauta" id="zd-art-${z.id}-cauta" data-z="${z.id}" placeholder="Caută articolul în stoc…" aria-label="Caută articolul" autocomplete="off" style="min-width:180px">
            <select class="camp-input" id="zd-art-${z.id}" aria-label="Articolul vândut" style="min-width:200px">${optArt}</select>
            <input type="number" min="0" step="0.001" class="camp-input" id="zd-cant-${z.id}" aria-label="Cantitatea vândută" placeholder="cantitate" style="width:120px">
            <button class="buton-secundar zd-iesire" data-z="${z.id}" data-data="${esc(z.data)}" data-actiune="POST /tenants/{tenant_id}/stocuri/iesire">Ieșire pe articol</button>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:6px">
            ${reteteZ ? `<select class="camp-input" id="zd-ret-${z.id}" aria-label="Rețeta vândută" style="min-width:200px">${optRet}</select>
            <input type="number" min="0" step="0.01" class="camp-input" id="zd-portii-${z.id}" aria-label="Porțiile vândute" placeholder="porții" style="width:120px">
            <button class="buton-secundar zd-reteta" data-z="${z.id}" data-data="${esc(z.data)}" data-actiune="POST /tenants/{tenant_id}/retete/descarca">Consum pe rețetă</button>` : ""}
            ${butonRand("buton-secundar zd-fara", `data-z="${z.id}" data-zd-fara="1" data-actiune="POST /tenants/{tenant_id}/horeca/raport-z/{nota_id}/fara-marfa"`, z.fara_marfa ? "Retrage „fără marfă”" : "Fără marfă din stoc",
              z.iesiri ? "Raportul Z are ieșiri din stoc legate: nu e „fără marfă din stoc”." : null)}
          </div>`}
          <p style="margin:8px 0 0"><button class="buton-sters buton-mic zd-sterge" id="zd-sterge-${z.id}" data-z="${z.id}" data-actiune="DELETE /tenants/{tenant_id}/horeca/raport-z/{nota_id}">Șterge raportul Z</button></p>
          <div id="zd-msg-${z.id}"></div>
        </div>`).join("")}`;
    });
    zDesc.querySelectorAll(".zd-art-cauta").forEach((c) => cautaInLista(c, zDesc.querySelector("#zd-art-" + c.dataset.z)));   // [488]
    // [lotul 12, C139] „Șterge raportul Z”: numai Z-ul nevalidat, cu descărcările lui necontate. Întâi întrebarea, cu ce se șterge și cifrele
    // (`z_descarcare.plan_stergere`, de pe server); refuzul cunoscut (luna blocată, la validare, descărcare validată) se spune fără întrebare
    zDesc.querySelectorAll(".zd-sterge").forEach((b) => b.addEventListener("click", () => {
      const zid = b.dataset.z, st = (nevalidate.find((x) => String(x.id) === zid) || {}).stergere || {};
      if (st.refuz) { arataMesaj(zDesc.querySelector(`#zd-msg-${zid}`), st.refuz, "eroare"); return; }
      confirmaCaseta(b.parentElement || b, esc(st.confirmare || "Ștergi raportul Z?"), async () => {
        try {
          const r = await api.del(`/tenants/${t.id}/horeca/raport-z/${zid}`);
          await deseneazaDescarcarea();
          peRandZ(zid, r.mesaj || "Raportul Z s-a șters.", "ok");   // rândul lui nu mai e: confirmarea în capul listei, adusă în vedere
        } catch (e) { arataMesaj(zDesc.querySelector(`#zd-msg-${zid}`), (e && e.mesaj) || "Raportul Z nu s-a șters.", "eroare"); }
      }, { textOk: "Da, șterge raportul Z" });
    }));
    zDesc.querySelectorAll(".zd-iesire").forEach((b) => b.addEventListener("click", async () => {
      const zid = b.dataset.z;
      let lipsa = false; if (cereAlegerile(zDesc, [`#zd-art-${zid}`])) lipsa = true;   // [lotul 11, 440] articolul și cantitatea, deodată
      const cant = parseFloat(zDesc.querySelector(`#zd-cant-${zid}`).value);
      if (!(cant > 0)) { eroareCamp(zDesc, `zd-cant-${zid}`, "Cantitatea vândută, mai mare ca 0."); lipsa = true; }
      if (lipsa) return;
      try {
        const r = await api.post(`/tenants/${t.id}/stocuri/iesire`, { articol_id: Number(zDesc.querySelector(`#zd-art-${zid}`).value), cantitate: cant, data: b.dataset.data, z_id: Number(zid) });
        dupaDescarcare(r, zid, `Ieșire înregistrată: ${bani(r.valoare)} lei la cost (nota ${r.nota}), legată de raportul Z.`);
      } catch (e) { arataMesaj(zDesc.querySelector(`#zd-msg-${zid}`), (e && e.mesaj) || "Ieșirea nu s-a salvat.", "eroare"); }
    }));
    zDesc.querySelectorAll(".zd-reteta").forEach((b) => b.addEventListener("click", async () => {
      const zid = b.dataset.z;
      let lipsa = false; if (cereAlegerile(zDesc, [`#zd-ret-${zid}`])) lipsa = true;   // [lotul 11, 440] rețeta și porțiile, deodată
      const portii = parseFloat(zDesc.querySelector(`#zd-portii-${zid}`).value);
      if (!(portii > 0)) { eroareCamp(zDesc, `zd-portii-${zid}`, "Porțiile vândute, mai mult de 0."); lipsa = true; }
      if (lipsa) return;
      try {
        const r = await api.post(`/tenants/${t.id}/retete/descarca`, { reteta_id: Number(zDesc.querySelector(`#zd-ret-${zid}`).value), portii, data: b.dataset.data, z_id: Number(zid) });
        dupaDescarcare(r, zid, `Consum pe rețetă înregistrat: ${bani(r.cost_total)} lei la cost, legat de raportul Z.`);
      } catch (e) { arataMesaj(zDesc.querySelector(`#zd-msg-${zid}`), (e && e.mesaj) || "Consumul nu s-a salvat.", "eroare"); }
    }));
    zDesc.querySelectorAll("[data-zd-fara]").forEach((b) => b.addEventListener("click", () => {
      const zid = b.dataset.z, retrage = b.textContent.startsWith("Retrage");
      confirmaCaseta(b.parentElement || b, retrage ? "Retragi declarația „fără marfă”? Z-ul nu se mai poate valida fără descărcare."
        : "Declari că în acest raport Z nu s-a vândut nicio marfă din stoc (numai servicii)? Declarația rămâne pe Z.", async () => {
        try { dupaDescarcare(await api.post(`/tenants/${t.id}/horeca/raport-z/${zid}/fara-marfa`, { fara_marfa: !retrage }), zid); }
        catch (e) { arataMesaj(zDesc.querySelector(`#zd-msg-${zid}`), (e && e.mesaj) || "Nu s-a salvat.", "eroare"); }
      }, { textOk: retrage ? "Retrage" : "Da, fără marfă" });
    }));
    // [lotul 10, comanda 10.2 pct.8e] validarea Z-ului descărcat, pe drumul unic al validării (Registru jurnal: `jurnal_api.valideaza`)
    // [lotul 12, deficiența 474] „Z validat cu descărcare parțială din stoc, fără avertisment”: Z-ul n-are articole, deci aplicația nu știe
    // dacă descărcarea e completă — înainte de validare se arată cifrele (vânzarea fără TVA, costul descărcat, adaosul) și se cere
    // confirmarea (`z_descarcare.avertisment_descarcare`); după validare nu se mai leagă ieșiri de Z
    zDesc.querySelectorAll("[data-zd-valideaza]").forEach((b) => b.addEventListener("click", () => {
      const zid = b.dataset.z, z = nevalidate.find((x) => String(x.id) === zid) || {};
      const valideaza = async () => {
        try {
          await api.post(`/tenants/${t.id}/jurnal/${zid}/valideaza`, {});
          await deseneazaDescarcarea();
          peRandZ(zid, `${numeZ(z)} din ${dataRo(z.data)} e validat: nota lui a intrat în evidență (Registru jurnal).`, "ok");
        } catch (e) { arataMesaj(zDesc.querySelector(`#zd-msg-${zid}`), (e && e.mesaj) || "Raportul Z nu s-a validat.", "eroare"); }
      };
      if (!z.avertisment) { valideaza(); return; }
      confirmaCaseta(b.parentElement || b, `${esc(z.avertisment)} Validezi raportul Z?`, valideaza, { textOk: "Da, validează raportul Z" });
    }));
  };
  deseneazaDescarcarea();
  // [lotul 12, C118 — clasa] orice raport Z adăugat (importul AMEF, Z-ul scris de mână) duce secțiunea descărcării pe luna LUI
  const mergiPeLunaZ = (data) => {
    const dz = new Date(String(data || "").slice(0, 10) + "T00:00:00");
    if (isNaN(dz)) return;
    zAn = dz.getFullYear(); zLuna = dz.getMonth() + 1;
    deseneazaDescarcarea();
  };
  corp.querySelector("#z-amef").addEventListener("change", async (ev) => {
      const f = ev.target.files[0];
      const zona = corp.querySelector("#z-amef-msg");
      if (!f) return;
      const fd = new FormData();
      fd.append("fisier", f);
      try {
        // [lotul 11, 422 / clasa 286] prin `api.postForm`, nu `fetch` direct: scrierea reușită anunță schimbarea (contorul „De validat”,
        // clopoțelul, pagina principală), iar refuzul are drumul comun (mesajul serverului, butonul spre ecran, sesiunea expirată)
        const r = await api.postForm(`/tenants/${t.id}/horeca/import-amef`, fd);
        zona.className = zona.className.replace(/\bmsg-(eroare|avert|info|ok)\b/g, "").trim();   // [lotul 10, 10.2 pct.8c] nu moștenește refuzul
        if (r.registru !== "rip") {
          // [8c] nota importului, pe drumul unic al confirmării unei note generate (stil de succes, conturile și sumele)
          dupaGenerare(zona, null, { titlu: `Importat: raportul Z din ${dataRo(r.data)}, total ${bani(r.total)} lei`,
            eticheta: `Nota ${r.nota_eticheta || ""} — ${stareNota(r)}`, linii: r.linii,
            detalii: [`Numerar ${bani(r.numerar)} lei · card ${bani(r.card_altele)} lei · TVA ${bani(r.tva_total)} lei. Verific-o cu Z-ul tipărit.`] });
        } else {   // [368] PFA: registrul de încasări și plăți, nu o notă
          zona.innerHTML = `<p class="pf-intro">Importat: Z din ${dataRo(r.data)}, total ${bani(r.total)}, TVA ${bani(r.tva_total)}. ${zInRip(r.numerar, r.card_altele)}</p>`;
        }
        // [lotul 12, C118] „un Z importat din AMEF pe o lună trecută nu se poate descărca din stoc din ecran, deci nici valida”: descărcarea
        // trece pe luna Z-ului importat (ca la Z-ul scris de mână) și se redesenează — altfel rămânea pe luna curentă, fără el
        mergiPeLunaZ(r.data);
      } catch (e) { arataMesaj(zona, e.mesaj || e.message || "eroare", "eroare"); }
      ev.target.value = "";
    });
    const zSalveaza = corp.querySelector("#z-salveaza");
    // [lotul 10, comanda 10.2 pct.8c; lotul 11, 8c central] alt raport Z scris în formular reactivează butonul dezactivat după generare
    const campuriZ = [...corp.querySelectorAll("#z-data, #z-nui, #z-nr, #z-11, #z-21, #z-num, #z-card, #z-bonuri")];
    zSalveaza.addEventListener("click", async () => {
    const v = (id) => parseFloat(corp.querySelector(id).value) || 0;
    const zona = corp.querySelector("#z-rezultat");   // [lotul 13, 605 — clasa 45] confirmarea sub butonul care a cerut-o, nu deasupra formularului
    curataEroriCamp(corp);
    const nrBonuri = parseInt(corp.querySelector("#z-bonuri").value, 10) || 0;
    if (nrBonuri <= 0) {
      // [D394 op2 Î1, decizia B] UX preventiv; refuzul autoritar e pe server (MESAJ_Z_FARA_BONURI)
      eroareCamp(corp, "z-bonuri", "Trece numărul de bonuri fiscale de pe raportul Z — intră în D394.");
      return;
    }
    try {
      const r = await api.post(`/tenants/${t.id}/horeca/raport-z`, {
        data: corp.querySelector("#z-data").value,
        // [R61] cheia de unicitate a raportului Z: casa de marcat + numarul raportului
        nui: corp.querySelector("#z-nui").value.trim(),
        nr_raport: corp.querySelector("#z-nr").value.trim(),
        nr_bonuri: nrBonuri,
        total_11: v("#z-11"), total_21: v("#z-21"),
        numerar: v("#z-num"), card: v("#z-card"),
      });
      // [lotul 10, comanda 10.2 pct.8c] „După generare, titlul «Notă generată» e roșu […] iar «Generează notă» rămâne activ.” Zona a
      // purtat refuzul de dinainte (`arataMesaj` pune `msg-eroare` pe ea): rezultatul reușit nu-i moștenește culoarea. Butonul se
      // dezactivează după înregistrare (un al doilea clic ar cere același Z) și se reactivează când se scrie alt raport Z.
      // [lotul 11, 8c — decizia 10.3 „reparația centrală”] totul pe drumul unic `api.dupaGenerare` (DS cap.6 v2.98).
      if (r.registru === "rip") {   // [368] PFA: registrul de încasări și plăți, nu o notă
        zona.className = zona.className.replace(/\bmsg-(eroare|avert|info|ok)\b/g, "").trim();
        butonGenerat(zSalveaza, "Raportul Z e înregistrat — îl vezi în registrul de încasări și plăți.");
        campuriZ.forEach((i) => i.addEventListener("input", () => butonDeGenerat(zSalveaza), { once: true }));
        zona.innerHTML = `<div class="caseta-info" id="z-rip"><span class="ci-mesaj">${zInRip(r.numerar, r.card)}</span></div>`;
        // [368] nota internă a Z-ului (TVA-ul pentru D300 / D394): validată automat, sau refuzul ei, cu motivul (ex. Z nedescărcat)
        if (refuzuriInterne(r).length) {
          zona.insertAdjacentHTML("beforeend", `<div class="caseta-atentie" id="z-interna-refuz"><div class="ca-mesaj">${pasNota(r)}</div></div>`);
          mergiPeLunaZ(corp.querySelector("#z-data").value || dataIso());
        }
        return;
      }
      dupaGenerare(zona, zSalveaza, {
        eticheta: `${r.nota_eticheta || ""} — ${stareNota(r)}`, linii: r.linii, idLinii: "z-nota-linii", reactiveazaLa: campuriZ,
        detalii: [`TVA 11%: ${bani(r.tva_11)} · TVA 21%: ${bani(r.tva_21)} · baze: ${bani(r.baza_11)} / ${bani(r.baza_21)}`],
        // [decizii 07.10 pct.3] la cantitativ-valoric nota e ciornă: se validează după descărcarea mărfii (secțiunea de mai jos)
        pas: r.descarcare_pe_articol ? `Nota e ${stareNota(r)}: se validează după ce descarci marfa vândută din stoc — mai jos, la acest raport Z.` : "" });
      if (r.descarcare_pe_articol) {
        mergiPeLunaZ(corp.querySelector("#z-data").value || dataIso());
        return;
      }
      // [z_desc_v1] propune descarcarea gestiunii GV a lunii dupa nota Z
      const dz = new Date(corp.querySelector("#z-data").value || new Date());
      const anz = dz.getFullYear(), lz = dz.getMonth() + 1;
      const zb = document.createElement("div");
      const zInCurs = lunaNeincheiata(anz, lz);   // [C198] pe luna în curs butonul stă inactiv, cu motivul, nu se oferă ca să fie refuzat
      zb.innerHTML = `<p><button class="buton-secundar" id="z-desc-gv" data-genereaza-nota data-actiune="POST /tenants/{tenant_id}/stocuri/descarcare"${zInCurs ? ' disabled aria-describedby="z-desc-gv-motiv"' : ""}>Descarc\u0103 gestiunea GV ${dataRo(`${anz}-${String(lz).padStart(2, "0")}-01`, "luna_an_numeric")} (not\u0103 ciorn\u0103)</button></p>${zInCurs ? `<p class="tip-micut" id="z-desc-gv-motiv">${esc(MOTIV_DESCARCARE_LUNA_IN_CURS)}</p>` : ""}<div id="z-desc-gv-rez"></div>`;
      zona.appendChild(zb);
      zb.querySelector("#z-desc-gv").addEventListener("click", async () => {
        try {
          const rd = await api.post(`/tenants/${t.id}/stocuri/descarcare?an=${anz}&luna=${lz}`, {});
          // [8c] confirmarea pe drumul unic: conturile notelor desc\u0103rc\u0103rii (citite din jurnal dup\u0103 id-urile \u00eentoarse), butonul inactiv
          const ultimaZi = dataIso(new Date(anz, lz, 0));
          dupaGenerare(zb.querySelector("#z-desc-gv-rez"), zb.querySelector("#z-desc-gv"), {
            titlu: `Desc\u0103rcare GV \u00eenregistrat\u0103 (${stareNota(rd)}): 607 = ${rd.cmv != null ? bani(rd.cmv) : "?"} lei (K=${rd.k ?? "?"})`,
            note: await noteGenerate(t.id, rd.inregistrari, ultimaZi) });
        } catch (e2) { arataMesaj(zb.querySelector("#z-desc-gv-rez"), e2.mesaj || "Eroare la desc\u0103rcare", "eroare"); }   // [lotul 07.10] prin helper: escapat, adus în vedere, cu butonul spre ecran
      });
        } catch (e) {   // [lotul 11, 440] erorile serverului lângă câmpurile raportului Z, textul refuzului în zona rezultatului
          arataRefuzul(corp, e, zona, { campuri: { data: "z-data", nui: "z-nui", nr_raport: "z-nr", nr_bonuri: "z-bonuri", total_11: "z-11",
            total_21: "z-21", numerar: "z-num", card: "z-card" } });
        }
  });
}


// [jurnal] Registru jurnal lunar
// [08.10.2026, decizia Costin U3] Blocarea perioadei contabile — butonul „Blochează / Deblochează luna”, o singură definiție pentru
// Registrul jurnal și pentru „Închidere lună”. Întoarce starea (true = blocată). Drepturile: blocarea = «Poate valida»; deblocarea =
// administratorul (decizia Costin 04.10) — butonul se judecă după ce se știe starea lunii.
async function legaBlocareLuna(bLock, zonaMesaj, t, an, luna, dupa) {
  let lunaBlocata = false;
  try {
    const pb = await api.get(`/tenants/${t.id}/perioade-blocate`);
    lunaBlocata = (pb.blocate || []).some((p) => p.an === an && p.luna === luna);
  } catch {}
  if (!bLock) return lunaBlocata;
  bLock.textContent = lunaBlocata ? "Deblocheaz\u0103 luna" : "Blocheaz\u0103 luna";
  if (!permis(lunaBlocata ? "DELETE /tenants/{tenant_id}/perioade-blocate" : "POST /tenants/{tenant_id}/perioade-blocate")) { bLock.remove(); return lunaBlocata; }
  bLock.addEventListener("click", async () => {
    if (lunaBlocata) { cereMotivDeblocare(bLock, zonaMesaj, t, an, luna, dupa); return; }
    try {
      await api.post(`/tenants/${t.id}/perioade-blocate?an=${an}&luna=${luna}`, {});
      dupa();
    } catch (e) { arataMesaj(zonaMesaj, (e && e.mesaj) || "eroare", "eroare"); }
  });
  // [08.10.2026, retest pct.11 + deficiența 197, proba blocului F: „«Blochează luna» e activ deși «Ce oprește închiderea» are un blocaj
  // (22 de ciorne pe Comert Micro TVA)”] cât timp ceva oprește închiderea (sau controalele n-au putut fi citite), butonul de blocare e
  // inactiv și spune de ce — AICI, o dată, pentru ambele locuri în care apare (Închidere lună și antetul Registrului jurnal; poarta
  // stătea numai în primul). Serverul refuză oricum (uc_comun.controale_inchidere).
  // Citirea NU se așteaptă: ecranul își leagă restul butoanelor (← luna / luna →) imediat, iar unul apăsat între timp nu se pierde
  // (proba plasei, 58: navigarea jurnalului aștepta după a doua cerere). Până sosesc controalele, blocarea e inactivă.
  if (!lunaBlocata) {
    bLock.disabled = true;
    bLock.title = "Se citesc controalele lunii…";
    api.get(`/tenants/${t.id}/perioade-blocate?an=${an}&luna=${luna}`).then((r) => {
      const ctl = (r || {}).controale;
      if (ctl && !(ctl.blocaje || []).length) { bLock.disabled = false; bLock.title = ""; return; }
      bLock.title = ctl ? `Rezolvă întâi ce oprește închiderea (${ctl.blocaje.length}): ${ctl.blocaje.map((x) => x.mesaj).join(" · ")}`
        : "Controalele lunii nu au putut fi citite.";
    }).catch((e) => {
      bLock.title = "Controalele lunii nu au putut fi citite.";
      arataMesaj(zonaMesaj, `Controalele lunii nu s-au putut citi, deci luna nu se poate bloca acum: ${(e && e.mesaj) || "eroare"}`, "eroare");
    });
  }
  return lunaBlocata;
}

// [lotul 12, deficiența 483 (grav), Costin: „Deblocarea lunii imposibilă: fără câmp de motiv”] serverul consemnează redeschiderea unei
// perioade închise NUMAI cu motiv (R58: `perioade_inchideri`, constrângerea de motiv în bază; refuzul REDESCHIDERE_FARA_MOTIV), dar butonul
// trimitea cererea fără niciun motiv — deci deblocarea era refuzată mereu. Acum „Deblochează luna” deschide, sub el, câmpul motivului
// (obligatoriu, lângă câmp dacă lipsește) cu „Deblochează luna” și „Renunță”; motivul pleacă în cerere și rămâne în istoricul perioadei.
// Un singur loc, pentru ambele ecrane care au butonul (Închidere lună și antetul Registrului jurnal).
function cereMotivDeblocare(bLock, zonaMesaj, t, an, luna, dupa) {
  const vechi = document.getElementById("bl-deblocare");
  if (vechi) { focusFaraSalt(vechi.querySelector("#bl-motiv")); return; }
  const lunaTxt = dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric");
  // un formular: Enter în câmpul motivului apasă „Deblochează luna” (trimiterea implicită a formularului), fără clic dat din cod
  const f = document.createElement("form");
  f.id = "bl-deblocare";
  f.noValidate = true;
  // [lotul 12, clasa 446.1 — DS cap.5] întrebarea dinaintea deblocării e o confirmare, nu o eroare: `.caseta-intrebare` (neutră), cu
  // butoanele în ea, ca `api.confirmaCaseta`
  f.innerHTML = `<div class="caseta-intrebare"><div class="ca-mesaj">
      <label class="camp" style="display:block;max-width:560px"><span class="camp-eticheta">Motivul deblocării lunii ${esc(lunaTxt)}<span class="oblig">*</span></span>
        <input type="text" class="camp-input" id="bl-motiv" autocomplete="off" placeholder="ex: corectez factura F1A nr. 12, înregistrată cu altă dată">
        <span class="camp-ajutor">Rămâne scris în istoricul perioadei, cu numele tău și ora. După corectură, blochează luna din nou.</span></label></div>
    <div class="ca-actiuni">
      <button type="submit" class="buton-primar" id="bl-deblocheaza" data-actiune="DELETE /tenants/{tenant_id}/perioade-blocate">Deblochează luna</button>
      <button type="button" class="buton-secundar" id="bl-renunta" data-fara-actiune="închide câmpul motivului, fără scriere">Renunță</button>
    </div></div>`;
  (bLock.closest("p") || bLock).insertAdjacentElement("afterend", f);
  const inp = f.querySelector("#bl-motiv");
  focusFaraSalt(inp);
  aduInVedere(f);
  const b = f.querySelector("#bl-deblocheaza");
  b.addEventListener("click", async (ev) => {
    ev.preventDefault();   // formularul nu pleacă nicăieri: cererea e cea de mai jos
    curataEroriCamp(f);
    const motiv = inp.value.trim();
    if (!motiv) { eroareCamp(f, "bl-motiv", "Scrie motivul deblocării: rămâne în istoricul perioadei."); focusFaraSalt(inp); return; }
    b.disabled = true;
    try {
      await api.del(`/tenants/${t.id}/perioade-blocate?an=${an}&luna=${luna}&motiv=${encodeURIComponent(motiv)}`);
      f.remove();
      await dupa();
      const z = zonaMesaj && zonaMesaj.id ? document.getElementById(zonaMesaj.id) : null;
      if (z) arataMesaj(z, `Luna ${lunaTxt} e deblocată. Motivul („${motiv}”) e în istoricul perioadei.`, "ok");
    } catch (e) {
      b.disabled = false;
      if (e && e.detaliu && e.detaliu.camp === "motiv") eroareCamp(f, "bl-motiv", e.mesaj || "Scrie motivul deblocării.");
      else arataMesaj(zonaMesaj, (e && e.mesaj) || "Luna nu s-a deblocat.", "eroare");
    }
  });
  f.querySelector("#bl-renunta").addEventListener("click", () => f.remove());
}

// [08.10.2026, decizia Costin U3] „Închiderea lunii devine card separat, «Închidere lună», în grupul Zilnic al ferestrei firmei.”
// Până azi închiderea avea două acte, în două ecrane, niciunul numit așa: blocarea perioadei contabile („Blochează luna”, în antetul
// Registrului jurnal) și închiderea evidenței facturilor („Închide luna”, în Istoric facturi); cardul Balanță spunea „cu închiderea
// lunii”, dar acolo e numai închiderea soldurilor. Ecranul le arată pe amândouă, pe aceleași rute și cu aceleași drepturi.
async function ecranInchidereLuna(corp, nav, t) {
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  const dubla = t.regim_contabil === "dubla";   // DS cap.18: cardul e „ambele”, blocarea jurnalului e de partidă dublă
  const cerereNoua = ultimaCerere();   // [C103] luna schimbată în șir (← / →): numai starea lunii afișate ajunge pe ecran
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;
    const actuala = cerereNoua();
    const facturiDin = (per) => (per.confirmat
        ? `<div class="caseta-info"><span class="ci-mesaj">Evidența facturilor e închisă${per.confirmat_la ? " la " + dataRo(String(per.confirmat_la).slice(0, 10)) : ""}: e completă, iar semaforul se poate sprijini pe ea.</span><p style="margin-top:8px"><button class="buton-secundar" id="il-fac-redeschide" data-actiune="POST /tenants/{tenant_id}/facturi/perioada/redeschide">Redeschide evidența facturilor</button></p></div>`
        : (per.blocaj
          ? `<div class="caseta-info"><span class="ci-mesaj">Evidența facturilor nu se poate închide încă: ${esc(per.blocaj)}${per.remediu ? " " + esc(per.remediu) : ""}</span></div>`
          : `<div class="caseta-info"><span class="ci-mesaj">Evidența facturilor e deschisă — informativă până la închidere.</span><p style="margin-top:8px"><button class="buton-verde" id="il-fac-inchide" data-actiune="POST /tenants/{tenant_id}/facturi/perioada/confirma">Închide evidența facturilor</button></p></div>`));
    corp.innerHTML = `
      <h2 class="pf-titlu">Închidere lună</h2>
      <p class="pf-intro">Luna ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")}
        <button class="buton-secundar" id="il-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="buton-secundar" id="il-next">luna \u2192</button></p>
      <div id="il-mesaj"></div>
      ${dubla ? `<h3 class="pf-subtitlu">Perioada contabilă</h3>
      <p class="pf-intro" id="il-stare-perioada"></p>
      <div id="il-controale"></div>
      <p><button class="buton-primar" id="il-lock"></button></p>` : ""}
      <h3 class="pf-subtitlu">Evidența facturilor</h3>
      <div id="il-facturi"><p class="ecran-nota">Se încarcă…</p></div>`;
    // [proba plasei, 58/96] navigarea se leagă ÎNAINTEA cererilor ecranului: un clic dat cât ele rulează nu se pierde
    corp.querySelector("#il-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#il-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    const zm = corp.querySelector("#il-mesaj");
    const zf = corp.querySelector("#il-facturi");
    try {
      const per = await api.get(`/tenants/${t.id}/facturi/perioada?an=${an}&luna=${luna}`);
      if (!actuala()) return;
      zf.innerHTML = facturiDin(per);
      // [comanda Costin 10.10 pct.8] butoanele evidenței se leagă cum apar, nu după cererile controalelor și ale blocării de mai jos
      const bI = zf.querySelector("#il-fac-inchide");
      if (bI) bI.addEventListener("click", () => confirmaCaseta(bI, "Închizi evidența facturilor lunii? Declari că e completă. O factură nouă sau ștearsă o redeschide automat.", async () => {
        try { await api.post(`/tenants/${t.id}/facturi/perioada/confirma`, { an, luna }); deseneaza(); }
        catch (e) { arataMesaj(zm, (e && e.mesaj) || "Eroare.", "eroare"); }
      }, { textOk: "Închide evidența" }));
      const bR = zf.querySelector("#il-fac-redeschide");
      if (bR) bR.addEventListener("click", () => confirmaCaseta(bR, "Redeschizi evidența facturilor? Redevine informativă până la o nouă închidere.", async () => {
        try { await api.post(`/tenants/${t.id}/facturi/perioada/redeschide`, { an, luna }); deseneaza(); }
        catch (e) { arataMesaj(zm, (e && e.mesaj) || "Eroare.", "eroare"); }
      }, { textOk: "Redeschide" }));
    }
    catch (e) { if (!actuala()) return; zf.innerHTML = ""; arataMesaj(zf, "Nu s-a putut citi starea evidenței facturilor" + (e && e.mesaj ? " (" + e.mesaj + ")" : "") + " — reîncearcă.", "eroare"); }
    if (dubla) {
      // [08.10, W2 + W3] controalele închiderii — aceleași pe care le aplică blocarea (blocaje) și semnalele (581, 401 …)
      let ctl = null;
      const zc = corp.querySelector("#il-controale");
      try { ctl = (await api.get(`/tenants/${t.id}/perioade-blocate?an=${an}&luna=${luna}`)).controale; if (!actuala()) return; }
      catch (e) { if (!actuala()) return; arataMesaj(zc, "Nu s-au putut citi controalele lunii" + (e && e.mesaj ? " (" + e.mesaj + ")" : "") + " — reîncearcă.", "eroare"); }
      const bLock = corp.querySelector("#il-lock");
      const blocata = await legaBlocareLuna(bLock, zm, t, an, luna, deseneaza);   // poarta „ceva oprește închiderea” e în ea (197)
      if (!actuala()) return;
      corp.querySelector("#il-stare-perioada").textContent = blocata
        ? "Luna e blocată: notele ei nu se mai modifică, nu se mai adaugă și nu se mai șterg."
        : "Luna e deschisă. Blocarea verifică întâi controalele de mai jos.";
      if (ctl) {
        const lista = (xs) => `<ul class="ci-mesaj" style="margin:6px 0 0;padding-left:18px">${xs.map((x) => `<li>${esc(x.mesaj)}</li>`).join("")}</ul>`;
        zc.innerHTML = (ctl.blocaje.length
            ? `<div class="caseta-atentie"><div class="ca-mesaj"><b>Ce oprește închiderea (${ctl.blocaje.length})</b>${lista(ctl.blocaje)}</div></div>`
            : `<div class="caseta-info"><span class="ci-mesaj">Nimic nu oprește închiderea lunii.</span></div>`)
          + (ctl.semnale.length ? `<div class="caseta-info" style="margin-top:8px"><div class="ci-mesaj"><b>Semnale (${ctl.semnale.length})</b>${lista(ctl.semnale)}</div></div>` : "");
        // [deficiența 281, comanda Costin 16.10.2026] amortizarea restantă dintr-o singură acțiune (o notă pe lună); iar când NUMAI ea
        // oprește închiderea, luna se închide cu confirmarea explicită (amortizarea lipsă schimbă profitul — D100/D101)
        // [deficiența 312] amortizarea deja generată (ciornă, `de_validat`) nu mai cere butonul: se validează în Registrul jurnal
        const amort = ctl.blocaje.filter((b) => (b.cod === "AMORTIZARE_ANTERIOARA_NEINREGISTRATA" || b.cod === "AMORTIZARE_NEINREGISTRATA")
                                              && !b.de_validat);
        if (amort.length) {
          zc.insertAdjacentHTML("beforeend", `<p style="margin-top:8px"><button class="buton-primar" id="il-amort-restanta" data-genereaza-nota="redesenat" data-actiune="POST /tenants/{tenant_id}/amortizare/restanta">Generează amortizarea restantă</button></p>`);
          zc.querySelector("#il-amort-restanta").addEventListener("click", async () => {
            try {
              const r = await api.post(`/tenants/${t.id}/amortizare/restanta?an=${an}&luna=${luna}`, {});
              const refuzate = r.luni.filter((x) => !x.ok);
              await deseneaza();
              const textRest = [(r.generate ? `${cate(r.generate, "notă de amortizare generată", "note de amortizare generate")}, de validat`
                  : "Nicio notă nouă") + (r.deja_generate ? ` · ${cate(r.deja_generate, "lună avea", "luni aveau")} deja nota de amortizare, de validat` : "")
                  + " (o notă pe lună, în Registrul jurnal)."];
              const lunaEt = (x) => dataRo(`${x.an}-${String(x.luna).padStart(2, "0")}-01`, "luna_an_numeric");
              const scrise = r.luni.filter((x) => x.ok && !x.deja_generata);
              if (!scrise.length) {
                arataMesaj(corp.querySelector("#il-mesaj"), textRest.concat(refuzate.map((x) => `${lunaEt(x)}: ${x.mesaj}`)).join("\n"), refuzate.length ? "avert" : "info");
              } else {
                // [8c] notele scrise acum, pe drumul unic al confirmării (conturile și sumele fiecărei luni); refuzurile lunilor, separat
                dupaGenerare(corp.querySelector("#il-mesaj"), null, { titlu: textRest[0],
                  note: scrise.map((x) => ({ eticheta: `${lunaEt(x)} — nota ${x.nota_eticheta || ""}`, linii: x.linii_nota })) });
                if (refuzate.length) corp.querySelector("#il-mesaj").insertAdjacentHTML("beforeend",
                  `<div class="caseta-atentie"><div class="ca-mesaj">${refuzate.map((x) => `${esc(lunaEt(x))}: ${esc(x.mesaj)}`).join("<br>")}</div></div>`);
              }
            } catch (e) { arataMesaj(zm, (e && e.mesaj) || "Amortizarea restantă nu s-a putut genera.", "eroare"); }
          });
        }
        // [lotul 10, deficiența 429] reevaluarea în valută propusă de aplicație (OMFP 1802/2014 pct.325). [lotul 11, 429] Butonul e MEREU
        // aici (primar când reevaluarea oprește închiderea): e singurul drum spre reevaluare — formularul manual din Operațiuni a fost scos,
        // iar o lună fără blocaj (luna în curs, facturile cu contarea în ciornă) trebuie să se poată verifica și ea.
        {
          const opreste = ctl.blocaje.some((b) => b.cod === "REEVALUARE_VALUTA");
          const cls = opreste ? "buton-primar" : "buton-secundar";   // clasa DS cap.1 aleasă înainte (regula BUTOANE citește clasa din atribut)
          zc.insertAdjacentHTML("beforeend", `<p style="margin-top:8px"><button class="${cls}" id="il-reevaluare" data-actiune="GET /tenants/{tenant_id}/reevaluare-valuta">Reevaluare valută</button></p>`);
          zc.querySelector("#il-reevaluare").addEventListener("click", () => nav.deschide("Reevaluare valută",
            (c2) => ecranReevaluareValuta(c2, nav, t, an, luna, { jurnal: (o) => nav.deschide("Registru jurnal", (c3) => ecranJurnal(c3, nav, t, o), { lat: "tabel" }) }),
            { lat: "tabel" }));
        }
        const confirmabile = ctl.blocaje.filter((b) => b.confirmabil);
        if (!blocata && confirmabile.length && confirmabile.length === ctl.blocaje.length) {
          zc.insertAdjacentHTML("beforeend", `<p style="margin-top:8px"><button class="buton-secundar" id="il-lock-confirma" data-actiune="POST /tenants/{tenant_id}/perioade-blocate">Închide luna fără amortizarea lunilor anterioare</button></p>`);
          const bC = zc.querySelector("#il-lock-confirma");
          const intrebare = `Închizi luna deși ${esc(confirmabile.map((b) => b.mesaj.split(" — ")[0]).join("; "))}? Amortizarea lipsă schimbă profitul (D100/D101). Confirmarea rămâne în istoricul închiderii, cu numele tău.`;
          // textul întrebării stă în afara handlerului: legarea apelului de buton (scan_drepturi_ui) citește acoladele handlerului
          bC.addEventListener("click", () => confirmaCaseta(bC, intrebare, async () => {
            try { await api.post(`/tenants/${t.id}/perioade-blocate?an=${an}&luna=${luna}&confirma_amortizare=true`, {}); deseneaza(); }
            catch (e) { arataMesaj(zm, (e && e.mesaj) || "Luna nu s-a putut închide.", "eroare"); }
          }, { textOk: "Închid luna" }));
        }
      }
    }
  };
  deseneaza();
}

export async function ecranJurnal(corp, nav, t, opt = {}) {   // exportat: garda în browser + „nota #…” din detaliul facturii
  const cheie = "jurnal:" + t.id;
  const azi = new Date();
  let an = opt.an || azi.getFullYear(), luna = opt.luna || azi.getMonth() + 1;   // din factură: luna notei ei
  let poateValida = permis("POST /tenants/{tenant_id}/jurnal/{nota_id}/valideaza");   // [lotul 07.10 pct.16]
  // [lotul 13, 673 / 563] nota nouă și editarea se scriu în fereastra lor; la întoarcere registrul se deschide pe luna notei salvate, cu
  // rândul ei evidențiat, adus în vedere, și confirmarea în rezumatul lipit sus (nu „sare la început”, fără mesaj — 563 / 529)
  let revenire = starePastrata(cheie);
  if (revenire && revenire.an && revenire.luna) { an = revenire.an; luna = revenire.luna; }

  // [14-1-1 col.3, lista 5, 30.08.2026] „Felul, numarul si data documentului justificativ care sta
  // la baza operatiunilor" (OMFP 2634/2015, Anexa 1, pct. 45). Ruta il DERIVA
  // (`jurnal_api.document_justificativ`) si intoarce `null` cand nu are din ce - ecranul spune
  // atunci ca nu S-A PUTUT DERIVA, nu ca nota n-are document: un necunoscut nu se rotunjeste la
  // „stiu ca nu" (interdictia 32).
  // [lotul 13, 602] „«Document justificativ: nederivat» e termen de programator”: textul spune ce lipsește și de unde se completează
  const docJustificativ = (n) => `Document justificativ: ${n.document
    ? esc(n.document) + (n.stinge ? " · stinge " + esc(n.stinge) : "")   // [08.10, U5] chitanța: factura pe care o stinge
    : "lipsește — nota n-are documentul scris pe ea și nu e legată de o factură"}`;   // [lotul 11, pct.23] nu „nederivat”: cuvânt din cod

  // [05.10.2026, comanda Costin pct.6] „Validarea unei note fără document justificativ trece fără niciun avertisment —
  // validatorul trebuie să vadă lipsa înainte să apese.” Lipsa se vede pe rând.
  // [lotul 10, comanda 10.2 pct.7k, deficiența 386] „la nota fără document, același mesaj apare de două ori (stânga și dreapta)”: un
  // mesaj; „Validează” e inactiv (regula de fond R3 din bază refuză validarea fără document) și trimite la el.
  // [lotul 12, comanda 12.2 pct.9, deficiența 617] „tabel cu un rând pe notă, detaliul la clic, explicațiile o singură dată”: explicația
  // unui semn din coloana Stare stă O DATĂ, deasupra tabelului (`tabel_note.js`); pe rând, semnul scurt („fără document”), iar în detaliul
  // notei pasul ei (cine scrie referința). Aceleași explicații ca în „De validat” (`validat.js`).
  // [lotul 13, 610] „La «Validează» pe o notă fără document, refuzul cu motiv apare de două ori”: „Validează” e inactiv, cu pasul notei la
  // trecerea cu mouse-ul (675); regula stă o dată, deasupra tabelului, iar pasul notei o dată, în detaliul ei — niciun refuz la clic.
  const EXPLICATII_JN = {
    fara_doc: { atentie: true, titlu: "Fără document justificativ",
      text: "o notă nu se validează fără documentul din care provine (Registrul-jurnal, col.3: felul, numărul și data)." },
    depasita: { atentie: true, titlu: "Depășită față de sursă",
      text: "documentul din care s-a făcut ciorna s-a schimbat după generare, deci nota nu se mai validează așa. Refă-o din sursă (butonul din detaliul ei), apoi validează nota nouă." },
    inainte: { atentie: true, titlu: "Scrisă înainte de încheierea lunii",
      text: "nota s-a calculat înainte ca luna ei să se încheie; motivul și ce urmează sunt în detaliul notei." },
    derivata: { atentie: false, titlu: "Făcută dintr-un document",
      text: "nota se corectează din documentul ei (factură, NIR, stat de plată …), nu din Registrul jurnal; unde anume, scrie în detaliul notei." },
    a_altuia: { atentie: false, titlu: "Ciorna altui utilizator",
      text: "o vezi, dar n-o modifici, n-o ștergi și n-o trimiți la validare; cine a pregătit-o, scrie în detaliul notei." },
  };
  // [617] „Un câmp (cont, document, partener, sumă, nr. crt.) și filtru de stare”: căutarea și starea aleasă, rândurile deschise — păstrate
  // la redesenarea pe loc (după o validare) și la luna schimbată
  const STARI_JN = [["", "Toate stările"], ["ciorna", "Ciorne (nevalidate)"], ["validata", "Validate"], ["la_validare", "La validare în cabinet"],
    ["respinsa", "Respinse, de corectat"], ["fara_doc", "Fără document justificativ"]];
  const filtru = { text: "", stare: "" };
  const deschise = new Set();
  let ultimeleNote = [];
  let centre = [];  // [F143] centre active, pentru selectorul de pe linia de nota manuala
  // [265] `peLoc`: redesenarea la schimbarea drepturilor nu golește registrul deschis cât se citește (fără „Se încarcă...” intermediar)
  // `mod.peLoc` (redesenarea la drepturi, 265): fără „Se încarcă” intermediar. Nu `opt`: acela e al ecranului (an, luna, evidentiaza)
  const cerereNoua = ultimaCerere();   // [C103] luna schimbată în șir (← / →): numai notele lunii afișate ajung pe ecran
  const deseneaza = async (mod = {}) => {
    // [617] „După «Validează» pagina sare sus fără confirmare”: pe loc (după o acțiune pe rând) fereastra nu trece prin „Se încarcă…”, deci
    // conținutul nu scade și derularea rămâne unde era; rândul arată starea nouă, iar confirmarea stă în rezumatul lipit sus
    if (!mod.peLoc) corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    const actuala = cerereNoua();
    let note = [], jur = {};
    try {
      const r = await api.get(`/tenants/${t.id}/jurnal?an=${an}&luna=${luna}`);
      if (!actuala()) return;
      note = (r && r.note) || [];
      jur = r || {};
    } catch { if (!actuala()) return; corp.innerHTML = `<p class="ecran-nota">Nu s-a putut încărca jurnalul.</p>`; return; }
    try {
      const rc = await api.get(`/tenants/${t.id}/centre-cost?doar_active=true`);
      if (!actuala()) return;
      centre = (rc && rc.centre) || [];
    } catch { if (!actuala()) return; centre = []; }
    // [617] rândul notei pentru tabelul comun (`tabel_note.js`): pe rând numărul, data, explicația, documentul, conturile, suma, starea
    // și acțiunea principală a stării; în detaliu liniile, documentul justificativ, mesajele notei și restul acțiunilor
    // [lotul 13, 675] aceleași butoane pe fiecare notă, în aceeași ordine — „Validează”, „Trimite la validare” pe rând; „Refă din sursă”,
    // „Editează”, „Șterge” în detaliu —, iar ce nu se aplică stă inactiv, cu motivul (`atributeInactiv`); ascunse rămân numai cele
    // refuzate rolului (`data-actiune`, drepturi.js)
    const randJn = (n) => {
      // [validare_note 06.10.2026, comanda Costin pct.1] starea notei în coada de validare a cabinetului (din aceeași coadă)
      const v = n.validare;
      const ciorna = n.status === "ciorna";
      const respinsa = ciorna && v && v.stare_coada === "respinsa";
      const laValidare = ciorna && v && v.stare_coada === "la_senior";
      // [lotul 07.10 pct.16] ciorna fără element în coadă (scrisă înainte de mecanism, sau de cine validează singur): cine nu
      // validează o trimite explicit la validare; cine validează o validează aici.
      const inAfaraCozii = ciorna && !v;
      const stareValidare = respinsa
        ? `<div class="caseta-atentie jn-respinsa"><div class="ca-mesaj">Respinsă la validare: ${esc(motivInFraza(v.motiv_respingere))} Corecteaz-o, apoi trimite-o din nou.</div></div>`
        : (laValidare ? `<div class="pf-frand-sub">La validare în cabinet: nu se modifică până nu e validată sau respinsă.</div>` : "");
      // [lotul 07.10 pct.6] nota la validare nu se editează și nu se șterge (serverul refuză oricum: cabinetul validează ce a văzut)
      // [deficiența 192] ciorna derivată dintr-un document (NIR, raport Z, stoc, amortizare …) nu se editează din jurnal, iar cea
      // indicată din alt tabel nu se șterge de aici — serverul le refuză; ecranul spune unde se corectează
      const der = ciorna ? n.derivata : null;
      // [deficiența 246] ciorna ALTUI utilizator, pentru un asistent: o vede, nu o editează, n-o șterge, n-o trimite la validare — serverul
      // o refuză (regula din bază, `ciorna_altui`); ecranul spune de ce, cu textul refuzului. „Validează” rămâne (numai cu „Poate valida”).
      const alt = ciorna ? n.a_altuia : null;
      const motive = (alt ? `<div class="pf-frand-sub jn-a-altuia">${esc(alt.motiv)}</div>` : "") +
        (!alt && der && !laValidare ? `<div class="pf-frand-sub jn-derivata">${esc(der.unde)}</div>` : "");
      // [386, 10.2 pct.7k] nota fără document: „Validează” inactiv, legat de pasul notei (în detaliu) și de explicația de deasupra tabelului
      const faraDoc = ciorna && !n.document;
      const pasDoc = alt ? "Referința o scrie cine a pregătit nota."
        : laValidare ? "Se respinge din „De validat”, cu motivul, ca referința s-o scrie cine a pregătit nota."
        : der ? (der.unde || "") : "Scrie referința cu „Editează” (în detaliul notei), apoi validează.";
      // [lotul 11, deficiența 451] ciorna DEPĂȘITĂ față de sursa ei: motivul în detaliu, „Validează” inactiv, refacerea din sursă în detaliu
      const dep = ciorna ? n.depasita : null;
      const validata = "Nota e validată: a intrat în evidență.";
      const motivVal = !ciorna ? validata
        : faraDoc ? `Notă fără document justificativ. ${pasDoc}`
        : dep ? "Nota e depășită față de sursă: refă-o din sursă (în detaliul ei), apoi validează nota nouă." : null;
      const valDescr = faraDoc ? ` aria-describedby="jn-fara-doc-${n.id} jn-expl-fara_doc"` : dep ? ` aria-describedby="jn-depasita-${n.id} jn-expl-depasita"` : "";
      const bVal = butonRand("buton-primar", `data-val="${n.id}" data-actiune="POST /tenants/{tenant_id}/jurnal/{nota_id}/valideaza"${valDescr}`, "Validează", motivVal);
      const motivTrimite = !ciorna ? validata : laValidare ? "Nota e deja la validare în cabinet."
        : alt ? "E ciorna altui utilizator: o trimite la validare cine a pregătit-o."
        : !respinsa && poateValida ? "Ai dreptul să validezi: nota se validează direct, fără coadă." : null;
      const bRetrimite = butonRand("buton-secundar", `data-retrimite="${n.id}" data-actiune="POST /tenants/{tenant_id}/jurnal/{nota_id}/retrimite"`,
        respinsa ? "Trimite din nou la validare" : "Trimite la validare", motivTrimite);
      const poateReface = !!(dep && dep.refacere && permis("POST /tenants/{tenant_id}/jurnal/{nota_id}/reface"));
      const bReface = butonRand("buton-secundar", `data-reface="${n.id}" data-actiune="POST /tenants/{tenant_id}/jurnal/{nota_id}/reface"`,
        esc(dep && dep.refacere ? dep.refacere.eticheta : "Refă din sursă"),
        !ciorna ? validata : poateReface ? null : dep ? "Refacerea din sursă cere dreptul „Poate pregăti”." : "Nota nu e depășită față de sursa ei: n-are ce reface.");
      const nuSeModifica = !ciorna ? "Nota validată nu se modifică: se corectează printr-o notă de corecție."
        : alt ? alt.motiv : laValidare ? "Nota așteaptă validarea în cabinet: nu se modifică până nu e validată sau respinsă." : null;
      const bEdit = butonRand("buton-secundar", `data-edit="${n.id}"`, "Editează", nuSeModifica || (der ? der.unde : null));
      const bDel = butonRand("buton-secundar", `data-del="${n.id}" data-actiune="DELETE /tenants/{tenant_id}/jurnal/{nota_id}"`, "Șterge",
        !ciorna ? "Nota validată nu se șterge: se corectează printr-o notă de corecție." : nuSeModifica || (der && !der.se_sterge ? der.unde : null));
      const stare = n.status === "validata" ? { fel: "validata", text: "Validată", culoare: "var(--verde)" }
        : respinsa ? { fel: "respinsa", text: "Respinsă la validare", culoare: "var(--rosu)" }
        : laValidare ? { fel: "la_validare", text: "La validare în cabinet", culoare: "var(--galben-text)" }
        : { fel: "ciorna", text: "Ciornă", culoare: "var(--galben-text)" };
      const semne = [faraDoc && { fel: "fara_doc", text: "fără document" }, dep && { fel: "depasita", text: "depășită față de sursă" },
        n.contata_inainte && { fel: "inainte", text: "scrisă înainte de încheierea lunii" },
        der && !alt && { fel: "derivata", text: "din " + (der.fel || "document") }, alt && { fel: "a_altuia", text: "a altui utilizator" }].filter(Boolean);
      const parteneri = [...new Set(n.linii.map((l) => l.partener_nume || l.partener_cui).filter(Boolean))];
      const { rulaj, storno } = rulajLinii(n.linii);
      const stari = [stare.fel, n.status === "ciorna" ? "ciorna" : "", !n.document ? "fara_doc" : ""].filter(Boolean);
      return {
        cheie: n.id, atribute: { "nota-id": n.id }, nrCrt: n.nr_curent, data: n.data, explicatie: n.descriere || n.numar,
        document: n.document ? n.document + (n.stinge ? " · stinge " + n.stinge : "") : "", partener: parteneri.join(" "),
        linii: n.linii, rulaj, storno, stare, semne,
        stari,
        actiuni: `${bVal} ${bRetrimite}`,
        detaliu: `<p class="pf-frand-sub">${docJustificativ(n)}${n.sursa_eticheta ? " · sursa: " + esc(n.sursa_eticheta) : ""}</p>
          ${faraDoc ? `<div class="caseta-atentie jn-fara-doc" id="jn-fara-doc-${n.id}"><div class="ca-mesaj">Notă fără document justificativ. ${esc(pasDoc)}</div></div>` : ""}
          ${dep ? `<div class="caseta-atentie jn-depasita" id="jn-depasita-${n.id}"><div class="ca-mesaj pe-randuri">${esc(dep.mesaj)}</div></div>` : ""}
          ${stareValidare}${motive}${n.contata_inainte ? `<div class="caseta-atentie jn-inainte" id="jn-inainte-${n.id}"><div class="ca-mesaj">${esc(n.contata_inainte.motiv)}</div></div>` : ""}
          <p class="tn-detaliu-actiuni">${bReface} ${bEdit} ${bDel}</p>`,
      };
    };
    const randuriJn = note.map(randJn);
    ultimeleNote = note;
    const randuri = htmlTabelNote({ pre: "jn", randuri: randuriJn, nrCrt: true, explicatii: EXPLICATII_JN, deschise, gol: "Nicio notă în luna asta." });
    // [lotul 07.10 pct.14 + 16, comanda Costin 06.10.2026] „Registrul jurnal arată «1 de validat» pentru o notă respinsă”;
    // „ciornele de dinainte de mecanism apar «de validat», dar nu sunt în coadă”. Antetul numără după STAREA din coadă:
    // la validare / respinse (de corectat) / ciorne în afara cozii.
    // [lotul 13, 563] „Aceeași informație, trei cifre [...] Aceeași numărătoare peste tot (sau spus clar ce cuprinde fiecare)”: aici se
    // numără NOTELE LUNII acestei firme, iar fiecare parte spune ce cuprinde; „de validat” e numai al cardului și al ferestrei „De validat”
    // (notele din coada cabinetului, toate firmele) — ciornele lunii rămase în afara cozii se numesc „în afara cozii”, nu „de validat”
    const ciorneToate = note.filter((n) => n.status === "ciorna");
    const laValidareN = ciorneToate.filter((n) => n.validare && n.validare.stare_coada === "la_senior").length;
    const respinseN = ciorneToate.filter((n) => n.validare && n.validare.stare_coada === "respinsa").length;
    const inAfaraN = ciorneToate.filter((n) => !n.validare).length;
    const partiCiorne = [
      // [lotul 13, 563] spune ce numără: NOTELE lunii acestei firme (cardul și „De validat” numără tot note, ale tuturor firmelor)
      laValidareN ? `${cate(laValidareN, "notă", "note")} ale lunii la validare în cabinet` : "",
      respinseN ? `${cate(respinseN, "respinsă", "respinse")}, de corectat` : "",
      inAfaraN ? (poateValida ? `${cate(inAfaraN, "ciornă", "ciorne")} ale lunii în afara cozii (le validezi de aici)` : `${cate(inAfaraN, "netrimisă", "netrimise")} la validare`) : "",
    ].filter(Boolean).join(" · ");
    // [14-1-1, pct. 45] „Sumele debitoare si sumele creditoare se totalizeaza lunar." Ruta le
    // trimite din 24.08; randarea le pierdea. `note_fara_document` se arata fiindca absenta se
    // numara, nu se ascunde - e chiar motivul pentru care ruta o trimite.
    // [lotul 11, decizia Costin 10.3: „Totalurile … fix”] totalizarea lunii stă în bara de jos, în vedere cât derulezi notele (DS cap.9 v2.100)
    const totalizare = !note.length ? "" : `
      <div class="bara-fixa"><div class="fd-totaluri">
        <div class="fd-tot-rand"><span>Note validate în lună</span><span>${note.length - ((jur.ciorne || {}).note || 0)}</span></div>
        ${jur.note_fara_document ? `<div class="fd-tot-rand"><span title="Notele lunii fără numărul unui document scris pe ele și fără factură legată (OMFP 2634/2015: registrul-jurnal arată documentul justificativ al fiecărei note)">Note fără document justificativ (nici document scris, nici factură legată)</span><span>${jur.note_fara_document}</span></div>` : ""}
        <div class="fd-tot-rand fd-tot-final"><span>Total sume debitoare (note validate)</span><span>${bani(jur.total_debit)} lei</span></div>
        <div class="fd-tot-rand"><span>Total sume creditoare (note validate)</span><span>${bani(jur.total_credit)} lei</span></div>
        ${(jur.ciorne || {}).note ? `<div class="fd-tot-rand"><span>Ciorne în lună (nu intră în total)</span><span>${jur.ciorne.note} · ${bani(jur.ciorne.total)} lei</span></div>` : ""}
      </div></div>`;
    // [deficiența 333, 18.10.2026] luna în curs (sau viitoare): serverul refuză generarea amortizării până după ultima zi a lunii
    // (`uc_comun._cere_luna_incheiata`); butonul nu se mai oferă ca să fie refuzat — spune de ce
    const lunaInCurs = lunaNeincheiata(an, luna);
    // [lotul 11, comanda 11.1 pct.23] „«Generează amortizarea» activ pe luni deja amortizate”: nota lunii (`AMORT-AAAA-LL`, aceeași cheie ca
    // serverul, `uc_tenants.tenant_amortizare`) validată -> butonul e inactiv, cu motivul și nota numită; ciornă -> „Regenerează”, care o
    // înlocuiește numai dacă registrul s-a schimbat (altfel serverul refuză, numit)
    const notaAm = note.find((n) => n.sursa === "amortizare" && n.numar === `AMORT-${an}-${String(luna).padStart(2, "0")}`);
    const amValidata = !!(notaAm && notaAm.status === "validata");
    const motivAm = lunaInCurs ? "Amortizarea lunii se generează după ce luna se încheie."
      : amValidata ? `Amortizarea lunii e generată: nota nr. crt. ${notaAm.nr_curent ?? ""} din ${dataRo(notaAm.data)}, validată — o corectură se face printr-o altă notă.`
      : notaAm ? `Amortizarea lunii e generată (ciornă din ${dataRo(notaAm.data)}, mai jos). „Regenerează” o înlocuiește numai dacă registrul mijloacelor fixe s-a schimbat.`
      : "";
    corp.innerHTML = `
      <h2 class="pf-titlu">Registru jurnal ${semnAjutor("F061")}</h2>
      ${t.regim_contabil === "simpla" ? `<p class="ecran-nota" id="j-interne">Firmă în partidă simplă: notele sunt interne. ${esc(TEXT_NOTA_INTERNA)}</p>` : ""}
      <div class="rezumat-fix" id="j-rezumat">   <!-- [lotul 11, decizia Costin 10.3: „rezumatul fix”] luna, butoanele ei și zona lor de mesaj rămân sus cât derulezi notele (DS cap.9 v2.100) -->
      <p class="pf-intro">Luna ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")} · ${cate(note.length, "notă", "note")}${partiCiorne ? ` · <span id="j-numaratoare" style="color:var(--galben-text);font-weight:600">${partiCiorne}</span>` : ""}
        <button class="buton-secundar" id="j-prev" style="margin-left:12px">← luna</button>
        <button class="buton-secundar" id="j-next">luna →</button>
        <button class="buton-primar" id="j-amort" data-genereaza-nota data-actiune="POST /tenants/{tenant_id}/amortizare" style="margin-left:12px"${lunaInCurs || amValidata ? " disabled" : ""}${motivAm ? ` aria-describedby="j-amort-motiv"` : ""}>${notaAm && !amValidata ? "Regenerează amortizarea" : "Generează amortizarea"}</button>
        <button class="buton-secundar" id="j-nota-noua" data-actiune="POST /tenants/{tenant_id}/jurnal" style="margin-left:6px">+ Notă nouă</button>
        <button class="buton-secundar" id="j-lock" style="margin-left:6px"></button>${semnAjutor("F118")}
        ${randuriJn.length ? `<span id="j-cautare" style="margin-left:12px">${htmlCautare("jn", { stari: STARI_JN, valoare: filtru.text, stare: filtru.stare })}</span>` : ""}</p>
      ${motivAm ? `<p class="tip-micut" id="j-amort-motiv">${esc(motivAm)}</p>` : ""}
      <div id="j-mesaj"></div>
      </div>
      <div class="jn-lista">${randuri}</div>${totalizare}`;   // [394, lotul 9] motivul amortizării stă sub rândul de butoane, nu între ele
    const zonaMesaj = corp.querySelector("#j-mesaj");
    // [617] căutarea (cont, document, partener, sumă, nr. crt.) și starea, în pagină: registrul se citește pe lună, iar notele lunii sunt
    // deja aici — filtrarea nu mai cere serverul. Numărul de lângă câmp spune câte note se văd din câte are luna.
    const tn = randuriJn.length ? legaTabelNote(corp, { pre: "jn", randuri: randuriJn, nrCrt: true, deschise }) : null;
    const aplicaFiltru = () => {
      if (!tn) return;
      const r = tn.filtreaza(filtru.text, filtru.stare);
      const z = corp.querySelector("#jn-numar");
      if (z) z.textContent = filtru.text || filtru.stare ? textNumar(r.vazute, r.total) : "";
    };
    aplicaFiltru();
    const cCauta = corp.querySelector("#jn-cauta"), cStare = corp.querySelector("#jn-stare");
    if (cCauta) cCauta.addEventListener("input", () => { filtru.text = cCauta.value; aplicaFiltru(); });
    if (cStare) cStare.addEventListener("change", () => { filtru.stare = cStare.value; aplicaFiltru(); });
    // [617] confirmarea unei acțiuni pe rând: în zona de mesaj din rezumatul lipit sus (se vede oriunde ar fi derulată fereastra), iar
    // rândul notei rămâne deschis și evidențiat, cu starea nouă
    const confirma = (id, text, tip = "ok") => {
      arataMesaj(corp.querySelector("#j-mesaj"), text, tip);
      const tb = corp.querySelector(`tbody[data-nota-id="${Number(id)}"]`);
      if (tb) tb.classList.add("val-evidentiat");
      return tb;
    };
    const numeNotaJn = (id) => {
      const n = ultimeleNote.find((x) => x.id === Number(id));
      if (!n) return "nota";
      return `nota${n.nr_curent != null ? " nr. crt. " + n.nr_curent : ""} din ${dataRo(n.data)}${n.descriere ? " („" + n.descriere + "”)" : ""}`;
    };
    // [08.10, U3] o singură copie. NU se așteaptă (rezultatul nu e folosit aici): butoanele jurnalului de mai jos se leagă imediat —
    // un clic dat cât blocarea își citește starea se pierdea (proba plasei, 58 și 96)
    legaBlocareLuna(corp.querySelector("#j-lock"), zonaMesaj, t, an, luna, deseneaza);
    const eroare = (e, txt) => { arataMesaj(zonaMesaj, (e && e.mesaj) || txt, "eroare"); };
    corp.querySelector("#j-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#j-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    // [lotul 13, 673] nota nouă: fereastra ei. [602 / 563 / 504] data propusă = ziua de azi (data faptului, DECIZII S2), nu 1 ale lunii; pe o
    // lună alta decât cea curentă câmpul rămâne gol — aplicația nu alege în locul omului o zi din luna răsfoită
    const lunaCurenta = an === azi.getFullYear() && luna === azi.getMonth() + 1;
    corp.querySelector("#j-nota-noua").addEventListener("click", () => {
      const notaNoua = { id: "nou", data: lunaCurenta ? dataIso() : "", descriere: "", linii: [{ debit: "", credit: "", suma: null }] };   // [lotul 10, 10.2 pct.7h] suma goală, nu „0,00”
      deschideActiunea(nav, cheie, { an, luna }, "Notă nouă", (c2) => ecranEditorNota(c2, nav, t, notaNoua, centre, cheie));
    });
    corp.querySelector("#j-amort").addEventListener("click", async () => {
      try {
        const r = await api.post(`/tenants/${t.id}/amortizare?an=${an}&luna=${luna}`, {});
        if (r.linii) {
          // [8c] re-randarea întâi (nota nouă apare în listă), apoi confirmarea în zona de mesaj a ecranului refăcut (DS cap.27, C64):
          // stilul de succes, rândurile notei, „Regenerează” inactiv cu motivul
          await deseneaza({ peLoc: true });
          dupaGenerare(corp.querySelector("#j-mesaj"), corp.querySelector("#j-amort"), {
            titlu: `Amortizarea ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")} generată: ${cate(r.linii, "mijloc fix", "mijloace fixe")}, total ${bani(r.total)} lei`,
            eticheta: r.nota_eticheta ? `Nota ${r.nota_eticheta} — ${stareNota(r)}` : "", linii: r.linii_nota,
            pas: r.inlocuita ? "A înlocuit ciorna de dinainte, scrisă din alt registru." : "",
            motiv: "Nota e generată — o vezi mai jos. „Regenerează” se reactivează după o schimbare în registrul mijloacelor fixe.",
            reactiveazaLaScriere: (cai) => cai.some((c) => /\/(mijloace-fixe|reevaluare-imobilizare|nota-inventariere)/.test(c)) });
        } else {
          arataMesaj(zonaMesaj, "Nimic de amortizat.", "info");   // FARA deseneaza() - altfel sterge mesajul (bug #9)
        }
      } catch (e) { eroare(e, "Eroare la generarea notei de amortizare."); }
    });
    // [386] regula de fond R3 din bază (comanda Costin 09.10.2026 pct.11: „fiecare notă are documentul-sursă”) refuză validarea fără
    // document: pe nota fără document „Validează” e inactiv, cu pasul notei (675; 10.2 pct.7k: un singur mesaj)
    corp.querySelectorAll("[data-val]").forEach((b) => b.addEventListener("click", async () => {
      try {
        await api.post(`/tenants/${t.id}/jurnal/${b.dataset.val}/valideaza`, {});
        await deseneaza({ peLoc: true });
        confirma(b.dataset.val, `Ai validat ${numeNotaJn(b.dataset.val)}: a intrat în evidență.`);
      }
      catch (e) {
        // [lotul 11, 451] ciorna a devenit depășită între încărcarea registrului și validare: rândul o arată, cu refacerea
        if (e && e.detaliu && e.detaliu.cod === "NOTA_DEPASITA") { await deseneaza({ peLoc: true }); arataMesaj(corp.querySelector("#j-mesaj"), e.mesaj, "eroare"); return; }
        eroare(e, "Eroare la validare");
      }
    }));
    // [lotul 11, 451] refacerea ciornei depășite din sursa ei (statul de plată, amortizarea, mișcarea de stoc): o ciornă nouă, de validat
    corp.querySelectorAll("[data-reface]").forEach((b) => b.addEventListener("click", async () => {
      try {
        const r = await api.post(`/tenants/${t.id}/jurnal/${b.dataset.reface}/reface`, {});
        await deseneaza({ peLoc: true });
        arataMesaj(corp.querySelector("#j-mesaj"), r.mesaj, "ok");   // [617] pe loc, cu mesajul serverului (ciorna nouă, de validat)
      } catch (e) { eroare(e, "Nota nu s-a putut reface din sursă."); }
    }));
    if (opt.evidentiaza) {   // [lotul 07.10 pct.8] deschis din notificare: nota ei; [244] din Bilanț: notele de închidere propuse
      // [617] rândul ei, cu detaliul deschis (liniile notei); căutarea / starea aleasă nu o ascund
      const rr = [].concat(opt.evidentiaza).map((id) => corp.querySelector(`[data-nota-id="${Number(id)}"]`)).filter(Boolean);
      rr.forEach((r0) => { r0.classList.add("val-evidentiat"); r0.hidden = false; if (tn) tn.deschide(r0.dataset.tn); });
      if (rr.length) rr[0].scrollIntoView({ block: "center" });
      opt.evidentiaza = null;
    }
    // [lotul 13, 563 / 529] întors din fereastra notei: confirmarea în rezumat, rândul notei salvate evidențiat și adus în vedere
    if (revenire && revenire.mesaj) {
      const r0 = revenire;
      revenire = null;
      const tb = confirma(r0.id, typeof r0.mesaj === "function" ? r0.mesaj(numeNotaJn(r0.id)) : r0.mesaj, r0.tip || "ok");
      if (tb) tb.scrollIntoView({ block: "center" });
    } else revenire = null;
    corp.querySelectorAll("[data-retrimite]").forEach((b) => b.addEventListener("click", async () => {
      try {
        const url = `/tenants/${t.id}/jurnal/${b.dataset.retrimite}/retrimite`;
        const r = await api.post(url, {});
        if (r && r.cod === "NESCHIMBATA") {   // [S3] neschimbată față de cea respinsă: confirmare explicită
          confirmaCaseta(locInDetaliu(b), r.mesaj, async () => {   // [617] întrebarea în detaliul notei, nu între celulele rândului
            try { await api.post(url + "?confirma=true", {}); await deseneaza({ peLoc: true }); confirma(b.dataset.retrimite, `Ai trimis din nou la validare ${numeNotaJn(b.dataset.retrimite)}.`); }
            catch (e2) { arataMesaj(zonaMesaj, (e2 && e2.mesaj) || "Nu s-a putut trimite nota din nou la validare.", "eroare"); }
          }, { textOk: "Retrimite fără schimbări" });
          return;
        }
        await deseneaza({ peLoc: true });
        confirma(b.dataset.retrimite, `Ai trimis la validare ${numeNotaJn(b.dataset.retrimite)}.`);
      }
      catch (e) { arataMesaj(zonaMesaj, (e && e.mesaj) || "Nu s-a putut trimite nota din nou la validare.", "eroare"); }
    }));
    corp.querySelectorAll("[data-del]").forEach((b) => b.addEventListener("click", () => {
      confirmaCaseta(locInDetaliu(b), "Ștergi această ciornă?", async () => {  // audit_cab_lot2_v1
        try {
          const nume = numeNotaJn(b.dataset.del);
          await api.del(`/tenants/${t.id}/jurnal/${b.dataset.del}`);
          deschise.delete(String(b.dataset.del));
          await deseneaza({ peLoc: true });
          arataMesaj(corp.querySelector("#j-mesaj"), `Ai șters ciorna: ${nume}.`, "ok");
        }
        catch (e) { eroare(e, "Eroare la ștergere"); }
      }, { textOk: "Șterge" });
    }));
    // [lotul 13, 673] editarea: fereastra ei (nu în rândul notei), cu nota citită acum
    corp.querySelectorAll("[data-edit]").forEach((b) => b.addEventListener("click", () => {
      const n = ultimeleNote.find((x) => x.id === Number(b.dataset.edit));
      if (n) deschideActiunea(nav, cheie, { an, luna }, "Editare notă" + (n.nr_curent != null ? " nr. crt. " + n.nr_curent : ""),
        (c2) => ecranEditorNota(c2, nav, t, n, centre, cheie));
    }));
  };
  // [265] drepturile schimbate în sesiunea deschisă: „de validat”, „Trimite la validare” se calculează la desenare, deci jurnalul se
  // redesenează; fereastra închisă își scoate ascultătorul
  const laDrepturi = () => {
    if (!corp.isConnected) { window.removeEventListener("iconta:drepturi", laDrepturi); return; }
    poateValida = permis("POST /tenants/{tenant_id}/jurnal/{nota_id}/valideaza");
    deseneaza({ peLoc: true });
  };
  window.addEventListener("iconta:drepturi", laDrepturi);
  // [673] registrul păstrat (omul scrisese în căutare) se redesenează el la închiderea ferestrei notei, cu confirmarea
  corp.addEventListener("nav:revenire", () => {
    revenire = starePastrata(cheie);
    if (!revenire) return;
    if (revenire.an && revenire.luna) { an = revenire.an; luna = revenire.luna; }
    deseneaza({ peLoc: true });
  });
  deseneaza();
}

// [lotul 13, 673] nota nouă / editarea unei ciorne — fereastra ei (DS cap.2a v2.104), aceleași câmpuri ca editorul de până acum (data,
// descrierea, documentul justificativ, liniile cu centrul de cost și partenerul). După „Salvează” fereastra se închide, iar Registrul jurnal
// se redesenează pe luna notei, cu rândul ei evidențiat și confirmarea (563 / 529); refuzul rămâne aici, lângă câmpuri.
function ecranEditorNota(corp, nav, t, n, centre, cheie) {
  const nou = n.id === "nou" || !n.id;
  const optCentru = (sel) => `<option value="">— centru —</option>` +
    centre.map((c) => `<option value="${c.id}"${sel === c.id ? " selected" : ""}>${esc(c.nume)}</option>`).join("");
  const linieNota = (l = {}) => `
    <input type="text" class="camp-input je-deb" placeholder="debit" aria-label="Cont debit" value="${esc(l.debit || "")}" style="width:90px">
    <span style="align-self:center">=</span>
    <input type="text" class="camp-input je-cre" placeholder="credit" aria-label="Cont credit" value="${esc(l.credit || "")}" style="width:90px">
    <input type="number" step="0.01" class="camp-input je-sum" placeholder="sumă" aria-label="Sumă" value="${l.suma == null ? "" : Number(l.suma).toFixed(2)}" style="width:120px">
    <select class="camp-input je-centru" aria-label="Centru de cost" style="width:140px">${optCentru(l.centru_cost_id)}</select>
    <input type="text" class="camp-input je-pcui" placeholder="CUI partener" aria-label="Codul fiscal al partenerului (401 / 4111)" value="${esc(l.partener_cui || "")}" style="width:120px">
    <input type="text" class="camp-input je-pnume" placeholder="partener (la 401 / 4111)" aria-label="Partenerul (furnizor / client), cerut la 401 și 4111" value="${esc(l.partener_nume || "")}" style="width:200px">
    <button type="button" class="buton-secundar je-scoate" aria-label="Scoate linia">−</button>`;
  corp.innerHTML = `
    <h2 class="pf-titlu" id="je-titlu">${nou ? "Notă nouă" : "Editare notă" + (n.nr_curent != null ? " nr. crt. " + n.nr_curent : "")}<span id="je-titlu-data">${n.data ? " · " + dataRo(n.data) : ""}</span></h2>
    ${n.factura_id ? `<div class="caseta-atentie" style="margin-bottom:8px"><div class="ca-mesaj">Atenție: nota e legată de ${n.document ? esc(n.document) : "o factură"} — modificarea sumei schimbă soldul facturii.</div></div>` : ""}
    <div class="grila-campuri" id="je-antet">   <!-- [lotul 11, 394 la 1280×720 — decizia Costin 10.3: „totul încape într-un ecran, fără derulare”] data, descrierea și documentul pe un rând (se rup pe telefon) -->
    <label class="camp"><span class="camp-eticheta">Data notei<span class="oblig">*</span></span><input type="date" id="je-data" class="camp-input" value="${esc(String(n.data || "").slice(0, 10))}"></label>
    <label class="camp"><span class="camp-eticheta">Descriere</span><input type="text" id="je-desc" class="camp-input" style="width:100%" value="${esc(n.descriere || "")}"></label>
    <label class="camp"><span class="camp-eticheta">Document justificativ (fel, număr, dată)</span><input type="text" id="je-doc" class="camp-input" style="width:100%" placeholder="ex: Factură CH-9 din 01.10.2026" value="${esc(n.document_ref || "")}"></label>
    </div>
    <div class="camp-eticheta" style="margin-top:8px">Linii: cont debit = cont credit · sumă</div>
    <div id="je-linii">${n.linii.map((l, i) => `<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:6px" data-lin="${i}">${linieNota(l)}</div>`).join("")}</div>
    <p><button type="button" class="buton-secundar" id="je-plus" data-fara-actiune="rând în formular; salvarea formularului poartă acțiunea">+ linie</button></p>
    <div class="bara-fixa"><p style="margin-top:10px">
      <button class="buton-primar" id="je-salveaza" data-actiune="POST /tenants/{tenant_id}/jurnal|PUT /tenants/{tenant_id}/jurnal/{nota_id}">Salvează</button>
      <button type="button" class="buton-secundar" id="je-renunta" data-fara-actiune="închide fereastra, fără scriere" style="margin-left:6px">Renunță</button>
    </p><div id="je-mesaj"></div></div>`;
  // [deficiența 260] titlul editorului urmează data aleasă (era data de la deschidere: „Notă nouă · 01.10.2026”)
  const _jeData = corp.querySelector("#je-data");
  const _jeTitlu = corp.querySelector("#je-titlu-data");
  const _titluData = () => { _jeTitlu.textContent = _jeData.value ? " · " + dataRo(_jeData.value) : ""; };
  _jeData.addEventListener("input", _titluData);
  _jeData.addEventListener("change", _titluData);
  const zona = corp.querySelector("#je-linii");
  const leaga = () => zona.querySelectorAll(".je-scoate").forEach((b) => {
    if (b.__legat) return;
    b.__legat = true;
    b.addEventListener("click", () => { if (zona.children.length > 1) b.parentElement.remove(); });
  });
  leaga();
  corp.querySelector("#je-plus").addEventListener("click", () => {
    const d = document.createElement("div");
    d.style.cssText = "display:flex;flex-wrap:wrap;gap:8px;margin-bottom:6px";
    d.innerHTML = linieNota();
    zona.appendChild(d); leaga();
  });
  corp.querySelector("#je-renunta").addEventListener("click", () => nav.inapoi());
  focusFaraSalt(nou ? _jeData : corp.querySelector("#je-desc"));
  corp.querySelector("#je-salveaza").addEventListener("click", async () => {
    const zonaMesaj = corp.querySelector("#je-mesaj");
    // [lotul 10, comanda 10.2 pct.7h] „câmpurile de sumă sunt goale”: suma necompletată nu pleacă drept 0 (serverul ar spune „suma 0”,
    // pe care omul n-a scris-o) — se cere lângă câmpul ei. [602 / 504] data notei la fel: câmpul gol se cere, nu se completează
    curataEroriCamp(corp);
    const sume = [...zona.querySelectorAll(".je-sum")];
    sume.forEach((x, i) => { x.id = "je-sum-" + i; });
    // [lotul 11, 440] fiecare câmp al liniei are id-ul pe care îl numește refuzul serverului (`jurnal_api._CAMP_LINIE`: `je-deb-<i>` …),
    // ca toate erorile notei să stea lângă câmpurile lor, nu numai suma
    [...zona.children].forEach((r, i) => [["je-deb", ".je-deb"], ["je-cre", ".je-cre"], ["je-pcui", ".je-pcui"], ["je-pnume", ".je-pnume"]]
      .forEach(([id, sel]) => { const x = r.querySelector(sel); if (x) x.id = `${id}-${i}`; }));
    let lipsa = false;
    if (!_jeData.value) { eroareCamp(corp, "je-data", "Completează data notei (ziua documentului)."); lipsa = true; }
    const goale = sume.filter((x) => x.value.trim() === "");
    goale.forEach((x) => eroareCamp(corp, x.id, "Scrie suma liniei."));
    if (goale.length || lipsa) return;
    const linii = [...zona.children].map((r) => ({
      debit: r.querySelector(".je-deb").value.trim(),
      credit: r.querySelector(".je-cre").value.trim(),
      suma: parseFloat(r.querySelector(".je-sum").value) || 0,
      centru_cost_id: (r.querySelector(".je-centru") && r.querySelector(".je-centru").value) || null,  // [F143]
      partener_cui: r.querySelector(".je-pcui").value.trim(), partener_nume: r.querySelector(".je-pnume").value.trim(),   // [381]
    }));
    const corpCerere = { descriere: corp.querySelector("#je-desc").value, data: _jeData.value, linii, document_ref: corp.querySelector("#je-doc").value };
    try {
      // [lotul 07.10 pct.5] data se corectează din editor (motivul tipic de respingere); luna nouă trebuie să fie deschisă
      const rs = nou ? await api.post(`/tenants/${t.id}/jurnal`, corpCerere) : await api.put(`/tenants/${t.id}/jurnal/${n.id}`, corpCerere);
      const idNota = nou ? (rs && (rs.id || rs.nota_id)) : n.id;
      const dz = new Date(_jeData.value + "T00:00:00");
      // [08.10, V3] contul din afara planului legal al normei: nota se scrie, dar nu fără avertisment (avertismentul înlocuiește confirmarea)
      // [279] starea reală a notei (ciornă / trimisă la validare în cabinet, antetul cozii pus de api.js), nu „ciornă” scris de mână
      const stare = stareNota(rs), extra = rs && rs.mesaj ? " " + rs.mesaj.charAt(0).toUpperCase() + rs.mesaj.slice(1) + "." : "";
      inchideCuConfirmarea(nav, cheie, rs && rs.avertisment ? (rs.avertisment.motiv || "Cont în afara planului legal.") : ((nume) => `Ai salvat ${nume} (${stare}).${extra}`),
        { an: dz.getFullYear(), luna: dz.getMonth() + 1, id: idNota, tip: rs && rs.avertisment ? "avert" : "ok" });
    } catch (e) {   // [lotul 11, 440] toate erorile notei (data, fiecare câmp al fiecărei linii) lângă câmpurile lor, restul sub buton
      arataRefuzul(corp, e && e.mesaj ? e : { ...(e || {}), mesaj: "Eroare la salvare" }, zonaMesaj, { campuri: { descriere: "je-desc", document_ref: "je-doc", data: "je-data" } });
    }
  });
}


// [F143] Centre de cost — nomenclator de management (dimensiune pe notele manuale)
// [Retest 2 pct.13, decizia Costin O12] Planul de conturi al firmei, pe tiparul registrelor: căutare după cont sau denumire, analiticele
// sub sinteticul lor, adăugarea unui analitic (de pe rândul sinteticului sau din formular), ștergerea refuzată pentru un cont folosit
// în note (serverul spune de ce; butonul nici nu apare pe un cont folosit). DS cap.24 (v2.85).
// [589] separatorii analiticului — aceiași ca serverul (`uc_tenants.SEPARATORI_ANALITIC`, păzit de `core/test_lot13_firme2_plan_conturi.py`)
const SEPARATORI_ANALITIC = "._-/";
async function ecranPlanConturi(corp, nav, t) {
  let conturi = [];
  corp.innerHTML = `<p class="ecran-nota">Se încarcă planul de conturi…</p>`;
  try { const r = await api.get(`/tenants/${t.id}/plan-conturi`); conturi = (r && r.conturi) || []; }
  catch (e) { corp.innerHTML = `<p class="ecran-nota">Nu s-a putut încărca planul de conturi.</p>`; return; }
  corp.innerHTML = `
    <h2 class="pf-titlu">Plan de conturi</h2>
    <p class="pf-intro">Conturile firmei: sinteticele planului general și analiticele adăugate de tine, sub contul lor; manual se adaugă numai analitice, sub un sintetic din planul legal.</p>
    <input type="text" class="camp-input" id="pcf-cauta" aria-label="Caută cont" placeholder="Caută după cont sau denumire…" style="width:100%;max-width:520px;margin-bottom:10px">
    <div class="mig-eticheta">Adaugă analitic</div>
    <span class="camp-ajutor">Analiticul se scrie după contul sintetic, cu punct: 4111.01, 401.07.</span>
    <div style="display:flex;gap:8px;margin:6px 0 4px;flex-wrap:wrap;max-width:620px">
      <input type="text" class="camp-input" id="pcf-simbol" aria-label="Simbol cont" placeholder="ex. 4111.01" style="width:160px">
      <input type="text" class="camp-input" id="pcf-denumire" aria-label="Denumire cont" placeholder="Denumire" style="flex:1;min-width:180px">
      <button class="buton-primar" id="pcf-adauga" data-actiune="POST /tenants/{tenant_id}/plan-conturi">Adaugă</button>
    </div>
    <div id="pcf-simbol-avert"></div>
    <div id="pcf-mesaj"></div>
    <div class="pf-lista zebra-lista" id="pcf-lista"></div>`;
  const lista = corp.querySelector("#pcf-lista"), msg = corp.querySelector("#pcf-mesaj");
  const inpS = corp.querySelector("#pcf-simbol"), inpD = corp.querySelector("#pcf-denumire"), campCautare = corp.querySelector("#pcf-cauta");
  // [lotul 13, 675] aceleași două butoane pe fiecare cont; ce nu se aplică stă inactiv, cu motivul (DS cap.1 v2.104) — și „Șterge” spune
  // de ce contul nu se șterge (589: „contul nu se poate șterge” fără să știi de ce); contul fără rulaj, sold sau analitice se șterge
  const rand = (c, analitic) => `
    <div class="pf-frand" data-simbol="${esc(c.simbol)}"${analitic ? ' style="padding-left:28px"' : ""}>
      <div class="pf-frand-text">
        <div class="pf-frand-nume">${esc(c.simbol)} \u00b7 ${esc(c.denumire)}</div>
        <div class="pf-frand-sub">${analitic ? "analitic" : "sintetic"}${c.folosit ? " \u00b7 folosit în note" : ""}${c.in_afara_planului ? " \u00b7 în afara planului legal al normei firmei" : ""}</div>
      </div>
      <div class="pf-frand-butoane">
      ${butonRand("buton-secundar buton-mic", `data-analitic="${esc(c.simbol)}" data-fara-actiune="completează formularul de mai sus; Adaugă poartă acțiunea"`, "Adaugă analitic",
        analitic ? "Analiticul nou se adaugă de pe rândul contului sintetic." : c.in_afara_planului ? "Contul nu e în planul legal al normei firmei: sub el nu se adaugă analitice." : null)}
      ${butonRand("buton-secundar buton-mic", `data-sterge="${esc(c.simbol)}" data-actiune="DELETE /tenants/{tenant_id}/plan-conturi/{simbol}"`, "Șterge",
        c.nu_se_sterge ? `Contul nu se șterge: ${c.nu_se_sterge}.` : null)}
      </div>
    </div>`;
  // [589] „avertismentul apare după salvare”: aceeași regulă ca serverul (`plan_legal.refuz_adaugare_manuala`), spusă cât scrii simbolul,
  // din lista conturilor deja citită (sinteticul analiticului și dacă e în planul legal); serverul rămâne cel care refuză la salvare
  const motivAdaugare = (simbol) => {
    const sm = String(simbol || "").trim();
    if (!sm) return "";
    const poz = [...SEPARATORI_ANALITIC].map((ch) => sm.indexOf(ch)).filter((i) => i >= 0);
    const sint = poz.length ? sm.slice(0, Math.min(...poz)) : null;
    if (!sint) return `Contul ${sm} e sintetic: sinteticele vin din planul general de conturi și sunt deja în planul firmei. Manual se adaugă numai un analitic, sub sinteticul lui (de exemplu ${sm}.01).`;
    const c = conturi.find((x) => x.simbol === sint);
    if (!c) return `Contul sintetic ${sint} nu e în planul firmei: analiticul se adaugă sub un cont sintetic din plan.`;
    if (c.in_afara_planului) return `Contul sintetic ${sint} nu e în planul de conturi al normei firmei: sub el nu se adaugă analitice.`;
    return "";
  };
  const zAvert = corp.querySelector("#pcf-simbol-avert");
  const arataAvert = () => {
    const m = motivAdaugare(inpS.value);
    zAvert.innerHTML = m ? `<div class="caseta-atentie" id="pcf-avert"><div class="ca-mesaj">${esc(m)}</div></div>` : "";
  };
  inpS.addEventListener("input", arataAvert);
  const deseneaza = () => {
    const q = campCautare.value.trim().toLowerCase();
    // [deficiența 219, retestul Costin 09.10: „căutarea «73» găsește și 473; căutarea după simbol potrivește începutul”] un text care
    // începe cu cifră e un simbol: se potrivește începutul lui; altfel se caută în denumire (și în simbol)
    const dupaSimbol = /^\d/.test(q);
    const potriveste = (c) => !q || (dupaSimbol ? c.simbol.toLowerCase().startsWith(q)
      : (c.simbol.toLowerCase().includes(q) || (c.denumire || "").toLowerCase().includes(q)));
    const sintetice = conturi.filter((c) => !c.sintetic);
    const analitice = conturi.filter((c) => c.sintetic);
    const sub = (s) => analitice.filter((a) => a.sintetic === s);
    // un sintetic apare dacă se potrivește el sau unul dintre analiticele lui; analiticul fără sintetic în plan apare singur
    const blocuri = sintetice.map((s) => {
      const copii = sub(s.simbol);
      const copiiVazuti = potriveste(s) ? copii : copii.filter(potriveste);
      if (!potriveste(s) && !copiiVazuti.length) return "";
      return rand(s, false) + copiiVazuti.map((a) => rand(a, true)).join("");
    });
    const orfane = analitice.filter((a) => !sintetice.some((s) => s.simbol === a.sintetic) && potriveste(a)).map((a) => rand(a, true));
    const html = blocuri.join("") + orfane.join("");
    lista.innerHTML = html || `<div class="stare-goala">Niciun cont cu „${esc(campCautare.value.trim())}” în simbol sau denumire. Caută după alt termen, sau adaugă contul mai sus.</div>`;
    lista.querySelectorAll("[data-analitic]").forEach((b) => b.addEventListener("click", () => {
      inpS.value = b.dataset.analitic + "."; focusFaraSalt(inpD);
    }));
    lista.querySelectorAll("[data-sterge]").forEach((b) => b.addEventListener("click", () => {
      confirmaCaseta(b.parentElement || b, `Ștergi contul ${b.dataset.sterge} din planul firmei?`, async () => {
        try {
          await api.del(`/tenants/${t.id}/plan-conturi/${encodeURIComponent(b.dataset.sterge)}`);
          conturi = conturi.filter((c) => c.simbol !== b.dataset.sterge);
          deseneaza();
          arataMesaj(msg, `Contul ${b.dataset.sterge} a fost șters din plan.`, "ok");
        } catch (e) { arataMesaj(msg, (e && e.mesaj) || "Contul nu s-a putut șterge.", "eroare"); }
      }, { textOk: "Șterge" });
    }));
  };
  let timer = null;
  campCautare.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(deseneaza, 200); });
  const cerereConturi = ultimaCerere();   // [C103] două adăugări la rând: lista recitită după prima nu acoperă lista de după a doua
  corp.querySelector("#pcf-adauga").addEventListener("click", async () => {
    const simbol = inpS.value.trim(), denumire = inpD.value.trim();
    // [lotul 11, 440] amândouă câmpurile goale se marchează deodată; înainte `eroareCamp("pcf-simbol", …)` fără rădăcină arunca TypeError
    // („pcf-simbol”.querySelector) — clicul nu arăta nimic
    if (cereCompletate(corp, [{ id: "pcf-simbol", mesaj: "Completează simbolul contului (ex. 4111.01)." },
      { id: "pcf-denumire", mesaj: "Completează denumirea contului." }])) return;
    const motiv = motivAdaugare(simbol);   // [589] refuzat înainte de salvare, lângă câmp — nu „avertisment după salvare”
    if (motiv) { eroareCamp(corp, "pcf-simbol", motiv); return; }
    let rs;
    try {
      rs = await api.post(`/tenants/${t.id}/plan-conturi`, { simbol, denumire });
    } catch (e) {   // [lotul 11, 440] erorile serverului lângă câmpurile lor, textul refuzului în zona mesajului
      arataRefuzul(corp, e && e.mesaj ? e : { ...(e || {}), mesaj: "Contul nu s-a putut adăuga." }, msg, { campuri: { simbol: "pcf-simbol", denumire: "pcf-denumire" } });
      return;
    }
    // [C103] refuzul salvării se arată mereu (mai sus); numai recitirea listei de după ea se lasă în seama ultimei cereri
    const actuala = cerereConturi();
    try {
      const r = await api.get(`/tenants/${t.id}/plan-conturi`);
      if (!actuala()) return;
      conturi = (r && r.conturi) || [];
      inpS.value = ""; inpD.value = ""; arataAvert();
      campCautare.value = rs.simbol; deseneaza();
      arataMesaj(msg, rs.avertisment ? (rs.avertisment.motiv || "Cont în afara planului legal.") : `Contul ${rs.simbol} a fost adăugat.`,
        rs.avertisment ? "avert" : "ok");
    } catch (e) {
      if (!actuala()) return;
      arataMesaj(msg, `Contul ${rs.simbol} a fost adăugat, dar lista nu s-a putut reîncărca: ${(e && e.mesaj) || "reîncearcă"}.`, "avert");
    }
  });
  deseneaza();
}

async function ecranCentreCost(corp, nav, t) {
  const azi = new Date();
  const anCur = azi.getFullYear();
  const aziIso = `${anCur}-${String(azi.getMonth() + 1).padStart(2, "0")}-${String(azi.getDate()).padStart(2, "0")}`;
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    let centre = [];
    try { const r = await api.get(`/tenants/${t.id}/centre-cost`); centre = (r && r.centre) || []; } catch { corp.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca centrele de cost.</p>`; return; }
    const rand = (c) => `
      <div class="pf-frand">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(c.nume)}</div>
          <div class="pf-frand-sub">${c.activ ? "activ" : "inactiv — nu se mai oferă la note noi"}</div>
        </div>
        <button class="buton-secundar" data-toggle="${c.id}" data-actiune="PUT /tenants/{tenant_id}/centre-cost/{centru_id}" data-activ="${c.activ ? 1 : 0}">${c.activ ? "Dezactivează" : "Reactivează"}</button>
      </div>`;
    corp.innerHTML = `
      <h2 class="pf-titlu">Centre de cost</h2>
      <p class="pf-intro">Dimensiune de management pe rândurile de venituri și cheltuieli: se alege pe notele manuale (Registru jurnal) și pe liniile facturilor (emise și primite); salariații, mijloacele fixe și articolele de stoc își primesc centrul în „Salariați, mijloace fixe, articole”, iar nota salariilor, amortizarea și ieșirea din stoc îl preiau. Un centru scos din uz se dezactivează — rămâne pe notele vechi, nu se mai oferă la note noi.</p>
      <div style="display:flex;gap:8px;max-width:760px;margin-bottom:12px;flex-wrap:wrap">
        <input type="text" id="cc-nume" class="camp-input" placeholder="Nume centru (ex: Vânzări, Producție)" aria-label="Nume centru" style="flex:1">
        <button class="buton-primar" id="cc-add" data-actiune="POST /tenants/{tenant_id}/centre-cost">Adaugă</button>
        <button class="buton-secundar" id="cc-alocari" data-fara-actiune="citire: salariații, mijloacele fixe și articolele cu centrul lor">Salariați, mijloace fixe, articole</button>
      </div>
      <div id="cc-mesaj"></div>
      <div class="pf-lista">${centre.length ? centre.map(rand).join("") : '<div class="stare-goala">Niciun centru încă. Adaugă primul.</div>'}</div>
      <h3 class="cap-titlu" style="margin-top:22px">Realizat pe centre</h3>
      <p class="pf-intro">Din notele validate: cheltuieli (clasa 6) și venituri (clasa 7) pe fiecare centru, în perioada aleasă.</p>
      <div style="display:flex;gap:8px;align-items:center;margin-bottom:10px;flex-wrap:wrap">
        <input type="date" id="cc-de" class="camp-input" value="${anCur}-01-01" style="width:160px" aria-label="De la">
        <span>–</span>
        <input type="date" id="cc-pana" class="camp-input" value="${aziIso}" style="width:160px" aria-label="Până la">
        <button class="buton-secundar" id="cc-raport">Vezi realizat</button>
      </div>
      <div id="cc-raport-zona"></div>
      <h3 class="cap-titlu" style="margin-top:22px">Bugete și varianță (anual)</h3>
      <p class="pf-intro">Plan anual pe centru (cheltuieli + venituri), comparat cu realizatul din notele validate ale anului. Abaterea e colorată: <b>roșu</b> = orice abatere nefavorabilă (cheltuieli peste buget sau venituri sub plan), <b>verde</b> = favorabil sau exact pe țintă. Fără culoare dacă bugetul respectiv nu e setat.</p>
      <div style="display:flex;gap:8px;align-items:center;margin-bottom:10px">
        <label class="camp-eticheta" for="cc-an">An</label>
        <input type="number" id="cc-an" class="camp-input" value="${anCur}" style="width:100px">
        <button class="buton-secundar" id="cc-bugete">Vezi bugete</button>
      </div>
      <div id="cc-bugete-zona"></div>`;
    const msg = corp.querySelector("#cc-mesaj");
    const adauga = async () => {
      const nume = corp.querySelector("#cc-nume").value.trim();
      if (!nume) { arataMesaj(msg, "Scrie un nume.", "eroare"); return; }
      try { await api.post(`/tenants/${t.id}/centre-cost`, { nume }); deseneaza(); }
      catch (e) { arataMesaj(msg, (e && e.mesaj) || "Eroare la adăugare.", "eroare"); }
    };
    corp.querySelector("#cc-add").addEventListener("click", adauga);
    // [lotul 13, 536, DS cap.2a — acțiunea din fereastră deschide o fereastră nouă] alocarea salariaților și a mijloacelor fixe pe centre
    corp.querySelector("#cc-alocari").addEventListener("click", () => nav.deschide("Salariați, mijloace fixe și articole pe centre",
      (c2) => ecranAlocariCentre(c2, nav, t)));
    corp.querySelector("#cc-nume").addEventListener("keydown", (e) => { if (e.key === "Enter") adauga(); });
    corp.querySelectorAll("[data-toggle]").forEach((b) => b.addEventListener("click", async () => {
      try { await api.put(`/tenants/${t.id}/centre-cost/${b.dataset.toggle}`, { activ: b.dataset.activ !== "1" }); deseneaza(); }
      catch (e) { arataMesaj(msg, (e && e.mesaj) || "Eroare.", "eroare"); }
    }));
    const raportZona = corp.querySelector("#cc-raport-zona");
    const linieRaport = (nume, ch, ve, net, inactiv) => `
      <div class="pf-frand">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(nume)}${inactiv ? " · <span style='color:var(--gri)'>inactiv</span>" : ""}</div>
          <div class="pf-frand-sub">cheltuieli ${bani(ch)} · venituri ${bani(ve)}</div>
        </div>
        <div style="font-weight:600;align-self:center;color:${net >= 0 ? 'var(--verde)' : 'var(--rosu)'}">${bani(net)}</div>
      </div>`;
    corp.querySelector("#cc-raport").addEventListener("click", async () => {
      const de = corp.querySelector("#cc-de").value, pana = corp.querySelector("#cc-pana").value;
      if (!de || !pana) { arataMesaj(msg, "Alege perioada.", "eroare"); return; }
      raportZona.innerHTML = `<p class="ecran-nota">Se calculează...</p>`;
      try {
        const r = await api.get(`/tenants/${t.id}/centre-cost/raport?de=${de}&pana=${pana}`);
        const centre = (r && r.centre) || [];
        const nz = (r && r.nealocat) || { cheltuieli: 0, venituri: 0 };
        let html = centre.length
          ? centre.map((c) => linieRaport(c.nume, c.cheltuieli, c.venituri, c.net, !c.activ)).join("")
          : `<div class="stare-goala">Niciun centru definit.</div>`;
        if (nz.cheltuieli || nz.venituri) {
          html += linieRaport("Nealocat (fără centru)", nz.cheltuieli, nz.venituri, nz.venituri - nz.cheltuieli, false);
        }
        raportZona.innerHTML = `<div class="pf-lista">${html}</div>`;
      } catch (e) { arataMesaj(raportZona, (e && e.mesaj) || "Eroare la raport.", "eroare"); }
    });
    // [F143 Faza 2] bugete anuale + varianta buget vs realizat
    const bugeteZona = corp.querySelector("#cc-bugete-zona");
    const randBuget = (c) => {
      const dch = c.realizat_cheltuieli - c.buget_cheltuieli;  // >0 = peste buget (rau la cheltuieli)
      const dve = c.realizat_venituri - c.buget_venituri;      // >=0 = peste plan (bun la venituri)
      const chTxt = c.buget_cheltuieli ? ` <span style="color:${dch > 0 ? 'var(--rosu)' : 'var(--verde)'}">(${dch > 0 ? '+' : ''}${bani(dch)})</span>` : "";
      const veTxt = c.buget_venituri ? ` <span style="color:${dve >= 0 ? 'var(--verde)' : 'var(--rosu)'}">(${dve >= 0 ? '+' : ''}${bani(dve)})</span>` : "";
      return `<div class="pf-frand" style="align-items:center">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(c.nume)}${c.activ ? "" : " · <span style='color:var(--gri)'>inactiv</span>"}</div>
          <div class="pf-frand-sub">chelt: buget ${bani(c.buget_cheltuieli)} / realizat ${bani(c.realizat_cheltuieli)}${chTxt} · venit: buget ${bani(c.buget_venituri)} / realizat ${bani(c.realizat_venituri)}${veTxt}</div>
        </div>
        <div style="display:flex;gap:6px;align-items:center">
          <input type="number" step="0.01" class="camp-input bg-ch" value="${c.buget_cheltuieli}" style="width:100px" aria-label="Buget cheltuieli">
          <input type="number" step="0.01" class="camp-input bg-ve" value="${c.buget_venituri}" style="width:100px" aria-label="Buget venituri">
          <button class="buton-secundar bg-save" data-actiune="PUT /tenants/{tenant_id}/centre-cost/{centru_id}/buget" data-c="${c.id}">Salvează</button>
        </div>
      </div>`;
    };
    const incarcaBugete = async () => {
      const an = parseInt(corp.querySelector("#cc-an").value) || anCur;
      bugeteZona.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
      try {
        const r = await api.get(`/tenants/${t.id}/centre-cost/varianta?an=${an}`);
        const centre = (r && r.centre) || [];
        bugeteZona.innerHTML = centre.length
          ? `<div class="pf-lista">${centre.map(randBuget).join("")}</div>`
          : `<div class="stare-goala">Niciun centru definit — adaugă un centru mai sus.</div>`;
        bugeteZona.querySelectorAll(".bg-save").forEach((b) => b.addEventListener("click", async () => {
          const row = b.closest(".pf-frand");
          try {
            await api.put(`/tenants/${t.id}/centre-cost/${b.dataset.c}/buget`,
              { an, buget_cheltuieli: row.querySelector(".bg-ch").value, buget_venituri: row.querySelector(".bg-ve").value });
            incarcaBugete();
          } catch (e) { arataMesaj(msg, (e && e.mesaj) || "Eroare la salvare buget.", "eroare"); }
        }));
      } catch (e) { arataMesaj(bugeteZona, (e && e.mesaj) || "Eroare.", "eroare"); }
    };
    corp.querySelector("#cc-bugete").addEventListener("click", incarcaBugete);
  };
  deseneaza();
}


// [lotul 13, deficiența 536 — comanda Costin 13.1, verbatim: „Centrul se poate pune pe liniile facturilor, NIR-urilor, salariilor și pe
// mijloacele fixe (amortizarea moștenește centrul activului)”; NIR-ul, decizia Costin (a): „centrul pe articol sau pe gestiune, ieșirea
// din stoc îl moștenește” — al treilea tabel, articolele de stoc] Centrul fiecărui salariat (nota salariilor își împarte cheltuielile cu
// personalul pe centre, după brutul fiecăruia) și al fiecărui mijloc fix (amortizarea și celelalte rânduri de cheltuială ale activului îl
// preiau). Se aplică notelor generate de acum; o notă deja scrisă rămâne cum e. Se salvează numai rândurile schimbate; un centru
// dezactivat rămâne afișat pe rândul care îl are, dar nu se mai poate alege.
async function ecranAlocariCentre(corp, nav, t) {
  const cerere = ultimaCerere();
  const actuala = cerere();
  corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
  let r;
  try { r = await api.get(`/tenants/${t.id}/centre-cost`); if (!actuala()) return; }
  catch (e) { if (!actuala()) return; corp.innerHTML = `<p class="ecran-nota pe-randuri">${esc((e && e.mesaj) || "Centrele de cost nu s-au putut încărca.")}</p>`; return; }
  const toate = (r && r.centre) || [], al = (r && r.alocari) || { salariati: [], mijloace: [] };
  const active = toate.filter((c) => c.activ);
  // lista rândului: centrele active, plus centrul dezactivat pe care rândul îl are deja (numit „inactiv”, ca să nu se piardă tăcut)
  const optiuni = (ales) => active.concat(toate.filter((c) => !c.activ && c.id === ales).map((c) => ({ ...c, nume: c.nume + " (inactiv)" })));
  const rand = (pre, x, celule, eticheta) => `<tr><td>${celule}</td><td>${htmlCentru(`cc-${pre}-${x.id}`, "cc-aloc", optiuni(x.centru_cost_id),
    x.centru_cost_id, eticheta, "", `data-fel="${pre}" data-id="${x.id}" data-initial="${x.centru_cost_id || ""}"`)}</td></tr>`;
  const tabel = (titlu, cap, randuri, gol) => `<h3 class="cap-titlu" style="margin-top:14px">${titlu}</h3>${randuri.length
    ? `<table class="fd-tabel"><thead><tr><th>${cap}</th><th>Centru de cost</th></tr></thead><tbody>${randuri.join("")}</tbody></table>`
    : `<div class="stare-goala">${gol}</div>`}`;
  corp.innerHTML = `
    <div class="rezumat-fix"><h2 class="pf-titlu">Salariați, mijloace fixe și articole pe centre</h2>
      <p class="pf-intro">Centrul salariatului împarte nota salariilor pe centre (cheltuielile cu personalul, după brutul fiecăruia); centrul mijlocului fix merge pe amortizarea lui și pe celelalte rânduri de cheltuială ale activului; centrul articolului de stoc merge pe ieșirea lui din gestiune (cheltuiala cu marfa, materialele, consumul) — NIR-ul intră pe stoc, iar cheltuiala apare la ieșire. Se aplică notelor generate de acum — o notă deja scrisă rămâne cum e.</p></div>
    ${active.length ? "" : `<div class="caseta-info"><span class="ci-mesaj">Firma n-are niciun centru de cost activ: adaugă întâi unul în fereastra Centre de cost.</span></div>`}
    ${tabel("Salariați", "Salariat", al.salariati.map((x) => rand("sal", x, esc(x.nume || ""), "Centrul de cost al salariatului " + (x.nume || ""))),
            "Firma n-are salariați în serviciu.")}
    ${tabel("Mijloace fixe", "Mijloc fix", al.mijloace.map((x) => rand("mf", x, esc([x.cod, x.denumire].filter(Boolean).join(" · ")),
            "Centrul de cost al mijlocului fix " + (x.denumire || x.cod || ""))), "Firma n-are mijloace fixe în registru.")}
    ${tabel("Articole de stoc", "Articol", (al.articole || []).map((x) => rand("art", x, esc([x.denumire, x.um, x.cont_stoc].filter(Boolean).join(" · ")),
            "Centrul de cost al articolului " + (x.denumire || ""))), "Firma n-are articole de stoc (ieșirea pe articol e a firmelor cu stocul la cost).")}
    <div class="bara-fixa"><p style="margin-top:10px"><button class="buton-primar" id="cc-aloc-salveaza" data-actiune="PUT /tenants/{tenant_id}/centre-cost/alocari"${active.length ? "" : atributeInactiv("Firma n-are niciun centru de cost activ.")}>Salvează alocarea</button>
      <button class="buton-secundar" data-renunta style="margin-left:6px">Renunță</button></p><div id="cc-aloc-mesaj"></div></div>`;
  legaRenunta(corp, nav);
  const msg = corp.querySelector("#cc-aloc-mesaj");
  corp.querySelector("#cc-aloc-salveaza").addEventListener("click", async () => {
    curataEroriCamp(corp);
    const corpReq = { salariati: {}, mijloace: {}, articole: {} };
    corp.querySelectorAll("select.cc-aloc").forEach((s) => {
      if (s.value !== s.dataset.initial) corpReq[{ sal: "salariati", mf: "mijloace", art: "articole" }[s.dataset.fel]][s.dataset.id] = valoareCentru(s.value);
    });
    const n = Object.values(corpReq).reduce((t, g) => t + Object.keys(g).length, 0);
    if (!n) { arataMesaj(msg, "Nimic schimbat: alege centrul pe rândurile de mai sus, apoi salvează.", "eroare"); return; }
    try {
      await api.put(`/tenants/${t.id}/centre-cost/alocari`, corpReq);
      corp.querySelectorAll("select.cc-aloc").forEach((s) => { s.dataset.initial = s.value; });
      arataMesaj(msg, `Alocarea s-a salvat (${cate(n, "rând schimbat", "rânduri schimbate")}). Notele salariilor, amortizarea și ieșirile din stoc generate de acum poartă centrul.`, "ok");
    } catch (e) { arataMesaj(msg, (e && e.mesaj) || "Alocarea nu s-a salvat.", "eroare"); }
  });
}


// [bonuri] documente pozate de client: lista -> detaliu la selectie  // bon_flux_e5_v1
let _bonuriMesaj = "";  // faza_b_traseu_v1
async function ecranBonuri(corp, nav, t) {
  const fmtPrimit = (iso) => {  // bon_flux_e7b_v1
    if (!iso) return "";
    const d = new Date(iso);
    const dd = (n) => String(n).padStart(2, "0");
    return "primit " + dd(d.getDate()) + "." + dd(d.getMonth() + 1) + "." + d.getFullYear() + " " + dd(d.getHours()) + ":" + dd(d.getMinutes());
  };
  let urlsPoze = [];
  let mesajSucces = "";
  let docs = [];

  const curata = () => { urlsPoze.forEach((u) => URL.revokeObjectURL(u)); urlsPoze = []; };

  async function pozaUrl(bonId, n) {
    const resp = await cereBlob(`/tenants/${t.id}/bonuri/${bonId}/imagine/${n}`);   // [R131]
    // CSP nginx: img-src 'self' data: (fara blob:) -> data:URL prin FileReader, nu createObjectURL.
    const blob = await resp.blob();
    const u = await new Promise((rez, resp2) => {
      const fr = new FileReader();
      fr.onload = () => rez(fr.result);
      fr.onerror = () => resp2(fr.error || new Error("Nu s-a putut citi imaginea."));
      fr.readAsDataURL(blob);
    });
    urlsPoze.push(u);
    return u;
  }

  const cerereLista = ultimaCerere();   // [C103] lista reîncărcată după documente adăugate în șir: numai lista cerută ultima ajunge pe ecran
  async function randeazaLista() {
    nav.setInapoi(undefined);
    curata();
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    const actuala = cerereLista();
    let err = null;
    try {
      const r = await api.get(`/tenants/${t.id}/bonuri/de-verificat`);
      if (!actuala()) return;
      docs = (r && r.bonuri) || [];
    } catch (e) { if (!actuala()) return; err = e; }
    if (err) {
      corp.innerHTML = `<h2 class="pf-titlu">Bonuri și chitanțe ${semnAjutor("F017")}</h2>
        <p class="msg-eroare">${esc(err.mesaj || "Nu s-au putut încărca documentele.")}</p>`;
      return;
    }
    const itemi = !docs.length
      ? `<div class="stare-goala">Niciun document de verificat. Clienții pozează, aici certifici.</div>`
      : docs.map((b, i) => `
        <button class="acces-card meniu-card pf-frand" data-doc="${i}" style="width:100%;text-align:left">
          <b>${b.tip === "chitanta" ? "Chitanță" : "Bon fiscal"}</b> · ${b.comerciant || "emitent necitit"}
          · ${b.total ? bani(b.total) + " lei" : "sumă necitită"}${b.data ? " · din " + dataRo(b.data) : ""}
          · <b>${fmtPrimit(b.primit_la)}</b>
        </button>`).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">Bonuri și chitanțe ${semnAjutor("F017")}</h2>
      <p class="pf-intro">Documente pozate de clienți sau adăugate de tine. Alege unul ca să-l verifici și să-l contezi.</p>
      <div style="margin:0 0 12px">
        <button class="buton-secundar" id="bc-adauga" data-fara-actiune="documentul intră ca ciornă prin /portal/bon (rută comună clientului și cabinetului); certificarea poartă acțiunea">Adaugă document (pozează / încarcă)</button>
        <input type="file" id="bc-fisier" accept="image/*" multiple hidden>
        <span class="msg-eroare" id="bc-msg" style="margin-left:8px"></span>
      </div>
      ${(mesajSucces || _bonuriMesaj) ? '<p style="color:var(--verde);font-weight:600;margin:0 0 12px">' + (mesajSucces || _bonuriMesaj) + '</p>' : ""}
      ${itemi}`;
    mesajSucces = ""; _bonuriMesaj = "";
    const bcInput = corp.querySelector("#bc-fisier");  // bon_cabinet_v1
    const bcBtn = corp.querySelector("#bc-adauga");
    bcBtn.addEventListener("click", () => bcInput.click());
    bcInput.addEventListener("change", async () => {
      const fs = Array.from(bcInput.files);
      if (!fs.length) return;
      const msg = corp.querySelector("#bc-msg");
      bcBtn.disabled = true; bcBtn.textContent = "Se citește documentul…";
      const fd = new FormData();
      fs.forEach((f) => fd.append("fisiere", f));
      try {
        const r = await api.postForm(`/portal/bon?tenant_id=${t.id}`, fd);
        await api.post(`/portal/bon/${r.bon_id}/confirma?tenant_id=${t.id}`, {});
        mesajSucces = "Document adăugat — deschide-l din listă ca să-l verifici și să-l contezi.";
        randeazaLista();
      } catch (e) {
        bcBtn.disabled = false; bcBtn.textContent = "Adaugă document (pozează / încarcă)";
        arataMesaj(msg, e.mesaj || "Nu s-a putut citi documentul. Încearcă o poză mai clară.", "eroare");
      }
    });
    corp.querySelectorAll("[data-doc]").forEach((el) =>
      el.addEventListener("click", () => {  // faza_b_traseu_v1
        const i = parseInt(el.dataset.doc);
        const b = docs[i];
        nav.mergi((b.tip === "chitanta" ? "Chitan\u021b\u0103" : "Bon fiscal") + (b.comerciant ? " \u00b7 " + b.comerciant : ""),
          (c) => { corp = c; randeazaDetaliu(i); });
      }));
  }

  async function randeazaDetaliu(i) {
    curata();  // faza_b_traseu_v1
    const b = docs[i];
    const eChitanta = b.tip === "chitanta";
    const sumaArt = (b.articole || []).reduce((s, a) => s + (Number(a.valoare) || 0), 0);
    const dif = (b.articole || []).length ? Math.abs(Math.round((sumaArt - b.total) * 100) / 100) : 0;

    corp.innerHTML = `
      <h2 class="pf-titlu">${eChitanta ? "Chitanță" : "Bon fiscal"}${b.numar_document ? " · nr. " + b.numar_document : ""}</h2>
      ${b.mentiuni ? `<p class="pf-intro">reprezentând: ${b.mentiuni}</p>` : ""}
      ${!eChitanta && dif > 0.05 ? `<div class="caseta-atentie" style="margin:0 0 12px"><div class="ca-mesaj">Suma articolelor citite (${bani(sumaArt)}) nu se închide cu totalul (${bani(b.total)}) — verifică cu poza.</div></div>` : ""}
      <div class="doc-split">
      <div class="doc-poza" id="d-poze"><p class="ecran-nota">Se încarcă poza...</p></div>
      <div class="doc-campuri">
      <div class="grila-doc" style="grid-template-columns:${eChitanta ? "2fr 1fr 1fr" : "2fr 1fr 1fr 1fr"}">
        <label class="camp"><span class="camp-eticheta">${eChitanta ? "Emitent (furnizor)" : "Comerciant"}</span><input class="camp-input" id="d-com" value="${b.comerciant || ""}"></label>
        <label class="camp"><span class="camp-eticheta">${eChitanta ? "Data plății" : "Data"}</span><input class="camp-input" type="date" id="d-data" value="${b.data || ""}"></label>
        <label class="camp"><span class="camp-eticheta">${eChitanta ? "Suma plătită" : "Total"}</span><input class="camp-input" type="number" step="0.01" id="d-tot" value="${b.total == null ? "" : Number(b.total).toFixed(2)}"></label>
        ${eChitanta ? "" : `<label class="camp"><span class="camp-eticheta">TVA total</span><input class="camp-input" type="number" step="0.01" id="d-tva" value="${b.tva == null ? "" : Number(b.tva).toFixed(2)}"></label>`}
      </div>
      ${eChitanta
        ? `<div id="d-cand" style="margin-top:12px"><p class="ecran-nota">Caut facturi de potrivit...</p></div>`
        : `<div style="margin-top:8px"><div class="camp-eticheta">Denumire \u00b7 valoare \u00b7 cont</div>${(b.articole || []).map((a, j) => `
            <div class="grila-doc" style="grid-template-columns:2fr 1fr 1fr;margin-top:4px">
              <input class="camp-input" id="d-den-${j}" aria-label="Denumire articol" value="${esc(a.denumire || "")}" readonly>
              <input class="camp-input" type="number" step="0.01" id="d-val-${j}" aria-label="Valoare articol" value="${a.valoare == null ? "" : Number(a.valoare).toFixed(2)}">
              <input class="camp-input" id="d-cont-${j}" value="${a.cont_propus || ""}" placeholder="cont" aria-label="Cont propus">
            </div>`).join("")}</div>`}
      <div style="margin-top:14px">
        <button class="buton-verde" id="d-certifica" data-actiune="${eChitanta ? "POST /tenants/{tenant_id}/bonuri/{bon_id}/stinge" : "POST /tenants/{tenant_id}/bonuri/{bon_id}/aproba"}">${eChitanta ? "Certifică plata (401 = 5311)" : "Certifică și contează"}</button>
        <button class="btn-link" id="d-renunta" style="margin-left:10px">Renunță</button>
        <span class="msg-eroare" id="d-msg" style="margin-left:10px"></span>
      </div>
      </div>
      </div>`;

    corp.querySelector("#d-renunta").addEventListener("click", () => nav.inapoiPas());  // faza_b_traseu_v1

    // pozele: mari, fixe langa date; rotita = zoom, tragere = mutare, dublu-click = ecran complet  // bon_flux_e8_v1
    (async () => {
      const zona = corp.querySelector("#d-poze");
      zona.innerHTML = "";
      // [PIVOT 04.10.2026, R52 răsturnat] Fotografia o vede oricine are «Poate pregăti» pe firma alocată (decizia Costin:
      // „nu poate emite/certifica ce nu vede”). Fără drept se spune DE CE lipsește, nu o imagine ruptă sau un refuz tăcut.
      if (!permis("GET /tenants/{tenant_id}/bonuri/{bon_id}/imagine/{n}")) {
        zona.innerHTML = '<p class="ecran-nota">Fotografia documentului cere dreptul „Poate pregăti”, pe care nu-l ai. Îl acordă administratorul cabinetului, din ecranul Asistenți.</p>';
        return;
      }
      for (let n = 1; n <= (b.nr_imagini || 0); n++) {
        try {
          const u = await pozaUrl(b.id, n);
          const cadru = document.createElement("div");
          cadru.className = "doc-poza-cadru";
          const img = document.createElement("img");
          img.src = u; img.alt = "document"; img.draggable = false;
          let scara = 1, tx = 0, ty = 0, drag = null, rot = Number(b.orientare) || 0;  // bon_flux_e9_v1
          const aplica = () => { img.style.transform = `translate(${tx}px,${ty}px) scale(${scara}) rotate(${rot}deg)`; };
          aplica();
          cadru.addEventListener("wheel", (e) => {
            e.preventDefault();
            if (e.shiftKey) {  // bon_flux_e9b_v1: rotire fina, indrepti bonul la orice unghi
              rot = (rot + (e.deltaY < 0 ? -2 : 2) + 360) % 360;
            } else {
              scara = Math.min(6, Math.max(1, scara * (e.deltaY < 0 ? 1.2 : 1 / 1.2)));
              if (scara === 1) { tx = 0; ty = 0; }
            }
            aplica();
          }, { passive: false });
          cadru.addEventListener("contextmenu", (e) => { e.preventDefault(); rot = (rot + 90) % 360; aplica(); });
          img.addEventListener("mousedown", (e) => { e.preventDefault(); drag = { x: e.clientX - tx, y: e.clientY - ty }; });
          cadru.addEventListener("mousemove", (e) => { if (drag) { tx = e.clientX - drag.x; ty = e.clientY - drag.y; aplica(); } });
          window.addEventListener("mouseup", () => { drag = null; });
          img.addEventListener("dblclick", () => deschideLupa(u, rot));
          cadru.appendChild(img);
          zona.appendChild(cadru);
          const bRot = document.createElement("button");
          bRot.className = "btn-link"; bRot.textContent = "\u21bb Rote\u0219te";
          bRot.addEventListener("click", () => { rot = (rot + 90) % 360; aplica(); });
          zona.appendChild(bRot);
        } catch {}
      }
      if (!zona.children.length) zona.innerHTML = `<p class="ecran-nota">Fără poză (document mai vechi).</p>`;
      else zona.insertAdjacentHTML("beforeend", '<p class="ecran-nota" style="margin:0">Rotița = mărește · Shift+rotița = îndreaptă · click-dreapta = rotește 90° · trage = mută · dublu-click = ecran complet</p>');
    })();

    // facturile candidate (doar chitanta)
    if (eChitanta) (async () => {
      const zona = corp.querySelector("#d-cand");
      let fc = [];
      try {
        const r = await api.get(`/tenants/${t.id}/bonuri/${b.id}/facturi-candidate`);
        fc = (r && r.facturi) || [];
      } catch {}
      const idPref = (fc.find((f) => f.potrivire_cui && f.potrivire_suma) || {}).id;
      zona.innerHTML = `
        <div class="camp-eticheta" style="margin-bottom:6px">Ce plătește chitanța?</div>
        ${fc.map((f) => `
          <label style="display:flex;gap:8px;align-items:center;padding:4px 0">
            <input type="radio" name="d-fact" value="${f.id}" ${f.id === idPref ? "checked" : ""}>
            <span>Factura ${f.numar || f.id} · ${f.furnizor || ""} · ${f.data ? dataRo(f.data) : ""} · ${bani(f.total)} lei${f.potrivire_cui ? '<span style="color:var(--verde);font-weight:600"> ✓ CUI</span>' : ""}${f.potrivire_suma ? '<span style="color:var(--verde);font-weight:600"> ✓ sumă</span>' : ""}</span>
          </label>`).join("")}
        <label style="display:flex;gap:8px;align-items:center;padding:4px 0">
          <input type="radio" name="d-fact" value="" ${idPref ? "" : "checked"}>
          <span>Plată directă, fără factură în sistem</span>
        </label>
        ${!fc.length ? '<p class="ecran-nota" style="margin:4px 0 0">Nicio factură primită neplătită găsită — rămâne plata directă.</p>' : ""}`;
    })();

    // certificare
    corp.querySelector("#d-certifica").addEventListener("click", async (ev) => {
      const btn = ev.currentTarget;
      const v = (id) => corp.querySelector(id).value;
      const msg = corp.querySelector("#d-msg");
      msg.textContent = "";
      curataEroriCamp(corp);
      if (eChitanta) {
        const suma = parseFloat(v("#d-tot")) || 0;
        // [lotul 11, 440] suma și data lipsă se marchează deodată, fiecare lângă câmpul ei (înainte: un text simplu, în afara casetei
        // „NU s-a salvat.”, și numai primul)
        let lipsa = false;
        if (suma <= 0) { eroareCamp(corp, "d-tot", "Completează suma plătită (citește-o de pe poză)."); lipsa = true; }
        if (!v("#d-data")) { eroareCamp(corp, "d-data", "Completează data plății."); lipsa = true; }
        if (lipsa) return;
        const ales = corp.querySelector('input[name="d-fact"]:checked');
        btn.disabled = true; btn.textContent = "Se contează...";
        try {
          const r = await api.post(`/tenants/${t.id}/bonuri/${b.id}/stinge`, {
            data: v("#d-data"), suma,
            partener: v("#d-com"), cui: b.cui || "",
            document: b.numar_document || "",
            factura_id: ales && ales.value ? parseInt(ales.value) : null,
          });
          const av = (r && r.avertismente) || [];
          _bonuriMesaj = "Plata a fost înregistrată în Registrul de casă." + (av.length ? " Atenție: " + esc(av.join(" ")) : "");
          nav.inapoiPas();
        } catch (e) {
          btn.disabled = false; btn.textContent = "Certifică plata (401 = 5311)";
          arataRefuzul(corp, e && e.mesaj ? e : { ...(e || {}), mesaj: "Eroare la înregistrare." }, msg,
            { campuri: { data: "d-data", suma: "d-tot", partener: "d-com" } });   // [lotul 11, 440]
        }
      } else {
        const grupe = {};
        let ok = true;
        (b.articole || []).forEach((a, j) => {
          const cont = v(`#d-cont-${j}`).trim();
          const val = parseFloat(v(`#d-val-${j}`)) || 0;
          // [lotul 11, 440] fiecare articol fără cont, marcat lângă câmpul lui (toate deodată)
          if (!cont) { ok = false; eroareCamp(corp, `d-cont-${j}`, "Pune contul pe acest articol."); }
          grupe[cont] = (grupe[cont] || 0) + val;
        });
        if (!ok) return;
        const linii = Object.entries(grupe).map(([cont, valoare]) => ({ cont, valoare: Math.round(valoare * 100) / 100 }));
        btn.disabled = true; btn.textContent = "Se contează...";
        try {
          await api.post(`/tenants/${t.id}/bonuri/${b.id}/aproba`, {
            comerciant: v("#d-com"), data: v("#d-data"),
            total: parseFloat(v("#d-tot")) || 0,
            tva: parseFloat(v("#d-tva")) || 0,
            linii,
          });
          _bonuriMesaj = "Bonul a fost contat.";
          nav.inapoiPas();
        } catch (e) {
          btn.disabled = false; btn.textContent = "Certifică și contează";
          arataRefuzul(corp, e && e.mesaj ? e : { ...(e || {}), mesaj: "Eroare la contare." }, msg,
            { campuri: { comerciant: "d-com", data: "d-data", total: "d-tot", tva: "d-tva" } });   // [lotul 11, 440]
        }
      }
    });
  }

  randeazaLista();
}

// [balanta] Balanta de verificare - tabelul pe ecran + descarcare PDF lunar
//
// [lista 5, 30.08.2026] Pana azi ecranul avea titlu, navigare pe luna si un buton „Descarca PDF",
// atat: singura ruta era cea care intoarce un FISIER. O cifra pe care n-o poti citi decat
// descarcand-o nu se poate verifica pe ecran - chiar criteriul listei 5. Acum cifrele vin pe
// `/tenants/{id}/balanta`, iar totalurile si inchiderea sunt calculate pe SERVER, in aceeasi sursa
// din care se tipareste PDF-ul (`documente_api.totaluri_balanta`): ecranul nu aduna nimic.
async function ecranBalanta(corp, nav, t) {
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;

  // [08.10.2026, decizia Costin W1] cinci egalități (OMFP 2634/2015, cod 14-6-30/a): rulajele CURENTE sunt notele lunii —
  // aceleași pe care le arată Registrul jurnal pe luna asta —, iar notele lunilor anterioare stau în „sume precedente”.
  const COL_BAL = ["si_d", "si_c", "prec_d", "prec_c", "rul_d", "rul_c", "tot_d", "tot_c", "sf_d", "sf_c"];
  const randCont = (r) => `<tr>
      <td>${esc(r.cont)}</td><td>${esc(r.denumire || "")}</td>
      ${COL_BAL.map((c) => `<td class="fd-td-num">${bani(r[c])}</td>`).join("")}
    </tr>`;

  // Inchiderea e un OBIECT cu stare, nu o propozitie (DS cap.25.5), si are TREI stari: pe o luna
  // fara inregistrari nu s-a verificat nimic - nu se afirma ca „se inchide".
  // [08.10.2026, decizia Costin §6 pct.7 — R36] „Balanța arată implicit doar validatul, iar ciornele apar separat, cu indicator.”
  // [lotul 12, comanda Costin 12.2 pct.11, deficiența 621] „casetele de sus ocupă jumătate din fereastră, se văd 2–3 rânduri de tabel”: în
  // rezumatul lipit sus stă numai ce trebuie văzut cât derulezi (DS cap.9 v2.102 „Rezumatul nu mănâncă tabelul”) — ciornele, pe un rând;
  // de ce nu intră, în „De unde vin cifrele” (pliat)
  const randCiorne = (c) => {
    const n = c ? (c.luna || 0) + (c.inainte || 0) : 0;
    if (!n) return "";
    return `<p class="pf-intro" id="b-ciorne"><b style="color:var(--galben-text)">${cate(n, "ciorn\u0103 nevalidat\u0103", "ciorne nevalidate")} nu intr\u0103 \u00een balan\u021b\u0103</b> (${c.luna || 0} \u00een luna asta, ${c.inainte || 0} din lunile anterioare ale anului) \u2014 le validezi \u00een Registrul jurnal.</p>`;
  };
  const casetaInchidere = (inc) => {
    if (!inc) return "";
    const perechi = `<table class="fd-tabel" style="max-width:640px">
        <thead><tr><th>Ce se \u00eenchide</th><th class="fd-td-num">Debit</th>
          <th class="fd-td-num">Credit</th><th class="fd-td-num">Diferen\u021b\u0103</th>
          <th>Verdict</th></tr></thead>
        <tbody>${inc.perechi.map((p) => `<tr><td>${esc(p.ce)}</td>
          <td class="fd-td-num">${bani(p.debit)}</td><td class="fd-td-num">${bani(p.credit)}</td>
          <td class="fd-td-num">${bani(p.diferenta)}</td>
          <td>${p.inchisa
            ? `<span style="color:var(--verde);font-weight:600">\u25cf se \u00eenchide</span>`
            : `<span style="color:var(--rosu);font-weight:600">\u25cf nu se \u00eenchide</span>`}</td></tr>`).join("")}</tbody>
      </table>`;
    if (inc.stare === "nimic_de_verificat") {
      return `<div class="caseta-info"><span class="ci-mesaj">Luna n-are nicio \u00eenregistrare contabil\u0103, deci nu s-a verificat nimic \u2014 ceea ce nu e acela\u0219i lucru cu „balan\u021ba se \u00eenchide". Treci pe o lun\u0103 cu opera\u021biuni, sau \u00eenregistreaz\u0103-le pe ale lunii \u0103steia din Registrul jurnal.</span></div>`;
    }
    if (inc.stare === "se_inchide") {
      // [621] verdictul bun e o notă informativă: concluzia în titlu, cifrele perechilor pliate (DS cap.9 v2.98 / v2.102) — nu mai ține
      // cinci rânduri de tabel deasupra balanței
      return `<details class="dec-xml" id="b-inchidere"><summary>Balan\u021ba se \u00eenchide pe toate cinci: sold ini\u021bial, sume precedente, rulajele lunii, total sume \u0219i sold final \u2014 verificat pe ${cate(inc.randuri, "cont", "conturi")}</summary>${perechi}</details>`;
    }
    return `<div class="caseta-atentie"><div class="ca-mesaj">Balan\u021ba nu se \u00eenchide. Diferen\u021bele sunt mai jos, pe fiecare pereche \u2014 c\u00e2t timp nu sunt zero, nici bilan\u021bul, nici declara\u021biile care citesc solduri nu se pot sprijini pe ea.</div></div>${perechi}`;
  };

  const cerereNoua = ultimaCerere();   // [C103] luna schimbată în șir (← / →): numai balanța lunii afișate ajunge pe ecran
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    const actuala = cerereNoua();
    let b = null;
    try {
      b = await api.get(`/tenants/${t.id}/balanta?an=${an}&luna=${luna}`);
      if (!actuala()) return;
    } catch (e) {
      if (!actuala()) return;
      corp.innerHTML = `<p class="ecran-nota">Nu s-a putut \u00eenc\u0103rca balan\u021ba. ${esc((e && (e.mesaj || e.message)) || "")}</p>`;
      return;
    }
    const randuri = (b && b.randuri) || [];
    const tot = (b && b.totaluri) || {};
    const tabel = !randuri.length
      ? `<div class="stare-goala">Nicio \u00eenregistrare \u00een luna asta, deci balan\u021ba n-are ce ar\u0103ta. Balan\u021ba se face din notele contabile ale lunii \u2014 trece pe o lun\u0103 cu opera\u021biuni, sau scrie-le din Registrul jurnal.</div>`
      : `<table class="fd-tabel">
          <thead><tr><th>Cont</th><th>Denumire</th>
            <th class="fd-td-num">Sold ini\u021bial D</th><th class="fd-td-num">Sold ini\u021bial C</th>
            <th class="fd-td-num">Sume precedente D</th><th class="fd-td-num">Sume precedente C</th>
            <th class="fd-td-num">Rulaj lun\u0103 D</th><th class="fd-td-num">Rulaj lun\u0103 C</th>
            <th class="fd-td-num">Total sume D</th><th class="fd-td-num">Total sume C</th>
            <th class="fd-td-num">Sold final D</th><th class="fd-td-num">Sold final C</th></tr></thead>
          <tbody>${randuri.map(randCont).join("")}</tbody>
          <tfoot><tr><td></td><td><b>Total</b></td>   <!-- [lotul 11, decizia Costin 10.3: „Totalurile … fix”] totalul rămâne jos, deasupra „Descarcă PDF” (DS cap.9 v2.100) -->
              ${COL_BAL.map((c) => `<td class="fd-td-num"><b>${bani(tot[c])}</b></td>`).join("")}</tr></tfoot>
          </table>`;
    // [lotul 10, 421/424] fereastra cu tabel: titlul, luna, ciornele și lipsa rulajelor preluate lipite sus; PDF-ul și mesajul lui jos
    // [lotul 10, 425] `b.avertismente`: rulajele dinainte de preluare lipsesc (balanța de deschidere numai cu solduri finale)
    // [621] „caseta «Importă…» nu are buton spre import”: sub textul ei, butonul spre importul firmei (Import date › Solduri inițiale);
    // caseta stă sub rezumat (nu lipită): se citește la deschidere și lasă tabelul întreg cât derulezi
    const casetaRulaje = ((b && b.avertismente) || []).map((a) =>
      `<div class="caseta-atentie" id="b-rulaje"><div class="ca-mesaj">${esc(a.motiv)}</div></div>${a.tip === "rulaje_preluare" ? `
      <p class="b-rulaje-import"><button class="buton-secundar" id="b-rulaje-import" data-fara-actiune="deschide importul datelor firmei; importul de acolo poartă acțiunea">Deschide Import date › Solduri inițiale</button></p>` : ""}`).join("");
    corp.innerHTML = `
      <div class="rezumat-fix">
      <h2 class="pf-titlu">Balan\u021b\u0103 de verificare</h2>
      <p class="pf-intro" id="b-intro">Luna ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")} · ${cate(randuri.length, "cont", "conturi")} · ${cate(b.note_lunii, "notă validată", "note validate")} în luna asta
        <button class="buton-secundar" id="b-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="buton-secundar" id="b-next">luna \u2192</button></p>
      <!-- [lotul 12, 498] Antetul spune numai luna și cifrele; de unde vin rulajele e o notă informativă, pliată (DS cap.9 v2.98). -->
      <details class="dec-xml" id="b-surse"><summary>De unde vin cifrele</summary>
        <p class="ecran-nota" style="margin:6px 0 0">Rulajele lunii sunt notele validate ale lunii — aceleași pe care le arată Registrul jurnal pe luna asta; ciornele nu intră (balanța arată numai notele validate de un om). Notele lunilor anterioare și, în anul preluării, rulajele aduse din balanța de deschidere stau în „Sume precedente”.</p></details>
      ${randCiorne(b && b.ciorne)}
      </div>
      ${casetaRulaje}
      ${casetaInchidere(b && b.inchidere)}
      ${tabel}
      <div class="bara-fixa"><div id="b-mesaj"></div><button class="buton-primar" id="b-pdf">Descarc\u0103 PDF</button></div>`;
    corp.querySelector("#b-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#b-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });
    const bImp = corp.querySelector("#b-rulaje-import");
    if (bImp) bImp.addEventListener("click", () =>
      nav.deschide("Import date", (c) => meniuMigrarePerFirma(c, nav, { tenant_id: t.id, nume: t.nume, tip_firma: t.tip_firma })));
    corp.querySelector("#b-pdf").addEventListener("click", async () => {
      const zona = corp.querySelector("#b-mesaj");
      try {
        await descarca(`/tenants/${t.id}/documente/balanta?an=${an}&luna=${luna}`,
                       `balanta_${an}_${String(luna).padStart(2, "0")}.pdf`);
        zona.innerHTML = `<p class="pf-intro">Balanta descarcata.</p>`;
      } catch (e) { arataMesaj(zona, e.mesaj || e.message || "eroare", "eroare"); }
    });
  };
  deseneaza();
}


// [rap_com_v1] F144 v1 — Rapoarte comerciale (read-only). Doar felia constructibila
// pe schema actuala (fisa client/furnizor, vanzari pe partener, durata de incasare).
// Profit/articol/agent = decizie deschisa (DECIZII.md 17.07 + DE_FACUT.md CARENTE pct.4).
async function ecranRapoarte(corp, nav, t) {
  let an = new Date().getFullYear();
  let fisaCui = "";
  let parteneriCui = new Set();  // [rap145] partenerii existenti (toate facturile), pt validarea referintei salvate

  const cerereFisa = ultimaCerere();   // [C103] partenerul ales în șir: numai fișa partenerului din listă ajunge pe ecran
  const randeazaFisa = async () => {
    const actuala = cerereFisa();   // și fără partener: o fișă cerută înainte nu mai umple zona golită
    const zona = corp.querySelector("#r-fisa");
    if (!zona) return;
    if (!fisaCui) { zona.innerHTML = ""; return; }
    // [rap145] referinta din varianta poate muri (partener sters/redenumit): gol + cauza + iesire (DS cap.6)
    if (!parteneriCui.has(fisaCui)) {
      zona.innerHTML = "";
      arataMesaj(zona, "Varianta trimite la un partener care nu mai există în facturile firmei. Alege alt partener.", "avert");
      fisaCui = "";
      const sel = corp.querySelector("#r-fisa-sel");
      if (sel) sel.value = "";
      return;
    }
    zona.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    let f;
    try {
      f = await api.get(`/tenants/${t.id}/rapoarte-comerciale/fisa?cui=${encodeURIComponent(fisaCui)}&de=${an}-01-01&pana=${an}-12-31`);
      if (!actuala()) return;
    } catch (e) { if (!actuala()) return; arataMesaj(zona, (e && e.mesaj) || "eroare", "eroare"); return; }
    const s = f.sumar || {};
    const rand = (r) => `
      <tr><td>${dataRo(r.data)}</td><td>${esc(numarCuSerie(r.serie, r.numar))}</td>
          <td>${r.directie === "emisa" ? "Emisă" : "Primită"}</td>
          <td class="fd-td-num">${bani(r.total)}</td>
          <td class="fd-td-num">${bani(r.decontat)}</td>
          <td class="fd-td-num">${bani(r.sold)}</td>
          <td>${r.stare === "achitata" ? "achitată" : "deschisă"}</td></tr>`;
    zona.innerHTML = (f.facturi || []).length ? `
      <table class="fd-tabel">
        <thead><tr><th>Data</th><th>Număr</th><th>Direcție</th>
          <th class="fd-td-num">Total</th><th class="fd-td-num">Decontat</th>
          <th class="fd-td-num">Sold</th><th>Stare</th></tr></thead>
        <tbody>${f.facturi.map(rand).join("")}</tbody>
        <tfoot><tr><td colspan="3"><b>Total (${s.nr})</b></td>   <!-- [lotul 11, decizia Costin 10.3: „Totalurile … fix”] (DS cap.9 v2.100) -->
            <td class="fd-td-num"><b>${bani(s.facturat)}</b></td>
            <td class="fd-td-num"><b>${bani(s.decontat)}</b></td>
            <td class="fd-td-num"><b>${bani(s.sold)}</b></td><td></td></tr></tfoot>
      </table>` : `<div class="stare-goala">Nicio factură pentru acest partener în perioadă.</div>`;
  };

  const cerereNoua = ultimaCerere();   // [C103] anul schimbat în șir (← / →) sau varianta aleasă: numai raportul cerut ultimul ajunge pe ecran
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    const actuala = cerereNoua();
    let d, variante = [];
    try {
      d = await api.get(`/tenants/${t.id}/rapoarte-comerciale?de=${an}-01-01&pana=${an}-12-31`);
      if (!actuala()) return;
    } catch (e) { if (!actuala()) return; arataMesaj(corp, (e && e.mesaj) || "eroare", "eroare"); return; }
    try {
      const rv = await api.get(`/tenants/${t.id}/rapoarte-salvate?tip_raport=comercial`);
      variante = rv.variante || [];
    } catch { /* variantele nu blocheaza raportul */ }
    if (!actuala()) return;
    parteneriCui = new Set((d.parteneri || []).map((p) => p.cui));
    const v = d.vanzari || { parteneri: [], total_net: 0 };
    const di = d.durata_incasare || {};
    const randVanzari = (v.parteneri || []).map((p) => `
      <tr><td>${esc(p.nume)}</td><td>${esc(p.cui || "")}</td>
          <td class="fd-td-num">${p.nr}</td>
          <td class="fd-td-num">${bani(p.net)}</td></tr>`).join("");
    const optParteneri = (d.parteneri || []).map((p) =>
      `<option value="${esc(p.cui)}"${p.cui === fisaCui ? " selected" : ""}>${esc(p.nume)}</option>`).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">Rapoarte comerciale ${semnAjutor("F144")}</h2>
      <div class="rezumat-fix"><p class="pf-intro">Anul ${an}
        <button class="buton-secundar" id="r-prev" style="margin-left:12px">← an</button>
        <button class="buton-secundar" id="r-next">an →</button></p></div>   <!-- [lotul 10, 421 / 424, DS cap.9 v2.97 pct.5] anul rămâne sus -->
      <div class="caseta-info"><span class="ci-mesaj">Profit pe produs și vânzări pe articol/agent nu apar aici: vânzarea și descărcarea gestiunii sunt documente separate, iar liniile de factură nu sunt legate de catalogul de produse.</span></div>

      <h3 class="pf-subtitlu">Durata medie de încasare</h3>
      <p class="pf-intro">${di.zile_medii != null
        ? `<b>${cate(di.zile_medii, "zi", "zile")}</b> · din ${cate(di.nr_facturi, "factură încasată", "facturi încasate")} integral`
        : "Nicio factură încasată integral în perioadă."}</p>

      <h3 class="pf-subtitlu">Vânzări pe partener</h3>
      ${(v.parteneri || []).length ? `
        <table class="fd-tabel">
          <thead><tr><th>Partener</th><th>CUI</th>
            <th class="fd-td-num">Facturi</th><th class="fd-td-num">Vânzări (net)</th></tr></thead>
          <tbody>${randVanzari}</tbody>
          <tfoot><tr><td colspan="3"><b>Total</b></td>   <!-- [lotul 11, decizia Costin 10.3: „Totalurile … fix”] (DS cap.9 v2.100) -->
              <td class="fd-td-num"><b>${bani(v.total_net)}</b></td></tr></tfoot>
        </table>` : `<div class="stare-goala">Nicio vânzare în perioadă.</div>`}

      <h3 class="pf-subtitlu">Profit pe produs</h3>
      ${(d.profit_produs || []).length ? `
        <table class="fd-tabel">
          <thead><tr><th>Articol</th><th class="fd-td-num">Cant.</th>
            <th class="fd-td-num">Venit</th><th class="fd-td-num">Cost</th><th class="fd-td-num">Profit</th></tr></thead>
          <tbody>${(d.profit_produs || []).map((p) => `
            <tr><td>${esc(p.articol)}</td><td class="fd-td-num">${cantitate(p.cant)}</td>
              <td class="fd-td-num">${bani(p.venit)}</td><td class="fd-td-num">${bani(p.cost)}</td>
              <td class="fd-td-num">${bani(p.profit)}</td></tr>`).join("")}</tbody>
        </table>` : `<div class="stare-goala">Niciun profit pe produs în perioadă. Disponibil doar la gestiune cantitativă (CV), pe articolele descărcate din stoc la emitere (întrebarea „pleacă marfa acum?”). La global-valoric costul pe articol nu există.</div>`}

      <h3 class="pf-subtitlu">Fișă client/furnizor</h3>
      <p><select id="r-fisa-sel" aria-label="Partener fișă" class="camp-input" style="max-width:360px">
        <option value="">— alege partenerul —</option>${optParteneri}</select></p>
      <div id="r-fisa"></div>

      <h3 class="pf-subtitlu">Variantele firmei</h3>
      ${variante.length ? `<div class="pf-lista">${variante.map((vr) => `
        <div class="pf-frand">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">${esc(vr.nume)}</div>
            <div class="pf-frand-sub">anul ${(vr.filtru && vr.filtru.an) || "?"}${vr.filtru && vr.filtru.cui ? " · partener " + esc(vr.filtru.cui) : ""} · creată de ${esc(vr.autor)}</div>
          </div>
          <div style="display:flex;gap:6px;align-items:center">
            <button class="buton-secundar" data-incarca="${vr.id}">Încarcă</button>
            <button class="buton-secundar" data-sterge="${vr.id}" data-actiune="DELETE /tenants/{tenant_id}/rapoarte-salvate/{vid}">Șterge</button>
          </div>
        </div>`).join("")}</div>` : `<div class="stare-goala">Nicio variantă salvată încă.</div>`}
      <p class="bara-fixa">   <!-- [lotul 10, 421/424] salvarea variantei și mesajul ei, lipite jos -->
        <input class="camp-input" id="r-var-nume" aria-label="Nume variantă" placeholder="Nume variantă (ex. Anul curent, client X)" style="max-width:320px" maxlength="80" autocomplete="off">
        <button class="buton-primar" id="r-var-salveaza" data-actiune="POST /tenants/{tenant_id}/rapoarte-salvate" style="margin-left:6px">Salvează varianta curentă</button>
        <span class="msg-eroare" id="r-var-msg" style="margin-left:8px"></span>
      </p>
      <div id="r-var-zona"></div>`;
    corp.querySelector("#r-prev").addEventListener("click", () => { an--; deseneaza(); });
    corp.querySelector("#r-next").addEventListener("click", () => { an++; deseneaza(); });
    const sel = corp.querySelector("#r-fisa-sel");
    sel.addEventListener("change", () => { fisaCui = sel.value; randeazaFisa(); });
    // [rap145] salveaza varianta curenta (an + partener selectat)
    corp.querySelector("#r-var-salveaza").addEventListener("click", async () => {
      const msg = corp.querySelector("#r-var-msg");
      const nume = corp.querySelector("#r-var-nume").value.trim();
      msg.textContent = "";
      curataEroriCamp(corp);
      if (cereCompletate(corp, [{ id: "r-var-nume", mesaj: "Dă un nume variantei." }])) return;   // [lotul 11, 440] lângă câmp
      try {
        await api.post(`/tenants/${t.id}/rapoarte-salvate`, { tip_raport: "comercial", nume, filtru: { an, cui: fisaCui || null } });
        deseneaza();
      } catch (e) { arataMesaj(msg, (e && e.mesaj) || "eroare", "eroare"); }
    });
    // [rap145] incarca varianta: aplica filtrul; validarea partenerului se face in randeazaFisa
    corp.querySelectorAll("[data-incarca]").forEach((b) => b.addEventListener("click", () => {
      const vr = variante.find((x) => String(x.id) === b.dataset.incarca);
      if (!vr) return;
      const fl = vr.filtru || {};
      if (fl.an) an = parseInt(fl.an, 10) || an;
      fisaCui = fl.cui || "";
      deseneaza();
    }));
    // [rap145] sterge varianta (ireversibil -> caseta de confirmare, nu dialog nativ de browser)
    corp.querySelectorAll("[data-sterge]").forEach((b) => b.addEventListener("click", () => {
      const vr = variante.find((x) => String(x.id) === b.dataset.sterge);
      confirmaCaseta(corp.querySelector("#r-var-zona"), `Ștergi varianta „${vr ? esc(vr.nume) : ""}"?`, async () => {
        try { await api.del(`/tenants/${t.id}/rapoarte-salvate/${b.dataset.sterge}`); deseneaza(); }
        catch (e) { arataMesaj(corp.querySelector("#r-var-zona"), (e && e.mesaj) || "eroare", "eroare"); }
      });
    }));
    if (fisaCui) randeazaFisa();
  };

  deseneaza();
}


// [registratura_v1] F146 — Registratură documente (registru unic intrare-ieșire, v1 manual).
async function ecranRegistratura(corp, nav, t) {
  let an = new Date().getFullYear();
  const cerereNoua = ultimaCerere();   // [C103] anul schimbat în șir (← / →): numai registrul anului afișat ajunge pe ecran
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    const actuala = cerereNoua();
    let d;
    try { d = await api.get(`/tenants/${t.id}/registratura?an=${an}`); if (!actuala()) return; }
    catch (e) { if (!actuala()) return; arataMesaj(corp, (e && e.mesaj) || "eroare", "eroare"); return; }
    const rand = (r) => `
      <div class="pf-frand">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${r.numar}/${r.an} · ${r.directie === "intrare" ? "Intrare" : "Ieșire"} · ${dataRo(r.data)}</div>
          <div class="pf-frand-sub">${esc(r.descriere)}${r.partener ? " · " + esc(r.partener) : ""}</div>
        </div>
      </div>`;
    corp.innerHTML = `
      <h2 class="pf-titlu">Registratură</h2>
      <p class="pf-intro">Anul ${an} · registru unic de intrare-ieșire
        <button class="buton-secundar" id="rg-prev" style="margin-left:12px">← an</button>
        <button class="buton-secundar" id="rg-next">an →</button></p>
      <div class="panou" style="margin-bottom:14px">
        <div class="camp" style="margin-bottom:8px">
          <label class="camp-eticheta">Direcție <span class="oblig">*</span></label>
          <select class="camp-input" id="rg-dir" data-butoane aria-label="Direcția înregistrării" style="max-width:200px">
            <option value="intrare">Intrare</option>
            <option value="iesire">Ieșire</option></select>
        </div>
        <div class="camp" style="margin-bottom:8px">
          <label class="camp-eticheta">Data</label>
          <input type="date" class="camp-input" id="rg-data" aria-label="Data înregistrării" style="max-width:200px" value="${dataIso()}">
        </div>
        <div class="camp" style="margin-bottom:8px">
          <label for="rg-desc" class="camp-eticheta">Descriere <span class="oblig">*</span></label>
          <input type="text" class="camp-input" id="rg-desc" placeholder="Ex. Factură furnizor X, adeverință salariat Y" autocomplete="off">
        </div>
        <div class="camp" style="margin-bottom:10px">
          <label for="rg-part" class="camp-eticheta">Partener</label>
          <input type="text" class="camp-input" id="rg-part" placeholder="opțional" autocomplete="off">
        </div>
        <button class="buton-primar" id="rg-add" data-actiune="POST /tenants/{tenant_id}/registratura">Înregistrează</button>
        <span class="msg-eroare" id="rg-msg" style="margin-left:8px"></span>
      </div>
      <div class="pf-lista">${(d.inregistrari || []).length
        ? d.inregistrari.map(rand).join("")
        : `<div class="stare-goala">Niciun document înregistrat în ${an} încă. Prima înregistrare primește numărul 1.</div>`}</div>`;
    corp.querySelector("#rg-prev").addEventListener("click", () => { an--; deseneaza(); });
    corp.querySelector("#rg-next").addEventListener("click", () => { an++; deseneaza(); });
    corp.querySelector("#rg-add").addEventListener("click", async () => {
      const msg = corp.querySelector("#rg-msg"); msg.textContent = "";
      const corpReq = {
        directie: corp.querySelector("#rg-dir").value,
        data: corp.querySelector("#rg-data").value || null,
        descriere: corp.querySelector("#rg-desc").value.trim(),
        partener: corp.querySelector("#rg-part").value.trim() || null,
      };
      curataEroriCamp(corp);
      // [lotul 11, 440] lângă câmp (înainte: text simplu, în afara casetei „NU s-a salvat.”)
      if (cereCompletate(corp, [{ id: "rg-desc", mesaj: "Descrierea e obligatorie." }])) return;
      try {
        const r = await api.post(`/tenants/${t.id}/registratura`, corpReq);
        if (r.an !== an) an = r.an;  // data dintr-un alt an -> sari la anul respectiv
        deseneaza();
      } catch (e) {
        arataRefuzul(corp, e, msg, { campuri: { directie: "rg-dir", data: "rg-data", descriere: "rg-desc", partener: "rg-part" } });   // [440]
      }
    });
  };
  deseneaza();
}


// [contracte_v1] F147 — Generare contracte din sabloane (mail-merge). Firma isi scrie textul cu
// marcaje {{...}}; generarea completeaza datele partenerului (clienti) + firmei si scoate PDF.
async function ecranContracte(corp, nav, t) {
  let mesajSucces = "";

  const cerereNoua = ultimaCerere();   // [C103] lista reîncărcată după ștergeri / salvări în șir: numai șabloanele cerute ultimele ajung pe ecran
  async function randeazaPrincipal() {
    nav.setInapoi(undefined);
    corp.innerHTML = '<p class="ecran-nota">Se încarcă...</p>';
    const actuala = cerereNoua();
    let sabloane = [];
    try { sabloane = (await api.get(`/tenants/${t.id}/contracte/sabloane`)).sabloane || []; if (!actuala()) return; } catch { if (!actuala()) return; corp.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca șabloanele de contract.</p>`; return; }
    const rand = (s) => `
      <div class="pf-frand">
        <div class="pf-frand-text"><div class="pf-frand-nume">${esc(s.nume)}</div></div>
        <div style="display:flex;gap:6px;align-items:center">
          <button class="buton-secundar" data-gen="${s.id}">Generează</button>
          <button class="buton-secundar" data-edit="${s.id}">Editează</button>
          <button class="buton-secundar" data-del="${s.id}" data-actiune="DELETE /tenants/{tenant_id}/contracte/sabloane/{sid}">Șterge</button>
        </div>
      </div>`;
    corp.innerHTML = `
      <h2 class="pf-titlu">Contracte</h2>
      <p class="pf-intro">Șabloane proprii cu marcaje {{...}}; generarea completează datele partenerului și scoate PDF.</p>
      ${mesajSucces ? '<p style="color:var(--verde);font-weight:600;margin:0 0 12px">' + mesajSucces + '</p>' : ""}
      <p><button class="buton-primar" id="c-nou" data-actiune="POST /tenants/{tenant_id}/contracte/sabloane">+ Șablon nou</button></p>
      <div class="pf-lista">${sabloane.length
        ? sabloane.map(rand).join("")
        : '<div class="stare-goala">Niciun șablon de contract încă. Creează primul cu „+ Șablon nou".</div>'}</div>
      <div id="c-zona"></div>`;
    mesajSucces = "";
    corp.querySelector("#c-nou").addEventListener("click", () => randeazaEditor(null));
    corp.querySelectorAll("[data-edit]").forEach((b) => b.addEventListener("click", () =>
      randeazaEditor(sabloane.find((s) => String(s.id) === b.dataset.edit))));
    corp.querySelectorAll("[data-gen]").forEach((b) => b.addEventListener("click", () =>
      randeazaGenerare(sabloane.find((s) => String(s.id) === b.dataset.gen))));
    corp.querySelectorAll("[data-del]").forEach((b) => b.addEventListener("click", () => {
      const s = sabloane.find((x) => String(x.id) === b.dataset.del);
      confirmaCaseta(corp.querySelector("#c-zona"), `Ștergi șablonul „${esc(s ? s.nume : "")}"?`, async () => {
        try { await api.del(`/tenants/${t.id}/contracte/sabloane/${b.dataset.del}`); mesajSucces = "Șablon șters."; randeazaPrincipal(); }
        catch (e) { arataMesaj(corp.querySelector("#c-zona"), (e && e.mesaj) || "eroare", "eroare"); }
      });
    }));
  }

  async function randeazaEditor(sablon) {
    nav.setInapoi(randeazaPrincipal);
    let marcaje = {};
    try { marcaje = (await api.get(`/contracte/marcaje`)).marcaje || {}; } catch (e) {}
    const chips = Object.entries(marcaje).map(([k, v]) =>
      `<code style="padding:2px 6px;margin:0 4px 4px 0;display:inline-block" title="${esc(v)}">{{${k}}}</code>`).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">${sablon ? "Editează șablon" : "Șablon nou"}</h2>
      <div class="camp" style="margin-bottom:8px">
        <label for="c-nume" class="camp-eticheta">Nume <span class="oblig">*</span></label>
        <input type="text" class="camp-input" id="c-nume" style="max-width:360px" value="${sablon ? esc(sablon.nume) : ""}" autocomplete="off">
      </div>
      <p class="camp-eticheta" style="margin:8px 0 4px">Marcaje disponibile:</p>
      <div style="margin-bottom:8px">${chips}</div>
      <div class="camp" style="margin-bottom:10px">
        <label for="c-continut" class="camp-eticheta">Text contract <span class="oblig">*</span></label>
        <textarea class="camp-input" id="c-continut" rows="16" style="width:100%">${sablon ? esc(sablon.continut) : ""}</textarea>
      </div>
      <button class="buton-primar" id="c-salveaza" data-actiune="POST /tenants/{tenant_id}/contracte/sabloane">Salvează</button>
      <button class="btn-link" id="c-renunta" style="margin-left:10px">Renunță</button>
      <span class="msg-eroare" id="c-msg" style="margin-left:8px"></span>`;
    corp.querySelector("#c-renunta").addEventListener("click", randeazaPrincipal);
    corp.querySelector("#c-salveaza").addEventListener("click", async () => {
      const msg = corp.querySelector("#c-msg"); msg.textContent = "";
      try {
        await api.post(`/tenants/${t.id}/contracte/sabloane`, {
          id: sablon ? sablon.id : null,
          nume: corp.querySelector("#c-nume").value.trim(),
          continut: corp.querySelector("#c-continut").value,
        });
        mesajSucces = "Șablon salvat."; randeazaPrincipal();
      } catch (e) { arataMesaj(msg, (e && e.mesaj) || "eroare", "eroare"); }
    });
  }

  async function randeazaGenerare(sablon) {
    if (!sablon) return;
    nav.setInapoi(randeazaPrincipal);
    corp.innerHTML = '<p class="ecran-nota">Se încarcă...</p>';
    let clienti = [];
    try { const r = await api.get(`/tenants/${t.id}/clienti`); clienti = r.clienti || (Array.isArray(r) ? r : []); } catch (e) {}
    corp.innerHTML = `
      <h2 class="pf-titlu">Generează contract</h2>
      <p class="pf-intro">Șablon: ${esc(sablon.nume)}</p>
      <div class="camp" style="margin-bottom:8px">
        <label for="c-client" class="camp-eticheta">Partener (client)</label>
        <select class="camp-input" id="c-client" style="max-width:360px">
          <option value="">— alege clientul —</option>
          ${clienti.map((c) => `<option value="${c.id}">${esc(c.nume)}${c.cui ? " · " + esc(c.cui) : ""}</option>`).join("")}
        </select>
        <span class="camp-ajutor">Datele partenerului se iau din client; câmpurile lipsă rămân goale în contract.</span>
      </div>
      <button class="buton-primar" id="c-gen" data-actiune="POST /tenants/{tenant_id}/contracte/genereaza">Descarcă PDF</button>
      <button class="btn-link" id="c-inapoi" style="margin-left:10px">Înapoi</button>
      <span class="msg-eroare" id="c-genmsg" style="margin-left:8px"></span>`;
    corp.querySelector("#c-inapoi").addEventListener("click", randeazaPrincipal);
    corp.querySelector("#c-gen").addEventListener("click", async () => {
      const msg = corp.querySelector("#c-genmsg"); msg.textContent = "";
      try {
        await descarca(`/tenants/${t.id}/contracte/genereaza`,
                       `contract_${sablon.nume.replace(/[^a-z0-9]+/gi, "_")}.pdf`,
                       { metoda: "POST", corp: { sablon_id: sablon.id, client_id: corp.querySelector("#c-client").value || null } });
      } catch (e) { arataMesaj(msg, e.mesaj || e.message || "eroare", "eroare"); }
    });
  }

  randeazaPrincipal();
}


// [wc_extras_v1] ecranMagazin mutat in ./woo_ecran.js (reutilizat de cont gratuit F156).

/* acces_client_ui_v1 */
async function ecranAccesClient(corp, nav, t) {
  let mesajSucces = "";
  const cerereNoua = ultimaCerere();   // [C103] lista reîncărcată după revocări / invitații în șir: numai conturile cerute ultimele ajung pe ecran
  async function randeazaPrincipal() {
    nav.setInapoi(undefined);
    const actuala = cerereNoua();
    corp.innerHTML = `
      ${mesajSucces ? '<p style="color:var(--verde);font-weight:600;margin:0 0 14px">' + mesajSucces + '</p>' : ""}
      <h3 style="margin:0 0 8px">Conturi client</h3>
      <div id="ac-lista" style="margin-bottom:16px"><p class="ecran-nota">Se încarcă...</p></div>
      <button class="buton-secundar" id="ac-btn-invita" data-actiune="POST /tenants/{tenant_id}/client-acces">Invit\u0103 client nou</button>
      <button class="buton-secundar" id="ac-btn-preview" data-actiune="POST /tenants/{tenant_id}/acces-portal" style="margin-left:8px">Previzualizeaz\u0103 portalul</button>
      <div id="ac-msg" style="margin-top:10px"></div>
    `;
    mesajSucces = "";
    // [deficiența 262, clasa] „Invită client nou” duce la un formular numai al administratorului: poarta îl ascunde asistentului.
    // Previzualizarea (citire, a oricui) își declară și ea acțiunea, ca motivul porții să spună „Unele acțiuni”, nu „Acțiunile”.
    corp.querySelector("#ac-btn-invita").addEventListener("click", randeazaFormular);
    corp.querySelector("#ac-btn-preview").addEventListener("click", async (e) => {  // [F-preview] deschide portalul clientului in tab nou, read-only
      const b = e.currentTarget; const _t = b.textContent;
      b.disabled = true; b.textContent = "Se preg\u0103te\u0219te\u2026";  // cap.1 feedback async
      try {
        const r = await api.post(`/tenants/${t.id}/acces-portal`, {});
        // [F-preview] tokenul + userul (nume_tenant/tenant_are_cabinet) trec prin URL catre tab-ul nou;
        // fara user, preview-ul cade pe portalul gratuit (F197). URLSearchParams encodeaza corect JSON-ul.
        const _p = new URLSearchParams({ acces: r.token, u: JSON.stringify(r.user || { rol: "client" }) });
        window.open(`/#${_p.toString()}`, "_blank");
      } catch (err) {
        arataMesaj(corp.querySelector("#ac-msg"), (err && err.mesaj) || "Nu s-a putut deschide previzualizarea.", "eroare");
      }
      b.disabled = false; b.textContent = _t;
    });
    const zona = corp.querySelector("#ac-lista");
    try {
      const r = await api.get(`/tenants/${t.id}/client-acces`);
      if (!actuala()) return;
      const cl = r.clienti || [];
      /* [lotul 13, 555] inactiv cu motivul SCRIS lângă el (DS cap.1, ca „Validează” din Bilanț): `title` pe un buton dezactivat nu se
         vede — Chromium nu arată indicația unui element dezactivat; același ajutor ca butonul unei generări făcute */
      { const _pv = corp.querySelector("#ac-btn-preview"); if (_pv && !cl.length) butonGenerat(_pv, "Previzualizarea cere un cont de client: invită unul cu „Invită client nou”."); }
      if (!cl.length) { zona.innerHTML = `<p class="ecran-nota">Niciun cont de client încă.</p>`; }
      else {
        zona.innerHTML = cl.map((c) => `
          <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #e5e9f0">
            <div><b>${esc(c.email)}</b> · ${esc(c.nume || "")} ${c.activ ? "" : ' · <span style="color:var(--rosu)">dezactivat</span>'}</div>
            <button class="buton-secundar" data-id="${c.id}" data-actiune="DELETE /tenants/{tenant_id}/client-acces/{user_id}"${c.activ ? "" : atributeInactiv("Accesul e deja revocat.")}>Revoc\u0103</button>   <!-- [lotul 13, 675] -->
          </div>`).join("");
        zona.querySelectorAll("button[data-id]").forEach((b) => b.addEventListener("click", () => {
          confirmaCaseta(b.parentElement, "Revoci accesul acestui client?", async () => {
            await api.del(`/tenants/${t.id}/client-acces/${b.dataset.id}`);
            randeazaPrincipal();
          }, { textOk: "Revoc\u0103" });
        }));
      }
    } catch (e) { if (!actuala()) return; zona.innerHTML = `<p class="ecran-nota pe-randuri">${esc(e.mesaj || e.message)}</p>`; }
  }
  function randeazaFormular() {
    nav.setInapoi(randeazaPrincipal);
    corp.innerHTML = `
      <div class="camp" style="margin-bottom:12px">
        <label for="ac-email" class="camp-eticheta">Email client</label>
        <input class="camp-input" id="ac-email" type="email" placeholder="client@firma.ro" autocomplete="off" autofocus>
      </div>
      <div class="camp" style="margin-bottom:14px">
        <label for="ac-nume" class="camp-eticheta">Nume (opțional)</label>
        <input class="camp-input" id="ac-nume" placeholder="Numele persoanei">
      </div>
      <p class="ecran-nota" id="ac-msg" style="margin:0 0 10px"></p>
      <button class="buton-primar" id="ac-btn" data-actiune="POST /tenants/{tenant_id}/client-acces">Trimite invitația</button>
      <button class="btn-link" id="ac-renunta" style="margin-left:10px">Renun\u021b\u0103</button>
    `;
    const msg = corp.querySelector("#ac-msg");
    corp.querySelector("#ac-renunta").addEventListener("click", randeazaPrincipal);
    corp.querySelector("#ac-btn").addEventListener("click", async () => {
      const email = corp.querySelector("#ac-email").value.trim();
      curataEroriCamp(corp);
      // [lotul 11, 440] lângă câmp, prin helper (intră în caseta „NU s-a salvat.”), nu un `<span>` scris de mână
      if (!email.includes("@")) { eroareCamp(corp, "ac-email", "Email invalid."); return; }
      msg.textContent = "Se trimite...";
      try {
        await api.post(`/tenants/${t.id}/client-acces`, { email, nume: corp.querySelector("#ac-nume").value.trim() });
        mesajSucces = "Invitație trimisă pe " + esc(email) + ".";
        randeazaPrincipal();
      } catch (e) {
        msg.textContent = "";
        arataRefuzul(corp, e && (e.mesaj || e.message) ? e : { ...(e || {}), mesaj: "Invitația nu a plecat." }, msg,
          { campuri: { email: "ac-email", nume: "ac-nume" } });   // [440]
      }
    });
  }
  randeazaPrincipal();
}
// fara_mesaj_v1

// inapoi_meniu_v1

// module_stiva_v1

// casa_std_v1

// verif_doc_pozate_v1

// bon_flux_e6_v1

// bon_flux_e7_v1

// bon_flux_e8_v1

// bon_flux_e9_v1

// bon_flux_e9b_v1

// audit_cab_lot1_v1

// audit_cab_lot2_v1

// bon_cabinet_v1

// firma_email_optional_v1

// faza_b_traseu_v1

// provenienta_v1

// fara_precompletari_v1

// entitate_sursa_unica_v1

// casa_conform_v1

// precompletari_rest_v1
