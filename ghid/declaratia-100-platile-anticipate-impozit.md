---
title: "Declarația 100 pentru plățile anticipate de impozit pe profit"
description: "Firmele care optează pentru sistemul anual de declarare a impozitului pe profit plătesc trimestrial plăți anticipate, declarate prin formularul 100, iar impozitul se definitivează abia prin D101."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Declarația 100 pentru plățile anticipate de impozit pe profit

Firmele care optează pentru sistemul anual de impozit pe profit nu declară trimestrial un impozit calculat pe date reale, ca la sistemul trimestrial obișnuit — ele plătesc plăți anticipate, prin Declarația 100, iar definitivarea vine abia o dată pe an, prin D101.

## Temeiul legal

::: ghid-temei
„Contribuabilii, alții decât cei prevăzuți la alin. (4) și (5), pot opta pentru calculul, declararea și plata impozitului pe profit anual, cu plăți anticipate, efectuate trimestrial. Termenul până la care se efectuează plata impozitului anual este termenul de depunere a declarației privind impozitul pe profit, prevăzut la art. 42.
Opțiunea pentru sistemul anual de declarare și plată a impozitului pe profit se efectuează la începutul anului fiscal pentru care se solicită aplicarea prevederilor alin. (2). Opțiunea este obligatorie pentru cel puțin 2 ani fiscali consecutivi."
— Codul fiscal (Legea 227/2015), art. 41 alin. (2)-(3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce presupune, concret, sistemul anual cu plăți anticipate:

- Firma achită trimestrial o **plată anticipată** (nu impozitul real calculat pe profitul trimestrului), declarată prin formularul 100, iar impozitul definitiv se stabilește o singură dată, la definitivarea anuală, prin D101.
- Opțiunea pentru acest sistem se face la începutul anului fiscal și e obligatorie pentru **cel puțin 2 ani fiscali consecutivi** — nu se poate reveni la sistemul trimestrial obișnuit după un singur an, decât la expirarea acestei perioade minime.
- Ieșirea din sistemul anual, ca și intrarea, trebuie comunicată organelor fiscale până la 31 ianuarie inclusiv a anului fiscal respectiv (sau, pentru contribuabilii cu an fiscal modificat, în 30 de zile de la începutul acestuia).

## Ce se greșește în practică

- Se calculează plata anticipată trimestrială ca pe un impozit real pe profitul trimestrului, deși mecanismul e diferit — plata anticipată nu e supusă acelorași reguli de calcul ca impozitul trimestrial din sistemul obișnuit.
- Se renunță la sistemul anual după un singur an, ignorând obligativitatea de minimum 2 ani fiscali consecutivi.
- Se omite comunicarea către organul fiscal a opțiunii sau a ieșirii din sistemul anual, deși legea impune un termen explicit (31 ianuarie) pentru această notificare.

## Ce face iConta.eu

Declarația 100 este funcționalitate live în iConta.eu (F026): aplicația calculează cota pe perioadă, aplică proratizarea și generează XML-ul validat, folosită astăzi în principal pentru impozitul pe veniturile microîntreprinderilor. Pentru firmele în regim de profit, D100 (cod obligație 103) calculează automat suma de plată — dar pe baza formulei standard din sistemul trimestrial obișnuit (impozit cumulat de la 1 ianuarie, cu regularizare la fiecare trimestru, potrivit art. 41 alin. (1)), nu pe baza mecanismului specific de „plată anticipată" al sistemului anual opțional de la art. 41 alin. (2). Aplicația **nu distinge**, la această dată, firmele care au optat pentru sistemul anual — pentru acestea, suma calculată automat de D100 nu corespunde formulei legale a plății anticipate, iar corectarea sumei declarate (sau introducerea ei manuală, prin cota indicată contabilului) rămâne în sarcina contabilului.

[iConta.eu](/)
