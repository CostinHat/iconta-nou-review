---
title: Cum se calculează salariul pentru program de 4 ore?
description: Pentru 4 ore/zi (jumătate de normă, la un program normal de 8 ore), brutul se calculează proporțional cu norma, apoi se verifică podeaua CAS/CASS. Vezi exemplul complet, cu net.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează salariul pentru program de 4 ore?

Pentru un salariat cu 4 ore/zi, la un program normal de 8 ore/zi, norma e jumătate (0,5). Brutul contractual se calculează proporțional, dar contribuțiile CAS/CASS rămân supuse unei podele minime — nu pot scădea oricât de mult doar pentru că norma e redusă. Exemplul de mai jos presupune un program normal de 8 ore/zi; dacă programul normal e altul, fracțiunea de normă se recalculează în consecință.

## Temeiul legal

::: ghid-temei
„(2) Drepturile salariale se acordă proporțional cu timpul efectiv lucrat, raportat la drepturile stabilite pentru programul normal de lucru." — Legea 53/2003 (Codul muncii), art.103 alin.(2)
:::

## Pasul 1 — brutul proporțional

Brut proporțional = brut la normă întreagă × (ore lucrate / ore normă). Pentru un angajat la salariul minim, fereastra 1 iulie – 31 decembrie 2026 (salariul minim 4.325 lei): brut = 4.325 × (4/8) = 2.162,50 lei.

## Pasul 2 — verificarea podelei CAS/CASS

Facilitatea „salariul minim neimpozabil" nu se aplică la normă parțială (una din cele 4 condiții cumulative e norma întreagă). Totuși, podeaua contribuțiilor se calculează pe salariul minim redus cu facilitatea aplicabilă perioadei, proratată pe fracțiunea de normă: podea = (4.325 − 200) × 0,5 = 2.062,50 lei.

Brutul contractual (2.162,50 lei) e peste podea (2.062,50 lei) → CAS și CASS se calculează direct pe brutul contractual, fără suprataxare.

## Pasul 3 — calculul complet, cu net

Deducerea personală se acordă la nivel maxim (865 lei, funcție de bază, fără persoane în întreținere), pentru că venitul brut lunar realizat (2.162,50 lei) e sub salariul minim brut întreg (4.325 lei) — pragul la care începe reducerea treptată a deducerii.

| Element | Calcul | Valoare |
|---|---|---|
| Brut | 4.325 × 0,5 | 2.162,50 lei |
| CAS (25%) | 25% × 2.162,50 | 540,63 lei |
| CASS (10%) | 10% × 2.162,50 | 216,25 lei |
| Deducere personală | maximă (venit sub minim întreg) | 865 lei |
| Bază impozabilă | 2.162,50 − 540,63 − 216,25 − 865 | 540,62 lei |
| Impozit (10%) | 10% × 540,62 | 54,06 lei |
| **Net** | 2.162,50 − 540,63 − 216,25 − 54,06 | **1.351,56 lei** |

## Ce se greșește în practică

Greșeala frecventă e aplicarea facilității „salariul minim neimpozabil" și la normă parțială — condiția normă întreagă exclude explicit part-time-ul din facilitate. A doua greșeală: proratarea deducerii personale pe fracțiunea de normă — deducerea nu se proratează, se aplică integral (la nivelul maxim din scară) atâta timp cât venitul brut realizat e sub salariul minim întreg.

## Ce face iConta.eu

Brutul proporțional și verificarea podelei sunt calculate automat de `core/salarizare.py` — funcția `calcul_salariu()` verifică `tip_norma` (întreagă/parțială) și aplică regula „baza_podea" (liniile 292-323) doar când brutul e sub prag. Cotele și salariul minim aplicabil vin din registrul „period-aware" `core.common.COTE`, potrivit lunii calculate.

[iConta.eu](/)
