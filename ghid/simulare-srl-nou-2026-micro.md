---
title: "Simulare: SRL nou 2026 pe micro vs profit"
description: "Ce compară de fapt o simulare micro vs. impozit pe profit pentru un SRL nou-înființat în 2026, și care sunt cele două cote de referință din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Simulare: SRL nou 2026 pe micro vs profit

Un SRL nou-înființat poate alege, în anumite condiții, între impozitul pe veniturile microîntreprinderilor (cotă unică asupra veniturilor totale) și impozitul pe profit (cotă asupra profitului net). O simulare corectă nu compară procentele izolat, ci baza de calcul: venituri totale, la micro, versus profit impozabil, la profit — iar cele două se pot îndepărta mult una de alta, în funcție de marja firmei.

## Temeiul legal

::: ghid-temei
„Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— Codul fiscal (Legea 227/2015), art. 51 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
— Codul fiscal (Legea 227/2015), art. 17 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce contează într-o simulare corectă:

- **Micro**: 1% aplicat asupra **veniturilor totale**, indiferent de cheltuieli sau profitabilitate — pentru o firmă cu marjă mare, poate fi mai avantajos; pentru una cu marjă mică sau pierdere, tot se plătește impozit, chiar dacă rezultatul e negativ.
- **Profit**: 16% aplicat asupra **profitului impozabil** (venituri minus cheltuieli deductibile, ajustat fiscal) — dacă firma nu are profit, nu se datorează impozit pe profit (deși poate exista impozit minim pe cifra de afaceri, pentru firmele mari, sau alte obligații).
- Încadrarea la micro nu e opțiune liberă necondiționată: trebuie îndeplinite condițiile de la art. 47 (plafon de venituri de 100.000 euro, structură a acționariatului, existența a cel puțin un salariat) — un SRL nou care nu le îndeplinește pornește direct pe profit, indiferent de ce ar arăta o simulare.
- O simulare la înființare trebuie să estimeze marja reală a afacerii (venituri minus cheltuieli), nu doar să compare 1% cu 16% ca procente abstracte — un SRL cu marjă de 10% plătește, la micro, un impozit echivalent cu 10% din profit (1% din venit = 10% din profitul de 10% din venit), nu 1% din profit.

## Ce se greșește în practică

- Se compară direct „1% vs. 16%" ca și cum ar fi cote aplicate aceleiași baze — sunt baze diferite, iar comparația corectă cere estimarea marjei.
- Se ignoră condițiile de eligibilitate la micro (art. 47) și se face simularea presupunând că firma poate alege liber oricare din cele două regimuri.
- Se omite faptul că opțiunea, odată aleasă la înființare sau la începutul anului fiscal, are reguli proprii de schimbare ulterioară — nu se poate trece de pe un regim pe altul oricând în cursul anului.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu am identificat în cod** un modul dedicat de simulare comparativă micro vs. profit pentru firme nou-înființate. Aplicația oferă evidența contabilă generală și generarea declarațiilor aferente ambelor regimuri (D100, D101 pentru profit) odată ce firma e configurată pe unul din ele — dar decizia de încadrare inițială, împreună cu simularea financiară care o susține, rămâne responsabilitatea contabilului sau a antreprenorului.

[iConta.eu](/)
