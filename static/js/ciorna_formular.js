// [deficiența 267, comanda Costin 15.10.2026 noaptea, verbatim în DECIZII „Lotul 5 — comanda 3”: „formularul «Înregistrează cabinetul
// tău» pierde tot ce s-a completat dacă e închis sau dacă utilizatorul iese din pagină. Se păstrează și se reface la redeschidere, mai
// puțin parolele; se șterge după crearea contului. Verifici clasa la formularele lungi.”]
// Ciorna unui formular de creare, în browserul omului (localStorage): câmpurile numite, la fiecare tastă; refăcute la redeschidere
// (și după ieșirea din pagină); șterse când înregistrarea s-a creat. Parolele nu se numesc, deci nu se păstrează niciodată. O ciornă
// mai veche de PASTRARE_ZILE se aruncă. Folosită de: înregistrarea cabinetului (login.js), salariatul nou (firme.js), concediul medical
// (flux_concediu.js). Gard: core/test_ciorna_formular.py + e2e test_def_267_*.
const PASTRARE_ZILE = 7;

function _citeste(cheie) {
  try {
    const c = JSON.parse(localStorage.getItem(cheie) || "null");
    if (!c || !c.campuri || Date.now() - (c.salvat_la || 0) > PASTRARE_ZILE * 86400000) return null;
    return c;
  } catch { return null; }
}

/**
 * @param {Element} radacina   formularul (ascultă `input` / `change` pe el)
 * @param {string} cheie       cheia din localStorage (una pe formular și, unde e cazul, pe firmă / utilizator)
 * @param {string[]} campuri   id-urile câmpurilor păstrate — FĂRĂ parole
 * @returns {{refacuta: boolean, sterge: Function}}
 */
export function ciornaFormular(radacina, cheie, campuri) {
  const c = _citeste(cheie);
  let refacuta = false;
  if (c) {
    for (const id of campuri) {
      const el = radacina.querySelector("#" + id);
      if (!el || el.readOnly || el.disabled || !(id in c.campuri)) continue;
      if (el.type === "checkbox") el.checked = !!c.campuri[id];
      else el.value = c.campuri[id];
      refacuta = refacuta || !!c.campuri[id];
    }
  }
  const salveaza = () => {
    const v = {};
    let are = false;
    for (const id of campuri) {
      const el = radacina.querySelector("#" + id);
      if (!el || el.readOnly) continue;
      v[id] = el.type === "checkbox" ? el.checked : el.value;
      are = are || (el.type !== "checkbox" && String(el.value).trim() !== "");
    }
    try {
      if (are) localStorage.setItem(cheie, JSON.stringify({ v: 1, salvat_la: Date.now(), campuri: v }));
      else localStorage.removeItem(cheie);
    } catch { /* stocare plină sau blocată: formularul merge mai departe, numai ciorna lipsește */ }
  };
  radacina.addEventListener("input", salveaza);
  radacina.addEventListener("change", salveaza);
  return { refacuta, sterge: () => { try { localStorage.removeItem(cheie); } catch { /* idem */ } } };
}
