---
title: "Am facturat către un client cu CUI nevalid"
description: O factură emisă deja nu se editează în locul CUI-ului greșit — mecanismul din iConta.eu e stornarea documentului emis și emiterea unuia nou, corect. Legal, factura corectă e cea care identifică real subiectul raportului fiscal.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Am facturat către un client cu CUI nevalid

O factură deja emisă cu un CUI greșit sau inexistent nu poate fi „reparată" prin simpla editare a câmpului CUI — documentul a fost deja emis, eventual transmis. Remediul, atât în logica aplicației cât și în practica de facturare, e stornarea și reemiterea, nu corectarea in-place.

## Temeiul legal

::: ghid-temei
„Orice persoană sau entitate care este subiect într-un raport juridic fiscal se înregistrează fiscal primind un cod de identificare fiscală." — Legea nr. 207/2015 privind Codul de procedură fiscală, art. 82 alin. (1)
:::

Un CUI nevalid pe o factură emisă înseamnă, practic, că documentul nu identifică real subiectul raportului juridic fiscal căruia i-a fost adresat — de aici nevoia de a corecta prin emiterea unui document nou, corect, nu prin editarea celui deja emis.

## Ce faci concret

1. **Verifică CUI-ul corect la ANAF** — înainte de a reemite, confirmă denumirea și CUI-ul real ale clientului, folosind verificarea directă la ANAF.
2. **Stornează factura greșită** — documentul deja emis nu se modifică; se generează o factură de stornare care anulează efectele celei greșite.
3. **Emite o factură nouă, cu CUI-ul corect** — stornarea nu „repară" automat CUI-ul; e nevoie de un al doilea document, complet nou, cu datele corecte ale clientului.

## Ce se greșește în practică

- Se încearcă editarea directă a câmpului CUI pe o factură deja emisă (mai ales dacă a fost doar salvată, nu și transmisă) — o factură emisă e un document finalizat; corectarea corectă e prin stornare, nu prin editare retroactivă.
- Se emite direct o „factură corectivă" fără să se storneze mai întâi factura greșită — asta lasă în evidență două documente active pentru aceeași operațiune, cu risc de dublă raportare a TVA.
- Se presupune că simpla corectare a CUI-ului în fișa clientului din aplicație corectează automat și facturile deja emise către acel client — fișa clientului și factura emisă sunt înregistrări separate; corectarea fișei nu modifică retroactiv un document deja emis.

## Ce face iConta.eu

Pentru o factură emisă cu date greșite ale clientului, iConta.eu nu oferă editare in-place a documentului emis — mecanismul verificat e stornarea (care generează al doilea document, nu corectează pe cel dintâi), urmată de emiterea unei facturi noi, cu CUI-ul corect al clientului, verificat în prealabil la ANAF. Dacă factura greșită a fost deja transmisă prin e-Factura (RO e-Factura/SPV), verifică separat dacă stornarea trebuie retransmisă — acest aspect nu a fost confirmat în cadrul verificării de față și trebuie tratat punctual, la nevoie.

[iConta.eu](/)
