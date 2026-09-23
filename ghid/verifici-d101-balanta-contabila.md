---
title: "Cum verifici D101 cu balanța contabilă?"
description: "Descrie mecanismele de verificare confirmate în cod: split exploatare/financiar, reconciliere independentă și avertismentul dedicat contului 691."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verifici D101 cu balanța contabilă?

## Temeiul legal

::: ghid-temei
CF art.25 alin.(4) lit.a): cheltuiala cu impozitul pe profit (cont contabil 691) este nedeductibilă și trebuie adăugată înapoi la baza impozabilă.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `core/d101.py`, dosar de cercetare F027.
:::

Datele pentru D101 sunt citite din profilul firmei și din balanța contabilă, cu separare exploatare/financiar (clasele 76/66 = financiar, restul 7x/6x = exploatare), plus conturile 1012 (capital social), 1061 (rezervă deja constituită) și 691 (cheltuiala cu impozitul pe profit) pentru calculul rezervei legale.

## Ce se greșește în practică

Cea mai frecventă cauză de neconcordanță este omiterea add-back-ului pentru cont 691 (art.25 alin.(4) lit.a)) — verificați întâi acest cont dacă rezultatul D101 nu corespunde așteptărilor.

## Ce face iConta.eu

La generare, iConta.eu rulează o reconciliere independentă a bazei contabile (`core/d101_reconciliere.py`) și verifică `totalPlata_A` emis (`core/reconciliere_emis.py`), pe lângă avertismentul dedicat contului 691 descris mai sus. Datele sunt citite din profilul firmei și din balanță, cu separarea exploatare/financiar (clasele 76/66 = financiar, restul 7x/6x = exploatare) plus conturile 1012 (capital social), 1061 (rezervă deja constituită) și 691 pentru calculul rezervei legale. Conform surselor verificate, aplicația nu compară însă explicit rezultatul cu soldul contului de bilanț 4411 (impozit pe profit datorat) — verificările acoperă contul de cheltuială (691) și structura balanței, nu soldul de bilanț al obligației față de buget.

[iConta.eu](/)
