---
title: "Consultare cu contabilul: micro sau profit în 2026"
description: "Diferența de cotă între impozitul pe veniturile microîntreprinderilor și impozitul pe profit în 2026, și condițiile care decid dacă o firmă poate alege regimul micro."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Consultare cu contabilul: micro sau profit în 2026

Alegerea între micro și profit nu mai este, din 2026, o discuție despre cote diferite pentru micro — există o singură cotă unică. Discuția reală e alta: firma respectă toate condițiile de eligibilitate, și dacă da, care regim e mai avantajos raportat la marja reală de profit.

## Temeiul legal

::: ghid-temei
„Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— Legea nr. 227/2015 (Codul fiscal), art. 51 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt), astfel cum a fost modificat prin OUG nr. 89/2025

„Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
— Legea nr. 227/2015 (Codul fiscal), art. 17 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă cifrele astea pentru decizie:

- La **micro**, impozitul de 1% se aplică la **venituri**, indiferent de profitabilitatea reală a firmei — o firmă cu marjă mică plătește impozit chiar dacă abia iese pe zero.
- La **profit**, impozitul de 16% se aplică la **profitul impozabil** (venituri minus cheltuieli deductibile) — o firmă fără profit real nu plătește impozit pe profit, dar cheltuielile nedeductibile pot umfla baza de impozitare.
- Eligibilitatea pentru micro rămâne condiționată cumulativ de criteriile de la art. 47: venituri sub 100.000 euro, capital deținut de persoane private, cel puțin un salariat, situații financiare depuse la termen, o singură microîntreprindere per grup de asociați cu peste 25% deținere.

## Ce se greșește în practică

- Se compară doar cotele (1% vs. 16%) fără să se raporteze la baza de calcul diferită — venituri versus profit impozabil — ceea ce poate duce la o concluzie greșită asupra regimului mai avantajos.
- Se ignoră faptul că regimul de profit poate fi, pentru firme cu marjă redusă sau pierdere, semnificativ mai avantajos, chiar dacă cota nominală pare mai mare.
- Se decide trecerea la profit „din mers", în cursul anului fiscal, deși legea permite opțiunea doar începând cu anul fiscal următor celui în care sunt îndeplinite/pierdute condițiile de eligibilitate, cu excepțiile de ieșire forțată de la art. 52.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează impozitul pe veniturile microîntreprinderilor (D100 trimestrial) și impozitul pe profit (D101 anual) în funcție de regimul fiscal setat de contabil în profilul firmei (`core/vector_fiscal_api.py`), folosind cotele curente în vigoare (1% micro, 16% profit). Aplicația **nu recomandă și nu simulează** automat care regim e mai avantajos pentru firmă — comparația între cele două scenarii, pe baza structurii reale de venituri și cheltuieli, rămâne o analiză pe care contabilul o face separat.

[iConta.eu](/)
