---
title: Cum se contabilizează tips-ul plătit cu cardul separat de nota de consum?
description: Chiar plătit separat de consumație, printr-o tranzacție de card distinctă, bacșișul urmează același traseu contabil ca cel inclus pe bon.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se contabilizează tips-ul plătit cu cardul separat de nota de consum?

Faptul că bacșișul e plătit printr-o tranzacție de card separată de plata consumației — de exemplu, clientul achită nota, apoi mai trece cardul o dată pentru bacșiș — nu schimbă tratamentul contabil sau fiscal. Legea cere doar ca bacșișul să fie evidențiat distinct pe bonul fiscal, indiferent de câte tranzacții de plată presupune.

## Temeiul legal

::: ghid-temei
„Sumele provenite din încasarea bacșișului se înregistrează în contabilitatea operatorilor economici pe seama conturilor de datorii folosind un analitic distinct și se distribuie integral salariaților, pe baza unei evidențe nominale a acestora. Operatorii economici stabilesc, printr-un regulament intern, procedura și modalitatea de distribuire..."

*(Legea nr. 376/2022 pentru modificarea și completarea OUG nr. 28/1999, art. 2^3 alin. (8))*
:::

## Fluxul de înregistrare

Indiferent dacă tranzacția de card pentru bacșiș e separată de cea pentru consumație, încasarea urmează același traseu: `461 = 462` (creanța internă pentru bacșișul de distribuit), apoi `5121 = 461` (încasarea efectivă prin card). Faptul că sunt două chitanțe/tranzacții POS diferite nu creează două trasee contabile diferite — ambele sume ale bacșișului, indiferent de câte tranzacții, se cumulează pe același analitic distinct de datorii.

La distribuire, procedura e identică: `462 = 446` (impozitul de 10% reținut la sursă) și `462 = 5121/5311` (netul plătit salariatului).

## Ce se greșește în practică

- **Bacșișul plătit separat, printr-o a doua tranzacție de card, e confundat cu o încasare suplimentară de venit** (de exemplu un produs vândut în plus), pentru că nu apare pe bonul fiscal inițial al consumației.
- **Se omite evidențierea lui pe bonul fiscal** doar pentru că a fost plătit separat — obligația de evidențiere de la alin. (2) se aplică indiferent de momentul sau modul plății.

## Ce face iConta.eu

Funcția `nota_incasare(bacsis, sursa="card")` din modulul F010 (`core/bacsis.py`) tratează fiecare încasare de bacșiș ca operațiune de sine stătătoare, indiferent dacă a fost plătită împreună cu consumația sau separat — nota generată e mereu `461=462` + `5121=461`, niciodată legată de altă tranzacție. Respinge orice sumă mai mică sau egală cu zero, cu mesaj dedicat.

[iConta.eu](/)
