---
title: Cum se raportează cotele de TVA în D406?
description: Cotele de TVA se raportează prin secțiunea Tax Table din MasterFiles, cu coduri de TVA sensibile la data facturii — mai ales în jurul schimbării de la 1 august 2025.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează cotele de TVA în D406?

Cotele de TVA nu sunt un câmp izolat în D406 — sunt raportate printr-un nomenclator dedicat (Tax Table), la care se leagă fiecare linie de document care conține TVA.

## Temeiul legal

::: ghid-temei
„MasterFiles ... Conţine date preluate din Registrul-jurnal, furnizori, clienţi, produse, stocuri, active etc." — cu subsecțiuni detaliate: GeneralLedgerAccounts (conturi, tip, solduri), Customers, Suppliers, Tax Table, UOMTable, AnalysisType Table, MovementType Table, Products, PhysicalStock, Owners, Assets. — OPANAF nr. 1783/2021, Anexa 1, pct. 4-5.
:::

**Tax Table** este subsecțiunea din MasterFiles care conține nomenclatorul cotelor și codurilor de TVA folosite de firmă. La nivelul documentelor (facturi emise/primite), fiecare linie poartă un cod de TVA (TaxCode) care trebuie să corespundă unei intrări din acest nomenclator — cota aplicată nu se scrie "liber" pe fiecare linie, ci prin referință la un cod standardizat.

Un element tehnic important: codurile de TVA pentru livrări s-au schimbat începând cu 1 august 2025, prin Legea nr. 141/2025. Orice sistem care generează D406 trebuie să aplice codul corect în funcție de data facturii, nu de data generării declarației — o factură din iulie 2025 și una din septembrie 2025 pot avea coduri TaxCode diferite pentru aceeași operațiune, dacă legea a schimbat regimul între cele două date.

## Ce se greșește în practică

Greșeala principală este aplicarea unui singur cod de TVA "curent" tuturor facturilor dintr-o perioadă de raportare, indiferent de data reală a fiecărei facturi — ceea ce poate genera coduri greșite pentru facturile emise chiar înainte de o schimbare legislativă de cotă/cod, dar incluse în aceeași declarație D406.

## Ce face iConta.eu

Conform docstring-ului generatorului (`core/d406.py`, actualizat 03.08.2026): „TaxCode livrari PERIOD-AWARE pe data facturii (03.08: coduri pre/post 01.08.2025, Legea 141/2025)" — adică iConta.eu aplică automat codul de TVA corect în funcție de data facturii, nu de data la care se generează declarația, ținând cont explicit de schimbarea din Legea 141/2025.

Nomenclatorul de coduri (TaxCode) folosit la generare provine din nomenclatoarele tehnice ale aplicației (`d406_nomenclatoare_anaf.properties`, `d406_schema_anaf.xlsx`), care descriu structura acceptată de ANAF pentru acest câmp.

[iConta.eu](/)
