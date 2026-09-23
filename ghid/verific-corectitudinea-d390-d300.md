---
title: Cum verific corectitudinea D390 față de D300
description: Două comparații rulează automat — D390 față de decontul depus și D390 față de evidența contabilă validată — fiecare cu semafor propriu.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum verific corectitudinea D390 față de D300

Verificarea D390 în raport cu D300 nu e o singură comparație, ci două, care rulează în paralel și au surse diferite: una pune D390 față de evidența contabilă validată, cealaltă pune D390 față de D300-ul efectiv depus.

## Temeiul legal

::: ghid-temei
**Art. 325 din Codul fiscal (Legea 227/2015)** — obligația depunerii lunare a declarației recapitulative (D390), cu livrările intracomunitare scutite (lit. a) și achizițiile intracomunitare taxabile (lit. d).

Structura oficială a formularului D300 confirmă rândurile **R1_1** (livrări intracomunitare) și **R5_1** (achiziții intracomunitare) ca puncte de comparație cu bazele din D390.
:::

**Prima comparație — D390 față de evidența contabilă validată.** Bazele de livrări/achiziții intracomunitare din D390 se confruntă cu facturile intracomunitare ale perioadei care au o notă contabilă validată legată de ele. O factură cu notă doar în ciornă nu contează ca evidență — trebuie să fie validată.

**A doua comparație — D390 față de D300 efectiv depus.** Aceleași baze din D390 (recalculate pe cea mai recentă perioadă cu D300 depus prin aplicație) se confruntă cu rândurile R1_1 (livrări) și R5_1 (achiziții) din acel D300.

Fiecare comparație primește propriul semnal:

- **verde** — valorile coincid, în limita unei toleranțe de rotunjire la leu;
- **roșu** — D390 arată o operațiune pe care evidența validată sau D300 depus nu o confirmă deloc; remediul e sugerat (contabilizare, rectificativă sau corecție D390), confirmat de tine;
- **gri** — orice altă diferență de cifre, sau situația în care nu există un D300 depus prin aplicație în fereastra relevantă.

Starea finală a firmei pe acest control e roșu dacă oricare dintre cele două comparații e roșie, altfel gri dacă oricare e gri, altfel verde.

## Ce se greșește în practică

- Se verifică o singură comparație (de obicei D390 ↔ D300) și se ignoră cealaltă (D390 ↔ evidența validată) — cele două pot avea rezultate diferite, pentru că au surse diferite.
- Se presupune că o notă contabilă în ciornă contează ca dovadă a contabilizării — nu contează; doar statusul „validată" intră în comparație.
- Se compară D390 cu un D300 din luna curentă a ecranului, deși fereastra reală a comparației e cea mai recentă perioadă cu D300 depus prin aplicație, nu neapărat luna afișată în ecran.

## Ce face iConta.eu

Aplicația calculează bazele D390 pe fereastra TVA curentă și rulează, automat, ambele comparații — față de evidența validată și față de D300 depus prin aplicație pe perioada lui proprie. Rezultatul combinat apare în secțiunea „Declarație vs contabilitate" din Control fiscal, cu semafor propriu pe fiecare comparație și explicația cauzei atunci când apare roșu.

Nu se verifică: operațiunile intracomunitare de servicii (P/S — D390 le ia manual, D300 nu expune rânduri echivalente în această comparație) și operațiunile triunghiulare (T/R).

[iConta.eu](/)
