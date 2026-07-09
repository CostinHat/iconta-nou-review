// admin_gratuite.js — Admin iConta: conturi gratuite (facturare, fara cabinet).
import { api, confirmaCaseta } from "../api.js";  /* audit_cab_lot2_v1 */
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
export async function randeazaAdminGratuite(corp, nav) {
  const f = corp.closest(".fereastra");
  if (f) f.classList.add("fer-larg-simplu");
  corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
  await randeaza(corp, nav);
}
async function randeaza(corp, nav) {
  let conturi = [];
  try {
    const r = await api.get("/admin/activitate/conturi-gratuite");
    conturi = (r && r.conturi) || [];
  } catch {
    corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca conturile.</p>`;
    return;
  }
  if (!conturi.length) {
    corp.innerHTML = `
      <h2 class="pf-titlu">Conturi gratuite</h2>
      <div class="mig-gol">Niciun cont gratuit încă.</div>`;
    return;
  }
  const randuri = conturi.map((c, i) => {
    const stare = c.activ ? "" : `<span class="mig-stare mig-rosu">suspendat</span>`;
    return `
      <div class="pf-frand" data-zebra="${i % 2}">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${(c.nume || "—")}${c.cui ? " · " + c.cui : ""}</div>
          <div class="pf-frand-sub">${c.nr_useri ?? 0} utilizatori · ${c.nr_facturi ?? 0} facturi emise · creat: ${fmtData(c.creat_la)} · ultima activitate: ${fmtData(c.ultima_activitate)}</div>
        </div>
        ${stare}
        <button class="${c.activ ? 'buton-sters' : 'buton-secundar'}" data-toggle="${i}" style="margin-left:10px">
          ${c.activ ? "Suspendă" : "Reactivează"}
        </button>
      </div>`;
  }).join("");
  corp.innerHTML = `
    <h2 class="pf-titlu">Conturi gratuite</h2>
    <div class="pf-lista" id="ag-lista">${randuri}</div>
  `;
  corp.querySelectorAll("[data-toggle]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const c = conturi[parseInt(btn.dataset.toggle)];
      const ruta = c.activ ? "suspenda" : "reactiveaza";
      const fa = async () => {  // audit_cab_lot2_v1
        try {
          await api.post(`/admin/conturi-gratuite/${c.id}/${ruta}`, {});
          await randeaza(corp, nav);
        } catch {
          corp.querySelectorAll(".msg-eroare").forEach((x) => x.remove());
          corp.insertAdjacentHTML("afterbegin", '<p class="msg-eroare">Operațiunea a eșuat. Reîncearcă.</p>');
        }
      };
      if (c.activ) confirmaCaseta(btn.parentElement || btn, `Suspenzi contul ${c.nume}? Utilizatorii nu se vor mai putea loga.`, fa, { textOk: "Suspendă" });
      else fa();
    });
  });
}

// audit_cab_lot1_v1

// audit_cab_lot2_v1
