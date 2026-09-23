---
title: Cum aplic TVA la încasare împreună cu taxarea inversă
description: Operațiunile cu taxare inversă nu intră niciodată în mecanismul TVA la încasare, chiar dacă firma e înscrisă în sistem — exigibilitatea lor rămâne la faptul generator, conform art. 282 alin. (6) Cod fiscal.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum aplic TVA la încasare împreună cu taxarea inversă

Fiind înscris în sistemul TVA la încasare nu înseamnă că absolut toate operațiunile firmei trec pe regimul de exigibilitate la încasare. Legea exclude explicit anumite categorii, iar taxarea inversă e cea mai frecventă dintre ele.

## Temeiul legal

::: ghid-temei
**Art. 282 alin. (6) CF** (rezumat din dosarul de cercetare): operațiunile supuse taxării inverse (art. 307 alin. (2)-(6) sau art. 331), livrările scutite, operațiunile din regimurile speciale (art. 311-313) și livrările către persoane afiliate (art. 7 pct. 26) sunt excluse din sistemul TVA la încasare, chiar dacă firma e înscrisă.

Comentariu verificat direct în codul sursă (`core/d300.py`), atașat exact acestei reguli: *„taxarea inversa e exigibila la faptul generator (art.282 alin.6 CF), NU la incasare: ramane pe calea de emitere ... chiar sub tva_la_incasare"*.
:::

## Ce înseamnă practic

Chiar dacă profilul firmei are activ regimul TVA la încasare, o achiziție sau livrare cu taxare inversă (de exemplu deșeuri, cereale, construcții — conform art. 307 alin. (2)-(6) sau art. 331) urmează regula ei proprie de exigibilitate — la faptul generator, exact ca într-un regim normal. Nu se amână nimic până la încasare sau plată.

Aceeași excludere se aplică livrărilor scutite de TVA, operațiunilor din regimurile speciale (art. 311-313, de regulă marjă) și livrărilor către persoane afiliate — toate rămân, din perspectiva exigibilității, în afara mecanismului de TVA la încasare, indiferent de statutul firmei în sistem.

## Ce se greșește în practică

- **Se presupune că toate operațiunile unei firme înscrise la TVA la încasare trec automat prin acest regim**, inclusiv cele cu taxare inversă. Art. 282 alin. (6) exclude explicit taxarea inversă.
- **Se amână greșit exigibilitatea unei achiziții/livrări cu taxare inversă** până la momentul plății/încasării, deși legea o leagă de faptul generator.
- **Se aplică excluderea doar pe livrări, uitând că include și livrările scutite, regimurile speciale (art. 311-313) și operațiunile către afiliați.**

## Ce face iConta.eu

`core/d300.py` tratează explicit taxarea inversă ca excepție de la mecanismul TVA la încasare: sumele aferente acestor operațiuni nu trec prin funcția de calcul al exigibilității la încasare (`tva_din_incasare()`), nici pentru firmele care au flag-ul `tva_la_incasare` activ pe profil — rămân pe calea normală de raportare, la faptul generator.

[iConta.eu](/)
