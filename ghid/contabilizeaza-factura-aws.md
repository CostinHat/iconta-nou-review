---
title: Cum se contabilizează factura AWS?
description: Factura de la Amazon Web Services se declară diferit după statutul de TVA al firmei și după entitatea care emite factura — verifici întâi cine e furnizorul, apoi alegi între D300 și D301.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează factura AWS?

Serviciile cloud (instanțe, stocare, trafic) cumpărate de la Amazon Web Services sunt, pentru o firmă din România, o achiziție de servicii cu locul prestării în România. Contabil e o cheltuială de exploatare; fiscal, contează cine emite factura și unde e stabilit.

## Temeiul legal

::: ghid-temei
„Taxa este datorată de orice persoană impozabilă (...) care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României (...)" — Codul fiscal (Legea 227/2015), art. 307 alin. (2)
:::

Regula mută obligația de plată a TVA de la furnizor la beneficiar, pentru un furnizor stabilit în alt stat membru UE. Dacă furnizorul care emite factura AWS **nu** e stabilit în UE, mecanismul de taxare inversă se aplică tot beneficiarului, dar pe alt temei (art. 307 alin. (6)) — cu o consecință declarativă diferită: acea operațiune nu apare în D390.

**Nu presupune** entitatea de facturare fără să te uiți pe factură — Amazon operează prin mai multe entități regionale, iar din perspectiva TVA doar cea care apare efectiv pe factura ta contează.

### Cum se declară

- **Firmă plătitoare de TVA:** taxare inversă în D300, rd. 7 + rd. 20, net zero, indiferent dacă furnizorul e sau nu stabilit în UE — D301 e blocat pentru acest profil.
- **Firmă neplătitoare de TVA, furnizor stabilit în UE:** D301 secțiunea 4.1 (tip 5) + D390 cod S. Necesită înregistrare specială prin art. 317, făcută **înainte** de primul serviciu cumpărat, fără plafon.
- **Firmă neplătitoare de TVA, furnizor stabilit în afara UE:** D301 secțiunea 4 (tip 4, art. 307 alin. (6)), fără D390.

### Exemplu de calcul

Factură AWS, 84,20 USD, curs zilei exigibilității 4,5850 lei/USD:

baza = round(84,20 × 4,5850; 0) = round(386,05...; 0) = **386 lei**

Rotunjirea se face la leu întreg (fără zecimale), nu la bani — formula oficială e coloana „valoare valută" × coloana „curs de schimb", rotunjită direct la leu.

## Ce se greșește în practică

- Se declară toate facturile AWS identic, fără să se verifice, factură cu factură, entitatea emitentă — două facturi din luni diferite pot avea temeiuri diferite (tip 4 vs. tip 5).
- Se așteaptă înregistrarea fiscală „când se atinge un prag" — pentru servicii intracomunitare (art. 307 alin. (2)), obligația de înregistrare prin art. 317 apare de la prima achiziție, fără plafon.
- Se calculează baza cu zecimale de bani, nu rotunjită la leu întreg.

## Ce face iConta.eu

La introducerea unei operațiuni D301, contabilul alege tipul, valuta, valoarea și cursul; câmpurile de țară și cod TVA ale furnizorului sunt opționale, dar completarea lor declanșează automat includerea în D390 (tip 5 → cod S). Baza nu se stochează la introducere — se recalculează la generarea declarației, rotunjită la leu întreg, exact conform formulei oficiale. Pentru o firmă plătitoare de TVA, introducerea în D301 e refuzată explicit, cu trimitere la D300.

[iConta.eu](/)
