// [lotul 11, deficiența 450 + pct.23 + decizia 10.3 „Borderoul se corectează prin stornare, ca factura.”] Borderoul de achiziție — ecranul lui,
// lângă NIR (Stocuri), cu nume în limbaj contabil. Până azi era formularul generic „Achiziție de la neînregistrat (persoană fizică) — D394
// op. N”, în „Operațiuni speciale › TVA regimuri speciale”, cu articolul ca text liber: borderoul crea tacit un articol nou („grau”) lângă
// cel existent, iar după generare formularul rămânea activ (a doua apăsare = a doua notă).
//   - articolul se ALEGE din nomenclatorul stocului (lista articolelor); „Articol nou…” e cererea explicită (denumirea și UM-ul lui apar
//     numai atunci); serverul refuză articolul nou cu denumirea unuia existent (și fără diacritice: „grau” = „grâu”);
//   - după generare formularul se închide (câmpurile și butonul inactive, confirmarea cu conturile notei — `dupaGenerare`, DS cap.6), iar
//     un borderou nou se începe cu „Borderou nou”; serverul refuză și el a doua trimitere a aceluiași borderou (`BORDEROU_DUBLAT`);
//   - borderourile lunii, fiecare cu nota lui și cu „Stornează” (documentul de stornare legat, nota inversă, intrarea în stoc stornată).
// Ruta scrierii rămâne `POST /tenants/{tenant_id}/achizitie-neinregistrat` (operațiunea D394 N); câmpurile poartă id-urile din refuzurile
// serverului (`op-*`). Gard: core/test_lot11_b_450_borderou.py (fiecare câmp citit de server are câmpul lui aici).
import { api, ultimaCerere, esc, bani, cantitate, arataMesaj, dataIso, dataRo, stareNota, pasNota, eroareCamp, curataEroriCamp, confirmaCaseta,
  dupaGenerare, atributeInactiv } from "../api.js?v=7036a2d894";
import { cautaInLista } from "./emitere_ecran.js?v=ff34c195be";   /* [lotul 12, 488] */

/** Conturile pe care borderoul aduce marfa în gestiune (aceeași listă ca serverul, `uc_tenants.achizitie_neinregistrat`). */
const CONTURI_STOC = ["371", "301", "302", "303"];
const laStoc = (cont) => CONTURI_STOC.some((p) => String(cont || "").trim().startsWith(p));
const ARTICOL_NOU = "__nou__";

