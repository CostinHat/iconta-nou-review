// semafor.js — helper comun pentru semaforul de pe carduri.
// Afiseaza doar starile active (zero ascuns), pe orizontala.
// Daca tot e zero -> rand verde pozitiv cu mesajOk.
// Refolosit de cabinet.js si asistent.js (principiul: construit o data).

export function semaforCard(perechi, mesajOk) {
  // perechi: [{n, cls, txt}, ...] in ordine rosu, galben (verdele e "ok")
  const active = perechi.filter((p) => (p.n || 0) > 0);
  if (!active.length) {
    return `<div class="cab-stari"><span class="cab-stare"><span class="cab-pct pct-verde"></span>${mesajOk}</span></div>`;
  }
  const html = active.map((p) =>
    `<span class="cab-stare"><span class="cab-pct ${p.cls}"></span>${p.n} ${p.txt}</span>`
  ).join("");
  return `<div class="cab-stari">${html}</div>`;
}
