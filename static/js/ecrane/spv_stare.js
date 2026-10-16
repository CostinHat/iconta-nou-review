// spv_stare.js — [lotul 6: 273a, 275c, 289b] Starea SPV a FIRMEI, spusă la fel peste tot (fereastra firmei, facturile primite, factura
// emisă): conexiunea cabinetului, ultima citire a CUI-ului firmei și răspunsul ANAF (`GET /tenants/{id}/spv/stare`,
// `spv_conector.stare_firma`). Când lipsește ceva ce se repară în Setări cont → Conectare SPV, mesajul are butonul spre acolo
// (`ecran_destinatie.butonSpreEcran`). O singură sursă a textului — nu câte o frază pe ecran.
import { api, arataMesaj, cate, dataRo } from "../api.js?v=9409795a49";
import { butonSpreEcran } from "./ecran_destinatie.js?v=627c3c3c38";

const _ora = (iso) => { const d = new Date(iso); return `${dataRo(iso)}, ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`; };

/** {text, tip, spreConectare}: ce se spune despre SPV pentru firmă. */
export function textStareSpv(st) {
  if (!st || !st.conectat) {
    return { tip: "avert", spreConectare: true,
      text: "SPV: cabinetul nu e conectat. Facturile nu pleacă în SPV, iar cele de la furnizori nu vin automat." };
  }
  if (st.are_drept === false) {
    return { tip: "avert", spreConectare: true,
      text: `SPV: cabinetul e conectat, dar ANAF răspunde pentru CUI ${st.cui}: „${st.eroare || "fără drept"}”. Certificatul n-are împuternicire `
        + "pentru firmă în SPV: împuternicirea se face la ANAF, apoi conexiunea o acoperă." };
  }
  if (!st.verificat_la) {
    return { tip: "info", spreConectare: false,
      text: "SPV: conectat. Firma n-a fost încă verificată în SPV — citirea automată rulează de două ori pe oră (la :17 și :47)." };
  }
  if (st.eroare) {
    return { tip: "avert", spreConectare: false, text: `SPV: conectat; ultima verificare (${_ora(st.verificat_la)}) a primit de la ANAF: „${st.eroare}”.` };
  }
  return { tip: "ok", spreConectare: false,
    text: `SPV: conectat · verificat ultima dată ${_ora(st.verificat_la)}${st.mesaje != null ? ` · ${cate(st.mesaje, "factură primită", "facturi primite")} la ultima citire` : ""}.` };
}

/** Citește starea și o scrie în `zona` (mesajul + butonul spre Conectare SPV, când e cazul); întoarce starea (sau null). */
export async function randeazaStareSpv(zona, nav, tenantId) {
  let st = null;
  try { st = await api.get(`/tenants/${tenantId}/spv/stare`); } catch (e) {
    zona.innerHTML = '<div class="spv-stare-text"></div>';
    arataMesaj(zona.querySelector(".spv-stare-text"), `Starea SPV a firmei nu s-a putut citi (${e.mesaj || "eroare"}).`, "avert");
    return null;
  }
  const t = textStareSpv(st);
  zona.innerHTML = '<div class="spv-stare-text"></div>';
  arataMesaj(zona.querySelector(".spv-stare-text"), t.text, t.tip);
  if (t.spreConectare) butonSpreEcran(zona, "conectare_spv", nav, tenantId, { clasa: "buton-secundar" });
  return st;
}
