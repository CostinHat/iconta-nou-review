---
title: "Contabilitatea unei firme de traduceri: TVA la servicii UE"
description: "Serviciile de traducere facturate unor firme din UE sunt neimpozabile în România dacă firma-client are cod de TVA valid, verificat în VIES; altfel, se facturează cu TVA românesc, regim B2C."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Contabilitatea unei firme de traduceri: TVA la servicii UE

O firmă de traduceri care lucrează cu clienți din UE nu are un regim de TVA diferit de orice altă firmă de servicii — testul e același: locul beneficiarului și validitatea codului lui de TVA.

## Temeiul legal

::: ghid-temei
„Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice.”
— Codul fiscal (Legea 227/2015), art. 278 alin. (2) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Dacă nu dispune de informații contrare, prestatorul poate considera că un client stabilit în alt stat membru are statutul de persoană impozabilă: a) atunci când respectivul client i-a comunicat codul său individual de înregistrare în scopuri de TVA și dacă prestatorul obține confirmarea validității codului de înregistrare respectiv, precum și a numelui și adresei aferente acestuia [...]”
— HG 1/2016 (Normele Codului fiscal), titlul VII, pct. 15 alin. (8) lit. a) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))

„Orice persoană impozabilă înregistrată în scopuri de TVA conform art. 316 sau 317 trebuie să întocmească și să depună la organele fiscale competente o declarație recapitulativă în care menționează: [...] c) prestările de servicii prevăzute la art. 278 alin. (2) efectuate în beneficiul unor persoane impozabile nestabilite în România, dar stabilite în Uniunea Europeană [...]”
— Codul fiscal (Legea 227/2015), art. 325 alin. (1) lit. c) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Dacă firma-client din UE are cod de TVA valid, verificat, factura pentru serviciul de traducere se emite fără TVA românesc, cu mențiunea taxării inverse, iar operațiunea se declară în D390. Fără cod valid — client persoană fizică sau firmă neînregistrată — se aplică regimul B2C, cu TVA românesc.

## Ce se greșește în practică

- Se emite factura fără TVA doar pentru că firma are sediul în UE, fără verificarea efectivă a codului în VIES.
- Se tratează diferit clienții „mari” față de cei ocazionali — regula e aceeași indiferent de dimensiunea contractului: cod de TVA valid, verificat, sau TVA românesc.
- Se omite declararea în D390 pentru operațiuni mici sau punctuale — obligația nu depinde de frecvență sau valoare.

## Ce face iConta.eu

La emiterea facturii cu cod de TVA de prefix non-RO, sistemul verifică automat în VIES (nu în registrul ANAF de CUI-uri) și afișează starea codului. Ecranul de vânzare/prestare intracomunitară cere cod TVA client și tipul operațiunii, iar rezultatul verificării stă la baza încadrării ca neimpozabilă sau taxabilă.

[iConta.eu](/)
