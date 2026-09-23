---
title: Cum evidențiez sponsorizarea în calculul impozitului pe profit?
description: Creditul de sponsorizare se trece la rândul P43 din D101, în limita dublă verificată automat de aplicație — 20% din impozitul pe profit (P41-P42) și 0,75% din cifra de afaceri — și se scade din impozitul datorat înainte de a ajunge la suma finală de plată (rândul P48).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum evidențiez sponsorizarea în calculul impozitului pe profit?

În declarația 101, sponsorizarea nu apare printre cheltuieli, ci într-o secțiune separată, dedicată creditelor fiscale care se scad din impozitul pe profit deja calculat — pe același palier cu alte reduceri, nu pe cel al veniturilor și cheltuielilor din care rezultă profitul impozabil.

## Temeiul legal

::: ghid-temei
„i) ... scad sumele aferente din impozitul pe profit datorat la nivelul valorii minime dintre următoarele: 1. valoarea calculată prin aplicarea a 0,75% la cifra de afaceri; ...; 2. valoarea reprezentând 20% din impozitul pe profit datorat. [...]”

— *Codul fiscal, art. 25 alin. (4) lit. i).*
:::

## Unde apare în calculul impozitului pe profit

Structura declarației 101 urmează, în linii mari, această secvență:

1. Se calculează **profitul impozabil** și, din el, **impozitul pe profit** înainte de credite (rândul care agregă cota de 16% aplicată profitului, plus eventualele cote speciale).
2. Din acest impozit se scad, pe rânduri separate, **creditele fiscale** — sumele plătite în străinătate, sponsorizarea, alte reduceri prevăzute de legi speciale — fiecare cu propriul plafon de verificare.
3. Sponsorizarea are rândul ei propriu, cu o limită dublă verificată automat: nu poate depăși nici 20% din impozitul rămas după alte credite anterioare, nici 0,75% din cifra de afaceri a firmei.
4. Diferența rezultată, după scăderea tuturor creditelor, e **impozitul pe profit datorat**, suma pe care firma o plătește efectiv.

Practic, sponsorizarea „evidențiată corect” înseamnă: calculată separat de restul cheltuielilor (care nu au fost deduse din profitul impozabil pentru ea), verificată împotriva ambelor plafoane, și scăzută direct din impozitul pe profit calculat, nu adăugată la cheltuielile deductibile.

## Ce se greșește în practică

- Se introduce suma sponsorizării la cheltuieli nedeductibile, dar se omite trecerea creditului corespunzător la rândul dedicat din declarație — sponsorizarea rămâne doar cheltuială, fără efectul de reducere a impozitului.
- Se completează suma integrală sponsorizată la rândul de credit, fără a o limita întâi la minimul dintre cele două plafoane (20% din impozit, 0,75% din cifra de afaceri).
- Se calculează plafonul de 20% raportat la impozitul pe profit total, ignorând că baza de calcul e impozitul rămas **după** alte credite fiscale scăzute anterior (de exemplu, impozitul plătit în străinătate).
- Se aplică procentul de 0,75% pentru o declarație aferentă unui an fiscal anterior lui 03.02.2022, când plafonul legal din cifra de afaceri era 0,5%.

## Ce face iConta.eu

Motorul de calcul D101 (`core/d101.py`) tratează sponsorizarea la rândul dedicat creditelor fiscale (secțiunea rd.42-45 din structura declarației) și aplică validarea dublă cerută de lege, nu doar limita de 20%: verificarea internă `V5` confirmă `P43 <= 20% × (P41 − P42)` — adică 20% din impozitul rămas după creditul fiscal extern (P42) — iar o verificare suplimentară (`V5-bis`, adăugată explicit pentru că validatorul oficial DUK confirmă doar limita de 20%) confirmă separat `P43 <= 0,75% × cifra de afaceri`, calculată din rulajul contului de venituri din vânzări (clasa 70x) atunci când cifra de afaceri e cunoscută din balanță. Dacă suma introdusă la P43 depășește oricare din cele două plafoane, aplicația respinge declarația cu eroare explicită, înainte de trimiterea către ANAF.

Calculul propriu-zis al plafonului și al creditului (câtă sponsorizare intră, de fapt, la P43) se face separat, cu `credit_sponsorizare()` din `core/sponsorizari.py` — D101 doar verifică, la depunere, că valoarea introdusă respectă cele două limite.

[iConta.eu](/)
