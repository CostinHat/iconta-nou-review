---
title: "Amortizarea și leasingul financiar: cine e proprietar fiscal"
description: "La leasingul financiar, locatarul e tratat fiscal drept proprietar al bunului — indiferent la cine rămâne titlul juridic — deci el amortizează și el deduce cheltuielile."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Amortizarea și leasingul financiar: cine e proprietar fiscal

Proprietatea juridică poate rămâne, prin contract, la societatea de leasing până la exercitarea opțiunii de cumpărare — dar fiscal, la leasingul financiar, „proprietarul" e utilizatorul (locatarul). Legea taie explicit legătura dintre titlul juridic și tratamentul fiscal.

## Temeiul legal

::: ghid-temei
**Legea 227/2015 (Codul fiscal), art. 29 alin. (1)**: „În cazul leasingului financiar utilizatorul este tratat din punct de vedere fiscal ca proprietar, în timp ce, în cazul leasingului operațional, locatorul are această calitate."

**OMFP 1802/2014, pct. 214 alin. (1)**: „Înregistrarea în contabilitate a amortizării bunului ce face obiectul contractului se efectuează în cazul leasingului financiar de către locatar/utilizator [...]."
— (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt; anaf_surse/omfp_1802_2014.txt)
:::

- Codul fiscal spune explicit: la leasingul financiar, **utilizatorul** (locatarul) e „tratat ca proprietar" — nu societatea de leasing, care rămâne formal creditor/finanțator.
- Din această calitate decurge dreptul (și obligația) de a amortiza bunul și de a deduce dobânda, la locatar.
- Simetric, la leasingul operațional, calitatea de „proprietar fiscal" rămâne la locator — el amortizează, firma utilizatoare deduce doar chiria.

## Ce se greșește în practică

- Se așteaptă ca actul de proprietate (de exemplu cartea de identitate a unui vehicul) să decidă cine e „proprietarul fiscal" — de fapt legea decide invers, pe baza tipului de contract, nu pe baza titlului juridic.
- Se aplică regula de la leasingul operațional unei situații de leasing financiar (sau invers), fără să se verifice întâi clasificarea contractului, potrivit criteriilor de la OMFP pct. 213.
- Se presupune că „proprietar fiscal" înseamnă și proprietar juridic definitiv — de fapt termenul se referă strict la tratamentul contabil-fiscal, nu la titlul de proprietate din contractul de leasing.

## Ce face iConta.eu

F056 (Leasing financiar și operațional) implementează monografia din perspectiva locatarului tratat ca proprietar la leasingul financiar: bunul intră în contabilitatea lui de la primire (2133=167), consecvent cu art. 29 alin. (1) din Codul fiscal. Clasificarea inițială a contractului (financiar sau operațional) rămâne însă decizia contabilului, luată înainte de a alege tipul de operațiune în ecran — aplicația nu evaluează automat criteriile de clasificare din OMFP pct. 213.

[iConta.eu](/)
