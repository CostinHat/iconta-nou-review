// Parametrul unei funcții interioare care acoperă parametrul funcției care o conține (lotul 5, comanda 4: regresia lui 244).
//
// Cazul care a deschis clasa: comanda 3 (265) i-a dat lui `deseneaza` din `ecranJurnal(corp, nav, t, opt)` parametrul `opt = {}`
// (`{ peLoc }`). De atunci `opt.evidentiaza` din corpul lui `deseneaza` citea obiectul gol, nu pe cel cu notele venite din Bilanț:
// Registrul jurnal se deschidea fără notele de închidere evidențiate. Codul nu dădea nicio eroare — numele exista, doar că era altul.
//
// Ieșire: JSON, o listă de {fisier, linie, nume, functie, linie_exterioara}. Codul de ieșire 2 = sursa nu se poate citi.
// Limita, declarată: se văd numai parametrii (inclusiv cei cu valoare implicită, destructurați sau `...rest`); o variabilă `let`/`const`
// din corp care acoperă un parametru exterior nu e în clasă.
"use strict";
const fs = require("fs");
const path = require("path");
const acorn = require("/usr/share/nodejs/acorn");

const RAD = path.resolve(__dirname, "..");
const FUNCTII = new Set(["FunctionDeclaration", "FunctionExpression", "ArrowFunctionExpression"]);

function fisiere(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) return e.name === "vendor" ? [] : fisiere(p);
    return e.name.endsWith(".js") && !e.name.endsWith(".min.js") ? [p] : [];
  });
}

function nume(tipar, out) {
  if (!tipar) return out;
  if (tipar.type === "Identifier") out.push(tipar.name);
  else if (tipar.type === "AssignmentPattern") nume(tipar.left, out);
  else if (tipar.type === "RestElement") nume(tipar.argument, out);
  else if (tipar.type === "ObjectPattern") tipar.properties.forEach((p) => nume(p.type === "RestElement" ? p : p.value, out));
  else if (tipar.type === "ArrayPattern") tipar.elements.forEach((e) => nume(e, out));
  return out;
}

function numeFunctie(fn, parinte) {
  if (fn.id) return fn.id.name;
  if (parinte && parinte.type === "VariableDeclarator" && parinte.id.type === "Identifier") return parinte.id.name;
  if (parinte && parinte.type === "Property" && parinte.key) return parinte.key.name || parinte.key.value;
  return "(anonimă)";
}

function scaneaza(fisier) {
  const sursa = fs.readFileSync(fisier, "utf8");
  const ast = acorn.parse(sursa, { ecmaVersion: "latest", sourceType: "module", locations: true });
  const gasite = [];
  (function viziteaza(n, parinte, stiva) {
    if (!n || typeof n.type !== "string") return;
    let s = stiva;
    if (FUNCTII.has(n.type)) {
      const proprii = n.params.flatMap((p) => nume(p, []));
      for (const x of proprii) {
        const ext = [...stiva].reverse().find((f) => f.nume.includes(x));
        if (ext) gasite.push({ fisier: path.relative(RAD, fisier), linie: n.loc.start.line, nume: x, functie: numeFunctie(n, parinte),
          linie_exterioara: ext.linie });
      }
      s = stiva.concat([{ nume: proprii, linie: n.loc.start.line }]);
    }
    for (const k of Object.keys(n)) {
      if (k === "loc" || k === "start" || k === "end") continue;
      const v = n[k];
      if (Array.isArray(v)) v.forEach((x) => viziteaza(x, n, s));
      else if (v && typeof v.type === "string") viziteaza(v, n, s);
    }
  })(ast, null, []);
  return gasite;
}

const tinte = process.argv.length > 2 ? process.argv.slice(2).map((f) => path.resolve(f)) : fisiere(path.join(RAD, "static", "js"));
let toate = [];
try {
  for (const f of tinte) toate = toate.concat(scaneaza(f));
} catch (e) {
  process.stderr.write(String(e && e.stack || e));
  process.exit(2);
}
process.stdout.write(JSON.stringify(toate, null, 1));
