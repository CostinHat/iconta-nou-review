---
title: Cum tratez un abonament software din UE la un neplătitor de TVA?
description: Un abonament software cumpărat de la un furnizor UE de o firmă neplătitoare de TVA e o achiziție intracomunitară de servicii — declarată în D301 secțiunea 4.1, cu înregistrare art. 317 în prealabil.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum tratez un abonament software din UE la un neplătitor de TVA?

Un abonament software (SaaS) cumpărat de la un furnizor stabilit într-un stat membru UE e, din perspectiva TVA, o achiziție intracomunitară de servicii — locul prestării e în România, la sediul beneficiarului.

## Temeiul legal

::: ghid-temei
"Locul de prestare a serviciilor către o persoană impozabilă (...) este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice." — Codul fiscal, Legea nr. 227/2015, art. 278 alin. (2)
:::

::: ghid-temei
"Taxa este datorată de orice persoană impozabilă (...) care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României (...)" — Codul fiscal, art. 307 alin. (2)
:::

::: ghid-temei
Secțiunea 4.1 „Achiziții de servicii intracomunitare, pentru care beneficiarul este obligat la plata TVA conform art. 307 alin. (2)" — OPANAF nr. 592/2016, Anexa 1
:::

Pentru o firmă neplătitoare de TVA (neînregistrată art. 316), pașii sunt:

1. **înregistrarea specială art. 317**, obligatorie înainte de a primi serviciul, fără prag valoric;
2. **declararea achiziției în D301**, la secțiunea 4.1 (tip 5), cu bază = valoare în valută × curs, TVA calculat la cota aplicabilă;
3. dacă țara și codul de TVA ale furnizorului sunt completate pe operațiune, ea apare automat și în D390 (cod S).

Firma plătitoare de TVA (art. 316) nu trece prin D301: aceeași achiziție se tratează în D300, taxare inversă, net zero.

## Ce se greșește în practică

- Se plătește abonamentul și se contabilizează cheltuiala, dar se omite complet obligația de autoimpunere prin taxare inversă.
- Se amână înregistrarea art. 317 până "se cumulează mai multe facturi" — nu există un plafon care să amâne obligația.
- Se completează D300 la o firmă neplătitoare, deși acest formular e specific plătitorilor de TVA.

## Ce face iConta.eu

Ecranul D301 refuză explicit introducerea unei operațiuni dacă firma e marcată plătitoare de TVA, cu mesaj care direcționează spre D300/D390. Pentru neplătitori, alegerea tipului de operațiune (aici, tipul 5) și completarea datelor furnizorului determină automat dacă operațiunea apare și în D390 — fără dublă introducere manuală.

[iConta.eu](/)
