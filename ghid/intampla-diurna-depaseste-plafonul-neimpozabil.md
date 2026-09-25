---
title: "Ce se întâmplă dacă diurna depășește plafonul neimpozabil?"
description: "Doar partea din diurnă care depășește 2,5 ori nivelul stabilit pentru personalul bugetar devine impozabilă — nu întreaga sumă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce se întâmplă dacă diurna depășește plafonul neimpozabil?

Diurna acordată salariaților pentru delegare/detașare are un plafon neimpozabil legat de nivelul stabilit pentru personalul bugetar. Depășirea acestui plafon nu impozitează toată diurna — doar partea care depășește limita devine avantaj impozabil.

## Temeiul legal

::: ghid-temei
„indemnizația de delegare, indemnizația de detașare, [...] precum și orice alte sume de aceeași natură, altele decât cele acordate pentru acoperirea cheltuielilor de transport și cazare, primite de salariați [...] pe perioada desfășurării activității în altă localitate, în țară sau în străinătate, în interesul serviciului, pentru partea care depășește plafonul neimpozabil stabilit astfel: (i) în țară, 2,5 ori nivelul legal stabilit pentru indemnizație, prin hotărâre a Guvernului, pentru personalul autorităților și instituțiilor publice, în limita a 3 salarii de bază corespunzătoare locului de muncă ocupat."
— Legea 227/2015 (Codul fiscal), art. 76 alin. (2) lit. k) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.html)
:::

Ce rezultă concret din text, cu valorile în vigoare:

- **Nivelul de referință** e diurna stabilită pentru personalul bugetar prin hotărâre a Guvernului — 23 lei/zi, valoare stabilită prin Ordinul 1235/2023, aplicabilă de la 1 aprilie 2023 (majorare față de cei 20 lei/zi fixați inițial prin HG 714/2018).
- **Plafonul neimpozabil** e 2,5 ori acest nivel — 2,5 × 23 lei = **57,5 lei/zi**, sumă sub care diurna în țară e neimpozabilă.
- **Limita suplimentară**: chiar și partea sub plafonul de 2,5 ori nivelul de referință e neimpozabilă doar în limita a 3 salarii de bază corespunzătoare locului de muncă ocupat — o diurnă foarte mare, cumulată pe multe zile, poate depăși și această a doua limită.
- **Doar excedentul e impozabil** — venitul din depășirea plafonului se asimilează salariilor (art. 76 alin. 2), cu impozit pe venit și contribuții sociale aferente, în timp ce partea din interiorul plafonului rămâne neimpozabilă.

## Ce se greșește în practică

- Se impozitează întreaga diurnă odată ce depășește plafonul, în loc să se calculeze impozitul doar pentru partea excedentară (art. 76 alin. 2 lit. k) vorbește explicit de „partea care depășește plafonul").
- Se aplică vechea valoare de 20 lei/zi (plafon 50 lei) pentru perioade ulterioare datei de 1 aprilie 2023, când valoarea de referință a devenit 23 lei/zi (plafon 57,5 lei).
- Se ignoră a doua limită, cea de 3 salarii de bază — o diurnă zilnică sub plafonul de 57,5 lei poate deveni totuși parțial impozabilă dacă suma cumulată pe lună depășește 3 salarii de bază ale angajatului.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are o funcție dedicată pentru plafonul neimpozabil al diurnei (`core/deconturi.py`, `plafon_diurna`), care aplică exact formula legală — minimul dintre 2,5 ori diurna internă bugetară (period-aware: 20 lei/zi până la 31.03.2023, 23 lei/zi din 01.04.2023, conform Ordinului MF 1235/2023) și 3 salarii de bază raportate la zilele lucrătoare din lună — și calculează automat partea neimpozabilă și excedentul impozabil al diurnei acordate. Rezultatul alimentează decontul de deplasare și, pentru partea impozabilă, statul de plată și **D112**.

[iConta.eu](/)
