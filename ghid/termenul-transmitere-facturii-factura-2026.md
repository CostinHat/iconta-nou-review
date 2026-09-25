---
title: "Care este termenul de transmitere a facturii în e-Factura în 2026?"
description: "Termenul de 5 zile lucrătoare pentru transmiterea facturilor în sistemul RO e-Factura, conform Legii 296/2023."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Care este termenul de transmitere a facturii în e-Factura în 2026?

Emiterea unei facturi și transmiterea ei în sistemul național RO e-Factura sunt două momente diferite, cu un termen legal precis între ele — termen care rămâne, în 2026, neschimbat față de forma actuală a legii.

## Temeiul legal

::: ghid-temei
„(6) Termenul-limită pentru transmiterea facturilor prevăzute la alin. (1)-(3) în sistemul național privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită prevăzută pentru emiterea facturii la art. 319 alin. (16) din Legea nr. 227/2015, cu modificările și completările ulterioare."
— Legea 296/2023, art. LIX alin. (6) (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

Structura termenului, cu cele două ancore posibile:

- **Regula de bază**: 5 zile lucrătoare de la **data emiterii** facturii.
- **Plafonul absolut**: nu mai târziu de 5 zile lucrătoare de la **data-limită legală de emitere** a facturii (art. 319 alin. (16) Cod fiscal) — chiar dacă factura a fost emisă cu întârziere față de acea dată-limită, termenul de transmitere în e-Factura nu se prelungește la nesfârșit, ci rămâne ancorat de data-limită de emitere.
- Practic, pentru o factură emisă la timp, termenul curge simplu: 5 zile lucrătoare de la emitere. Pentru o factură emisă cu întârziere, termenul de transmitere e mai strâns, calculat de la data-limită legală, nu de la emiterea efectivă tardivă.
- Nerespectarea termenului e contravenție, sancționată în funcție de mărimea contribuabilului: amendă de la 5.000 la 10.000 lei pentru contribuabilii mari, 2.500-5.000 lei pentru cei mijlocii, 1.000-2.500 lei pentru restul persoanelor juridice și pentru persoanele fizice (art. LIX alin. (7)).

## Ce se greșește în practică

- Se numără zile calendaristice în loc de zile lucrătoare — un termen de "5 zile" care include un weekend se calculează greșit dacă nu se exclud explicit sâmbăta și duminica.
- Se presupune că termenul curge mereu de la data emiterii, chiar și pentru facturi emise cu întârziere mare — legea limitează termenul și la data-limită de emitere, deci o factură foarte întârziată nu capătă automat 5 zile suplimentare de la emiterea ei tardivă.
- Se confundă emiterea facturii (către client) cu transmiterea în RO e-Factura (către sistemul ANAF) — sunt două acțiuni distincte, cu termene proprii, deși pot coincide în practică pentru firmele care emit direct prin sistem.

## Ce face iConta.eu

La data acestui ghid, `core/efactura_send.py` (`fctel`) generează XML-ul facturii (`genereaza_xml()`), îl validează (`valideaza()`) și îl transmite prin `upload_ubl()` către SPV, cu urmărirea stării prin `stare_mesaj()`. Transmiterea propriu-zisă către ANAF e deci o funcționalitate reală a aplicației — verificarea automată a încadrării în termenul de 5 zile lucrătoare de la art. LIX alin. (6), cu semnalarea unei transmiteri care riscă să depășească termenul, nu a fost identificată ca funcție distinctă în cod.

[iConta.eu](/)
