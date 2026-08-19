# ROADMAP INSTRUMENTE & METODĂ — verificare care nu se poate sări

Cele 11 propuneri (19.08.2026, agreat cu Costin) pentru a face metoda o POARTĂ, nu un document. Statut per fiecare;
cele **CONSTRUIT** numesc fișierul-gardă (existența lor e păzită de `core/test_instrumente_roadmap.py`). Motto:
*o regulă scrisă și citită nu e o regulă păzită — doar poarta ține* (vezi [[regula-scrisa-nu-e-regula-pazita]]).

## Construite (gard mecanic în pre-commit)

- **#1 Detector drop/overwrite tăcut — overwrite** — CONSTRUIT: `core/test_upsert_motivat.py`. Orice `INSERT ... ON CONFLICT DO UPDATE` din producție cere `# upsert-ok: <motiv>` (suprascriere conștientă). Grounded: bug plan_conturi. Prinsă latura suprascrierii; **RĂMAS latura DROP** (input curățat-la-gol-eliminat, ca `separa_cui`) — greu static fără fals-pozitive; abordare propusă: convenție „funcțiile de curățare intrări întorc `(păstrate, ignorate)`", plus `test_masti` (except-gol) + `DEFAULT_FISCAL_TACIT` (coerciție) acoperă restul clasei.
- **F6+F9 vizual/comportamental gardat pe diff** — CONSTRUIT: `frontend_test/vizual/interactiune_scan.py` + `core/test_acoperire_vizuala.py` (fundația lui #2). Apasă butoanele + completează casetele + axe desktop/mobil; poarta pică la schimbare UI fără re-scan curat.

## Propuse (neconstruite încă — backlog urmărit)

- **#2 Fuzzer de formulare** — PARȚIAL (interactiune_scan apasă/completează). RĂMAS: generarea invalidelor per câmp (gol/peste-lungime/tip/duplicat/limită) + verdict 14.4 automat. Playwright, deja instalat.
- **#3 Gard de completitudine a hărții** — PROPUS: pică dacă există un ecran în cod (`#fa-*`, `nav.deschide/mergi`) neînregistrat în `nav_ecrane.ECRANE`. Python pur.
- **#4 Matrice de stări de date** — PROPUS: fiecare ecran peste stări (gol/populat/limită, micro/profit/PFA). Playwright + seed.
- **#5 Reconciliator de cifre (Regula 14.2)** — PROPUS: total = suma rândurilor; previzualizare = buton = rezultat, asertat. Playwright.
- **#6 Golden field-by-field XML↔XSD/_struct pe date POPULATE** — PROPUS: DUK-trece ≠ conform. `lxml` (instalat).
- **#7 Verificator „temei la sursă"** — PROPUS: constantă/scadență fiscală fără sursă în corpus → pică. Python pur.
- **#8 Baseline determinist** — PROPUS: ceas + firmă-snapshot înghețate → pixel-diff real. `freezegun` (mic, de instalat).
- **#9 Pas keyboard-only** — PROPUS: tab-order, focus-trap în modal, Escape închide. Playwright.
- **#10 Linter de consistență între ecrane** — PROPUS: „identitate între situații similare" (DS). Python (+ AST JS opțional).
- **#11 Raport de acoperire perimetru — §5 CALCULAT** — PROPUS: din fișiere atinse → ecrane → declarații → fațete, computează ce a rulat; §5 = mulțimea neacoperită, calculată nu afirmată. Meta-gardul care ar fi prins că am sărit DS+mobil.

## Regulă de întreținere
Acest fișier e sursa de adevăr a roadmap-ului (nu chat-ul). Când un instrument trece PROPUS→CONSTRUIT, mută-l în
secțiunea de sus și numește fișierul-gardă; `core/test_instrumente_roadmap.py` pică dacă un CONSTRUIT numește un
fișier inexistent (simetric cu GARZI ACOPERIT). Ordinea agreată de atac: #1 ✓ → #3 → #2 → #11 → restul.
