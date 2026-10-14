---
title: "Cum declar o factură omisă din D300?"
description: Aplicația nu are un rând sau o rută dedicată pentru „factură omisă" — singura indicație directă din cod vizează cotele respinse de validator, prin extensie aplicabilă și facturii complet omise. Alegerea între a introduce factura sau a declara o regularizare rămâne o decizie a contabilului.
published: 2026-09-23
modified: 2026-10-13
poarta: v1
---

# Cum declar o factură omisă din D300?

Nu există un rând sau un flux dedicat „factură omisă" în panoul manual „Rând manual D300”. Ce urmează e reconstituit din singurele indicații directe găsite în cod — nu dintr-o regulă explicită pentru acest caz.

## Temeiul legal

::: ghid-temei
„Decontul de taxă întocmit de persoanele înregistrate conform art. 316 va cuprinde [...] suma taxei colectate a cărei exigibilitate ia naștere în perioada fiscală de raportare și, după caz, suma taxei colectate care nu a fost înscrisă în decontul perioadei fiscale în care a luat naștere exigibilitatea taxei [...]”
— Codul fiscal, art. 323 alin. (2) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Datele înscrise incorect într-un decont de taxă se pot corecta prin decontul unei perioade fiscale ulterioare și se vor înscrie la rândurile de regularizări.”
— Codul fiscal, art. 323 alin. (3) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„În situația în care nu sunt îndeplinite condițiile și formalitățile de exercitare a dreptului de deducere în perioada fiscală de declarare sau în cazul în care nu s-au primit documentele de justificare a taxei prevăzute la art. 299, persoana impozabilă își poate exercita dreptul de deducere prin decontul perioadei fiscale în care sunt îndeplinite aceste condiții și formalități sau printr-un decont ulterior, dar în cadrul termenului de prescripție prevăzut în Codul de procedură fiscală [...]”
— Codul fiscal, art. 301 alin. (2) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

## Singura instrucțiune directă din cod

Pentru facturile cu o cotă în afara 21/11/9/5%, motorul D300 tratează situația explicit ca sub-declarare de TVA colectată, cu o indicație clară: cotele istorice 19/5% nu au un rând acceptat de validatorul ANAF v12 — soluția e fie corectarea cotei facturii, fie tratarea ei ca regularizare, pe rândul 16.

Aceeași logică de bază e confirmată în textul de ajutor deja publicat pentru „Rând manual D300”: „Dublă numărare: nu introduce manual o sumă care vine deja dintr-o factură."

## Pentru o factură complet omisă

Codul nu tratează explicit acest caz, dar prin extensie logică a acelorași principii de mai sus:

- **Dacă perioada e încă deschisă**, calea corectă e introducerea facturii reale în aplicație — nu un rând manual în „Rând manual D300”. Gărzile anti-dublă-numărare ar respinge oricum coexistența: dacă factura e introdusă ulterior pe același cod de rând pentru aceeași perioadă, iar o sumă manuală există deja acolo, motorul ridică eroare de dublă numărare.
- **Dacă perioada e deja depusă/închisă**, corecția intră în sfera regularizărilor manuale — rândul 16 pentru taxa colectată, rândul 33 pentru taxa dedusă.

Nu există în cod o distincție explicită „perioadă deschisă vs. închisă" care să dicteze automat alegerea între cele două căi — rămâne o decizie profesională a contabilului.

## Ce se greșește în practică

Se introduce direct o sumă manuală pentru factura omisă, deși perioada e încă deschisă și factura poate fi înregistrată normal — la introducerea ulterioară a facturii reale pe același cod de rând, gărzile anti-dublă-numărare blochează situația.

## Ce face iConta.eu

„Rând manual D300” nu are o rută dedicată „factură omisă" — panoul acceptă doar rândurile din allow-list, cu validare explicită împotriva dublei numărări față de facturile deja înregistrate în perioadă. Alegerea între a introduce factura propriu-zisă sau a declara o regularizare manuală (rândurile 16/33) rămâne o decizie a contabilului.

[iConta.eu](/)
