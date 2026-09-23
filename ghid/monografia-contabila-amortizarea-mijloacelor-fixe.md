---
title: "Care este monografia contabilă pentru amortizarea mijloacelor fixe?"
description: "iConta.eu generează automat nota lunară de amortizare pe baza contului de amortizare configurat pe fiecare activ, pe metoda reală a acestuia."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Care este monografia contabilă pentru amortizarea mijloacelor fixe?

Fiecare mijloc fix din registru are asociat, pe lângă contul de imobilizare, și un cont de amortizare propriu — folosit la generarea automată a notei lunare.

## Temeiul legal

::: ghid-temei
"În cazul metodei de amortizare liniară, amortizarea se stabilește prin aplicarea cotei de amortizare liniară la valoarea fiscală de la data intrării în patrimoniul contribuabilului a mijlocului fix amortizabil." — Codul fiscal, art. 28 alin. (6)
:::

Suma înregistrată lunar e cheltuiala cu amortizarea corespunzătoare ratei calculate pe metoda reală a activului, creditată în contul de amortizare cumulată configurat pentru acel activ.

## Ce se greșește în practică

Se presupune că există un singur cont "standard" de amortizare folosit pentru toate activele, ignorând că fiecare mijloc fix are propriul cont de amortizare, introdus separat în registru.

## Ce face iConta.eu

Contul de amortizare nu e hardcodat pentru mijloacele fixe corporale — e un câmp introdus de contabil la import sau la înregistrarea activului, alături de contul de imobilizare. Motorul unic de amortizare calculează suma lunară pe metoda reală a activului, iar nota generată folosește contul de amortizare configurat pe acel activ. Spre deosebire de notele de casare și reevaluare, care sunt ciorne validate separat din Registrul jurnal, nota lunară de amortizare e înregistrată direct cu status „validată" — amortizarea lunii intră direct în contabilitate.

[iConta.eu](/)
