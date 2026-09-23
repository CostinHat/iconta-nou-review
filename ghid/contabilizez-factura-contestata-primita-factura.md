---
title: Cum contabilizez o factură contestată primită prin e-Factura?
description: Aplicația nu are un status „contestată” — are „respinsă”, cu motiv obligatoriu, dar respingerea e o acțiune pur internă, care nu comunică obiecția către emitent prin sistemul RO e-Factura.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum contabilizez o factură contestată primită prin e-Factura?

Aici merită clarificat întâi ce înseamnă „contestată” — pentru că legea și aplicația folosesc concepte apropiate, dar nu identice, iar confuzia poate crea impresia greșită că un click în iConta rezolvă și partea legală față de furnizor.

## Temeiul legal

::: ghid-temei
„În situaţia unei facturi electronice asupra căreia destinatarul are obiecţii, acesta înştiinţează emitentul facturii electronice, inclusiv în sistemul naţional privind factura electronică RO e-Factura, prin înscrierea unui mesaj în acest sens."

— OUG nr. 120/2021, art. 4 alin. (9)
:::

Legea prevede explicit mecanismul: dacă ai obiecții asupra unei facturi primite, îl înștiințezi pe emitent — **inclusiv prin înscrierea unui mesaj chiar în sistemul RO e-Factura**. E un pas formal, care produce efecte în sistemul ANAF, vizibil și emitentului.

## Ce nu face aplicația, și trebuie știut clar

La acest moment, iConta **nu implementează** înscrierea acestui mesaj de obiecție în sistemul RO e-Factura. Nu există nicio comunicare automată către ANAF sau către emitent atunci când respingi o factură din aplicație. Ce există e o funcție locală, de uz intern: poți respinge o factură primită, cu un motiv obligatoriu de completat — dar respingerea rămâne strict în evidența ta, nu produce niciun efect în sistemul SPV.

Cu alte cuvinte: „respinge” din iConta ≠ „contestare”/„obiecție” din lege. Sunt lucruri diferite, chiar dacă vorbesc despre aceeași situație practică (o factură cu care nu ești de acord).

## Ce faci, concret

Dacă ai obiecții reale față de o factură primită prin e-Factura, obiecția formală — cea cu efect legal față de emitent — trebuie transmisă separat, prin canalul prevăzut de lege (mesaj în sistemul RO e-Factura, prin mijloacele puse la dispoziție de ANAF), nu doar prin acțiunea din aplicație.

În paralel, în iConta poți respinge rândul respectiv (cu motivul obiecției consemnat), ca să nu rămână la nesfârșit în lista de „facturi de validat” — rândul respins nu se șterge, rămâne în istoric, cu motivul vizibil. Nu poți respinge o factură deja validată.

Dacă furnizorul corectează factura și o retransmite, corecția urmează procedura obișnuită de corecție a facturii electronice comunicate (art. 4 alin. (10) OUG 120/2021, care trimite la art. 330 din Codul fiscal) și se retransmite prin același sistem — noua versiune va ajunge, la rândul ei, ca un nou mesaj în lista ta de facturi de validat.

## Ce se greșește în practică

- Se folosește „respinge” din aplicație crezând că asta echivalează cu obiecția legală transmisă emitentului prin SPV — nu e cazul, e o acțiune pur internă.
- Se lasă factura contestată nerespinsă și nevalidată la nesfârșit, în loc de a o respinge cu motiv, ca să nu rămână ambiguă în lista de validat.
- Se validează factura „ca să dispară din listă”, deși există obiecții reale asupra ei — validarea creează deja o cheltuială contabilizată, greu de anulat curat ulterior.

## Ce face iConta.eu

Local, aplicația oferă un mecanism de respingere, cu motiv obligatoriu și istoric păstrat — util pentru gestiunea internă a facturilor cu care nu ești de acord. Nu există, verificat direct în cod, niciun status de „contestată” și nicio funcție care să scrie mesajul de obiecție înapoi în sistemul RO e-Factura — acel pas, prevăzut de lege, rămâne în afara aplicației, de făcut separat, direct în sistemul ANAF sau prin comunicare directă cu furnizorul.

[iConta.eu](/)
