---
title: "Cum se declară operațiunile cu nerezidenți"
description: "Care declarație se folosește pentru o operațiune cu un partener nerezident, în funcție de natura venitului plătit sau primit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se declară operațiunile cu nerezidenți

„Operațiuni cu nerezidenți" e o categorie foarte largă — declarația corectă depinde de natura operațiunii, nu de simplul fapt că partenerul e din altă țară. Un venit plătit unui nerezident (dividende, dobânzi, servicii) urmează un regim; o achiziție sau livrare de bunuri/servicii cu un partener din UE urmează alt regim, complet diferit.

## Temeiul legal

::: ghid-temei
„Plătitorii de venituri cu regim de reținere la sursă a impozitelor [...] au obligația să depună o declarație privind calcularea și reținerea impozitului pentru fiecare beneficiar de venit la organul fiscal competent, până în ultima zi a lunii februarie inclusiv a anului curent pentru anul expirat."
— Codul fiscal (Legea 227/2015), art. 231 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- **Venituri plătite unor nerezidenți** (dividende, dobânzi, redevențe, servicii de management/consultanță etc., conform art. 223 alin. (1) CF), pentru care firma română reține impozit la sursă, se declară în **D207**, anual, cu termenul de la art. 231 alin. (1).
- Obligația de declarare există și când impozitul datorat de nerezident e suportat de plătitorul de venit, nu doar reținut din suma plătită (art. 231 alin. (1^1) CF).
- Un beneficiar de dividende **fără CNP românesc valid** e tratat, pentru declararea la ANAF, ca nerezident — dividendele lui **nu se pot declara pe D205** (declarația pentru beneficiarii rezidenți), ci exclusiv pe D207.
- **Operațiuni comerciale cu parteneri din UE** (achiziții/livrări de bunuri, servicii B2B intracomunitare) sunt un subiect complet diferit, reglementat de art. 268/278 CF (TVA), declarate în D390 (declarația recapitulativă) — nu au legătură cu impozitul reținut la sursă și nu se declară în D207.

## Ce se greșește în practică

- Se declară pe D207 orice operațiune cu un partener străin, inclusiv achiziții și livrări comerciale obișnuite — D207 e strict pentru veniturile din categoriile enumerate la art. 223 CF, plătite de firma română unui beneficiar nerezident, nu pentru orice tranzacție cu un partener din altă țară.
- Se încearcă declararea dividendelor plătite unui asociat nerezident pe D205 — aplicația/regula fiscală refuză explicit acest lucru, pentru că un beneficiar fără CNP românesc valid se declară exclusiv pe D207.
- Se ignoră faptul că, pentru operațiunile comerciale cu UE (nu venituri cu reținere la sursă), declarația relevantă e D390, nu D207 — cele două declarații acoperă categorii de operațiuni total diferite.

## Ce face iConta.eu

Pentru veniturile plătite unor nerezidenți supuse reținerii la sursă, iConta.eu generează D207 pe baza datelor introduse manual de contabil pentru fiecare beneficiar (tip de venit, bază, impozit, stat de rezidență, act normativ) — aplicația nu are un registru automat al plăților către nerezidenți din care să preia aceste date, ci le colectează ca input direct. Pentru operațiunile comerciale cu parteneri din UE (achiziții/livrări de bunuri, servicii B2B), aplicația folosește un motor separat de operațiuni intracomunitare, care validează codul de TVA în VIES și clasifică operațiunea pentru D390 — un flux complet distinct de D207, fără suprapunere de cod între cele două module.

[iConta.eu](/)
