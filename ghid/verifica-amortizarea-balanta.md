---
title: "Cum se verifică amortizarea din balanță?"
description: "iConta.eu poate refuza o operațiune (reevaluarea) dacă soldul contabil real al amortizării e mai mic decât ce calculează registrul — cum funcționează verificarea."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se verifică amortizarea din balanță?

Soldul din balanță al contului de amortizare cumulată ar trebui să corespundă cu ce calculează registrul de mijloace fixe la aceeași dată — dacă nu corespunde, aplicația are un mecanism care semnalează problema în anumite operațiuni.

## Temeiul legal

::: ghid-temei
"La reevaluarea unei imobilizări corporale, amortizarea cumulată la data reevaluării este tratată în unul din următoarele moduri: [...] b) eliminată din valoarea contabilă brută a activului și valoarea netă, determinată în urma corectării cu ajustările de valoare, este recalculată la valoarea reevaluată a activului. Această metodă este folosită, deseori, pentru clădirile care sunt reevaluate la valoarea lor de piață." — OMFP 1802/2014, pct. 103 lit. b)
:::

La reevaluare, aplicația compară explicit soldul contabil real al contului de amortizare cu ce calculează registrul pentru activul respectiv.

## Ce se greșește în practică

Se reevaluează un activ fără ca notele lunare de amortizare aferente să fi fost validate deja în Registrul jurnal — soldul contabil real rămâne astfel în urmă față de ce calculează registrul.

## Ce face iConta.eu

La reevaluarea unui mijloc fix, aplicația **refuză** operațiunea dacă soldul contabil real al contului de amortizare e mai mic decât ce calculează registrul — motivul: reevaluarea ar elimina o amortizare care nu e încă înregistrată contabil, iar contul de amortizare ar deveni negativ silențios. Aceasta e singura verificare explicită de tip "registru vs. balanță" descrisă pentru mijloacele fixe — nu există un ecran dedicat separat de comparare a soldurilor în afara acestui context.

[iConta.eu](/)
