// cadru.js — BARA DE JOS a ferestrei de lucru (comanda 15.1-E2, pct.3; DS ferestre și tabele, secțiunea 1): o singură piesă, chemată de navigator
// la fiecare fereastră de lucru; ecranele nu o desenează.
//
//   72 px, fixă, mereu vizibilă, ultimul copil al corpului ferestrei; acțiunea principală L (52 px) în dreapta, „Renunță” M lângă ea numai pe ferestrele din PASTREAZA_RENUNTA; un singur
//   buton principal; nimic altceva în bară. Motivul butonului inactiv (729) stă în stânga, în bară. Mesajele de refuz și de eroare ale acțiunii
//   (`.bara-fixa`, rezumatul totalurilor) rămân DEASUPRA barei, fără derulare.
//
// Acțiunea principală a ecranului, în ordine: (1) elementul marcat `data-actiune-principala`; (2) butonul principal din `.bara-fixa` (ultimul);
// (3) butonul principal al unui formular (`form`, `.ds-formular`, `.pf-frand`), ultimul; (4) [15.1-E5] catalogul `CATALOG_ACTIUNE_PRINCIPALA`, pe tipuri
// de fereastră (salvează / emite -> coadă -> continuă -> creare / import -> „Descarcă PDF”). Același element, nu o copie: identificatorul, ascultătorii și
// testele ecranului rămân neschimbate; el se mută în bară și poartă `data-actiune-principala`. „Închide” nu e acțiune principală (fereastra se închide din „←”);
// ferestrele de stare și meniurile de butoane (`FARA_ACTIUNE_PRINCIPALA`) au bara fără buton principal și fără „Renunță”. „Renunță” (un pas înapoi, ca „←”)
// apare numai pe ferestrele cu formular din PASTREAZA_RENUNTA (fără „←” activ sau cu „Renunță” cu efect propriu).
//
// Starea o dă piesa: câmpurile obligatorii ale ecranului sunt etichetele cu „*”; cât un câmp vizibil de acest fel e gol, butonul principal e
// inactiv, cu motivul „Completează: …” în bară. Ecranul spune doar ce e obligatoriu; el nu-și mai ține butonul activ / inactiv.

import { alegereButoane, alegereComutator, alegereText, esteAlege, inactiv, activ, MAX_BUTOANE, cate } from "./api.js?v=7396e03327";
import { listaCuCautare, tabeleDSAplica, carduriDSAplica, listeDSAplica, coloaneDateSumeAplica, tiparesteTabel, LISTE_ASTEA } from "./ds_piese.js?v=e115d72f0f";

const _normalizeaza = (t) => String(t || "").replace(/\*/g, "").replace(/\s+/g, " ").trim();
const _vizibil = (el) => !!(el.offsetParent || el.getClientRects().length);

function _controlEtichetei(et) {
  const f = et.getAttribute("for");
  if (f) { const c = (et.getRootNode() || document).getElementById ? document.getElementById(f) : null; if (c) return c; }
  const interior = et.querySelector("input:not([type=hidden]), select, textarea");
  if (interior) return interior;
  const parinte = et.closest(".camp, .camp-rand, .ds-camp, .pf-camp, div, p");
  return parinte && parinte.querySelector("input:not([type=hidden]), select, textarea");
}

// câmpurile obligatorii (etichete cu „*”) goale și vizibile, în ordinea din ecran; [17.5-H2] fiecare control se numește o singură dată (`label.camp > span.camp-eticheta` are „*”
// și pe etichetă, și pe text) și cu numele din `.camp-eticheta` (nu cu tot textul etichetei: ajutorul și lista cu căutare din ea nu intră în nume)
function _lipsuri(corp) {
  const out = [], numite = new Set();
  for (const et of corp.querySelectorAll("label, .camp-eticheta")) {
    if (!/\*/.test(et.textContent) || !_vizibil(et)) continue;
    const c = _controlEtichetei(et);
    if (!c || numite.has(c) || c.disabled || c.readOnly || !_vizibil(c)) continue;
    if (c.type === "checkbox" || c.type === "radio") continue;
    if (String(c.value || "").trim() === "") { numite.add(c); const nume = (et.matches("label") && et.querySelector(".camp-eticheta")) || et;
      out.push(_normalizeaza(nume.textContent.replace(c.textContent || "", "")) || "câmp obligatoriu"); }
  }
  return out;
}

