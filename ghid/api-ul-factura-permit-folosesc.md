---
title: "API-ul e-Factura: ce permit și cum se folosesc"
description: "Ce prevede legea despre scopul și limitele sistemului RO e-Factura folosit prin API — de la structura facturii la protecția datelor cu caracter personal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# API-ul e-Factura: ce permit și cum se folosesc

API-ul RO e-Factura nu este un canal separat, cu reguli proprii — este pur și simplu o altă cale tehnică de a folosi același sistem național, supus acelorași reguli de structură, semnătură și protecție a datelor ca și interfața web.

## Temeiul legal

::: ghid-temei
„Sistemul naţional privind factura electronică RO e-Factura asigură interoperabilitatea cu sistemele de facturare ale operatorilor economici."
— OUG nr. 120/2021, art. 16 (sursă: anaf_surse/oug_120_2021.txt)
:::

Din întregul capitol I al ordonanței rezultă ce anume „permite" acest API, în esență:

- **Transmiterea facturilor electronice** de la emitent către sistem, cu validare de structură și aplicarea semnăturii electronice a Ministerului Finanțelor la acceptare (art. 4).
- **Primirea și descărcarea facturilor** de către destinatar, notificat automat de sistem (art. 4 alin. (7)).
- Datele cu caracter personal obținute prin prelucrarea facturilor electronice pot fi folosite „exclusiv în acest scop sau în scopuri compatibile cu acesta" (art. 14 alin. (2)) — o limită legală explicită pentru orice aplicație terță conectată prin API, nu doar pentru sistemul ANAF.
- Ministerul Finanțelor și ANAF asigură managementul datelor „cu păstrarea secretului fiscal" (art. 15) — informațiile din facturi nu pot fi folosite liber de sistemul central în alte scopuri decât cele prevăzute de lege, iar aceeași logică de limitare a scopului trebuie respectată și de aplicațiile care consumă API-ul.

## Ce se greșește în practică

- Se presupune că API-ul oferă acces la mai multe date decât interfața web (de exemplu, istoricul complet al tuturor facturilor unei alte firme) — accesul rămâne limitat la facturile proprii ale contribuabilului autorizat.
- Se folosesc datele descărcate prin API în scopuri neconforme cu prelucrarea facturilor (de exemplu, construirea de baze de date de marketing pe seama datelor de identificare ale clienților) — contravine limitării explicite de scop din art. 14.
- Se tratează API-ul ca pe un canal „mai relaxat" din punct de vedere al validării — orice factură transmisă, indiferent de canal, trebuie să respecte aceeași structură tehnică.

## Ce face iConta.eu

iConta.eu folosește API-ul RO e-Factura pentru trei funcții concrete: trimiterea facturilor emise (`core/efactura_send.py`), interogarea periodică a stării trimiterilor (`core/spv_poll.py`) și descărcarea automată a facturilor primite de la furnizori (`core/spv_receive.py`). Datele preluate din facturi sunt folosite exclusiv pentru evidența contabilă a firmei conectate — aplicația nu partajează sau reutilizează aceste date în alte scopuri, iar accesul token-ului OAuth2 este limitat la firma care l-a autorizat, fără posibilitate de acces încrucișat între firme diferite.

[iConta.eu](/)
