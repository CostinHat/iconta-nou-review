---
title: "Cum verific contul 4411 înainte de depunerea declarațiilor?"
description: Spre deosebire de TVA sau D112, contul 4411 (impozitul pe profit) nu are un verificator automat față de declarație — reconcilierea e manuală, cu pașii concreți de urmat, nu doar cu promisiunea unui buton.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific contul 4411 înainte de depunerea declarațiilor?

Răspunsul onest, întâi de toate: nu există un verificator automat care să compare rulajul contului 4411 cu declarația de impozit pe profit — nici în iConta, nici într-un modul separat al aplicației. Reconcilierea rămâne manuală, iar mai jos e metodologia concretă.

## Temeiul legal

::: ghid-temei
„Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%." — Legea nr. 227/2015 (Codul fiscal), art. 17.
:::

## De ce nu există un verificator automat aici

TVA are un comparator explicit între conturile 4427/4426 și rândurile din decont. D112 are, la fel, o comparație directă contra conturilor de reținere la sursă. Pentru impozitul pe profit, există doar reconcilieri **interne** ale generatorului declarației — recalculul independent al bazei contabile (veniturile și cheltuielile agregate pe clase de conturi) față de ce folosește generatorul — dar niciuna dintre ele nu compară rezultatul cu rulajul propriu al contului 4411/4418. E o limită de produs declarată, nu o eroare de rulare.

## Metodologia manuală de reconciliere

1. **Recalculează obligația din declarație.** Profit impozabil × 16% (cota standard, Codul fiscal art. 17). Dacă firma depășește pragul de cifră de afaceri pentru impozitul minim pe cifra de afaceri (IMCA), obligația se determină după formula specifică acelui regim, nu simpla înmulțire cu 16%.
2. **Extrage rulajul contului 4411** pentru perioada declarată — atenție la distincția între 4411 (impozit pe profit) și 4418 (impozit pe venit), conturi diferite în planul de conturi.
3. **Compară cele două sume.** O diferență poate veni din: plăți anticipate trimestriale neînregistrate corect, regularizări de la un an la altul, sau o eroare de calcul în declarație.
4. **Documentează diferența**, dacă există — nu o corecta „din ochi" fără să identifici sursa exactă, pentru că exact aceasta e verificarea pe care controlul o va cere.

## Ce se greșește în practică

- Se presupune că, pentru că alte reconcilieri rulează automat (TVA, D205), la fel rulează și pentru impozitul pe profit — nu e cazul.
- Se confundă reconcilierea internă a bazei contabile (venituri/cheltuieli corect agregate) cu o verificare a contului 4411 — prima nu acoperă a doua.
- Se ignoră distincția 4411 vs 4418 la extragerea rulajului de comparat, ceea ce falsifică rezultatul reconcilierii.

## Ce face iConta.eu

Nu construiește o comparație automată pe care nu o poate susține corect — pentru contul 4411 vs declarație, nu există azi un verificator, și spunem asta direct, nu implicit. Ce oferă aplicația e baza de calcul corectă pentru pasul manual: profitul impozabil calculat din venituri și cheltuieli validate, cota de 16% aplicată corect, și fișa de cont pentru rulajul propriu al contului 4411, ca să faci reconcilierea descrisă mai sus fără să cauți datele separat.

[iConta.eu](/)
