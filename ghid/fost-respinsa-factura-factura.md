---
title: "De ce mi-a fost respinsă factura în e-Factura?"
description: Cum se identifică, punctual, motivul real al respingerii unei facturi emise, deosebit de eșecul de încărcare sau de starea de procesare încă în curs.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# De ce mi-a fost respinsă factura în e-Factura?

Prima verificare, la o factură emisă pe care o credeți respinsă, este să vă asigurați că vorbiți despre respingere propriu-zisă — un verdict nefavorabil primit de la ANAF — și nu despre o factură care nici măcar nu a ajuns la ANAF (eroare de încărcare) sau despre una încă în așteptarea unui verdict.

## Temeiul legal

::: ghid-temei
"În situaţia în care factura electronică transmisă nu respectă structura prevăzută la alin. (1), emitentul primeşte mesaj cu erorile identificate. După corectarea erorilor identificate, factura electronică se transmite în cadrul aceluiaşi sistem naţional privind factura electronică RO e-Factura."
— OUG 120/2021, art. 4 alin. (5)
:::

Legea leagă respingerea strict de nerespectarea structurii cerute a facturii electronice, caz în care se generează un mesaj cu erorile identificate. Acest mesaj este specific fiecărei facturi — depinde de ce anume, concret, nu respectă structura cerută în cazul dumneavoastră.

## Ce se greșește în practică

- Se confundă o respingere reală (verdict nefavorabil primit de la ANAF, după interogarea stadiului) cu un eșec de încărcare (factura nu a ajuns deloc la ANAF) — primul caz are un mesaj de eroare de citit, al doilea nu are, pentru că nu a existat un răspuns ANAF de interogat.
- Se trage concluzia de respingere prematur, cât timp factura e încă "în prelucrare" — starea de procesare nu e o respingere, e doar absența, deocamdată, a unui verdict.
- Se ignoră textul exact al mesajului de eroare primit și se caută răspunsul în surse generale, deși motivul concret e specific facturii respective și trebuie citit direct din mesajul returnat de ANAF.

## Ce face iConta.eu

Când interogarea periodică a stadiului la ANAF întoarce un verdict nefavorabil pentru o factură emisă, iConta.eu marchează trimiterea ca respinsă și salvează mesajul de eroare exact așa cum a fost primit de la ANAF — acesta este locul unde se găsește motivul real, specific facturii dumneavoastră. Aplicația distinge intern această situație atât de eșecul de încărcare (factura netransmisă la ANAF), cât și de starea de procesare încă în curs — cele trei situații sunt marcate diferit, nu se confundă în evidența internă a trimiterii.

Menționăm onest o limitare: iConta.eu nu interpretează sau "traduce" mesajul de eroare al ANAF într-o explicație proprie, standardizată — îl salvează brut, exact cum a fost primit, pentru că nu există, la acest moment, un catalog local confirmat de coduri de eroare e-Factura care să permită o astfel de traducere automată și sigură.

[iConta.eu](/)
