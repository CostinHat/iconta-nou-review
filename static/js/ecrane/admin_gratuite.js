// admin_gratuite.js — Admin iConta: conturi gratuite (facturare, fara cabinet).
import { api, dataRo, confirmaCaseta, esc } from "../api.js";  /* audit_cab_lot2_v1 + esc_nc27 */
export async function randeazaAdminGratuite(corp, nav) {
  const f = corp.closest(".fereastra");
  if (f) f.classList.add("fer-larg-simplu");
  corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
  await randeaza(corp, nav);
}
async function randeaza(corp, nav) {
  let conturi = [], coliziuni = [];
  try {
    const [r, k] = await Promise.all([  // [F186] conturi + coliziuni CUI, o singura runda
      api.get("/admin/activitate/conturi-gratuite"),
      api.get("/admin/coliziuni-cui").catch(() => ({})),
    ]);
    conturi = (r && r.conturi) || [];
    coliziuni = (k && k.coliziuni) || [];
  } catch {
    corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca conturile.</p>`;
    return;
  }
  // [F186] bloc PERSISTENT de coliziuni CUI (gratuit + cabinet, ambele active) — deasupra listei.
  // Suspendarea foloseste ruta existenta pe contul gratuit; nimic automat (GDPR signal-not-block).
  const colizBloc = coliziuni.length ? `
    <div class="dec-avert" style="margin-bottom:18px">
      <div class="dec-avert-cap">Coliziuni CUI — ${coliziuni.length} ${coliziuni.length === 1 ? "cont gratuit" : "conturi gratuite"} pe un CUI aflat deja sub cabinet</div>
      <p class="ecran-nota" style="margin:4px 0 10px">Același CUI are cont gratuit <b>și</b> firmă de cabinet, ambele active — risc de emitere dublă (numerotare divergentă, e-Factură din două surse). Poți suspenda contul gratuit; nu se întâmplă nimic automat.</p>
      <div class="pf-lista zebra-lista" id="ag-coliz">${coliziuni.map((k, i) => `
        <div class="pf-frand" data-zebra="${i % 2}">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">${esc(k.gratuit_nume || "—")}${k.gratuit_cui ? " · " + esc(k.gratuit_cui) : ""}</div>
            <div class="pf-frand-sub">gratuit: ${k.gratuit_nr_facturi ?? 0} facturi emise · creat ${dataRo(k.gratuit_creat, "cu_ora")} — firma: <b>${esc(k.cabinet_nume || "—")}</b> · cabinet: <b>${esc(k.firm_nume || "—")}</b></div>
          </div>
          <button class="buton-sters" data-coliz="${i}" style="margin-left:10px">Suspendă gratuitul</button>
        </div>`).join("")}</div>
    </div>` : "";
  if (!conturi.length) {
    corp.innerHTML = colizBloc + `
      <h2 class="pf-titlu">Conturi gratuite</h2>
      <div class="stare-goala">Niciun cont gratuit încă.</div>`;
    _wireColiz(corp, nav, coliziuni);
    return;
  }
  const randuri = conturi.map((c, i) => {
    const stare = c.activ ? "" : `<span class="mig-stare mig-rosu">suspendat</span>`;
    return `
      <div class="pf-frand" data-zebra="${i % 2}">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(c.nume || "—")}${c.cui ? " · " + esc(c.cui) : ""}</div>
          <div class="pf-frand-sub">${c.nr_useri ?? 0} utilizatori · ${c.nr_facturi ?? 0} facturi emise · creat: ${dataRo(c.creat_la, "cu_ora")} · ultima activitate: ${dataRo(c.ultima_activitate, "cu_ora")}</div>
        </div>
        ${stare}
        <button class="${c.activ ? 'buton-sters' : 'buton-secundar'}" data-toggle="${i}" style="margin-left:10px">
          ${c.activ ? "Suspendă" : "Reactivează"}
        </button>
      </div>`;
  }).join("");
  corp.innerHTML = colizBloc + `
    <h2 class="pf-titlu">Conturi gratuite</h2>
    <div class="pf-lista zebra-lista" id="ag-lista">${randuri}</div>
  `;
  _wireColiz(corp, nav, coliziuni);
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
      if (c.activ) confirmaCaseta(btn.parentElement || btn, `Suspenzi contul ${esc(c.nume)}? Utilizatorii nu se vor mai putea loga.`, fa, { textOk: "Suspendă" });
      else fa();
    });
  });
}

// [F186] wiring butoane "Suspendă gratuitul" din blocul de coliziuni — reutilizeaza ruta de suspendare
// pe contul GRATUIT (partea care poate emite dublu). Confirmare inainte, apoi re-randare (coliziunea dispare).
function _wireColiz(corp, nav, coliziuni) {
  corp.querySelectorAll("[data-coliz]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const k = coliziuni[parseInt(btn.dataset.coliz)];
      const fa = async () => {
        try {
          await api.post(`/admin/conturi-gratuite/${k.gratuit_id}/suspenda`, {});
          await randeaza(corp, nav);
        } catch {
          corp.querySelectorAll(".msg-eroare").forEach((x) => x.remove());
          corp.insertAdjacentHTML("afterbegin", '<p class="msg-eroare">Operațiunea a eșuat. Reîncearcă.</p>');
        }
      };
      confirmaCaseta(btn.parentElement || btn, `Suspenzi contul gratuit ${esc(k.gratuit_nume)}? Utilizatorii nu se vor mai putea loga.`, fa, { textOk: "Suspendă" });
    });
  });
}

// audit_cab_lot1_v1

// audit_cab_lot2_v1
