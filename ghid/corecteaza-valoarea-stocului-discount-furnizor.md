---
title: "Cum se corectează valoarea stocului după un discount de la furnizor?"
description: "Ce prevede OMFP 1802/2014 despre corectarea costului stocurilor la primirea unei reduceri comerciale ulterioare facturării, în funcție de starea gestiunii."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se corectează valoarea stocului după un discount de la furnizor?

Un discount (reducere comercială) primit de la furnizor după emiterea facturii inițiale nu se contabilizează la fel indiferent de situație — legea contabilă face o distincție clară după cum marfa mai e sau nu în gestiune la momentul primirii reducerii.

## Temeiul legal

::: ghid-temei
„76. [...] (2) Reducerile comerciale primite ulterior facturării corectează costul stocurilor la care se referă, dacă acestea mai sunt în gestiune. Dacă stocurile pentru care au fost primite reducerile ulterioare nu mai sunt în gestiune, acestea se evidențiază distinct în contabilitate (contul 609 "Reduceri comerciale primite"), pe seama conturilor de terți. (2^1) În cazul în care informațiile deținute nu permit corectarea valorii stocurilor, potrivit alin. (2), reducerile menționate la acel alineat se reflectă, de asemenea, pe seama contului 609 "Reduceri comerciale primite"."
— OMFP 1802/2014, pct. 76 alin. (2) și (2^1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Regula, tradusă în pași:

- **Marfa încă în gestiune** — reducerea comercială primită ulterior **corectează direct costul stocului** la care se referă. Nu se înregistrează venit, ci se scade costul de achiziție înregistrat.
- **Marfa nu mai e în gestiune** (a fost deja vândută/consumată) — reducerea se evidențiază distinct, pe **contul 609 „Reduceri comerciale primite"** (cont cu funcție de pasiv, singurul din clasa 6 tratat astfel), pe seama conturilor de terți, nu prin corectarea unui stoc inexistent.
- **Dacă nu se poate stabili** ce parte din stoc mai e în gestiune (informație insuficientă), tot pe contul 609 se reflectă reducerea — legea rezolvă explicit și cazul de incertitudine.
- Pentru prestările de servicii, regula e alta, nu o extensie a distincției de mai sus: pct. 76 alin. (5) prevede că reducerile comerciale legate de servicii, primite (sau acordate) ulterior facturării, se evidențiază **întotdeauna** distinct, pe contul 609/709, indiferent de perioada la care se referă — nu se pune problema corectării unui „cost de stoc", pentru că serviciile nu se gestionează ca stoc.

## Ce se greșește în practică

- Se înregistrează întotdeauna discountul ca venit (cont 758) sau ca reducere directă a costului de achiziție, fără să se verifice mai întâi dacă marfa respectivă mai e în gestiune.
- Se ignoră distincția dintre reduceri comerciale (rabaturi, remize, risturne — cont 609/709) și reduceri financiare (sconturi de decontare — cont 767/667), tratându-le identic, deși au regim contabil diferit.
- Se omite corelarea cu evenimentele ulterioare datei bilanțului, când discountul e constatat după închiderea exercițiului financiar la care se referă stocul.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un modul dedicat de corectare automată a costului stocurilor** la primirea unei reduceri comerciale ulterioare de la furnizor — distincția „marfă încă în gestiune vs. marfă ieșită din gestiune" din OMFP 1802/2014 pct. 76 nu e implementată ca verificare automată. Înregistrarea corectă (pe cost sau pe contul 609) rămâne o decizie a contabilului, la introducerea notei contabile.

[iConta.eu](/)
