// centre_cost_linie.js — [lotul 13, deficiența 536] centrul de cost pe linia unui document contat automat (factura emisă, factura primită
// de mână sau din SPV). Comanda Costin 13.1, verbatim: „Centrul se pune doar pe notele manuale; tot ce se contează automat (facturi, NIR,
// salarii, amortizare) iese «nealocat» […] Centrul se poate pune pe liniile facturilor, NIR-urilor, salariilor și pe mijloacele fixe”.
// O singură listă și o singură formă, pe toate ecranele: centrele ACTIVE ale firmei (cele dezactivate nu se mai oferă, ca în Registrul
// jurnal); fără niciun centru definit, câmpul nu apare. Gol = fără centru (nimic precompletat). Contarea duce centrul pe rândul de venit /
// cheltuială al notei (`contare_facturi._note_pe_cote`).
import { api, esc } from "../api.js?v=4364ee71f3";

/** Centrele active ale firmei ([{id, nume}]); [] dacă firma n-are centre sau lista nu se poate citi (câmpul nu apare). */
export async function centreActive(tenantId) {
  try { return ((await api.get(`/tenants/${tenantId}/centre-cost?doar_active=true`)) || {}).centre || []; } catch { return []; }
}

/** Lista centrului unei linii: `id` al câmpului (refuzul serverului vine lângă el), `clasa`, centrele, centrul ales, eticheta pentru
 *  cititorul de ecran, stilul și atributele în plus ale listei (ex. `data-c` al formularului). Gol dacă firma n-are centre. */
export function htmlCentru(id, clasa, centre, ales, eticheta, stil = "", atribute = "") {
  if (!centre || !centre.length) return "";
  return `<select class="camp-input ${clasa}" id="${id}" aria-label="${esc(eticheta)}" title="Centrul de cost al liniei"${stil ? ` style="${stil}"` : ""}${atribute ? " " + atribute : ""}>
    <option value="">— fără centru de cost —</option>${centre.map((c) => `<option value="${c.id}"${String(ales || "") === String(c.id) ? " selected" : ""}>${esc(c.nume)}</option>`).join("")}</select>`;
}

/** Valoarea de trimis: id-ul centrului (număr) sau null. */
export const valoareCentru = (v) => (v === "" || v == null ? null : Number(v));
