---
title: "Cum declar achizițiile intracomunitare în D300?"
description: Achizițiile intracomunitare de bunuri și servicii se derivă automat din facturile cu partener UE. Panoul manual F251 intervine doar pentru regularizări (R6/R8/R19/R21) sau când operațiunea n-a fost captată corect automat.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum declar achizițiile intracomunitare în D300?

Achizițiile intracomunitare, cu taxare inversă pentru bunuri sau pentru servicii, nu se declară manual în cazul normal — motorul D300 le derivă direct din facturi. Panoul manual F251 acoperă doar regularizările și situațiile în care o factură nu a fost captată corect.

## Temeiul legal

::: ghid-temei
„Achiziții intracomunitare de bunuri pentru care cumpărătorul este obligat la plată TVA (taxare inversă)" — eticheta oficială a rândului R5, `d300_manual_api.py`, confirmată contra structurii ANAF D300 v12 (OPANAF 174/2026)
:::

## Ce se derivă automat

Pentru facturile de achiziție cu partener din UE (`tert_tara` în spațiul UE), motorul derivă automat:

- **achiziție de bunuri din UE cu autolichidare** → rd.5 colectat (`R5_1`/`R5_2`) + rd.18 deductibil oglindă (`R18_1`/`R18_2`), la cota internă standard;
- **achiziție de servicii intracomunitare** (dacă tipul din D390 e „S") → rd.7 colectat + rd.20 deductibil oglindă (net zero).

## Ce e strict manual, prin F251

Rândurile de regularizare a acestor achiziții — **R6** („Regularizări privind achizițiile intracomunitare de bunuri pentru care cumpărătorul este obligat la plată TVA") și **R8** (regularizări achiziții servicii intracomunitare), cu oglinzile lor deductibile **R19** și **R21** — apar, în motorul D300, doar în formulele de însumare (rd.17/rd.27), niciodată ca țintă a unei atribuiri automate. Sunt 100% manuale.

## Fallback: când factura nu a captat corect operațiunea

Dacă achiziția intracomunitară nu a fost captată corect de nicio factură (partener fără CUI IC recunoscut, `tert_tara` sau clasificare lipsă), gărzile anti-dublă-numărare permit introducerea manuală a R5/R18 sau R7/R20 prin F251 — dar **doar dacă** operațiunea nu a fost deja derivată automat din facturile perioadei. Dacă a fost, motorul ridică o eroare explicită de dublă numărare.

## Ce se greșește în practică

Se introduce manual R5/R18 sau R7/R20 pentru o achiziție deja captată automat dintr-o factură cu partener UE — aplicația respinge cererea, pentru că ar dubla suma deja derivată.

## Ce face iConta.eu

Motorul D300 derivă automat rd.5/rd.7 (colectat) și oglinzile deductibile rd.18/rd.20 din facturile de achiziție cu partener din UE, folosind și clasificarea bun/serviciu din D390. Panoul F251 acoperă doar regularizările (R6/R8/R19/R21) și cazurile de fallback în care operațiunea nu a fost captată corect automat, cu validare împotriva dublei numărări.

[iConta.eu](/)
