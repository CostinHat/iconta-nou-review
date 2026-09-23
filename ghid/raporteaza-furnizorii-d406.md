---
title: Cum se raportează furnizorii în D406?
description: Furnizorii se raportează în secțiunea Suppliers din MasterFiles, cu aceeași logică de identificare codificată pe tip de partener ca la clienți.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează furnizorii în D406?

Furnizorii firmei sunt raportați în MasterFiles, la subsecțiunea Suppliers — structural, simetrică cu subsecțiunea Customers pentru clienți.

## Temeiul legal

::: ghid-temei
„MasterFiles ... Conţine date preluate din Registrul-jurnal, furnizori, clienţi, produse, stocuri, active etc." — cu subsecțiuni detaliate: GeneralLedgerAccounts (conturi, tip, solduri), Customers, Suppliers, Tax Table, UOMTable, AnalysisType Table, MovementType Table, Products, PhysicalStock, Owners, Assets. — OPANAF nr. 1783/2021, Anexa 1, pct. 4-5.
:::

Ca și la clienți, identitatea fiecărui furnizor trebuie codificată conform nomenclatorului SAF-T, în funcție de tipul partenerului — persoană juridică sau persoană fizică — nu raportată printr-un identificator unic, generic.

## Ce se greșește în practică

Greșeala tipică este identică celei de la clienți: folosirea unui identificator brut de furnizor (de exemplu un ID intern din evidența contabilă), în loc de codificarea cerută de nomenclator, în special pentru furnizorii persoane fizice sau pentru cei fără cod fiscal standard.

## Ce face iConta.eu

Identitatea partenerului (furnizor) urmează aceeași regulă de nomenclator ca la clienți: cod „00" plus codul de identificare fiscală (CUI) pentru persoane juridice românești, cod „01" sau „02" plus codul, pentru operatori dintr-un alt stat UE, respectiv din afara UE, cod „03" plus CNP pentru persoane fizice, cod „04" plus numele, pentru cazurile fără identificator fiscal valid. Corecția care a înlocuit identificatorul brut folosit anterior cu această codificare conformă a fost aplicată în producție pe 11 august 2026 și este gardată împotriva regresiei.

[iConta.eu](/)
