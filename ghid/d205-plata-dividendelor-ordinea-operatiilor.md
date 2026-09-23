---
title: "D205 și plata dividendelor: ordinea operațiilor"
description: "Nota contabilă de dividend se înregistrează întâi; declararea la D205 este o funcționalitate separată, care preia datele din această notă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# D205 și plata dividendelor: ordinea operațiilor

Dividendul are două fețe: una contabilă (nota prin care se recunoaște datoria firmei față de asociat și impozitul reținut) și una declarativă (raportarea către ANAF prin D205). Cele două nu sunt aceeași operațiune, iar ordinea contează.

## Temeiul legal

::: ghid-temei
„Cota-parte din profit ce se plătește fiecărui asociat constituie dividend." — Legea 31/1990, art. 67 alin. (1)
:::

Din punct de vedere contabil, dividendul se recunoaște atunci când adunarea generală aprobă repartizarea profitului: se înregistrează datoria față de asociat (1171=457 pentru dividendul anual, sau 463=456 pentru cel interimar) și impozitul reținut (457=446, respectiv 456=446). Abia după ce nota contabilă există — cu suma brută, cota aplicată și impozitul calculat — datele respective pot fi raportate fiscal.

## Ce se greșește în practică

O greșeală frecventă e încercarea de a „declara" un dividend înainte ca acesta să fie efectiv aprobat și înregistrat contabil, sau, invers, omiterea raportării unui dividend deja înregistrat contabil. A doua greșeală e confuzia dintre dividendul interimar (463/456) și cel final (1171/457) atunci când se centralizează sumele pentru raportare.

## Ce face iConta.eu

iConta generează nota contabilă de dividend — repartizare, impozit calculat cu cota valabilă la data distribuirii și, opțional, plata netă — prin funcționalitatea de decontări cu asociații (F039). Declararea fiscală propriu-zisă a dividendului, prin formularul D205, este o funcționalitate separată în aplicație, distinctă de F039; F039 pregătește baza de date contabilă pe care se sprijină acea declarație, dar mecanismul intern de completare și depunere a D205 nu face parte din decontările cu asociații și nu e detaliat aici.

[iConta.eu](/)
