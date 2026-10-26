// sal_alegeri.js — [lotul 13, deficiența 676, comanda Costin 13.1] listele scurte din ferestrele salarizării: butoane alăturate.
// Comanda, verbatim: „Listele scurte (până la 6 opțiuni) nu sunt liste derulante: opțiunile apar ca butoane alăturate, toate vizibile,
// cea aleasă marcată (ex. Fel decont, Sursa Casa/Banca). Listele lungi (firme, conturi, țări, salariați) rămân câmp cu căutare. Nimic nu
// se deschide singur.” Forma: butoanele din setul DS (`.buton-secundar`), cel ales cu `.buton-activ` + `aria-pressed="true"` (DS cap.1,
// „Vederea aleasă e activă, nu dezactivată”); nimic ales la deschidere când nu există o valoare salvată (cap.17: aplicația nu alege în
// locul omului). Valoarea stă într-un `<input type="hidden">` cu id-ul câmpului, deci formularul o citește ca pe un select (`daNu`,
// `.value`) și ciorna formularului o păstrează; alegerea lipsă se cere lângă grup (`cereButoane`), ca `cereAlegerile` la select.
// [655] Sumele scrise de om se citesc în format românesc (`sumaRo`): „1.000” = o mie, „1.000,50”, „12,5”, „2000.41”; ce nu se poate citi fără ghicit se refuză lângă câmp.
// Dacă subagentul Design System a pus mecanismele comune în api.js, acest modul se înlocuiește cu ele (aceeași semantică).
import { esc, eroareCamp } from "../api.js?v=e38843b1ec";

// Grupul de butoane al câmpului `id` (opțiunile: [[valoare, eticheta]]); `ales` = valoarea salvată ("" / null = nimic ales).
export function alegereButoane(id, optiuni, ales, eticheta) {
  const a = ales === null || ales === undefined ? "" : String(ales);
  const b = optiuni.map(([v, l]) => {
    const sel = a !== "" && a === String(v);
    return `<button type="button" class="buton-secundar${sel ? " buton-activ" : ""}" data-v="${esc(String(v))}" aria-pressed="${sel}"`
      + ` data-fara-actiune="alegere în formular; salvarea poartă acțiunea">${esc(l)}</button>`;
  }).join("");
  return `<span class="alegere-butoane" id="${esc(id)}-grup" role="group" aria-label="${esc(eticheta || "")}"`
    + ` style="display:inline-flex;flex-wrap:wrap;gap:6px">${b}</span><input type="hidden" id="${esc(id)}" value="${esc(a)}">`;
}

// Da / Nu: aceeași valoare ca `selectDaNu` ("true" / "false"), citită cu `daNu`.
export function alegereDaNu(id, ales, eticheta) {
  const v = ales === true || ales === 1 || ales === "true" ? "true" : (ales === false || ales === 0 || ales === "false" ? "false" : "");
  return alegereButoane(id, [["true", "Da"], ["false", "Nu"]], v, eticheta);
}

// Marchează butonul ales al fiecărui grup din `root` după valoarea câmpului (după o ciornă refăcută sau o valoare citită din fișă).
export function sincronizeazaAlegeri(root) {
  root.querySelectorAll(".alegere-butoane").forEach((g) => {
    const inp = root.querySelector("#" + CSS.escape(g.id.replace(/-grup$/, "")));
    const v = inp ? inp.value : "";
    g.querySelectorAll("button[data-v]").forEach((x) => {
      const sel = v !== "" && x.dataset.v === v;
      x.classList.toggle("buton-activ", sel);
      x.setAttribute("aria-pressed", String(sel));
    });
  });
}

// Pune valoarea `v` în câmpul `id` și anunță schimbarea (ascultătorii formularului, ciorna).
export function puneAlegerea(root, id, v) {
  const inp = root.querySelector("#" + CSS.escape(id));
  if (!inp) return;
  inp.value = v == null ? "" : String(v);
  sincronizeazaAlegeri(root);
  inp.dispatchEvent(new Event("change", { bubbles: true }));
}

// Clicul pe un buton al unui grup alege valoarea lui (o singură dată pe rădăcină).
export function legaAlegeri(root) {
  if (root.__alegeriLegate) return;
  root.__alegeriLegate = true;
  root.addEventListener("click", (ev) => {
    const b = ev.target instanceof Element ? ev.target.closest(".alegere-butoane button[data-v]") : null;
    if (!b || b.disabled) return;
    const g = b.closest(".alegere-butoane");
    const id = g.id.replace(/-grup$/, "");
    puneAlegerea(root, id, b.dataset.v);
    const err = root.querySelector('.msg-eroare[data-camp="' + CSS.escape(g.id) + '"]');
    if (err) err.remove();
    g.classList.remove("camp-invalid");
    g.removeAttribute("aria-invalid");
  });
}

// Fiecare grup vizibil din `ids` rămas fără alegere primește refuzul lângă el; întoarce true dacă lipsește o alegere.
export function cereButoane(root, ids) {
  let lipsa = false;
  for (const id of ids) {
    const inp = root.querySelector("#" + CSS.escape(id));
    const g = root.querySelector("#" + CSS.escape(id) + "-grup");
    if (!inp || !g || g.offsetParent === null) continue;   // ascuns: nu se cere
    if (inp.value === "") {
      eroareCamp(root, id + "-grup", "Alege o valoare — aplicația nu alege în locul tău.");
      lipsa = true;
    }
  }
  return lipsa;
}

// [655] Suma scrisă de om, în format românesc: punctul desparte miile („1.000” = o mie, „1.000,50”), virgula zecimalele („12,5”); un punct
// urmat de una sau două cifre e zecimal („2000.41”). null = câmp gol; NaN = nu se poate citi fără ghicit (ex. „1.00.0”, „1,000.5”).
export function sumaRo(text) {
  const t = String(text == null ? "" : text).replace(/[\s ]/g, "");
  if (!t) return null;
  if (/^-?\d{1,3}(\.\d{3})+(,\d+)?$/.test(t) || /^-?\d+(,\d+)?$/.test(t)) return Number(t.replace(/\./g, "").replace(",", "."));
  // un punct urmat de una sau două cifre nu poate despărți miile: e zecimal („2000.41”)
  if (/^-?\d+\.\d{1,2}$/.test(t)) return Number(t);
  return NaN;
}

// Valoarea unei sume pentru câmpul de text: cu virgulă la zecimale („12,5”), fără separator de mii (se citește înapoi cu `sumaRo`).
export function sumaInCamp(v) {
  if (v === null || v === undefined || v === "") return "";
  const n = Number(v);
  return Number.isFinite(n) ? String(n).replace(".", ",") : "";
}

export const MESAJ_SUMA = "Scrie suma în lei, cu virgulă la zecimale (ex. 1.000 sau 1.000,50).";
