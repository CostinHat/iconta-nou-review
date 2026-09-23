---
title: Cum reconciliez soldul contului 5121 cu extrasul bancar?
description: Reconcilierea automată din iConta.eu potrivește linii de extras cu facturi, nu solduri. Confruntarea soldului contului 5121 cu extrasul rămâne o verificare separată, pe fișa de cont și balanța de verificare.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum reconciliez soldul contului 5121 cu extrasul bancar?

Motorul de reconciliere bancară din iConta.eu face potrivire **pe linie**: fiecare rând din extras se caută pe facturile deschise ale unui partener. Nu face verificare **de sold**: nu calculează soldul total al contului 5121 din contabilitate și nu îl compară automat cu soldul din extras la o dată dată. Confruntarea soldurilor e o operațiune separată, tratată mai jos.

## Temeiul legal

::: ghid-temei
„Disponibilitățile aflate în conturi la bănci sau la unitățile Trezoreriei Statului se inventariază prin confruntarea soldurilor din extrasele de cont emise de acestea cu cele din contabilitatea entității. În acest scop, extrasele de cont din ziua de 31 decembrie sau din ultima zi bancară, puse la dispoziție de instituțiile de credit și unitățile Trezoreriei Statului, vor purta ștampila oficială a acestora."
— OMFP 2861/2009, pct. 29 alin. (2)
:::

::: ghid-temei
„Pentru verificarea înregistrării corecte în contabilitate a operațiunilor efectuate, lunar se întocmește balanța de verificare."
— Legea contabilității nr. 82/1991, art. 22
:::

Textul cel mai apropiat de „confruntarea soldului 5121 cu extrasul" e formulat ca obligație de **inventariere**, de regulă la finalul exercițiului financiar — nu ca o procedură lunară numită explicit. Practica de a verifica soldul mai des (de exemplu lunar, odată cu balanța de verificare) e o bună practică de gestiune, sprijinită indirect de obligația lunară a balanței de verificare, dar fără un text legal separat care să ceară exact „reconciliere de sold lunară".

## Cum se face, în lipsa unui instrument automat de sold

Pentru că F073 nu oferă un raport dedicat de comparație de sold, verificarea se face manual, în doi pași:

1. **Soldul contabil** — se ia soldul contului 5121 (sau 5124, pentru conturile în valută) la data dorită, din fișa de cont sau din balanța de verificare a lunii.
2. **Soldul bancar** — se ia soldul de la aceeași dată din extrasul bancar (sau din soldul curent afișat de bancă).

Diferența dintre cele două, dacă există, se explică de regulă prin: linii de extras necontate încă (nepotrivite, alocare parțială neconfirmată), linii marcate „Ignorată", operațiuni fără factură asociată (comisioane, dobânzi, viramente interne) sau, mai rar, duplicate provenite dintr-un reimport al aceluiași extras.

## Ce se greșește în practică

- Se caută în ecranul Bancă un „sold reconciliat" afișat de aplicație — nu există un asemenea indicator; ecranul arată starea liniilor, nu un sold cumulat comparat cu banca.
- Se presupune că, odată ce toate liniile din extras apar „Contat ✓", soldul 5121 e automat egal cu soldul bancar — poate să nu fie, dacă există operațiuni fără factură (comisioane, dobânzi) contabilizate separat, cu întârziere sau deloc.
- Se face verificarea de sold o singură dată pe an, la închiderea exercițiului, deși o discrepanță descoperită abia atunci e mult mai greu de investigat decât una prinsă lunar.

## Ce face iConta.eu

Reconcilierea bancară din iConta.eu (`core/reconciliere.py` + `core/reconciliere_api.py`) potrivește linii de extras cu facturi deschise, ceea ce ajută să nu rămână facturi neînchise sau linii necontabilizate — dar nu calculează și nu afișează o comparație automată a soldului contului 5121 cu soldul din extrasul bancar. Această verificare rămâne manuală, pe baza fișei de cont 5121 și a balanței de verificare, comparată cu extrasul sau cu soldul curent pus la dispoziție de bancă.

[iConta.eu](/)