// [15.1-E3, 729] PIESA „câmp obligatoriu”: orice câmp pe care ecranul îl cere (`required` / `aria-required`) poartă „*” în etichetă, ca bara de jos să-și poată
// face treaba (butonul principal cenușiu cu „Completează: …”); ecranul nu mai scrie „*” de mână pe fiecare câmp. Etichetele care îl au deja nu se ating.
function _marcheazaObligatorii(corp) {
  for (const c of corp.querySelectorAll("input[required], select[required], textarea[required], [aria-required='true']")) {
    if (c.type === "hidden" || c.closest("template, [hidden]")) continue;
    const et = (c.id && document.querySelector(`label[for="${CSS.escape(c.id)}"]`)) || c.closest("label") || (c.previousElementSibling && c.previousElementSibling.matches(".camp-eticheta") ? c.previousElementSibling : null);
    if (!et || /\*/.test(et.textContent)) continue;
    const ast = document.createElement("span");
    ast.className = "oblig";
    ast.textContent = "*";
    const prim = et.querySelector(".camp-eticheta") || et;
    const control = prim.querySelector("input, select, textarea");
    if (control) prim.insertBefore(ast, control); else prim.appendChild(ast);   // „*” în etichetă, nu după câmp
  }
}

// [15.1-E3, 722 / F-A.3] PIESA „listă”: orice listă derulantă a ferestrei de lucru e fie grup de butoane (până la 6 variante scurte, 676), fie lista cu căutare (peste 6
// variante sau texte lungi); lista derulantă rămâne în pagină, nevăzută, ca sursă a valorii (`value`, `change`, `select_option` merg ca înainte). Nu se ating: listele
// din tabele (alegerea pe rând), cele deja înlocuite, cele cu `data-fara-piesa`, listele multiple.
function _listeDerulante(corp) {
  for (const sel of corp.querySelectorAll("select")) {
    const reale = [...sel.options].filter((o) => !esteAlege(o) && o.value !== "" && !o.hidden);
    if (sel.dataset.gol && reale.length) { sel.classList.remove("alegere-sursa"); delete sel.dataset.gol; }   // opțiunile au venit între timp
    if (sel.__lista || sel.__butoane || sel.multiple || !_vizibil(sel) || sel.closest(".fereastra-antet, .cautare-globala, [data-fara-piesa], template")) continue;
    if (sel.classList.contains("ds-lista-sursa") || sel.classList.contains("alegere-sursa")) continue;
    // [15.1-E5] lista fără nicio variantă (încă neîncărcată / goală) nu se arată: nu e nimic de ales, iar o listă derulantă goală nu rămâne pe ecran
    if (!reale.length) { if (!sel.closest("table")) { sel.classList.add("alegere-sursa"); sel.dataset.gol = "1"; } continue; }
    // [15.1-E5, pct.2] lista cu „— alege —” devine grup fără buton apăsat, iar câmpul e obligatoriu (eticheta cu „*”, butonul principal cenușiu până se alege)
    if ([...sel.options].some(esteAlege)) sel.required = true;
    if (sel.closest("table")) {   // [15.1-E5] în rândul de tabel: două variante = comutator XS; 7 sau mai multe = lista cu căutare
      if (reale.length === 2) alegereComutator(sel);
      else if (reale.length >= 7) listaCuCautare(sel, { gol: "Alege din listă", cautare: "Caută în listă…" });
      continue;
    }
    if (reale.length === 1) { alegereText(sel); continue; }   // [15.1-E5] o singură variantă = text, fără control
    const lung = reale.some((o) => (o.dataset.buton || o.textContent || "").trim().length > 30);
    // [16.8-C1, 760] lista cerută în șablon ca grup de butoane (`data-butoane`) rămâne grup: nu primește și lista cu căutare (două controale pentru aceeași alegere)
    const cerutButoane = sel.hasAttribute("data-butoane") && reale.length <= (Number(sel.getAttribute("data-butoane")) || MAX_BUTOANE);
    if ((reale.length >= 7 || lung) && !cerutButoane) listaCuCautare(sel, { gol: "Alege din listă", cautare: "Caută în listă…" });
    else alegereButoane(sel);
  }
}

// [15.1-E5, pct.2] grupul de butoane M care nu încape pe un rând (la 1366 px) trece pe DOUĂ rânduri egale, nu pe listă
function _grupuriPeDouaRanduri(corp) {
  for (const g of corp.querySelectorAll(".alegere-butoane")) {
    if (g.hidden || !_vizibil(g)) continue;
    const n = g.children.length;
    if (n < 2) continue;
    if (g.classList.contains("alegere-doua")) continue;   // nu se schimbă la fiecare sincronizare (ar re-declanșa observatorul)
    const sus = [...g.children].map((x) => x.offsetTop);
    if (new Set(sus).size > 1 || g.scrollWidth > g.clientWidth + 1) { g.style.setProperty("--alegere-col", String(Math.ceil(n / 2))); g.classList.add("alegere-doua"); }
  }
}

// [15.1-E3] explicația de sub un câmp (`.camp-ajutor`) stă pe un rând, cu textul întreg în `title`; câmpul focusat o arată întreagă (CSS) — nu paragrafe lungi în formular
function _ajutoareScurte(corp) {
  for (const a of corp.querySelectorAll(".camp-ajutor")) if (!a.title && a.textContent.trim()) a.title = a.textContent.trim();
}

