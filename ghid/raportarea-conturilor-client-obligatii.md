---
title: "Raportarea conturilor de client: obligații"
description: "Ce trebuie să conțină raportarea conturilor analitice de client în fișierul standard de control fiscal (SAF-T/D406) și cine e obligat la ea."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Raportarea conturilor de client: obligații

Dincolo de evidența analitică internă (fișa fiecărui client, cont 411), firmele obligate la depunerea SAF-T trebuie să raporteze periodic către ANAF, pentru fiecare client, contul analitic în care e înregistrat, identificarea lui fiscală și soldurile — o secțiune distinctă a fișierului standard de control fiscal.

## Temeiul legal

::: ghid-temei
„Customers (Clienți) — Conţine informaţii despre clienţi, precum detaliile de identificare (denumire, adresa, cod de înregistrare fiscală), contul analitic în care este înregistrat soldul clientului respectiv, soldul iniţial debitor/creditor, sold final debitor/creditor etc."
— OPANAF 1783/2021 (Ghidul contribuabilului pentru D406 — SAF-T), secțiunea MasterFiles > Customers (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Ce presupune, concret, această obligație:

- Secțiunea **Customers** din MasterFiles-ul SAF-T nu e opțională pentru firmele care au obligația de depunere a D406 — trebuie să conțină, pentru fiecare client cu care s-a operat în perioada raportată, identificarea completă (denumire, adresă, cod fiscal), contul analitic (de regulă 411 și subanaliticele lui) și soldurile de deschidere/închidere.
- Obligația de depunere a D406 se extinde progresiv pe categorii de contribuabili (mari, mijlocii, mici), pe date de referință publicate de ANAF prin „Ghidul contribuabilului" menționat în anexa actului normativ.
- Fiecare client raportat în Customers trebuie identificat consecvent și în secțiunea tranzacțiilor (GeneralLedgerEntries), prin `CustomerID` — o neconcordanță între cele două secțiuni e una dintre cauzele frecvente de respingere a fișierului la validare.

## Ce se greșește în practică

- Se raportează clienții doar cu denumirea și codul fiscal, fără contul analitic corect asociat — validatorul oficial respinge fișierul dacă `CustomerID`-urile nu sunt identice între secțiunea Customers și liniile de tranzacție.
- Se omit clienții cu sold zero la închiderea perioadei, presupunând că „nu mai au ce raporta" — dacă au avut mișcări în perioadă, rămân obligatorii în Customers.
- Se confundă raportarea SAF-T (obligație periodică, către ANAF) cu simpla ținere a fișei de cont a clientului în contabilitatea internă — a doua e permanentă și nu înlocuiește prima.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **generează secțiunea Customers** a declarației D406/SAF-T: modulul `core/d406.py` construiește, pentru fiecare client, elementul `<Customer>` cu `CustomerID`, `AccountID` (contul 4111) și identificarea fiscală, iar `core/repo_d406.py` extrage lista clienților din baza de date (`select_clienti`). Aplicația asigură și consecvența `CustomerID` între secțiunea Customers și liniile de tranzacție din registrul general, cerută de validatorul oficial ANAF (DUK). Judecata asupra completitudinii datelor de identificare introduse pentru fiecare client rămâne responsabilitatea contabilului.

[iConta.eu](/)
