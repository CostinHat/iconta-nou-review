---
title: Scutirea de impozit pentru salariații din construcții
description: Registrul complet de cote și facilități verificat pentru acest ghid (period-aware, valabil pentru 2026) nu conține nicio facilitate de scutire de impozit specifică sectorului construcțiilor. Nu presupunem că e neschimbată — raportăm exact ce arată dosarul.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Scutirea de impozit pentru salariații din construcții

Sectorul construcțiilor a avut, în anii anteriori, un regim fiscal special pentru salariați (scutire de impozit pe venit, cotă CAS redusă, prag propriu pentru salariul minim). Acest ghid verifică ce arată, concret, dosarul de cercetare disponibil pentru 2026 — și răspunsul onest e că **nu confirmă existența unei asemenea facilități active**.

## Temeiul legal

::: ghid-temei
Cotele standard, confirmate în registrul verificat, pentru orice salariat fără un regim special: CAS 25% — Codul fiscal, art.138 lit.a); CASS 10% — art.156; impozit pe venit 10% — art.64 alin.(1)/art.78. Funcționalitatea de calcul salarial (cod F080) are ca temei declarat, în lista funcționalităților aplicației, și OUG 34/2024 — act care a reformat regimul facilităților fiscale sectoriale — dar textul acestui act nu a fost reprodus verbatim în dosarul de cercetare.
:::

**De semnalat onest**: dosarul verificat pentru acest ghid conține registrul complet și exhaustiv de cote și facilități (`core/common.py`, dict `COTE`), „period-aware" — adică fiecare cotă sau facilitate are o fereastră de valabilitate explicită, cu temei legal atașat. Registrul conține, pentru 2026: cotele standard (CAS, CASS, impozit, CAM), cele două valori ale salariului minim, facilitatea generică „salariul minim neimpozabil" (300 lei, apoi 200 lei) și plafonul tichetelor de masă. **Nu conține nicio intrare pentru o facilitate distinctă de scutire de impozit pentru sectorul construcțiilor.** Funcționalitatea F080 are ca temei declarat, în lista de funcționalități a aplicației, și OUG 34/2024 — act care a modificat regimul facilităților fiscale sectoriale — dar dosarul nu conține textul acelui act, nici confirmarea explicită a datei sau condițiilor în care o eventuală facilitate pentru construcții a fost restrânsă sau eliminată. Nu inventăm acest detaliu: dacă aveți nevoie de un răspuns definitiv despre statutul facilității pentru construcții în 2026, verificați direct OUG 34/2024 și actele care l-au modificat ulterior, sau consultați un contabil.

## Ce se greșește în practică

- Se presupune, din obișnuință sau din informații mai vechi, că salariații din construcții beneficiază automat de scutire de impozit pe venit în 2026, fără o verificare a stadiului actual al reglementării.
- Se aplică o scutire de impozit „din oficiu" în calculul salarial, fără să fie confirmată o bază legală activă pentru anul și luna respectivă.

## Ce face iConta.eu

Motorul de calcul salarial verificat pentru acest ghid (`core/salarizare.py`, registrul `core.common.COTE`) nu aplică, pentru 2026, nicio facilitate de scutire de impozit distinctă pentru sectorul construcțiilor — calculul urmează cotele standard (CAS 25%, CASS 10%, impozit 10%), la fel ca pentru orice alt salariat, exceptând facilitatea generică „salariul minim neimpozabil" (disponibilă oricărui angajat încadrat la salariul minim, indiferent de sector, cu condițiile ei proprii). Dacă situația dumneavoastră implică un regim sectorial specific, verificați direct statutul actual al reglementării — acest dosar nu îl confirmă.

[iConta.eu](/)
