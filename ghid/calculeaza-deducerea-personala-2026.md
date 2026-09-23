---
title: Cum se calculează deducerea personală în 2026?
description: Deducerea personală depinde de nr. de persoane în întreținere și de venitul brut, raportat la salariul minim — care are, în 2026, două valori diferite pe cele două jumătăți de an (4.050 lei și 4.325 lei). Vezi scara completă și exemple pe ambele ferestre.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se calculează deducerea personală în 2026?

Deducerea personală se scade din venitul brut, înainte de aplicarea impozitului de 10%. Depinde de două lucruri: câte persoane are angajatul în întreținere și cât de mare e venitul brut lunar, raportat la salariul minim brut pe țară aplicabil acelei luni.

În 2026 există **două valori** ale salariului minim, cu ferestre diferite — 4.050 lei (1 ianuarie – 30 iunie 2026) și 4.325 lei (1 iulie – 31 decembrie 2026). Pentru că deducerea personală se calculează raportat la salariul minim, formula dă rezultate diferite pe cele două jumătăți de an, chiar dacă brutul angajatului rămâne neschimbat.

## Temeiul legal

::: ghid-temei
Codul fiscal (Legea 227/2015), art.77: pragul de bază pentru deducerea integrală e salariul minim brut pe țară; peste acest prag, deducerea scade degresiv cu 0,5 puncte procentuale pentru fiecare tranșă de 50 lei, până la pragul-limită de salariul minim + 2.000 lei, unde deducerea devine zero.
:::

## Scara deducerii (după persoane în întreținere)

Cât timp venitul brut lunar e **sub sau egal cu salariul minim** aplicabil lunii, deducerea se acordă la procentul maxim din scară:

| Persoane în întreținere | Procent din salariul minim |
|---|---|
| 0 | 20% |
| 1 | 25% |
| 2 | 30% |
| 3 | 35% |
| 4 sau mai multe | 45% |

Peste salariul minim, procentul scade cu 0,5 puncte pentru fiecare tranșă începută de 50 lei cu care venitul depășește salariul minim, până la pragul-limită (**salariul minim + 2.000 lei**), unde deducerea ajunge la zero.

## Exemplu — fără persoane în întreținere, la salariul minim brut întreg

| Fereastră | Salariul minim | Deducere (20%) |
|---|---|---|
| 1 ianuarie – 30 iunie 2026 | 4.050 lei | **810 lei** |
| 1 iulie – 31 decembrie 2026 | 4.325 lei | **865 lei** |

Aceeași persoană, cu același număr de persoane în întreținere, primește deduceri diferite pe cele două ferestre ale anului, pentru că salariul minim de referință e diferit.

## Facilități suplimentare, distincte de scara de mai sus

- **+15% din salariul minim**, pentru angajați sub 26 de ani — condiționat de venit brut sub pragul de la alin.(3) (salariul minim + 2.000 lei).
- **+100 lei/lună/copil** înscris la învățământ, indiferent de nivelul venitului — dar condiționat obligatoriu de un document de înscriere la învățământ și o declarație pe propria răspundere a părintelui (dacă părintele are mai mulți angajatori, și declarația de exclusivitate). Vezi ghidul dedicat deducerii pentru angajații cu copii.

## Ce se greșește în practică

- Se aplică o singură valoare a salariului minim pentru tot anul 2026 — corect e verificată fereastra (4.050 sau 4.325 lei) în funcție de luna pentru care se face calculul, nu de data curentă.
- Se calculează deducerea proporțional cu norma de lucru la part-time — deducerea nu se proratează; se aplică integral (la procentul maxim din scară) atâta timp cât venitul brut *realizat* e sub salariul minim întreg, indiferent de fracțiunea de normă.
- Se acordă deducerea de 100 lei/copil fără documentul de înscriere și declarația pe propria răspundere — legea condiționează explicit acordarea acestei sume de existența acestor documente.

## Ce face iConta.eu

Deducerea personală se calculează automat de `deducere_personala()` (`core/salarizare.py`), care necesită obligatoriu data la care se face calculul — codul refuză explicit ghicirea lunii curente, tocmai pentru că salariul minim (deci și deducerea) diferă pe cele două ferestre din 2026. Cotele și pragurile scării de deducere vin din registrul „period-aware" `core.common.COTE`, nu sunt scrise fix în cod.

[iConta.eu](/)
