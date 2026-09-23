---
title: 'Micro și sponsorizarea: cum se deduce din impozit'
description: Nu se mai deduce — facilitatea prin care micro-urile scădeau sponsorizarea din impozitul pe venit a fost abrogată de la 1 ianuarie 2024; cât timp a fost activă (01.04.2019–31.12.2023), limita era 20% din impozitul micro datorat pe trimestrul în care s-a înregistrat cheltuiala.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Micro și sponsorizarea: cum se deduce din impozit

Pentru o microîntreprindere, în 2026, sponsorizarea **nu se mai deduce din impozit sub nicio formă** — mecanismul care permitea asta a fost abrogat de la 1 ianuarie 2024. Mai jos explicăm cum funcționa mecanismul cât timp a fost în vigoare, util mai ales dacă verificați sau corectați o perioadă din trecut, și de ce în prezent nu se mai aplică.

## Temeiul legal

::: ghid-temei
„Microîntreprinderile care efectuează sponsorizări, potrivit prevederilor Legii nr. 32/1994, cu modificările și completările ulterioare, pentru susținerea entităților nonprofit și a unităților de cult, care la data încheierii contractului sunt înscrise în Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale potrivit art. 25 alin. (4^1), precum și microîntreprinderile care acordă burse elevilor școlarizați în învățământul profesional-dual... scad sumele aferente din impozitul pe veniturile microîntreprinderilor până la nivelul valorii reprezentând 20% din impozitul pe veniturile microîntreprinderilor datorat pentru trimestrul în care au înregistrat cheltuielile respective.”

— *Codul fiscal, art. 56 alin. (1^1), formă abrogată de la 01.01.2024.*

„(1^1) Abrogat. (la 01-01-2024 ... de ORDONANȚA DE URGENȚĂ nr. 115 din 14 decembrie 2023...)”
:::

## Cum funcționa deducerea (până la 31.12.2023)

1. Se calcula limita ca **20% din impozitul pe veniturile microîntreprinderilor datorat pentru trimestrul** în care fusese înregistrată cheltuiala de sponsorizare — nu un procent din cifra de afaceri (spre deosebire de regula de la impozitul pe profit) și nu raportat la un impozit anual.
2. Suma efectiv scăzută era minimul dintre sponsorizarea acordată și această limită trimestrială.
3. Condiția de fond: beneficiarul trebuia să fie o entitate nonprofit sau o unitate de cult **înscrisă în Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale**, la data încheierii contractului.

## Ce se greșește în practică

- Se aplică, din obișnuință, regula veche pentru o sponsorizare din 2024, 2025 sau 2026 — facilitatea nu mai există, indiferent de sumă sau de beneficiar.
- Se confundă limita micro (20% din impozitul micro trimestrial) cu cea de la impozitul pe profit (minimul dintre 0,75% din cifra de afaceri și 20% din impozitul pe profit) — sunt mecanisme diferite, aplicabile unor regimuri fiscale diferite.
- Se calculează limita raportat la un impozit micro anual, în loc de cel al trimestrului în care s-a înregistrat cheltuiala.
- Se ignoră condiția de înscriere a beneficiarului în Registrul ANAF, tratând orice ONG ca eligibil automat.

## Ce face iConta.eu

Funcția `credit_sponsorizare(cifra_afaceri, impozit_profit, sponsorizari_efectuate, tip_impozit="micro", beneficiar_in_registru=True, la_data=None)` din `core/sponsorizari.py` calculează, doar pentru `la_data` în intervalul 01.04.2019–31.12.2023, `plafon = 20% × impozit_profit` (unde parametrul reprezintă, pentru ramura micro, impozitul micro datorat pe trimestru, nu unul anual) și `credit = min(sponsorizari_efectuate, plafon)`. În afara acestui interval — inclusiv pentru 2026 — motorul returnează credit 0, cu o notă explicită că facilitatea nu se mai aplică. Sponsorizarea se contabilizează în continuare normal (`6582 = 401` la constituire, `6582 = 5121` la plată directă), doar că nu mai reduce impozitul datorat.

[iConta.eu](/)
