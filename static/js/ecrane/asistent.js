// asistent.js — desktopul asistentului: ecran de lucru ca al cabinetului,
// minus exclusivele cabinetului. Bara 3 = doar motivational (pozitiv).
// Sursa unica: identitatea/permisiunile din sesiune.user(); cifrele din /eu/calitate.
//
// [deficiența 231, comanda Costin 12.10.2026, verbatim în DECIZII] „la Ana, scoate meniul din stânga care repetă cardurile. Pagina
// principală are aceeași structură la ambele roluri.” PIVOT pe [p90_arbore 06.09.2026] (arborele de navigare din stânga): banda de
// sus și benzile „Recomandă” / „Suport” vin din salut.js, ca la cabinet; dedesubt, numai grila de carduri.

import { VERDICT_POZITIV } from "./verdict.js?v=59fd410a82";  // [P13c] punctul unic de verdict
import { api, ICOANE, CULORI_CARD } from "../api.js?v=e38843b1ec";
import { semaforCardControl } from "./semafor.js?v=60f4db5322";  // [p87_asistent] [224]
import { sesiune } from "../sesiune.js?v=898215e0ee";
import { randeazaControl } from "./control.js?v=680bf7a6fb";
import { randeazaTermene } from "./termene.js?v=74c373edbf";
import { randeazaValidat } from "./validat.js?v=058e9d8957";
import { randeazaListaFirme } from "./firme.js?v=4c2b4e3117";
import { paginaPrincipala, legaBenzile } from "./salut.js?v=f5a3ed7133"; // [225 + 231] banda de sus, aceeași la ambele roluri
import { randeazaPachete } from "./pachete.js?v=9228e3b2d1"; // [p63_pachete]
import { randeazaDeclaratii } from "./declaratii.js?v=cb3b13150a"; // [p44_declaratii]
import { randeazaSetari } from "./setari.js?v=08abddba63"; // [p28_setari] acces asistent: Date profil + Schimba parola (gating existent setari.js:8-19)

function svg(nume, culoare) {
  return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="${culoare}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICOANE[nume] || ""}</svg>`;
}

// ── CARDURILE, unul per functionalitate; `deschide` e destinatia lui.
const NODURI = {
  firme: { titlu: "Firme", icon: "building", ...CULORI_CARD.albastru,
    sinteza: "Firmele tale alocate",
    deschide: (nav) => nav.deschide("Firme", (corp) => randeazaListaFirme(corp, nav, () => nav.inapoi())) },
  control: { titlu: "Control fiscal", icon: "shield", ...CULORI_CARD.teal,
    sinteza: "Starea fiscală a firmelor tale",
    deschide: (nav) => nav.deschide("Control fiscal", (corp) => randeazaControl(corp, nav)) },
  termene: { titlu: "Termene", icon: "calendar", ...CULORI_CARD.verde,
    sinteza: "Scadențele firmelor tale",
    deschide: (nav) => nav.deschide("Termene", (corp) => randeazaTermene(corp, nav)) },
  declaratii: { titlu: "Declarații", icon: "declaratii", ...CULORI_CARD.albastru,
    sinteza: "Pregătește și trimite la validare", cere: "poate_pregati",
    deschide: (nav) => nav.deschide("Declarații", (corp) => randeazaDeclaratii(corp, nav), { lat: "tabel" }) },   // [08.10, W5]
  validat: { titlu: "De validat", icon: "clipboard", ...CULORI_CARD.piersica,
    sinteza: "Declarații și note de validat de la colegi", cere: "poate_valida",
    deschide: (nav) => nav.deschide("De validat", (corp) => randeazaValidat(corp, nav, { titlu: "De validat" })) },   // [292] titlul cardului
  pachete: { titlu: "Pachete lunare", icon: "mail", ...CULORI_CARD.violet,
    sinteza: "Trimite pachetul lunar către clienți",
    deschide: (nav) => nav.deschide("Pachete lunare", (corp) => randeazaPachete(corp, nav)) },
  setari: { titlu: "Setări cont", icon: "settings", ...CULORI_CARD.ardezie,
    sinteza: "Parolă și date de profil",
    deschide: (nav) => nav.deschide("Setări cont", (corp) => randeazaSetari(corp, nav)) },
};

// ── ORDINEA, si de ce e asta. Criteriul e fluxul de lucru al asistentului: ce se face ZILNIC
// inaintea a ce se face lunar sau trimestrial, si ce e de baza inaintea a ce e administrativ.
//
// Grupele NU sunt o taxonomie noua - sunt cardurile de azi, citite dupa ce raspund:
// starea firmelor · productia lunii · contul meu.
//
// „Firme" e primul fiindca lucrul zilnic (facturare, note, casa) traieste INAUNTRUL unei firme
// si se ajunge la el numai pe aici; pe ecranul asta, „zilnic" inseamna „Firme".
const SECTIUNI = [
  // zilnic: ce lucrez, ce arde azi, ce vine
  { titlu: "Firmele mele", noduri: ["firme", "control", "termene"] },
  // lunar/trimestrial, in ordinea actului: pregatesc -> verific -> livrez
  { titlu: "Lucrarea lunii", noduri: ["declaratii", "validat", "pachete"] },
  // ocazional si administrativ, la urma („Suport” și „Recomandă” sunt benzile de sus — deficiența 225)
  { titlu: "Contul meu", noduri: ["setari"] },
];

// Cheile pe care le are DREPTUL sa vada utilizatorul, in ordinea sectiunilor.
export function cheiPermise(u) {
  const are = (n) => !n.cere || !!(u || {})[n.cere];
  return SECTIUNI.map((s) => ({
    titlu: s.titlu,
    noduri: s.noduri.filter((k) => NODURI[k] && are(NODURI[k])),
  })).filter((s) => s.noduri.length);
}

export async function desktopAsistent(continut, nav) {
  const u = sesiune.user() || {};

  // [p25_bara3] bara 3 e in navigator acum, nu aici

  const sectiuni = cheiPermise(u);

  continut.innerHTML = paginaPrincipala(u);   // [269] numele din salut: `numeDeSalut` (salut.js)
  legaBenzile(continut, nav);
  const grila = continut.querySelector(".cab-grila");
  // Cardurile, in ordinea sectiunilor (fluxul de lucru al asistentului)
  sectiuni.forEach((s) => s.noduri.forEach((k) => {
    const c = NODURI[k];
    const card = document.createElement("button");
    card.className = "cab-card";
    card.style.background = c.bg;
    card.style.color = c.fg;
    card.innerHTML = `
      <div class="cab-card-cap">${svg(c.icon, c.fg)}<span class="cab-card-titlu">${c.titlu}</span></div>
      <div class="cab-card-sinteza" data-cheie="${k}">${c.sinteza}</div>
    `;
    card.addEventListener("click", () => c.deschide(nav));
    grila.appendChild(card);
  }));

  actualizeazaControlAsi(grila);  // [p87_asistent]
}


// [p87_asistent] semafor pe cardul Control fiscal (asistent) - doar firmele lui
async function actualizeazaControlAsi(grila) {
  const zona = grila.querySelector('[data-cheie="control"]');
  if (!zona) return;
  try {
    const r = await api.get("/control-fiscal");
    const s = (r && r.sumar) || {};
    zona.innerHTML = semaforCardControl(s);   // [deficiența 224] un rând: patru buline, numărul de firme în fiecare stare, fără text
  } catch {}
}
