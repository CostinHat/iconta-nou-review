---
title: "Cum automatizez facturarea lunară și transmiterea în SPV?"
description: "De ce emiterea automată a facturii lunare și transmiterea ei ca RO e-Factura în SPV sunt, legal și tehnic, doi pași separați, și ce automatizează iConta.eu din fiecare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum automatizez facturarea lunară și transmiterea în SPV?

Pentru relațiile B2B din România, o factură nu mai e valabilă legal doar pentru că a fost emisă — trebuie și transmisă prin sistemul național RO e-Factura pentru a avea regimul juridic de factură. E important, deci, să fie clar de la început: „emiterea automată a facturii" și „transmiterea automată în SPV" sunt două lucruri diferite, verificate separat mai jos.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile alin. (1), pentru operațiunile realizate între persoane impozabile stabilite în România conform art. 266 alin. (2), sunt considerate facturi numai facturile care îndeplinesc condițiile prevăzute de Ordonanța de urgență a Guvernului nr. 120/2021 privind administrarea, funcționarea și implementarea sistemului național privind factura electronică RO e-Factura [...]"
— Cod fiscal (Legea 227/2015), art. 319 alin. (1^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Pentru operațiuni B2B între persoane impozabile stabilite în România, doar documentul transmis prin RO e-Factura are, legal, statutul de „factură" — un document creat și trimis clientului pe altă cale (email, PDF) nu are acest regim.
- Alineatul e o excepție intrată în vigoare din 01-07-2024, prin Legea 296/2023, tocmai pentru a obliga trecerea prin sistemul național, nu doar recomanda.
- Din acest motiv, orice automatizare a facturării recurente trebuie evaluată separat pe cele două componente — emiterea documentului și transmiterea lui reală prin SPV — pentru că doar a doua componentă îi dă efectul juridic de factură în relația B2B.

## Ce se greșește în practică

- Se presupune că „am automatizat facturarea" înseamnă implicit că factura a și ajuns la ANAF prin SPV — fără verificarea explicită a statusului de transmitere.
- Se lasă facturile emise automat „în așteptare" (netransmise), acumulate luni la rând, până când cineva observă că niciuna nu are, de fapt, regimul de factură valabilă în relația B2B.
- Se confundă emiterea facturii (creare + numerotare) cu validarea ei fiscală — cele două nu coincid dacă transmiterea SPV nu s-a făcut.

## Ce face iConta.eu

Cele două jumătăți ale întrebării au răspunsuri diferite în cod. Partea de **facturare lunară automată** e acoperită integral: modulul Facturi recurente rulează un job zilnic care emite, dintr-un șablon (client, linii, zi de emitere), câte o factură pe lună, fără intervenție manuală, atâta timp cât șablonul e activ. Partea de **transmitere automată în SPV** însă **nu există** pentru facturile emise astfel: factura recurentă iese cu statusul „de preluat" și rămâne acolo până la un pas separat și manual — trimiterea la SPV se face per-factură, dintr-un ecran dedicat, apăsând explicit un buton de transmitere. Deci: emiterea e automată, transmiterea în SPV rămâne un pas manual, distinct, pentru fiecare factură emisă recurent.

[iConta.eu](/)
