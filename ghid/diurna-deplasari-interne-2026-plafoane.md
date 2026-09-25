---
title: "Diurna pentru deplasări interne 2026: plafoane și impozitare"
description: "Nivelul legal al diurnei/indemnizației de delegare pentru deplasările în țară și plafonul neimpozabil calculat pe baza lui, valabile în 2026."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Diurna pentru deplasări interne 2026: plafoane și impozitare

Diurna plătită unui salariat delegat sau detașat în altă localitate din țară e neimpozabilă doar până la un plafon calculat ca multiplu al nivelului stabilit prin hotărâre de Guvern pentru personalul bugetar — nu până la orice sumă stabilită liber prin contract sau regulament intern.

## Temeiul legal

::: ghid-temei
„ART. 1 Începând cu data de 1 aprilie 2023: a) cuantumul indemnizației de delegare prevăzute la art. 1 alin. (1) și alin. (2) lit. a) din anexa la Hotărârea Guvernului nr. 714/2018 [...] se majorează la 23 lei; [...] c) cuantumul indemnizației de detașare prevăzute la art. 4 alin. (1) din anexa la Hotărârea Guvernului nr. 714/2018 se majorează la 23 lei."
— OMF 1235/2023, art. 1 lit. a), c) (sursă: anaf_surse/omf_1235_2023.txt)

„k) [...] pentru partea care depășește plafonul neimpozabil stabilit astfel: (i) în țară, 2,5 ori nivelul legal stabilit pentru indemnizație, prin hotărâre a Guvernului, pentru personalul autorităților și instituțiilor publice, în limita a 3 salarii de bază corespunzătoare locului de muncă ocupat."
— Codul fiscal (Legea 227/2015), art. 76 alin. (2) lit. k) pct. (i) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cum se calculează plafonul, în 2026:

- Nivelul legal de referință pentru personalul bugetar e **23 lei/zi**, stabilit prin OMF 1235/2023 (care a majorat valoarea de 20 lei/zi fixată inițial de HG 714/2018, aplicabilă de la 1 aprilie 2023).
- Plafonul neimpozabil pentru un salariat din mediul privat, în deplasare internă, e **2,5 ori** acest nivel: 23 × 2,5 = **57,5 lei/zi**.
- Plafonul e dublu limitat: și la 2,5x nivelul bugetar pe zi, **și** la echivalentul a 3 salarii de bază lunare ale angajatului respectiv, per deplasare — oricare din cele două limite se atinge prima.
- Partea din diurnă care depășește 57,5 lei/zi (sau limita celor 3 salarii, dacă e mai mică) devine venit impozabil, asimilat salariului — supus impozitului pe venit și contribuțiilor sociale, ca orice altă sumă din categoria veniturilor salariale.

## Ce se greșește în practică

- Se aplică vechea valoare de 20 lei/zi (plafon 50 lei), uitând majorarea la 23 lei/zi (plafon 57,5 lei) intrată în vigoare la 1 aprilie 2023 și încă în vigoare în 2026.
- Se calculează plafonul doar din multiplul zilnic, fără să se verifice și limita alternativă a celor 3 salarii de bază — pentru un salariat cu salariu mic și o deplasare lungă, limita salarială poate deveni cea mai restrictivă.
- Se confundă diurna internă (2,5x nivelul HG 714/2018) cu diurna externă (deplasări în străinătate), care are un temei și un nivel de referință diferite (HG 518/1995).

## Ce face iConta.eu

La data acestui ghid, iConta.eu **calculează automat** plafonul de diurnă internă neimpozabilă: modulul `core/deconturi.py` aplică exact regula dublă din lege — minimul dintre 2,5 × diurna bugetară (23 lei/zi din 01.04.2023, deci plafon 57,5 lei/zi) și 3 × salariul de bază raportat la zilele lucrătoare din lună — și separă automat partea neimpozabilă de cea impozabilă a diurnei acordate, pe baza deconturilor de deplasare introduse. Modulul e „period-aware": pentru deconturi din perioada 2018 – 31.03.2023 folosește vechea diurnă bugetară de 20 lei/zi (plafon 50 lei), iar de la 01.04.2023 pe cea de 23 lei/zi (plafon 57,5 lei), conform Ordinului MF 1235/2023. Partea impozabilă calculată astfel se transferă în statul de plată.

[iConta.eu](/)
