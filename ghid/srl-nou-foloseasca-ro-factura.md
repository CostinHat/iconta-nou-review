---
title: "Când trebuie un SRL nou să folosească RO e-Factura?"
description: "De ce obligația de a transmite facturile prin sistemul RO e-Factura, în relația B2B dintre firme stabilite în România, nu are o perioadă de grație pentru firmele nou-înființate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când trebuie un SRL nou să folosească RO e-Factura?

Un SRL nou-înființat nu beneficiază de o perioadă de grație pentru obligația de a folosi RO e-Factura — de îndată ce emite o factură către o altă persoană impozabilă stabilită în România (o relație B2B), obligația de transmitere prin sistemul național se aplică de la prima astfel de factură, nu doar după un anumit termen de la înființare sau după depășirea unei cifre de afaceri.

## Temeiul legal

::: ghid-temei
„(1) În relația comercială B2B, între persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015, cu modificările și completările ulterioare, emitentul facturii electronice are obligația de transmitere a acesteia către destinatar utilizând sistemul național privind factura electronică RO e-Factura, cu respectarea prevederilor art. 4 alin. (1). Fac excepție facturile simplificate emise conform art. 319 alin. (12) din Legea nr. 227/2015, cu modificările și completările ulterioare."
— Ordonanța de urgență a Guvernului nr. 115/2023, care modifică art. 10 alin. (1) din OUG nr. 120/2021 privind sistemul național RO e-Factura (sursă: anaf_surse/oug_115_2023_consolidat.txt)
:::

Ce rezultă concret pentru o firmă nou-înființată:

- **Obligația se leagă de calitatea de persoană impozabilă stabilită în România**, nu de vechimea firmei — un SRL nou-înmatriculat, din momentul în care devine persoană impozabilă și emite prima factură către un alt partener stabilit în România, intră sub aceeași obligație ca orice firmă existentă.
- **Singura excepție** menționată explicit e cea a facturilor simplificate, emise conform art. 319 alin. (12) din Codul fiscal (de regulă, bonuri fiscale care îndeplinesc condițiile unei facturi simplificate) — nu există o excepție legată de dimensiunea sau vechimea firmei.
- Obligația vizează strict relația **B2B între persoane stabilite în România** — pentru livrări/prestări către persoane care nu sunt stabilite și nici înregistrate în scopuri de TVA în România, se aplică regulile generale de facturare de la art. 319 din Codul fiscal, nu obligația de transmitere prin RO e-Factura.

## Ce se greșește în practică

- Se presupune că o firmă nou-înființată are o perioadă de „acomodare" înainte de a intra sub obligația RO e-Factura — legea nu prevede o astfel de perioadă de grație legată de vechimea firmei.
- Se aplică obligația RO e-Factura și facturilor simplificate (de exemplu, bonurilor fiscale care întrunesc condițiile unei facturi simplificate) — acestea sunt explicit exceptate.
- Se confundă relația B2B (între două persoane impozabile stabilite în România) cu o livrare către un client dintr-un alt stat membru sau către o persoană nestabilită/neînregistrată în România — pentru aceste din urmă situații se aplică regulile generale de facturare, nu obligația RO e-Factura.

## Ce face iConta.eu

iConta.eu are o funcționalitate reală de generare și transmitere a facturilor electronice prin sistemul RO e-Factura, în `core/efactura_send.py` (construirea XML-ului UBL 2.1/CIUS-RO) și `core/spv_rute.py`/`core/spv_conector.py` (transmiterea efectivă către SPV, în limita de 1.500 de apeluri/zi/CUI). Aplicația nu diferențiază firmele nou-înființate de cele existente — de îndată ce profilul firmei e configurat ca persoană impozabilă stabilită în România, facturile emise către alți parteneri din România pot fi transmise prin RO e-Factura, fără o perioadă de tranziție specială aplicată intern.

[iConta.eu](/)
