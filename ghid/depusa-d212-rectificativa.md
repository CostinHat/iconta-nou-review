---
title: "Când trebuie depusă o D212 rectificativă?"
description: "Nu există un termen fix pentru rectificativă — se depune oricând în termenul de prescripție de 5 ani, de îndată ce se descoperă o eroare, cu o excepție: după anularea rezervei verificării ulterioare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când trebuie depusă o D212 rectificativă?

Spre deosebire de declarația inițială, care are un termen legal fix (25 mai), rectificativa nu are un termen-limită propriu — regula e „oricând, cât mai devreme posibil, în interiorul termenului de prescripție".

## Temeiul legal

::: ghid-temei
„Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale."
— Legea 207/2015 (Codul de procedură fiscală), art. 105 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„Declarația de impunere nu poate fi depusă și nu poate fi corectată după anularea rezervei verificării ulterioare."
— Legea 207/2015, art. 105 alin. (5) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă din combinația regulii și a excepției:

- Momentul potrivit pentru rectificativă e imediat ce se descoperă eroarea — legea nu impune să aștepți un termen anume, dar nici nu-ți permite să corectezi oricând, la infinit.
- Limita generală e termenul de prescripție a dreptului organului fiscal de a stabili creanțe fiscale — de regulă 5 ani de la 1 iulie a anului următor celui pentru care se datorează obligația (art. 110).
- Excepția de la art. 105 alin. (5): odată ce ANAF a anulat rezerva verificării ulterioare pentru perioada respectivă (de regulă în urma unei inspecții fiscale), declarația nu mai poate fi corectată — cu cele două excepții limitate de la alin. (6): o condiție legală care impune corectarea bazei de impozitare, sau o hotărâre judecătorească definitivă.
- Dacă bonificația de 3% (pentru veniturile 2025) a fost omisă la depunerea inițială, ea poate fi recuperată exclusiv printr-o rectificativă depusă până la 15 aprilie 2026 — un termen special, mai strict decât regula generală.

## Ce se greșește în practică

- Se amână corectarea unei erori descoperite, considerând-o „de mică importanță" — fără o rectificativă, obligația declarată greșit rămâne titlu de creanță exigibil la valoarea eronată.
- Se depune o rectificativă după ce ANAF a anulat rezerva verificării ulterioare pe acea perioadă, fără să se verifice dacă situația se încadrează în una din cele două excepții — riscul e respingerea rectificativei.
- Se presupune că orice rectificativă are un termen de 25 mai, ca și declarația inițială — regula pentru rectificativă e alta: perioada de prescripție, nu o dată fixă anuală.

## Ce face iConta.eu

Generatorul D212 al iConta.eu (`core/d212.py`) permite marcarea declarației ca rectificativă prin câmpurile `rectif1`/`rectif2` de pe rădăcina documentului, respectând structura oficială. Aplicația nu urmărește automat perioadele de prescripție pe fiecare an fiscal declarat și nu semnalează dacă rezerva verificării ulterioare a fost anulată pentru o anumită perioadă — aceste verificări, care țin de istoricul relației contribuabilului cu ANAF, rămân în sarcina contabilului.

[iConta.eu](/)
