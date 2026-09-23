---
title: "Cum se aplică taxarea inversă la un mijloc fix cumpărat din UE?"
description: "Taxarea inversă la un mijloc fix cumpărat din UE urmează formula contabilă 4426=4427, aceeași folosită la orice altă achiziție intracomunitară — norma o extinde explicit la toate situațiile de taxare inversă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se aplică taxarea inversă la un mijloc fix cumpărat din UE?

Mecanismul taxării inverse nu are o variantă separată pentru mijloacele fixe — formula contabilă e aceeași ca la o achiziție intracomunitară de marfă, doar destinația bunului diferă.

## Temeiul legal

::: ghid-temei
„HG 1/2016, norme la CF art. 331, pct. 109 alin. (1) — beneficiarul înregistrează… suma taxei aferente în următoarea formulă contabilă: 4426 = 4427. **Prevederile acestui alineat sunt valabile pentru orice alte situații în care se aplică taxarea inversă**.” — `anaf_surse/hg_1_2016_norme_cod_fiscal.txt` L242, dosarul F050.
:::

Beneficiarul (cumpărătorul din România) calculează TVA la valoarea achiziției, cu cota aplicabilă, și înregistrează simultan taxa colectată și taxa deductibilă în formula 4426=4427 — fără plată efectivă de TVA către furnizor sau către buget, cu excepția eventualelor regularizări legate de deductibilitate. Norma citată extinde explicit această formulă „la orice alte situații în care se aplică taxarea inversă”, deci acoperă și achiziția intracomunitară a unui mijloc fix.

## Ce se greșește în practică

- Se calculează taxarea inversă folosind o cotă „scrisă în cod” sau reținută din memorie, fără s-o declare explicit pentru fiecare operațiune — o schimbare de cotă legislativă poate rămâne neaplicată dacă valoarea nu e introdusă la fiecare calcul.
- Se omite înregistrarea 4426=4427 pe motiv că bunul e o imobilizare, nu marfă — formula se aplică oricărei taxări inverse, indiferent de destinația bunului.
- Se rotunjește suma TVA cu metode diferite de la o operațiune la alta, în loc de o rotunjire aritmetică consecventă.

## Ce face iConta.eu

Calculul taxării inverse nu are o cotă implicită — funcția care îl execută cere explicit baza și cota de la apelant, tocmai ca o schimbare legislativă a cotei să nu se piardă tăcut într-o valoare fixată în cod. Rotunjirea sumei se face cu regulă zecimală consecventă, nu prin rotunjire simplă la număr întreg.

[iConta.eu](/)
