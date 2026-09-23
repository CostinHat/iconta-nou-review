---
title: "Salariul minim în construcții 2026: prag special"
description: Registrul de cote verificat pentru 2026 conține un singur salariu minim la nivel național (pe cele două ferestre ale anului), fără un prag special pentru construcții. Nu presupunem că pragul sectorial a rămas neschimbat — raportăm exact ce arată dosarul.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Salariul minim în construcții 2026: prag special

Construcțiile au avut, în anii anteriori, un salariu minim brut distinct, mai mare decât cel general pe economie. Verificând registrul folosit efectiv de motorul de calcul salarial pentru 2026, acest ghid raportează onest: **nu există, în acest registru, un salariu minim separat pentru sectorul construcțiilor** — există un singur salariu minim la nivel național, cu două valori pe cele două ferestre ale anului.

## Temeiul legal

::: ghid-temei
„Începând cu data de 1 iulie 2026, salariul de bază minim brut pe țară garantat în plată ... se stabilește ... la suma de 4.325 lei lunar, pentru un program normal de lucru în medie de 166,667 ore pe lună, reprezentând 25,949 lei/oră." — HG 146/2026, art.1
:::

## Ce confirmă registrul verificat

| Salariu minim | Valabil | Temei |
|---|---|---|
| 4.050 lei | 1 ianuarie – 30 iunie 2026 | HG 1506/2024, art.1 |
| 4.325 lei | 1 iulie – 31 decembrie 2026 | HG 146/2026, art.1 |

Ambele valori sunt generale, pe economie — niciuna nu e marcată, în registrul verificat, ca aplicabilă specific sau diferit sectorului construcțiilor.

**De semnalat onest**: registrul de cote (`core/common.py`, dict `COTE`, „period-aware") conține o singură cheie `salariu_minim`, cu cele două valori de mai sus, fără o a treia intrare pentru un prag sectorial distinct (construcții). Funcționalitatea F080 declară, printre temeiurile ei generale, și OUG 34/2024 (actul care a reformat facilitățile fiscale sectoriale), dar dosarul de cercetare nu reproduce textul acelui act și nu confirmă dacă un eventual prag special pentru construcții a fost eliminat sau modificat. Nu presupunem că pragul sectorial a rămas neschimbat din ani anteriori — verificați direct stadiul actual al reglementării dacă aveți nevoie de certitudine.

## Ce se greșește în practică

- Se aplică un salariu minim mai mare, specific construcțiilor, bazat pe o regulă valabilă în anii anteriori, fără verificarea stadiului actual al reglementării pentru 2026.
- Se confundă cele două ferestre ale salariului minim general (4.050 lei, respectiv 4.325 lei) cu un eventual prag sectorial.

## Ce face iConta.eu

`salariu_minim_luna(la_data)` (`core/common.py`) returnează salariul minim general aplicabil lunii calculate — 4.050 sau 4.325 lei, după fereastră — fără un tratament diferit pentru angajatorii din construcții. Dacă aveți nevoie de un prag sectorial specific, verificați direct stadiul actual al reglementării — acest dosar nu-l confirmă.

[iConta.eu](/)
