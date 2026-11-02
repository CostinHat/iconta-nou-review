// Măsurătorile verificatorului de design (comanda 15.1-E1): se evaluează în pagină, după ce ecranul e deschis; întoarce faptele (piesele, nu
// pixelii) și, pe fiecare rând al criteriului „migrat” a–h (scripts/verificator_design.py::RANDURI), motivele pentru care rândul PICĂ.
// Un rând fără motive TRECE. Ce nu se poate decide mecanic (ton, sens) rămâne subagentului, cu captura.
(() => {
  const vw = innerWidth, vh = innerHeight;
  const toate = [...document.querySelectorAll(".fereastra")];
  const F = toate[toate.length - 1] || null;
  const pica = { a: [], b: [], c: [], d: [], e: [], f: [], g: [], h: [] };
  const fapte = { viewport: [vw, vh], ferestre_deschise: toate.length };
  const norm = (t) => (t || "").replace(/\s+/g, " ").trim();
  // textul propriu al unui element, fără butoanele/linkurile/câmpurile din el (un rând de acțiuni nu e un paragraf explicativ)
  const proprio = (el) => { const c = el.cloneNode(true); c.querySelectorAll("button, a, select, input, textarea, .ajutor-btn").forEach((x) => x.remove()); return norm(c.innerText || c.textContent); };
  const vizibil = (el) => !!(el.offsetParent || el.getClientRects().length) && getComputedStyle(el).visibility !== "hidden";
  const h = (el) => Math.round(el.getBoundingClientRect().height);
  if (!F) {
    for (const r of Object.keys(pica)) pica[r].push("nicio fereastră de lucru deschisă");
    return { fapte, pica };
  }
  const rF = F.getBoundingClientRect();
  fapte.fereastra = { clase: F.className, lat: Math.round(rF.width), inalt: Math.round(rF.height), stanga: Math.round(rF.left), sus: Math.round(rF.top) };
  fapte.titlul_ferestrei = norm((F.querySelector(".pf-titlu, h2, h1") || {}).innerText || "");
  const ant = F.querySelector(".fereastra-antet");
  const corp = F.querySelector(".fereastra-corp");

  // ── a. bara de sus ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  const a = { inaltime: ant ? h(ant) : null };
  if (!ant) pica.a.push("nu există bara de sus (.fereastra-antet)");
  else {
    if (Math.abs(a.inaltime - 56) > 1) pica.a.push("bara de sus are " + a.inaltime + " px, nu 56");
    // [15.1-E2, pct.5] traseu = două sau mai multe ecrane vizitate înșiruite; „firma › numele ferestrei” (un singur „›”) NU e traseu
    const traseu = [...ant.querySelectorAll(".fir-veriga")];
    const separatori = ant.querySelectorAll(".fir-sep").length;
    a.traseu = traseu.length + (separatori > 1 ? separatori : 0);
    if (traseu.length || separatori > 1) pica.a.push("bara de sus are traseu (" + norm(ant.querySelector(".fereastra-fir")?.innerText) + ")");
    const inapoi = ant.querySelector(".nav-inapoi");
    a.sageata = !!inapoi && norm(inapoi.innerText) === "←";
    if (!a.sageata) pica.a.push("lipsește „←” (un pas înapoi)");
    const fir = norm(ant.querySelector(".fereastra-fir")?.innerText);
    a.firma_sau_cabinet = fir;
    // [15.1-E2] Panou Admin n-are firmă sau cabinet în lucru: contextul ei e „Panou Admin”, fără CUI (decizie în raport, E)
    if (!/CUI\s*\S+/.test(fir) && !/^Panou Admin\b/.test(fir)) pica.a.push("firma sau cabinetul în lucru nu apare cu CUI în bara de sus");
    const nume = ant.querySelector(".fereastra-nume, .fir-acum");
    a.numele_ferestrei = nume ? norm(nume.innerText) : null;
    if (!nume) pica.a.push("numele ferestrei nu e în bara de sus");
    else if (fir && fir === norm(nume.innerText)) pica.a.push("în bara de sus numele ferestrei e doar firma/cabinetul");
    a.cautare = !!ant.querySelector(".cautare-in-fereastra input");
    if (!a.cautare) pica.a.push("lipsește căutarea în bara de sus");
  }
  fapte.a = a;

  // ── b. fereastra de lucru, derulare, bara de jos ────────────────────────────────────────────────────────────────────────────────────
  const b = {};
  const pePeEcran = /\bfer-(lucru|tabel)\b/.test(F.className) && rF.width >= vw - 34 && rF.height >= vh - 34 && rF.left <= 18 && rF.top <= 18;
  b.pe_tot_ecranul = pePeEcran;
  if (!pePeEcran) pica.b.push("fereastra nu e fereastră de lucru pe tot ecranul (" + Math.round(rF.width) + "×" + Math.round(rF.height) + " din " + vw + "×" + vh + ", " + F.className + ")");
  const derulari = [];
  for (const el of [F, ...F.querySelectorAll("*")]) {
    if (!vizibil(el)) continue;
    const cs = getComputedStyle(el);
    if (/(auto|scroll)/.test(cs.overflowY) && el.scrollHeight > el.clientHeight + 1)
      derulari.push({ loc: el.tagName.toLowerCase() + "." + String(el.className).split(" ")[0], fel: "vertical", ascuns: el.scrollHeight - el.clientHeight, tabel: !!el.querySelector("table, .ds-tabel") || el.matches(".ds-tabel-cutie, .zona-derulare") });
    if (el.scrollWidth > el.clientWidth + 1 && /(auto|scroll)/.test(cs.overflowX))
      derulari.push({ loc: el.tagName.toLowerCase() + "." + String(el.className).split(" ")[0], fel: "lateral", ascuns: el.scrollWidth - el.clientWidth, tabel: false });
  }
  b.derulari = derulari;
  const lat = derulari.filter((d) => d.fel === "lateral");
  const vert = derulari.filter((d) => d.fel === "vertical");
  if (lat.length) pica.b.push("derulare laterală în " + lat.map((d) => d.loc).join(", "));
  if (vert.length > 1) pica.b.push(vert.length + " locuri de derulare verticală: " + vert.map((d) => d.loc).join(", "));
  if (vert.some((d) => !d.tabel)) pica.b.push("derulează conținutul ferestrei, nu tabelul: " + vert.filter((d) => !d.tabel).map((d) => d.loc).join(", "));
  // bara de jos fixă: un rând de butoane lipit de marginea de jos a ferestrei, de 72 px
  const bj = [...F.querySelectorAll("*")].filter((el) => vizibil(el) && el.querySelector("button") && el.getBoundingClientRect().bottom >= rF.bottom - 2
    && Math.abs(h(el) - 72) <= 1 && el.getBoundingClientRect().width >= rF.width - 40).pop() || null;
  b.bara_jos = bj ? { clase: String(bj.className), inaltime: h(bj) } : null;
  if (!bj) pica.b.push("nu există bara de jos fixă de 72 px");
  else {
    const butoane = [...bj.querySelectorAll("button")].filter(vizibil);
    const principale = butoane.filter((x) => /buton-primar|buton-principal/.test(x.className));
    b.butoane_principale = principale.length;
    if (principale.length !== 1) pica.b.push("bara de jos are " + principale.length + " butoane principale, nu unul");
    if (!butoane.some((x) => norm(x.innerText) === "Renunță")) pica.b.push("bara de jos nu are „Renunță”");
    const dez = principale.filter((x) => x.disabled || x.dataset.cadruInactiv);
    b.principal_inactiv_fara_motiv = dez.filter((x) => !(x.title || x.getAttribute("aria-describedby") || bj.querySelector(".bara-motiv"))).length;
    if (b.principal_inactiv_fara_motiv) pica.b.push("butonul principal inactiv fără motiv");
  }
  fapte.b = b;

  // ── c. listele de înregistrări = tabelul DS ─────────────────────────────────────────────────────────────────────────────────────────
  const c = { tabele_ds: 0, tabele_vechi: [], liste_rand_buton: [] };
  const tabele = [...F.querySelectorAll("table")].filter(vizibil);
  for (const t of tabele) {
    const ds = t.classList.contains("ds-tabel");
    if (!ds) { c.tabele_vechi.push(String(t.className) || "(fără clasă)"); continue; }
    c.tabele_ds++;
    const th = t.querySelector("thead th"), td = t.querySelector("tbody td");
    if (th && Math.abs(h(th) - 40) > 1) pica.c.push("capul tabelului are " + h(th) + " px, nu 40");
    if (td && Math.abs(h(td) - 44) > 1) pica.c.push("rândurile tabelului au " + h(td) + " px, nu 44");
    const randuri = [...t.querySelectorAll("tbody tr")];
    if (randuri.length > 1 && getComputedStyle(randuri[0]).backgroundColor === getComputedStyle(randuri[1]).backgroundColor) pica.c.push("tabel fără zebra");
    const antete = [...t.querySelectorAll("thead th")].map((x) => norm(x.innerText));
    if (!antete.includes("Stare") && t.querySelector(".ds-pastila, .pastila-stare")) pica.c.push("starea nu e în coloana „Stare”");
    for (const r of randuri) if (r.querySelectorAll("button:not(.ds-xs-ascuns), a.buton-secundar").length > 2) { pica.c.push("peste 2 acțiuni pe un rând de tabel"); break; }
    const sub = t.closest(".ds-tabel-cutie")?.querySelector(".ds-tabel-subsol");
    if (!sub) pica.c.push("tabelul nu are subsol de 44 px");
    else if (Math.abs(h(sub) - 44) > 1) pica.c.push("subsolul tabelului are " + h(sub) + " px, nu 44");
  }
  if (c.tabele_vechi.length) pica.c.push(c.tabele_vechi.length + " tabel(e) care nu sunt tabelul DS: " + [...new Set(c.tabele_vechi)].join(", "));
  // liste de rânduri-buton (aceeași clasă repetată, ≥3, în afara tabelelor)
  const grupe = new Map();
  for (const bt of F.querySelectorAll("button")) {
    if (!vizibil(bt) || bt.closest("table") || bt.closest(".fereastra-antet")) continue;
    const cl = String(bt.className).split(" ")[0];
    if (!/(rand|item|lista|frand|nota|fisa)/i.test(cl)) continue;
    grupe.set(cl, (grupe.get(cl) || 0) + 1);
  }
  for (const [cl, n] of grupe) if (n >= 3) { c.liste_rand_buton.push(cl + " ×" + n); }
  c.liste_vechi = [...F.querySelectorAll("[class]")].filter((x) => vizibil(x) && !x.closest("table, .cautare-rez, .ds-tabel-cutie")
    && [...x.classList].some((k) => /(^|-)lista$|^zebra-lista$|^pf-lista$/.test(k) && !/^(ds-|cautare|firma-lista-fisiere)/.test(k))).map((x) => String(x.className).split(" ")[0]);
  c.liste_vechi = [...new Set(c.liste_vechi)];
  // rânduri repetate (≥3 frați cu aceeași etichetă și clasă, fiecare cu text și cu cel puțin o acțiune) în afara tabelului DS = listă de înregistrări
  for (const p of F.querySelectorAll("*")) {
    if (!vizibil(p) || p.closest("table, .cautare-rez, select, .ds-tabel-cutie, .ds-semnale, .ds-datorate, .ds-rezumat-detalii")) continue;
    const grupe2 = new Map();
    for (const k of p.children) { const cl = k.tagName + "." + String(k.className).split(" ")[0]; if (vizibil(k)) grupe2.set(cl, [...(grupe2.get(cl) || []), k]); }
    for (const [cl, ks] of grupe2) {
      if (ks.length < 3 || /(card|categorie|tab\b|-tab|pastila|optiune|nav-|op-|cab-|buton|alegere|camp|rap-|ds-)/i.test(cl)) continue;
      if (ks.every((k) => k.querySelector("button, a") && norm(k.innerText).length > 10 && h(k) > 30)) c.liste_vechi.push(cl.toLowerCase() + " ×" + ks.length);
    }
  }
  c.liste_vechi = [...new Set(c.liste_vechi)];
  if (c.liste_vechi.length) pica.c.push("listă de înregistrări care nu e tabelul DS: " + c.liste_vechi.join(", "));
  if (c.liste_rand_buton.length) pica.c.push("listă de înregistrări ca rânduri-buton, nu tabel DS: " + c.liste_rand_buton.join(", "));
  fapte.c = c;

  // ── d. avertismente și semnale ──────────────────────────────────────────────────────────────────────────────────────────────────────
  const d = { rezumat_ds: 0, semnale_ds: 0, carduri_vechi: 0, paragrafe_lungi: [] };
  for (const r of F.querySelectorAll(".ds-rezumat")) { if (!vizibil(r)) continue; d.rezumat_ds++; if (Math.abs(h(r) - 44) > 1) pica.d.push("card-rezumat de " + h(r) + " px, nu 44"); }
  for (const s of F.querySelectorAll(".ds-semnal")) { if (!vizibil(s)) continue; d.semnale_ds++; if (Math.abs(h(s) - 36) > 1) pica.d.push("semnal de " + h(s) + " px, nu 36"); }
  for (const r of F.querySelectorAll(".card-rezumat")) { if (!vizibil(r)) continue; d.rezumat_ds++; if (Math.abs(h(r) - 44) > 1) pica.d.push("card-rezumat de " + h(r) + " px, nu 44"); }
  const vechi = [...F.querySelectorAll(".cf-semnal, .caseta-info, .ecran-nota, .caseta-avertisment, .avertisment, .dec-avert-cap, .msg-info")].filter(vizibil);
  d.carduri_vechi = vechi.length;
  if (vechi.length) pica.d.push(vechi.length + " avertismente/semnale care nu sunt piese DS (" + [...new Set(vechi.map((x) => String(x.className).split(" ")[0]))].join(", ") + ")");
  for (const p of F.querySelectorAll("p, .pf-intro, .tip-micut, .ecran-nota, .camp-ajutor")) {
    if (!vizibil(p) || p.closest("[hidden], .ds-rezumat-detalii, .ds-semnal-detalii, details:not([open])")) continue;
    const txt = proprio(p);
    if (txt.length < 40) continue;
    const lh = parseFloat(getComputedStyle(p).lineHeight) || 20;
    if (h(p) > lh * 1.5) d.paragrafe_lungi.push(txt.slice(0, 50) + "…");
  }
  if (d.paragrafe_lungi.length) pica.d.push(d.paragrafe_lungi.length + " paragraf(e) explicativ(e) de peste un rând, nepliate: „" + d.paragrafe_lungi[0] + "”");
  fapte.d = d;

  // ── e. acțiuni în text ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
  const e = { in_text: [], casete_cu_actiuni: [] };
  for (const el of F.querySelectorAll("p button, p a[href], li button, textarea ~ button")) {
    if (!vizibil(el) || el.closest(".ds-actiuni-rand, .pf-intro, .fereastra-antet")) continue;
    const p = el.closest("p, li");
    if (p && proprio(p).length > 12) e.in_text.push(norm(el.innerText).slice(0, 30));
  }
  if (e.in_text.length) pica.e.push("acțiune în mijlocul unui text: " + [...new Set(e.in_text)].slice(0, 4).join(" · "));
  for (const el of F.querySelectorAll("[class*=galben], [class*=avert], [class*=caseta], [class*=atentie], .cf-extern-form")) {
    if (vizibil(el) && !el.matches(".ds-rezumat, .ds-semnal") && el.querySelector("button") && !el.closest(".ds-rezumat")) e.casete_cu_actiuni.push(String(el.className).split(" ")[0]);
  }
  if (e.casete_cu_actiuni.length) pica.e.push("acțiuni în casete colorate: " + [...new Set(e.casete_cu_actiuni)].join(", "));
  fapte.e = e;

  // ── f. titluri și texte ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
  const f = { titluri_cu_majuscule: [], fara_diacritice: [], plural: [], mesaje_duble: [] };
  for (const t of F.querySelectorAll("h1, h2, h3, h4, .pf-titlu, .pf-subtitlu, .ds-sectiune-titlu, [class*=-cap], [class*=titlu]")) {
    if (!vizibil(t) || t.closest(".fereastra-antet, table, button")) continue;
    const grup = t.matches(".ds-grup-titlu, .op-categorie > :first-child, [class*=grup-titlu]");
    const cs = getComputedStyle(t), txt = norm(t.innerText);
    const maj = cs.textTransform === "uppercase" || (txt.length > 3 && /[A-ZĂÂÎȘȚ]/.test(txt) && txt === txt.toUpperCase() && /[A-ZĂÂÎȘȚ]{3}/.test(txt));
    if (!maj) continue;
    if (grup) { if (Math.abs(parseFloat(cs.fontSize) - 14) > 0.5) pica.f.push("titlu de grup majuscule de " + cs.fontSize + ", nu 14 px: „" + txt.slice(0, 30) + "”"); }
    else f.titluri_cu_majuscule.push(txt.slice(0, 30));
  }
  if (f.titluri_cu_majuscule.length) pica.f.push("titluri de secțiune cu majuscule: " + [...new Set(f.titluri_cu_majuscule)].slice(0, 4).join(" · "));
  const text = norm(F.innerText);
  // numai etichete de interfață (nu numele firmelor sau datele din rânduri): butoane, etichete, capete de tabel, titluri de secțiune
  const interfata = [...F.querySelectorAll("button, label, th, h2, h3, h4, .ds-sectiune-titlu, .ds-grup-titlu")].filter((x) => vizibil(x) && !x.closest(".fereastra-antet") && !x.matches(".pf-titlu")).map((x) => norm(x.innerText)).join(" | ");
  const fara = interfata.match(/\b(Salariati|Fara|Tara|Inapoi|Inchide|Generare|Validare|Dupa|Pana|Cauta|Actiuni|Optiuni|Rezumat)\b/g);
  if (fara) { f.fara_diacritice = [...new Set(fara)]; pica.f.push("text fără diacritice: " + f.fara_diacritice.join(", ")); }
  const pl = text.match(/\b1 (note|facturi|salariați|firme|declarații|documente|articole|mișcări|operațiuni|conturi)\b|\b(\d+) (notă|factură|salariat|firmă|declarație|document|articol)\b(?! de)/gi);
  if (pl) {
    const rele = pl.filter((x) => { const m = x.match(/^(\d+) /); return m && ((m[1] === "1" && /(note|facturi|salariați|firme|declarații|documente|articole|mișcări|operațiuni|conturi)$/i.test(x)) || (m[1] !== "1" && /(notă|factură|salariat|firmă|declarație|document|articol)$/i.test(x))); });
    if (rele.length) { f.plural = rele; pica.f.push("pluralul nu urmează numărul: " + rele.slice(0, 3).join(", ")); }
  }
  const blocuri = [...F.querySelectorAll(".ds-rezumat-text, .ds-semnal-text, .card-text, .msg-info, .msg-eroare, .pf-intro")].filter(vizibil).map((x) => norm(x.innerText)).filter((x) => x.length > 20);
  const numar = {}; for (const x of blocuri) numar[x] = (numar[x] || 0) + 1;
  f.mesaje_duble = Object.keys(numar).filter((k) => numar[k] > 1);
  if (f.mesaje_duble.length) pica.f.push("același mesaj de mai multe ori: „" + f.mesaje_duble[0].slice(0, 50) + "”");
  fapte.f = f;

  // ── g. date, sume, perioade ─────────────────────────────────────────────────────────────────────────────────────────────────────────
  const g = { date_iso: [], sume_neformatate: [], perioade_ciudate: [], valori_goale: [] };
  g.date_iso = [...new Set(text.match(/\b\d{4}-\d{2}-\d{2}\b/g) || [])];
  if (g.date_iso.length) pica.g.push("date în format ISO pe ecran: " + g.date_iso.slice(0, 3).join(", "));
  g.sume_neformatate = [...new Set((text.match(/(?<![\d.,/-])\d{4,}\.\d{2}(?![\d.])|(?<![\d.])\d+,\d{3}(?![\d.,])/g) || []))];
  if (g.sume_neformatate.length) pica.g.push("sume care nu trec prin formatul unic (1.234,56): " + g.sume_neformatate.slice(0, 3).join(", "));
  g.valori_goale = [...new Set(text.match(/\b(undefined|null|NaN|None)\b/g) || [])];
  if (g.valori_goale.length) pica.g.push("valoare lipsă afișată brut: " + g.valori_goale.join(", "));
  const azi = text.match(/\b(azi|acum|ieri|mâine)\b(?! \d)/gi);
  g.azi_acum = azi ? [...new Set(azi.map((x) => x.toLowerCase()))] : [];
  fapte.g = g;

  // ── h. cota TVA și listele derulante ────────────────────────────────────────────────────────────────────────────────────────────────
  const hh = { liste_sub_7: [], alege: [], cota_tva_ca_lista: [] };
  for (const s of F.querySelectorAll("select")) {
    if (!vizibil(s) || s.classList.contains("ds-lista-sursa") || s.classList.contains("alegere-sursa")) continue;   // 15.1-E3: select-ul înlocuit de lista cu căutare sau de grupul de butoane e doar sursa valorii; omul vede lista / butoanele
    const opt = [...s.options].map((o) => norm(o.text));
    const nume = s.id || s.name || "(select)";
    if (opt.length < 7) hh.liste_sub_7.push(nume + " (" + opt.length + ")");
    if (opt.some((o) => /^[—–-]+\s*alege/i.test(o) || /^alege/i.test(o) || o === "")) hh.alege.push(nume);
    if (/tva|cota/i.test(nume) || opt.some((o) => /^\d+\s*%$/.test(o))) hh.cota_tva_ca_lista.push(nume);
  }
  if (hh.liste_sub_7.length) pica.h.push("listă derulantă cu sub 7 variante: " + hh.liste_sub_7.slice(0, 4).join(", "));
  if (hh.alege.length) pica.h.push("„— alege —” / opțiune goală în: " + hh.alege.slice(0, 4).join(", "));
  if (hh.cota_tva_ca_lista.length) pica.h.push("cota TVA e listă derulantă, nu grup de alegere: " + hh.cota_tva_ca_lista.join(", "));
  fapte.h = hh;

  return { fapte, pica };
})()
