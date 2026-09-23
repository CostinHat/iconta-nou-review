---
title: De unde descarc factura primită prin RO e-Factura?
description: Factura ajunge deja adusă în lista de facturi de validat; XML-ul original se vede sau se descarcă din ecranul facturii, la cerere, nu se afișează implicit pe listă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# De unde descarc factura primită prin RO e-Factura?

Factura nu trebuie căutată în SPV, pe portalul ANAF — ea ajunge deja adusă în aplicație. Întrebarea reală, de obicei, e unde anume se vede și de unde se ia XML-ul original, dacă e nevoie de el.

## Temeiul legal

::: ghid-temei
„Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul naţional privind factura electronică RO e-Factura. Destinatarul este notificat cu privire la facturile electronice primite (...) conform procedurii prevăzute la art. 3 alin. (4)."

— OUG nr. 120/2021, art. 4 alin. (7)
:::

Din punct de vedere legal, „primirea” facturii e legată de disponibilitatea ei pentru descărcare în SPV, nu de un act separat de descărcare făcut de destinatar. Aplicația preia acest moment automat, ca să nu depindă de o acțiune manuală.

## Unde o găsești

Facturile primite de la furnizori prin RO e-Factura apar în lista dedicată de „facturi primite”, alături de cele care mai așteaptă validare. Fiecare rând arată deja furnizorul, numărul, data și sumele extrase din XML — nu trebuie deschis XML-ul pentru datele de bază.

Dacă ai nevoie chiar de fișierul XML original (de exemplu pentru un control sau pentru arhiva proprie), acesta se descarcă separat, la cerere, din ecranul facturii respective — nu e afișat implicit pe listă, ci accesibil printr-un click dedicat.

## Ce se greșește în practică

- Se caută factura direct pe portalul ANAF/SPV, deși ea a fost deja adusă automat în aplicație — dublează căutarea degeaba.
- Se presupune că, dacă factura nu apare încă printre „cheltuieli”, nu a fost descărcată deloc — de fapt poate fi deja adusă ca ciornă, doar neconfirmată încă de contabil.
- Se caută XML-ul brut direct în lista de facturi, deși el e accesibil doar din ecranul individual al facturii respective.

## Ce face iConta.eu

Odată descărcată automat din SPV, factura primită apare ca ciornă în lista de validat, cu datele esențiale deja extrase. XML-ul brut original rămâne stocat, accesibil oricând la cerere din ecranul facturii — nu e afișat implicit, tocmai ca lista să rămână lizibilă. Nu există, la acest moment, o funcție separată de „export/arhivă” a mai multor XML-uri deodată — accesul e factură cu factură.

[iConta.eu](/)
