---
title: "Cum calculez rezultatul fiscal pornind de la balanța contabilă?"
description: "Rezultatul fiscal pornește din balanță, dar amortizarea, rezerva legală și contul 691 cer intervenție manuală atentă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum calculez rezultatul fiscal pornind de la balanța contabilă?

Calculul rezultatului fiscal în D101 pornește din balanță, dar nu se oprește la citirea automată a conturilor — câteva ajustări rămân, explicit, în sarcina contabilului.

## Temeiul legal

::: ghid-temei
"D101 tratează amortizarea ca INTRARE, nu o calculează — P11 = amortizare fiscală (deducere, intră în P16 total deduceri, reduce profitul impozabil), P2x/P28-tip = cheltuiala cu amortizarea contabilă (intră în rollup-ul P34 «cheltuieli nedeductibile», se adaugă înapoi la baza impozabilă). Contabilul introduce manual ambele valori." — dosarul de cercetare F027, pe baza `core/d101.py` și `calcul_d101`.
:::

Punctul de plecare este `pull()` (liniile 448–467), care citește balanța cu separarea clasică: conturile 76/66 ca financiar, restul 7x/6x ca exploatare. Din același pas se preiau și datele pentru rezerva legală: capitalul social (1012), rezerva existentă (1061) și cheltuiala cu impozitul pe profit (cont 691) — aceasta din urmă e și sursa avertismentului de nedeductibilitate dacă rândul P23 rămâne pe 0.

## Ce se greșește în practică

Cea mai frecventă greșeală e să se aștepte ca aplicația să calculeze singură amortizarea fiscală și add-back-ul contabil — ambele sunt intrări manuale, nu rezultate automate ale citirii balanței.

## Ce face iConta.eu

`pull()` aduce automat conturile relevante din balanță. Rezerva legală (P13) se calculează automat dacă nu e introdusă manual, plafonată conform CF art.26 alin.(1) lit.a). Amortizarea fiscală și add-back-ul contabil al amortizării rămân, în schimb, valori introduse manual de contabil.

[iConta.eu](/)
