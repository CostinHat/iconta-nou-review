---
title: Cum verifici D112 cu balanța contabilă?
description: Verificarea D112 vs. balanță se face pe patru conturi (444, 4315, 4316, 436), comparând sumele declarate cu rulajul creditor din notele validate, cu o toleranță de rotunjire proporțională cu numărul de salariați.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verifici D112 cu balanța contabilă?

Balanța de verificare a lunii conține, printre altele, patru conturi care ar trebui să corespundă cu sumele declarate în D112. Verificarea nu e o simplă comparație vizuală de solduri, ci o comparație pe fiecare tip de obligație, cu reguli precise de toleranță și de interpretare a diferențelor.

## Temeiul legal

::: ghid-temei
"Articolul 147 — Depunerea Declarației privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate. (1) Persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora [...] sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate." — Codul fiscal (Legea 227/2015), art. 147
:::

Din balanța de verificare a lunii, patru conturi sunt relevante pentru controlul cu D112 — toate comparate pe rulajul creditor, nu pe sold:

| Cont | Ce reprezintă | Se compară cu codul D112 |
|---|---|---|
| 444 | Impozit pe venit din salarii | 602 |
| 4315 | Contribuție de asigurări sociale (CAS) | 412 + 458 |
| 4316 | Contribuție de asigurări sociale de sănătate (CASS) | 432 + 459 |
| 436 | Contribuție asiguratorie pentru muncă (CAM) | 480 |

Codurile 458 și 459 din D112 (suprataxa angajatorului la part-time) se regăsesc tot în 4315/4316, nu în conturi separate.

Pași pentru verificarea manuală, dacă vrei să o faci fără aplicație:
1. Extrage rulajul creditor al fiecărui cont din balanța lunii, dar numai din notele deja validate — o notă de salarii în ciornă nu e evidență contabilă.
2. Extrage sumele declarate pe fiecare cod din XML-ul D112 (ideal cel efectiv depus, nu doar recalculat acum).
3. Compară fiecare pereche cont-cod cu o toleranță de 0,5 lei per salariat (minim 1 leu) — nu o valoare fixă.
4. Pentru orice diferență peste toleranță, verifică dacă există o notă de salarii lipsă, o notă în ciornă sau o modificare ulterioară a statului de plată.

## Ce se greșește în practică

Greșeala tipică e compararea soldului contului, nu a rulajului creditor al lunii — dacă un cont are solduri reportate din luni anterioare, soldul total poate diferi de D112 chiar dacă luna curentă e corect înregistrată. A doua greșeală e includerea contului 421 (brutul) în comparație — el nu face parte din verificare, pentru că D112 raportează baza de contribuții, nu brutul.

## Ce face iConta.eu

Funcția `verifica_d112` (`core/control_incrucisat.py`) automatizează exact acest proces: citește rulajele creditoare doar din notele validate, parsează sumele declarate direct din XML-ul D112, aplică toleranța corespunzătoare numărului de salariați și afișează verdictul (verde/roșu/gri) pentru fiecare din cele patru conturi, cu temeiul legal și cauza citate pe fiecare constatare.

[iConta.eu](/)
