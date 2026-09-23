---
title: Ce faci dacă ai ales greșit durata de amortizare?
description: O durată greșit aleasă se corectează prin identificarea intervalului corect din catalogul HG 2139/2004 și recalcularea amortizării de la data punerii în funcțiune - nu printr-o simplă schimbare a cifrei pe activul deja existent.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce faci dacă ai ales greșit durata de amortizare?

Durata normală de funcționare rămâne, prin lege, fixă odată stabilită pentru un activ — deci o corectare nu înseamnă "o ajustăm din mers", ci o revizuire reală, pornind de la identificarea duratei corecte din catalog și recalcularea amortizării deja înregistrate.

## Temeiul legal

::: ghid-temei
Astfel stabilita, durata normala de funcționare a mijlocului fix rămâne neschimbata până la recuperarea integrală a valorii de intrare a acestuia sau scoaterea sa din funcțiune.

— HG 2139/2004, Catalogul privind clasificarea și duratele normale de funcționare a mijloacelor fixe, cap. II pct.4
:::

Pasul întâi e să confirmați, din catalog, intervalul (plaja) de ani corect pentru codul de clasificare real al activului — greșeala tipică e alegerea unui cod apropiat, dar nu identic, cu durate diferite. Odată identificată durata corectă, amortizarea trebuie recalculată de la data punerii în funcțiune a activului, nu doar de la data la care ați observat eroarea — deoarece toate lunile deja amortizate cu durata greșită au generat o cheltuială incorectă, care trebuie corectată în evidența contabilă și fiscală.

## Ce se greșește în practică

- Se schimbă doar durata pentru lunile viitoare, lăsând neschimbată amortizarea deja înregistrată cu durata greșită — corectarea trebuie să pornească de la PIF, nu doar de la momentul descoperirii erorii.
- Se ignoră impactul unei corectări de durată asupra cheltuielii deductibile deja declarate în perioadele fiscale anterioare, dacă acestea au fost deja raportate.
- Se presupune că orice modificare a duratei e permisă oricând, fără să se verifice dacă e vorba de o corectare reală a unei erori sau doar de o schimbare de opțiune ulterioară — a doua situație nu are, în general, acoperire legală.

## Ce face iConta.eu

Nu există, la acest moment, un ecran dedicat de editare directă a unui singur câmp (durata) pe un mijloc fix deja înregistrat în registru — corectarea unei valori greșite, inclusiv a duratei, se face prin re-importul complet al registrului mijloacelor fixe (fișier CSV/XLSX), care înlocuiește integral rândurile existente ale firmei cu cele din fișierul reîncărcat. La reimport, aplicația validează blocant durata (respinge o valoare de zero sau negativă) și semnalează, ca avertisment informativ, situațiile în care lipsește contul de imobilizare — dar nu validează dacă durata introdusă se încadrează în plaja corectă din catalogul HG 2139/2004; această verificare rămâne responsabilitatea contabilului la momentul reimportului.

[iConta.eu](/)
