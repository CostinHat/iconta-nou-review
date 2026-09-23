---
title: Cum se înregistrează contabil concediile medicale?
description: Notele contabile pentru salarizarea obișnuită sunt confirmate în cod, dar dosarul de cercetare pentru F080 nu confirmă înregistrări dedicate pentru indemnizațiile de concediu medical — acestea țin de o funcționalitate distinctă (F122).
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează contabil concediile medicale?

Pentru salarizarea obișnuită, monografia contabilă e clar confirmată în codul iConta.eu. Pentru concediile medicale — reglementate separat, prin OUG 158/2005 — cercetarea disponibilă pentru funcționalitatea de calcul salarial (F080) nu confirmă notele contabile specifice.

## Temeiul legal

::: ghid-temei
„Concedii medicale (context F080↔F122, nu obiectul direct al celor 12 titluri, dar apare în descrierea F080) — OUG 158/2005, cu procentele 55/65/75% (Legea 141/2025, de la 01.08.2025); nu e detaliat aici, nu e cerut de titluri." — Dosar de cercetare F080, secțiunea „Temei legal", pct. 7
:::

## Ce e confirmat pentru salarizarea obișnuită

`monografie_salariu()` (`core/salarizare.py`, linia 390) generează notele contabile standard pentru un stat de plată obișnuit: 641/421 (cheltuiala cu salariile), 421/4315 (reținere CAS), 421/4316 (reținere CASS), 421/444 (reținere impozit), 646/436 (cheltuiala CAM a angajatorului), opțional 642/5328 (tichete de masă) și, la part-time sub salariul minim, 6451/4315 și 6453/4316 (cheltuiala de suprataxare a angajatorului).

## Ce nu confirmă acest dosar

Dosarul de cercetare pentru F080 nu confirmă dacă `monografie_salariu()` sau o altă componentă din cod generează note contabile dedicate pentru indemnizațiile de concediu medical (OUG 158/2005) — subiectul e marcat explicit ca aparținând unei funcționalități distincte, F122, nedetaliată în cercetarea de față. Acest ghid nu inventează conturi sau formule de înregistrare pentru concediul medical fără o sursă verificată — pentru înregistrarea contabilă corectă (de regulă, cu distincția între zilele suportate de angajator și cele suportate din bugetul asigurărilor sociale de sănătate), verifică cu un contabil sau cu resursele dedicate F122.

## Ce se greșește în practică

Greșeala frecventă e înregistrarea indemnizației de concediu medical prin aceleași conturi ca salariul obișnuit (421/4315, 421/4316, 421/444), fără să se țină cont de faptul că indemnizația nu urmează mecanica CAS/CASS/impozit a salariului — vezi „Ce venituri intră în baza de calcul a concediului medical?" pentru diferența dintre cele două mecanisme.

## Ce face iConta.eu

Pentru salarizarea obișnuită, notele contabile sunt generate automat de `monografie_salariu()`, pe baza rezultatului calculului din `_calcul_salariu_2018()`. Pentru concediile medicale, verifică ecranul dedicat din iConta.eu (F122) — dosarul de cercetare pentru F080 nu acoperă acest flux.

[iConta.eu](/)
