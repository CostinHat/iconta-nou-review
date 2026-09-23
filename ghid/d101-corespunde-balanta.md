---
title: "Ce fac dacă D101 nu corespunde cu balanța?"
description: "Descrie mecanismele de verificare confirmate în cod și cea mai frecventă cauză de neconcordanță."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă D101 nu corespunde cu balanța?

## Temeiul legal

::: ghid-temei
CF art.25 alin.(4) lit.a): cheltuiala cu impozitul pe profit (cont contabil 691) este nedeductibilă și trebuie adăugată înapoi la baza impozabilă.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `core/d101.py`, dosar de cercetare F027.
:::

iConta.eu citește datele pentru D101 direct din profilul firmei și din balanță, cu separare exploatare/financiar și rulează o reconciliere independentă la generare. Cea mai documentată cauză de neconcordanță este omiterea add-back-ului pentru cheltuiala cu impozitul pe profit (cont 691), nedeductibilă conform art.25 alin.(4) lit.a).

## Ce se greșește în practică

Verificați întâi soldul contului 691 și rândul P23 — dacă 691 are sold debitor iar P23 e zero, impozitul declarat e probabil subevaluat.

## Ce face iConta.eu

La generare, iConta.eu rulează o reconciliere independentă a bazei contabile (`core/d101_reconciliere.py`) și verifică `totalPlata_A` emis (`core/reconciliere_emis.py`), pe lângă avertismentul dedicat contului 691 descris mai sus. Datele sunt citite din profilul firmei și din balanță, cu separarea exploatare/financiar (clasele 76/66 = financiar, restul 7x/6x = exploatare) plus conturile 1012 (capital social), 1061 (rezervă deja constituită) și 691 pentru calculul rezervei legale. Conform surselor verificate, aplicația nu compară însă explicit rezultatul cu soldul contului de bilanț 4411 (impozit pe profit datorat) — verificările acoperă contul de cheltuială (691) și structura balanței, nu soldul de bilanț al obligației față de buget.

[iConta.eu](/)
