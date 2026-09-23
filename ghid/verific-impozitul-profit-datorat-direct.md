---
title: "Cum verific impozitul pe profit datorat direct din balanță?"
description: "Balanța conține semnalele care pot arăta o subevaluare a impozitului pe profit, mai ales prin soldul contului 691."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific impozitul pe profit datorat direct din balanță?

O parte din verificarea impozitului pe profit se poate face direct din balanță, înainte chiar de completarea propriu-zisă a D101.

## Temeiul legal

::: ghid-temei
"Avertisment cont 691 [...]: dacă soldul debitor al contului 691 (cheltuială cu impozitul pe profit) e >0 și rd.23 (P23, cheltuieli nedeductibile) e 0, se emite avertisment — cheltuiala e nedeductibilă (CF art.25 alin.(4) lit.a) și trebuie adăugată înapoi, altfel impozitul declarat iese subevaluat." — dosarul de cercetare F027, pe baza `core/d101.py` liniile 502–529.
:::

Semnalul cel mai direct din balanță e soldul contului 691: dacă e debitor și pozitiv, dar rândul de cheltuieli nedeductibile din declarație rămâne pe 0, există un risc concret de subevaluare a impozitului — confirmat pe un portofoliu monitorizat, unde omisiunea a redus impozitul declarat cu 2.432 lei fără niciun avertisment înainte de introducerea acestui gard.

Pe lângă acest semnal, `pull()` citește din balanță și conturile relevante pentru rezerva legală (1012 capital social, 1061 rezervă existentă) și separarea clasică financiar (76/66) versus exploatare (7x/6x), plus validările de plafoane V1–V7 pentru credite fiscale, sponsorizare și reduceri.

## Ce se greșește în practică

Greșeala tipică e verificarea doar a rezultatului contabil final, fără a urmări explicit soldul contului 691 și corelarea lui cu rândul de cheltuieli nedeductibile din declarație.

## Ce face iConta.eu

Aplicația citește automat balanța prin `pull()` și emite avertisment explicit dacă soldul contului 691 indică o posibilă subevaluare a impozitului.

[iConta.eu](/)
