// semafor.js — helper comun pentru semaforul de pe carduri.
// Afiseaza doar starile active (zero ascuns), pe orizontala.
// Daca tot e zero -> rand verde pozitiv cu mesajOk.
// Refolosit de cabinet.js si asistent.js (principiul: construit o data).

// [deficiența 224, aprobat de Costin 10.10.2026] Cardul Control fiscal = semafor cu PATRU lumini, fiecare cu numărul de firme în starea
// ei — partiția `sumar` a serverului (fiecare firmă într-o singură stare: `uc_control_fiscal.control_fiscal_portofoliu`). DS cap.8:
// vertical, ROȘU -> GALBEN -> VERDE (urgența întâi), apoi GRI; toate patru mereu, și cu 0. Roșu = termen depășit (deficiența 220).
// Gard: regula SEMAFOR_PATRU_LUMINI din verificator.
export const LUMINI_CONTROL = [
  ["rosu", "pct-rosu", "cu restanță", "cu restanțe"],
  ["galben", "pct-galben", "de urmărit", "de urmărit"],
  ["verde", "pct-verde", "la zi", "la zi"],
  ["gri", "pct-gri", "nu se poate verifica", "nu se pot verifica"],
];
export function semaforPatruLumini(sumar) {
  const s = sumar || {};
  return `<div class="cab-semafor4">${LUMINI_CONTROL.map(([k, cls, unu, multe]) => {
    const n = s[k] || 0;
    return `<span class="cab-stare" data-stare="${k}"><span class="cab-pct ${cls}"></span><b class="tip-figura">${n}</b>&nbsp;${n === 1 ? unu : multe}</span>`;
  }).join("")}</div>`;
}

export function semaforCard(perechi, mesajOk, verde) {
  // perechi: starile NEGATIVE/nedecise de aratat cand n>0 (rosu, galben, gri...), in ordine.
  // [P13b, interdictia 27+31] Verdictul POZITIV (mesajOk) apare DOAR dintr-o stare VERDE explicita
  // primita de la backend (`verde` > 0), NICIODATA din absenta rosului/galbenului, din zero sau
  // dintr-un sumar lipsa. Gri se arata ca gri. Cand nu e nimic negativ SI backendul nu afirma verde
  // -> "nu se poate verifica" (absenta e onesta, nu un verde fals).
  const active = perechi.filter((p) => (p.n || 0) > 0);
  if (active.length) {
    const html = active.map((p) =>
      `<span class="cab-stare"><span class="cab-pct ${p.cls}"></span>${p.n} ${p.txt}</span>`
    ).join("");
    return `<div class="cab-stari">${html}</div>`;
  }
  if ((verde || 0) > 0 && mesajOk) {
    return `<div class="cab-stari"><span class="cab-stare"><span class="cab-pct pct-verde"></span>${mesajOk}</span></div>`;
  }
  return `<div class="cab-stari"><span class="cab-stare"><span class="cab-pct pct-gri"></span>nu se poate verifica</span></div>`;
}
