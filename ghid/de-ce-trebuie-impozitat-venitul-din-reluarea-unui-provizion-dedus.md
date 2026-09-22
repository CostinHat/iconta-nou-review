---
title: De ce trebuie impozitat venitul din reluarea unui provizion dedus?
description: Legea impune explicit ca reluarea unui provizion dedus anterior să fie inclusă ca venit impozabil, indiferent de motivul reluării — omiterea acestui venit din calculul profitului impozabil e o greșeală frecventă și ușor de detectat la control.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# De ce trebuie impozitat venitul din reluarea unui provizion dedus?

O greșeală recurentă: firma constituie corect un provizion deductibil (de exemplu pentru garanții, sau o ajustare de creanță la 30%/100%), își reduce profitul impozabil în anul constituirii, iar apoi, când provizionul se reia la venituri, tratează venitul din reluare ca neimpozabil — "pentru că oricum a fost doar o mișcare contabilă". Legea spune exact contrariul: dacă deducerea a fost acordată la constituire, venitul din reluare trebuie impozitat, indiferent de motivul reluării.

## Temeiul legal

::: ghid-temei
"Reducerea sau anularea oricărui provizion ori a rezervei care a fost anterior dedusă, inclusiv
rezerva legală, se include în rezultatul fiscal, ca venituri impozabile sau elemente similare
veniturilor, indiferent dacă reducerea sau anularea este datorată modificării destinației
provizionului sau a rezervei, distribuirii provizionului sau rezervei către participanți sub orice
formă, lichidării, divizării sub orice formă, fuziunii contribuabilului sau oricărui altui motiv."
:::

## De ce contează "indiferent de motiv"

Legea enumeră explicit motivele reluării ca fiind irelevante pentru obligația de impozitare: schimbarea destinației, distribuirea către asociați, lichidarea, divizarea, fuziunea "sau orice alt motiv". Practic, nu există nicio situație în care reluarea unui provizion dedus anterior să scape de impozitare — inclusiv atunci când reluarea are loc într-un context de reorganizare a firmei (fuziune, divizare), unde alte reguli fiscale pot fi mai favorabile, dar nu și pentru acest venit specific.

::: ghid-exemplu
O firmă a dedus 3.000 lei la constituirea unui provizion pentru garanții (cotă contractuală de garanție). Doi ani mai târziu, firma fuzionează cu alta, iar provizionul rămas neutilizat e anulat cu ocazia fuziunii. Chiar dacă anularea are loc "din cauza fuziunii" și nu pentru că garanția a expirat normal, cei 3.000 lei rămân venit impozabil în anul reluării — exact ce prevede legea prin sintagma "indiferent de motiv".
:::

## Ce se greșește în practică

- Se presupune, greșit, că doar reluarea "normală" (expirarea garanției, stingerea litigiului) generează venit impozabil, iar reluarea din alte motive (fuziune, distribuire, schimbare de destinație) ar fi scutită.
- Se omite complet venitul din reluare la calculul rezultatului fiscal, tratând operațiunea ca "pur contabilă", fără vreun impact fiscal.
- Se impozitează integral reluarea unei ajustări de creanță care fusese dedusă doar parțial (30%), în loc să se impoziteze doar partea corespunzătoare deducerii acordate.
- Se pierde legătura dintre constituire și reluare atunci când cele două au loc în exerciții financiare diferite, mai ales dacă evidența nu a păstrat mențiunea că provizionul fusese dedus.

## Ce face iConta.eu

`core/provizioane.py` generează corect nota contabilă de reluare pentru fiecare tip de provizion (`15xx = 7812`, prin `nota_provizion`), dar nu recalculează automat, la momentul reluării, dacă provizionul respectiv fusese dedus la constituire — flagul `deductibil` nu e propagat de la constituire la reluare. Responsabilitatea de a identifica provizioanele deduse anterior și de a include venitul din reluarea lor în rezultatul fiscal, conform art. 26 alin. (5), rămâne a utilizatorului aplicației.

[iConta.eu](/)
