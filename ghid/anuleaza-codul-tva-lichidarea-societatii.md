---
title: Cum se anulează codul de TVA la lichidarea societății?
description: De ce anularea codului de TVA la lichidare se depune manual la ANAF, nu prin iConta.eu, și ce confirmă dosarul de cercetare al funcționalității F057 despre acest blocaj.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se anulează codul de TVA la lichidarea societății?

Anularea codului de înregistrare în scopuri de TVA face parte din formalitățile de scoatere a societății din vectorul fiscal, alături de celelalte mențiuni legate de radiere. Din păcate, la acest pas, iConta.eu are o limitare cunoscută, pe care o comunicăm explicit mai jos.

## Temeiul legal

::: ghid-temei
„Declarația D700 (mențiuni vector fiscal) - RESPINS", stare „RESPINS 20.07.2026"
— FUNCTIONALITATI.csv, rândul F196
:::

Mențiunile privind vectorul fiscal (inclusiv scoaterea din evidența plătitorilor de TVA) se declară, în mod normal, prin formularul D700. Această funcționalitate este marcată explicit ca **respinsă** în evidența internă a funcționalităților iConta.eu, fără cod sursă asociat.

## Ce se greșește în practică

Se presupune uneori, prin analogie cu alte declarații generate automat de aplicație (de exemplu D230 sau D311), că și D700 poate fi completat și trimis direct din iConta.eu. Nu este cazul, iar motivul nu este doar o decizie de prioritizare a echipei de dezvoltare, ci și unul tehnic, confirmat separat: D700 este un formular de tip SmartPDF, nu un XML validabil ca alte declarații ANAF, iar orice încercare de validare standalone a unui XML pentru D700 prin validatorul disponibil local returnează eroare. Lipsește, în plus, actul normativ (instrucțiunile OPANAF) cu maparea câmp-cu-câmp necesară unei implementări corecte.

## Ce face iConta.eu

Pentru anularea codului de TVA la lichidarea societății, **iConta.eu nu generează și nu depune declarația D700** — acest pas rămâne în sarcina contabilului, depus manual, în afara aplicației, la organul fiscal competent, în momentul relevant al procesului de radiere (fie odată cu depunerea cererii de radiere la registrul comerțului, fie separat, conform procedurii ANAF în vigoare).

Ce acoperă în schimb aplicația sunt operațiunile contabile propriu-zise legate de lichidare — vânzarea activelor rămase (cu TVA colectată corect calculată, dacă societatea era plătitoare) și partajul final către asociați — nu și formalitățile declarative de scoatere din vectorul fiscal.

[iConta.eu](/)
