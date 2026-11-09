// [17.5-C, 817 — decizia Costin 08.11.2026] „Luna de lucru”: luna la care pornește un ecran lunar al firmei când nici apelantul, nici fereastra din
// care vii nu dau o lună. Este luna dinaintea lunii de azi cât timp nu e blocată (contabilul închide luna trecută în prima parte a lunii), altfel
// luna de azi (în ianuarie, luna dinainte = decembrie al anului trecut). O singură definiție, pentru toate ecranele lunare (DESIGN_SYSTEM.md,
// „Luna propusă la deschidere”). Lunile blocate se cer o dată pe firmă (GET /tenants/{id}/perioade-blocate) și se țin cât trăiește pagina;
// după orice blocare sau deblocare din interfață se cheamă `uitaLunaDeLucru`. O cerere căzută sau un răspuns fără „blocate” = nicio lună blocată.
import { api } from "./api.js?v=0b48920b43";

export function lunaDeLucruDin(blocate, azi = new Date()) {
  const an = azi.getFullYear(), luna = azi.getMonth() + 1;
  const trecuta = luna === 1 ? { an: an - 1, luna: 12 } : { an, luna: luna - 1 };
  const blocata = (blocate || []).some((p) => p.an === trecuta.an && p.luna === trecuta.luna);
  return blocata ? { an, luna } : trecuta;
}

const BLOCATE = {};   // tenantId -> lista [{an, luna}] a lunilor blocate

export async function lunaDeLucru(tenantId) {
  if (!BLOCATE[tenantId]) {
    let r = null;
    try { r = await api.get(`/tenants/${tenantId}/perioade-blocate`); } catch { r = null; }
    BLOCATE[tenantId] = r && Array.isArray(r.blocate) ? r.blocate : [];
  }
  return lunaDeLucruDin(BLOCATE[tenantId], new Date());
}

export function uitaLunaDeLucru(tenantId) {
  delete BLOCATE[tenantId];
}
