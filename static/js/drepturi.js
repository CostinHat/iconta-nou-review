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
import { api } from "./api.js?v=72aa1cbbdb";

let _refuzate = new Set();
let _motive = {};          // „METODĂ /cale” -> nivelul refuzat (poate_pregati / poate_valida / poate_depune / admin_cabinet / rol)
let _numeNiveluri = {};    // nivel -> numele de pe ecranul Asistenți
let _bife = {};            // [265] bifele asistentului de la ultima citire (la administrator: niciuna)

function _pune(r) {
  _refuzate = new Set((r && r.interzise) || []);
  _motive = (r && r.motive) || {};
  _numeNiveluri = (r && r.nume_niveluri) || {};
  _bife = (r && r.bife) || {};
}

function _amprenta() {
  return JSON.stringify([[..._refuzate].sort(), Object.keys(_bife).sort().map((k) => [k, !!_bife[k]])]);
}

export async function incarcaDrepturi() {
  try {
    _pune(await api.get("/eu/drepturi"));
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
  // un mesaj al ecranului (`.drept-motiv` fără `-generic`) apărut DUPĂ notă o înlocuiește: un singur motiv pe zonă
  const specifice = [...radacina.querySelectorAll(".drept-motiv:not(.drept-motiv-generic)")];
  if (radacina.matches && radacina.matches(".drept-motiv:not(.drept-motiv-generic)")) specifice.push(radacina);
  specifice.forEach((m) => {
    const z = m.closest(ZONA_MOTIV);
    if (z) z.querySelectorAll(".drept-motiv-generic").forEach((g) => g.remove());
  });
  const elemente = [...radacina.querySelectorAll("[data-actiune]")];
  if (radacina.matches && radacina.matches("[data-actiune]")) elemente.push(radacina);
  const zone = new Set();
  elemente.forEach((el) => {
    if (permis(el.dataset.actiune)) return;
    refuza(el);
    const z = el.closest(ZONA_MOTIV);
    if (z) zone.add(z);
  });
  zone.forEach(motivInZona);
  const campuri = [...radacina.querySelectorAll("[data-actiune-camp]")];
  if (radacina.matches && radacina.matches("[data-actiune-camp]")) campuri.push(radacina);
  campuri.forEach((el) => {
    if (!permis(el.dataset.actiuneCamp) && !el.disabled) {
      el.disabled = true;
      el.setAttribute("aria-disabled", "true");
      el.dataset.dreptCampDezactivat = "1";   // [265] ca acordarea dreptului să-l reactiveze, și numai pe el
    }
  });
}

// [comanda Costin 05.10.2026 pct.3] „Când acțiunile lipsesc din cauza drepturilor, afișează motivul («cere dreptul «…»; îl
// acordă administratorul din Asistenți»)”. Instanța: asistentul fără „Poate pregăti” vedea fereastra poveștii fără niciun buton
// și fără nicio explicație. Poarta ȘTIE ce a ascuns și de ce (nivelul vine de la server), deci motivul îl pune ea, o singură
// dată pe zonă — nu fiecare ecran în parte (un ecran nou ar fi uitat). Zona: fereastra din navigator, overlay-ul poveștii sau
// un element marcat `data-zona-drepturi`. Un mesaj scris de ecran pentru aceeași situație poartă clasa `drept-motiv` și o
// înlocuiește pe asta (nu se dublează). DS cap.9; gard `core/test_drepturi_ui.py`.
const ZONA_MOTIV = ".pacm, .fereastra-corp, [data-zona-drepturi]";

export function textMotiv(niveluri, oriceVizibil) {
  const drepturi = [...niveluri].filter((n) => _numeNiveluri[n]).map((n) => "«" + _numeNiveluri[n] + "»");
  const doarAdmin = [...niveluri].some((n) => !_numeNiveluri[n]);
  const inceput = oriceVizibil ? "Unele acțiuni de aici nu se afișează" : "Acțiunile de aici nu se afișează";
  const parti = [];
  if (drepturi.length) {
    parti.push(inceput + ": " + (drepturi.length === 1
      ? "cer dreptul " + drepturi[0] + ", pe care nu-l ai. Îl acordă administratorul cabinetului, din ecranul Asistenți."
      : "cer drepturile " + drepturi.join(" și ") + ", pe care nu le ai. Le acordă administratorul cabinetului, din ecranul Asistenți."));
  }
  if (doarAdmin) parti.push((drepturi.length ? "Altele" : inceput + ":") + " le face doar administratorul cabinetului.");
  return parti.join(" ");
}

function motivInZona(zona) {
  if (zona.querySelector(".drept-motiv")) return;   // generică deja pusă, sau mesajul ecranului pentru aceeași situație
  const niveluri = new Set();
  zona.querySelectorAll(".drept-refuzat[data-actiune]").forEach((el) => {
    String(el.dataset.actiune).split("|").map((a) => a.trim()).filter((a) => _refuzate.has(a))
      .forEach((a) => niveluri.add(_motive[a] || "rol"));
  });
  if (!niveluri.size) return;
  const oriceVizibil = [...zona.querySelectorAll("[data-actiune]")].some((el) => !el.classList.contains("drept-refuzat"));
  const p = document.createElement("p");
  p.className = "ecran-nota drept-motiv drept-motiv-generic";
  p.setAttribute("role", "note");
  p.textContent = textMotiv(niveluri, oriceVizibil);
  const bara = zona.querySelector(":scope .pacm-bara");
  if (bara) bara.before(p); else zona.prepend(p);
}

function refuza(el) {
  el.classList.add("drept-refuzat");
  el.inert = true;
  // [265] numai ce dezactivează poarta se reactivează la acordarea dreptului: un buton dezactivat de ecran (nimic selectat) rămâne așa
  if ("disabled" in el && !el.disabled) { el.disabled = true; el.dataset.dreptDezactivat = "1"; }
}

// [deficiența 265, comanda Costin 15.10.2026] „o schimbare de drepturi nu se vede în sesiunea deschisă până la re-autentificare (Ana
// a rămas «junior» după ce a primit «Poate valida»; după retragere, butonul «Validează» a rămas afișat, deși serverul refuză corect).
// Ecranul urmează drepturile fără re-autentificare.” Poarta lua lista o singură dată, la intrare, și nu știa decât să ascundă. Acum
// lista se recitește pe ceasul aplicației (versiune.js: la cinci minute, la revenirea în filă, la întoarcerea acasă — navigator.js), iar
// dacă s-a schimbat, poarta se REAPLICĂ pe toată pagina: ascunde ce nu mai e permis și arată la loc ce a devenit permis, cu motivele
// din ferestre refăcute. Ecranul deschis nu se redesenează (nu se pierde nimic din el). O citire eșuată nu schimbă nimic.
// Întoarce bifele noi (navigatorul le pune în sesiune, cu eticheta senior/junior), sau null dacă nu s-a schimbat nimic.
export async function reimprospateazaDrepturi() {
  let r;
  try {
    r = await api.get("/eu/drepturi");
  } catch (e) {
    console.warn("drepturi: recitirea n-a reușit; rămân cele de până acum", e);
    return null;
  }
  const inainte = _amprenta();
  _pune(r);
  if (_amprenta() === inainte) return null;
  reaplicaDrepturi(document.body);
  // [265] ecranele deschise care își calculează textele la desenare (jurnalul, coada) se redesenează la acest semnal
  window.dispatchEvent(new CustomEvent("iconta:drepturi"));
  return { bife: Object.assign({}, _bife) };
}

/** [265] Poarta, din nou, pe tot ce e sub `radacina`: întâi elibereaza tot ce ascunsese ea, apoi aplică lista de acum. */
export function reaplicaDrepturi(radacina) {
  radacina.querySelectorAll(".drept-motiv-generic").forEach((m) => m.remove());
  radacina.querySelectorAll(".drept-refuzat").forEach((el) => {
    el.classList.remove("drept-refuzat");
    el.inert = false;
    if (el.dataset.dreptDezactivat) { el.disabled = false; delete el.dataset.dreptDezactivat; }
  });
  radacina.querySelectorAll("[data-drept-camp-dezactivat]").forEach((el) => {
    el.disabled = false;
    el.removeAttribute("aria-disabled");
    delete el.dataset.dreptCampDezactivat;
  });
  aplicaDrepturi(radacina);
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
