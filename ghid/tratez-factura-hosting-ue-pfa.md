---
title: Cum tratez o factură de hosting din UE la un PFA?
description: Un serviciu de hosting cumpărat de la un furnizor UE e o achiziție intracomunitară de servicii — PFA neplătitor de TVA se înregistrează art. 317 și declară achiziția în D301 secțiunea 4.1.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum tratez o factură de hosting din UE la un PFA?

Un serviciu de găzduire web (hosting) cumpărat de la un furnizor stabilit într-un stat membru UE e, pentru un PFA din România, o achiziție intracomunitară de servicii — locul prestării e la sediul beneficiarului, în România.

## Temeiul legal

::: ghid-temei
"Locul de prestare a serviciilor către o persoană impozabilă (...) este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice." — Codul fiscal, Legea nr. 227/2015, art. 278 alin. (2)
:::

::: ghid-temei
"Taxa este datorată de orice persoană impozabilă (...) care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României (...)" — Codul fiscal, art. 307 alin. (2)
:::

Pentru un PFA neplătitor de TVA:

1. **înregistrarea specială art. 317** trebuie făcută înainte de a primi serviciul, fără prag valoric;
2. achiziția se declară în **D301, secțiunea 4.1** (tip 5), cu bază de impozitare = valoare în valută × cursul de schimb;
3. dacă furnizorul (țară + cod TVA) e completat pe operațiune, ea apare automat și în **D390**, cu codul S.

Dacă PFA-ul e plătitor de TVA (art. 316), aceeași achiziție nu trece prin D301, ci prin D300, prin taxare inversă (colectat și deductibil, net zero).

## Ce se greșește în practică

- Se contabilizează cheltuiala de hosting fără să se declare autoimpunerea prin taxare inversă.
- Se așteaptă "un plafon" pentru înregistrarea art. 317 — nu există un asemenea prag pentru servicii intracomunitare.
- Se folosește cursul de schimb din data facturii fără verificare, când data exigibilității poate diferi.

## Ce face iConta.eu

Aplicația calculează baza de impozitare exclusiv din valoarea în valută și cursul introdus, refuzând un curs absent sau ≤ 0. Introducerea D301 e permisă doar pentru profilurile neplătitoare de TVA; pentru un PFA plătitor, ecranul respinge explicit operațiunea și direcționează spre D300.

[iConta.eu](/)
