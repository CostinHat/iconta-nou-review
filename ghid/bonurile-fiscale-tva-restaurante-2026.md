---
title: Bonurile fiscale și TVA în restaurante 2026
description: De la 1 august 2025, TVA pentru restaurant/catering e 11%, cu excepția băuturilor alcoolice și a celor nealcoolice cu cod NC 2202, care rămân la 21%. Plus ce nu acoperă încă aplicația — D394.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Bonurile fiscale și TVA în restaurante 2026

Pentru un restaurant care vinde prin bonuri fiscale (fără factură, conform excepției din Codul fiscal), regula de TVA de reținut în 2026 e simplă în structură, dar cu o excepție care se ratează des.

## Temeiul legal

::: ghid-temei
„Cota standard se aplică asupra bazei de impozitare pentru operațiunile impozabile care nu sunt scutite de taxă sau care nu sunt supuse cotei reduse, iar nivelul acesteia este 21%." / „Cota redusă de 11% se aplică asupra bazei de impozitare pentru următoarele [...]: n) serviciile de restaurant și de catering, cu excepția băuturilor alcoolice, precum și a băuturilor nealcoolice care se încadrează la codul NC 2202." — Codul fiscal, art. 291 alin. (1) și alin. (2) lit. n), ambele modificate de Legea 141/2025, în vigoare de la 1 august 2025
:::

## Regula 2026

Din 1 august 2025 există doar două cote de TVA în Codul fiscal — cotele intermediare de 5% și 9% au fost abrogate. Pentru servicii de restaurant și catering:

- **11%** — mâncarea și, în general, alimentele/băuturile care nu intră în excepție.
- **21%** — băuturile alcoolice **și** băuturile nealcoolice cu cod NC 2202 (energizante, ape gazoase sau aromatizate cu zahăr, sucuri) — o excepție mai largă decât „doar alcoolul", care se ratează des tocmai pentru că numele articolului menționează explicit doar băuturile alcoolice.

Această regulă e mai largă decât forma inițială a articolului din 2016, care excepta de la cota redusă doar băuturile alcoolice (cu o nuanță pentru bere la un cod NC specific) — sfera excepției s-a extins ulterior și la băuturile nealcoolice NC 2202.

## Ce nu acoperă (încă) mecanismul din aplicație

Vânzările înregistrate prin Raportul Z (sursă `amef` sau `horeca_z`) **nu apar încă** în declarația informativă D394 — acest gol e confirmat direct de codul aplicației, care marchează explicit că sumele rămân 0 pentru operațiunile pe facturi simplificate/AMEF, până la construirea integrării. Nu presupune un flux automat spre D394 dacă ții evidența unui restaurant prin acest mecanism.

## Ce se greșește în practică

Aplicarea cotei vechi de 9% (abrogată din august 2025) în loc de 11%. A doua greșeală: încadrarea la 11% a băuturilor nealcoolice îndulcite/energizante, pentru că „nu sunt alcool" — dar codul NC 2202 le scoate oricum din cota redusă.

## Ce face iConta.eu

Ecranul „Raport Z" separă explicit totalul pe cele două cote relevante — „Total 11% (mâncare)" și „Total 21% (alcool, sucuri)" — și calculează TVA prin sută mărită pentru fiecare. Nu generează automat rânduri pentru D394 din aceste note, pentru că integrarea respectivă nu există încă în aplicație — de reținut dacă firma are și obligația acestei declarații.

[iConta.eu](/)
