---
title: Taxarea inversă la achiziția intracomunitară de bunuri
description: La o achiziție intracomunitară de bunuri, taxa e datorată de cumpărător (art. 308 alin. (1) Cod fiscal), calculată ca bază × cotă și înregistrată prin 4426 = 4427, conform pct. 109 alin. (1) din normele HG 1/2016.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se aplică taxarea inversă la o achiziție intracomunitară?

Taxarea inversă înseamnă că, deși furnizorul din alt stat membru nu facturează TVA, tu — cumpărătorul — ești cel care calculează și evidențiază taxa, în aceeași lună, prin două conturi care se anulează reciproc. Nu e o scutire și nu e o taxă suplimentară: e o mutare a obligației de plată de la furnizor la beneficiar, ca să nu se piardă urma TVA la o tranzacție transfrontalieră.

## Temeiul legal

::: ghid-temei
**Art. 268 alin. (3) lit. a) Cod fiscal** — definește AIC ca operațiune impozabilă: *„Sunt, de asemenea, operațiuni impozabile și următoarele operațiuni efectuate cu plată, pentru care locul este considerat a fi în România, potrivit art. 276: a) o achiziție intracomunitară de bunuri, altele decât mijloace de transport noi sau produse accizabile, efectuată de o persoană impozabilă ce acționează ca atare sau de o persoană juridică neimpozabilă, care nu beneficiază de excepția prevăzută la alin. (4)..."*

**Art. 308 alin. (1) Cod fiscal** — cine plătește: *„Persoana care efectuează o achiziție intracomunitară de bunuri care este taxabilă, conform prezentului titlu, este obligată la plata taxei."*

**Norme HG 1/2016, pct. 109 alin. (1)** — formula contabilă: *„Din punct de vedere contabil, beneficiarul înregistrează în cursul perioadei fiscale în care taxa este exigibilă suma taxei aferente în următoarea formulă contabilă: 4426 = 4427. Prevederile acestui alineat sunt valabile pentru orice alte situații în care se aplică taxarea inversă."*
:::

## Cum se calculează suma

Formula e simplă în aparență — `TVA = bază × cotă / 100` — dar două lucruri contează în practică:

1. **Rotunjirea e aritmetică**, la 2 zecimale (dacă a treia zecimală e ≥ 5, se rotunjește în sus), nu rotunjirea bancară implicită a multor limbaje de programare, care poate produce diferențe de un ban la sume exacte pe „,5".
2. **Cota nu poate fi implicită.** Legea schimbă periodic cotele de TVA; o cotă scrisă o singură dată într-un șablon sau într-o constantă rămâne corectă doar până la următoarea modificare legislativă, după care produce sume greșite fără niciun semnal de eroare.

Baza de calcul trebuie să fie strict pozitivă — o achiziție cu bază zero sau negativă nu are sens economic pentru taxare inversă și nu se calculează.

Rezultatul se înregistrează prin **4426 = 4427**: 4426 (TVA deductibilă) și 4427 (TVA colectată) cresc cu aceeași sumă, simultan. Pentru o firmă cu drept integral de deducere, efectul net în decont e zero, dar înregistrarea și raportarea (D300, D390) rămân obligatorii.

## Un exemplu

::: ghid-exemplu
Bază de calcul: **4.250 lei**, cotă TVA **21%**.

`TVA = 4.250 × 21 / 100 = 892,50 lei`

Nota contabilă: `4426 = 4427` cu **892,50 lei**. Suma apare simultan la deduceri și la colectate — nu se plătește nimic furnizorului în plus, dar taxa e evidențiată integral, așa cum cere legea.
:::

## Ce se greșește în practică

- **Se ia o cotă implicită din memorie sau dintr-un șablon vechi**, în loc să se verifice cota în vigoare pentru perioada respectivă — riscul crește exact atunci când legea schimbă o cotă, moment în care valoarea veche „pare" în continuare corectă.
- **Se rotunjește bancar (half-to-even)** în loc de rotunjire aritmetică — diferența apare rar, dar apare exact pe sumele care cad pe „,5" la a treia zecimală.
- **Se omite complet formula 4426 = 4427**, tratând achiziția ca și cum n-ar avea TVA românesc, pentru că furnizorul n-a facturat taxă.

## Ce face iConta.eu

Calculul taxei aplică formula `TVA = bază × cotă / 100`, cu rotunjire aritmetică (`ROUND_HALF_UP`) la 2 zecimale, nu rotunjire bancară. Cota nu are valoare implicită — trebuie transmisă explicit la fiecare calcul, exact pentru ca o cotă înghețată în cod să nu producă sume greșite tăcut la o schimbare legislativă. Baza de calcul trebuie să fie strict pozitivă.

[iConta.eu](/)
