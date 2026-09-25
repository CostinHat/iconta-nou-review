---
title: "Cum se depune D406 Stocuri la solicitarea ANAF?"
description: "Regulile speciale pentru secțiunea Stocuri a SAF-T (D406), transmisă exclusiv la solicitarea organului fiscal central, nu periodic ca celelalte secțiuni."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se depune D406 Stocuri la solicitarea ANAF?

Spre deosebire de secțiunile obișnuite ale fișierului SAF-T (jurnal general, facturi, active), secțiunea **Stocuri** a Declarației informative D406 nu se transmite periodic, lunar sau trimestrial. Ea se depune **doar atunci când organul fiscal central o solicită explicit**, pentru perioada indicată în solicitare.

## Temeiul legal

::: ghid-temei
„9. Informaţiile privind «stocurile de produse» şi «producţie în curs» sunt transmise pe baza unei solicitări specifice din partea organelor fiscale centrale. În funcţie de perioada pentru care se solicită furnizarea informaţiilor privind stocurile prin fişierul standard de control fiscal (SAF-T), contribuabilii furnizează una sau mai multe declaraţii informative cuprinzând subsecţiunile din fişierul SAF-T relevante pentru «Stocuri», separate pentru fiecare dintre lunile/trimestrele calendaristice cuprinse în perioada pentru care a fost trimisă solicitarea din partea organelor fiscale centrale. 10. Declaraţiile informative D406 pentru «Stocuri» se depun în termenul stabilit de organul fiscal central, care nu poate fi mai mic de 30 de zile calendaristice de la data solicitării."
— OPANAF nr. 1783/2021, Anexa 4 — Termenele de transmitere a fișierului SAF-T, pct. 9-10 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

- Secțiunea Stocuri se transmite **exclusiv pe bază de solicitare**, spre deosebire de restul secțiunilor SAF-T, care au termene fixe (ultima zi calendaristică a lunii următoare perioadei de raportare) sau, pentru secțiunea Active, termenul de depunere a situațiilor financiare.
- Dacă solicitarea ANAF acoperă mai multe luni sau trimestre calendaristice, contribuabilul trebuie să depună **câte o declarație separată pentru fiecare perioadă** cuprinsă în solicitare, nu un singur fișier agregat.
- Termenul de depunere este stabilit de organul fiscal central prin solicitare, dar legea impune un **minim de 30 de zile calendaristice** de la data solicitării — organul fiscal nu poate acorda un termen mai scurt.
- La fel ca la celelalte secțiuni SAF-T, dacă se identifică ulterior erori, contribuabilul poate depune declarații rectificative, care trebuie să cuprindă integral informațiile din declarația inițială plus corecțiile.

## Ce se greșește în practică

- Se transmite secțiunea Stocuri periodic, din inerție, alături de celelalte secțiuni SAF-T, deși legea o rezervă strict cazurilor de solicitare expresă din partea ANAF.
- Se depune un singur fișier cumulat pentru toată perioada solicitată, în loc de declarații separate pentru fiecare lună/trimestru cuprins în solicitare.
- Se presupune că termenul de depunere este întotdeauna cel standard (sfârșitul lunii următoare), ignorând că pentru Stocuri termenul minim legal este de 30 de zile de la data solicitării, stabilit distinct de organul fiscal.
- Se ignoră structura tehnică specifică secțiunii PhysicalStock din schema SAF-T (solduri de deschidere/închidere pe articol, cantitate și valoare), tratând-o ca pe o simplă listă de stocuri contabile.

## Ce face iConta.eu

Din verificarea codului sursă, iConta.eu are un **generator dedicat pentru D406 Stocuri** (`core/d406_stocuri.py`), care calculează soldurile de deschidere și închidere pe articol (cantitate și valoare, pe baza mișcărilor de intrare/ieșire) și produce secțiunea `PhysicalStockEntry` a fișierului SAF-T, conform structurii oficiale verificate pe schema XSD a ANAF. Modulul generează fișierul pentru perioada cerută de utilizator; corelarea directă cu solicitarea specifică primită de la ANAF (identificarea automată a perioadei și a termenului-limită comunicate de organul fiscal) rămâne, în prezent, un pas realizat manual de contabil, pe baza informațiilor din solicitarea primită.

[iConta.eu](/)
