---
title: Cum verific corectitudinea D300 folosind balanța?
description: Reconcilierea automată a iConta recalculează independent taxa colectată (cotele 21/11/9%) și taxa deductibilă (cotele 21/11%) din liniile de factură — pentru rândurile manuale, lanțul de regularizări și TVA la încasare, verificarea cu balanța contabilă rămâne necesară.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum verific corectitudinea D300 folosind balanța?

Aplicația efectuează deja o reconciliere automată înainte de a genera decontul, dar aceasta acoperă doar o parte din rândurile formularului. Pentru restul — mai ales operațiunile speciale și soldurile reportate — comparația cu balanța contabilă (conturile de TVA colectată, deductibilă și de decontări cu bugetul) rămâne pasul de verificare final.

## Temeiul legal

::: ghid-temei
„19  TOTAL TAXĂ COLECTATĂ (sumă de la rd. 1 până la rd. 18, cu excepţia celor de la rd. 3.1,
5.1, 7.1, 12.1, 12.2)”

„30  TOTAL TAXĂ DEDUCTIBILĂ (sumă de la rd. 20 până la rd. 28, cu excepţia celor de la rd.
20.1, 22.1, 26.1, 26.2)”
— OPANAF 174/2026, ANEXA 2
:::

## Ce acoperă reconcilierea automată și ce trebuie verificat manual cu balanța

Aplicația recalculează independent, printr-o interogare separată direct pe liniile brute de factură (fără să reutilizeze codul motorului principal), totalurile pe cote pentru taxa colectată (21/11/9%) și taxa deductibilă (21/11%). Dacă rezultatul nu coincide cu ce a calculat motorul principal, generarea decontului se blochează cu o eroare care indică ambele valori — o divergență aici înseamnă aproape sigur o eroare de date la nivel de factură.

Ce nu intră în această reconciliere, și trebuie confruntat separat cu balanța contabilă:
- rândurile completate manual (intracomunitar, taxare inversă, ajustări, compensație forfetară agricultor);
- lanțul de regularizări rd.36–45 (soldurile reportate, diferențele stabilite de organele fiscale);
- TVA la încasare (regim în care exigibilitatea nu urmează facturarea, ci încasarea efectivă).

## Ce se greșește în practică

- Se consideră că trecerea reconcilierii automate înseamnă că întregul decont e corect — de fapt acoperă doar cotele automate pe colectată/deductibilă.
- Nu se confruntă soldurile din conturile de TVA (4423/4424/4426/4427) cu soldurile reportate introduse manual în decont (rd.38/rd.41).
- Se ignoră firmele cu TVA la încasare la verificarea cu balanța, deși exigibilitatea acolo urmează un calendar diferit de cel al facturării.
- Se compară balanța cu totalurile finale (rd.19/rd.30) fără să se separe mai întâi rândurile automate de cele manuale — o eventuală diferență devine greu de localizat.

## Ce face iConta.eu

`d300_reconciliere.verifica_reconciliere` rulează ca pas obligatoriu în fluxul de generare, cu SQL propriu, independent de motorul principal (`d300.py`) — recalculează totalurile pe cote pentru colectată (R9/R10/R11) și deductibilă (R22/R23) direct din liniile brute de factură. O divergență blochează generarea și afișează ambele valori pentru investigare. Limita e declarată explicit în cod: reconcilierea NU acoperă rândurile manuale (intracomunitar, taxare inversă, ajustări), lanțul pro-rata/rd.36–45 și TVA la încasare — pentru acestea, verificarea cu balanța contabilă rămâne necesară.

[iConta.eu](/)
