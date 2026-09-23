---
title: Cota CAS redusă pentru angajații din construcții 2026
description: Registrul de cote verificat pentru 2026 conține o singură cotă CAS standard (25%), fără o cotă redusă separată pentru sectorul construcțiilor. Nu presupunem că facilitatea a rămas neschimbată — raportăm exact ce confirmă dosarul.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cota CAS redusă pentru angajații din construcții 2026

Construcțiile au avut, în trecut, o cotă CAS redusă pentru angajați (spre deosebire de cota standard de 25%). Verificând registrul de cote folosit efectiv de motorul de calcul salarial pentru 2026, acest ghid raportează onest: **nu există, în acest registru, o cotă CAS distinctă pentru sectorul construcțiilor**.

## Temeiul legal

::: ghid-temei
Cota CAS standard, confirmată ca singura activă în registrul verificat pentru 2026, fără excepție sectorială: 25%, de la 2018-01-01 — Codul fiscal, art.138 lit.a).
:::

**De semnalat onest**: registrul de cote (`core/common.py`, dict `COTE`, „period-aware") conține o singură intrare pentru cota CAS — 25%, activă din 2018-01-01, fără fereastră de excepție și fără o a doua cotă redusă asociată vreunui sector. Funcționalitatea F080 declară, printre temeiurile ei generale, și OUG 34/2024 (actul care a reformat facilitățile fiscale sectoriale), dar dosarul de cercetare nu reproduce textul acelui act și nu confirmă dacă o eventuală cotă redusă pentru construcții a fost eliminată, restrânsă sau condiționată altfel. Nu presupunem că cota redusă a rămas neschimbată din ani anteriori — absența ei din registrul verificat e un indiciu clar că aplicația nu o mai aplică la data acestui dosar (mirror din 17.09.2026), dar fără un citat exact din actul de modificare, nu putem preciza data sau mecanismul exact al schimbării.

## Ce se greșește în practică

- Se aplică din obișnuință o cotă CAS redusă pentru un angajat din construcții, bazându-se pe o regulă valabilă în anii anteriori, fără verificarea stadiului actual.
- Se calculează greșit CAS-ul angajatorului (contribuția asiguratorie pentru muncă) pornind de la premisa unei cote reduse care nu mai e confirmată.

## Ce face iConta.eu

Motorul de calcul (`core/salarizare.py`) aplică, pentru orice salariat, cota CAS din registrul verificat — 25%, fără excepție sectorială pentru construcții în 2026. Dacă un angajator din construcții crede că ar trebui să beneficieze de o cotă redusă, recomandăm verificarea directă a stadiului actual al reglementării (OUG 34/2024 și actele ulterioare care l-au modificat) — acest dosar nu confirmă o asemenea facilitate activă.

[iConta.eu](/)
