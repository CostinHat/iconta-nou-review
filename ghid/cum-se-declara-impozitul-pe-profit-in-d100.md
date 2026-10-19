---
title: Cum se declară impozitul pe profit în D100?
description: Pentru firmele pe regim de profit, D100 declară trimestrial (trimestrele I-III) impozitul calculat pe baza profitului cumulat de la începutul anului, cu cotă de 16%.
published: 2026-09-22
modified: 2026-10-18
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
— sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282)

**OPANAF 587/2016, Anexa 4, Cap. I, pct. 1.2 lit. c):**
> „Trimestrial, pentru obligațiile de plată reprezentând: ... c) impozitul pe profit datorat de persoane
> juridice române și persoanele juridice străine, altele decât cele prevăzute la lit. a) și b), precum și
> de către persoanele juridice cu sediul social în România, înființate potrivit legislației europene
> (trimestrele I-III);"
— sursă: [OPANAF nr. 587/2016 pentru aprobarea modelului și conținutului formularelor utilizate pentru declararea impozitelor și taxelor cu regim de stabilire prin autoimpunere sau reținere la sursă](https://legislatie.just.ro/Public/DetaliiDocument/175662)

**CF art. 17:**
> „Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
— sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282)
:::

## Cum se calculează suma din D100 pentru trimestrele I-III

Legea (art. 41 alin. 1) și normele ANAF (OPANAF 587/2016, pct. 1.2 lit. c) limitează explicit declararea trimestrială prin D100 la trimestrele I-III; definitivarea și plata aferentă întregului an fiscal se face prin declarația anuală (D101, art. 42).

Baza nu se calculează izolat pe trimestru, ci **cumulat de la 1 ianuarie**: se stabilește impozitul de 16% pe rezultatul fiscal cumulat până la sfârșitul trimestrului, iar din el se scade impozitul deja declarat pe trimestrele anterioare ale anului. Practic, dacă un trimestru anterior a fost pe pierdere, iar trimestrul curent revine pe profit, se plătește impozit doar pe diferența cumulată, nu pe tot profitul trimestrului curent.

Dacă impozitul cumulat iese mai mic decât cel deja declarat — pierdere sau scădere a profitului —, D100 se depune totuși, cu 0 la impozitul pe profit: instrucțiunile formularului (OPANAF 587/2016, anexa 4, pct. 3.1.2) cer înscrierea cifrei 0 în această situație.

## Ce se greșește în practică

- Se calculează D100 pe profitul contabil, fără cheltuielile nedeductibile, veniturile neimpozabile și pierderea fiscală de recuperat — baza e rezultatul fiscal cumulat, nu profitul contabil.
- Se calculează impozitul trimestrial izolat, pe profitul strict al trimestrului, în loc de diferența față de profitul cumulat anterior.
- Se depune D100 pentru trimestrul IV cu formula standard (profit cumulat), deși legea rezervă D100 trimestrial doar pentru trimestrele I-III, iar trimestrul IV se regularizează prin D101.
- Nu se depune D100 pe un trimestru cu pierdere, pe motiv că nu e nimic de plată — declarația se depune și atunci, cu 0 la impozitul pe profit.

## Ce face iConta.eu

Pentru firmele cu regimul „profit” în vectorul fiscal, aplicația cere D100 (cod 103) pe trimestrele I, II și III, cu termen 25 a lunii următoare trimestrului: obligația apare în calendarul de termene, pe semafor și, după termen, la restanțe — inclusiv pe un trimestru cu pierdere, când se declară 0.

Suma de plată pornește de la rezultatul fiscal cumulat de la 1 ianuarie: veniturile minus cheltuielile din contabilitate, plus ajustările fiscale pe care le scrii, pe trimestrul în care s-au produs, în ecranul „Registrul de evidență fiscală” al firmei, secțiunea „Ajustări fiscale” (cheltuieli nedeductibile, venituri neimpozabile, deduceri), minus pierderea fiscală din anii anteriori, recuperată cel mult 70% (CF art. 31 alin. (1)). Din impozitul cumulat de 16% se scade ce s-a declarat deja pe trimestrele anterioare ale anului — inclusiv trimestrele declarate în programul folosit înainte de preluarea firmei, aduse cu suma lor în istoricul declarațiilor, la migrare. Dacă un trimestru anterior e consemnat ca depus, dar fără suma declarată, aplicația nu calculează D100 și îți cere să completezi suma în Migrare › Istoric declarații; nu presupune 0.

Pentru trimestrul IV, aplicația nu generează D100 pe impozitul pe profit: arată că trimestrul IV se definitivează în D101. Sistemul anual cu plăți anticipate (art. 41 alin. (2)) nu se alege în vectorul fiscal al firmei, deci aplicația aplică sistemul trimestrial descris mai sus; pentru o firmă care a optat pentru sistemul anual, plățile anticipate se stabilesc separat (vezi ghidul despre plățile anticipate 2026).

[iConta.eu](/)
