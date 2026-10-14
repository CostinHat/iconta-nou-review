---
title: "Cum declar achizițiile intracomunitare în D300?"
description: Achizițiile intracomunitare de bunuri și servicii se derivă automat din facturile cu partener UE. Panoul manual „Rând manual D300” intervine doar pentru regularizări (rândurile 6, 8, 21 și 23) sau când operațiunea n-a fost captată corect automat.
published: 2026-09-23
modified: 2026-10-13
poarta: v1
---

# Cum declar achizițiile intracomunitare în D300?

Achizițiile intracomunitare, cu taxare inversă pentru bunuri sau pentru servicii, nu se declară manual în cazul normal — motorul D300 le derivă direct din facturi. Panoul manual „Rând manual D300” acoperă doar regularizările și situațiile în care o factură nu a fost captată corect.

## Temeiul legal

::: ghid-temei
„persoana impozabilă înregistrată conform art. 316 va evidenția în decontul prevăzut la art. 323, atât ca taxă colectată, cât și ca taxă deductibilă, în limitele și în condițiile stabilite la art. 297-301, taxa aferentă achizițiilor intracomunitare, bunurilor și serviciilor achiziționate în beneficiul său, pentru care respectiva persoană este obligată la plata taxei, în condițiile prevăzute la art. 307 alin. (2)-(6).”
— Codul fiscal, art. 326 alin. (2) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Datele înscrise incorect într-un decont de taxă se pot corecta prin decontul unei perioade fiscale ulterioare și se vor înscrie la rândurile de regularizări.”
— Codul fiscal, art. 323 alin. (3) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

## Ce se derivă automat

Pentru facturile de achiziție cu partener din UE („țara partenerului” în spațiul UE), motorul derivă automat:

- **achiziție de bunuri din UE cu autolichidare** → rândul 5 colectat (valoare și TVA) + rândul 20 deductibil oglindă (valoare și TVA), la cota internă standard;
- **achiziție de servicii intracomunitare** (dacă tipul din D390 e „S") → rândul 7 colectat + rândul 22 deductibil oglindă (net zero).

## Ce e strict manual, prin „Rând manual D300”

Rândurile de regularizare a acestor achiziții — **rândul 6** („Regularizări privind achizițiile intracomunitare de bunuri pentru care cumpărătorul este obligat la plată TVA") și **rândul 8** (regularizări achiziții servicii intracomunitare), cu oglinzile lor deductibile **rândul 21** și **rândul 23** — apar, în motorul D300, doar în formulele de însumare (rândurile 19 și 30, totalurile de taxă colectată și deductibilă), niciodată ca țintă a unei atribuiri automate. Sunt 100% manuale.

## Fallback: când factura nu a captat corect operațiunea

Dacă achiziția intracomunitară nu a fost captată corect de nicio factură (partener fără CUI IC recunoscut, „țara partenerului” sau clasificare lipsă), gărzile anti-dublă-numărare permit introducerea manuală a rândurilor 5/20 sau 7/22 prin „Rând manual D300” — dar **doar dacă** operațiunea nu a fost deja derivată automat din facturile perioadei. Dacă a fost, motorul ridică o eroare explicită de dublă numărare.

## Ce se greșește în practică

Se introduce manual rândurile 5/20 sau 7/22 pentru o achiziție deja captată automat dintr-o factură cu partener UE — aplicația respinge cererea, pentru că ar dubla suma deja derivată.

## Ce face iConta.eu

Motorul D300 derivă automat rândurile 5/7 (colectat) și oglinzile deductibile 20/22 din facturile de achiziție cu partener din UE, folosind și clasificarea bun/serviciu din D390. Panoul „Rând manual D300” acoperă doar regularizările (rândurile 6, 8, 21 și 23) și cazurile de fallback în care operațiunea nu a fost captată corect automat, cu validare împotriva dublei numărări.

[iConta.eu](/)
