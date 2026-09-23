---
title: Cum corectez o factură înregistrată pe furnizorul greșit?
description: O factură primită, atribuită greșit altui furnizor, nu se editează în iConta.eu. Fără notă contabilă, se șterge și se reintroduce pe furnizorul corect. Cu notă contabilă, corecția se face prin stornare la nivel de notă — stornoul automat de factură e confirmat în cod doar pentru facturile emise.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectez o factură înregistrată pe furnizorul greșit?

Furnizorul greșit pe o factură primită înseamnă, de regulă, că documentul a fost legat în sistem de altă firmă decât cea care l-a emis efectiv. Câmpul „furnizor" nu se editează pe o factură deja introdusă — corecția urmează aceeași regulă generală de stare (fără/cu notă contabilă), cu o particularitate importantă pentru facturile primite.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ." — Legea contabilității nr. 82/1991, art. 6 alin. (1)

„Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (stornare în roșu), fie prin înregistrarea inversă a acesteia (stornare în negru), în funcție de politica contabilă și programele informatice utilizate." — OMFP 1802/2014, Anexa 1 – Reglementări contabile, pct. 69
:::

Documentul justificativ e legat de identitatea reală a furnizorului care l-a emis — dacă în sistem a fost atribuit altcuiva, consemnarea nu corespunde operațiunii reale, deci trebuie corectată, nu doar „reetichetată".

## Cum corectez în iConta.eu

- **Factura nu are încă notă contabilă** → se șterge și se reintroduce pe furnizorul corect. Simplu, fără urme ale greșelii.
- **Factura are notă contabilă** (a fost deja contată) → ștergerea e refuzată explicit („Factura are notă contabilă și nu se mai șterge... Corecția unei facturi contabilizate se face prin STORNO"). Aici intervine particularitatea: funcția de stornare automată a facturii (`storneaza`), care generează un document nou cu liniile negate, e verificată în cod **doar pentru facturile emise** — pentru o factură primită, apelul respectiv nu se aplică.
- Pentru o factură primită deja contată, cu furnizor greșit, corecția se face la nivelul notei contabile: dacă nota e încă ciornă, contul analitic al furnizorului se corectează direct în notă (editare de linii); dacă nota e deja validată, corecția se face printr-o notă nouă de stornare (semn minus pe furnizorul greșit, apoi înregistrare corectă pe furnizorul real), conform aceluiași principiu din pct. 69.
- Perioada contabilă închisă blochează la fel editarea ciornei, ștergerea sau validarea — indiferent de stadiul corecției.

## Ce se greșește în practică

- Se presupune că „stornarea de factură" (butonul dedicat) funcționează la fel pentru facturi primite ca pentru cele emise — codul verificat arată explicit că funcția se aplică doar facturilor emise.
- Se lasă factura legată de furnizorul greșit „ca să nu se piardă istoricul", deși evidența economică a operațiunii reale (cu furnizorul adevărat) rămâne incompletă.
- Se editează contul din nota de contare fără să se verifice mai întâi dacă nota e încă ciornă — dacă e deja validată, editarea directă e refuzată de aplicație.

## Ce face iConta.eu

O factură primită atribuită greșit unui furnizor nu se editează. Fără notă contabilă, se șterge și se reintroduce corect. Cu notă contabilă, aplicația refuză ștergerea și impune corecția prin stornare — la nivel de factură emisă prin funcția dedicată, sau la nivel de notă contabilă (cont analitic corectat direct în ciornă, ori printr-o notă de stornare dacă a fost deja validată) pentru facturile primite.

[iConta.eu](/)
