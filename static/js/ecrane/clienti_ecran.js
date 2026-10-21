// [lotul 10, deficiența 428, decizia Costin 20.10.2026 „Bifă pe client”] Clienții firmei, cu bifa „Persoană afiliată (Cod fiscal art.7
// pct.26)”: „factura către el ia regulile generale (4427) chiar dacă firma e în sistem” — CF art.282 alin.(6) lit.d): sistemul TVA la încasare
// nu se aplică „livrărilor de bunuri/prestărilor de servicii pentru care beneficiarul este o persoană afiliată furnizorului/prestatorului
// potrivit art. 7 pct. 26”. Bifa se îngheață pe factură la emitere (`facturi.beneficiar_afiliat`); o bifă schimbată nu mută facturile vechi.
// Lista: fișele de client + beneficiarii facturilor emise fără fișă (salvarea bifei le creează fișa).
// DS: fereastra cu tabel (cap.9 v2.96) — rezumatul și zona de mesaj a acțiunilor de pe rânduri lipite sus (`.rezumat-fix`), acțiunea pe rând
// stă în celula ei; cifrele în `.fd-td-num`.
import { api, arataMesaj, esc, selectDaNu, daNu } from "../api.js?v=ff30ebaf3f";

export async function ecranClienti(corp, nav, t) {
  let mesajDupa = null;
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
    let r;
    try {
      r = await api.get(`/tenants/${t.id}/clienti`);
    } catch (e) {
      corp.innerHTML = `<h2 class="pf-titlu">Clienți</h2><div id="cl-mesaj"></div>`;
      arataMesaj(corp.querySelector("#cl-mesaj"), "Clienții nu s-au putut citi" + (e && e.mesaj ? ": " + e.mesaj : "") + ".", "eroare");
      return;
    }
    const randuri = [
      ...(r.clienti || []).map((c) => ({ cheie: "c" + c.id, id: c.id, nume: c.nume, cui: c.cui, afiliat: !!c.afiliat, facturi: null })),
      ...(r.parteneri_fara_fisa || []).map((p) => ({ cheie: "p" + p.cui, id: null, nume: p.nume, cui: p.cui, afiliat: false, facturi: p.facturi })),
    ];
    const rand = (x) => `<tr data-cheie="${esc(x.cheie)}">
        <td>${esc(x.nume || "")}${x.id ? "" : `<div class="tip-desc">fără fișă de client — din facturile emise</div>`}</td>
        <td>${esc(x.cui || "—")}</td>
        <td class="fd-td-num">${x.facturi === null ? "" : x.facturi}</td>
        <td>${selectDaNu(`class="cl-afiliat" id="cl-afiliat-${esc(x.cheie)}" data-cheie="${esc(x.cheie)}"`, x.afiliat,
          `Persoană afiliată (Cod fiscal art.7 pct.26): ${x.nume || x.cui || ""}`)}</td>
        <td><button class="buton-secundar cl-salveaza" id="cl-salveaza-${esc(x.cheie)}" data-cheie="${esc(x.cheie)}" disabled
          data-actiune="${x.id ? "PUT /tenants/{tenant_id}/clienti/{client_id}" : "POST /tenants/{tenant_id}/clienti"}">Salvează</button></td>
      </tr>`;
    corp.innerHTML = `
      <div class="rezumat-fix" id="cl-rezumat">
        <h2 class="pf-titlu">Clienți</h2>
        <p class="pf-intro">Bifează clienții care sunt persoane afiliate firmei (Cod fiscal art.7 pct.26). Pentru ei, chiar dacă firma aplică
          TVA la încasare, factura ia regulile generale: TVA-ul e exigibil la emitere, pe 4427 (Cod fiscal art.282 alin.(6) lit.d). Bifa se
          aplică facturilor emise de acum înainte; cele emise rămân cum au fost emise.</p>
        <div id="cl-mesaj"></div>
      </div>
      ${randuri.length ? `<table class="fd-tabel" id="cl-tabel"><thead><tr><th>Client</th><th>CUI</th><th class="fd-td-num">Facturi emise</th>
        <th>Persoană afiliată (Cod fiscal art.7 pct.26)</th><th>Acțiune</th></tr></thead><tbody>${randuri.map(rand).join("")}</tbody></table>`
        : `<div class="stare-goala" id="cl-gol">Niciun client încă: clienții apar aici din facturile emise.</div>`}`;
    if (mesajDupa) arataMesaj(corp.querySelector("#cl-mesaj"), mesajDupa, "ok");
    const dupaCheie = Object.fromEntries(randuri.map((x) => [x.cheie, x]));
    corp.querySelectorAll(".cl-afiliat").forEach((cb) => cb.addEventListener("change", () => {
      const x = dupaCheie[cb.dataset.cheie];
      corp.querySelector(`#cl-salveaza-${CSS.escape(x.cheie)}`).disabled = daNu(cb) === (x.afiliat == null ? null : !!x.afiliat);
    }));
    corp.querySelectorAll(".cl-salveaza").forEach((b) => b.addEventListener("click", async () => {
      const x = dupaCheie[b.dataset.cheie];
      const afiliat = daNu(corp.querySelector(`#cl-afiliat-${CSS.escape(x.cheie)}`));
      if (afiliat === null) return;   // „— alege —”: nicio alegere, nimic de salvat
      try {
        if (x.id) await api.put(`/tenants/${t.id}/clienti/${x.id}`, { afiliat });
        else await api.post(`/tenants/${t.id}/clienti`, { nume: x.nume || x.cui, cui: x.cui, afiliat });
        mesajDupa = `${x.nume || x.cui}: ${afiliat ? "bifat ca persoană afiliată — facturile emise de acum înainte către el iau regulile "
          + "generale (TVA exigibil la emitere)" : "nu mai e persoană afiliată — facturile de acum înainte urmează regimul firmei"}.`;
        await deseneaza();
      } catch (e) {
        arataMesaj(corp.querySelector("#cl-mesaj"), (e && e.mesaj) || "Bifa nu s-a putut salva.", "eroare");
      }
    }));
  };
  await deseneaza();
}
