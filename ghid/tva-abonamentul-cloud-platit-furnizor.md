---
title: "TVA la abonamentul de cloud plătit către un furnizor din UE"
description: "Un abonament de cloud cumpărat de la un furnizor din alt stat membru e o achiziție de serviciu intracomunitar — taxa se plătește prin taxare inversă de către firma din România, indiferent dacă furnizorul a facturat sau nu cu TVA."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# TVA la abonamentul de cloud plătit către un furnizor din UE

Un abonament de cloud, la fel ca orice alt serviciu digital cumpărat de la un furnizor stabilit în alt stat membru, urmează regula B2B de la art. 278 alin. (2) — locul prestării e la beneficiar, adică în România.

## Temeiul legal

::: ghid-temei
„CF art. 308-309 — Obligat la plata taxei = beneficiarul, la AIC/servicii primite.” — `cod_fiscal_227_2015_consolidat.txt` L19405, L19418, dosarul F050.

„`tva_taxare_inversa(baza, cota=None)` — TVA prin taxare inversă la AIC/servicii primite; cota nu are valoare implicită...” — `core/intracomunitar.py`, dosarul F050.
:::

Firma din România, ca beneficiar al serviciului, e cea care datorează taxa — prin taxare inversă, nu prin plata unei sume suplimentare către furnizor. Operațiunea se declară în D390, la codul de achiziții de servicii intracomunitare, iar codul de TVA al furnizorului se verifică în VIES.

## Ce se greșește în practică

- Se tratează abonamentul ca simplă cheltuială cu TVA-ul inclus, fără verificarea codului de TVA al furnizorului și fără aplicarea taxării inverse.
- Se presupune că, dacă factura furnizorului nu conține TVA vizibil, operațiunea „nu are TVA” — de fapt, taxa e datorată de beneficiar, în România, separat de ce a facturat furnizorul.
- Se omite declararea în D390 pe motiv că e o cheltuială recurentă mică — valoarea operațiunii nu scutește de obligația declarativă.

## Ce face iConta.eu

Ecranul de achiziție intracomunitară (categoria „Extern”) acceptă și tipul „servicii”, cu cod TVA furnizor UE și valoare; codul furnizorului se verifică automat în VIES, iar taxa se calculează prin taxare inversă, cu cota declarată explicit la fiecare operațiune (fără valoare implicită „scrisă în cod”).

[iConta.eu](/)
