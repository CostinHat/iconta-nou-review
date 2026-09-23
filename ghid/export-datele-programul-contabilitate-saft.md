---
title: "Cum export datele din programul de contabilitate în SAF-T"
description: Ce înseamnă, tehnic, generarea unui fișier SAF-T din datele deja existente în contabilitate, și care module depind de surse de date suplimentare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum export datele din programul de contabilitate în SAF-T

Un fișier SAF-T nu se completează manual — se generează din datele deja existente în evidența contabilă, exact așa cum sunt ele înregistrate.

## Temeiul legal

::: ghid-temei
„MasterFiles ... Conţine date preluate din Registrul-jurnal, furnizori, clienţi, produse, stocuri, active etc." — OPANAF nr. 1783/2021, Anexa 1, pct. 4-5.
:::

## Ce înseamnă, concret, „exportul" către SAF-T

„Exportul" către SAF-T înseamnă generarea automată a fișierului XML din datele deja existente — planul de conturi, jurnalul contabil, nomenclatoarele de parteneri și produse, facturile emise și primite — nu o introducere separată a acelorași informații într-un alt format. Procedura oficială (Anexa 3, pct. 1-9) urmează generarea XML cu validarea structurală, apoi generarea PDF-ului semnat electronic, apoi transmiterea prin SPV sau prin e-guvernare.ro.

Cât de complet e „exportul" depinde strict de ce generează efectiv motorul de raportare: Header, MasterFiles și GeneralLedgerEntries pot fi generate integral din structura contabilă standard, dar unele secțiuni din SourceDocuments (de exemplu Payments) depind de existența unei surse de date dedicate — dacă acea sursă nu e conectată la evidența financiară (de exemplu o mapare a trezoreriei), secțiunea rămâne goală chiar dacă restul fișierului e complet.

## Ce se greșește în practică

- Se presupune că „exportul SAF-T" e un simplu export de tip CSV sau Excel, reformatat — e, de fapt, generarea unui XML structurat, validat pe o schemă oficială, cu reguli stricte de reconciliere internă.
- Se ignoră faptul că unele module (Payments, Movement of Goods, Asset Transactions) depind de surse de date suplimentare, nu doar de contabilitatea curentă — un fișier „complet" tehnic poate fi totuși incomplet pe aceste secțiuni.
- Se validează doar vizual fișierul generat, fără trecerea lui prin validatorul oficial.

## Ce face iConta.eu

iConta.eu generează fișierul D406 direct din evidența contabilă a firmei, fără un pas manual de „export" separat — Header, MasterFiles și GeneralLedgerEntries complet din structura XSD, iar SourceDocuments cu facturile de vânzare și achiziție linie cu linie. Fișierul rezultat e validat cu DUKIntegrator înainte de a fi pus la dispoziție. Secțiunea Payments rămâne neemisă la stadiul curent — codul de emitere e scris, dar lipsește sursa de mapare a plăților din trezorerie; Movement of Goods și Asset Transactions rămân, de asemenea, neacoperite.

[iConta.eu](/)
