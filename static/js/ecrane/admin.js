// admin.js — desktopul superadmin (Admin iConta).
// Spatiu separat de cabinet: doar functiile de administrare iConta.
// Acum: cardul Raportari (raspuns la sesizari). Extensibil (adaugi un dict in DEF).

import { sesiune } from "../sesiune.js";
import { randeazaAdminRaportari } from "./admin_raportari.js";

// iconite SVG inline (autonome)
const IC = {
  report: '<rect x="3" y="4" width="18" height="14" rx="2"/><path d="M3 8h18"/><path d="M7 12h7M7 15h4"/>',
};
function svg(cheie, fg) {
  return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="${fg}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${IC[cheie] || ""}</svg>`;
}

// cardurile panoului Admin iConta (extensibil)
const DEF = [
  { cheie:"raportari", titlu:"Raportări", icon:"report", bg:"#f3e8ff", fg:"#6d28d9",
    sinteza:"Răspunde la sesizările utilizatorilor",
    actiune:(nav) => nav.deschide("Raportări", (corp) => randeazaAdminRaportari(corp, nav)) },
];

export function desktopAdmin(continut, nav) {
  const u = sesiune.user() || {};
  const azi = new Date().toLocaleDateString("ro-RO", { day:"numeric", month:"long", year:"numeric" });
  const prenume = u.prenume || (u.nume || "").split(" ").slice(-1)[0] || u.nume || "";
  continut.innerHTML = `
    <div class="cab-salut">
      <div class="cab-salut-nume">Bună, ${prenume}</div>
      <div class="cab-salut-data">Panou Admin iConta — ${azi}</div>
    </div>
    <div class="cab-grila"></div>
  `;
  const grila = continut.querySelector(".cab-grila");
  DEF.forEach((c) => {
    const card = document.createElement("button");
    card.className = "cab-card";
    card.style.background = c.bg;
    card.style.color = c.fg;
    card.innerHTML = `
      <div class="cab-card-cap">${svg(c.icon, c.fg)}<span class="cab-card-titlu">${c.titlu}</span></div>
      <div class="cab-card-sinteza" data-cheie="${c.cheie}">${c.sinteza}</div>
    `;
    card.addEventListener("click", () => c.actiune(nav));
    grila.appendChild(card);
  });
}
