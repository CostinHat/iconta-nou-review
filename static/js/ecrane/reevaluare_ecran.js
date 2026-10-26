// [lotul 10, deficiența 429, comanda Costin 10.1 pct.8] Reevaluarea lunară în valută, PROPUSĂ de aplicație: „La închiderea lunii,
// aplicația propune singură creanțele și datoriile în valută neîncasate (pe factură), disponibilitățile în valută, cursul din evidență,
// cursul BNR din ultima zi bancară și diferența pe 665/765; contabilul verifică și generează nota.” Temeiul: OMFP 1802/2014 pct.325
// (`core/reevaluare_valuta.py`).
// [lotul 11, 429 — comanda 11.1 pct.11 și decizia 10.3] UN SINGUR FORMULAR: se deschide din „Închidere lună” (butonul „Reevaluare
// valută”, mereu acolo, nu numai când reevaluarea oprește închiderea); formularul manual din Operațiuni a fost scos. Creanțele și datoriile
// sunt pe PARTENER (facturi − plăți, legate sau nelegate); facturile în valută care nu intră se spun, cu motivul (caseta de deasupra
// butonului, DS cap.6 v2.91 „rândurile care nu intră”); ajustarea manuală (un cont pe care aplicația nu-l propune) e în același formular,
// marcată „adăugat de tine”, rând cu rând (DS cap.24: re-randare din model, fiecare rând adăugat se poate scoate cu `.buton-sters`,
// validarea pe server, erorile lângă câmp — toate deodată, `erori_campuri`).
// DS: tabelul `.fd-tabel` cu cifrele în `.fd-td-num` (cap.9), rezumatul lipit sus `.rezumat-fix`, acțiunea și mesajul ei lipite jos
// `.bara-fixa` (cap.6, v2.92), confirmarea care numește nota și consecința rămâne pe ecran (cap.27).
import { api, ultimaCerere, pastreazaCampulActiv, arataMesaj, bani, cursValutar as curs, dataIso, dupaGenerare, esc, dataRo, eroareCamp, noteGenerate, stareNota, pasNota, selectDaNu, daNu, cereAlegerile, focusFaraSalt } from "../api.js?v=9bcf50c899";

import { MONEDE } from "./operatiuni_ecran.js?v=54dc44fa27";   // [lotul 13, 631] aceeași listă de monede ca la factură

const FEL = { creanta: "Creanță", datorie: "Datorie", disponibil: "Disponibil" };
// [lotul 13, deficiența 631] „Moneda se scrie de mână; trebuie aleasă din lista de coduri BNR, ca la factură”: select, nu text
const selectMoneda = (atrib, val, eticheta, clasa) => `<select class="camp-input ${clasa}" ${atrib} aria-label="${esc(eticheta)}"><option value=""${val ? "" : " selected"}>— moneda —</option>${
  (val && !MONEDE.includes(val) ? [val] : []).concat(MONEDE).map((m) => `<option value="${esc(m)}"${m === val ? " selected" : ""}>${esc(m)}</option>`).join("")}</select>`;

/** De unde vine cursul din evidență: factura, media facturilor, reevaluarea anterioară sau soldul contului (lei / valută). */
function dinEvidenta(e) {
  if (!e.curs_evidenta_din) return "";
  if (e.curs_evidenta_din === "factura") return "cursul facturii";
  if (e.curs_evidenta_din === "medie") return "sold în lei / sold în valută, pe facturi";
  if (e.curs_evidenta_din === "sold") return "sold în lei / sold în valută";
  return "reevaluarea din " + dataRo(e.curs_evidenta_din);
}

/** Plățile unui partener, sub sold: cele nelegate de factură (intră în sold) și cele care cer legarea (partener cu mai multe monede). */
function plati(e) {
  const fraza = (xs) => xs.map((p) => `${bani(p.lei)} lei din ${dataRo(p.data)}${p.document ? " (" + esc(p.document) + ")" : ""}`).join("; ");
  return ((e.plati_nelegate || []).length ? `<div class="tip-desc">plăți nelegate de factură, scăzute din sold: ${fraza(e.plati_nelegate)}</div>` : "")
    + ((e.plati_de_legat || []).length ? `<div class="tip-desc rv-de-legat">de legat de factură (partenerul are facturi în mai multe monede):
      ${fraza(e.plati_de_legat)}</div>` : "");
}

