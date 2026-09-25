---
title: "Cum închid un SRL plătitor de impozit pe profit?"
description: "Etapele fiscale ale lichidării unui SRL plătitor de impozit pe profit: valorificarea activelor, impozitul pe câștigul din lichidare și partajul final."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum închid un SRL plătitor de impozit pe profit?

Lichidarea unui SRL nu înseamnă doar radierea de la Registrul Comerțului — presupune, în ordine, valorificarea activelor, stingerea datoriilor, stabilirea rezultatului lichidării și, la partaj, impozitarea câștigului cuvenit asociaților persoane fizice cu o cotă distinctă de cea a dividendelor.

## Temeiul legal

::: ghid-temei
„Venitul impozabil obținut din lichidarea unei persoane juridice de către acționari/asociați persoane fizice sau din reducerea capitalului social, potrivit legii, care nu reprezintă distribuții în bani sau în natură ca urmare a restituirii cotei-părți din aporturi se impun cu o cotă de 10%, impozitul fiind final. Obligația calculării, reținerii și plății impozitului revine persoanei juridice."
— Legea 227/2015 (Codul fiscal), art. 97 alin. (5) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Etapele fiscale pe care le presupune, în esență, o lichidare:

- Valorificarea activelor rămase (vânzare sau descărcare din gestiune), cu TVA colectată acolo unde operațiunea e taxabilă.
- Stabilirea rezultatului lichidării — diferența dintre activele rămase după plata datoriilor și capitalul social vărsat.
- Partajul: restituirea capitalului social către asociați este **neimpozabilă**, dar rezervele și profiturile nedistribuite reprezintă un câștig impozabil cu **cota fixă de 10%** (art. 97 alin. 5) — distinctă de cota dividendelor (16% începând cu 01.01.2026, conform art. 97 alin. 7).

## Ce se greșește în practică

- Se confundă cota de impozitare a câștigului din lichidare cu cea a dividendelor — sunt regimuri diferite, cu articole diferite (alin. 5, respectiv alin. 7 al art. 97), și rata e alta.
- Se distribuie activele către asociați înainte de închiderea completă a obligațiilor fiscale curente (TVA, impozit pe profit pe ultima perioadă) — ordinea corectă e: se sting datoriile, apoi se partajează ce rămâne.
- Se ignoră impozitarea rezervei legale deduse fiscal la constituire — la lichidare, aceasta se impozitează atât la nivelul firmei (16% impozit pe profit), cât și, ca parte din câștig, la asociat.

## Ce face iConta.eu

iConta.eu are un modul de lichidare (`core/lichidare.py`) care generează notele contabile pentru valorificarea activelor (vânzare cu TVA, descărcare din gestiune) și calculează partajul final — separă corect capitalul social (neimpozabil) de rezerve și profituri (impozabile cu cota fixă de 10%, conform art. 97 alin. 5), aplicând cota valabilă la data operațiunii. Aplicația nu depune însă cererea de radiere la Registrul Comerțului și nu automatizează declarațiile fiscale finale (ultimul D101/D100) — acestea rămân proceduri separate, făcute de contabil.

[iConta.eu](/)
