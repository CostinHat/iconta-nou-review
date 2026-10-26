// [lotul 10, deficiența 428, decizia Costin 20.10.2026 „Construiesc acum”] Compensarea creanțelor și datoriilor reciproce cu același
// partener: „tabelă de compensări (factura emisă ↔ factura primită, suma, data) și ecran; fiecare compensare stinge cele două facturi și
// mută TVA-ul prin același punct ca banca și casa.” Temeiul: Codul civil art.1616 (până la concurența celei mai mici datorii), HG 685/1999
// anexa 2 art.5 și 11 (ordinul de compensare, document justificativ), OMFP 1802/2014 pct.56 alin.(3), HG 1/2016 pct.26 alin.(7), (9) și
// CF art.282 alin.(3), (8) — `core/compensari_api.py`.
// DS: fereastra cu tabel (cap.9 v2.96): rezumatul lipit sus `.rezumat-fix` (partenerul, ordinul, totalul), tabelul `.fd-tabel` cu cifrele
// în `.fd-td-num`, acțiunea și mesajul ei lipite jos `.bara-fixa`; confirmarea numește notele și trimite la ele (cap.27).
import { api, ultimaCerere, arataMesaj, bani, curataEroriCamp, dataIso, dataRo, dupaGenerare, esc, eroareCamp, noteGenerate, ALEGE } from "../api.js?v=cb524f997d";

/** „CZ1 din 10.10.2026 · rest 1.210,00” — factura cum o citește omul. */
function doc(f) {
  return `${esc(f.document)} <span class="tip-desc">din ${dataRo(f.data)}</span>`;
}

/**
 * Ecranul compensărilor. `opt.jurnal({evidentiaza})` deschide Registrul jurnal pe notele generate (îl dă cine deschide ecranul; fără el,
 * confirmarea spune unde sunt notele, fără buton).
 */
