---
title: Cum se corectează TVA la un retur de marfă
description: TVA la un retur de marfă se corectează prin stornare — exact cota facturii inițiale, negată, fără recalculare la data returului — și se raportează pe același rând din D300 ca vânzarea sau achiziția originală.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se corectează TVA la un retur de marfă

La un retur de marfă, TVA nu se „recalculează" — se anulează exact proporția din factura inițială, prin stornare.

## Temeiul legal

::: ghid-temei
„69. — Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (**stornare în roșu**), fie prin înregistrarea inversă a acesteia (**stornare în negru**), în funcție de politica contabilă și programele informatice […]"

— OMFP 1802/2014, reglementări contabile consolidate, pct. 69
:::

Regula generală de stornare (pct. 69 de mai sus) se aplică indiferent de direcția returului — marfă returnată de un client (stornarea unei facturi emise) sau marfă returnată de firmă unui furnizor (stornarea unei facturi primite). În ambele cazuri, documentul de corecție preia cota de TVA exactă a facturii originale, fără recalculare la cota valabilă la data returului — chiar dacă între timp cota legală s-ar fi schimbat.

De precizat: OMFP 1802/2014 conține și un punct distinct (pct. 330), dedicat specific corectării mărfurilor returnate de clienți, cu conturile 411/707/607/371 — un caz particular de returnare a mărfurilor. Temeiul general pentru mecanismul de stornare cu semn (roșu/negru), aplicabil oricărei corecții de factură, inclusiv unui retur de marfă, rămâne pct. 69, citat mai sus.

## Ce se greșește în practică

- Se recalculează TVA la cota valabilă în ziua returului, în loc de a păstra cota facturii inițiale — mai ales riscant dacă între timp s-a schimbat cota standard sau redusă de TVA.
- Se declară returul pe rândul de „Regularizări taxă colectată" din D300, în loc de rândul aferent cotei originale a operațiunii — rândul de regularizări e pentru alte tipuri de ajustări, nu pentru stornarea unui retur din aceeași perioadă fiscală.
- Se tratează diferit din punct de vedere al cotei un retur de vânzare față de un retur către furnizor — principiul e identic în ambele direcții: cota rămâne cea a facturii corectate.

## Ce face iConta.eu

Funcția de stornare din iConta.eu generează documentul de corecție folosind exact cota de TVA a facturii originale, linie cu linie — dacă factura avea, de exemplu, o linie la 21% și una la 11%, stornarea produce aceleași două cote, cu sume negative, fără nicio recalculare. Aceasta se aplică identic pentru o factură emisă (retur de la client) sau o factură primită (retur către furnizor).

La declararea D300, corecția TVA intră automat pe același rând ca operațiunea originală (de exemplu rândul livrărilor taxabile la cota de 21%, pentru o vânzare internă la această cotă), cu valoare și TVA negative — nu pe rândul separat de regularizări.

[iConta.eu](/)
