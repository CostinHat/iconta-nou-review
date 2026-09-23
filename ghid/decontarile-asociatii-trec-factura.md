---
title: De ce decontările cu asociații nu trec prin e-Factura?
description: Dividendele și împrumuturile asociaților nu sunt operațiuni comerciale supuse facturării și TVA, deci nu intră în sistemul e-Factura — se înregistrează prin note contabile, nu prin facturi.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# De ce decontările cu asociații nu trec prin e-Factura?

„Decontări periodice" prin e-Factura e o formulare care poate induce în eroare: sistemul e-Factura (RO e-Factura) e conceput pentru facturi — documente emise între o firmă și un client/furnizor, pentru livrări de bunuri sau prestări de servicii supuse, de regulă, TVA. Distribuirea de dividende sau împrumutul de la/către un asociat **nu sunt operațiuni comerciale** și nu se facturează — deci nu au ce căuta în e-Factura.

## Temeiul legal

::: ghid-temei
„Cota-parte din profit ce se plătește fiecărui asociat constituie dividend."
— Legea 31/1990, art. 67 alin. (1)
:::

Dividendul e o repartizare a profitului către proprietarul firmei, nu o contraprestație pentru un bun sau un serviciu — de aceea nu presupune emiterea unei facturi. La fel, sumele puse la dispoziția firmei de un asociat, respectiv restituirea lor, sunt mișcări de trezorerie între firmă și asociat, documentate prin notă contabilă, nu prin factură (baza lor fiind OMFP 1802/2014, pct. 349, citat în ghidurile despre împrumutul asociat). Niciunul dintre aceste două tipuri de operațiuni nu generează TVA și, prin urmare, niciuna nu intră sub obligația de raportare prin e-Factura, care vizează exclusiv facturile fiscale.

## Ce se greșește în practică

- Se emite, din prudență excesivă, o „factură" pentru dividendul distribuit sau pentru împrumutul acordat de asociat — document care nu are obiect fiscal real și poate crea confuzii la reconcilierea TVA.
- Se așteaptă apariția unei mențiuni pentru dividende/împrumuturi asociați în rapoartele sau validările e-Factura, deși sistemul pur și simplu nu procesează acest tip de operațiune.
- Se confundă „decontare" în sensul contabil general (orice stingere de creanță/datorie) cu „decontare" în sensul comercial (plata unei facturi), deși în cazul asociaților vorbim de conturi de capital/asociați (456, 457, 463, 4551), nu de conturi de clienți/furnizori.

## Ce face iConta.eu

Funcționalitatea **Decontări asociați** (Operațiuni speciale > Finanțare) generează exclusiv note contabile — nu facturi — pentru dividend (`1171 = 457` / `463 = 456`), regularizare interimar-anual (`1171 = 457`, `457 = 463`) și împrumut asociat (`5121 = 4551` la primire, `4551 = 5121` la restituire). Aceste operațiuni rămân complet separate de modulele de e-Factura ale aplicației, care gestionează exclusiv facturile comerciale cu TVA.

[iConta.eu](/)
