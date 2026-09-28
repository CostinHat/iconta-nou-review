// P13c — proba pe portofoliu pe portal: verdictul din stare vine din PUNCTUL UNIC.
// Intai stare ABSENTA si stare NECUNOSCUTA (nu-verde), apoi verde EXPLICIT (verde).
import assert from "assert";
import { readFileSync } from "fs";

const PUNCT = "/home/costin/iconta_nou/static/js/ecrane/verdict.js";
const src = readFileSync(PUNCT, "utf8").replace(/export /g, "");
const mod = (0, eval)(src + "\n;({ VERDICT_POZITIV, verdictDinStare })");
const { VERDICT_POZITIV, verdictDinStare } = mod;

// simuleaza ramura portal.js pentru cazul non-rosu/galben
function clasaPortal(stare) {
  const v = verdictDinStare(stare, "portal");
  return { clasa: v.pozitiv ? "pa-verde" : "pa-neutru", titlu: v.titlu, pozitiv: v.pozitiv };
}

const cazuri = [
  ["INVALID: stare absentă (null)", null],
  ["INVALID: stare absentă (undefined)", undefined],
  ["INVALID: stare necunoscută ('mov')", "mov"],
  ["VALID: verde explicit", "verde"],
];
for (const [nume, st] of cazuri) {
  const r = clasaPortal(st);
  console.log("• " + nume + " -> clasa=" + r.clasa + " · titlu=\"" + r.titlu + "\" · pozitiv=" + r.pozitiv);
}

// ── ASERTII ──
for (const st of [null, undefined, "mov"]) {
  const r = clasaPortal(st);
  assert(!r.pozitiv, "stare " + JSON.stringify(st) + " NU trebuie sa dea verdict pozitiv");
  assert(r.clasa === "pa-neutru", "stare " + JSON.stringify(st) + " -> clasa neutra, nu pa-verde");
  assert(r.titlu === "nu se poate verifica", "stare " + JSON.stringify(st) + " -> „nu se poate verifica\"");
}
const verde = clasaPortal("verde");
assert(verde.pozitiv && verde.clasa === "pa-verde", "verde explicit -> pa-verde pozitiv");
assert(verde.titlu === VERDICT_POZITIV.portal && verde.titlu === "Totul e la zi", "verde -> textul pozitiv din punctul unic");

console.log("\nPROBA PORTOFOLIU P13c: TOATE ASERTIILE TREC (absent/necunoscut -> gri, verde -> pozitiv)");
