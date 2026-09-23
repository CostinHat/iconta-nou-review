---
title: "Închirierea de echipamente către o firmă din UE: TVA"
description: "Închirierea de echipamente către o firmă din alt stat membru e un serviciu B2B — neimpozabil în România dacă firma are cod de TVA valid, verificat în VIES; altfel, se facturează cu TVA românesc."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Închirierea de echipamente către o firmă din UE: TVA

Închirierea de echipamente (utilaje, aparatură, alte bunuri mobile) e, din perspectiva TVA, o prestare de servicii, nu o livrare de bunuri — chiar dacă bunul fizic traversează o frontieră pentru a ajunge la chiriaș.

## Temeiul legal

::: ghid-temei
„`valideaza_prestare_ic(cod_tva_client, cod_valid_vies)` — validează serviciul B2B intracomunitar (art. 278 alin. 2): client non-RO + cod valid VIES → neimpozabil în România, se declară D390 (S); fără cod valid → B2C, se facturează cu TVA românesc (art. 278 alin. 3).” — `core/intracomunitar.py`, dosarul F050.
:::

Ca la orice serviciu B2B intracomunitar: dacă firma chiriașă din UE are cod de TVA valid, verificat, factura de închiriere se emite fără TVA românesc, cu mențiunea taxării inverse, iar operațiunea se declară în D390. Fără cod valid, operațiunea devine B2C, cu TVA românesc.

## Ce se greșește în practică

- Se tratează închirierea ca livrare de bun, cu așteptări legate de transport și de documente specifice AIC — regimul corect e cel al serviciilor, nu al bunurilor.
- Se emite factura fără TVA fără verificare directă a codului clientului în VIES la momentul facturării.
- Se ignoră situația chiriașilor persoane fizice sau firme fără cod de TVA valid — pentru aceștia se aplică TVA românesc, regim B2C.

## Ce face iConta.eu

La emiterea facturii cu cod de TVA de prefix non-RO, sistemul verifică automat în VIES și afișează starea — valid, invalid, sau avertisment când VIES e indisponibil. Ecranul de vânzare/prestare intracomunitară cere cod TVA client și tipul operațiunii (bunuri/servicii), iar rezultatul verificării determină încadrarea.

[iConta.eu](/)
