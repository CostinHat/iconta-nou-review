---
title: "Un PFA cu cod special de TVA trebuie să depună D390?"
description: "Obligația de depunere a declarației recapitulative D390 pentru persoanele înregistrate cu codul special de TVA (art. 317 din Codul fiscal), inclusiv pentru achiziții de servicii intracomunitare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Un PFA cu cod special de TVA trebuie să depună D390?

Da — și obligația nu apare doar dacă PFA-ul prestează servicii către clienți din UE, ci și atunci când doar primește servicii de la un prestator stabilit în alt stat membru, pentru care datorează taxa în România.

## Temeiul legal

::: ghid-temei
„(1) Orice persoană impozabilă înregistrată în scopuri de TVA conform art. 316 sau 317 trebuie să întocmească și să depună la organele fiscale competente o declarație recapitulativă în care menționează: [...]
e) achizițiile de servicii prevăzute la art. 278 alin. (2), efectuate de persoane impozabile din România care au obligația plății taxei conform art. 307 alin. (2), pentru care exigibilitatea de taxă a luat naștere în luna calendaristică respectivă, de la persoane impozabile nestabilite în România, dar stabilite în Uniunea Europeană."
— Legea 227/2015 (Codul fiscal), art. 325 alin. (1), partea introductivă și lit. e) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„(1) Are obligația să solicite înregistrarea în scopuri de TVA, conform prezentului articol: [...]
c) persoana impozabilă care își are stabilit sediul activității economice în România și persoana impozabilă care aplică regimul special de scutire prevăzut la art. 310^2, care nu sunt înregistrate și nu au obligația să se înregistreze conform art. 316 [...] dacă primesc de la un prestator, persoană impozabilă stabilită în alt stat membru, servicii pentru care sunt obligate la plata taxei în România conform art. 307 alin. (2), înaintea primirii serviciilor respective."
— Legea 227/2015, art. 317 alin. (1) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul, pentru un PFA neplătitor de TVA în regimul normal (aplică scutirea de la art. 310^2), dar cu cod special de TVA obținut conform art. 317:

- Codul special (numit uzual „cod T") se obține exact pentru situația în care PFA-ul **primește** un serviciu de la un prestator stabilit în alt stat membru UE, pentru care taxa se datorează în România prin taxare inversă (art. 307 alin. (2)) — art. 317 alin. (1) lit. c).
- Odată obținut acest cod, art. 325 alin. (1), partea introductivă, e explicit: **orice persoană impozabilă înregistrată conform art. 316 sau 317** trebuie să depună declarația recapitulativă — nu doar cele înregistrate normal conform art. 316.
- Lit. e) confirmă direct scenariul PFA-ului: **achizițiile de servicii pentru care se datorează taxa prin taxare inversă, de la prestatori stabiliți în UE**, se raportează în D390 pentru luna în care ia naștere exigibilitatea taxei.
- Obligația de depunere D390 nu depinde de existența unor livrări sau prestări proprii către UE — simpla primire a unui serviciu intracomunitar taxabil prin reverse charge, odată înregistrat codul special, declanșează raportarea.

## Ce se greșește în practică

- Se presupune că un PFA cu cod special de TVA, neplătitor de TVA în regimul normal, e scutit și de obligațiile declarative — art. 325 alin. (1) leagă obligația D390 de înregistrarea conform art. 317, nu de statutul de plătitor „complet" de TVA.
- Se depune D390 doar pentru lunile în care PFA-ul emite facturi către clienți UE, omițând lunile în care doar a primit servicii de la prestatori UE, deși lit. e) acoperă explicit și acest sens al fluxului.
- Se confundă obligația de D390 cu cea de D301 (decontul special de TVA pentru operațiuni ocazionale) — cele două declarații au funcții diferite și pot fi ambele necesare pentru aceeași operațiune.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **generează declarația D390** (`core/d390.py`), cu cele șase tipuri oficiale de operațiune din OPANAF 705/2020, inclusiv tipul **„S" — achiziții intracomunitare de servicii**, exact categoria relevantă pentru un PFA cu cod special care primește servicii de la un prestator UE. Aplicația clasifică însă automat din facturi doar operațiunile cu bunuri (factură emisă → tip L, factură primită → tip A); operațiunile de tip P/S (prestări/achiziții de servicii) și T/R (triangulație, agricultori) **rămân de clasificare manuală a contabilului**, prin mecanismul intern de reclasificare — aplicația nu detectează singură, din conținutul facturii, că o achiziție reprezintă un serviciu supus taxării inverse conform art. 307 alin. (2).

[iConta.eu](/)
