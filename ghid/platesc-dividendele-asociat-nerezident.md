---
title: "Cum se plătesc dividendele către un asociat nerezident?"
description: Contabilizarea e aceeași ca la un asociat rezident (conturile 457/456), dar cota de impozit și declarația diferă — și verificarea unei eventuale convenții de evitare a dublei impuneri rămâne manuală.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se plătesc dividendele către un asociat nerezident?

Din punct de vedere contabil, plata dividendului unui asociat nerezident nu diferă structural de plata către un asociat rezident — aceleași conturi (457 „Dividende de plată" pentru dividende anuale, 456 pentru interimare). Diferența reală apare în două locuri: cota de impozit reținut (poate fi redusă printr-o convenție de evitare a dublei impuneri) și declarația în care se raportează (D207, nu D205).

## Temeiul legal

::: ghid-temei
„Impozitul datorat se calculează prin aplicarea următoarelor cote asupra veniturilor brute: […] b) 16% pentru veniturile din dividende prevăzute la art. 223 alin. (1) lit. a);"
— Codul fiscal, Legea 227/2015, art. 224 alin. (4) lit. b), modificată prin Legea 141/2025, art. II pct. 41, aplicabilă dividendelor distribuite începând cu 1 ianuarie 2026
:::

::: ghid-temei
„În înţelesul art. 224, dacă un contribuabil este rezident al unei ţări cu care România a încheiat o convenţie pentru evitarea dublei impuneri, cota de impozit care se aplică venitului impozabil obţinut de către acel contribuabil din România nu poate depăşi cota de impozit prevăzută în convenţia care se aplică asupra acelui venit. […] nerezidentul are obligaţia de a prezenta plătitorului de venit, în momentul plăţii venitului, certificatul de rezidenţă fiscală eliberat de către autoritatea competentă din statul său de rezidenţă"
— Codul fiscal, Legea 227/2015, art. 230 alin. (1)-(2)
:::

Cota internă e 16% (de la 1 ianuarie 2026, aceeași cu cea aplicată rezidenților), dar dacă asociatul nerezident prezintă firmei, la momentul plății, certificatul de rezidență fiscală din statul său, se poate aplica o cotă mai favorabilă — cea din convenția de evitare a dublei impuneri, dacă e mai mică decât 16%. Fără certificat prezentat la timp, se aplică automat cota internă. Certificatul prezentat în cursul anului rămâne valabil și în primele 60 de zile calendaristice ale anului următor. Obligația de calcul, reținere, declarare și plată a impozitului revine firmei plătitoare (art. 224 alin. (1)), iar declararea, pentru fiecare beneficiar nerezident, se face prin D207, nu prin D205.

## Ce se greșește în practică

- Se aplică automat cota de 16%, fără să se verifice dacă asociatul a prezentat certificatul de rezidență fiscală — dacă l-a prezentat și există o convenție mai favorabilă, cota corectă poate fi mai mică.
- Se contabilizează dividendul plătit unui nerezident exact ca pentru un rezident, dar apoi se raportează, din obișnuință, pe D205 — dividendele către nerezidenți nu au ce căuta acolo, merg pe D207.
- Se presupune că verificarea sau aplicarea cotei convenționale se face automat de aplicație — nu e cazul; e o verificare pe care o face contabilul, cu documentele beneficiarului.

## Ce face iConta.eu

Contabilizarea plății (457=5121 pentru dividendul net, respectiv 457=446 pentru impozitul reținut, sau 456/463 pentru dividende interimare) se face prin motorul de decontări asociați (F039), care calculează automat impozitul la cota internă în vigoare (16% de la 1 ianuarie 2026) — **fără nicio logică specifică pentru asociatul nerezident**: modulul nu diferențiază cota internă de o eventuală cotă redusă prin convenție, așa că, dacă se aplică o convenție mai favorabilă, contabilul introduce manual impozitul corect calculat, nu cel generat implicit de aplicație. Obligația declarativă rezultată se acoperă separat, prin ecranul D207 (F209), unde se completează manual beneficiarul nerezident, venitul, statul de rezidență și actul normativ aplicat.

[iConta.eu](/)
