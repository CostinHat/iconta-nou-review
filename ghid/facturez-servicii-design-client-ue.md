---
title: "Cum facturez servicii de design către un client din UE?"
description: "Regula de TVA pentru un serviciu B2B prestat unui client dintr-un alt stat membru și cum se verifică dreptul la neimpozitare în România."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum facturez servicii de design către un client din UE?

Serviciile de design prestate unei firme dintr-un alt stat membru urmează regula generală a serviciilor B2B intracomunitare — nu există o regulă separată pentru „design" ca tip de serviciu. Ce contează e dacă beneficiarul e o persoană impozabilă cu cod de TVA valid în alt stat membru, nu natura creativă a serviciului prestat.

## Temeiul legal

::: ghid-temei
„Taxa este datorată de orice persoană impozabilă [...] care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) şi care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României [...]"
— Codul fiscal (Legea 227/2015), art. 307 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Regula generală de la art. 278 alin. (2) CF stabilește locul prestării serviciilor B2B la sediul beneficiarului — pentru un serviciu de design prestat de o firmă română unei firme dintr-un alt stat membru, locul prestării e la beneficiar, nu în România.
- Consecința: operațiunea e **neimpozabilă în România**, cu condiția ca beneficiarul să aibă un cod de TVA valid, verificat prin VIES, într-un alt stat membru — atunci taxa devine datorată de beneficiar, în statul lui, prin taxare inversă.
- Dacă beneficiarul **nu** are un cod de TVA valid (persoană fizică sau firmă neînregistrată în scopuri de TVA), operațiunea devine B2C — se facturează cu TVA românesc, potrivit regulii generale de la art. 278 alin. (3) CF.
- Factura emisă pentru un serviciu B2B intracomunitar tratat ca neimpozabil trebuie să poarte mențiunea obligatorie „taxare inversă" (art. 319 alin. (20) lit. m) CF), pentru că beneficiarul e persoana obligată la plata TVA.

## Ce se greșește în practică

- Se caută o regulă specifică pentru „servicii de design" sau alte servicii creative/digitale — la nivelul Codului fiscal nu există o distincție pe tipul concret de serviciu; regula e generică pentru toate serviciile B2B care intră sub art. 278 alin. (2).
- Se facturează cu TVA românesc din prudență, fără să se verifice întâi codul de TVA al clientului în VIES — dacă acesta e valid, factura corectă e fără TVA românesc, cu mențiunea de taxare inversă.
- Se presupune că simpla existență a unui cod de TVA pe factura clientului e suficientă, fără verificarea lui efectivă în VIES — un cod introdus greșit sau expirat nu îndeplinește condiția scutirii.

## Ce face iConta.eu

Titlul acestui ghid seamănă cu funcționalitatea de previzualizare a portalului de client din iConta.eu (butonul „Previzualizează portalul", folosit de contabil din cabinet pentru a vedea, read-only, ce vede clientul lui în portal) — dar **nu are nicio legătură** cu facturarea serviciilor intracomunitare. Funcționalitatea reală relevantă pentru acest subiect e motorul de operațiuni intracomunitare al aplicației: la facturarea unui serviciu către un client din UE, iConta separă codul de TVA în țară și număr, interoghează VIES pentru validitate, și decide automat tratamentul — neimpozabil în România (dacă VIES confirmă un cod valid) sau TVA românesc, ca facturare B2C (dacă nu). Această clasificare alimentează apoi declararea corectă în D390 (cod P, prestare intracomunitară de servicii).

[iConta.eu](/)
