---
title: "Cum declar regularizarea unui avans în D300?"
description: Exigibilitatea avansului e deja tratată automat la extragerea facturilor din decont. Pentru regularizarea propriu-zisă la factura finală, aplicația nu are un rând D300 dedicat avansului — doar mecanismul general de regularizare (R16/R30).
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum declar regularizarea unui avans în D300?

Nu există în D300 un rând sau un mecanism dedicat „regularizare avans". Ce există, verificat direct în cod, sunt două lucruri distincte: exigibilitatea automată a avansului la data emiterii facturii și, separat, notele contabile de regularizare la factura finală — care nu ating deloc rândurile decontului.

## Temeiul legal

::: ghid-temei
„Regularizări taxă dedusă" — eticheta oficială a rândului R30, `d300_manual_api.py`, confirmată contra structurii ANAF D300 v12 (OPANAF 174/2026)
:::

## Ce e deja automat: exigibilitatea avansului

Exigibilitatea TVA la avans (art. 282 alin. 2 lit. b din Codul fiscal, coroborat cu OMFP 1802/2014) e tratată automat la nivelul interogării de extragere a facturilor din decont: o factură de avans emisă intră automat în decontul **lunii de emitere**, exact ca orice altă factură — fără nicio intervenție manuală. Nu e nevoie de vreun rând special pentru asta în F251.

## Ce nu are rând D300 dedicat: regularizarea la factura finală

Modulul de avansuri produce doar notele contabile aferente regularizării la factura finală (conturile 409/419/4426/4427) — nu generează rânduri de decont. În codul citit al panoului manual (`d300_manual_api.py`) nu apare nicio mențiune „avans" — nu există o regulă sau un cod de rând specific pentru acest caz.

Dacă regularizarea la factura finală (diferență de cotă, anulare parțială etc.) nu e deja corect reflectată prin facturile propriu-zise ale perioadei, singura cale rămasă în F251 e mecanismul general de regularizare: **R16** pentru taxa colectată, **R30** pentru taxa dedusă — nu un rând specific „avans".

## Ce se greșește în practică

- Se caută un rând special „avans" în panoul de declarații — nu există.
- Se confundă modulul de note contabile pentru avansuri (care produce doar înregistrări 409/419/4426/4427) cu declararea efectivă a TVA în D300 — sunt module separate.

## Ce face iConta.eu

Avansul emis intră automat în decont la data emiterii facturii, fără intervenție manuală. Notele contabile de regularizare la factura finală se generează separat, din modulul de avansuri, și nu ating rândurile D300. Pentru orice diferență de TVA rămasă neacoperită de facturile propriu-zise, singura cale în F251 e regularizarea generală (R16/R30) — nu există un rând dedicat avansului.

[iConta.eu](/)
