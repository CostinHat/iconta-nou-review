---
title: "Ce fac dacă ANAF a înregistrat greșit obligațiile din D212?"
description: "O eroare de redactare, omisiune sau mențiune greșită dintr-un act al organului fiscal se corectează prin cerere de îndreptare a erorii materiale, nu prin contestație pe fond."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă ANAF a înregistrat greșit obligațiile din D212?

Când discrepanța nu vine din declarația ta, ci din felul în care ANAF a înregistrat sau procesat-o, remediul legal e diferit de o rectificativă — e o cerere de îndreptare a erorii materiale, adresată direct organului fiscal.

## Temeiul legal

::: ghid-temei
„Organul fiscal poate îndrepta oricând erorile materiale din cuprinsul actului administrativ fiscal, din oficiu sau la cererea contribuabilului/plătitorului. [...] Prin erori materiale, în sensul prezentului articol, se înțelege orice greșeli de redactare, omisiuni sau mențiuni greșite din actele administrative fiscale, cu excepția acelora care atrag nulitatea actului administrativ fiscal, potrivit legii, sau care privesc fondul actului administrativ fiscal."
— Legea 207/2015 (Codul de procedură fiscală), art. 53 alin. (1)-(2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce distincție contează aici:

- Îndreptarea erorii materiale (art. 53) se aplică greșelilor de redactare, omisiunilor sau mențiunilor greșite — de exemplu, o sumă transcrisă greșit de sistemul ANAF față de ce ai declarat tu în D212.
- Nu se aplică situațiilor care „privesc fondul actului administrativ fiscal" — dacă discrepanța vine dintr-o interpretare fiscală diferită (nu o eroare de transcriere), calea corectă e contestația, nu cererea de îndreptare.
- Cererea de îndreptare se depune la organul fiscal care a emis actul, iar acesta poate corecta oricând, chiar și din oficiu, dacă descoperă singur eroarea (art. 53 alin. (1) și (3)).
- Dacă discrepanța provine din propria declarație (o valoare pe care ai declarat-o greșit tu, nu ANAF), remediul e altul — declarația rectificativă (art. 105 din aceeași lege), nu cererea de îndreptare a erorii materiale.

## Ce se greșește în practică

- Se depune o declarație rectificativă când, de fapt, eroarea aparține sistemului ANAF, nu declarantului — rectificativa înlocuiește propria declarație, nu corectează o eroare de procesare a organului fiscal.
- Se contestă pe fond o simplă eroare de transcriere, printr-un mecanism mai greoi decât cererea de îndreptare — dacă discrepanța e o greșeală materială evidentă, art. 53 e calea directă și mai rapidă.
- Se lasă discrepanța necorectată, presupunând că „se va regla de la sine" — erorile materiale nu se corectează automat decât dacă organul fiscal le descoperă singur; cererea contribuabilului grăbește procesul.

## Ce face iConta.eu

D212 e o declarație manuală în iConta.eu (`core/d212.py`), care generează declarația conform structurii validate de ANAF, dar aplicația nu are vizibilitate asupra modului în care ANAF procesează sau înregistrează ulterior datele în sistemele proprii. Aplicația nu ține evidența discrepanțelor dintre declarația transmisă și obligațiile efectiv înregistrate de ANAF — compararea celor două rămâne o verificare manuală, iar formularea cererii de îndreptare a erorii materiale se face direct către organul fiscal, în afara aplicației.

[iConta.eu](/)
