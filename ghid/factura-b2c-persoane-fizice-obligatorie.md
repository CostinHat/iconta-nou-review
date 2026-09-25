---
title: "e-Factura B2C către persoane fizice: este obligatorie"
description: "Din 1 ianuarie 2025, transmiterea facturilor către persoane fizice prin RO e-Factura este obligatorie, indiferent de înregistrarea în scopuri de TVA a emitentului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# e-Factura B2C către persoane fizice: este obligatorie

Da, este obligatorie — nu mai este o opțiune, așa cum a fost la început. De la 1 ianuarie 2025, orice persoană impozabilă stabilită în România trebuie să transmită prin RO e-Factura și facturile emise către persoane fizice.

## Temeiul legal

::: ghid-temei
„(2) Începând cu data de 1 ianuarie 2025, operatorii economici - persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015 [...], indiferent dacă sunt sau nu înregistraţi în scopuri de TVA [...], pentru livrările de bunuri şi prestările de servicii care au locul livrării/prestării în România [...], efectuate în relaţia B2C [...], au obligaţia să transmită facturile emise în sistemul naţional privind factura electronică RO e-Factura. Fac excepţie bonurile fiscale emise în conformitate cu prevederile Ordonanţei de urgenţă a Guvernului nr. 28/1999 [...] care îndeplinesc condiţiile unei facturi simplificate [...]"
— OUG nr. 120/2021, art. 10^1 alin. (2), text introdus prin OUG nr. 138/2024 (sursă: anaf_surse/oug_138_2024.txt)

„(3) Livrările de bunuri/Prestările de servicii efectuate către o persoană fizică care nu se identifică în relaţia cu furnizorul/prestatorul prin niciun cod de identificare fiscală sau optează să se identifice prin codul numeric personal se consideră efectuate în relaţia B2C, cu excepţia situaţiei în care beneficiarii sunt înscrişi în Registrul RO e-Factura obligatoriu. Dacă beneficiarul, persoană fizică, nu se identifică prin niciun cod de identificare fiscală, facturile se emit utilizând un cod format din 13 cifre de zero în locul codului de identificare fiscală al beneficiarului."
— OUG nr. 120/2021, art. 10^1 alin. (3), astfel cum a fost modificat prin OUG nr. 89/2025 (sursă: anaf_surse/oug_89_2025.txt)
:::

Ce rezultă concret pentru relația cu persoanele fizice:

- Obligația este generală, de la 1 ianuarie 2025, și nu depinde de faptul că emitentul este sau nu plătitor de TVA.
- O livrare/prestare este considerată B2C atunci când beneficiarul persoană fizică nu se identifică prin niciun cod fiscal, sau optează să se identifice prin codul numeric personal (nu prin CUI, dacă ar avea, de exemplu, calitatea de PFA într-o altă tranzacție) — **cu excepția** cazului în care acel beneficiar e înscris în Registrul RO e-Factura obligatoriu, adăugată prin OUG 89/2025: atunci tranzacția nu mai e tratată ca B2C, chiar dacă persoana fizică s-a identificat prin CNP.
- Dacă beneficiarul persoană fizică nu comunică niciun cod de identificare fiscală, factura se emite folosind un cod format din 13 cifre de zero în locul codului fiscal al beneficiarului — o regulă tehnică introdusă tocmai pentru a permite transmiterea facturii chiar și fără identificator fiscal al clientului.
- Excepția rămâne aceeași ca la B2B: bonurile fiscale care îndeplinesc condițiile unei facturi simplificate nu trebuie transmise separat prin sistem.

## Ce se greșește în practică

- Se presupune că facturile către persoane fizice rămân opționale, așa cum a fost cazul înainte de 1 ianuarie 2025 — obligația s-a schimbat, iar practica veche nu se mai aplică.
- Se refuză emiterea facturii electronice către un client persoană fizică fără CNP sau alt cod fiscal, deși legea prevede explicit mecanismul codului de 13 cifre de zero tocmai pentru acest caz.
- Se transmite eronat prin sistem un bon fiscal care ar fi trebuit exceptat, sau invers, nu se transmite o factură B2C obișnuită, confundând cele două categorii de documente.

## Ce face iConta.eu

Modulul de generare a facturii electronice (`core/efactura_send.py`) nu face o distincție separată de tratament între facturile B2B și cele B2C — orice factură emisă din aplicație, indiferent de tipul beneficiarului, este transmisă prin RO e-Factura conform structurii CIUS-RO. Pentru clienții persoane fizice fără cod fiscal comunicat, câmpul de identificare a beneficiarului urmează regula generală a schemei — aplicația nu generează încă automat codul convențional de 13 cifre de zero în absența oricărui identificator introdus de utilizator, aceasta rămânând o zonă în care emitentul trebuie să completeze corect datele clientului la introducerea facturii.

[iConta.eu](/)
