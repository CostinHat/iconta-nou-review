---
title: "Cum facturez servicii contabile către o firmă din UE?"
description: "Serviciile contabile facturate unei firme înregistrate în scopuri de TVA în alt stat membru sunt neimpozabile în România dacă îi verifici codul TVA în VIES; fără cod valid, factura se emite cu TVA românesc."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Cum facturez servicii contabile către o firmă din UE?

Serviciile contabile prestate unei firme din alt stat membru urmează aceeași regulă de loc al prestării ca orice serviciu B2B — ținuta de contabilitate, întocmirea de rapoarte sau consultanța fiscală nu au un regim special, intră la fel ca orice altă prestare intracomunitară.

Dacă clientul e o firmă din UE cu cod de TVA valid, factura se emite fără TVA românesc, cu mențiunea taxării inverse, iar operațiunea se declară în D390. Dacă nu are cod valid (persoană neimpozabilă), regimul devine B2C — TVA românesc pe factură.

## Temeiul legal

::: ghid-temei
„Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. [...] (3) Locul de prestare a serviciilor către o persoană neimpozabilă este locul unde prestatorul își are stabilit sediul activității sale economice.”
— Legea nr. 227/2015 privind Codul fiscal, art. 278 alin. (2) și (3) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Dacă nu dispune de informații contrare, prestatorul poate considera că un client stabilit în alt stat membru are statutul de persoană impozabilă: a) atunci când respectivul client i-a comunicat codul său individual de înregistrare în scopuri de TVA și dacă prestatorul obține confirmarea validității codului de înregistrare respectiv, precum și a numelui și adresei aferente acestuia [...]”
— HG nr. 1/2016, Normele metodologice de aplicare a Codului fiscal, titlul VII, pct. 15 alin. (8) lit. a) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))

„Factura cuprinde în mod obligatoriu următoarele informații: [...] m) în cazul în care clientul este persoana obligată la plata TVA, mențiunea «taxare inversă»;”
— Legea nr. 227/2015 privind Codul fiscal, art. 319 alin. (20) lit. m) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

## Ce se greșește în practică

- Se emite factura fără TVA doar pe baza faptului că firma e din UE, fără verificarea codului în VIES la momentul facturării.
- Se aplică scutirea și pentru clienți persoane fizice sau firme neînregistrate în scopuri de TVA — pentru aceștia se facturează cu TVA românesc, nu fără TVA.
- Nu se păstrează dovada verificării codului — importantă dacă apare o notificare de neconcordanță între ce a declarat firma română și ce a raportat clientul în statul lui.

## Ce face iConta.eu

La emiterea facturii cu cod de TVA de prefix non-RO, sistemul verifică automat în VIES (nu în registrul ANAF de CUI-uri) și afișează starea — valid, invalid, sau avertisment „VIES indisponibil”. Ecranul de vânzare/prestare intracomunitară cere cod TVA client și tipul operațiunii, iar rezultatul verificării determină încadrarea ca neimpozabilă sau taxabilă.

[iConta.eu](/)
