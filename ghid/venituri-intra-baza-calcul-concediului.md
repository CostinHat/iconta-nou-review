---
title: Ce venituri intră în baza de calcul a concediului medical?
description: Ce e sigur: indemnizația se aplică pe procente de 55/65/75%, nu pe reținerile salariului obișnuit. Lista exactă a veniturilor incluse în baza de calcul ține însă de o funcționalitate distinctă (F122).
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce venituri intră în baza de calcul a concediului medical?

Indemnizația de concediu medical nu se calculează din salariul brut al lunii curente, la fel ca un stat de plată obișnuit, ci dintr-o bază proprie, reglementată de OUG 158/2005. Lista exactă a veniturilor incluse în acea bază nu face însă parte din cercetarea disponibilă pentru funcționalitatea de calcul salarial (F080).

## Temeiul legal

::: ghid-temei
„Concedii medicale (context F080↔F122, nu obiectul direct al celor 12 titluri, dar apare în descrierea F080) — OUG 158/2005, cu procentele 55/65/75% (Legea 141/2025, de la 01.08.2025); nu e detaliat aici, nu e cerut de titluri." — Dosar de cercetare F080, secțiunea „Temei legal", pct. 7
:::

Confirmat: procentele de calcul (55%, 65%, 75%) au fost actualizate prin Legea 141/2025, aplicabile de la 1 august 2025, pe temeiul general al OUG 158/2005.

## Ce nu confirmă acest dosar

Care venituri intră exact în baza de calcul (dacă se includ sau nu sporuri, indemnizații anterioare, veniturile din contracte multiple, perioada de referință folosită) nu a fost verificat verbatim în corpusul cercetat pentru F080 — dosarul marchează explicit acest subiect ca aparținând unei funcționalități distincte (F122), nedetaliată în cercetarea de față. Un lucru e totuși cert, din structura confirmată a motorului F080: baza de calcul a concediului medical nu e aceeași cu baza de calcul a salariului obișnuit (brut redus, eventual, cu facilitatea „salariul minim neimpozabil") — cele două mecanisme sunt distincte, cu reguli proprii.

## Ce se greșește în practică

Greșeala frecventă e presupunerea că baza de calcul a concediului medical e salariul brut al lunii în care survine concediul — de fapt, baza se calculează dintr-o perioadă de referință proprie, reglementată de OUG 158/2005, nu din brutul lunii curente. A doua greșeală: aplicarea facilității „salariul minim neimpozabil" sau a deducerii personale la calculul indemnizației — aceste mecanisme aparțin exclusiv calculului salarial obișnuit (F080), nu indemnizațiilor de asigurări sociale de sănătate.

## Ce face iConta.eu

Pentru calculul salarial obișnuit, `core/salarizare.py` folosește ca bază brutul lunii (eventual redus cu facilitatea), conform registrului „period-aware" `core.common.COTE`. Dosarul de cercetare pentru F080 nu confirmă dacă și cum acest mecanism se leagă de calculul indemnizațiilor de concediu medical — pentru veniturile incluse în baza de calcul a concediului medical, verifică ecranul dedicat (F122) sau textul OUG 158/2005.

[iConta.eu](/)
