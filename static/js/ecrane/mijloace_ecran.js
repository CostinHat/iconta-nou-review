// [ecran_mf_v1 14.08.2026] Registrul mijloacelor fixe al firmei — ecranul de gestiune care lipsea.
// Pana acum MF existau doar in DB (import la migrare + butonul "Genereaza amortizarea"); nu se
// puteau vedea, casa sau reevalua din interfata — iar casarea/reevaluarea cereau un mijloc_fix_id
// pe care niciun ecran nu-l arata (casarea din formular dadea 422 garantat). Aici e sursa acelui id
// + doua actiuni directe: casare (POST nota-inventariere) si reevaluare (POST reevaluare-imobilizare).
import { api, esc, arataMesaj, confirmaCaseta, bani, dataRo, dataIso } from "../api.js?v=4242dc4353";

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

  // [08.10.2026, decizia Costin W2] „registrul afișează amortizarea înregistrată în contabilitate, iar separat diferența față de
  // calculul teoretic, cu lunile neînregistrate … durata, codul din catalog și planul lunar de amortizare”
  const inregistrat = (m) => m.inregistrat != null
    ? bani(m.inregistrat)
    : (m.inregistrat_pe_cont ? `<span class="tip-desc">pe contul ${esc(m.inregistrat_pe_cont.cont)}: ${bani(m.inregistrat_pe_cont.sold)} (${m.inregistrat_pe_cont.mijloace} mijloace)</span>` : "—");
  const diferenta = (m) => (m.diferenta == null ? "—"
    : `${bani(m.diferenta)}${(m.luni_neinregistrate || []).length ? `<div class="tip-desc">neînregistrate: ${esc(m.luni_neinregistrate.join(", "))}</div>` : ""}`);
  const catalogCel = (m) => `<div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">
      <input class="camp-input" style="max-width:120px" id="mf-catalog-${m.id}" value="${esc(m.cod_catalog || "")}" placeholder="ex. 2.1.17.2.1" aria-label="Cod din catalog ${esc(m.denumire || "")}">
      <button class="buton-secundar" data-catalog="${m.id}" data-actiune="PUT /tenants/{tenant_id}/mijloace-fixe/{mijloc_id}/cod-catalog">Salvează</button></div>
    ${m.catalog ? `<div class="tip-desc">${esc(m.catalog.denumire)} · ${m.catalog.ani_min}–${m.catalog.ani_max} ani</div>` : ""}`;
  const planLunar = (m) => !(m.plan_lunar || []).length ? "" : `<tr><td colspan="13"><details><summary>Planul lunar de amortizare — ${esc(m.cod || m.denumire || "")} (${m.plan_lunar.length} luni)</summary>
      <table class="fd-tabel"><thead><tr><th>Luna</th><th class="fd-td-num">Rata</th><th>Înregistrare</th></tr></thead><tbody>
      ${m.plan_lunar.map((p) => `<tr><td>${String(p.luna).padStart(2, "0")}/${p.an}</td><td class="fd-td-num">${bani(p.rata)}</td><td>${{ inregistrata: "înregistrată", sold_initial: "în soldul de preluare", neinregistrata: "neînregistrată", in_curs: "luna curentă", viitoare: "—" }[p.stare] || ""}</td></tr>`).join("")}
      </tbody></table></details></td></tr>`;

  function randeaza(lista) {
    const randuri = lista.map((m) => `
      <tr>
        <td>${esc(m.cod || "")}</td>
        <td>${esc(m.denumire || "")}</td>
        <td>${catalogCel(m)}</td>
        <td class="fd-td-num">${m.durata_luni ? m.durata_luni + " luni" : "—"}</td>
        <td class="fd-td-num">${bani(m.valoare)}</td>
        ${m.eroare
          ? `<td class="fd-td-num" colspan="4"><span class="msg-eroare">${esc(m.eroare)}</span></td>`
          : `<td class="fd-td-num">${m.amortizat_teoretic != null ? bani(m.amortizat_teoretic) : "—"}</td>
        <td class="fd-td-num">${inregistrat(m)}</td>
        <td class="fd-td-num">${diferenta(m)}</td>
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
      </tr>${planLunar(m)}`).join("");

    corp.innerHTML = `
      <h2 class="pf-titlu">Mijloace fixe</h2>
      <p class="pf-intro">Registrul activelor firmei: valoare, amortizarea <b>calculată</b> la zi (pe metoda fiecărui activ — liniar, degresiv, accelerat sau superaccelerat, CF art.28), amortizarea <b>înregistrată</b> în contabilitate (soldul contului de amortizare, note validate) și diferența, cu lunile neînregistrate; rămas. Casarea și reevaluarea generează note contabile drept <b>ciornă</b> — se validează din Registru jurnal. Butonul <b>C&amp;D</b> marchează aparatura și echipamentele destinate cercetării-dezvoltării: ele se pot amortiza accelerat din orice cont (CF art. 20 alin. (1) lit. b)).</p>
      <div id="mf-mesaj"></div>
      ${lista.length ? `
      <div style="overflow-x:auto">
        <table class="fd-tabel">
          <thead><tr>
            <th>Cod</th><th>Denumire</th><th>Cod din catalog</th><th class="fd-td-num">Durată</th>
            <th class="fd-td-num">Valoare</th><th class="fd-td-num">Amortizat (calculat)</th><th class="fd-td-num">Înregistrat (cont)</th>
            <th class="fd-td-num">Diferență</th><th class="fd-td-num">Rămas</th>
            <th>Metodă</th><th>PIF</th><th>Stare</th><th>Acțiuni</th>
          </tr></thead>
          <tbody>${randuri}</tbody>
        </table>
      </div>` : `<p class="ecran-nota">Firma nu are mijloace fixe înregistrate. Se adaugă la migrare sau prin Operațiuni speciale → Inventariere anuală (plus mijloc fix).</p>`}`;

    const zona = corp.querySelector("#mf-mesaj");

    // [08.10, W2] codul din catalog (HG 2139/2004), verificat de server
    corp.querySelectorAll("[data-catalog]").forEach((b) => b.addEventListener("click", async () => {
      const id = b.dataset.catalog;
      try {
        const r = await api.put(`/tenants/${tenantId}/mijloace-fixe/${id}/cod-catalog`, { cod_catalog: corp.querySelector(`#mf-catalog-${id}`).value.trim() });
        await incarca();
        if (r && (r.afirmatii || []).length) arataMesaj(corp.querySelector("#mf-mesaj"), r.afirmatii.map((a) => a.mesaj).join(" "), "avert");
      } catch (e) { arataMesaj(zona, e && e.mesaj ? e.mesaj : "Nu am putut salva codul din catalog.", "eroare"); }
    }));

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
