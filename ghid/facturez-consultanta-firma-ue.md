---
title: "Cum facturez consultanță către o firmă din UE?"
description: "Serviciul de consultanță facturat unei firme înregistrate în scopuri de TVA în alt stat membru e neimpozabil în România dacă îi verifici codul TVA în VIES; fără cod valid, factura se emite cu TVA românesc."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum facturez consultanță către o firmă din UE?

Consultanța e un serviciu, nu o livrare de bunuri — regula de TVA nu urmărește transportul mărfii, ci locul unde e stabilit clientul.

## Temeiul legal

::: ghid-temei
„`valideaza_prestare_ic(cod_tva_client, cod_valid_vies)` — validează serviciul B2B intracomunitar (art. 278 alin. 2): client non-RO + cod valid VIES → neimpozabil în România; fără cod valid → B2C, se facturează cu TVA românesc (art. 278 alin. 3).” — `core/intracomunitar.py`, dosarul F050.

OPANAF 705/2020: „prestări servicii — în care se înscriu prestările intracomunitare de servicii (cod P)”. (sursă: `anaf_surse/opanaf_705_2020_d390.txt`, L664)
:::

Condiția din lege (art. 278 alin. 2) e ca locul prestării să fie la beneficiar — adică la firma din UE, nu în România. Practic, două lucruri trebuie confirmate înainte de a emite factura fără TVA: clientul e o persoană impozabilă (are cod de TVA valid, comunicat) și codul acela e verificat, nu doar primit prin e-mail.

Dacă ambele condiții sunt îndeplinite: factura se emite fără TVA românesc, cu mențiunea taxării inverse, iar operațiunea se declară în D390, cod P (prestări intracomunitare de servicii).

## Ce se greșește în practică

- Se emite factura fără TVA pe baza codului de TVA trimis de client, fără verificare directă în VIES — un cod expirat sau greșit invalidează scutirea.
- Se presupune că orice firmă din UE e automat „B2B” — dacă clientul nu are cod de TVA valid (persoană neimpozabilă sau neînregistrată), operațiunea e B2C și se facturează cu TVA românesc (art. 278 alin. 3), nu fără TVA.
- Nu se păstrează dovada verificării (data, rezultatul) — la o notificare de neconcordanță ulterioară, lipsa acestei dovezi complică răspunsul.

## Ce face iConta.eu

La emiterea unei facturi cu cod TVA de prefix non-RO, sistemul verifică automat în VIES (nu în registrul ANAF de CUI-uri) și afișează starea — valid, invalid, sau avertisment „VIES indisponibil” dacă serviciul nu răspunde. Ecranul de vânzare/prestare intracomunitară cere cod TVA client și tip de operațiune (bunuri/servicii), iar rezultatul verificării stă la baza încadrării ca neimpozabilă sau taxabilă.

[iConta.eu](/)
