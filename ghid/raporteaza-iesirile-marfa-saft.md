---
title: "Cum se raportează ieșirile de marfă în SAF-T?"
description: "Structura oficială „Movement of Goods” din fișierul SAF-T (D406), nomenclatorul tipurilor de mișcări de stoc și când se cere efectiv raportarea lor."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează ieșirile de marfă în SAF-T?

Spre deosebire de avansurile de trezorerie, care se pierd în masa generală a înregistrărilor contabile din D406, mișcările de stoc au o secțiune proprie, dedicată, în structura oficială SAF-T: „Movement of Goods". Dar structura dedicată nu înseamnă că raportarea ei e cerută lunar, la fel ca restul fișierului.

## Temeiul legal

::: ghid-temei
„Movement of Goods (Mişcări de bunuri): Conţine detalii cu privire la mişcarea bunurilor, precum numărul total de mişcări în perioada selectată, total cantitate primită, total cantitate ieşită, referinţa unică a fiecărei mişcări de bunuri şi data fiecărei mişcări de bunuri, data postării fiecărei mişcări de bunuri, tipul mişcării de bunuri (conform nomenclatorului Codificare mişcări de [...])."
— OPANAF nr. 1.783/2021, Anexa 1 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Ce trebuie știut despre nomenclatorul și frecvența raportării:

- Fiecare mișcare de stoc — inclusiv o **ieșire prin vânzare** — se identifică printr-un cod de tip mișcare, dintr-un nomenclator oficial fix. Pentru vânzare, codul e **„30" — Vânzare**; alte coduri relevante pentru ieșiri sunt „70" (Consum), „160" (Bunuri degradate), „170" (Bunuri expirate) sau „180" (Alte tranzacții) — folosirea unui cod din afara acestei liste face fișierul respins la validare.
- Structura „Movement of Goods" (împreună cu nomenclatorul de tipuri de mișcări, „Movement Type Table") e **obligatorie doar în raportarea de stocuri**, care se cere separat de raportarea lunară/trimestrială standard a D406 — secțiunile respective se transmit **goale** în fișierele lunare obișnuite.
- Această distincție e importantă la planificare: o firmă poate depune D406 corect lunar, cu secțiunile de mișcări de stoc goale, fără să încalce legea — obligația de a popula efectiv „Movement of Goods" cu date reale apare doar când ANAF cere raportarea de stocuri (la un termen separat, conform anexelor ordinului).

## Ce se greșește în practică

- Se încearcă popularea secțiunii „Movement of Goods" cu date în fiecare fișier lunar, deși structura standard o cere goală, ceea ce poate produce erori de validare dacă formatul nu respectă exact schema pentru raportarea de stocuri.
- Se folosesc coduri de tip mișcare inventate sau apropiate ca sens (de exemplu „1" pentru vânzare) în loc de codul oficial din nomenclator („30") — orice cod în afara listei duce la respingerea fișierului.
- Se confundă obligația de raportare **lunară** a D406 (jurnal, facturi, plăți) cu obligația, separată, de **raportare a stocurilor**, presupunând că ambele sunt cerute cu aceeași frecvență.

## Ce face iConta.eu

La data acestui ghid, motorul de generare D406 din iConta.eu (`core/d406.py`) are nomenclatorul complet al tipurilor de mișcări de stoc verificat împotriva listei oficiale ANAF, dar secțiunea „Movement of Goods" nu este încă populată automat cu ieșirile efective de marfă în fișierele lunare — codul tratează în mod explicit acest lucru ca pe o limitare cunoscută, nu ascunsă, tocmai pentru că această secțiune e cerută separat, la raportarea de stocuri, nu în fiecare depunere lunară.

[iConta.eu](/)
