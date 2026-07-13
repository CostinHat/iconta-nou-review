// [rip] Registru incasari/plati (partida simpla PFA/II/IF) + Fisa D212
import { api, bani, confirmaCaseta, dataRo } from "../api.js";  /* investigatie_identitate_v1 */

const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

const CATEGORII_INC = [
  ["activitate", "\u00cencasare din activitate"],
  ["aport", "Aport numerar/banca"],
  ["credit", "Credit / imprumut primit"],
  ["subventie", "Subventie / fonduri"],
  ["alte_incasari", "Alte incasari"],
];
const CATEGORII_PL = [
  ["cheltuiala_deductibila", "Cheltuiala deductibila"],
  ["cheltuiala_limitata", "Cheltuiala deductibila limitat"],
  ["cheltuiala_nedeductibila", "Cheltuiala nedeductibila"],
  ["aport_retragere", "Retragere aport"],
  ["rambursare_credit", "Rambursare credit"],
];

export async function ecranRip(corp, nav, t) {
  const azi = new Date();
  let an = azi.getFullYear(), luna = azi.getMonth() + 1;

  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
    let reg = { operatiuni: [], total_incasari: "0", total_plati: "0", sold: "0" };
    try { reg = await api.get(`/tenants/${t.id}/rip/registru?an=${an}&luna=${luna}`); } catch {}
    const ziAzi = new Date().toISOString().slice(0, 10);

    const randuri = !(reg.operatiuni || []).length
      ? `<div class="mig-gol">Nicio opera\u021biune \u00een luna asta.</div>`
      : reg.operatiuni.map((o) => `
        <div class="pf-frand">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">${dataRo(o.data_operatiune)} \u00b7 ${o.tip === "plata" ? "\u2212" : "+"}${bani(o.suma)} ${esc(o.valuta)}
              ${o.status === "ciorna" ? '<span style="color:var(--galben);font-weight:600"> \u00b7 CIORNA</span>' : '<span style="color:var(--verde);font-weight:600"> \u00b7 VALIDATA</span>'}</div>
            <div class="pf-frand-sub">${esc(o.explicatie)} \u00b7 ${esc(o.categorie)}${o.deductibilitate ? " \u00b7 " + esc(o.deductibilitate) : ""}${o.document_numar ? " \u00b7 doc " + esc(o.document_numar) : ""} \u00b7 ${esc(o.metoda)}</div>
          </div>
          ${o.status === "ciorna" ? `<button class="buton-primar" data-val="${o.id}">Valideaz\u0103</button>
          <button class="buton-secundar" data-del="${o.id}">\u0218terge</button>` : ""}
        </div>`).join("");

    corp.innerHTML = `
      <h2 class="pf-titlu">Registru \u00eencas\u0103ri/pl\u0103\u021bi</h2>
      <p class="pf-intro">Luna ${String(luna).padStart(2, "0")}/${an}
        \u00b7 \u00eencas\u0103ri <b>${bani(reg.total_incasari)}</b> \u00b7 pl\u0103\u021bi <b>${bani(reg.total_plati)}</b> \u00b7 sold <b>${bani(reg.sold)} lei</b>
        <button class="buton-secundar" id="r-prev" style="margin-left:12px">\u2190 luna</button>
        <button class="buton-secundar" id="r-next">luna \u2192</button></p>
      <p>
        <button class="buton-secundar" id="r-imp-banca">Import din banc\u0103 (ciorne)</button>
        <button class="buton-secundar" id="r-imp-casa">Import din cas\u0103 (ciorne)</button>
        <button class="buton-secundar" id="r-d212">Fi\u0219a D212</button>
        <button class="buton-secundar" id="r-inv">Registru-inventar</button>
      </p>
      <div id="r-mesaj"></div>
      <p><button class="buton-secundar" id="r-toggle">+ Opera\u021biune nou\u0103</button></p>
      <div id="r-zona" hidden style="display:block;margin-bottom:14px">
        <div class="pf-frand-nume" style="margin-bottom:8px">Opera\u021biune nou\u0103</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;max-width:1000px">
          <label class="camp"><span class="camp-eticheta">Data<span class="oblig">*</span></span><input type="date" id="r-data" class="camp-input"></label>
          <label class="camp"><span class="camp-eticheta">Tip</span><select id="r-tip" class="camp-input"><option value="incasare">Încasare</option><option value="plata">Plată</option></select></label>
          <label class="camp"><span class="camp-eticheta">Categorie</span><select id="r-cat" class="camp-input"></select></label>
          <label class="camp"><span class="camp-eticheta">Deductibilitate</span><select id="r-ded" class="camp-input" disabled>
            <option value="">-</option><option value="integral">integral</option>
            <option value="limitat">limitat</option><option value="nedeductibil">nedeductibil</option></select></label>
          <label class="camp"><span class="camp-eticheta">Suma (lei)<span class="oblig">*</span></span><input type="number" step="0.01" id="r-suma" class="camp-input" placeholder="0,00"></label>
          <label class="camp"><span class="camp-eticheta">Metod\u0103</span><select id="r-met" class="camp-input"><option value="numerar">Numerar</option><option value="banca">Bancă</option></select></label>
          <label class="camp"><span class="camp-eticheta">Explicație<span class="oblig">*</span></span><input type="text" id="r-expl" class="camp-input"></label>
          <label class="camp"><span class="camp-eticheta">Document nr.</span><input type="text" id="r-doc" class="camp-input"></label>
        </div>
        <p style="margin-top:10px"><button class="buton-primar" id="r-adauga">Adaugă (ciornă)</button></p>
      </div>
      <div class="pf-lista">${randuri}</div>`;

    const zonaMsg = corp.querySelector("#r-mesaj");
    const _tg = (btnId, zonaId) => {  /* cap2_toggle_v1 */
      const b = corp.querySelector(btnId), z = corp.querySelector(zonaId);
      if (!b || !z) return;
      b.addEventListener("click", () => {
        z.hidden = !z.hidden;
        b.classList.toggle("buton-activ", !z.hidden);
      });
    };
    _tg("#r-toggle", "#r-zona");
    const selTip = corp.querySelector("#r-tip"), selCat = corp.querySelector("#r-cat"), selDed = corp.querySelector("#r-ded");
    const umpleCat = () => {
      const cats = selTip.value === "incasare" ? CATEGORII_INC : CATEGORII_PL;
      selCat.innerHTML = cats.map(([v, l]) => `<option value="${v}">${l}</option>`).join("");
      actDed();
    };
    const actDed = () => {
      const eChelt = selTip.value === "plata" && selCat.value.startsWith("cheltuiala");
      selDed.disabled = !eChelt;
      selDed.value = eChelt ? (selCat.value === "cheltuiala_limitata" ? "limitat"
        : selCat.value === "cheltuiala_nedeductibila" ? "nedeductibil" : "integral") : "";
    };
    selTip.addEventListener("change", umpleCat);
    selCat.addEventListener("change", actDed);
    umpleCat();

    corp.querySelector("#r-prev").addEventListener("click", () => { luna--; if (luna < 1) { luna = 12; an--; } deseneaza(); });
    corp.querySelector("#r-next").addEventListener("click", () => { luna++; if (luna > 12) { luna = 1; an++; } deseneaza(); });

    corp.querySelector("#r-adauga").addEventListener("click", async () => {
      try {
        await api.post(`/tenants/${t.id}/rip/operatiuni`, {
          data_operatiune: corp.querySelector("#r-data").value,
          tip: selTip.value, categorie: selCat.value,
          deductibilitate: selDed.value || null,
          suma: parseFloat(corp.querySelector("#r-suma").value || "0"),
          metoda: corp.querySelector("#r-met").value,
          explicatie: corp.querySelector("#r-expl").value,
          document_numar: corp.querySelector("#r-doc").value || null,
        });
        deseneaza();
      } catch (e) { zonaMsg.innerHTML = `<div class="mig-gol">${esc(e.mesaj || e.message || "eroare")}</div>`; }
    });

    corp.querySelector("#r-imp-banca").addEventListener("click", async () => {
      try { const r = await api.post(`/tenants/${t.id}/rip/import-banca?an=${an}&luna=${luna}`, {}); zonaMsg.innerHTML = `<p class="pf-intro"><b>${r.importate}</b> ciorne importate din bancă.</p>`; deseneaza(); }
      catch (e) { zonaMsg.innerHTML = `<div class="mig-gol">${esc(e.mesaj || e.message || "eroare")}</div>`; }
    });
    corp.querySelector("#r-imp-casa").addEventListener("click", async () => {
      try { const r = await api.post(`/tenants/${t.id}/rip/import-casa?an=${an}&luna=${luna}`, {}); zonaMsg.innerHTML = `<p class="pf-intro"><b>${r.importate}</b> ciorne importate din cas\u0103.</p>`; deseneaza(); }
      catch (e) { zonaMsg.innerHTML = `<div class="mig-gol">${esc(e.mesaj || e.message || "eroare")}</div>`; }
    });

    corp.querySelector("#r-inv").addEventListener("click", async () => {
      try {
        const d = await api.get(`/tenants/${t.id}/rip/inventar/${an}`);
        const mf = (d.mijloace_fixe || []).map((m) =>
          `<br>${esc(m.denumire)}: intrare ${m.valoare_intrare} \u2212 amortizare ${m.amortizare_cumulata} = <b>${m.valoare_ramasa}</b> lei`).join("");
        zonaMsg.innerHTML = `<div class="pf-frand" style="display:block">
          <div class="pf-frand-nume">Registru-inventar \u00b7 31.12.${d.an}</div>
          <div class="pf-frand-sub">Mijloace fixe (valoare ramasa): <b>${d.total_mijloace_fixe}</b> lei${mf}
          <br>Disponibilitati (RIP validat): <b>${d.disponibilitati}</b> lei
          <br><b class="tip-total">Total activ: ${bani(d.total_activ)} lei</b></div></div>`;
      } catch (e) { zonaMsg.innerHTML = `<div class="mig-gol">${esc(e.mesaj || e.message || "eroare")}</div>`; }
    });

    corp.querySelector("#r-d212").addEventListener("click", async () => {
      try {
        const d = await api.get(`/tenants/${t.id}/rip/d212/2025`);
        zonaMsg.innerHTML = `
          <div class="pf-frand" style="display:block">
            <div class="pf-frand-nume">Fi\u0219a de calcul D212 \u00b7 venituri 2025 (sm 4.050 lei)</div>
            <div class="pf-frand-sub">
              Venit brut: <b>${d.venit_brut}</b> \u00b7 Cheltuieli deductibile: <b>${d.cheltuieli_deductibile}</b> \u00b7 Venit net: <b>${d.venit_net}</b><br>
              CAS (25%): <b>${d.cas.cas}</b> lei${d.cas.obligatoriu ? "" : " (neobligatoriu - sub 12 salarii minime)"} \u00b7 baza ${d.cas.baza}<br>
              CASS (10%): <b>${d.cass.cass}</b> lei${d.cass.obligatoriu ? "" : " (neobligatoriu - sub 6 salarii minime)"} \u00b7 baza ${d.cass.baza}<br>
              Baza impozit: <b>${d.baza_impozit}</b> \u00b7 Impozit (10%): <b>${d.impozit}</b> lei<br>
              <b class="tip-total">Total datorat: ${bani(d.total_datorat)} lei</b>
              ${d.cheltuieli_limitate_de_analizat > 0 ? `<br><span style="color:var(--galben)">Cheltuieli limitate de analizat: ${bani(d.cheltuieli_limitate_de_analizat)} lei</span>` : ""}
              ${d.ciorne_nevalidate > 0 ? `<br><span style="color:var(--rosu-semafor)">${d.ciorne_nevalidate} ciorne nevalidate \u2014 neincluse \u00een calcul</span>` : ""}
              ${d.avertisment ? `<br><span style="color:var(--galben)">${esc(d.avertisment)}</span>` : ""}
            </div>
          </div>`;
      } catch (e) { zonaMsg.innerHTML = `<div class="mig-gol">${esc(e.mesaj || e.message || "eroare")}</div>`; }
    });

    corp.querySelectorAll("[data-val]").forEach((b) => b.addEventListener("click", async () => {
      try { await api.put(`/tenants/${t.id}/rip/operatiuni/${b.dataset.val}/valideaza`, {}); deseneaza(); }
      catch (e) { zonaMsg.innerHTML = `<div class="mig-gol">${esc(e.mesaj || e.message || "eroare")}</div>`; }
    }));
    corp.querySelectorAll("[data-del]").forEach((b) => b.addEventListener("click", () => {
      confirmaCaseta(b.parentElement || b, "\u0218tergi opera\u021biunea?", async () => {
        try { await api.del(`/tenants/${t.id}/rip/operatiuni/${b.dataset.del}`); deseneaza(); }
        catch (e) { zonaMsg.innerHTML = `<div class="mig-gol">${esc(e.mesaj || e.message || "eroare")}</div>`; }
      });
    }));
  };
  deseneaza();
}

// precompletari_rest_v1