// [15.1-E5, pct.1] CATALOGUL acțiunii principale, pe tipuri de fereastră, în ordinea regulii: (1) formular -> butonul care salvează / emite / generează; (2) coadă sau
// aprobare -> „Validează toate” / „Aprobă” / „Răspunde”; (3) pas de asistent -> „Continuă”; (4) listă sau registru cu creare -> acțiunea de creare sau import;
// (5) doar de citit cu export -> „Descarcă PDF”. Se folosește numai când ecranul n-a marcat singur acțiunea (`data-actiune-principala`) și n-are buton primar
// de formular; prima potrivire, în ordinea catalogului, în ordinea din fereastră.
export const CATALOG_ACTIUNE_PRINCIPALA = [
  /^(Validează toate|Validează selectate|Aprobă|Răspunde)(?=\s|$)/,
  /^(Salvează|Emite|Contabilizează|Închide luna|Înregistrează|Înscrie|Trimite|Importă|Aplică|Sincronizează|Validează \(ANAF\)|Rulează|Verifică|Schimbă parola)(?=\s|$)/,
  /^Continuă(?=\s|$)/,
  /^(\+ )?(Operațiune nouă|Import extras|Adaugă|Deschide Asistenți|Invită|Descarcă model)(?=\s|$)|^(\+ )?[\p{L} ]{2,30} (nou|nouă)$/u,
  /^(Generează|Regenerează)(?=\s|$)/,
  /^Descarcă PDF(?=\s|$)/,
];

// Ferestrele „doar de citit cu export” (Cartea mare, Balanță, Rapoarte, Analitică stoc): „Descarcă PDF” e acțiunea lor, chiar când tabelul lipsește încă
export const EXPORT_PDF = /^(Cartea mare|Balanță de verificare|Rapoarte comerciale|Registrul de evidență fiscală|Jurnal regim marjă|Activitate cabinete)$/;

// Ferestrele fără acțiune principală: ecran de stare fără nicio acțiune sau meniu de butoane care doar deschide alte ferestre. Bara rămâne, fără buton principal și
// fără „Renunță”; închiderea e „←”. Lista pe nume (verificatorul o are la rândul b): `scripts/verificator_design.py::EXCEPTII_B`.
export const FARA_ACTIUNE_PRINCIPALA = /^(Sinteza zilei|Operațiuni speciale|Facturi|Firme|Import date|Mișcări, fișe de magazie, coduri, nivel minim|Mișcări și fișe de magazie)$|· CUI /;   // „· CUI ” = fereastra firmei (titlul ei: nume · CUI cod)

// [17.3, decizia arhitectului] Bara de jos a ferestrei cu formular nu are „Renunță”: revenirea este „←” din antet, iar „✕” închide fereastra. Păstrează „Renunță” numai
// fereastra al cărei formular deschis nu are „←” activ (altfel n-ar rămâne cu cale înapoi) și cea cu o „Renunță” cu efect propriu (golește ciorna de pe server). Lista pe nume
// (titlul din `.fir-acum`), identică cu `scripts/verificator_design.py::PASTREAZA_RENUNTA` și cu numele din docs/dovezi/17_3/inapoi.txt; dialogurile de confirmare au „Renunță” oricum.
export const PASTREAZA_RENUNTA = ["Încasări/plăți", "Invitații cabinete", "Notificări", "Pachete lunare"];

// meniu de butoane: fereastra al cărei conținut sunt cardurile care deschid alte ferestre (`.firme-optiune`), fără altă acțiune proprie
const _esteMeniu = (corp, bara) => !![...corp.querySelectorAll(".firme-optiune")].find(_vizibil)
  && ![...corp.querySelectorAll(".buton-primar")].some((b) => !bara.contains(b) && _vizibil(b) && !b.closest("table, template, details"));

