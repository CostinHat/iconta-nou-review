---
title: Cum gestionez retururile unui magazin online în e-Factura?
description: Un retur de la un client se contabilizează prin stornarea facturii inițiale — aceleași conturi, aceeași cotă de TVA, sumă negativă — iar dacă factura originală a fost transmisă în SPV, documentul de stornare trebuie declarat separat.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum gestionez retururile unui magazin online în e-Factura?

Când un client returnează marfa cumpărată dintr-un magazin online, factura emisă inițial trebuie corectată — nu ștearsă, nu editată. Mecanismul contabil pentru asta e stornarea.

## Temeiul legal

::: ghid-temei
„69. — Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (**stornare în roșu**), fie prin înregistrarea inversă a acesteia (**stornare în negru**), în funcție de politica contabilă și programele informatice […]"

— OMFP 1802/2014, reglementări contabile consolidate, pct. 69
:::

Pentru un retur, factura de stornare preia exact liniile facturii originale (marfa returnată), cu cantități negative, aceeași cotă de TVA și aceeași clasificare fiscală — nu se recalculează nimic la data returului, nici cota de TVA, nici încadrarea operațiunii. Documentul de stornare primește un număr propriu, din aceeași serie, și se leagă de factura inițială printr-o referință internă, pentru trasabilitate.

Dacă factura originală a fost deja transmisă în RO e-Factura, corectarea nu se oprește la emiterea stornării — documentul de stornare e el însuși o factură care trebuie transmisă separat către ANAF, pentru că reprezintă o operațiune economică (negativă) distinctă de cea inițială.

## Ce se greșește în practică

- Se anulează sau se șterge factura inițială la retur, în loc să se emită o factură de stornare — greșit; documentul original rămâne în circuitul contabil și fiscal, corecția se face printr-un document nou.
- Se presupune că stornarea unei facturi transmise în SPV se trimite automat mai departe la ANAF — nu se întâmplă automat; e nevoie de un pas separat de transmitere.
- Se aplică la retur o cotă de TVA diferită de cea a vânzării inițiale — greșit; stornarea moștenește exact cota facturii pe care o corectează.

## Ce face iConta.eu

Butonul „Stornează" din iConta.eu generează automat, pentru retur, documentul de corecție: liniile facturii inițiale cu cantități negate, aceeași cotă de TVA, aceeași clasificare fiscală, curs valutar identic cu al originalului și un număr nou de factură din aceeași serie.

Limitare de produs de reținut pentru un magazin online cu facturi transmise în SPV: butonul de trimitere în e-Factura nu apare pe documentul de stornare — transmiterea efectivă a corecției către ANAF, după emiterea ei, nu are în acest moment o cale automată în interfață.

[iConta.eu](/)
