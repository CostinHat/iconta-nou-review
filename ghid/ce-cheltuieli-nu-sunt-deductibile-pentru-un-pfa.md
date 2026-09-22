---
title: Ce cheltuieli nu sunt deductibile pentru un PFA?
description: Codul fiscal exclude expres de la deducere cheltuielile personale, donațiile, amenzile și penalitățile, ratele la credite și achiziția de bunuri amortizabile trecute direct pe cheltuială — plus o categorie de cheltuieli "deductibile limitat" pe care contabilul trebuie să le plafoneze manual.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce cheltuieli nu sunt deductibile pentru un PFA?

Nu orice plată făcută din contul sau numerarul afacerii este automat o cheltuială deductibilă. Codul fiscal listează explicit categoriile excluse de la deducere, iar pe lângă acestea există o categorie intermediară — cheltuielile deductibile *limitat* — care nu sunt nici pe deplin nedeductibile, dar nici integral deductibile, ci plafonate.

## Temeiul legal

::: ghid-temei
Codul fiscal, art. 68 alin. (7) — cheltuieli nedeductibile: "a) sumele sau bunurile utilizate de contribuabil pentru uzul personal sau al familiei sale; ... e) donații de orice fel; f) dobânzile/majorările de întârziere, amenzile, sumele sau valoarea bunurilor confiscate ... și penalitățile, datorate autorităților române/străine ...; g) ratele aferente creditelor angajate; h) cheltuielile de achiziționare sau de fabricare a bunurilor și a drepturilor amortizabile din Registrul-inventar; i) cheltuielile privind bunurile constatate lipsă din gestiune sau degradate și neimputabile, dacă inventarul nu este acoperit de o poliță de asigurare; ..."

Codul fiscal, art. 68 alin. (4) — condiții generale de deductibilitate: "a) să fie efectuate în cadrul activităților independente, justificate prin documente; b) să fie cuprinse în cheltuielile exercițiului financiar al anului în cursul căruia au fost plătite; ... j) să fie efectuate în scopul desfășurării activității și reglementate prin acte normative în vigoare ..."
:::

## Trei categorii, nu doar două

Legea, și evidența practică din registru, disting de fapt trei situații:

1. **Cheltuieli deductibile integral** — îndeplinesc condițiile generale de la art. 68 alin. (4) și nu se regăsesc la lista de excluderi.
2. **Cheltuieli nedeductibile** — cele enumerate explicit la art. 68 alin. (7): uz personal, donații, amenzi și penalități, rate de credit, achiziția directă a unui bun amortizabil (care se deduce prin amortizare, nu integral la cumpărare), bunuri lipsă din gestiune neasigurate.
3. **Cheltuieli deductibile limitat** — de exemplu cheltuielile cu autoturismele folosite mixt (limitate la 50%), care nu sunt nedeductibile, dar nici integral deductibile — plafonul se calculează separat, de la caz la caz.

## Ce se greșește în practică

- Se trece integral pe cheltuială prețul de achiziție al unui echipament amortizabil, în loc să fie recuperat treptat prin amortizare (art. 68 alin. (7) lit. h).
- Se deduc amenzi de circulație sau penalități de întârziere la impozite, confundate cu "cheltuieli de funcționare a afacerii".
- Se deduc integral cheltuieli care ar trebui plafonate (de exemplu, cele legate de un autoturism folosit și în scop personal), fără să se calculeze partea limitată.
- Se deduc rate de credit ca și cheltuieli curente, deși doar dobânda e deductibilă, nu rata (componenta de principal).
- Se trece pe cheltuială valoarea unor bunuri constatate lipsă din gestiune, fără poliță de asigurare care să acopere inventarul — caz explicit exclus de la deducere.

## Ce face iConta.eu

`core/rip_api.py` separă la nivel de cod cele trei categorii din `CATEGORII_PLATA = {"cheltuiala_deductibila", "cheltuiala_limitata", "cheltuiala_nedeductibila", "aport_retragere", "rambursare_credit"}`, iar validarea (`_valideaza`) obligă alegerea unei deductibilități explicite pentru orice plată de tip `cheltuiala*`. În fișa de calcul D212, funcția `fisa_d212` include în calculul automat doar suma cheltuielilor din categoria `cheltuiala_deductibila`; cheltuielile din categoria `cheltuiala_limitata` sunt raportate separat, dar **nu** intră automat în calcul — comentariul din cod e explicit: "cheltuielile limitate NU sunt în calcul - contabilul stabilește partea deductibilă". Cu alte cuvinte, aplicația nu aplică ea singură plafoanele procentuale sau valorice din lege (de exemplu, pentru autoturisme, burse, protocol, tichete de masă) — evidențiază suma totală din categoria limitată și lasă calculul plafonului la latitudinea contabilului.

[iConta.eu](/)
