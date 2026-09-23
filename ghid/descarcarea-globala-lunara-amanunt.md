---
title: "Descărcarea globală lunară la amănunt: cum se face"
description: "Pașii descărcării lunare de gestiune la metoda global-valorică: solduri, rulaje, coeficient de repartizare și nota contabilă rezultată."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Descărcarea globală lunară la amănunt: cum se face

La comercianții cu amănuntul care țin evidența mărfii la preț de vânzare (metoda global-valorică), descărcarea de gestiune se face o dată pe lună, printr-o notă contabilă unică ce separă costul mărfii vândute, adaosul comercial și TVA neexigibilă.

## Temeiul legal

::: ghid-temei
OMFP 1802/2014, Anexa 1 — Reglementări contabile, pct. 286 alin. (4): „Repartizarea diferențelor de preț asupra valorii bunurilor ieșite și asupra stocurilor se efectuează cu ajutorul unui coeficient care se calculează astfel: Coeficient de repartizare = [Soldul inițial al diferențelor de preț + Diferențe de preț aferente intrărilor în cursul perioadei, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] / [Soldul inițial al stocurilor la preț de înregistrare + Valoarea intrărilor în cursul perioadei la preț de înregistrare, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] x 100."

pct. 286 alin. (7): „Diferențele de preț se repartizează proporțional atât asupra valorii bunurilor ieșite, cât și asupra bunurilor rămase în stoc."

(Text consolidat OMFP 1802/2014, verificat pe mirrorul local la 17.09.2026.)
:::

Pașii calculului, așa cum rezultă din formula legală de mai sus și din motorul de calcul al iConta.eu:

1. Se determină soldurile inițiale și rulajele conturilor 371 (mărfuri), 378 (adaos comercial) și 4428 (TVA neexigibilă), cumulat de la 1 ianuarie până la sfârșitul lunii.
2. Se calculează coeficientul de repartizare K, ca raport între adaosul cumulat (378) și stocul la preț de înregistrare, din care se exclude TVA neexigibilă (4428) — conform notei *2) de la alin. (4).
3. Se ia rulajul creditor al contului 707 (vânzările lunii) și se aplică K pentru a afla adaosul descărcat.
4. Se determină costul mărfii vândute (607) ca diferență între vânzări și adaosul descărcat, și TVA neexigibilă descărcată (4428), aferentă vânzărilor lunii.

## Ce se greșește în practică

- Calcularea coeficientului doar din rulajul lunii curente, nu cumulat de la începutul exercițiului financiar.
- Uitarea validării manuale a notei — descărcarea automată propusă de aplicație rămâne o ciornă până e validată de contabil.
- Generarea unei note „pe zero" pentru o lună fără vânzări, ceea ce nu are sens contabil.

## Ce face iConta.eu

Funcția `descarca_luna` (`core/stocuri_api.py`) automatizează exact pașii de mai sus: preia soldurile inițiale din `solduri_initiale` (dacă există), rulajele 371/378/4428 din notele deja validate, iar vânzările (707) filtrate explicit pe sursele `horeca_z`, `stocuri` și `facturi_marfa`, doar pe luna curentă. TVA aferentă vânzărilor lunii este aproximată proporțional cu cota medie din stoc (`tva_vanzari = rc_707 × tva_stoc / baza_stoc`), cu mențiunea explicită din codul sursă că o repartizare proporțională din contul 4427 ar fi riscantă.

Dacă nu au existat vânzări în lună, aplicația nu generează nicio notă, ci întoarce un „fapt" structurat care confirmă lipsa vânzărilor. Nota de descărcare, când există, se creează la data ultimei zile calendaristice a lunii, ca **ciornă** — validarea rămâne manuală, în jurnalul contabil.

[iConta.eu](/)
