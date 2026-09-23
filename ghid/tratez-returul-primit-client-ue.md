---
title: Cum tratez returul primit de la un client din UE?
description: Returul unei achiziții intracomunitare nu are un cod de tranzacție D390 propriu — se reflectă prin stornarea (ajustarea) bazei impozabile a achiziției inițiale, cu aceeași clasificare fiscală.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum tratez returul primit de la un client din UE?

Când returnați bunuri unui furnizor dintr-un alt stat membru, după o achiziție intracomunitară (AIC), operațiunea nu se declară printr-un cod separat de "retur" — nici în D300, nici în D390. Se ajustează (stornează) baza impozabilă și taxarea inversă înregistrate la achiziția inițială.

## Temeiul legal

::: ghid-temei
"Ajustările se declară pentru luna calendaristică în care intervine exigibilitatea taxei, conform **art. 282 alin. (9) din Codul fiscal**, respectiv în luna calendaristică în care regularizarea a fost comunicată clientului." — OPANAF 705/2020, instrucțiuni D390

Nomenclatorul D390 definește: "A - pentru achiziții intracomunitare de bunuri, achiziții care urmează transferurilor scutite, achiziții efectuate de beneficiarul livrării ulterioare în cadrul unei operațiuni triunghiulare din alte state membre." Nu există un cod separat pentru retur.
:::

O achiziție intracomunitară taxabilă se înregistrează cu taxare inversă (4426 = 4427, formula prevăzută de normele la Cod fiscal, art. 331). Când marfa e returnată furnizorului, tratamentul corect e stornarea acestei operațiuni — aceleași conturi, cu suma negată — nu o operațiune nouă, de sens opus. Clasificarea D390 rămâne aceeași (cod A pentru bunuri), doar cu bază negativă.

Cât privește momentul declarării, se aplică aceeași regulă ca la orice ajustare intracomunitară: luna exigibilității sau luna comunicării regularizării către furnizor (art. 282 alin. 9 CF), nu retroactiv, prin editarea unei declarații deja depuse — o corecție a unei perioade trecute se face printr-o declarație rectificativă pentru acea perioadă, nu prin înscrierea cifrei „0".

## Ce se greșește în practică

Cea mai des întâlnită greșeală: căutarea unui cod D390 dedicat de "retur la achiziție" — nu există un asemenea cod. A doua greșeală frecventă: confundarea codului "R" din nomenclator (regim special agricultori) cu ideea de retur, din cauza literei.

## Ce face iConta.eu

Motorul de stornare al aplicației generează, pentru o factură, un document nou cu aceleași conturi și aceeași cotă ca originalul, cu suma negată, păstrând clasificarea fiscală (țara partenerului, taxarea inversă, axa intracomunitară) — astfel încât o corecție a unei operațiuni IC aterizează pe același rând (A pentru achiziții de bunuri) ca operațiunea inițială, cu bază negativă, nu pe un rând separat de "regularizări".

De reținut o limitare onestă: butonul „Stornează" din ecranul de facturi e vizibil în aplicație doar pentru facturile **emise**. Pentru o achiziție intracomunitară (factură primită de la furnizorul din UE), corecția în contabilitate pornește de la documentul de corecție primit efectiv de la furnizor (factură de stornare sau notă de credit emisă de acesta) și se înregistrează ca atare — nu printr-un buton dedicat de stornare pe factura primită din iConta. Baza și taxarea inversă se ajustează totuși după același principiu descris mai sus (aceleași conturi, sumă negată, aceeași clasificare D390/D300).

[iConta.eu](/)
