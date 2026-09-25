---
title: "Micro pentru firmele care închiriază echipamente"
description: "Dacă o firmă care are ca activitate închirierea de echipamente se poate încadra la impozitul pe veniturile microîntreprinderilor, potrivit condițiilor din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Micro pentru firmele care închiriază echipamente

Nu există, în Codul fiscal actual, o excludere specifică pentru firmele de închiriere de echipamente — regimul micro se verifică prin aceleași condiții generale ca la orice altă activitate, nu prin natura obiectului de activitate.

## Temeiul legal

::: ghid-temei
„Nu intră sub incidența prezentului titlu următoarele persoane juridice române: [...] f) persoana juridică română care desfășoară activități în domeniul bancar; g) persoana juridică română care desfășoară activități în domeniul asigurărilor și reasigurărilor, al pieței de capital [...]; h) persoana juridică română care desfășoară activități în domeniul jocurilor de noroc; i) persoana juridică română care desfășoară activități de explorare, dezvoltare, exploatare a zăcămintelor de petrol și gaze naturale."
— Legea nr. 227/2015 (Codul fiscal), art. 47 alin. (3) lit. f)-i) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Lista completă de excludere de la regimul micro este limitativă și vizează domenii specifice (bancar, asigurări, piață de capital, jocuri de noroc, petrol și gaze) — închirierea de echipamente **nu se regăsește** printre ele. Consecința:

- O firmă care închiriază echipamente (utilaje, unelte, aparatură) poate aplica regimul micro dacă **îndeplinește condițiile generale** de la art. 47 alin. (1): venituri sub 100.000 euro, capital deținut de persoane private, cel puțin un salariat, situații financiare depuse la termen etc.
- Nu mai există, din 2025, o condiție separată legată de ponderea veniturilor din consultanță și management — acea literă a fost abrogată; firma trebuie evaluată doar prin condițiile actuale, aflate în vigoare.
- Riscul real pentru o firmă de închiriere nu ține de excludere din micro, ci de **plafonul de venituri**: dacă valoarea totală a chiriilor încasate depășește 100.000 euro în cursul anului, firma iese din micro începând cu trimestrul depășirii.

## Ce se greșește în practică

- Se caută excluderi vechi din Codul fiscal (de exemplu, legate de consultanță/management), care nu se mai aplică din 2025, și se refuză din start regimul micro pentru activități de închiriere fără temei actual.
- Se ignoră faptul că, la transferul unui mijloc fix (de exemplu, vânzarea unui echipament amortizat, uzual în business-ul de închiriere), veniturile din transfer se adaugă la cifra de afaceri dacă firma transferă mai mult de un activ dintr-o subgrupă în același an — cu impact asupra plafonului de 100.000 euro.
- Se presupune că orice activitate de „închiriere" se încadrează automat la o cotă de impozit diferită — regimul micro se aplică unitar, la cota generală, indiferent de sursa veniturilor, atâta timp cât nu apare o excludere explicită.

## Ce face iConta.eu

La data acestui ghid, iConta.eu urmărește regimul fiscal setat de contabil în profilul firmei (`core/vector_fiscal_api.py`) și generează declarațiile corespunzătoare, dar **nu evaluează automat** dacă o firmă din domeniul închirierii de echipamente îndeplinește condițiile de la art. 47 — inclusiv impactul veniturilor din transferul de mijloace fixe asupra plafonului de 100.000 euro. Verificarea eligibilității pentru regimul micro rămâne o analiză a contabilului, pe baza situației reale a firmei.

[iConta.eu](/)
