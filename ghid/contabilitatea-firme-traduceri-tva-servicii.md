---
title: "Contabilitatea unei firme de traduceri: TVA la servicii UE"
description: "Serviciile de traducere facturate unor firme din UE sunt neimpozabile în România dacă firma-client are cod de TVA valid, verificat în VIES; altfel, se facturează cu TVA românesc, regim B2C."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Contabilitatea unei firme de traduceri: TVA la servicii UE

O firmă de traduceri care lucrează cu clienți din UE nu are un regim de TVA diferit de orice altă firmă de servicii — testul e același: locul beneficiarului și validitatea codului lui de TVA.

## Temeiul legal

::: ghid-temei
„`valideaza_prestare_ic(cod_tva_client, cod_valid_vies)` — validează serviciul B2B intracomunitar (art. 278 alin. 2): client non-RO + cod valid VIES → neimpozabil în România, se declară D390 (S); fără cod valid → B2C, se facturează cu TVA românesc (art. 278 alin. 3).” — `core/intracomunitar.py`, dosarul F050.
:::

Dacă firma-client din UE are cod de TVA valid, verificat, factura pentru serviciul de traducere se emite fără TVA românesc, cu mențiunea taxării inverse, iar operațiunea se declară în D390. Fără cod valid — client persoană fizică sau firmă neînregistrată — se aplică regimul B2C, cu TVA românesc.

## Ce se greșește în practică

- Se emite factura fără TVA doar pentru că firma are sediul în UE, fără verificarea efectivă a codului în VIES.
- Se tratează diferit clienții „mari” față de cei ocazionali — regula e aceeași indiferent de dimensiunea contractului: cod de TVA valid, verificat, sau TVA românesc.
- Se omite declararea în D390 pentru operațiuni mici sau punctuale — obligația nu depinde de frecvență sau valoare.

## Ce face iConta.eu

La emiterea facturii cu cod de TVA de prefix non-RO, sistemul verifică automat în VIES (nu în registrul ANAF de CUI-uri) și afișează starea codului. Ecranul de vânzare/prestare intracomunitară cere cod TVA client și tipul operațiunii, iar rezultatul verificării stă la baza încadrării ca neimpozabilă sau taxabilă.

[iConta.eu](/)
