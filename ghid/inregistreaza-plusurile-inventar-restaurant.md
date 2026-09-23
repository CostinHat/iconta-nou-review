---
title: Cum se înregistrează plusurile de inventar într-un restaurant?
description: Un plus de stoc constatat la inventariere se evaluează la valoare justă și se înregistrează pe contul de venit corespondent contului de stoc.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează plusurile de inventar într-un restaurant?

Un plus de gestiune — mai multă marfă sau materie primă găsită faptic decât arată evidența contabilă — nu e un "câștig" pe care restaurantul îl poate trece direct la venit oricum dorește. Legea impune o metodă de evaluare, iar contabilitatea o metodă de înregistrare.

## Temeiul legal

::: ghid-temei
"d) la valoarea justă - pentru bunurile obținute cu titlu gratuit sau constatate plus la inventariere." — OMFP 1802/2014, pct. 75 alin. (1) lit. d)
:::

Bunul găsit în plus se evaluează deci la valoare justă (nu, de exemplu, la ultimul preț de achiziție cunoscut, dacă acesta diferă de valoarea justă la data constatării). Rezultatul se înregistrează în contabilitate pe contul de venit corespondent contului de stoc pe care s-a constatat plusul — de exemplu, un plus la marfă (371) se înregistrează prin reducerea cheltuielii cu marfa vândută (607), iar un plus la produse finite (345) prin cont de venit din producția stocată (711).

## Ce se greșește în practică

- Se evaluează plusul la costul de achiziție istoric, nu la valoarea justă de la data constatării — ceea ce poate denatura rezultatul, mai ales la marfa cu preț volatil.
- Se contabilizează plusul direct ca venit generic, fără să se folosească contul de corespondență specific tipului de stoc (marfă, materii prime, produse finite).
- Se confundă plusul de stoc cu plusul de mijloc fix — cele două au conturi de corespondență complet diferite (607/601/602/603/711/608 pentru stocuri, 4754 pentru mijloace fixe) și tratament fiscal diferit.

## Ce face iConta.eu

Operația "Plus stoc" din ecranul de inventariere determină automat contul de corespondență din contul de stoc dat: 371 → 607, 301 → 601, 302 → 602, 303 → 603, 345 → 711, 381 → 608. Doar aceste șase conturi de stoc sunt acceptate — orice alt cont introdus e refuzat de aplicație. Valoarea introdusă de contabil reprezintă valoarea justă stabilită de comisia de inventariere; aplicația nu recalculează sau nu verifică ea însăși valoarea justă.

Nota contabilă generată primește automat sufixul "- OMFP 2861/2009".

[iConta.eu](/)
