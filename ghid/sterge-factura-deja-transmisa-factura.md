---
title: "Se poate șterge o factură deja transmisă în e-Factura?"
description: "Ce prevede OUG 120/2021 despre imposibilitatea returnării unei facturi electronice comunicate și mecanismul legal de corectare a ei."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Se poate șterge o factură deja transmisă în e-Factura?

O factură emisă greșit și deja transmisă prin sistemul RO e-Factura nu poate fi pur și simplu ștearsă, ca un document local. Legea tratează momentul comunicării către destinatar ca pe un punct fără cale de întoarcere.

## Temeiul legal

::: ghid-temei
„(8) Factura electronică comunicată destinatarului nu se poate returna în sistemul naţional privind factura electronică RO e-Factura. (9) În situaţia unei facturi electronice asupra căreia destinatarul are obiecţii, acesta înştiinţează emitentul facturii electronice, inclusiv în sistemul naţional privind factura electronică RO e-Factura, prin înscrierea unui mesaj în acest sens."
— OUG nr. 120/2021, art. 4 alin. (8)-(9) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce înseamnă concret această regulă:

- Odată ce factura electronică a fost **comunicată destinatarului** (adică e disponibilă pentru descărcare din sistemul RO e-Factura), ea **nu mai poate fi retrasă sau ștearsă** — nici de emitent, nici, cu atât mai puțin, de destinatar.
- Singura cale legală pentru o factură greșită deja transmisă este **corectarea** ei, conform art. 330 din Codul fiscal (Legea nr. 227/2015): fie emiterea unei noi facturi cu valorile corecte, însoțită de mențiunea facturii corectate, fie o factură de stornare (cu valorile negative) urmată de una corectă — niciodată o modificare „pe loc" a facturii inițiale.
- Dacă destinatarul are obiecții față de o factură primită (de exemplu, constată o eroare), procedura prevăzută de lege e să **înștiințeze emitentul**, inclusiv printr-un mesaj în sistemul RO e-Factura — nu să refuze unilateral factura sau să o considere „nulă" din proprie inițiativă.
- Factura de corecție, la rândul ei, trebuie transmisă tot prin sistemul RO e-Factura (art. 4 alin. (10)) — corectarea nu iese din fluxul obligatoriu al facturării electronice, chiar dacă motivul corecției e o simplă eroare de emitere.

## Ce se greșește în practică

- Se presupune că o factură emisă greșit „nu contează" dacă nu a fost încă plătită, și se ignoră corectarea ei formală — factura rămâne validă în sistem până e corectată explicit, indiferent de stadiul plății.
- Se încearcă anularea unei facturi deja comunicate prin simpla emitere a uneia noi, cu același conținut corect, fără stornarea/referirea explicită la factura greșită — lipsa legăturii dintre cele două facturi face trasabilitatea dificilă la control.
- Se așteaptă ca sistemul RO e-Factura să permită o funcție de „ștergere" similară cu cea dintr-un program de facturare local — sistemul național nu are o astfel de funcție pentru facturile deja comunicate, prin construcție legală.

## Ce face iConta.eu

La data acestui ghid, iConta.eu transmite facturile către sistemul RO e-Factura prin motorul propriu (`core/efactura_send.py`, `core/efactura_trimitere.py`) și nu oferă o opțiune de „ștergere" a unei facturi deja transmise — corectarea unei facturi comunicate se face prin emiterea unei facturi noi/de stornare, conform mecanismului legal, nu prin eliminarea celei inițiale.

[iConta.eu](/)
