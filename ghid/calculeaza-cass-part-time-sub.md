---
title: Cum se calculează CASS la part-time sub salariul minim?
description: Ca și la CAS, angajatul plătește CASS pe brutul lui real, iar diferența până la podeaua minimă (salariul minim proratat, minus facilitate) e o cheltuială suplimentară a angajatorului.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează CASS la part-time sub salariul minim?

CASS urmează același mecanism ca CAS: când brutul contractual al unui part-time scade sub podeaua minimă, CASS-ul total datorat nu poate fi calculat sub nivelul corespunzător podelei — dar angajatul e reținut doar pentru partea aferentă venitului lui real.

## Temeiul legal

::: ghid-temei
Contribuția CAS „nu poate fi mai mică" decât CAS calculat pe salariul minim, „în baza unui contract individual de muncă cu normă întreagă SAU cu timp parțial" — condiția e venitul sub minim, nu norma de lucru. — Codul fiscal, art.146 alin.(5^6)
:::

Citatul verbatim disponibil în corpus privește explicit CAS; dosarul de cercetare confirmă însă că podeaua analogă se aplică și CASS, prin art.146 alin.(5^6)-(5^9) coroborat cu art.168 alin.(6^1). Excepțiile de la regula podelei (art.146 alin.(5^7)) — elevi/studenți sub 26 de ani, ucenici sub 18 ani, persoane cu dizabilități, pensionari la limită de vârstă, cumul de contracte cu bază cumulată la nivelul minimului — se aplică deopotrivă CAS și CASS.

## Pasul 1 — podeaua CASS

Podea = (salariul minim al perioadei − facilitatea aplicabilă) × fracțiunea de normă. Pentru un contract part-time la 4 ore/zi (fracțiune 0,5), fereastra 1 iulie – 31 decembrie 2026 (salariul minim 4.325 lei, facilitate 200 lei): podea = (4.325 − 200) × 0,5 = 2.062,50 lei.

## Pasul 2 — compararea cu brutul contractual

Dacă brutul contractual (de exemplu, 2.000 lei) e sub podea (2.062,50 lei), CASS-ul total datorat se calculează pe podea:

- CASS total la podea = 10% × 2.062,50 = 206,25 lei

## Pasul 3 — cine plătește cât

CASS reținut efectiv din venitul angajatului se calculează pe brutul lui real: 10% × 2.000 = 200 lei (contul 421/4316, reținere obișnuită). Diferența — 206,25 − 200 = 6,25 lei — e suportată de angajator, ca o cheltuială suplimentară distinctă (contul 6453/4316, cheltuială, nu reținere din venitul angajatului).

| Element | Calcul | Valoare |
|---|---|---|
| Brut contractual | — | 2.000 lei |
| Podea CASS | (4.325 − 200) × 0,5 | 2.062,50 lei |
| CASS total la podea | 10% × 2.062,50 | 206,25 lei |
| CASS reținut de la angajat | 10% × 2.000 | 200,00 lei |
| CASS suplimentar, cheltuială angajator | 206,25 − 200,00 | 6,25 lei |

## Ce se greșește în practică

Greșeala frecventă e reținerea de la angajat a întregului CASS calculat pe podea, în loc de doar partea aferentă brutului lui real — diferența e a angajatorului, nu se scade din netul angajatului. A doua greșeală: aplicarea podelei doar la CAS, uitând că mecanismul e analog și pentru CASS.

## Ce face iConta.eu

Regula „baza_podea" (`core/salarizare.py`, liniile 292-323) tratează CAS și CASS simetric, calculând podeaua o singură dată pentru fereastra activă a lunii și generând, când e cazul, atât reținerea obișnuită (421/4316), cât și cheltuiala suplimentară de suprataxare (6453/4316), conform `monografie_salariu()` (linia 390).

[iConta.eu](/)
