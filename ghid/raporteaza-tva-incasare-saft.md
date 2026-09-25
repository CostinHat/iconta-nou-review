---
title: "Cum se raportează TVA la încasare în SAF-T?"
description: "Ce cere legal fișierul standard de control fiscal (SAF-T/D406) de la o firmă la TVA la încasare, și cum reflectă azi iConta.eu mecanismul de exigibilitate în acest raport."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se raportează TVA la încasare în SAF-T?

SAF-T (Declarația informativă D406) e un export structurat al întregii contabilități a firmei — jurnale, facturi, planul de conturi, parteneri — nu o declarație de TVA separată. Regimul de TVA la încasare nu are un capitol sau o secțiune proprie în structura SAF-T: informația despre exigibilitate rămâne cea reflectată deja în conturile 4427/4428 și, la nivel declarativ, în decontul de TVA (D300), pe care SAF-T îl oglindește la nivel de tranzacție.

## Temeiul legal

::: ghid-temei
„ART. 1 Natura informațiilor pe care contribuabilul/plătitorul trebuie să le declare prin fișierul standard de control fiscal (SAF-T) este prevăzută în anexa nr. 1. ART. 2 Fișierul standard de control fiscal (SAF-T) se transmite de către contribuabili/plătitori prin intermediul Declarației informative privind fișierul standard de control fiscal, denumită în continuare Declarația informativă D406 [...]."
— OPANAF nr. 1783/2021, art. 1-2 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

- SAF-T cere raportarea facturilor emise și primite ca parte din `SourceDocuments`, cu datele lor de bază (număr, dată, părți, linii, TVA pe fiecare linie) — structura nu prevede un câmp separat pentru "regim TVA la încasare" al emitentului sau al beneficiarului.
- Exigibilitatea taxei la TVA la încasare (art. 282 alin. 3-8 din Codul fiscal) rămâne guvernată de decontul de TVA (D300), nu de SAF-T — SAF-T raportează operațiunile așa cum au fost înregistrate contabil, nu recalculează exigibilitatea.
- Termenele de transmitere și categoriile de contribuabili obligate diferă pe cifra de afaceri/mărime a firmei (anexele 4 și 5 la OPANAF 1783/2021), independent de regimul de TVA aplicat.

## Ce se greșește în practică

- Se caută în structura XSD a SAF-T un câmp dedicat "TVA la încasare" care să reflecte regimul firmei — un asemenea câmp nu există; informația relevantă trebuie citită din conturile folosite (4427 vs. 4428) și din jurnalele de operațiuni.
- Se presupune că data raportată în SAF-T pentru o factură e automat data exigibilității TVA — câmpurile de dată din structura facturii (data facturii) și data la care taxa devine exigibilă (relevantă la TVA la încasare) sunt concepte diferite, care pot să nu coincidă.
- Se omite raportarea corectă a soldurilor conturilor 4427/4428 în planul de conturi (`GeneralLedgerEntries`) al SAF-T, ceea ce lasă divergențe între decont și fișierul standard la un control ulterior.
- Se consideră SAF-T o declarație "opțională" pentru firmele mici, ignorând calendarul de obligativitate stabilit pe categorii de contribuabili prin anexa 5 la OPANAF 1783/2021.

## Ce face iConta.eu

Generatorul SAF-T al iConta.eu (`core/d406.py`) e complex și verificat pe validatorul oficial ANAF (DUK) pentru toate secțiunile cerute — antet, plan de conturi, parteneri, jurnale, facturi. Facturile raportate în `SourceDocuments` includ, la nivel de linie, câmpul `TaxPointDate`.

Verificat direct în cod: acest câmp e completat cu **data facturii**, nu cu data încasării, și nu există în `d406.py` nicio ramură de cod condiționată de flagul `tva_la_incasare` al firmei — spre deosebire de `core/d300.py`, unde exigibilitatea pe încasări are un tratament explicit și dedicat (vezi ghidurile despre decontul de TVA la încasare). Cu alte cuvinte, mecanismul specific de TVA la încasare (4428→4427 pe măsura încasării) trăiește azi doar în decont (D300); SAF-T raportează facturile și rulajele contabile așa cum au fost înregistrate, fără o secțiune sau un semnal distinct pentru firmele la TVA la încasare. Nu am găsit în cercetarea de față o confirmare directă, la sursa oficială ANAF (documentația XSD/DUK), a ceea ce ar trebui de fapt să reprezinte `TaxPointDate` pentru o firmă la TVA la încasare — e un aspect care merită verificat punctual, separat, înainte de a-l considera tranșat.

[iConta.eu](/)
