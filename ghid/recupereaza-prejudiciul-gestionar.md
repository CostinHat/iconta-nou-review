---
title: "Cum se recuperează prejudiciul de la gestionar"
description: "Cum se înregistrează în contabilitate imputarea unei lipse de inventar către gestionarul sau salariatul vinovat, inclusiv TVA aferentă valorii de imputare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se recuperează prejudiciul de la gestionar

Când comisia de inventariere constată o lipsă în gestiune și stabilește o persoană vinovată (gestionar, alt salariat sau un terț), lipsa nu rămâne o simplă cheltuială — ea se **impută**, adică se transformă într-o creanță față de persoana respectivă.

## Temeiul legal

::: ghid-temei
"Rezultatul inventarierii se înregistrează în contabilitate potrivit reglementărilor contabile aplicabile." — Legea contabilității nr. 82/1991 (republicată), art. 7 alin. (3)
:::

Stabilirea persoanei vinovate se face de comisia de inventariere, numită prin decizie scrisă (OMFP 2861/2009, Anexa 1, pct. 6), care consemnează concluziile în procesul-verbal de inventariere.

Din punct de vedere contabil, o lipsă **imputabilă** presupune două note distincte:
- descărcarea de gestiune a bunului lipsă, pe valoarea lui contabilă;
- înregistrarea creanței de recuperat, la **valoarea de imputare** (nu neapărat egală cu valoarea contabilă), pe seama contului 4282 dacă vinovatul este salariat, respectiv 461 dacă este un terț — cu venit corespunzător în contul 7581;
- TVA colectată suplimentar (4427), calculată pe valoarea de imputare, dacă operațiunea e asimilată unei livrări.

## Ce se greșește în practică

- Se calculează despăgubirea la valoarea contabilă a bunului, nu la valoarea de imputare stabilită de comisie (care poate include, de exemplu, prețul de înlocuire).
- Se confundă contul folosit după calitatea vinovatului: 4282 e pentru salariat, 461 pentru un terț din afara entității.
- Se omite TVA-ul aferent valorii de imputare, deși aceasta este calculată separat de eventuala ajustare de TVA aplicabilă lipsurilor neimputabile (art. 304 Cod fiscal, care nu se aplică aici — imputarea are alt regim).
- Se înregistrează nota fără o cotă de TVA explicită; aplicația nu are o cotă implicită și refuză operațiunea dacă nu este introdusă.

## Ce face iConta.eu

În ecranul „Inventariere anuală" (categoria „Imobilizări și capital"), la operația **Minus**, bifând „imputabil" și completând valoarea de imputare și persoana vinovată (salariat/terț), aplicația generează automat nota de descărcare de gestiune și nota de imputare cu TVA calculată pe valoarea de imputare. Cota de TVA trebuie introdusă explicit — motorul nu acceptă o cotă implicită, tocmai pentru ca o cotă „hardcodată" să nu rămână tacit în urma unei schimbări legislative. Descrierea notei contabile primește automat sufixul „ - OMFP 2861/2009".

[iConta.eu](/)
