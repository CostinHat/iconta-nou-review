---
title: "Cum transmit facturile unui magazin online în e-Factura?"
description: "Pasul de transmitere către RO e-Factura are un termen legal fix de 5 zile lucrătoare de la emitere, indiferent dacă factura provine dintr-un magazin online sau a fost emisă manual."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum transmit facturile unui magazin online în e-Factura?

O factură emisă din comenzile unui magazin online nu urmează un traseu separat către RO e-Factura. Odată creată, ea trebuie transmisă exact ca orice altă factură a firmei, cu același termen legal și aceleași riscuri de sancțiune la nerespectarea lui.

## Temeiul legal

::: ghid-temei
„Termenul-limită pentru transmiterea facturilor în sistemul naţional privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită pentru emiterea facturii prevăzută la art. 319 alin. (16) din Legea nr. 227/2015 [...] Calculul termenului-limită se efectuează conform Regulamentului (CEE, Euratom) nr. 1182/71 al Consiliului din 3 iunie 1971 [...]"
— OUG 89/2025 (sursă: anaf_surse/oug_89_2025.txt, linia 917)
:::

- Termenul de transmitere e legat de **data emiterii facturii**, nu de data la care a fost plasată comanda în magazinul online — cele două date pot diferi cu zile bune, mai ales dacă emiterea nu e imediată.
- Termenul se calculează în zile **lucrătoare**, după regula europeană de calcul a termenelor (Regulamentul 1182/71), nu în zile calendaristice.
- Nerespectarea termenului e sancționabilă distinct: Legea 296/2023 a introdus art. 13^2 alin. (3) din OUG 120/2021, cu amenzi cuprinse, în funcție de categoria contribuabilului, între 1.000 lei și 10.000 lei.

## Ce se greșește în practică

- Se așteaptă ca transmiterea la SPV să pornească automat odată ce comanda a devenit factură — nu există, în general, o legătură automată garantată între „factura a fost creată" și „factura a fost trimisă la ANAF"; fiecare sistem de facturare tratează diferit acest pas.
- Se numără termenul de la data comenzii din magazinul online, nu de la data efectivă de emitere a facturii, ceea ce poate duce la depășirea lui fără să fie observată.
- Se ignoră cazul indisponibilității sistemului RO e-Factura: dacă sistemul e nefuncțional minimum 24 de ore, obligația de transmitere se suspendă până la repunerea lui în funcțiune — dar numai cu condiția transmiterii ulterioare a facturilor emise în acel interval.

## Ce face iConta.eu

Conectorul WooCommerce din iConta.eu (ecranul „Magazin online") produce facturi interne din comenzile magazinului, dar **nu conține nicio logică de transmitere către e-Factura/SPV** — verificat direct în cod, `core/woocommerce.py` nu are nicio referință la e-Factura, SPV sau UBL. Facturile rezultate dintr-o comandă WooCommerce ajung în evidența firmei exact ca o factură introdusă manual, cu aceeași stare inițială de „de preluat".

Transmiterea propriu-zisă la ANAF rămâne, pentru orice factură din iConta.eu — inclusiv cele provenite din WooCommerce — o funcționalitate separată de conector, cu propriile verificări (validare de structură, evitarea unei duble trimiteri). Conectorul WooCommerce nu inițiază și nu automatizează acest pas.

[iConta.eu](/)
