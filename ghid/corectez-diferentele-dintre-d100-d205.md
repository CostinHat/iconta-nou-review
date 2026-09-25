---
title: "Cum corectez diferențele dintre D100 și D205?"
description: "Ce prevede legea pentru situația în care sumele din D100 și D205 nu se potrivesc, și de ce corectarea fiecărei declarații e un proces separat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez diferențele dintre D100 și D205?

D100 și D205 pot avea o legătură economică — de exemplu, impozitul pe dividende reținut la sursă apare declarat lunar/trimestrial în D100, iar apoi raportat anual, pe fiecare beneficiar, în D205. Dar sunt două declarații cu regim juridic diferit, iar o diferență între ele nu se „repară" printr-un singur formular comun.

## Temeiul legal

::: ghid-temei
„5.2. Declarația rectificativă se întocmește pe tipuri de venit și va cuprinde numai pozițiile corectate, declarate eronat în declarația inițială, sau pozițiile care, în mod eronat, nu au fost cuprinse în declarația inițială."
— instrucțiuni de completare a formularului 205 (sursă: anaf_surse/opanaf_179_2022_d205_d207_baza.txt)
:::

- Corecția D205 nu e o „retransmitere" a întregii declarații, ci se limitează la pozițiile efectiv greșite sau lipsă — util de reținut dacă diferența față de D100 vine dintr-o singură poziție omisă, nu din tot formularul.
- Regimul de corecție al celor două declarații diferă structural: D100 e o declarație de impunere, supusă termenului de prescripție (CPF art. 105 alin. 1), în timp ce D205 e informativă și „poate fi corectată [...] indiferent de perioada la care se referă" (CPF art. 105 alin. 2).
- Ambele corecții se raportează, ca temei, la același text de bază: rectificarea D205 se face „în condițiile art. 105 și 170" din Codul de procedură fiscală, deci diferența de regim vine chiar din interiorul aceluiași articol, nu din acte separate.

## Ce se greșește în practică

- Se pornește de la premisa că o corecție D100 „trage automat" corecția corespunzătoare în D205, sau invers — nu există o asemenea legătură automată prevăzută de lege.
- Se identifică diferența, dar se corectează greșit sursa — de exemplu se rectifică D205 pentru o sumă care de fapt a fost declarată greșit în D100, situație în care corecția corectă e prin formularul 710, nu prin D205.
- Se transmite o rectificativă D205 completă, cu toate pozițiile, deși regula cere doar pozițiile corectate sau omise.

## Ce face iConta.eu

Pentru diferențele care provin dintr-o eroare pe D100 (coduri de obligație 121 sau 103), corecția se face prin formularul 710, generat și validat de iConta.eu conform funcționalității descrise în acest ghid pentru declarația rectificativă. Pentru diferențele care provin din D205, corecția se face din ecranul propriu al declarației 205, cu marcajul ei de rectificativă — D205 nu e generată din codurile de obligație acoperite de D710 și nu are, în cod, nicio legătură automată cu acesta. iConta.eu **nu compară automat** sumele din D100 cu cele din D205 și nu semnalează diferențele dintre ele; identificarea diferenței rămâne, la acest moment, o verificare manuală a contabilului, care apoi alege formularul potrivit — 710 pentru D100, sau rectificativa proprie pentru D205 — în funcție de unde se află eroarea reală.

[iConta.eu](/)
