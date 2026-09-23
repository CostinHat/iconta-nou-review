---
title: "TVA la vânzarea de licențe software către firme din UE"
description: "Vânzarea unei licențe software către o firmă din alt stat membru e un serviciu B2B intracomunitar — neimpozabil în România dacă firma are cod de TVA valid, verificat în VIES; altfel, se facturează cu TVA românesc."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# TVA la vânzarea de licențe software către firme din UE

O licență software vândută unei firme din UE nu e o livrare de bun, e o prestare de serviciu — chiar dacă „produsul” pare tangibil pentru utilizator. Regimul de TVA urmează regulile serviciilor B2B, nu pe cele ale bunurilor.

## Temeiul legal

::: ghid-temei
„`valideaza_prestare_ic(cod_tva_client, cod_valid_vies)` — validează serviciul B2B intracomunitar (art. 278 alin. 2): client non-RO + cod valid VIES → neimpozabil în România, se declară D390 (S); fără cod valid → B2C, se facturează cu TVA românesc (art. 278 alin. 3).” — `core/intracomunitar.py`, dosarul F050.
:::

Dacă firma cumpărătoare are cod de TVA valid, verificat, factura se emite fără TVA românesc, cu mențiunea taxării inverse, iar operațiunea se declară în D390. Dacă firma nu are cod de TVA valid (persoană neimpozabilă), operațiunea devine B2C și se facturează cu TVA românesc.

## Ce se greșește în practică

- Se tratează vânzarea de licențe ca livrare de bunuri, cu confuzii legate de transport sau de plafonul de 10.000 euro — plafonul acela vizează exclusiv achizițiile de bunuri, nu serviciile.
- Se emite factura fără TVA fără verificare directă în VIES a codului clientului — un cod invalid sau inexistent anulează scutirea.
- Se ignoră cazul clienților persoane fizice sau firme neînregistrate în scopuri de TVA din UE, care intră la regimul B2C, cu TVA românesc pe factură.

## Ce face iConta.eu

La emiterea facturii cu un cod de TVA de prefix non-RO, sistemul verifică automat în VIES și afișează starea — valid, invalid, sau avertisment când serviciul VIES e indisponibil. Ecranul de vânzare/prestare intracomunitară cere cod TVA client și tipul operațiunii (bunuri/servicii), iar încadrarea corectă (neimpozabilă sau taxabilă) se stabilește pe baza acestei verificări.

[iConta.eu](/)
