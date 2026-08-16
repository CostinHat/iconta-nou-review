# PREDARE LANT — parcurgere import CUBUS (raspunsuri 3-16), regula 13 pe clasa

Marca intrare: **2509330** → iesire curenta: **e090166** (2 loturi livrate din campanie).
Comanda: repara TOT ce e defect in cele 22 de raspunsuri, pe CLASA (nu strat cu strat).

## LIVRAT + PROBAT (RED pe cod vechi, GREEN dupa)
- **Lot 1 (71995e4)** — corectitudine backend parsere de import:
  - Q3 mijloace: `verifica_randuri` citea cheia `durata` (inexistenta) in loc de `dnf_luni` → 0 pe fiecare rand. Reparat.
  - Q4 asociati: `verifica_randuri` rula `valideaza_cnp` pe CUI de juridica. Acum ramifica fizic/juridic ca `extrage` (CUI validat ca CUI). Motiv precis `cnp_invalid`/`cui_invalid`.
  - Q11 salariati: norma/ore FABRICATE tacit la coloana lipsa (regula 4). `extrage` nu mai fabrica; `SalariatRand` fara default; `verifica_randuri` semnaleaza norma lipsa.
  - Q13 mijloace: `MijlocFixRand.cont_imobilizare` default Pydantic `"2131"` scos (DS cap.17).
  - Garda: `core/test_import_backend_corect.py`.
- **Lot 2 (e090166)** — mesaje de import afisate cu diacritice + garda pe ROL (Q2/Q17):
  - Diacriticizate mesajele `raise ValueError` din 6 parsere de import (ajung la user via `HTTPException(str(e))`).
  - Garda `core/test_import_mesaje_afisate.py` acopera rolul `raise ValueError` DOAR pe fisierele de import (nu global: extensia globala flagra 159 mesaje, incl. erori interne/dev legitim ASCII).

## RAMAS DE FACUT (clasa neinchisa — NEPROBAT, neinceput)
Ordine sugerata dupa impact:

1. **Clasa preview↔salvare (Q5) — 5 straturi.** DS cap.24: validarea per-rand apartine BACKENDULUI (poarta unica); `extrage` face o a doua validare care DRIFTEAZA. Fix: endpointul de preview (`/incarca`) sa ruleze `verifica_randuri` pe randurile extrase si sa intoarca erorile field-keyed → frontendul le arata (cap.6 `eroareCamp`), preview = salvare. Straturi divergente: parteneri, salariati, asociati, mijloace_fixe, istoric. (Lot 1 a reparat bug-urile DIN `verifica_randuri`; ramane sa fie RULAT si la preview.)
2. **Q9 parteneri — coerenta pierduta.** Diferenta `coerenta()` (`solduri_parteneri_api.py:148`) se arata la preview dar nu se persista si nu blocheaza salvarea (spre deosebire de solduri). Fix: blocheaza salvarea pe incoerenta (ca solduri) SAU persista+propaga la controlul fiscal.
3. **Q6 + Q15 mijloace — amortizare.** (a) La import/preview coloana "rămas" = campul `rezidual` din fisier (`migrare.js:1166`), etichetata gresit — e rezidual, nu net book value; alinieaza eticheta. (b) Vizualizarea (`main.py:8486-8493`, `mijloace_ecran.js:45`) hardcodeaza "liniar" in text SI calculeaza mereu liniar, ignorand `metoda`. Fix: amortizare pe metoda reala (liniar/degresiv/accelerat/superaccelerat, CF art.28) + text care nu minte. LARG (calcul fiscal).
4. **UX migrare (Q7, Q8, Q12, Q14).** DS cap.5/6/8:
   - Q7 solduri: dupa salvare, `arataMesaj(..., "ok")` de confirmare (cap.6), nu revenire tacuta la formular gol.
   - Q8 `meniuMigrarePerFirma` (`migrare.js:1477`): badge de stare per strat, citind `/migrare/status` (ca `meniuMigrare` la nivel cabinet). Semafor prin tokeni (cap.8).
   - Q12 avertisment pe rand: doar `title=` (inaccesibil pe touch). Fix: `.caseta-atentie`/`arataMesaj` vizibil (cap.5), nu tooltip nativ.
   - Q14 "Descarca model (CSV)": exista doar la solduri (1/9). Adauga la celelalte parsere de fisier (parteneri, salariati, asociati, mijloace, istoric), fiecare cu model corect.
5. **Q16 salariati — COR brut.** `migrare.js:885` arata `r.cor` (codul), etichetat "Functie". Fix: endpointul de preview imbogateste cu `cor_api.denumire(conn, cor)`; frontendul arata denumirea (fallback la cod).
6. **Q18 XSD — nomenclator inghetat.** `d112.py:16` hardcodeaza `d112_06082026.xsd`. Fix: alege automat cel mai nou `d112_*.xsd` din `anaf_surse/` (glob pe data din nume), ca adaugarea fisierului sa fie de ajuns, fara editare de cod. Sistemic: toate declaratiile fixate la XSD datat.
7. **Q1 + Q10 — randare autentificata Playwright.** Reparate in cod (tura precedenta) + probate pe date/garda, DAR nerandate in browser autentificat cu navigare de la ecranul principal la Date firma (Q1) / Solduri (Q10). De randat.
8. **Audit mesaje generatoare (extinderea Q2/Q17).** ~150 `raise ValueError` in d100/d112/d205/d300/d390/... — unele afisate (via control_incrucisat cauza), unele interne. Cere judecata per-mesaj afisat-vs-intern, nu sweep mecanic. De triat si diacriticizat cele afisate; garda scopata ca la import.

## PREMISE FALSE confirmate la sursa (nu se "repara" — se noteaza)
- Q10: salariatii NU sar peste invalizi — ambele parsere blocheaza tot importul; calea "skip" e COD MORT (`salariati_import_api.py` bucla din `importa` + UI "X sariti") de dinainte de 15.07.2026. **De ELIMINAT** codul mort + textul care promite comportamentul (parte din clasa).
- Q13: cont imobilizare nu blocheaza fiecare rand (bug-ul de durata o facea, Q3, reparat).
- Q19/Q20/Q21: decizii documentate / fara comanda in context / deja ancorat — nu-s defecte de cod.
