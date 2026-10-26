// [ecran_mf_v1 14.08.2026] Registrul mijloacelor fixe al firmei — ecranul de gestiune care lipsea.
// Pana acum MF existau doar in DB (import la migrare + butonul "Genereaza amortizarea"); nu se
// puteau vedea, casa sau reevalua din interfata — iar casarea/reevaluarea cereau un mijloc_fix_id
// pe care niciun ecran nu-l arata (casarea din formular dadea 422 garantat). Aici e sursa acelui id
// + doua actiuni directe: casare (POST nota-inventariere) si reevaluare (POST reevaluare-imobilizare).
import { api, cate, esc, arataMesaj, arataRefuzul, bani, dataRo, dupaGenerare, noteGenerate, stareNota, pasNota, eroareCamp, curataEroriCamp } from "../api.js?v=e38843b1ec";

// ["01/2026", …, "08/2026", "11/2026"] -> "9 luni: 01–08/2026, 11/2026" (intervalele peste an: "11/2025–02/2026")
export function luniScurte(luni) {
  const idx = luni.map((x) => { const [l, a] = x.split("/").map(Number); return a * 12 + l - 1; }).sort((a, b) => a - b);
  const eticheta = (i) => `${String(i % 12 + 1).padStart(2, "0")}/${Math.floor(i / 12)}`;
  const parti = [];
  for (let k = 0; k < idx.length; k++) {
    let j = k;
    while (j + 1 < idx.length && idx[j + 1] === idx[j] + 1) j++;
    const [a, b] = [idx[k], idx[j]];
    parti.push(a === b ? eticheta(a) : (Math.floor(a / 12) === Math.floor(b / 12)
      ? `${String(a % 12 + 1).padStart(2, "0")}–${eticheta(b)}` : `${eticheta(a)}–${eticheta(b)}`));
    k = j;
  }
  return `${cate(idx.length, "lună", "luni")}: ${parti.join(", ")}`;
}

