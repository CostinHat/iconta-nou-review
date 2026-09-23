---
title: "Cum facturez servicii de programare către o firmă din UE?"
description: "Un serviciu de programare facturat unei firme înregistrate în scopuri de TVA în alt stat membru e neimpozabil în România dacă îi verifici codul TVA în VIES; fără cod valid, factura se emite cu TVA românesc."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum facturez servicii de programare către o firmă din UE?

Un serviciu de programare (dezvoltare software, mentenanță, integrare) urmează aceeași regulă de loc al prestării ca orice alt serviciu B2B intracomunitar — nu contează ce anume livrezi, ci unde e stabilit clientul și dacă are cod de TVA valid.

## Temeiul legal

::: ghid-temei
„`valideaza_prestare_ic(cod_tva_client, cod_valid_vies)` — validează serviciul B2B intracomunitar (art. 278 alin. 2): client non-RO + cod valid VIES → neimpozabil în România; fără cod valid → B2C, se facturează cu TVA românesc (art. 278 alin. 3).” — `core/intracomunitar.py`, dosarul F050.

OPANAF 705/2020: „prestări servicii — în care se înscriu prestările intracomunitare de servicii (cod P)”. (sursă: `anaf_surse/opanaf_705_2020_d390.txt`, L664)
:::

Locul prestării e la beneficiar (art. 278 alin. 2), deci factura se emite fără TVA românesc dacă firma din UE are cod de TVA valid, verificat. Operațiunea se declară în D390, cod P (prestări intracomunitare de servicii), nu în decontul de TVA ca operațiune internă.

## Ce se greșește în practică

- Se tratează serviciul de programare ca „export de servicii, deci automat fără TVA”, fără verificarea efectivă a codului clientului în VIES.
- Se confundă client persoană impozabilă cu simpla existență a unui contract sau a unei adrese în UE — fără cod de TVA valid, operațiunea e B2C și se facturează cu TVA românesc.
- Se omite declararea în D390, pe motiv că „nu e o marfă, e un serviciu” — serviciile B2B intracomunitare intră în D390 la fel ca livrările de bunuri, doar cu alt cod de operațiune.

## Ce face iConta.eu

La emiterea facturii, dacă prefixul codului de TVA al clientului e non-RO, sistemul verifică automat în VIES (nu în registrul ANAF de CUI-uri) și afișează rezultatul — valid, invalid, sau avertisment când VIES e indisponibil. Ecranul de vânzare/prestare intracomunitară cere cod TVA client și tipul operațiunii (bunuri/servicii), iar rezultatul verificării stă la baza încadrării.

[iConta.eu](/)
