---
title: Când emit factura fără TVA pentru un client din UE?
description: Fără TVA românesc doar dacă operațiunea se încadrează la livrare intracomunitară scutită (cod TVA valid al clientului + dovada transportului) sau la un serviciu B2B cu locul prestării la beneficiar. Altfel, se facturează cu TVA din România.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Când emit factura fără TVA pentru un client din UE?

O factură fără TVA către un client dintr-un alt stat membru nu e opțională — se aplică doar dacă operațiunea se încadrează strict în una din două categorii: livrare intracomunitară de bunuri scutită sau serviciu B2B al cărui loc de prestare e la sediul beneficiarului. În orice alt caz, factura se emite cu TVA românesc.

## Temeiul legal

::: ghid-temei
Livrarea intracomunitară de bunuri e scutită cu drept de deducere conform **art. 294 alin. (2) lit. a) Cod fiscal**, condiționat de cod TVA valid al cumpărătorului comunicat furnizorului și dovada transportului bunurilor în alt stat membru.

Pentru servicii, locul prestării către o persoană impozabilă (B2B) e la sediul beneficiarului — **art. 278 alin. (2) Cod fiscal** — deci neimpozabil în România dacă beneficiarul are un cod de TVA valid într-un alt stat membru.
:::

Pentru **bunuri**: scutirea (art. 294 alin. 2 lit. a) se aplică doar dacă sunt îndeplinite cumulativ două condiții — clientul are un cod de TVA valid, verificabil în VIES, și există dovada transportului bunurilor în alt stat membru. Lipsa oricăreia dintre ele înseamnă că factura trebuie emisă cu TVA românesc, nu scutită.

Pentru **servicii B2B**: regula de la art. 278 alin. (2) mută locul prestării la sediul beneficiarului, deci operațiunea e neimpozabilă în România — dar tot condiționat de un cod de TVA valid al clientului. Dacă clientul nu are (sau nu comunică) un cod de TVA valid, operațiunea devine B2C, iar factura se emite cu TVA românesc, conform art. 278 alin. (3) CF.

## Ce se greșește în practică

Cea mai frecventă greșeală: emiterea facturii fără TVA doar pe baza faptului că partenerul e "din UE", fără verificarea efectivă a codului de TVA în VIES la momentul facturării. Un cod de TVA valid ieri poate fi invalid azi (radiere, suspendare) — verificarea trebuie făcută la fiecare emitere, nu presupusă din tranzacții anterioare.

## Ce face iConta.eu

La emiterea unei facturi cu un cod de TVA de prefix non-RO, aplicația verifică automat validitatea în VIES (nu doar în registrul de CUI-uri ANAF) și afișează starea — valid, invalid sau "VIES indisponibil" dacă serviciul oficial nu răspunde. Pentru achiziții/livrări intracomunitare, ecranele dedicate din secțiunea Operațiuni speciale despart codul de TVA în țară și număr, validează prefixul contra listei statelor membre (inclusiv XI pentru Irlanda de Nord) și cer explicit dovada transportului pentru validarea scutirii de livrare (LIC). Pentru servicii B2B, aceeași verificare VIES decide dacă operațiunea e neimpozabilă în România sau trebuie facturată cu TVA românesc, ca la un client intern.

[iConta.eu](/)
