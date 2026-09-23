---
title: Cum descarc automat facturile din RO e-Factura?
description: Mecanismul rulează deja, la fiecare 30 de minute, prin conexiunea SPV a cabinetului — nu e nimic de pornit sau de configurat pentru descărcarea automată în sine.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum descarc automat facturile din RO e-Factura?

Dacă întrebarea e „cum activez” descărcarea automată, răspunsul e simplu: nu e ceva de activat separat — e activă implicit, pentru orice firmă al cărei cabinet are o conexiune SPV funcțională.

## Temeiul legal

::: ghid-temei
„Factura electronică se transmite de către emitent în sistemul naţional privind factura electronică RO e-Factura."

— OUG nr. 120/2021, art. 4 alin. (3)
:::

::: ghid-temei
„Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul naţional privind factura electronică RO e-Factura."

— OUG nr. 120/2021, art. 4 alin. (7)
:::

Cele două alineate descriu, împreună, tot circuitul: furnizorul transmite factura în SPV, iar din momentul disponibilității ei pentru descărcare, ea e considerată comunicată destinatarului. Mecanismul automat de descărcare din aplicație preia exact acest al doilea moment, fără intervenție manuală.

## Cum funcționează, tehnic

Un proces programat interoghează periodic ANAF, cerând mesajele noi de tip „factură primită” pentru fiecare firmă cu cabinet conectat la SPV. Interogarea acoperă o fereastră de 3 zile în urmă la fiecare rulare — nu doar intervalul de la ultima verificare — tocmai ca o eventuală rulare ratată să nu ducă la pierderea unei facturi. Fiecare factură nouă găsită e descărcată, verificată să aparțină efectiv firmei respective, apoi salvată ca ciornă; cele deja aduse la o rulare anterioară sunt recunoscute și sărite, ca să nu se dubleze.

Frecvența (la fiecare 30 de minute) și fereastra de interogare sunt fixate la nivel de sistem, nu configurabile de contabil din interfață — nu există un ecran de „pornit/oprit” sau de „ajustat intervalul” cronului de descărcare.

## Ce se greșește în practică

- Se caută o setare de activare sau un interval configurabil în interfață — nu există, pentru că mecanismul e pornit implicit și frecvența e fixă.
- Se confundă „descărcarea automată” cu „înregistrarea automată” — factura e adusă automat ca ciornă, dar transformarea ei în cheltuială contabilizată rămâne o acțiune manuală, cu contul de cheltuială confirmat de contabil.
- Se crede că descărcarea depinde de a fi logat în aplicație în momentul respectiv — nu depinde, rulează indiferent de sesiunile deschise.

## Ce face iConta.eu

Descărcarea automată e implementată ca proces programat, la 30 de minute, pentru toate firmele ai căror cabinete au o conexiune SPV activă. Nu există nicio configurare de făcut din partea contabilului pentru partea de descărcare în sine — singurul pas manual rămas e validarea facturii, unde contul de cheltuială trebuie confirmat sau ales explicit, fără valoare implicită.

[iConta.eu](/)
