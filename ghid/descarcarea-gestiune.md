---
title: "Când se face descărcarea de gestiune?"
description: La firmele cu gestiune cantitativ-valorică, descărcarea se face la emiterea facturii, doar dacă se confirmă explicit că marfa pleacă atunci — nu automat, la orice factură cu articole.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Când se face descărcarea de gestiune?

Momentul depinde de metoda de gestiune a firmei. La o firmă cu gestiune cantitativ-valorică (articole cu cost pe unitate), descărcarea se poate face chiar la emiterea facturii — dar nu automat: la fiecare factură cu cel puțin o linie de articol se cere o confirmare explicită, "pleacă marfa acum?". Doar răspunsul afirmativ declanșează descărcarea, în același moment cu emiterea facturii. La o firmă pe metoda global-valorică (preț de raft, marjă comercială), acest mecanism nu se aplică deloc — descărcarea rămâne cea lunară, calculată pe baza coeficientului de repartizare a adaosului.

## Temeiul legal

::: ghid-temei
"441. - (1) Veniturile din vânzarea bunurilor se recunosc în momentul în care sunt îndeplinite următoarele condiții: a) entitatea a transferat cumpărătorului riscurile şi avantajele semnificative care decurg din proprietatea asupra bunurilor; ... (2) Evaluarea momentului în care o entitate a transferat cumpărătorului riscurile şi avantajele semnificative aferente dreptului de proprietate asupra bunurilor impune o examinare a circumstanţelor în care s-a desfăşurat tranzacţia. În cele mai multe cazuri, transferul riscurilor şi avantajelor aferente dreptului de proprietate coincide cu transferul titlului legal de proprietate sau cu trecerea bunurilor în posesia cumpărătorului."
— OMFP 1802/2014, pct. 441 alin. (1)-(2)
:::

Legea nu fixează un moment unic, universal — leagă recunoașterea vânzării (și, implicit, ieșirea mărfii din gestiune) de transferul efectiv al riscurilor și avantajelor asupra bunului. În cele mai multe cazuri acesta coincide cu predarea mărfii, care poate să fie chiar momentul facturii sau un moment ulterior. Întrebarea "pleacă marfa acum?" e felul în care se traduce, în practică, la fiecare factură, exact acest criteriu legal.

## Ce se greșește în practică

- Se presupune că orice factură cu marfă descarcă automat gestiunea, indiferent de răspunsul dat la poartă — descărcarea se face doar dacă se răspunde afirmativ; la răspunsul negativ, factura rămâne pur fiscală, stocul nemodificat.
- Se așteaptă poarta și la o firmă pe metoda global-valorică — acolo nu apare deloc; descărcarea rămâne cea lunară, existentă dinainte.
- Se așteaptă poarta la proforme sau avize — se activează doar la emiterea facturii propriu-zise, nu și la celelalte tipuri de document.

## Ce face iConta.eu

La emiterea unei facturi, dacă firma are gestiune cantitativ-valorică și factura conține cel puțin o linie legată de un articol de stoc, aplicația cere obligatoriu un răspuns: marfa pleacă acum sau nu. La răspunsul afirmativ, gestiunea se descarcă în aceeași operațiune cu emiterea facturii (mișcare de stoc legată de factură, verificare pe patru ochi păstrată prin nota contabilă rămasă ciornă). La răspunsul negativ, factura rămâne pur fiscală, iar stocul nu se modifică la acel moment.

Menționăm onest: la firmele pe metoda global-valorică, această poartă nu apare — descărcarea rămâne cea lunară existentă, pe coeficient de repartizare, nelegată de emiterea facturilor individuale.

[iConta.eu](/)
