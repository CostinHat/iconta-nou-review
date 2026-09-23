---
title: "Cum calculez impozitul pe profit pentru o firmă nou-înființată?"
description: "Firmele nou-înființate sunt obligate la sistemul trimestrial de calcul al impozitului pe profit, fără posibilitate de opțiune pentru sistemul anual."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum calculez impozitul pe profit pentru o firmă nou-înființată?

Pentru o firmă nou-înființată, legea exclude explicit opțiunea pentru sistemul anual cu plăți anticipate — calculul se face obligatoriu trimestrial.

## Temeiul legal

::: ghid-temei
"Art.41 alin.(6): sistemul trimestrial e obligatoriu (nu se poate opta pentru anual) pentru firme nou-înființate, cu pierdere fiscală anul precedent, în inactivitate temporară, sau foste plătitoare de impozit micro — în anul imediat următor schimbării." — Legea 227/2015, citată în dosarul de cercetare F027.
:::

Calculul, declararea și plata se fac trimestrial, până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I–III (art.41 alin.(1)), prin D100 (cod de obligație 103, conform `COD_BUGETAR` din `core/d100.py`). Cota aplicată este cea standard de 16% (art.17), pe profitul impozabil realizat.

## Ce se greșește în practică

Greșeala tipică e încercarea de a opta pentru sistemul anual cu plăți anticipate în primul an de activitate — art.41 alin.(6) exclude explicit această opțiune pentru firmele nou-înființate.

## Ce face iConta.eu

Calculul trimestrial se declară prin D100. D101 rămâne, și pentru o firmă nou-înființată, exclusiv declarația anuală de definitivare, condiționată de completarea corectă a datelor de identitate (CUI, denumire, adresă, cod CAEN pe 4 cifre).

[iConta.eu](/)
