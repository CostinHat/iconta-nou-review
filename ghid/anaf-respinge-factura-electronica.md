---
title: "Ce fac dacă ANAF respinge factura electronică?"
description: Ce înseamnă un verdict nefavorabil ("nok") la o factură emisă transmisă prin RO e-Factura, ce documentează sistemul la respingere și ce trebuie făcut mai departe.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce fac dacă ANAF respinge factura electronică?

Când ANAF răspunde, la interogarea stadiului unei facturi emise, cu un verdict nefavorabil, factura respectivă nu poate fi "reparată" în cadrul aceleiași trimiteri — trebuie corectată și retrimisă ca o transmitere nouă, în urma corectării erorilor semnalate.

## Temeiul legal

::: ghid-temei
"În situaţia în care factura electronică transmisă nu respectă structura prevăzută la alin. (1), emitentul primeşte mesaj cu erorile identificate. După corectarea erorilor identificate, factura electronică se transmite în cadrul aceluiaşi sistem naţional privind factura electronică RO e-Factura."
— OUG 120/2021, art. 4 alin. (5)
:::

Legea descrie explicit doar procedura: la o structură incorectă, emitentul primește un mesaj cu erorile identificate, corectează și retrimite. Legea nu enumeră coduri de eroare concrete sau categorii standardizate de respingere — orice cod sau text de eroare pe care îl vedeți trebuie să provină din răspunsul real primit de la ANAF pentru factura dumneavoastră, nu dintr-un catalog general.

## Ce se greșește în practică

- Se așteaptă ca o factură respinsă să poată fi "corectată în loc" și retransmisă automat sub aceeași trimitere — nu e cazul: respingerea e un verdict terminal pentru acea trimitere, corecția presupune o transmitere nouă.
- Se ignoră mesajul de eroare returnat efectiv de ANAF și se caută explicații generice, deși singura sursă de adevăr pentru motivul respingerii este textul brut primit de la ANAF pentru acea factură anume.
- Se presupune existența unui catalog fix, numerotat, de coduri de eroare pentru respingerile din e-Factura — un asemenea catalog nu a fost identificat ca disponibil oficial; textul erorii trebuie citit direct, caz cu caz.

## Ce face iConta.eu

Când interogarea periodică a stadiului la ANAF întoarce un verdict nefavorabil pentru o factură emisă, iConta.eu marchează trimiterea respectivă ca respinsă, descarcă recipisa aferentă (dacă e disponibilă) și salvează mesajul de eroare exact așa cum a fost primit de la ANAF, fără interpretare sau reformulare. Acest mesaj brut este dovada de bază pentru a înțelege ce anume trebuie corectat înainte de retrimitere.

Menționăm onest o limitare: iConta.eu nu deține și nu afișează un catalog propriu de coduri de eroare e-Factura cu explicații standardizate pentru fiecare cod posibil — motivul respingerii trebuie citit din mesajul returnat efectiv de ANAF pentru fiecare factură în parte, iar corectarea și retrimiterea rămân un pas manual, realizat de utilizator, pe baza acelui mesaj.

[iConta.eu](/)
