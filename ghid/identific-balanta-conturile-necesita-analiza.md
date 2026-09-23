---
title: "Cum identific din balanță conturile care necesită analiză fiscală?"
description: "Patru categorii de conturi din balanță cer atenție fiscală explicită la completarea D101: exploatare/financiar, capital, rezervă și impozitul pe profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum identific din balanță conturile care necesită analiză fiscală?

Nu toate conturile din balanță au același impact asupra D101 — câteva grupuri cer verificare fiscală explicită.

## Temeiul legal

::: ghid-temei
"`pull()` [...] citește profilul firmei + balanța, cu split exploatare/financiar (clasele 76/66 = financiar, restul 7x/6x = exploatare) și datele pentru rezerva legală (capital 1012, rezervă existentă 1061, cheltuială impozit 691)." — dosarul de cercetare F027, pe baza `core/d101.py`.
:::

Cele patru grupuri de urmărit:

1. **76/66 (financiar)** vs. **7x/6x (exploatare)** — separarea corectă condiționează rulajul folosit în calculul rezultatului fiscal.
2. **1012 (capital social)** — intră direct în plafonul rezervei legale (min(5% × bază; 20% × capital social − rezervă existentă), CF art.26 alin.(1) lit.a)).
3. **1061 (rezervă existentă)** — se scade din 20% din capitalul social la determinarea plafonului rezervei legale.
4. **691 (cheltuială cu impozitul pe profit)** — dacă are sold debitor pozitiv și rândul de cheltuieli nedeductibile (P23) rămâne pe 0, aplicația avertizează asupra unei posibile subevaluări a impozitului (CF art.25 alin.(4) lit.a)).

## Ce se greșește în practică

Analiza fiscală superficială a balanței — tratarea tuturor conturilor la fel, fără separarea explicită financiar/exploatare și fără urmărirea soldului contului 691 — este cauza principală a erorilor de calcul semnalate în aplicație.

## Ce face iConta.eu

`pull()` citește automat aceste conturi din balanță. Rezerva legală se calculează automat dacă nu e introdusă manual, iar aplicația emite avertisment explicit pe contul 691 când semnalează un risc de subevaluare.

[iConta.eu](/)
