---
title: Cum completez D205 pentru beneficiari din afara UE?
description: D205 nu admite deloc beneficiari nerezidenți la venituri din dividende, indiferent dacă sunt din UE sau din afara UE — orice dividend plătit unui nerezident se declară pe D207, nu pe D205.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum completez D205 pentru beneficiari din afara UE?

Întrebarea „cum trec un beneficiar din afara UE în D205" pornește de la o presupunere greșită: D205 nu tratează diferit beneficiarii din UE față de cei din afara UE, pentru că, la venituri din dividende, D205 nu admite deloc beneficiari nerezidenți — indiferent de țara lor de rezidență. Explicăm mai jos regula exactă și unde se declară corect aceste dividende.

## Temeiul legal

::: ghid-temei
„Rezid =(1,2) 1- Rezident 2- Nerezident. Rezid=(1) pt. tip_venit1=(08,09,11,12). Rezid=(1,2) pt. tip_venit1=(04,16,18, 25, 26, 27,28,29, 30)" (structura D205, OPANAF 102/2025, rd.32-33)

„Stat_R... daca Rezid=2 atunci Stat_R in nomenclator state de rezidenta altfel Stat_R=null" (structura D205, OPANAF 102/2025, rd.32-33)

„01 a. Venituri din dividende (art.223 alin.(1) lit.a))"; „22 a. Venituri din dividende (cf. convențiilor de evitare a dublei impuneri)" (nomenclatorul de tip_venit al declarației D207, `structura_D207_2025.txt`)
:::

## Regula: nerezident ⇒ D207, niciodată D205

Nomenclatorul D205 permite `Rezid=2` (nerezident) doar pentru anumite tipuri de venit — 04, 16, 18, 25-30. Pentru tipul de venit „08 - dividende" este admis exclusiv `Rezid=1` (rezident). Nu există nicio excepție pentru beneficiari din UE: distincția relevantă în D205 nu este UE/non-UE, ci strict rezident/nerezident, iar pentru dividende doar rezidenții sunt admiși pe această declarație.

Dividendele plătite unor beneficiari nerezidenți — indiferent dacă provin din UE sau din afara UE — se declară pe **D207**, care are propriile categorii de venit dedicate exact acestei situații: dividende conform Codului fiscal (tip_venit 01) sau dividende conform convenției de evitare a dublei impuneri aplicabile (tip_venit 22).

## Ce se greșește în practică

- Se încearcă introducerea unui beneficiar nerezident direct în lista de asociați pentru generarea automată a D205, presupunând că aplicația va trata diferit un CNP/CIF din UE.
- Se caută un câmp „Stat_R" (statul de rezidență) în D205 pentru dividende — acest câmp nu se aplică deloc la tip_venit 08.
- Se declară eronat un beneficiar nerezident pe D205 cu `Rezid=1`, doar ca declarația să treacă validarea, ceea ce e incorect și expune firma la respingere/corectare ulterioară.
- Se presupune că D207 se completează automat din aceleași date ca D205 — D207 necesită introducere separată, cu actul normativ aplicabil (Cod fiscal sau convenție) pentru fiecare beneficiar.

## Ce face iConta.eu

Rezidența unui beneficiar este derivată automat din forma CNP-ului: un CNP românesc valid (13 cifre, prima cifră 1-8) e considerat rezident; orice altă formă — CNP cu prima cifră 9, NIF străin, pașaport, lungime greșită — e considerată nerezidentă. Când un beneficiar de dividende este identificat ca nerezident, generarea D205 este refuzată explicit pentru acel beneficiar, cu un mesaj care direcționează spre D207. În acest moment, D207 este o declarație completată manual în aplicație — nu există încă un registru automat de plăți către beneficiari nerezidenți, deci beneficiarii, sumele și actul normativ aplicabil (Cod fiscal sau convenție) trebuie introduse direct de contabil.

[iConta.eu](/)
