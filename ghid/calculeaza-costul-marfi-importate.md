---
title: "Cum se calculează costul unei mărfi importate?"
description: Costul unei mărfi importate se compune din prețul plătit furnizorului extern, taxele vamale nerecuperabile și transportul direct atribuibil achiziției, capitalizate împreună proporțional pe articolele intrării în gestiune.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se calculează costul unei mărfi importate?

Calculul are, în practică, doi pași separați: mai întâi se determină taxa vamală datorată la import, apoi se capitalizează, împreună cu transportul, în costul de achiziție al articolelor din nota de intrare-recepție.

## Temeiul legal

::: ghid-temei
OMFP 1802/2014, Secțiunea 1.2, pct. 6: „costul de achiziție al bunurilor cuprinde prețul de cumpărare, taxele de import și alte taxe (cu excepția acelora pe care persoana juridică le poate recupera de la autoritățile fiscale), cheltuielile de transport, manipulare și alte cheltuieli care pot fi atribuibile direct achiziției bunurilor respective."
:::

Costul de achiziție al unei mărfi importate = prețul de cumpărare (valoarea facturată de furnizorul extern) + taxele vamale nerecuperabile + cheltuielile de transport/manipulare direct atribuibile + alte cheltuieli directe (comisioane de intermediere la achiziție, de exemplu). Un exemplu simplificat, cu mecanica de repartizare confirmată prin teste: două articole cu cost de bază egal (100 lei fiecare), plus transport 10 lei și taxe vamale 10 lei — fiecare articol primește un accesoriu de 10 lei (repartizat proporțional cu costul de bază egal), costul final ajunge la 110 lei/articol, iar costul total al intrării e 220 lei, față de 200 lei fără capitalizarea accesoriilor.

## Ce se greșește în practică

- Se ia în calcul doar prețul facturat de furnizorul extern, fără taxele vamale sau transportul, subevaluând costul real al mărfii și, implicit, adaosul comercial calculat la vânzare.
- Se vinde marfa la un preț care acoperă doar costul de bază (fără accesorii), riscând să fie sub costul real de achiziție — aplicația blochează explicit o vânzare sub costul de achiziție care include accesoriile capitalizate.
- Se confundă baza de calcul a TVA la import (Codul fiscal, art. 289 — valoare în vamă + taxe + accize + cheltuieli accesorii) cu costul de achiziție contabil — elementele se suprapun parțial, dar scopurile sunt diferite.

## Ce face iConta.eu

Fluxul complet presupune doi pași: calculul taxei vamale și al bazei de TVA la import, în ecranul dedicat importului extracomunitar, apoi introducerea taxei vamale calculate ca parametru „taxe" (alături de transport) în ecranul NIR, unde costul de bază al fiecărui articol e majorat automat, proporțional, cu accesoriile — cu restul de rotunjire pe ultima linie, ca suma repartizată să fie exact egală cu accesoriul introdus. Prețul de vânzare e verificat automat față de costul majorat: o vânzare sub cost (incluzând accesoriile) e respinsă explicit. Acest mecanism funcționează doar pentru firmele care țin gestiunea global-valoric — pentru gestiunea cantitativ-valorică (CMP), tipică la comerțul en-gros, capitalizarea automată nu există, iar contabilul calculează manual costul pe articol.

[iConta.eu](/)
