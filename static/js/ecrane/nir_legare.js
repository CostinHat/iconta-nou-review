// nir_legare.js — alegerea NIR-ului „fără factură” la contarea facturii primite (decizia Costin 08.10.2026, pct.2).
//
// „la contarea facturii se propune legarea cu NIR-ul nelegat de la același furnizor (preselecție permisă — dedusă din date,
// vizibilă, modificabilă). Dacă contabilul nu leagă, confirmă explicit «altă livrare»; nu se blochează.”
//
// UN SINGUR LOC pentru cele trei drumuri care contează o factură primită (Contează din Facturi, Validează din SPV,
// Contabilizează facturile din controlul fiscal): serverul refuză contarea fără alegere (`cod: NIR_DE_LEGAT`, cu `candidati`
// și `propus`), iar `cuLegareaNir` arată caseta-poartă (DS cap.5 v2.14: două alegeri care merg amândouă înainte) și retrimite
// cu alegerea. Preselecția = `propus` (DS cap.17 v2.79: dedusă din date — același furnizor, același cost —, vizibilă, schimbabilă);
// fără propunere, „— alege —”.
import { esc, ALEGE, cereAlegerile, curataEroriCamp } from "../api.js?v=2561dbfd34";

// Refuzul care cere alegerea NIR-ului (oricare din codurile alegerii: de ales, nelegabil, cost diferit) — poartă candidații.
export function refuzLegareNir(e) {
  const d = e && e.detaliu;
  return d && Array.isArray(d.candidati) && d.candidati.length ? d : null;
}

// Caseta-poartă; se rezolvă cu alegerea: {nir_id} sau {alta_livrare: true}. `actiune` = ruta care primește alegerea (drepturi).
export function alegeLegareaNir(zona, d, actiune) {
  return new Promise((rezolva) => {
    const opt = d.candidati.map((c) => `<option value="${esc(String(c.id))}"${c.id === d.propus ? " selected" : ""}>${esc(c.eticheta)}${c.id === d.propus ? " — propus" : ""}</option>`).join("");
    zona.innerHTML = `
      <div class="caseta-poarta">
        <div class="cp-mesaj">${esc(d.mesaj || "")}</div>
        <label class="camp"><span class="camp-eticheta">NIR-ul acestei livrări<span class="oblig">*</span></span>
          <span class="camp-ajutor">${d.propus ? "Propus din date: același furnizor și același cost fără TVA ca factura. Îl poți schimba." : "Niciun NIR nu are costul facturii — alege-l pe cel al livrării, sau confirmă „altă livrare”."}</span>
          <select class="camp-input" id="nir-legat" aria-label="NIR-ul acestei livrări">${d.propus ? "" : ALEGE}${opt}</select></label>
        <div class="cp-butoane">
          <button class="buton-primar" id="nir-leaga" data-actiune="${esc(actiune)}">Leagă de NIR-ul ales</button>
          <button class="buton-secundar" id="nir-alta" data-actiune="${esc(actiune)}">Altă livrare — nu e niciunul</button>
        </div>
      </div>`;
    zona.querySelector("#nir-leaga").addEventListener("click", () => {
      curataEroriCamp(zona);
      if (cereAlegerile(zona, ["#nir-legat"])) return;   // [FAPT_FISCAL_NECERUT] fără alegere nu se trimite
      const id = Number(zona.querySelector("#nir-legat").value);
      zona.innerHTML = "";
      rezolva({ nir_id: id });
    });
    zona.querySelector("#nir-alta").addEventListener("click", () => { zona.innerHTML = ""; rezolva({ alta_livrare: true }); });
  });
}

// Trimite; dacă serverul cere alegerea NIR-ului, o cere omului în `zona` și retrimite cu ea. `trimite(alegere)` face cererea.
export async function cuLegareaNir(zona, actiune, trimite, alegere = {}) {
  try {
    return await trimite(alegere);
  } catch (e) {
    const d = refuzLegareNir(e);
    if (!d) throw e;
    return cuLegareaNir(zona, actiune, trimite, await alegeLegareaNir(zona, d, actiune));
  }
}

// Parametrii de interogare ai alegerii, pentru `POST …/contabilizeaza`.
export function interogareLegare(alegere) {
  if (alegere && alegere.alta_livrare) return "alta_livrare=true";
  if (alegere && alegere.nir_id) return "nir_id=" + encodeURIComponent(alegere.nir_id);
  return "";
}
