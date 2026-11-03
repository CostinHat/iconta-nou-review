// cadru.js — BARA DE JOS a ferestrei de lucru (comanda 15.1-E2, pct.3; DS ferestre și tabele, secțiunea 1): o singură piesă, chemată de navigator
// la fiecare fereastră de lucru; ecranele nu o desenează.
//
//   72 px, fixă, mereu vizibilă, ultimul copil al corpului ferestrei; acțiunea principală L (52 px) în dreapta, „Renunță” M lângă ea; un singur
//   buton principal; nimic altceva în bară. Motivul butonului inactiv (729) stă în stânga, în bară. Mesajele de refuz și de eroare ale acțiunii
//   (`.bara-fixa`, rezumatul totalurilor) rămân DEASUPRA barei, fără derulare.
//
// Acțiunea principală a ecranului, în ordine: (1) elementul marcat `data-actiune-principala`; (2) butonul principal din `.bara-fixa` (ultimul);
// (3) butonul principal al unui formular (`form`, `.ds-formular`, `.pf-frand`), ultimul. Același element, nu o copie: identificatorul,
// ascultătorii și testele ecranului rămân neschimbate; el se mută în bară. Fereastra fără acțiune proprie (listă, raport) are „Închide” ca
// acțiune principală. „Renunță” întoarce un pas, ca „←” (sau închide, la prima fereastră).
//
// Starea o dă piesa: câmpurile obligatorii ale ecranului sunt etichetele cu „*”; cât un câmp vizibil de acest fel e gol, butonul principal e
// inactiv, cu motivul „Completează: …” în bară. Ecranul spune doar ce e obligatoriu; el nu-și mai ține butonul activ / inactiv.

import { alegereButoane } from "./api.js?v=83fcf3ce06";
import { listaCuCautare, tabeleDSAplica, carduriDSAplica, listeDSAplica } from "./ds_piese.js?v=6c53e28e8f";

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

// câmpurile obligatorii (etichete cu „*”) goale și vizibile, în ordinea din ecran
function _lipsuri(corp) {
  const out = [];
  for (const et of corp.querySelectorAll("label, .camp-eticheta")) {
    if (!/\*/.test(et.textContent) || !_vizibil(et)) continue;
    const c = _controlEtichetei(et);
    if (!c || c.disabled || c.readOnly || !_vizibil(c)) continue;
    if (c.type === "checkbox" || c.type === "radio") continue;
    if (String(c.value || "").trim() === "") out.push(_normalizeaza(et.textContent.replace(c.textContent || "", "")) || "câmp obligatoriu");
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
    if (sel.__lista || sel.__butoane || sel.multiple || !_vizibil(sel) || sel.closest("table, .fereastra-antet, .cautare-globala, [data-fara-piesa], template")) continue;
    if (sel.classList.contains("ds-lista-sursa") || sel.classList.contains("alegere-sursa")) continue;
    const reale = [...sel.options].filter((o) => !o.hasAttribute("data-alege") && o.value !== "" && !o.hidden);
    if (!reale.length) continue;
    const lung = reale.some((o) => (o.dataset.buton || o.textContent || "").trim().length > 28);
    if (reale.length > 6 || lung) listaCuCautare(sel, { gol: "Alege din listă", cautare: "Caută în listă…" });
    else alegereButoane(sel);
  }
}

// [15.1-E3] explicația de sub un câmp (`.camp-ajutor`) stă pe un rând, cu textul întreg în `title`; câmpul focusat o arată întreagă (CSS) — nu paragrafe lungi în formular
function _ajutoareScurte(corp) {
  for (const a of corp.querySelectorAll(".camp-ajutor")) if (!a.title && a.textContent.trim()) a.title = a.textContent.trim();
}

function _alege(corp, bara) {
  const marcat = [...corp.querySelectorAll("[data-actiune-principala]")].filter((b) => !bara.contains(b)).pop();
  if (marcat) return marcat;
  const fixe = [...corp.querySelectorAll(".bara-fixa .buton-primar")].filter((b) => b.tagName === "BUTTON");
  if (fixe.length) return fixe[fixe.length - 1];
  const eligibil = (b) => b.tagName === "BUTTON" && !bara.contains(b) && !b.closest("table, template, details, .tn-actiuni, .rezumat-fix");
  const formular = [...corp.querySelectorAll("form .buton-primar, .ds-formular ~ * .buton-primar, .pf-frand:has(> .ds-formular) .buton-primar")].filter(eligibil);
  if (formular.length) return formular[formular.length - 1];
  return null;
}

// o urmă (comentariu) lăsată în locul din care butonul trece în bară: dispare odată cu zona pe care ecranul o redesenează
function _urma(b) { const u = document.createComment("fj"); b.before(u); return u; }

// containerul de formular din care vine butonul: numai câmpurile lui hotărăsc dacă butonul e inactiv (nu etichetele altor părți ale ferestrei)
const _formularul = (b) => b.closest("form, .ds-formular, .pf-frand:has(> .ds-formular)");

