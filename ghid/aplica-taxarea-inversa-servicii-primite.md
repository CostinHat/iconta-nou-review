---
title: "Când se aplică taxarea inversă la servicii primite din UE?"
description: "Condițiile aplicării taxării inverse (art. 278 alin. 2, art. 308-309) la servicii primite de la un furnizor cu cod de TVA valid în alt stat membru UE."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când se aplică taxarea inversă la servicii primite din UE?

Taxarea inversă la servicii primite din UE nu e o opțiune contabilă, ci consecința directă a unei reguli de TVA: locul prestării serviciului B2B e considerat la beneficiar.

## Temeiul legal

::: ghid-temei
CF art. 278 alin. (2): „Locul prestării serviciilor B2B = locul beneficiarului (bază pentru neimpozabilitate în RO + declarare D390 cod S).” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L17303-17420)

CF art. 307 alin. (2): „Taxa este datorată de orice persoană impozabilă… care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României…” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L19334-19342)

HG 1/2016, norme la CF art. 331, pct. 109 alin. (1): „beneficiarul înregistrează… suma taxei aferente în următoarea formulă contabilă: 4426 = 4427. Prevederile acestui alineat sunt valabile pentru orice alte situații în care se aplică taxarea inversă.” (sursă: `anaf_surse/hg_1_2016_norme_cod_fiscal.txt`, L242)
:::

Taxarea inversă se aplică atunci când: (1) firma din România e beneficiarul unui serviciu B2B (persoană impozabilă, indiferent dacă e plătitoare de TVA „normal” sau înregistrată special conform art. 317), și (2) furnizorul are cod de TVA valid, verificabil în VIES, într-un alt stat membru UE. În acest caz, furnizorul facturează fără TVA, iar beneficiarul din România e cel obligat la plata taxei (art. 307 alin. (2)) — o calculează el însuși, prin taxare inversă, și o înregistrează contabil prin formula 4426 = 4427.

Fără cod de TVA valid al furnizorului în VIES, condiția nu e îndeplinită — operațiunea nu se tratează ca achiziție intracomunitară de servicii.

## Ce se greșește în practică

- Se aplică taxare inversă doar pentru că factura „nu are TVA pe ea”, fără verificarea efectivă a codului de TVA al furnizorului în VIES.
- Se stabilește cota de TVA folosind o valoare „din memorie” sau învechită, în loc să fie declarată explicit pentru fiecare operațiune — o cotă scrisă „fix” se poate rupe tăcut de lege la prima schimbare de cotă.
- Se omite declararea D390 (cod S) pentru achiziția de servicii, deși taxarea inversă a fost calculată corect.

## Ce face iConta.eu

Formularul de achiziție intracomunitară (`achizitie_ic`), tip „servicii”, din categoria „Extern”, permite înregistrarea achiziției cu data, valoarea în RON, codul de TVA al furnizorului (verificabil în VIES), numărul facturii și cota de TVA aplicabilă — motorul intern cere cota declarată explicit la fiecare operațiune, fără o valoare implicită fixă în cod.

Aplicația calculează TVA prin taxare inversă, folosind rotunjire `Decimal` cu regula standard de rotunjire, generează formula contabilă 4426 = 4427 și clasifică automat operațiunea pentru D390, cod S.

[iConta.eu](/)
