---
title: "Cum corelez D205 cu declarația unică a asociatului"
description: "Legătura dintre D205 (declarația firmei care plătește dividende) și Declarația unică (D212) depusă de asociatul persoană fizică pentru CASS — ce raportează fiecare și de ce nu se suprapun automat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corelez D205 cu declarația unică a asociatului

D205 și Declarația unică (D212) sunt două declarații diferite, depuse de două persoane diferite, cu scopuri diferite: D205 e depusă de **firmă** și informează ANAF cât impozit pe dividende a reținut la sursă; D212 e depusă de **asociatul persoană fizică** și stabilește dacă acesta mai datorează CASS pe veniturile din investiții (inclusiv dividendele încasate), în funcție de plafonul anual. Cele două nu se completează una din cealaltă automat — corelarea e o verificare pe care asociatul (sau contabilul lui) trebuie s-o facă manual.

## Temeiul legal

::: ghid-temei
„Persoanele fizice care în anul fiscal pentru care se depune declarația prevăzută la art. 122 au realizat venituri din cele prevăzute la art. 155 alin. (1) lit. c)-h), din una sau mai multe surse și/sau categorii de venituri, datorează contribuția de asigurări sociale de sănătate la o bază de calcul stabilită potrivit alin. (3), dacă în anul de realizare a veniturilor valoarea cumulată a acestora este cel puțin egală cu 6 salarii minime brute pe țară."
— Legea 227/2015, art. 170 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă practic această legătură:

- **D205** raportează, pe fiecare beneficiar, dividendul brut plătit și impozitul de 16% reținut la sursă de firmă (art. 97 alin. (7) Cod fiscal) — e o declarație informativă a plătitorului, nu una a asociatului.
- **CASS pe dividende** se calculează separat, de asociat, prin D212, doar dacă veniturile lui din investiții (categoria din art. 155 alin. (1) lit. g), care include dividendele) cumulate cu alte venituri de aceeași natură (dobânzi, câștiguri din instrumente financiare) depășesc pe an pragul de 6 salarii minime brute pe țară.
- Dividendul reținut prin D205 **nu e diminuat automat cu CASS** — asociatul primește suma netă de impozitul pe dividende (16%), iar CASS-ul (dacă se datorează) e o obligație suplimentară pe care el o declară și o plătește separat, prin D212.
- Sursa de adevăr pentru „cât am încasat ca dividende în anul X" e D205-ul emis de firmă (sau extrasul de cont/nota contabilă 457), pe care asociatul trebuie să-l ceară de la firmă înainte să completeze D212.

## Ce se greșește în practică

- Se presupune că, din moment ce firma a depus D205 și a reținut impozitul pe dividende, asociatul nu mai are nimic de declarat — se omite verificarea plafonului CASS din D212.
- Se calculează plafonul de 6 salarii minime brute doar din dividendele unei singure firme, ignorând obligația de cumulare cu veniturile din investiții realizate din alte surse (alte firme, dobânzi, câștiguri de capital).
- Se depune D212 pe baza sumei nete încasate în cont, nu pe baza dividendului brut din D205 — CASS se calculează la baza stabilită de lege (nivelul de 6/12/24 salarii minime, nu venitul brut efectiv, dacă acesta din urmă depășește plafonul).

## Ce face iConta.eu

iConta.eu generează D205 pentru firmă, cu calculul impozitului pe dividende pe fiecare distribuire și plată (atribuire FIFO pe data distribuirii, ca impozitul să se aplice la cota corectă). Aplicația poate genera și D212, dar **declarația unică e o declarație manuală**: iConta nu ține un registru de persoane fizice și nu le cunoaște veniturile totale din investiții din alte surse, așa că nu poate stabili singură dacă asociatul a depășit plafonul CASS — valorile (venituri, baze, CASS deja calculat) trebuie introduse de utilizator în formularul D212. Corelarea între suma din D205 și baza CASS declarată în D212 rămâne o verificare manuală a contabilului sau a asociatului.

[iConta.eu](/)
