---
title: Cum se înregistrează domeniile și serviciile de hosting?
description: Domeniile web și serviciile de hosting sunt cheltuieli cu servicii, dar cumpărate frecvent de la furnizori stabiliți în afara României — ceea ce declanșează, pentru o firmă neplătitoare de TVA, obligații declarative separate.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează domeniile și serviciile de hosting?

Înregistrarea unui domeniu și abonamentul de hosting sunt, în cea mai mare parte a cazurilor, cumpărate de la furnizori care nu sunt stabiliți în România — companii de tip registrar sau furnizori de infrastructură cloud, cu sediul fie în alt stat membru UE, fie în afara Uniunii. Tratamentul contabil de bază (cheltuială cu servicii prestate de terți) e simplu; ce diferă e componenta de TVA.

## Temeiul legal

::: ghid-temei
„Locul de prestare a serviciilor către o persoană impozabilă (...) este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice." — Codul fiscal (Legea 227/2015), art. 278 alin. (2)
:::

Locul prestării pentru un domeniu sau un abonament de hosting cumpărat de o firmă din România e România, indiferent unde e stabilit furnizorul. Asta înseamnă că firma, nu furnizorul, datorează TVA pentru operațiune — furnizorul ar trebui să factureze fără TVA local.

### Cum se declară, în funcție de statutul TVA și de furnizor

- **Firmă plătitoare de TVA:** taxare inversă în D300, rd. 7 + rd. 20, net zero, indiferent dacă furnizorul e stabilit în UE sau nu.
- **Firmă neplătitoare de TVA, furnizor stabilit în UE:** D301 secțiunea 4.1 (tip 5) + D390 cod S. Necesită înregistrare specială prin art. 317, înainte de prima achiziție, fără plafon.
- **Firmă neplătitoare de TVA, furnizor stabilit în afara UE:** D301 secțiunea 4 (tip 4, art. 307 alin. (6)), fără D390.

**Verifică pe fiecare factură** țara de stabilire a furnizorului — mulți registrari și furnizori de hosting facturează prin entități diferite pentru clienți din UE față de clienți din afara ei, iar acest detaliu schimbă tipul operațiunii.

### Exemplu de calcul

Reînnoire domeniu + hosting, 65,00 EUR, curs zilei exigibilității 4,9773 lei/EUR:

baza = round(65,00 × 4,9773; 0) = round(323,52...; 0) = **324 lei**

Baza se rotunjește la leu întreg, conform formulei oficiale (valoare în valută × curs de schimb).

## Ce se greșește în practică

- Se înregistrează cheltuiala doar contabil, fără nicio verificare a obligației de TVA — pentru un neplătitor, achiziția tot trebuie declarată în D301, chiar dacă suma e mică.
- Se presupune că un domeniu „.ro" înseamnă automat furnizor din România — registrarul care emite factura poate fi stabilit oriunde, indiferent de extensia domeniului.
- Se tratează la fel toate facturile de hosting ale aceluiași furnizor, fără verificare periodică — entitatea de facturare se poate schimba în timp.

## Ce face iConta.eu

Fiecare operațiune de tip 5 introdusă în ecranul D301 poartă câmpurile de țară și cod TVA ale furnizorului, opționale la completare, dar cu efect automat: dacă sunt completate, operațiunea apare și în D390. Baza nu se stochează la introducere — se recalculează la generarea declarației, rotunjită la leu întreg. Pentru o firmă plătitoare de TVA, introducerea în D301 e blocată la nivel de aplicație, cu trimitere explicită la D300.

[iConta.eu](/)
