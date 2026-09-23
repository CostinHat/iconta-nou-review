---
title: Ce contribuții plătește angajatul din salariu în 2026?
description: Angajatul suportă trei rețineri din brut — CAS 25%, CASS 10% și impozit pe venit 10% — aplicate într-o ordine precisă. Vezi formula completă și un exemplu de calcul.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce contribuții plătește angajatul din salariu în 2026?

Din salariul brut al unui angajat se rețin trei sume, toate în sarcina lui, niciuna a angajatorului: CAS (contribuția de asigurări sociale), CASS (contribuția de asigurări sociale de sănătate) și impozitul pe venit. Ordinea în care se aplică rețineri contează, pentru că fiecare se calculează pe o bază diferită de cea anterioară.

## Temeiul legal

::: ghid-temei
Contribuția CAS „nu poate fi mai mică" decât CAS calculat pe salariul minim, „în baza unui contract individual de muncă cu normă întreagă SAU cu timp parțial" — condiția e venitul sub minim, nu norma de lucru. — Codul fiscal, art.146 alin.(5^6)
:::

Cotele aplicate veniturilor salariale, toate suportate de angajat prin reținere din brut:

| Reținere | Cotă | Temei |
|---|---|---|
| CAS | 25% | CF art.138 lit.a) |
| CASS | 10% | CF art.156 |
| Impozit pe venit | 10% | CF art.64 alin.(1) / art.78 |

Regula citată mai sus (art.146 alin.(5^6)) arată că aceste rețineri au un prag minim garantat prin lege — CAS (și, analog, CASS) nu pot fi calculate sub nivelul corespunzător salariului minim, indiferent de venitul efectiv realizat. Această podea e relevantă mai ales la program redus de lucru (part-time).

## Ordinea corectă a reținerilor

Cele trei rețineri nu se aplică toate pe brut, ci în cascadă:

1. Dacă se aplică facilitatea „salariul minim neimpozabil" (200 sau 300 lei, după fereastra din 2026), baza se reduce mai întâi cu această sumă.
2. CAS 25% se calculează pe bază.
3. CASS 10% se calculează pe aceeași bază (nu pe baza rămasă după CAS).
4. Se scade deducerea personală (dacă angajatul are funcție de bază).
5. Impozitul de 10% se aplică pe ce rămâne (baza impozabilă).

CAM (2,25%) nu apare în această listă — e cheltuială a angajatorului, nu reținere din venitul angajatului.

## Cât reține efectiv angajatorul, în cifre

Pentru un angajat la salariul minim, funcție de bază, fără persoane în întreținere, cu facilitatea aplicată, în fereastra 1 iulie – 31 decembrie 2026 (brut 4.325 lei, facilitate 200 lei, bază 4.125 lei):

- CAS = 25% × 4.125 = 1.031,25 lei
- CASS = 10% × 4.125 = 412,50 lei
- Deducere personală (0 persoane în întreținere) = 865 lei
- Bază impozabilă = 4.125 − 1.031,25 − 412,50 − 865 = 1.816,25 lei
- Impozit = 10% × 1.816,25 = 181,63 lei

Total reținut din brut: 1.031,25 + 412,50 + 181,63 = 1.625,38 lei → net = 4.325 − 1.625,38 = 2.699,62 lei.

Aceste cifre nu sunt un „exemplu oficial" publicat de ANAF — sunt calculate direct din cotele confirmate mai sus, aplicate în ordinea din motorul de calcul.

## Ce se greșește în practică

Cea mai frecventă greșeală e calcularea CASS pe baza rămasă după scăderea CAS, nu pe baza inițială (brut minus facilitate, dacă se aplică) — CAS și CASS se calculează separat, din aceeași bază, nu în cascadă una din cealaltă. A doua greșeală: confuzia „brut sub salariul minim" cu un brut care doar pare mic din cauza facilității — D112 refuză brutul sub salariul minim pe normă întreagă ca dată suspectă, tocmai pentru a preveni asemenea erori.

## Ce face iConta.eu

Motorul de calcul (`core/salarizare.py`, `_calcul_salariu_2018()`) aplică exact ordinea de mai sus: facilitate → CAS 25% → CASS 10% → deducere personală → impozit 10% → net. Toate cotele vin din registrul „period-aware" `core.common.COTE`, astfel încât aplicația folosește automat valorile corecte pentru fereastra din 2026 în care cade luna calculată.

[iConta.eu](/)
