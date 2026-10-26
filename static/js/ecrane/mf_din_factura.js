// static/js/ecrane/mf_din_factura.js — [lotul 13, deficiența 601, decizia Costin (a)] mijlocul fix de pe factura primită.
// „Pe ecranul Mijloace fixe nu există buton de adăugare a unui mijloc fix (la achiziții).” Decizia: linia „imobilizare” pe factura
// primită — linia pe un cont de imobilizare amortizabilă (203 / 205 / 208 / 212 / 213 / 214) cere, sub ea, datele fișei: codul din
// Catalogul HG 2139/2004 (cu plaja duratei), durata, data punerii în funcțiune, metoda. La validarea facturii, activul intră în registru
// legat de nota ei și devine activ când nota e validată (serverul: `core/mf_din_factura.py`). Aceeași bucată pentru factura din XML (`pr`,
// liniile de la 0) și pentru factura introdusă de mână (`pm`, liniile de la 1).
import { api, ultimaCerere, cate, esc, ALEGE } from "../api.js?v=cb524f997d";

const GRUPE = ["203", "205", "208", "212", "213", "214"];
export const eImobilizare = (cont) => GRUPE.includes(String(cont || "").trim().slice(0, 3));
const METODE = [["liniara", "Liniară"], ["degresiva", "Degresivă"], ["accelerata", "Accelerată"]];

// câmpurile fișei sub linia `idx` (ascunse cât linia nu e pe un cont de imobilizare)
export function campuriMf(pre, idx) {
  const id = (c) => `${pre}-mf${idx}-${c}`;
  return `<div class="mf-din-factura" data-mf="${idx}" hidden>
    <span class="camp-ajutor">Linia e pe un cont de imobilizare: mijlocul fix intră în registru din factura asta, la validarea notei ei.</span>
    <div class="grila-campuri grila-campuri-compacta">
      <div class="camp"><label class="camp-eticheta" for="${id("cod_catalog")}">Cod din catalog (HG 2139/2004)</label>
        <input type="text" class="camp-input mf-df-catalog" id="${id("cod_catalog")}"><div class="em-cui-stare" id="${id("cod_catalog")}-stare" aria-live="polite"></div></div>
      <div class="camp"><label class="camp-eticheta" for="${id("dnf_luni")}">Durata normală (luni)<span class="oblig">*</span></label>
        <input type="number" step="1" class="camp-input" id="${id("dnf_luni")}"></div>
      <div class="camp"><label class="camp-eticheta" for="${id("data_pif")}">Data punerii în funcțiune<span class="oblig">*</span></label>
        <input type="date" class="camp-input" id="${id("data_pif")}"></div>
      <div class="camp"><label class="camp-eticheta" for="${id("metoda")}">Metoda de amortizare<span class="oblig">*</span></label>
        <select class="camp-input" id="${id("metoda")}" data-butoane="">${ALEGE}${METODE.map(([v, l]) => `<option value="${v}">${l}</option>`).join("")}</select></div>
    </div></div>`;
}

// leagă câmpurile de conturile liniilor: `contLinie(idx)`, `contFactura()`, `indici()` (ordinea liniilor). -> { reimprospateaza, date }
export function pornesteMf(corp, tenantId, pre, { contLinie, contFactura, indici }) {
  const scrise = new Map();   // ce a scris omul, după id — rămâne când formularul își redesenează liniile
  const cont = (idx) => String(contLinie(idx) || "").trim() || String(contFactura() || "").trim();
  const cerereCatalog = ultimaCerere();   // o citire veche a catalogului nu se scrie peste una nouă
  const reimprospateaza = () => {
    for (const idx of indici()) {
      const z = corp.querySelector(`[data-mf="${idx}"]`);
      if (!z) continue;
      z.hidden = !eImobilizare(cont(idx));
      z.querySelectorAll("input, select").forEach((el) => { if (scrise.has(el.id) && !el.value) el.value = scrise.get(el.id); });
    }
  };
  corp.addEventListener("input", (ev) => {
    const el = ev.target;
    if (el.closest && el.closest(".mf-din-factura")) scrise.set(el.id, el.value);
    if (el.matches && el.matches(".pr-cont-linie, #pr-cont")) reimprospateaza();
  });
  corp.addEventListener("change", async (ev) => {
    const el = ev.target;
    if (!el.closest || !el.closest(".mf-din-factura")) return;
    scrise.set(el.id, el.value);
    if (!el.classList.contains("mf-df-catalog")) return;
    // codul din catalog: denumirea și plaja duratei, sub câmp (aceeași citire ca în Operațiuni speciale, 521)
    const st = corp.querySelector(`#${el.id}-stare`);
    const actuala = cerereCatalog();
    const cod = el.value.trim();
    st.className = "em-cui-stare"; st.textContent = "";
    if (!cod) return;
    try {
      const r = await api.get(`/tenants/${tenantId}/operatiuni-date?ce=catalog&tip=${encodeURIComponent(cod)}`);
      if (!actuala()) return;
      if (r.gasit) { st.innerHTML = `<span class="em-cui-info">${esc(r.denumire)} · durata între ${r.ani_min * 12} și ${cate(r.ani_max * 12, "lună", "luni")}</span>`; }
      else { st.className = "em-cui-stare em-cui-rau"; st.textContent = "Codul nu e în Catalogul HG 2139/2004."; }
    } catch { if (!actuala()) return; st.className = "em-cui-stare em-cui-rau"; st.textContent = "Catalogul nu s-a putut citi — reîncearcă."; }
  });
  // datele fișei pe fiecare linie, în ordinea liniilor: null pe liniile care nu sunt pe un cont de imobilizare
  const date = () => indici().map((idx) => {
    if (!eImobilizare(cont(idx))) return null;
    const v = (c) => (corp.querySelector(`#${pre}-mf${idx}-${c}`) || {}).value || "";
    return { cod_catalog: v("cod_catalog").trim(), dnf_luni: v("dnf_luni").trim(), data_pif: v("data_pif"), metoda: v("metoda") };
  });
  reimprospateaza();
  return { reimprospateaza, date };
}
