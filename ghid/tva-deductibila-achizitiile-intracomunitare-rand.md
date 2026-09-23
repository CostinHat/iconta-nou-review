---
title: "TVA deductibilă la achizițiile intracomunitare: rând în D300"
description: Pentru achizițiile intracomunitare de bunuri cu taxare inversă, rândul deductibil R18 se derivă automat din factură. Panoul manual din F251 intervine doar pentru regularizări (R19) sau când operațiunea n-a fost captată corect automat.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# TVA deductibilă la achizițiile intracomunitare: rând în D300

Rândul deductibil pentru achizițiile intracomunitare de bunuri cu taxare inversă e R18. În marea majoritate a cazurilor nu trebuie introdus manual — se derivă automat din factură. Mai jos, ce e automat, ce e manual și când intervine panoul F251.

## Temeiul legal

::: ghid-temei
„Achiziții intracomunitare de bunuri pentru care cumpărătorul este obligat la plată TVA (taxare inversă) — deductibil" — eticheta oficială a rândului R18, `d300_manual_api.py`, confirmată contra structurii ANAF D300 v12 (OPANAF 174/2026)
:::

## Ce se derivă automat

Pentru facturile de achiziție cu partener din UE (`tert_tara` în spațiul UE), motorul D300 derivă automat, fără nicio intervenție manuală: rd.5 colectat (`R5_1`/`R5_2`) și oglinda deductibilă rd.18 (`R18_1`/`R18_2`), la cota internă standard — mecanismul de taxare inversă (autolichidare) aplicat direct pe factura de achiziție.

## Ce e strict manual, prin F251

Rândul R19 — „Regularizări privind achizițiile intracomunitare de bunuri pentru care cumpărătorul este obligat la plată TVA (taxare inversă)" — apare doar în formula de însumare a taxei deduse (rd.27), niciodată ca țintă a unei atribuiri automate în motor. E 100% manual: orice regularizare ulterioară a unei achiziții IC deja înregistrate se introduce prin panoul F251, pe rândul R19.

## Fallback: când factura nu a captat corect operațiunea

Dacă achiziția intracomunitară nu a fost captată corect de nicio factură (partener fără CUI IC recunoscut, `tert_tara` sau clasificare lipsă), gărzile anti-dublă-numărare permit introducerea manuală a R18 (împreună cu oglinda colectată R5) prin F251 — dar **doar dacă** operațiunea nu a fost deja derivată automat din facturile perioadei. Dacă a fost, motorul ridică o eroare explicită de dublă numărare, care numește ambele surse.

## Ce se greșește în practică

- Se introduce manual R18 pentru o achiziție deja captată automat dintr-o factură cu partener UE — aplicația respinge cererea (eroare de câmp „rand"), pentru că ar dubla suma deja derivată.
- Se confundă R18 (rândul de bază, derivat automat) cu R19 (regularizarea lui, exclusiv manuală).

## Ce face iConta.eu

Motorul D300 derivă automat R5/R18 din facturile de achiziție cu partener din UE, la cota internă standard, fără intervenție manuală. Panoul F251 acoperă doar regularizările (R19) și cazurile de fallback în care operațiunea nu a fost captată corect automat — cu validare explicită împotriva dublei numărări față de ce a fost deja derivat din facturile perioadei.

[iConta.eu](/)
