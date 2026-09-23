---
title: "Cum se declară dividendele compensate cu o datorie a asociatului?"
description: "Compensarea dividendului de plată cu o sumă datorată de asociat se face manual, în afara notelor generate automat de iConta."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se declară dividendele compensate cu o datorie a asociatului?

Când asociatul are deja o datorie față de firmă (de exemplu un sold debitor pe contul curent de asociat) și firma îi aprobă un dividend, e tentant să le „compensezi" direct, fără mișcare de bani. Contabil, asta se poate face, dar nu e o singură operațiune automată — sunt două note distincte care se leagă printr-o înregistrare manuală de compensare.

## Temeiul legal

::: ghid-temei
„Cota-parte din profit ce se plătește fiecărui asociat constituie dividend." — Legea 31/1990, art. 67 alin. (1)
:::

Dividendul aprobat se înregistrează ca datorie a firmei față de asociat (cont 457 „Dividende de plată", pentru cel anual, sau 456, pentru cel interimar). Sumele depuse sau datorate de asociat către firmă se țin separat, în contul 4551 „Acționari/asociați - conturi curente" (OMFP 1802/2014, pct. 349). Compensarea celor două solduri — dividendul de plătit (457/456, creditor pentru asociat) cu datoria asociatului (4551, debitor pentru asociat) — este o operațiune contabilă distinctă de simpla înregistrare a dividendului, pentru că pune față în față două conturi diferite.

## Ce se greșește în practică

Cea mai frecventă greșeală e tratarea compensării ca și cum ar fi parte din nota de dividend, și omiterea înregistrării separate a stingerii datoriei asociatului. A doua greșeală e confuzia dintre „declararea" fiscală a dividendului (care se face prin D205, o funcționalitate separată) și simpla lui înregistrare contabilă — compensarea nu schimbă regimul fiscal al dividendului, doar modul în care se stinge datoria.

## Ce face iConta.eu

iConta generează automat nota de dividend (repartizare + impozit, cu cota valabilă la data aprobării) și, separat, notele de împrumut/decontare cu asociatul (primire și restituire pe 4551). Motorul din spatele acestor note (`core/decontari_asociati.py`) nu are însă o funcție dedicată de compensare între dividendul de plată și datoria asociatului — cele două note se generează independent, iar stingerea reciprocă a soldurilor (457 = 4551) rămâne o notă contabilă manuală, în afara acestor patru funcții. Declararea fiscală a dividendului la D205 este o funcționalitate separată de decontările cu asociații.

[iConta.eu](/)
