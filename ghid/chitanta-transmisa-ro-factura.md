---
title: "Chitanța trebuie transmisă în RO e-Factura?"
description: "Excepția bonurilor fiscale de la obligația de transmitere prin RO e-Factura, atunci când îndeplinesc condițiile unei facturi simplificate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Chitanța trebuie transmisă în RO e-Factura?

Nu toate documentele fiscale emise către clienți trec prin RO e-Factura. Bonurile fiscale emise cu aparate de marcat electronice au un regim separat, explicit exceptat, atât timp cât îndeplinesc condițiile unei facturi simplificate.

## Temeiul legal

::: ghid-temei
„(1) În relaţia comercială B2B, între persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015 [...], emitentul facturii electronice are obligaţia de transmitere a acesteia către destinatar utilizând sistemul naţional privind factura electronică RO e-Factura [...]. Fac excepţie bonurile fiscale emise în conformitate cu prevederile Ordonanţei de urgenţă a Guvernului nr. 28/1999 privind obligaţia operatorilor economici de a utiliza aparate de marcat electronice fiscale, republicată, cu modificările şi completările ulterioare, care îndeplinesc condiţiile unei facturi simplificate, în conformitate cu prevederile art. 319 alin. (12), (13) şi (21) din Legea nr. 227/2015 [...]"
— OUG nr. 120/2021, art. 10 alin. (1), astfel cum a fost modificat prin OUG nr. 138/2024 (sursă: anaf_surse/oug_138_2024.txt)
:::

Excepția este condiționată, nu absolută:

- Bonul fiscal scapă de obligația de transmitere prin RO e-Factura **doar dacă** îndeplinește condițiile unei facturi simplificate prevăzute la art. 319 alin. (12), (13) și (21) din Codul fiscal — practic, condițiile de conținut minim (identificarea vânzătorului, data, valoarea, TVA) pentru sume sub un anumit plafon.
- Excepția se aplică atât în relația B2B, cât și în relația B2C, unde textul echivalent (art. 10^1) exceptează în mod identic bonurile fiscale care îndeplinesc condițiile unei facturi simplificate.
- Dacă un client cere, ulterior unei vânzări cu bon fiscal, o factură propriu-zisă (nu simplificată), acea factură intră sub regulile obișnuite de transmitere prin RO e-Factura, ca orice altă factură.

## Ce se greșește în practică

- Se transmite eronat orice bon fiscal prin RO e-Factura, „ca să fie sigur", deși legea îl exceptează explicit atunci când îndeplinește condițiile facturii simplificate — efort administrativ inutil.
- Se presupune că orice chitanță sau bon emis manual (nu prin casă de marcat fiscală) intră sub aceeași excepție — textul se referă strict la bonurile fiscale emise conform OUG 28/1999, adică prin aparate de marcat electronice fiscale.
- Se ignoră situația în care valoarea vânzării depășește plafonul facturii simplificate — în acel caz, bonul fiscal nu mai îndeplinește condițiile excepției, iar operațiunea trebuie documentată printr-o factură obișnuită, transmisă prin RO e-Factura.

## Ce face iConta.eu

La data acestui ghid, iConta.eu tratează bonurile fiscale ca operațiuni distincte de facturile electronice: aplicația are un modul separat de import date din casa de marcat (`core/amef_import.py`), dar nu leagă automat aceste încasări de fluxul de transmitere prin RO e-Factura, în acord cu excepția legală de mai sus. Pentru facturile propriu-zise, generarea și transmiterea prin RO e-Factura se fac prin `core/efactura_send.py`, conform structurii CIUS-RO.

[iConta.eu](/)
