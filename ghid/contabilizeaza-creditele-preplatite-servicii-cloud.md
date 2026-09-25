---
title: "Cum se contabilizează creditele preplătite pentru servicii cloud?"
description: "Contul de cheltuieli înregistrate în avans, aplicat creditelor preplătite pentru servicii cloud consumate eșalonat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează creditele preplătite pentru servicii cloud?

Un credit cumpărat în avans pentru servicii cloud (procesare, stocare, API) nu e o cheltuială a lunii în care s-a plătit — e o plată anticipată pentru servicii care urmează să fie consumate eșalonat, în lunile următoare. Contabil, asta înseamnă cont de cheltuieli în avans, nu cheltuială directă.

## Temeiul legal

::: ghid-temei
„Cu ajutorul acestui cont se ține evidența cheltuielilor efectuate în avans care urmează a se suporta eșalonat pe cheltuieli, pe baza unui scadențar, în perioadele/exercițiile financiare viitoare. Contul 471 «Cheltuieli înregistrate în avans» este un cont de activ. În debitul contului 471 «Cheltuieli înregistrate în avans» se înregistrează: – sumele reprezentând chiriile, abonamentele, certificatele de emisii de gaze cu efect de seră achiziționate, sumele aferente prestării ulterioare de servicii (de exemplu, asistența tehnică) și alte cheltuieli efectuate anticipat (401, 512, 531)."
— OMFP nr. 1.802/2014, Reglementări contabile (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Aplicat la un credit preplătit pentru servicii cloud:

- La achiziția creditului: **471 „Cheltuieli înregistrate în avans" = 401/512**, la valoarea plătită furnizorului.
- Pe măsură ce creditul e consumat (procesare, stocare efectiv folosită), suma corespunzătoare trece din 471 pe cheltuiala de exploatare aferentă (de regulă 614 sau 628, servicii externe), conform unui scadențar de recunoaștere — nu neapărat liniar în timp, ci în funcție de consumul real.
- Dacă furnizorul e stabilit în alt stat (UE sau non-UE), la factura de achiziție a creditului se aplică regulile TVA pentru servicii electronice/servicii B2B (de regulă taxare inversă, dacă furnizorul e o persoană impozabilă din alt stat UE).
- Un credit neconsumat rămas la finalul exercițiului financiar rămâne în soldul contului 471, ca activ, nu ca o cheltuială a perioadei încheiate.

## Ce se greșește în practică

- Se înregistrează întreaga sumă plătită pentru credit direct pe cheltuială (614/628), în luna plății, deși serviciul va fi consumat eșalonat pe mai multe luni.
- Se recunoaște cheltuiala liniar, în rate egale, indiferent de consumul real, deși norma leagă recunoașterea de un scadențar corelat cu prestarea efectivă a serviciului.
- Se omite tratamentul TVA la achiziția de la un furnizor din alt stat (taxare inversă), tratând factura ca pe o achiziție internă obișnuită.

## Ce face iConta.eu

La data acestui ghid, iConta.eu ține evidența contabilă a cheltuielilor în avans (contul 471) pe baza notelor introduse manual, dar nu are un modul dedicat de urmărire automată a consumului de credite cloud preplătite (de exemplu, printr-un API al furnizorului) care să recunoască eșalonat cheltuiala pe măsura consumului real. Scadențarul de recunoaștere rămâne, în prezent, stabilit și aplicat manual de contabil.

[iConta.eu](/)
