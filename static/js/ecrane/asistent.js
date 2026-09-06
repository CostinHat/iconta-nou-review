// asistent.js — desktopul asistentului: ecran de lucru ca al cabinetului,
// minus exclusivele cabinetului. Bara 3 = doar motivational (pozitiv).
// Sursa unica: identitatea/permisiunile din sesiune.user(); cifrele din /eu/calitate.
//
// [p90_arbore 06.09.2026] PANOU DE NAVIGARE TIP ARBORE, in stanga, langa carduri.
//
// O SINGURA SURSA pentru amandoua. Arborele si cardurile se randeaza din `SECTIUNI` +
// `NODURI`, iar destinatia fiecarui nod e ACEEASI functie pe care o cheama cardul - nu o
// copie a ei. Motivul e masurat, nu estetic: chiar azi (R94) s-a reparat clasa „doua
// mecanisme raspund diferit la aceeasi intrebare", care traise noua zile fiindca ecranul
// si poarta citeau doua liste. Un arbore scris separat de carduri ar fi fost a treia.
// `core/test_asistent_arbore.py` cere egalitatea, pe structura.

import { api, ICOANE, CULORI_CARD } from "../api.js?v=1dccbc985b";
import { semaforCard } from "./semafor.js?v=df9fe94900";  // [p87_asistent]
import { sesiune } from "../sesiune.js?v=5d142951c9";
import { randeazaControl } from "./control.js?v=d09ca9ab5a";
import { randeazaTermene } from "./termene.js?v=e315c3005b";
import { randeazaValidat } from "./validat.js?v=decc4f494a";
import { randeazaListaFirme } from "./firme.js?v=53a469e3f4";
import { randeazaRecomanda } from "./recomanda.js?v=16ee976c05"; // [p31_recomanda]
import { randeazaRaporteaza } from "./raporteaza.js?v=f800de9e77"; // [p34_raporteaza]
import { randeazaPachete } from "./pachete.js?v=56eccd0e11"; // [p63_pachete]
import { randeazaDeclaratii } from "./declaratii.js?v=bd6aabd15a"; // [p44_declaratii]
import { randeazaSetari } from "./setari.js?v=f4a7f55d61"; // [p28_setari] acces asistent: Date profil + Schimba parola (gating existent setari.js:8-19)

function svg(nume, culoare) {
  return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="${culoare}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICOANE[nume] || ""}</svg>`;
}

// ── NODURILE, una per functionalitate. `deschide` e destinatia UNICA: o cheama si cardul,
// si nodul din arbore. Nimic din ce urmeaza nu duplica o navigare.
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
    deschide: (nav) => nav.deschide("Declarații", (corp) => randeazaDeclaratii(corp, nav)) },
  validat: { titlu: "De validat", icon: "clipboard", ...CULORI_CARD.piersica,
    sinteza: "Declarații de validat de la colegi", cere: "poate_valida",
    deschide: (nav) => nav.deschide("De validat", (corp) => randeazaValidat(corp, nav)) },
  pachete: { titlu: "Pachete lunare", icon: "mail", ...CULORI_CARD.violet,
    sinteza: "Trimite pachetul lunar către clienți",
    deschide: (nav) => nav.deschide("Pachete lunare", (corp) => randeazaPachete(corp, nav)) },
  raport: { titlu: "Raportează", icon: "report", ...CULORI_CARD.ardezie,
    sinteza: "Raportează o problemă către iConta.eu",
    deschide: (nav) => nav.deschide("Raporteaza", (corp) => randeazaRaporteaza(corp, nav)) },
  recomanda: { titlu: "Recomandă", icon: "gift", ...CULORI_CARD.chihlimbar,
    sinteza: "Invită un cabinet în iConta.eu",
    deschide: (nav) => nav.deschide("Recomanda", (corp) => randeazaRecomanda(corp, nav)) },
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
  // ocazional si administrativ, la urma
  { titlu: "Contul meu", noduri: ["raport", "recomanda", "setari"] },
];

