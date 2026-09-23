---
title: "Cum declar ajustările de TVA în D300?"
description: Rândul care se numește efectiv „ajustare" în structura D300 (R31, pro-rata) e calculat automat din profilul firmei și nu apare în panoul manual. Pentru o corecție fără factură, cel mai apropiat rând manual e R30, regularizări taxă dedusă — nu „ajustare".
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum declar ajustările de TVA în D300?

Întrebarea „unde declar o ajustare de TVA" are un răspuns care surprinde: rândul care poartă efectiv numele „ajustări" în structura oficială a D300 nu se poate introduce manual. E calculat automat, din profilul firmei.

## Temeiul legal

::: ghid-temei
„Ajustări conform pro-rata / ajustări de taxă" — structura D300 v12 (OPANAF 174/2026), rd.31 col.2
:::

## R31 — ajustarea pro-rata — e automată, nu manuală

Rândul R31_2 se calculează direct din câmpul `pro_rata` al profilului firmei, cu formula: `r31_2 = int(Decimal(r28_2) * Decimal(100 - pro_rata) / 100 * -1)` dacă pro-rata e sub 100%, altfel 0. Verificat direct în cod (`d300.py:573-588`).

R31 **nu apare** în allow-list-ul panoului manual F251 — rândurile computate, inclusiv R31, sunt listate explicit ca neacceptate manual. Dacă ajustarea pro-rata nu apare corect în decont, nu se introduce un rând manual: se verifică și, dacă e cazul, se corectează câmpul pro-rata din profilul firmei — motorul recalculează automat R31 la următoarea generare a decontului.

## Dacă „ajustare" înseamnă, de fapt, o corecție fără factură

Dacă prin „ajustare de TVA" te referi la o corecție sau regularizare a unei sume care nu are (sau nu mai are) o factură care s-o susțină, acela e cazul general de regularizare din F251 — nu un rând numit „ajustare". Cel mai apropiat rând manual disponibil e:

- **R30** — „Regularizări taxă dedusă" — pentru taxa dedusă;
- **R16** — „Regularizări taxă colectată" — pentru taxa colectată.

## Ce se greșește în practică

Se caută un rând „ajustare" în panoul manual F251 și se încearcă introducerea unei sume pe R31 — rândul nu apare în lista de rânduri disponibile a panoului, pentru că nu e permis manual, indiferent de context sau de valoarea introdusă.

## Ce face iConta.eu

Calculează automat R31 din pro-rata firmei, la fiecare generare a decontului, fără nicio intervenție manuală posibilă pe acest rând. Pentru corecții fără factură care nu privesc pro-rata, panoul F251 oferă rândurile de regularizare propriu-zise — R16 și R30 — nu un rând etichetat generic „ajustare".

[iConta.eu](/)
