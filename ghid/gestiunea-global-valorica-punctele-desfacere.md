---
title: Gestiunea global-valorică la punctele de desfacere
description: Legea permite calculul coeficientului de adaos la nivel de conturi sintetice, pe grupe sau categorii de stocuri — deci și separat pe puncte de desfacere; iConta, la data acestei verificări, calculează descărcarea la nivel de firmă/schemă, fără un parametru dedicat de punct de lucru.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Gestiunea global-valorică la punctele de desfacere

O firmă cu mai multe puncte de desfacere (magazine, chioșcuri, puncte de lucru) se poate confrunta cu o întrebare practică: se calculează un singur coeficient de adaos pentru toată firma, sau unul separat pentru fiecare punct de desfacere? Legea permite ambele variante — alegerea concretă depinde de cum organizați gestiunile, nu de o regulă unică obligatorie.

## Temeiul legal

::: ghid-temei
„(5) Coeficienții de repartizare a diferențelor de preț pot fi calculați la nivelul conturilor sintetice de gradul I și II, prevăzute în Planul de conturi general, pe grupe sau categorii de stocuri.”

— *OMFP 1802/2014, pct. 286 alin. (5).*
:::

## Ce înseamnă, în practică

Legea nu impune un coeficient unic la nivel de firmă — permite explicit calculul separat, pe grupe sau categorii de stocuri, care poate corespunde, funcțional, fiecărui punct de desfacere (dacă fiecare punct are propria gestiune, cu conturi analitice distincte de 371/378/4428). Alegerea concretă e organizatorică: dacă punctele de desfacere au marje și sortimente similare, un coeficient unic la nivel de firmă e suficient și mai simplu de administrat; dacă marjele diferă semnificativ între puncte (de exemplu, un magazin cu produse de bază și unul cu produse premium), un coeficient separat pe fiecare punct dă o imagine mai corectă a adaosului real.

Pentru a calcula separat pe puncte de desfacere, e nevoie de conturi analitice distincte (371.1, 371.2 etc., sau echivalent) pentru fiecare gestiune, cu solduri și rulaje ținute separat — altfel calculul revine, implicit, la un singur coeficient global.

## Ce se greșește în practică

- Se presupune că legea impune obligatoriu un coeficient unic pe firmă — alin. (5) permite explicit calculul pe grupe/categorii, deci și pe puncte de desfacere separate.
- Se calculează manual coeficienți separați pe puncte de desfacere, dar se introduc datele într-o singură gestiune contabilă nediferențiată — rezultatul nu mai corespunde cu ce arată soldurile reale din contabilitate.
- Se schimbă, în cursul anului, de la coeficient unic la coeficienți separați pe puncte (sau invers) fără o organizare analitică clară dinainte — asta rupe continuitatea calculului cumulat de la 1 ianuarie.

## Ce face iConta.eu

`core/stocuri_api.py`, funcția `descarca_luna(conn, schema, an, luna)`, calculează descărcarea de gestiune **la nivel de firmă/schemă** — nu am găsit, în cod, niciun parametru de „gestiune”, „punct de lucru” sau „locație” care să permită rularea calculului separat, pe fiecare punct de desfacere. Motorul citește soldurile și rulajele conturilor 371/378/4428 global, pentru întreaga schemă a tenantului, nu filtrate pe o subgestiune.

Dacă firma dvs. operează mai multe puncte de desfacere și dorește coeficienți de adaos separați pentru fiecare, conform alin. (5), acest calcul nu e susținut momentan ca funcționalitate dedicată în iConta — rămâne de organizat manual, în afara aplicației, sau de discutat cu privire la structura de conturi analitice folosită.

[iConta.eu](/)
