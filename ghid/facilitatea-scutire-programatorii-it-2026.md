---
title: Facilitatea de scutire pentru programatorii IT în 2026
description: Registrul complet de cote și facilități verificat pentru 2026 nu conține nicio facilitate specifică sectorului IT (programatori). Nu presupunem că e neschimbată față de anii trecuți — raportăm exact ce arată dosarul.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Facilitatea de scutire pentru programatorii IT în 2026

Sectorul IT a beneficiat, în anii anteriori, de o scutire de impozit pe venit pentru anumite funcții de programator, condiționată de tipul de activitate al angajatorului și de studii. Verificând registrul complet de cote și facilități folosit efectiv de motorul de calcul salarial pentru 2026, acest ghid raportează onest: **nu găsim o facilitate distinctă pentru sectorul IT activă**.

## Temeiul legal

::: ghid-temei
Funcționalitatea de calcul salarial (cod F080) declară, printre temeiurile ei, și OUG 34/2024 — actul care a reformat regimul facilităților fiscale sectoriale — dar textul acestui act nu a fost reprodus verbatim în dosarul de cercetare folosit la acest ghid. Cotele standard confirmate, aplicabile în absența unui regim special: impozit pe venit 10% — Codul fiscal, art.64 alin.(1)/art.78.
:::

**De semnalat onest**: registrul de cote și facilități (`core/common.py`, dict `COTE`, „period-aware") a fost verificat exhaustiv pentru acest dosar — conține, pentru 2026, cotele standard, cele două valori ale salariului minim, facilitatea generică „salariul minim neimpozabil" și plafonul tichetelor de masă. **Nu conține nicio intrare pentru o scutire de impozit specifică programatorilor sau sectorului IT.** Aceasta e consecventă cu faptul că funcționalitatea F080 declară OUG 34/2024 (actul de reformă a facilităților sectoriale) printre temeiurile ei generale — dar, fără textul acelui act reprodus în dosar, nu putem confirma data exactă sau mecanismul prin care facilitatea IT ar fi fost restrânsă sau eliminată. Nu inventăm acest detaliu — dacă aveți nevoie de un răspuns definitiv, verificați direct OUG 34/2024 și actele ulterioare care l-au modificat, sau consultați un contabil.

## Ce se greșește în practică

- Se presupune că scutirea de impozit pentru programatori funcționează în 2026 la fel ca înainte de reforma din 2024, fără o verificare a stadiului actual al reglementării.
- Se calculează impozitul pe venit ca fiind zero pentru un angajat IT, bazându-se pe o regulă mai veche, fără confirmarea unei baze legale active pentru luna respectivă.

## Ce face iConta.eu

Motorul de calcul salarial verificat pentru acest ghid (`core/salarizare.py`, registrul `core.common.COTE`) aplică, pentru 2026, impozitul standard de 10% pentru orice salariat, fără o scutire distinctă pentru sectorul IT — la fel ca pentru orice alt angajat, exceptând facilitatea generică „salariul minim neimpozabil" (disponibilă indiferent de sector, cu condițiile ei proprii). Dacă situația dumneavoastră ar trebui să beneficieze de un regim IT specific, recomandăm verificarea directă a stadiului actual al reglementării — acest dosar nu-l confirmă.

[iConta.eu](/)
