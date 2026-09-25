---
title: "Durata maximă a eșalonării la plată la ANAF"
description: "Care este durata maximă a unei eșalonări la plată acordate de ANAF pentru datorii fiscale și ce condiții reduc această durată."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Durata maximă a eșalonării la plată la ANAF

Când o firmă nu poate achita integral o datorie fiscală, ANAF poate acorda o eșalonare la plată — dar durata ei maximă nu e nelimitată și depinde, printre altele, de garanțiile pe care debitorul le poate constitui.

## Temeiul legal

::: ghid-temei
„Organul fiscal central acordă la cererea debitorilor eșalonări la plată pe o perioadă de cel mult 5 ani, dacă sunt îndeplinite condițiile de acordare a acestora. Pentru debitorii care nu au în proprietate bunuri în vederea constituirii de garanții în cuantumul prevăzut la art. 193 alin. (13) - (15) și nici nu pot constitui niciun fel de garanție ori cuantumul garanțiilor constituite este mai mic de 50% față de cuantumul obligațiilor fiscale restante ce fac obiectul înlesnirilor la plată, eșalonarea se acordă pe cel mult 6 luni."
— Legea 207/2015 (Codul de procedură fiscală), art. 184 (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce înseamnă, în practică, aceste durate:

- Regula generală: eșalonarea se poate acorda pe **cel mult 5 ani**, dacă debitorul îndeplinește condițiile legale de acordare (inclusiv depunerea documentelor cerute și constituirea garanțiilor corespunzătoare).
- Excepția: dacă debitorul nu poate constitui garanții suficiente (sub 50% din valoarea obligațiilor restante), durata maximă scade drastic, la **cel mult 6 luni**.
- Graficul de eșalonare se poate suplimenta, în cadrul aceleiași perioade aprobate inițial, dacă apare o declarație rectificativă ce modifică sumele eșalonate — perioada nu se prelungește automat din acest motiv.
- Debitorul poate renunța oricând la eșalonare, pe perioada ei de valabilitate, printr-o cerere de renunțare.

## Ce se greșește în practică

- Se presupune că orice cerere de eșalonare primește automat 5 ani — de fapt, fără garanții suficiente, durata reală acordată e mult mai scurtă (6 luni).
- Se confundă eșalonarea la plată cu amânarea la plată — amânarea are o durată maximă diferită (cel mult 6 luni, dar care nu poate depăși 20 decembrie a anului fiscal respectiv).
- Se pierde din vedere că nerespectarea graficului de eșalonare (o rată neplătită la termen) poate anula valabilitatea înlesnirii, caz în care redevin aplicabile dobânzile și penalitățile de întârziere obișnuite pentru întreaga sumă rămasă.

## Ce face iConta.eu

iConta.eu nu depune și nu gestionează cereri de eșalonare la plată către ANAF — aceasta este o procedură administrativă separată, în afara aplicației. Modulul propriu de scadențar (`core/scadentar.py`) urmărește facturile **emise** de firmă și neîncasate de la clienți, nu obligațiile fiscale eșalonate la bugetul de stat, așa că nu poate fi folosit pentru a urmări un grafic de eșalonare ANAF.

[iConta.eu](/)
