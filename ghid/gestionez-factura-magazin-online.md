---
title: "Cum gestionez e-Factura pentru un magazin online?"
description: "Facturile emise din comenzile unui magazin online nu au un regim legal separat de e-Factura: obligația de transmitere depinde de calitatea cumpărătorului, nu de canalul de vânzare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum gestionez e-Factura pentru un magazin online?

O comandă plasată printr-un magazin online (WooCommerce sau orice altă platformă) devine, contabil, o factură ca oricare alta. Legea nu prevede un regim separat de e-Factura pentru comerțul online — obligația de transmitere prin sistemul RO e-Factura depinde de cine e cumpărătorul, nu de canalul prin care a fost plasată comanda.

## Temeiul legal

::: ghid-temei
„În relaţia comercială B2B, între persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015, [...] emitentul facturii electronice are obligaţia de transmitere a acesteia către destinatar utilizând sistemul naţional privind factura electronică RO e-Factura, cu respectarea prevederilor art. 4 alin. (1). Fac excepţie facturile simplificate emise conform art. 319 alin. (12) din Legea nr. 227/2015."
— OUG 120/2021, art. 10 alin. (1), forma modificată prin Legea 296/2023 (sursă: anaf_surse/oug_115_2023_consolidat.html)
:::

- Obligația de transmitere prin RO e-Factura, în forma actuală (de la Legea 296/2023), vizează relația **B2B** — între persoane impozabile stabilite în România.
- Ce declanșează obligația e statutul cumpărătorului (persoană impozabilă înregistrată în România), nu platforma prin care s-a plasat comanda — un magazin online nu are, legal, un regim distinct.
- Fac excepție facturile simplificate emise conform art. 319 alin. (12) din Codul fiscal — tipic, vânzările cu amănuntul de valoare mică, cu bon fiscal.

## Ce se greșește în practică

- Se presupune că orice factură emisă dintr-un magazin online trebuie transmisă automat în e-Factura, indiferent cine e cumpărătorul — de fapt încadrarea depinde de calitatea beneficiarului (persoană impozabilă înregistrată vs. consumator final).
- Se confundă „factura a fost emisă/generată automat din comandă" cu „factura a fost transmisă la ANAF" — sunt două operațiuni distincte, fiecare cu propriile verificări.
- Se ignoră faptul că majoritatea comenzilor unui magazin online provin de la persoane fizice, ceea ce schimbă încadrarea față de o factură emisă către o firmă parteneră.

## Ce face iConta.eu

Conectorul WooCommerce din iConta.eu (ecranul „Magazin online", configurare URL + chei API și buton „Sincronizează acum") produce **facturi interne** din comenzile magazinului. Verificat direct în codul sursă: modulul care face conversia comandă → factură (`core/woocommerce.py`) nu conține nicio linie legată de e-Factura, SPV sau UBL. Conectorul tratează, prin decizie de produs asumată explicit în cod, orice comandă preluată ca venind de la o persoană fizică fără cod fiscal.

Odată create, facturile din comenzile WooCommerce intră în același flux general de facturare ca oricare altă factură din aplicație — inclusiv, unde e cazul, transmiterea către RO e-Factura, care rămâne însă o funcționalitate separată, cu propriile verificări. Conectorul WooCommerce **nu declanșează** automat nicio transmitere la SPV: el doar alimentează fluxul de facturare cu documentele rezultate din comenzi.

[iConta.eu](/)
