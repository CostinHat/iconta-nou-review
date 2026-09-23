---
title: "Cum declar o factură omisă din D300?"
description: Aplicația nu are un rând sau o rută dedicată pentru „factură omisă" — singura indicație directă din cod vizează cotele respinse de validator, prin extensie aplicabilă și facturii complet omise. Alegerea între a introduce factura sau a declara o regularizare rămâne o decizie a contabilului.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum declar o factură omisă din D300?

Nu există un rând sau un flux dedicat „factură omisă" în panoul manual F251. Ce urmează e reconstituit din singurele indicații directe găsite în cod — nu dintr-o regulă explicită pentru acest caz.

## Temeiul legal

::: ghid-temei
„Regularizări taxă colectată" — eticheta oficială a rândului R16, `d300_manual_api.py`, confirmată contra structurii ANAF D300 v12 (OPANAF 174/2026)
:::

## Singura instrucțiune directă din cod

Pentru facturile cu o cotă în afara 21/11/9/5%, motorul D300 tratează situația explicit ca sub-declarare de TVA colectată, cu o indicație clară: cotele istorice 19/5% nu au un rând acceptat de validatorul ANAF v12 — soluția e fie corectarea cotei facturii, fie tratarea ei ca regularizare, pe rândul R16.

Aceeași logică de bază e confirmată în textul de ajutor deja publicat pentru F251: „Dublă numărare: nu introduce manual o sumă care vine deja dintr-o factură."

## Pentru o factură complet omisă

Codul nu tratează explicit acest caz, dar prin extensie logică a acelorași principii de mai sus:

- **Dacă perioada e încă deschisă**, calea corectă e introducerea facturii reale în aplicație — nu un rând manual în F251. Gărzile anti-dublă-numărare ar respinge oricum coexistența: dacă factura e introdusă ulterior pe același cod de rând pentru aceeași perioadă, iar o sumă manuală există deja acolo, motorul ridică eroare de dublă numărare.
- **Dacă perioada e deja depusă/închisă**, corecția intră în sfera regularizărilor manuale — R16 pentru taxa colectată, R30 pentru taxa dedusă.

Nu există în cod o distincție explicită „perioadă deschisă vs. închisă" care să dicteze automat alegerea între cele două căi — rămâne o decizie profesională a contabilului.

## Ce se greșește în practică

Se introduce direct o sumă manuală pentru factura omisă, deși perioada e încă deschisă și factura poate fi înregistrată normal — la introducerea ulterioară a facturii reale pe același cod de rând, gărzile anti-dublă-numărare blochează situația.

## Ce face iConta.eu

F251 nu are o rută dedicată „factură omisă" — panoul acceptă doar rândurile din allow-list, cu validare explicită împotriva dublei numărări față de facturile deja înregistrate în perioadă. Alegerea între a introduce factura propriu-zisă sau a declara o regularizare manuală (R16/R30) rămâne o decizie a contabilului.

[iConta.eu](/)
