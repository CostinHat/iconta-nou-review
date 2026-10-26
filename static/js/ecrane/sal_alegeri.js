// sal_alegeri.js — [lotul 13, deficiența 676, comanda Costin 13.1] listele scurte din ferestrele salarizării: butoane alăturate.
// Comanda, verbatim: „Listele scurte (până la 6 opțiuni) nu sunt liste derulante: opțiunile apar ca butoane alăturate, toate vizibile,
// cea aleasă marcată (ex. Fel decont, Sursa Casa/Banca). Listele lungi (firme, conturi, țări, salariați) rămân câmp cu căutare. Nimic nu
// se deschide singur.” Forma: butoanele din setul DS (`.buton-secundar`), cel ales cu `.buton-activ` + `aria-pressed="true"` (DS cap.1,
// „Vederea aleasă e activă, nu dezactivată”); nimic ales la deschidere când nu există o valoare salvată (cap.17: aplicația nu alege în
// locul omului). Valoarea stă într-un `<input type="hidden">` cu id-ul câmpului, deci formularul o citește ca pe un select (`daNu`,
// `.value`) și ciorna formularului o păstrează; alegerea lipsă se cere lângă grup (`cereButoane`), ca `cereAlegerile` la select.
// [655] Sumele scrise de om se citesc cu regula unică a aplicației (`numarRo` din api.js, DS cap.6 „Numerele scrise de om”); `sumaRo`
// doar o adaptează la forma ferestrelor salarizării (null = gol, NaN = refuzat lângă câmp).
// Dacă subagentul Design System a pus mecanismele comune în api.js, acest modul se înlocuiește cu ele (aceeași semantică).
import { esc, eroareCamp, numarRo, MESAJ_NUMAR_RO } from "../api.js?v=e38843b1ec";

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

// [655] Suma scrisă de om, citită cu `numarRo` (api.js — regula unică, oglinda `core/numere.numar_ro`): null = câmp gol; NaN = nu se
// poate citi fără ghicit (refuzată lângă câmp cu `MESAJ_SUMA`); altfel numărul.
export function sumaRo(text) {
  const r = numarRo(text);
  return r.gol ? null : (r.eroare ? NaN : r.valoare);
}

// Valoarea unei sume pentru câmpul de text: cu virgulă la zecimale („12,5”), fără separator de mii (se citește înapoi cu `sumaRo`).
export function sumaInCamp(v) {
  if (v === null || v === undefined || v === "") return "";
  const n = Number(v);
  return Number.isFinite(n) ? String(n).replace(".", ",") : "";
}

export const MESAJ_SUMA = MESAJ_NUMAR_RO;
