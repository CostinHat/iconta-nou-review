// admin_activitate.js — Admin iConta: activitate + business cabinete (doar superadmin).
// Sumar + lista cu firme/angajati/recomandari/actiuni, suspenda/reactiveaza, click -> timeline.
import { api, dataRo, confirmaCaseta, esc } from "../api.js";  /* audit_cab_lot2_v1 + esc_nc27 */


export async function randeazaAdminActivitate(corp, nav) {
  const f = corp.closest(".fereastra");
  if (f) f.classList.add("fer-larg-simplu");
  corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
  await randeaza(corp, nav);
}

async function randeaza(corp, nav) {
  if (nav && nav.setInapoi) nav.setInapoi(undefined);
  let cabinete = [];
  try {
    const r = await api.get("/admin/activitate/cabinete");
    cabinete = (r && r.cabinete) || [];
  } catch {
    corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca activitatea.</p>`;
    return;
  }
  if (!cabinete.length) {
    corp.innerHTML = `
      <h2 class="pf-titlu">Cabinete</h2>
      <div class="stare-goala">Niciun cabinet încă. Apar automat aici când se înregistrează primul (self-service).</div>`;
    return;
  }

  const randuri = cabinete.map((c, i) => {
    const stare = c.activ ? "" : `<span class="mig-stare mig-rosu">suspendat</span>`;
    return `
      <div class="pf-frand" data-zebra="${i % 2}">
        <div class="pf-frand-text" data-i="${i}" style="cursor:pointer">
          <div class="pf-frand-nume">${esc(c.nume || "—")}</div>
          <div class="pf-frand-sub">${c.nr_firme ?? 0} firme · ${c.nr_angajati ?? 0} angajați · ${c.nr_facturi ?? 0} facturi emise · ${c.nr_declaratii ?? 0} declarații depuse · ${c.nr_recomandari ?? 0} recomandări · ultima activitate: ${dataRo(c.ultima_activitate, "cu_ora")}</div>
        </div>
        ${stare}
        <button class="${c.activ ? 'buton-sters' : 'buton-secundar'}" data-toggle="${i}" style="margin-left:10px">
          ${c.activ ? "Suspendă" : "Reactivează"}
        </button>
      </div>`;
  }).join("");

  corp.innerHTML = `
    <h2 class="pf-titlu">Cabinete</h2>
    <label class="camp" style="max-width:340px;margin-bottom:10px"><span class="camp-eticheta">Caut\u0103 cabinet</span><input type="text" id="ac-cauta" class="camp-input" placeholder="nume cabinet"></label>
    <div class="pf-lista zebra-lista" id="ac-lista">${randuri}</div>
    <div id="ac-detaliu"></div>
  `;

  corp.querySelector("#ac-cauta").addEventListener("input", (e) => {  // [ac_cauta] filtrare live
    const q = e.target.value.trim().toLowerCase();
    corp.querySelectorAll("#ac-lista .pf-frand").forEach((rand, i) => {
      rand.style.display = !q || (cabinete[i].nume || "").toLowerCase().includes(q) ? "" : "none";
    });
  });
  corp.querySelectorAll("#ac-lista [data-i]").forEach((el) => {
    el.addEventListener("click", () => {
      const c = cabinete[Number(el.dataset.i)];
      deschideTimeline(corp, c);
    });
  });

  corp.querySelectorAll("#ac-lista [data-toggle]").forEach((btn) => {
    btn.addEventListener("click", async (ev) => {
      ev.stopPropagation();
      const c = cabinete[Number(btn.dataset.toggle)];
      const ruta = c.activ ? "suspenda" : "reactiveaza";
      const mesaj = c.activ
        ? `Suspenzi accesul cabinetului "${esc(c.nume)}"? Login-ul se taie instant, datele rămân.`
        : `Reactivezi accesul cabinetului "${esc(c.nume)}"?`;
      confirmaCaseta(btn.parentElement || btn, mesaj, async () => {  // audit_cab_lot2_v1
      try {
        await api.post(`/admin/cabinete/${c.id}/${ruta}`, {});
        corp.innerHTML = `<p class="ecran-nota">Se actualizează...</p>`;
        await randeaza(corp, nav);
      } catch {
        corp.querySelectorAll(".msg-eroare").forEach((x) => x.remove());
        corp.insertAdjacentHTML("afterbegin", '<p class="msg-eroare">A apărut o eroare. Reîncearcă.</p>');
      }
      }, { textOk: c.activ ? "Suspendă" : "Reactivează" });
    });
  });
}

function actiuneRo(a) {  // [aa_ro] jurnalul pe romaneste; necunoscutele raman brute
  a = a || "";
  if (a === "login") return "Autentificare";
  const REGULI = [
    ["control-fiscal", "A deschis Control fiscal"], ["eu/competente", "A deschis competentele"],
    ["eu/cabinet", "A deschis cabinetul"], ["recomanda", "A deschis Recomanda"],
    ["asistenti/echipa", "A deschis echipa"], ["facturi", "A lucrat in Facturi"],
    ["declaratii", "A lucrat in Declaratii"], ["salariati", "A lucrat in Salariati"],
    ["migrare", "A lucrat in Migrare"], ["stocuri", "A lucrat in Stocuri"],
    ["banca", "A lucrat in Banca"], ["portal", "A folosit portalul"],
    ["raportari", "A folosit Raporteaza"], ["termene", "A deschis Termene"],
    ["anunturi", "A citit anunturile"], ["notificari", "A citit notificarile"],
    ["educatie", "A deschis Educatie pe tipare"], ["patru-ochi", "A deschis patru-ochi"],
    ["asistenti", "A deschis echipa"], ["coada", "A lucrat in coada de validare"],
    ["plan-conturi", "A deschis planul de conturi"], ["firma-profil", "A deschis profilul firmei"],
    ["capacitate", "A deschis Capacitate"], ["permisiuni", "A deschis permisiunile"],
    ["consolidare", "A deschis Consolidare"],
    ["tenants", "A deschis o firma"], ["recomanda", "A deschis Recomanda"],
  ];
  for (const [k, t] of REGULI) if (a.includes(k)) return t;
  return a;
}

async function deschideTimeline(corp, cabinet) {
  const zona = corp.querySelector("#ac-detaliu");
  zona.innerHTML = `<p class="ecran-nota">Se încarcă istoricul...</p>`;
  let activitate = [];
  try {
    const r = await api.get(`/admin/activitate/cabinet/${cabinet.id}`);
    activitate = (r && r.activitate) || [];
  } catch (e) {
    zona.innerHTML = `<div class="stare-goala">Nu am putut încărca istoricul cabinetului. Reîncearcă.</div>`;
    return;
  }
  if (!activitate.length) {
    zona.innerHTML = `<div class="stare-goala">Niciun eveniment înregistrat încă. Apar aici pe măsură ce cabinetele lucrează.</div>`;
    return;
  }
  // [aa_grupe] DS cap.2: nimic vizibil decat la selectie - jurnal grupat pe categorii, butoane toggle
  const grupe = {};
  activitate.forEach((a) => {
    const t = actiuneRo(a.actiune);
    (grupe[t] = grupe[t] || []).push(a);
  });
  const butoane = Object.keys(grupe).map((t, i) =>
    `<button class="buton-secundar buton-mic" data-grup="${i}">${esc(t)} (${grupe[t].length})</button>`).join(" ");
  const c = cabinet;  // [aa_rezumat] cifrele cabinetului, vizibile in capul detaliului
  zona.innerHTML = `
    <div class="panou" style="margin-top:14px">
      <div class="pf-frand-nume" style="margin-bottom:4px">${esc(c.nume || "")}</div>
      <div class="pf-frand-sub" style="margin-bottom:10px">${c.nr_firme ?? 0} firme \u00b7 ${c.nr_angajati ?? 0} angaja\u021bi \u00b7 ${c.nr_facturi ?? 0} facturi emise \u00b7 ${c.nr_declaratii ?? 0} declara\u021bii \u00b7 ${c.nr_recomandari ?? 0} recomand\u0103ri</div>
      <div style="display:flex;flex-wrap:wrap;gap:6px">${butoane}</div>
      <div id="aa-evenimente"></div>
    </div>`;
  const chei = Object.keys(grupe);
  let deschis = null;
  zona.querySelectorAll("[data-grup]").forEach((b) => b.addEventListener("click", () => {
    const i = Number(b.dataset.grup);
    const ev = zona.querySelector("#aa-evenimente");
    zona.querySelectorAll("[data-grup]").forEach((x) => x.classList.remove("buton-activ"));  // DS cap.1: fratii se inchid
    if (deschis === i) { deschis = null; ev.innerHTML = ""; return; }
    deschis = i; b.classList.add("buton-activ");
    ev.innerHTML = `<div class="sol-fir" style="margin-top:10px">${grupe[chei[i]].map((a) => `
      <div class="sol-rand sol-cabinet">
        <div class="sol-meta">${esc(a.nume || "")} ${esc(a.prenume || "")} \u00b7 ${dataRo(a.created_at, "cu_ora")}</div>
      </div>`).join("")}</div>`;
  }));
}

// audit_cab_lot1_v1

// audit_cab_lot2_v1
