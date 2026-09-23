---
title: "Cum corectez impozitul pe dividende calculat greșit?"
description: "Ce verifică motorul D205 automat înainte de generare și cum se corectează o valoare greșită a impozitului pe dividende, la sursă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez impozitul pe dividende calculat greșit?

Impozitul pe dividende afișat greșit în D205 are aproape întotdeauna cauza în datele sursă (notele contabile pe contul 457 sau cotele asociaților), nu într-o eroare de calcul izolată — de aceea corecția trebuie făcută acolo, nu direct în declarație.

## Temeiul legal

::: ghid-temei
"[...] recalculează INDEPENDENT (SQL propriu, aceeași formulă) baza și impozitul per beneficiar din contul 457 și compară cu ce a produs generatorul; orice divergență blochează generarea (`ReconciliereD205`)."
— descriere a modulului `core/d205_reconciliere.py`, verificată în sursă
:::

## Ce se greșește în practică

Se încearcă adesea modificarea directă a sumei impozitului în ecranul declarației, fără a corecta nota contabilă sau cota de asociat care a generat valoarea greșită — ceea ce lasă contabilitatea (contul 457) și declarația neconcordante.

## Ce face iConta.eu

Pentru beneficiarii preluați automat din contul 457, iConta rulează o verificare independentă (`core/d205_reconciliere.py`): baza și impozitul sunt recalculate separat, direct din notele contabile validate, și comparate cu rezultatul generatorului; orice diferență blochează generarea declarației, ceea ce înseamnă că o valoare corectă la nivel de bază de date nu poate produce automat o declarație greșită. Rezultă că singura cale corectă de corecție este verificarea și, dacă e cazul, corectarea notei contabile pe contul 457 (sau a cotei asociatului) și regenerarea D205. Pentru beneficiarii introduși manual (nu din contul 457), reconcilierea completă nu se aplică — se verifică doar consistența internă impozit = cotă × bază, deci corectitudinea datelor introduse manual rămâne în răspunderea contabilului. Important: dacă declarația a fost deja depusă la ANAF cu o valoare greșită, rețineți că iConta nu generează în acest moment declarație D205 rectificativă (vezi ghidul dedicat acestui subiect).

[iConta.eu](/)
