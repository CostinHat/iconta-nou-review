---
title: Cum reconciliezi extrasul bancar cu balanța?
description: Legea cere confruntarea soldului bancar cu contabilitatea la inventariere, comparând soldul contului 512 cu extrasul de cont; motorul de matching din F073 potrivește doar liniile legate de facturi, nu calculează un sold total comparat cu balanța.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum reconciliezi extrasul bancar cu balanța?

La finalul unei perioade, întrebarea firească e dacă soldul contului 5121/5124 din balanța de verificare corespunde cu soldul din extrasul bancar. Reconcilierea "cu balanța" e un pas suplimentar față de simplul matching linie-cu-linie făcut de F073 — presupune verificarea soldului agregat, nu doar a operațiunilor individuale.

## Temeiul legal

::: ghid-temei
**29. - (2)** Disponibilitățile aflate în conturi la bănci sau la unitățile Trezoreriei Statului se inventariază prin confruntarea soldurilor din extrasele de cont emise de acestea cu cele din contabilitatea entității. În acest scop, extrasele de cont din ziua de 31 decembrie sau din ultima zi bancară, puse la dispoziție de instituțiile de credit și unitățile Trezoreriei Statului, vor purta ștampila oficială a acestora.

Contul 512 "Conturi curente la bănci" [...] este un cont bifuncțional. [...] Soldul debitor reprezintă disponibilitățile în lei și în valută, iar soldul creditor creditele primite.
:::

## Ce acoperă și ce nu acoperă F073

Motorul de matching din F073 (`core/reconciliere.py` + `core/reconciliere_api.py`) potrivește fiecare linie de extras cu o factură deschisă (sau o combinație de facturi) a partenerului identificat prin CUI. Este util pentru a confirma că operațiunile legate de facturi au fost corect înregistrate, dar nu calculează și nu compară automat soldul total al contului 512 din balanță cu soldul din extrasul bancar.

Pentru reconcilierea cu balanța, verificarea corectă presupune: confirmarea că toate liniile din extras au fost importate și au un status final (contat, nu doar "nou"), apoi compararea soldului rezultat în fișa de cont 5121/5124 cu soldul de închidere din extrasul bancar al perioadei — exact confruntarea de solduri cerută de textul legal citat mai sus. Diferențele rămase după această confruntare provin de regulă din operațiuni fără factură asociată (comisioane, dobânzi, viramente interne), care nu trec prin motorul de matching pe facturi.

## Ce se greșește în practică

- Se consideră reconcilierea încheiată doar pentru că toate liniile din extras au status verde sau galben, fără verificarea soldului final din balanță.
- Se compară soldul din balanță cu soldul extrasului fără să se excludă liniile încă needitate (status "nou").
- Se ignoră faptul că textul legal citat vorbește de inventariere (de regulă anuală, la 31 decembrie sau ultima zi bancară), nu de o obligație distinctă de reconciliere lunară cu balanța.
- Se atribuie orice diferență de sold unei erori de matching, fără verificarea operațiunilor fără factură (comisioane, dobânzi, viramente).

## Ce face iConta.eu

`core/reconciliere_api.py` calculează soldul fiecărei facturi deschise (`total_lei` sau `total`, minus sumele deja decontate prin înregistrări legate de `factura_id`, plus eventualele storno-uri), și persistă fiecare alocare rezultată din matching. Contarea (`conteaza`) generează înregistrarea contabilă cu formula debit 5121/5124 – credit 4111 la încasare, respectiv debit 401 – credit 5121/5124 la plată, exact structura contului 512 descrisă în planul de conturi.

Sistemul nu produce, în cadrul acestui motor, un raport automat de tip "sold 512 din balanță vs. sold extras bancar" — acesta rămâne un pas de verificare separat, pe fișa de cont completă.

[iConta.eu](/)
