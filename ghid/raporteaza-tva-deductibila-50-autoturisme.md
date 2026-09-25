---
title: "Cum se raportează TVA deductibilă 50% pentru autoturisme în D406?"
description: "Temeiul legal al limitării la 50% a dreptului de deducere a TVA pentru vehicule și modul în care fișierul SAF-T (D406) trebuie să reflecte această limitare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează TVA deductibilă 50% pentru autoturisme în D406?

Firmele care dețin autoturisme folosite și în scop personal cunosc regula: TVA aferentă cumpărării, leasingului sau cheltuielilor de întreținere se deduce doar în proporție de 50%. Întrebarea care apare la raportarea SAF-T este cum se reflectă această pro-rata în structura fișierului D406.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile art. 297 se limitează la 50% dreptul de deducere a taxei aferente cumpărării, achiziției intracomunitare, importului, închirierii sau leasingului de vehicule rutiere motorizate și a taxei aferente cheltuielilor legate de vehiculele aflate în proprietatea sau în folosința persoanei impozabile, în cazul în care vehiculele nu sunt utilizate exclusiv în scopul activității economice."
— Legea nr. 227/2015 (Codul fiscal), art. 298 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă asta pentru raportarea SAF-T:

- Limitarea de 50% **nu se aplică automat tuturor vehiculelor**: art. 298 alin. (2) și (3) exceptează vehiculele peste 3.500 kg sau cu peste 9 scaune, precum și cele folosite exclusiv pentru servicii de urgență, pază, curierat, vânzări/achiziții, taximetrie, școli de șoferi, închiriere/leasing sau ca marfă — pentru acestea se aplică deducerea integrală, conform regulilor generale.
- Structura oficială SAF-T (schema ANAF) prevede coduri de taxă distincte pentru achiziții: coduri `301xxx`-`309xxx` pentru achizițiile cu deducere integrală și coduri `320xxx` pentru achizițiile cu deducere limitată pro-rata (cum e cazul celor 50% pentru autoturisme), fiecare cu propriul `BaseRate` — fracția de deducere efectivă, între 0,0000 și 1,0000 (0,5000 pentru cazul de 50%).
- Un cod de achiziție cu deducere de 50% trebuie să poarte `BaseRate = 0.5`, nu procentul „100" sau „50" ca număr întreg — schema oficială cere explicit fracția.

## Ce se greșește în practică

- Se raportează întreaga sumă a TVA deductibile din factura de achiziție a autoturismului, fără a marca separat partea nedeductibilă (50%) — riscă respingerea la validare sau, mai grav, o deducere incorectă la controlul încrucișat cu D300.
- Se folosește un `BaseRate` exprimat ca procent întreg (de exemplu „50") în loc de fracție zecimală („0.5") — schema oficială respinge valorile în afara intervalului [0, 1].
- Se presupune că toate vehiculele firmei intră automat sub limitare, fără verificarea excepțiilor de la art. 298 alin. (3) (vehicule de intervenție, taxi, agenți de vânzări etc.), care au drept de deducere integrală.

## Ce face iConta.eu

La data acestui ghid, motorul de generare D406 din iConta.eu (`core/d406.py`) emite coduri de taxă atât pentru livrări (seria `310xxx`, cu `BaseRate = 1`), cât și pentru achiziții — dar pentru achiziții folosește deocamdată un cod generic de deductibilitate (`300501`, respectiv `300101` pentru taxare inversă/cotă 0), nu codurile fine din seria `320xxx` pentru deducere limitată pro-rata (cazul autoturismelor la 50%). Această limitare e semnalată explicit în cod, ca datorie deschisă („TaxCode achiziții pe deductibilitate reală — acum grosier 300501"), nu ascunsă tăcut. Până la acoperirea ei, achizițiile cu deducere de 50% pentru autoturisme trebuie verificate și, dacă e cazul, ajustate manual înainte de depunerea D406.

[iConta.eu](/)
