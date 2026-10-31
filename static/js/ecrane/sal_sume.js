// sal_sume.js — [lotul 13, 655] suma scrisă de om în ferestrele salarizării, citită cu regula unică a aplicației (`numarRo` din api.js,
// DS cap.6 „Numerele scrise de om”, oglinda `core/numere.numar_ro`). Primește câmpul (se citește TEXTUL scris de om, `textCamp`: un text
// care nu e număr nu devine gol tacit) sau un text. Întoarce: null = gol; NaN = nu se poate citi fără ghicit (refuzat lângă câmp, cu
// `MESAJ_NUMAR_RO`); altfel numărul. Listele scurte ale salarizării folosesc mecanismul comun (`select[data-butoane]`, `alegereButoane`).
import { numarRo, textCamp } from "../api.js?v=ec2094fd4f";

export function sumaRo(sursa) {
  const r = numarRo(sursa && typeof sursa === "object" ? textCamp(sursa) : sursa);
  return r.gol ? null : (r.eroare ? NaN : r.valoare);
}
