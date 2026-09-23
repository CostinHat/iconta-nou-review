---
title: "Cum se descarcă gestiunea la vânzarea mărfurilor?"
description: Mecanismul depinde de metoda de gestiune a firmei — cantitativ-valorică (poartă la emiterea facturii) sau global-valorică (descărcare lunară, pe coeficient).
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se descarcă gestiunea la vânzarea mărfurilor?

Răspunsul depinde de metoda de gestiune folosită de firmă. La gestiunea cantitativ-valorică (articole cu cost pe unitate, tipic pentru firme cu stoc de produse identificabile), descărcarea se face la emiterea facturii, prin confirmarea explicită "pleacă marfa acum? DA/NU" — doar răspunsul afirmativ scade marfa din stoc, legat de factura respectivă. La gestiunea global-valorică (metoda prețului cu amănuntul, tipică pentru comerțul cu amănuntul cu preț de raft), acest mecanism nu există — descărcarea rămâne lunară, calculată global, pe baza coeficientului de repartizare a adaosului comercial.

## Temeiul legal

::: ghid-temei
"286. - (1) În funcție de specificul activității, pentru determinarea costului pot fi folosite, de asemenea, metoda costului standard, în activitatea de producție sau metoda prețului cu amănuntul, în comerțul cu amănuntul. ... (8) În comerțul cu amănuntul poate fi utilizată metoda prețului cu amănuntul, pentru a determina costul stocurilor de articole numeroase și cu mișcare rapidă, care au marje similare și pentru care nu este practic să se folosească altă metodă. În această situație, costul bunurilor vândute se calculează prin deducerea valorii marjei brute din prețul de vânzare al stocurilor."
— OMFP 1802/2014, pct. 286 alin. (1) și (8)
:::

Legea permite explicit metoda prețului cu amănuntul (global-valorică) ca alternativă, pentru comerțul cu amănuntul — de aceea cele două metode coexistă în practică și au mecanisme de descărcare diferite: una legată de fiecare factură individuală, cealaltă calculată global, periodic.

## Ce se greșește în practică

- Se caută poarta "pleacă marfa acum?" la un magazin cu preț de raft (gestiune global-valorică) — acolo poarta nu apare niciodată; descărcarea rămâne cea lunară.
- Se presupune că descărcarea la gestiunea cantitativ-valorică e automată, la orice factură — se descarcă doar dacă factura are linii legate de articole de stoc și se confirmă explicit că marfa pleacă.
- Se confundă cele două metode ca fiind interschimbabile în documentație — metoda folosită e o caracteristică a firmei, nu o alegere la fiecare vânzare.

## Ce face iConta.eu

La firmele cu gestiune cantitativ-valorică, iConta.eu pune o poartă obligatorie la emiterea fiecărei facturi cu cel puțin o linie legată de un articol de stoc: "pleacă marfa acum?". Răspunsul afirmativ descarcă automat gestiunea, în aceeași operațiune cu emiterea facturii, folosind același motor de descărcare ca și mișcările manuale de stoc, cu mișcarea legată explicit de factura respectivă. La firmele cu gestiune global-valorică, această poartă nu apare — descărcarea rămâne mecanismul lunar existent, pe coeficient de repartizare a adaosului, neschimbat.

Menționăm onest: firmele de pe portalul client (fără gestiune de stoc activată) nu văd niciodată această poartă — emiterea rămâne identică cu fluxul dinaintea introducerii ei.

[iConta.eu](/)
