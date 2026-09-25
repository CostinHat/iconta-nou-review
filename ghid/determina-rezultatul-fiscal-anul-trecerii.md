---
title: "Cum se determină rezultatul fiscal în anul trecerii de la micro la profit?"
description: "Ce declanșează trecerea obligatorie de la impozitul pe veniturile microîntreprinderilor la impozitul pe profit în cursul anului și de la ce trimestru se calculează rezultatul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se determină rezultatul fiscal în anul trecerii de la micro la profit?

Trecerea de la microîntreprindere la impozit pe profit nu așteaptă întotdeauna finalul anului fiscal — legea prevede situații în care obligația de a plăti impozit pe profit apare chiar în cursul anului, de la un trimestru anume, iar rezultatul fiscal se calculează separat, de la acel moment.

## Temeiul legal

::: ghid-temei
„ART. 52 Reguli de ieșire din sistemul de impunere pe veniturile microîntreprinderilor în cursul anului
(1) Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită.
(2) În cazul în care, în cursul unui an fiscal, o microîntreprindere nu a depus în termen situațiile financiare anuale pentru exercițiul financiar precedent anului fiscal respectiv, dacă avea această obligație potrivit legii, microîntreprinderea datorează impozit pe profit începând cu trimestrul în care nu mai este îndeplinită această condiție.
(3) În cazul în care, în cursul unui an fiscal, o microîntreprindere nu mai îndeplinește condiția prevăzută la art. 47 alin. (1) lit. g) [are cel puțin un salariat], microîntreprinderea datorează impozit pe profit începând cu trimestrul următor celui în care a încetat raportul de muncă. [...] În cazul în care, în acest termen [30 de zile] nu se angajează un nou salariat, microîntreprinderea datorează impozit pe profit începând cu trimestrul următor celui în care a încetat raportul de muncă."
— Legea 227/2015 (Codul fiscal), art. 52 alin. (1), (2), (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă asta pentru rezultatul fiscal:

- Momentul trecerii la profit nu e 1 ianuarie al anului următor, ci **trimestrul** în care s-a produs evenimentul declanșator: depășirea plafonului de 100.000 euro, nedepunerea la termen a situațiilor financiare anuale, sau pierderea condiției de „cel puțin un salariat" (fără angajare de înlocuire în 30 de zile).
- De la acel trimestru, firma trece la calculul impozitului pe profit (venituri minus cheltuieli deductibile, cu ajustările fiscale specifice titlului II din Codul fiscal), în timp ce pentru trimestrele anterioare rămâne aplicat impozitul pe veniturile microîntreprinderii, calculat separat.
- Limitele fiscale (plafonul de 100.000 euro) se verifică **cumulat de la începutul anului fiscal**, nu doar pe trimestrul curent — deci depășirea se constată prin însumarea veniturilor de la 1 ianuarie.

## Ce se greșește în practică

- Se așteaptă finalul anului fiscal pentru a face trecerea la profit, deși evenimentul declanșator (depășirea plafonului, pierderea salariatului) a avut loc cu câteva trimestre mai devreme.
- Se calculează plafonul de 100.000 euro doar pe trimestrul în care pare depășit, în loc de cumulat de la 1 ianuarie, ceea ce poate întârzia sau grăbi greșit momentul trecerii.
- Se ignoră excepția de 30 de zile pentru înlocuirea salariatului: dacă noul salariat e angajat în acest termen, condiția rămâne îndeplinită și nu se declanșează trecerea la profit.

## Ce face iConta.eu

iConta.eu ține evidența regimului fiscal declarat al firmei (micro sau profit) și, pe baza vectorului fiscal, generează planul de declarații datorate corespunzător (D100 pentru ambele regimuri, D101 doar pentru impozitul pe profit). Aplicația nu detectează însă automat, din veniturile înregistrate, momentul exact al depășirii plafonului de 100.000 euro sau al pierderii condiției de salariat, pentru a declanșa ea însăși schimbarea de regim — verificarea condițiilor de ieșire din sistemul micro și decizia de a comunica organului fiscal trecerea la profit rămân responsabilitatea contabilului, pe baza datelor din aplicație.

[iConta.eu](/)
