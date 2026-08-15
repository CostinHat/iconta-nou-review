// [ecran_mf_v1 14.08.2026] Registrul mijloacelor fixe al firmei — ecranul de gestiune care lipsea.
// Pana acum MF existau doar in DB (import la migrare + butonul "Genereaza amortizarea"); nu se
// puteau vedea, casa sau reevalua din interfata — iar casarea/reevaluarea cereau un mijloc_fix_id
// pe care niciun ecran nu-l arata (casarea din formular dadea 422 garantat). Aici e sursa acelui id
// + doua actiuni directe: casare (POST nota-inventariere) si reevaluare (POST reevaluare-imobilizare).
import { api, esc, arataMesaj, confirmaCaseta, bani, dataRo } from "../api.js?v=a0acf0511a";

export async function ecranMijloace(corp, nav, tenantId, opt = {}) {
  const azi = new Date().toISOString().slice(0, 10);

  async function incarca() {
    corp.innerHTML = `<h2 class="pf-titlu">Mijloace fixe</h2><div class="ecran-nota">Se încarcă registrul…</div>`;
    let date;
    try {
      date = await api.get(`/tenants/${tenantId}/mijloace-fixe`);
    } catch (e) {
      corp.innerHTML = `<h2 class="pf-titlu">Mijloace fixe</h2>` +
        `<p class="ecran-nota">Nu am putut încărca registrul de mijloace fixe${e && e.mesaj ? " — " + esc(e.mesaj) : ""}.</p>`;
      return;
    }
    randeaza(date.mijloace || []);
  }

  function randeaza(lista) {
    const randuri = lista.map((m) => `
      <tr>
        <td>${esc(m.cod || "")}</td>
        <td>${esc(m.denumire || "")}</td>
        <td class="fd-td-num">${bani(m.valoare)}</td>
        <td class="fd-td-num">${bani(m.amortizat)}</td>
        <td class="fd-td-num">${bani(m.ramas)}</td>
        <td>${esc(m.metoda || "")}</td>
        <td>${m.data_pif ? dataRo(m.data_pif) : "—"}</td>
        <td>${m.activ ? "activ" : "casat"}</td>
        <td>${m.activ ? `
          <div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center">
            <button class="buton-secundar" data-caseaza="${m.id}">Casează</button>
            <input type="number" step="0.01" class="camp-input" style="max-width:130px" id="mf-reeval-${m.id}" placeholder="valoare justă" aria-label="Valoare justă ${esc(m.denumire || "")}">
            <button class="buton-secundar" data-reeval="${m.id}">Reevaluează</button>
          </div>` : "—"}</td>
      </tr>`).join("");

    corp.innerHTML = `
      <h2 class="pf-titlu">Mijloace fixe</h2>
      <p class="pf-intro">Registrul activelor firmei: valoare, amortizat la zi (liniar, de la punerea în funcțiune), rămas. Casarea și reevaluarea generează note contabile drept <b>ciornă</b> — se validează din Registru jurnal.</p>
      <div id="mf-mesaj"></div>
      ${lista.length ? `
      <div style="overflow-x:auto">
        <table class="fd-tabel">
          <thead><tr>
            <th>Cod</th><th>Denumire</th>
            <th class="fd-td-num">Valoare</th><th class="fd-td-num">Amortizat</th><th class="fd-td-num">Rămas</th>
            <th>Metodă</th><th>PIF</th><th>Stare</th><th>Acțiuni</th>
          </tr></thead>
          <tbody>${randuri}</tbody>
        </table>
      </div>` : `<p class="ecran-nota">Firma nu are mijloace fixe înregistrate. Se adaugă la migrare sau prin Operațiuni speciale → Inventariere anuală (plus mijloc fix).</p>`}`;

    const zona = corp.querySelector("#mf-mesaj");

    corp.querySelectorAll("[data-caseaza]").forEach((b) => b.addEventListener("click", () => {
      const id = b.dataset.caseaza;
      const m = lista.find((x) => String(x.id) === String(id));
      confirmaCaseta(b.closest("tr"),
        `Casezi <b>${esc(m ? m.denumire : id)}</b>? Se generează nota de casare (ciornă), amortizarea la zi se calculează automat și mijlocul devine inactiv.`,
        async () => {
          try {
            await api.post(`/tenants/${tenantId}/nota-inventariere`,
              { operatie: "casare", mijloc_fix_id: Number(id), data: azi });
            arataMesaj(zona, "Casare înregistrată (ciornă). O validezi din Registru jurnal.", "info");
            await incarca();
          } catch (e) {
            arataMesaj(zona, e && e.mesaj ? e.mesaj : "Nu am putut casa mijlocul fix.", "eroare");
          }
        }, { textOk: "Casează" });
    }));

    corp.querySelectorAll("[data-reeval]").forEach((b) => b.addEventListener("click", async () => {
      const id = b.dataset.reeval;
      const inp = corp.querySelector(`#mf-reeval-${id}`);
      const v = inp && parseFloat(inp.value);
      if (!v || v <= 0) {
        arataMesaj(zona, "Introdu valoarea justă (din raportul evaluatorului) înainte de reevaluare.", "avert");
        return;
      }
      try {
        await api.post(`/tenants/${tenantId}/reevaluare-imobilizare`,
          { operatie: "reevaluare", mijloc_fix_id: Number(id), valoare_justa: v, data: azi });
        arataMesaj(zona, "Reevaluare înregistrată (ciornă). O validezi din Registru jurnal.", "info");
        await incarca();
      } catch (e) {
        arataMesaj(zona, e && e.mesaj ? e.mesaj : "Nu am putut reevalua mijlocul fix.", "eroare");
      }
    }));
  }

  await incarca();
}
