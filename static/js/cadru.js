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

function _alege(corp, bara) {
  const marcat = [...corp.querySelectorAll("[data-actiune-principala]")].filter((b) => !bara.contains(b)).pop();
  if (marcat) return marcat;
  const fixe = [...corp.querySelectorAll(".bara-fixa .buton-primar")].filter((b) => b.tagName === "BUTTON");
  if (fixe.length) return fixe[fixe.length - 1];
  const formular = [...corp.querySelectorAll("form .buton-primar, .ds-formular ~ * .buton-primar, .pf-frand .buton-primar")]
    .filter((b) => b.tagName === "BUTTON" && !bara.contains(b) && !b.closest("table, template, details, .tn-actiuni"));
  return formular.length ? formular[formular.length - 1] : null;
}

/** Pune bara de jos pe fereastra `fer`; întoarce `{ sincronizeaza, inchide }`. `renunta` = ce face „Renunță” (un pas înapoi / închide). */
export function baraDeJos(fer, corp, { renunta }) {
  const bara = document.createElement("div");
  bara.className = "fereastra-jos";
  bara.innerHTML = `<span class="fj-motiv" aria-live="polite"></span><span class="fj-butoane"><button type="button" class="buton-secundar fj-renunta">Renunță</button></span>`;
  const loc = bara.querySelector(".fj-butoane");
  const motiv = bara.querySelector(".fj-motiv");
  bara.querySelector(".fj-renunta").addEventListener("click", () => renunta());
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
    if (bara.parentElement !== corp || corp.lastElementChild !== bara) corp.appendChild(bara);
    const candidat = _alege(corp, bara);
    if (candidat && candidat !== principal) {
      if (principal && principal !== inchide) principal.remove();   // ecranul și-a redesenat acțiunea: cea veche rămâne fără rost
      if (inchide) inchide.remove();
      principal = candidat;
      principal.classList.add("fj-principal");
      loc.appendChild(principal);
    } else if (!candidat && (!principal || !principal.isConnected || principal === inchide)) {
      principal = _actiuneImplicita();
      if (!principal.isConnected) loc.appendChild(principal);
    } else if (principal && !principal.isConnected) {
      principal = null;
      sincronizeaza();
      return;
    }
    // motivul: al ecranului (`.ds-motiv-inactiv` existent, mutat în bară) dacă îl are, altfel al piesei
    for (const m of corp.querySelectorAll(".ds-motiv-inactiv")) if (!bara.contains(m) && !m.classList.contains("fj-text")) motiv.appendChild(m);
    const lipsa = principal === inchide ? [] : _lipsuri(corp);
    if (principal !== inchide) {
      if (lipsa.length) { principal.disabled = true; principal.dataset.cadruInactiv = "1"; }
      else if (principal.dataset.cadruInactiv) { principal.disabled = false; delete principal.dataset.cadruInactiv; }
    }
    for (const m of motiv.querySelectorAll(".ds-motiv-inactiv")) m.classList.toggle("bara-motiv", !!m.textContent.trim());
    const alEcranului = [...motiv.querySelectorAll(".ds-motiv-inactiv:not(.fj-text)")].some((m) => m.textContent.trim());
    let text = "";
    if (lipsa.length) text = "Completează: " + lipsa.join(", ");
    else if (principal.disabled && !alEcranului) text = principal.title || principal.getAttribute("aria-description") || "Completează datele cerute în fereastră, ca să poți continua.";
    let sp = motiv.querySelector(".fj-text");
    if (text) {
      if (!sp) { sp = document.createElement("span"); sp.className = "fj-text ds-motiv-inactiv bara-motiv"; motiv.prepend(sp); }
      if (sp.textContent !== text) sp.textContent = text;
    } else if (sp) sp.remove();
    bara.classList.toggle("fj-inactiv", !!principal.disabled);
  }

  let plan = 0;
  const programeaza = () => { if (!plan) plan = requestAnimationFrame(() => { plan = 0; sincronizeaza(); }); };
  corp.addEventListener("input", programeaza, true);
  corp.addEventListener("change", programeaza, true);
  new MutationObserver((muts) => { if (muts.some((m) => !bara.contains(m.target) || m.target === bara)) programeaza(); })
    .observe(corp, { childList: true, subtree: true, attributes: true, attributeFilter: ["disabled", "hidden", "class", "style"] });
  sincronizeaza();
  return { sincronizeaza, bara };
}
