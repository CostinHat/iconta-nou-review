---
title: "Serviciile prestate către un client din UE, scutite în statul lui, se declară în D390?"
description: "Nu. În D390 se raportează doar serviciile B2B care nu sunt scutite în statul clientului; se consideră scutite dacă ar fi scutite în România sau dacă există confirmare oficială."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Serviciile prestate către un client din UE, scutite în statul lui, se declară în D390?

Nu. Pentru serviciile cu locul prestării la client (regula generală B2B), prestatorul din România raportează în D390 doar serviciile care **nu sunt scutite** de TVA în statul membru în care sunt impozabile. Pentru a nu cere contabilului să cunoască legislația fiecărui stat, norma dă un criteriu simplu: serviciul se consideră scutit în statul clientului **dacă ar fi scutit în România**.

Există și situația inversă. Dacă serviciul nu este scutit în România, dar este scutit în statul clientului, prestatorul poate să nu îl declare numai dacă are o **confirmare oficială** de la autoritatea fiscală a acelui stat.

## Temeiul legal

::: ghid-temei
„prestările de servicii prevăzute la art. 278 alin. (2) efectuate în beneficiul unor persoane impozabile nestabilite în România, dar stabilite în Uniunea Europeană, altele decât cele scutite de TVA în statul membru în care acestea sunt impozabile, pentru care exigibilitatea de taxă a luat naștere în luna calendaristică respectivă;"
— Codul fiscal (Legea 227/2015), art. 325 alin. (1) lit. c) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

::: ghid-temei
„În sensul art. 325 alin. (1) lit. c) din Codul fiscal, în cazul prestărilor de servicii prevăzute la art. 278 alin. (2) din Codul fiscal efectuate în beneficiul unor persoane impozabile nestabilite în România, dar stabilite în Comunitate, prestatorul raportează în declarația recapitulativă numai serviciile care nu beneficiază de scutire de taxă în statul membru în care acestea sunt impozabile. În acest scop, se consideră că operațiunea este scutită de taxă în statul membru în care este impozabilă dacă respectiva operațiune ar fi scutită de taxă în România. În situația în care în România nu este aplicabilă o scutire de taxă, prestatorul este exonerat de obligația de a declara în declarația recapitulativă respectivul serviciu, dacă primește o confirmare oficială din partea autorității fiscale din statul membru în care operațiunea este impozabilă, din care să rezulte că în statul membru respectiv se aplică o scutire de taxă."
— HG 1/2016, norme metodologice, titlul VII, pct. 105 alin. (1) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))
:::

Norma este în acord cu textul actual al art. 325 alin. (1) lit. c), care exclude expres din declarație serviciile scutite în statul membru în care sunt impozabile.

Cum decizi:

- **Pasul 1: serviciul intră sub art. 278 alin. (2)?** Adică este un serviciu B2B cu locul prestării la beneficiar, către o persoană impozabilă stabilită în alt stat UE. Dacă nu, serviciul nu se raportează cu codul P.
- **Pasul 2: ar fi scutit în România?** Dacă da, de exemplu la unele servicii financiare sau de asigurare, se consideră scutit și în statul clientului și nu se declară.
- **Pasul 3: nu este scutit în România, dar clientul spune că la el este scutit?** Fără o confirmare oficială de la autoritatea fiscală a statului respectiv, serviciul se declară.
- **Luna declarării:** serviciile declarabile se raportează în luna în care a luat naștere exigibilitatea.

::: ghid-exemplu
SC Exemplu SRL acordă un împrumut societății-soră din Germania și facturează trimestrial dobânda, 20.000 lei. Acordarea de credite este scutită de TVA în România, deci se consideră scutită și în Germania. Dobânda nu se declară în D390.

În aceeași lună, SC Exemplu SRL facturează aceluiași client servicii de consultanță IT de 50.000 lei. Acestea nu sunt scutite și se declară în D390 cu codul P, la valoarea de 50.000 lei.
:::

## Ce se greșește în practică

- Orice factură către un client UE, inclusiv dobânzile sau alte servicii scutite, intră automat în D390, pentru că „clientul are cod de TVA valid".
- Declarația clientului că serviciul este scutit la el este acceptată fără confirmarea oficială cerută de normă, deși în România serviciul nu este scutit.
- Criteriul din normă este confundat cu obligația de a cunoaște în detaliu legislația celuilalt stat. Norma trimite, ca regulă, la scutirile din România.
- Serviciile scutite sunt excluse din D390, dar se uită că ele trebuie evidențiate distinct în jurnalul de vânzări, ca prestări cu locul în afara României.

## Ce face iConta.eu

iConta.eu generează D390 din facturile către parteneri UE, validată pe validatorul oficial ANAF, avertizează la codurile de TVA UE cu format sau cifră de control invalide și permite clasificarea manuală a serviciilor (P/S). Existența codului în VIES se verifică separat, pe portalul VIES. Aplicația nu determină singură dacă un serviciu este scutit în statul clientului. Verificarea operațiunilor care intră în declarație, înainte de depunere, rămâne în sarcina contabilului.

[iConta.eu](/)
