---
title: "Tichetele culturale 2026: tratament fiscal pentru angajator"
description: "Plafoanele legale ale tichetelor culturale acordate angajaților — sumă maximă lunară, valoare per tichet și cerințele de valabilitate, conform Legii 165/2018."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Tichetele culturale 2026: tratament fiscal pentru angajator

Tichetele culturale sunt unul dintre cele cinci tipuri de bilete de valoare pe care le poate acorda un angajator, alături de tichetele de masă, tichetele cadou, tichetele de creșă și voucherele de vacanță. Regimul lor are plafoane proprii, distincte de celelalte tipuri de tichete.

## Temeiul legal

::: ghid-temei
„Tichetele culturale sunt bilete de valoare acordate angajaților, lunar sau ocazional, pentru achitarea contravalorii de bunuri și servicii culturale. [...] Nivelul maxim al sumelor acordate sub forma tichetelor culturale nu poate depăși suma de 150 de lei pentru tichetele acordate lunar, respectiv suma de 300 de lei/eveniment, pentru cele acordate ocazional. Valoarea nominală a unui tichet cultural este de 10 lei sau un multiplu de 10, dar nu mai mare de 50 lei."
— Legea 165/2018 privind acordarea biletelor de valoare, art. 21 alin. (1) și art. 22 alin. (1), (2) (sursă: anaf_surse/legea_165_2018_consolidat.txt)
:::

Ce trebuie reținut pentru angajator:

- Tichetele culturale se pot acorda **lunar** (plafon 150 lei/lună) sau **ocazional**, legat de un eveniment (plafon 300 lei/eveniment) — cele două plafoane nu se cumulează arbitrar, ci corespund unor moduri diferite de acordare.
- Valoarea nominală a unui tichet e de 10 lei sau un multiplu de 10, dar nu poate depăși 50 lei — deci suma acordată se compune din tichete cu valori standardizate, nu orice sumă rotundă.
- Fiecare tichet cultural, indiferent de suport (electronic sau alt tip de stocare), trebuie să poarte mențiuni obligatorii, inclusiv numele, prenumele și codul numeric personal ale salariatului îndreptățit să îl utilizeze — tichetul e nominal, nu transmisibil liber.
- Tichetele culturale servesc la achitarea contravalorii de bunuri și servicii culturale (definite de lege), nu la orice tip de cheltuială a angajatului.

## Ce se greșește în practică

- Se confundă plafonul lunar (150 lei) cu cel ocazional (300 lei/eveniment) și se acordă suma mai mare în regim lunar, depășind plafonul legal pentru acest tip de acordare.
- Se emit tichete cu valoare nominală „rotunjită" arbitrar (de exemplu 25 lei), care nu respectă cerința de multiplu de 10 lei, cu maximul de 50 lei per tichet.
- Se omit mențiunile obligatorii de identificare a salariatului pe tichet, ceea ce poate invalida caracterul nominal al beneficiului la un control.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu emite tichete culturale** — furnizarea lor rămâne prin operatorii autorizați. Aplicația are însă un câmp dedicat (`tichet_cultural`) pentru suma introdusă manual de contabil, pe baza căreia calculează automat tratamentul fiscal corect: impozit 10% pe valoarea nominală integrală, fără CAS, CASS sau CAM (`core/salarizare.py`, `core/d112.py`). Aplicația **nu verifică automat** dacă suma introdusă respectă plafoanele legale (150 lei/lună sau 300 lei/eveniment) sau valoarea nominală standardizată a tichetului — încadrarea în plafoanele Legii 165/2018 rămâne responsabilitatea contabilului la introducerea sumei.

[iConta.eu](/)