/**
 * Ecranul propunerii. `opt.jurnal({an, luna, evidentiaza})` deschide Registrul jurnal pe nota generată (îl dă cine deschide ecranul;
 * fără el, confirmarea spune unde e nota, fără buton).
 */
export async function ecranReevaluareValuta(corp, nav, t, an, luna, opt = {}) {
  const completari = {};   // ce a scris contabilul pe ecran, pe element: {cheie: {sold_valuta, moneda, clauza}}
  const manuale = [];      // ajustarea manuală: [{cont, moneda, sold_valuta, clauza}] — rândurile adăugate de contabil
  let ultima = null;       // ultima propunere primită: un refuz al completărilor nu golește ecranul
  const cerereNoua = ultimaCerere();   // [C103] contul, moneda și soldul editate în șir: numai răspunsul ultimei cereri ajunge pe ecran
  // propunerea se recalculează pe server la orice completare (contabilul vede diferența înainte de generare); un refuz al completărilor
  // păstrează ultima propunere pe ecran și pune fiecare eroare lângă câmpul ei
  const deseneaza = async () => {
    if (!ultima) corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
    const actuala = cerereNoua();
    try {
      const q = (Object.keys(completari).length ? `&completari=${encodeURIComponent(JSON.stringify(completari))}` : "")
        + (manuale.length ? `&manuale=${encodeURIComponent(JSON.stringify(manuale))}` : "");
      const r = await api.get(`/tenants/${t.id}/reevaluare-valuta?an=${an}&luna=${luna}${q}`);
      if (!actuala()) return;
      ultima = r;
      pastreazaCampulActiv(corp, () => randeaza(ultima, null));   // [C103] câmpul în care omul scrie deja nu se pierde
    } catch (e) {
      if (!actuala()) return;
      if (!ultima || !(e && (e.erori_campuri || []).length)) {
        corp.innerHTML = `<h2 class="pf-titlu">Reevaluare valută</h2><div id="rv-mesaj"></div>`;
        arataMesaj(corp.querySelector("#rv-mesaj"), "Propunerea nu s-a putut calcula" + (e && e.mesaj ? ": " + e.mesaj : "") + ".", "eroare");
        return;
      }
      pastreazaCampulActiv(corp, () => randeaza(ultima, e));
    }
  };
  const randeaza = (p, refuz) => {
    const el = p.elemente || [];
    const tot = p.totaluri || {};
    const camp = (e, c, eticheta) => {
      if (!(e.editabile || []).includes(c)) {
        return c === "moneda" ? esc(e.moneda || "—") : (e.sold_valuta === null ? "—" : bani(e.sold_valuta));
      }
      const val = (completari[e.cheie] || {})[c] ?? (c === "moneda" ? (e.moneda || "") : (e.sold_valuta ?? ""));
      if (c === "moneda") return selectMoneda(`id="rv-${c}-${esc(e.cheie)}" data-cheie="${esc(e.cheie)}" data-camp="${c}" style="width:7em"`, val, eticheta, "rv-camp");
      return `<input class="camp-input rv-camp" id="rv-${c}-${esc(e.cheie)}" data-cheie="${esc(e.cheie)}" data-camp="${c}"
        aria-label="${esc(eticheta)}" value="${esc(val)}" inputmode="decimal" style="width:9em">`;
    };
    const nume = (e) => e.document || e.partener || "contul " + e.cont;
    const rand = (e) => `<tr data-cheie="${esc(e.cheie)}">
        <td>${FEL[e.fel] || ""}${e.manual ? ` <span class="tip-desc rv-manual">adăugat de tine</span>` : ""}<div class="tip-desc">${esc(e.document || "")}</div></td>
        <td>${esc(e.partener || "")}${e.clauza ? `<div class="tip-desc">în lei cu clauză valutară (668 / 768)</div>` : ""}</td>
        <td>${esc(e.cont)}</td>
        <td>${camp(e, "moneda", `Moneda, ${nume(e)}`)}</td>
        <td class="fd-td-num">${camp(e, "sold_valuta", `Sold în valută, ${nume(e)}`)}${e.estimat ? `<div class="tip-desc">estimat din plățile în lei — verifică</div>` : ""}${e.sold_anterior && e.sold_valuta === null ? `<div class="tip-desc">luna trecută: ${bani(e.sold_anterior)}</div>` : ""}${plati(e)}</td>
        <td class="fd-td-num">${curs(e.curs_evidenta)}<div class="tip-desc">${esc(dinEvidenta(e))}</div></td>
        <td class="fd-td-num">${bani(e.lei_evidenta)}</td>
        <td class="fd-td-num">${curs(e.curs_bnr)}${e.data_curs ? `<div class="tip-desc">din ${dataRo(e.data_curs)}${e.curs_provizoriu ? " — provizoriu" : ""}</div>` : ""}</td>
        <td class="fd-td-num">${e.diferenta === undefined || e.diferenta === null ? "—" : bani(e.diferenta)}${e.curs_provizoriu && e.diferenta !== undefined && e.diferenta !== null ? `<div class="tip-desc rv-provizoriu">provizorie</div>` : ""}</td>
        <td>${e.cont_diferenta ? esc(e.cont_diferenta) : (e.motiv_curs ? `<span class="tip-desc">${esc(e.motiv_curs)}</span>`
          : ((e.de_completat || []).length || (e.plati_de_legat || []).length ? `<span class="tip-desc">de completat</span>` : "—"))}</td>
      </tr>`;
    // rândurile ajustării manuale încă neprimite de server (contul tocmai adăugat, sau unul refuzat): câmpurile lor, lângă tabel
    const inPropunere = new Set(el.filter((e) => e.rand_manual !== undefined && e.rand_manual !== null).map((e) => e.rand_manual));
    const randManual = (m, i) => `<tr data-rand-manual="${i}">
        <td><input class="camp-input rv-m" id="rv-m${i}-cont" data-i="${i}" data-camp="cont" aria-label="Contul ajustării ${i + 1}"
          value="${esc(m.cont || "")}" style="width:8em"></td>
        <td>${selectMoneda(`id="rv-m${i}-moneda" data-i="${i}" data-camp="moneda" style="width:7em"`, m.moneda || "", `Moneda ajustării ${i + 1}`, "rv-m")}</td>
        <td><input class="camp-input rv-m" id="rv-m${i}-sold_valuta" data-i="${i}" data-camp="sold_valuta" inputmode="decimal"
          aria-label="Soldul în valută al ajustării ${i + 1}" value="${esc(m.sold_valuta || "")}" style="width:9em"></td>
        <td>${selectDaNu(`id="rv-m${i}-clauza" class="rv-m" data-i="${i}" data-camp="clauza"`, m.clauza, `În lei cu clauză valutară (668 / 768), ajustarea ${i + 1}`)}</td>
        <td>${inPropunere.has(i) ? `<span class="tip-desc">în tabel, mai sus</span>` : ""}</td>
        <td><button class="buton-sters buton-mic rv-m-scoate" data-i="${i}" data-fara-actiune aria-label="Scoate ajustarea ${i + 1}">Scoate</button></td>
      </tr>`;
    const neincluse = p.neincluse || [];
    corp.innerHTML = `
      <div class="rezumat-fix" id="rv-rezumat">
        <h2 class="pf-titlu">Reevaluare valută — ${dataRo(`${an}-${String(luna).padStart(2, "0")}-01`, "luna_an_numeric")}</h2>
        <p class="pf-intro">La sfârșitul lunii, creanțele și datoriile în valută (pe partener: facturi minus plăți, legate de factură sau nu)
          și disponibilitățile în valută se evaluează la cursul BNR din ultima zi bancară a lunii (OMFP 1802/2014 pct.325); diferența merge
          pe 765 (favorabilă) sau 665 (nefavorabilă). Avansurile (409, 419) nu se reevaluează (pct.316 alin.(2)). Verifică propunerea,
          completează ce lipsește și generează nota.</p>
        <p id="rv-totaluri"><b>Venituri:</b> ${bani(tot.venit)} lei · <b>Cheltuieli:</b> ${bani(tot.cheltuiala)} lei ·
          <b>Net:</b> ${bani(tot.net)} lei${tot.provizoriu ? " (provizoriu)" : ""}${tot.de_completat ? ` · <b>De completat:</b> ${esc((tot.de_completat_ce || []).join("; "))}` : ""}${tot.de_legat ? ` · <b>Plăți de legat:</b> ${tot.de_legat}` : ""}</p>
      </div>
      ${p.luna_in_curs ? `<div class="caseta-info" id="rv-luna-in-curs"><span class="ci-mesaj">${esc(p.luna_in_curs)} Propunerea e informativă:
        nota se generează după sfârșitul lunii.</span></div>` : ""}
      ${(p.curs_provizoriu || []).length ? `<div class="caseta-info" id="rv-curs-provizoriu"><span class="ci-mesaj">${p.curs_provizoriu.map(esc).join(" ")}</span></div>` : ""}
      ${(p.ciorna_lunii || []).length ? `<div class="caseta-info"><span class="ci-mesaj">Luna are deja nota de reevaluare în ciornă;
        „Generează nota” o înlocuiește cu propunerea de acum.</span></div>` : ""}
      ${el.length ? `<table class="fd-tabel" id="rv-tabel"><thead><tr><th>Element</th><th>Partener / cont</th><th>Cont</th><th>Moneda</th>
        <th class="fd-td-num">Sold în valută</th><th class="fd-td-num">Curs din evidență</th><th class="fd-td-num">Sold în lei</th>
        <th class="fd-td-num">Curs BNR</th><th class="fd-td-num">Diferență (lei)</th><th>Cont diferență</th></tr></thead>
        <tbody>${el.map(rand).join("")}</tbody></table>`
        : `<div class="stare-goala" id="rv-gol">Nicio creanță, datorie sau disponibilitate în valută la sfârșitul lunii.</div>`}
      <h3 class="pf-subtitlu">Ajustare manuală</h3>
      <p class="ecran-nota">Un cont în valută pe care aplicația nu-l propune (un împrumut, un depozit, o creanță în lei cu clauză valutară):
        scrii contul, moneda și soldul în valută din document; soldul în lei îl ia aplicația din evidență. Luna următoare contul revine
        singur aici.</p>
      ${manuale.length ? `<table class="fd-tabel" id="rv-manuale"><thead><tr><th>Cont</th><th>Moneda</th><th>Sold în valută</th><th>În lei cu clauză valutară (668 / 768)</th><th>Stare</th><th>Acțiune</th></tr></thead>
        <tbody>${manuale.map(randManual).join("")}</tbody></table>` : ""}
      <p><button class="buton-secundar" id="rv-m-adauga" data-fara-actiune>Adaugă un cont</button></p>
      ${neincluse.length ? `<div class="caseta-atentie" id="rv-neincluse"><div class="ca-mesaj"><b>Facturi în valută care nu intră în
        reevaluare (${neincluse.length})</b><ul style="margin:6px 0 0;padding-left:18px">${neincluse.map((f) =>
          `<li>${esc(f.document || "")}${f.partener ? " — " + esc(f.partener) : ""}: ${esc(f.motiv)}</li>`).join("")}</ul></div></div>` : ""}
      <div class="bara-fixa">
        <div id="rv-mesaj"></div>
        <p class="dec-bara"><button class="buton-primar" id="rv-genereaza" data-genereaza-nota data-actiune="POST /tenants/{tenant_id}/reevaluare-valuta/nota"
          ${(el.length || manuale.length) && !p.luna_in_curs && !(p.curs_provizoriu || []).length ? "" : "disabled"}>Generează nota</button></p>
      </div>`;
    const zm = corp.querySelector("#rv-mesaj");
    if (refuz) {
      (refuz.erori_campuri || []).forEach((c) => eroareCamp(corp, c.camp, c.mesaj));
      arataMesaj(zm, refuz.mesaj || "Corectează câmpurile marcate.", "eroare");
    }
    corp.querySelectorAll(".rv-camp").forEach((inp) => inp.addEventListener("change", () => {
      const c = completari[inp.dataset.cheie] = completari[inp.dataset.cheie] || {};
      c[inp.dataset.camp] = inp.value.trim();
      deseneaza();   // propunerea se recalculează pe server, cu ce s-a scris: contabilul vede diferența înainte de generare
    }));
    corp.querySelectorAll(".rv-m").forEach((inp) => inp.addEventListener("change", () => {
      // [DS cap.17 v2.79] clauza e un DA/NU situațional (`selectDaNu`): „— alege —” = null, nu „Nu” ales de ecran
      manuale[Number(inp.dataset.i)][inp.dataset.camp] = inp.dataset.camp === "clauza" ? daNu(inp) : inp.value.trim();
      deseneaza();
    }));
    corp.querySelectorAll(".rv-m-scoate").forEach((b) => b.addEventListener("click", () => {
      manuale.splice(Number(b.dataset.i), 1);
      deseneaza();
    }));
    corp.querySelector("#rv-m-adauga").addEventListener("click", () => {
      // rândul nou se adaugă în model și ecranul se re-randează din el (DS cap.24 regula 1), fără cerere: e încă gol
      manuale.push({ cont: "", moneda: "", sold_valuta: "", clauza: null });
      randeaza(p, null);
      focusFaraSalt(corp.querySelector(`#rv-m${manuale.length - 1}-cont`));   // [DS cap.9 v2.86] fără salt
    });
    corp.querySelector("#rv-genereaza").addEventListener("click", async () => {
      // [DS cap.17 v2.79, FAPT_FISCAL_NECERUT] clauza fiecărui rând manual (765/665 sau 768/668) o alege omul; serverul refuză și el
      if (cereAlegerile(corp, manuale.map((_, i) => `#rv-m${i}-clauza`))) return;
      try {
        const r = await api.post(`/tenants/${t.id}/reevaluare-valuta/nota`, { an, luna, completari, manuale });
        await deseneaza();
        const z = corp.querySelector("#rv-mesaj");
        if (!r.inregistrare_id) { arataMesaj(z, r.mesaj || "Nicio diferență de curs de înregistrat în luna aceasta.", "ok"); return; }
        // [279, clasa] starea reală a notei (ciornă / trimisă la validare / notă internă) și pasul următor, nu „ciornă” scris de mână
        // [8c] confirmarea verde prin helperul unic: titlul, conturile notei (din Registrul jurnal), butonul inactiv cu motivul
        dupaGenerare(z, corp.querySelector("#rv-genereaza"), {
          titlu: `Nota de reevaluare ${r.nota_eticheta || ""} (${stareNota(r)})${r.inlocuita ? ", în locul notei nevalidate de dinainte" : ""}`,
          note: await noteGenerate(t.id, [r.inregistrare_id], dataIso(new Date(an, luna, 0))),
          detalii: [`Venituri: ${bani(r.venit)} lei, cheltuieli: ${bani(r.cheltuiala)} lei. După validare reevaluarea nu mai oprește închiderea lunii.`],
          pas: pasNota(r),
        });
        if (opt.jurnal) {
          z.insertAdjacentHTML("afterend", `<p><button class="buton-secundar" id="rv-jurnal" data-actiune="GET /tenants/{tenant_id}/jurnal">Vezi nota în Registrul jurnal →</button></p>`);
          corp.querySelector("#rv-jurnal").addEventListener("click", () => opt.jurnal({ an, luna, evidentiaza: [r.inregistrare_id] }));
        }
      } catch (e) {
        // backendul e poarta (DS cap.24): fiecare câmp lipsă / plată de legat, lângă rândul lui, toate deodată
        (e && e.erori_campuri || []).forEach((c) => eroareCamp(corp, c.camp, c.mesaj));
        arataMesaj(zm, (e && e.mesaj) || "Nota nu s-a putut genera.", "eroare");
      }
    });
  };
  await deseneaza();
}
