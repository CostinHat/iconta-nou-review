---
title: "Cum tratez mijloacele fixe neînregistrate descoperite la inventar"
description: "Ce cere norma pentru evaluarea unui mijloc fix descoperit în plus la inventariere și ce date obligatorii cere iConta.eu pentru a-l trece corect în evidență."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez mijloacele fixe neînregistrate descoperite la inventar

Un mijloc fix folosit efectiv în activitate, dar niciodată trecut în evidență, e o situație tipică de "plus" la inventarierea anuală — și are reguli proprii de evaluare și de introducere în evidență.

## Temeiul legal

::: ghid-temei
"d) la valoarea justă - pentru bunurile obținute cu titlu gratuit sau constatate plus la
inventariere." — OMFP 1802/2014, pct. 75 alin. (1) lit. d)
:::

Bunul se evaluează la **valoarea justă** de la data constatării, nu la un cost istoric estimat. Pentru clasificarea contabilă a plusului, contul 4754 "Plusuri de inventar de natura imobilizărilor" — parte din clasa 47 "Conturi de subvenții, regularizare și asimilate" din planul de conturi OMFP 1802/2014 — este contul corespondent folosit pentru mijloacele fixe găsite în plus, spre deosebire de stocuri, unde plusul afectează direct un cont de cheltuială/venit (ex. 371=607).

Un mijloc fix descoperit la inventariere trebuie introdus și în registrul de mijloace fixe cu toate datele necesare calculului de amortizare (durată normală de funcționare, data punerii în funcțiune, metodă) — altfel activul rămâne, practic, "invizibil" pentru amortizare și pentru declarația D406. Metoda de amortizare aleasă trebuie să respecte restricțiile pe categorie de activ din Codul fiscal, art. 28.

## Ce se greșește în practică

- Se înregistrează doar nota contabilă de plus, fără să se introducă efectiv mijlocul fix în registrul de mijloace fixe — activul rămâne fără amortizare calculată pentru anii următori.
- Se evaluează bunul la o valoare arbitrară sau la costul de achiziție estimat, în loc de valoarea justă de la data constatării.
- Se alege o metodă de amortizare care nu e permisă pentru categoria activului.

## Ce face iConta.eu

Pentru operația "Plus mijloc fix" din ecranul "Inventariere anuală", iConta.eu cere obligatoriu durata normală de funcționare (`dnf_luni`) și data punerii în funcțiune, și refuză (cu eroare) metoda de amortizare care nu e permisă pentru categoria activului declarată. Mijlocul fix e apoi normalizat și adăugat efectiv în registrul de mijloace fixe — nu doar înregistrat ca notă contabilă — folosind contul 4754 pentru plusul constatat. Valoarea justă la care se înregistrează bunul rămâne, ca și la stocuri, cea introdusă de contabil — aplicația nu o calculează automat.

[iConta.eu](/)
