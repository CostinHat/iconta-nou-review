---
title: "Cum se facturează diferența finală pentru un eveniment după avansurile deja încasate?"
description: "Cum se regularizează în contabilitate avansurile încasate pentru un eveniment, înainte de emiterea facturii finale pentru diferența rămasă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se facturează diferența finală pentru un eveniment după avansurile deja încasate?

Dacă ai încasat unul sau mai multe avansuri pentru un eveniment, factura finală nu se emite izolat — soldul avansurilor deja înregistrat în contul 419 trebuie mai întâi regularizat, iar factura finală acoperă doar diferența rămasă de încasat.

## Temeiul legal

::: ghid-temei
„Contul 419 «Clienți ‐ creditori» […] Cu ajutorul acestui cont se ține evidența clienților ‐ creditori, reprezentând avansurile încasate de la clienți. Contul 419 «Clienți ‐ creditori» este un cont de pasiv. În creditul contului 419 […] se înregistrează: ‐ sumele facturate clienților reprezentând avansuri pentru livrări de bunuri sau prestări de servicii (411); […] În debitul contului 419 […] se înregistrează: ‐ decontarea avansurilor încasate de la clienți (411)” — OMFP 1802/2014
:::

La încasarea avansului, nota generată este 4111 = 419 + 4427 (TVA colectată devine exigibilă la data încasării). La factura finală, avansul se regularizează prin nota inversă: 419 = 4111, 4427 = 4111 — abia apoi diferența rămasă se facturează prin motorul general de facturare.

## Ce se greșește în practică

Greșeala tipică: emiterea facturii finale pe toată valoarea evenimentului, fără a regulariza mai întâi soldul din contul 419 — situație care dublează TVA colectată sau lasă un sold fantomă de avans neregularizat în evidență.

## Ce face iConta.eu

iConta generează separat cele două note: la încasarea fiecărui avans, 4111 = 419 + 4427; la factura finală, regularizarea inversează soldul avansului (419 = 4111, 4427 = 4111), iar diferența rămasă se facturează separat, prin motorul general de facturare. Atenție: dacă emiți factura de avans și factura finală prin e-Factura, iConta nu leagă automat, în documentul UBL transmis la SPV, cele două facturi între ele (nu se generează o referință de tip „factură anterioară”) — se transmit independent, iar regularizarea contabilă a avansului rămâne un pas separat.

[iConta.eu](/)
