---
title: Cum se calculează CAS la part-time sub salariul minim?
description: Angajatul plătește CAS pe brutul lui real, dar diferența până la podeaua minimă (salariul minim proratat, minus facilitate) e o cheltuială suplimentară a angajatorului, nu o reținere.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează CAS la part-time sub salariul minim?

Când brutul contractual al unui part-time scade sub podeaua minimă de referință, CAS-ul total datorat statului nu poate fi mai mic decât cel calculat pe podea — dar asta nu înseamnă că angajatul e reținut cu mai mult. Diferența se împarte între reținerea normală a angajatului și o cheltuială suplimentară a angajatorului.

## Temeiul legal

::: ghid-temei
Contribuția CAS „nu poate fi mai mică" decât CAS calculat pe salariul minim, „în baza unui contract individual de muncă cu normă întreagă SAU cu timp parțial" — condiția e venitul sub minim, nu norma de lucru. — Codul fiscal, art.146 alin.(5^6)
:::

## Pasul 1 — podeaua CAS

Podea = (salariul minim al perioadei − facilitatea aplicabilă) × fracțiunea de normă. Pentru un contract part-time la 4 ore/zi (fracțiune 0,5), fereastra 1 iulie – 31 decembrie 2026 (salariul minim 4.325 lei, facilitate 200 lei): podea = (4.325 − 200) × 0,5 = 2.062,50 lei.

## Pasul 2 — compararea cu brutul contractual

Dacă brutul contractual (de exemplu, 2.000 lei) e sub podea (2.062,50 lei), CAS-ul total datorat se calculează pe podea, nu pe brut:

- CAS total la podea = 25% × 2.062,50 = 515,63 lei

## Pasul 3 — cine plătește cât

CAS reținut efectiv din venitul angajatului se calculează pe brutul lui real: 25% × 2.000 = 500 lei (contul 421/4315, reținere obișnuită). Diferența dintre CAS-ul total datorat și cel reținut de la angajat — 515,63 − 500 = 15,63 lei — e suportată de angajator, ca o cheltuială suplimentară distinctă (contul 6451/4315, cheltuială, nu reținere din venitul angajatului).

| Element | Calcul | Valoare |
|---|---|---|
| Brut contractual | — | 2.000 lei |
| Podea CAS | (4.325 − 200) × 0,5 | 2.062,50 lei |
| CAS total la podea | 25% × 2.062,50 | 515,63 lei |
| CAS reținut de la angajat | 25% × 2.000 | 500,00 lei |
| CAS suplimentar, cheltuială angajator | 515,63 − 500,00 | 15,63 lei |

Dacă brutul contractual e egal sau peste podea, nu se aplică nicio suprataxare — CAS se calculează direct pe brut, integral reținut de la angajat.

## Ce se greșește în practică

Greșeala frecventă e reținerea de la angajat a întregului CAS calculat pe podea, nu pe brutul lui real — angajatul nu poate fi reținut cu mai mult decât proporția din venitul lui efectiv câștigat; diferența e a angajatorului. Greșeala inversă: ignorarea podelei complet, cu CAS calculat direct pe brutul contractual redus, fără verificare.

## Ce face iConta.eu

Regula „baza_podea" (`core/salarizare.py`, liniile 292-323) calculează automat podeaua pentru fereastra activă a lunii și generează, când e cazul, atât reținerea obișnuită (421/4315), cât și cheltuiala suplimentară de suprataxare (6451/4315), conform `monografie_salariu()` (linia 390).

[iConta.eu](/)
