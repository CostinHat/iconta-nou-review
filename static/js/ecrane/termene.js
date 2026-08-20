// termene.js — scadente fiscale viitoare pe portofoliu (orizont 60 zile).
// Grupate pe data-termen; click pe o declaratie -> firmele; click pe o firma -> fisa firmei.

import { api, dataRo } from "../api.js?v=a7f9e80ae0";
import { deschideFirma } from "./firme.js?v=474caf58f0";   // [P2] refolosim fisa firmei (firme.js:146), nu ruta noua; ?v=7 aliniat cu cabinet/asistent ca sa nu apara o a doua instanta a modulului

// [P1c] anul se afiseaza pe eticheta de perioada DOAR cand difera de asta (fereastra de 60z poate trece in an+1).
const ANUL_CURENT = new Date().getFullYear();

function etichetaZile(z) {
  if (z === 0) return "azi";
  if (z === 1) return "mâine";
  return `în ${z} zile`;
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
    corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca termenele.</p>`;
    return;
  }
  const grupuri = date.grupuri || [];
  const neeval = date.neevaluate || [];

  corp.innerHTML = `
    <p class="mig-intro">Scadențele care urmează în următoarele 60 de zile, grupate pe dată. Click pe o declarație ca să vezi firmele.</p>
    <div id="term-lista"></div>
  `;
  const lista = corp.querySelector("#term-lista");
  if (grupuri.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio scadență în următoarele 60 de zile.</div>`;
    randeazaNeevaluate(corp, neeval);   // [T1] chiar si fara scadente, firmele neevaluate NU dispar tacut
    return;
  }

  grupuri.forEach((g) => {
    const urgent = g.zile <= 7;
    const bloc = document.createElement("div");
    bloc.className = "term-grup";
    bloc.innerHTML = `
      <div class="term-data ${urgent ? "term-urgent" : ""}">
        <span class="term-data-zi">${dataRo(g.termen, "lung")}</span>
        <span class="term-data-cat">${etichetaZile(g.zile)}</span>
      </div>
      <div class="term-items"></div>
    `;
    const cont = bloc.querySelector(".term-items");
    g.items.forEach((it) => {
      const incert = !!it.incert;   // [P4] perioada DESCHISA -> D390 posibil, nu ferm
      const rand = document.createElement("button");
      rand.className = "term-item";
      rand.innerHTML = `
        <span class="term-tip">${(it.tip||"").toUpperCase()}</span>
        <span class="term-nr">${incert ? '<span class="cab-pct pct-gri" title="Perioadă deschisă — D390 se datorează doar dacă apar operațiuni intracomunitare în lună"></span>' : ""}${it.nr_firme} ${it.nr_firme === 1 ? "firmă" : "firme"}${incert ? '<span class="term-posibil">posibil</span>' : ""}</span>
        <svg class="term-chev" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>
      `;
      rand.addEventListener("click", () => nav.deschide("Detaliu termen", (cc, nn) => detaliuTermen(cc, nn, g, it)));  // [p122_nav_stiva]
      cont.appendChild(rand);
    });
    lista.appendChild(bloc);
  });

  randeazaNeevaluate(corp, neeval);   // [T1] gri cu temei, sub scadente
}

// [T1] firmele care nu au putut fi evaluate — afisate explicit (gri cu temei), nu omise.
// Reutilizeaza clasele DS existente (.mig-intro / .mig-lista / .mig-frand), fara regula noua.
function randeazaNeevaluate(corp, neeval) {
  if (!neeval || !neeval.length) return;
  const bloc = document.createElement("div");
  bloc.innerHTML = `
    <p class="mig-intro">Nu am putut evalua ${neeval.length} ${neeval.length === 1 ? "firmă" : "firme"} — apar aici ca să nu dispară tăcut din listă.</p>
    <div class="mig-lista"></div>
  `;
  const l = bloc.querySelector(".mig-lista");
  neeval.forEach((f) => {
    const rand = document.createElement("div");
    rand.className = "mig-frand";
    rand.style.cursor = "default";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${f.nume}</div>
        <div class="mig-frand-sub">${f.cauza}</div>
      </div>
    `;
    l.appendChild(rand);
  });
  corp.appendChild(bloc);
}

function detaliuTermen(corp, nav, grup, item) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${(item.tip||"").toUpperCase()}</b> · scadență ${dataRo(grup.termen, "lung")} · <b>${item.nr_firme}</b> ${item.nr_firme === 1 ? "firmă" : "firme"}</p>
    <div class="mig-lista" id="term-firme"></div>
  `;

  const lista = corp.querySelector("#term-firme");
  item.firme.forEach((f) => {
    const rand = document.createElement("div");
    rand.className = "mig-frand";
    rand.style.cursor = "pointer";   // [P2] rand-firma -> fisa firmei (nu mai e fundatura)
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${f.nume}</div>
        <div class="mig-frand-sub">perioada ${etichetaPerioada(f.perioada, item.an)}</div>
      </div>
    `;
    // [P2] tenant_id -> id; deschideFirma->meniuFirma cere {id, nume, cui, tip_firma} (contract strict, meniuFirma:241).
    // tip_firma lipsea din payload -> t.tip_firma.toLowerCase() crapa la randarea fisei. Adaugat in /termene.
    rand.addEventListener("click", () => deschideFirma({ id: f.tenant_id, nume: f.nume, cui: f.cui, tip_firma: f.tip_firma, regim_contabil: f.regim_contabil }, nav));
    lista.appendChild(rand);
  });
}
