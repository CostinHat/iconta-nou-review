---
title: Cum țin evidența diferențelor dintre provizioanele contabile și cele fiscale?
description: Fiindcă motorul contabil nu leagă automat notele de provizioane de rândurile nedeductibile din D101, e nevoie de un registru propriu (contabil, sold, procent/temei de deducere, tratament la reluare) pentru fiecare provizion, care să susțină atât declarația curentă, cât și impozitarea corectă la reluare.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum țin evidența diferențelor dintre provizioanele contabile și cele fiscale?

Provizioanele generează sistematic diferențe între rezultatul contabil și rezultatul fiscal: unele nu se deduc deloc, altele se deduc parțial, iar tratamentul de la reluare depinde de ce s-a întâmplat la constituire. Fără o evidență separată, aceste diferențe sunt ușor de pierdut, mai ales când constituirea și reluarea au loc în exerciții financiare diferite.

## Temeiul legal

::: ghid-temei
"cheltuielile cu provizioane/ajustări pentru depreciere și rezerve, în limita prevăzută la art. 26;"

"Reducerea sau anularea oricărui provizion ori a rezervei care a fost anterior dedusă, inclusiv
rezerva legală, se include în rezultatul fiscal, ca venituri impozabile sau elemente similare
veniturilor, indiferent dacă reducerea sau anularea este datorată modificării destinației
provizionului sau a rezervei, distribuirii provizionului sau rezervei către participanți sub orice
formă, lichidării, divizării sub orice formă, fuziunii contribuabilului sau oricărui altui motiv."

"d) [...] veniturile din reducerea sau anularea provizioanelor pentru care nu s-a acordat
deducere, [...]"
:::

## Ce trebuie să conțină evidența

Pentru fiecare provizion sau ajustare constituită, o evidență minimă trebuie să rețină:

- **contul și tipul** (1511 litigii, 1512 garanții, 1513 dezafectare, 1514 restructurare, 1516 impozite, 1518 altele, 491 ajustare creanțe, 39x ajustare stocuri);
- **suma constituită contabil** și data constituirii;
- **procentul/suma dedusă fiscal** la constituire (0%, 30%, 100%, sau cota contractuală de garanție) și temeiul legal aplicat;
- **suma nedeductibilă**, transferată în rândurile corespunzătoare din D101 la momentul constituirii;
- **tratamentul preconizat la reluare** — dacă provizionul e (parțial) dedus, reluarea va genera venit impozabil în limita sumei deduse; dacă e nededus, reluarea va fi venit neimpozabil.

Această evidență e cea care, la reluare, îți spune rapid dacă tratezi venitul din 7812/7814 ca impozabil sau neimpozabil, fără să reiei analiza de la zero.

::: ghid-exemplu
Registru simplificat pentru un provizion de garanții de 6.000 lei, dedus integral (cotă contractuală 100% acoperitoare): la constituire, 0 lei nedeductibil în D101; la reluare, 6.000 lei venit impozabil. Pentru un provizion de litigii de 12.000 lei, nedeductibil integral: la constituire, 12.000 lei trecuți în D101 ca nedeductibili; la reluare, 12.000 lei venit neimpozabil.
:::

## Ce se greșește în practică

- Se ține evidența doar a soldurilor conturilor 151/491/39x, fără informația de procent/temei de deducere aplicat la constituire — informație esențială pentru tratamentul corect la reluare.
- Se pierde legătura dintre constituire și reluare când cele două operațiuni au loc în ani fiscali diferiți sau sub responsabili contabili diferiți.
- Se presupune că aplicația de contabilitate calculează automat diferențele permanente/temporare generate de provizioane, deși de regulă acest calcul cere intervenție manuală.
- Se raportează în D101 doar diferențele de la constituire, fără a urmări și veniturile din reluare care trebuie impozitate simetric.

## Ce face iConta.eu

`core/provizioane.py` calculează, la constituire, procentul/flagul de deductibilitate pentru fiecare tip de operațiune (`deductibilitate_creanta` pentru ajustări de creanțe, flagul `deductibil` din `nota_provizion` pentru provizionul de garanții, `deductibil: False` necondiționat în `nota_ajustare_stoc`), dar acest rezultat nu e persistat sau reutilizat automat la reluare, și nu e legat de rândurile D101 (`core/d101.py` citește P23-P33 ca input manual, fără nicio legătură cu `provizioane.py`). Practic, motorul oferă calculul punctual de deductibilitate la constituire; evidența longitudinală (constituire → sumă dedusă → reluare → venit impozabil/neimpozabil) trebuie ținută separat de utilizator, folosind rezultatele motorului ca sursă de date pentru fiecare operațiune.

[iConta.eu](/)
