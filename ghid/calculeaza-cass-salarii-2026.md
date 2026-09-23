---
title: Cum se calculează CASS pentru salarii în 2026?
description: CASS se calculează cu cota de 10%, pe aceeași bază ca CAS — brutul, redus cu facilitatea aplicabilă, dacă e cazul. Vezi formula și un exemplu complet, pentru ambele ferestre din 2026.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează CASS pentru salarii în 2026?

CASS (contribuția de asigurări sociale de sănătate) se reține din salariul brut al angajatului, cu o cotă fixă de 10%. Baza de calcul e aceeași bază folosită și pentru CAS — nu se calculează CASS pe ce rămâne după CAS.

## Temeiul legal

::: ghid-temei
Contribuția CAS „nu poate fi mai mică" decât CAS calculat pe salariul minim, „în baza unui contract individual de muncă cu normă întreagă SAU cu timp parțial" — condiția e venitul sub minim, nu norma de lucru. — Codul fiscal, art.146 alin.(5^6)
:::

Cota CASS (10%) e confirmată la art.156 din Codul fiscal, activă din 2018-01-01, fără modificări până azi. Dosarul de cercetare arată că regula podelei minime — contribuția nu poate fi calculată sub nivelul corespunzător salariului minim — se aplică ambelor contribuții, CAS și CASS (art.146 alin.(5^6)-(5^9) coroborat cu art.168 alin.(6^1) pentru CASS); citatul verbatim disponibil în corpus se referă explicit la CAS, dar sinteza dosarului confirmă că mecanismul analog acoperă și CASS.

## Formula de calcul

Baza CASS e brutul angajatului, redus în prealabil cu facilitatea „salariul minim neimpozabil" (200 sau 300 lei, dacă sunt îndeplinite cele 4 condiții cumulative din OUG 89/2025). CASS = 10% × bază. Rezultatul nu depinde de deducerea personală (care scade doar baza impozitului, nu baza CASS).

## Exemplu de calcul, pentru ambele ferestre din 2026

Pentru un angajat la salariul minim, funcție de bază, cu facilitatea aplicată:

| Fereastră | Salariul minim brut | Facilitate | Bază CASS | CASS (10%) |
|---|---|---|---|---|
| 1 ian – 30 iun 2026 | 4.050 lei | 300 lei | 3.750 lei | 375,00 lei |
| 1 iul – 31 dec 2026 | 4.325 lei | 200 lei | 4.125 lei | 412,50 lei |

Dacă angajatul nu îndeplinește condițiile facilității (de exemplu, un brut peste minim), baza CASS e pur și simplu brutul, fără reducere.

## Podeaua CASS la program redus de lucru

La normă parțială, CASS nu poate fi calculată sub nivelul corespunzător salariului minim proratat pe fracțiunea de normă, redus cu facilitatea aplicabilă perioadei — aceeași regulă a podelei care se aplică și CAS. Detaliile mecanismului (inclusiv cine suportă diferența) sunt explicate în ghidul dedicat calculului CASS la part-time sub salariul minim.

## Ce se greșește în practică

Cea mai frecventă greșeală e calcularea CASS pe baza rămasă după scăderea CAS din brut, nu pe baza inițială (brut minus facilitate) — CAS și CASS se calculează separat, din aceeași bază. A doua greșeală: uitarea facilității la calculul CASS, cu reținerea unei sume mai mari decât ar avea angajatul dreptul.

## Ce face iConta.eu

CASS se calculează în `_calcul_salariu_2018()`, imediat după CAS, din aceeași bază (brut redus cu facilitatea, dacă se aplică). Cota și pragurile aferente vin din registrul „period-aware" `core.common.COTE`, care aplică automat valorile corecte pentru fereastra din 2026 în care cade luna statului de plată.

[iConta.eu](/)
