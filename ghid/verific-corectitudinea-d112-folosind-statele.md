---
title: Cum verific corectitudinea D112 folosind statele de plată
description: Verificarea D112 față de contabilitate se face pe patru perechi cod-cont (impozit, CAS, CASS, CAM), cu o toleranță de rotunjire care crește cu numărul de salariați și trei stări posibile — verde, roșu, gri.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific corectitudinea D112 folosind statele de plată

Cea mai fiabilă verificare a unei D112 nu e recitirea manuală a declarației, ci compararea ei automată cu ce a fost efectiv contabilizat din statele de plată ale lunii. iConta.eu face acest control încrucișat pe patru conturi, cu reguli explicite pentru fiecare tip de divergență.

## Temeiul legal

::: ghid-temei
"Articolul 147 — Depunerea Declarației privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate. (1) Persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora [...] sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate." — Codul fiscal (Legea 227/2015), art. 147
:::

Verificarea compară, pentru fiecare lună, sumele declarate în D112 cu rulajul creditor al patru conturi contabile:

| Obligație (cod D112) | Cont contabil | Cotă | Temei |
|---|---|---|---|
| Impozit pe salarii (602) | 444 | 10% | CF art. 64 alin. (1) |
| CAS (412 + 458) | 4315 | 25% | CF art. 138 lit. a) |
| CASS (432 + 459) | 4316 | 10% | CF art. 156 |
| CAM (480) | 436 | 2,25% | CF art. 220^3 alin. (1) |

Codurile 458 și 459 reprezintă suprataxa datorată de angajator la contractele part-time sub un anumit prag și se contabilizează tot în conturile 4315, respectiv 4316 (prin conturile de cheltuială aferente), nu separat.

Sursa sumelor declarate: se preferă XML-ul D112 efectiv depus și persistat la depunere (dacă există); dacă nu, se regenerează D112 pentru luna respectivă. Aplicația comunică mereu care variantă a folosit.

Toleranța nu e fixă la 1 leu — crește cu numărul de salariați (0,5 lei per salariat), pentru că D112 rotunjește totalul la leu, iar contabilitatea ține sume exacte pe fiecare persoană. O toleranță fixă ar da diferențe false la firmele cu mai mulți angajați.

Rezultatul verificării are trei stări posibile, nu doar două: verde (diferență în limita toleranței), roșu (diferență reală, cu remediu specific cauzei) și gri (D112 nu a putut fi generată sau nu se datorează în luna respectivă — de exemplu, dacă firma nu a avut salariați). Gri nu înseamnă eroare a aplicației, ci imposibilitatea de a da un verdict cu datele disponibile.

## Ce se greșește în practică

Greșeala frecventă e compararea manuală doar a impozitului pe venit din statul de plată cu D112, ignorând CAS, CASS și CAM — patru sunt conturile relevante, nu unul singur. A doua greșeală e ignorarea faptului că brutul contabil (contul 421) nu face parte din această verificare — D112 raportează baza de contribuții, care poate diverge legitim de brut pe lunile cu concedii medicale.

## Ce face iConta.eu

Funcția `verifica_d112` (`core/control_incrucisat.py`) execută automat acest control pentru fiecare lună: generează sau preia D112, parsează sumele declarate direct din XML (nu printr-o reagregare separată a salariaților, pentru a evita o "a treia cifră"), citește rulajele contabile doar din notele validate, aplică toleranța corectă și afișează verdictul pe fiecare din cele patru conturi, cu temeiul citat explicit pentru fiecare constatare.

[iConta.eu](/)
