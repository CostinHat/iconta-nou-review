---
title: "Închirierea de echipamente către o firmă din UE: TVA"
description: "Închirierea de echipamente către o firmă din alt stat membru e un serviciu B2B — neimpozabil în România dacă firma are cod de TVA valid, verificat în VIES; altfel, se facturează cu TVA românesc."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Închirierea de echipamente către o firmă din UE: TVA

Închirierea de echipamente (utilaje, aparatură, alte bunuri mobile) e, din perspectiva TVA, o prestare de servicii, nu o livrare de bunuri — chiar dacă bunul fizic traversează o frontieră pentru a ajunge la chiriaș.

Ca la orice serviciu B2B intracomunitar: dacă firma chiriașă din UE are cod de TVA valid, verificat, factura de închiriere se emite fără TVA românesc, cu mențiunea taxării inverse, iar operațiunea se declară în D390. Fără cod valid, operațiunea devine B2C, cu TVA românesc.

## Temeiul legal

::: ghid-temei
„Prestările de servicii cuprind operațiuni cum sunt: a) închirierea de bunuri sau transmiterea folosinței bunurilor în cadrul unui contract de leasing;”
— Legea nr. 227/2015 privind Codul fiscal, art. 271 alin. (3) lit. a) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. [...] (3) Locul de prestare a serviciilor către o persoană neimpozabilă este locul unde prestatorul își are stabilit sediul activității sale economice.”
— Legea nr. 227/2015 privind Codul fiscal, art. 278 alin. (2) și (3) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Dacă nu dispune de informații contrare, prestatorul poate considera că un client stabilit în alt stat membru are statutul de persoană impozabilă: a) atunci când respectivul client i-a comunicat codul său individual de înregistrare în scopuri de TVA și dacă prestatorul obține confirmarea validității codului de înregistrare respectiv, precum și a numelui și adresei aferente acestuia [...]”
— HG nr. 1/2016, Normele metodologice de aplicare a Codului fiscal, titlul VII, pct. 15 alin. (8) lit. a) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))
:::

## Ce se greșește în practică

- Se tratează închirierea ca livrare de bun, cu așteptări legate de transport și de documente specifice AIC — regimul corect e cel al serviciilor, nu al bunurilor.
- Se emite factura fără TVA fără verificare directă a codului clientului în VIES la momentul facturării.
- Se ignoră situația chiriașilor persoane fizice sau firme fără cod de TVA valid — pentru aceștia se aplică TVA românesc, regim B2C.

## Ce face iConta.eu

La emiterea facturii cu cod de TVA de prefix non-RO, sistemul verifică automat în VIES și afișează starea — valid, invalid, sau avertisment când VIES e indisponibil. Ecranul de vânzare/prestare intracomunitară cere cod TVA client și tipul operațiunii (bunuri/servicii), iar rezultatul verificării determină încadrarea.

[iConta.eu](/)
