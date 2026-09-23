---
title: "Cum tratez TVA când furnizorul este din UE, dar bunurile sunt deja în România?"
description: "Dacă bunurile se aflau deja în România la momentul cumpărării, operațiunea nu e achiziție intracomunitară, indiferent de țara furnizorului — nu a existat transportul dintr-un stat membru în altul cerut de lege."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez TVA când furnizorul este din UE, dar bunurile sunt deja în România?

Naționalitatea furnizorului nu decide regimul de TVA — decide traseul fizic al bunurilor. Dacă marfa era deja în România când ai cumpărat-o, nu a existat achiziție intracomunitară, oricât de „european” ar arăta furnizorul pe factură.

## Temeiul legal

::: ghid-temei
„CF art. 268 alin. (1)-(3) lit. a) — Operațiuni impozabile; alin. (3) lit. a) — AIC de bunuri (altele decât mijloace de transport noi/accizabile) urmând unei LIC scutite.” — `cod_fiscal_227_2015_consolidat.txt` L16593-16626, dosarul F050.
:::

O achiziție intracomunitară presupune, prin definiție, o livrare intracomunitară „de partea cealaltă” — adică un transport de bunuri dintr-un stat membru către România. Dacă bunurile se aflau deja pe teritoriul românesc (de exemplu, furnizorul avea deja stoc aici), nu există acest transport, deci nu există nici achiziție intracomunitară — indiferent că furnizorul e o firmă înregistrată în alt stat membru.

## Ce se greșește în practică

- Se încadrează automat ca AIC orice factură de la un furnizor cu sediu în UE, fără să se verifice de unde a plecat efectiv marfa.
- Se cere furnizorului un cod de TVA străin și se așteaptă factură fără TVA, deși operațiunea reală e o livrare locală (dacă furnizorul e înregistrat și în România) sau alt tip de operațiune, nu o AIC.
- Se declară eronat operațiunea în D390 — o operațiune care nu e AIC nu are ce căuta acolo, iar partenerul nu are ce raporta simetric în statul lui.

## Ce face iConta.eu

Ecranul de achiziție intracomunitară din categoria „Extern” e gândit pentru operațiuni cu transport real dintr-un alt stat membru — cere cod TVA furnizor UE, valoare și tip (bunuri/servicii). Pentru o marfă deja aflată în România, operațiunea nu se introduce pe acest ecran; se tratează ca achiziție internă obișnuită, cu regimul de TVA aplicabil facturii primite.

[iConta.eu](/)
