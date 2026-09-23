---
title: "Cum se decontează minusurile de inventar la gestionar"
description: "Notele contabile prin care o lipsă de inventar imputabilă se pune în sarcina gestionarului sau a unui terț, cu TVA aferentă valorii de imputare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se decontează minusurile de inventar la gestionar

Când o lipsă constatată la inventariere e imputabilă unei persoane, descărcarea de gestiune se dublează de o notă contabilă separată prin care paguba trece în sarcina acelei persoane.

## Temeiul legal

::: ghid-temei
"Rezultatul inventarierii se înregistrează în contabilitate potrivit reglementărilor contabile
aplicabile." — Legea 82/1991, art. 7 alin. (3)
:::

Legea cere ca rezultatul inventarierii — inclusiv decizia asupra cui îi este imputabilă o lipsă — să fie reflectat în contabilitate. Pentru mecanismul concret de imputare (contul folosit, calculul TVA aferent), dosarul de verificare pentru acest ghid nu conține o citare legală separată, verbatim, dedicată exclusiv acestui aspect — tratamentul descris mai jos reflectă direct implementarea din aplicație, construită pe principiile generale de înregistrare contabilă.

Important de reținut: **valoarea imputată nu e obligatoriu egală cu valoarea contabilă a lipsei** — sunt două sume distincte, iar diferența dintre ele are propriul tratament contabil.

## Ce se greșește în practică

- Se confundă valoarea contabilă a lipsei (cea descărcată din gestiune) cu valoarea de imputare (cea pusă în sarcina vinovatului) — pot fi sume diferite.
- Se aplică același cont de imputare indiferent dacă vinovatul e un salariat sau un terț, deși contul folosit diferă.
- Se omite calculul TVA aferent valorii de imputare.

## Ce face iConta.eu

Pentru un minus marcat drept **imputabil**, iConta.eu generează:

- descărcarea de gestiune la valoarea contabilă a lipsei, pe contul de stoc corespunzător;
- nota de imputare, la valoarea de imputare introdusă separat: 4282=7581 dacă vinovatul e un **salariat**, sau 461=7581 dacă e un **terț**;
- TVA aferentă (4427), calculată pe valoarea de imputare, nu pe valoarea contabilă a lipsei.

Cota de TVA trebuie introdusă explicit — aplicația nu are o cotă implicită, tocmai pentru a nu rămâne "în urma" unei eventuale schimbări legislative a cotei. Ca și la celelalte operațiuni de inventariere, nota afectează doar jurnalul contabil, nu și modulul de gestiune a stocurilor.

[iConta.eu](/)
