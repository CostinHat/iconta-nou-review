---
title: Cum se calculează impozitul micro trimestrial?
description: Impozitul micro se calculează independent pentru fiecare trimestru, aplicând cota unică de 1% la veniturile înregistrate contabil în trimestrul respectiv, fără cumulare de la începutul anului.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se calculează impozitul micro trimestrial?

Spre deosebire de impozitul pe profit (care se calculează cumulat de la începutul anului), impozitul pe veniturile microîntreprinderilor tratează fiecare trimestru independent. Explicăm formula exactă și de ce cumularea e o greșeală frecventă.

## Temeiul legal

::: ghid-temei
**CF art. 51 alin. (1):**
> „Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.html`

**CF art. 53 alin. (1):**
> „Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie **veniturile din orice
> sursă**, din care se scad: a) veniturile aferente costurilor stocurilor de produse; b) veniturile
> aferente costurilor serviciilor în curs de execuție; ... j) valoarea reducerilor comerciale acordate
> ulterior facturării, înregistrate în contul «709»..."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt:6480-6519`
:::

## Formula, trimestru cu trimestru

Formula e simplă: `impozit_trimestru = venituri_trimestrului × 1%`, unde veniturile trimestrului sunt cele înregistrate contabil (cont 70x/75x/76x minus 709) strict în intervalul trimestrului respectiv — nu cumulate de la 1 ianuarie. Fiecare trimestru „pornește de la zero": un trimestru cu venituri mari nu e afectat de un trimestru anterior slab, și invers.

Important: de la 1 ianuarie 2026, cota de 1% este **unică**, indiferent de numărul de salariați — a dispărut splitul vechi 1%/3% (cu/fără salariați), împreună cu pragul de 60.000 EUR care declanșa acel split.

::: ghid-exemplu
Trimestrul I: venituri 30.000 lei → impozit 300 lei.
Trimestrul II: venituri 45.000 lei → impozit 450 lei (nu se adaugă la cele 30.000 lei din T1).
Fiecare trimestru se calculează separat, pe baza proprie de venituri.
:::

## Ce se greșește în practică

- Se cumulează veniturile de la începutul anului, ca la impozitul pe profit — micro nu funcționează așa.
- Se aplică vechea cotă de 3% (pentru firme fără salariați) sau se verifică greșit pragul de 60.000 EUR — ambele au fost eliminate din 2026, cota fiind unic 1%.
- Se scade din bază deducerea de sponsorizare (până la 20% din impozit) — abrogată din 2024, nu se mai aplică pentru niciun trimestru din 2024 încoace.
- Se calculează baza pe încasări, nu pe veniturile facturate/înregistrate contabil.

## Ce face iConta.eu

`core/d100.py`, funcția `deriva_obligatii`, calculează obligația cod 121 (impozit micro) exact ca `venituri_trimestru × cotă(1%)`, unde baza e veniturile trimestrului curent citite din conturile 70x/75x/76x minus 709, necumulate de la începutul anului — fiecare trimestru fiind tratat independent. Deducerea de sponsorizare nu este implementată în motor, corect, pentru că e lege abrogată din 2024.

[iConta.eu](/)
