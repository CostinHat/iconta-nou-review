---
title: "Ghid practic pentru noii contabili D205"
description: "Ce este D205, cine o depune, până când și cum se corectează — un ghid de bază pentru un contabil care completează prima dată această declarație."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ghid practic pentru noii contabili D205

D205 este declarația informativă privind impozitul reținut la sursă și câștigurile/pierderile din investiții, pe beneficiari de venit. O depune orice plătitor de venit care a reținut la sursă impozit pe dividende, dobânzi, premii, pensii sau alte venituri similare plătite unor persoane fizice.

## Temeiul legal

::: ghid-temei
„6. Termenul de depunere a declarației 6.1. Declarația se completează și se depune anual: a) până în ultima zi a lunii februarie inclusiv a anului curent pentru anul expirat; b) ori de câte ori plătitorul de venit constată erori în declarația depusă anterior, acesta completează și depune o declarație rectificativă, în condițiile art. 105 și 170 din Legea nr. 207/2015 privind Codul de procedură fiscală [...]"
— OPANAF 102/2025 (care a înlocuit integral anexa nr. 1/instrucțiunile de completare D205 aprobate prin OPANAF 179/2022), capitolul I pct. 6.1 (sursă: anaf_surse/opanaf_102_2025_modificarea_ordinului_presedintelui_agentiei_nationale.txt)
:::

Ce trebuie să știe un contabil aflat la prima completare:

- Termenul standard e **ultima zi a lunii februarie** a anului curent, pentru veniturile plătite în anul precedent.
- Dacă în cursul anului au fost plătite mai multe tipuri de venituri către beneficiari diferiți (dividende, dobânzi, premii etc.), se completează **un singur formular**, cu câte un tabel separat pentru fiecare tip de venit.
- O eroare descoperită ulterior se corectează prin declarație rectificativă, cu bifa aferentă, potrivit art. 105 și 170 din Codul de procedură fiscală — aceleași reguli generale ca la orice altă declarație rectificativă.

## Ce se greșește în practică

- Se depune câte un formular D205 separat pentru fiecare tip de venit plătit către beneficiari — corect e un singur formular pe an, cu tabele multiple în interior.
- Se omite declararea impozitului pe dividende distribuite, dar neplătite până la finalul anului — termenul de declarare/plată pentru aceste sume e distinct (25 ianuarie anul următor), și trebuie inclus corect în D205.
- Se corectează manual, în evidența internă, o eroare de sumă fără să se mai depună declarația rectificativă la ANAF — pentru fisc, D205 inițială rămâne valabilă până e înlocuită oficial.

## Ce face iConta.eu

iConta.eu are un generator D205 funcțional (`core/d205.py`), care calculează impozitul pe dividende pe baza mișcărilor din contul 457 (distribuiri și plăți), aplicând cota corectă în funcție de data distribuirii — inclusiv tranziția de cotă de la 10% la 16%, aplicată prin metodă FIFO pe tranșe distribuite/plătite (`core/dividende_curs.py`). Aplicația construiește XML-ul declarației și verifică erorile de completare înainte de generare. La acest moment, D205 din iConta.eu acoperă în principal fluxul de dividende; alte categorii de venituri reținute la sursă (dobânzi, premii, pensii) pot necesita completare manuală suplimentară, în funcție de datele disponibile în aplicație.

[iConta.eu](/)
