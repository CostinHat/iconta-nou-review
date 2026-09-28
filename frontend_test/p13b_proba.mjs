// P13b — proba pe portofoliu: verdictul pozitiv apare DOAR din verde explicit.
// Intai cazul INVALID (cabinet cu firme doar-gri / sumar absent), apoi cazul VALID.
// Contrast vechi<->nou: forma VECHE arata verde fals; forma NOUA (din semafor.js) nu.
import assert from "assert";
import { readFileSync } from "fs";
// Citim sursa REALA a helperului (fara copie) si evaluam functia — proba ramane recomputabila pe fisierul viu.
const _src = readFileSync("/home/costin/iconta_nou/static/js/ecrane/semafor.js", "utf8");
const semaforCard = (0, eval)(_src.replace(/export\s+function/, "function") + "\n;semaforCard");

const MSG = "Toate firmele la zi";

// perechi exact ca in cabinet.js (dupa fix: include perechea gri)
function perechi(s) {
  return [
    { n: s.rosu, cls: "pct-rosu", txt: s.rosu === 1 ? "alertă fiscală" : "alerte fiscale" },
    { n: s.galben, cls: "pct-galben", txt: "de urmărit" },
    { n: s.gri, cls: "pct-gri", txt: s.gri === 1 ? "firmă nu se poate verifica" : "firme nu se pot verifica" },
  ];
}

// forma VECHE (bug): verde pe simpla absenta a rosu/galben, ignora gri si sumar absent
function semaforVechi(per, mesajOk) {
  const active = per.filter((p) => (p.n || 0) > 0);
  if (!active.length) return `<span class="cab-pct pct-verde"></span>${mesajOk}`;
  return per.filter((p) => (p.n || 0) > 0).map((p) => `${p.n} ${p.txt}`).join("");
}

const cazuri = [
  ["INVALID: firme doar-gri (rosu=galben=verde=0, gri=3)", { rosu: 0, galben: 0, verde: 0, gri: 3 }],
  ["INVALID: sumar absent ({})", {}],
  ["VALID: verde=5, restul 0", { rosu: 0, galben: 0, verde: 5, gri: 0 }],
];

for (const [nume, s] of cazuri) {
  const vechi = semaforVechi([
    { n: s.rosu, cls: "pct-rosu", txt: "r" }, { n: s.galben, cls: "pct-galben", txt: "g" },
  ], MSG);  // forma veche NU primea gri
  const nou = semaforCard(perechi(s), MSG, s.verde);
  console.log("• " + nume);
  console.log("   VECHI  verde-fals:", vechi.includes("pct-verde") && vechi.includes(MSG));
  console.log("   NOU    -> " + nou.replace(/</g, "‹").slice(0, 130));
}

// ── ASERTII ──
const griNou = semaforCard(perechi({ rosu: 0, galben: 0, verde: 0, gri: 3 }), MSG, 0);
assert(!griNou.includes(MSG), "only-gri NU trebuie sa arate verdictul pozitiv");
assert(griNou.includes("verifica"), "only-gri -> trebuie sa spuna ca nu se poate verifica");

const absentNou = semaforCard(perechi({}), MSG, undefined);
assert(!absentNou.includes(MSG), "sumar absent NU trebuie sa arate verdictul pozitiv");
assert(absentNou.includes("pct-gri") && absentNou.includes("nu se poate verifica"),
  "sumar absent -> nu se poate verifica (gri, absenta onesta)");

const validNou = semaforCard(perechi({ rosu: 0, galben: 0, verde: 5, gri: 0 }), MSG, 5);
assert(validNou.includes("pct-verde") && validNou.includes(MSG),
  "verde>0 explicit -> verdictul pozitiv apare");

// contrast: forma VECHE arata verde fals exact pe cazul invalid (dovada ca era bug)
assert(semaforVechi([{ n: 0 }, { n: 0 }], MSG).includes(MSG),
  "forma veche ar fi aratat verde fals pe absenta (contrast)");

console.log("\nPROBA PORTOFOLIU: TOATE ASERTIILE TREC (invalid -> nu-verde, valid -> verde)");
