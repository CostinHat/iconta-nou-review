---
title: Cum se aplică scutirea de impozit pentru angajații IT
description: Din verificarea directă a registrului de cote și facilități folosit de motorul de calcul salarial pentru 2026, nu există o scutire de impozit pentru sectorul IT implementată — răspunsul onest e că nu putem detalia condiții pentru ceva ce dosarul nu confirmă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se aplică scutirea de impozit pentru angajații IT

Întrebarea presupune existența unei scutiri de impozit pe venit pentru angajații IT, activă în 2026. Verificând registrul complet de cote și facilități folosit efectiv de motorul de calcul salarial, răspunsul onest e că **nu găsim o asemenea facilitate implementată pentru 2026**.

## Temeiul legal

::: ghid-temei
Funcționalitatea de calcul salarial (cod F080) declară, printre temeiurile ei, și OUG 34/2024 — actul care a reformat regimul facilităților fiscale sectoriale (construcții, agricultură, industrie alimentară, iar istoric și IT) — dar textul acestui act nu a fost reprodus verbatim în dosarul de cercetare folosit la acest ghid.
:::

## Ce arată, concret, verificarea

Registrul de cote și facilități (`core/common.py`, dict `COTE`) e „period-aware" — fiecare cotă sau facilitate activă are o fereastră de valabilitate explicită și un temei legal atașat, exact ca la salariul minim sau la facilitatea generică „salariul minim neimpozabil". Pentru 2026, registrul conține doar: cotele standard (CAS, CASS, impozit, CAM), cele două valori ale salariului minim, facilitatea generică „salariul minim neimpozabil" și plafonul tichetelor de masă — **nicio intrare pentru o scutire IT**.

Absența acestei facilități din registrul verificat e un indiciu solid că, la data mirror-ului folosit pentru acest dosar (17.09.2026), aplicația nu mai calculează o asemenea scutire — consecventă cu reforma declarată prin OUG 34/2024. Dar dosarul nu conține citatul exact din acel act, deci nu putem preciza condițiile, data exactă sau mecanismul restrângerii — nu inventăm acest detaliu.

## Ce se greșește în practică

- Se presupune că scutirea IT funcționează la fel ca în anii dinaintea reformei OUG 34/2024, fără o verificare a stadiului actual.
- Se calculează manual impozitul ca fiind zero pentru un angajat IT, fără o confirmare a bazei legale active pentru luna respectivă.

## Ce face iConta.eu

Motorul de calcul salarial verificat pentru acest ghid nu aplică, pentru 2026, o scutire distinctă pentru sectorul IT — folosește cotele standard din registrul verificat, aceleași pentru orice angajator, indiferent de sector. Dacă situația dumneavoastră ar trebui să beneficieze de un regim IT specific, recomandăm verificarea directă a stadiului actual al reglementării (OUG 34/2024 și actele ulterioare) — acest dosar nu-l confirmă.

[iConta.eu](/)
