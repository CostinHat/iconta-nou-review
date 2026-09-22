---
title: Cum verifici contul 5121 cu extrasul de cont?
description: Legea cere confruntarea soldurilor din extrasul de cont cu contabilitatea; verificarea practică presupune parcurgerea statusurilor liniilor de extras (verde, galben, roșu, nou) și compararea fișei de cont 5121 cu extrasul complet al perioadei.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum verifici contul 5121 cu extrasul de cont?

Verificarea contului 5121 față de extrasul bancar înseamnă, în esență, să confirmi că fiecare operațiune din extras are o înregistrare corespunzătoare în contabilitate, și invers — că nu lipsește nicio operațiune din extras din fișa de cont. iConta.eu oferă un flux structurat pentru asta, dar procesul rămâne parțial manual.

## Temeiul legal

::: ghid-temei
**29. - (2)** Disponibilitățile aflate în conturi la bănci sau la unitățile Trezoreriei Statului se inventariază prin confruntarea soldurilor din extrasele de cont emise de acestea cu cele din contabilitatea entității. În acest scop, extrasele de cont din ziua de 31 decembrie sau din ultima zi bancară, puse la dispoziție de instituțiile de credit și unitățile Trezoreriei Statului, vor purta ștampila oficială a acestora.
:::

## Pașii practici de verificare

Fiecare linie importată dintr-un extras primește un status: "nou" (importată, dar încă neprocesată prin matching), roșu (fără CUI detectat sau fără factură deschisă a partenerului), galben (alocare parțială FIFO, necesită confirmare) sau verde (potrivire exactă). Verificarea corectă a contului 5121 presupune parcurgerea explicită a acestor statusuri: mai întâi liniile "nou", care încă nu au fost procesate deloc, apoi liniile roșii, care semnalează fie lipsa unui CUI în descriere, fie lipsa unei facturi deschise corespunzătoare, apoi liniile galbene, care așteaptă o confirmare a alocării parțiale.

Doar după ce toate liniile din extras au un status final și au fost contate, are sens comparația de sold: soldul din fișa de cont 5121/5124, rezultat din operațiunile contate, trebuie confruntat cu soldul de închidere din extrasul bancar al perioadei — exact confruntarea cerută de textul legal citat mai sus. O diferență rămasă după acest pas provine de regulă din operațiuni fără factură asociată (comisioane, dobânzi, viramente interne), care nu trec prin acest motor de matching pe facturi.

## Ce se greșește în practică

- Se verifică doar liniile verzi (potrivire exactă), ignorând liniile galbene și roșii, care încă așteaptă acțiune.
- Se compară soldul 5121 cu extrasul înainte ca toate liniile importate să aibă un status final (unele rămân "nou", neprocesate).
- Se presupune că o linie roșie înseamnă automat o eroare a sistemului, deși de multe ori înseamnă doar lipsa unui CUI detectabil în descrierea bancară.
- Se ignoră faptul că motorul de matching acoperă doar operațiunile legate de facturi — comisioanele, dobânzile și viramentele interne rămân în afara acestui flux și trebuie verificate separat.

## Ce face iConta.eu

`core/reconciliere_api.py` persistă liniile de extras importate și rulează motorul de matching (`potriveste_extras`) pe fiecare linie, calculând totodată soldul fiecărei facturi deschise (total minus sumele deja decontate, plus eventualele storno-uri). Listarea liniilor și a facturilor deschise (`lista`, `facturi_deschise_detalii`) oferă doar formatarea necesară verificării — fără logică de matching suplimentară.

Confruntarea finală de sold — 5121/5124 din contabilitate versus soldul de închidere din extrasul bancar — nu e generată automat ca raport unic în acest motor; rămâne pasul de verificare manuală descris mai sus, pe fișa de cont completă.

[iConta.eu](/)