/** Pune bara de jos pe fereastra `fer`; întoarce `{ sincronizeaza, inchide }`. `renunta` = ce face „Renunță” (un pas înapoi / închide). */
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
  let principal = null, inchide = null;

  const _actiuneImplicita = () => {   // fereastra fără acțiune proprie
    if (!inchide) {
      inchide = document.createElement("button");
      inchide.type = "button"; inchide.className = "buton-primar fj-principal fj-inchide"; inchide.textContent = "Închide";
      inchide.addEventListener("click", () => renunta());
    }
    return inchide;
  };

  function sincronizeaza() {
    if (!corp.isConnected) return;
    _marcheazaObligatorii(corp);
    _ajutoareScurte(corp);
    _listeDerulante(corp);
    listeDSAplica(corp);   // [15.1-E4] lista de înregistrări → tabelul DS
    tabeleDSAplica(corp);   // [15.1-E4] tabelul DS, o singură dată pentru toate ecranele
    carduriDSAplica(corp);   // [15.1-E4] cardul-rezumat, o singură dată pentru toate ecranele
    if (bara.parentElement !== corp || corp.lastElementChild !== bara) corp.appendChild(bara);
    // acțiunea al cărei loc de origine (zona ecranului) a fost redesenat de ecran e veche: ecranul a scos-o odată cu zona (ex. „Scrie nota” după scriere)
    for (const b of [...loc.children]) if (b.__origine && !b.__origine.isConnected) { b.remove(); if (b === principal) principal = null; }
    const candidat = _alege(corp, bara);
    if (candidat && candidat !== principal) {
      if (principal && principal !== inchide) principal.remove();   // ecranul și-a redesenat acțiunea: cea veche rămâne fără rost
      if (inchide) inchide.remove();
      principal = candidat;
      principal.__formular = _formularul(candidat);   // înainte de mutare
      principal.__origine = _urma(candidat);   // locul lui din ecran; dacă ecranul îl redesenează, urma dispare și acțiunea e veche
      principal.classList.add("fj-principal");
      loc.appendChild(principal);
    } else if (!candidat && (!principal || !principal.isConnected || principal === inchide)) {
      principal = _actiuneImplicita();
      if (!principal.isConnected) loc.appendChild(principal);
    }
    if (principal === inchide) {   // „Închide” e acțiunea principală numai dacă fereastra n-are alta: un singur buton principal pe fereastră
      const alta = [...corp.querySelectorAll(".buton-primar")].some((x) => !bara.contains(x) && _vizibil(x) && !x.closest("template, details"));
      inchide.classList.toggle("buton-primar", !alta); inchide.classList.toggle("buton-secundar", alta);
    } else if (principal && !principal.isConnected) {
      principal = null;
      sincronizeaza();
      return;
    }
    // „Renunță” al ecranului (de lângă butonul principal, resetează formularul lui) ia locul celui al piesei: o singură „Renunță” în bară
    const renuntaEcran = [...corp.querySelectorAll(".bara-fixa button, form button")].find((x) => !bara.contains(x) && x.textContent.trim() === "Renunță");
    if (renuntaEcran) {
      const mea = loc.querySelector(".fj-renunta:not(.fj-al-ecranului)");
      if (mea) mea.remove();
      renuntaEcran.__origine = _urma(renuntaEcran);
      renuntaEcran.classList.add("fj-renunta", "fj-al-ecranului");
      loc.prepend(renuntaEcran);
    } else if (!loc.querySelector(".fj-renunta")) {
      loc.prepend(renuntaPiesei());
    }
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
    const lipsa = principal === inchide || !principal.__formular || !principal.__formular.isConnected ? [] : _lipsuri(principal.__formular);
    if (principal !== inchide) {
      // inactiv = cenușiu, cu motivul în bară (`data-cadru-inactiv`), nu `disabled`: apăsat, butonul arată refuzul întreg al ecranului, cu lista
      // câmpurilor lipsă (scenariile 535, 520, 611 — „trimiterea cu formularul gol arată toate câmpurile lipsă”)
      if (lipsa.length) { principal.dataset.cadruInactiv = "1"; principal.setAttribute("aria-describedby", "fj-motiv-text"); }
      else if (principal.dataset.cadruInactiv) { delete principal.dataset.cadruInactiv; principal.removeAttribute("aria-describedby"); }
    }
    for (const m of motiv.querySelectorAll(".ds-motiv-inactiv")) m.classList.toggle("bara-motiv", !!m.textContent.trim());
    const alEcranului = [...motiv.querySelectorAll(".ds-motiv-inactiv:not(.fj-text)")].some((m) => m.textContent.trim());
    let text = "";
    if (lipsa.length) text = "Completează: " + lipsa.join(", ");
    else if (principal.disabled && !alEcranului) {
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
    bara.classList.toggle("fj-inactiv", !!principal.disabled || !!principal.dataset.cadruInactiv);
    corp.classList.toggle("fj-are-principal", principal !== inchide);   // [15.1-E3] fereastra are acțiunea principală în bară: restul butoanelor principale din conținut arată ca secundare (CSS)
  }

  let plan = 0;
  const programeaza = () => { if (!plan) plan = requestAnimationFrame(() => { plan = 0; sincronizeaza(); }); };
  corp.addEventListener("input", programeaza, true);
  corp.addEventListener("change", programeaza, true);
  new MutationObserver((muts) => { if (muts.some((m) => !bara.contains(m.target) || m.target === bara || m.target === loc)) programeaza(); })
    .observe(corp, { childList: true, subtree: true, attributes: true, attributeFilter: ["disabled", "hidden", "class", "style", "open"] });
  sincronizeaza();
  return { sincronizeaza, bara };
}
