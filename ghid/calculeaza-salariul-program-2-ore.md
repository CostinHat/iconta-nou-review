---
title: Cum se calculează salariul pentru program de 2 ore?
description: Pentru 2 ore/zi (un sfert de normă, la un program normal de 8 ore), brutul e mic — atât de mic încât, la salariul minim, deducerea personală poate anula complet impozitul. Vezi exemplul complet.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează salariul pentru program de 2 ore?

Pentru un salariat cu 2 ore/zi, la un program normal de 8 ore/zi, norma e un sfert (0,25). Ca și la orice normă parțială, brutul se calculează proporțional, iar contribuțiile CAS/CASS rămân supuse podelei minime. Exemplul de mai jos presupune un program normal de 8 ore/zi.

## Temeiul legal

::: ghid-temei
„(2) Drepturile salariale se acordă proporțional cu timpul efectiv lucrat, raportat la drepturile stabilite pentru programul normal de lucru." — Legea 53/2003 (Codul muncii), art.103 alin.(2)
:::

## Pasul 1 — brutul proporțional

Brut proporțional = brut la normă întreagă × (ore lucrate / ore normă). Pentru un angajat la salariul minim, fereastra 1 iulie – 31 decembrie 2026 (salariul minim 4.325 lei): brut = 4.325 × (2/8) = 1.081,25 lei.

## Pasul 2 — verificarea podelei CAS/CASS

Podeaua se calculează pe salariul minim redus cu facilitatea aplicabilă perioadei (facilitatea nu se aplică efectiv la part-time, dar podeaua se calculează cu ea scăzută din nivelul de referință), proratată pe fracțiunea de normă: podea = (4.325 − 200) × 0,25 = 1.031,25 lei.

Brutul contractual (1.081,25 lei) e peste podea (1.031,25 lei) → CAS și CASS se calculează direct pe brutul contractual.

## Pasul 3 — calculul complet: aici impozitul poate ajunge la zero

Deducerea personală se acordă la nivel maxim (865 lei, funcție de bază, fără persoane în întreținere), pentru că venitul brut lunar (1.081,25 lei) e sub salariul minim brut întreg. La un brut atât de mic, deducerea poate depăși baza rămasă după CAS și CASS — caz în care baza impozabilă devine negativă și impozitul se plafonează la zero.

| Element | Calcul | Valoare |
|---|---|---|
| Brut | 4.325 × 0,25 | 1.081,25 lei |
| CAS (25%) | 25% × 1.081,25 | 270,31 lei |
| CASS (10%) | 10% × 1.081,25 | 108,13 lei |
| Deducere personală | maximă (venit sub minim întreg) | 865 lei |
| Bază impozabilă | 1.081,25 − 270,31 − 108,13 − 865 = −162,19 → | 0 lei |
| Impozit (10%) | plafonat la zero | 0 lei |
| **Net** | 1.081,25 − 270,31 − 108,13 − 0 | **702,81 lei** |

## Ce se greșește în practică

Greșeala frecventă e aplicarea impozitului chiar și când baza impozabilă a ieșit negativă — o bază negativă înseamnă impozit zero, nu o valoare negativă care s-ar aduna la net. A doua greșeală, ca la orice normă parțială: presupunerea greșită că facilitatea „salariul minim neimpozabil" se aplică și aici, deși condiția normă întreagă o exclude.

## Ce face iConta.eu

`core/salarizare.py` calculează automat baza impozabilă și o plafonează la zero când deducerea personală depășește baza rămasă, evitând un impozit negativ. Brutul proporțional și verificarea podelei folosesc aceleași reguli „period-aware" din `core.common.COTE`, aplicate corect pentru fereastra din 2026 în care cade luna calculată.

[iConta.eu](/)
