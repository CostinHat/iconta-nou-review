// tari_partener.js — [lotul 12, C160] Țara partenerului unei facturi emise, spusă la fel pe ecranele care o cer („Emite factură”, șablonul
// facturii recurente): lista țărilor (grupul UE OGLINDEȘTE core/d390.TARI_UE, ca încadrarea să coincidă cu backendul; codurile sunt cele
// de TVA / VIES — Grecia = EL) și deducerea țării din codul fiscal (DS cap.17: dedusă, vizibilă și modificabilă). O singură sursă.
import { esc } from "../api.js?v=309f4d66ae";

export const TARI_UE_JS = { AT:"Austria", BE:"Belgia", BG:"Bulgaria", CY:"Cipru", CZ:"Cehia",
  DE:"Germania", DK:"Danemarca", EE:"Estonia", EL:"Grecia", ES:"Spania", FI:"Finlanda",
  FR:"Franța", HR:"Croația", HU:"Ungaria", IE:"Irlanda", IT:"Italia", LT:"Lituania",
  LU:"Luxemburg", LV:"Letonia", MT:"Malta", NL:"Țările de Jos", PL:"Polonia", PT:"Portugalia",
  SE:"Suedia", SI:"Slovenia", SK:"Slovacia", GB:"Regatul Unit", XI:"Irlanda de Nord" };
export const TARI_NONUE_JS = { US:"Statele Unite", CH:"Elveția", TR:"Turcia", CN:"China",
  MD:"Republica Moldova", NO:"Norvegia", RS:"Serbia", UA:"Ucraina" };

/** Opțiunile listei de țări: România întâi (selectată), apoi Uniunea Europeană și țările din afara ei. */
export function optiuniTara() {
  return `<option value="RO" selected>România (RO)</option>`
    + `<optgroup label="Uniunea Europeană">`
    + Object.keys(TARI_UE_JS).sort().map((c) => `<option value="${c}">${esc(TARI_UE_JS[c])} (${c})</option>`).join("")
    + `</optgroup><optgroup label="În afara UE (export)">`
    + Object.keys(TARI_NONUE_JS).sort().map((c) => `<option value="${c}">${esc(TARI_NONUE_JS[c])} (${c})</option>`).join("")
    + `</optgroup>`;
}

/** Țara dedusă din codul fiscal: prefixul unui stat din listă (DE…, EL…, XI…) -> acel stat; cod numeric sau „RO…” -> România; altfel
 *  null (rămâne ce era — omul o schimbă din listă). */
export function taraDinCui(cui) {
  const c = (cui || "").replace(/\s+/g, "").toUpperCase();
  if (/^(RO)?\d{2,10}$/.test(c)) return "RO";
  const pfx = c.slice(0, 2);
  return /^[A-Z]{2}/.test(c) && (TARI_UE_JS[pfx] || TARI_NONUE_JS[pfx]) ? pfx : null;
}
