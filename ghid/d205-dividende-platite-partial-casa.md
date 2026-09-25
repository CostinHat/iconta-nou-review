---
title: "D205 pentru dividende plătite parțial prin casă și bancă"
description: "Ce spune legea despre plata mixtă, cash și bancă, a unui dividend către o persoană fizică, și cum se reflectă suma totală în declarația D205."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# D205 pentru dividende plătite parțial prin casă și bancă

Plata unui dividend nu trebuie făcută printr-un singur instrument — poate fi împărțită între numerar și transfer bancar, atâta timp cât partea în numerar respectă plafonul legal. Pentru D205, ce contează la final e suma totală efectiv plătită asociatului, indiferent prin ce instrument a ajuns la el.

## Temeiul legal

::: ghid-temei
„Operațiunile de plăți în numerar efectuate de persoanele prevăzute la art. 1 alin. (1), către persoane fizice, reprezentând contravaloarea unor achiziții de bunuri sau a unor prestări de servicii, dividende, cesiuni de creanțe sau alte drepturi și restituiri de împrumuturi sau alte finanțări se efectuează cu încadrarea în plafonul zilnic de 10.000 lei către o persoană. Sunt interzise plățile fragmentate în numerar către o persoană, pentru tranzacțiile mai mari de 10.000 lei."
— Legea 70/2015, art. 4 alin. (4) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

- Legea vizează explicit dividendele plătite persoanelor fizice, alături de alte tipuri de plăți — plafonul de 10.000 lei/zi/persoană se aplică la fel unei plăți de dividend ca oricărei alte plăți în numerar.
- Interdicția vizează fragmentarea plăților ÎN NUMERAR peste plafon (mai multe plăți cash mici, către aceeași persoană, aceeași zi), nu împărțirea între instrumente diferite — plata parte în numerar (până la plafon), parte prin bancă, nu e o fragmentare interzisă.
- Plafonul se raportează la persoană și la zi, nu la operațiune: două plăți cash de 6.000 lei în aceeași zi către același asociat depășesc plafonul, chiar dacă fiecare, luată separat, pare sub 10.000 lei.

## Ce se greșește în practică

- Se plătește integral în numerar un dividend care depășește 10.000 lei, fără a direcționa restul prin bancă.
- Se fac mai multe plăți cash în aceeași zi către același asociat, gândite ca tranșe separate, ignorând că plafonul se calculează cumulat pe zi și pe persoană.
- Se presupune greșit că orice plată mixtă cash+bancă e per se o încălcare a legii, deși ea e permisă atâta timp cât componenta numerar respectă plafonul.

## Ce face iConta.eu

Motorul de calcul al D205 citește dividendul plătit direct din contul 457, însumând toate notele contabile validate în care 457 apare pe partea de debit — indiferent de contul de contrapartidă folosit (bancă, casă sau altul). Aplicația nu distinge tehnic instrumentul de plată la nivelul declarației: dacă un dividend e plătit parțial prin casă și parțial prin bancă, iar ambele note contabile sunt înregistrate și validate, suma se cumulează corect în baza impozabilă din D205, la fel ca la o plată integrală printr-un singur instrument.

Ce NU face aplicația: nu verifică și nu avertizează dacă partea în numerar a plății depășește plafonul legal de 10.000 lei/zi din Legea 70/2015 — respectarea acelui plafon rămâne responsabilitatea contabilului la momentul înregistrării plății, nu un control automat al iConta.eu.

[iConta.eu](/)
