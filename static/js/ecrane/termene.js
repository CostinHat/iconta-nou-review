// termene.js — scadente fiscale viitoare pe portofoliu (orizont 60 zile).
// Grupate pe data-termen; fiecare declaratie arata nr firme; click -> lista firmelor.

import { api } from "../api.js";

const LUNI = ["ianuarie","februarie","martie","aprilie","mai","iunie",
              "iulie","august","septembrie","octombrie","noiembrie","decembrie"];

function dataLunga(iso) {
  const p = iso.split("-");
  if (p.length !== 3) return iso;
  return `${parseInt(p[2])} ${LUNI[parseInt(p[1]) - 1]}`;
}

function etichetaZile(z) {
  if (z === 0) return "azi";
  if (z === 1) return "mâine";
  return `în ${z} zile`;
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

  corp.innerHTML = `
    <p class="mig-intro">Scadențele care urmează în următoarele 60 de zile, grupate pe dată. Click pe o declarație ca să vezi firmele.</p>
    <div id="term-lista"></div>
  `;
  const lista = corp.querySelector("#term-lista");
  if (grupuri.length === 0) {
    lista.innerHTML = `<div class="stare-goala">Nicio scadență în următoarele 60 de zile.</div>`;
    return;
  }

  grupuri.forEach((g) => {
    const urgent = g.zile <= 7;
    const bloc = document.createElement("div");
    bloc.className = "term-grup";
    bloc.innerHTML = `
      <div class="term-data ${urgent ? "term-urgent" : ""}">
        <span class="term-data-zi">${dataLunga(g.termen)}</span>
        <span class="term-data-cat">${etichetaZile(g.zile)}</span>
      </div>
      <div class="term-items"></div>
    `;
    const cont = bloc.querySelector(".term-items");
    g.items.forEach((it) => {
      const rand = document.createElement("button");
      rand.className = "term-item";
      rand.innerHTML = `
        <span class="term-tip">${(it.tip||"").toUpperCase()}</span>
        <span class="term-nr">${it.nr_firme} ${it.nr_firme === 1 ? "firmă" : "firme"}</span>
        <svg class="term-chev" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>
      `;
      rand.addEventListener("click", () => nav.deschide("Detaliu termen", (cc, nn) => detaliuTermen(cc, nn, g, it)));  // [p122_nav_stiva]
      cont.appendChild(rand);
    });
    lista.appendChild(bloc);
  });
}

function detaliuTermen(corp, nav, grup, item) {
  corp.innerHTML = `
    <p class="mig-intro"><b>${(item.tip||"").toUpperCase()}</b> · scadență ${dataLunga(grup.termen)} · <b>${item.nr_firme}</b> ${item.nr_firme === 1 ? "firmă" : "firme"}</p>
    <div class="mig-lista" id="term-firme"></div>
  `;

  const lista = corp.querySelector("#term-firme");
  item.firme.forEach((f) => {
    const rand = document.createElement("div");
    rand.className = "mig-frand";
    rand.style.cursor = "default";
    rand.innerHTML = `
      <div class="mig-frand-text">
        <div class="mig-frand-nume">${f.nume}</div>
        <div class="mig-frand-sub">perioada ${f.perioada}</div>
      </div>
    `;
    lista.appendChild(rand);
  });
}
