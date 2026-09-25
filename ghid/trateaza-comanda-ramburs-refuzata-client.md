---
title: "Cum se tratează o comandă ramburs refuzată de client?"
description: "Când clientul refuză coletul la livrare, factura emisă trebuie stornată și, dacă era colectată, TVA se ajustează — baza legală și greșelile frecvente."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se tratează o comandă ramburs refuzată de client?

În comerțul online, o parte din comenzile cu plata ramburs se întorc la expeditor: clientul nu e acasă, refuză coletul sau se răzgândește. Fiscal, o comandă refuzată e un caz clasic de ajustare a bazei de impozitare — nu o simplă „anulare" fără urmă contabilă.

## Temeiul legal

::: ghid-temei
„Baza de impozitare se reduce în următoarele situații: [...] b) în cazul refuzurilor totale sau parțiale privind cantitatea, calitatea ori prețurile bunurilor livrate sau ale serviciilor prestate, precum și în cazul desființării totale ori parțiale a contractului pentru livrarea sau prestarea în cauză ca urmare a unui acord scris între părți sau ca urmare a unei hotărâri judecătorești definitive/definitive și irevocabile, după caz, sau în urma unui arbitraj."
— Legea 227/2015 (Codul fiscal), art. 287 lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă concret când coletul e refuzat la livrare:

- Refuzul total al coletului la curier e un **refuz privind bunurile livrate** în sensul art. 287 lit. b) — livrarea nu se mai consideră realizată către acel client, iar baza de impozitare a TVA aferentă acelei facturi se reduce.
- Practic, se emite o **factură de stornare** (sau o factură de corecție, conform art. 330 alin. (2) din Codul fiscal) pentru factura inițială, iar TVA colectată aferentă vânzării anulate se ajustează în decontul perioadei în care are loc stornarea — nu retroactiv, pe perioada facturii inițiale.
- Marfa care revine în gestiune se reintră pe stoc la valoarea de intrare inițială, iar veniturile din vânzare (707) și TVA colectată (4427) recunoscute inițial se reduc prin storno.
- Dacă firma a încasat deja contravaloarea (ramburs colectat de curier și virat firmei, apoi returnat), fluxul de trezorerie trebuie și el reconciliat cu stornarea facturii, altfel apar diferențe la reconcilierea casă/bancă.

## Ce se greșește în practică

- Se șterge pur și simplu factura sau comanda din sistem, fără stornare documentată — ceea ce lasă o gaură în secvența de numerotare a facturilor și nu respectă cerința de a păstra urma fiscală a operațiunii.
- Se ajustează TVA retroactiv, pe perioada facturii inițiale, în loc de perioada curentă în care are loc refuzul — art. 287 nu cere recalcularea unui decont deja depus, ci ajustarea în perioada stornării.
- Nu se reintegrează marfa refuzată în stocul contabil la momentul returului fizic, ceea ce duce la diferențe între stocul scriptic și cel faptic la inventar.

## Ce face iConta.eu

La data acestui ghid, iConta.eu oferă evidența contabilă generală pentru facturare și stocuri, inclusiv posibilitatea de a storna o factură emisă, dar **nu are un flux automat dedicat** pentru „comandă ramburs refuzată" care să lege, într-un singur pas, stornarea facturii, reintrarea mărfii în stoc și reconcilierea încasării de la curier — operațiunile trebuie înregistrate separat de contabil.

[iConta.eu](/)
