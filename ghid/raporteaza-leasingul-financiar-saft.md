---
title: "Cum se raportează leasingul financiar în SAF-T?"
description: "SAF-T/D406 nu are o secțiune dedicată leasingului — notele contabile intră generic în registrul de jurnal, iar bunul apare la Active doar dacă e introdus separat ca mijloc fix."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se raportează leasingul financiar în SAF-T?

Leasingul financiar nu are un tratament special în structura SAF-T (Declarația informativă D406). Notele contabile generate de un contract de leasing intră în raportare la fel ca orice altă notă — nu există un câmp, o secțiune sau o regulă dedicată acestui tip de operațiune.

## Temeiul legal

::: ghid-temei
„ART. 1. Natura informațiilor pe care contribuabilul/plătitorul trebuie să le declare prin fișierul standard de control fiscal (SAF-T) este prevăzută în anexa nr. 1. ART. 2. Fișierul standard de control fiscal (SAF-T) se transmite de către contribuabili/plătitori prin intermediul Declarației informative privind fișierul standard de control fiscal, denumită în continuare Declarația informativă D406 [...]."
— OPANAF 1783/2021, art. 1-2 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

- SAF-T/D406 e o raportare **generică** a tuturor înregistrărilor contabile și a activelor firmei — structura ei nu prevede o secțiune specifică pentru leasing.
- Notele contabile ale unui contract de leasing (primire, rate, valoare reziduală, chirie) intră în secțiunea generală de jurnal contabil (`GeneralLedgerEntries`), exact ca orice altă notă contabilă.
- Bunul recunoscut prin leasing financiar (contul 2133) ajunge în secțiunea de Active a SAF-T doar dacă a fost introdus **separat**, ca mijloc fix, în registrul dedicat — nu există o legătură automată între nota de leasing și acea secțiune.

## Ce se greșește în practică

- Se caută un câmp sau o secțiune dedicată „leasing" în structura SAF-T — nu există, nici în anexele oficiale (OPANAF 1783/2021, respectiv actualizarea OPANAF 407/2025), nici ca practică generalizată de raportare.
- Se presupune că bunul din leasing apare automat în secțiunea de Active a SAF-T doar pentru că a fost înregistrat printr-o notă de leasing — de fapt trebuie introdus separat, ca mijloc fix.

## Ce face iConta.eu

Notele generate de F056 (Leasing financiar și operațional) intră în exportul SAF-T generic, ca orice altă înregistrare contabilă — iConta.eu **nu are cod dedicat** de raportare a leasingului în D406 (nicio mențiune „leasing" în motorul de generare a SAF-T al aplicației). Pentru ca bunul din leasing să apară și în secțiunea de Active a raportării, el trebuie introdus separat, în registrul de Mijloace fixe.

[iConta.eu](/)
