---
title: D205 pentru dividende plătite în valută
description: D205 se completează în lei, iar conversia unui dividend plătit în valută se face la nivelul înregistrării contabile, nu în declarație. Ce anume nu e o particularitate a D205 și de ce.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# D205 pentru dividende plătite în valută

Un dividend poate fi, în anumite situații, plătit în valută (de exemplu unui beneficiar din străinătate sau prin convenție expresă). Din perspectiva D205 însă, formularul nu are un regim separat pentru "dividende în valută" — declarația se completează în lei, iar suma în valută trebuie deja convertită înainte de a ajunge la baza de impozitare raportată.

## Temeiul legal

::: ghid-temei
"(7) Veniturile sub formă de dividende, inclusiv câștigul obținut ca urmare a deținerii de titluri de participare definite de legislația în materie la organisme de plasament colectiv, se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final."
— Codul fiscal, Legea 227/2015, art. 97 alin. (7)
:::

Textul de lege vorbește de "suma" dividendului, fără nicio mențiune despre monedă — cota de impozitare (16%/10%/8%/5%, în funcție de perioadă) se aplică indiferent de moneda în care e exprimat dividendul. Cercetarea care stă la baza acestui ghid nu a identificat, în structura oficială a D205, în instrucțiunile ei de completare sau în codul funcționalității F029, nicio regulă specifică de conversie valutară (curs aplicabil, dată de referință) — declarăm explicit acest gol, ca să nu inventăm o regulă pe care nu o putem susține cu o sursă verificată. Conversia unei sume în valută la lei, pentru orice operațiune contabilă, urmează regulile generale de contabilitate, nu o regulă specifică D205.

## Ce se greșește în practică

- Se raportează în D205 suma în valuta originală a plății, netradusă în lei — declarația oficială nu are câmpuri în altă monedă decât leul.
- Se caută în D205 un mecanism dedicat pentru dividende în valută — nu există; din perspectiva declarației, un dividend plătit în valută nu diferă structural de unul plătit în lei, odată ce suma e exprimată corect în lei.
- Se amână conversia valutară până la generarea D205, deși ea trebuie deja făcută la momentul înregistrării contabile a plății (contul 457), înainte ca suma să ajungă în declarație.

## Ce face iConta.eu

Motorul de generare D205 din iConta.eu (`core/d205.py`) preia direct sumele deja înregistrate în lei din contul 457 (distribuit/plătit), pe notele contabile validate — nu efectuează el însuși nicio conversie valutară și nu conține o regulă de curs specifică dividendelor. Dacă un dividend a fost plătit în valută, conversia la lei trebuie făcută corect la momentul înregistrării notei contabile de plată; D205 preia, ca pentru orice altă operațiune, suma deja exprimată în lei din acea notă.

[iConta.eu](/)
