---
title: "Cum completez D101 pentru un SRL care a fost micro o parte din an?"
description: "D101 definitivează doar perioada în care firma a fost efectiv plătitoare de impozit pe profit, de la trimestrul depășirii plafonului micro."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum completez D101 pentru un SRL care a fost micro o parte din an?

Pentru un SRL care a fost microîntreprindere doar o parte din an, D101 nu definitivează întregul an fiscal, ci exclusiv perioada în care firma a devenit plătitoare de impozit pe profit.

## Temeiul legal

::: ghid-temei
"Art.52 alin.(1): «Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită.» Art.52 alin.(6): calculul și plata se efectuează luând în considerare veniturile și cheltuielile realizate începând cu trimestrul respectiv." — Legea 227/2015, citată în dosarul de cercetare F027.
:::

Practic: perioada de micro (declarată separat, prin D100 cu cod 121) rămâne în afara calculului de impozit pe profit; abia din trimestrul depășirii plafonului de 100.000 EUR venituri, firma intră sub incidența impozitului pe profit, iar plățile trimestriale aferente acestei perioade merg prin D100 (cod 103). D101, la finalul anului, definitivează doar acea porțiune a anului.

Dosarul de cercetare nu detaliază un câmp specific în interfața D101 pentru marcarea „perioadei parțiale" de profit — regula de mai sus e confirmată la nivel legal, dar mecanica exactă de completare în ecranul aplicației trebuie verificată direct în interfață.

## Ce se greșește în practică

Greșeala tipică e includerea în calculul D101 a veniturilor/cheltuielilor din perioada în care firma era încă la impozit micro, deși legea limitează clar baza de calcul la perioada de la trimestrul depășirii înainte.

## Ce face iConta.eu

`pull()` citește balanța firmei cu separarea standard financiar/exploatare. Pentru identificarea corectă a perioadei de profit din anul mixt, recomandăm verificarea manuală a datelor introduse în D101, conform regulii de la art.52.

[iConta.eu](/)
