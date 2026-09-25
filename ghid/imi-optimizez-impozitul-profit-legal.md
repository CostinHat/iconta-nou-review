---
title: "Cum îmi optimizez impozitul pe profit legal în 2026"
description: "Două pârghii prevăzute explicit de Codul fiscal pentru reducerea legală a impozitului pe profit: rezerva legală și creditul fiscal pentru sponsorizare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum îmi optimizez impozitul pe profit legal în 2026

„Optimizarea" impozitului pe profit nu înseamnă evitarea lui, ci folosirea mecanismelor pe care legea le prevede explicit pentru a reduce baza impozabilă sau chiar impozitul final datorat. Codul fiscal oferă câteva pârghii clare, nu interpretări la limită — rezerva legală și creditul fiscal pentru sponsorizare sunt printre cele mai directe.

## Temeiul legal

::: ghid-temei
„Contribuabilul are dreptul la deducerea rezervelor și provizioanelor/ajustărilor pentru depreciere, numai în conformitate cu prezentul articol, astfel: a) rezerva legală este deductibilă în limita unei cote de 5% aplicate asupra profitului contabil, la care se adaugă cheltuielile cu impozitul pe profit, până ce aceasta va atinge a cincea parte din capitalul social subscris și vărsat sau din patrimoniu, după caz."
— Codul fiscal (Legea 227/2015), art. 26 alin. (1) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„cheltuielile de sponsorizare și/sau mecenat, acordate potrivit legii; contribuabilii care efectuează sponsorizări și/sau acte de mecenat, potrivit prevederilor Legii nr. 32/1994 privind sponsorizarea, [...] scad sumele aferente din impozitul pe profit datorat la nivelul valorii minime dintre următoarele: 1. valoarea calculată prin aplicarea a 0,75% la cifra de afaceri; [...] 2. valoarea reprezentând 20% din impozitul pe profit datorat."
— Codul fiscal (Legea 227/2015), art. 25 alin. (4) lit. i) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă concret cele două pârghii:

- **Rezerva legală**: firma poate deduce fiscal, an de an, o sumă egală cu 5% din profitul contabil (plus cheltuiala cu impozitul pe profit), constituind rezerva legală — până când aceasta ajunge la o cincime din capitalul social subscris și vărsat. E o deducere reală, nu doar contabilă, atâta timp cât rezerva nu depășește pragul legal.
- **Sponsorizarea/mecenatul**: sumele destinate sponsorizării, conform Legii 32/1994, nu sunt doar o cheltuială deductibilă oarecare — se **scad direct din impozitul datorat** (credit fiscal), în limita minimului dintre 0,75% din cifra de afaceri și 20% din impozitul pe profit. Practic, o parte din impozitul care oricum s-ar plăti poate fi direcționată, în limitele legale, către o cauză aleasă de firmă, în loc să ajungă integral la buget.
- Ambele mecanisme funcționează doar în limitele stabilite prin lege — depășirea plafoanelor nu generează deducere/credit suplimentar, ci pur și simplu cheltuială/sponsorizare nedeductibilă peste prag.

## Ce se greșește în practică

- Se constituie rezerva legală peste pragul de 20% din capitalul social (a cincea parte), fără să se observe că deducerea fiscală se oprește la acest prag — sumele peste prag nu mai aduc niciun beneficiu fiscal.
- Se calculează plafonul de sponsorizare doar din impozitul pe profit, ignorând testul dublu — legea cere minimul dintre 0,75% din cifra de afaceri și 20% din impozitul pe profit, nu doar unul dintre cele două.
- Se tratează sponsorizarea ca simplă cheltuială deductibilă (care reduce baza impozabilă), când de fapt regimul ei e mai avantajos — se scade direct din impozitul de plată, ca un credit fiscal.
- Se ignoră condiția ca rezerva legală, odată redusă sau anulată (de exemplu, prin distribuire către asociați), devine venit impozabil — „optimizarea" nu e permanentă dacă rezerva e ulterior desfăcută.

## Ce face iConta.eu

iConta.eu are un modul dedicat (`core/sponsorizari.py`) care calculează exact acest plafon: creditul fiscal pentru sponsorizare, ca minim dintre 0,75% din cifra de afaceri și 20% din impozitul pe profit datorat, cu istoricul de reguli aplicat corect pe perioadă (inclusiv regimul special de micro-sponsorizare valabil între 2019 și 2023). Nu am găsit însă, în modulele verificate, o funcție separată care să calculeze automat plafonul de deducere a rezervei legale (5% din profitul contabil, limitat la a cincea parte din capitalul social) — acest calcul rămâne, la acest moment, în sarcina contabilului.

[iConta.eu](/)
