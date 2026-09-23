---
title: Cum verific toate obligațiile fiscale care îmi expiră luna aceasta?
description: Ecranul Termene din iConta.eu listează scadențele cronologic, pe o fereastră de 60 de zile — nu are un filtru dedicat "luna aceasta", dar acoperă practic orice lună curentă din listă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum verific toate obligațiile fiscale care îmi expiră luna aceasta?

Ecranul „Termene" din iConta.eu nu are un buton separat „luna aceasta" — arată toate scadențele din următoarele 60 de zile, în ordine cronologică, grupate pe dată. Practic, tot ce expiră în luna curentă se regăsește la începutul acestei liste, pentru că fereastra de 60 de zile acoperă mereu întreaga lună curentă, plus o parte din luna următoare.

## Temeiul legal

::: ghid-temei
„până la data de 25 inclusiv a lunii următoare celei în care se încheie perioada fiscală"
— Codul fiscal, art. 323 alin. (1) (termenul D300)
:::

Fiecare declarație de pe listă își are termenul calculat din temeiul ei legal specific (D300 mai sus, D112 — art. 147 alin. (1), D406/SAF-T — ultima zi a lunii următoare, D101 — 25 iunie anul următor etc.) — ecranul nu recalculează nimic propriu, doar le pune cronologic pe aceeași listă.

## Cum citești lista pentru „luna aceasta"

1. Deschide ecranul „Termene" — grupurile sunt afișate în ordine cronologică, cu eticheta „azi", „mâine" sau „în N zile" la fiecare dată.
2. Citește lista de sus în jos până la prima dată din luna următoare — tot ce vine înainte e „luna aceasta".
3. Fiecare grup arată numărul de firme cu acea scadență (dacă administrezi mai multe firme) și tipul declarației; click pe grup deschide lista firmelor.

Pentru o firmă cu foarte multe scadențe apropiate, e util să ții cont și de eticheta de urgență: aplicația marchează vizual scadențele din următoarele 7 zile ca fiind mai presante.

## Ce nu arată această listă

- **Restanțele** — declarații cu termen deja depășit nu apar aici, indiferent de lună; ele se verifică pe „Semafor" (control fiscal).
- **Scadențele de peste 60 de zile** — dacă întrebarea vizează o lună mai îndepărtată (ex. luna viitoare, dincolo de fereastra curentă), acea parte a listei încă nu s-a populat; va apărea pe măsură ce data se apropie.

## Ce se greșește în practică

- Se caută un filtru sau un selector de lună care nu există — lista e strict cronologică, nu paginată pe luni.
- Se confundă absența unei scadențe din listă cu „nimic de depus luna asta", când de fapt firma poate fi pe lista de „neevaluate" (vector fiscal necompletat) — verifică mereu și acea secțiune.
- Se ignoră faptul că fereastra e mobilă (azi + 60 de zile): ce era „luna viitoare" acum două săptămâni poate deveni „luna aceasta" fără nicio acțiune din partea ta — lista se actualizează singură pe măsură ce trece timpul.

## Ce face iConta.eu

Motorul derivă declarațiile datorate din vectorul fiscal al fiecărei firme și din faptele înregistrate, le grupează pe (dată, tip) și le prezintă cronologic, într-o fereastră de 60 de zile — fără un filtru explicit „luna aceasta", dar cu toată informația necesară ca să-l aplici manual, citind lista de sus până la schimbarea de lună.

[iConta.eu](/)
