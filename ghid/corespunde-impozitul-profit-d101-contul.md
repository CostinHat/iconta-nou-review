---
title: "De ce nu corespunde impozitul pe profit din D101 cu contul 4411?"
description: "Explică onest ce verifică aplicația (contul 691 și structura balanței) și ce nu acoperă (soldul de bilanț 4411)."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# De ce nu corespunde impozitul pe profit din D101 cu contul 4411?

## Temeiul legal

::: ghid-temei
CF art.25 alin.(4) lit.a): cheltuiala cu impozitul pe profit (cont contabil 691) este nedeductibilă și trebuie adăugată înapoi la baza impozabilă.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `core/d101.py`, dosar de cercetare F027.
:::

Sursele verificate în acest dosar arată că motorul D101 verifică explicit contul 691 (cheltuiala cu impozitul pe profit, cont de rezultat) și structura balanței pe clase (66/76 financiar, 7x/6x exploatare), dar nu confirmă o comparație explicită cu soldul contului de bilanț 4411 (impozit pe profit datorat).

## Ce se greșește în practică

O neconcordanță între impozitul din D101 și soldul 4411 poate avea cauze contabile obișnuite (decalaje între cheltuiala înregistrată și obligația recunoscută, plăți anticipate deja înregistrate în 4411 etc.) care nu sunt documentate în acest dosar — nu putem oferi aici o explicație specifică fără riscul de a inventa un mecanism neverificat.

## Ce face iConta.eu

La generare, iConta.eu rulează o reconciliere independentă a bazei contabile (`core/d101_reconciliere.py`) și verifică `totalPlata_A` emis (`core/reconciliere_emis.py`), pe lângă avertismentul dedicat contului 691 descris mai sus. Datele sunt citite din profilul firmei și din balanță, cu separarea exploatare/financiar (clasele 76/66 = financiar, restul 7x/6x = exploatare) plus conturile 1012 (capital social), 1061 (rezervă deja constituită) și 691 pentru calculul rezervei legale. Conform surselor verificate, aplicația nu compară însă explicit rezultatul cu soldul contului de bilanț 4411 (impozit pe profit datorat) — verificările acoperă contul de cheltuială (691) și structura balanței, nu soldul de bilanț al obligației față de buget. Pentru o neconcordanță specifică cu 4411, verificați manual, împreună cu contabilul, cronologia înregistrărilor (impozit calculat vs. plăți anticipate deja înregistrate) — aplicația nu documentează, conform surselor verificate, un control automat dedicat acestei comparații.

[iConta.eu](/)
