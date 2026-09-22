---
title: Cum se înregistrează un extras de cont bancar?
description: Contabilizarea extrasului de cont urmează sensul lui — creditul e încasare, debitul e plată — cu monografia din OMFP 1802/2014 pentru fiecare tip de operațiune: clienți, furnizori, comisioane, dobânzi, credite, salarii, TVA.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum înregistrezi corect un extras de cont bancar?

Extrasul de cont e documentul băncii, nu al tău — regula de citire e fixă, indiferent de bancă: **creditul înseamnă bani care intră**, **debitul înseamnă bani care ies**. De aici pornește toată nota contabilă: fiecare linie de extras devine o notă cu contul de bancă (5121 lei, 5124 valută) pe una din părți, și contul corespunzător operațiunii pe cealaltă.

## Temeiul legal

::: ghid-temei
Conturile și monografiile pentru operațiunile de trezorerie sunt cele din **OMFP 1802/2014** (planul de conturi general, capitolul de conturi de trezorerie — clasa 5). Fiecare tip de operațiune bancară are contul lui de corespondență: încasare de la client (4111), plată către furnizor (401), comision bancar (627), dobândă (666 la plată/766 la încasare), rambursare sau tragere de credit (519), salarii virate (421), TVA plătită (4423), impozit pe profit plătit (4411).
:::

## Regula de citire

Pe extras, sensul e din perspectiva băncii, nu a firmei:

- **Credit pe extras** = bani intră în cont = încasare → în nota contabilă, banca (5121/5124) e pe debit
- **Debit pe extras** = bani ies din cont = plată → în nota contabilă, banca e pe credit

Tipul de operațiune se stabilește din descrierea liniei: o încasare de la un partener e normal `5121 = 4111` (stingere creanță client), o plată către un furnizor e `401 = 5121` (stingere datorie). Dar extrasul mai conține și operațiuni proprii băncii — comision (`627 = 5121`), dobândă încasată (`5121 = 766`) sau plătită (`666 = 5121`), rate de credit, salarii virate, TVA sau impozit pe profit plătite direct din cont — fiecare cu contul lui, nu cu 4111/401 implicit.

## Ce se greșește în practică

- **Se tratează orice încasare ca venit de la client** — o dobândă încasată, o restituire de TVA sau o tragere de credit nu sunt încasări de la clienți, chiar dacă apar tot ca linie de credit pe extras.
- **Se confundă impozitul pe profit cu alte impozite** — contul e 4411, nu 441 (grupa generică) sau alt cont de impozite și taxe.
- **Nu se identifică partenerul din descriere** — fără CUI-ul sau numele din textul liniei, încasarea/plata rămâne nealocată pe client/furnizor și denaturează soldurile de creanțe/datorii din balanță.

## Ce face iConta.eu

Fiecare linie de extras se clasifică automat după cuvinte-cheie din descriere (comision, dobândă, credit, salarii, impozit pe profit, TVA, operațiuni cu numerar) și, dacă nu se potrivește niciuna, e tratată implicit ca încasare de la client sau plată către furnizor, după sensul liniei. Din descriere se extrage și CUI-ul sau CIF-ul partenerului, când apare (format RO urmat de cifre, sau precedat explicit de „CUI"/„CIF"), pentru alocarea corectă a notei pe partenerul din nomenclator. Fiecare notă păstrează urma regulii care a generat-o, ca să poată fi verificată ulterior.

[iConta.eu](/)
