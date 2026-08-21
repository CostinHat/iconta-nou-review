# ROADMAP INSTRUMENTE & METODĂ — verificare care nu se poate sări

Propunerile agreate cu Costin (19.08.2026, extinse 21.08) pentru a face metoda o POARTĂ, nu un document.
Statut per fiecare; cele **CONSTRUIT** numesc fișierul-gardă (existența lor e păzită de
`core/test_instrumente_roadmap.py`). Motto: *o regulă scrisă și citită nu e o regulă păzită — doar
poarta ține* (vezi [[regula-scrisa-nu-e-regula-pazita]]).

**INSTRUMENTE DECLARATE: 12.** Numărul e citit de gardă din rândul ăsta — dacă apare al 13-lea, rândul
trebuie schimbat, altfel poarta pică. Așa roadmap-ul poate CREȘTE, nu doar să nu mintă.

## Construite (gard mecanic în pre-commit)

- **#1 Detector drop/overwrite tăcut — overwrite** — CONSTRUIT: `core/test_upsert_motivat.py`. Orice `INSERT ... ON CONFLICT DO UPDATE` din producție cere `# upsert-ok: <motiv>` (suprascriere conștientă). Grounded: bug plan_conturi. Prinsă latura suprascrierii; **RĂMAS latura DROP** (input curățat-la-gol-eliminat, ca `separa_cui`) — greu static fără fals-pozitive; abordare propusă: convenție „funcțiile de curățare intrări întorc `(păstrate, ignorate)`", plus `test_masti` (except-gol) + `DEFAULT_FISCAL_TACIT` (coerciție) acoperă restul clasei.
- **F6+F9 vizual/comportamental gardat pe diff** — CONSTRUIT: `frontend_test/vizual/interactiune_scan.py` + `core/test_acoperire_vizuala.py` (fundația lui #2). Apasă butoanele + completează casetele + axe desktop/mobil; poarta pică la schimbare UI fără re-scan curat.
- **#11 §5 CALCULAT (meta-gard)** — CONSTRUIT: `core/test_perimetru_calculat.py`. Din registrul de fațete (MODEL_AUDIT_TENANT.md F1..F9) computează §5 = fațetele MANUAL (neacoperite mecanic), pinat la baseline; orice GARDAT trebuie să numească gard existent (enforcement nu dispare tăcut). Ar fi prins „am sărit DS+mobil". RED-probat.
- **#3 Gard de completitudine a hărții** — CONSTRUIT: `core/test_harta_ecrane.py`. Un `#fa-*` nou neînregistrat în baseline → pică (altfel „acoperit tot" e iar o afirmație).
- **#6 Golden XSD structural pe date POPULATE — latura structurală** — CONSTRUIT: `core/test_golden_xsd.py` + `core/test_d402.py`. Fiecare XSD de declarație din corpus cere un test care generează pe date populate și validează structura (lxml/jar). Grounded: d402 avea generator complet și ZERO teste. RĂMAS latura *valori-golden* (nesursabilă — n-avem declarații-etalon completate, [[anaf-surse-fara-exemple-completate]]).
- **#7 Verificator „temei la sursă"** — CONSTRUIT (21.08, era listat PROPUS deși exista): `core/test_temeiuri.py` (citarea aterizează pe un document din `anaf_surse/`) + `core/test_harta_temei.py` (R5: temei_legal ≠ regula_produs) + verificatorul `TEMEI-STRUCTURAT`/`GRI`. **RĂMAS:** citatul VERBATIM (azi se verifică doar că referința aterizează, nu că actul spune ce pretinzi) — vezi #12 și prioritatea P2.
- **#12 Scanul de constante fiscale + confruntarea instrumentelor** — CONSTRUIT (20-21.08, lipsea din roadmap): `core/scan_constante.py` + `core/test_constante_nesursate.py`. Clasifică literalii numerici din modulele fiscale (A sursat / B nomenclator / C nesursat / D precizie / E temei în proză), clichet **per fișier** (126 → 93), plus **confruntarea celor două instrumente**: un fișier de pe `_TVA_EXCLUSE` al verificatorului care are o cotă în clasa C = dezacord între două măsurători ale aceluiași lucru. Grounded: `cote_tva.py` era raportat nesursat deși verificatorul îl scutea deliberat.

## Propuse (neconstruite încă — backlog urmărit)

- **#2 Fuzzer de formulare** — PARȚIAL (interactiune_scan apasă/completează). RĂMAS: generarea invalidelor per câmp (gol/peste-lungime/tip/duplicat/limită) + verdict 14.4 automat. Playwright, deja instalat.
- **#4 Matrice de stări de date** — PROPUS: fiecare ecran peste stări (gol/populat/limită, micro/profit/PFA). Playwright + seed.
- **#5 Reconciliator de cifre (Regula 14.2)** — PROPUS: total = suma rândurilor; previzualizare = buton = rezultat, asertat. Playwright.
- **#8 Baseline determinist** — PROPUS: ceas + firmă-snapshot înghețate → pixel-diff real. `freezegun` (mic, de instalat).
- **#9 Pas keyboard-only** — PROPUS: tab-order, focus-trap în modal, Escape închide. Playwright.
- **#10 Linter de consistență între ecrane** — PROPUS: „identitate între situații similare" (DS). Python (+ AST JS opțional).

## ORDINEA DE ATAC — confirmată de Costin, 21.08.2026

Principiul: *întâi ce face restul mai ieftin sau mai sigur; apoi ce nu cade singur niciodată.*

| P | ce | de ce aici |
|---|---|---|
| **P1** | Roadmapul la zi + gardul care-i permite să crească | oprește sângerarea: un instrument construit putea lipsi din registru fără ca nimeni să afle |
| **P2** | **Comunicarea** (chiriaș, DS cap.25) + gardul de proprietate „niciun ecran nu scrie în coajă" | gardul blochează REGRESIA cât lucrăm la ceilalți chiriași — clichet, nu intenție |
| **P3** | `fel` + `obiect` pe afirmații (R2′ + R2) **+ `temei`/`arbitru` despărțite + `valabil_de`/`valabil_pana`** | necunoașterea declarată depinde de ele; R2 are deja xfail care cade singur |
| **P4** | **„Ce nu poate spune verificarea asta"** (chiriaș nou) + `limita` obligatorie la verificatori | devine posibilă abia după P3 |
| **P5** | **R4** — temeiul termenelor per tip | datorie fiscală reală; decizia luată, fezabilitatea verificată, gardul scris în xfail strict |
| **P6** | **Starea de lucru** + **Drumul** (chiriași) | mult mai mici odată ce gardul din P2 există |
| **P7** | Clichet pe afirmații-șir + cele 12 constrângeri ale hărții | închiderea firului, după ce structura există |
| **‖** | **`text_citat` obligatoriu la temeiurile noi** + gardul urcă la „citatul există VERBATIM în documentul citat" | Python pur, nu atinge niciun ecran → poate rula în PARALEL, oricând |

**Amânat deliberat:** #4, #5, #8, #9, #10 — toate testează ECRANE, iar ecranele sunt pe cale să se miște
(DS cap.25). Construite acum, le-am reface.

**Nu intră în ordine, fiindcă sunt decizii, nu muncă:** `state_plata` nepersistat (se persistă la emitere,
sau se scoate tabelul?) · cine închide cele 12 constrângeri ale hărții.

## Regulă de întreținere
Acest fișier e sursa de adevăr a roadmap-ului (nu chat-ul). Când un instrument trece PROPUS→CONSTRUIT,
mută-l în secțiunea de sus și numește fișierul-gardă; `core/test_instrumente_roadmap.py` pică dacă un
CONSTRUIT numește un fișier inexistent (simetric cu GARZI ACOPERIT), sau dacă numărul declarat de
instrumente nu se potrivește cu cele găsite.

**CE NU E GARDAT, și de ce (măsurat 21.08.2026).** Direcția inversă — *„tot ce s-a construit e trecut
aici"* — n-are proxy mecanic curat. Trei definiții încercate și respinse prin calibrare:
1. *„orice fișier cu clichet trebuie să fie într-un registru"* → toate cele 12 clichete existente sunt
   deja în GARZI.md, inclusiv cel care lipsea de aici. Gardul ar fi fost VID.
2. *„modul importat doar de teste"* → 44 de rezultate, aproape toate generatoare de declarații
   invizibile la grep fiindcă sunt dispecerizate dinamic. Zgomot inutilizabil.
3. *„modul cu bloc `__main__` care printează"* → 11 rezultate, ~jumătate joburi de rulare (`cron`,
   `alerta_acces`, `audit_retentie`), nu instrumente.

Deci „instrument" nu se poate recunoaște mecanic aici. Rămâne disciplină: **când construiești ceva ce
MĂSOARĂ repo-ul, treci-l în lista de sus și crește numărul declarat.** Un gard vid ar fi fost mai rău
decât absența lui — ar fi raportat verde despre o lume pe care n-o vede.
