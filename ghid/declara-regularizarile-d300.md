---
title: "Unde se declară regularizările în D300?"
description: Regularizările D300 se introduc printr-un panou manual dedicat, separat de motorul care generează rândurile din facturi — cu o listă fixă de rânduri acceptate și gărzi împotriva dublei numărări.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Unde se declară regularizările în D300?

Regularizările de TVA nu rezultă automat din facturile perioadei — se introduc explicit, printr-un panou manual dedicat, separat de motorul de calcul al decontului. Mai jos, exact ce rânduri acceptă panoul și cum funcționează mecanismul.

## Temeiul legal

::: ghid-temei
„Regularizări taxă colectată" — eticheta oficială a rândului R16
„Regularizări taxă dedusă" — eticheta oficială a rândului R30
— `d300_manual_api.py`, confirmate contra structurii ANAF D300 v12 (OPANAF 174/2026)
:::

## Rândurile de regularizare acceptate

Panoul manual acceptă o listă fixă (allow-list) de coduri de rând. Pentru regularizări, cele relevante sunt:

- **R16** — „Regularizări taxă colectată" — se oglindește automat în totalul taxei colectate (rd.17), la generarea decontului.
- **R30** — „Regularizări taxă dedusă" — intră direct în calculul totalului taxei deduse (rd.32).
- **R2, R4, R6, R8** — regularizări specifice operațiunilor intracomunitare (livrări bunuri, prestări servicii, achiziții bunuri, achiziții servicii), fiecare cu oglinda ei deductibilă unde e cazul (R19 pentru R6, R21 pentru R8).

Toate aceste coduri apar, în motorul D300, **doar** în formulele de însumare (rd.17/rd.27) — niciodată ca țintă a unei atribuiri automate din facturi. Sunt 100% manuale.

## Ce NU e o regularizare manuală

Rândurile computate — R17, R27, R28, R31, R32, R33, R34, R37, R40, R41, R42 — nu sunt în allow-list, indiferent de context. Nu pot fi introduse manual prin acest panou, chiar dacă tema pare de „ajustare" sau „regularizare" a unei sume.

## Mecanismul tehnic

Rândurile se introduc prin `POST /tenants/{id}/d300-manual` (an, lună, rând, bază, TVA, descriere), cu validare că rândul e în allow-list și nu e deja derivat automat din facturile perioadei. Se persistă în tabelul `d300_manual` și se recitesc automat la generarea decontului — atât la preview, cât și la depunerea efectivă, cu paritate garantată între cele două căi (test dedicat confirmă XML identic generat din baza de date și din parametru).

## Ce se greșește în practică

- Se încearcă introducerea manuală a unui rând computat (ex. R31, ajustarea pro-rata) crezând că e o formă de „regularizare" — rândul nu apare în lista de rânduri disponibile, pentru că nu e permis manual.
- Se introduce manual o sumă care e deja derivată automat dintr-o factură a perioadei — aplicația respinge cererea (dublă numărare).

## Ce face iConta.eu

Panoul din ecranul de declarații oferă exact lista rândurilor de regularizare acceptate (R2, R4, R6, R8, R16, R19, R21, R30), cu etichetele oficiale ANAF, validare împotriva dublei numărări cu facturile deja înregistrate și persistență cu paritate garantată între preview și depunere.

[iConta.eu](/)
