---
title: Provizioanele sunt deductibile la impozitul pe profit?
description: Provizioanele sunt deductibile fiscal doar dacă se încadrează într-unul din cazurile expres prevăzute de CF art. 26 (garanții de bună execuție, ajustări pentru deprecierea creanțelor); toate celelalte categorii contabile (litigii, dezafectare, restructurare, altele) sunt nedeductibile.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Provizioanele sunt deductibile la impozitul pe profit?

Răspunsul scurt: **nu automat**. Contabil, o firmă poate (și trebuie, dacă sunt îndeplinite condițiile de recunoaștere din reglementările contabile) să constituie provizioane pentru mai multe categorii de riscuri — litigii, garanții, dezafectare, restructurare, pensii, impozite. Fiscal însă, Codul fiscal deduce doar câteva dintre ele, limitativ, iar restul rămân cheltuieli nedeductibile la calculul impozitului pe profit, indiferent cât de justificată e constituirea lor contabilă.

## Temeiul legal

::: ghid-temei
"Articolul 26 — Provizioane/ajustări pentru depreciere și rezerve
(1) Contribuabilul are dreptul la deducerea rezervelor și provizioanelor/ajustărilor pentru
depreciere, numai în conformitate cu prezentul articol, astfel: [...]"

"cheltuielile cu provizioane/ajustări pentru depreciere și rezerve, în limita prevăzută la art. 26;"
:::

## Ce se deduce și ce nu

Art. 26 alin. (1) conține o listă limitativă de litere (a-n). Din categoriile pe care le întâlnești curent în contabilitate, doar două ies din nedeductibilitatea generală:

- **lit. b) — provizioane pentru garanții de bună execuție acordate clienților**, dar plafonate la cota contractuală de garanție (nivelul de garantare stabilit prin contract, de regulă un procent din valoarea lucrărilor/produselor vândute) — deductibil doar în limita acestei cote, nu la valoarea integrală a provizionului constituit contabil.
- **lit. c) și lit. j) — ajustări pentru deprecierea creanțelor**, la 30% respectiv 100%, dacă sunt îndeplinite condiții cumulative stricte (vezi ghidurile dedicate ajustărilor de creanțe).

Tot ce nu se regăsește explicit în listă rămâne **nedeductibil**, chiar dacă respectă întru totul condițiile de recunoaștere contabilă din OMFP 1802/2014 pct. 369-374:

- provizioane pentru litigii (cont 1511);
- provizioane pentru dezafectare imobilizări (cont 1513), în afara regimului special de capitalizare a costurilor de dezafectare;
- provizioane pentru restructurare (cont 1514);
- alte provizioane (cont 1518);
- ajustări pentru deprecierea stocurilor (conturile 39x).

::: ghid-exemplu
O firmă constituie un provizion de 50.000 lei pentru un litigiu în curs (cont 1511, cheltuială 6812). Contabil, cheltuiala e corect recunoscută dacă litigiul e probabil să genereze o ieșire de resurse și suma poate fi estimat credibil. Fiscal însă, art. 26 nu prevede deducerea provizioanelor pentru litigii — deci cei 50.000 lei sunt cheltuială nedeductibilă și se adaugă la calculul profitului impozabil (rând distinct în D101).
:::

## Ce se greșește în practică

- Se presupune că orice provizion constituit corect contabil e automat deductibil — regula contabilă și cea fiscală nu coincid.
- Se tratează provizionul pentru garanții ca 100% deductibil, fără verificarea cotei contractuale de garanție.
- Se uită că ajustările pentru deprecierea stocurilor (conturi 39x) nu apar deloc în lista de la art. 26 — sunt nedeductibile necondiționat, oricât de bine documentată e deprecierea.
- Nu se face distincția între cele două praguri de deducere a ajustărilor de creanțe (30% la peste 270 de zile, respectiv 100% la faliment/insolvență declarată).

## Ce face iConta.eu

Motorul de calcul din `core/provizioane.py` mapează fiecare tip de provizion pe contul sintetic din grupa 151 corespunzător (litigii → 1511, garanții → 1512, dezafectare → 1513, restructurare → 1514, impozite → 1516, altele → 1518) și generează nota contabilă corectă la constituire (6812=15xx) și la reluare (15xx=7812). Deductibilitatea fiscală e semnalată explicit doar pentru garanții (`deductibil = (tip == "garantii")`); pentru celelalte tipuri, aplicația nu marchează automat caracterul nedeductibil în declarația D101 — rândurile de cheltuieli nedeductibile (P23-P33) se completează manual, pe baza analizei de mai sus.

[iConta.eu](/)
