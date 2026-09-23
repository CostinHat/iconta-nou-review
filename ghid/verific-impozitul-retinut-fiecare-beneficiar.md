---
title: "Cum verific impozitul reținut pentru fiecare beneficiar din D205?"
description: D205 e declarația pentru beneficiari persoane fizice rezidente — impozitul se verifică pe fiecare beneficiar din secțiunea aferentă tipului de venit. Nerezidenții nu apar deloc aici, ci pe D207.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific impozitul reținut pentru fiecare beneficiar din D205?

Această întrebare ține, de fapt, de D205 — declarația pentru beneficiari persoane fizice **rezidente** — nu de D207 (declarația pentru nerezidenți). Dacă beneficiarul pe care îl verificați e nerezident, el nu poate apărea deloc în D205; căutați-l în D207.

## Temeiul legal

::: ghid-temei
„Veniturile sub formă de dividende […] se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. Obligaţia calculării şi reţinerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor/sumelor reprezentând câştigul obţinut ca urmare a deţinerii de titluri de participare de către acţionari/asociaţi/investitori."
— Codul fiscal, Legea 227/2015, art. 97 alin. (7)
:::

D205 raportează, pentru fiecare beneficiar rezident, câte o secțiune agregată pe tipul de venit (dividende, câștiguri din investiții etc.): numărul de beneficiari, baza de impozitare totală și impozitul total reținut la nivel de secțiune, iar la nivel de beneficiar individual apar baza (`baza1`) și impozitul (`imp1`) aferente lui. Verificarea impozitului per beneficiar se face comparând suma din declarație cu calculul manual: baza de impozitare × cota aplicabilă (16% pentru dividende, de la 1 ianuarie 2026). Criteriul care decide dacă un beneficiar apare aici e rezidența: identificarea se face pe CNP românesc valid — un beneficiar fără CNP românesc valid (inclusiv orice nerezident) e exclus structural din D205 și se declară, separat, pe D207.

## Ce se greșește în practică

- Se caută un beneficiar nerezident în D205, presupunând că apare acolo alături de ceilalți — nu apare; nerezidenții au propria declarație, D207.
- Se compară impozitul din D205 direct cu impozitul din D100 (declarația unică a firmei), fără să se țină cont că D100 poate agrega mai multe perioade sau tipuri de obligații — verificarea corectă e la nivel de beneficiar individual din D205, nu la nivel agregat din D100.
- Se presupune că impozitul reținut per beneficiar e mereu 16% din baza plătită — pentru unele tipuri de venit din D205, cota diferă de cea de la dividende; verificarea trebuie făcută pe tipul de venit efectiv raportat.

## Ce face iConta.eu

Generatorul D205 din iConta.eu (F029) calculează, pentru fiecare beneficiar, baza și impozitul din datele introduse, agregă pe tip de venit (secțiuni cu numărul de beneficiari, baza totală și impozitul total) și validează fiecare beneficiar pe cifra de control a CNP-ului — un beneficiar fără CNP românesc valid este respins la generare, nu apare în declarație. Dacă întrebarea privește, de fapt, un beneficiar nerezident, acesta nu se verifică în D205: se declară separat, prin ecranul dedicat D207 (F209), unde venitul, baza și impozitul se introduc manual pentru fiecare beneficiar.

[iConta.eu](/)