// Cheile pe care le are DREPTUL sa vada utilizatorul, in ordinea sectiunilor.
export function cheiPermise(u) {
  const are = (n) => !n.cere || !!(u || {})[n.cere];
  return SECTIUNI.map((s) => ({
    titlu: s.titlu,
    noduri: s.noduri.filter((k) => NODURI[k] && are(NODURI[k])),
  })).filter((s) => s.noduri.length);
}

function arbore(sectiuni, nav) {
  const el = document.createElement("nav");
  el.className = "asi-arbore";
  el.setAttribute("aria-label", "Navigare între funcționalități");
  sectiuni.forEach((s, i) => {
    const grup = document.createElement("div");
    grup.className = "asi-grup";
    const cap = document.createElement("h2");
    cap.className = "asi-grup-titlu";
    cap.id = `asi-grup-${i}`;
    cap.textContent = s.titlu;
    grup.appendChild(cap);
    const lista = document.createElement("ul");
    lista.className = "asi-lista";
    lista.setAttribute("aria-labelledby", cap.id);
    s.noduri.forEach((k) => {
      const n = NODURI[k];
      const li = document.createElement("li");
      const b = document.createElement("button");
      b.type = "button";
      b.className = "asi-nod";
      b.dataset.nod = k;
      b.innerHTML = `${svg(n.icon, "#2f6fa6")}<span>${n.titlu}</span>`;
      b.addEventListener("click", () => n.deschide(nav));
      li.appendChild(b);
      lista.appendChild(li);
    });
    grup.appendChild(lista);
    el.appendChild(grup);
  });
  return el;
}

export async function desktopAsistent(continut, nav) {
  const u = sesiune.user() || {};
  const prenume = u.prenume || u.nume || u.email || "";  /* [salut_prenume 27.07.2026] afisa numele de familie */

  // [p25_bara3] bara 3 e in navigator acum, nu aici

  const sectiuni = cheiPermise(u);

  continut.innerHTML = `
    <div class="cab-salut">
      <div class="cab-salut-nume">Salut, ${prenume}</div>
    </div>
    <div class="asi-cadru">
      <div class="asi-panou"></div>
      <div class="cab-grila"></div>
    </div>
  `;

  continut.querySelector(".asi-panou").appendChild(arbore(sectiuni, nav));

  const grila = continut.querySelector(".cab-grila");
  // Cardurile, in EXACT ordinea arborelui - aceeasi lista, plimbata o data.
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

  actualizeazaRaportariAsi(grila);  // [p34_raporteaza]
  actualizeazaControlAsi(grila);  // [p87_asistent]
  document.addEventListener("raportari:schimbat", () => actualizeazaRaportariAsi(grila));
}


// [p87_asistent] semafor pe cardul Control fiscal (asistent) - doar firmele lui
async function actualizeazaControlAsi(grila) {
  const zona = grila.querySelector('[data-cheie="control"]');
  if (!zona) return;
  try {
    const r = await api.get("/control-fiscal");
    const s = (r && r.sumar) || {};
    zona.innerHTML = semaforCard([
      { n: s.rosu, cls: "pct-rosu", txt: "cu restanță" },
      { n: s.galben, cls: "pct-galben", txt: "de urmărit" },
    ], "Toate firmele la zi");
  } catch {}
}

// [p34_raporteaza] badge rosu pe cardul Raporteaza (asistent)
async function actualizeazaRaportariAsi(grila) {
  const card = grila.querySelector('[data-cheie="raport"]');
  const host = card ? card.closest(".cab-card") : null;
  if (!host) return;
  try {
    const r = await api.get("/raportari/contor");
    const n = (r && r.necitite) || 0;
    let b = host.querySelector(".cab-card-badge");
    if (n > 0) {
      if (!b) {
        b = document.createElement("span");
        b.className = "cab-card-badge";
        host.style.position = "relative";
        host.appendChild(b);
      }
      b.textContent = n;
    } else if (b) { b.remove(); }
  } catch {}
}