export async function ecranCompensari(corp, nav, t, opt = {}) {
  let ales = null;          // CUI-ul partenerului ales
  const sume = {};          // ce a scris contabilul pe pereche: {index: suma}
  let mesajDupa = null;     // confirmarea generării, păstrată peste redesenare

  const cerereNoua = ultimaCerere();   // [C103] partenerul / sumele schimbate în șir: numai propunerea ultimei cereri ajunge pe ecran
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
    const actuala = cerereNoua();
    let p;
    try {
      p = await api.get(`/tenants/${t.id}/compensari/propunere`);
      if (!actuala()) return;
    } catch (e) {
      if (!actuala()) return;
      corp.innerHTML = `<h2 class="pf-titlu">Compensări</h2><div id="cz-mesaj"></div>`;
      arataMesaj(corp.querySelector("#cz-mesaj"), "Facturile de compensat nu s-au putut citi" + (e && e.mesaj ? ": " + e.mesaj : "") + ".", "eroare");
      return;
    }
    const parteneri = p.parteneri || [];
    if (ales && !parteneri.some((x) => x.cui === ales)) ales = null;   // partenerul se ALEGE (DS cap.17): niciunul preselectat
    const x = parteneri.find((y) => y.cui === ales);
    const facturi = x ? Object.fromEntries([...x.emise, ...x.primite].map((f) => [f.id, f])) : {};
    const perechi = x ? x.perechi : [];
    const suma = (i) => (sume[i] !== undefined ? sume[i] : perechi[i].suma);
    // [lotul 13, 655] suma scrisă în câmp vine deja citită în format românesc („1.210,50” -> „1210.50”) de câmpul numeric comun
    // (`api.campNumericRo`, DS cap.6): aici nu se mai citește cu un parsator local, care lua „1.210” drept 1,21
    const total = perechi.reduce((s, _q, i) => s + (Number(suma(i)) || 0), 0);
    const tva = (f) => (f.tva_la_incasare
      ? (f.directie === "emisa" ? "TVA la încasare: partea compensată trece 4428 → 4427" : "Deducere amânată: partea plătită trece 4428 → 4426")
      : "TVA exigibil la emitere: nimic de mutat");
    const rand = (q, i) => {
      const e = facturi[q.factura_emisa_id], f = facturi[q.factura_primita_id];
      return `<tr data-pereche="${i}">
        <td>${doc(e)}<div class="tip-desc">${esc(tva(e))}</div></td>
        <td class="fd-td-num">${bani(e.rest)}</td>
        <td>${doc(f)}<div class="tip-desc">${esc(tva(f))}</div></td>
        <td class="fd-td-num">${bani(f.rest)}</td>
        <td class="fd-td-num"><input class="camp-input cz-suma" id="cz-suma-${i}" data-pereche="${i}" inputmode="decimal" style="width:9em"
          aria-label="Suma compensată, ${esc(e.document)} cu ${esc(f.document)}" value="${esc(String(suma(i)))}"></td>
      </tr>`;
    };
    const opriteDe = x ? [...x.emise, ...x.primite].filter((f) => f.afirmatie) : [];   // afirmația tipată a opririi (`motiv`)
    corp.innerHTML = `
      <div class="rezumat-fix" id="cz-rezumat">
        <h2 class="pf-titlu">Compensări</h2>
        <p class="pf-intro">Datoriile reciproce cu același partener se sting prin compensare până la cea mai mică dintre ele (Codul civil
          art.1616), la data ordinului de compensare (HG 685/1999). Fiecare pereche primește o notă 401 = 4111; pe o factură în sistemul TVA
          la încasare, partea compensată mută și TVA-ul, ca o încasare sau o plată.</p>
        ${parteneri.length ? `<div class="grila-doc">
          <label class="camp"><span class="camp-eticheta">Partener</span>
            <select class="camp-input" id="cz-partener">${ales ? "" : ALEGE}${parteneri.map((y) => `<option value="${esc(y.cui)}"${y.cui === ales ? " selected" : ""}>${esc(y.partener || y.cui)} · CUI ${esc(y.cui)}</option>`).join("")}</select></label>
          <label class="camp"><span class="camp-eticheta">Data ordinului de compensare</span>
            <input class="camp-input" id="cz-data" type="date" value="${esc(corp._czData || dataIso(new Date()))}"></label>
          <label class="camp"><span class="camp-eticheta">Numărul ordinului de compensare</span>
            <input class="camp-input" id="cz-numar" maxlength="40" value="${esc(corp._czNumar || "")}"></label>
        </div>
        <p id="cz-total"><b>De compensat:</b> ${bani(total)} lei${x ? ` · <b>de încasat de la partener:</b> ${bani(x.emise.reduce((s, f) => s + Number(f.rest), 0))} lei · <b>de plătit partenerului:</b> ${bani(x.primite.reduce((s, f) => s + Number(f.rest), 0))} lei` : ""}</p>` : ""}
      </div>
      ${!parteneri.length ? `<div class="stare-goala" id="cz-gol">Niciun partener cu facturi emise neîncasate și facturi primite neplătite în același timp.</div>`
        : !ales ? `<div class="stare-goala" id="cz-alege">Alege partenerul: compensarea stinge facturile lui emise cu cele primite.</div>`
        : perechi.length ? `<table class="fd-tabel" id="cz-tabel"><thead><tr><th>Factura emisă (creanța)</th><th class="fd-td-num">Rest de încasat</th>
          <th>Factura primită (datoria)</th><th class="fd-td-num">Rest de plătit</th><th class="fd-td-num">Suma compensată (lei)</th></tr></thead>
          <tbody>${perechi.map(rand).join("")}</tbody></table>`
        : `<div class="stare-goala" id="cz-fara-perechi">Partenerul are facturi deschise în ambele sensuri, dar niciuna nu se poate compensa încă.</div>`}
      ${opriteDe.length ? `<div class="caseta-info" id="cz-oprite"><span class="ci-mesaj">Nu intră în compensare: ${opriteDe.map((f) =>
        `${esc(f.document)} (${f.directie === "emisa" ? "emisă" : "primită"}) — ${esc(f.afirmatie.motiv)}`).join("; ")}.</span></div>` : ""}
      <div class="bara-fixa">
        <div id="cz-mesaj"></div>
        <p class="dec-bara"><button class="buton-primar" id="cz-genereaza" data-genereaza-nota data-actiune="POST /tenants/{tenant_id}/compensari"
          ${perechi.length ? "" : "disabled"}>Generează compensarea</button></p>
      </div>`;
    const sel = corp.querySelector("#cz-partener");
    if (sel) sel.addEventListener("change", () => { ales = sel.value; Object.keys(sume).forEach((k) => delete sume[k]); mesajDupa = null; deseneaza(); });
    const tine = () => {
      corp._czData = (corp.querySelector("#cz-data") || {}).value;
      corp._czNumar = (corp.querySelector("#cz-numar") || {}).value;
    };
    corp.querySelectorAll("#cz-data, #cz-numar").forEach((inp) => inp.addEventListener("change", tine));
    corp.querySelectorAll(".cz-suma").forEach((inp) => inp.addEventListener("change", () => {
      sume[inp.dataset.pereche] = inp.value.trim();
      tine();
      mesajDupa = null;
      deseneaza();
    }));
    if (mesajDupa) {
      const z = corp.querySelector("#cz-mesaj");
      dupaGenerare(z, corp.querySelector("#cz-genereaza"), { titlu: mesajDupa.text, note: mesajDupa.notele });
      if (opt.jurnal && mesajDupa.note.length) {
        z.insertAdjacentHTML("afterend", `<p><button class="buton-secundar" id="cz-jurnal" data-actiune="GET /tenants/{tenant_id}/jurnal">Vezi notele în Registrul jurnal →</button></p>`);
        const ids = mesajDupa.note;
        corp.querySelector("#cz-jurnal").addEventListener("click", () => opt.jurnal({ evidentiaza: ids }));
      }
    }
    const b = corp.querySelector("#cz-genereaza");
    b.addEventListener("click", async () => {
      const zm = corp.querySelector("#cz-mesaj");
      curataEroriCamp(corp);
      const numar = corp.querySelector("#cz-numar").value.trim();
      const data = corp.querySelector("#cz-data").value;
      let rau = false;
      if (!data) { eroareCamp(corp, "cz-data", "Alege data ordinului de compensare: la ea se sting datoriile."); rau = true; }
      if (!numar) { eroareCamp(corp, "cz-numar", "Scrie numărul ordinului de compensare (documentul justificativ al notei)."); rau = true; }
      const trimise = perechi.map((q, i) => ({ factura_emisa_id: q.factura_emisa_id, factura_primita_id: q.factura_primita_id,
        suma: String(suma(i)) }));   // [655] forma canonică a câmpului numeric („1210.50”)
      trimise.forEach((q, i) => {
        const v = Number(q.suma);
        const max = Math.min(Number(facturi[q.factura_emisa_id].rest), Number(facturi[q.factura_primita_id].rest));
        if (!(v > 0) || v > max + 0.005) {
          eroareCamp(corp, `cz-suma-${i}`, `Suma compensată e între 0 și ${bani(max)} lei (restul cel mai mic al celor două facturi).`);
          rau = true;
        }
      });
      if (rau) { arataMesaj(zm, "Completează câmpurile marcate, apoi generează compensarea.", "eroare"); return; }
      try {
        const r = await api.post(`/tenants/${t.id}/compensari`, { data, numar, perechi: trimise.filter((q) => Number(q.suma) > 0) });
        const et = r.note_etichete || [];
        mesajDupa = {
          text: `${r.document}: ${bani(r.total)} lei compensați cu ${r.partener || "partenerul"}, în ${et.length === 1 ? "nota" : "notele"} `
            + `${et.join(", ")} (ciornă, 401 = 4111${(r.note || []).some((n) => n.linii.length > 1) ? ", cu TVA-ul la încasare mutat" : ""}). `
            + "Facturile apar încasate / plătite pe partea compensată; notele le validezi din Registrul jurnal.",
          note: r.inregistrari || [],
          notele: await noteGenerate(t.id, r.inregistrari || [], data),
        };
        corp._czNumar = "";
        Object.keys(sume).forEach((k) => delete sume[k]);
        await deseneaza();
      } catch (e) {
        (e && e.erori_campuri || []).forEach((c) => eroareCamp(corp, c.camp, c.mesaj));
        arataMesaj(zm, (e && e.mesaj) || "Compensarea nu s-a putut genera.", "eroare");
      }
    });
  };
  await deseneaza();
}
