---
title: "Cum văd facturile primite în SPV"
description: "Cum ajung facturile electronice primite de la furnizori la destinatar prin sistemul RO e-Factura, potrivit OUG 120/2021."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum văd facturile primite în SPV

O factură emisă prin sistemul RO e-Factura nu ajunge la beneficiar prin e-mail sau poștă, ci devine disponibilă pentru descărcare direct în Spațiul Privat Virtual, iar destinatarul e notificat automat de sistem.

## Temeiul legal

::: ghid-temei
„Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul național privind factura electronică RO e-Factura. Destinatarul este notificat cu privire la facturile electronice primite în sistemul național privind factura electronică RO e-Factura conform procedurii prevăzute la art. 3 alin. (4). Data comunicării este accesibilă în sistem și emitentului facturii electronice."
— OUG 120/2021, art. 4 alin. (7) (sursă: anaf_surse/oug_120_2021.txt)
:::

Câteva reguli practice care decurg din text:

- Factura devine „comunicată" din punct de vedere legal în momentul în care **poate fi descărcată**, nu în momentul în care destinatarul o deschide efectiv — data comunicării e cea de referință pentru termene.
- Odată comunicată, **factura nu mai poate fi „returnată"** în sistem (art. 4 alin. (8)) — dacă destinatarul are obiecții asupra conținutului, trebuie să înștiințeze emitentul, inclusiv prin sistem, prin înscrierea unui mesaj (art. 4 alin. (9)).
- O eventuală corecție se face conform art. 330 din Codul fiscal și se transmite tot prin sistemul RO e-Factura, nu pe alt canal.
- Emitentul vede și el data comunicării, deci ambele părți au aceeași referință de timp pentru factura respectivă.

## Ce se greșește în practică

- Se așteaptă factura pe e-mail sau prin alt canal clasic, deși obligația legală a emitentului e doar să o transmită prin RO e-Factura — destinatarul trebuie să o preia de acolo.
- Se ignoră mesajele de eroare la respingere: dacă factura nu respectă structura obligatorie, emitentul primește erorile și trebuie să retransmită, iar destinatarul nu vede nimic până la corectare (art. 4 alin. (5)).
- Se încearcă „anularea" unei facturi deja comunicate direct în sistem — legea permite doar obiecția prin mesaj și corecția ulterioară, nu returul facturii.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **automatizează parțial preluarea facturilor primite**: un cron dedicat interoghează periodic mesajele de tip „FACTURĂ PRIMITĂ" din sistemul RO e-Factura pentru fiecare firmă conectată, descarcă facturile noi și le introduce ca ciornă în evidența facturilor primite ale firmei. Aplicația nu creează automat o cheltuială din factura descărcată — contabilul validează manual fiecare factură, potrivit principiului „patru ochi" aplicat consecvent în iConta.eu. Vizualizarea propriu-zisă a facturilor deja transmise de furnizor rămâne, în paralel, disponibilă și direct în Spațiul Privat Virtual al firmei.

[iConta.eu](/)
