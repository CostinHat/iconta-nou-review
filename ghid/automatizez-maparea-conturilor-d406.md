---
title: "Cum automatizez maparea conturilor pentru D406?"
description: Ce înseamnă corespondența dintre planul de conturi al firmei și nomenclatorul GeneralLedgerAccounts din SAF-T, și ce parte din acest proces poate fi automatizată.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum automatizez maparea conturilor pentru D406?

Secțiunea GeneralLedgerAccounts din SAF-T reia, pentru fiecare cont contabil folosit de firmă, tipul lui și soldul — practic o oglindă a planului de conturi, adusă la structura cerută de ANAF. „Maparea" nu e o traducere liberă, ci o corespondență cu nomenclatorul oficial al conturilor acceptate.

## Temeiul legal

::: ghid-temei
„MasterFiles ... Conţine date preluate din Registrul-jurnal, furnizori, clienţi, produse, stocuri, active etc." — OPANAF nr. 1783/2021, Anexa 1, pct. 4-5.

Printre subsecțiunile MasterFiles se numără explicit GeneralLedgerAccounts (conturi, tip, solduri), alături de GeneralLedgerEntries, care reiau mișcările din Registrul-jurnal.
:::

## Ce înseamnă, tehnic, „maparea"

Structura SAF-T vine cu propriile nomenclatoare — planul de conturi acceptat pe fiecare normă contabilă și tipurile de cont recunoscute de schema XML. Acestea sunt referințe de structură, publicate de ANAF alături de schema XSD, nu texte de lege — dar respectarea lor e obligatorie pentru ca fișierul să treacă validarea.

„Automatizarea" mapării conturilor înseamnă, în esență, două lucruri separate:

1. **Generarea automată** a secțiunii GeneralLedgerAccounts direct din planul de conturi folosit deja în contabilitate, fără reintroducerea manuală a fiecărui cont într-un formular separat pentru SAF-T.
2. **Reconcilierea** — o verificare independentă a corespondenței dintre conturile folosite în GeneralLedgerEntries (jurnal) și cele raportate în GeneralLedgerAccounts (nomenclator), ca să nu apară un cont folosit în jurnal dar absent din MasterFiles, sau invers.

## Ce se greșește în practică

- Se întreține manual, la fiecare generare de SAF-T, o listă de conturi separată de planul de conturi curent al firmei — risc mare de desincronizare.
- Se ignoră reconcilierea dintre GeneralLedgerEntries și GeneralLedgerAccounts, iar fișierul poate trece validarea structurală, dar rămâne inconsistent intern.
- Se presupune că un cont analitic nou, adăugat direct în contabilitate, apare automat corect în SAF-T fără nicio verificare — depinde strict de cum e generată secțiunea MasterFiles din sursă.

## Ce face iConta.eu

iConta.eu generează secțiunea GeneralLedgerAccounts automat din planul de conturi al firmei — nu există o listă separată de întreținut manual pentru SAF-T. Pe lângă generator, aplicația are un modul distinct de reconciliere, care verifică independent secțiunea GeneralLedgerEntries față de restul datelor, tocmai pentru a prinde eventuale conturi nemapate corect înainte de depunere.

[iConta.eu](/)
