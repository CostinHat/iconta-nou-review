---
title: "Un PFA la normă de venit trebuie să folosească e-Factura?"
description: "Obligația de transmitere prin RO e-Factura în relația B2C se aplică indiferent de sistemul de impunere sau de înregistrarea în scopuri de TVA."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Un PFA la normă de venit trebuie să folosească e-Factura?

Da. Modul în care este determinat venitul impozabil — normă de venit sau sistem real — nu are nicio legătură cu obligația de a folosi RO e-Factura. Legea leagă obligația de calitatea de persoană impozabilă stabilită în România, nu de sistemul de impunere a venitului.

## Temeiul legal

::: ghid-temei
„(2) Începând cu data de 1 ianuarie 2025, operatorii economici - persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015 [...], indiferent dacă sunt sau nu înregistraţi în scopuri de TVA conform art. 316 din Legea nr. 227/2015 [...], pentru livrările de bunuri şi prestările de servicii care au locul livrării/prestării în România [...], efectuate în relaţia B2C [...], au obligaţia să transmită facturile emise în sistemul naţional privind factura electronică RO e-Factura. Fac excepţie bonurile fiscale emise în conformitate cu prevederile Ordonanţei de urgenţă a Guvernului nr. 28/1999 [...] care îndeplinesc condiţiile unei facturi simplificate [...]"
— OUG nr. 120/2021, art. 10^1 alin. (2), astfel cum a fost modificat prin OUG nr. 138/2024 (sursă: anaf_surse/oug_138_2024.txt)
:::

Textul rezolvă direct întrebarea:

- Obligația privește orice „persoană impozabilă stabilită în România", formulă care include un PFA indiferent de forma de impunere a venitului (normă de venit sau sistem real) — legea nu face nicio distincție în acest sens.
- Legea precizează explicit „indiferent dacă sunt sau nu înregistraţi în scopuri de TVA" — deci nici neînregistrarea ca plătitor de TVA (frecventă la PFA-urile mici, inclusiv la normă de venit) nu scutește de obligație.
- Singura excepție reală este cea a bonurilor fiscale care îndeplinesc condițiile unei facturi simplificate — nu ține de sistemul de impunere al emitentului, ci de tipul documentului emis către client.

## Ce se greșește în practică

- Se presupune că un PFA la normă de venit, tocmai fiindcă nu are contabilitate în partidă dublă și nu depune deconturi de TVA, este automat scutit de RO e-Factura — obligația nu depinde de acestea.
- Se confundă pragul de la care un PFA devine plătitor de TVA cu pragul de la care devine obligat să folosească RO e-Factura — sunt praguri și criterii diferite; obligația RO e-Factura se aplică de la 1 ianuarie 2025, indiferent de statutul de TVA.
- Se emit facturi „pe hârtie" sau în format liber (PDF, Word) fără transmitere prin sistem, crezând că simplitatea activității scutește de formalități — obligația legală rămâne aceeași ca pentru orice altă persoană impozabilă.

## Ce face iConta.eu

iConta.eu nu face nicio distincție, în modulul de facturare electronică, între un PFA la normă de venit și alți emitenți de facturi — generarea și transmiterea XML-ului prin RO e-Factura (`core/efactura_send.py`) urmează aceleași reguli pentru toți utilizatorii care emit facturi din aplicație, indiferent de forma de organizare sau de sistemul de impunere a venitului. Aplicația nu oferă, la acest moment, o funcție separată de verificare automată a încadrării fiecărui utilizator în categoriile de obligativitate din lege — aceasta rămâne responsabilitatea contribuabilului sau a contabilului său.

[iConta.eu](/)
