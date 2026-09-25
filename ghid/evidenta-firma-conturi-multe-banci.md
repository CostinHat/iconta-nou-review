---
title: Cum se ține evidența dacă firma are conturi la mai multe bănci
description: Contul 512 "Conturi curente la bănci" se dezvoltă pe analitice distincte, unul per bancă/cont, potrivit OMFP 1802/2014 pct. 303 și pct. 593 — fiecare cont bancar are evidență proprie, cu sold și extras reconciliate separat.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se ține evidența dacă firma are conturi la mai multe bănci?

Când o firmă are cont de operațiuni curente la o bancă, cont pentru încasări cu cardul la alta și eventual un cont separat pentru un credit sau un leasing, întrebarea e cum se organizează contabil fără să se amestece soldurile.

### Contul 512 se dezvoltă pe analitice

OMFP 1802/2014, pct. 303: "Contabilitatea disponibilităților aflate în bănci/casierie și a mișcării acestora, ca urmare a încasărilor și plăților efectuate, se ține distinct în lei și în valută." Iar regula generală de organizare a conturilor, pct. 593: "Conturile sintetice din planul de conturi se pot dezvolta pe conturi analitice în funcție de necesitățile impuse de anumite reglementări sau potrivit necesităților proprii ale fiecărei entități."

Aplicat la bănci multiple, asta înseamnă: contul sintetic **512 "Conturi curente la bănci"** (cont bifuncțional, potrivit normei de utilizare a contului) se dezvoltă pe analitice separate, de regulă câte unul pentru fiecare cont bancar real — de exemplu:

- 512.01 — Banca A, cont RON
- 512.02 — Banca B, cont RON
- 512.03 — Banca A, cont EUR

### De ce contează separarea, nu doar formal

1. **Reconcilierea cu extrasul de cont** se face per cont bancar real, nu pe un total agregat — orice diferență între soldul contabil și extrasul băncii trebuie identificată pe contul analitic corespunzător, altfel devine imposibil de urmărit care bancă are diferența.
2. **Valuta** — dacă firma are un cont în EUR și unul în RON, ele nu pot fi amestecate în aceeași analitică: pct. 303 cere evidență distinctă în lei și în valută, inclusiv pentru evaluarea la cursul de închidere.
3. **Viramentele între conturile proprii ale firmei** (de exemplu, mutare de bani din contul de la Banca A în contul de la Banca B) nu se înregistrează direct 512 = 512, ci prin contul de tranzit **581 "Viramente interne"** — pentru că suma iese dintr-un cont și intră în altul cu o zi sau două decalaj, iar 581 reflectă corect intervalul în care banii "sunt pe drum" între cele două bănci.

### Checklist de organizare

1. Deschide câte o analitică 512 pentru fiecare cont bancar real (IBAN), separat pe monedă dacă e cazul.
2. Denumește analiticele clar (bancă + monedă), nu generic — ușurează reconcilierea și controlul.
3. Orice transfer între conturile proprii trece prin 581, nu direct între analiticele 512.
4. Reconciliază fiecare analitică separat cu extrasul de cont lunar corespunzător — nu un total pe toate băncile.
5. Pentru rapoartele de trezorerie, soldul de disponibilități al firmei e suma tuturor analiticelor 512 (plus 531 casă, dacă relevant), dar evidența operativă rămâne pe fiecare cont în parte.
