---
title: Ce cotă de TVA se aplică alimentelor servite în restaurant?
description: Alimentele servite la masă, ca parte a serviciului de restaurant, intră la cota redusă de 11% — chiar și un desert dulce, pentru care excepția „zahăr ≥10g/100g" nu se aplică în acest context.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce cotă de TVA se aplică alimentelor servite în restaurant?

Alimentele servite la masă, ca parte a unui serviciu de restaurant sau catering, beneficiază de cota redusă de 11% — cu o singură excepție relevantă pentru alimente în acest context: cea legată de băuturi, nu de conținutul de zahăr al mâncării.

## Temeiul legal

::: ghid-temei
Cota redusă de 11% se aplică pentru „serviciile de restaurant și de catering, cu excepția băuturilor alcoolice, precum și a băuturilor nealcoolice care se încadrează la codul NC 2202” — Codul fiscal, art. 291 alin. (2) lit. n). Textul nu exclude alimentele pe criteriul conținutului de zahăr.
:::

## Regula pentru alimentele servite la masă

Când alimentul e servit ca parte a mesei, în cadrul serviciului de restaurant (deservire, spațiu de consum, farfurie/tacâmuri), operațiunea e integral „serviciu de restaurant" — inclusiv desertul, prăjitura sau alt preparat dulce servit ca parte a mesei intră la cota de 11%. Excepția explicită de la lit. n) vizează **doar băuturile** (alcoolice și NC 2202), nu conținutul de zahăr al mâncării.

Excepția „alimente cu zahăr adăugat ≥10g/100g" există în lege, dar e legată de **livrarea de bunuri** (art. 291 alin. (2) lit. b) — de exemplu, o prăjitură vândută la raft, într-un magazin, fără servicii conexe. Nu se transferă automat asupra unei prăjituri servite la masă ca parte a unui meniu de restaurant.

## Când alimentul NU mai e „servit în restaurant"

Dacă restaurantul vinde același preparat la pachet, fără servicii conexe (fără deservire, fără consum pe loc), operațiunea devine livrare de bunuri, nu serviciu de restaurant — și atunci cota corectă e cea a alimentului livrat, cu excepțiile proprii livrării de bunuri (inclusiv, dacă e cazul, excepția de zahăr).

## Ce se greșește în practică

Se aplică excepția „zahăr ≥10g/100g" și pentru desertul servit la masă, tratându-l ca la 21% — deși legea leagă acea excepție de livrarea de bunuri, nu de serviciul de restaurant. A doua greșeală frecventă: se aplică o singură cotă pe tot bonul, ignorând că băuturile (nu alimentele) sunt cele care pot avea o cotă diferită.

## Ce face iConta.eu

Categoria `restaurant_catering` din `core/cote_tva.py` acoperă alimentele servite ca parte a mesei la cota de 11%, distinct de excepțiile listate în `EXCEPTII_21` (băuturi alcoolice, băuturi NC 2202, suplimente, alimente cu zahăr pentru livrare de bunuri). Motorul de potrivire cotă folosește contextul denumirii produsului pentru a stabili încadrarea corectă linie cu linie.

[iConta.eu](/)
