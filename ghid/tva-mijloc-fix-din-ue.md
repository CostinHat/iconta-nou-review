---
title: TVA la cumpărarea unui mijloc fix din UE
description: Utilajul sau echipamentul cumpărat de la un furnizor din alt stat membru UE e achiziție intracomunitară de bunuri (art. 268 alin. (3) lit. a) Cod fiscal), cu TVA autoimpusă prin 4426 = 4427, indiferent că bunul se capitalizează ca mijloc fix.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum tratez TVA la cumpărarea unui mijloc fix din UE?

Un utilaj, un vehicul de firmă (altul decât mijloc de transport nou) sau un echipament de producție cumpărat de la un furnizor înregistrat în scop de TVA în alt stat membru UE urmează același mecanism fiscal ca orice altă achiziție de bunuri din UE: e o achiziție intracomunitară, cu TVA autoimpusă prin taxare inversă. Faptul că bunul se capitalizează, nu se cheltuiește direct, schimbă doar contul de imobilizare — nu schimbă tratamentul de TVA.

## Temeiul legal

::: ghid-temei
**Art. 268 alin. (3) lit. a) Cod fiscal** — mijlocul fix e bun, deci intră sub definiția AIC: *„Sunt, de asemenea, operațiuni impozabile și următoarele operațiuni efectuate cu plată, pentru care locul este considerat a fi în România, potrivit art. 276: a) o achiziție intracomunitară de bunuri, altele decât mijloace de transport noi sau produse accizabile, efectuată de o persoană impozabilă ce acționează ca atare sau de o persoană juridică neimpozabilă, care nu beneficiază de excepția prevăzută la alin. (4)..."*

**Art. 308 alin. (1) Cod fiscal** — obligația de plată a taxei: *„Persoana care efectuează o achiziție intracomunitară de bunuri care este taxabilă, conform prezentului titlu, este obligată la plata taxei."*

**Norme HG 1/2016, pct. 109 alin. (1)** — formula contabilă: *„Din punct de vedere contabil, beneficiarul înregistrează în cursul perioadei fiscale în care taxa este exigibilă suma taxei aferente în următoarea formulă contabilă: 4426 = 4427. Prevederile acestui alineat sunt valabile pentru orice alte situații în care se aplică taxarea inversă."*
:::

## Conturi și formulă

Recepția mijlocului fix se înregistrează la costul de achiziție (convertit în lei), fără TVA:

`213/214/... = 404` (furnizori de imobilizări, dacă se separă de furnizorii curenți) sau `401`, funcție de politica contabilă a firmei.

TVA se autoimpune separat, indiferent de contul folosit pentru imobilizare: `4426 = 4427`, cu `TVA = bază × cotă / 100`, rotunjit aritmetic la 2 zecimale.

Punerea în funcțiune și amortizarea ulterioară a mijlocului fix urmează regulile obișnuite de imobilizări (cont 281 pentru amortizare) — sunt independente de mecanismul de TVA, care se închide integral la momentul recepției, prin cele două conturi de mai sus.

## Un exemplu

::: ghid-exemplu
O firmă cumpără un echipament de producție de la un furnizor din Austria, valoare **45.000 lei**, cotă TVA **21%**.

- **Recepție imobilizare**: `213 = 404` cu **45.000 lei**
- **TVA autoimpusă**: `4426 = 4427` cu 45.000 × 21 / 100 = **9.450 lei**

Firma plătește furnizorului austriac doar cei 45.000 lei ai facturii. TVA de 9.450 lei se evidențiază simultan la deduceri și la colectate, iar amortizarea pornește ulterior de la valoarea de 45.000 lei, fără TVA.
:::

## Ce se greșește în practică

- **Se include TVA-ul autoimpus în costul de intrare al mijlocului fix.** TVA-ul deductibil nu majorează baza de amortizare — rămâne separat, în 4426/4427, nu în 213/214.
- **Se așteaptă o factură cu TVA de la furnizorul UE**, tratând lipsa TVA de pe factură ca pe o scutire — furnizorul facturează corect fără TVA, taxa se calculează la cumpărător.
- **Se confundă cu mijloacele de transport noi**, care au regim special separat (nu intră sub excepția din art. 268 alin. (3) lit. a) — sunt taxabile la cumpărător indiferent de statutul acestuia, cu reguli proprii ce depășesc AIC obișnuită de bunuri).

## Ce face iConta.eu

Codul de TVA al furnizorului e analizat automat — prefixul de țară e verificat contra listei celor 27 de state membre UE plus `XI`; operațiunea e tratată ca intracomunitară doar dacă țara codului nu e România. TVA la taxare inversă se calculează cu `TVA = bază × cotă / 100`, rotunjit aritmetic (`ROUND_HALF_UP`) la 2 zecimale, cu cota transmisă explicit la fiecare calcul și baza strict pozitivă.

[iConta.eu](/)
