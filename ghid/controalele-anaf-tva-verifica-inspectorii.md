---
title: "Controalele ANAF pe TVA: ce verifică inspectorii în 2026"
description: "Ce tip de inspecție fiscală poate declanșa ANAF pe TVA, cum se stabilește riscul unei firme și ce presupune concret o inspecție generală sau parțială."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Controalele ANAF pe TVA: ce verifică inspectorii în 2026

Un control ANAF pe TVA nu apare din senin: firma e mai întâi încadrată într-o clasă de risc fiscal, pe baza analizei de risc a organului fiscal, iar procedurile de administrare (inclusiv probabilitatea unei inspecții) depind de această clasă.

## Temeiul legal

::: ghid-temei
„În cazul creanțelor fiscale administrate de organul fiscal central, procedurile de administrare se realizează în funcție de clasa/subclasa de risc fiscal în care sunt încadrați contribuabilii ca urmare a analizei de risc efectuate de organul fiscal. [...] Contribuabilii se încadrează în 3 clase principale de risc [...]: a) contribuabili cu risc fiscal mic; b) contribuabili cu risc fiscal mediu; c) contribuabili cu risc fiscal ridicat."
— Legea 207/2015 (Codul de procedură fiscală), art. 7 alin. (5)-(6) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce înseamnă, structural, un control de TVA:

- Inspecția fiscală generală verifică modul de îndeplinire a **tuturor** obligațiilor fiscale și a altor obligații prevăzute de legislația fiscală și contabilă ale firmei, pe o perioadă determinată (art. 115 alin. (1) lit. a) din Codul de procedură fiscală).
- Inspecția fiscală parțială verifică una sau mai multe obligații punctuale — de exemplu doar TVA — pentru o perioadă determinată (art. 115 alin. (1) lit. b).
- Contribuabilul nu poate contesta modul în care a fost stabilită clasa/subclasa de risc (art. 7 alin. 11), iar cei cu risc ridicat care nu remediază riscurile notificate în cele 30 de zile de la notificarea de conformare sunt supuși obligatoriu unei inspecții fiscale sau unei verificări documentare (art. 121^1 alin. (2) și (4)).

## Ce se greșește în practică

- Se crede că un control e mereu precedat de o „selecție aleatorie" — de fapt criteriile de risc (istoricul de conformare, coerența declarațiilor, corelațiile D300-D394-D112 etc.) influențează direct probabilitatea și tipul de verificare.
- Se pregătesc documentele doar pentru perioada „suspectă", ignorând faptul că o inspecție generală poate acoperi toate obligațiile fiscale ale firmei, nu doar TVA.
- Se ignoră notificările de remediere a riscurilor fiscale — netratarea lor înăuntrul termenului atrage automat inspecție sau verificare documentară.

## Ce face iConta.eu

iConta.eu **nu simulează** analiza de risc a ANAF și nu are acces la criteriile interne folosite de organul fiscal pentru încadrarea în clase de risc — acestea nu sunt publice. Aplicația are însă un motor propriu de urmărire a conformării (`core/control_fiscal_api.py`) care calculează, pe baza vectorului fiscal al firmei, ce declarații sunt datorate, care au fost depuse și unde există discrepanțe (declarații lipsă, depuse fără obligație, sau contradictorii) — util pentru a reduce exact genul de neconcordanțe care atrag atenția unui inspector, dar fără să fie un instrument de predicție a controalelor ANAF.

[iConta.eu](/)
