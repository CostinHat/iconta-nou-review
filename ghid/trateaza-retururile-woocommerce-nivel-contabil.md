---
title: "Cum se tratează retururile din WooCommerce la nivel contabil?"
description: "Un retur cere reducerea bazei de impozitare a TVA și, de regulă, o factură de corecție — pași pe care conectorul WooCommerce al iConta.eu nu-i declanșează automat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se tratează retururile din WooCommerce la nivel contabil?

Un client care returnează un produs cumpărat dintr-un magazin online nu anulează pur și simplu vânzarea din punct de vedere contabil — factura deja emisă trebuie corectată, iar baza de impozitare a TVA ajustată corespunzător.

## Temeiul legal

::: ghid-temei
„Baza de impozitare se reduce în următoarele situații: [...] b) în cazul refuzurilor totale sau parțiale privind cantitatea, calitatea ori prețurile bunurilor livrate sau ale serviciilor prestate, precum și în cazul desființării totale ori parțiale a contractului pentru livrarea sau prestarea în cauză ca urmare a unui acord scris între părți sau ca urmare a unei hotărâri judecătorești definitive/definitive și irevocabile, după caz, sau în urma unui arbitraj."
— Legea 227/2015 (Codul fiscal), art. 287 lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Un retur de marfă e, fiscal, un „refuz total sau parțial" al bunurilor livrate — situație care impune reducerea bazei de impozitare a TVA, nu doar o simplă notă internă.
- Reducerea bazei de impozitare se materializează printr-o factură de corecție: fie o factură nouă cu valorile inițiale corectate, fie o factură cu valori negative care anulează (parțial sau total) factura inițială, conform regulilor de corectare a facturilor (art. 330 Cod fiscal).
- Momentul de referință pentru ajustare e data la care returul e efectiv acceptat/constatat, nu data plasării comenzii inițiale.

## Ce se greșește în practică

- Se așteaptă ca statusul „refunded" (rambursat) dintr-o comandă WooCommerce să genereze automat, în iConta, o factură de stornare — nu se întâmplă nimic automat pentru aceste comenzi.
- Se anulează pur și simplu factura inițială, în loc să se emită o factură de corecție conform regulilor de corectare a facturilor, cu referință explicită la factura corectată.
- Se ignoră obligația de a corecta factura doar pentru că suma a fost deja rambursată clientului prin procesatorul de plăți — rambursarea banilor și corectarea documentului fiscal sunt două operațiuni distincte.

## Ce face iConta.eu

Conectorul WooCommerce al iConta.eu importă exclusiv comenzile cu statusul `completed` sau `processing` — comenzile cu statusul `refunded` (sau `cancelled`, `on-hold`, `pending`, `failed`) **nu intră niciodată în listă**, indiferent de altă logică din aplicație. Nu există nicio funcție de stornare sau retur declanșată automat de o schimbare de status în WooCommerce. Dacă o comandă deja facturată e ulterior returnată, corectarea facturii (emiterea unei facturi de stornare, conform regulilor generale de corectare din aplicație) rămâne un pas manual, în afara acestui conector.

[iConta.eu](/)
