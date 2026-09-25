---
title: "Ce se schimbă în 2026 pentru firmele de construcții"
description: "Situația facilităților fiscale pentru sectorul construcțiilor la începutul lui 2026, după eliminarea scutirii de impozit pe venit și transformarea reducerii CAS în opțiune."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce se schimbă în 2026 pentru firmele de construcții

Sectorul construcțiilor a beneficiat ani la rând de un pachet de facilități fiscale pe salarii — scutire de impozit pe venit, cotă redusă de CAS, scutire (parțială) de CASS. Acest pachet a fost restrâns etapizat, iar în 2026 firmele de construcții operează deja sub regulile modificate în 2024-2025: scutirea de impozit pe venit a dispărut, iar reducerea de CAS a devenit opțională, nu automată.

## Temeiul legal

::: ghid-temei
„5. Abrogat."
— Legea nr. 227/2015 (Codul fiscal), art. 60 pct. 5, abrogat de la 01-01-2025 prin OUG nr. 156/2024 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Punctul 5 al art. 60 era temeiul scutirii de impozit pe venit pentru salariile din sectorul construcțiilor. Fiind abrogat de la 1 ianuarie 2025, scutirea nu mai există nici în 2026 — nu e o schimbare nouă a anului 2026, ci continuarea situației instaurate în 2025.

În paralel, regimul de contribuții sociale a fost și el rescris:

::: ghid-temei
„(1) Prin excepție de la prevederile art. 138^1 alin. (1) și (2), art. 138^2 alin. (1) și (2) și art. 138^4 alin. (1) și (2), persoanele fizice care realizează venituri din salarii și asimilate salariilor din domeniile respective **pot opta** pentru plata contribuției datorate la fondul de pensii administrat privat. (2) Opțiunea se depune în scris, la angajator [...]"
— Legea nr. 227/2015 (Codul fiscal), art. 138^5 „Prevederi specifice activității de creare de programe pentru calculator, sectorului construcții, sectorului agricol și industriei alimentare", introdus prin OUG nr. 115/2023 (sursă: anaf_surse/oug_115_2023_consolidat.txt)
:::

Ce înseamnă pentru 2026:

- Angajații din construcții **nu mai sunt scutiți de impozit pe venit** — salariile lor se impozitează după regulile generale.
- Reducerea cotei CAS cu punctele procentuale aferente pilonului II de pensii **nu mai e automată**, ci depinde de opțiunea scrisă a salariatului, depusă la angajator — dacă angajatul nu optează, se aplică cota standard de CAS.
- Nu am găsit, în sursele verificate, un act normativ intrat în vigoare special pentru anul 2026 care să modifice suplimentar acest regim — situația descrisă mai sus rămâne cadrul aplicabil la începutul lui 2026.

## Ce se greșește în practică

- Se presupune, din inerție, că salariile din construcții rămân scutite de impozit pe venit, deși scutirea (art. 60 pct. 5) a fost abrogată încă din 2025.
- Se aplică automat reducerea de CAS specifică sectorului, fără opțiunea scrisă depusă de salariat la angajator — de la introducerea art. 138^5, facilitatea nu mai e implicită.
- Se confundă facilitățile de CAS (opționale, art. 138^5) cu cele de impozit pe venit (abrogate integral) — cele două regimuri au avut, istoric, condiții și praguri diferite, iar tratarea lor ca un „pachet unic" duce la erori de calcul al salariului net.

## Ce face iConta.eu

Da — modulul de salarizare al iConta.eu (`core/salarizare.py`) tratează explicit acest subiect: documentația internă a funcției de calcul notează clar că facilitatea sectorială pentru construcții/agricultură/industrie alimentară (scutire de impozit conform fostului art. 60 pct. 5, CAS redus conform art. 138^1) **nu se aplică**, pentru că art. 60 pct. 5 și art. 60^1 au fost abrogate de la 1 ianuarie 2025 prin OUG nr. 156/2024. De aceea aplicația nu are o ramură separată de calcul după codul CAEN al angajatorului pentru aceste sectoare — orice salariat, indiferent de domeniu, este calculat cu cotele standard de impozit pe venit și CAS. Opțiunea individuală de reducere a CAS din art. 138^5 (OUG 115/2023), care depinde de o cerere scrisă a salariatului, nu apare implementată separat în modulul verificat.

[iConta.eu](/)
