---
title: "Cum verific D390 cu decontul D300?"
description: Pentru operațiunile intracomunitare reclasificate, D390 și D300 nu se compară printr-un buton dedicat — coerența e garantată structural, dintr-o singură sursă de date citită identic de ambele declarații.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum verific D390 cu decontul D300?

Nu există în panoul de declarații un buton „compară D390 cu D300". Mecanismul real e altul, și mai puternic decât o simplă verificare: pentru operațiunile reclasificate, coerența dintre cele două declarații e imposibil de rupt, pentru că se scriu dintr-o singură sursă.

## Temeiul legal

::: ghid-temei
„Livrări intracomunitare de bunuri, scutite conform art. 294 alin. (2) lit. a) și d) din Codul fiscal" — eticheta oficială a rândului R1, `d300_manual_api.py`, confirmată contra structurii ANAF D300 v12 (OPANAF 174/2026)
:::

## Mecanismul: o sursă unică, nu o comparație

Reclasificările bun-vs-serviciu ale operațiunilor intracomunitare (livrare sau achiziție) se scriu într-un singur tabel, `d390_reclasificare`, populat din panoul D390. Acest tabel e **citit identic** de ambele generatoare de declarație: D300 prin `_incarca_reclasificari` → `pull_reclasificari`, D390 prin `calculeaza` → `pull_reclasificari`, aceeași funcție.

Efectul, confirmat prin teste interne: după reclasificarea unei livrări IC emise ca „P" (serviciu), `D300.R3_1` devine egal cu suma serviciilor „P" din rezumatul D390, iar `R1_1` (bunuri) dispare din D300 — operațiunea e **mutată**, nu adăugată în plus. Simetric, pentru achizițiile IC reclasificate „S" (serviciu): `D300.R7_1` egal cu suma „S" din D390, cu oglinda deductibilă rd.20 (net zero).

Pentru că o singură scriere în `d390_reclasificare` schimbă simultan ambele declarații, o divergență între ele, pentru operațiunile reclasificate, e structural imposibilă — nu pentru că există un instrument care o verifică și o corectează, ci pentru că ambele citesc aceeași sursă.

## Ce nu există

Nu e un ecran sau o rută API dedicată „verifică D390 vs D300" în sursele citite — nici în panoul manual F251, nici altundeva în motorul D300. Verificarea/comparația celor două declarații, ca funcționalitate separată pe care contabilul o declanșează, e documentată în alt loc din aplicație, nu face parte din F251.

## Ce se greșește în practică

Se caută un buton dedicat „compară D390 cu D300" în ecranul de declarații al F251 — nu există unul aici; coerența pentru operațiunile reclasificate e garantată de motor prin sursa unică de date, nu printr-o acțiune de verificare separată.

## Ce face iConta.eu

Pentru operațiunile reclasificate prin panoul D390, D300 citește aceeași sursă (`d390_reclasificare`) prin aceeași funcție folosită și de D390 — coerența dintre cele două declarații e structurală, nu rezultatul unei verificări separate din F251. O funcționalitate dedicată de comparație/verificare a celor două declarații e documentată separat.

[iConta.eu](/)
