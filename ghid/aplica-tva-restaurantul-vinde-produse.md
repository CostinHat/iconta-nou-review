---
title: Cum se aplică TVA când restaurantul vinde produse cu cote diferite?
description: Un bon cu produse la cote diferite (meniu 11%, bere 21%) se împarte pe linii, fiecare cu cota ei — cu o excepție: ambalajul livrării la pachet urmează cota alimentului, ca livrare accesorie.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se aplică TVA când restaurantul vinde produse cu cote diferite?

Când pe același bon sau aceeași factură apar produse la cote diferite — de exemplu un meniu la 11% și o băutură alcoolică la 21% — nu se aplică o cotă „medie" sau dominantă pe tot documentul. TVA se calculează separat, linie cu linie, pe fiecare cotă în parte.

## Temeiul legal

::: ghid-temei
Un restaurant care vinde mâncare pentru a fi servită în afara locației nu realizează o prestare de servicii de restaurant, ci o livrare de bunuri, pentru care aplică cota redusă aferentă alimentului, „inclusiv pentru caserola sau paharele în care sunt servite alimentele sau băuturile nealcoolice, [...] acestea fiind livrări accesorii, nu un scop în sine pentru client” — principiu din normele de aplicare a art. 291 Cod fiscal (HG 1/2016), păstrat ca interpretare pentru cotele actuale (21%/11%).
:::

## Regula de bază: fiecare produs, cota lui

Un bon cu meniu servit la masă (11%), o bere (21%) și o apă plată servită la masă (11%) generează trei linii de calcul TVA distincte — nu se rotunjește totul la cota predominantă, nici nu se emite un total unic pe o singură cotă.

## Excepția: livrările accesorii urmează produsul principal

Când vinzi mâncare la pachet, fără servicii conexe (deci livrare de bunuri, nu serviciu de restaurant), tot ce servește exclusiv livrării — caserola, paharul, punga — nu se facturează separat la cotă proprie, ci **urmează cota alimentului principal**, chiar dacă valoarea ambalajului ar fi evidențiată separat pe bon. Ambalajul e o livrare accesorie, nu o operațiune de sine stătătoare.

Această regulă nu se extinde la produsele care au propria lor excepție legală — o băutură alcoolică rămâne la 21% indiferent cu ce e vândută împreună, pentru că excepția ei vine direct din lege, nu din calitatea de „accesoriu".

## Ce se greșește în practică

- Se aplică o singură cotă pe întreg bonul, de regulă cea a produsului predominant valoric, în loc de calcul separat pe linie.
- Se facturează separat, la cotă standard, ambalajul unei livrări la pachet — deși ar trebui să urmeze cota alimentului, ca livrare accesorie.
- Se confundă regula accesoriului (ambalaj care urmează produsul) cu ideea greșită că orice produs de pe același bon „ia" cota produsului principal — regula nu se aplică băuturilor cu excepție proprie (alcool, NC 2202).

## Ce face iConta.eu

Motorul de potrivire cotă (`core/cote_tva.py`) încadrează fiecare produs/serviciu individual, pe baza denumirii lui, nu pe baza documentului în ansamblu — astfel încât un bon cu produse la cote diferite generează automat liniile de TVA corecte pentru fiecare. Regula ambalajului ca livrare accesorie ține de interpretarea normelor, nu e un câmp separat în aplicație — se aplică manual, la nivelul deciziei de facturare a ambalajului împreună cu alimentul.

[iConta.eu](/)
