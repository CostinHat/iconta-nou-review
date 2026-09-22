---
title: Cum se descarcă gestiunea pentru produse finite?
description: Descărcarea gestiunii la vânzarea produselor finite se face la cost standard (711=345), cu diferențele de preț repartizate separat pe 348, potrivit OMFP 1802/2014 — metoda inventarului permanent cu cost standard.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se descarcă gestiunea de produse finite la vânzare?

O firmă cu producție proprie ține produsele finite la un **cost standard** (o valoare prestabilită, nu costul efectiv al fiecărui lot), iar diferența dintre cost standard și cost efectiv se izolează separat, pe contul 348. Descărcarea gestiunii la vânzare urmează aceeași logică: ieși din stoc la cost standard, apoi repartizezi asupra vânzării partea ei din diferențele acumulate.

## Temeiul legal

::: ghid-temei
Metoda ține de **OMFP 1802/2014**, secțiunea privind evaluarea stocurilor și utilizarea costului standard cu evidențierea distinctă a diferențelor de preț (cont 348 „Diferențe de preț la produse"). Principiul: stocul se ține la o valoare de referință constantă (costul standard), iar abaterile față de costul efectiv de producție se contabilizează separat, nu se amestecă în valoarea stocului.
:::

## Fluxul complet

**La obținerea produselor finite** din producție: `345 = 711`, la cost standard. Dacă se cunoaște și costul efectiv, diferența intră pe 348 — nefavorabilă (efectiv > standard) cu `348 = 711`, favorabilă (efectiv < standard) cu `711 = 348`.

**La vânzare**, două operațiuni concomitente:

- factura către client: `4111 = 701 + 4427` (venitul din vânzare, separat de TVA)
- descărcarea gestiunii: `711 = 345` la cost standard, plus repartizarea diferențelor acumulate pe 348 aferente cantității ieșite, calculată printr-un **coeficient de diferențe de preț** — raportul dintre soldul de diferențe (inițial + rulaj al lunii) și soldul de produse finite la cost standard (inițial + intrări). Coeficientul aplicat la cantitatea ieșită dă diferența care iese odată cu ea: nefavorabilă cu `711 = 348`, favorabilă cu `348 = 711`.

Ideea centrală: contul 345 rămâne mereu la cost standard — diferențele „călătoresc" separat, pe 348, și se decontează proporțional la fiecare ieșire din gestiune, nu doar la obținere.

## Ce se greșește în practică

- **Se descarcă gestiunea la cost efectiv**, nu la cost standard — asta rupe evidența, pentru că 345 nu mai reflectă valoarea de referință și diferențele nu se mai pot reconstitui.
- **Se uită repartizarea coeficientului de diferențe** la vânzare — diferențele rămân „blocate" pe 348 la nesfârșit, în loc să se deconteze proporțional cu ieșirile.
- **Producția în curs de la finele lunii nu se reia** la începutul lunii următoare (`331 = 711` la constatare, apoi stornare `711 = 331`) — fără reluare, luna următoare pornește cu o bază de calcul greșită.

## Ce face iConta.eu

Motorul de producție calculează nota de obținere la cost standard, cu diferențele de preț separate pe 348, și nota de vânzare cu descărcarea gestiunii la cost standard plus repartizarea coeficientului de diferențe pe cantitatea ieșită. Coeficientul se calculează din soldul inițial și rulajul contului 348 raportate la soldul inițial și intrările pe 345, exact structura din OMFP 1802/2014. Producția în curs de la finele lunii se constată și se reia distinct, ca operațiuni separate de obținerea produsului finit.

[iConta.eu](/)
