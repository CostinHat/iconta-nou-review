---
title: "Cum se înregistrează producția proprie într-o brutărie?"
description: "Notele contabile pentru obținerea produselor de panificație la cost standard, diferențele de preț pe contul 348 și vânzarea lor, conform OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează producția proprie într-o brutărie?

O brutărie nu cumpără marfă pentru revânzare — își fabrică produsul. Contabil, asta înseamnă că pâinea sau produsele de patiserie obținute la sfârșitul unui ciclu de producție intră în gestiune ca produse finite (cont 345), nu ca stoc de mărfuri (cont 371), iar veniturile din producția stocată (cont 711) apar înainte ca produsul să fie efectiv vândut clientului.

## Temeiul legal

::: ghid-temei
Reglementările contabile conforme cu directivele europene, aprobate prin OMFP 1802/2014, stabilesc funcționarea contului 345 „Produse finite" (evidența produselor finite, la cost de producție) în corespondență cu contul 711 „Venituri aferente costurilor stocurilor de produse", precum și a contului 348 „Diferențe de preț la produse" pentru diferența dintre costul standard (prestabilit) și costul efectiv de producție.
— OMFP 1802/2014, planul de conturi general și funcțiunea conturilor 345, 348, 711 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Fluxul contabil pentru o brutărie care lucrează la cost standard (metodă uzuală când costul efectiv se cunoaște abia la închiderea lunii) are trei momente:

- **obținerea produselor finite**, înregistrată la cost standard: `345 = 711`; dacă și costul efectiv e cunoscut, diferența se înregistrează separat pe contul 348 — nefavorabilă (efectiv > standard) prin `348 = 711`, favorabilă (efectiv < standard) prin `711 = 348`;
- **producția în curs de execuție**, pentru aluatul sau semifabricatele nefinalizate la închiderea lunii: constatare `331 = 711`, cu reluare la începutul lunii următoare `711 = 331`;
- **vânzarea**, care presupune atât recunoașterea venitului din vânzare (`4111 = 701` + TVA colectată), cât și descărcarea gestiunii la cost standard (`711 = 345`), cu repartizarea diferențelor de preț cumulate pe contul 348, aplicând coeficientul de repartizare calculat din soldurile și rulajele conturilor 348 și 345.

## Ce se greșește în practică

- Se înregistrează pâinea obținută direct ca marfă pe contul 371, tratând brutăria ca pe un magazin de revânzare — ceea ce falsifică atât gestiunea de stocuri, cât și costul de producție real.
- Se ignoră producția în curs de execuție la finalul lunii (aluatul dospit, dar necopt) — omisiune care denaturează rezultatul lunii în care se constată, pentru că o cheltuială de materie primă e deja înregistrată, dar venitul din producția stocată aferentă nu.
- Se aplică diferența de preț (cont 348) direct și integral la obținere, fără coeficient de repartizare pe ieșiri — ceea ce duce fie la subevaluarea, fie la supraevaluarea costului mărfii vândute la momentul descărcării de gestiune.

## Ce face iConta.eu

iConta.eu are un modul dedicat producției proprii, care generează exact notele descrise mai sus, potrivit OMFP 1802/2014: obținerea produselor finite la cost standard cu diferențe pe contul 348, constatarea și reluarea producției în curs de execuție (cont 331) și vânzarea cu descărcare de gestiune la cost standard plus repartizarea diferențelor de preț prin coeficientul K calculat din soldurile și intrările reale ale conturilor 348 și 345. Contabilul introduce costul standard, costul efectiv (când e cunoscut) și prețul de vânzare; aplicația propune notele ca ciornă, iar validarea rămâne a contabilului.

[iConta.eu](/)
