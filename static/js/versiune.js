// versiune.js — ANUNTA ca s-a publicat o versiune noua. NU intrerupe, NU reincarca. (R129)
//
// DECIZIA lui Costin (03.09.2026), varianta (a), verbatim: *„aplicatia compara periodic amprenta de
// versiune si anunta, fara sa intrerupa. Nu forta reincarcarea — un formular pe jumatate completat
// pierdut e mai rau decat defectul."*
//
// **DEFECTUL, masurat** (02.09.2026): fila lui Costin rula `validat.js?v=e771e38cc0` — modulele
// commitului `9b3bf419` —, iar intre ultima lui navigare si apasare intrasera **sapte** publicari.
// Pasul de confirmare construit in aceeasi zi „nu s-a deschis" fiindca in codul pe care il executa
// browserul lui el nu exista. *Nu era un defect al codului nou; era codul nou care nu ajunsese la el.*
// La pilot, un contabil tine fila deschisa toata ziua — deci ar raporta defecte deja reparate, iar
// noi am cauta cauze in cod curat.
//
// **AMPRENTA E CEA CARE EXISTA DEJA.** `/static/.publicat.json` e scris de `scripts/publica_static.py`
// (R118) si spune din ce s-a publicat, de pe ce commit si cand. Nu se construieste a doua sursa
// pentru aceeasi intrebare: *„nu construi al doilea mecanism"*.
//
// **CE NU FACE, si e chiar decizia:** nu reincarca, nu inchide nimic, nu muta focusul, nu re-randeaza
// coaja. Anuntul se ASEAZA in bara de sus ca un chirias (DS cap.25) — un nod pus intr-un loc declarat
// de proprietar. Re-randarea intregii coji ar fi pierdut exact formularul pe care decizia il apara.
//
// **O VERIFICARE ESUATA NU INSEAMNA VERSIUNE NOUA.** Reteaua pica, serverul reporneste. Un anunt pe
// eroare ar invata omul sa-l ignore, iar atunci n-ar mai anunta nimic.
import * as coaja from "./coaja.js?v=2776271008";

//: Cat de des se intreaba. Nu e o valoare fiscala, e o CADENTA: destul de rar ca sa nu conteze
//: (o cerere la cinci minute, catre un fisier de 120 de octeti), destul de des ca o publicare sa
//: fie vazuta in aceeasi sesiune de lucru. Se intreaba SI la revenirea in fila — momentul in care
//: omul se uita oricum la ecran.
export const INTERVAL_MS = 5 * 60 * 1000;

const CALE = "/static/.publicat.json";
const ID_ANUNT = "versiune-noua";

let incarcata = null;    // amprenta cu care a pornit codul care ruleaza ACUM
let gasita = null;       // amprenta noua, o data ce s-a vazut
let pornit = false;
let semnalatEsec = false;

/** Amprenta publicarii, ca sir. `commit` pe publicarile din HEAD, `la` pe cele din arbore. */
async function citeste() {
  const r = await fetch(CALE, { cache: "no-store" });
  if (!r.ok) throw new Error("HTTP " + r.status);
  const a = await r.json();
  return a.commit || a.la || null;
}

function nodAnunt() {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "versiune-noua";
  b.title = "S-a publicat o versiune nouă a aplicației. Reîncarcă atunci când îți convine — "
    + "ce ai pe ecran nu se pierde până atunci.";
  b.setAttribute("aria-label", b.title);
  b.innerHTML = '<span class="versiune-noua-punct" aria-hidden="true"></span>'
    + '<span class="versiune-noua-text">Versiune nouă · reîncarcă</span>';
  b.addEventListener("click", () => window.location.reload());
  return b;
}

/** Aseaza anuntul, DACA s-a gasit o versiune noua. Se cheama si la fiecare re-randare a cojii.
 *
 * **LIMITA, declarata:** bara de stare nu exista la rolul `client`, deci acolo anuntul NU se vede.
 * Prima forma il pusese in bara albastra de sus, tocmai ca sa acopere toate rolurile — dar acolo,
 * masurat pe Pixel 5, bara e la limita chiar fara el si trecea in revarsare orizontala. *Argumentul
 * era bun; masuratoarea l-a batut.* `pune` intoarce `false` cand locul lipseste, si asta e raspunsul
 * corect: un chirias nu-si ia spatiu care nu e al lui.
 */
export function aseaza() {
  if (!gasita) return false;
  return coaja.pune(coaja.LOCURI.BARA_DE_STARE, ID_ANUNT, nodAnunt());
}

async function verifica() {
  let acum;
  try {
    acum = await citeste();
  } catch (e) {
    // O verificare esuata nu e o versiune noua. Se spune o SINGURA data, ca sa nu umple consola.
    if (!semnalatEsec) {
      semnalatEsec = true;
      console.warn("[versiune] nu pot citi amprenta publicarii:", e && e.message);
    }
    return;
  }
  if (!acum) return;
  if (incarcata === null) { incarcata = acum; return; }   // prima citire = ce ruleaza acum
  if (acum !== incarcata && acum !== gasita) {
    gasita = acum;
    aseaza();
  }
}

/** Porneste urmarirea. Idempotent: a doua chemare nu deschide un al doilea ceas. */
export function porneste() {
  if (pornit) return;
  pornit = true;
  verifica();
  setInterval(verifica, INTERVAL_MS);
  // La revenirea in fila: momentul in care omul se uita oricum la ecran, deci cel mai ieftin
  // moment in care poate afla. Nu inlocuieste ceasul — o fila lasata vizibila nu revine niciodata.
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") verifica();
  });
}

/** Pentru probe si pentru diagnostic: ce amprenta ruleaza si ce s-a gasit. */
export function stare() {
  return { incarcata, gasita, pornit };
}
