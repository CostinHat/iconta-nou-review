---
title: "Cum corectez durata de amortizare stabilită greșit?"
description: "Câmpul de durată din registrul de mijloace fixe e liber și necontrolat față de catalogul legal — corectarea revine contabilului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez durata de amortizare stabilită greșit?

Durata normală de funcționare e un câmp introdus manual, fără verificare automată față de plajele legale din catalogul de clasificare — corectarea ei e simplă, dar responsabilitatea alegerii corecte rămâne integral a contabilului.

## Temeiul legal

::: ghid-temei
"pentru fiecare mijloc fix nou achiziționat se utilizează sistemul unor plaje de ani cuprinse între o valoare minimă și una maximă, existând astfel posibilitatea alegerii duratei normale de funcționare cuprinsă între aceste limite. Astfel stabilită, durata normală de funcționare a mijlocului fix rămâne neschimbată până la recuperarea integrală a valorii de intrare a acestuia sau scoaterea sa din funcțiune."
— HG 2139/2004, Catalogul privind clasificarea și duratele normale de funcționare a mijloacelor fixe, cap.II pct.4
:::

Legea permite alegerea duratei dintr-o plajă minim-maxim specifică fiecărei categorii de activ, iar odată stabilită, durata rămâne neschimbată pe toată perioada de amortizare. Dacă durata inițial introdusă e greșită (în afara plajei corecte pentru categoria activului), corectarea presupune actualizarea duratei în registru.

## Ce se greșește în practică

Greșeala tipică e introducerea unei durate "aproximative" sau preluate dintr-un alt activ similar, fără verificarea plajei corecte din catalog pentru categoria de clasificare specifică activului respectiv.

## Ce face iConta.eu

Câmpul de durată (`dnf_luni`) este complet liber, atât la introducere manuală, cât și la import — **catalogul de clasificare HG 2139/2004 nu este cablat în aplicație**, deci nu există lookup sau avertizare dacă durata aleasă e în afara plajei legale pentru categoria activului. Corectarea se face simplu, prin editarea directă a câmpului, dar verificarea corectitudinii duratei rămâne responsabilitatea contabilului.

[iConta.eu](/)
