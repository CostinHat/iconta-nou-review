// asistent.js — desktopul asistentului: ecran de lucru ca al cabinetului,
// minus exclusivele cabinetului. Bara 3 = doar motivational (pozitiv).
// Sursa unica: identitatea/permisiunile din sesiune.user(); cifrele din /eu/calitate.

import { api } from "../api.js";
import { semaforCard } from "./semafor.js";  // [p87_asistent]
import { sesiune } from "../sesiune.js";
import { randeazaControl } from "./control.js";
import { randeazaTermene } from "./termene.js";
import { randeazaValidat } from "./validat.js";
import { randeazaListaFirme } from "./firme.js?v=22";
import { randeazaRecomanda } from "./recomanda.js"; // [p31_recomanda]
import { randeazaRaporteaza } from "./raporteaza.js"; // [p34_raporteaza]
import { randeazaPachete } from "./pachete.js"; // [p63_pachete]
import { randeazaDeclaratii } from "./declaratii.js"; // [p44_declaratii]

function svg(nume, culoare) {
  const P = {
    building: '<path d="M3 21h18"/><path d="M5 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16"/><path d="M19 21V11a2 2 0 0 0-2-2h-2"/><path d="M9 7h2M9 11h2M9 15h2"/>',
    shield: '<path d="M12 3l8 3v6c0 4-3 7-8 9-5-2-8-5-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    calendar: '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M3 10h18M8 2v4M16 2v4"/>',
    clipboard: '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M8 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2"/>',
    mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    gift: '<rect x="3" y="8" width="18" height="4"/><path d="M12 8v13M5 12v9h14v-9"/><path d="M12 8C12 5 9 3 7.5 4.5S9 8 12 8zM12 8c0-3 3-5 4.5-3.5S15 8 12 8z"/>',
    report: '<path d="M4 4h16v16H4z"/><path d="M8 14v3M12 10v7M16 7v10"/>',
  };
  return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="${culoare}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${P[nume] || ""}</svg>`;
}

function inLucru(titlu) {
  return (nav) => nav.deschide(titlu, (corp) => {
    corp.innerHTML = `<p class="ecran-nota">${titlu} — în lucru.</p>`;
  });
}

export async function desktopAsistent(continut, nav) {
  const u = sesiune.user() || {};
  const prenume = u.nume || u.email || "";
  const poateValida = !!u.poate_valida;

  // [p25_bara3] bara 3 e in navigator acum, nu aici

  const DEF = [
    { cheie:"firme",     titlu:"Firme",          icon:"building",  bg:"#e9f0fe", fg:"#1d4ed8",
      sinteza:"Firmele tale alocate" },
    { cheie:"control",   titlu:"Control fiscal", icon:"shield",    bg:"#dff4f2", fg:"#0a807b",
      sinteza:"Starea fiscală a firmelor tale" },
    { cheie:"termene",   titlu:"Termene",        icon:"calendar",  bg:"#e6f6ec", fg:"#15803d",
      sinteza:"Scadențele firmelor tale" },
    ...(poateValida ? [
    { cheie:"validat",   titlu:"De validat",     icon:"clipboard", bg:"#faece7", fg:"#993c1d",
      sinteza:"Declarații de validat de la colegi" }] : []),
    { cheie:"pachete",   titlu:"Pachete lunare", icon:"mail",      bg:"#efebfe", fg:"#6d28d9",
      sinteza:"Trimite pachetul lunar către clienți" },
    { cheie:"recomanda", titlu:"Recomandă",      icon:"gift",      bg:"#fbeedd", fg:"#92500a",
      sinteza:"Invită un cabinet în iConta" },
    { cheie:"raport",    titlu:"Raportează",     icon:"report",    bg:"#eaeef6", fg:"#45597f",
      sinteza:"Raportează o problemă către iConta" },
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
      cheie:"declaratii", titlu:"Declarații", icon:"clipboard",
      bg:"#eaf3ff", fg:"#1d4ed8",
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
