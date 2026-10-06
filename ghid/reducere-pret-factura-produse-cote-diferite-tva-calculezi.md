---
title: "Reducere de preț pe o factură cu produse la cote diferite de TVA: cum calculezi corect taxa?"
description: "Reducerea se aplică separat pe baza fiecărei cote, iar TVA se calculează pe baza redusă: 21% pe produsele la cota standard, 11% pe cele la cota redusă. Nu pe total."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Reducere de preț pe o factură cu produse la cote diferite de TVA: cum calculezi corect taxa?

Reducerea se împarte pe cote. Se aplică pe baza impozabilă a fiecărei grupe de produse, iar TVA se calculează separat pentru fiecare cotă, asupra bazei rămase după reducere. O reducere acordată direct clientului la momentul livrării nu intră în baza de impozitare. De aceea nu poți calcula TVA la valoarea brută și apoi scădea reducerea „global”, cu o singură cotă.

Greșeala apare des la facturile mixte: alimente la 11% și nealimentare la 21%, cărți și papetărie, medicamente și cosmetice. O reducere trecută pe un singur rând, cu o singură cotă, strică TVA colectată. Afectează și D300, și D394.

## Temeiul legal

::: ghid-temei
„Baza de impozitare nu cuprinde următoarele: a) rabaturile, remizele, risturnele, sconturile și alte reduceri de preț, acordate de furnizori direct clienților la data exigibilității taxei;”
— Codul fiscal (Legea 227/2015), art. 286 alin. (4) lit. a) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

::: ghid-temei
„31. (1) În sensul art. 286 alin. (4) lit. a) din Codul fiscal, rabaturile, remizele, risturnele, sconturile și alte reduceri de preț nu se cuprind în baza de impozitare a taxei dacă sunt acordate de furnizor/prestator direct în beneficiul clientului la momentul livrării/prestării și nu constituie, în fapt, remunerarea unui serviciu sau unei livrări.”
— HG 1/2016 (Normele metodologice ale Codului fiscal), pct. 31 alin. (1), titlul VII (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))

„Pe factură se înscrie baza impozabilă a celor două livrări, respectiv 2.000 lei plus 5.000 lei, baza se reduce cu 10%, iar TVA se aplică asupra bazei reduse [...] Se consideră că factura este corectă inclusiv dacă TVA este menționată integral înainte de reducerea bazei și apoi se menționează cu minus TVA aferentă reducerii.”
— HG 1/2016, pct. 31 alin. (1), Exemplul nr. 2 (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))
:::

Exemplul din norme folosește cotele din 2016 (20% și 9%). Metoda rămâne valabilă, dar cotele de azi sunt 21% (standard) și 11% (redusă), conform art. 291 din Codul fiscal, în vigoare din 1 august 2025.

Ce înseamnă concret:

- **Reducerea în procente** se aplică pe fiecare bază în parte. TVA se calculează la baza redusă, cu cota fiecărei grupe.
- **Două prezentări sunt acceptate.** Fie bazele deja reduse, cu TVA calculată pe ele. Fie TVA integrală înaintea reducerii, urmată de rânduri cu minus pentru reducere și TVA aferentă, pe fiecare cotă. Rezultatul trebuie să fie același.
- **Reducerea în sumă fixă pe total** trebuie și ea împărțită pe cote. Norma nu impune o metodă. Soluția ușor de susținut la control este repartizarea proporțională cu bazele, arătată explicit pe factură.
- **Reducerea acordată după livrare** nu se tratează la fel. Ea ajustează ulterior baza de impozitare, conform art. 287 lit. c), prin factură cu minus, tot separat pe fiecare cotă a livrării inițiale.
- **Reducerea care e, de fapt, plata unui serviciu** nu reduce baza. Exemplu: furnizorul „reduce” prețul ca să acopere reparații făcute de client. Suma e remunerația unui serviciu prestat de client (pct. 31 alin. (1), Exemplul nr. 1).

::: ghid-exemplu
SC Exemplu SRL livrează într-o singură factură produse la cota de 21% în valoare de 2.000 lei și produse alimentare la cota de 11% în valoare de 5.000 lei. Acordă pe loc o reducere de 10%.

- Cota 21%: baza redusă este 2.000 − 200 = 1.800 lei, iar TVA este 1.800 × 21% = 378 lei.
- Cota 11%: baza redusă este 5.000 − 500 = 4.500 lei, iar TVA este 4.500 × 11% = 495 lei.
- Total factură: 6.300 lei bază + 873 lei TVA = 7.173 lei.

Greșit ar fi să se aplice 21% la toată reducerea de 700 lei, adică 147 lei. TVA colectată ar ieși (420 + 550) − 147 = 823 lei, cu 50 lei mai puțin decât trebuie.
:::

## Ce se greșește în practică

- Reducerea se trece pe un singur rând, cu cota standard, indiferent de ce produse a redus.
- O reducere fixă se repartizează după bunul-plac, de pildă toată pe produsele la 21%, ca să scadă TVA colectată.
- O reducere acordată ulterior se regularizează cu o singură cotă, deși factura inițială avea mai multe.
- Sumele care sunt, de fapt, servicii prestate de client (marketing, reparații, poziționare la raft) se tratează drept reduceri de preț.

## Ce face iConta.eu

La contarea facturilor, iConta.eu calculează TVA separat pe fiecare cotă și face stornările cu semn pentru reducerile ulterioare. Reducerea o introduci pe cote: bază redusă sau rând cu minus pentru fiecare cotă. Aplicația calculează TVA pentru fiecare dintre ele. Repartizarea unei reduceri fixe pe cote o decizi tu. Aplicația nu împarte automat o reducere globală între cote.

[iConta.eu](/)
