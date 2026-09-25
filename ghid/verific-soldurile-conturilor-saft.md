---
title: "Cum verific soldurile conturilor din SAF-T?"
description: "Ce reprezintă secțiunea de înregistrări contabile din fișierul SAF-T (D406) și de ce soldurile ei trebuie să corespundă cu balanța de verificare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific soldurile conturilor din SAF-T?

Fișierul SAF-T (declarația D406) nu e doar o listă de tranzacții — el conține și soldurile de deschidere și de închidere ale conturilor, în secțiunea de înregistrări contabile (GeneralLedgerEntries). Dacă aceste solduri nu corespund cu balanța de verificare a firmei, declarația poate fi respinsă la validare sau poate genera neconcordanțe la un eventual control.

## Temeiul legal

::: ghid-temei
„GeneralLedgerEntries → Înregistrări Contabile"
— OPANAF 1783/2021 pentru aprobarea specificațiilor tehnice de completare a fișierului standard de control fiscal (SAF-T), documentația structurii D406 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Ce trebuie verificat, pe baza structurii oficiale a fișierului:

- Secțiunea GeneralLedgerEntries a fișierului SAF-T conține, pentru fiecare cont din planul de conturi, soldul de deschidere și soldul de închidere ale perioadei raportate, alături de rulajele debitoare și creditoare.
- Aceste valori trebuie să corespundă exact cu balanța de verificare contabilă a firmei pentru luna raportată — orice diferență semnalează fie o eroare de mapare a datelor din contabilitate în fișier, fie o eroare reală în balanță.
- Structura oficială a D406 (nomenclatorul de conturi, obligativitatea partenerului pe fiecare linie de tranzacție) e definită prin specificațiile tehnice ANAF, nu prin ghidul informal de completare — orice modificare de nomenclator sau versiune trebuie verificată direct pe documentația tehnică în vigoare.

## Ce se greșește în practică

- Se generează fișierul SAF-T fără o reconciliere prealabilă cu balanța de verificare a lunii respective.
- Se ignoră faptul că o lună fără mișcări contabile tot trebuie raportată (fișier „pe zero", cu secțiunea de înregistrări contabile goală, nu omisă).
- Se presupune că soldurile SAF-T sunt generate independent de contabilitatea curentă, când de fapt trebuie să reflecte exact aceleași conturi și sume din balanța oficială a firmei.

## Ce face iConta.eu

Modulul SAF-T din iConta.eu (`core/d406.py`) generează fișierul D406 direct din datele contabile ale firmei, inclusiv secțiunea de înregistrări contabile cu soldurile conturilor — astfel încât soldurile din SAF-T provin din aceeași sursă ca balanța de verificare afișată în aplicație, fără o etapă de transcriere manuală separată care ar putea introduce diferențe.

[iConta.eu](/)
