---
title: "Evaluarea stocurilor în valută: cursul aplicabil"
description: Stocurile sunt elemente „nemonetare" — intră în gestiune la cursul BNR de la data achiziției (sau a recepției, dacă factura vine ulterior) și rămân la acea valoare, spre deosebire de disponibilitățile bănești și creanțele/datoriile în valută, care se reevaluează lunar.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Evaluarea stocurilor în valută: cursul aplicabil

O marfă achiziționată în valută intră în gestiune la un curs stabilit o singură dată, la achiziție — și rămâne acolo. Spre deosebire de un cont bancar în valută sau de o creanță/datorie în valută, care se reevaluează lunar la cursul BNR curent, stocurile nu se „actualizează" de fiecare dată când se schimbă cursul.

## Temeiul legal

::: ghid-temei
„Caracteristica esențială a unui element nemonetar este absența unui drept de a primi (sau a unei obligații de a furniza) un număr fix sau determinabil de unități monetare. Exemplele includ: sumele plătite în avans pentru bunuri și servicii; imobilizări necorporale; stocuri; imobilizări corporale […]." — OMFP 1802/2014 (Reglementările contabile), pct. 315 alin. (3). „O tranzacție în valută trebuie înregistrată inițial la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii." — pct. 319.
:::

## Cursul aplicat la intrarea în gestiune

Stocurile achiziționate în valută intră în gestiune la cursul BNR de la data operațiunii — data facturii, dacă marfa sosește însoțită de ea, sau data recepției, dacă marfa vine doar cu aviz de însoțire, urmând ca factura să sosească ulterior (pct. 314 alin. (4)). Odată stabilită, această valoare rămâne costul de intrare al stocului.

## De ce stocurile nu se reevaluează lunar

Regula reevaluării lunare la cursul BNR (pct. 325) se aplică elementelor **monetare** — disponibilități bănești, creanțe, datorii — nu și celor **nemonetare**, categorie în care stocurile intră explicit (pct. 315 alin. (3)). O marfă cumpărată la un curs de 4,97 lei/euro rămâne la acea valoare în gestiune, indiferent cum evoluează ulterior cursul BNR — spre deosebire de soldul unui cont bancar în euro, care se ajustează lunar.

## Ce se greșește în practică

- Se reevaluează lunar valoarea stocurilor în valută la cursul BNR curent, tratându-le ca element monetar — stocurile rămân la costul de intrare, nu se ajustează la fluctuațiile de curs.
- Se folosește, la intrarea în gestiune, cursul din ziua în care marfa a fost plătită (dacă plata se face ulterior recepției), în loc de cursul de la data recepției sau al facturii, după caz.
- Se confundă evaluarea stocului (nemonetar, la cost istoric) cu evaluarea datoriei către furnizor pentru acel stoc (element monetar, reevaluabil lunar) — sunt două valori distincte în contabilitate, care pot diverge după recepție.

## Ce face iConta.eu

Cursul BNR folosit la intrarea în gestiune a unei mărfi achiziționate în valută se determină pentru data operațiunii, prin motorul de curs (`core/curs_bnr.py`), aceeași sursă folosită pentru orice altă operațiune valutară din aplicație. Ca regulă contabilă (pct. 315 alin. (3), pct. 325), stocurile — element nemonetar — nu se reevaluează lunar precum disponibilitățile, creanțele sau datoriile în valută; ele rămân la costul lor de intrare, stabilit o singură dată prin cursul BNR al operațiunii.

[iConta.eu](/)
