---
title: "Cum declar impozitul pe profit la un SRL proaspăt înființat"
description: "O firmă nou-înființată e obligată la sistemul trimestrial de impozit pe profit, cu definitivare anuală prin D101."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum declar impozitul pe profit la un SRL proaspăt înființat

Pentru un SRL nou-înființat, regula de bază nu e opțională: legea impune sistemul trimestrial, nu pe cel anual cu plăți anticipate.

## Temeiul legal

::: ghid-temei
"Art.41 alin.(6): sistemul trimestrial e obligatoriu (nu se poate opta pentru anual) pentru firme nou-înființate, cu pierdere fiscală anul precedent, în inactivitate temporară, sau foste plătitoare de impozit micro — în anul imediat următor schimbării." — Legea 227/2015 (Codul fiscal), art.41 alin.(6), citat în dosarul de cercetare F027 pe baza `anaf_surse/cod_fiscal_227_2015_consolidat.txt`.
:::

Concret: în primul an, un SRL nou-înființat nu poate alege sistemul anual cu plăți anticipate trimestriale (art.41 alin.(2)) — acea opțiune presupune, oricum, angajament minim de 2 ani fiscali consecutivi și comunicare la organul fiscal până la 31 ianuarie (art.41 alin.(3)), lucru imposibil pentru o firmă abia înființată.

Declararea și plata efectivă a impozitului pe profit trimestrial se fac prin D100, nu prin D101: codul bugetar 103 din nomenclatorul D100 (`core/d100.py`, `COD_BUGETAR`) corespunde exact „impozitului pe profit/plăților anticipate PJ române". D101 rămâne, în toate cazurile, exclusiv declarația ANUALĂ de definitivare.

## Ce se greșește în practică

Greșeala tipică e să se aștepte ca D101 să acopere și obligațiile trimestriale din primul an, sau să se încerce opțiunea pentru sistemul anual cu plăți anticipate, deși legea o exclude explicit pentru firmele nou-înființate.

## Ce face iConta.eu

Pentru definitivarea anuală, motorul D101 (`core/d101.py`) nu generează declarația fără date de identitate complete: CUI valid (verificat prin checksum), denumire, adresă și cod CAEN pe 4 cifre (`erori_generare`). Pentru trimestrele din cursul anului, declarația relevantă în aplicație este D100, cu codul de obligație 103.

[iConta.eu](/)
