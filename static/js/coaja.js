// coaja.js — CONTRACTUL dintre ASPECTE (proprietari de spatiu) si CHIRIASI (ocupanti).
// DESIGN_SYSTEM cap.25, 21.08.2026.
//
// DE CE EXISTA. Pana azi, un ecran isi lipea elementul in bara de stare cu
// `document.querySelector(".subbara").appendChild(...)` — adica un chirias isi lua singur spatiu din
// coaja. Doua consecinte, amandoua traite: bara de stare nu-si mai controla propriul continut (de-aici
// „indicatorul mincinos" de pe 20.08, unde subbara si un card de pe acelasi ecran spuneau lucruri
// diferite despre acelasi fapt), si nu se putea schimba coaja fara sa cauti prin ecrane cine mai scrie
// in ea.
//
// CONTRACTUL, in doua propozitii (DS cap.25):
//   1. Proprietarul NU interpreteaza ce spune chiriasul — primeste un nod, nu un mesaj.
//   2. Chiriasul NU se atinge de spatiu care nu e al lui — CERE un loc, nu si-l ia.
//
// DE CE MODUL SEPARAT si nu o functie in navigator: `navigator.js` importa `ecrane/ansamblu.js`, deci
// un import invers din ecrane ar inchide un ciclu. Contractul nu apartine niciunei parti — sta intre ele.
//
// LOCUL POATE LIPSI, si asta e normal: bara de stare nu exista la rolul `client`. `cereLoc` intoarce
// null, iar chiriasul trebuie sa suporte asta — exact ca inainte, cand `querySelector` intorcea null.

const locuri = new Map();

/** Proprietarul isi declara un loc inchiriabil. Numit, nu dedus dintr-un selector. */
export function inregistreazaLoc(nume, nod) {
  if (nod) locuri.set(nume, nod);
}

/** Proprietarul isi retrage locurile (la re-randarea cojii), ca sa nu ramana noduri moarte. */
export function uitaLocurile() {
  locuri.clear();
}

/** Chiriasul intreaba daca locul exista. Poate lipsi — vezi rolul `client`. */
export function cereLoc(nume) {
  return locuri.get(nume) || null;
}

/**
 * Chiriasul cere sa i se puna un nod in loc. `id` e identitatea chiriasului acolo: a doua chemare cu
 * acelasi id NU dubleaza, inlocuieste. Intoarce true daca a incaput, false daca locul nu exista.
 * Idempotenta e ceruta de realitate: ecranele se re-randeaza, iar inainte fiecare apelant isi facea
 * singur verificarea `if (bara.querySelector("#id")) return;`.
 */
export function pune(nume, id, nod) {
  const loc = cereLoc(nume);
  if (!loc || !nod) return false;
  const vechi = loc.querySelector("#" + CSS.escape(id));
  nod.id = id;
  if (vechi) vechi.replaceWith(nod); else loc.appendChild(nod);
  return true;
}

/** Chiriasul pleaca. Fara efect daca nu era acolo. */
export function scoate(nume, id) {
  const loc = cereLoc(nume);
  const el = loc && loc.querySelector("#" + CSS.escape(id));
  if (el) el.remove();
  return !!el;
}

// Numele locurilor — nomenclator INCHIS, ca sa nu apara „locuri" inventate prin siruri ad-hoc.
export const LOCURI = {
  BARA_DE_STARE: "bara-de-stare",
};
