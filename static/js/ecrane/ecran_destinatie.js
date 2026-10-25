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
import { randeazaDateFirma } from "./date_firma.js?v=dba880c8b2";
import { panouConectareSPV } from "./setari.js?v=ba6bc8a464";
import { randeazaProduse } from "./produse_ecran.js?v=66a07e1f74";
import { ecranClienti, ecranFurnizori } from "./clienti_ecran.js?v=038e03a287";   // [lotul 11, decizia 10.3] fișa partenerului
import { panouIntocmitor } from "./intocmitor_bilant.js?v=5d705395fe";            // [lotul 11, decizia 10.3] întocmitorul bilanțului
import { sesiune } from "../sesiune.js?v=898215e0ee";

export const ECRANE = {
  date_firma: {
    titlu: "Date firmă",
    deschide: (nav, tenantId, inapoiLa, camp) => nav.deschide("Date firmă", (c2) => randeazaDateFirma(c2, nav, tenantId, { inapoiLa, camp })),
  },
  // [deficiența 289b] starea SPV a firmei și refuzul „Trimite în SPV” trimit aici (Setări cont → Conectare SPV)
  // [deficiența 274a] articolul fără cotă TVA în nomenclator trimite aici (emiterea facturii)
  produse: {
    titlu: "Produse",
    // [445] `inapoiLa` trece și aici (produse_ecran.js îl primește în `opt`; drumul înapoi îl spune oricum săgeata ferestrei)
    deschide: (nav, tenantId, inapoiLa, camp) => nav.deschide("Produse", (c2) => randeazaProduse(c2, nav, tenantId, { inapoiLa, camp })),
  },
  // [lotul 11, decizia Costin 10.3] „refuzul declarației trimite direct acolo”: fișa partenerului (camp = „partener:<cheie>:<camp>”)
  clienti: {
    titlu: "Clienți",
    deschide: (nav, tenantId, inapoiLa, camp) => nav.deschide("Clienți", (c2) => ecranClienti(c2, nav, { id: tenantId }, { inapoiLa, camp }), { lat: "tabel" }),
  },
  furnizori: {
    titlu: "Furnizori",
    deschide: (nav, tenantId, inapoiLa, camp) => nav.deschide("Furnizori", (c2) => ecranFurnizori(c2, nav, { id: tenantId }, { inapoiLa, camp }), { lat: "tabel" }),
  },
  // [lotul 11, decizia 10.3] întocmitorul bilanțului e în profilul cabinetului (îl scrie administratorul)
  date_cabinet: {
    titlu: "Date cabinet",
    numaiAdmin: true,
    faraDrept: "Întocmitorul bilanțului îl completează administratorul cabinetului (Setări cont → Date cabinet).",
    deschide: (nav, _tenantId, inapoiLa, camp) => nav.deschide("Date cabinet", (c2) => panouIntocmitor(c2, { inapoiLa, camp, nav })),
  },
  conectare_spv: {
    titlu: "Conectare SPV",
    // [deficiența 334, 18.10.2026] conectarea e a administratorului cabinetului (Setări cont o arată numai lui, `setari.js` eAdmin): altui
    // rol butonul nu se oferă — i se spune cine o face
    numaiAdmin: true,
    faraDrept: "Conectarea SPV o face administratorul cabinetului (Setări cont → Conectare SPV).",
    deschide: (nav) => nav.deschide("Setări cont → Conectare SPV", (c2) => panouConectareSPV(c2)),
  },
};

export function butonSpreEcran(zona, ecran, nav, tenantId, opt = {}) {
  const e = ECRANE[ecran];
  if (!zona || !e || !nav) return null;
  const rol = (sesiune.user() || {}).rol;
  if (e.numaiAdmin && rol !== "admin_firma" && rol !== "superadmin") {   // [334]
    const n = document.createElement("span");
    n.className = "ecran-nota drept-motiv";
    n.dataset.ecranDestinatie = ecran;   // un singur element lângă refuz (`api.js` _butonSpreEcran)
    n.textContent = e.faraDrept;
    zona.appendChild(n);
    return null;
  }
  const b = document.createElement("button");
  b.type = "button";
  b.className = opt.clasa || "buton-primar";
  if (opt.id) b.id = opt.id;
  b.dataset.ecranDestinatie = ecran;   // îl recunoaște `api.js` (_butonSpreEcran): un singur buton lângă un refuz
  b.dataset.faraActiune = `navigare la ${e.titlu}; salvarea de acolo poartă acțiunea`;
  b.textContent = `Deschide ${e.titlu}`;
  // [retest 08.10, completarea pct.2] „trebuie să ducă direct la secțiunea «Chitanțe», cu câmpul seriei în focus”: refuzul numește
  // câmpul (`detail.camp_ecran`, tabela `core/mesaje.CAMP_ECRAN_PE_COD`), iar ecranul-țintă îl aduce în vedere și îi dă focus
  // [lotul 11, deficiența 445: „orice buton «Deschide X» dintr-un refuz întoarce în formularul de plecare, cu datele intacte.”] navigatorul
  // află că deschiderea vine dintr-un refuz (`nav.dinRefuz`): formularul de dedesubt se păstrează oricum, săgeata destinației spune
  // „Înapoi la <formular>”, iar X întoarce acolo; `inapoiLa` implicit = titlul ferestrei de plecare (și pentru butonul pus automat de api.js)
  b.addEventListener("click", () => {
    const inapoiLa = opt.inapoiLa || (typeof nav.titluCurent === "function" && nav.titluCurent()) || null;
    if (typeof nav.dinRefuz === "function") nav.dinRefuz();
    e.deschide(nav, tenantId, inapoiLa, opt.camp || null);
  });
  zona.appendChild(b);
  return b;
}
