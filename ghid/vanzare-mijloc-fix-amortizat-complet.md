---
title: Cum se vinde un mijloc fix amortizat complet
description: Când amortizarea cumulată acoperă integral valoarea de intrare, scoaterea din evidență se face doar 2813 = 21x, fără cheltuială cu valoarea rămasă, iar prețul încasat de la cumpărător se înregistrează separat, ca venit din vânzare.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se vinde un mijloc fix amortizat complet?

Un utilaj complet amortizat mai are, de multe ori, valoare de piață — și firma îl vinde. Din punct de vedere contabil, faptul că amortizarea cumulată egalează valoarea de intrare simplifică nota de ieșire: nu mai rămâne nimic de trecut pe cheltuială pentru partea neamortizată, pentru că nu există parte neamortizată. Rămân totuși două operațiuni distincte de făcut corect: scoaterea activului din evidență și înregistrarea prețului de vânzare.

## Temeiul legal

::: ghid-temei
**Art. 28 alin. (1) din Codul fiscal (Legea 227/2015)**: *„Cheltuielile aferente achiziționării, producerii, construirii mijloacelor fixe amortizabile, precum și investițiile efectuate la acestea se recuperează din punct de vedere fiscal prin deducerea amortizării potrivit prevederilor prezentului articol."*

Recuperarea fiscală a costului unui mijloc fix se face exclusiv prin amortizare, eșalonat pe durata normală de utilizare — de aceea, când amortizarea cumulată atinge valoarea de intrare, costul activului e deja integral recuperat prin cheltuielile deductibile înregistrate în anii anteriori.
:::

## Regula concretă

**La un activ amortizat integral**, valoarea contabilă netă e zero: valoarea de intrare (cont 21x/213x) = amortizarea cumulată (cont 2813). Scoaterea din evidență se rezumă la o singură notă:

```
2813 = 21x    (amortizare cumulată = valoare de intrare)
```

Nu apare cheltuiala 6583, pentru că nu există valoare rămasă neamortizată de trecut pe cheltuială.

**Separat**, prețul obținut de la cumpărător se înregistrează ca venit din vânzarea activelor, cu TVA colectată dacă firma e plătitoare:

```
4111 = %
         7583   (venit din vânzarea activelor)
         4427   (TVA colectată)
```

Cele două note sunt independente: una scoate activul din registru la valoarea lui contabilă (zero, în acest caz), cealaltă înregistrează încasarea. Diferența dintre prețul de vânzare și valoarea contabilă netă (aici, întregul preț de vânzare, pentru că valoarea netă e zero) reprezintă profitul din operațiune.

## Un exemplu

::: ghid-exemplu
Un utilaj cu valoare de intrare **20.000 lei** are amortizarea cumulată **20.000 lei** (complet amortizat). Firma îl vinde cu **3.000 lei + TVA**.

- Scoatere din evidență: **2813 = 213x, 20.000 lei**
- Încasare: **4111 = 7583 + 4427**, adică 4111 = 3.630 lei (3.000 + 21% TVA), din care 7583 = 3.000 lei, 4427 = 630 lei

Rezultatul operațiunii: venit de 3.000 lei, fără nicio cheltuială corespunzătoare, pentru că valoarea contabilă a activului era deja zero.
:::

## Ce se greșește în practică

- **Se trece eronat o valoare pe 6583** la un activ complet amortizat, „ca să existe o cheltuială la vânzare" — dacă amortizarea cumulată acoperă integral valoarea de intrare, nu există valoare rămasă de trecut pe cheltuială; 6583 rămâne zero.
- **Se amestecă cele două note într-una singură**, înregistrând direct diferența netă. Corect e ca scoaterea din evidență (2813 = 21x) și încasarea de la cumpărător (4111 = 7583 + 4427) să fie note separate — combinarea lor ascunde valoarea de intrare și amortizarea cumulată din analiza contului 21x.
- **Se omite TVA colectată** pe vânzare, pe motiv că „activul era deja amortizat, deci scutit". Amortizarea completă nu are legătură cu regimul de TVA al vânzării — dacă firma e plătitoare de TVA, vânzarea unui mijloc fix e, în general, operațiune taxabilă.

## Ce face iConta.eu

Registrul de mijloace fixe calculează, la orice dată, amortizarea acumulată și valoarea rămasă a fiecărui activ, pe metoda reală înregistrată pentru acel activ (liniară, degresivă, accelerată sau superaccelerată), nu pe o aproximare simplificată. La scoaterea din evidență, amortizarea cumulată la data operațiunii nu se introduce manual — se preia direct din acest calcul, pe același motor folosit și pentru generarea declarației D406/SAF-T, astfel încât registrul și raportările rămân consistente.

[iConta.eu](/)
