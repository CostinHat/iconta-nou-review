// termene.js — restantele (termen trecut, nedepuse) si scadentele fiscale viitoare pe portofoliu (orizont 60 zile).
// Grupate pe data-termen; click pe o declaratie -> firmele; click pe o firma -> fisa firmei.

import { api, cate, dupaNumar, dataRo, esc } from "../api.js?v=7396e03327";
import { tabelDS } from "../ds_piese.js?v=e115d72f0f";   // [15.1-E3] lista scadențelor pe tabelul DS
import { deschideFirma } from "./firme.js?v=da8050724c";   // [P2] refolosim fisa firmei (firme.js:146), nu ruta noua; ?v=7 aliniat cu cabinet/asistent ca sa nu apara o a doua instanta a modulului

// [P1c] anul se afiseaza pe eticheta de perioada DOAR cand difera de asta (fereastra de 60z poate trece in an+1).
const ANUL_CURENT = new Date().getFullYear();

function etichetaZile(z) {
  if (z < 0) return `restanță de ${cate(-z, "zi", "zile")}`;   // [719, 14.3] termenul a trecut și declarația nu e depusă: apare, prima
  if (z === 0) return "azi";
  if (z === 1) return "mâine";
  return `în ${cate(z, "zi", "zile")}`;
}

// [P1c] "iun" cand perioada e in anul curent, "iun 2027" cand difera. Decizie de continut (DECIZII 23.07), nu format DS.
function etichetaPerioada(perioada, an) {
  return an && an !== ANUL_CURENT ? `${perioada} ${an}` : perioada;
}

export async function randeazaTermene(corp, nav) {
  corp.innerHTML = `<p class="ecran-nota">Se calculează scadențele…</p>`;
  let date = { grupuri: [] };
  try {
    date = await api.get("/termene");
  } catch {
    corp.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca termenele.</p>`;
    return;
  }
  const grupuri = date.grupuri || [];
  const neeval = date.neevaluate || [];

  corp.innerHTML = `
    <p class="mig-intro">Scadențele care urmează în următoarele 60 de zile, pe dată.</p>
    <div id="term-zona" data-zona-derulare><div id="term-lista"></div></div>
  `;   // [lotul 14, 687] lista scadențelor derulează în zona ei; introducerea rămâne fixă sus
  const zona = corp.querySelector("#term-zona");
  const lista = corp.querySelector("#term-lista");
  if (grupuri.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio scadență în următoarele 60 de zile și nicio restanță.</div>`;
    randeazaNeevaluate(zona, neeval);   // [T1] chiar si fara scadente, firmele neevaluate NU dispar tacut
    return;
  }

  // [15.1-E3, 7] lista scadențelor = tabelul DS: Termen · Declarație · Firme · Stare (pastila) · butonul XS „Deschide” pe fiecare rând (nu rând apăsabil cu „Click pe o declarație”)
  const randuri = grupuri.flatMap((g) => g.items.map((it) => ({
    celule: { termen: dataRo(g.termen), decl: (it.tip || "").toUpperCase(),
      firme: cate(it.nr_firme, "firmă", "firme") + (it.incert ? " (posibil — perioadă deschisă)" : "") },   // [P4] perioada DESCHISĂ -> D390 posibil, nu ferm
    stare: { text: etichetaZile(g.zile), ton: g.zile < 0 ? "eroare" : g.zile <= 7 ? "avertisment" : "info" },   // și restanțele (zile negative)
    actiuni: [{ eticheta: "Deschide", laClic: () => nav.deschide("Detaliu termen", (cc, nn) => detaliuTermen(cc, nn, g, it)), faraActiune: "deschide firmele cu acest termen" }] })));  // [p122_nav_stiva]
  tabelDS(lista, { coloane: [{ cheie: "termen", titlu: "Termen" }, { cheie: "decl", titlu: "Declarație" }, { cheie: "firme", titlu: "Firme" }, { tip: "stare", titlu: "Stare" }, { tip: "actiuni", titlu: "" }],
    randuri, subsol: cate(randuri.length, "scadență", "scadențe") });

  randeazaNeevaluate(zona, neeval);   // [T1] gri cu temei, sub scadente
}

// [T1] firmele care nu au putut fi evaluate — afisate explicit (gri cu temei), nu omise.
// Reutilizeaza clasele DS existente (.mig-intro / .mig-lista / .mig-frand), fara regula noua.
function randeazaNeevaluate(corp, neeval) {
  if (!neeval || !neeval.length) return;
  const bloc = document.createElement("div");
  bloc.innerHTML = `
    <p class="mig-intro">${neeval.length === 1 ? "O firmă nu a putut fi evaluată" : cate(neeval.length, "firmă", "firme") + " nu au putut fi evaluate"} — apar aici ca să nu dispară tăcut din listă.</p>
    <div class="mig-lista"></div>
  `;
  const l = bloc.querySelector(".mig-lista");
  neeval.forEach((f) => {
    const rand = document.createElement("div");
    rand.className = "mig-frand";
    rand.style.cursor = "default";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">${esc(f.cauza)}</div>
      </div>
    `;
    l.appendChild(rand);
  });
  corp.appendChild(bloc);
}

function detaliuTermen(corp, nav, grup, item) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${(item.tip||"").toUpperCase()}</b> · scadență ${dataRo(grup.termen, "lung")} · <b>${item.nr_firme}</b> ${dupaNumar(item.nr_firme, "firmă", "firme")}</p>
    <div class="mig-lista" id="term-firme"></div>
  `;

  const lista = corp.querySelector("#term-firme");
  item.firme.forEach((f) => {
    const rand = document.createElement("div");
    rand.className = "mig-frand";
    rand.style.cursor = "pointer";   // [P2] rand-firma -> fisa firmei (nu mai e fundatura)
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${esc(f.nume)}</div>
        <div class="mig-frand-sub">perioada ${etichetaPerioada(f.perioada, item.an)}${f.inainte_de_preluare ? " · înainte de preluare în iConta.eu" : ""}</div>
      </div>
    `;
    // [P2] tenant_id -> id; deschideFirma->meniuFirma cere {id, nume, cui, tip_firma} (contract strict, meniuFirma:241).
    // tip_firma lipsea din payload -> t.tip_firma.toLowerCase() crapa la randarea fisei. Adaugat in /termene.
    rand.addEventListener("click", () => deschideFirma({ id: f.tenant_id, nume: f.nume, cui: f.cui, tip_firma: f.tip_firma, regim_contabil: f.regim_contabil }, nav));
    lista.appendChild(rand);
  });
}
