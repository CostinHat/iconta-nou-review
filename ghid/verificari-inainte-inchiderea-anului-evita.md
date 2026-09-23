---
title: "Ce verificări fac înainte de închiderea anului pentru a evita diferențele la control?"
description: Pe lângă verificările lunare, închiderea anului adaugă reconcilierea D205 față de contul 457 și obligă o reconciliere manuală pentru cont 441 — zonă fără verificator automat, declarată ca atare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce verificări fac înainte de închiderea anului pentru a evita diferențele la control?

Pe lângă tot ce se verifică lunar (echilibru, TVA pe conturi), închiderea anului adaugă cel puțin două zone specifice — una acoperită automat, una care cere o metodologie manuală, fără ocolișuri.

## Temeiul legal

::: ghid-temei
„Veniturile sub formă de dividende [...] se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final." — Legea nr. 227/2015 (Codul fiscal), art. 97 alin. (7), forma modificată prin Legea 141/2025, art. II pct. 1.

„Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%." — Legea nr. 227/2015 (Codul fiscal), art. 17.
:::

## Ce se verifică automat, specific de an

**Balanța anuală** (solduri inițiale, echilibrul ledgerului) rulează pe aceleași reguli ca lunar, dar contează tot mai mult acum: erorile acumulate în cursul anului devin vizibile abia la agregarea anuală.

**D205 (declarația privind dividendele) față de contul 457** are DOI mecanisme de reconciliere: unul recalculează independent baza și impozitul per beneficiar direct din conturi și cota legală, comparând cu ce a generat declarația; celălalt e puntea folosită de motorul general de reconciliere a declarațiilor, cu stări verde/roșu/gri. Pentru firmele **fără dividende plătite în an**, reconcilierea nu rulează deloc (stare de „nimic de reconciliat"), nu verde — nu confunda absența verificării cu o verificare reușită.

**Limită declarată**: beneficiarii introduși **manual** în declarație (nu derivați din rulajul contului 457) nu sunt acoperiți de recalculul independent. Dacă ai completat manual un beneficiar în D205, verifică-l separat, nu presupune că a trecut prin reconciliere.

## Ce NU se verifică automat: cont 441 (impozit pe profit)

Nu există, la acest moment, un verificator care să compare rulajul contului 441/4411 (impozitul pe profit înregistrat în contabilitate) cu ce rezultă din D100/D101 — spre deosebire de TVA sau de D112, unde există o comparație automată explicită contra unui cont real.

Verificarea rămâne manuală: recalculezi obligația de impozit pe profit din D101 (profit impozabil × 16%, cu excepția regimului IMCA pentru cifre de afaceri peste prag), o compari cu rulajul propriu al contului 4411/4418, și urmărești manual diferențele. Nu e un pas pe care contabilul îl omite — e o limită curentă a produsului, de care ține cont în planul de închidere.

## Ce se greșește în practică

- Se presupune că, pentru că D205 și TVA au reconciliere automată, la fel are și impozitul pe profit — nu e cazul, iar diferența trebuie reconciliată manual.
- Se citește „stare verde" pe reconcilierea D205 ca „firma nu are probleme cu dividendele", când de fapt firma pur și simplu nu a avut dividende plătite în an — nimic de reconciliat, nu confirmare.
- Se validează beneficiarii D205 introduși manual fără verificare separată, presupunând că au trecut prin același recalcul ca cei derivați automat din 457.

## Ce face iConta.eu

La închiderea anului, rulează automat verificările de echilibru și reconcilierea D205 față de contul 457, prin cele două mecanisme descrise — cu semnalarea explicită a stărilor gri și a cazurilor „nimic de reconciliat". Pentru cont 441 vs D100/D101, nu pretindem o automatizare care nu există: recomandăm reconcilierea manuală descrisă mai sus, ca parte a checklistului de închidere, nu ca pas de bifat rapid.

[iConta.eu](/)
