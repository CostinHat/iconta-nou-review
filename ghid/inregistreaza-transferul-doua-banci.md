---
title: "Cum se înregistrează transferul între două bănci?"
description: "Contul contabil folosit pentru transferurile de disponibilități bănești între conturile bancare ale firmei, potrivit reglementărilor contabile OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează transferul între două bănci?

Mutarea de bani dintr-un cont bancar al firmei în altul nu e nici venit, nici cheltuială — e o mișcare internă de trezorerie, iar reglementările contabile îi rezervă un cont special, tocmai ca să nu se piardă în conturile obișnuite de disponibilități.

## Temeiul legal

::: ghid-temei
„În contul de viramente interne se înregistrează transferurile de disponibilități bănești între conturile la bănci, precum și între conturile la bănci și casieria entității."
— OMFP 1802/2014, Reglementări contabile, pct. 307 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Ce spune, punctual, reglementarea:

- Contul dedicat este **581 „Viramente interne"**, folosit pentru orice transfer de bani între conturile bancare ale entității, dar și între bancă și casierie — nu doar între două conturi bancare distincte.
- Rolul contului 581 e de **tranzit**: suma iese dintr-un cont de disponibilități (512, analitic pe banca sursă) prin 581 și intră în contul de disponibilități destinație (512, analitic pe banca destinație) tot prin 581, evitând ca operațiunea să apară, greșit, ca o plată sau o încasare cu efect asupra rezultatului.
- Deoarece transferul implică de regulă două date diferite (data debitării la banca sursă și data creditării la banca destinație, în funcție de durata procesării interbancare), contul 581 rămâne temporar cu sold, până la confirmarea ambelor mișcări prin extrasele de cont.

## Ce se greșește în practică

- Se înregistrează transferul direct de la un cont 512 la altul, fără trecerea prin 581 — funcționează contabil doar dacă ambele mișcări apar în aceeași zi și în aceeași înregistrare, dar nu reflectă corect decalajul real dintre extrasele celor două bănci.
- Se lasă soldul contului 581 nereconciliat la finalul lunii, deși el ar trebui să ajungă la zero odată ce ambele extrase de cont confirmă mișcarea — un sold rămas în 581 semnalează, de regulă, o sumă „în tranzit" neînregistrată corect la banca destinație.
- Se tratează transferul ca o cheltuială sau un venit financiar (comision, diferență de curs), atunci când singurul element care ar trebui înregistrat separat e comisionul bancar aferent transferului, nu suma transferată în sine.

## Ce face iConta.eu

Modulul de bancă al iConta.eu (`core/banca.py`) clasifică automat, din descrierea liniei de extras, operațiunile de tip „numerar" (retragere, alimentare ATM, depunere/ridicare numerar) și le contează prin contul **581 „Viramente interne"**, conform monografiei OMFP 1802/2014 — acesta acoperă transferurile dintre bancă și casierie. Pentru transferul de disponibilități **între două conturi bancare ale firmei** (nu bancă–casierie), aplicația nu are, la data acestui ghid, o recunoaștere automată a perechii de mișcări (ieșire dintr-un cont, intrare în altul) ca fiind unul și același transfer intern — contarea prin 581 pentru acest caz rămâne o operațiune manuală a contabilului la momentul procesării extraselor.

[iConta.eu](/)