// [16.8, 760] NU_MUTA = id-urile butoanelor găsite de catalog care NU se mută în bară (rămân în conținut; în bară stă un proxy care apasă originalul).
// Motivul fiecăruia: ecranul (sau testul) își caută butonul într-un container care nu conține bara, după mutare, într-un fișier în care lotul 16.8 nu are voie să schimbe
// logica (scrierea `?v=` în cascadă ar ieși din lista de fișiere permise) sau într-un test din plasa fixă, care nu se modifică. Un buton fără `id` nu se mută niciodată
// (ecranul nu-l poate căuta; rând dintr-o listă, ex. `.val-aproba`): proxy. Ecranele lor rămân roșii la rândul b: limită declarată, le închide lotul 16.9.
const NU_MUTA = new Set([
  "cab-salveaza-intocmitor",   // static/js/ecrane/intocmitor_bilant.js:66 (zona.querySelector)
  "op-trimite",               // static/js/ecrane/borderou_ecran.js:169 (f.querySelector)
  "rap-trimite",              // static/js/ecrane/admin_raportari.js:196, :246, :251 (fir.querySelector); frontend_test/e2e/e2e_pozitii_validate.py:656 („#rap-fir #rap-trimite”, plasa fixă)
  "nir-leaga",                // static/js/ecrane/nir_legare.js:34 (zona.querySelector)
  "pr-salveaza",              // static/js/ecrane/produse_ecran.js:311 (zona.querySelector)
  "asi-salveaza",             // static/js/ecrane/asistenti.js:284, :286 (box.querySelector)
  "pp-anaf-aplica",           // static/js/ecrane/clienti_ecran.js:442 (st.querySelector)
  "cm-calc",                  // static/js/ecrane/flux_concediu.js:213 (zona.querySelector)
  "mig-importa",              // static/js/ecrane/migrare.js:2557, :2664, :2665 (zona.querySelector)
  "mig-salveaza-rip",         // static/js/ecrane/migrare.js:2751, :2753 (zona.querySelector)
  "df-cui-continua",          // static/js/ecrane/date_firma.js:943 (zona.querySelector)
  "df-cui-confirma",          // static/js/ecrane/date_firma.js:957 (zona.querySelector)
  "an-trimite",               // static/js/ecrane/admin.js:206 (c.querySelector)
  "coada-confirma",           // static/js/ecrane/coada_trimite.js:80 (zona.querySelector)
  "coada-deja-inlocuieste",   // static/js/ecrane/coada_trimite.js:99 (b.querySelector)
]);
// [AC182] „Trimite sesizarea” din fereastra Suport (#rap-zona-sesizare) se mută în bară ca orice acțiune găsită de catalog; „Trimite” din Panou Admin › Raportări (același id) rămâne în fereastră
const _nuSeMuta = (b) => !b.id || (NU_MUTA.has(b.id) && !b.closest("#rap-zona-sesizare"));

// un buton dintr-un `<details>` închis nu se vede, dar există și poate fi acțiunea ferestrei: se judecă după `<details>`-ul lui, nu după el
const _vizibilSauInDetails = (b) => {
  if (_vizibil(b)) return true;
  const d = b.closest("details:not([open])");
  return !!d && _vizibil(d);
};

function _dinCatalog(corp, bara) {
  const eligibil = (b) => b.tagName === "BUTTON" && !bara.contains(b) && _vizibilSauInDetails(b) && !b.closest("table, template, .tn-actiuni, .fereastra-antet, .ds-semnal-cutie, .ds-rezumat-cutie, .set-meniu");   // [17.3] intrarea „Schimbă parola” din meniul Setări cont nu e acțiunea ferestrei
  const butoane = [...corp.querySelectorAll("button")].filter(eligibil);
  for (const rx of CATALOG_ACTIUNE_PRINCIPALA) {
    const g = butoane.find((b) => rx.test(_normalizeaza(b.textContent)));
    if (g) { g.__catalog = true; return g; }
  }
  return null;
}

function _proxy(sursa) {
  const p = document.createElement("button");
  p.type = "button";
  p.dataset.faraActiune = "apasă butonul din fereastră care face această acțiune";
  p.textContent = _normalizeaza(sursa.textContent);
  p.__sursa = sursa;
  if (sursa.__slab) p.__slab = true;   // proxy-ul unui buton slab rămâne slab (înlocuibil de catalog)
  sursa.classList.remove("buton-primar"); sursa.classList.add("buton-secundar");   // în fereastră rămâne ca buton secundar: un singur buton principal, cel din bară
  p.addEventListener("click", () => sursa.click());
  return p;
}

function _alege(corp, bara, areDeja, titlu) {
  const liber = (b) => !(b.__retras && areDeja !== false);   // o acțiune retrasă din bară nu o ia înapoi cât alta e în bară (altfel s-ar schimba la nesfârșit)
  const marcat = [...corp.querySelectorAll("[data-actiune-principala]")].filter((b) => !bara.contains(b) && liber(b)).pop();
  if (marcat) return marcat;
  if (EXPORT_PDF.test(titlu || "")) return _pdfulFerestrei(corp, bara, liber);   // [17.5-D, 819] în ferestrele de export PDF-ul e acțiunea, înaintea barei fixe, a formularului și a catalogului
  const fixe = [...corp.querySelectorAll(".bara-fixa .buton-primar")].filter((b) => b.tagName === "BUTTON" && liber(b));
  if (fixe.length) return fixe[fixe.length - 1];
  const eligibil = _eligibilPrincipal(bara, liber);
  const formular = [...corp.querySelectorAll("form .buton-primar, .ds-formular ~ * .buton-primar, .pf-frand:has(> .ds-formular) .buton-primar")].filter(eligibil);
  if (formular.length) return formular[formular.length - 1];
  if (areDeja === true) return null;   // catalogul nu înlocuiește o acțiune deja în bară (în afară de exportul de rezervă, care cedează locul)
  return _dinCatalog(corp, bara) || (areDeja === false ? _exportTabel(corp, bara, liber) : null);
}

