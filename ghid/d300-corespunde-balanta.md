---
title: Ce fac dacă D300 nu corespunde cu balanța?
description: O diferență D300–balanță nu e automat o greșeală — poate fi și semnul unei evidențe rămase în urmă. Aplicația împarte fiecare cont în verde, roșu sau gri, cu o toleranță de 1 leu.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă D300 nu corespunde cu balanța?

Când declarația D300 nu se potrivește cu rulajele conturilor de TVA, primul pas nu e să „forțezi" cifrele să coincidă, ci să înțelegi de ce diferă. D300 se calculează pe facturile lunii, iar balanța pe înregistrările contabile — cele două surse nu sunt mereu sincrone, mai ales dacă au rămas note de contabilitate nevalidate.

## Temeiul legal

::: ghid-temei
Art. 281 din Codul fiscal (Legea 227/2015) — "Faptul generator pentru livrări de bunuri și prestări de servicii" — stabilește momentul de la care se naște obligația de TVA. D300 se calculează pe baza facturilor lunii (fapt generator), în timp ce balanța contabilă reflectă înregistrările efectiv făcute — de aici pot apărea diferențe legitime, nu neapărat erori. Titlul și numărul articolului sunt confirmate în sursele legale folosite de aplicație; textul integral al articolului nu a fost citat literal aici.

Art. 282 din Codul fiscal — "Exigibilitatea pentru livrări de bunuri și prestări de servicii" — explică de ce unele diferențe (de exemplu TVA la încasare, cu exigibilitate decalată) nu trebuie tratate automat ca eroare. Menționat ca temei conceptual, nu ca prag de calcul folosit direct în verificare.
:::

## Cele cinci conturi verificate

Comparația se face pe cinci conturi, fiecare mapat pe rândul corespunzător din D300:

| Rând D300 | Cont | Sens | Observație |
|---|---|---|---|
| TOTAL TAXĂ COLECTATĂ (R17_2) | 4427 | credit | |
| TOTAL TAXĂ DEDUCTIBILĂ (R27_2) | 4426 | debit | nu R31_2 (acela e alt rând, „Ajustări/pro-rata") |
| Sold TVA de plată (R41_2) | 4423 | credit | tăcut dacă ambele sunt 0 |
| Sold TVA de recuperat (R42_2) | 4424 | debit | tăcut dacă ambele sunt 0 |
| — | 4428 (TVA neexigibilă) | net | doar informativ, niciodată roșu |

Fiecare cont primește o stare: **verde** (coerent), **roșu** (divergent, cu cifre) sau **gri** (nu s-a putut verifica, de regulă din lipsă de date). Toleranța aplicată e de 1 leu — normal, pentru că D300 rotunjește la leu, iar contabilitatea ține banii cu bani (subunități).

## Cum tratezi o diferență

Contează doar **notele validate** — o notă lăsată în ciornă nu e considerată evidență. În funcție de cauza diferenței:

- **cauză dovedită mecanic** (facturi emise/primite fără notă validată) — poți valida corecția propusă;
- **cauză sugerată** (note deja în ciornă, neconfirmate) — trebuie doar validate, nu recreate;
- **cauză nedovedită** (note manuale pe cont, storno neînregistrat, TVA la încasare, regularizări, facturi înregistrate în altă lună decât cea a facturii) — aplicația nu ajustează automat; e nevoie de investigație manuală.

## Ce se greșește în practică

- Se ignoră un verde considerându-l „automat corect" — dacă lipsesc simetric facturi din ambii termeni ai comparației, un verde poate fi fals-pozitiv; aplicația degradează atunci starea la gri, tocmai ca să nu dea o falsă asigurare.
- Se contabilizează diferența direct pe contul de TVA, fără să se stabilească întâi dacă e o cauză executabilă, una care doar așteaptă validarea unei note deja create, sau una care cere investigație.
- Se confundă contul 4428 (TVA neexigibilă) cu unul „de verificat" ca și celelalte patru — e doar informativ, nu intră niciodată în starea roșie.

## Ce face iConta.eu

Aplicația compară automat, lunar, D300 cu rulajele celor cinci conturi de mai sus, pe bază de note validate, și afișează pentru fiecare cont starea verde/roșu/gri, cu toleranța de 1 leu. Când poate identifica exact cauza diferenței dintr-o notă nevalidată, propune corecția (respectând principiul celor patru ochi); când cauza nu e dovedită mecanic (storno, TVA la încasare, regularizări), semnalează situația pentru investigație manuală, fără să ajusteze automat contul.

[iConta.eu](/)
