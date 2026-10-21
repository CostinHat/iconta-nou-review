// [lotul 10, deficiența 429, comanda Costin 10.1 pct.8] Reevaluarea lunară în valută, PROPUSĂ de aplicație: „La închiderea lunii,
// aplicația propune singură creanțele și datoriile în valută neîncasate (pe factură), disponibilitățile în valută, cursul din evidență,
// cursul BNR din ultima zi bancară și diferența pe 665/765; contabilul verifică și generează nota.” Temeiul: OMFP 1802/2014 pct.325
// (`core/reevaluare_valuta.py`). Ecranul se deschide din „Închidere lună” (blocajul „Ce oprește închiderea”); formularul manual din
// Operațiuni rămâne pentru cazurile speciale.
// DS: tabelul `.fd-tabel` cu cifrele în `.fd-td-num` (cap.9), rezumatul lipit sus `.rezumat-fix`, acțiunea și mesajul ei lipite jos
// `.bara-fixa` (cap.6, v2.92), confirmarea care numește nota și consecința rămâne pe ecran (cap.27).
import { api, arataMesaj, bani, esc, dataRo, eroareCamp, stareNota, pasNota } from "../api.js?v=ff30ebaf3f";

const FEL = { creanta: "Creanță", datorie: "Datorie", disponibil: "Disponibil" };

/** Cursul cu patru zecimale, în forma românească (4,9700). */
function curs(v) {
  if (v === null || v === undefined || v === "") return "—";
  return Number(v).toLocaleString("ro-RO", { minimumFractionDigits: 4, maximumFractionDigits: 4 });
}

/** De unde vine cursul din evidență: factura, reevaluarea anterioară sau soldul contului (lei / valută). */
function dinEvidenta(e) {
  if (!e.curs_evidenta_din) return "";
  if (e.curs_evidenta_din === "factura") return "cursul facturii";
  if (e.curs_evidenta_din === "sold") return "sold în lei / sold în valută";
  return "reevaluarea din " + dataRo(e.curs_evidenta_din);
}

/**
 * Ecranul propunerii. `opt.jurnal({an, luna, evidentiaza})` deschide Registrul jurnal pe nota generată (îl dă cine deschide ecranul;
 * fără el, confirmarea spune unde e nota, fără buton).
 */
