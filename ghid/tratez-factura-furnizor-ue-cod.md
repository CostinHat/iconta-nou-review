---
title: "Cum tratez factura unui furnizor UE cu cod TVA de România?"
description: "Dacă furnizorul din UE facturează bunuri cu un cod de TVA de România, operațiunea nu e achiziție intracomunitară — se tratează ca achiziție internă. La serviciile cu locul prestării în România prestate de o firmă nestabilită aici, taxa o datorează beneficiarul chiar dacă prestatorul are cod de TVA românesc (Codul fiscal, art. 307 alin. (2))."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Cum tratez factura unui furnizor UE cu cod TVA de România?

Un furnizor dintr-un alt stat membru poate fi, în același timp, înregistrat în scopuri de TVA în România (sediu fix, înregistrare directă). Dacă factura e emisă cu codul de TVA românesc, nu cu cel din statul membru de origine, operațiunea nu urmează regimul de achiziție intracomunitară.

Motorul de operațiuni intracomunitare lucrează cu prefixul de țară al codului de TVA de pe factură. Dacă acel cod are prefixul RO, furnizorul acționează, pentru operațiunea respectivă, ca persoană înregistrată în România — nu se mai verifică validitatea printr-un cod străin în VIES, iar operațiunea nu se încadrează ca achiziție intracomunitară de bunuri conform art. 268.

La servicii regula e alta. Pentru serviciile cu locul prestării în România conform art. 278 alin. (2), prestate de o persoană impozabilă care nu este stabilită în România (și nici nu e considerată stabilită pentru acele prestări), taxa o datorează beneficiarul, prin taxare inversă, chiar dacă prestatorul este înregistrat în scopuri de TVA în România conform art. 316 alin. (4) sau (6) — art. 307 alin. (2). Codul de TVA românesc de pe factură nu mută, singur, obligația de plată la prestator. Regimul intern, cu TVA colectat de furnizor, se aplică serviciilor doar dacă prestatorul este stabilit în România pentru acea prestare (de exemplu, printr-un sediu fix care participă la prestare).

## Temeiul legal

::: ghid-temei
„(2) Taxa este datorată de orice persoană impozabilă, inclusiv de către persoana juridică neimpozabilă înregistrată în scopuri de TVA conform art. 316 sau 317 , care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României sau nu este considerată a fi stabilită pentru respectivele prestări de servicii pe teritoriul României conform prevederilor art. 266 alin. (2) și care nu aplică regimul pentru micile întreprinderi în România prevăzut la art. 310^2 , chiar dacă este înregistrată în România conform art. 316 alin. (4) sau (6) .”
— Codul fiscal (Legea nr. 227/2015), art. 307 alin. (2) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

## Ce se greșește în practică

- Se așteaptă automat factură fără TVA de la orice furnizor cu sediu în UE, ignorând faptul că, dacă a facturat bunuri cu cod TVA de România, tranzacția e supusă regimului intern.
- Se declară în D390 o operațiune facturată de fapt cu cod TVA românesc — D390 e declarația recapitulativă a operațiunilor intracomunitare, nu a facturilor de la furnizori străini în general.
- Se aplică taxare inversă pe o factură de bunuri care conține deja TVA colectat de furnizor cu codul lui românesc — dublarea taxei prin taxare inversă peste TVA deja facturat.
- Invers, la servicii: se acceptă ca achiziție internă, cu TVA colectat de furnizor, un serviciu prestat de o firmă nestabilită în România doar pentru că factura poartă cod TVA de România — taxa o datorează beneficiarul, prin taxare inversă (art. 307 alin. (2)).

## Ce face iConta.eu

Verificarea automată la emitere/introducere se face pe baza prefixului codului de TVA: dacă prefixul e RO, operațiunea nu intră în motorul de operațiuni intracomunitare (care validează prefixul contra listei celor 27 de state membre plus `XI`). Practic, o factură de bunuri cu cod TVA românesc se introduce ca achiziție internă obișnuită, cu TVA-ul de pe factură, nu pe ecranul de achiziție intracomunitară. Aplicația decide doar după prefixul codului, nu după locul în care este stabilit prestatorul: pentru serviciile de la un prestator nestabilit în România, încadrarea la taxare inversă potrivit art. 307 alin. (2) rămâne în sarcina contabilului.

[iConta.eu](/)
