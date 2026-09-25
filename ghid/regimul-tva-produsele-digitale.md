---
title: "Regimul de TVA pentru produsele digitale"
description: "Unde se taxează serviciile furnizate pe cale electronică vândute către persoane neimpozabile, conform Codului fiscal, și de ce contează statutul clientului."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Regimul de TVA pentru produsele digitale

„Produsele digitale" — abonamente software, e-book-uri, cursuri online, aplicații — sunt din punct de vedere fiscal servicii furnizate pe cale electronică, iar Codul fiscal le tratează cu o regulă specială de stabilire a locului taxării, diferită de regula generală.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile alin. (3), locul următoarelor servicii este considerat a fi: [...] h) locul unde beneficiarul este stabilit, își are domiciliul stabil sau reședința obișnuită, în cazul următoarelor servicii prestate către o persoană neimpozabilă: 1. serviciile de telecomunicații; 2. serviciile de radiodifuziune și televiziune; 3. serviciile furnizate pe cale electronică."
— Legea 227/2015 (Codul fiscal), art. 278 alin. (5) lit. h) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă practic pentru un furnizor român de produse digitale:

- când clientul e o **persoană neimpozabilă** (de regulă, o persoană fizică ce nu acționează în scop profesional), TVA se datorează în statul unde acel client e stabilit, are domiciliul sau reședința obișnuită — nu în România, dacă clientul e din alt stat membru UE;
- pentru a nu se înregistra separat în TVA în fiecare stat membru unde are clienți persoane fizice, furnizorul poate folosi **regimul special UE** (OSS — One Stop Shop), reglementat la art. 315 din Codul fiscal, și declara/plăti centralizat, prin organul fiscal din România, TVA-ul datorat în toate statele membre de consum;
- când clientul e o **persoană impozabilă** (firmă, PFA, altă entitate care acționează ca atare), se aplică regula generală de la art. 278 alin. (2) — locul prestării e unde e stabilit beneficiarul, iar factura se emite de regulă fără TVA românesc, cu taxare inversă la client (dacă e stabilit în alt stat membru și înregistrat în scopuri de TVA);
- calificarea corectă a clientului (impozabil vs. neimpozabil) e cheia întregului regim — o greșeală aici schimbă complet statul de taxare și obligațiile declarative.

## Ce se greșește în practică

- Se facturează cu TVA românesc orice vânzare de produs digital, indiferent de țara clientului persoană fizică — dacă acesta e stabilit în alt stat membru UE, TVA se datorează acolo, nu în România (cu excepția cazului în care furnizorul se încadrează la plafonul de scutire pentru întreprinderile mici aplicabil transfrontalier, unde există reguli separate).
- Se confundă „vânzare online" cu „serviciu prestat pe cale electronică" — un curs livrat live, cu interacțiune umană în timp real, nu e considerat serviciu electronic în sensul acestei reguli, ci prestare de servicii educaționale, cu alt loc de taxare.
- Se amână înregistrarea în regimul special UE (OSS) până la depășirea unui plafon perceput intuitiv, fără verificarea pragului legal de 10.000 euro pentru vânzările intracomunitare la distanță și serviciile electronice B2C, sub care se poate aplica taxarea în statul de origine.

## Ce face iConta.eu

iConta.eu poate genera declarația D398 (regimurile speciale OSS — art. 314, 315 și 315^2 din Codul fiscal, `core/d398.py`), dar aceasta e o declarație strict manuală: aplicația nu ține evidența operațiunilor OSS pe stat de consum și cotă străină, iar toate valorile vin din datele introduse direct de contabil (`manual`), nu din facturile emise. Nu există, la data acestui ghid, nicio funcție care să clasifice automat o factură ca „serviciu furnizat pe cale electronică" în sensul art. 278 alin. (5) lit. h) și să determine astfel locul de taxare — calificarea corectă a serviciului și a statutului clientului, precum și alegerea sumelor raportate în D398, rămân o decizie manuală a contabilului.

[iConta.eu](/)
