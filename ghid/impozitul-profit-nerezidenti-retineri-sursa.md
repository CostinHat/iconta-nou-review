---
title: "Impozitul pe profit la nerezidenți: rețineri la sursă"
description: "De ce veniturile plătite unor nerezidenți nu intră sub impozitul pe profit, ci sub un regim separat de reținere la sursă, cu declarația D207."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Impozitul pe profit la nerezidenți: rețineri la sursă

Denumirea „impozitul pe profit la nerezidenți" e înșelătoare — impozitul reținut la sursă pentru veniturile plătite unor persoane nerezidente **nu face parte din impozitul pe profit** (Titlul II din Codul fiscal), ci dintr-un capitol distinct, dedicat exclusiv veniturilor obținute din România de nerezidenți (Titlul VI). Firma românească plătitoare de venit are rol de reținător, nu de contribuabil al acestui impozit.

## Temeiul legal

::: ghid-temei
„Nerezidenții care obțin venituri impozabile din România au obligația de a plăti impozit conform prezentului capitol."
— Codul fiscal (Legea 227/2015), art. 221 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Impozitul se aplică asupra veniturilor **brute** impozabile obținute din România de nerezidenți (art. 222) — nu asupra unui profit net calculat de firma română.
- Veniturile impozabile enumerate la art. 223 alin. (1) includ, printre altele: dividende plătite de un rezident, dobânzi, redevențe, comisioane, servicii de management/consultanță, servicii prestate în România.
- Cota standard e **16%** pentru dividende (art. 224 alin. (4) lit. b), modificată prin Legea 141/2025, aplicabilă dividendelor distribuite începând cu 1 ianuarie 2026) și, ca regulă generală, **16%** pentru celelalte venituri impozabile enumerate (lit. d); cota poate fi **10%** pentru anumite categorii, în condițiile lit. c^1).
- **„Plătitorii de venituri cu regim de reținere la sursă a impozitelor... au obligația să depună o declarație privind calcularea și reținerea impozitului pentru fiecare beneficiar de venit"** — art. 231 alin. (1) CF — aceasta e declarația D207, cu termen anual, până în ultima zi a lunii februarie inclusiv a anului curent, pentru anul expirat.
- Cota din convenția de evitare a dublei impuneri (dacă e mai mică decât cota internă) se poate aplica doar dacă nerezidentul prezintă plătitorului certificatul de rezidență fiscală **în momentul plății venitului** (art. 230 alin. (2)); fără certificat, se aplică automat cota internă din Titlul VI.

## Ce se greșește în practică

- Se caută regula de impozitare a nerezidentului în declarația de impozit pe profit (D101) — regimul corect e separat, în Titlul VI CF, iar declarația specifică e D207, nu D101.
- Se aplică automat cota redusă dintr-o convenție de evitare a dublei impuneri, fără să existe la momentul plății un certificat de rezidență fiscală valabil prezentat de nerezident — fără el, legea impune cota internă.
- Se presupune că firma română plătește impozit pe venitul obținut de nerezident din fondurile proprii, ca pe orice altă cheltuială — de fapt, firma reține impozitul din suma datorată nerezidentului și îl varsă la buget, în calitate de plătitor obligat, conform art. 224 alin. (1).

## Ce face iConta.eu

D207 din iConta.eu e o declarație în care contabilul introduce manual, pentru fiecare beneficiar nerezident, venitul plătit, tipul de venit, statul de rezidență, codul fiscal și actul normativ aplicabil (Cod fiscal, convenție sau acord internațional) — aplicația **nu deduce automat codul de venit, actul normativ sau cota aplicabilă**; acestea sunt introduse de contabil, pe baza analizei fiecărui caz. Motorul verifică totuși coerența internă a datelor introduse — de exemplu, pentru categoriile de venit scutite de impozit, forțează automat impozitul la zero — și respinge la generare orice beneficiar fără informațiile obligatorii completate (tip de venit valid, denumire, stat de rezidență, cod fiscal, act normativ). Din moment ce cota și actul normativ nu sunt calculate automat, riscul unei cote hardcodate greșite (prezent la alte declarații) nu se aplică aici, dar responsabilitatea aplicării corecte a cotei (internă sau convențională) rămâne integral a contabilului.

[iConta.eu](/)
