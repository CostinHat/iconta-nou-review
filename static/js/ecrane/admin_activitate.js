// admin_activitate.js — Admin iConta: activitate + business cabinete (doar superadmin).
// Sumar + lista cu firme/angajati/recomandari/actiuni, suspenda/reactiveaza, click -> timeline.
import { api } from "../api.js";

function fmtData(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  const zz = String(d.getDate()).padStart(2, "0");
  const ll = String(d.getMonth() + 1).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  return `${zz}/${ll}/${d.getFullYear()} ${hh}:${mm}`;
}

export async function randeazaAdminActivitate(corp, nav) {
  const f = corp.closest(".fereastra");
  if (f) f.classList.add("fer-larg-simplu");
  corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
  await randeaza(corp, nav);
}

async function randeaza(corp, nav) {
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
      <div class="mig-gol">Niciun cabinet încă.</div>`;
    return;
  }

  const randuri = cabinete.map((c, i) => {
    const stare = c.activ ? "" : `<span class="mig-stare mig-rosu">suspendat</span>`;
    return `
      <div class="pf-frand" data-zebra="${i % 2}">
        <div class="pf-frand-text" data-i="${i}" style="cursor:pointer">
          <div class="pf-frand-nume">${(c.nume || "—")}</div>
          <div class="pf-frand-sub">${c.nr_firme ?? 0} firme · ${c.nr_angajati ?? 0} angajați · ${c.nr_facturi ?? 0} facturi emise · ${c.nr_declaratii ?? 0} declarații depuse · ${c.nr_recomandari ?? 0} recomandări · ultima activitate: ${fmtData(c.ultima_activitate)}</div>
        </div>
        ${stare}
        <button class="btn" data-toggle="${i}" style="background:#fff;color:#111;border:1px solid #ddd;margin-left:10px">
          ${c.activ ? "Suspendă" : "Reactivează"}
        </button>
      </div>`;
  }).join("");

  corp.innerHTML = `
    <h2 class="pf-titlu">Cabinete</h2>
    <div class="pf-lista" id="ac-lista">${randuri}</div>
    <div id="ac-detaliu"></div>
  `;

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
        ? `Suspenzi accesul cabinetului "${c.nume}"? Login-ul se taie instant, datele rămân.`
        : `Reactivezi accesul cabinetului "${c.nume}"?`;
      if (!confirm(mesaj)) return;
      try {
        await api.post(`/admin/cabinete/${c.id}/${ruta}`, {});
        corp.innerHTML = `<p class="ecran-nota">Se actualizează...</p>`;
        await randeaza(corp, nav);
      } catch {
        alert("A apărut o eroare.");
      }
    });
  });
}

async function deschideTimeline(corp, cabinet) {
  const zona = corp.querySelector("#ac-detaliu");
  zona.innerHTML = `<p class="ecran-nota">Se încarcă istoricul...</p>`;
  let activitate = [];
  try {
    const r = await api.get(`/admin/activitate/cabinet/${cabinet.id}`);
    activitate = (r && r.activitate) || [];
  } catch {}
  if (!activitate.length) {
    zona.innerHTML = `<div class="mig-gol">Niciun eveniment înregistrat încă.</div>`;
    return;
  }
  const linii = activitate.map((a) => `
    <div class="sol-rand sol-cabinet">
      <div class="sol-mesaj">${(a.actiune || "")}</div>
      <div class="sol-meta">${(a.nume || "")} ${(a.prenume || "")} · ${fmtData(a.created_at)}</div>
    </div>`).join("");
  zona.innerHTML = `
    <div class="pov-card">
      <div class="sol-fir" style="max-height:480px">${linii}</div>
    </div>`;
}
