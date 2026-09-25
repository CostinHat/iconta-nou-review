---
title: "Ce fac dacă PDF-ul facturii diferă de XML-ul din e-Factura?"
description: "Pași practici când PDF-ul unei facturi arată sume diferite față de XML-ul din RO e-Factura: care document contează legal și cum verifici sursa diferenței."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă PDF-ul facturii diferă de XML-ul din e-Factura?

Observi o sumă diferită între PDF-ul unei facturi și XML-ul ei din RO e-Factura și nu știi ce să faci mai departe. Iată, pe scurt, care document e valabil legal și cum verifici practic ce a cauzat diferența.

## Temeiul legal

::: ghid-temei
„Exemplarul original al facturii electronice se consideră fişierul de tip XML însoţit de semnătura electronică a Ministerului Finanţelor."
— OUG 120/2021 (RO e-Factura), art. 4 alin. (6) (sursă: anaf_surse/oug_120_2021.txt)
:::

- Documentul cu valoare juridică e XML-ul semnat electronic de Ministerul Finanțelor, descărcabil din portalul SPV/ANAF — nu PDF-ul.
- Pasul practic corect: deschide factura în portalul SPV, descarcă XML-ul semnat și compară sumele de acolo (nu din PDF) cu cele raportate în contabilitate.
- Dacă diferența e de ordinul bănuților și apare la linii cu prețuri cu mai multe zecimale (de exemplu preț rezultat dintr-un discount sau dintr-o conversie valutară), cauza probabilă e tehnică — o rotunjire diferită — nu o greșeală de operare.

## Ce se greșește în practică

- Se corectează manual suma din contabilitate după PDF, în loc de XML — deși XML-ul e cel valabil.
- Se ignoră diferența, pe motiv că e „doar un bănuț" — la volume mari de facturi, aceste diferențe se pot cumula și pot genera neconcordanțe la reconcilierea TVA colectată.
- Se raportează diferența ca „bug la ANAF", fără să se verifice mai întâi dacă sursa e chiar aplicația care a generat cele două documente.

## Ce face iConta.eu

Cauza tehnică e confirmată în codul aplicației, nu doar teoretică: PDF-ul facturii (`core/pdf_util.py::bani`) rotunjește sumele fără să specifice metoda de rotunjire, ceea ce face Python să aplice implicit rotunjirea bancară (ROUND_HALF_EVEN). XML-ul pentru e-Factura (`core/efactura_send.py::_bani`) rotunjește explicit cu ROUND_HALF_UP, regula pe care aplicația o cere pentru orice sumă fiscală.

Concret: la 3 bucăți × 3,335 lei/bucată (bază de calcul 10,005 lei), PDF-ul arată 10,00 lei, iar XML-ul arată 10,01 lei — din același rând de date, fără nicio intervenție manuală. Ce poți face acum, până la o reparație: tratează întotdeauna suma din XML (verificată în SPV) ca fiind cea corectă; dacă diferența afectează un total raportat, corectează manual reconcilierea, nu factura. Nu există în acest moment în aplicație o atenționare automată care să semnaleze o astfel de divergență între cele două documente — depistarea ei rămâne, deocamdată, manuală.

[iConta.eu](/)
