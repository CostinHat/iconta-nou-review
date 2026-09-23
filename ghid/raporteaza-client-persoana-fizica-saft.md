---
title: Cum se raportează un client persoană fizică în SAF-T?
description: Un client persoană fizică se identifică în D406 prin CNP, cu cod de tip „03" în nomenclator — nu prin codul folosit pentru firme.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează un client persoană fizică în SAF-T?

Nu toți clienții unei firme sunt persoane juridice — iar D406 cere ca identitatea partenerului să reflecte corect acest lucru, printr-un cod de tip specific în nomenclator.

## Temeiul legal

::: ghid-temei
„MasterFiles ... Conţine date preluate din Registrul-jurnal, furnizori, clienţi, produse, stocuri, active etc." — cu subsecțiuni detaliate: GeneralLedgerAccounts (conturi, tip, solduri), Customers, Suppliers, Tax Table, UOMTable, AnalysisType Table, MovementType Table, Products, PhysicalStock, Owners, Assets. — OPANAF nr. 1783/2021, Anexa 1, pct. 4-5.
:::

Nomenclatorul SAF-T de identificare a partenerilor (clienți/furnizori) diferențiază explicit pe tip: cod „00" plus codul de identificare fiscală (CUI) pentru persoane juridice românești (cod „01" sau „02" pentru operatori din UE, respectiv din afara UE), cod „03" plus CNP pentru persoane fizice, respectiv cod „04" plus numele, pentru situațiile fără identificator fiscal valid. Pentru un client persoană fizică, identificatorul corect este deci CNP-ul, sub codul de tip „03" — nu un cod fiscal de firmă, care oricum nu există pentru o persoană fizică fără activitate independentă.

## Ce se greșește în practică

Greșeala cea mai relevantă aici este raportarea unui client persoană fizică folosind un identificator intern generic (de exemplu un ID din sistemul de facturare) în locul CNP-ului codificat corect — situație care, tehnic, duce la o identitate de partener neconformă cu nomenclatorul SAF-T.

## Ce face iConta.eu

iConta.eu a avut, până pe 11 august 2026, exact această problemă: identitatea partenerului era generată cu un identificator brut, indiferent de tipul clientului. Corecția aplicată în producție pe 11 august 2026 a introdus maparea conformă nomenclatorului — pentru un client persoană fizică, sistemul raportează acum CNP-ul sub codul de tip „03", nu identificatorul intern folosit anterior. Corecția este gardată împotriva regresiei.

Dacă ați generat declarații D406 înainte de această dată și aveți clienți persoane fizice în structura de parteneri, este utilă o verificare punctuală a identității raportate pentru acele perioade.

[iConta.eu](/)
