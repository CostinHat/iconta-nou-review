---
title: "Cum declar ajustările de TVA în D300?"
description: Rândul care se numește efectiv „ajustare" în structura D300 (rândul 34, pro-rata) e calculat automat din profilul firmei și nu apare în panoul manual. Pentru o corecție fără factură, cel mai apropiat rând manual e rândul 33, regularizări taxă dedusă — nu „ajustare".
published: 2026-09-23
modified: 2026-10-13
poarta: v1
---

# Cum declar ajustările de TVA în D300?

Întrebarea „unde declar o ajustare de TVA" are un răspuns care surprinde: rândul care poartă efectiv numele „ajustări" în structura oficială a D300 nu se poate introduce manual. E calculat automat, din profilul firmei.

## Temeiul legal

::: ghid-temei
„Ajustări conform pro-rata/ajustări de taxă”
— OPANAF 174/2026, anexa 1, formularul 300, rândul 34 (sursă: [OPANAF nr. 174/2026 pentru aprobarea formularului 300 (Decont de TVA)](https://legislatie.just.ro/Public/DetaliiDocument/307258))
:::

## Rândul 34 — ajustarea pro-rata — e automată, nu manuală

Rândul 34 (coloana TVA) se calculează direct din câmpul „pro-rata (Date firmă)” al profilului firmei, cu formula: partea întreagă din taxa de la rândul 31 × (100 − pro-rata) / 100, cu semn minus, dacă pro-rata e sub 100%, altfel 0. Verificat direct în cod (aplicația).

Rândul 34 **nu apare** în allow-list-ul panoului manual „Rând manual D300” — rândurile computate, inclusiv rândul 34, sunt listate explicit ca neacceptate manual. Dacă ajustarea pro-rata nu apare corect în decont, nu se introduce un rând manual: se verifică și, dacă e cazul, se corectează câmpul pro-rata din profilul firmei — motorul recalculează automat rândul 34 la următoarea generare a decontului.

## Dacă „ajustare" înseamnă, de fapt, o corecție fără factură

Dacă prin „ajustare de TVA" te referi la o corecție sau regularizare a unei sume care nu are (sau nu mai are) o factură care s-o susțină, acela e cazul general de regularizare din „Rând manual D300” — nu un rând numit „ajustare". Cel mai apropiat rând manual disponibil e:

- **rândul 33** — „Regularizări taxă dedusă" — pentru taxa dedusă;
- **rândul 16** — „Regularizări taxă colectată" — pentru taxa colectată.

## Ce se greșește în practică

Se caută un rând „ajustare" în panoul manual „Rând manual D300” și se încearcă introducerea unei sume pe rândul 34 — rândul nu apare în lista de rânduri disponibile a panoului, pentru că nu e permis manual, indiferent de context sau de valoarea introdusă.

## Ce face iConta.eu

Calculează automat rândul 34 din pro-rata firmei, la fiecare generare a decontului, fără nicio intervenție manuală posibilă pe acest rând. Pentru corecții fără factură care nu privesc pro-rata, panoul „Rând manual D300” oferă rândurile de regularizare propriu-zise — rândurile 16 și 33 — nu un rând etichetat generic „ajustare".

[iConta.eu](/)
