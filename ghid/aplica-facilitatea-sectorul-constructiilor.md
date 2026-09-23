---
title: Cum se aplică facilitatea pentru sectorul construcțiilor
description: Din verificarea directă a registrului de cote și facilități folosit de motorul de calcul salarial pentru 2026, nu există o facilitate sectorială pentru construcții implementată — răspunsul onest e că nu putem detalia condiții de aplicare pentru ceva ce dosarul nu confirmă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se aplică facilitatea pentru sectorul construcțiilor

Întrebarea presupune existența unei facilități fiscale active pentru sectorul construcțiilor în 2026 (scutire de impozit, cotă CAS redusă, prag propriu de salariu minim). Verificând registrul complet și exhaustiv de cote și facilități folosit efectiv de motorul de calcul salarial, răspunsul onest e că **nu găsim o asemenea facilitate implementată pentru 2026**.

## Temeiul legal

::: ghid-temei
Funcționalitatea de calcul salarial (cod F080) declară, printre temeiurile ei, și OUG 34/2024 — actul care a reformat regimul facilităților fiscale sectoriale (construcții, agricultură, industrie alimentară) — dar textul acestui act nu a fost reprodus verbatim în dosarul de cercetare folosit la acest ghid.
:::

## Ce arată, concret, verificarea

- Registrul de cote și facilități (`core/common.py`, dict `COTE`) e „period-aware" — fiecare cotă sau facilitate are o fereastră de valabilitate explicită și un temei legal atașat, exact ca pentru salariul minim sau pentru facilitatea generică „salariul minim neimpozabil".
- Pentru 2026, registrul conține: cotele standard (CAS 25%, CASS 10%, impozit 10%, CAM 2,25%), cele două valori ale salariului minim (4.050 și 4.325 lei), facilitatea generică „salariul minim neimpozabil" (300 lei, apoi 200 lei, cu plafoane 4.300/4.600 lei) și plafonul tichetelor de masă.
- **Nu conține nicio intrare separată pentru o facilitate sectorială construcții.**

Această absență e un indiciu solid că, la data mirror-ului folosit pentru acest dosar (17.09.2026), aplicația nu mai calculează o asemenea facilitate — consecventă cu faptul că OUG 34/2024, menționat ca temei general al funcționalității, e cunoscut ca actul care a restrâns regimurile fiscale sectoriale. Dar dosarul nu conține citatul exact din acel act, deci nu putem preciza condițiile, data exactă sau mecanismul restrângerii — nu inventăm acest detaliu.

## Ce se greșește în practică

- Se presupune că facilitatea pentru construcții funcționează la fel ca înainte de reforma OUG 34/2024, fără o verificare a stadiului actual.
- Se aplică manual o scutire sau o cotă redusă în calculul salarial, fără o confirmare a bazei legale active pentru luna respectivă.

## Ce face iConta.eu

Motorul de calcul salarial verificat pentru acest ghid nu aplică, pentru 2026, o facilitate distinctă pentru sectorul construcțiilor — folosește cotele și facilitățile standard din registrul verificat, aceleași pentru orice angajator, indiferent de sector. Dacă situația dumneavoastră ar trebui să beneficieze de un regim sectorial specific, recomandăm verificarea directă a stadiului actual al reglementării (OUG 34/2024 și actele ulterioare) — acest dosar nu îl confirmă.

[iConta.eu](/)
