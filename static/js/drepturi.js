// drepturi.js — interfața urmează serverul (decizia Costin 04.10.2026, varianta 2).
//
// Serverul spune ce acțiuni îi refuză utilizatorului (`GET /eu/drepturi`, derivat din gărzile rutelor —
// `core/drepturi.py`). Interfața NU știe niciun nivel și nicio regulă: scoate din pagină orice element
// marcat `data-actiune="METODĂ /cale"` (șablonul rutei, exact ca în main.py) aflat în lista refuzată.
// Mai multe acțiuni pe același element se despart cu `|`; elementul iese doar dacă TOATE sunt refuzate
// (un card care deschide un ecran cu acțiuni mixte rămâne cât timp măcar una e permisă).
//
// Un CÂMP care arată și o valoare (celula de pontaj, de pildă) poartă `data-actiune-camp`: la refuz se
// DEZACTIVEAZĂ, nu se scoate — valoarea rămâne de citit, doar nu se mai poate schimba.
//
// CUM se ascunde: clasa `drept-refuzat` (`display: none !important` în stil.css) + `inert` + `disabled`. Nu
// `hidden` simplu — o regulă CSS cu `display` îl răstoarnă; nu un stil doar vizual — butonul ar rămâne în ordinea
// de tabulare. Și NU `remove()`: poarta rulează ca microtask, DUPĂ codul care a randat ecranul, iar un ecran care
// își caută butonul după un `await` ar primi `null` și s-ar rupe. Elementul rămâne în DOM, dar nu se vede, nu
// primește focus și nu se poate apăsa (`display: none` îl scoate și din arborele de accesibilitate).
//
// Garda statică: `core/test_drepturi_ui.py` — orice fișier care cheamă o rută restrânsă își declară
// marcajul (scanerul `scripts/scan_drepturi_ui.py`).
import { api } from "./api.js?v=91e1c0701a";

let _refuzate = new Set();

export async function incarcaDrepturi() {
  try {
    const r = await api.get("/eu/drepturi");
    _refuzate = new Set((r && r.interzise) || []);
  } catch (e) {
    // Fără listă nu se ascunde nimic: serverul rămâne garda, iar refuzul lui se vede (pct.1 al comenzii).
    _refuzate = new Set();
    console.warn("drepturi: lista nu s-a putut încărca", e);
  }
  return _refuzate;
}

export function permis(actiune) {
  const lista = String(actiune || "").split("|").map((a) => a.trim()).filter(Boolean);
  return !lista.length || lista.some((a) => !_refuzate.has(a));
}

export function aplicaDrepturi(radacina) {
  if (!_refuzate.size || !radacina || !radacina.querySelectorAll) return;
  const elemente = [...radacina.querySelectorAll("[data-actiune]")];
  if (radacina.matches && radacina.matches("[data-actiune]")) elemente.push(radacina);
  elemente.forEach((el) => { if (!permis(el.dataset.actiune)) refuza(el); });
  const campuri = [...radacina.querySelectorAll("[data-actiune-camp]")];
  if (radacina.matches && radacina.matches("[data-actiune-camp]")) campuri.push(radacina);
  campuri.forEach((el) => {
    if (!permis(el.dataset.actiuneCamp)) { el.disabled = true; el.setAttribute("aria-disabled", "true"); }
  });
}

function refuza(el) {
  el.classList.add("drept-refuzat");
  el.inert = true;
  if ("disabled" in el) el.disabled = true;
}

let _observator = null;
export function pornestePoarta() {
  if (_observator) return;
  aplicaDrepturi(document.body);
  _observator = new MutationObserver((schimbari) => {
    for (const s of schimbari) s.addedNodes.forEach((n) => { if (n.nodeType === 1) aplicaDrepturi(n); });
  });
  _observator.observe(document.body, { childList: true, subtree: true });
}
