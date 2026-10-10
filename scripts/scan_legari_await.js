// Butoane legate după o cerere așteptată (comanda Costin 10.10.2026 pct.8, verbatim: „Clasa «butoane legate după o cerere
// așteptată»: măsoar-o pe toate ecranele și repar-o unde apare, cu gard. Un clic al contabilului nu se pierde nicăieri.”)
//
// Forma clasei, în aceeași funcție: (1) un element ajunge în pagină (`x.innerHTML = …` / `insertAdjacentHTML` / `outerHTML`) cu un
// `id="…"` sau un atribut `data-…`; (2) funcția face `await`; (3) abia apoi leagă clicul pe elementul acela (`addEventListener`,
// `.onclick =`, `onchange`, `oninput`, `onsubmit`). Între (2) și (3) butonul e pe ecran, dar clicul nu face nimic — se pierde.
// Cazul care a deschis clasa: jurnalul își lega butoanele după `await legaBlocareLuna(...)` (deficiențele 58 și 96, 10.10.2026).
//
// Ieșire: JSON, o listă de {fisier, functie, randat, asteptat, legat, selector}. Codul de ieșire 2 = sursa nu se poate citi.
// Limita, declarată: elementul randat de o funcție ajutătoare (HTML întors de alt apel) nu se vede ca randare în funcția curentă.
"use strict";
const fs = require("fs");
const path = require("path");
const acorn = require("/usr/share/nodejs/acorn");
const walk = require("/usr/share/nodejs/acorn-walk");

const RAD = path.resolve(__dirname, "..");
const FUNCTII = new Set(["FunctionDeclaration", "FunctionExpression", "ArrowFunctionExpression"]);
const EVENIMENTE = new Set(["onclick", "onchange", "oninput", "onsubmit", "onkeydown", "onkeyup"]);

function fisiere(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const p = path.join(dir, e.name);
    return e.isDirectory() ? fisiere(p) : (e.name.endsWith(".js") ? [p] : []);
  });
}

// textul static al unei expresii: toate literalele de șir și bucățile de șablon din ea
function textStatic(nod) {
  const bucati = [];
  walk.full(nod, (n) => {
    if (n.type === "Literal" && typeof n.value === "string") bucati.push(n.value);
    if (n.type === "TemplateElement") bucati.push(n.value.cooked || n.value.raw);
  });
  return bucati.join("\u0001");
}

// funcția care conține direct nodul (fără funcțiile imbricate)
function noduriDirecte(fn) {
  const out = [];
  (function viziteaza(n, radacina) {
    if (!n || typeof n.type !== "string") return;
    if (!radacina && FUNCTII.has(n.type)) return;
    out.push(n);
    for (const k of Object.keys(n)) {
      if (k === "loc" || k === "start" || k === "end") continue;
      const v = n[k];
      if (Array.isArray(v)) v.forEach((x) => viziteaza(x, false));
      else if (v && typeof v.type === "string") viziteaza(v, false);
    }
  })(fn.body, true);
  return out;
}

function selectorDin(nod, variabile) {
  // querySelector("#x") / querySelectorAll("[data-x]") / getElementById("x"), direct sau printr-o variabilă / .forEach
  if (!nod) return null;
  if (nod.type === "Identifier") return variabile.get(nod.name) || null;
  if (nod.type === "CallExpression" && nod.callee.type === "MemberExpression") {
    const m = nod.callee.property.name;
    const a = nod.arguments[0];
    if ((m === "querySelector" || m === "querySelectorAll") && a && a.type === "Literal" && typeof a.value === "string") return a.value;
    if (m === "getElementById" && a && a.type === "Literal") return "#" + a.value;
    if (m === "closest" || m === "forEach") return selectorDin(nod.callee.object, variabile);
  }
  if (nod.type === "MemberExpression") return selectorDin(nod.object, variabile);
  return null;
}

