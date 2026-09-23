---
title: Cum verific D390 cu balanța contabilă?
description: Nu există, în verificarea D390, o interogare pe conturi sau solduri din balanță — sursa e nota contabilă validată legată de factura intracomunitară.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum verific D390 cu balanța contabilă?

Răspunsul scurt: nu se poate, pentru că nu așa funcționează controlul din aplicație. Verificarea D390 nu interoghează balanța de verificare — nici solduri, nici rulaje de cont. Sursa e alta, și e mai punctuală decât o balanță.

## Temeiul legal

::: ghid-temei
**Art. 325 din Codul fiscal (Legea 227/2015)** — obligația depunerii lunare a declarației recapitulative (D390), cu livrările intracomunitare scutite (lit. a) și achizițiile intracomunitare taxabile (lit. d).

**OMFP 1802/2014** — reglementările contabile, temeiul distincției dintre o notă contabilă validată și una în ciornă, folosită ca prag pentru „evidență" în verificarea D390.
:::

Verificarea D390 din aplicație pornește de la **facturile intracomunitare ale perioadei** și verifică, pentru fiecare, dacă are o **notă contabilă cu statusul „validată" legată de ea** — nu de la conturile de TVA sau de la orice alt cont din balanță. O căutare directă în codul care rulează acest control (facturi, note contabile pe factură) nu găsește nicio interogare pe solduri sau rulaje de cont.

Motivul pentru care contează distincția: balanța arată o cifră agregată, indiferent de sursă și de statutul fiecărei înregistrări. Verificarea D390 e mai fină — urmărește dacă operațiunea declarată la VIES are, sau nu, o notă validă în spate, factură cu factură, ceea ce poate arăta lucruri diferite decât o simplă comparație pe sold.

## Ce se greșește în practică

- Se caută în ecranul de control fiscal o corespondență directă cu soldul unui cont din balanță — nu există, pentru că verificarea nu citește balanța.
- Se presupune că un verde pe D390 confirmă și corectitudinea balanței — verdele confirmă doar că facturile intracomunitare declarate au notă validată în spate, nu starea generală a conturilor de TVA.
- Se ignoră faptul că o notă în ciornă, chiar dacă apare deja în rulajul contului din balanță, nu contează ca dovadă în acest control — trebuie să fie validată.

## Ce face iConta.eu

Pentru D390, aplicația verifică fiecare factură intracomunitară a perioadei față de existența unei note contabile validate legate de ea — nu rulează nicio comparație pe conturi sau solduri de balanță. E o verificare pe document, nu pe agregat contabil.

Dacă vrei o reconciliere pe conturi de TVA (colectată, deductibilă, sold de plată sau de recuperat) față de balanța contabilă, e o funcționalitate separată, cu logică proprie pe perechi de conturi — nu parte din controlul D390 descris aici.

[iConta.eu](/)
