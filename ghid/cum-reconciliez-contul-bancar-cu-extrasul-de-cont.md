---
title: Cum reconciliez contul bancar cu extrasul de cont?
description: Legea cere confruntarea soldurilor bancare cu contabilitatea la inventariere (de regulă anuală); reconcilierea lunară sau la fiecare extras, deși recomandată ca bună practică, nu are un temei legal distinct pentru frecvență în sursele verificate.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum reconciliez contul bancar cu extrasul de cont?

Reconcilierea bancară înseamnă potrivirea fiecărei linii din extrasul de cont cu operațiunea contabilă corespunzătoare — de regulă o factură emisă sau primită. iConta.eu automatizează cea mai mare parte a acestui proces prin motorul de matching din F073.

## Temeiul legal

::: ghid-temei
**29. - (2)** Disponibilitățile aflate în conturi la bănci sau la unitățile Trezoreriei Statului se inventariază prin confruntarea soldurilor din extrasele de cont emise de acestea cu cele din contabilitatea entității. În acest scop, extrasele de cont din ziua de 31 decembrie sau din ultima zi bancară, puse la dispoziție de instituțiile de credit și unitățile Trezoreriei Statului, vor purta ștampila oficială a acestora.

**Articolul 6 (1)** Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ.
:::

## Cum funcționează procesul de reconciliere

La importul unui extras, fiecare linie trece automat prin motorul de matching. Dacă linia are un CUI identificat în descriere, sistemul caută facturile deschise ale acelui partener, pe direcția corespunzătoare (încasare → facturi emise; plată → facturi primite), și încearcă în ordine: o potrivire exactă pe o singură factură, apoi pe o combinație de 2-4 facturi, apoi o alocare parțială FIFO pe facturile cele mai vechi. Rezultatul fiecărei linii e marcat verde (potrivire exactă, gata de contare), galben (alocare parțială, necesită confirmare manuală) sau roșu (fără CUI detectat sau fără nicio factură deschisă a partenerului).

Textul legal citat mai sus vorbește explicit despre inventarierea disponibilităților bănești — un proces care se face, de regulă, anual sau la închiderea exercițiului financiar, prin confruntarea soldurilor. Trebuie spus onest: sursele legale verificate nu conțin o obligație distinctă de reconciliere lunară sau la fiecare extras — aceasta e o bună practică de gestiune financiară, larg recomandată, dar nu o cerință legală separată de obligația de inventariere anuală.

## Ce se greșește în practică

- Se crede că legea obligă la o reconciliere lunară strictă — textul citat vorbește de inventariere, de regulă anuală, nu de o cadență lunară obligatorie.
- Se lasă liniile roșii necontate pe termen lung, fără investigație, deși ele semnalează fie o factură lipsă, fie un CUI nedetectat.
- Se confundă statusul galben (alocare parțială, care încă necesită confirmare) cu o linie deja contabilizată definitiv.
- Se ignoră faptul că o linie contabilizată (`status='contat'`) nu mai poate fi recontată automat prin motor — o corecție ulterioară trebuie tratată manual.

## Ce face iConta.eu

`core/reconciliere.py` rulează motorul pur de matching pe fiecare linie de extras, iar `core/reconciliere_api.py` persistă rezultatul și calculează soldul fiecărei facturi deschise (total minus sumele deja decontate, plus eventualele storno-uri). Pentru liniile care ies roșii și nu au notă manuală, sistemul încearcă o sugestie de cont pe baza istoricului deja contat de utilizator (`core.ai_incredere.sugestie`) — o funcționalitate de confort, fără nicio bază legală, utilizatorul rămânând responsabil pentru validarea sugestiei.

La contare, fiecare alocare generează o înregistrare separată (`status='ciorna'`, `sursa='banca'`), iar dacă firma e pe TVA la încasare, exigibilitatea TVA se calculează separat pentru fiecare sumă alocată.

[iConta.eu](/)