export async function ecranReevaluareValuta(corp, nav, t, an, luna, opt = {}) {
  const completari = {};   // ce a scris contabilul pe ecran, pe element: {cheie: {sold_valuta, moneda}}
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
    let p;
    try {
      const q = Object.keys(completari).length ? `&completari=${encodeURIComponent(JSON.stringify(completari))}` : "";
      p = await api.get(`/tenants/${t.id}/reevaluare-valuta?an=${an}&luna=${luna}${q}`);
    } catch (e) {
      corp.innerHTML = `<h2 class="pf-titlu">Reevaluare valută</h2><div id="rv-mesaj"></div>`;
      arataMesaj(corp.querySelector("#rv-mesaj"), "Propunerea nu s-a putut calcula" + (e && e.mesaj ? ": " + e.mesaj : "") + ".", "eroare");
      return;
    }
    const el = p.elemente || [];
    const tot = p.totaluri || {};
    const camp = (e, c, eticheta) => {
      if (!(e.editabile || []).includes(c)) {
        return c === "moneda" ? esc(e.moneda || "—") : (e.sold_valuta === null ? "—" : bani(e.sold_valuta));
      }
      const val = (completari[e.cheie] || {})[c] ?? (c === "moneda" ? (e.moneda || "") : (e.sold_valuta ?? ""));
      return `<input class="camp-input rv-camp" id="rv-${c}-${esc(e.cheie)}" data-cheie="${esc(e.cheie)}" data-camp="${c}"
        aria-label="${esc(eticheta)}" value="${esc(val)}" ${c === "moneda" ? 'maxlength="3" style="width:5em"' : 'inputmode="decimal" style="width:9em"'}>`;
    };
    const rand = (e) => `<tr data-cheie="${esc(e.cheie)}">
        <td>${FEL[e.fel] || ""}<div class="tip-desc">${esc(e.document || "")}</div></td>
        <td>${esc(e.partener || "")}</td>
        <td>${esc(e.cont)}</td>
        <td>${camp(e, "moneda", `Moneda contului ${e.cont}`)}</td>
        <td class="fd-td-num">${camp(e, "sold_valuta", `Sold în valută, ${e.document || "contul " + e.cont}`)}${e.estimat ? `<div class="tip-desc">estimat din plățile în lei — verifică</div>` : ""}</td>
        <td class="fd-td-num">${curs(e.curs_evidenta)}<div class="tip-desc">${esc(dinEvidenta(e))}</div></td>
        <td class="fd-td-num">${bani(e.lei_evidenta)}</td>
        <td class="fd-td-num">${curs(e.curs_bnr)}${e.data_curs ? `<div class="tip-desc">din ${dataRo(e.data_curs)}</div>` : ""}</td>
        <td class="fd-td-num">${e.diferenta === undefined || e.diferenta === null ? "—" : bani(e.diferenta)}</td>
        <td>${e.cont_diferenta ? esc(e.cont_diferenta) : (e.motiv_curs ? `<span class="tip-desc">${esc(e.motiv_curs)}</span>`
          : ((e.de_completat || []).length ? `<span class="tip-desc">de completat</span>` : "—"))}</td>
      </tr>`;
    corp.innerHTML = `
      <div class="rezumat-fix" id="rv-rezumat">
        <h2 class="pf-titlu">Reevaluare valută — ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")}</h2>
        <p class="pf-intro">La sfârșitul lunii, elementele în valută se evaluează la cursul BNR din ultima zi bancară a lunii (OMFP
          1802/2014 pct.325); diferența merge pe 765 (favorabilă) sau 665 (nefavorabilă). Verifică propunerea, completează ce lipsește
          și generează nota.</p>
        <p id="rv-totaluri"><b>Venituri 765:</b> ${bani(tot.venit)} lei · <b>Cheltuieli 665:</b> ${bani(tot.cheltuiala)} lei ·
          <b>Net:</b> ${bani(tot.net)} lei${tot.de_completat ? ` · <b>De completat:</b> ${tot.de_completat}` : ""}</p>
      </div>
      ${p.luna_in_curs ? `<div class="caseta-info"><span class="ci-mesaj">${esc(p.luna_in_curs)} Propunerea e informativă: nota se
        generează după sfârșitul lunii.</span></div>` : ""}
      ${(p.ciorna_lunii || []).length ? `<div class="caseta-info"><span class="ci-mesaj">Luna are deja nota de reevaluare în ciornă;
        „Generează nota” o înlocuiește cu propunerea de acum.</span></div>` : ""}
      ${el.length ? `<table class="fd-tabel" id="rv-tabel"><thead><tr><th>Element</th><th>Partener / cont</th><th>Cont</th><th>Moneda</th>
        <th class="fd-td-num">Sold în valută</th><th class="fd-td-num">Curs din evidență</th><th class="fd-td-num">Sold în lei</th>
        <th class="fd-td-num">Curs BNR</th><th class="fd-td-num">Diferență (lei)</th><th>Cont diferență</th></tr></thead>
        <tbody>${el.map(rand).join("")}</tbody></table>`
        : `<div class="stare-goala" id="rv-gol">Nicio creanță, datorie sau disponibilitate în valută la sfârșitul lunii.</div>`}
      <div class="bara-fixa">
        <div id="rv-mesaj"></div>
        <p class="dec-bara"><button class="buton-primar" id="rv-genereaza" data-actiune="POST /tenants/{tenant_id}/reevaluare-valuta/nota"
          ${el.length && !p.luna_in_curs ? "" : "disabled"}>Generează nota</button></p>
      </div>`;
    corp.querySelectorAll(".rv-camp").forEach((inp) => inp.addEventListener("change", () => {
      const c = completari[inp.dataset.cheie] = completari[inp.dataset.cheie] || {};
      c[inp.dataset.camp] = inp.value.trim();
      deseneaza();   // propunerea se recalculează pe server, cu ce s-a scris: contabilul vede diferența înainte de generare
    }));
    corp.querySelector("#rv-genereaza").addEventListener("click", async () => {
      const zm = corp.querySelector("#rv-mesaj");
      const lipsa = el.filter((e) => (e.de_completat || []).length);
      if (lipsa.length) {
        lipsa.forEach((e) => e.de_completat.forEach((c) => eroareCamp(corp, `rv-${c}-${e.cheie}`,
          c === "moneda" ? "Scrie moneda contului (trei litere, ex. EUR)." : "Scrie soldul în valută din extrasul de la sfârșitul lunii.")));
        arataMesaj(zm, "Completează soldul în valută (și moneda, unde lipsește) pe conturile marcate, apoi generează nota.", "eroare");
        return;
      }
      try {
        const r = await api.post(`/tenants/${t.id}/reevaluare-valuta/nota`, { an, luna, completari });
        await deseneaza();
        const z = corp.querySelector("#rv-mesaj");
        if (!r.inregistrare_id) { arataMesaj(z, r.mesaj || "Nicio diferență de curs de înregistrat în luna aceasta.", "ok"); return; }
        // [279, clasa] starea reală a notei (ciornă / trimisă la validare / notă internă) și pasul următor, nu „ciornă” scris de mână
        arataMesaj(z, `Nota de reevaluare ${r.nota_eticheta || ""} a fost generată (${stareNota(r)})${r.inlocuita ? ", în locul notei nevalidate de dinainte" : ""}: `
          + `${r.nota || ""}. Venituri 765: ${bani(r.venit)} lei, cheltuieli 665: ${bani(r.cheltuiala)} lei. ${pasNota(r)} `
          + `După validare reevaluarea nu mai oprește închiderea lunii.`, "ok");
        if (opt.jurnal) {
          z.insertAdjacentHTML("afterend", `<p><button class="buton-secundar" id="rv-jurnal" data-actiune="GET /tenants/{tenant_id}/jurnal">Vezi nota în Registrul jurnal →</button></p>`);
          corp.querySelector("#rv-jurnal").addEventListener("click", () => opt.jurnal({ an, luna, evidentiaza: [r.inregistrare_id] }));
        }
      } catch (e) {
        arataMesaj(zm, (e && e.mesaj) || "Nota nu s-a putut genera.", "eroare");
      }
    });
  };
  await deseneaza();
}
