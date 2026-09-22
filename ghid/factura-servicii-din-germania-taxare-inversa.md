---
title: Factura de servicii primită din Germania — taxare inversă
description: Un serviciu B2B primit de la un furnizor din Germania are locul prestării în România (art. 278 alin. (2) Cod fiscal), iar TVA e datorată de beneficiarul român prin taxare inversă, conform art. 307 alin. (2) Cod fiscal.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se înregistrează o factură de servicii primită din Germania?

Când o firmă românească plătibilă TVA primește o factură de consultanță, mentenanță software sau alt serviciu de la un furnizor german, factura vine fără TVA german — dar asta nu înseamnă că operațiunea e scutită. Locul prestării se mută la sediul beneficiarului, adică în România, iar taxa se autoimpune aici, prin taxare inversă. Diferența față de o achiziție de bunuri e mecanismul de raportare și temeiul legal exact, des confundat în practică.

## Temeiul legal

::: ghid-temei
**Art. 278 alin. (2) Cod fiscal** — locul prestării pentru servicii B2B: *„Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. Dacă serviciile sunt furnizate către un sediu fix al persoanei impozabile, aflat în alt loc decât cel în care persoana își are sediul activității sale economice, locul de prestare a serviciilor este locul unde se află respectivul sediu fix al persoanei care primește serviciile. În absența unui astfel de loc sau sediu fix, locul de prestare a serviciilor este locul unde persoana impozabilă care primește aceste servicii își are domiciliul stabil sau reședința obișnuită."*

**Art. 307 alin. (2) Cod fiscal** — cine datorează taxa pentru servicii primite: *„Taxa este datorată de orice persoană impozabilă, inclusiv de către persoana juridică neimpozabilă înregistrată în scopuri de TVA conform art. 316 sau 317, care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României..."*

**Norme HG 1/2016, pct. 109 alin. (1)** — formula contabilă: *„Din punct de vedere contabil, beneficiarul înregistrează în cursul perioadei fiscale în care taxa este exigibilă suma taxei aferente în următoarea formulă contabilă: 4426 = 4427. Prevederile acestui alineat sunt valabile pentru orice alte situații în care se aplică taxarea inversă."*
:::

## Ce se înregistrează și cu ce temei

Pentru că furnizorul german nu e stabilit în România și serviciul are locul prestării aici (sediul beneficiarului), temeiul exact al taxării inverse la servicii **e art. 307 alin. (2)**, nu art. 308 — acesta din urmă privește achizițiile de bunuri (AIC), un mecanism paralel, dar cu articol propriu. Cele două se confundă des pentru că duc la aceeași formulă contabilă și aceeași logică de „autoimpunere", dar temeiul e diferit după cum obiectul e bun sau serviciu.

Înregistrarea are tot două note contabile:

`628/611/... = 401` — cheltuiala cu serviciul, la valoarea facturii (fără TVA, așa cum a facturat furnizorul german).

`4426 = 4427` — TVA autoimpusă, calculată `bază × cotă / 100`, rotunjit aritmetic la 2 zecimale.

## Un exemplu

::: ghid-exemplu
O firmă românească primește o factură de mentenanță software de la un furnizor din Germania, valoare **3.500 lei**, cotă TVA **21%**.

- **Cheltuiala**: `628 = 401` cu **3.500 lei**
- **TVA autoimpusă**: `4426 = 4427` cu 3.500 × 21 / 100 = **735 lei**

Firma nu plătește TVA german și nu plătește nimic în plus furnizorului — factura de 3.500 lei se achită integral. Cei 735 lei de TVA se evidențiază simultan la deduceri și la colectate.
:::

## Ce se greșește în practică

- **Se caută „scutire de TVA" pe factura de servicii externe**, pentru că furnizorul nu a facturat TVA — de fapt operațiunea e taxabilă în România, doar că prin taxare inversă, nu prin plată la furnizor.
- **Se confundă temeiul cu cel de la achiziția de bunuri.** Formula contabilă (4426 = 4427) e identică, dar temeiul pentru servicii primite e locul prestării (art. 278 alin. (2)) coroborat cu obligația de plată a beneficiarului (art. 307 alin. (2)), nu articolul care reglementează achizițiile intracomunitare de bunuri.
- **Se omite raportarea în declarația recapitulativă** pentru servicii intracomunitare primite, tratând operațiunea doar ca o cheltuială internă obișnuită.

## Ce face iConta.eu

Codul de TVA al furnizorului e analizat automat — prefixul de țară e verificat contra listei celor 27 de state membre UE plus `XI`; operațiunea e tratată ca prestare intracomunitară doar dacă țara codului nu e România și codul e valid. TVA la taxare inversă se calculează cu `TVA = bază × cotă / 100`, rotunjit aritmetic (`ROUND_HALF_UP`) la 2 zecimale, cu cota transmisă explicit la fiecare calcul, fără valoare implicită.

[iConta.eu](/)
