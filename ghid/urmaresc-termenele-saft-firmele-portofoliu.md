---
title: Cum urmăresc termenele SAF-T pentru toate firmele din portofoliu?
description: Ecranul Termene din iConta.eu agregă scadențele SAF-T ale tuturor firmelor tale, grupate pe dată, cu numărul de firme la fiecare termen — dar nu calculează perioada de grație de la prima raportare.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum urmăresc termenele SAF-T pentru toate firmele din portofoliu?

Dacă administrezi mai multe firme, nu e practic să verifici SAF-T-ul (D406) firmă cu firmă. Ecranul „Termene" din iConta.eu face exact agregarea asta: citește vectorul fiscal al fiecărei firme la care ai acces, derivă declarațiile datorate în următoarele 60 de zile și le grupează pe dată, cu numărul de firme care au aceeași scadență.

## Temeiul legal

::: ghid-temei
„Data-limită pentru transmiterea declarațiilor informative D406 privind fișierul standard de control fiscal este ultima zi calendaristică din luna depunerii, reprezentând luna calendaristică imediat următoare perioadei pentru care a fost pregătită declarația informativă."
— OPANAF 1783/2021, Anexa nr. 4, pct. 4
:::

Periodicitatea SAF-T diferă în funcție de statutul de TVA al fiecărei firme: firmele plătitoare de TVA raportează în ritmul deconturilor lor de TVA (lunar sau trimestrial, după tipul de decont), iar cele neplătitoare raportează trimestrial. Termenul cade întotdeauna pe ultima zi calendaristică a lunii următoare perioadei raportate, mutat pe prima zi lucrătoare dacă pică în weekend sau sărbătoare legală.

## Cum funcționează agregarea pe portofoliu

Ecranul „Termene" nu e o simplă listă per firmă — grupează efectiv rezultatele pe două chei, dată și tip de declarație, indiferent la câte firme se datorează:

1. Pentru fiecare firmă la care ai acces, aplicația derivă declarațiile datorate în fereastra [azi, azi+60 zile], pe baza vectorului fiscal (regim, statut TVA, tip decont, operațiuni intracomunitare).
2. Rezultatele individuale sunt grupate pe (dată-termen, tip declarație) — un SAF-T cu termen 31 octombrie, datorat de 6 firme, apare ca un singur rând, cu „6 firme".
3. Click pe rând deschide lista firmelor din acel grup; click pe o firmă deschide fișa ei.
4. Firmele al căror vector fiscal nu e completat, sau a căror evaluare a eșuat, NU dispar tăcut din listă — apar separat, sub „neevaluate", cu motivul exact.

Fereastra e strict de 60 de zile, strict viitoare — o firmă cu SAF-T restant (termen deja depășit) nu apare aici, ci pe ecranul „Semafor" (control fiscal), care are altă fereastră și include și restanțele.

## Ce se greșește în practică

- **Se presupune că data afișată e termenul real pentru o primă raportare.** Legea acordă o perioadă de grație la prima raportare SAF-T — 6 luni pentru firmele cu transmitere lunară (descrescător la a doua, a treia etc. raportare), respectiv 3 luni pentru cele cu transmitere trimestrială. Ecranul „Termene" NU scade această grație — afișează termenul nominal (ultima zi a lunii următoare), ca și cum grația nu ar exista. Pentru o firmă la primul SAF-T, verifică manual dacă se aplică perioada de grație înainte să tratezi data afișată drept scadență fermă.
- **Se ignoră firmele nou adăugate în portofoliu, fără vector fiscal completat.** Acestea apar „neevaluate", nu absente — dar dacă nu se verifică explicit secțiunea de neevaluate, pot trece neobservate luni la rând.
- **Se confundă fereastra de 60 de zile cu un calendar complet pe an.** Ecranul nu arată toate scadențele anului 2026 dintr-o dată, ci doar ce intră în fereastra curentă; termenele mai îndepărtate apar treptat, pe măsură ce se apropie.

## Ce face iConta.eu

Motorul (`core/termene_api.py`) refolosește exact maparea „cine ce declarație datorează" din motorul unic de control fiscal (`core/control_fiscal_api.py`), cu fereastra restrânsă la [azi, azi+60 zile]. Rezultatele per firmă sunt agregate pe (dată, tip) în `portofoliu()`, cu numărul de firme la fiecare grup. Datele nu sunt recalculate live la fiecare afișare — provin dintr-un model precalculat de un proces de fundal, actualizat la fiecare schimbare relevantă (vector fiscal, salariați, facturi).

Perioada de grație de la prima raportare SAF-T NU e implementată — nu există niciun calcul al ei în motorul de scadențe. Ecranul arată termenul nominal pentru toate firmele, indiferent dacă sunt la prima raportare sau nu; aplicarea grației rămâne, deocamdată, în sarcina contabilului.

[iConta.eu](/)
