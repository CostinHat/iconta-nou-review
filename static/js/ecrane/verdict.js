// verdict.js — PUNCTUL UNIC de verdict din stare (P13c, interdictiile 27+31).
//
// Verdictul POZITIV se rosteste DOAR aici, ca text NUMIT in VERDICT_POZITIV. In afara acestui fisier
// valorile de mai jos sunt INTERZISE ca literal (gard mecanic: core/test_verdict_punct_unic.py).
//
// Regula clasei (structurala, nu forma-cu-forma): un verdict POZITIV apare DOAR dintr-o stare VERDE
// EXPLICITA primita de la backend. Gri, ABSENT (null/undefined) sau NECUNOSCUT dau gri -> "nu se poate
// verifica". Rosu si galben raman la apelant (au numaratori proprii). Un verde nu apare NICIODATA din
// absenta unei stari sau dintr-o stare necunoscuta — instanta care a nascut fisierul: portal.js initializa
// "pa-verde"/"Totul e la zi" din oficiu si-l suprascria doar pe rosu/galben/gri, iar `stare` putea fi None.
export const VERDICT_POZITIV = {
  portal: "Totul e la zi",
  firme_toate: "Toate firmele la zi",
  control_firma: "totul la zi",
  control_depus: "Totul depus la zi",
};

export const VERDICT_GRI = "nu se poate verifica";

export function verdictDinStare(stare, varianta) {
  // Numai cazurile care NU sunt rosu/galben (acelea raman la apelant, cu numaratorile lor).
  if (stare === "verde") return { pozitiv: true, gri: false, titlu: VERDICT_POZITIV[varianta] };
  return { pozitiv: false, gri: true, titlu: VERDICT_GRI };
}
