---
title: "Cheltuieli mici de la casierie: cum le înregistrez"
description: "Plafoanele legale pentru plățile în numerar și pentru avansurile spre decontare, valabile pentru cheltuielile mărunte plătite din casierie."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cheltuieli mici de la casierie: cum le înregistrez

Cheltuielile mărunte plătite în numerar (birotică, combustibil, mese de protocol mici) trec, de regulă, prin casierie — fie direct din casa firmei, fie ca avans spre decontare acordat unui angajat. Ambele situații au plafoane legale precise, gândite să limiteze riscul de fragmentare a plăților în numerar.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile art. 1 alin. (1) se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: [...] e) plăți din avansuri spre decontare, în limita unui plafon zilnic de 5.000 lei, stabilit pentru fiecare persoană care a primit avansuri spre decontare."
— Legea 70/2015 pentru întărirea disciplinei financiare privind operațiunile de încasări și plăți în numerar, art. 3 alin. (1) lit. e), astfel cum a fost modificat prin OUG 115/2023 (sursă: anaf_surse/legea_70_2015_consolidat.html)
:::

Ce se aplică practic la cheltuielile mici din casierie:

- Fiecare persoană care a primit avans spre decontare poate plăti în numerar, din acel avans, în limita a 5.000 lei/zi — plafon calculat separat pentru fiecare angajat cu avans, nu pe total firmă.
- Acordarea inițială a avansului către angajat, dacă se face în numerar, intră în același calcul al plafonului zilnic (art. 3 alin. (4) din lege) — nu e o operațiune separată de restul plăților în numerar ale zilei respective.
- Documentele justificative (bon fiscal, factură, dispoziție de plată) rămân obligatorii pentru fiecare cheltuială mică, indiferent de valoare — plafonul numerarului nu înlocuiește obligația de documentare a cheltuielii.

## Ce se greșește în practică

- Se acordă un avans spre decontare fără să se urmărească plafonul zilnic de 5.000 lei pentru plățile efectuate din el.
- Se tratează acordarea avansului ca operațiune separată de restul plăților în numerar ale zilei, deși legea o include explicit în calculul plafonului zilnic (art. 3 alin. (4)).
- Se justifică o cheltuială mică doar cu bonul fiscal, fără dispoziția de plată/decontul aferent, ceea ce complică urmărirea soldului de casă.

## Ce face iConta.eu

Modulul de casierie al iConta.eu (`core/casa.py`) ține registrul de casă cu sold rulant zi de zi și verifică automat plafoanele legale relevante — soldul zilnic al casei și plafonul zilnic al plăților din avansuri spre decontare pe fiecare persoană — semnalând ca avertisment orice depășire constatată, cu temeiul legal atașat fiecărei reguli.

[iConta.eu](/)
