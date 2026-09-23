---
title: "Ce date din balanță trebuie verificate înainte de completarea D101?"
description: "Patru categorii de conturi din balanță condiționează direct corectitudinea D101: exploatare/financiar, capital, rezervă și impozit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce date din balanță trebuie verificate înainte de completarea D101?

Balanța pe care o citește motorul D101 trebuie verificată punctual pe câteva conturi-cheie, nu doar la nivel de total.

## Temeiul legal

::: ghid-temei
"`pull()` (liniile 448–467): citește profilul firmei + balanța, cu split exploatare/financiar (clasele 76/66 = financiar, restul 7x/6x = exploatare) și datele pentru rezerva legală (capital 1012, rezervă existentă 1061, cheltuială impozit 691)." — dosarul de cercetare F027, pe baza `core/d101.py`.
:::

Concret, de verificat înainte de completare:

- **Clasele 76/66** — trebuie încadrate corect ca financiar, nu confundate cu exploatarea.
- **Restul claselor 7x/6x** — tratate ca exploatare.
- **Contul 1012 (capital social)** și **1061 (rezervă existentă)** — intră direct în plafonul rezervei legale (min(5% × bază; 20% × capital social − rezervă existentă), CF art.26 alin.(1) lit.a)).
- **Contul 691 (cheltuială cu impozitul pe profit)** — dacă are sold debitor pozitiv și rândul de cheltuieli nedeductibile (P23) rămâne pe 0, aplicația emite avertisment de posibilă subevaluare a impozitului (CF art.25 alin.(4) lit.a)).

Separat, identitatea firmei trebuie să fie completă: CUI valid, denumire, adresă, cod CAEN pe 4 cifre — altfel `erori_generare` blochează generarea.

## Ce se greșește în practică

Verificarea superficială a acestor conturi — mai ales omiterea soldului 691 sau confuzia dintre clasele financiare și cele de exploatare — duce direct la erori în rezerva legală calculată automat sau la impozit subevaluat.

## Ce face iConta.eu

`pull()` citește automat toate aceste conturi din balanță. Rezerva legală se calculează automat dacă nu e dată manual, iar aplicația emite avertisment explicit pe contul 691.

[iConta.eu](/)
