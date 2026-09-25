---
title: "Casierie în valută: curs și înregistrare"
description: "Ce curs valutar se folosește la operațiunile de casă în valută și ce documente justificative distincte cere legea față de casieria în lei."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Casierie în valută: curs și înregistrare

Casieria în valută (de exemplu, avansuri în valută pentru deplasări externe sau încasări ocazionale în monedă străină) funcționează cu documente și un registru distincte de casieria în lei, iar conversia sumelor în lei pentru contabilitate se face la un curs de schimb precis reglementat — cel comunicat de Banca Națională a României pentru data operațiunii.

## Temeiul legal

::: ghid-temei
„(3) Sumele exprimate într-o monedă străină se convertesc în moneda națională a României, după cum urmează: [...] b) în oricare alt caz, sumele se convertesc în moneda națională a României prin utilizarea cursului de schimb valutar la data la care se primesc sau se plătesc sumele respective ori la altă dată prevăzută expres în prezentul cod. (4) În înțelesul prevederilor alin. (3), cursul de schimb valutar, folosit pentru a converti în moneda națională a României sumele exprimate în moneda străină, este cursul de schimb comunicat de Banca Națională a României valabil pentru datele respective, exceptând cazurile prevăzute expres în prezentul cod."
— Codul fiscal (Legea 227/2015), art. 9 alin. (3) lit. b) și alin. (4) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Cursul folosit este **cursul BNR valabil la data încasării sau plății efective** în numerar, nu un curs mediu lunar sau cursul de la data facturii, dacă acestea diferă.
- Pentru operațiunile de casă în valută există documente justificative distincte de cele în lei: **„Chitanța pentru operațiuni în valută"** (cod 14-4-1/a) și **„Registrul de casă în valută"** (cod 14-4-7/aA), care servesc drept document de înregistrare operativă a încasărilor/plăților în valută și de stabilire a soldului de casă la finalul fiecărei zile.
- Registrul de casă (în lei sau valută) se întocmește **zilnic**, pe baza documentelor justificative de încasări și plăți — nu retroactiv, la sfârșitul lunii.
- Avansurile în valută acordate pentru deplasări externe se justifică prin documente specifice (ordin de deplasare în străinătate, decont de cheltuieli valutare), care stau la baza înregistrării în registrul de casă în valută.

## Ce se greșește în practică

- Se folosește cursul BNR de la data facturii sau un curs mediu, în loc de cursul valabil la data efectivă a încasării/plății în numerar.
- Se ține un singur registru de casă „mixt", cu operațiuni în lei și în valută amestecate, în loc de registre separate pentru fiecare monedă.
- Se omit documentele justificative specifice operațiunilor în valută (chitanța pentru operațiuni în valută), folosind formularul obișnuit de chitanță, fără mențiunea valutei și a cursului aplicat.
- Se calculează greșit diferențele de curs valutar la închiderea zilei/lunii, prin neactualizarea soldului de casă în valută la cursul BNR de la data raportării.

## Ce face iConta.eu

Din verificarea codului, iConta.eu distinge explicit operațiunile de casă în valută de cele în lei: modulul de casierie contează automat operațiunile pe **contul 5314 „Casa în valută"**, dacă operațiunea este marcată ca fiind în valută, respectiv pe contul 5311 pentru operațiunile în lei — inclusiv pentru avansurile de trezorerie acordate sau restituite în valută. Aplicația face astfel distincția contabilă corectă cerută de operațiunile în valută, deși aplicarea cursului BNR exact la data operațiunii rămâne un element pe care contabilul trebuie să îl introducă/verifice la fiecare tranzacție.

[iConta.eu](/)
