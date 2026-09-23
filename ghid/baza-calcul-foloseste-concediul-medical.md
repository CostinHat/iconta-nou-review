---
title: Ce bază de calcul se folosește pentru concediul medical?
description: Indemnizația de concediu medical se calculează cu procente de 55%, 65% sau 75%, în funcție de tipul concediului — dar formula exactă a bazei de calcul ține de o funcționalitate distinctă (F122), nu de calculul salarial obișnuit.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce bază de calcul se folosește pentru concediul medical?

Concediile medicale nu se calculează cu aceleași reguli ca salariul obișnuit — nu se aplică CAS, CASS și impozit pe salariu, ci procente specifice, aplicate pe o bază de calcul proprie, reglementată separat.

## Temeiul legal

::: ghid-temei
„Concedii medicale (context F080↔F122, nu obiectul direct al celor 12 titluri, dar apare în descrierea F080) — OUG 158/2005, cu procentele 55/65/75% (Legea 141/2025, de la 01.08.2025); nu e detaliat aici, nu e cerut de titluri." — Dosar de cercetare F080, secțiunea „Temei legal", pct. 7
:::

Ce e confirmat: actul normativ de bază e OUG 158/2005 privind concediile și indemnizațiile de asigurări sociale de sănătate, iar procentele de calcul ale indemnizației — 55%, 65% și 75%, în funcție de tipul concediului — au fost modificate prin Legea 141/2025, aplicabile de la 1 august 2025.

## Ce nu confirmă acest dosar

Formula exactă a bazei de calcul (perioada de referință folosită pentru medierea veniturilor, veniturile incluse și eventualele plafoane) nu a fost verificată verbatim în cercetarea de față — dosarul de cercetare a fost elaborat pentru F080 (calculul salarial brut→net) și marchează explicit acest subiect ca nefiind obiectul cercetării, ci al unei funcționalități distincte, F122. Acest ghid nu afirmă, deci, detalii pe care nu le poate susține cu o sursă verificată — pentru formula completă a bazei de calcul, verifică textul OUG 158/2005 direct sau resursele dedicate F122.

## Ce se greșește în practică

Greșeala frecventă e tratarea concediului medical ca un salariu obișnuit — aplicarea CAS, CASS, deducerii personale sau a impozitului de 10% pe o bază calculată ca la salariu, deși mecanismul concediilor medicale e distinct, cu procente proprii (55/65/75%). A doua greșeală: aplicarea unui procent greșit fără verificarea tipului de concediu, pentru că cele trei procente corespund unor situații diferite.

## Ce face iConta.eu

Motorul de calcul salarial (F080, `core/salarizare.py`, `monografie_salariu()`) tratează rețineri și cheltuieli specifice salariului obișnuit — CAS, CASS, impozit, CAM și, la part-time sub minim, suprataxarea. Dosarul de cercetare disponibil pentru F080 nu confirmă dacă și cum acest motor sau o componentă distinctă calculează baza indemnizației de concediu medical — pentru asta, verifică ecranul dedicat concediilor medicale din iConta.eu (F122).

[iConta.eu](/)
