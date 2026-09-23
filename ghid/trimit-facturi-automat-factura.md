---
title: "Cum trimit facturi automat în e-Factura"
description: Trimiterea nu e automată azi — fiecare factură emisă se transmite prin acțiune manuală, factură cu factură, fără mecanism de reîncercare la eșec. O spunem direct, nu ocolit.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum trimit facturi automat în e-Factura

Răspunsul corect, azi, e simplu de spus: **nu trimiți automat**, pentru că nu există în produs niciun mecanism care să trimită singur facturile la un interval de timp, și nici reîncercare automată la eșec.

## Temeiul legal

::: ghid-temei
„Termenul-limită pentru transmiterea facturilor în sistemul naţional privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită pentru emiterea facturii prevăzută la art. 319 alin. (16) din Legea nr. 227/2015... Calculul termenului-limită se efectuează conform Regulamentului (CEE, Euratom) nr. 1182/71 al Consiliului din 3 iunie 1971..." — OUG nr. 89/2025.
:::

Legea prevede obligația de transmitere într-un termen — 5 zile lucrătoare, din 2026 —, nu impune un mecanism tehnic anume prin care ea trebuie automatizată. Absența automatizării nu e o problemă de conformitate legală, atâta timp cât termenul e respectat prin trimiteri manuale la timp.

## Ce rulează automat, și ce nu

Trei procese programate rulează în fundal pentru e-Factura: reîmprospătarea tokenului de conectare (zilnic), urmărirea stării facturilor deja trimise (la 30 de minute) și descărcarea facturilor primite de la furnizori (tot la 30 de minute).

**Niciunul dintre aceste trei procese nu inițiază trimiterea unei facturi emise.** Upload-ul inițial se declanșează exclusiv prin click pe „Trimite în SPV", din ecranul de facturi — nu există un al patrulea proces programat care să facă asta în locul tău.

## Ce se întâmplă la un eșec de trimitere

Dacă upload-ul eșuează, factura rămâne marcată cu eroare de încărcare, vizibilă prin semaforul roșu din ecranul de facturi. Sistemul **nu reîncearcă singur**. Următoarea încercare trebuie inițiată tot manual, printr-un nou click — nu există o „coadă" care se autocorectează.

## Ce se greșește în practică

- Se presupune că, pentru că sistemul urmărește automat starea facturilor deja trimise, la fel se întâmplă și cu trimiterea inițială — urmărirea și declanșarea sunt lucruri separate.
- Se așteaptă un volum mare de facturi să fie trimis „la finalul zilei" fără intervenție, bazându-se pe o coadă automată inexistentă.
- Se ignoră semaforul roșu de eroare, presupunând că o retrimitere automată va rezolva mai devreme sau mai târziu — nu se va întâmpla singură.

## Ce face iConta.eu

Spunem clar: trimiterea inițială a unei facturi în SPV e o acțiune manuală, per factură, fără reîncercare automată la eșec. Automatizăm tot ce vine după click — validarea prealabilă, protecția împotriva trimiterii duble și urmărirea recipisei. Dacă lucrezi cu volum mare de facturi, planifică trimiterea și verificarea ca pe un pas manual recurent, nu ca pe ceva ce rulează singur.

[iConta.eu](/)
