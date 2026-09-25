---
title: "Ce fac dacă am emis factura cu data greșită în e-Factura?"
description: "Cum se corectează o factură electronică deja transmisă în RO e-Factura, potrivit regulilor Codului fiscal pentru documentele care modifică o factură inițială."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă am emis factura cu data greșită în e-Factura?

O factură transmisă deja în sistemul RO e-Factura nu poate fi „ștearsă" sau editată retroactiv — sistemul funcționează pe principiul imutabilității documentelor transmise. Corectarea unei date greșite se face printr-un document nou, care se referă explicit la factura inițială.

## Temeiul legal

::: ghid-temei
„Orice document sau mesaj care modifică și care se referă în mod specific și fără ambiguități la factura inițială are același regim juridic ca o factură."
— Legea 227/2015 (Codul fiscal), art. 319 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă practic pentru o factură cu data greșită:

- Corectarea se face printr-o factură de corecție/stornare, care trebuie să facă trimitere clară și fără ambiguități la factura inițială greșită (număr, serie, dată) — nu printr-o simplă reemitere cu aceleași date, fără legătură vizibilă cu documentul corectat.
- Documentul de corecție are, potrivit legii, același regim juridic ca o factură propriu-zisă — deci trebuie și el transmis în RO e-Factura, cu respectarea acelorași termene de transmitere ca orice altă factură.
- Dacă eroarea de dată a afectat baza de impozitare sau TVA (de exemplu, a mutat operațiunea într-o altă perioadă fiscală), corecția poate influența și declarațiile deja depuse pentru perioada respectivă — nu doar factura în sine.

## Ce se greșește în practică

- Se emite o factură nouă, cu numărul următor din serie, fără nicio referire explicită la factura greșită — ceea ce lasă în circuit două documente contradictorii, fără o legătură formală între ele.
- Se presupune că o factură cu dată greșită, dar netransmisă încă în RO e-Factura, poate fi pur și simplu editată — odată emisă (numerotată), factura nu se mai poate „edita", ci doar corecta printr-un document nou.
- Se ignoră impactul asupra declarațiilor de TVA deja depuse, dacă eroarea de dată a mutat operațiunea într-o altă lună fiscală.

## Ce face iConta.eu

iConta.eu are un modul de emitere și transmitere a facturilor în RO e-Factura, iar pentru corectarea unei facturi deja emise, fluxul standard e emiterea unei facturi de stornare/corecție care face trimitere la documentul inițial. Aplicația nu detectează automat erorile de dată dintr-o factură deja transmisă — semnalarea și corectarea rămân o acțiune inițiată de contabil, pe baza propriei verificări.

[iConta.eu](/)