// butonul care poate urca în bară: în conținut (nu în bară), nu retras, în afara tabelului, a șabloanelor, a meniurilor și a rezumatului lipit
const _eligibilPrincipal = (bara, liber, cuRezumat = false) => (b) => b.tagName === "BUTTON" && !bara.contains(b) && liber(b)
  && !b.closest(cuRezumat ? "table, template, details, .tn-actiuni" : "table, template, details, .tn-actiuni, .rezumat-fix");

// [17.5-H2] înregistrare = rând de `tbody` care nu e starea goală a tabelului; lista de înregistrări goală = `.stare-goala` într-o listă din LISTE_ASTEA
const _randGol = (r) => r.classList.contains("fd-rand-gol") || !!r.querySelector(".stare-goala");
const _tabele = (corp) => [...corp.querySelectorAll("table")].filter((x) => _vizibil(x) && !x.closest("template, details"));
const _tabelCuInregistrari = (corp) => _tabele(corp).some((t) => [...t.querySelectorAll("tbody > tr")].some((r) => !_randGol(r)));
const _listaGoala = (corp) => [...corp.querySelectorAll(LISTE_ASTEA)].some((l) => _vizibil(l) && !l.closest("template, details:not([open])") && !!l.querySelector(":scope > .stare-goala"));
const MOTIV_FARA_INREGISTRARI = "Nu există înregistrări de exportat.";

// [15.1-E5, pct.1] fereastra doar de citit, cu tabel și fără export: „Descarcă PDF” se adaugă ca export al tabelului (tipărirea tabelului, „Salvează ca PDF”)
// [17.5, 791 / 793] când fereastra are un singur buton principal al ei (eligibil, `buton-primar`, altul decât „Descarcă PDF”), acela e acțiunea ferestrei: PDF-ul de
// rezervă nu mai e ales. Aici rezumatul lipit sus (`.rezumat-fix`) nu exclude butonul: „Fluturaș” al fișei salariatului stă în `#ss-butoane`, în rezumat. Mai multe sau
// niciunul: rezerva rămâne. Ferestrele din EXPORT_PDF rămân cu PDF-ul (la ele chiar el e acțiunea). Butonul ales trece prin drumul unuia găsit de catalog (`__catalog`: cu id în
// afara NU_MUTA se mută în bară, fără id rămâne în fereastră și în bară stă un proxy): „Fluturaș” (id ss-fluturas) se mută în bară, ca singura copie (AC108; oracolul X07, e.1: 12 copii direcți).
function _exportTabel(corp, bara, liber) {
  const eligibil = _eligibilPrincipal(bara, liber, true);
  const proprii = [...corp.querySelectorAll("button.buton-primar")].filter((b) => eligibil(b) && _normalizeaza(b.textContent) !== "Descarcă PDF");
  if (proprii.length === 1) { proprii[0].__slab = true; proprii[0].__catalog = true; return proprii[0]; }   // slab, ca PDF-ul: o acțiune găsită ulterior în catalog îl înlocuiește (un buton trecător din timpul încărcării nu ține locul)
  // [17.5-H2] PDF-ul de rezervă numai pe fereastra cu tabel sau cu o listă de înregistrări (goală: PDF-ul rămâne, inactiv, cu motivul în bară); fără listă și fără tabel, nimic
  if (!_tabele(corp).length && !_listaGoala(corp)) return null;
  const b = _exportPdf(corp);
  b.__slab = true;   // acțiune de rezervă: o acțiune găsită ulterior în catalog o înlocuiește
  return b;
}

// „Descarcă PDF” de rezervă al ferestrei: tipărirea tabelului, fără cerere la server; același nod la fiecare sincronizare
function _exportPdf(corp) {
  if (!corp.__exportPdf) {
    const b = document.createElement("button");
    b.type = "button"; b.className = "buton-primar"; b.textContent = "Descarcă PDF";
    b.dataset.faraActiune = "export al tabelului din fereastră (tipărire), fără cerere la server";
    b.addEventListener("click", () => tiparesteTabel(corp));
    corp.__exportPdf = b;
  }
  return corp.__exportPdf;
}

// [17.5-D, 819] fereastra din EXPORT_PDF: butonul ei „Descarcă PDF”, dacă îl are (trece prin drumul unuia găsit de catalog: `__catalog`), altfel cel de rezervă; nu e „slab”
function _pdfulFerestrei(corp, bara, liber) {
  const eligibil = _eligibilPrincipal(bara, liber, true);
  const propriu = [...corp.querySelectorAll("button")].find((b) => eligibil(b) && _vizibil(b) && /^Descarcă PDF(?=\s|$)/.test(_normalizeaza(b.textContent)));
  if (propriu) { propriu.__catalog = true; return propriu; }
  // [AC183] butonul propriu al ferestrei, ajuns în bară, rămâne acțiunea (nu e înlocuit de exportul de rezervă, altfel cele două s-ar schimba la fiecare cadru)
  const dinBara = [...bara.querySelectorAll(".fj-butoane .fj-principal")].find((b) => b.isConnected && !b.__sursa && b !== corp.__exportPdf && /^Descarcă PDF(?=\s|$)/.test(_normalizeaza(b.textContent)));
  if (dinBara) return dinBara;
  return _exportPdf(corp);
}

