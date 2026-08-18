// asistent.js — desktopul asistentului: ecran de lucru ca al cabinetului,
// minus exclusivele cabinetului. Bara 3 = doar motivational (pozitiv).
// Sursa unica: identitatea/permisiunile din sesiune.user(); cifrele din /eu/calitate.

import { api, ICOANE, CULORI_CARD } from "../api.js?v=a7f9e80ae0";
import { semaforCard } from "./semafor.js?v=df9fe94900";  // [p87_asistent]
import { sesiune } from "../sesiune.js?v=5d142951c9";
import { randeazaControl } from "./control.js?v=8576a174b7";
import { randeazaTermene } from "./termene.js?v=e315c3005b";
import { randeazaValidat } from "./validat.js?v=2720732c1c";
import { randeazaListaFirme } from "./firme.js?v=3a63916477";
import { randeazaRecomanda } from "./recomanda.js?v=4dcc56e1ec"; // [p31_recomanda]
import { randeazaRaporteaza } from "./raporteaza.js?v=f800de9e77"; // [p34_raporteaza]
import { randeazaPachete } from "./pachete.js?v=8c32cbb767"; // [p63_pachete]
import { randeazaDeclaratii } from "./declaratii.js?v=65d022c121"; // [p44_declaratii]
import { randeazaSetari } from "./setari.js?v=d3e3cec16d"; // [p28_setari] acces asistent: Date profil + Schimba parola (gating existent setari.js:8-19)

function svg(nume, culoare) {
  return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="${culoare}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICOANE[nume] || ""}</svg>`;
}

function inLucru(titlu) {
  return (nav) => nav.deschide(titlu, (corp) => {
    corp.innerHTML = `<p class="ecran-nota">${titlu} — în lucru.</p>`;
  });
}

export async function desktopAsistent(continut, nav) {
  const u = sesiune.user() || {};
  const prenume = u.prenume || u.nume || u.email || "";  /* [salut_prenume 27.07.2026] afisa numele de familie */
  const poateValida = !!u.poate_valida;

  // [p25_bara3] bara 3 e in navigator acum, nu aici

  const DEF = [
    { cheie:"firme",     titlu:"Firme",          icon:"building",  ...CULORI_CARD.albastru,
      sinteza:"Firmele tale alocate" },
    { cheie:"control",   titlu:"Control fiscal", icon:"shield",    ...CULORI_CARD.teal,
      sinteza:"Starea fiscală a firmelor tale" },
    { cheie:"termene",   titlu:"Termene",        icon:"calendar",  ...CULORI_CARD.verde,
      sinteza:"Scadențele firmelor tale" },
    ...(poateValida ? [
    { cheie:"validat",   titlu:"De validat",     icon:"clipboard", ...CULORI_CARD.piersica,
      sinteza:"Declarații de validat de la colegi" }] : []),
    { cheie:"pachete",   titlu:"Pachete lunare", icon:"mail",      ...CULORI_CARD.violet,
      sinteza:"Trimite pachetul lunar către clienți" },
    { cheie:"recomanda", titlu:"Recomandă",      icon:"gift",      ...CULORI_CARD.chihlimbar,
      sinteza:"Invită un cabinet în iConta.eu" },
    { cheie:"raport",    titlu:"Raportează",     icon:"report",    ...CULORI_CARD.ardezie,
      sinteza:"Raportează o problemă către iConta.eu" },
    { cheie:"setari",    titlu:"Setări cont",    icon:"settings",  ...CULORI_CARD.ardezie,
      sinteza:"Parolă și date de profil" },
  ];

  continut.innerHTML = `
    <div class="cab-salut">
      <div class="cab-salut-nume">Salut, ${prenume}</div>
    </div>
    <div class="cab-grila"></div>
  `;

  const grila = continut.querySelector(".cab-grila");
  // [p44_declaratii] card Declaratii doar pentru cine poate pregati
  const _listaA = DEF.slice();
  if ((sesiune.user() || {}).poate_pregati) {
    _listaA.splice(3, 0, {
      cheie:"declaratii", titlu:"Declarații", icon: "declaratii",
      ...CULORI_CARD.albastru,
      sinteza:"Pregătește și trimite la validare"
    });
  }
  _listaA.forEach((c) => {
    const card = document.createElement("button");
    card.className = "cab-card";
    card.style.background = c.bg;
    card.style.color = c.fg;
    card.innerHTML = `
      <div class="cab-card-cap">${svg(c.icon, c.fg)}<span class="cab-card-titlu">${c.titlu}</span></div>
      <div class="cab-card-sinteza" data-cheie="${c.cheie}">${c.sinteza}</div>
    `;
    if (c.cheie === "firme") {
      card.addEventListener("click", () =>
        nav.deschide("Firme", (corp) => randeazaListaFirme(corp, nav, () => nav.inapoi())));
    } else if (c.cheie === "control") {
      card.addEventListener("click", () => nav.deschide("Control fiscal", (corp) => randeazaControl(corp, nav)));
    } else if (c.cheie === "termene") {
      card.addEventListener("click", () => nav.deschide("Termene", (corp) => randeazaTermene(corp, nav)));
    } else if (c.cheie === "validat") {
      card.addEventListener("click", () => nav.deschide("De validat", (corp) => randeazaValidat(corp, nav)));
    } else if (c.cheie === "recomanda") {  // [p31_recomanda]
      card.addEventListener("click", () => nav.deschide("Recomanda", (corp) => randeazaRecomanda(corp, nav)));
    } else if (c.cheie === "pachete") {  // [p63_pachete]
      card.addEventListener("click", () => nav.deschide("Pachete lunare", (corp) => randeazaPachete(corp, nav)));
    } else if (c.cheie === "raport") {  // [p34_raporteaza]
      card.addEventListener("click", () => nav.deschide("Raporteaza", (corp) => randeazaRaporteaza(corp, nav)));
    } else if (c.cheie === "declaratii") {  // [p44_declaratii]
      card.addEventListener("click", () => nav.deschide("Declarații", (corp) => randeazaDeclaratii(corp, nav)));
    } else if (c.cheie === "setari") {  // [p28_setari] gating in setari.js -> non-admin vede doar Date profil + Schimba parola
      card.addEventListener("click", () => nav.deschide("Setări cont", (corp) => randeazaSetari(corp, nav)));
    } else {
      card.addEventListener("click", () => inLucru(c.titlu)(nav));
    }
    grila.appendChild(card);
  });
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
