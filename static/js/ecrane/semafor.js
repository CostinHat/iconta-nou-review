// semafor.js — helper comun pentru semaforul de pe carduri.
// Afiseaza doar starile active (zero ascuns), pe orizontala.
// Daca tot e zero -> rand verde pozitiv cu mesajOk.
// Refolosit de cabinet.js si asistent.js (principiul: construit o data).

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
