// restaurare.js — [15.1, 725] după F5 aplicația revine la fereastra în care erai, nu la ecranul cabinetului. O fereastră de lucru care vrea asta o
// memorează la deschidere (`memoreazaFereastra`) și o uită când omul iese din ea (`uitaFereastra`: Renunță, salvare, înapoi, închidere). La
// pornire, după ce ecranul cabinetului e desenat, `restaureazaFereastra` o redeschide pe aceeași firmă, prin aceleași butoane pe care le apasă
// omul (cardul firmei, apoi butonul operațiunii). Memoria stă în sessionStorage: ține de fila browserului, nu de contul de pe alt calculator.
const CHEIE = "iconta_fereastra_deschisa";
export function memoreazaFereastra(f) {
  try { sessionStorage.setItem(CHEIE, JSON.stringify({ ...f, la: Date.now() })); } catch { /* fără stocare: F5 duce la ecranul cabinetului */ }
}
export function uitaFereastra() {
  try { sessionStorage.removeItem(CHEIE); } catch { /* idem */ }
}
function _citeste() {
  try { const v = JSON.parse(sessionStorage.getItem(CHEIE) || "null"); return v && v.ecran ? v : null; } catch { return null; }
}
const _asteapta = (sel, ms = 15000) => new Promise((ok) => {
  const t0 = Date.now();
  const tick = () => { const el = document.querySelector(sel); if (el) return ok(el); if (Date.now() - t0 > ms) return ok(null); setTimeout(tick, 150); };
  tick();
});
/** Redeschide fereastra memorată: Firme › firma (după nume) › cardul „Operațiuni speciale” › butonul formularului — aceiași pași ca ai omului. */
export async function restaureazaFereastra() {
  const f = _citeste();
  if (!f || f.ecran !== "operatiuni" || !f.nume) return false;
  const esec = () => { uitaFereastra(); return false; };
  const cardFirme = await _asteapta("button.cab-card:has([data-cheie='firme'])", 20000);
  if (!cardFirme) return esec();
  cardFirme.click();
  const existente = await _asteapta("#opt-existente, #firme-lista button.firme-rand", 15000);
  if (existente && existente.id === "opt-existente") existente.click();
  if (!(await _asteapta("#firme-lista button.firme-rand", 15000))) return esec();
  const rand = [...document.querySelectorAll("#firme-lista button.firme-rand")].find((b) => (b.textContent || "").includes(f.nume));
  if (!rand) return esec();
  rand.click();
  const card = await _asteapta("#fa-operatiuni", 20000);
  if (!card) return esec();
  card.click();
  const buton = await _asteapta(`button[data-op="${String(f.cheie).replace(/[^\w-]/g, "")}"]`);
  if (!buton) return esec();
  const tab = buton.closest(".op-grup[hidden]");
  if (tab) { const b = document.querySelector(`.rap-tab[data-grup="${tab.dataset.frecventa}"]`); if (b) b.click(); }
  buton.click();
  return true;
}
