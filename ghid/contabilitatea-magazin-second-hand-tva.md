---
title: "Contabilitatea unui magazin de second-hand: TVA la marjă"
description: "Ghid complet pentru regimul special de TVA la marjă (art. 312 CF) la vânzarea bunurilor second-hand, cu monografia contabilă și condițiile legale."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Contabilitatea unui magazin de second-hand: TVA la marjă

Un magazin de second-hand care cumpără bunuri folosite în scopul revânzării aplică regimul special de TVA la marjă: taxa se calculează pe diferența dintre prețul de vânzare și prețul de cumpărare, nu pe prețul integral de vânzare.

## Temeiul legal

::: ghid-temei
"persoana impozabilă revânzătoare este persoana impozabilă care, în cursul desfășurării activității economice, achiziționează sau importă bunuri second-hand [...] în scopul revânzării" [...] "baza de impozitare este marja profitului [...] exclusiv valoarea taxei aferente." [...] "Persoana impozabilă revânzătoare nu are dreptul la deducerea taxei [...] în măsura în care livrarea acestor bunuri se taxează în regim special." [...] "Persoana impozabilă revânzătoare nu are dreptul să înscrie taxa [...] în mod distinct, în facturile emise clienților."
— Codul fiscal (Legea 227/2015), art. 312 alin. (1) lit. e), alin. (4), alin. (6), alin. (12), `anaf_surse/cod_fiscal_227_2015_consolidat.txt` (linia 19802), dosar de cercetare F098.
:::

Mecanismul: la fiecare vânzare, marja = preț de vânzare − preț de cumpărare; TVA-ul colectat se extrage din marjă prin procedeul sutei mărite (marja × cotă / (100 + cotă)); dacă marja e negativă sau zero, nu se colectează TVA, dar operațiunea rămâne evidențiată în jurnalul special obligatoriu. Revânzătorul nu are drept de deducere pentru TVA-ul aferent achiziției bunului taxat în regim special și nu poate înscrie TVA distinct pe factura emisă clientului — pe factură se înscrie în schimb mențiunea obligatorie "regimul marjei - bunuri second-hand" (art. 319 CF). Regimul se aplică doar bunurilor achiziționate în scopul revânzării, de la o persoană neimpozabilă, de la o persoană impozabilă cu livrare scutită, de la o întreprindere mică sau de la un alt revânzător care a taxat el însuși bunul în regim special — verificarea acestei eligibilități a furnizorului rămâne o judecată de fond a contabilului, nu un calcul automat.

## Ce se greșește în practică

Greșeli frecvente: calcularea TVA-ului direct din marjă la cota nominală (fără procedeul sutei mărite); înscrierea distinctă a TVA pe factura emisă clientului, deși legea o interzice explicit în regimul special; deducerea TVA-ului la achiziția bunului, deși revânzătorul nu are acest drept când livrarea e taxată în regim de marjă; și aplicarea regimului unui bun care nu a fost achiziționat în scopul revânzării (de exemplu un mijloc fix propriu, folosit anterior în activitate și apoi vândut — acesta nu se califică drept "bun second-hand" în sensul art. 312, iar TVA se calculează pe prețul integral, nu pe marjă).

## Ce face iConta.eu

Motorul de calcul (`core/tva_marja.py`) aplică formula sutei mărite pe fiecare vânzare, cu cota de TVA ca parametru obligatoriu (fără valoare implicită) și rotunjire ROUND_HALF_UP. Ruta dedicată de vânzare în regim de marjă generează automat o notă contabilă ciornă cu liniile: cost de achiziție (4111=707), marja netă (4111=707) și TVA-ul aferent marjei (4111=4427) — totalul debitat în 4111 corespunde exact prețului de vânzare. Aplicația acoperă complet calculul pentru bunuri cumpărate atât din România, cât și din UE (formula nu depinde de țara furnizorului).

Ce nu automatizează aplicația: verificarea eligibilității furnizorului (dacă vânzătorul chiar se încadrează la condițiile art. 312 alin. (2)) rămâne responsabilitatea contabilului; regimul de neimpozabilitate al achiziției intracomunitare de bunuri second-hand (art. 268 alin. (8) lit. c)) nu are, la acest moment, o funcție dedicată de clasificare — doar latura de vânzare/revânzare e acoperită de motor. De asemenea, un jurnal vizual al marjei există doar ca funcție internă de citire (API, fără ecran dedicat în interfață).

[iConta.eu](/)
