// Răspunsul unei cereri vechi scris peste cel nou (C103, găsită de Code la rularea țintită de după poarta 2 a lotului 11; C102 e
// prima ei instanță, din certificatul de concediu).
//
// Forma clasei: contabilul editează un câmp (`input` / `change` / `keyup` / `search`, prin `addEventListener` sau `.oninput =`) sau
// dă un clic care schimbă starea ecranului (luna următoare, filtrul, pagina — o variabilă din afara handlerului), handlerul — direct sau printr-o funcție din același fișier, oricât de adânc — cere ceva de la server, iar după `await` / `.then`
// scrie răspunsul pe ecran. Dacă omul mai editează o dată înainte să vină răspunsul, pleacă a doua cerere; cele două răspunsuri pot
// sosi în orice ordine, iar cel vechi, sosit ultimul, ajunge pe ecran peste cel nou: propunerea, totalul sau lista arată altă valoare
// decât cea scrisă în câmp (reevaluarea valutară cu diferența de dinainte de sold, 1010 zile de concediu în loc de 10).
//
// Reparația unică: `ultimaCerere()` din `static/js/api.js`. Funcția care cere ia un jeton înaintea cererii (`const actuala =
// cerereNoua()`) și, după răspuns, iese dacă între timp a pornit alta (`if (!actuala()) return`) — și în `catch`, ca refuzul unei
// cereri vechi să nu acopere ecranul nou.
//
// Ieșire: JSON, o listă de {fisier, eveniment, handler, functie, linie, metoda, aparat, catch_aparat}, una pe cerere atinsă dintr-un
// handler de editare. `aparat` = după cerere există `if (!<jeton>()) return` cu un jeton luat din `ultimaCerere()`; `catch_aparat` =
// fiecare `catch` din jurul cererii are și el verificarea (true dacă nu e niciun `catch`). Codul de ieșire 2 = sursa nu se poate citi.
// Limita, declarată: se urmăresc numai funcțiile chemate pe nume din același fișier; o cerere făcută de o funcție importată (alt
// modul) sau chemată ca metodă (`obj.f()`) nu se vede.
"use strict";
const fs = require("fs");
const path = require("path");
const acorn = require("/usr/share/nodejs/acorn");
const walk = require("/usr/share/nodejs/acorn-walk");

const RAD = path.resolve(__dirname, "..");
const FUNCTII = new Set(["FunctionDeclaration", "FunctionExpression", "ArrowFunctionExpression"]);
const EVENIMENTE = new Set(["input", "change", "keyup", "search", "click"]);
const PROPRIETATI = new Set(["oninput", "onchange", "onkeyup", "onsearch", "onclick"]);
const METODE = new Set(["get", "post", "put", "del", "postForm"]);

function fisiere(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const p = path.join(dir, e.name);
    return e.isDirectory() ? fisiere(p) : (e.name.endsWith(".js") && !e.name.includes(".min.") ? [p] : []);
  });
}

function copii(n, f) {
  for (const k of Object.keys(n)) {
    if (k === "loc") continue;
    const v = n[k];
    if (Array.isArray(v)) v.forEach((x) => x && typeof x.type === "string" && f(x));
    else if (v && typeof v.type === "string") f(v);
  }
}

