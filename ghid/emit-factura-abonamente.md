---
title: "Cum emit e-Factura pentru abonamente?"
description: "Ce parte din facturarea unui abonament se automatizează în iConta.eu și ce parte — transmiterea efectivă ca RO e-Factura — rămâne un pas manual, per factură."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum emit e-Factura pentru abonamente?

Pentru un abonament facturat periodic unui client din România, întrebarea „cum emit e-Factura" ascunde de fapt doi pași diferiți: emiterea facturii propriu-zise, dintr-un șablon recurent, și transmiterea ei ca RO e-Factura prin sistemul național. Doar al doilea pas îi dă facturii, legal, statutul de e-Factura.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile alin. (1), pentru operațiunile realizate între persoane impozabile stabilite în România conform art. 266 alin. (2), sunt considerate facturi numai facturile care îndeplinesc condițiile prevăzute de Ordonanța de urgență a Guvernului nr. 120/2021 privind administrarea, funcționarea și implementarea sistemului național privind factura electronică RO e-Factura [...]"
— Cod fiscal (Legea 227/2015), art. 319 alin. (1^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Termenul „e-Factura" nu descrie un format oarecare de fișier — descrie o factură care a trecut prin sistemul național RO e-Factura, singura formă considerată legal validă pentru operațiuni B2B între persoane impozabile din România.
- Un abonament facturat periodic (lunar, de exemplu) generează câte un document nou la fiecare ciclu — fiecare document, individual, trebuie transmis pentru a avea statutul de e-Factura, nu doar primul.
- Excepția din art. 319 alin. (1^1) e în vigoare din 01-07-2024 (introdusă prin Legea 296/2023) — se aplică oricărei facturi curente, indiferent dacă provine dintr-un ciclu de abonament sau dintr-o vânzare unică.

## Ce se greșește în practică

- Se emite corect factura pentru abonament, dar se omite transmiterea ei ca RO e-Factura, presupunând (greșit) că un sistem de facturare „modern" o face automat.
- Se transmite prima factură a unui abonament la SPV și se presupune că ciclurile ulterioare, emise automat, se trimit la fel — fără verificare per factură.
- Se confundă „am generat un PDF de factură" cu „am emis e-Factura" — pentru relația B2B, doar transmiterea prin sistemul național contează legal.

## Ce face iConta.eu

Pentru partea de **emitere**, modulul Facturi recurente automatizează complet ciclul unui abonament: dintr-un șablon cu client, linii și zi de emitere, un job zilnic generează factura lunar, fără intervenție. Pentru partea de **e-Factura**, însă, mecanismul nu face nimic automat: factura recurentă iese cu statusul „de preluat", iar transmiterea ei ca RO e-Factura la SPV e o funcționalitate separată, apelată manual, per factură, dintr-un buton dedicat în ecranul de facturi — nu există niciun apel către SPV integrat în ciclul de emitere recurentă. Pentru un abonament facturat lunar, asta înseamnă că fiecare factură lunară trebuie trimisă individual la SPV, chiar dacă emiterea ei a fost automată.

[iConta.eu](/)
