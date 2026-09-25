---
title: "Modificare vector fiscal: când și cum"
description: "Ce este vectorul fiscal al unei firme, când trebuie actualizat prin declarația de mențiuni și ce câmpuri gestionează efectiv iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Modificare vector fiscal: când și cum

Vectorul fiscal e ansamblul de obligații declarative pe care ANAF le asociază unei firme — regimul de TVA, periodicitatea declarațiilor, regimul de impozit (micro sau profit), obligația de a depune anumite declarații. Orice schimbare reală în activitatea firmei care afectează aceste obligații trebuie comunicată la ANAF, de regulă prin declarația de mențiuni, altfel vectorul fiscal rămâne neactualizat și declarațiile depuse nu se mai potrivesc cu ce așteaptă sistemul ANAF.

## Temeiul legal

::: ghid-temei
„(1) Modificările ulterioare ale datelor din declarația de înregistrare fiscală trebuie aduse la cunoștință organului fiscal central, în termen de 15 zile de la data producerii acestora, prin completarea și depunerea declarației de mențiuni. (2) în cazul modificărilor intervenite în datele declarate inițial și înscrise în certificatul de înregistrare fiscală, contribuabilul/plătitorul depune, odată cu declarația de mențiuni, și certificatul de înregistrare fiscală, în vederea anulării acestuia și eliberării unui nou certificat."
— Legea 207/2015, art. 88 alin. (1)-(2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Situații tipice care cer actualizarea vectorului fiscal:

- Trecerea de la regimul de microîntreprindere la impozit pe profit (sau invers, dacă legea permite revenirea), pentru că D100 și D101 sunt condiționate de regimul declarat la ANAF.
- Înregistrarea sau anularea calității de plătitor de TVA (art. 316 Cod fiscal) — declanșează sau oprește obligația de a depune D300, D390, D394.
- Schimbarea periodicității declarației de TVA (lunar/trimestrial), de regulă legată de cifra de afaceri sau de opțiunea contribuabilului.
- Angajarea sau disponibilizarea tuturor salariaților — afectează obligația de a depune D112.
- Fiecare astfel de modificare trebuie comunicată prin declarația de mențiuni (formularul 700 și variantele lui specifice), în termenul legal de 15 zile de la producerea evenimentului, nu doar reflectată intern în evidența contabilă.

## Ce se greșește în practică

- Se schimbă regimul fiscal (micro/profit) sau statutul de plătitor de TVA în evidența internă a firmei, fără să se depună și declarația de mențiuni la ANAF — vectorul fiscal oficial rămâne neschimbat, iar declarațiile depuse ulterior pot fi respinse sau semnalate ca inconsistente.
- Se depune declarația de mențiuni cu întârziere față de termenul de 15 zile, expunând firma la sancțiuni contravenționale pentru nedeclararea la timp a modificărilor.
- Se presupune că schimbarea vectorului fiscal produce efecte retroactive — de regulă modificările se aplică de la data comunicării sau de la data prevăzută expres de lege pentru fiecare tip de schimbare, nu retroactiv.

## Ce face iConta.eu

iConta.eu tratează vectorul fiscal ca pe o **afirmație declarată de utilizator**, nu ca pe o stare derivată automat din ANAF: regimul fiscal (micro/profit), statutul de plătitor de TVA, tipul de decont și periodicitatea se configurează manual în ecranul firmei, iar declarațiile generate (D100/D101, D300/D394/D390 etc.) urmează strict aceste setări. Motorul de scadențe (`core/control_fiscal_api.py`, funcția `declaratii_datorate`) semnalează ce declarații decurg din vectorul configurat, dar generatoarele individuale de declarații (`core/d100.py`, `core/d101.py`) nu refuză o declarație doar pentru că nu se potrivește regimului setat — nu există o astfel de validare încrucișată. Aplicația **nu depune ea însăși declarația de mențiuni la ANAF** și nu detectează automat momentul în care vectorul real al firmei ar trebui schimbat — actualizarea rămâne o decizie și o acțiune a contabilului, atât în aplicație, cât și la ANAF.

[iConta.eu](/)
