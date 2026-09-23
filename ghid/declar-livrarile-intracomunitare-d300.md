---
title: "Cum declar livrările intracomunitare în D300?"
description: Livrările de bunuri și prestările de servicii intracomunitare se derivă automat din facturile cu partener UE. Manual, prin F251, rămân doar regularizările — iar orice încercare de a dubla o sumă deja derivată automat e blocată explicit.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum declar livrările intracomunitare în D300?

Livrarea de bunuri sau prestarea de servicii către un partener din UE se declară, în cazul normal, automat — motorul D300 o derivă direct din factură. Manual, prin F251, rămân doar regularizările ulterioare.

## Temeiul legal

::: ghid-temei
„Livrări intracomunitare de bunuri, scutite conform art. 294 alin. (2) lit. a) și d) din Codul fiscal" — eticheta oficială a rândului R1, `d300_manual_api.py`, confirmată contra structurii ANAF D300 v12 (OPANAF 174/2026)
:::

## Ce se derivă automat

Pentru facturile cu partener din UE (`tert_tara` în spațiul UE), motorul derivă automat:

- **livrare de bunuri către UE, cotă 0%** → rd.1 (`R1_1`);
- **prestare de servicii intracomunitare emisă** (dacă tipul din D390 e „P") → rd.3 (`R3_1`/`R3_1_1`).

## Rândul R1 e și în allow-list — dar doar ca excepție

R1 apare și în lista de rânduri acceptate manual în F251. Asta nu înseamnă că se introduce în paralel cu derivarea automată: gardul anti-dublă-numărare al motorului respinge orice suprapunere. Există un test dedicat exact pentru acest caz: o livrare intracomunitară deja derivată automat pe rd.1, plus o încercare de a introduce manual `R1_1` → eroare (`ValueError`), cu mesaj care conține explicit „dublă numărare" (`test_antidubla_numarare_ic_livrare_manual_ridica`). R1 manual are sens doar ca fallback, când operațiunea n-a fost deloc captată automat.

## Ce e strict manual: regularizările

Rândurile **R2** („Regularizări livrări intracomunitare scutite conform art. 294 alin. (2) lit. a) și d)") și **R4** (regularizări prestări servicii intracomunitare) apar, în motorul D300, doar în formula de însumare rd.17, niciodată ca țintă a unei atribuiri automate. Sunt 100% manuale — orice corecție ulterioară a unei livrări/prestări deja înregistrate trece pe aceste rânduri.

## Ce se greșește în practică

Se introduce manual R1 sau R3 pentru o livrare deja captată automat dintr-o factură cu partener UE — aplicația respinge cererea cu eroare de dublă numărare, confirmat printr-un test dedicat exact pe acest scenariu.

## Ce face iConta.eu

Motorul D300 derivă automat rd.1/rd.3 din facturile cu partener din UE, folosind și clasificarea bun/serviciu din D390 pentru distincția livrare-bunuri vs. prestare-servicii. Panoul F251 acoperă regularizările (R2/R4) și, ca excepție validată, introducerea manuală a R1/R3 doar când operațiunea nu a fost deloc derivată automat — cu gard explicit împotriva dublei numărări.

[iConta.eu](/)
