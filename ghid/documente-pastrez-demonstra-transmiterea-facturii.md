---
title: "Ce documente păstrez pentru a demonstra transmiterea facturii în termen?"
description: Ce reprezintă, legal, exemplarul original al unei facturi electronice și ce salvează iConta.eu la finalizarea transmiterii unei facturi prin RO e-Factura.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce documente păstrez pentru a demonstra transmiterea facturii în termen?

Dovada că o factură a fost transmisă și acceptată în RO e-Factura nu este recipisa PDF în sine, ci fișierul XML original, însoțit de semnătura electronică a Ministerului Finanțelor — acesta este, potrivit legii, exemplarul original al facturii electronice.

## Temeiul legal

::: ghid-temei
"Exemplarul original al facturii electronice se consideră fişierul de tip XML însoţit de semnătura electronică a Ministerului Finanţelor."
— OUG 120/2021, art. 4 alin. (6)
:::

::: ghid-temei
"Termenul-limită pentru transmiterea facturilor în sistemul național privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită pentru emiterea facturii prevăzută la art. 319 alin. (16) din Legea nr. 227/2015, cu modificările și completările ulterioare."
— OUG 89/2025, art. X pct. 2 (modifică art. 10 alin. (7) din OUG 120/2021)
:::

Termenul-limită legal de transmitere a facturii către ANAF este de 5 zile lucrătoare de la data emiterii. Atenționăm asupra unei diferențe de formulare între preambulul acestei modificări legislative, care menționează "5 zile calendaristice", și textul de lege operativ, care stabilește "5 zile lucrătoare" — cel din urmă este cel care produce efecte juridice și cel care trebuie folosit la calculul termenului.

Dovada că factura a fost transmisă (și acceptată) este, conform legii, exemplarul original — fișierul XML plus semnătura electronică a Ministerului Finanțelor — nu recipisa PDF descărcată sau alt document intermediar.

## Ce se greșește în practică

- Se păstrează doar recipisa PDF (dacă există una vizuală) ca dovadă a transmiterii, în loc de fișierul XML original însoțit de semnătura MF, care este exemplarul cu valoare legală conform art. 4 alin. (6).
- Se calculează termenul de transmitere folosind "5 zile calendaristice", preluat din formularea motivațională a OUG 89/2025, în loc de "5 zile lucrătoare" din textul operativ — diferența poate muta efectiv data-limită.
- Se presupune că data încărcării în SPV este automat și data "comunicării" facturii — legea leagă data comunicării de momentul la care factura devine disponibilă pentru descărcare, accesibilă și emitentului în sistem.

## Ce face iConta.eu

La primirea unui verdict terminal de la ANAF pentru o factură emisă, iConta.eu descarcă automat arhiva cu recipisa, calculează amprenta (hash SHA-256) a fișierului XML semnat din interiorul arhivei — excluzând fișierul de semnătură propriu-zis — și salvează atât arhiva, cât și amprenta calculată, alături de momentul exact la care factura a fost finalizată. Aceste elemente formează, împreună, dovada tehnică internă a transmiterii și a rezultatului obținut de la ANAF pentru fiecare factură.

Trebuie spus onest: aplicația salvează aceste elemente ca parte a evidenței tehnice a trimiterii, dar responsabilitatea de a respecta termenul legal de 5 zile lucrătoare pentru transmiterea inițială a facturii rămâne a firmei emitente — iConta.eu nu garantează și nu poate garanta un termen de procesare din partea ANAF, care nu este documentat public.

[iConta.eu](/)
