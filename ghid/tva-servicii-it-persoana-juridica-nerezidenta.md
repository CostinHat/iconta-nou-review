---
title: Tratamentul fiscal al serviciilor IT cumpărate de la o persoană juridică nerezidentă
description: Un serviciu IT cumpărat de la o firmă nestabilită în România are locul prestării la sediul beneficiarului (art. 278 alin. (2) Cod fiscal), iar TVA e datorată de beneficiar prin taxare inversă, conform art. 307 alin. (2) Cod fiscal.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se tratează fiscal serviciile IT cumpărate de la o persoană juridică nerezidentă?

Găzduire cloud, licențe software, dezvoltare sau mentenanță cumpărate de la o firmă care nu e stabilită în România urmează aceeași logică indiferent dacă furnizorul e dintr-un alt stat membru UE sau din afara UE: locul prestării se mută la sediul tău, beneficiarul, iar TVA se autoimpune aici. Diferența practică între furnizor UE și furnizor din afara UE ține mai ales de raportare (declarația recapitulativă D390 vizează în special operațiunile intracomunitare), nu de principiul de bază al locului prestării.

## Temeiul legal

::: ghid-temei
**Art. 278 alin. (2) Cod fiscal** — locul prestării pentru servicii B2B: *„Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. Dacă serviciile sunt furnizate către un sediu fix al persoanei impozabile, aflat în alt loc decât cel în care persoana își are sediul activității sale economice, locul de prestare a serviciilor este locul unde se află respectivul sediu fix al persoanei care primește serviciile. În absența unui astfel de loc sau sediu fix, locul de prestare a serviciilor este locul unde persoana impozabilă care primește aceste servicii își are domiciliul stabil sau reședința obișnuită."*

**Art. 307 alin. (2) Cod fiscal** — cine datorează taxa pentru servicii primite de la un furnizor nestabilit în România: *„Taxa este datorată de orice persoană impozabilă, inclusiv de către persoana juridică neimpozabilă înregistrată în scopuri de TVA conform art. 316 sau 317, care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României..."*
:::

## Temeiul exact — 307(2), nu 308-309

Textul art. 307 alin. (2) e formulat general: se aplică oricărui furnizor „care nu este stabilit pe teritoriul României" — indiferent dacă e din alt stat membru UE sau dintr-un stat terț. Acesta e temeiul corect pentru servicii primite, deci nu se confundă cu:

- **art. 308**, care privește achiziția intracomunitară **de bunuri**, nu de servicii;
- **art. 309**, care privește **importul de bunuri**, un mecanism complet diferit (taxă plătită sau garantată în vamă de importator), nicidecum servicii primite de la un nerezident.

Confuzia dintre 307, 308 și 309 apare des în documentația internă tocmai pentru că toate trei ating cazuri de „taxă datorată de altcineva decât furnizorul stabilit în România" — dar fiecare articol acoperă un obiect diferit (servicii, bunuri intracomunitare, respectiv import), iar citarea greșită nu schimbă formula contabilă, dar poate induce în eroare la o verificare ulterioară a temeiului.

Înregistrarea contabilă rămâne aceeași indiferent de proveniența exactă a furnizorului (UE sau extra-UE):

`628/611/... = 401` — cheltuiala cu serviciul, la valoarea facturii.

`4426 = 4427` — TVA autoimpusă, `bază × cotă / 100`, rotunjit aritmetic la 2 zecimale.

## Un exemplu

::: ghid-exemplu
O firmă românească plătește **2.800 lei** pentru găzduire cloud unei firme nestabilite în România, cotă TVA **21%**.

- **Cheltuiala**: `628 = 401` cu **2.800 lei**
- **TVA autoimpusă**: `4426 = 4427` cu 2.800 × 21 / 100 = **588 lei**

Firma plătește furnizorului doar cei 2.800 lei ai facturii; TVA de 588 lei se evidențiază simultan la deduceri și la colectate.
:::

## Ce se greșește în practică

- **Se citează articolul de la achiziția de bunuri (308) sau de la import (309) drept temei pentru servicii primite**, când temeiul corect e art. 307 alin. (2) — cele trei articole privesc obiecte diferite (servicii, bunuri intracomunitare, import).
- **Se tratează diferit un furnizor UE față de unul din afara UE**, deși regula de bază a locului prestării (art. 278 alin. (2)) și obligația de plată a beneficiarului (art. 307 alin. (2)) nu depind de această distincție.
- **Se omite raportarea specifică pentru servicii intracomunitare** (D390) atunci când furnizorul e dintr-un alt stat membru UE, tratând operațiunea doar ca o cheltuială obișnuită.

## Ce face iConta.eu

Pentru furnizorii din UE, codul de TVA e analizat automat — prefixul de țară e verificat contra listei celor 27 de state membre plus `XI`; operațiunea e tratată ca prestare intracomunitară doar dacă țara codului nu e România. Calculul TVA la taxare inversă aplică formula `TVA = bază × cotă / 100`, cu rotunjire aritmetică (`ROUND_HALF_UP`) la 2 zecimale, cu cota transmisă explicit la fiecare calcul, fără valoare implicită.

[iConta.eu](/)
