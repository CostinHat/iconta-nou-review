// [ecran_mf_v1 14.08.2026] Registrul mijloacelor fixe al firmei — ecranul de gestiune care lipsea.
// Pana acum MF existau doar in DB (import la migrare + butonul "Genereaza amortizarea"); nu se
// puteau vedea, casa sau reevalua din interfata — iar casarea/reevaluarea cereau un mijloc_fix_id
// pe care niciun ecran nu-l arata (casarea din formular dadea 422 garantat). Aici e sursa acelui id
// + doua actiuni directe: casare (POST nota-inventariere) si reevaluare (POST reevaluare-imobilizare).
import { api, esc, arataMesaj, confirmaCaseta, bani, dataRo, dataIso } from "../api.js?v=eff78f4bb3";

export async function ecranMijloace(corp, nav, tenantId, opt = {}) {
  const azi = dataIso();

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
        ${m.eroare
          ? `<td class="fd-td-num" colspan="2"><span class="msg-eroare">${esc(m.eroare)}</span></td>`
          : `<td class="fd-td-num">${m.amortizat != null ? bani(m.amortizat) : "—"}</td>
        <td class="fd-td-num">${m.ramas != null ? bani(m.ramas) : "—"}</td>`}
        <td>${esc(m.metoda || "")}</td>
        <td>${m.data_pif ? dataRo(m.data_pif) : "—"}</td>
        <td>${m.activ ? "activ" : "casat"}</td>
        <td>${m.activ ? `
          <div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center">
            <button class="buton-secundar" data-caseaza="${m.id}" data-actiune="POST /tenants/{tenant_id}/nota-inventariere">Casează</button>
            <input type="number" step="0.01" class="camp-input" style="max-width:130px" id="mf-reeval-${m.id}" placeholder="valoare justă" aria-label="Valoare justă ${esc(m.denumire || "")}">
            <button class="buton-secundar" data-reeval="${m.id}" data-actiune="POST /tenants/{tenant_id}/reevaluare-imobilizare">Reevaluează</button>
            <button class="buton-secundar" data-cd="${m.id}" data-actiune="PUT /tenants/{tenant_id}/mijloace-fixe/{mijloc_id}/destinatie-cd" data-cd-val="${m.destinatie_cd ? 1 : 0}">C&amp;D: ${m.destinatie_cd ? "da" : "nu"}</button>
          </div>` : "—"}</td>
      </tr>`).join("");

    corp.innerHTML = `
      <h2 class="pf-titlu">Mijloace fixe</h2>
      <p class="pf-intro">Registrul activelor firmei: valoare, amortizat la zi (pe metoda fiecărui activ — liniar, degresiv, accelerat sau superaccelerat, CF art.28), rămas. Casarea și reevaluarea generează note contabile drept <b>ciornă</b> — se validează din Registru jurnal. Butonul <b>C&amp;D</b> marchează aparatura și echipamentele destinate cercetării-dezvoltării: ele se pot amortiza accelerat din orice cont (CF art. 20 alin. (1) lit. b)).</p>
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

    // [lot 19 d11] bifa «Destinat C&D» — CF art. 20 alin. (1) lit. b)
    corp.querySelectorAll("[data-cd]").forEach((b) => b.addEventListener("click", async () => {
      try {
        await api.put(`/tenants/${tenantId}/mijloace-fixe/${b.dataset.cd}/destinatie-cd`,
          { destinatie_cd: b.dataset.cdVal !== "1" });
        await incarca();
      } catch (e) {
        arataMesaj(zona, e && e.mesaj ? e.mesaj : "Nu am putut schimba destinația C&D.", "eroare");
      }
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
