---
title: Cum remediez diferențele semnalate prin e-TVA
description: iConta.eu nu este conectat la sistemul oficial RO e-TVA al ANAF — dar are o verificare internă proprie, D300 vs balanță, care semnalează diferențe similare înainte de depunere, direct în aplicație.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum remediez diferențele semnalate prin e-TVA

De clarificat de la început, onest: iConta.eu nu este integrat cu sistemul oficial **RO e-TVA** al ANAF (mecanismul prin care ANAF îți compară declarația de TVA cu datele proprii și îți trimite o notificare de conformare, dacă identifică diferențe). Dacă ai primit o notificare de la ANAF prin e-TVA, aceea e un proces extern, separat de aplicație, la care răspunzi direct în SPV, conform termenelor comunicate de ANAF.

Ce are aplicația, și confundă uneori utilizatorii cu „semnal de sistem" generic, e o verificare internă proprie: compararea lunară dintre D300 și balanța contabilă, pe conturile de TVA — un control preventiv, făcut înainte de depunere, nu un răspuns la o notificare ANAF.

## Temeiul legal

::: ghid-temei
Art. 281 din Codul fiscal (Legea 227/2015) — "Faptul generator pentru livrări de bunuri și prestări de servicii" — stabilește momentul de la care se naște obligația de TVA. D300 se calculează pe facturile lunii; balanța contabilă pe înregistrările efectiv făcute. Verificarea internă din aplicație folosește acest temei pentru comparația D300–balanță; ea nu are legătură cu procedura oficială de notificare de conformare a ANAF. Titlul și numărul articolului sunt confirmate în sursele legale folosite de aplicație; textul integral nu e citat literal aici.
:::

## Cum remediezi o diferență semnalată în aplicație

Verificarea internă acoperă cinci conturi (4427, 4426, 4423, 4424, informativ 4428), cu stările verde/roșu/gri și o toleranță de 1 leu, pe bază de note validate. În funcție de cauza diferenței:

- dacă e explicată mecanic de o factură fără notă validată — poți valida corecția propusă;
- dacă există deja o notă în ciornă care ar rezolva diferența — trebuie doar validată;
- dacă cauza nu e dovedită mecanic (storno neînregistrat, TVA la încasare, regularizări, note manuale) — e nevoie de investigație manuală, aplicația nu ajustează automat.

## Ce se greșește în practică

- Se confundă avertizarea internă a aplicației cu o notificare oficială ANAF — sunt lucruri diferite, cu proceduri de răspuns diferite.
- Se ignoră o notificare reală primită prin e-TVA, presupunând că verificarea din aplicație „acoperă" deja subiectul — verificarea internă e preventivă, nu un canal de comunicare cu ANAF.
- Se validează grăbit o corecție fără să se identifice întâi dacă diferența e executabilă sau cere investigație.

## Ce face iConta.eu

Aplicația compară automat, lunar, D300 cu rulajele celor cinci conturi de TVA, pe bază de note validate, și afișează starea fiecărui cont (verde/roșu/gri), cu toleranță de 1 leu — o verificare internă, preventivă, distinctă de mecanismul oficial RO e-TVA al ANAF. Pentru orice notificare primită efectiv de la ANAF prin e-TVA, răspunsul se face direct în SPV, conform indicațiilor din notificare.

[iConta.eu](/)
