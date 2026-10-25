// date_anaf.js — [lotul 12, deficiența 459.1, comanda Costin 12.2 pct.5] „la schimbarea CUI-ului denumirea adusă de la CUI-ul anterior
// (DANTE INTERNATIONAL SA) rămâne completată.” Datele pe care ANAF le aduce pentru un CUI (denumirea; la factură și adresa, localitatea,
// județul) țin de CUI-ul acela: când omul schimbă CUI-ul, ele dispar, ca formularul să nu poarte numele altei firme lângă CUI-ul nou.
// Ce a scris omul în câmp rămâne (regula F188: ANAF propune, nu suprascrie ce a corectat omul) — se șterge numai valoarea pe care a pus-o
// ANAF și pe care omul n-a atins-o. Linia de stare de sub CUI (numele găsit, „plătitor TVA”) ține și ea de CUI-ul vechi și se golește.
// O singură implementare pentru toate formularele în care ANAF completează câmpuri din CUI (Adaugă firmă, NIR, casa; emiterea facturii
// și factura primită o pot chema la fel). DS cap.6 („Nimic precompletat sau afișat care poate induce în eroare contabilul”, CLAUDE.md §9).

/** Leagă câmpul CUI de câmpurile pe care le completează ANAF. `campuri` = elementele (input / select) completate din răspuns, `stare` =
 *  linia de sub CUI (opțional). Întoarce `pune(valori, { suprascrie })`: `valori[i]` intră în `campuri[i]` (undefined / null = câmpul nu
 *  se atinge); fără `suprascrie`, numai într-un câmp gol sau încă cu valoarea pusă de ANAF (completarea automată, fără apăsare); cu
 *  `suprascrie` (omul a cerut-o explicit, „Verifică la ANAF”), oricum. */
export function legaDateAnaf(campCui, campuri, stare = null) {
  const puse = campuri.map(() => null);   // valoarea pusă de ANAF în fiecare câmp, cât timp omul n-a schimbat-o
  campCui.addEventListener("input", () => {
    campuri.forEach((c, i) => {
      if (c && puse[i] != null && c.value === puse[i]) c.value = "";
      puse[i] = null;
    });
    if (stare) { stare.textContent = ""; }
  });
  return {
    pune(valori, { suprascrie = false } = {}) {
      campuri.forEach((c, i) => {
        const v = valori[i];
        if (!c || v == null || v === "") return;
        if (!suprascrie && c.value.trim() && c.value !== puse[i]) return;   // F188: ce a scris omul rămâne
        if (c.tagName === "SELECT" && ![...c.options].some((o) => o.value === v)) return;
        c.value = v;
        puse[i] = c.value;
      });
    },
  };
}
