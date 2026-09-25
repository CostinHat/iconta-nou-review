---
title: "Cine amortizează bunul în leasing financiar?"
description: "La leasingul financiar, amortizarea bunului se ține la locatar (firma care îl folosește), nu la societatea de leasing, indiferent de cine rămâne proprietar juridic."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cine amortizează bunul în leasing financiar?

Răspunsul e direct din lege: la leasingul financiar, amortizarea bunului se ține la **locatar** — firma care folosește bunul — nu la societatea de leasing (locator/finanțator). Regula e valabilă pentru orice tip de bun preluat prin leasing financiar, nu doar pentru autoturisme.

## Temeiul legal

::: ghid-temei
„214. ‐ (1) Înregistrarea în contabilitate a amortizării bunului ce face obiectul contractului se efectuează în cazul leasingului financiar de către locatar/utilizator, iar în cazul leasingului operațional, de către locator/finanțator."
— OMFP 1802/2014, pct. 214 alin. (1) (sursă: anaf_surse/omfp_1802_2014.txt)

„(1) În cazul leasingului financiar utilizatorul este tratat din punct de vedere fiscal ca proprietar, în timp ce, în cazul leasingului operațional, locatorul are această calitate."
— Legea 227/2015, art. 29 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Cine amortizează depinde exclusiv de **tipul de leasing**, nu de cine deține titlul juridic de proprietate — la financiar, titlul poate rămâne formal al finanțatorului până la ultima rată, dar amortizarea tot la locatar se ține.
- Legea confirmă și pe latura fiscală: locatarul e „tratat ca proprietar" la leasingul financiar, deci el e cel care amortizează și deduce cheltuiala.
- Simetric, la leasingul operațional, locatorul rămâne și contabil, și fiscal, proprietarul bunului — el amortizează.

## Ce se greșește în practică

- Se așteaptă ca actul de proprietate (de exemplu cartea de identitate a unui vehicul) să decidă cine amortizează — de fapt legea taie explicit legătura dintre titlul juridic și tratamentul contabil/fiscal, pentru leasingul financiar.
- Se amână începerea amortizării până la plata valorii reziduale sau exercitarea opțiunii de cumpărare — greșit, bunul intră în patrimoniul contabil al locatarului de la primire, nu la finalul contractului.
- Se aplică regula de la leasingul operațional (amortizează locatorul) unei situații de leasing financiar, fără să se verifice întâi clasificarea corectă a contractului.

## Ce face iConta.eu

Funcția `nota_primire_financiar` din F056 (Leasing financiar și operațional) înregistrează bunul la intrare (2133=167), la valoarea capitalului din contract, exact ca pentru un mijloc fix cumpărat direct — consecvent cu regula de mai sus. De acolo, amortizarea propriu-zisă rulează prin registrul general de Mijloace fixe, la locatar, fără nicio cerință suplimentară din modulul de leasing. Clasificarea contractului (financiar sau operațional) rămâne însă decizia contabilului, făcută înainte de a alege tipul de operațiune în ecran — aplicația nu evaluează automat criteriile de clasificare din OMFP pct. 213.

[iConta.eu](/)
