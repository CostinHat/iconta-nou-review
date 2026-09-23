---
title: "Conversia datelor din balanță în SAF-T"
description: De ce balanța de verificare acoperă doar o parte din datele cerute de SAF-T — corespondența dintre GeneralLedgerAccounts (solduri) și GeneralLedgerEntries (mișcările din jurnal).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Conversia datelor din balanță în SAF-T

Balanța de verificare și secțiunea MasterFiles/GeneralLedgerAccounts din SAF-T conțin, în esență, aceleași informații — conturile folosite și soldurile lor — dar structurate diferit, iar balanța, singură, nu acoperă tot ce cere fișierul.

## Temeiul legal

::: ghid-temei
„MasterFiles ... Conţine date preluate din Registrul-jurnal, furnizori, clienţi, produse, stocuri, active etc." — OPANAF nr. 1783/2021, Anexa 1, pct. 4-5.

Subsecțiunea GeneralLedgerAccounts reia, pentru fiecare cont, tipul și soldurile lui, iar GeneralLedgerEntries reia mișcările din Registrul-jurnal.
:::

## Ce se suprapune și ce nu, între balanță și SAF-T

Structural, SAF-T separă cele două tipuri de informații pe care le găsești, de obicei, împreună într-o balanță de verificare:

- **GeneralLedgerAccounts** (parte din MasterFiles) — planul de conturi folosit, cu tipul fiecărui cont și soldurile aferente. E, practic, partea „statică" a balanței, adusă la formatul cerut de ANAF.
- **GeneralLedgerEntries** — mișcările efective din Registrul-jurnal, adică rândurile individuale de înregistrare contabilă din spatele soldurilor.

O balanță de verificare clasică arată doar rezultatul (soldurile), fără mișcările detaliate. SAF-T cere ambele: nomenclatorul de conturi cu solduri (GeneralLedgerAccounts) și jurnalul care a produs acele solduri (GeneralLedgerEntries) — nu se poate raporta corect doar soldul final, fără istoricul mișcărilor din perioadă.

## Ce se greșește în practică

- Se presupune că „exportul balanței" e suficient pentru SAF-T — balanța acoperă doar GeneralLedgerAccounts (solduri), nu și GeneralLedgerEntries (mișcările din jurnal), care sunt obligatorii separat.
- Se raportează conturi din balanță fără corespondența lor cu nomenclatorul tehnic de conturi acceptat de schema SAF-T, ceea ce duce la erori de validare structurală.
- Se ignoră reconcilierea între soldurile din GeneralLedgerAccounts și mișcările din GeneralLedgerEntries — cele două secțiuni trebuie să fie consistente între ele, nu doar corecte individual.

## Ce face iConta.eu

iConta.eu generează secțiunea GeneralLedgerAccounts (conturi, tip, solduri) direct din planul de conturi al firmei, alături de GeneralLedgerEntries, complet, din structura XSD — ambele module fiind produse din aceeași evidență, nu din exporturi separate. Aplicația are și un modul dedicat de reconciliere, care verifică independent GeneralLedgerEntries față de restul datelor, ca oglindă de control înainte de validare.

[iConta.eu](/)
