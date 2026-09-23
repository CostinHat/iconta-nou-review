---
title: "Cum facturez servicii contabile către o firmă din UE?"
description: "Serviciile contabile facturate unei firme înregistrate în scopuri de TVA în alt stat membru sunt neimpozabile în România dacă îi verifici codul TVA în VIES; fără cod valid, factura se emite cu TVA românesc."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum facturez servicii contabile către o firmă din UE?

Serviciile contabile prestate unei firme din alt stat membru urmează aceeași regulă de loc al prestării ca orice serviciu B2B — ținuta de contabilitate, întocmirea de rapoarte sau consultanța fiscală nu au un regim special, intră la fel ca orice altă prestare intracomunitară.

## Temeiul legal

::: ghid-temei
„`valideaza_prestare_ic(cod_tva_client, cod_valid_vies)` — validează serviciul B2B intracomunitar (art. 278 alin. 2): client non-RO + cod valid VIES → neimpozabil în România, se declară D390 (S); fără cod valid → B2C, se facturează cu TVA românesc (art. 278 alin. 3).” — `core/intracomunitar.py`, dosarul F050.
:::

Dacă clientul e o firmă din UE cu cod de TVA valid, factura se emite fără TVA românesc, cu mențiunea taxării inverse, iar operațiunea se declară în D390. Dacă nu are cod valid (persoană neimpozabilă), regimul devine B2C — TVA românesc pe factură.

## Ce se greșește în practică

- Se emite factura fără TVA doar pe baza faptului că firma e din UE, fără verificarea codului în VIES la momentul facturării.
- Se aplică scutirea și pentru clienți persoane fizice sau firme neînregistrate în scopuri de TVA — pentru aceștia se facturează cu TVA românesc, nu fără TVA.
- Nu se păstrează dovada verificării codului — importantă dacă apare o notificare de neconcordanță între ce a declarat firma română și ce a raportat clientul în statul lui.

## Ce face iConta.eu

La emiterea facturii cu cod de TVA de prefix non-RO, sistemul verifică automat în VIES (nu în registrul ANAF de CUI-uri) și afișează starea — valid, invalid, sau avertisment „VIES indisponibil”. Ecranul de vânzare/prestare intracomunitară cere cod TVA client și tipul operațiunii, iar rezultatul verificării determină încadrarea ca neimpozabilă sau taxabilă.

[iConta.eu](/)
