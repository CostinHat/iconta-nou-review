---
title: Cum primesc alerte pentru facturile primite în SPV
description: Facturile primite prin RO e-Factura ajung automat în aplicație, la interval fix, ca ciornă de validat - dar iConta.eu nu trimite, în acest moment, o alertă separată (e-mail, push) la fiecare factură nouă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum primesc alerte pentru facturile primite în SPV

Răspunsul scurt e că, în acest moment, nu există o alertă dedicată — dar nici nu e nevoie de una, pentru că factura nu trebuie „așteptată": ajunge deja adusă automat în aplicație, la un interval scurt și regulat.

## Temeiul legal

::: ghid-temei
„Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul naţional privind factura electronică RO e-Factura."
— OUG nr. 120/2021, art. 4 alin. (7)
:::

Legal, „primirea" facturii e legată de momentul în care ea devine disponibilă pentru descărcare în sistemul RO e-Factura, nu de o acțiune separată de confirmare din partea destinatarului. Practic, asta înseamnă că factura există deja, cu efecte fiscale, chiar dacă încă nu a fost verificată vizual de cineva din firmă.

## Ce se întâmplă, de fapt, cu o factură nouă primită

Facturile transmise de furnizori prin RO e-Factura sunt preluate automat din SPV la interval regulat (aproximativ o dată la 30 de minute) și apar, deja completate cu datele extrase din XML (furnizor, număr, dată, sume), în lista de „facturi primite" — ca ciornă, în așteptarea validării de către contabil. Nu e nevoie de nicio acțiune manuală de „descărcare" pentru ca factura să apară acolo.

Ce nu există, în acest moment, e un canal separat care să semnaleze activ „a sosit o factură nouă" — un badge dedicat pe ecran, un e-mail sau o notificare push. Preluarea automată există, dar rămâne un proces de fundal, vizibil doar când se deschide lista de facturi primite.

## Ce se greșește în practică

- Se așteaptă un e-mail sau o notificare la fiecare factură nouă primită prin SPV — un asemenea canal nu există în acest moment, iar așteptarea lui poate întârzia observarea facturii.
- Se verifică manual portalul ANAF/SPV pentru facturi noi, deși ele sunt deja aduse automat în aplicație — dublează inutil o muncă deja făcută de sistem.
- Se presupune că, dacă o factură nu apare încă printre „cheltuieli" confirmate, nu a fost primită deloc — de fapt poate fi deja adusă ca ciornă, doar neconfirmată încă de contabil.

## Ce face iConta.eu

Cronul intern de preluare RO e-Factura citește periodic mesajele din SPV și aduce automat facturile primite ca ciornă în lista dedicată din aplicație, cu datele esențiale deja extrase din XML — fără nicio acțiune manuală de descărcare. Nu există, la acest moment, un mecanism separat de alertă (e-mail, notificare push, badge dedicat) pentru fiecare factură nouă adusă astfel — cea mai sigură practică, până la o eventuală extindere a acestei zone, e verificarea periodică a listei de facturi primite, mai ales înainte de închiderea lunii.

[iConta.eu](/)
