---
title: "Cum se raportează producția în D406?"
description: "Cum apar stocurile de produse finite și producția în curs în fișierul SAF-T (D406) și când sunt efectiv solicitate de ANAF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se raportează producția în D406?

Spre deosebire de secțiunile obligatorii ale D406 (facturi, plăți, registrul-jurnal), informațiile despre stocurile de produse și producția în curs de execuție nu se transmit automat cu fiecare declarație lunară sau trimestrială — se transmit doar la cererea explicită a organului fiscal, pentru perioada indicată de acesta.

## Temeiul legal

::: ghid-temei
„9. Informaţiile privind «stocurile de produse» şi «producţie în curs» sunt transmise pe baza unei solicitări specifice din partea organelor fiscale centrale. În funcţie de perioada pentru care se solicită furnizarea informaţiilor privind stocurile prin fişierul standard de control fiscal (SAF-T), contribuabilii furnizează una sau mai multe declaraţii informative cuprinzând subsecţiunile din fişierul SAF-T relevante pentru «Stocuri», separate pentru fiecare dintre lunile/trimestrele calendaristice cuprinse în perioada pentru care a fost trimisă solicitarea din partea organelor fiscale centrale.
10. Declaraţiile informative D406 pentru «Stocuri» se depun în termenul stabilit de organul fiscal central, care nu poate fi mai mic de 30 de zile calendaristice de la data solicitării."
— OPANAF 1.783/2021, Anexa nr. 5, pct. 9 și 10 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Din structura oficială a fișierului SAF-T rezultă:

- Secțiunea **PhysicalStock (Stocuri)** conține, pentru fiecare produs, cantitatea și valoarea la începutul și la finalul perioadei de raportare — indiferent dacă produsul e marfă, materie primă sau produs finit rezultat din producție.
- Secțiunea **Assets (Active)** conține, pentru mijloacele fixe rezultate din producție proprie, „costurile totale de achiziţie/producţie la începutul şi finalul perioadei selectate pentru raportare".
- Raportarea „Stocuri" (care include producția în curs) se face **doar la solicitarea organului fiscal central**, cu un termen minim de 30 de zile calendaristice de la solicitare — nu odată cu declarația lunară/trimestrială standard.

## Ce se greșește în practică

- Se încearcă includerea stocurilor de produse finite și a producției în curs în fiecare D406 lunar/trimestrial, fără o solicitare explicită din partea ANAF — secțiunea „Stocuri" nu e parte din raportarea periodică standard.
- Se confundă „Active" (mijloace fixe, cu cost de producție capitalizat) cu „Stocuri" (produse destinate vânzării) — cele două secțiuni au reguli de raportare diferite: Activele pot fi transmise ca declarație independentă, Stocurile doar la cerere.
- Se ignoră termenul minim de 30 de zile pentru pregătirea raportării de stocuri odată ce vine solicitarea ANAF, tratând-o ca pe un termen fix, scurt, de tip declarație lunară.

## Ce face iConta.eu

iConta.eu are un generator funcțional pentru secțiunea de stocuri a SAF-T, în `core/d406_stocuri.py`: calculează soldurile de deschidere și închidere (cantitate și valoare) pe fiecare articol, pe baza mișcărilor de intrare/ieșire din perioada raportată, și construiește elementul XML `PhysicalStockEntry` cerut de schema oficială (`ProductType`, `UnitPrice`, `OpeningStockQuantity/Value`, `ClosingStockQuantity/Value` etc.).

Ce nu automatizează astăzi aplicația: identificarea automată a momentului în care vine o solicitare ANAF de raportare a stocurilor/producției în curs și declanșarea raportării corespunzătoare. Generarea secțiunii de stocuri rămâne, la această dată, o acțiune pe care contabilul o inițiază manual, când primește solicitarea de la organul fiscal.

[iConta.eu](/)
