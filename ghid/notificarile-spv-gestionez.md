---
title: "Notificările din SPV: cum le gestionez"
description: "Ce notificări din Spațiul Privat Virtual descarcă automat iConta din contul de e-Factura al cabinetului — și ce tipuri de mesaje rămân în afara acestei automatizări."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Notificările din SPV: cum le gestionez

Spațiul Privat Virtual comunică prin mesaje pe mai multe tipuri: facturi trimise, facturi primite, erori, mesaje ale cumpărătorului. Legea numește explicit obligația de a pune la dispoziție și de a notifica destinatarul cu privire la facturile primite prin sistem — restul rămâne, azi, în afara automatizării.

## Temeiul legal

::: ghid-temei
„Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul național privind factura electronică RO e-Factura. Destinatarul este notificat cu privire la facturile electronice primite [...]."
— OUG 120/2021, art. 4 alin. (7) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce înseamnă, concret, pentru gestionarea notificărilor din SPV:

- **Sistemul ANAF distinge tipuri de mesaje** prin parametrul `filtru` al interogării de listare: E = erori factură, T = factură trimisă (confirmare de primire ANAF), P = factură primită (de la furnizori), R = mesaj cumpărător.
- **Obligația legală de notificare** (art. 4 alin. (7) de mai sus) privește tocmai facturile primite — momentul în care factura devine disponibilă pentru descărcare e considerat, legal, momentul comunicării ei.
- **Obiecția destinatarului** asupra unei facturi electronice se face, potrivit legii, „inclusiv în sistemul național privind factura electronică RO e-Factura, prin înscrierea unui mesaj în acest sens" (OUG 120/2021, art. 4 alin. (9)) — un mecanism formal, distinct de o simplă respingere internă în programul de contabilitate.
- **Corecția unei facturi electronice deja comunicate** se face conform art. 330 din Codul fiscal și se retransmite prin același sistem RO e-Factura (OUG 120/2021, art. 4 alin. (10)).

## Ce se greșește în practică

- Se presupune că orice notificare/mesaj din SPV (inclusiv confirmările de trimitere sau erorile) e „descărcat" automat de aplicația de contabilitate — depinde strict de ce tip de mesaj (`filtru`) e configurat să fie preluat automat.
- Se confundă „respingerea" unei facturi primite, făcută intern în programul de contabilitate, cu obiecția formală prevăzută de lege (art. 4 alin. (9)), care presupune înscrierea unui mesaj în sistemul SPV către emitent — cele două nu au același efect juridic.
- Se așteaptă o alertă automată de tip e-mail/push pentru absența oricărei facturi noi descărcate din SPV — o astfel de tăcere poate însemna, la fel de bine, o conexiune SPV expirată, nu neapărat lipsa reală de facturi.

## Ce face iConta.eu

Funcționalitatea **Cron receive e-Factura** rulează automat, la fiecare 30 de minute, și descarcă din SPV mesajele de tip „factură primită" (`filtru=P`) pentru fiecare firmă conectată, pe o fereastră de 3 zile suprapusă (toleranță la eșecuri intermitente). Fiecare mesaj e verificat contra scurgerii de date între firme ale aceluiași cabinet (CIF-ul beneficiarului din mesaj trebuie să coincidă cu CIF-ul firmei) și deduplicat pe identificatorul de mesaj ANAF, apoi factura e inserată ca ciornă — fără să genereze automat nicio cheltuială: validarea (alegerea contului de cheltuială) rămâne un pas manual, obligatoriu, al contabilului.

Aplicația **nu descarcă și nu gestionează automat** celelalte tipuri de mesaje SPV — confirmările de trimitere (`T`), erorile (`E`) sau mesajele de tip cumpărător (`R`, care includ obiecția formală prevăzută de art. 4 alin. (9)) nu sunt preluate de acest mecanism. „Respingerea" unei facturi primite, disponibilă în iConta, e o acțiune pur internă (cu motiv, păstrată în istoric) — nu scrie niciun mesaj înapoi în sistemul SPV către emitent, deci nu echivalează cu obiecția formală din lege. Automatizarea rulează implicit, fără niciun ecran de configurare — frecvența și fereastra de interogare sunt fixate la nivel de server, nu editabile din interfață.

[iConta.eu](/)
