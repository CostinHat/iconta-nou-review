---
title: Cum se declară dividendele interimare în D205?
description: Dividendul interimar se înregistrează inițial în contul 463, distinct de contul 457 pe care se calculează D205 — el devine vizibil pentru declarație abia din momentul regularizării anuale, care mută valoarea în 457.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se declară dividendele interimare în D205?

Dividendele interimare — distribuite trimestrial, pe baza situațiilor financiare interimare — au un circuit contabil propriu, diferit de al dividendului anual, iar acest lucru contează pentru momentul în care apar în D205.

## Temeiul legal

::: ghid-temei
**OMFP 1802/2014, pct. 423^1**: „Entitățile care au optat [...] să repartizeze dividende în cursul exercițiului financiar evidențiază acea repartizare în contul 463 «Creanțe reprezentând dividende repartizate în cursul exercițiului financiar» (articol contabil 463 = 456 «Decontări cu acționarii/asociații privind capitalul»)."

**OMFP 1802/2014, pct. 423^2**: „Dividendele repartizate conform pct. 423^1 se regularizează pe seama dividendelor distribuite pe baza situațiilor financiare anuale aprobate [...] (articol contabil 457 «Dividende de plată» = 463)."
:::

Aici e punctul-cheie: dividendul interimar, la momentul distribuirii, se înregistrează prin contul 463, nu prin contul 457. Declarația D205 însă se calculează pe baza mișcărilor din contul 457 (dividendul distribuit apare ca sold creditor al acestui cont, dividendul plătit ca sold debitor). Practic, un dividend pur interimar, distribuit dar încă neregularizat prin situațiile financiare anuale, nu a ajuns încă în contul 457 — deci nu intră automat în calculul D205 pentru perioada respectivă.

Valoarea devine vizibilă pentru D205 abia din momentul regularizării anuale, când se înregistrează dividendul anual aprobat (1171=457) și se compensează cu interimarele deja distribuite (457=463, conform pct. 423^2) — moment în care suma ajunge efectiv în contul pe care declarația îl citește.

## Ce se greșește în practică

- Se așteaptă ca dividendul interimar să apară automat în D205 imediat după distribuire — nu apare, pentru că circuitul contabil trece prin 463, nu prin 457, până la regularizare.
- Se declară manual dividendul interimar înainte de regularizare, dublând ulterior suma când regularizarea anuală ajunge și ea în 457.

## Ce face iConta.eu

Ecranul de decontări asociați din iConta.eu înregistrează corect dividendul interimar prin contul 463 (potrivit pct. 423^1), iar D205, ca funcționalitate separată, calculează automat baza declarației din mișcările contului 457. Așadar dividendele interimare, distribuite dar neregularizate încă, nu apar în D205 până la regularizarea anuală — un aspect de verificat explicit de contabil dacă o firmă a distribuit dividende interimare și se apropie termenul de depunere a declarației fără să fi făcut încă regularizarea prin situațiile financiare anuale.

[iConta.eu](/)
