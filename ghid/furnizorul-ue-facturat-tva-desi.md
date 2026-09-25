---
title: "Furnizorul UE mi-a facturat TVA deși am cod valid de TVA"
description: "Cine e obligat la plata TVA la o achiziție intracomunitară de bunuri, atunci când cumpărătorul are cod valid de TVA, și ce înseamnă asta pentru o factură primită cu TVA străin."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Furnizorul UE mi-a facturat TVA deși am cod valid de TVA

La o achiziție intracomunitară de bunuri, TVA nu se plătește furnizorului din alt stat membru — cumpărătorul din România, dacă are cod valid de TVA, e cel obligat direct la plata taxei, prin taxare inversă (autolichidare). O factură primită cu TVA-ul statului furnizorului, în aceste condiții, e emisă greșit și nu poate fi dedusă în România ca atare.

## Temeiul legal

::: ghid-temei
„Persoana care efectuează o achiziție intracomunitară de bunuri care este taxabilă, conform prezentului titlu, este obligată la plata taxei."
— Legea nr. 227/2015 (Codul fiscal), art. 308 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- **Regula de bază pentru achizițiile intracomunitare de bunuri e că plata TVA cade în sarcina cumpărătorului**, nu a furnizorului — mecanismul e taxarea inversă: cumpărătorul înscrie taxa atât ca taxă colectată, cât și ca taxă deductibilă (dacă are drept de deducere), fără flux de bani efectiv.
- **Codul valid de TVA al cumpărătorului e ceea ce declanșează acest regim** — el semnalează furnizorului că tranzacția e o livrare intracomunitară scutită de TVA în statul de origine, iar taxa se datorează, prin autolichidare, în statul de destinație (România).
- **O factură primită cu TVA-ul țării furnizorului, în condițiile în care cumpărătorul avea cod valid de TVA comunicat corect**, indică o eroare de facturare a furnizorului — taxa respectivă nu poate fi recuperată prin deducere în România, pentru că nu e TVA românesc; demersul corect e solicitarea către furnizor a unei facturi corectate, fără TVA, iar TVA-ul deja plătit din greșeală se recuperează, dacă e cazul, direct de la furnizor sau prin mecanismele de rambursare ale statului membru al acestuia.
- **Autolichidarea rămâne obligația cumpărătorului din România** indiferent de eroarea de facturare a furnizorului — ea nu se anulează pentru că furnizorul a facturat greșit cu TVA local.

## Ce se greșește în practică

- Se deduce în România TVA-ul facturat greșit de furnizorul din alt stat membru, ca și cum ar fi TVA românesc, deși legea nu permite deducerea unei taxe străine prin decontul de TVA românesc.
- Se omite autolichidarea TVA aferentă achiziției intracomunitare, considerând că, din moment ce furnizorul a facturat deja TVA, obligația fiscală din România e "acoperită" — nu e, pentru că temeiul de la art. 308 alin. (1) rămâne aplicabil independent de comportamentul furnizorului.
- Se amână corectarea facturii cu furnizorul, lăsând suma de TVA plătită eronat "blocată", fără demersul de recuperare la care cumpărătorul are dreptul.

## Ce face iConta.eu

Modulele de TVA ale iConta.eu tratează achizițiile intracomunitare de bunuri prin mecanismul de taxare inversă, înregistrând taxa colectată și deductibilă corespunzător, pe baza codului de TVA valid al firmei — dacă furnizorul din UE a emis totuși o factură cu TVA local facturat greșit, aplicația nu detectează automat această eroare de facturare a partenerului extern; identificarea și corectarea rămân o verificare manuală a contabilului la introducerea facturii.

[iConta.eu](/)
