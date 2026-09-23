---
title: Cum corectez o factură deja transmisă în RO e-Factura?
description: O factură deja transmisă în SPV nu se editează — se corectează printr-o factură de stornare, un document nou, cu valori negative, care trebuie la rândul lui transmis separat în e-Factura.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez o factură deja transmisă în RO e-Factura?

O greșeală pe o factură deja transmisă în SPV nu se poate repara prin editarea documentului original — odată intrată în circuitul e-Factura, o factură e definitivă. Corecția se face prin stornare: un document nou, distinct.

## Temeiul legal

::: ghid-temei
„69. — Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (**stornare în roșu**), fie prin înregistrarea inversă a acesteia (**stornare în negru**), în funcție de politica contabilă și programele informatice […]"

— OMFP 1802/2014, reglementări contabile consolidate, pct. 69
:::

Corectarea unei facturi presupune emiterea unei facturi de stornare: un document nou, cu un număr propriu, care preia liniile facturii inițiale cu cantități negative, păstrează cursul valutar și clasificarea fiscală ale originalului (aceeași cotă de TVA, aceeași încadrare — livrare internă, intracomunitară, taxare inversă etc.) și se leagă de factura corectată printr-o referință internă. Practic anulează exact suma în lei a facturii inițiale, fără să recalculeze nimic la data corecției.

Corectarea are însă doi pași distincți: (1) emiterea facturii de stornare propriu-zise și (2) transmiterea acelui document nou către ANAF, prin SPV — pentru că factura de stornare e ea însăși un document fiscal care trebuie declarat, nu doar o corecție internă.

## Ce se greșește în practică

- Se încearcă editarea sau ștergerea facturii inițiale deja transmise — nu e o opțiune; corecția se face exclusiv prin stornare.
- Se emite factura de stornare, dar se uită transmiterea ei separată în SPV, considerând corectarea „încheiată" doar prin emiterea documentului.
- Se aplică la stornare o altă cotă de TVA decât cea a facturii originale, de exemplu dacă între timp s-a schimbat cota legală — greșit; stornarea păstrează exact cota, conturile și clasificarea fiscală a originalului.

## Ce face iConta.eu

La stornare, iConta.eu creează automat un document nou, cu număr propriu rezervat din aceeași serie, cu liniile facturii inițiale copiate și cantitățile negate, păstrând cursul valutar și clasificarea fiscală ale originalului. Corecția unei facturi contabilizate e blocată la ștergere — sistemul refuză explicit ștergerea unei facturi cu notă contabilă deja generată, cu mesajul că se corectează prin stornare, nu prin editare.

De reținut: butonul de trimitere în SPV nu apare pe documentul de stornare — la acest moment, transmiterea facturii de corecție către ANAF nu are un buton dedicat în interfață. Pasul (2) de mai sus, transmiterea efectivă a stornării, e o limitare curentă a produsului, nu un pas normal de flux acoperit automat.

[iConta.eu](/)
