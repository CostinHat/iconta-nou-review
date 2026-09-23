---
title: Cum mut o sumă înregistrată pe contul greșit?
description: Mutarea unei sume de pe un cont pe altul înseamnă, tehnic, aceeași corecție ca orice cont greșit — editarea liniei cât timp nota e ciornă, sau o notă de stornare dacă a fost deja validată. Nu există în iConta.eu o operație separată de „mutare între conturi".
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum mut o sumă înregistrată pe contul greșit?

„Mutarea" unei sume de pe un cont pe altul nu e, în iConta.eu, o funcție separată — e exact aceeași operație ca orice altă corecție de cont: se înlocuiește contul pe linia respectivă a notei, cât timp se poate, sau se stornează, când nu se mai poate.

## Temeiul legal

::: ghid-temei
„Persoanele prevăzute la art. 1 alin. (1)-(4) au obligația să conducă contabilitatea în partidă dublă și să întocmească situații financiare anuale, potrivit reglementărilor contabile aplicabile." — Legea contabilității nr. 82/1991, art. 5 alin. (1)

„Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (stornare în roșu), fie prin înregistrarea inversă a acesteia (stornare în negru), în funcție de politica contabilă și programele informatice utilizate." — OMFP 1802/2014, Anexa 1 – Reglementări contabile, pct. 69
:::

Partida dublă nu are un concept de „transfer" al unei sume între conturi ca operație distinctă — orice mutare e, contabil, fie o corecție a înregistrării inițiale (dacă nu a intrat definitiv), fie o stornare urmată de reînregistrare pe contul corect.

## Cum corectez în iConta.eu

- **Nota e ciornă** → se editează direct linia cu suma greșit atribuită: se schimbă contul (debit sau credit), păstrând suma corectă. Nu e nevoie de o operație separată de „transfer" — e o simplă corecție de linie, cu condiția ca noul cont să existe în planul de conturi al firmei.
- **Nota e validată** → nu se mai poate „muta" nimic direct. Corecția se face printr-o notă nouă de stornare: suma iese de pe contul greșit (înregistrare cu semn opus sau inversă, conform pct. 69) și intră, printr-o linie nouă, pe contul corect.
- Dacă suma greșit atribuită provine dintr-o notă de contare a unei facturi deja validate, „mutarea" trece prin stornarea facturii, nu prin dezlegarea sau editarea directă a notei — aplicația refuză explicit dezlegarea unei note care e chiar evidența contabilă a facturii.
- Luna închisă blochează atât editarea ciornei, cât și introducerea notei de stornare, indiferent care sunt cele două conturi implicate.

## Ce se greșește în practică

- Se caută o funcție de „transfer între conturi" care să nu existe ca atare — corecția reală e fie editare de linie (ciornă), fie stornare (validată).
- Se editează suma pe un cont și se lasă contul vechi cu soldul neschimbat, uitând că, într-o notă validată, orice corecție cere o linie de stornare pe fiecare cont afectat, nu doar pe unul.
- Se face corecția fără să se verifice mai întâi dacă nota e ciornă sau validată — încercarea de editare directă pe o notă validată e refuzată de aplicație.

## Ce face iConta.eu

Nu există o funcție separată de „mutare a sumei" între conturi. Cât timp nota e ciornă, contul greșit se înlocuiește direct pe linia notei. Odată validată, corecția se face exclusiv printr-o notă nouă de stornare, care scoate suma de pe contul greșit și o înregistrează pe contul corect, conform mecanismului de stornare în roșu/negru din reglementările contabile.

[iConta.eu](/)
