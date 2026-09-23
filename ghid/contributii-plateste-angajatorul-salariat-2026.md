---
title: Ce contribuții plătește angajatorul pentru un salariat în 2026?
description: Angajatorul datorează separat CAM 2,25% din fondul de salarii brut — o cheltuială proprie, care nu se reține din venitul angajatului și nu apare pe fluturaș ca reținere.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce contribuții plătește angajatorul pentru un salariat în 2026?

Spre deosebire de CAS, CASS și impozitul pe venit — toate reținute din brutul angajatului — angajatorul are o singură contribuție proprie: CAM, contribuția asiguratorie pentru muncă. E o cheltuială suplimentară a firmei, calculată pe lângă salariul brut, nu din el.

## Temeiul legal

::: ghid-temei
„Ordinea reținerilor din brut: facilitate (dacă se aplică) → CAS 25% → CASS 10% → deducere personală → impozit 10% pe baza impozabilă → net. CAM 2,25% e cheltuială angajator, nu reținere." — Dosar de cercetare F080, secțiunea „Cod sursă verificat" (`core/salarizare.py`)
:::

CAM se calculează cu cota de 2,25%, conform art.220^3 alin.(1) din Codul fiscal (confirmat în registrul de cote `core.common.COTE`, activ din 2018-01-01, fără modificări până azi). Fiind o cheltuială a angajatorului, CAM nu se scade din brutul sau din netul angajatului și nu figurează printre reținerile de pe fluturaș.

## Cum se calculează, în cifre

CAM se aplică la salariul de bază brut. Pentru un angajat la salariul minim, în cele două ferestre din 2026:

| Fereastră | Salariul minim brut | CAM (2,25%) | Cost total angajator (brut + CAM) |
|---|---|---|---|
| 1 ian – 30 iun 2026 | 4.050 lei | 91,13 lei | 4.141,13 lei |
| 1 iul – 31 dec 2026 | 4.325 lei | 97,31 lei | 4.422,31 lei |

Calculul e simplu aritmetic: 2,25% × 4.050 = 91,125 → 91,13 lei; 2,25% × 4.325 = 97,3125 → 97,31 lei. Aceste cifre nu sunt un „exemplu oficial" — sunt derivate direct din cota confirmată aplicată la brut.

Dosarul de cercetare nu confirmă dacă facilitatea „salariul minim neimpozabil" (200/300 lei), care reduce baza pentru CAS, CASS și impozit, reduce și baza de calcul a CAM — acest ghid nu face nicio presupunere pe acest punct; pentru certitudine, verifică rezultatul pe un fluturaș generat efectiv de aplicație.

## Ce se greșește în practică

Greșeala tipică e includerea CAM în calculul netului angajatului — CAM nu afectează niciodată salariul net, e o cheltuială separată a firmei, contabilizată distinct. A doua greșeală: presupunerea că CAM se calculează pe aceeași bază redusă (brut minus facilitate) ca CAS/CASS, fără verificare — vezi paragraful de mai sus.

## Ce face iConta.eu

CAM nu intră în funcția de calcul al netului (`_calcul_salariu_2018()`), fiind tratată separat, ca notă contabilă de cheltuială (641 pentru salarii, respectiv 646/436 pentru CAM, conform `monografie_salariu()`, linia 390). Cota vine din registrul „period-aware" `core.common.COTE`, care aplică automat valoarea corectă pentru luna calculată.

[iConta.eu](/)
