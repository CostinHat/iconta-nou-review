---
title: Micro pentru SRL cu asociați nerezidenți — ce trebuie să știți
description: Rezidența fiscală a asociaților nu afectează încadrarea firmei la regimul micro. Ce se schimbă, în schimb, e impozitarea dividendului plătit unui asociat nerezident — un subiect separat de distribuirea în sine.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Micro pentru SRL cu asociați nerezidenți — ce trebuie să știți

Un SRL cu unul sau mai mulți asociați nerezidenți nu e, prin acest simplu fapt, exclus de la regimul micro — încadrarea la impozitul pe veniturile microîntreprinderilor se face după plafonul de venituri și celelalte condiții din Codul fiscal, nu după cetățenia sau rezidența fiscală a asociaților. Acest aspect (praguri, condiții micro) nu ține de funcționalitatea „Decontări asociați" din iConta.eu și nu face parte din dosarul de cercetare care stă la baza acestui ghid.

Ce se schimbă cu adevărat atunci când un asociat e nerezident e modul de impozitare a dividendului pe care îl încasează — și acesta e un subiect care depășește, la rândul lui, funcționalitatea de decontări cu asociații.

## Temeiul legal

::: ghid-temei
„Cota-parte din profit ce se plătește fiecărui asociat constituie dividend."
— Legea 31/1990, art. 67 alin. (1)
:::

Acest text stabilește dreptul la dividend indiferent de rezidența asociatului. Contabil, iConta.eu calculează nota de dividend cu cota standard, aceeași pentru orice asociat (`1171 = 457`, `457 = 446`). Ce nu e acoperit de acest calcul standard e regimul special aplicabil dividendelor plătite nerezidenților — cotă redusă prin convenția de evitare a dublei impuneri, certificat de rezidență fiscală, declararea prin formularul specific impozitului reținut la sursă pentru nerezidenți. Acestea țin de o altă funcționalitate a aplicației (declarația privind impozitul reținut la sursă pentru nerezidenți), separată de „Decontări asociați", și nu au fost verificate în acest dosar.

## Ce se greșește în practică

- Se presupune că prezența unui asociat nerezident schimbă automat regimul fiscal al firmei (micro vs. profit) — fals, criteriul e plafonul de venituri, nu naționalitatea/rezidența asociaților.
- Se reține impozitul pe dividend cu cota standard internă pentru un asociat nerezident, fără să se verifice dacă o convenție de evitare a dublei impuneri prevede o cotă mai mică, condiționată de prezentarea certificatului de rezidență fiscală.
- Se omite declararea separată aferentă impozitului reținut la sursă pentru nerezidenți, tratând dividendul ca și cum ar fi fost plătit unui asociat rezident.

## Ce face iConta.eu

Funcționalitatea **Decontări asociați** (Operațiuni speciale > Finanțare) calculează și înregistrează nota contabilă a dividendului cu cota standard aplicabilă la data distribuirii, indiferent de rezidența asociatului — `1171 = 457` brut, `457 = 446` impozit. Aplicarea unei cote reduse prin convenție și declararea aferentă impozitului pe veniturile nerezidenților nu fac parte din această funcționalitate; verificați separat regimul de rezidență fiscală înainte de a plăti dividendul.

[iConta.eu](/)
