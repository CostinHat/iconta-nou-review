---
title: "O firmă plătitoare de impozit pe profit trebuie să folosească e-Factura?"
description: "Obligativitatea RO e-Factura în relația B2B depinde de faptul că firma este persoană impozabilă stabilită în România, nu de regimul de impozitare (micro sau profit) pe care îl aplică."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# O firmă plătitoare de impozit pe profit trebuie să folosească e-Factura?

Da. Obligativitatea sistemului RO e-Factura nu are legătură cu regimul de impozitare al firmei — se aplică deopotrivă firmelor plătitoare de impozit pe veniturile microîntreprinderilor și celor plătitoare de impozit pe profit, atât timp cât sunt persoane impozabile stabilite în România și realizează operațiuni B2B.

## Temeiul legal

::: ghid-temei
„În relația comercială B2B, între persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015, cu modificările și completările ulterioare, emitentul facturii electronice are obligația de transmitere a acesteia către destinatar utilizând sistemul național privind factura electronică RO e-Factura, cu respectarea prevederilor art. 4 alin. (1). Fac excepție facturile simplificate emise conform art. 319 alin. (12) din Legea nr. 227/2015."
— OUG nr. 120/2021, art. 10 alin. (1), introdus prin OUG nr. 115/2023 (sursă: anaf_surse/oug_115_2023_consolidat.txt)
:::

Criteriul legal pentru obligativitate este, deci, altul decât regimul de impozitare:

- Obligația de a transmite factura prin sistemul RO e-Factura revine **oricărei persoane impozabile stabilite în România**, în relația B2B cu o altă persoană impozabilă stabilită în România — indiferent dacă emitentul e plătitor de impozit micro, de impozit pe profit sau are alt statut fiscal.
- Termenul-limită de transmitere este de **5 zile lucrătoare** de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită legală de emitere a facturii (art. 319 alin. (16) Cod fiscal).
- Excepția principală este pentru **facturile simplificate** (art. 319 alin. (12) Cod fiscal), care nu intră sub această obligație.

## Ce se greșește în practică

- Se crede că firmele micro sunt exceptate de la e-Factura, pornind de la confuzia cu alte obligații (de exemplu casa de marcat sau anumite praguri de TVA) unde regimul micro poate avea reguli diferite — la e-Factura, criteriul e statutul de persoană impozabilă stabilită în România, nu regimul de impozit pe venit.
- Se presupune că obligația vizează doar firmele mari sau cele cu cifră de afaceri ridicată, deși legea nu prevede un prag valoric pentru obligativitatea B2B.
- Se omite transmiterea în termenul de 5 zile lucrătoare, tratând data facturii ca fiind suficientă pentru conformare.

## Ce face iConta.eu

iConta.eu emite facturi și le transmite în sistemul RO e-Factura direct din aplicație (modulele `efactura_send` și `efactura_trimitere` din motorul aplicației), indiferent de regimul de impozitare al firmei — micro sau profit. Firma rămâne responsabilă să confirme corectitudinea datelor de facturare și să urmărească eventualele erori raportate de sistemul ANAF.

[iConta.eu](/)