export async function ecranMijloace(corp, nav, tenantId, opt = {}) {
  // [368, lotul 9] la PFA (partidă simplă) nu există note contabile: registrul ține activele și amortizarea calculată (deductibilă în
  // D212), fără coloanele „înregistrat în contabilitate” / „diferență” și fără casarea / reevaluarea care scriu note
  const simpla = !!opt.simpla;

  async function incarca() {
    corp.innerHTML = `<h2 class="pf-titlu">Mijloace fixe</h2><div class="ecran-nota">Se încarcă registrul…</div>`;
    let date;
    try {
      date = await api.get(`/tenants/${tenantId}/mijloace-fixe`);
    } catch (e) {
      corp.innerHTML = `<h2 class="pf-titlu">Mijloace fixe</h2>` +
        `<p class="ecran-nota">Nu s-a putut încărca registrul de mijloace fixe${e && e.mesaj ? " — " + esc(e.mesaj) : ""}.</p>`;
      return;
    }
    randeaza(date.mijloace || [], date.calculat_pana_la || "");
  }

  // [08.10.2026, decizia Costin W2] „registrul afișează amortizarea înregistrată în contabilitate, iar separat diferența față de
  // calculul teoretic, cu lunile neînregistrate … durata, codul din catalog și planul lunar de amortizare”
  // [lotul 13, deficiența 522] „Înregistrat” e al ACTIVULUI (rândurile lui din note + partea lui din soldul preluat), nu soldul contului;
  // ce stă pe cont fără activ (notă manuală) se spune separat
  const inregistrat = (m) => m.inregistrat != null
    ? `${bani(m.inregistrat)}${m.inregistrat_pe_cont && Number(m.inregistrat_pe_cont.nealocat || 0) !== 0
        ? `<div class="tip-desc">pe contul ${esc(m.inregistrat_pe_cont.cont)}, fără activ: ${bani(m.inregistrat_pe_cont.nealocat)}</div>` : ""}`
    : "—";
  // [08.10.2026, retest pct.13] „Lunile lipsă scurtate («8 luni: 01–08/2026»)” — lunile consecutive se strâng într-un interval.
  const diferenta = (m) => (m.diferenta == null ? "—"
    : `${bani(m.diferenta)}${(m.luni_neinregistrate || []).length ? `<div class="tip-desc">neînregistrate: ${esc(luniScurte(m.luni_neinregistrate))}</div>` : ""}${
      (m.luni_in_ciorna || []).length ? `<div class="tip-desc">în ciornă, de validat: ${esc(luniScurte(m.luni_in_ciorna))}</div>` : ""}`);
  const catalogCel = (m) => `<div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">
      <input class="camp-input" style="max-width:120px" id="mf-catalog-${m.id}" value="${esc(m.cod_catalog || "")}" aria-label="Cod din catalog ${esc(m.denumire || "")}">
      <button class="buton-secundar" data-catalog="${m.id}" data-actiune="PUT /tenants/{tenant_id}/mijloace-fixe/{mijloc_id}/cod-catalog">Salvează</button></div>
    ${m.catalog ? `<div class="tip-desc">${esc(m.catalog.denumire)} · ${m.catalog.ani_min}–${cate(m.catalog.ani_max, "an", "ani")}</div>` : ""}`;
  const planLunar = (m) => !(m.plan_lunar || []).length ? "" : `<tr><td colspan="${simpla ? 11 : 13}"><details><summary>Planul lunar de amortizare — ${esc(m.cod || m.denumire || "")} (${cate(m.plan_lunar.length, "lună", "luni")})</summary>
      <table class="fd-tabel"><thead><tr><th>Luna</th><th class="fd-td-num">Rata</th>${simpla ? "" : "<th>Înregistrare</th>"}</tr></thead><tbody>
      ${m.plan_lunar.map((p) => `<tr><td>${dataRo(new Date(p.an, p.luna - 1, 1), "luna_an_numeric")}</td><td class="fd-td-num">${bani(p.rata)}</td>${simpla ? "" : `<td>${{ inregistrata: "înregistrată", sold_initial: "în soldul de preluare", neinregistrata: "neînregistrată", in_ciorna: "în ciornă, de validat", in_curs: "luna curentă", viitoare: "—" }[p.stare] || ""}</td>`}</tr>`).join("")}
      </tbody></table></details></td></tr>`;
  // [lotul 13, deficiența 519] starea activului: intră / iese din registru la VALIDAREA notei care îl aduce / îl casează
  const stare = (m) => ({
    activ: "activ", casat: "casat",
    intrare_in_asteptare: `intră la validarea notei ${esc(m.nota_asteptare || "")}`,
    casare_in_asteptare: `casarea e în ciorna ${esc(m.nota_asteptare || "")}, de validat`,
  }[m.stare] || (m.activ ? "activ" : "casat"));
  // [lotul 13, clasele 674 / 675] aceleași butoane pe fiecare rând, în aceeași ordine; cel care nu se aplică e inactiv, cu motivul
  const motivInactiv = (m, act) => {
    if (m.stare === "intrare_in_asteptare") return "Activul intră în registru la validarea notei lui; până atunci nu are acțiuni.";
    if (m.stare === "casat") return "Activul e casat.";
    if (m.stare === "casare_in_asteptare" && act !== "cd") return "Casarea e în ciornă: valideaz-o sau șterge-o din Registrul jurnal.";
    if (act === "lipsa" && !(m.luni_neinregistrate || []).length) return "Nicio lună de amortizare neînregistrată până la ultima lună încheiată.";
    return "";
  };
  const buton = (m, act, eticheta, atrib) => {
    const motiv = motivInactiv(m, act);
    return `<button class="buton-secundar" ${atrib}${motiv ? ` disabled title="${esc(motiv)}"` : ""}>${eticheta}</button>`;
  };

  function randeaza(lista, pana) {
    const randuri = lista.map((m) => `
      <tr data-mf="${m.id}">
        <td>${esc(m.cod || "")}</td>
        <td>${esc(m.denumire || "")}</td>
        <td>${catalogCel(m)}</td>
        <td class="fd-td-num">${m.durata_luni ? cate(m.durata_luni, "lună", "luni") : "—"}</td>
        <td class="fd-td-num">${bani(m.valoare)}</td>
        ${m.eroare
          ? `<td class="fd-td-num" colspan="${simpla ? 2 : 4}"><span class="msg-eroare">${esc(m.eroare)}</span></td>`
          : `<td class="fd-td-num">${m.amortizat_teoretic != null ? bani(m.amortizat_teoretic) : "—"}</td>
        ${simpla ? "" : `<td class="fd-td-num">${inregistrat(m)}</td>
        <td class="fd-td-num">${diferenta(m)}</td>`}
        <td class="fd-td-num">${m.ramas != null ? bani(m.ramas) : "—"}</td>`}
        <td>${esc(m.metoda_eticheta || "")}</td>
        <td style="white-space:nowrap">${m.data_pif ? dataRo(m.data_pif) : "—"}</td>
        <td class="mf-stare">${stare(m)}</td>
        <td><div style="display:flex;flex-direction:column;gap:6px;align-items:stretch">
          ${simpla ? "" : `${buton(m, "casare", "Casează", `data-caseaza="${m.id}" data-actiune="POST /tenants/{tenant_id}/nota-inventariere"`)}
          ${buton(m, "reeval", "Reevaluează", `data-reeval="${m.id}" data-actiune="POST /tenants/{tenant_id}/reevaluare-imobilizare"`)}
          ${buton(m, "lipsa", `Înregistrează lunile lipsă${(m.luni_neinregistrate || []).length ? " (" + m.luni_neinregistrate.length + ")" : ""}`, `data-lipsa="${m.id}" data-actiune="POST /tenants/{tenant_id}/amortizare/restanta"`)}`}
          ${buton(m, "cd", `C&amp;D: ${m.destinatie_cd ? "da" : "nu"}`, `data-cd="${m.id}" data-actiune="PUT /tenants/{tenant_id}/mijloace-fixe/{mijloc_id}/destinatie-cd" data-cd-val="${m.destinatie_cd ? 1 : 0}"`)}
        </div></td>
      </tr>${planLunar(m)}`).join("");

    // [lotul 10, deficiențele 421 / 424, DS cap.9 v2.96] „se derulează doar tabelul din mijloc, niciodată lateral”: tabelul stă direct în
    // corp (fără cutia lui cu derulare laterală), iar zona de mesaj a acțiunilor de pe rânduri e lipită sus (`.rezumat-fix`)
    corp.innerHTML = `
      <h2 class="pf-titlu">Mijloace fixe</h2>
      ${simpla ? `<p class="pf-intro" id="mf-intro-simpla">Registrul activelor firmei: amortizarea <b>calculată</b> până la ${esc(pana)} (metoda fiecărui activ, CF art.28); în partidă simplă amortizarea intră în cheltuielile deductibile ale anului, în D212.</p>` : `<p class="pf-intro">Registrul activelor firmei: amortizarea <b>calculată</b> până la ${esc(pana)} și cea <b>înregistrată</b> pe fiecare activ; un activ adus sau casat printr-o notă se schimbă în registru la validarea ei.</p>`}
      <div id="mf-mesaj" class="rezumat-fix"></div>
      ${lista.length ? `
        <table class="fd-tabel">
          <thead><tr>
            <th>Cod</th><th>Denumire</th><th>Cod din catalog</th><th class="fd-td-num">Durată</th>
            <th class="fd-td-num">Valoare</th><th class="fd-td-num">Amortizat (calculat, până la ${esc(pana)})</th>${simpla ? "" : `<th class="fd-td-num">Înregistrat pe activ (la ${esc(pana)})</th>
            <th class="fd-td-num">Diferență</th>`}<th class="fd-td-num">Rămas</th>
            <th>Metodă</th><th>PIF</th><th>Stare</th><th>Acțiuni</th>
          </tr></thead>
          <tbody>${randuri}</tbody>
        </table>` : `<p class="ecran-nota">Firma nu are mijloace fixe înregistrate. Se adaugă la migrare sau prin Operațiuni speciale → Inventariere anuală (plus mijloc fix) ori Leasing (primire bun).</p>`}`;

    const zona = corp.querySelector("#mf-mesaj");

    // [08.10, W2] codul din catalog (HG 2139/2004), verificat de server
    corp.querySelectorAll("[data-catalog]").forEach((b) => b.addEventListener("click", async () => {
      const id = b.dataset.catalog;
      try {
        const r = await api.put(`/tenants/${tenantId}/mijloace-fixe/${id}/cod-catalog`, { cod_catalog: corp.querySelector(`#mf-catalog-${id}`).value.trim() });
        await incarca();
        if (r && (r.afirmatii || []).length) arataMesaj(corp.querySelector("#mf-mesaj"), r.afirmatii.map((a) => a.mesaj).join(" "), "avert");
      } catch (e) { arataMesaj(zona, e && e.mesaj ? e.mesaj : "Nu s-a putut salva codul din catalog.", "eroare"); }
    }));

    // [lotul 13, deficiența 518 + clasa 673] casarea și reevaluarea se deschid într-o fereastră nouă: data casării (cerută, nu azi tăcut),
    // valoarea justă, nota generată arătată acolo; registrul se reîncarcă la întoarcere
    const fereastra = (titlu, m, fel) => nav.deschide(titlu, (c2) => {
      const casare = fel === "casare";
      c2.innerHTML = `<h2 class="pf-titlu">${esc(titlu)}</h2>
        <p class="pf-intro">${esc(m.cod || "")} · ${esc(m.denumire || "")} · valoare ${bani(m.valoare)} lei · înregistrat pe activ ${bani(m.inregistrat || 0)} lei.</p>
        <div class="grila-campuri">
          <div class="camp"><label class="camp-eticheta" for="mf-f-data">${casare ? "Data casării" : "Data reevaluării"}<span class="oblig">*</span></label><input type="date" id="mf-f-data" class="camp-input"></div>
          ${casare ? "" : `<div class="camp"><label class="camp-eticheta" for="mf-f-justa">Valoarea justă (raportul evaluatorului)<span class="oblig">*</span></label><input type="number" step="0.01" id="mf-f-justa" class="camp-input"></div>`}
        </div>
        <p class="camp-ajutor">${casare ? "Nota: luna casării pe 6811, amortizarea cumulată scoasă din contul de amortizare, restul neamortizat pe 6583; documentul e procesul-verbal de casare. Activul iese din registru la validarea notei." : "Rezerva din reevaluare (105) și pierderea anterioară (655) ale activului le ia aplicația din reevaluările lui."}</p>
        <div class="bara-fixa"><p class="dec-bara"><button class="buton-primar" id="mf-f-genereaza" data-genereaza-nota data-actiune="${casare ? "POST /tenants/{tenant_id}/nota-inventariere" : "POST /tenants/{tenant_id}/reevaluare-imobilizare"}">${casare ? "Generează nota de casare" : "Generează nota de reevaluare"}</button></p><div id="mf-f-mesaj"></div></div>`;
      const zf = c2.querySelector("#mf-f-mesaj");
      c2.querySelector("#mf-f-genereaza").addEventListener("click", async () => {
        curataEroriCamp(c2);
        const data = c2.querySelector("#mf-f-data").value;
        const justa = casare ? null : parseFloat(c2.querySelector("#mf-f-justa").value);
        let lipsa = false;
        if (!data) { eroareCamp(c2, "mf-f-data", "Alege data."); lipsa = true; }
        if (!casare && !(justa > 0)) { eroareCamp(c2, "mf-f-justa", "Scrie valoarea justă din raportul evaluatorului."); lipsa = true; }
        if (lipsa) return;
        try {
          const r = casare ? await api.post(`/tenants/${tenantId}/nota-inventariere`, { operatie: "casare", mijloc_fix_id: Number(m.id), data })
            : await api.post(`/tenants/${tenantId}/reevaluare-imobilizare`, { operatie: "reevaluare", mijloc_fix_id: Number(m.id), valoare_justa: justa, data });
          if (!r.inregistrare_id) { arataMesaj(zf, "Nicio diferență de reevaluat: valoarea justă e egală cu valoarea netă contabilă. Nu s-a generat nicio notă.", "info"); return; }
          dupaGenerare(zf, c2.querySelector("#mf-f-genereaza"), { titlu: `${casare ? "Nota de casare" : "Nota de reevaluare"} (${stareNota(r)})`,
            note: await noteGenerate(tenantId, [r.inregistrare_id], data), pas: pasNota(r) });
        } catch (e) { arataRefuzul(c2, e, zf, { campuri: { data: "mf-f-data", valoare_justa: "mf-f-justa" } }); }
      });
    });
    corp.querySelectorAll("[data-caseaza]").forEach((b) => b.addEventListener("click", () => {
      const m = lista.find((x) => String(x.id) === String(b.dataset.caseaza));
      fereastra(`Casare ${m.cod || ""}`, m, "casare");
    }));
    corp.querySelectorAll("[data-reeval]").forEach((b) => b.addEventListener("click", () => {
      const m = lista.find((x) => String(x.id) === String(b.dataset.reeval));
      fereastra(`Reevaluare ${m.cod || ""}`, m, "reevaluare");
    }));
    // [lotul 13, deficiența 517] „Din rândul activului se generează toate lunile lipsă deodată, ca ciorne” — până la ultima lună încheiată
    corp.querySelectorAll("[data-lipsa]").forEach((b) => b.addEventListener("click", async () => {
      const [luna, an] = String(pana).split("/").map(Number);
      b.disabled = true;
      try {
        const r = await api.post(`/tenants/${tenantId}/amortizare/restanta?an=${an}&luna=${luna}`, {});
        await incarca();
        const z = corp.querySelector("#mf-mesaj");
        const ok = (r.luni || []).filter((x) => x.ok && !x.deja_generata), refuz = (r.luni || []).filter((x) => !x.ok);
        dupaGenerare(z, null, { titlu: `${cate(ok.length, "notă de amortizare generată", "note de amortizare generate")} (ciorne)`,
          note: ok.map((x) => ({ eticheta: `${String(x.luna).padStart(2, "0")}/${x.an} — ${x.nota_eticheta || ""}`, linii: (x.linii_nota || []).map((l) => ({ debit: l.debit, credit: l.credit, suma: l.suma })) })),
          detalii: [r.deja_generate ? `${cate(r.deja_generate, "lună era deja generată", "luni erau deja generate")}, de validat.` : "", ...refuz.map((x) => `${String(x.luna).padStart(2, "0")}/${x.an}: ${x.mesaj}`)],
          pas: "Le validezi din Registrul jurnal; după validare lunile apar înregistrate pe activ." });
      } catch (e) { b.disabled = false; arataMesaj(zona, e && e.mesaj ? e.mesaj : "Lunile lipsă nu s-au putut genera.", "eroare"); }
    }));

    // [lot 19 d11] bifa «Destinat C&D» — CF art. 20 alin. (1) lit. b)
    corp.querySelectorAll("[data-cd]").forEach((b) => b.addEventListener("click", async () => {
      try {
        await api.put(`/tenants/${tenantId}/mijloace-fixe/${b.dataset.cd}/destinatie-cd`,
          { destinatie_cd: b.dataset.cdVal !== "1" });
        await incarca();
      } catch (e) {
        arataMesaj(zona, e && e.mesaj ? e.mesaj : "Nu s-a putut schimba destinația C&D.", "eroare");
      }
    }));
  }

  corp.addEventListener("nav:revenire", incarca);   // [lotul 13] întors din fereastra casării / reevaluării: registrul la zi
  await incarca();
}
