---
title: "Metoda de amortizare în leasing operațional: impozitul pe profit"
description: "La leasingul operațional, firma utilizatoare nu alege nicio metodă de amortizare — amortizarea rămâne integral la societatea de leasing, conform legii."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Metoda de amortizare în leasing operațional: impozitul pe profit

Întrebarea presupune că firma care folosește bunul (locatarul) ar avea de ales o metodă de amortizare pentru un bun luat în leasing operațional, deductibilă la impozitul pe profit. Regula legală spune exact opusul: la leasingul operațional, amortizarea nu se ține deloc la utilizator.

## Temeiul legal

::: ghid-temei
**OMFP 1802/2014, pct. 214 alin. (1) și (3)**: „Înregistrarea în contabilitate a amortizării bunului ce face obiectul contractului se efectuează în cazul leasingului financiar de către locatar/utilizator, iar în cazul leasingului operațional, de către locator/finanțator. [...] În cazul leasingului operațional, bunurile sunt supuse amortizării de către locator, pe o bază consecventă cu politica normală de amortizare pentru bunuri similare ale acestuia."

**Legea 227/2015 (Codul fiscal), art. 29 alin. (2)-(3)**: „Amortizarea bunului care face obiectul unui contract de leasing se face de către utilizator, în cazul leasingului financiar, și de către locator, în cazul leasingului operațional, cheltuielile fiind deductibile, potrivit art. 28. În cazul leasingului financiar utilizatorul deduce dobânda, iar în cazul leasingului operațional locatarul deduce chiria (rata de leasing), potrivit prevederilor prezentului titlu."
— (sursă: anaf_surse/omfp_1802_2014.txt; anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- La leasingul operațional, **locatorul** (societatea de leasing) amortizează bunul, folosind propria politică de amortizare — firma utilizatoare nu are nicio decizie de luat aici.
- Firma utilizatoare nu deduce o „amortizare", ci **chiria** (rata de leasing) — o cheltuială curentă, nu o cheltuială de amortizare.
- Nu există, la locatar, nicio bază legală pentru a alege liniară/degresivă/accelerată pentru un bun pe care nu-l are în propriile imobilizări.

## Ce se greșește în practică

- Se caută o „metodă de amortizare" de ales pentru bunul luat în leasing operațional — nu există așa ceva la utilizator, pentru că bunul nu intră niciodată în imobilizările lui.
- Se confundă cheltuiala cu chiria (612) cu o cheltuială de amortizare (681) — sunt conturi și regimuri fiscale diferite.
- Se aplică regulile de amortizare fiscală de la art. 28 din Codul fiscal unei situații care, la locatar, cade sub art. 29 alin. (3) — deducerea chiriei, nu a unei amortizări.

## Ce face iConta.eu

Pentru leasing operațional, funcția `nota_rata_operational` din F056 (Leasing financiar și operațional) produce o singură notă: chiria pe contul de cheltuială (implicit 612) = 401, plus TVA pe 4426. Nu există niciun câmp sau funcție pentru „metodă de amortizare" în ecranul de leasing operațional — corect, pentru că regula legală nu prevede așa ceva la locatar. Ce se poate întreba legitim în acest caz e deductibilitatea chiriei, nu a unei amortizări inexistente.

[iConta.eu](/)
