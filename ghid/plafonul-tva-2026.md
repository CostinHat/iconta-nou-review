---
title: "Care este plafonul de TVA în 2026?"
description: "Plafonul de scutire de TVA pentru întreprinderile mici, valabil în 2026: 395.000 lei, potrivit art. 310 din Codul fiscal, așa cum a fost modificat din septembrie 2025."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Care este plafonul de TVA în 2026?

Plafonul de scutire de TVA aplicabil întreprinderilor mici a fost modificat în cursul anului 2025, de la 300.000 lei la 395.000 lei, iar valoarea rămâne cea de referință și în 2026.

## Temeiul legal

::: ghid-temei
„Persoana impozabilă stabilită în România conform art. 266 alin. (2) lit. a), a cărei cifră de afaceri anuală, declarată sau realizată, nu depășește plafonul de 395.000 lei, poate aplica scutirea de taxă, denumită în continuare regim special de scutire, pentru operațiunile prevăzute la art. 268 alin. (1), cu excepția livrărilor intracomunitare de mijloace de transport noi, scutite conform art. 294 alin. (2) lit. b)."
— Legea nr. 227/2015 (Codul fiscal), art. 310 alin. (1), modificat prin Ordonanța nr. 22/2025 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă concret plafonul pentru 2026:

- Regimul special de scutire (fără TVA, dar și fără drept de deducere) se poate aplica atât timp cât cifra de afaceri anuală **declarată sau realizată** nu depășește 395.000 lei.
- Depășirea plafonului obligă la înregistrarea în scopuri de TVA, cu aplicarea regimului normal de taxare începând cu operațiunea care conduce la depășire.
- Plafonul anterior, de 300.000 lei, a rămas relevant doar pentru situațiile tranzitorii din 2025 (persoane care au depășit 300.000 lei în august 2025, dar nu și 395.000 lei), reglementate separat prin dispoziții tranzitorii ale aceleiași ordonanțe.

## Ce se greșește în practică

- Se folosește încă pragul vechi de 300.000 lei ca plafon de referință pentru 2026, deși acesta a fost înlocuit de 395.000 lei începând din septembrie 2025.
- Se calculează plafonul pe an calendaristic fix, ignorând regula specială pentru persoanele impozabile nou-înființate, pentru care plafonul de scutire se aplică proporțional de la începutul activității.
- Se presupune că depășirea plafonului înseamnă automat pierderea retroactivă a scutirii pentru tot anul — de fapt, regimul normal de taxare se aplică doar de la tranzacția care determină depășirea.

## Ce face iConta.eu

Verificat în cod: modulele `core/cota_tva_incasare.py`, `core/perioada_fiscala_tva.py` și `core/migrare_platitor_tva_anaf.py` gestionează perioada fiscală, cota TVA la încasare și statutul de plătitor de TVA confirmat de la ANAF (snapshot separat de valoarea introdusă manual), dar aplicația nu are, la acest moment, o alertă automată de monitorizare a apropierii cifrei de afaceri de plafonul de 395.000 lei — urmărirea plafonului rămâne, deocamdată, în responsabilitatea contabilului.

[iConta.eu](/)
