---
title: "Ce date din balanță trebuie verificate înainte de completarea D101?"
description: "Patru categorii de conturi din balanță condiționează direct corectitudinea D101: exploatare/financiar, capital, rezervă și impozit."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Ce date din balanță trebuie verificate înainte de completarea D101?

Balanța pe care o citește motorul D101 trebuie verificată punctual pe câteva conturi-cheie, nu doar la nivel de total.

Concret, de verificat înainte de completare:

- **Clasele 76/66** — trebuie încadrate corect ca financiar, nu confundate cu exploatarea.
- **Restul claselor 7x/6x** — tratate ca exploatare.
- **Contul 1012 (capital social)** și **1061 (rezervă existentă)** — intră direct în plafonul rezervei legale (min(5% × bază; 20% × capital social − rezervă existentă), CF art.26 alin.(1) lit.a)).
- **Contul 691 (cheltuială cu impozitul pe profit)** — dacă are sold debitor pozitiv și rândul de cheltuieli nedeductibile (P23) rămâne pe 0, aplicația emite avertisment de posibilă subevaluare a impozitului (CF art.25 alin.(4) lit.a)).

Separat, identitatea firmei trebuie să fie completă: CUI valid, denumire, adresă, cod CAEN pe 4 cifre — altfel „verificarea datelor înainte de generare (Declarații)” blochează generarea.

## Temeiul legal

::: ghid-temei
„Contribuabilul are dreptul la deducerea rezervelor și provizioanelor/ajustărilor pentru depreciere, numai în conformitate cu prezentul articol, astfel: a) rezerva legală este deductibilă în limita unei cote de 5% aplicate asupra profitului contabil, la care se adaugă cheltuielile cu impozitul pe profit, până ce aceasta va atinge a cincea parte din capitalul social subscris și vărsat sau din patrimoniu, după caz”
— Codul fiscal, art. 26 alin. (1) lit. a) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Următoarele cheltuieli nu sunt deductibile: a) cheltuielile proprii ale contribuabilului cu impozitul pe profit datorat, inclusiv cele reprezentând diferențe din anii precedenți sau din anul curent, precum și impozitele pe profit sau pe venit plătite în străinătate.”
— Codul fiscal, art. 25 alin. (4) lit. a) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

## Ce se greșește în practică

Verificarea superficială a acestor conturi — mai ales omiterea soldului 691 sau confuzia dintre clasele financiare și cele de exploatare — duce direct la erori în rezerva legală calculată automat sau la impozit subevaluat.

## Ce face iConta.eu

„preluarea datelor” citește automat toate aceste conturi din balanță. Rezerva legală se calculează automat dacă nu e dată manual, iar aplicația emite avertisment explicit pe contul 691.

[iConta.eu](/)