// un selector se potrivește cu HTML-ul randat dacă îi numește id-ul sau atributul data-
function potriveste(selector, html) {
  const id = /^#([\w-]+)/.exec(selector);
  if (id) return html.includes('id="' + id[1] + '"') || html.includes("id='" + id[1] + "'");
  const data = /\[(data-[\w-]+)/.exec(selector);
  if (data) return html.includes(data[1] + "=") || html.includes(data[1] + " ") || html.includes(data[1] + ">");
  const cls = /^\.([\w-]+)$/.exec(selector);
  if (cls) return new RegExp("class=[\"'][^\"']*\\b" + cls[1] + "\\b").test(html);
  return false;
}

function scaneaza(fisier) {
  const src = fs.readFileSync(fisier, "utf8");
  const ast = acorn.parse(src, { ecmaVersion: "latest", sourceType: "module", locations: true });
  const rel = path.relative(RAD, fisier);
  // fiecare funcție, cu părintele ei (funcția care o conține) și apelul `.then(...)` căruia îi e callback, dacă e cazul
  const fn = [];
  const parinte = new Map(), dupaThen = new Map();
  (function urca(n, curent) {
    if (!n || typeof n.type !== "string") return;
    if (n.type === "CallExpression" && n.callee.type === "MemberExpression" && ["then", "finally"].includes(n.callee.property.name))
      for (const a of n.arguments) if (FUNCTII.has(a.type)) dupaThen.set(a, n);
    let c = curent;
    if (FUNCTII.has(n.type)) { parinte.set(n, curent); fn.push(n); c = n; }
    for (const k of Object.keys(n)) {
      if (k === "loc") continue;
      const v = n[k];
      if (Array.isArray(v)) v.forEach((x) => urca(x, c));
      else if (v && typeof v.type === "string") urca(v, c);
    }
  })(ast, null);
  const date = new Map();
  for (const f of fn) {
    const noduri = noduriDirecte(f);
    const variabile = new Map();   // nume -> selector (const b = corp.querySelector("#x"))
    const initiale = new Map();    // nume -> textul static al valorii (const html = `...`; html += ...)
    for (const n of noduri) {
      if (n.type === "VariableDeclarator" && n.id.type === "Identifier" && n.init) {
        const s = selectorDin(n.init, variabile);
        if (s) variabile.set(n.id.name, s);
        initiale.set(n.id.name, (initiale.get(n.id.name) || "") + textStatic(n.init));
      }
      if (n.type === "AssignmentExpression" && n.left.type === "Identifier")
        initiale.set(n.left.name, (initiale.get(n.left.name) || "") + textStatic(n.right));
    }
    const html = (expr) => {
      let t = textStatic(expr);
      walk.full(expr, (x) => { if (x.type === "Identifier" && initiale.has(x.name)) t += initiale.get(x.name); });
      return t;
    };
    const d = { randari: [], asteptari: [], legari: [] };
    for (const n of noduri) {
      if (n.type === "AssignmentExpression" && n.left.type === "MemberExpression"
          && ["innerHTML", "outerHTML"].includes(n.left.property.name)) d.randari.push({ poz: n.end, linie: n.loc.start.line, html: html(n.right) });
      if (n.type === "CallExpression" && n.callee.type === "MemberExpression" && n.callee.property.name === "insertAdjacentHTML")
        d.randari.push({ poz: n.end, linie: n.loc.start.line, html: html(n.arguments[1] || n) });
      if (n.type === "AwaitExpression") d.asteptari.push({ poz: n.start, linie: n.loc.start.line });
      if (n.type === "CallExpression" && n.callee.type === "MemberExpression" && n.callee.property.name === "addEventListener") {
        const s = selectorDin(n.callee.object, variabile);
        if (s) d.legari.push({ poz: n.start, linie: n.loc.start.line, selector: s });
      }
      if (n.type === "CallExpression" && n.callee.type === "MemberExpression" && n.callee.property.name === "forEach") {
        // corp.querySelectorAll("[data-x]").forEach((b) => b.addEventListener(...)) — legarea e în callback, dar rulează acum
        const s = selectorDin(n.callee.object, variabile);
        const cb = n.arguments[0];
        if (s && cb && FUNCTII.has(cb.type) && /addEventListener|\.on(click|change|input|submit)\s*=/.test(src.slice(cb.start, cb.end)))
          d.legari.push({ poz: n.start, linie: n.loc.start.line, selector: s });
      }
      if (n.type === "AssignmentExpression" && n.left.type === "MemberExpression" && EVENIMENTE.has(n.left.property.name)) {
        const s = selectorDin(n.left.object, variabile);
        if (s) d.legari.push({ poz: n.start, linie: n.loc.start.line, selector: s });
      }
    }
    date.set(f, d);
  }
  const out = [];
  for (const g of fn) {
    for (const l of date.get(g).legari) {
      // lanțul de funcții de la cea care leagă până la rădăcină; randarea poate sta în oricare (ea rulează înainte)
      const lant = [];
      for (let f = g; f; f = parinte.get(f)) lant.push(f);
      let gasit = null;
      for (let i = 0; i < lant.length && !gasit; i++) {
        const r = date.get(lant[i]).randari.filter((x) => x.poz < l.poz && potriveste(l.selector, x.html)).pop();
        if (!r) continue;
        // așteptările care cad între randare și legare: în funcția randării după ea, și în funcțiile de sub ea până la legare;
        // un callback `.then(...)` e o așteptare la locul apelului
        const intre = [];
        for (let k = 0; k <= i; k++) {
          for (const a of date.get(lant[k]).asteptari) if (a.poz > r.poz && a.poz < l.poz) intre.push(a);
          const th = dupaThen.get(lant[k]);
          if (k < i && th && th.start > r.poz) intre.push({ poz: th.start, linie: th.loc.start.line });
        }
        if (intre.length) gasit = { r, a: intre.sort((x, y) => x.poz - y.poz)[0] };
        else break;   // randarea cea mai apropiată e urmată direct de legare: legat la timp
      }
      if (gasit) out.push({ fisier: rel, functie: g.loc.start.line, randat: gasit.r.linie, asteptat: gasit.a.linie, legat: l.linie, selector: l.selector });
    }
  }
  return out;
}

try {
  const tinta = process.argv.slice(2);
  const lista = tinta.length ? tinta.map((f) => path.resolve(f)) : fisiere(path.join(RAD, "static", "js")).sort();
  process.stdout.write(JSON.stringify(lista.flatMap(scaneaza), null, 1) + "\n");
} catch (e) {
  process.stderr.write("scan_legari_await: " + e.message + "\n");
  process.exit(2);
}
