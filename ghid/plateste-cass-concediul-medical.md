---
title: Se plătește CASS pentru concediul medical?
description: CASS 10% e cota confirmată pentru veniturile salariale obișnuite — dar dacă și cum se aplică indemnizațiilor de concediu medical (OUG 158/2005) nu a fost verificat în cercetarea disponibilă pentru F080.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Se plătește CASS pentru concediul medical?

Întrebarea e legitimă, pentru că indemnizația de concediu medical nu urmează mecanica salariului obișnuit. Răspunsul cert cere însă o sursă pe care cercetarea disponibilă pentru funcționalitatea de calcul salarial (F080) nu o acoperă.

## Temeiul legal

::: ghid-temei
„Concedii medicale (context F080↔F122, nu obiectul direct al celor 12 titluri, dar apare în descrierea F080) — OUG 158/2005, cu procentele 55/65/75% (Legea 141/2025, de la 01.08.2025); nu e detaliat aici, nu e cerut de titluri." — Dosar de cercetare F080, secțiunea „Temei legal", pct. 7
:::

## Ce e confirmat

CASS 10% (CF art.156) e cota confirmată pentru veniturile salariale obișnuite, calculată pe brutul angajatului (eventual redus cu facilitatea „salariul minim neimpozabil"). Concediile medicale funcționează pe un mecanism diferit — indemnizația se calculează cu procente proprii (55%, 65% sau 75%, actualizate prin Legea 141/2025, aplicabile de la 1 august 2025), nu pe cotele CAS/CASS/impozit ale salariului.

## Ce nu confirmă acest dosar

Dacă indemnizațiile de concediu medical sunt sau nu supuse CASS, și în ce condiții, nu a fost verificat verbatim în corpusul cercetat pentru F080 — dosarul marchează explicit acest subiect ca aparținând unei funcționalități distincte (F122), în afara obiectului celor 12 titluri cercetate pentru calculul salarial. Acest ghid nu oferă, deci, un răspuns cert pe acest punct — pentru certitudine, verifică textul OUG 158/2005 sau resursele dedicate F122.

## Ce se greșește în practică

Greșeala frecventă e presupunerea, fără verificare, că toate veniturile unui salariat (inclusiv indemnizațiile de asigurări sociale de sănătate) sunt tratate identic cu salariul obișnuit din perspectiva CAS/CASS — cele două mecanisme au baze de calcul și reguli distincte, confirmate ca atare în structura codului (motorul de salarizare F080 e separat de cel al concediilor medicale).

## Ce face iConta.eu

Motorul de calcul salarial (`core/salarizare.py`) aplică CASS 10% exclusiv pe veniturile salariale obișnuite, din registrul „period-aware" `core.common.COTE`. Pentru tratamentul CASS al indemnizațiilor de concediu medical, verifică ecranul dedicat din iConta.eu (F122) — dosarul de cercetare pentru F080 nu acoperă acest flux.

[iConta.eu](/)
