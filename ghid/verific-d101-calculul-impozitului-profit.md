---
title: "Cum verific D101 cu calculul impozitului pe profit?"
description: "Descrie mecanismele de verificare confirmate în cod pentru validarea D101 față de calculul propriu al impozitului pe profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific D101 cu calculul impozitului pe profit?

## Temeiul legal

::: ghid-temei
Art.17 CF: "Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.
:::

D101 aplică cota de 16% (art.17) pe profitul impozabil (P40 → P411), rezultat din profitul contabil ajustat cu deducerile (P11, P13) și cheltuielile nedeductibile (P23/P34). Pentru validare, motorul rulează verificări proprii înainte de generare.

## Ce se greșește în practică

Diferențele apar cel mai des din deduceri sau add-back-uri omise — vezi și avertismentul dedicat contului 691 de mai jos.

## Ce face iConta.eu

La generare, iConta.eu rulează o reconciliere independentă a bazei contabile (`core/d101_reconciliere.py`) și verifică `totalPlata_A` emis (`core/reconciliere_emis.py`), pe lângă avertismentul dedicat contului 691 descris mai sus. Datele sunt citite din profilul firmei și din balanță, cu separarea exploatare/financiar (clasele 76/66 = financiar, restul 7x/6x = exploatare) plus conturile 1012 (capital social), 1061 (rezervă deja constituită) și 691 pentru calculul rezervei legale. Conform surselor verificate, aplicația nu compară însă explicit rezultatul cu soldul contului de bilanț 4411 (impozit pe profit datorat) — verificările acoperă contul de cheltuială (691) și structura balanței, nu soldul de bilanț al obligației față de buget. iConta.eu emite un avertisment automat când soldul debitor al contului 691 (cheltuiala cu impozitul pe profit) e mai mare decât zero, iar rândul P23 (cheltuieli nedeductibile) e completat cu zero — semn tipic că impozitul pe profit propriu nu a fost adăugat înapoi ca nedeductibil (CF art.25 alin.(4) lit.a)). Măsurată pe un portofoliu de test, omiterea acestei adăugări a scăzut impozitul declarat cu 2.432 lei, fără niciun alt semnal înainte de introducerea acestui gard.

[iConta.eu](/)
