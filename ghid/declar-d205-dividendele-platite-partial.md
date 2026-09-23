---
title: Cum declar în D205 dividendele plătite parțial?
description: D205 calculează baza impozabilă și impozitul pe dividendul efectiv plătit, nu pe cel distribuit — dacă plata s-a făcut parțial, se declară doar partea plătită, iar restul intră în declarația anului în care se plătește.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum declar în D205 dividendele plătite parțial?

Un dividend poate fi aprobat integral, dar plătit efectiv în tranșe — mai ales când firma nu are lichiditate suficientă pentru toată suma dintr-o dată. D205 tratează distins cele două momente: distribuirea și plata.

## Temeiul legal

::: ghid-temei
**Structura oficială D205 (OPANAF 102/2025)**, câmpurile 7.V și 8.V: coloana „divid_D" înregistrează dividendul **distribuit**, coloana „divid_P" înregistrează dividendul **plătit** — sunt sume distincte, nu una derivată automat din cealaltă.
:::

Declarația D205 e o funcționalitate separată de decontările cu asociații (F039 alimentează doar notele contabile din care se calculează sumele) — D205 propriu-zis e generat de motorul declarativ, pe baza mișcărilor din contul 457 „Dividende de plată". Regula de calcul, confirmată direct în codul declarației: baza impozabilă și impozitul se calculează pe dividendul efectiv **plătit**, nu pe cel distribuit, pentru că impozitul pe dividende se reține la momentul plății.

Dacă un dividend aprobat de 100.000 lei se plătește 60.000 lei într-un an și restul de 40.000 lei în anul următor, D205 pentru primul an declară baza și impozitul aferente celor 60.000 lei plătiți, iar D205 pentru anul următor declară restul, la momentul plății efective. Suma distribuită (divid_D) e mereu mai mare sau egală cu suma plătită (divid_P) — nu se poate plăti cumulat mai mult decât s-a distribuit.

## Ce se greșește în practică

- Se declară în D205 întreaga sumă aprobată, imediat, deși plata s-a făcut doar parțial — corect e declararea doar a părții efectiv plătite în anul respectiv.
- Se uită să se declare restul sumei în anul în care se face plata rămasă, considerând (greșit) că dividendul „s-a declarat deja" complet la aprobare.

## Ce face iConta.eu

Declarația D205 e generată automat de iConta.eu din mișcările contului 457, calculând separat suma distribuită (creditul contului) și suma plătită (debitul contului), proporțional cu cota fiecărui asociat. Baza impozabilă și impozitul declarate pentru fiecare beneficiar se calculează exclusiv pe partea plătită în perioada declarației, exact conform structurii oficiale. Notele contabile care alimentează acest calcul — dividendul aprobat și impozitul reținut — provin din ecranul de decontări asociați.

[iConta.eu](/)