function scaneaza(fisier) {
  const src = fs.readFileSync(fisier, "utf8");
  const ast = acorn.parse(src, { ecmaVersion: "latest", sourceType: "module", locations: true });
  const rel = path.relative(RAD, fisier).split(path.sep).join("/");
  const parinte = new Map();      // nod -> părintele lui sintactic
  const nume = new Map();         // funcție -> numele ei (declarat, variabila, proprietatea) sau „<părinte>›anonim”
  const peNume = new Map();       // nume -> [funcții]
  const variabile = new Map();    // nume -> declarațiile lui (pentru HTML-ul pus în variabile)
  const fabrici = new Map();      // variabila `= ultimaCerere()` -> declarațiile ei
  const jetoane = new Map();      // variabila `= <fabrică>()` -> declarațiile ei
  (function urca(n, p) {
    parinte.set(n, p);
    if (n.type === "VariableDeclarator" && n.id.type === "Identifier")
      (variabile.get(n.id.name) || variabile.set(n.id.name, []).get(n.id.name)).push(n);
    if (n.type === "VariableDeclarator" && n.id.type === "Identifier" && n.init && n.init.type === "CallExpression"
        && n.init.callee.type === "Identifier" && n.init.callee.name === "ultimaCerere")
      (fabrici.get(n.id.name) || fabrici.set(n.id.name, []).get(n.id.name)).push(n);
    copii(n, (c) => urca(c, n));
  })(ast, null);
  // a doua trecere: jetoanele (fabricile pot fi declarate după funcțiile care le folosesc)
  // fabrica ținută pe element (`ultimaCerere(corp)`) e aceeași la fiecare apel: jetonul `= ultimaCerere(corp)()` e valabil oriunde
  const peElement = new Set();
  walk.full(ast, (n) => {
    if (n.type === "VariableDeclarator" && n.id.type === "Identifier" && n.init && n.init.type === "CallExpression"
        && n.init.callee.type === "CallExpression" && n.init.callee.callee.type === "Identifier"
        && n.init.callee.callee.name === "ultimaCerere" && n.init.callee.arguments.length) {
      (jetoane.get(n.id.name) || jetoane.set(n.id.name, []).get(n.id.name)).push(n);
      peElement.add(n);
    }
    if (n.type === "VariableDeclarator" && n.id.type === "Identifier" && n.init && n.init.type === "CallExpression"
        && n.init.callee.type === "Identifier" && fabrici.has(n.init.callee.name))
      (jetoane.get(n.id.name) || jetoane.set(n.id.name, []).get(n.id.name)).push(n);
  });
  const numeFunctie = (f) => {
    if (nume.has(f)) return nume.get(f);
    const p = parinte.get(f);
    let x = null;
    if (f.id) x = f.id.name;
    else if (p && p.type === "VariableDeclarator" && p.id.type === "Identifier") x = p.id.name;
    else if (p && p.type === "Property" && p.key) x = p.key.name || p.key.value;
    else if (p && p.type === "AssignmentExpression" && p.left.type === "MemberExpression") x = p.left.property.name;
    if (!x) {
      let s = p;
      while (s && !FUNCTII.has(s.type)) s = parinte.get(s);
      x = (s ? numeFunctie(s) : "<modul>") + "›anonim";
    }
    nume.set(f, x);
    return x;
  };
  walk.full(ast, (n) => {
    if (!FUNCTII.has(n.type)) return;
    const x = numeFunctie(n);
    if (!x.endsWith("›anonim")) (peNume.get(x) || peNume.set(x, []).get(x)).push(n);
  });
  const functiaDin = (n) => { let s = parinte.get(n); while (s && !FUNCTII.has(s.type)) s = parinte.get(s); return s; };
  const inauntru = (n, f) => n.start >= f.start && n.end <= f.end;
  // verificarea jetonului: `if (… !jeton() …) return` (oricât de imbricată în condiție)
  // o verificare ține numai dacă jetonul vine dintr-o fabrică declarată ÎN AFARA funcției care cere: o fabrică nouă la fiecare apel
  // are contorul ei, deci fiecare cerere e „ultima” și protecția e nulă
  const verificari = [];
  walk.full(ast, (n) => {
    if (n.type !== "IfStatement") return;
    const jet = [];
    walk.full(n.test, (t) => {
      if (t.type === "UnaryExpression" && t.operator === "!" && t.argument.type === "CallExpression"
          && t.argument.callee.type === "Identifier" && jetoane.has(t.argument.callee.name)) jet.push(t.argument.callee.name);
    });
    const c = n.consequent.type === "BlockStatement" ? n.consequent.body[0] : n.consequent;
    if (jet.length && c && c.type === "ReturnStatement") verificari.push({ start: n.start, end: n.end, jet });
  });
  // declarația care se vede din `la`: cea din cel mai apropiat domeniu care îl conține (numele se repetă de la un ecran la altul)
  const vazuta = (decl, la) => {
    let ales = null, d = null;
    for (const x of decl || []) {
      const s = functiaDin(x) || ast;
      if (inauntru(la, s) && (!d || s.start >= d.start)) { ales = x; d = s; }
    }
    return ales;
  };
  const valida = (v, fc) => v.jet.some((j) => {
    const dj = vazuta(jetoane.get(j), v);
    if (dj && peElement.has(dj)) return true;
    const df = dj && vazuta(fabrici.get(dj.init.callee.name), dj);
    return df && !inauntru(df, fc);
  });

  // numele chemat se leagă de declarația din cel mai apropiat domeniu care conține apelul (un fișier ca `firme.js` are zeci de
  // `deseneaza`, câte unul pe ecran — fără domeniu, un handler ar „atinge” toate ecranele)
  const domeniu = (f) => functiaDin(f.type === "FunctionDeclaration" ? f : (parinte.get(f) || f)) || ast;
  const rezolva = (n, apel) => {
    let ales = null, d = null;
    for (const g of peNume.get(n) || []) {
      const s = domeniu(g);
      if (inauntru(apel, s) && (!d || s.start >= d.start)) { ales = g; d = s; }
    }
    return ales;
  };
  // fluxul care rulează chiar din editare: corpul funcției, fără funcțiile imbricate (un handler de clic legat acolo rulează la alt
  // gest), dar cu callback-urile care rulează ca urmare a ei — `.then/.catch/.finally`, iterările pe liste, `setTimeout` (amânarea
  // unei căutări nu elimină cursa: răspunsul poate întârzia mai mult decât pauza) și funcția chemată pe loc
  const CALLBACK_METODE = new Set(["then", "catch", "finally", "forEach", "map", "filter", "some", "every", "reduce", "find"]);
  const CALLBACK_FUNCTII = new Set(["setTimeout", "queueMicrotask", "requestAnimationFrame", "pastreazaCampulActiv"]);
  const ruleazaAcum = (fn) => {
    const p = parinte.get(fn);
    if (!p || p.type !== "CallExpression") return false;
    if (p.callee === fn) return true;
    if (!p.arguments.includes(fn)) return false;
    if (p.callee.type === "MemberExpression") return CALLBACK_METODE.has(p.callee.property.name);
    return p.callee.type === "Identifier" && CALLBACK_FUNCTII.has(p.callee.name);
  };
  const directe = (f, cb) => {
    (function viz(n, radacina) {
      if (!radacina && FUNCTII.has(n.type) && !ruleazaAcum(n)) return;
      cb(n);
      copii(n, (c) => viz(c, false));
    })(f, true);
  };
  const handlere = [];
  walk.full(ast, (n) => {
    if (n.type === "CallExpression" && n.callee.type === "MemberExpression" && n.callee.property.name === "addEventListener"
        && n.arguments[0] && n.arguments[0].type === "Literal" && EVENIMENTE.has(n.arguments[0].value) && n.arguments[1])
      handlere.push({ ev: n.arguments[0].value, h: n.arguments[1], linie: n.loc.start.line });
    if (n.type === "AssignmentExpression" && n.left.type === "MemberExpression" && PROPRIETATI.has(n.left.property.name))
      handlere.push({ ev: n.left.property.name.slice(2), h: n.right, linie: n.loc.start.line });
  });
  const out = [];
  const vazute = new Set();
  for (const { ev, h, linie } of handlere) {
    // funcțiile atinse: handlerul + tot ce cheamă pe nume, tranzitiv
    const atinse = [];
    const coada = h.type === "Identifier" ? [rezolva(h.name, h)].filter(Boolean) : (FUNCTII.has(h.type) ? [h] : []);
    if (ev === "click") {
      // un clic intră în clasă numai dacă schimbă starea ecranului — o variabilă din afara lui (perioada, filtrul, pagina) — înainte
      // de a cere: atunci două clicuri pornesc cereri DIFERITE; un buton care cere același lucru de două ori nu poate arăta altceva
      let schimba = false;
      for (const f of coada) {
        const locale = new Set();
        directe(f, (c) => {
          if (c.type === "VariableDeclarator") walk.full(c.id, (x) => { if (x.type === "Identifier") locale.add(x.name); });
        });
        for (const p of f.params || []) walk.full(p, (x) => { if (x.type === "Identifier") locale.add(x.name); });
        directe(f, (c) => {
          const tinta = c.type === "AssignmentExpression" ? c.left : (c.type === "UpdateExpression" ? c.argument : null);
          if (tinta && tinta.type === "Identifier" && !locale.has(tinta.name)) schimba = true;
        });
      }
      if (!schimba) continue;
    }
    const viz = new Set();
    while (coada.length) {
      const f = coada.shift();
      if (viz.has(f)) continue;
      viz.add(f); atinse.push(f);
      directe(f, (c) => {
        if (c.type === "CallExpression" && c.callee.type === "Identifier") { const g = rezolva(c.callee.name, c); if (g) coada.push(g); }
      });
    }
    // a doua fațetă: răspunsul re-desenează CÂMPURI (`innerHTML` cu <input>/<select>/<textarea>, direct sau prin ajutătoarele care
    // întorc HTML — `camp(e)`, `randManual(m)`, `optCont`; fișierul, bifa și câmpul ascuns nu se tastează) — câmpul în care omul scrie
    // chiar atunci e înlocuit, iar ce a tastat și n-a confirmat încă (`change`) dispare. Fiecare desen de după cerere trebuie să ruleze
    // sub `pastreazaCampulActiv`: ori atribuirea însăși stă în callback-ul lui, ori apelul care duce la ea (un drum acoperit nu le
    // acoperă pe celelalte)
    const subPastreaza = (n) => {
      for (let x = parinte.get(n); x; x = parinte.get(x)) {
        const p = parinte.get(x);
        if (FUNCTII.has(x.type) && p && p.type === "CallExpression" && p.arguments.includes(x)
            && p.callee.type === "Identifier" && p.callee.name === "pastreazaCampulActiv") return true;
        if (x.type === "CallExpression" && x.callee.type === "Identifier" && x.callee.name === "pastreazaCampulActiv"
            && x.arguments.includes(n)) return true;
      }
      return false;
    };
    const CAMP = /<(select|textarea)\b|<input\b(?![^>]*type="(file|hidden|checkbox|radio)")/;
    // HTML-ul atribuit are câmpuri: în textul lui, sau într-o funcție / variabilă din fișier pe care o folosește (`camp(e)`, `optCont`)
    const areCampuri = (expr) => {
      if (CAMP.test(src.slice(expr.start, expr.end))) return true;
      let da = false;
      walk.full(expr, (x) => {
        const px = parinte.get(x);
        if (da || x.type !== "Identifier" || (px && px.type === "MemberExpression" && px.property === x && !px.computed)) return;
        const g = rezolva(x.name, expr);
        if (g && CAMP.test(src.slice(g.start, g.end))) da = true;
        const v = vazuta(variabile.get(x.name), expr);
        if (v && v.init && CAMP.test(src.slice(v.init.start, v.init.end))) da = true;
      });
      return da;
    };
    const deseneDupa = (c, fc) => {
      const gasite = [];
      const coada = [[fc, false, c.end]];
      const viz = new Set();
      while (coada.length) {
        const [g, prot, dela] = coada.shift();
        const k = g.start + ":" + prot;
        if (viz.has(k)) continue;
        viz.add(k);
        directe(g, (x) => {
          if (x.start < dela) return;
          const p = prot || subPastreaza(x);
          if (x.type === "AssignmentExpression" && x.left.type === "MemberExpression" && x.left.property.name === "innerHTML"
              && areCampuri(x.right)) gasite.push({ nod: x, prot: p });
          if (x.type === "CallExpression" && x.callee.type === "Identifier") {
            const h = rezolva(x.callee.name, x);
            if (h && h !== g) coada.push([h, p, 0]);
            if (x.callee.name === "pastreazaCampulActiv")
              for (const a of x.arguments) if (a.type === "Identifier") { const h2 = rezolva(a.name, a); if (h2) coada.push([h2, true, 0]); }
          }
        });
      }
      return gasite;
    };
    for (const f of atinse) {
      directe(f, (c) => {
        if (!(c.type === "CallExpression" && c.callee.type === "MemberExpression" && c.callee.object.type === "Identifier"
              && c.callee.object.name === "api" && METODE.has(c.callee.property.name))) return;
        const cheie = rel + ":" + c.start;
        if (vazute.has(cheie)) return;
        vazute.add(cheie);
        const fc = functiaDin(c);
        const desene = deseneDupa(c, fc);
        if (process.env.SCAN_DEPANARE) desene.forEach((d) => process.stderr.write(rel + ":" + c.loc.start.line + " -> desen " + d.nod.loc.start.line + (d.prot ? " păstrat" : "") + "\n"));
        // ecranul golit înainte de cerere (`corp.innerHTML = "Se încarcă…"`, fără câmpuri) nu lasă niciun câmp în care să se scrie cât
        // e cererea în zbor: fațeta a doua nu se aplică
        let golit = false;
        directe(fc, (x) => {
          if (x.type === "AssignmentExpression" && x.left.type === "MemberExpression" && x.left.property.name === "innerHTML"
              && x.end < c.start && x.left.object.type === "Identifier" && ["corp", "c", "zona"].includes(x.left.object.name)
              && parinte.get(x).type === "ExpressionStatement" && parinte.get(parinte.get(x)) === fc.body   // necondiționat
              && !/<(input|select|textarea)\b/.test(src.slice(x.right.start, x.right.end))) golit = true;
        });
        // verificarea trebuie să stea după cerere, în funcția care cere (sau într-un callback al ei)
        // verificarea din `catch` nu ține loc de cea de după răspuns: răspunsul reușit trece numai prin `try`
        const inCatch = (v) => { for (let x = parinte.get(c); x && x !== fc; x = parinte.get(x))
          if (x.type === "TryStatement" && x.handler && inauntru(c, x.block) && inauntru(v, x.handler)) return true; return false; };
        const dupa = verificari.filter((v) => v.start > c.end && inauntru(v, fc) && valida(v, fc) && !inCatch(v));
        // fiecare `catch` care învelește cererea, în funcția ei: și el cu verificarea
        let catchOk = true;
        for (let s = parinte.get(c); s && s !== fc; s = parinte.get(s)) {
          if (s.type === "TryStatement" && s.handler && inauntru(c, s.block) && s.handler.body.body.length
              && !verificari.some((v) => inauntru(v, s.handler) && valida(v, fc))) catchOk = false;
        }
        out.push({ fisier: rel, eveniment: ev, handler: linie, functie: numeFunctie(fc), linie: c.loc.start.line,
                   metoda: c.callee.property.name, aparat: dupa.length > 0, catch_aparat: catchOk,
                   redeseneaza_campuri: desene.length > 0 && !golit, pastreaza_campul: desene.length > 0 && desene.every((d) => d.prot) });
      });
    }
  }
  return out;
}

try {
  const tinta = process.argv.slice(2);
  const lista = tinta.length ? tinta.map((f) => path.resolve(f)) : fisiere(path.join(RAD, "static", "js")).sort();
  process.stdout.write(JSON.stringify(lista.flatMap(scaneaza), null, 1) + "\n");
} catch (e) {
  process.stderr.write("scan_cerere_veche: " + e.message + "\n");
  process.exit(2);
}
