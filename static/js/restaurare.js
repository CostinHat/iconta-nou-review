// restaurare.js — [15.1, 725] după F5 aplicația revine la fereastra în care erai, nu la ecranul cabinetului. O fereastră de lucru care vrea asta o
// memorează la deschidere (`memoreazaFereastra`) și o uită când omul iese din ea (`uitaFereastra`: Renunță, salvare, înapoi, închidere). La
// pornire, după ce ecranul cabinetului e desenat, `restaureazaFereastra` o redeschide pe aceeași firmă, prin aceleași butoane pe care le apasă
// omul (cardul firmei, apoi butonul operațiunii). Memoria stă în sessionStorage: ține de fila browserului, nu de contul de pe alt calculator.
const CHEIE = "iconta_fereastra_deschisa";
export function memoreazaFereastra(f) {
  try { sessionStorage.setItem(CHEIE, JSON.stringify({ ...f, la: Date.now() })); } catch { /* fără stocare: F5 duce la ecranul cabinetului */ }
}
/** [15.1-E3, 725.3] ce a scris omul în fereastra de sus (id -> valoare): se redă după redeschidere, ca fereastra să revină „cu datele ei”. Parolele și cheile nu se rețin. */
const _NEMEMORABIL = /parola|password|token|cheie|secret|cnp|iban|card/i;
export function memoreazaCampul(el) {
  if (!el || !el.id || el.type === "password" || el.type === "file" || el.type === "hidden" || _NEMEMORABIL.test(el.id + " " + (el.name || ""))) return;
  try {
    const v = JSON.parse(sessionStorage.getItem(CHEIE) || "null");
    if (!v || !Array.isArray(v.drum)) return;
    v.campuri = v.campuri || {};
    if (!(el.id in v.campuri) && Object.keys(v.campuri).length >= 60) return;
    v.campuri[el.id] = el.type === "checkbox" || el.type === "radio" ? { bifat: !!el.checked } : { valoare: el.value };
    sessionStorage.setItem(CHEIE, JSON.stringify(v));
  } catch { /* fără stocare: fereastra revine fără datele ei */ }
}
export function uitaFereastra() {
  try { sessionStorage.removeItem(CHEIE); } catch { /* idem */ }
}
function _citeste() {
  try { const v = JSON.parse(sessionStorage.getItem(CHEIE) || "null"); return v && Array.isArray(v.drum) ? v : null; } catch { return null; }
}
const _asteapta = (sel, ms = 15000) => new Promise((ok) => {
  const t0 = Date.now();
  const tick = () => { const el = document.querySelector(sel); if (el) return ok(el); if (Date.now() - t0 > ms) return ok(null); setTimeout(tick, 150); };
  tick();
});
/** Redeschide fereastra memorată: Firme › firma (după nume) › apoi fiecare buton din `drum`, în ordine — aceiași pași ai omului. */
export async function restaureazaFereastra() {
  const f = _citeste();
  if (!f || !Array.isArray(f.drum) || !f.drum.length) return false;
  const esec = () => { uitaFereastra(); return false; };
  if (f.nume) {   // fereastră de firmă: Firme › firma (după nume); fereastra de cabinet începe direct din cardurile paginii
    const cardFirme = await _asteapta("button.cab-card:has([data-cheie='firme'])", 20000);
    if (!cardFirme) return esec();
    cardFirme.click();
    const existente = await _asteapta("#opt-existente, #firme-lista button.firme-rand", 15000);
    if (existente && existente.id === "opt-existente") existente.click();
    if (!(await _asteapta("#firme-lista button.firme-rand", 15000))) return esec();
    const rand = [...document.querySelectorAll("#firme-lista button.firme-rand")].find((b) => (b.textContent || "").includes(f.nume));
    if (!rand) return esec();
    rand.click();
  } else if (!(await _asteapta("button.cab-card", 20000))) return esec();
  for (const sel of f.drum) {
    const el = await _asteapta(sel, 20000);
    if (!el) return esec();
    const tab = el.closest(".op-grup[hidden]");   // formularul Operațiunilor din grupul ascuns al listei
    if (tab) { const b = document.querySelector(`.rap-tab[data-grup="${tab.dataset.frecventa}"]`); if (b) b.click(); }
    el.click();
  }
  // [15.1-E3, 725.3] datele fereastrei: în ordinea în care au fost scrise (o listă schimbată poate aduce alte câmpuri), de două ori
  const campuri = Object.entries(f.campuri || {});
  for (let trecere = 0; trecere < 2 && campuri.length; trecere++) {
    for (const [id, c] of campuri) {
      const el = await _asteapta(`[id="${CSS.escape(id)}"]`, trecere ? 1500 : 8000);
      if (!el) continue;
      if ("bifat" in c) { if (el.checked !== c.bifat) el.click(); continue; }
      if (el.value === c.valoare) continue;
      el.value = c.valoare;
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
      await new Promise((r) => setTimeout(r, 120));
    }
  }
  return true;
}
