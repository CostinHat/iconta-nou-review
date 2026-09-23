---
title: Greșeala de a nu declara ieșirea din micro la timp
description: Obligația de ieșire din micro curge de la trimestrul depășirii plafonului, nu de la sfârșitul anului — iar întârzierea nu e semnalată automat de aplicație.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Greșeala de a nu declara ieșirea din micro la timp

Una dintre cele mai frecvente greșeli legate de regimul micro nu e alegerea greșită a regimului, ci întârzierea — continuarea depunerii declarațiilor de micro după ce plafonul de venituri a fost deja depășit.

## Temeiul legal

::: ghid-temei
**Art. 52 alin. (1) CF**: „Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit **începând cu trimestrul în care s-a depășit această limită**." Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, linia 6414 (modificat de OUG 8/2026, art. 6 pct. 20).
:::

Greșeala tipică nu e o decizie greșită, ci o lipsă de acțiune: firma continuă să depună D100 (declarația micro) trimestru după trimestru, deși veniturile cumulate au trecut deja de 100.000 euro. Legea nu lasă loc de interpretare — obligația de impozit pe profit curge din trimestrul depășirii, nu din trimestrul următor și nu din anul următor.

Consecința practică: fiecare trimestru raportat greșit ca micro după momentul depășirii înseamnă o declarație pe regimul greșit, cu impact direct asupra sumei de impozit datorate (1% pe venituri, la micro, față de 16% pe profitul impozabil, la profit) — o diferență care nu dispare, ci trebuie corectată retroactiv, cu declarații rectificative depuse la ANAF.

Pentru că nicio aplicație, inclusiv iConta, nu are un mecanism automat de alertă la depășirea plafonului, singura protecție reală e verificarea periodică manuală a veniturilor cumulate față de plafon, mai ales spre finalul fiecărui trimestru.

## Ce se greșește în practică

- Se verifică plafonul o singură dată, la începutul anului, fără monitorizare trimestrială a veniturilor cumulate.
- Se presupune că trecerea la profit se aplică doar din anul fiscal următor, nu din trimestrul efectiv al depășirii.
- Se depune declarația de micro din inerție (pentru că așa a fost regimul până atunci), fără verificare explicită înainte de fiecare depunere.

## Ce face iConta.eu

Motorul confirmă direct, prin comentariu de cod (`core/control_fiscal_api.py`): „Aplicația NU cunoaște plafonul de ieșire din micro [...], deci nu există fapt care să contrazică bifa" — nicio constantă de plafon micro (100.000 €) nu există în motorul de calcul. iConta nu poate, deci, avertiza automat asupra depășirii — verificarea rămâne integral responsabilitatea contabilului, iar corectarea vectorului (odată depistată depășirea) urmează regula generală de blocare peste perioade închise.

[iConta.eu](/)
