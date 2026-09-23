---
title: Cum se înregistrează raportul Z în contabilitatea unui restaurant?
description: Notă contabilă pe două cote de TVA (11% mâncare, 21% alcool și sucuri), pe numerar și pe card — construită din Raportul Z, prin import de fișier AMEF sau introducere manuală.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se înregistrează raportul Z în contabilitatea unui restaurant?

Pentru un restaurant, Raportul Z e forma tipică prin care intră în contabilitate vânzarea zilnică — pentru că serviciile de restaurant/catering au un tratament de TVA specific: cotă redusă, cu excepții.

## Temeiul legal

::: ghid-temei
„Cota redusă de 11% se aplică asupra bazei de impozitare pentru următoarele prestări de servicii și/sau livrări de bunuri: [...] n) serviciile de restaurant și de catering, cu excepția băuturilor alcoolice, precum și a băuturilor nealcoolice care se încadrează la codul NC 2202." — Codul fiscal, art. 291 alin. (2) lit. n), modificat de Legea 141/2025, în vigoare de la 1 august 2025
:::

## Cum arată nota

Din 1 august 2025, Codul fiscal are doar două cote de TVA: 21% standard (art. 291 alin. (1)) și 11% redusă (art. 291 alin. (2)) — cotele vechi de 5% și 9% au fost abrogate. Serviciile de restaurant intră la 11%, **cu excepția** băuturilor alcoolice și a celor nealcoolice cu cod NC 2202 (energizante, ape gazoase/aromatizate cu zahăr, sucuri), care rămân la 21%.

Pe ecranul „Raport Z" din iConta.eu, câmpurile pentru introducerea manuală reflectă direct această împărțire: „Total 11% (mâncare)" și „Total 21% (alcool, sucuri)". Din aceste totaluri (cu TVA inclus), aplicația extrage TVA prin „sută mărită" — `total × 11/111`, respectiv `total × 21/121` — și generează nota:

- `5311 = 707` pentru numerar
- `5125 = 707` pentru card
- `707 = 4427` pentru TVA colectată pe fiecare cotă

Dacă în locul introducerii manuale se importă direct fișierul AMEF (p7b/XML), aplicația citește orice cotă apărută efectiv în raportul casei de marcat, nu doar 11%/21% — util dacă restaurantul mai vinde și produse la o altă cotă (de exemplu produse nealimentare).

## Ce se greșește în practică

Aplicarea vechii cote de 9% (abrogată de la 1 august 2025) pentru mâncare, în loc de 11%. A doua greșeală: încadrarea greșită a băuturilor — nu doar alcoolul iese din cota redusă, ci și băuturile nealcoolice cu cod NC 2202, o categorie mai largă decât „alcool" (energizante, sucuri, ape gazoase/aromatizate cu zahăr intră aici).

## Ce face iConta.eu

Calea manuală de pe ecranul „Raport Z" separă direct suma pe cele două cote relevante pentru HoReCa și calculează automat TVA prin sută mărită, fără rotunjiri manuale. Calea de import citește direct structura raportului Z din fișierul AMEF (conform OPANAF 146/2018), cotă cu cotă, pentru cazurile în care restaurantul vinde și la alte cote decât 11%/21%.

[iConta.eu](/)
