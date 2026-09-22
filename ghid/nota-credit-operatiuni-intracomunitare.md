---
title: Nota de credit pentru operațiuni intracomunitare — tratament contabil
description: O notă de credit primită de la furnizorul UE pentru o achiziție intracomunitară reduce proporțional baza și TVA autoimpusă prin 4426 = 4427, conform pct. 109 alin. (1) din normele HG 1/2016, aplicabil oricărei situații de taxare inversă.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se tratează contabil o notă de credit pentru o achiziție intracomunitară?

Un furnizor din alt stat membru UE poate emite o notă de credit pentru o achiziție intracomunitară deja înregistrată — marfă returnată, discount ulterior sau corectare de preț. Pentru că achiziția inițială a fost înregistrată prin taxare inversă, nota de credit trebuie să reducă simetric ambele înregistrări: valoarea mărfii și TVA autoimpusă, nu doar una dintre ele.

## Temeiul legal

::: ghid-temei
**Art. 268 alin. (3) lit. a) Cod fiscal** — operațiunea inițială rămâne AIC: *„Sunt, de asemenea, operațiuni impozabile și următoarele operațiuni efectuate cu plată, pentru care locul este considerat a fi în România, potrivit art. 276: a) o achiziție intracomunitară de bunuri, altele decât mijloace de transport noi sau produse accizabile, efectuată de o persoană impozabilă ce acționează ca atare sau de o persoană juridică neimpozabilă, care nu beneficiază de excepția prevăzută la alin. (4)..."*

**Art. 308 alin. (1) Cod fiscal** — obligația de plată a taxei rămâne a cumpărătorului: *„Persoana care efectuează o achiziție intracomunitară de bunuri care este taxabilă, conform prezentului titlu, este obligată la plata taxei."*

**Norme HG 1/2016, pct. 109 alin. (1)** — formula contabilă, cu clauza de generalizare care acoperă și corecțiile: *„Din punct de vedere contabil, beneficiarul înregistrează în cursul perioadei fiscale în care taxa este exigibilă suma taxei aferente în următoarea formulă contabilă: 4426 = 4427. Prevederile acestui alineat sunt valabile pentru orice alte situații în care se aplică taxarea inversă."*
:::

## Cum se corectează cele două înregistrări

Nota de credit reduce **baza** achiziției — deci reduce simetric și **TVA autoimpusă**, pentru că cele două sunt legate prin aceeași formulă (`TVA = bază × cotă / 100`).

**Corecția valorii mărfii**: `401 = 301/371/...` (invers față de recepție), cu suma din nota de credit.

**Corecția TVA autoimpuse**: `4427 = 4426` (invers față de taxarea inversă inițială), cu TVA aferentă sumei corectate, la aceeași cotă cu care a fost calculată operațiunea inițială.

Pentru o firmă cu drept integral de deducere, corecția rămâne neutră în decont — la fel ca operațiunea inițială — dar trebuie înregistrată în aceeași perioadă fiscală în care nota de credit devine exigibilă, nu „compensată" tacit la următoarea achiziție de la același furnizor.

## Un exemplu

::: ghid-exemplu
O firmă a înregistrat o achiziție intracomunitară de **6.000 lei**, cu TVA autoimpusă de 6.000 × 21 / 100 = **1.260 lei**.

Furnizorul emite ulterior o notă de credit de **1.000 lei** pentru marfă returnată parțial.

- **Corecție marfă**: `401 = 301` cu **1.000 lei**
- **Corecție TVA**: `4427 = 4426` cu 1.000 × 21 / 100 = **210 lei**

După corecție, baza rămasă e 5.000 lei, iar TVA autoimpusă rămasă e 1.050 lei — exact ce ar fi rezultat dacă achiziția inițială ar fi fost de la început de 5.000 lei.
:::

## Ce se greșește în practică

- **Se corectează doar valoarea mărfii, nu și TVA.** Nota de credit lasă contul de marfă corect, dar 4426/4427 rămân „umflate" cu TVA aferentă unei sume care nu mai există.
- **Se aplică o cotă diferită de cea din operațiunea inițială**, de exemplu cota curentă în loc de cota folosită la achiziția originală — corecția trebuie să oglindească exact tranzacția pe care o ajustează.
- **Se amână înregistrarea** până la următoarea achiziție de la același furnizor, „compensând" informal — nota de credit are propria dată de exigibilitate și trebuie evidențiată separat, în perioada ei.

## Ce face iConta.eu

Calculul TVA la taxare inversă aplică formula `TVA = bază × cotă / 100`, cu rotunjire aritmetică (`ROUND_HALF_UP`) la 2 zecimale — aceeași formulă, indiferent dacă baza vine dintr-o achiziție inițială sau dintr-o corecție. Cota trebuie transmisă explicit la fiecare calcul, fără valoare implicită înghețată în cod, iar baza trebuie să fie strict pozitivă.

[iConta.eu](/)
