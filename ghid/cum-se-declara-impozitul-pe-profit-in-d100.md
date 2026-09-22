---
title: Cum se declară impozitul pe profit în D100?
description: Pentru firmele pe regim de profit, D100 declară trimestrial (trimestrele I-III) impozitul calculat pe baza profitului cumulat de la începutul anului, cu cotă de 16%.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se declară impozitul pe profit în D100?

Declararea trimestrială prin D100 e regula standard pentru impozitul pe profit, distinctă atât de impozitul micro (cod 121), cât și de declarația anuală D101 care definitivează situația la finalul anului fiscal. Iată exact ce calculează și ce depune aplicația pentru o firmă pe regim „profit".

## Temeiul legal

::: ghid-temei
**CF art. 41 alin. (1):**
> „Calculul, declararea și plata impozitului pe profit, cu excepțiile prevăzute de prezentul articol, se
> efectuează trimestrial, până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III.
> Definitivarea și plata impozitului pe profit aferent anului fiscal respectiv se efectuează până la
> termenul de depunere a declarației privind impozitul pe profit prevăzut la art. 42."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt:4532-4534`

**OPANAF 587/2016, Anexa 4, Cap. I, pct. 1.2 lit. c):**
> „Trimestrial, pentru obligațiile de plată reprezentând: ... c) impozitul pe profit datorat de persoane
> juridice române și persoanele juridice străine, altele decât cele prevăzute la lit. a) și b), precum și
> de către persoanele juridice cu sediul social în România, înființate potrivit legislației europene
> (trimestrele I-III);"
— sursă: `anaf_surse/opanaf_587_2016_aprobarea_modelului_continutului_formularelor_utilizate.txt:927-930`

**CF art. 17:**
> „Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.html`
:::

## Cum se calculează suma din D100 pentru trimestrele I-III

Legea (art. 41 alin. 1) și normele ANAF (OPANAF 587/2016, pct. 1.2 lit. c) limitează explicit declararea trimestrială prin D100 la trimestrele I-III; definitivarea și plata aferentă întregului an fiscal se face prin declarația anuală (D101, art. 42).

Baza nu se calculează izolat pe trimestru, ci **cumulat de la 1 ianuarie**: `bază_trimestru = max(0, profit_cumulat_până_acum) − max(0, profit_cumulat_până_la_trimestrul_anterior)`, apoi se aplică cota de 16%. Practic, dacă un trimestru anterior a fost pe pierdere, iar trimestrul curent revine pe profit, se plătește impozit doar pe diferența cumulată, nu pe tot profitul trimestrului curent.

Dacă baza cumulată e ≤ 0 (pierdere), declarația nu se poate depune pe zero — sistemul refuză structural generarea, pentru că secțiunea `<obligatie>` e obligatorie în structura XML oficială a D100.

## Ce se greșește în practică

- Se așteaptă ca aplicația să reamintească automat obligația D100 pentru firmele pe profit, ca la firmele pe regim micro — nu se întâmplă (vezi mai jos).
- Se calculează impozitul trimestrial izolat, pe profitul strict al trimestrului, în loc de diferența față de profitul cumulat anterior.
- Se depune D100 pentru trimestrul IV cu formula standard (profit cumulat), deși legea rezervă D100 trimestrial doar pentru trimestrele I-III, iar trimestrul IV se regularizează prin D101.
- Se încearcă depunerea unei declarații pe pierdere, deși legea/structura ANAF nu permite un XML fără nicio obligație pozitivă.

## Ce face iConta.eu

`core/d100.py` calculează efectiv obligația cod 103 (impozit pe profit) pentru firmele pe regim „profit", cu bază cumulată de la 1 ianuarie, conform mecanismului descris mai sus. Totuși, în `core/control_fiscal_api.py`, semaforul de obligații/restanțe adaugă D100 la lista de urmărit **doar** pentru firmele pe regim „micro" (`_adauga_d100_micro`); pe ramura „profit" se adaugă automat numai D101, nu și D100. Aceasta e o neconformitate deschisă (R95, urmărită în registrul intern al proiectului): deși generatorul calculează corect obligația, o firmă pe profit nu vede D100 în lista de restanțe/obligații urmărite — trebuie generată manual, trimestrial, din ecranul de declarații, pentru trimestrele I-III.

Pentru trimestrul IV, existența unei obligații cod 103 generate cu formula standard e o zonă tratată diferit intern față de regimul opțional cu plăți anticipate (vezi ghidul despre plățile anticipate 2026) — dacă firma dvs. se încadrează la un regim special, verificați suplimentar cu contabilul acest caz.

[iConta.eu](/)
