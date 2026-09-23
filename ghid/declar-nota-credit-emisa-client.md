---
title: Cum declar o notă de credit emisă unui client din UE?
description: O notă de credit emisă unui client din UE se tratează contabil ca storno — document nou, cu suma negată, care păstrează clasificarea intracomunitară a facturii inițiale. Declararea ei în D390 poate cere reclasificare manuală dacă tipul operațiunii se schimbă.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum declar o notă de credit emisă unui client din UE?

O notă de credit către un client dintr-un alt stat membru e, din punct de vedere contabil, un storno — un document nou, cu valoare negativă, care corectează o factură deja emisă și înregistrată. Se declară pe același rând ca operațiunea corectată (D300 și D390), nu ca o operațiune separată.

## Temeiul legal

::: ghid-temei
Distincția dintre stornare și anulare, din instrucțiunile oficiale D394: "seria şi numărul facturilor **stornate**; **factura stornată reprezintă factura emisă de persoana impozabilă, a cărei valoare totală este negativă**" — spre deosebire de "facturile **anulate**; **factura anulată reprezintă factura emisă de persoana impozabilă, netransmisă beneficiarului, operaţiunile înscrise în aceasta nefiind înregistrate în contabilitatea persoanei impozabile**." — OPANAF 2194/2025, instrucțiuni D394

"Coloana «Baza impozabilă»... precum şi valoarea bazei impozabile aferentă facturilor de stornare, defalcate pe cote de TVA... În cazul în care baza impozabilă este negativă valoarea totală a acesteia se înscrie cu semnul (-)." — OPANAF 2194/2025, instrucțiuni D394
:::

O notă de credit e o stornare (factură nouă, cu valoare negativă, înregistrată în contabilitate), nu o anulare (care presupune că factura originală n-a fost niciodată transmisă/înregistrată). Pentru D394, regula de semn e explicită: baza și TVA aferente stornoului se înscriu cu semnul minus. Pentru D390, regulile oficiale (OPANAF 705/2020) precizează doar **momentul** declarării unei ajustări — luna exigibilității sau luna comunicării regularizării către client, art. 282 alin. (9) CF — dar nu menționează explicit convenția de semn. Declararea cu bază negativă e coerentă cu restul sistemului (D394 o cere expres), dar nu e un citat verbatim din instrucțiunile D390 înseși — e o interpretare consecventă, nu o normă scrisă expres pentru D390.

Tipul operațiunii intracomunitare rămâne cel al facturii inițiale — dacă a fost o livrare de bunuri (L), nota de credit rămâne L, cu bază negativă; dacă a fost un serviciu (P), rămâne P. Dacă, din greșeală, factura inițială a fost clasificată eronat, reclasificarea (schimbarea tipului de operațiune în D390) se face separat, prin panoul de clasificări manuale D390, nu prin nota de credit în sine.

## Ce se greșește în practică

Cea mai frecventă greșeală: „corectarea" unei declarații D390 dintr-o lună trecută prin înscrierea valorii 0 la baza impozabilă, în loc de declarație rectificativă pentru perioada respectivă — instrucțiunile interzic explicit procedeul cu „0". A doua greșeală: tratarea notei de credit ca operațiune independentă, nelegată de factura inițială, ceea ce dublează raportarea în loc s-o corecteze.

## Ce face iConta.eu

Crearea unei facturi de stornare produce un document nou, cu cantități negative, cu propriul număr rezervat din aceeași serie, legat de original prin referința internă către factura sursă. Documentul păstrează cursul valutar al facturii inițiale (nu al datei stornării) și copiază identic clasificarea ei fiscală — țara terțului, taxarea inversă, axa intracomunitară bunuri/servicii — astfel încât o notă de credit pentru o livrare IC aterizează pe același rând (L) ca factura corectată, cu bază negativă.

Dacă tipul operațiunii trebuie totuși schimbat (de exemplu, o reclasificare de la P la S, sau adăugarea unei linii D390 pur manuale), asta se face din panoul de clasificări manuale D390, separat de crearea notei de credit — cu o limitare de reținut: pentru o factură creată prin ecranul dedicat de achiziție/livrare intracomunitară, tipul operațiunii e "înghețat" din momentul emiterii (nu se mai poate schimba din panoul de reclasificare); corectarea unui asemenea tip greșit presupune stornarea și reemiterea facturii, nu doar reclasificarea manuală.

De reținut și o limitare de produs: butonul de trimitere în SPV (RO e-Factura) nu apare pe un document de stornare — dacă factura inițială a fost transmisă în e-Factura, transmiterea documentului de corecție către ANAF nu e acoperită automat de ecranul de facturi.

[iConta.eu](/)