// o urmă (comentariu) lăsată în locul din care butonul trece în bară: dispare odată cu zona pe care ecranul o redesenează
function _urma(b) { const u = document.createComment("fj"); b.before(u); return u; }

// containerul de formular din care vine butonul: numai câmpurile lui hotărăsc dacă butonul e inactiv (nu etichetele altor părți ale ferestrei). [17.5-H2] Ecranul al cărui
// formular nu e `form` / `.ds-formular` îl numește cu `data-formular` (Ore suplimentare, Certificat nou, Firmă nouă, D104 pasul 2): fereastra care nu-l numește nu devine inactivă
const _formularul = (b) => b.closest("form, .ds-formular, .pf-frand:has(> .ds-formular), [data-formular]");

/** Pune bara de jos pe fereastra `fer`; întoarce `{ sincronizeaza, bara }`. `renunta` = ce face „Renunță” (un pas înapoi / închide) pe ferestrele din PASTREAZA_RENUNTA. */
export function baraDeJos(fer, corp, { renunta }) {
  const bara = document.createElement("div");
  bara.className = "fereastra-jos";
  bara.innerHTML = `<span class="fj-motiv" aria-live="polite"></span><span class="fj-butoane"></span>`;
  const loc = bara.querySelector(".fj-butoane");
  const motiv = bara.querySelector(".fj-motiv");
  const renuntaPiesei = () => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "buton-secundar fj-renunta"; b.textContent = "Renunță";
    b.addEventListener("click", () => renunta());
    return b;
  };
  let principal = null;

  function sincronizeaza() {
    if (!corp.isConnected) return;
    _marcheazaObligatorii(corp);
    _ajutoareScurte(corp);
    _listeDerulante(corp);
    listeDSAplica(corp);   // [15.1-E4] lista de înregistrări → tabelul DS
    tabeleDSAplica(corp);   // [15.1-E4] tabelul DS, o singură dată pentru toate ecranele
    _grupuriPeDouaRanduri(corp);   // [15.1-E5, pct.2]
    coloaneDateSumeAplica(corp);   // [15.1-E5, 741] data și suma nu se taie în niciun tabel DS
    carduriDSAplica(corp);   // [15.1-E4] cardul-rezumat, o singură dată pentru toate ecranele
    if (bara.parentElement !== corp || corp.lastElementChild !== bara) corp.appendChild(bara);
    // acțiunea al cărei loc de origine (zona ecranului) a fost redesenat de ecran e veche: ecranul a scos-o odată cu zona (ex. „Scrie nota” după scriere)
    for (const b of [...loc.children]) if (b.__origine && !b.__origine.isConnected) { b.remove(); if (b === principal) principal = null; }
    const titlu = _normalizeaza((fer.querySelector(".fir-acum") || {}).textContent);
    const faraPrincipal = FARA_ACTIUNE_PRINCIPALA.test(titlu) || _esteMeniu(corp, bara);   // ecran de stare sau meniu de butoane: bara rămâne, fără principal și fără „Renunță”
    if (principal && !principal.isConnected) principal = null;
    // acțiunea de bară care are un original în ecran (găsit de catalog): dacă originalul a dispărut sau nu se mai vede, și butonul din bară pleacă odată cu el
    if (principal && principal.__sursa && (!principal.__sursa.isConnected || !_vizibil(principal.__sursa))) { principal.remove(); principal = null; }
    // [17.5-F, 822] acțiunea mutată din ecran pe care ecranul a ascuns-o (`hidden`) se întoarce la locul ei și bara rămâne liberă pentru acțiunea următoare a ferestrei
    if (principal && !principal.__sursa && (principal.hidden || (principal.__origine && principal.__origine.parentElement && principal.__origine.parentElement.closest("[hidden]")))) {   // [AC182] și când panoul de unde a venit (tabul) s-a ascuns
      const urma = principal.__origine;
      if (urma && urma.isConnected) { principal.classList.remove("fj-principal"); principal.removeAttribute("data-actiune-principala"); principal.__retras = true; urma.after(principal); }
      else principal.remove();
      principal = null;
    }
    // [17.5-H2] PDF-ul de rezervă rămas pe o fereastră fără tabel și fără listă de înregistrări pleacă (portalul „Cifrele firmei” n-are acțiune principală)
    if (principal && principal === corp.__exportPdf && !EXPORT_PDF.test(titlu) && !_tabele(corp).length && !_listaGoala(corp)) { principal.remove(); principal = null; }
    let candidat = faraPrincipal ? null : _alege(corp, bara, principal && principal.__slab ? undefined : !!principal, titlu);
    if (candidat && candidat.__catalog) {
      // [16.8, 760] acțiune găsită de catalog: același nod (id, ascultători) se mută în bară, ca butonul marcat; un singur element vizibil pe ecran. Numai id-urile din
      // NU_MUTA păstrează proxy-ul: originalul rămâne în conținut, ca buton secundar (`fj-are-principal`)
      if (_nuSeMuta(candidat)) candidat = principal && principal.__sursa === candidat ? principal : _proxy(candidat);
    }
    if (principal && principal.__sursa) { principal.textContent = _normalizeaza(principal.__sursa.textContent); principal.disabled = !!principal.__sursa.disabled; principal.title = principal.__sursa.title || ""; }
    if (candidat && candidat !== principal) {
      if (principal) {
        // acțiunea veche nu se aruncă dacă ecranul ei încă există (urma lui e în pagină): se întoarce la locul ei, ca ecranul să-și găsească butonul când revine (ex. „Emite factură” după „Deschide Date firmă”)
        const urma = principal.__origine;
        if (urma && urma.isConnected && !principal.__sursa) { principal.classList.remove("fj-principal"); principal.removeAttribute("data-actiune-principala"); principal.__retras = true; urma.after(principal); }
        else principal.remove();   // ecranul și-a redesenat acțiunea: cea veche rămâne fără rost
      }
      principal = candidat;
      principal.__formular = _formularul(principal.__sursa || candidat);   // înainte de mutare
      if (!principal.__sursa && principal !== corp.__exportPdf) principal.__origine = _urma(candidat);   // [AC183] exportul de rezervă n-are loc de origine în pagină: o urmă pusă lângă un nod detașat n-ar fi niciodată legată, iar curățarea de mai sus l-ar scoate la fiecare cadru;   // locul lui din ecran; dacă ecranul îl redesenează, urma dispare și acțiunea e veche
      principal.classList.add("fj-principal", "buton-primar");   // butonul principal L: clasa piesei, oricum a fost desenat în ecran
      principal.classList.remove("buton-secundar", "buton-s", "buton-xs", "buton-mic");
      principal.setAttribute("data-actiune-principala", "");   // [15.1-E5] pe orice fereastră: exact un buton cu atributul
      loc.appendChild(principal);
    }
    bara.classList.toggle("fj-fara-principal", !principal);
    // fereastra cu formular: acțiunea principală vine dintr-un formular sau fereastra are câmpuri de completat (în afara tabelelor, listelor și căutării)
    const cuFormular = !!principal && (!!principal.__formular || /^Continuă(\s|$)/.test(_normalizeaza(principal.textContent)) || [...corp.querySelectorAll("input:not([type=hidden]):not([type=search]):not([type=checkbox]):not([type=radio]), textarea, select")]
      .some((x) => _vizibil(x) && !x.closest("table, template, .fj-butoane, .fereastra-antet, .ds-lista, [data-fara-piesa]") && !x.classList.contains("alegere-sursa") && !x.classList.contains("ds-lista-sursa")));
    // „Renunță” rămâne numai pe ferestrele din PASTREAZA_RENUNTA: al ecranului (cu efect propriu) ia locul celui al piesei, altfel îl pune piesa (o singură „Renunță” în bară)
    const inLista = PASTREAZA_RENUNTA.includes(titlu);
    const renuntaEcran = inLista ? [...corp.querySelectorAll(".bara-fixa button, form button, #op-renunta")].find((x) => !bara.contains(x) && x.textContent.trim() === "Renunță") : null;
    if (renuntaEcran) {
      const mea = loc.querySelector(".fj-renunta:not(.fj-al-ecranului)");
      if (mea) mea.remove();
      renuntaEcran.__origine = _urma(renuntaEcran);
      renuntaEcran.classList.add("fj-renunta", "fj-al-ecranului");
      loc.prepend(renuntaEcran);
    } else if (cuFormular && inLista) {
      if (!loc.querySelector(".fj-renunta")) loc.prepend(renuntaPiesei());
    } else {
      loc.querySelectorAll(".fj-renunta:not(.fj-al-ecranului)").forEach((x) => x.remove());
    }
    bara.dataset.cuFormular = cuFormular ? "1" : "";
    // zona de mesaje rămasă fără nimic în ea (butoanele au trecut în bară) nu ține loc
    for (const z of corp.querySelectorAll(".bara-fixa")) z.classList.toggle("fj-gol", !z.textContent.trim() && !z.querySelector("button, input, select, textarea, table, img"));
    // ce a pus ecranul lângă butonul principal (motivul butonului inactiv, mesajul unui refuz): nimic altceva în bară — motivul trece în stânga,
    // mesajul deasupra barei, în zona de mesaje
    for (const x of [...loc.children]) {
      if (x === principal || x.classList.contains("fj-renunta")) continue;
      if (/motiv/.test(x.className) || x.hasAttribute("data-motiv-generat")) motiv.appendChild(x);
      else {
        let zona = bara.previousElementSibling;
        if (!zona || !zona.matches(".bara-fixa")) { zona = document.createElement("div"); zona.className = "bara-fixa"; bara.before(zona); }
        zona.appendChild(x);
      }
    }
    // motivul: al ecranului (`.ds-motiv-inactiv` existent, mutat în bară) dacă îl are, altfel al piesei
    for (const m of corp.querySelectorAll(".ds-motiv-inactiv")) if (!bara.contains(m) && !m.classList.contains("fj-text")) motiv.appendChild(m);
    // [17.5-H2] motivul butonului principal inactiv: UN SINGUR text, cu o singură prioritate — (1) al ecranului: `.ds-motiv-inactiv` / `data-motiv-generat` mutat în bară, ori cel
    // dat de `inactiv()` pe buton (`data-motiv-inactiv`); (2) al piesei: „Completează: …” din câmpurile cu „*” ale formularului butonului;
    // (3) exportul de rezervă fără înregistrări; (4) `title` la `disabled`, altfel textul general. Eticheta butonului rămâne verbul acțiunii.
    const exportRezerva = !!principal && principal === corp.__exportPdf && !EXPORT_PDF.test(titlu);
    if (exportRezerva) {
      if (!_tabelCuInregistrari(corp)) inactiv(principal, MOTIV_FARA_INREGISTRARI);
      else if (principal.getAttribute("data-motiv-inactiv") === MOTIV_FARA_INREGISTRARI) activ(principal);
    }
    const lipsa = !principal || !principal.__formular || !principal.__formular.isConnected ? [] : _lipsuri(principal.__formular);
    const sursaB = principal && (principal.__sursa || principal);
    const motivDat = sursaB && sursaB.getAttribute("aria-disabled") === "true" ? (sursaB.getAttribute("data-motiv-inactiv") || sursaB.title || "").trim() : "";
    if (principal) {
      // inactiv = cenușiu, cu motivul în bară (`data-cadru-inactiv`), nu `disabled`: apăsat, butonul arată refuzul întreg al ecranului, cu lista
      // câmpurilor lipsă (scenariile 535, 520, 611 — „trimiterea cu formularul gol arată toate câmpurile lipsă”)
      if (lipsa.length || (motivDat && principal.__sursa)) { principal.dataset.cadruInactiv = "1"; if (!principal.__sursa) principal.setAttribute("aria-describedby", "fj-motiv-text"); }
      else if (principal.dataset.cadruInactiv) { delete principal.dataset.cadruInactiv; principal.removeAttribute("aria-describedby"); }
    }
    for (const m of motiv.querySelectorAll(".ds-motiv-inactiv")) m.classList.toggle("bara-motiv", !!m.textContent.trim());
    const alEcranului = [...motiv.querySelectorAll(".ds-motiv-inactiv:not(.fj-text), [data-motiv-generat]")].some((m) => m.textContent.trim());
    let text = "";
    if (alEcranului) text = "";
    else if (motivDat) text = motivDat;
    else if (lipsa.length) text = "Completează: " + (lipsa.length > 4 ? `${lipsa.slice(0, 3).join(", ")} și încă ${cate(lipsa.length - 3, "câmp", "câmpuri")}` : lipsa.join(", "));
    else if (principal && principal.disabled) {
      // motivul pus de ecran pe buton (`title`), dacă nu e deja scris în fereastră (același mesaj o singură dată pe ecran); altfel cel general
      const dinEcran = principal.title || principal.getAttribute("aria-description") || "";
      const scrisDeja = dinEcran && [...corp.children].some((x) => x !== bara && !x.contains(principal) && (x.innerText || "").includes(dinEcran));
      text = dinEcran && !scrisDeja ? dinEcran : "Completează datele cerute în fereastră, ca să poți continua.";
    }
    let sp = motiv.querySelector(".fj-text");
    if (text) {
      if (!sp) { sp = document.createElement("span"); sp.className = "fj-text ds-motiv-inactiv bara-motiv"; sp.id = "fj-motiv-text"; motiv.prepend(sp); }
      if (sp.textContent !== text) sp.textContent = text;
    } else if (sp) sp.remove();
    bara.classList.toggle("fj-inactiv", !!principal && (!!principal.disabled || !!principal.dataset.cadruInactiv || principal.getAttribute("aria-disabled") === "true"));
    corp.classList.toggle("fj-are-principal", !!principal);   // [15.1-E3] fereastra are acțiunea principală în bară: restul butoanelor principale din conținut arată ca secundare (CSS)
  }

  let plan = 0;
  const programeaza = () => { if (!plan) plan = requestAnimationFrame(() => { plan = 0; sincronizeaza(); }); };
  corp.addEventListener("input", programeaza, true);
  corp.addEventListener("change", programeaza, true);
  new MutationObserver((muts) => { if (muts.some((m) => !bara.contains(m.target) || m.target === bara || m.target === loc)) programeaza(); })
    .observe(corp, { childList: true, subtree: true, attributes: true, attributeFilter: ["disabled", "hidden", "class", "style", "open", "aria-disabled", "data-motiv-inactiv"] });
  sincronizeaza();
  return { sincronizeaza, bara };
}
