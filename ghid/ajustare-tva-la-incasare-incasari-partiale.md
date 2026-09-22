---
title: Cum se ajustează TVA la încasare la încasări parțiale
description: La fiecare încasare parțială sub TVA la încasare, se transferă contabil doar TVA-ul aferent sumei efectiv încasate, din 4428 (neexigibilă) în 4427 (colectată), calculat prin suta mărită — restul rămâne neexigibil până la următoarea încasare.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se ajustează TVA la încasare la încasări parțiale

„Ajustarea" TVA-ului la o încasare parțială, sub acest regim, nu e o corecție de eroare — e chiar mecanismul normal de funcționare a sistemului: la fiecare încasare, indiferent cât de mare, se recalculează exact cât TVA a devenit exigibil din acea tranșă, și doar acea sumă trece din TVA neexigibilă în TVA colectată.

## Temeiul legal

::: ghid-temei
**Art. 282 din Codul fiscal (Legea 227/2015) — Exigibilitatea taxei.**

**Alin. (3)**: *„... exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, în cazul persoanelor impozabile care optează în acest sens, denumite în continuare persoane care aplică sistemul TVA la încasare."*

**Alin. (8)**: *„Pentru determinarea taxei aferente încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, care devine exigibilă potrivit prevederilor alin. (3), fiecare încasare totală sau parțială se consideră că include și taxa aferentă."*
:::

## Mecanica ajustării, la fiecare tranșă

La emiterea facturii, TVA-ul intră integral în contul de TVA neexigibilă (**4428**), nu în TVA colectată (4427). Nota contabilă: `4111 = 707 + 4428`.

La fiecare încasare — integrală sau parțială — se calculează TVA-ul exigibil exact pe suma primită, prin suta mărită (alin. (8)):

```
TVA exigibil din tranșă = suma încasată × cotă / (100 + cotă)
```

și se face transferul contabil **doar pe acea sumă**: `4428 = 4427`. Restul TVA-ului facturii rămâne în 4428, neatins, până la următoarea încasare. Simetric, pentru o factură primită de la un furnizor la TVA la încasare, transferul la plată e `4426 = 4428`.

Nu există „ajustare" în sensul de corecție retroactivă a unei sume deja transferate — fiecare tranșă își calculează propriul TVA exigibil, independent, pe baza sumei ei.

## Un exemplu

::: ghid-exemplu
O firmă la TVA la încasare emite o factură de **12.100 lei** (bază 10.000 lei + TVA 2.100 lei, cotă 21%). La emitere: `4111 = 707 (10.000) + 4428 (2.100)`.

Clientul plătește în două tranșe:

- **Tranșa 1: 6.050 lei.** TVA exigibil = 6.050 × 21 / 121 = **1.050 lei**. Notă: `4428 = 4427`, cu 1.050 lei. Rămân în 4428: 2.100 − 1.050 = **1.050 lei**.
- **Tranșa 2: 6.050 lei** (restul facturii). TVA exigibil = 6.050 × 21 / 121 = **1.050 lei**. Notă: `4428 = 4427`, cu 1.050 lei. Sold 4428 pentru această factură: **0 lei**.

Total TVA colectat exigibil, după cele două tranșe: 1.050 + 1.050 = **2.100 lei** — exact TVA-ul facturii, transferat treptat, în ritmul încasării, nu dintr-odată la emitere.
:::

## Ce se greșește în practică

- **Se transferă tot TVA-ul din 4428 în 4427 la prima încasare parțială**, indiferent cât de mică e ea. Transferul trebuie să fie strict proporțional cu suma efectiv încasată în acea tranșă, calculat separat, prin suta mărită.
- **Se calculează TVA-ul din tranșă aplicând cota la baza fără taxă**, în loc de suta mărită pe suma încasată. Alin. (8) spune explicit că suma încasată „se consideră că include și taxa aferentă" — formula e `suma × cotă/(100+cotă)`.
- **Se presupune că, atunci când clientul are mai multe facturi deschise, legea impune o ordine anume de alocare a încasării pe facturi** (de exemplu strict cronologică). Art. 282 nu prescrie nicio ordine — alocarea pe factură, când există mai multe deschise, e o decizie de organizare, nu o cerință legală, iar de ea depinde pe care factură se face de fapt ajustarea.

## Ce face iConta.eu

Pentru fiecare tranșă încasată, TVA-ul exigibil se calculează prin suta mărită (`suma × cotă/(100+cotă)`, rotunjit la 2 zecimale), strict pe suma alocată acelei tranșe — formula e acoperită de teste dedicate.

Când o încasare trebuie repartizată pe mai multe facturi deschise ale aceluiași partener, alocarea se face întâi prin potrivire exactă (o factură cu soldul identic, sau o combinație exactă de facturi), iar în lipsa unei potriviri exacte, cronologic, pe facturile cele mai vechi întâi (FIFO) — o alegere de organizare a aplicației, nu o regulă impusă de art. 282, care nu prescrie ordinea de alocare.

Transferul contabil 4428→4427 (respectiv 4426→4428, pentru facturi primite) nu se face automat la contarea facturii — pentru firmele marcate la TVA la încasare, contarea automată e refuzată explicit, tocmai pentru că suma exigibilă depinde de alocarea încasării; factura trebuie contată manual. Mecanismul e verificat prin teste, dar la data acestui ghid nu are încă nicio instanță pe o firmă reală din portofoliu.

[iConta.eu](/)
