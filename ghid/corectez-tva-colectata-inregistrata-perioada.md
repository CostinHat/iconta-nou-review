---
title: "Cum corectez TVA colectată înregistrată în perioada greșită?"
description: TVA colectată înregistrată în perioada fiscală greșită se corectează prin decontul unei perioade ulterioare, la rândurile de regularizări — același mecanism ca la TVA deductibilă, prevăzut explicit de Codul fiscal pentru decontul de TVA.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez TVA colectată înregistrată în perioada greșită?

La fel ca la TVA deductibilă, o TVA colectată înregistrată în perioada fiscală greșită nu se corectează printr-o rectificativă care înlocuiește decontul greșit — se corectează prin decontul unei perioade ulterioare, la rândurile de regularizări.

## Temeiul legal

::: ghid-temei
**Art. 323 alin. (3) Cod fiscal (Legea 227/2015):** *„Datele înscrise incorect într-un decont de taxă se pot corecta prin decontul unei perioade fiscale ulterioare şi se vor înscrie la rândurile de regularizări."*

**Art. 105 alin. (4) Cod de procedură fiscală (Legea 207/2015):** *„... în cazul taxei pe valoarea adăugată, corectarea erorilor din deconturile de taxă se realizează potrivit prevederilor Codului fiscal [art. 323 alin. (3)]. Erorile materiale din decontul de TVA se corectează potrivit procedurii aprobate prin ordin al preşedintelui A.N.A.F."*
:::

## Mecanismul corect

Dacă ai colectat TVA într-o altă perioadă decât cea corectă (de exemplu, ai raportat colectarea unei livrări în luna următoare celei în care a avut loc de fapt faptul generator), corecția se face prin decontul unei perioade ulterioare celei greșite, la rândurile de regularizări — nu prin rectificarea directă a decontului deja depus.

Diferența față de TVA deductibilă e doar sensul erorii (taxă colectată în plus/minus, nu taxă dedusă), dar mecanismul legal de corecție e identic — art. 323 alin. (3) nu face distincție între cele două tipuri de eroare.

Ca și la deductibilă, dacă eroarea e strict materială (fără impact asupra sumei datorate), corecția urmează procedura separată aprobată prin ordin ANAF, nu rândurile de regularizări.

## Ce se greșește în practică

- **Se presupune că TVA colectată în plus/minus se corectează diferit de TVA deductibilă** — mecanismul legal (art. 323 alin. (3)) e unul singur, pentru orice dată înscrisă incorect în decont.
- **Se editează retroactiv decontul perioadei greșite**, în loc să se introducă regularizarea în decontul curent — corecția aparține perioadei în care se descoperă eroarea, nu perioadei în care s-a produs.
- **Se ignoră eroarea dacă suma e mică**, considerând-o nesemnificativă — legea nu prevede un prag valoric sub care corecția nu ar mai fi necesară.

## Ce face iConta.eu

Regularizările de TVA colectată se introduc din același panou manual dedicat corecțiilor (`core/d300_manual_api.py`), alături de intracomunitar și taxare inversă, cu recalcularea automată a decontului după fiecare modificare (buton „Regenerează D300"). Aplicația nu decide automat dacă o eroare e „materială" sau de fond — încadrarea rămâne o decizie a contabilului.

[iConta.eu](/)