export async function ecranBorderou(corp, nav, t) {
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;
  let articole = [], categoriiN = [];
  try {
    articole = (await api.get(`/tenants/${t.id}/stocuri/articole`)).articole || [];
    // categoria bunului pentru D394 op. N (lit.D), cu cerealele pe codul NC (HG 1/2016 pct.109 alin.(7)) — lista vine de la server
    categoriiN = (await api.get(`/tenants/${t.id}/borderouri?an=${an}&luna=${luna}`)).categorii_n || [];
  } catch (e) {
    corp.innerHTML = `<p class="ecran-nota">Nu s-a putut citi nomenclatorul articolelor: ${esc((e && e.mesaj) || "reîncearcă")}.</p>`;
    return;
  }
  const camp = (id, eticheta, input, opt = {}) => `<div class="camp" id="${id}-rand"${opt.ascuns ? " hidden" : ""}>
      <label class="camp-eticheta" for="${id}">${esc(eticheta)}${opt.optional ? "" : '<span class="oblig">*</span>'}</label>${input}
      ${opt.ajutor ? `<span class="camp-ajutor">${esc(opt.ajutor)}</span>` : ""}</div>`;
  const text = (id, et, opt = {}) => camp(id, et, `<input type="text" id="${id}" class="camp-input" aria-label="${esc(et)}"${
    opt.valoare != null ? ` value="${esc(opt.valoare)}"` : ""}>`, opt);
  const campNumeric = (id, et, opt = {}) => camp(id, et, `<input type="number" step="${opt.pas || "0.01"}" id="${id}" class="camp-input" aria-label="${esc(et)}">`, opt);

  const formular = () => `
      <form class="pf-frand" id="ba-form" style="display:block" novalidate>
        <fieldset id="ba-campuri" style="border:0;padding:0;margin:0">
        <div class="grila-campuri">
          ${camp("op-data", "Data", `<input type="date" id="op-data" class="camp-input" aria-label="Data" value="${dataIso()}">`)}
          ${text("op-numar", "Nr. borderou", { optional: true, ajutor: "Gol = numerotat de aplicație (BA-n, următorul număr al anului)." })}
          ${text("op-furnizor_nume", "Vânzătorul (persoană fizică)")}
          ${text("op-furnizor_adresa", "Domiciliul vânzătorului")}
          ${text("op-furnizor_act", "Actul de identitate (seria și numărul)")}
          ${campNumeric("op-valoare", "Valoarea")}
          ${text("op-cont_cheltuiala", "Contul (stoc sau cheltuială)", {
            ajutor: "Contul uzual: 301 (materii prime), 371 la mărfuri. Pe un cont de stoc (371, 301, 302, 303) marfa intră în gestiune odată cu borderoul: alege articolul și cantitatea." })}
          ${camp("op-articol", "Articolul (din nomenclator)", `<input type="text" id="op-articol-cauta" class="camp-input" placeholder="Caută articolul în stoc…" aria-label="Caută articolul" autocomplete="off" style="margin-bottom:6px">
            <select id="op-articol" class="camp-input" aria-label="Articolul (din nomenclator)">
              <option value="" selected>— alege —</option>
              ${articole.map((a) => `<option value="${a.id}" data-um="${esc(a.um || "")}">${esc(a.denumire)} · ${esc(a.um || "buc")} · stoc ${esc(cantitate(a.stoc, a.um))}</option>`).join("")}
              <option value="${ARTICOL_NOU}">Articol nou… (îl creez acum)</option>
            </select>`, { ajutor: "Alege-l din listă. „Articol nou…” îl creează în nomenclator, numai dacă denumirea nu e deja a altui articol." })}
          ${text("op-articol_den", "Denumirea articolului nou", { ascuns: true })}
          ${text("op-um", "UM-ul articolului nou", { ascuns: true })}
          ${campNumeric("op-cantitate", "Cantitatea", { pas: "0.001", ajutor: "În UM-ul articolului." })}
          ${camp("op-categorie", "Categoria bunului (D394, lit. D)", `<select id="op-categorie" class="camp-input" aria-label="Categoria bunului (D394, lit. D)">
              <option value="" selected>— alege —</option>${categoriiN.map((c) => `<option value="${esc(c.cod)}">${esc(c.eticheta)}</option>`).join("")}</select>`,
            { ajutor: "Codul de produs din D394 (operațiunea N, achiziția de la o persoană neînregistrată în scopuri de TVA)." })}
          ${text("op-descriere", "Descriere", { optional: true })}
        </div>
        </fieldset>
        <div class="bara-fixa">
          <p style="margin-top:12px"><button type="button" class="buton-primar" id="op-trimite" data-genereaza-nota data-actiune="POST /tenants/{tenant_id}/achizitie-neinregistrat">Generează nota (ciornă)</button></p>
          <div id="op-mesaj"></div>
        </div>
      </form>`;

  const randuri = (lista) => lista.length ? lista.map((b) => `
      <div class="pf-frand" data-borderou="${b.id}">
        <div class="pf-frand-nume">${esc(b.eticheta || ("Borderou " + b.numar))} · ${esc(b.vanzator || "")}</div>
        <div class="pf-frand-sub">${b.articol ? esc(b.articol) + (b.cantitate ? " · " + esc(cantitate(b.cantitate, b.um)) : "") + " · " : ""}${
          b.valoare != null ? bani(b.valoare) + " lei" : ""}${b.nota_eticheta ? " · nota " + esc(b.nota_eticheta) + (b.nota_status ? " (" + esc(b.nota_status) + ")" : "") : ""}</div>
        ${b.storno_din ? `<div class="pf-frand-sub">Stornare pentru ${esc(b.storno_din)}.</div>` : ""}
        ${b.stornat_de ? `<div class="pf-frand-sub">Stornat prin ${esc(b.stornat_de)}.</div>` : ""}
        <!-- [lotul 13, 675 — DS cap.1 v2.104] „Stornează” stă pe fiecare borderou; pe stornare și pe borderoul stornat, inactiv cu motivul -->
        <button type="button" class="buton-secundar ba-storneaza" id="ba-storneaza-${b.id}" data-id="${b.id}"
            data-actiune="POST /tenants/{tenant_id}/borderouri/{factura_id}/storneaza"${b.storno_din ? atributeInactiv(`E chiar stornarea lui ${b.storno_din}.`)
              : (b.stornat_de ? atributeInactiv(`Borderoul e stornat deja, prin ${b.stornat_de}.`) : "")}>Stornează</button>
        <div id="ba-storno-mesaj-${b.id}"></div>
      </div>`).join("") : `<div class="stare-goala">Niciun borderou de achiziție în luna asta.</div>`;

  const deschideNota = async (nid, data) => {
    const [a, l] = String(data || "").split("-").map((x) => parseInt(x, 10));
    const { ecranJurnal } = await import("./firme.js?v=eecc415409");
    nav.deschide("Registru jurnal", (c2) => ecranJurnal(c2, nav, t, Object.assign({ evidentiaza: nid },
      Number.isFinite(a) && Number.isFinite(l) ? { an: a, luna: l } : {})), { lat: "tabel" });
  };
  const butonNota = (zona, r, data) => {
    if (!r || !r.inregistrare_id) return;
    const p = document.createElement("p");
    const b = document.createElement("button");
    b.type = "button"; b.className = "buton-secundar"; b.id = "op-deschide-nota";
    b.dataset.faraActiune = "navigare la Registrul jurnal; validarea de acolo poartă acțiunea";
    b.textContent = `Deschide nota ${String(r.nota_eticheta || "").replace(/^nota\s+/i, "")} în Registrul jurnal`.replace(/\s+/g, " ");
    b.addEventListener("click", () => deschideNota(r.inregistrare_id, data));
    p.appendChild(b);
    zona.appendChild(p);
  };

  const cerereNoua = ultimaCerere();   // [C103] „← luna” / „luna →” apăsate în șir: numai lista lunii din etichetă ajunge pe ecran
  const incarcaLista = async () => {
    const actuala = cerereNoua();
    const z = corp.querySelector("#ba-lista");
    corp.querySelector("#ba-luna").textContent = dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric");
    try {
      const r = await api.get(`/tenants/${t.id}/borderouri?an=${an}&luna=${luna}`);
      if (!actuala()) return;
      z.innerHTML = randuri(r.borderouri || []);
    } catch (e) {
      if (!actuala()) return;
      z.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca borderourile: ${esc((e && e.mesaj) || "reîncearcă")}.</p>`;
      return;
    }
    z.querySelectorAll(".ba-storneaza").forEach((b) => b.addEventListener("click", () => {
      const zona = z.querySelector(`#ba-storno-mesaj-${b.dataset.id}`);
      confirmaCaseta(zona, "Stornezi borderoul? Se scrie un borderou de stornare legat de el (cantitatea și valoarea cu minus), nota inversă " +
        "(de validat în Registru jurnal) și, dacă a adus marfă în stoc, stornarea intrării. Borderoul inițial rămâne în evidență.", async () => {
        try {
          const r = await api.post(`/tenants/${t.id}/borderouri/${b.dataset.id}/storneaza`, {});
          await incarcaLista();
          const zm = corp.querySelector("#ba-lista-mesaj");
          dupaGenerare(zm, null, { titlu: r.mesaj || `Stornare ${r.eticheta || ""}`, eticheta: r.nota_eticheta, linii: r.nota_linii,
            detalii: [r.miscari_stornate && r.miscari_stornate.length ? "Intrarea în stoc a borderoului e stornată în fișa de magazie." : ""] });
          butonNota(zm, r, dataIso());
        } catch (e) {
          arataMesaj(zona, (e && e.mesaj) || "Stornarea nu s-a făcut — reîncearcă.", "eroare");
        }
      }, { textOk: "Stornează" });
    }));
  };

  const deseneaza = () => {
    corp.innerHTML = `
      <h2 class="pf-titlu">Borderou de achiziție</h2>
      <p class="pf-intro">Cumpărarea de la o persoană fizică (OMFP 2634/2015, cod 14-4-13): vânzătorul, bunul, cantitatea și valoarea. Nota se
        validează din Registru jurnal; în D394 intră ca operațiune N.</p>
      <div id="ba-form-zona">${formular()}</div>
      <h3 class="pf-subtitlu">Borderourile lunii <span id="ba-luna"></span>
        <button type="button" class="buton-secundar" id="ba-prev" style="margin-left:12px">← luna</button>
        <button type="button" class="buton-secundar" id="ba-next">luna →</button></h3>
      <div id="ba-lista-mesaj"></div>
      <div class="pf-lista" id="ba-lista"><p class="ecran-nota">Se încarcă...</p></div>`;
    corp.querySelector("#ba-prev").addEventListener("click", () => { luna -= 1; if (luna < 1) { luna = 12; an -= 1; } incarcaLista(); });
    corp.querySelector("#ba-next").addEventListener("click", () => { luna += 1; if (luna > 12) { luna = 1; an += 1; } incarcaLista(); });
    legaFormularul();
    incarcaLista();
  };

  const legaFormularul = () => {
    const f = corp.querySelector("#ba-form");
    const v = (id) => (f.querySelector("#" + id) || {}).value || "";
    const arata = (id, da) => { const r = f.querySelector("#" + id + "-rand"); if (r) r.hidden = !da; };
    // câmpurile articolului se văd numai pe un cont de stoc; denumirea și UM-ul, numai la „Articol nou…”
    const actualizeaza = () => {
      const stoc = laStoc(v("op-cont_cheltuiala"));
      arata("op-articol", stoc); arata("op-cantitate", stoc);
      const nou = stoc && v("op-articol") === ARTICOL_NOU;
      arata("op-articol_den", nou); arata("op-um", nou);
    };
    f.querySelector("#op-cont_cheltuiala").addEventListener("input", actualizeaza);
    f.querySelector("#op-articol").addEventListener("change", actualizeaza);
    cautaInLista(f.querySelector("#op-articol-cauta"), f.querySelector("#op-articol"));   // [lotul 12, 488] căutarea în lista articolelor
    actualizeaza();
    const buton = f.querySelector("#op-trimite");
    buton.addEventListener("click", async () => {
      const zona = f.querySelector("#op-mesaj");
      curataEroriCamp(f);
      const stoc = laStoc(v("op-cont_cheltuiala"));
      // articolul și cantitatea (pe un cont de stoc) le cere serverul, cu fraza întreagă (ce lipsește și de ce — 402), toate deodată (440)
      const obligatorii = ["op-data", "op-furnizor_nume", "op-furnizor_adresa", "op-furnizor_act", "op-valoare", "op-cont_cheltuiala", "op-categorie"];
      let lipsa = 0;
      for (const id of obligatorii) {
        if (!v(id).trim()) {
          const et = (f.querySelector(`label[for="${id}"]`) || {}).textContent || id;
          eroareCamp(f, id, "Completează: " + et.replace(/\*$/, "").trim() + ".");
          lipsa++;
        }
      }
      if (lipsa) return;
      const corpReq = {
        data: v("op-data"), furnizor_nume: v("op-furnizor_nume").trim(), furnizor_adresa: v("op-furnizor_adresa").trim(),
        furnizor_act: v("op-furnizor_act").trim(), valoare: parseFloat(v("op-valoare")), cont_cheltuiala: v("op-cont_cheltuiala").trim(),
        categorie: v("op-categorie"),
      };
      if (v("op-numar").trim()) corpReq.numar = v("op-numar").trim();
      if (v("op-descriere").trim()) corpReq.descriere = v("op-descriere").trim();
      if (stoc) {
        if (v("op-cantitate").trim()) corpReq.cantitate = parseFloat(v("op-cantitate"));
        if (v("op-articol") === ARTICOL_NOU) {
          corpReq.articol_nou = true;
          corpReq.articol = v("op-articol_den").trim();
          corpReq.um = v("op-um").trim();
        } else if (v("op-articol")) {
          corpReq.articol_id = parseInt(v("op-articol"), 10);
        }
      }
      try {
        const r = await api.post(`/tenants/${t.id}/achizitie-neinregistrat`, corpReq);
        // [450] după generare formularul se închide: câmpurile inactive, butonul inactiv cu motivul (`dupaGenerare`); altul = „Borderou nou”
        f.querySelector("#ba-campuri").disabled = true;
        const i = r.intrare_stoc;
        dupaGenerare(zona, buton, {
          titlu: `Borderou ${r.numar} generat — notă ${stareNota(r)}`, eticheta: r.nota_eticheta, linii: r.nota_linii,
          motiv: "Borderoul e generat — nota lui o vezi în Registru jurnal. Pentru altul: „Borderou nou”.",
          detalii: [i ? `Intrare în stoc: ${i.articol} · ${cantitate(i.cantitate)}${i.articol_nou ? " (articol nou în nomenclator)" : ""}.` : "",
            r.in_d394 ? "Intră în D394 ca operațiune N." : "", r.avertisment || ""],
          pas: pasNota(r),   // HTML deja escapat (api.pasNota)
        });
        butonNota(zona, r, corpReq.data);
        const p = document.createElement("p");
        const bn = document.createElement("button");
        bn.type = "button"; bn.className = "buton-secundar"; bn.id = "ba-nou";
        bn.dataset.faraActiune = "deschide un formular gol; generarea lui poartă acțiunea";
        bn.textContent = "Borderou nou";
        bn.addEventListener("click", () => { corp.querySelector("#ba-form-zona").innerHTML = formular(); legaFormularul(); });
        p.appendChild(bn);
        zona.appendChild(p);
        incarcaLista();
      } catch (e) {
        // refuzul serverului care își numește câmpurile: fiecare lângă câmpul lui; restul, în zona formularului
        const peCamp = ((e && e.erori_campuri) || []).filter((x) => eroareCamp(f, x.camp, x.mesaj)).length;
        arataMesaj(zona, (peCamp ? "Nota nu s-a generat: " : "") + ((e && (e.mesaj || e.message)) || "Nu s-a putut genera nota — verifică datele și reîncearcă."), "eroare");
      }
    });
  };

  deseneaza();
}
