---
title: Care este plafonul pentru TVA la încasare în 2026?
description: În 2026, plafonul pentru TVA la încasare nu e unic — a fost 4.500.000 lei până la 29 februarie și a crescut la 5.000.000 lei începând cu 1 martie 2026, odată cu intrarea în vigoare a OUG 8/2026.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Care este plafonul pentru TVA la încasare în 2026?

Anul 2026 e un an cu două plafoane pentru TVA la încasare, nu unul singur — o modificare legislativă intervenită la mijlocul anului schimbă răspunsul, în funcție de perioada exactă la care te raportezi.

## Temeiul legal

::: ghid-temei
**Art. 282 alin. (3) din Codul fiscal (Legea 227/2015)**, modificat prin art. 6 pct. 38 OUG 8/2026 (MO 147/25.02.2026): *„...Plafonul pentru aplicarea sistemului TVA la încasare este de: a) 5.000.000 lei, în perioada 1 martie-31 decembrie 2026; b) 5.500.000 lei, începând cu data de 1 ianuarie 2027."*
:::

## Ce înseamnă practic

Pentru perioada **1 ianuarie - 29 februarie 2026**, plafonul rămas în vigoare a fost cel introdus de Legea 296/2020, valabil din 2021: 4.500.000 lei. Din **1 martie 2026**, odată cu intrarea în vigoare a OUG 8/2026, plafonul a crescut la 5.000.000 lei, valabil până la 31 decembrie 2026. Din 1 ianuarie 2027, plafonul va urca la 5.500.000 lei.

Dosarul de cercetare al acestei funcționalități semnalează și o regulă tranzitorie: firmele care depășiseră 4.500.000 lei, dar nu ajunseseră la 5.000.000 lei, până în ianuarie 2026, nu au fost radiate din sistem odată cu schimbarea plafonului; cele aflate în aceeași situație în februarie 2026 nu au avut obligația unei notificări noi. Această regulă tranzitorie e prevăzută la art. 9 din OUG 8/2026.

## Ce se greșește în practică

- **Se raportează cifra de afaceri la un singur plafon pentru tot anul 2026**, ignorând schimbarea de la 1 martie 2026.
- **Se aplică plafonul de 5.000.000 lei retroactiv, și pentru ianuarie-februarie 2026**, deși în acea perioadă era încă valabil plafonul de 4.500.000 lei.
- **Se ignoră regula tranzitorie** pentru firmele care se aflau „la mijloc" (peste 4.500.000 lei, sub 5.000.000 lei) exact în lunile ianuarie-februarie 2026.

## Ce face iConta.eu

Funcția `plafon_la(data)` din `core/common.py` e period-aware — pe baza tabelului `COTE["plafon_tva_incasare"]`, întoarce automat plafonul corect pentru orice dată de referință: 4.500.000 lei înainte de 1 martie 2026, 5.000.000 lei între 1 martie și 31 decembrie 2026, 5.500.000 lei de la 1 ianuarie 2027.

[iConta.eu](/)
