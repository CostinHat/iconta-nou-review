// ecran_destinatie.js — [lotul 07.10 pct.2, comanda Costin 06.10.2026] „Orice mesaj care trimite în alt ecran are buton direct
// spre el și readuce la formular.”
//
// Un refuz al serverului care trimite omul în alt ecran poartă `ecran` (o cheie din ECRANE) în detaliul lui — metoda de stoc,
// capitalul social, orice refuz nou de același fel. Ecranul care arată refuzul NU scrie el butonul: îl cere de aici, deci un
// ecran nou de destinație se adaugă o dată, în ECRANE, și apare peste tot unde un refuz îl numește.
//
// „Readuce la formular”: ecranul se deschide PESTE cel curent (`nav.deschide`), deci „←” întoarce la formularul păstrat de
// navigator; iar după salvare, ecranul de destinație oferă singur „Înapoi la <formular>” (`inapoiLa`).
// Gard: `core/test_refuz_spre_ecran.py` (fiecare `ecran` emis de server are intrare aici, și fiecare ecran care afișează un
// astfel de refuz trece prin `butonSpreEcran`).
import { randeazaDateFirma } from "./date_firma.js?v=ef417ce42e";

export const ECRANE = {
  date_firma: {
    titlu: "Date firmă",
    deschide: (nav, tenantId, inapoiLa, camp) => nav.deschide("Date firmă", (c2) => randeazaDateFirma(c2, nav, tenantId, { inapoiLa, camp })),
  },
};

export function butonSpreEcran(zona, ecran, nav, tenantId, opt = {}) {
  const e = ECRANE[ecran];
  if (!zona || !e || !nav) return null;
  const b = document.createElement("button");
  b.type = "button";
  b.className = opt.clasa || "buton-primar";
  if (opt.id) b.id = opt.id;
  b.dataset.ecranDestinatie = ecran;   // îl recunoaște `api.js` (_butonSpreEcran): un singur buton lângă un refuz
  b.dataset.faraActiune = `navigare la ${e.titlu}; salvarea de acolo poartă acțiunea`;
  b.textContent = `Deschide ${e.titlu}`;
  // [retest 08.10, completarea pct.2] „trebuie să ducă direct la secțiunea «Chitanțe», cu câmpul seriei în focus”: refuzul numește
  // câmpul (`detail.camp_ecran`, tabela `core/mesaje.CAMP_ECRAN_PE_COD`), iar ecranul-țintă îl aduce în vedere și îi dă focus
  b.addEventListener("click", () => e.deschide(nav, tenantId, opt.inapoiLa || null, opt.camp || null));
  zona.appendChild(b);
  return b;
}
