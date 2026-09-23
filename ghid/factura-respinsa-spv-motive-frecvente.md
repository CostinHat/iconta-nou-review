---
title: "e-Factura respinsă de SPV: motive frecvente"
description: Ce forme de răspuns confirmate există pentru o respingere e-Factura și de ce nu există un catalog oficial de coduri de eroare de consultat în avans.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# e-Factura respinsă de SPV: motive frecvente

Legea descrie respingerea unei facturi electronice ca pe un "mesaj cu erorile identificate", fără să enumere coduri sau categorii standard de eroare. În practică, un sistem care interoghează ANAF poate confirma doar felul în care răspunsul ANAF se prezintă tehnic — nu o listă exhaustivă de "motive de respingere" garantată complet.

## Temeiul legal

::: ghid-temei
"În situaţia în care factura electronică transmisă nu respectă structura prevăzută la alin. (1), emitentul primeşte mesaj cu erorile identificate. După corectarea erorilor identificate, factura electronică se transmite în cadrul aceluiaşi sistem naţional privind factura electronică RO e-Factura."
— OUG 120/2021, art. 4 alin. (5)
:::

Singurul temei legal pentru respingere este acesta: dacă structura facturii nu respectă formatul cerut, emitentul primește un mesaj cu erorile identificate. Legea nu numerotează și nu clasifică aceste erori — textul mesajului variază de la caz la caz, în funcție de ce anume nu respectă structura cerută.

## Ce se greșește în practică

- Se caută un "catalog oficial" de coduri de eroare e-Factura, presupunând că fiecare respingere are un cod numeric standardizat, documentat public — un asemenea catalog complet, oficial, disponibil pentru consultare nu a fost confirmat ca existent.
- Se ignoră textul exact al mesajului returnat de ANAF pentru factura respinsă, în favoarea unor explicații generice găsite în altă parte, care pot să nu corespundă cazului real.
- Se tratează orice text care nu e clar "ok" ca fiind automat o respingere fermă — există și un răspuns care nu se încadrează în niciun tipar cunoscut (o formă neconformă, neașteptată), caz în care starea facturii nu avansează, dar nici nu e clasificată explicit drept respinsă.

## Ce face iConta.eu

La interogarea periodică a stadiului fiecărei facturi emise, iConta.eu clasifică automat răspunsul primit de la ANAF: dacă textul conține indicația de procesare în curs, factura rămâne "în prelucrare" (sau trece la "investigație" dacă durata depășește pragul intern); dacă textul confirmă explicit acceptarea, factura e marcată "ok"; dacă textul indică un verdict nefavorabil sau conține mențiunea de eroare, factura e marcată "nok" și mesajul de eroare este salvat exact așa cum a fost primit. Dacă răspunsul ANAF nu se încadrează în niciunul din aceste tipare cunoscute, aplicația nu avansează starea facturii spre "acceptat" — o tratează prudent, ca formă neașteptată, și păstrează starea anterioară, fără să o marcheze verde.

Trebuie spus onest: iConta.eu nu deține un catalog propriu, complet, de coduri sau texte de eroare pentru toate respingerile posibile din e-Factura — un asemenea catalog nu a fost confirmat ca existent nici la nivel de sursă legală, nici public la ANAF. Motivul exact al fiecărei respingeri se citește din mesajul brut, real, primit de la ANAF pentru acea factură.

[iConta.eu](/)
