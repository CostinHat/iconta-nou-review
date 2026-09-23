---
title: Cum se raportează clienții în SAF-T?
description: Clienții se raportează în secțiunea Customers din MasterFiles, cu identitatea partenerului codificată conform nomenclatorului ANAF, nu cu un identificator brut.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează clienții în SAF-T?

Clienții firmei fac parte din MasterFiles, ca subsecțiune distinctă (Customers), alături de furnizori, produse, stocuri și active.

## Temeiul legal

::: ghid-temei
„MasterFiles ... Conţine date preluate din Registrul-jurnal, furnizori, clienţi, produse, stocuri, active etc." — cu subsecțiuni detaliate: GeneralLedgerAccounts (conturi, tip, solduri), Customers, Suppliers, Tax Table, UOMTable, AnalysisType Table, MovementType Table, Products, PhysicalStock, Owners, Assets. — OPANAF nr. 1783/2021, Anexa 1, pct. 4-5.
:::

Un detaliu tehnic important, cu efect direct asupra corectitudinii raportării clienților, ține de modul în care se identifică fiecare client în fișier. Nomenclatorul SAF-T cere ca identitatea partenerului să fie codificată după tipul lui — nu un identificator brut, aceeași informație indiferent de tip.

## Ce se greșește în practică

Cea mai frecventă greșeală, la nivel de concept, este tratarea câmpului de identificare a clientului ca pe un singur text liber (de exemplu, doar codul fiscal sau doar numele), fără să se respecte codificarea pe tipuri cerută de nomenclator — mai ales pentru clienți persoane fizice, unde identificatorul corect nu este codul de înregistrare fiscală folosit pentru firme.

## Ce face iConta.eu

Identitatea partenerului (client) este generată conform nomenclatorului SAF-T: cod „00" plus codul de identificare fiscală (CUI) pentru persoane juridice românești, cod „01" sau „02" plus codul, pentru operatori înregistrați într-un alt stat UE, respectiv din afara UE, cod „03" plus CNP pentru persoane fizice, respectiv cod „04" plus numele, pentru situațiile în care nu există un identificator fiscal valid. Această mapare a fost corectată direct în producție pe 11 august 2026 — anterior, sistemul folosea un identificator brut al clientului, indiferent de tip, ceea ce nu respecta nomenclatorul; corecția este acum gardată (protejată împotriva regresiei).

Pentru raportarea specifică a unui client persoană fizică, vedeți ghidul dedicat acestei situații.

[iConta.eu](/)
