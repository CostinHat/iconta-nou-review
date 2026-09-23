---
title: "Ce curs BNR folosesc pentru reevaluarea disponibilităților în valută?"
description: Disponibilitățile bănești în valută se reevaluează lunar la cursul BNR din ultima zi bancară a lunii, nu la cursul zilei fiecărei operațiuni — diferența rezultată se recunoaște ca venit sau cheltuială din curs valutar.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce curs BNR folosesc pentru reevaluarea disponibilităților în valută?

Un cont bancar în valută nu rămâne „înghețat" la cursul din ziua în care a intrat fiecare sumă. La finalul fiecărei luni, soldul lui în valută se reevaluează la cursul BNR curent — separat de operațiunile efective (încasări, plăți), care rămân contabilizate fiecare la cursul zilei ei.

## Temeiul legal

::: ghid-temei
„La finele fiecărei luni, creanțele și datoriile în valută se evaluează la cursul de schimb al pieței valutare, comunicat de Banca Națională a României din ultima zi bancară a lunii în cauză. Diferențele de curs înregistrate se recunosc în contabilitate la venituri sau cheltuieli din diferențe de curs valutar, după caz." — OMFP 1802/2014 (Reglementările contabile), pct. 325 alin. (1). Alin. (2) lit. b) precizează explicit că evaluarea se aplică și „disponibilităților în valută și a altor valori de trezorerie".
:::

## Cursul folosit

Cursul de reevaluare este cel comunicat de BNR pentru **ultima zi bancară a lunii** — nu media lunii, nu cursul de la data ultimei operațiuni din cont. Reevaluarea se aplică tuturor elementelor „monetare" în valută: disponibilități bancare (5124), creanțe și datorii, nu și elementelor nemonetare (stocuri, imobilizări), care rămân la costul lor de intrare.

Diferența dintre soldul evaluat la cursul BNR de la finalul lunii și soldul evaluat la cursul folosit anterior (fie cursul de intrare al sumelor, fie cursul de la reevaluarea lunii precedente) se înregistrează ca venit din diferențe de curs favorabile (cont 765) sau cheltuială din diferențe de curs nefavorabile (cont 665).

## Ce se greșește în practică

- Se sare peste reevaluarea lunară a disponibilităților în valută, considerând-o necesară doar pentru creanțe și datorii comerciale — regula (pct. 325) acoperă explicit și disponibilitățile bănești.
- Se folosește cursul mediu al lunii sau cursul din ziua închiderii contabile, în loc de cursul BNR din **ultima zi bancară** a lunii respective.
- Se omite reevaluarea în lunile în care nu au avut loc mișcări în cont — reevaluarea se face pe sold, indiferent dacă a existat sau nu vreo tranzacție în luna respectivă.

## Ce face iConta.eu

Cursul BNR folosit pentru determinarea unui sold în valută la o dată dată provine din motorul de curs (`core/curs_bnr.py`) — ultimul curs BNR comunicat, valabil cel târziu la data cerută. Calculul diferenței față de cursul de evidență al soldului și recunoașterea ei pe 665/765 rămân, ca la orice reevaluare lunară, o operațiune realizată de contabil pe baza cursului preluat din motorul de curs. Dacă moneda soldului nu are curs BNR comunicat sau cursul găsit e prea vechi pentru pragul intern de siguranță, operațiunea e blocată cu un mesaj explicit, nu se aplică tăcut un curs aproximativ.

[iConta.eu](/)
